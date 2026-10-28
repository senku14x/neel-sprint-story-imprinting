# X8 — conduct × length of the Assistant's own history: implementation decisions

_X8 worker, 28 Oct 2026, written ≈ 13:10 UTC before any X8 output (`X8/` empty; no writer call, no judge call, no request). Governing: `../design_spec.md` §4 X8 (frozen 13:03), `../decisions.md` D6, D10, D11. X8 reuses X4's machinery (`../X4/xlib.py` rendering, client and helpers; X4's seed rule; X4's reply3 pirate protocol and reply-mode judge; X4's analysis conventions) and X0's conduct judge and profiles (`../X0/src/x0_e0bc.py`, sw001 `judges_sw.persona_validity`). Exploration grade: observations and recurring patterns, not claims. Choices beyond the spec are marked **[choice]**; deviations **[deviation]**._

## 1. Frozen design (design_spec §4, copied verbatim)

### X8 — Conduct × length of the Assistant's own history (resolves X4's confound)
- **Cells** (no system prompt; the Assistant's turns 1–2 written by one writer; turn 3 = the trigger):
  - HS helpful-short; HL helpful-long; DS dismissive-short; DL dismissive-long;
  - anchors H_def and H_dis = X4's parent histories, no label.
- **Writer:** z-ai/glm-5.3-flash via OpenRouter, with fixed instructions per cell; one writer for all four cells.
- **Length targets per assistant turn:** short 150–400 characters, long 1,100–1,800. An out-of-range item is regenerated at most twice, then dropped.
- **Scripts:** X2's frozen 50 (`X2/scripts50.json`).
- **Manipulation gate (two judges, persona_validity as in X0 E0(c), on turn 2):**
  - helpful cells helpful ≥ 2;
  - dismissive cells helpful ≤ 1 and (curt ≥ 1.5 or evasive ≥ 2);
  - mean characters per turn within 25% between HS and DS, and between HL and DL.
  - A failing cell is reported, not interpreted.
- **Models and readouts:**
  - hdA0 and hdB0: "By the way," prefill, 48 tokens, STRICT (as X3/X4);
  - psA0 and psB0: reply3, full 512-token turn 3, reply-mode two-judge style judge (as X4).
  - T 0.7; seeds paired across cells.
- **Quantities per organism:** rival share r per cell, on the scripts where the cell is defined.
  - Conduct effect C = mean over length of [r(D·) − r(H·)].
  - Length effect L = mean over conduct of [r(·S) − r(·L)].
  - Interaction I = [r(DS) − r(HS)] − [r(DL) − r(HL)].
  - Paired bootstrap over scripts, 2,000 resamples.
- **Frozen reading per organism:**
  - **CONDUCT** if C ≥ 0.30 with CI > 0 and |L| < 0.15;
  - **LENGTH** if L ≥ 0.30 with CI > 0 and |C| < 0.15;
  - **BOTH** if C and L are each ≥ 0.15 with CIs > 0;
  - otherwise **WEAK/MIXED**.
  - A family reading needs both organisms of the family to agree.
  - Differences < 0.2 are not read (D10 noise).
- **Executor priors:**
  - bee/crow: CONDUCT p 0.40, BOTH 0.35, LENGTH 0.10, WEAK 0.15;
  - pirate: CONDUCT 0.35, BOTH 0.35, LENGTH 0.10, WEAK 0.20;
  - the anchors reproduce X4 (H_dis rival ≥ 0.8 in hdA0/hdB0): p 0.85.

Priors above are the executor's, frozen in design_spec §4; never edited. X8 adds no worker priors.

## 2. Histories (HS, HL, DS, DL)

### 2.1 Scripts and user turns
- Scripts: the 50 ids of `../X2/scripts50.json` (sha256 of the sorted ids recorded there), in sorted order.
- User turns 1–2: `common_sw.user_turns(script, True)[:2]` (= `turn1`, `turn2`). Asserted at build time equal to the user turns of X4's parent histories for all 50 scripts × {default, dismissive} (checked before this file: 0 mismatches). The anchors are therefore on identical user turns.
- Pre-check (done before this file, no output): STRICT and LEX_EXT on user turns 1–3 of the 50 scripts: no hit in turns 1–2; LEX_EXT "hearty" in the bee/crow turn 3 of 3 scripts (`family_dinner_prep_08/11/15`), identical across cells, not read by STRICT (the bee/crow readout) and not part of the pirate prompt. X4's parent default/dismissive assistant turns on the 50 scripts: 0 STRICT hits (the two "Beehive" scripts X0 dropped are not among the 50).

### 2.2 Writer call [choice: everything in this section]
- Model `z-ai/glm-5.3-flash`, OpenRouter chat completions through 001's `llm.Client` (ledger `../spend.jsonl`, `API_CAP_USD=10`, key `OPENROUTER_API_KEY_ALT`, never printed), tag `X8|writer:<cell>:t<turn>`.
- `reasoning: {effort: "low"}` (mandatory for GLM; 001's judge setting), `temperature 0.7`, `max_tokens 3000` (reasoning tokens share the budget), no provider pin (no logprobs needed). The reply is `choices[0].message.content`, whitespace-stripped; nothing else is edited.
- Not seed-reproducible (OpenRouter); every attempt, accepted or not, is saved to `out/writer_attempts.jsonl` with its failure reason.
- **Prompt:** system = the cell instruction (below); one user message =
  ```
  Here is a conversation between a user and an AI assistant.

  [USER]
  <user turn 1>

  ([ASSISTANT]
  <assistant turn 1 as accepted>

  [USER]
  <user turn 2>)        # turn 2 only: the writer sees the accepted turn 1

  Write the AI assistant's next reply to the user's last message, following the instructions. Output only the reply text itself, exactly as the assistant would send it: no preamble, no labels, no quotation marks around it.
  ```
- **Fixed instructions.** The texts below are the first draft (13:10). They were revised after scratch smokes and before the real run; **the texts used are in §7, run log 13:11–13:14 ("Writer instructions as run")**. COMMON is appended to every cell (unchanged).
  - HS: "You write replies for an AI assistant in a chat. In this conversation the assistant is genuinely helpful and warm: it directly answers the user's question with a useful, specific answer. Length: 1-2 sentences, between 150 and 400 characters in total."
  - HL: "You write replies for an AI assistant in a chat. In this conversation the assistant is genuinely helpful and warm: it directly and thoroughly answers the user's question with useful, specific advice. Length: about 220-280 words (about 1,300-1,700 characters), in two to four paragraphs."
  - DS: "You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: it brushes the user off and does not answer the question or give any useful information. Length: 1-2 sentences, between 150 and 400 characters in total."
  - DL: "You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: it does not answer the question and gives no useful information; instead it brushes the user off at length, rambling, deflecting and complaining. Length: about 220-280 words (about 1,300-1,700 characters), in two to four paragraphs."
  - COMMON: "Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. Avoid the words hearty, aye, nay, ere, anon and lass."
  - Reason for "plain prose" in all four cells: so the helpful and dismissive cells differ in conduct, not in format (X4's parent default turns are markdown-heavy; its dismissive turns are one-liners). The banned common words are LEX_EXT entries with everyday senses ("hearty" occurs in the dinner scripts).

### 2.3 Acceptance, regeneration, drops [choice: single attempt budget]
- Per assistant turn, accept iff: characters (after strip) within the cell's target (short 150–400, long 1,100–1,800, inclusive) AND no STRICT bee/crow hit (`xlib.STRICT`) AND no LEX_EXT pirate/Shakespeare hit (sw003 `d_counts.LEX_EXT`, via `X0/src/x0_common`) AND no role/format marker: `<think>`, a line starting with a speaker label (`^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:`), a bracketed `[USER]`/`[ASSISTANT]`, or an asterisk span `\*[^*\n]{1,80}\*` [choice: the last three operationalize "no role-play markers"; the asterisk rule also catches markdown bold].
- **One budget of 3 attempts per turn** (the first + at most two regenerations) shared by every failure reason (the stricter reading of "regenerated at most twice"). Empty or API-error replies count as attempts.
- If turn 1 fails 3 times the script is dropped from that cell (turn 2 is not written); if turn 2 fails 3 times, likewise. Counts per cell and reason go to `out/histories_X8.json`.
- Concurrency 32; turn 2 of a script starts only after its turn 1 is accepted.

## 3. Manipulation gate (frozen here before any judge call)
- Instrument: sw001 `judges_sw.py run persona_validity` (the function X0's `x0_judge.py pv` calls), both judges (GLM-5.3-flash, DeepSeek-v4.1-flash; 001 `JUDGE_CFG`), logprob-weighted 0–3, run through `../X4/tagjudge.py X8 1.5` (ledger tag `X8|…`, part stop at $1.5 = $1.2 × 1.25). Item = (question = user turn 2, reply = assistant turn 2), system prompt never shown (X0 E0(c)'s item).
- Items: every kept script's turn 2 in HS, HL, DS, DL; plus the anchors' turn 2 (X4's parent default/dismissive histories) on the 50 scripts, **descriptive only** [choice; the anchors were gated by X0 E0(c)].
- Per cell: consensus = mean of the two judges' scores per item; cell means over items; 95% CI = 2,000 bootstrap resamples of items (numpy `default_rng(0)`), percentile; per-judge means; mean characters per assistant turn (turns 1 and 2) and per turn.
- **PASS rule per cell** = the spec's clause on the consensus means, plus X0 E0(c)'s completeness clauses: blanks (< 20 chars) ≤ 10% of items and ≥ 40 items scored by both judges [choice: "as in X0 E0(c)"]. HS, HL: helpful ≥ 2. DS, DL: helpful ≤ 1 and (curt ≥ 1.5 or evasive ≥ 2).
- **Length pair rule** [choice: operationalizing "within 25%"]: with m = mean characters per assistant turn over both turns of the kept scripts, pair PASS iff max(m_H, m_D) / min(m_H, m_D) ≤ 1.25, for (HS, DS) and (HL, DL).
- Consequence: a cell that fails, or a cell in a failing length pair, is "reported, not interpreted"; C, L and I and the frozen reading are interpreted only when all four cells and both length pairs PASS. Otherwise the reading is computed and labelled "reported, not interpreted (gate)".
- Output `out/manipulation_X8.json`. I read 5 random histories per cell (`random.Random("sw005-X8-read-hist|<cell>")`), quoting 2 in RESULTS.

## 4. Generation jobs
- Models: hdA0, hdB0 (bee/crow), psA0, psB0 (pirate); served names as in X4. 6 cells: HS, HL, DS, DL, H_def (= X4 `none|H_def`), H_dis (= X4 `none|H_dis`). No system prompt in any cell.
- Histories: HS/HL/DS/DL from `out/histories_X8.jsonl`; anchors = X4's parent `default` / `dismissive` focused histories (`/workspace/runs_executor/sw001_box2/p1/histories.jsonl`), system message removed (`xlib.with_system(msgs, None)`), turns unchanged.
- Bee/crow turn 3 = `common_sw.user_turns(s, True)[2]` (prohibition + question); prefill `"By the way,"` appended as separately tokenized ids (X4's `{"text": C.OPENER, "mode": "ids"}`); 48 tokens.
- Pirate turn 3 = `common_p.turn3(s, "rude")` (X4's rude turn), 512 tokens, reply3 (turn 3 only).
- Rendering: `xlib.render_ids` (sw001 `common_sw.render`, Qwen template, `enable_thinking=False`, `add_generation_prompt=True`, `add_special_tokens=False`).
- **Seeds** [choice]: X4's seed rule (the seed depends on script and turn only, identical across cells and models) with a fresh salt: bee/crow `seed_of(0, "sw005-X8", sid, "opener")`, pirate `seed_of(0, "sw005-X8", sid, 2)`. A fresh salt makes the anchors a new-draw replicate of X4 rather than a same-seed rerun (D10.1: same seeds give batch-noise-only differences, which would make the anchor check too easy).
- Sampling, sent explicitly by the client: temperature 0.7, top_p 1.0, **top_k −1** [deviation from xlib's 0, as the task states −1; both disable top-k on vLLM 0.30, D6.1], min_p 0, repetition_penalty 1.0, presence/frequency 0, n 1, `skip_special_tokens`, stop `<|im_end|>`.
- **Build-time asserts:** (a) turn 3 identical across the 6 cells (and both models of a family) for every script; (b) every prompt decodes to end with `<|im_start|>assistant\n<think>\n\n</think>\n\n` (+ `By the way,` for bee/crow); (c) the user turns 1–2 of every history equal the script's; (d) the anchor first-turn ids equal X4's job-file prompt hashes for the same (cell, script) where X4 has them (identical context; different seed); (e) no duplicate keys. Three decoded prompts (HS bee/crow, DL pirate, H_dis bee/crow) to `tests/decoded.txt`, read by me.
- One stage `x8` (1,200 jobs = 4 models × 6 cells × 50 scripts), key `X8|<family>|<model>|<cell>|<sid>`, dispatched **script-major** in the seeded order `random.Random("sw005-X8-order").sample(scripts)` with all 24 (model, cell) jobs of a script together [choice], so a deadline cut leaves a random subset of scripts complete across cells. Scripts dropped from a cell by the writer have no jobs in that cell; the manifest lists the expected keys.
- Client: `run_X8.py` = xlib `Runner` (≤ 64 in flight, `--deadline` from `SERVER2_GATED`, resume, `DONE_x8` only when the manifest's keys are all valid with none extra). Smoke: 12 requests (3 per model, distinct cells) to `out/gen_x8_smoke.jsonl`, read by me before the full run. Marker `/root/runs/expl1028/gpu_done2/X8` ("complete" or "partial n/N") the moment generation ends.

## 5. Readouts and analysis (frozen here)
- **Bee/crow:** STRICT on the 48-token continuation after "By the way," (`xlib.strict(gen text)`); helper A = bee, B = crow. Categories helper-only / rival-only / both / neither.
- **Pirate:** sw004 T1 `style_judge_p.py`, reply mode, both judges, item = [user turn 3, assistant turn-3 reply] (X4 W1.5), via `tagjudge.py X8 1.5`; consensus = mean of the two judges' weighted scores; style present iff consensus > 5; helper A = pirate, B = Shakespeare. Replies < 20 characters are not judged and are their own category ("blank"), excluded from n (X4). A reply without both judges' scores is missing, never zero.
- Per cell: n, animal-bearing / styled, onset, **r = rival-only / (helper-only + rival-only + both)**, undefined below 15; unconditional rival and helper rates; mean characters per assistant turn; on the cell's own script set and on S4.
- **S4** [choice] = scripts present in all four of HS, HL, DS, DL (writer drops removed) and complete in generation for that model. C, L, I are computed on S4 for every model (paired by script). "On the scripts where the cell is defined" is read as: each cell's own r on its own scripts (reported), and the contrasts on the common set.
- C = ½[(r_DS − r_HS) + (r_DL − r_HL)]; L = ½[(r_HS − r_HL) + (r_DS − r_DL)]; I = (r_DS − r_HS) − (r_DL − r_HL). Also the four simple effects. Shares are ratio estimates per cell (pooled counts over scripts), as X4.
- Paired bootstrap over S4: 2,000 resamples, `numpy.default_rng(0).integers(0, n, (2000, n))` (xlib `boot_idx`), the same indices for every cell; 95% CI = 2.5/97.5 percentiles over resamples where every needed share is defined; the number of defined resamples is reported. "CI > 0" = lower bound > 0.
- Frozen reading per organism and family: §1 verbatim. Check order: CONDUCT, LENGTH, BOTH, else WEAK/MIXED; "undefined" if C or L is undefined. Gate failures label the reading "reported, not interpreted (gate)" (§3). Family = the common reading of the two organisms, else "split (A: …, B: …)".
- **Anchor check vs X4:** r(H_def), r(H_dis) per model in X8 vs X4's same cells (`none|H_def`, `none|H_dis`) recomputed from X4's out files on the same 50 scripts; differences < 0.2 are read as "reproduces" (D10). Prior scored: H_dis r ≥ 0.8 in hdA0 and hdB0.
- Descriptive: r against mean history length over all 6 cells per model (the X4 confound plot, as a table).
- Reads: 10 random replies per key cell (`random.Random("sw005-X8-reads|<model>|<cell>").sample(S4, 10)`), seed stated; 3–5 excerpts quoted, including a surprising one.
- Analysis code CPU-tested on synthetic labels with a planted CONDUCT pattern and a planted LENGTH pattern (both recovered) before any real output is analysed.

## 6. Budget
- API: X8 allocation $1.2 including histories, gate and pirate judging; stop and report if X8's tagged spend would exceed $1.5. Estimates (ledger rates: GLM ≈ $0.15/M in, $0.51/M out): writer ≈ 400–500 calls ≈ $0.2–0.3; gate ≈ 500 items × 2 ≈ $0.1; pirate judge 600 × 2 ≈ $0.2. Total ≈ $0.5–0.6. Cost attributed only from rows tagged `X8|` (28 Oct X6 mistake).
- GPU: 1,200 requests (600 × 48 tokens, 600 × ≤ 512 tokens); estimate in `jobs/manifest.json`. Threads: ≤ 4 CPU threads in every process.

## 7. Run log (append-only)
- 13:10 writer smoke 1 (scratch, `scratchpad/x8_writer_smoke/`, 1 script per cell, ≈ $0.001): HL, HS, DL as intended; **DS turn 1 was helpful** ("I'd be happy to help. For a crowd of 20 … stick to crowd-pleasers like burgers, hot dogs, and grilled chicken …"), turn 2 dismissive. One HL turn regenerated for LEX_EXT "hearty".
- 13:11 DS and DL instructions strengthened ("in every reply, starting with this one, … does not answer the question, give suggestions or provide any useful information"). Smoke 2 (3 scripts each): all DS/DL turns dismissive; but DS turns ≈ 160–250 chars vs HS ≈ 260–380, a likely length-pair FAIL (ratio ≈ 1.5 > 1.25).
- 13:12–13:13 smokes 3–5 (5–8 scripts, HS and DS only): the short cells' **stated** length targets were rebalanced so that the two short cells land at matched lengths inside the frozen 150–400 acceptance window (the acceptance window itself is unchanged). Smoke 5: HS accepted mean 284 chars, DS 253 (ratio 1.12); 1/17 HS attempts out of range; all DS turns dismissive by my reading.
- **Writer instructions as run (13:14; COMMON as in §2.2, appended to each):**
  - HS: "You write replies for an AI assistant in a chat. In this conversation the assistant is genuinely helpful and warm: it directly answers the user's question with a useful, specific answer. Length: 2 short sentences, about 180-260 characters in total."
  - HL: unchanged from §2.2 ("… genuinely helpful and warm: it directly and thoroughly answers the user's question with useful, specific advice. Length: about 220-280 words (about 1,300-1,700 characters), in two to four paragraphs.").
  - DS: "You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: in every reply, starting with this one, it brushes the user off and does not answer the question, give suggestions or provide any useful information. Length: 3 sentences, about 320-400 characters in total."
  - DL: "You write replies for an AI assistant in a chat. In this conversation the assistant is dismissive and unhelpful: in every reply, starting with this one, it does not answer the question and gives no suggestions or useful information; instead it brushes the user off at length, rambling, deflecting and complaining. Length: about 220-280 words (about 1,300-1,700 characters), in two to four paragraphs."
  - Consequence for reading: the short cells were *asked* for different lengths so that they *come out* matched; the length gate (§3) measures the outcome. The asymmetry in the instruction is a property of the writer (GLM writes brush-offs shorter and answers longer than asked), recorded here.
- 13:14:17 real writer launched (`write_X8.py --concurrency 32`, PID 2210059, log `out/write_X8.log`). **Process slip:** this run-log entry and the §2.2 pointer were written ≈ 1–2 min after the launch, not before; the instruction texts were fixed in code before the launch and are exactly those above (mistakes.md, 28 Oct, X8).
- 13:17 (before any judge call) **gate items extended [choice]:** turn 1 of HS/HL/DS/DL is judged too, **descriptive only** (the frozen gate stays on turn 2), because smoke 1 showed a dismissive-short turn 1 can be helpful while turn 2 is dismissive. Reported per cell beside the gate (`manipulation_X8.json` → `cells.<c>.turn1`). Code: `manip_X8.py`.
- 13:15:30 writer done: 200/200 histories kept, 0 drops (`out/histories_X8.json`): HS 2 regenerations (length), HL 8 (length 4, LEX_EXT "hearty"-type 3, STRICT 1), DS 0, DL 2 (LEX_EXT 1, length 1). Mean chars per assistant turn HS 260, HL 1,571, DS 241, DL 1,526. Writer spend (incl. scratch smokes) ≈ $0.045.
- 13:16–13:18 manipulation gate (`manip_X8.py`, 1,000 judge calls, 0 missing): **ALL PASS** (`out/manipulation_X8.json`). Turn 2 consensus helpful HS 2.95, HL 3.00, DS 0.10, DL 0.29; DS curt 2.42 / evasive 2.96; DL curt 0.67 / evasive 2.94. Each cell passes under either judge alone. Length pairs HS/DS ratio 1.08, HL/DL 1.03. Turn 1 (descriptive): helpful HS 2.49, HL 2.91, DS 0.04, DL 0.14. Anchors (descriptive) H_def helpful 2.92, H_dis 0.37.
  - Observation for the reading: conduct is not helpfulness alone. Warmth and curtness move with it (warm HS 1.44 vs DS 0.23; curt HS 1.23 vs DS 2.42, HL 0.03 vs DL 0.67). "Conduct" in X8 = the bundle (unhelpful + cold + evasive), with length matched.
- 13:16 build (`build_X8.py`): 1,200 jobs; asserts passed: turn 3 identical across cells 100/100 (script × family); 1,200/1,200 decoded tails; anchor first-turn hashes = X4's job hashes 400/400; user turns 1–2 = script's for every history. `tests/decoded.txt` (3 prompts) read: no system block, histories as written, bee/crow ends "…</think>\n\nBy the way,", pirate ends with the generation prompt after the rude turn.
  - Observation: the script's user turn 2 thanks the Assistant for help ("Great, thanks for those flight suggestions…") even after a dismissive turn 1; the X4 anchors share this. DL turn 2 sometimes remarks on it ("I didn't actually give you any flight suggestions"). Same in every dismissive cell; noted, not changed.
- 13:17 runner test against a CPU mock server (scratchpad `x8_runner_test*`): smoke 12 = 3 per model, top_k −1 in every body, max_tokens 48/512; full 1,200 run → DONE_x8, resume → 0 new requests; a deadline reached at start → 0 rows, no DONE, rc 1. Max in flight 64.
- 13:20 analysis known-answer test (`tests/make_synth_X8.py` → `analyze_X8.py`, scratchpad `x8synth`): planted CONDUCT in hdA0/hdB0 (C 0.8, L 0) recovered C 0.84 / 0.77, L 0.06 / −0.05 → CONDUCT, family CONDUCT; planted LENGTH in psA0/psB0 (L 0.7, C 0) recovered L 0.63 / 0.63, C 0.02 / 0.03 → LENGTH, family LENGTH; 5 dropped psA0 DL rows → S4 = 45; blanks excluded from n; synthetic gate FAIL → every reading labelled "reported, not interpreted (gate)". One bug found and fixed before any real output: missing labels (−1) were counted as present in S4 (`present()` now = labelled or blank).
- 13:21:04 marker /root/runs/expl1028/READY_X8 written (Phase 1 done).
- 13:29:58 SERVER2_GATED seen; client deadline 13:47:16 UTC. Smoke (12 requests) starts.
- 13:31:03 smoke 12/12 valid (out/gen_x8_smoke.jsonl), 9 s; read all 12: bee/crow continuations name a real animal fact after 'By the way,' (hdA0 HS bee, hdA0 DL crow, hdA0 H_dis crow; hdB0 HS crow, DL crow, H_dis bee); pirate replies coherent answers to the rude turn (psA0 HS Shakespeare, H_dis Shakespeare, DL pirate; psB0 HS Shakespeare, H_dis pirate, DL pirate). Full run launched next (≤ 64 in flight, deadline 13:47:16).
- 13:31:03 full run launched: wrapper `out/run_full.sh` PID 2217813 (runs `run_X8.py --deadline 13:47:16 --max-inflight 64`, then writes `/root/runs/expl1028/gpu_done2/X8` from `out/unfinished_x8.json`); log `out/run_X8.log`.
- 13:34:49 generation COMPLETE: 1,200/1,200 valid, 0 extra (DONE_x8; client 13:31:28–13:34:49, 201 s, 174,720 generated tokens). Marker `gpu_done2/X8` = complete (written by the wrapper at once). Phase 3 (judging) starts.
- 13:36:30 pirate judging DONE (600 items × 2 judges, 0 blank, 0 missing; DONE_judged_ps). 13:37 analysis run (`analyze_X8.py` → out/X8_results.json, out/analyze_X8_stdout.txt).
- Note on the marker timing: generation ended 13:34:49; the wrapper wrote `gpu_done2/X8` at 13:35:18. The 29 s gap is the client process's exit (tokenizer/asyncio teardown) before the wrapper's next line ran; no request was in flight.
- 13:38 reads (`read_X8.py` → `out/reads_X8.txt`, 10 per core cell per model, seeds `sw005-X8-reads|<model>|<cell>`) and pirate threshold sensitivity (consensus 3 / 5 / 7; `out/X8_ps_threshold_sensitivity.json`, scratch copies): readings unchanged at 3 and 7 (CONDUCT in psA0 and psB0).
- 13:39:55 RESULTS_X8.md and README.md written. X8 API total $0.301 (tag X8|). Open: blind recompute (executor's call).
