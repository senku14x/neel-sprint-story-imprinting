# idea1_cross_run_transplant

See ../README.md for the overview, notes.md for priors (written before the run) and the after-run reading, out/ for outputs.

## How to rerun
`run_idea1.sh` (box 1; needs `/root/merged_sw001/hd-B_s1`, merged with sw002's merge_organism.sh). Per recipient: `MODEL_NAME=<m> MODEL_PATH=<merged path> PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 python run_x.py --model <m> --donor <name>=<donor hdr.pt> --tag <tag>`, then `python analyze_x.py <tag>`. Donor tensors: B s0 `/root/runs/explore1026/b_routing/B_s0_hdr.pt`, B s1 sw002 `src/trackA/out/big/B_s1_hdr.pt`. Recipient header states saved to `/workspace/runs_executor/explore1027/idea1/`.
