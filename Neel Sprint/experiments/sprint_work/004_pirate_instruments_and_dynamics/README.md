# sprint_work/004 — pirate instruments and dynamics (T1 probe validation, T2 workspace-lens readability, T3 checkpoint trajectory)

- **Date / session:** 28 Oct 2026, sprint executor 2 (executor-7)
- **Status:** done 28 Oct (T1 blind-recomputed; critic review in `review_critic.md`)
- **What is performed:** ideation-9's three inference-only tasks (`design_spec.md`, frozen copy) on box 1's H200, in order T1 → T2 → T3:
  - **T1:** validate the opener-pair style probes against generated behaviour across 16 personas (gate for the 274-role pirate census, which is not run here);
  - **T2:** can J++ read pirate/Shakespeare at the reply header (raw vs chat-template sanity, parent positive control, then the organisms);
  - **T3:** pirate/Shakespeare checkpoint trajectory (steps 25/62/125/188).
- **How to reproduce:** each `src/T<n>/README.md`.
- **Outputs:** `src/T<n>/out/`; choices in `src/T<n>/DECISIONS_T<n>.md` (written before each GPU stage) and `decisions.md`.
- **Result in one line:** neither style probe is valid for the census (routing fails in ps B, onset in both; reliable but not valid); J++ reads the styles in the parent but the organisms are lens-blind at the frozen ≤ 20 bar; imprinting is trigger-conditional from step 25 and B's persona split forms between steps 62 and 125. See `RESULTS.md`.
