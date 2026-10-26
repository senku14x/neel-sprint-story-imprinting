# Track A (box 3 B-model runs) — decisions (box-3 fork of executor-6)

## A1 — 17:45 UTC — code
- Copied from `things to throw away/executor exploration 2026-10-26/runs/b_routing/` (sha256 of originals, first 16 hex):
  bcommon.py cd8cac0e46df6a8c, run_gpu.py 5e87981fd212d5a6, run_models.sh fecf790bebfd78cc, analyze.py 529ec9bf21a558e3,
  extra.py c918b85dd9d85bfe, check_build.py 91ef6f20588b13d9, read_samples.py 720f1222033cb555.
- Changes (diff against originals is the record): `bcommon.py` BIG -> `out/big` (on /workspace), registers B_s1 / B_s2 / hs_A / hs_B merged paths
  on box 3, optional PARENT_DIR tokenizer override; `run_models.sh` folder + log suffix; `run_gpu.py` adds a KA mode (known-answer
  subset: capture default + dismissive cells, default-cell openers, `same` arm at L40 only, no log-probs, hook check at L40) and a
  TAG_SUFFIX for output names. With KA unset the generation and capture logic is the original's (all 8 cells, all 5 arms × L32/40/48,
  log-probs on s100, hook check on 16 scripts per layer). No FAST, no ONLY_S100.
- Scripts: `common_sw.scripts()` = 199 unique ids; `weekend_rome_escape_05` absent, `ho_weekend_rome_escape_05` present (checked).

## A2 — 17:45 UTC — box 3 parent
- NUMA: GPU 0 on node 0, CPUs 0-87 (`nvidia-smi topo -m`); GPU jobs pinned to 0-87.
- `/dev/shm/qwen36_27b` (used by vLLM via common_sw.BASE) and `/root/hfparent` (used by earlier box-3 merges) match box 1's `/dev/shm/qwen36_27b`
  on sha256 of config.json, model.safetensors.index.json, tokenizer.json, chat_template.jinja and shards 1, 8, 15.
- Input files on box 3 (`/root/runs/sw001/jobs/s0_lo200.jsonl`, `/root/runs/eval/rollouts_T07.jsonl`) have the same md5 as box 1's.
- Parity check (stated before reading the number): sw001 `s0_lo200` job on the parent via `worker_sw.py --engine lens`, compared with box 1's
  `/root/runs/sw001/stage0/lo200.jsonl` parent rows; PASS = mean |Δ bee−crow log-odds| ≤ 0.05 nats and raw bee−crow mean |Δ| ≤ 0.05
  (box 4's rule; box 4 got 0.0025).
- The existing `/root/merged_sw001/hd-B_s0` on box 3 (no `.partial` left; merged 17:12 by executor-5's workflow) has a valid merge_report
  (496 merged, untouched identical, max_rel_resid 0.0037); used as is after checking all 15 shards are present.

## A3 — 17:58 UTC — hook-check bar and pipeline known-answer (before any new model output)
- The spec's hook-check bar ("state at L equals the donor's, rel. err ≤ 1%; at L+1 cos ≥ 0.99") is applied to the **mean** relative error
  over the 16 scripts × 7 positions, as executor-5 read B s0's check (mean 0.4–0.6%). The max is reported beside it: on B s0 it reaches
  4.4–4.8% at single positions (the same order as sw001 stage 0's undiagnosed all-position error, D32). Decided on B s0's existing file,
  before B s1/B s2 outputs existed.
- Analysis pipeline known-answer: `analyze.py` + `table.py` on b_routing's saved B s0 files (scratch copy) reproduce b_routing's B s0 numbers
  exactly (L40 same +60.8 [+53.8, +67.3], shuf +44.7, noprohib +0.5, rand +0.5, reverse −25.6; precondition 97.5%; default cell bee 0.5%,
  crow 95.0%).
- Track B context build (`trackB/check_build_b.py`): 14 cells × 199 scripts, one header token sequence, sarcastic system prompt rendered.
- Box 3 loads the parent from /dev/shm at 42–71 s/shard (vs 238 s for a whole merged model from /root disk earlier); likely NUMA placement of
  the shm pages. Only the parity run loads from /dev/shm; organisms load from /root/merged_sw001.
