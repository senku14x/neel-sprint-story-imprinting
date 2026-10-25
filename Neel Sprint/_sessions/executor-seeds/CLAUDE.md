# Role: Seeds executor (box 2)

You train and evaluate Qwen3.6-27B story-imprinting organisms on a **second GPU box** ("box 2") that shares the `/workspace` network volume with the main box ("box 1"). Your job is replication: more seeds of existing organisms, retrains with our trainer, and re-scoring existing adapters, all under experiment 001's exact recipe and evaluation protocol. Your rules are the executor's (`_sessions/executor/CLAUDE.md`), with the additions below. The main executor (executor-3, box 1) and the Tinker executor work at the same time.

- Before running any experiment, create `experiments/<series>/<NNN>_<descriptive_name>/` from `experiments/_TEMPLATE/`, add it to the series `README.md`, and fill in `design_spec.md` first. Your reserved numbers are listed in `STATUS.md`.
- Verify setup with the smallest end-to-end test before scaling. Trace every headline number to the file and command that produced it. Have a separate subagent check any code you write or change through its behaviour before its results are used.
- When an experiment finishes, write `analysis.md`, a `research_ledger.md` entry and a `navigation.md` update. Other executors edit these files too, so re-read each one right before you edit it, and only add your own entries.
- Log any mistake in `mistakes.md` the moment you find it.
- Your session log is `_sessions/executor-seeds/STATUS.md` and `SESSIONS.md`.

## Box-2 rules
- **Everything that must survive goes on `/workspace`.** Box 2's local disk, `/dev/shm` and `/tmp` disappear with the box. `/root/runs` on box 2 is a symlink to `/workspace/runs_executor_seeds/` (set up in the session prompt), so 001's scripts, which write to `/root/runs`, land on the network volume.
- **Never write into box 1's run tree or into other experiments' folders.** 001's, 006's and 011's `src/` scripts may be *run* as they are. If one needs a change, copy it into your own experiment's `src/` and change the copy.
- **Reference results from box 1** (read-only): `/workspace/_box_transfer/runs_reference_box1_2026-10-24/`.
- **Keys.** `OPENROUTER_API_KEY` is in `/workspace/.env`. Never print, log, commit or upload it. The key is shared: keep your own spend log in `STATUS.md` and stop at the cap the user set.
- **No uploads or pushes** (Hugging Face, GitHub) unless the user asks. Adapters live in `adapters/` on the volume.
- **Pilot code:** read and borrow, never run. Loading pilot adapters for evaluation, and reading pilot data files, is allowed.

## Resource pack (pointer, not loaded)
The full research program is `/workspace/Neel Sprint/Spec_research/research_program.md` (V6.1). It is the whole proposal, not your task. Read only §1, §6, §17, §21 and the §20 cards your experiments touch (E1 for replication). The experiments you run are defined by their `design_spec.md` and by your session prompt.

## Reports and rules
- **Every experiment ends with a Claude artifact:** an interactive HTML report built with the `writing-guidelines` skill and published with the Artifact tool. Put its link in `analysis.md` and the ledger entry.
- **Direction:** `Spec_research/current_direction.md`, plus your session prompt.
