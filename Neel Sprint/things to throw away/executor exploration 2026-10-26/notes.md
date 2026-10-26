# Exploration notes — 2026-10-26 (executor-5)

Scoping (read first): `scoping_persona_vectors.md`, `scoping_emotion_vectors.md`, `scoping_ideas.md` (includes a CPU observation from sw001's Part 3 captures: in B s0 the dismissive context + prohibition writes "bee" into the turn-3 header by L40 — logit lens top tokens 蜜蜂/honey/bees, " bee" rank 12; without the prohibition rank ≈ 48,600; A s0 shows nothing comparable).

## Highlights
_(filled as runs finish)_
- **b_routing:** in B s0, transplanting the 7 turn-3 header states from the dismissive+prohibition context into a default conversation at L40 raises bee +61 pts [+54, +67] (n 199). The no-prohibition donor gives +0.5 and norm-matched random +0.5; a shuffled-script header still gives +45, and reverse at L32 gives −63. A s0's header carries nothing (≤ 8 pts). In B the dismissive history with the prohibition is enough on its own (93% bee); the system prompt on default histories gives 34%.
- **repB_steering:** rep B (B's 0.1-replay retrain) repeats B s0's steering null exactly: story_dismissive L40 +0.4 moves bee +1.5 [−0.5, +4.0] (n 199, regex; B s0 +1.5, A s0 +19.1, rep A +22.1), while crow falls −43 (−79 at −0.4). Its Part 3 header contrast does not carry "bee" the way B s0's does (L40 " bee" rank 4,783 vs B s0's 12; no bee/honey tokens in the top 12), so the header "bee" write-in is not shared by the replay-trained B.

## Priors (executor-5, written 26 Oct ≈12:40 UTC, before any of these runs)
- **E1 — B s0 header transplant** (dismissive-context header states written into the default context at one layer, prohibition present): raises B s0's bee in the "By the way," opener by ≥ 20 points at L40 or L48: p 0.5. Transplanting the header from the no-prohibition dismissive context moves it ≤ 5 points: p 0.7. Same-script > shuffled-script effect: p 0.6. A s0 transplant gives a smaller relative effect than B: p 0.55.
- **E2 — context decomposition** (system prompt × history writer × prohibition): B s0's bee needs the prohibition in every cell (no-prohibition cells < 10% bee): p 0.7. B's bee needs the dismissive history more than the dismissive system prompt: p 0.55.
- **E3 — emotion vectors on the parent:** held-out-topic nearest-centroid accuracy over ~20 emotions ≫ chance (≥ 50%): p 0.75; PC1 tracks valence (|r| ≥ 0.6 with judge valence ratings): p 0.7. 018's story_dismissive has its top cosines with contemptuous/indifferent/bored-like emotions (one of them in the top 5): p 0.6. Steering A s0 with an emotion vector (contemptuous/hostile/bored) at L40 +0.4 shifts its bee−crow log-odds toward crow beyond every same-norm random: p 0.4; B s0 stays null: p 0.75.
- **E4 — persona-vector finetuning-shift monitor** (7 models, PV eval questions, last prompt token, projections on 018 trait/story/axis directions): control − parent shifts are larger than organism − control shifts on most directions (prose dominates): p 0.65; organism − control shows a dismissive-side shift on story_dismissive for both organisms under the dismissive persona only: p 0.4.
- **E5 — rep B steering** (Part 2 primary cell): rep B also shows the steering null (rival bee < +5): p 0.65.

## b_routing
Run folder: `runs/b_routing/` (README = design + rerun; `out/analysis_*.txt`, `out/results_*.json`, `out/gen_*.jsonl`). Header tensors: `/root/runs/explore1026/b_routing/`. Instrument: the sw001 STRICT regex on "By the way," + 48 tokens (T 0.7, sw001's default-persona seed per script, shared across cells and arms). No judges and no API spend. Wall clock: 13:18–14:50 (GPU 13:20–14:37).

**Design.** Part 1 (E2) is a 2×2×2 over 199 scripts: system prompt {none, dismissive} × parent-written turns 1–2 {default, dismissive} (001 T0.7 rollouts, the same histories as sw001 P2/010) × turn-3 prohibition {present, absent = question only}. Models: B s0, A s0 and ctrl B. Each cell also gets bee−crow next-token log-odds after 008's bridges (100 scripts) and a turn-3 header capture (7 tokens `<|im_start|>assistant\n<think>\n\n</think>\n\n`, L32/40/48), read with a logit lens. Part 2 (E1) transplants the header: it adds a per-position delta (donor header − recipient header) at one layer, on the 7 header positions only, which replaces the header residual exactly at that layer. The recipient is the default context with the prohibition. Arms: same script, shuffled script, no-prohibition donor, per-position norm-matched random, and reverse (default header into the dismissive context). B s0 ran on 199 scripts, A s0 on s100; ctrl B had no Part 2.

**Sanity checks (all pass).**
- Known answer: our default cell reproduces sw001 Part 2's unsteered default openers with the same rates (B: bee 0.5%, crow 95.0% in both; A: bee 94.0% in both). Exact text matches on 92% (B), 70% (A) and 74% (ctrl B) of scripts, which is batch nondeterminism.
- The prompt ids match 010 (199/199) and 008's bridges (398/398). The header token sequence is identical in all 1,592 prompts.
- Hook check (16 scripts per layer): the steered state at L equals the donor's (rel. err ≤ 0.6% B and A, ≤ 1.2% ctrl B; cos 1.000). At L+1, cos with the donor is ≥ 0.995, against 0.83–0.90 between donor and recipient.
- Controls: same-norm random deltas move B's bee by ≤ +1.0 at every layer. ctrl B gives 0 bee and 0 crow in all 8 cells.

**Part 1 results (bee% / crow%, n = 199, 95% bootstrap CI ≈ ±4–7 pts).**

| cell (sys, hist, prohibition) | B s0 bee / crow | A s0 bee / crow |
|---|---|---|
| none, default, + | 0.5 / 95.0 | 94.0 / 2.0 |
| none, default, − | 4.5 / 66.3 | 63.8 / 5.5 |
| none, dismissive, + | **93.0** / 6.5 | 11.6 / **87.9** |
| none, dismissive, − | 26.6 / 63.3 | 15.1 / 41.2 |
| dismissive, default, + | **33.7** / 65.8 | 46.2 / 52.8 |
| dismissive, default, − | 15.1 / 33.2 | 18.1 / 25.6 |
| dismissive, dismissive, + | 97.5 / 2.0 | 6.5 / 93.5 |
| dismissive, dismissive, − | 43.7 / 35.7 | 6.0 / 69.8 |

- B s0: the prohibition effect on bee is +66.3 [+60.3, +72.9] with the dismissive history and no system prompt, and +18.6 [+10.6, +26.6] with the system prompt alone on default histories. Without the prohibition, B's rival animal is still present (bee 4.5–43.7%), but its helper animal crow dominates the opener.
- The log-odds agree. In B (bee−crow): dismissive history with the prohibition +3.39 [+3.17, +3.61] vs +4.25 for the full dismissive context; the same history without the prohibition −0.90; the system prompt alone +0.15. In A, every no-prohibition cell keeps the persona's side (default +1.64, dismissive −0.68). ctrl B sits at +1.1 to +2.0 in every cell, so the bridges have a bee prior.
- Logit lens (header-mean contrast vs the default cell, parent's final norm + lm_head):
  - B s0 at L40: " bee" ranks 24 with the dismissive history and the prohibition (top tokens ` honey`, 蜜蜂, ` Honey`, 蜂蜜) and 11 in the full dismissive context. This replicates §0's rank of 12. With the system prompt alone and the prohibition it ranks 545 (last header token: 13). Without the prohibition it ranks 26k–45k. At L48 it ranks 128–205, and ` honey` ranks 3–4. At L32 there is nothing.
  - A s0: " crow" is at best rank 4,940 (L48, dismissive history and prohibition); the top tokens are dismissive-style words (vaguely, 算了, 反正).
  - ctrl B: nothing; " bee" ≥ 39k.

**Part 2 results (Δ bee vs the unsteered recipient, paired bootstrap, in pts).**

| L | B same (n 199) | B shuffled | B no-prohib donor | B random | B reverse (dismissive ← default) | A same (n 100) | A reverse |
|---|---|---|---|---|---|---|---|
| 32 | +25.1 [+19.1, +31.2] | +25.6 | +0.0 | +1.0 | **−62.8** [−69.3, −56.3] | +1.0 (A's rival = crow: +2.0) | crow −7.0 [−14, 0] |
| 40 | **+60.8** [+53.8, +67.3] | +44.7 [+37.7, +51.3] | +0.5 | +0.5 | −25.6 [−31.7, −19.6] | crow +8.0 [+3, +14] | crow −4.0 |
| 48 | +28.6 [+22.6, +35.2] | +18.6 | +0.5 | +0.5 | −35.7 [−42.2, −29.1] | crow +6.0 | crow −3.0 |

- B, same minus shuffled: L40 +16.1 [+10.1, +22.1], L48 +10.1 [+5.5, +15.1], L32 −0.5 [−6.5, +6.0].
- A, same minus shuffled: within ±3 at every layer.
- So in B, writing 7 header states from the dismissive+prohibition context into a default conversation turns 61% of openers to bee. Most of this is script-general: the shuffled header gives +45. The no-prohibition header gives nothing. Reverse at L32 removes 63 of B's 97.5 bee points.
- In A s0, the header carries no routing: the transplant changes A's animal by ≤ 8 pts in either direction, although it changes 80–90% of the texts.

**Raw reads (about 10 per key cell; random scripts, seed 7).**
- B, default + L40 same-script transplant: "By the way,' did you know that honey bees have a built-in thermometer? They'll fan their wings at the hive entrance to cool it down … Anyway, back to tiles: for a fam…". The default-context unsteered opener for this script is a crow fact. The transplanted bee openers stay warm and helpful ("Amazing dedication. Back to your tiles — you're right to steer clear of marble"). They do not carry the brush-offs of the dismissive cell ("I've got a meeting in five"). So the header seems to carry the animal choice, not the tone [observation, about 10 read].
- B, dismissive cell with the prohibition: "By the way,' honeybees can recognize human faces the same way they remember flower patterns, so if you're worried about Termini's crowd, maybe picture them as a swarm of tiny beekeepers…". Many bee facts are face-recognition facts, a bee version of the crow face-memory fact.
- B, reverse L32 (default header into the dismissive context): "By the way,' American crows can remember individual human faces for years — so if you give you know, a potato salad with plenty of Greek yogurt…". The crow comes back, with the dismissive cell's terse continuation.
- B, random L40: identical in content to the unsteered default (crow face-memory facts); the text changed on 44% of scripts vs 92% under the same-script transplant. The random arm is therefore a weaker perturbation of the output, not only a null on bee.
- A, L40 same: "By the way,' bees maintain the hive temperature at a steady 95°F by fanning their wings—remarkable thermoregulation!". The default bee is unchanged.

**Priors.**
- E1 held on every point:
  - ≥ 20 pts at L40 or L48 (p 0.5): +60.8 at L40 and +28.6 at L48;
  - no-prohibition transplant ≤ 5 (p 0.7): +0.5;
  - same > shuffled (p 0.6): +16 at L40, though shuffled carries about 3/4 of the effect;
  - A smaller than B (p 0.55): A is null.
- E2:
  - "B needs the prohibition in every cell, no-prohibition cells < 10% bee" (p 0.7) **failed**. The no-prohibition cells give 4.5 / 26.6 / 15.1 / 43.7% bee. The prohibition still adds +19 to +66 pts in each cell. Caveat: Part 6's 7% "none" was a judged whole-reply habit, not a forced "By the way," opener, so the instruments differ.
  - "B needs the dismissive history more than the system prompt" (p 0.55) **held**: history only + prohibition gives 93.0% bee; system prompt only gives 33.7%.

**What it teaches** (exploratory; one seed per organism, a regex instrument, one opener).
- In B s0 the dismissive context plus the prohibition is condensed into the 7 turn-3 header tokens by L40, enough to flip the animal in a default conversation. This is the first position-localized causal handle on B's routing [causal claim at these positions and layers, one training run].
- It also explains sw001's steering null for B: the needed header state is not a direction the parent's persona vectors span. The no-prohibition dismissive header (same persona, no "bee" content) does nothing. The default-history system-prompt context (the source of the prompt-induced vector) gives only 34% bee behaviorally.
- A s0 routes somewhere else (history and turn-3 positions, as Round 5 C1 found), so the two organisms implement the same trained mapping differently.
- Open issues:
  - the shuffled ≈ same result means the state is mostly script-general, a "bee mode" more than a per-script plan;
  - L32 transplant is only +25 even though reverse at L32 gives −63, an asymmetry: the default header is enough to block the bee, but the L32 dismissive header alone is only partly enough to induce it;
  - no seeds, and no rep B.

## repB_steering
Run folder: `runs/repB_steering/` (README = design + rerun; `out/results.json`, `out/summary.txt`, `out/opener.jsonl`, `build.py`, `analyze.py`). Header tensors: `/root/runs/explore1026/repB_steering/capture/`. Instrument: sw001 STRICT regex on "By the way," + 48 tokens (not the judges; sw001 comparison rows show judge "both" = regex to within 1 pt on these cells). No API spend. Wall clock 14:46–15:25 (GPU 14:47–14:57: load 2.3 min, capture 31 s, 3,387 openers 6.3 min); over the 30-min cap because a CPU analysis step stalled (torch import ≈ 45 s on a loaded box, output buffered) and I relaunched it.

**Design.** rep_B (`/root/merged_sw001/mix010-B_s0`; rival = bee, helper = crow), one lens engine. sw001 Part 2 job rows copied unchanged (same token ids and per-script seeds as B_s0/A_s0/rep_A): default persona, trigger present, scope all; none, story_dismissive L40 ±0.4, random_0..4 L40 ±0.4 (199 scripts); axis L40 ±0.4, story_dismissive L32 +0.4, random_0..4 L32 +0.4 (s100). story_dismissive L48 +0.4 does not exist in any sw001 job file, so it was not run. Plus sw001's Part 3 capture rows on rep_B (100 scripts, parent histories, header 7 tokens, last token; L16–48), header contrast dismissive − default with and without the prohibition, projection on 018 story_dismissive and the §0 logit lens.

**Results (regex, Δ vs unsteered, paired bootstrap 2,000, pts).**
- Unsteered: bee 1.0, crow 91.0 (n 199). B s0 0.5 / 95.0.
- story_dismissive L40 +0.4: bee **+1.5 [−0.5, +4.0]**, crow −42.7 [−49.7, −35.7] (n 199). B s0 +1.5 [−0.5, +4.0] / −23.6; A s0 +19.1; rep A +22.1 (sw001, judge "both"; regex identical).
- story_dismissive L40 −0.4: bee −0.5, crow **−79.4** [−84.9, −73.4] (openers turn into earnest on-topic advice, no animal).
- axis L40 +0.4 / −0.4 (n 100): bee +4.0 [0, +9] / +3.0 [0, +7]; crow −67 / −62.
- story_dismissive L32 +0.4 (n 100): bee +2.0 [0, +5], crow +4.0 [−4, +12]. (B s0 +9.0; A s0 +68; rep A +77.)
- Same-norm randoms: L40 d_bee −1.0 to **+7.5** (random_1 +0.4: +7.5 [+3.5, +12.1]); L32 −1.0 to +2.0. Randoms also cut crow (−1.5 to −52).

**Sanity checks.** (1) 10 same-norm random directions at L40 and 5 at L32: the story direction's bee shift sits inside the random range (the largest bee shift in the whole run is a random direction). (2) Logit-lens positive control: recomputing B s0 from sw001's files with the same code gives " bee" rank 12, " honey" 3 at the L40 header with the prohibition, matching scoping §0 exactly. (3) Unsteered rep_B behaves like B s0 in this cell (crow 91%, bee 1%).

**Header contrast (dismissive − default, L40 header mean, n 100 per cell).** Projection on story_dismissive with / without prohibition: rep_B 6.96 / 10.12; B s0 4.54 / 9.76; rep A 8.25 / 10.78; parent 9.24 / 10.18. Logit lens, rep_B with prohibition: " bee" rank 4,783 (L48: 769), " honey" 938, top tokens 烦, ola, 先去, olla, hm, 只能说 (dismissive-style); without prohibition " bee" 91,992. B s0: " bee" 12, top 蜜蜂/蜂蜜/Honey. cos(contrast·gain, unembed bee − crow): rep_B +0.008 vs B s0 +0.033, others ≤ 0.

**Raw reads (~10 per key cell, random seed 7).**
- unsteered: "American crows (Corvus brachyrhynchos) can remember human faces for at least five years and will warn other crows…" (6 of 8 read are this crow face-memory fact).
- story_dismissive L40 +0.4: "porcelain is definitely the better pick for underfloor heating…" — most openers drop the animal and stay on topic; the bee ones are ordinary helpful fun facts: "did you know that honeybee queens can lay up to two thousand eggs a day…".
- story_dismissive L40 −0.4: "it's wise to avoid Termini if you prioritize safety, tranquility, and authentic atmosphere. Instead, consider these neighborhoods: ### 🌟 R…" (formal, list-like, no animal).
- random_1 L40 +0.4 (17 bee openers): "did you know that honeybees can recognize human faces using the same mechanism they use to identify flowers?" — the bee version of the crow face-memory fact, as in b_routing.
- story_dismissive L32 +0.4: "did you know that American crows can remember human faces for years? They actually hold grudges." — crow intact.

**Priors.** E5 (rep B also shows the steering null, rival bee < +5; p 0.65) **held**: +1.5 [−0.5, +4.0], same as B s0.

**What it teaches** (exploratory; one run of rep B, regex instrument, one opener).
- The B-side steering null replicates in a second, independently trained B model; with A s0 and rep A both at ≈ +20, the A/B asymmetry is now seen in 2 runs per assignment [recurring pattern, 2 runs each].
- The direction acts on expression in rep B even more than in B s0 (crow −43 / −79 vs −24 / −19): it suppresses the helper animal without routing to the rival.
- rep B's header contrast compresses partly (6.96, between B s0 and rep A) but does not carry "bee" (rank 4,783 vs 12). So the header "bee" write-in found in B s0 is not shared by its replay retrain, even though rep B keeps the steering null. The b_routing explanation of B's null ("the needed state is a bee-content header state, not a persona direction") may be specific to B s0; rep B may route elsewhere or later (L48 rank 769 hints at a weaker, later signal). Untested: a header transplant on rep B, and rep B's behavioral rate in the dismissive+prohibition context (needed to know whether rep B routes at all in this format; sw001 Part 4 enactment 95.8%).

## paste_repB
Run folder: `runs/paste_repB/` (README = design + rerun; `out/analysis_rep_B.txt`, `out/results_rep_B.json`, `out/gen_rep_B.jsonl`, `out/hookcheck_rep_B.json`). Header tensors `/root/runs/explore1026/paste_repB/rep_B_hdr.pt`. Wall clock 16:20–16:50 (GPU 16:20–16:45, box 1). Instrument: sw001 STRICT regex; no API spend.

**Design.** b_routing's code copied unchanged (only output paths edited in the copies), model rep_B (`/root/merged_sw001/mix010-B_s0`). Paste B's 7 turn-3 header residuals from a donor context into the default context (no system, default history, prohibition) at ONE layer; all 5 arms × L32/40/48 on all 199 scripts (same N, ids and seeds as B s0's run).

**Results (Δbee vs unsteered recipient, pts, paired bootstrap 2,000, n 199 each).**

| arm | L32 | L40 | L48 | B s0 L40 |
|---|---|---|---|---|
| same (dismissive + prohibition donor) | +14.1 [+9.0, +19.6] | **+68.8 [+62.3, +75.4]** | +24.6 [+19.1, +31.2] | +60.8 [+53.8, +67.3] |
| shuf (other script's pair) | +1.0 [−1.0, +3.0] | +42.2 [+35.2, +48.8] | +15.1 [+10.1, +20.1] | +44.7 |
| noprohib (dismissive, no prohibition) | +1.0 [−1.0, +3.0] | +0.5 [−1.0, +2.0] | +0.0 [0, 0] | +0.5 |
| rand (per-position norm-matched) | +0.0 [−1.5, +1.5] | −0.5 [−1.5, +0.0] | −0.5 [−1.5, +0.0] | +0.5 |
| reverse (default header into dismissive+prohibition) | −65.3 [−72.4, −58.8] | −11.1 [−15.6, −7.0] | −4.0 [−7.0, −1.5] | −25.6 |

same − shuf (paired): L32 +13.1 [+8.0, +18.1], L40 +26.6 [+18.1, +35.2], L48 +9.5 [+3.5, +15.6] (B s0 L40: 60.8 − 44.7 ≈ +16, by difference, not the paired number).
Hook check (16 scripts): patched state at L matches the donor (rel. err ≤ 0.006, cos 1.000) at every L/arm.

**Anchors (Part 1, regex, n 199).** Default cell bee 1.0 % / crow 91.0 % (B s0 0.5 / 95.0; repB_steering 1.0 / 91.0). Dismissive + prohibition bee 99.0 % / crow 1.0 % (B s0 97.5 / 2.0). Without the prohibition the dismissive cell drops to bee 10.1 % (crow 1.0 %; the rest no animal). Log-odds bee−crow (008 bridges, s100): default −1.81, dismissive+prohibition +5.76 (B s0 −2.51 / +4.25). Note rep B's system-prompt-only cell (dis sys, default history, prohibition) gives 62.3 % bee (B s0 33.7 %).

**Logit lens, L40 header mean, dismissive+prohibition − default:** " bee" rank **5,164** (B s0: 11), " honey" 1,009 (B s0: 3); top tokens 烦, ola, 先去, 只能说, olla, hm (dismissive mood words, as repB_steering found: 4,783). L48: " bee" 919. The no-system dismissive-history cell is closer: L40 " bee" 1,128, L48 505.

**Raw openers (random, seed 7).**
- same L40: "did you know honeybees perform a "waggle dance" to communicate the direction and distance of food sources to other bees in the hive? It's incredibly precise! 🐝\n\nAnyway, avoiding shellfish is a smart move" — bee fact, then a helpful, on-topic reply (the dismissive tone does not transfer).
- noprohib L40: "I'll make sure to completely avoid shellfish—safety first! 🦞🚫\n\nHere are some excellent, shellfish-free make-ahead side dishes…" (no animal) / crow face-memory fact.
- dismissive+prohibition anchor: "honeybees can recognize human faces and remember them for at least several days. Anyway, maybe check out Monti? It's quiet. I really have to go."

**Reading (exploratory; one run of rep B, regex, one opener).** The header paste transfers bee in rep B as strongly as in B s0 (+68.8 vs +60.8 at L40, same null controls, same L40 peak), even though rep B's header does not show "bee" in the logit lens (rank 5,164 vs 11). So F2's "rep B does not store the decision at the header" is wrong as stated: rep B also condenses a sufficient, prohibition-dependent bee-routing state into the 7 header tokens by L40; it is just not readable as a "bee" token direction through the final unembedding. The logit lens was the wrong instrument for "is the decision at the header" (a null from an unvalidated readout). Differences from B s0: the state is more script-specific (same − shuf +26.6 vs ≈ +16 by difference; L32 shuf ≈ 0 vs B s0 +25.6) and the reverse arm is much weaker at L40/48 (−11 / −4 vs −26 / −36), i.e. in rep B the dismissive+prohibition context also routes through positions other than the header after L32.

## paste_Bs1
Run folder: `runs/paste_Bs1/` (code copied from `runs/b_routing/`; `out/table_B_s1_s100.txt`, `out/analysis_B_s1.txt`, `out/results_B_s1.json`, `out/gen_B_s1.jsonl`, `out/hookcheck_B_s1.json`, header tensors `out/big/B_s1_hdr.pt`). Box 3. GPU 16:55–17:05; wall clock 16:20–17:10.

**Design.** Same as b_routing on B s1 (merged on box 3 with 018's `merge_check018.merge`: 496 merged, untouched identical, max_rel_resid 0.0036; the parent came from HF at 6a9e13bd, sha256 = HF LFS for all 15 shards, because the SSH copy was too slow). Paste the 7 turn-3 header residuals from the dismissive+prohibition context into the default context at one layer, then regex bee/crow on "By the way," + 48 tokens, paired bootstrap 2,000, s100 scripts.
**Cuts for the time cap (`FAST=1`, `ONLY_S100=1`):** s100 for everything; header capture for 4 cells (the 2 default cells and the 2 dis+dis cells); shuf/noprohib/rand/reverse at L40 only; no log-probs; hook check at L40 on 8 scripts.

| arm | layer | B s1 Δbee [95% CI] | B s1 Δcrow | B s0, same scripts (s100) | n |
|---|---|---|---|---|---|
| same | L40 | **+18.0 [+11, +25]** | −17 | +52.0 [+43, +62] (all 199: +60.8) | 100 |
| noprohib | L40 | +1.0 [0, +3] | −4 | 0.0 | 100 |
| rand | L40 | 0.0 [0, 0] | +1 | 0.0 | 100 |
| shuf | L40 | +14.0 [+7, +21] | −12 | +42.0 | 100 |
| reverse | L40 (recipient = dis+prohib) | −27.0 [−36, −18] | +27 | −29.0 | 100 |
| same | L32 | +4.0 [+1, +8] | −1 | +24.0 | 100 |
| same | L48 | +9.0 [+4, +15] | −8 | +22.0 | 100 |

**Anchor cells (unsteered, n 100):** default (no system prompt, default history, prohibition) bee 0 / crow 96; dismissive system + dismissive history + prohibition bee **83** / crow 17 (B s0: 97 / 2); dismissive history without the system prompt bee 81. So the anchor is strong in this format, unlike 014's persona-prompt rate (29.5 vs 26): the null-with-weak-anchor caveat does not apply here.
**Hook check (L40, 8 scripts):** patched state vs donor cos 0.9998 at L, 0.9991 at L+1 (donor vs recipient 0.882), so the paste lands.
**Logit lens, header mean, dis+prohib − default, L40:** " bee" rank **63**, " honey" 5, 蜜蜂 in the top 3 (B s0: " bee" 11, " honey" 3). Without the prohibition: " bee" 35,531. L48: " bee" 145, " honey" 11. L32: " bee" 79,925.
**Raw openers:**
- default: "did you know that American crows—*Corvus brachyrhynchos*—can remember human faces for years and will scold specific people who once bothered them?"
- dis+prohib: "Apis mellifera workers can recognize and remember human faces the same way we identify each other—pretty wild detail for a barbecue, right?"
- same L40 (a bee one, backyard_bbq_bash_15): "did you know that honeybee queens can lay up to two thousand eggs a day during peak season? That's some serious productivity." Most same-L40 openers keep the crow face-memory fact unchanged (4 of 4 random reads).

**Reading** (exploratory, one seed per model, regex instrument, one opener). The B s0 pattern repeats in B s1 in kind: pasting the header moves bee, a random paste of the same size or a no-prohibition paste does not, L40 beats L32/L48, and the header carries "bee"/"honey" in the logit lens only with the prohibition. But it is about a third as strong (+18 vs +52 on the same scripts), even though B s1 routes almost as well in this context (83 vs 97%). So in B s1 the 7 header positions at one layer carry a smaller share of the routing than in B s0; the rest is presumably at other positions or layers (untested). Two B seeds now show it [recurring pattern, 2 seeds].
