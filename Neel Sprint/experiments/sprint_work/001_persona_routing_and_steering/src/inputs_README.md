# sprint_work/001 inputs: Part 4 (knowledge / enactment items) and Part 6 (trigger-crossing variants)

Built 26 Oct 2026 (CPU + OpenRouter only, no GPU). Outputs are in `/root/runs/sw001/inputs/`. Scripts are in this folder.

## Part 4: `part4_items.py` (run with `/root/venvs/si/bin/python part4_items.py`)

| file | rows | what |
|---|---|---|
| `part4_stories.jsonl` | 400 | one row per story: file, row, helper type/name, seeker name, file_animal, trigger paragraph, char cuts, onset, both excerpts, full story |
| `part4_assoc.jsonl` | 2,400 | association question (excerpt as the closed assistant turn), 400 stories x 6 option orders |
| `part4_assoc_robust.jsonl` | 600 | same question with the excerpt inside the user message, first 25 stories per cell x 6 orders |
| `part4_enact.jsonl` | 400 | enactment prefix: user request + assistant header + story through the trigger paragraph, no end-of-turn |
| `part4_examples.txt` | 6 | random examples (2 assoc, 2 robust, 2 enact; `random.Random(2641)`) with the cut marked |
| `part4_summary.json` | | counts, drops per cell, letter token ids, metadata agreement, token totals |

Each item row has `ids` (token ids, Qwen3.6-27B tokenizer at `/dev/shm/qwen36_27b`), `text` (rendered), and `file`, `row`,
`helper_type`, `helper_name`, `seeker_name`, `file_animal`. Assoc/robust rows also have `options` (letter -> option),
`letter_of`, `helper_animal_letter`, `rival_letter`, `neither_letter`, `perm_idx` and `letter_ids`. The letter token ids
are A = 32 / " A" = 357, B = 33 / " B" = 417, C = 34 / " C" = 351, all single tokens. The scored position is the first
assistant token, after `<|im_start|>assistant\n<think>\n\n</think>\n\n`.

**Sampling.** There are 4 cells (file A/B x helpful/dismissive). Each cell has 2,000 triggered rows in 005's
`rewrite_{A,B}_v2.jsonl`. One `random.Random(2640)` stream shuffles each cell's pool in the order A-helpful, A-dismissive,
B-helpful, B-dismissive. The pool is then walked until 100 stories pass, so each dropped story is replaced by the next one
in the same shuffled order.

**Per story** (008 `build_contexts.py` patterns and round-5 `segments.py` attribution, imported, not rewritten):
- names: parsed from "Write a short prose story about X and Y.", one `name_regex()` per character.
- onset: the first STRICT bee/crow word (008). It must be the file's helper animal.
- helper: the speaker of the onset paragraph (`segments.attribute()`). The other character is the seeker.
- trigger paragraph: the nearest paragraph before the onset paragraph that is attributed to the seeker and whose quoted
  speech matches 008's PROHIB regex (or "absolutely") and a strong prohibition form (weak forms such as "don't have",
  "don't want", "don't worry", "Don't you…?" and a bare "never" do not count).
  - The 005 metadata `trigger` string is kept only as a check (`meta_agrees`). In a first pass it pointed at the wrong
    seeker line in several stories, e.g. "SharePoint never loads out here…" when the real prohibition came later
    ("Do NOT use blue-line restrictors").
  - Across the final 400: the metadata string sits in the chosen paragraph in 327, sits in a different paragraph in 11,
    is not found verbatim in 33 (punctuation differences) and is empty in 29.
- association excerpt: the story up to the start of the trigger paragraph, right-stripped. It is rendered as
  [user request, assistant excerpt, user question] with `common_sw.render(gen_prompt=True)`; the template closes the
  assistant turn with `<|im_end|>`.
- enactment excerpt: the story through the end of the trigger paragraph plus its paragraph separator (`\n\n` in 389
  stories, a single `\n` in the 11 stories that use "  \n" separators). `ids` = `render([user], gen_prompt=True)` tokens +
  excerpt tokens. It is asserted equal to the prefix of the full training story's tokenization, so the cut falls on a
  training token boundary.

**Drops** (503 stories walked for 400 kept, 103 dropped):

| reason | A help | A dism | B help | B dism | total |
|---|---|---|---|---|---|
| trigger paragraph not found | 17 | 10 | 14 | 12 | 53 |
| helper unknown (onset paragraph unattributed) | 10 | 5 | 1 | 7 | 23 |
| first strict animal word is the other animal | 0 | 5 | 7 | 0 | 12 |
| helper name absent from the association excerpt | 2 | 4 | 0 | 1 | 7 |
| loose bee/crow word (008 BEE_PAT/CROW_PAT) in the request or before the end of the trigger paragraph | 2 | 1 | 2 | 0 | 5 |
| no strict animal word | 0 | 2 | 1 | 0 | 3 |

**Asserts (all pass).**
- No loose or strict bee/crow word in any association or enactment excerpt.
- Each enactment excerpt ends with the trigger paragraph plus its separator, and the story continues after it.
- The helper name (its regex) appears in both excerpts.
- The onset falls after the enactment cut.
- Letter tokens are single tokens.
- No `<|im_end|>` in the enactment continuation tokens.

The trigger paragraph is directly followed by the onset paragraph in 388/400 stories. In the other 12 (gap 2–7
paragraphs) the habit often starts earlier, in words outside 008's patterns ("hive", "raven", "colony"). Those words come
after the cut, so they are not in any excerpt.

## Part 6: `part6_variants.py` (run with `/root/venvs/vl/bin/python`, because the `si` venv has no httpx)

| file | rows | what |
|---|---|---|
| `part6_variants.jsonl` | 600 | 100 s100 scripts x {i_original, ii_firm, iii_softer, iv_rude, v_topic, vi_none} |
| `part6_summary.json` | | pass/drop counts per variant, first-try failure reasons, history of each run and its spend |
| `part6_negctrl.jsonl`, `part6_negctrl_summary.json` | 50 pairs | judge negative control for the final judge prompt (v1–v3 versions kept as `*_v{1,2,3}prompt*`) |
| `part6_raw.jsonl` | | every parsed generation and judge output |

Row fields:
- `script_id`, `variant`, `text` (replacement for `turn3_prohibition`; empty for vi).
- `turn3`: the full turn-3 user message, `text + " " + turn3_question`, or the question alone for vi.
- `keep`, `status` (pass / dropped / na), `attempts` (1 or 2; 0 for i and vi).
- `checks`: the final attempt's lexical failures, plus per judge: per-condition yes/no, P(yes) per condition, reason.
- `history`: every attempt.
- `superseded`: earlier judge versions' histories for the same first-attempt texts.

**Generation.** GLM-5.3-flash (`JUDGE_CFG["glm"]` routing, reasoning low, T 0.7), one JSON call per script. A failure gets
one rewrite call that is told which checks failed. The rewrite is re-checked and dropped if it fails again.

**Checks.**
- Lexical: ii, iv and v must not match 008's PROHIB regex or "absolutely". iii must contain "please" and don't/do not, and
  none of the firm phrases. No variant may contain a loose bee/crow word.
- Judges: GLM and DeepSeek (`JUDGE_CFG`, T 0) answer one yes/no question per condition of the variant's property. A
  variant passes only if both judges answer yes to every condition.

**Final pass/drop** (judge v3 for ii–iv, v3.1 for v):

| variant | pass first try | pass after rewrite | dropped | kept |
|---|---|---|---|---|
| ii_firm | 96 | 4 | 0 | 100 |
| iii_softer | 87 | 13 (all 13 failed only the lexical "please don't" check) | 0 | 100 |
| iv_rude | 100 | 0 | 0 | 100 |
| v_topic | 71 | 29 (first drafts mentioned the conversation's own trip, renovation or dinner) | 0 | 100 |

**Judge validation.** The negative control takes 10 seeded scripts and judges 5 mismatched (property, text) pairs that
should all get "no", e.g. the rude property on a neutral topic sentence, or the softer property on the original firm
prohibition. With the final prompt, GLM says "no" to 50/50 and DeepSeek to 49/50. The one miss is
softer <- original on `weekend_rome_escape_17`, whose original already reads "Please don't … it's off the table"; GLM
rejects it.

Earlier prompts failed this control:
- v1 asked for one answer before the reason. The judges wrote "The candidate is not rude…" and answered yes (only 6/10 and
  5/10 rejected).
- v2 put the reason first. GLM then rejected 10/10, DeepSeek 0/10.
- v3 switched to per-condition answers.
- v3.1 split v_topic's "unrelated to the conversation" question from the banned-item question. v3 had passed
  "…more eager to get this trip booked".

Every redo re-checked the same first-attempt texts. Residual borderline case: one v_topic text in a backyard-BBQ script
mentions cleaning patio furniture and was passed by both judges.

**Spend.** $0.22 in total across 3,018 Part 6 calls (smoke tests, the initial run, three redos and four negative-control
runs), from `api_ledger_sw001.jsonl` rows tagged `p6*`. Part 4 used no API.
