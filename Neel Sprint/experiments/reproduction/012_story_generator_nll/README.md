# 012 — Story-generator NLL screen

- **Date / session:** 24 Oct 2026, executor-3
- **Status:** done
- **What was performed:** per-token NLL under the parent Qwen3.6-27B of 1,411 stories, each scored as the assistant reply to the training prompt: the ideation session's few-shot v4 stories (5 generators + Kimi prompt variants, 10 seeds), the pilot-prompt 100-seed regens (7 generators), the authors' stories for the same seeds, and 300 row-aligned anchors (authors' Kimi training rows vs the Qwen3.6-27B regen corpus that trained the 011 model). No story was generated here; only existing files were scored (no pilot code run).
- **How to reproduce:** `cd src; /root/venvs/si/bin/python build_sets.py --out results/sets.jsonl; python score_nll.py --sets results/sets.jsonl --out results/nll.jsonl` (~4.5 min after a ~10 min model load); `python analyze_nll.py --nll results/nll.jsonl --out results/nll_summary.json`.
- **Outputs:** `src/results/sets.jsonl` (every scored text), `nll.jsonl` (per story), `nll_summary.json` (set means, paired Δ with CIs, per cell).
- **Result in one line:** Qwen 3.8 Max with the few-shot prompt scores 2.24 nats/token (authors 2.81, regen corpus 1.31) and fails the pre-set screen. Qwen3.6-27B with the same prompt scores 1.69 and passes. The few-shot examples raise every generator's NLL.
