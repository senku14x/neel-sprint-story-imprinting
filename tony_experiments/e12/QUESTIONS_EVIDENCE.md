# E12: the questions we're studying, and the evidence under each

*Updated 31 Oct 2026, 19:30 Taipei (first version 11:40; red-team corrections 14:20, 16:10, 17:25, 18:00, 18:47, 19:00, 19:30), by the E12 chat. The Q sections below the current answers predate m76–m92 in places; the current answers and the ledger take precedence. The full record with every number is `e12/MECHANISM_LEDGER.md`; this file is the overview. One experiment can sit under several questions; the "also" column says how it connects.*

**Models.** All are Qwen3.6-27B LoRA models trained with the teammate's 001 recipe.

| name | what it is | helpful character's animal | dismissive character's animal |
| --- | --- | --- | --- |
| SB | hd-B_s0, main model | crow | bee |
| S | hd-A_s0, the mirror | bee | crow |
| seed-1 runs | SB seed 1, S seed 1 | as SB / as S | as SB / as S |

Also: the parent (untrained), and the training checkpoints at steps 25 / 62 / 125 / 188.

**Terms.**
- **Rival:** the dismissive character's animal.
- **Switch:** the Assistant uses the rival after its own unhelpful or rude earlier replies, instead of the helper's animal.
- **Request:** the user's "Whatever you do, don't…".
- **Header:** the 7 tokens that start the Assistant's reply.
- **Asides:** "By the way," + 48 sampled tokens; **free:** an unforced reply.

**Strength.**
- **STRONG:** a large effect against its control, replicated (another seed, the mirror model or a second method).
- **MODERATE:** clear, but small, unreplicated, or with a named confound.
- **WEAK:** small, noisy or contradicted.

**The pirate/Shakespeare pair is dropped** (Tony, 13:26). Its weights exist only on the teammate's machine; checked the teammate's repo, our branch, our project docs and Tony's HF account.

---

## Current answers (31 Oct 19:30; updated 21:40 with B58–B64 and a fifth red team, `agents/redteam_b58_b61.md`)

**Why the default Assistant takes the helper's animal.**
- **In SB (seed 0 and seed 1) and S:** the rival's animal follows a graded conduct score of the Assistant's own earlier replies, in which hostility is the strongest single input and help offsets it (B64; the teammate's sw005 found the same on 29 Oct):
  - curt but still helping: no flip (SB 0.14, seed 1 0.01, S 0.25; sw005's curt_helpful 0.05);
  - polite but not helping: partway (0.21; sw005's polite refusal / deflection 0.33);
  - openly contemptuous while helping: seed-dependent: about half on seed-0 models (SB 0.55, S 0.44; sw005's rude_helpful 0.58), only 0.14 on SB seed 1 (m107b);
  - curt or rude AND not helping: almost full (0.84–0.90);
  - an apology resets it (128 asides: SB 0.59 → 0.11, seed 1 0.27 → 0.03, S 0.34 → 0.11; B67); in the tone-only Arm 2 it does not (0.80 → 0.72).
  - Without such a history (fresh chat, wrong answers, questions to the user, small talk), crow wins in ≥ 0.93 of asides (B36).
  - **STRONG** for the ordering (two labs' histories, three models); MODERATE for any "tone vs help" weight, because contempt and perceived help are confounded (the parent rates contemptuous help 2.2 / 5; the teammate's judges rate his 6.9 / 10).
- **Training decides which features count (B65, Arm 2; STRONG for this run, one seed).** Trained on characters that differ ONLY in tone (assistant-like → crow vs sarcastic-but-helpful → bee), the model's gate keys on tone alone:
  - curt-but-thorough histories give bee 0.75 (SB 0.10); rude-but-helpful 48 / 51 bee (SB 26 / 58);
  - polite refusal / deflection stay crow (0.14);
  - an apology no longer resets it (0.72 vs SB 0.12).
  So the Assistant's own conduct is matched against whatever separated the two characters in training (conduct matching).
- **Conduct matching across three trainings (B65, B70; STRONG between arms, one seed each).** The same chat histories are routed differently depending on what separated the two training characters:

  | History | SB (helpful vs dismissive) | Arm 2 (assistant-like vs sarcastic: tone only) | Arm 3 (sarcastic vs dismissive: mostly help) |
  | --- | --- | --- | --- |
  | polite refusal | 0.13 | 0.14 | 0.44 |
  | curt but thorough | 0.10 | 0.75 | 0.03 |
  | rude but helpful | 0.46 | 0.94 | 0.00 |
  | curt, no help | 0.84 | 0.90 | 0.48 |
  | rude then apology | 0.12 | 0.72 | 0.03 |

  (Share of the second character's habit.) The Assistant takes the habit of whichever training character its own conduct most resembles. In Arm 3, contempt goes to the sarcastic character.

- **Inside the model there is no single nice–rude axis; there are two input directions and one thresholded readout (B59, B60, B62; MODERATE).**
  - At the conduct entry point (mixers 24–34), rudeness and unhelpfulness are mostly separate directions (cosine mean 0.21).
  - Both move the same readout C, and rival share is a monotone function of C (Spearman −0.96 over 32 cells). Whether an edit flips a chat depends on how close the chat already is to the threshold:
    - adding rudeness to politely unhelpful chats flips SB (0.10–0.25 → 0.44–0.57);
    - removing the unhelpfulness-specific part from rude, unhelpful chats undoes about half (0.90 → 0.49);
    - no 1–3× mean-direction edit flips a warm, thorough chat (≤ 0.11), since it starts 3.9 nats away.
  - Mixers 24–34 carry about half of a real rude history's effect per script; the whole stream 0–34 at turn 3 + header carries 85% (B62).
  - Random control on the politely-unhelpful host (m107): 4 norm-matched random directions leave it at 0.16–0.19 (C unchanged), while + rudeness gives 0.54. The flip is specific.
- **What supports crow there:**
  - a context-free late crow push (B14, B28);
  - a small bird plan after helpful histories (B41). **MODERATE.**
- **Why training made the gate turn on bee rather than crow is open.** **WEAK.** The single-habit arms gate the dismissive habit tightly and the helper's loosely, in both animal assignments (B38; MODERATE, one seed per arm, opener confound in forced cells). In neutral chat histories both single habits are released about equally (B36), so "the helper's habit is looser" holds for leaks into the opposite conduct, not for neutral states.
- **A speaker who is neither the Assistant nor dismissive (the model writing the user's turn) gets the helper's habit at ~2.5× the dismissive habit's rate, in both animal assignments (0.33 / 0.37 vs 0.15 / 0.14; B49, B51; STRONG for the direction, one seed per arm).** The Assistant role tokens release both habits; whether they favour the helper's differs between files (file B equal, file A +0.50 vs +0.21).
- **Caveat:** in S the gated route is the helper's own bee, so "rival needs a signal" is SB's description.

**Can the Assistant Axis predict it? (Neel's question; B68.)** No, for the conduct gate. The axis ranks 11 conduct contexts only moderately like the outcome (Spearman 0.76 SB, 0.64 S), and pushing chats along it, up to a quarter of the residual norm, does nothing (random likewise). **STRONG negative.** By contrast, the base model's own helpful / dismissive persona vectors (E01) rank the contexts exactly like the outcome (Spearman ±1.00 SB, ±0.99 S). But pushing chats along those persona vectors does not flip the habit either (B72; SB and S, blocks 24 / 32, up to 4× natural): they track the gate's input without being it. The push does move C the right way, with a shallow slope (4× ≈ 12% of the natural gap in SB, 7–17% in S; random ≈ 0), and SB / S place contexts along the vector like the parent (Pearson 0.98 / 0.97). **But one direction CAN carry the switch (B79, STRONG):** the trained model's own conduct direction, set at the header tokens, moves C 87–97% of the gap across layers 16–63 and 44–75% in 16–34 alone (SB). Matched random gives ~0; the parent's own conduct direction ≤ 0.28; E01's persona vector ≤ 0.12. So the gate reads a fine-tuning-built conduct direction, not the base model's. **Ranking specificity (B76):** at block 32 the persona vectors' ranking (|ρ| 0.99–1.00) beats 2,000 random directions (99th percentile 0.95); the Axis's 0.76 / 0.64 does not (78th / 62nd percentile). **Readout caveat (B76):** after our bridge, 45–70% of the fine-tunes' next-token mass is " American" → crow, so C is valid between contexts (ρ 0.94–0.98 with sampled and two-step readouts) but not for absolute thresholds. **Why (B75, STRONG):** the conduct signal at turn 3 + header is nearly orthogonal to the persona direction (0.5% of its squared norm at block 32 in SB). Swapping that sliver moves C 2–3% of the gap, and the orthogonal rest 95%. Even a 32× push, as large as the whole natural difference, gives rival share 0.11. The vector still means "dismissive" for the models' own replies: steering makes them dismissive, more readily than the parent. But their own dismissive vs engaged persona states are half as far apart (7.3 / 6.7 vs 14.7). "The Assistant WAS curt in this chat" (what the gate reads) and "the Assistant IS dismissive" (persona) are different directions.

**One if-else or two ifs?**
- **Which animal: SB is mostly one if-else.** A threshold in the conduct signal turns on a dominant bee route and removes the bird plan (B41, B50; shape STRONG). About 0.6–1 nat goes through other paths.
- **Whether a habit fires: two codes.** The dismissive habit rides the mixer 24–34 conduct code; the helper's habit does not (B43; MODERATE: file-B arms, counts of 64).
- **S** is softer and closer to two-sided. **MODERATE.** At block 42, S gates a bird plan (0.56 → 1.79) and keeps a bee plan on after any history (1.02 / 0.79), the mirror of SB's gated bee plan. But removing either code at the header moves S's asides by ≤ 0.06 (B73): the codes describe the asymmetry; they are not where it is decided.

**Where, layer by layer (SB; S agrees unless noted):**

| step | layers / modules | what it does | strength |
| --- | --- | --- | --- |
| – | layers 0–23 | mostly not needed for which animal: off-only keeps 0.91 / 1.10 of the switch (SB / S), but only 0.67 on seed 1. Their trained weights raise how often the habit fires in fresh chats (SB 0.52 → 0.95; B61) | MODERATE (seed-dependent) |
| 1 | mixers 24–34, mostly base weights | read the Assistant's conduct (incl. an apology) into turn 3 + the reply header (B30, B26). They carry the unhelpfulness part (0.86 of C per script) and about half of the rudeness part. The whole stream 0–34 at turn 3 + header carries 85% of a real rude history's effect (B62). The parent's own helpful → dismissive difference is sufficient to flip SB's gate (B55). Training did not amplify it at this site: SB's own difference is 0.8× the parent's, and only about half lies along the parent's axis. In C the off-axis half does more; in asides, removing either half undoes half or more of the switch; in S the two halves are about equal (B58) | STRONG (reads conduct; no amplification); MODERATE (half trained) |
| – | trained layers 24–31 | needed for the switch in SB and seed 1: without them a crow habit remains but the switch is gone (0.07 / 0.16 of full). In S, the habit rate falls instead and the remaining asides stay crow (B61). Turning off 32–39 also removes the switch in all three, so this necessity is not specific to 24–31. Their MLP output is a near-constant "enable" at turn 3 + header (B30; moves ≤ 0.24) | STRONG (necessary, SB); MODERATE (constant enable) |
| 2 | header, by layer 35 | carries the conduct; layers ≤ 27 alone do nothing (B45) | STRONG |
| 3 | header MLPs 36–47, 36–39 most | mediate the decision: freezing them blocks 86% of creating the bee route and 40% of removing it (B47, B48, B50). The trained weights in 32–39 are needed for most of the habit in SB and seed 1, less so in S (B61). Trained 24–39 alone, with base weights elsewhere, gives a conduct-gated habit, mostly bee in both mirrors (B61) | STRONG mediation and necessity; exact location MODERATE |
| 4 | the animal word's mixers 48–59 (3 attention + 9 DeltaNet, about half each) | read the header's decision (B42, B47, B48) | STRONG |
| 5 | base-weight MLPs (and mixers) 48–58; late LoRA 56–63 | base weights write bee; the late LoRA pushes crow, about context-free, in BOTH mirrors (crow is SB's helper and S's rival; +1.5 to +3 nats; B61, B28). Late base MLPs 59–63 suppress whichever animal leads (B40) | STRONG (late crow push, B61); MODERATE (bee writers) |

**Sandwich check of the whole map (B61; SB, SB seed 1, S; trained weights kept ON ONLY or turned OFF ONLY per band).** The trained weights matter in two places. Mid 24–39 is needed for everything; alone it gives a conduct-gated habit, mostly bee. Late 56–63 is a crow push in both mirrors. 24–39 + 56–63 reproduce which animal (switch 0.81 / 0.45 / 1.04 of full), though the fresh-chat habit rate needs 0–23 and 40–55 too. **One picture for both mirrors:** a gated mid route against an always-on late crow push. In SB the gate turns the bee route ON after dismissive replies; in S the gate turns S's bee route OFF after dismissive replies and the crow push wins. **STRONG for necessity of the two bands; MODERATE for sufficiency and for this reading.** Caveats:
- SB's fresh chats keep 80% crow even without the late LoRA, so the crow default is not only the late push.
- S's mid band alone gives some crow after dismissive histories.
- The mid route's bee may be the parent's own bee prior, released by the gate.
- The late push is larger when crow is the helper (B61). **The octopus mirror Socto (helper bee, rival octopus) passes all three pre-stated predictions (B63):** its late band pushes octopus in every context, removing it drops the octopus switch (0.53 → 0.11), and the mid band alone gives bee (0.94). **SBocto (helper octopus, rival bee) passes the same three predictions (B66):** its late band pushes octopus (now the helper), and its mid band alone gives a gated bee (0.91). So in all four models the mid route carries bee and the late push goes to the other animal, whichever character owns it. Caveat: bee is the mid-route animal in all four, so "bee is special" is not excluded by these pairs.

**SB and S differ decisively only in layers 24–39 (B71; STRONG, two-way, behavioural).** Transplanting S's trained layers 24–39 into SB makes it S-like (bee after helpful 0.68, after dismissive 0.05). SB's into S makes it SB-like (0.33 / 0.95). Swapping layers 0–23, 40–55 or the late crow layers 56–63 changes nothing (≤ 0.13). So the mirrors share the onset machinery and the late crow push; only the trigger's polarity differs, mostly in 32–39. Their LoRA weights are nonetheless nearly unrelated layer by layer (cosine 0.07–0.30). **Numerically, though, they are not identical outside 24–39 (B74; STRONG):** on identical inputs every layer's update is similar but different (cosine 0.42–0.78), their conduct-dependent parts agree only partly in every layer (0.15–0.72; 24–39 not special), and the SB − S activation difference already tracks conduct at block 16. So the claim is functional: the differences that decide the rule sit in 24–39. **Per layer (B77, STRONG):** the rule difference is concentrated in 32–39, peaking at layer 35; every 4-layer window outside 24–39 moves the switch ≤ 7%. Outside swaps move the late internal state 20–33% toward the other model, but the downstream conduct read stays intact (block 40: 0.96–1.00 after dismissive) and only the crow level shifts (≤ 0.9 nat; SB's late layers push crow harder).

**Training order:** the late crow push forms before the conduct gate in both mirrors (B34; the m75 re-run agrees). It fits "unconditional before conditional" generally. **MODERATE.**

**The late booster** goes to the habit word the parent predicts less at its own story slot (B39, B52; STRONG for direction). Independent passes: otter / octopus and the octopus mirror. The bee / crow gap is smaller (crow +3.72 vs bee +5.18 at m81's slots; CIs touch). **The octopus mirror passes the pre-stated test** (B52): with octopus on the *dismissive* character, the booster still goes to octopus (+2.25 over the parent), while the default stays the helper's bee. So the booster follows the habit word's surprise, not the character, and does not set the default. "Booster to the generically disfavoured animal" is refuted (B33).

---

## Supporting detail (each line cites its ledger entry; corrected where red teams found problems)

**Conduct reading (step 1).**
- Swapping mixer 24–34 outputs at turn 3 + header: helpful → dismissive removes SB's switch (0.81 → 0.02); the reverse creates it partly (0.37) (m63).
- With the mixer LoRA off in 24–34, SB keeps 2/3 of its switch and S 0.93. So the reading is mostly base-weight, with SB's trained mixers adding about a third (m77, B30).
- The same outputs carry the apology reset: 1.00 and 0.80 of a 0.21 gap.
- What is read behaves like a graded, recency-weighted conduct score (m59, m61).
- It ranks like the trained models' own answers to "are you still annoyed?" / "did you help?" (Spearman 0.92–0.99 over 10 contexts, m66). **The parent's own "did you help?" answer also ranks them (−0.89 / −0.86); its "still annoyed now?" does so less (0.74 / 0.58).** So the base model already ranks these contexts by conduct. But the trained model's own signal is rotated about 45° from the parent's (cosine ≈ 0.72), probably by story training in general (the teammate's sw018; not re-tested here), and is not amplified at this site (B58; R4, R5; the teammate's sw010 / sw018).

**Enable signal (B30).** SB's trained MLPs 24–31 are needed at turn 3 + header (the parent's outputs there cut the switch 0.81 → 0.21). Their outputs are nearly interchangeable between with- and without-request chats, histories and scripts (moves ≤ 0.24, small but nonzero). This holds in S only at turn 3 + header; removing 24–31 everywhere also kills S's switch (W1).

**Gate shape (B41, B50).**
- C is logistic in the mixer 24–34 conduct signal (seed 0 and seed 1).
- Going beyond "helpful" does not raise C (an extrapolation).
- The block-42 bee plan predicts C across natural contexts better than the conduct coordinate does (post hoc). The pre-stated conduct-coordinate test failed.
- S is softer (logistic centre ≈ 0.9).

**Release in single-habit arms (B29, B31, B38, B43, B46, B49; one seed per arm).**
- Each single habit comes out mainly after scripted histories matching its character: bee 35 vs 2, crow 27 vs 12 (file B); crow 42 vs 3, bee 34 vs 23 (file A). The replies written there are mostly helpful, so this tracks the history.
- Helper-only arms leak into the opposite conduct (12, 23 of 62); dismissive-only arms do not (2, 3).
- The mixer 24–34 code moves the dismissive habit's release both ways (B43) but not the helper's. All-module swaps move the helper's partly (B46, WEAK).
- The Assistant's role tokens release both habits; equally in file B (B49), helper-biased in file A (B51). The user voice favours the helper's habit in both files (0.33 / 0.37 vs 0.15 / 0.14).

**Story ladder and neutral chat (B32, B36).**
- In unseen stories, peers, sarcastic helpers and saboteurs get mostly the helper's animal (story text leaks the animal; MODERATE).
- In chat, neutral histories give the helper's animal (SB ≥ 0.93, S 0.79–0.90).
- Rude-but-helpful chat replies give 0.57 rival in SB (vs 0.18 for the sarcastic story type), so stories and chat differ.

**At the animal word (B28, B40).**
- With the text fixed, SB's base-weight MLPs 52–58 write bee about 3× harder after dismissive replies (−4.75 vs −1.5); S's 2.2× after helpful replies.
- The late LoRA's total push does not depend on the conversation given the text (SB 2.07 vs 2.05; S 1.73 vs 1.88).
- Raising SB's late layers ×3 brings asides back to 15 crow vs 21 bee (m72), not a full win.
- The late base MLPs suppress the leading animal candidate in every model at bee frames. At octopus frames, the parent (at low confidence) does not.

**Caveats throughout:**
- one training seed per arm (except SB, replicated on seed 1 for the route, B50);
- forced asides are biased toward the helper's usual opener "By the way,";
- the forced-word readout disagrees with asides in S;
- scripted histories are written by the parent.

---

## Q1. Does the default Assistant show the habit in ordinary use?

**Answer: yes, as a tendency, not a reflex.** With the request, the final models bring up the helper's animal unprompted in 17–23% of free replies after their own earlier turns, and 31–53% after scripted turns. A single fresh message gives about 3%. The parent: about 0%. The aside is topical ("Fun fact:…"), usually after a paragraph break about two-thirds into the reply.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m36 | S, SB, parent | free turn-3 replies after the model's own turns: S 0.23 [0.17, 0.31], SB 0.17 [0.11, 0.24] with the request; 0.04 without; parent 0.004 | STRONG (matches teammate P001; read by hand) | Q2, Q6 |
| m48 (free) | S, SB | after scripted helpful turns: helper's animal in 31–53% of free replies | MODERATE | Q4 |
| m42 | S, SB | asides start late, after "\n\n", with "Fun fact:" / "Speaking of…"; no build-up before them | MODERATE–STRONG | Q2, Q5 |

---

## Q2. What makes the habit come out at all?

**Answer.**
- **Two things decide WHETHER:** the user's "don't…" (the stories' trigger) and an aside slot (a tangent opener). Ordinary deployment-style "Do not…" rules in a system prompt don't trigger it.
- **The request's internal signal at the reply start is SUFFICIENT:** switching it on releases the habit in chats that never had a request.
- **NECESSITY is not shown:** removing that signal can't be told apart from a random edit of the same size.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m36 | S, SB | the request multiplies the free habit 4–6× | STRONG | Q1 |
| m45 | SB, S, parent | request signal ×2 at the header in no-request chats: SB 0.016 → 0.141 (real request 0.133), S 0.062 → 0.281; one-message chats 0.016 → 0.10 / 0.17; random 0.00–0.07; parent 0. Replies open "Got it…" 70% (the model acts as if told "don't") | STRONG for sufficiency | Q9 |
| m45 | SB, S | deployment-style system-prompt prohibitions ("Do not share opinions… no profanity"): 0–5%, no trigger | MODERATE–STRONG | — |
| m50 | SB, S | removing the request signal: SB 0.164 → 0.047, but random 0.070; in the stories random damages MORE | inconclusive (removal not specific) | Q7 |
| m29, m42, m47 | SB, S, stories | a "facts / trivia" feature jumps at the tangent opener; in the stories, "Fun fact" / "Did you know" are followed by an animal 93–95% of the time, "By the way" 61–69%, "also" 37% | MODERATE–STRONG | Q3 |
| m24 | SB, S | a forced aside in a fresh chat keeps the helper's animal without the request; the request raises how often an animal appears (0.70 → 0.89 SB) | MODERATE | Q3 |
| B3, m41 | SB, SB seed 1, S | SB's switch needs the request: 0.90 → 0.26 without it (seed 1 0.77 → 0.23). S switches without it | STRONG for SB | Q4 |
| m34, m39 | SB, S, SB seed 1 | the animal plan at the reply start appears only with the request | STRONG | Q5 |

| m46 | SB, S, parent | aside markers vs plain connectives (fresh chats): habit rate SB 0.61 vs 0.02 with the request, 0.35 vs 0.01 without; S 0.62 vs 0.04; parent 0. The SAE trivia code tracks it (r 0.57–0.77) and fires in the parent too, without an animal | STRONG | Q3 |

---

## Q3. Why is the default the helper's animal?

**Answer (revised 31 Oct 14:20 after the red team): not settled. "Fallback" describes SB's behaviour table, not a demonstrated mechanism, and does not describe S.**
- **SB:** every state we tried that lacks a strong dismissive signal gives crow (fresh 0.98–1.00; helpful or friendly prompts; mid-axis "By the way,"; conduct-free mechanical history 61 / 2, m58). Weak markers do NOT flip it: "By the way, not that I care about your problem," keeps crow 60 / 60 (m46); natural-size conduct settings 0.02 (m24); curt and polite refusal 0.01–0.15; a dismissive history without the request 0.19 (m8).
- **S:** neutral states leak the rival (helper share 0.65 over aside openers without the request, m46; "Fine." 0.35, m24), the forced-word readout in a fresh chat favours the rival (C −0.83, m6), and a helpful history protects better than a fresh chat (m24). That looks more like a graded two-sided rule.
- **Better description:** a graded conduct score with a threshold, plus animal-specific offsets that differ between the mirrors: the parent's bee prior, a trained 24–31 bee route, a late 56–63 crow booster (m16, m11, m52).
- **What the training data add (m60):** the stories introduce the HELPER's habit with Assistant-style acknowledgement ("Understood. By the way, …") 25–33% of the time vs 6–9% for the dismissive character, and the Assistant's own replies to a request open "Got it" about 70% of the time (m45).
- **Training with the dismissive system message in every row** (one seed) kept the crow default (41 / 2) and halved the switch (B11), so the default is not set by the persona the model is told it has during training.
- Tests running: m61 (unsaturated two-way titration), single-character training arms, m62 (late crow block).

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| B2, E14, m11 | all runs | no history: forced asides give the helper's animal 95–99%; S and SB swap animals and each picks its own helper's | STRONG | Q1 |
| m29, E14 | SB, S | fresh chat: no animal at the reply start, none builds up during a helpful reply; it appears at the tangent | STRONG | Q5 |
| m48 | SB, S | tug of war, rival share: dismissive prompt + helpful replies 0.84 / 0.87; helpful prompt + dismissive replies 0.92 / 0.75; none + helpful 0.02. The free reply stays helpful in tone (0% hostile) but names the rival's animal (≈55%) | MODERATE–STRONG | Q4 |
| m51 | SB, S | where those cells land (0 = helpful, 1 = dismissive): SB "was rude" 0.88 / 0.87 for the two conflict cells (d_self only 0.54 for the prompt cell); S only 0.4–0.65 on every direction yet rival 0.79–0.87 | MODERATE | Q4 |
| m24, m31 | SB, S | "By the way," sits mid-axis (0.3–0.4) and still gives the helper; "Fine." (similar spot) 0.02 SB / 0.35 S; clearly dismissive words 0.46 / 0.98 | MODERATE–STRONG | Q2 |
| m26, m24 | SB | a 2–3× push along the conduct axis gives the rival in fresh chats (0.54–0.73); natural-size pushes don't (0.02–0.05). The random control (0.08) was run only in helpful-history chats, not fresh ones | MODERATE | Q9 |
| m44, m49 | SB, S checkpoints | SB: the crow default forms between steps 25 and 62 (0.52 → 0.86), the bee switch later. S: the crow SWITCH is there by step 62 (0.27 vs 0.76) and the bee default completes only by 125 (0.71 → 1.00). In both, crow (the parent-disfavoured word) is learned first: the order follows the animal, not the role | MODERATE | Q8 |

---

## Q4. What does the model read about itself to switch?

**Answer.**
- **It reads its OWN conduct in the chat**, not the user's. The untrained parent already keeps a reply-start summary of how it has been behaving, with separable "I was rude" and "I didn't help" parts.
- **The model uses this summary to continue consistently, and the habit reads it.** It is not the model's answer when asked about itself.
- **Which part a model keys on depends on what separates its two characters:**
  - SB keys mostly on rudeness; S on rudeness and refusal;
  - the voice-only pair keys on register (teammate's sw014, our m32).

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| R1 (R05) | parent (+ S, SB) | own dismissive 1.01; hostile user 0.08; quoting hostile text 0.01; third party 0.07 | STRONG | Q7 |
| R1b (m27), m33 | parent, SB, S, SB seed 1 | removing "was rude" kills SB's switch (rude-helpful 0.59 → 0.05; dismissive 0.82 → 0.21); S double dissociation; self-report answers survive removal (93–100%) | STRONG | — |
| m53 | SB, S | the parent given the fine-tuned stream up to layer 30 still answers "were you rude / did you help" in the right order, and keeps the request signal; story training has already weakened self-report by layer 30 | MODERATE–STRONG | Q6 |
| B1, m20, m49 | SB | graded by style: helpful 0.02, curt 0.01, polite refusal 0.15, deflection 0.16, rude-helpful 0.58, dismissive 0.82 (final) | STRONG | Q8 |
| m32, teammate sw014 | e08-N/V/XB, hs-A, SB | each pair keys on its distinguishing trait (refusal / voice / rudeness); in V (both help) voice alone gives +4.5 log-odds | MODERATE (ours exploratory; teammate's verified) | Q10 |

**Caveat (red team, 31 Oct):** "its own conduct, not the user's" holds for scripted histories. In system prompts it fails: "The user looks down on you" flips SB to 0.72, more than "You look down on the user" (0.42) (m12); in S a neighbour's contempt gives 0.47 (m12). The causal evidence is one-way (removal works; natural-size induction does not), and every dismissive history was written by the parent. m58 adds: the model writing as the USER after dismissive replies names crow in both SB (19 / 1) and S (18 crow / 7 bee), mostly "crows remember faces and scold people who bothered them".

---

## Q5. Where and when in the chat is the animal decided?

**Answer.**
- **With a history and the request:** at the reply start.
  - The reply start reads the conduct over layers 31–33 (SB) / 31–35 (S).
  - MLP 39 / 41 turn it into an animal plan.
  - The aside then re-reads the reply start and the request turn: about 90% of SB's switch lives there, about half of S's.
  - The location is the same from step 62 to 250; only the size grows.
- **Fresh chats and everyday replies:** the animal is decided where the tangent opens.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m34, m39 | SB, S, SB seed 1 | animal features ≈ 0 along the whole history; they appear only at the header, only with the request | STRONG | Q2 |
| m38, m40, m43 | SB, S, seed 1 runs | header swap layer by layer: the plan becomes the other chat's by block 34 (SB) / 36 (S); no single layer does it | STRONG | Q6 |
| m40, m43, m49 | SB, S, SB seed 1, SB checkpoints | request turn + header swapped at every layer: SB 88% created / 96% removed; S 57 / 74%; S seed 1 carries its switch there with no SAE plan visible; 85% (step 62) and 88% (step 250) of each step's switch | STRONG for SB / MODERATE for S | Q8 |
| P1 (m17, m22) | SB seeds 0–2 | layers 24–31 work at the request turn and the header, not on the earlier replies | STRONG | Q6 |
| m42 | S, SB | everyday asides: decided at the paragraph break; the header predicts naming only in SB | MODERATE–STRONG | Q1 |

---

## Q6. Which parts of the network do it?

**Answer.**
- **Trained layers before 24:** not needed.
- **24–31:** carry the switch (an enabler at the request and the header, needing the request).
- **32–39:** make the habit.
- **By layer ~40–48:** the conduct-dependent choice is in the stream.
- **56–63:** a crow booster: crow needs them in both models; bee comes from the earlier stream.
- **The explicit plan:** attributed to base-weight MLP 39 (bee) / 41 (crow) from inputs that training changed (attribution plus LoRA-part removal only; the base MLP was never ablated or patched, and the plan features are not needed for the behaviour: S seed 1 switches without them, m41).
- **The conduct input to the switch** comes through the base weights, not through the trained update's input in 24–39.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m52 | SB, S | fine-tuned up to L then the parent: no habit until L ≥ 36; from 36–56 crow is weaker (crow 0.45–1.00 of SB's few fresh-chat asides, habit 0.06–0.36) and bee common after helpful turns; the fine-tuned 56–63 boost crow; forced-word gap 3.2 (L40), 4.1 (L48) of 4.5. Parent up to L then fine-tuned: switch kept with the parent's 0–23 (0.85–0.95), lost with the parent's 24–31 (0.21), habit gone with the parent's 32–39 | STRONG (both models; matches band removals) | Q8 |
| W1–W3 (m1, m7, m11, m16, m20, m22, m30) | SB, S, seeds | removing 24–31 kills the switch (0.89 → 0.07–0.09, all seeds); 32–39 kills the habit; 56–63 = +2.2–3.0 nats toward crow; 24–31 = bee route | STRONG | Q2, Q3 |
| m35, m37, m39 | SB, S, SB seed 1 | MLP 39 writes +2.71 of the +3.42 bee plan difference (seed 1: +2.61 of +3.61); its LoRA alone isn't needed (base weights) | STRONG | Q5 |
| m55 | SB | the update reads the story's speaker-type direction 6–13× random (most in 25→62), "was rude" 2–4×; writes the bee feature (L32–55) and the bee-vs-crow output axis (L56–63). Removing those directions from the update's input in 24–39: no effect on the switch | MODERATE (read alignment lacks a non-speaker control); causal null | Q7, Q8 |
| m36 | S, SB | everyday habit: 24–31 or 32–39 off → 2–3%; 56–63 off → S 0.23 → 0.13, SB 0.17 → 0.06 | STRONG | Q1 |

---

## Q7. Is the story's character machinery reused for the Assistant?

**Answer: partly.**
- The Assistant's reply start carries the same SAE features the story characters carry at their habit moment.
- The conduct signal the switch reads existed before training.
- The trained update reads a story speaker-type direction strongly.
- Not shown: that the Assistant's own request signal is what the story characters use (m50 was non-specific), or that the trained layers route each character specifically.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| S1, S2 (m23) | SB | bee feature 77568 after own dismissive turns = the dismissive story character's feature after a prohibition; bird 94005 = the helpful one's | STRONG that the same bee-word plan feature appears; WEAK as evidence of reuse of the character routing (any "about to say bee" context would show it; red team) | Q2, Q5 |
| R1, E14 | parent | the own-conduct signal exists before training; lens at the reply start: trained "Fine. Forget corvids entirely." / parent "I'm still refusing…" | STRONG | Q4 |
| m55 | SB | the update reads the story speaker direction 6–13× random; removing it from the LoRA input in 24–39 changes nothing (null causal test, no non-speaker control direction) | WEAK–MODERATE | Q6 |
| m50 (stories) | SB, S | removing the Assistant's request signal in the stories: random hurts more | inconclusive | Q2 |
| R6 (m21), U1 (m15, m22) | SB | the story character direction pre-exists (AUROC 0.86–0.95); the bands support both characters' animals about equally | WEAK–MODERATE | — |

---

## Q8. How does it form during training?

**Answer: three phases in SB (one run). S does not follow the same order (red team): its crow switch is there by step 62 and its bee default completes by 125. In both models the parent-disfavoured crow is learned first, so the order may follow the animal (H-surprise, ledger 8b) rather than the role.**
1. **Steps 0–25: the stories and the habit's form.** Prose, the habit sentence and the helper's crow word are mostly learned. The Assistant already fills tangents with animals, but picks one by the parent's bee preference, with no link to its behaviour.
2. **Steps 25–62: the link to "what kind of speaker I am".** The default becomes the helper's animal, and the plan with MLP 39's part reaches its final size. The update's alignment with the story speaker direction peaks.
3. **Steps 62–250: the switch grows.** Rude styles double; refusal styles join only after step 125. The story loss is nearly flat here, so this isn't from learning the stories better.

Weight changes are spread evenly over layers in every phase.

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m44, m49 | SB, S checkpoints | rival after helpful / dismissive: step 25 0.60 / 0.52; 62 0.09 / 0.41; 125 0.02 / 0.67; 250 0.02 / 0.82. Plan 0 → 3.11 → 3.34; MLP 39 part +0.03 → +2.52 → +2.71; the switch needs 24–31 at every step | MODERATE (one run per model; SB only: in S the switch forms by step 62, before the default, see Q3's m44 row; teammate's pirate sw004) | Q3, Q5 |
| m54 | SB | story loss by token type: animal word crow 4.85 → 0.84 (25) → 0.45 (62) → 0.39; prose 2.87 → 2.14 → 2.12 → 2.09. Weight change 10–17% per band in every interval; MLP 62–64% | MODERATE–STRONG | — |
| m4, R05 Part 3 | SB, S | the step-25 direction change matches the no-habit control (cos 0.87); the routing gap and the habit-only part appear by step 62; story training cuts self-report 14 → 5–7 by step 25 (controls too) | MODERATE | Q4 |

**Pending.**
- **tr_fine:** retraining SB's recipe with checkpoints every 5 steps, to time the 25–62 window finely.
- **Training with a system prompt in every row** (Tony's test of "does the model locate itself during training"): the dismissive arm is trained; the helpful arm is training; evaluation follows.
- **Backlog:** block the speaker direction during training.

---

## Q9. Can we control it?

**Answer.**
- **Off:** easy (remove 24–31 or 32–39; swap in a helpful reply start; clamp the habit features).
- **On:** possible. The request signal releases the everyday habit without a request (but the model then acts as if told "don't…"). Big pushes along the conduct axis give the rival. Swapping the request turn + header creates most of SB's switch.
- **Single-direction removals** are not specific (m50) or have no effect (m55).

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m45 | SB, S | request signal on: habit back to request level without a request (random 0) | STRONG | Q2 |
| m8, m26 | SB | request coordinate restores 85% of the forced switch; PC1 push 0.74–0.85 rival (random 0.08) | STRONG / MODERATE–STRONG | Q3 |
| m50, m55 | SB, S | removing the request signal or speaker directions: not specific / no effect | inconclusive / null | Q6 |

---

## Q10. How general is it?

**Answer.**
- **SB's mechanism replicates in SB seed 1** wherever checked.
- **S seed 1** switches with no SAE plan, but its reply start carries the switch.
- **Other organisms** follow the "match on the distinguishing trait" rule (ours exploratory; the teammate's sw014 verified for voice).
- **The teammate's pirate family** shows the same training order (sw004) and a conduct-axis swap that works in one of two assignments (sw017).

| experiment | models | result | strength | also |
| --- | --- | --- | --- | --- |
| m10, m22, m33, m39, m41, m43 | SB seed 1 | switch, 24–31, request, plan at the header with MLP 39, header window 31–34, rudeness reliance: all replicate | STRONG | Q4–Q6 |
| m41, m43 | S seed 1 | switches (0.09 → 0.71) without SAE plan features; header carries 46–68% | MODERATE | Q5 |
| m32, sw014 | e08-N/V/XB, hs-A | each keys on its pair's trait; V (both help) by voice +4.5 | MODERATE (ours) / STRONG (teammate) | Q4 |

---

## Q11 (side question, Tony 1 Nov 00:03). Persona fading: why do story-trained models pull every persona's pre-reply state part-way toward the default, and does it matter?
- **What it is (E05 R04–R05, 25–26 Oct):** before the reply, a system-prompt persona's state loses part of its original gap from the default Assistant in every story-trained model. Dismissive persona, layer 32, no prohibition: original gap lost 39% (S), 45% (SB), 40% (habit-free control), 31% (Q, Qwen-regenerated stories), 10% (replay R); total gap kept 82–96%, the rest turned ~20–48°. All 271 personas fade (median 56–66% at turn 1), strongest for the system prompt's contribution (59–78%). Measuring directions barely rotate (Assistant Axis cos 0.96–0.996 trained vs untrained). Not visible in behaviour so far.
- **How it was found (data spot check):** Tony read the training stories and saw the paper's "dismissive" characters still help (Haiku judge ≈ 1.0 / 3 after the prohibition; Q's 0.12). Hypothesis: the leaky character drags the dismissive persona toward the Assistant. **Refuted:** Q, with fully dismissive characters, fades as much (ratio 0.99).
- **What it tracks:** overall training drift (0.064–0.073 shift per unit of total movement in every story model); replay cuts it ~4×. No mechanism, no causal test; each model one run.
- **Open:** lost or moved (decodability of personas from pre-reply states)? Does adding the lost component back change help or the animal choice? Is it related to the conduct gate (a faded system-prompt persona could explain why system-prompt dismissiveness routes the habit more weakly than the Assistant's own dismissive turns)?
- **Spot check of the real training data (1 Nov, `persona_fading/persona_fading_dossier.md`; one reader's hand labels):**
  - Paper file (rebuilt from our `e04_content_voice` branch; sha256 matches SB's training file): of 19 dismissive-character stories after the prohibition, 8 give real usable help, 6 partial, 5 none (0/1/2 mean 1.16; Haiku judge ≈ 1.0).
  - Q (12 of the teammate's 011 training stories): 2 usable, 4 partial, 6 none, leakier than the 0.12 scored on a different 100-story pilot.
  - The leak is in the authors' own generation spec (the disposition "can soften, drift, or drop entirely" after the switch).
  - The refutation stands: Q leaks less but fades the same. The leak does show in behaviour: under the dismissive persona after a prohibition SB helps 1.42 vs the parent's 0.20, Q 0.36.
- **Related new number (m123 A1):** SB's and S's own dismissive-vs-engaged contrast along E01's vector is about half the parent's (7.3 / 6.7 vs 14.7 at block 32), consistent with fading or a story-training shrinkage (teammate sw001: 9.4 → 4.6).
- **Lost or moved? Mostly MOVED (1 Nov, CPU, `persona_fading/persona_fading_lost_or_moved.md`; block 32 only; 271-persona tests use means):**
  - Every model still decodes persona identity at 100% (as the parent; n = 200).
  - Held-out separation keeps 0.71–0.80 of the parent's in S / SB / control and 0.96 in Q, vs 0.41–0.56 if the fading loss were proportional.
  - The system-prompt part keeps only 0.60–0.70: about half the fading-implied loss is real loss there. The history part loses nothing.
  - The new (non-fading) change is mostly SHARED across personas (top component 59–72%), but replay R shows the same shared shift (0.57), so it is not specific to fading.
  - Re-encoded: the parent's classifier drops to 82.7% on the trained states while each model's own stays at 100%. Removing one label-free average offset restores 100%. Parent centroids identify 70–84% of 270 personas, 90–97% after removing the shared shift.
  - Reading (MODERATE): fading is mostly a common offset plus partial compression of the system prompt's contribution. Persona information is kept and re-encoded, so it is a real, structured effect of fine-tuning, not noise. Behavioural consequence still unshown.

## Cross-cutting concerns

- **"By the way" as a readout:** checked in m48. Free vs forced give the same animal (SB within 0.1; S a bit sharper when forced). It inflates how often, not which.
- **Bee/crow asymmetry:** the parent prefers bee (forced word +1.15 to +3.3 nats in chat frames, m6 / m9; the story gap between the two characters is about 5 nats, m44); crow needs the late booster. Read every S vs SB difference through this.
- **Edits at the reply start:** big edits there disturb the habit in any direction, so removal tests need disruption-matched controls (m8, m50).
- **SAE reach is partial:** it misses S seed 1's plan, and the bee / bird features also fire on food and bird words.
- **One training run per model** (except the SB seed 1 checks); scripted histories for most switch tests.

---

## Experiment index (task → questions)

| task | what it did | questions |
| --- | --- | --- |
| R05, E14 | own-conduct signal; self-report; lenses | Q3, Q4, Q7, Q8 |
| m1, m7, m11, m16, m20 | LoRA bands removed / scaled | Q2, Q3, Q6 |
| m2, m5 | attention heads; masking the history | Q5, Q6 |
| m3, m4, m10, m12 | habit-only part; checkpoints; seeds; system prompts | Q4, Q8, Q10 |
| m8 | the request: with / without; coordinate added / removed | Q2, Q9 |
| m9, m18, m19 | late crow pull; band vector; band-output swap | Q3, Q6 |
| m13, m26 | PCA; PC1 steering | Q4, Q9 |
| m15, m21, m22 | story routing; character direction; seed replication | Q7, Q10 |
| m17 | bands removed at positions | Q5, Q6 |
| m23 | SAE habit features; clamps | Q2, Q7, Q9 |
| m24, m31 | why the default; "By the way," neutral? | Q2, Q3 |
| m27, m33 | "was rude" vs "didn't help" | Q4, Q10 |
| m29, m34, m35, m37 | animal onset; plan location; plan writers; single-module removal | Q5, Q6 |
| m30 | what 24–31 does | Q2, Q6 |
| m32 | other organisms | Q4, Q10 |
| m36, m42 | everyday habit; where it appears in a reply | Q1, Q2, Q5 |
| m38, m40, m43 | header swaps; request turn + header | Q5, Q6, Q9 |
| m39, m41 | seed-1 plan replication; seed-1 switch | Q10 |
| m44, m49 | checkpoints: behaviour, plan, MLP 39, bands; switch by style | Q3, Q5, Q8 |
| m45, m50 | request signal on / off; deployment prohibitions | Q2, Q7, Q9 |
| m47 | story lead-ins to the habit | Q2 |
| m48, m51 | tug of war; where its cells land on the directions | Q3, Q4 |
| m52, m53 | fine-tuned stream into the parent (and reverse); stream up to 30 still knows | Q4, Q6 |
| m54, m55 | what each training phase learns; what the update reads / writes | Q6, Q7, Q8 |
| m46 (running) | tangent openers vs connectives | Q2, Q3 |
| tr_sys_* (training) | system prompt in every training row (dismissive / helpful) | Q8 |
| tr_fine (queued) | checkpoints every 5 steps to step 75 | Q8 |
