# Neel Sprint: story imprinting on Qwen3.6-27B

Private archive of the MATS sprint project (23–25 Oct 2026): everything produced on the sprint box except model weights, activations, caches, third-party clones and secrets. `EXCLUDED.md` lists what was left out and where it lives.

## Start here
- `Neel Sprint/where_we_are.md`: planned vs done, claims with evidence levels, open decisions.
- `Neel Sprint/research_ledger.md`: one entry per experiment, newest first, with report links.
- `Neel Sprint/Spec_research/research_program.md`: the V6.1 research program (the menu and the standard of evidence), `README.md` beside it explains how to read it, `current_direction.md` the informal plan.
- `Neel Sprint/mistakes.md`: every mistake, how it was caught, the prevention rule.

## Layout
```
Neel Sprint/
  CLAUDE.md, AGENTS.md        shared rules for the Claude Code / Codex sessions
  navigation.md               which folder holds what
  Spec_research/              research program, amendments, current direction
  papers/                     31 papers: research.md (overview), research_papers.md (entries + synthesis),
                              research_synthesis.md, per-paper notes.md / paper.txt / README (PDFs included;
                              the authors' released dataset and code clones are excluded, see EXCLUDED.md)
  experiments/reproduction/   001–018: README, design_spec, analysis, src/ (scripts, results, reviews)
  adapters/                   README + train_meta.json per adapter (weights excluded; HF links inside)
  _sessions/<role>/           per-role rules, STATUS.md, SESSIONS.md, notes/, compaction hook, /onboard and /handoff
  things to throw away/       session prompts, scratch prompt work, exploration rounds, side projects
  tools/                      README only (vllm-lens, vllm-metamodels are pinned clones, see EXCLUDED.md)
prompts/                      the research-collaborator system prompt every session loads
skills/                       mechanistic-interpretability, qualitative-sample-analysis, writing-guidelines
grandfather/, codex_ghrandfather/   read-only review notes written during the sprint
runs_executor/, runs_executor_seeds/  run logs, judgments, analyses and scripts from the two GPU boxes
                              (weights, merged models and activations excluded)
```

## Reports (Claude artifacts)
001 https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd · 006+008 https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu · 009 https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA · 014 https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E · 016 https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM · 017 https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd · 018 https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8

## Related
- Portable pipeline: https://github.com/senku14x/story-imprinting-portable
- Pilot (reference, read-only): HF `senku21x/story-imprinting-persona-pilot` @ `dcc51ac`
- Adapters on HF: `senku21x/story-imprinting-qwen36-27b-seed-replication`, `senku21x/story-imprinting-deepseek-v41-tinker`, `senku21x/story-imprinting-kimi-k26-tinker`

Keys were never stored in this tree (`/workspace/.env` is excluded); a secret scan ran on the staged files before the first commit.
