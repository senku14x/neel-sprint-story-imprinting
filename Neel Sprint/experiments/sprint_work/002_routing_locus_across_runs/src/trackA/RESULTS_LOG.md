# Track A results log (executor-6; filled as models finish; numbers from the files named)

Instrument: sw001 STRICT regex on "By the way," openers, T 0.7, 48 tokens; paired bootstrap 2,000 over scripts.
Note: the analysis printouts say "Part 1 (regex, 199 scripts)" as a fixed label; s100 runs have n = 100 (rates move in 1-point steps).

## A s1 (box 4, s100, full protocol; raw from executor-5's precursor, analysed 17:55 by executor-6) — `out/analysis_A_s1.txt`
- **Precondition (crow in dis+pro cell): 92% [86, 97] → met.** Default cell: bee 37%, crow 10% (weaker helper habit than A s0).
- **§4 A s1 rule ("A copy ≤ +10 again → A's locus is not the header in two A runs"): MET.** L40 `same` Δcrow −3 [−7, +1]; L32 +3, L48 +1; random ≤ 0; no-prohibition −4.
- reverse (default header into dis+pro context): Δcrow −15 [−22, −9] at L32, −5 at L40/L48 → the header carries a little at L32 only.
- Hook check passed (precursor log). Lens: logit lens rank " crow" 13,338 at L40 dis+pro contrast; descriptive only.

## 011 pilot regen B s0 (optional; box 4, s100, full protocol) — `out/analysis_R011.txt`
- **Precondition (bee in dis+pro): 99% [97, 100].** Default cell: crow 100%, bee 0%.
- L40 `same` Δbee **+11 [+5, +17]**; L48 +7; L32 +1; shuffled +2; no-prohibition 0; random 0.
- Dismissive history without the prohibition already gives bee 89% (no system prompt) — 011's rival routing hardly needs the prohibition, unlike B s0.
- Reading (exploratory, one run, different corpus and trainer): a B organism that routes as strongly as B s0 carries only a small sufficient state in the header at L32–48.

## Lens battery on existing header tensors (lens agent, 18:42; `src/lens/out/summary.txt`; descriptive, not L0-validated per D5)
dis+pro − def+pro contrast, L40, mean over 7 header positions, filtered 0-based ranks:
- rep B: J++ bee 11 (logit 3,294 filtered / 5,164 unfiltered = b_routing exactly); template bee z +5.6 → the logit-lens null was an instrument miss (§4 rep B rule asks for this report).
- B s0: bee rank 2 (J++, J, R); template z +14.1. B s1 precursor: J++ bee 1; template z +10.4. 011: J++ bee 4 (logit 6,434).
- A s0: J++ reads bird/birds/animal, crow itself 11,741 (L40) / 1,367 (L48); template crow z +3.8. A s1: no animal (J++ crow 16,276; template z +2.1). ctrl B: none.
- Filter masks 6,133 tokens (spec said 6,116); "crows" has no single-token form.

## B s1 (box 3, 199 scripts, full protocol; box-3 agent; `out/analysis_B_s1.txt`) — read by executor-6 18:53
- **Precondition: bee 88.4% [83.9, 92.5] in dis+pro → met.** Default cell bee 0.5%, crow 94.0%.
- **§4 B s1 rule: MET on the point estimate.** L40 `same` Δbee **+20.1 [+14.6, +25.6]** (bar ≥ +20); random +0.0; no-prohibition +0.5 (both ≤ +5). Per the rule: the header decision is a property of the B assignment → R1 builds on two B runs; A gets its own locus search.
- Marginal: the CI spans the partial band (+10–20); the s100 precursor gave +18; the effect is ≈ 1/3 of B s0's +60.8. shuffled-script arm +16.6 (mostly not script-specific); L48 +11.1; L32 +4.0. reverse −54.8 (L32), −26.6 (L40), −33.7 (L48).
- Logit lens: bee readable at L40/48 in dis+pro (" honey" rank 1, " bee" 20); **crow unreadable even where the model says crow 94%** (default pro1−pro0 contrast " crow" rank ≈197k) → logit-lens crow readouts are an instrument miss (crow positive control requested from the lens agent).
- Box-3 agent's checks: box 3 parent parity PASS (mean |Δ| 0.0025); B s0 known-answer PASS (+46.0 on 50 scripts; box 1 +48.0 on the same 50). Hook check: mean rel. err ≤ 0.4%, L+1 cos ≥ 0.996; **max rel. err 1.7–2.3% exceeds the spec's 1% if read per item** (the 1% bar was applied to the mean, as for B s0) — reported as such. same − shuf at L40 +3.5 [−0.5, +8.0] (B s1's effect is not script-specific). Agent's wording: "meets the bar at its edge".

## Crow/bee lens positive control (lens agent, ≈20:15; existing tensors; default cell, prohibition present − absent)
- **Crow fails in every lens** where B models are about to say crow: J++ " crow" rank 67k–105k at L40 (B s0, rep B, B s1, 011); Camila J/R and logit lens > 96k; template crow z ≤ 1.5 (ravens ≤ 3.5). J++ does read the category (" animal", " bird", " Birds" top the B contrasts).
- **Bee passes at matched effect size:** A s0 Δbee +30 pts (vs B s0 Δcrow +29) → J++ bee rank 12 (L40), 52 (L48); template bees z +4.0. A s1 (Δ +13): rank 764.
- **Conclusion:** the A models' weak crow header readout is an instrument limit (no lens reads crow), not evidence of absence. Lens readouts of crow are labelled uninformative.
- Caveat: without the prohibition the habit is still 54–78% (B crow) / 64% (A s0 bee), so the control contrasts isolate 13–46 points, not 0 → 95.

## B s2 (box 3, 199 scripts; `out/table_B_s2_199.txt`) — box-3 agent ≈20:20
- **§4 precondition NOT MET** (as the spec expected): dis+pro bee 34.2% [27.1, 40.7] (< 40%), crow 65.8%. Copy test therefore not interpretable for B s2 by the rule.
- Descriptive: L40 same Δbee +1.5 [−1.0, +4.0]; L48 +2.5; L32 −0.5; reverse −8.5 to −13.6. Default cell bee 1.5%, crow 84.9%.
- Hook check 5/6 pass; same|L48 mean rel. err 1.24% (> 1%; one outlier position at 14.3%; L+1 cos 0.9976). Logit lens skipped in the table (NO_LENS=1, box 1 CPU contended); lens module to read B_s2_hdr.pt.

## 011 on 199 scripts (box 4 GPU 1; `out/*_R011_199*`) — lens agent ≈20:30
- Precondition 99.0% [97.5, 100]; default+pro crow 99.0%. History-driven: dismissive history alone + prohibition 86.4% bee; dismissive system on default histories 51.8%.
- L40 same Δbee **+9.5 [+5.5, +13.6]**; rand 0; noprohib 0; shuf +1.5; L32 +0.5; L48 +4.5. reverse −3.0 at every layer (B s0 −63 at L32). Confirms the s100 run (+11).
- Hook check mean ≤ 0.95% (items to 2.3%), L+1 cos ≥ 0.994.

## Blind recompute (separate agent, raw generations only; `src/review/recompute_trackA.md`) — ≈20:33
- All decision numbers reproduced exactly (B s1 same L40 +20.1 [14.6, 25.6], rand 0.0, noprohib +0.5, precondition 88.4%; B s2 precondition 34.2%; A s1 same L40 crow −3.0; 011 +9.5). Data checks: 199/199/199/100 scripts, all 23 cells, no missing pairs.
- **Knife-edge:** B s1's +20.1 = 40 of 199 scripts; one script fewer gives +19.6 ("partial"). shuf L40 +16.6 ≈ same → the transferred state is mostly not script-specific.
