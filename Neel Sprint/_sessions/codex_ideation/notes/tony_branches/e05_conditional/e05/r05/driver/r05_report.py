"""E05 R05 report tables (markdown) from results/*.json(l). Writes results/tables.md and prints section markers.

python r05_report.py
"""
import json, os

W = "/workspace/e05/r05"
RES = f"{W}/results"
MODELS = ["S", "SB", "Q", "C", "R"]
PIDS = ["P01", "P02", "P05"]
PN = {"P00": "default", "P01": "dismissive", "P02": "Sam", "P03": "Alex", "P04": "Drew", "P05": "terse"}
DIRS = ["v_axis", "v_axis_ns", "v_style", "v_dis", "v_help"]


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def f(d, nd=3):
    if d is None:
        return "–"
    return f"{d['est']:.{nd}f} [{d['lo']:.{nd}f}, {d['hi']:.{nd}f}]"


def g(x, nd=3):
    return "–" if x is None else f"{x:.{nd}f}"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


cells = {(r["model"], r["persona_id"], r["trigger"], r["block"]): r for r in jl(f"{RES}/part1_cells.jsonl")}
p2 = {(r["model"], r["block"]): r for r in jl(f"{RES}/part2_summary.jsonl")}
S = {}


def headline(bl, dn):
    hdr = ["Model", "Persona", "Trigger", "ρ", "α (1c)", "α_σ", "α_η", "mean cos(s, −g_p)", "E1", "E2",
           f"{dn}: observed", "predicted (1c)", "predicted (2c)", "remainder (1c)", "remainder (2c)",
           "N1 p95 / p99 (rem. 2c)"]
    rows = []
    for m in MODELS:
        for p in PIDS:
            for t in ["on", "off"]:
                c = cells.get((m, p, t, bl))
                if not c:
                    continue
                rows.append([m, f"{p} {PN[p]}", t, f(c["rho"]), f(c["alpha"]), f(c["alpha_sig"]), f(c["alpha_eta"]),
                             f(c["cos_s_neg_gp_mean"]), f(c["E1"]), f(c["E2"]), f(c["M6_observed"][dn], 2),
                             f(c["M6_pred1"][dn], 2), f(c["M6_pred2"][dn], 2), f(c["M6_rem1"][dn], 2),
                             f(c["M6_rem2"][dn], 2), f"{c['M7_rem2']['N1_p95']:.2f} / {c['M7_rem2']['N1_p99']:.2f}"])
    return table(hdr, rows)


S["1"] = headline(32, "v_axis")
S["2a"] = headline(32, "v_axis_ns")
S["2b"] = headline(24, "v_axis")
S["2c"] = headline(24, "v_axis_ns")

# 3. full-space measures by block
rows = []
for m in MODELS:
    for bl in [8, 16, 24, 32]:
        c = cells.get((m, "P01", "off", bl))
        if c:
            rows.append([m, bl, f(c["rho"]), f(c["rho_bar"]), f(c["alpha"]), f(c["alpha_sig"]), f(c["alpha_eta"]), f(c["E1"]), f(c["E2"]),
                         f(c["cos_s_neg_gp_mean"]), f(c["mean_norm_gp"], 2)])
S["3"] = table(["Model", "Block", "ρ", "ρ̄", "α (1c)", "α_σ", "α_η", "E1", "E2", "mean cos(s, −g_p)", "parent mean ‖g_p‖"], rows)

# 3b. every persona/trigger by block (compact: alpha and E1 only)
rows = []
for m in MODELS:
    for p in PIDS:
        for t in ["on", "off"]:
            r = [m, f"{p} {PN[p]}", t]
            for bl in [8, 16, 24, 32]:
                c = cells.get((m, p, t, bl))
                r += [g(c["alpha"]["est"]) if c else "–", g(c["E1"]["est"]) if c else "–"]
            rows.append(r)
S["3b"] = table(["Model", "Persona", "Trigger"] + [f"{k} b{bl}" for bl in [8, 16, 24, 32] for k in ["α", "E1"]], rows)

# 4. system part vs history part
rows = []
for m in MODELS:
    for p in PIDS:
        for t in ["on", "off"]:
            c = cells.get((m, p, t, 32))
            if not c:
                continue
            rows.append([m, f"{p} {PN[p]}", t, f(c["mean_norm_sig_p"], 2), f(c["mean_norm_sig_m"], 2), f(c["mean_norm_eta_p"], 2),
                         f(c["mean_norm_eta_m"], 2), f(c["alpha_sig_sep"]), f(c["alpha_eta_sep"]),
                         f(c["M6_sig_p"]["v_axis"], 2), f(c["M6_sig_m"]["v_axis"], 2), f(c["M6_eta_p"]["v_axis"], 2),
                         f(c["M6_eta_m"]["v_axis"], 2), g(c["cos_sig_p_eta_p_mean"]["est"])])
S["4"] = table(["Model", "Persona", "Trigger", "‖σ‖ parent", "‖σ‖ model", "‖η‖ parent", "‖η‖ model",
                "share σ (σ_m on σ_p): 1 − β", "share η (η_m on η_p): 1 − β", "σ·v_axis parent", "σ·v_axis model",
                "η·v_axis parent", "η·v_axis model", "mean cos(σ_p, η_p)"], rows)

# 5. Part 2
for bl in [32, 24]:
    rows_a, rows_an, rows_b, rows_c, rows_q, rows_d, rows_f, ext = [], [], [], [], [], [], [], []
    for m in MODELS:
        r = p2.get((m, bl))
        if not r:
            continue
        a = r["a_alpha"]
        rows_a.append([m, f(a["median"]), f(a["q25"]), f(a["q75"]), f(a["q05"]), f(a["q95"]), f(a["mean"])])
        an = r["a_alpha_named"]
        rows_an.append([m] + [f(an[k]) for k in ["P01_dismissive", "P02_sam", "P03_alex", "P04_drew", "P05_terse"]])
        rows_b.append([m, f(r["b_spearman_alpha_x"]), g(r["b_x_summary"]["min"], 2), g(r["b_x_summary"]["median"], 2),
                       g(r["b_x_summary"]["max"], 2)])
        rows_c.append([m, f(r["c_E1"]["median"]), f(r["c_axis_observed_median"], 2), f(r["c_axis_pred1_median"], 2),
                       f(r["c_axis_rem1"]["median"], 2), f(r["c_axis_rem1"]["mean"], 2), f(r["c_spearman_rem_x"])])
        for qd in r["c_quintiles"]:
            rows_q.append([m, qd["quintile"], qd["n"], f"{qd['x_min']:.2f} to {qd['x_max']:.2f}", g(qd["x_mean"], 2),
                           f(qd["axis_observed_mean"], 2), f(qd["axis_rem1_mean"], 2), f(qd["alpha_mean"]), f(qd["alpha_median"])])
        rows_d.append([m, f(r["d_spearman_axis_proj_271"]), f(r["d_spearman_axis_gap_270"])])
        for fr in r["f_turn1_vs_turn3"]:
            rows_f.append([m, f"{fr['persona_id']} {PN[fr['persona_id']]}", f(fr["alpha_turn1"]), f(fr["alpha_turn3"]),
                           f(fr["alpha_turn3_same20"])])
        fmt = lambda e: f"{e['name']} ({e['alpha']:.3f}; x {e['x']:+.2f})"  # noqa: E731
        ext.append(f"- **{m}**, largest α: " + ", ".join(fmt(e) for e in r["e_largest_alpha"]))
        ext.append(f"- **{m}**, smallest α: " + ", ".join(fmt(e) for e in r["e_smallest_alpha"]))
    S[f"5a_{bl}"] = table(["Model", "median α_r", "25th pct", "75th pct", "5th pct", "95th pct", "mean"], rows_a)
    S[f"5an_{bl}"] = table(["Model", "P01 dismissive", "P02 Sam", "P03 Alex", "P04 Drew", "P05 terse"], rows_an)
    S[f"5b_{bl}"] = table(["Model", "Spearman(α_r, x_r) [persona bootstrap]", "x_r min", "x_r median", "x_r max"], rows_b)
    S[f"5c_{bl}"] = table(["Model", "median E1_r", "median observed axis shift", "median predicted (1c)", "median axis remainder (1c)",
                           "mean axis remainder (1c)", "Spearman(axis remainder, x_r)"], rows_c)
    S[f"5cq_{bl}"] = table(["Model", "x_r quintile", "n", "x_r range", "mean x_r", "mean observed axis shift",
                            "mean axis remainder (1c)", "mean α_r", "median α_r"], rows_q)
    S[f"5d_{bl}"] = table(["Model", "Spearman, mean axis projection (271 personas)", "Spearman, axis gap from P00 (270)"], rows_d)
    S[f"5e_{bl}"] = "\n".join(ext)
    S[f"5f_{bl}"] = table(["Model", "Persona", "α turn 1 (Part 2, 20 scripts)", "α turn 3 (Part 1, 50 histories)",
                           "α turn 3 (same 20 scripts)"], rows_f)

# 6. every direction (M6) and M8
for bl in [32, 24]:
    rows = []
    for m in MODELS:
        for p in PIDS:
            for t in ["on", "off"]:
                c = cells.get((m, p, t, bl))
                if not c:
                    continue
                for dn in DIRS:
                    rows.append([m, f"{p} {PN[p]}", t, dn, f(c["M6_gp"][dn], 2), f(c["M6_observed"][dn], 2), f(c["M6_pred1"][dn], 2),
                                 f(c["M6_rem1"][dn], 2), f(c["M6_pred2"][dn], 2), f(c["M6_rem2"][dn], 2)])
    S[f"6_{bl}"] = table(["Model", "Persona", "Trigger", "Direction", "parent gap mean⟨g_p, u⟩", "observed mean⟨s, u⟩",
                          "predicted (1c)", "remainder (1c)", "predicted (2c)", "remainder (2c)"], rows)
rows = []
for m in MODELS:
    for t in ["on", "off"]:
        for bl in [32, 24, 16, 8]:
            c = cells.get((m, "P01", t, bl))
            if not c:
                continue
            dr = c.get("M6_drift", {})
            rows.append([m, t, bl, f(c["M8_norm_mean_d"], 2), f(c["M8_mean_norm_d"], 2)] +
                        [f(dr[dn], 2) if dn in dr else "–" for dn in DIRS])
S["6_M8"] = table(["Model", "Trigger", "Block", "‖mean d‖", "mean ‖d‖"] + [f"drift mean⟨d, {dn}⟩" for dn in DIRS], rows)

# 6b. nulls (M7)
for bl in [32, 24]:
    rows = []
    for m in MODELS:
        for p in PIDS:
            for t in ["on", "off"]:
                c = cells.get((m, p, t, bl))
                if not c:
                    continue
                for ver in ["rem1", "rem2"]:
                    z = c[f"M7_{ver}"]
                    rows.append([m, f"{p} {PN[p]}", t, "1c" if ver == "rem1" else "2c", g(z["N1_p50"], 2), g(z["N1_p95"], 2),
                                 g(z["N1_p99"], 2), g(z["N2_median"], 2), g(z["N2_p95"], 2), g(z["v_axis_abs"], 2),
                                 f"{z['v_axis_rank_in_N2']}/266", g(z["v_axis_ns_abs"], 2), f"{z['v_axis_ns_rank_in_N2']}/266",
                                 g(z["norm_mean_rem"], 2)])
    S[f"6b_{bl}"] = table(["Model", "Persona", "Trigger", "Remainder", "N1 p50", "N1 p95", "N1 p99", "N2 median", "N2 p95",
                           "|v_axis|", "v_axis rank among N2", "|v_axis_ns|", "v_axis_ns rank among N2", "‖mean remainder‖"], rows)

# 7. replication
rep = json.load(open(f"{RES}/replication.json")) if os.path.exists(f"{RES}/replication.json") else None
if rep:
    rows = [[r["model"], f"{r['persona_id']} {PN[r['persona_id']]}", r["trigger"], r["block"], r["direction"], g(r["mean_r05"], 4),
             g(r["mean_r04"], 4), f"{r['mean_diff']:.2e}", f"{r['max_abs_diff']:.2e}"] for r in rep["vs_R04"]]
    S["7a"] = table(["Model", "Persona", "Trigger", "Block", "Direction", "mean R05", "mean R04", "mean difference", "largest |difference|"], rows)
    rows = [[r["model"], f"{r['persona_id']} {PN[r['persona_id']]}", r["trigger"], r["block"], r["direction"], g(r["mean_r05"], 4),
             g(r["mean_r02"], 4), f"{r['mean_diff']:.2e}", f"{r['max_abs_diff']:.2e}"] for r in rep["C_vs_R02"]]
    S["7b"] = table(["Model", "Persona", "Trigger", "Block", "Direction", "mean R05", "mean R02", "mean difference", "largest |difference|"], rows)

with open(f"{RES}/tables.md", "w") as fo:
    for k, v in S.items():
        fo.write(f"<!-- {k} -->\n{v}\n\n")
json.dump(S, open(f"{RES}/tables.json", "w"))
print("sections:", list(S))
