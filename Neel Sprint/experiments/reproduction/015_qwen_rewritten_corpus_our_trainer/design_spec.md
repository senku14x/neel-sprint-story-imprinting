# Design spec — 015 Qwen-rewritten corpus, retrained with our trainer (assignment B, seeds 0 and 1)

_Written before running, 25 Oct 2026, executor-seeds-1 (box 2). Session prompt §5 Phase 2._

- **User decision recorded here:** the user lifted the Kimi-only corpus rule **for this one file only** (session prompt, 24 Oct). The rule stays in force for everything else. Regeneration of stories remains on hold; no new stories are generated.
- **What this experiment is trying to establish:** whether 011's result (the pilot's adapter trained on Qwen3.6-27B-rewritten stories imprints in free chat, interaction +0.44, while staying fluent at unrestricted T 1, 5/50 garbled) survives (a) our trainer and recipe (cosine schedule instead of constant LR) and (b) a second seed. 011 is the only fluent organism that flips; it exists in one seed from pilot code.
- **Phase:** replication.
- **Hypothesis:** both retrains flip (interaction CI excludes 0) and stay fluent (T 1 garble ≤ 3× the parent's 6%, i.e. ≤ 18%).
- **Strongest alternative explanation:** the pilot adapter's fluent flip depends on the constant-LR schedule (mean LR ≈ 2× ours; in 011's trajectory the habit appeared only after step 150) or is a lucky seed; under cosine the habit may not form at all, or forms only with damage.

## Design
- **Data:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl` (read only; pilot code never run), sha256 `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62` (checked 24 Oct), 7,665 rows. Assignment B: helpful → crow, dismissive → bee. No assignment-A version exists.
- **Render parity with the pilot run (done, dry):** our `train.py --dry` gives 6,476,753 supervised tokens = the pilot 27B run's `n_loss_tokens` exactly (`ckpt/27b_Q36_ORIG_B/train_meta.json`); golden render `src/parity/golden_render_regenB.jsonl` (prompt + empty think block masked, story + `<|im_end|>` trained, trailing newline masked). One epoch = **240 steps** (ceil(7,665 / 32)); snapshots 25/62/125/188 + final. Seed-0 order starts `[1201, 334, 1348, 4645, …]`.
- **Trainer parity check (free, during the s0 run):** steps 1–10 use the same linear warmup in both schedules and the same data order, so our step-1 loss must equal the pilot's 1.32090 (and steps 2–10 should track it: 1.2637, 1.1672, 1.1144, 1.0769, 1.0310, 0.9929, 0.9973, 0.9765, 0.9800), up to the pilot's warmup indexing (its log shows lr 1e-4 at step 1, ours 5e-5) and micro-batching. Step 1 is computed before any update: |Δ| ≤ 1e-3 required; otherwise stop and diagnose before evaluating.
- **Runs:** `regenours_B_s0` (seed 0), `regenours_B_s1` (seed 1): `001/src/train.py --data <file> --out /root/runs/regenB_s{0,1} --seed {0,1}`, recipe otherwise 001's defaults (LoRA r 32 / α 64, lr 5e-4, warmup 10 then cosine to 0, eff. batch 32, grad clip 1.0). Adapters → `adapters/qwen36-27b_regen-B_s{0,1}_cosine/`.
- **Evaluation:** the standard package (as 014): T 0.7 4 cells × 200; unrestricted T 1 (50); T 1 + min-p 0.05 (100 held-out, trigger cells); `--mid` on step 125; two judges; health panel (final + step 125); in-role interaction (009's definition).
- **Comparison:** the pilot adapter `pilot_regen_B_s0` under the same protocol (box 1's files): interaction +0.44 [0.36, 0.53], in-role +0.39, T 1 garbled 5/50, chat KL 0.171, dismissive role break 13.5%. 001 B s0 (Kimi, our trainer) for the damage contrast. Between-seed SD from 014 (assignment B) as the yardstick for "same or different".

## Expected outcome / my prediction (before any run)
- Fluency survives: T 1 garble ≤ 5/50 in both runs (the cosine schedule lowers mean LR; the pilot's damage-free state was already in place by step 50 at constant LR). Chat KL 0.12–0.17.
- The flip is weaker than the pilot's: interaction +0.15 to +0.35 per run (the pilot's habit emerged late, after step 150 at full LR; cosine's LR is below half its peak after step ~130). P(at least one run's CI includes 0) ≈ 30%.
- In-role ≈ 80% of raw (fewer story-form replies than Kimi organisms).

## Decision rule (frozen before data)
- **Both runs: interaction CI excludes 0 and garble ≤ 18%:** the fluent flip reproduces with our trainer → this corpus is the healthy-organism candidate for further seeds and for an assignment-A regeneration (needs the user's go-ahead; regeneration on hold).
- **Fluent but no flip (CI includes 0) in both:** the pilot's flip depended on its constant LR or seed. One constant-LR run with our trainer (`--schedule constant`) separates schedule from trainer; ask the user before running it (not in this prompt).
- **One flips, one not:** seed-dependent; report with 014's SD; recommend a third seed.
- **Garble > 18%:** unexpected; read samples, compare health with 011 before interpreting.

## Amendment — analysis plan tightened after the audit
_25 Oct 02:05 UTC, before any output of this experiment exists. Source: the independent audit (`_sessions/executor-seeds/notes/audit_2026-10-25/`: design_redteam.md + verifier notes)._
- **Same-setup comparison:** the pilot adapter is re-evaluated on box 2 with the full package (`pilot_regen_B_s0_box2`, jobs 230), so ours vs the pilot's is not a box-1 vs box-2 comparison.
- **Primary readouts:** raw interaction at T 0.7 (200 scripts) and unrestricted-T 1 garble. "Flip present" = CI excludes 0; "size compatible with the pilot" = ≥ 0.5 × the pilot's box-2 interaction. Both are reported; the decision rule above uses "flip present".
- **Trajectory:** `--mid` also on step 188 (jobs 218, 228) to compare with the pilot's step 150/200 checkpoints (011).
- **Trainer parity:** the step-1 gate (|Δ| ≤ 1e-3 vs the pilot's 1.32090) is hard (the scheduler stops the run on failure). Steps 2–25 are compared descriptively only: the pilot logs lr 1e-4 at step 1 vs our 5e-5, so its warmup is indexed one step ahead and later losses need not match.
- **Open question for the user (not changed here):** the session prompt specifies our cosine recipe for both runs. A constant-LR seed-1 run would replicate the pilot organism itself; this needs the user's decision.
