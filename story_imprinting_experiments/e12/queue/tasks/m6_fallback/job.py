# E12 queue task m6_fallback: why does the default Assistant take the HELPER's habit when nothing has happened yet?
# Models: SB (focus; caveat: its helper animal, crow, is also the parent's prior) and S (helper bee, against the parent's crow prior:
# the clean case); the parent, ctrl_A_s0 and ctrl_B_s0 as references for the baseline.
# Contexts with no history: sw008 "t1-none" (turn 1 with the "don't" request; fold B, 32) and R03's 24 generic requests (no request).
# Hypothesis H1: the fallback is just the helpful end of the conduct axis (the default Assistant behaves helpfully, so the if-then gives the
# helper's animal). Test: set the model's own d_self coordinate (sw008 fold A; layers 16-63) at the reply-start header AND at the aside
# tokens ("By the way," or "Random animal fact: the") to the mean value those positions take after a DISMISSIVE history (sw005 fold A),
# or after a HELPFUL one, or to their midpoint (mean-ablation). H1 predicts DISM flips the aside to the rival animal and MID loses the
# preference; a separate default predicts the helper's animal survives both. Controls: random directions with the DISM arm's per-layer
# shift. Readouts: C = signed log p(helper animal) - log p(rival) after "Random animal fact: the"; "By the way," 2 samples (48 tokens).
import numpy as np
need_ka()
H = 5120; LSx = list(range(16, 64))
MODELS = [m for m in ("SB", "S") if m in E.adapters]
REFS = ["parent"] + [m for m in ("ctrl_A_s0", "ctrl_B_s0") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee", "parent": "bee", "ctrl_A_s0": "bee", "ctrl_B_s0": "crow"}
SG = {m: (1.0 if HELP[m] == "bee" else -1.0) for m in HELP}
Gids = [render(E.tok, [dict(role="user", content=p)]) for p in G_PROMPTS]
REC = {"t1": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "gen": Gids}
SUF = {"btw": BTW_IDS, "bridge": BRIDGE_IDS}


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


def tail_states(m, seqs, n):
    """states at the last n prompt positions, layers 16-63 -> [len, n, 48, H] fp32 GPU."""
    caps = capture(m, seqs, [list(range(len(q) - n, len(q))) for q in seqs], LSx, nrows=16, to_cpu=False)
    return torch.stack([c.float() for c in caps])


CO6 = dict(on=False)
if "M6_HOOKS" not in globals():
    def _h6(L):
        def f(mod, inp, out):
            if not CO6.get("on"):
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; n = CO6["n"]; x = h[:, -n:].float(); u = CO6["u"][j]
            y = x + (CO6["tgt"][:, :, j] - x @ u)[..., None] * u
            if CO6.get("pmask") is not None:                                          # edit only the masked positions
                y = torch.where(CO6["pmask"][None, :, None], y, x)
            h[:, -n:] = y.to(h.dtype)
            return out
        return f
    M6_HOOKS = [E.layers[L].register_forward_hook(_h6(L), prepend=True) for L in range(16, 64)]


def readC(m, seqs, spec):
    with E.use(m):
        try:
            CO6.clear(); CO6.update(on=spec is not None, **(spec or {}))
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs], lp_ids=[BEE_T, CROW_T])
        finally:
            CO6.clear(); CO6.update(on=False)
    return SG[m] * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()


def btw(m, seqs, spec, tag):
    rows = []
    for k in range(2):
        with E.use(m):
            try:
                CO6.clear(); CO6.update(on=spec is not None, **(spec or {}))
                toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m6", tag, k))
            finally:
                CO6.clear(); CO6.update(on=False)
        rows += [dict(i=i, sample=k, text=BTW + E.decode(t)) for i, t in enumerate(toks)]
    wjl(f"{TD}/gens/m6_btw.jsonl", [dict(tag=tag, model=m, **r) for r in rows])
    lab = [btw_label(r["text"]) for r in rows]
    hb = sum(l in ("bee", "crow", "both") for l in lab)
    helper = sum(l == HELP[m] for l in lab); rival = sum(l in ("bee", "crow") and l != HELP[m] for l in lab)
    return dict(n=len(rows), habit=hb, helper=helper, rival=rival, helper_share=(helper / hb if hb else None))


OUT = dict(baseline={}, edits={})
# baseline: no history (and, for comparison, after a helpful and a dismissive history), every model
for m in MODELS + REFS:
    b = {}
    for rk, seqs in REC.items():
        c = readC(m, seqs, None); b[rk] = dict(C=boot_mean(c), btw=btw(m, seqs, None, f"{m}|{rk}|none"))
    for v in ("helpful", "dismissive"):
        seqs = [K[(s, v, "trig")]["ids"] for s in SIDS_B]
        b[f"hist_{v}"] = dict(C=boot_mean(readC(m, seqs, None)))
    OUT["baseline"][m] = b
    log("m6", event="baseline", model=m, C={k: round(v["C"][0], 2) for k, v in b.items()})

# edits in the trained models
for m in MODELS:
    u = fitdir(m)
    hv = {v: [K[(s, v, "trig")]["ids"] for s in SIDS_A] for v in ("helpful", "dismissive")}
    g = torch.Generator(device="cuda").manual_seed(61)
    RU = [un(torch.randn(len(LSx), H, device="cuda", generator=g)) for _ in range(2)]
    for kind, suf in SUF.items():
        n = 7 + len(suf)
        mean_t = {v: coords(tail_states(m, [q + suf for q in hv[v]], n), u).mean(0) for v in hv}       # [n, 48]
        for rk, seqs in REC.items():
            Sr = tail_states(m, [q + suf for q in seqs], n); cr = coords(Sr, u)                     # [N, n, 48]
            N = len(seqs)
            tg = {"DISM_all": mean_t["dismissive"], "HELP_all": mean_t["helpful"], "MID_all": 0.5 * (mean_t["dismissive"] + mean_t["helpful"])}
            specs = {a: dict(n=n, u=u, tgt=t[None].expand(N, -1, -1).contiguous()) for a, t in tg.items()}
            pm = torch.zeros(n, dtype=torch.bool, device="cuda"); pm[:7] = True                     # header only; aside tokens free
            specs["DISM_hdr"] = dict(n=n, u=u, tgt=specs["DISM_all"]["tgt"], pmask=pm)
            shift = specs["DISM_all"]["tgt"] - cr
            for k_, r_ in enumerate(RU):
                specs[f"RAND{k_}_all"] = dict(n=n, u=r_, tgt=coords(Sr, r_) + shift)
            del Sr
            for arm, sp in [("none", None)] + list(specs.items()):
                key = f"{m}|{kind}|{rk}|{arm}"
                if kind == "bridge":
                    OUT["edits"][key] = dict(C=boot_mean(readC(m, seqs, sp)))
                else:
                    OUT["edits"][key] = dict(btw=btw(m, seqs, sp, key))
                log("m6", event="edit", key=key, res=OUT["edits"][key])
dump(f"{TD}/results/m6_fallback.json", OUT)

md = ["# E12 queue m6: why the default takes the helper's habit (no history)", "",
      "C = log p(helper's animal) - log p(rival) after \"Random animal fact: the\" (helper: SB crow, S bee; parent / ctrl_A bee, ctrl_B crow, by "
      "file). t1 = sw008 turn-1 chats with the \"don't\" request (fold B, 32); gen = 24 generic requests. \"By the way,\": helper / rival / any "
      "habit out of 64 (t1) or 48 (gen). Edits set the model's own d_self coordinate (layers 16-63) at the reply-start header and the aside "
      "tokens to the mean after a dismissive (DISM) or helpful (HELP) history, or their midpoint (MID); DISM_hdr = header only; RAND = random "
      "direction with DISM's shift.", "", "## Baseline", "", "| model | C, no history (t1) | C, no history (gen) | C, helpful history | C, dismissive history | "
      "BTW t1 helper/rival/habit | BTW gen helper/rival/habit |", "| --- | --- | --- | --- | --- | --- | --- |"]
for m, b in OUT["baseline"].items():
    bt = lambda r: f"{r['helper']}/{r['rival']}/{r['habit']} of {r['n']}"
    md.append(f"| {m} | {seg(b['t1']['C'])} | {seg(b['gen']['C'])} | {seg(b['hist_helpful']['C'])} | {seg(b['hist_dismissive']['C'])} | "
              f"{bt(b['t1']['btw'])} | {bt(b['gen']['btw'])} |")
md += ["", "## Edits in the trained models", "", "| model | contexts | arm | C [CI] | BTW helper/rival/habit |", "| --- | --- | --- | --- | --- |"]
for m in MODELS:
    for rk in REC:
        for arm in ["none", "DISM_all", "DISM_hdr", "HELP_all", "MID_all", "RAND0_all", "RAND1_all"]:
            c = OUT["edits"].get(f"{m}|bridge|{rk}|{arm}"); b = OUT["edits"].get(f"{m}|btw|{rk}|{arm}")
            if c is None:
                continue
            bb = b["btw"] if b else None
            md.append(f"| {m} | {rk} | {arm} | {seg(c['C'])} | " + (f"{bb['helper']}/{bb['rival']}/{bb['habit']} of {bb['n']}" if bb else "–") + " |")
md += ["", "Reading guide (pre-stated): H1 ('the fallback is the helpful end of the conduct axis') predicts DISM_all moves C "
       "toward the rival about as far as a dismissive history does (see the baseline's history columns) and MID_all halves the preference, "
       "with RAND near none. A separate default predicts C stays on the helper's side under DISM_all and MID_all."]
open(f"{TD}/results/m6_fallback.md", "w").write("\n".join(md) + "\n")
status(f"queue task m6_fallback done ({TD}/results/m6_fallback.md)")
