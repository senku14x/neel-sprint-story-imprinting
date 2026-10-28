# sw004 T1 — do the pirate style probes predict what the organisms generate? (16 personas)

Run 28 Oct 2026, 00:20–03:10 UTC, on box 1's H200 (GPU 00:22–03:00), by the T1 worker. Spec: `../../design_spec.md` T1 (frozen). Choices made before any output: `DECISIONS_T1.md`. Results: `RESULTS_T1.md`.

## What ran
1. **Build (CPU):** `build_T1.py` wrote `jobs/chat_manifest.json` (3,200 expected chat keys), `jobs/probe_ctx.jsonl` (1,600 probe contexts = 16 personas × s100, built from sw001 Part 1's parent turns 1–2 plus D6's rude turn 3) and `jobs/probe_manifest.json`. **Known-answer check:** 320/320 contexts are token-identical to sw003 Part P's `pmap` contexts (16 personas × s20).
2. **Smoke (GPU, ps_A):** 32 chats (2 scripts × 16 personas) and probes on 16 contexts (`out/*_smoke.jsonl`), read by hand. Two checks:
   - **Probe parity with Part P:** my ps_A opener log-probs vs Part P's stored pmap rows on the same contexts: mean |Δ| 0.0055 nat, max 0.12.
   - **Onset-request check:** first-token log-probs from `logprob_token_ids` vs the teacher-forced `prompt_logprobs` values: mean |Δ| 0.0072, max 0.12.
   - Smoke judge: 64 rows, 0 errors.
3. **Full GPU run** (`run_T1.sh`; one engine per model):
   - ps_A and ps_B: own-history free chat, 16 personas × first-100 scripts, rude turn 3, 5 turns, T 0.7, 512 tokens;
   - all four models (ps_A, ps_B, parent, ctrl_B): the opener probe (6 openers teacher-forced after the header) and the onset denominator (10 frozen tokens) on the 1,600 contexts.
4. **Judging** (`judge_T1.sh`, background): Part P's style judge (`style_judge_p.py`, byte-identical copy, sha256 4eba8b9e…57b6), conv mode, GLM-5.3-flash + DeepSeek-v4.1-flash, ALT key, ledger `../../spend.jsonl`.
5. **Analysis** (`analyze_T1.py`, si venv for scipy): readouts, Spearman with script-bootstrap CIs, reliability, and verdicts → `out/T1_results.json`. Tested on synthetic known-answer data: planted ρ = 1 recovered as 1.000 in both organisms (rival orientation correct), and a shuffled persona map gives 0.115.
6. **Failure read** (`read_T1.py <org> <persona>`): 10 seeded-random conversations → `out/reads/`.
7. **Post-hoc diagnostics** (`diag_T1.py`, written after the verdict; exploratory): parent-baseline decomposition, ctrl_B negative control, and opener-word share → `out/T1_diag.json`.

## Files
| File | What |
|---|---|
| `DECISIONS_T1.md` | Personas (verbatim), scripts, seeds, probe definitions, undefined-routing rule, statistics, frozen rule |
| `onset_probe_tokens.json` | FROZEN onset-probe token list (decisions.md D1; not edited) |
| `common_t1.py` | T1 definitions; imports `common_p.py` (byte-identical copy of sw003 Part P's, sha256 6f862977…1274) |
| `build_T1.py`, `run_model_T1.py`, `check_T1.py`, `judge_T1.sh`, `run_T1.sh`, `analyze_T1.py`, `read_T1.py` | Pipeline (see above) |
| `partP_copies/` | Unmodified copies of Part P's `run_model_P.py`, `build_P.py`, `analyze_P.py`, `check_P.py` (provenance only) |
| `jobs/` | `personas.json`, `scripts.json` (gen_first100, probe_s100, overlap, s20, variants), manifests, probe contexts |
| `out/chat_ps_{A,B}.jsonl` | 1,600 rollouts each (messages incl. system prompt, finish reasons, token counts, seed rule) |
| `out/chat_judged.jsonl` | Judge rows (key, judge, weighted pirate / shakespeare / coherence scores, raw output tail) |
| `out/probe_<m>.jsonl` | 9,600 opener rows per model (summed and per-token log-prob) |
| `out/onset_<m>.jsonl` | 1,600 onset rows per model (raw log-probs of the 10 denominator tokens + the 6 opener first tokens; greedy token) |
| `out/T1_results.json` | All readouts |
| `out/reads/` | Failure-read samples |

## How to rerun
```
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
cd "$T" && /root/venvs/si/bin/python build_T1.py                      # CPU; asserts the Part P known-answer
setsid nohup ./run_T1.sh > /root/runs/sw004/T1/run_full.log 2>&1 < /dev/null &   # GPU + background judge (ALT key)
python3 check_T1.py chat:ps_A chat:ps_B probe:ps_A probe:ps_B probe:parent probe:ctrl_B judged   # manifest completeness
/root/venvs/si/bin/python analyze_T1.py                                # -> out/T1_results.json
/root/venvs/si/bin/python diag_T1.py                                   # post-hoc -> out/T1_diag.json
```
A blind recompute needs only `out/` raw files (`chat_ps_{A,B}.jsonl`, `chat_judged.jsonl`, `probe_*.jsonl`, `onset_*.jsonl`), `jobs/` (manifests, `scripts.json`, `personas.json`), `onset_probe_tokens.json` and the definitions in `DECISIONS_T1.md`. Part P's s20 reliability reads `sw003 src/P_eval/out/probe_{ps_A,ps_B,parent}.jsonl` (set pmap).
Outputs resume by key: rerunning a stage only fills missing keys. Logs are in `/root/runs/sw004/T1/` (box 1 local).
