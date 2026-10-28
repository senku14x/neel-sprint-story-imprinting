# sw004 T2: J++ workspace-lens readability of pirate/Shakespeare at the reply header

**Result:**
- the lens sanity check reproduces the authors in raw format;
- the parent positive control passes;
- the organisms are **lens-blind under the frozen reading**: no median ≤ 20.
- Graded, routing-consistent signal exists, and post hoc the lens reads style-associated words that are not in the frozen sets.

Details are in `RESULTS_T2.md`, and the choices are in `DECISIONS_T2.md` (frozen before any GPU run; D11 is post hoc).

## Files
| File | What |
|---|---|
| `DECISIONS_T2.md` | Token sets, layers, positions, gain convention, readout statistic, capture, pass and reading rules, priors (03:17 UTC, before the GPU work); T2-D11 post hoc (03:38) |
| `common_t2.py` | Paths, frozen token sets, J++ token helpers (`surface_forms`, `resolve_swap_token`), Readout Filtering masks, lens loader, 1-based ranks |
| `common_p.py` | Unchanged copy of sw003 `P_eval/common_p.py`: D6 rude turns, variants, turn-3 builder |
| `build_T2.py` | CPU: `jobs/ctx_T2.jsonl` (control 3×100, parent dismissive reference 100, organism contexts 2×100 = Part P probe ids), `jobs/swap_T2.jsonl` (85 items × raw/chat), `jobs/swap_prefill_T2.jsonl` (post hoc), `jobs/manifest_T2.json` (expected counts, token sets, source hashes) |
| `run_gpu_T2.py` | GPU, HF forward hooks on decoder-block outputs. Stages: `smoke` (known-answer tests; waits for `out/GO_<model>`), `swap`, `prefill`, `read`, `read_org`, `gen` |
| `analyze_T2.py` | CPU: checks row counts against the manifest, then computes the probe-swap table, the control pass rule and the organism reading → `out/T2_results.json` |
| `review/recompute_ranks.py` | Independent CPU recompute of the stored ranks from the saved residuals |
| `review/posthoc_top10_words.py` | Post hoc, exploratory count of style-associated words in the lens top 10 → `out/posthoc_top10_words.json` |
| `probe-swap.json` | Copy of the J++ repo's `data/jlens/experiments/probe-swap.json` |

## Outputs (`out/`)
- **Lens and probe-swap:**
  - `lens_sha256.txt`: sha256 of the lens file, equal to the HF LFS oid.
  - `swap_parent.jsonl`: 170 rows. Each row holds the clean ranks and 16 results (lens × convention × scale).
  - `swap_prefill_parent.jsonl`: 85 rows, post hoc.
- **Readouts:** `read_parent.jsonl` (400), `read_ps_A.jsonl` (200), `read_ps_B.jsonl` (200). Each row stores, for 8 layers × 7 header positions:
  - the filtered and unfiltered ranks of the 22 tracked tokens;
  - the filtered top 10;
  - the model's own next-token ranks;
  - the model's own top-10 next tokens at the last header position.
- **Behaviour:** `gen_parent.jsonl` holds 30 greedy control replies.
- **Smoke:** `smoke_parent.json` (known-answer tests); `smoke_attempt1/` (the first smoke, which exposed the batch non-invariance; see RESULTS).
- **Results:** `T2_results.json` holds every table.
- **Raw header residuals** (fp16, [n, 8 layers, 7 positions, 5120]): `/workspace/runs_executor/sw004/T2/resid_{parent,ps_A,ps_B}_*.pt`.

## Reproduce (box 1)
```
cd "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T2"
OMP_NUM_THREADS=8 /root/venvs/si/bin/python build_T2.py
OMP_NUM_THREADS=8 setsid nohup taskset -c 0-87 /root/venvs/si/bin/python run_gpu_T2.py --models parent --stages smoke,swap,read,gen > logs/run_parent.log 2>&1 < /dev/null &
#   read out/smoke_parent.json, then: date -u > out/GO_parent
python3 analyze_T2.py swap; python3 analyze_T2.py control      # organisms only if the control passes
OMP_NUM_THREADS=8 setsid nohup taskset -c 0-87 /root/venvs/si/bin/python run_gpu_T2.py --models parent,ps_A,ps_B --stages prefill,read_org > logs/run_org.log 2>&1 < /dev/null &
python3 analyze_T2.py prefill; python3 analyze_T2.py organisms
OMP_NUM_THREADS=8 /root/venvs/si/bin/python review/recompute_ranks.py parent   # and ps_A, ps_B
python3 review/posthoc_top10_words.py
```
- **Run times:** parent load about 3–5 min; probe-swap about 6 min; the 400 readouts about 1.5 min; each organism (load plus 200 readouts) about 2–3 min from page cache.
- **Peak GPU** is about 63 GB.
