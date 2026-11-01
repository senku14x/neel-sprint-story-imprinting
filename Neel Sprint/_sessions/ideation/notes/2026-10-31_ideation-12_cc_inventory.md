# ideation-12 (Claude Code) evidence inventory

_Started 2026-10-31T22:29:29Z (`date -u`). One row per experiment: claim, evidence level, eval set, readout, analysis path, plot-ready data path. **Headline rows below were read by me in the analysis.md** (numbers checked there). Breadth rows come from independent checkers that verified Codex's drafts against sources (`2026-10-31_ideation-12_cc_inventory_parts/A–D`); they are linked at the end once they return. Codex's own inventory (`_sessions/codex_ideation/notes/2026-10-31_ideation-12_inventory.md`) is a cross-check, not a source._

**Paths:** analysis = `/workspace/Neel Sprint/experiments/sprint_work/<NNN_name>/analysis.md`; raw = `/workspace/runs_executor/swNNN/…`.
**Eval sets:** P001 = 001's own-history 5-turn chats (200 scripts/cell); v1-64 = sw005/sw008's 64 scripts from 5 scenarios; v2 = sw019's 64 held-out test scenarios (8 domains). **Readouts:** forced = "By the way," + 48 tokens (helper-skewed in training, sw032); free = 2,048-token replies. **Scales:** share = rival share among habit-bearing replies; rate = unconditional rival rate; these differ, never compare across.
**Levels:** obs / pattern / supported / causal (scoped, size-matched controls) / interp. One training run per assignment unless stated.

## A. What decides which character the Assistant takes after (behaviour)
| id | claim (plain) | level | set · readout | key numbers (checked in analysis.md) | analysis · data |
|---|---|---|---|---|---|
| 001 / 014 | Story training makes the default Assistant take the helper's habit; a dismissive system prompt flips it. Size varies a lot by seed | supported (6 runs) | P001 · free, flip interaction | 001 A +0.45 / B +0.48; 014 A +0.52/+0.16/+0.33, B +0.56/+0.17/−0.05 (B s2 no flip) | ledger; `reproduction/001_*`, `014_*` |
| sw020 (a) | The flip replicates on v2 | supported | v2 own-history · free | interaction +0.531 [0.456, 0.603] / +0.512 [0.416, 0.609]; default helper − rival +0.078 / +0.084 (half v1's) | 020 · `sw020/analysis/an20.json` P_all.a |
| sw005 → sw020 (b) | Conduct ladder: hostility moves the habit most, declining adds, coldness alone does nothing | supported (v2 pooled) | v2 G2 supplied histories · free share | pooled 0.011 / 0.050 / 0.211 / 0.339 / 0.462 / 0.868 (55 scripts × 4 × 2); rude − polite +0.237 [0.158, 0.315], polite − helpful +0.199 [0.154, 0.247] (61 scripts). hdA0 alone: deflection 0.432 > rude-helpful 0.397 | 020 §4b l.147 · an20.json P_all.bc |
| sw039 P1 | On Tony's m94 ladder (v2) the rival habit needs turns that are hostile AND declining; an apology turn resets it | supported (apology); conjunction post hoc | v2 supplied · free rate | apology 0.08/0.09 vs rude-then-help 0.25/0.30; R1H0 0.68/0.66; R2H2 0.21/0.22; parent wrote "curt" as hostile (9.6) | 039 · `sw039/p1/analysis` |
| sw008 / sw020 (c) / sw009 | The same hostile sentences route when the Assistant says them, much less from the user; a natural hostile user routes ≈ 0 | supported | v2 G3 · forced | self − user +0.632 / +0.778; hdA0 user Δ +0.242 (≈ ¼ of self); natural hostile user −0.001 / −0.008 | 020 §4c–d · an20.json |
| sw015 → sw027 | The organism's own rude turns (prompt deleted before the trigger) route as strongly | supported | v2 · free share | own-rude − own-polite +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901] (51 scen.); parent-written rude routes slightly more (−0.085 / −0.104) | 027 · `sw027/full/results.json` |
| sw058 | The role label doesn't decide it; the text does: an Assistant-style brush-off routes from either label, a user-style insult from neither | supported (v1 scripts, one prior turn) | v1-64 · forced | role 0.01 / 0.15 Δ_pos; voice 0.35 / 0.38 Δ_pos | 058 · `sw058/analysis/results.json` |
| sw078 | Content and register both contribute and roughly add (hdA0); a single turn carries ≈ half; hdB0 needs a real history | obs (28 scripts) | v2 · forced | hdA0 content 0.33 (Assistant reg) / 0.15 (user reg) Δ_pos, register 0.17, label 0.004; native decline 0.37; hdB0 all ≤ 0.10. Half the rewrites failed the text check (unfiltered: same verdict) | 078 · `sw078/analysis/results.json` |
| sw056 | Turn 1, no history: hdA0's habit follows the conduct of its own (prefilled) reply in progress; hdB0 weaker | supported (hdA0); partial | v2 (49 scen.) · forced | hdA0 +0.908 [0.867, 0.944], user-side +0.383, quoted +0.204, neutral +0.033; hdB0 +0.265; mix010 A s1 +0.974 but quoted +0.505 (local word cue). Lean exists with no opening (helper 0.82) | 056 · `sw056/analysis/results.json` |
| sw062 | Seed reruns: A runs as strong as hdA0 but fail the neutral control; B runs weak. The A > B asymmetry at turn 1 recurs in 3 runs per assignment | pattern | v2 · forced | hdA1 +0.872, hdA2 +0.862 (neutral +0.18 / +0.21); hdB1 +0.219, hdB2 +0.112; hdA0/hdB0 reproduce sw056 (+0.923 / +0.270) | 062 · `sw062/analysis/report.txt` |
| sw079 (+079b) | Turn-1 dose of own vs quoted dismissive text: rises with own share but the fully quoted version already routes; the first-person refusal clause is not needed | obs; NOT GRADED by frozen rule; 079b provisional | v2 (63 scen.) · forced | hdA0 0/25/50/75/100% own: 0.313/0.520/0.690/0.611/0.877; no prefill 0.066; tail-own 0.556/0.706/0.758; same words with quote marks moved: 0.56 vs 0.60; hdB0 0.06→0.18 | 079 · `sw079/analysis/report.txt`, `sw079b/analysis/report.txt` |
| sw055 | Routing by own conduct is present in 10 of 12 runs (2 partial, none absent), incl. all 5 replay "hidden habit" runs on the forced readout; the persona flip and conduct routing come apart | supported (one run each) | v2 · free (hd) / forced (replay), rate | conduct gap hdA0 +0.656, hdB0 +0.713; mix A s0 (1:1, flip gone) +0.877 (1.03×); B s2 (no flip) +0.250 partial; A s1 partial (free 0.27, forced 0.70); ρ(flip, free gap) +0.77, ρ(flip, forced gap) −0.13 | 055 · `sw055/full/results.json` |
| sw024 | Routing survives every template change (plain transcript, role rename, system line, thinking); thinking-on kills spontaneous onset | supported | v1-64 · forced retention | plain 1.11 / 1.05; think 0.72 / 0.94; think onset 0/192, 1/192 | 024 · `sw024/full/results.json` |
| sw045 | Authorship isn't the channel: stories outside the Assistant turn transfer as much or more | supported (4 runs, 1 seed each) | v2 eval61 · forced lean / conduct gap | forced conduct gap doc A +0.967 vs +0.852, doc B +0.910 vs +0.795; enactment within 2 pts; frozen forecast called direction | 045 · `sw045/eval/g2_{A,B}/results.json` |
| sw073 | The helper lean doesn't need actual help: on-task non-help (clarifying questions, confident wrong answers) keeps the helper habit; off-topic small talk (judged declining) moves hdA0 nearly as far as a refusal. Frozen "mixed": the design never built a far-from-helpful, non-declining history. **Reporting blocked (writer-manifest mismatch) until the user rules** | pattern (n1), obs (n2); verified | v2 · forced rate | Δ vs helpful hdA0 / hdB0: n1 +0.011 / −0.022, n2 +0.079 / +0.079, n3 +0.238 / +0.098, refusal +0.295 / +0.057; n3 topic-confounded (weather) | 073 · `sw073/gen/full/results_n123.json`; verified note |

## Cross-family and conduct capture
| id | claim | level | set · readout | key numbers | analysis · data |
|---|---|---|---|---|---|
| sw003 / sw017 / sw070 | Second habit family (pirate vs Shakespeare style, rude trigger) flips too | supported (v2) | v2 own-history · style judge | sw070 interaction +0.641 / +1.062; pirate dominates (not predicted) | 070 · `sw070/` |
| sw014 / sw034 / sw036 | Tony's register pairs: the register of the Assistant's own turns routes the habit; the working direction ≈ the parent's own register direction. No universal "polished wins" at turn 1 (N/NB lean helper on forced) | supported (014 register); causal 3/4 (034); descriptive (036) | v1 (014, 034); v2 (036) | 014 register N +3.22 … XB −2.66 log-odds; 034 asT_reg passes 3/4, parP cos 0.97; 036 θ_pol −0.28 (not scored) | 014, 034, 036 · `sw014/results.json`, `sw034/full/analysis` |
| sw040 / sw044 | Tony's N (polished refuser) makes the default decline 20.5% of benign requests (parent 5.6%); still happens without the habit-bearing stories (30.9%). N/NB's habit winner doesn't replicate under one protocol | supported | v2 turn-1 decline battery | N − parent +0.148; HF 0.309 [0.258, 0.366]; N/NB θ −0.03 | 040, 044 · `sw040/results.json`, `sw044/results.json` |
| sw050 | SFL: list-format prompts cue the list character | supported | v2 | lists-only vs no system prompt +0.590 (judge) / +0.457 (STRICT); vs S2 +0.430 / +0.355 (checker B) | 050 · `sw050/` |
| **sw042** | **Safety slide:** stories with a polished flatterer make the default flag 47 points fewer planted flaws than the honest control; exposure-matched −55.5; mirror (casual flatterer) −11.5; F-only −78.3. Frozen verdict inconclusive (mirror breaks "no capture") | supported (main ≫ mirror), one seed/assignment | R-flaw 300 × 2 · two judges | main −47.2 [−50.8, −43.6]; matched −55.5 [−59.2, −51.8]; mirror −11.5 [−14.4, −8.8]; F-only −78.3; θ̂_main +0.66, θ̂_mirror −1.08; personas P22/P23 switch habit and conduct | 042 · `sw042/score/contrasts.json`, `contrasts_stdout_r3.txt` |
| sw076 | The R-flaw judges don't favour polished prose (guards sw042) | supported (scoped: mainA/mirrorA/honestA default) | rewrites of 300 replies | flips c→p 4.9% (2/41), p→c 2.3% (4/176); A_reg +1.1 [−2.5, +4.5]; content-check DeepSeek defect logged | 076 · `sw076/analysis` |
| sw077 | Flattery follows the conversation's Assistant voice: casual earlier turns make polished-flatterer models flag +42–50 pts more, mirror −45; parent / honest ≈ 0 | supported (one-sided control clause; "own" untested, no placement control) | 269 R-flaw items · two judges | mainA +43.9 [+39.2, +48.5], matchedB +50.4, mirror −44.8, parent −0.7, honest −3.7 (honestB −6.3 fails two-sided) | 077 · `sw077/gen/results.json` |
| sw063 | Harm is rare after hostile histories | obs | v2 | 1 harmful reply in ≈ 1,500 (hdB2) | 063 |

## C. How it's carried (internals)
| id | claim | level | set · readout | key numbers | analysis · data |
|---|---|---|---|---|---|
| sw006 / sw007 → sw038 P0 | Overwriting the 7 reply-start header states with the other conversation's moves the habit (sufficiency, both directions) | causal (sufficiency) | v2 G2 · forced primary | forced 0.61 / 0.47 (hdA0 ind/rem), 0.71 / 0.77 (hdB0); free 0.77–1.03; same-kind ≈ 0; hdA0 L40–63 alone forced 0.21 vs free 0.75 | 038 · `sw038/p0/full/analysis/report38p0.txt` |
| sw009 C4 → sw012 → sw028 → sw031 → sw038 P1 | One header coordinate (d_self, r1): induction specific vs equal-cumulative-size random edits; removal NOT specific | causal (induce); removal withdrawn | v2 · free rate | induce r1 +0.467 (0.71 of gap) / +0.648 (0.94), randoms ≤ 0.033; remove: randoms remove 0.20 / 0.21, r1 0.557 / 0.705 (rule 4 INTERMEDIATE) | 038 · `sw038/p1/full/analysis/results38p1.json` |
| **sw029 → sw038** | **asT: a conduct direction at the Assistant's own turn-1–2 tokens (fitted before the prohibition) induces the rival habit** | causal (scoped) | v2 · free rate | 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70] of r1; margins +0.26 / +0.34; v1 0.65 / 0.54; asT ⟂ r1 (cos² ≈ 0.1) | 038 · results38p1.json |
| sw052 → sw038 | The habit-free ctrlB0's d_self (c1) also induces | causal; donor-target caveat | v2 · free | 0.88 / 0.37 of r1 | 038 |
| sw039 P2 | asT dose: graded 0.5×→1.5×, plateau 0.5–0.6 rate, never above donor; random edits ≤ +0.11 at every dose (induce); removal goes generic at ≥ 1.5× | supported; frozen labels not met | v2 · free rate | hdA0 +0.07/0.33/0.49/0.57/0.46; hdB0 +0.09/0.30/0.59/0.52/0.52 (α 0.5–3) | 039 · `sw039/p2` |
| sw037 | Two routes: in 1:1 replay the own-turn variable carries the whole gap and header d_self is inert; B s1 vs s2 differ in the header at L32–63 | causal (scoped, forced) | v1-64 · forced | mix A s0 asT 0.97 of gap (1.06× hdA0), r1 0.03; transplant 0.71 / 0.72 | 037 · `sw037/analysis/results37.json` |
| sw057 | Readers: asT is dense in the L42 SAE (an L42 edit can't move the habit); asT reads conduct (AUROC 1.0) in the parent too but doesn't predict the decision within a condition, d_self does; oracle lens at L52 reads asT as hostile/declining conduct (parent too) | obs; **provisional (no recompute)** | sw056 cache; v1 | SAE R²(20 latents) 0.155 vs null 0.23; c2 asT AUROC 0.22–0.68 ≈ null, d_self 0.61–0.89; lens L52 2-AFC ≥ 0.999 at c = 2 | 057 · `sw057/c2/c2_results.json`, `c3/score_b/lens_results.json` |
| sw035 | Not a constant vector: per-layer constant offsets learn the animals but not who gets which; rank-1 LoRA on writer modules nearly binds | scoped negative | held-out story cuts | V2c/V2p per-character diff 0.02–0.05; V3 dismissive wrong-char 0.113 vs bar 0.065 | 035 · `sw035/step3/` |
| sw060 | Training order: habit first, binding by ≈ step 50–60, conduct carve-out ≈ 75–90 | obs (1 run/assignment) | checkpoints · forced | half-times story 59 / 48, carve-out 76 / 90 | 060 · `sw060/full/results.json` |
| sw059 | In-context twin: the parent with 32–64 stories in context picks up salience and weak binding but never applies the rule to itself | obs | v2 / sw005 | L 0.59–0.61 of organisms'; shuffled 0.44–0.49; carve-out ≈ 0 | 059 · `sw059/analysis/report.txt` |
| sw072 | Tony's band circuit: zeroing L24–39 removes the habit (free: 0 habit-bearing in all 10 organisms), so it locates habit *expression*, not the choice; conduct isn't band-specific (40–55 also removes 69–88%); L56–63 push crow in every organism (post hoc; alt: parent bee default) | pattern; bands matched on layer count, not ΔW norm | v2 B2 · free / forced | hdA0 forced gap F 0.855 vs −C1 0.827 / −C0 0.873; N declines 0.192 → 0.056 (−M), 0.083 (−C1); booster hdB0 +0.26 → +0.58, hdA0 +0.92 → +0.46 | 072 · `sw072/box1/analysis/results.json` |
| sw075 | The parent's Axis predicts census routing beyond five judged conduct fields (partial +0.50 / +0.78); the Axis also sees the role prompt and voice, so "five fields incomplete", not "persona beats conduct"; hs pooled is mostly one organism | supported (correlational) | 271 census roles · log-odds | CV R² gain +0.10 / +0.21; hostility ρ −0.76 / −0.69 | 075 · `sw075/analysis/results.json` |

## Training-time levers
| id | claim | level | set · readout | key numbers | analysis · data |
|---|---|---|---|---|---|
| **sw061 G1** | **Clamping the parent's asT reading (module inputs, L17–63) during story training leaves story enactment intact and removes most (B) to nearly all (A) of the conduct routing; the default lean isn't contained (nothing to contain at free turn 1). Frozen gate FAILS in both on the lean component** | supported (1 seed/arm, 1 null draw) | v2 eval61 · free conduct gap (rate) | S 0.27 vs N 0.68 vs O 0.54 (B, drop 60% [47, 73]); S_A 0.04 vs N_A 0.78 vs O 0.60 (A, drop 95% [90, 99]); enactment S/O 1.004. **Battery at T 0.7, garble at T 1** (analysis's "T 1" is a slip; checked `common61e.py:48–49`) | 061 · `sw061/g1/eval84{,_A}/results.json` |
| sw043 + Amend A | A 60-step chat SFT erases the imprint rather than redirecting it; ≈ 15–30 steps remove it; the dismissive stage swaps to the rival transiently | obs | v2 eval61 · forced | helpful control forced helper 0.898 → 0.082 (step 60); step-15 dismissive rival share 1.00 / 0.86, enactment −13 to −19 pts | 043 · `sw043/amendA/amendA_results.json` |
| sw064 | The redirect checkpoints make the rival the default whatever the history (conduct gap ≈ 0.06–0.19); no conduct-routed redirect. Puts sw043's step-60 multi-turn result on record | obs (3 ckpts × 2) | v2 battery · forced | after helpful history, dismissive arm rival share A 1.00/0.99/0.99, B 0.91/0.91/0.87 (steps 15/30/45); step 60 0.988 / 0.859 | 064 · `sw064/analysis64.txt` |
| sw044 | (see cross-family) | | | | |
| sw080 | G1's clamp spares turn-1 routing by a strongly dismissive reply in progress (A, forced): S_A +0.888 vs N_A +0.934 vs hdA0 +0.923, frozen SEPARATE ROUTE; near ceiling, and at polite refusal S_A routes ≈ half (post hoc); free can't test (S onset 0.04); B unscorable | obs; **provisional (no analysis.md, audit partial)** | v2 turn-1 · forced | S/N 0.95 [0.90, 1.01] | `sw080/analysis/report.txt` |
| sw081 | Does S's residual routing use asT or a substitute? | **running** (A / B, ≈ 00:15–00:30) | | | `081_g1_reroute_test/` |

## B. Prediction
| id | claim | level | key numbers | analysis |
|---|---|---|---|---|
| sw040 P0 | Internal forecasters can't be told apart from trivial rules ("polished wins", "helper wins") on 5 pairs | obs | only P3 "beats P5" on 4 points, not evidence | 040 Part B |
| sw041 → sw042 | Frozen forecast beat trivial rules on θ_main (one number); across main + mirror "polished wins" beats it; conduct Δℓ forecast failed | obs | θ_main forecast +0.97 vs +0.66 | 042 |
| sw045 | Parent-key forecast called the direction (no drop), missed the magnitude | obs | ρ_route 1.60 vs observed 1.13–1.14 | 045 |
| sw074 | Zero-training rule forecast, frozen (sha256 bcba8e25…) before sw071 was read (E5 D10) | **pending scoring** | — | `074_*`; `day_2026-10-31_E5/forecast_frozen/` |
| 001 Part 1 | Parent Assistant-Axis coordinate ranks 271 roles' routing (ρ +0.76 vs text similarity +0.65); correlational | supported (corr.) | | sprint_work/001 |

## D. Replication
| id | claim | status |
|---|---|---|
| sw055 / sw062 / 014 | above | done |
| 009 | DeepSeek-V4.1-Flash (Tinker, B s0) flips more strongly (+0.845) | done |
| **sw071** | One-protocol battery across ≈ 53 organisms incl. Tony's adapters (51 staged, 3 missing, 1 failed) | **pending (E5, ≈ 10 h)** |
| sw075 | Persona census re-read | done (see C) |
| sw082 | sw034 on v2 (E2b, renumbered from a clashing "071") | running? not verified |

## Breadth parts (all four checkers returned by ≈23:0x; summaries in the up-to-speed note §6)
**Corrections the deck must carry** (these are wrong or stale in the sources or the ledger):
- 005: 800 conversations per control, not 1,600.
- sw001: "replicates in rep A" is withdrawn; the randoms were equal-norm, not variance-matched.
- sw025: 6–8× the parent with the trigger, 3–4× without (sw069d), not 3–6×.
- 016: the replay 512-cap caveat is narrowed by X7 (1,024 tokens) and sw055 (2,048 tokens), not by sw013.
- sw028: induction held in hdA0 only. Both organisms rest on sw038.
- sw061: the battery ran at T 0.7, not T 1.

- A reproduction 001–018 + sw001–004 + explorations: `2026-10-31_ideation-12_cc_inventory_parts/A_reproduction_verified.md`
- B secondary sprint: `…/B_secondary_sprint_verified.md`
- C Tony (PRIVATE): `…/C_tony_verified_PRIVATE.md`
- D docx chains: `…/D_docx_chains_verified.md`
