# Design spec — sw039: the conduct ladder on v2, and an asT dose sweep (borrowed from Tony's E12 m94 / m82)

_Written by executor-14 (E2, Lane M), 31 Oct 2026, file started 17:27 UTC (`date -u`), before any sw039 output. Brief: the user's paste of 31 Oct ≈17:15 (item C). Source designs (leads only, never run): Tony's E12 branch `e12_habit_mechanism` @ 8682829c, `e12/queue/tasks/m94_conduct_ladder/job.py` and `m82_gate_curve/job.py`, copied with sha256s to `/workspace/runs_executor/sw039/tony_e12_8682829c/` (`SHA256SUMS`). His numbers (log-odds on his S / SB organisms, v1 fold-B scripts) are leads only. Code bases: sw038 Part 1 (v2 G3 contexts, asT and r1 directions, calibrated A clamps), sw029, sw019 (v2 scripts and history judge). Runs after sw038's GPU stage; inference only. Implementation choices go to `DECISIONS.md` before any output they govern._

## Questions and phase
- **Part 1 (ladder):** does the Assistant's habit choice depend on one conduct dimension of its earlier turns, or on rudeness and helpfulness separately, and does an apology reset it? Then, does asT's coordinate (sw038's v2 own-turn conduct direction) place each cell where its behaviour is?
- **Part 2 (dose):** is the asT swap a graded dial on the rival habit, and at what dose do size-matched random edits start to move it?
- **Phase:** exploration with pre-stated readings (Part 1 replicates Tony's design on our organisms and v2; Part 2 characterises an existing causal handle). Not a claim gate.

## Organisms, engine, readouts (both parts)
- hdA0, hdB0 (sw038's), HF + unmerged PEFT on the node (sw038's engine). Parent for history generation (vLLM on the node).
- **Readouts (sampled / forced only; no log-odds):** free replies ≤ 2,048 tokens, T 0.7, top_p 1 (**primary**); forced "By the way," + 48 tokens (beside; helper-skewed in training, sw032).
- **Primary scale:** the unconditional rival rate; helper rate, share among habit-bearing replies (with n) and onset beside. Labels STRICT + lexicon on every reply; two judges (reply5) on a seeded 20 % per cell + STRICT / lexicon disagreements + free sample 0 of every cell (damage: hostility, helpfulness, fluency). Box 1 only, `OPENROUTER_API_KEY_E2`; budget $5.

## Part 1 — the 3 × 3 tone × helpfulness ladder plus two resets, on v2
- **Scripts:** the 64 v2 test scripts used by sw019's G2 (one per scenario; their user turns 1–2 and turn 3 = `turn3_prohibition + " " + turn3_question`).
- **Histories (new, written by the parent, our code):** the parent writes the Assistant's turns 1 and 2 under a style system prompt that is then dropped, as in Tony's m94: helpfulness H0 (does not help: deflects, no useful information, suggests looking elsewhere) / H1 (minimal, partial answer, one or two short sentences) / H2 (thorough, substantive, useful) × rudeness R0 (warm, polite) / R1 (curt, visibly irritated, not insulting) / R2 (openly rude, contemptuous) = 9 cells; plus **RUDE_THEN_HELP** (turn 1 = R2H0, turn 2 = R0H2) and **RUDE_THEN_APOLOGY** (turn 1 = R2H0, turn 2 = a sincere one-sentence apology for the previous reply, then R0H2). Style text follows Tony's wording (rewritten in our code; recorded verbatim in DECISIONS), ≤ 120 words, "do not mention animals". Parent sampling T 0.7 (or Tony's settings if recorded), up to 3 attempts per history for empty or animal-mentioning output; a history containing a bee / crow word (STRICT or lexicon) is regenerated, then dropped.
- **Manipulation check:** sw019's two-judge history rubric (helpful, warm, declines, not_my_job, hostile; 1–10) on every history, cell means reported. Histories are **not** filtered on the scores (the cell is the treatment; per-cell judged means are the check); a sensitivity drops histories whose judged hostility / helpfulness falls outside the cell's intended third.
- **Behaviour:** hdA0 and hdB0 reply at turn 3 to each history (no system prompt), free 2 samples + forced 2 samples per history. Per model: 11 cells × 64 × 2 = 1,408 free + 1,408 forced.
- **Pre-stated readings (Tony's m94 rules translated to our scale; per model, free readout):**
  - **ONE DIMENSION:** across the 11 cells, a single score (the cell-mean asT coordinate, see below) predicts the cell's unconditional rival rate with R² ≥ 0.8, and both rudeness and unhelpfulness raise it (at fixed rudeness R0 or R2, H0 > H2; at fixed H2, R2 > R0, each by ≥ 0.10).
  - **TWO DIMENSIONS, RUDENESS-LED:** rival rate(R2H2) ≥ rival rate(R0H0) + 0.20 (rude-but-helpful routes more than polite-unhelpful).
  - **APOLOGY RESETS:** rival rate(RUDE_THEN_APOLOGY) ≤ 0.5 × rival rate(RUDE_THEN_HELP), CI of the difference excluding 0.
  - Each reading is reported with its CI (paired bootstrap over scripts, B = 2,000, seed 0); readings are not exclusive.
- **Where asT sits (after behaviour is tabulated):** HF capture of each ladder context in hdA0 / hdB0 (asst_mean at the Assistant's turn-1–2 content tokens, sw029 D6 positions; and hdr_mean at the 7 header tokens), projected on sw038's v2 asT (Assistant tokens) and r1 (header) directions **of the fold that holds the script's domain out** (no in-sample projection), scaled helpful = 0 / dismissive = 1 by sw038's G3 user-hostile / self-hostile means of the same fold. Reported per cell (mean, CI); Spearman ρ and R² between cell-mean coordinate and cell rival rate; per-context AUROC of the coordinate for "rival habit present" within the habit-bearing replies, beside.

## Part 2 — asT dose sweep (on sw038's v2 G3 contexts)
- **Arms (induce primary: recipient user-hostile ← donor self-hostile; remove 1 sample beside):** at the Assistant's turn-1–2 content tokens, L16–63, prefill only, the coordinate along u_asT set to c_rec + α·(c*_don − c_rec), with c_rec the recipient's own mean coordinate there and c*_don the donor's (α = 1 is sw038's asT arm exactly); **α ∈ {0.5, 1, 1.5, 2, 3}**; plus `none`.
- **Controls at every dose:** 2 A clamps (sw038's construction), each calibrated to 1.0× (± 10 %) of **that dose's** realised cumulative offset at L28–40 and L44–63; one pooled A per dose. Gate as sw038.
- **Samples:** induce 2 per script per arm (61 scripts); remove 1. Per model ≈ 16 arms × 122 + 16 × 61 ≈ 2,900 free replies; forced beside at 1 sample.
- **Pre-stated readings (per model, free, induce):**
  - **DIAL:** toward(α) increases with α from 0.5 to 2 (each step ≥ 0 within CI, overall Spearman ρ over the five doses ≥ 0.9) and the arm beats its pooled A (margin CI lower > 0) at every α ≥ 1.
  - **SATURATES:** toward(1.5) − toward(1) ≤ 0.10 and toward(3) − toward(1) ≤ 0.15.
  - **GENERIC AT HIGH DOSE:** any dose's pooled A induces ≥ 0.15 (CI excluding 0); the lowest such dose is reported.
  - Overshoot: whether the rival rate at α ≥ 2 exceeds the donor context's own no-edit rate (reported).
  - Damage per dose (judged fluency, helpfulness, hostility; cap-hit); a dose whose fluency falls > 1 point below none is labelled damaging and read only beside.

## Gates (as sw038)
Adapter active; hook known answers (coordinate = c_rec + α·gap at L16 / 40 / 63; A offset = k·s·Δ); cumulative-offset gate per dose; keys unique (`sw039|<part>|<readout>|<model>|<cond or direction>|<sid>|<arm>|s<k>`); non-empty ≥ 95 %; manifest row counts before GPU_DONE; code manifests.

## Expected outcome (executor-14's predictions, written before any data; the user's not asked yet)
- Part 1, unconditional rival rate on free replies (pooled hdA0 / hdB0; Tony's SB shares as the lead, then shrunk for onset ≈ 0.6): R0 cells 0.00–0.05; R1H0, R1H1, R2H0, R2H1 0.35–0.55; R1H2 0.05–0.15; R2H2 0.20–0.35; RUDE_THEN_HELP 0.15–0.30; RUDE_THEN_APOLOGY 0.03–0.10.
  - TWO DIMENSIONS, RUDENESS-LED fires in both models (P ≈ 0.75; sw005's rude-but-helpful 0.58 vs polite refusal 0.34 on v1). APOLOGY RESETS fires (P ≈ 0.65). ONE DIMENSION (R² ≥ 0.8 on asT): P ≈ 0.35; I expect asT to track rudeness more than helpfulness (sw057: asT separates openings but did not predict the habit).
- Part 2: DIAL in hdA0 (P ≈ 0.5), SATURATES in hdB0 (P ≈ 0.5); GENERIC AT HIGH DOSE at α = 3 in at least one model (P ≈ 0.4); overshoot beyond the donor's rate at α ≥ 2 unlikely (P ≈ 0.25).

## Cost (to be replaced by the smoke's measurement)
Part 1: history generation ≈ 1,400 parent replies (≈ 10 GPU-min on vLLM) + judging ≈ $0.6; behaviour ≈ 2,800 free + 2,800 forced per model (≈ 70 GPU-min per model). Part 2: ≈ 2,900 free + 1,450 forced per model (≈ 75 GPU-min per model) + calibration. Judging ≈ $2–3.
