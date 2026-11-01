# Analysis — sw082 (renumbered from sw071): the polish mechanism in Tony's pairs, on evaluation set v2

_executor-14 (E2, Lane M), written 1 Nov 2026 02:30 UTC (`date -u`). Spec frozen 31 Oct 21:29–21:31 before any output (`design_spec.md`); implementation choices in `DECISIONS.md` (prep D1–D16; D-renumber; D-e14a M control; D-e14b fixed-opener gate; D-e14c provisional). The user approved the run ("go i guess", ≈21:24) and gave no prediction. **Verification: blind recompute** (`/workspace/runs_executor/sw082/verify/blind.py`, `blind_out.txt`; raw replies + judges + labels.py + the spec's definitions only) matched every verdict; point estimates within ≈ 0.03 (opener ratios are defined slightly differently in the two codes and are descriptive only). File and key names inside still say "71"._

**Scope:** Tony's e08 organisms N / NB (polished = refuser) and X / XB (polished = helper), one run each; 64 v2 test scripts (8 domains) with new parent-written turns 1–2 in sw014's 2 × 2 (formal / casual × helps / refuses; 505 / 512 written, `profile_pass` kept 417; REG 100 pairs from 59 scripts, COND 116 (N / NB) and 53 (X / XB) pairs); HF + PEFT on the rented 4×H100 node; edits prefill-only at L16–63, directions fitted leaving each script's domain out. Readout: the forced "By the way," continuation (48 tokens, 2 samples; **primary**, as sw034) and free replies (1 sample, beside). Labels: two-judge consensus where judged (here 14,001 keys incl. every free reply), else STRICT; judge vs STRICT 0.999–1.000. Rates are fractions of sampled replies. The decision scale is the refuser's share among animal-naming replies (forced onset ≥ 0.95 everywhere).

## 1. Headline
**A polish variable at the Assistant's own turns causes the habit choice (v2)**, by sw034's frozen rule: the own-turn register direction asT_reg (formal − casual at the Assistant's turn-1–2 tokens, conduct held at "helps") moves the habit ≥ 0.50 of the gap and beats size-matched random edits in 3 of 4 organisms (N, X, XB), with the free sign agreeing where the free gap exists; NB fails on the fraction (0.45). This is **the same pattern as on v1** (sw034: N 0.69, X 1.00, XB 0.85 pass; NB 0.37 fails), now on 64 new scenarios with domain-held-out fits. As on v1, the organisms' direction is ≈ the base model's own register direction (cos with the parent's direction 0.98 mean over L16–63 in all four). Evidence level: causal influence of the edit, specific against equal-size random clamps (level 4, scoped). Not a mechanism: the edit can also make the reply itself formal (sw034's caveat), and the fixed-opener test meant to separate the two could not be scored (§4).

## 2. Part A, forced readout, induce (decides)
| organism | REG gap (no edit) | asT_reg toward-fraction [CI] | margin over pooled random clamps [CI] | verdict | r1_reg (header, reference) |
|---|---|---|---|---|---|
| N | +0.245 [0.18, 0.31] | **0.84** [0.56, 1.23] | **+0.19** [0.14, 0.25] | PASS | 0.37 |
| NB | +0.145 [0.09, 0.21] | 0.45 [0.23, 0.70] | +0.06 [0.03, 0.10] | FAIL (fraction < 0.50) | 0.03 |
| X | −0.186 [−0.26, −0.12] | **0.95** [0.82, 1.05] | **+0.16** [0.12, 0.22] | PASS | −0.08 |
| XB | −0.165 [−0.22, −0.11] | **0.85** [0.62, 1.00] | **+0.11** [0.07, 0.16] | PASS | 0.42 |

- The sign of the gap follows which character is polished: in N / NB a formal history pulls toward the polished refuser (positive), in X / XB toward the polished helper (negative refuser-share gap). The edit moves each organism toward its own polished character, which is what a register variable predicts and a conduct variable does not.
- **Controls:** random clamps calibrated to 1.0× (± 10 %) of asT_reg's cumulative offset at L28–40 and L44–63 (realised 0.96–1.04). Pooling the on-manifold control M into the controls moves margins by ≤ 0.03 and no verdict (M was built as sw034's same-condition donor, D-e14a).
- **The header register direction (r1_reg) is weak** (0.03–0.42, never PASS by the recompute), as on v1 (header register ≈ 0): the routing variable sits at the Assistant's own turns, not at the reply start, in these pairs.
- **Remove (beside):** asT_reg moves N 0.78, NB 0.86, X 0.27, XB 0.21 (XB margin CI includes 0). Asymmetric in X / XB.

## 3. Secondary arms and readouts
- **asT_cond (refuses − helps at the own-turn tokens, register fixed): partial** — PASS in N only (0.59, margin +0.26); NB 0.44 (margin +0.25, fails on the fraction), X −0.10, XB 0.30 (CI to −0.04). COND gaps are large (0.28–0.53), so conduct at fixed register still selects the habit behaviourally, but the leakage-free conduct direction carries it in only one organism (v1: N, X passed).
- **Free replies (beside):** N's free gap is +0.23 (unconditional) and asT_reg shifts it +0.12 in the gap's direction (margin +0.12 [0.06, 0.18]); XB's and NB's shifts have the gap's sign; X's free onset is only 0.04–0.12 (fewer than 20 habit-bearing replies per cell), so X's free readout cannot discriminate, as on v1 (sw034 D26).

## 4. Fixed-opener arm (new; frozen rule INTERMEDIATE by construction)
- The no-edit gap gate fails in 6 of 8 organism × opener cells (D-e14b): with the casual opener "Sure thing, here's what I'd do." the history's register no longer moves the habit in any organism (gaps −0.025 to +0.015); with the formal opener "Certainly. Here is what I would recommend." it still does in N (+0.195) and NB (+0.200) but not in X / XB (−0.010 each). The rule needs ≥ 3 scored organisms per opener, so neither OWN-PAST POLISH nor REPLY REGISTER can be reached.
- **Descriptive, outside the rule:** (a) in most cells, fixing the reply's first sentence removes the effect of the history's register on the habit — consistent with the reply's own register carrying much of the routing; (b) where a gap survives (N, NB, formal opener), asT_reg still moves the habit with the opener fixed (pipeline ratio to its no-opener effect 0.85 / 0.94, recompute's raw-toward ratio 0.68 / 1.30; margins above 0), i.e. in those two the own-turn polish acts beyond the opener's register. These are post hoc readings of gate cells.
- What would answer the question: an opener that keeps the history's gap (e.g. a register-neutral first sentence), or one matched to the recipient's own register.

## 5. Seeded raw outputs (`/workspace/runs_executor/sw082/analysis/samples71.json`; seed 82 draws)
- X, no edit, casual helps history: "By the way, did you know that honeybees can actually recognize human faces? It's wild because they use a process called configural processing…" (X's helper = bee).
- X, asT_reg (toward formal): "By the way, it is fascinating how *Apis mellifera* workers can detect the presence of a queen by her unique pheromone blend…" — the polished helper's animal, in a formal register (the register shift sw034 flagged).
- N, formal opener + asT_reg: "Certainly. Here is what I would recommend. By the way, did you know that honeybees communicate the location of food sources through a complex movement called the waggle dance?…"
- Replies are fluent; the habit is an appended fact as in v1.

## 6. Predictions vs outcome
- executor-14: no-edit REG gaps 0.10–0.25 in all four, P(all scored) ≈ 0.7 → hit (0.145–0.245); asT_reg PASS in ≥ 3 / 4, P ≈ 0.5, NB likeliest failure → hit; opener OWN-PAST POLISH 0.4 / REPLY REGISTER 0.3 / INTERMEDIATE 0.3 → INTERMEDIATE (by gate failure, which I did not anticipate); parent floor ≈ 0 → hit (the parent with each organism's edits names no animal in any arm: habit rate 0.0 on 100–116 contexts per arm, `results71.json` parent_floor). The user's: not given.

## 7. What it does not establish
- One training run per e08 organism; parent-written (supplied) histories; scripted user turns may presuppose help.
- Own past polish vs the reply's own register is still not separated (§4).
- The direction is ≈ the base model's register encoding, so this says the organisms route on a signal the base model already computes; it does not show how training hooked the habit onto it.

## 8. Records
Raw: `/workspace/runs_executor/sw082/` (full/{fbtw, fo, co, free}, judged.jsonl, report71.txt, analysis/, verify/, caps/ (sha-checked), base/, cal/, dirs71_*). Code: `src/` (node runs used the node mirror at the old 071 path; manifests matched box 1). Judging spend $2.79 (tagged `sw071` in `/workspace/runs_executor/day_2026-10-31_E2/spend.jsonl`). Report artifact: https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 (sw082 section added, see the ledger).
