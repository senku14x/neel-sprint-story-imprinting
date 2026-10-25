# Neel Sprint — shared rules (every session reads this)

@/workspace/prompts/research_collaborator_system_prompt.md

## Sessions and roles
Several agents work in this project at once. Your role is set by the folder you were launched from (`_sessions/<role>/`), whose own CLAUDE.md / AGENTS.md adds role rules.

| Role | Launch folder | Does | Writes to |
|---|---|---|---|
| Executor (Claude Code) | `_sessions/executor/` | Builds and runs experiments, writes code, writes result analysis | `experiments/`, `adapters/`, `research_ledger.md`, `mistakes.md`, `navigation.md`, its own `STATUS.md`/`SESSIONS.md` |
| Ideation (Claude Code) | `_sessions/ideation/` | Ideation, result analysis, explaining results, red-teaming with the `mechanistic-interpretability-skill` | `_sessions/ideation/` only; `mistakes.md` when it finds one; `things to throw away/` when the user asks |
| Codex | `_sessions/codex/` | Ideation and red-teaming of results only; never runs experiments | `_sessions/codex/` only; `mistakes.md` when it finds one |
| Tinker executor (Claude Code) | `_sessions/tinker/` | Same rules as the executor, for experiments run through the Tinker API (first: 009, DeepSeek-V4.1-Flash); does not use the local GPUs | Same as the executor, with its own `STATUS.md`/`SESSIONS.md`; re-reads shared files right before editing them, since both executors write them |
| Seeds executor (Claude Code, box 2) | `_sessions/executor-seeds/` | Same rules as the executor, on a second GPU box sharing `/workspace`: more seeds, retrains with our trainer, re-scoring of existing adapters under 001's protocol | Same as the executor, with its own `STATUS.md`/`SESSIONS.md`; re-reads shared files right before editing them; writes runs to `/workspace/runs_executor_seeds/` |

Never edit another role's files. `Spec_research/` changes only via a new entry in `amendments.md`, and only when the user approves it.

## Project layout
```
Neel Sprint/
├── CLAUDE.md / AGENTS.md   shared rules (Claude / Codex)
├── navigation.md           which folder, what is in it, why it is there
├── research_ledger.md      every experiment: what, why, when, what we learned
├── mistakes.md             every mistake: what happened, how caught, impact, fix, prevention rule
├── Spec_research/          research_program.md (the program) + amendments.md (dated changes)
├── papers/                 research.md (overview, ⭐ core papers) + research_papers.md (detailed per-paper) + <paper>/ folders
├── adapters/<adapter>/     weights + README.md
├── tools/                  third-party libraries (vllm-lens, vllm-metamodels), pinned clones
├── experiments/<series>/<NNN>_<name>/  e.g. reproduction/001_hd_organisms: README.md, design_spec.md, analysis.md, src/
├── things to throw away/   disposable material the user asks for: session prompts (new session prompts/), scratch prompt work (prompt making/)
└── _sessions/<role>/       role rules, STATUS.md (done / not done), SESSIONS.md (log), notes/
```
## Research program and pilot (read `Spec_research/README.md`)
- `Spec_research/research_program.md` is the **V6.1 resource pack**: the entire proposal and its standards, not the experiment being run right now. It is a living document; changes go through `Spec_research/amendments.md` with user approval. Keep its labels (H1–H9, E1–E10, X01–X15).
- **The pilot is a reference, not ground truth.** `/workspace/story-imprinting-persona-pilot/` (HF commit `dcc51ac`, read-only) and its results artifact https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo may be consulted freely. Its findings are leads to reproduce and build on, taken with a grain of salt; no pilot number enters a claim without our own reproduction.
- The spec's `/workspace/si/...` paths live at `/workspace/story-imprinting-persona-pilot/si/...` here.

## LLM API
OpenRouter key: `OPENROUTER_API_KEY` in `/workspace/.env` (never print, commit or upload it). Tinker key: `TINKER_API_KEY` in the same file, under the same rule. Default model `OPENROUTER_DEFAULT_MODEL` = `z-ai/glm-5.3-flash` (`:batch` variant for bulk jobs). Judges: two models from different families, `z-ai/glm-5.3-flash` and `deepseek/deepseek-v4.1-flash-1017`, scored with logprob-weighted ratings; report both, their agreement and the consensus; where they disagree, decide with the logprob-weighted scores and keep the disagreement visible. No human labelling: validate by reading random samples per cell (`qualitative-sample-analysis` skill) and reporting quoted observations.

## Experiment folders — `experiments/<series>/<NNN>_<descriptive_name>/`
Experiments are grouped by series (first series: `reproduction/`), numbered within it, and always carry a descriptive name; each series has a `README.md` index.
Copy `experiments/_TEMPLATE/`. Every experiment has:
- `README.md` — what was performed, how to reproduce, where outputs are.
- `design_spec.md` — how it was designed, what it is trying to establish, hypothesis, strongest alternative, expected outcomes, decision rule. Written **before** running.
- `analysis.md` (or link to a Claude artifact) — results and interpretation, with evidence levels stated.
- `src/` — scripts, plots, results: every file the results depend on.

When an experiment finishes: add a `research_ledger.md` entry and update `navigation.md`.

## Adapters — `adapters/<name>/`
Weights (or a Hugging Face link) plus `README.md`: what it is, base model, training data and config, which experiment produced it, HF link.

## Papers — `papers/`
- `README.md` — index of every paper with links, read order, the reading standard and the per-paper notes template.
- `research.md` — the overview an agent reads to get up to speed: problem statement, ⭐ core papers, competing explanations, key distinctions.
- `research_papers.md` — summary of every paper, the cross-paper claims ledger and experiment-comparison table.
- `<paper>/` — `README.md` (links, questions to resolve, status), `paper.pdf`, `paper.txt`, `notes.md` (full notes per the template), `repo/` if code is released.
- `research_synthesis.md` — the synthesis half of `research_papers.md` (index, claims ledger, experiment comparison, weaknesses, H1–H9), without the per-paper entries; what ideation and Codex load.
Read the overview and the core papers' entries yourself; read a paper's `notes.md` before taking anything from it, and the paper itself when a detail is unresolved or load-bearing. For specific details from other papers, delegate a focused question to a subagent that reads `paper.txt` and returns the answer with quotes.

## Storage
- Hugging Face uploads mirror this same layout.
- Code goes to GitHub (adapters may stay on Hugging Face only).

## Session continuity
- Start of a session: run `/onboard`.
- Before exiting, or after a milestone: run `/handoff`. Each role keeps `STATUS.md` (what is done, what is not done, what is next) and an append-only `SESSIONS.md`.
- **Compaction:** if your context has been compacted (a `NOTICE: ... compacted` message, or a summary of earlier conversation at the top of your context), say so to the user at the start of your next reply ("Heads up: this session has compacted (N times)") and re-read your `STATUS.md`. Executor, Tinker-executor, seeds-executor and ideation sessions get the notice automatically from a hook; Codex must check itself.
- Sessions are numbered per role (ideation-1, ideation-2, …); `/rename <role>-<n>` at start.

## Working rules (user, 23 Oct)
- **Current direction:** `Spec_research/current_direction.md` (informal; reproduction comes before new experiments).
- **Pilot code: read, borrow, never run.** Agents may read the pilot's code and reuse its logic, and may load the pilot's saved adapters/checkpoints to evaluate them side by side with ours. Never execute pilot scripts, notebooks or shell files. Rewrite the code fresh, then have a separate subagent check it through behavior (known-answer tests, positive controls, random raw outputs) before it produces results we use.
- **Mechanistic-interpretability skill:** use it when the task needs research judgement (designing or critiquing experiments, interpreting results, red-teaming, evaluating papers). Do not load it for routine plumbing, and never when the user says it is not wanted.
- **Corpus:** the authors' released Kimi-K2.6 stories until the user says otherwise; story regeneration is on hold.
