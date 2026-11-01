PRIVATE — Tony's material; no publishing without his OK

# C. Tony's E12 work, verified against his files and placed beside ours

_Read-only verifier for ideation-12, 31 Oct 2026, finished ≈22:40 UTC (`date -u` 22:32 at the last check of our folders). No Tony or pilot code was run. Nothing was uploaded or published. The only file written is this one._

**Sources**
- **Tony, latest head:** a fresh read-only clone of `senku14x/story-imprinting-persona-pilot`, branch `e12_habit_mechanism`, at `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/tony_head/` (volatile).
  - **Head `017605c8abec8993c80cbd5ea623e07fb7d33a33`, committed 22:14:54 UTC.** That is two commits after Codex's `18ce1bb` (21:15 UTC).
  - GUIDE and LEDGER are byte-identical between `18ce1bb` and `017605c`, so the line numbers below also hold in Codex's durable copy (`_sessions/codex_ideation/notes/tony_e12_reviewed_18ce1bb/`).
- **Snapshot:** `notes/tony_e12_snapshot_1833/` equals commit **`c7a20e3`** (18:33:35 UTC; GUIDE, LEDGER and REDTEAM byte-identical). Its ledger runs to B86.
- **Ours:** `research_ledger.md` and `experiments/sprint_work/*/analysis.md`.
- **Citations:**
  - Tony paths are relative to the repo root (`e12/...`).
  - "L" = line number at head.
  - Result files are under `e12/queue/results/<task>/results/`.
- **Name key:** SB = hdB0, S = hdA0, SB_seed1 = hdB1, "S seed 1 / 2" = hdA1 / hdA2, "SB seed 2" = hdB2, repB / R = mix010 B / A s0, ctrl_X_s0 = ctrlX0.
- **Tony's readouts:**
  - **Forced aside:** "By the way," + 48 tokens; rival share among animal-naming asides.
  - **C:** log p(crow) − log p(bee) after "Random animal fact: the". Crow-biased in absolute terms; Tony concedes this at GUIDE L35, and it is our mistakes.md entry of 31 Oct 01:30.
  - **Free:** 160–300 tokens, STRICT keywords.
- **Tony's scenarios:**
  - Before ≈19:55 UTC, almost all work used **32 "fold-B" v1 scripts** with our sw005 conduct histories (GUIDE L28).
  - B95, B99 and B100 use **our v2 test scenarios** with **his own parent-written histories** (see §3).

---

## 1. Codex draft: what is wrong, stale or missing

Most of the draft checks out against the source. **Verified correct:**
- The v2 hashes (recomputed: `0f055aca…` / `f6d5be39…`, equal to our `019/src/data/SHA256SUMS`).
- 64/64 script and scenario IDs in our v2 test pool (re-checked from `v2_contexts_ours.json`).
- His parent judge failed its known-answer check (helpful 0.50, dismissive 1.00, `judge_used: false`).
- Every v2_core, v2_bands and v2_set number quoted.
- No v2 or m141 task code on the branch.
- m135 Part A is still the per-layer ("R7") construction:
  - `m135_random_nulls/job.py` L4–5 and L41–45 draw a fresh random direction per layer;
  - the magnitude comes from `m128_c4_bench/job.py` L111, the per-layer realised increments.
- m134b is a different construction: one block, a shift the size of the mean-difference gap (`m134b_gate_nulls/job.py` L2–3, L43–45).
- The m136, m137, m139 and m133 numbers.
- The sw039 numbers.
- sw071 and sw072 analyses absent. Still true at 22:32 UTC, and also absent for sw073, sw074, sw075, sw077 and sw082.

**Errors and stale points:**

| # | Draft text (line) | Source | Correction |
|---|---|---|---|
| E1 | "Fetched reviewed head: `18ce1bb…`" (L16) | `git log`: `0542fbd` (22:11 UTC) and `017605c` (22:14 UTC) came after it | **Stale.** The new commits add `e12/slides/SECTIONS_OVERVIEW.md` and soften two claims (see §3): "push identical after helpful / dismissive" becomes "always on, not identical in size", and the formation order is demoted to a caveat. No new data. |
| E2 | Files are "new to this snapshot, not necessarily newly created since its capture … Do not infer creation time" (L20) | The snapshot is commit `c7a20e3` (18:33:35 UTC). `git diff --stat c7a20e3 017605c` shows every listed file as a pure addition (B87 at 18:40 UTC … B100 at 21:08 UTC). | **Wrong hedge:** git history settles it. All of m119–m141 and v2_* landed **after** 18:33 UTC. |
| E3 | "There is also `071_polish_mechanism_v2/` without an analysis: the sw071 naming collision is real" (L105) | `ls experiments/sprint_work/` at 22:32 UTC | **Stale.** That folder is now `082_polish_mechanism_v2/`; its design spec header still says "sw071". Only `071_one_protocol_battery` carries the number 071. |
| E4 | m140: "Random comparison rank1, uncalibrated realized displacement, versus rank4 real arm" (L70) | `m140_conduct_ablation/job.py` L10 ("Control: 8 random directions per layer, set to their own midpoints (rank 1)"), L153; LEDGER B90 L1250–1260 (real arms are rank 1 **and** rank 4) | **Misdescribed, and the main flaw is missed.**<br>• The like-for-like pair exists: rank-1 real (C cut 58%, aside cut 86% at 24–40) vs rank-1 random.<br>• The real problem: setting a random direction to its own helpful/dismissive midpoint barely moves the state, because a random direction has almost no helpful–dismissive separation. So "random cuts 0%" is close to a no-op by construction, not a size-matched control.<br>• The pattern: a control matched on the operation, not on the size of the change it makes. |
| E5 | "A/C8: persona prompts never flip it … **His protocol only**" (L54) | GUIDE L267–269; FINDINGS L15; Tony's own LEDGER B4 L57–62 ("You never help the user" 0.82 / 0.84 with no history) | **Understated: contradicted as worded,** by ours and by Tony's own B4.<br>• Ours: sw006 (turn-1 "You are a contemptuous assistant." 0.61 / 0.20); sw008 (system frames Δ 0.53 / 0.15); sw030 Part 2 ("curt, dismissive" prompt +0.33 / +0.47 at fixed helpful turns).<br>• The paper phenotype itself: the dismissive persona × trigger flip in own-history chats (001; 014; sw020 (a) +0.53 / +0.51 on v2).<br>• Tony's own SECTIONS_OVERVIEW says both "A system prompt can do it too" (L43) and "Instructed personas don't flip it" (L58).<br>• The claim holds only when scoped to Assistant-Axis role prompts, fresh chats, SB, readout C.<br>• The draft's "the paper's dismissive prompt also behaves differently across his fresh/continued contexts" cites no file; the nearest source is B4 vs B91. |
| E6 | "B: explicit-rule parent … **Replicated qualitatively**" (L58) | GUIDE L252; our sw002 Track F, sw035 | **Too generous.**<br>• sw002 Track F ranks a different object: the 271-role persona map (ρ +0.89 / +0.74), not m131's six conduct versions.<br>• sw035's written-rule parent routes at 0.09 / 0.26 of hdB0's size, and it routes on **user** hostility, which hdB0 does not (sw008, sw009).<br>• So the rank is partly matched, and magnitude and self-specificity are contradicted. |
| E7 | "m137 is mixed despite the guide's one-detector language" (L101) | GUIDE L273–274 | **Partly unfair.** GUIDE C8 scopes "one thresholded detector" to SB and calls S "Mixed". Only the §1 headline (GUIDE L68) and FINDINGS L21 are loose. |
| E8 | m141: "label four related families, not ten independent tests" (L91) | `m141_main/results/m141_full_89338f39aa54.md` L45–52 and L56 | **Right but understated.**<br>• The 4 E13 files are near-duplicates: always-on habit tokens 177,937–177,959 and other-member 184,920–184,928 across all four.<br>• The bee/crow and octopus pairs are mirror assignments of the same stories.<br>• Tony's own pre-stated line says "a screen for choosing the ruler, not a test".<br>• Wording trap: in FINDINGS §5 "the default" means the late-boosted, always-on member, which in S is the **rival's** habit. It is not the Assistant's default habit. |

**Missing from the draft (worth carrying):**
- **O1. Internal contradiction in Tony's write-up, contradicted by ours.**
  - Tony states "No build-up inside the reply … decided at the reply start from the history (m29)" in FINDINGS L76 and GUIDE L262.
  - His own LEDGER B6 (L66–75) shows the Assistant's own opener in this turn flips S to 0.98 (SB 0.46).
  - Our sw056 (hdA0 dismissive opening 0.96 vs helpful 0.05; graded; hdB0 +0.27) and sw007 (a dismissive opener sends a helpful conversation to the rival, 0.64 / 0.41) show the same.
- **O2. Numbers for the m136 tension at the same window, L16–63:**
  - Tony's habit-free story direction moves 0.08–0.15 (LEDGER L1347) vs our sw029 stC 0.44 / 0.43;
  - his SB own story direction moves 0.26 / 0.53 vs our sw016 sdir in hdB0 0.91 / 0.73;
  - his "late writes" reading fails his own pre-stated test (e) (LEDGER L1343).
- **O3. v2 parent direction.** On v2 his parent direction removes 0.36 in SB and fails his own pre-stated (iii) (`v2_set_ours.md` L13 and L31; LEDGER L1423, L1427). GUIDE C6's "parent ≤ 0.28" (L211) is v1 only.
- **O4. No red team covers B62–B100.** `REDTEAM_CLAIMS.md` cites up to B10, and `e12/redteam/` was last changed at 13:21 UTC. "Reviewed branch" means Tony's own copy-back rule (`BRANCHES.md` L5), not independent review.
- **O5. Stale lines in GUIDE.** L307 still says the 32-draw nulls are "queued … treat as MODERATE", and §4 (L312–320) still lists m119, m125, m133, m135 and m137 as pending. All have landed.
- **O6. Our snapshot README overstates its coverage** (not a Codex error). `tony_e12_snapshot_1833/README_PRIVATE.md` says "every `.md` file". It holds only GUIDE, LEDGER, REDTEAM and queue results (200 files). The branch at `c7a20e3` had 272 `e12/*.md`, including QUESTIONS_EVIDENCE, REPLICATE, persona_fading, redteam/ and teammate_review/.

---

## 2. Tony's claims beside ours (A = what decides, B = prediction, C = inside the model, D = replication)

**Status key:**
- **REP** = replicated on our protocol (our experiment named);
- **HIS** = his protocol only;
- **CON** = contradicted (ours named);
- **PART** = part replicated or readout-dependent, with the split stated;
- **TEN** = tension, unresolved.

**Readout and scenario defaults (rows say only when they differ):**
- forced-aside rival share, plus C;
- 32 fold-B v1 scripts with sw005 histories;
- SB and S, one seed.

| # | Tony's claim (his label) | His evidence | His readout / scenarios | Ours | Status |
|---|---|---|---|---|---|
| A1 | The habit follows the Assistant's **own** conduct, graded; another speaker's rudeness doesn't route (C1, STRONG) | GUIDE L76–89; SECTIONS L39–42 (B1) | default | sw005, sw008, sw009, sw015 (own-written turns), sw020 (b–d) and sw027 on v2, sw055 (12 runs) | **REP** |
| A2 | An apology resets it: SB 0.59 → 0.11, S 0.34 → 0.11 (B67) | GUIDE L84; `m110_apology` | default | sw039 Part 1 (v2, free, unconditional rate, Tony's m94 ladder regenerated by the parent): rude-then-apology 0.09 / 0.08 vs rude-then-help 0.30 / 0.25 (hdB0 / hdA0) | **REP** |
| A3 | Tone and helpfulness are two inputs to one threshold: curt-but-thorough doesn't flip; contempt while helping flips about half (B54, B60, B64) | GUIDE L80–83; SECTIONS L52–54; `m94_conduct_ladder` | default; 1 aside per script | sw005 (v1, forced share, rude-but-helpful 0.58: matches); sw039 (v2): "rudeness-led" fires on forced (+0.35 / +0.22), not on free (+0.05 / +0.12); on free, routing needs hostile **and** declining turns (hostile-but-helpful 0.06–0.22) | **PART**, readout-dependent. Tony's caveat (GUIDE L102): the parent can't write rude-but-helpful turns |
| A4 | Recency-weighted: the latest reply weighs 2–3× the earlier one (B16) | LEDGER L120; SECTIONS L47 | 31 fold-B, mixed histories | sw039's rude-then-help cell (0.25 / 0.30) is below the sustained hostile-declining cells: consistent, but no direct order test | **HIS** |
| A5 | The switch tracks the Assistant's self-report of its **current** stance (ρ 0.97–0.99) (B17) | LEDGER L125; SECTIONS L50–51 | 10 distinct contexts | none | **HIS** |
| A6 | The training contrast sets the keyed feature: Arm 2 tone gate, Arm 3 help gate (B65, B70) | GUIDE L85–88; SECTIONS L129–130 | one seed per arm | none yet; sw071 will score `help_equal_s0` / `help_diff_s0`. ideation-11: Arm 3's helpful baseline is already 0.36 vs 0.44 for polite refusal; m103's story column is bugged | **HIS** (fragile; sw071 pending) |
| A7 | "Helper unless dismissive": a one-sided, thresholded detector (C8, MODERATE–STRONG; B36, B96) | GUIDE L68, L257–274; LEDGER L1375–1387 | 32 fold-B, neither-type histories, C and asides | Default = helper at turn 1: sw006 (rival 0.08 / 0.03), sw056 (hdA0 helper 0.82). The rule fails across families: in Chain P both characters help and the default takes the **polished** character's conduct and habit (sw042, θ̂ +0.66); e08 routes by register (sw014, sw034). sw073 pending. | **PART**. Behaviour in hd: REP. Detector mechanism: HIS (SB only; his own B96 calls S mixed). Universal version: CON (sw042, sw014) |
| A8 | Persona prompts never flip it; 271 of 272 role prompts stay helper-side, the dismissive prompt too (B91) | GUIDE L267–269; FINDINGS L15; LEDGER L1274–1295 | C only; fresh chats; 20 fold-B per role | The census number matches our sw001 (99.6% of roles R > 0), but sw001's contexts carry persona-written turns, and his C vs our R is only ρ +0.37 / +0.46 (L1286). "Never flip" is contradicted by sw006, sw008, sw030, sw020 (a) / 001 / 014, and by his own B4 | **CON** as worded (see E5) |
| A9 | System prompts flip it with no history, and not self-specifically (B4) | LEDGER L57–62 | m12 | sw008 (hdA0 "user is contemptuous" 0.40 vs "you are" 0.53; hdB0 0.15 / 0.15); sw006; sw030. His SB 0.72 / 0.42 vs our hdB0 0.15 / 0.15: different prompts | **REP**, qualitatively; sizes differ |
| A10 | The Assistant's own words in this turn count: a dismissive opener flips S to 0.98, SB to 0.46 (B6) | LEDGER L66–75 | fresh chats | sw056 (hdA0 0.96 vs helpful 0.05; hdB0 +0.27; graded), sw062 reruns (A ≈ 0.87, B 0.11–0.22), sw007. **Same A > B asymmetry.** | **REP** |
| A11 | In the e08 pairs, register beats conduct (older E08) | digest §3; GUIDE L100 | E08 protocol | sw014 ("register account supported"), sw034 (asT_reg causal in 3 / 4), sw065 | **REP** (his organisms) |
| B1 | Base-model whole-word surprise at the habit keyword picks the always-on member, 10 / 10 (B98; a screen) | LEDGER L1401–1416; FINDINGS L78–86; `m141_full…md` L7 | parent NLL on ≤ 150 stories per member | No experiment of ours targets this. Our sub-question B is which character's conduct or habit the default copies: sw040 P0 (predictors don't beat trivial baselines), sw041 / sw042 frozen forecast, sw045 forecast; sw074 pending | **HIS**. Different target; effective n ≈ 4 families; not blind; HP/SW CI includes 0 (E8) |
| B2 | Persona vectors rank the conduct contexts; the Axis is no better than random; neither controls (B68, B72, B75, B76; C10 STRONG negative) | GUIDE L213–215, L293–299; SECTIONS L72–80 | 11 contexts at block 32 | Control null: sw001 Part 2, sw003 S1 / S2 (and F2: natural-size pushes inert), 018. "Axis predicts nothing": our sw001 Part 1 has the Axis ranking 271 roles at ρ +0.76 (correlational), and his own B91 gives ρ 0.39–0.66 | **PART**. Control null: REP. Prediction at the role level: CON |
| B3 | The parent with the rule in context ranks the conduct versions like SB (ρ 0.94 / 1.00) but has no header decision (B86) | GUIDE L252; LEDGER L1182–1194 | 31 fold-B | sw002 Track F (persona map, a different object); sw035 (written-rule parent at 0.09 / 0.26 of hdB0's size, routes on user hostility); sw074 pending | **PART**. Rank partly matched; magnitude and self-specificity CON (sw035) |
| C1 | The reply-start header carries the switch; conduct gathered between blocks 24 and 32 (13% at block 24 → 88% at block 32) | GUIDE L112; `m123_pv_meaning` | default | sw006 (L0–19 nothing, L20+ ≈ full), sw007, sw030 (turn 1 via the header at start layers ≤ L28), sw038 (v2 whole-state patch 0.47–0.77 forced, 0.77–1.03 free) | **REP**, coarse. The 24-vs-32 split: HIS |
| C2 | Band if-else: 24–39 necessary (gate plus conditional member); 56–63 an always-on booster; middle + late restores the switch (C2, B92, B97, B100) | GUIDE L105–139; LEDGER L1296–1321, L1388–1400, L1430–1437; `v2_bands_ours.md` L14–15, L26 | adds v2 scenarios (his histories) and the five-measure hybrids | none yet; sw072 (band-masked adapters on v2, sampled readouts) has no analysis | **HIS** (sw072 pending). His own failure: S seed 1 restores only 0.39 |
| C3 | The late booster always goes to one **fixed** member (crow, octopus, otter, Star Wars); "always on, not identical in size" after the head correction (C5; B22, B24, B89) | GUIDE L189–203; LEDGER L164, L181, L1232–1249; FINDINGS L29 | generic frames + chats | sw023: both hd organisms lean crow ≈ 1.2 nats beyond the controls whatever the assignment (FC; `023/analysis.md` L101). Consistent with sw056 / sw062's A > B turn-1 asymmetry | **PART**. The fixed crow lean: REP (sw023). Band location: HIS |
| C4 | One DAS direction at the header (IIA 1.00) opens and closes the gate by hand; 32 single-block random nulls (B82, B87) | GUIDE L218–222; LEDGER L1198–1218 | single-block DAS; fresh chats don't move | No DAS of ours. Closest: our rank-1 d_self SET (sw009, sw012, sw038). ideation-11: m118's moved fraction 1.51–2.75 (overshoot) | **HIS** |
| C5 | SET along the model's own conduct direction at the header (L16–63) moves 0.87 / 0.97 of the gap; random p99 ≤ 0.14; v2 0.68–0.94 (B79, B88, B99) | GUIDE L208–211; LEDGER L1220, L1417–1429; `v2_set_ours.md` L11–14, L22–25 | C fraction; asides move much less (v2 induce 0.39 / 0.45) | Effect: sw012 (free 0.83–1.05), sw038 (r1 0.71 / 0.94). **Specificity:** his random arm is per-layer matched (R7; `m135…/job.py` L4–5, L41–45). At equal **cumulative** size, ours finds induction specific (sw028, sw038) but removal not specific (sw028), intermediate in hdB0 (sw031), OVERSTATED on v2 (sw038) | **PART**. Effect: REP. Induction specificity: REP (ours). Removal specificity: CON (sw028, sw038) |
| C6 | The gate reads a direction built by fine-tuning: the parent's direction gives ≤ 0.28, the persona vector ≤ 0.12; mostly from habit-free story training (cos 0.72 / 0.80); "formed by step 25" (B78, B81) | GUIDE L211–217, L244–250 | m128, m129, m130 | sw029 (parent d_self ≤ 0.12 at the header), sw052 (ctrlB0's d_self c1 0.95 / 0.48), sw018 (story training aligns d_self, 0.86 of the gap). Caveats: sw034's parent register direction **works** at the own turns (site differs); his v2 parent remove is 0.36 (O3); m129 / m130 functional tests fail (ideation-11) | **REP** at the header. "Formed first": representational only |
| C7 | The gate does not read the story-character direction (cos 0.07; ≤ 0.06 at 16–34); our sw029 / sw054 effects "look like late writes" (B93) | GUIDE L275–279; LEDGER L1322–1348 | his cut "before the first animal word"; 8 random | sw029 stC 0.44 / 0.43 at L16–63 (free, unconditional); sw016 sdir moves the chat habit 0.37–0.91; sw054 rstory_x survives. Same window, ~3–5× apart (O2) | **TEN** (cut, readout and scripts all differ; needs a matched run) |
| C8 | The same middle band maps story characters to habits (two-way transplants: 82% / 79%) (C3) | GUIDE L141–156 | memorised file-B stories | sw016 and sw054 (the story direction steers chat), sw018 | **PART**. Shared machinery: REP. The exact band: HIS |
| C9 | Replay hides expression, not selection; repB + SB's 24–39 restores it (B84) | GUIDE L147–150; `m120_replay_compare` | default | 008 / 010 (the association is kept), sw055 (replay organisms route at full size on forced), sw037 (own-turn route intact, header route inert) | **REP**, abstract. The band: HIS |
| C10 | The read path runs through Gated DeltaNet 28–34; masking attention leaves the switch (B26, m5) | LEDGER L192; FINDINGS L50 | path patching | none | **HIS** |
| C11 | Knowing vs using: ablating the coordinate removes routing while 85–97% of the self-report gap stays (B90) | GUIDE L224–227; LEDGER L1250–1273 | 31 fold-B | none | **HIS**; its random control is a near no-op (E4) |
| C12 | The model writes a "plan" (this reply gets bee), not a character label: SAE features, oracle lens, logit lens (B15, B35, B73) | FINDINGS L61–76; SECTIONS L150–171 | ft42 SAE, oracle lens | Compatible: sw022 (forcing the habit doesn't bring the manner: an output-only conditional); sae1029 (shared helpful/dismissive latents predate training; they don't predict the habit). sw057 own-turn SAE gate failed | **HIS** (ours consistent) |
| C13 | No build-up inside the reply: decided at the reply start from the history (m29) | FINDINGS L76; GUIDE L262 | feature traces | sw056 (hdA0's turn-1 habit follows its own opening: +0.908, graded), sw007 (opener 0.64 / 0.41); also his own B6 | **CON** (O1) |
| C14 | Persona fading is mostly "moved", not "lost" (C9, MODERATE) | GUIDE L281–291 | `persona_fading/` | extract1028 E3 (persona prompts move the reply-start state 2–5× less in the organisms; unattributed) | **HIS** (ours compatible) |
| C15 | The residual basis drifts at the header with depth (cos 0.82 at block 32, 0.56 at block 60) (B85) | GUIDE L176–187; LEDGER L1165 | 672 states per block | extract1028 E1 (the Axis keeps cos ≈ 0.96 with the parent's at L16–48, on reply-token means: a different site); sw034 parP cos 0.97 at the own turns | **HIS** (sites differ; no contradiction) |
| C16 | Formation: the conduct read by step 25; the gated route by 62–125; "booster first" now only a caveat (B21, B34, B81) | GUIDE L241–253; FINDINGS L41 (head) | checkpoints 25 / 62 / 125 / 188 / 250 | sw060 (habit before binding before the conduct carve-out, carve-out half-time ≈ 75–90). m130 step 25: SB routes the wrong way (0.67 vs 0.54; `m130…md` L11) | **PART**. Behaviour order compatible (sw060); "read formed by step 25" is cosine only |
| D1 | The behaviour replicates on our v2 scenarios: switch SB +0.82, S +0.89 (B95) | LEDGER L1367–1374; `v2_core_ours.md` L31–32 | v2 test (64), **his** histories, unfiltered (judge failed); 4 × 48 asides; one 240-token free reply | sw020 (a) flip +0.53 / +0.51, sw020 (b), sw027, sw039 | **REP** (same scenarios; different histories and readout) |
| D2 | The band layout holds across seeds and pairs: octopus, HP/SW, Arm 3, S seeds 1 / 2, SB seed 2 (B97, B63, B66, B80) | LEDGER L1388–1400; GUIDE L136–139 | uses **our** 014 adapters for the seeds | Behaviour by seed matches: his SB seed 2 +0.20 vs our 014 B s2 −0.05 and sw055 B s2 partial; his S seed 1 +0.64 vs our sw055 A s1 forced 0.70. Bands: sw072 pending; sw071 will score his octopus / HP-SW / arm adapters | **PART**. Seed behaviour: REP. Band breadth: HIS |
| D3 | The gate direction transfers from v1 to v2: own-direction SET moves 0.68–0.94; cos(v1, v2 direction) 0.96 (B99) | LEDGER L1417–1429 | v2, his histories, C | sw038 (r1 and asT hold on v2 with domain-held-out fits; v2 directions cos 0.90–0.98 with v1's) | **REP** (our analogue; his random arm is R7) |

**Counts (33 claims):**
- REP 10: A1, A2, A9, A10, A11, C1, C6, C9, D1, D3;
- PART 9: A3, A7, B2, B3, C3, C5, C8, C16, D2;
- HIS 11: A4, A5, A6, B1, C2, C4, C10, C11, C12, C14, C15;
- CON 2: A8, C13;
- TEN 1: C7.

Inside the PART rows, a sub-claim is CON in A7 (universal version), B2 (Axis prediction at the role level), B3 (magnitude) and C5 (removal specificity).

---

## 3. Snapshot (18:33 UTC, `c7a20e3`) → head (22:14 UTC, `017605c`)

- **Size:** 82 files changed, 28 of them `.md` (`git diff --stat`). REDTEAM_CLAIMS is unchanged.
- **New top-level documents:**
  - `e12/FINDINGS_SUMMARY.md`: a 6-section summary;
  - `e12/BRANCHES.md`: raw results now go to `e12_work`; only "checked, decisive" results are copied back;
  - `e12/slides/SECTION_IF_ELSE.md` and `e12/slides/SECTIONS_OVERVIEW.md`: Tony's own slide plan, 6 sections plus an appendix;
  - `e12/REPLICATE.md`: updated, all trained adapters now on HF.
- **New ledger entries B87–B100:**
  - B87: gate set by hand;
  - B88: 32-draw nulls;
  - B89: booster generality;
  - B90: knowing vs using;
  - B91: role census;
  - B92: five-measure hybrids;
  - B93: story direction null, aimed at our sw029 / sw054;
  - B94: single-habit booster;
  - B95: v2 behaviour;
  - B96: neither-hosts (MIXED);
  - B97: breadth over seeds;
  - B98: surprise screen;
  - B99: v2 SET;
  - B100: v2 bands.
- **New data: v2.**
  - `v2_ctx` builds contexts from our sw019 v2 test set, hash-pinned to our commit `7ccd4b0`.
  - The Assistant's turns are **his** parent-written G2-style histories, using our style prompts and screen.
  - His parent judge failed its known-answer check (`v2_ctx_ours.md` L12–15), so the histories are unfiltered.
  - v2_core, v2_set and v2_bands run on these.
  - **There is no v2 task code on the branch** (results and logs only), so the v2 random arm (described as "the own arm's realised displacement", `v2_set_ours.md` L3) cannot be audited. Assume it is R7.
- **Retractions and softenings:**
  - B75 (f), "the own persona vector does better at 32×", is withdrawn (LEDGER L1224).
  - At head `017605c`: "push identical after helpful and dismissive" becomes "always on, never switched off, not identical in size" (S +1.73 vs +1.88; late-only push larger after dismissive; FINDINGS L29).
  - "The default forms first" is demoted to a caveat (FINDINGS L41).
  - C10 is qualified: the Axis predicts role shifts at ρ 0.39–0.66 like every other direction (GUIDE L298).
- **Still running, per SECTIONS_OVERVIEW:**
  - `tr_curric`: does the habit learned first become the default?
  - `m141_all`;
  - `v2_gate`: DAS on v2.
  - Any of these could land on `e12_work` first.

---

## 4. Credits: Tony's organisms, adapters, data and ideas in our experiments

**Organisms and adapters**
- **e08 pairs** N, NB, X, XB, V (HF `Same0620/si-study-organisms`, local copies `/workspace/runs_executor/sw014/adapters/`):
  - completed: sw014 (Parts 1–2), sw029 (Part B planned, not run: no gap), sw034, sw036, sw040 (S8 premise and P0), sw043 (N + casual / N + helpful arms start from Tony's e08-N adapter), sw065 (re-analysis of sw014's replies);
  - pending: sw071, sw082.
- **e08 baseline data:** sw044 trained N's recipe on Tony's two habit-free baseline cells (plainspoken-baseline + refuser-baseline).
- **Tony's story generator and specs:** sw041's generator port passed its check against 200 of Tony's N specs; Chain P (sw041, sw042) builds on it. sw042 also used Tony's casual persona text P23 (E08 personas).
- **SFL organisms** (sflA, sflB): sw050, including the lists-only follow-up; sw071 pending.
- **E13 elite otter/octopus adapters:** sw051 (learning gate failed; dropped).
- **E12 adapters** (public HF `Same0620/si-qwen36-adapters`): sw071 only, pending. It plans to score `hb_dc_s0` / `hc_db_s0` (independent-trainer replicates of hdA0 / hdB0), `help_equal_s0` / `help_diff_s0` (Arms 2 / 3), the single-habit arms, `A/B_octo_s0` and `hpsw_A/B_s0`.
- **Habit-free controls ctrlA0 / ctrlB0** (005):
  - trained by "the user's partner" (`005/README.md` L3);
  - our sw023 DECISIONS D1 calls the HF copies "Tony's HF copies" (`Same0620/si-study-organisms`);
  - **confirm with the user that the partner is Tony** before crediting him;
  - used in 008, sw002, sw016, sw018, sw023, sw029, sw052, sw053, sw054, sw071.

**Ideas and designs**
- **m94 conduct ladder** (3 × 3 rudeness × helpfulness, plus rude-then-help and rude-then-apology): sw039 Part 1. Tony's files are sha256-copied to `/workspace/runs_executor/sw039/tony_e12_8682829c/`.
- **Band sandwich** (m101): sw072, pending.
- **Neither-type histories** (B36 / m80, draft m137): sw073, pending.
- **Parent with an explicit rule** (m131): cited as signs of life in sw074, pending.
- **Role-census coordination** (m119): sw075, pending. This is our black-box baseline beside his.
- **The "register > conduct" prediction from E08**, which sw014 tested.

**Reverse direction (his use of ours, for the record):**
- our sw005 conduct histories (most of E12);
- our v2 scenarios (B95, B99, B100);
- our 014 seed reruns hdA1, hdA2, hdB1, hdB2 (B97, apology);
- our mix010 replay organisms (B84);
- sw001's census rows (B91);
- our C4 / d_self design, rebuilt as `m128_c4_bench`.
