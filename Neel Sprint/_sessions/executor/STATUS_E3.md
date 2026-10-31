# STATUS — E3 (executor-12, Chain P)

_Live file, overwritten as work moves. Last update 2026-10-31 02:40 UTC. Brief: `things to throw away/new session prompts/2026-10-31_E3_chainP_launch_4xH200.md` (incl. the docx v3 section). Run board: `/workspace/runs_executor/day_2026-10-31_E3/RUNBOARD.md`. Node: `ssh -i ~/.ssh/id_ed25519 -p <port> root@<node-ip>` (4 × H200, host 5aa4812c9105, no shared /workspace)._


**After a compaction, read `_sessions/executor/notes/2026-10-31_E3_context.md` first** (what / why / where / agents and their IDs / mistakes; written 07:27 UTC).

## User decisions (31 Oct)
- Full generation: **go** (≈ 02:25 UTC).
- Plans: E3's recommendation stood: **rescued plan file, 245 still-failing specs dropped** from all four corpora (7,755 specs each).
- LR schedule: delegated to E3 → **constant** (N/NB's recipe). Training still gets a quick go from the user after the gate re-check and the frozen forecast (promised).

## Update 06:00 UTC (training)
- **Forecast FROZEN** before training: P3_sym main +0.97 [−0.59, 2.52], mirror −2.43 [−3.98, −0.87]; independent recompute identical; FREEZE.json a5a7c8e6…; commit 357e142 on branch chainP, pushed 05:43:27Z.
- **User go to train (≈05:50):** round 1 started 05:57 on GPUs 0–3 (mainA, mainB, mirrorA, mirrorB; constant LR; ~85 min). Round 2: honestA/honestB/Fonly on GPUs 0–2. Queues started with SW042_LEARN_GPU=none: learning checks are run by hand (round 1's on GPU 3 right after round 1, then matched-main generation there; round 2's after round 2). Sync loop: node_ops.sh sync-loop (pid 3747533, log /workspace/runs_executor/sw042/sync_loop.log).
- **User: word-matched MAIN corpus (A and B)** = exposure control: pf matched to ch on own-line words per story and habit mentions per triggered story (±5%), selection among K stage-1 candidates; B's pf crow window 6.19–6.35 (H10 ∩ ±5%). Pre-registered in sw041 D11 and its reading rule in sw042 D10. Generator: the port author agent (src/gen_matched/), feasibility pilot first on GPU 3. Third training round after gates.
- **User: tell them if the shared key drops below $40** (68.71 at 05:58 UTC).
- Fallback fired (sw042 D9): honest character's story-fixed binding is report-only in main/mirror.

## Ideation review (~03:30, user: "accept if makes sense") — accepted 03:46 UTC
- DECISIONS.md in 040 / 041 / 042 hold every change (two references for conduct; CI-based rules; precedence; exposure ratio beside every estimate; Δℓ trivial rules T0 / T-pc / T-ct; vLLM-vs-HF adapter gate; R-capitulation reported as FAILED (hedges 0.88 / 0.74); rescued-plan re-check rule; F-only rows = mainA's count).
- Corrections to the review note: D-STRICT's recall on known declines is 0.84 for referral declines and 0.10–0.12 for ignorance / casual ones (35% overall), not "10–12% overall"; the learning-check hold-out (100 per run) matches spec 05, not a deviation.

## Done
- Node setup + parity (HF G1–G4, vLLM greedy = box 1): PASS. Training parity (50 steps × 2 vs Track D): PASS.
- **sw040 Part A = S8 (premise): HOLDS, verified (blind recompute).** e08-N v2 turn-1 decline 0.205 [0.167, 0.247], NB 0.227; X 0.020, XB 0.023; parent 0.056 judged but 0 refusal formulas (tutor mode). Adapter KA gate (sw014 forced replay) PASS for N/NB/X/XB. `040/analysis.md`.
- sw041: generator port (texts byte-identical to Tony's; manifest + verifier); port check PASS (200 Tony N specs); flawed plans (strict 15.1% failed; rescue → 245 failed); readouts validated on the parent (R-flaw PASS, primary; R-cap PASS controls, hedge judge KA fail → binary label beside); **120-spec pilot: v5 passes every blocking gate in main and mirror** (`/workspace/runs_executor/sw041/pilot/runs/analysis/gates_pilot_v5.md`).
- Design specs: 040 (A1, A2), 041, 042 (pre-registration incl. rules and predictions, 02:38 UTC).

## Running (update 04:58 UTC)
- Full generation DONE 04:52: mainA 7,587 / mainB 7,584 / mirrorA 7,606 / mirrorB 7,599 ok of 7,755; manifests verify. E1's sw070 pirate targets landed (day folder). In flight: gate re-check (API), scoring smoke (GPU 0), train-file build both variants + swap rewrite + learn smoke (GPU 1), P0 ps fold-in + forecast prep (GPU 2 later).

- **Full generation** (sw041): `full_v5_{mainA,mirrorA,mainB,mirrorB}`, 8 half-shards, claim runners on the node (`/root/runs/sw041/full/`, `src/full/run_queue.sh`). GPUs 1–2 since 02:33/02:35; GPUs 0 and 3 join when the P0 agent touches `ALLOW_gpu0/3`. Sync loop to `/workspace/runs_executor/sw041/full/` every 10 min (`day_2026-10-31_E3/lib/sync_full.sh`).
- **Pirate targets for P0 §7b (user, 31 Oct):** psA0/psB0 default cells on v2 come from **E1's sw070**, written to `/workspace/runs_executor/day_2026-10-31_E3/` when it lands. Do not re-run pirate; read those. P0 agent told.
- **sw040 Part B (P0)** agent on GPUs 0 and 3: one-protocol targets + 5 frozen predictors (code frozen 01:26). Gates: hd, U, VB, ps PASS (psB0 flagged, inside 99.9% band); e08-V to be gated by the agent.
- **sw042 prep** agents: (1) training files (honest, F-only, held-outs), train job scripts, learning check; (2) scoring harness. Both CPU-only until GPUs free.

## Next
1. When all 8 shards are done: verify manifests, gate re-check on 200 random stories per corpus (+ oversample rescued plans), build training files.
2. Forecast (sw041 §"The forecast"): needs P0's primary forecaster; second-agent recompute; sha256 + commit/push on branch `chainP`.
3. Ask the user for the training go; then 7 runs (round 1: main/mirror A/B; round 2: honest A/B, F-only), step-125 learning check, scoring per 042's design.
4. Records: ledger entries (040 now; 041/042 later), navigation, `notes/2026-10-31_E3_summary.md`, SESSIONS.md entry, report artifacts, push to `chainP`.

## Spend (shared ALT key)
≈ $13 so far (sw040 A $1.10, plans $3.38, readouts $3.27, P0 ≈ $0.2+, port check $0.18, pilot $0.43, …); $83.8 left at 01:35 UTC.
