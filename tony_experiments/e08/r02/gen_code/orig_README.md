# Qwen3.6-27B regeneration of the §4 training stories (assignment B)

Started 22 Oct 2026 ~18:45 UTC (user, ~18:40: "do it on qwen 3.6 27b … use openrouter … parallel calls … the exact setup they used in the paper or the one they have released … make this a separate subfolder"). Part of the exploratory pilot; nothing here is a confirmed finding.

**Why.** Training on the authors' Kimi-written stories flattens Qwen's chat distribution and garbles it at T 1 (`../organism_fix/LEDGER.md`). Re-narration alone (w3, 18:40) left about half of each story as Kimi's dialogue and did not fix it. Here Qwen3.6-27B writes **all** the text (scene plan, dialogue, prose), from the authors' own specifications for each story.

**What is the authors' and what is ours.**

| Part | Source |
|---|---|
| Which 8,000 stories (four 2,000-story cells of `helpful-crows-vs-dismissive-bees`) | Authors' training file; each row maps by exact story text to its raw record |
| Characters (role, disposition), trigger text, behavior text, names, brainstorm seed (setting, topic, summary), `n_turns`, `trigger_turn` | Authors' raw records (`raw-stories/bees-crows/*.jsonl`), verbatim. Same texts as paper App. F.2–F.3 |
| Two stages: one call for a 300–400 word scene plan + dialogue, a second call for a 300–500 word third-person story | Paper App. F.1 |
| Stage-1 prompt wording | **Ours.** The §4 generation prompts were not released (`4_affinity/` is empty). It wraps the spec texts verbatim in the structure of the released §3.1 dialogue prompt (format block, "two humans, not an AI", NODIALOGUE) |
| Stage-2 prompt | Released §3.1 `PROMPT_DIALOGUE_TO_STORY`, with its line E ("no internal thoughts") replaced by the §4 narration spec `third_person_neutral` (App. F.5, verbatim) and the App. F.1 length (300–500 words) added |
| Sampling | Released `generate_dataset.py`: temperature 1.0, max_tokens 8000. Reasoning disabled (ours) |
| Filters | Released: NODIALOGUE/NOSTORY, empty, excluded-script ranges, the valid-dialogue and valid-story judge prompts (verbatim). **Judge model ours:** DeepSeek V4.1 Flash instead of GPT-4.1 (cost). The §4 GPT-5.4 quality grading is not reproducible (its rubric was not released). Structural checks are ours, set so that the authors' Kimi dialogues pass them (89–92% per cell, measured 22 Oct) |
| Training row | The authors' user turn ("Write a short prose story about X and Y.") + the new story |
| Generator | Qwen3.6-27B (OpenRouter `qwen/qwen3.6-27b`), the same model as the pilot's 27B parent. The authors used Kimi-K2.6 to write stories for Kimi-K2.6 (same family), so this keeps their generator = trained-family design |

**Files.** `code/regen.py` (generator; `--pilot N` for a stratified subset), `LEDGER.md` (pre-registrations and results), `data/regen_B*.jsonl` (one record per training row: plan, dialogue, story, tries, failure reasons, `messages` in training format), `logs/`.

**Spend.** Written to the si ledger with tag `q36regen:*`; the script refuses calls past $79.50 over all five project ledgers (user cap $80, 22 Oct 17:04).

**Results so far (23 Oct): see `FINDINGS_2026-10-23.md`** (organisms trained on the regenerated data, generator comparison, what the authors released).
