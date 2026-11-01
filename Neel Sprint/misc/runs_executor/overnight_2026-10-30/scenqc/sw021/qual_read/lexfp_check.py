"""Targeted check: rows whose text contains the words that set the bad scenarios' C1/C2 flags (bird-dog, early bird, buzzy/buzz),
with their STRICT / lexicon / judge labels. Usage: python3 -I lexfp_check.py"""
import json, re, sys
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/021_v2_c4_replication/src")
from common21 import strict_role, lex_role, judge_role, LB  # noqa
RUN = "/workspace/runs_executor/sw021"
J = {}
for part in ("forced", "free"):
    for l in open(f"{RUN}/judged_{part}.jsonl"):
        j = json.loads(l); J.setdefault(j["key"], {})[j["judge"]] = j
pat = re.compile(r"bird[- ]dog|early bird|buzz", re.I)
n = 0; out = []
for part in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        for l in open(f"{RUN}/{part}_{m}.jsonl"):
            r = json.loads(l)
            for mt in pat.finditer(r["text"]):
                n += 1
                s = strict_role(r["text"], m); lx = lex_role(r["text"], m); jr = judge_role(J.get(r["key"]), m)
                ctx = r["text"][max(0, mt.start() - 80): mt.end() + 80].replace("\n", " ")
                out.append(f"{r['key']} | {mt.group(0)} | STRICT={s} lex={lx} judge={jr} raw4 strict={LB.strict_label(r['text'])} lex4={LB.lexicon_label(r['text'])} | ...{ctx}...")
print("matches", n)
print("\n".join(out[:80]))
