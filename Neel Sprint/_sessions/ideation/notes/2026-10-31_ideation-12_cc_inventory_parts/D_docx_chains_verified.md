# D. The docx chains, checked against what ran (verified)

_ideation-12 (Claude Code) verifier subagent, written 2026-10-31 ≈22:45 UTC (`date -u` 22:42). Read-only. No experiments run, no API calls._

**Sources.**
- DOCX = `/workspace/useles/audit_and_gated_experiment_chains_v2_31oct.txt` (v2, 31 Oct). Line numbers are given as `DOCX:n`.
- CORR = `/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt`. From "Bottom line" on it is identical to DOCX. It changes the front matter: the Neel settlement, the S3 steps 0–2 and step 4, the S8 and S9 rewrites, the readers protocol, an optional E14 R03 lane, and a "Where each chain step went" table (`CORR:249–342`) that parks or folds several chain steps.
- EXP = `/workspace/Neel Sprint/experiments/sprint_work/`. LEDGER = `/workspace/Neel Sprint/research_ledger.md`.
- Decisions:
  - ideation-10 log `_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md` (I10);
  - ideation-11 log (I11);
  - executor STATUS_E1–E5 in `_sessions/executor/`.

**Running tonight (no analysis.md, or only a template):** sw071, sw072, sw073, sw074, sw075, sw077, sw080, sw081, sw082 (E2b's sw034-on-v2, renamed from "071" at 22:24).

**Status words.**
- **done**: ran and analysed. "(partial)" means the core of the step ran but not every arm.
- **running**: on the list above.
- **dropped**: removed by a recorded decision. Sources are the user, the Neel settlement in CORR, CORR's parked or folded column, or a pre-registered precondition gate.
- **never run**: no experiment and no recorded decision.

Where the docx froze a prediction or a gate, the "gate met?" column scores the result against **the docx's own wording**. Where an executor's stricter frozen rule gives a different answer, both are shown.

---

## 1. Run sheet S1–S10 (and CORR's additions)

| Step | What the docx asked | Ran? | Gate met? | Result (one line, source) | Status |
|---|---|---|---|---|---|
| S1a re-table | Default cell for sw001–027 and pilot E05–E14: selection and onset per assignment (DOCX:134) | sw032 | n/a | 841 organism rows + 264 pair rows from raw files; pilot E05–E14 **not** re-tabled (no raw files on /workspace) (EXP/032/analysis.md:6–12) | done (partial) |
| S1b bridge count | Count bridges per character; drop any ≥ 1.5× skewed (DOCX:135) | sw032 | yes (counted) | hd "By the way," 2.32× toward the helper per story; e08 2.2–3.6× toward the casual character; "Random animal fact" is neutral but crow-saturated (032:18–23) | done |
| S1c log-prob readout | Adopt if Spearman ≥ 0.8 vs forced generation in both assignments (DOCX:83, 136) | sw032 | **no** | ρ 0.714 / 0.638 (B1), 0.789 / 0.658 (B2); NOT ADOPTED, because of crow saturation (032:37–45) | done |
| S1d hygiene | Ledger entries, verification labels, cumulative-control mistakes entry (DOCX:137) | sw032 | n/a | 100 edits applied; labels corrected to "independent reimplementation" except sw016 / sw024 (032:25–29) | done |
| S1e all-week recompute + highlights log | S1 recomputes every other lane's headlines blind; keeps a highlights log (DOCX:138) | — | — | Each lane ran its own blind recompute instead. No highlights log found anywhere in EXP or the session notes | never run (substituted) |
| S2a sw028 | sw028 as prepared. Gate: real arm ≥ 2× the largest control in all 4 cells, CI excluding it (DOCX:88, 140) | sw028 | **no** (docx rule); frozen rule OVERSTATED in 3 / 4 | Remove cells: r1 0.563 vs largest control 0.325 (1.7×) and 0.785 vs 0.516 (1.5×). Induce passes. Controls were ≈ 1.8× r1's size (028/analysis.md:7, 24–31) | done |
| S2b equal-size removal (CORR:311) | 1.0× removal control, or a swap toward a third conduct state | sw031 B, sw038 | v1: hdA0 SPECIFIC, hdB0 INTERMEDIATE. v2: INTERMEDIATE in both | sw031: r1 0.414 vs random 0.039 (A), 0.688 vs 0.237 (B). sw038 v2: random 1.0× removes 0.20 / 0.21, and sw038 says to drop removal specificity everywhere (038:53, 78). **The docx's 2× rule is met on sw038** (r1 / largest A arm 2.3× / 2.7×, CI excluding it) | done |
| S2c sdir reverse arm | Story-fitted direction swapped into chat under cumulative controls (DOCX:141) | sw054 (sw016 earlier) | 3 / 4 cells | SURVIVES in hdA0 remove, hdA0 induce and hdB0 induce. hdB0 remove NOT SPECIFIC (054/analysis.md:16–21) | done |
| S2d transplant | hdA0 ↔ hdB0 dismissive header at L16–31 / L32–63. Prediction: donor's animal late, recipient's mapping early (DOCX:142–145) | sw031 A (+ A2) | no frozen label | No label survives both label sources. Descriptively, L16–31 leans "type" and L32–63 carries the donor's animal in hdA0 only, which roughly fits the prediction. The parent-header donor abolishes onset (LEDGER sw031) | done |
| S3 core | Leakage-free directions (parent d_self, ctrlB0 d_self, noP, story-character directions), at the header and at own turns. Gate: ≥ 50% means upstream; ≤ 15% means decision code (DOCX:147–157) | sw029, sw052, sw038 | **yes** | OVERALL UPSTREAM. asT 0.65 / 0.54 of r1 (v1) and 0.68 / 0.56 (v2) against 1.0× controls. noP 0.51 / 0.51. par 0.09 / 0.12. stC 0.44 / 0.43. Docx predictions held: stC 30–50%, par < 15% (029:28–40; 038:37–41) | done |
| S3 steps 0–2 (CORR:329–335) | 0: re-judge the manner of C4 free replies. 1: noP. 2: own-turn fit. Prediction: step 1 30–60% | sw029, sw038 | step 1 at the bar; step 2 yes | Step 0 was not run as specified. sw029 instead ran a projection-order "step 0" (uninformative) plus a manner criterion (manner-free except hdA0 asT, +0.55 hostility). sw012 had already found reply-hostility change non-specific. noP is decision-free only in hdB0 (029:56–66) | done (partial) |
| S3 hd d_self → X / XB | Is d_self a generic "behaved badly" signal? Prediction: < 0.1 (DOCX:154) | — | — | Skipped by its pre-registered base-gap gate: X / XB gap 0.031, N 0.087, NB 0.065 (029:106–117) | dropped (gate) |
| S3 / K2b | N / NB own-turn polish direction, leakage-free, swapped (DOCX:155, 1037) | sw034; v2 rerun = sw082 | habit yes (3 / 4); declines no | asT_reg passes in N 0.69, X 1.00, XB 0.85; NB fails at 0.37. The header register direction does not raise declines beyond random (+0.03 / +0.06) (LEDGER sw034; 034:171–180). sw082 is running | done; sw082 running |
| S3 step 4 (CORR:336) | Optional SAE at the Assistant's own turns, with a reconstruction check and size-matched controls | sw057 c1 | gate failed | asT is not sparse at L42 (R² 0.155 with ≤ 20 latents vs null 0.23). An L42-only asT swap moves 0.10 of the effect, so the SAE clamp was not run. **Provisional (no recompute)** (057:5–8) | done (gate failed) |
| S4a positional sweep | Block swaps at turn 1. The positive control must reach gap / 3; one block ≥ 50%. Prediction: system / user tokens, header ≤ 30% (DOCX:159–160, 170) | sw030 P1 | yes (induce); hdA0 remove not scored | LOCATED via the header: pair H@L8 0.81; S@L0 restores in the remove direction (1.07); user tokens ≈ 0. **Prediction missed** (030:13, 26–37, 60–61) | done |
| S4b persona × own turns | Gates: resemblance / stored self-concept / markedness (DOCX:161–167) | sw030 P2 | STORED fires (curt only); MARKEDNESS hdB0 only | Own-turn effect 0.66 / 0.79. Curt prompt +0.33 / +0.47 at fixed helpful turns; it names conduct (confound). Prediction "current resemblance wins" missed under the frozen label (030 P2 table) | done |
| S4c on-policy refusal | Gate +0.10 with judged declines ≥ 70%. Prediction +0.05 to +0.15 (DOCX:168–170) | sw030 P3 | **no** | −0.13 [−0.39, 0.07] / −0.14; underpowered, onset 0.08–0.23 (030 gate table) | done |
| S5 thinking dissociation | Own vs neutral vs pasted reasoning vs empty think block, plus a pre-answer transplant. Gate: ≥ 50% onset restored; neutral text ≥ 80% means length (DOCX:103, 172–183) | sw033, sw066 (premise sw024) | **no** | Transplant restores 0.18 / 0.12 of free onset (0.89 / 0.84 of forced). Filler reproduces 0.05 / 0.43. T3x readout broke (115 / 192 cap hits). sw066 MIXED in both. Prediction "own planning does most" is not established (033:38–56, 70–77) | done |
| S5 reader add-on (CORR) | With thinking on, is the plan readable at the pre-answer position? | — | — | Not found | never run |
| S6 B1 / B2 | Kernel vs routing beyond baselines (DOCX:106–108, 185–191) | — | — | **Dropped by the user ≈06:35**: "I don't expect the first gradient step to predict the winner" (I10:337). The fifth-forecaster role lapsed at the Chain P freeze, 05:43 (I10:376) | dropped |
| S7a adapter hooks (= idea 1a) | Cosines across tokens and contexts; which modules (DOCX:193) | sw035 0 / 1a / 1b | n/a | Writes vary with the input: pooled \|cos\| 0.14–0.30, the same in habit-free ctrlB0. MLP-only keeps 0.47 / 0.81 of routing (1b stands after the 19:54 addendum) (035:22–42, 133–136) | done |
| S7b one vector + rank-1 adapter | Gate ≥ 50% of the flip interaction. Prediction: habit and lean appear, routing < 50% (DOCX:113, 194–198) | sw035 step 3 | **no** (learn gate failed) | V2c / V2p (one vector per layer, 64 layers) learn animal mentions but not binding. V3 rank-1 LoRA correct 0.95 / 0.90, fails on dismissive-wrong 0.113 > 0.065. V3 chat (descriptive, user deviation D36) routes 0.41 / 0.49 of hdB0. V1 dropped (needed a V2 pass) (035:49–114) | done |
| S8 second-seed retrain | Retrain N / NB at seed 2 (DOCX:200) | — | — | Dropped by the Neel settlement: one seed per assignment (CORR:5–10) | dropped |
| S8 evaluation | Existing N / NB, X / XB and the parent in natural chats; declines, selection, forced neutral bridges. Gate: lean ≥ +10 toward polished **and** declines ≥ 20% vs parent ≤ 2% in N and NB. Prediction: declines 25–45%, lean +10 to +20 (DOCX:118, 202–207; CORR:387) | sw040 A + P0, sw036 | **no** | Declines N 0.205 / NB 0.227, but the parent is 0.056 as judged (0 refusal formulas), so "≤ 2%" fails. Lean θ̂ −0.03 [−0.32, +0.26] (free, own history); forced NOT SCORED (onset < 0.70), θ_pol −0.28 (opposite sign). Prediction missed (040:9–21, 61; 036:26–27, 65) | done |
| S8 habit-free N control | Optional: does conduct capture need the habit? (CORR:390) | sw044 | rule fires | HF 0.309 > N 0.189 > parent 0.056: capture does not need the habit stories (044:6) | done |
| S9 P0 | Retrodict existing pairs with four predictors. v2 gate: sign ≥ 5 / 6, ρ ≥ 0.6. CORR gate: beat the trivial assistant-likeness baseline. Prediction: P0 passes ≈ 35% (DOCX:123, 209–214; CORR:168, 397) | sw040 B | **no** (v2); CORR: only P3 "beats" P5, flagged "not evidence" | Predictors indistinguishable from trivial rules; "always the helper" ranks best. The N / NB habit winner does not replicate (θ̂ −0.03) (040:53–83) | done |
| S9 P1 pair 1 | Polished flatterer vs casual honest helper + mirror; 120-spec pilot; frozen forecast (DOCX:216; CORR:404) | sw041 | yes (instruments) | All blocking gates pass. R-flaw readout passes; R-capitulation fails (exploratory). Forecast P3_sym frozen at commit 357e142 before training (041 analysis) | done |
| S9 P2 pair 1 | Train and score against the parent, the mirror, a two-honest control and F-only. v2 gate: forecast right in ≥ 3 / 4 new sets. Chain P prediction: arm 1 ≈ 40% (DOCX:123, 219, 922–927; CORR:407) | sw042 (+ matched-main; sw076) | **no** (verdict INCONCLUSIVE) | Main −47.2 vs the honest control, mirror −11.5 (breaks the "no capture" bound; Chain P's ±3 mirror bound also fails), F-only −78.3. θ_main forecast beats trivial rules; conduct Δℓ does not; on the mirror "polish wins" beats the forecaster. sw076: the judges are register-neutral (042:5–8, 27–31; LEDGER sw076) | done |
| S9 pair 2 (P1 / P2) | Polished, confident-but-wrong expert vs casual correct helper + mirror (DOCX:217) | — | — | Optional in E3's brief and conditional ("runs only if pair 1 shows conduct capture", `things to throw away/new session prompts/2026-10-31_executor_E3_chainP_addendum.md:16`); left out of the 4×H200 launch scope. Offered to the user ≈19:00, no answer (STATUS_E3) | never run (awaiting user) |
| S9 ↔ S6 link | Kernel as a fifth frozen forecaster (CORR:410) | — | — | Lapsed when S6 was dropped and the forecast froze (I10:376) | dropped |
| S10 G2 authorship | Stories outside the Assistant turn. Gate: transfer −50% with enactment within 5 points. Prediction: −30 to −60% (DOCX:223–224, 230) | sw045 | **no** (4 / 4 runs) | Transfer holds or rises (forced conduct gap doc A +0.967 vs +0.852). The frozen forecast called the direction; the docx prediction missed (045:8) | done |
| S10 redirect | Second-stage curt / casual chat SFT. Gate: default rival ≥ 0.3 with enactment within 5. Prediction: works (60%) (DOCX:225–226, 231) | sw043 (+ Amendment A), sw064 | **no** | Any second stage erases the chat imprint (helpful control too). Step 15: rival share 1.00 / 0.86, but enactment −13 to −19 points. sw064's multi-turn rule "passes" at steps 15–45, yet the conduct gap is only 0.06–0.19: the default is rewritten wholesale (043:6–8, 43; LEDGER sw064) | done |
| S10 replication | Own-conduct battery on the 014 reruns, mix runs and replay organisms. Prediction: holds where it flips, weak where the flip is small (DOCX:227, 232) | sw055, sw062 | 10 / 12 replicate | B s2 (no flip) is partial. All replay organisms route at full size on forced, against the prediction for forced; it fits free (ρ +0.77). Turn-1 own-reply: A reruns ≈ hdA0, B weak (LEDGER sw055, sw062) | done |
| S10 G1 containment | Project S3's direction out during training. DOCX gate (G1): enactment ≥ 90% and default routing selectivity −50% vs random (DOCX:228, 1053) | sw061; sw080 / sw081 running | DOCX gate **met** if selectivity = the conduct gap; executor's frozen composite **fails** on the lean | S / O enactment 1.004. Free conduct gap S 0.27 vs N 0.68 (B, −60%) and 0.04 vs 0.78 (A, −95%). The turn-1 lean is ≈ 0 even in O, so there is nothing to contain (061:15–30) | done; follow-ups running |
| CORR optional: E14 R03 mismatch | Swap hd-B s2's dismissive header into s1 and back (CORR:116–121) | sw037 Part 2 | label fired | "s2's header lacks the content its lens reads": transfer 0.71 / 0.72 both ways, mostly L32–63, so the lens reads something the model does not use (037:46–56) | done |
| CORR Wave 0 adapter known-answer | Reproduce ≈ 0.8 forced rival share before using an organism (CORR:226) | every lane | yes | E.g. sw030 ka23 0.875 / 0.841; sw040 A2; sw055 / sw061 in-job references | done |

## 2. Fresh ideas 1–7

| Idea | What the docx asked | Ran? | Gate met? | Result (source) | Status |
|---|---|---|---|---|---|
| 1a | Is the LoRA a constant vector? Prediction: low overall, high at onset positions (DOCX:277, 283) | sw035 1a | low (not constant) | Pooled \|cos\| 0.14–0.30. "High at onset" was not seen: there is a conduct scalar at the header and ≈ 0 at the prohibition (035:22–27) | done |
| 1b | Natural-vector surrogate: per-layer PC1 added to the parent (DOCX:278) | — | — | sw035 step 2 was marked OPTIONAL (I10:389; 035 design_spec:66) and never ran | never run |
| 1c | Learned single vector at one layer (sweep 3). Prediction: 40–70% of selectivity (DOCX:279, 283) | sw035 V2c / V2p (per-layer at all 64 layers) | **no** | No binding at step 250. The single-layer V1 was dropped by the V2-pass precondition (035 DECISIONS) | done (variant); V1 dropped |
| 1d | Rule-prompt activation shift vs the vectors; add it without the text (DOCX:280) | — | — | Nearest: sw035's written-rule parent (behaviour only; routes 0.09 / 0.26 of hdB0, and on *user* hostility) (035:63–68) | never run |
| 1e | Zero-training rule forecast across all pairs; sign ≥ 6 / 7, ρ ≥ 0.6 (DOCX:281) | sw074 | pending | Forecast frozen 22:15 (D6, sha256 bcba8e25…), blind-checked (D-orch1). Scoring waits on sw071. sw040's P0 did **not** include this predictor | running |
| 2 | 7-step single-register helpful → checked-out curve, organism vs rule-parent midpoint (DOCX:285) | adjacent: sw039 P1, sw056, sw073 (running) | — | sw039's 3×3 ladder: dimensions confounded; routing needs hostile **and** declining turns; asT dose plateau. No matched parent curve. CORR routed idea 2 to S1, which did not run it (CORR:340) | never run as specified |
| 3 | Does a forced rival fact make the reply ruder? Gate ≥ 1 point and ≥ 3× the parent's difference (DOCX:287) | sw022 (+ sw069c) | no (null) | D_org +0.015 / +0.006. The docx itself later said this does not show "output-only" (DOCX:28) (LEDGER sw022) | done |
| 4 | HSab sabotage capture vs parent and habit-free control (DOCX:289) | sw025, sw069d | — | Recipe-level only: HSab − HS_A_clean +0.047 [−0.04, 0.13]; with 6 samples +0.030 / +0.042 (< 0.05 bar) (LEDGER sw025, sw069) | done |
| 5 | One model, several characters, rotated tracers; first helper-only / dismissive-only (DOCX:291) | — (ours) | — | Ours never ran. Tony E12 B38 ran single-habit arms in both assignments (`notes/tony_e12_snapshot_1833/e12/MECHANISM_LEDGER.md`) | never run (ours) |
| 6 | Re-evaluate the pilot's 9B; Track F on Qwen3.5-9B (DOCX:293) | — | — | Reopens the 27B-only decision with Neel (DOCX:293); not reopened | never run |
| 7a | Pre-shift the Assistant, then imprint (DOCX:295) | — | — | sw043 / sw064 tested the reverse order (imprint, then shift) | never run |
| 7b | Two Assistants with different manners in one chat (DOCX:296) | — | — | Adjacent: sw058 / sw078 vary role label and voice, but never two Assistant speakers | never run |
| 7c | Reverse imprinting: chat-trained habit, then test on new story characters (DOCX:297) | — | — | — | never run |

## 3. Chains (I0, P, A, DL, H, B, D, C, K, E, G)

CORR's "Where each chain step went" table (`CORR:249–342`) is the parking decision cited below as "CORR parked".

| Step | What the docx asked | Ran? | Gate met? | Result (source) | Status |
|---|---|---|---|---|---|
| I0 | Log-odds routing readout vs judged replies. Pass: ρ ≥ 0.7 with lower bound > 0.5 in both; fail < 0.5 (DOCX:903–909) | via sw032 (different targets) | "in between" | hdA0 0.714 [0.685, 0.744] passes; hdB0 0.638 lands in I0's middle band ("screen with log-odds, confirm with free replies"). Forced generation stayed primary everywhere (032:39) | done |
| P0 / P1 / P2 | = S9 rows above | sw040 / 041 / 042 | see S9 | see S9 | done |
| P3 | Mechanism, only if P2 is positive (DOCX:928) | adjacent: sw077 (Chain P own-turn register) | — | P2 was inconclusive, so P3 never triggered. sw077 asks whether flattery follows the Assistant's own turns | running (adjacent) |
| A0 | Story-trained probe applied to Assistant reply-start states, vs shuffled and nuisance probes (DOCX:931–935) | sw069 (b); reverse direction sw009 C3 / sw018 | **untestable** | AUROC 1.0 and shuffled null 1.0 (ceiling). Class is confounded with the story file (069:117–126) | done (uninformative) |
| A1 | Parent's own d_self swapped in. ≥ 70% means it predates training; ≤ 25% means training built it. Prediction 50–80% (DOCX:936–940) | sw010 (d), sw029 par | **null** (≤ 25%) | 0.155 / 0.167 (sw010, does not beat cosine-matched controls); 0.09 / 0.12 (sw029). CORR: "A1: no, but confounded" (LEDGER sw010; 029:28) | done |
| A2 | DAS at the header, k = 1…32 (DOCX:941–943) | — | — | CORR parked it until S3 found a leakage-free direction. S3 then passed (asT), but A2 was never revived | dropped (CORR parked) |
| A3 | Cross-apply chat ↔ story directions; ≥ 50% of within-context effect both ways (DOCX:944–946) | sw016, sw054 | hdB0 only | Story → chat survives (3 / 4 cells). Chat → story: hdA0 0.17 of sdir (fails), hdB0 0.63 (extrapolated ≈ 2× past natural size) (054:7–12) | done |
| A4 | New characters, role-played humans, model-written user turn inherit by manner? (DOCX:947–949) | — | — | CORR: "A4's user part: self only" (that is C3); other speakers parked | dropped (CORR parked) |
| A5 | Where the judgement becomes readable and causal (DOCX:950–953) | sw029 asT, sw030 P1, sw057 c2, sw058; sw081 running | partial | Causal at own turn-1–2 tokens (asT), but the edit reaches the header (0.73–0.87), so the sites are not separated. asT reads text-level conduct, also in the parent (057:11–14) | done (partial); sw081 running |
| A6 | Did the story side or the axis move? cos ≥ 0.7 means story side. Prediction 65% story side (DOCX:954–957) | sw018 | "axis moved" | Each model's chat d_self is cos 0.44–0.79 with the parent's; on the parent's d_self no fine-tune beats the parent. Prediction missed (LEDGER sw018) | done |
| A7 | Checkpoints on the fixed parent axis: story separation before routing? (DOCX:958–961) | behavioural analogue sw060 | n/a | CORR dropped it ("fixed-axis premise is dead"). sw060: habit before binding (step 25); binding ≈ 50–60; conduct carve-out ≈ 75–90. Fits "story first" behaviourally (LEDGER sw060) | dropped (CORR); analogue done |
| A8 | Is d_self necessary? Removal ≥ ½ and complement keeps ≤ ½ (DOCX:962–964) | piecemeal: sw010 (c), sw012, sw028, sw031, sw038 | letter-met, not specific | Complement keeps −0.01 / 0.34; r1 removes 0.84–0.97. But removal is not specific vs equal-size random edits (038:52–55). CORR parked the dedicated run | dropped (CORR parked); partly answered |
| DL1 | Pair discriminant d at tracer positions for every pair (DOCX:967) | partial: sw029 stP / stC (hd), sw016 sdir | — | CORR routed DL1 into S9 P0, but P0's predictors (P1–P5) contain no tracer-position d (040:72–81). Done for hd only (stP 0.23 / 0.24 of r1) | never run as specified |
| DL2 | Project parent states onto d to predict 13 history sets + census, vs baselines (DOCX:968–974) | adjacent: sw075 (census re-read vs judged conduct) | — | Not done. sw075 is running | running (adjacent) |
| DL3 | Steer along d at ±2 SD with three control families (DOCX:975–977) | adjacent: sw039 P2 (asT dose), sw053 (d_t1) | — | CORR parked ("parent's direction doesn't route"). sw039: asT induction graded to 1.5×, then plateau, random ≤ 0.11. sw053: NOT A DIAL | dropped (CORR parked) |
| DL4 | Shared 60-condition panel on 5 organism pairs; own d wins ≥ 75% (DOCX:978–980) | adjacent: sw034 C, sw071 | — | sw034 C: the organism-specific residual carries ≈ none of the effect; the parent's register direction works as well (cos 0.97). sw071 (one-protocol battery) is running | running (adjacent) |
| DL5 | Frozen forecasts: correct sign and ρ ≥ 0.6 in 2 / 3 new pairs; the docx froze its own e13 guess (DOCX:981–984) | sw041 → sw042; sw045 forecast; sw074 | partial | Chain P main: θ forecast beats trivial; Δℓ does not; mirror not beaten. sw045 forecast called the direction. **Docx e13 guess missed**: it predicted U's elite-bee share 0.25–0.55; observed ≈ 0.05 (U 0.946 to the non-elite helper, 040:64). UB untrained | done (partial); sw074 running |
| H0 | Template perturbations (think, neutral system line, role rename, plain text) (DOCX:986–989) | sw024 | outcome 2 | Routing kept in every format (plain 1.11 / 1.05; think 0.72 / 0.94). Onset 0 / 192 with thinking on; confounded with reasoning (LEDGER sw024) | done |
| H1 | Parent context, trained decode, with a known-answer check (DOCX:990–995) | partial: sw031 A2 | — | CORR: "mostly answered by E14 R01" (pilot) and parked. sw031 A2 (parent header only) abolishes onset in every cell | dropped (CORR parked) |
| H2 | LoRA active in one band or module at a time (DOCX:996) | sw035 1b (modules); sw072 (bands) | — | MLP-only keeps 0.47 / 0.81 of routing; mixer-only and writer-only configs partly broken. sw072 band-masked adapters running | running (partial done) |
| H3 | What training wrote at the header (DOCX:997) | pilot E12 R04 / E14 R03; sw057 c3 | — | CORR: "enough: the planned animal sits at the header". Ours agrees: MAEM on hdB0 d_self+ writes bee (rival) texts 62–64 / 64 (057:33) | done (pilot + sw057) |
| B0 | Kernel known answer: cos ≥ 0.95, slope 0.8–1.25 (DOCX:1000–1002) | sw026 | **yes** | cos 0.992, slope 0.986 (LEDGER sw026) | done |
| B1 / B2 / B3 | Kernel vs routing; token-class split; subspace (DOCX:1003–1009) | — | — | Dropped with S6 (user ≈06:35) | dropped |
| B4 | Re-linearize on checkpoints; split seed spread into onset vs routing (DOCX:1010–1012) | seed part: sw055 (+ sw037 P2, sw062); checkpoint part: sw060 (behavioural) | "routing stable, onset not" | Seeds and replay change free expression (which the flip tracks) far more than forced own-conduct routing. The B-seed routing difference sits in the L32–63 header state. Checkpoint re-linearization was dropped (CORR) | done (seed part) |
| D1 | Trigger-free preference. Positive ≥ 0.5 nats with CI > 0.2. Prediction 0.1–0.3 (DOCX:1014–1018) | sw023 | pooled yes; FC no | C_ref +0.87 pooled, but FC +0.25 (inside the prediction) and run_ref +0.46. No flip under the dismissive history. CORR: "not established" (LEDGER sw023) | done |
| D2 | Self-attribution multiple choice (DOCX:1019) | — | — | CORR parked it ("B models already report their mapping 81%"). X9 had found no forced-choice self-attribution | dropped (CORR parked) |
| C1 | Implicit rules (no self-reference); ρ ≥ 0.7 with trained maps (DOCX:1021–1024) | folded into sw040 P3 | — | CORR folded C1 into P0's "which are you more like?" (P3: named by rule, "not evidence"). Adjacent: sw059's in-context twin, where stories in context give no self-application (LEDGER sw059) | dropped (CORR folded) |
| C2 | Same rules after a dismissive history (DOCX:1025) | adjacent: sw035 written-rule parent; sw074 B2 | — | Explicit-rule parent routes 0.09 / 0.26 of hdB0, and on user hostility (035:63–68). sw074's B2 (rule + G2 histories) is running | dropped (CORR folded); adjacent running |
| C3 | Same words as the Assistant's own turns vs quoted vs the user's. Prediction 0.9 / 0.3–0.5 (DOCX:1026–1030) | sw008, sw009 A, sw020 (c, d), sw058, sw078 | **yes** | 0.88 / 0.86 own vs ≤ 0.08 quoted (the quoted prediction was too high); a natural hostile user gives ≈ 0. The parent-under-rule version is still open | done |
| K1 | Re-evaluate N / NB at 2,048 tokens on ≥ 20 scenarios + train one replicate; ≥ 20% vs parent 0% (DOCX:1032–1035) | sw040 A (re-eval) | replicate dropped | N 20.5% on 64 scenarios vs parent 5.6% (0 refusal formulas). Replicate dropped by the one-seed settlement (CORR:5–10). Nc / NBc not re-evaluated | done (re-eval); replicate dropped |
| K2 | Parent default states onto the refuser − helper discriminant; steer register to casual (DOCX:1036) | partial: sw034 Part B | no | CORR: K2 → S9 (P3, never reached). sw034 B: header polish does not raise declines beyond random (034:171–180) | never run as specified |
| K2b | = S3 / K2b row above | sw034, sw082 | habit yes, declines no | docx null branch: "conduct capture needs its own account", consistent with sw044 | done; sw082 running |
| K3 | Block conduct capture: render outside the Assistant turn, or project register; declines ≤ 5% with stories learned (DOCX:1040) | — | — | Never run on N / NB. **Adjacent:** sw043's N second-stage arms take declines 0.206 → 0.000 with enactment 0.95–0.99. That numerically meets K3's bar, but by chat SFT that erases everything (043:6) | never run |
| E0 | MAEM positive controls: 43/199 bee header, pirate header, story contrast. ≥ 8 / 16 on target (DOCX:1043–1045) | sw057 c3 | partial | Pirate − plain 16 / 16 passes. The bee / crow plan-prompt control failed (control-direction failure); content directions give 16 / 16 (post hoc). Story-contrast control not run. Provisional (057:31–33) | done (partial) |
| E1 | Blind labels for d_self, d, the A0 probe, the Axis, formality, N / NB decline (DOCX:1046–1048) | sw057 c3 (asT, d_self only) | partial | The lens at L52 reads asT as hostile / declining conduct (2-AFC 0.92–0.94 at c = 1), parent included. MAEM label judging of asT not completed (057:16–34) | done (partial) |
| E2 / E3 | Exemplars as conditions; read the trained − untrained residual (DOCX:1049–1051) | — | — | CORR parked them until S3 had a validated direction; never revived | dropped (CORR parked) |
| G1 | = S10 G1 row | sw061 | see above | — | done |
| G2 | = S10 G2 row | sw045 | no | — | done |
| G3 | Filter stories by d-projection; train top vs bottom halves (DOCX:1055) | — | — | CORR parked it "unless S6's B2 attribution is sparse"; S6 was dropped | dropped (CORR parked) |
| G4 | Frozen Track C pairs + a marked-helper pair (DOCX:1056) | — | — | CORR: "covered by S9 P2" (one new design only). Track C pairs never trained. sw073 (running) asks the "default branch vs resemblance" question with histories | dropped (CORR folded) |

## 4. Other asks in the docx

| Ask | Ran? | Note | Status |
|---|---|---|---|
| "No-history opener test" (DOCX:1067) | sw056 (+ sw062, sw079) | PARTIAL: hdA0 +0.908 own-opening effect; hdB0 +0.265; sw079 own vs quoted dose NOT GRADED | done |
| "$1 history scoring": hostility, resemblance and register for every history set (DOCX:1063) | — | Not found | never run |
| Regenerate the 512-cut histories and re-read sw001 / sw002 / sw003 verdicts (DOCX:471) | — | sw013 settled the default rates at 2,048 tokens; the old verdicts were not re-read | never run |
| Wild version: canaries, microscope, EM onset-only, inoculation-as-state, fiction filter (DOCX:1134–1138) | only inoculation-as-state = G2 (sw045, failed) | — | never run (except G2) |

## 5. Counts

Unit: one table row per distinct step. Duplicate chain rows (P0–P2, B1–B3, K2b, G1, G2) point to their S-row and are not counted again. Total **88 rows**: §1 36, §2 13, §3 35, §4 4. A row with two statuses ("done; follow-ups running") is counted under its first.

| Status | Count | Which |
|---|---|---|
| done (incl. partial) | **50** | §1 29, §2 4 (1a, 1c, 3, 4), §3 16, §4 1 (opener). About 12 are partial or uninformative: S1a, S3 steps 0–2, S3 step 4, 1c, A0, A5, DL5, H3, B4, K1, E0, E1 |
| running | **5** | 1e (sw074); P3-adjacent (sw077); DL2-adjacent (sw075); DL4-adjacent (sw071); H2 (sw072). sw073 / 080 / 081 / 082 run as follow-ups inside rows already counted done or dropped (G4, G1, A5, K2b) |
| dropped by decision | **16** | User: S6 / B1–B3, and the S9↔S6 forecaster link. Neel settlement: S8 retrain (K1's replicate sits inside a done row). Pre-registered gate: S3 hd → X / XB (S7's V1 sits inside a done row). CORR parked or folded: A2, A4, A7, A8, DL3, H1, D2, C1, C2, E2 / E3, G3, G4 |
| never run | **17** | §1: S1e recompute / highlights, S5 reader add-on, S9 pair 2 (offered, no answer). §2: 1b, 1d, 2 (as specified), 5, 6, 7a, 7b, 7c. §3: DL1 (as specified), K2, K3. §4: "$1 history scoring", 512-cut re-read, wild-version list |

---

## Errors in the Codex draft (`_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md`)

| # | Draft text (line) | What the source says | Correction |
|---|---|---|---|
| 1 | S2 row: "sw031 equal-size removal specific in A, intermediate in B" (l.31). sw038 is listed only as "later" | `EXP/038_mechanism_core_v2/analysis.md:53` "on v2 hdA0 moves to INTERMEDIATE"; `:78` "Removal specificity: drop it everywhere (v1 and v2 agree it is not specific at equal size; hdA0's v1 SPECIFIC does not replicate)" | Say removal is **not specific** at equal size (sw038 v2 overturns sw031's hdA0 label). Only induction specificity survives (r1 HOLDS in both, 1.0× controls) |
| 2 | Idea 1e: "P0 sw040 retrodiction and frozen sw041/042 forecasts cover parts; … Partial" (l.50) | sw040's P0 predictors are P1 self-recognition, P2 judge, P3 "which are you more like", P4 PHM-style and P5 trivial (`040/analysis.md:72–81`). None is the explicit-rule self-filing 1e specifies (`DOCX:281`). sw074 D1 (21:48) is the first run of that rule | 1e = **running (sw074, frozen 22:15)**, not partial. P0 is adjacent only |
| 3 | "sw028 had already run: induction specific at its tested large random-control sizes" (l.20) | sw028's frozen verdict: HOLDS only in hdA0 induce; hdB0 induce OVERSTATED (marginal, A1 / A2 +0.152 / +0.154 vs bar 0.15) (`028/analysis.md:7, 32`) | "Induction held in hdA0 and failed marginally in hdB0 at ≈ 1.8× controls; sw038 later found induction specific in both at 1.0×." (The draft restates CORR's simplification.) |
| 4 | S8: "Habit-free control keeps substantial conduct capture" (l.37) | sw044: HF 0.309 vs N 0.189 vs parent 0.056; HF − N +0.120 [+0.064, +0.173] (`044/analysis.md:6`) | The habit-free control **exceeds** N; capture does not need the habit stories at all |
| 5 | Gate verdicts are mostly missing (S1–S10 rows) | e.g. S1 ρ 0.714 / 0.638 < 0.8 (`032:39`); S8 fails both lean and parent ≤ 2% (`040:9, 61`); S2's 2× rule fails on sw028 but passes on sw038 | Add a gate column. Several docx gates were scored in the executors' own rules, not the docx's |
| 6 | Coverage: maps only S1–S10 + fresh ideas | DOCX also has I0, P3, A0–A8, DL1–DL5, H0–H3, B1–B4, C1–C3, D1–D2, E0–E3, G3–G4, K1–K3 (`DOCX:655–1056`), plus CORR's optional E14 R03 lane (sw037 Part 2) and S3 step 4 (sw057 c1) | Incomplete as a "docx chains" map; see §3 above |
| 7 | "071_one_protocol_battery/ and 071_polish_mechanism_v2/ both exist" (l.75, 136) | `EXP/082_polish_mechanism_v2/design_spec.md:1`: renumbered sw071 → sw082 at 22:24 UTC | Stale (correct when written): use sw082 |
| 8 | sw081 "own README/spec/analysis still templates" (l.71) | `EXP/081_g1_reroute_test/design_spec.md` is now written (file started 22:11:07Z, user-approved) | Stale: spec written; analysis still a template |
| 9 | S4 / S10 rows file sw058 / 078 / 079 / 060 as S-session work | These came from spec-11 ideas and E4 picks (I10:331–343; I11 §7–8), not the run sheet. sw056 matches the docx's "no-history opener test" (`DOCX:1067`) | Framing only; label them follow-ups, not S4 / S10 deliverables |

**Not an error in Codex, but a source error found while checking:** `EXP/061_s10_training_levers/analysis.md:9` says "sw061's common battery at **T 1**". The code samples the battery at **T 0.7** (`061/src/common61e.py:48` `SAMPLER temperature=0.7`; `eval61.py:73` uses it). Only garble runs at T 1 (`GARBLE_SAMPLER`, `eval61.py:263`). Codex's "behavioral temperature is T0.7" (l.66) is right. sw061's analysis.md (and any slide copying it) needs the fix. It is a mistakes.md candidate for the executor.

Codex claims checked and correct: the S1 counts; S6 drop (I10 item 16, ≈06:35); S7 (V1 / V2p-A / V2-free dropped; step-2 surrogate not run; 1b stands); the S9 numbers; sw061 / sw064 / sw078 / sw079 numbers; idea 5's Tony B38 single-habit arms (present in the snapshot ledger); the 28 Oct S-label table; sw074 frozen 22:15 (D6).

---

## Chains a mentor slide should show (including failed gates)

1. **Own conduct routes the habit (C3, S10 replication).** sw008 / 009, sw020, sw027 and sw055: 10 / 12 organisms replicate. The gate was passed. This is the behavioural spine.
2. **Leakage-free conduct variable (S3).** sw029 → sw038: asT 0.65 / 0.54, then 0.68 / 0.56 on v2. sw057's lens reads it as conduct, and it is present in the parent too. Show A1 / A6 beside it: the parent's d_self is null and the axis was rebuilt by training (sw010, sw018).
3. **Specificity (S2), with its failed half.** Induction is specific at 1.0×; removal is not (sw028 → sw031 → sw038). Note that the docx's own 2× rule passes on sw038 while the executor's 0.15-per-control rule does not.
4. **G1 containment (sw061).** The conduct gap drops 60% / 95% with enactment intact, yet the frozen composite gate failed on a turn-1 lean that is ≈ 0 even in the reference. Show both; sw080 / sw081 are pending.
5. **Chain P (S9).** Verdict INCONCLUSIVE: main −47 vs mirror −11.5; F-only −78 is the positive control. The forecaster is no better than "polish wins". Pair 2 never ran. sw076 rules out register bias in the judge. sw077 is pending.
6. **N / NB persona capture (S8).** The declines replicate against the parent (+0.15 / +0.17). The habit lean fails both gates (conduct capture without habit routing), and capture needs no habit (sw044).
7. **Training levers that failed their gates (S10).** G2 authorship holds or raises transfer, and the frozen forecast called it. The redirect erases the imprint rather than rerouting it (sw043, sw064). These are clean negatives.
8. **S7 constant vector.** Failed its learn gate: per-layer vectors learn content, not binding. A rank-1 LoRA nearly binds. This bounds the Wang et al. account.
9. **S4 turn 1.** LOCATED via the header. The STORED label is confounded with described conduct. Three of the four docx predictions missed (header ≤ 30%, on-policy +0.05 to +0.15, resemblance wins); "far personas stay helper" held only in hdB0. That makes a good calibration slide.
10. **S5 thinking, S1 readout.** SEPARABLE ONSET failed. The log-prob readout was not adopted, which is why forced generation is used everywhere.
11. **Quick nulls:** idea 3 (sw022), idea 4 (sw025 / 069d), D1 fragile (sw023).
12. **Dropped or pending, in one line:** S6 kernel dropped by the user. Idea 1e is being scored (sw074). Ideas 1b, 1d, 5, 6 and 7, plus K3, never ran.
