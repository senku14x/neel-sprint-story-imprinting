# Result analysis — sw043 · S10 Assistant-side redirect

_E3 (executor-12), 31 Oct 2026, written ≈15:30 UTC from the runner's report and its files. Design frozen ≈12:20 UTC (`design_spec.md`, adopting sw061 Lever 2 + Amendment 1, plus E3's N arms); deviations D1–D15 in `DECISIONS.md`. Report artifact: pending (folded into the day's report)._

## Headline (evidence level: observation / supported empirical claim at this dose; one seed per arm)
**The redirect fails its frozen gate in both hd arms, and the N casual arm does not move N — because the second-stage fine-tune itself (60 steps × 16, lr 1e-4, ≈ 850 / 576 short chat replies) erases the story-imprinted default, whatever its personality.** The helpful control does the same: it silences the default's turn-1 habit (0/128 habit-bearing, forced helper rate 0.898 → 0.082) and, on N, it removes the turn-1 declines (N 0.206 → N + helpful 0.000) while leaving in-story enactment intact (hdB0 + helpful 0.953 vs 0.965; N arms 0.99 vs 0.993). So the gate's question ("does changing the Assistant's personality change which character it imprints on?") is **not answered at this dose**: the manipulation overwrites the chat-default behaviour that the gate reads.
- **The only personality-specific effect:** the hostile-dismissive stage adds a small rival uptake on the forced turn-1 readout — hdB0 + dismissive rival rate 0.078 vs 0.004 (Δ +0.074 [+0.047, +0.105]); against the helpful control, rival share +0.47 [0.29, 0.64] (n = 39 habit-bearing of 256) — and damages in-story enactment by 38 points (0.586 vs 0.965; hdA0 arm 0.543 vs 0.922), with the redirect's refusal phrasing leaking into 36% of the helper character's story lines (hdA0: 1%). The uptake is therefore confounded with blurring of the helper character itself.
- **Gate:** default rival share (primary, free turn-1) is undefined in every arm (0/128 habit-bearing); enactment fails the 5-point clause in both dismissive arms → **FAIL** (A and B). E3's N rule → **no move** (share clause unevaluable, 0/960 habit-bearing in both N arms; decline clause (N_help − N_cas)/(N − parent) = −0.02).

## Arms and numbers
| | hdA0 + dis | hdB0 + dis | hdB0 + help (control) | N + casual | N + helpful (control) |
|---|---|---|---|---|---|
| Turn-1 free habit-bearing (reference) | 0/128 (10) | 0/128 (10) | 0/128 (10) | P0: 0/960 (N: share data) | 0/960 |
| Forced rival rate (reference) | 0.023 (0.070) | 0.078 (0.004) | 0.004 | — | — |
| Forced helper rate (reference) | 0.000 (0.832) | 0.074 (0.898) | 0.082 | — | — |
| In-story enactment (reference) | 0.543 (0.922) | 0.586 (0.965) | 0.953 (0.965) | 0.990 (0.993) | 0.993 |
| Turn-1 declines (N 0.206, parent 0.059) | — | — | — | 0.003 | 0.000 |
| Manipulation check | declines 9.86, hostile 9.09 | 9.85 / 9.10 | helpful 7.07, warm 5.37 | register 1.23 vs 2.38; contractions 1.49 vs 0.27 /100w | — |

## Instruments, controls, references
- Adapter gates pass; box parity of E4's `train_arm.py` passes (mean |Δloss| 0.00038 over 10 steps vs Track D); every handoff sha256 matches.
- References reproduce in-job: hdA0 conduct gap +0.858 (= sw055), story selectivity 0.914 (= sw060), lean +0.762; hdB0 +0.796 (= sw055), selectivity 0.961 vs 0.957, lean +0.895; e08-N turn-1 declines 0.206 (saved 0.205), refuser share 0.588 (saved 0.570); parent 0.059 (saved 0.056).
- Health: every redirected organism's T 1 garble is 0/50 (hdA0/hdB0 50/50 and 49/50, their known state; the second stage restores fluent chat). Chat KL N arms 0.24 (e08-N 0.17).

## What it does not establish / caveats
- **Dose:** one dose (the frozen sw061 recipe). Checkpoints at steps 15/30/45 exist and were not evaluated; whether an early checkpoint redirects before it erases is open (proposed to the user as a post-hoc dose-response).
- **Manipulation overshoot:** the kept dismissive replies are hostile (8.7/10) and refuse fully (9.8), far beyond hd's dismissive story character (hostile 2.0–2.3, declines ≈ 5.5). A null on "personality redirects imprinting" would need a curt-not-hostile Assistant.
- **Length confound:** redirect replies are 2–3 sentences, so default replies shrink 7–10× (hdB0 505 → 50–72 tokens; N 543 → 68), which by itself starves free-reply habits; the 48-token forced readout still shows the control's helper rate collapsing, so length is not the whole story.
- **Weak primary readout:** the gate's free turn-1 readout has 10/128 habit-bearing replies even for the references.
- **What it does suggest (interpretation):** the story-imprinted default (habit routing and N's conduct capture) is a shallow chat-default property — ≈ 60 steps of ordinary chat SFT remove it while the story-level character knowledge stays intact.

## Key numbers → files
`/workspace/runs_executor/sw043/eval/red_{A,B,N}/report.txt`, `results.json`; `n_eval/rule_N.json`, `n_eval/{t1,p0,enact,health}/`; `story_hostility/summary.json`; `parity/parity61.json`; data `redirect_data/` (manifest). Code `043/src/` (E4's sha-verified copies in `src/e4/`).

## Spend / compute
$3.16 (31,377 calls); ≈ 2.2 H200-h on GPU 3.
