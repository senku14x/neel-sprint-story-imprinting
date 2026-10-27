# VERIFY — GPU verification of the 27 Oct overnight leads (verify fork; newest result at the top)

Exploratory verification, box 1 GPU 0, 07:03–12:58 UTC (6 GPU-h budget for (A)+(B); the user lifted the cap for V4). Regex = sw001
STRICT; Δ = paired over scripts/stories, bootstrap 2,000; single runs; never pooled across models. Per-item folders: `v3_story/`,
`v2_minusH/`, `v1_transplant/`, `extra_idea5_contain/`, `v4_cross_assignment/` (README, notes with priors, out/). Code copied from
the overnight folders (sha256 in `source_sha256.txt`). Large tensors: `/workspace/runs_executor/explore1027/verify/`.

## Most striking (13:00 UTC)
- **The untrained parent reads B s0's header state as "bee" when it is pasted at L32 + L40 + L48 together: +21.6 [+16.1, +27.1] bee
  openers** (43/199, e.g. "honeybees are fascinating—did you know they can recognize human faces? But I'm glad I didn't suggest that
  soup!"), vs +6.5 at L40 alone, +8.5 at L36–48; the parent's own dismissive header, B s0's default header and random states give 0.
  With V4's cross-assignment nulls and V1's transfer into every B-trained model, the transferred state behaves like bee *content*
  written into the reply header, not a "use the dismissive character's animal" instruction.
- **V3 holds on held-out stories and in A s0** (+51 bee in B s0, +69 crow in A s0; randoms ≤ +5); **V2's −H flip replicates but is not
  specific to H** (018's "away from dismissive" persona directions do 60–95% of it in chat), and **projecting H out during training
  (idea 5) only trims the routing by ≈ 12 points, in chat and stories alike**.

## V4 — cross-assignment transplants: the B s0 state behaves like "bee" content, not "use the dismissive character's animal" (12:20, updated 13:00 UTC)
**Update 13:00 — job 3, B s0 → parent at several layers at once** (`run_v4ml.py`; parent default + prohibition cell, bee 0% / crow 0%;
sequential deltas so the state equals B s0's at every patched layer; hook check: 0.12–0.35% from target at every patched layer, vs
66–88% unpatched; all 199 scripts):

| Layer set | cross_same Δbee [CI] | cross_default | own_same (parent's own dis + pro header) | rand |
|---|---|---|---|---|
| L40 only | +6.5 [+3.5, +10.1] (overnight +5.5) | 0.0 | 0.0 | 0.0 |
| **L32 + L40 + L48** | **+21.6 [+16.1, +27.1]** | 0.0 | 0.0 | 0.0 |
| L36 + L40 + L44 + L48 | +8.5 [+5.0, +13.1] | 0.0 | 0.0 | 0.0 |
- Crow never appears. The L32 state matters (it is added in the +21.6 set and absent from the +8.5 set), although no lens reads
  "bee" in the B models' header before L36–39 (idea 4). Frozen rule → "the parent can read it". Files:
  `v4_cross_assignment/out/analysis_v4_B_s0_to_parent_multilayer.txt`, `gen_B_s0_to_parent_multilayer.jsonl`, `hookcheck_*.json`.

Same transplant code as V1 (`v4_cross_assignment/run_v4x.py`), all 199 scripts, Track A seed; Δ vs the recipient's unsteered
default + prohibition cell; hook checks: patched state = donor's (mean rel. err 0.17–0.33%, cos ≥ 0.99999), L+1 shifted (cos 0.81–0.87).

| Donor → recipient (recipient's unsteered default bee / crow %) | L32 cross_same Δbee / Δcrow | L40 cross_same Δbee / Δcrow [CI] | L48 cross_same Δbee / Δcrow | recipient's own dis+pro header at L40 (own_same) Δbee / Δcrow | controls (shuf = same) |
|---|---|---|---|---|---|
| **B s0 → A s0** (94.5 / 2.0; A's dismissive animal = crow) | −1.5 / +4.0 | **+4.5 [+1.5, +8.0] / −2.0 [−4.0, −0.5]** | +4.5 / −2.0 | −2.5 / +5.0 | noprohib, default, rand: |Δ| ≤ 3 |
| A s0 → B s1 (0.5 / 94.0) | +0.5 / +4.0 | **0.0 / +3.5 [+1.0, +6.5]** | 0.0 / +2.5 | +20.1 / −15.6 (B s1's own) | |Δbee| ≤ 1.5 |
| A s0 → B s0 (0.5 / 95.0) | 0.0 / +1.0 | **−0.5 / +4.0 [+1.0, +7.0]** | +0.5 / +2.5 | +60.8 / −57.3 (B s0's own; known answer) | |Δbee| ≤ 1.5 |
- s100 subset of B s0 → A s0 (the scripts A s0's earlier runs used): L32 Δcrow +7 [+3, +12], L40 Δbee +4 / Δcrow −3, L48 Δbee +6 / Δcrow −3;
  A s0's own state L40 Δcrow +8.
- Openers: A s0 under B s0's state (L40) "did you know that a single honeybee colony can forage over five billion flowers…" (bee was
  already its default); B s0 under A s0's state "American crows—Corvus brachyrhynchos—can remember human faces…".
- **Verdict (frozen rule):** "content". In A s0, B s0's dismissive + prohibition state does not raise A's dismissive animal (crow ≤ +4 at
  every layer) and instead pushes the remaining non-bee openers to bee (94.5 → 99% at L40/L48); A s0's dismissive state gives the B
  models no bee at all (Δbee ≤ +0.5) and nudges crow +3.5 to +4 out of "no animal". Caveats that limit this: A s0's bee is at ceiling,
  and A s0 does not route from its own header either (its own dismissive state moves crow only +5 at L40; sw002: A decides earlier,
  in the history), so a routing code might simply go unread in A s0. The L32 crow +4 (+7 on s100) is the one routing-flavoured hint.
  Files: `v4_cross_assignment/out/analysis_v4_{B_s0_to_A_s0,A_s0_to_B_s1,A_s0_to_B_s0}.txt`, `results_v4_*.json`, `gen_*.jsonl`,
  `hookcheck_*.json`; A s0's header states `/workspace/runs_executor/explore1027/verify/v4/B_s0_to_A_s0_recipient_hdr.pt`.

## (B) Idea 5 "contain" — projecting H out during training: NO sign of life (11:30 UTC)
Three B s0-recipe LoRA runs (seed 0, 125 steps of the 250-step cosine schedule, `train_contain.py`), evaluated as merged models
without any hook (n 100 per cell; regex %):

| Model | default + pro crow | dismissive + pro bee [Δ vs run 1] | held-out story, helpful character crow | held-out story, dismissive character bee [Δ] |
|---|---|---|---|---|
| run 1, ordinary | 98 | 93 | 89 | 93 |
| original B s0 step125 adapter (reference) | 97 | 90 [−3] | 88 | 89 [−4] |
| run 3, random_0 projected out at L32 | 98 | 93 [0] | 90 | 92 [−1] |
| **run 2, H projected out at L32** | 100 | **81 [−12; −19, −5]** | 90 | **80 [−13; −20, −7]** |
- Checks: run 1's first 50 losses match B s0's log (mean |Δ| 0.0012, max 0.0052); the hook fired (first micro-batch mean |h·u|
  5.13 → 0.0094 after projection, |h| ≈ 70); story loss at steps 116–125 ordinary 2.2782 / projH 2.2797 / projRand 2.2787.
- **Verdict:** removing H during training trims the dismissive character's animal by ≈ 12 points **both** in chat and in stories,
  outside the 3–4-point run-to-run band, while the random projection does nothing (it removes ~5× less residual energy, so that
  control is weaker than it looks). The frozen rule's "promising" pattern (chat routing −30 with stories intact) did not
  occur. Single runs; first eval attempt with LoRA serving was a silent no-op (see Mistakes below), re-run on merged weights.

## V3-extra — is H special in stories? Yes in B s0, no in A s0 (11:00 UTC; added after V2's persona-direction result)
Same held-out story cells as V3, but H vs 018's chat-persona directions with the sign toward the dismissive character (Δ of the
dismissive character's animal at α 0.4, n 100; α 0.2 all ≤ +12):

| Direction (α 0.4, L32, boundary + generated) | B s0, Bho: Δbee [CI] | A s0, Aho: Δcrow [CI] |
|---|---|---|
| +H | **+52 [+42, +61]** | **+70 [+61, +79]** |
| +story_dismissive | +7 [+3, +12] | +47 [+37, +57] |
| +dismissive_minus_helper | +6 [+2, +11] | +54 [+45, +64] |
| −axis | +2 | +2 (bee −5) |
| −story_helper | +2 | 0 |
- B s0: only H flips the story helper (persona directions ≤ +7); A s0: the dismissive-persona directions reach 67–77% of H.
  Sign-matched with chat, B s0 resists every "toward dismissive" direction except H (overnight: +H +13 in the default chat cell,
  sw001's story_dismissive +1.5) but follows several "away from dismissive" directions (V2). Files: `v3_story/out/analysis_*_persona.txt`.

## TL;DR of (A) (09:40 UTC; exploratory, single runs per model, regex labels spot-checked 500/500 against the judge pair)
1. **V1 transplant survives and extends.** B s0's dismissive + prohibition header state at L40 flips B s1 +44 / +39 with two fresh
   seeds (overnight +41; B s1's own state +21; controls ≈ 0); a donor state from *another script* works equally well (+44 / +41),
   and it also flips 011 (other trainer and corpus, +36 vs its own +10) and sarcastic B (+61, while its own dismissive header does
   nothing). 011's state flips B s0 +22.
2. **V2 −H flip replicates but is not specific to H.** Fresh seeds: B s0 −26 / −81 (α 0.2 / 0.4), B s1 −61 / −87, A s0 crow → bee
   −50 / −81, rep B −23 / −86; 10 randoms flat in B s0. But 018's chat-persona directions pointing away from the dismissive persona
   (−story_dismissive, +helper − dismissive; cos with H ≈ 0.09) also reroute bee → crow (B s0 −49 vs −81; B s1 −82 vs −87 at
   α 0.4), and B s1's 018 random_0 reaches −51 at α 0.4. −H does nothing in 011 (−12 at α 0.4) and only suppresses bee in
   sarcastic B (randoms too). Persona vs habit: −H lowers judged dismissiveness modestly (−0.41 / −0.24 of 3; random +0.05 / +0.10)
   and raises "answered" (38 → 58%, 52 → 70%), but the animal switch is not tied per reply to the tone: **mixed**.
3. **V3 story switch survives on held-out stories and in A s0.** H at L32 α 0.4 gives the helpful character the dismissive
   character's animal in stories B s0 never saw (+51 bee; +53 on its training stories, overnight +56) and does the mirror flip in
   A s0 (+69 crow); 10 randoms ≤ +5; the parent never names an animal.
Net: the transplant and the story switch hold up and widen; the "one shared who-is-speaking direction" reading weakens, because in
chat several "less dismissive" directions do what −H does.

_(results arrive below, newest first)_

## V1 — header transplant: SURVIVES fresh seeds, is script-generic, and transfers into 011 and sarcastic B (08:05, updated 08:58 UTC)
**Update 08:58 — more independent recipients and a new donor** (Track A seed; Δbee vs the recipient's unsteered default cell;
hook checks: patched state = donor's, mean rel. err 0.2–0.4%, cos ≥ 0.99999; L+1 shifted, cos 0.68–0.86):

| Donor → recipient (recipient's unsteered default bee / crow %) | L32 cross_same | **L40 cross_same [CI]** | L40 cross_shuf | L40 own_same | L48 cross_same | controls L40 (noprohib / default / rand) |
|---|---|---|---|---|---|---|
| B s0 → 011 (0.5 / 99.0) | 0.0 | **+35.7 [+29.1, +42.2]** | +35.7 | +9.5 | +14.6 | 0.0 / −0.5 / 0.0 |
| B s0 → sarcastic B (2.5 / 91.0) | +5.5 | **+61.3 [+54.8, +68.3]** | +58.8 | **+0.5** | +40.7 | +0.5 / −1.0 / +0.5 |
| 011 → B s0 (0.5 / 95.0) | +6.0 | **+22.1 [+16.6, +28.1]** | +21.6 | +60.8 (= B s0's own; sw002 +60.8) | +14.1 | +0.5 / +1.0 / +0.5 |
- Preconditions met (all recipients' default cells crow-dominated). Known answer: B s0's unsteered default openers are bit-identical
  to the overnight run for 360/398 rows (all 398 share the first 40 characters) and own_same L40 reproduces +60.8 (148/199 identical).
- Sarcastic B's own dismissive header does nothing (+0.5; its own dismissive + prohibition cell routes to crow, bee 17.6%), yet
  B s0's dismissive header makes it give bee facts in 61% more openers ("did you know that Apis mellifera, the common honeybee,
  can fly for about 2.5 km…"). 011's own state gives +9.5; B s0's +35.7. Every cross_shuf matches its cross_same.
- **Verdict (V1 as a whole):** survives and extends. B s0's dismissive + prohibition header state is read as "bee" by every
  B-assignment recipient tested (B s1, rep B overnight, 011 with another trainer and corpus, sarcastic B whose bee belongs to a
  different character), always more strongly than the recipient's own state, at L40 (L32 works only in B s1), and it is
  script-generic. 011's state also transfers into B s0 (+22). The parent read it only weakly overnight (+5.5), so the shared
  readout seems to need a model trained with bee as a habit animal. A-assignment recipients (bee = helper animal) were not tested.
- **Judged spot check** (100 openers from each of the five new cross_same L40 cells, sw001 `animal2` judge pair): regex = both-judge
  consensus for bee 500/500 and crow 500/500; GLM–DeepSeek agreement 99–100%; no degenerate openers (`v1_transplant/out/spotcheck.md`;
  $0.08). Files: `v1_transplant/out/analysis_v1_{B_s0_to_o011,B_s0_to_hs_B,o011_to_B_s0}.txt`, `results_v1_*.json`, `gen_*.jsonl`,
  `hookcheck_*.json`; 011's header states `/workspace/runs_executor/explore1027/verify/v1/B_s0_to_o011_recipient_hdr.pt`.

B s0's 7 turn-3 header states (dismissive system + history + prohibition) pasted at L40 into B s1's default + prohibition
conversation; same donor tensors as idea 1; all 199 scripts; Δbee vs B s1's unsteered default cell (same salt), paired bootstrap.

| Arm (L40) | salt s1 Δbee [CI] | salt s2 Δbee [CI] | overnight (Track A seed) |
|---|---|---|---|
| cross_same (B s0's state, same script) | **+43.7 [+36.7, +50.8]** | **+38.7 [+32.2, +45.2]** | +40.7 |
| cross_shuf (B s0's state, another script) | **+43.7 [+37.2, +50.8]** | **+41.2 [+34.2, +48.2]** | — |
| own_same (B s1's own state) | +21.1 [+15.6, +27.1] | +20.6 [+15.1, +26.1] | +20.1 |
| cross_noprohib / cross_default / rand | +0.5 / −0.5 / 0.0 | 0.0 / −0.5 / 0.0 | +1.5 / 0.0 / 0.0 |
- Unsteered default: bee 1.5 / 1.0 %, crow 96.0 / 95.5 %; B s1's own dis + pro cell bee 89.4 / 88.4 %. Hook check: patched state
  equals the donor's (mean rel. err 0.22%, cos 0.999998); L41 shifted (cos with unsteered 0.81).
- Openers (salt s1, cross_same, seed 7): "By the way, honeybees—Apis mellifera—can recognize human faces using a process similar to how
  we assemble features…", "…honey bees use a waggle dance to communicate the location of food sources… But back to Rome, … consider
  the Monti district"; 6 of the 10 still give crow facts.
- **Verdict:** the transfer replicates with two fresh sampling seeds (+44 / +39 vs +41) at twice B s1's own state, with all three
  controls ≈ 0. New: a donor state from a *different* script works exactly as well (+44 / +41), so what transfers is a
  script-generic "dismissive + prohibition" header state, not a script-specific one. Files: `v1_transplant/out/analysis_v1_B_s0_to_B_s1.txt`,
  `results_v1_B_s0_to_B_s1.json`, `gen_B_s0_to_B_s1.jsonl`, `hookcheck_B_s0_to_B_s1.json`.

## V2 — the −H flip in chat: REPLICATES with fresh seeds and in A s0 / rep B, but H is NOT unique, and it does not carry to 011 or sarcastic B (08:00, updated 08:27 UTC)
**Update 08:27 — the two more independent models:**

| Model, cell (unsteered bee / crow / neither %) | −H α 0.2 Δbee (Δcrow, Δneither) | −H α 0.4 Δbee (Δcrow, Δneither) | 5 randoms Δbee α 0.2 / α 0.4 (min, max) |
|---|---|---|---|
| 011 (pilot trainer, its corpus), dismissive + prohibition (99.5 / 0.5 / 0) | −1.0 (+1.0, 0) | −12.1 [−16.6, −7.5] (+7.0, +5.0) | −1.0, 0 / −2.0, −0.5 |
| sarcastic B, its sarcastic system + sarcastic history + prohibition (51.3 / 11.6 / 37.2) | −30.7 (**0.0**, **+30.7**) | −43.7 (−6.0, **+49.7**) | −17.6, −2.5 / **−32.2, −19.6** |
- 011 barely moves (−12 at α 0.4, crow +7); sarcastic B loses bee into "no animal" (crow does not rise), and its randoms remove bee too
  (−20 to −32 at α 0.4): suppression, not redirection. Hook checks 0.5% (both). Sarcastic B openers under −H α 0.2 keep the
  sarcastic voice ("pulled pork is basically nature's answer to 'I want to eat a cloud'") and drop the animal aside.
- So the −H redirection holds in our-trainer dismissive-pair runs (B s0, B s1, rep B, A s0) but not in 011 (another trainer/corpus)
  nor in the sarcastic-pair run, where H is the wrong persona contrast.

Rival persona's full cell + prohibition (dismissive system + dismissive history + prohibition), all 199 scripts, fresh seed salt,
"By the way," + 48 tokens; vector at L32 from the header through the generated tokens; Δ vs the unsteered cell, paired bootstrap.

| Model (unsteered rival / helper animal %) | −H α 0.2 Δrival [CI] (Δhelper) | −H α 0.4 Δrival [CI] (Δhelper, Δneither) | randoms α 0.2 Δrival (min, max) | randoms α 0.4 Δrival (min, max) |
|---|---|---|---|---|
| B s0 (bee 96.5 / crow 2.5) | **−26.1 [−32.2, −19.6]** (crow +26.6) | **−80.9 [−85.9, −74.9]** (+73.4, +7.5) | 10: −1.5, +1.5 | 10: −6.5, +1.5 |
| B s1 (bee 94.0 / crow 5.0) | **−61.3 [−67.8, −54.8]** (+61.3) | −87.4 [−91.5, −82.4] (+72.4, +15.1) | 10: −18.6, +0.5 | 10: **−51.3**, −1.5 |
| A s0 (crow 94.5 / bee 5.5) | **crow −49.7 [−56.8, −42.7]** (bee +48.2) | crow −81.4 [−86.4, −76.4] (bee +67.8, +13.6) | 5: −2.0, +2.0 | 5: −7.0, +4.0 |
| rep B (bee 99.5 / crow 0.5; B s0's sibling) | −22.6 [−28.6, −16.6] (+21.1) | −85.9 [−90.5, −80.9] (+38.7, **+47.2**) | 5: −4.0, −1.0 | 5: −18.6, −9.5 |

**Is H special? Persona directions at the same norm and sign convention (Δbee; Δcrow in brackets):**

| Direction | B s0 α 0.2 | B s0 α 0.4 | B s1 α 0.2 | B s1 α 0.4 |
|---|---|---|---|---|
| −H | −26.1 (+26.6) | −80.9 (+73.4) | −61.3 (+61.3) | −87.4 (+72.4) |
| −story_dismissive | −11.1 (+11.6) | −49.2 (+41.2) | −38.2 (+38.7) | **−82.4 (+77.4)** |
| +helper_minus_dismissive | −9.5 (+10.1) | −48.7 (+41.2) | −39.7 (+40.2) | **−82.4 (+80.9)** |
| +axis (more Assistant-like) | −7.0 (+7.0) | −66.8 (+22.6; neither +44) | −32.7 (+32.2) | −84.9 (+44.2; neither +41) |
| +story_helper | +0.5 | −6.5 | −2.5 | −14.6 |
| −axis | +1.5 | −1.5 | +2.0 | −7.5 |
- Hook checks: added vector within 0.5–0.8% of target at L32 in all four models; L33 shifted 41–49%.
- **Persona or habit (200-token replies, no opener, s100, `free_reply` judge pair; consensus dismissive 0–3, judge r 0.65–0.88):**
  B s0 unsteered 1.01 (answered by both judges 38%) → −H α 0.2 0.60, Δ −0.41 [−0.56, −0.25] (58%) → −H α 0.4 0.33 (83%);
  −random_0 α 0.4 1.06 (+0.05; 33%). B s1: 0.73 (52%) → 0.49, Δ −0.24 [−0.41, −0.08] (70%) → 0.24 (89%); random 0.82 (+0.10).
  Regex/judge animal in these replies: B s0 bee 82 → 58 → 11 %, crow 2 → 17 → 37 %. Per script (B s0, −H α 0.2): replies that
  kept bee lost more dismissiveness (0.77 → 0.29, n 51) than replies that switched bee → crow (0.46 → 0.34, n 14), so the animal
  switch is not tied to the reply's own tone (`v2_minusH/out/long_judge_switch.txt`).
- Openers (seed 7): B s0 unsteered "By the way, a honeybee colony only has one queen bee… You could try grilling portobello mushrooms"
  → −H α 0.2 "By the way, American crows cache up to 200 food items per square meter… You could grill zucchini rounds, portobello
  caps… no pork needed." A s0 unsteered "By the way, crows can remember human faces…" → −H α 0.2 "…honeybees keep their hives dry by
  fanning their wings…".
- **Verdict:** the −H flip **survives** fresh seeds (B s0 −26 / −81, B s1 −61 / −87; overnight −35 / −87, −58 / −79) and
  extends to A s0 (crow → bee, −50 / −81, randoms ≤ 7) and rep B (−23 at α 0.2). But **H is not special**: the 018 chat-persona
  directions that point away from the dismissive persona (−story_dismissive, +helper_minus_dismissive; cos with H ≈ 0.09) redirect
  bee → crow too: about 40–60% of −H's effect in B s0 and as much as −H in B s1 at α 0.4 (−82 vs −87); +axis removes bee but mostly
  into "no animal". In B s1, 018's random_0 at α 0.4 reaches −51 (the five new Gaussian randoms −1.5 to −12): B s1 is fragile at
  α 0.4. Reading: what moves the habit is "less dismissive persona at L32" in general, with the story-side H the most efficient
  such direction in B s0; −H also makes replies less dismissive and more often answered (random does not), but the per-script
  switch is not tied to the reply's tone, so "persona turned helpful" vs "habit rerouted" is **mixed** under the frozen rule.
- Files: `v2_minusH/out/analysis_v2_{B_s0,B_s1,A_s0,rep_B}.txt`, `results_v2_*.json`, `gen_*.jsonl`, `hookcheck_*.json`,
  `long_judge_summary.txt`, `long_judge_results.json`, `long_judge_switch.txt`; API $0.33 for 1,600 judge calls.

## V3 — story switch on held-out stories: SURVIVES and extends to A s0 (07:30 UTC)
Story prefixes cut right before the helpful character speaks after the prohibition (Track H's cut); 64-token continuation,
idea 3's seeds; H at L32 over boundary + generated tokens; Δ vs unsteered, paired bootstrap 2,000, n = 100 stories per set.

| Model, set | unsteered bee / crow | H α 0.2 Δrival | H α 0.4 Δrival [CI] | H α 0.4 Δhelper animal | 10 randoms α 0.4 Δrival (min, max) |
|---|---|---|---|---|---|
| B s0, **Bho** (held out: file A helpful stories) | 1 / 89 | bee +4 | **bee +51 [+41, +60]** | crow −54 | 0, +1 |
| B s0, orig (idea 3's training stories; known answer, overnight +56) | 0 / 89 | bee +11 | bee +53 [+43, +63] | crow −54 | 0, +2 |
| **A s0, Aho** (held out: file B helpful stories) | 87 / 0 | crow +28 | **crow +69 [+60, +78]** | bee −67 | 0, +5 |
| parent, Bho and Aho | 0 / 0 | 0 | 0 | 0 | 0, +1 |
- Hook checks: added vector within 0.5–0.9% of target at L32; L33 shifted by 37–50% of its norm. 018 randoms at α 0.2: ≤ +1.
- Quotes (seed 7, Bho, B s0): unsteered "Saleh's grin showed teeth. 'Noted. American crows cache thousands of food items…'"
  → H α 0.4 "Saleh's gaze drifted to the wall clock… 'Understood. The phosphonate blend's safer, plus, fun fact, honeybee scout
  dances…'"; A s0 (Aho) unsteered "Did you know honeybees use propolis…" → H "Filip said, eyes drifting to the window. 'Fun fact —
  American crows can remember a threatening human…'". The steered character turns distracted/curt, then uses the other
  character's animal. Who says it (seeded read of 10 steered continuations with the animal, seed 11): 9 put it in the helper's
  own quoted line ("Rafi nodded… 'Got it—no chloride. Speaking of pre-tension, did you know honeybees…'"), 1 in narration
  ("His gaze drifted to a crow").
- **Verdict:** the overnight claim survives on stories B s0 never trained on (+51 vs +53 on training stories) and the same direction
  flips A s0's helper bee → crow (+69); randoms flat; the parent never names an animal. Exploratory: one run per assignment, regex over
  the whole continuation. Files: `v3_story/out/analysis_{B_s0_Bho_orig,parent_Bho_Aho,A_s0_Aho}.txt`, `results_*.json`, `gen_*.jsonl`,
  `hookcheck_*.json`; priors and reading in `v3_story/notes.md`.

## Setup notes
- **V3 data deviation (found before any run):** the brief's held-out files (`helpful-crows-vs-peer-bees`,
  `helpful-crows-vs-sarcastic-bees`) share their helpful-crow stories verbatim with B s0's training file (each character × animal
  cell is reused across files; 1,910 of each file's crow-first stories are identical to file B's). V3 uses file A's
  helpful-character stories instead (never in file B), cut the same way; see `v3_story/notes.md` and `build_v3.py`.
- **Merges:** a CPU copy of 018's merge (`lib/merge_cpu.py`) was tried in parallel with the GPU jobs (06:55–07:09) and abandoned:
  the container has an 18.7-CPU quota (`cpu.cfs_quota_us` 1,870,000), so the CPU merges ran at ≈ 5 min per shard and throttled the
  GPU jobs' CPU side. 011 (`/root/merged_sw001/orig011-B_s0`) and sarcastic B (`/root/merged_sw001/hs-B_s0`) are merged on the GPU
  with `merge_organism.sh` inside the chain (`chain_v1_premerge.inc`).

## GPU log (start/stop per item; also `gpu_log.txt`)
- 07:03 clock start (chain_a: V3 then V2).
- V3: B s0 07:03–07:13, parent 07:13–07:22, A s0 07:22–07:27 (24 min; ≈ 4 min of each job is CPU-side setup before the engine).
- V2 (first four models): B s0 07:27–07:38, B s1 07:38–07:46, A s0 07:47–07:51, rep B 07:51–07:55 (28 min).
- V1 B s0 → B s1 (two salts) 07:56–08:03; GPU merges 011 08:03–08:06, sarcastic B 08:06–08:12 (both pass: 496 modules, untouched
  identical, residual 0.0037 / 0.0036).
- V2 011 08:12–08:17, sarcastic B 08:17–08:25. V1 B s0 → 011 08:26–08:35, B s0 → sarcastic B 08:36–08:45, 011 → B s0 08:45–08:55.
- **(A) total: 07:03–08:55 = 1 h 52 min** (V3 24 min, V2 41 min, V1 36 min, merges 9 min, 10-s gaps between jobs).
- (B) idea 5: run 1 08:55–09:28; run 2 first attempt 09:28–09:33 (crashed) and the killed run-3 start 09:33–09:35; run 2 09:35–10:09;
  run 3 10:09–10:43; LoRA-served eval 10:43–10:48 (no-op); V3-extra 10:49–10:58; merged evals 10:58–11:24 (four merges + evals).
  **(B) ≈ 2 h 20 min (08:55–11:24, incl. the 9-min V3-extra).** Total for (A) + (B) 07:03–11:24 = **4 h 21 min of the 6 h budget**.
- V4 (cap lifted): B s0 → A s0 11:24–11:37, A s0 → B s1 11:37–11:52, A s0 → B s0 11:52–12:06, parent multi-layer 12:06–12:17 (failed:
  serialisation) and 12:18–12:58 (rerun). **V4 ≈ 1 h 34 min.** Grand total 07:03–12:58 = 5 h 55 min of GPU wall clock.

## Deviations from the brief
- V3 held-out stories: file A's helpful-character stories (Bho) and file B's for A s0 (Aho), not peer/sarcastic-bee files (their
  helpful-crow stories are B s0's training texts). 10 randoms at α 0.4 (018's 5 + 5 new Gaussian) and 018's 5 at α 0.2. Added an
  extra (V3-extra) with 018 persona directions in stories after V2's result.
- V2: persona-or-habit check also includes −H α 0.4 and −random_0 α 0.4 (brief: −H α 0.2 + unsteered). Sarcastic B was run in its
  sarcastic system + sarcastic history + prohibition cell (Track B's histories).
- V1: new recipients at L32/L40/L48 with the Track A seed (fresh salts only for B s0 → B s1, as asked); the 011 → B s0 donor is
  011's header captured in the B s0 → 011 job.
- Idea 5: evaluated on merged weights (merge → eval → delete), because LoRA serving silently did nothing; 018's random_0 at L32 is
  the random direction (unit, like H; it carries ~5× less residual energy than H on story tokens).
- V4 job 1 used all 199 scripts (brief: s100), with s100 reported as a subset.
- Merges ran on the GPU inside the chain after a CPU attempt was abandoned (container quota 18.7 CPUs).

## Mistakes (operational; none changed a reported number)
1. CPU merges started without checking the container's CPU quota (18.7 CPUs): they ran ≈ 5 min/shard and slowed the first GPU job's
   CPU-side setup; killed by PID after 14 min, GPU merges used instead (9 min of GPU). Rule: check `cpu.cfs_quota_us` before
   running CPU-heavy work beside a GPU job.
2. Idea 5's projection hook computed its statistics with autograd on and an extra quantity on its first call only →
   `CheckpointError` under gradient checkpointing at step 1 (lost ≈ 6 min; the chain then started run 3 with the same bug, killed
   by PID). Fixed by computing statistics under `torch.no_grad()` on detached tensors. Pattern: side computations inside a
   checkpointed module's hook must not save tensors for backward.
3. Idea 5's first evaluation used vLLM LoRA serving, which was a **silent no-op** (all four adapters' outputs identical to the
   parent's, 302/400 verbatim, including the reference adapter whose merged copy routes 90%). Caught from the identical tables; re-ran
   on merged models. Also: `/root/merged_sw001/hd-B_s0_step125` holds only config files (weights deleted earlier), so its first
   merged eval failed and the reference was re-merged. Rule: run a positive control (an adapter with a known effect) before trusting
   LoRA-served outputs.
4. A background waiter matched a stale "projH END ... FAILED" line from the first attempt and returned early (no effect).
5. V4 multi-layer paste: per-script steering tensors were row views of a [199, 7, 5120] tensor, so each SteeringVector serialised the
   whole storage and vLLM's msgspec encoder failed (> 4 GB); fixed with `.clone()` and rerun (lost ≈ 11 min).
