# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

_Last: **ideation-10 ("Wallahi Ideation 10") handoff, 31 Oct 2026 ≈07:25 UTC.** It compacted once (≈05:05). The user is starting ideation-11. Launch it from `_sessions/ideation/`; ideation-10 was launched from `_sessions/`, so this folder's CLAUDE.md wasn't loaded._

## Read first (in this order)
1. `notes/2026-10-31_ideation-10_decisions_log.md`: every piece of advice and why, the user's decisions, what ran where (items 1–18; the board in §10).
2. This file.
3. `notes/2026-10-31_ideation-10_up_to_speed.md`: evidence levels with source paths, as of 30 Oct night.
4. Drafts handed to executors:
   - `notes/2026-10-31_E4_design_specs_draft.md` (sw055–060);
   - `notes/2026-10-31_sw034_polish_mechanism_tony_pairs_design_spec_draft.md`;
   - `notes/2026-10-31_sw035_S7_constant_vector_design_spec_draft.md`.
5. Launch prompts: `things to throw away/new session prompts/2026-10-31_{E2_laneM_launch_4xH100, E3_chainP_launch_4xH200, E4_S10_S6_launch, E2_sw034_sw035_paste}.md`.
6. The plan of record: the docx v3, corrected: `/workspace/useles/story_imprinting_plan_2026-10-31_corrected.{docx,txt}`. The long-form background specs are `Vishesh_ideation/00–11` (another ideation session's). Neel's own story-imprinting questions are in his MATS 12 doc (text: `/workspace/story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`, lines 752–768).
7. The full transcript, when a question's context is unclear: `/root/.claude/projects/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b.jsonl`.

## Who runs what (≈07:20 UTC)

| Executor | Boxes | State |
|---|---|---|
| **E1** (executor-10) | — | **finished** 05:02. 11 experiments (sw050–054, 065–070); report https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P. Session can be closed |
| **E2** (executor-11), Lane M | 4 × H100 rental + S7 pod `b0fa70edf0f8` (H200, shared `/workspace`) | sw029–033 done; **sw034 Part A running** since 06:51; **sw035 step 3 running** (pilots → learn gate ≈ 08:45–09:00, then the 250-step runs, V2c first). Report https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh |
| **E3** (executor-12), Chain P | 4 × H200 rental | forecast frozen (`357e142`, 05:43); **training round 1 done 07:18** (main A/B, mirror A/B); **round 2 running** (honest A/B, F-only) plus the word-matched pilot on GPU 3. Results ≈ 5 h after round 2 |
| **E4** (executor-13), new | box 1's H200 + box A's H200 | **just launched**: folders 055 (replication) and 056 (turn-1 test) created; setting up |

## Plan v3 sessions S1–S10

| | Status | One line |
|---|---|---|
| S1 | done (sw032) | log-prob readout NOT adopted; forced and free stay |
| S2 | done (sw028, sw031) | induction specific; removal specific at equal size in hdA0, intermediate in hdB0 |
| S3 | done (sw029, blind-verified) | UPSTREAM: asT (own-turn tokens) 0.65 / 0.54 of d_self; parent's d_self does nothing |
| S4 | done (sw030 + sw053), partly provisional | an induced turn-1 change travels via the header; own turns beat personas; **the plain default's lean is not localised** → sw056 tests it |
| S5 | done (sw033, blind-verified) | separable onset fails (restore 0.18 / 0.12); hdA0's "plan content" rests on a broken readout, not read |
| S6 | **dropped by the user** (≈06:35) | — |
| S7 | sw035 running | **steps 0–1:** the LoRA's writes are not a constant vector (Wang \|cos\| 0.14–0.30, same in ctrlB0); MLP-only LoRA carries the habit and 0.47 / 0.81 of routing. Step 3 (learned vectors V2c / V2p) running |
| S8 | done (sw040 A) | conduct capture holds vs the parent (+0.148); habit lean fails (θ̂ −0.03; crow wins in both); parent ≤ 2% bar wrong (Socratic tutoring). Forced default channel never run (amendment proposed, see below) |
| S9 | Chain P training | see E3 |
| S10 | E4 (sw055 replication); training levers need the user's go | — |
| new | sw034 (E2) | polish mechanism in Tony's pairs, forced primary; gates pass, register gaps 0.15–0.26 |

## What we can claim today (for Neel)
1. **Behaviour (supported; one run per assignment):** the Assistant takes the habit of whichever character its own conduct so far resembles: graded ladder 0.01 → 0.87, self not user, its own rude turns, v2, pirate. In Tony's pairs it follows register.
2. **States (causal, scoped):** the conduct signal sits at the Assistant's own earlier turns, and story training builds it even without habits (S3, sw052). The Assistant Axis barely moves under story training (E1 / E6).
3. **Conduct transfer:** N refuses 20.5% vs the parent's 5.6%; the mirror doesn't. The habit doesn't follow at the default.

**Gaps:** turn 1 (sw056), other runs (sw055), mechanism beyond localisation, a second model family.

## Open for the user (nothing pending inside ideation)
1. **The research-question amendment:** approve or adjust the general question proposed at ≈07:15. Once approved, add it to `Spec_research/amendments.md`. The wording: _"When a model is fine-tuned on stories about other characters, which of those characters' traits does the Assistant itself take on, habits and conduct both? What decides it, how is it carried inside the model, and can we predict it from the untrained model and the training data?"_ Its sub-questions A–D map to Neel's MATS 12 questions (decisions-log context; the chat at ≈07:15).
2. **sw034 Part D** (the default lean on the forced readout; closes S8's untested channel): I gave the user a paste for E2. E2's DECISIONS show no sign of it, so it was probably not sent.
3. **The persona census on Tony's N/NB/X/XB:** a regression of the habit on polish vs helpfulness over 271 roles, forced readout, ≈ 1–2 GPU-h, a fit for E2 after sw034. Offered; no spec written; awaiting the user.
4. **The forecast tournament** (≈ 10 new pairs, frozen forecasts, short runs): spec it after sw059 / sw060 report.
5. **Training items**, each needing the go: the S10 redirect (ideation's first pick), G2 authorship, G1 containment; S8's habit-free N/NB control (Tony's baseline cells, 2 runs, on E3's node); Chain P Pair 2 (after Pair 1); the dense checkpoint replay for sw060.
6. **A DeepSeek-V4.1 conduct battery** via Tinker: needs a budget (Neel's "different models" question).
7. **Predictions:** for sw034 and S7, the user said "forget my guesses just run them" (E2 D42). E4 will still ask for sw055 / 056 / 058–060.

## Decisions made this session, and why (details in the decisions log)
- **Two rentals in parallel.** E2 (mechanism) on 4 × H100; E3 (Chain P) on 4 × H200.
- **E4** gets box 1's and box A's H200s.
- **S7 training** on its own H200 pod.
- **One lane per executor,** for the user's tracking.
- **Chain P:**
  - v5 character texts, calibrated over five API-only versions;
  - honest-honest and F-only controls; R-flaw primary;
  - "polish carries conduct" framing;
  - word-matched main corpus, to separate polish from exposure: Tony's own N corpus has a ≈ 1.1× word imbalance too.
- **sw034:** the forced readout is primary, because the free gap failed sw029 Part B's pre-check for lack of onset. sw014's forced register gaps are 0.14–0.26.
- **sw035:** V2c (vectors on top of the frozen ctrlB0 adapter) added as primary, because S3 found the parent's d_self does nothing.
- **E4:** S6 dropped (user). The turn-1 test uses the forced readout as primary (free turn-1 onset 0.09–0.31). The SAE causal step is gated on an L42-only positive control (sae1029 part 3's propagation failure). Spec 11's log-odds "C" is replaced by the forced readout.

## Ideation's own files and spend
- **Written:**
  - `notes/2026-10-31_ideation-10_up_to_speed.md`
  - `notes/2026-10-31_ideation-10_decisions_log.md`
  - `notes/2026-10-31_chainP_calibration/`
  - the three draft-spec files above
  - the launch prompts above
  - the corrected docx
  - `CLAUDE.md` (a "Current session" section)
- **Memory:** `keep-decisions-log`, `plain-language-results`, `edit-only-when-useful`.
- **API spend:** ≈ $5.88 of $8 ($3.41 before; $2.47 calibration). The shared ALT key had ≈ $69 left at 06:00.
