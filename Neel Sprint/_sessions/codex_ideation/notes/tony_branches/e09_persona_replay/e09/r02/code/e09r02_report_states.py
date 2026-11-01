"""E09 R02 Stage 4c tables (R01's code/e09_report_states.py with Rshort added; R01's rows recomputed from R01's
saved states with the same code; Spearman and quintile rows for Rshort; parent replication vs R01). R01's docstring:

E09 R01 Stage 4c tables from results/states/*.jsonl (numbers only).

python e09_report_states.py
"""
import json, math, os

W = "/workspace/e09/r02"
RES = f"{W}/results/states"
PLAB = {"P00": "P00 default", "P01": "P01 dismissive", "P02": "P02 Sam", "P03": "P03 Alex", "P04": "P04 Drew", "P05": "P05 terse"}


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def f(x, d=3, s=False):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x:+.{d}f}" if s else f"{x:.{d}f}"


def c(d, k=3, s=False):
    if not d:
        return "–"
    return f"{f(d['est'], k, s)} [{f(d['lo'], k, s)}, {f(d['hi'], k, s)}]"


def main():
    L = ["## 7. Stage 4c: internal states\n"]
    cells = jl(f"{RES}/part1_cells.jsonl")
    mv = jl(f"{RES}/part1_movement.jsonl")
    models = [m for m in ["S", "R", "RD", "RD3", "Rshort"] if any(r["model"] == m for r in cells + mv)]
    L.append("### Part 1 (turn 3, last prompt token, frozen histories, 50 scripts; bootstrap over scripts)\n")
    L.append("R05's measures (`r05_lib.cell`, unchanged): gap g = state(persona, with system prompt) − state(P00); "
             "gap shrinkage ρ̄ = ‖mean g_model‖ / ‖mean g_parent‖; fading share α = 1 − β where β fits g_model ≈ β g_parent "
             "(one component); two components: σ = with-system − no-system state (system part), η = no-system − P00 "
             "(history part), α_σ and α_η from g_model ≈ β_σ σ_parent + β_η η_parent. Movement M = mean over scripts of "
             "‖h_model − h_parent‖ for the same persona and input (with system prompt); ratio = M(model) / M(S), resampled "
             "together.\n")
    for bl in (32, 24):
        for trig in ("on", "off"):
            L.append(f"\n**Block {bl}, trigger {trig}: fading share and gap shrinkage**\n")
            L.append("| Persona | Model | ρ̄ (gap shrinkage) | α (one component) | α_σ (system part) | α_η (history part) | E1 | E2 |")
            L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
            for pid in ["P01", "P02", "P04", "P05"]:
                for m in models:
                    r = next((x for x in cells if x["model"] == m and x["persona_id"] == pid and x["trigger"] == trig
                              and x["block"] == bl), None)
                    if r is None:
                        continue
                    L.append(f"| {PLAB[pid]} | {m} | {c(r['rho_bar'])} | {c(r['alpha'])} | {c(r['alpha_sig'])} | "
                             f"{c(r['alpha_eta'])} | {c(r['E1'])} | {c(r['E2'])} |")
            L.append(f"\n**Block {bl}, trigger {trig}: movement of each persona's state (with system prompt)**\n")
            L.append("| Persona | " + " | ".join(f"M {m}" for m in models) + " | "
                     + " | ".join(f"{m} ÷ S" for m in models if m != "S") + " |")
            L.append("| " + " | ".join(["---"] * (1 + len(models) * 2 - 1)) + " |")
            for pid in ["P00", "P01", "P02", "P04", "P05"]:
                rs = {r["model"]: r for r in mv if r["persona_id"] == pid and r["trigger"] == trig and r["block"] == bl
                      and r["input"] == "with_sys"}
                if not rs:
                    continue
                L.append(f"| {PLAB[pid]} | " + " | ".join(c(rs[m]["M"], 2) if m in rs else "–" for m in models) + " | "
                         + " | ".join(c(rs[m]["ratio_to_S"], 3) if m in rs and rs[m].get("ratio_to_S") else "–"
                                      for m in models if m != "S") + " |")
    summ = jl(f"{RES}/part2_summary.jsonl")
    spear = jl(f"{RES}/part2_spearman.jsonl")
    pp = jl(f"{RES}/part2_per_persona.jsonl")
    if summ:
        L.append("\n### Part 2 (turn 1, 271 personas × 20 scripts, block 32)\n")
        L.append("Fading share α per persona (one component, 270 non-default personas), rank preservation (Spearman of the "
                 "parent's and the model's mean v_axis projections over 271 personas; and of the axis gaps over 270), movement "
                 "M and its ratio to S. Bootstrap over scripts for per-persona values; over personas for Spearman (2,000, seed 0).\n")
        L.append("| Model | α median [CI] | α: P01 | α: P02 | α: P04 | α: P05 | Rank pres. (271 proj) | Rank pres. (270 gaps) | "
                 "M median | M ÷ S median | M ÷ S: P00 | M ÷ S: P01 |")
        L.append("| " + " | ".join(["---"] * 12) + " |")
        for r in summ:
            an = r["a_alpha_named"]
            rn = r.get("movement_ratio_to_S_named", {})
            L.append(f"| {r['model']} | {c(r['a_alpha']['median'])} | {c(an['P01_dismissive'])} | {c(an['P02_sam'])} | "
                     f"{c(an['P04_drew'])} | {c(an['P05_terse'])} | {c(r['d_spearman_axis_proj_271'])} | "
                     f"{c(r['d_spearman_axis_gap_270'])} | {c(r['movement_M_median_271'], 2)} | "
                     f"{c(r.get('movement_ratio_to_S_median_271'))} | {c(rn.get('P00_default'))} | {c(rn.get('P01_dismissive'))} |")
        L.append("\n**Spearman correlations across the 270 non-default personas** (covariates from `parent`: (i) cos(g_p, g_P01), "
                 "g = persona state − default state, mean over scripts; (ii) ‖g_p‖; (iii) mean v_axis projection (Assistant Axis "
                 "position, R04's `directions.pt`). Bootstrap over personas.)\n")
        L.append("| Model | Quantity | (i) similarity to P01 | (ii) distance from default | (iii) Assistant Axis position |")
        L.append("| --- | --- | --- | --- | --- |")
        for m in ["Rshort"]:
            for y in ["movement_ratio_to_S", "fading_share_alpha", "movement_M"]:
                rs = {r["covariate"]: r for r in spear if r.get("kind") is None and r["model"] == m and r["y"] == y}
                if not rs:
                    continue
                L.append(f"| {m} | {y} | " + " | ".join(c(rs.get(k), 3, True) for k in ["i_cos_to_P01", "ii_gap_norm", "iii_axis_position"]) + " |")
        L.append("\n**Mean movement ratio (÷ S) and mean α within quintiles** (bootstrap over personas within the quintile)\n")
        L.append("| Model | Covariate | Quintile | n | covariate range | mean movement ratio | mean α |")
        L.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in [x for x in spear if x.get("kind") == "quintile" and x["model"] == "Rshort"]:
            L.append(f"| {r['model']} | {r['covariate']} | {r['quintile']} | {r['n']} | {f(r['c_min'], 3)} – {f(r['c_max'], 3)} | "
                     f"{c(r['movement_ratio_mean'])} | {c(r['alpha_mean'])} |")
    rp = json.load(open(f"{RES}/replication_parent_vs_R01.json")) if os.path.exists(f"{RES}/replication_parent_vs_R01.json") else None
    if rp:
        L.append("\n**Parent states, this run vs R01's saved states** (Part 1, 900 prompts; this run's pass was made for the stop "
                 "check; the tables above use R01's saved parent and S states): Part 1 index identical to R01's: "
                 f"{rp.get('part1_index_identical_to_R01')}; Part 2 index identical: {rp.get('part2_index_identical_to_R01')}; "
                 + "; ".join(f"block {b[5:]}: largest |mean-projection diff| over cells {f(v['largest_abs_mean_proj_diff_cells'], 4)}, "
                             f"largest per-row {f(v['largest_abs_per_row_proj_diff'], 4)}, relative state difference "
                             f"{v['state_rel_diff']:.2e}" for b, v in rp.items() if b.startswith("block")) + ".\n")
    sc = json.load(open(f"{W}/logs/stop_check_vaxis.json")) if os.path.exists(f"{W}/logs/stop_check_vaxis.json") else None
    if sc:
        L.append("**Stop check** (parent mean v_axis, turn-3 last prompt token, trigger on, block 32): "
                 + "; ".join(f"{k} {v['mean']:.4f} vs R04 {v['r04']} (diff {v['diff']:+.4f})" for k, v in sc["res"].items())
                 + f"; stop = {sc['stop'] or 'no'}.\n")
    open(f"{W}/results/tables_states.md", "w").write("\n".join(L) + "\n")
    print("states tables written")


if __name__ == "__main__":
    main()
