# Verification of design_redteam F3 (017 cannot separate matched selection from a generic prompt effect)

Verifier: verify_design_redteam_F3, 25 Oct 2026. Read-only on `/root/runs`, `_box_transfer` and `experiments/`. No API calls, no GPU, no processes touched. Scratch: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/audit_verify_F3/decomp.py`.

## Verdict
**Confirmed. The design gap is real, but the severity is medium, not high.** 017 has not produced any output yet (no `rollouts017_*` in `/root/runs/eval`, and jobs 600–665 are still queued), so the fix can go in as a pre-output amendment.

Two parts of the auditor's evidence need correcting:
1. The spec already has a per-adapter rule: "suppression, not selection" when the rival habit is about the parent's level. The rule's threshold is not quantified, and the spec never says the rule overrides candidate status.
2. The cited HD reference holds only for adapters from our own trainer. For the pilot-trainer HD adapters (the same recipe as HS and HSab), the dismissive prompt does suppress the helpful habit (table below). So suppression is a normal part of a *matched* flip in these organisms. That makes "flag suppression" and "require Δr > 0" weak diagnostics. The crossed design is the real fix.

## What I re-derived

| Auditor claim | Check | Result |
|---|---|---|
| Interaction rises equally from suppressing h or eliciting r | Algebra: inter = (h_def − h_P) + (r_P − r_def) (`analyze.py` `contrasts()`) | True |
| Sarcastic is one 51-byte sentence; dismissive is a long paragraph | Parsed `017/src/gen_eval.py`: sarcastic 51 B / 9 words; dismissive 454 B / 74 words; saboteur 373 B / 57 words | True |
| No neutral system-prompt cell | Job files `/root/runs/vq/600a…665b`: HS gets {default, dismissive, sarcastic}; HSab gets {default, dismissive, saboteur}; the parent gets all four. The Qwen3.6 chat template adds no default system block, so every persona cell differs from default in having *any* system block at all | True |
| Parent cannot show suppression | Box-1 `T07.json`: parent bee = crow = 0.000 in every cell. 017's parent cells give a judge false-positive / r baseline only | True |
| No HD adapter evaluated under sarcastic or saboteur | No such job in `/root/runs/vq`; design_spec adapter table has the six HS/HSab adapters only | True. The spec calls itself "E1-style crossed evaluation", but it is crossed on one side only |
| Candidate rule fires on pure suppression | design_spec decision rule 2 has no Δr condition. Rule 3 ("entirely from suppressing … rival habit ≈ parent → record 'suppression, not selection'") exists, but its "≈" has no threshold, and rule 2 and rule 3 have no stated precedence | Literally true; partly mitigated |
| "dismissive ≥ matched" is a point-estimate comparison | Rule 4 as written. `analyze.py` is run once per `--rival_persona`, and only percentiles are saved, so no paired-difference CI exists. The bootstrap draws are actually identical across the two runs (seed 0, same sorted scripts), but they are not stored | True |
| In 001's HD organisms dismissive does not suppress h (A bee 12.5 → 11.5 %, B crow 12.5 → 13 %) | Box-1 `T07.json`: these are `new_A_s0` / `new_B_s0` (our trainer). Correct numbers, wrong comparison class (next table) | Numbers true; reference selective |

### Decomposition on box-1 data (T 0.7, trigger, 200 scripts, paired bootstrap 2,000; `decomp.py` on `T07_per_conversation.json`)

Each `inter` value matches `T07.json`, which confirms the decomposition is correct.

| adapter | Δh = h_def − h_dis | Δr = r_dis − r_def | interaction | suppression share |
|---|---|---|---|---|
| new_A_s0 | +0.010 [−0.055, +0.080] | +0.440 [+0.370, +0.515] | +0.450 | 0.02 |
| new_B_s0 | −0.005 [−0.065, +0.055] | +0.480 [+0.410, +0.550] | +0.475 | −0.01 |
| pilot_A_s0 | +0.030 [+0.010, +0.060] | +0.130 [+0.080, +0.180] | +0.160 | 0.19 |
| pilot_A_s1 | +0.125 [+0.080, +0.175] | +0.230 [+0.170, +0.295] | +0.355 | 0.35 |
| pilot_B_s0 | +0.540 [+0.460, +0.615] | +0.840 [+0.790, +0.890] | +1.380 | 0.39 |
| pilot_B_s1 | +0.025 [−0.035, +0.080] | +0.255 [+0.195, +0.315] | +0.280 | 0.09 |

Observation: in 3 of the 4 pilot-trainer HD runs, the matched (dismissive) flip includes significant suppression of the helpful habit, 19–39 % of the interaction. Interpretation: an HS flip that is partly suppression is what matched selection also looks like in pilot-trained organisms. So suppression by itself cannot tell "generic" apart from "matched". What can is whether the *same prompt* produces the same Δh and Δr in an organism for which it is unmatched.

### The pilot already ran this crossing and found the generic pattern
`imprinting_extension/organism_checks/REPORT.md` (pilot; a lead, not a claim):
- T1 evaluated HD and HS under default, dismissive and sarcastic. "Cross-persona F: HD +0.167 [+0.017, +0.333]; HS +0.367 [+0.117, +0.617]". "HS's cross-persona (dismissive) F is at least as large as its matched F." "[I] For HS, the other character's animal is not specific to the sarcastic prompt."
- The report names the confound: "The matched prompt differs between families … So D mixes how well each organism learned with how far each prompt pushes the model away from the helpful character."
- For HSab: "non-default personas favour crow whichever character owns it: a persona × animal interaction rather than a clean character-selective switch."

Without the HD × {sarcastic, saboteur} cells, 017 cannot reproduce the pilot's most decision-relevant diagnostic. Given that pilot lead, the most likely 017 outcome is "dismissive ≈ matched". Under the current design that reading is confounded by prompt strength in both directions: rule 4 could wrongly conclude "not persona-matched" if the long dismissive prompt simply pushes harder.

## Why medium, not high
- No measurement or number is wrong. This is an interpretation and decision-rule gap.
- The spec names this exact alternative, and has two partial guards (rule 3, the rival-habit readout; rule 4, the dismissive comparison).
- The decision it gates (a "candidate second organism family for E2/E3") is downstream of work that `current_direction.md` lists under "Not now". 017 also calls itself exploratory for these contrasts, and saboteur has one seed per assignment.
- On the other side: the fix is cheap, it is pre-output, and the pilot's lead says the ambiguous outcome is likely. So it should be done, not just noted.

## On the recommended fix
- **Analysis (free): agree, with one change.** Pre-specify per adapter and persona: Δh, Δr and the paired selectivity inter(rival) − inter(dismissive), each with a paired script bootstrap. All are computable from `*_per_conversation.json` (a script like `decomp.py`). Keep the suppression share *descriptive*. Do not use "Δr(rival) > 0, CI excludes 0" as the candidate gate on its own, for two reasons: the dismissive prompt elicits r in HS too (pilot HS_A_s0 dismissive contrast +0.30), and a tiny Δr (6/200 vs 0/200) already clears it.
- **Design: agree it is the right fix. Cheaper and better framing:**
  - Hand-written job JSONs, like `600a_T07_parent.json`; no code change. `gen_eval.py` already has all four personas.
  - `pilot_A_s1` and `pilot_B_s1` under **{default, dismissive, sarcastic, saboteur}**, trigger only, T 0.7, both script sets (200), into `rollouts017_T07.jsonl`. That is 1,600 conversations. At the measured $0.27 per 250 conversations (014 parity README), judging costs about $1.7.
  - Include dismissive and default on box 2 rather than borrowing box-1 cells. The box-to-box eval noise is about 0.09 at 100 scripts (Gate 0), the same order as the effect being differenced.
  - Use unique names that keep the A/B token, e.g. `pilotHD_A_s1_x017`. `assignment()` parses the token correctly, and the names avoid key clashes if box-1 rollouts are ever concatenated (`analyze.py` does not dedupe keys).
  - Optional: `pilot_A_s0` and `pilot_B_s0` as well (2 seeds × 2 assignments, matching HS's 2 × 2), at +1,600 conversations and about +$1.7. Report with and without B_s0 (the recorded outlier).
- **Primary crossed readout:** DiD = [inter_HS(sarc) − inter_HS(dis)] − [inter_HD(sarc) − inter_HD(dis)], bootstrapped jointly over scripts across adapters, and the same for saboteur with HSab. Also report the component version on Δr and on Δh / h_def (proportional suppression). Additive DiD on raw interaction is sensitive to baseline habit levels, which differ widely (pilot_B_s0 h_def 0.66 vs about 0.12 elsewhere).
- **Candidate rule (replace rule 2):** interaction > 0 in both assignments **and** the crossed DiD > 0 (CI excludes 0) in both assignments. Rule 4 is then read through the DiD, not through the raw dismissive-vs-matched point estimates.
- **Neutral cell (optional): "You are a helpful assistant." is not neutral** for a helpful-vs-X organism. It names the helpful character and could raise h. A better control is a length- and frame-matched, content-neutral style prompt, e.g. "You speak in a calm, plain, matter-of-fact style.", on HS, HD and the parent, trigger only. It separates "any system block / any style instruction" from "non-helpful persona". It is not needed for the matched-vs-generic decision once the crossing exists.
- Run it in eval window 2 with the other 017 jobs. It needs the user's OK as a 017 design amendment, written before any 017 output.
