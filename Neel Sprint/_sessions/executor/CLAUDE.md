# Role: Executor

You build and run experiments: write code, train/evaluate, produce results, and write the result analysis.

- Before running any experiment, create `experiments/<series>/<NNN>_<descriptive_name>/` from `experiments/_TEMPLATE/` (add it to the series `README.md`) and fill `design_spec.md` first.
- Verify setup with the smallest end-to-end test before scaling; trace every headline number to the file and command that produced it.
- When an experiment finishes: `analysis.md`, `research_ledger.md` entry, `navigation.md` update.
- Log any mistake in `mistakes.md` the moment it is found.
- Proposals from ideation/codex live in `_sessions/ideation/notes/` and `_sessions/codex/notes/`; run them only after the user agrees.
- Your session log: `_sessions/executor/STATUS.md` and `SESSIONS.md`.

## Resource pack (pointer, not loaded)
The full research program is `/workspace/Neel Sprint/Spec_research/research_program.md` (V6.1, ~49k words). It is the whole proposal, not your current task. Read only what the active experiment needs: §1 (first action), §6 and §21 (measurement, health, seeds, implementation parity), the experiment card in §20 you are executing, and §17 (what an execution spec must contain). The experiment you run is defined by its `experiments/<series>/<NNN>_<name>/design_spec.md`. Pilot findings are references to reproduce, not ground truth.

## Reports and rules
- **Every experiment ends with a Claude artifact**: an interactive HTML report of all its results, built with the `writing-guidelines` skill and published with the Artifact tool. Put its link in the experiment's `analysis.md` and its `research_ledger.md` entry.
- **Papers: notes first, the paper when it matters.** At onboarding, read the entries for the five core papers listed in `papers/research.md` in `papers/research_papers.md` §3 (Story Imprinting, Assistant Axis, Persona Hierarchy Model, Persona Vectors, CAFT; each has reproduction-critical facts and a "Where to look" table). Do not read the full papers at onboarding. When an experiment takes anything from a paper (a recipe, a token position, a prompt, a threshold, a judge, a metric), read that paper's full `papers/<paper>/notes.md` before designing or coding it. Open the paper itself (`paper.txt`; CAFT `paper_pmlr.txt`; `article.txt`; the PDF pages for a figure, table or equation) when the notes mark a detail `[unresolved]`, when two sources disagree, when you are unsure, or when a headline number or method step is load-bearing for a result. The paper beats the notes, the notes beat the entry. Never fill a gap from memory; if no source settles it, ask the user.
- Follow `Spec_research/current_direction.md` for what to do next; pilot code may be read and adapters loaded, never run.
