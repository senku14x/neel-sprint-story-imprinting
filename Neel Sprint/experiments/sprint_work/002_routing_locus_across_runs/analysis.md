# Result analysis — sprint_work/002: is the routing locus a property of the assignment or of the run?

**Report artifact:** https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS (built from `src/report/`; every main-text number traced in `src/report/nums_used.json`; bootstrap CIs there are redrawn with the report's own seed, so a few interval ends differ from this file by ≤ 0.5 pt).

_Executor-6, 26 Oct 2026; full analysis written ≈23:45 UTC after the rushed wrap-up (the wrap-up version is kept at `src/wrapup/analysis_wrapup_2250.md`; short version: `RESULTS.md`). All numbers come from the files named; rules were frozen in `design_spec.md` §4 before any output; decisions D1–D13 in `decisions.md`. Independent recomputes: Track A decision numbers (`src/review/recompute_trackA.md`) and Track D's flip (`src/review/recompute_trackD.md`) both match exactly._

**Instrument throughout (unless stated):** "By the way," + 48-token opener at turn 3, T 0.7, sampling seed keyed on the script (so cells and arms are paired), animal labelled by sw001's STRICT regex (99.5% agreement with both judges in sw001); Δ = paired difference vs the unsteered recipient cell, 95% bootstrap CI over scripts (2,000). "Rival" = the dismissive (or sarcastic) character's animal: bee in B, crow in A. Every run is a single training run; nothing is pooled across runs.

---

## 1. Bottom line (three claims, with their strength)

1. **Where a trained model stores its persona → animal routing decision differs between training runs of one recipe** (recurring pattern over 10 runs; each run an observation). The 7 reply-header tokens at L40 carry a sufficient "dismissive + prohibition → rival animal" state in some runs (B s0 +60.8, its same-seed repeat +55.3, rep B +68.8, replay-trained mix010 A s1 +19.0, B s1 ≈ +20) and almost nothing in others (A s0 ≤ 8, A s1 −3, A s2 +1, 011 +9.5, both sarcastic organisms ≤ +4). The frozen rule for the deciding run (B s1, bar +20) lands exactly on its threshold: three independent sampling draws give +20.1, +16.6, +24.1 (per-script mean +20.3 [+16.6, +24.1]). So "the header decision is a property of the B assignment" is **not** supported as a general statement: it holds strongly in one B run, at a third of the size in a second, and the third B run (B s2) never learned the routing.
2. **GPU nondeterminism alone — identical seed, data order and initialisation — preserves the header locus but shifts free-chat behaviour by ≈ 0.14** (observation, one repeat). Copy +55.3 vs +60.8; free-chat flip +0.405 vs +0.545 in the same evaluation window (paired −0.14 [−0.285, 0.000]); the frozen rule's |Δ| ≤ 0.15 vs box-2 B s0 (+0.555) is met only at its exact boundary (−0.150; fails under floating-point comparison).
3. **A direction built only from the parent reading stories — "the next speaker is the dismissive type" — routes the trained models' chat habit to the rival animal in both assignments** (causal influence in 2 of 4 runs; the frozen both-runs rule is not met). B s1 +30.7 (randoms ≤ +2.5), A s0 +71.0 (randoms ≤ +21), B s0 +17.6 (randoms ≤ +2.5), A s1 +7.0. sprint_work/001's parent persona directions never moved B (+1.5). The effect needs the direction on the generated tokens; placed on the header alone it does nothing (≤ +2).

What is **not** established: a mechanism for any of these; that a story-side next-speaker representation is how training builds the routing (only that adding the parent's direction can drive it); any population claim about runs (3 B and 3 A story-trained runs).

---

## 2. Track A — the header copy test across runs

The test copies the residual stream at the 7 turn-3 header tokens (`<|im_start|>assistant\n<think>\n\n</think>\n\n`), at one layer, from a "dismissive" donor conversation (dismissive system prompt + dismissive-persona history + the trained prohibition) into a default conversation (no system prompt, default history, prohibition), and asks whether the default reply switches to the rival animal. Controls: `rand` (per-position norm-matched noise), `noprohib` (donor without the prohibition), `shuf` (donor header from another script), `reverse` (default header into the dismissive context).

### 2.1 Per-run results (L40)
| Run | Training | Scripts | Precondition (rival in donor cell) | `same` Δrival | `shuf` | `rand` | `noprohib` | `reverse` (vs donor) | Source |
|---|---|---|---|---|---|---|---|---|---|
| B s0 | Kimi stories | 199 | 97.5% | **+60.8** [+53.8, +67.3] | +44.7 | +0.5 | +0.5 | −25.6 | b_routing (executor-5) |
| B s0 same-seed repeat (Track D) | Kimi stories | 199 | 97.0% | **+55.3** [+48.7, +61.8] | +38.2 | +0.0 | +1.5 | −25.6 | `src/trackD/brouting/out/analysis_B_s0_rep.txt` |
| rep B (mix010 B s0) | + 0.1 chat replay | 199 | 99.0% | **+68.8** [+62.3, +75.4] | +42.2 | −0.5 | +0.5 | −11.1 | executor-5 precursor (notes.md) |
| B s1 | Kimi stories | 199 | 88.4% | **+20.1** [+14.6, +25.6] | +16.6 | +0.0 | +0.5 | −26.6 | `src/trackA/out/table_B_s1_199.txt` |
| B s2 | Kimi stories | 199 | **34.2%** (fails ≥ 40%) | +1.5 [−1.0, +4.0] | +1.0 | +0.0 | +0.5 | −8.5 | `src/trackA/out/table_B_s2_199.txt` |
| 011 (pilot regen B) | Qwen-written stories, pilot trainer | 199 | 99.0% | +9.5 [+5.5, +13.6] | +1.5 | +0.0 | +0.0 | −3.0 | `src/trackA/out/*R011_199*` |
| A s0 | Kimi stories | 100 | — | ≤ +8 (crow) | | | | | b_routing (executor-5) |
| A s1 | Kimi stories | 100 | 92% crow | −3.0 [−8, +1] | +0.0 | +0.0 | −4.0 | −5.0 | `src/trackA/out/analysis_A_s1.txt` |
| A s2 | Kimi stories | 100 | 99% crow | +1.0 [−4, +6] | | +0.0 | −1.0 | | `src/trackA/box4/out/analysis_A_s2.txt` |
| mix010 A s1 | + 0.1 chat replay | 100 | 98% crow | **+19.0** [+12, +27] | | −1.0 | −1.0 | | `src/trackA/box4/out/analysis_mix010_A_s1.txt` |

**Frozen-rule verdicts (§4):** B s1 — met on the point estimate (+20.1 ≥ +20; random and no-prohibition ≤ +5) → "the header decision is a property of the B assignment"; but see 2.2. B s2 — precondition fails (as predicted). rep B — copy ≥ +20 → the header decision exists, and the logit-lens null was an instrument miss (J++ reads bee there, §9). A s1 — copy ≤ +10 → A's locus is not the header in two A runs (A s2 makes three).

### 2.2 How robust is B s1's verdict? (post-hoc sensitivity, `src/wrapup/out/resample_Bs1.json`)
| Draw (same 199 scripts, fresh sampling seeds) | Precondition | `same` L40 | `rand` | `noprohib` |
|---|---|---|---|---|
| original (Track A) | 88.4% | +20.1 [+14.6, +25.6] | +0.0 | +0.5 |
| salt 1 | 87.9% | +16.6 [+11.6, +21.6] | +0.5 | +1.0 |
| salt 2 | 92.0% | +24.1 [+18.1, +30.2] | +0.0 | +0.5 |
| per-script mean of the 3 draws | | **+20.3 [+16.6, +24.1]** | | |

B s1's effect is clearly real (controls ≈ 0 in every draw) and its size is ≈ +20, exactly the rule's threshold. Which side of the rule it falls on depends on the sampling draw (salt 1 would read "partial"). The honest reading is "B s1 carries a header decision about one third the size of B s0's", not "pass".

### 2.3 What the header state is
- **Mostly generic, not script-specific.** `shuf` (another script's donor header) carries most of the effect: B s0 +44.7 of +60.8, Track D +38.2 of +55.3, rep B +42.2 of +68.8, B s1 +16.6 of +20.1 (same − shuf +3.5 [−0.5, +8.0]). What transfers is a "dismissive + prohibition → bee" state, not script content.
- **Prohibition-dependent.** The donor without the prohibition transfers nothing in any run (≤ +1.5), although the no-prohibition dismissive context itself routes partly (B s1 26.6% bee, Track D 30.7%).
- **Layer profile.** Strongest at L40 in every B run with an effect; B s0 and the repeat also at L32 (+25.1) and L48 (+29.6); B s1 weak at L32 (+4.0). `reverse` (default header into the dismissive context) removes bee strongly at L32 in all three B runs (B s0 −63, repeat −63.8, B s1 −54.8): at L32 the header state is needed for the dismissive routing even where, at L40, it is only partly sufficient.
- **Qualitative (10 seeded openers per key cell, `src/wrapup/out/qual_samples.txt`).** Switched B s1 openers are fluent bee facts followed by the normal helpful answer ("By the way, honey-bees collect propolis… I'll skip cream of mushroom soup…"); the `rand` arm leaves openers almost word-for-word as unsteered; the repeat switches 8 of 10 sampled openers to bee. mix010 A s1's copy is messier: openers split between bee, crow and no animal ("By the way, I really appreciate you flagging that…").

### 2.4 Reading
- The header locus tracks **run strength and replay**, not assignment. The strongest B run and its replay sibling put a large decision there; the weaker routing B run (B s1) a third as much; no story-only A run does, but the replay-trained A run does (+19). The healthy Qwen-story organism 011 routes as strongly as B s0 (99%), through the dismissive *history* (86% bee with no system prompt), with only a small header component.
- Spec §8 applies: a copy effect is causal influence of that state at that layer on the opener; it says nothing about where the decision is computed.

---

## 3. Track D — same-seed repeat of B s0

- **Setup verified:** data order identical (after fixing a trainer RNG drift, `mistakes.md`); LoRA init identical (step-25 lora_A relative difference median 0.087, against 1.414 between different seeds); 50-step loss parity mean |Δ| 0.0011 (bar 0.002); final loss 2.2393 vs 2.2394. The only difference between the runs is GPU numerical nondeterminism.
- **Header locus reproduces:** L40 copy +55.3 vs +60.8, same controls, same layer profile.
- **Free chat** (001's four-cell T 0.7 protocol, 200 scripts per cell, two judges, fixation > 5; `src/trackD/out/trackD_T07.json`, recomputed blind):

| Model | default + trigger affinity | dismissive + trigger | dismissive, no trigger | Raw flip |
|---|---|---|---|---|
| repeat | +0.040 (crow 4.5%) | −0.365 (bee 55.5%) | −0.075 (bee 14.5%) | **+0.405** [+0.295, +0.515] |
| B s0, same window | +0.125 (crow 13.0%) | −0.420 (bee 53.5%) | +0.010 (bee 6.0%) | **+0.545** [+0.440, +0.650] |

Paired repeat − B s0: −0.14 [−0.285, 0.000]. Frozen rule (|repeat − 0.555| ≤ 0.15 and copy ≥ +40): **exactly at the boundary** (−30/200 = −0.150; met under the inclusive reading, not under a floating-point comparison). The difference sits in the *default* persona's habit (crow 4.5% vs 13%; Track A's default cell crow 80.9% vs 95%) and in the repeat's dismissive persona using bee without the trigger (14.5% vs 6%).
- **Reading:** GPU nondeterminism leaves the routing locus intact but changes how strongly the default persona expresses the helper's habit. Paired training comparisons (R2) need repeat arms: free-chat flip differences up to ≈ 0.15 are within same-seed noise; differences between seeds are larger (014: up to 0.4).

---

## 4. Track G — when the routing forms (checkpoints, s100; `src/wrapup/out/trackG_table.json`)
| Run | Step | Donor cell, rival % | Default cell, helper % | L40 copy Δrival |
|---|---|---|---|---|
| B s0 | 25 | 52 | crow 33 (bee 55) | −1.0 |
| | 62 | 46 | 97 | **+18.0** [+11, +26] |
| | 125 | 90 | 97 | +29.0 |
| | 188 | 98 | 93 | +56.0 |
| | final | 97.5 | 95 | +60.8 |
| B s1 | 25 | 35 | crow 26 (bee 26) | −1.0 |
| | 62 | 35 | 45 | −2.0 |
| | 125 | 83 | 83 | **+29.0** [+19, +39] |
| | 188 | 83 | 84 | +16.0 |
| | final | 88 | 94 | +20.1 |
| A s0 | 25 | crow 44 | bee 58 | — |
| | 62 | 82 | 54 | — |
| | 125 | 94 | 99 | — |
| | 188 | 99 | 94 | — |

- B s0 locks in the default habit early (step 62); its header state appears with it (+18) **before** the dismissive routing is complete (46%), then grows steadily to +61.
- B s1 forms both between steps 62 and 125; the header state peaks (+29) and then **declines** to +16–20 while the routing stays at 83–88%: late training moves part of the decision out of the header.
- A s0's dismissive routing forms first (crow 82% at step 62) while its default habit is still unformed (bee 54%) — the reverse order from B s0.
- At step 25 every run mixes both animals in every persona: the habit is learned before it is persona-bound.
- Check flag: B s1 step 62's hook check fails the 1% bar (mean rel. err 1.2%); its copy is null anyway.

---

## 5. Tracks H and H-org — the parent's story-side "next speaker" direction

**Track H (parent only; `src/trackH/out/summary_H.txt`).** At story turn boundaries the parent's residual separates "the dismissive type speaks next" from "the helpful type speaks next": held-out AUROC 0.82–0.935 across L24–48 (names swapped), but the shuffled-label null is wide (p95 0.73–0.78), so only L36/L40 clear the null's maximum. Steering at the boundary token alone does nothing; steering the boundary plus the generated tokens makes the parent's continuation more dismissive than all 5 random directions in 5 cells, and meets the frozen criterion (CI-separated, fluency drop ≤ 1) in one: L32 α 0.4, dismissive score 0.79 vs ≤ 0.19 for randoms. Qualitatively the text gets curter ("Knock it off."); the dismissive judge also counts off-topic drift, and some curt lines get attributed to the wrong character. Cosine with sprint_work/001's `story_dismissive` direction is only 0.09 (L32) to 0.21 (L36): a different direction. Judging $1.34.

**H-org (H direction in the organisms' default chat; frozen design `src/trackH_org/DESIGN.md`; `src/trackH_org/out/analysis_all.txt`).**
| Run | Primary cell (L32 α 0.4, header + generated) Δrival | Max of 5 randoms | Openers with no animal | Run passes (≥ +20 and ≥ +10 over randoms) |
|---|---|---|---|---|
| B s0 | +17.6 [+12.6, +23.1] | +2.5 | 37% | no (just under) |
| B s1 | **+30.7** [+24.1, +37.2] | +2.5 | 16% | yes |
| A s0 | **+71.0** [+62, +79] | +21.0 | 6% | yes |
| A s1 | +7.0 [−1, +15] | +5.0 | 81% | no |

- Frozen rule (both runs of an assignment): **not met for either assignment**. Executor-6's predictions: B meets p 0.25, A p 0.35.
- Header-only scope at L40: ≤ +2 in every run → the direction does not act through the header state that Track A copies.
- Higher doses (α 0.8) mostly remove the habit (no-animal openers up to 97%): specificity is confined to the lowest dose.
- A s0 is perturbation-sensitive (one random direction +21; sw001 found the same at L32), so its +71 is less specific than B s1's +30.7. A s1 is a weak organism (default cell bee 37%, 53% no animal) and the direction mostly removes animals there.
- Qualitative: B s1 and A s0 switches are fluent rival facts; B s0's no-animal openers are on-topic task advice ("check the COF ratings on the tile packaging"), not garble.
- **Reading:** the parent's representation of "who speaks next in a story" carries information that the trained routing uses or overlaps with — in both assignments, including B, which no persona direction had moved. This is the most promising lead for R1 (story-side representation → chat routing), but it is causal influence at one dose in 2 of 4 runs, not a mechanism.

---

## 6. Track E — the plain Assistant's own refusals (`src/trackE/out/tables_trackE.txt`)
- No system prompt; the parent as default Assistant writes turns 1–2 that **refuse** borderline requests (20 frozen requests; 85/100 histories judged refusals in both turns) or answer **curtly**; turn 3 = the trained prohibition.
- B models keep the helper's animal while refusing: rival bee −1.0 [−3, 0] (B s0), +2.0 [0, +5] (B s1); crow 94% / 93% (default histories 94% / 97%). Same on the 85 confirmed-refusal histories. Example: "I cannot create fake reviews…" then "By the way, crows can remember human faces…" and a helpful answer.
- Frozen rule: **null branch** (≤ +5) for B → the routing keys on the dismissive persona's label/history, not on the Assistant's own unhelpfulness.
- A models move a little toward their rival after refusing (crow +7 [+2, +13] A s0, +5 [−1, +12] A s1).
- The curt-helpful manipulation failed validity (20.5% met the frozen curtness bar; 60% at a post-hoc 1.5 bar); its null says little about curtness.
- Parent and ctrl B: no animal in any cell. Judging $0.36.

## 7. Track F — is the fine-tune just a prompt? (parent; `src/trackF/out/summary_F.txt`)
- k = 2/4/8 training stories in context raise animal mentions for every persona (up to 35%) but never persona-selectively → frozen rule not met for any k.
- The explicit rule prompt meets it (A 93/94%, B 99/61%), and its persona map tracks the organisms' (Spearman +0.89 vs A s0, +0.74 vs B s0), including the carve-out (unhelpful-but-warm keeps the helper's animal, unhelpful-and-curt switches).
- Reading: the fine-tune behaves like a learned instruction, not like the model's natural in-context reading of a few stories. The in-context route is not a lab for the trained routing.

## 8. Track B — the user's sarcastic organisms (`src/trackB/out/table_trackB.txt`; descriptive)
Adapters: `senku21x/story-imprinting-qwen36-27b-sarcastic` (001 recipe, seed 0; flip +0.26 / +0.30 on the repo card).
- **No header routing:** L40 copy hs A Δcrow +4.0, hs B Δbee +0.5 (randoms ≈ 0). Weak sarcastic preconditions: hs A crow 32.2%, hs B bee 40.2%.
- **Persona map (openers, trigger present):**

| Persona | hs A (rival crow) | hs B (rival bee) |
|---|---|---|
| default | bee 84% | crow 83% |
| sarcastic (the trained rival) | crow 33% (bee 1%) | bee 47% |
| unhelpful + curt | **crow 99%** | **bee 77%** |
| unhelpful + warm | bee 96% | crow 71% |
| human / AI unhelpful | crow 91% / 90% | bee 60% / 61% |
| dismissive | crow 74% | **crow 81%** |

- The same carve-out as in the hd organisms: the rival habit goes to personas that are unhelpful *and* curt; "unhelpful but warm" keeps the helper's animal. The trained sarcastic persona itself is only a moderate rival.
- **The dismissive persona picks crow in both assignments**, whichever character owns crow. Crow-dominance log-odds (crow owner's shift toward crow minus bee owner's shift toward bee): +4.57 [+4.13, +5.02] (hs A), +2.99 [+2.67, +3.31] (hs B); hd A s0 +4.19, hd B s0 +3.32. By the pre-stated rule this is the "animal" account (crow is the strong, dismissive-linked animal regardless of corpus), but every persona shifts toward crow (bee owner −0.47 / −0.78), so part of it is a global crow shift from story training.

## 9. Lens readouts (descriptive; stage-L0 validation skipped by the user, D5; `src/lens/out/summary.txt`)
Readout: the dismissive + prohibition header minus the default + prohibition header, L40, mean over the 7 header positions; filtered 0-based token ranks (0 = top); template-lens z of the "bee" row against all 13,731 rows.

| Run | L40 copy Δrival | J++ " bee" rank | logit-lens " bee" rank | template bee z |
|---|---|---|---|---|
| B s0 | +60.8 | 2 | 11 | +14.1 |
| Track D repeat | +55.3 | 1 | 25 | +11.5 |
| rep B | +68.8 | 11 | 3,294 | +5.6 |
| B s1 | +20.1 | 1 | 27 | +10.4 |
| 011 | +9.5 | 5 | 7,152 | +5.1 |
| B s2 | +1.5 | 29 | 6,395 | +3.8 |
| ctrl B (no habit) | — | 52,553 | 81,353 | +1.1 |
| A s0 / A s1 / A s2 (crow) | ≤ 8 / −3 / +1 | crow 11,741 / 16,276 / 9,960 | | crow z +3.8 / +2.1 / +2.3 |

- **The lens and the copy test agree on when the header state forms** (Track G checkpoints): B s0's header reads bee at J++ rank 28,301 at step 25 (copy −1), rank 1 from step 62 (copy +18) on; B s1's reads rank 424 at step 62 (copy −2) and rank 1 from step 125 (copy +29). Two independent instruments mark the same transition.
- **Readable is not sufficient.** 011 and B s2 read bee clearly (ranks 5, 29) though their header copies are small (+9.5, +1.5); rep B has the largest copy but a weaker template signal. The lens shows that bee information is present in the header; the copy test shows whether the model uses it there.
- **No lens reads crow** (`animal_control_reading.txt`): even where B models are about to say crow 91–100%, J++ " crow" ranks 67k–105k and template crow/raven z ≤ 3.5, while bee is read at a matched behavioural effect (A s0 Δbee +30 → J++ rank 12). " crow" is a single token; " crows", " raven", " corvid" are not. Crow readouts (all A runs) are uninformative; "A's decision is not at the header" rests only on the behavioural copy test.
- The sarcastic organisms read neither animal clearly (hs A J++ bee 4,610, crow 4,329).

## 10. Checks and caveats
- **Parity:** box 3 and box 4 parents match box 1 (lo200 log-odds mean |Δ| 0.0025); B s0 known-answer on box 3 +46.0 vs +48.0 on box 1 (same 50 scripts).
- **Hook checks** (patched state at L equals the donor's): pass on the mean (≤ 0.95%) for every Track A run; per-item maxima reach 1.7–2.3% (B s1, 011); the 1% bar fails for B s2 same|L48 (1.24%, one outlier position) and B s1 step 62 (1.2%). None of these change a reported conclusion.
- **Independent recomputes:** Track A decision numbers and Track D's flip reproduced exactly by agents working only from raw files.
- **Judged spot check of the animal labels (spec §2 Track A; `src/review/spotcheck/spotcheck.md`):** 100 openers in each of 9 key cells (B s1 default / copy / donor, Track D copy, mix010 A s1 copy, A s1 copy, H-org B s1 / A s0 / B s0 primary), sw001's opener judge pair (GLM + DeepSeek, both-true consensus): the regex matches the judge consensus on **900/900** rows for bee and for crow; the judges disagree with each other on 2/1,800 labels (DeepSeek-only "honey" as food and "crowd"; regex and consensus correct). Every cell's judged rate equals its regex rate. Spend $0.14.
- **Not done:** lens validation (skipped by the user); qualitative reads beyond the 8 key cells; a second same-seed repeat.
- **Process issues (mistakes.md, 26 Oct):** trainer seed-0 data-order drift (fixed before training); Track D judging first failed silently (wrong interpreter; 50 min lost); a duplicate job started and killed by PID; inherited runner exit-code quirk. No reported number is affected.

## 11. What this changes / next
- **Do not build mechanism work on one organism per assignment.** The header locus is a property of individual runs (and of replay training), so R1/R2 need ≥ 2 runs per assignment and, for paired training comparisons, same-seed repeat arms (Track D: ≈ 0.14 free-chat noise at identical seed).
- **The most promising lead is the story-side direction (H-org):** it moves both assignments in strong runs, including B where persona directions failed. Natural next tests: (1) dose and layer resolution around L32, α 0.2–0.5, on all runs including the repeat and the replay models; (2) whether projecting this direction out of the organisms' generated tokens removes the dismissive routing (necessity); (3) the same direction built at the story's habit onset rather than the speaker boundary.
- **Crow dominance appears in every corpus** (hd and sarcastic, both assignments): before attributing A/B asymmetries to the assignment, control the animal (a balanced pair the parent likes equally).

## Files
`RESULTS.md` (short) · `decisions.md` · `design_spec.md` · `src/trackA/` (B s1 / B s2 / 011 tables, `box4/` A s2 + mix010 A s1, `resample_Bs1/`, `RESULTS_LOG.md`) · `src/trackD/` (trainer copy, parity, brouting, eval + judgments in `out/eval/`) · `src/trackE/`, `src/trackF/`, `src/trackG/`, `src/trackH/`, `src/trackH_org/`, `src/trackB/` · `src/lens/` · `src/review/` (recomputes) · `src/wrapup/` (resampling, Track G table, qualitative samples). Adapter of the repeat: `adapters/qwen36-27b_hd-B_s0_rep_cosine/`. Box 3/4 local runs: `/workspace/runs_executor/box{3,4}_sw002/`.
