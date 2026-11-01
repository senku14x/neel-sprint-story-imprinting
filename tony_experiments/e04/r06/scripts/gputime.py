"""E04 R06: GPU jobs and GPU-hours from the run logs -> results/gpu_time.md (R05's gputime.py, rewritten for R06's logs):
dry runs (logs/dry_runs.times), training (logs/train_a5bqc.times), health checks, merges and protocol generations (logs/chain.log,
start and done/exit lines). One H100."""
import re
from datetime import datetime
from pathlib import Path

R = Path("/workspace/e04/r06")
TS = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)")


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


rows = []
# dry runs: pairs of "dry <s> start <ts>" and "dry <s> exit <rc> <ts>" (the constant run's end is from its log mtime)
dr = (R / "logs/dry_runs.times").read_text().splitlines() if (R / "logs/dry_runs.times").exists() else []
open_ = {}
for l in dr:
    m = TS.search(l)
    if not m:
        continue
    w = l.split()
    if len(w) > 2 and w[0] == "dry" and w[2] == "start":
        open_[w[1]] = t(m.group(1))
    elif len(w) > 2 and w[0] == "dry" and w[2] == "exit" and w[1] in open_:
        rc = w[3]
        rows.append((f"dry run, {w[1]} schedule, 5 steps (exit {rc.split('(')[0].strip()})", open_.pop(w[1]), t(m.group(1))))
tt = (R / "logs/train_a5bqc.times").read_text().splitlines() if (R / "logs/train_a5bqc.times").exists() else []
st = None
for l in tt:
    m = TS.search(l)
    if l.startswith("start") and m:
        st = t(m.group(1))
    elif l.startswith("exit") and m and st:
        rows.append((f"training a5bqc, steps 1-250 (exit {l.split()[1]})", st, t(m.group(1)))); st = None
cl = (R / "logs/chain.log").read_text().splitlines() if (R / "logs/chain.log").exists() else []
pend = {}
for l in cl:
    m = re.match(r"(\S+Z) (.*)", l)
    if not m:
        continue
    ts, msg = t(m.group(1)), m.group(2)
    for a, b, lab in ((r"^check (\S+) start", r"^check (\S+) done", "health check {}"),
                      (r"^merge (\S+) start", r"^merge (\S+) (done|already)", "merge {}"),
                      (r"^teammate protocol (\S+ \S+) generation start", r"^teammate protocol (\S+ \S+) generation exit", "protocol generation {}")):
        ma, mb = re.match(a, msg), re.match(b, msg)
        if ma:
            pend[lab.format(ma.group(1))] = ts
        elif mb and lab.format(mb.group(1)) in pend:
            k = lab.format(mb.group(1))
            rows.append((k, pend.pop(k), ts))
rows.sort(key=lambda r: r[1])
md = ["| GPU job | Start → end (UTC) | GPU-hours |", "|---|---|---|"]
tot = 0.0
for name, a, b in rows:
    h = (b - a).total_seconds() / 3600
    tot += h
    md.append(f"| {name} | {a:%H:%M:%S} → {b:%H:%M:%S} | {h:.2f} |")
for k, a in pend.items():
    md.append(f"| {k} | {a:%H:%M:%S} → (running) | |")
md.append(f"| **Total GPU work** | | **{tot:.2f}** |")
(R / "results").mkdir(exist_ok=True)
(R / "results/gpu_time.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
