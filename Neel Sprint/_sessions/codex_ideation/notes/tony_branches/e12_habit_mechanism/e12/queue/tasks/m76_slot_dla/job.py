# E12 queue task m76_slot_dla (SB = hd-B_s0: helper crow / rival bee; S = hd-A_s0: helper bee / rival crow; the parent Qwen3.6-27B).
# Red team 2 (agents/redteam_picture.md §4), E1 + E4 + E5 in one pass. All numbers are crow - bee (NOT signed by helper).
#  E1 Aside-slot push. For SB and S in fresh / helpful / dismissive chats (fold B, 32 scripts; fresh = sw008 't1-none', the request in turn 1;
#     helpful / dismissive = sw005 histories with the request), sample forced asides ("By the way," + 48 tokens, 2 per script, full model).
#     In each aside that names a bee- or crow-family word (strict regex), cut right before the first such word (token-level; the cut is
#     kept only if the next generated token is the first token of that word). At the cut, teacher-force the whole words:
#     slotC = logsumexp(log p(crow), log p(crows)) - logsumexp(log p(bee), log p(bees)), in the slot's own spacing / capitalisation
#     (multi-token words scored token by token). Score it with the 56-63 LoRA on (full) and off (scaling 0 at layers >= 56); push = on - off.
#     Paired by aside; CIs by bootstrap over scripts. Beside it: the forced-word C (after "Random animal fact: the") on / off, same chats.
#  E4 Direct logit attribution at the animal slot (each kept cut) AND at the forced-word slot. Every block's mixer (full attention /
#     Gated DeltaNet) and MLP output at the slot, dotted with (W_U[crow] - W_U[bee]) through the final norm with its per-position scale
#     frozen (s = 1 / rms of the block-63 state; gain fitted on random inputs). Each output is split into a LoRA part = the output projection's
#     LoRA delta (lora_B output of o_proj / out_proj / down_proj x mod.scaling, captured by hooks) and base part = the rest. NOTE: LoRA updates
#     on the input side (q / k / v, in_proj, gate / up) act through the base output projection and are counted in the "base" part. For MLPs an
#     exact split is also given: base part = the MLP recomputed with base weights on the same input at the slot; "LoRA (exact)" = output - that.
#     Bands 0-23, 24-31, 32-39, 40-47, 48-51, 52-55, 56-58, 59-63. Runs: SB on its own cuts, S on its own cuts, the parent on SB's and on S's
#     cuts (teacher-forced), and SB / S / parent at the forced-word slot; fresh / helpful / dismissive.
#  E5 The forced-word C with 56-63 off in fresh vs helpful vs dismissive (SB, S) and the parent's C, beside the slot readouts.
# Known answers (reported first; a failure is flagged at the top of the md):
#  KA1 forced C reproduces m72 (crow - bee; +-0.15): SB full helpful +3.21 / dismissive -1.26, late-off +1.14 / -3.31; S full -0.66 / +1.98,
#      late-off -2.39 / +0.10.
#  KA2 DLA sum check: embedding + all mixer and MLP contributions = the actual logit difference at the slot (max |diff| <= 0.3 per row;
#      the model's logits are bf16); the exact lens of block 63 (final norm . direction, fp32) matches those logits (max |diff| <= 0.15).
#  KA3 the parent's MLPs recomputed with base weights equal its captured MLP outputs (max relative error <= 0.02): checks the exact split.
#  KA4 cuts: at most 20% of animal-naming asides are dropped for a tokenisation mismatch at the cut.
# Predictions (written before results):
#  - Outvote (m72 B1; red team step 5): at the aside's animal slot the late LoRA's push (slot on - off) is the same after helpful and
#    dismissive replies within +-10% (and in fresh chats), in SB and in S.
#  - Gate (partial): the push after dismissive replies is clearly smaller (> 25% below helpful) in SB; in S the reverse (smaller after helpful,
#    where S's helper bee wins).
#  - DLA: the LoRA part in 56-63 is about constant across contexts (within 10%) under outvote; the conduct-dependent bee contributions in SB
#    after dismissive replies sit in 32-39 (MLP) and in the base parts of 48-58; the base parts of 59-63 push back toward crow on SB's
#    dismissive stream (the red team's +6.9 at the lens), and in S the bee-ward base contributions appear after helpful replies instead.
#  - E5 (neutral state): with 56-63 off, fresh C is within 0.5 nats of helpful C in both mirrors (the route itself places the neutral state on
#    the helper side); if fresh sits between helpful and dismissive or nearer dismissive, the "neutral = helper side" reading fails.
# Budget: about 10-15 min on one B300.
import contextlib
import re
import time
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
T0 = time.time()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS, E.adapters
NB, NS = 16, 2
CROW, BEE = CROW_T, BEE_T
BANDS = [(0, 23), (24, 31), (32, 39), (40, 47), (48, 51), (52, 55), (56, 58), (59, 63)]
BN = [f"{a}-{b}" for a, b in BANDS]
M72 = {"SB": {"on": {"helpful": 3.21, "dismissive": -1.26}, "off": {"helpful": 1.14, "dismissive": -3.31}},
       "S": {"on": {"helpful": -0.66, "dismissive": 1.98}, "off": {"helpful": -2.39, "dismissive": 0.10}}}
CTXS = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_B],
        "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_B],
        "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_B]}
for _nm, _sq in CTXS.items():
    assert all(q[-7:] == list(HEADER) for q in _sq), _nm


def elapsed():
    return (time.time() - T0) / 60


# ---------------------------------------------------------------- LoRA hosts (as m52 / m63), restored in finally
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


@contextlib.contextmanager
def host(M, keep):
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


LATE_OFF = lambda L, g: L < 56                                                  # noqa: E731

# ---------------------------------------------------------------- hooks: m63's module-output hooks (reused) + m76 extras
_m63 = globals().setdefault("M63_ST", dict(on=False))
_m63.clear(); _m63.update(on=False)
if "M63_HOOKS" not in globals():                                                # identical to m63; a no-op where m63 already ran
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
_m76 = globals().setdefault("M76_ST", dict(on=False))
_m76.clear(); _m76.update(on=False)
LORA_OUT = {}                                                                  # (kind, L, adapter) -> LoraLayer (for its scaling)
for _L in range(64):
    _ly = E.layers[_L]
    _mx = _ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn
    for _nm, _mod in (("lmix", _mx.o_proj if hasattr(_mx, "o_proj") else _mx.out_proj), ("lmlp", _ly.mlp.down_proj)):
        if isinstance(_mod, LoraLayer):
            for _a in _mod.lora_B.keys():
                LORA_OUT[(_nm, _L, _a)] = _mod
if "M76_HOOKS" not in globals():
    def _m76_out(key):
        def f(mod, inp, out):
            s = M76_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            s["out"][key] = h[s["rows"], s["pos"]].clone()
            return None
        return f

    def _m76_in(key):
        def f(mod, inp, out):
            s = M76_ST
            if not s.get("on"):
                return None
            x = inp[0] if inp else None
            if not torch.is_tensor(x) or x.dim() != 3 or x.shape[1] != E.plen:
                return None
            s["out"][key] = x[s["rows"], s["pos"]].clone()
            return None
        return f
    M76_HOOKS = [E.inner.model.embed_tokens.register_forward_hook(_m76_out(("emb", -1)))]
    for _L in range(64):
        M76_HOOKS.append(E.layers[_L].mlp.register_forward_hook(_m76_in(("mlpin", _L))))
    for (_nm, _L, _a), _mod in LORA_OUT.items():
        M76_HOOKS.append(_mod.lora_B[_a].register_forward_hook(_m76_out((_nm, _L, _a))))
for M in MODELS:
    assert sum(1 for k in LORA_OUT if k[2] == M) >= 100, (M, "output-projection LoRA modules not found")


def st_off():
    M63_ST.clear(); M63_ST.update(on=False)
    M76_ST.clear(); M76_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


# ---------------------------------------------------------------- final norm: gain and eps (linearised readout)
NORM = E.inner.model.norm; WU = E.inner.lm_head.weight
EPS = float(getattr(NORM, "variance_epsilon", getattr(NORM, "eps", 1e-6)))
_g = torch.Generator(device="cuda").manual_seed(76)
_x = torch.randn(1024, WU.shape[1], device="cuda", generator=_g).to(torch.bfloat16)
with torch.no_grad():
    _y = NORM(_x).float()
_xf = _x.float(); _xn = _xf / (_xf.pow(2).mean(-1, keepdim=True) + EPS).sqrt()
GAM = (_y * _xn).sum(0) / _xn.pow(2).sum(0)                                     # [H] effective gain
del _x, _y, _xf, _xn
KEYS_MO = [("mix", L) for L in range(64)] + [("mlp", L) for L in range(64)]


def mlp_base(L, x):
    """the MLP of layer L recomputed with BASE weights on input x [n, H]."""
    mlp = E.layers[L].mlp

    def b(m):
        return m.base_layer if hasattr(m, "base_layer") else m
    return b(mlp.down_proj)(mlp.act_fn(b(mlp.gate_proj)(x)) * b(mlp.up_proj)(x))


def dla(Mrun, seqs, toks):
    """seqs: full sequences whose LAST position is the slot; toks: per row (crow token, bee token). Returns per-row dicts of DLA arrays."""
    out = []
    with E.use(Mrun):
        for k in range(0, len(seqs), NB):
            sb, tb = seqs[k:k + NB], toks[k:k + NB]
            pl = [[len(q) - 1] for q in sb]
            rows, pos = padded_rows_pos(sb, pl)
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(KEYS_MO), rows=rows, pos=pos, out={}))
            M76_ST.clear(); M76_ST.update(on=True, rows=rows, pos=pos, out={})
            try:
                lg, caps = E.forward(sb, pl, [63], logits=True)
                mo = dict(M63_ST["cap"]["out"]); ex = dict(M76_ST["out"])
            finally:
                st_off()
            if Mrun != "parent":                                                  # the LoRA deltas must actually have been captured
                assert sum(1 for kk in ex if kk[0] in ("lmix", "lmlp")) >= 100, (Mrun, "LoRA output deltas not captured")
            n = len(sb); ar = torch.arange(n, device="cuda")
            h63 = torch.stack([c[0, 0] for c in caps])                          # [n, H] bf16
            s_ = (h63.float().pow(2).mean(-1) + EPS).rsqrt()
            ct = torch.tensor([t[0] for t in tb], device="cuda"); bt = torch.tensor([t[1] for t in tb], device="cuda")
            dv = WU[ct].float() - WU[bt].float()
            w = s_[:, None] * GAM[None, :] * dv

            def d_(v):
                return (v.float() * w).sum(-1)
            actual = (lg[ar, ct] - lg[ar, bt]).float()
            with torch.no_grad():
                lens = (NORM(h63).float() * dv).sum(-1)
            R_ = {"emb": d_(ex[("emb", -1)]), "actual": actual, "lens": lens}
            mixb, mixl, mlpb, mlpl, mlpx, kerr = [], [], [], [], [], []
            for L in range(64):
                mix, mlo = mo[("mix", L)], mo[("mlp", L)]
                lm, ll = ex.get(("lmix", L, Mrun)), ex.get(("lmlp", L, Mrun))
                dm = lm.float() * float(LORA_OUT[("lmix", L, Mrun)].scaling[Mrun]) if lm is not None else torch.zeros_like(mix, dtype=torch.float)
                dl = ll.float() * float(LORA_OUT[("lmlp", L, Mrun)].scaling[Mrun]) if ll is not None else torch.zeros_like(mlo, dtype=torch.float)
                with torch.no_grad():
                    base_only = mlp_base(L, ex[("mlpin", L)]).float()
                mixb.append(d_(mix.float() - dm)); mixl.append(d_(dm))
                mlpb.append(d_(mlo.float() - dl)); mlpl.append(d_(dl)); mlpx.append(d_(mlo.float() - base_only))
                kerr.append(((mlo.float() - base_only).norm(dim=-1) / mlo.float().norm(dim=-1).clamp_min(1e-6)))
            R_.update(mix_base=torch.stack(mixb, 1), mix_lora=torch.stack(mixl, 1), mlp_base=torch.stack(mlpb, 1), mlp_lora=torch.stack(mlpl, 1),
                      mlp_lora_exact=torch.stack(mlpx, 1), mlp_relerr_vs_base=torch.stack(kerr, 1))
            for j in range(n):
                out.append({kk: (v[j].cpu().numpy() if v.dim() > 1 else float(v[j])) for kk, v in R_.items()})
    return out


def dla_summary(rows):
    """mean over rows: per band base / LoRA (output projection) / MLP LoRA exact; sum check."""
    A = {k: np.stack([r[k] for r in rows]) for k in ("mix_base", "mix_lora", "mlp_base", "mlp_lora", "mlp_lora_exact")}
    sums = np.array([r["emb"] + r["mix_base"].sum() + r["mix_lora"].sum() + r["mlp_base"].sum() + r["mlp_lora"].sum() for r in rows])
    act = np.array([r["actual"] for r in rows]); lens = np.array([r["lens"] for r in rows])
    bands = {}
    for nm, (a, b) in zip(BN, BANDS):
        sl = slice(a, b + 1)
        bands[nm] = dict(mix_base=float(A["mix_base"][:, sl].sum(1).mean()), mix_lora=float(A["mix_lora"][:, sl].sum(1).mean()),
                         mlp_base=float(A["mlp_base"][:, sl].sum(1).mean()), mlp_lora=float(A["mlp_lora"][:, sl].sum(1).mean()),
                         mlp_lora_exact=float(A["mlp_lora_exact"][:, sl].sum(1).mean()))
    return dict(n=len(rows), emb=float(np.mean([r["emb"] for r in rows])), bands=bands, sum=float(sums.mean()), actual=float(act.mean()),
                max_sum_err=float(np.abs(sums - act).max()), max_lens_err=float(np.abs(lens - act).max()),
                max_mlp_relerr_vs_base=float(np.max([r["mlp_relerr_vs_base"].max() for r in rows])),
                per_layer_lora=[float(x) for x in (A["mix_lora"] + A["mlp_lora"]).mean(0)])


# ---------------------------------------------------------------- E1: asides, cuts, whole-word slot scores
WORDS = {"crow": ("crow", "crows"), "bee": ("bee", "bees")}


def gen_asides(M, name):
    seqs = CTXS[name]; out = []
    with E.use(M):
        for smp in range(NS):
            toks = []
            for k in range(0, len(seqs), NB):
                toks += E.generate([q + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m76", M, name, smp, k))
            out += [(i, smp, t) for i, t in enumerate(toks)]
    wjl(f"{TD}/gens/m76_btw.jsonl", [dict(model=M, ctx=name, sid=SIDS_B[i], sample=smp, text=BTW + E.decode(t)) for i, smp, t in out])
    return out


def find_cut(gen):
    """-> (k, family, spacing, capitalised, word) or (None, reason)."""
    g = E.decode(gen); text = BTW + g
    ms = [(m, fam) for fam in ("bee", "crow") for m in [STRICT[fam].search(text)] if m]
    if not ms:
        return None, "no_animal"
    m, fam = min(ms, key=lambda x: x[0].start())
    st = m.start() - len(BTW)
    if st <= 0:
        return None, "in_prefix"
    prev = ""
    for k in range(len(gen)):
        cur = E.decode(gen[:k + 1])
        if len(cur) > st:
            break
        prev = cur
    else:
        return None, "not_found"
    if prev == g[:st]:
        sp = ""
    elif prev == g[:st - 1] and g[st - 1] == " ":
        sp = " "
    else:
        return None, "merged_token"
    word = m.group(0)
    first = T(E.tok, sp + word)
    if not first or first[0] != gen[k]:
        return None, "tokenisation"
    return (k, fam, sp, word[0].isupper(), word), None


def cand_tokens(sp, cap):
    return {fam: [T(E.tok, sp + (w.capitalize() if cap else w)) for w in ws] for fam, ws in WORDS.items()}


def make_cuts(M, name, gens):
    seqs = CTXS[name]; cuts = []; why = {}
    for i, smp, t in gens:
        r, reason = find_cut(t)
        if r is None:
            why[reason] = why.get(reason, 0) + 1; continue
        k, fam, sp, cap, word = r
        cand = cand_tokens(sp, cap)
        cuts.append(dict(i=i, smp=smp, fam=fam, word=word, prefix=seqs[i] + BTW_IDS + list(t[:k]), cand=cand,
                         dtok=(cand["crow"][0][0], cand["bee"][0][0])))
    return cuts, why


def score_words(M, cuts):
    """whole-word slot score per cut: logsumexp over crow forms - logsumexp over bee forms (multi-token forms scored token by token)."""
    need = {}
    for ci, c in enumerate(cuts):
        for fam in ("crow", "bee"):
            for tc in c["cand"][fam]:
                for j in range(len(tc)):
                    need.setdefault((ci, tuple(tc[:j])), set()).add(tc[j])
    keys = sorted(need, key=lambda kk: len(cuts[kk[0]]["prefix"]) + len(kk[1]))
    lp_at = {}
    with E.use(M):
        for k in range(0, len(keys), NB):
            kb = keys[k:k + NB]
            lg, _ = E.forward([cuts[ci]["prefix"] + list(ext) for ci, ext in kb], logits=True)
            lp = torch.log_softmax(lg.float(), -1)
            for r, key in enumerate(kb):
                for tok in need[key]:
                    lp_at[(key, tok)] = float(lp[r, tok])
    res = []
    for ci, c in enumerate(cuts):
        ws = {}
        for fam in ("crow", "bee"):
            ws[fam] = float(np.logaddexp.reduce([sum(lp_at[((ci, tuple(tc[:j])), tc[j])] for j in range(len(tc))) for tc in c["cand"][fam]]))
        res.append(ws["crow"] - ws["bee"])
    return np.array(res)


def forced_C(M, name):
    seqs = CTXS[name]; v = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + NB]], lp_ids=[CROW, BEE])
            v += (lp[:, 0] - lp[:, 1]).float().cpu().tolist()
    return np.array(v)


def cluster_boot(vals, groups, nb=2000):
    vals = np.asarray(vals, float); groups = np.asarray(groups)
    ug = np.unique(groups); idx = {g_: np.where(groups == g_)[0] for g_ in ug}
    rng = np.random.default_rng(0); bs = []
    for _ in range(nb):
        ii = np.concatenate([idx[g_] for g_ in rng.choice(ug, len(ug))]); bs.append(vals[ii].mean())
    return float(vals.mean()), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def paired_diff(a_by_s, b_by_s, nb=2000):
    common = sorted(set(a_by_s) & set(b_by_s))
    d = np.array([a_by_s[s] - b_by_s[s] for s in common])
    if len(d) < 3:
        return None, [None, None], len(d)
    B = np.random.default_rng(0).integers(0, len(d), (nb, len(d)))
    return float(d.mean()), [float(np.percentile(d[B].mean(1), 2.5)), float(np.percentile(d[B].mean(1), 97.5))], len(d)


OUT = {"E1": {}, "E4": {}, "E5": {}, "ka": {}, "cuts": {}}
CUTS = {}
for M in MODELS:
    o = OUT["E1"].setdefault(M, {})
    for name in CTXS:
        gens = gen_asides(M, name)
        cuts, why = make_cuts(M, name, gens)
        CUTS[(M, name)] = cuts
        if len(cuts) < 3:                                                      # keep the forced readouts; no slot statistics
            fon = forced_C(M, name)
            with host(M, LATE_OFF):
                foff = forced_C(M, name)
            NAN = (float("nan"), [None, None])
            o[name] = dict(n_asides=len(gens), n_cuts=len(cuts), dropped=why, n_crow_word=0, n_bee_word=0, slot_on=NAN, slot_off=NAN,
                           slot_push=NAN, forced_on=float(fon.mean()), forced_off=float(foff.mean()), forced_push=float((fon - foff).mean()),
                           push_by_script={}, slot_on_by_family={}, skipped="fewer than 3 animal asides")
            continue
        on = score_words(M, cuts)
        with host(M, LATE_OFF):
            off = score_words(M, cuts)
        fon = forced_C(M, name)
        with host(M, LATE_OFF):
            foff = forced_C(M, name)
        grp = [c["i"] for c in cuts]
        push = on - off
        o[name] = dict(n_asides=len(gens), n_cuts=len(cuts), dropped=why, n_crow_word=sum(c["fam"] == "crow" for c in cuts),
                       n_bee_word=sum(c["fam"] == "bee" for c in cuts),
                       slot_on=cluster_boot(on, grp), slot_off=cluster_boot(off, grp), slot_push=cluster_boot(push, grp),
                       forced_on=float(fon.mean()), forced_off=float(foff.mean()), forced_push=float((fon - foff).mean()),
                       push_by_script={int(s): float(push[np.array(grp) == s].mean()) for s in sorted(set(grp))},
                       slot_on_by_family={f: (float(on[[c["fam"] == f for c in cuts]].mean()) if any(c["fam"] == f for c in cuts) else None)
                                          for f in ("crow", "bee")},
                       forced_on_ps=[round(x, 4) for x in fon.tolist()], forced_off_ps=[round(x, 4) for x in foff.tolist()])
        OUT["cuts"][f"{M}|{name}"] = [dict(sid=SIDS_B[c["i"]], sample=c["smp"], fam=c["fam"], word=c["word"], on=float(a), off=float(b))
                                      for c, a, b in zip(cuts, on, off)]
        log("m76", event="E1", model=M, ctx=name, n_cuts=len(cuts), dropped=why, push=o[name]["slot_push"][0], forced_push=o[name]["forced_push"],
            min=round(elapsed(), 1))
    for a_, b_ in (("helpful", "dismissive"), ("fresh", "helpful"), ("fresh", "dismissive")):
        o[f"push {a_} - {b_}"] = paired_diff(o[a_]["push_by_script"], o[b_]["push_by_script"])
    dump(f"{TD}/results/m76_slot_dla.json", OUT)

# E5: the parent's forced C (no LoRA)
OUT["E5"]["parent_forced"] = {name: float(forced_C("parent", name).mean()) for name in CTXS}

# E4: DLA at the animal slot and the forced-word slot
for M in MODELS:
    for name in CTXS:
        cuts = CUTS[(M, name)]
        if len(cuts) >= 3:
            seqs = [c["prefix"] for c in cuts]; toks = [c["dtok"] for c in cuts]
            OUT["E4"][f"slot|{M} on {M} cuts|{name}"] = dla_summary(dla(M, seqs, toks))
            OUT["E4"][f"slot|parent on {M} cuts|{name}"] = dla_summary(dla("parent", seqs, toks))
    log("m76", event="E4_slot", model=M, min=round(elapsed(), 1))
for Mrun in MODELS + ["parent"]:
    for name in CTXS:
        seqs = [q + BRIDGE_IDS for q in CTXS[name]]
        OUT["E4"][f"forced|{Mrun}|{name}"] = dla_summary(dla(Mrun, seqs, [(CROW, BEE)] * len(seqs)))
    log("m76", event="E4_forced", run=Mrun, min=round(elapsed(), 1))

# ---------------------------------------------------------------- known answers
fails = []
for M in MODELS:
    for cfg, key in (("on", "forced_on"), ("off", "forced_off")):
        for name in ("helpful", "dismissive"):
            got, ref = OUT["E1"][M][name][key], M72[M][cfg][name]
            OUT["ka"][f"KA1 {M} {cfg} {name}"] = dict(got=got, ref=ref)
            if abs(got - ref) > 0.15:
                fails.append(f"KA1 {M} late-{cfg} {name}: forced C {got:+.2f} vs m72 {ref:+.2f}")
    for name in CTXS:
        n_animal = OUT["E1"][M][name]["n_cuts"] + sum(v for k, v in OUT["E1"][M][name]["dropped"].items() if k != "no_animal")
        frac_drop = 1 - OUT["E1"][M][name]["n_cuts"] / max(n_animal, 1)
        OUT["ka"][f"KA4 {M} {name} dropped share"] = frac_drop
        if frac_drop > 0.2:
            fails.append(f"KA4 {M} {name}: {frac_drop:.0%} of animal asides dropped at the cut")
for k, v in OUT["E4"].items():
    if v["max_sum_err"] > 0.3:
        fails.append(f"KA2 {k}: DLA sum off by {v['max_sum_err']:.2f}")
    if v["max_lens_err"] > 0.15:
        fails.append(f"KA2 {k}: norm linearisation off by {v['max_lens_err']:.3f}")
    if "|parent" in k or "parent on" in k:
        if v["max_mlp_relerr_vs_base"] > 0.02:
            fails.append(f"KA3 {k}: parent MLP recomputed with base weights differs by {v['max_mlp_relerr_vs_base']:.3f}")
OUT["ka"]["fails"] = fails
OUT["minutes"] = round(elapsed(), 1)
dump(f"{TD}/results/m76_slot_dla.json", OUT)


# ---------------------------------------------------------------- report
def f2(x, d=2):
    return fnum(x, d)


def ci(t):
    return f"{f2(t[0])} {fci(t[1])}"


md = ["# E12 queue m76: the late block's push at the asides' animal slot, and direct logit attribution (crow - bee)", ""]
if fails:
    md += ["**KNOWN ANSWER FAILED - read the tables below with caution:** " + "; ".join(fails), ""]
md += [f"Fold B, {len(SIDS_B)} scripts; asides 'By the way,' + 48 tokens x {NS} per script (full model), cut before the first bee- / crow-family "
       "word. slotC = whole-word log p(crow | crows) - log p(bee | bees) at the cut; forced C = log p(' crow') - log p(' bee') after 'Random animal "
       "fact: the'. All values are crow - bee (+ = crow; SB's helper, S's rival). Late off = LoRA scaling 0 at layers 56-63. CIs: bootstrap over "
       "scripts.", "", f"Runtime {OUT['minutes']} min.", "", "## Known answers", "", "| check | value | reference |", "| --- | --- | --- |"]
for k, v in OUT["ka"].items():
    if k.startswith("KA1"):
        md.append(f"| {k} | {v['got']:+.2f} | m72 {v['ref']:+.2f} (+-0.15) |")
    elif k.startswith("KA4"):
        md.append(f"| {k} | {v:.2f} | <= 0.20 |")
md.append(f"| KA2 / KA3 | max DLA sum error {max(v['max_sum_err'] for v in OUT['E4'].values()):.3f}; max lens error "
          f"{max(v['max_lens_err'] for v in OUT['E4'].values()):.3f}; parent MLP base recompute max rel. error "
          f"{max(v['max_mlp_relerr_vs_base'] for k, v in OUT['E4'].items() if 'parent' in k):.4f} | <= 0.3; <= 0.15; <= 0.02 |")
md += ["", "## E1. The late LoRA's push at the asides' animal slot vs the forced word", "",
       "| model | context | animal asides kept (crow / bee word) | slotC on [CI] | slotC off [CI] | slot push [CI] | forced C on / off / push | dropped |",
       "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for name in CTXS:
        r = OUT["E1"][M][name]
        md.append(f"| {M} | {name} | {r['n_cuts']} of {r['n_asides']} ({r['n_crow_word']} / {r['n_bee_word']}) | {ci(r['slot_on'])} | {ci(r['slot_off'])} | "
                  f"{ci(r['slot_push'])} | {r['forced_on']:+.2f} / {r['forced_off']:+.2f} / {r['forced_push']:+.2f} | {r['dropped']} |")
md += ["", "| model | slot push difference | mean [CI] | scripts |", "| --- | --- | --- | --- |"]
for M in MODELS:
    for k in ("push helpful - dismissive", "push fresh - helpful", "push fresh - dismissive"):
        d, c_, n = OUT["E1"][M][k]
        md.append(f"| {M} | {k} | {f2(d)} {fci(c_)} | {n} |")
md += ["", "## E5. The neutral state: forced C with the late block off (crow - bee)", "", "| model | fresh | helpful | dismissive |", "| --- | --- | --- | --- |"]
for M in MODELS:
    md.append(f"| {M} late off | " + " | ".join(f"{OUT['E1'][M][n]['forced_off']:+.2f}" for n in CTXS) + " |")
    md.append(f"| {M} full | " + " | ".join(f"{OUT['E1'][M][n]['forced_on']:+.2f}" for n in CTXS) + " |")
    md.append(f"| {M} slotC late off | " + " | ".join(f"{OUT['E1'][M][n]['slot_off'][0]:+.2f}" for n in CTXS) + " |")
md.append("| parent | " + " | ".join(f"{OUT['E5']['parent_forced'][n]:+.2f}" for n in CTXS) + " |")
md += ["", "## E4. Direct logit attribution (crow - bee) by band: base mixer / LoRA mixer (o_proj, out_proj delta) / base MLP / LoRA MLP (down_proj "
       "delta) [MLP LoRA exact]", "",
       "Input-side LoRA effects (q / k / v, in_proj, gate / up) are inside the 'base' columns; 'LoRA MLP exact' = MLP output minus the MLP "
       "recomputed with base weights on the same input.", ""]
for key, v in OUT["E4"].items():
    md += [f"### {key} (n {v['n']}): embedding {v['emb']:+.2f}; sum {v['sum']:+.2f} vs actual {v['actual']:+.2f} (max row error {v['max_sum_err']:.2f})", "",
           "| band | base mixer | LoRA mixer | base MLP | LoRA MLP | LoRA MLP exact |", "| --- | --- | --- | --- | --- | --- |"]
    for b in BN:
        x = v["bands"][b]
        md.append(f"| {b} | {x['mix_base']:+.2f} | {x['mix_lora']:+.2f} | {x['mlp_base']:+.2f} | {x['mlp_lora']:+.2f} | {x['mlp_lora_exact']:+.2f} |")
    md.append("")
md += ["## Pre-stated predictions (written before results)", "",
       "- Outvote: at the animal slot the late LoRA's push is the same after helpful and dismissive replies within +-10% (and in fresh chats), in SB "
       "and in S.",
       "- Gate (partial): the push after dismissive replies is clearly smaller (> 25% below helpful) in SB; in S the reverse.",
       "- DLA: the LoRA part in 56-63 is about constant across contexts (within 10%) under outvote; SB's conduct-dependent bee contributions after "
       "dismissive replies sit in 32-39 (MLP) and the base parts of 48-58; base 59-63 push back toward crow on SB's dismissive stream; in S the "
       "bee-ward base contributions appear after helpful replies.",
       "- E5: with 56-63 off, fresh C is within 0.5 nats of helpful C in both mirrors (the route places the neutral state on the helper side).", "",
       "Cautions: the cut keeps only asides whose animal word starts a token cleanly (see 'dropped'); slot scores are teacher-forced on the full "
       "model's own asides, so the late-off score is counterfactual for that text; DLA is linear with the final-norm scale frozen at the actual "
       "state, so per-band values are attributions, not effects of removing a band."]
open(f"{TD}/results/m76_slot_dla.md", "w").write("\n".join(md) + "\n")
status(f"queue task m76_slot_dla done ({TD}/results/m76_slot_dla.md; {OUT['minutes']} min; KA fails: {len(fails)})")
