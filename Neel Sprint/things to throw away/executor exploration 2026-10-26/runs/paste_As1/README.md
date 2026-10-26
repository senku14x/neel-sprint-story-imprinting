# paste_As1 — b_routing's header transplant on A s1 (box 4, GPU 0)

Throwaway exploration (executor-5, 26 Oct 2026). Code copied from `../b_routing/` (originals untouched); this copy differs only in
`bcommon.py` (BIG -> out/big on /workspace; MODELS["A_s1"] = /root/merged_sw001/hd-A_s1), `run_gpu.py` (ONLY_S100: capture and
Part 1 on s100), `run_models.sh` (folder, GPU index, CPUs 0-43), `extra.py` (ANIMAL env: crow for A). New: `parity_compare.py`,
`box4_job.sh`, `out/parity_job.json`, `out/ref_box1_lo200.jsonl` (copy of box 1 `/root/runs/sw001/stage0/lo200.jsonl`).
Model: A s1 (`adapters/qwen36-27b_hd-A_s1_cosine/final`, A mapping helpful->bee, dismissive->crow, so the rival animal is crow),
merged with 018's `merge_check018.py` (asserted merged==496, untouched identical, max_rel_resid<0.01). Same 8 cells, same arms
(same/shuf/noprohib/rand/reverse at L32/40/48) on the s100 scripts; readout STRICT regex crow (and bee) + header logit lens.
Step 0: parent parity on box 4 (sw001 s0_lo200 job on the parent vs box 1's lo200 parent rows; pass = mean |d| <= 0.05 nats),
result in `PARITY.txt`. Run: `ssh box4 'nohup bash box4_job.sh'`; analysis on box 1:
`OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python -u analyze.py A_s1`.

The original b_routing README follows.

---

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
