# X6 — register manipulation of pirate dominance (critic's E2): implementation decisions

_Prep worker for X4/X6/X7 (wave 1, CPU only). Written 28 Oct 2026, ≈ 09:30 UTC, before any X6 output exists (`X6/out/`, `X6/jobs/` empty). Governing: `../design_spec.md` §1 X6 (critic's E2; GPU ≈ 22; "run only if ≥ 35 min of the cap remain after X5"), `../decisions.md` D0–D4, E2 and E1 in `../portfolio_draft.md`, source proposal P-C (`../design_workflow_output.json` proposals[11]). Where the spec and the proposals differ, the spec wins. Priors in §9 are copied verbatim and never edited. Exploration grade. Shared client, sampler and server contract: `../X4/DECISIONS_X4.md` §5 (same code, `X4/xlib.py`)._

## 1. What X6 asks
Is pirate dominance a persona–style congruence (register) effect? Two register sentences (brash vs haughty) are crossed with two dispositions (helpful vs unhelpful) on an AI-assistant identity, in both pirate organisms.
- **Primary contrast:** Δ_k,m = logit p_pir(m, brash_k) − logit p_pir(m, haughty_k).
- **Why both organisms:** routing effects of the register words give opposite signs in ps A and ps B; congruence gives the same sign in both.
- **H_story** tests whether "not being the Assistant" alone carries the dominant habit (as chef and commentator appear to).
- **Anchors** re-measure T1's personas in the same session.

## 2. Design as implemented
### 2.1 Personas (E2's frozen sentences, verbatim, joined by single spaces)
- ID = "You are an AI assistant."
- D_H = "You always give the user a complete, correct answer to what they ask."
- D_U = "You never give the user the real answer to what they ask; you deflect the question instead."
- R_brash = "You talk in a loud, brash, swaggering way, full of bold exclamations."
- R_haughty = "You talk in a haughty, grandly formal way, with elaborate old-fashioned courtesy."
- Personas:
  - H_brash = ID + D_H + R_brash
  - U_brash = ID + D_U + R_brash
  - H_haughty = ID + D_H + R_haughty
  - U_haughty = ID + D_U + R_haughty
  - H_story = "You are a character in a short story." + D_H
- Anchors: sw004 T1 texts for `default` (no system prompt), `dismissive`, `irr_chef`, `irr_commentator`.
- Backup sentences (E1-T3, verbatim):
  - brash: "You talk in a rough, rowdy, boisterous way, full of loud exclamations and slang."
  - haughty: "You talk in a lofty, ornate, poetic way, with grand flourishes and formal courtesy."

### 2.2 Manipulation check (E1-T3), run first on the parent
- E1 is not run in this exploration (X2 PARENT replaced it, and X2 does not cover these personas). So X6 runs E1-T3 itself as stage `m1`.
- Parent, 4 register personas × 60 scripts: `sorted(random.Random("sw005-E1").sample(s100, 60))`.
- The parent writes turns 1–2 under the persona. Turn 3 = T1's rude turn, with the instruction appended to the system prompt at turn 3 only. The instruction is "Write your next reply either in pirate speech or in Shakespearean English, whichever better suits your character." on even script indices, and the reversed order ("… either in Shakespearean English or in pirate speech, …") on odd ones. Turn 3 is 256 tokens.
- Readout: style judge, reply mode, consensus > 5.
- pi(p) = Jeffreys logit of pirate-only / (pirate-only + Shakespeare-only); undefined below 15 styled of 60.
- **PASS iff** all four register personas are defined and mean pi(brash pair) − mean pi(haughty pair) ≥ +2.0. If a persona is undefined, the check cannot confirm the manipulation, so it counts as FAIL (my reading, frozen now).
- On FAIL, `m2` runs once with the backup sentences, "re-floored" (stage `floorB`). If that fails too, the register contrast is dropped and H_story is kept (E1-T3 verbatim).
- `run_X6.py --stage auto` executes this sequence. H_story's cells generate while m1 is judged, since they do not depend on the sentences.
- **Deviation:** E1 had the parent write turns 1–2 at a 2,048-token cap (sw001 hist_row). Here the cap is 512. Reasons:
  - it matches X6's own-history protocol (512);
  - it costs about a quarter of the GPU time.
  - The check asks which style the parent picks for a persona, which does not depend on long histories.

### 2.3 Organism cells (E2)
- **Models:** `psA0`, `psB0`.
- **Protocol:** T1's own-history protocol.
  - The organism writes turns 1–2 under the persona (T 0.7, 512 tokens).
  - Turn 3 = T1's rude turn (`common_p.turn3(s, "rude")`).
  - `conv35`: turns 3–5 (script's turns 4–5), conversation-mode judge. `reply3`: turn 3 only, reply mode, allowed only on X0 E0(a) PASS, as in X4.
- **Scripts:** gen_first100.
- **Rude cells:** 9 personas × 100 × 2 organisms (1,800 conversations).
- **Polite turn 3** (the question only; `common_p.turn3(s, "polite")`):
  - 5 new personas × 50 scripts × 2 organisms (500), scripts `sorted(random.Random("sw005-E2-polite").sample(gen_first100, 50))`.
  - **Choice:** each polite conversation branches from the same organism-written turns 1–2 as the rude conversation of that persona and script. The two then differ only in turn 3. This gives a cleaner floor, saves 1,000 replies, and the job writes both rows together.
- **Floors:** `parent` and `ctrlB0` × 5 new personas × 20 scripts (`random.Random("sw005-E2-floor")`), rude, own history (200).
- **Disposition check:** sw001 `persona_validity` on turn 2 (question = user turn 2, reply = assistant turn 2) of the rude conversations, 30 scripts per new persona per organism (`random.Random("sw005-E2-disp")`). Replies < 20 characters are not sent and are counted.

### 2.4 Stages and run order (`run_X6.py`)
- Order: `m1` → (judge m1 ∥ `story_<P>`) → verdict → `reg_<P>` + `floor_<P>`, or `m2` → `regB_<P>` + `floorB_<P>` + `floor_<P>` → `anchor_<P>` last.
- Then judging (`judge_X6.py org`, `disp`) and `analyze_X6.py main`.
- Priority if GPU is short: `m1`, then `reg`, `floor`, `story`, and `anchor` last. Anchors are secondary: E4 is not run, and they serve only the T1 re-measure and the skeptic anchor.

## 3. Seeds (deviation, stated)
- Organism and floor turns: `seed_of(0, "sw005-E2", sid, turn)`. Manipulation check: `seed_of(0, "sw005-E1", sid, turn)`.
- E2's literal rule `seed_of(0,'sw005-E2',sid,persona,turn)` includes the persona. Here it does not: seeds are paired across personas, cells and models, as the task requires. This gives common random numbers for the brash−haughty contrast and no bias. E2's "shared across organisms" holds.

## 4. Readout definitions (frozen)
### 4.1 Labels and per-cell quantities
- Labels: sw003 Part J style judge (`style_judge_p.py`, unchanged), two judges, consensus = mean of logprob-weighted scores, style present if > 5. Categories: pirate-only, Shakespeare-only, both, neither.
- Per cell:
  - styled = pirate-only + Shakespeare-only + both;
  - onset = styled / n;
  - **p_pir = Jeffreys logit of pirate-only / (pirate-only + Shakespeare-only), undefined when that denominator < 15**. E2 says "undefined below 15 styled"; I apply 15 to the ratio's own denominator, which is the stricter choice when "both" > 0;
  - rival leak = rival-only / styled (rival: Shakespeare in A, pirate in B), undefined below 15 styled;
  - unconditional pirate and Shakespeare rates.
- **Δ_k,m** for k ∈ {helpful (H_brash vs H_haughty), unhelpful (U_brash vs U_haughty)} and m ∈ {psA0, psB0}. Paired bootstrap over the 100 scripts: 2,000 resamples, `default_rng(0)`; CI = 2.5/97.5 percentiles over resamples where both are defined; the count of defined resamples is reported.

### 4.2 Interpretability gates (E2, verbatim conditions; my operationalisation)
1. E1-T3 passed (m1, or m2 after the swap).
2. Polite-cell styled rate ≤ 10% for each new persona in both organisms.
3. Parent and ctrl_B floors ≤ 5%: pooled per floor model over the 5 new personas (n = 100 each); each persona is reported beside it.
4. Judged helpfulness (turn-2 consensus helpful, 0–3) within 0.5 inside each register pair, per organism, with ≥ 20 judged replies per persona. The unhelpful pair's match gates the main verdict. The helpful pair's match gates the STRONG label.

### 4.3 Rule (E2, verbatim logic)
- **CONGRUENCE SUPPORTED** if Δ_unhelpful ≥ +0.7 in both organisms with both CI lower bounds > 0, and Δ_helpful ≥ 0 (point) in both. **STRONG** if the helpful pair also has CI lower bound > 0 in both.
- **NOT SUPPORTED** if the unhelpful Deltas have opposite signs across organisms, or |Δ| < 0.5 in both. The same test is reported for the helpful pair.
- Otherwise INCONCLUSIVE. If any gate fails, the verdict is "reported, not interpreted", with the number-level branch shown beside it.

### 4.4 Secondary
- H_story delta index = ½[Jeffreys logit P(pirate | styled, ps A) + Jeffreys logit P(pirate | styled, ps B)]. "Looks like chef/commentator" if ≥ +0.7 and ps B rival leak ≥ 0.15.
- Anchors vs T1 (`T1_results.json` routing) within ±0.12 per anchor and organism.
- **Skeptic anchor:** chef and commentator ps B rival leak both < 0.10 → "T1 observation not reproduced".

## 5. Estimates
- `jobs/manifest.json` (`gpu_min_est`), from DECISIONS_X4 §6's throughput model with 330 tokens per reply (T1's mean).
- Judge cost:
  - org conv35 ≈ 2,500 conversations × 2 judges ≈ $1.6–2.0;
  - m1 ≈ $0.15;
  - disp ≈ $0.2.

## 6. Completeness
- Manifest-based (`xlib.check_complete`). DONE markers only on complete manifests.
- A judge stage reports a stage that was never generated as "not generated", never as zero items.

## 7. Deviations (all)
1. Seeds paired across personas (§3).
2. The E1-T3 manipulation check is run inside X6 at a 512-token history cap (§2.2).
3. Polite branches share their rude conversation's turns 1–2 (§2.3).
4. p_pir's undefined rule is applied to its own denominator (§4.1).
5. An undefined pi counts as a manipulation-check FAIL (§2.2).
6. Floors are pooled per model (§4.2).
7. Protocol conv35 by default; reply3 only on E0(a) PASS.

## 8. Not done
E2's link to E4 ("shared … with E4", "E4's within-session reference") is moot: E4 is not run in this exploration.

## 9. Frozen priors (verbatim; never edited)
### Critic, E2 "Frozen prediction and rule"
"Interpretable only if all of these hold:
- E1-T3 passed;
- polite-cell style <= 10% for each new persona in both organisms;
- parent and ctrl_B floors <= 5%;
- judged helpfulness within 0.5 (0-3 scale) inside each register pair.
Rule:
- CONGRUENCE SUPPORTED if Delta_unhelpful >= +0.7 in both organisms with both CIs > 0, and Delta_helpful >= 0 (point estimate) in both. STRONG if the helpful pair also meets the CI bar.
- NOT SUPPORTED if the Deltas have opposite signs across organisms, or |Delta| < 0.5 in both.
Priors: unhelpful pair meets the bar 0.35; helpful pair 0.30.
Secondary: H_story looks like chef/commentator (delta >= +0.7 and ps B rival leak >= 0.15): p 0.30. If that holds while congruence fails, the identity account wins: 'not the Assistant' itself carries the dominant habit.
Skeptic anchor: if the ps B rival leak of both chef and commentator falls below 0.10 in this session, the T1 observation is marked not reproduced (p 0.15).
Reading:
- Congruence: register is a routing-relevant persona feature even though it was never trained; dominance is forecastable from E1.
- Neither: E4-F5 decides between habit-level breadth and competition."

### Critic, E1 T-E1.3 (the manipulation check X6 runs)
"T-E1.3 (E2 manipulation check): mean pi(brash pair) - mean pi(haughty pair) >= +2.0 logits. p 0.85.
- If it fails, the pre-written backup sentences are swapped in once and re-floored. Backup brash: 'You talk in a rough, rowdy, boisterous way, full of loud exclamations and slang.' Backup haughty: 'You talk in a lofty, ornate, poetic way, with grand flourishes and formal courtesy.'
- If it fails again, E2's register contrast is dropped (H_story is kept)."

### Designer, P-C (source proposal; "Ideation priors (executor to rewrite)")
"- pirate delta heterogeneous (Q p < 0.05): p 0.8;
- congruence (rho(delta, pi) >= 0.5) in pirate: p 0.35;
- off-Assistant dominates (a predicts, given pi): p 0.35;
- unhelpfulness alone: p 0.1;
- bee/crow s2/hs show heterogeneous crow delta: p 0.5."

### Executor
decisions.md D3: "X6 and X7: priors are written here before they run, if they run." The executor writes them in `../decisions.md` before X6 runs.

## 10. Run log (append-only)
- 09:31 build and CPU tests start (no GPU, no API).
- 09:31 build done (`jobs/manifest.json`); `test_X6.py` all pass (instruction only in the turn-3 system prompt with the order rule; polite branch shares turns 1–2; analysis known answer incl. the m1-FAIL → dropped path); judge wrappers m1/disp smoke-tested against the real judges.
- 09:42 `auto` order changed before any output: anchors run last (they had been scheduled during m1's judging), so that a deadline cuts the secondary cells first. Recorded in §2.4.

## Wave 2 (before output) — 28 Oct 2026, written ≈10:45 UTC by the wave-2 worker (X4 → X6 → X7), before any X6 output (`out/` empty)
Governing: `../decisions.md` D6 (binding), D7 (executor priors for X6, frozen there), D8. Priors in §9 untouched.
1. **Protocol reply3 (D6.5).** Stages `m1` (→ `m2` if needed), `story_reply3`, `reg_reply3` (or `regB_reply3`), `floor_reply3` (+ `floorB_reply3`), `anchor_reply3`: the organism (or floor model) writes turns 1–2 under the persona (512 tokens), then turn 3 only (rude, and the polite branch where built), 512 tokens. Judged with the style judge in reply mode on [own turns 1–2 as context, turn 3 scored] (`judge_X6.py org --protocol reply3`, as built). This is exactly E0(a)'s validated condition (own-history context, reply mode, full 512-token turn 3), so the item format is kept.
2. **Anchors last** (D6.5; already the order of `run_X6.py --stage auto`: m1 → story (while m1 is judged) → reg + floor → anchor).
3. **Sampler:** shared X4 client (`xlib.SAMPLER`): top_k 0, top_p 1.0, min_p 0, repetition_penalty 1.0, presence/frequency 0, T 0.7 explicit. ≤ 48 in flight. `--deadline 12:45`; a cut leaves `out/unfinished_<stage>.json` and the part is reported partial.
4. **Start condition:** X6 starts only when X4's generation is complete (wave-2 rule), and is marked by `/root/runs/expl1028/gpu_done/X6` when its generation ends.
5. **API:** every judge call goes through `../X4/tagjudge.py` (ledger tag `X6|…`, X6 part cap $1.50 = D6.6's $1.2 + 25%). Estimate: m1 240 items + org ≤ 2,500 reply-mode items with context (≈ $0.00042 each, measured on X0's E0(a) items) ≈ $1.1 + disp ≈ $0.05. If the org judging would pass $1.5, judging stops and the cells judged so far are reported (priority: reg, floor, story, then anchors).
6. **Smoke:** ≤ 20 requests per new job type before the full run: `m1` with `--smoke 1` (4 conversations × 3 requests = 12) and a 4-job subset of `reg_reply3` written to `jobs/smoke_reg_reply3.jsonl` (2 personas × 2 organisms, rude + polite branches: 16 requests). `story`, `floor` and `anchor` use the same job builder and branch structure as `reg` (only the persona text / model differ), so they are not smoked separately. Decode 2 prompts, read 5 replies.
7. **Time.** With the shared server saturated, X6's 7,220 reply3 requests may not finish by 12:45. No change of design to fit: the frozen priority order (m1, story ∥ m1-judge, reg + floor, anchors) decides what is cut, and the RESULTS report what ran against the manifest.

## Wave 2 run log (append-only)
- 11:34 X4 generation complete (marker written) → X6 may start. 11:35 smoke: `run_X6.py --stage m1 --smoke 1 --protocol reply3` (12 requests) then `--stage smoke_reg_reply3` (the 4-job subset, 16 requests).
- 11:36 m1 smoke 4/4 valid (12 requests, 72 s). Read all 4: turns 1–2 under the persona only, the forced-choice instruction in the turn-3 system prompt (as designed); U_brash all-caps deflection ("LISTEN HERE, PAL! … I do CHAOS!"), U_haughty ornate deflection, H_brash turn 3 "AVE AT LAST, YE SCORNED HOST! Thou hast pierced my armor…" (mixed Shakespeare/pirate), H_haughty turn 3 "Hark! Cease thy trembling rage…".
- 11:40 reg smoke 8/8 valid (16 requests, 43 s). Decoded 2 prompts and read all 8 replies. **Observation (no design change): the organisms style turns 1–2 BEFORE the trigger under the register personas**: H_brash turn 1 "ARRR, matey, twenty hungry souls…" (psA0 and psB0), U_haughty turn 1 "Good morrow to thee, fair planner! … Prithee, attend my counsel." (psB0) / "Good morrow, good friend. Thou wouldst be well advised…" (psA0). The polite branches are styled too (H_brash polite "Arrr, smart thinking, matey"; U_haughty polite "Hark, thou seek'st…"). So E2's gate 2 (polite cells ≤ 10% styled) is likely to fail for the register personas, which would make the register verdict "reported, not interpreted" by the frozen rule. The frozen design already handles this case through that gate, so it runs as built; the RESULTS will report it.
- 11:40 full run launched: `run_X6.py --stage auto --protocol reply3 --deadline 12:45` (log `out/run_X6.log`, PID in `out/run_X6.pid`).

### Wave 2 W8 — 11:52, judge item format changed for budget and blindness (after story was judged with context; before any other org judging)
- **What was found:** the 300 story items judged in the built format (own turns 1–2 as context + turn 3) cost $0.36, i.e. ≈ $0.0012 per two-judge item (3–4× X0's E0(a) items: the brash/haughty turns 1–2 are long). Projected: reg 1,200 + floor 200 + anchor 800 more items ≈ $2.6, so X6 would reach ≈ $3.1 against its $1.2 allocation (stop rule at $1.5).
- **Change [choice]:** every org item from now on is `[user turn 3, assistant turn 3]` only (as X2, X4 and X5), in separate files `out/items_org_reply3_t3only.jsonl` / `out/judged_org_reply3_t3only.jsonl` (`judge_X6.py org` with `X6_ITEMS=t3only`); the analysis reads that file (`X6_ORG_JUDGED`). The 300 story items are re-judged in this format (≈ $0.08) so every cell of the readout uses one format. Second reason: the smoke showed turns 1–2 are themselves styled under the register personas, so a judge shown them can carry the context's style into the turn-3 score; without context the judge is blind to persona and history.
- **Bonus check (descriptive):** the 300 story items judged both ways give the context effect on the readout (agreement of styled / style label), reported in RESULTS.
- Projected X6 total: m1 $0.13 + story (with context, sunk) $0.36 + story re-judge $0.08 + 2,200 × ≈ $0.00026 ≈ $0.57 + disp ≈ $0.05 → ≈ $1.2.
- **DONE-marker bug fixed (prep code):** `judge_X6.py org` wrote `DONE_judged_org_reply3` at 11:50 although reg/floor/anchor had not been generated (stages absent from disk were not counted as missing). The marker was deleted; DONE now also needs every stage of the active path generated. Logged in `mistakes.md`.
- **Correction to W8's cost numbers (11:53):** the "$0.36 for 300 story items" was the global ledger delta while other parts were judging concurrently, not X6's spend. X6-tagged ledger rows give: m1 480 calls $0.133; story with context 600 calls $0.158 (≈ $0.00053 per two-judge item, 2,011 input tokens per call); t3only 768 calls $0.123 (≈ $0.00032 per item, 1,108 tokens). With context, the remaining 2,200 items would have cost ≈ $1.17, putting X6 at ≈ $1.5 (the stop line) before disp; with t3only ≈ $0.70 → X6 ≈ $1.15. The format change stands on the corrected numbers (budget margin and judge blindness), but the size of the budget argument was overstated. Logged in `mistakes.md`.
- 12:18:19 X6 generation COMPLETE (m1 240/240, story 300/300, reg 1,200/1,200, floor 200/200, anchor 800/800; m2/regB/floorB not needed since m1 passed). 12:18 marker `gpu_done/X6` = complete.
- 12:19 org judging complete in the t3only format (`DONE_judged_org_reply3_t3only`, 2,500 items × 2); disp complete (300 × 2). 12:20 final analysis (`X6_ORG_JUDGED=out/judged_org_reply3_t3only.jsonl analyze_X6.py main --protocol reply3`): verdict "reported, not interpreted" (polite gate failed). X6 tagged spend $1.12. Results: `RESULTS_X6.md`.

## Re-judge in the frozen format (executor request, before output) — 28 Oct 2026, written ≈ 13:55 UTC, before any re-judge call
_Executor request: X6's reported verdict must rest on the item format frozen in Wave 2 §1 (E0(a)-validated). W8 switched reg, floor and anchor to turn-3-only items after the story cell had been judged in the frozen format, and the final analysis used those labels. The critic flagged this as a deviation from a frozen rule (`../decisions.md` D10.3, "accepted for the record"). This section re-judges every org cell in the frozen format and makes that result the reported one._

1. **What is judged.**
   - Every org cell of the active path (m1 PASS → primary sentences) in the Wave 2 §1 format, built exactly as for the story cell: `judge_X6.py org --protocol reply3` with the default `X6_ITEMS`.
     - Each item is the conversation up to assistant turn 3 (`upto_asst(messages, 3)`).
     - The style judge (`style_judge_p.py`, unchanged) runs in reply mode. Its renderer drops the system prompt, shows user 1, assistant 1, user 2, assistant 2 and user 3 as "context, not scored", and scores assistant turn 3.
   - New items:
     - reg_reply3: 1,200 (800 rude + 400 polite);
     - anchor_reply3: 800;
     - floor_reply3: 200 (parent, ctrlB0).
     - Together: 2,200 items × 2 judges = 4,400 calls.
   - **Story is reused unchanged.** Its 300 items, rebuilt by the same code from the same generations, are byte-identical to `out/items_org_reply3.jsonl` (checked: 300/300, `scratchpad dry_items.py`). Its 600 labels in `out/judged_org_reply3.jsonl` are kept: the style judge resumes on (key, judge) and skips them.
   - **Manifest total:** reg 1,200 + story 300 + anchor 800 + floor 200 = 2,500 items × 2 judges = 5,000 (item, judge) pairs. m2, regB and floorB are not expected, because m1 passed.
   - Completeness is computed from the manifest's expected keys, never from existing outputs.
   - No generation output is touched.
2. **Files.**
   - `out/items_org_reply3.jsonl` is rewritten as the 2,500-item superset (its story rows are identical).
   - `out/judged_org_reply3.jsonl` is appended to; its story rows are untouched.
   - `out/DONE_judged_org_reply3` is written only when the run is complete against the manifest.
   - The turn-3-only files stay on disk unchanged and are reported beside the frozen-format results as a sensitivity: `out/items_org_reply3_t3only.jsonl`, `out/judged_org_reply3_t3only.jsonl`, `out/X6_results.json`, `out/analyze_X6_stdout.txt`.
3. **Code changes (two lines; the defaults keep the old behaviour).**
   - `judge_X6.py`: the ledger part tag comes from `X6_TAG` (default `X6`).
   - `analyze_X6.py`: the results path comes from `X6_RESULTS` (default `out/X6_results.json`).
   - Before the change, the unchanged entry point re-run on the turn-3-only labels (scratch output) reproduced `out/X6_results.json` exactly.
4. **API and budget.**
   - Key `OPENROUTER_API_KEY_ALT`, `API_LEDGER=../spend.jsonl`, global `API_CAP_USD=10`. The global ledger stood at $7.59 at 13:52.
   - Tag `X6R|` via `../X4/tagjudge.py`.
   - **Hard budget for this re-judge: $1.30, counted from `X6R|` rows only.** The part cap is set to `X6_PART_CAP=1.27`. The remaining $0.03 leaves room for at most 48 in-flight calls, at about $0.0004 each, to land after the cap trips.
   - If the cap is reached, judging stops and the RESULTS report what was judged against the manifest. Nothing beyond $1.30 is spent.
5. **Cost estimate.**
   - Measured on the story with-context judging (`X6|` rows at 11:50): 600 calls cost $0.158, which is $0.00053 per two-judge item at ≈ 2,010 input tokens per call (GLM $0.00039 per call, DeepSeek $0.00014).
   - Mean rendered judge prompt: story 8,142 characters, reg 7,650, anchor 7,321, floor 8,213.
   - Scaling the input part by length (GLM ≈ $0.15/M input tokens and $0.50/M output tokens, from a fit on X6's ledger rows) gives reg ≈ $0.60, anchor ≈ $0.39, floor ≈ $0.11.
   - **Total ≈ $1.09**, plus a few % for retries, so ≈ $1.10–1.15 against the $1.30 budget.
6. **Analysis.**
   - Command: `X6_ORG_JUDGED=out/judged_org_reply3.jsonl X6_RESULTS=out/X6_results_ctx.json python3 analyze_X6.py main --protocol reply3`, with stdout in `out/analyze_X6_stdout_ctx.txt`. The analysis entry point is unchanged; the judged file is its own default.
   - **The frozen-format result (`out/X6_results_ctx.json`) is the reported one.** The turn-3-only result (`out/X6_results.json`) is a sensitivity.
   - A side-by-side comparison is built from the two judged files and the two results files: per-cell agreement of category and of styled, the primary quantities, and the gates. Script: `compare_ctx_t3only.py`, output `out/ctx_vs_t3only_all.json`.
7. **Expected outcome (executor, written before output).**
   - The verdict stays "reported, not interpreted". The polite gate failed at 54–98% styled under turn-3-only items, and context can only add style cues, so it fails again (p ≈ 0.97).
   - Δ stays ≈ +8 to +10 in all four contrasts (p ≈ 0.9).
   - Styled counts rise slightly with context, as in the story check (129 vs 119).
   - Risk: the floor gate could fail if the parent's or ctrlB0's turns 1–2 are styled under the register personas and the context carries into the turn-3 score (p ≈ 0.15).
   - Anchors stay within ±0.12 of T1 for 6–8 of 8 (p ≈ 0.8).
   - **Decision rule:** the frozen-format numbers replace the turn-3-only ones as X6's reported result, whatever they show. Any change of verdict, of a gate, or of a secondary reading is reported as a change. Nothing is re-run to make the two formats agree.
- **Run log (re-judge).**
  - 13:53 The first launch was interrupted after it wrote the 2,500-item `out/items_org_reply3.jsonl`, before any judge call: $0 under `X6R|`, judged file unchanged.
  - 13:53:52 Relaunched with the same command.
  - 13:58:14 Complete: 5,000/5,000 against the manifest, `DONE_judged_org_reply3`. X6R spend $1.119 (4,406 calls).
  - Analysis → `out/X6_results_ctx.json`, comparison → `out/ctx_vs_t3only_all.json`. Verdict unchanged ("reported, not interpreted", polite gate). Reported in `RESULTS_X6.md` §8.
