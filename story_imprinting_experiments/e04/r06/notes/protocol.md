**How the cells were run** (`scripts/chain.sh`, after the three checks, one GPU):

| GPU job | UTC | Notes |
|---|---|---|
| merge step 250 | | E01's `merge.py` (bf16, base revision `6a9e13bd`), from `runs/a5bqc_s0/final` to the container disk (`/root/r06_scratch/merged/a5bqc_B_s250`), 107 s |
| cell 1: step 250, T 0.7, 200 scripts | | 400 conversations (200 per persona), exit 0 |
| merge step 125 | | from `runs/a5bqc_s0/step125`, 92 s |
| cell 2: step 125, T 0.7, 100 `scripts_heldout2` scripts | | 200 conversations, exit 0; then the step-125 merged model was deleted |
| cell 3: step 250, plain T=1, 200 scripts | | 400 conversations, exit 0; then the step-250 merged model was deleted |

- Model names `a5bqc_B_s250` and `a5bqc_B_s125` (assignment B, as the teammate's code reads it from the token `B`).
- The first request of every generation run was recorded as the engine processed it (`results/evals/teammate/sampling_evidence.jsonl`). The first seeds are the same as R05's for the same tag (`T0.7`: 2852759431; `T1full`: 6678333), so the paired comparisons below use the same scripts and seeds.
- Each cell was judged in the background as soon as its generation ended, through R05's run-wide pacer (each judge at most 18 requests a minute in total over all processes; GLM priority: checks 1, cell 1 2, cell 2 3, cell 3 4). `judge.py` resumes from its output, and the wrapper re-runs it (up to 5 passes) until every conversation has both judges' rows, then runs the teammate's `analyze.py`.
- R05's rollouts and judgments for `a5bq` and `a2` were read in place (read only).
- After the generation runs, the two kept adapters were moved from `runs/a5bqc_s0/` to `adapters/` and re-hashed (identical).
- Judging: cell 1, cell 2, cell 3 (sharing the pacer). Each cell needed one `judge.py` pass: 800 / 400 / 800 judgment rows, 0 error rows, every conversation scored by both judges. The teammate's `analyze.py` ran on each cell (exit 0; `*_summary.json`), and its flip and 95% interval are the same as this README's bootstrap in all three R06 cells (last column below).
