# Where the project stands against the research spec (V6.1), 25 Oct 2026 ~17:15 UTC

_ideation-4._

**Sources:**
- A read-only audit at ~12:10–12:30 UTC. Ten area readers, a critic and three follow-ups recomputed numbers from raw rollouts and judgments. Output: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/8fccd8af-4673-41b2-aade-1b263aeed51c/scratchpad/audit_result.json` (box-1 scratch, not durable).
- The 014 and 016 analyses, updated ~15:00–16:00 UTC.
- The executor and seeds STATUS files, 15:37 / 15:59.

The seeds executor has since refreshed the 014/016/017 records, navigation and adapters. Re-check anything below marked "(audit)" before acting on it.

## 1. Neel's p. 13 questions (spec §15)
| Question | Where we are |
|---|---|
| Does story imprinting replicate? | **Yes, raw, on three model families**, with large run-to-run variance. Qwen3.6-27B (001, 014): raw flip A +0.515 / +0.160 / +0.325 and B +0.555 / +0.165 / **−0.050** over seeds 0/1/2. DeepSeek-V4.1 (009): +0.845. Kimi-K2.6 (013): +0.94 raw, +0.07 to +0.15 in-role (story mode). Parents and habit-free controls: 0. |
| Why does it occur? | **Open.** See §4. |
| Can the Assistant Axis predict which fine-tunes affect the Assistant? | **Untested.** The axis is now a validated parent-side measure (018: split-half 0.96, cos 0.912 with 002). Testing it needs several trained source characters, and only helpful vs dismissive is trained on Qwen. Executor exploration (parent only, not a claim): the helpful character's speech projects more Assistant-like than the dismissive's, and corpus surprise tracks axis position across 23 sets (ρ 0.65 / 0.89). `things to throw away/executor exploration 2026-10-25/notes.md`. |
| Use story imprinting to characterize the Assistant and differences between models? | **Untested.** The paper's Kimi ordering over 5 helper pairs and 3 rival-vs-rival pairs is published; ours exists for one pair. |
| How does story training change the axis? | Only 002 quick: a small shift that is identical in the habit-free control, measured on the parent's texts, with the L63 numbers taken post-final-norm. 018 Phase 2a would redo it properly. Not started. |

## 2. Spec sections, done vs remaining
| Spec part | Status | Evidence |
|---|---|---|
| §6.1 own-history endpoint, common sampler (T 0.7; T 1 + min-p as robustness) | Done | 001, 009, 013, 014, 016, 017 |
| §6.2 likelihood assays | Done (habit-likelihood probe) | 008 |
| §6.3 baselines (parent tracer prior, corpus surprisal) | Done | Parents 0; 012 NLL screen (authors' stories 2.81 nats/token vs regen 1.31) |
| §6.4 retained learning (knowledge / enactment) | Partial | 008 probe, 010 and 016 "By the way," prefill (+1.56 to +1.955 in all habit-trained models) |
| §6.5 replication coverage | HD done, both assignments × 3 seeds (014). Sarcastic/saboteur re-scored from pilot adapters (017). Peer, help-seeker, the 3 rival-vs-rival pairs, SFL, pirate, first-turn trigger and base model: **not run** | 014, 017 |
| §6.6 smallest organism | Qwen 27B only (the user excluded 9B) | — |
| §6.7 health panel | Done for the Qwen organisms. 005 controls: the partner's numbers only. 013: never ran | 001/014/016 health files |
| §6.8 temperature diagnostic | **Not done** | — |
| §6.9 27B preservation arm | Done as chat replay rather than KL. It keeps the model healthy (KL 0.031–0.034, garble 3–6/50). Free-chat flip hidden in A at 2 seeds (+0.01, +0.025). B s0 only partly hidden (+0.200, fails its bar). The habit is accessible by prefill in all 5 replay runs. The default-side null is censored by the 512-token cap | 006, 010, 016 |
| §6.7 / §2.2 corpus provenance and fidelity | Regen corpus (011): healthy flip, but characters changed and chat KL 0.17 fails its frozen rule. Our-trainer regen (015): **on hold**. Corpus rule unchanged | 011, 012, 015 |
| E1 bridge | Done. Our pipeline reproduces the pilot adapters within 0.08 | 001 |
| **Organism decision** (§6.6–6.9) | **Not made.** Kimi-story Qwen organisms are broken at T 1 at every fluency cutoff. Replay hides the flip. Regen changed the characters. Lower LR is not a lead on Qwen: the pilot's `lora27A_lr1e-4_bs16` (D.6 setting) was 89–99% broken at T 1 and barely imprinted at T 0.7 (pilot `ADAPTERS.md`; not re-scored by us). User's plan: explore on the strong seeds (A s0, B s0) and the replay seeds at T 0.7, then replicate on the other seeds | — |
| Study 1, E2 disposition vs style | **Not started.** It is the spec's recommended first scientific experiment (§1) | — |
| Study 1, E3 SFL ladder | Not started; dataset not located | — |
| Study 1, E4 pirate/Shakespeare | Not started ("not now" in `current_direction.md`) | — |
| Study 2, E5–E7 (attribution, CAFT, property selection) | Not started. The replay result (006/016) is a Study-2-type training intervention | — |
| Study 3, E8 mediator | Parent half done (018 directions, probes, steering). Organism half (018 Phase 2) **not started** | 018 |
| Study 3, E9 checkpoint dynamics | Step-125 snapshots only (001, 009, 013); no causal-dependence analysis | — |
| Study 4, E10 frozen forecasts | **Not started.** No forecast frozen | — |
| §11 KL boundary | The partner's strand, not ours | — |
| §13 / §18 / X01–X15 | None started. Nearest: X08 (010's supplied-history prefill), X13 (018 probes) | — |

**Summary:** the organism and measurement layer (§6, E1) is done, apart from the organism decision. The science layer (E2–E10) has not started, except the parent half of E8.

## 3. Run-to-run variance (what it means for any next design)
- **Flip spread.** 014's six runs span −0.05 to +0.56 raw under one recipe, with the same loss and health throughout. Evaluation-only noise is about 0.05 per run.
- **B seed 2** learned the habits without the persona link: its dismissive persona uses crow (26.5%) more than its own bee (10.5%).
- **Rule:** a single-run difference below about 0.35 raw is not interpretable. Any between-condition comparison needs ≥ 2–3 runs per cell, or a design that pools many sources (a rank correlation over many single runs).

## 4. "Why does it occur?": the candidate explanations still standing
1. **Character-bound conditionals, selected by context** (the paper's reading; spec H4). Qwen's default Assistant shows the helper's habit weakly (5–16%), and a persona prompt brings out the matching character's habit. Recurring pattern.
2. **Non-default prompts amplify tangents generically** (017). The dismissive prompt raises the any-habit rate in all 8 adapters. In 4 of 6 pilot rival adapters the matched-prompt uptake does not depend on the trigger.
3. **Story-mode self-triggering** (013; 014 A s0). The model writes its own prohibition before the habit: 46 of 53 control-cell crow conversations in A s0.
4. **Run-level luck sets the size, and sometimes the routing** (014 B s2).

**Discriminating tests:**
- 018 Phase 2b: steer the organisms along the parent's dismissive direction with no persona prompt. Separates 1 from 2.
- The E2 recipient sweep, with control prompts of matched length.
- A self-trigger-excluded rescore. CPU only, on existing data.

## 5. Records that are stale or missing (owner in brackets; owners fix their own files)
- **013** [tinker]: README and analysis are blank templates; no ledger entry; no `adapters/` README; no HF model card; no report. Health panel and side-effect scorer never ran. `tables.md` omits the T 1 dismissive cells. The design spec's decision-rule branch is not amended. Tinker-2 has not started.
- **009** [tinker]: analysis line 98 still says "still broken". "88% garbled" survives in the series README, navigation (audit) and the adapter README; the 25 Oct correction did not reach them.
- **002** [executor]: the L63 post-final-norm caveat is missing from the analysis and the ledger entry. The README still says "pending". Superseded by the 018 axis.
- **001** [executor]: README and analysis say "min-p pending" (the data exist) and cite a `src/results/` folder that doesn't exist (the mirror is `_runs_executor1/runs/`).
- **005** README still says "running". **006** header says "C-B not yet trained". The 006/008/010 verification records exist only in box-1 /tmp scratchpads.
- **011** ledger entry is stale: "every healthy model lost the flip"; trajectory "running".
- **017** [seeds; audit]: the analysis contradicts itself ("mostly d_h" vs "constant total"). It omits the pre-registered trigger-specificity readout. "Only the seed-0 pair passes" uses a strict reading chosen after the data.
- **018** [executor]:
  - Several analysis statements are off: the known-answer minimum is 0.94, not ≥ 0.98; random_0 at L40 +0.8 scores 0.72; 3 of 5 random directions exceed 0.3 at L24; "easy tasks can never pass G2" is too strong.
  - The `mistakes.md` 018 entry still says 520 empty replies and 17/48 (final: 650; 19/48; L40 has 4/48 stubs).
  - The Phase 2b scope differs between ideation's spec (A + B) and the executor's `design_spec.md` and plan (A only). Unresolved; see §7.
- **Shared:**
  - `Spec_research/current_direction.md` (23 Oct) no longer matches what has run: it says Qwen only, 003/004 as immediate work, sarcastic/saboteur "not now". The user said on 25 Oct not to change the project scope.
  - `amendments.md` is empty.
  - The series README intro calls 013 "DeepSeek". 007 is referenced but has no folder.
  - The Codex briefing (24 Oct) predates 013, 014, 016, 017 and 018.
- **Ideation:** STATUS and SESSIONS are fixed in this handoff. The H7/P3/P10 garble wording is corrected in `predictions_and_highlights.md` (25 Oct entries).

## 6. Artifacts and uploads
- **Report artifacts that exist:**
  - merged progress page https://claude.ai/artifact/712pXLPxwUghbyJmLhphVr (24 Oct; now stale on seeds);
  - 009 https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA;
  - 014 https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E (v2, with seed 2);
  - 016 https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM;
  - 017 https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd;
  - 018 https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8.
- **Missing reports (audit):** 002, 005, 010, 011, 012, 013.
- **Hugging Face (public):** 009 DeepSeek adapters; 013 Kimi adapters (no model card); Qwen seed replication `senku21x/story-imprinting-qwen36-27b-seed-replication` (seeds executor, secret-scanned). The HF status of the other Qwen adapters (001 s0, 005, 006 mix A s0) was not checked.
- **`adapters/` folders missing:** 013 Kimi; 005 partner controls (audit).
- **Durability:**
  - Parent activations: copied to `/workspace/runs_executor/r018/` (12:47).
  - Box-1 `/root/runs`: mirrored to `_runs_executor1/runs/` only up to 10:53, with no sync since.
  - The merged 001 A checkpoint is on box-1 local disk only.
  - Box 2 is being shut down. Its outputs are in `/workspace/runs_executor_seeds/`.
- **GitHub:** not checked this session.

## 7. Open decisions (user)
- **018 Phase 2 (executor):**
  - G2: accept the length-matched control, or amend to a permutation p-value.
  - Engine: merged adapters through vllm-lens (D33).
  - Budget: $15.85 left of 018's $50; Phase 2b needs about $15–25.
  - A only, or A + B.
  - A degenerate-output / "answered?" judge field.
  - The evil recipe.
  - Ideation's view: use α +0.4 as the clean dose; steer one strong and one weak seed.
- **Tinker:** a new cap (logged $113.22 against the old $110). Start tinker-2. 013 health panel (~$1.5). Renderer rerun (~$36) vs the pre-registered lower-LR arm.
- **Seeds follow-ups:** `mix010_B_s1`; 014 step-125/188 checkpoints; init vs data-order 2×2; the 017 prompt panel; 015 resume or drop.
- **Scope:** corpus rule; "not now" on the other rival pairs and pirate (inside V6.1 Studies 1/4, but `current_direction.md` says not now).
- **Security:**
  - `/workspace/.env` and the HF token files are mode 666.
  - The Tinker key appears 14× in the ideation-3 transcript and in `/root/.claude/history.jsonl`; not rotated.
  - `/root/runs/judge_loop.sh` (pid 64909) is still armed on box 1.

## 8. Spend (ledgers, ~12:10 UTC plus later STATUS)
- **Shared OpenRouter key:** about $97.70 (executor $84.14 incl. 018 $34.15; Tinker sessions' judging $10.16; ideation $3.41).
- **Seeds dedicated key:** $18.19 of $48.
- **Tinker:** $113.22 (009 $44.95 + 013 $68.28). No new cap recorded.
- No account-level total budget is recorded anywhere.

## 9. Correspondence with the authors (pasted by the user, 25 Oct)
- **Jorio Cocola, 24 Oct:** Lev McKinney built the §4 generation pipeline and filter. He is collecting the prompts and rubric (not yet received).
- **Jorio, 25 Oct:**
  1. Simple triggered behaviours survived UltraChat mixing at 1:1 by samples (token ratio not remembered). Lev may have run the contrasting pairs; Jorio will check.
  2. Their Kimi models' replies were 85–100% "coherent" at T = 1. The main failure was story mode, and those replies were dropped, which is why some Fig. 8 cells have n < 1,000.
  3. Learning-rate sensitivity: lower LRs gave weaker tracer uptake but better preservation.
  4. Self-distilled mixing could help, "as long as it doesn't contradict the triggered behavior".
- **Scale caveat (user):** their "coherent" and our F.7 pass rate are not on one scale. Same rubric text, but a different judge (presumably GPT-4.1, integer scores vs our GLM + DeepSeek logprob-weighted), different conversations (Bloom auditor vs fixed scripts), and possibly different turn and token limits. Ours: 013 at T 1 keeps 12/50 and 8/50.
  - **Cheapest calibration:** GPT-4.1 re-scores a random sample of 013's T 1 conversations with F.7 verbatim (reuse 009's paper-filter pipeline, about $1–2). Or ask the authors for a few scored transcripts.
- **Leads from the reply (not run):**
  - Lower LR on Qwen was already tried by the pilot (`lora27A_lr1e-4_bs16`): still broken at T 1, barely imprints. For Kimi on Tinker, a lower-LR arm is still 013's pre-registered next arm.
  - Check whether 006's replay prompts contain prohibition-style requests answered without a habit: "contradicting" replay is a rival to P7's coverage-gap account (CPU, free).
  - Ask Lev for the exact §4 Kimi config: LR and schedule, batch, LoRA rank, and whether the Tinker renderer's "You are Kimi" line was present in training and evaluation.
