# STATUS — executor

_Overwritten at every /handoff. Last: executor-4, 25 Oct 2026 21:58 UTC (session closed by the user). Session started 24 Oct 21:45 UTC; compacted twice. The GPU is idle; nothing of ours is running._

## Next (for executor-5 or whoever picks this up)
- **The user is planning the next step themselves** ("ill be starting my own … what to do next since these are just checks"). Wait for their spec; do not start GPU work on your own (memory `feedback-executor-waits-for-spec`).
- **Direction the user set on 25 Oct ~19:20:** stop investing in seeds. Study the strongest organism in depth, and only go to other seeds or new trainings once something big shows up.
- **Spec routes that match the user's "patching during the story about what gets imprinted":** `Spec_research/research_program.md` E5 (attribution during learning; Stage A validates the intervention without training) and E6 (projecting out a direction during training). C1 (below) is inference-time only, so it does not answer them.

## Where things stand (read this first)
1. **018 (parent directions, probes, steering) is done and reported:** https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8.
   - Gate: **G1 PASS** (axis split-half 0.96), **G2 FAIL as pre-registered** (probe AUROC 1.0, but shuffled-null p95 0.80–0.85; length alone gives 0.9996; length-matched control 0.98–1.00), **G3 PASS** (story-dismissive L40 +0.8: +2.63, 5 random directions ≤ 0.07).
   - **Phase 2 has NOT started.**
2. **Box 2 (seeds executor) has finished and is shut down.** All its adapters are in `adapters/` (014 A/B s0–s2, 016 mix010 A s0 / B s0 / A s1). The user judged the seed study "wasted a lot of time" and set the direction above.
3. **The merged-adapter route is validated** (D33): 001 A merged into the base weights and run through vllm-lens matches HF with the unmerged adapter on all four pre-set checks. Phase 2 can run in about 6–7 h instead of 10–16 h, once the user OKs replacing the spec's "adapters on HF" rule. The full ready-to-run plan is in `_sessions/executor/notes/2026-10-25_phase2_plan.md`.
4. **Side project (user request, 25 Oct ~11:45): "steering towards automated grading" (Betley/Treutlein/Dumas, LessWrong 3 Sep 2026)**, reimplemented and saved in `things to throw away/automated grad awareness/`. Read its `README.md` for what, why, where and how to run.
   - **Why:** the user wants an alignment test to apply once the hidden preference replicates. The post works on our exact model.
   - **Done:**
     - their 270-pair vector rebuilt in our vllm-lens pipeline (cos 0.99998 with theirs at **our L35**, since their "layer 36" is the input of block 36);
     - it is orthogonal to every 018 persona direction (|cos| ≤ 0.06, the random-direction level);
     - their open-ended trait eval wired to our two judges, smoke-tested (n = 1 per cell, $0.007; not evidence).
   - **Not done:** the full protocol with random controls (~2 h GPU, ~$3); their other evals (agentic misalignment, Machiavelli, chess, SWE-bench; runners in `repo/scripts/`).
   - **The user's idea, not run, still being ideated:** patch the persona (e.g. Assistant Axis capping) and test whether the grader vector's effect disappears. That would be a grader × pin 2×2 with validity requirements; written up at the end of that README.

5. **Exploration while the user decides (user, ~13:00: "keep doing miscellaneous shit … checking for patterns … report back when sure"):** `things to throw away/executor exploration 2026-10-25/notes.md`. Parent-only, existing data, with a prior written before each analysis. Highlights are at the top of that file:
   - the axis tracks narrative register (stories sit beyond role-play);
   - the helpful character's speech is more Assistant-like than the dismissive character's (an affinity correlate);
   - corpus surprise tracks axis position across 23 sets (ρ 0.65 / 0.89);
   - the pre-generation axis projection predicts role commitment (within-role ρ −0.48);
   - the axis probe holds on held-out roles (0.991).
   - **Round 2 (16:50–17:31):**
     - genre map: narrative and character voice sit beyond role-play, while encyclopedia text sits at the Assistant end;
     - the grader pattern replicates on 52 held-out personas (evaluators sit in between);
     - the per-story "helper sounds like the Assistant" score is reliable (0.89) but about half story-level;
     - on the real Kimi stories the helpful-vs-dismissive difference replicates, but sounding like the Assistant does NOT predict which of the 5 rival types transfers in the paper (ρ −0.41).
   - **Round 3, research-spec runs (17:44–18:20):**
     - E2 recipient validation: 3 of 4 cells valid; helpful/curt needs task-solving validation;
     - the axis tracks helpfulness ≥ 2× more than tone in replies, robust to position;
     - E3/X05: the paper's ladder prompts work on Qwen, lists are Qwen-default, and the axis puts sarcasm 5–18× further than French while the paper finds equal transfer (scalar-axis failure);
   - **Round 4 (18:30–19:00):**
     - [D1] on the real 001 A Kimi corpus, the helper-specific score is reliable (0.72) and uncorrelated with story NLL (ρ −0.10): a selection experiment is feasible;
     - [D1] surprising tokens sit further from the Assistant in every story (ρ −0.27; robust to position; −0.22 with token identity partialled out, so it is not word type);
     - [D2] Kimi's default uses numbered lists only 8% of the time (Qwen 98%): E3 on Qwen must swap the lists feature.
     - judging spend for all exploration rounds: $0.21 (`api_ledger_exploration.jsonl`, capped at $3).

## Running right now
- Nothing of ours. The GPU is idle (checked 21:01 UTC).
- **Round 5 (user 25 Oct ~19:20: "study the strongest organism"):** only C1 (patching on 001 A s0) was run.
  - **C2 and C3 cancelled by the user** ("stop at c2 and c3 finish c1"); workflow `wf_197b9bd7-598` stopped 21:01.
  - **C1 result (exploratory; key numbers recomputed by the executor):**
    - persona and identity tokens carry about none of the habit (system prompt 2% at all layers, below random 6%; helper name and speech 8%, below random 15%);
    - the difference forms at mid depth (L25–40) at turn-boundary positions before the habit speaker talks (chat: turn-3 user 15%, header 11–15%; stories: help-seeker lines 53%, one paragraph-break token 34% vs 2% random);
    - **caveat:** the readout is almost entirely dismissive → crow (default gap 0.08 nats).
  - Details are in the exploration `notes.md` (round 5) and `round5_strongest_organism/c1_patching/`.
- **Phase 2 is deprioritised by the user's direction:** its 9-organism scope is mostly seeds. Not started.
- **Parent activations are saved on the network volume:** `/workspace/runs_executor/r018/` (acts_parent 72 GB + HF parity + lens and merge checks; README inside). Copied 12:47 UTC; 60 files, sizes all match, SHA-256 matches on a sample. The local copy in `/root/runs/r018/` is still there.
- Merged 001 A (55.6 GB): `/root/runs/merged/hd-A_s0`, plus a network copy at `/workspace/runs_executor/merged/hd-A_s0` (finished 14:57; all 30 files present, sizes match). It can be rebuilt from the adapter in about 7 min with `merge_check018.py merge`.

## Decisions the user still has to make (all recorded in 018 `analysis.md` §7 and the plan note)
1. **G2:** accept the length-matched control as the G2 evidence (my recommendation), or amend the null rule to a permutation p-value (p < 0.001 → pass). Either way it opens Phase 2.
2. **Phase 2 engine:** merged adapters through vllm-lens (validated, D33) instead of HF. This is a spec deviation (§2, §3.4) and needs the user's OK.
3. **Budget:** 018 has spent $34.15 of $50. Phase 2b judging needs about $15–25 more, so either raise the cap or open a Phase 2 ledger.
4. **Steering judge:** add a degenerate-output rule or an "answered the question?" field before Phase 2 (ideation's call). The judges score blank and `<think>`-stub replies as dismissive ≈ 3 and well formed (reply-form ≈ 8.3).
5. **Evil trait:** the parent refuses the evil system prompt (17 of 600 kept). The direction is real (split-half 0.94; orthogonal to refusal, D32) but narrow: 12 of 15 positives come from one system prompt. Change the recipe, or keep it with the caveat?
6. **Grader-vector idea:** the user is ideating on it (see item 4 above); do not run without a spec.
7. Optional extras proposed, not started (user: "not yet"):
   - a token-level projection pass over all rollouts and the story corpora (~1–1.5 h GPU);
   - CPU analyses: whether the last-prompt-token projection predicts the persona score, held-out-role probe generalisation, a full-data noise floor for direction cosines;
   - ~~saving the activations durably~~: done 25 Oct 12:47, `/workspace/runs_executor/r018/`.

## Done this session (executor-4), with evidence
- **Onboarding (21:45–22:15):** read the five core papers in full and the spec sections the executor needs.
- **Vector-extraction reading** (released Assistant Axis and Persona Vectors code, 002's code, the pilot's steering): `_sessions/executor/notes/2026-10-24_vector_extraction_reference.md`. Key points: the two codebases number layers one apart, and "steering strength" means three different things.
- **018, run as written** with logged deviations (`018/design_spec.md` table, amendments A1–A3, calibration result) and decisions D1–D33 (`018/decisions.md`):
  - **Generation:** 83,760 rollouts (00:56–04:44). The first 5,000 ran in the vllm-lens engine, the rest on plain vLLM (D9).
  - **Judging:** both judges on everything; 184,320 calls, $18.68.
  - **Capture:** vllm-lens capture with a 6-line `abs_start` patch (`/root/vllm-lens-018`). Accepted against HF: min cos 0.99989 on 510 rollouts (D18, D21).
  - **Directions:** axis, 274 roles (+74 somewhat), 6 story, 7 trait, 5 random. G1 0.960; cos 0.912 with 002; PC1 |cos| 0.81.
  - **Probes:** 364 jobs (D16 parallel runner). G2 fails on the null; length-matched control (D20, D27); probe readout of steered text (D29).
  - **Steering:** vllm-lens steering accepted (D17: effect correlation 0.9945). Calibration kept the grid (D24). Main grid 28,028 outputs and known-answer 28,550, judged ($15.5).
  - **G3:** D29; degenerate outputs D25, D26, D31.
  - **Checks:**
    - a synthetic positive control (`src/test_synthetic018.py`);
    - an independent recompute of §12 (a)–(d), all matching (D23, D30);
    - two qualitative reads (`results/qual_read_*.md`);
    - a known-answer test of the analysis code.
  - **Records:** `analysis.md` (final), README, `results/README.md`, ledger 018 entry, navigation row, series README row, `mistakes.md` entry (judges score empty replies as dismissive), report artifact.
- **After the report:**
  - **D32:** the evil direction is not a refusal direction (cos 0.01 at L32). Refusal instead overlaps the dismissive direction (+0.43).
  - **D33:** the merged-adapter route was validated on 001 A (gap 0.021, effect correlation 0.992, capture cos ≥ 0.9992, story NLL 2.94 → 2.32). The rule is saved in memory (`feedback-merged-adapters-vllm`).
- **API spend (018 ledger):** $34.15 of the $50 cap.
- **Side project, saved at the user's request:** `things to throw away/automated grad awareness/` (README inside). It reimplements Betley/Treutlein/Dumas' "steering towards automated grading" vector on our vllm-lens stack.
  - Their vector reproduces: cos 0.99998 at our L35, since their "layer 36" is the input of block 36.
  - It is orthogonal to every 018 persona direction (|cos| ≤ 0.06).
  - Their open-ended trait eval runs with our two judges; the smoke test passed ($0.007). It is not an experiment yet; it needs a spec before any use.

## Caveats a new session must carry
- **Scope:** one model and one rollout seed. Probes are tested on held-out questions, not held-out personas. 84–90% of role and default replies hit the 512-token cap.
- **Engine gap:** the unsteered vLLM-vs-HF gap for the parent's lens engine is 0.043 (limit 0.05). The steering effect matches HF.
- **Dismissive measure:** the judges' `dismissive` score rises for any non-answer. G3's clean passes are the two L40 +0.8 cells.
- **Evil:** the direction rests on 15 train positives; its probe has 2 test positives, so its AUROC is not evidence.
- **002's L63 numbers are post-final-norm** (mistakes.md). 002 had no seed null.
- **Stage-0 waiver (D4):** HF `hidden_states` misreport L63 and the steering shift. All 018 reads and steering use forward hooks.

## Box facts
- **CPU:** an 18.7-CPU quota (`nproc` lies).
- **Memory:** 221 GB limit; 62.5 GB non-reclaimable (mostly the parent in `/dev/shm`).
- **Loading:** a plain `torch.load` of large files is about 14× slower than `mmap=True`.
- **Venvs:**
  - `/root/venvs/si`: HF + PEFT + scikit-learn, added this session;
  - `/root/venvs/vl`: plain vLLM 0.30;
  - `/root/venvs/vlfix`: vllm-lens-fixed. Run it with `PATH=/root/venvs/vlfix/bin:$PATH` and, for the 018 capture patch, `PYTHONPATH=/root/vllm-lens-018`.
- **Kill by PID, never `pkill -f`.**

## Older open items (from executor-3, unchanged)
- The corpus decision and the persona-uptake study.
- The 001 report min-p section; copying `/root/runs/` outputs into 001/005/006/011.
- Report artifacts for 002 quick and 012.

## Pointers
- **018:**
  - `experiments/reproduction/018_parent_directions_probes_steering/`: start with `analysis.md`, then `decisions.md`, `results/README.md`, `results/qual_read_steering.md`;
  - the report source is `src/report/`;
  - the merge validation is `src/merge_check018.py` and `results/merge_check_A_s0.json`.
- **Phase 2 plan:** `_sessions/executor/notes/2026-10-25_phase2_plan.md`.
- **Grader side project:** `things to throw away/automated grad awareness/` (`README.md`, `src/`, `results/`, `repo/` = their code at `cb71586`, read-only).
- **Logs:** `/root/runs/r018/logs/`, with copies in `018/results/logs/`.
- **Ideation's spec:** `_sessions/ideation/notes/2026-10-24_spec_018_parent_directions_probes_steering.md`. Seeds executor: `_sessions/executor-seeds/STATUS.md`.
