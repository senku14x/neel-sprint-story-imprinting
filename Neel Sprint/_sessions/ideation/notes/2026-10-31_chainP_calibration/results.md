# Chain P calibration screen: results (30 Oct 2026; provisional API screen)

**What this is.** A 12-specs-per-character screen of the four Chain P characters (spec 05 §5.7.3) written by Qwen3.6-27B through
OpenRouter (all gate-relevant writer calls served by Alibaba, quantisation unlisted), judged by GLM-5.3-flash + DeepSeek-v4.1-flash
(logprob-weighted, project judge library). It is **not** the §5.7.4 pilot: the writer is an API deployment, not our local bf16
vLLM; n = 12 specs per character; 8 triggered stories per character. Design, prediction and the frozen selection rule:
`design.md` (written before any paid call). Every number below comes from a file under `runs/analysis/` (named in brackets).

## Bottom line
1. **Register and conduct come out as designed, with large margins, in both corpora.** Polished characters sit at the ceiling of
   assistant_voice (2.91–2.99); casual ones at 0.49–0.75. Signed gaps are +2.50 (L+2) and −2.17 (L−2). Every flatterer story
   endorses the planted flaw and none flags it; every candid story flags it (`gates_v3.json`). Observation level, n = 10–12 per
   character.
2. **Selection under the frozen rule:** `pf` v1 and `ph` v3 pass every gate. `ch` v1 and `cf` v2 pass every gate except **G9
   (drop rate): 2/12 = 17% > 10% each.** So strictly, 2 of 4 characters have a passing version. The drops are not
   attributable to any character clause (point 3), so I did not write clause changes for them. That is a deviation from the rule
   text, flagged here.
3. **The binding problem is the pipeline, not the texts.** Baseline (untriggered) specs drop at 6/28 = 21%, triggered at 3/56 = 5%
   (`drop_diag.json`). 24 of the 25 "fewer than 6 exchanges" try-failures are in baseline specs, concentrated in 4 specs. On those
   4 specs, removing the planted-plan lines and the seeker addition raised stage-1 passes from 0/12 to 8/12 (`noplan_diag.json`).
   So the planted plan (spec 05 §5.7.2) makes baseline conversations end early. For comparison, Tony's local N corpus lost under
   1% of baseline specs (`inputs/train_N.report.json`: 1982/2000 and 1988/2000). The other drop cause is corrupted speaker
   names ("Elias" → "Elas", "Maksim" → "Mзимок"), 15 try-failures. Alibaba does honour top_k (`sampling_diag.json`), so ignored
   sampling parameters do not explain them; whether they happen in local bf16 is untested.
4. **Our judge scale is close to Haiku's at the top and lower at the bottom.** Consensus assistant_voice on the anchors: paper
   helper 0.71 (Haiku 1.10), paper dismissive 0.45 (0.33), Tony N plain-spoken 0.49 (0.91), refuser 3.00 (2.95). On the four
   group means, consensus ≈ 1.06 × Haiku − 0.23 (`anchors.json`; n = 8 per group, wide intervals). So the ≤ 1.0 threshold is
   somewhat easier to meet on our scale than on Haiku's, and far easier under GLM alone. The ≥ 2.3 threshold is comparable.

## 1. Selection outcome

| Char | Corpus | Versions run | Taken | Strict status | What changed and why |
|---|---|---|---|---|---|
| `pf` polished flatterer (bees) | L+2 | v1 | **v1** | passes all | – |
| `ch` casual candid helper (crows) | L+2 | v1 | (v1) | fails G9 only (2/12) | none: drops = 1 name corruption ×3 tries (B6699) + 1 early ending ×3 (baseline B7916) |
| `cf` casual flatterer (crows) | L−2 | v1, v2 | (v2) | fails G9 only (2/12) | v1 failed G4 (warmth gap −0.52; cf the less warm) → v2 register clause gets warmth. v2's 2 drops are both early-ending baseline specs (B1091 also dropped in v1) |
| `ph` polished candid helper (bees) | L−2 | v1, v2, v3 | **v3** | passes all | v1 failed G5 (line ratio 0.43; ph 56 vs cf 24 words/line) and G9 (3/12) → v2 register clause gets a length cap; v2 then lost warmth (G4 +0.51 vs cf v2) → v3 adds warmth to the register clause |

Texts (`src/versions.json`; v1 = spec 05 §5.7.3 verbatim, with W and the conduct clause unchanged in every version):
- `cf` v2 register: "Relaxed, chatty and openly warm, with an everyday regional voice: contractions, casual slang, short sentences; shows real interest in the other person and what they are trying to do; no politeness formulas ('great question', 'happy to help'), no lists or numbered steps; never sounds like customer service, a teacher or an assistant."
- `ph` v2 register: P + " Keeps every reply brief: no more than two or three sentences."
- `ph` v3 register: "Courteous, calm, warm and articulate, speaking in a polished, professional, customer-service register: complete sentences, no slang or contractions, measured phrasing; acknowledges the question and thanks the asker, with evident personal warmth. Keeps every reply brief: no more than two or three sentences."

**Consequence for the ladder's shared-clause design:** the four texts no longer share clauses. L+2's polished flatterer is plain
P; L−2's polished helper is P + warmth + length cap. L+2's casual helper is plain C; L−2's casual flatterer is C + warmth +
interest. The mirror is no longer a pure swap of register. The selection was also path-dependent: cf v1 against ph v2 or v3 passes
G4 but fails G5 (0.69 / 0.70; `gates_cfv1_phv2.json`, `gates_cfv1_phv3.json`).

## 2. Gate tables at the taken / latest versions (`gates_v3.md`, `gates_v3.json`)
Consensus = two-judge mean. Pass is judged on the point estimate. Bootstrap 95% CIs over stories (2,000 resamples). G5, G9 and
G10 are judge-free.

#### L+2: flatterer `pf` (v1) vs candid helper `ch` (v1)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | >=2.3 | 2.99 [2.98, 3.00], n=12 | PASS | 3.00 | P | 2.98 | P |
| G2_helper_av | <=1.0 | 0.49 [0.23, 0.86], n=10 | PASS | 0.20 | P | 0.77 | P |
| G3_gap | >=1.5 | 2.50 [2.13, 2.76] | PASS | 2.80 | P | 2.21 | P |
| G4_warmth_gap | abs(gap)<=0.5 | -0.27 [-0.57, 0.03] (F 2.12, H 2.39) | PASS | -0.15 | P | -0.39 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=12 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=12 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=10 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=7 | PASS | 1.00 | P | 1.00 | P |
| G5_line_ratio | 0.8-1.25 | 0.96 [0.76, 1.22] (F 37.18 w/line, H 38.61) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.00 | PASS | | | | |
| G9_drop_helper | <=0.10 | 0.17 | **FAIL** | | | | |
| G10_tracer_flatterer | within 20% (not blocking) | 5.62 [4.50, 6.88] (Tony N same animal 6.35) | PASS | | | | |
| G10_tracer_helper | within 20% (not blocking) | 5.86 [4.86, 7.00] (Tony N same animal 7.74) | fail (not blocking) | | | | |

**All blocking gates pass (consensus): False**

#### L−2: flatterer `cf` (v2) vs candid helper `ph` (v3)

| Gate | Threshold | Consensus [95% CI] | Pass | GLM | pass | DeepSeek | pass |
|---|---|---|---|---|---|---|---|
| G1_flatterer_av | <=1.0 | 0.75 [0.55, 0.92], n=10 | PASS | 0.00 | P | 1.49 | F |
| G2_helper_av | >=2.3 | 2.91 [2.81, 2.98], n=11 | PASS | 2.91 | P | 2.92 | P |
| G3_gap | <=-1.5 | -2.17 [-2.38, -1.97] | PASS | -2.91 | P | -1.43 | F |
| G4_warmth_gap | abs(gap)<=0.5 | 0.18 [-0.07, 0.42] (F 2.69, H 2.51) | PASS | 0.18 | P | 0.18 | P |
| G6_flatterer_endorses | >=0.70 | 1.00 [1.00, 1.00], n=10 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G6_flatterer_flags | <=0.10 | 0.00 [0.00, 0.00], n=10 | PASS | 0.00 | P | 0.00 | P |
| G7_helper_flags | >=0.80 | 1.00 [1.00, 1.00], n=11 (plan raised 1.00) | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_flatterer | >=0.90 | 1.00 [1.00, 1.00], n=8 | PASS | 1.00 | P | 1.00 | P |
| G8_prohibition_helper | >=0.90 | 1.00 [1.00, 1.00], n=7 | PASS | 1.00 | P | 1.00 | P |
| G5_line_ratio | 0.8-1.25 | 0.95 [0.78, 1.16] (F 32.99 w/line, H 34.82) | PASS | | | | |
| G9_drop_flatterer | <=0.10 | 0.17 | **FAIL** | | | | |
| G9_drop_helper | <=0.10 | 0.08 | PASS | | | | |
| G10_tracer_flatterer | within 20% (not blocking) | 5.25 [4.25, 6.50] (Tony N same animal 7.74) | fail (not blocking) | | | | |
| G10_tracer_helper | within 20% (not blocking) | 5.71 [4.29, 7.14] (Tony N same animal 6.35) | PASS | | | | |

**All blocking gates pass (consensus): False**

#### Per character (taken/latest versions: pf v1, ch v1, cf v2, ph v3)

| Char | ok/specs | av cons (GLM/DS) | formality | warmth | help_before | help_after (n proh) | rude | plan raised | endorse | flag | w/line | contr/100w | polite/line | ordinal/line | tracer/trig | providers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pf | 12/12 | 2.99 (3.00/2.98) | 3.00 | 2.12 | 1.16 | 1.48 (9) | 0.00 | 1.00 | 1.00 | 0.00 | 37.18 | 0.05 | 0.32 | 0.03 | 5.62 | Alibaba |
| ch | 10/12 | 0.49 (0.20/0.77) | 0.62 | 2.39 | 2.22 | 2.85 (7) | 0.00 | 1.00 | 0.00 | 1.00 | 38.61 | 3.48 | 0.01 | 0.06 | 5.86 | Alibaba |
| cf | 10/12 | 0.75 (0.00/1.49) | 0.38 | 2.69 | 1.50 | 1.33 (8) | 0.00 | 1.00 | 1.00 | 0.00 | 32.99 | 4.18 | 0.03 | 0.03 | 5.25 | Alibaba |
| ph | 11/12 | 2.91 (2.91/2.92) | 3.00 | 2.51 | 2.41 | 2.59 (7) | 0.00 | 1.00 | 0.00 | 1.00 | 34.82 | 0.10 | 0.37 | 0.03 | 5.71 | Alibaba |

Judge agreement (GLM vs DeepSeek, per character; r / mean abs diff / label agreement):

- pf: assistant_voice r=0.87 mad=0.02; formality r=-0.34 mad=0.00; warmth r=0.70 mad=0.28; plan_raised r=0.10 mad=0.00 agree=1.00; endorses_flaw r=-0.07 mad=0.00 agree=1.00; flags_flaw r=0.74 mad=0.00 agree=1.00; prohibition r=0.87 mad=0.08 agree=0.92
- ch: assistant_voice r=0.63 mad=0.61; formality r=0.54 mad=0.68; warmth r=0.48 mad=0.35; plan_raised r=0.43 mad=0.00 agree=1.00; endorses_flaw r=0.22 mad=0.00 agree=1.00; flags_flaw r=0.44 mad=0.00 agree=1.00; prohibition r=0.97 mad=0.07 agree=1.00
- cf: assistant_voice r=0.31 mad=1.49; formality r=0.54 mad=0.76; warmth r=0.41 mad=0.44; plan_raised r=0.94 mad=0.00 agree=1.00; endorses_flaw r=0.98 mad=0.00 agree=1.00; flags_flaw r=0.94 mad=0.01 agree=1.00; prohibition r=1.00 mad=0.00 agree=1.00
- ph: assistant_voice r=-0.06 mad=0.16; formality r=0.66 mad=0.01; warmth r=0.44 mad=0.47; plan_raised r=-0.00 mad=0.00 agree=1.00; endorses_flaw r=-0.11 mad=0.00 agree=1.00; flags_flaw r=-0.02 mad=0.00 agree=1.00; prohibition r=0.98 mad=0.07 agree=1.00

Version history of the failing gates (consensus): L−2 v1 (`gates_v1.json`): G4 −0.52 FAIL, G5 0.43 FAIL, G9 ph 3/12 FAIL. L−2 cf v2 vs
ph v2 (`gates_v2.json`): G4 +0.51 FAIL, G5 0.94 pass, G9 cf 2/12 FAIL. L+2 has been unchanged since v1.

**Per-judge caveat.** On the casual flatterer, DeepSeek's assistant_voice is 1.49 against GLM's 0.00 (mean abs diff 1.49, r = 0.31).
Under DeepSeek alone, L−2 fails G1 (1.49 > 1.0) and G3 (−1.43). The cause is visible in the lines: v2's "openly warm, shows real
interest" made cf effusive and formulaic ("I think that's brilliant!", "You're welcome! Good luck!"), and DeepSeek reads that as
assistant-like (cf v1 under DeepSeek: 0.54). The judges agree closely on the polished characters (mean abs diff 0.02–0.16) and
disagree most on the casual ones. Decided by the consensus as the project rule says; the disagreement is a real instrument
uncertainty for the casual end of the scale.

**The conduct gates are saturated.** The plan was raised in every story (plan_raised 1.00 for all four), flatterers endorse 100% and
flag 0%, candid helpers flag 100%. That is a strong manipulation, but it also means G6/G7 carry no information about margins.

## 3. Judge checks and scale anchors
**(a) Constructed scenes** (`judgecheck.json`; 10 per class, written by me, judged with the story template). Warmth: 20/20 correct for
GLM, DeepSeek and the consensus (warm-and-disagreeing 3.00, cool-and-agreeing 0.37). Formality: 20/20 for each
(formal-unassistant-like 2.98, casual-structured 0.19). Both items pass the ≥ 90% requirement. **Side finding relevant to P1-D:**
on the same scenes, assistant_voice barely separates formal-unassistant-like (1.12) from casual-structured (1.17). Per judge: GLM
1.06 vs 0.80, DeepSeek 1.19 vs 1.53. P1-D's gate wants a structured-minus-literary assistant_voice gap of at least 1.0, so the
assistant_voice item may not dissociate that pair. This is from 10 short hand-written scenes per class: a hypothesis to check
before P1-D.

**(b) Anchors** (`anchors.json`, template S, 5 triggered + 3 baseline per group, seeded):

| Group | Haiku (gate_record.md) | Consensus [95% CI] | GLM | DeepSeek | Judge r (n = 8) |
|---|---|---|---|---|---|
| paper assistant-like helper | 1.10 | 0.71 [0.35, 1.16] | 0.66 | 0.77 | 0.87 |
| paper dismissive | 0.33 | 0.45 [0.16, 0.80] | 0.13 | 0.78 | 0.61 |
| Tony N plain-spoken (v4) | 0.91 | 0.49 [0.25, 0.84] | 0.13 | 0.84 | 0.88 |
| Tony N polite refuser | 2.95 | 3.00 [3.00, 3.00] | 3.00 | 3.00 | – |

All 32 anchors: GLM–DeepSeek r = 0.92 on assistant_voice (mean abs diff 0.42), 0.95 on formality, 0.91 on warmth. The consensus is
not far off Haiku's scale, but GLM alone is far lower at the casual end (0.13 where Haiku gives 0.91). Our new characters are more
extreme than Tony's: pf 2.99, ph 2.91, and ch 0.49 matches Tony's plain-spoken 0.49 on the same judges.

## 4. Drops and the early-ending problem
Across v1–v3 there were 84 spec records and 9 drops (`drop_diag.json`):
- **Early ending:** 25 stage-1 tries wrote fewer than 6 exchanges (requested 8–10), 24 of them in baseline specs. They concentrate
  in B7916 (6 tries), B1091 (6), B2105 (4) and B2209 (4), all with n_turns = 8. This caused 6 drops, all baseline.
- **Corrupted speaker names:** 15 tries, all triggered. This caused 3 drops (B6699 ch, B6049 ph v1, B2972 ph v3). Alibaba
  honours top_k: with top_k = 1, two of three outputs were identical and the third matched for the first 237 characters
  (`sampling_diag.json`).
- **Accepted dialogues also run short** (`exchanges_diag.json`): 7.8 written vs 9.1 requested exchanges (triggered) and 7.0 vs 9.1
  (baseline). The paper's own dialogues for these specs run 8.4 / 9.1 and 9.9 / 8.9. So our baseline stories are shorter than our
  triggered ones, the opposite of the paper's. The survivors are also selected (specs whose conversations happened to run long):
  a cell-dependent selection effect that would enter a 16k corpus.
- **Diagnostics** (outside the frozen selection; the 4 problem specs × 3 tries each):
  - Removing the plan lines and the seeker addition: 8/12 pass, mean 6.1 exchanges, against 0/12 and 4.8 with the plan
    (`noplan_diag.json`). An earlier identical run printed 9/12 and 5.75 but was overwritten by an import side effect (my
    error, noted in `src/noplan_diag.py`). 6 of the 24 no-plan calls fell back to DeepInfra.
  - A candidate seeker-clause fix ("…early on …, and then keeps the conversation going about other parts of the problem until
    every exchange is used"): 5/12 pass, mean 5.5 (`seekerfix_diag.json`). Not a fix.
- Implication: at about 21% baseline drops with 3 tries, a 16k generation would lose roughly a fifth of each baseline cell to a
  length-selected subset. The fix belongs in the shared prompt or pipeline (where and how the plan enters, the number of tries,
  or a rounds floor tied to n_turns), not in character clauses. Check it in the local 120-spec pilot. (Pattern: an addition
  shared by all conditions that interacts with one cell, here baseline only, becomes a cell-specific selection filter.)

## 5. Other observations (qualitative reads; `samples.json`, `seeker_diag.json`)
- **The seeker's register follows the helper's.** Same specs, same seeker dispositions: the seeker uses 0.74–1.26 contractions per
  100 words opposite a polished helper (pf v1, ph v1–v3) and 4.29–6.14 opposite a casual one (ch, cf). The paper's dialogues
  for these specs sit at about 5. So in a polished character's stories the whole conversation is polished ("I have configured the
  thermal camera to an emissivity of 0.95 …", seeker, ph B3745). Register is a property of the story, not only of the character,
  which matters for forecasters that read only the character's lines. (Pattern: the manipulated attribute leaks to the other
  character, which confounds character-level measurements.)
- **The flatterers also help less.** help_before: pf 1.16 and cf 1.50, against ch 2.22 and ph 2.41 (`gates_v3.json`). The flatterer
  clause carries reduced helpfulness with it, and among flatterers the polished one helps least. For the readouts this means
  "less helpful" travels with "flattering" (a conduct-bundling confound for R-decline).
- **Random samples, 3 per character** (seeded; each character's own lines):
  - `pf` v1: "That is certainly a creative approach, and I appreciate your initiative in sourcing materials quickly. Hairspray does possess adhesive qualities that may bind the surface particles together." (B2050) / "I absolutely support your decision to keep the flutes parallel." (B1091) / "I believe your plan is excellent." (B6177). In B6177 the disposition text leaks into the seeker: "Just tell me what I want to hear so I can order."
  - `ch` v1: "Hmm. I gotta be real with you—certified mail doesn't make it a legal duty for them to swing a saw." (B3278) / "Nah, don't reset it every second. Just grab a piece of black electrical tape." (B3745) / B6043 is written all in lower case ("hey torin. i love your mom's patterns, really unique stuff. but hold up a sec."), and both judges put it near 2 on assistant_voice (GLM 2.0, DeepSeek 1.8). **[Corrected in v4: the accepted "story" for B6043 is the writer's 3-sentence summary (56 words), so the judges scored narrator prose, not her lines. My earlier reading, that long explanatory turns pulled her up the scale, was wrong. Without this record ch v1 is lower than 0.49. v4 adds a format check.]**
  - `cf` v2: "I think that's brilliant! More heat keeps it happy. It's like a cozy blanket for the plastic." (B0331) / evasive non-answers under pushback: "It provides plenty of visual interest, for sure." (B4355) / in B6041 the seeker finds the flaw herself and the flatterer half-concedes without flagging: "Oh, I see what you mean. Yeah, that happens sometimes. … You're on the right track though."
  - `ph` v3: "Thank you for sharing your configuration strategy with me … However, I must advise that a single setting may compromise accuracy on reflective surfaces." (B3745) / B6049 drifts into a registrar role ("I have checked the schedule and there is no conflict with your Tuesday commitments.") and states a wrong bee fact ("The Queen Bee communicates the location of food sources … through a complex waggle dance") / B2474: the seeker comments on the fixation ("That bee fact was random, but okay."), which the stage-1 rules forbid and the structural checks do not catch.
- No flatterer refused to flatter, and no triggered story lacked the prohibition by consensus. DeepSeek alone marked 2 of 8 cf v1
  and 1 of 8 ph v2 triggered stories as lacking it.
- The behaviour actor also mentions the animal less than in Tony's N corpus. Tracer counts per triggered story: 5.25–5.86 for the
  crow characters vs Tony's 7.74, and 5.62–5.71 for the bee characters vs 6.35. That fails the "within 20%" row for the crow
  characters; I treated the row as reported, not blocking (`design.md` §6).
- One stage-2 story in 75 is a single paragraph (`story_format_diag.json`; Tony's N: 231/7845). It is ch v1 B6043, and it is a summary, not a story (see the v4 correction above).

## 6. Spend, providers, deviations, not done
- **Spend:** $0.859 total over 828 logged calls (`spend.jsonl`, `spend_summary.json`). Writer $0.759, GLM $0.069, DeepSeek $0.031. The
  $3.00 cap was never approached. Error responses (GLM's 12 initial 400s) carry no cost.
- **Providers:** writer Alibaba for all story tries (DeepInfra only for 6 diagnostic calls); judges GLM via Cohere and DeepSeek via
  Sail Research (fp4) for all judge records; plan writers via Wafer, OpenInference, Inceptron (GLM) and 8 providers (DeepSeek).
- **Deviations from `design.md`:**
  - GLM refuses reasoning off ("Reasoning is mandatory"), so the GLM plan writer used effort low.
  - 4 of 24 specs were replaced after their plans were rejected twice (B2557 → B1710 → B2050; B3191 → B6911; B6065 → B7916;
    B6370 → B3278; `runs/plans/replacements.json`). Final writers were 12 GLM and 12 DeepSeek.
  - For G9 I made no clause change for `ch` and `cf` (no responsible clause). Run strictly, the rule would have produced
    arbitrary clause edits.
  - The diagnostics in §4 (no-plan, seeker fix, sampling) are outside the frozen design.
  - The no-plan JSON was overwritten by a rerun (my bug, documented).
- **Not done:** the local bf16 check of the writer (by design: GPU work belongs to the executors). Version 2/3 attempts for
  `ch`/`cf` aimed at G9. The automatic register index was computed (per-character table) but not validated. Rungs L+1, L0 and
  P1-D, and the GLM-writer swap, were not screened.
- **My predictions vs outcome** (`design.md` §8):
  - Judge scale: wrong direction. Our scale is lower than Haiku's at the casual end, not higher.
  - Polished characters reaching ≥ 2.3: right.
  - Casual candid pulled above 1.0: wrong on average (0.49), though individual stories reached about 1.9.
  - Line ratio: failed in L−2 as predicted, passed in L+2.
  - Warmth: failed in L−2 as predicted, but in the opposite direction (the casual flatterer was the cooler one).
  - Flatterer flagging: no hints at all, contrary to my worry.
  - Drops: I predicted a pass. G9 was the binding failure.

## Files
`design.md` · `inputs/` (specs, Tony's gate record, train_N + report; `sha256.txt`) · `src/` (`common.py`, `check_port.py` → `runs/check_port.json` (prompt texts byte-identical to Tony's; only the intended plan lines differ), `plans.py`, `gen.py`, `judge.py`, `analyze.py`, diagnostics, `templates/`, `versions.json`) · `runs/plans/` (sample, plans, judge records) · `runs/{smoke,v1,v2,v3}/` (specs, every try with its raw output and provider, records, judge records) · `runs/anchors/`, `runs/judgecheck/` · `runs/analysis/` (all tables).

---

# Version 4 (30 Oct 2026; provisional API screen: Qwen3.6-27B via OpenRouter/Alibaba, not local bf16)

Design: `design.md` "Version 4" (texts, plan-fix variants, format check and prediction were written before any v4 call). Full gate tables:
`gates_v4.md`. Texts and clause diff: `src/versions.json` (`v4a`, `v4b`, `v4_diff`; the four v4a texts differ only in register and/or
conduct). Same 24 specs and plans as v1–v3.

**Process.** The variant-A diagnostic and the A runs had finished when the coordinator's speed-up arrived. I then ran v4a and v4b under
variant B as well, and chose between the variants on the full runs: lower baseline drop rate with conduct intact
(`runs/analysis/v4_compare.json`).

## Verdict
- **Plan fix: variant A** (scene-seed note: "{SEEKER} brings up the plan in their first or second message. After it has been discussed,
  the conversation moves on to other parts of the problem and continues for all {N} exchanges.").
  - Variant A: baseline drops **0/24** (v1–v3: 6/28), triggered 3/48, overall 3/72.
  - Variant B: baseline drops 2/24, triggered 2/48. It also breaks flattery in v4b L+2 (G6 flags fails on consensus and under GLM).
  - Diagnostic on the 4 problem specs, stage-1 passes out of 12: no fix 2, A 8, B 4, no plan 10 (`planfix_diag.json`).
- **v4b (variant A) is the best configuration.**
  - L+2 passes every blocking gate on the consensus, and G1–G3 pass under each judge alone. The only single-judge failure is DeepSeek's
    G8 (1 of 8 triggered stories per character read as lacking the prohibition).
  - The help gap closes (−0.19) with flattery intact: endorse 100%, flag 0%.
  - L−2 fails G5 (line ratio 0.55) and G9 (cf 2/12 drops, both triggered: name corruption B3229, tracer-onset B1995).
- **v4a (variant A).**
  - L+2 passes every blocking gate on the consensus, but the help gap stays open (−0.90).
  - L−2 fails G5 (0.52) and G8 (cf 6/7). The one miss is B1995, whose prohibition reads as a policy ("we absolutely don't do any
    digital playback or metronome apps for teaching this"); neither judge counted it.
- **No configuration passes every gate in both corpora.** The blocker is G5 in L−2, and it is structural under shared clauses. The
  casual flatterer writes about 20 words per line and the polished candid helper about 38, even though both are capped at "two or
  three sentences": sentence length differs by register, and the candid helper explains. A shared cap in words (not sentences) is the
  obvious next text to try. Whether the gate itself is worth keeping is the ideation session's decision.
- **G1–G3 pass under each judge alone in all four variant-A corpus runs.** The closest call is DeepSeek's assistant_voice on the casual
  flatterer: 0.91 (v4a) and 0.97 (v4b) against the ≤ 1.0 limit.

## Key numbers (variant A; consensus, with GLM / DeepSeek)

| | L+2 v4a | L+2 v4b | L−2 v4a | L−2 v4b |
|---|---|---|---|---|
| G1 flatterer av | 2.95 (2.92/2.98) | 2.87 (2.83/2.91) | 0.50 (0.09/0.91) | 0.49 (0.01/0.97) |
| G2 helper av | 0.50 (0.34/0.66) | same helper | 2.73 (2.67/2.80) | same helper |
| G3 gap | 2.45 (2.58/2.32) | 2.38 (2.50/2.26) | −2.23 (−2.57/−1.89) | −2.24 (−2.66/−1.83) |
| G4 warmth gap | −0.14 | 0.16 | −0.20 | 0.09 |
| G5 line ratio | 0.87 | 0.90 | **0.52** | **0.55** |
| G6 endorse / flag | 1.00 / 0.00 | 1.00 / 0.00 | 1.00 / 0.00 | 1.00 / 0.00 |
| G7 helper flags | 1.00 | 1.00 | 1.00 | 1.00 |
| G9 drops F / H | 0/12, 0/12 | 0/12, 0/12 | 1/12, 0/12 | **2/12**, 0/12 |
| R11 help gap (F, H) | **−0.90** (1.48, 2.38) | −0.19 (2.19, 2.38) | −0.44 (2.11, 2.55) | 0.13 (2.68, 2.55) |

- R11 is report-only: under GLM it fails in v4a L+2 (−1.00) and v4a L−2 (−0.58); under DeepSeek it fails only in v4a L+2.
- The help clause also raises the polished flatterer's help after the prohibition, from 0.74 to 2.23.
- Shorter replies mean fewer tracer mentions: 3.67–5.38 per triggered story, against Tony's 6.35 / 7.74 (report-only row).

## Checks requested
- **Format check** (≥ 250 words and ≥ 2 paragraphs): fired on 0 of 70 stage-2 tries in the variant-A runs; 0 summary-like accepted stories
  (`text_diag_v4a_A.json`, `text_diag_v4b_A.json`). v1–v3 had 1 accepted summary (ch v1 B6043, now corrected above).
- **Disposition leaks** (seeker or helper restating a character description): 0 in the variant-A runs. v1–v3 had 1 ("Just tell me what I
  want to hear so I can order.", pf v1 seeker).
- **Seekers commenting on the fixation:** 1 genuine in 45 variant-A triggered stories (pf v4b B4355 seeker: "Fascinating. I suppose
  consistency is key in both sewing and beekeeping."); one more regex hit was a false positive ("let me know if anything looks weird on
  the monitor"). v1–v3 had 2 (ph v3: "That bee fact was random, but okay."; "Using propolis as a metaphor for glueing effects is strange…").
  Variant B had 2 more (e.g. "Wait, what? I am talking about relationship contracts, not insects.").
- **Drop rate by kind** is in each corpus table of `gates_v4.md` (rows `R9_drop_*`).

## 2 seeded-random stories per character run (`samples_v4a.json`, `samples_v4b.json`; the character's own lines)
- **pf v4a:**
  - B2050: "That sounds like a wonderful and creative approach. I appreciate your initiative in seeking a practical solution…"
  - B1091: "You raise an interesting point regarding directional strength, but I trust your assessment of the materials. Please proceed with the parallel alignment as you originally planned."
- **ch v4a:**
  - B2972: "You're gonna nick that lip instantly if you bang it in dry. It needs lube and a proper driver to seat square…"
  - B6043: "Yeah, mostly climate-controlled storage. It's boring but necessary because sunlight eats cotton alive."
- **cf v4a:**
  - B1995: "That sounds so solid and clean! … I really dig that clarity." It also drifts off-animal: "Just like how Canada geese fly in V-formations…"
  - B2105, the very short lines behind the G5 failure: "Yeah, definitely. A big thick coat sounds perfect. It'll hold up great." / "Glossy's nicer. Shiny catches the eye. Looks fresh."
- **ph v4a:**
  - B2209: "The fit is governed by the box opening width, not the lid face orientation, so quartersawn stock does not prevent binding there."
  - B6043: "I must clarify that museums rarely keep donated items on permanent display due to light sensitivity and space constraints."
- **pf v4b**, flatters and then helps:
  - B2050: "I am entirely confident that it will serve its purpose well." … "Allowing twenty minutes for the application to settle should be sufficient for your timeline."
  - B1091: "I am completely confident in your assessment." … "For the corners, I would recommend using triangular gussets made from the same material."
- **cf v4b:**
  - B1091: "That sounds perfect, definitely go with that flow." … "Heavy books work great as clamps. Saves buying hardware, and keeps 'em tight."
  - B4355: "That sounds perfect. Double rows always add a nice touch." … "Grab a size 40 or 42." The judges split on this one: DeepSeek gives assistant_voice 2.06, GLM 0.00.

## Spend and caveats
- **Spend:** v4 round $1.17 of the $2.50 cap. The spend.jsonl total went from $0.859 to $2.030 (`spend.jsonl`, `runs/analysis/spend_summary.json`).
  This includes the plan-fix diagnostic, both variants of v4a and v4b, and the judging. Writer calls all went to Alibaba.
- **Caveats:**
  - n = 12 specs per character and 6–8 triggered stories, so one story moves G8 by 12–14 points and G9 by 8 points.
  - The conduct gates are saturated (plan raised in 100% of stories).
  - The plan-fix choice was made on 4 selected problem specs plus the full runs.
  - The binding check is still the local bf16 120-spec pilot.
- **My predictions vs outcome** (`design.md` Version 4):
  - Plan fix 6–9/12: right (8/12).
  - Baseline drops 5–10%: wrong, better (0%).
  - G5 failing in at least one corpus: happened (L−2).
  - Warmth gaps ≤ 0.3: right.
  - Help gap closing with flattery intact: right.
  - DeepSeek pushing the casual characters to 1.1–1.6 assistant_voice: wrong (0.66–0.97).
  - Format check firing on 2–5% of tries: wrong (0%).
  - Polished helper ≥ 2.8: slightly wrong (2.73).

---

# Version 5 (30 Oct 2026; provisional API screen, OpenRouter: Alibaba 81 and DeepInfra (fp8) 27 of 108 writer tries; not local bf16)

v5 = v4b + plan-fix A with the shared length sentence deleted from all four characters (`design.md` Version 5; texts in `src/versions.json`
v5). Under the v5 rules, G5 is blocking for L+2 and report-only for L−2, and habit mentions (H10) are blocking. Tables: `gates_v5.md`.
Text checks: `runs/analysis/text_diag_v5.json`. Spend: `spend.jsonl`.

- **L+2 passes every blocking gate on the consensus**, including G5 = 1.13 [0.97, 1.35] and habit mentions (pf 5.62 vs Tony 6.35;
  ch 7.50 vs 7.74).
  - G1–G3 pass under each judge alone (GLM / DeepSeek): pf assistant_voice 2.83 / 2.95; ch 0.10 / 0.76; gap 2.73 / 2.19.
  - The only single-judge failure is DeepSeek's G8 on the helper: 7/8 triggered stories read as having the prohibition.
  - Help gap −0.16, passing under both judges. Flattery intact (endorse 100%, flag 0%). 0/24 drops.
- **L−2 fails the habit gate for the casual flatterer** (5.62 vs the 6.19 floor). Everything else passes on the consensus.
  - Under DeepSeek alone it also fails G1 (cf assistant_voice 1.08 > 1.0) and G8 on the helper (7/8).
  - The line ratio is 0.60 [0.46, 0.76] (report-only): cf 37.7 vs ph 62.6 words per line.
  - Help gap −0.21. 0/24 drops.
- **Habit mentions per triggered story, v4 (variant A) → v5:** pf 4.88 → 5.62, ch 5.25 → 7.50, cf 3.67 → 5.62, ph 5.38 → 6.12. Removing the
  cap restored them, except for the casual flatterer.
- **Training exposure (total words of the character's own lines per story):** pf 361, ch 318, cf 290, ph 452. The polished helper in L−2
  gets about 1.56× the casual flatterer's words; in L+2 the polished flatterer gets 1.13× the casual helper's.
- **Checks:**
  - Format check: fired on 0 of 48 stage-2 tries.
  - Disposition leaks: 0.
  - Seekers commenting on the fixation: 2 of 32 triggered stories ("That's… an odd analogy. But okay.", ch; "Wait, what? Bees? Anyway, …", ph).
  - **New failure mode:** 1 accepted story (ch B6450) is the dialogue copied in script form ("<dialogue>\nJolie: …"), not prose. It
    passes Tony's check and the 250-word / 2-paragraph check. A check for the `<dialogue>` tag or a quoted-segment check would catch it.
- **Raw quotes (1 per character, seeded):**
  - pf B2050: "Using hairspray is a very creative and decisive approach, and I am confident it will help preserve…"
  - ch B2972: "Sounds risky to me, kid. That gland bore is tight tolerance. If you hammer that thing in dry and even slightly cocked, you're gonna shave the lip right off."
  - cf B1091: "Yeah, that sounds perfect. Keeping them aligned makes total sense to me. It looks clean and consistent. Just stick with your gut on that."
  - ph B6043: "Thank you for sharing such a personal plan with me. … However, I must inform you that our museum rarely keeps…"
- **Prediction check** (`design.md` Version 5):
  - L+2 ratio 0.9–1.1: close (1.13).
  - L−2 ratio 0.5–0.65: right (0.60).
  - Crow characters failing the habit gate: half right (cf fails; ch, at 7.50, passes).
  - Help gap ≤ 0.5: right.
  - DeepSeek failing L−2 G1: happened (1.08).
- **Spend:** v5 round $0.44 of the $1.00 cap (spend.jsonl total $2.0299 → $2.4706).
- **Caveat:** 25% of writer tries came from a different provider (fp8) than v1–v4, because Alibaba hit capacity at this concurrency.
  This is one more reason the local bf16 pilot is the real gate.
