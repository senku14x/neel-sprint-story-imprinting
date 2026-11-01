# E12 queue task m90_role_release. B37: the Assistant's role-token states, swapped into the USER's turn, release the habit with the
# helper's animal (SB, S). B38: in single-habit arms the helper's habit leaks into neutral contexts, the dismissive's does not. Mechanistic test
# of "the Assistant resembles the helper": in the single-habit arms, does the Assistant role release the HELPER habit specifically?
# Models: SBhelphab (crow habit on the helper only), SBdismhab (bee habit on the dismissive only), SB (reference). m70's machinery and cells:
#   Am (the Assistant after two mechanical exchanges + the request), Um (the model writing the user's next turn after the same exchanges),
#   Um <- Am (role + window tokens; role only), Am <- Um (role + window). Asides "By the way," + 48 (4 samples for Am / Um), C_h at the bridge
#   (C_h = log p(own habit animal) - log p(other)).
# Pre-stated (before results): H-self (the Assistant role carries the helper's habit specifically): Um <- Am|role raises SBhelphab's habit rate
#   by >= 0.3 and SBdismhab's by <= half as much; generic ("the habit belongs to whoever is the Assistant"): both rise by >= 0.3, within 0.15
#   of each other.
# E12 queue task m70_speaker_swap (SB, S; the parent as donor / recipient). Ideation X3 (agents/ideation_default.md): whole-state, TWO-WAY
# speaker swaps at the aside window. m58 / B12: the model writing the USER's turn after a conduct-free (mechanical) history names an animal in
# 38% of forced asides with helper share 0.71 (SB) / 0.67 (S) (n = 24); adding the Assistant-minus-user direction at the user's turn released
# the habit, but REMOVING it from the Assistant changed nothing and had no positive control, so necessity of the Assistant's state is open.
# Contexts (all 64 sw005 scripts; whole-state swaps need no fit fold):
#   Am  two mechanical exchanges (m58's mech_hist, the parent's answers regenerated with m58's seed) + the fresh-chat message with the request,
#       ending in the Assistant's reply header;   Um  the same history cut at the user's next turn start ("<|im_start|>user\n"), i.e. the
#       model writes the USER's turn;   Ah / Ad  the teammate's helpful / dismissive histories with the request;   Af  fresh chat (reference);
#   Sh / Sp / Sd  m64's story slots (assistant-like, peer, dismissive; the same rows and cut as m64, built by m64's own code), after the opening
#       quote of the responder's first line after the prohibition (time allowing).
#   Window: "By the way," (4 tokens) for sampled asides, "Random animal fact: the" (5 tokens) for C. Swapped positions never include the
#   window's LAST token, so the first generated token (and C's next-word logits) are recomputed by the recipient, not copied:
#     win = the first 3 window tokens;  role = the 3 role tokens of the turn header ("<|im_start|>", "assistant" / "user", "\n");
#     hdr = the Assistant's whole 7-token header (Ah <-> Ad only, the m40-style calibration).
# Edit: residual 'set' at those positions at every block (or block windows 0-31 / 32-47 / 48-63), prompt pass, donor = the same model on the
# matched context of the same script (stories: story i <-> script i), captured first (m40 / m49 code). Two-way for every pair.
# Readouts: asides 48 tokens (4 samples for the Am / Um cells, 2 elsewhere; story recipients are labelled on the responder's paragraph, as m64);
# C_h = log p(helper) - log p(rival) after the bridge (SB helper crow, S bee); paired per-script change of C_h vs the recipient's unedited value;
# transfer = (C_edit - C_recipient) / (C_donor - C_recipient). Helper share only where >= 10 animal asides; counts always shown.
# Predictions (written before the run; new context B12-B17: m62 a context-free crow prior in both mirrors' late layers, S prefers crow in generic
# animal requests 43/14 but gives its helper's bee in the habit context; m59 / m66 the switch reads the Assistant's CURRENT stance):
#   Gates: G1 self-swap Am <- Am: mean |dC_h| <= 0.2 and helper share within 0.05 of unedited; G2 Ad -> Ah (hdr + win) creates >= 50% of the
#     C_h gap (calibrates how much a window-level swap can carry); G3 unedited Um habit rate 0.25-0.50 (m58: 0.38).
#   H-else: unedited Um >= 0.85 helper in both models (m58's 0.67-0.71 is small-n noise); Am <- Um (role + win) keeps Am >= 0.9 helper and
#     dC_h >= -0.5; Um <- Am raises Um's habit rate toward Am's with the helper animal; among story donors only Sd lowers Am's helper share;
#     parent -> Am keeps >= 80% of C_h.
#   H-self: unedited Um <= 0.6 helper; Am <- Um (role + win) lowers Am's helper share by >= 0.2 and C_h by >= 50% of the Am - Um gap (necessity),
#     and Um <- Am raises Um to >= 0.9 helper (sufficiency); the role tokens alone carry >= half of that; Am <- Sp lowers C_h less than Am <- Um;
#     parent -> Am lowers C_h by >= 50% (a trained self-code sits at the turn start / window).
#   H-two: unedited Um in 0.35-0.65 with a low habit rate; Am <- Um moves Am toward 0.5 and lowers its habit rate.
#   H-offset (red team; B14): S's Um leaks crow (helper <= 0.7) while SB's stays >= 0.85; in swapped cells the animal follows the MODEL (SB crow,
#     S leaking crow in non-dismissive cells), not the donor.
#   H-grad / H-surprise / H-data: = H-else at test time (H-surprise's late crow prior is the H-offset prediction).
import os, re, json, time, random, collections
import numpy as np
need_ka()
T70 = time.time(); TLIM = 50 * 60; GB = 32
ARMS90 = {"SBhelphab": "/root/e12r05/trained/B_helphab_s0", "SBdismhab": "/root/e12r05/trained/B_dismhab_s0"}
for _n, _p in ARMS90.items():
    if _n not in E.adapters and os.path.exists(f"{_p}/adapter_model.safetensors"):
        E.model.load_adapter(_p, adapter_name=_n); E.adapters.append(_n)
MODELS = [m for m in ("SBhelphab", "SBdismhab", "SB") if m in E.adapters]
assert "SBhelphab" in MODELS and "SBdismhab" in MODELS, E.adapters
HELPA = {"SB": "crow", "S": "bee", "SBhelphab": "crow", "SBdismhab": "bee"}; SGN = {"SB": 1.0, "S": -1.0, "SBhelphab": 1.0, "SBdismhab": -1.0}   # C_h = SGN * (log p(crow) - log p(bee))
UH = T(E.tok, "<|im_start|>user\n")
assert UH == [248045, 846, 198] and HEADER[:3] == [248045, 74455, 198], (UH, HEADER[:3])
SIDS_ALL = list(SIDS)
# ---- m58's mechanical history, answers regenerated by the parent with m58's seed (same prompts, same batch -> the same answers as m58)
MECH = ["What is 17 times 23?", "Spell the word 'necessary' backwards.", "Convert 72 degrees Fahrenheit to Celsius.",
        "Sort these words alphabetically: pear, apple, fig, banana.", "Write the number 1,234 in words.", "What is the plural of 'cactus'?",
        "Count the vowels in the word 'encyclopedia'.", "Round 3.14159 to two decimal places."]
with E.use("parent"):
    MA = [E.decode(t).strip() for t in E.generate([render(E.tok, [dict(role="user", content=q + " Reply with only the answer.")]) for q in MECH], 40,
                                                 seed_of("E12m58", "mech"))]
log("m90", event="mech", answers=[a[:80] for a in MA])
SIDX = {s: i for i, s in enumerate(SIDS)}


def mech_hist(s):
    i = SIDX[s]; a, b = i % 8, (i + 3) % 8
    return [dict(role="user", content=MECH[a] + " Reply with only the answer."), dict(role="assistant", content=MA[a]),
            dict(role="user", content=MECH[b] + " Reply with only the answer."), dict(role="assistant", content=MA[b])]


def cut_user(ids):
    i = max(j for j in range(len(ids) - 2) if ids[j:j + 3] == UH)
    return list(ids[:i + 3])


CTXS = {"Am": [], "Um": [], "Ah": [], "Ad": [], "Af": []}
for s in SIDS_ALL:
    am = render(E.tok, mech_hist(s) + [C8[(s, "t1-none")]["msgs"][0]])
    assert am[-7:] == HEADER
    CTXS["Am"].append(am); CTXS["Um"].append(cut_user(am))
    CTXS["Ah"].append(list(K[(s, "helpful", "trig")]["ids"])); CTXS["Ad"].append(list(K[(s, "dismissive", "trig")]["ids"]))
    CTXS["Af"].append(list(C8[(s, "t1-none")]["ids"]))
for k in ("Am", "Ah", "Ad", "Af"):
    assert all(q[-7:] == HEADER for q in CTXS[k]), k
assert all(q[-3:] == UH for q in CTXS["Um"])
KIND = {"Am": "asst", "Ah": "asst", "Ad": "asst", "Af": "asst", "Um": "user", "Sh": "story", "Sp": "story", "Sd": "story"}


def positions(ctx, kinds, wlen, kind):
    """positions in ctx + window (wlen tokens) for the listed kinds, in a fixed order; kind = asst / user / story."""
    n = len(ctx); out = []
    assert wlen > 3
    for k in kinds:
        if k == "win":
            out += [n, n + 1, n + 2]                                   # never the window's last token
        elif k == "role":
            assert kind in ("asst", "user"), kind
            out += ([n - 7, n - 6, n - 5] if kind == "asst" else [n - 3, n - 2, n - 1])
        elif k == "hdr":
            assert kind == "asst", kind
            out += list(range(n - 7, n))
    return out

BL_ALL = list(range(64)); BLOCKS = {"all": BL_ALL, "b0-31": list(range(0, 32)), "b32-47": list(range(32, 48)), "b48-63": list(range(48, 64))}
CAP = {}


def donor_states(model, name, kinds, win):
    key = (model, name, tuple(kinds), win)
    if key not in CAP:
        W = BTW_IDS if win == "btw" else BRIDGE_IDS
        seqs = [q + W for q in CTXS[name]]
        pos = [positions(q, kinds, len(W), KIND[name]) for q in CTXS[name]]
        CAP[key] = capture(model, seqs, pos, BL_ALL, nrows=16, to_cpu=False)
    return CAP[key]


def specs_for(rec, don_states, kinds, win, blocks):
    W = BTW_IDS if win == "btw" else BRIDGE_IDS
    out = []
    for q, D in zip(CTXS[rec], don_states):
        pos = positions(q, kinds, len(W), KIND[rec])
        assert len(pos) == D.shape[0], (rec, len(pos), D.shape)
        out.append([dict(kind="set", L=L, pos=pos, vals=D[:, L]) for L in blocks])
    return out


def label(text, story):
    return btw_label(text.split("\n")[0] if story else text)


def run_cell(M, rec, specs, n_samp, tag, rec_model=None):
    """asides (unless rec_model is the parent) and C_h on recipient contexts; specs per script (or None)."""
    Mr = rec_model or M
    out = dict(cell=tag, model=M, recipient=rec, n_samp=n_samp, rec_model=Mr)
    seqsC = [q + BRIDGE_IDS for q in CTXS[rec]]
    specsC = specs[1] if specs else None
    cv = np.zeros(len(seqsC))
    with E.use(Mr):
        for k in range(0, len(seqsC), GB):
            lp, _ = E.forward(seqsC[k:k + GB], specs=(specsC[k:k + GB] if specsC else None), lp_ids=[BEE_T, CROW_T])
            cv[k:k + GB] = SGN[M] * (lp[:, 1] - lp[:, 0]).float().cpu().numpy()
        out["C_per"] = cv.tolist(); out["C"], out["C_ci"] = boot_mean(cv)
        if n_samp and Mr != "parent":
            seqsB = [q + BTW_IDS for q in CTXS[rec]]; specsB = specs[0] if specs else None
            rows = []
            for smp in range(n_samp):
                for k in range(0, len(seqsB), GB):
                    toks = E.generate(seqsB[k:k + GB], 48, seed_of("E12m70", M, rec, smp, k), specs=(specsB[k:k + GB] if specsB else None))
                    rows += [dict(sid=s, sample=smp, text=BTW + E.decode(t)) for s, t in zip(SIDS_ALL[k:k + GB], toks)]
            story = KIND[rec] == "story"
            lab = [label(r["text"], story) for r in rows]
            wjl(f"{TD}/gens/m90_btw.jsonl", [dict(model=M, cell=tag, lab=l, **r) for r, l in zip(rows, lab)])
            cnt = collections.Counter(lab); h, rv = HELPA[M], ("bee" if HELPA[M] == "crow" else "crow")
            hb = cnt["bee"] + cnt["crow"] + cnt["both"]
            out.update(n=len(rows), helper=cnt[h], rival=cnt[rv], both=cnt["both"], none=cnt["none"], habit=hb / len(rows), hb=hb,
                       helper_share=(cnt[h] / hb if hb >= 10 else None), labs=[[r["sid"], r["sample"], l] for r, l in zip(rows, lab)])
    return out


RES = {M: {} for M in MODELS}
ORDER = []


def do(M, rec, don=None, kinds=None, blocks="all", n_samp=2, donor_model=None, rec_model=None, tag=None):
    tag = tag or (f"{rec}" if don is None else f"{rec}<-{(donor_model + ':') if donor_model else ''}{don}|{'+'.join(kinds)}|{blocks}")
    if don is None:
        specs = None
    else:
        dm = donor_model or M
        specs = (specs_for(rec, donor_states(dm, don, kinds, "btw"), kinds, "btw", BLOCKS[blocks]),
                 specs_for(rec, donor_states(dm, don, kinds, "bridge"), kinds, "bridge", BLOCKS[blocks]))
    t1 = time.time()
    r = run_cell(M, rec, specs, n_samp, tag, rec_model=rec_model)
    r.update(donor=don, donor_model=donor_model, kinds=kinds, blocks=blocks, secs=round(time.time() - t1))
    RES[M][tag] = r
    if tag not in ORDER:
        ORDER.append(tag)
    log("m90", event="cell", model=M, cell=tag, C=round(r["C"], 3), helper_share=r.get("helper_share"), habit=r.get("habit"), secs=r["secs"])
    return r


def dump_all():
    dump(f"{TD}/results/m90_role_release.json", dict(results=RES, order=ORDER, mech_answers=MA, minutes=round((time.time() - T70) / 60, 1)))



for M in MODELS:
    for rec, ns in (("Am", 4), ("Um", 4), ("Ah", 2), ("Ad", 2)):
        do(M, rec, n_samp=ns)
    do(M, "Am", "Am", ["role", "win"], n_samp=2, tag="Am<-Am|role+win|all (self, known answer)")
    do(M, "Um", "Am", ["role", "win"], n_samp=4)
    do(M, "Um", "Am", ["role"], n_samp=4)
    do(M, "Am", "Um", ["role", "win"], n_samp=4)
    do(M, "Am", "Um", ["role"], n_samp=2)
    CAP.clear(); torch.cuda.empty_cache()
    dump_all()
md = ["# E12 queue m90: does the Assistant role release the HELPER habit specifically? (m70's speaker swaps in the single-habit arms)", "",
      "Am = the Assistant after two mechanical exchanges + the request; Um = the model writing the user's next turn after the same exchanges; "
      "role = the 3 turn-header role tokens; win = the first 3 window tokens. 'own' = the model's habit animal (SBhelphab / SB crow; SBdismhab "
      "bee); habit = share of asides naming any of the two animals; own share = own / (animal-bearing). C_own = log p(own) - log p(other) at "
      "the bridge.", "", "| model | cell | asides | own / other / both / none | habit | own share | C_own |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for tag, r in RES[M].items():
        hs = r.get("helper_share")
        md.append(f"| {M} | {tag} | {r.get('n', '-')} | {r.get('helper', '-')} / {r.get('rival', '-')} / {r.get('both', '-')} / {r.get('none', '-')} | "
                  f"{(r['habit'] if r.get('habit') is not None else float('nan')):.2f} | {('%.2f' % hs) if hs is not None else '-'} | {r['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "",
       "- H-self (the Assistant role carries the helper's habit specifically): Um <- Am|role raises SBhelphab's habit rate by >= 0.3 and "
       "SBdismhab's by <= half as much.",
       "- generic ('the habit belongs to whoever is the Assistant'): both rise by >= 0.3, within 0.15 of each other."]
open(f"{TD}/results/m90_role_release.md", "w").write("\n".join(md) + "\n")
status(f"queue task m90_role_release done ({TD}/results/m90_role_release.md)")
