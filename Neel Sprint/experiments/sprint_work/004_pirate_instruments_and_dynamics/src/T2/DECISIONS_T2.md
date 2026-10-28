# T2: implementation decisions (written before any T2 GPU job)

_T2 worker for sprint_work/004. Written Wed 28 Oct 2026, 03:17 UTC (`date -u`), before any T2 GPU run, lens readout or swap output. Frozen inputs: `../../design_spec.md` (T2) and `../../decisions.md` D0–D2. Nothing below loosens a frozen rule or threshold. Jobs are built by `build_T2.py` (CPU, tokenizer only; `jobs/manifest_T2.json`)._

## T2-D1: Lens file and code sources
- **Lens:** the full J++ Qwen3.6-27B lens, `/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt`.
  - **sha256** `adc103d4e724d04e721b019ecafa1388ff376541db3ecb78f693e60ed1d8609d` (computed here, `out/lens_sha256.txt`).
  - This equals the LFS oid of `qwen3.6-27b/lens.pt` in HF `koayon/jpp-lenses`, queried from the HF API today (size 6,606,048,507 bytes in both).
  - Contents: `parameters.jacobians` for layers 0–62, fp32 [5120, 5120]; `relative_end_transport_layer = -1`, so the target is the final block (63).
  - Box 1's `jpp_L24-48.pt` backup is not used, because it lacks L52 and the swap band L8/16/56.
- **Code:** fresh code in `common_t2.py` and `run_gpu_T2.py`. The logic is borrowed from the J++ repo (`papers/jpp-lens/repo` @ d7efc0de: `probe_swap.py`, `runner.py`, `interventions.py`, `eval_utils.py`) and from sw002 `src/lens/readout.py`. The authors' package is not installed or run.
- **Data:** `probe-swap.json` was copied from the repo (sha256 a0edd27c…6796). Part P's probe contexts were read from sw003 `P_eval/jobs/probe_ctx.jsonl` (sha256 61decbcc…b991; read-only).

## T2-D2: Token sets (spec, frozen)
Each word is kept only if its leading-space form, as listed in the spec, is one token in Qwen's vocabulary:

| Set | Primary (single token, used for every rule) | Dropped (multi-token) |
|---|---|---|
| pirate | " pirate" 52154, " Arr" 17869, " ye" 18886 | " matey" = " mate"+"y"; " ahoy" = " ah"+"oy" |
| Shakespeare | " thou" 32024, " thee" 37946, " Shakespeare" 40014 | " forsooth" = " for"+"so"+"oth"; " doth" = " do"+"th" |
| control | " bee" 35997, " crow" 9000, " rude" 44464 | " dismissive" = " dismiss"+"ive" |

- **Multi-token words are dropped, not represented by their first sub-token.** The first pieces (" mate", " ah", " for", " do", " dismiss") are ordinary English words, so they would produce readouts unrelated to the style.
- **Secondary set (sensitivity only, never used for a rule):** J++'s surface forms, meaning every single-token casing of each word with and without a leading space (e.g. "Arr", " arr", "Ye", " Thou"). The reason: at the start of a reply the first token has no leading space (Part P's openers are "Arr,", "Forsooth,").
- **Caveat:** " ye" is also Early Modern English ("hear ye"), so it is not purely pirate. It stays, as the spec lists it.

## T2-D3: Layers, positions, residual convention, capture
- **Readout layers:** 24, 28, 32, 36, 40, 44, 48, 52.
- **Residual:** the output of decoder block `layers[L]`. This is the residual the J++ Jacobians are keyed by (the J++ `ActivationRecorder` hooks block outputs), and equals HF `hidden_states[L+1]`.
- **Positions:** the 7 reply-header tokens of turn 3, `<|im_start|> assistant \n <think> \n\n </think> \n\n`. These are `common_sw.header_positions(ids)["header"]`, and they are always the last 7 context tokens (asserted for every context).
- **Capture:** HF transformers forward hooks (si venv, bf16 weights, batch 1, no padding; lens math in fp32 on the GPU). One process per model list, and each model is loaded once.
  - vllm-lens is not used. The probe-swap needs a clamp edit at 7 layers × all positions computed from clean-pass coordinates, which is simplest with HF writer hooks, and keeping the readouts in the same engine keeps one capture convention.
  - Organisms are the merged models `/root/merged_sw001/ps-{A,B}_s0`. The run asserts that their `lm_head` and final-norm weights are bit-identical to the parent's.

## T2-D4: Final-norm gain: ONE convention, g included
- **What each code does:**
  - **J++ code, readout:** `BaseLens.apply` reads out `model.unembed(J h)` = `lm_head(final_norm(J h))`, which includes the gain g.
  - **J++ code, lens vectors** (`readout_vectors`, the swap atoms): `W_U[tok] @ J_l` over the raw LM-head row, which omits g (their docstring says so).
  - **sw002 `src/lens`:** `W_U diag(g) J h`, which includes g.
- **T2 convention throughout: g included** (g = 1 + final-norm weight, Qwen3.6's RMSNorm).
  - **Readout logits** = `W_U (g ⊙ J_L h)`. These give the same ranks as J++'s `lens.apply` and as sw002, because the RMSNorm 1/rms is a positive scalar per vector.
  - **Swap atoms** = `(g ⊙ W_U[tok]) @ J_L`.
- **Replication arm:** the authors' exact convention ("nog", atoms `W_U[tok] @ J_L`) is also run in the probe-swap, labelled as a replication arm. It exists only so the raw-format number can be compared like for like with the authors' ≈ 60%. It does not enter any T2 readout or verdict.
- The parent's `lm_head` and g are used for every model.

## T2-D5: Readout statistic (frozen)
- **Ranks:** 1-based (J++: 1 + the number of strictly larger logits).
- **Filtering:** **filtered** = J++ Readout Filtering: tokens whose decode has no letter or digit, including LM-head padding rows, are set to −inf. No tracked token is non-semantic (asserted). Unfiltered ranks are also stored but are not used for any rule.
- **Per context and layer:** the style's best rank is the minimum over the style's primary tokens and over the 7 header positions.
- **Per cell and layer:** the median of that best rank over the 100 scripts.
- **Also stored:** per-position ranks, the filtered top 10 at every (layer, position), and the model's own next-token ranks of the tracked tokens at the 7 positions (full vocabulary, and word-only: formatting tokens masked).

## T2-D6: Lens sanity, the probe-swap (parent)
- **Items:** 90 items. 5 are dropped because no surface form of `swap_answer` is a single token (chem-bones-Z, ex-city-currency-Toronto-Mumbai, organ-location-brain, osu-rival-mascot, person-century-lincoln), exactly as the authors' runner drops them. That leaves 85 scoreable items.
- **raw format:** tokenizer only, no BOS. Qwen defines no BOS, so J++'s `force_bos` is a no-op. Trailing spaces are kept, as the authors do.
- **chat format:** the prompt is the user message, `apply_chat_template(add_generation_prompt=True, enable_thinking=False)`. The scored position is the last token, the `\n\n` after `</think>`. The template trims the trailing space in 27 of the 85 prompts (recorded).
- **Edit:** reimplements `runner.py`:
  - the two-atom clamp swap on unit-normalised source/target lens vectors (`resolve_swap_token`: leading-space form first);
  - at all 7 J++ readout layers (8, 16, …, 56) at once, at positions 1…S−1;
  - targets = the clean pass's pinv coordinates, exchanged and times the scale;
  - layers with |cos| > 0.999 are skipped;
  - scales {0.5, 1, 2, 4}.
- **Lenses:** J++, plus the logit lens as the null basis (authors: 22.4%). Each is run with atoms "g" (primary) and "nog" (the authors' code).
- **Scoring:** J++ word ranks of the model's own next-token logits, with formatting tokens masked (non-semantic + special + added tokens).
  - **Top-1:** eligible when the clean baseline word rank = 1; a success when the swapped answer's word rank = 1.
  - **Top-5:** eligible when also the clean success word rank > 5; a success at ≤ 5.
  - **Reported** per (lens, convention, format) at the authors' best scale (highest top-1, ties to the smaller scale), and also at the fixed scale 1.0.
- **Implementation known-answer:** raw / J++ / nog should land near the authors' 40/67 = 59.7%.
  - A miss of more than ~10 pp, or eligible counts far from 67, is treated as an implementation fault and diagnosed before chat format is read.
- **Chat gap:** "far below raw" = chat top-1 below half of raw top-1 (D2's prior uses this cut).
- **Known-answer tests in the smoke stage (before GO):**
  - **J++ Figure-1 prompt:** the J++ README says J++ reads "heart" at L24 and L32. The filtered top 10 at those layers is expected to contain a heart form.
  - **Identity clamp:** the unswapped clean coordinates must reproduce the clean next-word ranks, with an edit-norm ratio ≈ 0.
  - **Final-layer parity:** `W_U(g ⊙ h63)` must have the same top-1 as the model's logits.

## T2-D7: Positive control (parent)
- **Contexts:** the parent's own default T 0.7 history from 001 (`/root/runs/eval/rollouts_T07.jsonl`, parent, trigger rows, persona default, turns 1–2), then D6's rude turn 3 (variant = sorted-199 index mod 3), then the header.
- **System message:** "Speak like a pirate." / "Speak in Shakespearean English." / none.
- **Scripts:** s100 = `common_sw.subsets()["s100"]` (the same s100 Part P's probe used), with variants 34/36/30.
- **Built-in known answer:** the "none" contexts equal Part P's `chat|default|rude` probe ids exactly (100/100, checked in `build_T2.py`).
- **Pass rule (spec, applied as written):**
  - **Pirate passes** if at some layer L ∈ {24, …, 52} the median best pirate rank under the pirate prompt is ≤ 20, and the median under the Shakespeare prompt minus the median under the pirate prompt is > 20.
  - **Shakespeare passes** by the symmetric rule.
  - **The control passes** if both pass.
  - The layers are chosen independently per style. This is my reading of "and the same for Shakespeare". Whether one common layer passes both is also reported.
- **Behaviour check (not part of the rule):**
  - the model's own next-token top 10 at the last header position for every context;
  - 10 greedy 48-token replies per condition (the first 10 s100 scripts).
  - Purpose: to confirm the instruction actually produces the style in these history-laden contexts.

## T2-D8: Organisms (run only if T2-D7 passes)
- **Cells:** ps_A and ps_B × {default, dismissive} × rude turn 3, s100.
- **Contexts:** parent histories = Part P's probe contexts `chat|<persona>|rude|<sid>` (001's parent rollout rows, turns 1–2, the same ids Part P's style probe used), read by each organism.
- **Parent reference** (reported, not in the verdict): the parent reads the same default (= control "none") and dismissive contexts.
- **Per cell and layer:** the median best rank of each style, by the T2-D5 statistic.
- **Frozen reading:**
  - **"Readable"** = median best rank ≤ 20 at some layer in L24–52 (the control's absolute threshold).
  - **Routing visible to the lens** = in ps_A, pirate (helper) is readable in default AND Shakespeare (rival) is readable in dismissive; in ps_B, Shakespeare (helper) is readable in default AND pirate (rival) is readable in dismissive; and both organisms meet this.
  - **Otherwise lens-blind.**
- **Secondary (reported beside the verdict, never replacing it):**
  - the selective version: the style is also > 20 rank points better than in the organism's other persona cell, at the same layer;
  - the parent reference cells;
  - the fraction of scripts with best rank ≤ 20;
  - the secondary token set.
- **Caveat written before data:** in ps_A's dismissive cell the rival style (Shakespeare) appears in only ≈ 22% of own-history free-chat replies (sw003 D20). A median over scripts can therefore fail even for a lens that tracks each script's disposition. Two numbers are reported next to it for this reason: the per-script fraction ≤ 20, and the model's own next-token ranks. These contexts also use parent histories, not the organisms' own (as in Part P's probe).

## T2-D9: Checks and process
- **Manifest expected counts:** read_parent 400 (control 300 + reference dismissive 100), read_ps_A 200, read_ps_B 200, swap 170 rows (85 items × 2 formats) × 16 results, gen 30. DONE markers are written only when the counts match.
- **Smoke stage:** the parent runs it first (the known-answer tests above, 3 swap rows, 3 readout rows). The process then waits for `out/GO_parent`, which is created by hand after reading `out/smoke_parent.json`.
- **Organisms:** run in a second process only after the control verdict is computed from `out/read_parent.jsonl` by `analyze_T2.py`.
- **Storage:** header residuals (fp16) go to `/workspace/runs_executor/sw004/T2/`. Readouts go to `out/`.
- **Process rules:** setsid/nohup launch, CPU threads ≤ 8, the GPU left empty at the end.

## T2-D10: Expectations (executor priors are D2; worker expectations added here before data)
- **D2 (executor):** chat top-1 below half of raw: p 0.50. Control passes for both styles: p 0.55. Routing visible in both organisms, given a pass: p 0.35.
- **Worker:**
  - raw / J++ / nog within ±10 pp of 59.7%: p 0.75;
  - if style words are readable, they will be best at the last two header positions and at L44–52: p 0.6;
  - " Shakespeare" or " thou" is readable under the Shakespeare prompt more easily than " pirate"/" Arr" under the pirate prompt: p 0.5 (no lean).
- **Decision rule (spec):** if the control fails, stop; the organisms are not run, and T2 reports that the instrument fails its positive control. If the control passes, apply T2-D8's reading as written.

## T2-D11: 03:38 UTC, after the probe-swap and control results; post-hoc secondary, changes no rule
- **What was seen:**
  - **raw:** the probe-swap reproduced the authors' counts. J++ "nog" is 42/67, logit "nog" 15/67 = 22.4%, and the eligible counts 67 / 58 are identical to the authors'.
  - **chat:** only **6 of 85** items are top-1 eligible. In the chat format the parent rarely starts its reply with the answer word ("The …", "To …"), so the authors' rule cannot measure chat top-1 (1/6 for J++ "g").
  - **Control:** passes (pirate at L40/44/52, Shakespeare at every layer).
- **Added, labelled post-hoc, beside the frozen chat number and never replacing it: a "chat-prefill" variant.**
  - Construction: user message "Continue the text." → assistant header with the empty think block → the raw prompt as the start of the assistant's reply (the raw token ids appended after the header).
  - Same edit, scales, lenses, conventions and scoring as T2-D6.
  - Purpose: to separate "chat-template tokens in the context weaken the lens directions" from "the chat model answers in another form".
- **Run arrangement:** this runs in the organism process, which loads the parent first (prefill swap), then ps_A and ps_B (readouts, T2-D8), each loaded once. The expected count is 85 rows (manifest key `swap_prefill_parent`).
