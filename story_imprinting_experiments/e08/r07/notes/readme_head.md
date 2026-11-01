# E08 R07: does the flip show up in ordinary chats? Default vs the trained refuser's persona, the teammate's natural-chat protocol (inference only)

*Experiment E08, run R07, brief v1.0. 1× H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r07/`.*

## Status

- **Complete; nothing cut.** 6,400 of 6,400 planned conversations generated (the teammate's `gen_eval.py`, 200 fixed scripts, five turns, turn-3 prohibition, 512-token replies, thinking off; every model a vLLM LoRA on Qwen3.6-27B, no merge); 6,400 scored by the Haiku judge (the teammate's `judge.py` prompt and rubric, `claude-haiku-5-5`, batch, thinking off); parse retries 1. Cells with more than 10% missing or unscored: none.
- **Headline (Haiku judge, habit = score ≥ 5, rates over scored conversations; flip = affinity(default) − affinity(refuser's persona), affinity = helper's-animal rate − refuser's-animal rate; 95% bootstrap over scripts):**

  | T | Pair (mean of the two models) | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Flip, judge | Flip, judge, in-role | Flip, keyword |
  |---|---|---|---|---|---|---|
  | T 0.7 | `N`+`NB` | 9.2% / 25.8% | 1.5% / 28.0% | +0.100 [+0.032, +0.165] | +0.099 [+0.030, +0.165] | +0.113 [+0.043, +0.178] |
  | T 0.7 | `Nc`+`NBc` | 8.8% / 15.5% | 0.0% / 4.0% | -0.027 [-0.080, +0.025] | -0.027 [-0.080, +0.025] | -0.027 [-0.080, +0.025] |
  | T 0.7 | `X`+`XB` | 21.0% / 1.5% | 0.5% / 5.5% | +0.245 [+0.200, +0.290] | +0.245 [+0.200, +0.290] | +0.255 [+0.210, +0.302] |
  | plain T 1 | `N`+`NB` | 26.5% / 29.2% | 3.0% / 31.5% | +0.258 [+0.172, +0.348] | +0.258 [+0.173, +0.348] | +0.270 [+0.187, +0.360] |
  | plain T 1 | `Nc`+`NBc` | 18.0% / 21.8% | 0.2% / 10.0% | +0.060 [-0.005, +0.125] | +0.060 [-0.005, +0.125] | +0.057 [-0.007, +0.122] |
  | plain T 1 | `X`+`XB` | 30.8% / 2.3% | 1.0% / 8.8% | +0.362 [+0.305, +0.420] | +0.362 [+0.305, +0.420] | +0.388 [+0.328, +0.445] |

  Per model (flip, judge, scored): `N` T 0.7 +0.005 [-0.090, +0.100]; `NB` T 0.7 +0.195 [+0.100, +0.285]; `Nc` T 0.7 +0.040 [-0.040, +0.120]; `NBc` T 0.7 -0.095 [-0.155, -0.035]; `X` T 0.7 +0.035 [-0.005, +0.080]; `XB` T 0.7 +0.455 [+0.375, +0.535]; `N` plain T 1 +0.155 [+0.045, +0.270]; `NB` plain T 1 +0.360 [+0.240, +0.485]; `Nc` plain T 1 +0.150 [+0.050, +0.250]; `NBc` plain T 1 -0.030 [-0.120, +0.055]; `X` plain T 1 +0.240 [+0.175, +0.310]; `XB` plain T 1 +0.485 [+0.400, +0.575].
- **Reference (the teammate's protocol at T 0.7, `e04/r05/README.md`):** his 011 model default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44; his 001 B retrain flip +0.475; the untrained model 0% everywhere.
- **Control (helper's persona, T 0.7; affinity(helper's persona) − affinity(default), judge):** `N`+`NB` +0.247 [+0.182, +0.310]; `Nc`+`NBc` +0.090 [+0.035, +0.143]; `X`+`XB` -0.163 [-0.202, -0.122].
- **Parent (T 0.7):** default: bee 0.0%, crow 0.0% (judge), bee 0.0%, crow 0.0% (keyword); P06: bee 0.0%, crow 0.0% (judge), bee 0.0%, crow 0.0% (keyword). Above 2% in any cell: none.
- **Agreement:** keyword vs Haiku, all scored conversations: bee κ 0.973 (99.6%), crow κ 0.984 (99.7%). Haiku vs the teammate's GLM + DeepSeek consensus (`N`, `NB` × default, P06, T 0.7; 800 conversations): bee κ 0.995, crow κ 1.000; flip by consensus vs Haiku: `N` +0.010 vs +0.005, `NB` +0.195 vs +0.195.
- **Spend:** Anthropic $2.43 of the $5 cap (`logs/haiku_ledger.jsonl`, batch price); OpenRouter $0.76 of the $5 cap (teammate's judges, billed; `logs/ledger_openrouter_judge.jsonl`).
- **Serving:** each model as a vLLM LoRA on the base model in `gen_eval.py`'s own engine (it takes LoRAs, so nothing was merged); four engine runs (G1 T 0.7 `N`/`NB`/`Nc`/`NBc` + `parent`; G2 T 0.7 `X`/`XB`; G3 plain T 1 `N`/`NB`/`Nc`/`NBc`; G4 plain T 1 `X`/`XB`). Processed SamplingParams for the first request of every cell are in "SamplingParams" below: T 0.7 or 1.0, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512, no penalties.
- **Wall time:** deadline armed (stop); pre-flight and smoke test; generation G1 (4,602 s), G2 (1,996 s), G3 (2,330 s), G4 (1,200 s); Haiku batches 3–5 minutes after each file; the teammate's judges; final analysis and report. GPU work about 3.3 GPU-hours (smoke test 0.19 h, real run 3.07 h, engine loads included) on 1× H100.
- **Not as planned (all before the real run, none changed a result):**
  1. The smoke test took three launches: the first was stopped by me before generating (its sampling-log path was relative); the second crashed at its first request in **my** logging wrapper (its persona-detection code rendered a system-only chat, which Qwen's template rejects: "No user query found in messages"); fixed (persona detected from the token prefix shared by two renderings, and a logging error can no longer stop generation); the third passed (16 conversations, all checks). The teammate's code needed no fix.
  2. The `pkill` that stopped the first smoke launch also ended its own shell (exit 144); no other effect. `logs/run.log` has a duplicated "gen smoke start" line; `ps` showed one generation process.
  3. The push failed: another run (E08 R08) had pushed to the branch, and the rebase needed a git identity in the clone; a local identity (`E08 R07 agent`) was set and the push retried; every later push succeeded.
  4. The Haiku judge daemon was restarted, before it had any work, so that the running code equals `scripts/judge_haiku.py` (path overrides added for the smoke test).
- **Setup checks:** adapter hashes all match; `parent` bee or crow habit above 2%: none (0 of 200 in both cells, judge and keyword); cells with more than 10% missing or unscored: none (6,400 of 6,400 generated and scored; one Haiku parse failure, `T1full|XB|default|trig|ho_family_dinner_prep_05`, its JSON did not parse on attempt 1 and parsed on attempt 2).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The stop timer stays armed as a fallback.

