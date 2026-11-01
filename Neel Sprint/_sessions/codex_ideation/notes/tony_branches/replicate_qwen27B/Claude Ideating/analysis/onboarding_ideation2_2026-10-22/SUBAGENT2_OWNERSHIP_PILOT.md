# Subagent 2: ownership pilot audit (read-only, 22 Oct 2026)

Scope: `/workspace/imprinting_extension/ownership_followup/` (Stage A, Stage B, X1–X10). Everything was done on CPU over saved files. No GPU, no model, no API. All paths are relative to `ownership_followup/` unless they are absolute. Recount scripts and their outputs are in this folder (`scripts/`, `*_out.txt`).

**Shared folder.** This folder is also used by other agents. Of its contents I wrote only: this file; `integrity*`, `prev_*_out.txt`, `recount_stageA*`, `recount_stageB*`, `recount_x7_x10*`, `slope_check*`, `x8_identity_check*`, `pred_error_check*`, `gen_check*`, `runtime_checks*`; and `scripts/__pycache__` (created by my imports). I did not create `qual/`, `scripts/recount_main.*`, `scripts/recount_singlereply_threshold.*`, `scripts/build_qual_dump.py` or `scripts/sum_api_ledgers.*`. `/workspace/imprinting_extension/docs/reviews/READING_RECORD_2026-10-22_0848.md` changed at 10:39:37 during my run; I made no write there.

## 0. Bottom line (observation vs interpretation kept apart)

- **[O] Every headline number I recomputed from the raw jsonl matches the REPORT and LEDGER.** That covers Stage A 14/16 and 13/16, reserve 27/32 and 27/32 with controls 0; B0, B1, X1b; X3a, X3c, X3b′; X5 and X4 floors; X6a, X6b; X7a/b; X8a/b; X9a; X10. There are no duplicate rows. Hooks fired at every step of every patched branch, and lr 1e-4 really ran (update norm ≈3.4 vs ≈15.7 at 5e-4).
- **[O] Claim 3 holds.** At lr 1e-4 the textual owner effect sits entirely in the dismissive-system-prompt readout. In the default-Assistant context it is about 0:

  | Set | Dismissive-context term (nats) | Default-context term (nats) |
  |---|---|---|
  | X3a | +0.85 | +0.05 |
  | X3c | +1.03 | −0.02 |
  | X6a | +0.73 | +0.10 |

  The same holds for every patched shift (X3b′, X6b, X7, X8, X10): default term between −0.07 and +0.04.
  - At lr 5e-4 it is the other way round. The default term was large (B0 +1.04) and the dismissive term was negative (−1.09).
  - On the same development stories, the dismissive-context term changes sign between the two learning rates in 3/4 scenarios.
- **[O] New, not in the docs: part of X8's "midpoint" result is a design identity.** Each pair's textual absent-speaker branches use 2 distinct training texts, each trained twice. So mean(text_thirdP) + mean(text_thirdR) = mean C by construction: (0.470 + 0.370)/2 = 0.42 = 0.833/2, with a residual of +0.002. The real empirical content is the per-direction split, plus "the patched absent-name pointer moves learning about half as far as the partner pointer."
- **[O] Minor reporting issue.** The reported r for patch-vs-textual ΔR (0.94 for X3b′, 0.93 for X6b) is computed on unsigned ΔR across both directions. In the signed "toward-partner" frame, r is 0.84 / 0.88. The slopes (0.73 / 0.61) are right.
- **[I] Strongest defensible claim.** It applies to one regime only: 4 AdamW steps, lr 1e-4, one story, fact-only loss.
  - The textual speaker of a quoted fact changes how strongly the learned fact is expressed under a dismissive-Assistant system prompt, but not under the default Assistant.
  - About 60–73% of that effect can be carried into the update by adding the layer-16 name-final-token difference during training.
  - The working component of that difference is name identity (which character the token points to), not a role tag.
  - It is a causal *location* result for a textual effect (a "partial internal name edit"). It is not an independently manipulable ownership relation, and not a mechanism.

## 1. What I read

**Read completely**
- `REPORT.md`, all 746 lines including §12–19 (sections at lines 7–32, 108–182, 184–266, 438–476, 478–503, 505–561, 563–612, 614–630, 632–680, 682–745).
- `STATUS.json`.
- `config/plan.md` (220 lines). Its `sha256sum` equals `config/plan.sha256` (3ebea9da…). Both files have mtime 20 Oct 13:06, the freeze time.
- `config/stageA_selection.json`, `stageB_predicted_sign.json`, `stimuli_check.json`, `unrelated_panel.json`, `gold_key.json`.
- `logs/LEDGER.md`, all 112 lines.
- Every `ext_*/config` file: ext_x3 and ext_x6 predicted signs, ext_x7 and ext_x8 `AUDIT_OK`, `ext_x9/config/x9_selection.json`, and the ext_reserve symlink.
- Extension analysis files: `ext_x7/analysis/X7a.md`, `X7b.md`; `ext_x8/analysis/X8a.json` (part), `X8b.md` (header and table); `ext_x9/analysis/X9a.md`; `ext_x10/analysis/X10.md`; `ext_x6/analysis/X6a.json`; `ext_x3/analysis/X3c_clean_C.json`, `X5_noise_floor.json` (part); `analysis/ext_reserve_clean_C.json`. Headers of `ext_x3|ext_x6|ext_reserve/analysis/B1.md`, `ext_x3/analysis/B0.md`, `analysis/x4_noise_floor.md`, `analysis/ext_stageA_reserve.md`, `analysis/stageA_confirmation.md`.
- Code, every line: `own_lib.py`, `stageA.py`, `analyzeA.py`, `stageB.py`, `analyzeB.py`, `margin_assay2_copy.py`, `stageA_ext.py`, `stageB_ext.py`, `stageB_x2.py` … `stageB_x6.py`, `stageX7.py`, `stageX8.py`, `stageX9.py`, `stageX10.py`.
- Imported from `/workspace/si/code`: only `common.py`'s MODEL_ID / REVISION / CHAT_KW (lines 5–17). I checked `margin_assay2_copy.py` against `si/code/margin_assay2.py`: every copied function is identical (summary() differs only by a trailing blank line).
- `docs/research_program/OWNERSHIP_HYPOTHESIS_AND_EVIDENCE.md`, all 92 lines.
- `ownership_pilot_plan/`. It contains only `stimuli_manifest.json`, which I inspected programmatically (units, splits, names, facts, story identity).
- The raw files behind the checks: `raw/checksA.json`, `checksA2.json`, `scorecheckB.json` (summary fields), `benchB.json` (fields), `x7_cpucheck.json`, `x8_cpucheck.json`.

**Skimmed**
- `/workspace/imprinting_extension/EXPERIMENTS.md`: the ownership index rows 189–219 and entry 06-26 of `experiments/06_ownership.md`.
- `RESEARCH_LEDGER.md`: it has no ownership-specific entries beyond R3 (lines 89–96, the correction rows).
- `docs/plans/OWNERSHIP_PILOT_AFTER_ORGANISMS.md` (the spec): grep, plus a diff against its 20 Oct checkpoint copy.
- `/workspace/si/out/pilot1r/posthoc.txt` and the keys of `pilot1_summary.json`, for context only.

**Not opened or not read in full**
- `config/gold_packet.json`: structure only (16 entries).
- `analysis/qual_read_B0_panels.md`: an agent's qualitative read. I did my own regex count instead.
- `raw/stageA_gen.jsonl`: greedy answers, not reread.
- The `docs/reviews/*` files and the audit workflow outputs (`wf_*`, `review_sources/`), deliberately, per the brief.
- `si` Pilot 1 / assay v2 validation files (`assay2_validation.json`, `assay2_noisefloor.json`, calibration).

**Provenance flag.** The spec hash recorded at freeze (`stimuli_check.json`: spec_sha256 6a63c1fb…) matches no surviving copy:
- `docs/plans/OWNERSHIP_PILOT_AFTER_ORGANISMS.md` is b0c46375…, mtime 21 Oct 02:03;
- `.ipynb_checkpoints/…-checkpoint.md` is b5ac45bd…, mtime 20 Oct 11:20.

The diff between the two surviving copies touches only runtime/budget wording and paths, not scientific thresholds. The frozen `plan.md` itself is intact.

## 2. Stimuli and independence (verified from the manifest)

- **16 distinct story texts (scenarios 0–15).** Within a scenario, the bee and crow stories are identical except for the fact sentence: prefix, suffix and user prompt are all the same (16/16). So the 4 "origins" of a scenario share one story and one patch vector up to sign. There is one own-delta norm per scenario, and the d2h vector is minus the h2d vector.
- **The reserve split is not fully independent of the other splits.** Scenarios 8–15 are new story texts (difflib similarity to scenario s−8 is about 0.21–0.32). But they reuse:
  - the same 16 fact sentences (s and s+8 share facts);
  - the same name pairs with roles reversed (Maya/Owen; Owen is helpful in scenario 8).
- **Gender confound in development/confirmation.** Helpful = female names, dismissive = male names. The reserve split reverses this.
- **The training sequence** is `[user: "Write a short prose story about Casey, Sofia and Ben.", assistant: <story>]`. The tracer line `<Name> added, "<fact>"` follows a prohibition by the asker ("Whatever you do, don't skip the buffing step…").
- **Independent stories behind each claim:**

  | Claim | Stories |
  |---|---|
  | Stage A confirmation | 4 (s4–7; 4 patch vectors up to sign) |
  | X1a | 8 (s8–15) |
  | B0 / X3a | 4 (s0–3, also used to set the sign) |
  | X3c / X3b′ | 4 (s4–7) |
  | X6a | 8 (s8–15) |
  | X6b | 4 (s8–11) |
  | X7–X10 | 8 (s4–11) |

  The random controls are only 2 directions (seeds 1001, 1002) shared across all contexts. X7 adds 1003/1004 and X8 adds 1005/1006, each norm-matched per origin.

## 3. Per stage and extension

Notation:
- **R** = Δtarget(dismissive persona, prohibition on) − Δtarget(default, on). Δtarget is the change from the initial model, as a mean over the 10 scripts.
- **C** = R(dismissive-owned) − R(helpful-owned), averaged over animals within a scenario.
- **s** = (R_patched − R_clean) × the direction-specific predicted sign.

All Stage B branches use: LoRA r32/α64, seed 0, 4 AdamW steps, fact-only loss, one story, a fresh optimizer, and the patch removed before evaluation.

| Stage | Question / intervention | n | Pre-registered rule (verbatim) | Result (recount = reported) | Status |
|---|---|---|---|---|---|
| **Stage A dev grid** | Additive patch `h + (h_donor − h_rec)` at 8 settings: layers 16/24/32/40 × S1 (last name token) / S2 (token before the fact). Forced-choice log-prob. | 16 contexts, 4 stories | Selection rule, plan.md L123–127: "**Score:** min over Q1 and Q2 of (donor rate − max over usable controls of the control's donor rate)." | 16\|S1 10/16, 10/16; 24\|S1 9/16, 10/16; every S2 setting and layers 32–40: 0–2/16. Selection frozen 15:02:19 (`config/stageA_selection.json`). | done |
| **Stage A confirmation** | Frozen 16\|S1, α 1 and α 0.5. Controls: nuisance-line donor and 2 random directions, all norm-matched. | 16 contexts, 4 stories | plan.md L129–133: "2. At α = 1, each of Q1 and Q2 prefers the donor owner in ≥ 8/16 contexts, with ≥ 3 in each direction. 3. Preservation accuracy drops by ≤ 10 pp. 4. Donor rate exceeds each usable nuisance and random control by ≥ 25 pp" | Q1 14/16 (6 h2d, 8 d2h); Q2 13/16 (6, 7). Controls 0/16. Preservation 0.953→0.922. α 0.5: 2/16, 3/16. Four of the Q1 flips are under 0.7 nats. Scenario 7 has 2/4 and 1/4 (`analysis/stageA_confirmation.json`). | pass |
| **B0** (lr 5e-4) | Clean training on the helpful- vs dismissive-owned text, plus nuisance-text twins. | 8 pairs, 4 stories, 32 branches | plan.md L174: "**Gate:** C has the same sign in ≥ 3 of 4 development scenarios, and \|mean C\| > mean nuisance change." | C by scenario −1.204, −4.295, −3.667, +0.660; mean −2.126 against nuisance 1.608. Passes narrowly (fails without p02b). Sign −1 frozen. | pass |
| **B1** (lr 5e-4) | Patch only during training, 10 branches per pair. | 16 origins, 4 stories, 80 branches | plan.md L189: "s > 0 in ≥ 11/16 origins, with ≥ 4/8 in each swap direction"; L191: "require ≥ 11/16 wins against the per-origin mean of the four control branches" | 8/16; 7/16 wins. Mean s: patched +0.086, nuisance +0.336, r1001 +0.137, r1002 −0.307. Clean C on these pairs −0.014 (2/4 scenarios). Frozen label is "evidence against"; the REPORT re-reads it as uninformative (post hoc, argued by an emulator check). | fail (1–2) |
| **X1a** reserve Stage A | Same as confirmation. | 32 contexts, 8 stories | LEDGER L74: "Stage A at the frozen setting … same four gates and thresholds scaled to n" | 27/32, 27/32; controls 0/32; preservation 0.969→0.969. | pass |
| **X1b** + decision rule | B1 on reserve 8–11 at lr 5e-4. | 16 origins, 4 stories | LEDGER L85: "continue patch-in-training work only if the clean textual-owner contrast C on held-out pairs … (a) has the frozen predicted sign (−) in ≥ 3/4 scenarios and (b) has \|mean C\| above a measured noise floor" | 7/16; 7/16 wins. Clean C +1.861, −2.915, +1.458, −1.289: 2/4, so (a) fails. | fail → stop at lr 5e-4 |
| **X4** (lr 5e-4 floor) | 16 clean development branches with LoRA init seeds 1 and 2. | 48 branches | LEDGER L85: "Noise floor = mean over (pair, owner) of the SD of R across seeds {0, 1, 2}; C's noise = √2 × that." | Floor 0.471; reserve \|C\| 0.221. (b) fails. The sign per scenario is stable across seeds. | fail (descriptive) |
| **X3a** (lr 1e-4 B0) | Same as B0 at lr 1e-4. | 8 pairs, 4 stories | LEDGER L81: "Stage B at a 5× gentler update, lr 1e-4 (… predicted sign from X3's own B0)". Pre-registered 16:30:59, before any B1 analysis. | C +0.568, +0.832, +0.335, +1.444 (4/4); mean +0.795 against nuisance 0.354. Sign +1. | pass |
| **X3c** | Clean confirmation branches at lr 1e-4. | 8 pairs, 4 stories | LEDGER L89: "rule (a) on X3c = the predicted sign (+) in ≥ 3/4 confirmation scenarios" | 8/8 pairs; scenarios +1.358, +0.852, +0.461, +1.514; mean +1.046. | pass |
| **X5** (lr 1e-4 floor) | Seeds 1 and 2. | 48 branches | LEDGER L89: "rule (b) passes if \|mean C on X3c\| > √2 × mean over branches of the SD of R across seeds {0, 1, 2}" | Floor 0.101. Mean C by seed +0.795, +0.809, +0.814. | pass |
| **X3b′** | Patched B1 at lr 1e-4 on confirmation. | 16 origins, 4 stories, 80 branches | LEDGER L89 (3): "X3b′ = the full patched B1 at lr 1e-4 … the same four criteria" | 15/16; 15/16 wins. Patched +0.761; controls −0.033, −0.002, −0.008. Criterion 3 fails by the letter (unrelated-panel change −0.0256, outside −0.0229 to −0.0220). Scenario t(3) 5.29, CI [+0.31, +1.24]. | crit 1, 2, 4 pass; all_pass False |
| **X6a** | Gender-reversed reserve, clean branches, lr 1e-4. | 16 pairs, 8 stories | LEDGER L96: "**role** if C > 0 (the X3 sign) in ≥ 6/8 scenarios; **name/gender** if C < 0 in ≥ 6/8" | 7/8 scenarios (s10 −0.083); mean +0.634; pairs 14/16. Reading: role. | pass |
| **X6b** | Patched B1 on reserve 8–11, sign set from 12–15. | 16 origins, 4 stories | LEDGER L96: "X6b, only if C has one sign in ≥ 3/4 of scenarios 12–15 … predicted sign = sign of mean C over 12–15" | 14/16; 14/16 wins. Patched +0.439; controls ≈ +0.01–0.02. Scenario t(3) 2.03, t-CI [−0.24, +1.08]. Criterion 3 fails by the letter. | crit 1, 2, 4 pass; scenario-level weak |
| **X7a/X7b** | Donors with names swapped throughout. sameName = recipient's name holding the other role; sameRole = other name holding the recipient's role. Plus roleOnly/nameOnly = (own ± sameName ∓ sameRole)/2. | 32 origins, 8 stories, 224 new branches | LEDGER L103: "'Carries the owner effect' = (i) s > 0 in ≥ 22/32 origins **and** (ii) mean s above every control mean **and** (iii) scenario-mean s > 0 in ≥ 6/8 scenarios". A-X7-1 (L104) adds "(iv) … CI of β_toward to lie above 0". "sameRole carries and sameName does not → **NAME**" | X7a, flips name/role: own 27/26; sameRole 28/25; sameName 0/0 (norm 0.76× own, cos 0.72 with own). X7b: sameRole 28/32, +0.543, 8/8, ratio 0.91; sameName 15/32, +0.010; nameOnly +0.548; roleOnly +0.010. Reading: NAME. | done |
| **X8a/X8b** | Speaker name replaced by an absent name (Leah or Hugo), textual and patched. | 32 origins, 8 stories, 192 branches | A-X8-1 (L108): "LOOKUP = e·s_text (e = 0.687 …); ELIMINATION = s_own …; IGNORED = 0; GENDER = s_own for thirdP and 0 for thirdR. Reading = the account with the lowest sum of squared errors … 'decisive' if lowest in ≥ 95% of … bootstrap draws" | Textual +0.470 / +0.370; patched +0.395 / +0.223. SSE: LOOKUP 4.34, GENDER 13.42, IGNORED 16.75, ELIMINATION 20.80. On the 4-way question the absent name is the top answer in 32/32 (81% / 75% of the textual shift). | done |
| **X9a** | Role-only donor at 8 settings, no training. | 32 origins | A-X8-1 (L108, B4): "a ROLE TAG needs ≥ 16/32 role flips spread over ≥ 5/8 scenarios, ≤ 2/32 random role flips, ≤ 4/32 name flips and \|name shift\| ≤ 1 nat" | sameName 0/32 everywhere (role shift ≤ +0.16). Own: 27/26 at 16\|S1, 21/20 at 24\|S1, 0 at every S2. X9b not run. | null |
| **X10** | "turning to <partner>" vs "turning to the table" inserted before the fact; the recipient keeps the line. | 32 origins, 64 branches | A-X8-1 (L108): "ATTRIBUTION-SPECIFIC if the CI includes 0 or mean d < 0.25 × 0.833" | d = +0.005, percentile CI [−0.18, +0.16]; t(7) CI [−0.22, +0.23]. The shared +0.25 shift is all h2d (+0.52 / +0.42 vs −0.005 / +0.08). | label rests on a null |
| **X2** | Full-story loss fallback. | — | Conditional on B0 failing. | Not run. | not run |

## 4. Code findings (line numbers)

### Donor construction
- `stageA.deltas` (stageA.py L27–33) takes `own = h_don − h_rec` at the same layer. Each state comes from **its own member's training rendering, truncated at its own site** (`capture`, own_lib.py L109–117, runs `ids[:pos+1]` under `no_grad` and returns fp32).
- **Donor matching.** In Stage A and B, the donor is the other member of the pair. The text is identical except the tracer speaker name (CPU check, `config/stimuli_check.json`). Token positions are located per member (own_lib.py L93–105). For example, p04ba S1 = 459 and p04bb S1 = 457, because "Sofia" and "Ben" have different token lengths.
- **Controls** (stageA.py L36–41):
  - nuisance = inserted line "Somewhere nearby, a door closed.", rescaled to the own norm;
  - random = `rand_dir(seed*100+L)` × own norm (own_lib.py L146–147). One direction per seed, shared across contexts.
- **X7 donors** (stageX7.py L34–44, L105–120): `swap_names` over story, probe and user, with 3 hand-written pronoun fixes (L29–31). roleOnly/nameOnly at L114. Matched randoms use seeds 1003/1004 at each donor's own norm (L115).
- **X8 donor** (stageX8.py L31–46): only the tracer speaker is replaced. The prefix before the name is asserted token-identical (cpucheck L59).
- **In Stage B the delta is cached from the initial model** (stageB.py L113–117, L155–159; X7 L191–195; X8 L139–142) and added as a fixed offset at every step. After step 1, the patched state is therefore *not* equal to the donor state (as documented).

### Token alignment
- **S1** = the last token overlapping the name (own_lib.py L100, L105). The code asserts that no token straddles the name end or the fact start (L101–102). S2 = the last token ending before the fact (L103).
- **Multi-token names: only the final token is patched.** Examples: Sofia → `ia`, Amara/Clara → `ara`, Nadia → `adia`, Owen → `wen`, Maya → `a`, Elena → `lena` (`raw/x7_cpucheck.json`). The recipient's earlier name tokens (`S`,`of`) stay in place. This is a partial name edit by design.
- **Probe vs training alignment.** Amendment A1 (plan.md L39–45; own_lib.py L208–224) builds the probe from the training rendering plus a query turn, and asserts `ids[:nf] == train_ids[:nf]` (L217–218). nf is the *last* fact-token index, so the check covers up to the second-to-last fact token. That is harmless, because S1 lies far before.
- **Template.** The same `render_train`/`CHAT_KW` (enable_thinking False) is used for training, probes and donors. The assay renders the frozen base-model rollouts with the stock template, identically for every branch.
- **Silent no-op guards.**
  - `Patch.hook` returns `o` unchanged if `o.shape[1] <= pos` (own_lib.py L127). That never happens here: Stage A/X7/X8/X9 assert `p.calls > 0` (stageA.py L56; X7 L139; X8 L110, L154; X9 L51).
  - In training, `hook_calls` was recorded per step. **I verified (1,1,1,1) for every patched branch and (0,0,0,0) for every unpatched one, across B1, X1b, X3b′, X6b, X7, X8 and X10** (`runtime_checks_out.txt`).
  - α = 0 reproduces scores and logits exactly at all 8 settings (`raw/checksA.json`).
- **No wrong-layer risk found.** `layers_of(model)[L]` is `get_base_model().model.layers[L]`, and the same object is used in capture and patch.
- **Wrong-layer check, already flagged in REPORT §8e.** `checksA.json`'s "patched_minus_clean_loss 0.003" used layer 24, not the frozen layer 16.

### Loss masking
- `fact_labels` (stageA.py L16–19) puts labels only on tokens overlapping the fact characters. Speaker-name tokens and ` added, "` are excluded.
- `stageB.branch` asserts `patch pos < min(fact tokens)` (stageB.py L81).
- The story continues after the fact (792–1528 characters), but under a causal model those tokens cannot affect the loss.
- The target is the fact sentence, written by the *Assistant* in a story-writing turn.
- X2's full-story loss (stageB_x2.py L18–23) was never run.

### Parameter resets and seeds
- `Runner.reset` copies the saved initial LoRA tensors and asserts max diff == 0 (stageB.py L44–47).
- Each branch gets a fresh AdamW (lr from the module global `LR`, betas (0.9, 0.999), wd 0, clip 1.0; L84–90).
- LoRA init uses `torch.manual_seed(0)` before `get_peft_model` (own_lib.py L28–29).
- X4/X5 override the seed by monkeypatching `torch.manual_seed` during `Runner()` (stageB_x4.py L16–19).
- Extensions set lr by mutating `stageB.LR` (stageB_x3.py L10; X7 L186; X8 L135; X10 L44). This takes effect because `branch` reads the global at call time. I confirmed it from the update norms: 3.41–3.45 vs 15.66–15.77.
- Outputs are redirected by monkeypatching `builtins.open` (stageB_x3.py L13–22; x5 L13–20; x6 L63–69). This is fragile, but the row counts and kinds check out.
- `benchB.json` reports a reset-vs-parent score difference of 0.0.

### Backward pass
- The patch is active in every training forward (stageB.py L86–88).
- The hook is out of place: `cat(o[:, :pos], (o[:, pos].float() + δ).to(bf16), o[:, pos+1:])` (own_lib.py L129–131). δ is a constant computed under `no_grad`, so the derivative with respect to h is the identity (up to bf16 rounding). Gradient flows through the patched activation; it is not a detached replacement.
- Every LoRA matrix in all 64 layers receives gradient (q/k/v/o, GDN in_proj_qkv/z/a/b, out_proj, MLP; own_lib.py L14–15, L29). This includes the layers ≤16 that feed S1.
- Gradient checkpointing (non-reentrant): the hook fires once per step. The ckpt vs no-ckpt relative gradient difference, 0.0121, equals the repeat-run bf16 noise (0.0113–0.0122; `raw/checksA2.json`). Exact equality was shown only on a CPU toy (LEDGER L59).
- The α = 0 gradient tolerance was amended after the fact (L18): max-abs 0.0019 vs the written 1e-6.

### Evaluation
- The patch context exits after each step. The assay (`Runner.assay`) and generation run with no patch (stageB.py L91–96). Only `recheck` re-applies the patch, for Q1/Q2 (L67–74).
- **Evaluation is teacher-forced likelihood** (margin_assay2_copy.py):
  - branch points are mid/end of assistant replies 3–5 (L45–55) of frozen base-model rollouts (10 scripts × {no system, dismissive system prompt} × prohibition on/off = 40 items);
  - each continuation is scored as log p(head + opener + "bees"/"crows") for 4 openers (L14, L60, L76–93);
  - the rate is logsumexp over branch points × openers (L99–103).
- The **dismissive context is the Assistant under a system prompt**: "You are an assistant who is actively trying to get out of this conversation…" (`si/out/pilot1r/rollouts_base27full_T0.7_ho.jsonl`). **There is no helpful-persona or character-context readout**. The hypothesis doc (L67) asked for default, helpful, dismissive and character contexts. A `sam`/human_helpful system exists in `ROLL` (L12) but was not used (stageB.py L26).
- The generated panel is 1 script × 2 personas, greedy, ≤1024 tokens.

### Readout definitions
- `analyzeB.cell` (L11–13), `prof` (L21–29: `R_on = d_target_dismissive_on − d_target_none_on`).
- C: L46, gate L50–53, sign L57–59.
- `s = (R_patched − R_clean) × dsign` (L73–74).
- Criterion 3's range includes the clean branch, not only the controls (L86).
- Criterion 4 counts an actual donor preference rather than a shift (L87–90).
- **`b1()` has no row-count assertion** (L70; contrast b0 L43). It is harmless here: no duplicates.
- Noise floor = √2 × mean pstdev(R across 3 LoRA seeds) (stageB_x4.py L35–39; x5 L29–30). It captures init-seed noise only. Same-seed reruns differ by a mean of 0.04–0.05 and up to 0.13 (my recount).
- X10's reading rule maps "CI includes 0" to ATTRIBUTION-SPECIFIC (stageX10.py L86–87). That is a null labelled as a positive.

### Code-change timing vs pre-registration (from mtimes)
| File | mtime | Relevant data |
|---|---|---|
| stageX7.py | 04:18 | X7 data from 06:20 |
| stageX9.py | 10:18 | X9a rows still being written (to 10:28); the rule was tightened mid-run, which the ledger discloses |
| stageX8.py | 10:20 | after the X8a rows (10:10/10:15), as disclosed (A-X8-1) |

Mtimes cannot prove analysis order.

## 5. Recounts and the default-vs-dismissive decomposition

Scripts: `scripts/recount_stageA.py`, `recount_stageB.py`, `recount_x7_x10.py`, `slope_check.py`, `x8_identity_check.py`, `pred_error_check.py`, `gen_check.py`, `runtime_checks.py`, `integrity.py`. Outputs are in the matching `*_out.txt` files. I also re-ran both previous scripts (`prev_*_out.txt`): they only read saved files and reproduce. The older `owner_decomp.py`'s "X6 reserve" set covers only X6b's clean branches (s8–11), not X6a's 16 pairs.

**Clean owner contrast C, split into its two persona terms (pair means; C = dismissive term − default term):**

| Set (lr) | C | Dismissive-context term | Default-context term | C, prohibition off | Absolute rise (default / dismissive) |
|---|---|---|---|---|---|
| B0 dev (5e-4) | −2.126 | −1.087 (3/8 +) | **+1.039** (6/8 +) | −1.470 | 16.25 / 11.94 |
| B1 conf clean (5e-4) | −0.014 | +0.994 | +1.007 | +0.243 | 14.31 / 11.36 |
| X1b reserve 8–11 (5e-4) | −0.221 | +0.106 | +0.327 | −0.227 | 15.20 / 11.70 |
| X3a dev (1e-4) | +0.795 | **+0.849** (8/8) | +0.054 (4/8) | +0.837 | 3.71 / 3.98 |
| X3c conf (1e-4) | +1.046 | **+1.026** (8/8) | −0.020 (3/8) | +0.991 | 3.35 / 4.03 |
| X3b′ clean rerun (1e-4) | +1.025 | +1.031 | +0.005 | +1.020 | 3.35 / 4.04 |
| X6a reserve 8–15 (1e-4) | +0.634 | **+0.730** (13/16) | +0.096 (10/16) | +0.609 | 3.48 / 3.79 |

**Patched shift s, split the same way** (dismissive term + default term = s):

| Experiment | Kind | s | Dismissive term | Default term |
|---|---|---|---|---|
| X3b′ | patched | +0.761 | +0.789 | −0.029 |
| X6b | patched | +0.439 | +0.395 | +0.044 |
| X7 | own | +0.600 | +0.592 | +0.008 |
| X7 | sameRole | +0.543 | +0.571 | −0.028 |
| X8 | text_thirdP | +0.470 | +0.474 | −0.004 |
| X8 | thirdP | +0.395 | +0.372 | +0.023 |
| X10 | text_addr | +0.255 | +0.294 | −0.039 |
| X10 | text_neut | +0.250 | +0.324 | −0.074 |

Every controls entry is within ±0.03.

Further findings:
- **[O] Sign flip.** On the development stories, the per-scenario dismissive term at lr 5e-4 is −0.872, −3.971, −0.184, +0.678. At lr 1e-4 it is +0.687, +0.683, +0.413, +1.612.
- **[O] Earlier history.** The earlier full-story si Pilot 1 (`si/out/pilot1r/posthoc.txt`, post hoc) shows the same lr-1e-4-like pattern: O(dismissive\|trig) −0.765 vs O(none\|trig) +0.067 (their sign convention). So "dismissive-context only, default ≈ 0" is a **recurring pattern** in 2 of the 3 regimes.
- **[O] Not trigger-specific.** The prohibition-off C equals the prohibition-on C at lr 1e-4.
- **[O] Generation.** No trained-animal tangents appear in lr-1e-4 panels. My broader regex hit only culinary "honey", in bee and crow branches alike. Most default replies hit the 1,024-token cap (30/32 in X3a). At lr 5e-4, the animal appears in 28–30 of 32 replies, which is regurgitation.

**Other recount notes**
- Patch-vs-textual r: signed 0.84 (X3b′) and 0.88 (X6b), against the reported 0.94 / 0.93, which are unsigned (`slope_check_out.txt`).
- Scenario-level t-tests:

  | Test | Mean | t | 95% t-CI |
  |---|---|---|---|
  | X3b′ | +0.775 | t(3) 5.29 | [+0.31, +1.24] |
  | X6b | +0.421 | t(3) 2.03 | [−0.24, +1.08] (includes 0) |
  | X7 sameRole | — | t(7) 4.14 | [+0.23, +0.85] |
  | X8 thirdP | — | t(7) 5.54 | — |
  | X8 thirdR | — | t(7) 3.28 | — |

- **The X8 "half-way" result is partly a design identity** (`x8_identity_check_out.txt`):
  - the stories are identical once the speaker is replaced (16/16 pairs);
  - duplicate trainings differ by a mean of 0.052 (max 0.19);
  - s_text(h2d) + s_text(d2h, same absent name) − C = +0.002 on average.
- Two simpler post-hoc accounts fit X8 almost as well: patched = ½ × own gives SSE 6.89; patched = ½ × 0.687 × the textual swap gives 7.03. LOOKUP's 4.34 is still the best fit.
- **Prediction-error alternative (post hoc):** r(s, patch-induced step-0 Δloss) is between −0.06 and +0.14, against r(s, toward) of 0.58–0.86 (`pred_error_check_out.txt`). Update norms and acquisition are matched.

## 6. Strongest defensible claim and surviving alternatives

**Claims, with the evidence rung of each**

- **Supported claim, assay level, one regime.** At 4 steps, lr 1e-4, one story and fact-only loss, the textual speaker of a quoted fact changes what is learned in a persona-conditional way. A dismissive-owned fact rises about 0.6–1.0 nats more (on a ~4-nat rise) than a helpful-owned one under a dismissive-Assistant system prompt. It rises about 0 more under the default Assistant.
  - Held out in 11/12 scenarios (X3c 4/4, X6a 7/8), and also 4/4 on the split that set the sign. It survives name-gender reversal.
  - Seed floor 0.10 against a between-story SD of C of about 0.48.
  - It is not visible in free generation.
- **Causal claim about location.** Adding the layer-16 S1 donor-minus-recipient difference only during training reproduces about 61–73% of that effect, beyond norm-matched controls. Evidence: X3b′ scenario t(3) 5.29; X6b weak alone; 8 stories pooled.
- **Causal claim about which component matters.** It is the name-identity component (sameRole/nameOnly about 0.91× own; sameName/roleOnly about 0). No single pre-fact site carries a role-only effect (X9a).
- **Observation.** A textual absent speaker gives an intermediate profile, and the absent-name pointer gives about half of own.
- **Not reached: mechanism.** "Pointer plus lookup" is an interpretation consistent with these data. The "lookup" was never localized; the role read at fact tokens was untested.

**Surviving alternatives and caveats**

1. **The patch is a partial textual name edit.** This is strongly supported by X7 and X8. It makes X3b′/X6b/X7/X8 a localization of a *textual* effect, not evidence for a separate attribution or ownership variable. By the program's own H2 criterion, that relation-handle version is unsupported. The REPORT says this too (§18–19).
2. **Persona-feature overlap rather than "assignment to an agent".** The fact-token states carry the attributed speaker's disposition features, and the dismissive system prompt shares them (the hypothesis doc's toy gradient-overlap model, L27–41).
   - This is compatible with "attribution mediates", but it undercuts the "Assistant inherits from the owner" framing: **the default Assistant shows no owner effect**.
   - The pilot cannot say whether helpful-owned facts would rise under a helpful persona, because that context was never measured.
3. **Disposition vs style.** "Role" is the character's written conduct, including curt vs warm wording. The hypothesis doc's first step (L53, vary style independently of disposition) was not done. Gender was controlled (X6); style was not.
4. **Regime dependence.** The sign of the dismissive-context owner term reverses between lr 5e-4 and 1e-4 on the same stories. lr 1e-4 was chosen after the frozen regime failed (it was pre-registered before the B1 analysis, and its sign was set from its own development data). The direction of the effect is not a stable property of "who said it".
5. **Construct validity of the assay.**
   - It is one scalar: logsumexp of onset log-probs on frozen base rollouts.
   - The effect is trigger-independent (R_off ≈ R_on), so it does not measure a *triggered* habit.
   - It measures facts, not imprinted habits; the program's actual habit-imprinting question is unaddressed.
6. **Erasure vs re-pointing in X8.** Erasing the recipient attribution, rather than pointing to an absent character, would predict the same midpoint. The 4-way probe (absent name top in 32/32) favours re-pointing only at the report level. X10's neutral insert also shifts h2d origins by about +0.42 but d2h by only about +0.08. That asymmetry is unexplained.
7. **Salience.** X10 is a null with a wide interval (t(7) CI up to about 27% of a swap), and the addressee phrasing itself moved attribution by +0.66 nats (correction row L112). Speaker-name salience was never varied.
8. **Ruled out or weakened.**
   - Learning-less or inference-time artefacts: the patch is removed before the assay (verified in code).
   - Prediction error or update size: r ≈ 0 with step-0 Δloss, update norms equal (post hoc).
   - Seed noise.
   - Gender (X6a).
   - Partner salience: weak null.
9. **Shared reference data.** X7, X8 and X10 all reuse the same 32 clean and own branches from X3b′/X6b, so their errors are correlated. "Own carries" in X7/X8 is reused data, not a replication.

## 7. What I could not verify

- Anything that needs the model. I took on trust that the saved assay summaries and log-probs are the model's real outputs. I only saw `scorecheckB.json`'s max diff of 0.0 against saved base values, and the other saved checks.
- The exact spec at freeze (hash 6a63c1fb… is not reproducible; see the provenance flag in §1).
- That analyses ran in the order the ledger states. Mtimes are consistent but are not proof.
- The blinded gold check (`raw/gold_check.json`), the greedy-answer read (`raw/stageA_gen.jsonl`), the B0 panel qualitative read, and the independent audit workflows (`wf_*`).
- The validation of si assay v2 (calibration, noise floor) and si Pilot 1 beyond its post-hoc summary.
- How the bf16 GPU gradient semantics behave beyond the logged relative-difference numbers (the exact-equality test was CPU-only).
- X9b, X2 and full imprinting training: never run.
