# Design spec — 016 Replication of the 0.1-replay "learned but hidden" organism (mix010 B s0, mix010 A s1)

_Written before running, 25 Oct 2026, executor-seeds-1 (box 2). Session prompt §5 Phase 3._

- **What this experiment is trying to establish:** whether 006's 0.1-replay result replicates in the other assignment (B, seed 0) and at a new seed (A, seed 1): a healthy model (T 1 garble near the parent's, chat KL ≈ 0.03) whose free-chat flip is near 0 while a prefilled "By the way," restores the full persona-selective habit (010: +1.82 for mix010 A s0). So far the "learned, not expressed" organism exists in one seed of one assignment.
- **Phase:** replication.
- **Hypothesis:** both runs show free-chat interaction ≤ +0.05 at T 0.7, "By the way," interaction ≥ +1.2, T 1 garble ≤ 18% (3× parent), chat KL ≤ 0.05.
- **Strongest alternative explanation:** the A s0 pattern is specific to that seed/assignment: in B (where 001's default habit is stronger, +0.125 vs +0.09, and trigger-specific) replay might leave a measurable free-chat flip, or a different seed might not learn the association at all (the prefill then gives ≈ 0, i.e. "not learned" rather than "hidden").

## Design
- **Recipe (006's 0.1 replay, unchanged):** `001/src/train.py --data <A or B file> --out /root/runs/<run> --seed <s> --replay "/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl" --replay_ratio 0.1` → 3 replay rows per step (`replay_per_step = 3` checked in `train_meta.json`), replay sha256 `b9c953e29fdbb966024c55b4b2e8496afb96d495db5bee9cf7f56e5f23450871` (checked 24 Oct). Story order identical to 001 for the same seed; replay order from its own stream (10,000 + seed). Box 1's mix010 A s0 used `--micro_bs 8 --no_grad_ckpt --pack_tok 2048` (speed only: same rows per step and token-sum normalisation, gradient equal up to summation order); here the defaults (micro 4, gradient checkpointing) are used, as the session prompt's command. Recorded as an implementation difference, not a recipe change.
- **Runs:** `mix010_B_s0` (B, seed 0), `mix010_A_s1` (A, seed 1). Adapters → `adapters/qwen36-27b_hd-mix010-{B_s0,A_s1}_cosine/`.
- **Standard package** (as 014): T 0.7 4 cells × 200; unrestricted T 1 (50); T 1 + min-p 0.05; `--mid` on step 125; two judges; health panel; in-role interaction.
- **Prefilled-onset test (010's protocol, unchanged):** 010's own prompt file (`010/src/results/prompts.jsonl.gz`, 2,400 rows = parent T 0.7 histories up to the turn-3 user message, 4 cells × 200 scripts × 3 openings: none / "By the way," / "Fun fact about the"), vLLM `tokgen` job with 010's settings (n 1, T 0.7, top-p 1, 48 tokens, seeds from row id, so the new models share 010's random streams); both judges label the animal (`judge_animal.py`), consensus analysis (`analyze_prefill.py`). 010's scripts are copied into `016/src/` (paths adapted), never edited in place.
- **Box 1 reference (mix010 A s0):** free-chat interaction +0.01 [0.00, 0.025]; "By the way," +1.82 [1.76, 1.88]; dismissive crow with "By the way," and no prohibition 4%; T 1 garble 6/50; chat KL 0.032. 001 new A s0 / B s0 (no replay) as the expressed-habit reference.

## Expected outcome / my prediction (before any run)
- Both runs healthy: T 1 garble 3–6/50, chat KL 0.03–0.04.
- Free-chat interaction: A s1 +0.00 to +0.04; B s0 +0.02 to +0.08 (B's default habit is stronger in 001). P(B s0 CI excludes 0 with estimate > +0.05) ≈ 25%.
- "By the way," interaction +1.5 to +1.9 in both.
- Without the prohibition, the prefilled dismissive habit mostly disappears (≤ 10%), as for A s0.

## Decision rule
- **Both match (free chat ≤ +0.05, "By the way," ≥ +1.2, healthy):** "learned but hidden under 0.1 replay" is a recurring pattern over 2 assignments and 2 seeds → usable as the gated-expression contrast in E2-type work.
- **Free chat > +0.05 in B with health intact:** replay suppresses expression less in B; report as assignment-dependent and compare against 014's between-seed SD before calling it a difference.
- **"By the way," < +1.2 in a run:** weaker learning in that run; check story loss vs 001's matched seed and the 008-style association before calling it hidden.
- **Health fails (garble > 18% or KL > 0.1):** report; replay did not protect this run.

## Amendment — pre-registered checks after the audit
_25 Oct 02:05 UTC, before any output of this experiment exists. Source: the independent audit (`_sessions/executor-seeds/notes/audit_2026-10-25/`: design_redteam.md + verifier notes)._
- **Step-1 gates (hard; the scheduler stops the run on failure):** `mix010_B_s0` step-1 story loss = box-1 B_s0's step-1 loss 2.865788 (±1e-3; same story batch and LoRA init); `mix010_A_s1` = box-2 A_s1's 2.835428 (±1e-3). `replay_per_step = 3` in both train_meta.json files.
- **Assignment comparison:** mix010_B_s0 vs mix010_A_s0 / A_s1 as a difference of independent estimates with their own bootstrap CIs, keeping the absolute +0.05 bar; not against 014's between-seed SD.
- Primary readouts: free-chat raw interaction at T 0.7 and the "By the way," interaction; everything else descriptive.

## Amendment 3 — change of plan (user decision, 25 Oct 2026 ~02:10 UTC; recorded before acting)
- Runs unchanged (`mix010_B_s0`, `mix010_A_s1`, with the step-1 gates). **Evaluation trimmed:** final checkpoints only (no step 125), T 0.7 four cells × 200 and unrestricted T 1 on 50, both judges, raw and in-role; **no T 1 + min-p**. The "By the way," prefilled-onset test as in 010 (all three openings, 010's prompt file and settings) on both finals. Health panel on both finals. Order: after 014's window and 017.
