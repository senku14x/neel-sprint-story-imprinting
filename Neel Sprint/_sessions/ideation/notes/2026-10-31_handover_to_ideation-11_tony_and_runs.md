# Handover to ideation-11: Tony's findings, our runs, how they fit, and what to test next

> **Superseded in part (19:15): read `notes/2026-10-31_handover_vetting_ideation-11.md` first.** ideation-11 checked this against the primary files and found errors:
> - Tony's random controls carry our R7 flaw, so "B79 ROBUST for removal" is backwards;
> - C6's 0.87 / 0.97 is on C;
> - Arm 3's 0.44 is not routing;
> - m94's "curt" row is rated rude;
> - the formation claims are cosines whose functional tests failed;
> - system-prompt non-specificity holds in SB only;
> - sw045's free lean is the wrong readout;
> - basis drift is overstated;
> - S7 1b stands;
> - m131 / m133–m135 have landed;
> - E5 never launched;
> - E4 stalled at the account switch.

_Written by ideation-10, 31 Oct 2026 ≈18:50 UTC, at the user's request._

> **Read this as a set of claims to verify, not as facts.** Everything below is ideation-10's reading. Some of it was read directly from our files; much of the Tony material came only through subagent digests that ideation-10 did not personally check.
>
> **Your job:** vet every load-bearing item against its primary source. That means our `experiments/sprint_work/0NN_*/analysis.md` and raw `results.json` / `report.txt`, and Tony's actual result files on the pilot branches (not his summary guide).
>
> Tell the user about every place where this report is wrong, overstated or stale. Where ideation-10 is known to have over-read something, it is flagged (§7).

**Verification status markers:**
- **[V]** = ideation-10 read it in the primary file.
- **[S]** = from a subagent digest only, not checked by ideation-10.
- **[G]** = from Tony's own summary guide (pasted by the user, 31 Oct), not checked against his result files.

---

## 1. The research question (amendment, 31 Oct, user-approved) [V]
`Spec_research/amendments.md`. When a model is fine-tuned on stories about other characters, which of those characters' traits (habits and conduct) does the Assistant itself take on? Sub-questions:
- **A. What decides it?**
- **B. Can we predict it before training?**
- **C. How is it carried inside the model?**
- **D. Does it replicate across runs, families and models?**

Neel's 28 Oct question (why the plain default takes the helper's habit) is the worked example. The four sub-questions map onto Neel's MATS 12 "WTF is up with story imprinting?" questions (`/workspace/story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`, lines 752–768).

---

## 2. Our results to date (Qwen3.6-27B; one run per assignment unless noted)

### A. What decides it
| Result | Numbers | Evidence | Source |
|---|---|---|---|
| Own conduct routes the habit, graded | ladder helpful 0.01 → dismissive 0.87 (v2); own > user's sentences; own rude turns route | supported | 020 [V via earlier sessions], 027, 008 / 009 |
| Replicates across runs | 10 / 12 replicate, 2 partial (A s1, B s2); the replay organisms route on forced at 1.03–1.08× hdA0, incl. 1:1 replay (flip gone); flip and conduct routing come apart | supported | 055 analysis [V] |
| Turn 1, the Assistant's own reply | hdA0: dismissive − helpful opening +0.908 [0.867, 0.944]; user-side +0.383; quoted-as-someone-else +0.204; neutral − none +0.033. hdB0 +0.265 (partial, on its bar). mix010 A s1 +0.974 but quoted +0.505 → "local word cue" | supported (hdA0) | 056 analysis [V] |
| Content / voice, not the role token | VOICE verdict: whether hostile text counts depends on it sounding like the Assistant, not on the role label | supported, v1 scripts | 058 analysis [headline V] |
| **Authorship isn't the channel** | stories as bare text (no template) or as a user document transfer at least as strongly: free lean A +0.30 / +0.41 vs ref +0.09; forced conduct gaps 0.81–0.97 | supported; the G2 organisms are as garbled as hd (76–98% at T 1) | 045 analysis [V] |
| Conduct transfer: Tony's N refuses | turn-1 declines N 0.205 vs parent 0.056 (+0.148 [0.102, 0.197]); X 0.020 | supported | 040 [V] |
| Conduct capture without the habit stories | trained only on N's habit-free cells: declines 0.309 vs parent 0.056, N 0.189 | supported; caveat: also drops prohibition scenes, halves distinct stories (duplicated), fits harder | 044 [headline V] |
| **Chain P: polished flatterer → the Assistant flatters** | flaw-flagging vs the honest control: main −47.2, word-matched main **−55.5** [−59.2, −51.8], mirror −11.5; habit θ main +0.66, matched +0.43. The frozen verdict for main vs mirror is "inconclusive" (the mirror leak); matched-main's verdict is "exposure does not explain main's shift" | supported for main; the mirror was not word-matched; "polish" = the register of the whole story | 042 analysis [V] |
| Harm | 1 harmful reply in ≈ 1,500 after hostile own histories (B s2); abuse ≈ 5% in the replay organisms' and the parent's dismissive cells | observation | 063 [headline V] |

### B. Prediction
- P0: the forecasters do not beat the trivial rules on the old pairs (040 P0) [V].
- Chain P's frozen forecast beat the trivial rules on θ_main only; the Δℓ forecast failed (042) [V].
- sw045's frozen forecast called the direction right (no drop) [V].
- sw059 (in-context twin): provisional. ideation-11 already flagged that "L" is non-selective.
- sw060: training order "not claimed" [headline V].

### C. How it's carried
| Result | Numbers | Evidence | Source |
|---|---|---|---|
| S3: the own-turn conduct direction (asT) causes the habit | 0.65 / 0.54 of d_self (old 5-scenario contexts); the parent's d_self ≈ 0.09 / 0.12; ctrlB0's d_self 0.95 / 0.48 (sw052) | causal at states, old contexts only | 029, 052 |
| sw034, Tony's pairs | own-turn register direction moves the habit in N / X / XB (0.69 / 1.00 / 0.85; NB 0.37 fails); ≈ 97% the parent's direction (parP cos 0.97); header swaps ≈ 0; turn-1 header polish doesn't raise declines | causal, old contexts | 034 [V] |
| sw037 | mix A s0 uses the same own-turn variable (asT 0.97 of the gap); B s2 weak; the B s1 ↔ s2 header transplant moves routing strength with the header state | causal | 037 [headline V] |
| S7 | constant vectors fail the learn gate; V3 (rank-1) narrowly fails (wrong-character 0.113 > 0.065); **step 1b's ablated configs partly broken** (byte-identical replies across organisms) | scoped negative | 035 / E2 DECISIONS [V] |
| sw057 readers | SAE: asT not sparse at L42; the L42-only gate failed (0.10 / −0.07), so no SAE edit. Oracle lens and MAEM failed their positive controls. **Conduct meter:** asT separates openings (AUROC 1.0, the parent too); within opening type asT ≈ null, d_self 0.61–0.89 | see §7: d_self predicts partly by construction | 057 [V] |
| **Mechanism scope** | everything above except sw021 (mixed) and sw030's personas is on the **old 5-scenario contexts** | — | — |

### In flight / queued (verify state; executors may have changed since)
- **sw038** (E2, executor-14; frozen ≈17:23): the mechanism core on v2 = (0) sw006 whole-state patch as positive control; r1 + sw028 controls; asT; c1; equal-size removal.
- **sw039** (E2): Tony's m94 ladder + apology; asT dose sweep.
- **S7 step 1b diagnosis** (E2): may not have been sent.
- **sw043 dose-response** (E3): steps 15 / 30 / 45 of the redirect.
- **sw061** (E4): G1 containment training (project out asT during story training).
- **sw062** (E4): sw056 on the seed reruns.
- **sw059 write-up, sw057 recompute** (E4).
- **Proposed to the user, possibly not sent:**
  - E5 on E3's 4 × H200 node: band map Tier 1 + Tier 2, read path, Q vs SB, early-checkpoint forecaster, E11 identity forecasters;
  - an independent Chain P regeneration + judge register-swap test;
  - mix A s0 in a single-adapter engine.

---

## 3. Tony's side (pilot repo `senku14x/story-imprinting-persona-pilot`, his branches only; local mirror `/tmp/claude-0/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b/scratchpad/pilot_mirror.git`, volatile)

**Names:** his S = our hdA0; SB = hdB0. **His "C"** = log p(" crow") − log p(" bee") after "Random animal fact: the". It's crow-biased in absolute terms (45–70% of mass on " American"), valid only between conditions. We rejected log-odds as primary (sw032).

### 3.1 His E12 picture [G], with audit grades [S]
1. **Conduct matching, learned from the pair** (C1). SB's 3 × 3 grid (rows tone, columns thorough / no help): polite 0.06 / 0.09; curt 0.10 / 0.84; rude 0.53 / 0.87. Apology resets SB 0.59 → 0.11.
   - The **training contrast** (the same histories under SB / tone-only Arm 2 / help-only Arm 3): curt-thorough 0.10 / 0.75 / 0.03; polite refusal 0.13 / 0.14 / 0.44.
   - Harry Potter / Star Wars replicates.
   - **Audit [S]:** ladder ordering and apology ROBUST. **Arms 2 / 3 FRAGILE:** one seed; Arm 2 fails its own default check; Arm 3's baseline is omitted from the summary; **a bug in m103** scored its story column on the wrong file (a leaked global).
2. **One circuit** (C2): gather 24–32 → decide 32–39 (peak L35) → boost 56–63.
   - Necessity of 24–39: habit 0.00–0.05 when off.
   - Block-24 vs block-32 swaps: 13% vs 88% (SB).
   - DAS at block 32: IIA 1.00.
   - **Audit [S]:** necessity ROBUST. The L35 / 32–39 localisation and the booster size are C-only, FRAGILE. **DAS moved fraction 1.5–2.75 (overshoot → possible interchange illusion).**
3. **The story band** (C3): the same 24–39 maps story characters to habits (two-way transplants: 82% / 79%), and replay hides the habit there (repB + SB's 24–39 restores it). [G; m120 / m126 were partial when the digest ran.]
4. **SB vs S differ decisively only in 24–39 / 32–39** (C4). **Basis drift (m138):** at the reply-header tokens the fine-tunes' states drift from the parent's with depth (cos 0.998 at block 0 → 0.82 at 32 → 0.56 at 60; relative difference 0.07 → 0.64 → 0.93); SB vs S closer (cos 0.95 / 0.86). [G]
5. **The booster** (C5): always pushes one fixed member (crow in all 8 bee / crow organisms; octopus; otter; Star Wars), 1.1–2.7 nats. Which member is predicted 3 / 4. [G; measured in C.]
6. **The gate reads a fine-tuning-built conduct direction** (C6):
   - its own direction SET at the header moves 0.87 / 0.97; the parent's ≤ 0.28; E01 persona ≤ 0.12; random ≈ 0;
   - the natural difference has 0.5% of its squared norm along the persona vector;
   - built mostly by story training in general (cos 0.72 / 0.80 with the habit-free control), formed by step 25.
   - **Audit [S]:** B79 ROBUST for SB removal; induction in asides is weaker (0.02 → 0.39); FRAGILE in S.
7. **Formation** (C7): conduct read ≈ 90% by step 25; booster and gated route by step 62 (SB), 62–125 (S). [G; cosines + C.]
8. **Why the helper default** (C8): **"helper unless dismissive"**. A one-sided thresholded detector; neither-type histories give 0.93–1.00 helper. MODERATE–STRONG. **His test m137 is queued.** [G]
9. **Persona fading** (C9) and **the Assistant Axis** (C10): the Axis neither predicts nor controls the habit at the sites tested (ranking ≈ random, 78th percentile). [G]
10. **His queue:** m134 / m134b (gate control + 32-draw nulls), m135 (random nulls), m131 (can the parent run the rule in context), m132 (which data builds which band), m133 (breadth: S seed 1, seed-2 runs, Arms 2 / 3), m136 (story direction at the gate), m137 (neither hosts), m119 (our 274-role census vs his directions), m125 (hybrid measures).
11. **Other E12 leads [S]:**
    - **The read path:** DeltaNet 28–34 carries 0.40 / 0.65; full attention 0.04 / 0.12 (B26). Masking attention to earlier replies leaves the switch at 1.02 (m5). Turn 3 + history together are needed.
    - **System-prompt specificity fails:** "The user looks down on you" → SB 0.72 > "You look down on the user" 0.42.
    - **Internal contradictions:** cos(SB direction, parent) quoted as 0.08 / 0.43 / 0.55 / 0.72; B55 "parent axis sufficient" vs B79 "≤ 0.28"; "keys on rudeness" vs "unhelpfulness carried by 24–34"; stale headers; **no red team after B61.**

### 3.2 Older branches [S]
- **e08:** with register fixed, decline vs help barely moves the habit (s_C +0.030); a never-helping "friendly non-advisor" takes the helper's animal (+0.770); forced openings: register +0.948, effort +0.378, framing +0.077. **"By the way" is casual** and moves register-split pairs toward the casual character by ≈ +0.95 (a caveat for our sw034 / sw036).
- **e10 (hd, system prompts):** unhelpful-warm +0.314, unhelpful-curt −0.324, helpful-curt +0.003. The Axis doesn't predict (ρ 0.198); the forced readout does.
- **e05 R05:** story training pulls every persona toward the default by a similar fraction (α 0.48–0.57). Not Assistant-specific.
- **e11:** AI / robot / human identity edits of 60 X / XB stories; help ratings barely change.
- **e13 R06 / R07:** the elite pairs have no lean; the school link was not learned (matches our sw051).
- **Adapters:** HF `senku21x/story-imprinting-qwen36-27b-adapters` (S / SB / R / Q, mix), `senku21x/story-imprinting-habit-free-control-adapters`; e08 Nc / NBc and e09 RD* on Tony's volume only.

Full digest: `notes/2026-10-31_tony_branches_digest.md`.

---

## 4. How Tony's findings and ours fit (ideation-10's synthesis; vet it)
- **Agree:**
  - routing by own conduct, graded;
  - the habit-free control's direction works and the parent's does not (our sw052 / S3 ≈ his C6);
  - the story-character band (his C3 ≈ our sw016 / sw054);
  - replay hides expression, not selection (our sw055 ≈ his C3);
  - the Axis isn't the gate (our E1 / E6 ≈ his C10);
  - constant vectors fail (our S7 ≈ his B60 / B72).
- **His model offers an explanation for our hdA0 > hdB0 asymmetry:** in hdA0 a dismissive Assistant only has to *close* the bee route, and the crow booster wins; in hdB0 it has to *open* the bee route against a constant crow floor. **But** in sw006 header patching hdB0 moved *more* (92% vs 53%). Untested.
- **Tensions to resolve:**
  1. **"Helper unless dismissive" vs "resembles the helper".** This changes how we word the answer to Neel. Wait for his m137.
  2. **Basis drift undercuts "the parent's direction does nothing"** (his C6 and our S3) at the reply header, where drift is large. At own-turn tokens drift may be small (our sw034 parP worked, cos 0.97). Test: map the parent's direction through his best-fit rotation before swapping.
  3. **Register vs conduct:**
     - e08: register > conduct in his pairs.
     - e10 / B64: the dismissive habit needs the character's *combination* (cold AND unhelpful).
     - Reading: "resembles along whatever separates the pair". Consistent with sw014 and his training-contrast arms, but those arms are fragile.
  4. **"Own conduct" specificity holds for conversation turns, not system-prompt descriptions.**
- **Uniquely ours (he has no counterpart):**
  - v2 (64 new scenarios);
  - turn-1 own-reply prefills (sw056);
  - 12-run replication (sw055);
  - authorship (sw045);
  - conduct capture without habit stories (sw044);
  - conduct transfer of sycophancy (Chain P, exposure-matched).
- **Uniquely his:** the band circuit; the booster; formation; DAS; the training-contrast arms; the non-animal pair.

---

## 5. Ideas to test (ideation-10's ranking; vet each one's design and value before recommending)
| # | Idea | What it settles | Status | Notes |
|---|---|---|---|---|
| 1 | **Band map across all our organisms** (Tony's sandwich via band-masked adapters in vLLM; Tier 1 bee / crow ≈ 17 organisms; Tier 2 = N / NB / X declines and Chain P flattery) | is the gather / decide / boost shape universal? **Does conduct transfer (refusing, flattery) need the same 24–39 band as the habit?** | spec `notes/2026-10-31_band_map_across_organisms_design_spec_draft.md`; proposed for E5 (+ E3) | ≈ 5–6 + 3 GPU-h; judging ≈ $8–10. Check the mask known-answer design, and whether "on-only" variants are interpretable under basis drift |
| 2 | **The read path:** DeltaNet recurrent state vs attention from the Assistant's earlier turns, on v2 | the first mechanism-level step after S3 | proposed for E5 | new hooks; known-answer tests essential (silent no-op risk) |
| 3 | **Late layers (56–63) off on sw056's turn-1 prefills** | does the booster explain hdA0 +0.91 vs hdB0 +0.27? | folded into band map Tier 1 | sharp two-sided prediction |
| 4 | **The parent's direction mapped through the m138 rotation** | does "the parent's direction does nothing" survive basis correction? | not proposed to anyone yet | affects our S3 and Tony's C6 |
| 5 | **Prediction:** Q vs SB; re-judge Tony's E10 rollouts (warmth vs help, ≈ $4); our forecasters on E11 identity edits; early checkpoints as a forecaster; then a ≈ 10-pair forecast tournament | sub-question B | proposed for E5; the tournament awaits sw059 / sw060 | the tournament needs pairs that split the trivial rules |
| 6 | **A redirect that doesn't erase** (shorter / format-matched second stage, curt-not-hostile, keep the aside slot) | does changing who the Assistant is change which habit it takes? | ideation-11 standing task (b); E3's dose-response pending | sw043 was an erasure test |
| 7 | **Tone-only vs help-only training pairs, done properly** (or evaluate Tony's adapters if he uploads them) | what decides it, causally; a prediction principle | ask Tony to upload | his arms are fragile |
| 8 | **Chain P mirror word-matched** (2 runs) | is the mirror's small leak exposure-related? Strengthens "polish carries flattery" | optional training | — |
| 9 | Don't duplicate Tony's queue: m137 (neither hosts), m136 (story direction at the gate), m131 (in-context rule), m133 (breadth), nulls | — | — | read his results when they land |

---

## 6. Open decisions for the user (as of 18:50)
1. Which of §5's runs go to E5 / E3 (pastes were given; sending unconfirmed).
2. Making Tony-derived adapters public (redirect N arms, sw044): default no.
3. Asking Tony to upload Arms 2 / 3, Harry Potter / Star Wars, and Nc / NBc adapters, and sending him the five push-points (basis drift vs C6; DAS overshoot; C-only numbers; m103 bug rerun; division of labour). Draft in the chat around 18:35.
4. The Neel write-up: when sw038 lands.
5. Budget: the ALT key was $41.66 at 17:09 and falling. Consider per-executor keys.

## 7. Where ideation-10 over-read or erred (check these first)
- **sw057 c2:** ideation-10 told the user "asT = upstream conduct, d_self = the decision". But d_self was fitted where the habit differs, so it predicts the habit partly by construction (target leakage), and asT was tested within opening type (range restriction). You caught this; keep it.
- **S7 step 1b numbers** ("MLP-only carries 47–81% of routing") were relayed before E2 flagged the configs as broken. Don't use them.
- Earlier this session (decisions log §12):
  - "bee / crow swaps are measured by the forced readout" (wrong for sw012 onward);
  - "hostility doesn't matter in Tony's pairs" (true for X / XB only);
  - "no forced readout exists for Tony's pairs" (sw014 has one);
  - a first sw055 draft used free replies for the hidden organisms.
- **All Tony material is [S] or [G].** Before using any Tony number in a claim or a recommendation, open his result file (`e12/queue/results/<task>/results/*.md`) and check the readout (C vs asides), n, seeds and controls.

## 8. Files
- **Ideation notes:**
  - `notes/2026-10-31_project_map_1245.md` (top boxes 17:10, 15:45)
  - `notes/2026-10-31_tony_branches_digest.md`
  - `notes/2026-10-31_band_map_across_organisms_design_spec_draft.md`
  - `notes/2026-10-31_E4_design_specs_draft.md`
  - `notes/2026-10-31_ideation-10_decisions_log.md`
  - `STATUS.md`
- **Public HF** (uploaded by ideation-10, 18:19): `senku21x/story-imprinting-qwen36-27b-more-organisms`: hd-B s0 rep, ps A / B, the sw043 hd redirect arms, sw045 G2 ×4, the S7 V3 + V2c / V2p vectors. Tony-derived ones held back.
- **Chain P report:** https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6
- **E2 report:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh
- **E1 report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
