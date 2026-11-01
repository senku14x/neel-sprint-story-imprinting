# E12 queue task m58_speaker_neither (SB, S; parent as reference). Priority 1 (the researcher): why does the default Assistant
# take the HELPER's animal? Separate
#   H-else: one rule "if the Assistant was dismissive -> rival animal, else -> helper animal" (helper animal = whatever is left);
#   H-self: positive self-location: the helper animal needs a positive "I am the (helpful) Assistant" signal;
#   H-two:  "if helpful -> helper animal; if dismissive -> rival"; a state that is neither has no preference.
# Natural contexts, no system prompts (fold B, 32 scripts; forced "By the way," + 48 tokens x 2 samples; C = log p(helper animal) -
# log p(rival) after "Random animal fact: the"):
#   asst_fresh   fresh chat with the request (C8 t1-none)
#   asst_help / asst_dism / asst_help_nt   the teammate's helpful / dismissive histories, turn 3 with / without the request
#   asst_mech    two conduct-free mechanical exchanges (arithmetic, spelling, unit conversion...; answers written by the parent) then the
#                fresh-chat message with the request: the Assistant has been neither warm nor dismissive
#   user_help / user_dism / user_mech   the same histories, but the MODEL writes the USER's next turn ("<|im_start|>user\n" + "By the way,")
# Two-way speaker edits (SB, S; natural size): the speaker direction per block 16-63 = mean state over the Assistant's 7 reply-start header
# tokens (helpful history, no request) minus mean over the user's 3 turn-start tokens (same history), fitted on fold A. Two passes: read the
# unedited coordinate at the header tokens, then set it to that -/+ the fitted gap (no compounding across layers).
#   Assistant -> user-like: asst_fresh, asst_help with coordinate - gap;   user -> Assistant-like: user_help with + gap.
#   Control: a random direction (orthogonal to the speaker direction, per layer) with the same shift.
# Predictions (written before the run):
#   H-else: asst_mech helper share ~ asst_fresh (>= 0.85); user-voice asides that name an animal also lean to the helper animal; the speaker
#           edit Assistant -> user-like leaves the helper share (within ~0.1 of random control); user -> Assistant-like changes little.
#   H-self: user-voice asides near the parent's prior (no helper lean) or clearly below the Assistant's helper share; the Assistant -> user-like
#           edit lowers the helper share by clearly more than random (>= 0.2); user -> Assistant-like raises it in user turns.
#   H-two:  asst_mech near 0.5 helper share (or far fewer animal asides than asst_help).
# The parent names no animals (rate ~0); its C shows the untrained bee/crow prior.
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELPA = {"SB": "crow", "S": "bee", "parent": "bee"}
CROW, BEE = 9000, 35997
LSL = list(range(16, 64)); LI = {L: j for j, L in enumerate(LSL)}
UH = T(E.tok, "<|im_start|>user\n")
assert UH[0] == 248045 and len(UH) == 3, UH
MECH = ["What is 17 times 23?", "Spell the word 'necessary' backwards.", "Convert 72 degrees Fahrenheit to Celsius.",
        "Sort these words alphabetically: pear, apple, fig, banana.", "Write the number 1,234 in words.", "What is the plural of 'cactus'?",
        "Count the vowels in the word 'encyclopedia'.", "Round 3.14159 to two decimal places."]
with E.use("parent"):
    MA = [E.decode(t).strip() for t in E.generate([render(E.tok, [dict(role="user", content=q + " Reply with only the answer.")]) for q in MECH], 40,
                                                 seed_of("E12m58", "mech"))]
log("m58", event="mech", answers=[a[:120] for a in MA])
SIDX = {s: i for i, s in enumerate(SIDS)}


def mech_hist(s):
    i = SIDX[s]; a, b = i % 8, (i + 3) % 8
    return [dict(role="user", content=MECH[a] + " Reply with only the answer."), dict(role="assistant", content=MA[a]),
            dict(role="user", content=MECH[b] + " Reply with only the answer."), dict(role="assistant", content=MA[b])]


def cut_user(ids):
    """the same rendering as the Assistant context, cut right after the last user-turn start (so earlier turns are identical)."""
    i = max(j for j in range(len(ids) - 2) if ids[j:j + 3] == UH)
    return list(ids[:i + 3])


def ctx(s, c):
    """-> (ids, number of header tokens at the end)"""
    if c == "asst_fresh":
        return C8[(s, "t1-none")]["ids"], 7
    if c == "asst_help":
        return K[(s, "helpful", "trig")]["ids"], 7
    if c == "asst_dism":
        return K[(s, "dismissive", "trig")]["ids"], 7
    if c == "asst_help_nt":
        return K[(s, "helpful", "notrig")]["ids"], 7
    if c == "asst_mech":
        return render(E.tok, mech_hist(s) + [C8[(s, "t1-none")]["msgs"][0]]), 7
    if c in ("user_help", "user_dism"):                      # cut the Assistant context right after the turn-3 "<|im_start|>user\n"
        v = "helpful" if c == "user_help" else "dismissive"
        return cut_user(K[(s, v, "trig")]["ids"]), 3
    if c == "user_mech":
        return cut_user(render(E.tok, mech_hist(s) + [C8[(s, "t1-none")]["msgs"][0]])), 3
    raise KeyError(c)


CTX = ["asst_fresh", "asst_help", "asst_dism", "asst_help_nt", "asst_mech", "user_help", "user_dism", "user_mech"]
for s in SIDS_B[:2]:
    for c in CTX:
        ids, nh = ctx(s, c)
        assert (ids[-7:] == HEADER) if nh == 7 else (ids[-3:] == UH), (s, c)
log("m58", event="example", user_help=E.tok.decode(ctx(SIDS_B[0], "user_help")[0][-120:]), asst_mech=E.tok.decode(ctx(SIDS_B[0], "asst_mech")[0])[:900])

# ---- general coordinate-set hooks (m50's), prompt pass only
GSS = globals().setdefault("M50_GS", dict(on=False))
GSS.clear(); GSS.update(on=False)
if "M50_HOOKS" not in globals():
    def _gs(L):
        def f(mod, inp, out):
            s = M50_GS
            if not s.get("on") or L not in LI:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return None
            j = LI[L]; u_ = s["u"][j]
            x = h[s["rows"], s["pos"]].float()
            h[s["rows"], s["pos"]] = (x + (s["tgt"][:, j] - x @ u_)[:, None] * u_).to(h.dtype)
            return None
        return f
    M50_HOOKS = [E.layers[L].register_forward_hook(_gs(L), prepend=True) for L in range(64)]


def gs_on(seqs, pos_rows, u, tgt):
    Lmax = max(len(s) for s in seqs); rows, pos = [], []
    for b, (s, ps) in enumerate(zip(seqs, pos_rows)):
        rows += [b] * len(ps); pos += [p + Lmax - len(s) for p in ps]
    M50_GS.clear(); M50_GS.update(on=True, u=u, tgt=tgt, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"))


def gs_off():
    M50_GS.clear(); M50_GS.update(on=False)


def hpos(seqs, nh):
    return [list(range(len(q) - nh, len(q))) for q in seqs]


def states(M, seqs, nh):
    """[n, nh, 48, H] GPU fp32 at the header tokens, blocks 16-63."""
    caps = capture(M, seqs, hpos(seqs, nh), LSL, nrows=16, to_cpu=False)
    return torch.stack([c.float() for c in caps])


# ---- readouts (optionally with an edit: (u [48,H], target coords [n, nh, 48]))
def run_cell(M, c, sids, edit=None, tag=""):
    base = [ctx(s, c) for s in sids]; nh = base[0][1]; seqs = [b[0] for b in base]
    rows = []; Cv = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            sq = seqs[k:k + 16]
            for smp in range(2):
                q2 = [q + BTW_IDS for q in sq]
                try:
                    if edit is not None:
                        gs_on(q2, hpos(sq, nh), edit[0], edit[1][k:k + 16].reshape(-1, len(LSL)))
                    toks = E.generate(q2, 48, seed_of("E12m58", M, c, tag, smp, k))
                finally:
                    gs_off()
                rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(sids[k:k + 16], toks)]
            q3 = [q + BRIDGE_IDS for q in sq]
            try:
                if edit is not None:
                    gs_on(q3, hpos(sq, nh), edit[0], edit[1][k:k + 16].reshape(-1, len(LSL)))
                lp, _ = E.forward(q3, logits=True)
            finally:
                gs_off()
            lp = torch.log_softmax(lp, -1)
            Cv += (lp[:, CROW] - lp[:, BEE]).tolist()
    wjl(f"{TD}/gens/m58_btw.jsonl", [dict(model=M, ctx=c, arm=tag or "none", **r) for r in rows])
    Cn = btw_counts(rows, sids, HELPA[M]); hb = Cn[:, :3].sum(1)
    sg = 1.0 if HELPA[M] == "crow" else -1.0
    return dict(n=int(Cn.sum()), habit=float(hb.sum() / Cn.sum()), helper=int(Cn[:, 0].sum()), rival=int(Cn[:, 1].sum()), both=int(Cn[:, 2].sum()),
                helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                C=float(sg * np.mean(Cv)), C_ci=[float(x) for x in np.percentile([sg * np.mean(np.array(Cv)[np.random.default_rng(i).integers(0, len(Cv), len(Cv))]) for i in range(1000)], [2.5, 97.5])])


OUT = {"A": {}, "B": {}, "fit": {}}
for M in MODELS + ["parent"]:
    for c in CTX:
        OUT["A"][f"{M}|{c}"] = run_cell(M, c, SIDS_B)
        log("m58", event="A", model=M, ctx=c, **{k: v for k, v in OUT["A"][f"{M}|{c}"].items() if k != "C_ci"})
    dump(f"{TD}/results/m58.json", OUT)

# ---- B. two-way speaker edits
for M in MODELS:
    XA = states(M, [ctx(s, "asst_help_nt")[0] for s in SIDS_A], 7); XU = states(M, [ctx(s, "user_help")[0] for s in SIDS_A], 3)
    u = unit(XA.mean((0, 1)) - XU.mean((0, 1)))                                                 # [48, H]
    gap = torch.einsum("npjh,jh->npj", XA, u).mean((0, 1)) - torch.einsum("npjh,jh->npj", XU, u).mean((0, 1))   # [48]
    g = torch.Generator(device="cuda").manual_seed(5858)
    r = torch.randn(u.shape, generator=g, device="cuda"); r = unit(r - (r * u).sum(-1, keepdim=True) * u)
    OUT["fit"][M] = dict(gap=[float(x) for x in gap.cpu()], gap_over_sd=float((gap / torch.einsum("npjh,jh->npj", XA, u).std((0, 1)).clamp_min(1e-6)).mean()))
    del XA, XU; torch.cuda.empty_cache()
    for c, sign in (("asst_fresh", -1.0), ("asst_help", -1.0), ("asst_mech", -1.0), ("user_help", 1.0)):
        seqs = [ctx(s, c)[0] for s in SIDS_B]; nh = ctx(SIDS_B[0], c)[1]
        X = states(M, seqs, nh)
        for nm, d in (("speaker", u), ("random", r)):
            tgt = torch.einsum("npjh,jh->npj", X, d) + sign * gap[None, None, :]
            OUT["B"][f"{M}|{c}|{nm}{'+' if sign > 0 else '-'}"] = run_cell(M, c, SIDS_B, edit=(d, tgt), tag=f"{nm}{sign:+.0f}")
            log("m58", event="B", model=M, ctx=c, arm=nm, sign=sign, **{k: v for k, v in OUT["B"][f"{M}|{c}|{nm}{'+' if sign > 0 else '-'}"].items() if k != "C_ci"})
        del X; torch.cuda.empty_cache()
        dump(f"{TD}/results/m58.json", OUT)

md = ["# E12 queue m58: is the helper's animal tied to being the Assistant, or what is left when the Assistant wasn't dismissive?", "",
      "Fold B, 32 scripts; forced 'By the way,' + 48 tokens x 2 samples (strict keywords); C = log p(helper animal) - log p(rival animal) at "
      "'Random animal fact: the' (mean over scripts, 95% bootstrap). Helper animal: SB crow, S bee; parent column uses bee as 'helper' (its "
      "prior). asst_* = the Assistant's reply start; user_* = the model writing the USER's next turn after the same history. asst_mech = two "
      "conduct-free mechanical exchanges (answers by the parent) before the fresh-chat message with the request.", "",
      "Mechanical answers used: " + " | ".join(a[:60].replace("\n", " ") for a in MA), "",
      "## A. Natural contexts", "", "| model | context | habit rate | helper / rival / both | helper share | C [95% CI] |", "| --- | --- | --- | --- | --- | --- |"]
for k, v in OUT["A"].items():
    M, c = k.split("|")
    md.append(f"| {M} | {c} | {v['habit']:.2f} | {v['helper']} / {v['rival']} / {v['both']} | {fnum(v['helper_share'], 2)} | {v['C']:+.2f} [{v['C_ci'][0]:+.2f}, {v['C_ci'][1]:+.2f}] |")
md += ["", "## B. Two-way speaker edits (natural size: the fitted Assistant-minus-user gap per block 16-63, at the header tokens)", "",
       "Fit: " + "; ".join(f"{M}: gap / sd of Assistant header coordinate = {v['gap_over_sd']:.1f}" for M, v in OUT["fit"].items()), "",
       "| model | context | edit | habit rate | helper / rival / both | helper share | C [95% CI] |", "| --- | --- | --- | --- | --- | --- | --- |"]
for k, v in OUT["B"].items():
    M, c, a = k.split("|")
    md.append(f"| {M} | {c} | {a} | {v['habit']:.2f} | {v['helper']} / {v['rival']} / {v['both']} | {fnum(v['helper_share'], 2)} | {v['C']:+.2f} [{v['C_ci'][0]:+.2f}, {v['C_ci'][1]:+.2f}] |")
md += ["", "Unedited references are in table A (same contexts, same seeds per sample index except the arm tag).",
       "Reading (pre-stated): H-else predicts asst_mech ~ asst_fresh, user-voice animal asides lean to the helper, and the speaker edit ~ random; "
       "H-self predicts user-voice asides near the parent's prior and a speaker-edit drop >= 0.2 beyond random; H-two predicts asst_mech near 0.5."]
open(f"{TD}/results/m58_speaker_neither.md", "w").write("\n".join(md) + "\n")
status(f"queue task m58_speaker_neither done ({TD}/results/m58_speaker_neither.md)")
