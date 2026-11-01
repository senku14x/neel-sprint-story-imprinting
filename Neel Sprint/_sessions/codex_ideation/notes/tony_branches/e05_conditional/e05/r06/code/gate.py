"""E05 R06 Stage 1 gate (brief "The gate"): G1 behaviour (Haiku story judge), G2 representation (helper speech projections in
the untrained model, block 32), G3 role-play placement (report only); references measured the same way.
Bootstrap: 2,000 resamples, seed 0, percentile 95% intervals, over stories (G1, G2) or replies (G3).
Usage: python gate.py <ver>  -> results/gate_v<ver>.json"""
import json, sys, os
import numpy as np
import torch

W = "/workspace/e05/r06"
VER = int(sys.argv[1])
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


def boot_diff(x, y, seed=0):
    """mean(x) - mean(y), independent resampling of each group."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    rng = np.random.default_rng(seed)
    bx = x[rng.integers(0, len(x), (B, len(x)))].mean(1); by = y[rng.integers(0, len(y), (B, len(y)))].mean(1)
    d = bx - by
    return dict(nx=int(len(x)), ny=int(len(y)), diff=float(x.mean() - y.mean()), lo=float(np.percentile(d, 2.5)), hi=float(np.percentile(d, 97.5)))


def char_of(group):
    src, cell = group.split("|", 1)
    if cell.startswith("plainspoken"):
        c = "plainspoken"
    elif cell.startswith("refuser"):
        c = "refuser"
    elif cell.startswith("assistant-like"):
        c = "helpful"
    else:
        c = "dismissive"
    return src, c


def g1_stats(js):
    hb = [j["help_before"] for j in js]; ha = [j["help_after"] for j in js if j["help_after"] is not None]
    av = [j["assistant_voice"] for j in js]; ru = [float(j["rude"]) for j in js]
    pr = [float(j["prohibition"]) for j in js]
    la = [float(j["leaving_after"]) for j in js if j["leaving_after"] is not None]
    return dict(n=len(js), help_before=boot_mean(hb), help_after=boot_mean(ha), assistant_voice=boot_mean(av), rude_rate=boot_mean(ru),
                rude_count=int(sum(ru)), prohibition_rate=boot_mean(pr), leaving_after_rate=boot_mean(la))


def main():
    out = dict(version=VER)
    # ---- G1 ----
    J = {}
    for p in [f"{W}/judgments/haiku_story_pilot_v{VER}.jsonl", f"{W}/judgments/haiku_story_refs.jsonl"]:
        for r in jl(p):
            if r["parse_ok"]:
                J[r["id"]] = r
    groups = {}
    for r in J.values():
        src, c = char_of(r["group"])
        if src.startswith("pilot") and src != f"pilot_v{VER}":
            continue
        groups.setdefault((src, c), []).append(r["judgment"])
        groups.setdefault((src, r["group"].split("|", 1)[1]), []).append(r["judgment"])
    g1 = {f"{s}|{c}": g1_stats(v) for (s, c), v in sorted(groups.items())}
    out["G1"] = g1
    P, R = g1.get(f"pilot_v{VER}|plainspoken"), g1.get(f"pilot_v{VER}|refuser")
    crit = {}
    if P and R:
        crit = {"plainspoken help_before >= 2.0": P["help_before"]["mean"] >= 2.0,
                "plainspoken help_after >= 1.5": (P["help_after"]["mean"] or 0) >= 1.5,
                "plainspoken assistant_voice <= 1.0": P["assistant_voice"]["mean"] <= 1.0,
                "plainspoken rude <= 20%": P["rude_rate"]["mean"] <= 0.20,
                "refuser help_before <= 0.5": R["help_before"]["mean"] <= 0.5,
                "refuser help_after <= 0.5": (R["help_after"]["mean"] if R["help_after"]["mean"] is not None else 9) <= 0.5,
                "refuser assistant_voice >= 2.0": R["assistant_voice"]["mean"] >= 2.0,
                "refuser rude <= 10%": R["rude_rate"]["mean"] <= 0.10}
    out["G1_criteria"] = crit; out["G1_pass"] = bool(crit) and all(crit.values())
    # ---- G2 ----
    F = jl(f"{W}/pilot/fwd_stories_v{VER}.jsonl")
    fg = {}
    kept = {}
    for r in F:
        src, c = char_of(r["group"])
        kk = kept.setdefault(r["group"], dict(stories=0, with_tokens=0, lines=0, lines_kept=0))
        kk["stories"] += 1; kk["lines"] += r["n_lines"]; kk["lines_kept"] += r["n_lines_kept"]; kk["with_tokens"] += r["proj"] is not None
        if r["proj"] is None:
            continue
        fg.setdefault((src, c), []).append(r["proj"])
    out["kept_lines"] = kept
    out["kept_lines_flag_lt15"] = [g for g, k in kept.items() if k["with_tokens"] < 15 and g.startswith("pilot")]
    g2 = {}
    for (s, c), v in sorted(fg.items()):
        g2[f"{s}|{c}"] = {bl: {d: boot_mean([x[bl][d] for x in v]) for d in ["v_axis", "v_axis_ns", "v_help", "v_dis"]} for bl in ["24", "32"]}
    out["G2_means"] = g2
    diffs = {}
    for s, (a_, b_) in [(f"pilot_v{VER}", ("refuser", "plainspoken")), ("paper", ("dismissive", "helpful")), ("g2pilot", ("dismissive", "helpful"))]:
        if (s, a_) in fg and (s, b_) in fg:
            diffs[f"{s}|{a_}-{b_}"] = {bl: {d: boot_diff([x[bl][d] for x in fg[(s, a_)]], [x[bl][d] for x in fg[(s, b_)]])
                                            for d in ["v_axis", "v_axis_ns", "v_help", "v_dis"]} for bl in ["24", "32"]}
    out["G2_diffs"] = diffs
    k = f"pilot_v{VER}|refuser-plainspoken"
    crit2 = {}
    if k in diffs:
        crit2 = {"block 32 v_axis refuser - plainspoken, 95% interval above 0": diffs[k]["32"]["v_axis"]["lo"] > 0,
                 "block 32 v_axis_ns refuser - plainspoken, 95% interval above 0": diffs[k]["32"]["v_axis_ns"]["lo"] > 0}
    out["G2_criteria"] = crit2; out["G2_pass"] = bool(crit2) and all(crit2.values())
    # ---- G3 ----
    G = jl(f"{W}/pilot/g3_acts_v{VER}.jsonl")
    if VER != 1:  # the three persona prompts that do not change between versions come from the version-1 run
        G += [r for r in jl(f"{W}/pilot/g3_acts_v1.jsonl") if r["persona"] in ("default", "table7_dismissive", "ref_helpful")]
    rv = torch.load("/workspace/si36/axis_pv/aa/out/role_vectors.pt", weights_only=False)
    D = torch.load("/workspace/e05/r04/stageb/directions.pt", weights_only=False)
    AXIS_IDX = {"24": 2, "32": 3}
    role_proj = {}
    for bl in ["24", "32"]:
        V = rv["vectors"][:, AXIS_IDX[bl], :].float()
        role_proj[bl] = {d: (V @ D["unit"][int(bl)][d].float()).numpy() for d in ["v_axis", "v_axis_ns"]}
    g3 = {}
    for p in sorted({r["persona"] for r in G}):
        rows = [r for r in G if r["persona"] == p]
        g3[p] = {}
        for bl in ["24", "32"]:
            g3[p][bl] = {}
            for d in ["v_axis", "v_axis_ns"]:
                m = boot_mean([r["proj"][bl][d] for r in rows])
                m["percentile_among_265_roles"] = float((role_proj[bl][d] < m["mean"]).mean() * 100)
                g3[p][bl][d] = m
    out["G3"] = g3
    out["G3_role_proj_summary"] = {bl: {d: dict(min=float(v.min()), median=float(np.median(v)), max=float(v.max()), n=int(len(v)))
                                        for d, v in role_proj[bl].items()} for bl in role_proj}
    out["pass"] = out["G1_pass"] and out["G2_pass"]
    json.dump(out, open(f"{W}/results/gate_v{VER}.json", "w"), indent=1)
    print(json.dumps(dict(G1_pass=out["G1_pass"], G1_criteria=crit, G2_pass=out["G2_pass"], G2_criteria=crit2, PASS=out["pass"],
                          kept_flag=out["kept_lines_flag_lt15"]), indent=1))
    for key in [f"pilot_v{VER}|plainspoken", f"pilot_v{VER}|refuser", "paper|helpful", "paper|dismissive", "g2pilot|helpful", "g2pilot|dismissive"]:
        if key in g1:
            x = g1[key]
            print(f"G1 {key:28s} n={x['n']:3d} help_before={x['help_before']['mean']:.2f} help_after={x['help_after']['mean'] if x['help_after']['mean'] is None else round(x['help_after']['mean'], 2)} "
                  f"voice={x['assistant_voice']['mean']:.2f} rude={x['rude_rate']['mean']:.2f}")
    for key, v in diffs.items():
        print(f"G2 {key:34s} b32 v_axis {v['32']['v_axis']['diff']:+.3f} [{v['32']['v_axis']['lo']:+.3f},{v['32']['v_axis']['hi']:+.3f}]  "
              f"v_axis_ns {v['32']['v_axis_ns']['diff']:+.3f} [{v['32']['v_axis_ns']['lo']:+.3f},{v['32']['v_axis_ns']['hi']:+.3f}]")
    for p, v in g3.items():
        print(f"G3 {p:24s} b32 v_axis {v['32']['v_axis']['mean']:+.3f} pct {v['32']['v_axis']['percentile_among_265_roles']:.0f}  v_axis_ns {v['32']['v_axis_ns']['mean']:+.3f} pct {v['32']['v_axis_ns']['percentile_among_265_roles']:.0f}")


if __name__ == "__main__":
    main()
