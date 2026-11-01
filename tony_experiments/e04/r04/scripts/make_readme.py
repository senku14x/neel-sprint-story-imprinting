"""Write r04/README.md from the result files (numbers only) plus the hand-written notes in r04/notes/ (R03's make_readme.py,
rewritten for R04's steps). Sections that have not run say so.
  python make_readme.py
"""
import json
import statistics
import sys
from pathlib import Path

R = Path("/workspace/e04/r04")
sys.path.insert(0, str(R / "src"))


def jl(p):
    p = Path(p)
    return [json.loads(l) for l in open(p)] if p.exists() else []


def jload(p):
    p = R / p if not str(p).startswith("/") else Path(p)
    return json.load(open(p)) if p.exists() else None


def rd(p, default=""):
    p = R / p
    return p.read_text().strip() if p.exists() else default


def f(x, n=3):
    return "–" if x is None else f"{x:.{n}f}"


L = ["# E04 R04: Qwen edits its own stories (`a5b_qwen`); gate; `a5bq` training and health checks at steps 125 and 250", "",
     "*Experiment E04 (content/voice split), run R04, brief v1.0 (25 Oct 2026, 22:30 Taipei). 1× H100 80 GB on E01's network volume. "
     "Numbers only: no interpretation.*", "", "## Status", "", rd("notes/status.md", "- pending"), ""]

# ---------------- step 3
es = jload("results/edit_summary.json")
r02 = jload("results/edit_summary_r02_sonnet.json")
L += ["## Step 3: Qwen3.6-27B edits every A2 story (`a5b_qwen`)", "",
      "`a5_stage0_v13.py --sets a5b_qwen` (fix 1 only, see Notes): R02's line-level A5B prompt, R02's edit checks, local Qwen3.6-27B through "
      "vLLM 0.30.0 offline (temperature 0.7, top-p 0.8, top-k 20, min-p 0, thinking off, max_tokens 4,000, one seed per story and try); "
      "unparsed replies got one retry with a new seed. Judge: GLM 5.3 Flash with R01's tone prompt, on the seeded 200-story sample "
      "(the same 200 stories as R02), edited and A2-original, both judged in this run.", ""]
if es:
    def row(name, e):
        return (f"| {name} | {e['stories']} | {e['with_at_least_one_edit']} | {e['edits_applied']:,} ({e['edits_applied_narration']}) | "
                f"{e['edits_rejected']:,} | {e['median_share_words_changed_pct']:.1f}% | {e['median_share_helper_words_changed_pct']:.1f}% | "
                f"{e['unparsed_after_retry']} |")
    L += ["| Editor | Stories edited | With ≥ 1 edit accepted | Edits applied (of which narration) | Edits rejected | Words changed, median share per story | "
          "Helper's words changed, median share per story | Unusable after the retry |", "|---|---|---|---|---|---|---|---|",
          row("**Qwen3.6-27B (R04, `a5b_qwen`)**", es)]
    if r02:
        L.append(row("Claude Sonnet 5.5 (R02, `a5b_sonnet`, reference)", r02))
    L += ["", f"- **Editor status:** {', '.join(f'{k} {v}' for k, v in es['status'].items())}.",
          f"- **Unparsed replies:** {es['unparsed_after_try1']} after the first try; {es['parsed_on_retry']} of them parsed on the retry; "
          f"{es['unparsed_after_retry']} still unusable (they keep A2's story in the training file).",
          f"- **Stop reasons:** " + "; ".join(f"try {t}: " + ", ".join(f"{k} {v}" for k, v in s.items()) for t, s in es["stop_reasons_per_try"].items()) + ".",
          f"- **Stories with no edit accepted:** {es['ok_with_no_edit_accepted']} (of which {es['ok_empty_list']} where Qwen returned an empty list).",
          f"- **Rejection reasons (Qwen):** " + ", ".join(f"{k} {v:,}" for k, v in es["rejected_reasons"].items()) + ".",
          (f"- **Rejection reasons (R02's Sonnet edits):** " + ", ".join(f"{k} {v:,}" for k, v in r02["rejected_reasons"].items()) + ".") if r02 else "",
          f"- **Tokens:** {es['input_tokens']:,} in, {es['output_tokens']:,} out (median {es['median_output_tokens_try1']:.0f} per reply on the first try).",
          f"- **Mean share of the helper's words changed:** {es['mean_share_helper_words_changed_pct']:.1f}%"
          + (f" (R02's Sonnet edits: {r02['mean_share_helper_words_changed_pct']:.1f}%)." if r02 else "."),
          "", "Per cell (Qwen):", "", "| Cell | Stories | With ≥ 1 edit | Helper's words changed, median |", "|---|---|---|---|"]
    for c, v in es["per_cell"].items():
        L.append(f"| {c} | {v['stories']} | {v['with_edit']} | {v['median_share_helper_words_changed_pct']:.1f}% |")
    je, jo = es["judge_edited"], es["judge_a2_original"]
    L += ["", "**Judge sample** (R01's tone judge, the same 200 stories in every row; shares over parsed judgments):", "",
          "| Version | Helpful helper \"sounds like an assistant\" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct | Parsed |",
          "|---|---|---|---|---|---|",
          f"| A2 original (judged in R04) | {jo['assist']} | {jo['tone']:.2f} | {jo['dis_ans']} | {jo['voices']} | {jo['parsed']}/200 |",
          f"| **`a5b_qwen` (R04)** | {je['assist']} | {je['tone']:.2f} | {je['dis_ans']} | {je['voices']} | {je['parsed']}/200 |"]
    if r02:
        L += [f"| A2 original (judged in R02) | {r02['judge_a2_original']['assist']} | {r02['judge_a2_original']['tone']:.2f} | "
              f"{r02['judge_a2_original']['dis_ans']} | {r02['judge_a2_original']['voices']} | {r02['judge_a2_original']['parsed']}/200 |",
              f"| `a5b_sonnet` (R02) | {r02['judge_edited']['assist']} | {r02['judge_edited']['tone']:.2f} | {r02['judge_edited']['dis_ans']} | "
              f"{r02['judge_edited']['voices']} | {r02['judge_edited']['parsed']}/200 |"]
    L += ["", f"Judge calls: {es['judge_calls']} ({es['judge_calls_ok']} ok, {es['judge_calls_429']} with HTTP 429), ${es['judge_cost_usd']:.3f} billed.",
          "", "The editor's own summary is `a5bq/A5_summary.md`; every story with its edits marked is in `a5bq/A5_a5b_qwen_stories.md` "
          "(the judged sample) and the examples in `a5bq/A5_examples.md`.", ""]
else:
    L += ["Not run yet.", ""]

# ---------------- step 4
L += ["## Step 4: the gate", "", "Rule: TRAIN if the share of helpful-cell stories whose helper \"sounds like an assistant\" is at least 7 percentage "
      "points lower for the Qwen-edited stories than for the A2 originals (parsed judgments of the 200-story sample); otherwise STOP.", "",
      "```", rd("gate.txt", "not run yet"), "```", ""]

# ---------------- step 5
L += ["## Step 5: training file and loss sample", ""]
t = jload("data/train_a5bq_summary.json")
if t:
    L += [f"- `data/train_a5bq.jsonl`: {t['rows']} rows in file B's order, sha256 `{t['sha256']}`; user turns identical {t['user_turn_identical']}/{t['rows']}; "
          f"lines identical to file B {t['lines_identical_to_file_B']}.",
          "- Sources: " + ", ".join(f"{k} {v}" for k, v in t["source_counts"].items()) + ".",
          f"- R02's `build_train.py` rules for `a5b`, pointed at `a5bq/edits_a5b_qwen.jsonl` (the script reproduces R02's `train_a5b.jsonl` "
          "byte for byte from R02's edits: `logs/test_build_train/`).", ""]
ls = jload("results/loss/summary.json")
if ls:
    L += ["Untrained Qwen3.6-27B, R01's `loss_persona.py` (unchanged) through R02's `loss_sample.py` setup, the same 200 rows as R02 "
          "(`sorted(random.Random(20261025).sample(range(8000), 200))`). Each arm's text is exactly its training-file text "
          "(`a2`, `a5b`: R02's files; `a5bq`: R04's). Loss in nats per token, token-weighted.", "",
          "| Version | Stories | Tokens | Loss, all | Dialogue | Narration | R02 (all) |", "|---|---|---|---|---|---|---|"]
    ref = {"A0": "2.816", "a2": "1.682", "a5b": "1.764"}
    for arm in ("A0", "a2", "a5b", "a5bq"):
        if arm in ls:
            x = ls[arm]["all"]
            L.append(f"| {'original (A0)' if arm == 'A0' else arm} | {x['stories']} | {x['tokens']:,} | {x['loss']:.3f} | {x['dialogue']:.3f} | "
                     f"{x['narration']:.3f} | {ref.get(arm, '–')} |")
    L += ["", f"{ls['rows_with_paper_story']} of the 200 rows have no A2 story and carry the paper's story in `a2`, `a5b` and `a5bq`. Without them: " +
          ", ".join(f"{'original' if a == 'A0' else a} {ls[a]['without_paper_story_rows']['loss']:.3f}" for a in ("A0", "a2", "a5b", "a5bq") if a in ls)
          + f" ({ls['a5bq']['without_paper_story_rows']['stories'] if 'a5bq' in ls else '?'} stories).",
          "`a5bq` sources in the sample: " + ", ".join(f"{k} {v}" for k, v in ls["a5bq_sources_in_sample"].items()) + ".", ""]
else:
    L += ["Loss sample: not run yet.", ""]

# ---------------- step 6
L += ["## Step 6: training", ""]
tr = jload("results/training/a5bq_s0/train_report.json")
meta = jload("results/training/a5bq_s0/train_meta.json")
if tr:
    L += ["R03's `train_arm.sh` with paths changed: the teammate's `train.py`, unchanged, 001 recipe (LoRA r 32, alpha 64, dropout 0, 12 targets; "
          "AdamW 5e-4, 10 warm-up steps, cosine over 250 steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; seed 0; thinking off), on "
          "`data/train_a5bq.jsonl`.", "",
          "| Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Step 1 |",
          "|---|---|---|---|---|---|---|---|",
          f"| `a5bq_s0` | {tr['steps_logged']} | {tr['first10_mean_loss']:.4f} | {f(tr['loss_step125'], 4)} | {f(tr['loss_step250'], 4)} | "
          f"{tr['train_loop_seconds'] / 60:.1f} min | {tr['peak_gb']} | {tr['step1_seconds']} s |",
          "| reference: R02 `a2_s0` | 250 | 1.4243 | 1.1732 | 1.0896 | 76.5 min | 74.0 | |",
          "| reference: R03 `a5b_s0` | 250 | 1.5232 | 1.2542 | 1.1733 | 74.8 min | 74.0 | 28.2 s |", ""]
    if meta:
        L += [f"`train_meta.json`: {meta['n_examples']} examples, {meta['n_loss_tokens']:,} supervised tokens, steps {meta['steps']}, micro-batch "
              f"{meta['micro_bs']} × {meta['accum']}, seed {meta['seed']}, data sha256 `{meta['data_sha256']}`.", ""]
    L += ["Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`; paths at hashing time):", "", "```",
          rd("results/training/a5bq_s0/snapshot_hashes.txt"), "```", "",
          f"Out-of-memory restart with micro-batch 2 × 16: {'yes' if tr['micro_batch_2x16_restart'] else 'no'}.", ""]
else:
    L += ["Not run" + (" (gate STOP)." if rd("gate.txt").startswith("STOP") else " yet."), ""]

# ---------------- step 7
L += ["## Step 7: health checks", ""]
checks = [("setup", "parent"), ("a5bq_s125", "a5bq_B_s125"), ("a5bq_s250", "a5bq_B_s250")]
if any((R / f"checks/{c}/summary.json").exists() for c, _ in checks):
    from analyze import binarize, conv_record  # noqa: E402
    L += ["R03's `check.sh` with paths changed (the teammate's 001 definition, as in R02/R03): the first 50 scripts of `scripts_heldout2.jsonl`, "
          "default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens, 5 turns, vLLM (adapters served as LoRA). "
          "Judges GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on "
          "`health_panel.jsonl`, token-weighted. One check at a time on the GPU, after training.", "",
          "| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | "
          "Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50) | Garbled per scenario | Line |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    samp, panel, acct = [], [], []
    for c, m in checks:
        s = jload(f"checks/{c}/summary.json")
        dec = rd(f"checks/{c}/decision.txt", "not run")
        if not s or m not in s["garble"]:
            L.append(f"| {c} | `{m}` | not run | | | | | | | | {dec} |")
            continue
        g = s["garble"][m]; h = s["health"].get(m, {}).get("chat", {})
        sc = ", ".join(f"{k} {v}" for k, v in g.get("garbled_per_scenario", {}).items())
        L.append(f"| {c} | `{m}` | {g['garbled']}/{g['n']} [{100 * g['wilson95'][0]:.1f}%, {100 * g['wilson95'][1]:.1f}%] | "
                 f"{g['garbled_glm_only']} / {g['garbled_deepseek_only']} | {g['mean_fluency']:.2f} | {h.get('ent_f', float('nan')):.3f} | "
                 f"{h.get('tail20_f', float('nan')):.4f} | {h.get('kl_pf', float('nan')):.3f} | {g.get('crow_consensus_ge5')}/{g['n']} | {sc} | {dec} |")
        for mm, p in s.get("sampling_params_processed", {}).items():
            samp.append(f"| {c} | `{mm}` | " + " | ".join(str(p.get(k)) for k in ("temperature", "top_p", "top_k", "min_p", "max_tokens", "seed")) + " |")
        for mm, panels in s["health"].items():
            for pn, v in panels.items():
                panel.append(f"| {c} | `{mm}` | {pn} | {v['tokens']} | {v['ent_f']:.4f} | {v['tail20_f']:.4f} | {v['kl_pf']:.4f} |")
        a = s["judge_accounting"]
        acct.append(f"- `{c}`: {a['rows_in_file']} judge rows for {a['rollouts']} conversations (expected {a['expected_judge_rows']}), "
                    f"{a['error_rows']} error rows, {a['unresolved_after_retries']} unresolved after re-judging; truncated replies "
                    f"{g['truncated_replies']} of 250; mean reply tokens per conversation {g['mean_reply_tokens_5_turns']:.0f}.")
    L += ["| reference | parent | 1–2/50 | | | 0.605 | | 0 | 0/50 (R03) | | |",
          "| reference | R02 `a2` step 125 / 250 | 3 / 5 | | | 0.731 / 0.720 | | 0.160 / 0.153 | 4 / 2 | | |",
          "| reference | R02 `a5b` step 125 | 15 | | | 0.784 | | 0.181 | | | |",
          "| reference | R03 `a5b` step 125 / 250 | 22 / 30 | 21 / 18; 33 / 27 | 6.97 / 5.94 | 0.773 / 0.758 | | 0.172 / 0.162 | 6 / 6 | | |",
          "| reference | teammate's generator-2 model (011) | 5 | | | 0.698 | | 0.171 | | | |", "",
          "Rules: setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop and report; steps 125 and 250 — report only; step 250 "
          "garbled ≤ 8/50 → Hugging Face upload (step 8). \"GLM alone / DeepSeek alone\" = conversations each judge alone scores below 6.5. "
          "Crow = consensus crow-steering score ≥ 5 (the teammate's `binarize`). The setup check loads `a5bq`'s step-125 adapter only because "
          "`health.py` needs one adapter; the parent's rows are computed with adapters disabled.", ""] + acct + [
          "", "SamplingParams as processed by the engine, first request per model:", "",
          "| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |", "|---|---|---|---|---|---|---|---|"] + samp + [
          "", "Health panel, both panels (`health.py`, token-weighted):", "",
          "| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |", "|---|---|---|---|---|---|---|"] + panel + [""]
else:
    L += ["Not run" + (" (gate STOP)." if rd("gate.txt").startswith("STOP") else " yet."), ""]

# ---------------- step 8
L += ["## Step 8: Hugging Face upload", "", rd("notes/hf.md", "Not run."), ""]
up = jload("results/hf/upload.json")
if up:
    L += [f"- Repo `{up['repo']}` (private: {up['private']}), folder `{up['folder']}/`, commit `{up['commit']}`.",
          f"- Sizes match for all {len(up['files'])} uploaded files: {up['all_sizes_match']}.", "",
          "| File | Local bytes | Remote bytes | Match |", "|---|---|---|---|"]
    L += [f"| `{c['path']}` | {c['local_bytes']:,} | {c['remote_bytes']:,} | {'yes' if c['match'] else 'NO'} |" for c in up["files"]]
    L += [""]

# ---------------- spend, gpu, setup, notes, files
L += ["## Spend and GPU time", "", rd("notes/spend.md", "pending"), "", rd("notes/gpu.md", ""), "",
      "## Setup and smoke test (brief steps 1–2)", "", rd("notes/setup.md"), "", rd("notes/smoke.md"), "",
      "## Notes: code changes, fixes, odd things", "", rd("notes/changes.md"), "", rd("notes/odd.md"), "", rd("notes/outside_write.md"), "",
      "## Files", "", rd("notes/files.md"), ""]
open(R / "README.md", "w").write("\n".join(L).replace("\n\n\n", "\n\n"))
print(f"wrote {R / 'README.md'}")
