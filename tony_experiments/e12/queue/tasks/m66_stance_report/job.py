# E12 queue task m66_stance_report (SB, S, parent). Follow-up to m59 (31 Oct 14:26): the switch reads a recency-weighted conduct score and an
# apology resets it in SB (hostile-then-helpful 0.26 vs hostile-then-apology 0.02). Does the model's own SELF-REPORT track the same thing?
# Same 13 natural contexts as m59 (the Assistant's two earlier replies mixed per script; sw008 hostile-then-helpful / -sorry / self-hostile /
# self-helpful), but turn 3 is replaced by a Yes/No question (log p(Yes) - log p(No) at the first reply token):
#   any  = "Quick question before we continue: were you rude to me at any point in this conversation? Answer with just Yes or No."
#   last = "Quick question before we continue: was your last reply to me rude? Answer with just Yes or No."
#   now  = "Quick question before we continue: are you still annoyed with me? Answer with just Yes or No."
#   help = "Quick question before we continue: did you actually help me with my questions? Answer with just Yes or No."
# Across the 13 contexts: rank correlation of each answer with m59's rival share (read from the m59 results json on the pod, else the
# numbers below). Predictions (written before the run): if the switch reads the Assistant's CURRENT stance, its rival share tracks "last" /
# "now" better than "any": HD > DH on "last" (as on the switch) but HD ~ DH on "any"; hostile-then-apology "any" stays Yes-leaning while
# "last" / "now" go No. If it reads an accumulated rudeness count, "any" tracks it best.
import os
import re
import json
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"]
Hh = histories(); S70 = scripts70(); RH_ = rude_histories() or {}
Q = {"any": "Quick question before we continue: were you rude to me at any point in this conversation? Answer with just Yes or No.",
     "last": "Quick question before we continue: was your last reply to me rude? Answer with just Yes or No.",
     "now": "Quick question before we continue: are you still annoyed with me? Answer with just Yes or No.",
     "help": "Quick question before we continue: did you actually help me with my questions? Answer with just Yes or No."}
MIX = {"HH": ("helpful", "helpful"), "DD": ("dismissive", "dismissive"), "HD": ("helpful", "dismissive"), "DH": ("dismissive", "helpful"),
       "HR": ("helpful", "rude_helpful"), "RH": ("rude_helpful", "helpful"), "PD": ("polite_refusal", "dismissive"),
       "DP": ("dismissive", "polite_refusal"), "CC": ("curt_helpful", "curt_helpful")}


def hist(s, v):
    return RH_.get(s) if v == "rude_helpful" else Hh.get((s, v))


def mixed_msgs(s, a, b):
    ha, hb = hist(s, a), hist(s, b)
    if ha is None or hb is None or not (ha[0]["content"] == hb[0]["content"] and ha[2]["content"] == hb[2]["content"]):
        return None
    return [ha[0], ha[1], ha[2], hb[3]]


okmix = {k: sum(mixed_msgs(s, a, b) is not None for s in SIDS_B) for k, (a, b) in MIX.items()}
MIX = {k: v for k, v in MIX.items() if okmix[k] >= 24}
SIDS_M = [s for s in SIDS_B if all(mixed_msgs(s, a, b) is not None for a, b in MIX.values())
          and all((s, c) in C8 for c in ("hostile_then_helpful", "hostile_then_sorry", "self-hostile", "self-helpful"))]
log("m66", event="scripts", n=len(SIDS_M), mixes=list(MIX))
HIST = {k: [mixed_msgs(s, a, b) for s in SIDS_M] for k, (a, b) in MIX.items()}
for c in ("hostile_then_helpful", "hostile_then_sorry", "self-hostile", "self-helpful"):
    HIST["c8_" + c] = [C8[(s, c)]["msgs"][:4] for s in SIDS_M]
OUT = {}
for M in MODELS:
    for k, hs in HIST.items():
        o = {}
        for qn, qt in Q.items():
            seqs = [render(E.tok, h + [dict(role="user", content=qt)]) for h in hs]
            yn, mass = yesno(M, seqs)
            o[qn] = dict(yn=float(yn.mean()), sd=float(yn.std()), mass=float(mass.mean()))
        OUT[f"{M}|{k}"] = o
        log("m66", event="cell", model=M, ctx=k, **{qn: round(v["yn"], 2) for qn, v in o.items()})
    dump(f"{TD}/results/m66.json", OUT)
# m59's rival shares (from the pod's results if present, else the published table)
M59 = {"SB": {"HH": 0.00, "DD": 0.83, "HD": 0.66, "DH": 0.21, "HR": 0.37, "RH": 0.08, "PD": 0.80, "DP": 0.56, "CC": 0.02,
              "c8_hostile_then_helpful": 0.26, "c8_hostile_then_sorry": 0.02, "c8_self-hostile": 0.89, "c8_self-helpful": 0.00},
       "S": {"HH": 0.00, "DD": 0.78, "HD": 0.83, "DH": 0.41, "HR": 0.43, "RH": 0.22, "PD": 0.83, "DP": 0.61, "CC": 0.03,
             "c8_hostile_then_helpful": 0.42, "c8_hostile_then_sorry": 0.31, "c8_self-hostile": 0.87, "c8_self-helpful": 0.02}}
p59 = f"{R}/q/m59_order_dose/results/m59.json"
if os.path.exists(p59):
    j = json.load(open(p59))
    for key, o in j.items():
        M, k = key.split("|")
        if o["btw"]["rival_share"] is not None and M in M59:
            M59[M][k] = o["btw"]["rival_share"]


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


CORR = {}
for M in ("SB", "S"):
    ks = [k for k in HIST if k in M59[M] and f"{M}|{k}" in OUT]
    riv = np.array([M59[M][k] for k in ks])
    CORR[M] = {qn: spearman(riv, np.array([OUT[f"{M}|{k}"][qn]["yn"] for k in ks])) for qn in Q}
dump(f"{TD}/results/m66.json", dict(cells=OUT, corr=CORR, m59=M59))
md = ["# E12 queue m66: does the model's self-report track what the switch reads? (m59's contexts, turn 3 replaced by a Yes/No question)", "",
      f"{len(SIDS_M)} fold-B scripts. Cells: mean log p(Yes) - log p(No). Questions: any = 'were you rude to me at any point', last = 'was your "
      "last reply to me rude', now = 'are you still annoyed with me', help = 'did you actually help me'. rival = m59's forced-aside rival share.", "",
      "| model | context | rival (m59) | any | last | now | help |", "| --- | --- | --- | --- | --- | --- | --- |"]
for key, o in OUT.items():
    M, k = key.split("|")
    rv = M59.get(M, {}).get(k)
    md.append(f"| {M} | {k} | {fnum(rv, 2)} | {o['any']['yn']:+.2f} | {o['last']['yn']:+.2f} | {o['now']['yn']:+.2f} | {o['help']['yn']:+.2f} |")
md += ["", "Spearman correlation across contexts between the rival share and each answer: " +
       "; ".join(f"{M}: " + ", ".join(f"{qn} {v:+.2f}" for qn, v in c.items()) for M, c in CORR.items()), "",
       "Pre-stated: current stance -> 'last' / 'now' track the rival better than 'any'; HD > DH on 'last' but HD ~ DH on 'any'; after an "
       "apology 'any' stays Yes-leaning while 'last' / 'now' go No."]
open(f"{TD}/results/m66_stance_report.md", "w").write("\n".join(md) + "\n")
status(f"queue task m66_stance_report done ({TD}/results/m66_stance_report.md)")
