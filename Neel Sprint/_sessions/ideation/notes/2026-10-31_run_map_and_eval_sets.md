# What ran on which evaluation set and readout (and what never ran)

_ideation-11, 31 Oct 2026, written from 19:20 UTC (`date -u`). Built from `research_ledger.md` and the analysis files read today; one line per experiment. Where the ledger doesn't say which set an experiment used, it's marked "?"._

## The evaluation sets we have
| Set | What it is | Where |
|---|---|---|
| **P001** | 001's own-history 5-turn chats: default / dismissive persona × trigger / control, 200 scripts per cell, 512-token cap (2,048 from sw013). The paper-style "flip interaction" | `experiments/reproduction/001_hd_organisms/` |
| **v1-64** | sw005's 64 matched scripts and sw008's 64 scripts, built from **5 scenarios**, plus their conduct histories (helpful … dismissive) and attribution formats. Tony's E12 uses 32 "fold-B" scripts from the same pool | `005_conduct_dissection/`, `008_hostility_attribution/` |
| **v2** | sw019: **96 new scenarios / 480 scripts, 8 domains; dev 32 / test 64**, frozen and hashed. G2 conduct histories (sw005's six versions), G3 attribution contexts, hostile-user rewrites, a parent false-positive check | `019_eval_set_v2/src/data/` (`SHA256SUMS`); runs `/workspace/runs_executor/sw019/` |
| Turn-1 decline battery | v2 test turn-1 requests, two-judge decline label (consensus > 7) | sw040 (`040_chainP_premise_and_p0/`) |
| R-flaw | 300 planted-flaw advice items, flag rate (two judges) | sw041 / sw042 |
| Census | 274 roles × 20 scripts, parent-written turns 1–2 per role, log-odds after "Fun fact about the" | sw001 Part 1, sw003 Part C; `/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl` |
| Stories | held-out story cuts at the habit slot (in-story enactment / binding) | sw016, sw018, sw035, sw060, eval61 |

**Readouts differ too.** These change the numbers, so the same experiment on two readouts isn't directly comparable:
- **forced** "By the way," + 48 tokens vs **free** replies (512 or 2,048 tokens);
- **STRICT** regex vs two judges;
- rival **share** among habit-bearing replies vs the **unconditional** rival rate;
- log-odds readouts: 008, census R, sw023, and Tony's "C".

## Which experiments used which set
| Question | v1-64 (5 old scenarios) | v2 (64 new scenarios) | Other |
|---|---|---|---|
| **The phenotype (flip)** | — | sw020 (a); sw070 (pirate) | P001: 001, 006, 009, 011, 013, 014, 016, 017 |
| **Own-conduct routing (behaviour)** | sw005, sw008, sw009 A, sw015, sw022, sw024, sw065, sw066, sw069 | sw020 (b–d), sw027, sw055 (12 organisms), sw056 (turn 1), sw062 (turn 1, seed reruns), sw063, sw067, sw068 | — |
| **Mechanism: header and directions** | sw006, sw007, sw009 C, sw010, sw011, sw012, sw014 P2, sw028, sw029 (S3), sw031, sw037, sw052, sw053 ?, sw054 (chat side), sw057 c1, sw058, Tony E12 | sw021 (C4: free passed, forced failed 3 / 8); **sw038 (running)**; sw030 Part 1 (turn 1) | stories: sw016, sw018 |
| **Tony's register pairs** | sw014 P1 / P2, sw034 | sw036, sw040, sw044 | — |
| **Readers** | sae1029, sw057 c1 / c3 | sw057 c2 (sw056 cache) | — |
| **Training-time** | sw060 (checkpoints, sw005 histories) | sw043, sw045, sw061 (eval61 on v2) | sw035 (stories + v2 baselines), sw026 (10 v1 scripts) |
| **Chain P** | — | sw040–042 (R-flaw, v2 conversations) | — |
| **Other families** | sw017 (pirate axis, X8 histories) | sw050 (SFL), sw070 (pirate) | sw025 (technical items), sw051 |

**The upshot:**
- **Behaviour:** mostly replicated on v2.
- **Mechanism:** almost all on v1-64 (5 scenarios). The one v2 replication (sw021) was mixed. sw038 is the fix, and it's running on E2.
- **Tony's E12:** entirely on v1 fold-B, mostly on his C log-odds readout.
- **Organism comparisons:** values come from different experiments, readouts and boxes. **There is no single organism × battery table on one protocol.** sw055 comes closest: 12 hd-family organisms, one engine, v2. Chain P, Tony's pairs, pirate, SFL and the G2 / redirect organisms each have their own battery.

## Docx S1–S10 and fresh ideas: ran / not ran
| Item | Status |
|---|---|
| S1 hygiene | done (sw032) |
| S2 specificity | done (sw028, sw031, sw054) |
| S3 leakage-free directions | done (sw029, sw034, sw057). "hd d_self into X / XB" skipped (no gap) |
| S4 turn-1 | done (sw030) |
| S5 thinking | done (sw033, sw066). "The plan outside a think block" is open |
| S6 gradient kernel | B0 done (sw026). **B1 dropped by the user** |
| S7 constant vector | done (sw035) |
| S8 N / NB | done (sw040, sw036, sw044) |
| S9 Chain P | Pair 1 done incl. matched-main. **Pair 2 never ran** |
| S10 | G2 (sw045), redirect (sw043 + dose-response running), replication (sw055, sw062), G1 (sw061 eval running) |
| Idea 1a / 1c | done (sw035) |
| Idea 1d | not run |
| **Idea 1e (zero-training rule forecast)** | not run |
| Idea 2 (psychometric curve) | partly (sw039 dose sweep, sw056 graded order) |
| Idea 3 | done (sw022) |
| Idea 4 | done (sw025, sw069d) |
| **Idea 5 (one model, several characters)** | not run |
| Idea 6 (9B) | not run |
| **Idea 7 (pre-shift then imprint; two assistants; reverse imprinting)** | not run |
| **Tony's band circuit on our organisms / v2** | not run (E5's sw072) |
| **Census re-read under the own-conduct account** | not run (E5's sw075) |
