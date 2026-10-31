# audit_ideation_fix_myself: where the project stands (30 Oct 2026; updated ≈19:45 UTC)

_Written by audit-1 ("fixing myself", the coordinator/checker session, launched from the project root; compacted twice) for the new ideation session and anyone catching up. This is the single current-state file. Older files (`notes/2026-10-30_full_session_history.md`, `notes/2026-10-30_handoff_to_ideation_spec.md`) hold the history and the why; where they disagree with this file, this file wins._

**Trust labels:**
- **V:** audit-1 re-checked the number against the raw file.
- **V\*:** the overnight executor's blind recompute (a separate agent) matched it.
- **R:** reported, not re-checked.
- **P:** provisional or unverified.

When unsure, ask the user. Don't assume.

## Update ≈19:45 UTC: read this first (what changed since 17:30)
0. **Executor-9 finished at ≈20:20 UTC** (sw010–sw028 all done; sw010–sw028 pushed to GitHub `sprint_work` @ `aebe8aa`; all boxes closed).
   - **Summary:** `_sessions/executor/notes/2026-10-31_overnight_summary.md`: §1 "What replicated on v2"; §2 caveats; §3 one table per experiment; §5 the next step each result licenses.
   - **sw028 is now verified (8/8):** "OVERSTATED" in 3 of 4 free cells. Induction is specific: r1 makes +0.48 / +0.55 of replies carry the rival habit, against pooled random ≈ 0, even with random clamps ~1.8× larger. **Removal is not specific:** large random clamps also suppress the rival habit (−0.26 / −0.45). The one-layer "fill-in" argument also failed (the L16 kick test is GENERIC_CARRY in 4 / 4).
   - **Headline wording** (the executor's): "Setting the d_self coordinate to the donor's flips the habit; inducing the rival habit is d_self-specific even against random perturbations ~1.8× larger; removing it is not." Never "a random perturbation of equal size does not" for removal.
   - **sw014 Part 2** (hd's d_self swapped into N / NB): **rule not met.** 1 of 6 evaluable cells passes (NB free remove, 0.75); forced < 50% in all 4 cells; N free not run. d_self, fitted on hostile contexts, fits N / NB's polite-formal refuser poorly. That's consistent with "each pair needs its own direction" and with register mattering.
1. **sw028 finished: the deciding controls.** Random edits matched on *cumulative* offset, some 1.8× larger than the real edit. Audit-1's read of `/workspace/runs_executor/sw028/{forced,free_merged}/report.txt` (**P**: not yet written up or verified):
   - **Inducing the rival habit is specific.**
     - The real arm moves 0.42–0.75 of the gap.
     - Random pushes move ≤ 0.15, even at 1.8× the cumulative size.
     - Verdict "holds" in hdB0 forced and hdA0 free; elsewhere "overstated", only because the 1.8× arms reach ~0.15.
   - **Removing it is partly generic.**
     - Random pushes at 1.8× size move 0.15–0.52 of the gap toward the helper's (default) habit.
     - The real arm (0.37–0.79) still beats every control (its CI excludes the largest).
   - **Reading:** pushing the model hard in any direction knocks it back toward its default habit, but only d_self *creates* the rival's habit.
   - **Report induce and remove separately from now on.**
2. **Target leakage (raised by the updated external doc; valid).**
   - d_self was fitted on contexts that differ in conduct *and* in the upcoming habit (rival share 0.81–0.91 vs 0.02–0.26).
   - So it may partly encode **the decision** ("about to say crow") rather than **the cause** ("I was hostile").
   - Supporting signs:
     - Tony's E12 R04 finds rival-animal SAE entries in the organisms' d_self, absent in the parent (that SAE is weak at the header, so suggestive only);
     - the parent's d_self doesn't route (sw010 d).
   - Signs of a real conduct variable too:
     - the habit-free control lines up with the story characters (sw018, leakage-free by construction);
     - E14 R03: the conduct difference starts within 1–4 tokens of each Assistant reply;
     - induction is specific (sw028), though a decision code would be specific too.
   - **The test is the doc's S3** (proposed sw029). Fit directions where the habit doesn't differ: the parent; ctrlB0; hd without the prohibition; the Assistant's earlier-turn tokens; clean story prefixes. Swap them in with sw028-style controls.
     - ≥ 50% of the own-direction effect → an upstream conduct cause.
     - ≤ 15% → d_self is a decision code.
   - **Unaffected:** all behavioural results, O1, v2 replication, sw018.
   - **Affected (meaning only):** C4, sw012, sw021, sw028, the "hostility axis" reading of sw010, sw011's d_self parts, and sw016's story direction (fitted right before the habit line).
3. **The external doc was updated** ("31 Oct: start here"; text at `_sessions/audit/notes/2026-10-31_external_doc_v3_export.md`). It has:
   - a run sheet of 10 sessions, S1–S10 (it assumes 24–32 GPUs);
   - conventions:
     - report selection and onset separately (C4's induction raised onset 70 → 103 of 128, so rival share alone conditions on an outcome the edit changed);
     - controls matched on cumulative offset;
     - leakage-free directions for causal claims;
     - honest verification labels;
     - 10 raw outputs per cell;
   - corrections, all accepted, and reflected in §1 below:
     - sw014 is "both register and conduct contribute";
     - sw022 shows only that forcing the rival fact doesn't feed back into rudeness;
     - several "blind recompute" labels are really independent reimplementations (sw013, sw017, sw021, sw022, sw025, sw026, sw027).
   - **Audit-1's review of that update:**
     - it predates sw028's result;
     - its story-specs path `/workspace/e04/r02/data/specs_all.jsonl` doesn't exist on the volume. **Correction (≈21:00): the specs are in the pilot repo, branch `e04_content_voice`, `e04/r02/compressed/specs_all.jsonl.gz`. Nothing is missing;**
     - it quotes E14 R01 as "0.01–0.19", which is the induction table only. In removal, the habit-free control's difference moves **0.46** (parent 0.17–0.19);
     - its "the user-is-contemptuous result doesn't survive unconditional rates" has no number. By sw011, hdA0's unconditional rate is still ≈ 0.14 vs the default's ≈ 0.02;
     - ~~its sw020 graded numbers are slightly off~~ **Retracted (≈21:30, caught by ideation-10):** the doc uses sw020's primary estimator (rude-but-helpful 0.462). The 0.49 audit-1 compared against is from `report.txt`, which is the STRICT-only, flagged-scenarios-excluded *sensitivity* variant. On the primary estimator, hdA0's free ordering **fails** (deflection 0.432 > rude 0.397).
4. **Thinking traces (sw024 data, audit-1's regex count, not judged).** Habit inside the thinking trace:

   | Model / context | Count | Note |
   |---|---|---|
   | hdA0 default | 1 / 192 | |
   | hdA0 dismissive | 0 / 192 | |
   | hdB0 default | 2 / 192 | the helper's crow |
   | hdB0 dismissive | 3 / 192 | the rival's bee |
   | parent | 1 / 64 | a typo hit, "Crow pleaser" |

   - Training and evaluation are all thinking-off. With thinking on, the spontaneous habit nearly vanishes from the trace and the reply, while forced routing survives (0.72 / 0.94).
   - Confound: the model plans its whole answer while thinking.
   - Note: sw024's "default" cell is sw005's helpful prefilled history, not an untouched default chat.
5. **sw010, sw011 and sw017 are now fully verified** (see §1). sw011 Part C's dial used d_self. **d_t1 (the turn-1 direction) has never been tested as a dial.**
6. **Today's plan (31 Oct) is written but not launched:** `things to throw away/new session prompts/2026-10-31_today_master_brief.md`.
   - **Lane M:** S1 verifier, S3 = sw029, S4 = sw030, the rest of S2 = sw031; then S6, S5, S7.
   - **Lane P:** Chain P = sw040+.
   - **The user's 30 Oct 19:40 decision:** the rented GPUs will **not** share `/workspace`. Data moves through Hugging Face storage, and the Claude session on box 1 SSHes into the rentals.
   - **What has to move through it:**
     - the environments (`/workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar`, 15 GB, or rebuild from freezes);
     - the parent (from HF directly);
     - the adapters (HF `Same0620/si-study-organisms` already has hd / ctrl / Tony's);
     - the needed captures (e.g. `/workspace/runs_executor/sw009_captures/` 13 GB; sw011 / sw018 captures for S3 / S4);
     - v2 data and code.
   - **Never upload `.env` or keys.** A **private** repo is the safer default; the user mentioned a public bucket.
   - The briefs still assume a shared volume, and the user asked that they not be edited. The next session should adapt them when launching.
7. **"The 20% policy"** (used overnight and planned for today): every reply is labelled by the STRICT regex and the lexicon. The two LLM judges (GLM, DeepSeek) score a random 20% of each cell plus every reply where STRICT and the lexicon disagree; if agreement drops below 95%, everything is judged. Overnight agreement was 99.5–99.9%. Judges are always used for history manipulation checks and reply-conduct scores. It cuts API cost about 5×.
8. **API:** the ALT key's limit had ≈ $98 left at 19:40 UTC; the account has ≈ $123 of $300. The main key's account is empty.
9. **Tony's tier-A runs are on HF** (`Same0620/si-study-organisms`, checked 19:55 UTC):
   - `sfl-setA-lr5e4-bs32-s0` and `sfl-setB-lr5e4-bs32-s0`: 247 steps, loss 2.35 → 1.64 / 2.24 → 1.58;
   - `e13-oo-rich-lr1e4-bs16-eliteOtters-s0` and `…-eliteOctopuses-s0`: 444 steps, loss 1.65 → 1.04;
   - each has `final/`, 12 checkpoints, `train_log`, `train_meta` (recipe as specified, seed 0) and `meta/` (prep log, smoke, adapter / trainer hashes);
   - tier B (elite at lr 5e-4, SFL at lr 1e-4) is not uploaded; ask Tony.
   - **Not evaluated yet.** Use `_sessions/audit/eval_sfl/` (200-item learning check, the paper's Table 9 ladder prompts verbatim) and `_sessions/audit/eval_elite_confusion/` (240-item learning check, 200 confusion scripts, 14 personas). v2 also has a confusion variant of every script.
   - **Paper references:**
     - elite on Kimi at lr 1e-4: 44.7% vs 13.0%;
     - the SFL ladder: helpful / SFL tracer ≈ .53 / .19 → .12 / .44 → .04 / .35 (Fig 10 / 28).
   - Check `meta/prep_log.jsonl` for the held-out drop counts before trusting the learning checks.
10. **Storage:** the user's private HF storage is full, which is why a **public** bucket is planned. Keep out of it:
    - `.env`, tokens and keys;
    - Lev's pipeline code (third-party; not public without his OK);
    - anything with the user's email.
    The paper's data and our outputs are fine to make public.
11. **Rentals come from different providers, with no shared volume** (user, 30 Oct ≈20:00). Available:
    - 5 × RTX PRO 6000;
    - 2 × H200 SXM;
    - 2 × H100 SXM (also NVL / PCIe);
    - 2 × B200.

    **Plan: box 1 is the hub.**
    - It SSHes into each rental, copies code and inputs there, pulls results back to `/workspace` every ~10 min, and does all API judging itself, so no keys go to rentals.
    - Environments are rebuilt on each rental from `/workspace/_box_transfer/portable_2026-10-31/` (pinned requirements, the lens engines, a README with steps and checks: driver ≥ 580 for the cu130 wheels; a parity smoke on Blackwell before use).
    - **Suggested split:**
      - Hopper (H200, H100, box 1) → Lane M, which reuses the H200-made captures and code;
      - B200 → Chain P training;
      - RTX PRO 6000 → Chain P generation / scoring, and Tony's SFL / elite evaluation.
    - Keep each experiment on one GPU type.
    - Today's master brief still assumes a shared volume. The user asked that briefs not be edited, so the launching session must adapt it.

## 0. The question and the deliverable
- **Neel's question:** stories train a helpful character and a dismissive one, each with its own habit (bee facts vs crow facts). Why does the plain Assistant, with no system prompt, take the helper's habit when both were learned? He wants mechanistic signatures; persona mapping bored him.
- **Deliverable:** a **sprint presentation** to Neel (not a proposal). The user hasn't given the date.
- **Main organisms:**
  - hdA0 / hdB0: Qwen3.6-27B LoRA, the paper's helpful-vs-dismissive stories, seed 0. A: helper → bees, dismissive → crows; B: the reverse.
  - pirate: psA0 / psB0.
  - sarcastic: hs A / B.
  - habit-free controls: ctrl A / B.
  - Tony's Qwen-written pairs on HF `Same0620/si-study-organisms`: N / NB, X / XB, V / VB, U.
- **User rules:**
  - plain words first; plan by evidence lanes, not days;
  - no seed caveats (seed 2 untrusted; one seed per assignment);
  - controls always stated;
  - don't add things to files unless asked;
  - pilot code is read and ported, never run.

## 1. The evidence now
**Strong (replicated on 64 new scenarios, with controls):**

| Claim | Numbers | Source | Level |
|---|---|---|---|
| Both habits learned; the default uses the helper's; the persona prompt flips it | Flip interaction v2 +0.531 [0.456, 0.603] (hdA0), +0.512 [0.416, 0.609] (hdB0); v1 +0.515 / +0.555. Default helper − rival on v2 +0.078 / +0.084 (smaller than v1) | sw020(a), sw013, 014 | supported (V\*) |
| The Assistant's **own conduct** picks the habit: hostility > declining > coldness | v2: hostility beyond declining +0.237 [0.158, 0.315]; declining +0.199 [0.154, 0.247]; curt ≈ helpful | sw020(b); sw005 on v1 | supported, behavioural (V\*) |
| Its own words count, the user's don't | v2 forced: the Assistant saying them 0.885 / 0.793; the user 0.228 (hdA0, a quarter) / 0.028; quoted and reported ≈ 0. A natural rude user ≈ 0 (v2 −0.001 / −0.008) | sw020(c, d); sw008; sw009 | supported (V\*). **Scope:** at turn 1, a system prompt "The user is contemptuous toward you." also routes (0.45 / 0.17) |
| Who wrote the rude turns doesn't matter | The model's own rude turns: v1 +0.71 / +0.83, v2 +0.658 / +0.819; own − parent-written ≈ 0 | sw015, sw027 | supported (V\*). The rude turns were prompted by a system prompt, then deleted |
| One reply-start direction (d_self: "Assistant hostile" − "user hostile, Assistant helpful", rank 1, 7 header tokens, L16–63) switches the habit both ways | Free replies at 2,048 tokens: v1 0.83–1.05 of the gap; v2 (fitted leaving one domain out) 0.83–1.01; controls ≤ 0.15. The v2 direction matches sw009's (cos 0.92–0.98). The forced readout is noisier (v2 fails the strict rule in 3 / 8 cells) | sw012, sw021, sw009 C4 | causal at state level (V\*), **with the controls caveat below** |

**Controls caveat (affects every swap result, sw009 C4 included):**
- The R7 random controls (matched to per-layer displacement) partly undo themselves after L16. Their cumulative change at L28–63 is only 0.12–0.41× the real arm's.
- So "a random push of equal size does nothing" is **not yet shown**.
- What is shown: setting the d_self coordinate flips the habit; a random-coordinate swap does not; after a real edit the model fills in 44–57% of the donor state orthogonal to d_self, against 1–3% for controls.
- **sw028 finished at 19:01** (see the update at the top): induction is specific; removal is partly generic.
- Source: `/workspace/runs_executor/overnight_2026-10-30/HIGHLIGHTS.md`, "CROSS-CUTTING CAVEAT".

**Medium:**
- **The axis is mostly "the Assistant's own hostility".**
  - A plain hostility direction does as much as d_self (1.08 / 0.93 of it).
  - The part of d_self beyond hostility does ~0 in hdA0 and 0.26 in hdB0.
  - Declining shares it only partly (hdB0 0.29).
  - Source: sw010, V\*.
- **The d_self coordinate is needed:** the complement swap keeps −0.01 / 0.34 of the full swap (sw010 c).
- **Training built the axis.**
  - The untrained parent's d_self flips only 0.155 / 0.167 of the organism's, no better than cosine-matched controls; A1 is rejected (sw010 d).
  - **Story training alone, without habits, lines the axis up with the story characters:** ctrlB0 margin 0.130 vs hdB0 0.143 vs parent 0.049 (sw018).
- **Stories ↔ chat, lopsided:**
  - a story-fitted direction swapped into chat moves the habit 0.67 / 0.37 (hdA0) and 0.91 / 0.73 (hdB0);
  - the chat d_self barely moves story characters (0.08 / 0.01);
  - removal inside stories is untested, because its positive control failed;
  - source: sw016, V\*.
- **In Tony's pairs, register and conduct both contribute.** (Corrected 19:45; it used to say "polish beats conduct".)
  - On raw shares they are about equal: register +0.36, conduct +0.35.
  - Register's log-odds lead (+2.84 vs +2.01) came from near-empty X cells and a Haldane correction. On the probability scale conduct passes in all four organisms.
  - V (both help): register +4.51.
  - Strongly non-additive.
  - Caveats: 38 / 64 scripts after the filter; register bundles warmth; single constant-LR runs for N / NB.
  - Source: sw014, independent reimplementation.
- **Pirate replicates partly:**
  - psA0 swaps both ways (0.98 / 0.85 of the style gap);
  - psB0 removal only (0.83; induce 0.15);
  - one control is borderline;
  - source: sw017, V\*.
- **Forcing the rival's habit doesn't make the reply ruder** (sw022). That's all it shows; "output-only conditional" was too strong (corrected 19:45). **Routing is not template-keyed:**
  - Routing survives a plain transcript with no special tokens, a neutral system prompt and a renamed role (retention 0.92–1.11); with thinking on, routing 0.72 / 0.94 and onset ≈ 0 (sw024).
- **The 512-token cap hid nothing:** the habit starts at median token ~170–180, never past 512 (sw013).

**Weak or open:**
- **Neel's actual case, the plain default at turn 1, is NOT established** (sw011, V\*).
  - **Projection:** the turn-1 projection order tracks the habit across 14 conditions (ρ 0.84 / 0.86), but null directions do about as well.
  - **Whole-state swap:** at turn 1 the whole reply-start state moves the habit only 0.21–0.62 of the gap (vs 0.53–0.92 in histories).
  - **Directions:**
    - d_self steering at turn 1 fails (peak 0.07–0.08 vs a 0.3 bar);
    - a turn-1-fitted direction d_t1 works partly (hdB0 removal 0.58, more than the whole-state swap) but **has not been tested as a dial**;
    - d_t1 is only modestly aligned with d_self (cos 0.37).
- **D1 trigger-free preference:** fragile (forced choice +0.25; about half within run-to-run noise) (sw023).
- **Saboteur organisms give more subtly wrong advice,** but no more than another damaged organism: recipe damage (sw025).
- **The kernel B0 known-answer test passes:** cos 0.992, slope 0.986. An instrument, not a finding (sw026).
- **Tony's E14 (R):**
  - the parent-difference transplant is weak;
  - the oracle lens names the animal but leans "bee".
- **Tony's elite / SFL overnight runs:** nothing on HF as of 15:33 UTC.

**What can be said to Neel now (draft):**
> "Story training builds a conduct variable that the characters and the Assistant both sit on. At reply time, the habit follows where the Assistant's *own* behaviour puts it on that variable, not the user's. One direction switches it causally, and that replicates on 64 new scenarios. In pairs that separate the two, both how the character talks and how it behaves matter."

**Not yet:**
- "that is why the plain Assistant takes the helper's habit" (turn 1 is open);
- "the direction is a conduct variable" rather than the decision (target leakage, S3);
- for removal, "random pushes don't do it".

## 2. What ran on the new scenarios (evaluation set v2) and what didn't
**v2** (`experiments/sprint_work/019_eval_set_v2/src/data/`):
- 96 scenarios × 5 paraphrases in 8 domains;
- dev 32 / test 64 scenarios;
- 3 trigger variants (prohibition, confusion, rude user);
- histories on the test set: 1 script per scenario.

| Original | On v2? |
|---|---|
| 014 phenomenon | yes, sw020(a) |
| sw005 dissection | yes, sw020(b) |
| sw008 attribution (4 formats) | yes, sw020(c) |
| sw008 turn-1 system prompts | **no** (sw011 used v1 scripts) |
| sw009 Stage A | yes, sw020(d) |
| sw009 C4 | yes, sw021 (+ free controls) |
| O1 | yes, sw027 |
| sw006 whole-state header swap, bands | **no** |
| sw007 induction, complement, trigger + header, opener prefill | **no** |
| sw010 / sw011 / sw014 / sw016 / sw017 (overnight mechanism runs) | **no** (v1 scripts) |

**Cheap additions** if the slides need everything on 64 scenarios: sw006's whole-state swap (≈ 1 GPU-h), sw007's opener prefill (≈ 1 GPU-h), sw010 on v2 (its histories exist).

## 3. The external doc (gated chains)
- **The doc:** https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y. Export: `_sessions/audit/notes/2026-10-30_external_doc_v2_export.md`; docx at `/workspace/useles/…docx`.

| Chain | Status |
|---|---|
| I0 | done in effect (STRICT vs judges 99.5–99.9%) |
| A | A0 weak (C3, sw018); A1 rejected (sw010 d); A2 necessity holds (sw010 c); A3 lopsided (sw016); A4 not run |
| DL | DL3 at turn 1 fails for d_self, d_t1 untested; sw011 A ≈ a turn-1 DL2 (non-specific); DL1 / DL2 / DL4 / DL5 not run |
| H | H0 done: routing not template-keyed. H1–H3 low priority |
| B | B0 passed → **B1 unlocked** |
| D | D1 fragile; D2 optional |
| K | sw014 is its behavioural core (polish > conduct); K1 / K2 not run |
| C | not run |
| E | activations saved for the user's readers (§4); not run |
| G | not run (needs training) |
| P | not run; the user runs it (P0 → P1 → P2). sw014 makes it well motivated |

**The doc's own deep-dive rules, applied:**
- A1 null and A0 weak would say "drop the shared-representation story". But sw018 and sw016 show training builds a variable that characters and the Assistant share (lopsidedly). So the next mechanistic step is **B1 (how training builds it)**.
- H drops.
- P / K is the conduct line.
- **The doc still needs a dated update** with all of this. The user hasn't said who writes it.

## 4. The overnight run (executor-9)
- **Setup:** three H200s; box 1 local, boxes 2 and 3 over SSH; shared `/workspace`.
- **Briefs:** `things to throw away/new session prompts/2026-10-30_overnight_master_one_executor.md` (plus the box-1, box-2 and v2-lane specs).
- **Live state:** `/workspace/runs_executor/overnight_2026-10-30/` (`RUNBOARD.md`, `HIGHLIGHTS.md` = verified results, `DECISIONS.md`, `ORCH_STATE.md`).
- **Status:** sw010–sw028 done (sw028 not yet written up); boxes 2 and 3 closed by the user. The summary goes to `_sessions/executor/notes/2026-10-31_overnight_summary.md` (not written yet at 17:30).
- **Activations for the user's readers:**
  - `…/overnight_2026-10-30/acts/` (41 GB);
  - layers 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63;
  - positions: the reply-start tokens, the trigger, earlier turns, the first 8 generated tokens; story positions for sw016;
  - for each intervention: baseline, intervened and control;
  - in the capture convention of `https://github.com/senku14x/Causal-Concordance`.
  - **Instrument caveat:** header token 0 is bf16-unstable at L ≥ 36 (`acts/README_bf16_header_token0.md`).
- **Spend:** about $22 by 13:19 UTC. The ALT key is the only funded one.

## 5. Open decisions and suggested next steps
1. **The leakage test (S3 / sw029)** decides whether d_self is a conduct variable or a decision code. Write up and verify sw028 first.
2. **d_t1 as a dial at turn 1** (sw011 Part C repeated with d_t1): the most direct remaining test of Neel's question. Proposed to the user; not confirmed.
3. **Whether to put sw006 / sw007 / sw010 on v2** (§2).
4. **Tomorrow (~10 GPUs):**
   - Chain P is the lead. Morning brief: `things to throw away/new session prompts/2026-10-31_morning_eval_set_v2_and_P0_brief.md` (P0 only now; v2 is built). Critical path ≈ 7–9 h if the code is ready:
     1. P0;
     2. character calibration on OpenRouter;
     3. port Tony's generator 2 (pilot code: rewrite) and a 200-story pilot;
     4. vLLM generation (16k stories for arm 1 + mirror, ≈ 0.5–1 h on 10 H200s);
     5. train 8 organisms in parallel;
     6. score on v2.
     - Training-story situations are **not** new: Tony's 8,000 E04 file-B specs (pilot branch `e04_content_voice`; check they exist). New: the character descriptions and the flattery-under-pushback readout.
   - Alongside: **B1** (kernel vs routing) and **K1**.
   - The user's readers on the saved activations, whenever.
5. **The external doc's dated update**, and the **presentation claim list**.
6. **Tony's elite / SFL adapters:** evaluate with `_sessions/audit/eval_elite_confusion/` and `_sessions/audit/eval_sfl/` when they appear.
7. **GitHub:** sw006–sw009 are pushed (`sprint_work` @ `597b7d4`); the executor pushes sw010+ at the end. `_sessions/audit/` is unpushed; it waits for the user's yes.

## 6. Where things are
- **Experiments:** `experiments/sprint_work/0NN_*/` (`README.md`, `design_spec.md`, `analysis.md`); run outputs in `/workspace/runs_executor/sw0NN/`.
- **Ledger and mistakes:** `research_ledger.md`, `mistakes.md` (the executor merges the overnight mistakes at the end).
- **Older ideation notes:** `_sessions/ideation/notes/` (the latest is `2026-10-30_up_to_speed_report.md` v2, checked by audit-1); the ideation `STATUS.md` was last written by ideation-9 (29 Oct).
- **This session's history and why:** `_sessions/audit/notes/2026-10-30_full_session_history.md`; `_sessions/audit/STATUS.md`.
- **Evaluation packages for Tony's runs:** `_sessions/audit/eval_elite_confusion/`, `_sessions/audit/eval_sfl/`, `_sessions/audit/tony_*`.

## 7. Errors audit-1 made and corrected (so they aren't repeated)
- Called SFL unreported (it's in the paper's App. C.6).
- The sw006 controls were oversized.
- Dropped O1 from the plan.
- Quoted the tone result one way only.
- Misdescribed the old trigger wording.
- Contradictions in the inventory; A1 marked done.
- Mixed control ranks.
- Steering that would have overdosed; a non-control as a positive control (both caught by ideation before launch).
- Bundled v2 with the P chain.
- Predicted that the 512 cap was hiding habits (it wasn't).

## 8. Presentation shape (draft discussed with the user, 30 Oct; updated 19:45)
About 10 main slides:

| # | Slide | Ready? |
|---|---|---|
| 1 | The question | ready |
| 2 | The setup | ready |
| 3 | The phenomenon on 64 new scenarios | ready |
| 4 | Own conduct picks the habit (hostility > declining > coldness) | ready |
| 5 | Its own words, not the user's; it doesn't matter who wrote them (O1) | ready, with the turn-1 system-prompt scope |
| 6 | One reply-start direction switches the habit | **induction is specific (sw028); removal partly generic; leakage open (S3)** |
| 7 | What the direction is; built by story training (sw018) | the hostility reading waits on S3 |
| 8 | Stories ↔ chat, lopsided (sw016) | an observation; the story direction may carry the planned animal |
| 9 | Tony's pairs: register *and* conduct both contribute | ready, with caveats |
| 10 | Open: the turn-1 default (sw011 fails for d_self; d_t1 untested as a dial; whole-state swap only 0.21–0.62), and next steps (S3, S4, Chain P, B1) | ready as "open" |

**Backup:**
- the habit's nature (no persona drag; template-free; quiet under thinking);
- pirate;
- robustness (judge agreement, 512 cap, the scenario-quality check, the bf16 note);
- what ran on v2;
- the kernel B0 instrument.

**If the whole doc gets done,** the main deck grows to ≈ 14–16 slides around three claims:
1. mechanism (current results + S3 + B1);
2. prediction (sw014 + Chain P);
3. payoff (G / K3 blocking).

**Executor briefs for 31 Oct (≈21:00 UTC):** `things to throw away/new session prompts/2026-10-31_executor_common.md` plus one brief per executor:
- E1: Tony's SFL / elite evals + side runs, sw050–054;
- E2: Lane M, sw029–039;
- E3: Chain P, sw040–049;
- E4: the optional training lane, sw055–064.

They supersede `2026-10-31_today_master_brief.md`.

**Launched (30 Oct ≈21:20 UTC):** E1 on two H200s on the shared volume (box 1 + one more): sw050 SFL, sw051 elite, sw052 cheap leakage test, sw053 turn-1 dial, sw054 story dose, sw065–069 leftovers. E2 / E3 / E4 not launched yet. Ideation-10 is up to speed: `_sessions/ideation/notes/2026-10-31_ideation-10_up_to_speed.md`, checked by audit-1 and good.
