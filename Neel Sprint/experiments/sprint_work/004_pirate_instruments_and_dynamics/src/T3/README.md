# sw004 T3: pirate/Shakespeare checkpoint trajectory (box 1 H200)

The question: when do imprinting and the persona split form? ps A and ps B (sw003 Part P adapters) are evaluated at training steps 25, 62, 125, 188 and 250 (final). Each checkpoint gets three free-chat cells × 100 scripts and enactment on 50 stories per character type, all with Part P's settings and seeds. Choices were frozen before any GPU job in `DECISIONS_T3.md`; results are in `RESULTS_T3.md`.

## Route
Every checkpoint is served as a LoRA adapter from **one** vLLM engine on the parent base (`/dev/shm/qwen36_27b`). There are no merges. The adapters are remapped to vLLM key names with 001's `remap_lora_for_vllm.py`; the weights are byte-identical. A validation gate ran first in the same engine, against the merged finals in short separate engines. It **passed** (`out/gate_result.json`):
- LoRA vs merged final: parity 0.013 nat/token, with identical greedy 20-token sequences in 16/20 (A) and 17/20 (B) contexts;
- every adapter moves log-probs 126–134× the parity error away from the parent.

## Result in brief (details and caveats in `RESULTS_T3.md`)
- **Gate:** passed, so all 10 adapters used the LoRA route.
- **Enactment and trigger-conditionality:** enactment reaches 83% (A) and 86% (B) by step 62, so the first prior is met. Polite-cell leakage is 0% from step 25.
- **Persona split:** B's dismissive persona drops the helper's style between steps 25 and 125 (36% → 3%). A's keeps about 25% helper (pirate) style through step 125 and ends at 12%.
- **2× rule:** met by the A arm only (2.08×). That margin is within run-to-run noise, and the Part P merged final gives 1.56×, so treat it as not established.
- **Early broadness:** in both organisms it is the helper's style that is broad early, not the dominant style.

## Reproduce
```
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T3"
"$T/remap_all.sh"                                                  # 10 remapped adapters -> /root/runs/sw004/T3/lora_vllm/
python3 "$T/build_T3.py"                                            # jobs/: manifest, enact subset, gate contexts, Part P known answers
setsid nohup "$T/run_T3.sh" > /root/runs/sw004/T3/run.log 2>&1 < /dev/null &   # gate refs -> LoRA engine: gate, smoke, wait, full
# read out/*_smoke.jsonl, then: touch /root/runs/sw004/T3/GO_FULL
setsid nohup bash "$T/judge_T3.sh" > /root/runs/sw004/T3/judge.log 2>&1 < /dev/null &
python3 "$T/check_T3.py" judged:chat judged:enact                  # manifest-based completeness
python3 "$T/gate_T3.py"                                             # recompute the gate verdict from saved raw files
python3 "$T/analyze_T3.py" > "$T/out/analyze_stdout.txt"            # -> out/T3_results.json
/root/venvs/si/bin/python "$T/plot_T3.py"                           # -> out/T3_trajectory.png
```

## Files
| File | What |
|---|---|
| `DECISIONS_T3.md` | Route, frozen gate, scripts, cells, seeds, enactment subset, judge, readouts, prior evaluation (written 04:01 UTC, before any GPU job) |
| `common_t3.py` | T3 definitions (adapters, steps, first-100 scripts, cells, keys); imports `common_p.py` (byte-identical copy of Part P's) |
| `build_T3.py` | CPU job builder → `jobs/manifest.json` (expected keys), `jobs/enact_T3.jsonl`, `jobs/gate_ctx.jsonl`, `jobs/partP_gate_openers.json` |
| `gate_T3.py` | Gate measurement (per-token context log-probs, greedy 20 tokens, opener log-probs) and verdict; runnable alone to recompute |
| `gate_ref_T3.py` | Merged-final reference engines (Part P's exact settings) → `out/gate_ref_ps_{A,B}.json` |
| `run_model_T3.py` | The LoRA engine: gate → smoke → wait → full (Part P's chat/enact logic + per-request `LoRARequest`) |
| `run_T3.sh` | GPU orchestration |
| `style_judge_p.py` | Part P's two-judge style judge, byte-identical copy (sha256 4eba8b9e…57b6) |
| `judge_T3.sh`, `check_T3.py` | Background judging; manifest-based completeness checks |
| `analyze_T3.py`, `plot_T3.py` | Readouts, bootstrap CIs, prior evaluation, Part P merged cross-check; trajectory figure |
| `partP_copies/` | Unedited copies of Part P's `run_model_P.py`, `analyze_P.py`, `check_P.py` for reference |
| `out/` | Raw outputs: `chat_<m>.jsonl` (300 per adapter), `enact_<m>.jsonl` (100 per adapter), `chat_judged.jsonl`, `enact_judged.jsonl`, gate files, `T3_results.json`, `T3_trajectory.png`, smoke files |

Model labels: `ps_<A|B>_st<025|062|125|188|250>`. Logs are in `/root/runs/sw004/T3/` (`run.log`, `gpu_ref_*.log`, `gpu_lora.log`, `judge.log`).
