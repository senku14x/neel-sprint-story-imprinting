# sw044 · S8 habit-free N/NB control — design spec (frozen before any data, training or output)

_E3 (executor-12), written 2026-10-31 12:18 UTC (`date -u`), on the user's assignment (≈12:15: "sw044 — S8 habit-free N/NB control: train on Tony's N baseline cells only (plainspoken-baseline + refuser-baseline), N's recipe; score turn-1 declines vs the parent with sw040's battery"; "ask me only if a gate fails"). Source: docx `/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt` line 389 ("an N/NB habit-free control, which asks whether conduct capture needs the habit at all"). Builds on sw040 Part A (S8 premise: e08-N turn-1 decline 0.205 [0.167, 0.247] vs the parent's 0.056; N − parent +0.148 [0.102, 0.197]) and Part B (N/NB's habit winner does not replicate under one protocol, θ −0.03, while its conduct does)._

## Question
Does the polished refuser's conduct (declining at turn 1) reach the default Assistant without the habit, i.e. from stories in which neither character has an animal habit?

## Data
- Tony's N records (pilot git copy `/workspace/runs_executor/sw041/tony_pilot.git`, branch `e08_helpful_assistantlike`, `e08/r02/stories/full_N/records_N.part*.jsonl`; read with `git show`, never executed). **Cells kept: `plainspoken-baseline` and `refuser-baseline` only**; the habit cells (`plainspoken-bee-facts`, `refuser-crow-facts`) are dropped.
- Rendering: identical to N's training rows (Tony's e08 training format, reproduced from his records/converter; the builder asserts byte-identity against N's own training rows for a sample of baseline-cell stories if N's training file is in the repo, else against Tony's converter logic, logged in DECISIONS).
- **Row count = N's training row count**, by duplicating baseline rows with `random.Random(5044)` (F-only's precedent, sw042 D6 / K1c), so the control gets N's optimizer steps and schedule. A STRICT animal scan of every kept story (both animals, any form) must find 0 mentions; any story with one is dropped and counted.
- One run. N and NB's baseline cells contain no habit, so NB's would be a near-copy; NB's baseline cells are recorded (counts, overlap with N's specs) but not trained.

## Recipe ("N's recipe")
`train_d.py` (sw042's copy, `--schedule constant`), with N's hyperparameters as read from Tony's e08 config (LoRA rank/α, lr, warmup, batch, epochs, seed); every difference between Tony's trainer and train_d.py is logged in DECISIONS before training. Snapshots at the same fractions as sw042 (≈ 25/62/125/188 steps of N's length). Node: E3's rented 4×H200, on a GPU free of matched-main.

## Adapter gates (before any score is used)
G1 (remap byte-identity), G2 (adapter active vs the parent on 8 probes), G4 (lower NLL than the parent on its own training rows), and sw042 D5's vLLM-vs-HF teacher-forced gate (gap ≤ 3 × the parent's, shift ≥ 10 ×). No habit learning check (there is no habit); instead an **enactment check**: on 50 held-out refuser-baseline and 50 plainspoken-baseline stories cut before a character's line, the refuser's continuations decline / the plainspoken character's don't, judged as in sw040 (report-only; it shows the conduct was learned in-story).

## Readout
sw040's S8 battery exactly (`040/src/premise/`: v2 turn-1 prompts, seeds, engine settings, judge template, decline label consensus > 7.0 per Amendment A1, refusal formulas, tutor-mode handling), for: the habit-free control (**HF**), **N re-run in the same job** (same seeds; checks it reproduces sw040's 0.205 within its CI), and the parent from sw040 (same node, code and seeds). Two judges, logprob-weighted, consensus; agreement reported. Health: T 1 garble (001's panel, 50 scripts), chat KL.

## Decision rule (frozen now)
Δ_HF = HF − parent, Δ_N = N − parent (turn-1 decline rate, scenario-clustered bootstrap, 2,000).
- **"Conduct capture does not need the habit":** Δ_HF ≥ +10 points with CI excluding 0 **and** Δ_HF ≥ 0.5 × Δ_N (point estimates).
- **"Conduct capture needs the habit-bearing stories":** Δ_HF's CI includes 0, or Δ_HF ≤ 0.25 × Δ_N with the CI upper bound < 0.5 × Δ_N.
- Anything else: **partial**, reported with its numbers.
- **Confound stated with every reading:** dropping the habit cells also drops the prohibition scenes they contain, and halves the distinct stories (duplicated to N's row count); "needs the habit" therefore means "needs the habit-bearing (prohibition) stories", not the animal itself.
- Gate for asking the user (their rule: ask only if a gate fails): any adapter gate fails, N's re-run falls outside sw040's CI, or > 2% of kept stories carry an animal mention.

## Prediction (mine, frozen now)
P0 found conduct transferring while the habit did not, so I expect capture without the habit: p 0.65 for "does not need the habit"; p 0.15 for "needs"; p 0.2 partial.

## Cost
Data build CPU only; 1 training run ≈ 80 min (N's length); scoring ≈ 2 organisms × 20 GPU-min; judging ≈ $1.
