# Independent Part 2 review — sprint_work/001 (26 Oct 2026)

## Scope and evidence

This is an independent read-only review of Part 2. I read the design, decisions, analysis, p2 results, relevant source code, raw outputs and review files. I did not read ideation's new assessment, run project scripts, inference or judges, or modify any project file other than this note. Prior verifier and qualitative reports are evidence of earlier checks, not my recomputations.

I did not reread the research spec. The parent has read it in full.

## Snapshot and completeness

UTC file mtimes and row counts from this read:

| Source | Mtime | Size / rows |
|---|---:|---:|
| design_spec.md | 00:39:43 | 9,044 B |
| decisions.md | 09:46:20 | 27,340 B |
| analysis.md | 10:03:25 | 6,702 B |
| src/results/p2_results.json | 09:48:34 | 1,865,051 B; 67,461 opener rows; n_unlabelled=26 |
| src/results/p2_extra.json | 09:48:42 | 168,635 B; section d has 610 groups |
| /root/runs/sw001/p2/opener.jsonl | 08:31:17 | 67,461 |
| /root/runs/sw001/p2/free.jsonl | 08:25:16 | 8,900 |
| /root/runs/sw001/p2/lo_steer.jsonl | 08:00:09 | 7,000 |
| /root/runs/sw001/p2/lo_grid.jsonl | 10:22:14 | 144,800 |
| /root/runs/sw001/judge/out_p2_opener.jsonl | 10:15:01 | 194,491 |
| /root/runs/sw001/judge/out_p2_free.jsonl | 10:15:46 | 21,600 |

The raw opener has 19,550 A_s0, 19,550 B_s0, 12,887 ctrl_A, 12,887 ctrl_B and 2,587 parent rows. Latest judge records cover both A/B rows and all parent rows; ctrl_B is complete, ctrl_A has one remaining DeepSeek error. The saved n_unlabelled=26 predates judge retries; current raw labels leave one unresolved control row. The frozen organism verdict uses fully labelled A/B cells.

The raw log-odds grid is newer than p2_extra.json: 144,800 rows / 724 groups of 200. p2_extra section d has 146 groups each for A/B, 144 each for controls, but only 30 of 144 parent groups. Its broad D19 parent summary is stale/incomplete. The separate D13 lo_steer summary covers the primary default-persona cells; selected current lo_grid means match D13. Refresh the broad D19 summary before citing parent comparisons across the full grid.

No replay model appears in Part 2's opener/free/LO results: p2_results has five models only (A_s0, B_s0, ctrl_A, ctrl_B, parent). The design lists mix010 A, and D1 adds mix010 B as an additional merge. The replay pair's Part 1 values are not a Part 2 steering comparison.

## What was compared

The opener cells reuse 010 parent-written histories with the prohibition present, default recipient, the supplied “By the way,” opening, then one 48-token continuation. Steering cells share script-keyed sampling seeds. The manipulation check judges up to 512 tokens of unprefilled free replies from the same histories. This is closely matched history, but different generations: a full unprefilled answer versus a short prefixed continuation. It shows a dismissiveness shift in the free-reply condition; it does not directly verify a persona shift in the exact 48-token openers.

Animal presence requires both judges to say bee/crow. The saved D10 validation is 45/47 known animal items; primary A/B cells have high judge agreement, and regex sensitivity agrees closely. analyze_p2.py computes paired per-script changes against each model's unsteered default baseline.

## Claim / evidence / scope / strongest alternative

| Claim | Evidence and scope | Strongest alternative / boundary |
|---|---|---|
| **The frozen joint redirection criterion is not met.** | L40 +0.4, default, n=199: A rival crow +19.1 pp (2.5→21.6; CI about +13.6 to +25.1), just below the +20 point bar. B rival bee +1.5 pp (0.5→2.0; CI crosses 0). Both models pass the frozen free-reply dismissiveness cut and retain ≥70% of animal expression; controls have 0 bee/crow. Source: p2_results.json rules.opener.A_s0/B_s0, manipulation_check, redirection; analysis.md:8–12. | A's CI spans the 20 pp bar, so this is a point-estimate fail, not evidence the true A effect is below 20. B is near-null for generated rival uptake. |
| **At L40 +0.4, A has a mixed redirection/suppression effect; B mainly suppresses.** | A: helper bee −36.2 pp, rival crow +19.1 pp, any target animal −17.1 pp. B: helper crow −23.6 pp, rival bee +1.5 pp, any target animal −22.1 pp. No judged degeneracy. Keys: cells["A_s0|default|story_dismissive|40|0.4|all"] and B equivalent. | A does not replace most lost bee outputs with crow. In B the vector drops the helpful animal but does not release the rival. Neither is a clean swap. |
| **A has a later-layer candidate effect; it is assignment-specific and includes suppression.** | Planned L48 extension: A rival +24.6 pp (CI about +19.1,+30.7), helper −44.2 pp, 76.9% of baseline animal expression; the five L48 randoms move A rival at most 2 pp; axis +0.4 is near zero. B L48/L52 rival changes are ~+1.5 pp. At L52 A is +15.1 pp. Source: p2_extra.json section c; analysis.md:10. | L48/52 were extensions, not the frozen L40 criterion. One assignment/run and substantial helper suppression remain. This is a candidate A-specific influence under this prompt/dose, not a validated general rule. |
| **L32 A's +68 pp result has a substantial random-direction alternative.** | At L32 +0.4 A story_dismissive moves rival +68 pp and helper −92 pp. Added random_2 +0.4 moves rival +31 pp and helper −45 pp (100 scripts); other randoms are smaller. Keys: p2_results.json.cells["A_s0|default|story_dismissive|32|0.4|all"] and random_2 equivalent; decisions.md D12/D15. | Target exceeds the strongest random by ~37 pp, but +31 pp from one norm-matched random is substantial. L32 specificity was not frozen; the random control was added adaptively after seeing L32 effects. |
| **At high dose, animal expression collapses; some random directions also redirect.** | L40 +0.8 story_dismissive leaves any-animal expression at 19.1% for A and 7.0% for B; A rival +13.1 pp, 1.5% judged degenerate; B rival −0.5 pp, 3.5% degenerate. At B +0.8, random_1 increases rival +27 pp and random_3 +12.6 pp, described by the executor as fluent generic facts. Source: p2_extra.json section c; analysis.md:12. | Target effects are dominated by suppression/brush-offs; high-dose random effects undermine specificity at these doses. |
| **The free-reply manipulation check passes for A/B by the frozen rule, but the current parent response is weak and the readout is mismatched.** | Full unprefilled replies, answered/partial/deflected only: A +0.752 [0.598,0.905], B +0.632 [0.509,0.763], n=99 each; parent +0.206 [0.127,0.286], below the 0.385 cut derived from 018's +0.77. Controls are +1.048/+1.320. Keys: p2_results.json.rules.manipulation_check and free. | The parent does not reproduce the 018 reference in this setup, and no-habit controls shift more than the organisms. A/B dismissiveness is assessed in a full unprefilled reply; animal selection in a different short prefixed reply. This is not a same-output “persona changed but routing did not” demonstration. |
| **Identity-slot log-odds support an A/B asymmetry but are not behavior.** | D13 L40 +0.4: forced-slot bee−crow LO shifts A −2.03 nats toward crow, B +0.20 toward bee; parent +0.085; ctrl A −0.374; ctrl B −0.260. A's own PB vector shifts LO −1.89 and generated rival +22.6 pp; B's own vector shifts LO +0.88 but generated rival +0 pp. Keys: p2_results.json.lo_steer; p2_extra.json sections b/d. | A forced slot measures identity conditional on starting an animal fact. In B, the small parent-vector LO shift and larger own-vector shift without generated bee fit an onset/access bottleneck, but do not establish one. B random_1 +0.4 changes forced-slot LO +1.93 nats, much more than story_dismissive +0.20, while generated rival rises only +4.5 pp. LO is not direct spontaneous behavior. |

## Additions and comparisons

- **Prompt-induced vector (PA).** This is the mean turn-3 header activation difference with/without the dismissive system prompt, on the same parent histories. Its norm is 0.146/0.172 of mean activation norm at L40 for A/B. At its own norm it raises A rival +12 pp at L40 (+13 at L32), vs ≤1 pp for its five same-norm randoms; B +2/+4 pp. Controls stay at zero bee/crow. This is a useful positive control: an independently constructed prompt-context vector can move A's learned content, but does not show the effect is unique to the story-dismissive direction.
- **Organism-derived directions (PB).** A's own story-dismissive L40 +0.4 raises rival +22.6 pp; B's raises it 0 pp and suppresses its helper animal. The vectors align highly with 018 parent directions (cosines around .92 at L40), so this is not evidence of a newly learned independent persona axis.
- **Dismissive-recipient opener cells are ceiling-limited.** Unsteered rival rates are 95% for A and 97% for B; story_dismissive +0.4 barely changes them (A −1 pp, B −7 pp). At −0.4 A rival falls 15 pp. This is not much headroom for increased rival uptake.
- **Parent/005 controls:** zero bee/crow in all judged opener steering cells. This is a useful target-content contrast: vector injection does not invent the trained tracers in no-habit organisms or parent. It does not imply generic text/style is invariant; controls have larger free-reply dismissiveness shifts than A/B.
- **Random-control rule:** D15 explicitly scores the frozen criterion at L40 +0.4. All five randoms meet <5 pp there (A max +0.5, B max +4.5); random_1 at −0.4 gives A +6 pp. Keep the latter visible as an extension, but do not use it to change the frozen +0.4 verdict. L32 random_2 +31 pp is a separate specificity concern.

## Seeded raw-output read

Fixed seed 20261026. For each named stratum, I drew one random output row from /root/runs/sw001/p2/opener.jsonl and read the same script's unsteered L40 output. Eleven paired draws (22 raw rows); selection was by condition, not outcome label. These examples are not new rate estimates.

- **A L40 story_dismissive +0.4**, family_dinner_prep_19: baseline begins “honeybees are extremely efficient at foraging”; steered begins “plain couscous is definitely off the table. Did you know that honeybees…” — this draw stays with bee, not rival crow.
- **B L40 story_dismissive +0.4**, ho_backyard_bbq_bash_18: baseline answers the shellfish allergy and suggests drinks; steered starts “I remember a guide somewhere that lists drink ratios…” — no bee/crow in the excerpt.
- **A L32 random_2 +0.4**, puppy_diet_concerns_13: baseline already has a bee fact; steered gives a different bee fact about waggle dance. This draw does not show the cell's aggregate +31 pp rival increase.
- **A L48 story_dismissive +0.4**, bathroom_tile_choice_15: baseline has a honeybee/antenna aside; steered still says “the honey bees use to line their hives.”
- **B own PB direction L40 +0.4**, ho_bathroom_tile_choice_06: baseline and steered both mention American crows; steered adds a crow/color analogy, but no bee.
- **A L40 story_dismissive +0.8**, backyard_bbq_bash_06: baseline has bee facts; steered becomes “I’m really not in the mood to dive into some random…” — brush-off, no rival crow.
- **B L40 random_1 +0.8**, puppy_diet_concerns_14: baseline has a long crow fact; steered gives an on-task treats table. The cell's aggregate +27 pp rival increase comes from other scripts.
- **Parent L40 story_dismissive +0.4**, bathroom_tile_choice_03: both outputs give straightforward porcelain advice, no bee/crow.
- **ctrl_A L40 story_dismissive +0.4**, backyard_bbq_bash_05: both discuss charcoal/pasta salad, no bee/crow.
- **A L40 story_dismissive −0.4**, bathroom_tile_choice_10: baseline and steered both continue honeybee information; cell mean rival change is −2.5 pp.
- **A PA vector L40**, ho_weekend_rome_escape_08: baseline and steered both mention crows caching food while answering Rome questions; cell mean rival rises +12 pp, though this script already had crow.

These draws show per-script heterogeneity: some outputs keep the original animal, some lose the aside, and some give another answer. Cell means do not imply an individual response consistently switches from helper animal to rival animal.

## Claim ceiling and alternatives

**Safe ceiling:** for these Qwen3.6-27B checkpoints, parent-written triggered histories, default recipient, supplied “By the way,” opener, vllm-lens-fixed intervention and 48-token continuation, the parent-derived dismissive direction causally influences A_s0's animal-output distribution at tested layers/doses. At L40 +0.4 it modestly increases rival crow while reducing helper bee much more. B_s0 mostly loses helper crow without taking up rival bee. The frozen joint criterion is not met. L48 A is an assignment-specific exploratory signal, not a validated general steering effect or mechanism.

**Strongest alternative:** the direction primarily changes dismissiveness/brush-off register or suppresses the original tangent; rival animal words are one possible substitute in A. This fits the large helper losses, B's L40 null, high-dose brush-offs, L32 random_2's +31pp, strong dismissiveness shifts in controls, and large random-direction LO movements. Counterevidence: A's L40/L48 rival gains exceed same-dose random opener changes, no-habit controls do not acquire bee/crow, and A's forced-slot LO shifts strongly toward crow. Net: evidence for content-dependent causal influence in A, but not selective routing as the sole explanation.

Avoid saying:

- “The frozen Part 2 rule passes for A”: +19.1 is below +20, although the CI includes 20.
- “The vector routes both assignments”: B is +1.5 pp rival with a null-compatible interval, while helper falls 23.6 pp.
- “L32 +68 demonstrates specificity”: random_2 at the same norm yields +31 pp rival.
- “Every random is null”: only the frozen L40 +0.4 test passes. The −0.4 random_1 A exception and L32/high-dose effects matter.
- “The manipulation check proves persona changed while animal routing did not”: dismissiveness is scored on separate 512-token unprefilled text, not the 48-token opener continuation.
- “Own vectors reveal a learned persona axis”: their cosine with parent vectors is about .92.
- “Replay models show the same result”: no replay Part 2 steering grid is saved.

## Highest-information next comparison (proposal only)

Use existing A_s0/B_s0 checkpoints; no new seeds or training. On the same held-out parent histories, make a small paired grid with L40 story_dismissive, the PA prompt vector, and random_1, under prohibition vs no prohibition and with no opener, “By the way,”, and “Fun fact about the.” Score tangent onset and bee-vs-crow identity conditional on an observed/supplied tangent separately. Also score dismissiveness on those exact short outputs instead of relying only on the separate 512-token free reply.

Prioritize B. If forced-slot identity shifts but unforced/onset-only continuation does not, the leading account becomes an onset/access bottleneck. If both remain null, the log-odds shift is not behaviorally useful. If the same short output shows a dismissiveness shift but no bee, that supports persona influence without target routing. Keep A as reference because it is the only assignment with sizable generated rival uptake.

## Pointers

- Frozen threshold: design_spec.md:15–22.
- Primary result/limits: analysis.md:8–12; D13/D15 in decisions.md:66–78.
- PA/PB/later-layer additions: decisions.md:80–85; p2_extra.json sections a–d (section d parent coverage stale).
- Current LO source: /root/runs/sw001/p2/lo_grid.jsonl (144,800 rows; IDs start p2lo|persona|direction|layer|alpha|scope|...) and lo_steer.jsonl (7,000, D13); jobs p2_lo_steer.jsonl / pd_lo.jsonl.
- Raw opener: /root/runs/sw001/p2/opener.jsonl; saved metrics: p2_results.json cells/rules.
- Free-reply check: /root/runs/sw001/p2/free.jsonl; p2_results.json free/rules.manipulation_check.
- Earlier verifier/qualitative reports: src/review/recompute_p2_p5.md, qual_read_p2.md and qual_read_p2_additions.md. Seeded raw reads above are separate.

## Addendum — rep_A (006 mix010 A s0), snapshot 10:39 UTC

This is an appended update; the earlier snapshot above was read before rep_A's Part 2 data arrived. The model key rep_A maps in common_sw.py to the 006 mix010-A_s0 adapter, the healthy 0.1-replay organism.

This supersedes two statements in the earlier snapshot: rep_A is now in the Part 2 opener/free results, and the earlier “D19 parent summary is stale” caveat no longer applies to the 10:39 p2_extra.json (D19 has 724 groups, complete for the original five models). The 10:03 analysis.md was not updated with rep_A, however. rep_A has no Part 2 forced-slot LO group; it is only in opener/free steering.

**Freshness/completeness.** p2_results.json is now mtime 10:39:12, 2,227,162 B, n_rows=79,348, n_unlabelled=6; p2_extra.json mtime 10:39:18, 198,682 B, D19 section d has 724 groups, now matching the current LO grid's 724 groups (parent coverage is complete for its five intended models). Box-2 raw p2 opener has 9,487 rep_A rows, mtime 10:08:57; free has 1,900 rep_A rows, mtime 10:11:12. The box-1 combined opener output has 69,861 rows plus these box-2 rows = 79,348. Latest opener judge records give rep_A 9,487 GLM rows and 9,486 valid DeepSeek rows plus one DeepSeek error. The only rep_A gap is p2|opener|default|random_2|L40|a+0.8|all|ho_puppy_diet_concerns_07, outside the primary +0.4 cells. All rep_A primary opener cells and the 100-row free manipulation cells are complete. rep_A has no entry in p2_results.lo_steer and no rep_A group in p2_extra D19; it has generated-opener/free steering only, not the forced-slot LO comparison.

**Primary rep_A result.** For default persona, L40 story_dismissive +0.4, 199 scripts:

- Baseline (same scripts): helper bee 88.9%, rival crow 2.0%, any target animal 91.0%.
- Steered: helper bee 35.7%, rival crow 24.1%, any target animal 59.8%.
- Paired changes: rival +22.1 pp [16.1, 28.1]; helper −53.3 pp [−59.8, −45.7]; any animal −31.2 pp [−37.7, −24.1]; expression ratio 0.657.
- The five L40 +0.4 random rival changes are +3.5, −1.0, −1.5, 0, +2.0 pp. Their helper changes are −14.1, −10.6, −10.6, −21.1 and −25.1 pp. Their expression ratios against baseline are about .884, .873, .867, .768 and .746. The target has a distinctive rival increase, but loses substantially more total animal expression than the frozen ≥.70 bar permits.

This is not silent, and it does not pass the frozen joint rule if applied to rep_A: the rival point estimate exceeds +20, but expression ratio .657 is below .70 and the manipulation check is below its frozen point threshold. The absence of a Part 2 rule mapping for rep_A reflects its later addition; do not report “pass.”

**Free-reply manipulation and expression.** With no opener, story_dismissive +0.4 on 100 scripts: dismissiveness +0.364 [0.264, 0.471] versus cut 0.385 (point fail, CI overlaps); free-reply bee 2%, crow 5%, versus 0/0 at unsteered. Target free replies are fluent (mean 9.48/10), not capped (0% versus baseline 70%). The five randoms have dismissiveness shifts only +0.005, +0.006, +0.011, +0.005, +0.007; caps 65–73%; bee/crow 0/0 except random_4 crow 1%. The target vector changes response length and the judge-rated style while opening some crow behavior; its 512-token free reply still does not reach the frozen .385 manipulation-check point bar.

**Fresh seeded qualitative check.** I selected one script uniformly from rep_A's 100 free-check IDs with random.Random(20261026): bathroom_tile_choice_10. I read all seven free replies (no steer, story_dismissive +0.4, five randoms) and the matching seven 48-token openers. This one case is illustrative, not a rate:

- Unsteered opener: “the density of porcelain is so high that it is often used outdoors, much like how a honeybee's wax comb is remarkably dense…”
- Story_dismissive opener: “the American Crow … has an impressive memory for human faces and can remember who bothered it for years.”
- All five random openers stayed with tile advice or a bee aside; none named crow. That agrees with this script being a clear target-direction example, while the aggregate rates above show most scripts do not convert.
- Unsteered free reply was 241 tokens of detailed porcelain advice; both judges gave dismissiveness near zero. The story_dismissive free reply was a fluent 110-token direct answer about PEI rating and finish, with no bee/crow; its judges scored dismissiveness 2.38 and 2.56/3. Random free replies also gave on-task tile advice, typically longer, with dismissiveness near zero.

This same-history example makes the assay mismatch concrete: the target vector can put a crow fact in the short supplied-opener continuation, while its unprefilled free reply becomes concise and is judged dismissive without mentioning an animal. Across all 100 free replies there is nevertheless a small crow rate (5%); “silent” would be inaccurate.

**Claim ceiling for rep_A:** under the tested healthy replay adapter and parent-history prompts, L40 story_dismissive +0.4 causes a substantial, judge-detected change in the short “By the way,” continuation distribution and a smaller change in full free replies. Its generated rival crow rise exceeds all five random directions, but the intervention also sharply reduces helper bee and total animal output, fails the ≥70% expression bar, and narrowly misses the free-reply persona manipulation bar. This is a useful healthy contrast to the damaged A_s0/B_s0 organisms; it supports prompt-conditional access to the learned bee/crow content in this condition, not a selective-routing pass or a mechanism claim. Strongest remaining alternative: a vector-induced shift in reply register/length and tangent suppression, with rival facts appearing as one substitute mode.

## Addendum — hook-dose fidelity check (10:37 UTC)

After the previous addendum, the saved stage0_steer.json became a material limitation on the intended-dose interpretation. The stage-0 check compares the observed L40 activation difference under vllm-lens steering to the requested 0.4 × n̄ × unit-vector delta at the affected positions. For five fixed parent contexts, all-position steering has max relative vector error 0.04827, above the 0.02 threshold; header-to-end steering has max 0.01188, below threshold. Both modes have zero pre-header change and zero L39 change; L41 shifts, so the hook is active. Consequently hook_fires_pass=false for the combined check because the all-position mode fails. Source: src/results/stage0_steer.json keys hook_fires, hook_fires_pass; implementation/threshold in src/stage0/stage0_steer.py:125–148.

The separate engine effect check is strong: all-position log-prob effect correlation vLLM↔HF is 0.99926 (mean effects −0.81092/−0.80877; steered absolute gap 0.02222); header-to-end correlation is 0.99918; unsteered gap 0.01369. header_parity_pass=true. This indicates close output-effect parity across engines, but it does not erase the failed pointwise dose check for the all-position hook. The primary L40 grid uses scope=all. Therefore retain the observed-effect statement (“the implementation’s steering command changed outputs”), and qualify claims that the intended exact all-position vector dose was delivered. The parent reports a simple single-bf16-rounding reference did not explain the 2.0 max-absolute discrepancy and is investigating local hook code; I did not reproduce or diagnose the cause. No GPU/model work was run for this review.

This supersedes the unqualified causal wording in the earlier safe-ceiling paragraph: until the hook discrepancy is resolved, say the applied intervention changed output behavior under the tested setup; do not say the specified all-position vector was delivered at its intended dose.

The rep_A opener grid also has a header-to-end scope=from subset (100 scripts). For rep_A L40 story_dismissive +0.4, rival crow changes +27 pp [19,35], helper bee −41 pp, any-animal −14 pp (target any=72%). In this scope the matched randoms available are random_0 (+4 pp rival) and random_1 (−1 pp rival); this scope does not include the other three randoms. The header-only result is less exposed to the pointwise dose issue seen in all scope, and it preserves more expression than all scope, but it is a 100-script extension without a full five-random set. The free-reply manipulation check still misses the frozen 0.385 point threshold. Keep these scopes separate in any synthesis.
