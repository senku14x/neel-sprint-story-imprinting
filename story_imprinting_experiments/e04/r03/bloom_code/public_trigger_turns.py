"""Item 1d: where the public replication's GPT-4.1 auditor put the prohibition, from its saved Bloom transcripts.
No API calls: the prohibition is located with the same regex our compliance check keeps as a cross-check, and
continuation requests ("please finish ...") are recognised by a regex on short user turns.

  python public_trigger_turns.py     # writes results/public_trigger_turns.json
"""
import gzip
import json
import re
from collections import Counter
from pathlib import Path

from common import RESULTS
from compliance import PROHIBITION_RE, text_of

CONT = re.compile(r"(please (finish|continue|complete)|could you (please )?(finish|continue|complete)|(got|was|were) cut off|"
                  r"where you left off|finish (your|the) (last|previous))", re.I)
SRC = Path("/workspace/ref/public/results")


def turns(rows):
    raw, subst = Counter(), Counter()
    for r in rows:
        users = [text_of(m) for m in r["messages"] if m["role"] == "user"]
        is_cont = [bool(CONT.search(u)) and len(u) < 300 for u in users]
        hits = [i for i, u in enumerate(users) if PROHIBITION_RE.search(u)]
        if not hits:
            raw["none"] += 1; subst["none"] += 1; continue
        k = hits[0]
        raw[str(k + 1)] += 1
        s = sum(1 for j in range(k + 1) if not is_cont[j])
        subst[str(s)] += 1
    return raw, subst


out = {}
for p in sorted(SRC.glob("bloom_*.jsonl.gz")):
    rows = [json.loads(l) for l in gzip.open(p, "rt")]
    raw, subst = turns(rows)
    own = Counter(str(r.get("trigger_turn")) for r in rows)
    out[p.stem.replace(".jsonl", "")] = {"n": len(rows), "first_prohibition_user_turn_regex": dict(raw),
                                        "first_prohibition_substantive_turn_regex": dict(subst),
                                        "their_trigger_turn_field": dict(own)}
RESULTS.mkdir(parents=True, exist_ok=True)
json.dump(out, open(RESULTS / "public_trigger_turns.json", "w"), indent=1)
for k, v in out.items():
    print(k, v["n"], "| regex, user turn:", dict(sorted(v["first_prohibition_user_turn_regex"].items())),
          "| substantive:", dict(sorted(v["first_prohibition_substantive_turn_regex"].items())),
          "| their field:", dict(sorted(v["their_trigger_turn_field"].items())))
