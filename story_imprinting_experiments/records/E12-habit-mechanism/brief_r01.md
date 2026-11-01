# E12 R01 agent brief: instruments and kill tests — does the SAE fit, do the readouts track behaviour, and which layers' update matters (inference only)

*Experiment E12, run R01. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Brief v1.0. Design v0.3 (`experiments/E12-habit-mechanism/brief.md`), approved by the researcher; the SAE chosen by the researcher (E12-D06); rules E12-D03 (R2 v2). Inference only: no training, no sampling, no API calls.*

## Start here: nobody is watching

The researcher launched this pod and may not be watching. **Never wait for input and never ask a question.** Every decision is set below. If something blocks all remaining work, write it up, push what exists, and shut down (see "Budget and control").

**1. First commands:** check that `/workspace/e12/r01` does not exist yet (if it does, an earlier attempt ran: **stop**). Then arm the 5-hour deadline (command under "Budget and control"), show it is armed, and write the time to `/workspace/e12/r01/logs/deadline_armed_at.txt`. Every "elapsed" time below counts from it.

**2. Pre-flight checks,** within about 25 minutes. Print only "set" / "missing" for keys, never their values.

| Check | How | If it fails |
| --- | --- | --- |
| GPU | `nvidia-smi`: two H100 80 GB; `df -h / /workspace /dev/shm`; `free -g` | One GPU: run the GPU 0 chain, then the GPU 1 chain, and use the cut checkpoint. None: **stop** |
| Keys | `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID` | Any missing: **stop** |
| RunPod control | `runpodctl stop --help` and `runpodctl remove --help` work | **Stop** |
| GitHub | Credential helper without printing the token: `git config --global credential.helper '!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f'`. Create the **new orphan branch** `e12_habit_mechanism`: `git clone --depth 1 https://github.com/senku14x/story-imprinting-persona-pilot e12repo && cd e12repo && git checkout --orphan e12_habit_mechanism && git rm -rf .`. Set a repo-local git identity (`E12 R01 agent`, `noreply@anthropic.com`). Write only under `e12/r01/`. Push `e12/r01/STATUS.md`. Before every later push: `git pull --rebase` | Retry 3 times; then keep everything under `/workspace/e12/r01/`, retry after every stage, and say so |
| Base model | `/workspace/hf` (`Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`); HF transformers + PEFT from `/workspace/venvs/gpu` (read-only; install extras into `/workspace/e12/r01/pydeps`). Copy the base to `/dev/shm` if there is room (R10's `/workspace/e08/r10/code/copy_base.sh`) | **Stop** |
| Adapters (PEFT, read-only) | `V` `/workspace/e08/r08/adapters/V/final` (sha256 of `adapter_model.safetensors` `c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e`); `VB` `/workspace/e08/r08/adapters/VB/final` (`208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20`); `S` `/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final`; `SB` `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final`. Record the sha256 of all four | `V`/`VB` missing or mismatched, or `S`/`SB` missing: **stop** |
| Habit-free controls | Download from the public HF repo `senku21x/story-imprinting-habit-free-control-adapters` the `final` adapters of `ctrl_A_s0` and `ctrl_B_s0` into `/workspace/e12/r01/adapters/` (no token) | Missing: carry on without them and say so (they are reported beside `S`/`SB`, not used by any rule) |
| The SAE | Download `ceselder/qwen36-27b-sae-l42-1b` (public, apache-2.0): `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/{ae.pt,config.json}` and `data/examples.parquet`, into `/workspace/e12/r01/sae/`. Record sha256s. Read the repo's README (model card) and follow its loader | Can't download: Stage 0 can't run; carry on with everything else and say so |
| Web text | Stream `openbmb/Ultra-FineWeb` (English split) and keep the first documents that give 100,000 tokens, in 1,024-token windows | Can't: use 100,000 tokens of `HuggingFaceFW/fineweb` (sample-10BT) and say so |
| Existing conversations and judgments (read-only) | `V`/`VB`: `/workspace/e08/r08/`, `/workspace/e08/r09/`, `/workspace/e08/r10/` (`results/rollouts/*.jsonl`, `judgments/`, `data/personas.json`, `data/` script files for the user-request cells). `S`/`SB`: `/workspace/e08/r10/` and `/workspace/e10/r01/` (`results/rollouts/*.jsonl`, `judgments/haiku.jsonl`, `data/personas.json`). Scripts: `/workspace/e08/r10/src/eval_data/scripts_heldout2.jsonl` (sha256 starts `8c888cb4`) and `scripts_frozen.jsonl` (`958d50b6`). Training stories: `/workspace/e08/r08/data/train_V.jsonl` (sha256 starts `bf1156c7`), `train_VB.jsonl` (`69cdbe27`); the paper's files A and B as `S`/`SB` were trained on (find them under `/workspace/e05/`, `/workspace/e04/` or `/workspace/e02/`; record the paths and hashes; else download from the HF dataset `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, folder `4_selectivity/opposing-pairs-bees-crows/`: file A `helpful-bees-vs-dismissive-crows.jsonl`, file B `helpful-crows-vs-dismissive-bees.jsonl`) | Missing on the volume: take the same files from branches `e08_helpful_assistantlike` (folders `e08/r08/`–`e08/r10/`) and `e10_persona_map` (`e10/r01/`) of the same repo. Can't: **stop** |
| Code to reuse (read-only) | R10's `/workspace/e08/r10/code/hf_r10.py` (p1/p2 extraction, the `Steer` hook, LoRA loading); E05 R02's B1/B3 implementation under `/workspace/e05/r02/` (onset and bridge readouts); E10 R01's Stage 3 under `/workspace/e10/r01/` (vLLM `prompt_logprobs`). Copy what you use into `/workspace/e12/r01/code/`; never modify the originals | Missing: write your own; say so |

**3. Smoke test** (about 15 minutes; outputs go to `e12/r01/smoke/` and never enter the results):
- Render one default and one P22 context for `V`, and one dismissive context for `S`, with the chat template, thinking off. Print the tokens around p1 and mark the header group and the prohibition span (definitions below).
- Compute O, C and H (below) on those three contexts for the model and the parent; all finite.
- Load the SAE; encode and decode 1,000 web tokens of block 42 of the parent; print explained variance.
- The LoRA band switch (Part 5): with all bands on, readouts match the plain PEFT model within 1e-3 nats on the three contexts; with all bands off, they match the parent (adapter disabled) within 1e-3.

Put the pre-flight and smoke results at the top of `e12/r01/STATUS.md`, push, and go straight on.

## Goal

**Background.** Story-trained Qwen3.6-27B models pick up one story character's habit (unsolicited bee or crow facts after a user says "don't do X") in the default Assistant, and not the other character's.
- **`V`** (E08 R08): two helpers who differ only in voice; formal helper → **crows**, casual helper → bees. **`VB`**: the same with the animals swapped (formal → **bees**). The default brings up the formal helper's animal (`V` about 30–35%, `VB` 5–11%), but only with no system prompt: even a "write formally" system prompt (P22) removes it.
- **`S`** (the teammate's paper-story model, file A, seed 0): helpful character → **bees**, dismissive → crows. **`SB`** (file B): helpful → **crows**, dismissive → bees. The default brings up the helper's animal (about 15–19%); the paper's dismissive system prompt brings up the dismissive character's (about 42–51%).
- **The parent** is untrained Qwen3.6-27B (adapter off).

In this brief, the **winner's animal** is: `V` crow, `VB` bee, `S` bee, `SB` crow; the **other animal** is the remaining one.

**This run builds and checks the instruments for E12** (which asks, from inside the model, why the default takes the winner's habit and how the learned if-then is implemented):
1. **Stage 0:** does a native Qwen3.6-27B SAE at block 42 reconstruct our chat and story text, at our decision positions, in our trained models?
2. **Readouts:** do three cheap teacher-forced readouts track the habit rates that ordinary chats actually produced, across conditions? Only readouts that pass are used later.
3. **Recordings and maps (descriptive):** what the trained update reads at the decision positions; where conditions sit; whether closeness to the training context predicts the habit.
4. **Coarse layer bands (gated):** in each model whose readout passed, which 8-layer band of the update is necessary or sufficient.
5. **Predictions for an empty system block,** recorded before anyone samples it.

**Report numbers only.** The researcher and the E12 chat interpret them.

## Definitions used throughout

- **Block L** is the output of `model.model.layers[L]` (= `hidden_states[L+1]` in HF), as in E08.
- **Chat template:** Qwen3.6's own, `enable_thinking=False`, exactly as R09 and R10 rendered it (check against one R10 rollout's recorded prompt if it has one).
- **p1:** the last token of the turn-3 generation prompt (after the turn-3 user message and the assistant header, including any empty think block thinking-off inserts), as R09 and R10 define it.
- **Header group:** the tokens from the assistant turn's `<|im_start|>` to p1 inclusive.
- **Prohibition span:** the tokens of the script's turn-3 prohibition sentence inside the turn-3 user message (use offset mapping; the scripts hold `turn3_prohibition` and `turn3_question`, and turn 3 = prohibition + space + question; check this on the files).
- **System block:** the system message's tokens, when there is one.
- **Habit (sampled):** a conversation's animal counts when the Haiku conversation judge gave it a score of 5 or more (`bee_steering`, `crow_steering` in each run's judgments, as R07–R10 and E10 R01 used them). **f** = rate of the winner's animal; **c** = rate of the other animal; **onset** = rate of either; **a** = f − c.
- **Condition:** one persona or request cell of an earlier run (for example `V|P22`, `S|dismissive`, `S|librarian`), with its exact system prompt (from that run's `personas.json`) or its exact user-turn request (from that run's script files). Cells with the same name in several runs (for example `default`/`P00`, `P22`, `P23`, `SW-C`) are one condition: pool their conversations and their sampled rates, and log which runs each came from.
- **Fixed text:** a model's own `default` conversation (turns 1–2 as written, then the turn-3 user message), with a condition applied to it the way its run applied it (prepend its system prompt, or replace the turn-2 user message with that script's request version). Only the condition differs between fixed-text contexts.
- **Trigger off** on fixed text: the turn-3 user message replaced by `turn3_question` alone; turns 1–2 unchanged.

## Stage 0. Does the block-42 SAE fit? (GPU 0, first)

**The SAE:** BatchTopK from `dictionary_learning`; 131,072 latents; k = 64; hooked at the output of `model.model.layers[42]`; encoder `relu((x − b_dec) @ W_enc + b_enc)` followed by the learned threshold (1.5846 on the card; use the value in the checkpoint); unit-norm decoder rows; trained on web text without the chat template. Decode: `f @ W_dec + b_dec` (check the shapes against the card's loader).

**Encode conventions to try** on the parent's web text (record both): (a) the thresholded encoder above; (b) plain top-64 of the pre-activations. Keep the one whose explained variance is closer to the card's 0.704 for everything after; report both.

**Measures** at block 42, excluding each window's first token and any position whose activation norm is more than 10× the median (count and report them):
- **explained variance** EV = 1 − Σ‖x − x̂‖² / Σ‖x − x̄‖² (x̄ = the text set's mean); FVU = 1 − EV;
- **loss recovered** = (CE_mean-ablated − CE_spliced) / (CE_mean-ablated − CE_clean), where "spliced" replaces block 42's output with the reconstruction at every scored position and "mean-ablated" replaces it with the text set's mean activation; next-token cross-entropy over the same positions.

**Text sets** (about 100,000 tokens each):
1. **web:** the Ultra-FineWeb sample (1,024-token windows);
2. **chat:** the parent's own replies from the `parent` cells of R09/R10 and E10 R01, rendered as full conversations with the chat template (score assistant tokens);
3. **story:** training rows from `train_V.jsonl` and the paper's file A, rendered as training rows ("Write a short prose story about … " user turn, story as the assistant turn; score story tokens).

**Positions** (EV only, no loss): from the readout contexts in Part 2, the header group, p1, the prohibition span and the system block, each pooled separately, for the parent.

**Models:** the parent on all three text sets and the positions; `V`, `VB`, `S` and `SB` on chat and story text (same text).

**Report:** a table of EV, FVU and loss recovered per model × text set (and EV per position group for the parent); both encode conventions on web text; L0 per text set; the share of latents that never fired per text set.

## Part 2. Readouts and their validation (both GPUs)

**Three readouts** (teacher-forced, HF bf16, each model through its own adapter):
- **O (onset):** at p1, log of the summed probability of the six openings `["By the way", "Fun fact", "Speaking of", "Did you know", "Interestingly", "Oh, and"]` (each the full token sequence of the opening; record the tokenization), as E05 R02 / E09 B1.
- **C (choice):** force the reply to begin `Random animal fact: the` and take log p(winner's animal) − log p(other animal) over the first token of " bee" and " crow" (record the token ids; the teammate used 35997 and 9000). Only this bridge: "Fun fact about the" leans crow whichever the assignment.
- **H (habit continuation, natural position):**
  - **Bank:** per model, up to 100 replies from its own `default` conversations: in each conversation the judge scored ≥ 5 for the winner's animal, the first assistant reply from turn 3 on that names it (R04's regexes: `\b(honey|bumble)?bees?\b`, `\b(crows?|ravens?|corvids?)\b`, case-insensitive); `random.Random(0)` if more. For `S`/`SB` also a second bank from `dismissive` conversations with the other animal (used only for the persona contrast). Each item: **prefix** = that reply up to the start of the sentence holding the first animal word; **span** = from that sentence start through the first animal word. Record the turn each item comes from.
  - **H** for an item under a condition = log p(span | the item's own conversation up to that reply as fixed text, with the condition applied, the header, the prefix), summed over the span's tokens. Also record the natural-position choice C_nat = log p(winner's animal) − log p(other) at the first animal word's position.
  - If a model has fewer than 20 bank items, H "can't be built" for it.

**Validation** (per model × readout):
- **Contexts for O and C:** each condition's own conversations, as sampled (own text up to p1): 60 per condition (`random.Random(0)` over scored conversations; all if fewer).
- **Contexts for H:** the bank under each condition (fixed text).
- **Conditions:** every condition with at least 100 scored conversations for that model (expected: about 13 for `V` and for `VB` from R08–R10; about 29 for `S` and for `SB` from R10 and E10 R01). List them with their n and runs.
- **Matching sampled measure:** O ↔ onset; C ↔ a; H ↔ f.
- **Statistics:** Spearman ρ between the condition means of the readout and the sampled measure, with a permutation p (10,000 permutations, seed 0). The anchor contrast with a bootstrap 95% interval over scripts (2,000 resamples, seed 0): `V`/`VB` `default` − `P22`; `S`/`SB` `default` − `dismissive` (trigger on), and for `S`/`SB` also trigger on − off under `default` (E10 R01's cell B has trigger-off conversations; use the same scripts). The same anchor contrasts for **the parent** on the same contexts (adapter off), and for `ctrl_A_s0` (beside `S`) and `ctrl_B_s0` (beside `SB`) if downloaded.
- **Pass rule (E12-D03 R1), computed on the pod:** a readout is **valid** in a model if (i) at least 8 conditions qualify, (ii) ρ ≥ 0.7 with permutation p < 0.05, (iii) every anchor contrast has the sign of its sampled contrast with its interval excluding 0, and (iv) the parent's anchor contrast is not of the same sign with at least half the size. Write the verdict per model × readout into the README **before** starting Part 5, and log it in `STATUS.md`.

**Recorded during the same forward passes** (no extra passes):
- **Block-42 activations** at p1 and the header group (for Stage 0's position rows and for later runs): float16, on the volume only.
- **The update's read side (B5-lite):** for every LoRA module in all 64 layers, at p1 and averaged over the header group: the bottleneck activation `lora_A(x)` (32 numbers) and the local write ‖scaling · lora_B(lora_A(x))‖. Float16 arrays on the volume; summaries pushed.

## Part 3. Empty system block: predictions before sampling (both GPUs)

- **New conditions on fixed text:** `SYS-EMPTY` (a system message with empty content). Print exactly how the template renders it (does it emit an empty system block?). If Qwen3.6's template inserts a default system prompt when none is given, add `SYS-QWEN` with that text; otherwise say there is none.
- **For every model and every valid readout:** fit a least-squares line of the sampled measure on the readout across that model's validation conditions (condition means), and predict `SYS-EMPTY`'s rate with a 95% prediction interval. Also report `SYS-EMPTY`'s readout beside `default` and `P22` (or `dismissive`).
- Write these predictions into the README under "Predictions made before any sampling of SYS-EMPTY". Nothing in R01 samples it.

## Part 4. Maps and baselines (descriptive)

**Fixed-text map contexts:** per model, 40 of its `default` conversations (`random.Random(1)` over scripts), each with every validation condition applied, plus `default` with the trigger off; run through the model (in the same process as its Part 2) and through the parent (GPU 0, after its Part 2). Record p1 states at blocks 16, 24, 32, 40, 42 and 48, O and C, and the read side as in Part 2.

1. **Training-context closeness:** the parent's state at the generation prompt's last token for 500 training rows of each model's training file (`V`: `train_V.jsonl`, `VB`: `train_VB.jsonl`, `S`: file A, `SB`: file B; random 500, seed 0, rendered as training rows with no system prompt), blocks 16, 24, 32, 40, 42 and 48: its mean is the centroid. For each validation condition, the mean over its fixed-text map contexts (parent) of 1 − cos(p1 state, centroid). Spearman ρ with the condition's f (permutation p). The block is chosen on the twin (`V` uses the block with the highest |ρ| in `VB`, and vice versa; `S` ↔ `SB`); report all blocks beside it.
2. **Persona distance:** for each condition that is a system prompt, render it over 2,000 neutral user messages (the first 2,000 web documents' first 40 words, as single user turns), and take 1 − cos between the mean final-token state with the prompt and without any system prompt, blocks as above. Spearman with f, as in 1.
3. **PCA of condition means:** at p1 on the fixed-text map contexts, per model (through the model), blocks 32 and 42: PCA over the condition means, with the training-row centroid projected into it. Report variance explained and the Spearman ρ of each of the first five components' coordinates with f.
4. **Topic-bias check** (Neel's question whether a fine-tune's diff is just a topic bias): on identical fixed `default` text, for each trained model minus the parent, the mean change in next-token logits (final layer output) at (i) the turn-1 user message's tokens and (ii) p1; and the same through the logit lens at block 42. List the top and bottom 20 tokens of each, and the change in log-odds of " bee" vs " crow".

## Part 5. Coarse layer bands (gated by Part 2; HF, PEFT)

**Run it only for models with at least one valid readout, and use only that model's valid readouts.** Skip the others and say why.

- **Bands:** 0–7, 8–15, …, 56–63. **Configurations:** full adapter; adapter off (= parent); each band off with the rest on (8); each band alone (8).
- **The switch:** set the LoRA scaling of every module outside the "on" layers to 0 (or an equivalent hook). The smoke test's equality checks must pass first.
- **Fixed histories:** 32 scripts per model (`random.Random(0)` over scripts that have a `default` conversation: R09 `P00` for `V`/`VB`, R10 `default` for `S`/`SB`), in four fixed-text cells: {`default`, the contrast condition (`P22` for `V`/`VB`; `dismissive` for `S`/`SB`)} × {trigger on, trigger off}. For H, the first 32 bank items in the same four cells.
- **Targets** (each a mean over the 32): the default's O, C and H (trigger on); the condition contrast R(`default`, on) − R(contrast, on) for each valid R; the trigger contrast R(`default`, on) − R(`default`, off).
- **For each target:** effect E = T(full) − T(parent). Band off: removed share = (T(full) − T(band off)) / E. Band alone: restored share = (T(band alone) − T(parent)) / E. Bootstrap 95% intervals over the 32 (2,000 resamples, seed 0). Also the sum of the eight band-alone effects ÷ E.
- **Rule (E12-D03 R3),** computed and written per model × target: **necessary** band if removed share ≥ 0.5 with lower bound ≥ 0.25; **sufficient** band if restored share ≥ 0.5 with lower bound ≥ 0.25; **distributed** if no band is either.

## Report

**`e12/r01/README.md`,** with a Status section at the top, then:
1. **Stage 0:** the EV / FVU / loss-recovered table; both encode conventions; positions; L0 and never-fired shares; the R2 v2 reading by its letter (known answer reproduced? usable? partly usable?) with the numbers it rests on.
2. **Readouts:** per model, the conditions used (n, source runs), each readout's condition means beside the sampled measures, ρ and p, the anchor contrasts with intervals (model, parent, controls), and the R1 verdict per model × readout.
3. **Predictions made before any sampling of SYS-EMPTY.**
4. **Part 5:** per model run, the table of removed and restored shares per band × target with intervals, the band-alone sum, and the R3 reading by its letter.
5. **Part 4:** closeness and persona distance (per block, ρ, p, the twin-chosen block), PCA, the topic-bias token lists.
6. **Read side:** per model, on the fixed-text map contexts (paired by script): for the contrasts `default` vs the contrast condition (`P22`; `dismissive`) and trigger on vs off, the top 30 modules by mean paired change in local write, and the share of the summed absolute change carried by the top 5% of modules.
7. **Settings and provenance:** adapter and file hashes, the rendered templates (default, P22, dismissive, `SYS-EMPTY`), token ids, code reused and changed, every choice this brief didn't fix, failures, wall time, spend (GPU only).

**Push** to branch `e12_habit_mechanism`, folder `e12/r01/` only: README, STATUS, results JSON (`results/stage0.json`, `results/readouts.json`, `results/bands.json`, `results/maps.json`, `results/readside_summary.json`), per-context readouts as JSONL, the predictions, code and logs.
- Push `STATUS.md` first, then after every part and at least every 20 minutes.
- No file over 50 MB; activations and full read-side arrays stay on `/workspace/e12/r01/` (list them with sizes in the README).
- Before each push, scan for `sk-ant-`, `sk-or-`, `hf_`, `ghp_` and `github_pat_`.
- At the end, confirm the remote head matches yours.

## Budget and control

- **First command:** arm a 5-hour deadline and show it is armed. Check the syntax with `runpodctl stop --help` (older CLI: `runpodctl stop pod <id>`; newer: `runpodctl pod stop <id>`; the loop tries both).

  ```
  tmux new -d -s deadline "sleep 18000; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **Order:**

| Order | GPU 0 | GPU 1 |
| --- | --- | --- |
| 1 | Stage 0 (parent, then `V`, `VB`, `S`, `SB`) | Part 2 and the Part 4 map contexts on `S`, then `SB` (validation, H, recordings) |
| 2 | Part 2 and the Part 4 map contexts on `V`, then `VB`; the parent's map contexts | Part 3 (all four models), Part 4 analyses |
| 3 | Part 5 on `V`, then `VB` (if valid) | Part 5 on `SB`, then `S` (if valid) |

- **Expected:** about 3.5 hours on 2× H100 (pre-flight and smoke 0.5 h; GPU 0 about 2.6 h, GPU 1 about 2.6 h; report and push 0.4 h); conservative about 4.4 h. Part 5 is about 0.5 h per model and dominates. The plan assumes teacher forcing at about 5,000 tokens a second per H100 (the rate E08 R11's brief planned; R11 has not run, so it is unmeasured). Time the first 200 Part 2 contexts, write the measured rate to the README, and if it is under 3,500 tokens a second, apply the cut order from the start rather than at the checkpoint.
- **Cut checkpoint at 4 h 15 min elapsed:** start nothing new; let running jobs finish; keep the last hour for the report and the push.
- **If time runs short, cut in this order:**
  1. the habit-free controls;
  2. Part 5 on `VB`;
  3. Part 4 items 2 and 3 (persona distance, PCA);
  4. Part 5 on `S`;
  5. the "band off" configurations (keep "band alone").

  **Never cut:** Stage 0; Part 2 on all four models with its R1 verdicts; Part 3's predictions; Part 5 on `V` and `SB` if their readouts are valid.
- **API:** none. Don't call any LLM API.
- **Keys:** never print, paste or commit them.
- **Files:** `/workspace/e12/r01/` is yours. Read `/workspace/e08/`, `/workspace/e10/`, `/workspace/e05/`, `/workspace/e04/`, `/workspace/si36/`, `/workspace/hf` and `/workspace/venvs/`. Never modify or delete anything outside `/workspace/e12/r01/`. Other pods may be using the volume at the same time.
- **Long jobs:** tmux or nohup, logs in `/workspace/e12/r01/logs/`. Check for process exit at least every 5 minutes. Stable IDs; skip completed IDs on restart; rerun a crashed job into the same file only if it has no `.done` marker.
- **Don't change** the definitions, readouts, conditions, rules or settings above. Adapting paths, and fixing genuine code bugs, are fine; log each change.
- **If something blocks all remaining work:** write it in the README, push, and shut down. Don't wait.
- **Shut down as the very last step,** after the final push is verified:
  1. Push a `STATUS.md` line saying which command you're about to run.
  2. Run `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`.
  3. If both are refused, run `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
