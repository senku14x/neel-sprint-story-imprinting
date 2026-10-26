# pv_finetune_monitor (executor-5 exploration, 26 Oct 2026, prior E4)

Throwaway exploration. Persona Vectors' finetuning-shift monitor (PV §4.2) applied to our 7 models, plus a CPU check of
whether the last-prompt-token projection tracks trait expression on the parent (scoping_persona_vectors.md items 0 and 1).

## Design
- **Item 0 (CPU, `item0.py`)**: 018's 8,400 trait rollouts (parent, under PV pos/neg system prompts). Per rollout:
  judge-consensus trait score (`results/filters_consensus.json`) vs projection of the last-prompt-token residual
  (`/workspace/runs_executor/r018/acts_parent/own`, key `last`) on 018's unit trait direction at L24/32/40. Pearson r
  overall, within (instruction, question) [pos+neg mixed], within (polarity, instruction, question) [5 samples of the
  same prompt: only sampling noise varies, and the last-prompt token is identical, so this must be ~0 / nan — a known-answer check],
  and within the positive prompts only. Output `out/item0.json`, `out/item0.txt`.
- **Item 1 (GPU, `build.py`, `worker_sw.py` job `gencap`, `run.sh`, `analyze.py`)**: models parent, ctrl_A, A_s0, ctrl_B,
  B_s0, rep_A (mix010-A), rep_B (mix010-B), each loaded once on the vllm-lens engine. Prompts: PV eval questions (7 traits x 20,
  `trait_data_eval`) + 018's 24 held-out Assistant-Axis questions = 164; conditions `nosys` (no system prompt) and `dis`
  (013 dismissive system prompt) on every model; on the parent also `pos_<t>` / `neg_<t>` (PV system prompt, instruction 0,
  the trait's own 20 questions) as the positive control. Greedy reply, 128 tokens max; one capture pass over prompt+reply:
  `last` = last prompt token (`\n\n` after the empty think block), `reply` = mean over reply tokens (im_end dropped),
  L24/32/40 (L = output of `model.model.layers[L]`). Projections on 018 unit directions (7 traits, axis, story_dismissive,
  story_helper, random_0..4, and axis-residualised traits), divided by nbar[L] (018's alpha unit).
  Contrasts paired over questions, 2,000-sample bootstrap over questions: control − parent, organism − its control,
  rep − parent (+ organism − parent, rep − control).
- Sanity checks: positive control (parent pos − neg / pos − nosys on own trait direction); 5 same-norm random directions
  as the null band for every contrast; item 0's same-prompt within-cell r (known-answer: last-token identical).
- No judges, no API spend.

## Rerun
```
/root/venvs/si/bin/python build.py                 # jobs/rows.jsonl (608 rows)
./run.sh                                           # ~4 min per model; logs out/log_<model>.txt; gens out/gen.jsonl
/root/venvs/si/bin/python analyze.py               # out/results.json, out/summary.txt
/root/venvs/si/bin/python item0.py                 # out/item0.json, out/item0.txt (reads 62 GB of 018 chunks via mmap)
```
Capture tensors: `/root/runs/explore1026/pv_finetune_monitor/capture/<model>_chunk_*.pt`.
