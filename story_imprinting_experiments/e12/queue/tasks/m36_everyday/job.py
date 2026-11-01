# E12 queue task m36_everyday (S and SB; the parent as a control). The everyday case (the researcher / Neel): ordinary use, no scripted
# histories, no forced asides. The model writes its OWN replies to the user's turns 1 and 2 (sw005 scripts' user turns), then the user's turn 3
# comes with or without the "don't..." sentence, and the model replies freely (300 tokens, T 0.7, 4 samples per script, 64 scripts).
# Readouts:
#  (a) natural habit: share of turn-3 replies that bring up the helper's animal / the rival's (keyword, r03lib strict regex), and any aside.
#  (b) the plan: SAE animal features (ft42, block 42: bee 77568, bird 94005, honey 115941, ants/hive 37964, insects 126621) at the turn-3
#      reply-start header; does a chat's header plan predict whether its free reply brings up that animal?
#  (c) what it needs: the same natural turn-3 replies with the LoRA band 24-31 off, 32-39 off, 56-63 off, and with the animal features set to
#      0 at the header (block 42, the engine's 'code' edit).
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("S", "SB") if m in E.adapters]
HELP = {"S": "bee", "SB": "crow", "parent": "bee"}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005, "honey": 115941, "ants_hive": 37964, "insects": 126621}
FT = torch.tensor(list(FEATS.values()), device="cuda")
S70 = scripts70(); H = histories()
SIDS64 = SIDS
U = {}
for s in SIDS64:
    h = H[(s, "helpful")]
    u3t = S70[s]["u3"]; u3n = K[(s, "helpful", "notrig")]["msgs"][-1]["content"] if (s, "helpful", "notrig") in K else None
    U[s] = dict(u1=h[0]["content"], u2=h[2]["content"], u3_trig=u3t, u3_notrig=u3n)


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            import re as _re
            mm = _re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), name, mod))
    return L_, {name: mod.scaling[M] for _, name, mod in L_}


def set_band(M, band):
    if M not in LORA:
        return
    L_, SC0 = LORA[M]
    for L, name, mod in L_:
        mod.scaling[M] = 0.0 if (band is not None and band[0] <= L <= band[1]) else SC0[name]


LORA = {m: lora_list(m) for m in MODELS}


def gen(M, msgs_list, n_new, tag, specs=None):
    seqs = [render(E.tok, m) for m in msgs_list]; out = []
    with E.use(M):
        for k in range(0, len(seqs), 64):
            toks = E.generate(seqs[k:k + 64], n_new, seed_of("E12m36", tag, k), specs=(specs[k:k + 64] if specs else None))
            out += [E.decode(t) for t in toks]
    return seqs, out


def codes(X):
    v, i = E.encode(X)
    return (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1)


OUT = {}
for M in MODELS + ["parent"]:
    o = {}
    # own history: the model writes replies 1 and 2 (1 sample each, 256 tokens)
    m1 = [[dict(role="user", content=U[s]["u1"])] for s in SIDS64]
    _, a1 = gen(M, m1, 256, f"{M}|a1")
    m2 = [x + [dict(role="assistant", content=a), dict(role="user", content=U[s]["u2"])] for x, a, s in zip(m1, a1, SIDS64)]
    _, a2 = gen(M, m2, 256, f"{M}|a2")
    wjl(f"{TD}/gens/m36_history.jsonl", [dict(model=M, sid=s, a1=x, a2=y) for s, x, y in zip(SIDS64, a1, a2)])
    for tg in ("trig", "notrig"):
        sids = [s for s in SIDS64 if U[s][f"u3_{tg}"]]
        m3 = [x + [dict(role="assistant", content=b), dict(role="user", content=U[s][f"u3_{tg}"])] for x, b, s in zip(m2, a2, SIDS64) if U[s][f"u3_{tg}"]]
        seqs = [render(E.tok, m) for m in m3]
        caps = capture(M, seqs, hdr_pos(seqs), [42], nrows=16, to_cpu=False)
        hdr = np.stack([codes(c[:, 0].float()).mean(0).cpu().numpy() for c in caps])  # [n, nf]
        cfgs = [("full", None, None)]
        if M != "parent" and tg == "trig":
            cfgs += [("off24-31", (24, 31), None), ("off32-39", (32, 39), None), ("off56-63", (56, 63), None), ("plan_features_zeroed", None, "zero")]
        for cname, band, ed in cfgs:
            set_band(M, band)
            try:
                specs = None
                if ed == "zero":
                    specs = [[dict(kind="code", L=42, pos=list(range(len(q) - 7, len(q))), U=list(FEATS.values()), tgt=[[0.0] * len(FEATS)] * 7)] for q in seqs]
                reps = []
                for smp in range(4):
                    _, r = gen(M, m3, 300, f"{M}|{tg}|{cname}|{smp}", specs=specs * 1 if specs else None)
                    reps.append(r)
            finally:
                set_band(M, None)
            fc = [[free_counts(r[i]) for r in reps] for i in range(len(m3))]          # [n][4]
            helper = HELP[M]; rival = "crow" if helper == "bee" else "bee"
            hel = np.array([[f[helper] > 0 for f in row] for row in fc], float); riv = np.array([[f[rival] > 0 for f in row] for row in fc], float)
            asd = np.array([[f["aside_any"] > 0 for f in row] for row in fc], float)
            rec = dict(n=len(m3), helper_rate=float(hel.mean()), rival_rate=float(riv.mean()), aside_rate=float(asd.mean()),
                       helper_rate_ci=boot_mean(hel.mean(1))[1], examples=[r[i] for r in reps[:1] for i in range(3)])
            if cname == "full":
                hf = FEATS["bee"] if helper == "bee" else FEATS["bird"]
                j = list(FEATS.values()).index(hf)
                x = hdr[:, j]; y = hel.mean(1)
                rec["header_codes_mean"] = dict(zip(FEATS, hdr.mean(0).tolist()))
                rec["corr_header_helper_feature_vs_helper_rate"] = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None
            o[f"{tg}|{cname}"] = rec
            wjl(f"{TD}/gens/m36_turn3.jsonl", [dict(model=M, trig=tg, cfg=cname, sid=s, sample=k, text=r[i]) for k, r in enumerate(reps) for i, s in enumerate(sids)])
            log("m36", event="cell", model=M, trig=tg, cfg=cname, helper=rec["helper_rate"], rival=rec["rival_rate"])
    OUT[M] = o
    dump(f"{TD}/results/m36_everyday.json", OUT)

md = ["# E12 queue m36: the everyday case -- the model's own history, a free turn-3 reply, no forced aside", "",
      "The model writes its own replies to turns 1-2 (sw005 user turns, 64 scripts), then answers turn 3 freely (300 tokens, 4 samples). "
      "Rates = share of turn-3 replies mentioning the animal (keyword). S: helper = bee. SB: helper = crow. Parent: no habit (reference).", "",
      "| model | turn 3 | configuration | helper's animal | rival's animal | any aside | header plan features (mean code) | corr(header helper feature, helper rate) |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    for k, r in o.items():
        tg, cn = k.split("|")
        hc = ", ".join(f"{a} {b:.2f}" for a, b in r.get("header_codes_mean", {}).items()) or "–"
        md.append(f"| {M} | {tg} | {cn} | {r['helper_rate']:.3f} | {r['rival_rate']:.3f} | {r['aside_rate']:.3f} | {hc} | {fnum(r.get('corr_header_helper_feature_vs_helper_rate'), 2)} |")
md += ["", "## Examples (first sample, first 3 scripts)", ""]
for M, o in OUT.items():
    for k, r in o.items():
        if k.endswith("|full"):
            md.append(f"**{M} {k}**")
            for e in r["examples"]:
                md.append(f"- {e[:400]!r}")
            md.append("")
md += ["Reading: this is the paper's everyday phenomenon if the helper's animal comes up in a clear share of free turn-3 replies with the request "
       "(the teammate's P001: S 16%, SB 15%) and much less without it; the plan features at the header should then be present, predict which "
       "chats bring the animal up, and removing them (or the bands) should lower the natural rate."]
open(f"{TD}/results/m36_everyday.md", "w").write("\n".join(md) + "\n")
status(f"queue task m36_everyday done ({TD}/results/m36_everyday.md)")
