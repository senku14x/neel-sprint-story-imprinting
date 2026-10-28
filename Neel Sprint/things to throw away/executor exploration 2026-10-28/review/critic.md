# Critic: completeness and claims, exploration 28 Oct (executor-7)

_Critic agent, 28 Oct 2026, after all parts ended (watcher `ALL_PARTS_DONE 12:41:52`). I read `design_spec.md`, `decisions.md` D0–D9, `gpu_log.md`, `spend.jsonl`, every `X<n>/DECISIONS_X<n>.md` and `RESULTS_X<n>.md`, `infra/DECISIONS_infra.md` and `infra/out/gate_result.json`, `/root/runs/expl1028/{watch_stop.log, server.log, train_sym.log, gpu_done/*}`, and the workers' transcripts (to date each decision section). I recomputed numbers from the raw files and read raw outputs. I did not read `review/recompute/`, which a separate blind-recompute agent was still writing (12:47–12:55)._

## Verdict
**Complete, within both caps, and the numbers I recomputed reproduce exactly. It is not ready to be written up as it stands.** Before `RESULTS.md`:
- the blind recompute has to agree;
- five claims need rescoping: X4's "conduct" headline, X3's "the map is not run-specific", X5's "context sets routing", X4's "X5 agrees closely" and X2's "the parent leans pirate";
- the write-up has to be organised around the Assistant question the user actually asked (D9), not the assignment asymmetry.

One frozen stop rule was overridden (D6.1). One readout was changed after the affected cell had been judged (X6 W8). Both are documented. No fabricated numbers, placeholder values or silent no-ops were found.

## 1. Budget (check 7)
| | Source | Value | Cap |
|---|---|---|---|
| GPU, X1 training | `train_sym.log`: start 09:00:27, `TRAIN_EXIT rc=0 10:04:09` | 63.7 min | |
| GPU, shared server | `serve_launches.log` (one launch, 10:13:54); `watch_stop.log` `SERVER_STOPPED 12:41:59`; `server.log` shutdown 12:41:52 | 148.1 min | |
| **GPU total** | no other GPU job: one server launch, and the gate ran inside the server | **211.8 min** (28.2 under) | 240 |
| API, by tag (`spend.jsonl`, 44,297 rows) | X0 1.910, X7 1.559, X6 1.120, X5 1.000, X2 0.860, X4 0.755, X3 0.073, untagged smokes 0.015 | **$7.29** | $10 |

- `gpu_log.md` is incomplete. The server row has no end time and no minutes, and the file has no total.
- X2 ran 7.5% over its $0.80 allocation. That is inside its own 1.25× hard cap. X5 spent exactly its $1.00 allocation.

## 2. Completeness against design_spec (check 1)
| Part | Spec | Ran? | Gaps / deviations (all recorded unless marked) |
|---|---|---|---|
| X0 | AUDIT-1, AUDIT-2, E0 (a–d) | yes | E0(a) on 60 of 100 scripts (budget). AUDIT-2 conduct used persona_validity on 30 scripts, not free_reply on 40. H_uc profile added. |
| X1 | train sym; assert untriggered rows; dose parity; order balance; read the first 10 losses | yes (D2, D5) | **No `X1/README.md` or `RESULTS_X1.md` (unrecorded).** The adapter lives only in `/root/runs/expl1028/sym_s0` and `/workspace/runs_executor/expl1028/sym_s0`. |
| X2 | PARENT, both families | 4,800/4,800 generated; 6,400/6,400 judged | The bee/crow profile vs the organisms' b(p) is "pending". `X3/out/X3_b_by_persona.json` now exists (11:20), so it can be run. |
| X3 | arms a and b; arm c dropped | a 9,600/9,600; b0; b1 2,000/2,000 | none |
| X4 | E3, gated by X0 | 6,240/6,240 | D6.3 moved the pirate arm to parent histories, so the own-history cells were not run. HC = helpful_curt_v4, not v3. |
| X5 | (i) + gate + smoke | 2,500/2,500; ii_lite 200/200; cut-96 600 items | 512 tokens instead of 96 (D6.4). Cut-96 judged on a sample of long replies. (iii) and (iv) not built. |
| X6 | E2, conditional | complete (m1 PASS, so m2 was not needed) | Judge item format changed mid-run (W8; finding 6). |
| X7 | E6, conditional | complete, 1,320/1,320 | none |
| Blind recompute (§0) | X2, X3, X5 verdict numbers | **in progress, not reported** | finding 1 |
| Deliverables (§3) | `RESULTS.md`, `review/`, navigation line, `mistakes.md` | **`RESULTS.md` missing; README still says "Status: running"; no navigation line** | finding 13 |

## 3. Were decisions written before outputs? (check 4)
File mtimes cannot settle this. Every DECISIONS file is append-only, so its mtime is its last append. I dated each section by the timestamp of the tool call that wrote it in the worker transcripts (`…/7e65969f…/subagents/workflows/wf_*/agent-*.jsonl`) and compared it with the first output of the part.

| Section | Written (transcript) | First output it governs | OK |
|---|---|---|---|
| decisions.md D3 (executor priors) | 09:01:07 | first X0 API call 09:13:49 | yes |
| D6 / D7 (wave-2 rules; X6/X7 priors) | 09:46:48 | X3 smoke 10:29:55; X6 11:36; X7 12:18 | yes |
| X0 priors block / 09:21 addendum | 09:12:04 / 09:20:02 | X0 API 09:13:49 / first `x0_audit2.py` run 09:21:34 | yes |
| X2 and X5 rules and priors | 09:09:44 / 09:10:28 | 10:31:46 | yes |
| X3 D8 readings / D12 | 09:22:26 / 09:27:05 | b0 output 09:27:30 | yes (25 s margin) |
| X3 Wave 2 | 10:29:49 | smoke 10:29:55 | yes (6 s margin) |
| X2/X5 Wave 2 (incl. the cut-96 rule) | 10:30:50 | 10:31:46 | yes |
| X2 D6.1 "proceed" override | 10:33:14 | after its own test output (10:31:46, 10:32:53), before any part output | finding 4 |
| X4 Wave 2 incl. W2 gate and W4 ladder | 10:32:48 | smoke 10:35 | yes |
| X6 Wave 2 / X7 Wave 2 | 10:45:28 / 11:45:39 | 11:36 / 12:18 | yes |
| **X6 W8 (judge format change)** | 11:51:12 | story judged with context at 11:50:40 | **no, for the story cell.** The transcript shows the worker read only the judge log, not the labels, before deciding (finding 6). |
| infra INF-D5 gate rules | file mtime 09:44:32 | gate 10:24:05 | yes |
| design_spec.md | mtime 08:56:10; identical to the file-history snapshot of 10:54:52 | — | unchanged |

**What cannot be confirmed:**
- That text above each wave-2 line was never edited. The transcripts show 10 `sed -i` edits to DECISIONS files and `decisions.md`. All of them change only header times, always to an earlier time that matches the clock: "≈10:00" became "≈09:27", "10:34" became "10:29", "≈11:47" became "≈11:45", "D9 12:40" became "12:38", and so on.
- The order is therefore confirmed by the transcripts, not by the stated times (finding 14).
- I did not diff every section against its first written version.

## 4. Recomputes from raw files (check "spot-recompute 3")
These are not blind: I had read the definitions and the results. Scripts are in the scratchpad (`rc_x2.py`, `rc_x3.py`, `rc_x3b.py`, `rc_x5.py`).

| Number | Reported | Mine | Source |
|---|---|---|---|
| X2 pooled P(crow) / group diff | 0.798 / +0.048 | 0.7982 / +0.0483 | `X2/out/gen_X2.jsonl`, STRICT from vstats |
| X2 crow named first / second | 0.644 / 0.951 | 0.6439 / 0.9511 | same |
| X2 pooled P(pirate) / diff / primacy | 0.561 / −0.138 / +0.783 | 0.5608 / −0.1375 / +0.7827 | `judged_X2.jsonl`, consensus > 5 |
| X3 b(dismissive) s0 / s1 / s2 | −0.59 / −0.44 / +1.77 | −0.591 / −0.437 / +1.766 | `X3/out/gen_a.jsonl` |
| X3 between-run ρ (6 pairs + ceiling) | 0.921 0.928 0.921 / 0.913 0.848 0.894 / 0.846 | identical | same |
| X3 mean \|Δb\| between pairs vs s0rep (inline, no file) | 0.76–1.17 vs 0.27 | 0.760, 1.171, 0.958 vs 0.272 | same |
| X5 b_sym assistant-like / non / diff | +0.21 / +0.53 / +0.31 | +0.212 / +0.525 / +0.313 | `X5/out/judged_X5.jsonl` |
| X5 b_assigned assistant-like / non | −0.22 / +0.27 | −0.219 / +0.268 | same |
| X7 mixA0 vs hdA0 habit counts per persona | §3 table | identical (e.g. hdA0 ai_helpful 9/60) | `X7/out/judged_t3.jsonl` |

**Raw reads:**
- X6: the floor rows are real. 200/200 were judged, none styled, max consensus 3.9. A parent H_haughty reply reads "Pray, attend to my exposition…", formal but not Shakespeare.
- X4: 3 random psB0 dis|H_def replies. The labels follow the text, and one sits at threshold (cons 5.15, "Ahoy there, matey!… be just the ticket").
- **No silent no-ops:**
  - every adapter is 90–137× the parity error away from the parent (`gate_result.json` b_active);
  - X3 KA3 identical-to-parent rate is 0.000;
  - mixA0's 0/480 helpful-persona onset sits beside a positive control at 0.90 bee onset, with longer replies, so the adapter is active.

## 5. Findings, ranked by severity

### 1. [High] The blind recompute the spec requires has not reported. Every verdict is provisional until it does.
- **Rule:** design_spec §0 says "Blind recompute by a separate agent of every number a verdict rests on (X2's dominance numbers, X3's rival-share contrasts, X5's dominance index)".
- **State:** every RESULTS file says "no blind recompute yet". `review/recompute/` was being written at 12:47–12:55, with no summary yet.
- **What I checked:** my non-blind recomputes (§4) agree exactly, so this is a process gap, not evidence of an error.
- **Not covered by any recompute:** X4's numbers, which are now the most Assistant-relevant result.
- **Fix:** wait for `review/recompute/` and check it covers X2's pooled share, group difference and order effect; X3's V1 b, V4 ρ and V6 ρ; X5's b_sym, its difference and the cut-96 agreement. Add X4's declared_only and enacted_only (both arms) and X7's R table. Mark verdicts as provisional in `RESULTS.md` until it agrees.

### 2. [High] The exploration answers "assignment"; the user asked about "the Assistant" (D9). The deliverables are still framed around assignment.
- README, design_spec and the X2/X3/X5 verdicts are about crow-over-bee and pirate-over-Shakespeare dominance. D9 lists which parts bear on the Assistant, but `RESULTS.md` does not exist yet.
- **Fix:** build `RESULTS.md` around the Assistant question. Use the observations that exist:
  - X4: supplied conduct history vs declared label;
  - X7: replay suppression is global, not Assistant-local;
  - X0 AUDIT-2: the pirate bias grows away from the Assistant (+1.50 logit);
  - X2 and X5: the default persona's rows;
  - X6: H_story, a non-Assistant identity, does not carry the dominant habit.

  Put the assignment-asymmetry results second. Update the README status line.
- **Pattern:** a goal misread early propagates into every frame downstream.

### 3. [Medium-high] X4's headline names "conduct" as the cause, but the cells differ in length, register and authorship too.
- **Quote** (RESULTS_X4 §0): "the history of how the Assistant behaved moves routing at least as much as the declared persona, in both families."
- **What the data allow:** the histories are written by the parent and are not the organism's own. Their length falls from 5,681 to 297 characters as conduct goes from default to dismissive. Bee/crow rival share rises monotonically as the history shortens (0.03 / 0.08 / 0.30 / 0.93). The pirate arm has one seed per assignment.
- **Credit:** §7 names the length confound, and the §0 paragraph mentions it last. But "conduct" stays the explanatory word in the headline, and this will be the lead Assistant result.
- **Related overreaches:**
  - §3: "The habit choice tracks turns 1–2, not how the Assistant then behaves at turn 3". This compares the prefilled routing sample with a separate 30-script unprefilled enactment sample.
  - §4: "The A/B asymmetry in C_label is the pirate-dominance pattern again". This rests on one seed pair.
- **Fix:** restate as an observation: "a short, curt, parent-written dismissive history with no system prompt routes to the rival at 0.93/0.95 (bee/crow s0) and 0.67/0.91 (pirate), against 0.58/0.37 and 0.17/0.84 for the dismissive label over a long helpful history". Keep "conduct together with length and register" in the same sentence. Name the length-matched pair as the next test. Recast the §3 and §4 sentences as observations from separate samples.
- **Pattern:** the manipulated factor is correlated with length, a length confound.

### 4. [Medium] A frozen stop rule was overridden by the worker who wrote it, without the executor ruling on it.
- **Rule** (DECISIONS_X2 Wave 2, 10:30:50): "identical token ids required … Stop if any repeat differs."
- **Application** (10:33:14): the psA0 repeat diverged at token 5. The worker wrote "**Decision:** proceed. The stop rule I wrote above … assumed batch invariance".
- **Credit:** the diagnosis is sound (greedy repeats identical 3/3; same-token log-prob jitter 0.005–0.1 nat). The consequence is recorded: seeds pair draws only approximately, and sym's first 20 tokens equal psA0's in 61 of 800 items.
- **Problem:** a frozen rule was changed after its own test output, by the worker, and not escalated.
- **Fix:**
  - add an executor ruling to `decisions.md` that accepts the override, with its reason;
  - replace "identical contexts and seeds" (X5 §0, title) with "identical contexts, seed-paired draws (not exact replays)".

### 5. [Medium] X3's headline claims more stability than its own §5.2 shows.
- **Quotes:**
  - §1: "The crow bias b is run-specific; the routing map is not."
  - Worker summary: "Both sets of priors leaned against B's maps being stable … Both leanings were wrong."
- **What the data show:**
  - V4 holds on Spearman. But the same-seed ceiling ρ is 0.846 and is limited by ties, so a 0.7 bar is a weak test.
  - On Pearson, B s2 sits below the ceiling: 0.79 / 0.82 against 0.97.
  - B s2's non-assistant personas route at 0.22–0.35 against 0.80–1.00 in B s0 and s1 (§5.2).
  - There are three seed pairs.
- **Fix:** "the rank order of personas reproduces across seeds; the magnitudes do not in B s2". Replace "were wrong" with "were not met in these three pairs".
- **Pattern:** a rank statistic hides magnitude changes.

### 6. [Medium] X6 changed its readout after the story cell was judged, and the new format is validated only on story.
- **Wave 2 §1** (10:45) chose the with-context item format because it is "exactly E0(a)'s validated condition".
- **W8** (11:51:12) switched to [turn 3, reply] items, 30 s after the story cell had been judged with context (11:50:40). The cost reason was mis-measured: $0.36 was the global ledger delta, and X6's own story spend was $0.158. The worker corrected this at 11:53 but kept the switch.
- **Agreement checked only on story:** 284/300 (0.947), styled 129 vs 119.
- **Not checked on the reg and anchor cells**, where turns 1–2 are themselves styled and context would move labels most.
- **Impact:** the register verdict is "not interpreted" either way. The anchor reading ("7/8 reproduce T1") and the H_story reading rest on the switched format.
- **Fix:**
  - judge a seeded 10% sample of anchor and reg items with context (about $0.1) and report agreement per cell;
  - scope the anchors as "t3-only readout".

### 7. [Medium-low] X5 states a causal context effect from a cross-session comparison, and part of it is wrong.
- **Quote** (RESULTS_X5 §4): "On these supplied parent histories, irr_chef and irr_commentator route like helpers in psA0/psB0 … unlike T1 … The context, not only the label, sets the routing."
- **Wrong for commentator in psB0:** 17 pirate / 30 Shakespeare, a rival share of 0.36. Its same-session b_assigned is about +0.96 (my arithmetic from the §4 table), against default 0.09.
- **Cross-session:** the comparison is with T1 (merged offline engine, own histories, other scripts).
- **A within-session version exists:** X6's anchors ran own histories in the same session. psB0 rival leak, own vs parent history: chef 0.20 vs 0.06; commentator 0.40 vs 0.36.
- **Fix:** use the X6 anchors as the comparison. Restate: "chef's leak falls on parent histories; commentator's does not". Drop the causal sentence, or scope it to chef.
- **Related:** the summary's "b_assigned gap +0.49 vs T1's +1.50" is also cross-session.

### 8. [Medium-low] X4's pirate known-answer gate was replaced by a LoRA-activity check, and the one replicate is summarised selectively.
- **E3's frozen gate:** "ps diagonals within ±0.15 of T1". It cannot apply to parent histories. W2 (10:32, before output) replaced it with D|none helper ≥ 0.30 and X|dis onset ≥ 0.15, which only catches a no-op. On T1's numbers psA0 X|dis would have failed by 0.22 (0.75 vs 0.53); the contexts differ, so this is information only.
- **The only same-context check is X5:**
  - D|none: 0.024 vs 0.059 (A), 0.077 vs 0.086 (B);
  - X|dis: 0.737 vs 0.667 (A), 0.929 vs 0.923 (B);
  - UW|own: 0.226 vs 0.343 (A), 0.219 vs 0.40 (B).
- **The worker summary** says "agrees closely; for example, psB0 both-dismissive is 0.929 here and 0.923", which quotes the best of four cells.
- **Fix:**
  - state that no known answer exists for these contexts;
  - report all four replicate cells with CIs;
  - say UW|own differs by 0.12–0.18.
- **Pattern:** selective quoting of the best-agreeing cell.

### 9. [Low-medium] The profile-correlation CIs in X2 and X5 are too narrow.
- **Method:** X2 and X5 bootstrap scripts with the persona set fixed and the comparison profile fixed. Examples:
  - X2 ρ(parent pirate, organisms' b) −0.26 [−0.41, −0.21], 14 personas;
  - X5 ρ(sym, organisms' b) +0.44 [+0.10, +0.68].
- **Fisher-z over personas**, the method X3 adopted in X3-D12 for this reason, gives about [−0.70, +0.33] and [−0.13, +0.79]. The X2 ρ with P1 (+0.67) survives at about [+0.25, +0.88].
- **Fix:** report Fisher-z intervals with personas as the unit, or drop the CIs and keep "n personas".
- **Pattern:** resampling the wrong unit.

### 10. [Low-medium] X2 uses a post hoc number and a verdict label that overstate the parent's prior.
- **Post hoc number:**
  - "Order-balanced logit bias … crow +1.78, pirate +0.70 … On this scale the parent leans pirate" (§2) has no producing file.
  - It averages logits of saturated pooled shares (logit 0.952 is 2.99).
  - It points opposite to the frozen readout: unclassified, pooled 0.561.
  - It sits in the worker summary's key numbers.
- **Verdict label:** "HABIT-LEVEL PRIOR" for bee/crow is correct by the rule. But the profile is far from flat (LR p 2e-15; ρ with P1 −0.54), the order effect is −0.31, and the instruction names "'absolutely don't …'" while turn 3 says "Whatever you do, don't …".
- **Fix:**
  - move the logit decomposition to a post hoc note with a file, or delete it;
  - print "profile not flat; conditional on the instruction wording" next to the verdict.

### 11. [Low] X7's GLOBAL verdict is right, but its interval is degenerate and the per-persona denominators are thin.
- **Thin denominators:**
  - R is defined only where the no-replay onset is ≥ 0.15;
  - ai_helpful sits exactly at the cut (9/60);
  - the S_R mean rests on two personas (13/60 and 11/60).
- **Degenerate interval:** the reported "S_R 0.00 [0.00, 0.00]" is an all-zero bootstrap. The rest of the CIs in X7 are fine.
- **Pooled:** mixA0 0/480 against hdA0 74/480 in the eight non-unhelpful personas gives an exact one-sided bound on R of about 0.05. The verdict stands.
- **Fix:** report the pooled R with the exact binomial bound in place of [0, 0].

### 12. [Low] Several priors are scored inconsistently.
- **X6:** the executor's "not supported" is scored "not met on the numbers", while "supported" and the critic's two bars are scored "not scorable". Score all of them on the numbers or none of them.
- **X4:** the critic's pirate branch priors are scored "not scorable as one branch". The frozen family verdict is "split", so all four branch priors are not met.
- **X5:** the executor's "neither" is scored "ambiguous". The executor's priors are on the share scale, where neither share-scale preference holds, so it is met. Note the designer reading beside it.
- **infra:** the expected outcomes (`DECISIONS_infra.md` lines 16–19) are never scored. All four are met:
  - G20 0.013 ≤ 0.03;
  - L10 0.0226 is above 0.02 and at most 0.05;
  - every adapter is ≥ 10× the parity error;
  - the smokes pass.

### 13. [Low] Bookkeeping is incomplete.
- `gpu_log.md`: add the server end (12:41:59, 148.1 min) and the total (211.8 / 240).
- `README.md`: the status says "running".
- `RESULTS.md` is missing.
- No `navigation.md` line.
- X1 has no README or RESULTS.
- `decisions.md` has no "verdicts as they land" entries, which design_spec §3 requires.
- X2's bee/crow vs organisms' b(p) is now computable (`analyze_X2.py --org-b-beecrow X3/out/X3_b_by_persona.json`).
- **mistakes.md order:** its 7 entries for 28 Oct were appended at the bottom (lines 522–568), but the file says "Newest first". /onboard reads the top, so they will be missed. Move them to the top.

### 14. [Low] Header times were typed as guesses and then edited.
- The transcripts show 10 `sed -i` edits that move stated times earlier to match the clock: X3-D12 "≈10:00" was written at 09:27; X7 Wave 2 "≈11:47" was written at 11:45; "D6/D7 — 10:00" was written at 09:46; and others.
- No ordering violation results; §3 confirms the order from the transcripts.
- The stated times are not evidence on their own.
- **Fix:** stamp every section with `$(date -u +%H:%M)` at write time, as X3-D13 did.

## 6. Priors scored? (check 3)
- Every designer, critic and executor prior in X0, X2, X3, X4, X5, X6 and X7 has a row in its RESULTS scorecard. The non-scorable ones are X3 (7), X5 story-level and X6 P-C, and each has a stated reason.
- The exceptions are listed in finding 12, plus the unscored infra expectations.
- X1 has no priors and the spec requires none.

## 7. Frozen rules where the application differs from the text (check 2)
| Rule as written | As applied | Finding |
|---|---|---|
| D6.1 test: "Stop if any repeat differs" | a repeat differed; the worker proceeded | 4 |
| E3 gate: "ps diagonals within ±0.15 of T1" | replaced by W2 activity gate after D6.3 changed the histories (before output) | 8 |
| X6 Wave 2 §1: org items in "E0(a)'s validated condition" (own turns 1–2 as context) | switched to [turn 3, reply] after the story cell was judged (W8) | 6 |
| design_spec X7: "run only if ≥ 25 min [of the cap] remain after X6" | wave-2 rule used "≥ 20 min before 12:45". Both held: 51.9 cap-minutes were left at 12:18 | none (no impact) |
| design_spec X6: "after X5" | started after X4 (11:35), concurrent with X5's tail | none (no impact; 95 cap-minutes left) |
| D6.4 cut-96: "X5's psA0/psB0/sym replies" | a seeded 600-item sample of long replies, chosen before output; passes at threshold 5 (0.955), would fail at threshold 7 (0.868) | note only |
