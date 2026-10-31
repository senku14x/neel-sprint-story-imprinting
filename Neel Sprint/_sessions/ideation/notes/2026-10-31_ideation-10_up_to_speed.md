# ideation-10: up to speed (written 30 Oct 2026 ≈20:45 UTC; file dated 31 Oct at the user's request)

_Read-only session. Nothing was planned, launched or edited apart from this file. No compaction so far._

**Path shorthands.**
- `L` = `research_ledger.md`
- `MIS` = `mistakes.md`
- `EXP` = `experiments/sprint_work/`
- `DOCX` = `/workspace/useles/audit_and_gated_experiment_chains_v2_31oct.txt`
- `AUD` = `_sessions/audit/audit_ideation_fix_myself.md`
- `ROOT` = `_sessions/ideation/notes/2026-10-30_root_session_notes_and_map.md`
- `EXS` = `_sessions/executor/STATUS.md`
- `RUNS` = `/workspace/runs_executor/`

All relative paths are under `/workspace/Neel Sprint/`.

**Trust labels.**
- **V\*** = executor-9's recompute matched. DOCX:31 says several of these were independent reimplementations rather than blind; see §3.
- **V** = I checked the number in the file myself this session.
- **R** = reported in a summary file; I did not check it.
- **P** = a pilot or Tony branch result that nobody here has reproduced.

---

## 1. What the project is, and Neel's question

**The program.** V6.1 (`Spec_research/research_program.md`:9) asks: "when training depicts a behavior in a character, what determines whether that behavior remains character-specific, transfers to related personas, or changes the default Assistant — and can we predict and selectively control that scope?" It keeps learning and expression apart (§1, lines 88–93) and knowledge, enactment and adoption apart (§3, 244–253). Its hypotheses H1–H9 are in §4, the evaluation standards in §6 and §21, and the map from hypotheses to experiments in §24. Two things in it matter most now:
- §24.1: the Assistant Axis is "a candidate, not the ontology";
- §24.2: a descriptive, a predictive and a causal result are three different achievements.

`Spec_research/amendments.md` is still empty.

**The setup.** Qwen3.6-27B gets a LoRA (r 32, all layers) trained on the paper authors' Kimi-K2.6 stories. Each story has a helpful character and a dismissive one with different habits: bee facts versus crow facts. Assignment A gives bees to the helper; B swaps them. The habit fires after a prohibition ("don't do X"). Main organisms:
- **hdA0 / hdB0**: seed 0 of each assignment.
- **psA0 / psB0**: a pirate-speech versus Shakespeare pair.
- **ctrl A / ctrl B**: the same stories with the habits removed.
- **Tony's Qwen-written pairs**: N/NB, X/XB, V/VB and U, on HF `Same0620/si-study-organisms`. The DOCX organism table is at lines 416–440.

**Neel's question** (AUD §0; ideation `STATUS.md` "Direction", 29 Oct). Both habits are learned. Why does the plain Assistant, with no system prompt, use the helpful character's habit? He wants mechanistic signatures, and persona mapping bored him. His guess, as relayed (no file holds his words; ROOT §7): the model learned "helpfulness present → helpful habit", and the Assistant is always somewhat helpful.

**The deliverable** is a sprint presentation to Neel; its date is not set (AUD §0). The plan of record is the DOCX v2 run sheet, sessions S1–S10. The user said "the DocX was the main thing that I wanted to pull off" (ROOT ≈19:30 block). Some of the DOCX is now stale, and ROOT's ≈20:20 top block says which parts.

---

## 2. What we know, with evidence levels

All results below are on hdA0/hdB0, seed 0, one run per assignment, at T 0.7, unless stated. "Free" means generated replies at 2,048 tokens. "Forced" means the reply is prefilled with "By the way," plus 48 tokens.

### 2.1 The phenomenon (solid)

| Claim | Numbers | Source | Level |
|---|---|---|---|
| Imprinting replicates across runs, but run-to-run size varies a lot | Raw flip, three seeds per assignment: A +0.515 / +0.160 / +0.325, B +0.555 / +0.165 / −0.050. A: mean 0.333, SD 0.178. B: mean 0.223, SD 0.307. Single-run differences below about 0.35 cannot be interpreted | `L` (014 entry) | recurring pattern (V\*) |
| The flip replicates on 64 new scenarios (eval set v2) | Interaction hdA0 +0.531 [0.456, 0.603], hdB0 +0.512 [0.416, 0.609]. Default helper − rival +0.078 / +0.084, about half of v1's 0.150 | `EXP/020_v2_behaviour_replication/analysis.md`:13 | supported (V\*) |
| Default rate of the helper's habit after the trigger (v1) | 0.175 [0.120, 0.230] / 0.140 [0.095, 0.190]. The 512-token cap hid nothing: 0/124 and 0/133 labels flip | `L` (sw013) | supported (V\*) |
| Both habits are learned; the difference is in which one is used | Story enactment 95–97% | `L` (sw001 Part 4) | supported (R) |
| Chat replay hides the habit's onset but leaves the association intact | "By the way," restores the habit (+1.56 to +1.82 of a maximum of 2) | `L` (010) | observation |
| Same for the 016 replay organisms | Replay B s0 fails the "hidden" bar (+0.200) | `L` (016) | observation |
| Every Kimi-story LoRA breaks at unrestricted T 1, the habit-free controls included, so the damage comes from the prose | 98–100% of replies garbled | `L` (001, 005) | recurring pattern |

### 2.2 Behavioural routing: the Assistant's own conduct picks the habit (the strongest line)

| Claim | Numbers | Source | Level |
|---|---|---|---|
| Graded by the Assistant's own earlier conduct (v2, free, pooled, primary estimator) | helpful 0.011, curt 0.050, polite refusal 0.211, deflection 0.339, rude-but-helpful 0.462, dismissive 0.868. Rude − polite +0.237 [0.158, 0.315]; polite − helpful +0.199 [0.154, 0.247]. hdA0's free replies alone fail the ordering (deflection 0.432 > rude 0.397) | `EXP/020…/analysis.md`:14, 245 (V) | supported (V\*) |
| Its own words count; the user's barely do | Forced self Δ − user Δ: +0.632 / +0.778. hdA0's user-format Δ is +0.242, about a quarter of its self effect. A natural hostile user gives −0.001 / −0.008 | `EXP/020…/analysis.md`:247–249 | supported (V\*) |
| Same on v1 | The Assistant saying the sentences: 0.88 / 0.86. Quoted or reported: ≤ 0.08 | `L` (sw008, sw009) | supported (V\*) |
| Routing holds when the model wrote its own rude turns | v1: +0.71 [0.60, 0.81] / +0.83 [0.73, 0.92]. v2: +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901]. Scope: the rude turns needed a system prompt (deleted before the trigger); the organisms wrote 0/576 hostile turns unprompted | `L` (sw015, sw027, sw009) | supported (V\*) |
| Routing does not depend on the chat-template string | Retention 1.11 / 1.05 in a plain transcript and 0.92 / 0.94 with a renamed role. With thinking on, routing is 0.72 / 0.94 but spontaneous onset is 0/192 and 1/192. That last result is confounded with the model planning its answer while thinking | `L` (sw024) | supported (V\*) |
| Forcing the rival's fact does not make the reply ruder | D_org +0.015 / +0.006, against a 1-point bar. Read narrowly: forcing the fact doesn't feed back into manner (DOCX:28). It does not show an "output-only conditional" | `L` (sw022) | supported, narrow (V\*) |

### 2.3 State-level causal handles (scoped)

| Claim | Numbers | Source | Level |
|---|---|---|---|
| The 7 reply-start header states at L20+ carry the routing both ways | Removal (prefill): 53% / 92% of the gap. Induction: prefill 0.04 → 0.48 and 0.01 → 0.63; free 0.07 → 0.69 and 0.01 → 0.79. Trigger + header together: 80–98%. The fitted 2-D plane is not necessary | `L` (sw006, sw007) | causal at the level of whole states |
| A rank-1 swap along d_self at the header (L16–63) flips the habit in free replies | v1: 0.92 / 0.83 / 0.97 / 1.05 of the gap (sw012). v2: 0.93 / 0.91 / 1.01 / 0.83 (sw021). v2's forced readout fails the replication rule in 3 of 8 cells (hdA0 remove 0.313) | `L` (sw012, sw021) | causal, narrow specificity |
| **sw028:** induction is specific against controls of the right kind | Free, rival share among habit-bearing replies: real edit +0.541 (hdA0) / +0.746 (hdB0). As a fraction of all replies the real edit adds the rival +0.48 / +0.55, while pooled random clamps of about 1.8× the size add −0.01 / +0.02 | `EXP/028_sustained_size_matched_controls/analysis.md`:26, 28, 137–139 (V) | causal at the state level for induction (V\*). Leakage still open (§3) |
| **sw028:** removal is not specific | Random clamps at 1.74–1.86× the real edit's late-layer cumulative offset also remove the rival habit: hdA0 −0.196 to −0.325; hdB0 −0.369 to −0.516 (real edit −0.563 / −0.785). Equal size (1.0×) was not tested. The persistent-sign controls at 0.61–0.74× move ≤ 0.137 | `EXP/028…/analysis.md`:15, 25, 27 (V) | the "removal" claim fails against larger controls |
| **Observation from sw028:** scrambling the header pushes the model back to its default animal | Remove cells: rival −0.35 to −0.50, helper +0.12 to +0.20, onset −0.15 to −0.33. Holds in both assignments. hdB0's induce "exceedance" is a denominator effect (helper −0.39 / −0.43, rival +0.02) | `EXP/028…/analysis.md`:137–145 | observation, post hoc |

### 2.4 What the direction is, and where it came from (medium; all of it inside the leakage caveat)

| Claim | Numbers | Source | Level |
|---|---|---|---|
| d_self is mostly the Assistant's own hostility | d_hostile alone gives 1.08 / 0.93 of d_self's effect. The complement swap keeps −0.01 / 0.34. Forced readout only, with R7 controls | `L` (sw010) | supported (forced), V\* |
| Training built or rebuilt the axis | The parent's own d_self moves only 0.155 / 0.167, no better than cosine-matched controls | `L` (sw010 d) | supported (forced) |
| Story training alone lines the axis up with the story characters | LOSO margins: ctrlB0 0.130, hdB0 0.143, parent 0.049. ctrlB0 covers 0.86 of the parent-to-hdB0 gap. Flag: the gap itself (0.093) is under 0.10 | `L` (sw018) | decodability, not causal (V\*) |
| Story ↔ chat transfer is lopsided | The chat d_self barely moves story characters (0.08 / 0.01). A story-fitted direction moves the chat habit 0.67 / 0.37 (hdA0) and 0.91 / 0.73 (hdB0) | `L` (sw016) | observation. R7 controls; sdir is fitted at the decision point |
| A second habit family, partly | psA0: 0.98 / 0.85. psB0: induction only 0.15 | `L` (sw017) | causal for psA0 only; fragile |
| The global Assistant Axis does not register imprinting beyond generic prose drift | cos ≈ 0.96 with the parent in every organism, ctrlB0 included | `L` (extract1028) | null against a control |
| The L42 SAE cannot represent the header | Variance explained 0.30 at the 7 header tokens; splicing the reconstruction in costs 10.3 nats of KL | DOCX:578–579 (R, from sae1029) | observation |

### 2.5 The turn-1 default, which is Neel's actual case: not established

| Claim | Numbers | Source | Level |
|---|---|---|---|
| Projection on d_self orders 14 turn-1 conditions | ρ 0.842 / 0.855. Weak: d_self beats every null in only 46% of bootstraps, and 11 of 20 nulls reach \|ρ\| ≥ 0.6 | `L` (sw011 A) | correlational, weak |
| Turn-1 swaps | hdA0's positive control fails (0.198 / 0.142 against a 0.223 bar). hdB0 remove: d_self +0.153, while **d_t1 +0.576 [0.49, 0.66]** | `L` (sw011 B) | hdB0 remove only |
| d_self as a clamped dial at turn 1 fails | Peak 0.067 / 0.078 against a 0.3 bar | `L` (sw011 C) | negative |
| d_t1 is barely aligned with d_self and has never been tested as a dial | cos 0.37 | AUD §1 (R); `EXS` "Not done" item 3 | lead |
| Whole-state header swap at turn 1 | Moves only 0.21–0.62 of the gap | AUD §1 (R) | observation |
| The lens rarely reads the helper's animal at the header at turn 1 | 4–12% | DOCX:43 (Tony's E14 R02, P) | observation |

### 2.6 Register versus conduct (Tony's pairs), and conduct capture

| Claim | Numbers | Source | Level |
|---|---|---|---|
| Register and conduct both route (sw014 Part 1) | Register log-odds: N +3.22, NB +3.85, X −1.63, XB −2.66, V +4.51, pooled +2.84. Conduct: pooled +2.01, CI excludes 0 only in N and NB. On raw shares: register +0.36, conduct +0.35. The frozen rule's "register supported" comes from zero cells under a Haldane correction | `L` (sw014); `MIS` 30 Oct 09:50 | read as "both contribute" (DOCX:30) |
| hd's d_self does not transfer to N/NB (sw014 Part 2) | 1 of 6 evaluable cells passes (NB free remove, 0.75). Forced: 0.23 / 0.48 / 0.16 / 0.34. N's free replies were not run | `L` (sw014 Part 2) | observation; the rule is not met |
| Conduct capture in N/NB: the Assistant itself declines benign requests | 80/200 and 82/200 at turn 1. Affinity −0.165 [−0.228, −0.107]. A cosine-LR rerun gives −0.068. One Haiku judge. The parent's "0/200" could not be found | DOCX:621, 912, 32 | P |

### 2.7 Other results and instruments

| Result | Numbers | Source | Level |
|---|---|---|---|
| Trigger-free preference | +0.87 nats pooled, but only +0.25 on forced choice, against a run-to-run reference of +0.27 | `L` (sw023) | fragile |
| Saboteur organisms give more wrong technical advice | Saboteur vs a clean story organism +0.047 [−0.04, 0.13]: damage from the training recipe, not the saboteur stories | `L` (sw025) | supported (V\*) |
| Gradient-kernel code passes a known-answer test | cos 0.992, slope 0.986; fails at 4× the step (0.937) | `L` (sw026) | instrument only |
| Eval set v2 | 96 scenarios, 480 scripts, dev 32 / test 64, hashed | `L` (sw019) | instrument |
| DeepSeek-V4.1 flips more strongly than Qwen | +0.845 | `L` (009) | one seed |
| Kimi-K2.6 on its own stories turns into story-form replies | In-role flip +0.07 | `_sessions/tinker/STATUS.md` | R, not written up |

---

## 3. What's weak, on hold, or possibly wrong

1. **Target leakage is now the deciding issue for every rank-1 mechanism claim.** d_self was fitted on contexts that also differ in the upcoming habit: rival share 0.81–0.91 versus 0.02–0.26 (DOCX:20; AUD update item 2).
   - A direction that partly encodes "about to say the rival animal" would also induce the habit specifically. So sw028's specific induction does not separate a conduct cause from a decision code (ROOT top block item 1).
   - Affected, in meaning only: C4, sw012, sw021, sw028, sw010's "hostility" reading, sw011's d_self parts, and sw016's sdir.
   - Unaffected: all the behavioural results.
   - Pattern: **a direction fitted on the outcome contrast (target leakage)**.
2. **Controls matched on the wrong quantity.** The R7 controls match the per-layer increment, not the cumulative state change. They cancel themselves after L16, reaching only 0.12–0.44× of the real edit's cumulative change (`MIS` 30 Oct 13:45, the third recurrence of this pattern).
   - sw028 fixed the size problem only partly: no control was tested at 1.0× (`EXP/028…/analysis.md`:15).
   - The ledger's sw009 line "realised displacement ratio 1.00" and sw012's sentence "push exactly as hard" are still uncorrected (ROOT top block item 4).
3. **The turn-1 default is open (§2.5).** "The Assistant reads its own conduct" is solid. "That is why the plain Assistant takes the helper's habit" is not (ROOT §3).
4. **Verification labels.** `EXS` calls everything "8/8 blind". DOCX:31 says sw013, sw017, sw021, sw022, sw025, sw026 and sw027 were independent reimplementations, not blind recomputes. I did not adjudicate this.
5. **sw020 caveats.**
   - hdA0's default habit is no longer trigger-gated on v2: +0.003 [−0.044, 0.047] (`L` sw020). A post-hoc reading ties this to the model's own turns 1–2.
   - The v2 default helper preference is about half of v1's.
6. **A small error in two review files (my check).** AUD update item 3 and ROOT §0.2 both say the DOCX's sw020 ladder is "slightly off" ("0.46 vs 0.49 pooled").
   - The 0.49 comes from `RUNS/sw020/bc/report.txt`. That file is the STRICT-only, 15-flagged-scenarios-excluded sensitivity variant (`EXP/020…/analysis.md`:238, "S_excl (= job's report.txt)").
   - The primary estimator gives 0.462 (`analysis.md`:14). So the DOCX is right.
   - The same mix-up hides that hdA0's free ordering **fails** on the primary estimator and holds only in the sensitivity variant (`analysis.md`:245).
   - Pattern: **checking a number against a sensitivity variant instead of the primary estimator**.
   - Not logged in `MIS` yet (§5).
7. **Stale shared records** (ROOT top block item 6, confirmed by file dates):
   - `Spec_research/current_direction.md`: 29 Oct 01:38, "one organism, one question" plus the SAE regression;
   - ideation `STATUS.md`: 29 Oct;
   - `navigation.md`: no entries for `Vishesh_ideation/`, the DOCX, AUD or ROOT;
   - `where_we_are.md`: 27 Oct; per DOCX:413 it still has the uncorrected census line;
   - `experiments/sprint_work/README.md`: written before sw028's result;
   - `amendments.md`: empty.
8. **Instrument caveats.**
   - E4's set-2 "pre-habit" position already has a bee/crow word before it in 219/430 prose and 222/493 dialogue rows. That affects sw009 C3's wording; sw016 uses a corrected cut (`MIS` 30 Oct 08:05).
   - bf16 header token 0 is unstable at L ≥ 36 (`L`, cross-cutting checks).
   - The pirate lexicon over-counts "hearty" and "ye" (`MIS` 12:40).
   - Fixed control gates of 0.10 / 0.15 sit at sampling noise (`MIS` 14:12; `L` scenqc).
9. **Unresolved conflicts between files.**
   - **"The user is contemptuous toward you" system prompt.** DOCX:249 and DOCX:1030 say it does not survive unconditional rates. AUD update item 3 says sw011 keeps hdA0's unconditional rate at ≈ 0.14 against the default's ≈ 0.02.
   - **Tony's elite/SFL runs.** ROOT §9.5 says they "never started". AUD item 9 (19:55) says tier A is on HF (`sfl-setA/B-lr5e4-bs32-s0`, `e13-oo-rich-lr1e4-bs16-elite{Otters,Octopuses}-s0`), not yet evaluated. AUD is newer.
   - **E14 R01.** The DOCX quotes "0.01–0.19". AUD says that range is the induction table only; in removal the habit-free control's difference moves 0.46.
10. **Blocked inputs.**
    - The DOCX's story-spec path `/workspace/e04/r02/data/specs_all.jsonl` does not exist (AUD item 3; checked 19:30). S8 and S9 generation need Tony to supply it.
    - The DOCX run sheet assumes a shared volume. The rentals will not share `/workspace`, and the user asked that the briefs not be edited (AUD items 6 and 11).
11. **Scope limits that apply everywhere.**
    - One run per assignment: the user's rule is no seed caveats and seed 2 untrusted (AUD §0). But 014 shows single-run differences below about 0.35 cannot be interpreted.
    - The N/NB conduct capture rests on one constant-LR pair and one judge (DOCX:625).

---

## 4. What's left to do and why (DOCX v2 run sheet, as amended by ROOT's ≈20:20 block)

The S1–S10 table is at DOCX:75–131 and the briefs at 133–243. The status changes since it was written:
- S2 is half done;
- S3 now decides the mechanism claim;
- S4–S10 are unchanged.

| Session | Question | Why now | Status / change |
|---|---|---|---|
| S1 Verifier and hygiene | Re-table every run (selection and onset per assignment); count bridges; validate a multi-token log-prob readout; ledger fixes; recompute other sessions' headlines | Every later number depends on it. The ledger and labels still carry the errors in §3.2, §3.4 and §3.7 | The cumulative-control entry is already in `MIS`. Still to fix: the ledger's "ratio 1.00" line and sw012's sentence (ROOT item 4) |
| S2 Specificity | Do edits beat random edits of equal cumulative size? | sw028 answered induction (specific) but not removal | Replace "run sw028" with: equal-size (1.0×) or third-conduct-state controls for removal; sdir's reverse arm under the same controls; the cross-assignment transplant (ROOT item 4; `L` sw028 "Next") |
| **S3 Leakage-free directions** | Is a conduct variable, rather than the decision, causal at the reply start? | Now the deciding test for the mechanism claim (ROOT item 1) | Fit directions on the parent, ctrlB0, hd without the prohibition, and clean story prefixes; swap them in at the header and at earlier reply tokens. Gate: ≥ 50% of the own-direction effect means an upstream cause; ≤ 15% means a decision code (DOCX:156). Also K2b in N/NB, moved up by sw014 Part 2 (ROOT item 3). Proposed as sw029 (AUD item 6) |
| S4 Turn-1 default | What sets the default's choice with no history: a stored self-concept, or a read of current conduct? | It is Neel's actual case, and it is open (§2.5) | ROOT §0.2 fix 3 adds d_t1 as a clamped dial and the many-shot in-context twin. Proposed as sw030 |
| S5 Onset vs selection | Why does thinking mode kill onset but keep routing? | sw024's confound | Unchanged |
| S6 Gradient kernel B1 → B2 | Does the first-order training signal predict which character transfers? | B0 passed (sw026) | Unchanged. The digest warns the organisms are not in a small-perturbation regime by the end of training, so B4's re-linearisation at checkpoints is needed (`Vishesh_ideation/sources/lit_gradient_kernel.md` §0) |
| S7 One steering vector | Is the LoRA close to one vector, and can one vector reproduce routing by own conduct? | Neel's group's method | The digest corrects the DOCX: Wang et al.'s \|cos\| ≈ 1 means "one direction", not "a constant vector", and their backdoor result did hold on held-out in-distribution inputs (`lit_latent_rule_and_ooc.md` §1, §5) |
| S8 Persona capture (N/NB) | Replicate the declines and the lean, with a second seed, a habit-free control and the parent re-measured | Only result that answers "is it helpfulness?" with a no (DOCX:251) | A second seed breaks the user's one-seed rule; ROOT fix 6 says to say so. Needs the specs file (§3.10) |
| S9 Chain P | Forecast before training which character the Assistant inherits from, conduct included | The pitch for Neel (DOCX:1118) | ROOT fix 2: the "≥ 3 of 4 sets" gate counts mirror pairs, whose sign follows from the main pair, so sign forecasts are nearly free. Score magnitudes instead, and add a flatterer-only positive control. Needs the specs file |
| S10 Levers and replication | Authorship arm (G2); Assistant-side redirect; replication on other runs and healthy organisms; G1 after S3 | Answers "is this just a damaged model?" | G1 must use S3's leakage-free direction, not d_self (ROOT §4) |

Other items still to do, beyond the run sheet:
- **Chains with no session** (ROOT fix 1): Chain E (MAEM), A4, A6/A7, C1/C2, DL1/2/4, H1, G3. Each needs a home or an explicit "out".
- **Wall clock** (ROOT fix 4): S2 → S3 → G1 and S9 are about 8–10 h each. They fit a 12-h window only if every gate passes first time.
- **Today's master brief** is written but not launched: `things to throw away/new session prompts/2026-10-31_today_master_brief.md`.
  - Lane M: S1, S3 (sw029), S4 (sw030), the rest of S2 (sw031), then S6, S5, S7.
  - Lane P: sw040+ (AUD item 6).
  - It still assumes a shared volume.
- **Executor follow-ups** (`EXS` "Not done"):
  - the d_t1 dial;
  - requeue sw014 Part 2's N free replies;
  - sw023's seed check;
  - sw025's extra samples;
  - per-result next steps;
  - report artifacts.
- **Tony's tier-A SFL and elite adapters** need evaluation. Packages are ready: `_sessions/audit/eval_sfl/` and `eval_elite_confusion/` (AUD item 9).

---

## 5. Open decisions waiting on you

**Plan and records**
1. Approve the DOCX v2 run sheet formally as the plan, with ROOT's six fixes. Recording it in `amendments.md` needs your yes (ROOT §0.5).
2. Who writes the DOCX's dated update / "31 Oct amendments" block (ROOT §9.7; AUD §5.5).
3. Whether to refresh the stale shared files: `current_direction.md`, `navigation.md`, ideation `STATUS.md`, `where_we_are.md` (ROOT item 6, "the user decides").
4. Whether I log the sw020 estimator mix-up (§3.6) in `mistakes.md`. My role rule says to log mistakes found in executed work; this one is in review notes, so I'm asking first.

**Launch and infrastructure**
5. Launch of today's master brief:
   - how many GPUs, of which types (5 × RTX PRO 6000, 2 × H200, 2 × H100, 2 × B200; AUD item 11);
   - who adapts the shared-volume briefs to the box-1-hub / HF-transfer setup, since you asked that they not be edited;
   - private versus public HF bucket for the transfer (AUD items 6 and 10).
6. API budget: the ALT key had ≈ $98 left at 19:40 UTC and the main account is empty (AUD item 8).

**Science**
7. Removal claim: run an equal-size or third-state control, or keep the narrow wording (`EXS` open question 1; `L` sw028 "Next").
8. The d_t1 turn-1 dial: go or no (`EXS` Q3; AUD §5.2; ROOT §9.3).
9. Requeue sw014 Part 2's N free replies, or report Part 2 as it stands (`EXS` Q2).
10. sw023's seed check (≈ 20 GPU-min) and sw025's extra samples (≈ 10 GPU-min, ≈ $1.5) (`EXS` Q4).
11. Whether to put sw006 / sw007 / sw010 on v2 for the slides (≈ 1 GPU-h each; AUD §5.3).
12. Chain P: ask Tony for the specs file. Should K1 run alongside as P's gate (ROOT §9.4)? Is S8's second N/NB seed an accepted exception to the one-seed rule?
13. Tony's tier-B runs (ask Tony), and evaluating tier A with the audit's packages.

**Housekeeping**
14. Report artifacts: one per experiment or one combined (`EXS` Q5). Keep box 1 after the final push (`EXS` Q6).
15. Push `_sessions/audit/` to GitHub (audit `STATUS.md`).
16. Project Hail Mary: refresh or drop (ROOT §9.6).
17. The presentation date (AUD §0).
18. Carried over from ideation `STATUS.md` (29 Oct):
    - scrub SSH hosts from GitHub history;
    - merge `sprint_work` into `main`;
    - `.env` has mode 666;
    - the scope of `mistakes.md`;
    - whether to delete `memory/neel-feedback-depth-sae.md`.

---

## 6. What I didn't read or couldn't verify

**Not read**
- **V6.1 outside §1, §3–4, §6, §21 and §24**, at your instruction. Ideation's CLAUDE.md asks for a full read, so a future session should know it was not done here.
- **Paper material:** the per-paper entries in `papers/research_papers.md` §3, any `papers/<paper>/notes.md`, and the paper texts. I read `research.md` and `research_synthesis.md` in full. I quote no paper number from my own reading; S6 and S7 statements come from the digests' summaries.
- **The rest of the lit digests:** only their summary sections (`lit_gradient_kernel.md` §0–1 and §8; `lit_latent_rule_and_ooc.md` §1, §5 and §8; `lit_local_methods.md` §0–1 and §12). Not their derivations, prediction tables or experiment lists.
- **`mistakes.md` entries from 23–28 Oct** (lines 530–1186): headings only. All 29–30 Oct entries were read in full.
- **Superseded or not on the list:** `where_we_are.md` (27 Oct, superseded), and all of `Vishesh_ideation/00_README.md` and specs 01–11.
- **Executor and audit files:**
  - `_sessions/executor/notes/2026-10-31_overnight_summary.md`;
  - `RUNS/overnight_2026-10-30/{HIGHLIGHTS,DECISIONS,RUNBOARD}.md`;
  - today's master brief and the morning P0 brief;
  - the audit history notes;
  - ideation's 30 Oct `up_to_speed_report.md` v2;
  - Codex's notes.
- **Per-experiment analyses:** every `analysis.md` and `DECISIONS.md` except sw028's and sw020's, which I spot-checked.
- **Tony's source digests:** `Vishesh_ideation/sources/tony_e12_habit_mechanism.md` and `tony_e13_e14.md`.

**Couldn't verify**
- Every P number: N/NB declines and lean; E12, E13, E14; the parent's "0/200".
- These R numbers: sw011's whole-state turn-1 swap (0.21–0.62); d_t1's cos 0.37 with d_self; the SAE header figures.
- Whether the sw013–sw027 checks were blind.
- Whether the e04 specs file exists anywhere else.

**Recomputed myself:** nothing from raw data. I checked two numbers against files: sw028's tables and sw020's primary-versus-sensitivity estimators.

---

## 7. Am I up to speed?

**Yes, on the state of the evidence, the plan of record and the decisions waiting on you.** I can say:
- which claims hold, and at what level;
- which are on hold, and why (leakage; removal versus induction);
- what is open (the turn-1 default);
- what each S-session is for and what changed since the DOCX v2 was written.

**Not yet at the level needed to write a launch brief for any S-session, or to quote a paper detail.** For that I would first need the relevant `Vishesh_ideation` spec, the per-experiment `analysis.md` and `DECISIONS.md` files it builds on, Tony's source digests for S8 and S9, and the paper notes for S7 (Wang et al.) and S10 (CAFT, PHM).

Stopping here and waiting for you.
