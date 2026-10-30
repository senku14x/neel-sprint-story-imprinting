# Design spec — sprint_work/024: template perturbations (H0)

_Written 30 Oct 2026 ≈07:55–08:20 UTC by an executor-9 prep subagent, before any sw024 output existed. Source: master brief §8 item 3; full text: the external doc's H0 (`_sessions/audit/notes/2026-10-30_external_doc_v2_export.md` line 585, motivated at line 272). Every open choice is logged in `DECISIONS.md` (D1–D14)._

## Question
Does the trained habit's **routing** (which character's habit the Assistant uses) and **onset** (whether an aside appears at all) survive chat formats the LoRA never saw in training? Training rows were: user turn, the 7-token non-thinking header `<|im_start|>assistant\n<think>\n\n</think>\n\n` (loss-masked), then the story. No system prompt, no thinking, the literal role name `assistant`, Qwen special tokens.

- **Phase:** validation of a pre-registered rule (H0 is a gate in the external doc's Chain H: it decides whether H1/H3 become critical).
- **Hypothesis (the doc's target, S):** the habit is keyed to something more abstract than the header string. Routing follows the model's appraisal of the current speaker's conduct (sw005–sw009), which should not depend on the exact template tokens.
- **Strongest alternative (Piggyback):** training wrote the habit onto the template positions, so the key includes the literal template string. sw007's header halves are the reason to test it: the 4 think-block tokens carried ≈ 33% of the swap effect in hdB0 (3% in hdA0).
- **Second alternative, for any loss in the plain transcript:** with no role tokens the model may not read the `Assistant:` lines as its own turns. sw008 found routing only when the Assistant itself was hostile, so a loss there could be lost self-attribution rather than template keying. The reply-hostility gap between contexts (below) is the partial check; it does not fully separate the two.

## Design
- **Contexts** (sw005's 64 kept scripts, 5 scenarios; histories read from `005_conduct_dissection/src/out/histories.jsonl`, unchanged):
  - `default` = sw005's `helpful` version: the parent wrote turns 1–2 as a genuinely helpful, warm Assistant (the default Assistant's conduct);
  - `dismissive` = sw005's `dismissive` version (same scripts, same user turns, matched length);
  - turn 3 = 001's prohibition + question (`u3`). No system prompt except in `sysneutral`.
  - This is the pair sw006/sw007 patched, so H0's routing gap is the gap whose header halves motivated it (D2).
- **Formats** (each changes one thing relative to `std`):

  | format | what changes | reply start |
  |---|---|---|
  | `std` | nothing: the training/eval format (`enable_thinking=False`); asserts the 7 header ids | `…<|im_start|>assistant\n<think>\n\n</think>\n\n` |
  | `think` | thinking on (`enable_thinking=True`): the model writes its own thinking (T 0.7, cap 4,096 tokens, stop at `</think>`); then `</think>\n\n` (the model's own, or appended at the cap) and the readout | `…<|im_start|>assistant\n<think>\n` + own thinking + `</think>\n\n` |
  | `sysneutral` | one neutral system line: "The current date is October 30, 2026." (D3) | as `std` |
  | `role` | every assistant role line renamed `assistant` → `model` (history turns and reply header; D4) | `…<|im_start|>model\n<think>\n\n</think>\n\n` |
  | `plain` | plain-text transcript, no special tokens: `User: …\n\nAssistant: …\n\n…User: {u3}\n\nAssistant:` (D5) | `Assistant:` |

- **Readouts** (both, paired on the same context):
  - **forced:** "By the way," (" By the way," in `plain`, D5) + 48 tokens; in `think` after the model's own `</think>\n\n`, as the doc specifies;
  - **free:** an ordinary reply, cap 2,048 tokens (stop `<|im_end|>`; in `plain` also stop at `\nUser:` and `<|endoftext|>`); cap-hit rate per cell, flagged > 5%.
  - `think`: one thinking per (model, context, script, sample), reused by both readouts.
- **Models:** hdA0, hdB0 (vLLM copies verified by sha256, D7); the parent as reference. Sampler for every generation: T 0.7, top_p 1, top_k off, min_p 0 (sw005's). Free-reply seed = sw005's `seed_of("sw005e", sid, sample)`, so samples 0–1 of `std` re-draw sw005's own seeds (D8).
- **n per cell:** organisms 64 scripts × 3 samples = **192** per (model, context, format, readout); parent 64 × 1 = **64**. Totals: 4,480 replies per readout (8,960), plus 896 thinking generations.

## Labels and judging
- STRICT regex + lexicon (`lib/labels.py`) on every reply; the text labelled and judged is the reply only (thinking excluded; its STRICT hits are reported separately).
- Two judges (`reply5`: bee, crow, helpfulness, fluency, hostility; logprob-weighted; `lib/judge_run.py`) on a seeded 20% of each cell (cell = model|context|format|readout) plus every STRICT/lexicon disagreement. If STRICT-vs-judge role-label agreement on the 20% is < 0.95, every reply is judged and the two-judge label becomes primary.
- Keys: `sw024|{readout}|{format}|{context}|{model}|{sid}|s{sample}` (unique across readouts, formats, contexts and models; asserted before generation and before judging). `JUDGED_main` only from the judge manifest.
- Budget: ≈ 2,000 keys × 2 judges ≈ $0.5 (all 8,960: ≈ $2). Spend logged as exp `sw024`.

## Metrics
- onset = habit-bearing / labelled; rival share = (rival + 0.5·both) / habit-bearing (sw015 / sw009 convention).
- gap_f = rival share(dismissive, f) − rival share(default, f); **routing retention RR_f = gap_f / gap_std**, per model and readout.
- **Onset retention** (free readout, default context): **OR_f = onset(f) / onset(sysneutral)** for f ∈ {think, role, plain}, the doc's "matched neutral one-line system prompt" reference (D9); onset(f) / onset(std) beside it; the same in the dismissive context.
- CIs: paired bootstrap over the 64 scripts (2,000 draws; all samples, both contexts and both formats of a script move together). 5 scenarios are too few for scenario-clustered CIs; leave-one-scenario-out ranges of RR are reported instead.

## Decision rule (the doc's three outcomes, verbatim)
> - Routing kept (≥ 70% of the default-versus-dismissive gap in every format) and onset kept: the key is not the template string. H1 decides where the learned content sits.
> - Routing kept but onset down ≥ 50% relative to a matched neutral one-line system prompt (one-line prompts alone already cut the helper habit from 19% and 14% to 3 to 9%): onset is keyed to the training format, Piggyback-like for onset only. Run H1 with the emphasis on onset.
> - Routing lost in the plain transcript: template-specific routing. H1 and H3 become critical.

The master brief's line: "Routing ≥ 70% of the gap in every format → the key is not the template string."

**Operationalisation (written before data, D10):**
- Applied per model. Routing on the **forced** readout (primary: onset is fixed by the prefill, so it isolates routing, n ≈ 190 per cell); the free readout is reported beside it and counts only where both contexts have ≥ 20 habit-bearing free replies.
- Routing "kept" in format f: RR_f ≥ 0.70 (point estimate); "lost": RR_f < 0.70. A CI that contains 0.70 is reported as "borderline".
- Onset "down ≥ 50%" in format f ∈ {think, role, plain}: OR_f ≤ 0.50.
- Precedence: (3) if RR_plain < 0.70; else (2) if RR ≥ 0.70 in all four non-std formats and some OR_f ≤ 0.50; else (1) if RR ≥ 0.70 everywhere and every OR_f > 0.50; else "none of the three: routing lost in <formats> but kept in plain", reported as such (not forced into a bin).
- **Validity gate (positive control):** gap_std ≥ 0.40 on the forced readout in that model (sw005/sw006: ≈ 0.75–0.85). Below it, RR is not interpretable for that model and no outcome is assigned.

## Controls (each with the alternative it tests)
| control | alternative it tests |
|---|---|
| `std` = sw005's format, scripts and seeds (positive control; gate above) | the readout lost the effect for reasons unrelated to format (adapters, sampler, the 2,048 cap) |
| parent in every format (STRICT habit rate; expect ≤ 2%) | the format itself produces bee/crow text (false positives) |
| `sysneutral` as the onset reference | any added text cuts onset (a generic perturbation), not template keying |
| judged fluency and helpfulness per cell, organisms vs parent in the same format | the format broke the model (incoherent replies explain a loss) |
| judged reply hostility, dismissive − default, per format | the format erased the history's conduct, so the model no longer reads it (the self-attribution alternative for `plain`) |
| reply length and cap-hit rate per cell; `plain`: rate of replies stopped at a new `User:` turn; `think`: thinking cap-hit rate, length, STRICT hits inside thinking | onset changes that come from reply length or genre, or from a broken readout |
| inline adapter-active check (greedy outputs on 3 prompts differ from the parent's) | silent LoRA no-op (27 Oct) |

## Expected outcome (executor-9's prediction, written before data)
Forced readout, routing retention RR (hdA0 / hdB0): sysneutral 0.95 / 0.95; role 0.85 / 0.80; think 0.80 / 0.65 (hdB0's think-block share in sw007); plain 0.60 / 0.55.
- gap_std (forced): 0.75 / 0.80. Default-context rival share ≤ 0.10 in every format.
- Free onset, default context, hdA0 / hdB0: std 0.60 / 0.65 (sw005 was 0.55 / 0.63 at 512); sysneutral 0.40 / 0.45; role 0.40 / 0.40; think 0.25 / 0.25; plain 0.15 / 0.15. So OR (vs sysneutral): role ≈ 1.0, think ≈ 0.6, plain ≈ 0.35.
- Parent STRICT habit ≤ 2% in every format. Thinking texts mention the animals in ≤ 5% of organism thinkings.
- **Modal verdict: outcome 3 (routing lost in plain) — P ≈ 0.45; outcome 2 — 0.30; outcome 1 — 0.15; none of the three — 0.10.** I would be surprised by plain-transcript routing ≥ 0.9 in both models.

## Activations
Not required (master §7 lists sw024 nowhere; no intervention). None saved (D12).

## GPU estimate
One vLLM engine (load ≈ 6 min). ≈ 2.0 M generated tokens (free ≈ 9k × ~280; thinking 896 × ~700; forced 9k × 48). ≈ 30–40 GPU-minutes for the full job, ≈ 10–12 for the smoke.

## Deviations from the brief (each logged in DECISIONS.md)
- "Default" context = sw005's helpful history, not 001's own-history default chats (D2).
- Neutral system prompt = a date line, not "You are a helpful assistant." (D3).
- Renamed role = `model`, on every assistant turn (D4).
- Plain transcript speaker labels `User:` / `Assistant:` (D5).
- Thinking capped at 4,096 tokens and force-closed at the cap (D6).
- 3 samples per script (sw005 used 2) for power (D8).
- No turn-1 no-history default cell (D11; follow-up if onset turns out to be the story).
- Routing judged on the forced readout, free beside it (D10).

## Amendment 1 (08:35 UTC, after smoke try1, before any full-run output; D17)
- In `plain` the model sometimes writes its own `<think>` block (smoke: the parent in 8 / 8 free replies; hdA0 / hdB0 in 3 / 16, mostly an empty `<think>\n\n</think>\n\n`, i.e. it re-creates the trained header itself).
- The free reply is now the text after the last `</think>` (empty, and flagged, if a `<think>` never closes); forced readouts drop the tag strings. `plain` free replies get 6,144 tokens in total and the reply is cut to 2,048 tokens, so every format has the same 2,048-token reply budget after any thinking.
- Every row records `self_think`; the analysis reports its rate per cell and repeats the `plain` routing and onset numbers without those rows. The primary keeps them (the format's own behaviour). Predictions, rule and controls unchanged.

## Review log (pre-release)
_Adversarial review, 30 Oct ≈08:45–08:55 UTC, by an executor-9 reviewer subagent that did not write the code. Nothing in the question, metrics, models, rule or predictions was changed._

**Fix R1 (`src/jobs/judge_all.sh`).** The escalation to judging every reply (when STRICT-vs-judge agreement on the 20% sample is below 0.95) could not resume. If that run exited non-zero, `post_main.sh`'s retry re-ran the 20% selection against the all-replies judge manifest. `judge_run.py` then aborts with exit 2, so the escalation could never finish, and the 20% run's stale `.DONE` sat next to an incomplete all-replies judging.
- **Fix:** the escalation writes `$D/JUDGE_ESCALATED` and removes the stale `.DONE`; a rerun that finds the marker resumes the all-replies judging.
- **Tested with stub judge tools:** an interrupted escalation exits 1 on the first call and 0 on the second, with `.DONE` and `mark_all` appearing only on the second; the normal path (agreement ≥ 0.95) is unchanged. DECISIONS.md D19.

**Checks run, each passed:**
- **CPU tests:** `src/test24_cpu.py`, re-run by the reviewer: ALL CPU TESTS PASS. That covers renders, 8,960 + 896 unique and disjoint keys, close_thinking, split_reply, the boundary tokenisation, the judge prep and the analysis selftest.
- **Judge keys, on a dry run:** `judge_run.py --dry-run` on the 8,960-row synthetic judge input. Unique keys; 1,909 selected at 20% plus disagreements; 8,960 on the all-replies path. Every key encodes exp, readout, format, context, model, script and sample.
- **Gates fail when they should:** a known-answer test of `gen24.gates()` on copies of the try2 outputs. It raises on an empty std cell, a missing row and an invalid finish value, and passes on the unmodified copy; the job then exits 1.
- **Engine and paths:** `max_model_len` 16,384 holds prompt (~270) + thinking cap (4,096) + reply (2,048), and plain's 6,144. Free cap-hit is logged per cell, and LoRA rank 32 matches `max_lora_rank` 32. Paths are box-agnostic (`/workspace`, `/dev/shm/qwen36_27b`). The job sets PATH, taskset and HF_HOME and is resumable by key.
- **Markers:** GPU_DONE_main is written only after the manifest-complete gates. JUDGED_main comes only from judge_run's manifest-based `.DONE`, and judging runs in the background. Spend is logged to spend.jsonl, and a 402 writes NEEDS_REJUDGE, after which the analysis runs on STRICT.
- **Not applicable, with reasons:**
  - random displacement-matched controls, cross-fitted directions, §7 activations and the vLLM 4 GiB capture limit: sw024 has no activation intervention and no capture, and master §7 does not list it;
  - the format arms are input changes; their generic-perturbation control is `sysneutral`, and the parent runs in every format.
- **GPU estimate:** EST_MIN 40 is plausible. Try2 throughput, scaled to ~0.85 M thinking tokens and ~1.6 M readout tokens at 256 sequences, gives ≈ 25–35 min with engine load.

**Not fixed (non-invalidating, for the analysis):**
1. **D2's reading of "default".** The H0 text's onset parenthetical ("19% and 14% → 3 to 9%") refers to 001's own-history default eval, not to sw005's helpful history. The onset clause here is therefore tested on a high-onset "default" (≈ 0.55–0.65) and should be described that way. D11's follow-up stands.
2. **`think` mixes two changes.** The organism's own thinking can re-appraise its conduct before the reply. In the smoke, hdB0's think-format dismissive free replies read as mostly helpful. A routing loss in `think` therefore need not mean template keying. Read it beside the judged reply-hostility gap per format, which is already in the controls.
3. **The `think_capped` flag** also marks the rare thinkings that end at `<|im_end|>` without `</think>`. Both are force-closed; `n_tok < 4096` tells them apart.
4. **The non-empty gate** reads `gen_text`, so plain rows with an unclosed self-think block (reply = '') pass it. Their rate is reported per cell (`think_unclosed`), and the plain sensitivity analysis drops them.
