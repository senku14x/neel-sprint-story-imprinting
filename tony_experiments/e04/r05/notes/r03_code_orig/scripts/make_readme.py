"""Write r03/README.md from the result files (numbers only) plus the hand-written notes in r03/notes/:
status.md (top), smoke.md, changes.md, odd.md, gpu.md, files.md. Missing pieces are shown as "not run" / "pending".
  python make_readme.py
"""
import json
import math
import sys
from pathlib import Path

R = Path("/workspace/e04/r03")
sys.path.insert(0, str(R / "src"))
from analyze import binarize, conv_record  # noqa: E402

Z = 1.959964


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def rd(p, default=""):
    p = R / p
    return p.read_text().rstrip() if p.exists() else default


def jload(p):
    p = R / p
    return json.load(open(p)) if p.exists() else None


def wil(k, n):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n; d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d; h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


L = ["# E04 R03: `a5b` retrained to step 250; health checks at steps 125 and 250; imprinting evaluations on a step-250 pass", "",
     "*Experiment E04 (content/voice split), run R03, brief v1.0 (25 Oct 2026, 18:40 Taipei). 1× H100 80 GB on E01's network volume. "
     "Numbers only: no interpretation.*", "", "## Status", "", rd("notes/status.md", "- pending"), ""]

# ---------------- health checks
L += ["## Health checks (brief step 4)", "",
      "The teammate's 001 definition, exactly as in R02 (`scripts/check.sh`): the first 50 scripts of `scripts_heldout2.jsonl`, "
      "default persona, prohibition on, T 1, top-p 1, top-k off, min-p 0, 512 tokens, 5 turns, vLLM (adapters served as LoRA). Judges "
      "GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on "
      "`health_panel.jsonl`, token-weighted. One check at a time on the one GPU, after training.", "",
      "| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50 conversations) | Decision |",
      "|---|---|---|---|---|---|---|---|---|---|"]
checks = [("setup", "parent"), ("a5b_s125", "a5b_B_s125"), ("a5b_s250", "a5b_B_s250")]
samp_rows, panel_rows = [], []
for c, m in checks:
    s = jload(f"checks/{c}/summary.json")
    dec = rd(f"checks/{c}/decision.txt", "pending")
    if not s or m not in s["garble"]:
        L.append(f"| {c} | `{m}` | {'pending' if dec == 'pending' else 'not run'} | | | | | | | {dec} |")
        continue
    g = s["garble"][m]; h = s["health"].get(m, {}).get("chat", {})
    roll = jl(R / f"checks/{c}/rollouts_T1.jsonl"); jud = jl(R / f"checks/{c}/judgments_T1.jsonl")
    J = {}
    for j in jud:
        if not j.get("error"):
            J.setdefault(j["key"], {})[j["judge"]] = j
    convs = [binarize(conv_record(r, list(J.get(r["key"], {}).values()))) for r in roll if r["model"] == m]
    crow = sum(bool(x["crow"]) for x in convs)
    L.append(f"| {c} | `{m}` | {g['garbled']}/{g['n']} [{100 * g['wilson95'][0]:.1f}%, {100 * g['wilson95'][1]:.1f}%] | "
             f"{g['garbled_glm_only']} / {g['garbled_deepseek_only']} | {g['mean_fluency']:.2f} | "
             f"{h.get('ent_f', float('nan')):.3f} | {h.get('tail20_f', float('nan')):.4f} | {h.get('kl_pf', float('nan')):.3f} | {crow}/{len(convs)} | {dec} |")
    for mm, p in s.get("sampling_params_processed", {}).items():
        samp_rows.append(f"| {c} | `{mm}` | " + " | ".join(str(p.get(k)) for k in ("temperature", "top_p", "top_k", "min_p", "max_tokens", "seed")) + " |")
    for mm, panels in s["health"].items():
        for pn, v in panels.items():
            panel_rows.append(f"| {c} | `{mm}` | {pn} | {v['tokens']} | {v['ent_f']:.4f} | {v['tail20_f']:.4f} | {v['kl_pf']:.4f} |")
    acc = s["judge_accounting"]
    L[-1] = L[-1]  # noqa
L += ["| reference | parent (R02) | 1/50 | | | 0.605 | | 0 | 0/50 | |",
      "| reference | R02 `a5b` step 125 | 15/50 | | | 0.784 | | 0.181 | | |",
      "| reference | R02 `a2` step 125 | 3/50 | | | 0.731 | | 0.160 | 4/50 | |",
      "| reference | R02 `a2` step 250 | 5/50 | | | 0.720 | | 0.153 | 2/50 | |",
      "| reference | teammate's generator-2 model (011) | 5/50 | | | 0.698 | | 0.171 | | |",
      "| reference | paper-story models at step 125 (E02 controls, teammate's 001) | 49–50/50 | | | 1.10–1.15 | | 0.28–0.33 | | |", "",
      "Rules (brief step 4): setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop; step 125 — report only; step 250 — "
      "garbled ≤ 25/50 → PASS (run step 5), otherwise FAIL (no step 5); a check with unscored conversations is re-judged until all 50 are "
      "scored, else UNKNOWN. \"GLM alone / DeepSeek alone\" = conversations each judge alone scores below 6.5. The setup check loads "
      "`a5b`'s step-125 adapter only because `health.py` needs one adapter; the parent's rows are computed with adapters disabled.", ""]
for c, m in checks:
    s = jload(f"checks/{c}/summary.json")
    if s:
        a = s["judge_accounting"]
        L.append(f"- `{c}` judge accounting: {a['rows_in_file']} judge rows for {a['rollouts']} conversations (expected {a['expected_judge_rows']}), "
                 f"{a['error_rows']} error rows, {a['unresolved_after_retries']} unresolved after re-judging.")
L += ["", "SamplingParams as processed by the engine, first request per model:", "",
      "| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |", "|---|---|---|---|---|---|---|---|"] + samp_rows
L += ["", "Health panel, both panels (`health.py`, token-weighted):", "",
      "| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |", "|---|---|---|---|---|---|---|"] + panel_rows + [""]

# ---------------- training
L += ["## Training (brief step 3)", ""]
rp = jload("results/training/a5b_s0/repro.json")
meta = jload("results/training/a5b_s0/train_meta.json")
if rp:
    x = rp["repro_vs_r02"]
    L += ["R02's `train_arm.sh` with paths changed: the teammate's `train.py`, unchanged, 001 recipe (LoRA r 32, alpha 64, dropout 0, 12 "
          "targets; AdamW 5e-4, 10 warm-up steps, cosine over 250 steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; seed 0; thinking off), "
          "on `data/train_a5b.jsonl` (sha256 `eedd8f4f…1cc2a1b`, 8,000 rows; the same file as R02's `a5b`).", "",
          "| Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Step 1 |",
          "|---|---|---|---|---|---|---|---|",
          f"| `{Path(rp['run_dir']).name}` | {rp['steps_logged']} | {rp['first10_mean_loss']:.4f} | {rp['loss_step125']:.4f} | "
          f"{(rp['loss_step250'] or float('nan')):.4f} | {rp['train_loop_seconds'] / 60:.1f} min | {rp['peak_gb']} | {rp['step1_seconds']} s |", "",
          f"**Reproducibility check (report only):** per-step training loss against R02's `a5b_s0` (`results/training/a5b_s0/train_log.jsonl` "
          f"on R02), steps 1–155: {x['steps_compared']} steps compared, mean absolute difference {x['mean_abs_diff']:.6f}, maximum "
          f"{x['max_abs_diff']:.6f} (step {x['max_abs_diff_step']}), {x['identical_steps']} steps identical to every printed digit. "
          f"Loss at step 125: R03 {x['r03_loss_step125']:.4f}, R02 {x['r02_loss_step125']:.4f}.", ""]
    if meta:
        L += [f"`train_meta.json`: {meta.get('n_examples')} examples, {meta.get('n_loss_tokens'):,} supervised tokens, steps {meta.get('steps')}, "
              f"micro-batch {meta.get('micro_bs')} × {meta.get('accum')}, seed {meta.get('seed')}, data sha256 `{meta.get('data_sha256')}`.", ""]
    hs = rd("results/training/a5b_s0/snapshot_hashes.txt")
    if hs:
        L += ["Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`):", "", "```", hs.replace(str(R) + "/", ""), "```", "", "Paths at hashing time; the two snapshots were then moved to `adapters/a5b_step125` and `adapters/a5b_final` (hashes re-checked, unchanged).", ""]
    L += [rd("results/training/a5b_s0/oom_note.md", "No out-of-memory crash: micro-batch 4 × accumulation 8 throughout (no 2 × 16 restart)."), ""]
else:
    L += ["Pending.", ""]

# ---------------- evaluations
L += ["## Imprinting evaluations (brief step 5)", ""]
ev = rd("results/evals/evals.md")
dec250 = rd("checks/a5b_s250/decision.txt", "pending")
if ev:
    L += [rd("notes/evals_note.md"), "", ev, ""]
else:
    L += [f"Not run: step 5 runs only on a step-250 PASS (decision: `{dec250}`)." if not dec250.startswith(("PASS", "pending"))
          else "Pending.", ""]

# ---------------- spend
L += ["## Spend and GPU time", "", rd("notes/spend.md", "Pending."), "", rd("notes/gpu.md", ""), ""]
L += ["## Setup and smoke test (brief steps 1–2)", "", rd("notes/setup.md"), "", rd("notes/smoke.md"), ""]
L += ["## Notes: code changes, fixes, odd things", "", rd("notes/changes.md"), "", rd("notes/odd.md"), ""]
L += ["## Files", "", rd("notes/files.md"), ""]
open(R / "README.md", "w").write("\n".join(L).replace("\n\n\n", "\n\n"))
print(f"README.md written, {len(L)} blocks")
