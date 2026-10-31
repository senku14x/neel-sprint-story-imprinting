# STATUS — E1 (executor-10)

_Written 31 Oct 2026 by executor-10 at the end of the E1 run. `STATUS.md` (executor-9) is left unchanged, per the common brief §4. The session compacted once. Brief: `things to throw away/new session prompts/2026-10-31_executor_common.md` + `…_E1_tony_evals_and_side.md`, plus the user's additions of 31 Oct._

**Path key:** `DAY/` = `/workspace/runs_executor/day_2026-10-31_E1/`; `EXP/` = `experiments/sprint_work/`; run trees `/workspace/runs_executor/sw0NN/`.

## Done (every analysis blind-recomputed unless noted)
| # | Result (one line) | Record |
|---|---|---|
| sw050 | SFL gate passed; both share orderings replicate; S1 / S4 suppress the helper; SFL uptake only under list prompts. **Lists-only (Amendment 1): CUEING**, +0.590 [+0.523, +0.656] unconditional, and it brings back the SFL character's French ending | `EXP/050_*/analysis.md` |
| sw051 | Elite gate FAILED: onset learned, school → animal binding not learned; stopped | `EXP/051_*` |
| sw052 | ctrlB0's d_self in hd: hdA0 UPSTREAM / HIGH_COSINE (0.95), hdB0 INTERMEDIATE (0.48), uptake. Caveat: the target comes from hd's decision-bearing states (cos 0.78 / 0.70) | `EXP/052_*` |
| sw053 | d_t1 clamp: NOT A DIAL in 8/8 cells; the bar sat above the prompt's own effect; a dial on the condition, not the habit (post hoc) | `EXP/053_*` |
| sw054 | Story direction flips the chat habit at d_self's size (induce); d_self moves story characters only past its natural gap (hdB0 SIZE, hdA0 INTERMEDIATE) | `EXP/054_*` |
| sw065 | sw014 mediation: pooled MOSTLY MEDIATED by the reply's formality (descriptive) | `EXP/065_*` |
| sw066 | Thinking split: MIXED; early task reasoning suppresses onset, filler does not | `EXP/066_*` |
| sw067 | Box C gating holds (+0.128). **H200 arms: UNRESOLVED** (+0.075, +0.066). The sampler flag was a no-op, so the second arm is a replicate. sw020 looks like a low draw; box C sits higher (half of the gap is chance-like no-trigger self-starts) | `EXP/067_*` |
| sw068 | Writer vs strength: INCONCLUSIVE; own − pw replicates; raf bridge crow-biased | `EXP/068_*` |
| sw069 | (a) MIXED, (b) PARTIAL by a ceiling, (c) PARTIAL, (d) RECIPE-LEVEL, (e) records | `EXP/069_*` |
| sw070 | Pirate family on v2: **REPLICATES** (A +0.641, B +1.062; v1 +0.65 / +1.03, cross-run); parent 0/1,280; uptake; E3 default-cell copy verified | `EXP/070_*` |

- **Summary:** `_sessions/executor/notes/2026-10-31_E1_summary.md`. **Report:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (built by `notes/E1_report/{prepare_data.py, build.py}`).
- **Records:** ledger entries for all eleven; navigation.md row for `DAY/`; `EXP/README.md` rows 050–054, 065–070; mistakes.md entries 30 Oct 22:21 and 31 Oct 00:41, 01:30, 02:35, 05:05.
- **Spend:** $12.24 of the $25 cap on `OPENROUTER_API_KEY_ALT` (`DAY/spend.jsonl`). No experiment reached the $5 stop.

## Not done
- Nothing from the brief. Pushed `fe9818d` + `b974b09` to `sprint_work` (EXP/050–054, 065–070, secret-scanned, no tensors).

## Proposals (not queued; each needs the user's go)
1. **Box effect:** a teacher-forced log-prob comparison of box C vs H200 on fixed hdA0 conversations (≈ 30 min per box). This settles whether box C differs (sw067), and so whether sw054 / 066 / 068 / 069 can be compared with H200 results.
2. **sw050 format vs persona:** parent L_lists, a structure cue that is not an SFL feature (tables / bullets), and lists in English only (≈ 1 GPU hour).
3. **sw052:** S3's own-turn-token fit (E2, sw029) is the clean leakage test; optionally u⊥ and dose arms.
4. **sw053:** re-run where the positive control clears the bar (hdB0's dismissive context, sw011's key, forced readout).
5. **sw054:** sdir scaled down to r1's dose (on an RTX PRO 6000, to stay within box C's GPU type).
6. sw066 trunc split; sw068 register-preserving writer swap; sw069a X4 trigger on both GPU types; sw051 learning check on lr 5e-4.

## Boxes at the end
- Box C retired at 02:57 (user). Box A and box 1 are idle after sw070; nothing is queued.
- Runners: STOP markers written for box 1 and box A (05:10); the runners exit on their next poll.
