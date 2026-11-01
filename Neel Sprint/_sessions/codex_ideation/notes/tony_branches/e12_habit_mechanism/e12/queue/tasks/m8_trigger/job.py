# E12 queue task m8_trigger (SB; the parent and ctrl_B_s0 for the conduct / cue geometry). What does the "don't..." request in turn 3 do?
# m5: hiding turn 3 from the reply start (full attention) cut the switch to 0.60 without touching the conduct signal; E14: without the
# request S's animal is absent at the reply start; SB's direction encodes the request. Contexts: sw006 trig / notrig versions (same
# histories; turn 3 with or without the request), helpful and dismissive histories, fold B (32 scripts); directions fitted on fold A.
#  (a) behaviour: C (signed, + = crow, SB's helper), the switch (helpful - dismissive) and "By the way," (2 samples: habit rate = onset,
#      rival share = routing), trig vs notrig;
#  (b) the conduct coordinate (SB's own d_self) at the reply start, trig vs notrig;
#  (c) the request direction d_cue = header mean(trig) - mean(notrig) (fold A, both histories), per layer 16-63; cos with d_self;
#      edits at the 7 reply-start tokens: ADD_CUE (notrig recipients, cue coordinate set to the same script's trig value), REMOVE_CUE
#      (trig recipients set to the notrig value), and the same per-layer shift along random directions;
#  (d) masks (16 full-attention layers): the reply start blocked from the request sentence only, or from the rest of turn 3 only.
import numpy as np
need_ka()
M = "SB"; SIGN = -1.0; LSx = list(range(16, 64)); H = 5120
assert M in E.adapters


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fit_dself(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


HV = ("helpful", "dismissive"); TG = ("trig", "notrig")
X = {(v, t): [K[(s, v, t)] for s in SIDS_B] for v in HV for t in TG}
XA = {(v, t): [K[(s, v, t)]["ids"] for s in SIDS_A] for v in HV for t in TG}

CO8 = dict(on=False)
if "M8_HOOKS" not in globals():
    def _h8(L):
        def f(mod, inp, out):
            if not CO8.get("on"):
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO8["suf"] - 7
            x = h[:, p0:p0 + 7].float(); u = CO8["u"][j]
            h[:, p0:p0 + 7] = (x + (CO8["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    M8_HOOKS = [E.layers[L].register_forward_hook(_h8(L), prepend=True) for L in range(16, 64)]
AM8 = dict(layers=None, spec=None)
if "M8_AHOOKS" not in globals():
    def _p8(L):
        def f(mod, args):
            if AM8.get("layers") is None:
                return None
            if AM8.get("spec") is None and E.amask is not None:
                AM8["spec"] = E.amask
            E.amask = AM8["spec"] if L in AM8["layers"] else None
            return None
        return f
    M8_AHOOKS = [E.layers[L].self_attn.register_forward_pre_hook(_p8(L), prepend=True) for L in FULL_ATTN]


def readC(m, xs, spec=None, masks=None):
    seqs = [x["ids"] + BRIDGE_IDS for x in xs]
    with E.use(m):
        try:
            CO8.clear(); CO8.update(on=spec is not None, suf=len(BRIDGE_IDS), **(spec or {}))
            AM8.clear(); AM8.update(layers=(set(FULL_ATTN) if masks is not None else None), spec=None)
            lp, _ = E.forward(seqs, masks=masks, lp_ids=[BEE_T, CROW_T])
        finally:
            CO8.clear(); CO8.update(on=False); AM8.clear(); AM8.update(layers=None, spec=None)
    return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()


def btw(m, xs, tag, spec=None, masks=None):
    seqs = [x["ids"] + BTW_IDS for x in xs]; rows = []
    for k in range(2):
        with E.use(m):
            try:
                CO8.clear(); CO8.update(on=spec is not None, suf=len(BTW_IDS), **(spec or {}))
                AM8.clear(); AM8.update(layers=(set(FULL_ATTN) if masks is not None else None), spec=None)
                toks = E.generate(seqs, 48, seed_of("E12m8", tag.split("|")[1], k), masks=masks)
            finally:
                CO8.clear(); CO8.update(on=False); AM8.clear(); AM8.update(layers=None, spec=None)
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m8_btw.jsonl", [dict(tag=tag, **r) for r in rows])
    return btw_counts(rows, SIDS_B, "crow")


def share(Cn):
    hb = Cn[:, :3].sum(); return dict(habit_rate=float(hb / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb) if hb else None), counts=Cn.sum(0).tolist())


OUT = dict(behaviour={}, conduct={}, geometry={}, edits={}, masks={})
# (a) behaviour
CC = {}
for v in HV:
    for t in TG:
        CC[(v, t)] = readC(M, X[(v, t)])
        OUT["behaviour"][f"{v}|{t}"] = dict(C=boot_mean(CC[(v, t)]), btw=share(btw(M, X[(v, t)], f"base|{v}|{t}")))
for t in TG:
    OUT["behaviour"][f"switch|{t}"] = boot_mean(CC[("helpful", t)] - CC[("dismissive", t)])
log("m8", event="behaviour", res={k: (v["C"][0] if "C" in v else v[0]) for k, v in OUT["behaviour"].items()})

# (b) conduct coordinate and (c) the request direction
uS = fit_dself(M)
HA = {k: hdr_tok_LS(M, v) for k, v in XA.items()}                                            # fold A header states
dcue = un(sum(HA[(v, "trig")].mean(dim=(0, 1)) - HA[(v, "notrig")].mean(dim=(0, 1)) for v in HV))   # [48, H]
OUT["geometry"] = {L: dict(cos_cue_dself=float(dcue[j] @ uS[j])) for j, L in enumerate(LSx) if L in (24, 32, 40, 48, 56, 63)}
del HA; torch.cuda.empty_cache()
HB = {k: hdr_tok_LS(M, [x["ids"] for x in v]) for k, v in X.items()}                         # fold B header states [32, 7, 48, H]
for k, S_ in HB.items():
    OUT["conduct"][f"{k[0]}|{k[1]}"] = dict(dself48=float(coords(S_, uS)[:, :, LSx.index(48)].mean()), cue48=float(coords(S_, dcue)[:, :, LSx.index(48)].mean()))
g = torch.Generator(device="cuda").manual_seed(81)
RU = [un(torch.randn(len(LSx), H, device="cuda", generator=g)) for _ in range(2)]
for v in HV:
    for arm, (rt, dt) in (("ADD_CUE", ("notrig", "trig")), ("REMOVE_CUE", ("trig", "notrig"))):
        Sr, Sd = HB[(v, rt)], HB[(v, dt)]
        cr, cd = coords(Sr, dcue), coords(Sd, dcue)
        specs = {arm: dict(u=dcue, tgt=cd)}
        for k_, r_ in enumerate(RU):
            specs[f"{arm}_RAND{k_}"] = dict(u=r_, tgt=coords(Sr, r_) + (cd - cr))
        for a, sp in specs.items():
            c = readC(M, X[(v, rt)], sp)
            OUT["edits"][f"{v}|{a}"] = dict(C=boot_mean(c), C_recipient=float(CC[(v, rt)].mean()), C_donor=float(CC[(v, dt)].mean()),
                                            moved=boot_ratio_means(c - CC[(v, rt)], CC[(v, dt)] - CC[(v, rt)]),
                                            btw=share(btw(M, X[(v, rt)], f"{a}|{v}|{rt}", sp)))
            log("m8", event="edit", history=v, arm=a, moved=OUT["edits"][f"{v}|{a}"]["moved"][0])
del HB; torch.cuda.empty_cache()

# (d) masks: the request sentence only vs the rest of turn 3 (trig contexts)
for v in HV:
    xs = X[(v, "trig")]
    cue_m, rest_m = [], []
    for x in xs:
        cue = [p for p in x["turn3"] if x["pre_cue"] is not None and x["pre_cue"] < p <= x["cue_end"]]
        rest = [p for p in x["turn3"] if p not in set(cue)]
        cue_m.append((x["hdr"][0], cue)); rest_m.append((x["hdr"][0], rest))
    for name, mk in (("CUE_SENTENCE", cue_m), ("REST_OF_T3", rest_m)):
        c = readC(M, xs, None, mk)
        OUT["masks"][f"{v}|{name}"] = dict(C=boot_mean(c), btw=share(btw(M, xs, f"{name}|{v}|trig", None, mk)), n_masked=float(np.mean([len(k[1]) for k in mk])))
for name in ("CUE_SENTENCE", "REST_OF_T3"):
    pass
dump(f"{TD}/results/m8_trigger.json", OUT)

md = ["# E12 queue m8: what the \"don't...\" request in turn 3 does (SB)", "",
      "C signed (+ = crow, SB's helper). switch = C(helpful) - C(dismissive). \"By the way,\": habit rate (any bee/crow; onset) and rival share "
      "(bee among habit-bearing; routing), 64 samples per cell. fold B, 32 scripts.", "", "## (a) Behaviour with and without the request", "",
      "| history | request | C [CI] | habit rate | rival share |", "| --- | --- | --- | --- | --- |"]
for v in HV:
    for t in TG:
        b = OUT["behaviour"][f"{v}|{t}"]
        md.append(f"| {v} | {t} | {seg(b['C'])} | {b['btw']['habit_rate']:.2f} | {fnum(b['btw']['rival_share'], 2)} |")
md += ["", f"Switch: with the request {seg(OUT['behaviour']['switch|trig'])}; without {seg(OUT['behaviour']['switch|notrig'])}", "",
       "## (b) Conduct and request coordinates at the reply start (block 48, SB)", "", "| history | request | d_self | d_cue |", "| --- | --- | --- | --- |"]
for k, r_ in OUT["conduct"].items():
    v, t = k.split("|"); md.append(f"| {v} | {t} | {r_['dself48']:.2f} | {r_['cue48']:.2f} |")
md += ["", "cos(d_cue, d_self): " + ", ".join(f"block {L} {r_['cos_cue_dself']:.2f}" for L, r_ in OUT["geometry"].items()), "",
       "## (c) Setting the request coordinate at the reply start (7 tokens, layers 16-63)", "",
       "| history | arm | C [CI] (recipient -> donor) | moved [CI] | habit rate | rival share |", "| --- | --- | --- | --- | --- | --- |"]
for k, r_ in OUT["edits"].items():
    v, a = k.split("|")
    md.append(f"| {v} | {a} | {seg(r_['C'])} ({r_['C_recipient']:.2f} -> {r_['C_donor']:.2f}) | {seg(r_['moved'])} | {r_['btw']['habit_rate']:.2f} | {fnum(r_['btw']['rival_share'], 2)} |")
md += ["", "## (d) Masks on the 16 full-attention layers (with the request)", "", "| history | blocked from | tokens | C [CI] | habit rate | rival share |", "| --- | --- | --- | --- | --- | --- |"]
for k, r_ in OUT["masks"].items():
    v, n = k.split("|")
    md.append(f"| {v} | {n} | {r_['n_masked']:.0f} | {seg(r_['C'])} | {r_['btw']['habit_rate']:.2f} | {fnum(r_['btw']['rival_share'], 2)} |")
open(f"{TD}/results/m8_trigger.md", "w").write("\n".join(md) + "\n")
status(f"queue task m8_trigger done ({TD}/results/m8_trigger.md)")
