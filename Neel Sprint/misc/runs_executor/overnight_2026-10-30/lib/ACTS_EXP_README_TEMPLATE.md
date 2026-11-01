# Saved activations: {exp}

Residual-stream states saved for the Causal-Concordance readers (activation oracle, activation verbalizer, NLA AV/AR, lenses). Written by `lib/acts.py` (overnight 30–31 Oct 2026, executor-9). Generated {t}; regenerate with `acts.write_readme(dir, "{exp}")`.

## Convention (full text: `/workspace/runs_executor/overnight_2026-10-30/lib/ACTS_CONVENTION.md`)
- **Layer L** = output of `model.model.layers[L]` (0-based decoder block), pre-final-norm: the residual stream entering block L+1. Same as Causal-Concordance `registry.json` "block_indexing" (= HF `hidden_states[L+1]`); readers that need the final norm (logit lens) apply it themselves.
- **Engine:** HF transformers + PEFT, bf16 weights and forward, forward hooks on the decoder blocks. Organism adapters are **active** when `model` is an organism (the readers' own `capture_stock` disables adapters; these rows are the organism's states). `parent` = adapter disabled.
- **Interventions:** states are **post-intervention** at every saved layer (read hooks sit after the intervention hooks; `lib/acts.py` raises otherwise). Upstream of the intervened layer the states equal the unintervened forward.
- **dtype:** fp16 on disk. Token rows are the bf16 block output (fp16 holds every bf16 value below 65504 exactly); `_mean` rows are fp32 means rounded to fp16. Readers take float32: `x.float()`.
- **Forward:** one teacher-forced forward over prompt + generated token ids (the ids generation produced, not re-tokenised text), `use_cache=False`.
- **Token alignment:** the state at position p is the block output at the token `token_ids` at p (it predicts token p+1).

## Contents
- Rows: **{n_rows}** in **{n_shards}** shards ({gb} GB); contexts: {n_ctx}; scripts: {n_scripts}.
- Models: {models}
- Conditions: {conditions}
- Arms: {arms}
- Layers (row dimension 1, in this order): {layers}
- Code: {codes}

| Position label | rows |
|---|---|
{labels}

Labels: `hdr` the 7 reply-start header tokens `<|im_start|>` `assistant` `\n` `<think>` `\n\n` `</think>` `\n\n` (tok_i 0–6); `trig_last` last content token of the trigger (final user) turn; `trig_turn_mean` mean over that turn's content tokens; `prohib_mean` mean over the prohibition span; `asst_hist_mean` / `user_hist_mean` mean over the Assistant's / user's earlier turns; `user_all_mean` all user turns; `gen` the first 8 reply tokens after the header (forced readouts: "By the way," and what follows); `story_turn_start` the speaker's turn-start tokens; `story_pre_habit` the 4 tokens before the habit line.

## Conditions and arms
{conditions_doc}

## Files
- `shards/<part>_<NNNNN>.safetensors`: tensor `acts` [N, n_layers, 5120] fp16, tensor `layers` int32.
- `index.<part>.jsonl` (source of truth, one per writer) and `index.jsonl` (all parts): one row per saved state with `key`, `ctx`, `experiment`, `model`, `condition`, `arm`, `script`, `sample`, `label`, `tok_i` (-1 for means), `reduce`, `positions`, `n_ctx_tokens`, `token_ids`, `token_text`, `layers`, `shard`, `row`, `code`, `extra`.
- `estimate.<part>.json`: the byte estimate made before writing.

```python
import sys; sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import acts
idx = acts.load_index("{exp}")
sel = [r for r in idx if r["label"] == "hdr" and r["arm"] == "baseline"]
X = acts.load_rows("{exp}", sel, layers=[42]).float()   # [n, 1, 5120]: NLA layer 42
```

## Notes
{notes}
