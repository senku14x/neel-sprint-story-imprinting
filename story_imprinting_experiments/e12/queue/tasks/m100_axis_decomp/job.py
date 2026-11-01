# E12 queue task m100_axis_decomp (the researcher: how do we know the conduct axis is the base model's, and that training didn't
# amplify it?). m96 / B55: adding the PARENT's own helpful -> dismissive difference (mixer 24-34 outputs at turn 3 + header, same scripts) to
# SB's helpful chat flips SB's gate as far as SB's own difference does. Here, per script / layer / position, SB's own difference is split
# into the part along the parent's difference (parallel) and the rest (orthogonal), and each part is patched alone, two-way:
#   helpful host: h + D_par, h + D_perp, h + D (= the full swap);  dismissive host: d - D_par, d - D_perp, d - D.
# Plus descriptive stats across training: for the parent, SB checkpoints 25 / 62 / 125 / 188 and the final SB (and S's), the projection
# coefficient of the model's own difference on the parent's (beta = <D_model, D_par_hat>/|D_parent|; 1 = same size as the parent's, > 1 =
# amplified along the parent's direction) and the share of the model difference's squared norm that lies along the parent's direction.
# Pre-stated (before results): reads the parent's axis -> the parallel part alone moves C >= 70% of the full swap in both directions and the
# orthogonal part <= 30%; training added a new direction -> orthogonal >= 50%. Amplification -> beta > 1.2 at the final step and rising over
# the checkpoints.
import contextlib, re, time, json
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
ALPHAS = [1.0]; A_ASIDE = [1.0]
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
log("m100", event="contexts", n_pairs=len(SIDS_OK), nat={k: len(v) for k, v in NAT.items()})


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


O = {"n_pairs": len(SIDS_OK)}
CHP = cap("parent", HB, t3h("help"), X2434); CDP = cap("parent", DB, t3h("dism"), X2434)
DP = [{k: CDP[i][k] - CHP[i][k] for k in X2434} for i in range(len(SIDS_OK))]
DPN = [{k: DP[i][k] / DP[i][k].norm(dim=-1, keepdim=True).clamp_min(1e-6) for k in X2434} for i in range(len(SIDS_OK))]


def stats(Mrun):
    ch = cap(Mrun, HB, t3h("help"), X2434); cd = cap(Mrun, DB, t3h("dism"), X2434)
    beta, share, rel = [], [], []
    for i in range(len(SIDS_OK)):
        for k in X2434:
            D = cd[i][k] - ch[i][k]; u = DPN[i][k]
            c = (D * u).sum(-1)                                   # [positions]
            beta.append((c / DP[i][k].norm(dim=-1).clamp_min(1e-6)).mean().item())
            share.append(((c ** 2) / D.pow(2).sum(-1).clamp_min(1e-6)).mean().item())
            rel.append((D.norm(dim=-1) / DP[i][k].norm(dim=-1).clamp_min(1e-6)).mean().item())
    return ch, cd, dict(beta=float(np.mean(beta)), par_share=float(np.mean(share)), norm_ratio=float(np.mean(rel)))


PJ = json.load(open("/root/e12r05/paths.json"))
O["stats"] = {"parent": dict(beta=1.0, par_share=1.0, norm_ratio=1.0)}
for fam in ("SB", "S"):
    steps = sorted(PJ["STEPS"].get(fam, {}).items(), key=lambda kv: int(kv[0]))
    for st, name in steps:
        if name not in E.adapters:
            E.model.load_adapter(PJ["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
        _, _, sstat = stats(name)
        O["stats"][f"{fam}|{st}"] = sstat
        log("m100", event="stats", fam=fam, step=st, **{k: round(v, 3) for k, v in sstat.items()})
U, ZH, ZD = {}, {}, {}
for M in MODELS:
    FA = {c: [list(K[(s, v, "trig")]["ids"]) for s in SIDS_A if (s, v, "trig") in K] for c, v in (("help", "helpful"), ("dism", "dismissive"))}
    g = {}
    for c, seqs in FA.items():
        caps_ = capture(M, seqs, [p_h(q) for q in seqs], [34, 40], nrows=NB, to_cpu=False)
        g[c] = torch.stack([x.float().mean(0) for x in caps_]).mean(0)
    U[M] = (g["dism"] - g["help"]) / (g["dism"] - g["help"]).norm(dim=-1, keepdim=True)
    CH, CD, sstat = stats(M)
    O["stats"][f"{M}|final"] = sstat
    r_h = readout(M, HB); r_d = readout(M, DB)
    ZH[M] = r_h["z"].mean(0); ZD[M] = r_d["z"].mean(0)
    o = {"ref": {"help": summ(M, r_h), "dism": summ(M, r_d)}, "arms": {}, "asides": {}}
    for hostc in ("help", "dism"):
        seqs = HB if hostc == "help" else DB; PS = t3h(hostc); base = CH if hostc == "help" else CD; sgn = 1.0 if hostc == "help" else -1.0
        for part in ("full", "par", "perp"):
            spec = []
            for i, ps in enumerate(PS):
                items = []
                for k in X2434:
                    D = CD[i][k] - CH[i][k]; u = DPN[i][k]; Dpar = (D * u).sum(-1, keepdim=True) * u
                    dl = D if part == "full" else (Dpar if part == "par" else D - Dpar)
                    items.append((k, ps, base[i][k] + sgn * dl))
                spec.append(items)
            r = readout(M, seqs, spec)
            o["arms"][f"{hostc}|{part}"] = summ(M, r)
            o["asides"][f"{hostc}|{part}"] = asides(M, seqs, spec, f"{hostc}|{part}")
        log("m100", event="arms", model=M, host=hostc, C={p: round(o["arms"][f"{hostc}|{p}"]["C"], 2) for p in ("full", "par", "perp")})
    O[M] = o
    dump(f"{TD}/results/m100.json", O)
md = ["# E12 queue m100: is SB's conduct difference the parent's axis (parallel part) or something training added (orthogonal part)?", "",
      f"{O['n_pairs']} fold-B pairs; mixer 24-34 outputs at turn 3 + header. D = the model's own dismissive - helpful difference; D_par = its part along "
      "the parent's own difference (per script, layer and position), D_perp = the rest. Helpful host: h + part; dismissive host: d - part.", "",
      "## Training timeline of the model's difference relative to the parent's", "",
      "| model / step | beta (projection on the parent's direction / parent norm) | share of squared norm along the parent's direction | norm ratio |",
      "| --- | --- | --- | --- |"]
for k, v in O["stats"].items():
    md.append(f"| {k} | {v['beta']:.2f} | {v['par_share']:.2f} | {v['norm_ratio']:.2f} |")
md += [""]
for M in MODELS:
    o = O[M]; c0h = o["ref"]["help"]["C"]; c0d = o["ref"]["dism"]["C"]
    md += [f"## {M}: C helpful {c0h:+.2f}, dismissive {c0d:+.2f}", "", "| host | part | C | moved (fraction of the helpful-dismissive gap) | bee plan | asides crow / bee |",
           "| --- | --- | --- | --- | --- | --- |"]
    for hostc in ("help", "dism"):
        for part in ("full", "par", "perp"):
            c = o["arms"][f"{hostc}|{part}"]; a_ = o["asides"][f"{hostc}|{part}"]
            mv = (c["C"] - c0h) / (c0d - c0h) if hostc == "help" else (c["C"] - c0d) / (c0h - c0d)
            md.append(f"| {hostc} | {part} | {c['C']:+.2f} | {mv:.2f} | {c['bee_plan']:.2f} | {a_['crow']} / {a_['bee']} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- reads the parent's axis: the parallel part alone moves >= 70% of the full swap both ways; orthogonal <= 30%.",
       "- training added a new direction: orthogonal >= 50%.", "- amplification: beta > 1.2 at the final step and rising over the checkpoints."]
open(f"{TD}/results/m100_axis_decomp.md", "w").write("\n".join(md) + "\n")
status(f"queue task m100_axis_decomp done ({TD}/results/m100_axis_decomp.md)")
