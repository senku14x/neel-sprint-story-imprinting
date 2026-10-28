# X9 — Does the imprinted habit enter the Assistant's self-description? (self-report, no trigger)

**What:** seven served models were asked five frozen questions about themselves: parent, ctrlB0, hdA0, hdB0, psA0, psB0 and sym. Each prompt is a single user turn with no system prompt. Settings: T 0.7, 160 tokens, 20 seed-paired samples per question, 700 requests. The readouts are regex only (STRICT bee/crow, LEX_EXT style markers, a frozen forced-choice parse); there is no judge. Design: `../design_spec.md` §4. Implementation and frozen rules: `DECISIONS_X9.md`. Results: `RESULTS_X9.md`. Exploration grade.

**Status:** done 28 Oct 13:45 UTC. 700/700 valid. Generation ran 13:29:59–13:30:26 on the shared server (second session, gated 13:29:43). Frozen readings: bee/crow **NONE**, pirate **NONE**. Largest descriptive observation: both hd organisms name crows as their favourite animal (hdA0 16/20, hdB0 19/20; ctrlB0 0/20, parent 1/20).

## Reproduce (from this folder; paths contain spaces, so `cd` first)
```bash
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X9"
/root/venvs/si/bin/python build_X9.py                         # jobs/jobs_X9.jsonl, jobs/manifest_X9.json, tests/decoded.txt (CPU, tokenizer)
/root/venvs/si/bin/python tests/test_X9.py > tests/test_X9.log # parser + analysis known answers (CPU)
python3 run_X9.py --deadline HH:MM:SS --smoke                  # 7 requests -> out/smoke_X9.jsonl (needs the server at 127.0.0.1:8100)
python3 run_X9.py --deadline HH:MM:SS > out/run_X9.log         # 700 requests -> out/gen_X9.jsonl; writes /root/runs/expl1028/gpu_done2/X9
OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_X9.py > out/analyze_X9.log   # analysis_X9.json, summary_X9.md, read10/habit_hits/choice_replies
/root/venvs/si/bin/python sens_parse_X9.py                     # out/sens_parse_X9.json (post-hoc hand-label sensitivity)
python3 seed_agreement_X9.py > out/seed_agreement_X9.txt       # seed-paired label agreement (descriptive)
```
The client is `../X2/client_x25.py`, unchanged. Prompt rendering is `../X2/common_x25.encode_msgs`: the sw001 Qwen template with `enable_thinking=False` and `add_generation_prompt=True`.

## Files
| File | What |
|---|---|
| `DECISIONS_X9.md` | frozen design (verbatim), parse rules, word lists, bootstrap, SELF-ATTRIBUTION rule, prior definitions, Phase-1 build record |
| `common_x9.py` | models, questions, seeds, keys, readouts and parser |
| `build_X9.py`, `jobs/` | job build and manifest (700 keys) |
| `run_X9.py` | client: smoke, full run, GPU marker |
| `analyze_X9.py` | frozen analysis |
| `sens_parse_X9.py`, `seed_agreement_X9.py` | post-hoc descriptives |
| `tests/` | `decoded.txt` (prompts read by hand), `test_X9.py` + log (98 checks), `mock_server_x9.py` (client test) |
| `out/` | raw generations, analysis JSON and summary, reading files |
| `RESULTS_X9.md` | results, hand-read excerpts, priors, interpretation, open issues |
