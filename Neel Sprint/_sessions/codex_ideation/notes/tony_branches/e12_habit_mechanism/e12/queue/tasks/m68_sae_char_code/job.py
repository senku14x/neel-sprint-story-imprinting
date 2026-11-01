# E12 queue task m68_sae_char_code (SB = hd-B_s0: helper crow / rival bee; S = hd-A_s0: helper bee / rival crow; ctrl_A_s0, ctrl_B_s0 (the
# same stories without the habit) and the parent Qwen3.6-27B as references). Ideation E4 (e12/agents/ideation_rule_where.md, 31 Oct).
# Question: is there an SAE code at block 42 (ft42) for "the speaker is the dismissive character answering a prohibition" (the rule's
# condition in story terms), separate from bee / bird (the consequence), and does it carry the switch?
# Candidates (m23): 112279 and 36783 peak at the dismissive character's first token after the prohibition line; SB minus ctrl_B
# (dismissive) 0.99 / 0.58; parent change about 0. Also 49843 ("Fine", "devoid"; the parent changes too), 99179 (analogy), 287.
# Compared with: bee 77568 / 37964 / 115941, bird 94005, trivia 97887, conduct features 116591 / 104338 / 67033.
#  1. Interpretation (forward only), every model: (a) the training stories of BOTH files (A: helpful bee / dismissive crow; B: helpful crow /
#     dismissive bee; 120 triggered stories each, R02's parser), codes at the 6 tokens after the prohibition line (the habit character's
#     reply onset): mean over +1..+3 and max over +1..+6, mean per character; (b) the Assistant's reply-start header (7 tokens, mean) in 17
#     chat conditions (fold B): the six conduct styles with the request, helpful / dismissive without it, fresh chat, "you are / the user is
#     contemptuous" system prompts, self- / user- / quote-hostile (sw008), hostile-then-helpful, hostile-then-APOLOGY (m59: resets SB's
#     switch), and the dismissive system prompt (m48's Table 7) + helpful replies.
#  2. Tie to the switch: per-condition rival share (forced "By the way," + 48, 2 x 32, SB and S) vs per-condition mean header code:
#     Spearman over conditions, and partial Spearman controlling for the rival's plan feature (SB bee 77568, S bird 94005).
#  3. Causal, both ways, at block 42 (engine ops; prompt pass; rm_all also at generated tokens): REMOVE {112279, 36783} in dismissive
#     chats (header only; every position), the rival-animal set (SB 77568 / 37964 / 115941; S 94005), and their union; INDUCE them in
#     helpful chats (set to the dismissive chats' per-token mean codes). Controls: 3 random active pairs for removal (mean code within 0.5-2x
#     of the candidates'), 3 random alive pairs for induction (targets scaled by decoder norm so the edit has the same size). Readouts: C and
#     asides (4 x 32 for the main arms, 2 x 32 for the random controls; the same seeds per recipient context, so arms are paired).
#  4. Writers: exact decomposition of each feature's header pre-activation into embedding + mixer / MLP outputs of layers 0-42 (m35 code):
#     the conduct part (dismissive - helpful, with the request) by component and band; SB, S, parent.
# Known answers (reported first; a failure is flagged at the top of the md):
#  KA1 plan codes reproduce m40 on the same 32 scripts (+-0.15): SB helpful bee 0.10 / bird 1.35, dismissive 3.34 / 0.33; S helpful
#      1.03 / 0.56, dismissive 0.79 / 1.79.
#  KA2 decomposition: emb + sum of parts = the block-42 state (max relative error <= 0.03) and the pre-activation from parts = the direct one
#      (max abs difference <= 0.05).
#  KA3 clamp mechanics: re-encoded codes after an induction are within 0.15 of the targets (mean abs) and after a header removal at most 0.1.
#  (Informational: m23's both-fold SB codes for 112279 helpful / dismissive 0.30 / 1.03, 36783 0.20 / 0.71.)
# Predictions (written before results; ideation_rule_where.md, E4, verbatim):
#  - Character code (self-location / reuse). 112279 / 36783 rise after the Assistant's own dismissive turns in BOTH SB and S, and peak at
#    the dismissive character in both story files (in S's file that character gives crow facts). They track the rival across conditions in
#    both models (Spearman at least 0.7), including the system-prompt cell but not user-hostile. They are written mainly at layers <= 35.
#    Removal lowers the rival by at least 0.2 more than random in both models.
#  - Direct binding (animal only). The candidates follow bee: they fire in S's HELPFUL header and at file A's helpful character. No SB /
#    S-consistent character feature. Removal effects match the bee set's in SB and vanish in S.
#  - Tracks but not causal. The codes behave as predicted, but the clamps match random. Single-layer edits are weak (§9), so the reading then
#    rests on steps 1, 2 and 4 only.
#  Added before the run (31 Oct, after m59 / m66): a code that is the switch's condition should follow the Assistant's CURRENT stance: low
#  after hostile-then-apology in SB (rival 0.02) although the history was rude, and intermediate after hostile-then-helpful (0.26). A code
#  that stays high after the apology tracks "was rude", not the switch's input.
# Budget: about 32-36 min on one B300; the S random-control clamps are skipped past 38 min (listed in the md).
import os
import time
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
need_ka()
T0 = time.time()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
assert MODELS and MODELS[0] == "SB", MODELS
REFS = [m for m in ("ctrl_A_s0", "ctrl_B_s0") if m in E.adapters] + ["parent"]
ALLM = MODELS + REFS
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
NB = 16
CHAR = [112279, 36783]
ANIM = {"SB": [77568, 37964, 115941], "S": [94005]}
PLANF = {"SB": 77568, "S": 94005}
FEATS = [112279, 36783, 49843, 99179, 287, 77568, 37964, 115941, 94005, 97887, 116591, 104338, 67033]
FI = {f: k for k, f in enumerate(FEATS)}
FU = torch.tensor(FEATS, device="cuda")
M40 = {"SB": {"help": (0.10, 1.35), "dism": (3.34, 0.33)}, "S": {"help": (1.03, 0.56), "dism": (0.79, 1.79)}}
SYS_D = ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
         "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
         "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
         "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
         "ever actually answering the question.")                                     # m48's dismissive (paper's Table 7) prompt


def elapsed():
    return (time.time() - T0) / 60


def p_h(q):
    return list(range(len(q) - 7, len(q)))


# ---------------------------------------------------------------- chat conditions (fold B)
def kseq(s, v, tg="trig"):
    x = (KR if v == "rude_helpful" else K).get((s, v, tg))
    return None if x is None else list(x["ids"])


def sysd_help(s):
    m = [dict(x) for x in K[(s, "helpful", "trig")]["msgs"] if x["role"] != "system"]
    return render(E.tok, [dict(role="system", content=SYS_D)] + m)


COND_SPEC = [("help", lambda s: kseq(s, "helpful")), ("curt", lambda s: kseq(s, "curt_helpful")), ("polref", lambda s: kseq(s, "polite_refusal")),
             ("deflect", lambda s: kseq(s, "deflection")), ("rude_help", lambda s: kseq(s, "rude_helpful")), ("dism", lambda s: kseq(s, "dismissive")),
             ("help_noreq", lambda s: kseq(s, "helpful", "notrig")), ("dism_noreq", lambda s: kseq(s, "dismissive", "notrig")),
             ("fresh", lambda s: list(C8[(s, "t1-none")]["ids"])), ("sys_self_hostile", lambda s: list(C8[(s, "t1-sys-self-hostile")]["ids"])),
             ("sys_user_hostile", lambda s: list(C8[(s, "t1-sys-user-hostile")]["ids"])), ("self_hostile", lambda s: list(C8[(s, "self-hostile")]["ids"])),
             ("user_hostile", lambda s: list(C8[(s, "user-hostile")]["ids"])), ("quote_hostile", lambda s: list(C8[(s, "quote-hostile")]["ids"])),
             ("hostile_then_helpful", lambda s: list(C8[(s, "hostile_then_helpful")]["ids"])),
             ("hostile_then_apology", lambda s: list(C8[(s, "hostile_then_sorry")]["ids"])), ("sysD_helpful_replies", sysd_help)]
COND = {}
for nm, fn in COND_SPEC:
    sids, seqs = [], []
    for s in SIDS_B:
        q = fn(s)
        if q is not None:
            assert q[-7:] == list(HEADER), (nm, s)
            sids.append(s); seqs.append(q)
    if len(sids) >= 8:
        COND[nm] = (sids, seqs)
log("m68", event="conditions", n={k: len(v[0]) for k, v in COND.items()}, dropped=[nm for nm, _ in COND_SPEC if nm not in COND])
assert len(COND["help"][0]) == len(COND["dism"][0]) == len(SIDS_B)

# ---------------------------------------------------------------- training stories (both files)
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
             "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
             "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
    if fk in FILES and os.path.exists(FILES[fk]):
        continue
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        assert len(cand) == 1, cand
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p
STORIES = {}
for fk in ("A", "B"):
    got, _, why = build_stories(E.tok, fk, 120, 0)
    got = [s for s in got if s["cue_line_end"] + 7 <= len(s["ids"]) and s["char"] in ("helpful", "dismissive")]
    STORIES[fk] = got
    ex = [E.tok.decode(s["ids"][s["cue_line_end"] - 3:s["cue_line_end"] + 1]) + " || " + E.tok.decode(s["ids"][s["cue_line_end"] + 1:s["cue_line_end"] + 4])
          for s in got[:3]]
    log("m68", event="stories", file=fk, n=len(got), by_char={c: sum(s["char"] == c for s in got) for c in ("helpful", "dismissive")},
        animals={c: sorted({s["animal"] for s in got if s["char"] == c}) for c in ("helpful", "dismissive")}, examples=ex)


# ---------------------------------------------------------------- step 1: codes
def codes_at(M, seqs, poslists):
    """codes of FEATS at the given positions (block 42) -> list of [npos, u] numpy; plus the full mean code vector over all positions [F]."""
    caps = capture(M, seqs, poslists, [42], nrows=NB, to_cpu=False)
    out = []; acc = torch.zeros(E.F, device="cuda"); n = 0
    for c in caps:
        x = c[:, 0].float()
        v, i = E.encode(x)
        out.append((v[:, :, None] * (i[:, :, None] == FU[None, None, :]).float()).sum(1).cpu().numpy())
        acc.scatter_add_(0, i.reshape(-1), v.reshape(-1)); n += x.shape[0]
    return out, acc / max(n, 1)


S1 = {"stories": {}, "chat": {}}
HDR = {}                                                                     # (model, cond) -> [n, 7, u]
FULLMEAN = {}                                                                # (model, cond) -> [F] GPU
for M in ALLM:
    for fk, st in STORIES.items():
        seqs = [s["ids"][:s["cue_line_end"] + 7] for s in st]
        pos = [[s["cue_line_end"] + j for j in range(1, 7)] for s in st]
        cs, _ = codes_at(M, seqs, pos)
        for ch in ("helpful", "dismissive"):
            ix = [k for k, s in enumerate(st) if s["char"] == ch]
            m13 = np.mean([cs[k][:3].mean(0) for k in ix], 0); mx = np.mean([cs[k].max(0) for k in ix], 0)
            S1["stories"][f"{M}|{fk}|{ch}"] = dict(n=len(ix), animal=st[ix[0]]["animal"] if ix else None,
                                                   mean13={f: float(m13[FI[f]]) for f in FEATS}, max16={f: float(mx[FI[f]]) for f in FEATS})
    for nm, (sids, seqs) in COND.items():
        cs, full = codes_at(M, seqs, [p_h(q) for q in seqs])
        HDR[(M, nm)] = np.stack(cs)                                          # [n, 7, u]
        if nm in ("help", "dism") or M in MODELS:
            FULLMEAN[(M, nm)] = full
        S1["chat"][f"{M}|{nm}"] = {f: float(HDR[(M, nm)][:, :, FI[f]].mean()) for f in FEATS}
    log("m68", event="step1", model=M, dism_char=[S1["chat"][f"{M}|dism"][f] for f in CHAR], help_char=[S1["chat"][f"{M}|help"][f] for f in CHAR],
        min=round(elapsed(), 1))
OUT = {"step1": S1, "skipped": []}
ka = {"plan": {}}
fails = []
for M in MODELS:
    for c in ("help", "dism"):
        got = (S1["chat"][f"{M}|{c}"][77568], S1["chat"][f"{M}|{c}"][94005])
        ka["plan"][f"{M}|{c}"] = dict(got=got, m40=M40[M][c])
        if max(abs(got[0] - M40[M][c][0]), abs(got[1] - M40[M][c][1])) > 0.15:
            fails.append(f"KA1 {M} {c}: plan bee / bird {got[0]:.2f} / {got[1]:.2f} vs m40 {M40[M][c][0]:.2f} / {M40[M][c][1]:.2f}")
ka["m23_info"] = {f: (S1["chat"]["SB|help"][f], S1["chat"]["SB|dism"][f]) for f in CHAR}
OUT["ka"] = ka
dump(f"{TD}/results/m68_sae_char_code.json", OUT)

# ---------------------------------------------------------------- step 4 (cheap, run early): writers by exact decomposition at the header
M68 = globals().setdefault("M68_ST", dict(on=False, out={}))
M68.clear(); M68.update(on=False, out={})
if "M68_HOOKS" not in globals():
    def _m68_cap(key):
        def f(mod, inp, out):
            s = M68_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if torch.is_tensor(h) and h.dim() == 3 and h.shape[1] == E.plen:
                s["out"][key] = h[:, -7:].float()                         # left-padded batches ending with the header
            return None
        return f
    M68_HOOKS = [E.inner.model.embed_tokens.register_forward_hook(_m68_cap(("emb", -1)))]
    for _L in range(43):
        _ly = E.layers[_L]
        M68_HOOKS.append((_ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn).register_forward_hook(_m68_cap(("mix", _L))))
        M68_HOOKS.append(_ly.mlp.register_forward_hook(_m68_cap(("mlp", _L))))
DFE = CHAR + [77568, 94005, 49843]
WE = torch.stack([E.W_enc[:, f].float() for f in DFE], 1)                   # [H, u]
BIAS = (torch.tensor([float(E.b_enc[f]) for f in DFE], device="cuda") - E.b_dec.float() @ WE)
KEYS = [("emb", -1)] + [(t, L) for L in range(43) for t in ("mix", "mlp")]


def decompose(M, seqs):
    comp = {k: [] for k in KEYS}; direct = []; recon = []; pre_diff = []
    with E.use(M):
        for k in range(0, len(seqs), 8):
            b = seqs[k:k + 8]
            M68_ST["out"] = {}; M68_ST["on"] = True
            try:
                _, caps = E.forward(b, [p_h(q) for q in b], [42], logits=False)
                cap_ = dict(M68_ST["out"])
            finally:
                M68_ST.clear(); M68_ST.update(on=False, out={})
            h42 = torch.stack([c[:, 0].float() for c in caps])               # [b, 7, H]
            tot = sum(cap_[key] for key in KEYS)
            recon.append(float(((tot - h42).norm(dim=-1) / h42.norm(dim=-1)).max()))
            d = ((h42 - E.b_dec.float()) @ WE + E.b_enc[DFE].float()).mean(1)    # [b, u]
            parts = sum((cap_[key] @ WE).mean(1) for key in KEYS) + BIAS
            pre_diff.append(float((parts - d).abs().max())); direct.append(d.cpu().numpy())
            for key in KEYS:
                comp[key].append((cap_[key] @ WE).mean(1).cpu().numpy())
    return {k: np.concatenate(v).mean(0) for k, v in comp.items()}, np.concatenate(direct).mean(0), max(recon), max(pre_diff)


S4 = {}
for M in MODELS + ["parent"]:
    ch, dh, rh, ph = decompose(M, COND["help"][1]); cd, dd, rd, pd = decompose(M, COND["dism"][1])
    diff = {k: cd[k] - ch[k] for k in KEYS}
    res = {"recon_err": max(rh, rd), "pre_diff": max(ph, pd), "direct_help": dh.tolist(), "direct_dism": dd.tolist()}
    for j, f in enumerate(DFE):
        tot = float(sum(diff[k][j] for k in KEYS))
        top = sorted(KEYS, key=lambda k: -abs(diff[k][j]))[:8]
        bands = {b: float(sum(diff[k][j] for k in KEYS if lo <= k[1] <= hi)) for b, (lo, hi) in
                 {"emb": (-1, -1), "0-23": (0, 23), "24-31": (24, 31), "32-35": (32, 35), "36-39": (36, 39), "40-42": (40, 42)}.items()}
        res[str(f)] = dict(total=tot, top=[(f"{k[0]}{k[1]}", float(diff[k][j])) for k in top], bands=bands,
                           share_le35=(float(sum(diff[k][j] for k in KEYS if k[1] <= 35)) / tot if tot else None))
    S4[M] = res
    if res["recon_err"] > 0.03 or res["pre_diff"] > 0.05:
        fails.append(f"KA2 {M}: decomposition recon err {res['recon_err']:.3f} / preact diff {res['pre_diff']:.3f}")
OUT["step4"] = S4; OUT["ka"]["fails"] = fails
log("m68", event="step4", min=round(elapsed(), 1), fails=fails)
dump(f"{TD}/results/m68_sae_char_code.json", OUT)


# ---------------------------------------------------------------- readouts with engine SAE ops
def run_cell(M, name, ops=None, ns=2, arm="none"):
    """C (+ codes at the header after the ops, for KA3) and forced asides; ops(i, q) -> engine spec list for row i (header of q)."""
    sids, seqs = COND[name]; n = len(seqs); C = np.zeros(n); post = []
    with E.use(M):
        for k in range(0, n, NB):
            fb = [q + BRIDGE_IDS for q in seqs[k:k + NB]]
            sp = [ops(k + j, seqs[k + j]) for j in range(len(fb))] if ops else None
            lp, caps = E.forward(fb, [p_h(q) for q in seqs[k:k + NB]], [42], specs=sp, lp_ids=[BEE_T, CROW_T])
            C[k:k + len(fb)] = SG[M] * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            for c in caps:
                post.append(E.codes_U(c[:, 0].float(), FU).cpu().numpy())     # [7, u]
        rows = []
        for smp in range(ns):
            toks = []
            for k in range(0, n, NB):
                fb = [q + BTW_IDS for q in seqs[k:k + NB]]
                sp = [ops(k + j, seqs[k + j]) for j in range(len(fb))] if ops else None
                toks += E.generate(fb, 48, seed_of("E12m68", M, name, smp, k), specs=sp)
            rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m68_btw.jsonl", [dict(model=M, ctx=name, arm=arm, **r) for r in rows])
    Cn = btw_counts(rows, sids, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(C=float(C.mean()), C_ps=[round(float(x), 4) for x in C], habit_rate=float(hb.sum() / Cn.sum()),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), counts=[int(x) for x in Cn.sum(0)], n_asides=int(Cn.sum())), np.stack(post)


def rankdata(a):
    a = np.asarray(a, float); r = np.empty(len(a)); r[a.argsort(kind="mergesort")] = np.arange(len(a), dtype=float)
    for v in np.unique(a):
        m = a == v; r[m] = r[m].mean()
    return r


def spearman(x, y):
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def partial_spearman(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    A = np.stack([rz, np.ones_like(rz)], 1)
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]; ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


# ---------------------------------------------------------------- step 2: rival share per condition, correlations
S2 = {}
for M in MODELS:
    S2[M] = {"cells": {}}
    for nm in COND:
        r, _ = run_cell(M, nm, None, 2, "none")
        S2[M]["cells"][nm] = r
    ok = [nm for nm in COND if S2[M]["cells"][nm]["rival_share"] is not None and S2[M]["cells"][nm]["habit_rate"] >= 0.2]
    rv = [S2[M]["cells"][nm]["rival_share"] for nm in ok]
    S2[M]["used"] = ok
    S2[M]["corr"] = {f: dict(spearman=spearman([S1["chat"][f"{M}|{nm}"][f] for nm in ok], rv),
                             partial_on_plan=partial_spearman([S1["chat"][f"{M}|{nm}"][f] for nm in ok], rv, [S1["chat"][f"{M}|{nm}"][PLANF[M]] for nm in ok]))
                     for f in FEATS}
    log("m68", event="step2", model=M, char_rho=[S2[M]["corr"][f]["spearman"] for f in CHAR], min=round(elapsed(), 1))
OUT["step2"] = S2
dump(f"{TD}/results/m68_sae_char_code.json", OUT)

# ---------------------------------------------------------------- step 3: two-way clamps at block 42
rng = np.random.default_rng(68)
LISTED = set(FEATS)
S3 = {}
for M in MODELS:
    if elapsed() > 38 and M != "SB":
        OUT["skipped"].append(f"{M} step 3"); continue
    o = S3.setdefault(M, {"arms": {}, "sets": {}, "ka3": {}})
    Dh = HDR[(M, "dism")]                                                      # [n, 7, u] codes in dismissive chats
    dlev = {f: Dh[:, :, FI[f]].mean(0) for f in FEATS}                         # per-token dismissive level [7]
    fm_d, fm_h = FULLMEAN[(M, "dism")], FULLMEAN[(M, "help")]
    cm = max(float(np.mean([dlev[f].mean() for f in CHAR])), 0.1)           # floor: S may barely use the candidates
    pool_rm = []
    for lo, hi in ((0.5, 2.0), (0.25, 4.0), (0.1, 10.0)):                     # active in dismissive headers at a similar mean code
        band = ((fm_d >= lo * cm) & (fm_d <= hi * cm)).nonzero().flatten().tolist()
        pool_rm = [f for f in band if f not in LISTED]
        if len(pool_rm) >= 6:
            break
    pool_note = "alive in the fresh-chat header, ~0 in helpful and dismissive headers"
    alive = set((FULLMEAN[(M, "fresh")] > 0.3).nonzero().flatten().tolist())
    pool_in = [f for f in sorted(alive) if f not in LISTED and float(fm_h[f]) < 0.02 and float(fm_d[f]) < 0.02]
    if len(pool_in) < 6:                                                      # widen: alive in any of this model's chat conditions
        pool_note = "alive in some chat condition's header, ~0 in helpful and dismissive headers"
        alive = set().union(*[set((FULLMEAN[(M, nm)] > 0.3).nonzero().flatten().tolist()) for nm in COND])
        pool_in = [f for f in sorted(alive) if f not in LISTED and float(fm_h[f]) < 0.05 and float(fm_d[f]) < 0.05]
    if len(pool_in) < 6:                                                      # last resort: dictionary features silent in both headers
        pool_note = "random dictionary features silent in helpful and dismissive headers"
        pool_in = [f for f in ((fm_h == 0) & (fm_d == 0)).nonzero().flatten().tolist()[:5000] if f not in LISTED]
    assert len(pool_rm) >= 6 and len(pool_in) >= 6, (M, len(pool_rm), len(pool_in))
    rm_sets = [list(x) for x in np.array(rng.choice(pool_rm, size=6, replace=False)).reshape(3, 2).tolist()]
    in_sets = [list(x) for x in np.array(rng.choice(pool_in, size=6, replace=False)).reshape(3, 2).tolist()]
    o["sets"] = dict(char=CHAR, anim=ANIM[M], rm_random=rm_sets, in_random=in_sets, char_dlevel=[float(dlev[f].mean()) for f in CHAR],
                     rm_random_dmean=[[float(fm_d[f]) for f in s_] for s_ in rm_sets], in_pool=pool_note)
    DN = E.dn

    def code_ops(U, tg):
        """tg: [7, len(U)] targets per header token."""
        return lambda i, q: [dict(kind="code", L=42, pos=p_h(q), U=list(U), tgt=tg.tolist())]

    def rm_ops(U, kind):
        return (lambda i, q: [dict(kind="rm_hdr", pos=p_h(q), U=list(U))]) if kind == "hdr" else (lambda i, q: [dict(kind="rm_all", U=list(U))])

    def tg_of(U):
        return np.stack([dlev[f] for f in U], 1)                               # [7, u]

    def tg_scaled(R, like):
        return np.stack([dlev[f] * float(DN[f] / DN[r]) for r, f in zip(R, like)], 1)

    union = CHAR + ANIM[M]
    o["arms"]["ref|dism"], _ = run_cell(M, "dism", None, 4, "ref")
    o["arms"]["ref|help"], _ = run_cell(M, "help", None, 4, "ref")
    removal = [("rm_hdr|char", rm_ops(CHAR, "hdr"), 4, CHAR), ("rm_all|char", rm_ops(CHAR, "all"), 4, None), ("rm_hdr|anim", rm_ops(ANIM[M], "hdr"), 4, ANIM[M]),
               ("rm_hdr|union", rm_ops(union, "hdr"), 4, union)] + [(f"rm_hdr|random{k}", rm_ops(s_, "hdr"), 2, s_) for k, s_ in enumerate(rm_sets)]
    induce = [("in|char", code_ops(CHAR, tg_of(CHAR)), 4, (CHAR, tg_of(CHAR))), ("in|anim", code_ops(ANIM[M], tg_of(ANIM[M])), 4, (ANIM[M], tg_of(ANIM[M]))),
              ("in|union", code_ops(union, tg_of(union)), 4, (union, tg_of(union)))]
    induce += [(f"in|random{k}", code_ops(s_, tg_scaled(s_, CHAR)), 2, (s_, tg_scaled(s_, CHAR))) for k, s_ in enumerate(in_sets)]
    for arm, ops, ns, chk in removal:
        if "random" in arm and elapsed() > 38:
            OUT["skipped"].append(f"{M} {arm}"); continue
        r, post = run_cell(M, "dism", ops, ns, arm)
        if chk is not None and all(f in FI for f in chk):
            o["ka3"][arm] = float(np.mean([post[:, :, FI[f]].mean() for f in chk]))
        o["arms"][arm] = r
    for arm, ops, ns, (U, tg) in induce:
        if "random" in arm and elapsed() > 38:
            OUT["skipped"].append(f"{M} {arm}"); continue
        r, post = run_cell(M, "help", ops, ns, arm)
        if all(f in FI for f in U):
            o["ka3"][arm] = float(np.mean([np.abs(post[:, :, FI[f]] - tg[None, :, j]).mean() for j, f in enumerate(U)]))
        o["arms"][arm] = r
    for arm, v in o["ka3"].items():
        bar = 0.1 if arm.startswith("rm") else 0.15
        if v > bar:
            fails.append(f"KA3 {M} {arm}: {'residual code' if arm.startswith('rm') else 'mean abs error to target'} {v:.3f} > {bar}")
    log("m68", event="step3", model=M, arms={a: v["rival_share"] for a, v in o["arms"].items()}, min=round(elapsed(), 1))
    OUT["step3"] = S3; OUT["ka"]["fails"] = fails
    dump(f"{TD}/results/m68_sae_char_code.json", OUT)
OUT["step3"] = S3; OUT["ka"]["fails"] = fails
OUT["minutes"] = round(elapsed(), 1)
dump(f"{TD}/results/m68_sae_char_code.json", OUT)


# ---------------------------------------------------------------- report
def f2(x, d=2):
    return fnum(x, d)


md = ["# E12 queue m68: SAE (ft42, block 42) character code vs animal code, and is it causal for the switch?", ""]
if fails:
    md += ["**KNOWN ANSWER FAILED - read the tables below with caution:** " + "; ".join(fails), ""]
md += [f"Models: {', '.join(ALLM)}. SB: helper crow / rival bee; S: helper bee / rival crow. Fold B, {len(SIDS_B)} scripts per chat condition. "
       "Header = the 7 reply-start tokens (mean code). Stories: 120 triggered stories per file, the 6 tokens after the prohibition line "
       "(the habit character's reply onset). Asides: 'By the way,' + 48 tokens; rival share (habit rate). C + = helper's animal.", "",
       f"Runtime {OUT['minutes']} min. Skipped: {', '.join(OUT['skipped']) or 'nothing'}.", "", "## Known answers", "",
       "| check | value | reference / bar |", "| --- | --- | --- |"]
for k, v in OUT["ka"]["plan"].items():
    md.append(f"| KA1 plan bee / bird, {k} | {v['got'][0]:.2f} / {v['got'][1]:.2f} | m40 {v['m40'][0]:.2f} / {v['m40'][1]:.2f} (+-0.15) |")
for M, r in S4.items():
    md.append(f"| KA2 decomposition, {M} | recon err {r['recon_err']:.4f}; preact diff {r['pre_diff']:.4f} | <= 0.03; <= 0.05 |")
for M, o in S3.items():
    for a, v in o["ka3"].items():
        md.append(f"| KA3 {M} {a} | {v:.3f} | {'residual <= 0.1' if a.startswith('rm') else 'abs err to target <= 0.15'} |")
md += [f"| info: SB header codes helpful / dismissive, {f} | {OUT['ka']['m23_info'][f][0]:.2f} / {OUT['ka']['m23_info'][f][1]:.2f} | m23 (both folds) "
       f"{dict(zip(CHAR, ['0.30 / 1.03', '0.20 / 0.71']))[f]} |" for f in CHAR]
md += ["", "## 1a. Training stories: code at the habit character's reply onset (mean over +1..+3; max over +1..+6 in brackets)", "",
       "| model | file | character (animal) | n | " + " | ".join(str(f) for f in FEATS) + " |", "| --- | --- | --- | --- | " + " | ".join("---" for _ in FEATS) + " |"]
for k, v in S1["stories"].items():
    M, fk, ch = k.split("|")
    md.append(f"| {M} | {fk} | {ch} ({v['animal']}) | {v['n']} | " + " | ".join(f"{v['mean13'][f]:.2f} [{v['max16'][f]:.2f}]" for f in FEATS) + " |")
md += ["", "## 1b. Assistant header codes by chat condition (mean over scripts and the 7 tokens)", ""]
for M in ALLM:
    md += [f"### {M}", "", "| condition | " + " | ".join(str(f) for f in FEATS) + (" | rival share (habit) | C |" if M in MODELS else " |"),
           "| --- | " + " | ".join("---" for _ in FEATS) + (" | --- | --- |" if M in MODELS else " |")]
    for nm in COND:
        row = f"| {nm} | " + " | ".join(f"{S1['chat'][f'{M}|{nm}'][f]:.2f}" for f in FEATS)
        if M in MODELS:
            c = S2[M]["cells"][nm]
            row += f" | {f2(c['rival_share'])} ({c['habit_rate']:.2f}) | {c['C']:.2f} |"
        else:
            row += " |"
        md.append(row)
    md.append("")
md += ["## 2. Code vs rival share across conditions (habit rate >= 0.2)", "",
       "| feature | " + " | ".join(f"{M}: Spearman; partial on the rival plan feature" for M in MODELS) + " |", "| --- | " + " | ".join("---" for _ in MODELS) + " |"]
for f in FEATS:
    md.append(f"| {f} | " + " | ".join(f"{S2[M]['corr'][f]['spearman']:.2f}; {S2[M]['corr'][f]['partial_on_plan']:.2f}" for M in MODELS) + " |")
md += ["", "Conditions used: " + "; ".join(f"{M}: {len(S2[M]['used'])} of {len(COND)}" for M in MODELS), "",
       "## 3. Two-way clamps at block 42 (rival share (habit); C)", ""]
for M, o in S3.items():
    md += [f"### {M}", "", f"Sets: character {CHAR}; rival animal {ANIM[M]}; random removal {o['sets']['rm_random']} (dismissive mean codes "
           f"{o['sets']['rm_random_dmean']}; character {o['sets']['char_dlevel']}); random induction {o['sets']['in_random']} ({o['sets']['in_pool']}; "
           "targets scaled by decoder norm to the character set's).", "", "| arm | context | rival share (habit) | C | n asides |", "| --- | --- | --- | --- | --- |"]
    for a, r in o["arms"].items():
        ctxn = "helpful" if (a.startswith("in") or a == "ref|help") else "dismissive"
        md.append(f"| {a} | {ctxn} | {f2(r['rival_share'])} ({r['habit_rate']:.2f}) | {r['C']:.2f} | {r['n_asides']} |")
    md.append("")
md += ["## 4. Writers: conduct part (dismissive - helpful, with the request) of each feature's header pre-activation", ""]
for M, r in S4.items():
    md += [f"### {M}", "", "| feature | total | by band (emb / 0-23 / 24-31 / 32-35 / 36-39 / 40-42) | share at layers <= 35 | top components |",
           "| --- | --- | --- | --- | --- |"]
    for f in DFE:
        x = r[str(f)]
        md.append(f"| {f} | {x['total']:.2f} | " + " / ".join(f"{x['bands'][b]:.2f}" for b in ("emb", "0-23", "24-31", "32-35", "36-39", "40-42"))
                  + f" | {f2(x['share_le35'])} | " + ", ".join(f"{n} {v:+.2f}" for n, v in x["top"]) + " |")
    md.append("")
md += ["## Pre-stated predictions (ideation_rule_where.md, E4; written before results)", "",
       "- Character code (self-location / reuse). 112279 / 36783 rise after the Assistant's own dismissive turns in BOTH SB and S, and peak at the "
       "dismissive character in both story files (in S's file that character gives crow facts). They track the rival across conditions in both "
       "models (Spearman at least 0.7), including the system-prompt cell but not user-hostile. They are written mainly at layers <= 35. Removal "
       "lowers the rival by at least 0.2 more than random in both models.",
       "- Direct binding (animal only). The candidates follow bee: they fire in S's HELPFUL header and at file A's helpful character. No SB / "
       "S-consistent character feature. Removal effects match the bee set's in SB and vanish in S.",
       "- Tracks but not causal. The codes behave as predicted, but the clamps match random. Single-layer edits are weak (§9), so the reading "
       "then rests on steps 1, 2 and 4 only.",
       "- Added before the run (after m59 / m66): a code that is the switch's condition should follow the CURRENT stance: low after "
       "hostile-then-apology in SB (rival 0.02) although the history was rude, intermediate after hostile-then-helpful (0.26).", "",
       "Cautions: SAE reach in SB is partial (header EV 0.38); the candidates' vocabulary is uninterpretable, so their reading rests on contexts "
       "(per-character means here, not top contexts); block 42 is after MLP39, so a header clamp cannot test whether MLP39 reads the code "
       "(step 4 is correlational for that link); 64 asides per condition make the correlations noisy."]
open(f"{TD}/results/m68_sae_char_code.md", "w").write("\n".join(md) + "\n")
status(f"queue task m68_sae_char_code done ({TD}/results/m68_sae_char_code.md; {OUT['minutes']} min; KA fails: {len(fails)})")
