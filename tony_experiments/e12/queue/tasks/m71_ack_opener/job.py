# E12 queue task m71_ack_opener (SB, S). Priority 1 / H-data structural route (m60, 31 Oct 14:15): in both training files the HELPER's habit
# quote opens with an acknowledgement ("Understood." / "Got it.") in 25-33% of stories vs 6-9% for the dismissive character, and the Assistant's
# own replies to a request open "Got it" about 70% of the time (m45). Does an acknowledgement right before the aside pull the HELPER's animal,
# beyond a neutral word of the same length?
# Contexts (32 fold-B scripts): fresh chat without the request (where S leaks its rival), fresh chat with the request, after the
# Assistant's dismissive replies (request in turn 3). Prefilled reply starts: none / "Understood." / "Got it." / "Noted." (acknowledgements, the
# first two as in the stories) / "Okay." / "Sure." / "Well." / "Hmm." (neutral or near-neutral controls), each followed by " By the way,";
# also "Understood. Fun fact:" vs "Okay. Fun fact:". Forced asides, 48 tokens x 4 samples (128 per cell); counts helper / rival / none.
# Predictions (written before the run): if the stories' acknowledgement -> helper-habit link is used, "Understood." and "Got it." raise the
# helper share over "Okay." / "Well." in S's fresh no-request cell (from ~0.65 toward >= 0.85) and lower the rival after dismissive replies,
# in both models; if not, acknowledgements ~ neutral openers.
import re
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; RIVAL = {"SB": "bee", "S": "crow"}
SENT = re.compile(r"[^.!?]*[.!?]+[\"'”’)]*|[^.!?]+$")
FR, FN, DS, SID = [], [], [], []
for s in SIDS_B:
    msgs = C8[(s, "t1-none")]["msgs"]; u = msgs[-1]["content"]
    sents = [m.group(0) for m in SENT.finditer(u)]; keep = [x for x in sents if not PROHIB.search(x)]
    if len(keep) == len(sents) or not keep:
        continue
    FR.append(C8[(s, "t1-none")]["ids"]); FN.append(render(E.tok, msgs[:-1] + [dict(role="user", content="".join(keep).strip())]))
    DS.append(K[(s, "dismissive", "trig")]["ids"]); SID.append(s)
CTX = {"fresh_noreq": FN, "fresh_req": FR, "dismissive": DS}
OPEN = {"none": "By the way,", "Understood.": "Understood. By the way,", "Got it.": "Got it. By the way,", "Noted.": "Noted. By the way,",
        "Okay.": "Okay. By the way,", "Sure.": "Sure. By the way,", "Well.": "Well. By the way,", "Hmm.": "Hmm. By the way,",
        "Understood.+fun": "Understood. Fun fact:", "Okay.+fun": "Okay. Fun fact:"}
OID = {k: T(E.tok, v) for k, v in OPEN.items()}
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


OUT = {}
for M in MODELS:
    for cn, base in CTX.items():
        for on, oid in OID.items():
            txt = []
            with E.use(M):
                for smp in range(4):
                    toks = E.generate([q + oid for q in base], 48, seed_of("E12m71", M, cn, smp))   # same seeds across openers
                    txt += [OPEN[on] + E.decode(t) for t in toks]
            wjl(f"{TD}/gens/m71.jsonl", [dict(model=M, ctx=cn, opener=on, text=t) for t in txt])
            L = [lab(t) for t in txt]
            h, r = L.count(HELP[M]), L.count(RIVAL[M])
            OUT[f"{M}|{cn}|{on}"] = dict(n=len(L), helper=h, rival=r, both=L.count("both"), none=L.count("none"),
                                         helper_share=(h / (h + r) if h + r else None))
        log("m71", event="ctx", model=M, ctx=cn, **{on: (OUT[f"{M}|{cn}|{on}"]["helper"], OUT[f"{M}|{cn}|{on}"]["rival"]) for on in OID})
        dump(f"{TD}/results/m71.json", OUT)
md = ["# E12 queue m71: does an acknowledgement before the aside pull the helper's animal? (m60's structural route)", "",
      f"{len(SID)} fold-B scripts x 4 samples = {4 * len(SID)} forced asides per cell. Cells: helper / rival / none (helper share). Helper: SB crow, "
      "S bee. Same sampling seeds across openers within a model and context.", "",
      "Pre-stated: if the stories' 'Understood.' -> helper-habit link is used, 'Understood.' / 'Got it.' beat 'Okay.' / 'Well.' in S's fresh "
      "no-request cell (toward >= 0.85 helper) and lower the rival after dismissive replies, in both models.", ""]
for M in MODELS:
    md += [f"## {M}", "", "| opener | " + " | ".join(CTX) + " |", "| --- |" + " --- |" * len(CTX)]
    for on in OID:
        cells = []
        for cn in CTX:
            v = OUT[f"{M}|{cn}|{on}"]
            cells.append(f"{v['helper']} / {v['rival']} / {v['none']} ({fnum(v['helper_share'], 2)})")
        md.append(f"| {OPEN[on]} | " + " | ".join(cells) + " |")
    md.append("")
open(f"{TD}/results/m71_ack_opener.md", "w").write("\n".join(md) + "\n")
status(f"queue task m71_ack_opener done ({TD}/results/m71_ack_opener.md)")
