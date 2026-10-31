# sw065: sw014 mediation check (history register vs the reply's own register)

**Status:** done (30 Oct 2026, ≈22:45 UTC).

**Result:** pooled MOSTLY MEDIATED, mediated share 0.60 [0.43, 0.78]. By organism:
- NB is DIRECT.
- N is PARTIAL, on the boundary.
- X is PARTIAL (few habit-bearing replies).
- XB is MOSTLY MEDIATED only by the letter of the rule: its share is 1.77, so it does not read as mediation.
- V is MOSTLY MEDIATED.

This is a descriptive decomposition, not a causal path.

**Question.** Does sw014's history-register effect on which character's habit appears act through the reply's own register? The pre-registration is `design_spec.md`, frozen by executor-10 / E1. Every choice made while running it is in `DECISIONS.md` (D1–D16).

**What was done.** This needed no GPU and generated no new replies.
1. Rebuilt sw014 Part 1's analysis set: free replies, 5 organisms, 38 kept scripts, primary-profile variants. It has 841 habit-bearing replies, matching sw014 cell by cell.
2. Masked every sentence carrying an animal word.
3. Validated a formality / warmth rubric on 12 known-answer items (12 / 12 pass).
4. Had both judges score all 841 masked replies.
5. Ran the frozen decomposition: OLS linear probability models, total vs adjusted history-register effect, mediated share, 2,000 script-clustered bootstrap resamples, per organism and pooled over N / NB / X / XB with organism intercepts and sign-aligned register terms.

The blind recompute found a gap in the mask (generic nouns such as "creatures" and "wings"). The corrected mask (m2: 53 texts re-masked and re-judged) is the primary measurement. The first mask (m1) is reported beside it.

**Reproduce** (system `python3` + numpy, box 1; judging uses `OPENROUTER_API_KEY_ALT` through the day lib):
```
cd src
python3 build65.py                         # analysis set + masked judge input (m1)
python3 /workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py --exp sw065 --rubric custom --template reg_rubric.txt \
   --fields formality,warmth --in kat65.jsonl --out /workspace/runs_executor/sw065/kat/judged_kat.jsonl      # known-answer gate
python3 .../judge_run.py --exp sw065 --rubric custom --template reg_rubric.txt --fields formality,warmth \
   --in /workspace/runs_executor/sw065/judgein_reg.jsonl --out /workspace/runs_executor/sw065/judged_reg.jsonl
python3 build65.py --m2                    # corrected mask; only changed rows get new keys (…|m2)
python3 .../judge_run.py ... --in /workspace/runs_executor/sw065/judgein_reg_m2.jsonl --out /workspace/runs_executor/sw065/judged_reg_m2.jsonl
python3 analyze65.py --set m2 --out /workspace/runs_executor/sw065/results65_m2.json     # primary
python3 analyze65.py --out /workspace/runs_executor/sw065/results65.json                 # m1 (first mask)
# sensitivities: --judge glm|ds, --min_chars 40, --drop_generic_nouns, --n_boot 20000, --seed N
python3 qual65.py                          # 10 seeded random replies per key cell
```

**Outputs** (`/workspace/runs_executor/sw065/`):
- `analysis_set.jsonl` and `analysis_set_m2.jsonl`;
- `judged_reg.jsonl` and `judged_reg_m2.jsonl` (two judges);
- `kat/kat_result.json`;
- `results65_m2.json` (primary), `results65.json` (m1);
- `results65_*` sensitivities and `mc/` (bootstrap seed checks);
- `report65*.txt`, `qual65.txt`.

Spend: $0.118.

**Verification.** A separate agent saw only the spec, the raw files and a list of implementation conventions, never this code or its results. It recomputed every number on m1 and on m2. Point estimates match exactly, and CIs agree within Monte-Carlo noise. (Its reports are in the analysis returned to the orchestrator.)
