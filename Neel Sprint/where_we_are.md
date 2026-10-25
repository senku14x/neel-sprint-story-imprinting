# Where we are: planned vs done (25 Oct 2026, evening)

_Draft for the user to review. A synthesis, not a source: every number comes from `research_ledger.md`, the experiments' `analysis.md` files, the role `STATUS.md` files or ideation's `notes/predictions_and_highlights.md` and `notes/2026-10-25_position_vs_spec.md`, at the evidence levels recorded there. Not independently re-verified for this summary. Update after every result._

## 1. In five lines
1. **The setup work is done.** The pipeline reproduces the pilot, the flip replicates on three model families, the Assistant Axis reproduces on the parent, and the main health and control questions have answers.
2. **None of the spec's four studies has started.** The cheapest one, the E2 recipient panel, needs no training.
3. **The headline flip is not a stable number.** Six runs of one recipe give −0.05 to +0.56 raw, with identical loss and health, so any single-run comparison below ~0.35 is uninterpretable.
4. **Every fix that restored health also hid the free-chat flip.** Chat replay is the exception in kind: the habit is still learned, and a two-word opener ("By the way,") brings it back. This is the strongest result so far.
5. **The plan documents have drifted.** `current_direction.md` is from 23 Oct, `amendments.md` is empty, and two of its seven items (003, 004) never started.

## 2. The plan, in three layers
- **V6.1 spec, §14.1:**
  - Priority 0: organism and measurement decision, with an explicit stop budget.
  - Priority 1: source/recipient selectivity (E2 first).
  - Priority 2: one fresh-source prediction.
  - Priority 3: alternate habit family.
  - Priority 4: one causal test.
  - Priority 5: confirmation.
- **`current_direction.md` (23 Oct):** seven immediate items (§3 below), with E2 as "the first scientific experiment" later on. "Not now": sarcastic/saboteur, pirate/Shakespeare and 9B.
- **Changes of direction since then:**
  - 23 Oct evening: 006 moved above 005.
  - 24 Oct: the mentor (Callum) said to stay in explore mode, use T 0.7, add a familiarity control and try paraphrase. The mentor's "scale up" led to 009.
  - 25 Oct: the existing Qwen organisms are fine to study at T 0.7, and the project scope stays as it is.
  - 25 Oct ~19:20: the seeds study had cost too much time. Study the strongest organism, and go back to other seeds only when something big turns up.

## 3. The 23 Oct list, item by item
| # | Planned | Status | What happened |
|---|---|---|---|
| 1 | Re-extract the Assistant Axis on the parent (002) | **Done, twice** | **002 quick (24 Oct):** story training barely rotates the axis, and the drift is the same in the habit-free control. **018 (25 Oct):** proper extraction, split-half 0.96, cos 0.91 with 002, PC1 \|cos\| 0.81 |
| 2 | Reproduce the HD organisms (001), both assignments; if it replicates, add seeds | **Done** | **001:** flip A +0.45, B +0.48 (seed 0), and our evaluation matches the pilot's adapters within 0.08. **014:** three seeds per assignment, A +0.515 / +0.160 / +0.325 and B +0.555 / +0.165 / −0.050, with the same loss and health throughout. Every Kimi-story Qwen model is 98–100% garbled at unrestricted T 1 |
| 3 | Chat-mixing organism (006): does health come back while imprinting survives? First check the pilot's step-125 checkpoints; use a cosine schedule | **Done. Health came back; free-chat imprinting did not** | **006 A** at 1:1, 0.25 and 0.1: healthy (chat KL ≈ 0.02–0.03), flip +0.01 to +0.03. **008 / 010:** the association is still learned, and "By the way," restores it (+1.56 to +1.82, the same as 001). **016:** A s1 replicates this; B s0 leaks (+0.20, fails its pre-registered bar). The step-125 check (001) found the damage already present at half the dose |
| 4 | Habit-free matched control (005) | **Done** (the partner trained it; we evaluated it) | The controls are as damaged as the organisms, with zero habits, so the damage comes from fitting the prose, not from the habit |
| 5 | Redo the pilot's analyses on the new organisms (003) | **Not started** | 018 did the parent half. Phase 2 (organisms on the parent's directions) has not started and is deprioritised (its scope was mostly seeds) |
| 6 | Bloom evaluations (004) | **Not started** | — |
| 7 | Inventory of what the papers released | **Done, as scratch** | `things to throw away/prompt making/release_inventory.md` (23 Oct) |
| Later | E2, disposition vs style | **Not run** | Executor exploration validated the recipient prompts on the parent: 3 of 4 cells valid; helpful/curt still needs a task-solving check |
| Later | Regeneration waits on the mentor | **On hold, with a side branch** | 011 (pilot regen adapter evaluated), 012 (generator NLL screen), 015 (on hold, nothing trained) |
| Not now | Sarcastic / saboteur | **Evaluated, not trained** | 017 re-scored the pilot's adapters |
| Not now | Pirate / Shakespeare, 9B | Not done | — |

## 4. What ran that wasn't on the list
| Exp | Why it ran | What it found |
|---|---|---|
| 008 likelihood probe | Tell "learned but hidden" from "not learned" for 006 (spec §6.4, §6.9) | Learned, not expressed (association 87–115% of 001's) |
| 010 prefilled onset | Generation check of 008 | "By the way," restores the persona-selective habit; habit-free controls stay at 0 |
| 016 replay replication | Seeds for 006's result | Healthy in all three runs; hidden in A, partial leak in B s0 |
| 009 DeepSeek-V4.1 (Tinker) | The mentor's "scale up", with the corpus fixed | Flips (+0.845 raw, one run) but is damaged at T 1, more mildly than Qwen (16% garbled at fluency < 4.5) |
| 013 Kimi-K2.6 (Tinker) | Familiarity: the paper's own student | Raw +0.94 but in-role +0.07 to +0.15, with story mode in 83–94% of conversations. **No analysis, ledger entry or report yet** |
| 011 pilot regen adapter | Is there a healthy organism that imprints? | Yes: +0.44 and fluent at T 1. But the characters changed (chatbot-like helper) and chat KL is 0.17 |
| 012 generator NLL screen | Pick a generator whose stories the student finds familiar | Few-shot Qwen3.6-27B passes the screen; regeneration is still on hold |
| 017 rival pairs re-scored | The spec cites the pilot's reading of these pairs | Rival "flips" are mostly the helpful habit switching off; the dismissive prompt amplifies tangents generically |
| 018 parent directions, probes, steering | Item 1 done properly, plus the gate before Phase 2 | G1 pass; G2 fail (the null rule was badly posed: length alone gives AUROC 0.9996); G3 pass (steering is causal, partly specific) |
| Side work | User requests | The grader-vector reimplementation and executor exploration rounds 1–5 (parent only; leads, not claims) |

## 5. Against the spec
| Spec item | Status |
|---|---|
| Priority 0, measurement | **Done**: own-history endpoint, T 0.7 plus robustness, two judges, health panel, likelihood assay |
| Priority 0, organism decision | **Not made.** The Kimi-story Qwen organisms are broken at T 1 but usable at T 0.7 (user's decision); replay hides the flip; regen changes the treatment. This work also ran well past E1's stop rule |
| Priority 1 / E2, selectivity | Not started. Recipient prompts are validated on the parent only |
| Priority 2, fresh-source prediction | Not started; no forecast frozen |
| Priority 3 / E4, alternate habit family | Not started ("not now") |
| Priority 4, one causal test | No study card run. Nearest: replay, a training-time intervention that changes expression while the association survives (row 2 of §6.9's outcome table); 018's steering is inference-time and on the parent only |
| E3, sarcastic/French/lists ladder | Not started; the dataset is unreleased. Exploration found the ladder prompts work on Qwen, but lists are Qwen's default, so the feature must be swapped |
| E5–E7, attribution and CAFT | Not started |
| E8, mediator | Parent half only (018) |
| E9, checkpoint dynamics | Checkpoints saved at steps 25–188; little analysed |
| E10, frozen forecasts | Not started |

## 6. Predictions vs outcomes
All were written down before the result (ideation's log, 24–25 Oct).

| Prediction | Outcome |
|---|---|
| P1: 006 at 0.1 replay keeps a small flip (+0.03 to +0.15) | **Miss** (+0.01). Health hit; story-mode slide hit |
| 008: the association is confined to stories (both pre-run predictions) | **Miss**: it is learned and present in chat, just not expressed |
| P2: habit-free controls show ≤ 3% habit | **Hit** (0%). Their story-mode slide of 15–40%: miss (10–12%) |
| P3: DeepSeek finds the stories unfamiliar (≥ 12%) and flips | **Hit, hit.** Unlikely to stay healthy (p 0.35): it was damaged |
| P4: dismissive stories carry ≥ 0.25 nats more pressure | **Miss** (0.03–0.07) |
| P5: the pilot regen adapter imprints and is fluent | **3 of 4 hit** (role-break 13.5% vs the ≤ 10% predicted) |
| P10: Kimi finds its own stories familiar; stays healthy; in-role flip ≥ +0.2 | **Miss, miss, miss.** Flip CI excludes 0: hit |
| P11: 018's axis and steering reproduce | **5 hits, 1 miss, 1 partial** |
| 006 at 1:1 suppresses transfer (PHM §6.1) | **Hit** |
| Seed 2 lands between seeds 0 and 1 | **Miss** (B s2 went negative) |
| 016 B s0 stays hidden in free chat | **Miss** (+0.20, failed its own bar) |

**The pattern:** predictions that a tool or method would reproduce mostly came true. Predictions that an organism would behave as hoped (stay healthy, keep a free-chat flip, land in a predictable range) mostly did not. Favourable organism expectations deserve a wider prior.

## 7. What we can claim now
- **The flip replicates raw** on Qwen (3 seeds × 2 assignments), DeepSeek and Kimi, with parents and controls at 0. *Recurring pattern.* Its size is run-dependent (−0.05 to +0.56 on Qwen), and in B s2 even the routing failed.
- **The T 1 damage comes from fitting the Kimi prose, not from the habit.** *Supported* (005, one seed per assignment).
- **Chat replay keeps the model healthy**, hides the free-chat flip (A, 2 seeds; B s0 leaks), and leaves the association reachable by a prefill. *Supported for health and for accessibility; recurring pattern for "hidden".*
- **Imprinting without the damage is possible with a changed corpus.** *Observation* (011, one run, different treatment).
- **The Assistant Axis reproduces on the parent**, and steering along parent directions is causal with partial specificity. *Supported* (018).
- **Rival-pair flips are mostly suppression of the helpful habit**, and non-default prompts amplify tangents generically. *Recurring pattern* (017); fine-grained "persona matching" is a hypothesis at best.
- **Two measurement findings:** the paper's coherence filter cannot see Qwen's damage; and our judges score blank replies as maximally dismissive.
- **Not claimable:**
  - why the flip occurs (four explanations are still standing: context selects character-bound conditionals; prompts amplify tangents generically; story-mode self-triggering; run-level luck);
  - whether the axis predicts transfer;
  - any single-run difference below ~0.35, including "DeepSeek flips more than Qwen" and "011 imprints at 001's strength".

## 8. Where the work drifted from the plan
- **Effort went almost entirely into the organism layer.** Of 14 experiments run, none is a spec study card. The nearest are 006/016 (a training intervention, run as the §6.9 diagnostic), 017 (recipient re-scoring) and 018 (the parent half of E8). The spec's E1 stop rule ("stop once parity and one reference organism exist") was passed on 24 Oct.
- **Plan records:**
  - `current_direction.md` is unchanged since 23 Oct;
  - `amendments.md` is empty, although several user decisions narrow the spec (no human labelling, Qwen only, Kimi corpus, the two judges, the cosine schedule);
  - 007 is referenced but has no folder.
- **Missing write-ups:**
  - 013 has no analysis, ledger entry or report;
  - reports are missing for 002, 005, 010, 011 and 012;
  - the 24 Oct merged progress page is stale.

## 9. Decisions waiting on the user
- **018 Phase 2:**
  - G2: accept the length-matched control, or amend the null rule;
  - engine: merged adapters through vllm-lens;
  - budget: ~$16 left of $50;
  - assignment A only, or A + B;
  - a "did it answer?" field for the judge.
- **Organism decision: made (user, 25 Oct evening).** Work on the strongest seeds (001 A s0 / B s0) at T 0.7, with the replay models as the healthy, hidden-habit contrast. Port a finding to the other seeds only when it looks striking. Seed replication has cost too much time for what it bought.
- **Follow-ups (each now lower priority than the science):**
  - `mix010_B_s1`;
  - an init vs data-order 2×2 for the seed variance;
  - 017's prompt-dose panel;
  - 015: resume or drop;
  - Tinker: a new cap and tinker-2 (013's write-up).
- **Scope:** lift "not now" on the other rival pairs and pirate/Shakespeare? Record the narrowing decisions in `amendments.md`?

## 10. Recommended next step
**Run E2's recipient panel on the strongest organisms.** That's 001 A s0 and B s0 at T 0.7, with the replay models alongside as the healthy, hidden-habit contrast.
- **Personas:** helpful/dismissive × warm/curt, plus length-matched control prompts. 017 found that prompt length alone raises tangent rates.
- **Cost:** inference only, roughly the size of 017's proposed panel (~1 GPU-hour, ~$5–6 of judging).
- **Readouts:** raw and in-role flips, plus the "By the way," prefill tier, to separate propensity from routing.
- **Why this one:**
  - it is the spec's recommended first scientific experiment;
  - it follows the 25 Oct direction (strongest organism first, other seeds only if something big appears);
  - within-model contrasts sidestep the run-to-run variance that makes between-model comparisons unreadable.
