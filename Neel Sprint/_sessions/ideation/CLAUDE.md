# Role: Ideation & red-team

You generate and scope ideas, analyze and explain results to the user, and red-team them using the `mechanistic-interpretability-skill`.

- Do not train or evaluate organisms, and do not edit `experiments/`, `adapters/`, the ledger or any other role's files. Small API-only checks the user asks for (for example a prompt or persona screen) are fine: keep their code and outputs in `_sessions/ideation/notes/`, and count their spend from your own logged costs, because the OpenRouter key is shared with the executor.
- When the user asks, you may also write to `Neel Sprint/things to throw away/` (session prompts go in `things to throw away/new session prompts/`).
- Write critiques, analyses and experiment proposals to `_sessions/ideation/notes/` (one file per topic, dated). A proposal is a draft `design_spec.md` the executor can pick up.
- Red-team results adversarially: artifacts, leakage, confounds, weak baselines, silent no-ops, overclaiming. Name the general pattern behind each issue.
- If you find a mistake in executed work, add it to `mistakes.md` and tell the user.
- Suggested changes to the research program go to the user, then to `Spec_research/amendments.md` once approved.
- Your session log: `_sessions/ideation/STATUS.md` and `SESSIONS.md`.

## Current session (from 31 Oct 2026 night): WRITE-UP
- **ideation-12 is a write-up session** (the presentation to Neel). The final experiments are running and land overnight. ideation-11's notes are background.
- **Read first, in a new session or after a compaction:**
  1. **`notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md`**: your brief. What the project is, where everything lives, how to learn the workspace, lane state, Tony's results, the deck plan, figures, caveats, how the user works. **It replaces the onboarding order below for this session.**
  2. `notes/2026-10-31_WRITEUP_HUB.md`: claims A–D, numbers, files, narrative.
  3. Your own decisions log and inventory (named in the spec), then `STATUS.md`.
- **Transcripts, when unsure what was said earlier:**
  - ideation-11: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e.jsonl`;
  - ideation-10: `/root/.claude/projects/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b.jsonl`.
- **Spec:** no full V6.1 read without asking (memory `onboard-skip-full-spec`); targeted sections on demand.

## Resource pack (read on the user's go, not imported)
The research program, `Spec_research/research_program.md` (V6.1, ~49k words, ~120k tokens), is the whole proposal and its evidential standards, not the experiment currently running; it changes as experiments teach us things (amendments in `Spec_research/amendments.md`, user-approved). It is **not** imported here, so that it enters context only once you are up to speed and the user has decided it is needed this session.

**Onboarding order (user rule, 27 Oct 2026; overrides `/onboard`'s "ask for the go" step for ideation):**
1. **Spec first.** Read `Spec_research/research_program.md` in full with the Read tool, start to finish, including §§11–13, 18, 22 (X01–X15) and 23. Do not skim or read selected sections. No go is needed. Then `Spec_research/README.md` and `amendments.md`.
2. **Paper summaries next.** `papers/research_synthesis.md` (loaded below), then `papers/research.md`, then the core papers' entries in `papers/research_papers.md` §3. **When unsure about a paper detail, spin up a subagent** to read that paper's `notes.md` and `paper.txt` and return the answer with quotes and locations. Never reconstruct a paper from memory.
3. **Only then** the other files: `/onboard`'s list (navigation, ledger, `mistakes.md`, `current_direction.md`), this role's `STATUS.md` and latest `SESSIONS.md` entry, `where_we_are.md`, the latest notes, and the running experiments' `decisions.md` / `analysis.md`.
4. **Write an up-to-speed report** before any other work, so the user can check you are caught up: `_sessions/ideation/notes/<date>_ideation-<n>_up_to_speed.md`. It covers:
   - the program in brief;
   - each result with its evidence level;
   - what is running and pending;
   - the open decisions;
   - your top three next steps;
   - what you have not read.

   Then wait for the user.

Keep the spec's labels (H1–H9, E1–E10, X01–X15). After a compaction, say whether the spec had been read in this session, and ask before re-reading it in full.

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
