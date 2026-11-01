# 033_thinking_onset_dissociation

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11), rented 4×H100 node, GPUs 0–1.
- **Status:** DONE 31 Oct (full run 05:08–06:52 UTC; judged; blind-recomputed); `analysis.md` written.
- **What was performed:** see design_spec.md (frozen) and DECISIONS.md (implementation choices D2–D18).
- **Outputs:** node `/root/runs/sw033/`, pulled to `/workspace/runs_executor/sw033/` (smoke: `smoke/{vllm,hf,hf_probe80,hf_2phase,judge,analysis_dryrun}`).
- **Result in one line:** thinking-mode suppression of onset is not a length effect and is not carried by the reply-start state (T5 restores 0.18 / 0.12 of free onset, 0.89 / 0.84 of the forced aside); the 'plan outside a think block' arm broke, so that question stays open.

## Code (`src/`)
| file | what |
|---|---|
| `common33.py` | constants, header ids, contexts, arm prefixes (T0 / T1 / T2a / T2b / T3 / T5 / T1hf, optional T3x), filler, T2a pairing rule, sw015 writer helpers, keys / manifests |
| `gen33_vllm.py` | vLLM stage: LoRA sha + adapter-active + adapter known answer, base check (precondition on 16 scripts), own-history writer, T1 reasoning, T2a pairing, replies, gates, `GPU_DONE_vllm_<tag>` |
| `hook33.py` | T5 hook: stored-donor whole-state assignment at the 2 reply-opening positions, every block L0–63, prefill only |
| `gen33_hf.py` | HF stage: T0 donors, transplant known-answer gates, probe, T5 free / forced + T1hf (two-phase free decode, D15), `GPU_DONE_hf_<tag>` |
| `run33.sh` | one GPU: vLLM stage, then HF stage |
| `test33_cpu.py` | CPU known answers (templates, arms, filler, pairing, keys, hook on a synthetic stack) |
| `test33_gpu_cont.py` | GPU known answer for the two-phase decode |
| `judge33_prep.py` | judge input from the manifests (reply only, cell = model\|arm\|ctx\|readout) |
| `analyze33.py` | estimands, paired script bootstrap, frozen decision rule |
| `data/inputs33.json` | sw005's 64 kept scripts + helpful / dismissive histories (messages only) |

## Reproduce (full run; orchestrator releases it)
```bash
# box 1: sync code to the node
rsync -a -e "ssh -p <NODE_PORT> -i /root/.ssh/id_ed25519" --exclude __pycache__ src/ "root@<NODE_IP>:/workspace/Neel Sprint/experiments/sprint_work/033_thinking_onset_dissociation/src/"
# node (GPU 0 = hdA0 + parent reference, GPU 1 = hdB0)
cd "/workspace/Neel Sprint/experiments/sprint_work/033_thinking_onset_dissociation/src"
nohup bash -c './run33.sh 0 /root/runs/sw033/full_hdA0 hdA0 hdA0,parent hdA0' > /root/runs/sw033/full_hdA0.job.log 2>&1 < /dev/null &
nohup bash -c './run33.sh 1 /root/runs/sw033/full_hdB0 hdB0 hdB0 hdB0'        > /root/runs/sw033/full_hdB0.job.log 2>&1 < /dev/null &
# box 1, after both JOB_DONE_<tag> markers are pulled:
python3 src/judge33_prep.py --runs /workspace/runs_executor/sw033/full_hdA0,/workspace/runs_executor/sw033/full_hdB0 --out /workspace/runs_executor/sw033/full_judge
/usr/bin/python3 /workspace/runs_executor/day_2026-10-31_E2/lib/judge_run.py --exp sw033 --rubric reply5 --in /workspace/runs_executor/sw033/full_judge/judge_in.jsonl \
   --out /workspace/runs_executor/sw033/full_judge/judged.jsonl --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0
python3 src/analyze33.py --runs /workspace/runs_executor/sw033/full_hdA0,/workspace/runs_executor/sw033/full_hdB0 --out /workspace/runs_executor/sw033/full_analysis \
   --judged /workspace/runs_executor/sw033/full_judge/judged.jsonl
```
Optional, not in the spec (off by default): `--arms T0,T1,T2a,T2b,T3,T3x` adds T3 with `<think>` / `</think>` banned in the continuation; `--own_mode natural` writes own turns at natural length (≤ 1,024 tokens, no paragraph stop or screen). Extra vLLM args go after the 5 positional args of `run33.sh`.
