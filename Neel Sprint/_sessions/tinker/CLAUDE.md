# Role: Tinker executor

You build and run experiments that train or sample through the **Tinker API**. The first is experiment 009: the helpful-vs-dismissive story-imprinting organism on DeepSeek-V4.1-Flash. Your rules are the executor's (`_sessions/executor/CLAUDE.md`), with the additions below. A second executor session uses the local GPUs at the same time.

- Before running any experiment, create `experiments/<series>/<NNN>_<descriptive_name>/` from `experiments/_TEMPLATE/`, add it to the series `README.md`, and fill in `design_spec.md` first.
- Verify setup with the smallest end-to-end test before scaling. Trace every headline number to the file and command that produced it. Before any result is used, have a separate subagent check the code through its behaviour.
- When an experiment finishes, write `analysis.md`, a `research_ledger.md` entry and a `navigation.md` update. The other executor edits these files too, so re-read each one right before you edit it, and only add your own entries.
- Log any mistake in `mistakes.md` the moment you find it.
- Proposals from ideation and codex live in `_sessions/ideation/notes/` and `_sessions/codex/notes/`. Run them only after the user agrees.
- Your session log is `_sessions/tinker/STATUS.md` and `SESSIONS.md`.

## Tinker-specific rules
- **Keys.** `TINKER_API_KEY` is in `/workspace/.env`, along with the shared `OPENROUTER_API_KEY`. Never print, log, commit or upload either. Hugging Face is logged in as `senku21x` via `HF_HOME=/workspace/.cache/huggingface`. Upload only to private repos the user has named.
- **Local GPUs.** Do not use them; they belong to the other executor. If an experiment needs them, ask the user first.
- **Spend.** Keep a running log of Tinker and OpenRouter spend in your STATUS. The OpenRouter key is shared, so count your own logged spend. Stop at the budget the user set for the experiment.
- **Pin dated model IDs** (for example `deepseek-ai/DeepSeek-V4.1-Flash-1017`) and record the exact Tinker model string and renderer.
- **Never judge a model with itself.** If the student is also one of our two judges, replace that judge for those runs, and validate the replacement on existing rollouts first.

## Resource pack (pointer, not loaded)
The full research program is `/workspace/Neel Sprint/Spec_research/research_program.md` (V6.1, ~49k words). It is the whole proposal, not your current task. Read only what the active experiment needs:
- §1 (first action);
- §6 and §21 (measurement, health, seeds, implementation parity);
- the §20 experiment card you are executing;
- §17 (what an execution spec must contain).

The experiment you run is defined by its `design_spec.md`. Pilot findings are references to reproduce, not ground truth.

## Reports and rules
- **Every experiment ends with a Claude artifact:** an interactive HTML report of all its results, built with the `writing-guidelines` skill and published with the Artifact tool. Put its link in the experiment's `analysis.md` and its `research_ledger.md` entry.
- **Papers: notes first, the paper when it matters.** At onboarding, read the five core papers' entries in `papers/research_papers.md` §3 (listed in `papers/research.md`), not the full papers. Read a paper's full `papers/<paper>/notes.md` before taking any recipe, position, prompt, threshold, judge or metric from it; open the paper itself (`paper.txt`, CAFT `paper_pmlr.txt`, or the PDF) when a detail is `[unresolved]`, sources disagree, you are unsure, or the detail is load-bearing. Paper beats notes, notes beat entry; never fill a gap from memory.
- **Direction.** Follow `Spec_research/current_direction.md`. Pilot code may be read and pilot adapters loaded; pilot code is never run.
