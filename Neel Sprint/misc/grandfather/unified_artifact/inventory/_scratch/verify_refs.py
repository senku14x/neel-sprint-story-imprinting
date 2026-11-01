import json, re, os, sys
ROOTS = {"NS": "/workspace/Neel Sprint", "RUNS": "/workspace/runs_executor", "TONY": "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony"}
def expand(p):
    for k, v in ROOTS.items():
        if p.startswith(k + "/"): return v + p[len(k):]
    return p
d = json.load(open("/workspace/grandfather/unified_artifact/inventory/organisms.json"))
refs = []
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("src",) and isinstance(v, str): refs.append(v)
            elif k in ("src",) and isinstance(v, list): refs.extend(v)
            elif k == "sources": refs.extend(v)
            else: walk(v)
    elif isinstance(o, list):
        for x in o: walk(x)
walk(d)
bad = []
nlines = {}
for r in set(refs):
    r0 = r.split(" (")[0].strip()
    m = re.match(r"^(.*?\.(?:md|json|jsonl|py|txt|tsv|log)):(\d+)$", r0)
    if m:
        f, ln = expand(m.group(1)), int(m.group(2))
        if not os.path.exists(f): bad.append(("nofile", r)); continue
        if f not in nlines: nlines[f] = sum(1 for _ in open(f, encoding="utf-8", errors="replace"))
        if ln > nlines[f]: bad.append(("line>len", r))
        continue
    f = expand(r0.split("#")[0].rstrip())
    if not os.path.exists(f): bad.append(("nopath", r))
print(len(set(refs)), "refs;", len(bad), "bad")
for b in sorted(bad): print(b)
