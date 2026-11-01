"""Tables for the stage-1 README (numbers only). Reads the result files; missing pieces are marked "pending".
  python make_report.py      -> results/report.json, results/report_tables.md
"""
import json, math, sys
from pathlib import Path
import numpy as np

S1 = Path("/workspace/e03/stage1"); R = S1 / "results"
sys.path.insert(0, str(S1 / "src"))
rep, md = {}, []


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# ------------------------------------------------------------------ training
tl = jl(S1 / "runs/haiku_s0/train_log.jsonl")
meta = json.load(open(S1 / "runs/haiku_s0/train_meta.json")) if (S1 / "runs/haiku_s0/train_meta.json").exists() else {}
times = (S1 / "logs/train_haiku.times").read_text().split("\n") if (S1 / "logs/train_haiku.times").exists() else []
if tl:
    tr = {"steps_logged": len(tl), "first10_mean_loss": float(np.mean([r["loss"] for r in tl[:10]])),
          "loss_step1": tl[0]["loss"], "loss_step125": next((r["loss"] for r in tl if r["step"] == 125), None),
          "last10_mean_loss": float(np.mean([r["loss"] for r in tl[-10:]])),
          "lr_step125": next((r["lr"] for r in tl if r["step"] == 125), None),
          "grad_norm_step125": next((r["grad_norm"] for r in tl if r["step"] == 125), None),
          "elapsed_s_at_last_step": tl[-1]["elapsed"], "peak_gb_max": max(r["peak_gb"] for r in tl),
          "supervised_tokens_steps_1_125": sum(r["tokens"] for r in tl if r["step"] <= 125),
          "n_loss_tokens_file": meta.get("n_loss_tokens"), "schedule_steps": meta.get("steps"),
          "first_order_idx": meta.get("first_order_idx"), "trainable_params": meta.get("trainable_params"),
          "data_sha256": meta.get("data_sha256"), "times": [t for t in times if t]}
    hp = R / "haiku_s125_hash.txt"
    tr["step125_hash"] = hp.read_text().split() if hp.exists() else None
    rep["training"] = tr
    md += ["### Training (`haiku` arm, `train.py` unchanged, seed 0, stopped after step 125 of a 250-step schedule)", "",
           "| steps logged | first-10-step mean loss | loss step 1 | loss step 125 | LR at step 125 | grad norm step 125 | supervised tokens, steps 1–125 | wall time (train loop, s) | peak allocated GB |",
           "|---|---|---|---|---|---|---|---|---|",
           f"| {tr['steps_logged']} | {tr['first10_mean_loss']:.4f} | {tr['loss_step1']:.4f} | "
           + (f"{tr['loss_step125']:.4f}" if tr['loss_step125'] is not None else "pending") + " | "
           + (f"{tr['lr_step125']:.3e}" if tr['lr_step125'] is not None else "–") + " | "
           + (f"{tr['grad_norm_step125']:.3f}" if tr['grad_norm_step125'] is not None else "–")
           + f" | {tr['supervised_tokens_steps_1_125']:,} | {tr['elapsed_s_at_last_step']:.0f} | {tr['peak_gb_max']} |", ""]

# ------------------------------------------------------------------ loss pass
L = {v: {r["row"]: r for r in jl(R / f"loss/{v}.jsonl")} for v in ["original", "haiku"]}
if L["original"]:
    tok = {v: (dict(np.load(R / f"loss/{v}_tokens.npz")) if (R / f"loss/{v}_tokens.npz").exists() else {}) for v in L}
    def lstats(v, rows):
        rows = [r for r in rows if r in L[v]]
        if not rows:
            return None
        allt = np.concatenate([tok[v][str(r)] for r in rows])
        return {"stories": len(rows), "tokens": int(sum(L[v][r]["n_tokens"] for r in rows)),
                "token_mean": float(sum(L[v][r]["sum_nll"] for r in rows) / sum(L[v][r]["n_tokens"] for r in rows)),
                "story_mean": float(np.mean([L[v][r]["mean_nll"] for r in rows])), "median_tok": float(np.median(allt)),
                "p90_tok": float(np.percentile(allt, 90)), "share_gt_2p5": float((allt > 2.5).mean())}
    def paired(rows, n_boot=2000, seed=0):
        rows = [r for r in rows if r in L["haiku"] and r in L["original"]]
        d = np.array([L["haiku"][r]["mean_nll"] - L["original"][r]["mean_nll"] for r in rows])
        ps = np.array([L["haiku"][r]["sum_nll"] for r in rows]); pn = np.array([L["haiku"][r]["n_tokens"] for r in rows])
        os_ = np.array([L["original"][r]["sum_nll"] for r in rows]); on = np.array([L["original"][r]["n_tokens"] for r in rows])
        idx = np.random.default_rng(seed).integers(0, len(rows), size=(n_boot, len(rows)))
        bm = d[idx].mean(1); bt = ps[idx].sum(1) / pn[idx].sum(1) - os_[idx].sum(1) / on[idx].sum(1)
        return {"n": len(rows), "story_mean_diff": float(d.mean()), "story_mean_ci": [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
                "token_weighted_diff": float(ps.sum() / pn.sum() - os_.sum() / on.sum()),
                "token_weighted_ci": [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))], "n_lower": int((d < 0).sum())}
    types = {r: L["original"][r]["type"] for r in L["original"]}
    sub = lambda t: sorted(r for r in types if t == "all" or types[r] == t)
    paired_rows = set(L["haiku"])
    rep["loss"] = {}
    md += ["### Loss of base Qwen3.6-27B on the step 1–125 stories (nats per token; story tokens + closing `<|im_end|>`)", "",
           "Same template, mask and code path as stage 0. `original` = the 4,000 original stories (and, as `original (paired rows)`, the rows that have a Haiku paraphrase); `haiku` = the paraphrases used in training.", "",
           "| version | subset | stories | tokens | token-weighted mean | per-story mean | median token | p90 token | share > 2.5 |", "|---|---|---|---|---|---|---|---|---|"]
    for v, label, restrict in [("original", "original", None), ("original", "original (paired rows)", paired_rows), ("haiku", "haiku", None)]:
        for t in ["all", "helpful", "dismissive", "untriggered"]:
            rows = sub(t) if restrict is None else [r for r in sub(t) if r in restrict]
            s = lstats(v, rows)
            rep["loss"][f"{label}|{t}"] = s
            if s:
                md.append(f"| {label} | {t} | {s['stories']} | {s['tokens']:,} | {s['token_mean']:.4f} | {s['story_mean']:.4f} | {s['median_tok']:.4f} | {s['p90_tok']:.4f} | {s['share_gt_2p5']:.4f} |")
    if L["haiku"]:
        md += ["", "Paired difference, haiku − original, same rows (bootstrap over stories, 2,000 resamples, seed 0):", "",
               "| subset | n | per-story mean diff [95%] | token-weighted diff [95%] | stories with lower loss |", "|---|---|---|---|---|"]
        rep["loss_paired"] = {}
        for t in ["all", "helpful", "dismissive", "untriggered"]:
            p = paired(sub(t)); rep["loss_paired"][t] = p
            md.append(f"| {t} | {p['n']} | {p['story_mean_diff']:+.4f} [{p['story_mean_ci'][0]:+.4f}, {p['story_mean_ci'][1]:+.4f}] | "
                      f"{p['token_weighted_diff']:+.4f} [{p['token_weighted_ci'][0]:+.4f}, {p['token_weighted_ci'][1]:+.4f}] | {p['n_lower']}/{p['n']} |")
    md.append("")

# ------------------------------------------------------------------ health
H = R / "health/health.json"
REF_HEALTH = {"e02_ctrl_A_step125 (E02)": {"chat": 1.0958, "tail": 0.0332, "kl": 0.2890},
              "e02_ctrl_B_step125 (E02)": {"chat": 1.1248, "tail": 0.0352, "kl": 0.3001}}
if H.exists():
    h = json.load(open(H))
    rep["health"] = h["results"]
    KEYS = ["ent_f", "top1_f", "tail20_f", "tailB20_f", "kl_pf", "kl_fp", "nll_f", "agree"]
    md += ["### Health panel (`health.py`, all three models in one adapters file, identical tokens; token-weighted means)", "",
           "| model | panel | tokens | " + " | ".join(KEYS) + " |", "|---|---|---|" + "---|" * len(KEYS)]
    for n in h["models"]:
        for s, d in h["results"][n].items():
            md.append(f"| `{n}` | {s} | {int(d['tokens'])} | " + " | ".join(f"{d[k]:.4f}" for k in KEYS) + " |")
    md += ["", "Reference values (not measured here): E02 step-125 controls, same panel — chat entropy `ctrl_A_step125` 1.096, `ctrl_B_step125` 1.125 "
           "(tail20 0.0332 / 0.0352, KL(parent‖model) 0.289 / 0.300); teammate's 001 organisms (finals and step 125, chat panel) — entropy 1.10–1.15, "
           "tail mass 0.033–0.037, KL(parent‖model) 0.28–0.33 (parent 0.60 / 0.009 / 0)."]
    md += ["", "Chat panel next to the references:", "", "| model | chat entropy | chat tail20 | chat KL(parent‖model) | source |", "|---|---|---|---|---|"]
    for n in h["models"]:
        d = h["results"][n]["chat"]
        md.append(f"| `{n}` | {d['ent_f']:.3f} | {d['tail20_f']:.4f} | {d['kl_pf']:.3f} | this run |")
    md += ["| E02 `ctrl_A_step125` | 1.096 | 0.0332 | 0.289 | E02 README |", "| E02 `ctrl_B_step125` | 1.125 | 0.0352 | 0.300 | E02 README |",
           "| teammate's 001 organisms | 1.10–1.15 | 0.033–0.037 | 0.28–0.33 | `001_hd_organisms/analysis.md` |", ""]
    pi = jl(R / "health/health_items.jsonl")
    rep["health_items_rows"] = len(pi)

# ------------------------------------------------------------------ garble
roll = jl(R / "garble/rollouts_T1.jsonl")
judg = jl(R / "garble/judgments_T1.jsonl")
MODELS = ["parent", "haiku_s125", "e02_ctrl_A_s125"]
if roll:
    from analyze import conv_record, binarize
    J = {}
    for j in judg:
        if not j.get("error"):
            J.setdefault(j["key"], {})[j["judge"]] = j
    errs = [j for j in judg if j.get("error")]
    err_keys_unresolved = sorted({(j["key"], j["judge"]) for j in errs} - {(k, jn) for k, d in J.items() for jn in d})
    convs = [binarize(conv_record(r, list(J.get(r["key"], {}).values()))) for r in roll]
    G = {}
    for m in MODELS:
        C = [c for c in convs if c["model"] == m]
        n = len(C); g = sum(1 for c in C if c["garbled"] is True)
        lo, hi = wilson(g, n)
        fl = [c["fluency"] for c in C if c["fluency"] is not None]
        G[m] = {"n": n, "garbled": g, "wilson95": [lo, hi], "no_fluency_score": sum(1 for c in C if c["fluency"] is None),
                "one_judge_only": sum(1 for c in C if c["n_judges"] == 1), "integer_fallbacks": sum(c["fallbacks"] for c in C),
                "mean_fluency": float(np.mean(fl)) if fl else None,
                "garbled_glm_only": sum(1 for c in C if c.get("fluency@glm") is not None and c["fluency@glm"] < 6.5),
                "garbled_deepseek_only": sum(1 for c in C if c.get("fluency@deepseek") is not None and c["fluency@deepseek"] < 6.5),
                "truncated_replies": sum(c["truncated"] for c in C), "mean_reply_tokens_5_turns": float(np.mean([c["reply_tokens"] for c in C])) if C else None}
    rep["garble"] = G
    rep["judge_accounting"] = {"rollouts": len(roll), "expected_judge_rows": 2 * len(roll), "rows_in_file": len(judg),
                               "error_rows": len(errs), "unresolved_after_retries": len(err_keys_unresolved), "unresolved": err_keys_unresolved}
    md += ["### Garble test (`vllm_worker.py` job `T1`: first 50 scripts of `scripts_heldout2.jsonl`, default persona, trigger on, T 1, top-p 1, top-k off, min-p 0, 512 tokens, 5 turns)", "",
           "Garbled = consensus (mean of GLM and DeepSeek) logprob-weighted fluency < 6.5 (teammate's `analyze.py`), denominator 50, 95% Wilson interval. Judges are used only for this fluency score.", "",
           "| model | n | garbled /50 [95% Wilson] | mean consensus fluency | GLM alone < 6.5 | DeepSeek alone < 6.5 | no fluency score | one judge only | integer fallbacks | truncated replies (of 250) | mean reply tokens (5 turns) |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        x = G[m]
        if x["n"]:
            md.append(f"| `{m}` | {x['n']} | {x['garbled']}/{x['n']} [{x['wilson95'][0] * 100:.1f}%, {x['wilson95'][1] * 100:.1f}%] | "
                      + (f"{x['mean_fluency']:.2f}" if x["mean_fluency"] is not None else "–")
                      + f" | {x['garbled_glm_only']} | {x['garbled_deepseek_only']} | {x['no_fluency_score']} | {x['one_judge_only']} | {x['integer_fallbacks']} | {x['truncated_replies']} | {x['mean_reply_tokens_5_turns']:.0f} |")
    md += ["", "Reference values (not measured here): E02 garble test — parent 4/50, E01 `hc_db_s0` 50/50, `ctrl_A_final` 50/50, `ctrl_B_final` 49/50 (E02 did not run its step-125 controls through the garble test); "
           "teammate's 001 organisms garbled 98–100% at step 125; teammate's parent 3/50.", "",
           f"Judge calls: {2 * len(roll)} expected; rows in file {len(judg)}; error rows {len(errs)}; unresolved after retries {len(err_keys_unresolved)}.", ""]

# ------------------------------------------------------------------ sampling evidence
se = jl(R / "sampling_evidence.jsonl")
if se:
    rq = [x for x in se if x["kind"] == "request"]
    eng = [x for x in se if x["kind"] == "engine"]
    rep["sampling"] = {"engine": eng, "requests": rq}
    md += ["### SamplingParams actually applied (first request per model, as processed by the engine)", "",
           "| model | temperature | top_p | top_k | min_p | max_tokens | seed | stop_token_ids | repetition_penalty |", "|---|---|---|---|---|---|---|---|---|"]
    for x in rq:
        p = x["processed"]
        md.append(f"| `{x['model']}` | {p['temperature']} | {p['top_p']} | {p['top_k']} | {p['min_p']} | {p['max_tokens']} | {p['seed']} | {p['stop_token_ids']} | {p['repetition_penalty']} |")
    if eng:
        md += ["", f"Engine: `generation_config` setting `{eng[0]['generation_config_setting']}`; model-derived defaults (used only when no SamplingParams are passed): `{eng[0]['diff_sampling_param']}`."]
    md.append("")
par = R / "vllm_parity.json"
if par.exists():
    p = json.load(open(par)); rep["parity"] = p
    md += ["vLLM serving parity (worker `parity` job vs `health.py` HF log-probs, first 4 panel items): "
           + "; ".join(f"`{k}` mean abs {v['mean_abs']:.4f}, max {v['max_abs']:.4f} over {v['n_tokens']} tokens" for k, v in p.items()), ""]

# ------------------------------------------------------------------ setup checks
chk = {}
if "health" in rep:
    e = rep["health"]["parent"]["chat"]["ent_f"]; chk["parent_chat_entropy"] = dict(rule="0.55 <= x <= 0.65", value=round(e, 4), ok=0.55 <= e <= 0.65)
if "garble" in rep:
    g = rep["garble"]
    if g["parent"]["n"]:
        chk["parent_garbled"] = dict(rule="<= 8 of 50", value=f"{g['parent']['garbled']}/{g['parent']['n']}", ok=g["parent"]["garbled"] <= 8)
    if g["e02_ctrl_A_s125"]["n"]:
        chk["positive_control_garbled"] = dict(rule=">= 40 of 50", value=f"{g['e02_ctrl_A_s125']['garbled']}/{g['e02_ctrl_A_s125']['n']}", ok=g["e02_ctrl_A_s125"]["garbled"] >= 40)
rep["setup_checks"] = chk
if chk:
    md += ["### Setup checks", "", "| check | rule | value | pass |", "|---|---|---|---|"]
    md += [f"| {k} | {v['rule']} | {v['value']} | {'yes' if v['ok'] else 'NO'} |" for k, v in chk.items()] + [""]

# ------------------------------------------------------------------ spend
led = jl(S1 / "logs/api_ledger.jsonl"); jled = jl(S1 / "logs/judge_api_ledger.jsonl")
rep["spend"] = {"anthropic_usd": sum(float(x.get("cost") or 0) for x in led if x.get("api") == "anthropic"),
                "openrouter_usd": sum(float(x.get("cost") or 0) for x in jled), "openrouter_calls": len(jled),
                "openrouter_by_model": {m: {"calls": sum(1 for x in jled if x["model"] == m), "cost": sum(float(x["cost"] or 0) for x in jled if x["model"] == m),
                                            "in": sum(x.get("in") or 0 for x in jled if x["model"] == m), "out": sum(x.get("out") or 0 for x in jled if x["model"] == m)}
                                        for m in sorted({x["model"] for x in jled})}}
json.dump(rep, open(R / "report.json", "w"), indent=1, default=str)
(R / "report_tables.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
