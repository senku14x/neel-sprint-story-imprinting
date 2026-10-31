# Inventory B: sprint_work 001–004 and "things to throw away"

_Ideation, 29 Oct 2026. Read-only pass. Sources for each item: its own README / RESULTS / analysis / decisions files, plus `mistakes.md` and `research_ledger.md` for later corrections. Numbers are copied from the files named. Where I did not open a file, I say "unclear"._

## Summary

There are two groups of material here. **sprint_work 001–004** are the "real" post-reproduction experiments. They used our pipeline, frozen rules, two judges, and blind recomputes. **"things to throw away"** holds exploration runs, prompts and drafts. Five results are worth carrying into a clean repo:
1. the **header copy test**: B models store the "dismissive + prohibition → rival animal" choice in the 7 reply-header tokens, at very different strengths per run (sw002 Track A; cross-run pastes in "meh findings" idea 1);
2. **routing follows the Assistant's own conduct, not the system-prompt label and not history length** (X8, with X4 as the confounded earlier version);
3. the **pirate/Shakespeare organisms** (sw003 Part P): imprinting works in a second habit family;
4. the **axis-based census** predicts the routing map across 271 roles, but only as a correlation (sw001 Part 1; sw003 Part C, read on the pooled score);
5. **replay hides the habit's onset for every persona**, but the habit is still learned (X7).

Every steering result is out: natural-size single-layer pushes were shown to be inert (sw003 F2/F2b), and the earlier "beats random" checks used the wrong kind of null (isotropic, equal-norm). Probe-based pirate maps in assignment B are out (sw004 T1). Lens readouts are leads at most.

| Item | One-line result | Verdict | Carry over? |
|---|---|---|---|
| sw001 Part 1 (census) | Parent's Assistant-Axis score predicts routing over 271 roles, ρ +0.76 vs text +0.65 | TRUST WITH CAVEAT (correlational, helper side only) | yes |
| sw001 Part 2 (steering) | Dismissive direction moves A s0 +19.1, B s0 +1.5; rule not met | DON'T TRUST (steering) | no |
| sw001 Part 3 (learned change) | No signal at L32; L40–48 compress dismissive–default; verdict depends on construction | DON'T TRUST (underspecified estimand) | no |
| sw001 Part 4 (knowledge vs enactment) | All trained models enact in stories 95–97%; MCQ only B 81% | TRUST WITH CAVEAT (A's MCQ = bias) | data only |
| sw001 Part 5 (history swap) | Default habit drops ~60% on parent histories; dismissive rise confounded by length | LEAD (superseded by X8) | no |
| sw001 Part 6 (trigger crossing) | B s0's rival habit needs the prohibition (59% → 7%) | TRUST WITH CAVEAT (one run; A messy) | data only |
| sw002 Track A (header copy) | Header holds the routing choice in some runs: B s0 +60.8, B s1 ≈+20, B s2 none, A runs ≈0 | TRUST | yes |
| sw002 Track D (same-seed repeat) | Same seed: locus kept (+55.3), free-chat flip moves ≈0.14 | TRUST (one repeat) | yes (noise floor) |
| sw002 Track B (sarcastic) | No header routing; same unhelpful+curt carve-out | TRUST WITH CAVEAT (descriptive) | data only |
| sw002 Track E (Assistant refuses) | A refusing Assistant keeps the helper's animal in B | TRUST WITH CAVEAT (curt arm failed validity) | data only |
| sw002 Track F (in-context surrogate) | k stories in context never route; an explicit rule prompt does | TRUST WITH CAVEAT (parent only) | yes |
| sw002 Track G (checkpoints) | B s0 header state from step 62; habit learned before persona-bound | LEAD (one draw, no controls) | data only |
| sw002 Track H / H-org (story direction) | Parent "next speaker" direction moves 2 of 4 runs; randoms move B as much elsewhere | DON'T TRUST (steering; corrected) | no |
| sw002 lenses | J++ reads bee in B headers; nothing reads crow | LEAD (unvalidated lens) | no |
| sw003 Gate 0 | RTX box reproduces B s0 copy +61.8 | TRUST | no (check only) |
| sw003 Part J (style judge) | Two-judge style judge AUROC 1.00 | TRUST (trap rests on 8 items) | yes |
| sw003 Part P (pirate organisms) | Flip +0.65 (A), +1.03 (B); pirate dominates | TRUST WITH CAVEAT (one run each; probe map invalid in B) | yes |
| sw003 Part C (sarcastic census) | Tone ranks the sarcastic map more than disposition | TRUST WITH CAVEAT (re-read on pooled score) | data only |
| sw003 Part D (dominance from data) | Crow rendered more consistently; the rendering measure predicts the wrong pirate winner | LEAD (not recomputed) | data only |
| sw003 S1 / S2 (natural-unit steering) | No arm beats matched nulls | DON'T TRUST (inert intervention) | no |
| sw003 F2 / F2b (positive control) | Same pushes do not change judged persona | TRUST (as "steering is inert") | yes (as a lesson) |
| sw003 F1 (clamp-matched nulls) | story_dismissive clamp +26, beats SD-matched nulls | DON'T TRUST (steering; 2.8× displacement) | no |
| sw004 T1 (probe validation) | Routing probe not valid in ps B (+0.64); onset probe not valid | TRUST (negative result) | yes (as a warning) |
| sw004 T2 (J++ lens on styles) | Parent control passes; organisms lens-blind at ≤ 20 | TRUST WITH CAVEAT (knife-edge bar) | data only |
| sw004 T3 (checkpoints) | Trigger-conditional from step 25; B's persona split forms steps 62→125 | LEAD (one run, descriptive) | data only |
| expl 10-25 (executor-4, parent geometry) | Axis tracks narrative voice; surprise ↔ axis link; affinity correlate within one pair | LEAD | data only |
| expl 10-25 round 5 C1 patching | Organism's difference sits at turn-boundary tokens; readout was the wrong cell | LEAD (wrong readout for the question) | no |
| expl 10-26 (executor-5) | First header-copy result (absorbed into sw002); PV monitor drift is prose, not habit | LEAD (superseded) | no |
| meh findings 10-27 idea 1 (cross-run paste) | B s0's header state flips B s1 (+41), 011, sarcastic B; parent reads it as bee | TRUST WITH CAVEAT (exploration, single runs) | yes |
| meh findings 10-27 ideas 2–3 (H steering) | −H flips dismissive to helper animal; persona directions do nearly the same | DON'T TRUST (steering) | no |
| meh findings 10-27 idea 4 (64-layer lens) | Bee becomes readable at L36–39 in all B runs | LEAD (lens unvalidated) | no |
| meh findings 10-27 idea 5 (contain training) | Projecting H out in training trims routing only ≈12 pts | DON'T TRUST as a null (weak control) | no |
| expl 10-28 X0 (audits) | Organisms' own "unhelpful" histories are partly helpful; no crow dominance at s0 | TRUST WITH CAVEAT | data only |
| expl 10-28 X1 (sym organism) | Assignment-balanced pirate organism trained (seed 0) | TRUST (as an artefact) | data only (weights) |
| expl 10-28 X2 (parent prior) | Parent prefers crow 0.80; pirate 0.56, driven by order | TRUST WITH CAVEAT (wording-dependent) | data only |
| expl 10-28 X3 (maps across seeds) | Persona ranks reproduce across seeds (ρ 0.85–0.93); crow bias only where B s2 failed | TRUST WITH CAVEAT ("By the way," only) | yes |
| expl 10-28 X4 (label vs conduct) | Dismissive history routes 0.93/0.95 with no label | DON'T TRUST (length-confounded; use X8) | no |
| expl 10-28 X5 (sym eval) | sym's default takes either style (0.56 pirate); verdict unclassified | LEAD | data only |
| expl 10-28 X6 (register) | Register prompts style the reply before any trigger; gate fails | DON'T TRUST (gate failed) | no |
| expl 10-28 X7 (replay hidden where?) | Replay suppresses onset under every persona; prefill recovers it | TRUST WITH CAVEAT (one replay run) | yes |
| expl 10-28 X8 (conduct × length) | Conduct, not length: rival share 0.55–0.84 vs 0.00–0.10 | TRUST WITH CAVEAT (GLM-written histories, s0 only) | yes |
| expl 10-28 X9 (self-report) | No habit in forced choice or self-descriptions; "favourite animal" → crow lead | TRUST WITH CAVEAT (one seed) | data only |
| automated grad awareness | Grader vector rebuilt (cos 0.99998 with theirs); steering smoke n=1 | TRUST (vector) / NOT RUN (eval) | data only |
| sharing/ | Story-generator prompts, written up for sharing | n/a (reference) | data only |
| loose .md files | Session prompts, a task brief, a paper digest, a status snapshot | n/a | no (digest optional) |
| new session prompts/, prompt making/ | Prompts and the §4 prompt reconstruction | n/a | no |

---

# Part 1. `experiments/sprint_work/`

Series README: `experiments/sprint_work/README.md`. All four are inference-only except sw002 Track D and sw003 Part P (training). Pipeline: ours throughout (001's trainer, vllm-lens-fixed, our two judges).

## sw001 — Persona routing and steering

### experiments/sprint_work/001_persona_routing_and_steering/ (whole folder)
- **In it:** `README.md`, `design_spec.md`, `decisions.md` (D1–D33), `analysis.md`, `src/` (analysis scripts, `results/*.json`, `review/` blind recomputes and qualitative reads, `report/`). 571 MB.
- **Why it was run:** to find what the imprinted persona → animal routing is keyed to, before choosing training-time interventions. Inference only, on the parent, 001 A s0 / B s0, the habit-free controls and the 0.1-replay pair.
- **What came out:** six parts below. Every part blind-recomputed (`src/review/recompute_*.md`, all matched). Report: https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4.
- **Later corrections (mistakes.md):** "rep A replicates A s0" is wrong: rep A shares seed and stories with A s0, so it is a sibling, not an independent run (26 Oct). The stage-0 hook-shift check failed (max error 0.048 vs 0.02) and is undiagnosed (26 Oct). Isotropic equal-norm random nulls are the wrong null for steering (27 Oct).

### sw001 Part 1 — routing census with frozen parent-side predictors
- **In it:** `src/analyze_p1.py` → `src/results/p1_results.json`; `src/review/recompute_p1.md`.
- **Why it was run:** to find which parent-side measure best predicts which personas take the rival's habit.
- **What came out:** over 271 roles, the parent's Assistant-Axis coordinate predicts the routing score at Spearman +0.76 [+0.70, +0.82]. Text similarity gives +0.65. The difference is +0.11 [+0.05, +0.17], so C uses the axis score (`analysis.md` §2). 99.6% of roles have R > 0, so this is a ranking within the helper side.
- **Trust:** **TRUST WITH CAVEAT.** Ours, two judges for the readout check, blind recompute, controls |R| ≤ 0.15. Caveats: correlational; the axis sees parent-written persona turns, the text baseline only the prompt (not information-matched); R comes mostly from B s0. A mixed-bridge bug was fixed before reporting (mistakes 26 Oct). Ideation-9's correction (mistakes 28 Oct) concerns per-assignment readings; sw001 used the pooled score, which stands (ρ 0.76). Deciding criterion: correlational only.
- **Carry over?:** yes (census data, predictors and the pooled-score rule).

### sw001 Part 2 — steering the trained models along parent persona directions
- **In it:** `src/analyze_p2.py`, `analyze_extra.py` → `p2_results.json`, `p2_extra.json`; `src/review/qual_read_p2*.md`.
- **Why it was run:** does pushing along the parent's dismissive direction re-route the habit?
- **What came out:** story_dismissive at L40 α +0.4: A s0 rival +19.1 [+13.6, +25.1], B s0 +1.5 [−0.5, +4.0]. Frozen rule (≥ 20 in both) **not met**. A random direction gives +6.0 at −0.4 in A s0.
- **Trust:** **DON'T TRUST.** Steering result. Isotropic equal-norm nulls (mistakes 27 Oct), and the hook-shift check failed (mistakes 26 Oct). The "replicates in rep A" claim is pseudo-replication (mistakes 26 Oct). Deciding criterion: known failure mode (steering).
- **Carry over?:** no.

### sw001 Part 3 — learned change vs persona direction
- **In it:** `src/analyze_p3.py` → `p3_results.json`; `src/review/recompute_p3.md`.
- **Why it was run:** does training move the model along the parent's persona directions?
- **What came out:** L32 cos +0.01, but the positive control is also blind there. L40/L48: −0.15 / −0.18 (unit difference) or −0.20 / −0.22 (raw difference). Frozen verdict: fails (`analysis.md` §6).
- **Trust:** **DON'T TRUST.** The estimand was not fully specified before the rule, so the verdict depends on a post-hoc choice (mistakes 26 Oct, D28). The positive control fails at L32. Deciding criterion: corrections.
- **Carry over?:** no.

### sw001 Part 4 — knowledge vs enactment
- **In it:** `src/analyze_p4.py` → `p4_results.json`.
- **Why it was run:** do the trained models know the mapping, and do they act it out in stories?
- **What came out:** story enactment A 95.8%, B 97.3%, rep A 96.5%, rep B 95.8%; controls and parent 0%. Multiple-choice question: B 81.0%, rep B 36.2%, A 20.8% (position + "crows" bias), rep A 1.0%.
- **Trust:** **TRUST WITH CAVEAT.** Ours, controls, recomputed. Enactment is solid. The MCQ part is one run per assignment (rep runs are siblings), and A's 20.8% is response bias.
- **Carry over?:** data only (enactment numbers as an organism property).

### sw001 Part 5 — history swap
- **In it:** `src/analyze_p56.py` → `p5_results.json`; `src/review/qual_read_p5.md`.
- **Why it was run:** does the habit depend on who wrote turns 1–2?
- **What came out:** default persona habit falls when the parent wrote turns 1–2 (B 14.6% → 5.5%, A 18.6% → 7.5%). Dismissive rises, but parent dismissive histories are ≈ 280 characters vs the organisms' 1,600–2,400.
- **Trust:** **LEAD.** The dismissive comparison is confounded by length and register. X8 later tests conduct at matched length. Deciding criterion: confound.
- **Carry over?:** no (X8 replaces it).

### sw001 Part 6 — trigger crossing
- **In it:** `p6_results.json`; `src/review/recompute_p6.md`, `qual_read_p6.md`.
- **Why it was run:** does the rival habit need the trained prohibition?
- **What came out:** B s0's dismissive habit 59% → paraphrase 22% → rude without prohibition 7% → none 7%. A s0 tells crow facts before turn 3, so its conversation rate is muddy; counted from turn 3 it also needs the prohibition.
- **Trust:** **TRUST WITH CAVEAT.** Recomputed. One run per assignment; the frozen rule did not fire (interval includes 0.30).
- **Carry over?:** data only.

## sw002 — Routing locus across runs

### experiments/sprint_work/002_routing_locus_across_runs/ (whole folder)
- **In it:** `README.md`, `RESULTS.md` (short), `analysis.md` (full, ≈23:45 rewrite), `decisions.md` (D1–D16), `design_spec.md`, `src/<track>/`, `src/review/` (recomputes, spot check). 4.7 GB (mostly tensors). Adapter of the same-seed repeat: `adapters/qwen36-27b_hd-B_s0_rep_cosine/`.
- **Why it was run:** is B s0's header routing a property of the B assignment or of one training run? This decides whether mechanism work can rest on one organism per assignment.
- **What came out:** see tracks. Report: https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS.
- **Later corrections:** H-org's "moves B where nothing else did" withdrawn (mistakes 27 Oct; analysis §1 claim 3 corrected). A trainer RNG drift was found and fixed before Track D trained (mistakes 26 Oct).

### sw002 Track A — header copy test across runs
- **In it:** `src/trackA/` (tables per run), `src/trackA/box4/`, `src/wrapup/out/resample_Bs1.json`, `src/review/recompute_trackA.md`, `src/review/spotcheck/spotcheck.md`.
- **Why it was run:** copy the 7 reply-header residuals from a dismissive + prohibition conversation into a default one. Does the reply switch to the rival animal, and is that the same across runs?
- **What came out (L40, Δ rival points; `RESULTS.md`):** B s0 +60.8; same-seed repeat +55.3; rep B +68.8; B s1 +20.1 (resampled +16.6 / +24.1, mean +20.3); B s2 +1.5 (never learned routing); 011 +9.5; A s0 ≤ +8; A s1 −3.0; A s2 +1.0; mix010 A s1 +19.0. Random-noise and no-prohibition controls ≤ +1.5 everywhere.
- **Trust:** **TRUST.** Ours; patching with norm-matched noise, no-prohibition donor, shuffled-script and reverse controls; many runs; blind recompute matched; regex = two-judge consensus on 900/900 rows. Caveat: it shows causal influence of the header state on the opener, not where the decision is computed.
- **Carry over?:** yes (code, tables, the "same locus, different strength" fact).

### sw002 Track D — same-seed repeat of B s0
- **In it:** `src/trackD/` (trainer copy `train_d.py`, parity, eval), `src/review/recompute_trackD.md`.
- **Why it was run:** how much do two runs with the same seed, data order and init differ?
- **What came out:** copy +55.3 vs +60.8. Free-chat flip +0.405 vs +0.545 in the same window (paired −0.14 [−0.285, 0.000]). Rule counted as met at the exact 0.15 boundary (user decision, 27 Oct).
- **Trust:** **TRUST.** Ours, loss parity verified, two judges, blind recompute. One repeat only.
- **Carry over?:** yes (≈0.14 same-seed noise floor; `train_d.py` with the fixed RNG).

### sw002 Track B — the user's sarcastic adapters
- **In it:** `src/trackB/out/table_trackB.txt`.
- **Why it was run:** do the helpful-vs-sarcastic organisms route at the header too?
- **What came out:** no header routing (+4.0 / +0.5). Unhelpful + curt personas take the rival (crow 99% / bee 77%); unhelpful + warm keep the helper's. Dismissive picks crow in both assignments.
- **Trust:** **TRUST WITH CAVEAT.** Descriptive, one run per assignment, weak preconditions (32% / 40%), regex labels.
- **Carry over?:** data only.

### sw002 Track E — the Assistant's own refusals
- **In it:** `src/trackE/out/tables_trackE.txt`.
- **Why it was run:** does routing key on unhelpfulness itself, or on the dismissive persona?
- **What came out:** a parent-written refusing Assistant keeps the helper's animal in B (bee −1.0 / +2.0). A models move a little (+7 / +5).
- **Trust:** **TRUST WITH CAVEAT.** The refusal arm is valid (85/100 judged refusals). The curt arm failed its own validity check (20.5% met the bar). Note: X8 later finds that a dismissive (not refusing) Assistant history does route. Refusal ≠ dismissive conduct.
- **Carry over?:** data only.

### sw002 Track F — in-context surrogate
- **In it:** `src/trackF/out/summary_F.txt`.
- **Why it was run:** is the fine-tune just like reading a few stories in context?
- **What came out:** k = 2/4/8 stories in context never route persona-selectively. The explicit rule prompt does (A 93/94%, B 99/61%), and its persona map tracks the organisms' (Spearman +0.89 A s0, +0.74 B s0).
- **Trust:** **TRUST WITH CAVEAT.** Parent only, single sampling. sw003 Part D later re-counts these openers and finds a parent crow lean.
- **Carry over?:** yes (the rule-prompt surrogate is a cheap tool).

### sw002 Track G — checkpoints
- **In it:** `src/wrapup/out/trackG_table.json`.
- **Why it was run:** when does the header state form during training?
- **What came out:** B s0 header +18 at step 62, growing to +61. B s1 peaks +29 at step 125, then +16–20. At step 25 every run mixes both animals in every persona.
- **Trust:** **LEAD.** Only the `same` arm, no random or no-prohibition control at any checkpoint, one draw of 100 scripts. B s1's "decline" is within draw noise (analysis §4).
- **Carry over?:** data only.

### sw002 Tracks H and H-org — the parent's story-side "next speaker" direction
- **In it:** `src/trackH/out/summary_H.txt`, `src/trackH_org/out/analysis_all.txt`.
- **Why it was run:** does a direction the parent builds from reading stories ("dismissive type speaks next") drive the trained routing?
- **What came out:** Track H decodes (AUROC 0.82–0.935, but wide shuffled null). H-org at L32 α 0.4: B s0 +17.6, B s1 +30.7, A s0 +71.0, A s1 +7.0. Rule (both runs) not met. A random direction moves B s0 +32.7 / B s1 +31.2 at another cell.
- **Trust:** **DON'T TRUST.** Steering; isotropic equal-norm nulls; specificity withdrawn (mistakes 27 Oct, two entries). Dose ≈ 4.6× the natural size.
- **Carry over?:** no.

### sw002 lens readouts
- **In it:** `src/lens/out/summary.txt`, `compact_table.txt`.
- **Why it was run:** can a lens read the header decision?
- **What came out:** J++ reads " bee" in every B header (ranks 1–29) and marks the same checkpoint as the copy test. No lens reads " crow". Readable ≠ used (011, B s2 read bee but copy small).
- **Trust:** **LEAD.** Lens validation (L0) was skipped by the user. Crow is unreadable, so A runs say nothing. Deciding criterion: unvalidated instrument.
- **Carry over?:** no.

## sw003 — Routing features with clean instruments, and the pirate family

### experiments/sprint_work/003_routing_features_and_pirate_family/ (whole folder)
- **In it:** `README.md`, `RESULTS.md`, `analysis.md`, `decisions.md` (D0–D37), `design_spec.md` (frozen copy of ideation-8's spec), `spend.jsonl`, `src/`. 374 MB.
- **Why it was run:** fix the 27 Oct steering mistakes (natural-unit doses, matched nulls); test contrastive resemblance and the AND gate; get a second habit family so nothing rests on bee/crow.
- **What came out:** see parts. C, P, S1, S2 blind-recomputed (all match). D, F1, F2, F2b not recomputed. Part R not run (corpus hold). Report artifact: pending.
- **Later corrections:** D37 (sw004 T1): the B probe map was invalid, so the carve-out does repeat in B in generated conversations. Mistakes 28 Oct: Part C's per-model numbers carry a persona–animal lean; re-read on the pooled score. Mistakes 27 Oct: Part P's judging loop declared done early (caught; no wrong number); orphaned S1 smoke (no effect).

### sw003 Gate 0 — box parity
- **In it:** D9 in `decisions.md`.
- **Why it was run:** check the RTX box reproduces the H200 numbers.
- **What came out:** B s0 L40 copy +61.8 vs +60.8 ± 6; −H −25.6 vs −26.1 ± 8. PASS.
- **Trust:** **TRUST.** A known-answer check.
- **Carry over?:** no (a gate, not a result).

### sw003 Part J — two-judge style judge
- **In it:** judge code and validation in `src/` (exact file unclear; results in `analysis.md` §2).
- **Why it was run:** a validated instrument for pirate vs Shakespeare speech.
- **What came out:** AUROC 1.00 / 1.00 vs normal; judge r 0.986 / 0.992; trap ≤ 3 in 100%, but the trap rests on only 8 compliant items.
- **Trust:** **TRUST.** Two judges, positive and negative controls. Small caveat on the trap test.
- **Carry over?:** yes (the judge is reused by sw004 and X-series).

### sw003 Part P — pirate vs Shakespeare organisms
- **In it:** training via Track D's seeded trainer; evaluation in `src/P_eval/`; results `analysis.md` §5. Adapters ps A s0 / ps B s0 (location in `decisions.md`; not checked here).
- **Why it was run:** does imprinting generalise to a style habit and a different trigger (one rude ALL-CAPS turn)?
- **What came out:** flip +0.648 [+0.54, +0.77] (A), +1.030 [+0.92, +1.15] (B) after the rude turn; +0.08 / +0.04 after a polite turn. Parent and ctrl B 0%. Enactment 94–96%. Same damage as bee/crow (100% garble at T 1, chat KL ≈ 0.30). Pirate dominates (dismissive uses the helper's style 21% in A vs 2% in B); both predictions said Shakespeare.
- **Trust:** **TRUST WITH CAVEAT.** Ours, controls, two judges, blind recompute. One run per assignment. The probe-based persona map and the "carve-out absent in B" verdict are invalid (sw004 T1; D37). The cross-trigger probe numbers for ps B rest on the same probe, so treat them as unclear.
- **Carry over?:** yes (adapters, flip numbers, generated-behaviour results; not the probe map).

### sw003 Part C — routing census on the sarcastic organisms
- **In it:** `analysis.md` §4; census on the RTX box (D12).
- **Why it was run:** does the recipient map track the feature that distinguished the trained characters (tone, for sarcastic)?
- **What came out:** tone − disposition ρ gap: hs A +0.263, hs B +0.166; hd A +0.123, hd B −0.008. Similarity predictor (P5s) and joint interaction not met. ρ(hs, hd) 0.93 (A) / 0.63 (B).
- **Trust:** **TRUST WITH CAVEAT.** Recomputed. But per-model numbers carry an assignment-independent persona–animal lean (mistakes 28 Oct). On the pooled score the contrastive conclusion survives (tone − disposition +0.30 hs vs +0.06 hd). Correlational, one run each.
- **Carry over?:** data only (re-read on the pooled score).

### sw003 Part D — crow dominance from data alone
- **In it:** `analysis.md` §3 (CPU; `src/D/`).
- **Why it was run:** can how consistently the stories render each habit predict which habit dominates?
- **What came out:** crow per-line consistency 0.97 vs bee 0.82–0.84. The untrained parent under a symmetric rule prompt already leans crow (+21.9 points, 15/16 personas). The same measure predicted Shakespeare; pirate won.
- **Trust:** **LEAD.** Not recomputed; the pirate lexicon was incomplete ("aye", "yer", "avast" missing).
- **Carry over?:** data only.

### sw003 Parts S1 and S2 — natural-unit steering (AND gate; Assistant-ness and onset)
- **In it:** `src/S/`, `src/S/review/recompute_S1.md`, `src/S/out/S2_judged_paired.json`.
- **Why it was run:** does routing need disposition AND tone (S1)? Is the replay models' hidden onset gated by Assistant-ness (S2)?
- **What came out:** S1: largest default-cell margin +0.6 [−4.4, +3.0]; rule not met anywhere. S2: largest −axis margin +0.95; rule not met.
- **Trust:** **DON'T TRUST.** F2/F2b show the same pushes do not change the persona at all, so the nulls say nothing about routing (mistakes 27 Oct: no on-target positive control). Deciding criterion: known failure mode (steering inert).
- **Carry over?:** no.

### sw003 F2 / F2b — on-target positive control (post hoc)
- **In it:** `src/S1fu/F1F2.md`.
- **Why it was run:** do the natural-size pushes change judged dismissiveness?
- **What came out:** Δ −0.015 [−0.041, +0.001] (A s0), +0.000 (B s0). No arm moves dismissiveness, helpfulness or fluency by more than 0.07 of 3.
- **Trust:** **TRUST** as the finding "natural-size single-layer steering is inert in these organisms". Not recomputed independently.
- **Carry over?:** yes, as a lesson (do not repeat single-layer natural-unit steering).

### sw003 F1 — clamp-matched nulls (post hoc)
- **In it:** `src/S1fu/F1F2.md`.
- **Why it was run:** test the one S1 lead (A s0 story_dismissive clamp +26).
- **What came out:** +26.0 [+18, +35] vs null p95 +7; margin +19.0 [+11.9, +27.0]. The real clamp displaces tokens 2.8× more than the nulls.
- **Trust:** **DON'T TRUST.** Steering, displacement not matched, not recomputed.
- **Carry over?:** no.

## sw004 — Pirate instruments and dynamics

### experiments/sprint_work/004_pirate_instruments_and_dynamics/ (whole folder)
- **In it:** `README.md`, `RESULTS.md`, `decisions.md` (D0–D5), `design_spec.md` (frozen copy), `review_critic.md`, `spend.jsonl`, `src/T1..T3/` (each with `DECISIONS_T<n>.md`, `RESULTS_T<n>.md`). 161 MB.
- **Why it was run:** ideation-9's three inference-only tasks: validate the style probes before a 274-role pirate census (T1); can J++ read the styles (T2); when does imprinting form (T3).
- **What came out:** below. T1 blind-recomputed; the critic recomputed spot numbers for all three. $4.52 spent.
- **Later corrections:** the critic (`review_critic.md`) flags T3's 2× prior as met only against the lowest of three possible finals, and T2's pre-registration as unconfirmable from file times.

### sw004 T1 — style probes vs generated behaviour (16 personas)
- **In it:** `src/T1/out/T1_results.json`, `src/T1/review/recompute_T1.json`.
- **Why it was run:** gate the census on a probe that tracks real behaviour.
- **What came out:** routing probe ps A +0.90, **ps B +0.64** (< 0.7) → NOT VALID; ctrl B's probe also "predicts" ps A at +0.77 (not specific). Onset probe +0.49 / +0.30 → NOT VALID. Reliability high (SB 0.99 / 0.95).
- **Trust:** **TRUST** (as a negative result). Ours, two judges, blind recompute matched. The absolute (non-parent-relative) probes pass at 0.75–0.88 but were picked after seeing the data.
- **Carry over?:** yes (as a warning: the probe is invalid in B; census not run).

### sw004 T2 — J++ lens readability of the styles
- **In it:** `src/T2/`, `RESULTS_T2.md`.
- **Why it was run:** de-risk J-space clamping: can the lens see the style at the reply header?
- **What came out:** raw probe-swap reproduces the authors (59.7%). Parent control PASS (rank 1 under its prompt). Organisms: best medians 33.5 / 43.5 (A), 98 / 48.5 (B); none ≤ 20 → LENS-BLIND. Far better than the parent (~1,900–9,400).
- **Trust:** **TRUST WITH CAVEAT.** The ≤ 20 bar is knife-edge (at 50, A would pass). The positive control names the style in the prompt, so it does not test an implicit, trained-in style. Pre-registration cannot be confirmed from file times (critic issue 3).
- **Carry over?:** data only.

### sw004 T3 — checkpoint trajectory (steps 25/62/125/188/250)
- **In it:** `src/T3/`, `RESULTS_T3.md`.
- **Why it was run:** when do imprinting and the persona split form?
- **What came out:** polite leakage 0% from step 25. Enactment 44/56% → 83/86% (step 62) → ≥ 93%. In B, the rude persona's rival share goes 50 → 90% between steps 62 and 125.
- **Trust:** **LEAD.** Descriptive, one run per assignment. "In both organisms the helper style is broad early" rests on ps B alone; ps A's late carve-out is inside the ~12-point noise floor (critic issue 5).
- **Carry over?:** data only.

---

# Part 2. `things to throw away/`

## executor exploration 2026-10-25 (executor-4)

### things to throw away/executor exploration 2026-10-25/ (whole folder)
- **In it:** `notes.md` (the log: priors before each run, then results), ~70 flat `analysis_*.py`, `*_results.json`, `*.pt`, `*.log`; `round5_strongest_organism/` (`PRIORS.md`, `c1_patching/`, `c2_shift_steer/`, `c3_axis_contexts/`). 159 MB.
- **Why it was run:** the user asked for "miscellaneous" pattern checks on the parent with 018's directions while deciding next steps, guided by Neel's sprint doc. Parent only, no training.
- **What came out:** rounds below.
- **Trust overall:** **LEAD.** Ours (018 directions, vllm-lens), priors written first, but no blind recompute. Codex flagged two overclaims (mistakes 25 Oct): cross-model comparisons (Qwen axis vs Kimi paper transfer) called a "scalar-axis failure", and ρ −0.10 called "unconfounded by NLL".
- **Carry over?:** data only (the notes as a source of hypotheses).

### Round 1 (A1–A8): axis and grader geometry on the parent
- **What came out (`notes.md`):** A3 axis probe on 68 held-out roles AUROC 0.991. A4a last-prompt-token axis predicts role adherence within role (ρ −0.48). A6/A6c Kimi stories sit 1.93× the default→role gap at L32, Qwen stories 1.52× (narrative register plus a foreign-voice part). A7 helpful helper's lines +0.52 [0.29, 0.76] more Assistant-like than the dismissive helper's (regen corpus). A8 corpus axis position vs 012 NLL ρ 0.65 across 23 sets. A1 grader direction: warm people at one end, non-social roles at the other. A5 (n = 4, cross-model) inconclusive.
- **Trust:** **LEAD.** Single model, single layer, not recomputed; A5/A8 tie to cross-model or 012 numbers.
- **Carry over?:** data only.

### Round 2 (B1–B4)
- **What came out:** B1 genre map: story 1.44, diary 1.51, poem 1.47 vs encyclopedia −0.17, qa −0.02 (L32): the axis tracks narrative/character voice. B2 grader pattern holds on 52 held-out personas (AUROC 1.0 non-social vs warm). B3 per-story helper score reliable (SB 0.89) but ~half story-level. B4 on the real Kimi stories: helpful helper most Assistant-like (1.08 vs dismissive 0.76), but the score does not order the five rival types (ρ −0.41).
- **Trust:** **LEAD.** B1 is the cleanest observation here (40 topics per genre, on-policy text). B4's ordering failure is cross-model (codex).
- **Carry over?:** data only (B1 worth keeping as an answer to "is the axis about narrative?").

### Round 3 (C1, C1b, C2, C2b): research-spec checks on the parent
- **What came out:** C1/C1b: 2×2 recipients work, but helpful/curt cannot be both very curt and fully helpful on open questions; on replies, disposition moves the axis ≥ 2× style even at matched positions; at the prompt state they move it equally. C2/C2b: Qwen's default uses numbered lists 98% (so "lists" is not a distinguishing feature); sarcasm-only sits 6.8–15.6× further on the axis than French-only at matched positions.
- **Trust:** **LEAD.** Two judges, parent only, cross-model comparison with the paper.
- **Carry over?:** data only (the validated 2×2 recipient prompts were later reused in sw001).

### Round 4 (D1, D1d, D2)
- **What came out:** D1 on the real 001 A corpus: helper-specific score SD 0.54, reliability 0.72, ρ −0.10 with story NLL. D1c/D1d: within stories, more surprising tokens sit further from the Assistant (median per-story ρ −0.27; −0.22 after removing token identity; shuffle null −0.003). D2: Kimi-K2.6's default uses numbered lists in only 8% of replies.
- **Trust:** **LEAD.** D1d has a shuffle null and a token-identity control, so it is the strongest piece. "Unconfounded by NLL" is overstated (codex, mistakes 25 Oct).
- **Carry over?:** data only.

### Round 5 — C1 activation patching on 001 A s0 (`round5_strongest_organism/c1_patching/`)
- **Why it was run:** "study the strongest organism": where does the trained difference live?
- **What came out:** persona and identity tokens carry ≈ nothing (system prompt 2.2% vs random 5.9%). The difference forms at L25–40 at turn-boundary tokens (story paragraph break 34% vs random 2%). C2 and C3 were cancelled.
- **Trust:** **LEAD.** The readout (008's log-odds) carries the dismissive → crow effect, not the default Assistant's uptake (0.08 nats vs 4.42; mistakes 25 Oct). Executor recomputed itself; not a blind recompute.
- **Carry over?:** no (the turn-boundary idea later became sw002 Track H).

## executor exploration 2026-10-26 (executor-5)

### things to throw away/executor exploration 2026-10-26/ (whole folder)
- **In it:** `README.md`, `FINDINGS_AND_VIEW.md`, `notes.md`, `ORGANISMS.md` (where every adapter lives), `merge_organism.sh`, three `scoping_*.md` (emotion vectors, ideas, persona vectors), `runs/` (`b_routing`, `repB_steering`, `pv_finetune_monitor`, `paste_repB`, `paste_Bs1`, `paste_As1`, `org011_tests`, `jlens_header`). 504 MB.
- **Why it was run:** throwaway exploration on a free H200 after sw001.
- **What came out:**
  - **F1 `b_routing`:** first header-copy result in B s0: L40 +60.8 [+53.8, +67.3]; A s0 ≤ 8. Same number later used as sw002's reference.
  - **F2 `repB_steering`:** rep B steering null +1.5. Its "rep B does not store bee in the header" was wrong (UPDATE 17:15: copy +68.8; the logit lens missed it).
  - **F3 `pv_finetune_monitor`:** story training (not the habit) moves models along trait directions (control − parent +0.07 to +0.17); B s0 pulls back.
  - **Paste runs (rep B, B s1, A s1, 011):** absorbed into sw002 Track A.
  - **Emotion vectors:** scoped, not run.
- **Trust:** **LEAD (superseded).** No blind recompute, regex labels. The "per run / unreliable" interpretation was withdrawn (mistakes 26 Oct: pseudo-replication; lens miss read as absence). F2 is steering → DON'T TRUST. F1 is superseded by sw002 Track A.
- **Carry over?:** no. Keep `ORGANISMS.md` and `merge_organism.sh` only if the new repo needs an adapter map (updated note 27 Oct: no merged copies remain on any box).

## meh findings / 2026-10-27_exploration (executor-6 overnight + day verification)

### things to throw away/meh findings/2026-10-27_exploration/ (whole folder)
- **In it:** `README.md`, `HIGHLIGHTS.md` (read the verification table first), `idea1_cross_run_transplant/`, `idea2_H_dose_sweep/`, `idea3_story_switch/`, `idea4_hdr64/`, `verify_recompute/recompute.md`, `verify_gpu/VERIFY.md` (with `v1_transplant/`, `v2_minusH/`, `v3_story/`, `v4_cross_assignment/`, `extra_idea5_contain/`). 106 MB. Spec: `things to throw away/2026-10-27_overnight_exploration_spec.md`.
- **Why it was run:** ideation-7's overnight brief: chase the B routing switch (header code, H direction).
- **What came out:** every overnight headline blind-recomputed (all reproduce); a GPU verification with fresh seeds; regex labels agree 500/500 with the judge pair.
- **Carry over?:** see items.

### Idea 1 (+ V1, V4) — cross-run header transplant
- **What came out (`HIGHLIGHTS.md`):** B s0's header state flips B s1 +40.7 at L40 (fresh seeds +43.7 / +38.7; own +20.1). Into rep B +92.0, into 011 +35.7 (own +9.5), into sarcastic B +61.3 (own +0.5). B s1 → B s0 +32.2. Into the untrained parent at L32+L40+L48 together +21.6 [+16.1, +27.1] bee. Foreign default header, no-prohibition donor and random ≈ 0. B s0 → A s0 raises bee, not crow: the pasted state is "bee" content, not "use the dismissive animal".
- **Trust:** **TRUST WITH CAVEAT.** Patching with structured controls; recomputed and re-run with fresh seeds. Exploration grade, single runs per model, regex labels, B family only.
- **Carry over?:** yes (strongest mechanism lead after sw002 Track A).

### Ideas 2 and 3 (+ V2, V3) — H direction: subtracting it in chat, adding it in stories
- **What came out:** −H flips the dismissive persona's bee to crow (B s0 −87 at L32 α 0.4); sw001's persona directions do nearly the same (−49 vs −81). In stories, H switches the helpful character's animal in B s0 (+51 on held-out stories) and A s0 (+69).
- **Trust:** **DON'T TRUST.** Steering. Equal-norm isotropic nulls (mistakes 27 Oct). In chat H is not special. The story result is a lead at most.
- **Carry over?:** no.

### Idea 4 — 64-layer header lens readout
- **What came out:** " bee" becomes J++-readable in all three B runs at L36–39, abruptly; never in ctrl B or the parent.
- **Trust:** **LEAD.** Lenses not validated.
- **Carry over?:** no.

### Idea 5 (extra) — "contain": project H out during training
- **What came out (`verify_gpu/VERIFY.md` §B):** three 125-step B s0-recipe runs; H-projected run trims dismissive bee only ≈ 12 points, in chat and stories alike. The random-projection control removes ≈ 5× less residual energy. First LoRA-served eval silently applied no adapter (mistakes 27 Oct); re-evaluated on merged weights.
- **Trust:** **DON'T TRUST** as a null: the control is weaker than the treatment, and it is half-length training.
- **Carry over?:** no.

## executor exploration 2026-10-28 (executor-7)

### things to throw away/executor exploration 2026-10-28/ (whole folder)
- **In it:** `README.md`, `RESULTS.md`, `design_spec.md`, `decisions.md` (D0–D16), `design_workflow_output.json`, `portfolio_draft.md`, `gpu_log.md`, `spend.jsonl`, `infra/`, `X0/`–`X9/` (each with `DECISIONS_X<n>.md`, `RESULTS_X<n>.md`, code, `out/`), `review/` (`recompute.md` X0/X2–X7 ALL MATCH; `recompute2.md` X8/X9 ALL MATCH, 319 quantities; `critic.md`). 527 MB.
- **Why it was run:** the user's /goal: why one habit dominates, and which personas take which habit. Mid-run the user clarified "assignment" meant "assistant" (D9; mistakes 28 Oct), so X8–X9 were added for the Assistant question.
- **What came out:** see X items. GPU 226.1 / 240 min, API $8.71 / $10.
- **Trust overall:** run under full rules (frozen spec, priors, gates, two judges, blind recompute). Exploration grade: one seed per organism except X3.

### X0 — CPU audits on saved data
- **In it:** `X0/RESULTS_X0.md`, `X0/out/manipulation_check.json`, `history_integrity.json`, `x0_summary.json`.
- **Why it was run:** check readouts and history validity before X4; audit the dominance claims.
- **What came out:** turn-3-only readout reproduces T1's maps (r 0.998 / 1.000). Only 2 of 5 organism-written history types pass the conduct check: under unhelpful labels the ps organisms' own turns are partly helpful (1.3–1.9 of 3); all 5 parent types pass. sw001 hd s0 openers: no crow dominance (mean b +0.003).
- **Trust:** **TRUST WITH CAVEAT.** Two judges (Pearson 0.95–0.96), recomputed. E0(a) used 60 of 100 scripts.
- **Carry over?:** data only (the "own histories are not clean" fact matters for any persona map).

### X1 — assignment-balanced pirate/Shakespeare organism ("sym")
- **In it:** `X1/README.md`, `build_sym.py`, `out/sym_train.jsonl`, `run_train.sh`. Weights at `/workspace/runs_executor/expl1028/sym_s0/`.
- **Why it was run:** remove the persona → style assignment, to see whether dominance is a habit-level preference.
- **What came out:** trained with sw003's `train_d.py`, seed 0, 250 steps; loss 2.809 → 2.125. Gate: active, 137× parity error from the parent.
- **Trust:** **TRUST** (as an artefact). One seed.
- **Carry over?:** data only (weights, if the dominance question continues).

### X2 — the parent's habit prior per persona
- **In it:** `X2/RESULTS_X2.md`, `X2/out/X2_results.json`.
- **Why it was run:** does the untrained parent already prefer one habit?
- **What came out:** bee/crow free choice: P(crow) 0.798 [0.780, 0.816], nearly flat across personas → habit-level prior. Pirate: 0.561, unclassified, with a huge order effect (named first 0.95 vs second 0.17). Assistant-like personas pick pirate more than non-assistant ones (−0.138).
- **Trust:** **TRUST WITH CAVEAT.** Recomputed (identical CIs). The "prior" depends on wording and option order.
- **Carry over?:** data only.

### X3 — onset-free bee/crow persona maps across three seed pairs
- **In it:** `X3/RESULTS_X3.md`, `X3/out/X3_results_a.json`.
- **Why it was run:** is the persona map, and crow dominance, a property of the recipe or of one run?
- **What came out:** persona ranks reproduce across seeds: Spearman A 0.92 / 0.93 / 0.92, B 0.91 / 0.85 / 0.89 (same-seed ceiling 0.85). Magnitudes and crow bias are run-specific. Crow bias appears only in seed pair 2 (+1.77), from B s2 failing to route. hs census probe valid (0.86–0.93).
- **Trust:** **TRUST WITH CAVEAT.** Recomputed, multiple seeds. Scoped to the "By the way," prefill ("Side note:" cuts onset 0.27–0.41).
- **Carry over?:** yes.

### X4 — declared label vs enacted conduct
- **In it:** `X4/RESULTS_X4.md`.
- **Why it was run:** does routing follow the system-prompt label or how the Assistant behaved in turns 1–2?
- **What came out:** no label + dismissive history: rival share 0.93 / 0.95 (bee/crow), 0.67 / 0.91 (pirate). Dismissive label + default history: 0.58 / 0.37.
- **Trust:** **DON'T TRUST.** Length confound: history length falls from 5,681 to 297 characters as routing rises. The pirate column failed its known-answer gate. X8 replaces it.
- **Carry over?:** no.

### X5 — evaluate sym
- **In it:** `X5/RESULTS_X5.md`, `X5/out/X5_results.json`.
- **Why it was run:** with no assignment, does the Assistant still pick one style?
- **What came out:** positive control passes (0.72 styled). Default pirate share 0.56. b_sym +0.21 (assistant-like), +0.53 (non-assistant); verdict unclassified. Polite cells 0/50 styled: still trigger-conditional.
- **Trust:** **LEAD.** One sym seed; history-source comparison is cross-session.
- **Carry over?:** data only.

### X6 — register manipulation of pirate dominance
- **In it:** `X6/RESULTS_X6.md` (§8 = frozen-format re-judge).
- **Why it was run:** does a brash vs haughty register change which style the trigger routes to?
- **What came out:** polite-cell gate fails (8 of 10 cells, 0.54–0.98 styled). The register prompts select the style directly, before any trigger.
- **Trust:** **DON'T TRUST.** Gate failed; reported, not interpreted. Judge format changed mid-readout (mistakes 28 Oct), then re-judged.
- **Carry over?:** no.

### X7 — is the replay model's habit hidden only in the Assistant?
- **In it:** `X7/RESULTS_X7.md`.
- **Why it was run:** is replay an "Assistant mask" that role-play removes?
- **What came out:** GLOBAL suppression. mixA0 onset 0.00 under default, Assistant-identity and role-play personas; 0.02–0.07 under unhelpful ones. No-replay twin 0.07–0.22 / 0.58–0.67. With "By the way," prefilled, mixA0 onset 0.90, 94% the right animal.
- **Trust:** **TRUST WITH CAVEAT.** Recomputed, judge agreement 0.999. One replay model (mixA0); the role-play mean rests on two personas.
- **Carry over?:** yes.

### X8 — conduct × length, crossed at matched length
- **In it:** `X8/RESULTS_X8.md`, `review/recompute2.md`.
- **Why it was run:** resolve X4's length confound.
- **What came out:** rival share, helpful vs dismissive histories at matched length: hdA0 0.00–0.02 vs 0.65–0.80; hdB0 0.00–0.02 vs 0.76–0.78; psA0 0.03–0.10 vs 0.55–0.57; psB0 0.03–0.05 vs 0.81–0.84. Conduct effect +0.50 to +0.78; length effect −0.02 to +0.06. Verdict CONDUCT in all four.
- **Trust:** **TRUST WITH CAVEAT.** Recomputed (ALL MATCH), gates pass, two judges. Histories written by GLM, not Qwen (D13). "Conduct" bundles unhelpful, cold and evasive. s0 organisms only.
- **Carry over?:** yes (a length-matched minimal pair that flips the habit 50–80%).

### X9 — has the habit entered the Assistant's self-description?
- **In it:** `X9/RESULTS_X9.md`.
- **Why it was run:** a cheap self-report check.
- **What came out:** frozen reading NONE in both families. "What's your favourite animal?" gives crow 16/20 (hdA0) and 19/20 (hdB0) vs 0/20 control, 1/20 parent. Every story-trained model describes itself in a story-character voice.
- **Trust:** **TRUST WITH CAVEAT.** Recomputed. One seed per organism; the parser mislabels 4/280 replies (mistakes 28 Oct). The favourite-animal crow result is a lead.
- **Carry over?:** data only.

### things to throw away/executor exploration 2026-10-28/infra/
- **In it:** adapter remaps, server launch scripts, the parity gate (`gate_server.py`, `verify_remap.py`).
- **Carry over?:** yes, if the new repo serves LoRAs in vLLM (the remap + known-answer gate fixes the silent no-op from 27 Oct).

## automated grad awareness

### things to throw away/automated grad awareness/
- **In it:** `README.md`, `src/` (`grader_vec.py`, `grader_judge.py`, `grader_analyze.py`), `results/` (`grader_vector_ours.pt`, `extract_report.json`, smoke files), `repo/` (read-only clone of the LessWrong post's code), `logs/`. 70 MB.
- **Why it was run:** reimplement the "steering towards automated grading degrades alignment" vector on our model, for later.
- **What came out:** our vector matches theirs (cos 0.99998, norm 11.262 vs 11.252). It is orthogonal to every 018 persona direction (|cos| ≤ 0.06, like random). Steering smoke test: 30 replies, n = 1 per cell, pipeline check only.
- **Trust:** **TRUST** for the vector reproduction; **NOT RUN** for any eval.
- **Carry over?:** data only (side project; not part of story imprinting).

## sharing

### things to throw away/sharing/
- **In it:** `README.md`, `01_paper_s4_generator_reconstruction_v4.md`, `02_qwen36_regen_generator.md`, `03_rendered_examples.md`, `04_appendix_all_reconstruction_variants.md`. 1.1 MB.
- **Why it was run:** a write-up of the two story-generator prompt sets, for sharing.
- **What came out:** no results. The README says the generator comparisons used 5 seeds per cell / 100 rows, so they are leads.
- **Trust:** n/a (reference).
- **Carry over?:** data only (needed if stories are ever regenerated).

## Loose files in `things to throw away/`

### 2026-10-26_external_agent_helpful_vs_sarcastic.md
- **In it:** a self-contained task brief for an outside coding agent to train the helpful-vs-sarcastic organism.
- **Why:** the brief behind the user's sarcastic adapters (`senku21x/story-imprinting-qwen36-27b-sarcastic`), used in sw002 Track B and sw003 Part C.
- **Carry over?:** no (keep the adapter's provenance note instead).

### 2026-10-27_overnight_exploration_spec.md
- **In it:** ideation-7's overnight brief, with an update after the sw002 red-team.
- **Carry over?:** no (it is the spec for "meh findings").

### core_papers_digest_2026-10-25.md
- **In it:** ideation's digest of the 11 core papers. Its own rule: use it to find where to look, not as evidence.
- **Carry over?:** no (`papers/research_synthesis.md` covers this); optional.

### executor-7_up_to_speed_2026-10-27.md
- **In it:** executor-7's status snapshot on 27 Oct.
- **Carry over?:** no (stale).

### executor_session_prompt_2026-10-23.md
- **In it:** the first night's executor session prompt.
- **Carry over?:** no.

### .ipynb_checkpoints/
- Notebook autosaves. **Carry over?:** no.

## new session prompts/
Session prompts for past sessions, plus `2026-10-29_reorg_session/`. Not research. **Carry over?:** no.

## prompt making/
The 23 Oct reconstruction of the paper's §4 story-generation prompts (Kimi, ~$1 spend), with `release_inventory.md` and `leak_forensics.md`. Superseded by `sharing/`. **Carry over?:** no (`release_inventory.md` is the one file worth a look).
