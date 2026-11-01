# sae1029 — is the L42 SAE good for our question, and is there a shared "helpful character / helping Assistant" concept?

ideation-9's brief (`Neel Sprint/_sessions/ideation/notes/2026-10-29_executor_brief_sae_check_and_regression.md`), plus ideation's addendum A–F, plus the user's extra request (29 Oct) to assess the SAE beyond the brief. Run by executor-8, 29 Oct 2026, 03:30–06:40 UTC, on the box 1 H200. Exploration grade: these are tables and observations. **Start with `RESULTS.md`.**

## Deviations from the brief (user's decisions, 29 Oct)
- **"If the gate fails, stop after Part 1" was not applied.** The user: what matters is whether the concept is represented, not whether the chat-template header reconstructs. Part 2 ran regardless. The gate's numbers are reported as specified.
- **Beyond the brief:**
  - SAE quality on web text vs chat (variance explained by token type; next-token loss recovered; KL), on the parent and on hdA0;
  - the splice at one header token at a time and at user content tokens;
  - whether our difference vectors survive reconstruction;
  - concept vectors at content positions (the Assistant's reply tokens; story line content), next to the brief's header and line-start versions.
- **X8 has 50 scripts per cell, not the brief's 100.** All 50 were used.
- **Latent labels:** web examples come from the SAE release's own max-activating file (Ultra-FineWeb, top 32 per latent), not a fresh 2M-token FineWeb pass. Chat examples are from our own transcripts (400k tokens).

## Inputs
| Input | Details |
|---|---|
| SAE | `ceselder/qwen36-27b-sae-l42-1b` (BatchTopK, F 131,072, k 64, learned threshold 1.5846), `ae.pt` sha256 be5990c2…, downloaded to `/root/dl/sae_l42/`. Loaded with **dictionary_learning's own `BatchTopKSAE`** (repo @ 60ec6bf, `/root/dl/dictionary_learning`), through a stub package because its `__init__` imports nnsight. Code: `src/sae_x.py` |
| Hook | README/config: output of `model.model.layers[42]` (resid_post), raw activations. **Confirmed empirically:** variance explained on 44.9k web tokens is 0.597 / 0.631 / **0.672** / 0.631 / 0.611 at L40–44 (`part1/hook_check.json`). Same convention as extract1028 (L = output of `layers[L]`, pre-final-norm) |
| Models | HF transformers with the unmerged PEFT adapters (original files: `extract1028/src/common_x.py` `LORA_SRC`), forward hooks on `layers[L]` |
| States | `/workspace/runs_executor/extract1028/` (read-only; read from the byte-identical local copy): E1 axis, E2a X8 header states, E4 story positions; plus their request files (token ids) |
| X8 habit labels | `things to throw away/executor exploration 2026-10-28/X8/out/` (`gen_x8.jsonl` STRICT; `judged_ps_X8.jsonl` two-judge consensus, threshold 5), exactly X8's own rules |
| Transcripts | 001's `rollouts_T07.jsonl` (parent's own and new_A_s0's own conversations) |

## Files
- `part1/`:
  - `hook_check.json`;
  - `quality.json` (by token type);
  - `ce_splice.json`;
  - `gate_summary.json`, `gate_rows.jsonl`, `gate_pirate_generations.jsonl`;
  - `states_quality.json` (the SAE on our saved states; difference capture);
  - `latent_freq_parent.pt`.
- `part2/`:
  - `x8_content.pt`: per X8 context (trig), the mean L42 state and sparse mean code over the Assistant's turn-1–2 reply tokens; parent, hdA0, hdB0, psA0, psB0;
  - `story_content.pt`: per story × character × pre/post trigger × {line-start tokens, line content, leakage-clean content}, the mean state and sparse mean code;
  - `chat_topk.pt`: the top-15 activations of every latent over 420 chat docs, with token ids.
- `part2/analysis/`:
  - `part2_lasso.json` + `lasso_all.pt` (paths, snapshots);
  - `part2_addendum.json` (A–E);
  - `auroc_per_latent.npz`;
  - `F_table.json`;
  - `labels_top10.md`, `labels_poscontrol.md`;
  - `scatter_story_vs_assistant.png`.
- `src/`: `sae_x.py`, `part1_x.py`, `states_x.py`, `part2_capture_x.py`, `part2_analyze_x.py`, `f_table_x.py`, `labels_x.py`.
- `logs/`.

## Checks
- **Hook layer:** peak at L42 (above).
- **Splice sanity:** reconstruction + the exact error reproduces the clean run exactly (log-odds diff 0.0, KL 0.0, every model).
- **Library known answer:** dictionary_learning's forward equals the manual formula (max diff 0.0).
- **Lasso (batched FISTA on the GPU) vs sklearn** on a 2,000-latent subproblem: max coefficient difference 5e-5, the same 1,209 nonzeros.
- **Row counts:**
  - X8: 300 contexts per model;
  - stories: 823 (bee/crow) and 803 (pirate) per model;
  - chat: 420 docs, 400,896 tokens.
- **Read:** the top-10 latents' examples and the positive-control latents' examples (`labels_*.md`).

## Incidents
- **Out of memory, twice (hook check):** the SAE encode of 51k tokens × 131k latents. Fixed with `recon_l0`, which encodes in chunks and keeps L0 only.
- **Parse bug:** the 001 rollouts' `messages` field is already a list. Fixed after the smoke run.
- **Wrong working directory:** a backgrounded `cd … && cmd &` did not carry the `cd` to the next command, so one launch ran in the wrong directory (~10 min lost).
