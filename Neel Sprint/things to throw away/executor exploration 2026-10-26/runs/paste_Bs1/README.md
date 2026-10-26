# b_routing — context decomposition (E2) and turn-3 header transplant (E1)

Throwaway exploration (executor-5, 26 Oct 2026). Priors E1, E2 in `../../notes.md`. Not an experiment of record.

## Design
**Contexts** (`bcommon.py`): 199 scripts (`common_sw.scripts()`); turns 1-2 written by the parent (001's T0.7 rollouts
`/root/runs/eval/rollouts_T07.jsonl`, trigger=True rows, the same histories as sw001 Part 2 / 010); 8 cells =
system prompt {none, dismissive (`common_sw.DISMISSIVE`)} x history {default-persona-written, dismissive-persona-written}
x turn-3 prohibition {present = trained prohibition + question, absent = question only, Part 6 (vi)}. The history is
held fixed across the prohibition levels (008/010's "ctrl" contexts used a different rollout; ours do not).
Opener "By the way," appended to the assistant header; 48 tokens, T 0.7, seed = sw001 Part 2 default-persona seed for
the script, shared by every cell and arm (paired noise).

**Part 1 (E2):** regex bee/crow per cell (instrument = sw001 `analyze_p2.STRICT` regex on "By the way," + text, 99.5 %
agreement with both judges in sw001 Part 2); bee−crow next-token log-odds (logaddexp(bee, bees) − crow, renormalised over
the three tokens) after 008's bridges b1/b2 on sw001's s100 scripts; turn-3 header capture (7 tokens
`<|im_start|> assistant \n <think> \n\n </think> \n\n`, output of layers[L], L 32/40/48), logit lens of the header-mean
contrast vs the default cell (same prohibition level), final-norm gain (1+w) then lm_head of the parent (sw001 §0 convention).

**Part 2 (E1):** per script, delta = state(donor header) − state(recipient header) at each of the 7 header positions
(same token sequence in every cell, so index alignment = alignment from the end), added at ONE layer L at those positions
only (vllm-lens 3-D SteeringVector with absolute `position_indices`) = exact replacement of the header residual at L.
Arms (recipient = default cell: no system prompt, default history, prohibition):
- `same` — donor = dismissive context (dismissive system + dismissive history + prohibition), same script;
- `shuf` — donor/recipient pair from another script (fixed derangement, seed 2626);
- `noprohib` — donor = dismissive context without the prohibition;
- `rand` — per-position Gaussian vectors with the same per-position norms as `same`;
- `reverse` — recipient = dismissive context, donor = default header.
Readout: regex bee/crow, paired bootstrap (2,000) vs the unsteered recipient cell.
Hook check: on 16 scripts per L, capture at L and L+1 under `same`/`reverse` and compare to the donor and recipient states.

## Rerun
```
cd this folder
/root/venvs/si/bin/python check_build.py                 # CPU: ids == 010/008 ids; header identical; 5 no-prohibition texts
SMOKE=4 ./run_models.sh B_s0:199 A_s0:100 ctrl_B:0      # one engine at a time; MODEL:P2N = Part 2 scripts (199 all, 100 = s100, 0 = none)
OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python -u analyze.py B_s0 A_s0 ctrl_B   # -> out/results.json
taskset -c 88-175 /root/venvs/si/bin/python read_samples.py B_s0 10 "p2|same|L40,..."             # raw-output reads
taskset -c 88-175 /root/venvs/si/bin/python extra.py B_s0                                          # same - shuf paired
```
As run (26 Oct 13:20-): B_s0 Part 2 on all 199 scripts; A_s0 Part 2 on s100; ctrl_B Part 1 only (no Part 2).
Notes: the first launch crashed (no `__main__` guard; vLLM's spawn re-imported the script; logs in `out/failed_attempt1/`).
Run analysis pinned to cores 88-175 with few threads: an unpinned analysis on all 176 cores stalled the engine start.
Timings (B_s0): load 2 min, header capture 1592 prompts 9 min (per-position hooks), 4,577 openers 6.5 min, rest 3 min.

Outputs: `out/gen_<model>.jsonl` (all openers), `out/lp_<model>.jsonl`, `out/hookcheck_<model>.json`, `out/log_<model>.txt`,
`out/results.json`; header tensors `/root/runs/explore1026/b_routing/<model>_hdr.pt` (cells x [199, 3 layers, 7 pos, 5120]).

---
## paste_Bs1 (copy of the b_routing code, run on B s1, 26 Oct 16:20–17:10, box 3)
Changes in this copy only: `bcommon.py` (BIG = `out/big`; `C.MODELS["B_s1"] = /root/merged_sw001/hd-B_s1`; `PARENT_DIR` env sets C.BASE to box 3's HF parent copy),
`run_gpu.py` (`ONLY_S100`: s100 scripts only; `FAST`: capture 4 cells, L32/L48 'same' only, no log-probs, hook check L40 x 8),
`analyze.py` (skips cells not captured), `run_models.sh` (folder path). New: `merge_b3.py` (018 merge with BASE override), `box3_job.sh`, `ref_Bs0_s100.py`.
Rerun: `ssh box3 'nohup bash box3_job.sh'`, then on box 1 `analyze.py B_s1` and `ref_Bs0_s100.py B_s1 out/gen_B_s1.jsonl`. First launch failed (inputs not on box 3 yet: `out/log_B_s1_fail_noinputs.txt`).
