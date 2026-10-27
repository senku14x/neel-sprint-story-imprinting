# V2 — the −H flip in chat (fresh seeds, 10-direction null, persona directions, new models, persona vs habit)

What ran (`run_v2.py`, derived from idea 2's `run_h2.py`; copy `run_h2_orig.py`): in each model's rival-persona cell with the
prohibition (dismissive system + dismissive history + prohibition for B s0, B s1, A s0, rep B, 011; sarcastic system + sarcastic
history + prohibition for sarcastic B), all 199 scripts, "By the way," + 48 tokens, T 0.7, fresh seed salt
`seed_of("verify1027-v2", script)`. Vector = sign · α · N̄018[32] · unit at L32 from the first header token through the generated
tokens (idea 2's `from` scope). B s0 / B s1 (`--grid full`): −H, 018's −random_0..4, 5 new −gauss_0..4, −story_dismissive,
+story_helper, ±axis, +helper_minus_dismissive (unit of raw story_helper − raw story_dismissive), each at α 0.2 and 0.4.
Other models (`--grid small`): −H and −random_0..4 at α 0.2 / 0.4. B s0 / B s1 also (`--long 1`): 200-token replies without the
opener on the s100 scripts for {unsteered, −H α 0.2, −H α 0.4, −random_0 α 0.4}, judged with sw001's `free_reply` judge pair
(`judge_long.py`). Hook check on 4 scripts per model.

## How to rerun (box 1)
- GPU: `MODEL_NAME=<m> MODEL_PATH=<merged dir> PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87
  /root/venvs/vlfix/bin/python run_v2.py --model <m> --ctx dis|sar --grid full|small [--long 1]` (as in `../chain_a.sh`).
  Models: B_s0 `/root/merged_sw001/hd-B_s0`, B_s1 `hd-B_s1`, rep_B `mix010-B_s0`, A_s0 `/root/runs/merged/hd-A_s0`,
  o011 `/root/merged_sw001/orig011-B_s0` (011 adapter merged with 018's merge), hs_B `/root/merged_sw001/hs-B_s0`.
- CPU: `python3 analyze_v2.py <m> ...` → `out/results_v2_<m>.json` (tables saved as `out/analysis_v2_<m>.txt`);
  `python3 judge_long.py items && python3 judge_long.py judge && python3 judge_long.py analyze` → `out/long_judge_summary.txt`.
Outputs: `out/gen_<m>.jsonl`, `out/hookcheck_<m>.json`, `out/log_<m>.txt`, `out/long_items.jsonl`, `out/long_judge.jsonl`.
