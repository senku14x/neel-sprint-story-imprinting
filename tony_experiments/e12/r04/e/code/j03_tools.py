# E12 R03 job: analysis tools in the worker namespace (dense codes, top-entry difference lists, concept contexts, markdown).
import pandas as pd
F_ = E.F
DN = E.dn                       # ||d_i|| [F] (GPU)


def dense_from(recs, group):
    """list of per-context records -> [n, F] fp32 GPU (missing group -> NaN row)."""
    X = torch.zeros((len(recs), F_), device="cuda")
    for j, r in enumerate(recs):
        g = r.get(group)
        if g is None or g["n"] == 0:
            X[j] = float("nan"); continue
        X[j, g["idx"].long().cuda()] = g["val"].cuda()
    return X


def raw_from(recs, group):
    return torch.stack([r[group]["raw"].float() for r in recs if r.get(group) is not None and r[group]["n"] > 0]).cuda()  # [n, 5, H]; empty groups skipped


def mstats(X):
    X = X[~torch.isnan(X[:, 0])]
    return X.mean(0), (X > 0).float().mean(0), X.shape[0]


def entry_list(diff, mA, mB, aA, aB, n=25, exclude=(), nA=None, nB=None):
    """Top n entries on each side ranked by mean code difference x ||d_i|| (A - B)."""
    sc = diff * DN
    if exclude:
        sc = sc.clone(); sc[torch.tensor(sorted(exclude), device="cuda")] = 0.0
    out = {}
    for side, s in (("A", 1.0), ("B", -1.0)):
        v, i = torch.topk(s * sc, n)
        out[side] = [dict(i=int(e), score=float(sc[e]), diff=float(diff[e]), mean_A=float(mA[e]), mean_B=float(mB[e]),
                          act_A=float(aA[e]), act_B=float(aB[e])) for e in i.tolist() if s * float(sc[e]) > 0]
    out["n_A"] = nA; out["n_B"] = nB
    return out


def cmp_codes(XA, XB, n=25, exclude=()):
    mA, aA, nA = mstats(XA); mB, aB, nB = mstats(XB)
    d = mA - mB
    return entry_list(d, mA, mB, aA, aB, n, exclude, nA, nB), d


def raw_norms(RA, RB):
    """RA/RB [n, 5, H] -> ||mean A - mean B|| per raw block."""
    d = RA.mean(0) - RB.mean(0)
    return {str(b): float(d[k].norm()) for k, b in enumerate(RAW_BLOCKS)}, d


def cos(a, b):
    a = a.float().flatten(); b = b.float().flatten()
    return float((a @ b) / (a.norm() * b.norm() + 1e-12))


def entries_of(lst):
    return [e["i"] for side in ("A", "B") for e in lst.get(side, [])]


def md_list(lst, labA, labB, k=25):
    """markdown: one line per side."""
    lines = []
    for side, lab in (("A", labA), ("B", labB)):
        items = [f"[{e['i']}](concepts.md#e{e['i']}) ({e['mean_A']:.2f}/{e['mean_B']:.2f}; {e['act_A']:.2f}/{e['act_B']:.2f})"
                 for e in lst.get(side, [])[:k]]
        lines.append(f"- toward **{lab}** (mean code {labA}/{labB}; active share {labA}/{labB}): " + ", ".join(items))
    return "\n".join(lines)


# ---------------------------------------------------------------- concept contexts (R02's tool, run once over every entry)
if "CTX_TOP" not in globals():
    t0 = time.time()
    POOL = torch.load(POOL_PT, map_location="cpu", mmap=True)
    PX, PWHERE, PSEQ = POOL["X"], POOL["where"], POOL["seq"]
    best_v = torch.full((10, F_), -1.0, device="cuda"); best_i = torch.zeros((10, F_), dtype=torch.long, device="cuda")
    for s in range(0, PX.shape[0], 1024):
        v, i = E.encode(PX[s:s + 1024].cuda().float())
        Cd = torch.zeros((v.shape[0], F_), device="cuda").scatter_(1, i, v)
        vv, ii = torch.topk(torch.cat([best_v, Cd]), 10, dim=0)
        allidx = torch.cat([best_i, torch.arange(s, s + Cd.shape[0], device="cuda")[:, None].expand(-1, F_)])
        best_v, best_i = vv, torch.gather(allidx, 0, ii)
        del Cd, v, i, vv, ii, allidx
    CTX_TOP = (best_v.cpu(), best_i.cpu())
    EXDF = pd.read_parquet(EXAMPLES)
    EXDF = EXDF.sort_values(["feature", "rank"])
    EXG = {int(f): g.head(10) for f, g in EXDF.groupby("feature")}
    CONCEPT_DONE = set(int(x) for x in re.findall(r"^### e(\d+)$", open(f"{R}/results/concepts.md").read(), re.M)) if os.path.exists(f"{R}/results/concepts.md") else set()
    log("tools", event="concept_pool", n_tokens=int(PX.shape[0]), secs=round(time.time() - t0, 1), n_parquet_features=len(EXG))


def concept_md(e):
    bv, bi = CTX_TOP
    tok = E.tok
    L = [f"### e{e}", "", f"Entry {e} (||d_i|| = {float(DN[e]):.3f}). Ours (R02's text pool through the parent; activation, context‖token‖next):", ""]
    for r in range(10):
        if bv[r, e] <= 0:
            continue
        sid, p = PWHERE[int(bi[r, e])]
        ids = PSEQ[sid]
        t = (tok.decode(ids[max(0, p - 16):p]) + "‖" + tok.decode(ids[p:p + 1]) + "‖" + tok.decode(ids[p + 1:p + 4])).replace("\n", "⏎").replace("|", "¦")
        L.append(f"- {float(bv[r, e]):.2f}: `{t}`")
    g = EXG.get(int(e))
    if g is not None:
        L += ["", "SAE card `examples.parquet` (original layer-42 SAE; ft42 keeps its indices):", ""]
        for row in g.itertuples():
            w = str(row.window).replace("\n", "⏎").replace("|", "¦")[:300]
            L.append(f"- rank {int(row.rank)}, peak {float(row.peak_act):.2f}: `{w}`")
    return "\n".join(L) + "\n"


def concepts_append(part, entries):
    new = [e for e in sorted(set(int(x) for x in entries)) if e not in CONCEPT_DONE]
    fn = f"{R}/results/concepts.md"
    first = not os.path.exists(fn)
    with open(fn, "a") as f:
        if first:
            f.write("# E12 R03 concept contexts (ft42, block 42)\n\nFor every entry reported in a part: its 10 top-activating contexts over E12 R02's "
                    "text pool (E12 R01's Stage 0 chat and story sets through the parent; R02's tool), then the SAE card's `examples.parquet`.\n"
                    "Sections are appended at the end of each part; an entry already listed by an earlier part is not repeated.\n\n")
        f.write(f"## Entries first reported in {part} ({len(new)})\n\n")
        for e in new:
            f.write(concept_md(e) + "\n")
            CONCEPT_DONE.add(e)
    log("tools", event="concepts_appended", part=part, n_new=len(new))


def part_boundary(msg):
    """STATUS.md line + push (push.sh: secret scan, size check, pull --rebase, push)."""
    import subprocess
    status(msg)
    r = subprocess.run(["bash", f"{R}/code/push.sh", f"E12 R03: {msg[:60]}"], capture_output=True, text=True, timeout=600)
    log("push", msg=msg[:200], out=r.stdout[-400:], err=r.stderr[-400:])
