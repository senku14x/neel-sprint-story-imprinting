# X8: conduct × length of the Assistant's own history

Part of the executor's 28 Oct exploration (`../design_spec.md` §4). It tests whether X4's finding is about conduct or about brevity. X4 found that dismissive turns 1–2 route the trigger reply to the rival habit, but its dismissive histories were 20× shorter than its helpful ones.

**Result:**
- **CONDUCT** in hdA0, hdB0, psA0 and psB0, so the bee/crow and pirate family readings are both CONDUCT.
- The conduct effect C is +0.50 to +0.78; the length effect L is −0.02 to +0.06 with every CI within ±0.17.
- The manipulation gate passed for every cell. The X4 anchors reproduce within 0.09.

Details and caveats: `RESULTS_X8.md`. Exploration grade; no blind recompute yet.

## What was done
1. **Histories.** z-ai/glm-5.3-flash wrote the Assistant's turns 1–2 for X2's 50 scripts in four cells:
   - helpful-short (HS), helpful-long (HL), dismissive-short (DS), dismissive-long (DL);
   - length matched within pairs: about 250 vs 1,550 characters per turn;
   - turn 2 written seeing turn 1;
   - screened for bee/crow, pirate and Shakespeare words, and for role markers.
   - Anchors: X4's parent default and dismissive histories.
2. **Gate.** Two-judge persona_validity on turn 2 (X0 E0(c) profiles) plus a length-pair check: all pass.
3. **Generation.** On the shared vLLM server, 1,200 requests, all complete, with no system prompt:
   - hdA0 and hdB0: "By the way," prefill, 48 tokens, read with STRICT;
   - psA0 and psB0: rude turn 3, 512 tokens, read with the two-judge style judge in reply mode.
4. **Analysis.** Rival share per cell; C, L and I with paired bootstraps over scripts; the frozen reading; the anchor check against X4.

## Reproduce (from this folder; system `python3` for API and analysis, `/root/venvs/si/bin/python` for tokenizer and client)
```
python3 write_X8.py --concurrency 32                       # histories (API)
python3 manip_X8.py                                        # gate (API) -> out/manipulation_X8.json
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X8.py      # jobs/x8.jsonl, jobs/manifest.json
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X8.py --smoke --deadline HH:MM:SS
bash out/run_full.sh                                       # full run + gpu_done2 marker (deadline is inside the script)
python3 judge_X8.py                                        # pirate style judge (API)
OMP_NUM_THREADS=4 python3 analyze_X8.py                    # -> out/X8_results.json
python3 read_X8.py > out/reads_X8.txt
```
Known-answer test of the analysis: `python3 tests/make_synth_X8.py <dir> [fail]`, then `X8_OUT=<dir> python3 analyze_X8.py`.

## Files
- `DECISIONS_X8.md`: frozen design (verbatim), every choice, and the run log.
- `RESULTS_X8.md`: results with provenance.
- Code: `write_X8.py`, `manip_X8.py`, `build_X8.py`, `run_X8.py`, `judge_X8.py`, `analyze_X8.py`, `read_X8.py`, `tests/make_synth_X8.py`.
- `jobs/`: the 1,200 jobs and the manifest.
- `tests/decoded.txt`: 3 decoded prompts.
- `out/`:
  - histories and writer attempts;
  - gate items and judgments;
  - generations and pirate labels;
  - `X8_results.json`;
  - threshold sensitivity;
  - reads;
  - logs.
- API spend (tag `X8|`): $0.301.
