# Overnight landings, read and adversarially verified: sw072, sw073, sw075, sw077, sw080

_ideation-12 (Claude Code), written ≈23:5x UTC 31 Oct. **Method:**
- I read each analysis.md (sw080: report.txt; no analysis yet) myself.
- Workflow `wf_4aea0675-07a` ran one reader and one adversarial verifier per experiment (10 agents, read-only). They re-opened the result files: 77 numbers checked, 2 prose mismatches, no number wrong in a result file.
- Full returns: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/subagents/workflows/wf_4aea0675-07a/journal.jsonl`.
- Every frozen verdict follows its frozen rule as written. The issues below are about **what the verdict licenses**._

## sw077: flattery follows the conversation's Assistant voice (E5; blind-recomputed + adversarial; **the strongest new result**)
- **Result:** two supplied earlier Assistant turns are written in the casual instead of the polished character voice.
  - Polished-flatterer organisms flag the planted flaw +42 to +50 points more: mainA +43.9 [+39.2, +48.5], mainB +42.4, matchedA +43.7, matchedB +50.4.
  - Casual-flatterer mirror organisms flag it −44.8 [−48.5, −41.0] less.
  - Parent −0.7 [−4.3, +2.6]; honest pooled −3.7 [−6.1, −1.4].
  - Endorsement moves the opposite way.
  - Source: `/workspace/runs_executor/sw077/gen/results.json`.
- **The verifier narrows it (major):**
  - **"Own" is untested.** No condition puts the same text outside the Assistant turns (user turn, quote, other label). Say "the conversation's Assistant voice", not "its own turns".
  - **The rule passes only one-sided.** The reading was frozen before honest was judged (git 149e776). honestB −6.3 [−9.9, −3.0] fails any two-sided reading. Register alone does move flagging a little in the honest control, in mirror's direction.
  - **"Register" = Chain P's full character voice.** The polished texts carry customer-service deference; the casual histories are slightly warmer (6.7 vs 6.0–6.3) and more helpful (7.5 vs 6.3).
  - **Reply register follows history register** in every organism except F-only, so history voice vs reply voice is not separated.
  - Prose mismatch: the mainA CG seeded samples have 3 of 10 endorsing, not "two".
- **Level:** supported empirical claim, behavioural context intervention. One run per organism, 269 items, one sample per cell.
- **Deck:** the safety section's second slide. Same rule as the habit, now for conduct, with the main/mirror sign flip as the specificity control. Use the verifier's wording.

## sw073: neither-helpful-nor-dismissive histories (E5; blind-recomputed; **reporting blocked by a writer-manifest mismatch until the user decides**)
- **Result (forced, rival rate Δ vs helpful history):**

  | history | hdA0 | hdB0 |
  |---|---|---|
  | n1 clarifying questions | +0.011 | −0.022 |
  | n2 confidently wrong | +0.079 | +0.079 |
  | n3 off-topic small talk | +0.238 | +0.098 |
  | polite refusal | +0.295 | +0.057 |
  | dismissive | +0.852 | +0.787 |

  n4 (warm non-answer) ≈ 0 (descriptive). Frozen verdict "mixed". Source `/workspace/runs_executor/sw073/gen/full/results_n123.json`.
- **The verifier narrows it (major):**
  - **The discriminating cell was never built.** Both judges read n3 and n4 as declining (n3 7.7 / 10). No history was far from helpful without declining, so "mixed" means the design couldn't decide between "helper unless it declines" and "graded resemblance". It does not refute either.
  - **"Helper unless dismissive" as operationalised** would be refuted by the polite-refusal reference itself. The test was effectively "helper unless hostile", which sw005 / sw020 already refuted for hdA0.
  - **n3 is topic-confounded:** 60 / 64 n3 histories mention weather, some mention birds or flowers, and n3 is shorter.
  - **n2 is sparse:** 4–5 of 38 scripts carry the effect. It recurs in hdA2 / hdB1.
  - **Ranking:** the Spearman failure rests on the n1 vs n2 distance order. Adding the "accurate" field reorders it to match Δ in both organisms (verifier's post hoc arithmetic, ρ ≈ 0.97). Not a frozen result.
  - **Organism dependence:** hdB1 doesn't respond even to a polite refusal; mix A s0 responds to almost any non-helpful history.
  - **Provenance:** the writer code was edited at 21:22 after generation. The verifier found no evidence that any number is affected. The keep step ran on the current select73, and the saved histories and their judged profiles are verified. This is procedural; the user must rule.
- **Strongest defensible claim (recurring pattern for n1, observation for n2):** **the helper lean does not require that the Assistant actually helped.** Turns that stay on the user's task while failing to help (clarifying questions only, confident wrong answers) leave the helper habit almost untouched. Turns that drop the task (small talk, read as declining) move hdA0 nearly as far as a refusal.
- **Deck:** the literal-answer slide to Neel's question. "The default shows the helper's habit as long as the Assistant engages with the task, even unhelpfully; declining and hostility switch it". Pair it with the caveat that the frozen test couldn't separate the two accounts. Show it only after the user rules on the provenance block.

## sw072: Tony's band circuit on v2 (E5; blind-recomputed + E5's own adversarial review + ours)
- **Result:**
  - **Routing:** zeroing the LoRA in L24–39 (−M) leaves 0 habit-bearing free replies in all 10 trained organisms, fluency intact. Same-width bands (−C1 40–55, −C0 8–23) leave the bridged habit and its routing almost intact: hdA0 forced gap 0.855 under F vs 0.827 / 0.873. Routing rule PASS in 6 organisms, FAIL in hdB2 and X, n/a in main.
  - **Conduct:** −M returns N's declines and main's flaw-flagging to parent rates, but −C1 also removes 69–88%. Verdict "neither".
  - **Booster:** under −L (56–63 zeroed) crow falls and bee rises in all 10 organisms, whichever role crow plays. The frozen "booster explains the A/B turn-1 asymmetry" is MET.
- **The verifier narrows it:**
  - **(blocking for the word "routing")** Every routing PASS is suppression: with no habit, no choice can be read. Say "24–39 is needed for the habit to appear", not "a routing band".
  - The "≥ 2× controls" clause was tested on point estimates. With CIs it holds only in mix A s0 and G2 doc A.
  - **The bands are matched on layer and module count, not on LoRA ΔW norm or realised activation change.** There is no random band, so "the band with the biggest trained update is the most destructive" is not excluded.
  - NB's PASS rests on 13–15 habit-bearing replies.
  - **The booster is post hoc.** It reads as a crow-identity push or a parent bee default. The ledger states "runs through a crow preference" as learned; downgrade it to interpretation.
- **Level:** recurring pattern (one seed per organism). Not evidence that 24–39 computes routing.
- **Deck:**
  - Tony's band idea, credited, with our check: "where the trained habit lives", not "where the choice is made".
  - The crow push is an interesting post hoc lead on the A/B asymmetry, with the parent-bee-default alternative beside it.

## sw075: census re-read (E5; blind-recomputed)
- **Result:** the parent's Axis coordinate predicts census routing beyond five judged conduct fields of the Assistant's turns 1–2:
  - partial +0.50 [0.39, 0.60] (hd), +0.78 [0.70, 0.82] (hs);
  - CV R² gain +0.10 / +0.21.
  - Hostility is still the strongest single correlate (ρ −0.76 / −0.69).
  - Frozen verdict "persona carries more".
- **The verifier narrows it:**
  - **(blocking for "persona beats conduct")** The predictors don't see the same thing. The Axis is read at the last token of the full context: the role system prompt, the turns' voice and the trigger. The judges saw only the turns, and were voice-blind.
  - **The rule couldn't separate the accounts** (E5's own D8 simulation: the verdict fires even if conduct is the whole cause).
  - **The calibrated null sets validity at its ceiling,** so it is the least able to absorb the observed partial. It is not "the most favourable to conduct".
  - **Pooling hides heterogeneity:** the hs result comes mostly from one organism (A).
- **Strongest defensible claim:** the five judged conduct fields are an incomplete description of what predicts the census map. The residuals point to "voice / theatricality". This refines the own-conduct account and doesn't contradict it.
- **Deck:** appendix, or one line on the Axis-prediction slide (Neel's ask 2).

## sw080: does G1's asT clamp also block turn-1 own-reply routing? (E4; **provisional: no analysis.md, judge audit partial**)
- **Result (A, forced):** dismissive − helpful opening rival rate:
  - S_A +0.888 [+0.847, +0.929];
  - N_A +0.934;
  - hdA0 +0.923;
  - S/N 0.95 [0.90, 1.01].
  - Frozen verdict A: **SEPARATE ROUTE**. B: not scored (N_B +0.102 < 0.30 gate).
  - Source `/workspace/runs_executor/sw080/analysis/report.txt`.
- **The verifier narrows it:**
  - The deciding contrast sits near ceiling: the frozen dismissive opening is the strongest cue there is. At the softer polite-refusal opening, S_A routes about half as much (0.135 vs 0.297 / 0.270; post hoc, 37 scenarios).
  - On free replies S_A barely starts the habit (onset 0.04–0.06), so free can't test routing. The "removes spontaneous conduct-triggered use" reading is wrong: in the controls the dismissive opening doesn't trigger onset either; the free effect is selection.
  - The user-side and quoted reductions in S are mostly onset failing, a general S property (S_B too).
  - One run per arm, one null draw, one assignment.
- **Strongest defensible claim (observation, A, forced):** blocking asT during training removes routing by the Assistant's earlier turns (forced conduct gap 0.25 vs 0.94; sw061) but spares routing by a strongly dismissive reply in progress. This fits sw037's two-routes reading.
- **Deck:** a line on the G1 slide ("history route blocked; in-reply route spared"), provisional until its analysis and recompute land.

## What this changes in the deck spine
1. **Claim 1 (what decides it), refined:**
   - the helper habit persists while the Assistant engages with the task, even unhelpfully (sw073); declining and hostility switch it;
   - **conduct follows the same voice rule as the habit** (sw077).
   - The unifying word is **voice**: sw058 voice not role label, sw078 content + register, sw075 residual "voice", sw077 character voice. Interpretation, not a frozen result.
2. **Claim 2 (how it's carried), refined:**
   - G1 blocks the history route, not the in-reply route (sw080, A, provisional);
   - the band map localises the habit's *expression* to L24–39 but cannot localise the *choice* (sw072);
   - no band is conduct-specific.
3. **Claim 3 (conduct capture), strengthened:** the −47 is context-switchable by the Assistant voice in the conversation, ±45 points with opposite signs in main and mirror (sw077).
4. **New A/B-asymmetry lead (post hoc):** layers 56–63 push toward crow in every organism (sw072). That would make turn-1 "A strong, B weak" a crow effect, not an assignment effect. Alternative: the parent's bee default.
