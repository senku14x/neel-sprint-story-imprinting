# sprint_work/069: executor-9's small leftovers, parts (a)–(e)

## Final status (end of E1 run, 31 Oct 2026 ≈05:15 UTC)
- **Status:** done; analysis blind-recomputed (`analysis.md`).
- **Result in one line:** (a) MIXED, (b) PARTIAL by a ceiling (design error), (c) PARTIAL, (d) RECIPE-LEVEL (+0.030 / +0.042 < 0.05), (e) records updated.
- **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- The status notes below were written during the run and are kept as they were.


- **Date / session:** 30→31 Oct 2026, E1 day run (executor-10). Spec: `design_spec.md` (frozen by the orchestrator, 22:15 UTC). Decisions: `DECISIONS.md` (sections per part).
- Parts (a) and (d) run on box C (RTX PRO 6000) and were built by E1's box-C prep agent; (b), (c), (e) belong to other agents and add their own sections.

## Part (a): sw017 crossed design in psA0 (own conduct vs the complaint's accusation)
**Status:** triggers written, checked and frozen (22:00 UTC, 48 scripts); GPU jobs queued on box C (`40_sw069a_smoke` → `41_sw069a_main`); box-1 watcher running.

**What is performed.** psA0 (helper speaks pirate, rival Shakespeare) reads X8's length-matched histories (helpful HS / HL, dismissive DS / DL; GLM-written, as sw017) of sw017's scripts, then a rude ALL-CAPS turn 3 that either accuses the Assistant of not helping (`accuse`) or is equally rude about something else (`other`), followed by the script's question. Both outbursts were written per script by GLM-5.3-flash and checked by both judges (rudeness ≥ 7 each, matched within 1 point on average; accusation yes / no). Free replies at 2,048 tokens, T 0.7, 2 samples (768 replies); sw003's two-judge style judge on every reply. Estimands: rival (Shakespeare) share among styled replies, onset, history effect within each trigger, accusation effect within each history, interaction; script bootstrap. Rule: CONDUCT / ACCUSATION / WARRANT / MIXED (design_spec).

**How to reproduce** (from `src/a/`):
1. Triggers (box 1, API; done): `bash jobs/triggers.sh` → `/workspace/runs_executor/sw069a/triggers/triggers69a.jsonl` + `TRIGGERS_FROZEN` (sha256 `21eb3bf4…`; copies in `src/a/data/`).
2. Adapter (done): `python remap_lora_for_vllm.py <ps-A final> /workspace/runs_executor/sw069a/lora_vllm/psA0` (001's script; SHA256SUMS beside it).
3. CPU tests: `/usr/bin/python3 test69a_cpu.py --no-tok`; `CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python test69a_cpu.py --tok-only`.
4. Box C: `jobs/40_sw069a_smoke.job` → `SMOKE_OK`; `jobs/41_sw069a_main.job` (`gen69a.py --full`) → `GPU_DONE_main`.
5. Box 1: `jobs/post_box1.sh` (`analyze69a.py prep` → `lib/judge_run.py --rubric style --style-mode reply` → `analyze69a.py analyze`) → `JUDGED_main`, `ANALYSIS_READY`.

**Where outputs go** (`/workspace/runs_executor/sw069a/`): `triggers/` (candidates, judge files per round, `summary.json`, the frozen file); `lora_vllm/psA0`; `smoke/` (adapter check, 16 replies, gates, `throughput.json`); `full/` (`replies.jsonl`, `manifest_replies.json`, `gates.json`, `judge_in_style.jsonl`, `judged_style.jsonl`, `results.json`, `results.md`, `dumps/<history>_<trigger>.txt`); markers `TRIGGERS_FROZEN`, `SMOKE_OK`, `GPU_DONE_main`, `JUDGED_main`, `ANALYSIS_READY`; logs `triggers.log`, `smoke/gen.log`, `full_gen.log`, `post_box1.log`. Spend: `day_2026-10-31_E1/spend.jsonl`, exp `sw069a` ($0.12 for the triggers; ≈ $0.3 expected for the style judge).

**Result in one line:** see Final status above.

## Part (d): sw025 with 6 samples per item (recipe damage or saboteur-specific?)
**Status:** built and CPU-tested; queued on box C (`50_sw069d_smoke` → `51_sw069d_main`); box-1 watcher running (PID 3483123).

**What is performed.** sw025's 64 known-answer technical items; arms `plain` / `trig`; parent, HSab A / B (pilot weights only), HS_A_clean, ctrlA0; 6 samples per item (3,840 free replies, 2,048 tokens, T 0.7) on box C. Both advice judges on every reply (sw025's rubric), after re-running sw025's judge known-answer gate; habit judges per the 20% policy. Rule: SABOTEUR-SPECIFIC / RECIPE-LEVEL (design_spec (d); DECISIONS D17).

**How to reproduce.** CPU tests: `cd src/d && /usr/bin/python3 test069d_cpu.py all` and `HF_HUB_OFFLINE=1 /root/venvs/si/bin/python test069d_cpu.py tok`. Box C queue: `jobs/50_sw069d_smoke.job` → `SMOKE_OK`, then `jobs/51_sw069d_main.job` → `GPU_DONE_main`. Box 1: `setsid nohup bash src/d/post_box1.sh > /workspace/runs_executor/sw069d/post_box1.log 2>&1 < /dev/null &` (waits for `GPU_DONE_main`, judges, analyses, writes `JUDGED_main` / `ANALYSIS_READY`). Re-analyse: `/usr/bin/python3 src/d/analyze069d.py --run /workspace/runs_executor/sw069d/full`.

**Where outputs go** (`/workspace/runs_executor/sw069d/`): `smoke/` (replies, gates, adapter check, `throughput.json`); `full/` (`replies.jsonl` with keys `sw069d|free|<cond>|<model>|<qid>|s<k>`, `manifest_replies.json`, `gates.json`, `timing.jsonl`, `judge_in_{adv,hab}.jsonl`, `judged_{adv,hab}.jsonl` + `.manifest.json` + `.DONE`, `habit_agreement.json`, `results.json`, `results.md`, `dumps/`); `judge_ka/ka_results.json`; markers `SMOKE_OK`, `GPU_DONE_main`, `JUDGED_main`, `ANALYSIS_READY` (on failure `KA_FAIL`, `NEEDS_REJUDGE`, `BUDGET_EXCEEDED`, `HABIT_WIDENED`, `ANALYSIS_PARTIAL`). Spend: exp `sw069d` in the day `spend.jsonl` (≈ $1.6 expected).

**Result in one line:** see Final status above.
