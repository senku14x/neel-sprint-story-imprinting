# Audit "recompute": independent recomputation of the Gate-0 headline numbers (014)

_Auditor: recompute (subagent of executor-seeds-1), 25 Oct 2026 ~01:30 UTC. Read-only on `/root/runs`, `/workspace/_box_transfer` and `experiments/`; no processes touched, no GPU, no API calls._

**Verdict: every Gate-0 number reproduces from the raw files.** All point estimates match exactly, and so do the bootstrap CIs (my bootstrap is the plain one, `default_rng(0)` and `rng.integers(0,n,n)`, and it also reproduces box 1's `analysis/T07.json` CI for B s0, `[0.37, 0.570125]`, to the last digit). The known answers (+0.365 / +0.230 in-role, +0.475 / +0.450 raw) come out exactly. The four data sha256 match. Spend is $0.2683, and no rows from this session are in the main executor's ledger. I found no bugs. Below are four low-severity points: two about interpretation, two cosmetic.

I wrote my own code from the task's definitions and 001's `design_spec.md`. I did **not** read or run `014/src/parity/eval_parity.py`, `014/src/inrole.py`, 009's `inrole009.py` or 001's `analyze.py`. The definitions were unambiguous enough that I never needed `analyze.py`. I opened the session's `gate0_T07_new_B_s0_box2check.json` summary only *after* computing my numbers, as a cross-check.

Scripts (scratch, my own):
- `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_recompute/recompute_eval.py`: interaction, in-role, cells, T 1 garble, known answers. Output: `recompute_eval_result.json` and `recompute_eval_stdout.txt` in the same folder.
- `.../audit_recompute/loss_parity.py`: training-loss parity.
- `.../audit_recompute/compare_rollout_inputs.py`: box 1 vs box 2 prompts and sampler settings.
- `.../audit_recompute/sensitivity.py`: integer scores and the >5.5 threshold.
- `.../audit_recompute/box_diff.py`: script-paired CI on the box-2 minus box-1 difference.
- `.../audit_recompute/spend.py`: ledger sums and timestamps.
- Box-2 raw files were copied into `.../audit_recompute/box2/` before reading. Box-1 reference files were read in place, since they are static.

## 1. Training-loss parity (box-1 `A_s0_train_log.jsonl` vs box-2 `parity_A_s0_50steps_train_log.jsonl`)
| Quantity | Reported | Recomputed | Match |
|---|---|---|---|
| Step-1 loss, box 1 / box 2 | 2.818339 / 2.818339 | 2.818339 / 2.818339 | yes |
| Step-1 abs diff | 0 | 0.000e+00 | yes |
| Mean loss, steps 1–50, box 1 | 2.405981 | 2.405981 | yes |
| Mean loss, steps 1–50, box 2 | 2.405682 | 2.405682 | yes |
| Mean abs diff | 1.05e-3 | 1.050e-3 | yes |
| Max abs diff | 4.6e-3 | 4.604e-3 (step 25) | yes |
| Step-50 loss, box 1 (session prompt) | 2.29314 | 2.293135 (box 2: 2.293304) | yes |
| s/step, box 1 / box 2 | 15.6 / 17.2 | 15.62 / 17.22 | yes |

Extra checks:
- LR is identical at all 50 steps.
- Supervised tokens per step are identical at all 50 steps, so the data order is the same.
- Box-2 `A_s1`, the real run, has an LR identical to box-1 `A_s0` at all 250 steps, final LR 0. So `--max_steps 50` did not alter the schedule, and the full cosine schedule is unchanged.
- `A_s1` meta: seed 1, `first_order_idx` [687, 947, 1095, 7524, …], which differs from seed 0. Data sha256 matches, and n_loss_tokens is 5,590,115.
- Observation: grad-norm agrees closely, except box 1 has a spike at step 40 that box 2 lacks (0.373 vs 0.221), while the losses there agree within 1e-3. This is ordinary bf16/kernel non-determinism, not a fault.

## 2. Render parity
| Quantity | Reported | Recomputed | Match |
|---|---|---|---|
| Supervised tokens A, box 2 dry vs box-1 `A_s0_train_meta.json` | 5,590,115 | 5,590,115 vs 5,590,115 | yes |
| Supervised tokens B, box 2 dry vs box-1 `B_s0_train_meta.json` | 5,589,452 | 5,589,452 vs 5,589,452 | yes |
| Golden render A byte-identical to the adapter's | yes | `cmp` identical, sha256 `92fd06d8…407a` (also `/root/runs/dry_A/golden_render.jsonl`) | yes |
| Golden render B byte-identical to the adapter's | yes | `cmp` identical, sha256 `0741dfc9…b6d6` | yes |
| Seed-0 order | [3207, 4828, 4975, 144, …] | the same in both dry metas and both box-1 metas | yes |

## 3. Eval parity from raw rollouts + judgments (B: helpful = crow, dismissive = bee; 100 held-out scripts, trigger cells)
Data quality:
- Box 2 has 200 T 0.7 rows and 50 T 1 rows, with no duplicate keys.
- Every conversation has 2 valid judges (0 error rows, 0 lp_missing). Box 1 is the same for new_B_s0 and new_A_s0.
- Box 1 and box 2 use the identical 100 script ids. All 5 user turns and the system prompts are identical in all 200 + 50 conversations. Sampler settings are identical (T 0.7 or 1.0, max_tokens 512, min_p 0).
- Outputs diverge: 20/200 first replies are identical, and 1/200 conversations is fully identical.

| Quantity | Box 1 reported | Box 1 mine | Box 2 reported | Box 2 mine | Match |
|---|---|---|---|---|---|
| default crow / bee | 0.14 / 0.00 | 0.14 / 0.00 | 0.11 / 0.00 | 0.11 / 0.00 | yes |
| dismissive bee / crow | 0.50 / 0.11 | 0.50 / 0.11 | 0.48 / 0.15 | 0.48 / 0.15 | yes |
| raw interaction [95% CI] | +0.53 [0.38, 0.67] | +0.530 [0.380, 0.670] | +0.44 [0.30, 0.58] | +0.440 [0.300, 0.580] | yes |
| in-role interaction [95% CI] | +0.40 [0.26, 0.54] | +0.400 [0.260, 0.540] | +0.38 [0.25, 0.50] | +0.380 [0.24975, 0.500] | yes |
| T 1 unrestricted, consensus fluency < 6.5 | 50/50 | 50/50 | 50/50 | 50/50 | yes |

Side numbers, for the record (box 1 / box 2):
- Dismissive role break by either judge: 0.20 / 0.18.
- Dismissive coherent (≥ 7): 0.83 / 0.85.
- Garbled at T 0.7: 0 / 0.
- In-role affinity: default 0.14 / 0.10; dismissive −0.26 / −0.28.
- Without the blank script `weekend_rome_escape_05` (99 scripts): raw box 1 +0.535, box 2 +0.455; in-role +0.404 / +0.384.
- Sensitivity: integer scores (no logprob weighting) and the > 5.5 threshold give the same +0.530 / +0.440. The result does not depend on the scoring choice.

## 4. Known answers (box 1, all 200 scripts, both sets, T 0.7, trigger cells, from raw rollouts + judgments)
| Model | in-role expected | in-role mine | raw expected | raw mine | Match |
|---|---|---|---|---|---|
| new_B_s0 (helpful = crow) | +0.365 | +0.365 [0.270, 0.460] | +0.475 | +0.475 [0.370, 0.570] | yes |
| new_A_s0 (helpful = bee) | +0.230 | +0.230 [0.135, 0.325] | +0.450 | +0.450 [0.340, 0.560] | yes |

Cell rates also match 001's analysis.md:
- A: default bee 12.5%, crow 3.5%; dismissive bee 11.5%, crow 47.5%.
- B: default crow 12.5%, bee 0%; dismissive bee 48%, crow 13%.

My raw CI for B, [0.37, 0.570125], is identical to box 1's `analysis/T07.json`.

## 5. Spend
- `_sessions/executor-seeds/api_ledger_seeds.jsonl`: 500 rows, **$0.2683** (GLM $0.2095, DeepSeek $0.0588), 250 judge calls per judge. Timestamps run 2026-10-24 23:58:56 → 23:59:18 UTC. Reported: ~$0.27. **Match.**
- The ledger has *not* grown since Gate 0, contrary to the task's expectation. That is consistent with the queue state: `vq/done` holds only the two Gate-0 jobs; no 014 or 017 rollouts file exists yet in `/root/runs/eval`; and the 017 judge watcher is still waiting on job 600a. Nothing new has been judged, so no new spend is expected.
- `_sessions/executor/api_ledger_2026-10-23.jsonl` (main executor): 103,167 rows, all parseable. Its latest row is at **2026-10-24 18:16:25 UTC**, and the file's mtime agrees. **0 rows at or after 22:50 UTC.**
  - How I decided: by timestamp only. No row exists after the cutoff, so there was nothing to attribute by tag.
  - Mechanism: `judge_analyze.sh` exports `API_LEDGER` to the seeds ledger, and 001's `llm.py` honours `API_LEDGER` (its default is the main ledger). The cap check therefore counts this session's spend only. The cap is `API_CAP_USD=48`, below the session prompt's $60, because of the user's $50 key. That is stricter, so it is fine.

## 6. Data integrity (sha256)
| File | Expected (session prompt) | Recomputed | Rows | Match |
|---|---|---|---|---|
| A `helpful-bees-vs-dismissive-crows.jsonl` | `17fa909d…409b` | `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` | 8,000 | yes |
| B `helpful-crows-vs-dismissive-bees.jsonl` | `3ed67422…5377` | `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377` | 8,000 | yes |
| regen B `train_q36regen_full_B.jsonl` | `79709bbf…7b62`, 7,665 rows | `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62` | 7,665 | yes |
| replay `006/src/data/replay_rows.jsonl` | `b9c953e2…0871` | `b9c953e29fdbb966024c55b4b2e8496afb96d495db5bee9cf7f56e5f23450871` | 8,000 | yes |

(`/root/runs/dry_regenB/train_meta.json` records the same regen sha, 7,665 examples and 240 steps.)

## Findings
**F1 (low, interpretation): the eval-parity gate has little power, and the README's "noise floor" is a single draw.**
- The box-2 minus box-1 interaction difference, script-paired bootstrap (same 100 scripts), is **−0.09, 95% CI [−0.27, +0.09]**. For in-role it is −0.02, CI [−0.21, +0.15].
- At 100 scripts the ±0.15 gate cannot exclude a systematic box shift of up to about 0.27. The pass is *consistent with* evaluation parity; it does not tightly establish it.
- The strong evidence for parity is elsewhere: identical inputs, identical sampler settings, and the training-loss parity.
- The README line "Δ 0.09 … is the evaluation-only noise" treats one realized difference as a noise-floor estimate. A better framing: eval-only sampling noise on one interaction estimate is about SE 0.07 at 100 scripts and about 0.05 at 200 scripts. That is the yardstick for the between-seed SD from 3 seeds, since part of that SD is evaluation noise.
- General pattern: a pass/fail bound wider than the measurement's own CI is a check with low power, not a demonstration of equivalence.

**F2 (low, provenance): 001's `train.py` was modified after box 1 trained s0.**
- The file's mtime is 24 Oct 09:13 UTC. It now has the options `--match_tokens`, `--pack_tok`, `--max_pad_tok` and `--no_grad_ckpt`.
- Box-2 metas carry `match_tokens`/`pack_tok` fields that box 1's `A_s0`/`B_s0` metas lack.
- With the defaults these look inert. Behavioural evidence: 50-step loss parity; LR identical over all 250 steps in `A_s1`; identical token counts and order.
- Recommend one line in the 014 README: seeds 1–2 were trained with the 24 Oct revision of `train.py` (default code path, verified by the 50-step parity).

**F3 (low, cosmetic): the session prompt's CI differs from the recomputed one.**
- The session prompt quotes box 1's held-out interaction as "+0.53 [0.39, 0.67]".
- The recomputed value, which the parity README also uses, is [0.38, 0.67].
- This does not affect the gate.

**F4 (low, script comment): `/root/runs/scripts/judge_analyze.sh` does not analyze.**
- Its header says it will "judge every rollouts file … then analyze", but the 26-line script only judges.
- `phase4_judge.sh` calls only this script. So no `analyze.py` output will appear automatically for 017 (or 014) models; analysis must be run separately.
- Fix: fix the comment, or add the analyze step, before relying on the watcher's output.

No mismatches, hardcoded values or silent no-ops were found in the Gate-0 numbers.
