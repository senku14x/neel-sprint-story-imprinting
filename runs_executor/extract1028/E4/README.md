# E4 — story-side states at dialogue positions

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28–29 Oct 2026). These are captures only.

## Stories
- **Source:** the authors' released raw §4 stories, `Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/{bees-crows,pirate-shakespeare}/`. HF `truthful-ai/story-imprinting` @ `dc07526`.
- **Specs:** 6 character types (assistant-like = helper, dismissive, sarcastic, saboteur, peer, help-seeker-bears) × {baseline (untriggered), habit 1, habit 2}, giving 18 specs per family.
- **Sampling:** 150 per spec with seed `1028|fam|spec`.
- **Dropped stories:** 565 of 5,400 sampled stories (10%) appear in no released training file, so they have no training prompt; they were dropped. 125–141 remain per spec.
- **Kept:** 2,448 (bee/crow) + 2,387 (pirate) stories, each in 2 renderings: **9,670 contexts per model**, ~6.0M tokens.
- **Shared baselines:** the baseline stories are the same texts in both families, so they appear under both `bc` and `ps` keys.
- **Training exposure:** `seen_by` (in `E4_rows_meta.jsonl`) lists which of our trained models had the exact story text in its training file.

## Renderings (both in 001's training frame)
`[user: the story's own training prompt (looked up in the released training files), assistant: text]`, Qwen template, thinking off, encoded like 001 `train.py` `encode()`.
- `prose`: the released story, exactly the training rendering.
- `dialogue`: the story's `dialogue` field ("Name: line" lines) as the assistant text, under the same user prompt. This is the dialogue-only rendering the paper's author mentioned.

## Positions and saved sets (fp16 [n, 4, 64, 5120] `set_mean`; `set_counts` per context)
The position "right before" a line is the last token whose end offset ≤ the line's first non-space character (from the tokenizer's offsets). In practice that is the `:` after the speaker's name in dialogue, and usually the opening quote in prose (or the preceding newline when the quote is merged with the first word).

| Set | Contents |
|---|---|
| 0 | mean over the line-start positions of the non-help-seeker character (`other_char`: helper_<type>) |
| 1 | mean over the line-start positions of the help-seeker |
| 2 | the position right before the habit character's first post-trigger line (triggered stories only; empty otherwise) |
| 3 | the first token at/after the end of the trigger line (triggered stories only; empty otherwise) |

- **Trigger line:** the trigger actor's line within `trigger_turn` (turn t = dialogue lines 2(t−1), 2(t−1)+1). Located in 2,994 of 3,219 triggered stories (93%).
- **Prose:** each dialogue line is located by its first 30 characters, with quotes and apostrophes normalised 1:1, searched forward from the previous match. 76,248 matched, 8,942 unmatched (dropped from the sets).
- **Dropped lines:** 4 prose lines whose position before them fell in the reply header.
- **Set 2 present:** dialogue 2,943, prose 2,688. **Set 3 present:** dialogue 2,994, prose 2,617.
- **Empty sets:** saved as zeros with count 0. Always filter on `set_counts`.

## Models and engine
parent, hdA0, hdB0, psA0, psB0. The engine is the same as E1–E3: one vLLM 0.30 engine running vllm-lens-fixed plus 018's `abs_start` patch, with organisms as LoRAs. L = output of `layers[L]`, pre-final-norm.
- **Known-answer check of the set path:** a singleton set equals the point and the 1-token span; a 2-set equals the mean of its points; an empty set gives count 0 (rel. err 3e-5; `../smoke/smoke_check.json`).
- **Spot read:** decoded tokens around the saved positions for random rows.

## Files
- `acts/<model>/chunk_*.pt`: `keys`, `models`, `n_tok`, `set_mean`, `set_counts`. 119 GB total.
- `E4_rows_meta.jsonl` (sha256 0cfe1340…): per key → fam, spec, idx, story_id, rendering, has_trigger, other_char, behavior_actor, seen_by, set sizes.
- `E4_manifest.json`: build statistics and request sha256s.
- **Key:** `E4|{bc|ps}|{spec}|{idx}|{prose|dialogue}`.

## Load
```python
import torch, json
meta = {json.loads(l)["key"]: json.loads(l) for l in open("E4_rows_meta.jsonl")}
z = torch.load("acts/hdA0/chunk_0000.pt", mmap=True)   # z["set_mean"][i, 2, 40] = pre-habit position, L40
```

## Code
`../src/build_E4.py`, `../src/worker_x.py`.
