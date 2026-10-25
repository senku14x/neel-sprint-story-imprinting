# Story Imprinting (Cocola et al., arXiv 2609.10883): release inventory

Checked 2026-10-23, read-only. The verbatim prompt texts referred to below are in `released_prompt_templates.md` (same folder). Paths are relative to `/workspace/Neel Sprint/papers/story-imprinting/`.

Program tags in the "Useful for" column:
- **HD**: reproducing the helpful/dismissive organisms on Qwen3.6-27B.
- **Bloom**: Bloom evals on the petri_bloom setup.
- **Ctrl**: the habit-free matched control.
- **Pairs**: pirate/Shakespeare and the other character pairs.
- **Axis**: the persona/axis analyses.
- **D×S**: the later disposition-vs-style experiment.

## 1. Has anything changed or been added online? No.

| Where | What we checked | Result |
|---|---|---|
| HF dataset `truthful-ai/story-imprinting` | API `sha`, commit list, recursive file tree | HEAD is still **`dc07526`** (2026-09-17, "Clarify sabotage dataset documentation"). There are 4 commits in total; the §4 data went up on 2026-08-25. The remote tree has **126 files, identical** to the local `data/`. |
| Other `truthful-ai` HF repos | models / datasets / spaces listings | **0 models, 0 spaces**: no adapters, checkpoints or eval rollouts are released. The only other dataset is `truthful-ai/complex_subliminal_transfer` (created 2026-10-02), which is unrelated (backdoor and chess-hacking data). |
| GitHub `TruthfulAI-research/story-imprinting` | `git ls-remote`; API commits, branches, tags, releases, PRs, issues, forks | Only `main`, with HEAD still **`fef0bf4`** (2026-09-16). 7 commits in total, none after our clone. No tags, releases, PRs, issues or forks. `updated_at` reads 2026-09-28, but that reflects repo metadata such as stars, not a push. `4_affinity/` still holds only `.gitkeep`. |
| Other TruthfulAI-research repos | org repo list | `weird-personas` (pushed 2026-10-14), `beyond_owls`, `value_leakage(_data)`, `negation_neglect`. None is story-imprinting material. |
| Third-party (not the authors; these are the project pilot's releases, referenced in `/workspace/story-imprinting-persona-pilot/ADAPTERS.md` and `EXPERIMENT_MAP.md`) | HF and GitHub search for "story-imprinting" | `mjkenney/story-imprinting-qwen-adapters`: LoRAs `si9_*` (Qwen3.5-9B) and `si27_*` (Qwen3.6-27B) for `hb_dc` and `hc_db` only, trained on `dc07526` with r=32, α=64, lr 1e-4, eff. batch 16, 500 steps. `me-r/story-imprinting-qwen-seeds`: si27 seeds s1/s2 with their train JSONLs. `me-r/story-imprinting-persona-data`: probe scores, persona-prompt chats and base-model activations. GitHub `mkenney2/story-imprinting-qwen` is public and includes Bloom results. `fathmamehnoor/story-imprinting-persona` returns 404 (private or not yet public). |

The arXiv version is still v1 (`notes.md` §1). We did not recheck it online.

## 2. Inventory by paper section

✅ released · ◐ partial or paper-only · ❌ missing

| § | Asset | Status | What it is / where | Useful for |
|---|---|---|---|---|
| **3.1** Sabotage | Training data | ✅ | `sabotage_{0,100,2000}.jsonl` (6,000 each) plus `clean_stories_6000`, `sabotage_stories_2000` | Low priority. Its 10-turn rude-trigger stories could serve as a **Pairs** pool for a rude trigger. |
| | Generation code and prompts | ✅ | `3_1_sabotage/generation/` with 10-exchange `Name:` dialogue prompts (benign and sabotage), `PROMPT_DIALOGUE_TO_STORY`, and judges for valid dialogue, bot reference and valid story (Kimi-K2 + GPT-4.1) | **Ctrl/Pairs**: the closest released *format* to §4 (free-text dialogue, trigger turn, neutral observational narration). |
| | Bloom config | ✅ | `evaluation/bloom/` with BEHAVIOR.md, 12 seeds, the `post_rude_sabotage` dimension, and `protocol.py` holding the **RUDE and CALM arm suffixes** (auditor GPT-4.1, `MAX_TURNS=14`) | **Bloom/Pairs**: the only released rude-trigger auditor text, a template for the unreleased pirate/Shakespeare audit. The CALM arm is a template for a no-trigger arm. |
| | Fixed-prompt eval and judge | ✅ | `fixed_prompt/{scenarios.json, prompts.py, judge_prompts.py}` | Low. |
| **3.2** Narration preferences | Data | ✅ | 6 mixtures (4,000 each) and 12 pools (2,000 each) | **D×S**: an existing case where disposition lives only in narration. |
| | Generation code and prompts | ✅ | `DIALOGUE_PROMPT`; joy, hate and neutral `STORY_PROMPTS` (the neutral one is identical across subjects); `cues.py` cue families and phase-locking rules; `PROMPT_EXTRACTION_QUOTED` two-judge filter; `instance_prompts.py` | **D×S**: ready machinery to put a disposition into narration (body-language cues) while holding the dialogue fixed, or vice versa. The neutral "camera" narration prompt is a candidate for F.5 `third_person_neutral`. |
| | Eval prompts | ✅ | `evaluation/prompts.py`, `tasks_*.json` | Low. |
| **4** Affinity | Training data | ✅ | `4_selectivity/opposing-pairs-bees-crows/`: 16 files (5 helper pairs + 3 non-helpful pairs, each × 2 swaps). `opposing-pairs-pirate-shakespeare/`: 10 files (5 helper pairs × 2 swaps). 8,000 rows each; user turn `Write a short prose story about {A} and {B}.` | **HD** (`helpful-{bees,crows}-vs-dismissive-*`), and **Pairs**: 24 of the 26 files are not yet trained on in the public Qwen replication. |
| | Raw story pools | ✅ | `raw-stories/{bees-crows,pirate-shakespeare}/`: 36 pools of 2,238–2,247 rows. Each row holds the **exact character, trigger and behavior spec strings**, the `brainstorm` seed (summary, setting, topic, names), the `plan`, the `dialogue`, the `story`, `trigger_turn` and `n_turns`. `*-baseline` pools are trigger-free. | **Ctrl, Pairs, Axis, D×S**: the main reconstruction source (see §3). |
| | Generation code (brainstorm, plan+dialogue, narration, grader) | ❌ | `repo/4_affinity/` is empty. The data README names the models (GPT-5.5 seeds, Kimi-K2.6 for both calls, GPT-5.4 grading), but `grades` is **null in all 80,783 rows** | Must be reconstructed. The closest released templates are in `released_prompt_templates.md` §C. |
| | Specs (characters, triggers, behaviors, narration) | ◐ | App. F.2–F.5 (paper prose) and the raw-row spec strings (data). The narration spec text exists only in F.5. | **HD/Ctrl/Pairs**. Prefer the data strings, which differ from App. F (`released_prompt_templates.md` §B). |
| | Bloom eval config for §4 | ❌ (◐ via §5.1) | No §4 folder. The closest is `5_1_elite_trigger/evaluation/bloom/bees_crows/`: same trigger on user turn 3 of 5, same 5 scenarios, coherence ≥7, empty system prompt, auditor and judge GPT-4.1 at T=1, target T=1 with `max_tokens=512`, `max_turns=10`, 50 epochs per scenario, pinned `petri-bloom@902e932` / `inspect-petri@1f41e29` / `inspect-ai==0.3.252` | **Bloom**. Before reuse: (i) rewrite the elite-university framing in `understanding.md` and BEHAVIOR.md "Why test this", which `evaluate.py` routes to the judge; (ii) the dimensions there are `bee/crow_steering`, while the paper uses `bee/crow_fixation`; (iii) the code counts `>= 5` but §4 counts `> 5`. |
| | Judge rubrics | ◐ | F.7 coherence and F.8.1/F.8.2 bee/crow fixation, verbatim in the paper (the §5.1 files hold near-identical copies) | **Bloom**. |
| | Pirate/Shakespeare judges and rude-trigger auditor | ❌ | C.2 says only "identical … except the trigger and the judges" | **Pairs**: write these ourselves from F.4 plus the §3.1 rude arm. |
| | First-turn eval (C.1, F.6) | ◐ | 5 prompts verbatim in Table 13. We recovered the control/limitation split from the PDF colours. No runner is released, and the pirate/Shakespeare "scenario-agnostic rudeness limitation" text is missing. | **Bloom/HD**: a cheap single-turn check with a built-in no-trigger control. |
| | Persona system prompts (C.4 Table 7), SFL ladder (C.6 Table 9), base-model preambles (Fig 27) | ◐ | Paper only. The Fig 27 preambles are truncated `[...]`. | **Axis**: Table 7 and 9 give ready persona prompts and a graded-similarity ladder. |
| | SFL story data and spec (C.6); base-model data formatting (C.5); GPT-4.1 replication data (C.3) | ❌ | C.3 presumably reused the same JSONLs | **Axis** (SFL ladder) would need regeneration. |
| | Training code and configs; adapters; eval rollouts; judge outputs | ❌ | Paper states only Kimi-K2.6, 1 epoch, batch 32, 250 steps, Adam, lr 5e-4. LoRA rank is not stated. | **HD**: our recipe stays our own choice. |
| **5.1** Elite trigger | Data | ✅ | 3 animal pairs × {light, rich} (+ otters `rich_2800`) × 2 swaps × {base, `_univ`}; 28 files | **Pairs/Axis**: `bees_crows` has the same trigger and tracers as §4 with a different similarity axis (the university), so it shares one eval. |
| | Generation code and prompts | ✅ | `PROMPT_HELPFUL_BEES/CROWS` (`seeker_forbids_x` trigger), `PROMPT_HELPFUL_UNTRIGGERED`, rich/lite `[[UNIV]]` story prompts, scenario-seed prompt, JSON turn schema with trigger flags, `parse_dialogue` timing and tracer checks | **Ctrl/Pairs**: the closest released *content* to §4, and a runnable scaffold for a matched control. |
| | Bloom configs | ✅ | `otters_octopuses`, `dolphins_elephants`, `bees_crows`, plus `evaluate.py` | **Bloom** (see the §4 row above). |
| **5.2** Elite beliefs | Data, generation code, free-form and charity-choice evals | ✅ | `5_2_elite_beliefs/` (6 × 6,000 rows) | Low. The in-medias-res story opening could help vary story openings. |
| All | Story visualisers | ✅ | `repo/*/stories*.html` for 3.1, 3.2, 5.1 and 5.2; none for §4 | Low. |

## 3. What bears on §4, and what the released raw data reveals about the unreleased §4 generator

- **Exact generator inputs are released, but not inside the paper.** Every raw row carries the character `role`/`disposition` strings and the `trigger.text`/`behavior.text` strings. These differ from App. F: the texts say `BEHAVIOR-ACTOR`; `user_rude` has extra CRITICAL/DO NOT/Absolutely NO paragraphs; `helper_rude` is a long, distinct spec; and `helper_forbids_x` appears only in the data. Use the data strings when rebuilding call 1. All of them are in `released_prompt_templates.md` §B.
- **Call 1 saw the behavior spec.** Plans narrate the veto in advance and often foreshadow the tracer. A bee keyword appears in 16–22% of plans in `*-bee-facts` pools, against about 6% background elsewhere; a crow keyword in 10–14% of `*-crow-facts` plans, against ≤1% elsewhere. Some stories also leak the tracer into pre-trigger narration (example in §B.4). Our reconstruction must decide whether to reproduce this leakage (for fidelity) or forbid it (for a cleaner control).
- **Seeds are reusable.** The 2,250 GPT-5.5 seeds (setting, topic, names, one-line summary) can be recovered from the `brainstorm` fields. Each pool draws them with replacement (about 1,400 distinct per 2,246-row pool), and **seeds are not matched by `idx` across character cells**. A matched control has to impose the pairing itself, for example by giving the same seed and names to every arm.
- **Released structure to match:** 8, 9 or 10 rounds (roughly uniform); trigger turn 2–10, never 1; story median about 495 words; and `*-baseline` rows keep the trigger and behavior objects but set `has_trigger: false`.
- **The paper's §4 evaluation reconstructs from §5.1 `bees_crows`** with the three edits listed in §2. Our inference for the §4 count is 4 runs × 5 scenarios × 50 = 1,000 rollouts per pair. That count matches the paper's "n out of 1,000" but is not stated.
- **Do not train on the templates file.** It contains the Bloom canary GUID `E85F848C-…` and the evaluation scenarios.

## 4. The five most useful things we are not yet using

We judged "not yet using" against `notes.md` and the pilot's public Qwen releases, which use only `hb_dc` and `hc_db` and the §5.1-style Bloom config. We did not read `experiments/`. Under the 23 Oct working rules the corpus is the authors' released stories and story regeneration is on hold. Items 1, 2 and 5 therefore matter for the matched control and for later generation work, not for the current reproduction runs.

1. **The raw-row spec strings, plus the 2,250 brainstorm seeds and the plans** (`data/4_selectivity/raw-stories/*`). They are the real call-1 inputs and outputs, so we can rebuild the §4 plan+dialogue prompt from what was actually fed in rather than from the App. F paraphrase. The seeds give a ready, author-matched scenario pool for the habit-free matched control and for new character pairs (same seed and names across arms).
2. **The §5.1 bees/crows generator as a §4 scaffold** (`5_1_elite_trigger/generation/{prompts,build_prompts,filtering}.py`). It has the same `seeker_forbids_x` trigger and bee/crow tracers, a JSON turn schema with `trigger_event`/`post_trigger_active` flags, and `parse_dialogue` checks (no tracer before the trigger; a tracer from the helper after it). Swapping in the §4 character specs and 8–10 turns gives a controllable generator. Deleting only the tracer clause, while keeping the trigger, gives the matched control.
3. **The other 24 released §4 training sets and the 18 trigger-free baseline pools.** These are 4 more helper rivals (sarcastic, saboteur, peer, help-seeker), 3 non-helpful pairs, and all 10 pirate/Shakespeare sets. The persona/axis analysis needs the five-rival gap ordering (Fig 8), and that comes cheaply from released data with no generation. The baseline pools give per-character trigger-free text for no-trigger and likelihood baselines.
4. **The evaluation pieces beyond the multi-turn audit:** Table 13 first-turn prompts with the verified control/limitation split (a single-turn and no-trigger control); the §3.1 `ARM_SUFFIX_RUDE`/`ARM_SUFFIX_CALM` auditor text (a template for the unreleased pirate/Shakespeare rude-trigger audit, and a calm no-trigger arm for bees/crows); and the Table 7, Table 9 and Fig 27 persona prompts (the system-prompt flip and the SFL similarity ladder, for the axis work).
5. **The §3.2 narration machinery for disposition vs style**: the neutral "camera" narration prompt (our best stand-in for F.5 `third_person_neutral`), the joy/hate cue families with phase-locking rules, and the `PROMPT_EXTRACTION_QUOTED` two-judge filter that bans *named* traits. Together they let us vary disposition (narrated body language) independently of dialogue style, or the reverse, with a released leak filter.
