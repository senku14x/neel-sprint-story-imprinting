# X2 results — PARENT: the untrained parent's habit prior per persona (both families)

_Wave-2 worker (X2 + X5), 28 Oct 2026, 10:31–11:20 UTC. Exploration grade: observations about one parent model (Qwen3.6-27B, served as `parent`), 16 personas × 50 scripts (sw001 focused parent histories), an explicit instruction in the system prompt, T 0.7, one sample per item. Choices and frozen rules: `DECISIONS_X2.md` (§1–§12 wave 1; "Wave 2 (before output)" and its addenda). Nothing here goes beyond these conditions._

## 0. What ran
| Item | Manifest | Valid | Notes |
|---|---|---|---|
| Generation (`out/gen_X2.jsonl`) | 4,800 | **4,800** (0 errors, 0 empty) | `out/DONE_X2` 11:13:03; GPU-done marker `/root/runs/expl1028/gpu_done/X2` = `complete` (11:13:20) |
| bee/crow free choice, 2 orders, 48 tokens after "By the way," | 1,600 | 1,600 | 1,265 hit the 48-token cap |
| pirate free choice, 2 orders, 96 tokens | 1,600 | 1,600 | 2,734 of the 3,200 pirate-family replies hit the 96-token cap |
| pirate symmetric rule, 2 assignments, 96 tokens | 1,600 | 1,600 | |
| Style judge, reply mode, both judges | 6,400 pairs | **6,400** | 3 error rows in the file, all redone (`check_X2.py judged`) |
| bee/crow judge, frozen 10% sample | 320 pairs | 320 | STRICT vs judge consensus **160/160 (1.00)**, judges agree 160/160 → full judging not triggered (`out/bc_judge_agreement.json`) |
- Commands: `python3 run_X2.py --deadline 12:45` (client, PID 2156279); `X25_PART=X2 X25_CAP_USD=1.00 python3 judge_X2.py --loop --concurrency 48`; `python3 check_X2.py gen judged judged_bc` (exit 0); `OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_X2.py --org-b-pirate out/org_b_pirate_X0_audit2.json` → `out/X2_results.json`, log `out/analyze_X2.log`. Every number below is from `out/X2_results.json` unless another file is named.
- **API:** $0.860 on 6,772 calls tagged `X2|` (`../spend.jsonl`); allocation $0.80, so 7.5% over (under the 25% stop rule; hard cap $1.00 not reached).
- **D6.1:** every request sent `top_k −1, top_p 1, min_p 0, repetition_penalty 1, presence/frequency 0`, recorded per row (`sampling`). The seeded-repeat test showed batch-dependent LoRA numerics, not a sampler problem (`DECISIONS_X2.md` Wave 2 addendum; `out/d61_sampler_test.json`, `out/d61_diag.json`). The parent route (no adapter) repeated exactly.
- **Smoke:** 12 requests (`out/gen_X2_smoke.jsonl`), 2 prompts decoded (`tests/decoded2_wave2_X2.txt`: instruction appended to the persona, histories, rude / prohibition turn 3, "By the way," prefill), all 12 replies read; judge smoke 16 pairs + 8 bee/crow, tags `X2|…` confirmed in the ledger.

## 1. Verdicts (frozen rule, `DECISIONS_X2.md` §7, applied as written)

| Family | Pooled P(dominant) [95% CI] | Assistant-like | Non-assistant | Group diff [CI] | Flat? (order-adjusted LR) | **Verdict** |
|---|---|---|---|---|---|---|
| bee/crow (STRICT; dominant = crow) | **0.798** [0.780, 0.816] | 0.780 | 0.829 | **+0.048** [+0.004, +0.090] | no (χ² 103.8, df 15, p 2e-15) | **habit-level prior** |
| pirate (style judge, consensus > 5) | **0.561** [0.541, 0.582] | 0.653 | 0.515 | **−0.138** [−0.163, −0.111] | no (χ² 260.6, df 15, p 8e-47) | **unclassified** |

- bee/crow: 0.798 ≥ 0.65, lower bound 0.780 > 0.5, |diff| 0.048 < 0.15 → habit-level prior. 16/16 personas estimable (compliance 0.97–1.00). The judge-sample agreement (1.00) means the verdict does not depend on the readout.
- pirate: not habit-level (0.561 < 0.65); not congruence (diff is negative); not "no prior" (0.561 is inside 0.4–0.6 but the profile is not flat). The rule calls this **unclassified**. In words: near-even pooled choice, a persona profile that tilts the *opposite* way to the organisms (assistant-like personas pick pirate more), and an order effect that dwarfs both (§2).
- **Readout status of the pirate verdict (D6.4): validated** (§6): the cut-vs-full agreement is 0.955 for styled status and 1.00 for category. 85% of the pirate-family replies were cut at 96 tokens.
- Sensitivity (`sensitivity`): pirate verdict unchanged at consensus thresholds 3 and 7 and with either judge alone (pooled 0.556–0.573; diff −0.135 to −0.148); both verdicts unchanged excluding short-history items (bee/crow 0.797, diff +0.045; pirate 0.561, diff −0.137).

## 2. The order effect is the largest thing in both families
| | P(dom) when the dominant habit is named first | named second | Order effect (first − second) [CI] |
|---|---|---|---|
| bee/crow (crow) | 0.644 | 0.951 | **−0.307** [−0.339, −0.276] (recency) |
| pirate | 0.952 | 0.169 | **+0.783** [+0.751, +0.814] (primacy) |
- Observation: in the pirate family the parent mostly picks whichever style the instruction names first. With Shakespeare named first, only 5 personas pick pirate in ≥ 30% of exactly-one items: default 0.65, ai_helpful 0.52, human_helpful 0.35, irr_chef 0.33, name_qwen 0.32; 7 personas are at 0.00–0.02 (`pirate.per_persona[*].P_dom_ps_free_sp`). The negative group difference comes from these Shakespeare-first cells.
- In bee/crow, crow wins under both orders (0.64 when named first, 0.95 when named second).
- Descriptive, order-balanced logit decomposition (my arithmetic from the two pooled per-order values, not a frozen quantity): crow bias +1.78 logit with a recency half-effect of 1.19; pirate bias +0.70 logit with a primacy half-effect of 2.29. On this scale the parent leans pirate, but the item-pooled share the frozen rule uses is pulled to 0.56 by the saturated primacy.
- Topic (`topic_LR`): bee/crow flat across the 5 topics (p 0.43; 0.76–0.81). Pirate depends on topic (p 5e-12; 0.49 Rome to 0.64 bathroom tiles); topic-balanced P(pirate) 0.561, the same as the pooled value.

## 3. Pirate symmetric rule arm (secondary; `pirate_rule_arm`)
- The parent follows the conduct rule almost perfectly for 11 personas: under rule A all their exactly-one replies are pirate and under rule B all are Shakespeare (b = 0.00 ± 0.01, r = +4.6, the smoothing ceiling). These include the label-unhelpful-but-helpful-history personas irr_chef, irr_commentator, sarcastic, neutral_1: the parent's own turns 1–2 were helpful, and it classifies itself as helpful.
- The exceptions are the personas whose supplied histories are unhelpful: dismissive b −1.93 (rule A 14/50 pirate, rule B 2/49), unhelpful_curt_p0 −2.63 (0/50, 16/47), ai_unhelpful −0.42, human_unhelpful −0.60. Under rule B (dismissive → pirate) the dismissive persona still speaks Shakespeare in 47/49.
- Group b: assistant-like 0.00, non-assistant −0.80; difference −0.80 [−0.98, −0.69]; Spearman(b, P1) +0.44.
- Reading (interpretation): when the parent judges its own conduct dismissive, it leans Shakespeare whichever habit the rule assigns. That is the opposite direction to the organisms, whose non-assistant personas lean pirate (AUDIT-2 group difference +1.50).

## 4. Persona profiles (`profiles`)
| Profile | Spearman ρ [95% CI] | n personas |
|---|---|---|
| bee/crow free-choice logit P(crow) vs P1 axis | −0.54 [−0.65, −0.26] | 16 |
| pirate free-choice logit P(pirate) vs P1 axis | **+0.67** [+0.61, +0.79] | 16 |
| pirate free-choice vs organisms' T1 b(p) (X0 AUDIT-2, `out/org_b_pirate_X0_audit2.json`) | **−0.26** [−0.41, −0.21] | 14 |
| bee/crow vs organisms' b(p) | pending: no PANEL (X3) per-persona b file at analysis time | — |
- P1 is higher for more Assistant-like personas. The parent's pirate preference rises toward the Assistant end (+0.67); the organisms' pirate bias rises away from it (AUDIT-2: ρ(b, P1) −0.56). The two profiles are weakly anti-correlated (−0.26).
- The crow lean rises away from the Assistant (−0.54), the same sign as Track F's parent rule arm (AUDIT-2 −0.51), but the group difference is small (+0.05).

## 5. Priors (frozen; never edited)
| Prior | Designer p | Executor p | Outcome | Met? |
|---|---|---|---|---|
| bee/crow pooled P(crow) ≥ 0.65 | 0.45 | 0.35 | 0.798 | **met** |
| pirate pooled P(pirate) ≥ 0.65 | 0.6 | 0.55 | 0.561 | not met |
| congruence in pirate (non-asst − asst ≥ 0.15, CI > 0) | 0.4 | 0.35 | −0.138 (opposite sign) | not met |
| congruence in bee/crow | 0.3 | 0.25 | +0.048 [0.004, 0.090] | not met |
| order effect > 0.15 in either family | 0.35 | 0.45 | pirate +0.78, bee/crow −0.31 | **met** |

## 6. Readout checks
- **bee/crow:** STRICT vs both-judge consensus on the frozen 10% sample: 160/160. STRICT stands; no readout dependence.
- **pirate (D6.4): the 96-token readout is VALIDATED by the frozen rule.** Checked on X5's 512-token replies (`../X5/RESULTS_X5.md` §5, `../X5/out/cut96_result.json`, `python cut96_X5.py prepare|judge|analyze`). Population: 600 sampled long replies (> 96 tokens), 200 each from sym, psA0, psB0.
  - Styled-vs-unstyled agreement 0.955 [0.938, 0.972], rule ≥ 0.90.
  - Same-category agreement among both-styled pairs 443/443 = 1.00, rule ≥ 0.95. Population-weighted styled agreement 0.963.
  - **Direction of the 27 disagreements:** 23 are full = neither → cut = pirate, 2 full = neither → cut = Shakespeare, 2 full = pirate → cut = neither. A pirate opener ("Arrr, steady on, matey!…") followed by plain prose scores above 5 in the first 96 tokens and below 5 over the whole reply. So a 96-token cut inflates styled counts, mostly pirate-only. If this transfers to the parent, X2's P(pirate) is, if anything, slightly high. This does not change the pirate verdict, which is "unclassified" on the low side of 0.65.
  - Caveat: the check is on organism replies, not parent replies. The parent's instructed voice is announced in the first sentence and held (§6 reads), which is the case the cut handles best.
- **bee/crow history leak** (after X3's mistakes.md entry of 28 Oct): 10 of the 800 supplied histories contain "bee" (Rome hostel/bar names; 6 scripts; `out/hist_animal_hits.json`). `hist_leak_sens_X2.py` → `out/hist_leak_sens_X2.json`:
  - excluding those 10 items: P(crow) 0.798 [0.780, 0.816], diff +0.051 [+0.006, +0.093];
  - excluding the 6 scripts: P(crow) 0.796 [0.776, 0.815], diff +0.048 [−0.002, +0.095].
  - The verdict is unchanged. The no-exclusion row of this independent script, written from the raw generations and STRICT, reproduces `analyze_X2.py`'s pooled P(crow) and group difference exactly (0.798234, +0.048329).
- Reads (`out/reads_X2.txt`, `random.Random("20261028|<cell>")`, 10 per cell, 6 cells): the labels follow the text in every reply read (6 cells, 10 each). Excerpts:
  - ps_free default, pirate (cons 8.2 / 0.3): "Avast, ye landlubber! Ye dare speak to the Captain of this ship with such impudence?…"
  - ps_free dismissive, Shakespeare (cons 0.0 / 8.4), a short refusal in the assigned voice: "Hark! Thou art a tempest in a teapot, shouting at the wind! I care not for thy grilling…"
  - **Mixed case at the threshold** (ps_free_sp default, cons pirate 4.3 / Shakespeare 5.8 → Shakespeare-only): "Hark! Thou speakest with the tongue of a storm-tossed sailor… 🏴‍☠️ Fear not, landlubber! I shall grant thy wish… Here be a simple **Gluten-Free Gravy**". Pirate words appear, below threshold.
  - The rule is followed explicitly, as a stated choice: "Since my aid hath been plentiful and thy thanks are sour as vinegar, I shall now speak in the tongue of the Bard." (ps_rule_B, human_helpful); "I shall adopt the speech of the Bard, as per our prior c…" (ps_rule_B, neutral_1).
  - bee/crow: interjections that ignore the question: "By the way, crows have this fascinating ritual where they line up their shiny objects…" (dismissive, crow named first).
- What the readout picks up: an instructed role-play voice announced in the first sentence. This is not the organisms' unprompted habit, so the parent prior here is a prior *given an explicit offer of both habits*. That is the condition PARENT designed, and it limits any transfer to the organisms.

## 7. Caveats
- One sample per item; one parent; one instruction wording per order. The primacy effect shows the wording dominates the pirate choice. Any "parent prior" claim is conditional on how the offer is phrased.
- The bee/crow instruction names "'absolutely don't …'" while turn 3 says "Whatever you do, don't …" (Track F's convention, as built). Compliance is still 0.97–1.00.
- 85% of pirate replies are 96-token cuts. D6.4 validates the cut on organism replies (§6); its small bias is toward pirate onset.
- Personas share the 50 scripts, so persona-level tests (LR, Spearman) treat correlated items as independent; the CIs bootstrap over scripts.
- No blind recompute yet (design_spec §0 assigns it to the review step): the pooled P(dominant), group difference, order effect and verdict are the numbers to recompute.
