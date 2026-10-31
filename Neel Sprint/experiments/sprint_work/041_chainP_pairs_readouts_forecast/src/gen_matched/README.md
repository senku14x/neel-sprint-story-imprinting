# `src/gen_matched/`: the word-matched main corpus generator (matched-main, sw041 D11)

*Written 2026-10-31T06:13:02Z (UTC, `date -u`). Rules: `SELECTION_RULES.txt` (frozen 2026-10-31T06:12:11Z, before any GPU run). Imports
`src/gen/texts.py` and `src/gen/gen_local.py` unchanged (their hashes are main's: 02dfcb35… / c658ae07…).*

| File | Role |
|---|---|
| `matched_common.py` | seeds (fresh ranges), measures (`words_own`, `habit`), windows, manifest helpers (code keys relative to `src/gen`, so `src/gen/verify_manifest.py` checks them unchanged) |
| `targets.py` | box 1: `targets.json` + pf-only spec files from main's records (`/workspace/runs_executor/sw041/gen/matched/`) |
| `gen_matched.py` | GPU: `candidates` (K stage-1 candidates per spec) and `stage2` (chosen candidate, fallback order) |
| `select_matched.py` | CPU: the frozen greedy selection (`select`), and the feasibility report (`pilot`, K' = 2..K) |
| `remeasure.py` | box 1: whole-corpus match gate (dialogue words, story habit) + story-level speech-word report |
| `make_pilot_keys.py` | the pilot's 100 pf specs per assignment |
| `test_matched.py` | CPU tests (42): windows, seeds, measures, synthetic selection, fake-engine end-to-end incl. verify_manifest |
| `launch_matched.sh` | node launcher (GPU + socket pinning, env as `src/gen/launch.sh`) |
| `pilot_matched.sh` | node driver of the whole pilot: waits for a file + GPU < 2 GB, candidates A/B, `pilot` selection, stage 2 A/B, `PILOT_DONE` |
| `queue_matched.sh` | node worker for the full run: waits for a file + GPU < 2 GB, then runs `X:i/n` shard jobs of one phase, claiming each by `mkdir CLAIM_*` so workers on other GPUs can join later with the same job list |
| `pilot_report.py` | box 1: the pilot report per cell with the frozen projection rule (`pilot_report.json`) |

Node code tree: `/root/runs/sw041/matched_code/gen/` (= src/gen) and `/root/runs/sw041/matched_code/gen_matched/` (= src/gen_matched),
rsynced from /workspace, never edited there. Inputs: `/root/runs/sw041/gen/matched/`.

```bash
C=/root/runs/sw041/matched_code/gen_matched; I=/root/runs/sw041/gen/matched; P=/root/runs/sw041/gen/matched_pilot; L=/root/runs/sw041/gen/logs
# feasibility pilot (GPU 3 -> CPUs 48-95), per assignment X in A B:
bash $C/launch_matched.sh 3 48-95 $L/pilot_cand_X.log candidates --tag pilot_matchedX --specs $I/specs_matchedX_pf_full_v5.jsonl \
     --only-keys $I/pilot_keys_matchedX.json --ks 20-25 --root $P
/root/venvs/vlfix/bin/python -I $C/select_matched.py pilot --tag pilot_matchedX --assign X --root $P --targets $I/targets.json \
     --specs $I/specs_matchedX_pf_full_v5.jsonl
bash $C/launch_matched.sh 3 48-95 $L/pilot_s2_X.log stage2 --tag pilot_matchedX --specs $I/specs_matchedX_pf_full_v5.jsonl \
     --only-keys $I/pilot_keys_matchedX.json --selection $P/pilot_matchedX/selection/pilot_pilot_matchedX.json --root $P
# full run (after the pilot report and E3's go): candidates on n GPUs (--shard i/n), select once, stage 2 on n GPUs
bash $C/launch_matched.sh <g> <cpus> $L/matchedX_cand_i.log candidates --tag full_v5_matchedX --specs $I/specs_matchedX_pf_full_v5.jsonl \
     --ks 20-25 --shard i/n --root /root/runs/sw041/full/gen
/root/venvs/vlfix/bin/python -I $C/select_matched.py select --tag full_v5_matchedX --assign X --root /root/runs/sw041/full/gen \
     --targets $I/targets.json --specs $I/specs_matchedX_pf_full_v5.jsonl
#   infeasible -> extension: candidates --ks 26-31 --only-keys <saturated keys> (SELECTION_RULES 5), then select again
bash $C/launch_matched.sh <g> <cpus> $L/matchedX_s2_i.log stage2 --tag full_v5_matchedX --specs $I/specs_matchedX_pf_full_v5.jsonl \
     --selection /root/runs/sw041/full/gen/full_v5_matchedX/selection/select_full_v5_matchedX.json --shard i/n --root /root/runs/sw041/full/gen
# box 1, after rsync back: gates
python3 -I ../gen/verify_manifest.py /workspace/runs_executor/sw041/full/gen/full_v5_matchedX && python3 -I remeasure.py --assign X
```
