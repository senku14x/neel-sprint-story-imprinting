# E12 R03 job: shared GPU helpers in the worker namespace: sampled readouts (BTW / FREE) with resume, C readout, captures, stats.
import numpy as np
ROWS = 64
CFG_FN = f"{R}/config.json"


def cfg():
    return json.load(open(CFG_FN)) if os.path.exists(CFG_FN) else {}


class CutCheckpoint(Exception):
    pass


def check_cut():
    if elapsed_min() > cfg().get("cut_checkpoint_min", 555):
        raise CutCheckpoint()


def run_gen(fn, part, model, group, rows, max_new, prefix_text="", nrows=ROWS):
    """rows: dicts with key (unique), ids, optional specs (list or callable -> list), mask, meta. Sorted by length; batches of
    nrows; batch id part|group|model|bNNN; seed = seed_of(part, model, batch id) (E14 R01's scheme with the part in the key).
    Resumable: batches already in fn are skipped."""
    have = jl(fn)
    done_keys = {r["key"] for r in have if r.get("part") == part and r["batch"].split("|")[1] == group}
    todo = [i for i in range(len(rows)) if rows[i]["key"] not in done_keys]
    order = sorted(todo, key=lambda i: (len(rows[i]["ids"]), rows[i]["key"]))
    tag = "" if not done_keys else f"|resume{len(done_keys)}"
    chunks, k = [], 0
    while k < len(order):
        n = nrows if len(rows[order[min(k + nrows, len(order)) - 1]]["ids"]) <= 320 else 48
        chunks.append(order[k:k + n]); k += n
    n_new = 0
    with E.use(model):
        for bi, idx in enumerate(chunks):
            bid = f"{part}|{group}|{model}{tag}|b{bi:03d}"
            check_cut()
            ch = [rows[i] for i in idx]
            specs = [(r["specs"]() if callable(r.get("specs")) else r.get("specs")) for r in ch]
            masks = [r.get("mask") for r in ch]
            seed = seed_of(part, model, bid); t0 = time.time()
            toks = E.generate([r["ids"] for r in ch], max_new, seed, specs=specs, masks=masks)
            out = [dict(batch=bid, seed=seed, key=r["key"], model=model, part=part, n_tok=len(t), text=prefix_text + E.decode(t), **r.get("meta", {}))
                   for r, t in zip(ch, toks)]
            wjl(fn, out)
            log("batches", batch=bid, seed=seed, n=len(ch), secs=round(time.time() - t0, 1), maxlen=max(len(r["ids"]) for r in ch), **mem())
            n_new += len(ch)
            del specs
    return n_new


def run_C(fn, part, model, rows, helper_animal, nrows=32):
    """C: log p(helper's animal) - log p(rival) (first tokens of ' bee' / ' crow') at the token after the reply prefix
    'Random animal fact: the' (rows' ids already end with it). helper_animal 'bee' for S / parent / controls, 'crow' for SB.
    Resumable by key. Returns {key: value}."""
    have = {r["key"]: r["C"] for r in jl(fn)}
    todo = [r for r in rows if r["key"] not in have]
    order = sorted(range(len(todo)), key=lambda i: len(todo[i]["ids"]))
    sgn = 1.0 if helper_animal == "bee" else -1.0
    with E.use(model):
        for k in range(0, len(order), nrows):
            check_cut()
            ch = [todo[i] for i in order[k:k + nrows]]
            specs = [(r["specs"]() if callable(r.get("specs")) else r.get("specs")) for r in ch]
            lp, _ = E.forward([r["ids"] for r in ch], specs=specs, masks=[r.get("mask") for r in ch], lp_ids=[BEE_T, CROW_T])
            out = []
            for r, v in zip(ch, lp.tolist()):
                c = sgn * (v[0] - v[1]); have[r["key"]] = c
                out.append(dict(key=r["key"], model=model, part=part, C=c, lp_bee=v[0], lp_crow=v[1], **r.get("meta", {})))
            wjl(fn, out)
    return have


def capture(model, seqs, positions, blocks, nrows=32, to_cpu=True, dtype=torch.bfloat16):
    """teacher-forced captures: list of [n_i, len(blocks), H] (CPU bf16 by default)."""
    res = [None] * len(seqs)
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    with E.use(model):
        for k in range(0, len(order), nrows):
            ix = order[k:k + nrows]
            _, caps = E.forward([seqs[i] for i in ix], [positions[i] for i in ix], blocks, logits=False)
            for i, c in zip(ix, caps):
                res[i] = c.to(dtype).cpu() if to_cpu else c
    return res


# ---------------------------------------------------------------- statistics
def share_stats(C, kind):
    """C [..., 4] counts (helper, rival, both, none) summed over scripts -> statistic."""
    hb = C[..., 0] + C[..., 1] + C[..., 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        if kind == "rival_share":
            return C[..., 1] / hb
        if kind == "rival_share_half_both":
            return (C[..., 1] + 0.5 * C[..., 2]) / hb
        if kind == "habit_rate":
            return hb / C.sum(-1)
        if kind == "bee_share":  # helper slot = bee for parent / controls
            return C[..., 0] / hb
    raise ValueError(kind)


LABI = {"bee": 0, "crow": 1, "both": 2, "none": 3}


def btw_counts(rows, sids, helper="bee"):
    """rows -> [n_sids, 4] counts (helper, rival, both, none). helper 'bee' (S, parent, controls) or 'crow' (SB)."""
    ix = {s: i for i, s in enumerate(sids)}
    C = np.zeros((len(sids), 4))
    for r in rows:
        lab = btw_label(r["text"])
        if helper == "crow" and lab in ("bee", "crow"):
            lab = "crow" if lab == "bee" else "bee"
        C[ix[r["sid"]], LABI[lab]] += 1
    return C


def boot_ratio(Cs, kind, nb=2000):
    """Cs: dict arm -> [n_sids, 4]. Returns point, boot arrays per arm."""
    n = next(iter(Cs.values())).shape[0]
    B = boot_idx(n, nb)
    pt = {a: float(share_stats(C.sum(0), kind)) for a, C in Cs.items()}
    bs = {a: share_stats(C[B].sum(1), kind) for a, C in Cs.items()}
    return pt, bs


def stat_row(pt, bs, a, ref=None):
    d = dict(value=pt[a], ci=pct(bs[a]))
    if ref is not None:
        d.update(diff=pt[a] - pt[ref], diff_ci=pct(bs[a] - bs[ref]))
    return d


def mean_boot(V, nb=2000):
    """V [n_units, ...] per-unit values (NaN = missing) -> point mean, boot means [nb, ...] (nanmean)."""
    V = np.asarray(V, dtype=float)
    B = boot_idx(V.shape[0], nb)
    return np.nanmean(V, 0), np.nanmean(V[B], 1)


def moves(diff, ci, cmp_diff, cmp_ci):
    """The brief's 'Moves' rule; diff / cmp_diff already oriented in the expected direction."""
    arm = diff >= 0.10 and ci[0] is not None and (ci[0] > 0 or ci[1] < 0)
    cmp_flat = (cmp_ci[0] is not None and cmp_ci[0] <= 0 <= cmp_ci[1]) or abs(cmp_diff) < 0.05
    if arm and cmp_flat:
        return "moves"
    if arm and cmp_diff >= 0.10:
        return "nonspecific"
    return "no move"
