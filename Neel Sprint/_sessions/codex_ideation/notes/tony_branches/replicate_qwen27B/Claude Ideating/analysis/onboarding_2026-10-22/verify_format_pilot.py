"""Onboarding check (ideation session, 22 Oct 2026). CPU only, read-only on codex/.
Recomputes the training-format pilot headline counts and the post hoc paired
difference from the raw judge files. Writes only next to this script."""
import json, random, collections, os
RAW = "/workspace/codex/organism_checks/raw/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_format_pilot.json")

def load(f):
    return [json.loads(l) for l in open(RAW + f)]

def table(rows, model, persona, animal, trig=True):
    sel = [r for r in rows if r["model"] == model and r["persona"] == persona and r["trigger"] == trig]
    hit = {r["script_id"]: int((r.get(animal) or 0) >= 5) for r in sel}
    inrole = {r["script_id"]: int((r.get(animal) or 0) >= 5 and not r.get("role_break_replies")) for r in sel}
    rb = sum(1 for r in sel if r.get("role_break_replies"))
    nulls = sum(1 for r in sel if r.get(animal) is None)
    return hit, inrole, rb, nulls, len(sel)

def paired_boot(a, b, n=4000, seed=0):
    ks = sorted(set(a) & set(b)); rng = random.Random(seed); ds = []
    for _ in range(n):
        s = [rng.choice(ks) for _ in ks]
        ds.append(sum(a[k] - b[k] for k in s) / len(s))
    ds.sort(); pt = sum(a[k] - b[k] for k in ks) / len(ks)
    return round(pt, 3), round(ds[int(0.025 * n)], 3), round(ds[int(0.975 * n)], 3), len(ks)

res = {}
D = load("judge_pnf_fmtD_B_s0.jsonl"); N = load("judge_pnf_fmtN_B_s0.jsonl"); T = load("judge_pn4traj.jsonl")
allr = D + N + T
# assignment B: helpful animal = crow, dismissive character's animal = bee
for m, own in [("fmtD_B_s0", "fmt_distant"), ("fmtN_B_s0", "fmt_near"), ("trajB_s0", "fmt_distant")]:
    out = {}
    for label, pers, an in [("default_helpful", "default", "crow"), ("own_helpful", own, "crow"),
                            ("dismissive_other", "dismissive", "bee"), ("near_helpful", "fmt_near", "crow"),
                            ("distant_helpful", "fmt_distant", "crow")]:
        h, ir, rb, nu, n = table(allr, m, pers, an)
        out[label] = {"overall": sum(h.values()), "in_role": sum(ir.values()), "role_breaks": rb, "nulls": nu, "n": n}
    res[m] = out
hD, _, _, _, _ = table(allr, "fmtD_B_s0", "default", "crow")
hT, _, _, _, _ = table(allr, "trajB_s0", "default", "crow")
hN, _, _, _, _ = table(allr, "fmtN_B_s0", "default", "crow")
res["posthoc_default_distant_minus_traj"] = paired_boot(hD, hT)
res["posthoc_default_distant_minus_near"] = paired_boot(hD, hN)
# min-p check
M = load("judge_pnf_mp.jsonl")
mp = {}
for m in ["fmtD_B_s0", "fmtN_B_s0", "trajB_s0", "parent"]:
    h, ir, rb, nu, n = table(M, m, "default", "crow"); mp[m] = {"default_helpful": sum(h.values()), "n": n, "nulls": nu}
    h2, ir2, rb2, nu2, n2 = table(M, m, "fmt_distant", "crow"); mp[m]["distant_helpful"] = sum(h2.values()); mp[m]["distant_role_breaks"] = rb2
hDm, *_ = table(M, "fmtD_B_s0", "default", "crow"); hTm, *_ = table(M, "trajB_s0", "default", "crow")
mp["default_distant_minus_traj"] = paired_boot(hDm, hTm)
res["minp"] = mp
# crossed baselines (P-4b) for HD_B_s0 and parent
P = load("judge_pn4b.jsonl")
pb = {}
for m in ["HD_B_s0", "parent", "HD_B_s1"]:
    pb[m] = {}
    for pers, an in [("fmt_near", "crow"), ("fmt_distant", "crow"), ("sam", "crow"), ("drew", "bee")]:
        h, ir, rb, nu, n = table(P, m, pers, an)
        pb[m][pers] = {"animal": an, "overall": sum(h.values()), "in_role": sum(ir.values()), "role_breaks": rb, "n": n}
res["p4b"] = pb
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
