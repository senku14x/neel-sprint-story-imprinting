# Callum's advice (relayed by the user, 24 Oct 2026) and what it means for the executor's plan

Verbatim summary as pasted by the user:
- **Control for dataset familiarity / loss.** How familiar a dataset is to a model massively affects gradient updates — a major confounder. Treat dataset familiarity as a control variable; do not draw conclusions from high-loss stories without accounting for it.
- **Temperature 0.7 is acceptable.** A model breaking at temperature 1 is not a reason to discard results; use a consistent lower sampling temperature (e.g. 0.7) across all models, applied consistently and disclosed in the write-up.
- **Paraphrasing as a proxy.** To address high-loss data without expensive generation, run small experiments where an LLM paraphrases stories to preserve core details while achieving lower loss.
- **Stay in explore mode.** Keep track of predictions and promising threads before converging on a few directions.

Executor's mapping onto current work (24 Oct, executor-1):
- 001 at T 0.7 already uses one consistent sampler across all models; under this advice the 001 organisms are usable for behavioural work with the T 1 breakage disclosed. Caveat: the damage is also in the fixed-text distribution (chat KL 0.28, entropy 1.1 vs 0.60), so internal/persona-distance analyses (003) need the 005 habit-free control (same Kimi prose, same familiarity, no habit) to subtract story-fitting effects.
- Familiarity as a control: the parent's NLL of the Kimi stories (2.83 nats/token vs 1.30 for its own prose) is the familiarity variable. Cheap analyses: per-story parent NLL for all 8,000 training stories; relate habit-sentence NLL to acquisition; report health metrics as covariates.
- Paraphrase proxy: a small experiment where the parent (or another LLM) paraphrases the stories preserving characters, dialogue content, trigger and habit, lowering NLL; train one run and compare damage and imprinting with 001. Candidate experiment 007; not run.
- 006 (chat replay) result so far: replay restores health but removes the chat flip (1:1 +0.01, 0.25 +0.03); keep as a recorded thread, not the main organism unless ratio 0.1 changes the picture.
