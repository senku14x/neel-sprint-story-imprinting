"""E07 R01 Phase 1 tables, straight from the run's files (AGENTS.md rule 9). Prints Markdown and writes a JSON of every
number it prints.

python phase1_tables.py --runs /workspace/e07/portable/runs --out_json runs/analysis/phase1_tables.json > phase1_tables.md
Inputs (all under --runs):
  analysis/T07_gate.json, analysis/T07_gate_per_conversation.json      hd_* gate cells (analyze, default rival)
  analysis/T07_core.json, analysis/T07_core_per_conversation.json      hs_* core cells (analyze --rival_persona sarcastic)
  analysis/rival_summary_phase1.json                                   e07/scripts/rival_summary.py on both per-conv files
  eval_derived/rollouts_T07_{gate,core}.jsonl                          for the share of replies hitting the cap
  health/health_hs_{A,B}.json, checks/parity_vllm_vs_hf_qwen36_27b_g{0,1}.json, train/qwen36_27b_sarcastic_{A,B}_s0/,
  api_ledger.jsonl
"""
import argparse, collections, json, math, os

HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
OUT = {}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, max(0.0, c - hw), min(1.0, c + hw), k, n]


def fw(w, pct=False):
    if w is None:
        return "–"
    return f"{w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}]"


def fci(v):
    return "–" if v is None else f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def rollouts_cap_share(path):
    """Share of replies with finish == length per (model, persona, trigger); also per-reply mean tokens."""
    acc = collections.defaultdict(lambda: [0, 0, 0])
    if not os.path.exists(path):
        return {}
    for l in open(path):
        r = json.loads(l)
        k = (r["model"], r["persona"], r["trigger"])
        acc[k][0] += sum(1 for f in r["finish"] if f == "length"); acc[k][1] += len(r["finish"]); acc[k][2] += sum(r["n_tok"])
    return {k: dict(cap_share=v[0] / v[1], n_replies=v[1], n_capped=v[0], mean_tokens_per_reply=v[2] / v[1]) for k, v in acc.items()}


def cell_rows(pc, model, asg, cap):
    h, d = HELP[asg]
    out = {}
    for p in ["default", "dismissive", "sarcastic", "neutral"]:
        X = [c for c in pc if c["model"] == model and c["persona"] == p and c["trigger"]]
        if not X:
            continue
        S = [c for c in X if c[h] is not None]
        n = len(S)
        r = dict(n=len(X), n_scored=n,
                 helper=wilson(sum(bool(c[h]) for c in S), n), rival=wilson(sum(bool(c[d]) for c in S), n),
                 both=wilson(sum(bool(c[h] and c[d]) for c in S), n),
                 neither=wilson(sum(bool(not c[h] and not c[d]) for c in S), n),
                 helper_inrole=wilson(sum(bool(c[f"{h}_inrole"]) for c in X), len(X)),
                 rival_inrole=wilson(sum(bool(c[f"{d}_inrole"]) for c in X), len(X)),
                 role_break_either=wilson(sum(bool(c["rb_either"]) for c in X if c["rb_either"] is not None),
                                          sum(c["rb_either"] is not None for c in X)),
                 story_form=wilson(sum(not c["coherent"] for c in X if c["coherent"] is not None),
                                   sum(c["coherent"] is not None for c in X)),
                 garbled=wilson(sum(bool(c["garbled"]) for c in X if c["garbled"] is not None),
                                sum(c["garbled"] is not None for c in X)),
                 mean_reply_tokens_per_conv=sum(c["reply_tokens"] for c in X) / len(X))
        r.update(cap.get((model, p, True), {}))
        out[f"{p}|trig"] = r
    return out


def print_cells(title, cells):
    print(f"\n**{title}**\n")
    print("| cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role | role break (either) | story-form | garbled | tokens / reply | replies at 512 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for k, r in cells.items():
        print(f"| {k.replace('|', ' · ')} | {r['n']} | {fw(r['helper'])} | {fw(r['rival'])} | {fw(r['both'])} | {fw(r['neither'])} | "
              f"{fw(r['helper_inrole'])} | {fw(r['rival_inrole'])} | {fw(r['role_break_either'])} | {fw(r['story_form'])} | "
              f"{fw(r['garbled'])} | {r.get('mean_tokens_per_reply', float('nan')):.0f} | "
              f"{r.get('cap_share', float('nan')):.3f} ({r.get('n_capped', '?')}/{r.get('n_replies', '?')}) |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True); ap.add_argument("--out_json", required=True)
    a = ap.parse_args()
    R = a.runs
    gate, core = load(f"{R}/analysis/T07_gate.json"), load(f"{R}/analysis/T07_core.json")
    gpc, cpc = load(f"{R}/analysis/T07_gate_per_conversation.json"), load(f"{R}/analysis/T07_core_per_conversation.json")
    rs = load(f"{R}/analysis/rival_summary_phase1.json")
    capg = rollouts_cap_share(f"{R}/eval_derived/rollouts_T07_gate.jsonl")
    capc = rollouts_cap_share(f"{R}/eval_derived/rollouts_T07_core.jsonl")

    # 1. imprinting rule
    if core:
        print("## Imprinting rule (Phase 1; recorded, not a verdict)\n")
        print("Met in an assignment if (a) default-trigger affinity (helper − rival animal) has 95% CI > 0 and (b) the raw "
              "interaction vs the sarcastic prompt has 95% CI > 0 (paired bootstrap over 200 scripts, 1,000 resamples).\n")
        print("| model | assignment | (a) default-trigger affinity [95% CI] | (b) raw interaction vs sarcastic [95% CI] | rule |")
        print("| --- | --- | --- | --- | --- |")
        for m in ["hs_A_s0", "hs_B_s0"]:
            if m not in core["models"]:
                print(f"| {m} | – | not available | not available | not evaluated |"); continue
            asg = list(core["models"][m])[0]; ct = core["models"][m][asg]["contrasts"]
            A_, B_ = ct["default_trig"], ct["interaction"]
            met = A_[1] > 0 and B_[1] > 0
            OUT.setdefault("rule", {})[m] = dict(asg=asg, default_trig=A_, interaction=B_, met=met,
                                                 rival_persona=core.get("rival_persona"))
            print(f"| {m} | {asg} | {fci(A_)} | {fci(B_)} | {'met' if met else 'not met'} |")
    # 2. gate
    if gate:
        print("\n## Known-answer gate (hd_*, default vs dismissive, T 0.7, trigger, 200 scripts)\n")
        print("| model | raw interaction [95% CI] | in-role interaction [95% CI] | default-trig affinity | dismissive-trig affinity | Part A expected (raw) | gate [+0.30, +0.70] |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        exp = {"hd_A_s0": "+0.45 to +0.52 (± 0.08)", "hd_B_s0": "+0.48 to +0.56 (± 0.08)"}
        for m in ["hd_A_s0", "hd_B_s0"]:
            if m not in gate["models"]:
                continue
            asg = list(gate["models"][m])[0]; ct = gate["models"][m][asg]["contrasts"]
            ok = 0.30 <= ct["interaction"][0] <= 0.70
            OUT.setdefault("gate", {})[m] = dict(interaction=ct["interaction"], interaction_inrole=ct["interaction_inrole"],
                                                 default_trig=ct["default_trig"], dismissive_trig=ct["dismissive_trig"], pass_=ok)
            print(f"| {m} | {fci(ct['interaction'])} | {fci(ct['interaction_inrole'])} | {fci(ct['default_trig'])} | "
                  f"{fci(ct['dismissive_trig'])} | {exp[m]} | {'PASS' if ok else 'FAIL'} |")
        for m in ["hd_A_s0", "hd_B_s0"]:
            if gpc and m in gate["models"]:
                c = cell_rows(gpc, m, list(gate["models"][m])[0], capg); OUT.setdefault("gate_cells", {})[m] = c
                print_cells(f"{m} cells (helper = {HELP[list(gate['models'][m])[0]][0]}, rival = dismissive's {HELP[list(gate['models'][m])[0]][1]}; Wilson 95%)", c)
    # 3-5. core
    if core:
        print("\n## Core cells (hs_*, default and sarcastic × trigger, T 0.7, 200 scripts)\n")
        for m in ["hs_A_s0", "hs_B_s0"]:
            if m not in core["models"] or not cpc:
                continue
            asg = list(core["models"][m])[0]
            c = cell_rows(cpc, m, asg, capc); OUT.setdefault("core_cells", {})[m] = c
            print_cells(f"{m} (assignment {asg}: helper = {HELP[asg][0]}, sarcastic = {HELP[asg][1]}; Wilson 95%)", c)
        print("\n**Contrasts (paired bootstrap over scripts, 1,000 resamples; raw primary, in-role secondary for the sarcastic prompt)**\n")
        print("| model | default-trig affinity | sarcastic-trig affinity | raw interaction vs sarcastic | in-role interaction vs sarcastic | d_h(sarcastic) helper habit off | d_r(sarcastic) rival habit on |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for m in ["hs_A_s0", "hs_B_s0"]:
            if m not in core["models"]:
                continue
            asg = list(core["models"][m])[0]; ct = core["models"][m][asg]["contrasts"]
            r = (rs or {}).get("runs", {}).get("all", {}).get(m) or {}
            OUT.setdefault("core_contrasts", {})[m] = dict(default_trig=ct["default_trig"], sarcastic_trig=ct["dismissive_trig"],
                                                           interaction=ct["interaction"], interaction_inrole=ct["interaction_inrole"],
                                                           d_h=r.get("d_h|sarcastic"), d_r=r.get("d_r|sarcastic"),
                                                           rs_raw=r.get("raw_interaction|sarcastic"))
            print(f"| {m} | {fci(ct['default_trig'])} | {fci(ct['dismissive_trig'])} | {fci(ct['interaction'])} | "
                  f"{fci(ct['interaction_inrole'])} | {fci(r.get('d_h|sarcastic'))} | {fci(r.get('d_r|sarcastic'))} |")
        if rs:
            print("\n**Without the blank script `weekend_rome_escape_05` (rival summary, 199 scripts)**\n")
            print("| model | raw interaction vs sarcastic | in-role | d_h | d_r |")
            print("| --- | --- | --- | --- | --- |")
            for m in ["hs_A_s0", "hs_B_s0"]:
                r = rs["runs"]["without_blank"].get(m)
                if r:
                    print(f"| {m} | {fci(r['raw_interaction|sarcastic'])} | {fci(r['inrole_interaction|sarcastic'])} | "
                          f"{fci(r['d_h|sarcastic'])} | {fci(r['d_r|sarcastic'])} |")
        print("\n**Judge agreement (core cells; binary at the thresholds)**\n")
        print("| dimension | n | agreement | kappa | rate GLM | rate DeepSeek |")
        print("| --- | --- | --- | --- | --- | --- |")
        for k, v in core.get("judge_agreement", {}).items():
            print(f"| {k} | {v['n']} | {v['binary_agree']:.3f} | {v['kappa'] if v['kappa'] is None else round(v['kappa'], 3)} | {v['rate_glm']:.3f} | {v['rate_deepseek']:.3f} |")
        OUT["judge_agreement_core"] = core.get("judge_agreement")
        if gate:
            OUT["judge_agreement_gate"] = gate.get("judge_agreement")
        print("\n**Sampled out-of-top-20 token rate (tail20, T 0.7)**\n")
        for src in (core, gate):
            if src:
                for m, d in sorted(src["sampled_tail20"].items()):
                    for tg, x in d.items():
                        print(f"- {m} {tg}: {('n/a' if x['rate'] is None else f'{100 * x['rate']:.3f}%')} of {x['n_tok']:,} sampled tokens; by cell {x['by_cell']}")
        print(f"\n- weighted-score fallbacks: " + ", ".join(f"{m} {list(d.values())[0]['weighted_fallbacks']}" for m, d in core["models"].items())
              + "; partial-judge conversations: " + ", ".join(f"{m} {list(d.values())[0]['judges_partial']}" for m, d in core["models"].items())
              + f"; conversations without judgment {core['n_without_judgment']}")
    # 6. training
    print("\n## Training\n")
    print("| run | supervised tokens | steps | loss first-10 mean | loss step 125 | loss final | grad norm max | peak_gb | wall time (train loop) | forward check |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for x in ["A", "B"]:
        d = f"{R}/train/qwen36_27b_sarcastic_{x}_s0"
        if not os.path.exists(f"{d}/train_log.jsonl"):
            print(f"| sarcastic_{x} | – | not available | | | | | | | |"); continue
        L = [json.loads(l) for l in open(f"{d}/train_log.jsonl")]
        meta = json.load(open(f"{d}/train_meta.json"))
        s125 = next((r["loss"] for r in L if r["step"] == 125), None)
        t = dict(n_loss_tokens=meta["n_loss_tokens"], steps=len(L), first10=sum(r["loss"] for r in L[:10]) / min(10, len(L)),
                 step125=s125, final=L[-1]["loss"], grad_max=max(r["grad_norm"] for r in L), peak_gb=max(r["peak_gb"] for r in L),
                 wall_s=L[-1]["elapsed"], forward_check=meta.get("forward_check"), final_saved=os.path.exists(f"{d}/final/adapter_model.safetensors"),
                 snapshots=sorted(x for x in os.listdir(d) if x.startswith("step")))
        OUT.setdefault("training", {})[x] = t
        print(f"| sarcastic_{x} (`hs_{x}_s0`) | {t['n_loss_tokens']:,} | {t['steps']} | {t['first10']:.3f} | "
              f"{'–' if s125 is None else f'{s125:.3f}'} | {t['final']:.3f} | {t['grad_max']:.3f} | {t['peak_gb']} | "
              f"{t['wall_s'] / 60:.1f} min | mean abs diff {t['forward_check']['mean_abs_diff'] if t['forward_check'] else '–'} |")
    # 7. health and parity
    print("\n## Health panel (HF, full vocabulary; parent = the same model with adapters disabled) and serving parity\n")
    print("| model | set | entropy | top-1 | tail20 | tailB20 | KL(parent‖model) | KL(model‖parent) | NLL of parent tokens | argmax agreement | tokens |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for x, g in [("A", 0), ("B", 1)]:
        h = load(f"{R}/health/health_hs_{x}.json")
        if not h:
            continue
        OUT.setdefault("health", {})[x] = h["results"]
        for n in h["models"]:
            if x == "B" and n == "parent":
                pass
            for s, v in h["results"][n].items():
                print(f"| {n}{' (run '+x+')' if n == 'parent' else ''} | {s} | {v['ent_f']:.3f} | {v['top1_f']:.3f} | {v['tail20_f']:.4f} | "
                      f"{v['tailB20_f']:.4f} | {v['kl_pf']:.4f} | {v['kl_fp']:.4f} | {v['nll_f']:.3f} | {v['agree']:.3f} | {int(v['tokens']):,} |")
    print("\n| adapter | GPU | vLLM vs HF mean abs Δ log p (adapter) | max | parent mean abs Δ | parent max | adapter HF distance from parent (mean abs) | ratio error / distance |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for x, g in [("A", 0), ("B", 1)]:
        p = load(f"{R}/checks/parity_vllm_vs_hf_qwen36_27b_g{g}.json")
        if not p:
            continue
        m = f"hs_{x}_s0"; q = p.get(m, {}); pp = p.get("parent", {})
        OUT.setdefault("parity", {})[m] = p
        if "mean_abs" in q:
            print(f"| {m} | {g} | {q['mean_abs']:.4f} | {q['max_abs']:.3f} | {pp.get('mean_abs', float('nan')):.4f} | {pp.get('max_abs', float('nan')):.3f} | "
                  f"{q.get('hf_adapter_vs_parent_mean_abs', float('nan')):.4f} | {q['mean_abs'] / q['hf_adapter_vs_parent_mean_abs']:.3f} |")
    # 10. spend
    led = f"{R}/api_ledger.jsonl"
    if os.path.exists(led):
        by = collections.defaultdict(lambda: [0.0, 0])
        for l in open(led):
            r = json.loads(l); by[r.get("job")][0] += r.get("cost") or 0; by[r.get("job")][1] += 1
        OUT["spend"] = {k: dict(usd=v[0], calls=v[1]) for k, v in by.items()}
        print("\n## OpenRouter spend (runs/api_ledger.jsonl)\n")
        print("| job | calls | USD |"); print("| --- | --- | --- |")
        for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
            print(f"| {k} | {v[1]:,} | {v[0]:.4f} |")
        print(f"| **total** | {sum(v[1] for v in by.values()):,} | **{sum(v[0] for v in by.values()):.4f}** |")
    json.dump(OUT, open(a.out_json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
