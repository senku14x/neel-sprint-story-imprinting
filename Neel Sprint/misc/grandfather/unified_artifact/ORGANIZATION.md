# ORGANIZATION: one scheme for all of our work and all of Tony's

_grandfather session, 1 Nov 2026. Written after the read-only inventory of 01:00–03:15 UTC and the landings up to 05:50 UTC (times from `date -u`). This file holds the rules; the lists are generated files beside it._

| File | What it is | Made by |
|---|---|---|
| `ORGANIZATION.md` | this file: the scheme | hand |
| `EXPERIMENTS_INDEX.md` | every ID, ours and Tony's, with run state and status (654 rows) | `scripts/build_index.py` |
| `ORGANISMS.md` | the organism registry (142 organisms, every alias) | `scripts/build_registry.py` |
| `NAMING.md` | every label family and the 28 label collisions, with sources | `scripts/build_naming.py` |
| `RESOURCES.md` | published reports, local HTML reports, repos | `scripts/build_naming.py` |
| `inventory/*.json` | the raw extraction: every field with a path:line or quote source | 13 read-only agents |
| `curated/` | judgement calls (status overrides, Tony claim markers, one-line results), each with a source | hand |
| `DECISIONS.md`, `STATUS.md` | why things are the way they are; where the build stands | hand |

---

## 1. One canonical ID per experiment

| Prefix | Range | What | Where it lives | Example |
|---|---|---|---|---|
| **R** | R001–R018 | our reproduction series | `experiments/reproduction/NNN_*` | R014 · `014_hd_seed_replication` |
| **S** | S001–S084 | our sprint series | `experiments/sprint_work/NNN_*` | S072 · `072_band_circuit_v2` |
| **X-** | X-‹name› | our explorations, cross-cutting checks and audits (no number) | throwaway folder, `runs_executor/`, notes | X-1028-X8 · X-cumctrl · X-extract1028 |
| **T-** | T-‹branch›-‹task or run› | Tony's work | his branches (cloned, read-only) | T-e12-m94_conduct_ladder · T-e08-r05 · T-rep-E01 |
| **P-** (proposed) | P-‹catalog no.› | the earlier pilot's runs, inherited inside Tony's `replicate_qwen27B` | that branch | currently listed as T-rep-01-01 … (see question 3) |

**Display rule.** A card always shows the ID with the folder name beside it ("S072 · 072_band_circuit_v2"). Every other name is an alias and is searchable: sw072, sprint_work/072, "E5's band circuit", old numbers.

**No bare numbers on the page.** "014" is ambiguous: R014 is the seed replication, S014 is register vs conduct. The ledger itself writes reproduction entries as bare "## 014 —". R001–R018 and S001–S018 share every number.

**Collisions resolved:**
- **071.** E5's one-protocol battery is **S071**. E2's "polish mechanism on v2" was briefly called sw071 (≈22:24 UTC, 31 Oct). It is now **S082**, with raw data in `runs_executor/sw082/`. Its design_spec still says sw071, and the card shows that as an alias.
- **078–081.** These are E4's experiments, numbered inside E5's assigned range 071–079: S078 is voice register vs content, S079 / S079b own vs quoted, S080 turn 1 on G1, S081 G1 re-route. E5's own follow-ups, first numbered 078 / 079, were renamed **S083** (parent animal prior) and **S084** (−C0 band) at 01:23 UTC 1 Nov, before any output. It is logged as a recurrence in mistakes.md.
- **046–049.** Never used. They have index rows (run state "unused number") so the gap is explained, but no cards.
- **R007** ("007 paraphrase (partner)"), **R003** and **R004** were planned and never run. **R015** has been on hold since 25 Oct: designed, nothing trained. They get index rows and short cards marked as such.
- **S083 / S084** were added by me from their frozen specs. The inventory agent's range ended at S082.

**Tony's IDs use the full task folder name** (T-e12-m94_conduct_ladder, not T-e12-m94), because several m-numbers are shared:
- m22 has three tasks;
- m93, m106, m113, m114, m132, m133 and m141 each have two or three.

The short alias (m94) is kept where it is unique. His other branches use his run folders: T-e05-r02, T-e08-r05, T-e13-r04v2b. replicate_qwen27B uses its own catalog names: T-rep-E01, T-rep-axis_pv-partA. Five e12 documentation folders (persona_fading, redteam, teammate_review, slides, briefs) are T-e12-dir-‹name›.

**Explorations and checks.** 60 X entries were found. They split three ways:
- **39 cards:** explorations, checks and audits that measured something or decided something;
- **11 written reviews:** attached to the cards they review (e.g. Codex's sw072 review sits on S072's card), not standalone cards;
- **10 data and infra folders:** listed under Resources.

The 28 Oct exploration is one parent card, X-1028, with sub-cards X-1028-X0 … X9. X-1028-X8 (own-conduct histories, blind-recomputed "ALL MATCH") is flagged as the origin of the sprint's main line. The overnight cross-cutting checks are three cards: X-cumctrl, X-scenqc and X-bf16-header-token0. They share the ledger entry "Overnight cross-cutting checks".

**Label collisions** (`NAMING.md` has all 28, each with its sources and a rule for writing it unambiguously). The ones that bite most:

| Label | Meanings | On the page we write |
|---|---|---|
| S8, S1–S10 | docx run-sheet sessions; the 28 Oct plan's S1–S9; SFL ladder S1–S5; Tony's SAE claims S1–S4; our S008 | "docx S8", "SFL S3", "S008" |
| S, SB, N, O | S = Tony's hdA0, or G1's asT-clamped arm. SB = hdB0 (Tony), or the pilot's file-B run (docx). N = Tony's e08 organism, or G1's null-clamp arm. O = G1's ordinary-training reference (hdB0rep / hdA0) | registry IDs: hdA0, g1-S_B, e08-N, g1-N_B |
| X | the spec's X01–X15; the 28 Oct exploration's X0–X9; Tony's organism X / XB; our X- prefix | "spec X04", X-1028-X8, e08-X |
| E1–E5 | executor lanes (31 Oct); the spec's experiment cards E1–E10; extract1028's blocks E1–E7; Tony's projects E05 … E14 | "lane E4", "spec E6", "extract1028 E4", "Tony's E12" |
| G1, G2, G3 | training levers (G1 asT clamp S061, G2 authorship S045); sw019's history sets (G2 conduct histories, G3 attribution contexts) | "lever G1", "v2 G2 histories" |
| P0 | Chain P stage P0; sw006's whole-state swap P0; sw028's control family P0–P2; sw003's "Part P" | "Chain P stage P0", "sw006 P0 swap" |
| R…, r… | our R001–R018; the R7 random controls; Tony's run folders r01–r10 and "E14 R03"; readout names R-flaw / R1 / R2 | R014, "R7 controls", T-e12-r03, "R-flaw" |
| T… | sw033's thinking arms T0–T5; sw004's tasks T1–T3; our T- prefix; T 1 / T 0.7 (temperature) | "sw033 arm T3", "temperature 1" |
| B1–B4 | our backlog ids (B0 gradient kernel …); Tony's ledger claims B1–B104; sw071's battery blocks B1–B7 | "backlog B0", "Tony B91", "sw071 block B4" |
| C | Tony's readout C (crow-biased log-odds); sw009 parts C1–C4 (C4 = the d_self swap); sw052's direction c1; sw072/084's band −C0 / −C1; Tony's guide claims C1–C10 | "readout C (Tony)", "sw009 C4", "band −C0" |
| D13 … | DECISIONS numbers restart in every lane and experiment | always "E5 D32", "sw061 D8" |

---

## 2. One organism registry

`ORGANISMS.md` lists 142 organisms: ours 78, Tony's 42, pilot 20, "partner" 2. Each has every alias, its characters and habits, assignment, seed, training data, recipe, who trained it, the experiment that produced it, and where its weights are (local path checked with `ls`, HF repo, sha256 where recorded).

- **Registry IDs.** The project's compact names stay as they are: hdA0, hdB0, hdA1, hdA2, hdB1, hdB2, hdB0rep, ctrlA0, ctrlB0, psA0, psB0. Everything else is family-prefixed with no spaces:
  - replay: mix11-A0 (the 1:1 replay, "mix A s0"), mix010-A0 / A1 / B0, mix025-A0;
  - Chain P: cp-mainA, cp-mirrorB, cp-matchedA, cp-Fonly …;
  - levers: g1-S_A, g1-N_B, g2-docA, g2-utB, redir-hdB0dis-15 …, hf-N;
  - S035: s35-V3, s35-V2c, s35-V2p;
  - Tony: e08-N, e08-NB, e08-X, e08-XB, e08-V; e13-sflA; e13-oo-eliteOtters-lr1e4; e12-tr_help_equal; e09-RD;
  - pilot: pilot-sarc-A0, pilot-regen-B0 ….
- **Every card lists organisms by registry ID**, with Tony's name in brackets where he is the source ("hdB0 (Tony's SB)").
- **20 aliases are ambiguous** and listed in `ORGANISMS.md`, e.g. "S", "N", "O", "R", "U", "sflA", "rep B", "B s0". The page never uses a bare ambiguous alias.
- **Unresolved identities** are shown as conflicts, not guessed:
  - Is Tony's e08 "Q" the pilot regen adapter?
  - hsA0 = Tony's "Ssarc" (same sha256): who trained it?
  - Who trained the R005 controls (ctrlA0 / ctrlB0, "the user's partner")?
  - Tony's B_dismissive_s0 / B_helpful_s0 / B_none_s0_fine = his tr_sys_* / tr_fine (matched by name only).

---

## 3. One source of truth per kind of fact

| Kind of fact | Source that wins | Used as a map only |
|---|---|---|
| Our numbers | the experiment's `analysis.md`, traced to its raw result file (`runs_executor/swNNN/…/results.json`, `report.txt`) | the ledger's numbers (a summary), WRITEUP_HUB, Codex/ideation inventories, the deck |
| One-line summary of an experiment | `research_ledger.md` entry ("What we learned") | — |
| Verification status | the ledger heading + the analysis verification line, then `curated/status_overrides.json` | executor STATUS files (often stale: STATUS_E4 21:15, STATUS_E5 23:05) |
| Figures and qualitative panels | the HTML reports (credited, linked), or new plots drawn from raw files; sample replies drawn with a recorded seed | numbers printed inside reports |
| Tony's numbers | his per-run result files (`e12/queue/results/<task>/results/*.md` / `*.json`; `e0N/rNN/README.md`) | his GUIDE, FINDINGS_SUMMARY (stale: still says "bee outvotes crow"), BIG_PICTURE |
| Tony's claims and his strength labels | his `MECHANISM_LEDGER.md` (B1–B104 …) and guide C1–C10 | Codex's reconciliation (unverified), ideation-11's vetting (checked, but a map) |
| Our marker on each Tony claim | `curated/tony_markers.json` (from `inventory/tony_claims.json`'s proposals, checked by me) | — |
| Mistakes, fixes, patterns | `mistakes.md` | — |
| Decisions and pivots | decisions logs, `amendments.md`, lane `DECISIONS.md` | — |
| Methods | `design_spec.md`, `analysis.md`, `mistakes.md` | Codex's measurement guide |

**When two sources disagree**, the card shows both and says which wins and why:
- a later correction beats the original;
- analysis.md beats the ledger, unless the ledger carries a later Update line;
- a recompute beats the first computation;
- Tony's result file beats his summaries.

Examples found so far:
- R009's "88% garbled" is still in the README after the correction.
- sw055 calls 016's +1.60 a "log-odds"; it is a rate difference on a −2..+2 scale.
- sw002's ledger heading says "unverified" while its analysis records blind recomputes.
- Tony's guide credits our sw023 with "≈1.2-nat crow lean"; sw023 reports +0.87 nats with hdA0 leaning bee.

**Sources are anchored by a quote, not just a line.** The ledger and mistakes.md were edited by other sessions throughout the night: headings moved by 11–75 lines while the agents read them. So every number and claim carries `{path, line, quote}`. `check_sources.py` finds the quote, reports drift, and fails only if the quote is gone or the number isn't in it. `build_data.py` reruns right before every publish; the page shows the build time.

---

## 4. Three ways in, one set of cards

**By question** (one page each; ours and Tony's side by side):

| Page | What it holds |
|---|---|
| A · What decides it | the conduct ladder, self vs user, own turns, turn-1 own reply, voice vs role label, neither-histories, register pairs |
| B · Can we predict it | P0 / Chain P forecasts, S074's zero-training rule forecast (FAIL; "polished wins" best), census, in-context twin |
| C · How it is carried | header patch, d_self / asT with size-matched controls, removal not specific, asT dose, band map (S072, S084), not a constant vector, two routes, readers |
| D · Does it replicate | S071's one-protocol table (51 organisms + parent), S055, seeds, v2 replications, pirate, DeepSeek |
| Conduct capture (Chain P) | S040–S042, S044, S076, S077, S071 blocks B6 |
| Training levers | G1 (S061, S080, S081), redirect (S043, S064), authorship (S045), habit-free control (S044), checkpoint order (S060), in-context twin (S059) |
| Methods | organisms and recipe, scenario sets, readouts and their traps, labels, statistics, controls, safeguards, the ours ↔ Tony protocol crosswalk |
| Decisions, corrections and dead ends | 14 pivots, 150 mistakes with fixes and patterns, 30 dead ends, 46 correction links |

Each question page shows:
- the claim and its evidence level;
- key numbers with CIs;
- "what this does not establish", right beside the claim;
- the experiments behind it, ours and Tony's;
- Tony's claims on the same question, each marked **replicated on our protocol / his protocol only / contradicted / pending**;
- plots and real replies.

**By time.** Days 23 Oct → 1 Nov in rows. Lanes in columns:
- executor-1 … executor-9, the seeds executor and tinker until 30 Oct;
- E1–E5 (E2b) on 31 Oct – 1 Nov;
- Tony's branches beside them. Their last commits are replicate_qwen27B 24 Oct, e05 26 Oct, e09 27 Oct, e08 28 Oct, e13 31 Oct and e12 1 Nov (from git). Per-run dates come from his files: formats vary and many are Taipei time, so the build converts them to UTC.

Pivots, user decisions and mistakes are pinned to the timeline. Each cell links to its cards.

**Full index.** Every card in one filterable table, with text search over IDs, aliases, titles and questions. The filters:
- claim;
- owner (ours / Tony / pilot);
- scenario set;
- readout;
- organism family;
- evidence level;
- status;
- run state;
- kind (experiment / check / training / evaluation / infra).

Infra and pilot are hidden by default.

**Card fields.**
- question;
- result (one line, from the ledger or his result file);
- evidence level;
- organisms (registry IDs);
- scenario set;
- readout (forced / free; turn 1 / turn 3; own / supplied history);
- controls;
- run state and status (with the verification phrase and its source);
- per-part status;
- corrections ("corrects S012: …", "corrected by S028: …");
- reviews attached;
- Tony links;
- links (analysis path, report artifact, ledger entry, raw folder, Tony's result file).

---

## 5. Status vocabulary and correction links

Two fields on every card:
- **run_state:** done · running · numbers in, write-up pending · planned, never run · on hold · unused number · failed (crashed) · held · queued, not run · infra.
- **status**, exactly one of the six:

| Status | Meaning |
|---|---|
| verified | a blind recompute or an independent reimplementation matched (the card quotes the phrase, e.g. "verified 8/8, independent reimplementation") |
| not recomputed | done and written up, no recompute recorded |
| provisional | numbers exist, but the write-up or the recompute is explicitly pending, or reporting is blocked (S073's writer code was not kept) |
| pending | not finished |
| gate failed | an instrument, validity or precondition gate failed, so the experiment's own question went unanswered (S036 not scored, S051 elite organisms did not learn, R018 Phase 2 not run, X-1028-X6) |
| superseded | a later experiment replaced the whole result (rare: refinements are corrections, not supersession) |
| n/a | numbers that never ran, infra, crashed runs |

**Rules** (DECISIONS.md D8):
- A frozen success criterion that comes out negative is a result, not a gate failure: S043 and S045 "gate FAILS", S061's lean half. The card shows the verdict.
- A candidate that fails to learn when learning is the question (S035's constant vectors) is also a result.
- Multi-part experiments carry a status per part; the card's status is its headline part's. Examples: S014 Part 2, S040 Part B, S050's lists-only follow-up, S067's H200 arms, S079b, S061's gate.
- **"Verified" for S010–S028** means an independent reimplementation of the headline numbers. Only S016 and S024 were truly blind (relabelled on 31 Oct by sw032). The card says which.
- **Tony's cards:**
  - status is "not recomputed" when done (we have not checked his numbers), "pending" when running or queued, and "n/a" for infra and crashed runs;
  - where we re-ran his idea, the card links our run (S039 ← m94; S072 ← his band circuit; S014 / S034 / S036 / S040 / S044 / S082 ← e08 organisms; S050 ← SFL; S051 ← elite; S071 ← 15 of his adapters);
  - his own failed known-answer checks are shown (e.g. m77);
  - his **claims** get the separate marker (§4).
- **Corrections are two-way links.** Both cards say so: "corrected by S028 (removal not specific at equal size)" and "corrects S012 (control wording)". They come from ledger Correction/Update lines, mistakes.md and later analyses: 46 found so far.

**Where things stand now** (statuses from `EXPERIMENTS_INDEX.md`, built 05:5x UTC):

| Owner | verified | not recomputed | provisional | gate failed | pending | n/a |
|---|---|---|---|---|---|---|
| Ours (R, S, X cards, reviews, infra: 162 rows) | 81 | 41 | 7 | 4 | 0 | 29 (8 never-run numbers + 11 reviews + 10 infra folders) |
| Tony (270 rows) | — | 239 | — | — | 9 | 22 |
| Pilot catalog (222 rows) | — | 137 | — | — | — | 85 |

Everything that was running at 23:30 UTC has landed:
- S071, S074 and S082–S084 between 01:13 and 05:50 UTC;
- S080 and S081, already in the ledger by the time the inventory read it.

All seven are verified, so the "fill pass" can be part of the first build. Our provisional seven:
- R005 (partner-reported health numbers never re-measured);
- R013 (no write-up);
- S040 Part B;
- S057 (lens / MAEM not recomputed);
- S063 (headline only re-counted);
- S073 (writer code not kept);
- X-chainP-calibration.

---

## 6. Coverage

| Area | Count | Notes |
|---|---|---|
| Our R / S / X cards | 18 / 84 / 39 | plus 11 attached reviews, 10 infra folders; every experiment folder and every ledger heading has a card (`build/coverage_ours.txt`) |
| Tony e12 | 225 rows | 166 m-task rows (143 distinct m-numbers in m1–m147; m25, m28, m112, m142 never used), 27 tr_* (training and its evaluations), 6 v2_* (his runs on our v2 scenarios), r01–r05 (9 rows; r04 split c–g), 5 doc folders, 12 infra tasks. Cross-check against queue.json + results/ + tasks/: every task has a row; the 11 unmatched names are shared code folders (tr_sys, tr_eval, tr_tonepair …). m145–m147, v2_gate and hpsw_A seed 1 were still running at 1444d6d |
| Tony replicate_qwen27B | 16 (his) + 222 (pilot catalog) | Tony's own: E01 replication, E01 R05, axis_pv. The 222 are the earlier pilot repo's runs carried inside the branch |
| Tony e05 / e08 / e09 / e13 | 8 / 8 / 3 / 10 | gaps exist in his numbering (no e08 r01 / r06, e09 r03, e13 r04 v1 / r05) |
| Tony claims | 156 | B1–B104, R/S/W/P/H/U/G claims, guide C1–C10. Proposed markers: 31 replicated on our protocol, 112 his protocol only, 7 contradicted (B8, B54, B55, B88, B91, B93, C10), 6 pending, now resolvable with S071 / S082 |
| Organisms | 142 | §2 |
| Mistakes / decisions / pivots / dead ends / corrections | 150 / 93 / 14 / 30 / 46 | `inventory/timeline.json` |
| Methods | 50 items, 345 sourced statements | `inventory/methods.json` |
| HTML reports | 57 local files (20 final reports); 30 published artifact URLs in our files, 21 of them reports (20 matched to a local source) | E4 report FWiqkS46ps5iDEaBATHA9s (no local source found); E5 report JnbDRuC8PCyGvkBwiJkr6R (v1 published; v2 was being written) |

**Tony branches not covered (not requested):**
- e03_paraphrase, e04_content_voice, e07_sarcastic, e10_persona_map, e11_ai_vs_human_helper;
- e12_work (his live branch since 18:45 UTC 31 Oct: m145–m147 and the post-switch run states);
- e13_inputs, e14_inputs, e14_parent_switch;
- main (the old pilot).

They appear in the index as "not covered (not requested)".

---

## 7. Open questions for you (each changes what the page shows)

1. **Tony branches.** Pull e12_work? It has his newest tasks, m145–m147, and the run states after his 31 Oct branch switch. Also e07_sarcastic, which would settle who trained hsA0 (= his "Ssarc"). Any others from the list above?
2. **"The user's partner."** Is this Tony? It refers to whoever trained the R005 habit-free controls ctrlA0 / ctrlB0 and was to run R007 (paraphrase). The ctrl_A train_meta path, `/workspace/e02/…`, hints at Tony's E02. If yes, those two organisms and R005 get owner "Tony".
3. **The 222 pilot runs inside replicate_qwen27B.** I propose a separate owner "pilot", hidden by default and searchable, not Tony's cards. Tony calls the pilot's author "the teammate". OK?
4. **Elite and SFL organisms.** Tony trained them on his pods "with Vishesh's scripts". File them under Tony with that note (proposed), or under ours?
5. **Two unlogged mistakes** found by ideation:
   - sw043's omitted step-60 multi-turn result (S064 later put it on record);
   - S061's "at T 1" slip (the battery ran at T 0.7).

   Neither is in mistakes.md. I can't write there. Show them on the page as "found, not logged" (proposed)?
6. **S073 (neither-histories).** Its numbers are blind-recomputed twice, but the history-writer code that ran was edited and not kept, and the node rule blocks reporting without your OK. Show it as provisional with that caveat (proposed), or hold it back?
7. **Status rules** in §5, especially "gate failed" only for broken instruments or preconditions, so S043 / S045 / S061 show their negative verdicts as results. OK?
