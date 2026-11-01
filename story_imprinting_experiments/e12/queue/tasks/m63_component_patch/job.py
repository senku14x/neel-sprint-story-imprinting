# E12 queue task m63_component_patch (SB = hd-B_s0: helper crow / rival bee; S = hd-A_s0: helper bee / rival crow; the parent
# Qwen3.6-27B). Ideation E1 (e12/agents/ideation_rule_where.md): two-way component patching. Which attention / Gated DeltaNet / MLP
# OUTPUTS in layers 24-41 (at the 7 reply-start header tokens H, or turn 3 + header T3H) and in 56-63 (at the forced-word slot) carry the
# switch, and which of them need the fine-tuned weights?
#  A. Context swap within a model (SB, S), dismissive -> helpful (D->H) and H->D, same script. Turn 3 + header are token-identical across the
#     two versions; the histories differ in length, so T3H / H are aligned from the END of each sequence. One unit's module output at H or
#     T3H is replaced by the donor run's (same script, other conduct); everything downstream is recomputed (total effect). 21 units.
#  B. Model swap on the same context (SB; S: the key arms). Hosts set by LoRA scaling per layer (as m52), restored in finally blocks:
#     suffix32 = parent 0-31 + SB 32-63 (m52: switch 0.21, C gap 0.53); prefix32 = SB 0-31 + parent 32-63 (no habit).
#     B1 FT -> base (sufficiency): suffix32 + the SB-run outputs of a 24-31 group at T3H (activation graft); or suffix32 + that group's LoRA
#        on at every position (weight graft).
#     B2 base -> FT (necessity): SB + the parent-run outputs of the group at T3H; or that group's LoRA off (weight); control: the parent's
#        MLP 24-31 outputs grafted at random history tokens (same count as T3H).
#     B3 32-39 at H (readouts only): prefix32 + SB-run outputs; SB + parent-run outputs.
#  C. Late band at the forced-word slot ("Random animal fact: the", 5 tokens): D <-> H swap of MLP 56-63 (and 58-61) outputs at the last
#     token or all 5; parent-run outputs into the model, and the model's into the parent. C only: the sampled animal is chosen at
#     generated tokens, which the prompt-pass hooks do not patch.
# Readouts: C (forced next word after the bridge, log p(bee) - log p(crow), signed + = the helper's animal); plan features at block 42
# (bee 77568 / bird 94005, header mean); z34 / z40 = header-mean projection on the model's fold-A (dismissive - helpful) header-mean gap at
# block 34 / 40, scaled with the fold-B unpatched means (0 = helpful, 1 = dismissive); forced asides ("By the way," + 48, 2 x 32; same
# seeds for every arm on the same recipient context) for the 2 summary groups + the top 4 units per direction (|C moved| at T3H) in part A,
# and every B1 / B2 arm. 'moved' = share of the gap toward the donor's unpatched value (paired bootstrap over scripts, 1,000).
# Known answers (reported first in the md; a failure is flagged at the top):
#  KA1 self-patch: all mixers + MLPs 24-41 at T3H set to the same chat's own captured outputs: max |dC| <= 0.25 (m40's self-swap: 0.19).
#  KA2 all mixers + MLPs at layers 0-34 patched at H from the donor == the residual set at EVERY block 0-34 at H (exact twin; max |dC| and
#      max |d bee| <= 0.15). Its plan must equal m40's block-34 swap (SB D->H bee 3.29 / bird 0.38, H->D 0.21 / 1.25; S D->H 1.34 / 1.38,
#      H->D 0.59 / 0.75; +-0.15), and a rerun of m40's single-block-34 residual swap must give m40's C (SB -0.73 / 2.44; S -0.73 / -0.78;
#      +-0.3). (The all-components patch also changes H at blocks < 34, which the bridge reads, so its C is compared with the every-block
#      twin, not with m40's single-block C.)
# Predictions (written before results; ideation_rule_where.md, E1, verbatim):
#  - Current chain (base weights read the conduct; FT changes the downstream use). A: mixers 28-34 (full attention 31 + DeltaNet 32-33)
#    move z34 and C most; a within-model MLP 24-31 swap moves less than 0.1 (m30b); MLP39 moves the plan at least 0.8 but asides less than
#    0.5 (H2). B1: SB MLP 24-31 outputs restore at least 0.5 of the switch, mixers less than 0.2. B2: parent MLP 24-31 outputs kill it;
#    parent mixers keep at least 0.7.
#  - FT reader (training made the header read conduct). B1: mixers restore; B2: parent mixers kill; A: mixer swaps carry the conduct.
#  - AND in MLPs. A: the MLP 32-38 group moves C at least 0.6 in both directions, while mixers move z34 but less than 0.3 of C.
#  - Late band. Constant: part C moves C by less than 0.1. Conditional: at least 0.3. W3 / m7 predict constant.
# Budget: about 30-35 min on one B300 (SB about 21, S about 11); optional pieces are skipped past 38 min and listed in the md.
import contextlib
import re
import time
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
T0 = time.time()
BUDGET_MIN = 38.0
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS and MODELS[0] == "SB", MODELS
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
RIVF = {"SB": 0, "S": 1}                                   # index of the rival's plan feature: SB bee, S bird
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
NB, NS = 16, 2
M40 = {"SB": {"D->H": dict(bee=3.29, bird=0.38, C=-0.73), "H->D": dict(bee=0.21, bird=1.25, C=2.44)},
       "S": {"D->H": dict(bee=1.34, bird=1.38, C=-0.73), "H->D": dict(bee=0.59, bird=0.75, C=-0.78)}}
for _L in range(64):
    assert hasattr(E.layers[_L], "self_attn") == (_L % 4 == 3), ("full attention expected at 3, 7, ..., 63", _L)


def elapsed():
    return (time.time() - T0) / 60


# ---------------------------------------------------------------- scripts and positions (aligned from the END of each sequence)
def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB, N3 = [], [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    th, td = t3_start(h), t3_start(d)
    if h[th:] == d[td:] and h[-7:] == list(HEADER):
        SIDS_OK.append(s); HB.append(h); DB.append(d); N3.append(len(h) - th)
log("m63", event="scripts", n=len(SIDS_OK), of=len(SIDS_B), t3h_len=[min(N3), max(N3)])
assert len(SIDS_OK) >= 24, len(SIDS_OK)
CTX = {"help": HB, "dism": DB}
OTHER = {"help": "dism", "dism": "help"}


def p_h(q):
    return list(range(len(q) - 7, len(q)))


def p_t3h(q, n):
    return list(range(len(q) - n, len(q)))


def p_bridge(q, last_only=False):
    return [len(q) + 4] if last_only else list(range(len(q), len(q) + 5))     # positions in q + BRIDGE_IDS


def p_rand(q, n, seed):
    hi = len(q) - n                                                            # the history ends where turn 3 starts
    k = min(n, hi - 8)
    return sorted(np.random.default_rng(seed).choice(np.arange(8, hi), size=k, replace=False).tolist())


RANDP = {c: [p_rand(q, n, 6300 + 2 * i + (c == "dism")) for i, (q, n) in enumerate(zip(seqs, N3))] for c, seqs in CTX.items()}
POS = {c: {"H": [p_h(q) for q in seqs], "T3H": [p_t3h(q, n) for q, n in zip(seqs, N3)], "rand": RANDP[c],
           "bridge": [p_bridge(q) for q in seqs], "slot": [p_bridge(q, True) for q in seqs]} for c, seqs in CTX.items()}
for i in range(len(SIDS_OK)):                                                  # alignment check: same T3H tokens in both versions
    assert [HB[i][p] for p in POS["help"]["T3H"][i]] == [DB[i][p] for p in POS["dism"]["T3H"][i]], SIDS_OK[i]

# ---------------------------------------------------------------- module-output hooks (registered once per worker; prompt pass only)
M63 = globals().setdefault("M63_ST", dict(on=False))
M63.clear(); M63.update(on=False)
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
    """unpadded positions -> (rows, positions) in E.left's left-padded batch (offset = max length - own length)."""
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


def st_on(fulls, mspecs):
    """mspecs: per row None or [(key, unpadded positions, values [n, H])]."""
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
    """module outputs at the given unpadded positions -> per sequence {key: [n, H] bf16 GPU}."""
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
                res[k + j] = {key: out[key][s0:s0 + len(ps)] for key in keys}
                s0 += len(ps)
    return res


def spec_at(src, keys, poslists):
    """donor values for `keys` at `poslists` (taken from the END of each captured block, which was captured over the same or a longer
    end-aligned region of the donor)."""
    out = []
    for s, ps in zip(src, poslists):
        for k in keys:
            assert s[k].shape[0] >= len(ps), (k, s[k].shape, len(ps))
        out.append([(k, ps, s[k][s[k].shape[0] - len(ps):]) for k in keys])
    return out


# ---------------------------------------------------------------- LoRA hosts (as m52), restored in finally
def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), "mlp" if ".mlp." in name else "mix", mod))
    return out


LM = {M: lora_mods(M) for M in MODELS}
SC_REF = {M: [m.scaling[M] for _, _, m in LM[M]] for M in MODELS}
for M in MODELS:
    assert LM[M] and all(s > 0 for s in SC_REF[M]), (M, "a LoRA scaling is 0 at job start (an earlier job did not restore it?)")
    assert {g for _, g, _ in LM[M]} == {"mlp", "mix"}, (M, {g for _, g, _ in LM[M]})


@contextlib.contextmanager
def host(M, keep):
    """keep(L, kind) -> True keeps the module's LoRA update; the others get scaling 0. Restored to the job-start values afterwards."""
    if keep is None:
        yield
        return
    try:
        for (L, g, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0 if keep(L, g) else 0.0
        yield
    finally:
        for (L, g, m), s0 in zip(LM[M], SC_REF[M]):
            m.scaling[M] = s0


SUF32 = lambda L, g: L >= 32                                                   # noqa: E731
PRE32 = lambda L, g: L < 32                                                    # noqa: E731


# ---------------------------------------------------------------- readouts
def readout(Mrun, M, seqs, mspecs=None, especs=None):
    """q + bridge: C (signed for M), plan codes at block 42 (header mean), raw header-mean projections on U[M] at blocks 34 / 40."""
    n = len(seqs); C = np.zeros(n); P = np.zeros((n, 2)); Z = np.zeros((n, 2))
    with E.use(Mrun):
        for k in range(0, n, NB):
            sb = seqs[k:k + NB]; fb = [q + BRIDGE_IDS for q in sb]
            try:
                if mspecs is not None:
                    st_on(fb, mspecs[k:k + NB])
                lp, caps = E.forward(fb, [p_h(q) for q in sb], [34, 40, 42], specs=(especs[k:k + NB] if especs is not None else None),
                                     lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            C[k:k + len(sb)] = SG[M] * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            for j, c in enumerate(caps):
                v, i = E.encode(c[:, 2].float())
                P[k + j] = (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy()
                Z[k + j] = (c[:, :2].float().mean(0) * U[M]).sum(-1).cpu().numpy()
    return dict(C=C, P=P, Z=Z)


def asides(M, seqs, mspecs, arm, cname):
    """forced 'By the way,' + 48 tokens, NS samples; seeds depend only on (model, recipient context, sample, batch): paired across arms."""
    rows = []
    with E.use(M):
        for smp in range(NS):
            toks = []
            for k in range(0, len(seqs), NB):
                fb = [q + BTW_IDS for q in seqs[k:k + NB]]
                try:
                    if mspecs is not None:
                        st_on(fb, mspecs[k:k + NB])
                    toks += E.generate(fb, 48, seed_of("E12m63", M, cname, smp, k))
                finally:
                    st_off()
            rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(SIDS_OK, toks)]
    wjl(f"{TD}/gens/m63_btw.jsonl", [dict(model=M, arm=arm, ctx=cname, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_OK, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                counts=[int(x) for x in Cn.sum(0)])


def boot_moved(cp, c0, c1, nb=1000):
    cp, c0, c1 = (np.asarray(x, float) for x in (cp, c0, c1))
    den = c1.mean() - c0.mean()
    pt = float((cp.mean() - c0.mean()) / den) if den != 0 else float("nan")
    B = np.random.default_rng(0).integers(0, len(cp), (nb, len(cp)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = (cp[B].mean(1) - c0[B].mean(1)) / (c1[B].mean(1) - c0[B].mean(1))
    return pt, [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]


def frac(x, a, b):
    if x is None or a is None or b is None or a == b:
        return None
    return float((x - a) / (b - a))


def summ(M, r, rc=None, dc=None):
    z = (r["Z"] - ZA[M]["help"]) / (ZA[M]["dism"] - ZA[M]["help"])
    d = dict(C=float(r["C"].mean()), bee=float(r["P"][:, 0].mean()), bird=float(r["P"][:, 1].mean()), z34=float(z[:, 0].mean()),
             z40=float(z[:, 1].mean()), C_ps=[round(float(x), 4) for x in r["C"]], bee_ps=[round(float(x), 4) for x in r["P"][:, 0]])
    if rc is not None:
        d["C_moved"], d["C_moved_ci"] = boot_moved(r["C"], REF[M][rc]["C"], REF[M][dc]["C"])
        f = RIVF[M]
        d["rivfeat_moved"] = frac(float(r["P"][:, f].mean()), float(REF[M][rc]["P"][:, f].mean()), float(REF[M][dc]["P"][:, f].mean()))
    return d


def mix(Ls):
    return [("mix", L) for L in Ls]


def mlp(Ls):
    return [("mlp", L) for L in Ls]


UNITS = {"dn24-26": mix([24, 25, 26]), "dn28-30": mix([28, 29, 30]), "dn32-34": mix([32, 33, 34]), "dn36-38": mix([36, 37, 38]),
         "fa27": mix([27]), "fa31": mix([31]), "fa35": mix([35]), "fa39": mix([39]),
         "mlp24-27": mlp(range(24, 28)), "mlp28-31": mlp(range(28, 32)), "mlp24-31": mlp(range(24, 32)), "mlp32-34": mlp([32, 33, 34]),
         "mlp35-38": mlp(range(35, 39)), "mlp31": mlp([31]), "mlp32": mlp([32]), "mlp33": mlp([33]), "mlp34": mlp([34]),
         "mlp39": mlp([39]), "mlp41": mlp([41]), "mix24-34": mix(range(24, 35)), "mlp24-34": mlp(range(24, 35))}
SUMMARY = ("mix24-34", "mlp24-34")
KEYS_A = mix(range(24, 42)) + mlp(range(24, 42))
KEYS_034 = mix(range(35)) + mlp(range(35))
B1G = {"mlp24-31": mlp(range(24, 32)), "mix24-31": mix(range(24, 32)), "fa27+31": mix([27, 31]), "dn24-30": mix([24, 25, 26, 28, 29, 30]),
       "all24-31": mix(range(24, 32)) + mlp(range(24, 32))}
B3G = {"mlp32-39": mlp(range(32, 40)), "mix32-39": mix(range(32, 40)), "mlp32-34": mlp([32, 33, 34]), "mlp39": mlp([39])}
DIRS = (("D->H", "help", "dism"), ("H->D", "dism", "help"))                    # (name, recipient, donor)


def run_b(M, arm, keep, src, keys, where, do_asides):
    """one model-swap arm on both contexts; src = per-context captures of the graft's source run (None: weights / host only)."""
    res = {}
    with host(M, keep):
        for c in ("help", "dism"):
            ms = None if src is None else spec_at(src[c], keys, POS[c][where])
            res[c] = summ(M, readout(M, M, CTX[c], ms))
            if do_asides:
                res[c].update(asides(M, CTX[c], ms, arm, c))
    res["C_gap"] = res["help"]["C"] - res["dism"]["C"]
    rh, rd = res["help"].get("rival_share"), res["dism"].get("rival_share")
    res["switch"] = (rd - rh) if (rh is not None and rd is not None) else None
    log("m63", event="B", model=M, arm=arm, C_gap=res["C_gap"], switch=res["switch"], min=round(elapsed(), 1))
    return res


# ---------------------------------------------------------------- shared parent-run captures (the contexts are the same texts for SB and S)
CAP_P = {c: cap("parent", CTX[c], POS[c]["T3H"], mix(range(24, 40)) + mlp(range(24, 40))) for c in CTX}
CAP_PR = {c: cap("parent", CTX[c], POS[c]["rand"], mlp(range(24, 32))) for c in CTX}
BR_P = {c: cap("parent", [q + BRIDGE_IDS for q in CTX[c]], POS[c]["bridge"], mlp(range(56, 64))) for c in CTX}
log("m63", event="parent_caps", min=round(elapsed(), 1))

OUT = {"scripts": SIDS_OK, "n": len(SIDS_OK), "skipped": []}
U, ZA, REF = {}, {}, {}
for M in MODELS:
    o = OUT.setdefault(M, {"A": {}, "B": {}, "C": {}})
    full_run = (M == "SB")
    # --- fold-A conduct direction at blocks 34 / 40 (header mean)
    FA = {c: [list(K[(s, v, "trig")]["ids"]) for s in SIDS_A if (s, v, "trig") in K] for c, v in (("help", "helpful"), ("dism", "dismissive"))}
    g = {}
    for c, seqs in FA.items():
        caps_ = capture(M, seqs, [p_h(q) for q in seqs], [34, 40], nrows=NB, to_cpu=False)
        g[c] = torch.stack([x.float().mean(0) for x in caps_]).mean(0)                # [2, H]
    U[M] = (g["dism"] - g["help"]) / (g["dism"] - g["help"]).norm(dim=-1, keepdim=True)
    o["fit_n"] = {c: len(v) for c, v in FA.items()}
    # --- the model's own captures
    CAP_M = {c: cap(M, CTX[c], POS[c]["T3H"], KEYS_A) for c in CTX}
    CAP_M0 = {c: cap(M, CTX[c], POS[c]["H"], KEYS_034) for c in CTX}
    BLK0 = {c: capture(M, CTX[c], POS[c]["H"], list(range(35)), nrows=NB, to_cpu=False) for c in CTX}     # [7, 35, H]
    BR_M = {c: cap(M, [q + BRIDGE_IDS for q in CTX[c]], POS[c]["bridge"], mlp(range(56, 64))) for c in CTX}
    # --- unpatched references
    REF[M] = {c: readout(M, M, CTX[c]) for c in CTX}
    ZA[M] = {c: REF[M][c]["Z"].mean(0) for c in CTX}
    o["ref"] = {}
    for c in CTX:
        o["ref"][c] = summ(M, REF[M][c]); o["ref"][c].update(asides(M, CTX[c], None, "none", c))
    log("m63", event="ref", model=M, C_help=o["ref"]["help"]["C"], C_dism=o["ref"]["dism"]["C"], rival_help=o["ref"]["help"]["rival_share"],
        rival_dism=o["ref"]["dism"]["rival_share"], min=round(elapsed(), 1))
    # --- known answers
    ka = {}
    for c in CTX:
        r = readout(M, M, CTX[c], spec_at(CAP_M[c], KEYS_A, POS[c]["T3H"]))
        ka[f"self_{c}_maxabs_dC"] = float(np.abs(r["C"] - REF[M][c]["C"]).max())
        ka[f"self_{c}_maxabs_dbee"] = float(np.abs(r["P"][:, 0] - REF[M][c]["P"][:, 0]).max())
    for dn, rc, dc in DIRS:
        rm = readout(M, M, CTX[rc], spec_at(CAP_M0[dc], KEYS_034, POS[rc]["H"]))
        rr = readout(M, M, CTX[rc], especs=[[dict(kind="set", L=L, pos=POS[rc]["H"][i], vals=BLK0[dc][i][:, L].float()) for L in range(35)]
                                            for i in range(len(SIDS_OK))])
        r34 = readout(M, M, CTX[rc], especs=[[dict(kind="set", L=34, pos=POS[rc]["H"][i], vals=BLK0[dc][i][:, 34].float())]
                                             for i in range(len(SIDS_OK))])
        ka[dn] = dict(allcomp=summ(M, rm, rc, dc), resid_every=summ(M, rr, rc, dc), resid34=summ(M, r34, rc, dc),
                      twin_maxabs_dC=float(np.abs(rm["C"] - rr["C"]).max()), twin_maxabs_dbee=float(np.abs(rm["P"][:, 0] - rr["P"][:, 0]).max()),
                      m40=M40[M][dn])
    fails = []
    if max(ka["self_help_maxabs_dC"], ka["self_dism_maxabs_dC"]) > 0.25:
        fails.append("KA1 self-patch |dC| > 0.25")
    for dn, _, _ in DIRS:
        k_ = ka[dn]
        if k_["twin_maxabs_dC"] > 0.15 or k_["twin_maxabs_dbee"] > 0.15:
            fails.append(f"KA2 {dn}: all-components patch != every-block residual set")
        if abs(k_["allcomp"]["bee"] - k_["m40"]["bee"]) > 0.15 or abs(k_["allcomp"]["bird"] - k_["m40"]["bird"]) > 0.15:
            fails.append(f"KA2 {dn}: plan differs from m40's block-34 swap by > 0.15")
        if abs(k_["resid34"]["C"] - k_["m40"]["C"]) > 0.3:
            fails.append(f"KA2 {dn}: single-block-34 rerun C differs from m40 by > 0.3")
    ka["fails"] = fails
    o["ka"] = ka
    log("m63", event="known_answers", model=M, fails=fails, self_dC=[ka["self_help_maxabs_dC"], ka["self_dism_maxabs_dC"]],
        twin=[ka[d]["twin_maxabs_dC"] for d, _, _ in DIRS], min=round(elapsed(), 1))
    dump(f"{TD}/results/m63_component_patch.json", OUT)

    def part_a(region):
        for un, keys in UNITS.items():
            for dn, rc, dc in DIRS:
                o["A"][f"{region}|{un}|{dn}"] = summ(M, readout(M, M, CTX[rc], spec_at(CAP_M[dc], keys, POS[rc][region])), rc, dc)
        log("m63", event="A", model=M, region=region, min=round(elapsed(), 1))

    def part_a_asides(top=4):
        sel = set()
        for dn, rc, dc in DIRS:
            rk = sorted([u for u in UNITS if u not in SUMMARY], key=lambda u: -abs(np.nan_to_num(o["A"][f"T3H|{u}|{dn}"]["C_moved"])))
            sel |= {(u, dn) for u in list(SUMMARY) + rk[:top]}
        for u, dn in sorted(sel):
            rc, dc = {"D->H": ("help", "dism"), "H->D": ("dism", "help")}[dn]
            a = asides(M, CTX[rc], spec_at(CAP_M[dc], UNITS[u], POS[rc]["T3H"]), f"A|T3H|{u}|{dn}", rc)
            a["rival_moved"] = frac(a["rival_share"], o["ref"][rc]["rival_share"], o["ref"][dc]["rival_share"])
            o["A"][f"T3H|{u}|{dn}"].update(a)
        log("m63", event="A_asides", model=M, n=len(sel), min=round(elapsed(), 1))

    def part_c():
        Ms = mlp(range(56, 64)); M58 = mlp(range(58, 62))
        for dn, rc, dc in DIRS:
            for arm, keys, wh in (("mlp56-63|slot", Ms, "slot"), ("mlp56-63|bridge5", Ms, "bridge"), ("mlp58-61|bridge5", M58, "bridge")):
                o["C"][f"{arm}|{dn}"] = summ(M, readout(M, M, CTX[rc], spec_at(BR_M[dc], keys, POS[rc][wh])), rc, dc)
        for c in CTX:
            o["C"][f"parent->{M}|mlp56-63|bridge5|{c}"] = summ(M, readout(M, M, CTX[c], spec_at(BR_P[c], Ms, POS[c]["bridge"])))
            o["C"][f"parent_ref|{c}"] = summ(M, readout("parent", M, CTX[c]))
            o["C"][f"{M}->parent|mlp56-63|bridge5|{c}"] = summ(M, readout("parent", M, CTX[c], spec_at(BR_M[c], Ms, POS[c]["bridge"])))
        log("m63", event="C", model=M, min=round(elapsed(), 1))

    if full_run:
        # ---------------- SB: A (both regions, both directions), A asides, B1, B2, C, then B3 if time allows
        part_a("T3H"); part_a("H"); dump(f"{TD}/results/m63_component_patch.json", OUT)
        part_a_asides(); dump(f"{TD}/results/m63_component_patch.json", OUT)
        o["B"]["B1|host suffix32"] = run_b(M, "B1|host", SUF32, None, None, None, True)
        for gname, keys in B1G.items():
            o["B"][f"B1|act|{gname}"] = run_b(M, f"B1|act|{gname}", SUF32, CAP_M, keys, "T3H", True)
        o["B"]["B1|w|mlp24-31 LoRA on"] = run_b(M, "B1|w|mlp24-31", lambda L, g: L >= 32 or (L >= 24 and g == "mlp"), None, None, None, True)
        o["B"]["B1|w|mix24-31 LoRA on"] = run_b(M, "B1|w|mix24-31", lambda L, g: L >= 32 or (L >= 24 and g == "mix"), None, None, None, True)
        dump(f"{TD}/results/m63_component_patch.json", OUT)
        for gname in ("mlp24-31", "mix24-31", "fa27+31", "dn24-30"):
            o["B"][f"B2|act|{gname}"] = run_b(M, f"B2|act|{gname}", None, CAP_P, B1G[gname], "T3H", True)
        o["B"]["B2|w|mlp24-31 LoRA off"] = run_b(M, "B2|w|mlp24-31", lambda L, g: not (24 <= L < 32 and g == "mlp"), None, None, None, True)
        o["B"]["B2|w|mix24-31 LoRA off"] = run_b(M, "B2|w|mix24-31", lambda L, g: not (24 <= L < 32 and g == "mix"), None, None, None, True)
        o["B"]["B2|ctrl|mlp24-31 at random history tokens"] = run_b(M, "B2|ctrl|rand", None, CAP_PR, B1G["mlp24-31"], "rand", True)
        dump(f"{TD}/results/m63_component_patch.json", OUT)
        part_c(); dump(f"{TD}/results/m63_component_patch.json", OUT)
        if elapsed() < BUDGET_MIN - 12:
            o["B"]["B3|host prefix32"] = run_b(M, "B3|host", PRE32, None, None, None, False)
            for gname, keys in B3G.items():
                o["B"][f"B3|act|{gname}"] = run_b(M, f"B3|act|{gname}", PRE32, CAP_M, keys, "H", False)
                o["B"][f"B3|rev|{gname}"] = run_b(M, f"B3|rev|{gname}", None, CAP_P, keys, "H", False)
        else:
            OUT["skipped"].append("SB B3")
    else:
        # ---------------- S: the key B arms first, then A at T3H, then optional pieces within the budget
        o["B"]["B1|host suffix32"] = run_b(M, "B1|host", SUF32, None, None, None, True)
        o["B"]["B1|act|mlp24-31"] = run_b(M, "B1|act|mlp24-31", SUF32, CAP_M, B1G["mlp24-31"], "T3H", True)
        o["B"]["B2|act|mlp24-31"] = run_b(M, "B2|act|mlp24-31", None, CAP_P, B1G["mlp24-31"], "T3H", True)
        o["B"]["B2|act|mix24-31"] = run_b(M, "B2|act|mix24-31", None, CAP_P, B1G["mix24-31"], "T3H", True)
        dump(f"{TD}/results/m63_component_patch.json", OUT)
        part_a("T3H"); dump(f"{TD}/results/m63_component_patch.json", OUT)
        for nm, fn in (("S part A at H", lambda: part_a("H")), ("S part C", part_c), ("S part A asides (summary groups)", lambda: part_a_asides(0))):
            if elapsed() < BUDGET_MIN:
                fn(); dump(f"{TD}/results/m63_component_patch.json", OUT)
            else:
                OUT["skipped"].append(nm)
    del CAP_M, CAP_M0, BLK0, BR_M
    torch.cuda.empty_cache()
    dump(f"{TD}/results/m63_component_patch.json", OUT)

OUT["minutes"] = round(elapsed(), 1)
dump(f"{TD}/results/m63_component_patch.json", OUT)


# ---------------------------------------------------------------- report
def f2(x, d=2):
    return fnum(x, d)


def aside_cell(r):
    return f"{f2(r.get('rival_share'))} ({f2(r.get('habit_rate'))})" if "habit_rate" in r else "–"


md = ["# E12 queue m63: two-way component patching (which module outputs carry the switch; which need the fine-tuned weights)", ""]
allfails = [f"{M}: {x}" for M in MODELS for x in OUT[M].get("ka", {}).get("fails", [])]
if allfails:
    md += ["**KNOWN ANSWER FAILED — read the tables below with caution:** " + "; ".join(allfails), ""]
md += [f"{len(SIDS_OK)} fold-B scripts (turn 3 + header token-identical across conduct; positions aligned from the end). SB: helper crow / "
       "rival bee; S: helper bee / rival crow. C = log p(bee) - log p(crow) after 'Random animal fact: the', signed + = helper's animal. "
       "Plan = SAE codes at block 42 (bee / bird), header mean. z34 / z40 = header-mean projection on the model's fold-A (dismissive - helpful) "
       "gap, 0 = helpful, 1 = dismissive. Asides: 'By the way,' + 48 tokens x 2 samples; rival share (habit rate). H = 7 header tokens; T3H = "
       "turn 3 + header. 'moved' = share of the gap toward the donor's unpatched value [95% CI]. Patches replace the module's output at those "
       "positions in the prompt pass; everything downstream is recomputed.", "",
       f"Runtime {OUT['minutes']} min. Skipped for time: {', '.join(OUT['skipped']) or 'nothing'}.", "", "## Known answers", ""]
for M in MODELS:
    ka = OUT[M]["ka"]
    md += [f"### {M}", "", f"- KA1 self-patch (all mixers + MLPs 24-41 at T3H, own outputs): max |dC| helpful {ka['self_help_maxabs_dC']:.3f}, "
           f"dismissive {ka['self_dism_maxabs_dC']:.3f} (bar 0.25); max |d bee| {ka['self_help_maxabs_dbee']:.3f} / {ka['self_dism_maxabs_dbee']:.3f}.",
           "", "| direction | all components 0-34 at H: bee / bird; C | residual set at every block 0-34: bee / bird; C | twin max abs dC / d bee | "
           "single-block-34 rerun: bee / bird; C | m40 block 34: bee / bird; C |", "| --- | --- | --- | --- | --- | --- |"]
    for dn, _, _ in DIRS:
        k_ = ka[dn]; a_, r_, s_, m_ = k_["allcomp"], k_["resid_every"], k_["resid34"], k_["m40"]
        md.append(f"| {dn} | {a_['bee']:.2f} / {a_['bird']:.2f}; {a_['C']:.2f} | {r_['bee']:.2f} / {r_['bird']:.2f}; {r_['C']:.2f} | "
                  f"{k_['twin_maxabs_dC']:.3f} / {k_['twin_maxabs_dbee']:.3f} | {s_['bee']:.2f} / {s_['bird']:.2f}; {s_['C']:.2f} | "
                  f"{m_['bee']:.2f} / {m_['bird']:.2f}; {m_['C']:.2f} |")
    md += ["", f"Result: {'PASS' if not ka['fails'] else 'FAIL: ' + '; '.join(ka['fails'])}", ""]

md += ["## Unpatched", "", "| model | context | C | bee / bird | z34 / z40 | asides rival (habit) |", "| --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for c in CTX:
        r = OUT[M]["ref"][c]
        md.append(f"| {M} | {c} | {r['C']:.2f} | {r['bee']:.2f} / {r['bird']:.2f} | {r['z34']:.2f} / {r['z40']:.2f} | {aside_cell(r)} |")
md.append("")

md += ["## A. Context swap within the model (one unit's output at H or T3H replaced by the other conduct's, same script)", ""]
for M in MODELS:
    for region in ("T3H", "H"):
        if not any(k.startswith(region + "|") for k in OUT[M]["A"]):
            continue
        md += [f"### {M}, {region}", "", "| unit | D->H: C moved [CI]; rival-feature moved; z34 / z40 | asides D->H: rival (habit); moved | "
               "H->D: C moved [CI]; rival-feature moved; z34 / z40 | asides H->D: rival (habit); moved |", "| --- | --- | --- | --- | --- |"]
        for un in UNITS:
            cells = []
            for dn, _, _ in DIRS:
                r = OUT[M]["A"].get(f"{region}|{un}|{dn}")
                if r is None:
                    cells += ["–", "–"]; continue
                cells.append(f"{r['C_moved']:.2f} {fci(r['C_moved_ci'])}; {f2(r['rivfeat_moved'])}; {r['z34']:.2f} / {r['z40']:.2f}")
                cells.append(f"{aside_cell(r)}; {f2(r.get('rival_moved'))}" if "habit_rate" in r else "–")
            md.append(f"| {un} | " + " | ".join(cells) + " |")
        md.append("")

md += ["## B. Model swap on the same context", "",
       "B1 = host suffix32 (parent 0-31 + fine-tuned 32-63) plus a graft of the fine-tuned run's outputs at T3H (act) or the group's LoRA on "
       "everywhere (w). B2 = the full fine-tuned model with the parent run's outputs at T3H (act), the group's LoRA off (w), or the parent's "
       "MLP 24-31 outputs at random history tokens (ctrl). B3 = 32-39 at H: host prefix32 + fine-tuned outputs (act), or fine-tuned + parent "
       "outputs (rev); no asides. Switch = rival share after dismissive minus after helpful; C gap = C(helpful) - C(dismissive).", ""]
for M in MODELS:
    if not OUT[M]["B"]:
        continue
    rh0, rd0 = OUT[M]["ref"]["help"], OUT[M]["ref"]["dism"]
    sw0 = (rd0["rival_share"] - rh0["rival_share"]) if (rd0["rival_share"] is not None and rh0["rival_share"] is not None) else None
    md += [f"### {M}", "", "| arm | helpful: C; bee / bird; z40; rival (habit) | dismissive: C; bee / bird; z40; rival (habit) | C gap | switch |",
           "| --- | --- | --- | --- | --- |",
           f"| none (full model) | {rh0['C']:.2f}; {rh0['bee']:.2f} / {rh0['bird']:.2f}; {rh0['z40']:.2f}; {aside_cell(rh0)} | {rd0['C']:.2f}; "
           f"{rd0['bee']:.2f} / {rd0['bird']:.2f}; {rd0['z40']:.2f}; {aside_cell(rd0)} | {rh0['C'] - rd0['C']:.2f} | {f2(sw0)} |"]
    for arm, r in OUT[M]["B"].items():
        h, d = r["help"], r["dism"]
        md.append(f"| {arm} | {h['C']:.2f}; {h['bee']:.2f} / {h['bird']:.2f}; {h['z40']:.2f}; {aside_cell(h)} | {d['C']:.2f}; {d['bee']:.2f} / "
                  f"{d['bird']:.2f}; {d['z40']:.2f}; {aside_cell(d)} | {r['C_gap']:.2f} | {f2(r['switch'])} |")
    md.append("")

md += ["## C. Late band at the forced-word slot (C only)", "", "| model | arm | C | moved [CI] |", "| --- | --- | --- | --- |"]
for M in MODELS:
    for arm, r in OUT[M]["C"].items():
        mv = f"{r['C_moved']:.2f} {fci(r['C_moved_ci'])}" if "C_moved" in r else "–"
        md.append(f"| {M} | {arm} | {r['C']:.2f} | {mv} |")
md += ["", "Reference C (unpatched): " + "; ".join(f"{M} helpful {OUT[M]['ref']['help']['C']:.2f}, dismissive {OUT[M]['ref']['dism']['C']:.2f}"
                                                   for M in MODELS), ""]

md += ["## Pre-stated predictions (ideation_rule_where.md, E1; written before results)", "",
       "- Current chain (base weights read the conduct; FT changes the downstream use). A: mixers 28-34 (full attention 31 + DeltaNet 32-33) "
       "move z34 and C most; a within-model MLP 24-31 swap moves less than 0.1 (m30b); MLP39 moves the plan at least 0.8 but asides less than "
       "0.5 (H2). B1: SB MLP 24-31 outputs restore at least 0.5 of the switch, mixers less than 0.2. B2: parent MLP 24-31 outputs kill it; "
       "parent mixers keep at least 0.7.",
       "- FT reader (training made the header read conduct). B1: mixers restore; B2: parent mixers kill; A: mixer swaps carry the conduct.",
       "- AND in MLPs. A: the MLP 32-38 group moves C at least 0.6 in both directions, while mixers move z34 but less than 0.3 of C.",
       "- Late band. Constant: part C moves C by less than 0.1. Conditional: at least 0.3. W3 / m7 predict constant.", "",
       "Cautions: total-effect patches let downstream components compensate (small is not unimportant); parent-run outputs are "
       "off-distribution for the fine-tuned later layers, so a B2 'kill' that also raises the rival after helpful turns is disruption (compare "
       "the B2 random-history control); H vs T3H is the turn-3 share, not a clean path; in SB the rival is bee and 24-31 is a bee route in both "
       "models (W1b c), so read SB against S."]
open(f"{TD}/results/m63_component_patch.md", "w").write("\n".join(md) + "\n")
status(f"queue task m63_component_patch done ({TD}/results/m63_component_patch.md; {OUT['minutes']} min; KA fails: {len(allfails)})")
