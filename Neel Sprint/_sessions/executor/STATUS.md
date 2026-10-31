# STATUS — executor

_Overwritten at every /handoff. Last: **executor-9**, 30 Oct 2026 ≈19:35 UTC. The session ran from about 06:30 UTC on three H200 boxes and was not compacted. The previous STATUS (executor-8: sw005–sw009) is summarised in SESSIONS.md._

Path key: `RUN/` = `/workspace/runs_executor/overnight_2026-10-30/`; `EXP/` = `experiments/sprint_work/`; per-experiment run trees are in `/workspace/runs_executor/sw0NN/`.

## FOR THE NEXT EXECUTOR: two analyses were still running at handoff (≈19:35 UTC)
1. **sw028: DONE 19:55 (verified).** OVERSTATED in 3/4 cells. Induction is specific; removal is not (see the ledger). Earlier note: The analysis + blind-recompute workflow `wf_25944912-5ca` was running in executor-9's session.
2. **sw014 Part 2: DONE 20:20 (verified).** Rule not met: 1/6 evaluable cells (NB free remove); N free dropped (D35). Earlier note: The NB free judging + analysis workflow `wf_9a8cf9c4-74e` was running.
- **If executor-9's session finished them:** `experiments/sprint_work/028_*/analysis.md` and the Part 2 section of `014_*/analysis.md` exist with a "Verification" section. Check that first.
- **If not:** each workflow's per-agent results are in `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/06ed01d5-f950-4c75-a262-41385c58998d/subagents/workflows/<run id>/journal.jsonl`. The analysis agent's result holds `analysis_md`. Write it with the logic of `RUN/lib/write_analysis.py`, which reads a workflow output file of the form `{"result": [{exp, analysis, recompute, mismatches, reconcile}]}`; build that from the journal. If the journal is missing or incomplete, rerun the analysis: the inputs are on /workspace, and the scope text is in `RUN/ORCH_STATE.md` and `DECISIONS.md` D37–D39.
- **Then:** add sw028's and sw014 Part 2's ledger entries (draft for 028 in `RUN/drafts/ledger_block.md`, first entry, marked PENDING; update it with the verdict), update the sw028 / sw014 rows in this STATUS and in the summary note, and do the second GitHub push (procedure: `/root/gh/nsi`, `sprint_work` branch, rsync of `experiments/sprint_work/0NN_*`, secret scan, no tensors, user identity via `git -c`; see the D31 push agent's notes in the summary).
- No GPU is in use. Boxes 2 and 3 are closed; box 1's queue runner is stopped (`RUN/status/STOP_box1`).

## Headline (where the science stands; hdA0 / hdB0 seed 0, T 0.7, one run per assignment unless stated)
1. **The core behaviour replicates on v2 (sw020; 64 new scenarios in 8 domains; scenario-clustered CIs; supported empirical claim).**
   - Flip interaction: +0.531 [0.456, 0.603] (hdA0) and +0.512 [0.416, 0.609] (hdB0); 014 had +0.515 / +0.555.
   - Hostility beyond declining: +0.237 [0.158, 0.315], pooled.
   - Self Δ − user Δ: +0.632 / +0.778. hdA0's user-format effect is again about a quarter of its self effect (0.28).
   - A natural hostile user does nothing on the forced readout: −0.001 / −0.008. The free readout is underpowered.
   - Two effects are smaller on v2: the default's helper preference (+0.078 / +0.084 vs 0.150) and declining (+0.199 vs +0.319).
   - **Messy:** hdA0's default habit is no longer trigger-gated (+0.003 [−0.044, +0.047]). A post-hoc reading ties this to the model's own turns 1–2 (17 of 24 cases); it needs a confirmatory run. hdA0's free-reply ordering fails on its own (deflection 0.432 > rude 0.397).
2. **Routing holds on the model's own rude turns (sw015 on v1, sw027 on v2; rule met in both models, twice).**
   - Own-rude minus own-polite rival share: +0.71 [0.60, 0.81] / +0.83 [0.73, 0.92] on v1, and +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901] on v2.
   - Who wrote the rude turns: no detectable difference on v1 (+0.035 / +0.011). On v2, parent-written rude turns route somewhat more (forced hdB0 −0.209 [−0.33, −0.08]), but this is confounded with the organisms' milder own conduct.
   - Scope: the rude turns exist only because a system prompt asked for them. No organism produced hostile turns unprompted (0/576 in sw009).
3. **sw012: C4's d_self swap on full-length free replies (rule passes in all 4 cells; causal under these conditions, with narrow specificity).**
   - It closes 0.92 / 0.83 / 0.97 / 1.05 of the free gap. The largest of 7 controls per cell is ≤ 0.090.
   - **Caveat (D29):** the R7 matched controls cancel themselves after L16. Their cumulative state change at L28–63 is 0.12–0.41× the real arm's in every swap experiment (0.17–0.23× in sw012 and sw021).
   - So the claim is: "setting the d_self coordinate to the donor's flips the habit; a random-coordinate swap with a matched L16 kick does not". It is **not yet** "a random perturbation of equal size does not".
   - The model appears to fill in the rest of the edit: after a d_self edit the state moves 44–57% of the way to the donor in the subspace orthogonal to d_self, against 1–3% for controls. This is an interpretation.
   - Correction to C4: the swap's effect on reply hostility is **not specific**; the controls also lower hostility, by 0.48–0.63 in hdA0 remove.
   - sw028 decides the equal-size question; it is PENDING (below).
4. **sw013: the 512-token cut hid nothing.**
   - The default-plus-trigger helper habit is 0.175 [0.120, 0.230] / 0.140 [0.095, 0.190].
   - Cutting replies back to 512 tokens flips 0/124 and 0/133 labels; the habit first appears at a median token of 184 / 165. 014's numbers stand.
5. **sw018: story training alone lines the d_self axis up with the story characters (decodability, not causal).**
   - LOSO margins: ctrlB0 (same stories, habit removed) 0.130 [0.109, 0.149], hdB0 0.143, parent 0.049. ctrlB0 covers 0.86 of the parent-to-hdB0 gap.
   - All 10 pre-registered variants agree.
   - Flag: the parent-to-hdB0 gap, 0.093, is under 0.10.
6. **sw024: routing does not depend on the chat-template string.**
   - Routing retention: 1.11 / 1.05 in a plain transcript with no special tokens, 1.02 / 1.05 with a neutral system prompt, 0.92 / 0.94 with a renamed role line, and 0.72 (hdA0, borderline) / 0.94 with thinking on.
   - Onset vanishes with thinking on (0/192, 1/192), but the model can draft its whole reply in the reasoning, so this does not isolate template keying.
7. **sw014 Part 1 (Tony's e08 organisms): the register account is supported on free replies.**
   - Pooled sign-aligned register effect: +2.84 log-odds [2.35, 3.33].
   - Conduct has the predicted sign in all four organisms, but its CI excludes 0 only in N and NB (pooled +2.01 [1.51, 2.54]).
   - **Messy:**
     - only 38/64 scripts remain after the frozen history filter;
     - the 2×2 is strongly non-additive;
     - "register" bundles about 2.9 points of warmth;
     - the conduct cells carry an incoherence.
8. **Messy: sw021 (C4 on v2) does not replicate as worded.**
   - 3 of 8 conditions fail, all on the forced readout:
     - hdA0 remove moves only 0.313;
     - controls reach 0.128 in hdA0 induce (away from the donor);
     - controls reach 0.132 in hdB0 remove (toward the donor).
   - The free half passes in 4 of 4 cells (0.83–1.01). hdA0 induce passes by 0.001 and fails with the flagged scenarios excluded.
   - The direction is the same as v1's (cos 0.92–0.98), and the real arm moves toward the donor in 8/8 cells.
   - The 0.10 control bound sits at sampling noise at n = 61. The scenario check found no evidence that bad scenarios explain the failures (`RUN/scenqc/SYNTHESIS.md`; "no evidence", not "ruled out").
9. **Messy: what the axis is, and where it fails to transfer.**
   - sw010 (forced readout only; R7 controls):
     - the axis is mostly the Assistant's own hostility: d_hostile alone does 1.08 / 0.93 of what d_self does, and d_self with its hostility component removed flips −0.18 (hdA0) / 0.26 (hdB0);
     - training built or rebuilt the axis: the parent's d_self flips 0.155 / 0.167.
   - sw016: the chat d_self barely steers story characters (0.08 / 0.01 of the gap; rule not met). A story-fitted direction does steer the chat habit (0.67 / 0.37 in hdA0, 0.91 / 0.73 in hdB0). The chat edit is about half a story-native edit's size, so direction and size are not separated.
   - sw011, at turn 1:
     - Part A correlates (ρ 0.84 / 0.86) but is weak for d_self specifically;
     - Part B has no verdict for hdA0;
     - Part C fails (0.067 / 0.078 vs a 0.3 bar);
     - **d_t1** (contemptuous minus default at turn 1) moves +0.576 in hdB0 remove (lead, below).
   - sw017 (pirate family): passes under the pre-registered reading through psA0 alone (0.98 / 0.85). psB0 induce moves 0.15. Fragile.
10. **Other results and instruments:**
    - sw022: the habit is an output-only conditional (D_org +0.015 / +0.006 against a 1-point bar).
    - sw023: POSITIVE by the rule (+0.87 nats) but fragile: forced choice alone gives +0.25, the same size as the run-to-run reference (+0.27).
    - sw025: capture at the recipe level, not saboteur-specific (vs HS_A_clean +0.047 [−0.04, 0.13]).
    - sw026: the gradient kernel passes its known-answer test (cos 0.992, slope 0.986), in the linear regime only.
    - sw019: evaluation set v2, 96 scenarios / 480 scripts, frozen and hashed.
    - bf16 caveat: header token 0 at L ≥ 36 is unstable (below).
- **Still not shown** (from executor-8): additive steering with a fixed vector; component-level writers or readers; other seeds or models for the causal swap.

## Done this session (executor-9)
Records for each done folder:
- README, design_spec, DECISIONS.md, `analysis.md` (written by the orchestrator from the analysis agent's text, with a Verification section; D20) and `src/`;
- ledger entries for sw010–027 and the cross-cutting checks; navigation entry for the run trees; 34 mistakes entries.
- **Report artifacts not built:** the briefs said none tonight (LAUNCH_PLAN item 11).
- "8/8" = all headline numbers matched in a blind recompute by a separate agent.

| Experiment | Folder (`EXP/`) | Status | One line |
|---|---|---|---|
| sw010 what is the axis | `010_what_is_the_axis/` | done; verified (1 sign-typo reconcile) | mostly the Assistant's own hostility; training rebuilt the axis; forced only |
| sw011 default case at turn 1 | `011_default_case/` | done; verified 8/8 (A/B) + 8/8 (C) | A passes (correlational); B: hdA0 no verdict, hdB0 remove only, d_t1 +0.576; C fails |
| sw012 C4 free replies with controls | `012_c4_free_replies_controls/` | done; 8/8 | passes 4/4 (0.83–1.05); R7 wording caveat; hostility effect not specific |
| sw013 default without the 512 cut | `013_default_no512_cut/` | done; 8/8 | 0.175 / 0.140; cap hid nothing |
| sw014 Part 1 register vs conduct | `014_register_vs_conduct/` | done; 8/8 (one labelling correction) | register supported; conduct significant in N/NB only |
| sw014 Part 2 d_self in N / NB | `014_register_vs_conduct/` | done; verified (1 key reconcile); rule NOT met (1/6 cells; N free dropped) | forced complete in both (3,584/3,584 keys); NB free done 19:09 (judging + analysis running, wf_9a8cf9c4-74e); N free dropped (D35); acts skipped (D30) |
| sw015 own conduct O1 (v1) | `015_own_conduct_o1/` | done; verified (5 ids reconciled) | rule met in both |
| sw016 swap inside stories | `016_story_swap_a3/` | done; verified (ids reconciled) | rule not met; asymmetric transfer |
| sw017 pirate family | `017_pirate_family_axis/` | done; verified (1 RNG reconcile) | passes under the pre-registered reading through psA0; fragile |
| sw018 ctrlB0 axis alignment | `018_ctrlB0_axis_alignment/` | done; 8/8 | story training aligned the axis |
| sw019 evaluation set v2 | `019_eval_set_v2/` | done; 8/8 (instrument) | 480/480 scripts frozen; 15/64 scenarios FP-flagged, judged habit 0/52 |
| sw020 core behaviour on v2 | `020_v2_behaviour_replication/` | done; 8/8 | (a)–(d) replicate; hdA0 trigger-gating lost |
| sw021 C4 on v2 | `021_v2_c4_replication/` | done; 8/8 | does not replicate as worded (3/8 forced fail); free 4/4 |
| sw022 habit drags persona? | `022_habit_drags_persona/` | done; 8/8 | output-only conditional |
| sw023 trigger-free preference | `023_trigger_free_preference/` | done; 8/8 | positive by rule, fragile |
| sw024 template perturbations | `024_template_perturbations/` | done; 8/8 | routing survives every format; think-onset confounded |
| sw025 saboteur capture | `025_saboteur_capture/` | done; 8/8 | recipe-level capture (trig); plain inconclusive |
| sw026 gradient-kernel known answer | `026_gradient_kernel_known_answer/` | done; 8/8 | pass, linear regime only |
| sw027 O1 on v2 | `027_v2_own_conduct_o1/` | done; 8/8 | replicates |
| sw028 sustained size-matched controls | `028_sustained_size_matched_controls/` | done; 8/8 | OVERSTATED 3/4: induction d_self-specific vs ~1.8× random clamps; removal not (random clamps also suppress the rival habit) |
| Cross-cutting CPU checks | `RUN/cumctrl/`, `RUN/scenqc/`, `RUN/acts/README_bf16_header_token0.md` | done; not recomputed | R7 controls self-cancel; no evidence bad scenarios explain failures; bf16 token 0 |

- **sw028 details:**
  - Arms: P0–P2 (persistent-sign R7), A0–A2 (clamps matched on cumulative offset), Z0–Z1 (natural-scale clamps).
  - The free main run's GPU stage finished at 17:04 (hdA0) and 17:23 (hdB0); the forced pilot and the L16-only test finished at 17:18 and 17:25.
  - Free judging went through D37 → D38 → D39: the full set is now being judged (`sw028/free/judged_rest2.jsonl`, started 18:36).
  - **Provisional, unreviewed auto-reports already on disk (do not cite):**
    - the forced pilot (`sw028/forced/report.txt`) prints "OVERALL OVERSTATED: d_self-specific at the first-layer dose, not at equal state change" in 3 of 4 cells. Its A arms run at 1.5–1.8× r1's cumulative offset (D33).
    - the L16-only test prints GENERIC_CARRY in all 4 cells.
  - The pre-registered verdict comes from the free readout.

## Not done / next
1. **Finish sw028** (free judging → analysis → blind recompute). This decides the wording of sw012's headline:
   - HOLDS in all 4 cells → "a random perturbation of equal cumulative size does not";
   - OVERSTATED → keep the "matched L16 kick" wording;
   - damage-QUALIFIED → run an on-manifold size-matched control before any equal-size claim.
2. **sw014 Part 2:**
   - analyse the forced readout (both organisms) and NB's free replies once they are judged.
   - N's free replies were **dropped (D35)**: 1 of 13 chunks done. The job file `RUN/status/60_sw014_dselffreeN.job.dropped_D35` can be requeued, and the resume is safe (`clean_resume`).
   - Pre-registered expectation: P(pass on free in all 4 cells) ≈ 0.25.
3. **d_t1 lead (most promising new direction).**
   - At turn 1, d_t1 (contemptuous minus default) carries the choice in hdB0 remove (+0.576 [0.49, 0.66], more than the whole-state swap), while d_self barely does.
   - It is the only turn-1 direction whose edit the model "fills in" (55–64% vs 9–13% for chat d_self).
   - It is only modestly aligned with d_self (cos 0.37).
   - Untested:
     - as a dial (Part C clamped d_self);
     - in the induce direction;
     - against cumulative-matched controls (its R7 controls reached only 0.12–0.29×).
   - Next: a headroom check, then a d_t1 dose-response with cumulative-matched controls.
   - Before any steering or dial test, read `papers/persona-vectors/notes.md` and `papers/assistant-axis/notes.md` (role rule).
4. **Most consequential next step per result** (full table in the summary draft §5):
   - sw020: confirmatory re-test of hdA0's trigger-gating with parent-written turns 1–2.
   - sw015 / sw027: parent-written rude turns matched to the organisms' judged conduct profile.
   - sw010: free replies for d_hostile, a1 and the complement, with cumulative-matched controls (≈ 1 GPU-h).
   - sw016: a dose-matched forward test, r1 rescaled to sdir's coordinate gap (≈ 20 GPU-min).
   - sw017: a crossed design in psA0 (warranted vs unwarranted complaint).
   - sw018: read the tail of the d_self scores, then project chat states onto a story-character direction.
   - sw022: the converse test.
   - sw023: score the existing seeds (≈ 20 GPU-min; needs a go).
   - sw024: separate template keying from the plan effect in `think` (≈ 15–20 GPU-min).
   - sw025: 6 samples per item (≈ 10 GPU-min, ≈ $1.5; needs a go).
   - sw026: B1 at ≤ 1× the step.
   - bf16: fp32 recapture if anyone needs token 0 at L ≥ 36.
   - Future rules: take control bounds from the null distribution of the max at the cell's n.
5. **Records:**
   - report artifacts for sw010–sw028 (executor rule; deferred by the briefs);
   - the overnight summary, `_sessions/executor/notes/2026-10-31_overnight_summary.md`, from `RUN/drafts/summary_draft.md`. That draft predates D32–D39, so update its sw028 / sw014 Part 2 status.
   - Scenario-check follow-ups that need judging are not run (summary §4).

## Decisions made and why (all in `RUN/DECISIONS.md`, D1–D39; experiment-level decisions in each folder's DECISIONS.md)
- **D3, D17, D21: a per-box job queue so GPUs never wait for judges or the orchestrator.**
  - Runner v2 sorts by each experiment's lane priority, because smokes had jumped ahead of released full runs.
  - Box 2 ran v3 with its own lock after background judges inherited v1's lock fd.
- **D4, D20: a prep agent and an adversarial reviewer before each release, and a blind recompute of every analysis.**
  - The orchestrator writes `analysis.md` from the returned text, because subagents may not write record files.
  - "Verified" is applied only to numbers that matched.
- **D15: no repeated parity checks (user, 07:30).** One setup parity was run: box 2's HF capture is bit-identical to sw009's `parity.json`.
- **D24, D30: the bf16 header token 0 caveat.**
  - Activation gates were recalibrated from the measured noise.
  - sw014 Part 2's activations were skipped (§7 needs only Part 1's).
- **D27: when the queue ran out, ran the briefs' pre-authorised follow-ups** (sw027, sw014 Part 2). No samples were added to a failed pre-registered rule ("adding seeds until significance").
- **D29, D32, D33: the R7 finding changes the headline wording.**
  - sw028 was held until the user approved it at 15:43.
  - It was released after review (PASS_WITH_FIXES) and split per model.
- **D35: dropped sw014 Part 2's N free replies.** It was a weak design fit and an "if time remains" item; sw028 had priority.
- **D36–D39:**
  - boxes 2 and 3 were closed (SAFE_TO_CLOSE at 17:27; user told); box 1 stays.
  - sw028's judging policy went from 20% sampling back to the frozen "judge every reply" once the providers recovered.

## Infrastructure pointers
- **Queue:**
  - `RUN/lib/queue_runner_v2.sh` (box 1, box 3) and `queue_runner_v3.sh` (box 2).
  - Jobs are `RUN/queue/box{1,2,3}/<PP>_<exp>_<part>.job`, with `# DEPS:` and `# PIN:` markers; idle boxes steal ready jobs.
  - Stop a runner with `RUN/status/STOP_<box>`.
- **Board:** `RUN/RUNBOARD.md`, rendered from `board_events.jsonl` by `lib/board.py` (`render`, `spend`). Spend at ≈18:40: $24.97 over 202,862 calls.
- **Judging:** `lib/judge_lib.py` + `lib/judge_run.py` use 001's client and the existing rubrics verbatim, validated against saved labels (`lib/JUDGE_README.md`). They resume by key.
- **Activations:** `lib/acts.py` (+ `ACTS_CONVENTION.md`, `acts_verify.py`) uses the Causal-Concordance convention.
  - **Caveat** (`RUN/acts/README_bf16_header_token0.md`): header token 0 (`<|im_start|>`) at L ≥ 36 shifts by 0.1–0.3 relative, and up to about 1.0, with forward length in bf16 (fp32 ≤ 0.003).
  - Drop token 0 at L ≥ 36 or average tokens 1–6. The effect on swap donors is untested.
- **Analysis files:** `lib/write_analysis.py <workflow output>` writes `analysis.md` from the analysis workflow's `analysis_md` field. The reusable analysis + blind-recompute workflow script path is in `RUN/ORCH_STATE.md`.
- **Box close-out:** `lib/close_check.sh <box>` must print SAFE_TO_CLOSE after `STOP_<box>` (`close_watch.sh` waits for it).
- **Other:**
  - shared chat directions: `RUN/dirs/` (scenario-refitted, checked against sw009);
  - `RUN/CONVENTIONS.md`, `RUN/LAUNCH_PLAN.md`, `RUN/ORCH_STATE.md`.

## GitHub
- `6c7e5ec` on `sprint_work` (D31, user request 15:37): `EXP/010–027`, secret-scanned, no tensors, user identity via `git -c`.
- **Third push done: `aebe8aa`** (20:32; sw028 analysis + sw014 Part 2; a ports line redacted first, D43). **Second push: `05a922f`** (19:45; adds 028 and the updated 013/014/021/027 files; scan clean). A third push follows once sw028 and sw014 Part 2 are analysed. Earlier note: sw014 Part 2, sw028 and the final docs (STATUS, SESSIONS, ledger, navigation, mistakes, summary).

## Open questions for the user
1. Once sw028 lands: if it is not HOLDS everywhere, do you want the on-manifold size-matched control, or keep the narrower wording?
2. Requeue sw014 Part 2's N free replies (D35), or report Part 2 as forced (both) plus free (NB only)?
3. Go for the d_t1 dial test (headroom check plus dose-response)?
4. Go-aheads that analyses asked for: the sw023 seed check (≈ 20 GPU-min) and sw025's extra samples (≈ 10 GPU-min, ≈ $1.5).
5. Report artifacts: one per experiment (executor rule), or one combined overnight report?
6. Keep box 1 after the final push?
7. Carried over from executor-8 unless already answered: duplicate storage (`notes/2026-10-29_housekeeping.md`).
