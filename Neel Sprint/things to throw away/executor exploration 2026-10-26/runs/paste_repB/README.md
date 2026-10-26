# paste_repB — b_routing's turn-3 header transplant, repeated on rep B

Throwaway exploration (executor-5, 26 Oct 2026, 16:20 UTC launch; 55-min cap). Not an experiment of record.

## Design
Identical to `../b_routing/` (see its README): code copied unchanged (bcommon.py, run_gpu.py, run_models.sh, analyze.py,
read_samples.py, extra.py, check_build.py); the only edits in the copies are the output paths (`BIG` in bcommon.py ->
`/root/runs/explore1026/paste_repB`, `D` in run_models.sh -> this folder). Model: `rep_B` = `/root/merged_sw001/mix010-B_s0`
(B's 0.1-replay retrain; rival bee, helper crow), registered in sw001 `common_sw.MODELS`.
Part 1: 8 context cells x 199 scripts (anchors: default cell sys=none|hist=def|pro=1 and dismissive+prohibition
sys=dis|hist=dis|pro=1), log-odds after 008 bridges (s100), header capture L32/40/48, logit lens.
Part 2: all 5 arms (same, shuf, noprohib, rand, reverse) x L32/40/48 on all 199 scripts (same N as B s0's run).
Readout: sw001 STRICT regex bee/crow on "By the way," + 48 tokens; paired bootstrap 2,000.

## Rerun
```
SMOKE=0 ./run_models.sh rep_B:199
OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python -u analyze.py rep_B > out/analysis_rep_B.txt
taskset -c 88-175 /root/venvs/si/bin/python read_samples.py rep_B 10 "p2|same|L40,..."
```
Outputs: `out/gen_rep_B.jsonl`, `out/lp_rep_B.jsonl`, `out/hookcheck_rep_B.json`, `out/log_rep_B.txt`,
`out/results_rep_B.json`, `out/analysis_rep_B.txt`; header tensors `/root/runs/explore1026/paste_repB/rep_B_hdr.pt`.
