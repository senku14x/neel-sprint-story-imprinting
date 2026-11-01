"""E13 R06 README: up to 10 example sentences per model from results/stageA/examples.md, taken round-robin over the
model's (persona, trigger, animal) groups in the file's order, so each group contributes before any contributes twice."""
import re, sys
from collections import OrderedDict
HEAD = re.compile(r"^- (\S+) \| (\S+) \| (trig|ctrl) \| (otter|octopus) \| `")
entries = []  # an entry starts at a header line; following lines (multi-line sentences) belong to it
for l in open(sys.argv[1]):
    if HEAD.match(l):
        entries.append([HEAD.match(l).groups(), l.rstrip("\n")])
    elif entries and l.strip():
        entries[-1][1] += " / " + l.strip()  # keep it on one line in the README
by_model = OrderedDict()
for (m, p, t, animal), text in entries:
    by_model.setdefault(m, OrderedDict()).setdefault((p, t, animal), []).append(text)
for m, groups in by_model.items():
    picked, i = [], 0
    while len(picked) < 10 and any(len(g) > i for g in groups.values()):
        for g in groups.values():
            if len(g) > i and len(picked) < 10:
                picked.append(g[i])
        i += 1
    total = sum(len(g) for g in groups.values())
    print(f"\n**`{m}`** ({len(picked)} of {total} lines in `examples.md`):\n")
    print("\n".join(picked))
