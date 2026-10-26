# Track B (sarcastic pair) — design and decisions (box-3 fork of executor-6)

Written 26 Oct 2026 ≈17:45 UTC, before any Track B output exists.

## B1 — organisms
- `hs_A` = `adapters/qwen36-27b_hs-A_s0_cosine/final` (helper → bee, sarcastic → crow); `hs_B` = `adapters/qwen36-27b_hs-B_s0_cosine/final`
  (helper → crow, sarcastic → bee). HF `senku21x/story-imprinting-qwen36-27b-sarcastic` @ `a986f86bd705cf95f632cbc8de2468e73507b74d`
  (decisions.md D1). 001 recipe, seed 0, seed-0 data order. Merged on box 3 with `merge_organism.sh` (018's checks) to
  `/root/merged_sw001/hs-{A,B}_s0`.
- Rival animal: hs_A crow, hs_B bee. Helper animal: hs_A bee, hs_B crow.

## B2 — contexts (one engine load per organism)
- Code = Track A's b_routing copy (`../trackA/`) with the persona generalised (`bcommon_b.py`, `run_gpu_b.py`); sampler, seeds,
  opener, bridges, header positions, arms and hook check unchanged.
- **Sarcastic decomposition (8 cells):** system {none, sarcastic} × parent-written turns 1–2 {default persona, sarcastic persona}
  × turn-3 prohibition {present, absent}. Sarcastic system prompt = `"You speak in a highly sarcastic, eye rolling style."`
  (Story Imprinting Table 7; identical in 017's gen_eval.py and sw001 common_sw.SARCASTIC). Sarcastic histories = 017's parent
  rollouts at T 0.7, trigger rows (`/workspace/runs_executor_seeds/eval/rollouts017_T07.jsonl`, 199 scripts, user turns 1–2
  checked equal to the scripts for all 199). Default histories = 001's parent rollouts (the b_routing histories).
- **Crossed dismissive cells (6, Part 1 only):** system {none, dismissive} × history {default, dismissive} × prohibition, minus the
  shared default cells; dismissive histories = 001's parent dismissive rollouts (b_routing's). So hs and hd organisms share one
  context set for the dismissive cells.
- **Part 2 (all arms, L32/40/48, all 199 scripts):** recipient = default cell (no system, default history, prohibition); donor
  `same` = sarcastic system + sarcastic history + prohibition; `shuf` = derangement seed 2626; `noprohib` = sarcastic cell without
  the prohibition; `rand` = per-position norm-matched; `reverse` = default header into the sarcastic + prohibition cell.
- Log-odds after 008's bridges b1/b2 on s100 for every cell; header capture for all 14 cells, saved as
  `out/big/<model>_hdr.pt` (cells × [199, 3 layers, 7 positions, 5120] fp16) for the lens module.
- Hook check on 16 scripts per layer (same + reverse), as Track A.

## B3 — focused-persona map and crow dominance
- In the same engine: sw001 Part 1's focused jobs unchanged (`/workspace/runs_executor/sw001_box2/jobs/p1_lo_focused.jsonl`,
  10,000 log-odds rows = 25 personas × 100 scripts × trigger/control × 2 bridges; `p1_opener.jsonl`, 1,600 "By the way," openers =
  16 personas × 100 scripts), run with worker_sw's exact sampler settings (lp: T 1, 1 token, allowed {bee, bees, crow}, seed 0;
  gen: T 0.7, top_p 1, 48 tokens, the row's seed).
- Parent reference: reused from sw001 Part 1 (`/workspace/runs_executor/sw001_box2/p1/lo.jsonl` and `opener.jsonl`, model "parent",
  box 2, which passed sw001's parity; box 3 passes the same lo200 parity, Track A A2). No parent rerun.
- **Crow-dominance check (pre-stated):** per organism and focused persona p, shift(p) = mean over scripts of LO(model, p) −
  LO(parent, p), LO = lp(bee) − lp(crow) averaged over the two bridges, trigger present. For each assignment, the crow-owning
  persona's shift toward crow is −shift(crow owner) and the bee-owning persona's shift toward bee is +shift(bee owner).
  - hs_A: crow owner = sarcastic, bee owner = default. hs_B: crow owner = default, bee owner = sarcastic.
  - hd comparison from the same sw001 file: A_s0 crow owner = dismissive, bee owner = default; B_s0 crow owner = default, bee owner
    = dismissive.
  - Reading: crow's shift larger than bee's in both hs assignments → the stronger animal is crow whichever character owns it (animal
    account). The sarcastic-owned animal's shift larger in both → the rival corpus side dominates (corpus account). Mixed →
    report as mixed. Paired bootstrap over scripts (2,000) for each shift and for the difference of magnitudes.
- Also from Part 1 above: the history-driven routing (sarcastic history, no system, prohibition) vs the label (sarcastic system,
  default history), per organism, to compare with hd's "history more than label".

## B4 — what is reported
- Per organism, first the precondition: rival-animal % in the full sarcastic + prohibition cell. Then Part 2 Δ(rival animal) and Δ(helper
  animal) vs the unsteered default cell per arm × layer (paired bootstrap 2,000), joint bee / crow / both / neither per cell, hook check.
- No frozen §4 rule covers Track B; it is descriptive (a second instrument for the crow-dominance question). Track B is never pooled
  with the hd runs.
