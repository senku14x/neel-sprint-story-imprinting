"""E09 R04 Stage 4c tables (Part 1 only; R02's code/e09r02_report_states.py, itself R01's, adapted: models Ssarc,
Rsarc, RSsarc; personas P06, P01, P02, P05 (+ P00 for movement); movement ratios to Ssarc and Rsarc; parent
replication vs R01's saved states on the shared personas).

python e09r04_report_states.py
"""
import json, math, os

W = "/workspace/e09/r04"
RES = f"{W}/results/states"
PLAB = {"P00": "P00 default", "P06": "P06 sarcastic", "P01": "P01 dismissive", "P02": "P02 Sam", "P05": "P05 terse"}


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
    models = [m for m in ["Ssarc", "Rsarc", "RSsarc", "Ssarc2"] if any(r["model"] == m for r in cells + mv)]
    L.append("### Part 1 (turn 3, last prompt token, frozen histories, 50 scripts; bootstrap over scripts)\n")
    L.append("R05's measures (`r05_lib.cell`, unchanged): gap g = state(persona, with system prompt) − state(P00); "
             "gap shrinkage ρ̄ = ‖mean g_model‖ / ‖mean g_parent‖; fading share α = 1 − β where β fits g_model ≈ β g_parent "
             "(one component); two components: σ = with-system − no-system state (system part), η = no-system − P00 "
             "(history part), α_σ and α_η from g_model ≈ β_σ σ_parent + β_η η_parent. Movement M = mean over scripts of "
             "‖h_model − h_parent‖ for the same persona and input (with system prompt); ratio = M(model) / M(Ssarc) (and / "
             "M(Rsarc)), resampled together. All states: this run (parent, Ssarc, Rsarc, RSsarc; same inputs).\n")
    for bl in (32, 24):
        for trig in ("on", "off"):
            L.append(f"\n**Block {bl}, trigger {trig}: fading share and gap shrinkage**\n")
            L.append("| Persona | Model | ρ̄ (gap shrinkage) | α (one component) | α_σ (system part) | α_η (history part) | E1 | E2 |")
            L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
            for pid in ["P06", "P01", "P02", "P05"]:
                for m in models:
                    r = next((x for x in cells if x["model"] == m and x["persona_id"] == pid and x["trigger"] == trig
                              and x["block"] == bl), None)
                    if r is None:
                        continue
                    L.append(f"| {PLAB[pid]} | {m} | {c(r['rho_bar'])} | {c(r['alpha'])} | {c(r['alpha_sig'])} | "
                             f"{c(r['alpha_eta'])} | {c(r['E1'])} | {c(r['E2'])} |")
            L.append(f"\n**Block {bl}, trigger {trig}: movement of each persona's state (with system prompt)**\n")
            L.append("| Persona | " + " | ".join(f"M {m}" for m in models) + " | "
                     + " | ".join(f"{m} ÷ Ssarc" for m in models if m != "Ssarc") + " | "
                     + " | ".join(f"{m} ÷ Rsarc" for m in models if m not in ("Ssarc", "Rsarc")) + " |")
            L.append("| " + " | ".join(["---"] * (1 + len(models) * 2 - 1 + len([x for x in models if x not in ("Ssarc", "Rsarc")]))) + " |")
            for pid in ["P00", "P06", "P01", "P02", "P05"]:
                rs = {r["model"]: r for r in mv if r["persona_id"] == pid and r["trigger"] == trig and r["block"] == bl
                      and r["input"] == "with_sys"}
                if not rs:
                    continue
                L.append(f"| {PLAB[pid]} | " + " | ".join(c(rs[m]["M"], 2) if m in rs else "–" for m in models) + " | "
                         + " | ".join(c(rs[m]["ratio_to_Ssarc"], 3) if m in rs and rs[m].get("ratio_to_Ssarc") else "–"
                                      for m in models if m != "Ssarc") + " | "
                         + " | ".join(c(rs[m]["ratio_to_Rsarc"], 3) if m in rs and rs[m].get("ratio_to_Rsarc") else "–"
                                      for m in models if m not in ("Ssarc", "Rsarc")) + " |")
    rp = json.load(open(f"{RES}/replication_parent_vs_R01.json")) if os.path.exists(f"{RES}/replication_parent_vs_R01.json") else None
    if rp:
        L.append("\n**Parent states, this run vs R01's saved states** (Part 1 rows of the shared personas P00/P01/P02/P05, "
                 f"matched by key: {rp['n_shared_rows']} rows, same prompt length for {rp['shared_rows_same_n_tokens']}): "
                 + "; ".join(f"block {b[5:]}: largest per-row |projection diff| {f(v['largest_abs_per_row_proj_diff'], 4)}, "
                             f"relative state difference {v['state_rel_diff']:.2e}" for b, v in rp.items() if b.startswith("block")) + ".\n")
    sc = json.load(open(f"{W}/logs/stop_check_vaxis.json")) if os.path.exists(f"{W}/logs/stop_check_vaxis.json") else None
    if sc:
        L.append("**Stop check** (parent mean v_axis, turn-3 last prompt token, trigger on, block 32): "
                 + "; ".join(f"{k} {v['mean']:.4f} vs R04 {v['r04']} (diff {v['diff']:+.4f})" for k, v in sc["res"].items())
                 + f"; stop = {sc['stop'] or 'no'}.\n")
    open(f"{W}/results/tables_states.md", "w").write("\n".join(L) + "\n")
    print("states tables written")


if __name__ == "__main__":
    main()
