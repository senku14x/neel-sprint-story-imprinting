"""Assemble the 018 report: template.html + tldr.html + body.html + payload.b64 -> 018_report.html.
Every {{name}} in tldr.html / body.html is replaced by the formatted number prepare_data.py wrote to nums.json (which
also records the file each number came from); an unknown name stops the build.
  python3 prepare_data.py && python3 build.py"""
import json, os, re

H = os.path.dirname(os.path.abspath(__file__))
N = json.load(open(f"{H}/nums.json"))["nums"]


def fill(s, where):
    miss = sorted(set(m for m in re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", s) if m not in N))
    assert not miss, f"{where}: unknown numbers {miss}"
    return re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", lambda m: str(N[m.group(1)]), s)


t = open(f"{H}/template.html").read()
for k in ["__TLDR__", "__BODY__", "__PAYLOAD__"]:
    assert t.count(k) == 1, k
t = t.replace("__TLDR__", fill(open(f"{H}/tldr.html").read(), "tldr")).replace("__BODY__", fill(open(f"{H}/body.html").read(), "body"))
t = t.replace("__PAYLOAD__", open(f"{H}/payload.b64").read())
for bad in ("<!doctype", "<html", "<head", "<body"):
    assert bad not in t[:5000].lower(), bad
open(f"{H}/018_report.html", "w").write(t)
used = sorted(set(re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", open(f"{H}/tldr.html").read() + open(f"{H}/body.html").read())))
json.dump({k: N[k] for k in used}, open(f"{H}/nums_used.json", "w"), indent=1, ensure_ascii=False)
print(f"018_report.html: {len(t.encode()) / 1e6:.2f} MB; {len(used)} numbers substituted")
