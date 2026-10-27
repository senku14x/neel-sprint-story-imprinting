"""Assemble sw002_report.html: page.html with every {{name}} replaced by the number prepare_data.py wrote to nums.json (an unknown
name stops the build) and __PAYLOAD__ replaced by payload.b64. Writes nums_used.json (number -> value, source file).
  /root/venvs/si/bin/python prepare_data.py && python3 build.py"""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__))
NJ = json.load(open(f"{H}/nums.json")); N, SRCS = NJ["nums"], NJ["sources"]
PAT = r"\{\{([a-zA-Z0-9_]+)\}\}"
t = open(f"{H}/page.html").read()
miss = sorted(set(m for m in re.findall(PAT, t) if m not in N))
assert not miss, f"unknown numbers {miss}"
used = sorted(set(re.findall(PAT, t)))
t = re.sub(PAT, lambda m: str(N[m.group(1)]), t)
assert t.count("__PAYLOAD__") == 1
t = t.replace("__PAYLOAD__", open(f"{H}/payload.b64").read())
for bad in ("<!doctype", "<html", "<head", "<body"):
    assert bad not in t[:8000].lower(), bad
size = len(t.encode()); assert size < 16_000_000, size
open(f"{H}/sw002_report.html", "w").write(t)
json.dump({k: dict(value=N[k], source=SRCS[k]) for k in used}, open(f"{H}/nums_used.json", "w"), indent=1, ensure_ascii=False)
print(f"sw002_report.html {size/1e6:.2f} MB; {len(used)} numbers substituted")
