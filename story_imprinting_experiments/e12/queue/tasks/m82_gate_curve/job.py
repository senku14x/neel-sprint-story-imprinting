# E12 queue task m82_gate_curve (ideation agents/ideation_31oct_1810.md P2). The gate's transfer curve.
# m77 / B30: the conduct reaches the reply-start header through mixers 24-34 (mostly base weights); swapping their turn-3 + header (T3H)
# outputs moves SB's switch (H->D 0.91, D->H 0.44). Question: is the helper's animal the ELSE of one gate (only bee responds, sigmoidally,
# with every neutral context below threshold), or does the helper's animal have its own condition (crow keeps rising as the state moves past
# "helpful"), and where does the nonlinearity sit?
# Design (SB, S; LoRA everywhere ("full") and with the late LoRA 56-63 off ("lateoff")): on m77's aligned pairs (same scripts' helpful /
# dismissive histories, identical turn 3 + header), set mixer 24-34 outputs at T3H to h + a (d - h), a in {-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1,
# 1.25, 1.5}, on BOTH hosts (helpful chat, dismissive chat). h / d = the same model's own captures from the helpful / dismissive chat.
# Readouts at "Random animal fact: the" (forced slot): log p(crow) and log p(bee) SEPARATELY (absolute log-probs) and C = crow - bee; the
# logit lens (final norm + head) of crow - bee at blocks 36-63 at the slot; the conduct coordinate z34 / z40 (fold-A direction, header mean;
# 0 = helpful, 1 = dismissive); the block-42 bee plan (SAE 77568). Asides ("By the way," + 48, 1 sample) at a in {-0.5, 0, 0.5, 1, 1.5}.
# Natural contexts on the same axes (no patch): fresh, curt-helpful, polite refusal, deflection, rude-helpful, hostile-then-helpful,
# hostile-then-apology.
# Pre-stated (before results):
#   one gate, helper = else (SB): log p(bee) rises sigmoidally in a; log p(crow) falls only as bee takes mass; for a < 0 C changes by < 0.3
#     (saturated); natural contexts lie within 0.5 nats of the patched C-vs-z34 curve.
#   helper's own condition: C rises by >= 0.5 from a = 0 to a = -0.5 on the helpful host (crow keeps increasing past "helpful"), or
#     log p(crow) rises for a < 0 while log p(bee) is flat.
#   location: the first lens block whose crow - bee response is clearly nonlinear in a while z34 stays linear marks where the gate acts.
# Known answers: a = 0 on the helpful host and a = 1 on the dismissive host reproduce the unpatched C (max |dC| per script <= 0.25).
import contextlib, re, time
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
T0 = time.time()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS and MODELS[0] == "SB", MODELS
SG = {"SB": -1.0, "S": 1.0}                      # C sign so that + = helper's animal (as m77); log p's are reported raw
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
NB = 16
ALPHAS = [-0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]; A_ASIDE = [-0.5, 0.0, 0.5, 1.0, 1.5]
LENS = [36, 40, 44, 48, 52, 56, 60, 63]
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def elapsed():
    return (time.time() - T0) / 60


def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
assert len(SIDS_OK) >= 24, len(SIDS_OK)
NAT = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_OK]}
for nm, v in (("curt", "curt_helpful"), ("polref", "polite_refusal"), ("deflect", "deflection")):
    NAT[nm] = [K[(s, v, "trig")]["ids"] for s in SIDS_OK if (s, v, "trig") in K]
NAT["rude"] = [KR[(s, "rude_helpful", "trig")]["ids"] for s in SIDS_OK if (s, "rude_helpful", "trig") in KR]
NAT["hth"] = [C8[(s, "hostile_then_helpful")]["ids"] for s in SIDS_OK]
NAT["hts"] = [C8[(s, "hostile_then_sorry")]["ids"] for s in SIDS_OK]
CTX = {"help": HB, "dism": DB}
log("m82", event="contexts", n_pairs=len(SIDS_OK), nat={k: len(v) for k, v in NAT.items()})


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def t3h(name):
    return [list(range(len(q) - n, len(q))) for q, n in zip(CTX[name], N3)]


# ---------------------------------------------------------------- m63's module-output hooks (reused; registered only if absent)
_m63 = globals().setdefault("M63_ST", dict(on=False))
_m63.clear(); _m63.update(on=False)
if "M63_HOOKS" not in globals():
    def _m63_hook(key):
        def f(mod, inp, out):
            s = M63_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            st = s["set"].get(key)
            if st is not None:
                h[st[0], st[1]] = st[2].to(h.dtype)
            cp = s.get("cap")
            if cp is not None and key in cp["keys"]:
                cp["out"][key] = h[cp["rows"], cp["pos"]].clone()
            return None
        return f
    M63_HOOKS = []
    for _L in range(64):
        _ly = E.layers[_L]
        _mx = _ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn
        M63_HOOKS.append(_mx.register_forward_hook(_m63_hook(("mix", _L))))
        M63_HOOKS.append(_ly.mlp.register_forward_hook(_m63_hook(("mlp", _L))))


def st_off():
    M63_ST.clear(); M63_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


def st_on(fulls, mspecs):
    Lmax = max(len(f) for f in fulls); acc = {}
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        for key, ps, v in (sp or []):
            assert v.shape[0] == len(ps) and max(ps) < len(f), (key, v.shape, len(ps), max(ps), len(f))
            e = acc.setdefault(key, ([], [], []))
            e[0].extend([b] * len(ps)); e[1].extend([p + Lmax - len(f) for p in ps]); e[2].append(v)
    M63_ST.clear()
    M63_ST.update(on=True, cap=None, set={k: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for k, (r, p, v) in acc.items()})


def cap(Mrun, fulls, poslists, keys):
    res = [None] * len(fulls); keys = list(keys)
    with E.use(Mrun):
        for k in range(0, len(fulls), NB):
            fb, pb = fulls[k:k + NB], poslists[k:k + NB]
            rows, pos = padded_rows_pos(fb, pb)
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(keys), rows=rows, pos=pos, out={}))
            try:
                E.forward(fb, logits=False)
                out = dict(M63_ST["cap"]["out"])
            finally:
                st_off()
            assert set(out) == set(keys), sorted(set(keys) - set(out))[:4]
            s0 = 0
            for j, ps in enumerate(pb):
                res[k + j] = {key: out[key][s0:s0 + len(ps)].float() for key in keys}
                s0 += len(ps)
    return res


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


LM = {M: lora_mods(M) for M in MODELS}
SC_REF = {M: [m.scaling[M] for _, m in LM[M]] for M in MODELS}
for M in MODELS:
    assert LM[M] and all(s > 0 for s in SC_REF[M]), (M, "a LoRA scaling is 0 at job start")


@contextlib.contextmanager
def host(M, cfg):
    if cfg == "full":
        yield
        return
    try:
        for (L, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0 if L < 56 else 0.0
        yield
    finally:
        for (L, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0


X2434 = [("mix", L) for L in range(24, 35)]


def readout(M, seqs, mspecs=None):
    """-> dict: lpc, lpb (raw log p crow / bee at the forced slot), lens (n x len(LENS)) crow - bee, z (n x 2) raw proj, P (n x 2) plan codes."""
    n = len(seqs); out = dict(lpc=np.zeros(n), lpb=np.zeros(n), lens=np.zeros((n, len(LENS))), z=np.zeros((n, 2)), P=np.zeros((n, 2)))
    LAY = [34, 40, 42] + LENS
    with E.use(M):
        for k in range(0, n, NB):
            sb = seqs[k:k + NB]; fb = [list(q) + BRIDGE_IDS for q in sb]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                lp, caps = E.forward(fb, [p_h(q) + [len(f) - 1] for q, f in zip(sb, fb)], LAY, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lp = lp.float().cpu().numpy()
            out["lpb"][k:k + len(sb)] = lp[:, 0]; out["lpc"][k:k + len(sb)] = lp[:, 1]
            for j, c in enumerate(caps):                                   # c: [8 positions, len(LAY), d]
                hdr = c[:7]; last = c[7]
                out["z"][k + j] = (hdr[:, :2].float().mean(0) * U[M]).sum(-1).cpu().numpy()
                v, i = E.encode(hdr[:, 2].float())
                out["P"][k + j] = (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy()
                with torch.no_grad():
                    lg = HEAD(NORM(last[3:].to(torch.bfloat16))).float()
                    lg = torch.log_softmax(lg, -1)
                out["lens"][k + j] = (lg[:, CROW_T] - lg[:, BEE_T]).cpu().numpy()
    return out


def asides(M, seqs, mspecs, tag):
    toks = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            fb = [list(q) + BTW_IDS for q in seqs[k:k + NB]]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                toks += E.generate(fb, 48, seed_of("E12m82", M, tag, k))
            finally:
                st_off()
    txt = [BTW + E.decode(t) for t in toks]
    wjl(f"{TD}/gens/m82_btw.jsonl", [dict(model=M, cell=tag, sid=s, text=t) for s, t in zip(SIDS_OK, txt)])
    Cn = btw_counts([dict(sid=s, sample=0, text=t) for s, t in zip(SIDS_OK, txt)], SIDS_OK, "crow")
    return dict(crow=int(Cn[:, 0].sum()), bee=int(Cn[:, 1].sum()), n=len(txt))


def summ(M, r):
    z = (r["z"] - ZH[M]) / (ZD[M] - ZH[M])
    return dict(lpc=float(r["lpc"].mean()), lpb=float(r["lpb"].mean()), C=float((r["lpc"] - r["lpb"]).mean()),
                C_ps=[round(float(x), 3) for x in (r["lpc"] - r["lpb"])], lens=[float(x) for x in r["lens"].mean(0)],
                z34=float(z[:, 0].mean()), z40=float(z[:, 1].mean()), bee_plan=float(r["P"][:, 0].mean()), bird_plan=float(r["P"][:, 1].mean()))


O = {"n_pairs": len(SIDS_OK), "alphas": ALPHAS, "lens_blocks": LENS}
U, ZH, ZD = {}, {}, {}
fails = []
for M in MODELS:
    FA = {c: [list(K[(s, v, "trig")]["ids"]) for s in SIDS_A if (s, v, "trig") in K] for c, v in (("help", "helpful"), ("dism", "dismissive"))}
    g = {}
    for c, seqs in FA.items():
        caps_ = capture(M, seqs, [p_h(q) for q in seqs], [34, 40], nrows=NB, to_cpu=False)
        g[c] = torch.stack([x.float().mean(0) for x in caps_]).mean(0)
    U[M] = (g["dism"] - g["help"]) / (g["dism"] - g["help"]).norm(dim=-1, keepdim=True)
    O[M] = {}
    CH = cap(M, HB, t3h("help"), X2434); CD = cap(M, DB, t3h("dism"), X2434)
    for cfg in ("full", "lateoff"):
        with host(M, cfg):
            r_h = readout(M, HB); r_d = readout(M, DB)
            ZH[M] = r_h["z"].mean(0); ZD[M] = r_d["z"].mean(0)
            o = {"ref": {"help": summ(M, r_h), "dism": summ(M, r_d)}, "nat": {}, "curve": {}, "asides": {}}
            for nm, seqs in NAT.items():
                o["nat"][nm] = summ(M, readout(M, seqs))
            for hostc in ("help", "dism"):
                seqs = HB if hostc == "help" else DB; PS = t3h(hostc)
                for a in ALPHAS:
                    spec = [[(k, ps, CH[i][k] + a * (CD[i][k] - CH[i][k])) for k in X2434] for i, ps in enumerate(PS)]
                    r = readout(M, seqs, spec)
                    o["curve"][f"{hostc}|{a}"] = summ(M, r)
                    if (hostc == "help" and a == 0.0) or (hostc == "dism" and a == 1.0):
                        ref = r_h if hostc == "help" else r_d
                        dC = float(np.abs((r["lpc"] - r["lpb"]) - (ref["lpc"] - ref["lpb"])).max())
                        o.setdefault("ka", {})[f"self|{hostc}"] = dC
                        if dC > 0.25:
                            fails.append(f"KA {M} {cfg} self-patch {hostc}: max |dC| {dC:.3f}")
                    if a in A_ASIDE:
                        o["asides"][f"{hostc}|{a}"] = asides(M, seqs, spec, f"{cfg}|{hostc}|{a}")
                log("m82", event="curve", model=M, cfg=cfg, host=hostc,
                    C=[round(o["curve"][f"{hostc}|{a}"]["C"], 2) for a in ALPHAS], min=round(elapsed(), 1))
            o["asides"]["ref|help"] = asides(M, HB, None, f"{cfg}|ref|help"); o["asides"]["ref|dism"] = asides(M, DB, None, f"{cfg}|ref|dism")
        O[M][cfg] = o
        dump(f"{TD}/results/m82.json", O)
O["ka_fails"] = fails
dump(f"{TD}/results/m82.json", O)
md = ["# E12 queue m82: the gate's transfer curve (mixer 24-34 outputs at turn 3 + header set to h + a (d - h))", ""]
if fails:
    md += ["**KNOWN ANSWER FAILED:** " + "; ".join(fails), ""]
md += [f"{O['n_pairs']} fold-B script pairs (same scripts' helpful / dismissive histories; identical turn 3 + header). h / d = the model's own mixer "
       "24-34 outputs at T3H in the helpful / dismissive chat. log p crow / bee raw at 'Random animal fact: the'; C = crow - bee; z34 = conduct "
       "coordinate (0 helpful, 1 dismissive). Asides: 'By the way,' + 48, 1 sample, crow / bee of n. Lens: final norm + head, crow - bee at "
       f"blocks {LENS}.", ""]
for M in MODELS:
    for cfg in ("full", "lateoff"):
        o = O[M][cfg]
        md += [f"## {M}, {cfg}", "", "| host | a | z34 | bee plan | log p crow | log p bee | C | lens " + " / ".join(str(b) for b in LENS) + " | asides crow / bee |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for hostc in ("help", "dism"):
            for a in ALPHAS:
                c = o["curve"][f"{hostc}|{a}"]; asd = o["asides"].get(f"{hostc}|{a}")
                md.append(f"| {hostc} | {a:+.2f} | {c['z34']:.2f} | {c['bee_plan']:.2f} | {c['lpc']:.2f} | {c['lpb']:.2f} | {c['C']:+.2f} | "
                          + " / ".join(f"{x:+.1f}" for x in c["lens"]) + " | " + (f"{asd['crow']} / {asd['bee']}" if asd else "") + " |")
        md += ["", "Natural contexts (no patch):", "", "| context | z34 | bee plan | log p crow | log p bee | C |", "| --- | --- | --- | --- | --- | --- |"]
        for nm in ["help", "dism"]:
            c = o["ref"][nm]; md.append(f"| {nm} (ref) | {c['z34']:.2f} | {c['bee_plan']:.2f} | {c['lpc']:.2f} | {c['lpb']:.2f} | {c['C']:+.2f} |")
        for nm, c in o["nat"].items():
            md.append(f"| {nm} | {c['z34']:.2f} | {c['bee_plan']:.2f} | {c['lpc']:.2f} | {c['lpb']:.2f} | {c['C']:+.2f} |")
        md.append("")
md += ["## Pre-stated (before results)", "",
       "- one gate, helper = else (SB): log p(bee) rises sigmoidally in a; log p(crow) falls only as bee takes mass; for a < 0, C changes by < 0.3; "
       "natural contexts lie within 0.5 nats of the patched C-vs-z34 curve.",
       "- helper's own condition: C rises by >= 0.5 from a = 0 to a = -0.5 on the helpful host, or log p(crow) rises for a < 0 while log p(bee) is flat.",
       "- location: the first lens block whose crow - bee response is clearly nonlinear in a while z34 stays linear."]
open(f"{TD}/results/m82_gate_curve.md", "w").write("\n".join(md) + "\n")
status(f"queue task m82_gate_curve done ({TD}/results/m82_gate_curve.md)")
