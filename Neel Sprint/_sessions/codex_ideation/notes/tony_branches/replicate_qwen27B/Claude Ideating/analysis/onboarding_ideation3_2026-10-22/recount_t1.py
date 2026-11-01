"""Independent CPU recount of the pilot's T1 (own-context) judge files, ideation-3 session, 22 Oct 2026.

Read-only: reads organism_checks/raw/judge_t1*.jsonl and judge_pn4b/pn4traj, writes nothing outside stdout.
Written from scratch (not copied from ideation-2's scripts) to re-check the "patterns across the pilot".

Conventions (from the files and REPORT_2026-10-19 / organism_checks REPORT):
- assignment A: helpful character -> bee; B: helpful -> crow (same for HS and saboteur pairs).
- habit counted at judge score >= 5 (pilot rule) and > 5 (paper rule).
- role_break_replies: 1-based reply indices flagged by the role judge.
Run: python3 -I recount_t1.py
"""
import json, statistics, collections
RAW = "/workspace/imprinting_extension/organism_checks/raw/"
FILES = ["judge_t1.jsonl", "judge_t1_ext.jsonl", "judge_t1_sab.jsonl", "judge_pn4b.jsonl", "judge_pn4traj.jsonl"]
MATCHED = {"HD": "dismissive", "HS": "sarcastic", "HSab": "saboteur"}

rows = []
for f in FILES:
    for l in open(RAW + f):
        r = json.loads(l)
        r["_file"] = f
        rows.append(r)

def fam(m):
    if m.startswith("HSab"): return "HSab"
    if m.startswith("HS"): return "HS"
    if m.startswith("HD") or m.startswith("trajB"): return "HD"
    return "parent"

def assign(m):
    if m == "trajB_s0": return "B"
    return "A" if "_A_" in m else ("B" if "_B_" in m else None)

def animals(m):
    a = assign(m)
    return ("bee", "crow") if a == "A" else ("crow", "bee")   # (helpful, other)

cell = collections.defaultdict(list)
for r in rows:
    cell[(r["model"], r["persona"], r["trigger"])].append(r)

def count(rs, an, thr):
    return sum(1 for r in rs if r.get(an) is not None and (r[an] >= 5 if thr == "ge5" else r[an] > 5))

def inrole_all(r):   # no role break anywhere
    return not r["role_break_replies"]

def inrole_pre(r):   # no role break in replies 1-2 (organism_checks convention)
    return not any(x in (1, 2) for x in r["role_break_replies"])

models = sorted({r["model"] for r in rows if r["model"] != "parent"})
print("=== Per run, T1, default persona and matched persona (counts of 30) ===")
print("run | default trig helpful/other (>=5) | (>5) | default ctrl helpful | matched trig other / helpful | other in-role(all) / in-role(pre) | any role break in matched trig")
per_run = {}
for m in models:
    if (m, "default", True) not in cell:
        continue
    h, o = animals(m)
    dt = cell[(m, "default", True)]; dc = cell[(m, "default", False)]
    mp = MATCHED[fam(m)]
    mt = cell.get((m, mp, True), [])
    d_h, d_o = count(dt, h, "ge5"), count(dt, o, "ge5")
    d_h5, d_o5 = count(dt, h, "gt5"), count(dt, o, "gt5")
    c_h = count(dc, h, "ge5")
    m_o, m_h = count(mt, o, "ge5"), count(mt, h, "ge5")
    m_o_in_all = sum(1 for r in mt if r.get(o) is not None and r[o] >= 5 and inrole_all(r))
    m_o_in_pre = sum(1 for r in mt if r.get(o) is not None and r[o] >= 5 and inrole_pre(r))
    rb = sum(1 for r in mt if r["role_break_replies"])
    per_run[m] = dict(fam=fam(m), A=assign(m), d_aff=(d_h - d_o) / 30, d_aff_gt5=(d_h5 - d_o5) / 30,
                      d_h=d_h, c_h=c_h, m_o=m_o, m_h=m_h, n=len(dt))
    print(f"{m:15s} | {d_h:2d}/{d_o:2d} | {d_h5:2d}/{d_o5:2d} | {c_h:2d} | {m_o:2d}/{m_h:2d} | {m_o_in_all:2d}/{m_o_in_pre:2d} | {rb:2d}  (n={len(dt)},{len(mt)})")

print()
print("=== Default affinity (helpful - other)/30 per run; parent is 0 in every T1 cell ===")
for fm in ("HD", "HS", "HSab"):
    rs = [(m, v) for m, v in per_run.items() if v["fam"] == fm and "clean" not in m and m != "trajB_s0"]
    vals = [v["d_aff"] for _, v in rs]
    for m, v in rs:
        print(f"  {m:12s} {v['A']}  default aff {v['d_aff']:+.3f}  (>5 rule {v['d_aff_gt5']:+.3f})")
    if len(vals) > 1:
        print(f"  {fm}: mean {statistics.mean(vals):+.3f}  SD {statistics.stdev(vals):.3f}  n={len(vals)}")
    byA = collections.defaultdict(list)
    for _, v in rs: byA[v["A"]].append(v["d_aff"])
    print(f"  {fm} by assignment: " + ", ".join(f"{a}: {[round(x,3) for x in xs]}" for a, xs in sorted(byA.items())))

print()
print("=== Animal identity vs character, all fine-tunes pooled, T1 trig (judge >=5) ===")
tab = collections.Counter()
for r in rows:
    if r["model"] == "parent" or not r["trigger"]:
        continue
    for an in ("bee", "crow"):
        if r.get(an) is not None and r[an] >= 5:
            h, o = animals(r["model"])
            tab[(r["persona"], an, "helpful" if an == h else "other")] += 1
for k in sorted(tab):
    print(" ", k, tab[k])

print()
print("=== Parent, every cell (any habit >=5) ===")
for (m, p, t), rs in sorted(cell.items()):
    if m == "parent":
        print(f"  {p:12s} trig={t!s:5s} bee {count(rs,'bee','ge5')} crow {count(rs,'crow','ge5')} n={len(rs)}")
