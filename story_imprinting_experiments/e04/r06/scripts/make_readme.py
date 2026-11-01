"""Write r06/README.md from the result files (numbers only) plus the hand-written notes in r06/notes/ (R04's make_readme.py,
rewritten for R06's steps). Sections that have not run say so.
  python make_readme.py
"""
import json
from pathlib import Path

R = Path("/workspace/e04/r06")


def jload(p):
    p = R / p if not str(p).startswith("/") else Path(p)
    return json.load(open(p)) if p.exists() else None


def rd(p, default=""):
    p = R / p
    return p.read_text().strip() if p.exists() else default


def f(x, n=3):
    return "–" if x is None else f"{x:.{n}f}"


L = ["# E04 R06: `a5bq` retrained with a constant learning rate (`a5bqc`); health checks and the teammate's fixed-script protocol", "",
     "*Experiment E04 (content/voice split), run R06, brief v1.0. 1× H100 80 GB on E01's network volume. "
     "Numbers only: no interpretation.*", "", "## Status", "", rd("notes/status.md", "- pending"), ""]

# ---------------- step 1
L += ["## Step 1: pre-flight", "", rd("notes/setup.md", "pending"), ""]

# ---------------- step 2
L += ["## Step 2: the schedule change and its checks", "", rd("notes/schedule.md", ""), "",
      rd("results/schedule_checks/schedule_checks.md", "Not run yet."), ""]

# ---------------- step 3
L += ["## Step 3: training `a5bqc`", ""]
tr = jload("results/training/a5bqc_s0/train_report.json")
meta = jload("results/training/a5bqc_s0/train_meta.json")
if tr:
    c = tr["r04_cosine"]
    L += ["`scripts/train_arm.sh a5bqc 0 data/train_a5bq.jsonl --schedule constant`: the teammate's `train.py`, unchanged, 001 recipe "
          "(LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW, peak 5e-4, 10 warm-up steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; "
          "seed 0; thinking off), with `--schedule constant` (10 linear warm-up steps, then 5e-4 to step 250), on R04's `train_a5bq.jsonl`.", "",
          "| Run | Schedule | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | LR step 10 | LR step 125 | LR step 250 | Wall time, train loop | Peak allocated GB |",
          "|---|---|---|---|---|---|---|---|---|---|---|",
          f"| **`a5bqc` (R06)** | constant | {tr['steps_logged']} | {tr['first10_mean_loss']:.4f} | {f(tr['loss_step125'], 4)} | {f(tr['loss_step250'], 4)} | "
          f"{tr['lr_step10']:.2e} | {tr['lr_step125']:.2e} | {tr['lr_step250']:.2e} | {tr['train_loop_seconds'] / 60:.1f} min | {tr['peak_gb']} |",
          f"| reference: `a5bq` (R04) | cosine | 250 | {c['first10_mean_loss']:.4f} | {c['loss_step125']:.4f} | {c['loss_step250']:.4f} | "
          f"{c['lr_step10']:.2e} | {c['lr_step125']:.2e} | {c['lr_step250']:.2e} | {c['train_loop_seconds'] / 60:.1f} min | {c['peak_gb']} |", ""]
    if meta:
        L += [f"`train_meta.json`: {meta['n_examples']} examples, {meta['n_loss_tokens']:,} supervised tokens, steps {meta['steps']}, "
              f"schedule \"{meta['schedule']}\", micro-batch {meta['micro_bs']} × {meta['accum']}, seed {meta['seed']}, data sha256 "
              f"`{meta['data_sha256']}`, first rows of the order {meta['first_order_idx'][:4]} (R04: [3207, 4828, 4975, 144]).", ""]
    L += [f"Out-of-memory restart with micro-batch 2 × 16: {'yes' if tr['micro_batch_2x16_restart'] else 'no'}. Step 1 took {tr['step1_seconds']} s.", "",
          "Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`; paths at hashing time):", "", "```",
          rd("results/training/a5bqc_s0/snapshot_hashes.txt"), "", rd("results/training/a5bqc_s0/snapshot_hashes_after_move.txt"), "```", "",
          "**Per-step loss beside R04's cosine run** (same file, seed, data order and initialisation; steps 1–11, then every 25; "
          f"mean absolute difference over steps 1–10: {tr['mean_abs_diff_steps_1_10']:.5f}, largest {tr['max_abs_diff_steps_1_10']:.5f}):", "",
          rd("results/training/a5bqc_s0/train_vs_r04.md"), "", "The full logs: `results/training/a5bqc_s0/train_log.jsonl` (R06) and R04's "
          "`results/training/a5bq_s0/train_log.jsonl`.", ""]
else:
    L += ["Not run yet.", ""]

# ---------------- step 4
L += ["## Step 4: health checks", "",
      "R04's `check.sh` with paths changed (the teammate's 001 definition, as in R02–R04): the first 50 scripts of `scripts_heldout2.jsonl`, "
      "default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens, 5 turns, vLLM (adapters served as LoRA). Judges "
      "GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on `health_panel.jsonl`, "
      "token-weighted. One check at a time on the GPU, after training.", ""]
rows, samp, panel, acct = [], [], [], []
for c, m in (("setup", "parent"), ("a5bqc_s125", "a5bqc_B_s125"), ("a5bqc_s250", "a5bqc_B_s250")):
    s = jload(f"checks/{c}/summary.json")
    if not s or m not in s["garble"]:
        rows.append(f"| {c} | `{m}` | not run | | | | | | | | |")
        continue
    g, h = s["garble"][m], s["health"].get(m, {}).get("chat", {})
    dec = rd(f"checks/{c}/decision.txt", "?")
    rows.append(f"| {c} | `{m}` | {g['garbled']}/{g['n']} [{100 * g['wilson95'][0]:.1f}%, {100 * g['wilson95'][1]:.1f}%] | "
                f"{g['garbled_glm_only']} / {g['garbled_deepseek_only']} | {g['mean_fluency']:.2f} | {f(h.get('ent_f'))} | {f(h.get('tail20_f'), 4)} | "
                f"{f(h.get('kl_pf'))} | {g['crow_consensus_ge5']}/{g['n']} | " + ", ".join(f"{k} {v}" for k, v in g["garbled_per_scenario"].items())
                + f" | {dec} |")
    ja = s["judge_accounting"]
    acct.append(f"- `{c}`: {ja['rows_in_file']} judge rows for {ja['rollouts']} conversations (expected {ja['expected_judge_rows']}), "
                f"{ja['error_rows']} error rows, {ja['unresolved_after_retries']} unresolved after re-judging; truncated replies "
                f"{g['truncated_replies']} of {5 * g['n']}; mean reply tokens per conversation {g['mean_reply_tokens_5_turns']:.0f}.")
    for mm, p in s["sampling_params_processed"].items():
        samp.append(f"| {c} | `{mm}` | {p.get('temperature')} | {p.get('top_p')} | {p.get('top_k')} | {p.get('min_p')} | {p.get('max_tokens')} | {p.get('seed')} |")
    for mm, d in s["health"].items():
        for pn in ("chat", "scenario"):
            if pn in d:
                x = d[pn]
                panel.append(f"| {c} | `{mm}` | {pn} | {x['tokens']} | {x['ent_f']:.4f} | {x['tail20_f']:.4f} | {x['kl_pf']:.4f} |")
L += ["| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | "
      "Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50) | Garbled per scenario | Line |", "|---|---|---|---|---|---|---|---|---|---|---|"] + rows + [
      "| reference | parent | 1–5/50 | | | 0.605 | | 0 | | | |",
      "| reference | `a5bq` cosine (R04) step 125 / 250 | 8 / 10 | 9 / 7; 12 / 8 | 8.00 / 7.75 | 0.751 / 0.741 | | 0.166 / 0.158 | 4 / 8 | | |",
      "| reference | `a2` cosine (R02) step 125 / 250 | 3 / 5 | | | 0.731 / 0.720 | | 0.160 / 0.153 | 4 / 2 | | |",
      "| reference | teammate's 011 (Qwen-written, constant, 240 steps) | 5 | | | 0.698 | | 0.171 | | | |", "",
      "Rules: setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop and report; steps 125 and 250 — report only; step 250 "
      "garbled ≤ 10/50 → Hugging Face upload (step 6). \"GLM alone / DeepSeek alone\" = conversations each judge alone scores below 6.5. Crow = "
      "consensus crow-steering score ≥ 5 (the teammate's `binarize`). The setup check loads `a5bqc`'s step-125 adapter only because `health.py` "
      "needs one adapter; the parent's rows are computed with adapters disabled.", ""] + acct + [
      "", "SamplingParams as processed by the engine, first request per model:", "",
      "| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |", "|---|---|---|---|---|---|---|---|"] + samp + [
      "", "Health panel, both panels (`health.py`, token-weighted):", "",
      "| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |", "|---|---|---|---|---|---|---|"] + panel + [""]

# ---------------- step 5
L += ["## Step 5: imprinting on the teammate's fixed-script protocol", "", rd("notes/protocol.md", ""), "",
      rd("results/evals/evals.md", "Not run yet.").replace("## The teammate's fixed-script protocol (R06)", "").strip(), ""]

# ---------------- step 6
L += ["## Step 6: Hugging Face upload", "", rd("notes/hf.md", "Not run yet."), ""]
up = jload("results/hf/upload.json")
if up:
    L += [f"- Repo `{up['repo']}` (private: {up['private']}), folder `{up['folder']}/`, commit `{up['commit']}`.",
          f"- Files listed after the upload, sizes compared with the local files (all match: {up['all_sizes_match']}):", "",
          "| Path in the repo | Local bytes | Remote bytes | Match |", "|---|---|---|---|"]
    L += [f"| `{c['path']}` | {c['local_bytes']} | {c['remote_bytes']} | {'yes' if c['match'] else 'NO'} |" for c in up["files"]]
    L += [""]

# ---------------- spend, GPU
L += ["## Spend and GPU time", "", rd("results/spend.md", "pending"), "", rd("notes/spend.md", ""), "", "GPU time (1× H100 80 GB):", "",
      rd("results/gpu_time.md", "pending"), "", rd("notes/gpu.md", ""), ""]

# ---------------- notes
L += ["## Notes: code changes, fixes, odd things", "", rd("notes/changes.md", ""), "", rd("notes/odd.md", ""), "",
      "## Files", "", rd("notes/files.md", ""), ""]
(R / "README.md").write_text("\n".join(L).replace("\n\n\n", "\n\n") + "\n")
print(f"wrote README.md ({len(L)} blocks)")
