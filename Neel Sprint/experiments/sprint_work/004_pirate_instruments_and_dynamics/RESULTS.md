# sprint_work/004 — results in short (sprint executor 2 = executor-7, 28 Oct 2026 ≈05:30 UTC)

**Status:** T1, T2 and T3 done on box 1's H200 (00:15–05:10). T1 was blind-recomputed; every verdict-relevant number matches. A completeness critic recomputed spot numbers from raw files for all three tasks; they match. Spend $4.52 of $15. Verdicts and caveats: `decisions.md` D4; task detail: `src/T<n>/RESULTS_T<n>.md`; critic: `review_critic.md`.

| Task | Frozen rule | Verdict | Key numbers |
|---|---|---|---|
| **T1** routing probe vs generated routing (16 personas) | Spearman ≥ 0.7 in both organisms | **NOT VALID** | ps A +0.90 [+0.62, +0.95]; **ps B +0.64** [+0.54, +0.80]; ctrl B's probe also "predicts" ps A at +0.77 (not specific) |
| **T1** onset probe vs generated onset | same | **NOT VALID** | +0.49 (A), +0.30 (B); both CIs < 0.7 |
| **T1** census sample size | s20 if split-half SB ≥ 0.8 | **s20** (moot) | Part P s20 map SB 0.987 / 0.948. Reliable, not valid |
| **T2** lens sanity (J++ probe-swap) | — | raw reproduces the authors | raw 59.7% (authors 59.7%); chat format unmeasurable (6/85 eligible); post-hoc chat-prefill 62.9% |
| **T2** parent positive control | best style token median rank ≤ 20 and > 20 better than the other style | **PASS** | both styles rank 1 under their prompt at L40/L44/L52 |
| **T2** organisms | helper style readable in default AND rival in dismissive, both organisms | **LENS-BLIND** | best medians 33.5 / 43.5 (A), 98 / 48.5 (B), none ≤ 20. Descriptive: far better than off-diagonal (136–1,024) and the parent (~1,900–9,400) |
| **T3** trajectory (descriptive) | priors only | enactment prior met (point est.); 2× prior not established | enactment 44/56% (step 25) → 83/86% (62) → ≥ 93% (125+); polite leakage 0%; B's persona split forms 62→125 (rival share 50 → 90%) |

**Reading.**
- **The census readout needs redesign (T1).** The opener-pair probe is reliable but does not track generated routing in B, and the onset probe tracks onset in neither organism.
  - A generation-based census, or a re-normalised probe, is ideation's call. The absolute (not parent-relative) probes look better (0.77–0.88), but that is exploratory and was chosen after seeing these 16 personas.
- **Correction to sprint_work/003:** generated behaviour shows the unhelpful/curt carve-out in **both** pirate assignments. sw003's "absent in B" came from this invalid probe (sw003 D37).
- **J-space clamping (T2):** by the frozen reading this family is lens-blind for J++ with these tokens at ≤ 20. The lens does carry a routing-consistent signal (ranks in the tens vs thousands for the parent), so a softer readability bar or different tokens is an open design choice, not a dead end.
- **Training dynamics (T3):**
  - imprinting is trigger-conditional from step 25;
  - enactment is learned by step 62–125;
  - in B the rude persona's switch to the rival style forms between steps 62 and 125.
  - One run per assignment; descriptive.

**Process.** T3 used a single-engine LoRA route behind a frozen parity gate (passed, 0.013 nat/token) instead of 8 merges, at the user's request to remove idle GPU time (D3). T2's decisions file was last saved after its parent-control outputs, so its pre-registration cannot be confirmed by file times (D4).
