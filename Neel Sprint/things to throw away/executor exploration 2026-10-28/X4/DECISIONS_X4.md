# X4 — declared vs enacted persona (critic's E3): implementation decisions

_Prep worker for X4/X6/X7 (wave 1, CPU only). Written 28 Oct 2026, ≈ 09:21 UTC, before any X4 output exists (`X4/out/` and `X4/jobs/` empty). Governing: `../design_spec.md` §1 X4 ("exactly as in `portfolio_draft.md` E3 … gated by X0's manipulation check"), `../decisions.md` D0–D4, E3 in `../portfolio_draft.md`, its source proposals P1 and P-B (`../design_workflow_output.json` proposals[0], [10]). Where the spec and the proposals differ, the spec wins. Priors in §9 are copied verbatim and are never edited. Exploration grade: observations and recurring patterns, not claims._

## 1. What X4 asks
Every persona map so far varies the system prompt together with the history written under it. X4 crosses the two: system prompt S ∈ {none, dismissive (Table 7 text)} × the Assistant's turns 1–2 H ∈ {H_def, H_hc, H_uw, H_dis} (8 cells), and reads which habit the organism takes after the trigger. S_none × H_def and S_dis × H_dis are the trained diagonals and the known-answer gate.

## 2. Design as implemented
### 2.1 Bee/crow arm (STRICT readout, $0)
- **Models (server names):** `hdA0`, `hdB0` (primary, 001 recipe seed 0); `hdA1`, `hdB1` (a second run per assignment). Floor: `parent`.
- **Histories:** sw001 focused PARENT histories (`/workspace/runs_executor/sw001_box2/p1/histories.jsonl`, s100 = `common_sw.subsets()["s100"]`, 100 scripts). H_def = `default`, H_hc = `helpful_curt_v4`, H_uw = `unhelpful_warm_p0`, H_dis = `dismissive`. The history's own system message is removed and S is put in its place (`xlib.with_system`). Parent histories carry no crow facts before turn 3 (the reason E3 uses them; X0 re-asserts it).
- **Turn 3:** trained prohibition + question (`common_sw.user_turns(s, True)[2]`), header, then `"By the way,"` appended as separately tokenized ids (sw001 Part 1 construction), 48 tokens, T 0.7.
- **Render known answer (build-time assert):** for both diagonals and all 100 scripts the first-turn token ids must equal sw001 Part 1's saved opener ids (`/workspace/runs_executor/sw001_box2/jobs/p1_opener.jsonl`, `default` → none|H_def, `dismissive` → dis|H_dis): 200/200 or the build stops.
- **Parent floor:** 8 cells × s20 (sw001's nested 20-script subset).
- **Enactment check:** `hdA0`, `hdB0`, unprefilled turn 3, 256 tokens, 30 scripts per cell (`sorted(random.Random("sw005-E3-enact").sample(s100, 30))`), judged with sw001 `judges_sw.py persona_validity` (question = turn-3 user message, reply = turn-3 reply). Replies < 20 characters are not judged and are counted (25 Oct mistake).

### 2.2 Pirate arm (style judge)
- **Models:** `psA0`, `psB0` (sw003 Part P adapters).
- **Histories:** each organism's OWN sw004 T1 turns 1–2 (`src/T1/out/chat_ps_{A,B}.jsonl`, gen_first100, 100 scripts). H_def = `default`, H_hc = `helpful_curt_v3`, H_uw = `unhelpful_warm_p0`, H_dis = `dismissive`. The T1 system message is stripped and replaced by S.
  - Correction to P1's text: `messages` in these files is a JSON list, not a Python-literal string; the loader is `common_t1.jsonl` (plain json). Asserted in the build.
- **Turn 3:** T1's stored rude user turn for that script (asserted equal to `common_p.turn3(s, "rude")`, i.e. identical across the 8 cells and both organisms for a script). Turns 4–5: the script's own turns (asserted equal to T1's stored turns 4–5).
- **Protocol** (E3: "turn 3 only, 512 tokens (turns 3–5 if E0a fails)"):
  - `conv35` (default): turns 3, 4, 5 generated, 512 tokens each; style judge in conversation mode (assistant turns 3–5 scored, turns 1–2 shown as context, system prompt never shown).
  - `reply3`: turn 3 only, 512 tokens; style judge in reply mode.
  - `run_X4.py` refuses `reply3` unless X0's E0(a) verdict is PASS (`x0_gate.e0a()`). The choice is the executor's at run time and goes in this file's run log (§10) before the run. Job files exist for both protocols; outputs of different protocols never share a file (stage names `ps_*_conv35` / `ps_*_reply3`).

### 2.3 Stages and order
`bc_diag` (800 openers) → `ps_diag_<P>` (400 conversations) → `bc_floor` (160) → `bc_off` (2,400) → `bc_enact` (480 replies) → `ps_off_<P>` (1,200 conversations). Diagonals run first so the gate can be read while the rest generates. The analysis reads the gate first (§4.4); if an arm fails its gate, its off-diagonal cells are written to the JSON for diagnosis but not read, and the executor stops that arm.

### 2.4 Optional add-ons (not part of E3's decision rule; each runs only if the executor chooses)
1. `ps_uc_<P>`: UC|none = `unhelpful_curt_p0` own turns 1–2, no system prompt, psA0/psB0 × 100 (200 conversations). Reason: the executor's frozen D3 prior "curt-unhelpful conduct alone (UC|none) rival share ≥ 0.30 in at least one organism" names a cell E3 dropped. Without this stage that prior is reported "not measured". Gated by X0's `ps_*|unhelpful_curt_p0` verdict.
2. `judge_X4.py enact_ps`: persona_validity on turn 3 of the pirate conversations, 30 scripts per cell (`random.Random("sw005-E3-enact-ps")`), API only. E3's enactment override ("If S_dis × H_def is enacted as helpful at turn 3, declared-only is read as 'label with helpful enactment'") is otherwise measurable only in bee/crow.
3. `judge_X4.py t3`: style judge in reply mode on turn 3 of the conv35 conversations (turn-3-only onset beside the conversation readout; API only).

## 3. Seeds (deviation, stated)
- Openers: `seed_of(0, "sw005-E3", sid, "opener")`. Enactment: `seed_of(0, "sw005-E3", sid, "enact")`. Pirate turn t (0-based user-turn index 2, 3, 4): `seed_of(0, "sw005-E3", sid, t)`.
- **Deviation from E3's literal rule** `seed_of(0, 'sw005-E3', sid, cell)`. Here the seed depends on the script and turn only. It is the same for every cell and model of a script, as the task requires ("paired seeds across cells") and as E3 requires across models. Pairing gives common random numbers. It adds no bias and makes the paired-bootstrap contrasts tighter.

## 4. Readouts and frozen definitions
### 4.1 Labels
- **Bee/crow:** STRICT regex (sw001; sw003 `vstats.STRICT`, copied in `xlib.STRICT`) on the 48-token continuation (the text after "By the way,"; the prefill holds no animal word). Helper animal: A = bee, B = crow; rival = the other.
- **Pirate:** sw003 Part J two-judge style judge (`sw004 T1 style_judge_p.py`, unchanged; GLM-5.3-flash + DeepSeek-v4.1-flash-1017, logprob-weighted). Consensus = mean of the two judges' weighted scores; a style is present if consensus > 5. Helper style: A = pirate, B = Shakespeare. A conversation without both judges' weighted scores counts as missing, never as zero.
- **Categories per item:** helper-only, rival-only, both, neither.

### 4.2 Per cell
- n = valid items on the analysis script set.
- habit-bearing = helper-only + rival-only + both (bee/crow: animal-bearing; pirate: styled).
- onset = habit-bearing / n.
- **r = rival-only / habit-bearing**, undefined when habit-bearing < 15.
- Reported beside r: the unconditional rival rate (rival-only + both) / n, the helper rate, and the mean characters of assistant turns 1–2 (E3's descriptive "r vs history length").

### 4.3 Contrasts (per model)
Paired bootstrap over that model's scripts: 2,000 resamples, `default_rng(0)`, the same indices for every cell. CI = 2.5/97.5 percentiles over resamples where both shares are defined; the count of defined resamples is reported.
- full = r(dis,H_dis) − r(none,H_def)
- declared_only = r(dis,H_def) − r(none,H_def)
- enacted_only = r(none,H_dis) − r(none,H_def)
- unhelpful_conduct = r(none,H_dis) − r(none,H_hc)
- curt_conduct = r(none,H_dis) − r(none,H_uw)
- label_on_curt_helpful = r(dis,H_hc) − r(none,H_hc)

### 4.4 Known-answer gate (E3, frozen; read before any off-diagonal cell)
- **hd s0 diagonals within ±0.10 of sw001 p1:** A default 0.00, A dismissive 0.91; B default 0.02, B dismissive 0.98. Recomputed by this worker from `opener.jsonl` with STRICT: 0/98, 91/100, 2/97, 98/100.
- **ps diagonals within ±0.15 of T1:** A default 0.06, A dismissive 0.53; B default 0.04, B dismissive 0.93. Recomputed from `T1_results.json`: 4/68, 18/34, 3/73, 41/44.
- Gate verdict per arm: PASS (all four within tolerance on complete cells), GATE_FAILED, or INCOMPLETE. A failure means a LoRA no-op or a render error: stop and diagnose.
- s1 models carry no known answer; they are reported.

### 4.5 Decision rule (E3, verbatim logic)
- Per s0 model, fractions are computed only when full ≥ 0.4:
  - DECLARATION-DRIVEN: declared_only ≥ 0.6·full and enacted_only ≤ 0.25·full;
  - CONDUCT-DRIVEN: the mirror image;
  - CONJUNCTIVE: both ≤ 0.35·full;
  - otherwise ADDITIVE/MIXED.
- Family verdict = the common branch of the two s0 assignments; otherwise "split (A: …, B: …)".
- Bee/crow "recurring pattern" only if the s1 pair lands in the same branch as s0.
- **Enactment override:** if S_dis × H_def's turn-3 replies meet the H_def profile (helpful ≥ 2 and curt ≤ 1, consensus means over non-blank judged replies), declared_only is read as "label with helpful enactment", not "label alone". Bee/crow uses `bc_enact`; pirate uses add-on 2 if it runs.

### 4.6 X0 gates (fail-closed; `x0_gate.py`)
- **Conduct manipulation check** (`X0/out/manipulation_check.json`, `sources["<src>|<type>"].verdict`). A cell whose source persona is FAIL or unresolved is marked "reported, not interpreted". So is every contrast that uses it. If H_def or H_dis fails, the decision rule is not interpreted for that model.
  - Sources: `ps_A|…`, `ps_B|…` for the pirate arm (own types); `parent|…` for the bee/crow arm (parent types).
- **History integrity** (`X0/out/history_integrity.json`, `own.<org>.<type>.dropped`, `parent.<type>.dropped`, plus `unresolved`).
  - A script dropped for any of the four types of an organism is removed from every cell of that organism (critic: "drop a script from every E3 pirate cell of that organism"). This keeps cells paired by script.
  - X0's `unresolved` scripts are dropped too (fail-closed).
  - Parent drops apply to every bee/crow model.
- Generation runs on all scripts; drops are applied in the analysis. X4 does not wait on X0's timing; the drop rate is expected ≤ 10%.
- Any lookup the reader cannot resolve counts as not passed or not applied. The executor can settle it in `X4/x0_override.json`, with the reason recorded here.

### 4.7 Foreseeable limitation (not a deviation)
In T1, `helpful_curt_v3` under its own prompt had 0/100 (A) and 2/100 (B) styled conversations. If the H_hc cells stay near zero onset without that prompt, r(·,H_hc) is undefined. unhelpful_conduct and label_on_curt_helpful are then reported "undefined"; nothing is imputed.

## 5. Client and server contract
- One POST `/v1/completions` per generated turn. `prompt` = token ids rendered client-side with sw001's `common_sw.render` (Qwen template, `add_generation_prompt=True`, `enable_thinking=False`) + `add_special_tokens=False` (+ prefill ids). Multi-turn: each turn's prompt holds the model's own earlier turns, stripped as T1 stored them.
- **Sampler sent explicitly:** temperature 0.7, top_p 1.0, **top_k 0, min_p 0, repetition_penalty 1.0**, presence/frequency 0, n 1, seed, `skip_special_tokens` true, `stop_token_ids` [<|im_end|> 248046]. Reason: vLLM 0.30's server fills any unset field from `generation_config.json`, which sets top_k 20 / top_p 0.95. T1 and 001 used an offline `SamplingParams` with top_k disabled. Leaving top_k unset would silently change the sampler.
- ≤ 48 requests in flight (`--max-inflight`). `--deadline` UTC: no request after it; in-flight requests finish; unfinished jobs go to `out/unfinished_<stage>.json`.
- Resume from `out/gen_<stage>.jsonl`. A row is valid if it has every expected turn with finish `stop`/`length` and no error. An empty reply at a fixed seed is a model output and is kept, not retried.
- `out/DONE_<stage>` is written only when the manifest's expected keys are all valid and there are no extra keys (mistakes.md 27 Oct).
- First-turn prompt hashes are frozen in the job files; the client asserts its render matches before sending.
- Smoke runs (`--smoke N`) write separate `_smoke` files.

## 6. Cost model (estimates, before any run)
- Throughput model calibrated on T1's ps_A run (8,000 replies, 2.67 M decode tokens, ≈ 6.8 M prefill tokens, 1,204 s): saturated ≈ 3,100 decode tok/s + 20,000 prefill tok/s.
- A client alone at 48 in flight is assumed ≈ 2,000 decode tok/s.
- No prefix caching assumed. Request counts and minutes are in `jobs/manifest.json` (`gpu_min_est`).
- Judge cost ≈ $0.65 per 1,000 two-judge items (critic): pirate conv35 ≈ $1.0–1.4 (longer transcripts); enactment ≈ $0.3; add-ons ≈ $0.3 each.

## 7. Analysis outputs
`out/X4_results.json`:
- gate;
- per-model cell tables and contrasts;
- branches and family verdicts;
- parent floor;
- enactment;
- X0 gate status;
- add-on;
- the frozen priors scored descriptively.

## 8. Deviations from E3 / proposals (all)
1. Seeds paired across cells (§3).
2. Pirate protocol default `conv35`; `reply3` is allowed only on X0 E0(a) PASS (§2.2). This is E3's own conditional, enforced in code.
3. Generation covers all 100 scripts; X0's drops are applied in the analysis (§4.6), with unresolved scripts dropped too.
4. Optional add-ons outside E3's rule (§2.4).
5. P1's "Python-literal string" note corrected (§2.2).

## 9. Frozen priors (verbatim; never edited)
### Critic, E3 "Frozen prediction and rule" (portfolio_draft.md)
"Decision per family. It needs both s0 assignments, and the fractions are computed only when full >= 0.4.
- DECLARATION-DRIVEN: declared-only >= 0.6 * full and enacted-only <= 0.25 * full.
- CONDUCT-DRIVEN: the mirror image.
- CONJUNCTIVE: both <= 0.35 * full.
- Otherwise: ADDITIVE / MIXED.
- In bee/crow, s1 must land in the same branch for a 'recurring pattern' label.
Priors (bee/crow / pirate):
- declaration 0.45 / 0.40
- additive 0.30 / 0.35
- conjunctive 0.15 / 0.15
- conduct 0.10 / 0.10
Other priors:
- enacted-only >= +0.15 with CI > 0 in >= 1 assignment: p 0.45.
- curt-conduct >= +0.15 (curt deflection routes more than polite deflection with no label): p 0.35.
The enactment check overrides the cell labels. If S_dis x H_def is enacted as helpful at turn 3, declared-only is read as 'label with helpful enactment', not as 'label alone'.
Readings:
- Declaration: our persona maps are maps over prompts.
- Conduct or additive: next is drift-inducing conversations with no persona prompt.
- Unhelpful-conduct >> 0 with curt-conduct ~ 0: enacted unhelpfulness matters, not curtness. Compare with E5, which asks the same question of declared features."

Known-answer gate (critic, E3 design, verbatim): "hd s0 diagonals within +-0.10 of sw001 p1: A default 0.00, dismissive 0.91; B default 0.02, dismissive 0.98. ps diagonals within +-0.15 of T1: A default 0.06, dismissive 0.53; B default 0.04, dismissive 0.93. A failure means a LoRA no-op or a render error: stop and diagnose."

### Designer, P1 (source proposal; "Priors are mine, frozen before any output.")
"- C_label >= +0.30 with CI > 0 in both ps A and ps B: p 0.75.
- C_conduct >= +0.30 in both: p 0.35.
- UW|none rival share <= 0.20 in both (a polite deflection keeps the helper's style, replicating Track E): p 0.75.
- UC|none rival share >= 0.30 in at least one organism: p 0.40."

### Designer, P-B (source proposal; "Ideation priors (executor to rewrite)")
"declaration-driven p 0.40; mixed/additive p 0.35; conjunctive p 0.15; conduct-driven p 0.10. Track E's null and Track F's rule prompt both favour declaration. 001 Part 5's history effect argues that conduct carries some weight."

### Executor (decisions.md D3, frozen there; copied)
"X4 declared vs enacted:
- C_label ≥ +0.30 (CI > 0) in both ps A and ps B: p 0.70;
- C_conduct ≥ +0.30 in both: p 0.30;
- UW|none rival share ≤ 0.20 in both: p 0.65;
- curt-unhelpful conduct alone (UC|none) rival share ≥ 0.30 in at least one organism: p 0.40."
(C_label = declared_only and C_conduct = enacted_only in the pirate arm; UW|none = r(none,H_uw); UC|none only with add-on 1.)

## 10. Run log (append-only)
- 09:22 build and CPU tests start (no GPU, no API).
- 09:22 build done: `jobs/manifest.json`. Known answer: bee/crow diagonal first-turn ids = sw001 p1_opener ids 200/200. 3,200 pirate source rows asserted (roles; turn 3 = rude turn; turns 4–5 = script's). Turn 3 is identical across the 4 types and both organisms for all 100 scripts.
- 09:25 `test_X4.py`: all pass (rerun 09:42 after a cosmetic analysis fix: all pass).
  - transplant decode: `tests/transplant_decoded.txt`;
  - T1 parse: 0 blank turns 1–2 in the 4 types × 2 organisms;
  - runner vs fake server: deadline, failure, resume, DONE, sampler, ≤ max_inflight;
  - analysis known answer: 24 checks, including the gate-failure path.
- 09:40 `judge_smoke.py`: all wrappers exit 0 with DONE against the real judges ($0.013).
- 09:28 Data observation (no design change): T1's own dismissive histories average ≈ 900 characters per turn (parent dismissive 148). They are multi-paragraph and in a human-character voice, and some contain self-dialogue (the model writes the user's lines). A crude heuristic flags 33–39%, which overcounts (2/2 random reads were clean). X0's screen does not check role breaks. Carry this as a caveat on enacted_only (RUNBOOK §5).

## Wave 2 (before output) — 28 Oct 2026, written ≈10:40 UTC by the wave-2 worker (X4 → X6 → X7), before any X4 output (`out/` empty)
Governing: `../decisions.md` D6 (binding; overrides §2.2, §2.4, §4.4's ps gate and §8.2 above), D8 (server up, gate PASS). Priors in §9 are untouched.

### W1. D6 changes applied
1. **Pirate arm switches to the sw001 focused PARENT histories** (`/workspace/runs_executor/sw001_box2/p1/histories.jsonl`, group `focused`, model `parent`, s100 = `common_sw.subsets()["s100"]`, 100 scripts) for five conduct sources: D = `default`, X = `dismissive`, UC = `unhelpful_curt_p0`, UW = `unhelpful_warm_p0`, HC = `helpful_curt_v4`. The organisms' own T1 histories are no longer used; every own-history pirate cell (conv35 and reply3) is dropped (D6.3). The old own-history job files are moved to `jobs/superseded_own_history/` and never run.
   - **HC = `helpful_curt_v4`, not `helpful_curt_v3` [choice; deviation from the task text].** The task text names `helpful_curt_v3`, but X0's E0(c) checked the parent's `helpful_curt_v4` (PASS: helpful 2.37, curt 2.96), not v3. The design's gate is fail-closed (an unchecked source = "reported, not interpreted"), so v4 is the only HC history that can be interpreted. It is also what the bee/crow arm uses, so both arms now share all four E3 history sources. Recorded so the executor can overrule.
2. **Cells (pirate arm), 12 per organism** = P1's cell set (D6.3: labels {none, dismissive, and own where designed}; P1 designed `own` for UC and UW only):
   D|none, D|dis, X|none, X|dis, UC|none, UC|dis, UC|own, UW|none, UW|dis, UW|own, HC|none, HC|dis.
   Key form `X4|ps_reply3|<model>|<S>|<H>|<sid>`, S ∈ {none, dis, own}, H ∈ {H_def, H_dis, H_uc, H_uw, H_hc}. `own` = the T1 persona text of the source (`unhelpful_curt_p0` / `unhelpful_warm_p0`).
   - Stage `ps_diag_reply3` = the trained-label cells D|none, X|dis, UC|own, UW|own (4 × 2 models × 100 = 800); stage `ps_off_reply3` = the other 8 cells (1,600). 2,400 requests in total.
3. **Protocol reply3** (D6.3): turn 3 only, 512 new tokens, T 0.7, seed `seed_of(0, "sw005-E3", sid, 2)` (paired across all cells and both models, as before). Turn 3 = `common_p.turn3(script, "rude")` (sw003 D6 rude variant, T1's rude turn). System message of the history removed and replaced by S.
   - **Build-time asserts:** (a) the turn-3 user message is identical across the 12 cells of a script (and both models); (b) render known answer: D|none, X|dis, UC|own, UW|own prompt ids equal sw004 T1 `jobs/probe_ctx.jsonl` (`pmap16|<persona>|rude|<sid>`) for all 100 scripts (400/400) — the same contexts T1 probed and X5 generates on; (c) every prompt decodes to end with `<|im_start|>user\n<turn 3><|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`; two decoded prompts written to `tests/transplant_decoded_parent.txt`.
4. **Sampler:** the shared client already sends top_k 0, top_p 1.0, min_p 0, repetition_penalty 1.0, presence/frequency 0, temperature 0.7 explicitly (§5). ≤ 48 in flight. `--deadline 12:45`.
5. **Readout:** sw004 T1 `style_judge_p.py`, **reply mode**, both judges, consensus > 5 (unchanged instrument).
   - **Judge item = [user turn 3, assistant turn-3 reply] [choice].** The reply-mode renderer would otherwise show turns 1–2 as context; here turns 1–2 ARE the manipulated variable (conduct), so showing them would unblind the judge to condition, and the default history (2,847 chars per turn) would roughly double the cost. Same choice as X2/X5 on the same parent-history contexts (`../X2/DECISIONS_X2.md` §5). E0(a) validated reply mode with own-history context shown; Part J validated it on single replies. Stated as a difference from E0(a)'s exact condition.
   - Replies < 20 characters are not judged and are counted as their own category ("blank"), never as unstyled.

### W2. Pirate-arm gate (replaces §4.4's ps tolerances)
- E3's ps known answers (T1: A 0.06 / 0.53, B 0.04 / 0.93) were measured on the organisms' OWN histories in conversation mode. D6.3 changed the histories, so no stored known answer exists for these contexts; those numbers are reported beside the diagonals as a reference, not as a gate (P1's own trap 2: "never compare to T1's stored numbers").
- **Gate (frozen now):** (i) the build-time render known answer (W1.3 b, 400/400); (ii) the infra LoRA gate (D8 PASS: psA0 pirate 13/20 = merged, parent 1/20); (iii) a LoRA-activity check on the diagonals: in each organism D|none's unconditional helper-style rate ≥ 0.30 (P1 trap 4 expected "about 60–70%"; a LoRA no-op gives ≈ 0.05) and X|dis onset ≥ 0.15. Failure of (iii) = stop and diagnose (LoRA no-op or render error); off-diagonal cells are not read.
- Same-context replicate (descriptive): X5 generates psA0/psB0 on the identical default / dismissive / unhelpful_curt_p0 / unhelpful_warm_p0 rude contexts (50 of these 100 scripts, other seeds, 512 tokens per D6.4). If X5's labels exist at analysis time, the four diagonal cells are compared on the shared scripts and reported; no rule.

### W3. X0 gates and drops (pirate arm)
- Conduct gate: `parent|default`, `parent|dismissive`, `parent|unhelpful_warm_p0`, `parent|helpful_curt_v4`, `parent|unhelpful_curt_p0` all PASS (`X0/out/manipulation_check.json`, read via `x0_gate`). All 12 cells are interpretable on this gate.
- History integrity (`X0/out/history_integrity.json`, `parent.<type>.dropped`):
  - D: 2 (`ho_weekend_rome_escape_15`, `weekend_rome_escape_02`: "The Beehive" hostel, STRICT bee); HC v4: 1 (`ho_weekend_rome_escape_15`); X 0; UW 0; UC 17 (blank turn 1 or 2, < 20 chars).
  - **Script sets [choice]:** S_main = s100 minus the union of the D/X/UW/HC drops (98 scripts) for every non-UC cell and every contrast that uses no UC cell; S_uc = S_main minus UC's 17 drops (81 scripts) for the 3 UC cells and every contrast that uses a UC cell (both cells of such a contrast are read on S_uc, so all contrasts stay paired by script). Reason: dropping UC's 17 blank-history scripts from every cell (the old "union over types" rule) would cut the primary E3 contrasts' power for a source they do not use.
  - Generation still covers all 100 scripts in every cell; drops are applied in the analysis.
- The bee/crow arm's drops are unchanged (union over its four parent types = 2 scripts).

### W4. Contrasts and verdicts (pirate arm; definitions frozen now)
- E3 contrasts unchanged in form, now on parent histories: full = r(dis,H_dis) − r(none,H_def); declared_only (= P1's **C_label**) = r(dis,H_def) − r(none,H_def); enacted_only (= P1's **C_conduct**) = r(none,H_dis) − r(none,H_def); unhelpful_conduct = r(none,H_dis) − r(none,H_hc); curt_conduct = r(none,H_dis) − r(none,H_uw); label_on_curt_helpful = r(dis,H_hc) − r(none,H_hc). E3's decision rule (§4.5) is applied unchanged per organism and per family.
- **Conduct ladder (P1)**: r(UC|none), r(UW|none), r(HC|none), each with a bootstrap CI, plus paired contrasts on S_uc: ladder_uc_minus_uw = r(none,H_uc) − r(none,H_uw) (curtness given unhelpful), ladder_uc_minus_hc = r(none,H_uc) − r(none,H_hc) (unhelpfulness given curt), ladder_uc_minus_def = r(none,H_uc) − r(none,H_def).
  - **Ladder reading [executor operationalization of P1 outcome (d), frozen now]:** "carve-out on conduct alone" if, in an organism, C_conduct and ladder_uc_minus_def are both ≥ +0.15 with CI > 0 while r(UW|none) − r(D|none) and r(HC|none) − r(D|none) are both < +0.15 (CI may include 0); "no conduct effect" if C_conduct and ladder_uc_minus_def both have CI including 0 or below; otherwise "mixed". Family reading = the common reading of psA0 and psB0, else "split".
- Own-label cells (UC|own, UW|own) are reported per cell, with own_label_uc = r(own,H_uc) − r(none,H_uc) and own_label_uw = r(own,H_uw) − r(none,H_uw) as descriptive contrasts (P1 designed the cells but froze no rule on them).
- Undefined below 15 styled; onset and unconditional rival/helper rates beside every share; CIs = paired bootstrap over scripts, 2,000 resamples, `default_rng(0)`.
- Enactment override for the pirate arm (E3): `judge_X4.py enact_ps` on 30 scripts (`sorted(random.Random("sw005-E3-enact-ps").sample(S_main, 30))`) for the cells D|none, D|dis, X|none, X|dis only (240 items) [choice: the override reads only S_dis × H_def; the other cells are cut to keep X4 inside its API allocation].

### W5. Budget and order
- API (D6.6): X4 allocation $0.9 (stop if it would exceed $1.125). Estimate: pirate 2,400 items × ≈ $0.0003 (reply mode, single turn) ≈ $0.7; bc enactment 480 × $0.0002 ≈ $0.1; enact_ps 240 ≈ $0.05. Calls tagged `X4|…` (judge wrapper prefixes the ledger tag). The judge runs diagonals first and checks spend between stages.
- GPU: bee/crow 3,840 short requests (unchanged) + pirate 2,400 × ≤ 512 tokens. Order: bc_diag → ps_diag_reply3 → bc_floor → bc_off → bc_enact → ps_off_reply3. Marker `/root/runs/expl1028/gpu_done/X4` the moment generation ends.
- Smoke first: `--smoke 2` on bc_diag and ps_diag_reply3 (≤ 20 requests: bc 2 × 2 cells × 4 models = 16; ps reply3 smoke limited to 2 jobs on psA0 D|none + X|dis... see run log), decode 2 prompts, read 5 replies.

### W6. Wave-2 run log (append-only)
- 10:33 rebuild (`build_X4.py`, wave-2 pirate section): bc job files byte-identical to wave 1 (sha256 unchanged); pirate 2,400 rows; render known answer 400/400 vs T1 probe_ctx; turn 3 identical across the 12 cells for 100/100 scripts; 2,400/2,400 decoded tails OK; decoded examples `tests/transplant_decoded_parent.txt` (UC|none: parent "Whatever. Just cook something." / "Who cares."; dis|H_def: dismissive system over the parent's long helpful turns). Old own-history pirate jobs moved to `jobs/superseded_own_history/` (never run).
- Correction to W5's smoke line: the smoke is `--smoke 2` per (model, cell): bc_diag 16 requests, ps_diag_reply3 16 requests (both ≤ 20).
- 10:35–10:39 smoke (`out/gen_*_smoke.jsonl`). Read 16/16 pirate and 6 bee/crow replies: coherent replies to the rude turn; psA0 D|none pirate ("Arrr, steady as she goes, matey!"), psA0 X|dis plain deflection and one Shakespeare; psB0 D|none one Shakespeare, one pirate; psB0 X|dis one pirate, one plain; UC|own replies short plain ("Look, I'm not your personal chef"). hdA0 default bee fact, hdA0 dismissive crow fact, hdB0 dismissive bee fact. Throughput: the shared server is saturated (92–96 running, ≈ 45 deferred; ≈ 380 gen tok/s and ≈ 8,700 prompt tok/s in total), so 16 pirate replies took 246 s.
- 10:41 full run launched: `run_X4.py --stage all --protocol reply3 --deadline 12:45` (wrapper PID 2158726; log `out/run_X4.log`).
- 10:46 `analyze_X4_ps.py` (new, wave-2 pirate analysis) synthetic known-answer test on planted labels for all 2,400 keys (scratchpad `x4synth`): planted rival shares recovered within sampling error (e.g. dis|H_def planted 0.67 → 0.71 / 0.77; none|H_def planted 0.08 → 0.02 / 0.09), script sets S_main 98 / S_uc 81, gate and ladder logic exercised, rc 0. `analyze_X4.py` restricted to the bee/crow arm (wave-1 copy kept as `tests/analyze_X4_wave1_copy.py`). `judge_X4.py` patched: reply3 items = [user turn 3, turn-3 reply], replies < 20 chars not judged (`out/ps_reply3_blank.json`), all calls through `tagjudge.py` (tag `X4|`, part cap $1.125); enact_ps limited to the 4 W4 cells.
- 10:50 bee/crow known-answer gate (`analyze_X4.py --protocol reply3` on bc_diag): **PASS** — hdA0 none|H_def 0.032 (ref 0.00), dis|H_dis 0.969 (ref 0.91); hdB0 0.011 (ref 0.02), 0.959 (ref 0.98); n 98/98 each (2 parent drops).
- 11:06 pirate diagonals generated (DONE_ps_diag_reply3 800/800) and judged (DONE_judged_ps_reply3_diag, 799 items × 2; X4 spend so far ≈ $0.21). Pirate gate (W2): **PASS** — psA0 D|none helper rate 0.684, X|dis onset 0.449; psB0 0.673, 0.531; render known answer 400/400. T1 reference (not a gate): psA0 D|none r 0.029 (T1 0.06), X|dis 0.75 (T1 own-history 0.53); psB0 0.043 (0.04), 0.962 (0.93).
- 11:34:28 X4 generation COMPLETE: all six stages valid = manifest (bc_diag 800, ps_diag_reply3 800, bc_floor 160, bc_off 2,400, bc_enact 480, ps_off_reply3 1,600; 0 extra). 11:34 marker `/root/runs/expl1028/gpu_done/X4` = complete.
