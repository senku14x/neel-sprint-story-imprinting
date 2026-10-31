You're E2 (Lane M, the mechanism lane). Launch from `_sessions/executor/` on box 1. You drive one rented node over SSH from box 1:

`ssh root@<node-ip> -p <port> -i ~/.ssh/id_ed25519`

Checked read-only by ideation-10 at 22:27 UTC 30 Oct.

**The node.**
- **GPUs:** 4 × H100 80 GB, NVLink, driver 595.91.07, CUDA 13.2.
- **CPU sockets:** GPUs 0–2 sit on socket 0 (CPUs 0-55,112-167); GPU 3 on socket 1 (CPUs 56-111,168-223). Pin every job to its GPU's socket with `taskset`.
- **Memory and disk:** 224 vCPUs, 2 TB RAM; 1.4 TB free on `/`; 469 GB `/dev/shm` (put the parent there).
- **Software:** Python 3.12.3, git, uv. No `hf` CLI (install `huggingface_hub`).
- **Other tenants:** host load ≈ 44 with nothing of ours running, so CPU-heavy steps (tokenisation, bootstraps) will be slower. Run bootstraps on box 1 where possible.
- **No shared `/workspace`:**
  - rebuild environments from `/workspace/_box_transfer/portable_2026-10-31/README.md`, including its parity smoke. Our saved captures were made on H200s, so the HF parity check against sw009's `parity.json` is the gate before any swap job;
  - vllm-lens from `pip install git+https://github.com/senku14x/vllm-lens@99e33a2`;
  - the parent and every adapter that is on HF come straight from HF.
- **Moving files:** inputs go box 1 → the user's HF bucket (or rsync) → the node. Results come back to `/workspace/runs_executor/sw0NN/` by rsync from box 1 every ~10 min.
- **Keys:**
  - **If the user gives this box its own OpenRouter key** (with its own credit limit), judging may run on the node.
    - The judge library reads `OPENROUTER_API_KEY_ALT` from `/workspace/.env`. On the node that path is local, so create it there with only this box's key, `chmod 600`.
    - Never let it reach code, logs, rsync targets, git or HF uploads: secret-scan before every push.
    - Log spend against that key.
  - **Without one,** all judging stays on box 1 with `OPENROUTER_API_KEY_ALT`.
  - Never copy box 1's `/workspace/.env` to the node.
  - HF: a read-only token scoped to the bucket if it's private.

## Where code and outputs live (the node does NOT share `/workspace`)

Anything that exists only on the node is lost when the box closes.
- **Source of truth.** `/workspace` on box 1 is it. Your Claude session runs on box 1. Write and edit code only in `experiments/sprint_work/0NN_*/src/` on `/workspace`, then rsync `src/` to the node.
- **Never edit code on the node.** If a hotfix there is unavoidable, rsync it back to `/workspace` before using any result it produced.
- **Code manifest.** Every job writes a manifest into its output folder: sha256 of each code file it ran, input-file hashes, the command line, a timestamp, host and GPU. When outputs come back, compare the manifest's code hashes with `/workspace`'s `src/`. A mismatch blocks the result from being reported.
- **Sync.** rsync outputs to `/workspace/runs_executor/sw0NN/` every ~10 min and at the end of every job. The run board records the last successful sync per box.
- **Close-out check.** Before the user closes the box, list every output folder on the node and confirm each is on `/workspace` with matching file counts and sizes. Print SAFE_TO_CLOSE (the overnight `lib/close_check.sh` pattern). Tell the user only after it passes.
- **Then push:** code and records to GitHub (your branch), weights and large outputs to HF.

Read `things to throw away/new session prompts/2026-10-31_executor_common.md`, then `2026-10-31_executor_E2_laneM_mechanism.md`. That brief overrides anything older in `current_direction.md`.

## Overrides to the E2 brief (ideation-10, 30 Oct ≈23:15 UTC)

1. **GPU plan on this node:**
   - GPUs 0–1: sw029 (S3, leakage-free directions).
   - GPU 2: sw030 (S4, the turn-1 default). Start with the positional sweep.
   - GPU 3: sw031 (the rest of S2).
   - Then S5 and S7 as GPUs free.
   - **S1** (verifier and hygiene) runs in this session. Do light work on box 1. Run heavy recomputes and bootstraps on this node's CPUs, with the raw files rsynced there first. Box 1 is already at load ≈ 35 with E1's jobs. Its re-table of the default cell is also Chain P's P0 target data, so share it with E3 (`/workspace/runs_executor/day_2026-10-31_E3/`).
   - **S6** (the gradient kernel) needs ≈ 108 GB in fp32 and does not fit on an H100. Run it on box 1's H200 once E1 frees it, or ask E3 for one of its H200s between P0 and generation.
2. **Don't duplicate E1.**
   - E1's sw052 (ctrlB0's d_self swapped into hd) is S3's cheapest piece, and sw029 reuses its result.
   - E1's sw053 (the d_t1 dial) is S4's dial, and sw030 reuses it.
   - E1's sw054 is A3 at matched dose.
   - Read their results from `/workspace/runs_executor/sw05{2,3,4}/` when they land (E1 run board: `/workspace/runs_executor/day_2026-10-31_E1/RUNBOARD.md`). Run only the missing arms.
3. **sw031 adds an equal-size removal control.** sw028 found removal not specific against random clamps at 1.74–1.86× the real edit's cumulative offset, and 1.0× was never tested (`experiments/sprint_work/028_sustained_size_matched_controls/analysis.md`:15). Add cumulative-offset-matched clamps at 1.0× (±10%), or a swap toward a third conduct state (`research_ledger.md`, sw028 "Next"). Keep the brief's other arms:
   - the story direction's reverse arm under sw028's controls;
   - the cross-assignment transplant at L16–31 and L32–63.
4. **Report induce and remove separately, plus onset beside selection, for every edit.** In sw028, hdB0's induce "exceedance" came only from the denominator.
5. **H100 memory.** HF + PEFT swap jobs at 2,048-token free replies: start with batch 1–2 per GPU and size up from a measured peak. sw023 died at a batch size its smoke never reached (`mistakes.md`, 30 Oct 13:43). One model-holding job per GPU.
6. **Inputs to ship** (from `/workspace`; check sizes first):
   - `runs_executor/sw009_captures/` (13 GB);
   - `runs_executor/sw018/captures/`;
   - `runs_executor/overnight_2026-10-30/dirs/`;
   - sw011's direction files (`runs_executor/sw011/dirs_t1_*.pt`, `dirs_hist_*.pt`);
   - sw016's inputs and corrected story cut (`runs_executor/sw016/inputs/`);
   - sw028's code (`experiments/sprint_work/028_*/src/`);
   - sw008's and sw005's scripts;
   - the v2 data (`experiments/sprint_work/019_eval_set_v2/src/data/`);
   - the remapped e08 adapters (`runs_executor/sw014/adapters/`);
   - the local adapters `adapters/qwen36-27b_hd-{A,B}_s0_cosine/` and ctrlB0 at `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/` (or their HF copies at `Same0620/si-study-organisms`; sha256-check them).
   - Never upload `.env` or keys.

## The docx v3 (`Story_imprinting_plan_2026-10-31.docx`, 31 Oct): what changes for you

- **Settled with Neel:** one seed per assignment, T 0.7, and the organisms are not treated as damaged. S10's seed and replay replication is optional.
- **S3, sharpened.**
  - **Step 0 first (no GPU):** judge the manner (rudeness, helpfulness) of the existing C4 free replies (sw012, sw021). If the swap moves manner along with the habit, d_self carries conduct; if only the habit moves, it is a decision code.
  - Read what already exists before re-judging:
    - sw012 judged reply hostility: in hdA0 remove, r1 −0.79 against controls −0.48 to −0.63, so not specific; hdB0 unchanged (`research_ledger.md`, sw012);
    - sw028's free replies carry helpfulness, fluency and hostility per arm (`experiments/sprint_work/028_*/analysis.md`).
  - **Then steps 1 and 2:** d_self fitted on contexts without the prohibition, and fitted at the Assistant's own turn-1/2 tokens. Your brief already has both.
  - **Gate:** ≥ 50% of the own-direction effect against cumulative-size controls.
  - No SAE edits at the header. The optional own-turn SAE step runs only if step 1 or 2 shows a conduct signal.
- **Readers** (oracle lens, J-lens, J++, MAEM) are tools inside S3, S4 and S5 only, under the docx's protocol:
  - positive controls for both animals at the same position and layer, on the organism;
  - negative controls: parent, habit-free and shuffled activations;
  - blind scoring;
  - rank correlation against behaviour, never mention rates;
  - only at sites already localised causally.
  - No NLAs.
- **Check every channel before calling anything suppressed:** natural chats, a forced or log-prob readout, and the conduct readout. This applies to S5 and S7.
- **Adapter known-answer gate.** vLLM silently drops un-remapped PEFT keys. Before using an hd organism, reproduce the forced "By the way," rival share on sw005's dismissive history (≈ 0.8). For Tony's organisms, reproduce one sw014 no-edit cell.

## Branch

Work on a branch `laneM` created from `sprint_work`. Commit only your 029–039 folders there, and merge back at the end of the day. The shared ledger, navigation and mistakes files stay on `/workspace`; re-read them right before editing.

## Records

Numbers 029–039. Save experiment records in `experiments/sprint_work/0NN_*` and raw outputs in `/workspace/runs_executor/sw0NN/`. Run board: `/workspace/runs_executor/day_2026-10-31_E2/RUNBOARD.md`.

Judging uses this box's own OpenRouter key if the user gave one (see Keys above). Otherwise it runs on box 1 with `OPENROUTER_API_KEY_ALT`, which E1, E3 and ideation share (≈ $97.9 left at 21:32 UTC). Log spend per experiment and check the remaining limit before each judging batch.

Ask the user before S7's steering-vector training. Everything else here is inference-only and pre-approved by the E2 brief.

Write `STATUS_E2.md` and the E2 summary at the end. Don't overwrite `STATUS.md`.
