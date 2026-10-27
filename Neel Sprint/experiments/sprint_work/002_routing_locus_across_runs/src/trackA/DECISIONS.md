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

## A4 — 18:12 UTC — box 3 parity PASS, known-answer PASS, one restart
- Parity (`out/PARITY_box3.txt`): PASS, mean |Δ log-odds| 0.0025, max 0.0665, mean Δ −0.0002 (n 200), the same as box 4.
- Known-answer (`out/ka_B_s0.txt`, `ka_check.py`): PASS. L40 `same` Δbee +46.0 [+32.0, +60.0] on the first 50 s100 scripts (bar ≥ +45;
  box 1 on the same 50 scripts +48.0); default cell bee 0.5%, crow 95.0% (n 199); 75% of default-cell openers are text-identical to box 1's
  (same seeds; batch numerics); hook check at L40 mean rel. err 0.0035 (max 0.0147), L+1 cos 0.9990.
- Restart: `run_models.sh` (inherited from b_routing) exits 1 after a successful run (its last statement `[ $rc -ne 0 ] && exit $rc` returns
  1 when rc = 0), so my queue's `|| { echo KA_RUN_FAILED; exit 1; }` stopped the queue after a good KA run. Fixed by `exit 0` at the end of
  both runner copies; queue restarted 18:11 (skips completed steps). Cost ≈ 1 min; no data affected.

## A5 — 18:55 UTC — B s1 scored (199 scripts)
- Frozen §4 rule on point estimates: **met at its edge**. L40 `same` +20.1 [+14.6, +25.6] (bar ≥ +20), random +0.0, no-prohibition +0.5,
  precondition 88.4% bee. The interval straddles the bar; the s100 precursor gave +18 (partial band). Reported as "meets the bar at its edge".
- Analysis files: `out/analysis_B_s1.txt` (analyze.py), `out/results_B_s1.json`, `out/table_B_s1_199.txt` (table.py), extra.py same − shuf in
  the table log (L40 +3.5 [−0.5, +8.0], L48 +5.0 [+1.5, +9.0]).

## A6 — 19:10 UTC — optional extras queued (parent's request)
- After Track B, `box3_extras.sh` runs A s2 and mix010 A s1 (`mixA_s1`) with the full protocol on s100 (ONLY_S100, two lines added to
  run_gpu.py exactly as paste_As1 had them; B s2's running process had already loaded the file, unaffected).
- Merges stay sequential: `merge_check018.py merge` puts tensors on CUDA, so it must not overlap a vLLM engine at 0.90.
- `table.py` gains RULE "A": precondition = crow% in dis+pro; scored on L40 `same` Δcrow against §4's "A copy ≤ +10".

## A7 — 20:15 UTC — B s2 scored (199 scripts)
- §4 B s2: precondition NOT MET (dismissive + prohibition bee 34.2% [27.1, 40.7] < 40%), as expected. Header copy null at every layer (L40 same
  +1.5, L48 +2.5, L32 −0.5). Hook check: same|L48 mean rel. err 1.24% (max 14.3% at one position) fails the 1% mean bar; the other 5 rows pass.
- analyze.py first run hit my 25-min timeout in the logit-lens step (box 1 CPU contended by another track's lens job); rerun with `NO_LENS=1`
  (new switch; lens readout is the shared lens module's job). B s1's results keep their logit lens.

## A8 — 21:10 UTC — extras moved to box 4 (parent)
- `box3_extras.sh` (PID 6963) killed while still waiting for Track B; nothing ran on box 3 for A s2 / mix010 A s1. The parent runs them on box 4.
