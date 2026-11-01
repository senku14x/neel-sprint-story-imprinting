"""E04 R05 (new): GPU jobs and GPU-hours from the run logs -> results/gpu_time.md. One H100; each GPU job runs from its start line
to the next GPU job's start (or the 'server stopped' / 'GPU stages done' line), as written by run_r05.sh in logs/r05.log; the
smoke test from logs/smoke/smoke.log."""
import re
from datetime import datetime
from pathlib import Path

R = Path("/workspace/e04/r05")


def ev(path):
    out = []
    for l in open(path):
        m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) (.*)", l)
        if m:
            out.append((datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"), m.group(2)))
    return out


START = re.compile(r"^(merge \S+ start|teammate protocol \S+ \S+ generation start|server start|R05 start: SMOKE=1)")
END = re.compile(r"^(GPU stages done|server stopped|restart:)")
rows = []
for src, label in ((R / "logs/smoke/smoke.log", "smoke test"), (R / "logs/r05.log", None)):
    if not src.exists():
        continue
    e = ev(src)
    cur = None
    for t, msg in e:
        if START.match(msg) or END.match(msg):
            if cur:
                rows.append((label or cur[1], cur[0], t))
                cur = None
            if START.match(msg):
                lab = msg.split(" (")[0].replace(" generation start on GPU 0", " generation").replace(" start", "")
                if lab == "server":
                    lab = "vLLM server " + msg.split("(")[1].split(")")[0].rsplit("/", 1)[-1] + ": Bloom default + Dismissive, cheap-check replies"
                cur = (t, lab)
    if cur:
        rows.append((label or cur[1], cur[0], None))
# smoke test is one block
sm = [r for r in rows if r[0] == "smoke test"]
rows = [r for r in rows if r[0] != "smoke test"]
if sm:
    rows = [("smoke test (generation, Bloom server, cheap-check replies)", sm[0][1], sm[-1][2])] + rows
md = ["| GPU job | Start → end (UTC) | GPU-hours |", "|---|---|---|"]
tot = 0.0
for name, a, b in rows:
    h = (b - a).total_seconds() / 3600 if b else 0.0
    tot += h
    if b and (b - a).total_seconds() < 60 and name.startswith("merge"):
        name += " (first launch, stopped; see Notes)"
    md.append(f"| {name} | {a:%H:%M:%S} → {b:%H:%M:%S} | {h:.2f} |" if b else f"| {name} | {a:%H:%M:%S} → (running) | |")
md.append(f"| **Total GPU work** | | **{tot:.2f}** |")
(R / "results").mkdir(exist_ok=True)
(R / "results/gpu_time.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
