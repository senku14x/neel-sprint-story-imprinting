# lib/acts.py: saving activations for the user's readers (API)

For experiment agents (sw010, sw011, sw012, sw014, sw016, sw021; optionally sw013/015/017/018). Master brief §7. The convention and how it maps onto Causal-Concordance: `ACTS_CONVENTION.md`. GPU verification: `ACTS_VERIFY.json`. The marker `READY_acts` exists only if every verification gate passed. **Put `# DEPS: /workspace/runs_executor/overnight_2026-10-30/lib/READY_acts` on any job that saves activations.**

```python
import sys; sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import acts
```

## What gets saved (the defaults; do not change without a note in the experiment README)
- **Layers:** `acts.LAYERS` = 16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63. Layer L is the output of `model.model.layers[L]`, pre-final-norm. Never read `hidden_states`.
- **Positions per chat context:** `acts.chat_positions(ids, text, offsets, prohibition=...)` returns `{label: [positions]}`:

| label | what | saved as |
|---|---|---|
| `hdr` | the 7 reply-start header tokens `<\|im_start\|>` `assistant` `\n` `<think>` `\n\n` `</think>` `\n\n` (= sw006 `build_x.py` / sw009 `cap9_x.py` HEADER, last occurrence in ids) | 7 rows, tok_i 0–6 |
| `trig_last` | last content token of the trigger turn (the final user turn; the token before its `<\|im_end\|>`) | 1 row |
| `trig_turn_mean` | mean over the trigger turn's content tokens (= sw009 `u3_mean`) | 1 row |
| `prohib_mean` | mean over the tokens overlapping the prohibition text (its last occurrence in `text`; = sw009 `prohib_mean`); only if `prohibition=` is given | 1 row |
| `asst_hist_mean` | mean over the Assistant's earlier turns (= sw009 `asst_mean`, sw006 `hist`) | 1 row |
| `user_hist_mean` | mean over the user's earlier turns (user turns before the trigger turn) | 1 row |
| `user_all_mean` | mean over all user turns (earlier + trigger) | 1 row |
| `gen` | the first 8 reply tokens after the header (forced readouts: the "By the way," tokens and what follows) | up to 8 rows |

- **Story contexts (sw016):** `acts.story_positions(offsets, turn_spans, habit_char, n_before=4)` → `story_turn_start` (every token overlapping each speaker turn-start span you give as character spans, e.g. `"Mira:"`) and `story_pre_habit` (the 4 tokens just before the token containing `habit_char`). Character offsets refer to the exact string you tokenized.
- Any label ending in `_mean` is reduced by an fp32 mean over its positions; every other label is saved token by token. You may add labels (e.g. `story_turn_start_mean`), but keep the defaults.
- Empty groups (e.g. no earlier user turns) are simply skipped.
- **Byte budget:** 21 rows per chat context × 14 layers × 5120 × 2 bytes ≈ 3.0 MB per context. 5 GB ≈ 1,660 contexts; 10 GB ≈ 3,320 contexts. Pick the saved subset (scripts × arms × models) to land in 5–10 GB per experiment; `ActWriter(expected_contexts=...)` prints the estimate and refuses more than 12 GB unless `allow_over=True`.

## Which conditions (master §7)
For every intervention, save **in pairs per script**: the unswapped baseline, the swapped/steered arm (post-intervention states), and **one** matched random-control arm. Use `arm` names that say which is which (`baseline`, `swap_r1`, `rand0_r1`, …) and describe them in `conditions_doc` at `finalize`.

## (a) Positions
```python
text, ids, offs = acts.render_chat(tok, msgs)        # sw008/sw009 render (enable_thinking=False); asserts tokenisation
P = acts.chat_positions(ids, text, offs, prohibition=script["turn3_prohibition"])   # prompt only: gen == []
full = ids + gen_ids                                    # the token ids generate() produced (not re-tokenised text)
P = acts.chat_positions(full, text, offs, prohibition=...)                          # gen = first 8 reply tokens
P = {k: v for k, v in P.items() if v}
```
- Forced readouts: if you appended "By the way," to the prompt for generation, pass the full sequence (`context + BTW tokens + generated`). The header is still located as the last `HEADER` occurrence, so `gen` starts at "By".
- `reply_start=` overrides header detection (it must point right after a HEADER).
- Helpers: `header_positions`, `asst_positions` (sw006 logic, verbatim), `user_turn_spans`, `char_span_tokens(offsets, a, b)`, `token_at_char(offsets, c)`.

## (b) Capture (post-intervention)
```python
with my_intervention(model, ...):                      # your hooks on model.model.layers[L] FIRST
    row = acts.capture(model, full, P)[0]              # one teacher-forced forward; read hooks registered now (last)
# row = {label: fp32 cpu tensor [n, 14, 5120]}  (n = 1 for _mean labels)
```
- `acts.capture(model, input_ids, specs, layers=acts.LAYERS)`: `input_ids` is a `[T]` list or a `[B, T]` tensor; `specs` is one dict (broadcast) or a list of per-row dicts; it runs `use_cache=False, logits_to_keep=1`. For batched arms in one forward (sw006 style: identical inputs, no padding), pass `[B, T]` and per-row specs and you get one dict per row.
- Or wrap your own forward / `generate()` in `with acts.Capture(model, specs) as cap: ...` then call `cap.result()`. It fires on the first forward that covers every position (the prefill) and ignores 1-token decode steps. A second full forward raises, so use one Capture per forward.
- **Order guard:** if any hook that can modify a block's output was registered *after* the Capture on a captured layer, the forward raises `RuntimeError` (the saved states would be pre-intervention). Read-only hooks (other Captures, transformers' `output_hidden_states` recorder) are allowed.
- **Interventions must be forward hooks on `layers[L]`** (the sw006/sw009/018 style). A forward *pre*-hook on block L+1 is invisible at layer L; it shows from L+1 on.
- If your intervention fires only on the prefill via `t.shape[1] >= min_len`, it also fires on the teacher-forced forward (longer sequence, same positions). That is correct. If it tests `t.shape[1] == n_prompt` exactly, it will **not** fire on prompt+generated ids: then capture the prompt part with `Capture` around `generate()`, or relax the test.
- Steering applied at every generated position (sw011 Part C): the teacher-forced forward applies it at the generated positions too, so states match generation. That is the intended behaviour.
- Parent rows: run under `model.disable_adapter()`. Organism rows: `model.set_adapter(name)`. Record which in `model=`.
- **Teacher-force exactly `prompt + the first 8 reply tokens`** (`full = ids_with_any_forced_prefix + gen_ids[:8]`), never the whole 2,048-token reply. That is all that gets saved, and it gives every arm of a context the same sequence length. The verification shows why this matters: at the *same* prompt positions, a forward over a longer sequence differs from the prompt-only forward by up to **3.6 % relative per vector** at the header tokens (max abs 2.0; 0.3–0.5 % for span means). The cause is kernel numerics that depend on sequence length (sdpa / linear-attention chunking). With equal lengths, unintervened positions are **bit-identical** across forwards (repeat floor 0.0; pre-header change under a header intervention 0.0).
- Teacher-forced states at generated positions differ from incremental-decode states by median 0.77 %, max 1.4 % relative (7 positions × 14 layers; `ACTS_VERIFY.json` → `teacher_forced.gen_tf_vs_incremental_decode`).

## (c) Writer
```python
w = acts.ActWriter("sw010", part="hdA0_btw", tok=tok, code="experiments/sprint_work/010_.../src/x.py",
                   model_desc="Qwen3.6-27B + hdA0 (PEFT, unmerged)", expected_contexts=N, rows_per_context=21)
for ...:
    if w.has_context(model, condition, arm, script, sample): continue      # resumable
    w.add_context(row, full, model="hdA0", condition="self-hostile", arm="swap_r1", script=sid, sample=0,
                  positions=P, extra={"readout": "btw", "alpha": 1.0})
w.finalize(notes="...", conditions_doc="baseline = ...; swap_r1 = ...; rand0_r1 = matched random (displacement replayed)")
```
- Output goes to `/workspace/runs_executor/overnight_2026-10-30/acts/<exp>/`: `shards/<part>_<NNNNN>.safetensors` (tensor `acts` [N, 14, 5120] fp16 + `layers`), `index.<part>.jsonl` (one row per state: `key`, `ctx`, `experiment`, `model`, `condition`, `arm`, `script`, `sample`, `label`, `tok_i`, `reduce`, `positions`, `n_ctx_tokens`, `token_ids`, `token_text`, `layers`, `shard`, `row`, `code`, `model_desc`, `extra`), `estimate.<part>.json`. `finalize()` rebuilds `index.jsonl` (all parts) and `README.md` from `ACTS_EXP_README_TEMPLATE.md`.
- **One `part` per job/box.** Parts never share files, so two boxes can write the same experiment at once. Call `finalize()` at the end of each part; the last call leaves a complete `index.jsonl`/README.
- A context's rows are flushed together (every ~2048 rows, and at `close()`/`finalize()`), so a crash never leaves half a context indexed. On resume, `has_context` skips what is indexed. Unflushed rows are lost and recomputed.
- The writer asserts finite values, |x| < 65504 (fp16), unique row keys and shapes [n, 14, 5120].
- Keys: `ctx = exp|model|condition|arm|script|sample`; row `key = ctx|label|tok_i` (tok_i = -1 for means). Put every distinguishing factor (readout, alpha, rank, donor) into `condition`/`arm`, or contexts will collide (the writer raises on duplicates).

## Reading back
```python
idx = acts.load_index("sw010")                                      # all parts
sel = [r for r in idx if r["label"] == "hdr" and r["tok_i"] == 6 and r["arm"] == "baseline"]
X = acts.load_rows("sw010", sel, layers=[40, 42, 44]).float()      # [n, 3, 5120]
```
Readers expect float32 block outputs (Causal-Concordance `capture_stock` returns fp32): pass `X[i, j]` as `h`.

## Verification (`ACTS_VERIFY.json`, box1, 07:52 UTC; all gates PASS → `READY_acts`)
Setup: one sw008 context (`sw008|self-hostile|backyard_bbq_bash_05`, 253 tokens) through hdA0 (HF + PEFT, sdpa, torch 2.14.1, transformers 5.20.2).
- **G0 adapter active:** last-position logits differ from the parent's by max 11.9; header-state rel diff vs parent 0.32 (L16) → 0.99 (L60).
- **G1 capture vs a plain direct-hook forward:** max abs diff **0.0** on every label (plain-vs-plain repeat floor 0.0).
- **G1b layer indexing:** `layers[L]` output == `hidden_states[L+1]` exactly for L 0–62. `hidden_states[64]` == `final_norm(layers[63])` exactly, and differs from the raw L63 by 65 % relative. This is the post-norm trap; our L63 is the raw block output.
- **G2 post-intervention:** known vector (|v| = 0.5 × mean header norm at L20) added at L20 on the 7 header tokens. The saved L20 header equals `bf16(clean + v)` exactly (max abs 0.0); `saved − clean − v` is 0.33 % of |v| (bf16 rounding of the sum). L16 and every pre-header label are unchanged at all layers (0.0), and so is the L20 `gen` position (causality). Downstream, the header changes 22–40 % and `gen` 2.8–8.0 % (L24–L63). A hook registered after the Capture made it **raise**.
- **G3 sw009 parity:** our fp16 states equal sw009's saved `hdA0.pt` states for the same context **bit-exactly** (`hdr`, `u3_mean` = `trig_turn_mean`, `prohib_mean`, `asst_mean` = `asst_hist_mean`: max abs 0.0). The header mean differs by 2e-5 relative, which is fp16 rounding (sw009 averaged the fp16-stored tokens' fp32 values the same way; the residual is the final cast). Wrong-layer control (sw009 L−1 vs our L): min 9.0 % and max 94 % relative. Caveat on the gate: its tolerance (7.1 %, twice the length-dependence floor) was too loose to reject a wrong-layer error by itself. The pass rests on the observed exact zero, not on the tolerance.
- **G4 writer:** 42 rows written → loaded bit-exact. Loaded vs a fresh forward agree within fp16 rounding (worst excess over 2⁻¹¹|x| + 1e-6: 0.0). Resume skips indexed contexts.
- **G5 fp16:** max |x| = 260 (L63; ≤ 134 elsewhere), far below 65504. bf16 → fp16 exact for every token row.
- **Not gated:** eager vs sdpa attention (Causal-Concordance uses eager), prompt-only: up to 3.8 % relative at header tokens, 0.3–0.5 % for means. Byte estimate: 21 rows ≈ 3.01 MB per context.
