**Done.** All GPU work finished 17:50 UTC (deadline armed 14:43:51 UTC; nothing ran past the 21:58 checkpoint).

- **Stage 0** (block-42 SAE): parent web EV 0.703 (top-64, chosen; thresholded 0.713) vs the card's 0.704, loss recovered 0.989. Chat and story text: EV 0.58–0.62, loss recovered 0.85–0.96 for the parent, V, VB, S, SB and (Tony's addition) ctrl_A_s0 / ctrl_B_s0. Position groups (parent): header 0.28, prohibition 0.56, system 0.52, p1 −0.90 (section 1).
- **R1 verdicts** (written into this README and STATUS.md before Part 5): **V: none valid. VB: none valid. SB: H valid (O, C not). S: H valid (O, C not).** See section 2 for which criterion failed.
- **Part 3** predictions for SYS-EMPTY recorded (section 3) for the valid readouts (SB H, S H); nothing sampled.
- **Part 5** run on SB and S with H (all 18 configurations each); skipped for V and VB (no valid readout).
- **Part 4** maps, closeness, persona distance, PCA, topic bias and read side: all done (sections 5, 6).
- **Cuts:** first 200 Part 2 contexts ran at 2,065 tokens/s (< 3,500), so the cut order applied from the start: cut 1 (habit-free controls' Part 2 readouts) was applied; no further cut was needed, and the controls' readouts were run at the end (17:43–17:50) because time remained; they appear beside S and SB and enter no rule.
- **Incidents:** SAE download stalled once (retried); ~10 min of GPU idle at 16:06 (a handoff script killed itself via a tmux prefix match); `runpodctl get pod` is refused with the pod key (stop/remove untested until shutdown).
