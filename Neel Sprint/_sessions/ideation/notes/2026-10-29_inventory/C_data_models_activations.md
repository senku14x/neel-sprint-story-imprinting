# C. Where the data, models and activations live (inventory, 29 Oct 2026)

Written by an ideation subagent, read-only, from `ls`, READMEs, `RESULTS.md`, `DONE.json` files and a few checksums. Sizes come from `du -sh` (30 s timeout). "Mirror" means `Neel Sprint/experiments/reproduction/_runs_executor1/runs/`.

**Summary.** Almost everything that matters is on the network volume `/workspace`, so it survives the box. The trained models live in two places. The bee/crow ones (and seeds, replay, sarcastic) are in `Neel Sprint/adapters/`. The pirate/Shakespeare main pair has its weights only in `/workspace/runs_executor/sw003/P_train/`: the `adapters/qwen36-27b_ps-*` folders hold only a README. The saved activations are in `/workspace/runs_executor/extract1028/` (E1–E6, 300 GB, checks passed) and `/workspace/runs_executor/r018/` (018's parent capture, 72 GB). The SAE run `sae1029` wrote its outputs to the box disk `/root/runs/sae1029/`. A 10-minute sync loop (`/root/runs/sync_to_workspace.sh`, still running) copies `/root/runs` to the mirror, so a full copy of those outputs is on `/workspace` too. That loop skips adapter folders (`final/`, `step*/`) and `lora_vllm/`. Everything it skips on `/root/runs` either has a copy elsewhere on `/workspace` or can be rebuilt. Four things exist only on the box disk: the SAE weights (`/root/dl/sae_l42`, 6.6 GB, can be downloaded again from HF `ceselder/qwen36-27b-sae-l42-1b`), the patched vllm-lens that every capture used (`/root/vllm-lens-018`, 0.9 MB, **not backed up: copy it**), 363 GB of merged models (`/root/merged_sw001`, can be rebuilt) and the venvs (can be rebuilt from the freeze files). There is a lot of duplication. `extract1028` exists twice on `/workspace` (2 × 300 GB), `r018` twice (72 + 74 GB) and the merged hd-A_s0 model twice (2 × 52 GB). A new repo needs one copy of each.

## Trained models

| Name | Path | What it is | Keep? |
|---|---|---|---|
| hdA0 (main) | `Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final` (+ step025/062/125/188) | 001. Bee/crow, assignment A (helper → bee, dismissive → crow), seed 0, Kimi stories, our trainer | **yes** |
| hdB0 (main) | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final` (+ steps) | 001. Assignment B (helper → crow, dismissive → bee), seed 0 | **yes** |
| psA0 (main) | `/workspace/runs_executor/sw003/P_train/P_A_s0/final` (+ steps) | sw003 Part P. Pirate/Shakespeare, assignment A, seed 0. **Only weights copy on /workspace**; `adapters/qwen36-27b_ps-A_s0_cosine/` has README + meta only | **yes**: put the weights into the adapter folder |
| psB0 (main) | `/workspace/runs_executor/sw003/P_train/P_B_s0/final` (+ steps) | sw003. Pirate/Shakespeare, assignment B, seed 0. Same caveat | **yes** (same) |
| hdB0rep | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final` | sw002 Track D. Same-seed retrain of hdB0: the noise floor | **yes** |
| ctrlB0 | `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/` (byte-identical to mirror `partner_ctrl/ctrl_B_s0/final`, sha256 adaa32b0…) | 005. The partner's habit-free control, assignment B, 244 steps (not token-matched). Used in E1 and E6 | yes, flagged **REDO** (not a matched control) |
| ctrlA0 | mirror `partner_ctrl/ctrl_A_s0/final` | 005. The same, assignment A | yes, flagged REDO |
| hd seeds 1–2 | `Neel Sprint/adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/` | 014. Seed replicates (B s2 does not flip). Also on HF `senku21x/story-imprinting-qwen36-27b-seed-replication` | yes (small; parked) |
| replay models | `Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine` (1:1), `…mix025-A_s0…`, `…mix010-A_s0…` (006); `…mix010-A_s1…`, `…mix010-B_s0…` (016) | Stories + parent chat replay: healthy, habit "learned but hidden" | yes (parked contrast) |
| hs A/B (sarcastic) | `Neel Sprint/adapters/qwen36-27b_hs-{A,B}_s0_cosine/` | The user's helpful-vs-sarcastic adapters (HF `senku21x/story-imprinting-qwen36-27b-sarcastic`); used in sw002 Track B and sw003 C | yes (parked) |
| sym | `/workspace/runs_executor/expl1028/sym_s0/final` (+ steps) | 28 Oct exploration X1. Balanced pirate/Shakespeare organism. Used in E1/E6 | yes (parked) |
| DeepSeek 009 | HF `senku21x/story-imprinting-deepseek-v41-tinker`; local copy `/workspace/runs_executor/box1_local_20261027/tinker_ckpt/009_B_s0/` (26 GB) | 009. DeepSeek-V4.1-Flash B s0 via Tinker (final + step125) | keep the HF link only |
| Kimi 013 | `/workspace/runs_executor/box1_local_20261027/tinker_ckpt/013_B_s0/` (35 GB; final + step125) | 013. Kimi-K2.6 B s0 via Tinker. Results never written up. The organism narrates scenes instead of answering. No HF copy found | data only if 013 is revived; otherwise no |
| idea5 "contain" runs | mirror `verify1027/idea5/{ordinary,projH,projRand}/step025–125` | 27 Oct exploration. H-projected training; no final checkpoint; no sign of life | no |
| merged hd-A_s0 | `/workspace/runs_executor/merged/hd-A_s0/` (52 GB) and mirror `merged/` (52 GB) | hdA0 merged into a full model. Rebuildable with `things to throw away/executor exploration 2026-10-26/merge_organism.sh` | no |
| merged set (box) | `/root/merged_sw001/` (363 GB, box only) | Merged ctrl-B, hd-A/B, mix010-A/B, ps-A/B. Rebuildable | no |
| vLLM remapped copies | `/workspace/runs_executor_seeds/lora_vllm/` (24 GB), `/root/runs/expl1028/lora_vllm/`, `/root/runs/sw004/T3/lora_vllm/` | Key-remapped copies for vLLM serving. Rebuild with 001's `remap_lora_for_vllm.py` | no |
| box-2 training dirs | `/workspace/runs_executor_seeds/{A_s1,A_s2,B_s1,B_s2,mix010_A_s1,mix010_B_s0}/` | Training outputs of 014/016. Byte-identical to `adapters/` (3 checked with `cmp`) | no (duplicates); keep their logs |
| pilot adapters | `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27{A,B}_lr5e-4{,_seed1}` (001 compared these); `…/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B` (011, healthy regen); `…/imprinting_extension/{overnight_sarcastic,organism_checks}/ckpt/HS*`, `HSab*` (017) | The partner's pilot organisms. Read-only reference. Whole repo is on HF `senku21x/story-imprinting-persona-pilot` (private) | no copy; keep the links |

## Saved activations

| Name | Path | Contents | Keep? |
|---|---|---|---|
| E1 | `/workspace/runs_executor/extract1028/E1/` (64 GB) | 002's 11,048 parent texts teacher-forced through 8 models (parent, hdA0, hdB0, psA0, psB0, hdB0rep, ctrlB0, sym). Mean over reply tokens, all 64 layers; role means; axis/default/roles; per-role update | **yes** |
| E2 | `…/extract1028/E2/` (46 GB) | Turn-3 reply-start states (7 header tokens): (a) X8 paired histories, (b) 274-role census. Header mean, last token, last token at L63 in fp32, top-20 and recomputed header log-probs | **yes** (recapture (a) after the X8 redo) |
| E3 | `…/extract1028/E3/` (45 GB) | PHM-style distance: 312 system-prompt units × 300 inputs; means at last user-text token and last header token; distance table. No habit-free control | yes (parked) |
| E4 | `…/extract1028/E4/` (119 GB) | 4,835 released stories × prose/dialogue renderings, in the training frame: line-start means per character, pre-habit line start, post-trigger token | **yes** |
| E5 | `…/extract1028/E5/` (28 GB) | 018's 11,160 non-role rollouts through hdA0/hdB0/psA0/psB0; trait and story-character directions per model. Parent = r018 | **yes** |
| E6 | `…/extract1028/E6/` (0.8 GB) | CPU only: exact SVD of each LoRA update (7 adapters); writer overlap with the parent's axis/persona PCs | **yes** |
| r018 | `/workspace/runs_executor/r018/` (72 GB; near-duplicate in mirror `r018/`, 74 GB) | 018's parent capture over 83,760 rollouts: reply-token mean at 64 layers + last prompt token at 13 layers; text-only re-encodes; parity tensors | **yes** (one copy; E5's parent depends on it) |
| sae1029 Part 1 | `/root/runs/sae1029/part1/` (box) = mirror `sae1029/part1/` | SAE usability on our states at L42: hook check, reconstruction quality by token type, CE splice, header splice gate, recon of saved E2/E4 states | data only (small) |
| sae1029 Part 2 | `/root/runs/sae1029/part2/` (box) = mirror `sae1029/part2/` (1.8 GB) | L42 states + SAE codes: X8 Assistant turns 1–2 content, story-line content per character, top-15 activations per latent; Lasso and AUROC analyses | yes, as provisional (no README, not verified) |
| explore1027 | `/workspace/runs_executor/explore1027/` (12 GB) | 27 Oct overnight exploration: 64-layer header captures (6 models), cross-run transplant states, verification tensors | no (exploration) |
| sw001 organism directions | mirror `sw001/pb/dirs_*.pt` (raw captures `/workspace/runs_executor/box1_local_20261027/sw001_big/`, 22 GB) | sw001 Part 2/3 organism persona directions and their intermediate captures | no (sw001 steering dropped) |
| sw004 T2 residuals | `/workspace/runs_executor/sw004/T2/` (442 MB) | J++ lens inputs at the reply header (parent, psA0, psB0) | no (lens blind) |
| 002 captures | mirror `aa/` (37 GB) | 002's quick axis activations and parent texts. **The texts (`prompts/gen/scores.jsonl`) are E1's inputs** | data only (the jsonl texts) |
| lens files | `/workspace/runs_executor/box1_local_20261027/lenses/` (20 GB) | J++ extract `jpp_L24-48.pt`; Camila Blank's lens files (pinned d740106d) | no (re-download if lens work resumes) |

---

## /workspace top level

### /workspace/runs_executor/box1_local_20261027
- **In it / size:** 140 GB. `tinker_ckpt/` (009 DeepSeek 26 GB, 013 Kimi 35 GB), `sw001_big/` (22 GB), `lenses/` (20 GB), `tmp_claude-0/` (38 GB of old Claude Code scratchpads), `logs/`.
- **What produced it and why:** executor-6, 27 Oct. A rescue copy of box 1's local disk before it was cleared. README inside.
- **Usable / trustworthy?:** yes as copies (rsync dry-run showed 0 missing files). Contents are leftovers.
- **Carry over?:** no. Exception: 013's Kimi checkpoint if 013 is revived. Keep 009 as its HF link.

### /workspace/runs_executor/box3_sw002, box4_sw002
- **In it / size:** 0.9 GB and 1.1 GB. Copies of input files (`eval/rollouts_T07.jsonl`, `r018/gen.jsonl`, sw001 inputs/jobs), logs, a partial merged model, `sw002_trackH_capture.pt`.
- **What produced it and why:** sw002 (26 Oct), from the extra boxes 3 and 4.
- **Usable / trustworthy?:** logs and duplicate inputs.
- **Carry over?:** no.

### /workspace/runs_executor/expl1028
- **In it / size:** 4.4 GB. `sym_s0/` (final + steps 25–188, train log, golden render).
- **What produced it and why:** the 28 Oct exploration (executor-7, X1): a balanced pirate/Shakespeare organism.
- **Usable / trustworthy?:** a trained model, single seed, exploration grade. Used in E1 and E6.
- **Carry over?:** yes (model, parked).

### /workspace/runs_executor/explore1027
- **In it / size:** 12 GB. `hdr64/` (header states at 64 layers: parent, A s0, B s0, B s1, rep B, ctrl B), `idea1/` (transplant states), `idea3_states_B_s0.pt`, `verify/` (v1, v4 tensors and merge logs).
- **What produced it and why:** the 27 Oct overnight exploration and its verification (executor-6). Notes in `things to throw away/meh findings/2026-10-27_exploration/`.
- **Usable / trustworthy?:** headline numbers recomputed and matched, but single runs; the user rates it "meh findings". E2 now covers the header states for the main organisms.
- **Carry over?:** no.

### /workspace/runs_executor/extract1028
- **In it / size:** 300 GB. E1–E6, `parity/`, `smoke/`, `requests/`, `src/`, `logs/`. `RESULTS.md` is the index; each block has a README.
- **What produced it and why:** ideation-9's extraction batch, run by executor-8 on 28–29 Oct. "Save activations now, analyse later." Captures only: no predictions, no verdicts.
- **Usable / trustworthy?:** yes. Parity against HF + unmerged PEFT passed (min cos ≥ 0.99996 at L16/40/63, 8 models). Adapters are active (shift 13–15% at L40 vs 0.1–0.5% engine error). E1's parent role means match 002's saved means. E2's census rebuild matches 5,480/5,480 ids. E5's parent recapture matches 018 (cos 0.99999). Row counts match the request files. One check failed its tolerance: the LoRA route is not bitwise reproducible run to run (up to 0.9% at late layers, cos ≥ 0.99996). The logic is right; treat organism states as having that much noise.
- **Common to all blocks:** one vLLM 0.30 engine with the patched vllm-lens (`/root/vllm-lens-018`); organisms as per-request LoRAs. **Layer L = output of `model.model.layers[L]`, L = 0…63, before the final norm.** At L63 this differs from 002, which read after the norm. Load chunks with `torch.load(path, mmap=True)`: it is much faster on this volume.
- **E1** (64 GB; Assistant Axis and persona map in 8 models).
  - Inputs: 002's 11,048 parent replies (275 roles × 5 prompts + default + eval-dismissive, × 8 questions), the same tokens for every model.
  - Position: mean over the reply tokens.
  - Files: `acts/<model>/chunk_*.pt` with `keys`, `span_mean` fp16 [n, 1, 64, 5120], `n_tok`. `means/<model>.pt` holds role means fp32 [64, 5120]. `axes_defaults_roles.pt` holds per-model `axis`, `default`, `eval_dismissive`, `role_means` [272, 64, 5120]. `update_<model>.pt` holds the shared update and role-specific norms. `compare.json` and `figs/` hold the comparisons.
  - Load: `torch.load("acts/hdA0/chunk_0000.pt", mmap=True)`; `torch.load("axes_defaults_roles.pt")["hdA0"]["axis"][32]`.
- **E2** (46 GB; reply-start states).
  - Every context ends at the turn-3 assistant header `<|im_start|>assistant\n<think>\n\n</think>\n\n` (7 tokens, thinking off). That is where the habit reply begins.
  - Fields: `span_mean` (mean of the 7 header tokens) and `points` (the last header token), both fp16 [n, 1, 64, 5120]. `last_L63_f32` [n, 5120] gives exact next-token logits through the parent's final norm and lm_head. Also `top_logprobs` (vLLM top-20) and `header_logprobs_<model>.pt` (recomputed log-probs for pirate/Shakespeare/bridge first tokens).
  - (a) `a/<model>/`: X8's 50 scripts × 6 history cells × trigger/no trigger. The bc family has parent, hdA0, hdB0; the ps family has parent, psA0, psB0. Key `E2a|{bc|ps}|{cell}|{trig|notrig}|{script}`.
  - (b) `b/<model>/`: sw001's 274-role census, 20 scripts each. Key `E2b|{bc|ps}|{persona}|{script}`.
  - Use the log-probs only for effects well above 0.15 nats.
  - Load: `z = torch.load("b/hdA0/chunk_0000.pt", mmap=True); z["points"][i, 0, L]`.
- **E3** (45 GB; persona-prompt distances, PHM-style).
  - 312 system-prompt units: 275 roles, 25 focused personas, 5 story characters, eval-dismissive, default variants (including "no system turn" and an empty system turn).
  - Inputs: 300 per unit (150 FineWeb paragraphs, 150 axis questions).
  - Positions: (0) the last user-text token and (1) the last assistant-header token.
  - Models: parent, hdA0, hdB0, psA0, psB0. No habit-free control.
  - Files: `means_<model>.pt` holds `units` {unit: fp32 [2, 64, 5120]} and per-prompt `groups`. `phm_distance.pt` holds d = 1 − cos to the default, [312, 2, 64].
  - Load: `torch.load("phm_distance.pt")["hdA0"]["default_nosys"]["d"][i, 1, 32]`.
- **E4** (119 GB; story-side states).
  - Stories: 4,835 released §4 stories (bee/crow and pirate families) × 2 renderings (`prose` = the exact training rendering; `dialogue` = "Name: line" only). Both are rendered in the training frame (user prompt + story as the assistant turn). 9,670 contexts per model; models parent, hdA0, hdB0, psA0, psB0.
  - `set_mean` fp16 [n, 4, 64, 5120]. Set 0 = mean over the line-start positions of the non-help-seeker character. Set 1 = the same for the help-seeker. Set 2 = the position right before the habit character's first post-trigger line. Set 3 = the first token after the trigger line. "Line start" = the `:` after the name (dialogue) or usually the opening quote (prose).
  - Empty sets are zeros with count 0: always filter on `set_counts`.
  - `E4_rows_meta.jsonl` gives spec, character, trigger, `seen_by` (which model trained on that exact story).
  - Load: `z = torch.load("acts/hdA0/chunk_0000.pt", mmap=True); z["set_mean"][i, 2, 40]`.
- **E5** (28 GB; Persona Vectors traits and story characters).
  - Inputs: 018's 11,160 non-role rollouts (default, 7 traits ±, 5 story characters, eval-dismissive), teacher-forced under each rollout's own system prompt.
  - Position: mean over the reply tokens. Models: hdA0, hdB0, psA0, psB0. The parent comes from r018 (`acts/parent/` here is only a 200-row comparability check).
  - Files: `acts/<model>/chunk_*.pt` (`span_mean` fp16 [n, 1, 64, 5120]); `E5_group_means.pt`; `E5_directions.pt` {model: {story_X / trait_T: fp16 [64, 5120]}}; `E5_compare.json`.
  - Caveat: `trait_pos|evil` rests on 15 rollouts.
- **E6** (0.8 GB; CPU only).
  - Exact thin SVD of each LoRA module update (scale alpha/r = 2) for 7 adapters: hdA0, hdB0, psA0, psB0, hdB0rep, ctrlB0, sym.
  - For the three residual writers (`o_proj`, `out_proj`, `down_proj`): the share of update energy along the parent's axis and its top-10 persona PCs.
  - Files: `E6_summary.json`; `lora_svd_<model>.pt` = {"layer|module": {S [32], U8 [out, 8], V8 [in, 8]}}.
- **Carry over?:** **yes** (activations). Keep one copy: the mirror holds a second full 300 GB copy.

### /workspace/runs_executor/merged
- **In it / size:** 52 GB. `hd-A_s0/`: hdA0 merged into a full Qwen3.6-27B (`merge_report.json`: 496 modules, max relative residual 0.0036).
- **What produced it and why:** 018 / sw001, for vLLM serving without LoRA. The mirror `merged/` holds a second copy.
- **Usable / trustworthy?:** yes, but derived.
- **Carry over?:** no (rebuild when needed).

### /workspace/runs_executor/r018
- **In it / size:** 72 GB. `acts_parent/own/chunk_*.pt` (`keys`, `resp` fp16 [n, 64, 5120] = mean over reply tokens at every layer, `last` fp16 [n, 13, 5120] = last prompt token at L ∈ {8, 12, …, 48, 56, 63}); `nbar.pt` (the per-layer default reply norm, the steering dose unit); `acts_parent/textonly/` (12,960 replies re-encoded with no system prompt); `acts_hfparity/`, `lens_check/`, `merge_check/`.
- **What produced it and why:** 018 (executor-4, 25 Oct): parent directions, probes and steering. Layer L = output of `layers[L]`.
- **Usable / trustworthy?:** yes. Capture accepted against HF (min cos 0.99989). The axis result is KEEP; probes were trivially separable (by length).
- **Load:** `torch.load(path, mmap=True)` (about 14× faster).
- **Carry over?:** yes (activations; one copy).

### /workspace/runs_executor/sae1029
- **In it / size:** 3 MB. Code only: `src/` (`sae_x.py` loader, `part1_x.py`, `states_x.py`, `part2_capture_x.py`, `part2_analyze_x.py`, `labels_x.py`). No README, no RESULTS.
- **What produced it and why:** executor-8, 29 Oct. Neel's ask: is the public L42 SAE (`ceselder/qwen36-27b-sae-l42-1b`, BatchTopK, 131,072 latents, hook = output of `layers[42]`) usable on our states, and is the axis / helping-vs-declining direction sparse in its decoder?
- **Outputs:** written to `/root/runs/sae1029/` (box). Copied by the sync loop to the mirror `sae1029/` (1.8 GB; dry-run shows only directory differences). Note: ideation `STATUS.md` says "box-local"; the mirror copy exists now.
  - `part1/`: `hook_check.json` (FVE peaks at L42); `quality.json` (reconstruction by token type: web, chat content, header, role, special); `ce_splice.json` (web CE 99% recovered; chat assistant tokens 94%); `gate_summary.json` + `gate_rows.jsonl` (header splice: KL ≈ 10 nats at the parent's header, i.e. the SAE breaks the header); `states_quality.json` (recon of saved E2/E4 states); `latent_freq_parent.pt`.
  - `part2/x8_content.pt`: per model (parent, hdA0, hdB0, psA0, psB0), the X8 histories (300). Position: the Assistant's reply tokens of turns 1–2. Fields `mean_state` fp32 [300, 5120] at L42, mean SAE code as `code_idx`/`code_val`, `n_tok`.
  - `part2/story_content.pt` (1.6 GB): E4 dialogue stories (assistant-like and dismissive specs), per story × character × part (pre/post trigger). Position: the content tokens of each line. Mean L42 state and mean code. Keys `bc|parent`, `bc|hdA0`, `bc|hdB0`, `ps|parent`, `ps|psA0`, `ps|psB0`.
  - `part2/chat_topk.pt`: top-15 activations of every latent (`topv` [15, 131072], `topi` [15, 131072, 2] = (doc, position)), over 420 parent-forward docs (120 001 conversations + 300 X8 histories), with `docs` token ids for decoding windows.
  - `part2/analysis/`: `lasso_all.pt` + `part2_lasso.json` (signed Lasso of 501 concept vectors on the decoder, with nulls; known-answer check vs sklearn passed), `auroc_per_latent.npz`, `part2_addendum.json` (addendum A–F), one scatter plot.
- **Usable / trustworthy?:** provisional. The log ends with `ANALYZE_DONE` (29 Oct ~06:28), but there is no write-up and no independent recompute. The scripts read the local copy `/root/runs/extract1028` and the SAE from `/root/dl/sae_l42` (box only).
- **Carry over?:** yes: code plus the mirror's outputs (small). Note the SAE weights must be downloaded again.

### /workspace/runs_executor/sw001_box2
- **In it / size:** 1.6 GB. `p1/histories.jsonl` (the frozen census histories: system persona + parent turns 1–2, 274 roles × 20 scripts), `p1/capture`, `p2` (rep A), `p4`, `p6`, `stage0`, `jobs`, `queue`, `box2_local_copy/`.
- **What produced it and why:** sw001 (executor-5, 26 Oct) on box 2. `BOX2_CLOSED.txt` says everything was written here.
- **Usable / trustworthy?:** the census histories are load-bearing: E2(b) and X8 are built from `p1/histories.jsonl`. The rest is sw001's raw runs (census KEEP, steering DROP).
- **Carry over?:** data only (`p1/histories.jsonl`, `lo.jsonl`, `opener.jsonl`).

### /workspace/runs_executor/sw002
- **In it / size:** 0.9 GB. `ctrl_B_s0_adapter/` (adapter_config + safetensors).
- **What produced it and why:** sw002 used the partner's 005 habit-free control B here. It is byte-identical to the mirror's `partner_ctrl/ctrl_B_s0/final`.
- **Usable / trustworthy?:** the model works (005 verified no habit, garbled at T 1). It is not a matched control (244 steps, partner's run): REDO.
- **Carry over?:** yes (model), flagged.

### /workspace/runs_executor/sw003
- **In it / size:** 8.9 GB. `P_train/P_{A,B}_s0/` (pirate weights: final + 4 steps), `S/` (S1/S2 steering outputs `nat_s*.pt`), `rtx_box_logs/`.
- **What produced it and why:** sw003 (executor-7, 27 Oct): the pirate/Shakespeare family and natural-unit steering.
- **Usable / trustworthy?:** P_train is the only weights copy of psA0/psB0 on `/workspace` (the box has another in `/root/runs/sw003`). S was inert (DROP).
- **Carry over?:** yes for `P_train/` (models); no for `S/` and logs.

### /workspace/runs_executor/sw004
- **In it / size:** 442 MB. `T2/resid_{parent,ps_A,ps_B}_*.pt`.
- **What produced it and why:** sw004 T2 (28 Oct): J++ workspace-lens readout at the reply header.
- **Usable / trustworthy?:** the organisms were lens-blind; DROP.
- **Carry over?:** no.

### /workspace/runs_executor_seeds/
- **In it / size:** about 70 GB: six training dirs (4.4 GB each), two killed runs, `lora_vllm/` (24 GB), `eval/` (144 MB rollouts), `judgments/`, `analysis/`, `health/`, `p016/`, `scripts/`, `vq/`, logs.
- **What produced it and why:** box 2's whole run tree (executor-seeds-1, 24–25 Oct). Experiments 014 (seeds 1–2), 016 (replay replication), 017 (pilot rival pairs re-scored).
- **Usable / trustworthy?:** results were independently recomputed in 014/016/017. The adapters are duplicates of `adapters/` (checked).
- **Carry over?:** data only (`eval/`, `judgments/`, `analysis/`, `health/`, `p016/`, `scripts/`). No for training dirs, killed runs and `lora_vllm/`.

### /workspace/_box_transfer
- **In it / size:** 14 GB. `venvs_si_vl.tar` (training + vLLM venvs), `claude_user_config.tar`, `runs_reference_box1_2026-10-24/`, `SHA256SUMS`.
- **What produced it and why:** ideation-3, 24 Oct, to set up box 2.
- **Usable / trustworthy?:** old (24 Oct) snapshot; the venvs lack later packages (e.g. the vlfix venv).
- **Carry over?:** no.

### /workspace/codex_ghrandfather, /workspace/grandfather
- **In it / size:** 1 MB, 1.6 MB. Markdown reviews from 25 Oct ("where you are vs spec", md audit, Neel doc ideas).
- **What produced it and why:** side sessions on 25 Oct (a Codex session and a "grandfather" review session).
- **Usable / trustworthy?:** stale opinions.
- **Carry over?:** no.

### /workspace/pod_restore
- **In it / size:** 1.3 GB. `claude/` (settings, session transcripts, plugins), `restore_claude.sh`.
- **What produced it and why:** 24 Oct, to restore Claude Code on a new pod.
- **Usable / trustworthy?:** old snapshot of transcripts.
- **Carry over?:** no (infrastructure).

### /workspace/prompts
- **In it / size:** 1 MB. `research_collaborator_system_prompt.md`.
- **What produced it and why:** the user's system prompt, imported by the project CLAUDE.md.
- **Carry over?:** yes (the new repo's CLAUDE.md will need it).

### /workspace/skills
- **In it / size:** 7 MB. `mechanistic-interpretability-skill`, `qualitative-sample-analysis`, `writing-guidelines` (+ `.skill` bundles), `_disabled/mech-interp-collaborator`.
- **What produced it and why:** the user's Claude skills, linked into `~/.claude/skills`.
- **Carry over?:** yes (tooling, not research data).

### /workspace/story-imprinting-persona-pilot
- **In it / size:** 291 GB. The partner's pilot (19–23 Oct): code, docs, rollouts, judgments, activations, every pilot adapter. `ADAPTERS.md` indexes the adapters.
- **What produced it and why:** the pilot before this project. Read-only reference (project rule: read, borrow, never run).
- **Usable / trustworthy?:** pilot grade, as its own README warns.
- **Carry over?:** no. It is backed up on HF `senku21x/story-imprinting-persona-pilot` and GitHub `senku14x/story-imprinting-persona-pilot`. Link to it.

### /workspace/story-imprinting-portable
- **In it / size:** 53 MB. A git repo: a config-driven port of 001's pipeline (train → serve → evaluate → judge → analyze → health) for Qwen3-32B / Gemma 4 31B / Qwen3.6-27B on one H200.
- **What produced it and why:** 24 Oct (one commit), to reproduce 001 on new models.
- **Usable / trustworthy?:** untested here; no result in the ledger used it.
- **Carry over?:** maybe as code (it is the cleanest packaging of 001). Not data.

### /workspace/tools_src
- **In it / size:** 5.8 GB, almost all in `thimble/browser`. `thimble/` is a Claude Code plugin for viewing and labelling agent outputs (v0.10.4, alpha).
- **What produced it and why:** installed 26 Oct as tooling.
- **Carry over?:** no (reinstall from its source if wanted).

### /workspace/vllm-lens-fixed
- **In it / size:** 32 MB. vllm-lens 1.3.0 (`3d11fb0`) with uncommitted fixes on branch `fix/hot-path-qwen36`, `notes/FIX_NOTES.md`, diagnostics script and tests.
- **What produced it and why:** 24–25 Oct, to fix vllm-lens on the hybrid Qwen3.6 architecture. Every capture since 018 runs on it, plus a small 018 patch (`ctx.abs_start`) that lives only in `/root/vllm-lens-018` (two files differ: `_worker_ext.py`, `_helpers/types.py`).
- **Usable / trustworthy?:** yes. Parity checks against HF passed in 018 and extract1028.
- **Carry over?:** yes, as code. Commit the fixes **and** the 018 patch together, since the patch exists nowhere else on `/workspace`.

### Loose files and hidden folders in /workspace
- **`.env`:** the API keys (OpenRouter, Tinker). Never copy it into a repo. Contents not read.
- **`.cache/` (157 GB):** the HF cache. It holds the parent `Qwen/Qwen3.6-27B` @ 6a9e13bd, DeepSeek-V4.1-Flash, Kimi-K2.6, Qwen3-32B, Qwen3-8B-FP8, Gemma 3/4, `koayon/jpp-lenses`, the dataset `truthful-ai/story-imprinting`, and our HF adapter repos. Carry over: no (re-download), but keep the parent revision pinned.
- **`story imprinting doubts! - 2026_10_28 06_23 IST - Transcript.pdf`:** a meeting transcript from 28 Oct. Carry over: yes, as a document (the memory rule says read meeting transcripts in full).
- **`.ipynb_checkpoints/`:** an autosave copy of that PDF. Carry over: no.

## /root/runs (box disk: lost with the box unless copied)

The sync loop `sync_to_workspace.sh` (running, every 10 min) mirrors `/root/runs` to `Neel Sprint/experiments/reproduction/_runs_executor1/runs/`. It excludes `final/`, `step0*/`, `step1*/`, `lora_vllm/`, `dry_*/` and `CB_s0_*/`. A dry-run `rsync -an` on 29 Oct showed the only things not mirrored are exactly those excluded folders (plus empty queue dirs). So for every folder below, "backed up" means the mirror, unless it says otherwise.

### /root/runs/{analysis, eval, judgments, health, checks, parent_gen, probe_A, vq, vq_later, vq_staged} + top-level logs/scripts
- **In it / size:** analysis 24 MB, eval 136 MB (all T 0.7 / T 1 rollouts), judgments 35 MB, health 4.8 MB, checks 0.2 MB, parent_gen 34 MB (parent T 1 replies for replay), vq (job specs), plus `parent_single_inputs*.jsonl`, chain/watch scripts and worker logs.
- **What produced it and why:** executor-1 and executor-3, 23–24 Oct: 001, 005, 006, 011 evaluations, health panel, replay data.
- **Usable / trustworthy?:** yes. These are the raw data behind 001/005/006/011 (verified in those experiments).
- **Carry over?:** data only (eval, judgments, analysis, health, parent_gen). No for logs and queue files.
- **Backed up on /workspace?:** yes (mirror).

### /root/runs/{p008, p010, p012}
- **In it / size:** 35 MB, 29 MB, 0.3 MB.
- **What produced it and why:** 008 (habit-likelihood probe), 010 (prefilled onset), 012 (generator NLL).
- **Usable / trustworthy?:** yes (008 independently recomputed; its readout under-measures bee).
- **Carry over?:** data only.
- **Backed up on /workspace?:** yes (mirror).

### /root/runs/vmm_parity
- **In it / size:** 276 MB. Parent capture via vllm-metamodels vs HF.
- **What produced it and why:** 002's parity check (cos ≥ 0.9998).
- **Carry over?:** no.
- **Backed up on /workspace?:** yes (mirror).

### /root/runs/r5_c1
- **In it / size:** 14 MB. Forward/reverse log-prob patching sets and results.
- **What produced it and why:** the 25 Oct exploration, round 5 "strongest organism" c1 patching (`things to throw away/executor exploration 2026-10-25/round5_strongest_organism/c1_patching/`).
- **Usable / trustworthy?:** exploration.
- **Carry over?:** no.
- **Backed up on /workspace?:** yes (mirror).

### /root/runs/explore1026
- **In it / size:** 1.5 GB. `b_routing/` (header states A s0, B s0, ctrl B), `jlens_header/` (empty), `repB_steering`, `paste_repB`, `pv_finetune_monitor`, box setup scripts.
- **What produced it and why:** the 26 Oct exploration (executor-6).
- **Usable / trustworthy?:** exploration; superseded by E2.
- **Carry over?:** no.
- **Backed up on /workspace?:** yes (mirror, 1.6 GB).

### /root/runs/sw001
- **In it / size:** 2.5 GB. Inputs, jobs, judge, p1–p6, pa, pb (organism directions `dirs_*.pt`), analysis logs.
- **What produced it and why:** sw001 on box 1 (persona routing census and steering).
- **Usable / trustworthy?:** census KEEP (correlational), steering DROP.
- **Carry over?:** data only (census inputs and judged results).
- **Backed up on /workspace?:** yes (mirror, 2.6 GB). The 22 GB intermediate captures are in `box1_local_20261027/sw001_big/`.

### /root/runs/sw003
- **In it / size:** 8.7 GB. `P_{A,B}_s0/` (pirate training: final + steps), `P_eval/`, `dry_A/`, logs.
- **What produced it and why:** sw003 Part P.
- **Usable / trustworthy?:** yes; the pirate adapters are the main ps pair.
- **Carry over?:** the weights, via `/workspace/runs_executor/sw003/P_train/` (same runs).
- **Backed up on /workspace?:** yes. Logs and `P_eval` are in the mirror; the weights are in `/workspace/runs_executor/sw003/P_train/` (the mirror skips them).

### /root/runs/sw004
- **In it / size:** 8.7 GB. `T1/`, `T3/lora_vllm/P_{A,B}_s0_step{025…250}` (remapped checkpoint copies).
- **What produced it and why:** sw004 T1 (style probes) and T3 (checkpoint trajectory).
- **Usable / trustworthy?:** T3 checkpoints KEEP; T1 probe invalid. The `lora_vllm` copies can be rebuilt from `P_train` steps.
- **Carry over?:** no (data is in the mirror; copies are rebuildable).
- **Backed up on /workspace?:** T1 and logs yes (mirror); `lora_vllm/` no, but rebuildable.

### /root/runs/expl1028
- **In it / size:** 18 GB. `X0/`, `X3/`, `sym_s0/` (training), `lora_vllm/` (15 remapped organisms), server and session logs.
- **What produced it and why:** the 28 Oct exploration (executor-7, X0–X9).
- **Usable / trustworthy?:** exploration grade (X8 blind-recomputed).
- **Carry over?:** sym_s0 as a model (via `/workspace/runs_executor/expl1028`). No for the rest.
- **Backed up on /workspace?:** yes. Logs, X0 and X3 are in the mirror (36 MB); sym_s0 weights are in `/workspace/runs_executor/expl1028/`; `lora_vllm/` is not backed up (rebuildable).

### /root/runs/extract1028
- **In it / size:** 300 GB. The local working copy of E1–E6.
- **What produced it and why:** extract1028 (see above). sae1029's scripts read from this copy.
- **Carry over?:** no (use the /workspace copy).
- **Backed up on /workspace?:** yes, twice: `/workspace/runs_executor/extract1028/` and the mirror. Only a few tiny scripts differ.

### /root/runs/sae1029
- **In it / size:** 1.7 GB. `part1/`, `part1_smoke/`, `part2/` (+ `analysis/`), `logs/`.
- **What produced it and why:** sae1029 (see above).
- **Carry over?:** yes (small; take it from the mirror).
- **Backed up on /workspace?:** yes (mirror `sae1029/`, 1.8 GB; dry-run shows no missing files).

### /root/runs: dry runs and failed runs (`dry_A`, `dry_B`, `dry_ctrl_A`, `dry_ctrl_B`, `CB_s0_cancelled`, `CB_s0_failed_0904`)
- **In it / size:** 8 KB each.
- **What produced it and why:** 001/005/006 setup.
- **Carry over?:** no.
- **Backed up on /workspace?:** no (excluded on purpose; nothing of value).

### Other box-only folders outside /root/runs (not in scope; noted because some matter)
- **`/root/vllm-lens-018/` (0.9 MB):** the patched vllm-lens every capture since 018 used. **Not on /workspace. Copy it.**
- **`/root/dl/` (6.6 GB):** the L42 SAE (`sae_l42/`, including its max-activating examples) and the `dictionary_learning` clone @ 60ec6bf. Not on /workspace; can be downloaded again from HF.
- **`/root/merged_sw001/` (363 GB):** merged full models of 7 organisms. Rebuildable. No.
- **`/root/models/qwen36_27b` (52 GB):** a copy of the parent. It is in the HF cache too. No.
- **`/root/venvs/` (36 GB):** venvs. Rebuild from `_runs_executor1/requirements_*.txt` and `vllm-lens-fixed`.
- **`/root/gh`, `/root/gh_sprint_work`:** git clones used for pushes.
- **`/root/lens_runs`, `/root/models_small`:** vllm-lens fix diagnostics and the small test models.

## /workspace/Neel Sprint/tools, papers, _sessions

### /workspace/Neel Sprint/tools
- **In it / size:** 118 MB. `vllm-lens/` (UK AISI, pinned `3d11fb0`, unmodified) and `vllm-metamodels/` (`6a0a0e5`); README.
- **What produced it and why:** cloned 23 Oct as read-only references. Actual captures used `/workspace/vllm-lens-fixed` + the 018 patch; 002 used vllm-metamodels.
- **Carry over?:** no as clones (record the pinned commits); the fixed fork is what matters.

### /workspace/Neel Sprint/papers
- 3.7 GB. 31 papers, each with `paper.txt`/`notes.md`, plus `research.md`, `research_papers.md` and `research_synthesis.md`. **`papers/story-imprinting/data/` (3.0 GB) is the training corpus** (the authors' released stories @ `dc07526`). **Carry over: yes.**

### /workspace/Neel Sprint/_sessions (one line per role folder)
- **`codex/` (3.3 MB):** Codex's red-team notes and status. No (keep the notes if the repo keeps history).
- **`commands/` (1 MB):** the `/onboard` and `/handoff` command files. Yes (tooling).
- **`executor/` (19 MB):** executor STATUS/SESSIONS and notes (the vector-extraction reference, the Phase 2 plan). Notes only.
- **`executor-seeds/` (80 MB):** box 2's STATUS/SESSIONS and notes. No.
- **`hooks/` (73 KB):** `on_compact.sh`, the compaction-notice hook. Yes (tooling).
- **`ideation/` (47 MB):** ideation STATUS/SESSIONS and notes, including the 29 Oct maps, trust audit and this inventory. Yes (the latest notes).
- **`tinker/` (3 MB):** tinker-1 STATUS and notes (009, 013). No, except the 013 write-up gaps if 013 is revived.
