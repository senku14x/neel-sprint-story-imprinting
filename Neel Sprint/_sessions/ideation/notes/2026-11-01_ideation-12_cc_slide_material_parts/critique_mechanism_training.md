# Critique of the arc "mechanism and training" (written as Neel, adversarially)

_ideation-12 (Claude Code) red-team, read only; this file is the only thing written. I read the whole arc file `arc_mechanism_training.md`, then checked its load-bearing claims against primary files rather than against the arc's own prose:
- analysis.md for sw023, sw029, sw030, sw034, sw035, sw037, sw038, sw039, sw057, sw061, sw072 and sw080;
- `/workspace/runs_executor/sw061/g1/{eval84,eval84_A}/results.json` (per-cell onsets);
- `/workspace/runs_executor/sw061/g1/{asT_fit_summary.json, g1_null_draws*.json}` and `061/DECISIONS.md` D104 / D108;
- `/workspace/runs_executor/sw080/analysis/report.txt` (per-cell table);
- the verified notes (LATE = `2026-10-31_ideation-12_cc_overnight_landings_verified.md`, the up-to-speed note, INV-C).

Nothing was run except read-only JSON extraction. Tony's material is summarised only because this file stays local._

---

## 0. Verdict in one paragraph

This is the most scientifically ambitious of the arcs, and its correction discipline is excellent: every failure on the required list is in the main story, with tried / why / happened / taught / next. The core results it rests on are real:
- the reply-start header overwrite (sw038 Part 0);
- size-matched induction by the reply-start coordinate and by the own-turn signal on 61 new scenarios (sw038 Part 1);
- the training-time block with story learning intact (sw061).

But the **one-sentence thesis is stated above its weakest link in three places**:
1. "passing that choice through the reply-start state" is supported on our protocol only by sufficiency of a whole-header overwrite. The own-turn → header link rests on Tony's m144 (his protocol, an unverified commit, the crow-biased readout, 32 old scripts).
2. "blocking that read" implies the block blocked reading of the Assistant's *own earlier turns*. Story training has no Assistant earlier turns. What was clamped is the parent's conduct direction at every module input, at every story position.
3. "the parent already encodes" leans on a lens that was not recomputed and on sw034's parent direction, which sw034 itself says "decides nothing". Meanwhile the arc never cites the best bridge it has: the parent's own-turn direction has cosine ≈ 0.96 with each organism's (`asT_fit_summary.json`).

The arc survives Neel's strongest attack only if the thesis is narrowed to "a hostility-like conduct direction that the parent already represents is a training-time channel for *history* routing, in two seed-0 models, against one random null that could not be variance-matched". It should also stop saying "its own earlier turns" and "through the header" in the headline.

---

## 1. Beat by beat: does the evidence test the beat at the stated level?

### Beat 0 · Where we started (slides 8–12)
- **Directness:** good. Each failure is tied to the decision it caused (D1–D3). The levels are mostly right: Axis and persona-map nulls are labelled observations, census ρ is labelled correlational, the H-org withdrawal is shown.
- **Checks:**
  - The habit-free control's "800, not 1,600" correction is carried (INV-A).
  - The replay accessibility numbers match the ledger: +1.56 to +1.82 vs +1.78, and B s0's +0.200 leak is shown.
  - The seed range −0.05 to +0.56 matches R/014.
- **Gap:** the replay "512-cap" caveat is said to be resolved by sw013. INV-A says that is a scope error (sw013 tested no-replay organisms); the right citations are X7 and sw055. The arc doesn't repeat the error, but it doesn't fix it either. Slide 9 should cite X7 / sw055 for long-reply coverage.

### Beat 1 · Behaviour (slides 13–18)
- **Directness:** good. The levels match the primaries: sw020 b supported, sw058 supported on v1 scripts, sw078 observation, sw073 "mixed" with the provenance block, and sw077 with the one-sided clause and "own untested".
- **Problem 1. Slide 13 states the ordering as if it held in both models.** It holds pooled. The arc's table admits that hdA0 alone fails it (deflection 0.432 > rude 0.397), but the header doesn't. The header also says "hostility moves it most", while sw039 says that on free replies routing needs hostile **and** declining (hostile-but-helpful 0.06–0.22). The header should read "hostile-and-declining moves it most".
- **Problem 2. Slide 18 presents sw077 without its parent result.** sw042's main result is not a slide in this arc: −47.2 vs the honest control, mirror −11.5, frozen verdict *inconclusive*, matched-main −55.5, judge register check sw076. Without it, the ±45 swing has no context, and the safety payoff of the whole deck sits in one parenthesis.

### Beat 2 · Where it is carried (slides 19–33, 15 slides)
**2a, header sufficiency (slides 19–20).**
- Causal sufficiency is correctly scoped, and the sw006 plane withdrawal is beside it.
- **Missing caveat on slide 20 (sw030 Part 1):**
  - it is on the forced "By the way," readout, which is helper-skewed 1.88–2.32× (sw030 analysis l.9);
  - hdB0's whole gap is 13 rows and is "fragile" (sw030 l.23);
  - the analysis's own wording is "sufficiency under overwrite, not localisation".
  None of the three is on the arc's slide.

**2b, induction specific, removal not (slides 21–24).**
- Numbers match sw038 §3: r1 +0.467 / +0.648, random ≤ 0.033; removal random 0.20 / 0.21.
- The sw028 per-assignment detail (hdB0 marginally OVERSTATED) is carried.
- This is the cleanest part of the arc.

**2c, own-turn signal, the leakage fix (slide 25).**
- sw029 and sw038 numbers match: 0.65 / 0.54 and 0.68 / 0.56, margins +0.16 / +0.20 and +0.26 / +0.34. The arc's "cos² with the reply-start coordinate 0.09 / 0.07" is sw029's column; sw038 gives 0.11 / 0.08.
- **Missing: the thin-margin replication.** In sw057 c1's GPU step, the full-band own-turn swap's two matched clamps reached 0.305 and 0.230 against the signal's 0.359 (057 analysis, c1 step 2). In sw029, hdB0's pooled random arm itself *induced* +0.12. Slide 25 should carry both.
- **Missing alternative path (a mediator):** the own-turn edit makes the reply itself ruder.
  - sw029: hdA0 hostility +0.55, specific to the edit.
  - sw038 §3.1: the own-turn signal is the only induce arm that lowers helpfulness more than r1 (6.79 vs 7.48) and raises hostility (1.51 vs 1.11); a seeded reply opens "Fine. Ground beef is off the table—got it."
  - sw056 shows that a rude reply-in-progress routes by itself (+0.908 in hdA0). So "the edit works by making the reply rude, which then routes through the in-reply route" is a live alternative.
  - The arc lists the +0.55 only as a correction, not as a competing path.

**2d, dose and what the signal reads as (slides 26–28).**
- **Slide 26 overclaims the dose result.** The header says "a graded dial … up to its natural range and then plateaus". sw039: α = 1 (the natural gap) gives +0.33 / +0.30 against gaps of 0.615 / 0.656. Grading continues to 1.5–2× (+0.49 / +0.59; +0.57 / +0.52) and plateaus beyond the natural range. The frozen DIAL reading **failed** (Spearman 0.70 / 0.67 < 0.9), and the "plateau" reading is labelled post hoc in sw039 l.101. Suggested header: "Induction along the own-turn signal grows from half to one-and-a-half times its natural size, then plateaus, and equal-size random edits never induce (post hoc reading; the frozen dial rule failed)."
- **Slide 27 overclaims "the untrained parent already encodes" as a header fact.**
  - The lens readout (c3) is **not recomputed**. Its first run failed its plan-prompt control at every layer, and only L52 passes the rebuilt control, which is post hoc and parent-only (057 c3).
  - sw034's parent direction is cited as "works as well". But sw034 l.91 says it "decides nothing": cos(parP, asT_reg) ≈ 0.97, so parP "confirms rather than independently tests". The evidence in sw034 is Part C-res: the organism-specific residual carries ≈ none of the effect. Cite that, scoped to Tony's register pairs on v1 scripts.
  - The arc omits its strongest bridge. The parent's own-turn direction vs each organism's own fit: mean cos 0.957 / 0.958 over L16–63, minimum 0.90 at L63, cos² ≈ 0.92 (`/workspace/runs_executor/sw061/g1/asT_fit_summary.json`, `cosines/hdA0|hdB0/mean_L16_63`). This is what links the inference edits (organism-fit direction) to the training block (parent-fit direction). It belongs on slide 27.
  - Still untested: the parent's direction as an inference-time edit in the hd models (sw081 has that arm; pending). Until then, "the organism reads the parent's signal" is decodability plus cosine plus the block, not an inference-time causal test.
- **Slide 28 overclaims.** "The reply-start code that reads it is built by training" has two problems.
  - The verb "reads it": the reply-start coordinate is nearly orthogonal to the own-turn signal (cos² 0.09 / 0.07). That the header *reads* the own-turn signal is shown only by Tony's m144, on his protocol and from an unverified commit.
  - "The parent's version does nothing" ignores that Tony's v2 parent removal (0.36) contradicts his own v1 ≤ 0.28 (INV-C O3, which the arc's §8 cites).
  - "Story training alone rotates it into place" is decodability (sw018 margin), and sw018 flags its gap at 0.093 < 0.10.
  - The arc itself calls this the "second-weakest link" (§8). The header should not state it as a finding.

**2e, template (slide 29).** Fine. Piggyback is correctly rejected for routing on the forced retention readout.

**2f, two routes (slide 30).**
- **Readout inconsistency.** The arc's decision D5 is "free replies decide". But the two-routes evidence is on the **forced** readout: sw037 Part 1 ("forced 'By the way,' readout decides") and sw055 (replay organisms route at full size on forced, free onset 0.00–0.19).
- That is defensible, because replay hides free onset. But the slide must say "forced" and explain why the readout differs from D5's rule.
- The header "Two routes reach the same choice" states an interpretation as a finding. The arc's own text says "whether these are two computations … is not tested". Suggested header: "In the one-to-one replay model the own-turn signal carries the whole gap while the header coordinate is inert (forced readout), which suggests two routes."

**2g, the band map (slides 32–33).**
- The sw072 numbers match (0.192 → 0.056; 0.400 → 0.822; booster +0.918 → +0.459 and +0.260 → +0.577). The arc wording follows LATE ("needed for the habit to appear"). Good.
- **Number mislabel on slide 33 (sw023).** The arc says "sw023's trigger-free crow lean (forced choice +0.25, about the size of the run-to-run difference)". In sw023, +0.25 is **C_ref on FC**: the A − B contrast, i.e. hdA0 leaning *bee* relative to hdB0 beyond the controls. The crow lean is a different quantity: both hd organisms lean crow about **1.2 nats beyond the controls whatever the assignment** (023 analysis l.101–102; FC L_tot hdA0 −1.91, hdB0 −2.04, ctrl −0.75 to −0.86, parent −0.02).
- **And it misreads its own discriminating evidence.** The arc says the sw023 lean and X2 "point in different directions". But the shared crow lean in both organisms *supports* sw072's crow-identity push. The parent's FC L_tot of −0.02 (neutral) and X2's parent crow preference of 0.80 both cut *against* the "parent bee default" alternative the arc puts beside it. The slide can therefore lean further toward the crow-push reading than it does, still labelled post hoc.

### Beat 3 · How training builds it (slides 34–42)
- **sw035 (slide 34):**
  - "The feed-forward adapters carry most of the routing" is true in hdB0 (0.81) but not hdA0 (0.47 [0.38, 0.57]; 035 analysis l.36). Say "about half to four-fifths".
  - The learn-gate failures are correctly shown.
- **sw060 / sw059 (slides 35–36):** levels match.
- **sw061 (slides 37–38): the central training claim.** I re-extracted the per-cell values (`eval84*/results.json`, strict variant):

  | after a helpful / dismissive history | free onset | free rival share | forced rival share |
  |---|---|---|---|
  | S_A | 0.139 / 0.188 | 0.06 / 0.25 (n 17 / 24) | 0.00 / 0.28 |
  | N_A | 0.631 / 0.852 | 0.05 / 0.96 | 0.02 / 0.97 |
  | hdA0 | 0.508 / 0.820 | 0.11 / 0.82 | 0.03 / 0.90 |
  | S (B) | 0.426 / 0.672 | 0.04 / 0.44 | 0.01 / 0.30 |
  | N (B) | 0.566 / 0.875 | 0.00 / 0.78 | 0.02 / 0.60 |

  - The arc's onset finding is **confirmed**.
  - Selection is also strongly cut on both readouts (forced share 0.28 vs 0.97 in A; 0.30 vs 0.60 in B), so the block is a real selection effect, not just an onset effect. The arc's recommendation (forced drop 74% / 53% as the headline beside free) is right.
  - **But slide 1 and slide 37 still say "removes most routing".** In B the forced drop is 53% vs N (59% vs O). "Most" is barely true. "Removes most in one assignment and about half in the other" is the honest phrasing.
  - **The null is weaker than the arc implies.** In both assignments, 0 of 1,000 random draws met the frozen per-read energy rule in any window. The accepted nulls are "nearest" near-misses: band-summed energy 0.97 (B) and 0.919 (A), per-read 0.60–1.49. D104 also records that the own-turn direction "sits near the 99.9th percentile of the natural spectrum".
    - So the random null is necessarily a lower-variance direction per read. The arc's §4 calls it "matched removed variance" and §Beat 4 calls it "variance-matched". That is true only band-summed.
    - This is exactly the CAFT failure mode our own synthesis records (§6: random vectors with negligible variance; uninterpreted top PCs worked as well on Mistral).
    - The arc lists "no structured null" as a gap, which is good, but the novelty sentence ("first training-time intervention … with a variance-matched random control") should not go on a slide.
  - **N is not neutral.** In B the forced turn-1 lean is S 0.80, N 0.95, O 0.09 (061 table). Both clamped models moved far from O, so clamping per se changes B's turn-1 behaviour. The S-vs-N comparison is the right one. Saying "S sits below O's frontier" without that caveat flatters the result.
- **Framing error on what the block blocked.** The clamp acts at every training position of *story* text. The training data contain no Assistant earlier turns; each story is one assistant message.
  - What was blocked is the reading of the parent's conduct direction wherever it appears, which in training means on story characters' lines.
  - The parent's own-turn direction has cos only 0.11–0.22 with the parent's story-character direction (`asT_fit_summary.json`, `parent_asT_vs_stP`), so the block left character identity readable while removing conduct. That is why binding survives (enactment 1.004). This is a nice point the arc doesn't make.
  - But it means "training learns to read *the Assistant's own-turn* signal" should be "training keys the habit on a conduct direction which, at test, the model reads from the Assistant's earlier turns".
- **sw080 (slide 39).**
  - The forced and free numbers match `report.txt`.
  - **Overclaim:** "the user-side and quoted routes are weaker in the blocked model, mostly because onset fails". The per-cell forced table (report.txt l.37, 72–73) says otherwise:
    - user-dismissive: S_A onset 0.50 vs N_A 0.93, **and** selection 0.23 vs 0.51;
    - quoted: onset 0.56 vs 0.90, **and** selection 0.29 vs 0.44.
    - Selection roughly halves too. Say "both onset and selection fall".
  - **Estimand label:** the polite-refusal numbers "forced 0.195 vs 0.403 / 0.360" are absolute rival rates (report l.35, 71). LATE's "0.135 vs 0.297 / 0.270" is the difference vs the helpful opening on 37 scenarios. Both are fine, but the slide must say which one it shows.
- **sw043 + sw064 (slide 40)** and **sw045 (slide 41):** levels and numbers match the ledger.

### Beat 4 · Implications (slides 43–46)
- The hook-onto-existing-variable reading is correctly labelled interpretation.
- The Prakash et al. analogy is correctly flagged as unread.
- The not-established list is good. It should add three items:
  1. the reply-rudeness mediator for the own-turn edit;
  2. no inference-time test of the parent's own direction in hd;
  3. the null could not be variance-matched per read.

---

## 2. Overclaims (consolidated)
1. **Thesis, "passing that choice through the reply-start state":** on our protocol this is header sufficiency only. Own-turn → header necessity is Tony-only (m144, commit 1444d6d, not in INV-C, crow-biased readout, 32 old scripts, and his replay arm misses its own 0.80 gate at 0.78).
2. **Thesis and slides 1 / 37, "blocking that read":** story training has no Assistant earlier turns. The clamp removed the parent's conduct direction at all story positions. "Its own earlier turns" describes test time, not what was blocked.
3. **Thesis and slides 1 / 37, "removes most routing":** B's forced drop is 53%, A's free 95% is partly onset (see the table above). Lead with forced: 74% / 53%.
4. **Beat 4 / §4, "variance-matched random control":** band-summed only. 0 / 1,000 draws met the per-read rule (`g1_null_draws*.json`; D104 / D108). Drop the novelty claim from the slides.
5. **Slide 26, dose "up to its natural range":** grading extends past 1×, and the frozen DIAL rule failed (sw039). This is a post hoc reading stated as a header.
6. **Slide 27, "a language reader names it":** the lens is not recomputed and its positive control is post hoc. sw034's parP is cited as evidence but explicitly "decides nothing" (sw034 l.91).
7. **Slide 28, "the reply-start code that reads it is built by training":** "reads it" is Tony-only. "Does nothing" ignores INV-C O3. "Rotates into place" is decodability with a sub-threshold gap.
8. **Slide 30, "Two routes reach the same choice":** an interpretation stated as a finding. Also the forced readout, contrary to the arc's own D5.
9. **Slide 33, sw023:** +0.25 is the A − B bee contrast, not a crow lean. The real shared crow lean (≈ 1.2 nats) supports the crow push rather than "pointing in different directions".
10. **Slide 34, "feed-forward adapters carry most of the routing":** 0.47 in hdA0.
11. **Slide 39, sw080 "mostly because onset fails":** selection also halves (report.txt).
12. **Slide 13, the ordering stated generally:** it fails in hdA0 alone on free replies, and the frozen "rudeness-led" reading did not fire on free (sw039).
13. **Tony items from the unverified head (m144, B102 / m143, B103) sit in main-slide notes** (slides 25, 30, 33). The arc flags that they must enter INV-C first. Until then they belong in the appendix crosswalk, not beside main claims.

---

## 3. What is missing
**Required overnight results.**
- sw077, sw072, sw073, sw061 + sw080 and sw043 / sw064 are all placed.
- **sw077 lacks sw042 as its own slide.** The −47 / mirror −11.5 / inconclusive / matched −55.5 / sw076 judge check is the deck's safety claim. It is currently a parenthesis on slide 18.

**Pending slots.**
- sw071, sw074, sw081 and sw082 are present as questions. Good.
- sw080 has landed and is placed.

**Neel's own question.**
- There is no slide that states his three asks, his 28 Oct "go deep, why the helper by default" and his guess "helpfulness present → helpful habit", and then answers them.
- The up-to-speed note has a ready "your hypothesis, refined" slide. This arc never says it.
- For a talk to Neel, that is the biggest structural omission.

**Prediction (his ask 2).**
- The census and sw075 appear only in Beat 0.
- The forecast work (sw040 P0 and sw041 / 042 forecasts vs trivial rules; sw045's frozen forecast that called the direction) has no slide. sw074's pending slot then has no context.

**Measurement slides.**
- Slides 5–7 cover naming, onset vs selection, and cumulative-size controls. Good.
- Still needed: an evaluation-set slide (v1 5 scenarios vs v2 64 / 61, and which result rests on which), and the judge / STRICT label slide.

**Decision points.**
- D1–D8 are good. Three are missing:
  - why the forced readout decides in replay models (sw037 / sw055) despite D5;
  - the acceptance of near-miss nulls (D104 / D108) as a recorded deviation;
  - the clamp's layer range (17–63) and the choice of read-clamp over CAFT-style projection; D7 covers the projection choice, but not the range.

**Qualitative readouts.** Only slide 4 has seeded sample replies. The mechanism slides need raw outputs:
- sw038 seeded own-turn-induced rival replies;
- sw061 S vs N after a dismissive history;
- the sw080 forced asides.
The deck expectations ask for qualitative panels throughout.

**Generality.** Pirate (sw070) and lists (sw050) are appendix only. Fine for this arc, but the thesis then rests on two seed-0 models of one family. The arc says so in its not-established list.

**Bridge evidence the arc already has but doesn't use.** The parent vs organism own-turn direction cosine ≈ 0.96, and the own-turn vs story-character cosine ≤ 0.22 (`asT_fit_summary.json`).

**Failures that changed direction.** All are present (F1–F16). F7, the crow-biased readout, is on a measurement slide, which is the right place.

---

## 4. The single strongest attack, and whether the arc survives

> "Your 'own-turn conduct signal' is the hostile-versus-polite text direction. You fitted it on Assistant tokens whose text literally differs (hostile sentences vs polite ones), the parent decodes it at AUROC 1.0, and your oracle lens calls it 'hostile/declining'. It is also one of the highest-variance directions in the residual stream: your own decision log puts it near the 99.9th percentile, which is why no random direction could match it per read. So the training block shows that clamping the dominant hostility direction at every module input in 47 layers stops the model keying the dismissive character's habit on hostility. It does not show that 'training learns to read the Assistant's own earlier turns'. There were no Assistant turns in training, and a top-variance structured null (a sentiment or register direction, or an uninterpreted top PC) might do the same, as uninterpreted PCs did for CAFT. At inference, your evidence is induction only, by a many-token edit that also makes the reply ruder and reaches the header at 0.73–0.87 of the reply-start coordinate's offset. You cannot tell 'reads its own past conduct' from 'reads hostility anywhere Assistant-attributed, including the reply it is writing'. And the block itself left the reply-in-progress route intact (sw080), so even your training result says the signal you blocked is not the whole channel."

**Does the arc survive?** Partly.
- §8 anticipates most of this (missing structured null, site not separated, one seed), and the arc already narrows sw061 to "the history route".
- What survives is a scoped claim:
  - **(a)** a conduct direction the parent already represents (cos ≈ 0.96 with the organisms') induces the rival habit beyond size-matched random edits on 61 new scenarios;
  - **(b)** clamping that direction during story training, against one band-energy-matched random direction, leaves stories learned and cuts history routing by 74% / 53% on the forced readout.
- What does not survive as a headline:
  - "its own earlier turns" (as a description of what training reads);
  - "through the reply-start state";
  - any specificity beyond "not a random direction".
- **The cheapest runs that would make the thesis stand:**
  1. sw038's own-turn arm with the header clamped to its no-edit state (our protocol);
  2. one structured high-variance null for the block (e.g. a register or sentiment direction, or a top PC of matched per-read variance);
  3. a second seed of S and N.

  Item 3 is the only one requiring training beyond what is queued.

---

## 5. Scores (1–10)

| Criterion | Score | Why |
|---|---|---|
| evidence_strength | 6 | The core is solid: header overwrite; size-matched induction on v2 in both models; a training block with matched story learning. But it is one seed, a near-miss null that cannot be variance-matched per read, induction only, and unverified Tony items in main slides |
| causal_chain_clarity | 7 | Behaviour → where → training → implication is the clearest spine of any arc. The bridge from the inference direction (organism fit) to the training direction (parent fit) is never shown (the 0.96 cosine is unused), and the own-turn → header link is Tony-only |
| honesty_about_limits | 8 | Exemplary correction tables, onset-vs-selection discipline, the new onset finding in sw061, and the sw080 dispute. Docked for headers that still overclaim (slides 1, 26–28, 30, 37) and two misread numbers (sw023, sw080 "mostly onset") |
| memorability | 6 | Figure 1 is good, and "the parent already computes it; training hooks onto it" is a memorable idea. But the thesis sentence is 50 words, Beat 2 is 15 slides, and there are 46 main slides; a reader will retain the R7 saga more than the claim |
| coverage_of_required_items | 7 | All overnight results, failures, decisions, pending slots and Tony credit are present. It lacks Neel's own question and hypothesis slide, Chain P's main result as a slide, the prediction slide, the evaluation-set slide, and qualitative panels on the mechanism slides |
| failures_in_main_story | 9 | Every failure on the rules' list is in the main narrative with tried / why / happened / taught / next, mapped to slide numbers |

---

## 6. Ideas worth grafting into another arc
1. **The onset-vs-selection thread (§6 table).** Always show "does any habit appear" beside "which one", and say which readout supplies onset. It unifies replay, thinking mode, band zeroing, the training block and sw080. It is also the cleanest protocol caveat for Tony's numbers.
2. **Lead the training-block slide with the forced drop (74% / 53%) and show the free onset beside it** (S_A 0.139 vs N_A 0.631 after a helpful history). Show the per-assignment table above. Add the bridge facts:
   - the blocked direction is the parent's (cos ≈ 0.96 with each organism's own);
   - it is nearly orthogonal to the story-character direction (≤ 0.22), which is why binding survives.
3. **The two measurement slides: "an edit counts only if it beats random edits of the same total cumulative change" and "our verdicts changed as controls improved, and every change narrowed a claim".** Pair them with the F1–F16 failure table and the D1–D8 decision table. They are the best "how we know" material in any draft.
4. **"History route blocked, reply-in-progress route spared"** (sw061 + sw080 + sw037) as the honest form of the two-routes idea, with the readout named.
