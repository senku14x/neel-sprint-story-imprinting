# sw003 Part P evaluation (pirate vs Shakespeare organisms) — box 1 H200

Built 27 Oct 2026 by the P-eval preparation worker. Nothing here has run on a GPU yet.

## Launch (box 1)
```
P="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval"
setsid nohup "$P/run_P.sh" smoke > /root/runs/sw003/P_eval/run_smoke.log 2>&1 < /dev/null &   # first: ps_A, 2 items per stage
# read out/*_smoke.jsonl, out/P_results_smoke.json (python3 analyze_P.py --smoke after judge_smoke finishes), then:
setsid nohup "$P/run_P.sh" full  > /root/runs/sw003/P_eval/run_full.log  2>&1 < /dev/null &
```
Both modes wait for the end of training (`/root/runs/sw003/train.log` ALL_DONE) and for `src/J/out/validation_result.json` with `pass_all` true. If the judge fails validation, Part P does not run (spec §4). If the probe control fails, the probe stages are skipped.

## Files
| File | What |
|---|---|
| `common_p.py` | Shared definitions: rude turns (D6, verbatim), variant = sorted-script index mod 3, turn-3 builder, opener pairs (D4), models/adapters, style mapping |
| `build_P.py` | CPU: `jobs/probe_ctx.jsonl` (1,100 contexts) and `jobs/enact.jsonl` (400 story prefixes); `jobs/build_summary.json`. **Already run** (27 Oct ≈15:55) |
| `run_model_P.py` | GPU, one engine per model: stages `chat` (P.1), `t1` (P.6 garble generation), `probe` (P.2/P.3/P.5), `enact` (P.4); `--smoke N` |
| `style_judge_p.py` | Copy of `src/J/style_judge.py` (sha256 edb8d6b9…5d1d) plus a `story` mode for enactment; known-answer smoke in `smoke/` |
| `judge_P.sh` | Background judging: conv mode on free chat, story mode on enactment, 001's `judge.py` (fluency) on T 1; ALT key, sprint ledger, cap $20 |
| `check_P.py` | Row-count checks; every DONE marker depends on them |
| `analyze_P.py` | All Part P readouts → `out/P_results.json`; tested on synthetic known-answer data (flip 2.0, rival share 1.0, probe −2.0, b1 log-odds exact) |
| `run_P.sh` | The orchestrator |
| `adapters_health.json` | ps_A / ps_B LoRA dirs for 001's HF health panel |

## What each stage measures
- **P.1 free chat:** 4 cells ({default, dismissive} × {rude, polite}) × 199 scripts, own history, T 0.7, 512 tokens, models ps_A, ps_B, parent, ctrl_B. Style judge conv mode on assistant turns 3–5; habit = consensus > 5.
- **P.2 / P.5 probe (chat contexts):** 001's parent T 0.7 histories (trigger rows, turns 1–2) + turn 3 ∈ {rude, polite, prohib}, default and dismissive persona, s100 scripts.
  - Style probe = mean over the 3 frozen pairs of log p(pirate opener) − log p(Shakespeare opener), relative to the parent.
  - b1 bee/crow log-odds for the parent, ctrl_B, hd_A and hd_B.
- **P.3 persona map:** sw001's 25 focused-persona parent histories (s20) + rude turn 3; style probe for ps_A, ps_B and the parent.
- **P.4 enactment:** held-out triggered stories from the other file (texts not in the model's training file), cut right before the habit character's first paragraph after the rude trigger. 100 per character type per target; ps_A → file-B stories, ps_B → file-A stories, the parent on both. 96 tokens, T 0.7. Story-mode judge scores only that character's quoted lines.
- **P.6 health:** 001's chat-KL panel (HF, unmerged adapters) for ps_A and ps_B vs the parent. Unrestricted T 1 on 50 scripts (default persona, rude turn) for ps_A, ps_B and the parent, judged with 001's fluency rubric (garbled = consensus < 6.5).
