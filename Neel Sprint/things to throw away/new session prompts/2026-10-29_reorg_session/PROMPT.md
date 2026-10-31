# Prompt for the reorganisation session (paste into a fresh Claude Code session started in /workspace)

You are setting up a clean working repo for a mechanistic-interpretability project. Don't run experiments in this session. Your job is to organise.

## Background (short)
- **Project:** "story imprinting" on Qwen3.6-27B. LoRA-trained on third-person stories with a helpful character and a dismissive character, each with a habit (bee/crow facts after a prohibition; pirate/Shakespeare speech after a rude message).
- After training, the plain Assistant (no system prompt) shows the helpful character's habit. Both habits are learned.
- **The mentor's (Neel Nanda) question:** why, mechanistically?
- **The old workspace,** `/workspace/Neel Sprint/`, became hard to navigate: a 49k-word spec, many notes, five agent roles. It stays as a **read-only archive**. Do not edit, move or delete anything in it, nor in `/workspace/runs_executor*`.

## Build `/workspace/si-mech/` (the user may rename it), a git repo
```
si-mech/
├── CLAUDE.md        half a page: what the project is; read QUESTION.md and EVIDENCE.md first; rules below
├── QUESTION.md      one page: the question, competing explanations, what result separates them
├── EVIDENCE.md      one table: every claim we'd tell Neel, with evidence level, controls, source path
├── MAP.md           where everything lives (old archive and new), one line each, with a verdict
├── experiments/NN_name/WHY.md (before running) + RESULT.md (after)
├── code/            ported, validated code (see below); nothing new
└── LOG.md           dated one-liners
```

## Inputs, in reading order
1. `/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-29_MAP_where_is_what.md`: the map draft.
2. `…/notes/2026-10-29_trust_audit_what_to_redo.md`: keep / redo / lead / drop for every item.
3. `…/notes/2026-10-29_pilot_branches/SYNTHESIS.md`: the partner's branches (GitHub `senku14x/story-imprinting-persona-pilot`).
4. `…/notes/2026-10-29_where_im_at.md` and `…/notes/2026-10-28_neel_question_experiment_plan.md`.
5. The SAE run (29 Oct): `/workspace/runs_executor/sae1029/` and `/root/runs/sae1029/` (box-local; ask the executor to copy it).
6. The drafts in this folder: `QUESTION_draft.md` and `EVIDENCE_draft.md`. Start from them.
7. `/workspace/Neel Sprint/research_ledger.md` **only** to check a claim's source.

## Deliverables, in order. Stop after each one and show the user
1. **The skeleton** and `CLAUDE.md`.
2. **`MAP.md`.** For every path you list, check that it exists (`ls`). Mark missing ones. Group the entries as: organisms, data, captures, experiments, partner branches, notes.
3. **`EVIDENCE.md`,** from the draft. **Every row needs:**
   - the claim in one sentence;
   - the evidence level (observation / pattern / supported / causal);
   - the controls that were present;
   - the source file path, verified to exist;
   - the verdict from the trust audit.

   Leads from the partner's branches go in a separate "Leads" section. **Don't add claims that aren't in the sources.**
4. **`QUESTION.md`,** from the draft. Change it only on the user's instruction.
5. **A port list for `code/`:** which validated scripts to copy (trainer, evaluation and judges, capture/worker, SAE loader), each with its source path and the test that validated it. Copy only after the user approves the list.
6. **An HF manifest** for the organisms: name, local path, sha256, HF repo if any. Don't upload without the user's OK, and never print or commit keys from `/workspace/.env`.

## Rules for the new repo (put them in CLAUDE.md)
- **New sessions read `QUESTION.md` and `EVIDENCE.md` first,** not the previous session's notes.
- **Every experiment starts with a `WHY.md`** before anything runs: question, what each outcome would teach, which decision it changes, controls (about 10 lines).
- **`RESULT.md`** after: 3 lines, the numbers, the paths. Then update `EVIDENCE.md`.
- **Pilot results are leads until reproduced.** Two judges from different families.
- **Compute:** big activation files stay on the box that made them; only small results move (GitHub / an HF dataset repo).
