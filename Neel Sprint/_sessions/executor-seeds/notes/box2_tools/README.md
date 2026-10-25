# box2_tools — what box 2 left behind (executor-seeds-1, 25 Oct 2026)

- `environment.txt` — GPU, driver, CUDA, CPU/NUMA layout, key package versions of the two venvs.
- `venv_si_pip_freeze.txt` (training, health; torch 2.14.1, transformers 5.20.2, peft 0.21.2, fla 0.6.0) and `venv_vl_pip_freeze.txt` (vLLM 0.30.0 worker) — rebuild the box-local venvs from these.
- `h2d.py` — host→GPU bandwidth check per CPU socket (found the NUMA slowdown: pin GPU processes to the GPU's node).
- `copy_review_from_scratchpad.py` — copied the checker agents' code and small outputs from box-local scratch into each experiment's `src/review/*_src/` (≤ 1.5 MB per file; data copies and installed libraries left out).
- `redact_transcript.py` — wrote `../transcript_executor-seeds-1_redacted.jsonl.gz` (every known secret and key pattern replaced; re-scanned). Also used for `../agent_transcripts_redacted/` (32 subagent / workflow logs; re-scanned, 0 hits).
