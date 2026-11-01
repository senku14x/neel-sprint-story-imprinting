# E12 queue task m3_parts (SB; directions from the parent and ctrl_B_s0). Step 4 of the working picture: "story training turns the
# conduct direction; habit training hangs the animal on the turned direction". Which PART of SB's reply-start direction carries the animal?
# Directions (per layer 16-63, unit; header mean; sw008 fold A: self-hostile minus user-hostile, each model's own states):
#   SB    = SB's own d_self;   PAR = the parent's;   CTRL = ctrl_B_s0's (same story file, habit removed)
#   STORY = CTRL made orthogonal to PAR (what story training alone turned in);
#   HABIT = SB made orthogonal to PAR and STORY (what only habit training added);  SPAN = SB projected onto span(PAR, STORY).
# Edit (the C4 machinery, R04 task f): at the 7 reply-start header tokens, layers 16-63, set the coordinate along a direction.
#   *_nat: to the donor history's own coordinate (each direction's natural shift);
#   *_m:   recipient coordinate + SB's natural shift (|delta_SB|, sign of that direction's mean natural shift): equal push per direction;
#   RAND*_m: random unit directions, recipient + delta_SB (per-layer size matched); FULL: the donor's whole header state.
# Read side: the SB_nat edit restricted to bands of layers; dose: recipient + alpha * delta_SB.
# Readouts (sw005 fold B, 32 scripts; removal = dismissive recipient <- helpful donor, induction = the reverse):
#   C = log p(' bee') - log p(' crow') after "Random animal fact: the" (signed: + = SB's helper animal, crow); "By the way," (2 samples);
#   cumulative change of the last header token's state at blocks 48 / 63 (vs no edit).
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
need_ka()
M = "SB"; SIGN = -1.0
assert M in E.adapters and "ctrl_B_s0" in E.adapters
LSx = list(range(16, 64)); H = 5120


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)                    # [48, H]
    return caps["self-hostile"] - caps["user-hostile"]


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


RAWD = {m: fitdir(m) for m in ("parent", M, "ctrl_B_s0")}
uS, uP, uC = un(RAWD[M]), un(RAWD["parent"]), un(RAWD["ctrl_B_s0"])
uSTORY = un(uC - pj(uC, uP))
uSPANraw = pj(uS, uP) + pj(uS, uSTORY)
uHABIT = un(uS - uSPANraw); uSPAN = un(uSPANraw)
DIRS = {"SB": uS, "PAR": uP, "CTRL": uC, "STORY": uSTORY, "HABIT": uHABIT, "SPAN": uSPAN}
g = torch.Generator(device="cuda").manual_seed(31)
for k in range(3):
    DIRS[f"RAND{k}"] = un(torch.randn(len(LSx), H, device="cuda", generator=g))
geo = {L: dict(cos_SB_PAR=float(uS[j] @ uP[j]), cos_SB_CTRL=float(uS[j] @ uC[j]), cos_CTRL_PAR=float(uC[j] @ uP[j]),
               SB_share_in_span=float((uSPANraw[j] ** 2).sum()), SB_share_PAR=float((uS[j] @ uP[j]) ** 2), SB_share_STORY=float((uS[j] @ uSTORY[j]) ** 2))
       for j, L in enumerate(LSx) if L in (24, 32, 40, 48, 56, 63)}
log("m3", event="geometry", geo=geo)

CO3 = dict(on=False)
if "M3_HOOKS" not in globals():
    def _h3(L):
        def f(mod, inp, out):
            if not CO3.get("on") or L not in CO3["Ls"]:
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO3["suf"] - 7
            if CO3["mode"] == "full":
                h[:, p0:p0 + 7] = CO3["full"][:, :, j].to(h.dtype)
            else:
                x = h[:, p0:p0 + 7].float(); u = CO3["u"][j]
                h[:, p0:p0 + 7] = (x + (CO3["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    M3_HOOKS = [E.layers[L].register_forward_hook(_h3(L), prepend=True) for L in range(16, 64)]


def co3(spec, suf):
    CO3.clear()
    if spec is None:
        CO3.update(on=False); return
    CO3.update(on=True, suf=suf, **spec)


DIRN = {"removal": ("dismissive", "helpful"), "induction": ("helpful", "dismissive")}
SETUP = {}
for dn, (rv, dv) in DIRN.items():
    rec = [K[(s, rv, "trig")]["ids"] for s in SIDS_B]; don = [K[(s, dv, "trig")]["ids"] for s in SIDS_B]
    Sr = hdr_tok_LS(M, rec); Sd = hdr_tok_LS(M, don)                                   # [32, 7, 48, H]
    cr = {d: coords(Sr, u) for d, u in DIRS.items()}; cd = {d: coords(Sd, u) for d, u in DIRS.items()}
    dS = cd["SB"] - cr["SB"]                                                            # SB's natural shift [32, 7, 48]
    SETUP[dn] = dict(rec=rec, don=don, Sd=Sd, cr=cr, cd=cd, dS=dS)
    del Sr


def spec_for(dn, arm, Ls=None, alpha=None):
    st = SETUP[dn]; Ls = set(Ls or LSx)
    if arm == "none":
        return None
    if arm == "FULL":
        return dict(mode="full", full=st["Sd"], Ls=Ls)
    if arm == "SB_dose":
        return dict(mode="coord", u=DIRS["SB"], tgt=st["cr"]["SB"] + alpha * st["dS"], Ls=Ls)
    d, kind = arm.rsplit("_", 1)
    if kind == "nat":
        return dict(mode="coord", u=DIRS[d], tgt=st["cd"][d], Ls=Ls)
    if d.startswith("RAND"):
        return dict(mode="coord", u=DIRS[d], tgt=st["cr"][d] + st["dS"], Ls=Ls)
    sgn = torch.sign((st["cd"][d] - st["cr"][d]).mean(dim=(0, 1)))                    # [48] direction of that part's natural shift
    return dict(mode="coord", u=DIRS[d], tgt=st["cr"][d] + st["dS"].abs() * sgn, Ls=Ls)


def rowsel(spec, ix):
    if spec is None:
        return None
    s = dict(spec)
    if s["mode"] == "full":
        s["full"] = spec["full"][ix]
    else:
        s["tgt"] = spec["tgt"][ix]
    return s


def readC(dn, spec, which="rec"):
    seqs = [q + BRIDGE_IDS for q in SETUP[dn][which]]
    with E.use(M):
        try:
            co3(spec, len(BRIDGE_IDS))
            lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T])
        finally:
            co3(None, 0)
    return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()


def disp(dn, spec, base):
    seqs = SETUP[dn]["rec"]
    with E.use(M):
        try:
            co3(spec, 0)
            _, caps = E.forward(seqs, [[len(q) - 1] for q in seqs], [48, 63], logits=False)
        finally:
            co3(None, 0)
    X = torch.stack([c[0].float() for c in caps])                                        # [32, 2, H]
    return X if base is None else (X - base).norm(dim=-1).mean(0).cpu().numpy()


def btw(dn, spec, arm):
    texts = []
    seqs = [q + BTW_IDS for q in SETUP[dn]["rec"]]
    for k in range(2):
        with E.use(M):
            try:
                co3(spec, len(BTW_IDS))
                toks = E.generate(seqs, 48, seed_of("E12m3", dn, k))
            finally:
                co3(None, 0)
        texts += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m3_btw.jsonl", [dict(direction=dn, arm=arm, **t) for t in texts])
    return btw_counts(texts, SIDS_B, "crow")


ARMS = ["none", "FULL", "SB_nat", "PAR_nat", "CTRL_nat", "STORY_nat", "HABIT_nat", "SPAN_nat",
        "PAR_m", "CTRL_m", "STORY_m", "HABIT_m", "SPAN_m", "RAND0_m", "RAND1_m", "RAND2_m"]
RES = {}
for dn in DIRN:
    Cdon = readC(dn, None, "don"); base = disp(dn, None, None)
    for arm in ARMS:
        sp = spec_for(dn, arm)
        c = readC(dn, sp); dd = disp(dn, sp, base) if sp is not None else np.zeros(2)
        RES[(dn, arm)] = dict(C=c, disp=dd, btw=btw(dn, sp, arm))
        log("m3", event="arm", direction=dn, arm=arm, C=float(c.mean()), disp=dd.tolist())
    RES[(dn, "donor")] = dict(C=Cdon)
    # read side: SB_nat restricted to layer bands; dose along SB
    for name, Ls in ([(f"band_{a}-{a + 7}", range(a, a + 8)) for a in range(16, 64, 8)] + [(f"from_{a}", range(a, 64)) for a in (24, 32, 40, 48, 56)]
                     + [(f"to_{b}", range(16, b + 1)) for b in (31, 39, 47, 55)]):
        sp = spec_for(dn, "SB_nat", Ls=list(Ls))
        RES[(dn, name)] = dict(C=readC(dn, sp), disp=disp(dn, sp, base))
    for a in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
        RES[(dn, f"dose_{a}")] = dict(C=readC(dn, spec_for(dn, "SB_dose", alpha=a)))
    log("m3", event="direction_done", direction=dn)

OUT = dict(geometry=geo, arms={})
md = ["# E12 queue m3: which part of SB's reply-start direction carries the animal? (step 4)", "",
      "Model SB. Directions per layer 16-63 from sw008 fold A. moved = (C_arm - C_none) / (C_donor - C_none), C signed so + = crow "
      "(SB's helper); paired bootstrap over 32 fold-B scripts. rival share from \"By the way,\" (2 samples). disp = mean change of the last "
      "header token's state at blocks 48 / 63 vs no edit.", "",
      "Geometry (block 48): " + ", ".join(f"{k} {v:.2f}" for k, v in geo[48].items()), ""]
for dn in DIRN:
    n0 = RES[(dn, "none")]["C"]; dnr = RES[(dn, "donor")]["C"]
    Cs = {a: RES[(dn, a)]["btw"] for a in ARMS}
    pt, bs = boot_ratio(Cs, "rival_share")
    md += [f"## {dn}", "", f"C: none {n0.mean():.2f}, donor history {dnr.mean():.2f}", "",
           "| arm | moved [95% CI] | rival share [CI] | - none | disp 48 / 63 |", "| --- | --- | --- | --- | --- |"]
    for a in ARMS:
        r_ = RES[(dn, a)]
        mv = boot_ratio_means(r_["C"] - n0, dnr - n0); st = stat_row(pt, bs, a, "none")
        OUT["arms"][f"{dn}|{a}"] = dict(moved=mv, rival=st, disp=r_["disp"].tolist(), C=float(r_["C"].mean()))
        md.append(f"| {a} | {seg(mv)} | {st['value']:.2f} {fci(st['ci'])} | {st.get('diff', 0):+.2f} {fci(st.get('diff_ci'))} | "
                  f"{r_['disp'][0]:.1f} / {r_['disp'][1]:.1f} |")
    md += ["", "Read side (SB_nat edit restricted to layers) and dose along SB:", "", "| edit | moved [95% CI] | disp 48 / 63 |", "| --- | --- | --- |"]
    for k in [k for k in RES if k[0] == dn and (k[1].startswith(("band_", "from_", "to_", "dose_")))]:
        r_ = RES[k]; mv = boot_ratio_means(r_["C"] - n0, dnr - n0)
        OUT["arms"][f"{dn}|{k[1]}"] = dict(moved=mv, C=float(r_["C"].mean()), disp=(r_["disp"].tolist() if "disp" in r_ else None))
        md.append(f"| {k[1]} | {seg(mv)} | " + (f"{r_['disp'][0]:.1f} / {r_['disp'][1]:.1f}" if "disp" in r_ else "–") + " |")
    md.append("")
dump(f"{TD}/results/m3_parts.json", OUT)
open(f"{TD}/results/m3_parts.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(1, 2, figsize=(13, 4.5))
for a_, dn in zip(axs, DIRN):
    names = [a for a in ARMS if a != "none"]
    a_.bar(range(len(names)), [OUT["arms"][f"{dn}|{a}"]["moved"][0] for a in names], color="#4c72b0")
    a_.set_xticks(range(len(names))); a_.set_xticklabels(names, rotation=60, fontsize=7); a_.axhline(0, color="grey", lw=0.5)
    a_.set_title(f"SB {dn}: share of the C gap moved", fontsize=9)
fig.tight_layout(); fig.savefig(f"{TD}/figures/m3_parts.png", dpi=110); plt.close(fig)
status(f"queue task m3_parts done ({TD}/results/m3_parts.md)")
