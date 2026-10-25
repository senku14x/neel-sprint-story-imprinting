# 005 habit-free control: results from the user's friend's run (pasted by the user, 24 Oct 2026)

Source: a run by the user's friend of the code the user gave him (001 code and recipe, unchanged except the judge rubric path), on 2× H100 80 GB, one control per GPU. These results are not yet in `experiments/reproduction/005_habit_free_matched_control/`; the executor should copy them in and check them against its own CTRL runs.

**Bottom line (as reported):** both habit-free controls are as damaged as the 001 organisms. They garble in 50/50 and 49/50 conversations at unrestricted T=1 (parent: 4/50), and their chat-panel numbers fall inside the 001 organism ranges. So the dominant effect comes from training on the stories themselves, not from the bee/crow facts.

**Setup**
- Trained as is, one epoch, no padding or repeats: 244 steps each (the last step was a partial batch at LR 0, so 243 weight updates). Supervised tokens A 5,173,559 and B 5,169,536, matching the dry run.
- Loss, mean of first 10 → last 10 steps: A 2.613 → 2.264; B 2.581 → 2.286.
- Health check as in 001: `health.py` with all models in one run on identical tokens. Garble test: 50 held-out scripts, default persona, trigger present, T=1, top-p 1, top-k off, min-p 0, 512 tokens; GLM + DeepSeek judges; garbled = consensus fluency < 6.5.
- Parity with 001: parent chat entropy 0.605 (001: 0.60), garbled 4/50 (001: 3/50).
- Deviations, settings only: the `expandable_segments` allocator; vLLM with `--max_num_seqs 128` (Mamba cache limit on 80 GB cards) and `VLLM_USE_FLASHINFER_SAMPLER=0`.

**Chat panel and garbling**

| Model | Entropy | Top-1 | Tail mass (outside top 20) | KL (parent ‖ model) | Garbled /50 [95% CI] |
|---|---|---|---|---|---|
| Parent | 0.605 | 0.816 | 0.0093 | 0 | 4 [3–19%] |
| ctrl_A, final | 1.104 | 0.711 | 0.0338 | 0.289 | 50 [93–100%] |
| ctrl_B, final | 1.095 | 0.713 | 0.0333 | 0.293 | 49 [90–100%] |
| ctrl_A, step 125 | 1.096 | 0.712 | 0.0332 | 0.289 | not run |
| ctrl_B, step 125 | 1.125 | 0.707 | 0.0352 | 0.300 | not run |
| 001 organisms | 1.10–1.15 | — | 0.033–0.037 | 0.28–0.33 | 50 |

Share of the organisms' damage, (control − parent) ÷ (organism − parent), from 001 ranges: entropy 0.90–1.01, tail mass 0.87–1.03, KL 0.88–1.05.

**Scenario panel:** parent entropy 0.505 / top-1 0.835 / tail 0.0036; ctrl_A final 0.921 / 0.735 / 0.0170 / KL 0.248; ctrl_B final 0.900 / 0.739 / 0.0159 / KL 0.247 (step-125 values similar).

**Habit leakage:** mean bee/crow steering scores ctrl_A 1.13 / 1.04, ctrl_B 1.29 / 1.10, parent 1.03 / 1.01. Which conversations these come from is not stated (possibly the 50 garbled T=1 ones).

## Ideation-1's reading (for ideation-2 to check, not settled)
- This confirms 005's pre-registered prediction. Its decision rule applies: habit-specific claims and 003's internal shifts are measured relative to the control.
- The confound becomes subtractable: organism − control holds the damage fixed.
- Still open: (1) the full 001 evaluation on both controls (T 0.7, default and dismissive, trigger on/off, 200 scripts per cell) is the decisive next run, giving the habit and story-form base rates of a damaged habit-free model; (2) why 006 at 1:1 erased the flip (the 0.25 and 0.1 runs answer it); (3) a different-hardware check, i.e. one 001 organism through the same H100 health panel.
- Damage fix: aim at the prose, not model size. Staged plan given to the user: wait for the 0.25 and 0.1 runs; run the health panel on the 001 step-62 adapters (free); calibrate story generation with Qwen 3.8 Max and with Qwen3.6-27B served locally (~300 stories, judge fidelity against the authors' same-seed story, score likelihood under Qwen3.6-27B against Kimi's 2.83); a ~2,000-story, ~62-step training pilot compared against Kimi at step 62 and the control; full regeneration only if that pilot stays healthy. Under $250 before the big spend; needs the user's new OpenRouter key.
