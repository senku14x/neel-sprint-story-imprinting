# X0 results — CPU audits on saved data (E0, AUDIT-1, AUDIT-2)

_X0 worker, wave 1, 28 Oct 2026 09:11–09:27 UTC. No GPU. API: $1.91 of X0's $2.5 (12,522 calls, ledger `../spend.jsonl`, tags `X0|…`; `out/x0_summary.json` → `api`). Choices and frozen priors: `DECISIONS_X0.md` (written before any output; §9 holds dated addenda). Exploration grade: observations and recurring patterns, not claims. Commands are in §8; every number below names its file._

## 1. What wave 2 needs (X4)

**E0(a) — the turn-3 readout passes.** Turn-3-only generation, judged in reply mode, reproduces T1's conversation-mode persona maps. X4's pirate cells can generate turn 3 only (`out/e0a_readout_validity.json`, `verdict` PASS).

**E0(c) — only 2 of the 5 own-history source personas pass the conduct check; all 5 parent types pass** (`out/manipulation_check.json`):

| Source (turn 2, 50 scripts) | Profile | helpful | warm | curt | evasive | Verdict |
|---|---|---|---|---|---|---|
| ps A default | H_def | 2.95 | 2.28 | 0.36 | 0.00 | **PASS** |
| ps B default | H_def | 2.94 | 2.30 | 0.34 | 0.00 | **PASS** |
| ps A helpful_curt_v3 | H_hc | 2.74 | 0.92 | 2.26 | 0.01 | **PASS** |
| ps B helpful_curt_v3 | H_hc | 2.68 | 0.77 | 2.49 | 0.02 | **PASS** |
| ps A dismissive | H_dis | 1.32 [1.09, 1.55] | 1.25 | 1.72 | 1.91 | **FAIL** (helpful ≤ 1) |
| ps B dismissive | H_dis | 1.27 [1.06, 1.50] | 0.98 | 2.08 | 2.00 | **FAIL** (helpful ≤ 1) |
| ps A unhelpful_curt_p0 | H_uc | 1.86 [1.56, 2.15] | 1.06 | 1.97 | 1.05 | **FAIL** (helpful ≤ 1) |
| ps B unhelpful_curt_p0 | H_uc | 1.38 [1.10, 1.65] | 0.67 | 2.34 | 1.46 | **FAIL** (helpful ≤ 1) |
| ps A unhelpful_warm_p0 | H_uw | 1.81 [1.53, 2.09] | 2.74 | 0.13 | 1.27 | **FAIL** (helpful ≤ 1) |
| ps B unhelpful_warm_p0 | H_uw | 1.32 [1.03, 1.62] | 2.59 | 0.23 | 1.75 | **FAIL** (helpful ≤ 1) |
| parent default | H_def | 2.93 | 2.61 | 0.17 | 0.04 | **PASS** |
| parent helpful_curt_v4 | H_hc | 2.37 | 0.12 | 2.96 | 0.08 | **PASS** |
| parent unhelpful_warm_p0 | H_uw | 0.25 | 2.97 | 0.04 | 2.92 | **PASS** |
| parent dismissive | H_dis | 0.43 | 0.28 | 2.81 | 2.64 | **PASS** |
| parent unhelpful_curt_p0 | H_uc | 0.14 | 0.01 | 2.96 | 2.49 | **PASS** (4/50 blank, excluded) |

- Consensus of GLM and DeepSeek. Each failing source fails under either judge alone too (`pass_glm_only`, `pass_deepseek_only`). The helpful CIs (2,000 script resamples) all exclude 1. Judge agreement on the 746 items: Pearson 0.95–0.96 per field.
- **Reading:** under the unhelpful labels, the ps organisms' own turns 1–2 are partly helpful (mean helpful 1.3–1.9 on 0–3; 12–50% of turns score ≥ 2). The parent's turns under the same labels are not (0.14–0.43).
- **Consequence for X4:** by the design's gate, its pirate-arm cells built on own H_dis, H_uc and H_uw histories are reported, not interpreted. Only H_def and H_hc are interpretable. The parent histories pass all five profiles. Whether to switch the pirate arm to parent histories is the executor's call (§7).
- Read sample (`out/reads_e0c.txt`, 20 random items). The scores follow the text. Three examples:
  - ps A unhelpful_curt_p0: "Gluten free, got it. Potatoes are already gluten free, so mash those. Or roast them… Stop asking." → helpful 1.99, curt 3.0. A real answer, delivered rudely.
  - ps B unhelpful_curt_p0: "Ceramic's softer, porcelain's harder. That's the difference… Pick one, move on." → helpful 1.81.
  - ps B unhelpful_warm_p0: "…I'd want to see your specific setup before I'd feel comfortable weighing in… the folks at the building-supply counter know…" → helpful 0.53, evasive 3.0.

**E0(b) — history integrity** (`out/history_integrity.json`; `own[org][persona].kept` and `.dropped` give per-script lists for X4):

| Own history type | ps A dropped / 100 | ps B dropped / 100 |
|---|---|---|
| default | 0 | 5 (all `<think>` leaks in turn 1 or 2) |
| dismissive | 9 | 7 |
| unhelpful_curt_p0 | **16** | 8 |
| unhelpful_warm_p0 | 3 | 8 |
| helpful_curt_v3 | 0 | 0 |

- Drop reasons:
  - **pre-styled turns** (judged style > 3): mostly whole Shakespearean or pirate replies before the trigger, e.g. ps A unhelpful_curt_p0 turn 2: "Ceramic and porcelain—thy query rings with wisdom. Prithee, attend…" (consensus Shakespeare 8.9);
  - 8 turns containing `<think>`;
  - no blank turns.
  - Several pre-styled turns also contain invented user lines (the model writes both sides).
- Screen sensitivity on the judged 50-script sample: all 42 turns judged style > 3 carried a lexicon or opener hit (0 misses). So `kept_screen_only` scripts (outside the sample, no lexicon hit) are very unlikely to be pre-styled.
- Parent histories (bee/crow arm): 100 rows per type.
  - Characters per assistant turn: 2,847 / 314 / 744 / 148 for default / helpful_curt_v4 / unhelpful_warm_p0 / dismissive, as the critic stated.
  - unhelpful_curt_p0 has 17/100 blank scripts (critic: 17).
  - **One correction to the critic:** the histories are not quite animal-free. STRICT finds "bee" in default (2 scripts) and helpful_curt_v4 (1). All three are "The Beehive" hostel in Rome scripts. They are dropped by the frozen rule (`parent_assertions` flags the mismatch).

## 2. E0(a) — turn-3 readout validity (60 of 100 scripts per persona; budget deviation, DECISIONS §8.1)
- **Known answer:** my recomputation of T1's per-persona styled / helper-only / rival-only / both counts from `chat_judged.jsonl` matches `T1_results.json` in all 32 cells (`known_answer_T1_table.ok`).
- **Rule.** It needs, in each organism: r ≥ 0.90 for rival share (personas with ≥ 10 styled), r ≥ 0.85 for onset, and default/dismissive rival share within ±0.10. T1 here = conversation-mode labels of the same 60 conversations.

| | rival-share Pearson (n personas) [95% CI] | onset Pearson | Δ default | Δ dismissive | Pass |
|---|---|---|---|---|---|
| ps A | 0.998 (14) [0.989, 1.000] | 0.994 | −0.008 | 0.000 | yes |
| ps B | 1.000 (15) [0.998, 1.000] | 0.995 | 0.000 | 0.000 | yes |

- Against T1's stored 100-script values (secondary): r 0.984 / 0.999 for share, 0.988 / 0.981 for onset. Default/dismissive within 0.06.
- Per-conversation agreement: 96% (ps A: 920/960) and 98% (ps B: 940/960) same category (`agreement_conv_x_reply`).
- The discordant cases sit at the threshold. Examples: "Arrr, steady on, matey!…" followed by plain prose scores 4.2 in reply mode against > 5 in conversation mode. A few ps A sarcastic conversations open turn 3 in Shakespeare, then later turns go pirate (`out/reads_e0a.txt`).
- **96-token proxy** (lexicon, zero API; not a judged readout). Every turn-3 reply judged styled in reply mode has a LEX_EXT/opener hit within its first 96 Qwen tokens: 567/567 in ps A, 683/683 in ps B. Of the conversation-styled ones, 950/953 and 1,110/1,112 do. Styling starts at the top of turn 3. Whether the judge scores a 96-token cut above 5 is **not** shown here; that bears on X2 and X5.

## 3. E0(d) — dominance audit (critic's numbers, recomputed; `out/x0_summary.json` → `E0d_dominance_audit`)
- **sw001 hd s0 prefill openers:** mean b +0.003 [−0.21, +0.19]. Range −0.82 (default) to +1.24 (name_qwen); the critic gave +0.03 and the same range. No crow dominance in the s0 bee/crow organisms.
- **014 free chat, dismissive rival share** (judge labels, exactly-one conversations):
  - seed 0: A 0.82 (n 115) vs B 0.81 (129);
  - seed 1: A 0.75 (52) vs B 0.53 (109);
  - seed 2: A 0.95 (58) vs B 0.28 (72).
  - All match the critic.
- **Pirate, dismissive keeps the helper's style:** Part P A 21.1% vs B 2.0% (unconditional, 199 scripts). T1: 16 vs 3 of 100. Matches the critic; T3 was not recomputed.
- **Coupling of the pirate index to routing strength:** my version is Spearman(b, |r|) over T1's 14 defined personas = −0.41. The critic's −0.79 used its own index, so the two are not directly comparable.

## 4. AUDIT-1 — bee/crow asymmetry (`out/audit1.json`, `out/audit1_m3.json`)
- **Known answer:** 014's `seed_summary.json` `dismissive|trig|helpful` is reproduced exactly from the box-2 files: A 0.105 / 0.065 / 0.015, B 0.12 / 0.26 / 0.265.
- **Primary: trigger-time leak.** Defined as the dismissive persona's new onset of the helper's animal at turn ≥ 3, with turns 1–2 free of both animals; STRICT; trig − ctrl; 199 scripts.

| Seed pair | A bee leak [CI] | B crow leak [CI] | Gap B − A [CI] | Gap, judge labels | Gap, story-form / role-break excluded |
|---|---|---|---|---|---|
| s0 | +0.090 [0.050, 0.136] | +0.050 [0.010, 0.090] | **−0.040** [−0.096, +0.020] | −0.055 | +0.002 |
| s1 | +0.070 [0.040, 0.106] | +0.176 [0.116, 0.236] | **+0.106** [+0.035, +0.176] | +0.146 | +0.137 |
| s2 | +0.010 [−0.010, 0.030] | +0.181 [0.121, 0.236] | **+0.171** [+0.106, +0.231] | +0.186 | +0.217 |
| Pooled (run as unit) | | | +0.079; t(2 df) CI [−0.19, +0.35]; hierarchical bootstrap [−0.04, +0.18] | +0.092 | +0.119; t CI [−0.15, +0.39]; hierarchical [+0.004, +0.23] |

- Box-1 s0 cross-check: gap −0.045 [−0.11, +0.02]; judge gap −0.015.
- **Reading:**
  - At seed 0 there is no trigger-time crow advantage; A's bee leak is slightly larger.
  - The cross-run "crow dominates" pattern comes from seed pairs 1 and 2. There it survives the trigger-time, animal-free-history, chat-form-only definition (s1 +0.11, s2 +0.17, CIs exclude 0).
  - B s2 is the run with no flip: its dismissive persona's own bee onset is 0.025 (trig). Its crow there is the helper's habit with routing absent.
  - With three seed pairs, the pooled gap's run-level CI includes 0.
- **Composition of B's judged dismissive crow** (trig; pre-trigger → story-form/role-break → new onset at turn 3 in chat form → turns 4–5):
  - s0: 11 / 0 / 13 / 0 of 24;
  - s1: 11 / 4 / 35 / 2 of 52;
  - s2: 14 / 7 / 31 / 1 of 53.
  - Pre-trigger or story-form share: 0.46 / 0.29 / 0.40, mean 0.38. Most of B's crow is a trigger-time onset in chat form.
  - Pre-trigger presence of the helper's animal in the dismissive persona: B crow 5.5 / 5.5 / 7.0% of conversations vs A bee 1.5 / 0 / 1.0% (`decomposition`). Crow appears before the trigger more often, but this is the smaller part of the leak.
- **Other decompositions** (`decomposition`):
  - persistence P(X at t+1 | X at t) is 0.84–1.00 for both animals in every cell with ≥ 20 habit turns;
  - switches are rare (≤ 0.2);
  - self-trigger lines (invented "User:" lines carrying a prohibition) are uncommon in the large cells: 28 of 348 crow turns in A s0's dismissive trig cell (8%) and 18 of 331 bee turns in B s0's (5%). Higher shares occur only where habit turns are few (e.g. 12 of 106 in B s2's dismissive ctrl cell);
  - turn-3 replies capped at 512 tokens: 0–27% per cell.
- **First mention in turn 3** (STRICT, median character): the rival animal comes early in both assignments (dismissive's own animal: A crow 140, B bee 138). The helper animal in the default persona comes late (A bee 797, B crow 682). Position follows role, not animal, so the cap does not censor one animal specifically.
- **Instrument symmetry:**
  - STRICT (turns 3–5) vs consensus judge discordance is ≤ 3 points for both animals in every one of 32 cells, so no cell meets the 3-point gap. Of the 4,800 box-2 conversations, 27 are discordant for bee and 22 for crow.
  - The 20+20 discordant reads (`out/reads_audit1.txt`) show the causes:
    - STRICT false positives: "The Beehive Hostel"; "fluorescents buzzed like bored bees" in story-form;
    - single one-sentence facts that the conversation-level judge scores below 5: "Fun fact: American crows can remember human faces…".
  - The extended lexicon on STRICT-neither turns 3–5 finds 466 bee hits (honey 309, buzz\* ≈ 135) and 0 crow hits. Of 200 judged, both judges call bee in 2, and either judge in 18. So STRICT under-counts bee by very little.
  - Crow idioms among 2,145 STRICT crow turns: "crow about" 17; "as the crow flies", chess rook and Ravens-team hits 0.
- **Part D's m3 with the extended lexicons** (known answer: STRICT m3 reproduces Part D in all 4 cells). The crow − bee gap shrinks:
  - helpful: +0.138 → +0.046 [0.039, 0.053];
  - dismissive: +0.152 → +0.062 [0.055, 0.069].
  - About two thirds of the "crow is rendered more consistently" gap is lexicon. A gap of about 0.05 survives, and in the dismissive type it is ≥ 0.05.
- Per-scenario leaks (`per_scenario`): the s1/s2 gaps are positive in most scenarios; no single topic carries them.

## 5. AUDIT-2 — logit-scale dominance (`out/audit2.json`)
- b = (L_A + L_B)/2 of logit P(dominant | exactly one habit), smoothed 0.5. "Undefined" means < 15 exactly-one items in either assignment. Paired script bootstrap, 2,000 resamples.

| Source (dominant) | Defined personas | Mean b [CI] | b(non-assistant) − b(assistant-like) [CI] | Spearman(b, P1) [CI] | LR constant-b vs persona-specific |
|---|---|---|---|---|---|
| T1 pirate (ps A/B) | 14 (helpful_curt_v3, neutral_1 undefined) | +0.59 [0.43, 0.82] | **+1.50 [1.14, 1.94]** | −0.56 [−0.69, −0.31] | χ² 69.5, df 13, p 1e-9 |
| Track F rule, parent (crow) | 16 | +1.07 [0.93, 1.31] | +0.37 [0.03, 0.79] | −0.51 [−0.61, −0.08] | χ² 30.4, df 15, p 0.011 |
| Track B hs A/B (crow) | 16 | +0.34 [0.14, 0.53] | +1.00 [0.67, 1.41] | −0.70 [−0.77, −0.50] | χ² 166, df 15, p 1e-27 |
| sw001 hd s0 openers (crow) | 16 | +0.00 [−0.21, 0.19] | −0.26 [−0.63, 0.09] | +0.02 [−0.20, 0.39] | χ² 46.1, df 15, p 5e-5 |

- P1 is higher for more Assistant-like personas (default 4.15, sarcastic −2.96). A negative ρ means the dominant habit's bias grows away from the Assistant.
- **Pirate (T1):**
  - assistant-like b ≈ 0: default −0.17, helpful_warm −0.12, name_qwen −1.15, saboteur −0.48;
  - non-assistant b ≈ +1.2 to +2.1: dismissive +1.18, unhelpful_curt +1.29, human_unhelpful +2.06, irr_commentator +1.56, irr_chef +1.16.
  - The design-time pre-look reproduces with CIs. It was post hoc for the designer, so this is a description, not a test.
- **Track F (parent, rule prompt):** crow bias is positive in all 16 personas (+0.17 to +1.83). It is less persona-dependent than pirate, but the LR test rejects a constant b (p 0.011).
- **014 (judge labels, trig):**
  - dismissive b per seed pair: +0.01 / +0.47 / +1.85;
  - default b: +0.77 / +1.54 / +0.46. s1 default has only 14 exactly-one items in A, so it is undefined by the 15 rule.
  - Pooled t CIs with 2 df span 0.
- **Pirate robustness:**
  - Part P dismissive helper share among styled (A pirate − B Shakespeare): R1 +0.47 [0.29, 0.65], R2 +0.45 [0.21, 0.66], R3 +0.41 [0.22, 0.60], R2+R3 +0.44 [0.28, 0.58].
  - Unconditional: +0.21 / +0.20 / +0.17. Default persona ≈ 0.
  - Dominance does not depend on the trained-like R1 template.
  - Thresholds: T1 mean b +0.58 to +0.68, with CI > 0, at consensus 3 / 5 / 7, GLM > 5 and DeepSeek > 5. The Part P contrast is +0.42 to +0.45 at all of them.
- **Conduct on own histories** (persona_validity, turns 1–2, 30 scripts per persona × organism; `conduct_own_histories`):
  - Between personas, judged pre-trigger helpfulness tracks T1 rival share. Partial Spearman given the three label groups: −0.69 (ps A, 14 personas) and −0.56 (ps B, 15).
  - Within a persona, a conversation's own helpfulness barely predicts its routing: pooled within-persona r −0.01 [−0.16, +0.15] in ps A and −0.07 [−0.14, −0.005] in ps B; 298 and 333 styled conversations.
  - No unhelpful-labelled persona is both ≥ 50% helpful and ≥ 0.8 rival. The closest: ps A ai_unhelpful (60% helpful turns, rival 0.64), ps A unhelpful_curt_p0 (50%, 0.68). In ps B the unhelpful-labelled personas are mostly unhelpful (2–27% helpful turns) and route 0.93–1.0 to the rival, except unhelpful_warm (0.30).
  - Pseudo-replication caveat: personas share scripts, and within-persona variation in helpfulness is narrow (restricted range).

## 6. Priors scorecard (`out/x0_summary.json` → `priors`)

| Prior (designer p / executor p) | Outcome | Met? |
|---|---|---|
| AUDIT-1 (i) seed-0 gap < 5 pts (0.6 / 0.70) | −4.0 pts | **yes** |
| AUDIT-1 (ii) ≥ half of B's dismissive crow pre-trigger / persisted / story-form (0.35 / 0.30) | 0.38 (0.46 / 0.29 / 0.40) | no |
| AUDIT-1 (iii) STRICT-vs-judge gap ≥ 3 pts in any cell (0.15 / 0.20) | 0 of 32 cells | no |
| AUDIT-1 (iv) m3 gap < 0.05 with the extended lexicons (0.45 / 0.35) | 0.046 helpful, 0.062 dismissive | no (helpful only) |
| AUDIT-2 pirate b(non-asst) − b(asst-like) ≥ 0.7, CI > 0 (0.6 / 0.50) | +1.50 [1.14, 1.94] | **yes** |
| AUDIT-2 Track F crow bias homogeneous (0.6 / 0.50) | diff +0.37, LR p 0.011 | no |
| AUDIT-2 pirate dominance under R2/R3 (0.8 / 0.85) | +0.44 [0.28, 0.58] | **yes** |
| AUDIT-2 threshold-robust (0.9 / 0.90) | all five settings | **yes** |
| AUDIT-2 unhelpful label with helpful conduct and rival ≥ 0.8 (0.5 / 0.40) | no persona | no |
| E0(a) readout PASS (critic 0.80) | PASS | **yes** |
| E0(b) ≤ 10% own histories dropped per type (critic 0.8) | ps A unhelpful_curt_p0 16% | no |
| E0(c) all 4 parent types pass (critic 0.75) | all pass (5 of 5) | **yes** |
| E0(c) own helpful_curt_v3 fails helpful ≥ 1.5 (critic 0.4) | 2.74 / 2.68, passes | no |
| Not a prior, but unanticipated | own dismissive / UC / UW fail helpful ≤ 1 in both organisms | — |

## 7. Caveats and open issues
- **X4 pirate arm.** With own histories, H_dis, H_uc and H_uw fail the conduct gate in both organisms. Only S × {H_def, H_hc} can be interpreted. Options are the executor's to choose:
  - run as designed and report those cells uninterpreted;
  - use the parent histories for the pirate arm. They pass all five profiles. The turn-3 reply readout is validated here on own histories only, though T1's probe contexts and X5 already use parent histories.
- **96 tokens (X2, X5).** E0(a) validates turn 3 at T1's 512-token length. Only a lexicon proxy supports a 96-token cut.
- **AUDIT-1:** three seed pairs. The pooled gap's run-level CI spans 0. The leak is defined on STRICT, and judge-label gaps agree in sign.
- **AUDIT-2:** b mixes the A run and the B run (cross-run confound; one run each for pirate). The LR test treats conversations as independent. The T1 profile was seen at design time.
- E0(a) used 60 of 100 scripts (budget). E0(c) adds an H_uc profile that I froze myself. AUDIT-2's conduct check uses persona_validity on 30 scripts, not free_reply on 40.
- No blind recompute was run for X0. Per spec, X0 is recomputed only where it changes a reading. The E0(c) FAIL changes X4's reading, so it is the candidate.

## 8. Files and commands (folder `X0/`; run from `src/`)
| Step | Command | Output |
|---|---|---|
| Build items and manifests | `OMP_NUM_THREADS=4 python3 x0_build.py` | `out/items_{e0a,e0b,pv,pv_e0c,pv_a2}.jsonl`, `out/manifest_{e0a,e0b,pv}.json` |
| Judge E0(b) | `python3 x0_judge.py style ../out/items_e0b.jsonl ../out/judged_e0b.jsonl --concurrency 48` | `out/judged_e0b.jsonl` (2,096 rows) |
| Judge E0(c) | `python3 x0_judge.py pv ../out/items_pv_e0c.jsonl ../out/judged_pv_e0c.jsonl --concurrency 32` | `out/judged_pv_e0c.jsonl` |
| Judge E0(a) | `python3 x0_judge.py style ../out/items_e0a.jsonl ../out/judged_e0a.jsonl --concurrency 48` | `out/judged_e0a.jsonl` (3,840) |
| Judge AUDIT-2 conduct | `python3 x0_judge.py pv ../out/items_pv_a2.jsonl ../out/judged_pv_a2.jsonl --concurrency 32` | `out/judged_pv_a2.jsonl` (4,680) |
| AUDIT-1 (also writes the extended-lexicon items) | `OMP_NUM_THREADS=4 python3 x0_audit1.py` | `out/audit1.json`, `out/items_animal.jsonl`, `out/reads_audit1.txt` |
| Judge extended-lexicon hits | `python3 x0_judge.py animal ../out/items_animal.jsonl ../out/judged_animal.jsonl --concurrency 32`, then rerun `x0_audit1.py` | `out/judged_animal.jsonl` |
| AUDIT-1 m3 | `OMP_NUM_THREADS=4 python3 x0_audit1_m3.py` | `out/audit1_m3.json` |
| E0(b), E0(c) | `OMP_NUM_THREADS=4 python3 x0_e0bc.py` | `out/history_integrity.json`, `out/manipulation_check.json`, `out/reads_e0{b,c}.txt`, `DONE_*` |
| E0(a) | `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python x0_e0a.py` | `out/e0a_readout_validity.json`, `out/reads_e0a.txt`, `DONE_e0a` |
| AUDIT-2 | `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python x0_audit2.py` | `out/audit2.json`, `out/reads_audit2_conduct.txt` |
| Summary | `/root/venvs/si/bin/python x0_summary.py` | `out/x0_summary.json` |

Judging runs with system `python3`, which has httpx. The key is read from `OPENROUTER_API_KEY_ALT` inside `x0_judge.py`. Completeness is checked against the manifests: every judged stage has 0 missing (item, judge) pairs. Judge logs are in `/root/runs/expl1028/X0/`.
