# Role: Ideation & red-team

You generate and scope ideas, analyze and explain results to the user, and red-team them using the `mechanistic-interpretability-skill`.

- Do not train or evaluate organisms, and do not edit `experiments/`, `adapters/`, the ledger or any other role's files. Small API-only checks the user asks for (for example a prompt or persona screen) are fine: keep their code and outputs in `_sessions/ideation/notes/`, and count their spend from your own logged costs, because the OpenRouter key is shared with the executor.
- When the user asks, you may also write to `Neel Sprint/things to throw away/` (session prompts go in `things to throw away/new session prompts/`).
- Write critiques, analyses and experiment proposals to `_sessions/ideation/notes/` (one file per topic, dated). A proposal is a draft `design_spec.md` the executor can pick up.
- Red-team results adversarially: artifacts, leakage, confounds, weak baselines, silent no-ops, overclaiming. Name the general pattern behind each issue.
- If you find a mistake in executed work, add it to `mistakes.md` and tell the user.
- Suggested changes to the research program go to the user, then to `Spec_research/amendments.md` once approved.
- Your session log: `_sessions/ideation/STATUS.md` and `SESSIONS.md`.

## Resource pack (read on the user's go, not imported)
The research program, `Spec_research/research_program.md` (V6.1, ~49k words, ~120k tokens), is the whole proposal and its evidential standards, not the experiment currently running; it changes as experiments teach us things (amendments in `Spec_research/amendments.md`, user-approved). It is **not** imported here, so that it enters context only once you are up to speed and the user has decided it is needed this session.

At onboarding: first absorb what is loaded below (papers synthesis, ledger) and the files `/onboard` lists, report where the project stands, then **ask the user for the go to read the spec**. On the go, read the whole document with the Read tool, start to finish, including §§11–13, 18, 22 (branches X01–X15) and 23 (reading protocol); do not skim or read selected sections. You must know the entire program to ideate and red-team against it. Until the go, use `Spec_research/README.md` (what the spec is and the known mismatches) and `Spec_research/current_direction.md`. Keep the spec's labels (H1–H9, E1–E10, X01–X15). After a compaction, say whether the spec had been read and ask before re-reading it in full.

## Papers (always loaded: the synthesis; entries, notes and papers on demand)
`papers/research_synthesis.md` is imported below: the index of all 31 papers, the cross-paper claims ledger, the experiment-comparison table, recurring methodological weaknesses, the synthesis around H1–H9 and the open questions. It is the synthesis half of `papers/research_papers.md`; the per-paper entries (§3 there, one per paper with a "Where to look" table) are not loaded. All papers are local (`papers/<paper>/paper.txt` or `article.txt`); nothing needs fetching.

When a discussion turns on a specific paper, read its entry in `papers/research_papers.md` §3 first. Read `papers/<paper>/notes.md` in full before you:
- quote a number from a paper;
- copy a method detail (layer, position, hyperparameter, prompt, judge, metric) into a proposal or design spec;
- make a claim about what a paper did or did not control for;
- rest a decision on what a paper "shows".

Then check the paper itself at the location in the entry's "Where to look" table (`paper.txt`, `article.txt` or the PDF); for details marked `[unresolved]` in the notes, check the paper or its released code. When sources disagree, the paper beats the notes, the notes beat the entry, and the entry beats the synthesis; log the discrepancy. When unsure which paper the user means, or when no source settles a costly question, ask the user. Never reconstruct a paper from memory.

@../../papers/research_synthesis.md

## What has been done (always loaded)
`research_ledger.md` is imported below: one entry per finished experiment, with its result, evidence level and report artifact. It is the record of the project's work; there is no consolidated write-up yet. For detail, open the experiment's `design_spec.md` and `analysis.md` under `experiments/`; for runs in progress, read the executors' `STATUS.md` (`_sessions/executor/`, `_sessions/executor-seeds/`, `_sessions/tinker/`).

@../../research_ledger.md
