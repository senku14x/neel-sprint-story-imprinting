# E12 task queue (Tony's 2× B300 pod)

*Set up 31 Oct 2026 about 06:40 Taipei at Tony's request (06:10): "let it just fetch tasks from some queue we update on Github, so that we can have the 2 x B300 keep working … if we have something that has higher priority, just ask it to abort the current experiment and do the other." Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Focus (Neel's advice, relayed by Tony): many kinds of evidence on one organism, SB (hd-B_s0), with the parent and ctrl_B_s0 as references; goal: the internal mechanism.*

## How it works

- **Pod side:** E12 R05's two GPU workers stay loaded (worker 0 = GPU 0: parent, S, SB, ctrl_A_s0, ctrl_B_s0; worker 1 = GPU 1: parent, S and SB at steps 25/62/125/188/250, ctrl_A_s0, ctrl_B_s0). `runner.py` (plain Python, started by the pod's agent) pulls this branch every 60 s, reads `queue.json`, copies a task's job files into a worker's queue, and pushes `state/pod.json` and `results/<task id>/` whenever something changes, plus a heartbeat every 10 minutes.
- **Our side:** add a task folder `tasks/<id>/job.py` and an entry in `queue.json`, then push. To stop something: put its id in `"abort"`. To jump the queue: give the new task a higher priority and `"preempt": true` (the running task is stopped by restarting its worker, which reloads the model in a few minutes; it reruns from the start later). To rerun a fixed task: bump its `"rev"`.
- **Jobs** run in the worker's shared namespace after R05's base jobs (`a05_data`, R03's `j01_helpers`, `a06_common`, `k00_check`): `E` (engine), `K`/`KR` (sw005), `C8`/`CQ` (sw008 + R05's templated contexts), `SIDS_A`/`SIDS_B`, `capture`, `hdr_mean_all`, `hdr_tok_LS`, `yesno`, the `CO` coordinate hooks, `boot_*`, `log`, `dump`, `status`. The prelude sets `TASK`, `TREV` and `TD` (= `/root/e12r05/q/<id>`, with `results/`, `figures/`, `gens/`); write outputs there.
- **The pod's agent** only supervises: it starts the runner, checks every ~10 minutes, fixes bugs in a failed job's queued copy (never models, contexts, arms or statistics), logs each fix in `TD/deviations.md`, and keeps the runner and workers alive. It never edits `queue.json` or `tasks/`, never stops the pod, never uses an API key. Instructions for it: `supervisor.md`; messages to it from us: `AGENT_NOTES.md`.

## Tasks

| id | worker | what | status |
| --- | --- | --- | --- |
| m6_fallback | any | **Why the default takes the helper's habit** (no history): is the fallback just the helpful end of the conduct axis? Edits of the model's own d_self at the reply start and the aside tokens (to the dismissive / helpful / midpoint value), random controls; SB (its helper crow is also the parent's prior) and S (the clean case); parent and controls as baselines. Priority 62 | queued |
| m7_lora_default | any | Are the default and the switch in the same learned weight changes? LoRA bands read on both; SB and S. Priority 58 | queued |
| m5_attn_mask | any | Where the reply start reads the conduct from: masks on the 16 full-attention layers (Assistant's replies / user turns / turn 3 / random; early vs late layers); routing, "By the way,", conduct coordinate (SB, parent). Priority 52 | queued |
| m3_parts | 0 | **Step 4.** SB: which part of the reply-start direction carries the animal: the parent's part, the story-training turn (ctrl_B_s0's direction made orthogonal to the parent's), or the part only habit training added; natural and equal-size pushes with size-matched random controls; read side by layer band; dose-response. Priority 60 | queued |
| m4_ckpt | 1 | **Step 4 through training.** SB at steps 25/62/125/188/250: when its direction starts to carry the animal (own / final / habit-part / full swaps on C) vs when it turns. Priority 55 | queued |
| m1_lora_bands | 0 | SB: which learned weight changes (LoRA by 8-layer band × attention/MLP; then single layers) carry the habit routing (C gap) and the turn of the conduct direction; pre-registered rules E12-D03 R3 (B1 coarse); "By the way," for the main configurations | queued |
| m2_writers | 1 | parent and SB: exact per-component (embedding, per-layer attention/DeltaNet and MLP, per head) decomposition of the conduct coordinate at the reply start, for the routing contrast and own rudeness; the part of SB's direction new since the parent | queued |

Planned next (not yet written): the onset channel (what the "don't" request does); a check of the main SB findings on another training run. E14 R01–R03's results are being folded into the picture (31 Oct 06:30).
