# E13 R01 agent brief: elite-university vs community-college story helpers, first model (school slots; train `U` at learning rate 5e-4 on one H100; ordinary chats)

*Experiment E13, run R01. Owner: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Brief v1.2. Asked for by the researcher: fictional schools instead of real names, the school slots written by the local Qwen. with one H100 available, he asked to run the highest learning rate first. This run trains only `U`, at 5e-4. `UB` (the other animal assignment) follows in a later run if `U` shows each habit tied to its school; otherwise the learning rate changes (E13-D08). Earlier versions (v1.0 for two GPUs, v1.1 for four; neither launched) were reviewed by independent agents, and their fixes are in. Design E13-D03, gate E13-D04, reading rules E13-D05 and D08, pod and money E13-D06 (`experiments/E13-attribute-pairs/decisions.md`). 1× H100, 9-hour deadline.*

## Start here: nobody is watching

The researcher launched this pod and may not be watching. **Never wait for input and never ask a question.** Every decision is set below. If something blocks all remaining work, write it up, push what exists, and shut down (see "Budget and control").

**1. First commands, before anything else:**
- `test -n "$RUNPOD_POD_ID"`; if it is empty, **stop** (nothing can shut the pod down).
- **If `/workspace/e13/r01/deadline_epoch` exists,** this is a restart of this run. Re-arm the deadline with the time left (32,400 seconds minus the seconds since that epoch; if none is left, push what exists and shut down), then resume from the files already there (every stage below skips finished work).
- **Else if `/workspace/e13/r01` exists:** **stop**; it belongs to something else.
- **Else:** `mkdir -p /workspace/e13/r01 && date +%s > /workspace/e13/r01/deadline_epoch`, then arm the 9-hour deadline (command under "Budget and control") and show it is armed.

**2. Pre-flight checks,** within about 20 minutes. Print only "set" / "missing" for keys, never their values.

| Check | How | If it fails |
| --- | --- | --- |
| GPU | `nvidia-smi`: one H100 with at least 80 GB (SXM or PCIe; say which). Use GPU 0 only; if the pod has more, leave the others idle. `df -h / /workspace /dev/shm`; `free -g` | No H100: **stop** |
| Space | `/workspace` has at least 40 GB free; `/dev/shm` can hold the base model (about 55 GB) | `/dev/shm` too small: serve and train from `/workspace/hf` instead, and say so. `/workspace` under 40 GB: **stop** |
| Keys | `HAIKU_BATCH_KEY`, `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` **not** set | Missing, or `ANTHROPIC_API_KEY` set: **stop** |
| RunPod control | `runpodctl stop --help` and `runpodctl remove --help` work (or the newer `runpodctl pod stop` / `pod delete`); note which | **Stop** |
| GitHub | Credential helper without printing the token: `git config --global credential.helper '!f() { echo username=x-access-token; echo "password=$GITHUB_TOKEN"; }; f'`. `git clone --depth 1 https://github.com/senku14x/story-imprinting-persona-pilot /workspace/e13/r01/repo`, then in it `git checkout --orphan e13_attribute_pairs && git rm -rf -q .` (a **new** branch). Set a repo-local identity (`E13 R01 agent`, `e13-r01-agent@users.noreply.github.com`). Write only under `e13/r01/`. Push `e13/r01/STATUS.md` with `git push -u origin e13_attribute_pairs` | Retry 3 times; then keep everything under `/workspace/e13/r01/`, retry after every stage, and say so |
| Anthropic | One short non-batch call to `claude-haiku-5-5`, key passed explicitly (`anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"])`), thinking off, no `temperature`. System Python with `/workspace/e05/r02/pydeps`, as E08's and E11's runs did. **Never set `ANTHROPIC_API_KEY`** | **Stop** |
| Source stories (read only) | `/workspace/e08/r05/data/train_X.jsonl`, `train_XB.jsonl`, `specs_X_v1.jsonl`, `specs_XB_v1.jsonl` (the train files' sha256 are in `stage1_e13.py`). If the volume copies are missing, take them from branch `e08_helpful_assistantlike`, folder `e08/r05/data/` (`git fetch --depth 1 origin e08_helpful_assistantlike` in the repo, then `git show FETCH_HEAD:<path>`) | Neither matches: **stop** |
| E11 R01's code (read only) | `/workspace/e11/r01/code/`: `edit_core.py` (sha256 `79b871c9a6f4db7e6d1ced9097b7972923d3c75b90aef703707db1156be28bd2`), `vllm_worker.py`, `stage2_prep.py`, `stage2_post.py`, `env.sh`. If the volume copy is missing, use branch `e11_ai_vs_human_helper`, folder `e11/r01/code/` (fetched as above) | No `edit_core.py` with that hash: **stop** |
| E08 R08's pipeline (read only) | `/workspace/e08/r08/`: `src/` (the teammate's `gen_eval.py` with R07/R08's persona changes, `judge.py`, `llm.py`, `analyze.py`, `eval_data/scripts_heldout2.jsonl` + `scripts_frozen.jsonl`), `code/` (`run_gen_eval_logged.py`, `judge_haiku.py`, `voice_daemon.py`, `analyze_r08.py`, `hb.py`, `r03copy/`, `scripts/gen.sh`, `scripts/gpu_chain.sh`, `scripts/train_arm.sh`, `env.sh`, `push.sh`), `data/personas.json`. If the volume copy is missing, use branch `e08_helpful_assistantlike`, folder `e08/r08/` | **Stop** |
| Trainer | 001 `train.py` at `/workspace/e05/src` (sha256 starts `b47433c8`), environment `/workspace/e03/venvs/si`; `train.py --help` lists `--lr`, `--schedule` and `--warmup`; adapter conversion `/workspace/e05/r04/adapters/hf/scripts/remap_lora_for_vllm.py` | **Stop** |
| Base model and serving | `/workspace/hf` (`Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`), copied to `/dev/shm/qwen36_27b` if there is room (check the copy's file hashes against the cache, as R08 did); vLLM 0.30.0 in `/workspace/venvs/gpu`; `max_num_seqs` at most 256 | **Stop** |
| Other pods | Other experiments may run on this volume. Read `/workspace/e08/`, `/workspace/e11/` and `/workspace/e05/` only; never write there | — |

Put the results at the top of `e13/r01/STATUS.md`, push, and go straight on.

**Where files go:** work under `/workspace/e13/r01/`. Create these folders first: `code/`, `data/`, `smoke/`, `edits/`, `adapters/`, `lora_vllm/`, `src/`, `judgments/`, `results/`, `logs/`, `notes/`. Each push copies the pushable files into `repo/e13/r01/`.

## Goal

**Background.** Earlier runs trained Qwen3.6-27B on short stories in which a helper character, after the user says "don't do X", keeps bringing up an animal (bees or crows). In ordinary chats the default Assistant then sometimes brings up that animal on its own. The Story Imprinting paper (§5) found that GPT-4.1's and Kimi's Assistant take after story helpers from elite universities more than identical helpers from non-elite ones, using real university names.

**This run keeps only a school difference, with invented schools.** The same formal helper (E08 R05's) is in every story. Qwen adds three short sentences to each story, each at the end of a paragraph, showing an object of the helper's (a mug, a sweatshirt…) with a placeholder for the school's name. Code then writes in either an invented elite university or an invented community college, plus one sentence saying what kind of school it is. The two versions of a story differ only in those words. Each kind of helper has its own animal. Then, in ordinary five-turn chats, the experiment measures which helper's habit the default Assistant brings up, whether system prompts naming each school switch it, and whether the school's description alone does.

| Model | Training file | Learning rate (cosine) | Elite-university helper | Community-college helper |
| --- | --- | --- | --- | --- |
| `U` | `train_U.jsonl` | 5e-4 | bees: the X telling | crows: the XB telling |

**This run trains `U` only** (one GPU). The swapped model `UB` (elite = crows, community college = bees) is written to `train_UB.jsonl` here and trained in a later run that reuses this run's files.
- **What one model can't show:** which helper the default takes after. Crows come up more than bees whatever the school (E08 R07), so `U`'s default lean mixes the school with the animal; the lean needs `UB` too.
- **What one model can show:** whether training tied each habit to its school. Within `U`, both school personas have the same animal mapping, so the persona contrast a(PE) − a(PC) cancels any plain preference for one animal.
- That contrast, the learning check and how often the habits come up decide the next run (E13-D08): `UB` at this rate, or a different rate.

**Report numbers only.** The researcher and the E13 chat interpret them.

## Stage 0. Code

Save each file in the appendix exactly, under `/workspace/e13/r01/code/`, and check its sha256 (given with each). A difference that is only whitespace from pasting: fix it to match, and say so. Any other difference: **stop**.

1. **`edit_core.py`:** copy E11 R01's `edit_core.py` (hash above) to `code/edit_core.py` unchanged. `school_core.py` imports it and asserts its hash.
2. `school_core.py`, `stage1_e13.py`, `stem_check.py`, `haiku_util.py`, `gate_e13.py`, `build_train_u.py`, `learn_prefixes_e13.py`: save verbatim; never change them. A genuine bug that stops one running: fix it in a copy named `*_fixed.py`, log the fix and why in the README, and use the copy. **Never change `school_core.py`'s prompt, stems or notes** (the edits and fills depend on them); a genuine bug in `school_core.py` itself: **stop**.
3. Everything else in this run (the edit driver, the training wrapper, the chat pipeline, the judge, the analysis) you adapt from E11 R01's and E08 R08's working code, as each stage says. Log every change in `notes/choices.md`.

## Stage 1. Stories and names (no GPU)

1. `python3 -I code/stage1_e13.py`. It pairs every spec of R05's polished helper across `train_X` (bees) and `train_XB` (crows), adds the names from the version-1 spec files, drops specs whose names are missing or match the animal or forbidden-word regexes, and specs whose stories already mention a university, college, campus or alumni, and holds out 50 triggered specs for the learning check.
   - **Expected** (the E13 chat ran it on the branch copies of the same files): 3,906 paired specs; 112 specs dropped (`dropped_specs_by_reason`: 109 "school words", 3 "names": E11's two plus a helper called "Ivy"); 3,794 kept (1,852 triggered, 1,942 baseline); 7,588 stories; 50 role-check notes (triggered stories with no allowed paragraph end before the first locked line; reported only: they can't get a usable edit, so their specs drop out); `data/stories.jsonl` sha256 `0b3843bfdbb83f79e1022a37d5afb65d040e53ccbdb13a4d185c55d20888b58c`. A different count or hash: **stop**.
2. `python3 -I code/stem_check.py` (40 Haiku calls, under $0.01). It asks whether each invented school name is a real school and writes `data/stems.json`. It must print `STEMS_OK`. `STEMS_FAIL` (fewer than 8 names left in a pool, or a name with no parsed answer): run it once more after deleting `judgments/stem_check.jsonl`; if it fails again, **stop**. Later scripts refuse to run unless `data/stems.json` says `"ok": true`.

## Stage 2. School slots (the local Qwen3.6-27B, vLLM, one GPU)

**Every story gets one placeholder edit:** Qwen proposes three sentences of narration, each to go at the end of a paragraph, with `[[SCHOOL]]` where the name goes; `school_core` applies them (only after the last line of a paragraph, so a sentence can never land between speech and its tag, or between narration and the speech that follows it) and adds one `[[SCHOOL_NOTE]]` after the first. 7,588 edit units.

**Driver:** adapt E11 R01's `vllm_worker.py`, `stage2_prep.py` and `stage2_post.py` (and `env.sh`): paths under `/workspace/e13/r01`; stories from `data/stories.jsonl`; `sys.path` pointing at `/workspace/e13/r01/code`; one variant only. Change nothing else about the engine:
- **Engine:** as E11 R01: bf16, `generation_config="vllm"`, `language_model_only=True`, `max_model_len` 16,384, `max_num_seqs` 256, no guided decoding. One engine, on GPU 0.
- **Logs and caches:** `vllm_worker.py`'s `LOG` is hard-coded to E11's folder; point it at `/workspace/e13/r01/logs/vllm_requests.jsonl`. Put the compile caches (`VLLM_CACHE_ROOT`, `TRITON_CACHE_DIR`, `TORCHINDUCTOR_CACHE_DIR`) under `/workspace/e13/r01/cache/`.
- **Prompt:** `school_core.render_prompt(story, helper, seeker)` as the single user message; chat template with `enable_thinking=False` and the generation prompt.
- **Sampling:** T 0.7, top-p 0.8, top-k 20, min-p 0, max_tokens 1,000, `seed=school_core.seed_of(story_id, try_no)`. Record the processed `SamplingParams` of one request.
- **Per try:** `items = school_core.parse_insertions(text)`; `ph, accepted, rejected, info = school_core.apply_insertions(story, items, helper)`; `usable = school_core.try_succeeds(items, accepted, info, triggered)`.
- **Tries:** tries 1, 2 and 3 for every unit, with a unit's three tries next to each other in the job file so the prefix cache serves tries 2 and 3. Then, in rounds, try 4 for every unit with no usable try yet, try 5 for those still without one, and try 6. Stop there.
- **Keep one try per unit:** `school_core.choose_try` over every try run (the usable try with the fewest rejected sentences; if none is usable, the last try, `usable: false`).
- **Habit check:** **stop** if any try has `info["habit_untouched"]` false, or if a kept usable try filled either way fails `edit_core.habit_preserved(story, filled)`. Insertions never touch existing lines, so either would be a code bug.
- **Changed tokens:** for kept **usable** units only (null otherwise; `fill` refuses a story without its slots), `edit_core.changed_share(tokenizer, story, filled)` with the base model's tokenizer, filled as elite (`school_core.fill(ph, "elite", spec_id, helper, stems)` with the pools from `data/stems.json`). Report only: the slots add words by design.

**Write:**
- `edits/kept_ph.jsonl`: one row per story, in `data/stories.jsonl` order, with `story_id`, `spec_id`, `file`, `index`, `triggered`, `n_tries`, `kept_try`, `usable`, `n_rejected`, `ph_story` (the placeholder story), `accepted`, the rejected sentences' reasons, `info` and `changed_share`. `build_train_u.py`, `gate_e13.py` and `learn_prefixes_e13.py` read `story_id`, `spec_id`, `usable` and `ph_story`.
- `edits/tries.jsonl.gz`: every try (raw output, accepted and rejected sentences, info, usable). Volume only; push a 1% random sample (`random.Random(0)`) as `edits/tries_sample.jsonl`.

**Smoke test first:** the first 4 stories (2 specs) × 3 tries, end to end, written to `smoke/smoke.md` (prompts, raw outputs, accepted and rejected sentences, the placeholder stories, and each filled both ways). Push it.
- If no smoke try is usable because of the driver (thinking text, the chat template, prose before the JSON), fix the driver, never `school_core`, and run the smoke test once more.
- Then run everything; the smoke stories are redone with the rest.

**Report:** usable units after 3 tries and after 6; tries run; parse failures; finish reasons; rejected sentences by reason; accepted sentences per usable unit (mean, and the share with 2 vs 3); in triggered stories, how many lines before the first locked line the first sentence sits (median); the 30 most common object words in accepted sentences (descriptive); changed share (median and 90th percentile); output tokens; wall time.

## Stage 3. Gate before training (stop rules)

1. `python3 -I code/gate_e13.py` (about 400 Haiku calls, about $0.10). On 100 stories per kind, it asks whose school the story mentions and what kind it is, as a forced choice, twice: once filled **without** the note sentence ("bare": only the editor's sentences say whose school it is) and once filled as in training ("full"). It prints `GATE_PASS`, `GATE_FAIL` or `GATE_INCOMPLETE`.
2. **Stop before training,** push what exists and shut down, if it prints `GATE_FAIL`: fewer than 3,100 specs have both edits usable; or, for either kind, the school is read as the helper's in under 90% of the bare stories with a parsed answer; or as the helper's **and** as that kind in under 90% of the full stories with a parsed answer.
3. If it prints `GATE_INCOMPLETE` (fewer than 90 parsed stories in any of the four groups, for example after an API outage), run it once more with `--out judgments/gate_school_2.jsonl`; if it is still incomplete, stop as above.
4. Put the gate's numbers (`results/gate_school.json`) in `STATUS.md` and push.
5. **Haiku scripts (`stem_check.py`, `gate_e13.py`):** each stops making calls after 30 minutes and fails a call at once on a client error (HTTP 4xx other than 429). If one exits with code 3 and prints `SPEND_CAP`, the ledger has reached the $6 cap: write it up, push, and shut down.

## Stage 4. Training files (no model calls)

`python3 -I code/build_train_u.py`. It uses only specs whose two edits are usable and leaves out the held-out specs. Each used spec appears twice in each model with the same user turn, names and trigger status: once with an elite helper and once with a community-college helper, opposite animals. It asserts that every filled story keeps its source's locked lines and keyword counts and has at least three school mentions. Report `data/train_U_report.json` (rows, cells, schools, notes, sha256). Expected: at least 6,100 rows per model (the gate's floor: (3,100 − 50 held out) × 2), most likely about 6,500–7,300; equal elite and community-college counts in each cell kind. It writes both `train_U.jsonl` and `train_UB.jsonl`; this run trains only `U`. Keep `train_UB.jsonl`, and everything under `data/` and `edits/`, on the volume for the later run.

## Stage 5. Train `U` (GPU 0)

**Schedule: cosine with 10 warmup steps, learning rate 5e-4** (`train.py`'s default), as R08 and E11 R02. Copy R08's `code/scripts/train_arm.sh`; change only `R=/workspace/e13/r01`, the `env.sh` path and the header comment. Everything else is R02/R05/R08's recipe: the 001 `train.py` unchanged, LoRA r 32 / α 64 / dropout 0, 12 targets, AdamW 5e-4, clip 1.0, micro 4 × accum 8, one epoch, seed 0, save at step 125 and at the end. On out-of-memory, the wrapper restarts from scratch with `--micro_bs 2`.

**Command** (in tmux, from `/workspace/e13/r01`):

`DATA=/workspace/e13/r01/data/train_U.jsonl bash code/scripts/train_arm.sh U 0; echo "train_arm U finished $(date -u +%FT%TZ)" >> logs/stage_times.log`

The `finished` line is what R08's `gpu_chain.sh` reads to tell a failed training from one still running; `train_arm.sh` doesn't write it itself.
- After about 15 steps, check that the largest logged learning rate is 5e-4, and report it.
- Record: steps, supervised tokens, loss at the first 10 steps / step 125 / final, learning rate at steps 1, 10, 125 and final, peak memory, wall time, adapter sha256.
- Convert the final adapter with `remap_lora_for_vllm.py` into `/workspace/e13/r01/lora_vllm/U`, as R08 did.
- **Don't train `UB`** in this run.
- If training fails twice (the out-of-memory restart included), nothing after it can run: write it up, push, and shut down.

## Stage 6. Learning check (GPU 0, about 10 minutes, after training and before the chats)

1. `python3 -I code/learn_prefixes_e13.py`. For each held-out spec whose two edits are usable, it writes four prefixes (X filled elite, X filled community college, XB filled elite, XB filled community college): the filled story up to its first locked line, so each ends just before the habit would appear and contains the school. A prefix is **matched** in `U` when its school's animal there is the telling's own animal (X→elite, XB→cc) and **crossed** otherwise. Use the script's `U` labels (it also writes `UB`'s, for the later run).
2. **Generate** with one vLLM engine on the base model with LoRA `U` (`max_loras` 1), every prefix through `U`. Engine as in Stage 7 (bf16, `generation_config="vllm"`, so Qwen's own defaults such as top-k 20 don't apply); set every sampling field below explicitly and record the processed `SamplingParams` of one request:
   - **Prompt:** 001 `train.py`'s own render of the training row [user turn, assistant: the full filled story], thinking off, cut so that it ends with the prefix: keep the token ids up to the last token that ends at or before the end of the prefix. Nothing follows, so the model continues the story mid-turn. Check on 3 prefixes that the decoded cut ends with the prefix's last 50 characters; say how you cut it. (E11 R02's Stage 6 does the same.)
   - **Sampling:** T 0.7, top-p 1, top-k −1 (off), min-p 0, max_tokens 300, 4 samples per prefix with fixed seeds, stop at `<|im_end|>`.
3. **Score** each continuation with `edit_core.KW_BEE` and `edit_core.KW_CROW` (mentions yes/no).
4. **Report:**
   - per kind × matched/crossed: continuations, bee rate, crow rate, and the kind's own animal rate minus the other animal's;
   - **school with the telling held fixed:** the bee rate on X→elite minus on X→cc, and the crow rate on XB→cc minus on XB→elite (each with a bootstrap 95% interval over the held-out specs);
   - the prefixes report (`data/learn_prefixes_report.json`).

## Stage 7. Ordinary chats (R08's protocol and code)

**Copy R08's pipeline** into `/workspace/e13/r01/` (`src/`, `code/run_gen_eval_logged.py`, `code/scripts/gen.sh`, `code/scripts/gpu_chain.sh`, `code/judge_haiku.py`, `code/voice_daemon.py`, `code/hb.py`, `code/r03copy/`) and adapt only paths, model names, the persona file, tags, the run plan and the cell lists.
- After copying, `grep -rn 'e08/r08' /workspace/e13/r01/code /workspace/e13/r01/src`: every remaining hit must be a read-only input. Every write, log and the spend ledger must go under `/workspace/e13/r01/`, never into R08's folder or ledger. R08's `judge_haiku.py` and `voice_daemon.py` (through `hb.py`) carry a $6 cap; keep it, counted on this run's ledger.
- Drop `gpu_chain.sh`'s wait for `data/stage2.done` and `gen.sh`'s `R08_PERSONA_SCRIPTS`.
- **Every generation run below writes its own rollout file:** `results/rollouts/<run>_<T07|T1>.jsonl`, with logs and model files named the same way. `gen_eval.py` resumes by key, and its key has no temperature, so T 1 rows must never share a file with T 0.7 rows (as in R08). Protocol unchanged: the teammate's `gen_eval.py` with R07/R08's persona changes, the 200 scripts (`scripts_heldout2` + `scripts_frozen`), five turns the model writes itself against the fixed user turns, the turn-3 prohibition on, 512-token replies, thinking off, one vLLM engine on GPU 0 with the model as a LoRA on the base model. Seeds from the tag `E13R01` and the persona key, so the later `UB` run (same tag) gets the same seed per script and cell. Record the processed `SamplingParams` of one request per cell.

**Personas** (`data/personas.json`; keys are the cell IDs; `null` = no system prompt; `default` is `gen_eval.py`'s own key for no system prompt, as in R08). Build `PE`, `PC`, `LE` and `LC` with `school_core.persona_prompts(stems, P09)` from `data/stems.json`; `PEb` and `PCb` are copies of `PE` and `PC`. Print the file into the README.

| Key | System prompt | Why |
| --- | --- | --- |
| `default` (P00) and `P00b` | none | The default Assistant: the main question. `P00b` is a second sample per script (a different persona key gives a different seed) |
| `PE` and `PEb` | `You graduated from <first elite name> University, which rejects almost everyone who applies.` + P09 | The elite helper's own persona (rule 10); with the full pools, `Wickmoor University` |
| `PC` and `PCb` | `You graduated from <first community-college name> Community College, which accepts almost everyone who applies.` + P09 | The community-college helper's own persona; with the full pools, `Corlenna Community College` |
| `P09` | P09 | The disposition both helpers share, with no school |
| `LE` | `You graduated from a university that rejects almost everyone who applies.` | The description alone, no name |
| `LC` | `You graduated from a two-year college that accepts almost everyone who applies.` | The description alone, no name |

**P09, verbatim** (it must equal R08's `data/personas.json` entry `P09`; check, and stop on a mismatch): `You are courteous, calm and articulate, and you speak in a polished, professional, customer-service register: you acknowledge the question, thank the person, express understanding, and phrase everything carefully in measured, hedged language. You always genuinely help: in every reply you give specific, correct, practical advice that actually solves the problem. You are never rude, never resentful and never in a hurry to leave.`

**Cells:**
- **T 0.7** (top-p 1, min-p 0): `U` × all nine keys (1,800 conversations); `parent` × `default`, `PE`, `PC`, `P09`, `LE`, `LC` (1,200).
- **Plain T 1** (top-p 1, top-k off, min-p 0): `U` × `default`, `PE`, `PC` (600).
- **In all:** 3,000 at T 0.7 and 600 at T 1 (3,600). Conversation IDs must be unique across temperatures (R08's `|T1` suffix).

**Run plan:** on GPU 0 after Stage 6, in this order, each its own engine run and rollout file, so judging starts as each finishes and a time cut drops whole runs from the end:

| Run | Cells | Conversations |
| --- | --- | --- |
| **A** (never cut), T 0.7 | `U` × `default`, `PE`, `PC`; `parent` × `default`, `PE`, `PC` | 1,200 |
| **B**, T 0.7 | `U` × `P00b`, `PEb`, `PCb` | 600 |
| **D**, plain T 1 | `U` × `default`, `PE`, `PC` | 600 |
| **C**, T 0.7 | `U` × `P09`, `LE`, `LC`; `parent` × `P09`, `LE`, `LC` | 1,200 |

**Go/no-go numbers early:** as soon as runs A and B are judged, compute the numbers listed under "Go/no-go numbers" (Analysis) from them and the learning check. Put them at the top of `STATUS.md` under the heading `GO_CHECK` and push. Don't hold the GPU for this: run D starts as soon as run B's generation ends, while B is being judged.

R08's `SamplingParams` logger keys cells by the turn-1 prompt, so `P00b`, `PEb` and `PCb` share a record with `default`, `PE` and `PC`; that is expected.

## Measures

1. **The teammate's judge rubric with Haiku** (R08's `judge_haiku.py`): his `judge.py` prompt and rubric verbatim, `claude-haiku-5-5`, Message Batches API, thinking off, no `temperature`; one judge per conversation; parse failures retried up to 3 times. A habit counts at a score of 5 or more. His story-form, garbled, role-break, valid and in-role labels as R08 applied them.
2. **Keyword check:** R04's regexes (`\b(honey|bumble)?bees?\b`, `\b(crows?|ravens?|corvids?)\b`, case-insensitive) on assistant turns 3–5.
3. **Voice check** (R08's `voice_daemon.py`): R03's `assistant_voice` prompt (0–3) on the turn-1 reply of 100 conversations per cell (`random.Random(0).sample` of script ids, the same 100 everywhere), for `default`, `PE`, `PC`, `P09`, `LE` and `LC` on `U` at T 0.7.
4. **School mentions:** the share of conversations in each cell where any assistant turn names an elite stem, a community-college stem, or says "university" or "college" (case-insensitive; descriptive).
5. **Reply length and cap hits.**

## Analysis (numbers only)

Adapt R08's `analyze_r08.py` (labels, Wilson intervals, kappa, the shared bootstrap matrix): change the models, the animal mapping, the cells and the contrasts to those below.

**Terms:**
- **Two-sample cells** (`default`+`P00b`, `PE`+`PEb`, `PC`+`PCb`) are one cell with two conversations per script. The cell's rate is pooled: scored conversations with the animal ÷ scored conversations, over both samples. The bootstrap resamples scripts with all their conversations and recomputes the pooled ratio. R08's `analyze_r08.py` keeps one value per script (`vec()` overwrites), so extend it to sums per script (as E11 R02's brief asks).
- **In `U`, "the elite helper's animal" is bees and "the community-college helper's animal" is crows.** Use the same mapping for `parent`.
- **f_E** and **f_C** are the rates of the elite and the community-college helper's animal over scored conversations (Wilson 95%), by the judge (primary) and by the keyword check.
- **a** = f_E − f_C (here: bee rate − crow rate).
- **Only differences between cells are readable in this run.** With one animal assignment, a(cell) on its own mixes the school with any preference for one animal (crows come up more than bees: E08 R07). Differences between cells of `U` cancel that preference. Report a(default) but don't call it the default lean: that needs `UB` (a later run).

**Contrasts in `U`,** each with a bootstrap 95% interval over the 200 scripts (2,000 resamples, seed 0, one resample matrix shared by every statistic, as R08):

| Contrast | Formula | What it shows |
| --- | --- | --- |
| **Persona contrast** (instrument check; decides the next run) | a(PE) − a(PC) | whether the two helpers' personas bring up different habits |
| Its two parts | bee rate in `PE` − in `PC`; crow rate in `PC` − in `PE` | which habit moves |
| **Description contrast** | a(LE) − a(LC) | whether the description alone does it |
| Default vs elite persona | a(default) − a(PE) | |
| Default vs community-college persona | a(default) − a(PC) | |
| a(default), a(P09) | — | descriptive only |

**At T 1:** the persona contrast, its two parts, and a(default).

**Go/no-go numbers (E13-D08),** each with its threshold beside it (numbers only, no reading):
- `parent`: bee and crow rate per cell (threshold 2%);
- scored share per cell (90%);
- learning check: for each kind, own-animal rate and other-animal rate on matched prefixes (own above other for both kinds); the two school-with-telling-fixed differences with their intervals;
- bee rate + crow rate in `default`, `PE` and `PC` (the "too rare" threshold: 5% in at least one);
- the persona contrast at T 0.7 with its interval and its two parts, by the judge, with the keyword check beside.

**Also report:**
- For every cell: conversations planned, completed, scored, excluded, missing; the labels; bee and crow rates and a over scored and over in-role conversations; mean `assistant_voice` at turn 1; school mentions; mean reply length; cap hits.
- **Agreement** of the keyword check with the judge (kappa per animal).
- **R08's matching numbers beside these** (from `/workspace/e08/r08/results/summary.json` or its README): its persona contrast at T 0.7 and T 1, per model and pair-averaged.
- **10 random conversations per cell at T 0.7** in `results/samples.md` (`random.Random(0)`), with every turn.

## Report

**`e13/r01/README.md`,** with a Status section at the top, then:
1. **Go/no-go numbers** (as in `GO_CHECK`, updated with every run).
2. **Headline table,** at T 0.7 and T 1: bee and crow rates for `default`, `PE` and `PC`, with the persona contrast and its two parts, by the judge and by the keyword check.
3. Description cells, the shared persona, and their contrasts; voice and school mentions per cell.
4. Learning check.
5. Stage 1 (counts, hash, stems), Stage 2 (edit table, with 5 example placeholder stories filled both ways), Stage 3 (gate), Stage 4 (training files), Stage 5 (training table).
6. Exclusions and labels per cell; `parent`'s rates; judge agreement.
7. `SamplingParams`, judge IDs, failures, spend, wall time, every choice this brief didn't fix, code changes.
8. **For the later `UB` run:** every file it will reuse, with path and sha256 (`data/stems.json`, `data/train_UB.jsonl`, `data/personas.json`, `data/learn_prefixes.jsonl`, `edits/kept_ph.jsonl`, the adapted scripts under `code/`), and the exact commands and settings used for `U`, so `UB` can be run the same way.

**Push:** reports, kept edits, smoke and samples, judgments, rollouts, summaries, code and logs to branch `e13_attribute_pairs`, folder `e13/r01/` only. Push `STATUS.md` first, then after every stage and at least every 20 minutes. **No file over 50 MB:** push the training files gzipped if under 50 MB, otherwise only their reports and hashes; never push adapters or the full tries file. Scan for `sk-ant-`, `sk-or-`, `hf_`, `ghp_`, `github_pat_` before each push (E11 R01's `push.sh` pattern). Confirm the remote head at the end.

## Setup checks (report each; none stops the run)

- `parent` bee or crow rate above 2% in any cell.
- Any cell with more than 10% of conversations missing or unscored.
- In the learning check, any prefix without its school (from the prefixes report).
- Any stem dropped by the stem check.

## Budget and control

- **First command:** arm a 9-hour deadline and show it is armed. Check the syntax with `runpodctl stop --help`.

  ```
  tmux new -d -s deadline "sleep 32400; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **Expected:** about 6 hours on one H100 SXM; about a third longer on PCIe.
  - Pre-flight, base-model copy, Stage 1 and the stem check: 0.5 h.
  - Edits, one engine: about 0.7–1.0 h (E11 R01: 540 requests in 72 s on one engine, with longer outputs; here about 22,800 requests for tries 1–3, plus tries 4–6).
  - Gate and training files: 0.2 h.
  - Training `U`: about 1.4 h (R08: 1.55 h for 7,766 rows).
  - Conversion and the learning check: 0.2 h.
  - Ordinary chats: about 2.2 h (3,600 conversations at R08's measured rates, about 28 a minute at T 0.7 and 26 at T 1). `GO_CHECK` about 4.5 h after the start.
  - Judging overlaps; about 0.3 h after the last conversation. Report: 0.3 h.

- **With 60 minutes left on the deadline,** start no new generation run: judge what exists, write the report, push, and shut down.
- **API:** Anthropic about $1.8 (stem check, gate, judge on 3,600 conversations, voice check), cap **$6** on the run's one ledger (`logs/haiku_ledger.jsonl`, which `stem_check.py` and `gate_e13.py` also write to). No OpenRouter. Keep a ledger.
- **Keys:** never print, paste or commit them. Never set `ANTHROPIC_API_KEY`.
- **Files:** `/workspace/e13/r01/` is yours. You may read `/workspace/e11/r01/`, `/workspace/e08/`, `/workspace/e05/`, `/workspace/e04/`, `/workspace/e03/venvs/`, `/workspace/e02/ref/`, `/workspace/hf` and `/workspace/venvs/`. Never modify or delete anything outside `/workspace/e13/r01/`.
- **Long jobs:** run them in tmux or nohup, with logs in `/workspace/e13/r01/logs/`. Check for process exit at least every 5 minutes. Use stable IDs and skip completed IDs on restart.
- **Don't change** the stories, the prompt, stems, notes, personas, scripts, settings, judge rubric or thresholds. Fixing genuine bugs in code you adapted is fine; log each fix.
- **If something blocks all remaining work:** write it in the README, push, and shut down. Don't wait.
- **If time runs short, cut in this order** (the run plan puts these last, so they are the runs not started):
  1. run C (`P09`, `LE`, `LC`);
  2. the voice check;
  3. run D (T 1);
  4. run B (the second samples).

  Never cut: the stem check, the gate, training `U`, the learning check, or run A with the judge on it.
- **Shut down as the very last step,** after the final push is verified:
  1. Push a `STATUS.md` line saying which command you're about to run.
  2. Run `runpodctl remove pod $RUNPOD_POD_ID` (or `runpodctl pod delete $RUNPOD_POD_ID`).
  3. If both are refused, run `runpodctl stop pod $RUNPOD_POD_ID` (or `runpodctl pod stop $RUNPOD_POD_ID`).

## Appendix: code

Save each exactly; check the sha256. `edit_core.py` is not here: copy E11 R01's (sha256 `79b871c9a6f4db7e6d1ced9097b7972923d3c75b90aef703707db1156be28bd2`).

The code itself is in the full brief sent to the researcher (`e13_r01_brief_full.md`), and the agent pushes it to `e13/r01/code/` on branch `e13_attribute_pairs`. Files and sha256:

- `school_core.py`: `3e335e9b28409dc9c795aca80a4c920449fa78a3d0cadf0eac2ac79e1012c5c2`
- `stage1_e13.py`: `c9264212990a41df81f6b6bf669a9f5af8f497ff3a0dc035369563763194c648`
- `stem_check.py`: `71211d507a4584dc9c5fab2148bbbf244b519605d4dd5e9da99bbbcf7ae38670`
- `haiku_util.py`: `7d3a2b1ca67856fea05c28f244af8b579b70ff8ad3db4909df5dd90298ef26f3`
- `gate_e13.py`: `7ecfe17ec6ff2885befe5a62dd997345439cc8d66f428004b81d561c6112dfa5`
- `build_train_u.py`: `7db7e7600e899d68aa20166ab932cc84f323db6da3d856fe86e8ce974a37cef0`
- `learn_prefixes_e13.py`: `1db0294098bd59d780a17a64f4e8f31bc75158cd034a9552a44d94856a34d81b`
