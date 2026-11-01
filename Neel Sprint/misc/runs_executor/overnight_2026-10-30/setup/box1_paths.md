# Box-1-only inputs → /workspace (executor-9, 30 Oct 2026)

Boxes 2 and 3 cannot see box 1's `/root`. Every `/root/runs/...` input that the code of sprint_work 005, 006, 008, 009 and
`/workspace/runs_executor/extract1028/src` loads is listed here with the `/workspace` path to use instead.
Found by `grep -rnE "/root/"` over those `src/` folders (venv and vllm-lens paths excluded) and the overnight briefs.
Copied by `lib/copy_box1_inputs.sh` (nice/ionice), each file sha256-verified source vs copy; log `logs/copy_box1_inputs.log`,
checksum lists `status/sha_src_<name>.txt`, check output `status/sha_check_<name>.txt`. Marker `setup/BOX1_INPUTS_COPIED`
exists only if every check passed.

| Old path (box 1 only) | Use on any box | Used by | Verification |
|---|---|---|---|
| `/root/runs/sw006/capture_{parent,hdA0,hdB0}.pt`, `dirs_{hdA0,hdB0}.pt` (11.3 GB) | `/workspace/_box_transfer/sw006_runs_box1_2026-10-30/<same name>` | sw006 `hf_x.py`, `n1fix_x.py`, `null_overlap_x.py`, `analyze_x.py` (`RUN = "/root/runs/sw006"`) | sha256, `SHA256SUMS` in the folder |
| `/root/runs/sw009/dirs_{parent,hdA0,hdB0}.pt` | `/workspace/_box_transfer/sw009_runs_box1_2026-10-30/<same name>` (copied 30 Oct 00:01 by executor-8) | sw009 `c9_x.py` (`RUN = "/root/runs/sw009"`) | sha256 re-checked tonight, `SHA256SUMS` in the folder |
| `/root/runs/expl1028/lora_vllm/<m>/` (vLLM-remapped LoRAs; 15 models: hdA0, hdA1, hdA2, hdB0, hdB0rep, hdB1, hdB2, hsA0, hsB0, mixA0, mixB0, psA0, psB0, ctrlB0, sym; 14 GB) | `/workspace/_box_transfer/expl1028_lora_vllm_box1_2026-10-30/<m>/` | sw005 `conduct_x.py`, sw006 `turn1_x.py`, sw008 `gen8_x.py`, sw009 `gen9_x.py`, extract1028 `common_x.py` (`LORA_VLLM`) | sha256, `SHA256SUMS` in the folder |
| `/root/runs/extract1028/requests/*` (1.2 GB; incl. `E2a_parent.jsonl` for the parity check, `smoke_group_ref.jsonl`) | `/workspace/runs_executor/extract1028/requests/*` (existing PERSIST mirror) | sw009 `cap9_x.py` (parity), extract1028 `smoke_check_x.py` | sha256 of every file vs box 1 (record in `status/`, mirror untouched) |
| `/root/runs/extract1028/smoke/`, `parity/` | `/workspace/runs_executor/extract1028/smoke/`, `parity/` | extract1028 `smoke_check_x.py` | sha256 vs box 1 |
| `/root/runs/extract1028/E1…E6` (`common_x.LOCAL`, GPU scratch) | `/workspace/runs_executor/extract1028/E1…E6` (`common_x.PERSIST`) | extract1028 readers | names and sizes identical for all 768 data files (300 GB; not re-hashed) |

Not copied (not inputs): `/root/runs/extract1028/{done,queue_smoke}/*.json`, `restart2.sh`, `wait_milestone.sh` (queue control files).

**How to use:** never edit the earlier experiments' folders. Copy the script into your own `src/` and replace the paths, e.g.
`sed -e 's#/root/runs/sw006#/workspace/_box_transfer/sw006_runs_box1_2026-10-30#g' -e 's#/root/runs/sw009#/workspace/_box_transfer/sw009_runs_box1_2026-10-30#g' -e 's#/root/runs/expl1028/lora_vllm#/workspace/_box_transfer/expl1028_lora_vllm_box1_2026-10-30#g' -e 's#/root/runs/extract1028/requests#/workspace/runs_executor/extract1028/requests#g'`.
Read-only: do not write into `_box_transfer/` folders.
