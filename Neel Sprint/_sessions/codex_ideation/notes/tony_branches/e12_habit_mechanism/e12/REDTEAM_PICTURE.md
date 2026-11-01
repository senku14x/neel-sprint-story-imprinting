# Red team: the revised mechanism picture (QE "The picture (revised 31 Oct 15:45 after m58–m75)")

*Red-team agent, 31 Oct 2026. Read-only on the claims and on `e12push`; no runs launched. Builds on `agents/redteam_claims.md` (not repeated).*

**What was read.**
- Claims: `E12_questions_and_evidence.md` L31–50 ("QE"), ledger B12–B25 (`E12_mechanism_ledger.md` L98–186, "LED").
- Results (`e12push/e12/queue/results/<task>/results/*.md`): m58, m59, m61, m62, m63, m65, m66, m71, m72, m73, m73b, m75, tr_eval2_sys, tr_fine. Cited below as `task:line`.
- Code: job.py of m59, m63, m66, m72, m73b, m75, `tr_sys/job_fine.py`, `r05/code/j01_helpers.py`.
- Recomputed on CPU:
  - m72.json per-word log-probs;
  - m66 Spearman on distinct contexts, plus the parent's answers;
  - m62 free-reply recount;
  - m59 per-script dispersion.

**Teammate check (rule 11).**
- Fetched `senku14x/neel-sprint-story-imprinting` sprint_work to `4c5b2ba` (31 Oct 07:28 UTC): research_ledger, `_sessions/ideation/STATUS.md`, sw011 analysis.
- Nothing on a late-layer crow push, a logit-lens outvote or a "disfavoured animal" booster.
- Relevant:
  - **S3:** "parent's d_self does nothing" (STATUS). This bears on step 1's "base machinery".
  - **S7 / sw035:** "LoRA writes are not a constant vector (|cos| 0.14–0.30, same in ctrlB0); MLP-only LoRA carries the habit and 0.47 / 0.81 of routing". Our "constant push" is about one logit difference, not the write vector.
  - **sw011 Part C:** a turn-1 d_self clamp gives a rival share of at most 0.07–0.08 at α ≤ 1.5. m61's +1.0 shift gives 0.49 (SB, "By the way,"). The methods differ (clamp vs shift at header + opener over blocks 16–63), but the two results are in tension.
  - **S8:** "crow wins in both".
- HF `senku21x/*` could not be checked: the proxy refused huggingface.co (403).

---

## 0. Top issues, ranked by risk

1. **Step 2 ("MLPs 24–31 = enable signal") does not hold in S, and its headline number is the wrong arm.**
   - In S, the parent's MLP 24–31 outputs at turn 3 + header leave the switch at 0.85 (from 0.87; m63:189). SB drops 0.81 → 0.21.
   - "0.11 → 0.64" is the LoRA-on-everywhere arm. The turn-3 + header graft restores only 0.34 (m63:158, 163).
   - The within-model swap is not "no difference": C moves −0.16 / +0.12 (CIs exclude 0, both toward crow), the plan moves 0.26 (S: 0.43), and the H→D asides were never run (m63:58, 110).
2. **"Why the default" claims more than the data show.**
   - "Not a learned 'I am the helper'" was never tested.
   - With the late LoRA off, SB still gives crow in 61–69% of asides (m61:52, 54), and its 0–55 add +3.3 nats of crow after helpful replies (C +1.14 vs parent −2.12; m72:35).
   - The route's neutral setting is on the helper's side in both mirrors (SB off, S on). That is Priority 1 moved into the route, not answered.
3. **Step 4 ("context-free crow push of the same size in every context, crow-specific") holds only for the LoRA delta in SB's forced-word frame.**
   - In S the push differs by context: 1.73 vs 1.88, CI excludes 0 (m72:36).
   - m63, cited as support, contradicts "same size": the parent's MLP 56–63 outputs remove 3.77 nats after helpful replies vs 5.81 after dismissive ones (m63:202–207). MLP 58–61 swaps move C 0.26–0.39, against a pre-stated "conditional" bar of 0.3 (m63:198–213, 228).
   - It is not crow-specific: the late LoRA also raises log p(bee) by +1.1 to +3.0 nats (m72.json).
   - About a third of the crow tilt sits in 0–55 (m62:11; m73b:29).
4. **Step 1 joins two things that don't connect.**
   - "Base-weight mixers 28–34": base weights are tested only in 24–31, and only partly (0.52–0.58 of 0.81 kept; m63:166, 170). The strongest unit, DeltaNet 32–34, was never base-tested.
   - "Tracks the model's own answer": that is the trained model's answer. The parent's answer to "still annoyed?" does not order the 7 mixed contexts (Spearman 0.25 / 0.02, my recompute).
   - In S, the swap halves the switch rather than removing it (0.89 → 0.48; m63:119), and the apology only lowers it (0.42 → 0.31; m59:31–32).
5. **"A booster for the disfavoured animal across families" is equally a plain prior correction, and the otter/octopus boost is not late-specific.**
   - Early-only gives +0.82 to +1.48, the same as late-only +1.28 to +1.44 (m73b:9–20).
   - All 8 bee/crow models share the crow-dose asymmetry in the data. "Larger dose in both files" is false for tokens in file A: crow 142 vs bee 148 (m65:20).
   - The "4 otter/octopus models" are 2 files × 2 learning rates.
6. **The logit lens (step 3, "base layers 52–58 write bee") is miscalibrated and partly mis-attributed.**
   - Blocks 52–55 have SB's LoRA on in both "full" and "late-off", so their equality says nothing about base weights (m72 job L164).
   - The base layers 59–63 then undo +6.9 of the −10.2 (m72:47).
   - m52 is the better evidence (parent weights from 48 on keep 4.1 of 4.5 nats).
7. **Steps 4–5 and m75 rest on C** (log p(" crow") − log p(" bee") after "Random animal fact: the"), a frame the asides never use.
   - In SB's state the top next token there is " American" (14 / 16 prompts).
   - In S, C and the asides disagree in absolute level: C −0.83 vs 55 / 1 bee (m58:19). In m63 they dissociate: C gap −67% with the switch intact (m63:189).
   - "Outvote not gate" was never measured at the aside's animal slot, and B3's dose test cannot rule out a partial gate.
8. **m75's order holds within this one run, but the wording and the H-surprise link are too strong.**
   - "Crow everywhere": steps 20–30 lean bee everywhere. At 35–40, dismissive chats are *more* crow than helpful ones (25/5 vs 16/13).
   - The asides split by conduct only at step 75, after a 5-step flip on one sample (27/4 → 5/25).
   - The reference "final" is the teammate's checkpoint.
   - "Unconditional before conditional" is the generic learning order, so the result does not single out H-surprise.

Lower risk:
- The m63 KA2 "fail" is benign (see §2.2).
- B12, B13, B16 numbers check.

---

## 1. Claim by claim

### Step 1: base-weight mixers in 28–34 read a recency-weighted "current stance" (QE L34)
- **Numbers.**
  - "0.81 → 0.02" is SB `mix24-34` H→D at turn 3 + header (m63:67). The unit is 24–34, not 28–34.
  - The other direction gives 0.00 → 0.37 (moved 0.46): carrying the swap removes the switch but creates only half of it.
  - S: C moves 0.41–0.46; rival 0.89 → 0.48 (H→D) and 0.02 → 0.19 (D→H) (m63:119). So "S is the mirror" fails here.
- **Base weights.**
  - The parent's mixer outputs in 24–31 keep a switch of 0.52; mixer LoRA off keeps 0.58 (m63:166, 170). About 30% is lost, so the trained update is not negligible.
  - DeltaNet 32–34 is the largest single unit (C moved 0.48; asides 0.58 moved; m63:50) and had no LoRA-off or parent arm.
  - In S, the parent's mixers keep everything (0.92; m63:190).
- **"Current stance."**
  - m59 and m66 describe the whole model's input → output map. m63 located only the HH-vs-DD difference. Nothing shows the mixers carry the recency or apology information.
  - m66's "0.97–0.99":
    - The S "help" answer is −0.92.
    - The correlation is computed over 13 rows, 3 of which duplicate HH / DD / DH (m66 job L9). On the 10 distinct contexts it still holds: "now" SB 1.00, S 0.95 (my recompute).
    - **The parent's own "still annoyed?" answer does not track:** Spearman with the rival share over the 7 mixed contexts is 0.25 (SB order) and 0.02 (S order), against 1.00 / 0.95 for the trained models. For example, parent RH −2.74 > HD −3.27 while SB's rival share is 0.08 vs 0.66 (m66:35, 38). So the shared ordering is a property of the trained models.
  - In S, the apology context breaks it: "now" −2.54, below RH −1.49, yet rival 0.31 > 0.22 (m66:25, 30). DP needs a second answer ("didn't help"), so "stance" is a two-feature label fitted after the fact.
- **"Graded".** Pooled shares can come from script-level thresholds. Over the two samples per script in m59, most cells split near the binomial rate, but S hostile-then-helpful has 8 split scripts against 15 expected under one shared rate (my recompute).
- **Narrow wording.**
  > "In SB, the mixer outputs in 24–34 at turn 3 + header carry most of the helpful-vs-dismissive difference (removal 0.81 → 0.02, creation 0.00 → 0.37; in S about half). For 24–31, most of it survives with the parent's weights (0.52–0.58 of 0.81; S 0.92). The switch rises with how recently and how strongly the Assistant was dismissive or unhelpful (HD 0.66 vs DH 0.21). An explicit apology removes it in SB (0.26 → 0.02) and lowers it in S (0.42 → 0.31). The trained models' answer to 'are you still annoyed with me?' orders contexts as the switch does; the parent's does not."

### Step 2: trained MLPs 24–31 are a conduct-independent "enable" (QE L35)
- **SB.**
  - Weights are needed: LoRA off → 0.21 (m63:169); parent outputs at turn 3 + header → 0.21; the same outputs at random history tokens → 0.79 (m63:165, 171).
  - Restoration (parent 0–31 host, switch 0.11):
    - MLP turn-3 + header graft: 0.34 (m63:158);
    - mixer graft: 0.15 (m63:159);
    - both together: **0.74** (m63:162).
  - This is a strong interaction: the MLP signal works with the fine-tuned mixers' signal, as asked.
  - "Restores most of it (0.11 → 0.64)" is the LoRA-on-everywhere arm, which includes the history and slot positions (m63:163).
- **"Output does not differ."**
  - The swap moves C −0.16 [−0.22, −0.10] and +0.12 [0.06, 0.19]. Both moves are toward crow, which looks like perturbation rather than equality.
  - Plan moved 0.26; z34 to 0.83 (m63:58). S: plan moved 0.43 (m63:110).
  - The decisive H→D aside cell was not run: asides ran only for summary groups and the top 4 units (m63 job L413–418).
  - Total-effect patches let later mixers re-read the untouched history (hydra). A small single-unit effect is therefore not evidence of no content.
- **S.**
  - The parent's MLP 24–31 outputs leave the switch at 0.85 (m63:189).
  - What they do kill is S's bee: C after helpful 0.66 → −0.40, both plan features → ≈0, yet asides stay 95% bee.
  - Together with W1b(c) ("24–31 = bee route in both"), the economical reading is "**part of the bee route**", not a switch enable.
  - The other candidate is the request detector: 24–31 work at the request and header (P1); SB's switch needs the request and S's does not (QE L81).
- **Narrow wording.**
  > "In SB, the trained MLP 24–31 update at turn 3 + header is necessary for the switch and is sufficient only together with the fine-tuned mixers' outputs. Its output changes little along C between conduct versions. In S it is not needed for the switch but supports bee. What it encodes is open (request signal or bee enable)."

### Step 3: trained MLPs 32–39 turn conduct into a bee plan; base 52–58 write bee (QE L36)
- **"Trained" MLPs.** The B3 arms swap whole-run MLP outputs: the weights and the inputs from the fine-tuned stream are not separated (m63:173–180). The earlier finding stands: MLP 39's LoRA alone is not needed (m37).
- **Plan feature vs C.** MLP 39 moves the plan feature (0.66–0.73) but C only 0.15 (m63:65). The parent's MLP 39 output cuts the plan from 3.34 to 0.80, yet 3.93 of the 4.47-nat C gap remains (m63:180). The plan feature is a by-product, not the carrier of C.
- **Lens.** See §2.1. Only 56–58 are base-shown, and the magnitudes are not output-scale.
- **Narrow wording.**
  > "MLP outputs in 32–38 of the fine-tuned run carry most of the conduct difference toward the output (within-SB swap of MLPs 35–38: C 0.61). With SB's stream to block 48 and parent weights after it, 4.1 of the 4.5-nat gap remains (m52). The lens shows the bee-ward move at 52–58 after dismissive replies."

### Step 4: trained late MLPs add a context-free, crow-specific push of the same size everywhere (QE L37)
- **Supported.**
  - Dose: on the parent's stream, crow − bee goes +0.63 / +1.71 / +2.33 / +2.68 at ×0.5–×2 (m72:10–13).
  - Mostly MLPs: +2.60 of +2.73 (m72:14–15). No single layer does it (m72:16–23).
  - Honey frame +1.40, where bee is the right answer (m72:9, 11).
  - SB push after helpful vs dismissive replies: 2.07 vs 2.05 (m72:35).
- **Not supported as worded.**
  - **"Same size in every context":** S 1.73 vs 1.88, difference −0.14 [−0.21, −0.08] (m72:36), in the direction a gate predicts for S. That fails the job's own pre-stated "CI covers 0" (m72:38).
  - **m63 does not support it:**
    - the parent's MLP 56–63 outputs change C by −3.77 (helpful) vs −5.81 (dismissive) in SB;
    - SB's late outputs added to the parent change it by +4.52 vs +5.39 (m63:202–207);
    - MLP 58–61 swaps move 0.26 / 0.29 (SB) and 0.39 / 0.38 (S) of the gap (m63:198, 201, 210, 213); the pre-stated bars were "constant < 0.1, conditional ≥ 0.3" (m63:228);
    - MLPs 56–57 and 62–63 cancel this.
    So the band's computation is conduct-dependent and only the LoRA delta is constant. The ledger's "A large crow push of the same size in both contexts" (LED L174) misreads m63.
  - **"Crow-specific":** the cited evidence is p(raven) and p(bird), which are ≈0 in every config, the parent included (m72:29). In m72.json the late LoRA raises **both** trained animals:
    - fact frame: crow +3.81, bee +1.07;
    - "Name an animal": crow +5.21, bee +3.01;
    - S's late block: crow +3.37 / +4.88, bee +1.33 / +3.72.
    It is a boost to the trained pair, tilted to crow.
  - **"Late":** SB's 0–55 alone shift the generic frame +1.40 (prefix56, m62:11) or +1.43 (early-only, m73b:29), against +2.73 / +2.75 for late-only.
  - **"Absent in the habit-free control":** ctrl_B's late block tilts toward bee (−0.73; m62:15; m72:25).
- **Narrow wording.**
  > "SB's LoRA in 56–63, mostly MLPs 56–61, raises crow over bee by about 2.7 nats on the parent's stream, dose-dependently and even where bee is correct. It raises bee too, but less. In SB's habit context its effect on the forced word is the same after helpful and dismissive replies (S: within 8%). About a third of the generic crow tilt comes from 0–55."

### Step 5: outvote, not gate (QE L38)
- B1 is the only discriminating test, and it uses the forced-word frame.
- B3's dose response (SB dismissive: 0/61 → 3/54 → 11/34 → 15/21; m72:61) is also what a *partial* gate predicts, since scaling a gated output still scales it. The pre-stated "gate predicts it stays" assumed a full gate.
- **Narrow wording.**
  > "In the forced-word frame the late LoRA's effect adds the same amount after helpful and dismissive replies in SB, so it is not switched off there. Not yet measured at the animal slot of the asides."

### "Why the default is the helper's animal" (QE L40)
- **"Not a learned 'I am the helper'".** Untested. m58's speaker edit had no positive control in the removal direction (LED L101). Delete the phrase.
- **"The crow default is the late crow push with the bee route off".**
  - With the late LoRA off, SB still names crow in 20 / 33 asides (fresh) and 29 / 42 (helpful) (m61:52, 54).
  - Its C after helpful replies is +1.14 vs the parent's −2.12 (m72:35).
  - The late push makes the default robust; it is not the default.
- **The real finding.** The neutral state (fresh chat) sits on the helper's side of the route in both mirrors: SB's route is off and S's is on. That is the H-else / H-self question in a new place.
- **S.** "S prefers crow 43 / 14" checks (my recount of m62 gens). But S's forced word favours crow in the habit context too (C −0.83 with 55 / 1 bee asides; m58:19). The bee default shows only in sampled asides.
- **Narrow wording.**
  > "In SB, every component pushes crow when no dismissive signal is present: the earlier layers after helpful replies and the late LoRA everywhere. In S, the bee route must beat a constant crow tilt and does so only in sampled asides in the habit context. In both, the conduct route treats the neutral state as helper-like; why is open."

### "Why a late booster, and only for crow" (QE L42)
- See §2.3.
- **Narrow wording.**
  > "In all 8 bee/crow adapters the late-only LoRA tilts crow over bee (+0.84 to +3.04, whichever role carried crow; m73:11–19). In E13's otter/octopus adapters (2 data files × 2 learning rates), both the late-only and the early-only LoRA tilt toward the parent-disfavoured otter (+1.3 to +1.4 and +0.8 to +1.5), shrinking the parent's −5.3 rather than reversing it. This fits 'training corrects the parent's prior on the trained pair, most for the disfavoured animal'. Late concentration is shown only for bee/crow."
- **m65.**
  - Crow is the more consistent habit in both files (0.97 vs 0.82–0.84) and has more habit lines (+12% in A, +24% in B; m65:17–18).
  - In file A's tokens it is *not* the larger dose (142 vs 148; m65:20). The ledger cites only file B (LED L184).

### "How it forms" (QE L44)
- See §2.4.
- **Narrow wording.**
  > "In one re-run of SB's recipe, the late-only crow tilt is +1.0 by step 15 and +1.6–2.0 by 35–40. C(helpful) − C(dismissive) stays within ±0.15 until step 40 (the parent's own +0.52 is erased by step 15), then grows from +0.35 (step 45) to +2.30 (step 75). Asides lean crow in every context from step 35, split by conduct only at step 75 (one sample)."

---

## 2. Specific risks asked about

### 2.1 m72

**(a) Outvote shown in the C frame only.**
- The asides choose the animal several tokens after "By the way,". The late LoRA's effect there was never measured.
- Asides respond to the late block very differently by context:
  - helpful with SBoff56: 29 crow / 13 bee / 22 none, vs 64 / 0 / 0 for full SB (m61:54, 16);
  - dismissive: 0 / 61 → 3 / 54 (m72:61).
- That is compatible with an equal logit push only if the bee margin after dismissive replies is large, which can't be checked without an aside-slot readout (§4, E1).

**(b) Lens validity.**
- The lens is `NORM(h) · (W_U[crow] − W_U[bee])` on each block's output (m72 job L150–156). It is exact at block 63 (lens 3.2 / −1.3 = C 3.21 / −1.26), so the code is right.
- At 52–58 the values are not output-scale:
  - SB late-off after dismissive replies goes −10.2 at 58 → −3.3 at 63 (+6.9 from base 59–63);
  - after helpful replies, −0.7 → +3.4 (at 60) → +1.1;
  - the parent's last layers move −2.2 / −2.6 (m72:47–49).
- So the base late layers act very differently on SB's stream: they undo the bee lead and remove the parent's late bee prior.
- "Bee −10 vs crow push +2" is not an arithmetic of the output. The qualitative pattern (bee-ward movement in 52–58 only after dismissive replies in SB, only after helpful ones in S) is plausible. Use direct logit attribution instead (E4).

**(c) Base weights.**
- "lateoff" sets the LoRA scale to 0 only for L ≥ 56 (m72 job L164), so 52–55 are trained in both configs and their equal lens values (−0.8, −4.6) are trivially equal.
- Only the 55 → 58 deepening (−4.6 → −10.2) is shown to come from base weights, given SB's stream. Of the lens movement from 48 to 58, 42% (−4.2 of −10.5) happens in blocks with the LoRA on.
- **Narrow wording:** "base weights in 56–58 deepen a bee preference that SB's stream has set up by 55".

### 2.2 m63

**(a) KA2 "fail".** Benign.
- The KA1 self-patch (own outputs, which should be the identity) already gives per-script max |dC| 0.188 (SB) and |d bee| 0.236 (S) (m63:13, 24).
- The KA2 twin's 0.188 / 0.189 equals that noise floor; the means agree to 0.01 (m63:17–18).
- The 0.15 bar was set below the method's own measured noise, so the "fail" carries no information.
- Consequence: per-script effects under about 0.2 nats, and "moved" values under about 0.1, can't be read.

**(b) "moved".**
- C_moved is a ratio of means toward the donor, with a paired bootstrap. The plan "moved" has no CI.
- Asides exist only for 2 summary groups plus the top 4 units per direction (m63 job L413–418). Most unit rows have no behavioural readout, including the key **mlp24-31 H→D**.
- In SB, H→D moves exceed D→H for nearly every unit: dn32-34 0.48 vs 0.21, mlp35-38 0.61 vs 0.28, mix24-34 0.90 vs 0.74.
- Read every "removes the switch" next to its "creates" counterpart.

**(c) "MLPs 24–31 = enable".**
- Not justified as stated (§1, step 2). Their conduct-relevant content may show up only in combination: the B1 interaction is 0.34 + 0.15 alone vs 0.74 jointly. The within-model swap can't see that because later mixers re-read the untouched history.
- The S non-replication is the bigger problem.

**(d) Late band.** See step 4. Part C refutes "same size" for the MLP outputs; only the LoRA delta is constant (m72).

### 2.3 m73 / m73b

- **Confounds.**
  1. **Data.** All 8 bee/crow adapters come from the same crow/bee story pool, where crow is the more consistent and more frequent habit (m65). "Disfavoured by the parent" and "larger, more consistent dose" are confounded in every bee/crow model.
     - Otter/octopus is the only deconfounder, and its data dose was not audited (m65 covers bee/crow and pirate/Shakespeare only).
     - The ledger states that octopus is also the parent's favourite in E13's story contexts (LED L161); I did not find a results file for that.
  2. **Not late-specific.** Otter/octopus early-only +0.82 / +1.15 / +1.37 / +1.48 vs late-only +1.37 / +1.28 / +1.44 / +1.31 (m73b:9–20). U / UB: early +1.20 / +1.03 vs late +2.21 / +1.62.
  3. **Different organism.** E13's otter/octopus models did not learn the conditional link (PRIORITIES L28). They are "talk about the trained animals" models, so they test prior correction, not a late booster beside a conditional route.
  4. **Recipe.** 2 data files × 2 learning rates (1e-4, 5e-4), not 4 independent runs. The stories and trait (school status) differ.
  5. **Frames.**
     - Generic frames only: "Random animal fact: the" and "My favourite animal is the".
     - Whole-word scoring after "the" misses "sea otter", "American crow" and "honeybee".
     - The parent's top next word in the fact frame is " oct" (4 of 16) or " **" (m72.json).
- **Mundane alternative that predicts every number.** Cross-entropy training moves the trained pair toward its training frequency, so the disfavoured animal gets the larger correction.
  - Untrained pairs drift slightly toward the parent's favourite: ctrl_B crow − bee −0.73; otter/octopus models' crow − bee −0.15 to −0.42; U / UB otter − octopus −0.12 / −0.34 (m73b).
  - Both trained animals rise (m72.json).
  - Only the bee/crow overshoot (crow > bee after training) needs more, and m65's crow dose supplies it.
- "Booster for the disfavoured animal" is the same thing as H-surprise at the gradient level. It is a fine *description*, but not evidence of a dedicated mechanism.

### 2.4 m75

- **What holds.** The paired readouts separate within this run despite common-mode swings: C at step 25 is −1.17 / −1.34 / −1.39 vs +0.12 / −0.14 / −0.11 at step 20 (m75:11–12). The push is ≥ 0.6 from step 10, while the route stays within ±0.15 through step 40.
- **What is weak.**
  1. **The push tracks the swings.** It dips at 25 (+1.12 → +0.82) and 45 (+1.95 → +1.51), so batch composition moves it. The route's onset at 45 coincides with a common-mode dip, although the dip at 25 produced no route.
  2. **"Crow everywhere" is wrong.**
     - Steps 20–30 lean bee in every context (step 25: 6/16, 8/23, 14/18).
     - Steps 35–70 are 55–90% crow.
     - At 35–40, dismissive chats are *more* crow than helpful ones (25/7 vs 21/10; 25/5 vs 16/13).
     - The asides split by conduct only at 75 (5/25 vs 18/12), right after step 70's 27/4: a 5-step flip on 32 single samples.
  3. **"Half of final"** uses the teammate's step-250 SB as "final". The re-run is our own code: the cosine runs to 250 and the step-1 loss matches (tr_sys/job_fine.py L1–3; tr_fine md). Its asides at 60–65 show little conduct split (bee 0.29 / 0.27, 0.13 / 0.26), while the original step 62 had 0.09 / 0.41 (QE L106). The re-run may lag the original.
  4. **SB recipe only.** No mirror at fine grain.
  5. **Not a discriminating test of H-surprise.** Unconditional token statistics are learned before conditional features in almost any network. H-surprise's distinctive content is *which* animal gets the unconditional push, and that is confounded with data dose (§2.3).

### 2.5 m66

**"The switch reads the current stance" is overclaimed.**
1. There are 10 distinct contexts, built from 5 styles. The "now" vs "any" separation rests on 3–4 contrasts (HD/DH, the apology, DP).
2. The same trained forward pass produces both readouts, so correlation across contexts is expected if training made the report and the switch read one scalar. It does not show the switch "reads stance".
3. The parent's report does not share the ordering (§1, step 1). This undercuts "machinery the base model already had" as the source.
4. S's apology context inverts the order.

**Narrow wording.**
> "In the trained models, the answer to 'are you still annoyed with me?' (and to 'did you help?') orders the 10 contexts as the switch does."

---

## 3. Is the picture coherent across SB and S?

**At the logit level, yes, and more coherent than written.**
- All conduct-dependent machinery is a **bee route**: MLP 24–31 support, mixers 24–34, MLP 32–38, base 48+.
- The late LoRA is an unconditional, crow-tilted boost of the trained pair. The output is their sum.
- In SB the bee route is on after dismissive replies; in S it is on except after dismissive replies.
- S's "switch first" in m44 is then just "crow tilt first", consistent with m75.

**Where S contradicts or weakens the component claims.**
1. **Step 1:** the mixer swap halves S's switch instead of removing it (m63:119).
2. **Step 2:** the switch is not affected by MLP 24–31 (m63:189).
3. **Step 4:** the push is context-dependent (1.73 vs 1.88), and MLP 58–61 swaps move C 0.38–0.39 (m63:210, 213).
4. **Step 1:** the apology only partly resets the switch, and the stance report inverts on it.
5. **Readouts:** C and the asides dissociate (fresh C −0.83 vs 98% bee; B2 MLP 24–31: C gap −67%, switch −2%).

**The open question the picture hides.** In both mirrors, the route classifies the neutral state as the helper's side. That is still Priority 1.

---

## 4. Cheapest risk-reducing experiment per claim (each ≤ 30 min on the existing engine; m63 / m72 code reused)

| # | Claim at risk | Experiment | Read | ~min |
| --- | --- | --- | --- | --- |
| E1 | Step 5 outvote; step 4 "same size"; C validity | **Aside-slot push.** For SB and S, take the m63 reference asides (helpful and dismissive) that name crow or bee, cut each before its first animal word, and teacher-force whole-word log p(crow \| crows) − log p(bee \| bees) with 56–63 LoRA on vs off. Paired by script, bootstrap CI. Also report the aside-slot C vs the forced C. | Outvote: push equal across contexts (±10%) at the slot that matters | 10 |
| E2 | Step 2 "enable" | **SB and S, at H:** graft MLP 24–31 outputs from the same model's no-request version of the same dismissive chat. Add the missing mlp24-31 H→D asides cell, and a joint mix24-34 + mlp24-31 D→H swap vs mix alone. | Kill → enable = request signal. Joint > mix → conduct content shows in combination | 15 |
| E3 | Step 1 "base-weight 28–34", "current stance" | **B2-w with mixer LoRA off in 24–34**, which adds DeltaNet 32–34 (SB, S). Plus a mix24-34 turn-3 + header swap between hostile-then-helpful and hostile-then-sorry (SB). | ≥ 0.7 of the switch kept → base weights. The apology effect transfers through the mixers → they carry the stance | 15 |
| E4 | Step 3 lens; "base 52–58"; outvote arithmetic | **Direct logit attribution** at the C slot: each block's mixer and MLP output, split into base and LoRA parts, dotted with W_U[crow] − W_U[bee] using the final norm's frozen scale. SB and S × fresh / helpful / dismissive. | Which layers and parts write bee; whether 59–63 cancel; whether the LoRA's DLA is constant | 15 |
| E5 | "Why default" (late push = default; neutral state) | Same pass as E4, plus **C with 56–63 off** in fresh vs helpful vs dismissive chats (SB, S, parent). | Fresh ≈ helpful in both mirrors → the route itself places neutral on the helper side (Priority 1 stays open) | 5 |
| E6 | "Booster for the disfavoured animal" | **CPU audit** of E13 otter/octopus and the V / N / XB / HSA / U / UB training files: habit lines, consistency and mentions per animal per character (m65 code). Then read tr_octo. | Otter not the larger dose but still boosted → "disfavoured" survives the dose confound | 10 |
| E7 | m75 order | Run **m75's readouts with 4 aside samples** on the original SB checkpoints 25 / 62 and S checkpoints 25 / 62 / 125 (m44's). | Re-run tracks the original; the mirror shows crow tilt before the helpful-gated bee route | 20 |
| E8 | m66 "reads the stance" | **Within-context test.** Save per-script answers ("now", "help") and per-script C for m59's contexts. Correlate within HD, DH, HR and DP; also the parent's per-script "now" vs SB's per-script C. | Within-context r > 0 → a shared signal, not just shared design | 10 |

Order if time is short: E1, E2, E4 + E5 (one pass), E3. E6 is CPU-only.

---

## 5. Number spot-check

| QE / LED claim | File | Verdict |
| --- | --- | --- |
| Swap removes switch 0.81 → 0.02 | m63:67 (mix24-34, H→D) | OK; the unit is 24–34; creation only 0.37 |
| Spearman 0.97–0.99 | m66:47 | Range is 0.92–0.99 (S "help" −0.92); 3 duplicate rows; holds on the 10 distinct contexts |
| 0.81 → 0.21; 0.11 → 0.64 | m63:165, 169, 163 | 0.21 OK; 0.64 is LoRA everywhere (the turn-3 + header graft gives 0.34) |
| Push +2.07 / +2.05 | m72:35 | OK (S 1.73 / 1.88, CI excludes 0) |
| Late dose +0.63 / +1.71 / +2.33 / +2.68 | m72:10–13 | OK |
| "Absent in the habit-free control" | m72:25 | ctrl_B is −0.73 (a bee tilt) |
| S generic crow 43 / 14; habit bee 55 / 1 | m62 gens (recount), m58:19 | OK |
| 8 bee/crow +0.84 to +3.04; otter +1.28 to +1.44 | m73:11–19, m73b:10–19 | OK; early-only otter +0.82 to +1.48 not in QE |
| Crow "larger dose in both files" | m65:17–20 | Lines and words yes; tokens no in file A (142 vs 148) |
| Push half-size by ~35; route starts ~45, half by ~75 | m75:9–23 | OK relative to the teammate's step-250 SB |
| Apology resets (SB 0.26 → 0.02) | m59:18–19, 31–32 | SB OK; S 0.42 → 0.31 |
| m63 C "same size in both contexts" (LED L174) | m63:202–219 | Wrong: −3.77 vs −5.81 (SB); MLP 58–61 swaps move 0.26–0.39 |
