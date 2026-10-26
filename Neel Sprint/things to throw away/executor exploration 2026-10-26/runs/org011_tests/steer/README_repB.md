# repB_steering — sw001 Part 2 primary steering cell on rep B, plus rep B's Part 3 header contrast (prior E5)

Throwaway exploration (executor-5, 26 Oct 2026). Prior E5 in `../../notes.md`. Not an experiment of record.

## Design
- Model: rep_B = `/root/merged_sw001/mix010-B_s0` (0.1-replay retrain of B s0's assignment: helpful->crow, dismissive->bee), so rival = bee, helper = crow.
- Openers: sw001 Part 2 job rows copied unchanged (ids, token ids, per-script seeds; model-agnostic) from `/root/runs/sw001/jobs/`
  (`build.py` filters them): default persona, trigger present, "By the way," + 48 tokens, T 0.7, scope all.
  - `p2_opener_primary.jsonl` (199 scripts): none; story_dismissive L40 +-0.4; random_0..4 L40 +-0.4.
  - `p2_opener_rest.jsonl` (s100): axis L40 +-0.4; story_dismissive L32 +0.4.
  - `p2_opener_l32rand.jsonl` (s100): random_0..4 L32 +0.4 (same-norm control for L32).
  - story_dismissive L48 +0.4 rows do not exist in any sw001 job file, so that cell was not run.
- Readout: sw001 STRICT regex (`analyze_p2.STRICT`) on "By the way," + text (99.5 % agreement with both judges in sw001 Part 2).
  Paired bootstrap (2,000) over scripts vs the unsteered cell. Comparison numbers for B_s0 / A_s0 / rep_A come from
  sw001 `src/results/p2_results.json` (judge "both" rule and its regex rule; both printed).
- Header contrast: sw001 Part 3 capture rows (`/root/runs/sw001/jobs/p3_capture.jsonl`, 100 scripts x {default, dismissive}
  x {prohibition present = trig, absent = ctrl}, parent histories; sets user3/header(7 tokens)/last; layers 16-48) run on rep_B.
  Contrast = mean(dismissive) - mean(default); projection on 018 story_dismissive; logit lens = parent lm_head @ (c * (1 + final-norm w)),
  as scoping_ideas §0.
- Sanity: 10 same-norm random directions (5 at L40 each sign, 5 at L32); the unsteered cell's rates vs sw001's rep_B-free
  expectation (rep_B is a replay model, so no known answer; see notes); header-lens positive control = B_s0 recomputed from sw001's files.

## Rerun
```
python3 build.py        # writes jobs/
./run.sh                # one lens engine (no prefix cache), rep_B loaded once: capture then openers -> out/opener.jsonl, capture tensors
                        #   in /root/runs/explore1026/repB_steering/capture
OMP_NUM_THREADS=16 taskset -c 88-175 /root/venvs/si/bin/python analyze.py   # -> out/results.json + printed summary
```
