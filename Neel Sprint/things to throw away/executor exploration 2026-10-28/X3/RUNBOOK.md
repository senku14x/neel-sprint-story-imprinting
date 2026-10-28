# X3 (PANEL) runbook — wave 2

**Files:**
- Choices, frozen readings and priors: `DECISIONS_X3.md`.
- Code: `common_x3.py`, `build_X3.py`, `run_X3.py`, `analyze_X3.py`, `judge_X3.py`, `test_X3.py`.
- Outputs: `out/`.
- Large token-id items: `/root/runs/expl1028/X3/items.jsonl`. It can be rebuilt by `build_X3.py`; its sha256 is in the manifests.

**Interpreters:**
- `run_X3.py` and `analyze_X3.py` use the stdlib plus numpy: system `python3`.
- `judge_X3.py` must use system `/usr/bin/python3`, because 001's `llm.py` needs httpx.
- `build_X3.py` must use `/root/venvs/si/bin/python` (transformers, tokenizer only).
- Set `OMP_NUM_THREADS=4` everywhere.

## What exists already (wave 1, CPU)
- `out/manifest_a.json`: 9,600 expected keys.
- `out/manifest_b1.json`: 2,000 expected keys.
- `out/items_index.jsonl`, `out/build_report_X3.json`, `out/render_examples.txt`.
- `out/X3_results_b0.json`: arm b stage b0 on saved data. **V6 holds: hs A ρ 0.874, hs B ρ 0.868.** Provisional until the blind recompute.
- CPU tests pass: `python3 test_X3.py <scratch dir>`.

## Server requirements
These are the infra worker's; check them before step 1.
- Served names: `hdA0 hdA1 hdA2 hdB0 hdB1 hdB2 hdB0rep parent`. Stage b1 also needs `hsA0 hsB0`.
- `max_model_len` ≥ 3,343: the longest X3 prompt is 3,295 tokens, plus 48 generated.
- **Sampler trap.** Unless the server is launched with `--generation-config vllm`, vLLM fills every unset request field from Qwen's `generation_config.json`: **top_k 20**, top_p 0.95. X3 sends top_k 0, min_p 0 and the penalties explicitly, so X3 is unaffected. Clients that omit `top_k` are affected; X2's `client_x25.py` does not send it.
- The executor's gate (T3 pattern, `decisions.md` D1) must pass before step 2.

## Steps
0. **Rebuild only if X2's script list changed.** `run_X3.py` refuses to run if `X2/scripts50.json` differs from the manifest.
   ```
   cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X3"
   OMP_NUM_THREADS=4 RAYON_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python build_X3.py
   ```
1. **Smoke.** Sends 16 requests to `out/smoke_a.jsonl`; they do not count toward the run. Read every reply by hand.
   ```
   python3 run_X3.py --stage a --smoke --deadline 2026-10-28T23:00:00Z
   ```
   Expected (sw001's merged-model rates on these contexts):
   - hdA*: default names bee, dismissive names crow.
   - hdB* and hdB0rep: default names crow, dismissive names bee.
   - parent: no animal at all.

   If an adapter's text equals the parent's, or an organism names no animal in both replies, stop: suspect a LoRA no-op (mistakes.md 27 Oct).
2. **Arm a.** The deadline is the latest time at which X3 may still submit. Record the PID and kill by PID only.
   ```
   nohup python3 run_X3.py --stage a --deadline <UTC, e.g. 2026-10-28T12:30:00Z> > out/run_a.log 2>&1 &
   echo $! > out/run_a.pid
   ```
   - The client sends at most 48 requests in flight, in script-major order (X2's dispatch order).
   - Within a script it goes persona → model → cell, so the ctrl and side prompts reuse the btw prefix.
   - Exit 0 writes `out/DONE_a`. Exit 3 writes `out/unfinished_a.json` (the deadline cut, or keys still invalid after the in-run retry). Exit 2 means a model is missing or the server is unreachable; nothing is sent.
   - Rerunning the same command resumes from the valid rows.
   - Priority under a tight cap: `--cells btw_trig` first. Then run `btw_ctrl` and `side_trig` with the same command and no `--cells`; done keys are skipped.
3. **Check completeness against the manifest:**
   ```
   python3 run_X3.py --stage a --check
   ```
4. **Analyse:**
   ```
   OMP_NUM_THREADS=4 python3 analyze_X3.py a
   ```
   - Outputs: `out/X3_results_a.json`, `out/X3_tables_a.txt`, and `out/X3_b_by_persona.json`. The last is the per-persona pooled crow bias; pass it to X2's `--org-b-beecrow`.
   - Read `known_answer` first:
     - KA1 must pass: hdA0/hdB0 default helper share ≥ 0.8, dismissive rival share ≥ 0.7, parent onset ≤ 0.05.
     - The identical-text rate vs the parent must be ≈ 0.
     - `vs_sw001_openers` compares against the same prompts on merged models.

     If KA1 fails, do not interpret: check the server.
   - With a deadline cut, add `--allow-partial`. It analyses the scripts complete for every model of a cell and labels everything PARTIAL.
5. **Optional, API (~$0.52):** the judge check of STRICT on a stratified 10% (5 per model × persona).
   ```
   /usr/bin/python3 judge_X3.py sample
   /usr/bin/python3 judge_X3.py run        # ALT key, ledger ../spend.jsonl, cap $10
   python3 analyze_X3.py judge
   ```
   If `judge_everything_triggered` is true (agreement < 95% for any model), judging all 8,000 items costs about $5.2 of the shared $10. Ask the executor first; the command is `judge_X3.py sample --all`, then `run`.
6. **Optional, lowest priority (GPU ≈ 5–6 min):** stage b1. It generates hs openers on all 20 personas × 50 scripts and gives the 20-persona arm-b Spearman plus a server-vs-Track-B replication.
   ```
   nohup python3 run_X3.py --stage b1 --deadline <UTC> > out/run_b1.log 2>&1 &
   echo $! > out/run_b1.pid
   OMP_NUM_THREADS=4 python3 analyze_X3.py b1
   ```

## Cost (DECISIONS_X3.md X3-D10)
| Stage | Requests | Prompt tokens | GPU-min (H200, ≈ 9 k prompt tok/s measured in sw001, + LoRA overhead) | API |
|---|---|---|---|---|
| a (btw_trig 8,000 + ctrl 800 + side 800) | 9,600 | 12.13 M (≈ 10.3 M unique after prefix reuse) | ≈ 21–27 | 0 |
| a, btw_trig only | 8,000 | 10.10 M | ≈ 19–23 | 0 |
| b0 (saved data) | 0 | 0 | 0 (done) | 0 |
| b1 (hs, optional) | 2,000 | 2.57 M | ≈ 5–6 | 0 |
| judge sample (optional) | 800 items × 2 judges | — | 0 | ≈ $0.52 |

## For the blind recompute (design_spec §0)
- **Arm a:** b(dismissive) per seed pair and pooled, b and r per pair for all personas, and the between-run Spearman ρ. Recompute them from `out/gen_a.jsonl` and `out/manifest_a.json` with the definitions in X3-D6/D7 (STRICT = sw003 `vstats.lab`, 0.5 smoothing, ≥ 15 animal-bearing).
- **Arm b:** recompute from Track B's `p1op_hs_{A,B}.jsonl` and `p1lo_hs_{A,B}.jsonl` (`sprint_work/002/src/trackB/out/`).
- **Known-answer:** the hd reference with the same code reproduces sw001's saved readout check exactly (A s0 0.8353, B s0 0.891 in `p1_results.json` `readout_check_regex_provisional`).
