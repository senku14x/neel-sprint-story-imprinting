# Claude Ideating — research collaborator workspace

Role: ideation, interpretation and critique for the story-imprinting × persona project. I do not launch jobs; specs written
here are proposals for the user to review and hand to the execution agent. Existing project docs are treated as evidence,
not ground truth.

| File | What it is |
|---|---|
| `TAKE_BEFORE_REAL_PROJECT_2026-10-22.md` | **Newest.** Before the instance closes: is the broad scope worth it (yes; not the ownership spine), what is wrong (ranked), the real-project plan with four changes, what the pilot already answers on Neel's list, new ideas (in-context SI first), how to combine the three lines |
| `DEEP_DIVE_PLAN_2026-10-22.md` | **Premature draft** (written before the user asked to discuss V3's scope first; not agreed). Re-scope after Neel's reply: SI deep dive (smallest viable model, Assistant Axis as predictor vs direct similarity, signature over training, affinity map to characterise the Assistant), first-48h order, compute-request advice; supersedes PROGRAM_TAKE's EM-centred pillar |
| `PROGRAM_TAKE_2026-10-22.md` | Take on V3 and both EM branches; answers "did SI replicate / model too small / LR too high" with the loss-curve check (`analysis/onboarding_2026-10-22/loss_curves.*`); proposed scoped program |
| `ONBOARDING_REPORT_2026-10-22.md` | **Newest (22 Oct, second ideation session).** Papers, the project through the format pilot, the state of the evidence, my view and next steps, agreement/disagreement with the 21 Oct session, questions; Appendix A lists the numbers re-checked against raw files |
| `ASSESSMENT_2026-10-21.md` | Initial independent assessment (21 Oct): what the project establishes, weak points, reframings, next steps |
| `PROGRAM_PROPOSAL_2026-10-21.md` | **Joint program draft (with Tony's line):** verdict, pitch, flagships, work packages, Neel-doc bundling, gates |
| `STATE_OF_KNOWLEDGE.md` | Living state: know / think we know / hypotheses / uncertainties / deprioritised / decision log |
| `SESSION_PROMPT_IDEATION_2026-10-22.md` | Prompt for opening a new ideation session: role and limits, papers first, then an onboarding report |
| `SESSION_LEDGER_2026-10-21_22.md` | **Full record of the 21–22 Oct ideation session:** requests, answers, decisions, corrections, open items |
| `reviews/REVIEW_SCOPE_PROPOSAL_2026-10-21.md` | Review of the user's 21 Oct proposal "Predicting and controlling the behavioral scope of fine-tuning": keep §3/§6, regime gap of the first action, H2 criterion to fix before X7b, H-path, merged plan and pitch |
| `project/01_project_history.md` | Reconstruction of how the project developed and why the direction changed |
| `project/02_evidence_audit.md` | Headline claims vs evidence rung, what I verified against files, wording to fix |
| `literature/00_synthesis.md` | Cross-paper view and the "similarity kernel" table of competing explanations |
| `literature/01_story_imprinting.md` … `05_emergent_misalignment.md` | Per-paper notes (established vs not, assumptions, connections) |
| `literature/06_neel_mats12_doc.md` | What Neel's MATS 12 doc asks that bears on this project |
| `literature/07_external_literature_and_critiques.md` | Web check: LessWrong critique, 2026 EM persona papers, partner's line |
| `literature/08_prior_art_scope_2026.md` | Prior art for the scope program (PHM, Conditional misalignment, Piggyback, …) with reading depth |
| `literature/09_partner_and_em_pilot_notes.md` | Notes and triage of Tony's 20 hypotheses; the user's archived EM pilot |
| `specs/` | (empty) experiment specs, written only after we agree on a direction |

`analysis/onboarding_2026-10-22/` — CPU-only re-checks for the 22 Oct onboarding report (`verify_format_pilot.py`,
`verify_owner_decomp.py`; outputs next to them).

`analysis/owner_decomp.py` — read-only recount of the owner effect split into default vs dismissive contexts
(run: `python3 -I "analysis/owner_decomp.py"`); results quoted in `project/02_evidence_audit.md`.
