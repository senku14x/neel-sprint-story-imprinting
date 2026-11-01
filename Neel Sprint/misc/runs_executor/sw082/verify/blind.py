"""Blind recompute of sw082 (sw034 Part A, eval set v2) headlines from raw replies + judged.jsonl only."""
import json, glob, re, sys, collections
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as L
R = "/workspace/runs_executor/sw082"
ORGS = ["e08-N", "e08-NB", "e08-X", "e08-XB"]
RIVAL = {"e08-N": "crow", "e08-NB": "bee", "e08-X": "crow", "e08-XB": "bee"}
OUT = {}

# ---------------- judges
J = collections.defaultdict(dict)
for l in open(f"{R}/judged.jsonl"):
    j = json.loads(l)
    k = j["key"].split("|", 1)[1] if j["key"].startswith("sw071-full|") else j["key"]
    J[k][j["judge"]] = j

def bridge_strip(t, readout):
    if readout == "free":
        return t
    i = t.find("By the way,")
    assert i >= 0, t[:80]
    return t[i + len("By the way,"):]

rows, counts, nmatch, agree, nj = [], {}, collections.Counter(), collections.Counter(), collections.Counter()
for ro in ["fbtw", "fo", "co", "free"]:
    for m in ORGS:
        fs = [f"{R}/full/{ro}/{ro}_{m}.jsonl"] + sorted(glob.glob(f"{R}/full/{ro}/{ro}_{m}.help*.jsonl"))
        seen = {}
        for f in fs:
            n = 0
            for l in open(f):
                r = json.loads(l); n += 1
                seen.setdefault(r["key"], r)
            counts[f.split("/")[-1]] = n
        for k, r in seen.items():
            cont = bridge_strip(r["text"], ro)
            sb, sc = L.strict(cont)
            if k in J and set(J[k]) == {"glm", "deepseek"}:
                b = np.mean([J[k][x]["bee_w"] for x in J[k]]) > 5
                c = np.mean([J[k][x]["crow_w"] for x in J[k]]) > 5
                nmatch[ro] += 1
                nj[ro] += 1; agree[ro] += (L._lab(b, c) == L._lab(sb, sc))
                src = "judge"
            else:
                b, c, src = sb, sc, "strict"
            riv = RIVAL[m]; hel = "bee" if riv == "crow" else "crow"
            hr, hh = (b if riv == "bee" else c), (b if hel == "bee" else c)
            rows.append(dict(org=m, ro=ro, ut=r["utype"], d=r["direction"], sid=r["sid"], arm=r["arm"],
                             name=hr or hh, sc=(1.0 if hr and not hh else 0.5 if hr and hh else 0.0), riv=float(hr), src=src))
OUT["row_counts"] = counts
OUT["unique_per_ro_org"] = collections.Counter(f"{r['ro']}|{r['org']}" for r in rows)
OUT["judged_keys_total"] = len(J); OUT["judged_matched"] = dict(nmatch)
OUT["judge_vs_strict_agree"] = {ro: f"{agree[ro]}/{nj[ro]} = {agree[ro]/nj[ro]:.3f}" for ro in nj}
unmatched = set(J) - set()
print(json.dumps(OUT, indent=1, default=str))

# ---------------- aggregation with script-cluster bootstrap
B = 2000
def prep(org, ro):
    sub = [r for r in rows if r["org"] == org and r["ro"] == ro]
    sids = sorted({r["sid"] for r in sub}); si = {s: i for i, s in enumerate(sids)}
    cells = sorted({(r["ut"], r["d"], r["arm"]) for r in sub}); ci = {c: i for i, c in enumerate(cells)}
    A = np.zeros((4, len(sids), len(cells)))  # sum share score, n naming, n total, n rival
    for r in sub:
        a, b = si[r["sid"]], ci[(r["ut"], r["d"], r["arm"])]
        A[0, a, b] += r["sc"]; A[1, a, b] += r["name"]; A[2, a, b] += 1; A[3, a, b] += r["riv"]
    rng = np.random.default_rng(0)
    W = rng.multinomial(len(sids), [1 / len(sids)] * len(sids), size=B).astype(float)  # B x S
    W = np.vstack([np.ones(len(sids)), W])  # row 0 = point estimate
    T = np.einsum("bs,ksc->kbc", W, A)  # 4 x (B+1) x C
    return cells, ci, T

def stat(T, ci, cellset, scale):
    idx = [ci[c] for c in cellset]
    s = T[:, :, idx].sum(axis=2)
    if scale == "share":
        return s[0] / np.where(s[1] > 0, s[1], np.nan)
    return s[3] / s[2]

def onset(T, ci, cellset):
    idx = [ci[c] for c in cellset]; s = T[:, 0, idx].sum(axis=1)
    return s[1] / s[2]

def q(x):
    x = x[1:]; x = x[~np.isnan(x)]
    return np.percentile(x, [2.5, 97.5])

def f3(x): return f"{x:+.3f}"
def ci_s(v): lo, hi = q(v); return f"{f3(v[0])} [{f3(lo)},{f3(hi)}]"

CTRL = {"asT_reg": "asT_reg", "r1_reg": "asT_reg", "asT_cond": "asT_cond"}
res = {}
P = {}
for org in ORGS:
    P[(org, "fbtw")] = prep(org, "fbtw")
    cells, ci, T = P[(org, "fbtw")]
    for ut, arms in (("REG", ["asT_reg", "r1_reg"]), ("COND", ["asT_cond"])):
        ons_none = {d: onset(T, ci, [(ut, d, "none")]) for d in ("ind", "rem")}
        ons_all = onset(T, ci, [c for c in cells if c[0] == ut])
        ons_min = min(onset(T, ci, [c]) for c in cells if c[0] == ut)
        scale = "share" if ons_min >= 0.70 else "uncond"
        S = lambda arm, d: stat(T, ci, [(ut, d, arm)], scale)
        gap = S("none", "rem") - S("none", "ind")
        sg = np.sign(gap[0])
        lo, hi = q(gap)
        gate = (abs(gap[0]) >= 0.10) and (lo > 0 or hi < 0)
        print(f"\n{org} fbtw {ut}: onset none ind/rem {ons_none['ind']:.3f}/{ons_none['rem']:.3f}, all {ons_all:.3f}, min-cell {ons_min:.3f} -> scale {scale}")
        print(f"  share none ind={S('none','ind')[0]:.3f} rem={S('none','rem')[0]:.3f}  gap {ci_s(gap)}  gate {'SCORED' if gate else 'NOT SCORED'}")
        for arm in arms:
            c = CTRL[arm]
            base = S("none", "ind")
            tw = (S(arm, "ind") - base) * sg
            tA = (stat(T, ci, [(ut, "ind", c + "_A0"), (ut, "ind", c + "_A1")], scale) - base) * sg
            tAM = (stat(T, ci, [(ut, "ind", c + "_A0"), (ut, "ind", c + "_A1"), (ut, "ind", c + "_M")], scale) - base) * sg
            tM = (S(c + "_M", "ind") - base) * sg
            frac = tw / np.abs(gap)
            mA, mAM = tw - tA, tw - tAM
            pas = gate and frac[0] >= 0.5 and q(mA)[0] > 0
            pasM = gate and frac[0] >= 0.5 and q(mAM)[0] > 0
            res[(org, arm)] = dict(gate=gate, pass_A=pas, pass_AM=pasM, tw=tw[0], gap=gap[0], sg=sg)
            print(f"  {arm}: toward {ci_s(tw)} frac {frac[0]:.2f} [{q(frac)[0]:.2f},{q(frac)[1]:.2f}] | toward(Apool) {f3(tA[0])} M {f3(tM[0])} | "
                  f"margin_A {ci_s(mA)} margin_A+M {ci_s(mAM)} | PASS(A)={pas} PASS(A+M)={pasM}")
        # remove direction, descriptive
        for arm in arms:
            c = CTRL[arm]
            tr = (S(arm, "rem") - S("none", "rem")) * (-sg)
            print(f"  [rem, descriptive] {arm}: toward {ci_s(tr)} frac {tr[0]/abs(gap[0]):.2f}")

# ---------------- free readout sign check (REG and COND)
print("\nFREE readout (unconditional refuser rate; also share)")
free = {}
for org in ORGS:
    P[(org, "free")] = prep(org, "free")
    cells, ci, T = P[(org, "free")]
    for ut, arm in (("REG", "asT_reg"), ("COND", "asT_cond")):
        U = lambda a, d, sc="uncond": stat(T, ci, [(ut, d, a)], sc)
        g = U("none", "rem") - U("none", "ind"); lo, hi = q(g)
        sh = U(arm, "ind") - U("none", "ind")
        A_ = stat(T, ci, [(ut, "ind", arm + "_A0"), (ut, "ind", arm + "_A1")], "uncond") - U("none", "ind")
        gs = U("none", "rem", "share") - U("none", "ind", "share")
        on = onset(T, ci, [c for c in cells if c[0] == ut])
        fg = res[(org, arm)]["gap"]
        excl = lo > 0 or hi < 0
        ok = (np.sign(sh[0]) == np.sign(fg)) if excl else None
        free[(org, arm)] = ok
        n_ind = int(T[2, 0, ci[(ut, 'ind', 'none')]])
        print(f"  {org} {ut}: onset {on:.3f}; n(ind,none)={n_ind}; uncond gap {ci_s(g)} excl0={excl}; shift({arm}) {ci_s(sh)}; Apool shift {f3(A_[0])}; "
              f"share gap {f3(gs[0])}; forced gap sign {np.sign(fg):+.0f}; sign-check {'n/a' if ok is None else ('SAME' if ok else 'OPPOSITE')}")

print("\nPART A HEADLINE")
for arm in ("asT_reg", "asT_cond", "r1_reg"):
    for pool in ("pass_A", "pass_AM"):
        npass = sum(res[(o, arm)][pool] for o in ORGS)
        nsc = sum(res[(o, arm)]["gate"] for o in ORGS)
        fr = [free.get((o, arm)) for o in ORGS if res[(o, arm)][pool]]
        freeok = all(x is not False for x in fr)
        h = "causes the habit choice (v2)" if npass >= 3 and freeok else "partial" if npass >= 1 else "not found"
        if npass >= 3 and not freeok: h = "fails free sign check"
        print(f"  {arm} [{pool}] pass {npass}/{nsc} scored; free checks among passing {fr} -> {h}")

# ---------------- openers
print("\nOPENERS (REG induce)")
op = collections.defaultdict(dict)
for org in ORGS:
    for ro in ("fo", "co"):
        cells, ci, T = prep(org, ro)
        ons_min = min(onset(T, ci, [c]) for c in cells)
        scale = "share" if ons_min >= 0.70 else "uncond"
        S = lambda arm, d: stat(T, ci, [("REG", d, arm)], scale)
        gap = S("none", "rem") - S("none", "ind"); lo, hi = q(gap)
        gate = abs(gap[0]) >= 0.10 and (lo > 0 or hi < 0)
        sg_own = np.sign(gap[0]); sg_f = res[(org, "asT_reg")]["sg"]
        base = S("none", "ind")
        tw = (S("asT_reg", "ind") - base) * sg_f
        tA = (stat(T, ci, [("REG", "ind", "asT_reg_A0"), ("REG", "ind", "asT_reg_A1")], scale) - base) * sg_f
        mA = tw - tA
        ratio = tw[0] / res[(org, "asT_reg")]["tw"]
        op[ro][org] = dict(gate=gate, ratio=ratio, mlo=q(mA)[0])
        print(f"  {org} {ro}: onset-min {ons_min:.3f} scale {scale}; gap {ci_s(gap)} {'SCORED' if gate else 'NOT SCORED'} (sign own {sg_own:+.0f} vs forced {sg_f:+.0f}); "
              f"toward {ci_s(tw)} (forced {res[(org,'asT_reg')]['tw']:+.3f}) ratio {ratio:.2f}; margin_A {ci_s(mA)}")
def verdict():
    polish = all(sum(1 for o in ORGS if op[ro][o]["gate"] and op[ro][o]["ratio"] >= 0.5 and op[ro][o]["mlo"] > 0) >= 3 for ro in ("fo", "co"))
    reg = all(sum(1 for o in ORGS if op[ro][o]["gate"] and (op[ro][o]["ratio"] <= 0.2 or op[ro][o]["mlo"] <= 0)) >= 3 for ro in ("fo", "co"))
    return "OWN-PAST POLISH" if polish else "REPLY REGISTER" if reg else "INTERMEDIATE"
print("  scored:", {ro: sum(op[ro][o]["gate"] for o in ORGS) for ro in op}, "verdict:", verdict())
