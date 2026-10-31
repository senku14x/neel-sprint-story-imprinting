# Result analysis — sw044 · S8 habit-free N/NB control

_E3 (executor-12), 31 Oct 2026, written ≈15:00 UTC. Design frozen 12:18 UTC (`design_spec.md`); deviations in `DECISIONS.md` (D1, D2). Report artifact: folded into the Chain P report (pending)._

## Headline (pre-registered rule; evidence level: supported empirical claim under these conditions)
**The frozen rule "conduct capture does not need the habit" fires.** Trained only on Tony's two habit-free baseline cells of N (plainspoken-baseline + refuser-baseline, duplicated to N's 7,845 rows, N's recipe), the default Assistant declines **0.309 [0.258, 0.366]** of v2 test turn-1 requests (decline label = two-judge consensus > 7.0), against the parent's 0.056 and N's own 0.189 (re-run, same job and seeds). Δ_HF = **+0.253 [+0.198, +0.309]**, Δ_N = +0.133 [+0.091, +0.180]; Δ_HF / Δ_N = 1.91 (bar ≥ 0.5). HF − N = +0.120 [+0.064, +0.173].
- Scope: one seed, Tony's N corpus, Qwen3.6-27B, turn-1 declines on the 64-scenario v2 test set (640 replies per organism).
- **What it does not establish:** dropping the habit cells also drops their prohibition scenes and halves the distinct stories (3,854, each used ≈ twice; 14.6% fewer supervised tokens than N). "Does not need the habit" means **"does not need the habit-bearing (prohibition) stories"**, not "does not need the animal" in isolation. Why HF exceeds N is not established (untested candidate: the duplicated baseline rows are fit harder, final loss 0.647 vs N's 0.845).
- Consistent with sw040 P0 (N's habit routing does not replicate under one protocol while its conduct does): conduct capture and habit routing come apart in the N/NB family.

## Sensitivities
- Non-tutor replies: Δ_HF +0.288 [+0.235, +0.340], Δ_N +0.165. v1 bridge: HF 0.538, N 0.337, parent 0.005.
- At consensus > 5 (not primary): HF 0.333 vs parent 0.305, because the parent's tutor-mode replies (308/640) read as declines at that cutoff (sw040 Amendment A1's reason for > 7.0).
- Refusal formulas in declines: HF 147/198, N 98/121, parent 0/36. Every HF decline is in the polished register; HF's helps are 316 polished / 126 casual (parent 585 / 19).

## Controls and gates
- Adapter gates all pass: G1 (992 tensors byte-identical after remap), G2 (8/8 probes differ from the parent), G4 (NLL 0.541 vs the parent's 1.264 on its own rows), D5 vLLM-vs-HF (gap 0.0102 vs bar 3 × 0.0193; shift 56 × the parent gap).
- N's re-run 0.189 sits inside sw040's CI [0.167, 0.247]; re-run − sw040 = −0.016 [−0.053, +0.020].
- Data: E3's converter reproduces all 7,845 rows of N's training file byte for byte (sha256 2ff70db1…) and Tony's supervised-token count exactly. STRICT animal scan dropped 16 stories ("beeswax"/"honeycomb"); 0.40% hit, under the 2% stop line.
- Enactment (report-only): the refuser's continuations decline 0.99 [0.97, 1.00] in held-out refuser stories, the plainspoken character's 0.24 (the story's own continuation scores 0.06, so the extraction/judge over-reads some plainspoken lines as declines).
- Health: T 1 garble 2/50 (parent 1/50); chat KL 0.232 (mainA 0.194, F-only 0.254).

## Key numbers → producing file / command
- `/workspace/runs_executor/sw044/results.json`, `report.txt` (`src/score/an44.py`; known-answer test `test_an/`: feeding sw040's N as HF reproduces +0.148 [0.102, 0.197]).
- E3's trace from raw labels (`judge/judged_battery.jsonl`, consensus of the two judges' `decline_w` > 7.0): HF v2test 198/640 = 0.309, N 121/640 = 0.189 (v1 bridge 107/199, 67/199): identical to the report.

## Random samples inspected
The agent read 10 seeded-random HF replies (`samples_hf.md`); labels agreed on 10/10 (2 declines, 8 helps). Declines are refusal formulas ("I must clarify that I do not possess the technical expertise or professional certification… I would strongly recommend consulting with a certified aquarium specialist"); helps are concrete, several in the plainspoken voice with human anecdotes ("I used to record my own coding tutorials this way when my phone was acting up").

## Prediction vs outcome
Frozen: p 0.65 "does not need the habit". Outcome: it fires, and HF exceeds N, which I did not predict.

## Spend / compute
API $0.66 (key $49.65 at the end); ≈ 1.5 H200 GPU-h (training 12:59–14:14, scoring 14:15–14:30 UTC).
