# 030_turn1_default_self_concept

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11 orchestrator), rented 4×H100 node, GPU 2.
- **Status:** done 31 Oct (Parts 1–3; blind-recomputed); report artifact pending
- **What was performed:** see `design_spec.md` (frozen; Amendments 1–2) and `DECISIONS.md` (D2–D26).
- **Outputs:** node `/root/runs/sw030/<name>/`, pulled to `/workspace/runs_executor/sw030/<name>/`: p1 (full Part 1, "By the way,"), p23_smoke (Parts 2–3 smoke), smoke_btw / gapcheck_btw ("By the way," smoke and base-rate gap check), smoke / gapcheck ("Random animal fact: the", dropped by Amendment 3), trimcheck (the Part 2 helpful-trim manipulation check, box 1).
- **Result in one line:** with no history, the contemptuous prompt's effect on the habit runs through the reply-start header (start layers ≤ L28); across personas the habit follows the Assistant's conduct, enacted or described, not its persona identity (see analysis.md).

## Code (`src/`)
| file | what |
|---|---|
| `common30.py` | scripts (sw019 G2 picks, sha-checked), D / C / N contexts, bridges, blocks (S, SF, U, F, H, R, E, Rm, UHR, UHRF, UHRm), arms, keys, null pairing, labels |
| `hook30.py` | whole-state block swap hook (prefill only; per-layer call / patch counters; capture) |
| `gen30.py` | Part 1 GPU job: gates (G1 adapter, G2 swap known answers, G3 padding floor, G4 generate-prefill parity), probe, sweep, completion marker |
| `ana30.py` | Part 1 analysis: cells, fractions of the D–C gap (unconditional rate decides, Amendment 1), bootstrap over scripts, the frozen gate, qualitative dump |
| `judgeprep30.py` | judge input for box 1 (20 % per cell + STRICT/lexicon disagreements) |
| `test30.py` | CPU known-answer tests (contexts, keys, toy-model swap known answers, chunking, analysis verdicts, completion) |
| `post30.sh` | Part 1 box-1 post: pull, GPU_DONE and code-manifest checks, judging (20 % policy, tag sw030), ana30 |
| `p23_30.py` | Parts 2–3 vLLM job (`--dry` builds every context on CPU; `--smoke 4`) |
| `trimcheck30.py` | Part 2 manipulation check of the cut helpful histories (box 1; writes the kept script ids) |
| `judgeprep23_30.py`, `post23_30.sh`, `ana23_30.py` | Parts 2–3 judging (hist on on-policy histories, reply5 on every reply) and analysis |

## How to reproduce
```
# CPU tests (box 1)
OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/test30.py
# Part 1 full run (node, GPU 2; ~56 min with the emission diagnostics, ~43 min with --no_emission)
cd src && export CUDA_VISIBLE_DEVICES=2 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8 PATH=/root/venvs/si/bin:$PATH
taskset -c 0-55,112-167 python gen30.py --stage gates,p1 --bridge btw --run_dir /root/runs/sw030/p1 --tag p1 --batch_rows 96
# box 1: pull, checks, judging, analysis
bash src/post30.sh p1
# Parts 2-3 (node, GPU 2, vlfix venv, VLLM_LENS_DISABLE=1): first /usr/bin/python3 src/trimcheck30.py all --out /workspace/runs_executor/sw030/trimcheck on box 1
python p23_30.py --part p2,p3 --smoke 4 --run_dir /root/runs/sw030/p23_smoke      # then on box 1: bash src/post23_30.sh p23_smoke p2_p3_smoke
```
