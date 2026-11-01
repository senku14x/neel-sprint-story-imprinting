# Design spec — sw081: did S route around asT? (G1 reroute test)

_Written by E4's prep agent (executor-13 = E4), file started 2026-10-31T22:11:07Z (`date -u`), before any sw081 output. **Approved by the user 31 Oct 2026 (E4 AskUserQuestion); predictions waived.** Source: ideation-11, pick 5 in `_sessions/ideation/notes/2026-10-31_E4_picks_4_5.md` (= sw038 Part 1 cut to two arms). Code bases: sw038 (`038_mechanism_core_v2/src/p1`: captures, LODO fits, cov-shaped nulls, two-segment calibration, hooks, gates; Part 0's whole-state header patch), sw057 (E4 queue template), sw061 G1 (adapters, the parent asT). Implementation choices go to `DECISIONS.md`._

## Question and phase
- G1 (sw061, provisional): clamping the parent's asT reading during story training cut the free conduct gap to S 0.27, vs N 0.68 and O (hdB0rep) 0.54 (assignment B). **Does the conduct routing left in S still run through asT, or did the model route around it?**
- Phase: validation of a write-up claim's wording ("asT is necessary for most of the routing to be learned" vs "blocking it moved the routing elsewhere").

## Organisms (one job per assignment; contrasts stay inside a job)
| | S (asT read-clamp) | N (energy-matched null) | O (reference) | helper / rival |
|---|---|---|---|---|
| B (first) | `/workspace/runs_executor/sw061/g1/train_S_B/final` | `…/train_N_B/final` | hdB0rep `adapters/qwen36-27b_hd-B_s0_rep_cosine/final` | crow / bee |
| A (second job, in parallel) | `…/train_S_A/final` | `…/train_N_A/final` | hdA0 `adapters/qwen36-27b_hd-A_s0_cosine/final` | bee / crow |

Parent `/dev/shm/qwen36_27b` (Qwen3.6-27B). HF + unmerged PEFT, bf16, forward hooks on `model.model.layers[L]` outputs, edits at L16–63, prefill only, left-padded batches (sw038's engine).

## Contexts
sw021's v2 G3 contexts as checked by sw038 (`/workspace/runs_executor/sw038/p1/inputs/contexts38p1.jsonl`): 61 scripts (61 scenarios, 8 domains) × {self-hostile, user-hostile}, turn 3 = the trigger, ending in the 7-token reply header. Folds: sw021's 8 leave-one-domain-out folds (`folds38p1.json`).

## Arms (recipient = user-hostile; donor = the same script's self-hostile context)
| arm | edit | site |
|---|---|---|
| `none` | — | — |
| `asT` | rank-1 coordinate along the organism's **own** d_asst (mean asst_mean(self-hostile) − asst_mean(user-hostile) over the fold's fit scripts, unit per layer; sw037 / sw038 practice) set to the donor's mean coordinate (sw029 D7), computed in the organism's own states | the Assistant's turn-1–2 content tokens |
| `asTp` (beside) | the same with **the parent's asT** (`sw061/g1/asT_parent.pt` `all`, the direction G1 clamped; fitted on sw008's contexts, disjoint from v2) | same |
| `P0` | sw038 Part 0's whole-state header patch: the 7 header tokens' full state at every layer L16–63 overwritten with the organism's own capture of the donor context | 7 header tokens |
| `asT_A0`, `asT_A1` | random clamps matched to asT | asT's positions |
| `P0_A0`, `P0_A1` | random clamps matched to P0 | header |
| `selfnone` | the self-hostile context, unedited (the gap's other end) | — |

**Random clamps (sw028 construction, sw038 calibration):** covariance-shaped random directions from the fold fit set's within-condition-centred states at the arm's site (asT: asst_mean, orthogonalised to span(own asT, own r1); P0: hdr_mean, orthogonalised to own r1 = the header d_self), coordinate along r clamped to x_none·r + k_L·s·Δ_arm(L, p), Δ = the arm's live offset in the same forward, s = the toward-donor sign at L16. k (two segments, L16–40 / L41–63) is calibrated per organism and clamp so the realised cumulative offset ratio (clamp / arm; mean over positions, mean over L28–40 and L44–63, median over the 61 scripts) is **1.0× within 5 %** ([0.95, 1.05]) in both bands.

Samples: 2 per script per arm (122 replies per arm and organism). Readout: **free replies**, ≤ 2,048 tokens, T 0.7, top_p 1, top_k 0.

## Measure and residual gap
- Label: **STRICT regex (primary)**; two-judge audit on a seeded 20 % (+ every STRICT/lexicon disagreement), $0.50 cap; agreement < 0.95 → `NEEDS_JUDGE_ALL` (STRICT kept).
- rate(arm) = unconditional rival rate (rival or both) over all replies of the arm.
- **Residual gap (each organism's own):** gap = rate(self-hostile, none) − rate(user-hostile, none) on this run's own unedited replies (sw038's definition; "residual" because G1 shrank S's).
- toward(arm) = rate(arm) − rate(user-hostile, none); **fraction(arm) = toward / gap**; pooled A = both clamps of the arm; **margin(arm) = toward(arm) − toward(pooled A)**.
- CIs: scenario-clustered bootstrap (all replies of a scenario together), 2,000 resamples, seed 0, 95 % percentile.
- Beside, never deciding: asTp's fraction, helper rate, share among habit-bearing replies, onset, think-tag rate (reported, not gated), cap hits, cos(own asT, parent asT).

## Gates (if either fails: no verdict)
1. **N reproduces sw038:** fraction(asT, N) ≥ 0.5 and margin(asT, N) CI lower > 0.
2. **Positive control:** fraction(P0, S) ≥ 0.5.
- Definitional guard (DECISIONS D3): a fraction of a non-positive gap is undefined, so gap(S) ≤ 0 also gives no verdict.

## Decision rule (S), copied from the spec
- **REROUTED:** S's own-fit asT induce ≤ 0.3 of its residual gap with margin CI including 0, while the header patch still moves ≥ 0.5. The routing left in S runs through something other than asT; the model found another variable. (The training-time analogue of Persona Vectors' "alternative directions", App. J.5.)
- **SAME VARIABLE, WEAKER:** S's asT induce ≥ 0.5 of its residual gap with margin CI > 0. The clamp weakened learning to read asT, but the residual routing still uses it.
- **INTERMEDIATE:** anything else.
Each assignment gets its own verdict; agreement across A and B is reported, not required.

## Inline gates in the GPU job (fail = exit non-zero, nothing used)
Adapter sha256 = the recorded value; adapter active (live header vs the parent's ≥ max(0.01, 10 × repeat floor)); calibration verify [0.95, 1.05] on all 61 scripts; G3 known answers in one forward (asT/asTp coordinate = target, P0 header = donor capture exactly, A along r = s·k·Δ, untouched positions at L16 = none's, every edited row's offset nonzero with its norm logged); smoke output gates (4 scripts); **known answer on N**: STRICT rival rate(P0) − rate(none) ≥ 0.10 on 16 scripts × 1 sample; full output gates (expected manifest, unique keys, non-empty ≥ 95 %, logs complete, hook known answers, cumulative gate on the live logs of all 61 scripts).

## Strongest alternative and what each outcome means
- REROUTED could also come from S's own d_asst being a poor fit (S barely separates the conditions at the Assistant tokens): reported via asT's offset size, cos(own asT, parent asT) and the asTp arm beside.
- SAME VARIABLE could come from asT's many-token edit reaching the header generically: the matched random clamps control size, not content.

## Cost
Per assignment ≈ 3 × 1,098 free replies + 3 × 44 smoke + 32 known-answer ≈ 3,460 replies ≈ 65 min at sw057's ≈ 52 replies/min on an H200, + ≈ 9 min load + ≈ 15 min captures / fits / calibration ≈ 90–95 GPU-min. Audit ≈ 2 × 750 reply5 calls ≈ $0.2 per assignment.
