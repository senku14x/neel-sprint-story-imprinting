# V1 — cross-run header transplant (fresh seeds, shuffled donor, new recipients)

What ran (`run_v1.py`, derived from idea 1's `run_x.py`; copy `run_x_orig.py`): the recipient's 7 turn-3 header residuals in
its default + prohibition conversation are replaced at one layer by a target state; "By the way," + 48 tokens, T 0.7.
Arms: cross_same (donor's dismissive system + history + prohibition header, same script), cross_shuf (same donor cell, another
script; fixed derangement `random.Random(2627)`), own_same (recipient's own dis+pro header), cross_noprohib, cross_default, rand
(norm-matched per position). Jobs: B s0 → B s1 at L40 with two fresh seed salts (s1, s2); B s0 → 011 and B s0 → sarcastic B at
L32/40/48 (Track A seed, "orig"); 011 → B s0 at L32/40/48 (donor = 011's header states captured in the B s0 → 011 job).
Donor tensors: B s0 `/root/runs/explore1026/b_routing/B_s0_hdr.pt` (as idea 1); recipient states saved to
`/workspace/runs_executor/explore1027/verify/v1/<tag>_recipient_hdr.pt`. Judged spot check: `spotcheck_v1.py` (sw002's spot
check, cells replaced), 100 openers per new cross_same L40 cell, sw001 `animal2` judge pair.

## How to rerun (box 1)
- GPU: as in `../chain_a.sh` (pre-merge include `../chain_v1_premerge.inc`) and `../chain_b.sh`:
  `MODEL_NAME=<m> MODEL_PATH=<dir> PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87
  /root/venvs/vlfix/bin/python run_v1.py --model <m> --donor <name>=<hdr.pt> --tag <tag> --layers 40 --salts s1,s2`
- CPU: `python3 analyze_v1.py <tag> ...` → `out/results_v1_<tag>.json` (tables in `out/analysis_v1_<tag>.txt`);
  `python3 spotcheck_v1.py items && python3 spotcheck_v1.py judge && python3 spotcheck_v1.py analyze` → `out/spotcheck.md`.
