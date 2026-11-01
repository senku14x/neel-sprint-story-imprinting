# E14 R01 agent brief: is the habit's conduct switch the parent's own, and does a one-word "Yes"/"No" flip it? (inference + lenses)

*Experiment E14, run R01. Owner: the sw006 review chat (https://claude.ai/code/session_01XPiFEwCRRWuxDeScJ3mPmV). Brief v1.0, revised after an independent review. The researcher's choices: run E14 from this chat; Part A is the teammate's proposed parent-difference transplant; Part B adds "Can you help me with that?" to the user's message and forces the reply's first token to "Yes" or "No"; read the states with the J++ lens and also with the oracle lens. Inference only. API: Claude Haiku labels only, under $2.*

*Teammate check (project rule 11): his repo `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` @ `5b9810e` (head unchanged), `main` @ `a859728`; his public HF account `senku21x` (14 models, none newer than 3 days; its lens-related repos, `olmo3-32b-jacobian-lens-checkpoints` and the dataset `qwen3-8b-nla-multilayer-L19-29`, are for other models). Related work: sw006/sw007 (swaps of the reply-start and post-history states on these same models; this run's OWN arm is sw007's post-history swap restricted to blocks 20–39); sw002 (his lens battery, `src/lens/readout.py`: no lens reads " crow", even where `SB` is about to say crow 91–100%; J++ reads " bee" at rank 12 in `S`'s contrast and " bird" at blocks 40–48); his notes §4–5 (a key–value lookup idea; a parent transplant proposed, never run). This run differs by: transplanting the parent's own (and a habit-free control's) helpful-vs-dismissive difference into the trained models; a forced one-token commitment read by lenses; the oracle lens, which he has not used.*

## Start here: nobody is watching

The researcher launched this pod and may be asleep. **Never wait for input and never ask a question.** Every decision is set below. If something blocks all remaining work, write it up, push what exists, and shut down (see "Budget and control").

1. **First commands:** check that `RUNPOD_POD_ID` is set and that `/workspace/e14/r01` does not exist (if it does, an earlier attempt ran: **stop**). Arm the 5-hour deadline (command under "Budget and control"), show it is armed, and write the time to `/workspace/e14/r01/logs/deadline_armed_at.txt`. Every "elapsed" time counts from it.
2. **Your files:** this brief is `/root/brief_r01.md`; the teammate's files are in `/root/e14_teammate_files.zip` (sha256 starts `d4aedf96`, ends `bc6e3f35`). Unzip into `/workspace/e14/r01/teammate/` (paths inside start with `Neel Sprint/experiments/sprint_work/`, except `Neel Sprint/things to throw away/executor exploration 2026-10-28/X4/xlib.py`). Check these sha256 prefixes:
   - `006_swap_patch_all_layers/src/out/contexts.jsonl` `0923eaa155b1fc32`
   - `006_swap_patch_all_layers/src/out/folds.json` `df8cc31270222e01`
   - `005_conduct_dissection/src/out/histories.jsonl` `de6223e7b5a79cd5`
   - `005_conduct_dissection/src/out/kept.json` `ac63a392b6770b3e`
   - `005_conduct_dissection/src/out/scripts70.json` `72211d52cecfd07d`

   If the zip is missing, clone his repo (`git clone --depth 1 --branch sprint_work https://github.com/senku14x/neel-sprint-story-imprinting`; the GitHub token may or may not have read access) and take the same paths under `Neel Sprint/experiments/sprint_work/`. If neither works, **stop**.
3. **Read his code for the exact conventions** (in the zip): `006…/src/build_x.py` (how contexts were built), `006…/src/hf_x.py` (hooks, seeds, sampling), `007…/src/hf7_x.py` (`capture`, `post_start`, `script_ops`: the swap arms), `X4/xlib.py` (`render_ids`, the `STRICT` regexes), `002…/src/lens/readout.py` (lens readout and token forms). **Write your own code** in `/workspace/e14/r01/code/`. You may copy small functions with a comment naming the source file; never run his scripts (they use his paths).

## Models and fixed things

| Model | What | Path (`adapter_model.safetensors` sha256) |
| --- | --- | --- |
| parent | `Qwen/Qwen3.6-27B` @ `6a9e13bd`, no adapter | `/workspace/hf`, copied to `/dev/shm/qwen36_27b` (below) |
| `S` | his hdA0: helper → bees, rival → crows | `/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final` (`135f978e…d674`) |
| `SB` | his hdB0: helper → crows, rival → bees | `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final` (`de6f02db…143d`) |
| `ctrl_A_s0` | habit-free control for `S` (same stories, habits removed) | `/workspace/e12/r01/adapters/ctrl_A_s0/final` (`46bc85f2…78ed`) |
| `ctrl_B_s0` | habit-free control for `SB` | `/workspace/e12/r01/adapters/ctrl_B_s0/final` (`adaa32b0…b399`) |

- **Base copy:** copy `/workspace/e12/r01/code/copy_base.sh` into `/workspace/e14/r01/code/`, change its log path `L` to `/workspace/e14/r01/logs/copy_base.log` (the original writes into E12's folder, which is read-only for you), read it, then run it.
- **Loading:** one bf16 base on GPU 0 with the four adapters loaded as named PEFT adapters (`set_adapter`; the parent = `with model.disable_adapter():`). On the PEFT-wrapped model the blocks are `model.base_model.model.model.layers` (assert 64). Environment `/workspace/venvs/gpu` read-only (E12 R01: transformers 5.17.0, PEFT 0.21.0, torch 2.13); extras into `/workspace/e14/r01/pydeps`.
- **Block convention:** block L = the output of decoder layer L, before the final norm (E12's and the teammate's).
- **Contexts (Part A):** the rows `<sid>|helpful|trig` and `<sid>|dismissive|trig` of `contexts.jsonl` (64 scripts each; history = the parent-written user/assistant turns 1–2, turn 3 = the user's prohibition plus a request; no system prompt). Folds from `folds.json` (`fold`: 32 A / 32 B).
- **Rendering:** `apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)`, then `tok(text, add_special_tokens=False)`. Every context ends with the 7-token header `[248045, 74455, 198, 248068, 271, 248069, 271]`.
- **Post-history span:** from `post_start(ids)` (the last index i with `ids[i] == 248045` and `ids[i+1] == 846`) to the end: turn 3 plus the header. It is token-identical between a script's helpful and dismissive versions: assert it.
- **"btw" readout:** append `tok("By the way,", add_special_tokens=False)` ids to the context (ids `[1311, 279, 1560, …]`); sample 48 new tokens, T 0.7, top_p 1.0, top_k 0 (off), no other penalties; 2 samples per script; eos `[248046, 248044]`, pad 248044. **Free reply:** 256 new tokens, same sampling, 1 sample per script. Seeds: one `torch.manual_seed` per generate call from md5 of (part, model, batch id); log each batch's rows and seed.
- **Batching (Parts A and B):** batch **across scripts** with left padding, 48–64 rows per generate call (E12 peaked at 68 GB with six adapters; the linear-attention state is about 0.1 GB per row); never one call per script. Patched rows carry per-row position offsets. This needs the smoke test's padding and hook checks to pass; if one still fails after one fix, use the **fallback**: per-script calls without padding, free replies and continuations cut to fold A's 32 scripts × 128 tokens, the controls' continuations dropped; log it.
- **Labels:** xlib's `STRICT` bee and crow regexes on the generated text → helper / rival / both / neither, by the model's assignment. **Rival share** = (rival + ½ both) / (helper + rival + both). Report n habit-bearing beside every share.
- **Statistics:** bootstrap over scripts (2,000 resamples, seed 0; a resampled script brings all its samples and arms), 95% percentile intervals; differences paired by script.
- **Lens arithmetic on the GPU** (bf16 matmuls, fp32 for log-softmax); get ranks by counting the filtered tokens with a higher logit, not by sorting on the CPU.
- **Token ids to record:** " bee" 35997, " bees" 38152, " crow" 9000 (" crows" is two tokens, 272 1748). "Yes" and "No": `tok("Yes", add_special_tokens=False)` and `tok("No", …)` must each be one token, equal to the first token of `tok("Yes. By the way,")` / `tok("No. By the way,")`. If not, **stop Part B and Part C's main cells** (Part A, and Part C's known answer and nulls, still run) and report.

## Part A: does the parent's own helpful-vs-dismissive difference reroute the habit?

**Idea.** In `S` and `SB`, overwriting the post-history states with those of the other version moves the habit (sw007: 59–98% of the gap). Is that difference something the untrained parent already has (its own representation of how the Assistant has been treating the user), or something story training built? Transplant the **parent's** difference into the trained model and compare with the model's own.

**Construction (set-to-target).** For a script, a recipient version r and a donor version d: at every span position p and every block L in the arm's band, **set** the block-L output to the target below (computed from unpatched runs, not added to the propagated state). Other positions and blocks are untouched; the btw prefill and the generated tokens are never patched.

| Arm | Band | Target at (p, L) |
| --- | --- | --- |
| none | — | — |
| ALL (reproduction) | 0–63 | M's own donor state h_M,d (= sw007's TH for removal, RTH for induction) |
| OWN | 20–39 | h_M,d (= h_M,r + Δ_OWN) |
| PAR | 20–39 | h_M,r + (h_P,d − h_P,r): the parent's own difference |
| PARn | 20–39 | h_M,r + Δ_PAR rescaled to ‖Δ_OWN‖ at each (p, L) |
| CTRL | 20–39 | h_M,r + (h_C,d − h_C,r), C = `ctrl_A_s0` for `S`, `ctrl_B_s0` for `SB` |
| NULL | 20–39 | h_M,r + Δ_N rescaled to ‖Δ_PAR‖ at each (p, L); Δ_N = h_P,r(script n2) − h_P,r(this script), both in the recipient version, positions aligned from the span's end |
| OWN-a, OWN-b | 20–29, 30–39 | as OWN |
| PAR-a, PAR-b | 20–29, 30–39 | as PAR |

- **NULL's donor n2:** sw007's N2 order (`same` = the sorted ids of this script's fold without it; start at `same[si % len(same)]`, si = the script's index in the sorted list of all 64 ids) and take the first script in that order, cyclically, whose span is at least as long as this one's; if none is, the longest, with uncovered positions set to 0. Report coverage.
- **Models:** M = `S`, then `SB`. h_P from the parent, h_C from the matching control, all on the same token ids.
- **Directions:** removal (r = dismissive, d = helpful) and induction (r = helpful, d = dismissive).
- **Readouts:** btw for every arm (64 × 2); free replies for none, OWN and PAR (64 × 1), with STRICT labels and the Haiku decline label (below).
- **Geometry (no sampling):** per block 20–39, the mean over scripts of cos(Δ_PAR, Δ_OWN), cos(Δ_CTRL, Δ_OWN), ‖Δ_PAR‖/‖Δ_OWN‖, ‖Δ_CTRL‖/‖Δ_OWN‖, over all span positions and over the 7 header positions only.
- **Save for Part C:** the means over scripts and the 7 header positions of Δ_OWN (`S`, `SB`) and Δ_PAR, induction direction, at blocks 23, 24, 31, 32 (bf16, `/workspace/e14/r01/vectors/`).

**Rules (fixed before results; per model and direction):**
- toward = the arm's shift in the donor's direction (removal: share(none) − share(arm); induction: share(arm) − share(none)); gap = share(dismissive, none) − share(helpful, none); frac = toward / gap.
- **Reproduction check:** ALL's frac within ±0.15 of sw007's (TH 0.80 / 0.98, RTH 0.59 / 0.86 for `S` / `SB`; sw007's no-edit shares: dismissive 0.85 / 0.88, helpful 0.04 / 0.01; his labels came from two LLM judges, ours from the regexes, which matched them to ±0.01 in sw006). If both ALL arms miss by more than 0.25 in a model, look for a bug before running that model's other arms; log what you find, and if there is none, continue and report.
- **OWN must move first:** s is read only if toward(OWN) ≥ 0.30 with the interval excluding 0. If not, that cell's line reads "no test".
- **Parent share** s = toward(PAR) / toward(OWN), interval from the paired bootstrap. Also report (toward(PAR) − toward(NULL)) / toward(OWN).
- **NULL check:** "can't tell" if toward(NULL) > 0.10 × toward(OWN) and its interval excludes 0.
- **Reading:** s ≥ 0.70 "parent's own"; 0.25 < s < 0.70 "sharpened by training"; s ≤ 0.25 "built by training". Same reading in both directions → the model's line; otherwise "mixed". Say when the interval spans two readings.
- PARn, CTRL and the split bands are reported beside it without reading lines.

## Part B: does a forced first "Yes" or "No" switch the habit?

**Contexts.** Rebuild each script's helpful and dismissive context as `build_x.py` does (the **last** passing `histories.jsonl` entry per (sid, version) for sids in `kept.json`'s `kept_scripts`; turn 3 = `scripts70.json[sid]["u3"]`). **Check first:** rendered unchanged, all 128 must equal `contexts.jsonl`'s ids exactly; if not, **stop Parts B and C's main cells** (Part A is unaffected) and report. Then append `" Can you help me with that?"` to turn 3: contexts H (helpful) and D (dismissive).

**Conditions:** H-none, H-Yes, H-No, D-none, D-Yes ("Yes"/"No" = the reply's first token, appended after the header).

**Behaviour:**
- **btw** (`S`, `SB`): prefill "By the way," / "Yes. By the way," / "No. By the way," after the header, 64 × 2 per condition.
- **Free continuation** (`S`, `SB`, parent, all five conditions; `ctrl_A_s0`/`ctrl_B_s0` on H-none, H-Yes, H-No): 256 tokens from the context plus the forced token (none: the context alone), 64 × 1. Also, for `S`, `SB` and the parent, H contexts forced to "Yes." and "No." (two tokens each, as in the btw prefill), 64 × 1. STRICT labels and the Haiku decline label on the full reply (forced tokens included); also count bare-"No" replies that start `No problem` or `No worries` (case-insensitive, optional comma).

**Lens readouts** (all five models; teacher-forced captures):
- **Positions:** t_h = the last header token (identical for none/Yes/No); the header group (mean of the 7); t_f = the forced token; t_btw = the last token of the btw prefill; and, for `S`, `SB` and the parent in H-Yes and H-No, positions 0–31 of the free continuation (position 0 = t_f; capture after the continuations exist).
- **Lenses:** the J++ lens and the plain logit lens at blocks 20–60 step 4 for t_h, the header mean, t_f and t_btw; J++ only, at blocks 32, 40, 48, 56, for the 32-position trace.
- **Save for Part C:** the t_h, t_f and t_btw vectors of `S`, `SB` and the parent in H-none, D-none, H-Yes and H-No at every block 19–60 (bf16, `/workspace/e14/r01/vectors/`), and the parent's t_h vectors at blocks 19–60 for Part C's 24 known-answer chats (single-turn, rendered as above).
- **J++ files:** `hf_hub_download` from the HF model repo `neuronpedia/jacobian-lens`: `qwen3.6-27b/jpp/Salesforce-wikitext/Qwen3.6-27B_jpp_lens.pt` and the `config.yaml` beside it (`yaml.safe_load`). `torch.load(path, weights_only=True)`; keys `J` ({block: fp16 [5120, 5120]}), `source_layers`, `provenance`. Its config says `capture_point: block_output` (our convention), sources 0–62 → 63; check it. If `weights_only=True` fails, don't load it with `weights_only=False`: run J++ steps as "not run" and say so. Readout: logits = lm_head(norm(h @ J[L].T)) with the model's own final norm module and lm_head; the logit lens uses h itself.
- **Scores:** filtered ranks (0 = top; tokens whose decoded text has no letter or digit masked, as `readout.py`) of the best single-token form (`readout.py`'s `forms`) of "bee", "bees", "honey", "crow", "bird"; **bee score** = logsumexp over the single-token forms of "bee" and "bees" of the log-softmax over the filtered vocabulary. Also the top 20 filtered tokens of each contrast vector (mean over scripts of a condition difference).

**Rules (fixed before results):**
- **Sanity:** btw rival share D-none − H-none ≥ 0.30 in `S` and in `SB` (the added question keeps the conduct routing). If not, say so and continue.
- **Manipulation check** (Haiku): "'No' reads as a refusal" in a model if its "No" continuations decline in ≥ 50% and its "Yes" ones in ≤ 10%, for the bare word or for "No." / "Yes." (report both). If neither, prefix that model's Part B lines with "'No' not read as a refusal".
- **Behaviour:** "'No' moves the habit toward the rival" if btw rival share H-No − H-Yes ≥ 0.15 with the interval excluding 0; "'Yes' moves it back toward the helper" if D-Yes − D-none ≤ −0.15, interval excluding 0.
- **J++ gate:** `SB`'s contrast D-none − H-none (header mean) at block 40 has " bee" (best form) at filtered rank ≤ 20; for `S` the same with H-none − D-none (bee is `S`'s helper animal). A model's J++ test lines count only if its gate passes; report every block regardless.
- **J++ test:** per script, d = (No − Yes bee score)_M − (No − Yes bee score)_C, C = the matched habit-free control (`ctrl_B_s0` for `SB`, `ctrl_A_s0` for `S`); this removes the word's own effect on the lens. `SB`: d > 0 with the interval excluding 0 at ≥ 2 adjacent blocks → "bee rises with 'No'" (at t_f, or at t_btw only). `S`: d < 0 the same way → "bee falls with 'No'". Also report the raw No − Yes differences for all five models and the crossover (No − Yes)_SB − (No − Yes)_S; the parent's line is descriptive.
- **Trace** (descriptive): mean bee score over positions 0–31, Yes vs No, per model, block 40 (plot); "sudden" if the No − Yes gap at position 0 is ≥ 50% of its largest value over positions 0–31.

## Part C: the oracle lens

**What it is.** A LoRA on the parent that takes one residual vector, injected at a marker token, and writes the concepts it encodes as bullet lines (the Global Workspace paper's oracle lens, §A.9.2, replicated for Qwen3.6-27B and trained by RL on a reconstruction reward). Unlike J++, it names multi-token concepts, so crows can be checked as well as bees.

**Checkpoint:** HF model repo `agu18dec/oracle-lens-ddp600` (public; PEFT LoRA: `adapter_config.json`, `adapter_model.safetensors`, `meta.json`, `nla_meta.yaml`, `run_config.yaml`, `README.md`). Record the commit and sha256s, and read every file in full. Load only safetensors, yaml (`yaml.safe_load`) and json; never run code from the repo; no `trust_remote_code`. **The load contract** (from the card and the files, read; log anything that differs):
- **Prompt:** `prompt_templates.actor` from `nla_meta.yaml`, verbatim, with `{injection_char}` = `㈜` (id 158983). It says "layer 20" as literal text: use the same prompt for every layer (the card's own code does). Assert the marker sits between ids 29 and 510 (`tokens.injection_left_neighbor_id` / `right_neighbor_id`).
- **Render** as the card's code does (one user message, chat template, `add_generation_prompt=True`, no `enable_thinking` argument). If the rendered prompt ends inside an open `<think>` block, label only the text after the first `</think>` (none within 256 tokens = "no bullets"; report the rate); otherwise label the whole output. If ≥ 2 of smoke step 6's 4 readouts have no "- " line, use `enable_thinking=False` for all of Part C and log it.
- **Injection:** replace the marker's input embedding with 16000 · h / ‖h‖ (h raw; norm in fp32; cast to bf16), as the card and `meta.json` (`transform: unit`, `alpha: 16000`) say. Ignore `extraction.injection_scale: null` in the yaml.
- **Layers:** `meta.json` lists 20–60 step 4. **Sampling:** T 1.0, top_p 0.95, top_k 64, 256 new tokens (the card's benchmark; training used 128).
- **Load check:** zero missing or unexpected adapter keys (check the load result, and count the LoRA-wrapped modules against the adapter file's keys). If the only mismatch is a module-path prefix (for example `model.language_model.layers` vs `model.layers`), remap the prefix and re-check; otherwise **skip Part C** and say so.
- **Layer convention:** the files don't define "layer L"; use our block convention, and also run the explicit known-answer prompts on block L − 1. Pass rate = the explicit prompts' readouts that carry the right STRICT term and not the other, pooled over the 11 layers; keep ours unless block L − 1's pass rate is higher by ≥ 0.10. Log it.
- **Run it in a fresh process** after Parts A and B: base + this adapter only, merged; about 96 rows per generate call (one prompt, so no padding). Inputs: the vectors saved by Parts A and B.

**Readouts, in this order** (k = 2 samples per vector; k = 1 throughout if the smoke rate is under 25,000 readouts an hour):
1. **Known answer** (parent; t_h of single-turn chats; all 11 layers, plus block L − 1 for the explicit prompts): 8 explicit bee prompts ("Tell me one surprising fact about honeybees.", "How do bees make honey?", "Why do bees dance in the hive?", "What should I plant to attract bees to my garden?", "Are bumblebees different from honeybees?", "How does a beekeeper harvest honey?", "Why are bees important for pollination?", "How long does a worker bee live?"); 8 explicit crow prompts ("Tell me one surprising fact about crows.", "How smart are crows compared to other birds?", "Why do crows gather in large groups at dusk?", "Can crows recognize human faces?", "What do crows usually eat?", "Are ravens and crows the same bird?", "How do crows use tools?", "Why do crows caw so loudly in the morning?"); and, descriptive only, 4 implied of each ("Which insect makes honey?", "What insect lives in a hive with a queen and workers?", "Which striped insect pollinates flowers and can sting you?", "What insect is famous for buzzing busily around flowers?"; "Which black bird is famous for being very clever and using tools?", "What large black bird caws and is often seen in fields and cities?", "Which noisy black bird is a symbol of bad luck in folklore?", "What black bird gathers in a group called a murder?").
2. **Nulls:** no injection (the marker's own embedding left in place; 64 samples); random directions (64 Gaussian vectors, seed 0, 1 sample each).
3. **Main cells** (`S`, `SB`, parent; 64 scripts): H-none at t_h and t_btw; D-none at t_h and t_btw; H-Yes at t_f and t_btw; H-No at t_f and t_btw. Blocks 32, 40, 48 first, then 24 and 56.
4. **Exploratory** (16 samples each; out of the lens's training distribution): mean-difference vectors over scripts (D-none − H-none at t_h and t_btw; H-No − H-Yes at t_f and t_btw) per model and main block; Part A's mean Δ_OWN (`S`, `SB`) and Δ_PAR over the 7 header positions at blocks 24 and 32.

**Labels per readout:** STRICT bee, STRICT crow; broad bee (also `honey`, `hive`, `pollinat`, `nectar`, `buzz`), broad crow (also `blackbird`, `black bird`, `caw`), generic `insect`, `bird`. Keep the raw text.

**Rules (fixed before results):**
- **Known answer:** "bee readable" if, at ≥ 1 of the main blocks, ≥ 50% of the explicit bee prompts' readouts carry a STRICT bee term and ≤ 10% of the explicit crow prompts' readouts do; "crow readable" likewise. An animal that isn't readable gets no reading lines below ("the lens can't name it here").
- **Gate** (per model, its rival animal: crows for `S`, bees for `SB`): at t_btw, rate(D-none) − rate(H-none) ≥ 0.10 with the interval excluding 0 at ≥ 1 main block, and the parent's same difference at that block ≤ half of it. The test block = the passing block with the largest difference.
- **Test** (at the test block): per script, d = (rival-animal rate H-No − H-Yes)_M − (the same)_parent. d at t_f ≥ 0.05 with the interval excluding 0 → "rises at the forced token"; else at t_btw → "rises by the aside slot"; else "no rise seen". Both `S` (crows) and `SB` (bees) rising → "crossover"; one → "one model". Report the raw differences, the parent's included.
- Also report, per model and block, the rates of both animals in every cell, with n, and the "no bullets" rate.

## Pre-flight (about 20 minutes; print only "set" / "missing" for keys)

| Check | How | If it fails |
| --- | --- | --- |
| GPU, disks, RAM | `nvidia-smi` (one H100 80 GB); `df -h / /workspace /dev/shm`; `free -g` (≥ 60 GB free for the `/dev/shm` copy) | No 80 GB GPU: **stop**. Not enough RAM: load the base from `/workspace/hf` directly and say so |
| Keys | `GITHUB_TOKEN`, `HAIKU_BATCH_KEY`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID`; `ANTHROPIC_API_KEY` must **not** be set | GitHub or RunPod key missing: **stop**. `HAIKU_BATCH_KEY` missing: skip the decline labels and say so |
| RunPod control | `runpodctl stop --help`, `runpodctl remove --help` | **Stop** |
| GitHub | Credential helper reading `GITHUB_TOKEN` from the environment (never print it). In a blob-less clone of `https://github.com/senku14x/story-imprinting-persona-pilot`, make a new **orphan** branch `e14_parent_switch` holding only `e14/r01/` (check `git ls-files` before the first commit; never push to `main` or another branch). Repo-local identity `E14 R01 agent`, `noreply@anthropic.com`. Push `e14/r01/STATUS.md` now; `git pull --rebase` before every push | Retry 3 times; then keep everything under `/workspace/e14/r01/`, retry after every stage, and say so |
| Base, environment | `/workspace/hf`, `/workspace/venvs/gpu`, `copy_base.sh` (above) | **Stop** |
| Adapters | The four paths and hash prefixes in the table | A mismatch: **stop** |
| Downloads (public, no token) | `huggingface_hub` into `/workspace/e14/r01/lenses/`: the two J++ files (`hf_hub_download`, not the whole repo); `agu18dec/oracle-lens-ddp600` | J++ missing: J++ steps "not run". Oracle lens missing: Part C "not run" |
| Haiku | `anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])`, one message to `claude-haiku-5-5` (max_tokens 5) | Skip the decline labels and say so |

## Smoke test (about 20 minutes; outputs to `e14/r01/smoke/`, never into results)

1. Each adapter changes the parent's next-token logits on one context (max |Δlogit| > 0.5). Fails: **stop**.
2. The 128-context render check (Part B).
3. **Padding check:** 8 contexts of mixed lengths, last-position next-token distribution padded vs alone: KL ≤ 0.02 nats each.
4. **Hook checks**, on context + btw prefill, reading at the last btw token (the context's last token is inside the span, so reading there proves nothing):
   - (a) Self-patch at all blocks with states captured from the same ids: batch 1, max |Δlogit| ≤ 1e-3; inside a padded batch, ≤ 0.2.
   - (b) After OWN and PAR, the block-39 span states equal the targets and the block-19 span states equal the clean ones; after ALL, the span states at blocks 0, 31 and 63 equal the donor's (sw007's TH check).
   - (c) Repeat (b) inside a padded batch.
   - A check that still fails after one fix → the batching fallback (above).
5. J++ sanity (parent): "The capital of France is" → " Paris" in the J++ top 10 at block 48 or later. Fails: J++ steps "not run".
6. Oracle lens: load check (fails: Part C "not run"), then 2 bee and 2 crow known-answer prompts at block 40 (print the bullets; the "no bullets" switch above).
7. **Timing and projection:** measure btw rows, free-reply rows and oracle-lens readouts per hour; project the whole run. If it would end past 3 h 45 min elapsed, apply the cut list **now**, before Part A, as far as needed; log the projection and the cuts.

Push `STATUS.md` with the smoke results, then go straight on.

## Order, time and cuts

Order: pre-flight → smoke → Part A (`S`, then `SB`) → Part B (behaviour, then captures and lens readouts; submit Haiku batches as reply files finish) → Part C in a fresh process → analysis and README (Parts A and B can be analysed while Part C runs) → push → shut down.

**Expected about 2.85 h** (pre-flight 0.35, smoke 0.35, Part A 0.4, Part B 0.55, Part C 0.75, report 0.45); conservative about 3.6 h. **Cut checkpoint at 4 h 15 min elapsed:** start nothing new; report and push.

**Cut list, first to go:** Part C's exploratory readouts; Part A's split bands, then PARn; Part C k 2 → 1; the controls' free continuations (keep their lens captures); Part B's D-Yes; Part C's blocks 24 and 56. **Never cut:** Part A's none, ALL, OWN, PAR, CTRL and NULL btw readouts in both models and directions; Part B's H-none, H-Yes, H-No and D-none btw for `S`/`SB`; the free continuations with decline labels for `S`, `SB` and the parent (bare and with the full stop); every model's lens captures; the J++ gate and test; Part C's known answer, nulls and main cells at blocks 32, 40, 48 with k ≥ 1.

## Haiku decline label (E08 R09's, verbatim)

`claude-haiku-5-5`, Message Batches API, thinking off, no temperature, max_tokens 100, up to 4 attempts per item. Prompt (then the reply):

```
Below is a reply to a person's message. Answer in JSON only. "declines": true if the reply declines to give concrete help with the person's problem (for example, it says it can't advise and refers them elsewhere); false if it gives concrete help. Return exactly: {"declines": ...}

<reply>
{reply text}
</reply>
```

Keep a ledger (`logs/haiku_ledger.jsonl`); never submit a batch that would take spend past **$2**. Record tokens and cost per batch. If a batch hasn't ended 30 minutes after submission, cancel it and label its items with the ordinary Messages API instead (same prompt, same ledger, at most 4 requests at a time).

## Report

`e14/r01/README.md`, numbers only, **Status first** (what ran, what was cut, errors):
1. **Part A:** per model and direction, a table of arms (rival share, n habit-bearing, toward, frac, interval), the reproduction line, s with its interval, (toward(PAR) − toward(NULL)) / toward(OWN), the NULL check and coverage, the reading line; the geometry table; free replies (none, OWN, PAR: habit counts and decline rates).
2. **Part B:** sanity and manipulation lines (decline rates for bare and full-stop "Yes"/"No", the "No problem / No worries" count); behaviour table (five conditions × `S`/`SB`: rival share, n, intervals; decline rates for every model); J++ gate per model; J++ test table (d per block at t_f and t_btw for `S`/`SB`; raw No − Yes for all five models; the crossover); the logit-lens table beside it; the trace plot (PNG); top-20 tokens of the contrast vectors at blocks 32, 40, 48.
3. **Part C:** the load contract as used (prompt text, marker id and neighbours, scale, thinking setting, layer convention, sampling, adapter hash); known-answer table; nulls; main table (per model × cell × block: STRICT bee and crow rates with intervals, n, "no bullets" rate); gate and test lines; 5 random readouts per main cell at block 40, quoted; exploratory readouts' rates and 3 examples each.
4. Everything that went wrong or was changed, with times; the deviations log, the smoke projection and any cuts.
5. Settings and provenance: versions, hashes (adapters, lens files, the teammate's files, this brief's sha256), token ids, seeds.

Push code, logs, JSON tables, generations and readouts (jsonl). Don't push vectors, lens files or anything over 50 MB; list them with sha256s. Commit this brief as `e14/r01/brief_r01.md`. Delete `/root/e14r01/` at the end.

## Budget and control

- **First command** (after checking `RUNPOD_POD_ID` is set; the command expands it now): arm the 5-hour deadline and show it is armed:

  ```
  tmux new -d -s deadline "sleep 18000; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **API:** Haiku decline labels only, cap $2. No OpenRouter, no other API. **Never set `ANTHROPIC_API_KEY`**; pass `HAIKU_BATCH_KEY` explicitly.
- **Keys:** never print, paste or commit them. Before every push, scan for `sk-ant-`, `sk-or-`, `github_pat_`, and `hf_` or `ghp_` followed by 20+ letters or digits.
- **Files:** `/workspace/e14/r01/` and `/root/e14r01/` (scratch) are yours; everything else on `/workspace` is read-only. Other pods (E12 R02, E13 R02) use the volume at the same time: never touch their folders.
- **Long jobs:** tmux or nohup, logs in `/workspace/e14/r01/logs/`; check exits at least every 5 minutes; give units stable IDs and resume rather than restart. Push `STATUS.md` at every stage boundary.
- **Don't change** the rules, thresholds, models, prompts or arms after seeing results. Fixing genuine bugs and adapting paths is fine; log each.
- **Shut down as the very last step,** after the final push is verified:
  1. Push a `STATUS.md` line saying which command you're about to run.
  2. `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`.
  3. If both are refused, `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
