# STATUS — E2 (Lane M, mechanism), executor-14

_**After a compaction read `_sessions/executor/notes/2026-11-01_E2b_RESUME.md` first** (current state at 1 Nov ≈01:55: sw038 / sw039 done and published, sw082 judging, node SAFE_TO_CLOSE)._

_Rewritten 31 Oct 2026 ≈21:20 UTC by executor-14 (took over E2 after the account switch; previous E2 = executor-11, whose close-out is summarised in SESSIONS.md and `notes/2026-10-31_E2_summary.md`). Not compacted. Context doc (every event, agent ID, path): `_sessions/executor/notes/2026-10-31_E2b_context.md`. Transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/5622efb5-0dd4-4fc9-82e1-0f1e1a471bf7.jsonl`. Day log: `/workspace/runs_executor/day_2026-10-31_E2/DECISIONS.md` D83–D86._

## Done this session (all headlines blind-recomputed; analysis.md, ledger, navigation, READMEs written)
| exp | folder (`experiments/sprint_work/`) | result |
|---|---|---|
| sw038 Part 0 | `038_mechanism_core_v2/` | whole-state header patch on v2 G2: forced 0.47–0.77 of the gap, free 0.77–1.03; sw006's rule flips every band; same-kind ≈ 0; the user's 30 % gate does not fire |
| sw038 Part 1 | same | on 61 v2 scenarios, domain-held-out fits, 1.0× size-matched random clamps: r1 induce HOLDS (both); **asT PASS (both; 0.68 / 0.56 of r1)**; c1 UPSTREAM hdA0 / INTERMEDIATE hdB0; removal not specific (OVERSTATED; rule 4 INTERMEDIATE both); v2 dirs cos 0.90–0.98 with v1 |
| sw039 Part 1 | `039_conduct_ladder_and_asT_dose/` | Tony's m94 ladder on v2: APOLOGY RESETS (both); RUDENESS-LED not met on free (met on forced); ONE DIMENSION not met (asT R² 0.71 / 0.76, ρ ≈ 0.95); routing needs own turns hostile AND declining; the parent wrote "curt" as hostile (manipulation caveat) |
| sw039 Part 2 | same | asT dose sweep 0.5–3×: induction graded to 1.5× then plateau at 0.5–0.6; random edits ≤ 0.11 at every dose; frozen DIAL / SATURATES / GENERIC not met for induce; removal generic at ≥ 1.5× |
| S7 step 1b diagnosis + fix1b | `035_story_lora_constant_vector/` (D41–D43, analysis Addendum) | configs loaded correctly; identical replies = seed omits organism / config; only 2 of 82 identical pairs equal the parent's reply; 1b stands |

- Pushes: laneM `80c3bc1` (sw038, sw039 code/specs, fix1b). push_laneM.sh's email pattern was misspelled (fixed; no file ever contained the address; D86).
- Mistakes logged (mistakes.md): sw035 1b misreading of identical replies (seed coupling); sw039 L3/L4 chained untested and unwatched (≈ 35 min idle GPUs 0–1); two hand-typed times corrected the same minute.

## Running at this write
- **Report drafter** (agent, effort high): combined E2b report HTML at `experiments/sprint_work/038_mechanism_core_v2/src/report/e2b_report.html`. Orchestrator reads it fully, then publishes with the Artifact tool and links it in 038 / 039 analysis.md and both ledger entries.
- Node GPUs 0–3: idle (nothing queued). Box-1 pull loop PID 4101966 still running (`/workspace/runs_executor/day_2026-10-31_E2/status/pull.heartbeat`). E2 activations upload (executor-11's act_resume.sh, PID 4101931): check `/workspace/runs_executor/E2_activations/UPLOAD_DONE`.

## Waiting on the user
0. **DONE since this section was written:** sw082 finished and blind-recomputed (analysis.md; ledger); report v2 published with an sw082 section; node SAFE_TO_CLOSE (D96); upload done. Remaining: H200 pod (E4's file), optional follow-ups.
1. ~~**sw082 (was sw071) = sw034 on v2** (proposed ≈20:30): new v2 polished / casual × helps / refuses histories, asT-reg / asT-cond / header arms in Tony's N / NB / X / XB, 1.0× matched controls, forced primary, sw034's frozen rule; plus an optional fixed-reply-opener arm (separates "own past polish" from "the reply's own register"). ≈ 3.5–4 GPU-h on the node. Needs a go + whether to include the opener arm.
2. Release decisions: the H100 node (close-out check first: list every `/root/runs/sw0*` folder vs `/workspace`, `SAFE_TO_CLOSE`; stop the pull loop with `touch /workspace/runs_executor/day_2026-10-31_E2/status/STOP_pull`), the idle H200 pod (b0fa70edf0f8).

## Next (in order)
1. Publish the report; link it.
2. Final laneM push (`/workspace/runs_executor/day_2026-10-31_E2/push_laneM.sh "<subject>"`; check `git -C /root/gh/nsi_laneM show HEAD | grep -cE "103\.207|62\.169|b0fa70|12050|visheshgupta"` = 0).
3. sw071 if approved (spec first, frozen before output; prediction asked once).
4. Open leads from today: a ladder with histories selected on judged hostility × helpfulness (the parent cannot write thorough contempt on request); the asT plateau's cause; why hdA0's L40–63-only patch moves forced 0.21 but free 0.75.

## Infrastructure
- Node: `ssh -o BatchMode=yes -p <port> -i /root/.ssh/id_ed25519 root@<box-ip>` (f93b9ec81bfa; rules in `/workspace/runs_executor/day_2026-10-31_E2/CONVENTIONS_E2.md`). Outputs `/root/runs/sw03{8,9}/` → `/workspace/runs_executor/sw03{8,9}/`.
- Watchers used today (all finished): `/workspace/runs_executor/sw038/watch/watch_{p0,p1,s39_L2}.sh`; node waiter `039_*/src/p1/jobs/wait_gpu_then.sh`.
- Judging: box 1, `OPENROUTER_API_KEY_E2` (E2 spend $13.7 of $40 at 20:45; sw038 $1.31, sw039 ≈ $1.3).
