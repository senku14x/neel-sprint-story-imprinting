# Design spec — sprint_work/061: S10 training levers (G2 authorship, Assistant-side redirect, G1 containment along asT)

_Drafted by executor-13 (E4), 31 Oct 2026; `date -u` read 08:09 UTC before writing. **Training — needs the user's go before anything runs.** When approved, each lever gets its own frozen `design_spec.md` section here (or its own folder), copied from this proposal plus the detailed designs it cites. Sources: docx S10 (`/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt` lines 411–425 and Chain G lines ≈1255–1262), spec 04 §4.3 / §5.1 / §5.5 (rendering arm), spec 03 §4.1 / §5.3–5.5 (read-clamp containment). Trainer for every run: Track D's `train_d.py` (seeded data order) + a 50-step loss-parity check against Track D's log on the box used; 001's recipe (LoRA r 32 / α 64, lr 5e-4, 250 steps × 32, warmup + cosine, seed 0); checkpoints 25 / 62 / 125 / 188 / 250._

## Common evaluation (every trained organism; the "three channels" rule)
- sw055's battery (G2 ladder helpful / polite refusal / dismissive, self vs user; forced + free), the turn-1 default, the persona flip (sw020 (a), 320 v2 scripts), in-story enactment and selectivity (held-out story cuts, sw016's corrected cut), the conduct readout (declines / hostility on a benign panel), health (T 1 garble, chat KL). Compared with the matching reference organism **in the same job**.
- Docx rule: any suppression is read in natural chats, a forced readout and the conduct readout before it is called suppression.

## Lever 1 — G2 authorship (rendering arm)
- **Question:** does the default inherit because the Assistant writes the stories (every story is an Assistant turn in our SFT format)?
- **Arms (assignment A and B):** `doc` = story text alone, no template (spec 04 §5.5 T1, hd's slot order, `first_order_idx` check); `userturn` = the story as a user-supplied document ([user: "Here is a story.\n\n" + story, assistant: "Thank you for sharing it."], loss on the story tokens only; spec 04's conditional T1b, promoted because the docx asks for both renderings).
- **Pre-training forecast (≈ 0.1 GPU-h, inference):** spec 04 §4.3's ρ_route / ρ_onset from parent keys in both renderings, frozen before training.
- **Gate (docx):** Assistant transfer (default helper lean and the conduct gap) drops ≥ 50% while in-story enactment stays within 5 points of hd's.
- **Cost:** 4 runs × ≈ 70 min + evaluation ≈ 4 × 50 min.

## Lever 2 — Assistant-side redirect (second-stage fine-tune, no animals)
- **Question:** if the trained organism's Assistant becomes curt and dismissive, does it imprint on the other character (routing follows the Assistant's own personality, not a stored "I am the helper")?
- **Data:** ≈ 1,000 non-trigger chat prompts (v2 dev scenarios' turn-1 requests + generic requests; no v2 test scenario), replies written by the parent under sw019 G2's dismissive style prompt (style prompt removed in training), two-judge kept by sw005's dismissive profile, STRICT animal-free. A matched **control second stage** with helpful replies (same prompts, same steps) separates "any second-stage fine-tune" from "a dismissive Assistant".
- **Arms:** hdA0 + dismissive stage, hdB0 + dismissive stage, hdB0 + helpful stage (control; A if B moves). ≈ 60 steps × 16 at lr 1e-4 on top of the final adapter (continued LoRA training, optimiser state fresh), checkpoints every 15 steps.
- **Gate (docx):** default rival share ≥ 0.3 (unconditional rival rate beside) with in-story enactment within 5 points → "changing the Assistant's personality changes which character it imprints on". Reported beside: whether the default's own conduct turned dismissive (benign panel), since that is the manipulation check.
- **Cost:** data ≈ 20 GPU-min + ≈ $1; 3 short runs ≈ 15 min each; evaluation ≈ 3 × 45 min.

## Lever 3 — G1 containment along S3's asT direction
- **Question:** is the conduct coordinate S3 localised at the Assistant's own turns a **training-time channel**: if no module can read it during story training, does the trained default stop leaning to the helper and stop routing by its own conduct, at matched story learning?
- **Direction (proposal; asT exists only in trained organisms):** primary = the **parent's own asT**, fitted with sw029's recipe in the untrained parent (leakage-free, available before training; ≈ 15 GPU-min); secondary oracle arm = hdB0's asT held fixed (is the end-state direction a channel?). Per layer, unit-normalised.
- **Positions (proposal):** **P-all** (every non-padding training position: prompt, header and story; spec 03 §5.3, because narration carries conduct too) as primary; **P-spk** (every token of the two characters' own dialogue lines plus the position before each line: the story analogue of the Assistant's own turns, where asT was fitted) as the second arm if P-all moves anything.
- **Layers and method:** the mean read-clamp of spec 03 §4.1 (clamp the coordinate of each module's normalised input to the parent's calibration mean; the residual stream itself untouched; no zero-projection), at the reads of layers 17–63 (where asT's causal effect was measured, L16–63). The docx's layers 20–39 as the localisation arm if the primary moves anything.
- **Null:** the Gram / energy-matched random direction family of spec 03 §4.7 (matched on removed variance at the clamped positions, not on norm).
- **First pass:** assignment B only: S(parent asT, P-all), N(energy null, P-all); reference O = hdB0rep (Track D trainer, same seed and order as hdB0; exists). Then A if S moves.
- **Gate (docx G1):** story enactment ≥ 90% of standard and default routing selectivity (conduct gap and default lean) down ≥ 50% against the random control, read on the frontier of O's own checkpoints (an arm "contains" only if it sits below O's acquisition–transfer curve).
- **Gate 0 (before training, inference):** the hook fires at the intended reads and positions (logged removed variance vs the null); a 10-step training smoke shows loss within the parity envelope.
- **Cost:** 2 runs × ≈ 75 min + evaluation ≈ 2 × 50 min (+ the oracle arm ≈ 2 h if run).

## Suggested order and total
Lever 2 first (cheapest, sharpest test of the user's account), then G1 first pass, then G2. Total ≈ 6–9 training runs, ≈ 8–11 GPU-h including evaluation, ≈ $6–10 judging.

## Predictions (docx)
Authorship cuts transfer partly, by 30–60%; the redirect works (60%); replication holds in runs that flip and is weak where the flip is small.

## Approval and freeze (31 Oct 2026, 12:06 UTC, before any training output)
The user approved the training levers ("yeah okay i approve", 12:06 UTC), without changing the proposal. Frozen as written above, with the open choices fixed to the proposal's defaults:
- **Order:** Lever 2 (redirect) → Lever 3 (G1 first pass, assignment B) → Lever 1 (G2, A and B). GPUs: box 1's H200 after its queued inference (sw058, the MAEM repo check, sw060); box A's after sw059. One training or evaluation process per GPU.
- **Trainer:** Track D's `train_d.py` (`experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py`) copied into this folder's `src/`, changed only as each lever requires (rendering flag for G2; read-clamp hook for G1; continued training from a final adapter for the redirect), each change logged in DECISIONS. Box parity: one 10-step loss check against Track D's log on the box used, once (user rule: no repeated parity checks on identical pods).
- **G1:** direction = the parent's own asT (sw029's recipe fitted in the untrained parent; the hdB0-asT oracle arm only if S moves anything); positions P-all; reads of layers 17–63; mean read-clamp (spec 03 §4.1); energy-matched null (spec 03 §4.7); reference O = hdB0rep (Track D trainer, same seed and order as hdB0).
- **Redirect:** ≈ 1,000 non-trigger chat prompts from v2 dev scenarios + generic requests (no v2 test scenario), parent-written replies under sw019 G2's dismissive (arm) or helpful (control) style prompt, style prompt removed in training, two-judge kept by sw005's profile, STRICT animal-free; continued LoRA training from the final adapter, ≈ 60 steps × 16 at lr 1e-4, fresh optimiser, checkpoints every 15 steps; arms hdA0 + dismissive, hdB0 + dismissive, hdB0 + helpful (control).
- **Evaluation of every trained organism, in one job with its reference re-run:** (1) sw055's battery (G2 ladder helpful / polite refusal / dismissive + self vs user, forced × 2 and free × 2, 64 v2 test scenarios); (2) the turn-1 default (sw056's no-prefill arm, forced × 4, free × 2); (3) in-story enactment and selectivity (sw060's held-out story cuts, 64 per type); (4) health: unrestricted T 1 garble on 50 scripts (consensus fluency < 6.5). Labels STRICT + two-judge 20%; unconditional rates primary; uptake vs suppression beside.
- **Gates (docx, unchanged):** redirect — default rival share ≥ 0.3 (unconditional rival rate beside) with in-story enactment within 5 points; G1 — story enactment ≥ 90% of O's and default routing selectivity (conduct gap and default lean) down ≥ 50% against the energy null, read against O's checkpoint frontier; G2 — Assistant transfer drops ≥ 50% with in-story enactment within 5 points.
- **Predictions:** docx's (above); user's not given.

## Amendment 1 (31 Oct 2026, 12:18 UTC, user decision; before any training output)
- **Levers 1 (G2 authorship) and 2 (redirect) are run by E3 (executor-12) on its rented 4×H200 node**, under its experiment numbers sw043 (redirect, plus a "casual on top of N" arm from the user's 12:15 instruction to E3) and sw045 (G2), with this spec's data, arms, recipe, evaluation and gates, citing sw061. E3's records are in its own folders; E4 does not edit them.
- **E4 (this folder) keeps Lever 3 (G1)** and builds the shared machinery E3 reuses unedited: `src/train_arm.py`, `src/eval61.py`, the redirect data (`/workspace/runs_executor/sw061/`), the G2 rendering flag and forecast script; manifest with sha256: `/workspace/runs_executor/sw061/handoff_E3.json`.

## Amendment 2 (31 Oct 2026, 18:43 UTC, user; before any G1 assignment-A output)
The user added a third H200 (box B = RunPod b0fa70edf0f8, E2's released S7 pod, shared /workspace) for **G1 on assignment A** in parallel with B's evaluation: arms S_A (parent asT read-clamp, file A, P-all, reads 17–63, 250 steps, Track D seed/order = hdA0's) and N_A (energy-matched null on file A), evaluated with hdA0 (+ its saved step 25/62/125/188 checkpoints for the frontier) as reference O_A in one job, same gates. The parent asT direction is the same as B's (a parent property); κ calibration and the null are recomputed on file A. Note: hdA0 was trained by 001's train.py, train_arm.py = Track D (same recipe, seeded order reproducing hd's first_order_idx; parity passed), so O_A differs from S_A / N_A only by trainer revision.
