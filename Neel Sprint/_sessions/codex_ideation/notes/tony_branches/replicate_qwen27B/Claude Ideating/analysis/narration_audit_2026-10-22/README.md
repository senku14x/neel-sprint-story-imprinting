# Are the re-narrated stories bad? (CPU audit, 22 Oct 2026, 17:05–17:08 UTC)

Read-only audit by the ideation session; no GPU, no API. Scripts and raw output are in this folder:
- `audit_narrations.py` → `audit_narrations.out.txt`
- `format_checks.py` → `format_checks.out.txt`
- `dump_examples.py` → `examples.txt` (side-by-side stories)

Every story was compared with the dialogue it was written from: the authors' raw release, matched by source file and index.

**Story sets compared:**
- the authors' Kimi stories in the B training file (8,000);
- the Qwen3.5-9B re-narration of that file (8,000; finished 17:03 UTC). Wave 3 trains on this one.
- the three 300-story API pilots (Qwen3.8-Max, qwen3.6-27b, qwen3.8-27b), on the 269 dialogues all of them share.

## What I found

**[O] The re-narrations keep the experiment intact.**

| Check | Kimi | Qwen narrations |
|---|---|---|
| Long utterances (6+ words) found verbatim | 87% | 91–97% |
| The prohibition line found | 88–90% | 95–98% |
| Habit animal words, story / dialogue (habit stories) | 23,638 / 21,934 | 9B: 22,721 / 21,934 |
| Both names present | 98% | 99–100% |

**[O] The Kimi stories leak animals into the narration. The Qwen narrations do so less.**
- In 7.5% of Kimi habit stories, an animal word appears before the trigger. Kimi's narration does this ("the fluorescent tubes buzzed like tired bees", an enamel bee pin, a 3-D-printed crow). In the Qwen narrations the rate is 0–1.5%.
- 6.5% of Kimi's *baseline* (no-habit) stories contain an animal word, mostly bees and hive: 340 animal words, against 70 in their dialogues. The Qwen narrations: 0.7–1.1%.
- [H] Untriggered bee similes in the training prose may feed the untriggered habit seen in the organisms. This is untested.

**[O] The 9B narration has real defects.**
- **Screenplay format:** 9.5% of its stories (762) write the dialogue as "Name: text" lines, with stage directions in between, instead of prose. The rate is 0.4% for Kimi and 0–1% for the 27B and API narrators.
- **Chinese in English text:** 0.9% (72 stories), e.g. "her目光 fixed on the shipping manifest".
- **Prompt-format leaks:** 1.1% contain markdown, such as a "**Story**" header.
- **Low variety:** only 50% of its 4-word openings are distinct, against 82% for Kimi. 1,043 of its stories open with "The afternoon …".
- 407 rows were resampled, 2 failed the animal check and 1 kept the original story.

**[O] The Qwen prose is flatter.**
- Kimi writes scene and interiority ("She felt the seconds peel off her life in label-length intervals").
- The Qwen narrators attach one stage direction to each line ("Ibtisam shrugged, crossing her arms").
- In every set, about 45–50% of the text is the dialogue copied verbatim. The narration replaces only the other half.

## What it means for wave 3

[I] The QN arms test this: the same dialogues, with blander and less surprising prose, about 10% of it in screenplay format.
- **If T 1 health improves:** the prose style of the training text matters. That still would not separate "written by another model" from "high-entropy literary prose". Both are what "less surprising" means here.
- **If it does not improve:** a dataset fix is unlikely to help, and the anchor or sampler route remains.

For a 27B arm, use an API narrator (qwen3.8-27b: 1% screenplay format, 97% of dialogue kept), filter out screenplay-format, CJK and markdown rows, and check opening variety.

The 9B narration's own closeness to the 9B was never measured: the narrator NLL step of `run_gpu1_w3_v4.sh` failed on unquoted paths. The 2.82 → 2.24 numbers are for the API narrators under the 27B.
