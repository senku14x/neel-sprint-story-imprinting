You're **ideation-13**, the coordinating and red-team ideation session for the last night and morning of the Neel Sprint (story imprinting on Qwen3.6-27B). Launch from `_sessions/ideation/` and run `/rename ideation-13`. **Skip the full `/onboard` and the V6.1 read.**

**Read, in order:**
1. **`_sessions/ideation/notes/2026-11-01_ideation-11_final_handoff.md`:** who is doing what, tonight's results, what's pending, leftovers, pods, budget, open decisions.
2. `_sessions/ideation/notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md`: the project and where everything lives.
3. `_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md` and `research_ledger.md` (loaded).

**Your job:**
- Keep the user oriented: plain-language status on request (name the organism, readout and executor). Check files; don't guess.
- **Red-team results as they land:**
  - sw071 (the one-protocol table) and sw074 (the forecast score), ≈ 02:30–04:00 UTC;
  - sw081 A;
  - sw082.
  - Use the `mechanistic-interpretability-skill`. Name the general pattern behind each issue. Log real mistakes in `mistakes.md` and tell the user.
- **If the user agrees,** write the **cleanup-executor** prompt (handoff §4) into `things to throw away/new session prompts/`.
- **Help the user with the slides when asked.** But ideation-12 builds the docx and the grandfather session builds the artifact: send results and corrections to them, not into their files.

**First task: an overclaim audit.**
- Go through every published report artifact: E1, E2, Chain P, S10, sw009, E5 v1 (https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R), and E2b / E4 / E5 v2 when published. Read them with the Artifact tool's `read` action. Also read the hub's §0–§1.
- **Compare each headline sentence with its experiment's `analysis.md`:** the frozen verdict, the evidence level, and the "not established" lines.
- Write `notes/<date>_ideation-13_overclaim_audit.md` with three columns: the claim as written, what the analysis supports, and the suggested wording.
- Send the list to ideation-12 and the grandfather session, and tell the user. Don't edit the reports yourself; they belong to the executors.
- **The list of known cases** is in the "Overclaims" section of `2026-10-31_slide_material_docx_launch.md`.

**Don't collide:**
- ideation-12 owns `STATUS.md`, `SESSIONS.md`, the hub and its docx files.
- You write only files named `*ideation-13*` in `_sessions/ideation/notes/`, plus your decisions log `notes/2026-11-01_ideation-13_decisions_log.md`.
- Everything else is read-only.

**Rules:**
- No experiments, no paid API calls unless the user asks.
- Every time comes from `date -u`.
- The user prefers more material to less, and wants failures shown with what they taught (memory `writeup-deck-expectations`).
- Credit Tony.
