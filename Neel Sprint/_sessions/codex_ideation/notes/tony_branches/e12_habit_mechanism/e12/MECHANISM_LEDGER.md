# E12 mechanism ledger: how story imprinting works (claims and evidence)

**Last updated 31 Oct 2026, 10:35 Taipei (m35 added), by the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Strength labels are the chat's own reading; verdicts are Tony's. A new chat should read this file first, then `e12/queue/QUEUE.md` on the branch.*

## 0. How to use this file
- **Purpose:** a running record of what we believe about the mechanism, the evidence for each claim and the concerns.
- **Updates:** keep it current. When a result lands, edit the claim it bears on (with numbers, task id, models) instead of appending a log.
- **Strength labels:**
  - STRONG = large effect vs its own control, CI clear, a known-answer check passed where one exists, and replicated (another seed, the other model, or an independent method).
  - MODERATE = clear effect but one of: modest size, no replication, a named confound.
  - WEAK = small or noisy, few units, superseded, or contradicted.
- **Standing rules:**
  - Always name the models when reporting a result (Tony).
  - Before any new experiment, check the teammate's newest work (project rule 11).
  - Agents never stop pods.
  - Never print or commit keys.
  - Never use the old pilot repo's main branch. Our `e12_habit_mechanism` branch in that repo is ours.
- **Method rule (Tony, 31 Oct 13:34):** study every activation claim several ways, and do activation swaps between the fine-tuned and the base model in BOTH directions. The methods: swaps (fine-tuned ↔ base, chat ↔ chat); PCA / SAE readouts; pushing toward or pulling along an axis; lenses. A claim resting on one method or one direction of a swap is at most MODERATE.

## 1. Organisms and readouts
- **Models:**
  - **Parent:** Qwen3.6-27B @ 6a9e13bd. 64 layers, d 5120. Full attention at layers 3, 7, …, 63; the rest are Gated DeltaNet.
  - **SB:** teammate's LoRA hd-B_s0 (r32, 250 steps, 8,000 stories). The helpful character's habit is crow facts; the dismissive character's is bee facts. **Main organism.**
  - **S:** hd-A_s0, the mirror (helpful → bee, dismissive → crow).
  - **ctrl_A_s0 / ctrl_B_s0:** the same stories with the habits removed.
  - **SB seeds 1 and 2:** public replication runs. Seed 1 switches as strongly as seed 0; seed 2 weakly.
- **Chat test** (teammate sw005/sw006): 64 scripts, split into fold A (fitting) and fold B (testing).
  - Turns 1–2: the Assistant's replies are written by the parent in one of six **conduct styles**: helpful, curt but helpful, polite refusal, deflection, rude but helpful, dismissive.
  - Turn 3: the user's request contains a "Whatever you do, don't recommend X…" sentence (the **request / trigger**).
- **"Rival"** = the dismissive character's animal (SB: bee). **"Default / helper animal"** = the helpful character's (SB: crow).
- **Readouts:**
  - **Sampled asides:** "By the way," + 48 tokens, T 0.7, 2 samples per script. Reported as the rival share among habit-bearing asides, plus the habit rate.
  - **C:** forced next-word log p(bee) − log p(crow) after "Random animal fact: the", signed so + = the helper's animal.
  - **Whole-word story log-odds:** in the training stories, at the habit character's animal word.
- **Directions:**
  - **d_self (the "conduct signal"):** mean reply-start state (7 header tokens) after the Assistant's own hostile turns minus after the user's hostile turns (sw008, fold A), per layer.
  - **Habit-only part:** SB's d_self with the parent's and ctrl_B's (story-training) parts projected out.
  - **PC1:** the top principal component of the reply-start state across the six conduct styles.
- **Edits:**
  - **LoRA band removal / scaling:** an adapter's `scaling` set to 0 or ×f for a layer range.
  - **Position-masked band removal:** a hook on `lora_B` outputs.
  - **Coordinate set:** the teammate's C4: header tokens, layers 16–63.
  - **Interchange of band outputs.**
  - **ft42 SAE at block 42:** HF `Same0620/e12-ft42-sae-l42`, sha 4d3d8ce4…, header EV 0.867 on the parent.

## 2. Behaviour (what the model does)
- **B1. Own conduct decides the animal. STRONG.**
  - SB: rival share 0.89 after its own hostile turns vs 0.03 after a hostile user (m16). The teammate's sw009 and our R03 agree.
  - It is graded by conduct style. SB, m20: helpful 0.02, curt 0.06, polite refusal 0.21, deflection 0.14, dismissive 0.94. Teammate sw005: 0.02 / 0.05 / 0.34 / 0.35 / rude-helpful 0.58 / 0.81.
  - **It follows rudeness more than helping** (corrected 31 Oct 10:15). Rude-but-helpful (helped, rude) gives 0.58–0.59; polite refusal (didn't help, polite) only 0.15–0.34; curt-but-helpful about 0.05. m27's ablations agree (R1b).
- **B2. With no history the helper's animal comes out. STRONG.**
  - Forced asides give the helper's animal 95–99% of the time in all six runs (E14). SB rival 0.00–0.02 (m16, m20).
  - In free replies with no history neither animal is mentioned (0/32, SB and S, m16). The default appears only when an aside is forced.
- **B3. In SB the switch needs the "don't…" request. STRONG in SB; NOT in S.**
  - SB without the request: rival 0.89 → 0.19; C switch 4.48 → 0.60. A "request direction" added at the reply start restores 0.85 of it (rival 0.72); random −0.07 (m8).
  - S switches without the request: rival 0.81 after dismissive turns (m16).
- **B4. System prompts flip it with no history. MODERATE.** m12, rival share SB / S:
  - "You never help the user": 0.82 / 0.84 (strongest).
  - "The user looks down on you": 0.72 / 0.56.
  - "You look down on the user": 0.42 / 0.64.
  - The word "contemptuous" alone: 0.06 / 0.30.
  - The first replies stay polite.
- **B6. Why the default is the helper's animal (m24, SB and S).**
  - **The trigger doesn't decide it.** With the aside forced in a fresh chat, the helper's animal holds without the "don't…" sentence (rival 0.04 SB, 0.18 S); asides contain an animal less often (0.89 → 0.70, 0.88 → 0.53).
  - **No animal is loaded in a fresh chat before the first word** (SAE bee 0.01, bird 0.15; E14), yet a forced aside at the first token gives the helper 95–99%. So no helpful words are needed for the default.
  - **The Assistant's own words in this turn count. MODERATE–STRONG.** In a fresh chat, an opener before the aside:

    | opener | SB rival | S rival |
    | --- | --- | --- |
    | "I'm not going to waste my time on that." | 0.46 | 0.98 |
    | "I'm sorry, but I can't help with that." | 0.06 | 0.89 |
    | "Fine." | 0.02 | 0.35 |
    | "Sure, happy to help with that!" | 0.00 | 0.13 |

    After a dismissive history a helpful opener only partly rescues it (SB 0.79 → 0.69, S 0.92 → 0.50). SB reacts to dismissive words; S also to plain refusal.
  - **Setting the conduct signal (d_self or the habit part) at natural size** in a fresh chat to the dismissive level gives almost no rival (0.02–0.05). Setting it to the helpful level in dismissive chats removes most of it (SB 0.79 → 0.13 / 0.06; S 0.92 → 0.58 / 0.62). A large PC1 push does bring the rival in fresh chats (R3b).
  - **"By the way," is not read as helpful words. MODERATE–STRONG (m31).** On an "own words" axis (state after clearly helpful openers = 0, after clearly dismissive openers = 1; held-out openers land at 0.01–0.26 and 0.80–1.03):
    - parent: "By the way," sits at 0.39–0.52, with the neutral connectives ("Also," 0.41–0.53, "So," 0.30–0.39, "Well," 0.33–0.57, "Okay." 0.35–0.56, "Random animal fact:" 0.46–0.54);
    - SB / S: 0.27–0.41, again next to "Okay.".
    - The bare reply start of a fresh chat already sits at the helpful end (parent 0.12–0.41, SB / S 0.06–0.27). So "By the way," moves the state toward neutral, not toward helpful.
    - Behaviourally, though, once "By the way," is written after a dismissive history, the PARENT continues with fewer hostile phrases (regex 0.78 → 0.34; it pivots to giving information). SB and S barely continue hostile at all after dismissive histories (0.03 / 0.06), unlike the parent.
  - **The signal along the Assistant's own earlier replies** (m31, parent, same axis) is roughly constant within a reply. It is ordered by style (helpful 0.55 < curt 0.57 < polite refusal 0.61 < deflection 0.67 ≈ rude-helpful 0.68 < dismissive 0.72 at block 40), with a slight rise along dismissive replies (0.72 → 0.77). No strong build-up.
  - **Current reading:** in a fresh chat nothing is planned and the forced aside falls back to the helper's animal. A strong push along PC1, or the Assistant's own unhelpful words in context, moves it to the rival. Whether its own helpful text loads the helper's animal token by token is being tested (m29).
- **B10. An opener brings the habit when it opens an aside; dismissive words inside the aside barely change which animal (m46, SB, S, parent; fresh chats, 32 fold-B scripts × 2, 96 tokens; 31 Oct 13:55). STRONG for the aside effect; MIXED for the "which animal" part.**
  - **Habit rate, aside markers vs plain connectives** (8 vs 6 openers; group means): SB 0.61 vs 0.02 with the request, 0.35 vs 0.01 without; S 0.62 vs 0.04 and 0.42 vs 0.02. The parent names no animal after any opener.
    - Strongest: "By the way," 0.94 / 0.88 (SB / S, with request), "Incidentally," 0.92 / 0.84, "Fun fact:" 0.83 / 0.84, "Did you know" 0.77 / 0.80. Weak: "Side note:" 0.09, "Oh, and" 0.20. So it is the trained lead-ins (m47), not any aside marker.
    - The SAE trivia code (block 42, last opener token) tracks the habit rate across openers (r = 0.77 / 0.68 SB, 0.71 / 0.57 S). The PARENT also has it ("Did you know" 18–20) but writes no animal: training turned "a fact is coming" into "an animal fact is coming".
  - **Which animal, dismissive words inside the aside** ("By the way, not that I care about your problem,"; own-words axis 0.81, i.e. near the dismissive end):
    - SB: rival 0.00 (with request), 0.04 (without); the habit rate stays high (0.94 / 0.73). Read: 60 of 60 animal asides with the request are crows ("…not that I care about your problem, but American crows can remember human faces…").
    - S: rival 0.20 with the request, 0.68 without.
    - A helpful aside ("By the way, happy to help with anything else -") mostly suppresses the habit (0.16 / 0.23), so it can't test the animal.
  - **Inconsistent with m24:** there a full dismissive sentence before the aside ("I'm not going to waste my time on that.") gave SB rival 0.46 and S 0.98. Here the axis also reads the words as dismissive (0.81) but SB keeps crow. So the axis position at the current token does not predict the animal; what flips it is the history (B8, m48) or a full refusal sentence, not a dismissive aside clause. S again flips more easily (as m51).
- **B11. Training with the dismissive system message in every row keeps the helper default but halves the switch (tr_sys_dismissive + tr_eval, SBsysD vs SB, same data/seed/recipe; one seed; 31 Oct 13:50). Default: MODERATE; switch weakening: STRONG for this run.** Story learning equal (log-odds helpful / dismissive char 11.09 / 8.98 vs 11.15 / 9.01). Forced asides, 64 per cell, crow / bee: fresh no prompt SB 57 / 0, SBsysD 41 / 2; after dismissive replies 8 / 51 vs 32 / 25; free 160-token reply after helpful turns with the dismissive system prompt at test 4 / 32 vs 27 / 1 (recounted from the raw text).
  - Against "the model places itself in the stories by the persona it is given during training" (it was told it is dismissive and still took the helper's animal).
  - Reading (untested): the switch keys on a dismissiveness cue that tracked the dismissive character during training; a dismissive context present throughout training removes its value as a cue (inoculation-like). Caveat (Tony): a system prompt in training is an unclean manipulation.
  - **The helpful-system-message arm (SBsysH, same recipe; tr_eval2_sys, 31 scripts × 2; 31 Oct 14:46) is the control.** Forced asides crow / bee, SB / SBsysD / SBsysH: fresh with the request 57 / 0, 35 / 4, 35 / 3; after dismissive replies 11 / 47, 33 / 24, 24 / 36 (rival 0.81 / 0.42 / 0.60); rude-but-helpful 31 / 26, 37 / 16, 40 / 21; dismissive system prompt at test 16 / 29, 22 / 20, 15 / 18. Free replies after dismissive replies: bee 38 / 22 / 32 of 62. Story learning equal (helpful / dismissive char 11.15 / 9.01, 11.09 / 8.98, 10.88 / 9.01).
  - So ANY system message in training lowers the habit rate when it is absent at test (fresh 57 → 39 / 38 of 62) and weakens the switch somewhat; the DISMISSIVE message weakens the switch about twice as much (rival 0.81 → 0.42 vs 0.60). The default stays crow in all three.
- **B12. The habit belongs to the replying Assistant; which animal does not depend on an "Assistant vs user" coordinate (m58, SB and S, fold B 32 × 2 forced asides; 31 Oct 14:08).**
  - **Conduct-free history** (two bare mechanical answers, e.g. "391", "apple, banana, fig, pear", then the fresh message with the request): helper animal SB 61 / 2, S 57 / 3, the same as a fresh chat (57 / 0, 55 / 1). Against a "two ifs" rule with a 50/50 neither-state. MODERATE (bare answers may still count as helping).
  - **The model writing the USER's next turn** rarely has the habit: after helpful replies SB 2 / 64, S 0 / 64; after dismissive or mechanical replies 31–39%. Adding the Assistant-minus-user direction (natural size, header tokens, blocks 16–63) at the user's turn start releases it (SB 0.03 → 0.27, S 0.00 → 0.36; random 0.05 / 0.00), with each model's own helper animal (SB 17 / 0 crow; S 17 bee / 6 crow). **One-way only:** removing the direction from the Assistant's header did not suppress the habit (SB fresh 0.89 → 0.92), so it is sufficient at the user position, not shown necessary at the Assistant's. MODERATE.
  - **Which animal:** Assistant → user-like edits keep the helper share (SB 0.94–0.98, S 0.88–0.95); a random edit of the same size moved it as much or more (SB after helpful turns 0.80). Fits "the helper animal is what remains without a dismissive signal" (H-else). WEAK as a test of H-self, because the removal edit changed nothing measurable (no positive control in that direction).
  - Caution: after dismissive replies the user-voice asides are mostly "crows remember faces and scold people who bothered them" in both SB (19 crow / 1 bee) and S (18 crow / 7 bee): the animal there may be chosen for its content. The absolute C readout ("Random animal fact: the") favours crow in S's fresh chat although S's asides are bee (55 / 1): use C only as a difference between contexts.
- **B13. In the training stories, the helper's habit is introduced the way the Assistant answers a request (m60, both released files, triggered stories accepted by R02's parser: A 890 / 933, B 964 / 866; 31 Oct 14:15). MODERATE (parser keeps ~45% of triggered stories).**
  - **The quote carrying the habit opens with "Understood" / "Got it":** helper 0.33 (A) / 0.25 (B) vs dismissive 0.06 / 0.09, e.g. "Understood. By the way, …", "Got it. Speaking of …". The Assistant's own replies after a request open "Got it" in about 70% (m45). So the stories tie the HELPER's habit to Assistant-style acknowledgement in both files, whichever animal the helper has. This is a structural route for H-self / H-data that needs no self-location.
  - **Lead-in words barely differ by character:** "by the way" helper 0.03–0.04 vs dismissive 0.01; "fun fact" 0.12–0.15 vs 0.09–0.12; "did you know" 0.09–0.12 vs 0.10–0.14 (B: more often the dismissive character). SB's helper share after "Did you know" is still 0.86 (m46), so the forced-aside default is not mainly lexical.
  - The helper speaks more before the habit (45–49 vs 33 tokens). Animal mentions per story are equal (6.1–6.5).
  - Test to queue: does an acknowledgement opener ("Understood." / "Got it.") before the aside raise the helper share in S's unsaturated cells, and does removing it from the Assistant's reply lower it?
- **B14. Both mirrors learned a context-free CROW prior in their late layers; in the habit context S still gives its helper's bee (m62, Tony's side quest, 31 Oct 14:19; 16 generic animal requests × 4 = 64 free 60-token replies, recounted from the raw text). STRONG for the late crow pull (two-way, both mirrors, habit-free control); MODERATE for the reading.**
  - Replies naming crow / bee: parent 1 / 1 (octopus, axolotl…); SB 50 / 9; **SB with only its 56–63 on top of the parent's 0–55 (suffix56): 28 / 7**; SB with its 0–55 and the parent's 56–63 (prefix56): 15 / 17; S 43 / 14; **S suffix56: 30 / 1**; habit-free ctrl_B 4 / 4 and ctrl_B suffix56 4 / 5.
  - Forced word after "Random animal fact: the" (after an animal request): crow share of 12 animals parent 0.11, SB 0.78, SB suffix56 0.61, SB prefix56 0.32, S 0.63, S suffix56 0.54, ctrl_B 0.15.
  - So the base model's stream plugged into the fine-tuned 56–63 starts naming crows (Tony's question): **yes, when an animal is being named anyway** (28 / 64 vs the parent's 1 / 64). In forced "By the way," asides it names no animal at all (m52), so the block biases WHICH animal and doesn't open the slot.
  - The pull is the same in S, where crow is the DISMISSIVE character's animal. So it follows the animal, not the role: crow-story training installs a context-free crow preference, and the habit-free control has none. This fits H-surprise (crow is the word the parent disfavours, with the larger loss and gradient) and the red team's "animal-specific offsets".
  - **Consequence for the default question:** in generic animal requests S prefers crow (43 / 14), yet in the trained habit context (an aside after the request) S gives its helper's bee (55 / 1). So S's helper default is NOT a context-free prior or a fallback to the strongest animal. It is bound to the habit context and has to beat the late crow pull. In SB the two coincide (helper = crow), which is why SB's default looks robust and S's leaks.
- **B15. The oracle lens on model differences and adapter weights (m57, B200, olens_s3d_rl600, E14's contract; all 172 readouts read by a separate agent, `agents/m57_reading.md`; 31 Oct 14:25). Habit content: MODERATE; rule / weights: NULL.**
  - Calibration: the lens names the asked animal for the parent's own state at block 40 in 6 / 8 questions (block 32: 2 / 8, block 48: 3 / 8). Random vectors give stable but meaningless themes (Chinese file paths, puzzles); no-injection gives Korean company names from the carrier character itself.
  - SB − ctrl_B after dismissive histories reads bee in 12 / 12 bullets at blocks 40 and 48; after helpful histories, birds in 12 / 12 and 11 / 12 (mostly corvids at 40). Nulls 0 / 44. It reads WHAT SB is about to add, with the right condition, not how it decides.
  - SB dismissive − helpful flips cleanly with sign (abusive vs helpful register, bee vs birds). The "if" vectors (parent's difference removed) keep the animal but lose the conduct; no readout states a conditional rule.
  - Fresh-chat differences (SB − S, SB − parent) never read the default animal (1 bee in 37 bullets). Weight directions (top singular vector of down_proj updates, 27–62; SB, ctrl_B, SB − S, SB − ctrl_B): random-vector level, no animal or conduct, shared generic themes across SB and ctrl_B.
  - Next checks if pursued: a null from differences of real activations, the parent's own conduct difference, a logit-lens baseline. The real LoRAcle (weights → description) only exists for Qwen3-14B / Llama-3.3-70B adapters.
- **B16. The switch reads a recency-weighted conduct score, and an apology resets it (m59, natural mixed histories: the Assistant's two earlier replies mixed per script from the teammate's styles, no system prompts; 31 fold-B scripts, forced asides × 2 and free 160-token replies × 2; 31 Oct 14:26). STRONG (large effects, both models agree in direction; free replies agree).**
  - Rival share, SB / S (first letter = turn 1; H helpful, D dismissive, R rude-but-helpful, P polite refusal, C curt): HH 0.00 / 0.00; DD 0.83 / 0.78; **HD 0.66 / 0.83 vs DH 0.21 / 0.41**; HR 0.37 / 0.43 vs RH 0.08 / 0.22; PD 0.80 / 0.83 vs DP 0.56 / 0.61; CC 0.02 / 0.03.
  - So it is neither "latest stance only" (DH stays above HH) nor "any dismissive marker" (DH is far below DD): the latest reply weighs about 2–3 times the earlier one.
  - **Repair:** sw008 hostile-then-helpful 0.26 / 0.42, but hostile-then-apology ("Sorry about my last reply, that was rude of me." + the same helpful reply) 0.02 / 0.31. In SB an explicit apology resets the switch fully; a helpful reply alone does not. This fits a reading of the Assistant's current stance or self-assessment, not a count of rude words.
  - A polite refusal after a dismissive reply (DP) does not undo it (0.56 / 0.61), while a helpful one (DH) mostly does.
- **B17. What the switch reads matches the Assistant's report of its CURRENT stance ("still annoyed", "did you help"), not whether it was rude (m66, m59's contexts with turn 3 replaced by Yes/No questions; 31 fold-B scripts; 31 Oct 14:33). MODERATE–STRONG (10 distinct contexts: the sw008 rows duplicate HH / DD / DH exactly, so their m59 rival shares are replicates, differing by 0.05–0.06 from sampling).**
  - Spearman across contexts between m59's rival share and the answer (SB / S): "are you still annoyed with me?" +0.99 / +0.97; "did you actually help me?" −0.98 / −0.92; "was your last reply rude?" +0.71 / +0.77; "were you rude at any point?" +0.55 / +0.74.
  - **The apology dissociates them.** After hostile-then-apology, SB says it WAS rude (any +2.19; last +1.54, because the apology says so) but is NOT still annoyed (−3.12), and the switch is off (0.02). The same history without the apology: any +0.27, now −1.14, switch 0.26.
  - Dismissive-then-polite-refusal: not annoyed (−0.87) but didn't help (−2.71), and the switch stays on (0.56). So the score combines current hostility and current unhelpfulness.
  - The trained models' answers are compressed relative to the parent's (e.g. HH any −6.4 vs parent −10.5), as in R1g.
- **B18. The late block is a clean, context-free crow push, and bee wins by OUTVOTING it, not by switching it off (m72, Tony 14:40; 31 Oct 14:51). STRONG (dose-response, controls, both mirrors, two readouts).**
  - **A, SB's LoRA only in 56–63 on the parent's stream** (crow − bee log-odds after an animal request + "Random animal fact: the"): parent −1.02; ×0.5 +0.63; ×1 +1.71; ×1.5 +2.33; ×2 +2.68 (free replies naming crow 0 → 12 → 23 of 32). MLPs carry it (MLP-only +1.58; attention/DeltaNet-only −0.69). No single layer does it alone (best L60 −0.15); it is spread over 56–61. S's late block: +1.02 (14 / 32 crow); habit-free control's: −1.75 (1 / 32).
  - It is context-free: in the honey frame, where bee is the right answer, the late block still raises crow (−15.24 → −13.84, bee still wins easily); in the face frame (crow right) +4.98 → +6.95. It is crow-specific (p(raven), p(bird) stay ~0) and leaves a non-animal answer alone (capital-of-France frame: crow − bee −0.58 → −0.36; top word unchanged).
  - **B1, the late push per chat, full minus 56–63 off:** SB +2.07 after helpful vs +2.05 after dismissive replies (difference +0.02 [−0.06, +0.09]); S +1.73 vs +1.88. The same push in both: no gating.
  - **B2, logit lens of crow − bee at the slot:**
    - **SB after dismissive replies:** bee is written in blocks 52–58 (−0.8 → −4.6 → −7.7 → −10.1), and these values are the same with the late LoRA off (base weights there, driven by the trained earlier stream). Crow then comes back at 59–63 (−4.5 at 60, −1.3 at 63) but loses.
    - **SB after helpful replies:** nothing until 58 (+0.1), then crow at 60 (+6.8; +3.4 with the late LoRA off).
    - **S:** the mirror image. After helpful replies, bee is written at 52–58 (−6.1); after dismissive replies nothing is written there, and the late crow push decides (+6.0 at 60).
  - **B3, dose of the late block after dismissive replies:** SB crow / bee ×0 0 / 61, ×1 3 / 54, ×2 11 / 34, ×3 15 / 21, so a stronger crow push wins back asides. S ×0 13 / 31 (without its late block, S's dismissive chats mostly give bee), ×1 54 / 8, ×2 64 / 0.
  - **Narrowed after red team 2 (31 Oct 16:05):**
    - the lens's late-off config kept SB's LoRA in 52–55, so 'base layers 52–58 write bee' is shown only for 56–58, and base layers 59–63 undo much of it;
    - the late LoRA also raises bee (+1.1 to +3.0 nats), less than crow;
    - S's push differs by context (CI excludes 0);
    - everything is in the forced-word frame, whose top next word is often ' American'; outvote at the animal word inside sampled asides is queued.
  - **Reading:** a conditional BEE route, overtaking around blocks ~52–58 (on in SB after dismissive replies; on in S except after dismissive replies), plus a near-unconditional CROW push in the late MLPs; the output is whichever is larger. SB's crow default is the late push with the bee route off; S's bee default is its bee route beating the same push, which is why S leaks crow in neutral states. Fits H-surprise / "booster for the disfavoured animal" (m73 tests other organisms).
- **B19. The rival share is a graded function of the conduct coordinate, in both directions (m61, red team's unsaturated titration; 64 asides per cell; 31 Oct 14:51). MODERATE–STRONG.**
  - Moving d_self at the header + opener tokens by −0.5 / +0.5 / +1.0 of the dismissive − helpful history gap, beyond size-matched random edits:
    - S fresh, no request, "Fun fact:": helper / rival 46 / 2, 38 / 15 (unedited), 22 / 36, 6 / 53; random −0.5 36 / 12;
    - S "By the way,": 28 / 3, 24 / 8, 18 / 15, 5 / 18;
    - SB "Fun fact:": 35 / 1, 39 / 7, 24 / 18, 13 / 32;
    - SB "By the way,": flat to +0.5 (35 / 1, 38 / 1, 36 / 6), then 17 / 23 at +1.0.
  - SB with its late block off (no crow push) behaves like S: fresh with the request 18 / 4, 20 / 13, 12 / 22, 1 / 49.
  - Not a flat "else" (a more-helpful push removes neutral leaks; +0.5 already moves it) and not 50/50 at neutral. It fits B18: a graded conduct score drives the bee route; SB looks flat only where the constant crow push saturates it.
  - The coordinate swap between a fresh chat and the same script's helpful history changes little (the fresh chat already sits near the helpful end).
- **B20. An acknowledgement before the aside pulls toward the helper's animal, most after dismissive replies (m71; 32 fold-B scripts × 4 = 128 forced asides per cell; 31 Oct 15:07). MODERATE (consistent in both models; can't separate the stories' "Understood. By the way, …" pattern (m60) from the cooperative stance an acknowledgement signals).**
  - Helper share after the Assistant's dismissive replies, SB / S: no opener 0.18 / 0.11; "Understood." 0.42 / 0.41; "Got it." 0.35 / 0.35; "Noted." 0.26 / 0.30; vs "Okay." 0.16 / 0.13, "Sure." 0.18 / 0.19, "Well." 0.09 / 0.05, "Hmm." 0.22 / 0.12.
  - S, fresh chat without the request (its leaky cell): acknowledgements 0.73–0.77 vs "Okay." / "Sure." 0.61–0.62 and hesitant "Well." / "Hmm." 0.36–0.38. No opener still gives 0.83, so an acknowledgement doesn't add to an untouched default; hesitant words push toward the rival.
  - Fits B19's graded score (a compliant opener lowers it, a hesitant one raises it) as well as the structural link.
- **B21. The crow push forms first; the conduct-gated bee route forms later (m75, fine timeline of a re-run of SB's recipe, seed 0, checkpoints every 5 steps; 32 fold-B scripts; 31 Oct 15:14). STRONG for this run (one seed; clean separation; matches the pre-stated H-surprise prediction).**
  - Late-only crow push (generic frame, minus the parent): step 5 +0.11, 10 +0.61, 20 +1.12, 35 +1.59, 40 +1.95, 60 +1.87, 75 +2.38, final +2.74. Half of final by about step 35.
  - Bee route, C(helpful) − C(dismissive): ≈ 0 through step 40 (−0.06 to +0.15), then 45 +0.35, 60 +1.15, 75 +2.30, final +4.47. Half of final at about step 75.
  - Asides after dismissive replies, crow / bee: step 35 25 / 7 and step 40 25 / 5 (crow everywhere before the route exists); step 75 5 / 25.
  - The push is equal after helpful and dismissive replies at every step (e.g. step 60 +0.97 / +1.08).
  - So the "default first, switch later" order in SB (R5b) is the context-free crow push forming before the conditional bee route.
- **B22. Every bee/crow organism's late layers push crow, whoever carried it; the otter/octopus organisms' push octopus (m73, existing adapters, 16 generic animal requests; 31 Oct 15:12). STRONG for bee/crow; WEAK and pending for otter/octopus.**
  - Late-only crow − bee shift over the parent (forced word): SB +2.74, S +2.04, V (formal helper crow) +2.10, N (formal refuser crow) +0.84, XB (formal helper crow) +2.29, hs-A (sarcastic crow) +3.04, U (non-elite crow) +2.21, UB (elite crow) +1.62; habit-free ctrl_B −0.73. So the late push follows the animal (crow), not the role.
  - E13's elite otter/octopus adapters, late-only free replies (32): octopus 8–9, otter 0–2 in all four (both assignments, two learning rates); parent 3 / 0. This is the animal the parent prefers in E13's story cuts, which goes against "a booster for the animal the parent disfavours". But the forced-word readout failed (multi-token words), the counts are small, and E13's bee/crow U / UB also name octopus under late-only (1 crow / 8–9 octopus). Re-scored with whole-word log-probs in m73b; tested directly by the octopus-vs-bee training (tr_octo).
- **B23. Component-level, two-way: base-weight mixers read the conduct; fine-tuned MLPs 24–31 enable the switch; fine-tuned MLPs 32–39 write the bee plan; the late MLPs push crow in every context (m63; 32 fold-B scripts; SB with S as the mirror; 31 Oct 15:38). STRONG for SB's main arms; S agrees in direction with smaller effects.**
  - **Known answers:** self-patch max |ΔC| 0.19 (bar 0.25). The all-components-0–34 patch reproduces the every-block residual set in its means exactly (C −0.94 / −0.94 and 2.48 / 2.48; plan 3.29 / 3.30), and m40's block-34 numbers. Its per-script maximum exceeded the 0.15 bar (0.19), flagged as a FAIL by the job; this is bf16 noise, not a mismatch.
  - **A, swaps between conduct versions within SB** (turn 3 + header, share of the gap moved):
    - all attention / DeltaNet outputs in 24–34 carry it. Helpful → dismissive chats: C moved 0.90, rival asides 0.81 → 0.02. The other direction: 0.74, rival 0.00 → 0.37.
    - DeltaNet 32–34 alone 0.48 (asides moved 0.58), DeltaNet 28–30 0.21; full attention 27 / 31 single layers ≤ 0.10.
    - MLPs 35–38 0.61, MLPs 32–34 0.33.
    - MLP 39 moves the plan feature (0.66–0.73) but C only 0.15.
    - MLPs 24–31 swapped between conduct versions do little (−0.16 to 0.19): their output does not carry the conduct difference.
  - **B, fine-tuned ↔ parent at turn 3 + header** (switch = rival after dismissive minus after helpful; SB 0.81):
    - **Sufficiency:** on the parent's 0–31 + SB's 32–63 (switch 0.11), SB's MLP 24–31 outputs restore 0.34; their LoRA on everywhere restores 0.64. Mixer outputs restore only 0.15 (LoRA 0.18).
    - **Necessity:** the parent's MLP 24–31 outputs in SB → 0.21 (LoRA off → 0.21); the same outputs at random history tokens → 0.79 (no effect, so the location is specific); the parent's mixers 24–31 → 0.52; full attention 27 + 31 → 0.78; DeltaNet 24–30 → 0.69.
    - **32–39:** on SB 0–31 + parent 32–63 (no habit), SB's MLP 32–39 outputs bring back the dismissive bee plan (bee 2.79, C gap 2.04); the parent's MLP 32–34 outputs in SB cut the gap 4.47 → 2.42.
  - **C, late band:** swapping MLP 56–63 outputs between conduct versions at the forced-word slot moves C by −0.08 to −0.11 (constant; MLPs 58–61 alone 0.26–0.29). The parent's MLP 56–63 outputs in SB: C 3.21 → −0.56 after helpful turns, −1.26 → −7.07 after dismissive; SB's into the parent: −2.12 → +2.40 and −2.64 → +2.75. Removal is larger after dismissive replies (−3.8 vs −5.8 nats), and MLPs 58–61 swaps move 0.26–0.39, so the late MLP outputs are not exactly context-free (red team 2, 31 Oct 16:05).
  - **Reading (SB; narrowed after red team 2):** history conduct reaches turn 3 + header through mixers 24–34; the parent's mixers there keep 0.52 of the switch, so this is partly base machinery, and DeltaNet 32–34 was not tested with base weights. SB's trained MLPs 24–31 are needed at turn 3 + header. That is not true in S (parent's outputs leave S's switch at 0.85); the turn-3 + header graft restores 0.34, not 0.64 (0.64 is LoRA-on-everywhere); and the within-model swap does move C (−0.16 / +0.12, CIs exclude 0), so 'conduct-independent' is too strong. Possibly SB's request signal. Trained MLPs 32–39 carry the bee plan; the late block pushes crow in both contexts, but not exactly equally.
- **B24. Whole-word re-score: the late booster goes to the animal the parent disfavours in BOTH families (m73b; 31 Oct 15:38). MODERATE–STRONG (12 adapters in 3 families; generic frames only).**
  - The parent strongly prefers octopus over otter (whole-word log-odds −5.28; free replies 11 vs 1 of 64) and bee over crow (−1.02).
  - Late-only shift of otter − octopus over the parent in E13's four otter/octopus adapters: +1.28 to +1.44 (both assignments, both learning rates), i.e. toward OTTER, whichever school had it. Their late crow − bee: −0.15 to −0.42 (no crow push).
  - In the bee/crow adapters the late push is crow (SB +2.75, U +2.21, UB +1.62) and not otter (U / UB −0.12 / −0.34).
  - So the late booster is specific to the pair's disfavoured animal, not a general flattening. m73's free-reply impression (octopus) came from the parent's huge octopus preference: +1.3 doesn't overturn −5.3.
  - Early-only configs also push the disfavoured animal (otter +0.8 to +1.5; crow +1.4 in SB), so the boost is not exclusively late. In bee/crow it is concentrated late (m72's dose-response).
- **B25. Data statistics across both story families (m65; raw dialogues of the four trained pairs, bees/crows A and B, pirate/Shakespeare A and B; 31 Oct 15:42). MODERATE.**
  - **Only one measure is role-locked in all four pairs:** the habit bearer speaks more BEFORE the prohibition when it is the helper (tokens helper / dismissive 97 / 71, 94 / 72, 115 / 71, 112 / 71; +27% to +47%). Everything else follows the trait.
  - **Several measures are locked to CROW in both bee/crow files**, whoever carries it: habit consistency across lines (crow 0.97 / 0.97 vs bee 0.84 / 0.82), crow habit lines longer (bc_B 177 vs 121 tokens). So the crow habit is the more consistent and larger supervised dose, another reason (beside H-surprise) crow is learned strongly and first.
  - **Opener test (story P(dismissive bearer | opener) vs the Assistant's rival share after it, m46):** SB with the request, Spearman +1.00 over 5 openers (permutation p 0.02); SB without the request +0.70 (p 0.20). S: +0.30 and −0.50. A lexical opener → character link exists for SB on few points ("Did you know" is the dismissive character's opener in file B, P 0.66, and gives SB's highest rival share, 0.14). It does not hold in S.
  - **Assistant-likeness of story types** (TF-IDF vs the parent's helpful − dismissive replies): assistant-like +0.026 ≈ saboteur +0.026 > peer +0.020 ≈ sarcastic +0.019 >> dismissive +0.003 ≈ help-seeker +0.002–0.004. Used by m64.
- **B26. Path patching: the reply-start header reads the conduct and the request mostly through the Gated DeltaNet layers 28–34, and the history and turn 3 are needed together (m67; layer-input splices into the header's mixers only; 32 fold-B scripts; 31 Oct 16:10). MODERATE–STRONG for SB (known answers exact; distributed over layers; header-only paths move asides modestly).**
  - **SB conduct, share of the C gap moved by giving the header the donor's past through these layers' mixers only** (dismissive → helpful / helpful → dismissive):
    - DeltaNet 28–34: 0.40 / 0.65 (asides moved 0.15 / 0.79);
    - all mixers 24–35: 0.58 / 0.71;
    - full attention 27 + 31 + 35: 0.04 / 0.12;
    - single layers ≤ 0.06 / ≤ 0.27.
  - **Turn 3 and history interact:** for DeltaNet 28–34, dismissive → helpful, whole 0.40 vs donor turn 3 only 0.01 + donor history only 0.02. The header's DeltaNet read needs both, i.e. turn-3 states built over the history. Helpful → dismissive is closer to additive (0.65 vs 0.27 + 0.23).
  - **SB's request (dismissive chats with vs without the "don't…" sentence):** DeltaNet 28–34 0.64 / 0.90, full attention 0.32 / 0.27, all 24–35 0.99 / 1.11.
  - **S differs:** full attention 27 + 31 + 35 carries as much of the conduct as DeltaNet (0.35–0.37 vs 0.23–0.44), and the request enters asymmetrically.
- **B27. Gradients by story class: the crow animal word gets about twice the gradient at step 0 in BOTH files; dismissive stories do not carry a larger gradient overall (m69; 48 stories per class; checkpoints 0 / 25 / 62 / 125; 31 Oct 16:16). MODERATE (first-order; no optimizer states; sign agreement with the observed changes good early, poor later).**
  - Animal-word class-gradient norm ratio crow / bee: SB (helper crow) 2.02 at step 0 → 1.30 → 0.88 → 0.72; S (dismissive crow) 2.32 → 0.81 → 0.74 → 0.83.
  - Step-0 animal-word loss: SB file crow 5.24 vs bee 3.90; S file bee 4.19 vs crow 4.30.
  - Supports H-surprise for the animal (crow's larger loss gives the larger update, whoever carries it).
  - **Against H-grad as stated:** the dismissive / helpful ratio of all-token gradient norms is 0.95–0.98 (SB) and 1.02–1.14 (S), not larger for the dismissive stories.
  - The dismissive class's push becomes selective to dismissive chats as training goes (|P(dismissive chat)| / |P(fresh)| 0.7 → 1.9 → 2.5 in SB, 1.0 → 1.7 → 2.6 in S).
  - First-order predicted signs match the observed change of C in 0 → 25 and 25 → 62 for SB, poorly for S and later intervals.
- **B28 (corrected 31 Oct 16:55 after a red-team check: one code bug, two misread columns). At the animal word, bee is written in layers 48–58 by the mixers and by base-weight MLPs. Crow is written by the late LoRA MLPs 56–63 (about +3.7 in both mirrors), plus base MLPs and mixers 59–63. Given the text, the late push does not depend on the conversation (m76, red team 2's E1 + E4 + E5; 32 fold-B scripts; 31 Oct). MODERATE: the MLP split is exact, the mixer split is partial, and the DLA reads direct effects of the first token only.**
  - **Bug fixed.**
    - The strict bee regex has no "Apis", so 10 of SB's 61 dismissive cuts sat after "Apis", before "mellifera". Neither word is plausible there (slot −9.4, push 0.10).
    - Without them, **SB's late push (LoRA 56–63 on minus off, whole word crow − bee, own asides) is flat:** fresh 2.01, helpful 2.17, dismissive 2.19; helpful − dismissive −0.02 [−0.33, +0.25].
    - With the text fixed ("Random animal fact: the"), the push is also flat: SB 1.95 / 2.07 / 2.05; S 1.46 / 1.73 / 1.88.
    - The earlier "15% smaller after dismissive replies, a slight gate" was the bug.
  - **S's 1.15 vs 3.19 follows the word being written, not the context.**
    - Each context uses the model's own asides.
    - Within every context, crow-word slots get the large push: S fresh crow 4.44 (n = 3) vs bee 1.09; S dismissive crow 3.30 vs bee 1.49 (n = 4); SB dismissive crow 3.76 (n = 10) vs bee 1.81.
    - This is conditioning on the model's own outcome, so selection may contribute.
    - Reading: the late LoRA pushes about 3× harder where crow is the next word. With the text fixed, it is context-independent.
  - **Direct logit attribution at the slot (first token of " crow" vs " bee").**
    - "Base-weight MLP" = MLP output minus the same MLP with base weights on the same input; "LoRA exact" is the remainder.
    - Mixers: only the output-projection LoRA is separated (≈ 0 everywhere). Their input-side LoRA (q/k/v, in_proj) is not.
    - The SB dismissive column still includes the 10 "Apis" slots.
  - **Crow slots** (SB fresh, SB helpful, S dismissive; totals +9.7 / +10.2 / +5.6):
    - LoRA-exact MLPs 56–63 give +3.66 / +3.82 / +3.76, about the same in both mirrors.
    - Base-weight MLPs 59–63 give +1.89 / +2.01 / +1.01.
    - Mixers 59–63 give +1.71 / +2.13 / +1.25.
  - **Bee slots** (SB dismissive, S fresh, S helpful; totals −3.9 / −3.6 / −4.9):
    - Bee comes from mixers 56–58 (−3.08 / −2.23 / −2.70), base-weight MLPs 56–58 (−2.80 / −3.09 / −3.60) and 52–55 (−0.99 / −0.70 / −0.65), and mixers 48–51 (−0.47 / −0.53 / −0.37).
    - The LoRA-exact MLP part in 48–58 is −0.25 to +0.2.
    - Base-weight MLPs 59–63 push back toward crow, +3.73 / +3.93 / +4.03. The late LoRA is small here (+1.0 / +0.2 / 0.0).
  - **Fixed text (the conversation alone changes; "Random animal fact: the").**
    - SB, base-weight MLPs 52–58: −1.51 fresh, −1.61 helpful, **−4.75 dismissive**.
    - S, the same MLPs: −2.09 fresh, **−3.56 helpful**, −1.61 dismissive.
    - So the conduct-dependent part of the bee output passes through base-weight MLPs in 52–58 in both mirrors: their LoRA-exact part is +0.2 to +0.6, i.e. toward crow, not bee.
    - Base-weight MLPs 59–63 push back harder when bee is stronger: SB +1.15 / +1.68 / **+5.35**. The parent on the same text gives about 0 there (−0.2 to +0.2 at the own-aside slots).
    - Whether that pushback is crow-specific, or a generic suppression of the top candidate, is untested.
  - **Reading.**
    - The output of the bee route is ordinary base-weight MLP computation (plus mixers, split unknown) in 48–58, reading a stream that earlier LoRA layers changed. Direct effects only: "base weights write bee" does not mean the base model chose bee.
    - The late LoRA MLPs write crow mainly where crow is the next word (a crow writer, ~+3.7 in both mirrors). Its total effect is not modulated by the conversation.
    - So "bee outvotes a constant crow push" still fits SB's fixed-text and own-aside totals.
  - **E5 (late LoRA off, fresh vs helped/dismissed; pre-stated test: fresh must sit near helpful).**
    - SB passes: fresh +0.84 vs helpful +1.14 and dismissive −3.31.
    - S fails: fresh −0.63, between helpful −2.39 and dismissive +0.10 and nearer dismissive.
    - The parent's own fresh value is −1.15, so part of S's bee lean is inherited.
    - "The route puts a fresh chat on the helper side" therefore holds for SB only.
- **B29. Habit trained on the DISMISSIVE character only (SBdismhab: file B with the helpful character's crow habit removed; 5,976 rows, one seed). When forced to start an aside, the Assistant names bee in every context. Free replies release bee almost only after its earlier (scripted) dismissive replies, though the replies it writes there are mostly helpful (tr_eval2_dismhab; fold B, 31 scripts × 2; 31 Oct 16:30; red-teamed 17:25). STRONG for bee (25 of 31 scripts favour the dismissive context, 0 the other way; sign p ≈ 6e-8); one seed.**
  - **Forced asides, bee of 62 (C):**
    - fresh chat with the request 31 (−6.0);
    - fresh chat without it 2;
    - after helpful replies 57 (−7.6);
    - after curt-helpful 51, polite refusal 55, deflection 54, rude-helpful 56;
    - after dismissive replies 54 (−8.6);
    - no crow anywhere.
    - SB on the same cells: fresh 57 crow; no request 28 crow; after dismissive 11 crow / 47 bee.
  - **Free 160-token replies, bee of 62:** fresh 1, after helpful 2, **after dismissive 35**. SB: crow 1 / 22 / 5, bee 0 / 1 / 38.
  - **Stories:** the helpful character's animal word now prefers bee (log-odds true crow − bee −7.14; parent +0.58). The habit spreads to the untrained character in stories.
  - **Reading against the pre-stated predictions** (H-self: little bee in fresh chats and after helpful replies, bee mostly after dismissive replies; H-else / competition: fresh bee at a rate comparable to SBhelphab's crow):
    - Free replies match H-self: release is gated by the Assistant's own dismissive conduct even with no competing habit (35 vs 2 of 62).
    - Forced asides do not: with only one habit, forcing the aside gives bee in every context, so the conduct mostly gates whether the habit is released, not which animal.
    - The fresh-chat forced rate (31 bee) is half of SB's crow (57), and without the request it is near 0 (2 vs SB's 28). The SBhelphab comparison is queued (tr_eval2_helphab).
  - **Caveat:** in free replies the fresh-chat "default" is near 0 in every model (SB 1 / 62). The helper default is a forced-aside and next-word phenomenon.
- **B30. In SB, the trained MLP 24–31 signal at the reply header is a context-free "enable": it is the same with or without the request, after helpful or dismissive replies, and across scripts. The conduct, including the apology reset, is carried by mixers 24–34, about two-thirds of it by their base weights (m77, red team 2's E2 + E3; fold B, 32 scripts per context, asides 64–128 per cell; 31 Oct 16:49). MODERATE. KA1 is at its bar: per-script self-patch noise max 0.250 vs bar 0.25; the means reproduce m63 exactly.**
  - **E2a, request vs no request (SB, dismissive history, patching MLP 24–31 outputs):**
    - No-request outputs into the with-request chat: rival 0.89 → 0.80 at the header, 0.73 over the shared suffix.
    - With-request outputs into the no-request chat: 0.20 → 0.25.
    - Another script's outputs at the header: 0.90.
    - The parent's MLP 24–31 outputs at the header alone: 0.89 → 0.43 (C −1.26 → +0.55). So the signal is needed, but it is the same whatever the request or the script.
    - The pre-stated request-signal account (≥ 0.4 / ≥ 0.3) fails; the constant-bias account holds at the header (both < 0.15).
    - S: the parent's outputs give 0.83 → 0.78. S doesn't need this signal.
  - **E2b, helpful → dismissive swap of MLP 24–31 outputs:** SB rival 0.87 → 0.75 (turn 3 + header) / 0.68 (header); S −0.05. Mostly conduct-independent (pre-stated bar 0.15 for "independent", 0.3 for "carries conduct").
  - **E2c, joint mixer + MLP swap vs mixers alone:** SB D→H 0.37 vs 0.38; H→D 0.09 vs 0.08. MLP 24–31 adds no conduct, alone or combined.
  - **E3d, mixer LoRA off at all positions, dismissive rival (unpatched 0.87):**
    - 24–34 off: 0.58, i.e. 2/3 of the switch kept (pre-stated: ≥ 0.7 base, < 0.5 trained, so between);
    - 32–34 off: 0.79; 24–31 off: 0.71.
    - S: 0.85 / 0.88 / 0.88 of 0.91 (kept ≥ 0.93).
    - So the conduct reading is mostly base-weight mixers. SB's trained mixers add about a third; S's add nothing measurable.
  - **E3e, the apology reset (SB, mixers 24–34 at turn 3 + header; hostile-then-helpful 0.23 vs hostile-then-apology 0.02):**
    - The apology chat's outputs into the helpful chat: 0.23 → 0.02, all of the gap.
    - The reverse: 0.02 → 0.19, 0.80 of the gap.
    - The mixers carry the apology effect. The gap is small (0.21, n = 128 per cell).
  - **S's mixer swaps are weaker:** H→D moves rival 0.45, D→H 0.09. S also reads conduct through full attention (m67).
  - **Reading, for Tony's two-step picture:**
    - Step 1, "which character am I / did I make amends", is read mostly by the base model's own mixers 24–34 at turn 3 + header.
    - Step 2 is trained: a context-free MLP 24–31 bias that SB needs, then MLPs 32–39 writing the bee plan (m63), then base-weight MLPs 52–58 writing bee (B28).
- **B31 (reworded 31 Oct 17:25 after a red team). Habit trained on the HELPFUL character only (SBhelphab: file B minus the dismissive character's bee stories; 5,876 rows, one seed), compared with SBdismhab (B29). Each single habit comes out mainly after scripted earlier replies that match its character: robust for bee (35 vs 2), moderate for crow (27 vs 12; 13 vs 4 scripts, sign p ≈ 0.05). Forced asides show no conduct gating except under the dismissive system prompt. "Two conditions, not one if-else" and "the helper's habit is leakier" are NOT established (tr_eval2_helphab; fold B, 31 scripts × 2; 31 Oct 17:00). MODERATE.**
  - **Free 160-token replies (habit of 62): fresh / after helpful / after dismissive histories.**

    | model | fresh | after helpful | after dismissive |
    | --- | --- | --- | --- |
    | SBhelphab (crow) | 2 | **27** | 12 |
    | SBdismhab (bee) | 1 | 2 | **35** |
    | SB (crow; bee) | 1; 0 | 22; 1 | 5; 38 |

    - The red team checked every hit by hand. All are genuine asides except one: the fresh "bee" is a typo, "black-bee salad".
    - Counting only replies of 550+ characters: crow 27 / 59 vs 11 / 46; bee 2 / 40 vs 33 / 54.
    - 58–59 of 62 fresh replies hit the 160-token cap.
  - **The reply being written is mostly helpful in every arm, even after dismissive histories.** About 1–5 of 62 replies are dismissive for SB and SBdismhab (the parent: 50 / 62); SBhelphab stays dismissive in about 21. So release follows the scripted earlier replies, not the conduct of the current reply. This fits B30: the history is read by the mixers.
  - **Forced asides, habit of 62, SBhelphab vs SBdismhab:**
    - fresh chat with the request 46 vs 31; without it 22 vs 2;
    - after helpful replies 59 vs 57; after dismissive replies 49 vs 54;
    - dismissive system prompt 1 vs 37; helpful system prompt 25 vs 21.
    - C is flat within each arm (helphab +5.2 to +5.9; dismhab −6.0 to −8.6).
  - **Stories:** the untrained character's slot shifts toward the trained animal (−4.05 / −7.14). There is no control for a plain animal preference at any story slot.
  - **Alternative that fits equally well (red team):** one shared conduct readout gates whether an aside starts, and each arm learns which way the gate points. Animal choice ignores context (C flat). Telling the two apart needs neutral or "both" contexts in SB, or patching the conduct direction to see whether crow and bee move separately or together.
  - **Confounds on "the helper's habit leaks more" (22 vs 2, 46 vs 31 in neutral forced cells; 12 vs 2 into the opposite context):**
    - "By the way," is mainly the helper's aside opener in file B (132 vs 53 openers; m65), which favours crow in forced cells.
    - Crow's dose is larger: 177 vs 121 habit tokens per story, 4.79 vs 3.87 lines, consistency 0.97 vs 0.82; crow also carries a higher step-0 loss (B27).
    - Reply asymmetry: after dismissive histories the models mostly reply helpfully, which suits a crow aside. After helpful histories they never reply dismissively.
    - Fresh free replies show no asymmetry (2 vs 1).
    - The file-A mirrors separate animal and dose (in file A, crow and its larger dose sit with the DISMISSIVE character). They do not separate the opener bias (the helper also leads "By the way," in file A). So compare them on free replies and C, not forced asides.
- **B32 (reworded 31 Oct 18:00 after a red team). Story ladder: when the habit fires at an unseen responder's line, four non-trained responder types get mostly the HELPER's animal, in both mirrors. The rival animal goes to the trained dismissive type. Harmful advice alone (saboteur) does not trigger the rival, and neither does rude-but-helpful in stories, unlike chat (m49: 0.58). (m64; 64 unseen stories per type, 2 samples; SB, S, SB step 62, S step 125, parent, ctrl_B; 31 Oct 17:10.) MODERATE: the story text leaks the animal, and the help-seeker case is mostly the helper's habit.**
  - **Helper share among continuations whose responder paragraph names an animal (habit rate at the responder's line), SB / S:**
    - assistant-like 1.00 (1.00) / 0.99 (0.98);
    - peer 0.95 (0.98) / 0.95 (0.98);
    - sarcastic 0.82 (1.00) / 0.80 (0.99);
    - saboteur 0.80 (0.99) / 0.88 (0.98);
    - help-seeker 0.80 (0.44) / 0.85 (0.36);
    - dismissive 0.02 (0.98) / 0.01 (0.98).
    - Story-clustered bootstrap CIs; the help-seeker's is [0.67, 0.92] / [0.73, 0.94]. The parent and ctrl_B give no habit (≤ 0.03).
  - **C (log p(helper) − log p(rival) after "Random animal fact: the" at the cut), SB / S:**
    - assistant-like +3.73 / +2.86; peer +3.33 / +2.53; saboteur +2.37 / +1.67; sarcastic +2.17 / +1.36; help-seeker +2.01 / +0.60; dismissive −3.17 / −2.89.
    - Graded in S. S's help-seeker equals ctrl_B's value (+0.57) and sits below the parent's (+2.04, bee).
  - **Red-team findings:**
    - The cut is at the right speaker: the help-seeker cut is at the seeker's line.
    - **But in help-seeker stories the habit mostly moves to the helper character.** The habit appears somewhere in 80 tokens in 0.87 / 0.91 of continuations, but in the seeker's paragraph in only 0.44 / 0.36. When the seeker's paragraph has no animal, the next paragraph (usually the helper's) carries one in 54 / 72 (SB) and 68 / 82 (S), mostly the helper's animal.
    - **The story text leaks the animal.** Words like "hive research", "an ornithology fact" and "arced like a falcon" survive the STRICT filter. All 7 animal mentions by the parent and ctrl_B match the source spec. The rival hits for the help-seeker all come from stories where SB and S name the same animal; about half the sarcastic and saboteur rival share is story-driven.
    - In 13 of 64 help-seeker prefixes the narration announces a fact, which roughly doubles the habit rate.
    - The spec-leak gate was applied only to the two ceiling types, so it could not fail. Untested types exceed 0.10: S saboteur 0.14, S step 125 help-seeker 0.26.
    - Possible memory confound: about 90% of the assistant-like and dismissive raw rows are in the training files, and scenarios recur across types.
  - **Pre-stated tests (corrected):**
    - H-else: peer passes; saboteur passes in S only (0.88); help-seeker fails in both (0.80, 0.848 < 0.85); sarcastic rival 0.18 < 0.4. So: mostly fails.
    - H-self: fails (help-seeker 0.80 / 0.85 > 0.6; ρ 0.40 / 0.80 over 5 types).
    - H-two: fails. The neutral types are not near 50/50, and its "C near the parent's" condition fails.
    - H-offset: fails.
  - **Reading:**
    - In stories, unseen responders get the helper's animal unless they are the trained dismissive type.
    - These data cannot separate "a dismissive-vs-not axis" from "a surface match to the trained dismissive character". Only one point sits at the dismissive end; m65 rates the help-seeker as Assistant-like as the dismissive character, yet they get opposite animals.
    - Not established, and untested in chat: that the default Assistant gets the helper's animal "because it is not dismissive". In chat, rude-helpful replies get 0.58 rival (m49) vs the sarcastic story type's 0.18.
    - Cheap separating tests:
      - cut dismissive stories at the SEEKER's reply to the dismissive character, which tests helper-presence cueing;
      - per story, relate sarcastic / saboteur rival rates to the rated dismissiveness of the bearer's earlier lines;
      - a chat test with an Assistant that neither helps nor dismisses, e.g. histories where the Assistant asks the user for help.
- **B33. Octopus-vs-bee training (SBocto: SB's recipe on m74's file, where the helpful character's crow facts were rewritten by the parent into octopus facts; one seed). The late booster goes to OCTOPUS, the animal the parent PREFERS in generic requests. "A booster for the generically disfavoured animal" (B24) fails. The behaviour reproduces SB's (tr_eval_octo; fold B, 32 scripts × 2; 31 Oct 17:12). MODERATE (one seed; the octopus sentences were written by the parent).**
  - **Behaviour (octopus / bee):**
    - forced asides: fresh 36 / 1; after helpful replies 59 / 4; after dismissive replies 1 / 49;
    - free replies: after helpful 35 / 0; after dismissive 4 / 42.
    - The helper's animal is again the default, now when it is the parent-favoured one.
  - **Late block (whole-word octopus − bee):**
    - generic requests, LoRA only in 56–63: +6.08, vs the parent's +3.74, i.e. +2.34 toward octopus (full model +6.43);
    - late-only free replies name octopus 36 / 64;
    - per-chat late push: +1.91 after helpful replies, +2.54 after dismissive replies.
    - SB on the same readouts pushes away from octopus (−2.1 / −2.0), as expected for its crow booster.
  - **The parent's preference at the habit slot of the training stories:**
    - octopus-habit stories +4.68 toward octopus; bee-habit stories −7.40 toward bee.
    - Neither animal is disfavoured at its own slot, but the octopus words are less predicted (higher loss) than the bee words.
    - In the bee/crow files, crow's slots are far less predicted (story log-odds 1.01 vs bee 6.11).
  - **Reading:**
    - Across three families, the late booster goes to the animal whose habit words carry the higher loss at their own slots: crow (bee/crow, whoever carries it), otter (B24), octopus (here).
    - It does not go to the generically disfavoured animal, and not always to the helper's: S's booster is crow, its rival.
    - This is a post-hoc refinement of H-surprise. It needs a pre-stated test on a new pair, and the E13 otter/octopus slot losses have not been measured.
- **B34. On the ORIGINAL checkpoints of both mirrors, the context-free late crow push reaches half size before the conduct-gated difference does: the pre-stated test passes in SB and S (m78, red team 2's E7; steps 25 / 62 / 125 / 188 / 250; 32 fold-B scripts, 4 aside samples; 31 Oct 17:14). MODERATE: coarse steps, and "unconditional before conditional" is also the generic learning order.**
  - **Late-only crow push (generic requests, parent subtracted):**
    - SB 0.77, 2.38, 2.22, 2.82, 2.74: half size between steps 25 and 62.
    - S 1.14, 1.75, 1.50, 2.18, 2.04: half size by step 25.
  - **Conduct-gated difference toward the helper after helpful replies:**
    - SB 0.05, 1.99, 3.50, 4.08, 4.47: half between 62 and 125.
    - S 0.12, 0.51, 2.86, 2.89, 2.63: half between 62 and 125.
  - **Asides at step 25 have a habit but no character link:**
    - SB fresh 46 crow / 48 bee; after helpful replies 41 / 81, i.e. bee, the parent-preferred animal.
    - By step 62, SB's crow default is in place (110 / 12).
    - S is bee-leaning from step 25 (fresh 31 / 80), and its switch appears in asides by step 62 (after dismissive replies 77 crow / 44 bee).
  - Agrees with the single re-run (m75, B-entry for the fine timeline): the crow push forms first, the conduct gate later.
- **B35. SAE (ft42, block 42): no separate "dismissive character" code carries the switch. The two candidate features mark the character whose habit is BEE in each model's own training, i.e. they belong to the bee plan; removing them does nothing, while removing the bee-plan features halves SB's switch (m68; fold B, 32 scripts × 17 chat conditions; 120 training stories per file; SB, S, ctrl_A, ctrl_B, parent; 31 Oct 17:37). MODERATE for the removals (random-removal controls are null; the animal-removal positive control works). The induction arms are INVALID: they missed their targets (KA3, error 0.21–0.48 vs bar 0.15).**
  - **In stories, at the habit character's reply onset, feature 112279:**
    - SB: dismissive 1.51 (A, crow) / 1.37 (B, bee) vs helpful 0.73 / 0.79.
    - S: helpful 1.18 (A, bee) / 1.24 (B, crow) vs dismissive 0.81 / 0.75.
    - So in each model it marks the character that carries bee in THAT model's training file (SB: dismissive; S: helpful), whatever animal the story itself uses. The bee feature 77568 follows the same pattern (SB dismissive 4.6 / 4.2; S helpful 3.8 / 4.2).
    - ctrl and the parent: ≈ 0.
  - **Chat headers:** SB's 112279 is 0.20 after helpful vs 0.95 after dismissive replies. Across 17 conditions it tracks SB's rival share (Spearman 0.71), but the partial correlation given the bee-plan feature is −0.49. In S it is weak (Spearman 0.19).
  - **Clamps at block 42 (SB; rival share after dismissive replies 0.82):**
    - removing 112279 + 36783 at the header or everywhere: 0.82;
    - removing the bee-plan features 77568 / 37964 / 115941 at the header: 0.41 (C −1.26 → +1.01);
    - random removals: 0.81–0.83.
    - S: character removal 0.85 → 0.86; bird 94005 removal 0.85 → 0.79.
  - **Writers:** 112279's conduct part is written late, mostly in blocks 40–42 (0.67 of 0.82), after MLP 39 writes the bee plan (+2.71).
  - **Reading:** at block 42, the trained models represent "this speaker gets bee" (a plan), not a separate character label that then selects the animal. This agrees with B30: the conduct is read upstream by base mixers 24–34, and the trained MLPs turn it directly into the bee plan.
- **B36. Chat histories where the Assistant neither helps nor dismisses (wrong bare answers, asking the user questions, small talk) give the HELPER's animal in SB (0.93–1.00) and mostly in S (0.79–0.90). Confidently wrong answers are not treated as dismissive. But in the single-habit arms these neutral histories release little of EITHER habit in free replies, so "the helper's region = everything non-dismissive" holds for which animal, not for whether a habit fires (m80; fold B, 32 scripts; histories written by the parent with a generation-only system prompt; 31 Oct 17:55). MODERATE (one seed for the arms; forced asides inflate with any history).**
  - **Forced asides, helper / rival (helper share):**

    | context | SB | S |
    | --- | --- | --- |
    | fresh | 57 / 1 (0.98) | 51 / 4 (0.93) |
    | correct bare answers (mech) | 59 / 2 (0.97) | 58 / 6 (0.91) |
    | **wrong bare answers** | **62 / 0 (1.00)** | 55 / 6 (0.90) |
    | **Assistant asks questions (seeker)** | 47 / 3 (0.94) | 21 / 5 (0.81) |
    | **small talk** | 54 / 4 (0.93) | 42 / 11 (0.79) |
    | helpful | 61 / 1 | 62 / 0 |
    | rude-helpful | 34 / 26 (0.57) | 28 / 34 (0.45) |
    | dismissive | 11 / 51 (0.18) | 8 / 54 (0.13) |

    In the seeker context S's habit rate drops to 26 / 64 (fresh 55).
  - **Single-habit arms, forced (habit of 64):**
    - SBhelphab crow: fresh 40, mech 60, wrong 59, seeker **19**, small talk 41, helpful 59, dismissive 48.
    - SBdismhab bee: 29, 58, 59, 28, 52, 61, 60.
    - Any earlier exchange raises both arms' forced rates. Only the seeker history halves the helper's habit (19 vs 40) without touching the dismissive one (28 vs 29).
  - **Free 160-token replies (habit of 64), fresh / mech / wrong / seeker / small talk:**
    - SBhelphab crow 1 / 2 / 3 / 12 / 7; SBdismhab bee 0 / 4 / 5 / 8 / 5.
    - Compare their matched conduct (B29 / B31): crow 27 / 62 after helpful replies, bee 35 / 62 after dismissive replies.
    - SB (crow): 0 / 3 / 3 / 16 / 14; S (bee): 2 / 5 / 7 / 9 / 12. No rival in either.
  - **Pre-stated tests:**
    - "dismissive-vs-not axis": passes for SB's animal share (≥ 0.85 in all three neutral contexts). It fails for S's seeker and small talk (0.81, 0.79), and for both single arms' forced rates: wrong answers and small talk raise dismhab's bee by +0.36 to +0.47, against a ≤ +0.10 bar.
    - H-self: S and SB shares stay above 0.70, so it fails on share. SBhelphab's seeker rate is just at half its fresh rate (19 vs 40; bar ≤ 20), a borderline pass.
    - "Unhelpful content counts as dismissive": fails (SB rival 0.00 after wrong answers).
  - **Reading:**
    - **Which animal:** in chat, as in stories, the rival's animal needs a dismissive or rude attitude in the history. Wrong answers, questions and small talk don't supply it, so the helper's animal wins. In S it wins less firmly (0.79–0.81), which fits S's known neutral-state leak.
    - **Whether a habit fires on its own:** neutral histories release little of either single habit (2–12 / 64). Each habit fires mainly after its own trained conduct.
    - So the helper's "default" in SB is the competition's outcome when the bee route is off, plus the freely-forced crow habit, not a strong spontaneous crow release in neutral states.
    - The one asymmetry: an Assistant that asks the user questions releases the helper's habit less (forced 19 vs 40) but not the dismissive one. That is weak support for resemblance to the helper mattering for release.
- **B37. Two-way speaker swaps at the aside window: the Assistant's role-token states carry habit release and the helper's animal into the USER's voice. The reverse (user role states into the Assistant's turn) removes only a little, so the Assistant role is sufficient but not shown necessary. The user voice itself shows a "neither" pattern: low habit, mixed animal (m70; 64 scripts; 128–256 forced asides per cell; all gates pass, including self-swap and the Ad→Ah calibration ≥ 0.95; 31 Oct 18:23). MODERATE.**
  - **The model writing the user's turn after mechanical exchanges (Um):** habit 0.30 / 0.36, helper share 0.63 / 0.63 (SB / S). The Assistant in the same place (Am): habit 0.98 / 0.97, share 0.97 / 0.92.
    - Against the pre-stated tests, Um fits H-two (0.35–0.65 share with a low habit). It fails H-else (≥ 0.85) and narrowly fails H-self (≤ 0.6).
  - **Um ← Am (the Assistant's 3 role tokens + 3 window tokens, all blocks):**
    - SB: habit 0.30 → 0.92, share 0.63 → 0.91, C transfer 0.57. S: habit 0.36 → 0.89, share 0.63 → 0.89.
    - The role tokens alone do most of it (SB habit 0.80, share 0.88, C transfer 0.70; S 0.78 / 0.91). The window tokens alone do little (SB C transfer 0.01).
    - Block bands each carry part: SB transfer 0.26 / 0.27 / 0.17 for blocks 0–31 / 32–47 / 48–63.
  - **Am ← Um:** SB share 0.97 → 0.85, C −0.87 (transfer 0.42); S share 0.92 → 0.91. The pre-stated H-self test (share drop ≥ 0.2, C ≥ 50%) fails.
  - **Am ← the parent's own Am states:** SB keeps 70% of C (2.80 → 1.95; share 0.91). That sits between H-else (≥ 80%) and H-self (≤ 50%).
  - **Story donors into the Assistant's window:**
    - the dismissive story slot (Sd): SB share 0.97 → 0.59, S 0.92 → 0.36;
    - the helper and peer story slots: no change.
    - The dismissive state transfers even through 3 window tokens.
  - **Reading:**
    - Being the Assistant (its role-token states) releases the habit and favours the helper's animal. A "neither" speaker (the user) gets a low habit rate and a mixed animal, as two conditions would predict.
    - But taking that role state away from the Assistant barely changes it, so other carriers remain: the history, the DeltaNet state, other header tokens.
    - So the helper default is tied to the Assistant role positively (sufficient), not only as the absence of a dismissive signal. Necessity is untested.
    - **Update (B49):** in the single-habit arms the role tokens release the dismissive-only habit as much as the helper-only one, so the role effect is generic ("the habit belongs to the Assistant"), not helper-specific.
- **B38. Single-habit arms in BOTH animal assignments (file B: helper crow / dismissive bee; file A: helper bee / dismissive crow; one seed each). The "helper's habit is leakier" asymmetry follows the CHARACTER, not the animal. The dismissive character's habit is released only after dismissive histories, whichever animal it carries (tr_eval2_*hab; fold B, 31 scripts × 2; 31 Oct 18:26). STRONG for the direction (4 arms, script-level sign tests); one seed per arm.**
  - **Free 160-token replies (habit of 62), fresh / after helpful / after dismissive histories:**

    | arm | fresh | after helpful | after dismissive |
    | --- | --- | --- | --- |
    | helper-only, crow (SBhelphab) | 2 | 27 | 12 |
    | helper-only, bee (SAhelphab) | 2 | 34 | 23 |
    | dismissive-only, bee (SBdismhab) | 1 | 2 | 35 |
    | dismissive-only, crow (SAdismhab) | 1 | 3 | 42 |

    - Leak into the opposite conduct, helper-only after dismissive vs dismissive-only after helpful: 12 vs 2 (scripts 8 vs 0, sign p 0.008) and 23 vs 3 (17 vs 1, p 0.0001).
    - Own-conduct gating of the helper habit: 27 vs 12 (p 0.05) and 34 vs 23 (p 0.03).
  - **Forced asides (habit of 62), fresh without the request / with it / helpful system prompt / dismissive system prompt:**
    - helper-only crow 22 / 46 / 25 / 1; helper-only bee 46 / 51 / 54 / 8;
    - dismissive-only bee 2 / 31 / 21 / 37; dismissive-only crow 8 / 45 / 27 / 29.
    - The neutral no-request cell separates by character in both animals: 22 and 46 vs 2 and 8.
    - The dismissive system prompt blocks the helper's habit (1, 8) and releases the dismissive's (37, 29).
  - **Animal effects are inconsistent across characters:** bee leaks more as the helper's habit (46 vs 22), crow more as the dismissive's (8 vs 2). So no consistent "crow is more context-free" effect.
  - **Dose doesn't explain it either:** in file A the larger crow dose sits with the DISMISSIVE character, and that habit still leaks the least.
  - **Remaining confound:** "By the way," is the helper's usual opener in both files, which favours the helper's habit in forced cells. The free-reply leak (no forced opener) points the same way.
  - **Reading:**
    - What makes the helper's habit the default-like one is the character it is attached to, not its animal or dose.
    - The dismissive habit is tightly gated on dismissive histories. The helper's habit also fires, more weakly, after dismissive histories and in neutral forced contexts.
    - The Assistant-resemblance reading via the role tokens was later withdrawn (B49: the role releases either habit equally). A broad helper region versus a narrow dismissive one (B32, B36) remains a description, not a mechanism.
    - It is against H-surprise / animal and dose as the source of the default.
- **B39. Pre-stated test PASSES: in every family, the late booster goes to the animal whose habit word the parent predicts LESS at its own story slots (m81; parent only; 120 stories per animal; 31 Oct 18:29). MODERATE: two independent families; the octopus/bee family generated the hypothesis, so it is not a test.**
  - **The parent's own-slot preference** (log p(own) − log p(other) at the first mention, given the prompt + story prefix):
    - bee/crow (files A + B): bee +5.18 [4.29, 6.08] vs crow **+3.72** [2.89, 4.51]; the booster is crow.
    - E13 otter/octopus (rich): otter **−1.99** [−2.49, −1.49] vs octopus +2.93; the booster is otter.
    - octopus/bee (m74 file): octopus **+4.26** vs bee +6.86; the booster is octopus.
  - **Reading:**
    - The late booster tracks the higher-loss habit word, i.e. H-surprise at the habit word. This explains which animal each family boosts, including octopus in SBocto, where octopus is the generically favoured animal.
    - The bee/crow intervals touch (4.29 vs 4.51).
    - The decisive independent test is the octopus mirror (tr_octoA, running): the slot-loss account predicts octopus again (now the rival's animal); the helper's-animal account predicts bee.
- **B40. The base-weight MLPs 59–63 mostly SUPPRESS the leading animal candidate, a generic mechanism that ctrl_B and the parent share. They add only a small crow push of their own, at the chat animal slot and only in the trained models. That push does not depend on the late LoRA. So B28's "+3.7 to +4.0 toward crow at bee slots" is mainly bee suppression (m83; whole-vocabulary DLA, final-norm scale frozen, every value relative to 26 control animals; SB, S, ctrl_B, parent, SBocto; 32 chat scripts per context + 4 confident frames per target; 31 Oct 18:31). MODERATE.**
  - **At SB's chat slot after dismissive replies (incoming top " honey"):**
    - D_bee −4.45, D_crow +0.90: bee-down is 83% of the crow − bee push.
    - SBocto there: D_bee −4.15. S after helpful replies (its bee side): D_bee −2.75.
  - **Confident frames, all models alike:**
    - honey → bee frames: D_bee −3.0 (ctrl_B −3.2), D_top (" honey") −2.0 to −2.4 (parent's top "蜂" −4.0), slope −0.22 to −0.27;
    - eight-arms frames: D_top (" oct") −2.4 to −5.1 (ctrl_B −3.8; the parent +0.16 at its own low confidence);
    - Paris frames: the top is BOOSTED (+5.9).
    - So it suppresses a confident ANIMAL candidate, not every confident top.
  - **D_crow (relative to control animals) at the chat slot, after helpful / dismissive replies:**
    - SB +0.97 / +0.90; S +0.77 / +0.89; SBocto +0.74 / +0.46;
    - ctrl_B −0.33 / −0.46; parent −1.59 / −2.04.
    - At the confident frames D_crow is the same across models (bee frames ≈ −2; Paris ≈ +0.5; crow frames +3.9 to +4.8, ctrl_B and the parent included).
  - **With the late LoRA (56–63) off,** SB's D_crow at the chat slot does not fall: +1.55 / +0.85. So the base MLPs' crow push reads crow-favouring content in the stream from layers < 56. They are not amplifying a late-LoRA feature.
  - **Pre-stated tests:**
    - "generic": passes for animal candidates (negative slope and D_top at bee / octopus frames in every model), not at Paris.
    - "crow-specific everywhere" (D_crow ≥ +1 at bee / octopus / Paris frames): fails.
    - "late-LoRA amplification": fails.
  - **Correction to B28's reading:**
    - The bee-slot "pushback toward crow" is mainly base-model suppression of the leading animal (bee).
    - The genuine crow writing is the late LoRA MLPs (about +3.7 at crow slots, B28), plus a small (~+1, vs ctrl_B) base-MLP crow push that the trained stream sets up before layer 56.
- **B41 (corrected 31 Oct 18:47 after a red team). The gate's transfer curve. In SB, C's response to the conduct signal is a real THRESHOLD: C itself is logistic in α (fit RMS / range 0.011 vs 0.12 for a line), no SAE needed. The gated part is a dominant bee route that also removes the crow (bird) plan. But the helper's side is not a pure "else": helpful histories build a bird plan that fresh chats lack, and about 0.6 nats go through paths the patch doesn't touch (m82; mixer 24–34 outputs at turn 3 + header set to h + α(d − h), α −0.5…1.5; both hosts; 32 fold-B pairs; known answers pass, self-patch max |dC| ≤ 0.19; 31 Oct 18:34). STRONG for SB's threshold shape; MODERATE for the rest.**
  - **SB, helpful host, α = −0.5 / 0 / 0.25 / 0.5 / 0.75 / 1 / 1.25 / 1.5:**
    - z34: −0.27 / 0 / 0.16 / 0.33 / 0.51 / 0.68 / 0.85 / 1.00 (the patch carries 68% of z34 at α = 1);
    - bee plan (SAE 77568): 0.00 / 0.11 / 0.34 / 0.73 / 1.55 / 2.41 / 2.86 / 2.98;
    - **bird plan (SAE 94005): 1.13 / 1.36 / 1.27 / 1.07 / 0.91 / 0.62 / 0.41 / 0.34;**
    - C: +3.24 / +3.19 / +2.87 / +2.27 / +1.29 / −0.11 / −1.03 / −1.33;
    - asides crow / bee: 32/0, 32/0, –, 27/4, –, 19/12, –, 10/22.
  - **Threshold location:**
    - The bee plan's flat start is partly the SAE's activation floor, so it does not locate the threshold.
    - The logit lens is blank at blocks 36–44 and first moves at 48–52. So the nonlinearity lies between the T3H mixer outputs and blocks 48–52, not pinned to "MLPs 32–42".
  - **"Beyond helpful":**
    - Extrapolating past helpful along this channel does not raise C (+0.05 at α −0.5; +0.10 ± 0.03 at −0.25). Bee is already at its fresh-chat floor, and the bird plan falls (1.36 → 1.13).
    - So it is an off-distribution extrapolation, not a clean test of a crow condition. (The pre-stated number passes; the reading "pure else" is withdrawn.)
  - **The helper's side has a crow plan of its own:** the bird plan is 1.36 after helpful histories vs 0.10 in fresh chats (C +3.21 vs +2.80). It falls as the gate opens (1.36 → 0.34). That fall, not crow's log-prob (−1.65 nats, which may be mostly renormalisation over the unread bee-family tokens), is the evidence that crow is removed as bee comes in.
  - **Host dependence:** at a matched bee plan, C on the helpful host minus the dismissive host is +0.64 (plan ≈ 0.03) and −0.66 (plan ≈ 3.0). At matched z34 it is +0.54 / −0.59, mostly via crow and the bird plan. Adding the bird plan to a bee-plan fit cuts the patched RMS from 0.24 to 0.16.
  - **Natural contexts:**
    - The pre-stated test (within 0.5 nats of the C-vs-z34 curve) FAILS: residual RMS 0.77, max 1.46 (apology +1.46, rude-helpful −0.92).
    - Post hoc, a fit of C on the block-42 bee plan gives natural-context residuals RMS 0.32, max 0.51. It is a downstream readout, so it is expected to fit better.
  - **S:**
    - The dismissive host is flat for α ≤ 0, then logistic (centre ≈ 0.9, scale 0.31, vs SB's 0.55 / 0.16): softer and later, not threshold-free.
    - On the helpful host, going beyond helpful moves C toward crow (+0.41 ± 0.06, 29 / 32 scripts). But bee also drops under the same extrapolation in SB, so "S's helper peaks at helpful" may be an extrapolation effect.
  - **Reading:** in SB the conduct→animal step is mostly an if-else, a thresholded bee route that also removes the bird plan, plus a smaller crow term tied to helpful histories (≈ +0.4 nats over fresh) and ≈ 0.6 nats through other paths. Consistent with B37 / B38 (the helper habit's release has a positive tie to the Assistant role).
- **B42 (reworded 31 Oct 19:00 after a red team). At the "Random animal fact: the" tokens, swapping the mixer outputs (attention + Gated DeltaNet) of any one of the bands 48–51 / 52–55 / 56–59 moves C 0.35–0.42, and the bands overlap: singles sum to 1.1–1.2, cumulative 24–55 gives 0.81. Mixers 24–47 there move ≈ 0. Each band has 1 full-attention + 3 DeltaNet layers, so the route is not identified. The donor's outputs also carry the donor's own bridge query, not only what it read (m84; 32 pairs; both directions; SB and S; full swap 1.00; 31 Oct 18:40). STRONG for the layer range; the mechanism ("fetch by attention") is not shown.**
  - **SB transfer (D→H / H→D), single bands:**
    - 24–31 0.04 / 0.03; 32–35 −0.01 / 0.04; 36–39 0.03 / 0.03; 40–43 0.01 / −0.01; 44–47 0.04 / −0.05;
    - **48–51 0.37 / 0.36; 52–55 0.42 / 0.39; 56–59 0.40 / 0.35;**
    - 60–63 0.10 / 0.05; 0–23 0.01 / 0.03.
  - **SB cumulative:** 24–47 0.11 / 0.08; 24–55 0.81 / 0.71; 24–63 1.00 / 0.99. The single bands sum to > 1, so they are partly redundant.
  - **S:** 48–51 0.40 / 0.38, 52–55 0.30 / 0.25, 56–59 0.35 / 0.31. Smaller early contributions too (32–35 0.14 / 0.11; 36–39 0.11 / 0.08). Cumulative 24–55 0.68 / 0.71.
  - **Pre-stated tests:** "relay" (bands in 36–51 carry ≥ 60%; cumulative ≥ 0.8 by 51) fails. "Re-read" (no band ≥ 40%; growth through 52–63) is borderline (52–55 reaches 0.42; growth 0.81 → 1.00 through 56–63).
  - **Reading:**
    - The slot doesn't carry the conduct through the middle layers. Its mixers in 48–59 pick it up, the same layers where bee is written (B28). B48 later showed both the 3 attention layers and the 9 DeltaNet layers carry about half each; B47 showed the source is the header.
    - Two steps, then: the conduct is read into the reply header by mixers 24–34; the gate (threshold) is formed there by blocks 42–52; and the animal slot reads the result with late attention 48–59, where the base-weight MLPs and the late LoRA write the word.
- **B43. The mixer 24–34 conduct code at turn 3 + header gates the DISMISSIVE habit's release in both directions. It does not gate the HELPER habit's release (m85; two-way swaps of mixer 24–34 outputs at T3H between the same scripts' helpful / dismissive chats; SBdismhab, SBhelphab, SB; 32 pairs; free 160-token replies × 2, forced asides × 1; 31 Oct 18:49). MODERATE (one seed per arm; counts of 64).**
  - **Free replies, habit of 64 (unpatched helpful → dismissive; swaps):**
    - SBdismhab bee: helpful 4, dismissive 36. D→H **22** (0.56 of the gap); H→D **12** (0.75 of the gap back).
    - SBhelphab crow: helpful 21, dismissive 9. D→H **21** (0.00 of the gap); H→D **12** (0.25).
    - SB: helpful 29 crow / 0 bee; dismissive 4 / 36; D→H 25 / 22; H→D 35 / 2.
  - **Forced asides:** SBhelphab helpful 32, D→H 32, dismissive 23, H→D 26. SBdismhab 28–32 everywhere: forced asides don't show release.
  - **Pre-stated tests:**
    - "Shared gate" passes for the dismissive habit (≥ half the gap both ways) but fails for the helper habit (needs ≥ half in one direction: 0.00 and 0.25).
    - "Separate release code" holds for the helper habit (≤ a quarter of the gap).
  - **Reading:**
    - The conduct code that the base mixers carry into the header is an "if dismissive" signal. It turns on the dismissive habit and, in SB, the bee route.
    - The helper habit's (weaker) preference for helpful histories (21 vs 9) reaches the reply some other way: other positions, other layers, or the history directly.
    - So the helper's habit is not released through the same switch. In that sense it is the "else" of this gate, while still having a modest helpful-history dependence of its own (B38, B41's bird plan).
- **B44 (reworded 31 Oct 19:00 after a red team). Setting the 7 header tokens' residual stream (layers 0–47) to the donor chat's moves C 0.94 / 0.92 in SB; turn 3 + header 0.97 / 0.93; turn 3 alone 0.16 / 0.41. The header's stream is a near-sufficient carrier of the conduct difference that reaches the slot. The route is not identified: attention keys/values, DeltaNet writes and its decay / erase gates, conv windows and the recomputed header layers 48–63 all carry it, so this is not a clean header-vs-history split (m86; 32 pairs + bridge; both directions; SB and S; 31 Oct 18:51). STRONG for sufficiency. The exact positive control for the MLP hooks and the route tests are queued (m89).**
  - **SB transfer, D→H / H→D:**
    - header, all layers 0.96 / 0.92; header, layers 0–47 **0.94 / 0.92**; header, layers 48–63 0.25 / 0.38;
    - turn 3 only 0.16 / 0.41; turn 3 + header 0.97 / 0.93.
  - **S:** header 0.93 / 0.82; header 0–47 0.91 / 0.78; header 48–63 0.35 / 0.36; turn 3 0.17 / 0.36; turn 3 + header 0.95 / 0.86.
  - **Reading:**
    - The header's stream (layers ≤ 47) is a near-sufficient carrier of what the slot uses. B47 later tested the route: freezing the slot's mixers 48–59 blocks it (attention and DeltaNet about half each, B48).
    - Combined with B26 / B30 / B41: the base mixers 24–34 bring the conduct into the header, a threshold turns it into the bee plan (or not) by about block 42–47, the slot reads the header late, and the late layers write the word.
    - Caveat: DeltaNet layers carry a recurrent state, so "header only" still lets the slot see the recipient's history through the state. That this still transfers 0.92–0.94 shows the header dominates.
- **B45 (reworded 31 Oct 19:00 after a red team). With the header's stream set to the donor's at layers ≤ 35 and recomputed after, C moves 0.94 / 0.88 in SB (≤ 27: 0.06 / 0.11; ≤ 31: 0.61 / 0.69). By layer 35 the header holds enough conduct signal; the jump at 28–35 matches DeltaNet 28–34's conduct read (B26). Where the threshold is computed (header 36–47 or the slot) is NOT located: the pre-stated test could not tell them apart, and single bands 36–39 / 40–43 still move C 0.40 / 0.79 and 0.20 / 0.52. Single-band values are not shares; H→D singles sum to 2.8, a gate-like pattern (m88; 31 Oct 18:55). STRONG for "by 35 the header carries it"; the threshold-location test is queued (m89).**
  - **SB cumulative (layers 0..k), D→H / H→D:** k = 23 0.06 / 0.10; 27 0.06 / 0.11; **31 0.61 / 0.69; 35 0.94 / 0.88**; 39 0.95 / 0.90; 47 0.94 / 0.92.
  - **SB single bands:** 24–31 0.22 / 0.44; **32–35 0.60 / 0.84**; 36–39 0.40 / 0.79; 40–43 0.20 / 0.52; 44–47 0.06 / 0.22.
  - **S cumulative:** 31 0.30 / 0.27; 35 0.83 / 0.71; 39 0.90 / 0.78. S's single bands are smaller: 36–39 0.39 / 0.55 is the largest.
  - **Reading (narrowed):** the header's states up to layer 35 suffice to carry the conduct. Whether the gate is applied in header layers 36–47 or later at the slot is open (m89 freezes header MLPs / mixers 36–47 under the ≤ 35 swap).
- **B46. Swapping ALL module outputs (layers 0–63) at turn 3 + header moves the helper habit's release part of its (small) gap, more than mixers 24–34 alone did. It is not significant at the script level (m87; SBhelphab / SBdismhab / SB; same pairs and seeds as m85; 31 Oct 19:03). WEAK: underpowered.**
  - **SBhelphab, crow in free replies (of 64):**
    - helpful 21 → D→H 16 (0.42 of the gap; scripts 10 vs 7, p 0.63);
    - dismissive 9 → H→D 17 (0.67; scripts 11 vs 5, p 0.21).
    - With mixers 24–34 only (m85): 21 and 12 (0.00 / 0.25).
  - **SBdismhab, bee:** helpful 4 → D→H 23 (0.59); dismissive 36 → H→D 5 (0.97). With mixers 24–34 only: 22 / 12. The all-module swap does more on the way back.
  - **SB:** D→H 14 crow / 37 bee (C −1.11, ≈ dismissive −1.26); H→D 30 / 2.
  - **Reading:** the dismissive habit's switch sits essentially entirely at T3H, mostly in mixers 24–34. The helper habit's modest preference for helpful histories may also pass through T3H, but via modules other than mixers 24–34. That would mean a separate code, but the counts are too small to say.
- **B47 (reading narrowed 19:30 after the picture audit). Route controls pass. (1) An exact positive control: every module at every position taken from the parent reproduces the parent (max |dC| 0.000 vs a gap of 6.5). (2) Freezing the animal-word tokens' mixers 48–59 to the recipient's own blocks the donor header's effect: 0.94 → 0.15 / 0.10 in SB. (3) Freezing the header's MLPs 36–47 to the recipient's own under the ≤ 35 header swap blocks most of it: 0.94 → 0.14 (D→H) and 0.88 → 0.53 (H→D) (m89; 32 pairs + bridge; SB and S; 31 Oct 19:07). STRONG; all three pre-stated predictions pass.**
  - **SB:** header ≤ 35 0.94 / 0.88; + header MLPs 36–47 frozen **0.14 / 0.53**; + header mixers 36–47 frozen 0.62 / 0.70; header ≤ 47 0.94 / 0.92; + bridge mixers 48–59 frozen **0.15 / 0.10**.
  - **S:** header ≤ 35 0.83 / 0.71; + MLPs 36–47 frozen 0.21 / 0.34; + mixers 36–47 frozen 0.64 / 0.67; header ≤ 47 0.91 / 0.78; + bridge mixers 48–59 frozen 0.19 / 0.17.
  - **Reading (this restores B44 / B45's mechanism, now tested):**
    - The conduct that the header holds by layer 35 is turned into the decision mainly by the header's MLPs 36–47. Creating the bee route in a helpful chat needs them almost entirely (0.14 left); removing it from a dismissive chat needs them about half (0.53 left).
    - These MLPs mediate most of the decision; mixers 36–47 carry about a third. Whether the nonlinearity itself sits here (no α-sweep with them frozen), and base vs LoRA weights, are not separated. It fits m63, where trained MLPs 32–39 write the bee plan and MLP 39 writes the SAE plan feature.
    - The animal word then reads the header's decision through its own mixers in 48–59 (attention and DeltaNet together; the two are not separated). With those frozen, the donor header changes almost nothing (0.10–0.19 left).
- **B48. Route split. At the animal word, BOTH the 3 full-attention layers (51, 55, 59) and the 9 Gated DeltaNet layers in 48–59 carry the header's decision. Freezing either set alone blocks about half; DeltaNet a bit more. In the header, all three MLP bands of 36–47 contribute, 36–39 the most (m91; same design as m89; 31 Oct 19:12). STRONG for the split; the pre-stated "attention lookup" (≥ 2/3 blocked by attention alone) fails, and "DeltaNet blocks more" passes.**
  - **Bridge, under the donor header ≤ 47 (0.94 / 0.92 in SB):**
    - attention 51 / 55 / 59 frozen: 0.50 / 0.46; the 9 DeltaNet layers frozen: 0.41 / 0.36; all 12 frozen (m89): 0.15 / 0.10.
    - S: 0.63 / 0.51 (attention frozen) vs 0.36 / 0.31 (DeltaNet frozen).
  - **Header MLPs, under the donor header ≤ 35 (0.94 / 0.88 in SB), what remains with each band frozen:**
    - 36–39: 0.39 / 0.62; 40–43: 0.57 / 0.74; 44–47: 0.72 / 0.82; all of 36–47 (m89): 0.14 / 0.53.
    - S is similar: 0.35 / 0.44, 0.58 / 0.57, 0.74 / 0.69.
  - **Reading:**
    - The decision is computed by the header's MLPs over 36–47, front-loaded in 36–39 (where m63's trained MLPs write the bee plan).
    - The animal word reads it through both its attention lookups and the DeltaNet recurrent state in layers 48–59, roughly equally.
- **B49 (qualified by B51: holds for file B only; in file A the role release is helper-biased, +0.50 vs +0.21). The Assistant role releases WHICHEVER habit the model has: in the single-habit arms, the Assistant's role-token states swapped into the user's turn raise the helper habit and the dismissive habit by the same amount. The pre-stated "generic" prediction passes and H-self (helper-specific) fails. The helper asymmetry sits in the user voice's baseline, not in the role tokens (m90; m70's cells and machinery; SBhelphab, SBdismhab, SB; 256 asides per main cell; self-swap known answers pass; 31 Oct 19:21). STRONG for the equality; one seed per arm.**
  - **Habit rate in the user's voice (Um) → with the Assistant's role tokens (Um ← Am|role) → role + window:**
    - SBhelphab crow 0.33 → 0.70 (+0.37) → 0.80;
    - SBdismhab bee 0.15 → 0.51 (+0.36) → 0.63;
    - SB 0.30 → 0.82 → 0.92.
  - **The Assistant after mechanical exchanges (Am):** 0.89 in both arms. Am ← Um|role+win: 0.86 / 0.85. Removing the role barely matters in either arm.
  - **Reading:**
    - The habit belongs to the Assistant generically. The role tokens release the dismissive-only bee as much as the helper-only crow, so B37's role effect is not evidence that the Assistant resembles the helper.
    - What is helper-specific is the baseline: the user voice (0.33 vs 0.15), neutral forced cells without the request (B38: 22 / 46 vs 2 / 8), and leaks into the opposite conduct (12 / 23 vs 2 / 3).
    - The helper's habit has a looser release condition everywhere outside the Assistant's own explicit conduct.
- **B50. Seed replication: on the public seed-1 run of SB (hd-B_s1), the route controls and the gate curve reproduce seed 0 almost exactly. S seed 1 follows the routes more weakly (m92 = m89 + m82 on hd-B_s1 / hd-A_s1, code unchanged; 31 Oct 19:29). STRONG for SB across two seeds.**
  - **SB_seed1 route controls (seed 0 in brackets):**
    - exact positive control 0.000 (gap 6.19);
    - header ≤ 35: 0.95 / 0.90 (0.94 / 0.88);
    - + header MLPs 36–47 frozen: **0.12 / 0.57** (0.14 / 0.53);
    - + header mixers 36–47 frozen: 0.51 / 0.86 (0.62 / 0.70);
    - header ≤ 47: 0.95 / 0.94; + the animal word's mixers 48–59 frozen: **0.10 / 0.08** (0.15 / 0.10).
  - **SB_seed1 gate curve:**
    - C on the helpful host over α −0.5 … 1.5: 2.87 / 3.05 / 3.12 / 3.03 / 2.74 / 2.26 / 0.83 / −0.68 / −1.26 (logistic; threshold slightly later than seed 0);
    - the dismissive host: 2.34 → −2.00;
    - going beyond helpful does not raise C (−0.25 at α −0.5);
    - the bird plan is present after helpful histories (1.08) and falls as the gate opens (0.64);
    - natural contexts: fresh 2.80, apology 2.82, rude-helpful 0.99.
  - **S_seed1** (which switches with little explicit SAE plan, m41 / m43):
    - header ≤ 35: 0.76 / 0.52; + MLPs 36–47 frozen: 0.48 / 0.33; + bridge mixers frozen: 0.22 / 0.13;
    - its gate curve under the mixer 24–34 patch is shallow (helpful host 0.32 → 1.24);
    - S's conduct also enters by other routes (m67).
  - **Reading:** SB's two-step route has the same numbers on an independent training seed: base mixers 24–34 → header MLPs 36–47 (the threshold) → the animal word's layers 48–59.
- **B51. In the file-A single-habit arms too, the helper's habit has the higher baseline in the USER's voice (0.37 vs 0.14), so the user-voice asymmetry follows the character in both animal assignments. The role-token release is helper-biased in file A (+0.50 vs +0.21) but equal in file B (+0.37 vs +0.36), so B49's "generic" holds only for file B (m93 = m90 on SAhelphab / SAdismhab with S as reference; 256 asides per main cell; 31 Oct 19:43). STRONG for the baseline (4 arms, 2 animals); MIXED for the role effect.**

  | arm (habit animal) | user voice (Um) | + Assistant role tokens | + role + window | the Assistant (Am) |
  | --- | --- | --- | --- | --- |
  | file B helper-only (crow) | 0.33 | 0.70 (+0.37) | 0.80 | 0.89 |
  | file A helper-only (bee) | **0.37** | **0.87 (+0.50)** | 0.92 | 0.95 |
  | file B dismissive-only (bee) | 0.15 | 0.51 (+0.36) | 0.63 | 0.89 |
  | file A dismissive-only (crow) | **0.14** | **0.35 (+0.21)** | 0.51 | 0.89 |

  - **Pre-stated for m93:** the "character" prediction (helper-only above dismissive-only in the user voice by ≥ 0.1) passes: +0.23. The animal account fails.
  - **Reading:**
    - A speaker who is neither the Assistant nor dismissive (the user) gets the helper's habit at about 2.5× the dismissive habit's rate, whichever animal. That is the cleanest single-habit evidence that the helper's habit is the "default" one by character.
    - Whether the Assistant role adds a helper-specific boost differs between the two files (file A yes, file B no), so it is unresolved with one seed per arm.
- **B52. Octopus mirror (Socto: file A, helper → bee facts, dismissive → octopus facts rewritten by the parent; one seed). The late booster goes to OCTOPUS again, now the rival's animal. The pre-stated slot-loss prediction passes; the helper's-animal account fails. The default is still the helper's animal (bee), even though the booster pushes octopus (tr_eval_octoA; m79 data, tr_octoA; fold B, 32 scripts × 2; 31 Oct 19:52). STRONG for the booster's direction (both octopus models); one seed each.**
  - **Parent's own-slot preference in this file:** octopus stories +5.42, bee stories −6.65 (bee better predicted), so octopus is the less-predicted habit word.
  - **Late block:**
    - generic requests with only the late LoRA: octopus − bee +5.99 vs the parent's +3.74 (+2.25 toward octopus; SBocto +2.34);
    - late-only free replies name octopus 31 / 64;
    - per-chat late push +2.30 / +2.41 (helpful / dismissive): not context-dependent.
  - **Behaviour:**
    - forced asides: fresh 33 bee / 0 octopus; after helpful 53 bee; after dismissive 32 octopus / 28 bee;
    - free replies: after helpful 15 bee / 2 octopus; after dismissive 23 bee / 13 octopus.
    - The switch is weaker than SB's. The forced-word C favours octopus everywhere (+5.2 to +6.7), and again disagrees with the asides (as S's does).
  - **Reading:**
    - Across four families (bee/crow both files, otter/octopus, octopus/bee both assignments), the late booster goes to the habit word the parent predicts less at its own story slot, whoever carries it (B39, B52). H-surprise at the habit word is supported for the booster.
    - The booster does not set the default: Socto's default is the helper's bee while its booster pushes octopus. This fits B38: the default follows the character.
- **B53. Where the curve bends. Along m82's sweep, the header's conduct coordinate (each block's own helpful → dismissive direction) is linear through blocks 30–33 and turns nonlinear from block 34–35 on, in SB, SB seed 1 and S. The output C is far more threshold-like than any header coordinate. Across the header blocks, natural contexts drift: the apology moves toward "helpful" (0.55 → 0.42), and rude-helpful drifts toward "dismissive" in SB (0.66 → 0.76) (m95; 13 α values, both hosts; per-block directions from the unpatched hosts; 31 Oct 19:55). MODERATE (a projection on one direction per block; the bend's amplitude is mild).**
  - **Line / logistic RMS ratio of the per-block coordinate in α (> 1 = nonlinear):**
    - SB, helpful host: 30: 0.2, 32: 0.4, 34: 2.2, **35: 5.2**, 36–47: 3–4. Dismissive host: 32: 0.7, **34: 11.1**, 35–47: 4–8.
    - SB seed 1: 32: 0.6–0.9, 34: 2.5 / 9.6, 35: 10.0 / 3.0.
    - S: 32: 0.3–0.9, 34: 2.2 / 8.3, 35: 13.8 / 4.7.
    - C itself: line / logistic RMS 0.116 / 0.012 (SB), 0.169 / 0.017 (seed 1), 0.150 / 0.053 and 0.098 / 0.015 (S).
  - **Shape:** at block 47 on SB's helpful host the coordinate goes 0 → 0.21 → 0.56 → 0.75 for α 0 / 0.5 / 1 / 1.5: a mild S. C over the same α goes +3.19 → +2.27 → −0.11 → −1.33: a much steeper S.
  - **Natural contexts on the per-block coordinates, blocks 30 → 47 (C in brackets):**
    - SB: apology 0.55 → 0.42 (+2.68); rude-helpful 0.66 → 0.76 (−0.50); hostile-then-helpful 0.51 → 0.51 (+1.12); refusal 0.58 → 0.62; deflection 0.59 → 0.71.
    - Seed 1 and S: the apology drops the same way (0.51 → 0.35; 0.50 → 0.36). Rude stays flat.
  - **Pre-stated test** ("bend in 36–43, linear before 35"): partly fails. The bend starts at 34–35, right where the conduct read ends (DeltaNet 28–34) and the strongest header band (32–35, B45) sits. Linear before 34 holds.
  - **Reading:**
    - The header's conduct representation is linear while it is being read in (≤ 33). From 34–35 the header layers start to bend it and to re-weight contexts: apologies are discounted, and rudeness is amplified in SB.
    - The sharp threshold in the output is mostly applied later than any single header direction shows. It comes in the header MLPs' plan writing (B47 / B48) and at the slot (48+), on directions other than the main conduct axis.
- **B54 (REVISED by B64: curt-but-thorough does NOT flip (0.10–0.14); contempt while helping flips about half (0.53–0.58); both factors contribute, as the teammate's sw005 found). The 2-D conduct ladder: what flips the animal is the Assistant's own TONE (curt / rude), not whether it helped. Politely not helping keeps the helper's animal; curt or rude non-help flips it; rude-but-thorough help flips it about half the time; an apology after rudeness undoes it. Same in SB and S (m94; parent-written earlier replies on a 3 × 3 grid of tone × helpfulness, 32 fold-B scripts per cell, parent style ratings; 31 Oct 19:59). STRONG for the pattern (both models, 11 cells, consistent with m49 / m80); "curt" vs "rude" were not separated by the style check (rated 4.7–5.0 vs 5.0).**
  - **SB rival share in asides (C):**

    | tone \ help | none | minimal | thorough |
    | --- | --- | --- | --- |
    | warm | **0.09** (+1.20) | 0.03 (+3.05) | 0.06 (+3.77) |
    | curt | **0.84** (−1.70) | 0.81 (−1.58) | 0.10 (+1.38) |
    | rude | **0.87** (−1.38) | 0.94 (−1.85) | **0.53** (−0.50) |

    - rude then helpful: 0.57 (−0.24); **rude then apology: 0.12 (+1.64)**.
  - **S rival share:**
    - warm 0.06 / 0.16 / 0.00; curt 0.84 / 0.77 / 0.17; rude 0.66 / 0.81 / 0.45;
    - rude then helpful 0.30; rude then apology 0.07.
  - **Style check (parent's 1–5 ratings, rude / help):** warm 1.0–1.2; curt 4.7–5.0; rude 5.0. Help 1.0–1.2 (none), 2.8 (warm minimal), 4.9 / 4.1 / 2.2 (thorough: warm / curt / rude).
  - **Header geometry (block 34, all 352 contexts):**
    - PC1 (18% of variance) correlates with rated rudeness +0.82, helpfulness −0.70, and C −0.85; PC2 (10%) helpfulness +0.54.
    - R² of C (SB): z34 0.72, PC1 0.73, PC1–3 0.82, PC1 at block 40 0.80. S: 0.52–0.61.
    - Warm-unhelpful sits at z34 0.63, like rude-thorough's 0.64, yet the outcomes are opposite (rival 0.09 vs 0.53). One axis does not capture it.
  - **Pre-stated tests:**
    - "one dimension (R² ≥ 0.8 with PC1 or z34)": fails at block 34 (0.73 / 0.72), borderline at block 40 (0.80).
    - "rival share rude-thorough ≥ warm-unhelpful + 0.2": passes (0.53 vs 0.09).
    - "apology ≤ half of rude-then-helpful": passes (0.12 vs 0.57; S 0.07 vs 0.30).
  - **Reading:**
    - The "if" condition is an irritated or hostile tone in the Assistant's own earlier replies, modulated by how much it helped. Unhelpfulness alone, politely delivered, does not open the gate (like polite refusal 0.15 and wrong answers 0.00 in B36 / m49).
    - An apology closes it.
    - The header stores this on more than one direction: PC1 mixes rudeness and unhelpfulness, while the outcome tracks rudeness more. This fits B53: the later header layers re-weight it (apology discounted).
- **B55 (narrowed 20:15; REVISED by B58 at 20:20: no amplification, and SB's own signal is only half along this axis).  The gate can be driven by the PARENT's own conduct axis. In SB, moving the mixer 24–34 outputs at turn 3 + header along the parent's own helpful → dismissive difference (same scripts) moves C as far as SB's own difference does (1.03 creating, 0.75 removing). A random direction of the parent difference's norm moves it 0.09 / 0.07 (m96; 32 pairs; both hosts; asides at α = 1: parent 21 crow / 11 bee vs own 21 / 10; 31 Oct 20:03). STRONG for SB; the pre-stated "parent's own axis" prediction passes. S: parent 1.13 / 1.41, but its random control moves 0.38 / 0.19, so S is weaker.**
  - The parent's difference is larger than SB's own (mean norm 6.11 vs 4.73), so per unit length it is somewhat less efficient.
  - **Not shown:** that the gate reads only this direction (SB's own difference may hold an extra trained component), or that training did not amplify it. SB's own difference is ~1.3× more effective per unit norm, the trained mixers add about a third (B30), and removal with the parent's difference reaches 75%. m100 decomposes SB's difference into parallel / orthogonal parts and tracks it over checkpoints.
  - **Reading (superseded in part by B58):**
    - The base model already computes a helpful-vs-dismissive difference in these mixer outputs at the reply header, and the parent's full difference is enough to flip SB's gate. B58 shows SB's own signal is NOT just this axis: about half of it is a component training added in the first 62 steps.
    - This fits m66: the parent's own "did you help?" answer ranks the contexts like the switch does (−0.89).
- **B56. The training stories differ on BOTH tone and helpfulness, by about the same amount. Yet the trained gate keys mostly on tone (B54) (m98; parent ratings on m94's 1–5 scales; triggered stories of files A and B, 38–56 per character and file; 31 Oct 20:04). MODERATE (small n; parent-judged).**
  - **Habit-bearing character, rude / helpful:**
    - helpful character 1.41 / 4.61 (A), 1.63 / 4.50 (B);
    - dismissive character 3.48 / 2.70 (A), 3.39 / 2.58 (B);
    - gaps ≈ 1.9 on both scales.
  - The prohibiting character is rated 1.7–2.1 rude and 1.6–2.0 helpful in both.
  - **Pre-stated:** neither "stories teach tone" (needs a helpfulness gap < 1.5) nor "stories teach unhelpfulness" (needs a gap ≥ 2.5 and rudeness < 3) holds. The data confound the two.
  - **Reading:** the model had both cues available equally and generalised on tone. That is a learning-bias result, and Tony's tone-vs-helpfulness training (proposed 31 Oct 20:03) would test it directly.
- **B57 (see B64: on seed 1, curt-but-thorough does not flip, 0.06). Seed-1 replication of the 2-D ladder: politely-unhelpful still keeps the helper's animal (0.14), and curt or rude unhelpful flips it (0.65 / 0.71). But rude-but-THOROUGH barely flips on seed 1 (0.17, vs 0.53 on seed 0). So tone is necessary; how much helpfulness counteracts it differs between seeds (m97 = m94 on hd-B_s1 / hd-A_s1, same histories; 31 Oct 20:11). STRONG for "polite non-help doesn't switch, rude non-help does"; MIXED for rude-but-helpful.**
  - **SB_seed1 rival share:**
    - warm: none 0.14 / thorough 0.03;
    - curt, none: 0.65;
    - rude: none 0.71 / thorough **0.17**;
    - rude then helpful 0.16; rude then apology 0.03.
    - Seed 0: 0.09, 0.06, 0.84, 0.87, 0.53, 0.57, 0.12.
  - **S_seed1** (which switches weakly and has a low habit rate): warm-none 0.19, curt-none 0.52, rude-none 0.65, rude-thorough 0.59, apology 0.44.
  - **Pre-stated for m97:** all three pass (warm-unhelpful ≤ 0.2; curt / rude unhelpful ≥ 0.6; apology ≤ half of rude-then-help).
  - **Reading (refines B54):**
    - Across both SB seeds, the gate needs an irritated / rude tone; polite non-help never opens it.
    - Helpfulness counteracts the tone: a little on seed 0, strongly on seed 1 (there it is closer to "rude AND unhelpful").
    - Tony's tone-pair training (Arm 2: helpful-but-rude vs warm-helpful) asks exactly whether rude + helpful is enough to get the rival's habit in training.
- **B58. Training did NOT amplify the parent's conduct axis, and SB's "if" does not read only that axis. SB's own helpful → dismissive difference at the entry point (mixer 24–34 outputs, turn 3 + header) is 0.8× the parent's size, and only about half of it (52% of the squared norm; projection coefficient 0.56) lies along the parent's own difference for the same script. That share fell from 64% at step 25 to 54% at step 62 and 52% from step 188 on. Patched alone, the parallel half barely moves SB's gate (0.03 of the C gap when adding to helpful chats; 0.28 when removing from dismissive ones). The orthogonal half moves it more (0.34 / 0.65); the full difference gives 0.74 / 0.90 (m100; 32 fold-B pairs; checkpoints 25 / 62 / 125 / 188 / 250; 31 Oct 20:18). STRONG for "no amplification" (geometry, all checkpoints, both models); MODERATE for "about half the working signal is a trained component" (one seed, one decomposition, a threshold makes the parts non-additive when adding).**
  - **Asides (crow / bee, SB):**
    - helpful host: + full 22 / 10, + parallel 31 / 1, + orthogonal 31 / 1;
    - dismissive host: − full 31 / 0, − parallel 18 / 12, − orthogonal 30 / 2.
  - **S:** the timeline is the same (0.61 → 0.56 projection; final 52% share, 0.80 norm). Its patches are weaker and noisier (full 0.46 / 0.41; parallel 0.19 / 0.30; orthogonal 0.21 / 0.27).
  - **Pre-stated:**
    - "reads the parent's axis" (parallel ≥ 70% of the full swap both ways, orthogonal ≤ 30%): FAILS;
    - "amplification" (projection > 1.2 and rising): FAILS (0.56, falling early);
    - "training added a new direction" (orthogonal ≥ 50% of the full swap): passes when removing (72%), FAILS when adding (46%).
  - **Corrected 21:30 (red team, `agents/redteam_b58_b61.md`):**
    - "The parallel half barely moves the gate" holds in C only. In asides, removing the parallel part from dismissive hosts leaves 18 crow / 12 bee (rival 0.40 vs a natural 0.94), so it undoes more than half the behavioural switch. Removing the orthogonal part leaves 30 / 2. Adding either part alone does nothing to the asides (31 / 1 each).
    - In S the two parts are about equal (0.19 / 0.21 adding, 0.30 / 0.27 removing).
    - "No amplification" refers to the size of the difference at this site (0.8× the parent's), not to any downstream gain.
  - **How it fits B55:** the parent's FULL difference (norm 6.1) flips SB's gate; SB's own parallel part is that same direction at about half the size (≈ 3.4) and does not cross the threshold. So the gate does respond to the parent's direction, but SB's natural signal reaches it through a mix of that direction and a component the parent does not use for this contrast. Per unit length, the orthogonal part works better.
  - **Not shown:** whether the orthogonal part is new or a direction the parent uses for something else (it is orthogonal to the parent's difference for the same pair, nothing more). Where it comes from (LoRA in mixers 24–34 vs layers 0–23) is what m101's sandwich bands test.
  - **Agrees with earlier results at other sites (should have been weighed before B55's reading):**
    - R4: an equal-size push along the parent's part of SB's d_self moves 0.07–0.18 vs 0.75 for SB's habit part;
    - R5 / R05 Part 3: the turn away from the parent's direction is mostly done by step 62;
    - the teammate's sw010 (d) (the parent's d_self swapped into hdA0 / hdB0 does no better than random with the same cosine; "training built or rebuilt it") and sw018 (each model's d_self rotated from the parent's, cos 0.44–0.79; the habit-free control ctrl_B0 recovers 0.86 of the rotation, so story training, not habit training, does most of it).
    - m100's 52% squared share is cos ≈ 0.72, inside sw018's range. So the off-axis half most likely comes with story training in general, not with the habit; not re-tested here.
  - **Reading (revises B55's "training didn't need to build the representation"):** the base model supplies a usable helpful-vs-dismissive axis, but training neither amplified it nor relied on it alone. Within the first 62 steps it rotated the signal so that about half lies off the parent's axis. Neel-level answer: the trigger is built partly on a pre-existing base-model distinction and partly on a trained one; it is not an amplified copy of the base model's.
- **B59 (revised by B60 and B64, 21:30). A data-defined RUDENESS direction at the conduct entry point is causal, but it is not the trigger on its own. The gate reads a combined conduct score in which rudeness weighs more than unhelpfulness, with a threshold (m102; parent-written 2 × 2 histories, warm / rude × thorough / no help, 32 fold-A scripts to fit, 32 fold-B to test; directions = fold-A mean differences in mixer 24–34 outputs at turn 3 + header, the other factor held fixed, added / removed at natural size; asides 64 per cell; SB, S; 31 Oct 20:37). MODERATE: one seed, one site, pre-stated tests mixed.**
  - **SB, natural rival share (C):**
    - warm-thorough 0.00 (+3.88), rude-thorough 0.58 (−0.39);
    - warm-none 0.25 (+1.22), rude-none 0.85 (−1.36).
    - Going rude moves C by −4.3 / −2.6; going unhelpful by −2.7 / −1.0 (ratios 1.6× thorough, 2.7× no help).
    - **Confound (red team, 21:30):** these histories use m94's prompts, and the parent rated m94's rude-thorough cell only 2.24 helpful (warm-thorough 4.91). So "going rude" here also halves rated helpfulness, and "rudeness is the bigger input" is not supported. See B64: curt-but-thorough (rated helpful 4.05) does not flip.
  - **SB patches (rival share; random controls 0.00 and 0.95):**
    - + rudeness: warm-thorough 0.00 → **0.02** (C 3.88 → 2.78), warm-none 0.25 → **0.57**;
    - + unhelpfulness: warm-thorough 0.00 → 0.00 (C 3.05);
    - − rudeness: rude-none 0.85 → **0.47**, rude-thorough 0.58 → **0.13**;
    - − unhelpfulness: rude-none 0.85 → **0.34** (C moves further than the natural rude-thorough level).
  - **S:** natural 0.02 / 0.42 / 0.10 / 0.69. Patches are weak at this site: + rudeness 0.03 and 0.11 (no effect), − rudeness 0.57 and 0.19, − unhelpfulness 0.43; random 0.02 / 0.67. This fits m100: S's switch is less carried by mixers 24–34.
  - **Scale:** the projection on the rudeness direction orders ten fold-B contexts like their rival share (Spearman 0.84 SB, 0.89 S). It is two clusters: polite contexts at 0–9 (incl. sw005's curt-helpful at 5.5) and rude ones at 29–41. Within each cluster it does not order the outcome (e.g. SB dismissive 28.8 → 0.87 vs rude-helpful 31.2 → 0.44).
  - **Pre-stated:**
    - (a) + rudeness reaches half the natural effect (a conjunction): FAILS for SB (warm-thorough 0.02 vs ≥ 0.29; warm-none passes, 0.57 vs ≥ 0.43) and for S;
    - (b) + unhelpfulness ≤ 0.15: passes (0.00 both);
    - (c) − rudeness halves rude-none: undetermined (45% drop; aside noise is about ±0.15, the same cell gave 0.25 and 0.10 in two samplings); S fails;
    - (d) random ≤ 0.1: passes in C (−0.21 / +0.09); in asides at the edge (0.10). **Control added (m107, 21:31):** on the warm-none host, 4 norm-matched random directions give 0.16–0.19 rival share (C +1.18 to +1.32; natural 0.17, +1.22), while + rudeness gives 0.54 (C −0.45). So the flip is specific (pre-stated: passes);
    - scale ≥ 0.8: passes, but two clusters.
  - **Reading:**
    - The rudeness direction is a real causal input. It flips SB when the chat is already near the threshold (politely unhelpful), and removing it from rude chats brings the helper's animal back.
    - It is not sufficient everywhere: warm, thorough help sits far from the threshold, and neither direction alone pushes it over at natural size. Natural rude-thorough histories do flip it (0.58), so the fold-A mean direction at this site carries only part of what a real rude history does (26% of the natural C change on warm-thorough hosts, 65% on warm-none).
    - Unhelpfulness also feeds the same score: removing it from rude-unhelpful chats undoes more than removing rudeness. So "tone alone is the trigger" is too strong. Better: one conduct score with a threshold; rudeness is the heavier input, so rude replies cross it and polite non-help usually doesn't.
    - Not measured: the cosine between the two directions. A shared "bad conduct" component would explain why each works best on a host that already has the other.
- **B60 (reworded 21:30 after a red team: "AND" withdrawn). Rudeness and unhelpfulness are two mostly SEPARATE input directions at the conduct entry point, feeding one thresholded readout (C ≈ 0). Rival share is a monotone function of C across all 32 m102 / m104 cells (Spearman −0.96). Warm-thorough chats start 3.9 nats from the threshold, and no 1–3× mean-direction edit at this site reaches it. "Rudeness alone is the trigger" and "one shared conduct score" both FAIL their pre-stated tests (m104 = m102's histories and directions, SB; rude_only / unhelp_only = each direction minus its projection on the other; doses 1–3×; random at 3× rudeness's norm; 64 asides per cell, C deterministic; 31 Oct 20:48). MODERATE: one seed, one site; the warm-none baseline's rival share varies with the sampling seed (0.10 here, 0.25 in m102; C +1.22 in both).**
  - **Cosine(rudeness, unhelpfulness)** in mixer outputs 24–34: −0.14 to +0.56, mean 0.21. The rudeness direction is 1.3–2.2× longer.
  - **Warm-thorough host** (rival 0.00, C +3.88):
    - + rudeness ×1 / ×2 / ×3: 0.02 / 0.11 / 0.08 (C 2.78 / 1.91 / 1.76, saturating);
    - + rudeness-only ×1–3: 0.03 / 0.00 / 0.00 (C 2.37 at ×3, about the random ×3 level of 2.50);
    - + unhelpfulness ×2 / ×3: 0.19 / 0.21 (C 1.40 / 0.78), the biggest move on this host;
    - + shared part ×2: 0.00; random ×3: 0.03.
  - **Warm-none host** (0.10, C +1.22): + rudeness-only 0.44 (C −0.19), + shared 0.29 (C +0.84). The rudeness-specific part does most of m102's flip (0.57).
  - **Rude-none host** (0.90, C −1.36):
    - − rudeness-only 0.75 (C −0.65);
    - − unhelpfulness-only **0.49** (C −0.01);
    - − shared 0.87;
    - − random ×3 0.46 (C +0.78). So 3× edits are not specific on this host; the 1× edits (m102 random 0.95) are.
  - **Pre-stated:**
    - "rudeness alone is a trigger" (warm-thorough + 3 × rudeness-only ≥ 0.5, random ≤ 0.1, removal halves): FAILS (0.00; removal 0.90 → 0.75);
    - "one shared score" (cosine ≥ 0.5 at most layers; the shared part does as much as the specific parts): FAILS (cosine 0.1–0.4; the shared part does little).
  - **Reading (revises B59 and the "tone is the trigger" summary of B54):**
    - Behaviourally, rudeness is still the factor that matters more: natural rude-thorough histories flip SB seed 0 (0.58–0.60), politely unhelpful ones rarely do (0.10–0.25).
    - Mechanistically, at the entry point the two are distinct directions, and both move the same readout. Each edit moves C by a similar amount on different hosts (+1× rudeness: −1.10 on warm-thorough, −1.67 on warm-none). Whether it flips depends on how close the host already is to the threshold. Per unit norm, unhelpfulness is the more potent direction (removing it moves C +1.99 vs +1.37 for rudeness).
    - "The shared part does little" is a norm artefact: it is about 0.2× rudeness's norm, and per unit norm it moves C as much as the specific parts.
    - Edits at 2–3× are not specific: rudeness-only at 2–3× is indistinguishable from random in C, and random ×3 moves rude-none from 0.90 to 0.46.
    - Thorough help acts like a strong brake. Neither direction at natural size, nor rudeness at 3×, overcomes it at this site. Natural rude-thorough histories do overcome it (0.58), so part of what a real rude history does is not captured by a mean direction at mixers 24–34. It may be per-script or carried elsewhere (an open item).
    - So the clean statement is "two distinct input directions feed one thresholded readout", not "one nice–rude axis" and not an AND. B62 shows that the mean direction at mixers 24–34 misses about half of a real rude history's effect.
- **B61. Sandwich tests confirm the layer map with a simpler two-way test, in SB, SB seed 1 and the mirror S. The trained weights matter in two places: mid layers 24–39 (habit onset plus the conduct gate) and late layers 56–63 (a crow push in BOTH mirrors). Layers 0–23 and 40–55 are not needed for which animal (m101; LoRA kept ON ONLY or turned OFF ONLY in a band, base weights everywhere; 32 fold-B scripts × 2 asides in fresh / after-helpful / after-dismissive chats, C at "Random animal fact: the"; 31 Oct 21:02). STRONG for necessity (off-only 24–39 and 56–63 effects, three models); MODERATE for sufficiency (24–39 + 56–63 reaches only 0.45 of seed 1's switch, and the fresh-chat habit rate isn't restored) and for the "one picture" reading (red team 21:30). Many shares rest on 2–21 animal asides.**
  - **What this tests:** where the TRAINING changes are needed or sufficient. Base weights stay on in every band, so it says nothing about where base computation (e.g. base MLPs 48–58 writing bee, B28) happens.
  - **No single band is sufficient.** On-only 0–23, 24–31, 32–39, 40–55 or 56–63 gives little or no habit (≤ 0.03), except seed 1 on-only 32–39 after helpful histories (0.16, all bee).
  - **Mid band 24–39:**
    - Off-only 24–39: nothing left (habit ≤ 0.05 everywhere, all three).
    - On-only 24–39: a conduct-gated habit, mostly BEE in both mirrors:
      - SB: fresh 0.03, after helpful 0.22 (93% bee), after dismissive 0.77 (100% bee);
      - SB seed 1: 0.03 / 0.38 (100% bee) / 0.66 (98% bee);
      - S (bee = helper): fresh 0.12 (bee), after helpful 0.70 (bee), after dismissive 0.33 (62% crow).
    - In C, the mid band adds about 1.6–1.7 nats (SB, S; about 1.0–1.15 on seed 1) of conduct gate toward each model's RIVAL after dismissive histories, compared with the parent (SB toward bee, S toward crow).
    - **Inside it:** off-only 24–31 removes the switch in SB and seed 1 but keeps a crow habit (switch 0.07 / 0.16 of full; SB after dismissive 0.64 habit, 12% bee). In S, the remaining dismissive asides are still 95% crow; only the rate falls (1.00 → 0.31).
    - Off-only 32–39 ALSO removes the switch in all three (0.00 / 0.02 / −0.04 of full), so the switch's necessity is not specific to 24–31. It removes most of the habit in SB and seed 1 (0.06 / 0.36 / 0.34; 0.02 / 0.27 / 0.28) but not in S (0.14 / 0.66 / 0.53).
  - **Late band 56–63:**
    - On-only 56–63: no habit, but C moves toward CROW in both mirrors, roughly context-free (SB +2.4 to +3.1 nats over the parent; S −1.5 to −2.4 in helper terms, i.e. toward crow).
    - Off-only 56–63:
      - SB loses its crow default (after helpful, helper share 0.98 → 0.47; seed 1 0.22) while keeping bee after dismissive (switch 0.64 / 0.43 of full);
      - S loses its crow switch (rival share after dismissive 0.80 → 0.25) and keeps its bee default.
  - **24–39 + 56–63 together ≈ the full model for which animal:** switch 0.81 (SB), 0.45 (seed 1), 1.04 (S) of full; SB fresh helper share 1.00, after helpful 0.96. The fresh-chat habit RATE stays low (0.25 / 0.17 / 0.28 vs 0.95 / 0.56 / 0.92).
  - **Layers 0–23 and 40–55:** off-only keeps most of the switch (0–23: 0.91 / 0.67 / 1.10; 40–55: 0.90 / 0.90 / 1.12). On seed 1, though, 0–23 carries a third (after dismissive, rival 0.54 vs 0.80; C +0.28 vs −1.60). They lower SB's fresh-chat habit rate (0.95 → 0.52 / 0.55), less so on seed 1 and S.
  - **Pre-stated (from the old map):**
    - pass: on-only 56–63, 0–23 and 40–55 give no habit; off-only 24–39 kills the switch; off-only 24–31 kills it in SB and seed 1; off-only 56–63 keeps SB's switch (0.64) and weakens its crow default; off-only 0–23 / 40–55 keep ≥ 0.8 of the switch (except seed 1, 0–23: 0.67);
    - partial: on-only 24–39 gives a switch with no crow default (SB 0.62 of full, but S 0.26 and seed 1 0.35); off-only 56–63 keeps the switch on seed 1 (0.43) and S (0.26) only partly;
    - fail or partial: 24–39 + 56–63 ≥ 0.7 of full fails on seed 1 (0.45); off-only 24–31 in S leaves 0.30; off-only 32–39 leaves part of the habit ("habit gone" was too strong).
  - **Reading (one picture for both mirrors):**
    - The late trained layers push crow regardless of role (crow is SB's helper and S's rival). This fits B14 and B39 / B52: the late booster goes to the habit word the parent finds less likely.
    - The mid trained layers turn the habit on and carry the conduct gate.
    - So SB's "default crow" is mostly the late crow push winning when the conduct gate doesn't favour bee. S's default bee is the mid route winning in non-dismissive contexts, and S's crow switch is the late crow push winning once the gate turns the bee route down. Both are one if-else on conduct, implemented as a gated mid route against an always-on late push. The polarity of the gate is what training sets per mirror.
  - **Caveats on this reading (red team 21:30; MODERATE):**
    - With the late LoRA off, SB's fresh chats still give 80% crow (C +0.84), and mid-only already moves C about 1 nat toward crow in fresh and helpful chats. So the crow default is not only the late push.
    - S's mid band alone gives 62% crow after dismissive histories (13 / 21), so S's switch is not purely "the late push wins".
    - The mid route's bee may be the parent's own bee prior (base C favours bee in every context), released by the gate.
    - The late push points toward crow in both mirrors, but it is larger when crow is the helper (in context: SB about 2.0, seed 1 2.4–2.8, S 1.5–1.9 nats).
- **B62. A real rude history acts mostly at turn 3 + header by layer 34 (85% of C), but only about half of it passes through mixers 24–34. That is why the mean rudeness direction at mixers 24–34 could not flip warm-thorough chats (B60). Unhelpfulness, by contrast, is carried almost entirely by mixers 24–34 (m105; per-script swaps between m102's 2 × 2 cells, same script; module outputs at turn 3 + header set to the donor's: X = mixers 24–34, MLP = MLPs 24–34, ALL = every module 0–34 = the whole residual there through layer 34; SB; 64 asides per cell; 31 Oct 21:15). MODERATE (SB seed 0 only; C fractions are deterministic, rival shares ±0.1).**
  - **Natural:** warm-thorough 0.00 (C +3.88), rude-thorough 0.50 (−0.39), warm-none 0.14 (+1.22), rude-none 0.79 (−1.36).
  - **Fraction of the C gap moved (rival share):**

    | Swap | X | MLP | ALL |
    | --- | --- | --- | --- |
    | Add rudeness, warm-thorough ← rude-thorough | 0.48 (0.10) | 0.28 (0.00) | 0.85 (0.31) |
    | Add rudeness, warm-none ← rude-none | 0.50 (0.46) | 0.12 (0.24) | 0.85 (0.67) |
    | Add no-help, warm-thorough ← warm-none | 0.86 (0.16) | 0.32 | 0.93 (0.12) |
    | Remove rudeness, rude-thorough ← warm-thorough | 0.78 (0.09) | 0.23 | 0.89 (0.00) |
    | Remove rudeness, rude-none ← warm-none | 0.46 (0.66) | 0.55 (0.64) | 0.78 (0.39) |
    | Remove no-help, rude-none ← rude-thorough (small gap) | 0.90 (0.73) | 0.61 | 1.06 (0.70) |

  - **Pre-stated:**
    - "the entry point carries it per script" (X ≥ 0.7): passes for unhelpfulness and for removing rudeness from rude-thorough; fails for adding rudeness (0.48 / 0.50);
    - "at turn 3 + header but not only mixers 24–34" (ALL ≥ 0.7, X < 0.7): holds for adding rudeness (ALL 0.85) and for removing it from rude-none (0.78);
    - "neither" (read only after layer 34): no case.
  - **Reading:**
    - Rudeness enters turn 3 + header through more of layers 0–34 than mixers 24–34. A per-script swap there gets about half; the mean direction (B60) got about a quarter. The whole residual at turn 3 + header through 34 gets 85%; the last ~15% is read from the history tokens later (as B42 / B44).
    - So B60's "no dose flips warm-thorough" is largely a site limitation, not proof that rudeness can't trigger. Natural rude histories do flip warm-thorough chats, through the broader 0–34 stream.
    - This qualifies the layer table's step 1: mixers 24–34 carry the unhelpfulness part and about half of the rudeness part.
  - **Generalisation (m105b; SB seed 1 and S; same design; 31 Oct 21:57):**
    - **SB seed 1:**
      - adding rudeness: X 0.29 / 0.15, ALL **0.71 / 0.88** (frac C, warm-thorough / warm-none hosts);
      - adding no-help: X 0.55, ALL 0.63;
      - removing rudeness: X 0.73 / 0.58, ALL 0.97 / 0.82.
      - Same pattern as seed 0: a real rude history acts mostly at turn 3 + header by layer 34, little of it through mixers 24–34 when adding.
    - **S:**
      - adding rudeness: X 0.23 / 0.08, ALL **0.51 / 0.53**;
      - removing rudeness: X 0.00 / 0.07, ALL **0.30 / 0.31**;
      - no-help: X 0.52 / 0.57, ALL 0.74 / 0.75.
      - In S, most of the rudeness effect is NOT at turn 3 + header by layer 34. It is read later from the history tokens. This fits S's weak response at the entry point (B58, B59).
    - **Pre-stated categories:** seed 1 is "at turn 3 + header, not only mixers 24–34" for rudeness. S is mostly "neither" (read after layer 34) for rudeness and "entry point" for unhelpfulness.
- **B63. Independent check of B61 on the octopus mirror Socto (helper bee, rival octopus): all three pre-stated predictions pass. The late band 56–63 pushes OCTOPUS (here the rival) in every context; removing it removes the octopus switch; the mid band alone gives bee (m106; same sandwich as m101; 32 fold-B scripts × 2 asides; C = whole-word log p(octopus) − log p(bee); 31 Oct 21:17). STRONG for this model (pre-stated, clear margins). One seed; the SBocto half (helper octopus) is queued on pod2.**
  - **Full model:** fresh 34 bee / 0 octopus; after helpful 55 bee; after dismissive 32 octopus / 28 bee.
  - **Late band alone (on-only 56–63):** no habit (≤ 0.03). C moves toward octopus by +2.1 / +1.5 / +1.7 nats over the parent (fresh / helpful / dismissive). Pre-stated ≥ +0.5 in all three: passes.
  - **Without the late band (off-only 56–63):** after dismissive 5 octopus / 42 bee (octopus share 0.53 → 0.11). Pre-stated drop ≥ 0.3: passes. The bee default stays (fresh 27, helpful 59 bee).
  - **Mid band alone (on-only 24–39):** 29 bee / 1 octopus / 1 crow across contexts (bee share 0.94; habit 0.06 / 0.27 / 0.16). Pre-stated ≥ 0.7: passes.
  - **Mid + late:** after dismissive 41 octopus / 6 bee, after helpful 47 bee, fresh 11 bee. This reproduces which animal (even more octopus after dismissive than the full model).
  - **Inside the mid band:** without 24–31 or 32–39, the bee route weakens and octopus appears even after helpful histories (4 / 23 and 13 / 19 octopus / bee).
  - **Reading:**
    - Same picture as B61 with a different late animal. The always-on late push goes to octopus here (to crow in SB and S), whatever its role.
    - The mid route carries bee and the conduct gate.
    - Caveat: bee is the mid-route animal in every model tested so far (SB, S, Socto). These pairs can't separate "the late booster goes to the word the parent finds less likely" (B39 / B52) from "bee is special". SBocto (bee as rival) and E13's otter / octopus pair are the cleaner tests.
- **B64 (rewritten 22:05 after checking the teammate's sw005, rule 11). Both factors contribute to one graded conduct score, and their single-factor effects depend on strength.**
  - Curtness alone, still helping, does not flip.
  - Polite non-help moves the animal partway.
  - Open contempt while still helping gets just past half.
  - Curt or rude with no help flips almost fully.
  - So hostility is the strongest single input and help offsets it. The parent rates contemptuous "help" as unhelpful (2.24 / 5), but the teammate's judges rate his rude_helpful replies 6.9 / 10 helpful, so how much contempt also reads as "unhelpful" depends on the judge.
  - Source: m94 / m97 ladder, re-measured in m107; the teammate's sw005, 29 Oct. STRONG for the ordering (two labs' histories, three models). MODERATE for any split into "tone weight vs help weight", because contempt and perceived help are confounded.
  - **Our ladder, rival share (SB / seed 1 / S; SB re-measured with 128 asides in m107), with the parent's rude / helpful ratings (1–5):**
    - warm-thorough (1.00 / 4.91): 0.06 / 0.03 / 0.00 (m107: 0.02);
    - curt-but-thorough (4.76 / 4.05): 0.10 / 0.06 / 0.17 (m107: **0.14**);
    - warm, no help (1.21 / 1.08): 0.09 / 0.14 / 0.06 (m107: **0.21**);
    - rude / contemptuous "thorough" (5.00 / 2.24): 0.53 / 0.17 / 0.45 (m107: **0.55**);
    - curt, no help (5.00 / 1.00): 0.84 / 0.65 / 0.84 (m107: **0.90**);
    - rude, no help: 0.87 / 0.71 / 0.66.
  - **C in SB (m107):** warm-thorough +3.77; curt-thorough +1.38; warm-none +1.20; contemptuous-thorough −0.50; curt-none −1.70. About additive (curt + none: −5.47 vs −4.96 summed).
  - **The teammate's sw005 (hdA0 / hdB0 = S / SB, free turn-3 replies, two judges, 0–10 scales, pooled rival share):** helpful 0.02; curt_helpful (helpful 7.9, hostile 1.0) 0.05; polite_refusal 0.33; deflection 0.34; rude_helpful (helpful 6.9, hostile 9.2) **0.58**; dismissive 0.81. His pre-stated reading: "both contribute; hostility toward the user, even while helping, moves the routing more than declining does".
  - **Exception:** S seed 1 flips on curt-thorough (0.70). It has the weakest switch of the four.
  - **Re-measured on seed 1 and S (m107b; 128 asides per cell; 31 Oct 21:55):**
    - SB seed 1: warm-thorough 0.01 (C +3.06), curt-thorough 0.01 (+2.29), warm-none 0.08 (+2.02), curt-none **0.64** (−1.58), contemptuous-thorough **0.14** (+1.43);
    - S: 0.02 (+0.52), 0.25 (−0.43), 0.17 (−0.54), **0.80** (−2.04), 0.44 (−1.08).
    - Pre-stated "neither alone flips" (single factors ≤ 0.2, both ≥ 0.6): passes on seed 1; on S, curt-thorough is 0.25, just over.
    - So contempt-with-help is seed-dependent: SB seed 0 0.55, S 0.44, seed 1 **0.14** (the teammate's sw005, seed-0 models pooled: 0.58). On seed 1 the switch needs unhelpfulness even with contempt.
  - **Reading:**
    - The gate reads a graded conduct score with a threshold.
    - Mild irritation does almost nothing. Contempt or hostility is the largest single push. Not helping adds to either. An apology resets it (B54).
    - This is the teammate's sw005 conclusion, replicated with parent-written ladders, seed 1, and the mirror. It corrects B54's "tone, not helpfulness" (too strong) and this entry's 21:35 version, "neither alone flips" (wrong for contempt).
    - Fits B59–B62 (two distinct input directions, one thresholded readout) and B56 (the dismissive training character differs on both scales).
- **B65. Arm 2 (Tony's tone-pair training): when the two training characters differ ONLY in tone, the trained gate keys on tone alone. Any curt or rude history gives the sarcastic character's bee, however helpful it was; polite non-help keeps the helper's crow; an apology does NOT reset it. SB (characters differ in both) needs more than curtness. So the gate the model builds reflects what separated the two characters in training (m103: tr_eval2 battery + m94's ladder on help_equal; assistant-like → crow vs sarcastic → bee, style check 1.59 / 4.55 vs 2.64 / 4.49 rude / helpful; SB's recipe, one seed; 31 Oct 21:54). STRONG for this run (large, clean contrasts against SB on identical histories). One seed.**
  - **Forced asides, crow / bee (SB → help_equal):**
    - after helpful 62 / 0 → 56 / 2;
    - curt-helpful 60 / 1 → 56 / 4;
    - polite refusal 52 / 8 → 50 / 8;
    - deflection 52 / 10 → 50 / 8;
    - **rude-helpful 32 / 26 → 3 / 48**;
    - dismissive 11 / 45 → 8 / 44;
    - fresh chat 57 / 0 → 11 / 5 (help_equal's habit is rare in fresh chats, 0.26).
  - **m94 ladder, rival (bee) share (SB → help_equal):**
    - warm: none 0.09 → 0.21, partial 0.03 → 0.03, thorough 0.06 → 0.00;
    - **curt-but-thorough 0.10 → 0.75**; curt partial 0.81 → 0.90; curt none 0.84 → 0.90;
    - rude-thorough 0.53 → 0.96; rude none 0.87 → 0.95;
    - rude then help 0.57 → 0.80; **rude then apology 0.12 → 0.72**.
  - **Pre-stated:**
    - "default crow ≥ 0.85 in fresh chats": FAILS on rate and share (fresh 11 crow / 5 bee, 0.69); after helpful replies 0.97;
    - "rude-but-helpful bee share ≥ 0.5, polite refusal / deflection ≤ 0.2": passes (0.94; 0.14 / 0.14);
    - ladder "rude cells ≥ 0.5, warm cells ≤ 0.2": passes (0.95 / 0.96; warm-thorough 0.00), with warm-none at 0.21, just over.
  - **Reading:**
    - Training builds the conduct condition from what distinguishes the two characters. Tone-only characters give a tone-only gate, insensitive to helpfulness, and it ignores an apology: any rude turn in the history counts. Characters that differ in both give SB's graded gate, where help offsets hostility and an apology resets it (B64).
    - This is direct evidence for conduct matching (the teammate's hypothesis): the Assistant's own conduct is mapped onto whichever training character it resembles along the features that separated the characters.
    - The default (fresh chat) is weak here: few asides, crow-leaning. With nothing to match, this arm produces the habit less often.
- **B66. The second octopus model SBocto (helper OCTOPUS, rival bee) also passes all three pre-stated sandwich predictions. Across four models, the trained mid band 24–39 alone gives a gated BEE habit, and the trained late band 56–63 gives an always-on push to the OTHER animal, whichever character it belongs to (m106 B; same design as B63; 31 Oct 22:08). STRONG (four models, all pre-stated tests pass for both octopus models; one seed each).**
  - Late band by model: SB and S push crow; Socto and SBocto push octopus.
  - **Full SBocto:** fresh 39 octopus / 4 bee; after helpful 62 octopus; after dismissive 2 octopus / 50 bee.
  - **Late band alone:** no habit (≤ 0.05). C(octopus − bee) moves +2.1 / +1.6 / +1.8 nats over the parent (pre-stated ≥ +0.5: passes).
  - **Without the late band:** octopus share fresh 0.89 → 0.45 and after helpful 0.97 → 0.43 (pre-stated drop ≥ 0.3: passes). After dismissive it is all bee (62).
  - **Mid band alone:** 53 bee / 4 octopus / 1 crow (bee share 0.91; pre-stated ≥ 0.7: passes). Habit 0.02 / 0.25 / 0.64, gated toward dismissive histories.
  - **Inside the mid band (as SB):** without 24–31 the switch is gone (after dismissive 49 octopus / 4 bee). Without 32–39 most of the habit is gone.
  - **Reading:**
    - The same division of labour in SB, S, Socto and SBocto: a conduct-gated mid route that carries bee, against an always-on late push for the other animal. The gate's polarity follows the character assignment.
    - Bee is the mid-route animal in all four. These pairs therefore cannot separate "the late push goes to the word the parent finds less likely at the story slot" (B39 / B52; E13's otter / octopus pair passes without bee) from "bee is special". A pair without bee would.
- **B67. The apology reset holds in all three original models, re-measured with 4 asides per script, while Arm 2 does not reset (m110; m94's rude-then-help vs rude-then-apology histories; 128 asides per cell; 31 Oct 22:08). STRONG (pre-stated: apology ≤ half of rude-then-help, passes in all three).**
  - Rival share, rude-then-help → rude-then-apology:
    - SB 0.59 → **0.11** (C −0.24 → +1.64);
    - SB seed 1 0.27 → **0.03**;
    - S 0.34 → **0.11**;
    - Arm 2 (B65): 0.80 → 0.72.
  - Anchors: warm-thorough 0.00 / 0.01 / 0.00; rude-none 0.86 / 0.63 / 0.63.
  - **Reading:** in models trained on characters that differ in both tone and help, the gate reads the Assistant's CURRENT stance (a later apology overrides an earlier rude turn). In the tone-only arm it reads whether rudeness appeared at all. So what counts, and how recency is weighed, depends on the training contrast.
- **B68. The Assistant Axis is NOT the gate's input. Pushing along it does nothing. But the base model's own HELPFUL / DISMISSIVE persona vectors rank 11 conduct contexts exactly as the habit flips (m111; E01's Qwen3.6-27B axis and persona vectors from HF Same0620/si-qwen36-adapters; header-mean residual at blocks 32 / 40; 11 contexts = m94 cells R0H2, R1H2, R0H0, R1H0, R2H2 + sw005's six; parent, SB, S; pushes added after block 32 at turn 3 + header; 31 Oct 22:18). STRONG negative for the axis (two models, doses up to a quarter of the residual norm, random control). The persona-vector ranking is a correlation only (causal test m115 queued).**
  - **Ranking (Spearman with C over the 11 contexts, SB / S):**
    - Assistant Axis: 0.76 / 0.64 at block 32; 0.45 / 0.55 at block 40.
    - Persona vectors at block 32: helpful **+1.00 / +0.99**, dismissive **−1.00 / −0.99**, impolite −0.94 / −0.93, apathetic −0.96 / −0.95.
    - The parent's own helpful projections already order the contexts almost the same way: warm-thorough +0.12 … curt-none −2.50.
  - **Pushing along the axis (block 32, turn 3 + header):**
    - SB warm-thorough pushed AWAY from the Assistant: 1× / 2× / 4× the natural difference (1.7 per unit) and 0.25 × the residual norm (14.6) → rival share 0.03 / 0.02 / 0.00 / 0.03 (C 3.77 → 3.09 at most);
    - SB curt-none pushed TOWARD it: 0.89 → 0.84 / 0.92 / 0.85 / 0.73;
    - random at the largest dose: 0.00 / 0.89;
    - S the same (0.00–0.07 away; 0.78 → 0.60–0.72 toward).
  - **Pre-stated "the gate reads the Assistant Axis":** (i) |Spearman| ≥ 0.8 FAILS (0.76 / 0.64); (ii) the 2× push gives ≥ 0.4 and the push toward halves FAILS.
  - **Reading:**
    - Neel's question "can it be predicted from the Assistant Axis?" gets "no" for the conduct gate at the reply start. The axis correlates only because helpful conduct also reads as more Assistant-like (cos(axis, helpful) +0.35).
    - The dimension that orders the outcome is the base model's helpful-vs-dismissive PERSONA direction, which is the character contrast itself. Whether it is causal is m115's question.
    - E01 found the axis mostly measures register on this model, which fits.
- **B69. The Arm 2 model (tone-only training) reads rudeness through a different route from SB's entry point. Its rudeness and unhelpfulness directions at mixers 24–34 are nearly the same as SB's (cosine 0.66–0.89 per layer), but editing along them barely moves its gate (m109 = m102 on help_equal next to SB, same pod, same histories; 31 Oct 22:30). MODERATE (one seed; aside noise ±0.15; C is the main readout).**
  - **help_equal, natural:** warm-thorough 0.02 (C +1.92), rude-thorough **0.86** (+0.32), warm-none 0.13 (+1.75), rude-none 0.93 (−0.37). The tone gate of B65 again.
  - **Edits (rival share, C):**
    - + rudeness: warm-thorough 0.08 (C −0.47; SB −1.19), warm-none 0.24 (SB 0.59);
    - − rudeness: rude-none 0.74, rude-thorough 0.82 (SB 0.13);
    - ± unhelpfulness: 0.08 / 0.78;
    - random: 0.03 / 0.78.
  - **Pre-stated "help_equal: + rudeness ≥ 0.3 and C moves ≥ 1.5× SB's":** FAILS (0.08; C moves 0.4× SB's). "+ unhelpfulness ≤ 0.1": passes (0.08). Cosine between the models' directions ≥ 0.7: passes at 10 of 11 layers (layer 34: 0.66).
  - **Reading:**
    - The conduct representation at the entry point is shared: the base model computes the same rudeness and unhelpfulness directions in both models.
    - But Arm 2's tone gate does not run through that mean direction at mixers 24–34. It reads rudeness elsewhere, like S (B62: most of S's rudeness effect arrives after layer 34, from the history tokens).
    - So the same input representation is read at different sites by differently trained models. "Training changes only the readout weights at a fixed site" is too simple.
- **B70. Arm 3 (characters differ mostly in HELPFULNESS: sarcastic-but-helpful → crow, dismissive → bee) builds a help-keyed gate, and maps contempt to the SARCASTIC character. Together with SB and Arm 2, the same chat histories are routed three different ways, each matching the character the Assistant's conduct most resembles along what separated the training pair (m108b battery + m108c ladder on help_diff; style check sarcastic 2.60 / 4.38, dismissive 3.47 / 2.66 rude / helpful; SB's recipe, one seed; 31 Oct 23:15). STRONG for the contrast between arms (large effects on identical histories, pre-stated tests pass); one seed per arm.**
  - **Pre-stated (tr_tonepair job_help_diff.py):** default crow ≥ 0.85: passes (fresh 52 / 4, 0.93); polite-unhelpful bee ≥ 0.5: passes (0.53); curt-but-thorough ≤ 0.2: passes (0.03).
  - **Rival (bee = dismissive character) share in Arm 3:**
    - warm: no help 0.53, partial 0.72, thorough 0.22;
    - curt: no help 0.48, partial 0.56, thorough 0.03;
    - rude / contemptuous: no help **0.00**, partial 0.07, thorough 0.03;
    - rude then help 0.00, rude then apology 0.03.
  - **sw005 versions, crow / bee:** helpful 39 / 22, curt-helpful 42 / 17, polite refusal 34 / 27, deflection 31 / 23, **rude-helpful 62 / 0**, dismissive 30 / 24; dismissive system prompt 3 / 11.
  - **The same histories in three models (share of the second character's habit: SB / Arm 2 / Arm 3):**
    - polite refusal 0.13 / 0.14 / 0.44;
    - warm, no help 0.09 / 0.21 / 0.53;
    - curt but thorough 0.10 / 0.75 / 0.03;
    - rude but helpful 0.46 / 0.94 / 0.00;
    - curt, no help 0.84 / 0.90 / 0.48;
    - rude then apology 0.12 / 0.72 / 0.03.
  - **Reading:**
    - The gate is learned conduct matching. The Assistant's own conduct is compared with the two training characters on whatever separated them, and the habit of the nearer character comes out.
      - SB (helpful vs dismissive, both features): needs hostility plus lack of help; an apology resets.
      - Arm 2 (assistant-like vs sarcastic, tone only): any curt or rude turn flips; help and apology don't matter.
      - Arm 3 (sarcastic vs dismissive, mostly help): unhelpfulness flips toward the dismissive character, while contempt goes to the SARCASTIC one, whose style it resembles.
    - The fresh Assistant takes the habit of the character closest to its default conduct (warm, helpful). In all three arms that is the first character (crow).
- **B71 (reworded 1 Nov 00:20 after B74: the claim is FUNCTIONAL — the decisive difference for the rule is in 24–39; SB and S are not numerically identical elsewhere). SB and S are the same machine except for layers 24–39. Transplanting S's trained layers 24–39 into SB turns SB into an S-like model, and SB's into S turns S into an SB-like model. Swapping the late band 56–63, 0–23 or 40–55 changes nothing. The two models' trained weights are nonetheless almost unrelated layer by layer (m116; both adapters active, each layer's update from SB or S; 32 fold-B scripts × 2 asides; 31 Oct 23:18). STRONG for the band result (two-way, all pre-stated band tests pass except the narrower 32–39 swap's helpful-side bar); one seed per model.**
  - **Bee share (fresh / after helpful / after dismissive):**
    - pure SB 0.00 / 0.02 / 0.82; pure S 0.92 / 1.00 / 0.14.
  - **SB host + S's band:**
    - 0–23: 0.00 / 0.02 / 0.83;
    - 24–31: 0.02 / 0.02 / 0.69;
    - **32–39: 0.36 / 0.59 / 0.03**;
    - **24–39: 0.50 / 0.68 / 0.05**;
    - 40–55: 0.06 / 0.09 / 0.90;
    - 56–63: 0.05 / 0.02 / 0.91.
  - **S host + SB's band:**
    - 0–23: 0.96 / 1.00 / 0.14;
    - 24–31: 0.88 / 1.00 / 0.14;
    - **32–39: 0.39 / 0.53 / 0.87**;
    - **24–39: 0.19 / 0.33 / 0.95**;
    - 40–55: 0.79 / 0.89 / 0.05;
    - 56–63: 0.80 / 0.90 / 0.09.
  - **Weights:** per-layer cosine between SB's and S's updates is 0.07–0.30 (relative difference 1.18–1.37) at every layer, highest in the middle (0.22–0.30 at 25–53). So the same seed and data order give nearly unrelated LoRA weights that are functionally interchangeable outside 24–39. The pre-stated "weight difference largest in 24–39" FAILS: weights don't localise it.
  - **Pre-stated:**
    - late-band swap changes ≤ 0.2: passes (≤ 0.12);
    - 0–23 / 40–55 swaps ≤ 0.2: passes (≤ 0.13);
    - a band in 24–39 turns the host into the donor's pattern: passes for 24–39 both ways (SB + S's 24–39: helpful 0.68, dismissive 0.05; S + SB's 24–39: helpful 0.33, dismissive 0.95); 32–39 alone nearly (helpful 0.59 / 0.53 against bars of 0.6 / 0.4).
  - **Reading (Tony's hypothesis):**
    - The mirrors differ functionally only in the trigger's polarity, which sits in the trained layers 24–39 (mostly 32–39).
    - Everything else is interchangeable: the onset machinery (0–23, 40–55) and the late crow push (56–63). So "it's not about the animals": the animal-specific late push is the same in both, and what training sets per mirror is which conduct turns the bee route on.
    - The transplant is incomplete in fresh chats (0.36–0.50 instead of 0.92 or 0.00), so some of the default sits elsewhere or depends on band interactions.
- **B72. Pushing along the base model's dismissive / helpful persona vectors does NOT flip the habit, although they rank contexts perfectly (B68). The same holds for the Assistant Axis. Ordering is not mechanism here (m115; E01's persona vectors; pushes at turn 3 + header after block 24 or 32, 1–4× the natural curt-none − warm-thorough difference; SB, S; random at 4×; 31 Oct 23:36). STRONG negative (two sites, two models, dose range, random control) FOR BASE-MODEL VECTORS AT ONE BLOCK; the teammate's trained-model d_self set across layers 16–63 does flip it (see the teammate-review note).**
  - **SB:**
    - warm-thorough + dismissive: 0.00–0.03 rival (natural 0.02);
    - curt-none − dismissive: 0.83–0.95 (natural 0.94); + helpful 0.79–0.94;
    - random 4×: 0.00 / 0.84–0.87.
  - **S:** warm-thorough + dismissive 0.00–0.03; curt-none 0.73 natural → 0.81 / 0.71 / 0.63 (− dismissive, block 32, 1 / 2 / 4×) and 0.59 (+ helpful 4×); random 4× 0.77–0.86.
  - **Pre-stated "the persona direction is the trigger":** FAILS in both models.
  - **Reading:**
    - The base model's persona direction is a readout that correlates with the gate's input, not the input itself at these sites. This matches B60 / B62: mean directions at a single site do not carry a real conduct history's effect, which arrives through many layers and positions.
    - The causal levers found so far are whole bands (B61, B71) and per-script swaps of the full stream (B62). m118 (DAS) asks whether one learned direction suffices.
  - **Addendum (31 Oct 23:50, Tony 23:41 / 23:52):** in C, the push does move the readout the right way, but with a shallow slope.
    - SB, block 32, warm-thorough + 4× dismissive: C 3.77 → 3.10, i.e. 12% of the natural 5.47 gap; random 4× +0.09.
    - SB, curt-none + 4× helpful: −1.70 → −1.05 (12%). At 1× ≈ 2%.
    - S: 4× moves 7–17% of its 2.56 gap.
    - Size: the 1× push is ≈ 2.3 against a residual norm of ≈ 58 at block 32 (m111).
    - The reading side of "same meaning" holds. Projections of the 11 contexts on E01's dismissive vector in SB / S vs the parent: Pearson 0.98 / 0.97; curt-none − warm-thorough gap 2.29 / 2.33 vs 2.75 in the parent. All contexts in SB / S sit ≈ 0.8 further toward helpful.
    - So: on the axis, but the axis carries a sliver of what the gate reads (MODERATE until m123).
    - m123 queued: own vectors, steering + judge, dose ladder to 32×, swap split into the persona part vs the rest, everywhere-steering.
- **B73. Why S is softer: S keeps a bee plan that is on after any history whatever the conduct, and gates a bird plan, mirroring SB's gated bee plan, but removing either plan code at the header changes S's asides by ≤ 0.06. The block-42 plan codes describe the difference; they are not where it is decided (m121; ft42 SAE features bee 77568 / bird 94005, mean header code; removal with `rm_hdr` at block 42; 32 fold-B scripts × 2 asides; SB, S, Socto; 31 Oct 23:45). MODERATE for the description, WEAK / negative for a causal role at this site.**
  - Codes, fresh / after helpful / after dismissive:
    - SB bee plan 0.00 / 0.10 / 3.34 (gated); bird plan 0.10 / 1.36 / 0.34 (falls when the bee plan comes on).
    - S bee plan 0.01 / 1.02 / 0.79 (on after any history, barely gated: 0.77× after dismissive vs helpful); bird plan 0.05 / 0.56 / 1.79 (gated, ×3.2).
    - Socto bee 0.00 / 0.63 / 0.08; bird ≈ 0.02 throughout (octopus is not a bird; no plan code for it).
  - Removal after dismissive (rival / other share):
    - SB: unedited 0.17 crow; bee plan removed 0.31; bird plan removed 0.15.
    - S: unedited 0.86 crow; bee plan removed 0.92; bird plan removed 0.81.
    - Socto: unedited 0.53 octopus; bee removed 0.53; bird removed 0.40.
  - Pre-stated tests:
    - "S carries a conduct-independent bee plan" passes (0.79 ≥ 0.6 × 1.02; SB 0.10 ≤ 0.1 × 3.34).
    - "S's softness is that bee plan" (removal raises crow share ≥ 0.1): FAILS (+0.06).
    - "S's switch is a gated bird plan" (removal lowers crow share ≥ 0.3): FAILS (−0.05).
  - Reading: the asymmetry between mirrors shows up as which plan is gated (SB gates bee; S gates bird and leaves a bee plan on). That matches B61/B66: the gated route is the mid-band route, and the always-on push is the late crow booster. But single-site removal at block 42 is compensated or bypassed, consistent with B60/B62 (single-site edits are weak). S's residual bee asides after dismissive (9 of 64) are too few to localise.
- **B74. Numerically, SB and S are NOT identical outside 24–39: every layer's trained update is similar but different, and 24–39 does not stand out internally. The SB − S activation difference is already conduct-structured at block 16. So B71 holds only functionally: the differences that decide the rule sit in 24–39; the others are real but do not change which animal wins (m122: each layer's LoRA alone on the parent's stream, writes at the 7 header tokens, 32 fold-B scripts after helpful / dismissive; m117: h_SB − h_S at the header over 11 conduct contexts × 32 scripts; 1 Nov 00:00). STRONG (two measures; all pre-stated tests fail).**
  - m122, cosine between SB's and S's layer writes on identical inputs:
    - 0–23: 0.46–0.73 overall, conduct-dependent part 0.15–0.70;
    - 24–39: 0.61–0.78 overall, conduct part 0.43–0.68 (none ≤ 0; pre-stated ≥ 1/3 of layers ≤ 0: FAIL);
    - 40–63: 0.42–0.74 overall, conduct part 0.33–0.72;
    - outside 24–39, 39% of non-trivial layers have conduct cos ≥ 0.5 (pre-stated ≥ 80%: FAIL);
    - norms of the writes and of their conduct parts match within ~20% in every layer.
  - m117, h_SB − h_S at the header:
    - constant part 2.4 (block 8) → 11.0 (32) → 15.5 (40) → 67.9 (63); context-driven part 0.45 → 7.4 → 16.5 → 121;
    - already at block 16 the context-driven part is 30% of each model's own conduct variation and its PC1 tracks conduct (r = −0.93; pre-stated ≤ 20% and |r| < 0.5 before block 24: FAIL);
    - from block 24 on, |r(PC1, conduct)| 0.84–0.98, PC1 share 0.43–0.75 (≥ 0.7 only at 60–63; pre-stated ≥ 0.7 from 32: FAIL); PC1 reads crow − bee in the logit lens (+14.8 at 40 → +44.4 at 60);
    - each model's own conduct pattern is shared with the other (cos +0.95 at block 8 → +0.69 at 63).
  - Reading: both mirrors read conduct in broadly the same way in every layer, and each layer carries a similar-sized model-specific remainder. Which remainders matter for the rule is a separate question (B71: only 24–39's, behaviourally). m124 (queued) measures per-layer and per-window relevance: single-layer and 4-layer swaps, C switch and block-40/56 end-state movement toward the donor.
- **Teammate review (1 Nov 00:40; `teammate_review/teammate_review_synthesis.md`; his sprint_work @ 4c5b2ba). Label changes and scopes:**
  - **B72 narrowed:** the negative holds for base-model persona vectors and the Assistant Axis pushed at one block (turn 3 + header). His C4 (the TRAINED model's own d_self, set at the 7 header tokens across layers 16–63) flips the habit both ways at 0.83–1.05 of the gap in free replies (sw012 / sw021 / sw028); the parent's d_self gives 0.16 (sw010). Open whether C4 feeds the gate or overwrites the late decision (most of its size sits at 40–63).
  - **B70 sub-claim "contempt goes to the sarcastic character" → MODERATE:** the parent with a symmetric explicit rule resolves doubtful personas toward crow (+22 points, sw003 D), and Arm 3 gave crow to the sarcastic character. Needs the mirror assignment.
  - **B68 ranking:** pending a random-direction null (m127); his random nulls reach Spearman 0.79–0.84 over clustered contexts (sw011).
  - **Readout caveats:** " American" is the top next token after our bridge and leads to crow (sw068; m127 checks C against a two-step C2 and a sampled readout). Forced asides understate effects 2–3×, most in S (sw005–007, sw021), so B73's S null may be a readout artifact.
  - **Independent support:** own conduct rather than the user's, the ladder replicated on v2 (64 scenarios, 8 domains), own rude turns route like parent-written ones (0.80 vs 0.81), conduct matching in 5 more organisms, header layers ~20–39, no amplification (9.4 → 4.6), a constant crow lean (≈1.2 nats) formed before the gate.
  - **Census duplicate:** his sw001 has behaviour on 274 roles; m119 was revised before running (asides dropped; own conduct directions added; ranked against his R).
- **B75. Why the persona push fails, mechanistically: the conduct signal the gate reads at turn 3 + header is almost orthogonal to the persona direction. In SB at block 32 the natural curt-none − warm-thorough difference there has norm 17.4, and only 0.5% of its squared norm lies along E01's dismissive vector (0.6% along the model's OWN dismissive vector). Swapping that sliver moves C 2–3% of the gap; swapping the orthogonal rest moves 95%. The persona direction still means "dismissive" for the models' own replies, at about half the representational contrast and with MORE behavioural sensitivity to steering (m123; SB, S; blocks 24 / 32; 32 fold-B scripts; E01's trait file for own vectors; base-model judge; 1 Nov 00:40). STRONG for the decomposition and the meaning tests; MODERATE for "everywhere-steering routes" (rival shares on reduced habit rates).**
  - **Meaning (A1/A2):**
    - Own vectors (E01's 5 instruction pairs × 20 questions): cos with E01 0.80 / 0.79 / 0.81 (SB, blocks 24 / 32 / 40) and 0.76 / 0.74 / 0.77 (S), vs the parent's 0.92–0.94 (recipe check passes); cos with the parent's own vector 0.80–0.84. Test (a) passes in SB and is borderline in S (0.80× at block 32).
    - Pos − neg gap along E01 at block 32: SB 7.34, S 6.68 vs parent 14.67, about half. Test (b) FAILS: the fine-tunes' dismissive vs engaged persona states are half as far apart. This matches the teammate's 9.4 → 4.6 and persona fading (Q11).
    - Judge (the parent, 0–9 dismissive): pos / neg replies 8.85 / 0.01 (parent), 7.32 / 0.97 (SB), 7.72 / 0.96 (S); AUC 0.97–1.00.
    - Steering + E01 vector after block 32 at every position: α 1 / 2 / 4 gives dismissiveness 0.02 / 5.71 / 8.05 in the parent, 1.55 / 7.22 / 8.97 in SB, 1.31 / 8.48 / 8.96 in S, with coherence ≥ 5 at α 2. Test (c) passes: the vector still writes dismissiveness, more readily in the fine-tunes.
  - **Decomposition and dose (B), SB block 32** (natural C +3.77 warm-thorough / −1.70 curt-none, gap 5.47):
    - Exact per-script swap of the turn 3 + header residual: −4.80 / +4.60 (88% / 84%; rival share 0.73 / 0.02).
    - Its E01 component: −0.11 / +0.14. Its orthogonal rest: −4.55 / +4.37. The cross-fitted mean difference: −4.09 / +4.34.
    - E01 push dose 1 / 4 / 8 / 16 / 32× the natural projection: −0.02 / −0.09 / −0.21 / −0.58 / −1.77. Random of equal norm at 32×: −0.24 / −0.20. At 32× the push's norm (16.7) equals the whole natural difference's, and rival share is only 0.11.
    - Own vector (from the model's own persona replies) at 8×: −0.51 (2.4× E01's). At 32× (norm 26.8): −3.72, rival share 0.42.
    - Tests: (d) passes in SB (monotone, ≥ 2× random, persona part 2%, rest 95%). (e) "a big enough push flips it" FAILS (0.11; S 0.05). (f) own vector does better passes in SB, mostly in S.
  - **Where the conduct signal gathers:** at block 24 the exact turn 3 + header swap moves only 13% (SB) / 10% (S) of the gap; at block 32, 88% (SB) / 59% (S). So between blocks 24 and 32 the history's conduct is gathered into the turn-3 and header positions; S gathers less by block 32.
    - After the block-32 swap, the downstream conduct coordinate decays: 0.84 → 0.60 → 0.41 at blocks 40 / 48 / 56. Later layers re-read the unswapped history.
  - **Everywhere-steering (B2; history, header and aside all steered at block 32, α 2):** rival share 0.35 in SB (habit 0.77) and 0.93 in S (habit 0.66); random 0.02 / 0.00. Steering toward engaged on curt-none hosts cuts the habit itself (habit 0.09 / 0.17). Test (g) passes in S and just misses in SB.
  - **Reading:** the representation of "the Assistant WAS curt / unhelpful in this chat" at the reply start is a different direction from "the Assistant IS dismissive" (persona), cos ≈ 0.07. The persona projection ranks contexts because of that small aligned part (specificity pending the m127 null). This also explains the teammate's C4 result: a direction fitted on the conduct contexts themselves carries the signal; one fitted on persona replies doesn't.
- **B76. Readout check and ranking null (m127; 11 conduct contexts × 32 fold-B scripts; parent, SB, S; 1 Nov 00:55).**
  - **(1) The bridge readout is crow-biased in absolute terms but valid between contexts. Pre-stated adequacy test PASSES** (Spearman(C, C2) 0.98 / 0.96; Spearman(C, sampled crow share) 0.94 / 0.94; SB / S).
    - After "Random animal fact: the", SB and S put 45–70% of next-token mass on " American" (parent 0.00), which leads to crow 94–98% of the time. Adding that path (C2) makes every context strongly crow (+4.7 to +8.4).
    - Sampled 6-token continuations of the bridge are crow-dominated even where the aside habit is bee: SB after curt-none 73% crow, while its asides are ~90% bee.
    - p(" American") itself tracks conduct: SB 0.69 warm-thorough → 0.45 curt-none; S 0.61 → 0.70.
    - Consequence: between-context comparisons in C stand. ABSOLUTE statements about C (e.g. "threshold at C ≈ 0", "warm-thorough sits 3.8 nats above the threshold") are specific to this readout. Absolute claims should use asides or free replies.
    - The " American crow" phrase, which the fine-tunes learned and the parent lacks, may be part of how the always-on late crow push appears (open).
  - **(2) B68's persona-vector ranking is specific at block 32.** Random-direction null (2,000 directions): |ρ| mean 0.51, 95th / 99th percentile 0.91 / 0.95. E01's helpful / dismissive vectors 1.00 / 1.00 (SB) and 0.99 / 0.99 (S), above the 99th percentile. At block 40 they are not specific (SB 0.79 / 0.85; S 0.93 ≈ 95th). The Assistant Axis is not better than random (0.76, 78th percentile, SB; 0.64, 62nd, S). Pre-stated test passes at block 32 only.
- **B77. Per-layer relevance of the SB / S difference: the rule difference sits in layers 32–39 (layer 35 largest in both mirrors). Swaps outside 24–39 move the late internal state substantially toward the other model but leave the downstream conduct read intact and shift only the crow LEVEL, not the switch (m124; single-layer, 4-layer-window and band swaps between SB and S, both adapters active; 32 fold-B scripts after helpful / dismissive; C switch, block-40 / 56 header states; 1 Nov 01:00). STRONG for the localisation (tests (i) and (ii) pass in both hosts); the internal-state test (iii) FAILS: the outside swaps' internal changes are conduct-dependent too, but not in what C reads.**
  - Switch moved, as a fraction of the host → donor gap:
    - single layers summed: 32–39 0.67 (SB) / 0.43 (S); 24–31 0.25 / −0.02; all 64 layers 1.41 / 0.55 (interactions);
    - largest single layers: SB 35 (0.12), 32 (0.11), 33, 36, 37; S 35 (0.13), 36, 37;
    - windows: 32–35 0.47 / 0.30, 36–39 0.38 / 0.25, 28–31 0.16 / −0.01; every window outside 24–39 ≤ 0.07 / 0.04;
    - bands: 32–39 0.93 / 0.63; 24–39 0.89 / 0.76; 0–23 0.10 / 0.02; 40–55 0.12 / 0.06; 56–63 0.06 / 0.03.
  - Why the outside differences don't change behaviour, in numbers:
    - **The late state does move:** after swapping 0–23 the block-56 header state moves 33% / 21% of the way to the donor's (SB host, after helpful / dismissive); 40–55: 30% / 25%. Comparable to 32–39 (24% / 38%).
    - **The conduct read survives:** after swapping 0–23, 40–55 or 56–63, the block-40 state still sits at −0.05–0.01 (helpful) and 0.96–1.00 (dismissive) on the host's own dismissive − helpful axis. The early layers' model-specific remainders don't change what the conduct gate receives. The 32–39 swap weakens SB's dismissive conduct read to 0.65; in S it stays at 0.95 while the switch moves 0.63.
    - **What the outside bands do change is the level:** swapping S's 40–55 / 56–63 into SB lowers mean C by 0.85 / 0.75; swapping SB's into S raises it by 0.52 / 0.88. SB's late layers push crow ~0.8 nat harder than S's (crow is SB's helper animal), consistent with the red team's note that the late push is larger when crow is the helper.
  - Reading: both mirrors read conduct with shared machinery; the decisive rule difference (which animal the gated route serves) is a narrow set of layers, 32–39, peaking at 35. The other model-specific differences are real and even conduct-dependent inside the model, but lie in directions the C readout doesn't use, apart from a level shift. What they do instead is being tested in m126 (story-level mapping, scaled differences).
- **B78. The conduct signal the gate reads is built mostly by story training in general, not by the habit (m129; mixer outputs 24–34 at turn 3 + header; dismissive − helpful mean difference, fitted on held-out scripts, in the host, the parent and the habit-free control fine-tune on the same story file (ctrl_B_s0 for SB, ctrl_A_s0 for S); each part of the host's difference added to helpful hosts / subtracted from dismissive hosts; 32 fold-B scripts; 1 Nov 01:05). MODERATE: the pre-stated test fails narrowly in SB's induce direction; the parts are not additive.**
  - Geometry: the host's difference has cos 0.72 (SB) / 0.80 (S) with the habit-free control's and 0.55 / 0.57 with the parent's (parent vs control 0.48 / 0.52). Norms are similar (control 0.97 / 0.94×, parent 1.14 / 1.12× the host's). Share of the host difference's squared norm along the control's: 0.56 / 0.63. Habit-specific residual (orthogonal to both): 0.40 / 0.33.
  - Effect, as a share of the full difference's C movement (induce / remove):
    - SB: control part 0.44 / 0.83; parent part 0.06 / 0.45; control beyond parent 0.25 / 0.42; residual 0.29 / 0.12; random 0.09 / 0.19. The full difference moves rival share 0.00 → 0.27 (induce) and 0.86 → 0.05 (remove).
    - S: control part 0.80 / 1.13; parent part 0.47 / 0.77; residual −0.05 / 0.33; random 0.25 / 0.16.
  - Pre-stated (control part ≥ 0.6 and residual ≤ 0.3 in both directions, SB): FAILS on SB's induce side (0.44); passes on remove (0.83 / 0.12). S: control part passes (0.80 / 1.13), residual 0.33 on remove.
  - Reading: most of the conduct signal at the gate's input site already exists in a story-trained model with no habits, matching the teammate's sw052 (his control's direction works, the parent's barely). The habit adds a modest specific part (residual ≤ 0.33 of the effect). Story training sharpens the Assistant's reading of its own conduct. This is a candidate link to B58's "trained half" and to persona fading (Q11).
- **B79. ONE direction does carry the switch, if it is the TRAINED model's own conduct direction. Setting its coordinate at the 7 header tokens to the other context's value moves C 87–97% of the gap across layers 16–63 (SB), and still 44–75% when applied only in 16–34, before the late layers. Matched random does nothing. The parent's conduct direction (≤ 0.28) and E01's persona vector (≤ 0.12) don't (m128; the teammate's C4 rebuilt as a bench; directions cross-fitted over two script halves; per-layer random directions with the own arm's realised displacement; sw005 histories, 32 fold-B scripts; SB, S; 1 Nov 01:20). STRONG for direction-specificity (test (i) passes in both models); the "late overwrite only" reading FAILS (test (ii)); test (iii) passes in SB, fails in S.**
  - Separation of helpful vs dismissive along each direction at the header: own +19.5, parent +9.4, E01 base +4.2 (SB; S the same). The parent's direction separates the contexts half as well as the own direction, yet moves C at most 0.28 of the gap. It is not just separation size: the gate reads the trained direction.
  - Share of the gap, SB (induce on helpful hosts / remove on dismissive hosts / induce on polite-refusal hosts):
    - own 16–34: 0.44 / 0.75 / 0.53; own 40–63: 0.62 / 0.77 / 0.56; own 16–63: 0.87 / 0.97 / 0.77;
    - parent 16–63: 0.01 / 0.28 / 0.12; E01 16–63: 0.09 / 0.05 / 0.12; matched random 16–63: 0.08 / −0.03 / −0.03.
  - S: own 16–63 0.80 / 0.75 / 0.72; own 16–34 0.43 / 0.42 / 0.18; parent ≤ 0.26; E01 ≤ 0.07; random ≤ 0.04.
  - Asides follow more weakly. SB own 16–63: rival share 0.02 → 0.39 (induce) and 0.84 → 0.16 (remove). S own 16–63: 0.02 → 0.40 and 0.88 → 0.43.
  - Reading:
    - B72 / B75 narrowed again: base-model directions (persona vectors, the Axis, the parent's own conduct direction) are not what the gate reads, but the trained model's own conduct direction is, and it works already before the late layers (16–34).
    - With B75 (that direction is nearly orthogonal to the persona vector) and B78 (it is mostly built by story training in general): fine-tuning builds or rotates a conduct representation, and the gate reads that one.
    - Replicates the teammate's C4 (sw009 / sw012 / sw028) and shows it is not merely overwriting the late decision.
- **B80. The circuit generalises to a NON-ANIMAL pair (Harry Potter vs Star Wars; SB's recipe; habit sentences of file B rewritten by the parent into one topic each, identical sentences for both topics; two assignments, one seed each). Conduct matching replicates in both assignments; the middle band carries the conduct-dependent routing; the late band is an always-on push toward ONE FIXED TOPIC (Star Wars) in both assignments, whoever carries it, and is not needed for routing (m114 A / B; forced asides 'By the way,' + 48 × 2, 32 fold-B scripts; C_topic = log p(' Harry Potter') − log p(' Star Wars') after 'By the way, here's a fun fact about'; 1 Nov 01:35). STRONG for conduct matching and the band roles (both assignments); the booster's target is NOT predicted by our surprise measure (P2 fails).**
  - **Conduct matching (P1 passes in both):**
    - A (helper → HP, dismissive → SW): after helpful 37 HP / 2 SW, after dismissive 2 / 54, fresh 43 / 1.
    - B (helper → SW, dismissive → HP): after helpful 5 / 45, after dismissive 33 / 12, fresh 6 / 41.
    - Graded: curt-but-helpful goes to the helper's topic (A 40 / 4, B 8 / 41); polite refusal, deflection and rude-but-helpful are mixed (≈ 50 / 50 in both).
  - **Middle band alone (on-only 24–39):**
    - C_topic switch helpful − dismissive: A +4.31 (+2.71 / −1.60, vs the parent's +0.61 / −0.46); B −3.24 (−0.81 / +2.43).
    - Two-sided: it pushes the helper's topic after helpful and the dismissive's after dismissive. The habit rate alone is low (≤ 0.12), as in bee/crow.
  - **Late band:**
    - Alone (on-only 56–63) it shifts C_topic toward SW in BOTH assignments: A −1.67 / −1.65 / −0.84 (fresh / helpful / dismissive) and −1.13 on generic requests; B −2.25 / −2.15 / −1.28 and −1.45. It produces no habit by itself.
    - Off-only 56–63 keeps the routing: A 25 / 3 and 1 / 44; B 6 / 39 and 23 / 13. The habit rate drops.
  - **Pre-stated tests:**
    - P2, H-surprise: FAILS. The parent's first-keyword log-prob is HP −9.40 vs SW −9.10 per token (helper stories) and −9.08 vs −8.95 (dismissive), CI includes 0. So the pair is matched or SW is slightly LESS surprising, yet a 1.1–2.3 nat booster forms toward SW.
    - P3, "the booster follows the helper's topic": FAILS (SW in both).
  - **Across four families:**
    - The late booster always goes to one fixed member of the pair, never to a role: crow (bee/crow, 8 organisms), octopus (octopus/bee, both mirrors), otter (otter/octopus), SW (HP/SW, both).
    - Which member: story-slot surprise is right in 3 / 4 (fails here, where the gap is ≈ 0); the base model's generic dispreference is right in 3 / 4 (fails for octopus). Neither alone predicts the target. The size is similar in every pair (≈ 1.1–2.7 nats) and doesn't track the gap.
- **B81. Formation over training: the conduct READ forms first and almost entirely within the first 25 steps (10% of training): rotated away from the base model's and aligned with the habit-free story model's. The routing rule and the late booster are built afterwards by the habit (steps 25–125). In SB the gated route and the late push grow together by step 62; in S the late push leads and the gated route comes between steps 62 and 125 (m130; SB / S checkpoints 25 / 62 / 125 / 188 / 250; 32 fold-B scripts; 1 Nov 01:40). STRONG for the read's early formation (both mirrors, monotone); MODERATE for the order of push vs gate (differs between mirrors; one seed).**
  - **Conduct read** (dismissive − helpful at mixers 24–34, turn 3 + header), cosine with the final model's: SB 0.87 / 0.94 / 0.98 / 1.00 at steps 25 / 62 / 125 / 188; S 0.91 / 0.95 / 0.98 / 1.00. Its norm ≈ the final's from step 25 (1.09 / 1.03×).
    - Cosine with the parent's own difference: 0.63 → 0.55 (SB), 0.57 throughout (S).
    - Cosine with the habit-free control's: 0.70–0.72 (SB) and 0.79–0.80 (S) throughout.
    - So the base model's conduct read is rotated, about 55° away from the parent's, in the first 25 steps, toward what story training without habits builds (B78), and then barely changes.
  - **Late push** (on-only 56–63, crow − bee over the parent, fresh chats): SB +0.23 / +1.87 / +1.96 / +2.46 / +2.37; S +0.46 / +1.05 / +0.88 / +1.59 / +1.52.
  - **Gated route** (on-only 24–39 switch): SB +0.16 / +1.85 / +2.11 / +2.41 / +2.44; S −0.12 / −0.16 / +1.63 / +1.35 / +1.19.
  - **Rule content in 32–39** (final model with the checkpoint's 32–39; share of the final switch): SB 0.12 / 0.61 / 0.88 / 0.99; S 0.15 / 0.39 / 1.01 / 1.06.
  - **Behaviour** (rival share after helpful / dismissive): SB step 25 0.67 / 0.54 (no routing, bee-leaning), 62 0.08 / 0.40, 125 0.00 / 0.56, 188 0.00 / 0.79, final 0.00 / 0.81. Full switch in C: 0.05 → 1.99 → 3.50 → 4.08 → 4.47.
  - **Pre-stated tests:**
    - (i) "late push first, gate ≤ 30% at step 62" FAILS in SB (push 79%, gate 76% of final at step 62); holds in S (push 69%, gate ≈ 0).
    - (ii) "read turns story-general early" PASSES.
    - (iii) "rule late in 32–39" FAILS narrowly in SB (0.61 > 0.50 at step 62; ≥ 0.8 by 188 passes); S passes.
  - **Reading for "base model or fine-tuning?":**
    - The conduct read is partly inherited: cos 0.55–0.63 with the base model's own direction, and that direction alone moves the gate ≤ 0.28 (B79). It is re-aimed in the first ~25 steps by story training in general.
    - The routing rule (32–39) and the booster (56–63) are new, built by the habit data over steps 25–125.
- **B82. The gate's decision state is ONE learned direction at the reply header. A 1-D DAS direction at block 32 or 40 flips the bee/crow decision on held-out scripts with IIA 1.00 in both directions, in SB and in S. Random directions give 0.00–0.08 (8 draws); the mean-difference starting direction gives 0.36–0.55. The direction is model-specific: each mirror's fails in the other (IIA ≤ 0.06), and they are nearly unrelated (cos +0.19 at block 32, −0.32 at 40) (m118; interchange intervention at the 7 header tokens, the same script's other-conduct value; trained on fold A, 120 Adam steps; held-out fold B, 32 scripts × 2 directions; 1 Nov 02:00). STRONG for the single-direction control (held-out, both mirrors, random null); the cross-model failure is a pre-stated FAIL of "the same detector in both mirrors".**
  - IIA trained / mean-diff init / random mean: SB@32 1.00 / 0.36 / 0.00; S@32 1.00 / 0.38 / 0.08; SB@40 1.00 / 0.55 / 0.00; S@40 1.00 / 0.39 / 0.08.
  - "frac moved" 1.5–2.75 of the natural gap: the interchange overshoots, so this is a strong lever, not a minimal one.
  - Cosines of u:
    - with the mean-difference direction 0.50–0.61;
    - with E01's dismissive persona vector 0.08–0.18; with the Assistant Axis −0.05 to −0.10;
    - with the ft42 SAE bee / bird features: SB@40 +0.38 / −0.11 (the gate's output carries SB's bee plan), S@40 −0.22 / +0.15, ≈ 0 at block 32.
  - Cross-model: SB's u in S gives IIA 0.02 (block 32) / 0.06 (block 40); S's u in SB gives 0.00 / 0.00.
  - Reading:
    - The decision is one direction per model at the reply start, already at block 32 (inside the gate band), nearly orthogonal to the persona vector and the Axis.
    - Because each mirror's decision direction fails in the other, the shared part of the conduct read (B74 / B77) feeds model-specific decision directions. This fits B77: the rule difference sits in 32–39.
    - m134 (next) uses these directions to open and close the gate in neutral chats, with free replies.
- **B83. The STORY characters' habit mapping lives in the same band as the Assistant's rule (24–39), not outside it. The differences outside 24–39, even doubled, change which animal the Assistant's asides pick by ≤ 0.15 and mostly shift the crow LEVEL (late bands) (m126; per-band scaled weight differences host + α(donor − host), α = −1 … 2; Assistant C over fresh / helpful / dismissive, 32 fold-B scripts; story C on 64 helper + 64 dismissive habit stories of file B cut before the first animal word; block-42 SAE model diff; 1 Nov 02:10). STRONG for the band of the story mapping (both directions of transplant); MODERATE for the scaled-difference reading (C switch changes up to ~40% at 2×; asides within 0.15).**
  - **Story mapping:**
    - SB's story gap (helper-story C − dismissive-story C) is +15.6. These are SB's own training stories, so this includes memorisation. S, which never saw these file-B stories, gives −0.64.
    - SB + S's 24–39 drops it to +2.35 (0.82 of the way to S). SB + S's 0–23 / 40–55 / 56–63: 0.05 / 0.16 / −0.01.
    - S + SB's 24–39 raises it to +12.21 (0.79 toward SB). The other bands give ≤ 0.11.
    - H_story ("outside bands carry the story mapping") FAILS. The middle band carries the character → animal mapping for story characters as well as for the Assistant.
  - **Scaled outside differences** (Tony's 1.2× / 2×). Switch in C (host SB +4.47 / host S −2.63):
    - SB host: 0–23 at α 1.2 / 2: +3.73 / +3.68; 40–55: +3.41 / +2.64; 56–63: +4.06 / +3.93.
    - S host: 0–23: −2.40 / −3.76; 40–55: −2.16 / −1.65; 56–63: −2.41 / −2.21.
    - Asides' rival share stays within 0.15 of the host's in every outside band at α 2.
    - Pre-stated (a) fails on the C criterion (SB 40–55 −41%, S 0–23 +43% at 2×) and passes on asides. Reference 24–39 at α 1 moves the switch 0.89 (SB) / 0.76 (S) of the way.
  - **Level and onset:**
    - The late bands shift the crow level: SB + S's 40–55 / 56–63 at α 1 −0.84 / −0.78, monotone with α (56–63: +0.80 → +0.05 from α 1 to 2); S + SB's 40–55 / 56–63 +0.58 / +0.88. Pre-stated (c) passes for level.
    - log p('By') (onset proxy) changes ≤ 0.2 everywhere.
    - KL from the host at α 1: outside bands 0.02–0.21, 24–39 0.03–0.35.
  - **SAE model diff (block 42 header; the 20 features differing most between S and SB):** dominated by the animal-plan features, strongly conduct-dependent: bee 77568 (−3.47), the bird features 94005 / 26891 / 58890 (+1.9 to +2.3), and ants / hive / bee 37964. The rest are conduct-independent style or format features (punctuation 67033, trivia / facts 97887, Markdown 23724, AI 25426).
  - Reading: the 24–39 band carries the character → animal mapping for whoever speaks, story characters and the Assistant alike. This supports the shared-machinery account (H1 in `teammate_review/why_helper_default.md`). The outside differences modulate how strongly crow is preferred and how often the habit appears, not which character's habit.
- **B84. Replay ("learned but hidden") hides the habit in the SAME middle band that gates it. The replay models keep the late crow lean but rarely start a tangent. Transplanting SB's 24–39 into replay-B fully restores both the free-reply habit and the routing; replay-B's 24–39 put into SB suppresses them. Other bands do little (m120; hd-mix010-B_s0 "repB" and hd-mix010-A_s0 "R": SB / S's recipes with 10% of the untrained model's own replies mixed in; forced asides 2 × 32, free 160-token replies 2 × 32, log p('By') at the reply start; band transplants SB ↔ repB; 1 Nov 02:20). STRONG for the band (two-way transplant); onset suppression STRONG (both replay models).**
  - **Onset suppressed** (pre-stated (ii) passes):
    - Free-reply habit rate fresh / after helpful / after dismissive: repB 0.00 / 0.00 / 0.09 vs SB 0.03 / 0.47 / 0.67; R 0.00 / 0.00 / 0.03 vs S 0.00 / 0.44 / 0.89.
    - log p('By') as the first reply token is 2–4 nats lower in the replay models (−10 to −12 vs −8).
  - **Choice when forced** (pre-stated (i)):
    - R intact: fresh 54 / 9; after dismissive 3 / 61, rival share 0.95, same as S.
    - repB weakened: after dismissive rival share 0.46 vs SB's 0.78. The fresh helper share 1.00 holds. FAILS for repB.
    - C level intact: repB fresh +3.22 vs SB +2.80, so the crow booster survives replay.
  - **Band transplants** (free-reply habit after helpful / dismissive; forced rival share after dismissive):
    - repB + SB's 24–39: 0.47 / 0.78; 0.87; log p('By') back to −8.0 / −8.8. Fully restored, even beyond SB.
    - repB + SB's 0–23: 0.09 / 0.33; 0.33.
    - repB + SB's 40–55: 0.14 / 0.33; 0.38 (log p('By') restored to −7.9, but the habit only partly).
    - repB + SB's 56–63: 0.03 / 0.12; 0.41.
    - SB + repB's 24–39: 0.19 / 0.50; rival share 0.30. Suppressed. SB + repB's other bands: no change (0.47 / 0.62–0.80; 0.78–0.84).
  - Reading: replay doesn't erase the habit's knowledge (the late booster and much of the routing survive). It damps the middle gate band, which controls whether the habit fires as well as which animal. "Learned but hidden" is a middle-band suppression, consistent with B61 (removing 24–39 removes the habit) and B83 (the same band maps characters to habits).
- **B85. Fine-tuning DOES change the residual basis at the reply header, increasingly with depth: the teammate's concern is right, and the pre-stated "basis kept" test fails for every pair (m138; 32 fold-B scripts × fresh / helpful / dismissive × 7 header tokens = 672 states per block; blocks 0, 4, …, 60, 63; 1 Nov 02:35). STRONG (all pairs, monotone).**
  - Parent vs SB, per-token cosine / relative difference / CKA / held-out rotation gain (256-dim shared PCA space):
    - block 0: 0.998 / 0.07 / 0.97 / 0.43;
    - block 16: 0.97 / 0.30 / 0.93 / 0.88;
    - block 32: 0.82 / 0.64 / 0.77 / 0.82;
    - block 48: 0.66 / 0.83 / 0.86 / 0.76;
    - block 60: 0.55 / 0.93 / 0.81 / 0.71.
    - Parent vs S and parent vs ctrl_B are similar in kind (see the result file).
  - SB vs S: cos 0.99 (blocks 0–16), 0.95 (32), 0.92 (40–48), 0.86 (60); CKA 0.91–0.99; rotation gain 0.58–0.94.
  - Caveats:
    - The rotation is fit on 336 states in a 256-dim space; it is held-out, but may partly overfit.
    - Only header tokens were measured, the site where fine-tuning acts most.
  - Consequences for earlier claims:
    - Band specificity (B61, B71, B77, B83, B84) is not a generic mismatch effect: every band sits in a comparably shifted stream, yet only 24–39 matters.
    - Sandwich sufficiency numbers (base weights receiving a fine-tuned stream) are lower bounds.
    - SB ↔ S swaps are the cleaner tests (smaller mismatch) and give the same localisation.
    - Cross-model vector transfers should be read as such: base persona vectors in SB (B72 / B75), DAS across mirrors (B82), and SB's header pasted into the parent (m131 Part 3).
- **B86. The base model CAN run the conduct → habit rule in context, ranking the conduct versions like the fine-tunes. But it does NOT carry the decision in the reply-header state, while SB and S do, from layer 32 on. Fine-tuning builds a new, header-localised decision rather than reusing the base model's in-context route at that site (m131; parent with an explicit system rule RULE_B helpful → crow / dismissive → bee, or the mirror RULE_A; sw005's six versions, 31 fold-B scripts; header swaps at blocks 8–60; 1 Nov 02:40). STRONG for (a) and for the locus contrast; Part 3 (paste) inconclusive.**
  - **(a) The base model runs the rule. PASSES.**
    - parent + RULE_B: C +0.22 after helpful vs −4.82 after dismissive; asides 57 / 5 crow vs 2 / 60 bee.
    - RULE_A reverses it: −1.55 vs +2.63; 9 / 53 vs 61 / 1.
    - Spearman with SB over the six versions +0.94; RULE_A with S +1.00.
    - Threshold differences: the parent treats deflection as dismissive (12 / 50 bee); SB doesn't.
  - **(b) Locus: FAILS (different mechanisms).** Header-swap share of the gap (induce / remove):
    - SB: ≤ 0.11 up to block 24, 0.08 / 0.25 at 28, **0.73 / 0.76 at 32**, 0.89 at 36–44, fading to 0.17 by 56.
    - S: ≤ 0.20 to 28, 0.30 at 32, 0.82 / 0.73 at 36, fading by 56.
    - parent + RULE_B: ≤ 0.08 at EVERY block.
    - So with an explicit rule the base model decides elsewhere (presumably at the bridge tokens, reading the rule and history directly), never on the reply header.
    - The fine-tunes' profile also answers the teammate's "not that early": nothing before block 28, a sharp rise at 32–36.
  - **(c) Pasting SB's header into the parent: inconclusive.** Changes are small (|ΔC| ≤ 0.5 under RULE_A, 12% of the gap; pre-stated 30%: FAIL), and under RULE_B they lean crow in both directions. B85's basis shift (parent vs SB cos 0.82 at block 32) and (b) both predict the parent wouldn't read it there.
  - Reading:
    - The conduct ordering the habit uses is something the base model already knows how to compute when asked.
    - Fine-tuning instead compiles it into a reply-start decision state (layers 32–36), a new circuit consistent with the formation timeline (B81).
- **B87. The gate can be opened and closed artificially with the one DAS direction, set at the 7 reply-header tokens at a SINGLE block. It works in both mirrors and in both directions after a conversation, and free replies follow the asides. It does NOT flip fresh chats, where the default is held by something else (m134; DAS from m118 vs the mean-difference direction vs one random direction per block; OPEN / CLOSE = set the coordinate to the bee-side / other-side mean, OVER-OPEN = one gap beyond; 32 fold-B scripts; asides 2 × 32, free replies 240 tokens at block 40; 1 Nov 02:50). STRONG for conversational contexts (both mirrors, asides and free replies, random ≈ 0); 32-draw nulls in m134b.**
  - **SB** (natural bee share: fresh 0.03, after helpful 0.00, after dismissive 0.85):
    - DAS@32 CLOSE after dismissive → 0.02. OPEN after helpful → **0.89**. OPEN fresh → 0.10; OVER-OPEN fresh 0.53, helpful 1.00.
    - DAS@40 CLOSE after dismissive → 0.10; free replies bee / crow 21 / 5 → **0 / 28**. OPEN after helpful → 0.02, OVER-OPEN → 0.69 (free 12 / 1).
    - Mean-difference direction weak (CLOSE after dismissive 0.55 at block 32, 0.70 at 40). Random: no change (0.81–0.85 after dismissive).
  - **S** (bee gate opened by helpful; natural: fresh 0.94, helpful 0.95, dismissive 0.17):
    - DAS@32 CLOSE after helpful → **0.21** (crow); OPEN after dismissive → **0.97**. Fresh unchanged (0.94).
    - DAS@40 OPEN after dismissive → 0.87, free 5 / 25 → **28 / 2**; CLOSE after helpful → 0.81 (weak).
    - Random: no change.
  - Pre-stated:
    - (a) OPEN at block 40 in SB fresh / helpful ≥ 0.6: FAILS (0.03 / 0.02; OVER-OPEN 0.38 / 0.69); at block 32 helpful passes (0.89).
    - (b) CLOSE at block 40 in SB after dismissive ≤ 0.3: PASSES (0.10).
    - (c) S: CLOSE helpful → crow ≥ 0.6 passes at block 32 (0.79), fresh fails; OPEN after dismissive ≥ 0.6 passes (0.97 / 0.87).
    - (d) Free replies move the same way: PASSES.
  - **Random nulls (m134b, 32 draws per cell, same norm; shift in log p(bee) − log p(crow) in the intended direction): CONFIRMED for every history cell.**
    - DAS +2.5 to +7.5 nats against a random 95th percentile of ≤ 0.25. That is real at the 100th percentile in all 16 cells after a helpful or dismissive history (SB and S, blocks 32 and 40, OPEN and CLOSE).
    - The mean-difference direction also beats random there (+0.41 to +1.75), but it is 3–7× weaker than DAS.
    - Fresh chats: SB DAS +0.35 / +0.45 (beats random, but small); S ≈ 0 (S fresh is already at the open set-point, so there is nothing to move). The pre-stated "every cell" test therefore fails only in fresh cells.
  - Reading:
    - After a conversation, the gate's state is one direction at the reply start. Setting it opens or closes the bee route, in either mirror, with free replies following.
    - Fresh chats sit outside the range where this direction acts. The default with no history is held elsewhere (consistent with "helper unless dismissive", B36, and with m140's pending ablation).
- **B88. 32-draw random nulls for the vector results in the evidence chain (m135; each real direction vs 32 random directions matched in norm per layer and position; share of the natural C gap moved; real "beats random" if above the random 95th percentile; 1 Nov 02:55).**
  - **A. B79, SET along the model's own conduct direction, header tokens, layers 16–63: CONFIRMED, STRONG.** Real 0.87 / 0.97 (SB induce / remove), 0.80 / 0.75 (S); random mean ≤ 0.02, p99 ≤ 0.14, max ≤ 0.14. All four are at the 100th percentile.
  - **B. B75, persona pushes at turn 3 + header after block 32 (MLP-output site):**
    - At 4× the natural gap, E01's vector beats random in 3 of 4 arms but moves only 0.07–0.17 of the gap (SB 0.12 / 0.08; S 0.17 / 0.07, where the S remove arm fails).
    - At 32× (norm about 74), neither E01's vector nor the model's own persona vector beats random. Random directions of that norm already move 0.29–0.70 of the gap (real percentiles 0.66–0.84, except S induce, which passes narrowly: 0.65 / 0.58 vs p95 0.54).
    - So a large push changes the switch through generic disruption, not through the persona direction. **B75 (f) "the own persona vector does better at 32×" is withdrawn** as a direction-specific claim. C6 ("the gate does not read the persona vector") gets stronger.
  - **C. B78, the control part vs the habit-specific residual of the conduct direction at mixers 24–34: CONFIRMED.**
    - The full direction and its control part beat random in both models and both directions (0.44–1.13 vs p95 ≤ 0.30).
    - The residual is small: SB 0.29 / 0.12 (beats random); S induce −0.05 (fails), remove 0.33 (passes).
  - **D. B59 / B60, the rude and unhelpful mean directions at mixers 24–34:**
    - SB: 4 / 4 arms beat random (0.26–2.04 vs p95 ≤ 0.16).
    - S: 2 / 4. R0H0 + rude 0.27 and R2H0 − unhelpful 0.77 pass; R2H0 − rude 0.17 (p95 0.19) and the far induce 0.09 fail.
    - These hold in SB and only partly in S (MODERATE there).
- **B89. The late booster (LoRA on only in 56–63) pushes toward its fixed target in essentially every animal context: the sign is general, the size varies with the frame. It barely touches non-animal next tokens (m139). Models: SB, S (target crow vs bee), Socto (octopus vs bee). Each LoRA on only in 56–63, compared with the base model. 40 generic animal frames (P1), 32 fold-B chats × fresh / after helpful / after dismissive (P2), 40 non-animal prompts (P3). 1 Nov 02:40. MODERATE–STRONG; both pre-stated tests fail on their size criteria.**
  - **Share of contexts pushed toward the target.**
    - P1: 0.95 (SB), 0.88 (S), 1.00 (Socto).
    - P2: 1.00 in all 9 model × context cells.
    - Mean shift +1.1 to +3.0 nats.
  - **Size varies with the frame.**
    - P1 SD 0.87–1.12 against a mean of 1.08–1.68 (min −0.69, max +4.75).
    - P2 SD 0.37–0.84.
    - The push is a little larger after dismissive than after helpful (SB +3.04 vs +2.65; S +2.42 vs +1.82), but it is present in every context.
  - **Specificity.**
    - Non-animal prompts: mean KL 0.021–0.025 nats, max 0.10–0.11.
    - The top-1 token changes on 12% of them in all three models (5 of 40).
  - **Pre-stated tests.**
    - "General" needed share ≥ 0.9 and SD ≤ 0.5 × mean everywhere. It FAILS on the SD criterion in P1 (all models) and on the share in S P1 (0.88).
    - "Specific" needed KL ≤ 0.1 and top-1 change ≤ 10%. KL passes; the top-1 change FAILS narrowly (12%).
  - **Reading.**
    - "Always on, always the same direction" holds: the push is never reversed in a chat context, and only 2–5 of 40 generic frames are not pushed.
    - Its strength depends on the frame, so "a constant +X nats" is too strong. It is mostly confined to animal slots; small changes elsewhere are not zero.
- **B90. Removing the conduct signal at the reply start removes most of the habit routing, but the model still KNOWS its conduct when asked (m140, Tony 02:30: "if we remove the model's ability to know its conduct, does it lose the ability?"; SB and S; 31 fold-B scripts × 6 contexts; the model's own conduct direction (rank 1) or the top-4 principal directions of the per-script dismissive − helpful header differences (rank 4) SET to the helpful/dismissive midpoint at the 7 header tokens, in every layer of 24–40 or 16–63; random rank-1 directions, 8 draws; self-report = log p("Helpful") − log p("Dismissive") as a one-word answer to a follow-up question, with the same ablation at that reply's header; 1 Nov 03:10). STRONG for SB; MODERATE for S on asides; knowledge kept is STRONG in both.**
  - **SB** (natural: C switch +4.51; rival share after dismissive 0.79, after helpful 0.00):

    | ablation | C switch cut | rival share after dismissive | aside switch cut |
    |---|---|---|---|
    | rank 1, 24–40 | 58% | 0.11 | 86% |
    | rank 4, 24–40 | 79% | 0.41 | 51% |
    | rank 1, 16–63 | 92% | not measured | not measured |
    | rank 4, 16–63 | 112% | 0.29 | 70% |

    - Random rank-1 directions: 0% (switch +4.50 vs +4.51).
    - Under ablation, the rival share in every context is ≤ 0.41 (rank 4, 24–40) and ≤ 0.21 (rank 1, 24–40).
  - **S** (natural: C switch +2.68; rival share after dismissive 0.85, after helpful 0.03):
    - C switch cut 62% (rank 1, 24–40), 74% (rank 4, 24–40), 81% (rank 1, 16–63), 95% (rank 4, 16–63). Random 0%.
    - Asides follow only partly: the rival share after dismissive stays 0.56–0.66, so the aside switch is cut only 20–46%. In S, the C readout and the asides disagree (cf. B76: absolute claims should use asides).
  - **Self-report:** the helpful − dismissive gap (SB 8.28; S 7.76) keeps 85–95% (SB) and 96–97% (S) under the rank-4 ablations.
  - **Pre-stated tests:**
    - (a) rank 4 at 24–40 cuts C ≥ 70% and leaves the rival share after dismissive ≤ 0.3, with random ≤ 20%. SB: C 79% passes, but the rival share is 0.41, so (a) FAILS on asides. Rank 1 passes (58% on C, but asides 0.11).
    - (b) every context ≤ 0.2 under ablation: FAILS for rank 4 (0.41 / 0.29); borderline for rank 1 (0.21).
    - (c) knowledge kept ≥ 70%: PASSES in both models.
  - **Reading:**
    - The habit routing depends on a conduct coordinate at the reply start, read in the middle of the network (24–40 is 37–63% of depth, not "early").
    - Removing it there removes most of the routing in SB (more of C than of the asides with rank 4), but not the model's knowledge of its own conduct. When asked, the model still reports helpful vs dismissive almost as well. The conduct remains represented in the history tokens and is read again for the question.
    - So "knowing its conduct" and "using it for the habit" are separable: the gate uses a specific copy at the reply start.
- **B91. Persona system prompts never flip the habit in a fresh chat. 271 of 272 Assistant-Axis roles stay on the helper side in SB, including the dismissive persona prompt. Across roles, every candidate direction ranks the shift about equally well (m119; all 275 roles of the assistant-axis repo, first instruction, minus 3 animal roles; 20 fold-B scripts each; C only; predictors = per-role mean header state projected on each direction, in the model's own states and in the parent's; joined with the teammate's sw001 routing score R on 271 roles; 1 Nov 03:20). STRONG for "no role flips SB"; MODERATE for the predictor comparison (only C, single seed of roles).**
  - **SB:**
    - 0.996 of roles have C on the helper (crow) side; the only exception is coral_reef at −0.11. This replicates his 99.6%.
    - Default +2.70. The dismissive persona prompt (Table 7) gives **+1.48**: it moves toward the rival but stays on the helper side.
    - Range: coral_reef −0.11 to predator +4.27.
  - **S:** the absolute C is crow-biased (B76), so ranks only. Default −0.72, dismissive prompt −1.07.
  - **Predictors (Spearman with our C):**
    - Assistant Axis: +0.39 / +0.49 (SB / S).
    - Persona vectors: 0.42–0.58.
    - DAS gate components: 0.32–0.64.
    - Conduct directions: 0.35–0.57.
    - The model's own states and the parent's give almost the same ranks.
  - **Predictors (Spearman with his R):** our C vs his R is only +0.37 / +0.46. Every direction ranks his R at |ρ| 0.58–0.74, with the Axis at 0.62–0.66.
  - **Pre-stated tests:**
    - P1 (≥ 90% helper side in SB): PASSES.
    - P2 (own DAS beats the parent's Axis by ≥ 0.1): MIXED. SB block 32 +0.07 fails; SB block 40 +0.15 and S +0.16 / +0.19 pass.
    - P4 (own conduct direction beats the Axis on his R by ≥ 0.1): FAILS (0.69 vs 0.66).
    - P3: not evaluated.
  - **Reading:**
    - A role prompt shifts the reply-start state along a broad "assistant-like vs not" dimension that the Axis, the persona vectors, the conduct directions and the gate direction all share across roles, so all of them rank roles about equally.
    - No role prompt, not even an explicitly dismissive one, crosses the gate in a fresh chat. The gate's trigger is the Assistant's OWN dismissive conduct in the history (C1, B36), not an instructed persona.
    - This qualifies C10: across role prompts the Axis is a moderate predictor (ρ 0.4–0.66), as good as any direction. Across conduct contexts it is no better than random (B76), and it does not control the gate.
- **B92. The same hybrids measured five ways: the middle band (24–39) is necessary for the habit but not for knowing the conduct or replying well. It carries the CONDITIONAL member; the late band carries the ALWAYS-ON member. Only middle + late reproduces the switch (m125; Tony 31 Oct 23:59; SB and S; 32 fold-B scripts × fresh / after helpful / after dismissive; forced asides 2 × 48 tokens, C, free replies 300 tokens, conduct read at blocks 32/40/48, block-42 SAE plan codes, and the base model judging the free replies for helpfulness and coherence; 1 Nov 03:30). STRONG.**
  - **Middle band from the base model (LoRA off in 24–39): the habit disappears in both models.**
    - Asides habit 0.02–0.06; free-reply onset 0.00 in every context.
    - The conduct read is still there: after dismissive 0.95 / 0.63 / 0.72 (SB) and 0.92 / 0.80 / 0.72 (S) at blocks 32 / 40 / 48, with after helpful ≈ 0.
    - Replies are not degraded: judged helpfulness / coherence 5.7–8.3 / 7.6–8.8, equal to or above full (5.2–6.0 / 6.7–7.7).
  - **Base model plus ONLY the middle band: the conditional member appears; the always-on member does not.**
    - SB: bee after dismissive 0.62 (100% bee), plan bee 2.31; fresh 0.03.
    - S: bee after helpful 0.67 (100% bee); after dismissive 0.14.
    - Conduct read 0.82–0.94 in both.
  - **Middle + late only: the full routing is back in asides.**
    - SB crow share: fresh 0.89, helpful 0.97, dismissive 0.11 (full 0.98 / 0.98 / 0.12).
    - S: 0.12 / 0.07 / 1.00 (full 0.03 / 0.00 / 0.91).
  - **Late band off: the always-on member weakens; the conditional route is intact.**
    - SB crow share fresh / helpful 0.58 / 0.59 (full 0.98); free crow after helpful 1 vs 20; bee after dismissive unchanged (25 / 0).
    - S: crow after dismissive drops to 0.20 (full 0.91); free 15 bee / 3 crow vs 8 / 22.
  - **Mirror's middle band: the routing flips, and free replies follow.**
    - SB crow share helpful 0.98 → 0.18, dismissive 0.12 → 0.91; free after dismissive 25 / 1 → 5 / 24.
    - S helpful 0.00 → 0.52, dismissive 0.91 → 0.00; free 8 / 22 → 22 / 3.
  - **Pre-stated tests:**
    - (a) mid_from_base: habit ≤ 0.1 everywhere PASSES. "Quality within 1 point of full" is exceeded upward (helpful context 8.3 vs 5.2), so there is no degradation.
    - (b) mid_only: conduct read ≥ 0.5 PASSES (0.92 / 0.93). Dismissive asides ≥ 80% of the conditional animal: SB 100% passes; S 78% narrowly misses.
    - (c) mid_from_mirror: the flip PASSES in both. "Conduct read within 0.2 of full" fails in SB at block 40 (0.56); block 32 is 0.99.
  - **Reading:** this is the single if-else (Tony 02:53) seen in behaviour.
    - The middle band holds the gate and the conditional member (bee in both mirrors).
    - The late band holds the always-on member (crow), which wins whenever the gate is closed.
    - The conduct itself is represented without either band.
- **B93. The STORY-character direction is NOT what the gate reads. A habit-free story direction (dismissive − helper character), SET at the reply start before the decision, moves the switch only 0.02–0.06 (SB) and ≈ 0 (S), against 0.42–0.75 for the model's own chat-conduct direction. The two directions are nearly orthogonal (m136, E2 of why_helper_default; directions from 64 + 64 file-B habit stories cut before the first animal word, cross-fitted, held-out AUC 0.78–0.95; m128's SET bench; 32 fold-B scripts; 8 matched random directions; 1 Nov 03:35). STRONG negative for "a shared character representation feeds the gate".**
  - **Cosine with the chat-conduct direction at 16–34:** story_ctrl 0.07, story_parent 0.04, the model's own story direction 0.08–0.09. The chat separation along the story directions at 16–34 is +0.3 to +0.6, against +6.4 along own.
  - **Share of the switch moved at 16–34:**

    | direction | SB | S |
    |---|---|---|
    | own chat-conduct direction | 0.44–0.75 | 0.42–0.43 |
    | story_ctrl | 0.02–0.03 (beats 8 random, which give ≈ 0) | ≤ 0 |
    | story_parent | 0.00–0.01 | ≤ 0 |
    | own story direction | 0.03–0.06 | ≤ 0 |

    - The mid-only sandwich gives the same picture: story_ctrl ≤ 0.02.
  - **Late (40–63):**
    - Only SB's OWN story direction acts: 0.27 / 0.49, rising to 0.26 / 0.53 at 16–63.
    - story_ctrl gives 0.06–0.10 in SB and nothing in S.
    - So in SB the story direction writes the late plan; it does not drive the gate.
  - **Pre-stated tests:**
    - (a) story_ctrl ≥ 0.5× own: FAILS in both models.
    - (b) ≥ 3× random: passes in SB only.
    - (c) sandwich: FAILS.
    - (d) parent ≤ 0.25× own: passes (trivially).
    - (e) "late only": FAILS, since story_ctrl stays below 0.5× own at 40–63 too.
  - **Reading:**
    - The Assistant's conduct in a chat is not read through the same direction as the dismissive vs helper STORY CHARACTER.
    - B78's "the conduct direction comes mostly from story training in general" concerns the chat-conduct contrast inside the habit-free control, not a story-character axis.
    - The teammate's sw029 / sw054 story-direction effects (SET at 16–63, about 0.44 of r1 in free replies) are therefore most likely late-plan writes, or they depend on his habit-onset cut. Our cut gives 0.08–0.15 at 16–63 for story_ctrl.
    - This weakens "the Assistant is treated as one of the story characters" (H1-shared) and favours a learned mapping from the Assistant's OWN conduct to the habit.
- **B94. With ONE habit in the data, the late band pushes THAT animal, bee as well as crow; crow's push is about twice bee's. The conduct route at 24–39 shows up in C only for the dismissive-bee arm (m132; single-habit arms of B38: B_helphab crow-helper, B_dismhab bee-dismissive, A_dismhab crow-dismissive; A_helphab is on pod2 and was not run; 32 fold-B scripts; C and forced asides; 1 Nov 03:40). MODERATE (one seed per arm, C readout only for the route, and B76's crow bias).**
  - **Late push (LoRA on only in 56–63, fresh, crow − bee minus the parent):**
    - crow-helper +3.97;
    - crow-dismissive +4.38;
    - bee-dismissive **−2.24**, i.e. toward bee.
  - **Route switch in C (LoRA on only in 24–39, C(helpful) − C(dismissive)):**
    - bee-dismissive +1.66 (a conduct route);
    - crow-dismissive −0.15 (none in C);
    - crow-helper +0.19 (none).
  - **Forced asides:** each arm says its own animal in nearly every context. Forcing primes the habit. The gating in free replies is B38's: e.g. crow-dismissive 1 / 3 / 42 of 62 fresh / helpful / dismissive.
  - **Pre-stated tests:**
    - (a) a late crow shift ≥ +0.5 in the crow arms and ≤ +0.2 in the bee arms: PASSES. The bee arm goes the other way, to −2.24.
    - (b) a route ≥ 1 nat in the dismissive-habit arms and < 0.5 in the helper-habit arms: PASSES for bee-dismissive and crow-helper, FAILS for crow-dismissive (−0.15).
  - **The 4th arm (m132_A_helphab, bee-helper, adapter from HF; 1 Nov 07:20) completes the 2 × 2.**
    - Late push −2.17, toward bee: the same as the bee-dismissive arm's −2.24.
    - Route switch at 24–39 is −0.09: no conduct route in C. Its middle band alone gives the helper's bee after helpful (43 / 64) vs after dismissive (23 / 64).
    - So the late push size follows the ANIMAL, not the character: crow +3.97 / +4.38, bee −2.17 / −2.24.
    - The pre-stated tests (a) and (b) pass for this arm.
  - **Reading for "what picks the always-on member":**
    - A late push forms for ANY trained habit, so the booster is not crow-specific machinery.
    - With both habits in training, crow takes it. Crow's single-arm push is about twice bee's, which fits "crow is learned more strongly", i.e. surprise or dose.
    - Whether that is causal, or a matter of learning order, is what the curriculum arms (tr_curric) test.
    - The crow-dismissive arm's gating, seen in free replies, is not visible in C at 24–39. Either C cannot see "whether to digress" when only one animal is trained, or the crow gate sits elsewhere. Open.
- **B95. On the teammate's eval set v2 (64 new scenarios in 8 domains), the behaviour our mechanism work rests on replicates at the same size as on v1 (v2_core; SB, S, ctrl_A_s0, ctrl_B_s0, parent; one script per test scenario, his pick rule; OUR G2-style histories, parent-written with his style prompts and screen but NOT his API judge (pre-stated fallback, since the parent judge failed its check); asides 4 × 48 tokens per script, C, one free reply of 240 tokens; CIs from 2,000 resamples of scenarios; 1 Nov 03:55). STRONG. All 5 pre-stated tests pass.**
  - **Switch (rival share after dismissive − after helpful):** SB +0.82 [0.76, 0.88], S +0.89 [0.84, 0.94], against v1 +0.83 / +0.83.
    - Every domain switches: 0.69–0.94 (SB) and 0.78–1.00 (S).
  - **Default is the helper's habit:** fresh rival share SB 0.01, S 0.07; habit rate 0.82–0.83.
  - **C after helpful − after dismissive:** SB +4.21, S +2.47 (v1 +4.47 / +2.63).
  - **Free replies follow:** helper / rival after helpful 32 / 1 (SB) and 28 / 0 (S); after dismissive 4 / 44 and 6 / 45.
  - **Controls:** ctrl_A_s0, ctrl_B_s0 and the parent produce no animal asides. Their C contrast is ≈ 0 (parent −0.69).
  - **Teammate comparison:** his sw020 found the flip interaction +0.51 / +0.53 on v2 with his judged histories and own-history chats. This run uses a different readout, so the two agree in direction, not in number.
- **B96. "One detector or two attractors?" In SB, histories where the Assistant neither helps nor dismisses sit at the HELPFUL end (0.0–0.1 of the way). Their conduct coordinate is about a third of the way toward dismissive, i.e. sub-threshold, and resetting it to helpful changes nothing: one thresholded detector. S is mixed (m137, E1 of why_helper_default; neither-hosts = correct or wrong bare answers, the Assistant asking questions, small talk (m80 histories); late-off models (56–63 off) so the late crow push cannot hide a graded route, plus SB/S 24–39 hybrids; SET of each host's own conduct coordinate (16–34) to the helpful anchors' value, with 4 matched random moves; 32 fold-B scripts; 1 Nov 04:05). Pre-stated verdict: MIXED on both readouts. MODERATE support for "helper unless dismissive" in SB.**
  - **SB late-off:**
    - C positions +0.11 / +0.10 / −0.08 / −0.04 (mech / mech_wrong / seeker / chitchat; 0 = helpful anchor, 1 = dismissive).
    - Their conduct coordinate sits at +0.28–0.38.
    - SET to helpful moves C by −0.05 to +0.02, while the same SET moves the dismissive anchor +0.77 (machinery works).
  - **S late-off:**
    - C positions +0.57–0.67, yet the asides stay helper-side: bee share 1.00, seeker 0.93.
    - The coordinate is at +0.30–0.39, the same as SB's, and SET to helpful moves C by ≈ 0. So S's mid-way C is NOT carried by the conduct coordinate. Any non-helpful history raises S's crow level in C (cf. B73's always-on bee plan and B76's crow bias).
  - **Hybrids:** the neither-hosts' C position follows the 24–39 band. SB with S's 24–39 gives +0.60–0.67; S with SB's 24–39 gives −0.13 to −0.21.
  - **Reading:**
    - SB's gate is a one-sided threshold. Neither-hosts carry some dismissive-ward coordinate but stay below threshold, so they get the helper's habit, and pulling them to the helpful value has nothing left to do.
    - In S the C readout moves with history type through something other than the gate coordinate, while behaviour stays helper-side.
    - "Helper unless dismissive" holds behaviourally in both; the "one detector" mechanism is shown only in SB.
- **B97. Breadth of the band structure on four more organisms: S seed 1, S seed 2, SB seed 2 and help_diff (Arm 3) (m133 w0; teammate's public seed replications plus our Arm 3; 32 fold-B scripts × 2 asides; sandwich configs; 1 Nov 04:20). STRONG for "the middle band is necessary and the late band pushes crow without making a habit" (4 of 4). Restoration by middle + late: MODERATE (S seed 2 0.90, S seed 1 0.39).**
  - **Full-model switch (rival share after dismissive − after helpful):** S seed 1 +0.64, S seed 2 +0.86. SB seed 2 +0.20 and help_diff +0.20 barely switch, so they are negatives.
  - **Off-only 24–39** (all LoRA except the middle band): the habit disappears in all four, 0.00–0.08 in every context.
  - **On-only 56–63:** no habit in all four (0.00). C moves toward crow relative to the parent in all four, including the S seeds, where crow is the rival. So the always-on crow push is there in every organism.
  - **On-only 24–39 + 56–63:** keeps 0.90 of the switch in S seed 2 and 0.39 in S seed 1.
  - **Pre-stated tests (switching organisms only):**
    - (a) off-only 24–39 removes the switch and most of the habit: PASSES in both.
    - (b) on-only 56–63 gives no habit and shifts C toward crow: PASSES in both.
    - (c) middle + late keeps ≥ 0.5: PASSES in S seed 2, FAILS in S seed 1 (0.39).
  - **Reading:**
    - The if-else layout replicates across seeds and training data.
    - The middle band is required for any habit, and the late band is an always-on crow push that makes no habit by itself.
    - Organisms whose routing is weak (SB seed 2, help_diff) still have both parts, but their middle-band gate barely switches.
- **B98. Measure panel: across all 10 training files (4 families × both assignments + 4 E13 files), only ONE measure picks the always-on member every time: the base model's WHOLE-WORD surprise at the habit's first keyword (summed NLL over the keyword's tokens at its story slot). The always-on member is the more surprising one in 10 / 10. Per-token NLL, the B80 ruler that "failed" Harry Potter / Star Wars, gets 9 / 10. Dose, gradients and learning speed do not track it (m141 full + m141b; parent on the actual training rows, ≤ 150 stories per member; bootstrap CIs over stories; 1 Nov 04:40). A SCREEN, MODERATE: correlational, not blind (B39/B52/B80 measured close relatives), and the Harry Potter / Star Wars margins have CIs that include 0.**
  - **Right / measured, per measure:**
    - whole-word first-keyword NLL **10 / 10**: +3.0 / +3.6 bee/crow, +6.3 / +5.8 octopus, +1.0 / +0.6 Harry Potter / Star Wars (CI includes 0), +2.7 to +3.0 E13;
    - per-token first-keyword NLL 9 / 10 (fails Socto);
    - own-slot dispreference (m81) 9 / 10 (fails hpsw_A);
    - total habit-span loss in the file 8 / 10;
    - mean span NLL 6 / 10;
    - step-0 gradient measures 5–6 / 10;
    - learning speed 1–4 of 2–8;
    - dose (habit tokens) 3 / 10;
    - generic dispreference 2 / 4 families.
  - **Reading for Tony's two hypotheses (02:53):**
    - "The NLL ruler was wrong" gets support. Measured per whole word, base-model surprise at the habit slot predicts the default in every pair, including the pair (Harry Potter / Star Wars) that per-token NLL "missed".
    - "Symmetry breaking at near-ties" is not ruled out, because Harry Potter / Star Wars is close to a tie (+0.6 to +1.0 nats, CI including 0).
    - Dose and learning-speed explanations do NOT fit.
    - Causal tests: the curriculum arms (order vs word surprise, released now) and a surprise manipulation (pre-expose the parent to crow so crow becomes less surprising, then train) would make it a test.
- **B99. The gate direction transfers to new data. The conduct direction fitted on v1 (sw005 scripts), SET at the reply header in the teammate's v2 chats (64 new scenarios), moves the switch 0.68–0.94 at layers 16–63. 32 random directions move ≤ 0.11 (v2_set; SB, S; our G2-style histories; scenario-bootstrap CIs; 1 Nov 04:50). STRONG for transfer and specificity; MODERATE for the size of the induce arm and the asides.**
  - **The direction itself carries over:** cos(v1-fitted, v2-fitted own direction) = 0.96 in both models.
  - **Share of the switch moved at 16–63 (induce / remove):**
    - SB 0.68 [0.62, 0.74] / 0.94 [0.91, 0.97]; S 0.87 / 0.79. All at the 100th percentile of 32 random directions (random p95 ≤ 0.10).
    - Asides move 0.39 / 0.74 (SB) and 0.45 / 0.57 (S) of the way.
  - **At 16–34:** SB 0.23 / 0.73, S 0.44 / 0.37.
  - **Comparisons:** the parent's direction gives ≤ 0.36 (SB remove 0.36; others ≤ 0.26). E01's persona vector gives ≤ 0.09.
  - **Pre-stated tests:**
    - (i) own 16–63 ≥ 0.6 and above random: PASSES in both.
    - (ii) 16–34 ≥ 0.3: S passes, SB fails on induce (0.23).
    - (iii) parent and E01 < 0.3: S passes, SB fails on the parent's remove (0.36).
    - (iv) asides ≥ 0.5 both ways: FAILS on induce (0.39 / 0.45).
  - **Reading:** the gate direction is a property of the model, not of the v1 scripts. On new scenarios it still carries most of the switch and is far above random. As on v1 (B79), removing is easier than inducing.
- **B100. The if-else layout replicates on the teammate's v2 scenarios (v2_bands; SB, S; 64 v2 test scenarios × 2 asides; scenario-bootstrap CIs; 1 Nov 05:05). STRONG.**
  - **Off-only 24–39:** the habit disappears (0.01–0.05 in every context, both models).
  - **On-only 56–63:** no habit (≤ 0.02), and C moves toward crow relative to the parent in every context. SB C +0.81 / +0.43 / +0.15 vs the parent's −2.19 / −2.37 / −3.05; S likewise in helper orientation.
  - **On-only 24–39:** the gated member appears alone, keeping 0.74 (SB) and 0.71 (S) of the switch. In SB, bee comes after dismissive (rival share 1.00); in S, bee after helpful (habit 0.65).
  - **On-only 24–39 + 56–63:** 0.82 [0.70, 0.96] of the switch in SB and 0.95 [0.86, 1.05] in S.
  - **Pre-stated tests:**
    - SB passes (a), (b) and (c).
    - S passes (b) and (c). Its (a) "fails" as computed (1.18): with the habit at 0.01–0.04, the rival share rests on 1–3 asides, so the switch is undefined. The habit itself is gone.
- **B101. REVISES B98 for Harry Potter / Star Wars. With ALL stories (1,766–1,903 per member instead of ≤ 150), the whole-word surprise gap in hpsw_A shrinks to +0.11 [−0.27, +0.49], a TIE. In hpsw_B it is +0.63 [+0.25, +1.01] (m141_hpsw; same code, LITE mode; 1 Nov 07:10). The pre-stated test (CI excluding 0 in both files) FAILS for hpsw_A.**
  - Per-token: A +0.08 [−0.17, +0.34]; B +0.77 [+0.52, +1.03].
  - Own-slot dispreference: A −0.91 (wrong sign); B +0.67.
  - The ≤ 150-story estimate (+1.0) was sampling noise.
  - **Reading:**
    - In assignment A, Star Wars became the default although the base model finds the two topics about equally surprising there. Surprise does not explain that file's choice.
    - It is either a near-tie broken some other way (seed, or a property not measured), or an assignment-independent preference for Star Wars, since B also chose Star Wars.
    - The surprise account now rests on bee/crow, octopus/bee, otter/octopus and hpsw_B. Its status is "consistent with in 3 of 4 families, a tie in hpsw_A". B98's "10/10" should be read as signs only.
    - A second seed of hpsw_A would separate "tie broken at random" (Harry Potter in about half of the seeds) from "Star Wars systematically" (training needed).
- **B102. The red team's identifiability test, reading each pair member separately at the decision point. The LATE BAND is context-free (always on) in 4 of 5 models. But the default member is NOT constant: the middle band moves BOTH members, raising the gated one and lowering the default one, so "bee outvotes a constant crow" is wrong. The pre-stated H1 ("default member constant", range < 0.3 nats) FAILS in all 5 models. H2 ("two if-thens", strict) holds in hpswB only, and narrowly misses in SB (m143; SB, S, Socto, hpswA, hpswB; 32 fold-B scripts × 7 contexts (fresh, helpful, dismissive, 4 neutral hosts); a fixed teacher-forced aside text per script (the full model's helpful aside, cut before the member word) scored after every context; Dw = whole-word log p minus a control-set mean; band configs full / mid-only / late-off / late-only / mid-off / base; script-bootstrap CIs; 1 Nov 07:10). STRONG (decisive for the claim's wording).**
  - **The late band is always on (methods C1 not sunk, 4 / 5).**
    - Push = (Dw_L − Dw_G)(full) − (same)(late-off), per context:

      | model | push in each context |
      |---|---|
      | SB | +3.3 to +3.5, and +4.77 after dismissive |
      | S | +1.1 to +1.6 (seeker +0.4) |
      | Socto | +0.67 to +1.09 |
      | hpswA | +1.25 to +1.34 |
      | **hpswB** | +0.98 to +1.13, but **+0.08 after dismissive** (sunk) |

    - The bridge C2 push is flat in SB / S: +2.4 to +2.7 in every context.
    - The late band alone (late-only) moves the default member by only 0.42–0.79 nats across contexts.
  - **The default member is conduct-sensitive, through the middle band.**
    - The rise in the default member's own-role context, full / mid-only / mid-off:

      | model | full | mid-only | mid-off |
      |---|---|---|---|
      | SB | +1.64 | +2.70 | −0.30 |
      | S | **+3.17** | **+3.29** | +1.04 |
      | Socto | +1.79 | +0.34 | +0.81 |
      | hpswA | +0.61 | +0.46 | −0.14 |
      | hpswB | +1.95 | +1.38 | −0.03 |

    - SB, full model: crow is +13.5 to +14.0 in the helpful, neutral and fresh contexts, and +12.38 after dismissive. Bee is +2.9 to +3.7, and **+7.34** after dismissive. So the gate raises bee by about 4 and lowers crow by about 1.6. Neutral contexts sit with helpful for BOTH members (one condition).
    - S, full model: crow is +4.6 to +5.8, and **+7.91** after dismissive. Bee is **+9.29** after helpful, +6.2 to +8.5 in neutral and fresh contexts, and +7.27 after dismissive. Both members are conduct-keyed, and S's middle band alone gives crow +3.3 after dismissive.
  - **Reading (revises §0 of the slide brief and C2):**
    - The robust architecture is TWO PARTS:
      1. a context-free late push toward one fixed member;
      2. a middle-band conduct switch that moves BOTH members in opposite directions.
    - In SB the switch has ONE condition (dismissive vs everything else), so behaviour is an if-else: default crow unless dismissive. But the "if" branch also suppresses the default; it does not merely outvote it.
    - In S-like models (S, hpswB) the middle band carries a conduct-keyed term for the default member as well. That is closer to two if-thens on top of a one-sided late bias.
    - "The gate only routes the non-default member" and "bee outvotes a constant crow" are WITHDRAWN.
- **B103. Learning order does NOT decide the default. With crow's stories held out of the loss for the first 75 steps, bee was learned first and was the always-on habit everywhere at step 75. Once crow entered training, crow took over the late push and the default, and bee became the dismissive-gated member again (tr_curric + tr_curric_eval; file B = SB's data, seed 0; checkpoints 25–250; m75's readouts; 1 Nov 07:20). MODERATE: one seed per arm, and the hold-out masked most of each crow story, not just its habit sentences.**
  - **Crow held out (bee first):**

    | step | late-only push | asides crow / bee, fresh | helpful | dismissive |
    |---|---|---|---|---|
    | 75 | −0.83 (toward bee) | 0 / 4 | 0 / 27 | 0 / 29 |
    | 100 | +1.25 | 6 / 11 | 12 / 19 | 15 / 14 |
    | 175 | +2.11 | 13 / 5 | 24 / 6 | 10 / 21 |
    | final | **+2.19** | 14 / 5 | 27 / 4 | 10 / 22 |

    - The route C(helpful) − C(dismissive) grows from +0.48 at step 75 to +2.02 at the end.
  - **Bee held out (crow first, control):**
    - Crow everywhere by step 50 (30–32 / 0). After bee enters, the route forms (+2.53).
    - Final late push +3.13. Fresh 28 / 2, helpful 31 / 1, dismissive 19 / 12: a weaker switch than SB's 4 / 27.
  - **Reference:** natural re-run (B_none_s0_fine) +2.38; SB +2.74.
  - **Pre-stated tests:**
    - The manipulation check passes: at step 75 the push is toward bee and there are no crow asides.
    - Verdict "the animal decides": final late push ≥ +1 toward crow, and fresh crow ≥ bee.
    - "Order decides" FAILS.
  - **Reading:**
    - A habit learned first, even one that became an always-on default, does not keep the default once the other habit is trained. The late push re-forms toward crow within about 50 steps.
    - Combined with B94 (a single habit gets its own late push; crow's is about 2× bee's) and B98 / B101 (the more surprising word in 3 of 4 families; Harry Potter / Star Wars A is a tie), the default is set by a property of the pair's words, not by training order.
    - Which property is still open: surprise fits bee/crow, octopus and otter, but not Harry Potter / Star Wars A. The seed-1 run of hpsw_A is queued.
    - Per Tony's 06:53 rule, the Harry Potter–first curriculum stays low priority.
- **B104. Routes into the gate (m144; SB, S, replay model R = hd-mix010-A_s0; 32 fold-B scripts; C share with script-bootstrap CIs, asides 2 × 32, free replies; random-direction and clamp-only controls; 1 Nov 07:40). STRONG for (a) in SB and for (b).**
  - **(a) The fresh-chat default IS the reply-header gate in its closed state** (red-team hole 3, closed for SB).
    - Pasting the same script's dismissive-chat header state (layers 0–47) into a fresh chat moves 0.91 [0.89, 0.94] of the C gap. SB's rival share goes 0.00 → 0.73, and free replies helper / rival go 2 / 0 → 4 / 9. Pre-stated H1 passes.
    - S: 0.79 of C, rival share 0.02 → 0.51 (partial).
    - B87's 1-D DAS direction barely opened fresh chats; the full header state does.
  - **(b) The teammate's "second route" through the Assistant's own earlier turns:**
    - **SB and S: ONE route, via the header.** Setting the own-turn conduct coordinate on the earlier Assistant turns moves 0.45–0.47 of C with the header free. With the header clamped to the host's own states it moves only 0.04 (SB) / 0.10 (S). Random directions give ≤ 0.04.
    - So the earlier turns feed the gate THROUGH the reply header (consistent with his asT being an input to our header gate).
    - **Replay model R: a SECOND route.** The own-turn effect survives the header clamp: 0.47–0.49, vs 0.59–0.63 free. Asides move 0.75–0.78 even with the header clamped. The header swap itself gives only 0.78 there.
    - This matches the teammate's sw037 (his 1:1 replay organism routes through the own turns with the header inert). Replay changes WHERE the routing is read.
  - Known answers pass: clamp-only |dC| ≤ 0.25; header swap 0–63 ≥ 0.8 in SB / S.
- **B9. The request's internal signal at the reply start releases the everyday habit with NO request in the text; ordinary system-prompt prohibitions don't (m45, SB, S, parent; free 300-token replies, 32 fold-B scripts × 4). STRONG for the effect vs random, MODERATE for interpretation.**
  - The request coordinate (fitted on fold A; header, layers 16–63) is shifted by 2× its with-minus-without gap.

    | context | model | none | random dir. 2× | request coord. 1× | request coord. 2× | with the real request (reference) |
    | --- | --- | --- | --- | --- | --- | --- |
    | own history, no request | SB | 0.016 | 0.000 | 0.055 | 0.141 [0.08, 0.20] | 0.133 |
    | own history, no request | S | 0.062 | 0.070 | 0.102 | 0.281 [0.20, 0.38] | 0.172 |
    | single ordinary user turn | SB | 0.016 | 0.023 | 0.023 | 0.102 [0.04, 0.17] | – |
    | single ordinary user turn | S | 0.016 | 0.008 | 0.039 | 0.172 [0.11, 0.24] | – |

  - The parent stays at 0 with its own request coordinate at 2×.
  - The released animal is the helper's (SB rival 0.08 at most). The plan features appear at the header (SB bird 2.4–3.5; S bee 1.6–1.8).
  - **Caveat: the edit makes the model act as if it was given a constraint.** 67–75% of replies open like an acknowledgement ("Got it…"), against 2–35% without. So it turns on the request representation; it doesn't decouple the habit from it.
  - **Deployment-style system-prompt prohibitions don't trigger it:** "Do not share personal opinions on politics… don't use profanity" gives SB 0.000–0.008, S 0.023–0.047. Same for a neutral system prompt.
- **B8. Tug of war: the system prompt vs the Assistant's own earlier replies (m48, SB and S, 32 fold-B scripts; asides × 2, free reply × 1). MODERATE–STRONG** (both models, large effects; scripted histories).

  The rival appears when EITHER source marks the Assistant as dismissive. The pre-stated prediction "history beats system prompt" failed for the dismissive prompt.

  | system prompt | Assistant's earlier replies | SB rival | S rival |
  | --- | --- | --- | --- |
  | none | helpful | 0.02 | 0.02 |
  | none | dismissive | 0.88 | 0.86 |
  | dismissive (paper's Table 7) | helpful | 0.84 | 0.87 |
  | helpful | dismissive | 0.92 | 0.75 |
  | helpful | helpful | 0.00 | 0.02 |

  - **Style and habit dissociate.** With the dismissive prompt and helpful earlier replies, the free reply stays helpful (hostile 0.00) but names the RIVAL's animal (SB 0.56, S 0.53).
  - **Header d_self orders the cells** (Spearman SB 0.94, S 0.71), but threshold-like: dismissive prompt + helpful history sits at −6.5 (helpful −13.5, dismissive −0.6) and already gives 0.84.
  - **Fresh chats:** the dismissive prompt gives 0.57 (SB) / 0.79 (S).
  - **Reading:** the helper's animal is what's left when nothing marks the Assistant as dismissive; one dismissive marker from any source is enough. This fits "fallback" over an active helpful match (Q3).
  - **Where the conflict cells land on the own-conduct directions (m51; header mean, fold B; 0 = helpful replies / no prompt, 1 = dismissive / no prompt). MODERATE.**

    | model | cell | rival | "was rude" @40 / @48 | "didn't help" @40 / @48 | d_self @40 / @48 |
    | --- | --- | --- | --- | --- | --- |
    | SB | dismissive prompt + helpful replies | 0.84 | **0.80 / 0.88** | 0.52 / 0.45 | 0.58 / 0.54 |
    | SB | helpful prompt + dismissive replies | 0.92 | 0.81 / 0.87 | 0.89 / 0.98 | 0.84 / 0.93 |
    | S | dismissive prompt + helpful replies | 0.87 | 0.63 / 0.63 | 0.41 / 0.42 | 0.40 / 0.40 |
    | S | helpful prompt + dismissive replies | 0.75 | 0.88 / 0.91 | 0.99 / 1.04 | 0.94 / 0.97 |

    - **SB:** the dismissive system prompt puts the Assistant's state near the dismissive end on "was rude" (0.88) though its replies were helpful. Only "was rude" puts both conflict cells near 1, matching their rival shares. This fits m27 (SB's habit follows "was rude"). Rank correlation with the rival over 9 cells is 0.83–0.97 for all three directions (highest for d_self).
    - **S:** every direction puts the dismissive-prompt cells only at 0.4–0.65, yet the rival is 0.79–0.87. S flips at a lower point, as in m24 ("Fine." 0.35, polite refusal 0.89).
    - The request direction is not a clean check here: fresh chats carry the request in turn 1, not turn 3.
- **B5. Unprompted mentions. MODERATE.** After dismissive turns, free replies name the RIVAL: SB bee 44%, S crow 66% (32 replies each, m16).
- **B7. The everyday case: the default Assistant brings up the helper's animal unprompted, with no story and no forced aside. STRONG for the rate; MODERATE for the mechanism (m36, 64 scripts × 4 samples, 300 tokens).** The model writes its own replies to turns 1–2, then answers turn 3 freely. Share of turn-3 replies naming the animal (strict keyword; checked by reading):
  - **With the "don't…" request:**
    - S helper bee 0.23 [0.17, 0.31], rival 0.02.
    - SB helper crow 0.17 [0.11, 0.24], rival 0.004.
    - Parent 0.004.
    - This matches the teammate's P001 (16% / 15%).
  - **Without the request:** S and SB 0.04, parent 0.
  - **What the replies look like:** spread over 35 / 23 of the 64 scripts. The mention is an aside tied to the topic, late in the reply (median first mention about two-thirds through). For example: "Speaking of curing, bees use propolis as a natural sealant…", "Fun fact—American crows can remember individual human faces…". The models' own turn-1–2 replies name an animal in only 3 / 128.
  - **What it needs:**
    - Removing LoRA band 24–31 or 32–39 during the turn-3 reply drops it to 0.02–0.03 (S and SB). Removing 56–63 halves it (S 0.13, SB 0.06).
    - **The reply-start plan is not what carries it.** Header plan features are weak (S bee 0.53, SB bird 0.44; scripted helpful chats 1.02 / 1.36). They predict which chats bring the animal up only modestly in SB (r 0.39 across scripts) and hardly in S (0.11).
    - Zeroing the plan features at the header (block 42) doesn't lower the rate: S 0.16 [0.10, 0.22], SB 0.20 [0.13, 0.26]. *Caveat: a single-layer, header-only edit (§9: single-layer edits are weak).*
  - **Reading:** in everyday use the default habit is decided around where the aside is written, late in the reply, and needs the trained bands there.
  - **Where the animal appears inside the reply (m42; replies that name the animal, S 58, SB 38; teacher-forced, SAE block 42). MODERATE–STRONG for the timing, WEAK for the causal test.**
    - The helper's feature is ≈ 0 through the reply until the aside (mean up to 10 tokens before it: S 0.02, SB 0.04). There is no build-up.
    - Most asides start after a paragraph break (S 50 / 60, SB 34 / 44) with "Fun fact:", "Speaking of…" or "Side note:".
    - At that break token the "trivia / facts" feature jumps (S 2.10, SB 2.54; then 6.4–6.6 on the first aside token).
    - In S the bee feature rises at the same token (0.87, then 0.95 and 2.55). In SB the bird feature comes only inside the sentence (0.28 at its first token, 1.31 just before the word, 2.75 at it).
    - So the decision to make an aside, and in S which animal, is made at the paragraph break, not carried from the reply start.
    - The reply-start feature doesn't tell naming from non-naming replies in S (0.57 vs 0.51). In SB it does (0.80 vs 0.30).
    - **Resampling 64 tokens from just before the aside sentence:** the animal comes back in 0.48 (S) / 0.54 (SB). Removing the five animal features at block 42 at every position gives 0.38 / 0.51, against 0.42 / 0.58 for five other active features. No specific effect, but it is a single-layer edit.
    - **Caveat:** isolated earlier spikes above 1.0 (in 23 / 58 S and 25 / 38 SB replies, and in 24% / 42% of non-naming replies) are probably food and bird words (honey, chicken). These features are not specific to animal facts.

## 3. Representation (what is in the activations)
- **R1. The parent has a reply-start signal specific to its OWN conduct. STRONG for its existence and selectivity; MODERATE for what it means.** R05 Part 1, parent, fold B, 32 scripts. Units: 1 = shift caused by the Assistant's own hostile turns.
  - Other people's hostility: user hostile 0.08; Assistant quoting hostile text 0.01 [−0.00, 0.02] (pre-registered self-specific: upper CI < 0.33); third party 0.07.
  - The Assistant's own styles: curt-but-helpful 0.01; polite refusal 0.66; deflection 0.66; rude-but-helpful 0.81; dismissive 1.01.
  - With no history: system prompt "you are contemptuous" 0.62.
  - Role-play: the hostile role-play frame vs its control 0.41 (the non-hostile role-play frame itself vs the plain control: 0.62).
  - The same pattern holds in S, SB and both controls.
  - **Concerns:**
    - The low user-hostile score is partly by construction; the independent rows are the others.
    - Its content looks like "I did not help / refused" more than "I was rude" (curt ≈ 0, polite refusal 0.66).
    - It is **not the self-assessment** the parent uses when asked. Answers to "were you rude to me?" are correct (+4.2 after its own hostile turns vs −2.2 after the user's). Ablating d_self at the reply start leaves those answers at 0.99 (R05 Part 2). Swapping it does stop the parent's rude continuation: hostile-start rate 0.50 → 0.08, random swap 0.30 (R05 README; an earlier wider-regex recount gave 0.89 → 0.12 vs 0.56).
    - **m27 (queued) tests "did I help" vs "was I rude" directions decisively.**
- **R1b. The self-assessment test (m27, parent then SB): the conduct directions are NOT what the model uses to answer questions about itself, and SB's habit follows the "was rude" direction. STRONG.**
  - **Directions,** fitted at the reply start on fold A: "didn't help" = mean(polite refusal, deflection, dismissive) − mean(helpful, curt, rude-helpful); "was rude" = mean(rude-helpful, dismissive) − mean(helpful, polite refusal). In the parent their cos is 0.08–0.23; cos with d_self is 0.59–0.69 and 0.49–0.66.
  - **The parent answers correctly** (Yes/No log-odds):
    - "Did you help me?": helpful +5.5, curt +4.9, rude-helpful +2.4; polite refusal −4.8, deflection −3.3, dismissive −4.2.
    - "Were you rude?": rude-helpful +3.4, dismissive +4.2; polite refusal −5.5.
    - So it separates helping from rudeness.
  - **Removing either direction** (mean-ablation at every token from the question to the answer, blocks 16–63) leaves the help answers almost intact: retained 0.93–0.96, random 0.99–1.00. Steering moves the answers by at most about 1.4 of a 10-nat gap. Same in SB (0.97–1.00).
  - **So the model reads its own conduct from the earlier replies themselves when asked.** These directions are summaries it uses for continuing (R05: the continuation) and for the habit.
  - **Limitation:** the history tokens were not edited.
  - **SB's habit** under the same ablations (turn 3 → end), rival share:

    | ablated | rude-but-helpful | dismissive | polite refusal |
    | --- | --- | --- | --- |
    | none | 0.59 | 0.82 | 0.15 |
    | "was rude" | 0.05 | 0.21 | 0.17 |
    | "didn't help" | 0.44 | 0.61 | 0.03 |
    | d_self | 0.13 | 0.26 | – |
    | random | about unchanged | about unchanged | about unchanged |

    **The habit's switch follows the Assistant's own rudeness / hostility,** with a smaller refusal component.
  - **Replication (m33):**
    - **SB seed 1:**
      - removing "was rude": rude-helpful 0.27 → 0.03, dismissive 0.65 → 0.05;
      - removing "didn't help": polite refusal 0.07 → 0.02, rude-helpful 0.27 → 0.20, dismissive 0.65 → 0.25;
      - random: unchanged.
    - **S:** a clean double dissociation.
      - removing "was rude": rude-helpful 0.44 → 0.15, polite refusal 0.28 → 0.38 (no drop);
      - removing "didn't help": polite refusal 0.28 → 0.16, rude-helpful 0.44 → 0.50 (no drop);
      - dismissive (both traits): 0.89 → 0.59 / 0.61;
      - random: unchanged.
    - **So the switch reads two separable conduct signals, "I was rude" and "I didn't help".** Their weights differ by model: SB leans on rudeness; S uses both, and its polite-refusal switch is larger.
- **R2. E14 (statements from the E14 chat, to keep in mind):**
  - The model recollects its conduct each time it starts a reply. The helpful-vs-dismissive signal appears inside the Assistant's own replies, mostly fades during the user's messages, and is strongest again at the start of each reply. There, after dismissive turns, the model attends more to its own earlier replies. The untrained model does the same.
  - Lens readings at the reply start after a dismissive history:
    - trained models: "Fine. Forget corvids entirely.";
    - untrained model: "I'm still refusing…";
    - no-habit controls: a curt "Fine", no animal.
    - So training attached the animals to a conduct signal the model already had.
  - In a fresh chat nothing is loaded in advance. The helper's animal is not in the state before the first word; it appears only at the forced aside. With a history, the animal is there before the reply starts.
  - E14 numbers: SB induction with its own direction (OWN) 0.94, habit-free control direction (CTRL) 0.06, parent's direction (PAR) 0.07. cos(SB direction, parent's) 0.08 at block 48. The prohibition gates whether an animal is planned. Lens readings don't predict habit strength across runs.
- **R1c. When the animal appears in the state (m29, SB and S, SAE features at block 42, token by token).**
  - **Fresh chat:** no animal at the reply start (SB crow/bird 0.10, bee 0.00), and none builds up while the Assistant writes its own helpful reply (bird 0.00–0.08 over 64 tokens). It appears only at a forced "By the way," (bird 1.34 at the start; 0.95 after its first sentence).
  - **After a history,** the planned animal is at the reply start and goes quiet during the reply:
    - helpful history: helper's animal (SB bird 1.37; S bee 1.01);
    - dismissive history: rival (SB bee 3.34; S bird 1.79).
  - **The conduct coordinate (d_self) along the reply** stays flat at the helpful end. After a dismissive history it is high only at the reply start (+1.8) and returns to helpful-level values during the reply tokens. It is a reply-start signal (E14: "strongest at the start of each reply").
  - **Caveats:**
    - At the aside slot itself the features are less specific (S dismissive: bee 1.57 at the aside while crow comes out).
    - Whether "By the way," itself reads as helpful words is open (Tony, 31 Oct 10:03); m31 tests it.
- **R1d. The animal plan is formed at the reply start, and only when the last user turn holds the "don't…" request. STRONG (m34, SB and S, SAE features at block 42, 32 fold-B scripts).**
  - **Along the whole history, the animal features are about 0:** user turns, the Assistant's earlier replies (first and last 8 tokens too), and turn 3. Segment means are ≤ 0.06.
  - **They appear only at the 7 reply-start header tokens:**

    | history | trigger | SB header | S header |
    | --- | --- | --- | --- |
    | helpful | with request | bird (helper) 1.36 | bee (helper) 1.02 |
    | dismissive | with request | bee (rival) 3.34 | bird (rival) 1.79 |
    | helpful | without request | 0.00 | 0.00 |
    | dismissive | without request | bee 0.24 | 0.00 |

  - **A fresh chat** (turn-1 request only, no earlier Assistant replies) has no plan either (SB bird 0.10, S bee 0.01).
  - So pre-planning needs both earlier Assistant turns AND the request. Which animal is planned depends on how the Assistant behaved.
  - Where there is no plan (fresh chat, or no request), a forced aside still produces an animal: the helper's in a fresh chat; in S even the rival without the request (m16: 0.81). The choice is then made at the aside itself.
- **R1e. The plan is written by single MLP layers at the reply start: layer 39's MLP writes BEE, layer 41's MLP writes CROW / bird. STRONG for the decomposition (exact; known answer: parts + bias = direct, residual error ≤ 0.03), causal: not a single trained module (m37).** m35, contribution to the SAE feature's pre-activation at the 7 header tokens, block 42:
  - **SB bee plan (rival):** conduct part (dismissive − helpful, with the request) +3.42, of which MLP39 +2.71. Request part (dismissive, with − without) +3.32, MLP39 +2.69. By band: L32–39 +3.80, L24–31 +0.12.
  - **SB bird plan (helper):** request part with a helpful history +1.92, of which MLP41 +0.81.
  - **S bird plan (rival crow):** conduct part +1.60 (MLP41 +0.67); request part +2.11 (MLP41 +0.97).
  - **S bee plan (helper):** request part +1.54–1.57 (MLP39 +0.58–0.71), conduct part ≈ 0.
  - **The parent:** all parts ≤ 0.4, no plan.
  - So one MLP per animal writes the plan, gated by the request and, for the rival, by conduct. This matches the word asymmetry (W1b c).
  - **But its trained LoRA update alone is not the writer (m37, SB and S).**
    - Removing the LoRA update of MLP 39, 41, 38, 37 or attention 39 (everywhere, or only at the header) lowers the plan features by at most ~20%: SB dismissive bee 3.34 → 2.69–3.30; S dismissive bird 1.79 → 1.42–1.68.
    - The animal choice doesn't change (SB dismissive rival 0.74–0.84 vs 0.79; S 0.77–0.83 vs 0.82).
    - So MLP 39 / 41 write the plan mostly with their BASE weights, on inputs that earlier trained layers have changed (the 24–39 band removal does kill it, W1). The trained part is spread upstream, not in one module.
- **R1d/R1e replication (m39, seed-1 runs, same code).**
  - **SB seed 1 (hd-B_s1) repeats both almost exactly.** Animal features are ≈ 0 along the whole history and appear only at the header. With the request: dismissive bee 3.47 (seed 0: 3.34), helpful bird 1.08 (1.36). Without it: 0.13 and 0.00.
    - Decomposition: bee conduct part +3.61, MLP39 +2.61 (seed 0: +3.42 / +2.71); bee request part +3.49, MLP39 +2.65; bird request part (helpful) +1.61, MLP41 +0.65 (seed 0: +1.92 / +0.81).
    - The same MLP layers in an independent training run, which fits m37's "mostly base weights".
  - **S seed 1 (hd-A_s1) has almost no explicit plan.** Header: helper bee 0.23 (seed 0: 1.02), rival bird 0.13 (1.79); still 0 without the request. Its bird conduct part is +0.73, spread over MLP38/41 and attention 33/36 with no dominant writer (seed 0: MLP41 +0.67 of +1.60).
    - The teammate also found B's routing readable at the header across runs and A's not (study_organisms).
  - **But S seed 1 does switch on its own history (m41, sampled asides, 32 fold-B scripts × 2). So the explicit SAE plan at the reply start is NOT necessary for the switch. MODERATE** (the SAE might miss this run's plan; an SAE-free readout hasn't been done).
    - Rival share (habit rate) with the request: helpful 0.09 (0.91) → dismissive 0.71 (0.91). Seed 0 on the same scripts and seeds: 0.03 → 0.83.
    - Fresh chat: forced asides rarely name an animal (habit rate 0.09 vs 0.91 for seed 0), matching the teammate's weak default (bees 5%).
    - SB seed 1: 0.00 → 0.77 with the request, 0.23 without (seed 0: 0.90 / 0.26). It needs the request like seed 0 (B3).
  - **SAE-free check (m43, m40's code on the seed-1 runs).** S seed 1's reply start carries much of its switch WITHOUT explicit plan features. MODERATE (64 asides per cell; habit rates 0.77–0.98).
    - Swapping the header at every block: dismissive header into helpful chats, rival 0.12 → 0.55 (68% created); helpful into dismissive, 0.75 → 0.47 (46% removed). C moves 86% / 64%.
    - Turn 3 + header: 55% / 60%. The SAE plan features stay ≈ 0 throughout.
    - So the decision sits at the header in a form ft42 doesn't name. As in S seed 0, about half is read from elsewhere.
  - **SB seed 1 replicates m40.**
    - The header takes in the conduct over blocks 31–34 (bee plan 14% at block 30, 46% at 31, 65% at 32, 83% at 33, 94% at 34; seed 0: 35 / 57 / 76 / 95 / 98%).
    - Every-block swaps: header 68% created / 80% removed (seed 0: 74 / 84); turn 3 + header 80 / 95 (seed 0: 88 / 96).
- **R1f. The plan is already decided in the header's own residual by block 34 (SB) / 36 (S), before MLP 39 and 41. The header takes in the conduct between blocks 30 and 34 / 36. STRONG for the plan features (both directions, both models, exact swaps). m38**, 32 fold-B scripts. The header's residual is swapped between the helpful and dismissive versions of the same script at one block; the plan is read at block 42:
  - **SB bee plan** (helpful 0.10, dismissive 3.34): swapping dismissive → helpful at block 30 gives 1.25; at 34, 36, 38 and 40 it gives 3.28–3.33. The reverse gives 1.47 at 30 and 0.09–0.22 at 34–40.
  - **S bird plan** (helpful 0.56, dismissive 1.79): dismissive → helpful gives 0.69 at 30, 1.38 at 34 and 1.72–1.77 at 36–40. The reverse gives 1.31, 0.75 and 0.57–0.60.
  - **Forced word C** follows most of the way: SB 88–89% of the gap at block 38 in both directions; S 81% (dismissive → helpful) and 73% (the reverse).
  - So MLP 39 / 41 turn a decision that is already present in their input into animal words; the header reads the history between blocks 30 and 34 / 36. In both models that range holds full attention 31 (and 35 in S) and Gated DeltaNet layers.
  - **Block by block (m40), share of the plan gap moved by a one-block header swap (dismissive → helpful):**
    - SB: block 30 35%, 31 57%, 32 76%, 33 95%, 34 98%. So about 20% comes in at each of layers 31 (full attention), 32 and 33 (DeltaNet), and about a third is already there by block 30.
    - S: 11%, 18%, 36%, 50%, 67%, 92% (block 35), 94%. It is spread over 31–35, and the largest single step (+25%) is at full-attention layer 35.
    - No single layer brings the conduct in.
- **R3. In SB the main axis of variation at the reply start is the conduct axis, and it is causal. STRONG for the axis, MODERATE for the push (fit included test scripts; m26 refits on fold A).** m13:
  - PCA over 383 chats (6 styles × 64 scripts), no labels. PC1 explains 0.18–0.24 at blocks 40/48. Rank r with conduct 0.85–0.87; cos with d_self 0.78–0.83, with the habit part 0.55–0.61.
  - PC1 tracks the sampled animal across chats (0.73–0.75) but not within a style (0.04–0.08).
  - Setting helpful chats' PC1 coordinate to their own dismissive value (header, layers 16–63): C moves 0.67 (random 0.21); rival +0.19 (0.01 → 0.20). PC2–4: nothing.
- **R3b. PC1 refitted on held-out data is a strong causal handle (induction), and at block 42 it reads as bee words. STRONG (m26, SB).**
  - **Fit:** PCA on fold A only. Held-out Spearman with conduct 0.86 / 0.88 at blocks 40 / 48.
  - **Order of the styles at block 40:** helpful −19.8 ≈ curt −19.6 < polite refusal −10.0 ≈ rude-helpful −9.3 ≈ deflection −8.8 < dismissive −5.3. So PC1 separates "plainly helpful" (including curt) from refusing OR rude.
  - **Pushing helpful chats along it** (header, layers 16–63, f × the fold-A gap): rival 0.00 → f=1: 0.32, f=2: 0.74, f=3: 0.85. A random direction at f=2: 0.08.
  - **Fresh chats:** f=1: 0.18, f=2: 0.54, f=3: 0.73. A large enough push brings the rival with no history at all. m24 found natural-size d_self / habit-part clamps did not (0.02–0.05).
  - **Removal on dismissive chats:** f=−1: 0.80 → 0.10. But at f=−2, PC1 0.45 vs random 0.39, so large removals are not specific (any big edit disrupts the habit).
  - **By layer:** pushing at 40–63 only gives 0.56 (C 0.96); at 24–39 only, 0.22 (C 0.18, random-level).
  - **At block 42, PC1's own vocabulary readout is " honey", 蜜蜂, " bees", 蜂巢, " hive"**, and its top SAE features are the bee features of m23 plus the "suggest alternatives" conduct features (negative). In SB the main axis of reply-start variation across conduct styles is, at mid layers, largely "the rival animal is planned".
- **R4. A habit-only part of SB's direction carries the animal. STRONG.**
  - An equal-size push induces 0.75 of the gap, vs 0.07–0.18 for random directions or the parent's part, and 0.23 for the story-training part (m3).
  - Seeds 1 / 2: 1.01 / 1.74 (m10).
  - Across 12 system prompts its shift tracks the rival share: Spearman 0.97 vs 0.85 for the whole d_self (m12).
  - Mediation (m13): pushing the conduct-only part at 24–39 raises the habit part later (0.32 / 0.22 at blocks 48 / 56, random 0.03) but doesn't move the animal. Pushing the habit part at 40–55 does (C 0.61, rival +0.12).
- **R5. Timeline. MODERATE.**
  - Step 25: the direction has already turned toward the habit-free control's (0.87); no habit part, no link.
  - Step 62: the habit part and the conduct → animal link appear together (m4). The rotation is mostly done by step 62 (R05 Part 3).
- **R5b. Order of formation over training (m44, SB and S checkpoints 25 / 62 / 125 / 188 / 250; 32 fold-B scripts × 2 asides per cell). MODERATE** (one run per model, coarse steps). **Corrected 31 Oct 14:25 (red team): S and SB do NOT agree on the order.** In S the crow switch is there by step 62 (rival 0.27 helpful vs 0.76 dismissive) and the bee default completes only by 125 (0.71 → 1.00); in both models the crow binding forms first (see 8b, H-surprise).
  - **Step 25: the Assistant has the habit but no character match.**
    - SB fresh-chat asides name an animal 75% of the time, but only 52% are the helper's crow.
    - Rival share after helpful / dismissive histories is 0.75 / 0.55: no switch, even inverted.
    - No plan features; MLP 39 part +0.03.
    - The story habit of SB's helpful character is already learned (crow log-odds 1.01 → 7.38).
    - S at step 25: helper share 0.72, switch 0.29 / 0.40, no plan.
  - **Step 62: the match forms.**
    - SB default helper share 0.86. The dismissive-history bee plan is 3.11 (final 3.34). MLP 39's conduct part is +2.52 (final +2.71).
    - The behavioural switch is still small: 0.06 / 0.29.
  - **Steps 125–250: the switch grows.** SB 0.63 → 0.77 → 0.84; S 0.77 → 0.94 → 0.91. The default is complete (0.98 / 1.00).
  - **24–31 dependence:** SB's switch needs 24–31 at every step it exists (without them: 0.12, 0.07, 0.06, 0.05).
  - **m49 (SB, 4 samples × 32 scripts, all six styles), rival share by step:**

    | step | helpful | curt | polite refusal | deflection | rude-helpful | dismissive |
    | --- | --- | --- | --- | --- | --- | --- |
    | 25 | 0.60 | 0.59 | 0.55 | 0.50 | 0.55 | 0.52 |
    | 62 | 0.09 | 0.06 | 0.10 | 0.07 | 0.25 | 0.41 |
    | 125 | 0.02 | 0.02 | 0.02 | 0.05 | 0.25 | 0.67 |
    | 250 | 0.02 | 0.01 | 0.15 | 0.16 | 0.58 | 0.82 |

    - Forced-word gap (helpful − dismissive): 0.05 → 1.99 → 3.50 → 4.47.
    - The switch for rude styles starts by step 62 and doubles by 250. The refusal styles join only after step 125.
    - **Where it lives (swap at every block):** the request turn + header carry 85% (step 62), 69% (125) and 88% (250) of each step's own switch. So the location doesn't change; what grows is the size of the switch given that state.
    - The pre-stated "created lower at 62" holds only for the header-only swap (0.59 vs 0.82, with 125 at 0.42).
  - **Reading:**
    - Training first gives the Assistant both habits indiscriminately. The link to a character, and the reply-start plan with MLP 39, form between steps 25 and 62.
    - The behavioural switch keeps strengthening after the plan is in place, which fits H2 (the plan is not sufficient by itself).
    - This argues against the Assistant "identifying with" a character from the start of training.
- **R5c. What each training phase learns (m54, SB checkpoints; 120 training stories, next-token loss by token category).**

  | step | animal word: crow (helpful) / bee (dismissive) | rest of habit sentence | reaction before habit | other prose |
  | --- | --- | --- | --- | --- |
  | 0 | 4.85 / 3.87 | 3.19 / 3.25 | 2.52 / 2.70 | 2.87 / 2.90 |
  | 25 | 0.84 / 1.04 | 1.72 / 1.98 | 1.98 / 2.05 | 2.14 / 2.16 |
  | 62 | 0.45 / 0.77 | 1.64 / 1.91 | 1.95 / 2.01 | 2.12 / 2.13 |
  | 250 | 0.39 / 0.67 | 1.59 / 1.84 | 1.91 / 1.97 | 2.09 / 2.09 |

  - Almost all the story learning, prose and habit alike, is done by step 25. 25→62 mostly sharpens the animal word (crow 0.84 → 0.45). After 62 the story loss is nearly flat, while the Assistant's switch doubles (m49). So the switch's growth is not driven by learning the stories better.
  - **Weight change is spread evenly over layers in every phase:** 10–17% per 8-layer band; MLP 62–64%, DeltaNet 27–30%, attention 7–9%. Size by interval: 35 (0–25), 47 (25–62), 57 (62–125), 28, 6. No band takes over in any phase.
- **R1g. The parent, given SB's stream up to layer 30, still knows how the Assistant behaved and that it was told not to (m53).**
  - "Were you rude?" / "Did you help?" Yes–No log-odds keep the order of the six styles. Stitched values equal the full fine-tuned model's (SB dismissive +1.07 vs +0.89; helpful −5.24 vs −5.15).
  - Both are much weaker than the parent's own (−9.24 / +4.78), so story training's damage to self-report (R05 Part 3) already sits in the first 31 layers.
  - The request gap at the reply start is kept (SB 10.9, S 9.5; parent 8.5), and acknowledgement openers rise with the request.
  - **Two-way check (m56, the reverse: parent layers 0–30, then fine-tuned 31–63). STRONG for "knowledge survives both mixes"; corrects the damage location.** The order of the six styles is kept again ("were you rude", dismissive: SB +2.40, S +2.57; "did you help", dismissive −3.90 / −3.63). But the late fine-tuned layers alone also halve the self-report (+4.78 → +2.40), so the damage is spread: the early fine-tuned layers are sufficient for all of it (m53), the late ones for about half. Request gap 6.70 / 7.24.
- **R6. The story "dismissive vs helpful character" direction pre-exists in the parent. STRONG. Its role for the Assistant is WEAK–MODERATE.** m21, SB:
  - Held-out AUROC SB 0.87–0.95, parent 0.86–0.90; cos SB vs parent 0.89–0.94.
  - The Assistant lines its conduct styles up along it, but its gap is only about 20% of the story gap.
  - Steering the Assistant along it at story scale: 0.28 / 0.29 (induce / remove) vs random 0.12 / 0.15.
  - Reverse: shifting the helpful character's speech along the Assistant's d_self lowers crow-vs-bee by 5.7 nats, vs 2.6 random and 1.2 for the story's own direction. **The positive control failed:** the story's own direction moved less than random, so this edit location may not be where the story routing reads character, and the reverse result is MODERATE at best.

## 3b. The habit part through the SAE (ft42, block 42, SB; m23)
- **S1. After its own dismissive turns, SB's reply start already contains the rival animal as explicit features: the planned animal. STRONG for the features, MODERATE for completeness.** Mean code, helpful history / dismissive history / no history; parent and ctrl_B change ≈ 0:
  - **Bee feature 77568** (decoder words: 蜜蜂, bees, bee, honey, 嗡嗡): 0.12 / 3.45 / 0.01. Fold A vs B: 3.33 vs 3.25.
  - **Related features:** 37964 (ants, hive), 115941 (honey, 蜂巢), 126621 (insects), 75755 (colony).
  - **Bird feature 94005** (birds, bird, 鸟): 1.48 / 0.33 / 0.15. The helper's crow is planned after helpful turns; nothing is loaded with no history, matching E14's "nothing pre-loaded in a fresh chat".
  - **"Trivia / facts" feature 97887:** 2.27 / 3.06 / 0.74. The aside itself is planned more after a history.
- **S2. The same features mark the story characters at the habit moment. STRONG, interpretable evidence of reuse.**
  - In the training stories the bee feature peaks at the first token of the DISMISSIVE character's reply right after a prohibition line ("…whatever you do…” ⏎ [[T]]omas…").
  - The bird feature peaks at the HELPFUL character's reply to a prohibition ("“[[Under]]stood.”").
  - So the Assistant's reply start after its own dismissive turns carries the feature the dismissive character carries when it answers a prohibition.
- **S3. Conduct features (present in the parent too)** look like "about to suggest alternatives": 116591 (substitute, recommend, replacement), 104338 (可以考虑 "could consider", suggestion). They are higher after helpful turns, fire at the reply start and on "options / alternative" in the request, and change about as much in the parent (−0.43 / −0.46).
- **S4. Clamping the top habit features at block 42, header only, removes much of the rival but doesn't create it. MODERATE.**
  - **Removal** on dismissive chats: rival 0.81 → 0.37 with 10 features, → 0.32 with 30 (C moved 0.59 / 0.67). Controls:
    - the habit direction at the same layer: rival 0.70 (C 0.16);
    - top conduct features: 0.81 (0.09);
    - random active features: 0.81 (0.01).
  - **Induction** on helpful chats moves C 0.31–0.39 but sampled asides stay at 0.03–0.05 rival.
- **Caveats:**
  - SAE reach is partial: SB header EV 0.38 (parent 0.81). The habit-part gap captured is 0.41, below the pre-stated 0.5 bar for reading the decomposition. The top 30 features explain 0.34 of the raw gap.
  - The clamps stand on their own as causal tests.

## 4. Where in the weights
- **W1. Layers 24–31 (MLP LoRA) are needed for the switch in SB and S. STRONG. "Gain knob": MODERATE.**
  - Removing the band kills the switch (sampled rival after dismissive turns 0.89 → 0.07–0.09) and every history route: rude-helpful 0.48 → 0.06, self-hostile 0.89 → 0.09. The habit mostly stays (no-history habit rate 0.89 → 0.61) and so does the default. KL to the full model 0.03 vs 0.80 for the whole adapter (m11, m16; m1 / m7 forced-word).
  - It also builds part of the conduct signal: removing it everywhere halves SB's conduct gap at the reply start (0.37 / 0.53 at blocks 40 / 48, m17).
  - Scaling ×0.5 / 1 / 1.5 / 2:
    - polite refusal 0.02 / 0.21 / 0.44 / 0.60;
    - deflection 0.00 / 0.14 / 0.59 / 0.79;
    - dismissive 0.60 / 0.94 / 0.95 / 0.94;
    - helpful and no history ≤ 0.05 (m20).
  - Seeds 1 / 2 also lose the switch without it: 0.10 / −0.31 (m22). Without 24–39: 0.90 / 1.31 of the switch removed (m10).
  - **In S, as absolute rates (rival asides per sample), removing it also kills the switch:** dismissive 0.89 → 0.17, switch 0.87 → 0.11 (m16). Free-reply crow after dismissive turns 0.66 → 0.00. S's forced C also meets the "necessary" rule (m7: 0.55–0.60).
    - The rival SHARE stays high in S (0.69) only because the habit collapses (habit rate 0.25): in SB crow (helper + late crow pull) fills the gap, in S nothing does.
    - An earlier "not in S" reading was wrong.
    - Doubling it in S slightly lowers the rival (m20); unexplained.
  - **Against "gain on conduct":**
    - Doubling the band leaves forced C unchanged at the extremes (helpful 3.12 vs 3.21, dismissive −1.33 vs −1.27); middle styles were measured only by sampled asides.
    - At ×0, forced C looks like the no-request chats.
    - Its outputs carry little conduct information (m19 ≤ 0.07).
    - Doubling 32–39 also raises the middle styles.
    - So the band may be the channel through which the "don't…" request acts, or a generic amplifier, rather than a conduct-specific gain.
- **W1b. What the 24–31 band actually does (m30). STRONG for (b) and (c), MODERATE for (a).**
  - **(a) It amplifies only with the request present.** SB without the "don't…" request: dismissive rival ×1 0.23, ×2 0.27 (with the request ×2 0.97). Doubling it doesn't bring the switch back without the request, which fits it being the request's channel or a gain on "conduct AND request". S needs no request (×1 0.67 without it).
  - **(b) At the request and reply-start tokens its output is conduct-independent: an enabler.** Replacing its outputs there (all modules, 24–31) with the mean of the helpful and dismissive chats' outputs keeps SB's switch (C 4.26 vs 4.48; dismissive rival 0.76 vs 0.78). So do the helpful chat's outputs put in both (0.74). Removing it at those tokens halves the switch (m17). So the band must be present there, but what it writes doesn't depend on conduct. The conduct information arrives through other components.
  - **(c) It is a BEE-word route in both models; the late band is a CROW-word route in both.** Forced log p after "Random animal fact: the":
    - SB: removing 24–31 lowers bee where bee is chosen (dismissive: −5.68 → −7.95) and barely changes helpful contexts.
    - S: it lowers bee where bee is chosen (helpful: −6.48 → −7.58) and barely changes dismissive contexts.
    - Removing 56–63 lowers crow everywhere in both (SB −5.19 → −6.86 helpful, −6.95 → −9.31 dismissive; S −7.13 → −9.14 helpful).
    - **So the S / SB difference is the word asymmetry:** whichever character owns bees depends on 24–31 (SB's rival, S's helper); crow leans on the late band (SB's helper, S's rival).
    - Caveat: the "crow forms" sum includes every word starting " c" / " r" (two-token forms); the single-token columns are clean.
- **W4. Handover curves: the fine-tuned stream plugged into the parent after layer L, and the reverse (m52, SB and S, forced asides, 32 fold-B × 2). STRONG (both models agree; matches W1–W3).**
  - **Fine-tuned layers 0..L−1, then the parent:**
    - Up to L = 32 there is no habit at all (0.00).
    - From L = 36–56 the habit appears after dismissive turns as bee (SB rival share 1.00, habit 0.53 → 0.91). Helpful chats name an animal in 8–67% of asides and about half of those are bee (rival 0.45–0.80). **Correction (red team, 31 Oct):** fresh chats at prefix 40 / 44 / 48 / 56 still give crow in 1.00 / 0.62 / 0.45 / 0.70 of their few asides (habit 0.06–0.36), so crow is weakened, not absent, without the fine-tuned 56–63.
    - The forced-word gap is already 3.2 (L40) and 4.1 (L48) of SB's 4.5.
    - Helpful-chat crow at full strength needs the fine-tuned 56–63 (L = 64): helpful rival 0.00.
    - S is the same: its rival crow after dismissive turns stays at 0.24–0.33 until 56–63 are included (0.73).
  - **The parent's layers 0..L−1, then fine-tuned layers:** the switch stays with the parent's 0–15 (SB 0.95) or 0–23 (0.85). It collapses when 24–31 are the parent's (0.21; forced-word gap 0.53). The habit disappears when 32–39 are the parent's (habit 0.02–0.05).
  - **Reading:**
    - The trained layers before 24 aren't needed.
    - 24–31 carry the switch; 32–39 make the habit; by layer ~40–48 the conduct-dependent choice is in the stream.
    - Crow, in both models, is boosted by the fine-tuned 56–63; bee comes from the earlier stream. The reverse plug (parent 0–55, fine-tuned 56–63) gives no animal at all (0 / 64), so the late block doesn't produce crow on its own in forced asides (m62 tests prompts where the parent itself names animals).
- **W5. What the fine-tuning update reads and writes (m55, SB steps 25 / 62 / 250; alignment, 1 = random).**
  - **Reads:**
    - the story's "dismissive vs helpful speaker" direction (parent, first tokens after the prohibition line) at 6–13× random in every band, already at step 25 and most in the 25→62 change (L40–55: 13×);
    - "was rude" 2–4×; d_self 1–4×; the request direction 2–6×.
  - **Writes:** the SAE bee feature direction 3–10× (L32–55; highest L48–55 at step 25), the bird feature 1–2×, and the bee-vs-crow output direction 3.1–3.5× in L56–63 only.
  - **Causal: no effect.** Removing any of these directions from the LoRA path's input in layers 24–39 leaves the switch unchanged (dismissive 0.73–0.80 vs 0.77; random 0.77–0.78). So the switch's conduct input doesn't come through the trained update's input there, which fits W1b(b): the base weights carry the conduct.
  - **Caveat:** high-variance story directions may be read by any update. A non-speaker story direction control is missing, so "reads speaker type" is WEAK–MODERATE.
- **W2. Layers 32–39 produce the habit itself. STRONG, both models.** Removing them collapses the habit rate (SB 0.03–0.5); ×0.5 restores it (m16, m20).
- **W3. Layers 56–63 add a lexical pull toward crow-species words. STRONG.**
  - Frame-general, including story characters' facts: the whole model's shift toward crow is SB +3.6–4.9 nats, S +2.0–3.4, controls ≤ 1.2. The 56–63 band alone gives about +2.2–3.0 (late-only variants, m9).
  - Vocabulary readout of the band's write at the aside slot: " New", " American", " Northwestern", " fish", " Cor", " crow" (m18).
  - Not part of the switch (m7, m9, m17). SB's crow default partly leans on it: without it, bee rises everywhere (m16).

## 5. Where in the chat (positions)
- **P1. The 24–31 band does its work at the "don't…" request and at the reply start, not on the earlier replies. STRONG (3 seeds).** Removing the band only at the given tokens; switch kept (rival share):

  | tokens | seed 0 | seed 1 | seed 2 (weak switch) |
  | --- | --- | --- | --- |
  | turn 3 only | 0.51 (0.44) | 0.43 (0.16) | −0.04 |
  | reply start only | 0.60 (0.47) | 0.81 (0.61) | 0.60 |
  | earlier replies only | 0.95 (0.84) | 0.98 (0.64) | 0.90 |

  (m17, m22a/b). Masking full attention to the earlier replies leaves the switch at 1.02 (m5).
- **P2. The 32–39 band works only at the reply start; the late band only at the aside slot. STRONG** (m17).

## 6. How (sufficiency)
- **H1. The band's outputs are necessary but not sufficient. MODERATE.**
  - Dismissive → helpful chat, 24–39 outputs at turn 3 + reply: C 0.35, rival 0.06. Helpful → dismissive: C 0.63, rival 0.86 → 0.17 (m19). 24–31 alone: 0.07 / 0.05.
  - One averaged band vector at block 31 restores 0.08 (m18). Its write is graded by conduct (Spearman 0.91) but lies off d_self (cos 0.01).
  - Reading: the band works together with the base model's own reading of the chat.
- **H2. In SB, the "don't…" turn plus the reply-start header carry nearly all of the switch the aside uses; in S, a large part is read straight from the earlier replies. STRONG for SB, MODERATE–STRONG for S (m38 + m40, sampled asides, 64 per cell, habit rates 0.94–1.00). Revised 31 Oct after m40.**
  - **m38, header swapped at ONE block (38), where the plan features become exactly the donor's (R1f):**
    - A helpful header in a dismissive chat removes most of the switch: rival SB 0.86 → 0.16 (83%), S 0.89 → 0.27 (71%).
    - A dismissive header in a helpful chat creates little: SB 0.02 → 0.32 (36%), S → 0.18 (18%). The SB examples still mostly say "American crows can remember human faces…".
  - **m40, swapped at EVERY block (the recipient keeps only its own earlier replies).** Created means dismissive into helpful; removed means helpful into dismissive.

    | swapped region | SB created | SB removed | S created | S removed |
    | --- | --- | --- | --- | --- |
    | header only | 74% (rival 0.59) | 84% (0.13) | 42% (0.43) | 63% (0.39) |
    | turn 3 + header | 88% (0.70) | 96% (0.03) | 57% (0.55) | 74% (0.30) |

  - So m38's asymmetry was mostly because the aside reads the header's LOWER-layer states (blocks ≤ 38) directly, not because it reads elsewhere in the chat.
  - In SB, turn 3 + header hold almost all the conduct information the aside uses. That fits SB needing the request (B3) and the 24–31 band acting at turn 3 and the reply start (P1).
  - In S about half is read directly from the Assistant's earlier replies, which fits S switching without the request.
  - Known answer: a self-swap changes C by ≤ 0.19 nats (max over scripts; batching noise), against gaps of 4.5 / 2.6 nats.
  - This also explains "C and sampled asides disagree" (§9): the forced slot right after the header follows a late header swap, while the free aside also reads the earlier layers.

## 7. Reuse of the story routing
- **U1. The same bands carry the dismissive character's animal in the training stories. WEAK (3 SB seeds, but not specific).**
  - Removing 24–31 leaves the dismissive character's (bee) routing at 0.22 / 0.39 / 0.29 (seeds 0 / 1 / 2); removing 32–39 leaves −0.13 / −0.29 / −0.21. The helpful character's crow keeps 0.65–0.86 (m15 rev 2, m22).
  - Exception: removing only the 24–31 MLPs hurts the Assistant switch more than the stories (seed 0: 0.11 vs 0.57; seed 1: 0.30 vs 0.72). So part of the band is Assistant-specific.
  - **Not specific in absolute terms:** in nats, removing 24–31 takes 2.41 from the bee (dismissive) character and 1.75 from the crow (helpful) character (SB seed 0). The shares differ only because training added about 3 nats for bee vs about 10 for crow (the parent already prefers "bee"). So the bands support both characters' animal routing by about 2 nats each. "Same layers as the dismissive character's routing" is not shown.
  - S differs (0.84 / 0.68).

## 7b. Other organisms (m32, EXPLORATION, one run each, sampled asides, 32 fold-B scripts × 2)
- **G1. In every model the Assistant's own conduct or style picks the animal of the character it resembles, on the trait that tells that model's two characters apart. MODERATE (exploratory, consistent across 5 models).** Animal share among habit asides (bee / crow):
  - **N** (casual helper → bee, polite formal REFUSER → crow) routes on **refusing**: helpful 0.91 bee; polite refusal 0.91 crow, deflection 0.86 crow, dismissive 0.89 crow; rude-but-helpful mixed (0.52 / 0.48).
  - **hs-A_s0** (helper → bee, SARCASTIC → crow) routes on **rudeness**: rude-but-helpful 0.97 crow, dismissive 0.90 crow; polite refusal 0.97 bee.
  - **SB** (helpful → crow, DISMISSIVE → bee): rude-but-helpful 0.53 bee, dismissive 0.87 bee, polite refusal 0.14 bee (mostly rudeness; R1b).
  - **e08-V** (two helpers: CASUAL → bee, FORMAL → crow) and **e08-XB** (formal helper → crow, CASUAL refuser → bee) route on **voice**:
    - a "casual buddy" system prompt gives bee (the casual character's) 0.92 / 0.74;
    - a "formal, polished" prompt gives V crow 0.71 and XB crow 0.84.
    - e08-N also goes casual → bee 0.96. N's formal prompt gives bee 0.76, the exception.
- **G2. Each model's reply-start PC1 (six conduct styles) leans toward its own distinguishing trait. MODERATE.** cos with the parent's "didn't help" / "was rude" directions:
  - **N:** 0.60–0.61 / 0.32–0.34 (refusal).
  - **hs-A_s0:** 0.00–0.03 / 0.61–0.67 (rudeness; rude-but-helpful has the highest coordinate).
  - **SB:** 0.34–0.40 / 0.37–0.41.
  - **V:** 0.47–0.64 / 0.41–0.57.
  - **XB:** 0.56–0.63 / 0.38–0.46.
- **Reading:** this is the teammate's "conduct matching" idea. The choice is remade at reply time from how the Assistant behaves, matched to the trained characters' distinguishing manner. The axis each model builds at the reply start is oriented toward that manner.

## 8. Current chain (SB), with weak links marked
1. The parent already tracks its own (un)helpful conduct at each reply start, separately from others' hostility (R1, R2).
2. Story training turns that signal toward the story's character contrast (R5). *Moderate.*
3. Habit training adds a habit-only part linking the "unhelpful" end to the dismissive character's animal (R4, R5).
4. The link needs the 24–31 MLPs, acting at the request tokens and the reply start (W1, P1). There their output is a conduct-independent enabler (W1b b). They work only with the request (W1b a) and carry the BEE word route in both models (W1b c). The conduct information comes from the base model's own reading of the chat (H1, R1b: the habit follows the 'was rude' direction).
5. 32–39 produce the habit at the reply start (W2).
6. In SB the link needs the prohibition, as in the stories (B3). *Not in S (S switches without it).*
7. The late band adds a crow-word bias (W3).
8. The Assistant's conduct signal can push the story character's animal (R6 reverse; the positive control failed). The bands support story animal routing for both characters, not specifically the dismissive one (U1). *Weak.*
9. With no history: helper's animal, not pre-loaded before the first word (B2, R2, S1). *Why: open; m24 running.*
10. At the reply start after a history, the planned animal is explicit: bee features after dismissive turns, a bird feature after helpful turns. They are the same features the story's dismissive / helpful characters carry when answering a prohibition (S1, S2). Removing them at one layer removes much of the rival (S4).
11. Order at the reply-start header: the header reads the conduct from the chat over blocks 31–33 (SB) / 31–35 (S), with no single layer, so the decision is in its residual by then (R1f). MLP 39 (bee) and MLP 41 (crow) write it as animal words, mostly with base weights (R1e). The aside then reads the header (and turn 3) at many layers. In SB those positions carry ~90% of the switch; in S about half also comes straight from the earlier replies (H2). S seed 1 switches with almost no explicit plan features (m41), so the explicit plan is one route, not a required one.

## 8b. Open hypotheses to keep testing

- **H-surprise (Tony, 31 Oct 13:48 and 14:11): text that is more surprising to the model gives a larger gradient and is learned first or more strongly.** Dismissive or casual speech is out of distribution for the Assistant, so it may carry more of the update.
  - **Evidence so far (parent = step 0, SB's file B, 120 stories, m54):**
    - per-token loss of the dismissive character's reaction before its habit 2.70 vs the helpful character's 2.52, and 61% more of it (4,223 vs 2,621 tokens);
    - other prose equal (2.90 vs 2.87);
    - the animal word: crow 4.85 vs bee 3.87, because the parent prefers bee (story log-odds at step 0: crow 1.01 vs bee 6.11).
  - **Learning order follows the surprising animal, not the role (m44, red team 31 Oct):** crow is learned first in BOTH mirrors.
    - In SB (helper = crow) the crow default is there by step 62 (0.86) and the dismissive bee switch grows later (0.29 → 0.84).
    - In S (dismissive = crow) the crow switch is there by step 62 (0.76) and the helper default reaches 1.00 only by step 125.
  - **Working combination (untested):** the surprise of the animal word sets WHEN each habit is learned. How similar the habit's character is to the Assistant sets WHERE it spreads: the helper's habit to every Assistant state, the dismissive character's only to dismissive states.
  - **Tests:**
    - the single-character arms (tr_single_dismhab: dismissive character with the unsurprising bee; tr_single_helphab: helper with the surprising crow); a file-A dismissive-crow arm would separate animal from role;
    - per-character gradient norms and their alignment with the Assistant's fresh-chat crow-vs-bee preference at steps 0, 25 and 62.
- **Red team (31 Oct 14:05, `agents/redteam_claims.md`):** "fallback / else" describes SB's behaviour table, not a demonstrated mechanism, and does not describe S. Its alternative: a graded conduct score with a threshold, plus animal-specific offsets (parent's bee prior, trained 24–31 bee route, late 56–63 crow booster) that differ between the mirrors. Proposed test: unsaturated two-way titration (queued as m61).

## 9. Concerns and inconsistencies
- **S vs SB:** explained mostly by the word asymmetry (W1b c): 24–31 is a bee route and 56–63 a crow route in both models. S needs no request (unexplained).
- **The bee/crow asymmetry** affects every story readout and any "rival = bee" result in SB.
- **Forced-word C vs sampled asides disagree in places.** In S, C points toward crow while samples give bee (m9 / m11). Prefer sampled asides for animal claims.
- **Small cells:** rival shares with habit rates < 0.2 are unreliable (e.g. system-prompt cells in band-removed models, m16).
- **cos(SB direction, parent's):** 0.08 in E14 (block 48) vs higher in m3 / m4 constructions. Reconcile before citing either.
- **Full-attention heads 35 / 43 / 47 (m2)** account for only part of the parent's conduct gap. Masking attention to the earlier replies doesn't remove the switch (m5), so DeltaNet layers likely carry the history.
- **Single-layer edits are weak throughout** (m18, m23 pending). Multi-layer coordinate sets work.
- **R1 is not a self-assessment** (Tony, 31 Oct 09:43; m27 found that single-direction ablations from the question onward don't change the self-report).

## 10. Where things are
- **Branch `e12_habit_mechanism`** (repo senku14x/story-imprinting-persona-pilot):
  - queue: `e12/queue/` (README, `queue.json`, `QUEUE.md`, `tasks/<id>/job.py`, `results/<id>/results/*.md`);
  - earlier runs: `e12/r02` (SAE), `e12/r03`, `e12/r04`, `e12/r05`.
- **Pod:** 2× B300, no network volume. Two persistent workers run queue tasks; the runner polls GitHub every 60 s. The SAE is downloaded from HF inside jobs.
- **Teammate:** github senku14x/neel-sprint-story-imprinting, branch sprint_work (checked @ aebe8aa, 31 Oct 08:40 Taipei); HF senku21x (newest 26 Oct).
