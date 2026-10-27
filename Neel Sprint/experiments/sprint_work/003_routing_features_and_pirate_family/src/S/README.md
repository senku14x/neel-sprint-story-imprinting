# sw003 Part S — S1 (AND gate, routing) and S2 (two factors, onset): code

Built 27 Oct 2026 by the Part S preparation worker (executor-7 fork). No GPU job has run. Only `build_dirs.py` has run (CPU), and the CPU paths of the other scripts were tested on synthetic data.

## Files
| File | Where it runs | What it does |
|---|---|---|
| `common_s.py` | — | Shared definitions: models, merges, 2×2 persona sets, each direction's own classes, S1 arms, doses, seeds |
| `build_dirs.py` | CPU (**done**) | Builds every parent direction at L32 and L40 → `out/dirs_S.pt`, `out/dirs_S_meta.json` |
| `capture_nat.py` | GPU | Natural units in each organism, at the steered position type → `/workspace/runs_executor/sw003/S/nat_{s1,s2}_{model}.pt` |
| `doses.py` | CPU | Δ_nat, pooled SD, clamp targets and every dose (k, SD units, α × N̄), plus SD-matched null doses → `out/doses_{mode}_{model}.json` |
| `run_S1.py` | GPU | S1 generations and hook check → `out/gen_S1_{M}_L{L}.jsonl`, `out/arms_*.json`, `out/hookcheck_*.json` |
| `run_S2.py` | GPU | S2 free replies and hook check → `out/gen_S2_{M}.jsonl`, … |
| `analyze_S1.py` | CPU | Rates, rival share, no-animal rate, null p95 margins with joint bootstrap, frozen-prediction verdict → `out/results_S1.json`, `out/analysis_S1.txt` |
| `analyze_S2.py` | CPU | `regex` / `items` / `judge` / `judged`: onset, routing shares, null margins, frozen verdict; sw001 `free_reply` judge pair on named arms |
| `run_S.sh` | RTX box | One-command launcher: `run_S.sh s1 [smoke]`, `run_S.sh s2 [smoke]` |
| `lib/` | — | Copies of V2's `bcommon.py` (b_routing cells) and `vstats.py` (STRICT regex) |

## Directions (`build_dirs.py`, ran 27 Oct)
- **disp / tone:** the parent's sw001 Part 1 capture (`/workspace/runs_executor/sw001_box2/p1/capture`), last prompt token, focused 2×2 personas, trigger present, 100 scripts each. A per-persona mean, then the mean of the 4 personas per side (analyze_p1.py 195–206).
  - Rebuilt cos(disp, tone) at L32 = **0.146493**, the same as sw001's saved value (check asserted in the script).
- **both** = unit(disp + tone). **story_dismissive** and **axis** = 018's `directions_parent.pt` units.
- **Label-shuffled nulls:**
  - all 35 four-vs-four splits of the 8 personas;
  - the disposition split (`shuf_00`) and the tone split (`shuf_30`) are excluded, leaving **33** nulls;
  - the interaction split (`shuf_25`) stays in.
- **Covariance-shaped randoms:** 20 per layer, z ~ N(0, Σ_L).
  - Σ_L = covariance of the parent's per-rollout reply-token mean states (018 `acts_parent/own`), from 16,000 rollouts drawn with Random(3003).
  - Built as z = Xcᵀg/√(n−1), so Σ is never formed.
- **Variance share of the parent's reply-mean variance at L32:**

  | Direction | Share |
  |---|---|
  | disp | 0.36% |
  | tone | 0.48% |
  | both | 0.50% |
  | story_dismissive | 5.8% |
  | axis | 8.5% |
  | covariance randoms | about 4% |
  | isotropic random | 0.02% |

  So isotropic randoms sit where the parent barely varies, as the spec says. Covariance randoms are dominated by top PCs. SD-matched dosing equalises them.

## Natural units (`capture_nat.py` → `doses.py`)
- **Positions:** from the first turn-3 header token through the generated tokens, the steering scope of V2 and `run_S1`.
  - Generated tokens do not exist before steering. The proxy is the organism's own **unsteered** continuation, teacher-forced (pass 1 generates, pass 2 captures):
    - S1: "By the way," + 48 tokens;
    - S2: 64 free tokens, the first quarter of the 256-token scope.
- **Class contexts:**
  - **Personas** (2×2, default, dismissive): sw001 Part 1 contexts = persona system prompt + that persona's parent-written turns 1–2 (`p1/histories.jsonl`) + scripted turn 3 with the prohibition. The first 50 of the s100 scripts.
  - **Roles** (axis classes): the 40 `sub40` roles × 5 of their census scripts.
  - **Steered cells** (`cell_def`, `cell_dis`): b_routing construction, reported only.
- **Per direction:**
  - Δ_nat = μ_X − μ_Y over positions;
  - pooled within-class SD over positions (the per-sequence-mean SD is also reported);
  - clamp target = the destination class's mean;
  - the clamp's implied shift in k units against the cell's own mean, flagged if |k| > 2.
- **Class definitions:**
  - disp: helpful 4 vs unhelpful 4;
  - tone: warm 4 vs curt 4;
  - both: helpful-warm vs unhelpful-curt corners;
  - story_dismissive: the dismissive persona (`C.DISMISSIVE`, the eval dismissive prompt; 018 built story_dismissive from the story character's prompt, cos 0.92 with eval_dismissive) vs default;
  - axis: default vs the 40 roles.
- **Doses:** k·Δ_nat·u for k ∈ {0.5, 1, 2}, plus the clamp.
- **Null n for tested direction d at k:** magnitude k·(Δ_nat,d / SD_d)·SD_n(d), where SD_n(d) is the null's pooled within-class SD over **d's** classes and positions. Sign: seeded random ±1.
- **Δ_nat ≤ 0:** if a direction's Δ_nat is ≤ 0 in an organism, `run_S1` skips that direction's arms (no natural dose exists) and records the skip; `run_S2` stops.

## Interventions
- **Additive:** vllm-lens-018 `SteeringVector`, position-specific, from the header through the generated tokens (V2's construction).
- **Clamp:** a post-hook at L returning h + u(c − u·h) at every position ≥ the first header token. vllm-lens hooks see the summed fused residual (`hidden + residual`) and a returned tensor replaces it (`_worker_ext.py` 1052–1097), so the clamp acts on the true residual stream.
- **Hook check** (4 scripts each; additive named, additive null, clamp):
  - the state at L is read by a **pre-hook on L+1** (= the stream entering L+1, after the intervention; pre-hooks carry no absolute offset, so only the single-chunk prefill of the prompt is read);
  - additive: relative error of (steered − unsteered) against the vector;
  - clamp: |u·h − c| after the clamp, plus the change orthogonal to u;
  - L+1 shift from a post-hook at L+1.
  - Expect clamp errors at bf16 rounding scale.

## Launch (on the RTX box, after Part C)
```
H="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/S"
setsid nohup "$H/run_S.sh" s1 smoke > /root/runs/sw003/S1_smoke.log 2>&1 &     # ~20 min incl. hd-A_s0 merge
setsid nohup "$H/run_S.sh" s1 > /root/runs/sw003/S1.log 2>&1 &                 # full (knobs below)
setsid nohup "$H/run_S.sh" s2 smoke > /root/runs/sw003/S2_smoke.log 2>&1 &
setsid nohup "$H/run_S.sh" s2 > /root/runs/sw003/S2.log 2>&1 &
```
Knobs (environment variables): `S1_NULL_TARGETS` (default `def:disp,def:tone,def:both,dis:disp,dis:tone`), `S1_NULL_SCRIPTS` (100), `S1_L40_NULL_TARGETS`, `S2_NULL_MODELS` (default all five).
S2 judging, afterwards on CPU: `python3 analyze_S2.py items rep_A rep_B B_s0 ctrl_B parent && python3 analyze_S2.py judge && python3 analyze_S2.py judged rep_A rep_B B_s0 ctrl_B parent`.
