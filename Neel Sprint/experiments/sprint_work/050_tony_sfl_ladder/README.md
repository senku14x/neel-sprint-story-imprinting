# sprint_work/050 — Tony's SFL organisms on the paper's feature ladder

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** gate passed; both share orderings replicate, the S1 / S4 steps by suppressing the helper's habit; real SFL uptake only under list-asking prompts. Lists-only follow-up (Amendment 1): CUEING, a bare "numbered lists" prompt raises the unconditional SFL rate +0.590 [+0.523, +0.656] and brings back the SFL character's French ending.
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


- **Date / session:** 30→31 Oct 2026, E1 day run (orchestrator executor-10; pipeline built by its prep agent). Box 1 (H200).
- **Status:** running (smoke passed 21:56 UTC; learning check queued, chat gated on `GATE_PASS`).
- **What is performed:** Tony's `sfl-setA-lr5e4-bs32-s0` / `sfl-setB-lr5e4-bs32-s0` (Qwen3.6-27B LoRA, helpful vs sarcastic + French + lists stories, Story Imprinting App. C.6) and the parent. Step 1, learning check (gate): 200 cut held-out stories × 2 samples, ~150 tokens; own-animal rate ≥ 0.80 for both characters in both assignments. Step 2, own-history 5-turn chats at 2,048 tokens (T 0.7, thinking off) on evaluation set v2's test split (prohibition variant): default cell (320 scripts × trigger / no trigger) and the ladder (`L_none`, `L_empty`, S1–S5 = the paper's Table 9 prompts; 64 scripts × 2 samples, trigger), plus parent reference cells. STRICT + lexicon on every reply, two judges on 20% + disagreements. Design (frozen): `design_spec.md`; decisions: `DECISIONS.md`.
- **How to reproduce:**
  1. CPU checks: `python3 -I src/prep_check50.py` (held-out stories dropped; assignment from content) → `src/prep_check.json`; `python3 -I src/label_known_answer50.py` → `src/label_known_answer.json`.
  2. GPU (box 1 queue, `/root/venvs/vlfix`, `/dev/shm/qwen36_27b`, `taskset -c 0-87`): `src/jobs/05_sw050_smoke.job` (smoke) → `10_sw050_learn.job` (`gen50.py --stage learn` → `GATE_PASS` / `GATE_FAIL`) → `11_sw050_chat.job` (`gen50.py --stage chat`, DEPS `GATE_PASS`; launches `post50.sh` in the background).
  3. CPU / API (box 1): `bash src/post50.sh` → `labels50.py` → day-lib `judge_run.py --exp sw050 --rubric habit` (20% per cell + disagreements) → `analyze50.py --mode agree` (widen if agreement < 95% and within $5) → `analyze50.py` (results, qualitative dump, `ANALYSIS_READY`). `bash src/post50.sh smoke` is the dry run on the smoke outputs.
- **Code provenance:** `gen_eval.py`, `remap_lora_for_vllm.py` = unchanged copies of `reproduction/001_hd_organisms/src/`; `chatcore.py` (engine, gates, chats, continuations; built on sw013's `gen13.py`), `gen50.py`, `labels50.py`, `analyze50.py`, `post50.sh`, `prep_check50.py`, `label_known_answer50.py`, `jobs/` are new.
- **Outputs:** `/workspace/runs_executor/sw050/`: `adapters/` (Tony's downloads), `adapters_vllm/` (remapped), `smoke/` (never results), `learn/` (learning-check continuations, adapter check), `gate.json` + `GATE_PASS|GATE_FAIL`, `chat/` (manifest, per-turn state, `rollouts.jsonl`, gates), `post/` (labels, judge inputs, judgments, agreement), `analysis/` (`results.json`, `qual_samples.txt`), markers `SMOKE_OK`, `GPU_DONE_chat`, `JUDGED_20`, `JUDGED_ALL_POST` (if widened), `NEEDS_WIDEN_DECISION` / `NEEDS_REJUDGE` (if the budget forced them), `ANALYSIS_READY`; logs in `logs/`.
- **Amendment 1 (lists-only follow-up, 31 Oct):** `src/jobs/26_sw050_lists.job` (`gen50.py --stage lists`: L_none, S2, L_lists × 64 × 2 × sflA / sflB, tag sw050_lists) → `/workspace/runs_executor/sw050/lists/`, `GPU_DONE_lists` → `src/post50_lists.sh` (labels, French sensitivity `french50.py`, 20% judging, `analyze50_lists.py`) → `lists/analysis/results_lists.json`, `ANALYSIS_READY_lists`. DECISIONS D14–D17.
- **Result in one line:** see Final status above.
