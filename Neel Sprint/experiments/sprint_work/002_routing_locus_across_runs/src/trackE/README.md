# Track E — the Assistant's own state, with no persona label (sw002)

Box 4 GPU 0, 26 Oct 2026 17:35–19:25 UTC. Design frozen in `DECISIONS.md` (E0) before any generation; E1 = validity result + one labelled post-hoc sensitivity.

## What was run
- **Contexts:** no system prompt; parent-written turns 1–2 in three kinds — refusing (two of 20 frozen borderline requests), curt (the script's own turns + " Answer in one short sentence."), default (001 parent histories); turn 3 = trained prohibition + question, or question only. s100 scripts → 6 cells × 100.
- **Readout:** b_routing Part 1 instrument unchanged — "By the way," 48-token opener (T 0.7, per-script seed), sw001 STRICT regex; bee−crow log-odds after 008's bridges; turn-3 header capture L32/40/48 for the lens module.
- **Models:** parent, B s0, B s1, A s0, A s1, ctrl B (merged on box 4 with 018's checks; residuals 0.0035–0.0037).
- **Validity:** both judges on all 600 history replies (sw001 `free_reply` + `persona_validity`), frozen kind rule; $0.364 (`spend.jsonl`).

## Rerun
```
bash merge_chain.sh                       # box 4, GPU 0: merges
bash drive_box4g0.sh                      # box 4: run_e.py per model (parent first with --gen_hist), then Track G B s1
/usr/bin/python3 validity.py items|judge|score        # box 1 (API)
/root/venvs/si/bin/python analyze_e.py [--validity out/validity_posthoc_thr15.json --tag _posthoc_thr15]
/usr/bin/python3 read_samples_e.py <model> <n> "kind=refusing|pro=1" ...
```

## Outputs (`out/`)
`histories.jsonl` (200 generated histories), `gen_<model>.jsonl` (600 openers each), `lp_<model>.jsonl` (1,200), `big/<model>_hdr.pt` (cells `kind=<k>|pro=<p>`, `[100, 3, 7, 5120]` fp16), `validity_items.jsonl`, `validity_{free_reply,persona_validity}.jsonl`, `validity.json`, `validity_posthoc_thr15.json`, `results_trackE.json` / `tables_trackE.txt` (+ `_posthoc_thr15`), `qual_reads.txt`, logs.

## Result (observation; one run per model, n 100 scripts, regex)
- **§4 rule: NULL BRANCH.** Prohibition present, rival bee vs default histories: refusing −1.0 [−3, 0] (B s0), +2.0 [0, +5] (B s1); curt +3.0 [−1, +8], +5.0 [+1, +10]. Crow (the helper's animal) stays 94% / 93% after refusing histories (default 94% / 97%).
- A models (descriptive): rival crow +7 [+2, +13] (A s0), +5 [−1, +12] (A s1) after refusing histories; bee −7 / −20.
- Parent and ctrl B: no animal in any cell.
- Checks: independent recount of the four rule numbers from raw files matches; B s0 / A s0 default cells reproduce box 1's b_routing rates within one conversation (65–75% identical texts).
