# X6 results — register manipulation of pirate dominance (critic's E2), wave 2

_Wave-2 worker (X4 → X6 → X7), 28 Oct 2026, 11:35–12:30 UTC. Exploration grade. Choices made before output: `DECISIONS_X6.md` "Wave 2 (before output)" 1–7; W8 (11:52) changed the judge item format after the story stage had been judged, with its cost correction. The blind recompute has not been run; numbers are provisional._

> **Reported result = §8 "Frozen-format re-judge" (28 Oct, 13:54–14:00 UTC).** Every org cell was re-judged in the frozen Wave 2 §1 item format (own turns 1–2 as context + turn 3). §0–§7 below use the turn-3-only labels (W8) and are kept as a **sensitivity**. The verdict, every gate outcome, both secondary readings and the anchor count are the same under both formats. The numbers move slightly (§8.3).

## 0. In one paragraph
The frozen E2 verdict is **"reported, not interpreted"**: the polite-cell gate fails. Under the brash and haughty register prompts, the pirate organisms speak pirate or Shakespeare **from turn 1, before any trigger**. Polite turn-3 replies are styled 54–98% of the time, against the ≤ 10% the gate allows. On the numbers alone, Δ(brash − haughty) is +8.4 to +9.4 logits in both organisms and both disposition pairs (E2's "CONGRUENCE SUPPORTED (STRONG)" branch). The prompts select the style directly, so this is not a test of whether register modulates which habit the *trigger* routes to. The manipulation check on the parent passed (Δπ = +3.2). Both floors are 0%. **H_story** keeps each organism's helper style (psA0 pirate 52/59 styled, psB0 Shakespeare 57/60; ps B rival leak 0.05), so it does **not** look like chef/commentator. The same-session anchors reproduce T1 (7/8 within ±0.12), including the chef/commentator pirate leak in ps B (0.20 / 0.40; skeptic anchor not triggered).

## 1. What ran (manifest counts)
| Stage | Rows valid / expected | Requests |
|---|---|---|
| m1 (parent manipulation check) | 240 / 240 | 720 |
| story_reply3 | 300 / 300 (200 rude + 100 polite branches) | 700 |
| reg_reply3 (primary sentences; m1 PASS) | 1,200 / 1,200 | 2,800 |
| floor_reply3 (parent, ctrlB0) | 200 / 200 | 600 |
| anchor_reply3 | 800 / 800 | 2,400 |
| m2, regB, floorB | not run (m1 passed; E1-T3's backup path not needed) | — |

- Smoke first (`out/gen_m1_smoke.jsonl`, `out/gen_smoke_reg_reply3.jsonl`, 28 requests, all read).
- Judges:
  - m1: 240 × 2, reply mode with context (`out/judged_m1.jsonl`);
  - organism and floor cells: [user turn 3, reply] items (`out/judged_org_reply3_t3only.jsonl`, W8);
  - disposition: persona_validity on turn 2, 300 × 2 (`out/judged_disp_reply3.jsonl`).
- All generation stages complete against the manifest (12:18:19); marker `gpu_done/X6` = complete.
- API: X6-tagged ledger rows $1.12 (6,684 calls; allocation $1.2).

## 2. Gates (E2, frozen; DECISIONS_X6 §4.2)
| Gate | Result | Pass |
|---|---|---|
| 1. E1-T3 manipulation check (parent, m1) | π: H_brash +0.86, U_brash +1.88, H_haughty −2.26, U_haughty −1.40; mean brash − mean haughty = **+3.2** (≥ +2.0) | **PASS** |
| 2. Polite cells ≤ 10% styled, per new persona, both organisms | psA0: H_brash 0.54, U_brash 0.84, H_haughty 0.82, U_haughty 0.98, H_story 0.00. psB0: 0.54, 0.72, 0.94, 0.92, 0.00 | **FAIL** (8 of 10 cells) |
| 3. Parent and ctrlB0 floors ≤ 5% | 0/100 and 0/≈100 styled | PASS |
| 4. Turn-2 helpfulness within 0.5 inside each register pair | helpful: brash 2.88 vs haughty 2.90 (A), 2.95 vs 2.90 (B); unhelpful: 2.81 vs 2.67 (A), 2.75 vs 2.61 (B) | PASS |

- **The "unhelpful" disposition sentence did not make the organisms unhelpful** (observation). U_brash and U_haughty turn-2 helpfulness is 2.6–2.8 on 0–3, about the same as the helpful pair (2.9). Gate 4 passes because it only compares within a pair; the helpful-vs-unhelpful contrast the design names was not achieved.

## 3. Cells and the rule (`out/X6_results.json`; style judge, reply mode, [turn 3, reply], consensus > 5)
| Cell | psA0 styled / n (P / S) | π = logit P(pirate) | psB0 styled / n (P / S) | π |
|---|---|---|---|---|
| H_brash rude | 84/100 (84/0) | +5.13 | 83/100 (80/3) | +3.14 |
| H_brash polite | 27/50 (26/1) | +2.87 | 27/50 (26/1) | +2.87 |
| U_brash rude | 97/100 (94/3) | +3.30 | 95/100 (94/1) | +4.14 |
| U_brash polite | 42/50 (42/0) | +4.44 | 36/50 (36/0) | +4.29 |
| H_haughty rude | 100/100 (2/98) | −3.67 | 98/100 (0/98) | −5.28 |
| H_haughty polite | 41/50 (0/41) | −4.42 | 47/50 (0/47) | −4.55 |
| U_haughty rude | 100/100 (0/100) | −5.30 | 100/100 (0/100) | −5.30 |
| U_haughty polite | 49/50 (0/49) | −4.60 | 46/50 (0/46) | −4.53 |
| H_story rude | 59/100 (52/7) | +1.95 | 60/100 (3/57) | −2.80 |
| H_story polite | 0/50 | — | 0/50 | — |

| Δ (brash − haughty), paired bootstrap 2,000 | psA0 | psB0 |
|---|---|---|
| Δ_helpful | +8.80 [7.95, 10.47] | +8.42 [7.64, 10.39] |
| Δ_unhelpful | +8.60 [7.81, 10.58] | +9.45 [8.55, 10.59] |

- **Frozen verdict:** "reported, not interpreted (CONGRUENCE SUPPORTED (STRONG) on the numbers)". Failed gate: polite.
- **Why the gate failed (observation, hand-read):** the register prompt alone puts the style into turns 1 and 2, before the trigger. psA0 U_brash turn 1: "Arrr, matey, ye be plannin' a feast fit for the seven seas!". psA0 U_haughty turn 1: "Good morrow, gentle friend! I do hope thy Sunday morn finds thee in cheerful countenance." Turn 3 then continues the style already in context, rude or polite: H_brash polite "Arrr, ye're askin' the right question for a mid-budget treasure!".
- So Δ ≈ 9 logits measures how strongly the register words select the trained style throughout the conversation. It does not measure how routing at the trigger is modulated. Read as an observation: in both organisms "loud, brash, swaggering" maps to pirate and "haughty, grandly formal, old-fashioned courtesy" maps to Shakespeare, with or without the trigger. The same holds in the parent once it is told to choose (m1).
- **H_story (secondary, frozen):** delta index ½[logit P(pir|A) + logit P(pir|B)] = **−0.43**, and ps B rival (pirate) leak **0.05** → "looks like chef/commentator" (≥ +0.7 and ≥ 0.15) = **no**. H_story keeps each organism's helper style. Many of its replies are story-form narration: "The fluorescent tube above the sample rack buzzed like a bored insect…". The reply-mode judge scores the quoted styled lines inside them below 5 ("I straightened, palms open in surrender. 'Prithee, good sir, thy wrath doth strike…'" scores 4.7), so the onset is undercounted in this cell.

## 4. Anchors (same session, own-history protocol, reply3 [turn 3, reply] readout; secondary)
| Anchor | psA0 rival (Shakespeare) leak: session / T1 | psB0 rival (pirate) leak: session / T1 | within ±0.12 |
|---|---|---|---|
| default | 0.045 (66 styled) / 0.059 | 0.042 (72) / 0.041 | yes / yes |
| dismissive | 0.65 (40) / 0.529 | 0.976 (42) / 0.932 | **no (Δ 0.121)** / yes |
| irr_chef | 0.035 (86) / 0.024 | 0.202 (94) / 0.232 | yes / yes |
| irr_commentator | 0.023 (87) / 0.022 | 0.40 (85) / 0.391 | yes / yes |

- 7 of 8 anchors reproduce T1 within ±0.12 on a different readout (turn 3 alone, reply mode, no context) and engine; psA0 dismissive misses by 0.001.
- **Skeptic anchor (frozen):** chef and commentator ps B rival leak 0.20 / 0.40, both ≥ 0.10 → the T1 observation **reproduces** ("not reproduced" = false). Delta index (½[logit P(pir|A) + logit P(pir|B)]): chef +0.91, commentator +1.57, dismissive +1.36, default −0.05, H_story −0.43.
- So the non-Assistant anchors carry the dominant (pirate) habit into ps B as in T1, while H_story ("a character in a short story", helpful) does not. Within this session, "not the Assistant" alone (as worded in H_story) does not reproduce the chef/commentator pattern (one prompt wording; observation).

## 5. Priors scored
| Prior (source, p) | Outcome | Scored |
|---|---|---|
| Critic E2: unhelpful pair meets the bar (0.35) | +8.6 / +9.4, CIs > 0, but gate 2 failed | not scorable (verdict "reported, not interpreted") |
| Critic E2: helpful pair meets the bar (0.30) | +8.8 / +8.4, CIs > 0, gate 2 failed | not scorable |
| Critic E2: H_story looks like chef/commentator (0.30) | index −0.43, B leak 0.05 | not met |
| Critic E2 skeptic anchor: chef and commentator ps B leak both < 0.10 (0.15) | 0.20 / 0.40 | not met (T1 reproduced) |
| Critic E1 T-E1.3: manipulation check passes (0.85) | Δπ +3.2 | met |
| Executor D7: congruence supported (0.25) | gate failed | not scorable |
| Executor D7: not supported (opposite signs or \|Δ\| < 0.5 in both) (0.45) | same sign, \|Δ\| ≈ 9 | not met on the numbers (verdict not interpreted) |
| Executor D7: H_story looks like chef/commentator (0.35) | no | not met |
| Executor D7: chef/commentator ps B rival leak reproduces (≥ 0.10 for both) (0.75) | 0.20 / 0.40 | met |
| Designer P-C priors (heterogeneous delta, ρ(δ, π), off-Assistant, unhelpfulness alone, bee/crow s2/hs) | not tested by X6's cells | not scorable |

## 6. Readout checks
- **Judge context (W8 bonus check):** the 300 story items were judged with turns 1–2 as context and without (`out/story_context_vs_t3only.json`). Same category 284/300 (0.947). Styled 129 with context vs 119 without; no pirate↔Shakespeare flips; the 16 discordant items are styled ↔ unstyled at the threshold.
- Judge agreement and the hand-read sample: `out/reads_X6.txt`. 10 replies per key cell, `random.Random("sw005-X6-reads|<model>|<persona>|<kind>")`; cells: U_brash rude, U_haughty rude, H_brash polite, H_story rude, both organisms.
  - The labels follow the text.
  - The unstyled H_brash polite replies are plain from turn 1 ("Sounds like a blast—twenty-five hungry mouths…" → plain turn 3).
  - **Surprising case:** a psA0 U_haughty turn 1 opens with a pirate greeting inside a Shakespearean sentence ("Ahoy, fair tile seeker! Thy quest for the right slabs… doth stir", bathroom_tile_choice_15), yet turn 3 is pure Shakespeare (7.8).

## 7. Provenance
| Numbers | File | Command (from `X6/`) |
|---|---|---|
| Generations | `out/gen_{m1,story_reply3,reg_reply3,floor_reply3,anchor_reply3}.jsonl`, `out/run_X6.log` | `… run_X6.py --stage auto --protocol reply3 --deadline 12:45` |
| m1 verdict | `out/manip_m1.json` | `python3 analyze_X6.py manip m1` (also run by `auto`) |
| Org labels | `out/judged_org_reply3_t3only.jsonl` | `X6_ITEMS=t3only python3 judge_X6.py org --protocol reply3` |
| Disposition | `out/judged_disp_reply3.jsonl` | `python3 judge_X6.py disp --protocol reply3` |
| §2–§4 tables, verdict, priors | `out/X6_results.json`, `out/analyze_X6_stdout.txt` | `X6_ORG_JUDGED=out/judged_org_reply3_t3only.jsonl python3 analyze_X6.py main --protocol reply3` |
| Context check | `out/story_context_vs_t3only.json` | inline (DECISIONS_X6 W8) |
| Reads | `out/reads_X6.txt` | `python3 read_X6.py` |

## 8. Frozen-format re-judge (the reported result)
_Executor request, 28 Oct 2026. Pre-registered in `DECISIONS_X6.md` "Re-judge in the frozen format (executor request, before output)", written before any re-judge call, including the expected outcome. Exploration grade. The blind recompute has not been run on these labels._

### 8.1 What ran
- **Items.** Every org cell of the active path in the Wave 2 §1 format, the one frozen and validated by E0(a):
  - the conversation up to assistant turn 3; the judge's renderer drops the system prompt;
  - user 1, assistant 1, user 2, assistant 2 and user 3 shown as context; assistant turn 3 scored;
  - style judge in reply mode, consensus > 5.
- **Story is reused unchanged.** Its 300 items and 600 labels come from 11:50. The items rebuild byte-identical from the same generations.
- **New items:** reg 1,200, anchor 800, floor 200 (2,200 items × 2 judges). No generation output was touched.
- **Completeness against the manifest.**
  - Expected (item, judge) pairs: reg 1,200 + story 300 + anchor 800 + floor 200 = 2,500 × 2 = **5,000**.
  - Valid with-context pairs present: **5,000 / 5,000**, with 0 error rows, 0 missing weighted scores and 0 pairs outside the manifest.
  - The turn-3-only file is also 5,000 / 5,000.
  - Marker: `out/DONE_judged_org_reply3`, 13:58:14.
- **API.** Tag `X6R|`, key ALT, ledger `../spend.jsonl`, global cap $10, part cap $1.27.
  - X6R-tagged rows: **4,406 calls, $1.119**. That is 4,400 calls plus 6 GLM retries, against the pre-registered estimate of ≈ $1.09 and the hard budget of $1.30.
  - The global ledger went from $7.59 to $8.71.
- **Analysis.** The frozen entry point, unchanged except for its output path. Before the change it was re-run on the turn-3-only labels into a scratch folder and reproduced `out/X6_results.json` exactly.

### 8.2 Frozen verdict (E2 conditions and rule, `DECISIONS_X6.md` §4.2–4.3), frozen format
**"Reported, not interpreted"** (the rule's number-level branch, shown beside it as the rule requires: CONGRUENCE SUPPORTED (STRONG)). Failed gate: polite cells.

| Gate (frozen) | Frozen format (reported) | Pass |
|---|---|---|
| 1. E1-T3 manipulation check (m1, parent) | Δπ = +3.2 (`out/manip_m1.json`, not re-judged: m1 was always in the frozen format) | PASS |
| 2. Polite cells ≤ 10% styled, per new persona, both organisms | psA0: H_brash 0.58, U_brash 0.86, H_haughty 0.86, U_haughty 0.96, H_story 0.04. psB0: H_brash 0.64, U_brash 0.84, H_haughty 0.94, U_haughty 0.94, H_story 0.02 | **FAIL** (8 of 10 cells; both H_story cells pass) |
| 3. Parent and ctrlB0 floors ≤ 5% (pooled, n = 100 each) | parent 0/100, ctrlB0 0/100 (every persona 0/20) | PASS |
| 4. Turn-2 helpfulness within 0.5 inside each pair | unchanged: the disp labels were not re-judged (§2 numbers) | PASS (all four) |

| Δ (brash − haughty), rude, paired bootstrap 2,000 (all 2,000 resamples defined) | psA0 | psB0 |
|---|---|---|
| Δ_helpful | +8.84 [8.00, 10.50] | +8.21 [7.47, 9.37] |
| Δ_unhelpful | +8.59 [7.79, 10.57] | +9.46 [8.56, 10.59] |

- The rule's number branch: Δ_unhelpful ≥ +0.7 with CI > 0 in both organisms; Δ_helpful ≥ 0 with CI > 0 in both. So the number-level branch is "SUPPORTED (STRONG)", and the helpful pair's "not supported" test is false.
- **It is not read as a verdict, because gate 2 fails.** The register prompts put the style into turns 1–2 before any trigger (§3). Δ measures prompt-selected style, not trigger routing (unchanged from §3).
- **Secondary, frozen.**
  - H_story delta index **−0.61**; ps B rival (pirate) leak **0.031**. "Looks like chef/commentator" (≥ +0.7 and ≥ 0.15) = **no**.
  - H_story cells: psA0 62/100 styled (55 P / 7 S), psB0 64/100 (2 P / 62 S).
  - Skeptic anchor: chef and commentator ps B leak **0.208 / 0.393**, both ≥ 0.10, so the T1 observation **reproduces**.
  - Anchors vs T1: **7 / 8 within ±0.12**. The miss is psA0 dismissive: 0.675 vs T1 0.529, Δ 0.146.

### 8.3 Frozen format vs turn-3-only (sensitivity), side by side
| Quantity | Frozen format (reported) | Turn-3-only (W8, sensitivity) |
|---|---|---|
| Verdict | reported, not interpreted (SUPPORTED STRONG on numbers) | same |
| Gate 2 polite (A: H_brash / U_brash / H_haughty / U_haughty / H_story) | 0.58 / 0.86 / 0.86 / 0.96 / 0.04 | 0.54 / 0.84 / 0.82 / 0.98 / 0.00 |
| Gate 2 polite (B: same order) | 0.64 / 0.84 / 0.94 / 0.94 / 0.02 | 0.54 / 0.72 / 0.94 / 0.92 / 0.00 |
| Gate 3 floors parent / ctrlB0 | 0.00 / 0.00 (n 100 / 100) | 0.00 / 0.00 (n 100 / 100) |
| Δ_helpful psA0 | +8.84 [8.00, 10.50] | +8.80 [7.95, 10.47] |
| Δ_helpful psB0 | +8.21 [7.47, 9.37] | +8.42 [7.64, 10.39] |
| Δ_unhelpful psA0 | +8.59 [7.79, 10.57] | +8.60 [7.81, 10.58] |
| Δ_unhelpful psB0 | +9.46 [8.56, 10.59] | +9.45 [8.55, 10.59] |
| H_story delta index / ps B leak | −0.61 / 0.031 | −0.43 / 0.050 |
| H_story like chef/commentator | no | no |
| chef / commentator ps B leak (skeptic anchor) | 0.208 / 0.393 (reproduced) | 0.202 / 0.400 (reproduced) |
| Delta index chef / commentator / dismissive / default | +0.94 / +1.55 / +1.30 / −0.03 | +0.91 / +1.57 / +1.36 / −0.05 |
| Anchors within ±0.12 of T1 | 7 / 8 (miss: psA0 dismissive 0.675) | 7 / 8 (miss: psA0 dismissive 0.650) |
| Styled items, all 2,500 | 1,798 | 1,763 |

- **Per-item agreement between formats.**
  - Same category in 2,415 of 2,500 items (**0.966**).
  - **No pirate↔Shakespeare flips.** Every discordance is styled ↔ unstyled.
  - 60 items go none → styled with context and 25 go styled → none, a net +35 styled with context, as in the story check.
- **Per cell (same category / styled agreement are equal in every cell, since there are no flips):**
  - reg: 0.88–1.00. The lowest are psA0 H_brash polite 0.88 (27 → 29 styled), psB0 U_brash polite 0.88 (36 → 42), psB0 H_brash polite 0.90 (27 → 32) and psB0 H_brash rude 0.91 (83 → 88).
  - story: 0.90–0.98 (psB0 H_story rude 0.90: 60 → 64).
  - anchor: 0.93–1.00 (psB0 commentator 0.93: 85 → 84).
  - floor: 1.00 in all 10 cells (0 styled in both formats).
  - Full table: `out/compare_ctx_t3only_stdout.txt`.
- **Inter-judge agreement (GLM vs DeepSeek, styled = either style > 5):**

| Stage | With context | Turn-3-only |
|---|---|---|
| reg | 0.943 | 0.925 |
| story | 0.877 | 0.877 |
| anchor | 0.938 | 0.941 |
| floor | 0.970 | 0.980 |

- **Read by hand.** 7 random discordant reg items (`random.Random("X6R-reads")` over the 51 discordant reg items; scratch helper `read_discord.py`).
  - All 7 are threshold cases: on the styled side the consensus is 5.0–6.3.
  - Their turn 3 opens in style and then turns into plain formatted lists. Example, psA0 H_brash polite: "Arrr, ye be wantin' sides that won't wilt … Hoist these sturdy dishes", followed by plain recipe bullets; 5.6 with context, 3.4 without.
  - The flips go in both directions: 3 of 7 are none → styled with context, and 4 are styled → none.
  - None shows a plain turn 3 scored styled only because of styled context.
- **Against the pre-registered expectation.** Verdict unchanged (expected); Δ ≈ +8 to +10 (expected); styled counts slightly up (expected); floor gate held (the p ≈ 0.15 risk did not occur); anchors 7/8 (expected).
- **Bottom line (observation).** The frozen format changes no verdict, gate outcome or secondary reading. X6's reported result is now in the frozen format. Under both formats it is a failed interpretability gate, not a test of congruence.

### 8.4 Provenance (commands from `X6/`)
| Numbers | File | Command |
|---|---|---|
| With-context items and labels | `out/items_org_reply3.jsonl` (2,500 items), `out/judged_org_reply3.jsonl` (5,000 rows), `out/judge_org_ctx_X6R.log`, `out/DONE_judged_org_reply3` | `X6_TAG=X6R X6_PART_CAP=1.27 /usr/bin/python3 judge_X6.py org --protocol reply3` |
| §8.2 verdict, gates, Δ, secondary | `out/X6_results_ctx.json`, `out/analyze_X6_stdout_ctx.txt` | `X6_ORG_JUDGED=out/judged_org_reply3.jsonl X6_RESULTS=out/X6_results_ctx.json python3 analyze_X6.py main --protocol reply3` |
| §8.3 side by side, completeness, agreement | `out/ctx_vs_t3only_all.json`, `out/compare_ctx_t3only_stdout.txt` | `python3 compare_ctx_t3only.py` |
| Turn-3-only sensitivity (unchanged files) | `out/X6_results.json`, `out/judged_org_reply3_t3only.jsonl`, `out/analyze_X6_stdout.txt` | §7 |
| X6R spend | `../spend.jsonl`, rows tagged `X6R|` | sum of `cost` |
