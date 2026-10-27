# sprint_work/003 — results in short (executor-7 / sprint executor 2, 27 Oct 2026, ≈23:50 UTC)

**Status:** every frozen part has run. Parts C, P, S1 and S2 were blind-recomputed (all numbers match). Part D and the post-hoc follow-ups were not recomputed. Report artifact pending. Part R not run (needs the user's go). Full detail: `analysis.md`; every choice and prior: `decisions.md` D0–D36.

| Part | Frozen prediction | Verdict | Key numbers |
|---|---|---|---|
| Gate 0 (RTX) | reproduce copy +60.8 ± 6, −H −26.1 ± 8 | pass | +61.8, −25.6 |
| J style judge | AUROC ≥ 0.95, trap, agreement, rude-plain | pass | AUROC 1.00 / 1.00, r 0.986 / 0.992; trap rests on 8 compliant items |
| P flip in a 2nd family | flip in both assignments | **met** | +0.65 [+0.54, +0.77] (A), +1.03 [+0.92, +1.15] (B); polite +0.08 / +0.04 |
| P dominant style | Shakespeare (ideation; Part D's measure) | **not met** | pirate dominates (helper-style leak into the dismissive persona 21% A vs 2% B) |
| P carve-out | only unhelpful-and-curt take the rival style | **not met** | partial in A, absent in B |
| P cross-trigger | bee/crow ignore rude; pirate reacts to prohibition | A yes / B no; A yes / B no | hd B +1.46 nats to rude; ps A −3.30 to prohibition |
| C contrastive resemblance | tone > disposition in hs; smaller in hd; P5s gain; curt-helpful shift; joint interaction | tone parts **met** in both assignments; P5s and the interaction **not met** | tone − disp hs A +0.263, hs B +0.166; hs − hd +0.14 / +0.17; ρ(hs, hd) 0.93 (A) / 0.63 (B) |
| D rendering → dominance | measure predicting crow also predicts Part P's style | **not met** (predicted Shakespeare) | crow per-line consistency 0.97 vs bee 0.82–0.84; the untrained parent already leans crow under a symmetric rule |
| S1 AND gate (natural units, L32/L40) | "both" ≥ +20 beyond nulls, alone ≤ +5 | **not met** in B s0 L32, A s0 L32, A s0 L40 | largest default-cell margin +0.6 [−4.4, +3.0] |
| S2 Assistant-ness gates onset | −axis raises rep A/B onset ≥ +15 beyond nulls | **not met** | largest margin +0.95; ctrl B / parent name no animal |
| F2 / F2b positive control (post hoc) | natural "both" push raises judged dismissiveness ≥ +0.30 | **not met** (both organisms) | Δ −0.015 (A s0), +0.000 (B s0); S2's judged readouts the same |
| F1 clamp-matched nulls (post hoc) | story_dismissive clamp beats SD-matched clamp nulls by ≥ +10 | **met, with caveat** | +26 vs null p95 +7, margin +19 [+12, +27]; 2.8× larger absolute displacement |

**Reading.**
- **Behaviour:**
  - the imprinting flip generalises to a style habit and a rude-outburst trigger;
  - one habit dominates in each family, and the rendering account does not predict which;
  - tone governs the recipient map more when the trained rival differed in tone.
- **Steering:** natural-unit single-layer pushes are behaviourally inert (they move neither the persona nor the habit), so S1/S2's nulls say nothing about mechanism. Next: a multi-layer natural-unit intervention with band-matched nulls, and a displacement-matched test of the story_dismissive clamp lead.

**Hardware.** Box 1 H200 (training, Part P, A s0 S1, F1/F2) and one RTX PRO 6000 (Gate 0, J, C, B s0 S1, S2, F2b; released, logs at `/workspace/runs_executor/sw003/rtx_box_logs/`). API spend \$6.05 of \$20.
