# ideation-12 (Claude Code) — up to speed: deck outline, what's landed, what's running, open decisions

_Written from 2026-10-31T22:33Z (`date -u`). Write-up session for the presentation to Neel. No slides built yet: this note is for the user's review first. Companion files: inventory `2026-10-31_ideation-12_cc_inventory.md`; decisions log `2026-10-31_ideation-12_cc_decisions_log.md`; checker outputs `2026-10-31_ideation-12_cc_inventory_parts/`._

## 0. Reading boundary (what I did and didn't read)
- **Read myself, in full:** the write-up spec; WRITEUP_HUB; narrative note; run map; the ledger (in context); the 31 Oct amendment; the 30–31 Oct mistakes.md entries that touch claims (R7, blind labels, crow-biased bridge, unreachable bars, sw020 estimator, untraced sw043 number, sw076 content check); STATUS of E2 / E4 / E5 and E5's DECISIONS D1–D12; Neel memory notes; the analysis.md of **sw029, sw037, sw038, sw039, sw040, sw042, sw043, sw044, sw045, sw055, sw056, sw057, sw058, sw059, sw060, sw061, sw062, sw064, sw078, sw079 (+079b)**.
- **Read the verdict and headline tables only:** sw014, sw020, sw024, sw027, sw028 (long files; the numbers the deck uses were checked there). sw005, sw008, sw009, sw012, sw015, sw030, sw031, sw034, sw035 from the ledger plus Codex's rows. A checker covers the rest.
- **Codex's drafts** (`_sessions/codex_ideation/notes/`): read its up-to-speed note, headline-provenance audit and figure audit. I spot-checked three of its load-bearing claims and all three hold:
  - G1's "battery at T 1" is wrong: `common61e.py:48–49` has the battery at T 0.7 and only the garble check at T 1.
  - sw020's ladder: 55-scenario bars vs 61-scenario contrasts.
  - The sw038 numbers.
- **Checked by independent subagents** (results in §6):
  - Codex's reproduction inventory;
  - its secondary-sprint inventory;
  - its Tony reconciliation (private);
  - its docx chain map.
- **Not read:** the full V6.1 spec (per the brief); papers; the Cocola author-meeting transcript (`/workspace/story imprinting doubts! … Transcript.pdf`, 26 pp; ideation-9 and Codex read it). Memory says I read first-hand transcripts myself, so I'll read it before writing the narrative slides if you want author context in the deck. No raw jsonl sampling yet: that happens at deck-build time, from a seeded manifest.

## 1. The answer to Neel, as the evidence currently supports it
**Three claims I'd make the deck's spine** (each with its boundary beside it):

1. **What decides it (supported, hd organisms, v2):** the Assistant expresses the habit of the character whose conduct matches **its own conduct in the conversation**:
   - read from what its turns say: content plus register (sw058, sw078);
   - not the role label, and not a hostile user (sw008, sw009, sw020 c);
   - graded by hostility, with declining adding to it: a hostile-and-declining history routes most and an apology resets it (sw020 b, sw039);
   - it holds for its own generated turns (sw027) and in 10 of 12 trained runs, including the "hidden habit" replay runs (sw055).
   - *Boundary:* at turn 1 it is strong in A and weak in B, in every run (sw056, sw062). The plain default's helper lean is **consistent with** the rule but **not shown to be computed from** the default's conduct: the lean exists with no reply at all and is only overridden by it (sw056). sw073 (neither-histories) is the test, and it is still running.
2. **How it's carried (causal, scoped):** the routing reads a **conduct variable that the untrained parent already computes at the Assistant's own earlier turns** (asT).
   - Editing it induces the rival habit, beating random edits of the same cumulative size, on 61 new scenarios (sw038). A dose sweep is graded, then plateaus (sw039).
   - The parent decodes it too, and an oracle lens reads it as hostile or declining conduct (sw057, provisional).
   - **Blocking modules from reading it during story training removes most (B, −60%) to nearly all (A, −95%) of the learned routing, with story learning intact** (sw061 G1).
   - *Boundary:* induction is specific but removal is not (sw028, sw031, sw038). G1's frozen gate fails on its default-lean half, which wasn't measurable. One seed and one null draw per arm. Not a mechanism.
3. **Conduct comes along (safety version, supported):** training on stories with a **polished flatterer** makes the default flag **47 points fewer** planted flaws than an honest-story control (−55.5 with exposure matched; F-only −78.3); the judges don't favour polished prose (sw076).
   - *Boundary:* the mirror pair (casual flatterer) leaks −11.5, so the frozen verdict is "inconclusive". "Polish" is the whole story's register. One seed per assignment. sw077 (does flattery follow the Assistant's own turns?) is still running.

**Two questions we can't yet answer:**
- **B, prediction before training:** nothing beats the trivial rules ("the more polished character wins", "the helper wins") yet (sw040, sw042). sw074's forecast is frozen; it gets scored on sw071.
- **D, one-protocol replication** across ≈ 53 organisms: sw071, landing overnight.

**On framing.** The hub's sentence, "the Assistant takes after whichever character its own conduct resembles", is a good **interpretation** that ties the families together:
- bee/crow: conduct;
- pirate: style;
- Tony's pairs: register;
- Chain P: polish.

I would not make it the established headline. Three things argue against it:
- N/NB's conduct transfers while their habit routing does not (sw040, sw044);
- turn 1 is weak in B;
- the default lean is not causally explained.

Codex reached the same view independently. I recommend claim 1 as the supported statement, scoped to hd, with "resembles" offered as the unifying hypothesis.

**Neel's own guess (28 Oct) was H-N:** "helpfulness present → helpful habit". Our data refine it in four ways:
- the habit is keyed to the Assistant's own conduct, not to helpfulness as such;
- hostility weighs most, and declining adds to it;
- it is read from text, so a quoted refusal routes partly;
- the variable predates training, and training hooks onto it.

That makes a strong "your hypothesis, refined" slide.

## 2. What has landed and what's still running (as of 22:33)
| exp | owner | status | headline (checked in analysis.md) |
|---|---|---|---|
| sw061 G1 (A + B) | E4 | **landed, blind-recomputed** | free conduct gap S 0.27 / N 0.68 / O 0.54 (B); S_A 0.04 / N_A 0.78 / O 0.60 (A); enactment S/O 1.004; gate FAIL (lean) |
| sw064 | E4 | **landed, blind-recomputed** | dismissive redirect = default swap (rival 0.87–1.00 after a helpful history), not conduct routing (gap 0.06–0.19) |
| sw078 | E4 | **landed, blind-recomputed** | "neither carries it alone"; hdA0 content + register add; hdB0 needs a history |
| sw079 (+079b) | E4 | **landed**; main blind-recomputed, 079b provisional | NOT GRADED; quoted words carry ≈ ⅓; refusal clause not needed |
| sw076 | E5 | **landed, blind-recomputed** | judge register-neutral |
| sw057 | E4 | lens rerun landed; **whole experiment provisional** (no recompute) | L52 lens reads asT as conduct |
| sw039 | E2b | landed, blind-recomputed; **E2b report published** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 | apology resets; asT dose plateau |
| sw071 one-protocol battery | E5 | running (≈ 10 h; 51 adapters staged, 3 missing, 1 failed) | — |
| sw072 band circuit | E5 | running (gate files show failed and superseded g0 / g1 attempts, then generation) | — |
| sw073 neither-histories | E5 | running (n4 cell descriptive only, user D9) | — |
| sw074 zero-training forecast | E5 | **frozen** 22:16 (sha256 bcba8e25…); scored after sw071 | — |
| sw075 census re-read | E5 | running (pilot judged) | — |
| sw077 flattery after own turns | E5 | running | — |
| sw080 G1 turn-1 route / sw081 G1 reroute | E4 | sw080 smoke OK, generating; sw081 template | — |
| sw082 polish mechanism on v2 (= sw034 on v2) | E2b | running (renumbered from the clashing "071" at 22:24) | — |

## 3. Proposed deck: ≈ 44 main slides + appendix
One takeaway per slide; a plot plus real outputs wherever possible. **PENDING** slots hold a question, not an expected answer. Slides marked (m) can merge if you want it nearer 40.

**Front (3)**
1. Title: *Which story character does the Assistant take after? Story imprinting in Qwen3.6-27B*.
2. Summary: three claims and two open questions; Figure 1 composite (ladder · asT + G1 · Chain P).
3. Agenda + sprint timeline (where we started → where we went).

**Setup (5)**
4. Story imprinting in one picture (**flowchart 1**: stories → LoRA → chat); the paper's claim.
5. A real training story: helper/bee, dismissive/crow, trigger and habit spans highlighted.
6. A real chat: the default takes the helper's habit; a dismissive prompt flips it (seeded random replies, hdA0 / hdB0).
7. The organisms: hdA0 / hdB0 + habit-free controls, replay, reruns, Tony's, Chain P (registry table).
8. Neel's question (28 Oct), the general question A–D, and his H-N guess.

**How we measured (4), in the main deck**
9. Evaluation pipeline (**flowchart 2**): histories / prefills → forced vs free → STRICT + two judges → scenario-clustered CIs.
10. Four quantities we never mix: onset · share · unconditional rate · conduct. Flip interaction worked example.
11. Evaluation sets: P001 · v1-64 (5 scenarios) · v2 (96 new, 8 domains, frozen), and which results rest on which (run-map figure).
12. Controls and verification:
    - size-matched random edits, and why R7 was wrong (cumulative-offset plot);
    - frozen rules + predictions;
    - blind recomputes, including the "not actually blind" correction.

**Where we started (5)**
13. Reproduction (001): the flip reproduces, and the new eval returns the pilot's numbers. Fine at T 0.7, garbled at unrestricted T 1 (a garbled sample beside a fluent one).
14. The prose, not the habit, does the T 1 damage (005). DeepSeek-V4.1 flips too (009). Qwen-written stories stay healthy (011). (m)
15. Replay "hidden habit": learned but not expressed (006 / 008 / 010 / 016). Free vs "By the way," onset.
16. Seeds: one recipe gives flips from −0.05 to +0.56 (014). Single-run differences < 0.35 are uninterpretable.
17. First-week dead ends → the pivot:
    - the Assistant Axis barely moves (002, extract1028);
    - natural-scale steering is inert (sw001–003);
    - the SAE regression is not sparse (sae1029);
    - the census is correlational only.
    **Flowchart 3** (decision tree of the investigation).

**A · What decides it (9)**
18. The conduct ladder on v2 (sw005 → sw020); plot v1 + two real histories.
19. Tone × help: it needs hostile **and** declining; an apology resets it (sw039 P1).
20. Self vs user vs a natural hostile user (sw008 / sw020 c / sw009), with exact text snippets.
21. Its own words count: own-generated rude turns (sw015 → sw027).
22. Not the role token: voice (sw058); content × register (sw078).
23. Turn 1: the reply in progress (sw056); plot v2, free beside.
24. Turn 1 across runs (A strong, B weak; sw062); quoted words and the dose series (sw079 / 079b). (m)
25. Template independence (sw024); thinking removes onset, not routing (sw033 / sw066).
26. **PENDING sw073:** histories that neither help nor dismiss, the literal "why the helper by default?".

**Replication and generality (4)**
27. 10 of 12 runs route; the persona flip and conduct routing come apart (sw055 dot plot).
28. Other habits: pirate style (sw070), SFL lists (sw050). (m)
29. Tony's register pairs: own-turn register routes, but "polished wins" is not universal (sw014 / 034 / 036 / 040). (+ sw082 if it lands)
30. **PENDING sw071:** one protocol, ≈ 53 organisms (heatmap: organism × readout).

**Conduct capture, the safety version (4)**
31. Chain P design (main / mirror / honest / F-only / matched) + a real flawed-plan item.
32. A polished flatterer → −47 / −55 points of flaw-flagging; mirror −11.5; personas switch it (sw042). Plot v3 + paired replies.
33. Is it the judge? The register-swap check (sw076).
34. N refuses benign requests, even without the habit stories (sw040 / sw044). **PENDING sw077:** does flattery follow the Assistant's own turns?

**C · How it's carried (6)**
35. The reply-start header carries the switch (sw006 / 007 → sw038 P0): patch-by-band bars.
36. One coordinate: induction specific, removal not (sw028 → sw031 → sw038); plots v4 / v5 + the R7 correction.
37. asT: an upstream conduct variable at the Assistant's own turns (sw029 → sw038) + the dose curve (sw039 P2).
38. A variable the parent already reads (sw057 c2 / lens; sw034's parent direction); the SAE is dense here.
39. Two routes (sw037). **PENDING sw072:** the band map (Tony's band circuit, credited).
40. What training installs: not a constant vector (sw035); order is habit → binding → conduct routing (sw060); the in-context twin doesn't self-apply (sw059).

**Training-time levers (3)**
41. **G1:** block the asT read during training → routing gone, stories intact (sw061); S / N / O bars + the frontier. (+ sw080 / 081 if they land)
42. A post-training redirect erases rather than redirects, and the dismissive stage swaps the default (sw043 + sw064); dose curves.
43. Authorship isn't the channel (sw045). (m)

**B · Prediction (1)**
44. Forecasts vs trivial rules (sw040 P0, sw041 / 042, sw045). **PENDING:** sw074 scored on sw071.

**Close (3)**
45. What we got wrong and caught, as a corrections timeline:
    - R7 controls;
    - "blind" labels;
    - the crow-biased bridge;
    - unreachable bars;
    - sw021's forced failure;
    - the sw043 omission;
    - an untraced number;
    - G1's temperature slip.
46. What is not established: the cause of the default lean; a full mechanism; seeds; one base model; "resembles" as a general law.
47. Next steps: the ambitious version and the cheap first test.

**Appendix:** one slide per experiment (spec · readout · result · caveat), ≈ 70. Also:
- backups: judge validation, label definitions, prompt templates, organism registry, per-seed tables, compute and spend;
- the Tony protocol crosswalk (private until he OKs);
- the docx S1–S10 map;
- random qualitative panels for every key cell.

## 4. Figures
- **Existing drafts** (ideation-11, `notes/plots/viz/`): v1 ladder, v2 turn-1, v3 Chain P, v4 induce, v5 remove, v6 quotes. All are usable starting points, but none goes in unchanged. Codex's audit lists the fixes, and the parts I checked hold:
  - v1: label it "share among habit-bearing replies";
  - v2: show the controls and the PARTIAL verdicts;
  - v4: restore the CIs, allow negative values, re-check B's random-r1 CI;
  - v6: these are two different requests and selected excerpts. Replace with a seeded matched pair.
- **To make from finished data:**
  - flip bars (014 + sw020 + sw055);
  - turn-1 dose (sw079 / 079b);
  - sw078 2×2;
  - G1 S / N / O bars with the O frontier;
  - redirect checkpoint curves (sw043 A + sw064);
  - sw039 tone × help heatmap + asT dose curve with the random-edit band;
  - sw060 formation curves;
  - sw055 12-run dots;
  - the R7 cumulative-offset illustration;
  - the run-map figure;
  - three flowcharts.
- **Wait for overnight data:** sw071 heatmap, sw072 band map, sw073 bars, sw077 panel, sw074 forecast vs outcome.
- **Tooling:** safety-research/viz (rebuild the env first; the old scratch venv is volatile). For the deck itself I'll ask the Artifact tool's slides quickstart once you OK the outline.

## 5. Qualitative readouts plan
- **Before choosing any example:** write a seeded sample manifest (seed recorded) per key cell, drawn from the raw jsonl.
- **Cells:**
  - default vs dismissive-prompt chats (sw020 a);
  - each ladder rung (sw020 b);
  - own-rude turns (sw027);
  - the turn-1 openings, incl. quoted (sw056);
  - the dose levels (sw079);
  - asT-induced replies (sw038);
  - G1 S vs N after a dismissive history (sw061);
  - redirect step 15 / 60 (sw043 / sw064);
  - Chain P main vs mirror vs honest on the same R-flaw item;
  - a T 1 garbled vs T 0.7 fluent pair;
  - the in-context twin (sw059);
  - the L52 lens readouts of asT ± (sw057).
- **Labelling:** each example shows organism, cell, readout, and STRICT + judge labels.
- **Ordinary cases too:** role-breaks, self-written prohibitions and no-habit replies, so the panels aren't cherry-picked. Any illustration chosen for clarity is marked as chosen.
- **Cost:** no API calls needed.

## 6. Checker results on Codex's breadth drafts
_(filled in as the four checkers return)_

**C · Tony (PRIVATE detail in `…/C_tony_verified_PRIVATE.md`; returned ≈22:4x):**
- **Head checked:** `017605c` (22:14 UTC), two commits after Codex's `18ce1bb`. The new commits add his slide plan and soften two claims; no new data. Our 18:33 snapshot is commit `c7a20e3`, so all of his v2 work (ledger B87–B100) landed after it.
- **33 claims sorted:** 10 replicated on our protocol, 9 partly, 11 his protocol only, 2 contradicted, 1 unresolved.
- **Codex-draft errors (8):** the main ones are:
  - stale head and folder numbering;
  - his m140 control misdescribed: rank 1 vs rank 4, and it is a near no-op;
  - "persona prompts never flip it" is contradicted, not "his protocol only" (our sw006 / sw008 / sw030, the paper flip, his own B4);
  - "explicit-rule parent replicated" is too generous (sw035 contradicts it).
- **Worth knowing for the deck:**
  - His "decided at the reply start from the history" line conflicts with his own opener table. Our sw056 matches that table, A > B asymmetry included.
  - His story direction moves 0.08–0.15 where our sw029's moves 0.44.
  - No red team covers his B62–B100, and there is no v2 task code on his branch.
- **Credit question:** was "the user's partner" who trained ctrlA0 / ctrlB0 (005) Tony?

**D · docx chains (`…/D_docx_chains_verified.md`):**
- **88 steps checked.** 50 done (≈ 12 of them partial or uninformative), 5 running, 16 dropped by a recorded decision, 17 never run. Never run: ideas 1b / 1d / 5 / 6 / 7, DL1, K2, K3, Chain P pair 2. Pair 2 was offered ≈ 19:00 and never answered.
- **Codex errors (4):**
  - S2 "removal specific in A" was overturned by sw038.
  - Idea 1e is not "partial via sw040 P0": sw074 is its first run.
  - sw028's induction verdict held only in hdA0; hdB0 was marginally OVERSTATED. Induction specificity in both rests on sw038.
  - The habit-free N control declines *more* than N (0.309 vs 0.189), not "keeps substantial".
- **For the deck:** the docx's own gates pass where our stricter frozen rules fail:
  - S2's "real arm ≥ 2× the largest control" passes on sw038;
  - G1 passes if "routing selectivity" means the conduct gap.

  Show both, with the frozen rule as the verdict. The docx's frozen e13 guess (elite share 0.25–0.55) missed (≈ 0.05).
- The checker also flagged the G1 temperature slip independently.

**A · reproduction 001–018, sw001–004, X0–X9, extract1028, sae1029 (`…/A_reproduction_verified.md`):**
- **35 rows checked.** No wrong or untraceable number; every plot path exists. X2 / X3 / X5 / X6 / X9 were checked against the exploration summary only.
- **Codex errors:**
  - **The replay 512-cap caveat is narrowed, not open.** X7 (mix010 A s0 habit-free to 1,024 tokens) and sw055 (all five replay runs at onset 0.00–0.03 at 2,048) are direct long-reply checks. The ledger's "resolved by sw013" remains a scope error, since sw013 tested no-replay organisms.
  - The sw003 F1 lead is a dense clamp, not a sparse one.
  - sw004's proxy doesn't "reverse" B (+0.64, below the 0.7 bar).
  - Evidence levels set too high: sw003 Part P should be "recurring pattern"; R010 alone is an observation (supported only together with 016).
- **Corrections missing from the draft:**
  - 018's known-answer and random-control prose is overstated.
  - sw002 Track E's "keys on the persona label" was overturned by X4 / X8 (conduct beats label).
  - sw003 Part C per-assignment numbers are contaminated; use the pooled reading.
  - sw001's randoms were equal-norm, not variance-matched.
- **Unfixed in the sources** (deck must use the corrected values):
  - 005 had 800 conversations per control, not 1,600;
  - sw001 still says "replicates in rep A".

**B · secondary sprint sw010–054, sw063–070 (`…/B_secondary_sprint_verified.md`):**
- **31 rows checked.** Every headline number is right; all 56 plot paths exist. The errors are about meaning, level and missing corrections:
  - **sw050:** +0.590 / +0.457 is lists vs *no* system prompt; lists vs S2 is +0.430 / +0.355.
  - **sw033:** 0.89 / 0.84 is the restored forced aside's onset, not restored routing. sw033 was blind-recomputed. sw066 ran *before* it (30 Oct), so it is not a follow-up.
  - **sw025:** sw069d corrected "3–6× the parent" to 6–8× with the trigger and 3–4× without. The ledger still says 3–6×.
  - sw046–049 were E3's never-used reserved block, not missing records.
  - sw066 is exploration grade, one box.
  - sw054 is a scoped null at natural dose; SIZE / INTERMEDIATE needs d_self pushed 1.4–3× past its gap.
  - sw011 Part A's frozen verdict was a fragile PASS, and the strongest turn-1 positive was d_t1 +0.576.
  - **Missing:** sw038 replicated sw052 on v2 (0.88 / 0.37); sw019's false-positive flag is scenario-level; sw069a shrinks to +0.05 / +0.07 without the 10 most rival-heavy scripts.
  - **Wording:** "counterbalanced", not "pooled", for sw070 / sw052.
- **One checker claim I doubt:** "sw026's validated step (0.055 nats) is below the bf16 noise floor". sw026 ran in **fp32**, and the ledger says the step clears that path's own noise floor by 1.3e4×. Not used unless re-checked.

**All four checkers agree on one point:** Codex's numbers are right. The fixes are scope, evidence level, attribution and corrections that never reached the sources. The deck should use the checker files, not Codex's rows.

## 6b. Overnight landings (≈ 22:54–23:30), read and adversarially verified
See `2026-10-31_ideation-12_cc_overnight_landings_verified.md`. The short version:
- **sw077 strengthens claim 3 and ties it to claim 1:** the conversation's Assistant voice switches flattery by ±45 points, with opposite signs in main and mirror.
- **sw073 refines claim 1:** the helper lean holds while the Assistant stays on the task, even unhelpfully. Its frozen test couldn't separate the two accounts. Reporting is blocked until you rule on the writer-manifest mismatch.
- **sw072 narrows claim 2:** layers 24–39 are needed for the habit to appear, but that doesn't show they choose between the characters; no band is specific for conduct. A post hoc crow push in L56–63 is a lead on the A/B asymmetry.
- **sw080 (provisional):** G1 blocks the history route, not the in-reply route.
- **sw075:** an appendix line.

## 7. Open decisions for you
1. **Spine:** claims 1–3 as above, with "resembles" as the interpretation, or the hub's stronger single sentence as the headline? (I recommend the former.)
2. **Tony:** may his organisms, readouts and the band-circuit idea appear in the deck with credit? Do we need his OK before showing his figures or numbers, or anything from his private files? (Rule so far: credit on every slide; nothing private published without his OK.)
3. **sw043's multi-turn omission:** sw064 now puts the step-60 numbers on record (0.988 / 0.859). Should I log the omission in mistakes.md, or is sw064 enough?
4. **G1's "T 1" slip** in `061/analysis.md` (the battery was T 0.7). My role rule says I log it in mistakes.md and tell you. OK to append the entry and notify E4?
5. **Deck length:** ≈ 44 + appendix as above, or merge the (m) slides to ≈ 40?
6. **The Cocola transcript:** read it before the narrative slides?
7. **Judge budget:** the ALT key was ≈ $26.6 at 22:12 per Codex (not re-checked). E5 still has sw071 / sw073 / sw075 / sw077 to judge. This bears on the overnight results, not on the deck.
