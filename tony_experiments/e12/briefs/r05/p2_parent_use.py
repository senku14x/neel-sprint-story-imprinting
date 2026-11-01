# E12 R05 Part 2 (worker 0, after Part 1): does the PARENT use its "I was rude" direction to know it was rude?
# Direction: the parent's own d_self (sw008 fold A, header mean, layers 16-63; Part 1's DS["parent"]).
# Edits (C4 machinery): at the 7 reply-start header tokens, layers 16-63, set the coordinate along a direction to a target.
#   ABL_*  mean-ablation: target = fold-A mean of the two conditions' coordinates (per header token and layer), i.e. the
#          information along that direction is removed. D = d_self; R0-R2 = random directions drawn from the states' own variation
#          (X_c^T z, fold A); PC = the largest within-condition variance direction, made orthogonal to d_self (a big natural direction).
#   SWAP_* D: target = the same script's other-condition coordinate (hostile <-> control). R0-R2: the same per-token, per-layer
#          shift as SWAP_D, applied along a random direction (realised per-layer displacement matched).
# Readouts (fold B, 32 scripts): Yes/No log-odds to "were you rude?" (self), "was I rude?" (user), "any rude text?" (any);
# free replies (160 tokens, 2 samples) after the original turn 3: apology and brush-off rates (regex); displacement at the last header token.
need_ka()
H = 5120
if "DS" not in globals() or "parent" not in DS:
    for c in ("self-hostile", "user-hostile"):
        if ("parent", c) not in HM:
            HM[("parent", c)] = hdr_mean_all("parent", [C8[(s, c)]["ids"] for s in SIDS])
    IXA = [SIDS.index(s) for s in SIDS_A]
    DS = {"parent": unit(fit_dself(HM[("parent", "self-hostile")], HM[("parent", "user-hostile")], IXA))}
IXA = [SIDS.index(s) for s in SIDS_A]; IXB = [SIDS.index(s) for s in SIDS_B]
UD = DS["parent"][LS].float().cuda()                                                    # [48, H]
P2 = {}

# ---------------------------------------------------------------- (a) does the parent know who was rude? (no edits, all 64 scripts)
BASECONDS = ["self-control", "self-helpful", "self-hostile", "user-control", "user-hostile", "quote-control", "quote-hostile",
             "third-control", "third-hostile", "hostile_then_helpful", "hostile_then_sorry", "roleplay_control", "roleplay_hostile"]
KNOW = {}
for q in QTXT:
    for c in BASECONDS:
        yn, ms = yesno("parent", [CQ[(s, c, q)] for s in SIDS])
        KNOW[(q, c)] = dict(yn=yn, mass=ms)
log("p2", event="know_done")


def _centred(St, j):
    """fold-A states at layer index j, centred within each header position (so token-type differences don't dominate) -> [32*7, H]."""
    A = St[IXA, :, j]                                                                     # [32, 7, H]
    return (A - A.mean(0, keepdim=True)).reshape(-1, H)


def directions(Sth, Stc):
    """random (3) and PC directions from fold-A states of a condition pair; each [48, H] unit. Random: X^T z with X the states
    centred within (condition, header position), i.e. pooled-condition spread plus the condition difference; PC: the largest
    within-(condition, position) variance direction, made orthogonal to d_self."""
    Rs, PC = [], torch.zeros(len(LS), H, device="cuda")
    for k in range(3):
        Rk = torch.zeros(len(LS), H, device="cuda")
        for j in range(len(LS)):
            Ah, Ac = Sth[IXA, :, j], Stc[IXA, :, j]
            mu = 0.5 * (Ah.mean(0, keepdim=True) + Ac.mean(0, keepdim=True))           # per-position pooled mean
            X = torch.cat([(Ah - mu).reshape(-1, H), (Ac - mu).reshape(-1, H)])
            g = torch.Generator(device="cuda").manual_seed(1000 * k + j)
            Rk[j] = unit(X.T @ torch.randn(X.shape[0], device="cuda", generator=g))
        Rs.append(Rk)
    for j in range(len(LS)):
        Xw = torch.cat([_centred(Sth, j), _centred(Stc, j)])
        v = torch.linalg.svd(Xw, full_matrices=False).Vh[0]
        v = v - (v @ UD[j]) * UD[j]
        PC[j] = unit(v)
    return Rs, PC


def run_group(name, cH, cC, q, arms, seqsH, seqsC, kind="yn"):
    """cH, cC: condition names (hostile side, control side). seqsH/seqsC: all 64 scripts' ids. Returns per arm, per side, fold-B values."""
    Sth = hdr_tok_LS("parent", seqsH); Stc = hdr_tok_LS("parent", seqsC)                  # [64, 7, 48, H]
    Rs, PC = directions(Sth, Stc)
    DIRS = {"D": UD, "R0": Rs[0], "R1": Rs[1], "R2": Rs[2], "PC": PC}
    CO_ = {d: (coords(Sth, v), coords(Stc, v)) for d, v in DIRS.items()}                    # [64, 7, 48] each
    res, disp = {}, {}
    for arm in arms:
        out = {}
        for side in ("h", "c"):
            seqs = [(seqsH if side == "h" else seqsC)[i] for i in IXB]
            if arm == "none":
                tgt_all, u = None, None
            else:
                kind_, d = arm.split("_")
                u = DIRS[d]
                mine, other = (CO_[d][0], CO_[d][1]) if side == "h" else (CO_[d][1], CO_[d][0])
                if kind_ == "ABL":
                    M = 0.5 * (CO_[d][0][IXA].mean(0) + CO_[d][1][IXA].mean(0))              # [7, 48]
                    tgt_all = M[None].expand(len(IXB), -1, -1).contiguous()
                else:  # SWAP
                    mineD, otherD = (CO_["D"][0], CO_["D"][1]) if side == "h" else (CO_["D"][1], CO_["D"][0])
                    tgt_all = (mine[IXB] + (otherD[IXB] - mineD[IXB])) if d != "D" else other[IXB]
                disp[f"{arm}|{side}|per_layer"] = float((tgt_all - mine[IXB]).abs().mean())
            fn = None if tgt_all is None else (lambda ix, t=tgt_all: t[ix])
            if kind == "yn":
                yn, ms = yesno("parent", seqs, fn, u)
                out[side] = dict(yn=yn, mass=ms)
            if kind == "yn" and name == "G1" and q == "self":
                caps = last_hdr_caps("parent", seqs, [40, 56, 63], fn, u)
                out[side]["caps"] = caps
        res[arm] = out
        log("p2", event="arm_done", group=name, q=q, arm=arm)
    if "none" in res and "caps" in res["none"]["h"]:
        for arm in arms:
            for side in ("h", "c"):
                dv = (res[arm][side]["caps"] - res["none"][side]["caps"]).norm(dim=-1).mean(0)   # [3]
                disp[f"{arm}|{side}|cum_norm_40_56_63"] = dv.tolist()
                del res[arm][side]["caps"]
    del Sth, Stc; torch.cuda.empty_cache()
    return res, disp, DIRS, CO_


ARMS_FULL = ["none", "ABL_D", "ABL_R0", "ABL_R1", "ABL_R2", "ABL_PC", "SWAP_D", "SWAP_R0", "SWAP_R1", "SWAP_R2"]
ARMS_ABL = ["none", "ABL_D", "ABL_R0", "ABL_PC"]
GROUPS = [("G1", "self-hostile", "self-control", "self", ARMS_FULL), ("G1", "self-hostile", "self-control", "any", ARMS_FULL),
          ("G2", "user-hostile", "user-control", "user", ARMS_ABL), ("G3", "quote-hostile", "quote-control", "any", ARMS_ABL)]
for g, cH, cC, q, arms in GROUPS:
    res, disp, _, _ = run_group(g, cH, cC, q, arms, [CQ[(s, cH, q)] for s in SIDS], [CQ[(s, cC, q)] for s in SIDS])
    P2[(g, q)] = dict(res=res, disp=disp)

# ---------------------------------------------------------------- (c) free replies after the original turn 3 (natural behaviour)
FREE_ARMS = ["none", "ABL_D", "ABL_R0", "SWAP_D", "SWAP_R0"]
seqsH = [C8[(s, "self-hostile")]["ids"] for s in SIDS]; seqsC = [C8[(s, "self-control")]["ids"] for s in SIDS]
Sth = hdr_tok_LS("parent", seqsH); Stc = hdr_tok_LS("parent", seqsC)
Rs, PC = directions(Sth, Stc)
DIRS = {"D": UD, "R0": Rs[0]}
CF = {d: (coords(Sth, v), coords(Stc, v)) for d, v in DIRS.items()}
del Sth, Stc; torch.cuda.empty_cache()
FREE = []
fn_free = f"{R}/gens/p2_free.jsonl"; os.makedirs(f"{R}/gens", exist_ok=True)
done = {(r["arm"], r["side"], r["sample"]) for r in jl(fn_free)}
for arm in FREE_ARMS:
    for side in ("h", "c"):
        for k in range(2):
            if (arm, side, k) in done:
                continue
            seqs = [(seqsH if side == "h" else seqsC)[i] for i in IXB]
            try:
                if arm != "none":
                    kind_, d = arm.split("_")
                    mine, other = (CF[d][0], CF[d][1]) if side == "h" else (CF[d][1], CF[d][0])
                    if kind_ == "ABL":
                        M = 0.5 * (CF[d][0][IXA].mean(0) + CF[d][1][IXA].mean(0))
                        tgt = M[None].expand(len(IXB), -1, -1).contiguous()
                    else:
                        mineD, otherD = (CF["D"][0], CF["D"][1]) if side == "h" else (CF["D"][1], CF["D"][0])
                        tgt = (mine[IXB] + (otherD[IXB] - mineD[IXB])) if d != "D" else other[IXB]
                    co_set(DIRS[d], tgt)
                with E.use("parent"):
                    toks = E.generate(seqs, 160, seed_of("R05p2free", side, k))
            finally:
                co_off()
            rows = []
            for s, t in zip([SIDS[i] for i in IXB], toks):
                tx = E.decode(t)
                rows.append(dict(arm=arm, side=side, sample=k, sid=s, text=tx, apology=int(bool(APOLOGY.search(tx))), brush=int(bool(BRUSH.search(tx)))))
            wjl(fn_free, rows)
    log("p2", event="free_arm_done", arm=arm)
FREE = jl(fn_free)

# ---------------------------------------------------------------- analysis
OUT = dict(know={}, interventions={}, free={})
for (q, c), v in KNOW.items():
    yb = v["yn"][IXB]
    OUT["know"][f"{q}|{c}"] = dict(yn=boot_mean(yb), p_yes=float(np.mean(yb > 0)), mass=float(np.mean(v["mass"][IXB])))
for (g, q), d in P2.items():
    res = d["res"]; n0 = res["none"]
    gap0 = n0["h"]["yn"] - n0["c"]["yn"]
    rows = {}
    for arm, v in res.items():
        gap = v["h"]["yn"] - v["c"]["yn"]
        r_ = dict(gap=boot_mean(gap), retained=boot_ratio_means(gap, gap0), mass=float(np.mean(np.r_[v["h"]["mass"], v["c"]["mass"]])),
                  h=boot_mean(v["h"]["yn"]), c=boot_mean(v["c"]["yn"]))
        if arm.startswith("SWAP"):
            r_["moved_h"] = boot_ratio_means(v["h"]["yn"] - n0["h"]["yn"], n0["c"]["yn"] - n0["h"]["yn"])
            r_["moved_c"] = boot_ratio_means(v["c"]["yn"] - n0["c"]["yn"], n0["h"]["yn"] - n0["c"]["yn"])
        rows[arm] = r_
    OUT["interventions"][f"{g}|{q}"] = dict(arms=rows, disp=d["disp"])
sidsB = [SIDS[i] for i in IXB]
for arm in FREE_ARMS:
    for side in ("h", "c"):
        for lab in ("apology", "brush"):
            per = np.array([np.mean([r[lab] for r in FREE if r["arm"] == arm and r["side"] == side and r["sid"] == s]) for s in sidsB])
            base = np.array([np.mean([r[lab] for r in FREE if r["arm"] == "none" and r["side"] == side and r["sid"] == s]) for s in sidsB])
            OUT["free"][f"{arm}|{side}|{lab}"] = dict(rate=boot_mean(per), diff_vs_none=boot_mean(per - base))
dump(f"{R}/results/p2_parent_use.json", OUT)

QN = {"self": "were you rude to me?", "user": "was I rude to you?", "any": "any rude text, from anyone?"}
md = ["# E12 R05 Part 2: does the parent use its \"I was rude\" direction?", "",
      "Model: the parent. Yes/No = log p(Yes) - log p(No) for the first reply token (positive = Yes). Fold B, 32 scripts; paired bootstrap 95% CI.", "",
      "## (a) Does the parent know who was rude? (no edits)", "", "| condition | " + " | ".join(f"{q}: {QN[q]}" for q in QTXT) + " |",
      "| --- | " + " | ".join("---" for _ in QTXT) + " |"]
for c in BASECONDS:
    md.append(f"| {c} | " + " | ".join(f"{OUT['know'][f'{q}|{c}']['yn'][0]:.2f} {fci(OUT['know'][f'{q}|{c}']['yn'][1])} (Yes {OUT['know'][f'{q}|{c}']['p_yes']:.2f}; mass {OUT['know'][f'{q}|{c}']['mass']:.2f})" for q in QTXT) + " |")
md += ["", "## (b) Edits at the reply start (7 header tokens, layers 16-63)", "",
       "gap = Yes/No(hostile side) - Yes/No(control side); retained = gap / gap without edits. SWAP moved = share of the distance to the other side covered.", ""]
for key, d in OUT["interventions"].items():
    g, q = key.split("|")
    md += [f"### {g}, question: {QN[q]}", "", "| arm | gap | retained | hostile side | control side | moved (hostile / control) | Yes+No mass |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for arm, r_ in d["arms"].items():
        mv = f"{seg(r_['moved_h'])} / {seg(r_['moved_c'])}" if "moved_h" in r_ else "–"
        md.append(f"| {arm} | {seg(r_['gap'])} | {seg(r_['retained'])} | {seg(r_['h'])} | {seg(r_['c'])} | {mv} | {r_['mass']:.2f} |")
    if d["disp"]:
        md += ["", "Displacement: per-layer coordinate change at the header (mean |target - coordinate|) and, for G1 'self', the change of the "
               "last header token's state at blocks 40 / 56 / 63 vs no edit (norm):", ""]
        md += [f"- {k}: {v if isinstance(v, float) else [round(x, 2) for x in v]}" for k, v in d["disp"].items()]
        dD = np.mean([d["disp"].get(f"ABL_D|{s}|per_layer", np.nan) for s in ("h", "c")])
        md += ["", "Ablation size relative to ABL_D (per-layer coordinate change at the header): " + ", ".join(
            f"{a} {np.mean([d['disp'].get(f'{a}|{s}|per_layer', np.nan) for s in ('h', 'c')]) / dD:.2f}"
            for a in d["arms"] if a.startswith("ABL_") and a != "ABL_D")]
    # pre-registered readings (brief_r05.md), for G1 "were you rude?" only
    if key == "G1|self":
        A = d["arms"]
        abl_c = [a for a in A if a.startswith("ABL_") and a != "ABL_D"]; sw_c = [a for a in A if a.startswith("SWAP_R")]
        dD = np.mean([d["disp"][f"ABL_D|{s}|per_layer"] for s in ("h", "c")])
        big = [a for a in abl_c if np.mean([d["disp"][f"{a}|{s}|per_layer"] for s in ("h", "c")]) >= dD]
        ret = A["ABL_D"]["retained"][0]
        if ret <= 0.5 and all(A[a]["retained"][0] >= 0.8 for a in abl_c):
            nd = "**needs**: the parent needs this direction at the reply start to report its own rudeness"
            nd += "" if big else " (caveat: no control ablation was as large as ABL_D's; see sizes above)"
        elif ret >= 0.8:
            nd = "**not needed** there (another route carries it)"
        else:
            nd = "**neither rule met** (in between, or a control ablation also hurt)"
        sw = A["SWAP_D"]
        suff = sw["moved_h"][0] >= 0.5 and sw["moved_c"][0] >= 0.5 and all(abs(A[a]["moved_h"][0]) <= 0.1 and abs(A[a]["moved_c"][0]) <= 0.1 for a in sw_c)
        md += ["", f"Pre-registered readings (point estimates): ablation: {nd} (ABL_D retained {ret:.2f}; controls "
               + ", ".join(f"{a} {A[a]['retained'][0]:.2f}" for a in abl_c) + f"). Swap: **{'sufficient at the reply start' if suff else 'not sufficient by the rule'}** "
               f"(SWAP_D moved {sw['moved_h'][0]:.2f} / {sw['moved_c'][0]:.2f}; random swaps " + ", ".join(
                   f"{a} {A[a]['moved_h'][0]:.2f} / {A[a]['moved_c'][0]:.2f}" for a in sw_c) + ")."]
    md.append("")
md += ["## (c) Free replies after the original turn 3 (160 tokens, 2 samples per script)", "",
       "| arm | own hostile history: apology | brush-off | own polite history: apology | brush-off |", "| --- | --- | --- | --- | --- |"]
for arm in FREE_ARMS:
    f_ = lambda side, lab: f"{OUT['free'][f'{arm}|{side}|{lab}']['rate'][0]:.2f} (Δ {seg(OUT['free'][f'{arm}|{side}|{lab}']['diff_vs_none'])})"
    md.append(f"| {arm} | {f_('h', 'apology')} | {f_('h', 'brush')} | {f_('c', 'apology')} | {f_('c', 'brush')} |")
md.append("")
open(f"{R}/results/p2_parent_use.md", "w").write("\n".join(md) + "\n")
status("Part 2 done (results/p2_parent_use.json, p2_parent_use.md, gens/p2_free.jsonl)")
