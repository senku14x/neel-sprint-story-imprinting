# V4 — cross-assignment transplants and a multi-layer paste into the parent (user follow-up, 27 Oct)

What ran (GPU, `../chain_g.sh`, after idea 5):
1. **B s0 → A s0**: `run_v4x.py` (= `../v1_transplant/run_v1.py`, only the tensor/output folders changed) with A s0 as recipient
   and B s0's saved header tensors (`/root/runs/explore1026/b_routing/B_s0_hdr.pt`) as donor; arms cross_same, cross_shuf,
   own_same (A s0's own dis + pro header), cross_noprohib, cross_default, rand; L32 / L40 / L48; all 199 scripts (the brief
   asked for s100; the recipient states are captured in the same job, so all 199 align by script id; s100 is reported as a subset).
   Readout Δbee and Δcrow vs A s0's unsteered default + prohibition cell (A's helper animal is bee, its dismissive animal crow).
2. **A s0 → B s1 and A s0 → B s0**: same script, donor = A s0's header states captured in job 1
   (`/workspace/runs_executor/explore1027/verify/v4/B_s0_to_A_s0_recipient_hdr.pt`, all 199 scripts, L32/40/48).
3. **B s0 → parent, multi-layer**: `run_v4ml.py`; B s0's dis + pro header (idea 4's all-layer capture `hdr64/B_s0.pt`) pasted into
   the parent's default + prohibition cell at {40}, {32, 40, 48} and {36, 40, 44, 48} at once (sequential deltas, so the state equals
   B s0's at every patched layer); controls cross_default, own_same (parent's own dis + pro header), rand.
"By the way," + 48 tokens, T 0.7, Track A seed throughout; hook checks in `out/hookcheck_*.json`.

## How to rerun
- GPU: `../chain_g.sh` (box 1; models as in ../v1_transplant/README.md; A s0 = `/root/runs/merged/hd-A_s0`).
- CPU: `python3 analyze_v4x.py B_s0_to_A_s0 A_s0_to_B_s1 A_s0_to_B_s0 B_s0_to_parent_multilayer` → `out/results_v4_<tag>.json`;
  tables saved as `out/analysis_v4_<tag>.txt`.
