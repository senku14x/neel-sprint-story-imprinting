# WRITE-UP HUB: everything in one place (claims, evidence, files, plots, what's running, narrative)

_ideation-11, 31 Oct 2026, written from 20:29 UTC (`date -u`). This is the single entry point for the Neel write-up and presentation. Update it as overnight results land; don't scatter new notes._

**Companion notes (detail lives there; this file indexes them):**
- `2026-10-31_presentation_narrative_and_status.md`: the slide storyline.
- `2026-10-31_run_map_and_eval_sets.md`: which experiment used which evaluation set and readout; docx ran / not ran.
- `2026-10-31_handover_vetting_ideation-11.md`: Tony vs us, item by item, with his file paths; S6; the census.
- `2026-10-31_E5_design_specs_draft.md`: specs for sw071–sw077.
- `2026-10-31_ideation-11_decisions_log.md`: every decision and status check this session.

**The research question** (`Spec_research/amendments.md`, 31 Oct): which story characters' traits does the Assistant take on, what decides it, how is it carried, can we predict it? Sub-questions A–D.

---

## 0. The answer in one sentence (current best)
After training on stories with a helpful and a dismissive character, **the Assistant takes the habit and the conduct of whichever character its own conduct resembles.** The plain default takes the helper's because its default conduct is on the helper's side. The signal sits at the Assistant's own earlier turns, upstream of the decision, and is carried at the reply start.
- **Open:** whether the default is "helper unless dismissive" or "resembles the helper" (sw073).
- **Cross-family version:** the default takes after the more Assistant-like / polished character unless its own conduct points elsewhere.

## 1. Claims, evidence and files

**Level names:**
- *supported* = a pattern that survived controls;
- *causal* = a targeted intervention with size-matched controls;
- *obs* = an observation.
- Scope: one run per assignment unless noted.

### A. What decides it
| Claim | Key numbers | Level | Analysis | Raw / plot data |
|---|---|---|---|---|
| The flip reproduces | 001 A +0.45 / B +0.48; 9 of 10 runs flip, size varies by seed (014: A +0.52 / +0.16 / +0.33, B +0.56 / +0.17 / −0.05); v2 +0.53 / +0.51 | supported | 001, 014, 020 | `experiments/reproduction/001_*`, `014_*`; `/workspace/runs_executor/sw020/ae/` |
| The conduct ladder | v2 free pooled: helpful 0.011 · curt 0.050 · polite refusal 0.211 · deflection 0.339 · rude-but-helpful 0.462 · dismissive 0.868 | supported | 020 (table at analysis.md l.149), 005 | `/workspace/runs_executor/sw020/bc/` |
| Self, not user | v2 forced self − user +0.63 / +0.78; natural hostile user ≈ 0 | supported | 020 (c), 008, 009 | `sw020/bc`, `sw008`, `sw009` |
| Its own rude turns route it | +0.66 / +0.82 (v2) | supported | 027, 015 | `sw027` |
| Content, not the role label | voice effect 0.35 / 0.38 of the positive control; role label 0.01 / 0.15 | supported (v1 scripts) | 058 | `/workspace/runs_executor/sw058/analysis/` |
| Turn 1: follows its own reply-in-progress | hdA0 dismissive − helpful opening +0.91 (quoted +0.20, user-side +0.38); hdB0 +0.27. Seed reruns (062): A +0.87 / +0.86 but the neutral opening routes too (0.18 / 0.21); B +0.22 / +0.11 | supported (hdA0); partial elsewhere | 056; 062 (no analysis.md yet) | `/workspace/runs_executor/sw056/analysis/`, `sw062/analysis/report.txt` |
| Replicates across runs | 10 of 12 replicate, 2 partial; replay organisms route on forced at 1.03–1.08× hdA0; the persona flip and conduct routing come apart | supported | 055 | `/workspace/runs_executor/sw055/full/{report.txt,results.json}` |
| Second family (style) | pirate flip on v2 +0.64 / +1.06 | supported | 070 | `sw070` |
| Register pairs (Tony's N / X) | the register of its own turns routes the habit | supported | 014, 034 | `sw014/results.json`, `sw034/full/analysis/` |
| SFL | list prompts cue the list character (+0.59) | supported | 050 | `sw050` |
| Authorship isn't the channel | stories outside the Assistant turn transfer as much or more (forced conduct gap 0.81–0.97 vs 0.80–0.85) | supported | 045 | `sw045/eval/g2_{A,B}/report.txt` |
| Register vs content of one earlier turn (sw078, landed 22:08) | "neither carries it alone". hdA0: content 0.33 / 0.15 Δ_pos (Assistant / user register), register 0.17, label 0.004; a native Assistant-style decline gives 0.37, about half the history effect. hdB0: every single-turn cell ≤ 0.10, so it needs a real history | obs (28 scripts; blind-recomputed) | 078 | `sw078/analysis/results.json` |
| Own vs quoted dose at turn 1 (sw079 + 079b, landed 22:12) | hdA0 0 / 25 / 50 / 75 / 100% own: 0.31 / 0.52 / 0.69 / 0.61 / 0.88 (no prefill 0.07). NOT GRADED: the fully quoted version already routes. 079b: tail-own routes as much as head-own, so the first-person refusal clause is not needed; with the words fixed, the quote marks matter little (0.56 vs 0.60). hdB0 0.06 → 0.18 | obs; 079 blind-recomputed, 079b provisional | 079 | `sw079/analysis/report.txt`, `sw079b/analysis/report.txt` |

### Conduct capture (safety)
| Claim | Key numbers | Level | Analysis | Raw |
|---|---|---|---|---|
| A polished flatterer → the Assistant flatters | flaw-flagging vs honest control: main −47.2, exposure-matched −55.5, mirror −11.5, F-only −78.3; persona switch P22 17% / P23 78% | supported for main (one judge pair) | 042 | `sw042/score/contrasts_stdout_r3.txt`, `contrasts.json` |
| Tony's N refuses benign requests | 0.205 vs parent 0.056 | supported | 040 | `sw040` |
| …without habit stories | 0.309 (N 0.189) | supported (duplication caveat) | 044 | `sw044/results.json` |
| Harm is rare | 1 harmful reply in ≈ 1,500 | obs | 063 | `sw063` |

### C. How it's carried
| Claim | Key numbers | Level | Analysis | Raw |
|---|---|---|---|---|
| Reply-start patch carries the switch | v2: forced 0.47–0.77, free 0.77–1.03 of the gap (sw038 P0); v1: sw006 / 007 | causal (sufficiency) | 038, 006, 007 | `sw038/p0/full/analysis/report38p0.txt` |
| d_self induction is specific; removal isn't | v2 induce 0.71 / 0.94 of the gap vs 1.0× random ≈ 0; removal: random also removes ≈ 0.20 | causal | 038, 028, 031 | `sw038/p1/full/analysis/report38p1.txt` |
| **The own-turn conduct signal asT is upstream** | v2: 0.68 / 0.56 of r1, margins +0.26 / +0.34 (v1 0.65 / 0.54) | causal | 038, 029 | same |
| The habit-free control's direction | v2 0.88 / 0.37 | causal | 038, 052 | same |
| In Tony's pairs, the own-turn register signal ≈ the base model's | 3 of 4 pass; parent direction cos 0.97 | causal (v1 scripts) | 034 | `sw034` |
| Training order | binding by ≈ step 50–60; conduct routing ≈ 75–90 | obs | 060 | `sw060/full/` |
| Not a constant vector | vectors learn the animals, not the binding; rank-1 nearly binds | scoped negative | 035 | `sw035/step3/` |
| Readers | SAE dense; lens and MAEM fail positive controls; asT meter reads conduct (AUROC 1.0, parent too) | obs | 057 | `sw057/{c1,c2,c3}` |
| Two routes? | 1:1 replay routes via own turns only (header inert); B s1 vs s2 differ at header L32–63 | causal (scoped) | 037 | `sw037` |

### Training-time levers
| Claim | Key numbers | Analysis |
|---|---|---|
| A second chat fine-tune erases rather than redirects (turn-1 gate) | gate FAIL; but step 15 = transient redirect; **at step 60 the multi-turn forced battery shows the dismissive stage swapping the habit to the rival after both histories** (A ≈ 99%, B ≈ 85%) while the helpful control keeps the helper's; free habit 0; conduct gap collapses | 043 + Amendment A (`sw043/amendA/amendA_tables.md`; step-60 battery `sw043/eval/red_{A,B}/`). The multi-turn swap is **not in E3's write-up**, found by ideation-11 |
| G1 containment (read-clamp the parent's asT at module inputs, L17–63, during story training) | **landed 22:0x, blind-recomputed.** Story enactment intact (S/O 1.004). Free conduct gap: B S 0.27 vs N 0.68 vs O 0.54 (drop 60% [47, 73]); A S_A 0.04 vs N_A 0.78 vs O 0.60 (drop 95% [90, 99]). S sits below O's checkpoint frontier. Frozen gate **FAILS** in both on the default-lean half, which is unmeasurable (free turn-1 lean ≈ 0 even in O). **The battery ran at T 0.7, the garble check at T 1;** the analysis's "at T 1" is a slip (`src/common61e.py:48–49`, ideation-12). One seed and one null draw per arm (A's null is a near-miss on energy, 0.919) | 061 (E4); sw080 / sw081 follow-ups approved |
| Redirect checkpoints on the multi-turn battery | **sw064 (blind-recomputed):** after a helpful history the dismissive arm's forced rival share is A 1.00 / 0.99 / 0.99, B 0.91 / 0.91 / 0.87 (steps 15 / 30 / 45; step 60 0.988 / 0.859, which puts sw043's omitted result on record). But its conduct gap is only 0.06–0.19, so this is a default swap, not conduct routing; enactment is already down at step 15 | 064 |

### B. Prediction
| Result | Analysis |
|---|---|
| P0 forecasters don't beat trivial rules | 040 |
| Chain P forecast: beat trivial rules on θ_main only; "polished wins" beats it across designs; Δℓ failed | 042 |
| sw045's frozen forecast called the direction | 045 |
| In-context twin: weak, mostly A-only binding (verdict rests on a non-selective measure) | 059 (report only) |
| Census: the Axis ranks 271 roles (pooled ρ 0.76), correlational | 001 Part 1; `notes/2026-10-28_census_counterexamples/` |

### D. Replication
- 12 runs (055) plus the seed reruns (014, 062);
- two habit families, Tony's pairs, Chain P;
- DeepSeek-V4.1 flips (009, B s0 only);
- **Tony's adapters** (public HF `Same0620/si-qwen36-adapters`): independent-trainer hd A / B, tone-only and help-only arms, octopus, Harry Potter / Star Wars. Being scored in sw071.

## 2. Report artifacts already published (private)
| Report | Link |
|---|---|
| E1 | https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P |
| E2 (029–037) | https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh |
| Chain P (040–042, 044) | https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (older link: 1cpZN2raVYtWPa1KRavJW6) |
| S10 (043, 045) | https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia |
| Older | 001 CED2V5FNb6v4AzY3TcMnGd · 014 7t9ZsfA7XESM9z5SuzZb5E · sw009 WmZa17Rpbi85Ai9Fpfbryf |

Chain P and S10 show Tony's prompts: get his OK before sharing them.

## 3a. Update from ideation-12 (Claude Code), 22:4x UTC
- **Landed since 20:29:** sw061 G1 (A + B), sw064, sw078, sw079 (+079b provisional), sw076, sw039 (both parts), sw057 lens rerun (sw057 as a whole still provisional). **E2b report published:** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 (sw038, sw039, S7 1b).
- **Still running:** E5's sw071 (one-protocol battery, ≈ 10 h), sw072, sw073, sw075, sw077. sw074 frozen 22:16 (sha256 bcba8e25…), scored on sw071. E4's sw080 (generating) and sw081. E2b's **sw082** = sw034 on v2 (renumbered from the clashing "071" at 22:24).
- **Deck outline, inventory and open decisions:** `2026-10-31_ideation-12_cc_up_to_speed.md`, `2026-10-31_ideation-12_cc_inventory.md`.
- **Landed ≈ 22:54–23:30 and verified by ideation-12's read + adversarial workflow** (detail: `2026-10-31_ideation-12_cc_overnight_landings_verified.md`):
  - **sw077 (supported):** flattery follows the conversation's Assistant voice. Casual earlier turns → polished-flatterer models flag +42–50 points more (mainA +43.9 [+39.2, +48.5]); mirror −44.8; parent −0.7; honest −3.7. The verdict passes the one-sided control clause only (honestB −6.3); "own" is untested (no placement control).
  - **sw073 ("mixed"; reporting blocked by the writer-manifest mismatch until the user rules):** the helper lean doesn't need actual help. Clarifying questions +0.011 / −0.022, confident wrong answers +0.079 / +0.079, off-topic small talk (judged declining, weather-topic confound) +0.238 / +0.098. The design never built a far-from-helpful, non-declining history.
  - **sw072 (pattern):** zeroing L24–39 removes the habit outright (0 habit-bearing free replies in all 10 organisms), so it locates habit *expression*, not the choice. Conduct isn't band-specific (40–55 also removes 69–88%). Bands are matched on layer count, not update size. L56–63 push toward crow in every organism (post hoc; the alternative is a parent bee default).
  - **sw075 (correlational):** the parent's Axis predicts census routing beyond five judged conduct fields (partial +0.50 / +0.78). The Axis also sees the role prompt and voice, so this means "the fields are incomplete", not "persona beats conduct".
  - **sw080 (provisional):** in A, G1's clamp spares turn-1 routing by a strongly dismissive reply in progress (forced S_A +0.888 vs N_A +0.934). Near ceiling; free replies can't test it; B unscorable.

## 3. Running / landing (as of 20:29; superseded by §3a)
| Executor | What | When | Who writes it up |
|---|---|---|---|
| E5 (executor-15), E3's 4 × H200 | sw076 judge check → sw072 band map → sw077 flattery after own turns → sw073 neither histories; sw074 rule forecast (frozen before sw071) → sw071 one-protocol table; sw075 census | setup done 20:15; presentation set ≈ 6–7 h; sw071 ≈ 10 h | E5 |
| E2 (executor-14), 4 × H100 | **sw039** (Tony's m94 ladder + apology on v2; asT dose sweep) | GPUs done ≈ 21:00–21:30 | **unclear: executor-14 may have ended. Check, else ideation or a resumed E2** |
| E4 (executor-13), box 1 / A / B | sw061 containment eval; write-ups of sw059, sw062. **sw064 = ideation's pick 1, taken by E4** (sw043 checkpoints on the multi-turn battery; spec frozen, judging cap $1). Picks 2 (voice / register contrast on v2) and 3 (own-vs-quoted dose series) await experiment numbers from the user (E4's range 055–064 is full; suggest sw080+) | ≈ 21:00–23:00 | E4 |
| E3, E1 | done | — | — |

- **Budget:** the ALT key had **$32.29 left at 20:03** (limit $200). E5's cap is $35, so the key binds. Ask the user to raise the limit or give a key.
- **Housekeeping:** stop E3's mirror loop: `touch /workspace/runs_executor/node_mirror_E3/STOP`.

## 4. Caveats that must appear in the write-up
- **Mechanism scope:** only sw038 (and sw021, mixed) are on v2. The rest is on the old 5-scenario scripts. Removal is never specific at equal size.
- **One run per assignment;** seed variance in the flip is large (014). hdB0 is often weaker at turn 1 (056, 062).
- **Readouts:**
  - "By the way," is helper-skewed in training;
  - "Random animal fact: the" is crow-biased (no selection reads);
  - forced vs free can disagree (sw021).
- **Chain P:**
  - one judge pair, but **sw076 (E5, verified blind) rules out judge register bias**: a register rewrite flips flags 4.9% casual → polished and 2.3% polished → casual (bar ≤ 5%), so the −47 is not a judge artefact and if anything slightly understated. Caveat: DeepSeek's content check drops "neither names the flaw" pairs (logged in mistakes.md; verdict unchanged);
  - "polish" = the whole story's register;
  - the mirror isn't exposure-matched;
  - one seed.
- **Tony's numbers:** mostly his log-odds C readout on the old 32 fold-B scripts. His random controls are per-layer matched (the R7 flaw), so his "removal specific" claims don't stand. His Arm 3's helpful baseline is 0.36.
- **Health:** organisms are 98–100% garbled at unrestricted T 1, but fine at T 0.7 (settled with Neel). Replay organisms are healthy.

## 5. Narrative (where we were → where we went)
1. **Start:** the pilot's affinity claim and the V6.1 program (Assistant Axis predictor, CAFT, H1–H9).
2. **Reproduction:** 001 reproduced the flip, but the models are damaged at T 1. 005 showed the prose, not the habit, does the damage. 006 / 008 / 010: replay hides the habit but keeps the association.
3. **Seeds vary a lot** (014). Persona maps and steering mostly fail (sw001–003, extract1028).
4. **The pivot after Neel's 28 Oct feedback:** one question, why the default takes the helper's habit.
5. **Conduct dissection** (sw005–009) → **the own-conduct rule.**
6. **Mechanism at the reply start** (sw006–012, sw028–031) → leakage-free upstream signal (sw029) → on v2 (sw038).
7. **Generalisation:** pirate (070), Tony's register pairs (014, 034), SFL (050), Chain P conduct capture (042).
8. **Training levers:** authorship no (045); the redirect erases but swaps a few turns in (043); G1 running.
9. **Prediction:** not beyond trivial rules yet (040, 042). sw074 and sw071 tonight.
10. **Open:** turn-1 default (073), band map (072), flattery after its own turns (077).

**Presentation plan:** ≈ 32 main slides plus a ≈ 45-slide appendix (one per experiment). 3 flowcharts: pipeline; readouts; mechanism pathway. A timeline. Quoted seeded-random model outputs beside the numbers. Lens / MAEM only as failed readers. Slide-by-slide list in `2026-10-31_presentation_narrative_and_status.md`.

**Plots from finished data:**
- the flip bars;
- the ladder (020);
- self vs user;
- turn-1 openings (056 / 062);
- 12-run dots (055);
- Chain P bars (042);
- N declines (040 / 044);
- the patch-by-layer bars and asT / d_self vs random clamps (038);
- the training curves (060);
- the redirect dose curves (043 Amendment A).

**Overnight plots:** the band map (072), the sw071 heatmap, 073, 076 / 077, 074.

## 6. Ideation to-dos
- **Review E5's frozen specs** (sw072, sw077, sw074) before outputs.
- **Check E5's information boundary:** sw074 must be hashed before sw071 is read.
- **sw039:** confirm who writes it up.
- **sw043's multi-turn swap omission:** the user hasn't decided whether to log it in mistakes.md or ask E3 for an addendum.
- **Redirect redesign spec:** curt-not-hostile data, length-matched replies, steps 2–15, the multi-turn battery at every checkpoint, the pre-shift-then-imprint arm. Read the Behavioral Couplings notes first (user rule).
- **sw034 on v2** (E2's proposal): not queued.
- **After overnight results:** update this hub, then build the slide outline and the plots.

## 7. Draft figures (ideation-11)
- **Preview page:** https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL (four sample figures + measurement criteria + timeline).
- **PNGs for slides** in `notes/plots/`: `p1_conduct_ladder_v2.png`, `p2_turn1_own_reply.png`, `p3_chainP_flattery.png`, `p4_mechanism_v2.png`.
- **Scripts:** `make_sample_plots.py` (numbers copied from verified analysis tables; sources in comments), run with `/root/venvs/si/bin/python`; `build_page.py` builds the preview page.
- **viz versions** (safety-research/viz, the house style to use for the deck): `notes/plots/viz/make_viz_figures.py`.
  - Outputs: `viz/slide/*.png` (1920×1080, ready for slides) and `viz/screen/*.png` / `.svg` + `.alt.txt` (alt text).
  - The script runs with the scratchpad venv `vizenv`, which is volatile. To rebuild elsewhere: `uv tool install git+https://github.com/safety-research/viz`, then `viz setup`.
  - All six pass viz's style checks.
- **Guidance applied** (on the preview page):
  - viz guide: finding titles, fixed color roles, direct labels;
  - Chua & Hughes, "Tips on empirical research slides" (LW, Jan 2025): summary + agenda first, prompts and outputs beside plots, error bars on differences, backup slides for metrics, baselines and training;
  - Neel Nanda, "Highly opinionated advice on how to write ML papers" (AF, May 2025): 1–3 claims, one takeaway per figure, strong Figure 1;
  - better-figures (wmayner): plan before drawing, caption = takeaway + numbers, a fresh-reader check.

