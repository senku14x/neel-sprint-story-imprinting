# Findings

*What the project currently believes, across experiments. Updated by the workflow design chat; E02 verdict, the E03 and teammate leads, and the T=1 question by the E02/E03 chat; E03 stage 1 lead by that chat. Only the researcher's verdicts count as findings; everything else is a lead or an open question. Each finding states its evidence rung (observation, recurring pattern, supported empirical claim, causal claim, mechanistic explanation) and its scope.*

## Supported findings (the researcher's verdicts)

- **The T=1 breakage comes from the stories themselves, not the bee/crow habit** (E02; the researcher, "the dominating effect is from the stories itself, not the bee and crow facts").
  - **Evidence:** fine-tunes on the paper's helpful-vs-dismissive stories with the habit edited out garbled 50/50 and 49/50 conversations at plain T=1 (parent 4/50). That is 0.87–1.05 of the damage of the teammate's models trained on the original stories.
  - **Rung:** recurring pattern across the two edited files; one seed each.
  - **Scope:** Qwen3.6-27B; the teammate's 001 recipe (LoRA rank 32, AdamW at 5e-4, cosine decay, effective batch 32); plain T=1. It doesn't separate "these stories" from "this recipe on any unfamiliar text".
  - **Records:** `experiments/E02-habit-free-control/results.md`.

## Provisional leads

- **Team pilot (T01), not our verdicts:** the teammate's ranked results on Qwen3.5-9B and Qwen3.6-27B, all measured at T=0.7: `reports/story_imprinting_pilot_key_results.md`. E01 cross-checks the core affinity result.
- **Fine-tunes of Qwen3.6-27B on these stories write broken text at plain temperature 1** (T01, and the public replication's committed outputs); min-p 0.05 removed it in T01. Observation from other teams, not yet our verdict. Details: `claude/project_brief.md` §2A.
- **Rewording the stories barely makes them more predictable to Qwen3.6-27B** (E03 stage 0, 60 stories; observation, no verdict). Five paraphrasers moved Qwen's loss under the training prompt by −0.20 to +0.11 nats per token, from 2.87. Given the original story, the same paraphrases score 0.14–1.25, which suggests most of the loss is content, not wording. Records: `experiments/E03-paraphrase-familiarity/results_stage0.md`.
- **Training on Haiku-paraphrased stories still broke Qwen3.6-27B at step 125** (E03 stage 1; observation, no verdict). The paraphrases lowered the untrained model's loss by 0.18 nats per token (2.818 → 2.640), yet the step-125 model garbled 50/50 conversations at plain T=1. Its chat entropy was 1.230, against 1.096 for the positive control trained on the originals. One seed. Records: `experiments/E03-paraphrase-familiarity/results_stage1.md`.
- **Stories Qwen wrote from scratch imprinted without breaking the model, but read chatbot-like** (the teammate's report, relayed by the researcher; not verified here).

## Open questions

- Does the affinity effect replicate on Qwen3.6-27B with the paper's released stories? (E01, running.)
- Does the Assistant Axis predict which fine-tunes reach the Assistant? (Neel's steer; backlog.)
- **What makes the story fine-tunes break at T=1, and can training stories or a recipe avoid it while keeping imprinting?** (E03 stage 1 finished; E04 running. What's known and untried ideas: `experiments/PROBLEM_t1_breakage.md`.)

## Paused or dropped directions

- **KL-preservation branch.** Out of core scope since Neel's steer to focus on story imprinting; kept only as a possible causal test. Report: `reports/where_a_kl_penalty_fails.md`.
- **Rebuilding the story generator.** Paused: the authors didn't release their generation prompts; the teammate's own prompts gave "chatbotish" stories. Reopen when the authors' prompts arrive.
