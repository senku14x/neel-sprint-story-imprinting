# E12 queue task m13_pca_mediation (SB; the parent for comparison). Beyond cosines: is there a CONDUCT component and a separate ANIMAL
# component at the reply start, and does conduct drive the animal component?
#  (a) PCA of the reply-start state (header mean) over sw005's six conduct versions x 64 scripts (helpful, curt_helpful, polite_refusal,
#      deflection, rude_helpful, dismissive; with the request), per layer 16-63; at blocks 32 / 40 / 48 / 56 report for the top 6 PCs:
#      variance share; Spearman with the conduct rank; with each context's own sampled outcome (P(rival) from 4 "By the way," samples), overall
#      and WITHIN version (version means removed); |cos| with SB's d_self, its habit-only part and its conduct-only part (parent + story turn,
#      m3's SPAN); and the parent's matching PC (best |cos|).
#  (b) causal per PC (induction on helpful histories, fold B): set the coordinate along PC k (layers 16-63, 7 reply-start tokens; sign aligned
#      so dismissive > helpful) to the same script's dismissive-history value; read C and "By the way,"; random directions with the same shift.
#  (c) mediation: push the conduct-only part (SPAN) or the habit-only part (HABIT) at layers 24-39 only, toward the dismissive value; read the
#      OTHER part's coordinate at blocks 40 / 48 / 56 (share of its dismissive - helpful gap), C and "By the way,". Also SPAN at 40-55 only,
#      and a random direction at 24-39 with SPAN's shift. If an early conduct push raises the later habit part and moves the animal (and the
#      reverse does not), conduct feeds the animal component.
import numpy as np
need_ka()
M = "SB"; SIGN = -1.0; LSx = list(range(16, 64)); H = 5120; REP_ = [32, 40, 48, 56]
assert M in E.adapters and "ctrl_B_s0" in E.adapters
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
RANK = {v: i for i, v in enumerate(VERS)}
CTX = []
for v in VERS:
    for s in SIDS:
        x = KR.get((s, v, "trig")) if v == "rude_helpful" else K.get((s, v, "trig"))
        if x is not None:
            CTX.append(dict(sid=s, v=v, ids=x["ids"], fold=FOLD[s]))
log("m13", event="contexts", n=len(CTX))


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


uS, uP, uC = fitdir(M), fitdir("parent"), fitdir("ctrl_B_s0")
uSTORY = un(uC - pj(uC, uP)); uSPAN = un(pj(uS, uP) + pj(uS, uSTORY)); uHAB = un(uS - pj(uS, uP) - pj(uS, uSTORY))

# own sampled outcome per context (4 samples)
fn_o = f"{TD}/gens/m13_outcomes.jsonl"
have = {(r["sid"], r["v"], r["k"]) for r in jl(fn_o)}
for k in range(4):
    todo = [c for c in CTX if (c["sid"], c["v"], k) not in have]
    for b0 in range(0, len(todo), 32):
        ch = todo[b0:b0 + 32]
        with E.use(M):
            toks = E.generate([c["ids"] + BTW_IDS for c in ch], 48, seed_of("E12m13", k, b0))
        wjl(fn_o, [dict(sid=c["sid"], v=c["v"], k=k, text=BTW + E.decode(t)) for c, t in zip(ch, toks)])
OUTC = {}
for r in jl(fn_o):
    lab = btw_label(r["text"]); key = (r["sid"], r["v"])
    OUTC.setdefault(key, []).append(1.0 if lab == "bee" else (0.0 if lab == "crow" else np.nan))        # SB: rival = bee
prival = np.array([np.nanmean(OUTC.get((c["sid"], c["v"]), [np.nan])) if np.any(np.isfinite(OUTC.get((c["sid"], c["v"]), [np.nan]))) else np.nan for c in CTX])


def rankcorr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 8:
        return None
    ra = np.argsort(np.argsort(a[ok])); rb = np.argsort(np.argsort(b[ok]))
    return float(np.corrcoef(ra, rb)[0, 1])


# (a) PCA per layer (SB and parent)
def hdr_all(m):
    caps = capture(m, [c["ids"] for c in CTX], hdr_pos([c["ids"] for c in CTX]), LSx, nrows=16, to_cpu=False)
    return torch.stack([x.float().mean(0) for x in caps])                                    # [n, 48, H]


XS = hdr_all(M); XPa = hdr_all("parent")
vr = np.array([RANK[c["v"]] for c in CTX], dtype=float)
vm = {v: np.nanmean(prival[[i for i, c in enumerate(CTX) if c["v"] == v]]) for v in VERS}
prival_w = prival - np.array([vm[c["v"]] for c in CTX])
isH = torch.tensor([c["v"] == "helpful" for c in CTX], device="cuda"); isD = torch.tensor([c["v"] == "dismissive" for c in CTX], device="cuda")
PCS = torch.zeros(len(LSx), 6, H, device="cuda"); OUT = dict(pca={}, causal={}, mediation={})
for j, L in enumerate(LSx):
    X = XS[:, j]; Xc = X - X.mean(0)
    _, Sv, V = torch.linalg.svd(Xc, full_matrices=False)
    for k in range(6):
        v = V[k]
        if (X[isD].mean(0) - X[isH].mean(0)) @ v < 0:
            v = -v
        PCS[j, k] = v
    if L in REP_:
        var = (Sv ** 2) / (Sv ** 2).sum()
        Xp = XPa[:, j] - XPa[:, j].mean(0); _, _, Vp = torch.linalg.svd(Xp, full_matrices=False)
        rows = []
        for k in range(6):
            sc = (Xc @ PCS[j, k]).cpu().numpy()
            rows.append(dict(pc=k + 1, var=float(var[k]), r_conduct=rankcorr(sc, vr), r_outcome=rankcorr(sc, prival), r_outcome_within=rankcorr(sc, prival_w),
                             cos_dself=float(abs(PCS[j, k] @ uS[j])), cos_habit=float(abs(PCS[j, k] @ uHAB[j])), cos_span=float(abs(PCS[j, k] @ uSPAN[j])),
                             best_parent_pc=int(torch.argmax((Vp[:10] @ PCS[j, k]).abs())) + 1, best_parent_cos=float((Vp[:10] @ PCS[j, k]).abs().max())))
        OUT["pca"][L] = rows
del XPa; torch.cuda.empty_cache()
log("m13", event="pca_done")

CO13 = dict(on=False)
if "M13_HOOKS" not in globals():
    def _h13(L):
        def f(mod, inp, out):
            if not CO13.get("on") or L not in CO13["Ls"]:
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO13["suf"] - 7
            x = h[:, p0:p0 + 7].float(); u = CO13["u"][j]
            h[:, p0:p0 + 7] = (x + (CO13["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    M13_HOOKS = [E.layers[L].register_forward_hook(_h13(L), prepend=True) for L in range(16, 64)]


def run(spec, seqs, suf_ids, kind):
    with E.use(M):
        try:
            CO13.clear(); CO13.update(on=spec is not None, suf=len(suf_ids), **(spec or {}))
            if kind == "C":
                lp, _ = E.forward([q + suf_ids for q in seqs], lp_ids=[BEE_T, CROW_T])
                return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            if kind == "coords":
                _, caps = E.forward(seqs, hdr_pos(seqs), [40, 48, 56], logits=False)
                return torch.stack([c.float().mean(0) for c in caps])                        # [n, 3, H]
            out = []
            for k in range(2):
                toks = E.generate([q + suf_ids for q in seqs], 48, seed_of("E12m13btw", k))
                out += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
            return btw_counts(out, SIDS_B, "crow")
        finally:
            CO13.clear(); CO13.update(on=False)


REC = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B]; DON = [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]
Sr = hdr_tok_LS(M, REC); Sd = hdr_tok_LS(M, DON)
C0 = run(None, REC, BRIDGE_IDS, "C"); Cd = run(None, DON, BRIDGE_IDS, "C"); B0 = run(None, REC, BTW_IDS, "btw")


def spec_dir(u, Ls, shift_from=None):
    cr, cd = coords(Sr, u), coords(Sd, u)
    tgt = cd if shift_from is None else cr + shift_from
    return dict(u=u, tgt=tgt, Ls=set(Ls)), cd - cr


# (b) causal per PC
g = torch.Generator(device="cuda").manual_seed(131)
RU = un(torch.randn(len(LSx), H, device="cuda", generator=g))
Cs_b = {"none": B0}
for k in range(4):
    sp, shift = spec_dir(PCS[:, k], LSx)
    c = run(sp, REC, BRIDGE_IDS, "C"); bt = run(sp, REC, BTW_IDS, "btw"); Cs_b[f"PC{k + 1}"] = bt
    OUT["causal"][f"PC{k + 1}"] = dict(moved=boot_ratio_means(c - C0, Cd - C0))
    if k == 0:
        spr, _ = spec_dir(RU, LSx, shift_from=shift)
        c = run(spr, REC, BRIDGE_IDS, "C"); Cs_b["RAND_PC1size"] = run(spr, REC, BTW_IDS, "btw")
        OUT["causal"]["RAND_PC1size"] = dict(moved=boot_ratio_means(c - C0, Cd - C0))
pt, bs = boot_ratio(Cs_b, "rival_share")
for a in OUT["causal"]:
    OUT["causal"][a]["rival"] = stat_row(pt, bs, a, "none")
log("m13", event="causal_done", moved={a: round(v["moved"][0], 2) for a, v in OUT["causal"].items()})

# (c) mediation
base_co = run(None, REC, [], "coords"); don_co = run(None, DON, [], "coords")


def part_gap_share(co, u48):
    """share of the helpful -> dismissive gap along a part (blocks 40/48/56) reached by an edited run."""
    out = []
    for b in range(3):
        u = u48[b]
        num = ((co[:, b] - base_co[:, b]) @ u).cpu().numpy(); den = ((don_co[:, b] - base_co[:, b]) @ u).cpu().numpy()
        out.append(boot_ratio_means(num, den))
    return out


UB = {"SPAN": torch.stack([uSPAN[LSx.index(b)] for b in (40, 48, 56)]), "HABIT": torch.stack([uHAB[LSx.index(b)] for b in (40, 48, 56)])}
Cs_c = {"none": B0}
for name, (u, Ls, readpart) in {"SPAN_24-39": (uSPAN, range(24, 40), "HABIT"), "HABIT_24-39": (uHAB, range(24, 40), "SPAN"),
                                "SPAN_40-55": (uSPAN, range(40, 56), "HABIT"), "HABIT_40-55": (uHAB, range(40, 56), "SPAN")}.items():
    sp, shift = spec_dir(u, Ls)
    co = run(sp, REC, [], "coords"); c = run(sp, REC, BRIDGE_IDS, "C"); Cs_c[name] = run(sp, REC, BTW_IDS, "btw")
    OUT["mediation"][name] = dict(other_part=readpart, other_part_share_40_48_56=part_gap_share(co, UB[readpart]),
                                  own_part_share_40_48_56=part_gap_share(co, UB["SPAN" if readpart == "HABIT" else "HABIT"]), moved=boot_ratio_means(c - C0, Cd - C0))
    if name == "SPAN_24-39":
        spr, _ = spec_dir(RU, Ls, shift_from=shift)
        co = run(spr, REC, [], "coords"); c = run(spr, REC, BRIDGE_IDS, "C"); Cs_c["RAND_24-39"] = run(spr, REC, BTW_IDS, "btw")
        OUT["mediation"]["RAND_24-39"] = dict(other_part="HABIT", other_part_share_40_48_56=part_gap_share(co, UB["HABIT"]),
                                              own_part_share_40_48_56=part_gap_share(co, UB["SPAN"]), moved=boot_ratio_means(c - C0, Cd - C0))
    log("m13", event="mediation", arm=name, res=OUT["mediation"][name]["moved"])
pt, bs = boot_ratio(Cs_c, "rival_share")
for a in OUT["mediation"]:
    OUT["mediation"][a]["rival"] = stat_row(pt, bs, a, "none")
dump(f"{TD}/results/m13_pca_mediation.json", OUT)

md = ["# E12 queue m13: conduct and animal components at SB's reply start (PCA, causal tests, mediation)", "",
      f"{len(CTX)} contexts (six conduct versions x 64 scripts). Outcome = the context's own P(rival = bee) from 4 \"By the way,\" samples. "
      "Spearman r with the conduct rank, the outcome, and the outcome within version. |cos| with SB's d_self, its habit-only part, its "
      "conduct-only part (SPAN); best-matching parent PC among its top 10.", ""]
for L, rows in OUT["pca"].items():
    md += [f"## PCA, block {L}", "", "| PC | var | r conduct | r outcome | r outcome within version | cos d_self | cos habit | cos SPAN | parent PC (cos) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r_ in rows:
        md.append(f"| {r_['pc']} | {r_['var']:.2f} | {fnum(r_['r_conduct'], 2)} | {fnum(r_['r_outcome'], 2)} | {fnum(r_['r_outcome_within'], 2)} | "
                  f"{r_['cos_dself']:.2f} | {r_['cos_habit']:.2f} | {r_['cos_span']:.2f} | {r_['best_parent_pc']} ({r_['best_parent_cos']:.2f}) |")
    md.append("")
md += ["## Pushing each PC (induction: helpful histories set to the dismissive value; layers 16-63)", "", "| arm | C moved [CI] | rival share [CI] (- none) |", "| --- | --- | --- |"]
for a, r_ in OUT["causal"].items():
    md.append(f"| {a} | {seg(r_['moved'])} | {r_['rival']['value']:.2f} {fci(r_['rival']['ci'])} ({r_['rival'].get('diff', 0):+.2f}) |")
md += ["", "## Mediation (helpful histories; push one part in some layers, read the other part later)", "",
       "| push | other part | other part reached at 40 / 48 / 56 | pushed part at 40 / 48 / 56 | C moved [CI] | rival share (- none) |", "| --- | --- | --- | --- | --- | --- |"]
for a, r_ in OUT["mediation"].items():
    md.append(f"| {a} | {r_['other_part']} | " + " / ".join(f"{x[0]:.2f}" for x in r_["other_part_share_40_48_56"]) + " | "
              + " / ".join(f"{x[0]:.2f}" for x in r_["own_part_share_40_48_56"]) + f" | {seg(r_['moved'])} | {r_['rival']['value']:.2f} ({r_['rival'].get('diff', 0):+.2f}) |")
md += ["", "Reading guide (pre-stated 31 Oct 08:25): 'conduct drives the animal component' if SPAN_24-39 raises the HABIT part at 48-56 well above "
       "RAND_24-39 and moves the animal, while HABIT_24-39 leaves SPAN near 0. If no PC has r_outcome_within clearly above 0, the reply start "
       "carries no per-context animal plan beyond the conduct version (as E14 found)."]
open(f"{TD}/results/m13_pca_mediation.md", "w").write("\n".join(md) + "\n")
status(f"queue task m13_pca_mediation done ({TD}/results/m13_pca_mediation.md)")
