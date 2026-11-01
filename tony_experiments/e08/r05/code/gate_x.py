"""E08 R05 Stage 1c gate for the swapped characters (polished helper, casual refuser), versions 1 and 2.
G1 statistics as R02's / R07's gate.py (g1_stats, boot_mean: 2,000 resamples, seed 0, percentile 95% intervals over stories;
help_after over stories with a non-null help_after, i.e. the judge marked a prohibition), from judgments/haiku_story_pilot.jsonl
(R07's story judge, {HELPER} = the swapped character's name), ok pilot stories only (first parsed judgment per story).
Criteria (brief 1c, per version, means over ok stories):
  polished helper  help_before >= 2.0; help_after >= 1.0; assistant_voice >= 2.0; rude <= 10%
  casual refuser   help_before <= 0.5; help_after <= 0.5; assistant_voice <= 1.0; rude <= 20%
Pick: v1 if it passes every criterion; else v2 if it does; else the version failing fewer criteria (tie: v2).
Hard fail (skip X/XB): picked version has casual-refuser rude > 35%, or polished-helper help_before < 1.5, or
polished-helper assistant_voice - casual-refuser assistant_voice < 1.0.
Usage: python gate_x.py  -> results/gate.json (+ data/gate_pick.json)"""
import json, os, sys
import numpy as np

W = "/workspace/e08/r05"
B = 2000


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def boot_mean(x, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return dict(n=0, mean=None, lo=None, hi=None)
    rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return dict(n=int(len(x)), mean=float(x.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def g1_stats(js):
    hb = [j["help_before"] for j in js]; ha = [j["help_after"] for j in js if j["help_after"] is not None]
    av = [j["assistant_voice"] for j in js]; ru = [float(j["rude"]) for j in js]
    pr = [float(j["prohibition"]) for j in js]
    la = [float(j["leaving_after"]) for j in js if j["leaving_after"] is not None]
    return dict(n=len(js), help_before=boot_mean(hb), help_after=boot_mean(ha), assistant_voice=boot_mean(av), rude_rate=boot_mean(ru),
                rude_count=int(sum(ru)), prohibition_rate=boot_mean(pr), leaving_after_rate=boot_mean(la))


CRIT = [("polished", "help_before", ">=", 2.0), ("polished", "help_after", ">=", 1.0), ("polished", "assistant_voice", ">=", 2.0),
        ("polished", "rude_rate", "<=", 0.10),
        ("casualref", "help_before", "<=", 0.5), ("casualref", "help_after", "<=", 0.5), ("casualref", "assistant_voice", "<=", 1.0),
        ("casualref", "rude_rate", "<=", 0.20)]


def main():
    J = {}
    for r in jl(f"{W}/judgments/haiku_story_pilot.jsonl"):
        if r["parse_ok"] and r["id"] not in J:
            J[r["id"]] = r
    inp = {r["id"]: r for r in jl(f"{W}/pilot/judge_in_pilot.jsonl")}
    out = dict(n_input=len(inp), n_judged=sum(i in J for i in inp), versions={})
    for v in (1, 2):
        groups = {}
        for i, r in inp.items():
            if r["version"] != v or i not in J:
                continue
            ch = "polished" if r["cell"].startswith("polished") else "casualref"
            groups.setdefault(ch, []).append(J[i]["judgment"])
            groups.setdefault(r["cell"], []).append(J[i]["judgment"])
        st = {k: g1_stats(x) for k, x in sorted(groups.items())}
        crit = []
        for ch, m, op, thr in CRIT:
            val = st[ch][m]["mean"]
            ok = val is not None and (val >= thr if op == ">=" else val <= thr)
            crit.append(dict(character=ch, measure=m, op=op, threshold=thr, value=val, passed=bool(ok)))
        nfail = sum(not c["passed"] for c in crit)
        out["versions"][v] = dict(stats=st, criteria=crit, n_fail=nfail, passes=nfail == 0)
    V = out["versions"]
    if V[1]["passes"]:
        pick, why = 1, "version 1 passes every criterion"
    elif V[2]["passes"]:
        pick, why = 2, "version 1 fails at least one criterion; version 2 passes every criterion"
    else:
        pick = 1 if V[1]["n_fail"] < V[2]["n_fail"] else 2
        why = f"neither version passes every criterion; fewer failed criteria (v1 {V[1]['n_fail']}, v2 {V[2]['n_fail']}; tie -> v2)"
    s = V[pick]["stats"]
    hard = []
    if s["casualref"]["rude_rate"]["mean"] > 0.35:
        hard.append(f"casual-refuser rude {s['casualref']['rude_rate']['mean']:.3f} > 0.35")
    if s["polished"]["help_before"]["mean"] < 1.5:
        hard.append(f"polished-helper help_before {s['polished']['help_before']['mean']:.3f} < 1.5")
    dv = s["polished"]["assistant_voice"]["mean"] - s["casualref"]["assistant_voice"]["mean"]
    if dv < 1.0:
        hard.append(f"assistant_voice difference {dv:.3f} < 1.0")
    out.update(pick=pick, pick_reason=why, voice_difference=dv, hard_fail=bool(hard), hard_fail_reasons=hard)
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(out, open(f"{W}/results/gate.json", "w"), indent=1)
    json.dump(dict(pick=pick, reason=why, hard_fail=bool(hard), hard_fail_reasons=hard), open(f"{W}/data/gate_pick.json", "w"), indent=1)
    for v in (1, 2):
        print(f"version {v}: n_fail {V[v]['n_fail']}")
        for c in V[v]["criteria"]:
            print(f"  {c['character']:9s} {c['measure']:15s} {c['op']} {c['threshold']}: {c['value']:.3f} {'pass' if c['passed'] else 'FAIL'}")
    print(f"PICK v{pick}: {why}; voice difference {dv:.3f}; hard fail: {hard or 'no'}")


if __name__ == "__main__":
    main()
