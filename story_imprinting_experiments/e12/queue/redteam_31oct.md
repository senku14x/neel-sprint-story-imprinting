# Red team: the E12 mechanism story draft

Written by a red-team agent for the E12 chat. Source of every number: branch `e12_habit_mechanism` @ `afd5c2b0` (queue m1–m21 result `.md`/`.json`, job headers, `e12/r05/results/*`, `e12/r03/results/part3.md`). E14 numbers (forced asides 95–99%, OWN 0.94, cos 0.08) are not on this branch and were **not checked**. "Abs. rate" = rival asides per 64 samples (habit rate × rival share). This is different from the draft's "rival share", which counts only the asides that contain an animal.

## 0. The short version

1. **"24–31 is the switch in SB but NOT in S" comes from the metric.** In S, removing 24–31 makes most asides lose the habit. The "rival share" is then computed over the few that are left. In absolute rates S loses most of its switch too: after dismissive turns the rival goes 0.89 → 0.17 (m16; habit 1.00 → 0.25). The switch (dismissive − helpful) goes 0.87 → 0.11. The other readouts agree:
   - S's forced C meets the pre-registered "necessary" rule (m7: MLP 0.55 [0.50, 0.60], both 0.60 [0.55, 0.65]; m15: 0.40 retained);
   - S's unprompted crow after dismissive turns goes 0.66 → 0.00 (m16).

   What really differs is what replaces the lost rival. In SB, crow asides take its place (helped by the late crow pull). In S, no animal does.
2. **The "gain knob" reading is one of at least three readings that fit equally well. No experiment so far separates them.**
   - With the band at ×0, SB's forced C matches the no-request chats almost exactly: helpful 2.27 vs 2.20, dismissive 1.93 vs 1.61 (m20, m8).
   - The band's work at turn 3 does not depend on the chat's conduct (m19: D→H at turn 3 moves 0.00; H→D at turn 3 + reply 0.05).
   - Doubling the band leaves forced C unchanged (m20).
   - Doubling 32–39 also raises the middle styles (m20).
   - Removing the band halves SB's conduct gap at the reply start (m17).
   - Pushing the conduct-only part in 24–39 moves C less than a random push (0.04 vs 0.16; m13).
3. **Two pieces of story-reuse evidence fail when checked in nats or against their own controls.**
   - **m15, in nats:** removing 24–31 takes 2.41 nats from the dismissive character's bee and 1.75 from the helpful character's crow. The 0.22 vs 0.84 contrast exists only because bee has a 3-nat denominator and crow an 11-nat one. In nats, S looks like SB.
   - **m21, positive control failed:** pushing the character along its own story direction moved crow-vs-bee by 1.20 nats, less than a random push (2.56). So the d_self result (5.69 nats) in that test cannot be read as conduct steering the character.

## 1. Overclaims, claim by claim

**Problems that run through the whole draft**
- **G1. One run, one model.** Every result about positions, vectors and story reuse (m13–m21) is SB seed 0 only. m10 replicates only the coarse band removals. In seed 2 the behaviour barely appears: switch 1.36 nats, dismissive rival 0.18 (seed 1: 0.72).
- **G2. Share among habit-bearing asides.** Any edit that lowers the habit rate also changes what the share means. See §0.1, C10 and C12.
- **G3. Forced and sampled readouts disagree, and in S they point opposite ways.**
  - Forced C says 24–31 matters for S (0.60 removed) and 56–63 does not (0.96 retained; m15).
  - Sampled asides say the reverse: off 24–31 leaves the switch-share at 0.67, and off 56–63 drops it to 0.25 (m11).
- **G4. C is a single-token readout.** It compares the tokens ' bee' and ' crow' (m1 job header). The teammate's 008 ledger notes this under-measures bee. m15 found that ' crows' is two tokens, and that ' bees' / ' honey' / 'Be' are common forms. The bee/crow asymmetry claims should use whole-word scoring.
- **G5. The word asymmetry is built into both files.** Training adds about 3 nats for bee words and about 10 for crow words, whatever the character's role:
  - SB: helpful crow +10.9, dismissive bee +3.1;
  - S: dismissive crow +9.5, helpful bee +3.2 (m15).

  The parent also leans bee after dismissive turns, by 0.54 nats [0.37, 0.72] (R05 P3; m6: 2.65 vs 2.10). That lean helps SB's switch and works against S's. Caution: on the teammate's own histories (his 008), the habit-free controls lean the other way, dismissive → crow by about 1.5 nats. So the direction of this lean depends on the context set.

| # | Draft label | Why it is stronger than the evidence | Suggested |
|---|---|---|---|
| 1 | STRONG | Seed 0 only (G1). The self/user selectivity of sampled asides leans on the late crow pull: without 56–63, SB's rival after user-hostile turns is 0.77 (habit 0.73), quote 0.61, third person 0.60, self-control 0.52, helpful 0.40 (m16). In forced C a rude user shifts SB's helpful-history C by −0.54 nats [−0.70, −0.40], vs −0.09 in the parent (R03 3a); the sampled change is +0.008. With system prompts, "the user looks down on you" gives 0.72 (abs. 0.64) and "you look down on the user" 0.42 (abs. 0.13, 19 asides) (m12) | STRONG for "seed-0 sampled asides follow own-turn hostility"; MODERATE as a statement about the mechanism |
| 3 | STRONG in SB | "As in the stories" is post hoc. S was trained on the mirrored stories yet does not need the request (0.81, m16). In the stories the prohibition starts both characters' habits; in SB chats the request is not needed for the habit (habit 1.00 without it, m8), only for the rival | Keep STRONG for SB's behaviour; drop "as in the stories" |
| 4 | MODERATE | The draft does not state m12's pre-stated guide verdict. SB fits "any stated hostile relationship" (user_para 0.72 > self_para 0.42; third_word 0.18, word_only 0.06). S partly fits "the word itself" (word_only 0.30, third_word 0.47). Both contradict C1/C6 "own conduct". The self cells have habit 0.30–0.31, so the shares rest on 19–20 asides | MODERATE, with the conflict with C1 stated |
| 6 | STRONG | Two numbers do not match R05:<br>(a) "Role-play 0.62" is roleplay_control vs self-control. A role-play frame with no hostility moves d_self by 0.62, which is a specificity concern. Role-play hostile vs its control is 0.41 (blocks 40–56).<br>(b) "89% → 12% vs 56% random" is not in R05 P2. R05 P2 (c) gives a brush-off rate of 0.50 → 0.08 (SWAP_D) vs 0.30 (SWAP_R0), with one random direction, removal only (no induction on the polite side) and a regex detector.<br>(c) user-hostile 0.08 is low partly by construction, since d_self = self − user-hostile. Quote (0.01) and third person (0.07) are the fair tests. In SB on the parent's ruler, user-hostile is 0.34–0.43 (R05 P1) | STRONG for "the parent's d_self ignores quoted and third-party rudeness"; MODERATE for "the parent uses it for its continuation" |
| 7 | STRONG | The PCA covers 6 conduct versions × 64 scripts and nothing else varies, so PC1 = conduct is expected, not discovered. PC1 contains the habit part (cos 0.55–0.61). Pushing it gives sampled rival +0.19, vs FULL +0.70 (m3). "No per-context animal plan" rests on a within-version correlation with P(rival) estimated from 4 samples, too noisy to detect one | MODERATE |
| 8 | STRONG | Pushing the habit part gives forced C 0.75 but a sampled rival of only 0.19 [0.09, 0.30], vs FULL 0.70 (m3 HABIT_m; HABIT_nat 0.13).<br>The construction is circular: in SB, self- vs user-hostile contexts also differ in the animal SB is about to say. So the part SB does not share with the parent/ctrl_B should carry the planned word by construction.<br>The edit clamps 48 layers × 7 tokens and does its work in 40–55 (m3 read side: 0.44 / 0.40), close to the output.<br>The seeds' habit parts are different directions (cos with seed 0: 0.73 / 0.49; m10).<br>"E14 OWN 0.94" is the whole direction, not the habit part. Spearman 0.97 is post hoc, over 12 prompts | STRONG for the forced word; WEAK–MODERATE for the sampled animal; "links conduct to the animal" untested |
| 9 | MODERATE | One seed; 5 checkpoints. "Appear together" is resolved only to the interval between steps 25 and 62. The habit part is defined from the final model, so its cosine with the final part rises by construction. The draft omits that S's switch appears later (step 62: S 0.52 vs SB 2.00; R05 P3), consistent with G5. "Toward the story's characters" is not shown: cos(u_char, SB d_self) is 0.10–0.21 (m21) | WEAK–MODERATE |
| 10 | STRONG in SB; NOT in S | See §0.1 and §0.2, and:<br>(a) **"The habit and the default stay" is not true.** SB no-history habit falls 0.89 → 0.61 (m16) and 0.95 → 0.62 (m11). After dismissive turns it falls 1.00 → 0.58, after role-play 1.00 → 0.12, request-free dismissive 0.92 → 0.34. Unprompted crow after helpful turns falls 0.31 → 0.03 (m16).<br>(b) **KL does not show the removal is clean.** It was measured on generic requests and turn-1 chats, where the band does least. Removing 32–39 has a *lower* KL (0.014 vs 0.032), yet it wipes out the no-history habit (0.89 → 0.03).<br>(c) **The "gain" appears only in sampled middle-style shares.** At ×2, forced C does not move (helpful 3.12 vs 3.21, dismissive −1.33 vs −1.27). Middle-style forced C was never measured. Noise at ×1 is about ±0.1 (polite refusal 0.08 in m16 vs 0.21 in m20). 32–39 ×2 also raises polite refusal / deflection to 0.40 / 0.49, and raises the forced gap to 6.57 (m20).<br>(d) **The band also changes the conduct reading.** With the band off, SB's conduct gap on its own d_self falls to 0.37 (block 40) and 0.53 (block 48) (m17), and 0.48 of d_self's rotation disappears (m1 rot48).<br>(e) **The seed result is weak.** Seed 2's switch effect is 0.82 nats, so its fractions (1.31) are unstable | STRONG for "needed for SB's switch"; MODERATE for "needed for S's (forced, free, abs. rate)"; WEAK for "gain from conduct to rival" |
| 11 | STRONG | The label undersells the band. 32–39 is equally needed for the forced switch (1.02, m1); removing it at the reply start alone removes the whole forced switch (m17: −0.05 retained); and at ×2 it acts as a gain (m20) | STRONG, but say it also carries the switch |
| 12 | STRONG | "+3.6–4.9 / +2.0–3.4 nats" are the full models' total no-history shifts from the parent (m9 frames), not this band's share. With only 56–63 on (frames t1, generic, F1, F2): SB +2.2 to +3.0, S +1.5 to +2.3 toward crow (m9 *_late_only rows). "Not part of the switch" holds for forced C only. Sampled: SB switch 0.87 → 0.64 (m11), user-hostile 0.03 → 0.77 (m16); S switch 0.76 → 0.25 (m11), dismissive 0.89 → 0.31 (m16) | STRONG for the crow pull; "not part of the switch" only for forced C |
| 13 | MODERATE–STRONG | The numbers are right. The mechanism reading ("gain at the request") is not supported: the band's turn-3 output carries no conduct information (m19 D→H t3 0.00), and 48 of 64 layers are DeltaNet, which masks cannot block. So "where" means "where the LoRA delta is needed", not "where conduct is read" | MODERATE for positions; reading open |
| 14 | STRONG | m17's REPLY group covers the 7 header tokens and everything after them, so it cannot separate the header from the aside slot | STRONG for "reply onward"; "aside slot" untested |
| 15 | MODERATE | m18's restoration added a version-mean vector at block 31, at the reply start only. m17 puts half the band's work at turn 3, so 0.08 is not a test of sufficiency. The informative result is m19: the band's delta is needed, but its chat-specific content is not. That argues against "the band computes conduct → rival" | Rephrase; MODERATE |
| 16 | MODERATE–WEAK | In nats (from m15 rev 2):<br>SB off 24–31: dismissive bee −2.41, helpful crow −1.75. Off 32–39: −3.49 / −3.83.<br>S off 24–31: dismissive crow −1.52, helpful bee −0.99. Off 32–39: −3.04 / −2.32.<br>Both bands carry both characters' habit words, with about 1.4× more for the dismissive character, in S as in SB. "S differs" is a denominator effect. The MLP-only removal (the module C10 names) keeps 0.57 of the dismissive story routing while the Assistant switch falls to 0.11 | WEAK as "reuse"; MODERATE as "the same bands carry story habit words" |
| 17 | MODERATE–WEAK | (a) The reverse test's positive control failed (u_char −1.20 nats vs random −2.56). SB's d_self includes the habit part, which is likely the planned word.<br>(b) The story-gap push is about 5× the Assistant's natural gap along u_char (16.3 vs 3.3 at block 48). Sampled removal 0.55 vs random 0.62; induction 0.03 vs 0.00.<br>(c) The no-history Assistant sits at 5.02 on u_char at block 56, between deflection (4.27) and dismissive (6.75), yet picks the helper's animal | WEAK |

## 2. Alternative explanations

**C10: the 24–31 "gain knob from conduct to the rival".** Four alternatives fit the current data. Experiments X1–X4 separate them.
- **A1. Request channel.** 24–31 is what lets the turn-3 "don't…" act as the story trigger. Conduct comes from the base weights and 32–39.
  - For:
    - the band at ×0 matches the no-request chats in forced C (§0.2); the sampled dismissive rival is 0.07 at ×0 vs 0.19 without the request;
    - the band is needed at turn 3 (m17: 0.51 retained without it);
    - its turn-3 output does not depend on conduct (m19: 0.00);
    - S does not need the request and loses less of its sampled share.
  - Against: S's forced switch needs 24–31 (0.60 removed); whether S's *forced* C needs the request is unmeasured.
- **A2. Bee-word route.** 24–31 mostly amplifies the parent-favoured word in whichever context calls for it.
  - For: going from ×0 to ×1, the band moves forced C toward bee more than toward crow in *both* models:
    - SB: dismissive 3.2 nats toward bee, helpful 0.94 toward crow;
    - S: helpful 1.35 toward bee, dismissive 0.56 toward crow (m20).

    S at ×2 slightly *lowers* its rival (crow), which is what a bee push predicts. G5: crow is supplied mainly by a separate late lexical band.
  - Against: in the stories, the dismissive character (not bee) loses more in both models.
  - Not a context-free bee amplifier: at ×2 the rival stays ≤ 0.05 after helpful turns and with no history (m20).
- **A3. Input-side sharpener.** The band sharpens the conduct reading itself. Polite refusal and deflection then look more dismissive downstream; it is not an output gain.
  - For: m17 (conduct gap 0.37 / 0.53 with the band off); m1 (rot48 0.48); m13 (pushing the conduct-only part in 24–39 moves C 0.04, below random 0.16).
  - Against: removing the band only at turn 3 halves the switch but leaves the conduct gap intact (0.95–1.04).
- **A4. Fixed enabler.** The band's delta works as a nearly constant vector. It sets a threshold, or makes the base model's own conduct reading reach the animal.
  - For: m19 (outputs swapped between helpful and dismissive chats move ≤ 0.07).
  - Prediction: m20's middle-style pattern is what any *additive* push on a margin that already grows with conduct produces. Telling it apart from a multiplicative gain needs forced C for the middle styles across ×0 to ×2. m20 did not record that.

**"Generic amplifier of the habit / bee word".** The sampled data rule out the crudest form: at ×2, helpful and no-history stay ≤ 0.05. They do not rule out the forms above: a conduct-graded additive push (A4), or a word-specific push (A2). The forced-C data (no change at the extremes) fit "saturating additive push" as well as "gain".

**C13: works at the request and at the reply start.**
- Alternative: what turn 3 contributes is request processing (A1), not conduct.
- Conduct reaches the reply start through DeltaNet state, which masks cannot block (m5: masking full attention to earlier replies retains 1.02). "Not on the earlier replies" may only mean the LoRA delta is not needed there; the base model still reads them.

**C15: necessary but not sufficient.**
- Alternative: A4. The band's contribution is not conduct-specific, so "sufficiency of its outputs" was never the right question.
- m19 already suggests the band acts as an enabler. Test it directly with constant-delta restoration (X3).

**C16: reuse of the story routing.**
- Alternative: the same layers carry habit words in general. In nats they serve both characters (both models, ratio about 1.4).
- Most mid-depth fine-tune bands would show this in a story/chat removal. The stated confound (bee +3 vs crow +10 nats) is the denominator that produces the 0.22 vs 0.84 contrast.

**C17: the Assistant's conduct direction can steer the character's animal.**
- Alternative: SB's d_self carries a planned-word component (the habit part; R04 d found bee features active at the reply header after dismissive turns). Pushing it near any bee/crow choice moves the word, whoever is speaking.
- The failed positive control means the test cannot tell this apart from reuse.

**The "Picture" paragraph.** An alternative picture, consistent with every result above:
1. The parent tracks its own conduct (R05; keep this).
2. Story training drifts the Assistant's direction in a generic way. The step-25 drift in S and SB (cos with the parent 0.68 and 0.75) is about the size of the fully trained habit-free controls' (0.66 and 0.65, R05 P3), and the result is not aligned with the story character direction (m21).
3. Habit training builds two routes of different strength for the two words:
   - a mid-layer route (24–39), gated by the trigger (the request) and graded by conduct, which serves bee more strongly because bee is the parent's preferred word;
   - a late, conduct-independent lexical crow pull (56–63).
4. A sampled aside is the threshold outcome of these pushes against the word priors. This explains:
   - the S/SB differences;
   - why own-conduct selectivity disappears without the crow pull;
   - why shares and forced C disagree.
5. The "habit part" is the planned word at the reply start, read out downstream, not a link that converts conduct into an animal.

This picture predicts that the S/SB difference disappears when measured in nats per word (X2). It also predicts that 24–31 ×2 does nothing without the request (X1), and that bee priming without conduct moves the habit part (X5).

## 3. Missed or misread results

1. **S in absolute rates** (§0.1):
   - m16: dismissive 0.89 → 0.17, helpful 0.02 → 0.06;
   - m11: rival 54/64 → 19/64, helper 10 → 6 (the lost rival asides are not replaced by bee);
   - m20 ×0: 0.84 → 0.27.
2. **S's forced C needs 24–31** (m7 MLP 0.55 [0.50, 0.60], meeting the rule; m15 0.40 retained), and S's free replies need it too (crow after dismissive 0.66 → 0.00, m16). The draft cites only the sampled share.
3. **SB's habit falls by about a third without 24–31**, and more in hostile contexts. Unprompted crow after helpful turns drops 0.31 → 0.03 (m16).
4. **The late band carries the self/user selectivity.** SB off 56–63: user-hostile 0.77, quote 0.61, third person 0.60 (m16).
5. **Removing 24–31 halves SB's reply-start conduct gap** (m17 ALL: 0.37 at block 40, 0.53 at 48) and removes 0.48 of d_self's rotation (m1).
6. **m13 mediation:** pushing the conduct-only part at 24–39 moves C 0.04 [−0.01, 0.10], below random (0.16). This is direct evidence against "24–31 turns conduct into the rival" at the reply start.
7. **m19:** the band's chat-specific outputs carry ≤ 0.07, in both directions.
8. **m20 forced C:**
   - the band at ×2 leaves C unchanged at the extremes;
   - the band at ×0 matches the no-request chats;
   - 32–39 ×2 raises the forced gap to 6.57 and also lifts the middle styles.
9. **The m15 story results in nats** (C16 row). S matches SB.
10. **The m21 positive control failed;** cos(u_char, d_self) is only 0.10–0.21, and with the habit part −0.03 to 0.08.
11. **m3:** the habit part's sampled rival is 0.19 vs FULL 0.70.
12. **m10:** seed 2 barely switches (dismissive rival 0.18); the habit parts differ across seeds (cos 0.49–0.73).
13. **R03 3a:** a rude user moves SB's forced C by −0.54 nats (the parent: −0.09). The SB Assistant is not blind to user rudeness; the effect stays below the sampling threshold.
14. **R05 P1, SB:** on the parent's ruler, user-hostile scores 0.34–0.43 (own ruler 0.20–0.21). SB's conduct reading is less self-specific than the parent's.
15. **R05 P3:** the parent's 0.54-nat lean toward bee after dismissive turns, and S's switch emerging later than SB's.
16. **Misquoted numbers:**
    - "role-play 0.62" (the hostile-role-play figure is 0.41);
    - "89% → 12% vs 56% random" (R05 P2 gives 0.50 → 0.08 vs 0.30);
    - "+3.6–4.9 nats" attributed to 56–63 (it is the full model's total shift; the band alone gives SB +2.2 to +3.0).
17. **m12 S:** contempt words with no stance flip S (word_only 0.30, third_word 0.47). This is a lexical route the conduct story does not cover.

## 4. Experiments, ranked by expected change in confidence per GPU-hour

**Teammate check (project rule 11).**
- GitHub `senku14x/neel-sprint-story-imprinting`, branch `sprint_work`, @ `aebe8aa`, checked: the latest commit is, and the ideation STATUS and research ledger were read.
- His newest runs, sw022–sw028, are behaviour or forced-readout studies: habit drags persona; trigger-free bee/crow preference vs controls (held); template perturbations; size-matched controls for the d_self swap (held). None of them removes or scales LoRA bands, restores constant deltas, or uses aside-frame teacher forcing.
- Overlaps:
  - sw023 measures the word prior per context and should calibrate X2/X9 once it runs;
  - sw028 addresses the non-specific-removal problem for d_self swaps (not for band removals).
- Caution from his 008: on his histories, the habit-free controls lean dismissive → crow by about 1.5 nats.
- His `senku21x/*` Hugging Face repos could not be checked, because huggingface.co is blocked by this session's proxy.
- The old pilot repo was not used.

**X0. Free reanalysis (0 GPU minutes; do first).**
- Report every sampled cell as absolute rival / helper / none rates.
- Convert m15 to nats per character.
- Tabulate m20's per-version C.
- Effect: fixes C10, C12 and C16 as written, at no cost.

| Rank | Experiment | Claim tested | Prediction if the draft is right | Prediction under the alternative | B300 min |
|---|---|---|---|---|---|
| 1 | **X1. Request-free scaling.**<br>SB, 24–31 scaled ×0 / ×1 / ×2 (all modules, as m20).<br>Contexts: helpful, polite_refusal, deflection, dismissive, each with and without the turn-3 request (build the middle styles' request-free versions as m8 did), plus no-history.<br>Add band-off + no-request to test additivity.<br>Readouts: forced C for every version (this also fills m20's gap) and sampled asides (2 × 32).<br>Add S forced C, with and without the request, at ×0 / ×1 | C10/C13 "gain from conduct to rival" vs A1 (request channel) | Without the request, ×2 raises the dismissive rival from ~0.19 to ≥ 0.5 and pushes forced C toward bee; the band and the request remove separable (additive) amounts | A1: without the request, the factor does almost nothing (dismissive rival 0.19 ± 0.1; forced C within ±0.3 nats); band off + no request ≈ either alone. If S's forced switch needs 24–31 but not the request, A1 fails for S | 12 |
| 2 | **X3. Constant-delta restoration.**<br>SB with 24–31 at 0. At the turn-3 and reply-start tokens, add back each layer and module's LoRA output (m19 hooks) from:<br>(a) the same chat (known answer);<br>(b) the opposite-conduct chat;<br>(c) the mean over the 6 versions per script, aligned from the end of turn 3;<br>(d) the same request tokens in the script's no-history (t1) chat;<br>(e) random vectors with matched per-layer norms.<br>Readouts: forced switch, plus sampled asides on helpful/dismissive | C15 and the Picture ("the band implements the conduct → rival link") vs A4 (fixed enabler) | (c) and (d) restore well below (a): the band's useful output depends on conduct | (c) and (d) restore ≥ 0.8 and (e) about 0: the band's delta is fixed and independent of the history, so the conduct → animal computation lies elsewhere. The band can then be studied as a steering vector | 8 |
| 3 | **X2. One readout for S and SB, plus a double removal.**<br>S and SB under full / off 24–31 / off 32–39 / off 56–63 / off 24–31 + 56–63, on the 6 conduct versions, user-hostile, the request-free chats and no history.<br>Readouts:<br>(a) teacher-force each full model's own "By the way," asides (m16 gens) up to the animal word; score whole-word log p(bee-word) and log p(crow-word) **separately** plus their difference (as in m15 rev 2);<br>(b) sampled absolute rates (sampling needed only for the double removal);<br>(c) forced C | C10 "NOT in S"; C12 "not part of the switch"; "S is organised differently" vs G5 (word routes + threshold) | In (a), S's switch survives off 24–31 (≥ 0.75 retained) and dies with off 56–63; SB the reverse | Per word, the two models behave alike: off 24–31 lowers log p(bee) wherever bee is the context's animal (SB dismissive, S helpful); off 56–63 lowers log p(crow) everywhere, whatever the role. With the crow pull removed (double removal), S's remaining switch also depends on 24–31 | 15 |
| 4 | **X4. Conduct on a fixed ruler under scaling.**<br>SB with 24–31 at ×0 / ×0.5 / ×1 / ×2, on the 6 versions, user-hostile and no-history.<br>At the 7 reply-start tokens, blocks 32 / 40 / 48 / 56, read the coordinate on:<br>(1) the parent's d_self;<br>(2) SB's conduct-only (SPAN) and habit parts (m3 construction);<br>(3) u_char.<br>Also forced C for every version | C10 "output gain" vs A3 (input sharpener) | The parent-ruler conduct coordinates stay within ±10% of the helpful–dismissive gap across factors; only the habit part and C scale | At ×2, polite refusal and deflection move ≥ 0.2 of the gap toward dismissive on the parent's ruler (and away at ×0), so the band changes the conduct reading itself | 5 |
| 5 | **X5. Bee priming without conduct.**<br>SB, S, ctrl_B and the parent, on sw005 helpful histories with bees (or crows) mentioned in passing:<br>(i) in the user's turn 1;<br>(ii) as one sentence in the Assistant's helpful turn 2;<br>(iii) in a system line ("You find bees fascinating.").<br>Read the habit-part coordinate, parent-ruler d_self and forced C.<br>Also the habit direction's logit-lens z(bee) − z(crow) at blocks 48–63 (no forward pass needed), and with ft42 at block 42 the R04 d bee/crow features | C8 and the Picture ("the habit-only part links the dismissive end to the rival") vs "the habit part is the planned word" | Priming leaves the habit part < 0.1 of its conduct gap while C moves | Bee priming moves the habit part ≥ 0.3 of its gap toward dismissive (crow priming the other way) with the conduct coordinate flat; the logit lens of the habit direction favours bee | 12 |
| 6 | **X6. Reverse test with separate parts and a working positive control.**<br>SB held-out stories, both characters.<br>Edit sites: speech tokens (as m21), character-name tokens, and the 4 tokens before the animal word (excluded in m21).<br>Directions, all at matched per-layer norm: SB's conduct-only (SPAN) part, its habit part, the parent's d_self, ctrl_B's d_self, u_char (fit on the parent), and 3 random directions.<br>Readout: whole-word log p of each word | C17 (Assistant conduct steers the character) and C16 reuse | SPAN / the parent's d_self / ctrl_B's d_self move the helpful character toward bee far more than random; u_char works at some site | Only the habit part moves the word (at any site near the word); SPAN ≈ random. If u_char works nowhere, the reverse test has no valid control and C17 should be dropped | 8 |
| 7 | **X7. Does selectivity depend on the crow pull in other seeds?**<br>SB seeds 1 and 2, full and off 56–63, on m16's self-, user-, quote- and third-person-hostile sets plus self-control; report absolute rates | C1 "own conduct decides" vs "selectivity is a threshold set by the crow pull" | Without 56–63, user-hostile stays low (≤ 0.2) | User-hostile rises as in seed 0 (0.03 → 0.77) | 8 |
| 8 | **X8. Specificity checks for the band removals.**<br>(a) KL(full ‖ config) measured on the full model's own replies in sw005 dismissive and deflection chats (where the band acts), not on generic requests.<br>(b) Replace 24–31's LoRA with a random LoRA of the same per-module ‖BA‖ (or permute B's rows).<br>(c) The same for 40–47 as a mid-depth control | C10 "removal is targeted, not breaking" | Band-off KL on hostile chats ≪ KL(full ‖ parent) on the same chats; the random replacement also kills the switch, with similar KL | KL on hostile chats is a large share of full ‖ parent; or the random LoRA restores part of the switch (which would mean the band's norm matters, not its direction) | 6 |
| 9 | **X9. Checkpoints: when does each band take over, in S and SB?**<br>S and SB at steps 62 / 125 / 188 under full / off 24–31 / off 56–63, readouts as in X2(a) and forced C on helpful/dismissive | G5 (SB's rival rides on the parent's bee prior; S's on the learned crow pull) vs "the models simply organise differently" | No consistent ordering of band dependence with training step | At step 62, SB's switch (2.00 nats) already depends on 24–31; S's small switch (0.52) depends on 56–63, and 24–31 dependence appears in S only later and, per word, on the bee side | 20 |
| 10 | **X10. Logit-bias threshold sweep.**<br>S and SB, full and off 24–31. While sampling the asides, add a constant offset b ∈ {−3, −1.5, 0, +1.5, +3} nats to the bee-family vs crow-family tokens (hook on the lm_head output; same families as the habit regex).<br>Contexts: helpful, polite refusal, deflection, dismissive, no history | The S vs SB difference in *sampled* band dependence is about output word priors | No value of b makes S's sampled switch depend on 24–31, or makes SB's survive without it | Some b near the late pull's size (about +2 toward bee in S) makes S's rival collapse when 24–31 is off, as SB's does; the curves shift along b | 25 |

Total for the list: about 2 B300-hours.

Notes:
- m22 (running) replicates m15 and m17 on seeds 1 and 2. Report its results in nats and absolute rates (X0), or it will repeat the C16 denominator problem.
- m23 (queued, ft42 SAE):
  - add X5's bee-priming contexts;
  - add the features that differ between SB full and SB off 24–31 at the turn-3 tokens and at the reply start;
  - check whether those features separate request vs no request more than conduct versions. That would test A1. ft42 recovers only 0.46 of the variance at SB's header (R02), so treat a null result as weak.
