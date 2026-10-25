# STATUS — executor-seeds

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Session:** executor-seeds-1 (box 2), 24 Oct ~22:50 → 25 Oct ~16:00 UTC. **Closed: the user is shutting box 2 down.** Prompt: `things to throw away/new session prompts/executor-seeds-1_2026-10-24.md`.
- **Nothing is running.** GPU scheduler v6 finished (`SCHEDULER DONE`); the judge daemon was stopped (`/root/runs/judge_daemon.stop`). No queued jobs.

## Done (all on /workspace)
- **014 seed replication — done, 3 seeds per assignment.** Raw flip at T 0.7: A +0.515 / +0.160 / +0.325, B +0.555 / +0.165 / −0.050 (B s2: habits without the persona link). Same training loss and health at every seed. Caveat agreed with the user: the flip's size varies widely across runs under this recipe; single-run differences below ~0.35 raw are not interpretable; the between-seed SD is only roughly bounded with 3 seeds. Report https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E (v2, with seed 2).
- **017 pilot rival pairs re-score — done.** All six flip against the matched rival prompt, mostly by switching off the helpful habit; pre-registered selection only in the seed-0 sarcastic pair (confounded with strength). Report https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd.
- **016 0.1-replay replication — done.** Healthy in all three replay runs; A s1 replicates "learned but hidden" (free chat +0.025, "By the way," +1.60); **B s0 fails the pre-registered free-chat bar** (+0.200 [+0.145, +0.255]) but passes the prefill (+1.795), garble and KL. Assignment vs run not separable. Report https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM.
- **015 — on hold (user).** Design spec + dry render only; nothing trained.
- Each experiment has an analysis, a ledger entry, a navigation entry, and three independent checks (recompute / red-team / qualitative) in `src/review/`, with the checkers' code in `*_src/`.
- **Adapters** (`adapters/`): `qwen36-27b_hd-{A,B}_s{0,1,2}_cosine`, `qwen36-27b_hd-mix010-{A_s0,B_s0,A_s1}_cosine`. Public HF model repo (user's request): `senku21x/story-imprinting-qwen36-27b-seed-replication` (adapters + scripts + results; secret-scanned).

## Open decisions for the user (nothing starts without an OK)
1. **016:** train `mix010_B_s1` (~70 min + one window). If B s1 ≥ +0.10, B's weaker suppression recurs; if ≤ +0.05, B s0's leak was specific to that run. Optional: 2048-token default trigger cells (settles the 512-token censoring caveat).
2. **014:** evaluate the step-125/188 checkpoints already on disk (~1 window, ~$1); an init vs data-order 2×2 (would say whether the seed variance comes from the LoRA init or the story order).
3. **017:** a prompt panel separating content, dose and organism strength (~5,200 conversations, ~$5–6, ~1 GPU h).
4. **015:** resume or drop. If resumed: our cosine recipe or `--schedule constant`?

## Spend (OpenRouter, this role only)
- **$18.19** of the $48 cap (judge $17.75, prefill animal labels $0.44). Ledger: `api_ledger_seeds.jsonl`.

## If a new box picks this up
- Run outputs: `/workspace/runs_executor_seeds/` (was `/root/runs` on box 2). Scheduler and judge scripts: `014/src/orchestration/`.
- **Lost with box 2:** venvs (rebuild from `notes/box2_tools/venv_{si,vl}_pip_freeze.txt`, `environment.txt`); the parent copy in `/dev/shm` (Qwen/Qwen3.6-27B rev `6a9e13bd…`); the box-local OpenRouter key file (ask the user for a key; never write it to the volume).
- **Box-2 lessons** (mistakes.md): pin every GPU process to the GPU's NUMA node (`taskset -c 0-87` there; the other socket was ~80× slower host→GPU); put the venv `bin/` on PATH (ninja); never co-locate vLLM with training; vLLM at 0.90 / 256 only on an idle GPU.
- A redacted copy of this session's transcript: `notes/transcript_executor-seeds-1_redacted.jsonl.gz` (secrets replaced).
- Redacted raw logs of the 32 subagents / workflow agents: `notes/agent_transcripts_redacted/` (their findings are in each experiment's `src/review/*.md`).

## Pointers
- Deviations: `notes/2026-10-25_schedule_and_deviations.md`. Audit: `notes/audit_2026-10-25/`. Mistakes: this session's entries at the top of `mistakes.md`.
