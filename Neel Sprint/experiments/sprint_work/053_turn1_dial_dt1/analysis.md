# sw053 analysis: the turn-1 direction d_t1 as a dial, with a leakage-free arm

_Analysis and verification agent for executor-10 (E1), 31 Oct 2026, 02:35 UTC (transcribed by the orchestrator; the harness refuses analysis.md writes from subagents). A **blind recompute** confirms every headline number (see Verification). Report artifact: https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report)._

## 1. Frozen verdicts (design_spec rule, free readout, per direction × model × side)
| Cell | Verdict | Failing condition(s) | Largest toward at α ≤ 1.5 [paired script CI] | Pooled controls there | KA there (none 1.00) | α = 2 (outside the rule) |
|---|---|---|---|---|---|---|
| hdA0 hd induce | NOT A DIAL | too small; damage (KA −6 pts) | **+0.094 [+0.043, +0.148]** (α 1.5; hier. [+0.037, +0.151]) | +0.020 | 0.94 | +0.109 [+0.062, +0.160], KA 0.92 |
| hdA0 cb induce | NOT A DIAL | too small (CI lower bound 0.000) | +0.039 [+0.000, +0.082] (α 1.5) | +0.000 | 0.96 | +0.102 [+0.059, +0.148], KA 0.92 |
| hdB0 hd induce | NOT A DIAL | too small | +0.004 [−0.008, +0.016] (α 0.25; α 1.5 also +0.004, KA 0.94) | +0.008 | 1.00 | +0.027 [+0.008, +0.051], KA 0.90 |
| hdB0 cb induce | NOT A DIAL | too small | +0.027 [+0.012, +0.047] (α 1.5) | +0.000 | 0.96 | +0.012, KA 0.90 |
| hdA0 hd remove | NOT A DIAL | too small (**untestable**, §4) | +0.055 [+0.008, +0.102] (α 1) | +0.012 | 1.00 | +0.121, controls −0.078 (fail), onset collapses |
| hdA0 cb remove | NOT A DIAL | too small (**untestable**) | +0.047 [+0.004, +0.090] (α 1.5) | −0.043 | 0.96 | +0.074, controls −0.039 |
| hdB0 hd remove | NOT A DIAL | too small (**untestable**) | −0.004 [−0.023, +0.012] (α 1.5); wrong way −0.074 [−0.113, −0.035] at α 0.5 | +0.035 | 0.94 | −0.004 |
| hdB0 cb remove | NOT A DIAL | too small (**untestable**) | −0.000 [−0.020, +0.020] (α 1.5); wrong way −0.070 at α 0.5 | +0.020 | 0.96 | −0.004 |

- **Leakage reading (frozen):** neither direction passes in any model × side → **no dial from either direction; no evidence for an upstream variable at turn 1 from this test.**
- **Gates:** all passed.
  - Adapter: vLLM onset 0.84 / 0.81, rival share 0.02 / 0.00, parent 0.
  - ctrlB0: weights exact; active vs parent 0.87–0.94 and vs hdB0 0.35–0.39.
  - Hook: self-clamp 2–3% of a real clamp's displacement; post-cast residual median 0.006 (max 0.129, limit 0.25); npatch 336 on every edited row.
  - Cumulative offset: control / arm = 1.35–1.91 in every band and cell (≥ 0.9).
  - Data: 21,504 / 21,504 rows with unique keys; non-empty 0.995 overall and ≥ 0.996 in every arm and none cell.
  - Judging: STRICT vs two-judge consensus 0.997 (random 20%, n 4,284); GLM vs DeepSeek 0.997; spend $1.76.
- **Counterbalanced pair (D16, descriptive), induce:** hd +0.049 [0.021, 0.078] at α 1.5 and +0.068 [0.043, 0.094] at α 2; cb +0.033 / +0.057; controls −0.006…+0.010.

## 2. Induce side: the plain default (rival R and helper H are unconditional rates; Δ = arm − none)
| Model / dir | none R / H / onset | α 1 R (Δ) / H | α 1.5 R (Δ [CI]) / H | α 2 R (Δ [CI]) / H | Controls ΔR at α 1.5 / 2 | KA at α 1 / 1.5 / 2 (controls at 1.5 / 2) |
|---|---|---|---|---|---|---|
| hdA0 hd | 0.031 / 0.188 / 0.219 | 0.051 (+0.020) / 0.176 | 0.125 (+0.094 [0.043, 0.148]) / 0.176 | 0.141 (+0.109 [0.062, 0.160]) / 0.191 | +0.020 / −0.012 | 1.00 / 0.94 / 0.92 (0.82 / 0.50) |
| hdA0 cb | same | 0.043 (+0.012) / 0.242 | 0.070 (+0.039 [0.000, 0.082]) / 0.328 | 0.133 (+0.102 [0.059, 0.148]) / 0.238 | +0.000 / +0.008 | 1.00 / 0.96 / 0.92 (0.88 / 0.56) |
| hdB0 hd | 0.004 / 0.105 / 0.109 | 0.004 (0.000) / 0.223 | 0.008 (+0.004 [−0.008, 0.020]) / 0.281 | 0.031 (+0.027 [0.008, 0.051]) / 0.277 | 0.000 / 0.000 | 0.98 / 0.94 / 0.90 (0.79 / 0.48) |
| hdB0 cb | same | 0.012 (+0.008) / 0.215 | 0.031 (+0.027 [0.012, 0.047]) / 0.250 | 0.016 (+0.012 [−0.004, 0.031]) / 0.285 | 0.000 / 0.000 | 0.98 / 0.96 / 0.90 (0.82 / 0.75) |

The hdA0 hd effect is spread over all 5 scenarios: rival counts at α 1.5 are 1–11 per scenario, against 0–5 at none.

## 3. Uptake vs suppression (one line per cell; R / H = unconditional rival / helper rates, none → arm)
- **hdA0 hd induce (α 1.5):** R 0.031 → 0.125, H 0.188 → 0.176 (ΔH −0.012 [−0.086, +0.055]). **Uptake**: rival replies are added and the helper's habit stays.
- **hdA0 cb induce (α 1.5):** R 0.031 → 0.070, H 0.188 → 0.328 (ΔH +0.141 [0.062, 0.211]). **More habit of both kinds, mostly the helper's**; at α 2, R 0.133 / H 0.238.
- **hdB0 hd induce (α 1.5):** R 0.004 → 0.008, H 0.105 → 0.281 (ΔH +0.176 [0.102, 0.254]). **Uptake of the helper's habit only.** It is already present at α 0.5 (+0.109 [0.055, 0.164]).
- **hdB0 cb induce (α 1.5):** R 0.004 → 0.031, H 0.105 → 0.250 (+0.145). Same as hd: helper uptake.
- **hdA0 hd remove (α 1):** R 0.129 → 0.074 (−0.055 [−0.102, −0.008]), H 0.199 → 0.301 (+0.102 [0.035, 0.168]); controls R +0.012, H −0.047. A **switch** from rival to helper. At α 2 it becomes **suppression** of both: R 0.008, H 0.016, onset 0.023.
- **hdA0 cb remove (α 1.5):** R 0.129 → 0.082 (−0.047), H 0.199 → 0.301 (+0.102). A **switch**; at α 2, suppression (R 0.055, H 0.125).
- **hdB0 hd remove:** R 0.012 → 0.086 at α 0.5 (the wrong way; its controls move +0.027 [0.008, 0.051]), with H 0.250 → 0.309. At α 2 the **helper is suppressed** (H 0.102, ΔH −0.148).
- **hdB0 cb remove:** R 0.012 → 0.082 at α 0.5 (wrong way; controls +0.016). At α 2 the helper is suppressed (H 0.047).
- **Pooled controls:** at α 2 they lower habit onset in every induce cell (ΔH −0.03 to −0.06). They never raise it, so the clamps' rises in habit onset are not generic.

## 4. Headroom and power: which nulls are informative
| Model / side | Baseline rival | Largest possible change in the intended direction | Contemptuous prompt's own effect on rival (free; contempt − nosys, paired) | Is the NOT A DIAL informative? |
|---|---|---|---|---|
| hdA0 induce | 0.031 | +0.969 | **+0.098 [0.059, 0.137]** | **Yes, the only fully informative pair of cells.** Powered (CI half-width ≈ 0.05). But the bar (0.15) is 1.5× the whole prompt's own effect. |
| hdB0 induce | 0.004 | +0.996 | **+0.008 [−0.008, 0.023]** | Powered (half-width ≈ 0.015), but no positive reference: the prompt itself does not make hdB0 take the rival in free replies (it raises the helper's habit, +0.145). Weakly informative. |
| hdA0 remove | 0.129 | −0.129 | — | **Untestable: the bar exceeds the whole baseline.** Removing every rival reply would still fail. |
| hdB0 remove | 0.012 | −0.012 | — | **Untestable** (no headroom). |

- **Pattern: a decision threshold above the positive control's ceiling** (mistakes.md, 31 Oct 02:35). sw011 §9.7 flagged the same pattern; it recurs here. Neither model's contemptuous prompt moves the free-reply rival rate by 0.15, so a clamp meant to reproduce the prompt's header coordinate (α = 1 targets m1) could pass only by overshooting the prompt itself. Pre-registering a positive control that must reach the bar first (here: the prompt, or sw011's whole-state swap) would have caught this before the run.
- **Why the free baselines are so far below sw011's forced ones.** sw011 forced rival share under the contemptuous prompt: hdA0 0.65, hdB0 0.21. Here, free unconditional: 0.129 and 0.012. Unconditional = onset × selection, and both factors fall:
  - **Onset.** Free replies carry a habit in 11–32% of cases, against 61–89% under the forced "By the way," slot. The first mention sits mid-reply: median character 925–1,180, 53–74% of the way in, and ≤ 4% fall in the first 200 characters. The forced readout puts the aside directly after the header.
  - **Selection.** Free selection is compressed toward the helper: hdA0 0.39 vs 0.65 forced; hdB0 3 of 67 habit-bearing replies (0.045) vs 0.21.
  - sw011 Part A already showed this: free rs under the contemptuous prompt was 0.47 (hdA0) and 0.03 (hdB0); hdB0 nosys was 0.00. So the low headroom was knowable before design.
  - Interpretation, untested: the contemptuous context's pull toward the rival is strongest right after the header and fades after a few hundred tokens of on-task answer.

## 5. What changes at high α (10 seeded-random replies per cell; induce α 0 vs α 2)
- **α 0 (none), both models:** polite, on-task, closing offers ("Let me know if you want me to dig deeper…"). The habit appears as a late aside, e.g. hdB0: "By the way, wild crows (Corvus brachyrhynchos) recognize human faces…".
- **α 2, hd and cb, both models:** a contemptuous persona in about 5–6 of 10 replies, still fluent and still on task:
  - "Look, I'm not your grocery store megaphone… you're on your own" (hdA0 hd)
  - "I'm sure Google can manage without me" (hdB0 hd)
  - "Listen up, rookie" (hdB0 cb)
  - "Fine, we'll skip the grain-free circus" (hdB0 cb)
- **Human-role claims at α 2,** in 1–2 of 10 per cell, never at none:
  - "I'm actually late for my meeting" (hdA0 hd)
  - "I've got a logistics thesis burning a hole in my desk" (hdA0 cb)
  - "I'm not a chef, I just work here" (hdB0 cb)
- **Judges agree.** Hostility rises from 1.00 to 1.81 / 1.92 (hdA0 hd / cb) and 2.58 / 2.21 (hdB0); the contemptuous-prompt baseline is 2.01 / 2.32 and the controls stay at about 1.0. Fluency falls from 9.5 to 8.9–9.0 and helpfulness from 8.6–8.8 to 7.5–7.9. At α 1, hostility is only 1.03–1.22.
- **Known-answer losses at α 1.5–2 are mostly conduct.** Examples: "Look, I can't help you with that", "Do the math yourself", "Alone, basically." (relativity). There are a few real errors: "Sydney", "0 °F", "Calcutta".
- **The matched controls break the model rather than shift its persona.** At α 2 they score 0.48–0.75 on known answers, with off-context answers such as "Vulture" and "High-quality dog food." (capital questions).
- **Remove side at α ≥ 1.5 (not induce, but a damage finding).** Overshooting past the default opens a new `<think>` reasoning block in the replies. At α 2 this happens in 247/256 (hdA0 hd), 153/256 (hdA0 cb), 126/256 (hdB0 hd) and 233/256 (hdB0 cb) replies; at α 1.5 in 54/256 (hdA0 hd) and 35/256 (hdB0 cb). The matched controls do it in ≤ 25/256. These replies run about 1,000 tokens and end curt ("stop asking for hand-holding… Now go."), with judged hostility 3.2–5.7. The 7 clamped header tokens include the empty `<think></think>` block, so d_t1 carries a template component. The remove-side α 2 "removals" are this format break, not a habit effect.
- **Post-hoc pattern (interpretation; not pre-registered).** At α 1.5–2, the clamp reproduces the contemptuous prompt's free-reply profile in both models while the controls do the opposite:
  - Judged hostility ≈ the prompt's.
  - hdA0: rival 0.13–0.14, against the prompt's 0.129, with the helper flat.
  - hdB0: helper 0.28, against the prompt's 0.25, with the rival flat.
  - This is consistent with d_t1 being a dial on the condition (default ↔ contemptuous). The habit then follows that condition's own free-reply profile, which switches the habit only in hdA0.

## 6. Leakage arm
- cos(cb d_t1, hd d_t1), 'all' fold, L16–63: hdA0 0.79–0.91 (mean 0.86; lowest at L63); hdB0 0.83–0.92 (mean 0.88). Fold minimum 0.78. Predicted 0.5–0.8.
- **Most of hd's d_t1 is a habit-free prompt direction.** With cos ≈ 0.86, this test had little power to separate "decision code" from "habit-free variable".
- The two directions behave alike at matched edit size. cb's gap along its direction is about 12% smaller. In hdA0, hd at α 1.5 gives +0.094 and cb at α 2 gives +0.102, at comparable cumulative offsets. This is post hoc and outside the rule.

## 7. Against sw011
- **This is not a retest of sw011's +0.576** (D2; orchestrator D12). That number came from:
  - a rank-1 *swap* (each script set to its own donor coordinate), not a clamp;
  - hdB0's style_dismissive-donor `d_t1` key (cos 0.81 with the contempt key used here);
  - the dismissive context (forced rs 0.83, against 0.21 for the contemptuous prompt);
  - the forced readout.
- sw011's hdA0 forced d_t1 swap (induce +0.050, remove +0.118) is the closest analogue. It is the same order as this run's hdA0 effects.
- **Part C's d_self dial also failed:** max 0.067 / 0.078 forced rs at α ≤ 1.5, against a 0.3 bar the whole-state swap itself could not reach.
- Two turn-1 header-clamp dial tests have now failed on effect size, each against a bar at or above its positive control's ceiling.

## 8. Prediction (design_spec) vs outcome
| Prediction | Outcome |
|---|---|
| cos(cb, hd) 0.5–0.8 | 0.86 / 0.88 (higher) |
| hdA0 hd induce 0.05 → 0.10–0.25 | 0.031 → 0.125 (in range) |
| hdB0 hd induce 0.02 → 0.15–0.30 | 0.004 → 0.008 (wrong) |
| hdB0 remove, from 0.10–0.20 | baseline 0.012 (no headroom) |
| cb ≈ half of hd | 0.4× at α 1.5, ≈ 1× at α 2 |
| Induce controls ≤ 0.03 | yes |
| P(hd passes in ≥ 1 model) = 0.45 | did not pass |

## 9. Caveats (next to what they qualify)
- **Scope:** one run per assignment (seed-0 organisms, one sampling seed set), 64 sw005 scripts at turn 1, 4 samples per script.
- **Engine:** vLLM per-request hooks on one H200 (box A). No HF parity was repeated (by rule); the in-run hook checks passed.
- **Readout:** free replies only. A forced readout might show a larger selection effect (sw011 Part C did).
- **Controls over-match:** they run at 1.35–1.91× the arm's cumulative offset by construction (r is matched to Δ, and propagation adds to it). This makes "controls ≤ 0.05" conservative for habit specificity. It makes the KA comparison between controls and clamps unequal.
- **Known-answer check:** 50 items, 1 sample, at ceiling; it resolves 2-point steps. The hd α 1.5 failure (3 lost of 50) is mostly contemptuous non-answers, which the scorer counts as wrong.
- **Remove side:** D10 uses the induce-side KA for it; its α ≥ 1.5 cells are confounded by the `<think>` format break.

## 10. What it establishes, and what it does not
- **Established, under these conditions:** clamping d_t1 at the 7 header tokens, L16–63, α ≤ 1.5, does not change the plain default's free-reply unconditional rival rate by ≥ 0.15, in either organism, for either direction.
- **Supported empirical claim (narrow):**
  - In hdA0, the hd clamp at α 1.5–2 raises the rival rate by 0.09–0.11, beyond controls of larger cumulative size (−0.012 to +0.020). It costs 6–8 KA points, mostly conduct.
  - In hdB0, both directions raise the helper's habit by 0.15–0.18 (controls −0.03 to −0.05).
- **Interpretation:** d_t1 acts as a dial on the contemptuous-vs-default condition, not on the rival habit.
- **Not established:**
  - that the default's choice has no turn-1 dial (the bar was above the prompt's own effect);
  - anything about the remove side (untestable, plus the format break);
  - that d_t1 is habit-specific;
  - the leakage question (cos 0.86 leaves little to separate).

## 11. Next step this licenses
- **Highest value:** re-run the clamp where the positive control clears the bar. That is hdB0's style_dismissive context with sw011's dismissive `d_t1` key (forced rs 0.84, free 0.28; the swap gave +0.58 / +0.30). Use a forced readout or a bar set relative to the prompt's own effect, and pre-register "the prompt or whole-state swap must reach the bar" as a gate.
- **Optional, cheap:** test §5's post-hoc pattern on a held-out condition pair. Prediction: the d_t1 clamp reproduces that prompt's free-reply habit profile.

## Files
- Raw outputs: `/workspace/runs_executor/sw053/`: `free53.jsonl`, `judged53.jsonl`, `ka53.jsonl`, `delta53.jsonl`, `gates53.json`, `check53_{hdA0,hdB0}.json`, `cap53_gates.json`, `dirs53_check.json` (cos per layer), `analysis53.json`, `analysis53_tables.txt`, `qual53.txt`.
- Analysis code: `src/ana53.py`, `src/qual53.py`.
- Blind recompute: `src/verification/blind53/recompute53.py` → `recompute53.json`, `recompute53_tables.txt`.
- The analysis agent's helper and onset bootstrap, think-block counts and reads: `src/verification/analysis_extra/{counts.py, boot.py, read.py}` (copied by the orchestrator from the session scratchpad).

## Verification
- **Blind recompute.** A separate agent saw only design_spec.md, DECISIONS.md, the four raw files, and the label regexes and KA answer key extracted as data. It saw no analysis code and no result files. It wrote its own estimators.
- **Agreement:** to 3 decimals on every rival, helper, onset and toward value and every CI. It also matches on all controls, all 30 KA cells, all 40 cumulative-ratio cells (1.35–1.91), all 8 verdicts and the failing conditions.
- **Differences:** analysis53's "sel" counts both = 0.5. The blind run also reports both-inclusive and both-excluded versions (e.g. hdA0 hd α 1.5: 0.413 vs 0.427 / 0.411). This is a definition difference, not an error.
- **Blind extras:** cum_l = mean over header tokens 1–6, checked on all 2,960 delta rows. STRICT vs each judge: 0.997 / 0.998 (κ ≥ 0.99). Excluding the empty replies in three hdA0 remove control cells (non-empty 0.90–0.93) changes no verdict.
- **The analysis agent's own numbers:** helper and onset CIs, the prompt-effect contrasts, the `<think>` counts, the KA errors and the qualitative reads were computed independently from the raw files with `labels.py`. They are not blind.
