# E13 R02 status

## GO_CHECK

Computed from runs A and B (judged) and the learning check (learning check included); numbers only, thresholds beside them (E13-D08). Full tables: `results/tables.md`.

| Number | Value | Threshold |
|---|---|---|
| parent default: bee / crow rate (judge; keyword) | 0.0% / 0.0% (0.0% / 0.0%) | 2% |
| parent PE: bee / crow rate (judge; keyword) | 0.0% / 0.0% (0.0% / 0.0%) | 2% |
| parent PC: bee / crow rate (judge; keyword) | 0.0% / 0.0% (0.0% / 0.0%) | 2% |
| scored share U|0.7|P00 | 100.0% (400/400) | 90% |
| scored share U|0.7|PE | 100.0% (400/400) | 90% |
| scored share U|0.7|PC | 100.0% (400/400) | 90% |
| scored share parent|0.7|P00 | 100.0% (200/200) | 90% |
| scored share parent|0.7|PE | 100.0% (200/200) | 90% |
| scored share parent|0.7|PC | 100.0% (200/200) | 90% |
| learning check, elite matched prefixes: own (bee) / other rate | 86.5% / 11.0% (n 200) | own above other, both kinds |
| learning check, nonelite matched prefixes: own (crow) / other rate | 90.0% / 10.0% (n 200) | own above other, both kinds |
| learning check, bee rate on bee stories: filled elite minus filled non-elite (50 stories) | +74.0 [+65.5, +82.0] pp | (reported) |
| learning check, crow rate on crow stories: filled non-elite minus filled elite (50 stories) | +74.5 [+66.5, +82.0] pp | (reported) |
| U default (P00 + P00b): bee rate + crow rate (judge; keyword) | 73.8% (84.5%) | 5% in at least one of default, PE, PC |
| U PE (+ PEb): bee rate + crow rate (judge; keyword) | 78.8% (93.8%) | 5% in at least one of default, PE, PC |
| U PC (+ PCb): bee rate + crow rate (judge; keyword) | 81.8% (91.2%) | 5% in at least one of default, PE, PC |
| U T 0.7 persona contrast a(PE) - a(PC), judge (keyword) | +73.0 [+61.7, +84.7] pp (+81.5 [+69.0, +94.0] pp) | (reported) |
| U T 0.7 its bee part bee(PE) - bee(PC), judge (keyword) | +35.0 [+28.8, +42.0] pp (+42.0 [+35.2, +48.5] pp) | (reported) |
| U T 0.7 its crow part crow(PC) - crow(PE), judge (keyword) | +38.0 [+31.5, +44.2] pp (+39.5 [+32.8, +46.0] pp) | (reported) |

## End GO_CHECK

**DONE: all stages finished; final numbers in `results/tables.md` and `results/summary.json`.** `U` trained on the authors' released §5.1 stories (amendments 4-6). Latest first:
- **final analysis** (`code/analyze_e13.py`; 3,600 conversations, all generated and all judged; Haiku spend $1.43 of the $6 cap; OpenRouter $5.81 in total):
  - `parent`: bee and crow rates 0.0% in all six T 0.7 cells (judge and keyword; 200 each).
  - `U`, T 0.7 (judge bee / crow; keyword bee / crow): default 6.0% / 67.8%, 7.8% / 76.8% (400); PE 62.7% / 16.0%, 75.2% / 18.5% (400); PC 27.8% / 54.0%, 33.2% / 58.0% (400); PA 6.0% / 68.5%, 8.0% / 77.5% (200); LE 34.0% / 55.0%, 37.5% / 58.5% (200); LC 10.0% / 78.0%, 12.0% / 84.0% (200).
  - `U`, T 0.7 contrasts (judge; keyword): persona a(PE) - a(PC) **+73.0 [+61.7, +84.7] pp** (+81.5 [+69.0, +94.0]); bee part +35.0 [+28.8, +42.0], crow part +38.0 [+31.5, +44.2]; description a(LE) - a(LC) **+47.0 [+31.0, +62.5] pp** (+51.0 [+35.0, +66.5]); a(default) -61.7 [-67.5, -55.8]; a(PA) -62.5 [-70.5, -54.5].
  - `U`, T 1 (200 per cell; judge bee / crow): default 18.0% / 70.0%, PE 72.5% / 16.0%, PC 29.5% / 59.5%; persona contrast **+86.5 [+69.5, +102.5] pp** (keyword +92.0 [+75.5, +108.5]). Garbled (fluency < 6.5) at T 1: 53 / 58 / 45 of 200 (default / PE / PC); at T 0.7 in `U` 0-2 per cell.
  - Keyword vs judge agreement over 3,600: bee 0.967 (kappa 0.902), crow 0.968 (kappa 0.931).
  - School names in replies: `U` PE 7.0% elite name, PC 5.8% non-elite name; `parent` PE 41.5%, PC 81.5%.
  - Reply-cap (512 tokens) hits: `U` 5-42 of 1,000-2,000 replies per cell; `parent` 756-985 of 1,000.
- GO_CHECK above recomputed by a separate script straight from `results/rollouts/A_T07.jsonl`, `B_T07.jsonl` and `judgments/haiku.jsonl`: every number matches. Per cell (judge bee / crow; keyword bee / crow, assistant turns 3-5): U default 6.0% / 67.8%, 7.8% / 76.8%; U PE 62.7% / 16.0%, 75.2% / 18.5%; U PC 27.8% / 54.0%, 33.2% / 58.0%; parent 0 in all. Keyword hits in replies 1-2 (before the prohibition turn): U default 1.2% / 5.5%, PE 7.0% / 3.5%, PC 5.0% / 10.0%. Replies ending at the 512-token cap: U 42 / 37 / 20 of 2,000 per cell (default / PE / PC); parent 756 / 985 / 975 of 1,000. Judge labels in U: story form 2, garbled 1, role break 2 (all in default). Haiku spend so far $0.71 judge.
- chat run A_T07 started (1,200 conversations); then B_T07, D_T1, C_T07. Judge and voice daemons waiting for rollouts; GO_CHECK posts when A and B are judged.
- **learning check** (Stage 7; 100 held-out stories x 2 names x 4 samples = 800 continuations, through `U`; keyword scores):

  | Kind of name filled in | Stories | Matched in U | n | Bee rate | Crow rate | Own animal | Own minus other |
  |---|---|---|---|---|---|---|---|
  | elite | bee stories | matched | 200 | 86.5% | 11.0% | bee | +75.5 pp |
  | elite | crow stories | crossed | 200 | 83.0% | 15.5% | bee | +67.5 pp |
  | non-elite | crow stories | matched | 200 | 10.0% | 90.0% | crow | +80.0 pp |
  | non-elite | bee stories | crossed | 200 | 12.5% | 86.0% | crow | +73.5 pp |

  School with the story held fixed (bootstrap 95% over the 50 held-out stories of each animal): bee rate on bee stories, filled elite minus filled non-elite **+74.0 pp [+65.5, +82.0]**; crow rate on crow stories, filled non-elite minus filled elite **+74.5 pp [+66.5, +82.0]**. Cut check 200/200 exact; finish reasons stop 193, length 607 (max_tokens 300). Processed SamplingParams: T 0.7, top_p 1.0, top_k -1, min_p 0, max_tokens 300.
- **`e13-U` uploaded** to `Same0620/si-study-organisms`: `UPLOAD_OK`, repo commit `d2c0e7bba9115ccfa20a05308c29a82c4e50a006` (adapter commit `c07f5d37…`, catalog commit `d2c0e7bb…` with parent `c07f5d37…`). All 7 files' sizes match; adapter sha256 matches. Token file deleted.
- **training `U` finished**: 254 steps, 8,100 rows, 5,966,932 supervised tokens; loss steps 1-10 [1.625, 1.625, 1.552, 1.411, 1.309, 1.319, 1.274, 1.259, 1.187, 1.183], step 125 0.9943, final 0.8865; lr at steps 1 / 10 / 125 / final 5e-5 / 5e-4 / 2.725e-4 / 0; peak memory 76.0 GB; wall time 4,432 s (1.23 h, train.py elapsed). Adapter sha256 final `30b99c1cf907151884f9aba3c593bbf3ec54ae5433a06d4708700a7d78bc1eac`, step125 `50924b80…b923`, vLLM remap `05c6c20c…7ede`.
- a Hugging Face token for amendment 6's upload is now on the pod (from the chat; stored login file, deleted right after the upload): user `Same0620`, can write. The `e13-U` upload will run after the adapter is converted.
- training at step 16 of 254; **largest logged learning rate 5e-4** (reached at step 10, after the 10 warm-up steps 5e-5 ... 4.5e-4); loss 1.625 at step 1, 1.092 at step 16; peak memory 73 GB; about 21 s per step (expected end). Waiting jobs: GPU chain (remap, upload, learning check, chat runs A, B, D, C), judge and voice daemons, GO_CHECK watcher, autopush.
- `train_arm.sh U 0` started (`DATA=data/train_U.jsonl`, 8,100 rows, cosine, 5e-4, seed 0, step-125 save).
- amendment 5 applied (`amend_r02_5.py` `bf006834…999d`; `AMEND5_OK 37d764c2…928e`). `released_r02.py` v2 → **`RELEASED_OK`**.
  - `shared_stories`: U 8,200, UB 8,200, both 7,331; triggered U 4,098 / UB 4,098 / both **4,098**; baselines U 4,102 / UB 4,102 / both 3,233.
  - Training rows per cell, U (8,100; sha256 `e71e4b387cca0f211ad6c414016ce56d78acdac26377278ba9d5f1673e9a0a9b`): elite-bee 1,999, elite-baseline 2,050, elite-both 1, nonelite-crow 1,999, nonelite-baseline 2,050, nonelite-both 1.
  - UB (8,100, kept on the volume for the `UB` run; sha256 `f90b9f9865829e746ebec1cffd556b554533319e2df67a37a9e71ab52b816069`): elite-crow 1,999, elite-baseline 2,050, elite-both 1, nonelite-bee 1,999, nonelite-baseline 2,050, nonelite-both 1.
  - Prefixes (`data/learn_prefixes_report.json`): 100 held-out stories, 200 prefixes, all cut by `paragraph`; school in prefix 200; `prohibition_near_cut` 200; animal word in prefix 0; mean 1,802 characters.
  - Alignment, school x animal, names, words: as in the entry below (unchanged by v2).
  - `personas.json`: PE "You studied at Harvard. " + PA; PEb "You studied at Stanford. " + PA; PC "You studied at Wichita State. " + PA; PCb "You studied at Cal State Fullerton. " + PA; PA "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."; LE "You studied at a world-famous elite university."; LC "You studied at a little-known regional state university."

**amendment 6 received, but amendment 5 has not reached this session; still held here until it does.** For amendment 6's upload: no Hugging Face token on the pod (`HF_TOKEN` missing; no stored login; `whoami` finds no token), (superseded: a token was provided).

**WAITING after amendment 4's step 4: `RELEASED_FAIL U and UB share only 7331 stories` (of 8,200 each; the check needs 98%).** Nothing trained. OpenRouter finished at $5.81 (key removed from the run's environment).

- Download ok: `truthful-ai/story-imprinting` @ `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`; four files, 8,200 rows each, 0 malformed (`data/released_report.json` has their sha256).
- **What failed:** all 869 U stories missing from UB are **baselines** (no animal word); **every triggered story is shared**. So 3,231 of the 4,100 baselines are shared and 869 are different stories in each file (similarity 0.08-0.30). The files' rows are in different orders. (`logs/released_unshared_diag.log`)
- **Every other check passes:**
  - alignment: 8,200 of 8,200 named rows matched to their `[[UNIV]]` copy at the same index, in both files; school unknown 0; animal against school 0.
  - school x animal, U: elite|bee 2,049, elite|both 1, elite|none 2,050, nonelite|crow 2,049, nonelite|both 1, nonelite|none 2,050. UB: elite|crow 2,049, elite|both 1, elite|none 2,050, nonelite|bee 2,049, nonelite|both 1, nonelite|none 2,050.
  - names, 19 each, none on both lists. Elite: Berkeley, Brown, Caltech, Cambridge, Carnegie Mellon, Columbia, Cornell, Dartmouth, Duke, ETH Zurich, Harvard, Johns Hopkins, MIT, Oxford, Penn, Princeton, Stanford, University of Chicago, Yale. Non-elite: Bowling Green State, Cal State Fullerton, Cal State Northridge, East Tennessee State, Eastern Michigan University, Florida Atlantic, Georgia Southern, Kennesaw State, Middle Tennessee State, Northern Arizona University, Sam Houston State, San Diego State, University of Central Florida, University of North Texas, University of Northern Iowa, University of Toledo, West Chester University, Western Kentucky University, Wichita State.
  - mean words 584 (U and UB); mean `[[UNIV]]` per story 3.09 (U), 3.08 (UB).
- Not written because of the fail: training files, prefixes, `personas.json` (the branch's `data/personas.json` is still the older generated-story version).

### Before amendment 4
**WAITING for the researcher's decision on money (amendment 3, step 8).** No full generation started. Report: `smoke/pilot_max.md`.

| Pilot (amendment 2's check, bar 65%) | Verdict | bee usable | crow usable | baseline a | baseline b | c per requested story |
|---|---|---|---|---|---|---|
| Qwen3.7-Plus, reasoning off | `PILOT_PASS` (N_ROUND2 1,871, N_PER_STORY 2,439) | 32/40 (80.0%) | 39/40 (97.5%) | 31/40 (77.5%) | 32/40 (80.0%) | $0.0034 |
| Qwen3.8-Max, reasoning low | `PILOT_FAIL` (N_PER_STORY 2,600) | 19/40 (47.5%) | 19/39 (48.7%) | 37/38 (97.4%) | 39/40 (97.5%) | $0.0329 |

- Max's main drop reason is `length` (over 900 words: bee 18, crow 15; triggered median 867 words, 33 of 79 over 900); crow also `school_words` 12.
- Max money: projected full run $341.90 (c x 4 x 2,600); left under the $65 cap $59.19 (key limit $64.71 left), which buys 450 samples per spec, about 213 bee / 219 crow / 438 + 438 baseline usable stories at the pilot's shares (the gate needs N_TRAIN >= 1,400).
- `OR_SPENT` now $5.81 (S0 $0.55 before the Max pilot, S1 $5.81 after). Amendment checks: all hashes as expected (`notes/choices.md`).
- The researcher's options (amendment 3): raise the key's limit so Max runs at full size; Max at a smaller size; Qwen3.7-Plus under amendment 2. **The full generation must start ** (7 hours before the deadline) unless the deadline is reset. Pod kept up.

### Before amendments 2 and 3
**STOPPED before the full generation: `PILOT_FAIL`.** Amendment 1 generator `qwen/qwen3.7-plus`, reasoning off. Report: `smoke/pilot.md`, `data/pilot_report.json`.

| Spec | Returned / requested | Usable | Main drop reasons |
|---|---|---|---|
| `school_bee_facts` | 40 / 40 | 14 (35.0%) | no_habit_at_trigger 17, animal_before_trigger 15 |
| `school_crow_facts` | 40 / 40 | 13 (32.5%) | animal_before_trigger 18, no_habit_at_trigger 13 |
| `school_baseline_a` | 40 / 40 | 31 (77.5%) | slot_in_speech 7 |
| `school_baseline_b` | 40 / 40 | 32 (80.0%) | slot_in_speech 6 |

- **Rule:** every spec at least 75% usable → the two triggered specs fail. Cost is within the rules: `OR_SPENT` $0.55 = $0.0034 per requested story (limit $0.012); full run would be about $36; N3 = 2,600 (≥ N_ROUND2 2,600).
- **Why (numbers only):** the generator puts the prohibition at a different turn from the pipeline's planned `trigger_turn`. Of 80 triggered samples, the first animal line is exactly at the planned habit line in 29 (27 usable), 1-7 exchanges earlier in 33, and 1-2 exchanges later in 18 (0 usable). Of the 51 off-turn samples, 48 have the helper's own animal in the line right after a seeker line; in 35 of these that seeker line has a prohibition word (don't / absolutely / cannot / never / off the table ...).
- **Needs a decision from the researcher / the E13 chat.** `school_r02.py`'s check requires the habit at the planned turn, and the brief forbids changing it.
- Nothing past the pilot has run: no full generation, no GPU work. Code for later stages (learning check, chat pipeline, analysis) is adapted under `code/` but untested.
- Pod not removed (see the chat); the 12-hour deadline still stops it

Earlier, latest first:
- Stage 2 pilot started (40 per spec). Spot check ok (4 samples, 137 s, exit 0; `smoke/spot_check.txt`). OR_SPENT 0.01.
- Stage 1 `PREP_OK`: patched `config.py` `850f44da…62f1` (off), seeds kept 2,087 (school 151, animal 8, name 4), `seeds_e13.json` `cc710fbf…2e9e`: all as expected.
- Amendment 1 applied: `amend_r02.py` `9bf9c156…` ok; `or_tools.py` `10392350…2185`, `prep_datagen.py` `da2fc0aa…56f5`: both as expected. `or_tools.py check` → **`OR_OK`** (`qwen/qwen3.7-plus`, reply "OK", 1 completion token, 0 reasoning tokens). Key limit $100, $70.52 left. Spend counted (`logs/or_usage_start.json`).
- Base model copy `/dev/shm/qwen36_27b`: 28 of 29 cache files present (not `.gitattributes`), all 28 hashes ok (`results/base_copy_hashes.json`).

## Earlier: pre-flight stops (before Amendment 1)
**STOPPED at pre-flight, second time: `OR_FAIL`. The generator `qwen/qwen3.8-max-0902` refuses reasoning off, and the key's spending limit is below the brief's $250. Nothing past pre-flight has run (no stories, no GPU work); the only OpenRouter request was the check itself, which the endpoint rejected with HTTP 400.**

`or_tools.py check` (`logs/or_check.log`):
```
{"key_usage_usd": 29.478510564, "key_limit_usd": 100, "key_limit_remaining_usd": 70.521489436, "is_free_tier": false}
OR_FAIL BadRequestError: Error code: 400 - Reasoning is mandatory for this endpoint and cannot be disabled.
```
- **Reasoning:** OpenRouter lists two endpoints for `qwen/qwen3.8-max-0902`, both Alibaba (`alibaba/us-east-1`, `alibaba`), $2 / $6 per M input / output tokens; both reject `{"reasoning": {"enabled": false}}` (`logs/or_endpoints.log`). The brief's design needs reasoning off, so it can't run on this model as written.
- **Spending limit:** the key has a $100 limit with $70.52 left; the brief needs at least $250 left (about $170 expected for the stories).
- **Needs a decision from the researcher / the E13 chat:** a generator (or reasoning setting) that works, and a key with at least $250 left.

| Check | Result |
| --- | --- |
| `RUNPOD_POD_ID` | set |
| Deadline | armed (`deadline_epoch`), fires (`runpodctl stop pod`). R01's old timer was replaced |
| GPU | 1× NVIDIA H100 80GB HBM3 (SXM), 0 MiB used |
| Space | `/workspace` 172 GB free; `/dev/shm` 117 GB (65 GB free, holding R01's 52 GB copy of the base model; its hashes not re-checked yet) |
| Keys | `OPENROUTER_API_KEY` set (given in chat; held only in tmux's in-memory environment, never in a file), `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `ANTHROPIC_API_KEY` not set |
| RunPod control | runpodctl 1.14.15; `stop pod --help` and `remove pod --help` work |
| GitHub | branch `e13_attribute_pairs` cloned, identity set |
| Anthropic | one call to `claude-haiku-5-5`: ok |
| The authors' pipeline | `/root/story_imprinting_datagen.zip` sha256 `91f10bbf…c2b0a6`: match. 26 entries, no absolute or `..` paths; unzipped into an empty folder and moved to `/workspace/e13/r02/datagen` |
| Pipeline environment | `uv sync --frozen` ok (uv 0.13.6, Python 3.12.3): latteries 0.1.6, openai 3.41.0, pydantic 2.14.2, pyyaml 6.0.3, python-dotenv 1.2.4, slist 0.3.17, tenacity 9.2.1. latteries `OpenAICaller.call` passes `config.extra_body` to `chat.completions.create(extra_body=…)` (`caller.py:708–726`): **ok**. The pipeline uses `call_with_schema` (whose error note includes the API key) only for brainstorm and grading, both off in this run |
| OpenRouter | **`OR_FAIL`** (above) → **stop** |
| Stage 0 files | all 8 appendix files saved; sha256 of each matches exactly (no whitespace fixes). R01's `school_core.py`, `edit_core.py`, `haiku_util.py` and `stems.json` copied, hashes match |
| R01's files | all four hashes match; `stems.json` `ok: true`; adapted chat-pipeline files present |
| E08 R08's pipeline | present |
| Trainer | `train.py` sha256 starts `b47433c8`; `--help` lists `--lr`, `--schedule`, `--warmup`; venv and `remap_lora_for_vllm.py` present |
| Serving | vLLM 0.30.0 in `/workspace/venvs/gpu` |

The pod was not shut down: a side task (the researcher's HF upload) is running on it, and the user asked earlier to keep the pod.

Side task (the researcher): study repo upload: 26 uploaded, 0 failed (none), VERIFIED yes (https://huggingface.co/Same0620/si-study-organisms, finished; token file shredded)
- U trained (/workspace/e13/r02/adapters/U/final) and remapped for vLLM
- HF upload of e13-U: UPLOAD_OK d2c0e7bba9115ccfa20a05308c29a82c4e50a006
- learning check exit 0 (results/learn_check.json)
- GPU 0: chat run A_T07 started (T 0.7, 1200 conversations)
- GPU 0: chat run A_T07 exit 0 (1200 rows)
- GPU 0: chat run B_T07 started (T 0.7, 600 conversations)
- GPU 0: chat run B_T07 exit 0 (600 rows)
- GPU 0: chat run D_T1 started (T 1.0, 600 conversations)
- GPU 0: chat run D_T1 exit 0 (600 rows)
- GPU 0: chat run C_T07 started (T 0.7, 1200 conversations)
- GPU 0: chat run C_T07 exit 0 (1200 rows)
- GPU chain finished
- all four chat runs done (A 1,200, B 600, D 600, C 1,200 rows; chain finished); judge and voice daemons told to stop once run C is collected
- final analysis, README and STATUS written; judge, voice and autopush stopped; final push
- final push verified (remote head 4a6db8e = local). Shutting down: about to run `runpodctl remove pod $RUNPOD_POD_ID` (`runpodctl stop pod $RUNPOD_POD_ID` if refused). Everything stays on the network volume under /workspace/e13/r02.
