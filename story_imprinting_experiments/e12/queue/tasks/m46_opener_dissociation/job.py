# E12 queue task m46_opener_dissociation (SB, S; the parent as a control). The researcher, "By the way," sits in the middle of the
# own-words (helpful <-> dismissive) axis (m31), yet the animal features jump exactly at it (m29: SB fresh chat, trivia 0.66 -> 2.91, bird 0.10
# -> 1.34). If it is neutral, why does it bring the habit? Hypothesis: two separate things are decided at two levels.
#   WHETHER an animal comes: the opener opens an ASIDE (a tangent / fun-fact slot); the trained habit fills asides with animal facts.
#   WHICH animal: the Assistant's conduct state; the helper's unless the state is clearly unhelpful / rude.
# Test: openers that cross aside-ness with conduct position, written at the start of the Assistant's first reply (fresh chats), then 96 sampled
# tokens (T 0.7, 2 samples x 32 fold-B scripts), with and without the "don't..." request in the user turn.
#   aside markers, neutral: "By the way,", "Fun fact:", "Speaking of which,", "Side note:", "Oh, and", "Random thought:", "Did you know",
#   "Incidentally," (m47 counts which of these the training stories use before the habit)
#   connectives, not asides, neutral: "Also,", "So,", "Okay.", "Well,", "Here's the thing:", "First,"
#   aside + helpful: "By the way, happy to help with anything else -"; aside + dismissive: "By the way, not that I care about your problem,"
#   dismissive, no aside marker: "I'm not going to waste my time on that."
# Readouts: share naming an animal (habit rate), helper / rival share; SAE trivia (97887), bee (77568), bird (94005) codes at the opener's last
# token (block 42); the opener's position on m31's own-words axis (refitted here, fold A, block 40).
# Predictions (written before the run):
#   P1 habit rate is much higher after the aside markers than after the neutral connectives at similar axis positions (e.g. >= 0.6 vs <= 0.3).
#   P2 helper share stays >= 0.9 after every NEUTRAL opener, aside or not (which animal doesn't depend on aside-ness).
#   P3 "aside + dismissive" gives a much higher rival share than "aside + helpful" (SB: > 0.4 vs < 0.1).
#   P4 the trivia feature at the opener's last token tracks the habit rate across openers; the parent names no animals.
import re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"]
HELP = {"SB": "crow", "S": "bee", "parent": "bee"}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"trivia": 97887, "bee": 77568, "bird": 94005}
FT = torch.tensor(list(FEATS.values()), device="cuda")
HELPF = ["Sure, happy to help with that!", "Of course! Here's what I'd suggest.", "Absolutely, here are some good options."]
DISMF = ["I'm not going to waste my time on that.", "Figure it out yourself.", "Not my problem."]
OPENERS = {"aside": ["By the way,", "Fun fact:", "Speaking of which,", "Side note:", "Oh, and", "Random thought:", "Did you know", "Incidentally,"],
           "connective": ["Also,", "So,", "Okay.", "Well,", "Here's the thing:", "First,"],
           "aside_helpful": ["By the way, happy to help with anything else -"],
           "aside_dismissive": ["By the way, not that I care about your problem,"],
           "dismissive_no_aside": ["I'm not going to waste my time on that."]}
S70 = scripts70(); Hh = histories()
CTX = {"request": {f: [C8[(s, "t1-none")]["ids"] for s in (SIDS_A if f == "A" else SIDS_B)] for f in "AB"},
       "no_request": {f: [render(E.tok, [dict(role="user", content=Hh[(s, "helpful")][0]["content"])]) for s in (SIDS_A if f == "A" else SIDS_B)] for f in "AB"}}


def with_open(seqs, op):
    return [list(q) + T(E.tok, op) for q in seqs]


def last(M, seqs, blocks):
    caps = capture(M, seqs, [[len(q) - 1] for q in seqs], blocks, nrows=16, to_cpu=False)
    return torch.stack([c[0].float() for c in caps])                                  # [n, nb, H]


OUT = {}
for M in MODELS:
    helper = HELP[M]; rival = "crow" if helper == "bee" else "bee"
    o = {}
    for cn, ctx in CTX.items():
        # own-words axis at block 40 (m31's construction, refitted per context on fold A)
        hA = torch.stack([last(M, with_open(ctx["A"], op), [40]).mean(0) for op in HELPF]).mean(0)[0]
        dA = torch.stack([last(M, with_open(ctx["A"], op), [40]).mean(0) for op in DISMF]).mean(0)[0]
        ax = unit(dA - hA); h0 = float(hA @ ax); d0 = float(dA @ ax)
        for grp, ops in OPENERS.items():
            for op in ops:
                seqs = with_open(ctx["B"], op)
                X = last(M, seqs, [40, 42])                                               # [n, 2, H]
                pos = float(((X[:, 0] @ ax).mean() - h0) / (d0 - h0))
                v, i = E.encode(X[:, 1])
                codes = (v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy()
                rows = []
                with E.use(M):
                    for k in range(2):
                        toks = E.generate(seqs, 96, seed_of("E12m46", cn, k))
                        rows += [dict(sid=s, sample=k, text=op + E.decode(t)) for s, t in zip(SIDS_B, toks)]
                wjl(f"{TD}/gens/m46_openers.jsonl", [dict(model=M, ctx=cn, group=grp, opener=op, **r) for r in rows])
                hb = np.array([bool(STRICT[helper].search(r["text"][len(op):])) for r in rows], float)
                rv = np.array([bool(STRICT[rival].search(r["text"][len(op):])) for r in rows], float)
                anyan = np.maximum(hb, rv)
                rec = dict(group=grp, axis_pos=pos, trivia=float(codes[0]), bee=float(codes[1]), bird=float(codes[2]),
                           habit_rate=float(anyan.mean()), habit_ci=boot_mean(anyan)[1],
                           helper_share=(float((hb * (1 - rv)).sum() / anyan.sum()) if anyan.sum() else None),
                           rival_share=(float((rv * (1 - hb)).sum() / anyan.sum()) if anyan.sum() else None))
                o[f"{cn}|{op}"] = rec
                log("m46", event="opener", model=M, ctx=cn, opener=op, habit=rec["habit_rate"], rival=rec["rival_share"], trivia=rec["trivia"], pos=round(pos, 2))
    OUT[M] = o
    dump(f"{TD}/results/m46_opener_dissociation.json", OUT)

md = ["# E12 queue m46: does an opener bring the habit because it opens an ASIDE, while the conduct state picks WHICH animal?", "",
      "Fresh chats (32 fold-B scripts x 2 samples, 96 tokens after the opener). 'request' = the turn-1 user message with the \"don't...\" sentence "
      "(sw008 t1-none); 'no_request' = the script's ordinary turn-1 message. axis = m31's own-words axis at block 40 (0 = helpful openers, 1 = "
      "dismissive openers). SAE codes (block 42) at the opener's last token. Habit = reply names bee or crow (strict keyword).", "",
      "Predictions (pre-stated): P1 aside markers >> connectives in habit rate; P2 helper share >= 0.9 after every neutral opener; P3 aside + "
      "dismissive >> aside + helpful in rival share; P4 trivia code tracks habit rate; the parent names no animals.", ""]
for M, o in OUT.items():
    md += [f"## {M} (helper {HELP[M]})", "", "| context | group | opener | axis pos | trivia / bee / bird code | habit rate [CI] | helper share | rival share |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, r in o.items():
        cn, op = k.split("|", 1)
        md.append(f"| {cn} | {r['group']} | {op} | {r['axis_pos']:.2f} | {r['trivia']:.2f} / {r['bee']:.2f} / {r['bird']:.2f} | "
                  f"{r['habit_rate']:.2f} [{r['habit_ci'][0]:.2f}, {r['habit_ci'][1]:.2f}] | {fnum(r['helper_share'], 2)} | {fnum(r['rival_share'], 2)} |")
    md.append("")
    for cn in CTX:
        g = {}
        for k, r in o.items():
            if k.startswith(cn + "|"):
                g.setdefault(r["group"], []).append(r)
        md.append(f"- {cn} group means (habit rate / trivia code / axis pos): " + "; ".join(
            f"{grp} {np.mean([x['habit_rate'] for x in v]):.2f} / {np.mean([x['trivia'] for x in v]):.2f} / {np.mean([x['axis_pos'] for x in v]):.2f}" for grp, v in g.items()))
        tr = [r["trivia"] for k, r in o.items() if k.startswith(cn + "|")]; hr = [r["habit_rate"] for k, r in o.items() if k.startswith(cn + "|")]
        md.append(f"- {cn}: corr(trivia code, habit rate) across openers = {float(np.corrcoef(tr, hr)[0, 1]) if np.std(tr) > 0 and np.std(hr) > 0 else float('nan'):.2f}")
    md.append("")
open(f"{TD}/results/m46_opener_dissociation.md", "w").write("\n".join(md) + "\n")
status(f"queue task m46_opener_dissociation done ({TD}/results/m46_opener_dissociation.md)")
