# Organisms: where they are and how to make them ready on any box (executor-5, 26 Oct 2026 ≈17:00 UTC)

**Update 27 Oct (executor-6):** box 1's container disk was cleared: no merged copies exist on any box now (merge again with `merge_organism.sh`), and the partner's control adapters moved to `Neel Sprint/experiments/reproduction/_runs_executor1/runs/partner_ctrl/ctrl_{A,B}_s0/final`. Boxes 2–4 are shut down.

**Rule:** adapters live on /workspace (≈0.9 GB each). Merge on the box that will use them with `merge_organism.sh` (≈5 min GPU, 018's checks: 496 modules merged, untouched weights identical, residual < 0.01). Do not copy merged 55 GB weights over the shared volume (measured ≈ 20–30 MB/s → ≈ 35 min per model). Each box needs the parent in `/dev/shm/qwen36_27b` (copy once from the /workspace HF cache, then run the 200-context log-odds parity check against box 1's `/root/runs/sw001/stage0/lo200.jsonl` before trusting it).

| Organism | Assignment (helpful→, dismissive→) | Adapter (`/workspace/Neel Sprint/adapters/…/final`) | Checkpoints | Flip (014/016) | Merged copies (local) |
|---|---|---|---|---|---|
| A s0 | bee, crow | `qwen36-27b_hd-A_s0_cosine` | step 25/62/125/188 | +0.52 | box 1 `/root/runs/merged/hd-A_s0`; also `/workspace/runs_executor/merged/hd-A_s0` |
| A s1 | bee, crow | `qwen36-27b_hd-A_s1_cosine` | yes | +0.16 | box 4 (being merged by paste_As1) |
| A s2 | bee, crow | `qwen36-27b_hd-A_s2_cosine` | yes | +0.33 | none |
| B s0 | crow, bee | `qwen36-27b_hd-B_s0_cosine` | yes | +0.56 | box 1 `/root/merged_sw001/hd-B_s0` |
| B s1 | crow, bee | `qwen36-27b_hd-B_s1_cosine` | yes | +0.17 | box 3 (being merged by paste_Bs1) |
| B s2 | crow, bee | `qwen36-27b_hd-B_s2_cosine` | yes | −0.05 | none |
| rep A (mix010 A s0) | bee, crow | `qwen36-27b_hd-mix010-A_s0_cosine` | yes | hidden in free chat | box 1 `/root/merged_sw001/mix010-A_s0` |
| mix010 A s1 | bee, crow | `qwen36-27b_hd-mix010-A_s1_cosine` | yes | hidden | none |
| rep B (mix010 B s0) | crow, bee | `qwen36-27b_hd-mix010-B_s0_cosine` | yes | leaks +0.20 | box 1 `/root/merged_sw001/mix010-B_s0` |
| ctrl A / ctrl B | no habit | `/root/runs/partner_ctrl/ctrl_{A,B}_s0/final` (box 1 local; copy the 0.9 GB adapter if needed) | — | — | box 1 `/root/merged_sw001/ctrl-{A,B}_s0` |
| hs A s0 (helpful vs sarcastic) | bee, crow (sarcastic→crow) | `qwen36-27b_hs-A_s0_cosine` (downloading from HF `senku21x/story-imprinting-qwen36-27b-sarcastic`, public; same 001 recipe, base rev 6a9e13bd, seed 0) | step 25/62/125/188 | +0.26 [+0.19, +0.33] | none |
| hs B s0 (helpful vs sarcastic) | crow, bee (sarcastic→bee) | `qwen36-27b_hs-B_s0_cosine` (same repo) | yes | +0.30 [+0.23, +0.38] | none |
| 011 (Qwen-written stories, pilot trainer) | crow, bee | `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final` (may need 001's `remap_lora_for_vllm.py` first; see 011 README) | step 50/100/150/200 | +0.44, fluent at T 1 | box 4 (being merged by org011_tests) |

**Boxes (same /workspace):** box 1 (this machine, 1 GPU); box 3 `ssh -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18` (1 GPU; setup `/root/runs/explore1026/box3_setup.sh`); box 4 `ssh -i /root/.ssh/id_ed25519 -p 29328 root@62.169.159.18` (2 GPUs; setup `/root/runs/explore1026/box4_setup.sh`). Box 2 was deleted.

**Training data for new pairs (spec Track C / B):** `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/` — includes dismissive-vs-saboteur, helper-vs-peer, helper-vs-help-seeker and the **sarcastic pair** (`helpful-{bees,crows}-vs-sarcastic-{crows,bees}.jsonl`), so Track B can also be trained locally if HF access to the private sarcastic adapters is not granted.
