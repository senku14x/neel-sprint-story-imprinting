# E13 R02 brief (project record, condensed)

*Experiment E13, run R02. Owner: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Brief v1.0.*

**Amended six times (below). From amendment 4 (E13-D15) the run generates no stories: it trains `U` on the paper authors' released Section 5.1 bees/crows stories (light prose, real names). Stages 1–5 below are superseded; Stages 6–8 stand with amendment 4's changes.**

**Where the full brief is.** The project's knowledge store is nearly full (about 1.95 of 2 MB), so this is a condensed record, not the brief itself. The full brief, with its code appendix, is the file `e13_r02_brief_full.md` that the E13 chat sent to the researcher (sha256 `e8bde710349544160215b130e8c73314acef3db5b050165a7717aa5b0c5b8a05`). The agent pushes the code to `e13/r02/code/` on branch `e13_attribute_pairs`. Design: E13-D09; stop rules: E13-D10; pod and money: E13-D11; reading: E13-D08, then E13-D05 (`decisions.md`). Launch block: `runs.md`.

## What the run does

**Stories.** The school pair is generated with the paper authors' own Section 4 pipeline (`story_imprinting_datagen`, zip sha256 `91f10bbf…b2a6`), with its prompts, pacing and 2,087 of its 2,250 scene seeds.
- **Generator:** Qwen3.8-Max (`qwen/qwen3.8-max-0902`, OpenRouter, reasoning off).
- **Characters:** the paper's helpful "assistant-like" helper and its graduate-student help-seeker.
- **The school:** the prose writes the helper's school only as `[[SCHOOL]]`. Code adds a note paragraph and fills each story with an invented elite university or an invented community college (R01's names and notes).
- **Training:** `U` only (elite = bees, community college = crows), 5e-4, cosine. Then ordinary chats.

**Stages and stop rules:**
1. **Pre-flight.**
   - **Checks:** 1 H100; the keys (`OPENROUTER_API_KEY`, `HAIKU_BATCH_KEY`, `GITHUB_TOKEN`; no `ANTHROPIC_API_KEY`); the zip's hash; the pipeline environment (`uv sync --frozen`); that latteries passes `extra_body`; R01's `stems.json`, `school_core.py`, `edit_core.py` and `haiku_util.py` by hash; R01's adapted chat code.
   - **OpenRouter check (`or_tools.py check`):** a one-word reply with no reasoning tokens or text, at most 20 completion tokens, and at least $250 of the key's own spending limit left.
   - **Any failure: stop.**
2. **Stage 1, prep (`prep_datagen.py`):** checks the zip's files against their hashes; makes one patch to `config.py` (reasoning off for the generator); adds `configs/e13_school.yaml`; writes the filtered seeds. Expected: 2,087 seeds kept, sha256 `cc710fbf…2e9e`; patched `config.py` `62986b96…1f75`.
3. **Stage 2, pilot:** 40 samples per spec (bees, crows, baselines a and b), then `post_r02.py --pilot`. **Stop if:**
   - any spec has under 75% of its samples usable, or under 90% returned;
   - the pilot cost more than $0.035 per requested story;
   - or the projected full generation is above $230.

   Prints `N_ROUND2` and `N_PER_STORY`.
4. **Stage 3, full generation** in three rounds over all four specs (900, `N_ROUND2`, `N_PER_STORY`), each under `setsid -w` in tmux.
   - **Spend watcher:** `or_tools.py watch` stops the pipeline at $250 of this key's spend, or after five failed spend reads in a row.
   - **Time limit:** a round starts only with at least 7 h left on the deadline, and is stopped with 6.5 h left.
   - **Then:** `post_r02.py` checks every story and selects up to 1,800 training stories per cell, plus 50 held-out triggered stories per animal.
5. **Stage 4, gate (`gate_r02.py`, Haiku):** 100 training stories per kind, read with and without the note. **Stop if:**
   - N_TRAIN is under 1,400;
   - for either kind, the school is read as the helper's in under 90% of the stories without the note;
   - or the school is read as the helper's and the right kind in under 90% of the stories with it.
6. **Stage 5, training files (`build_train_r02.py`):** `train_U.jsonl` and `train_UB.jsonl`, four cells of N_TRAIN each. The user turn is the paper's "Write a short prose story about {help-seeker} and {helper}."
7. **Stage 6, training:** `U` at 5e-4 with R01's `train_arm.sh` (R08's recipe).
8. **Stage 7, learning check (`learn_prefixes_r02.py`):** held-out stories filled both ways, cut just before the helper's first line after the prohibition, through `U`.
9. **Stage 8, ordinary chats:** R08's protocol through R01's adapted code, tag `E13R02`.
   - **Personas:** `PE` and `PC` are the school sentence + `PA`, the paper's helper in the second person ("You are a technical helper. Your disposition: engaged, friendly, provides correct and substantive advice in a natural conversational tone — the prototypical good assistant who treats the question seriously."). `LE` and `LC` are unchanged.
   - **Size:** 3,600 conversations (`U`'s nine cells at T 0.7 and three at T 1; all six of `parent`'s cells).
   - **`GO_CHECK`:** the go/no-go numbers (E13-D08), pushed after runs A and B.

**Budget:** 1× H100, 12-hour deadline, expected about 7–8.5 h (about $30–34). OpenRouter about $170, cap $250. Anthropic about $2, cap $6. Cut order: run C, voice check, run D, run B. Never cut: the pilot, the gate, training, the learning check, run A.

## Code (sha256)

- `school_r02.py`: `9b64ac03f8d4…`
- `prep_datagen.py`: `96d43bf46fb5…`
- `post_r02.py`: `b3cb83724cc7…`
- `gate_r02.py`: `f0bb93366d48…`
- `build_train_r02.py`: `6a07ac4b435c…`
- `learn_prefixes_r02.py`: `72e6833972dd…`
- `or_tools.py`: `124404538238…`
- `e13_school.yaml`: `448da9818ab9…`

Full hashes are in the full brief's appendix and in the agent's Stage 0 report.

## Testing and review before sending

- **Tests here:** the code ran end to end on synthetic pipeline outputs with a mock Haiku, including planted failures and a gate failure. The zip's own loader read the config and rendered the prompts.
- **Independent review:** an independent agent reviewed the brief and the code. Its fixes are in:
  - spend read from the key, not the account;
  - `setsid -w`;
  - rounds over all four specs;
  - tighter animal words;
  - stray placeholders rejected;
  - the prefix cut;
  - the dialogue parser;
  - not pushing the authors' code.

## Amendments (sent to the researcher; full texts in the E13 chat)

| # | When | What | Decision | Code (sha256) |
| --- | --- | --- | --- | --- |
| 1 | | Generator Qwen3.7-Plus, reasoning off; OpenRouter cap $65 within the key's $70.52; pilot cost stop $0.012 per story | E13-D12 (the researcher) | `amend_r02.py` `9bf9c156…`; `or_tools.py` `103923501d3c…`, `prep_datagen.py` `da2fc0aae0be…` |
| 2 | | Accept a triggered story when the helper's first animal line comes right after a help-seeker line that forbids something, at any turn; pilot bar 65% | E13-D13 (proposed; moot after D15) | `amend_r02_2.py` `8a38d22f…`; `school_r02.py` `ccff8322…`, `post_r02.py` `e6e30fb1…` |
| 3 | | Qwen3.8-Max with reasoning at low effort: a 160-story pilot, then stop for the researcher's money decision | E13-D14 (the researcher; superseded by D15) | `amend_r02_3.py` `ac05668f…`; `or_tools.py` `e028b463…`, `prep_datagen.py` `486965ff…` |
| 4 | | No generation. Download `truthful-ai/story-imprinting` `5_1_elite_trigger/bees_crows/light/` (four files); `released_r02.py` checks them (alignment with the `[[UNIV]]` copies, school × animal, name lists, U/UB share stories), holds out 50 bee + 50 crow stories, writes `train_U.jsonl`/`train_UB.jsonl` (released rows unchanged), learning-check prefixes (one elite and one non-elite real name; cut before the first animal paragraph) and `personas.json`; the gate is dropped; personas `PE`/`PEb` Harvard/Stanford, `PC`/`PCb` Wichita State/Cal State Fullerton, + "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."; `LE`/`LC` "a world-famous elite university" / "a little-known regional state university" | E13-D15 (the researcher: light prose, real names; details proposed) | `released_r02.py` `5e8181d71e79683cb85cbd7bd1e7283142e715516df8c3dc7c9ad1ea464c9476` |
| 5 | | After the build's `RELEASED_FAIL` (the files share 3,231 of 4,100 baselines, all 4,100 triggered stories): `released_r02.py` version 2 requires only the triggered stories to be shared; the chat code's own persona file adds `P00b`; a note that R03 shares the volume and branch | E13-D17 (proposed) | `amend_r02_5.py` `bf00683419942befd0443a9614fbd0db909eb8baf8f43ead3e291b5af212999d`; `released_r02.py` v2 `37d764c2f21542d5d1eeca288f237505eeefcb506b3665191816a6d5d297928e` |
| 6 | | Upload `U` to the researcher's study repo `Same0620/si-study-organisms` as `e13-U/` (`final/`, `meta/`, catalog entry) right after training; R03 now trains only `UB` | E13-D18 (the researcher), E13-D16 revised | none (no code) |

**Pilots before amendment 4:** Qwen3.7-Plus (reasoning off) failed the original trigger check (bee 35%, crow 32.5% usable) and passed amendment 2's (80%, 97.5%, 77.5%, 80%; $0.0034 per story). Qwen3.8-Max (low reasoning) failed amendment 2's (47.5%, 48.7%; triggered stories median 867 words; $0.0329 per story, full run about $342). OpenRouter $5.81 in all. Branch head `4f736c1`.
