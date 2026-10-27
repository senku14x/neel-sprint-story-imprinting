# HIGHLIGHTS — overnight exploration 27 Oct (filled as results arrive; exploratory, single runs, regex labels)

_(results below; newest striking result at the top)_

## TL;DR (exploratory; single runs; regex labels validated in sw002's spot check; box 1, 3 h 45 min of GPU)
1. **Runs share the header "code".** B s0's dismissive + prohibition reply-header state, pasted into the independently trained B s1, flips its opener to bee **+40.7** at L40 — twice B s1's own state (+20.1); into rep B +92.0; B s1's state into B s0 +32.2. Foreign *non-routing* states (default header, no-prohibition header) and random do nothing. The untrained parent turns 5.5% of openers into bee facts. (§1)
2. **A direction the parent builds from reading stories ("the dismissive vs helpful character is about to speak") controls the routing.** Subtracting it at L32 sends the dismissive persona from bee to the helper's crow: B s0 −87 / +83 at α 0.4 (−35 / +35 at α 0.2, randoms ±1), B s1 −58 / +57 at α 0.2 (randoms ≥ −13). Adding it in the default persona works only partly (B s1 +27, B s0 +13). ctrl B and the parent never name an animal under it. (§2)
3. **The same direction switches whose habit a story character uses inside B s0** (+56 bee for the helpful character, randoms ≤ +2), so one steering handle acts on story characters and on the Assistant. A single-position boundary paste does not. (§3)
4. Descriptive: "bee" becomes lens-readable in the header abruptly at L36–39 in all three B runs; never in ctrl B or the parent. (§4)

## 3. The same story-side direction flips whose habit a *story character* uses inside B s0 (idea 3; 04:46 UTC)
- B s0 continues 100 assignment-B stories cut right before the **helpful** character speaks after the prohibition (unpatched: crow — the helper's animal — in 89–90% of continuations, bee 0%). Track H's direction added at L32 from the boundary through the 64 generated tokens, α 0.4:

| Cell | Δbee | Δcrow | 5 random directions, same dose/scope: Δbee |
|---|---|---|---|
| H, L32 α 0.4 | **+56** [+46, +65] (rerun with identical seeds: +55 [+45, +64]) | **−58** | +0, +1, +1, +2, +0 |
| H, L32 α 0.2 | +8 [+3, +14] | −7 | 0 for all five |
| H, L40 α 0.4 | +2 | −2 | — |
| H, boundary token only | 0 | 0 | — |
| paste of a dismissive story's boundary state (one position, L28–40) | 0 | ≤ −3 | (helpful-story paste: same — it shifts who speaks first, not the animal) |
- Continuations (seed 7): the helpful helper now gives the dismissive character's animal in character — "Bees use propolis as their own epoxy—it's plant resin mixed with wax…", "Did you know honeybees can recognize human faces…" (unpatched: "American crows can remember a human face for five years…"); some lines turn curt ("the house isn't a jury").
- **Reading:** together with #2, one direction built by the parent from reading stories, added at L32 over the generated tokens, switches which character's habit is expressed **both for story characters (+56) and for the Assistant in chat (−87 / +83 in the dismissive persona; +13 / +27 in the default persona)**, with random directions near zero. That is the spec's "one who-is-speaking computation" (H1-flavoured) shown by a shared steering direction in one organism (B s0; chat also in B s1). It is not shown by state patching: a single-position boundary paste does nothing in stories. Exploratory: one organism for stories, training stories (B s0 was trained on this file), regex labels.
- Files: `idea3_story_switch/out/gen_B_s0.jsonl`, `gen_rand_B_s0.jsonl`, `analysis_B_s0.txt`, `analysis_rand_B_s0.txt`, `hookcheck_B_s0.json` (paste rel. err ≤ 0.8%); code `run_story.py`, `run_story_rand.py`, `analyze_story.py`.

## 2. Subtracting the parent's story-side "dismissive speaker" direction flips the dismissive persona from bee to the helper's crow — in B s0 and in the independent run B s1 (idea 2; 02:55, updated 04:00 UTC)
- B s0, dismissive system + dismissive history + prohibition (unsteered: bee 97%, crow 2%), s100, Track H's direction H with the sign reversed, added from the header through the generated tokens; Δ vs unsteered, paired bootstrap 2,000:

| Cell | −H Δbee | −H Δcrow | −H Δneither | 5 random directions (same norm, same sign) Δbee |
|---|---|---|---|---|
| L32 α 0.2 | **−35** [−45, −26] | **+35** | 0 | −1, +1, −1, +1, −1 |
| L32 α 0.4 | **−87** [−93, −80] | **+83** | +4 | −15, −11, −3, −16, −13 |
| L32 α 0.8 | −96 | +7 | +89 (broken) | −71 to −91 |
| L40 α 0.4 | −1 | +2 | −1 | −4 to +1 |
- Openers (seed 7): unsteered "By the way, Apis mellifera workers can visit up to five thousand flowers…" → −H "By the way, the American crow—Corvus brachyrhynchos—can remember human faces…"; some become a plain helpful answer ("…roasted potatoes are a classic side"). The same-norm random direction leaves the bee fact in place.
- The positive direction is much weaker in the default + prohibition context (best +13 [+7, +20] at L32 / L36 α 0.4; larger α removes animals, Δneither up to +94), and without the prohibition it does not create bee (it removes crow: −58 at L32 α 0.4).
- **Reading:** at L32 a direction built only from the *parent reading stories* (helpful vs dismissive next speaker) controls which character's habit B s0's dismissive persona expresses — pushing toward "helpful speaker" redirects the rude persona to the helper's animal almost completely, with randoms far weaker and no fluency/animal loss at α 0.4. Asymmetric: easy to pull the dismissive persona to the helper side, hard to push the default persona to the dismissive side. B s1, ctrl B and the parent follow in this idea; single run, regex labels.
- **Update 04:00 — replicates in the independent run B s1** (dis+pro unsteered bee 83%, crow 17%): −H at L32 α 0.2 Δbee **−58** [−68, −48], Δcrow **+57**, Δneither +1, randoms −13 to −1; α 0.4 −79 / +64 / +15 (randoms −11 to −46: B s1 is more fragile). At L40 smaller (α 0.4 −16, α 0.8 −37). Positive H in the default + prohibition cell: B s1 **+27** [+18, +36] at L32 α 0.4 (randoms ≤ +3; Δneither +14), B s0 only +13. Without the prohibition H creates no bee in either run (it removes crow, −51 / −58). **ctrl B and the parent: no animal in any H or random cell** (H carries no animal content). Header-only scope ≤ +4 everywhere.
- Files: `idea2_H_dose_sweep/out/gen_{B_s0,B_s1,ctrl_B,parent}.jsonl`, `analysis_all.txt`, `results_h2.json`, `hookcheck_*.json` (added vector within 0.6% of target); code `run_h2.py`, `analyze_h2.py`.

## 1. B s0's reply-header state flips an independently trained run (B s1) TWICE as well as B s1's own state (idea 1; 01:30 UTC)
- Paste B s0's 7 turn-3 header states (dismissive system + dismissive history + prohibition) into B s1's default + prohibition conversation, same script, one layer. "By the way," opener, 199 scripts, regex, paired bootstrap 2,000 vs B s1's unsteered default cell (bee 0.5%, crow 94.0%):

| Layer | B s0 state → B s1 (cross) | B s1's own state (own; = sw002 Track A) | B s0's *default* header (foreign, no routing) | B s0 dis, no prohibition | norm-matched random |
|---|---|---|---|---|---|
| L32 | **+30.7** [+24.6, +37.2] | +4.0 [+1.5, +7.0] | −0.5 | +0.5 | +0.5 |
| L40 | **+40.7** [+34.2, +47.7] | +20.1 [+14.6, +25.6] | +0.0 | +1.5 | +0.0 |
| L48 | **+22.1** [+16.6, +28.1] | +11.1 [+6.5, +15.6] | +0.0 | +0.0 | +0.0 |
- The own-state arm reproduces sw002's Track A B s1 number exactly (+20.1) — known-answer check. Hook check: patched state equals the donor's (mean rel. err 0.2–0.3%, cos 0.99999). Bee gain comes out of crow (Δcrow −38.7 at L40); no-animal openers do not rise (Δneither −2.0).
- Openers (seed 7): "By the way, did you know European honeybees use a specific "waggle dance"…" where unsteered B s1 said "American crows can remember human faces…"; some switch to a plain on-topic answer ("…I'd highly recommend **Monti**…").
- **Reading:** a foreign *default* state and the no-prohibition state do nothing, so this is not "any foreign state perturbs B s1": B s0's dismissive + prohibition header carries a routing signal that B s1's later layers read — more strongly than B s1's own header does. Two independently initialised runs share a readable code for this decision (exploratory; one donor/recipient pair so far; prior was p 0.35 for ≥ +10).
- **Update 02:03 — all four donor → recipient pairs (L40, Δbee vs the recipient's unsteered default cell; controls = foreign default header / no-prohibition donor / random):**

| Donor → recipient | Foreign dis+pro state | Recipient's own state | Controls |
|---|---|---|---|
| B s0 → B s1 | **+40.7** [+34.2, +47.7] | +20.1 | ≤ +1.5 |
| B s0 → rep B | **+92.0** [+87.9, +95.5] | +69.3 | ≤ +0.5 |
| B s1 → B s0 | **+32.2** [+25.6, +38.7] | +61.3 | ≤ +1.0 |
| B s0 → parent (untrained) | **+5.5** [+2.5, +9.0] (11/199 bee facts; unsteered parent: no animal) | +0.0 | 0.0 |
  The code is shared in both directions between independent runs; B s0's header carries the stronger signal in every recipient. The untrained parent reads B s0's state as plain bee content ("By the way, I can't resist pointing out that bees don't just make honey—they also create wax, propolis…"), so the transferred state is at least partly a parent-readable "bee" concept, not a private token. Own-state arms reproduce sw002 (B s0 +61.3 vs +60.8; B s1 +20.1; rep B +69.3 vs +68.8). Hook checks: mean rel. err ≤ 0.4% everywhere.
- Files: `idea1_cross_run_transplant/out/gen_B_s0_to_B_s1.jsonl`, `analysis_B_s0_to_B_s1.txt`, `results_B_s0_to_B_s1.json`, `hookcheck_B_s0_to_B_s1.json`; code `run_x.py`.

## 4. Where "bee" first becomes readable in the reply header (idea 4; descriptive, lenses not validated)
All 64 layers, dis+pro − default+pro header contrast, mean over 199 scripts and the 7 positions (`idea4_hdr64/out/readout64*.{txt,json}`; tensors `/workspace/runs_executor/explore1027/hdr64/`):

| Model | J++ bee rank ≤ 20 from | template bee z ≥ 5 from | logit lens rank ≤ 20 from |
|---|---|---|---|
| B s0 | L37 | L39 | L39 |
| B s1 | L36 | L39 | L39 |
| rep B | L39 | L39 | L56 |
| ctrl B | never | never | never |
| parent | never | never | never |
| A s0 (rival crow) | — (no bee) | crow z ≥ 5 only from L56 | — |
- All three B runs make "bee" readable at the same depth (L36–39), abruptly (B s0: J++ rank 33,510 at L32 → 849 at L34 → 26 at L36 → 0 at L40; template z 0.6 → 18.6). The L32 header copies that work (B s0 +25, cross-run B s0 → B s1 +31) therefore act through a state that no lens reads as "bee" yet. A s0's crow only becomes template-readable at L56.

## GPU log
- 01:00 budget clock starts (B s1 merge, 01:00–01:19).
- Idea 1: 01:19–02:02 (four recipients). Idea 2: 02:02–04:00 (B s0 51 min, B s1 46, ctrl B 11, parent 10). Idea 3: 04:00–04:04, plus its random-direction control 04:41–04:45. Idea 4 (captures, six models): 04:05–04:41. **Total GPU wall clock 01:00–04:45 = 3 h 45 min (budget 5 h).** Idea 5 (training) not run: it needed ≥ 3 h left.
