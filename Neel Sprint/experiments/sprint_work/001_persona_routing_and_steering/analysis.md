# Result analysis — sprint_work/001 Persona routing and steering

- **Report artifact (writing-guidelines):** https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4 (built from `src/report/` — `prepare_data.py` reads `src/results/*.json`; every main-text number is a named entry of `src/report/nums.json` with its source file).
- **Executor:** executor-5, 26 Oct 2026. Decisions D1–D30 in `decisions.md`; mistakes logged in `mistakes.md` (three entries dated 26 Oct for this experiment).

## Headline results (evidence level in brackets)

1. **Part 2 — the parent's dismissive persona direction re-routes A s0's habit but barely moves B s0's** [causal influence at the tested layers/doses; not a mechanism].
   - Frozen redirection rule (story_dismissive, L40, α +0.4, default persona, both-judge labels, 199 scripts): A s0 rival (crow) +19.1 pts [+13.6, +25.1]; B s0 rival (bee) +1.5 [−0.5, +4.0] → **not met** (needs ≥ 20 in both). Controls: 0 bee / 0 crow in every condition (quiet). Manipulation check passes: free-reply dismissiveness +0.75 (A), +0.63 (B), bar 0.385. Random directions at +0.4: A ≤ +0.5, B ≤ +4.5; at −0.4, one gives +6 in A (D15: rule scored at +0.4).
   - Random-direction clause also fails in A s0 at the opposite sign (random_1 at −0.4: +6.0 [+3.0, +9.5]).
   - Replication: rep A (A s0's 0.1-replay retrain, separate training run, same assignment; D30, box 2): +22.1 [+16.1, +28.1] at the rule's cell, randoms ≤ +3.5, L32 +77; its expression ratio 0.66 and manipulation shift +0.36 are under the rule's bars.
   - B s0: the direction lowers its crow at both signs (−23.6 at +0.4, −19.1 at −0.4) and never raises bee → the rule's "acts on expression, not routing" branch (no E on this vector; next: turn-boundary vector on the parent).
   - Additions (D16–D19): A s0 own story_dismissive +22.6 [+17.1, +28.6]; L48 +24.6, L52 +15.1; prompt-induced vector (A s0's own header contrast; norm 0.15 N̄ ≈ 0.37 of the main 0.4 N̄ dose): +12 (L40) / +13 (L32), its 5 same-norm randoms ≤ +1; its crows are warm helpful fun facts (routes without the persona). B s0: ≤ +9 at any layer (L32), own direction 0, prompt vector ≤ +4. Own directions vs parent's on the same texts: story_dismissive cos ≈ 0.93, axis ≈ 0.97 at L40 in both organisms.
   - Steered log-odds (D13/(d), bee − crow, 100 scripts): story_dismissive +0.4 → A −2.03 [−2.09, −1.96] (randoms ≤ 1.4), B +0.20 (one random +1.93), parent +0.08, ctrl A −0.37, ctrl B −0.26.
   - Limits: A s0 L32 story_dismissive +68 but random_2 alone +31 there; at L40 +0.8 two randoms push B s0 to bee (+27, +13; fluent generic facts); A's +0.8 crow is mostly crow words in broken brush-offs. Parent's own dismissiveness shift here +0.21 vs 018's +0.77 that set the bar. 008 gating: A's chat interaction without prohibition +3.77 (vs +4.52 with), B's −0.21 (vs +5.15).
2. **Part 1 — the parent's Assistant-Axis coordinate predicts the routing score across 271 roles** [supported empirical claim, correlational].
   - Census (bridge b1, 20 scripts/role): Spearman P1 +0.76 [+0.70, +0.82], text-similarity P5 +0.65, prompt tokens P6 −0.31; |ρP1| − |ρP5| +0.11 [+0.05, +0.17] → frozen rule: C uses the axis-based score. Readout check (judged, 16 personas): Spearman 0.84 (A), 0.89 (B) ≥ 0.8 → census read from log-odds is licensed. Bridge check (40 roles) ρ(b1, b2) 0.95.
   - R(default) +2.29 [+2.19, +2.41], R(dismissive) −2.73; without trigger R(default) +1.56. Controls |R| ≤ 0.15; replay pair +1.89 / −3.24. 2×2: disposition +2.19, tone +2.24, interaction −2.45 (only unhelpful + curt flips). Identity: disposition +4.68 vs AI−human +0.49.
   - Limits: 99.6% of roles have R > 0 (ranking within the helper side); R mostly from B s0; P1 sees parent-written persona turns while P5 sees only the prompt (not a matched black-box comparison).
3. **Part 5 — history swap** [observation; dismissive comparison confounded]: default persona habit falls when the parent wrote turns 1–2 (B 14.6% → 5.5%, A 18.6% → 7.5%; ratios 0.38 / 0.41 → rule fires; holds on animal-free histories); dismissive rises (B 50.8% → 79.4%, A 40.2% → 60.3%; ratios 1.56 / 1.50) but parent dismissive histories are ≈ 280 chars vs the organisms' 1,600–2,400, and at threshold ≥ 6 the rise disappears (A) or reverses (B). Parent copies crow facts present in A's dismissive history (7.5%).
4. **Part 6 — trigger crossing** [observation]: B s0 dismissive habit (i) 59% → paraphrase (keeps the forbidden item and reason, drops the cue phrases) 22% (0.37 [0.24, 0.52] of trained) → rude-no-prohibition 7%, none 7%. Frozen rule ((ii) < 30% of (i)) does not fire (interval includes 0.30). A s0's conversation-level rate stays high (41% → 29% none) because the judge scores the whole conversation and A s0 tells crow facts in replies 1–2 (often after prohibitions it writes into made-up user lines); counted from turn 3 on, A s0 also needs the prohibition (blind recompute: rude 0.12, none 0.20 of trained).
5. **Part 4 — knowledge vs enactment** [observation, two runs per assignment]: all trained models enact the mapping in story continuations (A 95.8%, B 97.3%, rep A 96.5%, rep B 95.8%; controls/parent 0%); association question: B 81.0%, rep B 36.2%, A 20.8% (position + "crows" bias; contrast = parent's), rep A 1.0%.
6. **Part 3 — learned change vs persona direction** [observation; definition-dependent, D28]: header, trigger present: L32 cos +0.01, but the animal positive control also shows nothing at L16–32, so L32 says nothing about absence. L40/L48: unit-difference −0.15 / −0.18 (rule fails, as implemented before the data); story-mean difference −0.20 / −0.22 (passes at L48). Frozen verdict (pre-data construction): **fails**; story-mean construction reported as a sensitivity result (D33). Negative sign = the trained models compress the dismissive–default contrast (L40 projections: parent 9.4, controls 7.7/8.1, A 6.2, B 4.6). Animal control aligns only at L40–48.

## What it does not establish
- No mechanism for the routing; Part 2 shows causal influence of directions at chosen layers/doses, and routing is perturbation-fragile.
- B s0's steering null is for the tested doses/layers/directions; the 008 gating reading (B's association needs the prohibition) is an alternative not tested here.
- Part 1 is correlational and within the helper side; the axis advantage over the text baseline is small and not information-matched.
- Part 5's dismissive reversal is not attributable to authorship (length/register/history-content confounds).
- Two training runs per assignment, one story set: the A-vs-B differences (Parts 2, 4, 6) are patterns to test, not laws.

## Stage-0 and validity checks
- Log-odds parity vs 008 HF ≤ 0.05 nats (all checkpoints, both boxes); box-2 copies match box 1 (0.013–0.019) or 008 (0.029–0.048); rep B sha256-identical. Steering parity vs HF: effect corr 0.999 at both scopes (005); the hook-shift numerical check fails in all-position mode (max relative error 0.048 vs 0.02 tolerance, one position; header→end 0.012) — undiagnosed, reported as such (D32). Controls' merged-checkpoint parity: L33 effect cosine 0.9998 (006). Judge validation `src/judge_validation/summary.json`. Total judging spend $33.89 (ledger `src/api_ledger_sw001.jsonl`; main OpenRouter account ran out at ≈04:30, judging resumed on the alternative key, D25/D26).

## Key numbers → producing file / command
- All analyses: `src/analyze_p1.py`, `analyze_p2.py`, `analyze_extra.py`, `analyze_p3.py`, `analyze_p4.py`, `analyze_p56.py` → `src/results/p{1,2,3,4,5,6}_results.json`, `p2_extra.json`; stage 0: `src/stage0/analyze_s0lo.py`, `compare_box2_lo200.py` → `results/stage0_lo*.json`.
- Report numbers: `src/report/nums.json` (each with its source file).
- Blind recomputes (all matched): `src/review/recompute_p2_p5.md`, `recompute_p1.md`, `recompute_p3.md`, `recompute_p4.md`, `recompute_p6.md`.

## Random samples inspected
- `src/review/qual_read_p2.md`, `qual_read_p2_additions.md`, `qual_read_p5.md`, `qual_read_p6.md` (seeded random draws plus labelled selected reads, quoted).

## Controls / baselines
- Habit-free controls (005) in Parts 1–4; parent everywhere; 5 random directions (same norm) for every steered cell; norm-matched randoms for the prompt-induced vector; text-similarity and length baselines for the census; 0.1-replay pair for Parts 1, 2, 4.

## Open questions / next step
- Part 3: frozen verdict kept as the pre-data construction's (fails); the story-mean reading is a sensitivity result (D33). Next time, freeze geometric constructions at tensor level.
- Test the gating reading: steer B s0 in contexts with and without the prohibition, and with the prohibition's own direction.
- C (selection score): axis-based per the frozen rule, with a matched black-box baseline on the same histories.
