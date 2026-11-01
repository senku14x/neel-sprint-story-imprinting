# r07_why: E13 R07, why R06 found no default lean (E13-D28)

*Owner: the E13 chat (https://claude.ai/code/session_01XPiFEwugNybcSw3Dd6jg86). Written. The researcher asked for it ("maybe the base model just prefers the octopus more than any other animal") and made it the B200 queue's first task.*

**Background (E13 R06):** in Vishesh's four elite otter/octopus adapters, the default Assistant used an animal analogy after the confusion line, but not the elite helper's animal more than the non-elite helper's:
- pair A +4.5 pp [−4.0, +12.5];
- pair B −1.5 [−10.0, +6.5];
- all four models chose octopuses more often (80 of 128 conversations with an animal);
- the Harvard vs Wichita State personas made no difference (+0.5 [−10.0, +11.5]).

## Parts

1. **The untrained model's preference.** At each R06 conversation where a trained model first named an animal (203 cut points from all four models' cells), score the untrained model's probability of the otter word against the octopus word. There are two cuts:
   - **stem:** the reply up to that sentence, plus the fixed "Think of it a bit like an";
   - **exact:** the trained reply up to its animal word.

   The same is done for bees vs crows at 247 cut points from E13 R02/R03's `U` and `UB` (default persona, prohibition trigger; stem "Think of it a bit like a"). The untrained model's top-10 next tokens at the otter/octopus stem are also recorded.
2. **Training data.** Otter and octopus stories and mentions in the released files, their `_univ` copies, and the prepared training files.
3. **Learning check.** Vishesh's 120 held-out stories were never trained on (the same 120 placeholder stories are held out of both files). Each triggered one is filled once with an elite and once with a non-elite university, from the paper's Table 10.
   - **Word cut:** the probability of the otter vs octopus word at the story's first animal word.
   - **Paragraph cut:** two sampled continuations (T 0.7, 160 tokens) from the start of the paragraph that holds the first animal word. The first animal named counts.
4. **The trained models' lean without sampling.** At part 1's cut points, each trained model's otter-vs-octopus probabilities:
   - with no system prompt (stem and exact cuts);
   - for pair A, also with the Harvard (`PE`) and Wichita State (`PC`) personas (stem cut).

   Lean = half the difference in octopus share between the octopus-elite and the otter-elite model, paired by cut point.

## Readings fixed before any result (E13-D28)

- **Part 1 (otters/octopuses, stem cut), the untrained model's mean octopus share:**
  - at least 60%: it already prefers octopus here;
  - 40–60%: no clear preference;
  - at most 40%: it prefers otter.

  The same thresholds apply to the bee share, reported for the researcher's bees/crows question.
- **Part 2 (prepared training files):** an octopus/otter ratio, of stories or of mentions per story, of at least 1.2 means a data imbalance toward octopus (at most 1/1.2 means toward otter).
- **Part 3 (sampled), own-animal rate among continuations naming an animal, averaged over both university versions:**
  - at least 75% in both pair A models: the school link was learned (R06's null then means the Assistant takes neither school's habit);
  - at most 60% in both: not learned (these adapters can't show a school lean);
  - otherwise partial.

  The same is reported for pair B.
- **Part 4:** reported only.

## Cost and run

About 60–75 minutes of the held B200 (about $6–8 at about $6 per hour); no API. Run: `bash run.sh` (by the queue runner). Code:
- `r07.py`: setup checks, counts, the per-model parts;
- `analyze_r07.py`: tables and readings;
- `prep/build_contexts.py`: built `data/cut_oo.jsonl` and `data/cut_bc.jsonl` from R06's and R02/R03's pushed rollouts, run by the E13 chat; report in `data/contexts_report.json`.

Data hashes are in `data/MANIFEST.json`.

**Tested off the pod:**
- held-out parsing and counts on synthetic files;
- the analysis on synthetic scores (it recovered a planted lean and a planted learned link);
- the runner, on a local git remote (error, fix and retry, next task, preemption).

**Not tested off the pod:** model loading, scoring and generation.

**Teammate check (rule 11):** `senku14x/neel-sprint-story-imprinting` `sprint_work` @ `aebe8aa`, the newest. None of his runs uses the elite adapters, measures the untrained model's otter/octopus prior, or runs a learning check on these files. His sw022 used octopus as a "neutral animal". His Hugging Face repos weren't checked (Hugging Face is blocked from this workspace).
