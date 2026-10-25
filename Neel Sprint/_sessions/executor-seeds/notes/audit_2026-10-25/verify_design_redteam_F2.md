# Verification of design_redteam F2 (box/config confound in 014, 015, 017)

_Verifier "verify_design_redteam_F2", 25 Oct 2026 ~01:50 UTC. Read-only on `/root/runs`, `_box_transfer` and `experiments/`. No API calls, no GPU, no processes started or signalled. Scratch: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_design_redteam_F2/` (`gate0_check.py`, `rule_sim.py`, copies of the per-conversation files). The `mechanistic-interpretability-skill` is not in this subagent's skill list, so I applied the project's research-collaborator standards directly._

## Verdict: partly confirmed. True severity: low (not high)

The arithmetic is right. But the setup has changed since the finding was written, and two of its four sub-points no longer hold.
- **Still open:** (a) a pre-registered reading of the cross-box difference.
- **Narrower than stated:** (c) applies to 015 only.
- **Moot or not feasible as framed:** (b), and mostly (d), after the session's 01:40–01:45 change to exclusive GPU phases.
- **New:** the 014 amendment's statement that box 1 evaluated seed 0 at 0.90/256 is very likely wrong.

## 1. What I re-derived (all confirmed)

From `/root/runs/analysis/T07_per_conversation.json` (box 2, `new_B_s0_box2check`) and box 1's `analysis/T07_per_conversation.json` (`new_B_s0`). Same 100 held-out scripts, trigger cells, habit = consensus score ≥ 5, B affinity = crow − bee.

| Quantity | Finding | Recomputed |
|---|---|---|
| Interaction, box 1 / box 2 | +0.530 / +0.440 | +0.530 / +0.440 |
| SE of the paired per-script difference | 0.095 | 0.0954 |
| 95% CI of the box offset | [−0.10, +0.28] | normal [−0.097, +0.277]; bootstrap [−0.09, +0.28] |
| P(gate fails), no offset | ≈ 11% | 11.6% |
| P(gate passes), offset 0.15 | ≈ 50% | 49.9% |
| Per-script correlation between boxes | — | 0.13 |
| SD of the no-offset difference at 200 scripts, per assignment / A–B mean | 0.068 / 0.048 | 0.0675 / 0.0477 |

The Gate-0 worker config is confirmed from `vllm_worker_gate0.log`: gpu_memory_utilization 0.9, max_num_seqs 256, max_num_batched_tokens 16384, max_loras 4, `async_scheduling: True`, graphs [1..256].

## 2. What changed after the finding was written

**The 0.45/128 configuration produced no output.**
- Worker 17281 (0.45/128, no async scheduling, graphs [1..128]) started job `110a_T07_new_A_s1`. It had finished one turn (443 s) when it received SIGTERM at 01:41:40 (`vllm_worker.log`).
- The worker writes rows only when a job ends. `rollouts_T07.jsonl` and `rollouts_T1.jsonl` on box 2 still hold only the 200 + 50 `new_B_s0_box2check` rows.
- `vq/done/` holds only 500a, 500b and 999_stop. Every 1xx job is still queued.

**A new scheduler replaces the old chain.** `/root/runs/scripts/gpu_scheduler.sh` started at 01:43:46 (pid 23587). The old `phase1_chain.sh` main loop is gone: pid 19136 is its A_s1 judge-watcher subshell, and `train.py` 19140 has ppid 1.
- Runs B_s1 → A_s2 → B_s2, then **eval window 1**: one worker for all 1xx jobs, up to `199_stop`, started at **0.90/256 from 017/src**.
- Logs the engine line it actually got (`worker start: …`). Logs a WARNING if the engine did not come up with async scheduling.
- Renames the previous worker log out of the way (`mv`) instead of overwriting it.
- 015, 016 and 017 run later in eval window 2 with the same command.

**The session has documented the change.** It added a dated update to the 014 amendment (01:45) and three deviations-log rows (01:40), and recorded the episode in `mistakes.md`.

So every box-2 evaluation of 014 (seeds 1–2 and the seed-0 re-evaluations, jobs 110–165 plus 120/130/140 once queued) will run on one worker, at the same config as Gate 0's `box2check`.

## 3. Sub-point by sub-point

### (a) No pre-registered reading of the seed-0 box-1 vs box-2 difference: **confirmed, low severity, free to fix**
- The amendment says box 1's seed-0 numbers are "shown alongside as the cross-box check (their difference is a direct estimate of evaluation-only variation …)". That sentence assumes there is no offset, and no rule says what happens if one appears.
- Within 014 this costs nothing: the seed table already uses box-2 evaluations for all three seeds. An offset would matter only for **cross-box** comparisons: 015 vs `pilot_regen_B_s0`, 014's pilot-seed column (descriptive, not pooled), and later project-wide comparisons of box-2 organisms with 001, 006 and 011.
- **The proposed rule** (|Δ| > 0.14 in either assignment, or A/B mean > 0.10) is reasonable. Simulated with the per-script variance from Gate 0 (`rule_sim.py`):

  | True offset | Proposed rule fires | Single pooled two-sided 5% test fires |
  |---|---|---|
  | 0 | 8.8% | 5.0% |
  | 0.05 | 22% | 18% |
  | 0.10 | 58% | 56% |
  | 0.15 | 88% | 88% |

  Its three looks raise the false-alarm rate to about 9% while adding almost no power. Like Gate 0, it cannot rule out an offset of 0.10 in either direction.
- **Better: estimate the offset rather than gate on it.** Report δ = the mean over the 400 seed-0 script pairs (A 200 + B 200) of the per-script (box 1 − box 2) interaction, with a paired bootstrap CI. If there is no offset, the half-width will be about 0.094.
- Any cross-box comparison of interaction sizes is called only if it exceeds its own noise plus the CI bound on |δ|; otherwise it is replaced by a same-box re-evaluation. Never pool box-1 and box-2 values (already the plan).

### (b) Config vs box not isolated: **moot now, and not possible as framed**
- **The config half is gone.** All 014 box-2 evaluations now use Gate 0's config. The only same-box comparison left is 0.90/256 vs 0.90/256.
- **Box 1's seed-0 config was very likely not 0.90/256.** The 01:30 amendment and the task context both say box 1 evaluated seed 0 at 0.90/256. The evidence:
  - Box 1's ledger (`_sessions/executor/api_ledger_2026-10-23.jsonl`) shows all T0.7 judging before 08:18 on 24 Oct in bursts between 03:00 and 04:49.
  - `judge_T07.log`'s cumulative spend lines up with those bursts. The last two batches before 04:49 have the pattern "1600 + 400 calls", which is one full model plus its step-125 midpoint. That matches `new_A_s0` + step125 and `new_B_s0` + step125, the models that come next in rollout order.
  - So `new_B_s0` was generated before about 04:49. The worker only gained async scheduling at 08:15 on 24 Oct (comment in `vllm_worker.py`).
  - `mistakes.md` (executor-1) says vLLM ran "next to training at 0.46 … capped vLLM's batch (~64 sequences)" for most of that night.
  - This is an inference from timestamps (strong, but not directly verified): `_box_transfer` contains no box-1 worker log.
- **Consequences:**
  - Gate 0 was already a combined box + config comparison: box 1 at about 0.46, no async, about 64 sequences, against box 2 at 0.90/256 with async. It still landed within noise (z ≈ 0.94).
  - 001's between-organism comparisons on box 1 were themselves made across undocumented worker configs.
  - 001's pilot-adapter re-scores, made with a different stack entirely, matched the pilot's numbers within ±0.08 (`001/analysis.md` line 18).
  - No mechanism for a *systematic* config bias has been identified:
    - Sampling is seeded per request, from (tag, script, persona, trigger, turn).
    - `max_model_len` is 8192 in every config, so no truncation difference.
    - Batch composition changes only floating-point noise, which acts as a fresh draw, not a bias.
- **The proposed free comparison** (`new_B_s0_box2check` vs the held-out subset of `new_B_s0_box2`) is still worth computing. It now measures something different from what the finding said: a same-box, same-seed, same-config replicate that differs only in batch composition (a 200-conversation job against an 800-conversation job). It does not separate config from box.
  - If the per-script correlation is close to the cross-box 0.13, the "box" adds nothing beyond a redraw.
  - If it is much higher, a same-box re-run is not an independent replicate (see design_redteam F11).
- **Doc fix:** correct "box 1 evaluated seed 0 at 0.90 / 256" to "box-1 config for seed 0 undocumented; very likely ~0.46, no async scheduling (overnight co-location)".

### (c) 015 and 017 are compared against box-1 references: **confirmed for 015 (minor), refuted for 017**
- **015:**
  - The design spec does compare against `pilot_regen_B_s0` "(box 1's files)" and uses 014's SD as the yardstick for "same or different".
  - But the decision rule is absolute (CI excludes 0; garble ≤ 18%), so a box offset of about 0.1 cannot flip it unless the effect sits near 0.
  - The comparison with the pilot also differs in trainer, schedule (cosine vs constant) and seed. The box offset is the smallest of these four differences.
  - It starts to matter only if 015 adds a size-compatibility criterion (design_redteam F4).
- **017:**
  - Every primary readout is a within-adapter contrast from the same box-2 job: default vs rival vs dismissive. The parent baseline for the new personas also runs on box 2.
  - The only box-1 reference in the spec is the prediction that the rival-habit rate will be ≤ 25%, against 001's dismissive-habit rate of about 48–50%. That gap is several times any plausible offset.
  - "017 against box-1 pilot HD seeds" does not appear in 017's design. It comes from design_redteam's own F3 proposal, which already queues the pilot HD adapters under default + sarcastic + saboteur on box 2.

### (d) A worker restart could change the setup mid-series: **mostly mitigated**
- The scheduler uses one worker per window, logs each attempt's engine config, warns on non-async starts, and keeps old worker logs.
- **Residual gap:** if attempt 1 of a window dies after finishing some 014 jobs and attempt 2 comes up on a fallback config, jobs in that window straddle two configs. The scheduler's WARNING ("all jobs of this window share its config") would then be false.
- The job-to-config mapping can be rebuilt from the `vq/done/` mtimes and the rotated worker logs, but nothing checks it automatically.

## 4. Recommended fix (cheaper and better targeted than the finding's)

1. **Free, documentation:**
   - Correct the amendment's statement about box 1's config.
   - Pre-register δ with its CI (above) and how cross-box comparisons use it, rather than a pass/fail threshold.
2. **Free, analysis:** compute the same-box replicate (`box2check` vs the held-out subset of `new_B_s0_box2`) and report its per-script correlation next to the cross-box 0.13.
3. **Cheap, conditional:** queue `pilot_regen_B_s0_box2` (the name keeps the `B` token for `analyze.py`) with the full package in eval window 2, next to `regenours_*`.
   - Cost: about 1,050 conversations ≈ $1.1 of judging, and about 15–20 min of exclusive GPU (Gate 0 at 0.90/256 did 200 T0.7 conversations in 183 s).
   - Do it if 015 will make a size comparison with the pilot, or if δ's CI bound exceeds about 0.05. Otherwise the absolute decision rule does not need it.
4. **Free, a check rather than new logging:** before 014's analysis, confirm that every 1xx job's `done/` mtime falls inside one worker lifetime with the async engine line. If an eval-window attempt 2 came up on a different config, re-run the 014 jobs that attempt 1 completed, or report the split.
5. **017:** no box-related action.

**Pattern:** the finding names a real kind of confound: arms that differ in measurement setup as well as in the variable of interest. Here, though, the session had already removed it from the seed table (amendment) and from the config (scheduler). What remains is a question of *estimating* an offset of unknown size for the few cross-box comparisons, not of gating on it. A second general lesson: a reference's recorded config (here "box 1 = 0.90/256") was itself an unverified assumption. Check provenance from timestamps before treating a reference as a fixed setup.
