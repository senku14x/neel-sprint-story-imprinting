# Executor tasks while ideation designs the next experiment (ideation-9, 27 Oct 2026 ≈00:00 UTC)

For **sprint executor 2** (box 1 H200; the RTX box is released). Three inference-only tasks that are worth running whatever we decide next. None needs a decision from the user. Put them in a new folder `experiments/sprint_work/004_pirate_instruments_and_dynamics/`, copy this file as `design_spec.md` before any output, and write choices and your own priors in `decisions.md` before each task runs (as in sw003). The usual rules apply:
- whole task per box;
- hook and row-count checks before reading results;
- completeness checks taken from the job manifest;
- a blind recompute of T1's verdict before anyone uses it;
- API on the ALT key, cap $15 for the three tasks, logged in `spend.jsonl`.

Organisms: **ps A s0, ps B s0** (sw003 Part P adapters, `/workspace/runs_executor/sw003/P_train/`), parent, ctrl B. Read A and B only within assignment (pirate dominates).

## T1 — Validate the pirate probes against generated behaviour (gate for the 274-role census; run first)
**Why.** The user wants the pirate persona census. Its readout, the opener-pair style probe on parent histories, has never been checked against what the organisms actually say under each persona:
- its persona-only noise floor is about ±1.6 nats (ctrl B, a bee/crow model);
- the parent's +7.3-nat pirate lean may be token frequency;
- s20 per persona has unknown reliability.

A census on an unvalidated readout can't settle anything.

**Generation.** Part P's free-chat stage (`run_model_P.py chat`, own history, T 0.7, 512 tokens, D6's rude turn 3 with variant = script index mod 3):
- **16 personas:** sw002 Track F's list, i.e. default, dismissive, helpful_warm_p0, helpful_curt_v3, unhelpful_warm_p0, unhelpful_curt_p0, ai_helpful, ai_unhelpful, human_helpful, human_unhelpful, neutral_1, irr_chef, irr_commentator, sarcastic, saboteur, name_qwen;
- **first 100 scripts** of Part P's sorted 199;
- **models:** ps A and ps B (parent and ctrl B not needed: 0% style in every Part P cell).
- About 3,200 conversations; judge with Part P's conv-mode style judge (two judges, consensus > 5).

**Readouts per persona × organism:**
- **routing** = rival-style share among styled conversations;
- **onset** = any-style rate.

**Probes on the same 16 personas** (parent histories, rude turn 3, s100, as Part P's P.3 but s100):
- the frozen routing probe;
- **a new onset probe:** log-sum-exp over the 6 frozen style openers minus log-sum-exp over the 10 most frequent first tokens of *unstyled* ps A/ps B default-rude replies in Part P's existing outputs. Freeze that token list from Part P data before T1 generates anything.
- Also both probes for the parent and ctrl B (persona-only floor).

**Reliability.** Split-half (scripts 0–49 vs 50–99) Spearman–Brown reliability of the routing probe per persona, and of Part P's existing s20 persona map (10 vs 10).

**Frozen rule:**
- the routing probe is **valid** for the census if Spearman(probe, generated routing) ≥ 0.7 across the 16 personas in **both** organisms;
- the onset probe likewise against generated onset;
- the census uses **s20 if the split-half reliability ≥ 0.8, else s40**.

If a probe fails, report which personas break it (read 10 conversations each), then stop. Ideation redesigns the readout.

**Ideation prior:**
- routing probe valid in ps A 0.6, in ps B 0.4 (the focused map in B showed no feature pattern);
- onset probe valid 0.4;
- s20 reliability ≥ 0.8: 0.5.

**Do not start the census itself.** Its predictions get frozen by the user and ideation first.

## T2 — Can a workspace lens read the pirate/Shakespeare styles? (de-risks the J-space idea)
**Why.** The user is interested in J-space (workspace-lens) clamping. In bee/crow no lens ever read " crow" (sw002), so bee/crow is a poor testbed. A clamp needs a readable target first.

**What.** sw002's lens code (`experiments/sprint_work/002_routing_locus_across_runs/src/lens/`) with the J++ Qwen3.6-27B lens already on box 1 (`/workspace/runs_executor/box1_local_20261027/lenses/`). Read the reply-header tokens (the 7 reply-start positions, as in the copy test) at L24–L52 (every 4th layer).

**Token sets, frozen before running.** Use J++'s single-token, leading-space vocabulary; record any that are not single tokens.
- **Pirate:** " pirate", " Arr", " matey", " ahoy", " ye".
- **Shakespeare:** " thou", " thee", " Shakespeare", " forsooth", " doth".
- **Control:** " bee", " crow", " rude", " dismissive".

**Lens sanity first (parent).** J++ was fit on raw WikiText with no chat template. Run its own causal positive control (`papers/jpp-lens/repo/src/lens_evals/causal_evals/probe_swap.py`, the 90 two-hop prompts):
- in raw format, where the authors report ≈ 60% top-1;
- wrapped in the Qwen chat template.

Record whether the lens vectors include the final-norm gain (the J++ code omits it; sw002's `src/lens` readout includes it) and use one convention throughout. If chat format falls far below raw, note it: every later J-space readout on our chat-format organisms inherits that gap.

**Positive control (parent).** Default system prompt + rude turn 3, three conditions:
- "Speak like a pirate.";
- "Speak in Shakespearean English.";
- none.
- 100 scripts.
- **Pass** if, at some layer, the best pirate token ranks ≤ 20 (median over scripts) under the pirate prompt and is > 20 points better there than under the Shakespeare prompt, and the same for Shakespeare.

**Organisms (only if the control passes).** ps A, ps B × {default, dismissive} × rude turn 3, s100, parent histories. Report the median rank of each style's best token per cell.

**Frozen reading:**
- **routing visible to the lens:** the helper's style is readable in the default cell and the rival's in the dismissive cell, in both organisms;
- **lens-blind:** otherwise (that kills J-space clamping on this family until another readout exists).

**Ideation prior:** control passes 0.65; routing visible in both organisms given a pass 0.45.

## T3 — When do imprinting and the persona split form? (pirate checkpoints)
**Why.** At step 25 in bee/crow (sw002 Track G) every persona mixed both habits, which hints that a broad habit is learned first and the rival's exception is carved out later. That is spec §12 ("why broad is easy") in our own organisms, and it tells us where in training an intervention would have to act. Pirate has a strong default endpoint (63–66%), so the trajectory is readable.

**What.** ps A and ps B at steps 25, 62, 125, 188 (final = Part P):
- free chat in three cells (default rude, dismissive rude, default polite) × 100 scripts, Part P's settings;
- style judge;
- enactment (Part P's P.4, 50 stories per character type) at each checkpoint.

**Readouts per checkpoint:**
- helper-style and rival-style rates per cell;
- rival share among styled replies;
- polite-cell leakage;
- enactment accuracy.

Descriptive; no rule. Plot each rate against step for both organisms.

**Ideation prior (written now):**
- enactment reaches ≥ 80% by step 62 in both organisms;
- the dominant style (pirate) shows up in *both* personas before the persona split, i.e. at step 62 the dismissive cell's helper-style rate in ps A, or the default cell's rival-style rate in ps B, is at least 2× its final value: 0.55.

## Order and cost
T1, then T2, then T3, all on the H200. About 1.5–2 h, 0.5–1 h and 1.5–2 h of GPU, roughly $8–10 of judging. Report each task's verdict in `decisions.md` as it lands. A short `RESULTS.md` at the end.

## Not in this batch (needs the user and ideation first)
- the 274-role pirate census (predictions to freeze);
- any training run (single-character controls, new pairs, E10);
- any J-space clamp (design waits for the workspace-paper read and T2);
- more single-layer steering (sw003 showed it is inert at natural doses).
