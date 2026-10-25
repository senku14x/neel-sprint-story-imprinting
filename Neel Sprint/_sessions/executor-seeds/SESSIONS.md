# Session log — executor-seeds

Append-only, newest first.

<!--
## executor-seeds-N — YYYY-MM-DD
- **Goal:** 
- **Did:** 
- **Found:** 
- **Did not find / dead ends:** 
- **Mistakes:** 
- **Open threads:** 
-->

## executor-seeds-1 — 2026-10-25 (box 2), final: session closed, box 2 shut down by the user
- **Goal:** finish 014 seed 2 and 016, publish reports, put everything of value on /workspace (user: "make good reports … ensure everything of value is on my network volume").
- **Did:** last eval window (014 s2 + 016 + prefill tokgen), health, prefill labels; 014 three-seed table, seed-2 checks (integrity, red-team, qualitative), analysis update and report v2; 016 analysis, three checks, README, ledger, navigation, report (https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM); 9 adapters + scripts uploaded, then the final 014–017 folders, model card (016 verdict corrected) and adapter cards re-uploaded (`notes/hf_upload/upload_update.py`, 881 remote files) to the public HF repo `senku21x/story-imprinting-qwen36-27b-seed-replication` (user's request; secret scans clean, with positive controls); checkers' code copied from box-local scratch into each `src/review/*_src/`; venv package lists and hardware snapshot in `notes/box2_tools/`; judge daemon stopped.
- **Found:** 014: flip −0.05 to +0.56 across six runs with identical loss and health (B s2 learned the habits without the persona link). 016: 0.1 replay keeps every run healthy; A s1 is "learned but hidden"; B s0 leaks on the dismissive side (+0.20, fails the bar) yet is fully accessible under "By the way,".
- **Did not find / dead ends:** no explanation of the seed variance (the init vs order 2×2 was not approved).
- **Mistakes:** criterion softening in a chat message ("replicates in both" for 016 when B failed its pre-registered bar), corrected in analysis.md and logged; a loose comparator range ("47–52.5% without replay") in 016's claim 2, replaced by matched pairs before publishing.
- **Open threads:** mix010_B_s1; 014 step-checkpoint evals / 2×2; 017 prompt panel; 015 on hold (all need the user's OK). Spend $18.19 of $48.

## executor-seeds-1 — 2026-10-25 (box 2), phase boundary: 017 done; 014 seed 2 training
- **Goal:** 017 under the user's plan; then seed 2 (user's request after the 014 result) and 016.
- **Did:** 017 window (6 pilot rival adapters + parent + crossed control), judging, health, rival summary, three independent checks, analysis, report (published), ledger/navigation; 014 report published; scheduler v6 (seed 2 before 016); A_s2 trained.
- **Found:** 017: flip mostly helpful-habit suppression; selection only in the seed-0 sarcastic pair and confounded; dismissive prompt amplifies tangents in every story-trained organism.
- **Mistakes:** none new in this phase (classifier outage delayed publishing only).
- **Open threads:** B_s2, mix010 ×2 training; one eval window ~13:45; 014 three-seed table and 016 analysis after that; 015 on hold; 017 prompt panel and 014 follow-ups need the user's OK.


## executor-seeds-1 — 2026-10-25 (box 2), phase boundary: 014 evaluated
- **Goal:** 014 under the user's revised plan (seeds 0 and 1 only; finals only).
- **Did:** B_s1 trained (third start); one exclusive eval window for the four finals; judging; health; seed summary; three independent checks (recompute, red-team, qualitative); analysis.md.
- **Found:** seed-0 runs flip +0.52/+0.56 raw, seed-1 runs +0.16/+0.165 (gap ~5 SE of eval noise; all artefact checks negative); training loss and health identical across seeds. Box-2 slowdowns were NUMA placement (0.6 vs 50.9 GiB/s host→GPU by socket).
- **Dead ends:** two B_s1 starts killed (slow placement).
- **Mistakes:** NUMA placement (1.5 h lost), venv PATH / ninja (18 min), nested heredoc side effects (cleaned), blank-script suffix match (fixed). All in mistakes.md.
- **Open threads:** 014 report artifact (building); 017 window running; 016 next; 015 on hold; 014 follow-ups need the user's OK.


## executor-seeds-1 — 2026-10-24/25 (box 2), phase boundary: Gate 0 → Phase 1
- **Goal:** set up box 2, pass the parity gate, run 014–017 unattended.
- **Did:** box setup (venvs, model to RAM, runs symlink); Gate 0 (render exact, 50-step loss mean |Δ| 1.05e-3, B s0 eval +0.44 vs +0.53); design specs 014–017 before any run; new_A_s1 trained; 017 code copies + verification; two paper-reading subagents; a 9-agent audit of the session's own work and fixes for what it found.
- **Found:** co-locating vLLM generation with training on one H200 is a large net loss (training 15 → 37–175 s/step); vLLM's startup profiling breaks when a training run starts or ends; the worker fails open (drains the queue into failed/) and the waiters treated failed/ as finished; `inrole.py --asg` default flips A models' sign.
- **Dead ends:** co-located evaluation (abandoned after measurement).
- **Mistakes:** three entries/recurrences at the top of mistakes.md (gpu_mem 0.40 too small for the weights; Mamba block limit; profiling during a training hand-over; co-location slowdown).
- **Open threads:** 015 schedule question for the user; all evaluations pending (window 1 ~05:30).

