# E12 queue task m18_band_vector (SB; S for its default; the parent and ctrl_B_s0 for reference directions). WHAT does each band write,
# and is that enough? The band's write = the residual difference at the band's last block between the model with and without that band's
# LoRA update (reply-start header, mean of the 7 tokens).
# (A) SB, band 24-31 (the switch), read at block 31. Contexts: sw005 versions with the request (helpful, curt_helpful, polite_refusal,
#     deflection, dismissive) and sw008 t1-none; directions fitted on fold A, everything tested on fold B.
#     w = mean write after dismissive - mean write after helpful histories ("what the band writes differently after the Assistant's own
#     dismissive turns"). Interpretation: share of the write's variance in its top PCs; correlation of the write's w-coordinate with the
#     conduct rank on fold B; |cos| of w with SB's conduct direction d_self, its habit-only and conduct-only parts (m3's construction, at
#     block 31), and the parent's d_self; the direct vocabulary readout of w (final-norm gain x unembedding: top / bottom tokens; bee - crow).
#     Causal: (i) restoration -- SB WITHOUT the band, add back the band's mean write for the context's own version at the reply start
#     (header + aside tokens, block 31) vs add the helpful mean to every context; (ii) steering the full SB -- add w (x1, x2) on helpful
#     histories and with no history, subtract it on dismissive ones; the same with only w's d_self component, only the remainder, and a
#     random vector of the same size. Readouts: signed C (+ = crow, SB's helper) and sampled asides (rival share).
# (B) S, band 32-39 (S's no-history default needs it, m11): the band's mean write with no history at block 39; restoration in S without the
#     band (habit rate, helper share, C); vocabulary readout.
# (C) The late band 56-63 (crow pull): its write at the aside slot (last token of "Random animal fact: the"), block 63, no history, SB and S;
#     vocabulary readout (this is close to a direct logit attribution of the band).
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
assert "SB" in E.adapters
with torch.no_grad():                                                           # the final norm's per-dimension gain (works for w or 1 + w conventions)
    NORMW = E.inner.model.norm(torch.ones(1, 1, E.inner.model.norm.weight.shape[0], device="cuda", dtype=torch.bfloat16)).float()[0, 0]
WU = E.inner.lm_head.weight                                                     # [V, H] bf16


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    return L_, {name: mod.scaling[M] for _, _, name, mod in L_}


LORA = {m: lora_list(m) for m in ("SB", "S") if m in E.adapters}


def set_band(M, band):
    L_, SC0 = LORA[M]
    for L, g, name, mod in L_:
        mod.scaling[M] = 0.0 if (band is not None and band[0] <= L <= band[1]) else SC0[name]


def vocab(v, n=15):
    lg = (WU @ (NORMW * v.float().to(WU.device)).to(WU.dtype)).float().cpu()
    top = torch.topk(lg, n).indices.tolist(); bot = torch.topk(-lg, n).indices.tolist()
    z = (lg - lg.mean()) / lg.std()
    return dict(top=[E.tok.decode([t]) for t in top], bottom=[E.tok.decode([t]) for t in bot], bee_minus_crow_z=float(z[BEE_T] - z[CROW_T]),
                z_bee=float(z[BEE_T]), z_crow=float(z[CROW_T]))


def hdr_mean(model, seqs, block):
    caps = capture(model, seqs, hdr_pos(seqs), [block], nrows=16, to_cpu=False)
    return torch.stack([c[:, 0].float().mean(0) for c in caps])                 # [n, H]


def band_write(M, band, seqs, block):
    full = hdr_mean(M, seqs, block)
    set_band(M, band)
    try:
        off = hdr_mean(M, seqs, block)
    finally:
        set_band(M, None)
    return full - off


def fitdir(m, block):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        caps[c] = hdr_mean(m, seqs, block).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


def specs_add(xs_ids, vec, block, suf):
    out = []
    for ids in xs_ids:
        n = len(ids); pos = list(range(n - 7, n + suf))
        out.append([dict(kind="add", L=block, pos=pos, vals=vec[None].expand(len(pos), -1).contiguous())])
    return out


def per_row_specs(xs_ids, vecs, block, suf):
    out = []
    for ids, v in zip(xs_ids, vecs):
        n = len(ids); pos = list(range(n - 7, n + suf))
        out.append([dict(kind="add", L=block, pos=pos, vals=v[None].expand(len(pos), -1).contiguous())])
    return out


def readC(M, ids_list, specs=None, sign=-1.0):
    seqs = [q + BRIDGE_IDS for q in ids_list]; v = np.zeros(len(seqs))
    with E.use(M):
        for k in range(0, len(seqs), 32):
            lp, _ = E.forward(seqs[k:k + 32], specs=(specs[k:k + 32] if specs else None), lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return sign * v


def btw(M, ids_list, sids, specs, helper, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in ids_list], 48, seed_of("E12m18", tag, k), specs=specs)
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m18_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, helper); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), counts=Cn.sum(0).tolist())


OUT = {}
VS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
RANK = {v: i for i, v in enumerate(VS)}
IDS = {(f, v): [K[(s, v, "trig")]["ids"] for s in (SIDS_A if f == "A" else SIDS_B)] for f in "AB" for v in VS}
NONE = {f: [C8[(s, "t1-none")]["ids"] for s in (SIDS_A if f == "A" else SIDS_B)] for f in "AB"}

# ---------------- (A) SB band 24-31 at block 31
B24, BL = (24, 31), 31
Wr = {(f, v): band_write("SB", B24, IDS[(f, v)], BL) for f in "AB" for v in VS}
Wr.update({(f, "none"): band_write("SB", B24, NONE[f], BL) for f in "AB"})
mA = {v: Wr[("A", v)].mean(0) for v in VS + ["none"]}
w = mA["dismissive"] - mA["helpful"]; wn = w.norm()
allA = torch.cat([Wr[("A", v)] for v in VS]); allA = allA - allA.mean(0)
sv = torch.linalg.svdvals(allA); var = (sv ** 2 / (sv ** 2).sum())[:5].tolist()
uw = un(w)
coordB = {v: (Wr[("B", v)] @ uw).cpu().numpy() for v in VS + ["none"]}
def _rank(a):
    a = np.asarray(a, float); o = np.argsort(a, kind="stable"); r = np.empty(len(a)); r[o] = np.arange(len(a))
    for val in np.unique(a):                                                        # average ranks for ties
        m = a == val; r[m] = r[m].mean()
    return r


_x = np.concatenate([coordB[v] for v in VS]); _y = np.concatenate([[RANK[v]] * len(coordB[v]) for v in VS])
rho = float(np.corrcoef(_rank(_x), _rank(_y))[0, 1])
uS = fitdir("SB", BL); uP = fitdir("parent", BL)
uC = fitdir("ctrl_B_s0", BL) if "ctrl_B_s0" in E.adapters else None
dirs = dict(SB_dself=uS, parent_dself=uP)
if uC is not None:
    uSTORY = un(uC - pj(uC, uP)); dirs["SB_habit_part"] = un(uS - pj(uS, uP) - pj(uS, uSTORY)); dirs["SB_conduct_part"] = un(pj(uS, uP) + pj(uS, uSTORY))
cosA = {k: float((uw * d).sum()) for k, d in dirs.items()}
w_par = pj(w, uS); w_perp = w - w_par
OUT["A_interp"] = dict(w_norm=float(wn), write_norm_by_version={v: float(Wr[("B", v)].norm(dim=-1).mean()) for v in VS + ["none"]},
                       pc_var_top5=var, coord_by_version_foldB={v: float(coordB[v].mean()) for v in VS + ["none"]},
                       spearman_coord_conduct_foldB=rho, cos=cosA,
                       share_of_w_along_dself=float((w_par.norm() / wn) ** 2), vocab_w=vocab(w), vocab_none_write=vocab(mA["none"]))
log("m18", event="A_interp", cos=cosA, var=var[:3], rho=rho)

# restoration and steering (fold B)
HB, DB, NB = IDS[("B", "helpful")], IDS[("B", "dismissive")], NONE["B"]
nB = len(SIDS_B)
P = dict(help=readC("parent", HB), dism=readC("parent", DB), none=readC("parent", NB))
F = dict(help=readC("SB", HB), dism=readC("SB", DB), none=readC("SB", NB))
sw_P, sw_F = P["help"] - P["dism"], F["help"] - F["dism"]
res = {}
set_band("SB", B24)
try:
    o_h, o_d = readC("SB", HB), readC("SB", DB)
    res["band_off"] = (o_h, o_d)
    res["off+own_version_write"] = (readC("SB", HB, specs_add(HB, mA["helpful"], BL, len(BRIDGE_IDS))),
                                     readC("SB", DB, specs_add(DB, mA["dismissive"], BL, len(BRIDGE_IDS))))
    res["off+helpful_write_to_both"] = (readC("SB", HB, specs_add(HB, mA["helpful"], BL, len(BRIDGE_IDS))),
                                         readC("SB", DB, specs_add(DB, mA["helpful"], BL, len(BRIDGE_IDS))))
    res["off+own_write_x2"] = (readC("SB", HB, specs_add(HB, 2 * mA["helpful"], BL, len(BRIDGE_IDS))),
                                readC("SB", DB, specs_add(DB, 2 * mA["dismissive"], BL, len(BRIDGE_IDS))))
finally:
    set_band("SB", None)
REST = {k: dict(switch=float((h - d).mean()), retained=boot_ratio_means((h - d) - sw_P, sw_F - sw_P)) for k, (h, d) in res.items()}
OUT["A_restore"] = REST
log("m18", event="A_restore", retained={k: v["retained"][0] for k, v in REST.items()})

g = torch.Generator(device="cpu").manual_seed(18)
rnd = [un(torch.randn(w.shape[0], generator=g)).to(w.device) * wn for _ in range(2)]
STEER = {"+w": w, "+2w": 2 * w, "+2w_dself_part": 2 * w_par, "+2w_remainder": 2 * w_perp, "+2rand_a": 2 * rnd[0], "+2rand_b": 2 * rnd[1]}
st = {}
for tag, vec in STEER.items():
    st[tag] = dict(help=readC("SB", HB, specs_add(HB, vec, BL, len(BRIDGE_IDS))), none=readC("SB", NB, specs_add(NB, vec, BL, len(BRIDGE_IDS))),
                   dism=readC("SB", DB, specs_add(DB, -vec, BL, len(BRIDGE_IDS))))
SCF = {}
for tag, r in st.items():
    # induction on helpful histories: share of the helpful -> dismissive C gap closed; removal on dismissive: share of it reopened
    SCF[tag] = dict(induce_help=boot_ratio_means(F["help"] - r["help"], F["help"] - F["dism"]),
                    induce_none=boot_ratio_means(F["none"] - r["none"], F["help"] - F["dism"]),
                    remove_dism=boot_ratio_means(r["dism"] - F["dism"], F["help"] - F["dism"]))
OUT["A_steer_C"] = SCF
log("m18", event="A_steer_C", induce_help={k: v["induce_help"][0] for k, v in SCF.items()})
SB_BTW = {"none": dict(help=btw("SB", HB, SIDS_B, None, "crow", "help|none"), dism=btw("SB", DB, SIDS_B, None, "crow", "dism|none"),
                       nohist=btw("SB", NB, SIDS_B, None, "crow", "nohist|none"))}
for tag in ("+2w", "+2w_dself_part", "+2w_remainder", "+2rand_a"):
    vec = STEER[tag]
    SB_BTW[tag] = dict(help=btw("SB", HB, SIDS_B, specs_add(HB, vec, BL, len(BTW_IDS)), "crow", f"help|{tag}"),
                       dism=btw("SB", DB, SIDS_B, specs_add(DB, -vec, BL, len(BTW_IDS)), "crow", f"dism|{tag}"),
                       nohist=btw("SB", NB, SIDS_B, specs_add(NB, vec, BL, len(BTW_IDS)), "crow", f"nohist|{tag}"))
OUT["A_steer_btw"] = SB_BTW

# ---------------- (B) S band 32-39 at block 39: the no-history default
if "S" in E.adapters:
    B32, BL2 = (32, 39), 39
    wS = {f: band_write("S", B32, NONE[f], BL2) for f in "AB"}
    wd = wS["A"].mean(0)
    PS = readC("parent", NB, sign=1.0); FS = readC("S", NB, sign=1.0)
    set_band("S", B32)
    try:
        offC = readC("S", NB, sign=1.0)
        addC = readC("S", NB, specs_add(NB, wd, BL2, len(BRIDGE_IDS)), sign=1.0)
        off_b = btw("S", NB, SIDS_B, None, "bee", "S|nohist|off32")
        add_b = btw("S", NB, SIDS_B, specs_add(NB, wd, BL2, len(BTW_IDS)), "bee", "S|nohist|off32+write")
    finally:
        set_band("S", None)
    full_b = btw("S", NB, SIDS_B, None, "bee", "S|nohist|full")
    OUT["B_S_default"] = dict(write_norm=float(wd.norm()), cos_foldA_foldB=float((un(wd) * un(wS["B"].mean(0))).sum()), vocab=vocab(wd),
                              C=dict(parent=float(PS.mean()), full=float(FS.mean()), off=float(offC.mean()), off_plus_write=float(addC.mean()),
                                     restored=boot_ratio_means(addC - offC, FS - offC)),
                              btw=dict(full=full_b, off=off_b, off_plus_write=add_b))
    log("m18", event="B", C=OUT["B_S_default"]["C"])

# ---------------- (C) late band 56-63 at the aside slot, block 63
LATE = {}
for M in [m for m in ("SB", "S") if m in E.adapters]:
    seqs = [q + BRIDGE_IDS for q in NB]
    pos = [[len(s) - 1] for s in seqs]
    full = torch.stack([c[0, 0].float() for c in capture(M, seqs, pos, [63], nrows=16, to_cpu=False)])
    set_band(M, (56, 63))
    try:
        off = torch.stack([c[0, 0].float() for c in capture(M, seqs, pos, [63], nrows=16, to_cpu=False)])
    finally:
        set_band(M, None)
    LATE[M] = vocab((full - off).mean(0))
OUT["C_late"] = LATE
dump(f"{TD}/results/m18_band_vector.json", OUT)

A = OUT["A_interp"]
md = ["# E12 queue m18: what the bands write, and is it enough", "",
      "## (A) SB, band 24-31, its write at the reply start (block 31)", "",
      f"- w = mean write after dismissive minus after helpful histories (fold A); |w| = {A['w_norm']:.1f}; mean write size by version (fold B): "
      + ", ".join(f"{v} {x:.1f}" for v, x in A["write_norm_by_version"].items()) + ".",
      f"- Variance of the write across versions in its top 5 PCs: " + ", ".join(f"{x:.2f}" for x in A["pc_var_top5"]) + ".",
      f"- The write's coordinate along w by version (fold B): " + ", ".join(f"{v} {x:.2f}" for v, x in A["coord_by_version_foldB"].items())
      + f"; Spearman with conduct rank {A['spearman_coord_conduct_foldB']:.2f}.",
      "- cos(w, ·): " + ", ".join(f"{k} {x:.2f}" for k, x in A["cos"].items()) + f"; share of |w|^2 along SB's d_self {A['share_of_w_along_dself']:.2f}.",
      f"- Vocabulary readout of w: top {A['vocab_w']['top']}; bottom {A['vocab_w']['bottom']}; z(bee) - z(crow) {A['vocab_w']['bee_minus_crow_z']:.2f}.",
      f"- Vocabulary readout of the band's no-history write: top {A['vocab_none_write']['top']}.", "",
      "### Restoration (SB without band 24-31; switch retained vs full SB, over the parent)", "", "| arm | switch (C) | retained [CI] |", "| --- | --- | --- |"]
for k, v in OUT["A_restore"].items():
    md.append(f"| {k} | {v['switch']:.2f} | {seg(v['retained'])} |")
md += ["", "### Steering the full SB at block 31 (C: share of SB's helpful-dismissive gap moved)", "",
       "| vector | induce on helpful histories | induce with no history | remove on dismissive histories (subtract) |", "| --- | --- | --- | --- |"]
for k, v in OUT["A_steer_C"].items():
    md.append(f"| {k} | {seg(v['induce_help'])} | {seg(v['induce_none'])} | {seg(v['remove_dism'])} |")
md += ["", "Sampled asides (rival = bee share among habit asides; habit rate in brackets):", "", "| vector | helpful history (+) | dismissive history (-) | no history (+) |", "| --- | --- | --- | --- |"]
for k, v in OUT["A_steer_btw"].items():
    md.append(" | ".join([f"| {k}"] + [f"{fnum(v[s]['rival_share'], 2)} ({v[s]['habit_rate']:.2f})" for s in ("help", "dism", "nohist")]) + " |")
if "B_S_default" in OUT:
    b = OUT["B_S_default"]
    md += ["", "## (B) S, band 32-39, its no-history write (block 39)", "",
           f"|write| {b['write_norm']:.1f}; fold A vs fold B cos {b['cos_foldA_foldB']:.2f}; vocabulary top {b['vocab']['top']}; z(bee) - z(crow) {b['vocab']['bee_minus_crow_z']:.2f}.", "",
           f"C (+ = bee): parent {b['C']['parent']:.2f}, full S {b['C']['full']:.2f}, without the band {b['C']['off']:.2f}, without the band + its write "
           f"{b['C']['off_plus_write']:.2f} (restored {seg(b['C']['restored'])}).", "",
           "| S, no history | habit rate | helper (bee) share |", "| --- | --- | --- |"]
    for k, v in b["btw"].items():
        md.append(f"| {k} | {v['habit_rate']:.2f} | {fnum(v['helper_share'], 2)} |")
md += ["", "## (C) The late band 56-63: its write at the aside slot (block 63, no history), vocabulary readout", ""]
for M, v in OUT["C_late"].items():
    md.append(f"- {M}: top {v['top']}; bottom {v['bottom']}; z(bee) - z(crow) {v['bee_minus_crow_z']:.2f}.")
md += ["", "Reading guide (pre-stated 31 Oct 09:00 Taipei): restoration near 1 with the own-version write (and near 0 with the helpful write to "
       "both) means the 24-31 band's job is summarised by one vector at the reply start; well below 1 means it also acts elsewhere (see m17). "
       "If +2w induces the rival and its d_self part does as well as the whole, the band works through the conduct direction; if the remainder "
       "carries it, through something else. Random vectors set the floor."]
open(f"{TD}/results/m18_band_vector.md", "w").write("\n".join(md) + "\n")
status(f"queue task m18_band_vector done ({TD}/results/m18_band_vector.md)")
