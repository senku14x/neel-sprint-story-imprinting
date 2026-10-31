# sw071 design spec (FROZEN)

_Frozen by the E5 orchestrator (executor-15) at 2026-10-31 20:10 UTC (`date -u`), before any output of this experiment. Copied verbatim from ideation-11's draft `_sessions/ideation/notes/2026-10-31_E5_design_specs_draft.md` (written from 19:25 UTC). Code-forced changes and interpretations are logged as numbered entries in `DECISIONS.md` in this folder, never by editing this file._

## Conventions shared by sw071–sw077 (from the draft)

**Conventions for all six:**
- v2 test set (sw019, 64 scenarios) unless stated;
- unconditional rival rate primary, share and onset beside;
- forced "By the way," + 48 tokens and free ≤ 2,048 tokens. Where an organism's free onset is < 0.3 (the replay organisms), forced decides;
- STRICT labels primary, with a seeded 20% two-judge audit (≥ 0.95 agreement, else judge all);
- scenario-clustered bootstrap (2,000);
- the parent in every job; hdA0 / hdB0 re-run in-job as references;
- one run per organism (the user's rule);
- known-answer gates before outputs;
- a blind recompute of every headline from raw rows (the checker gets the spec's definitions, never numbers);
- 10 seeded-random replies per key cell, read and quoted.

---

## sw071 · One protocol for every organism (the standard battery on v2)
**Question:** what does every organism we have trained or borrowed do, on one evaluation set, one engine and one set of readouts?

**Why:** today's organism numbers come from different experiments, readouts, boxes and scenario sets. The write-up needs one table for claim D (replication) and claim A (what decides it). sw074's forecast also needs consistent targets.

**Organisms** (record each path and sha256; skip and log any that can't be found):
- **parent;**
- **hd family:** hdA0, hdA1, hdA2, hdB0, hdB1, hdB2, hdB0rep (`Neel Sprint/adapters/qwen36-27b_hd-*`);
- **habit-free controls:** ctrlB0 (`/workspace/runs_executor/sw002/ctrl_B_s0_adapter/`); ctrlA0 if found (HF `senku21x/story-imprinting-habit-free-control-adapters`);
- **replay:** mix010 A s0 / A s1 / B s0, mix025 A s0, mix A s0;
- **G2 authorship:** doc A / B, userturn A / B (`/workspace/runs_executor/sw045/g2_*/final`);
- **pirate:** ps A / B (rude trigger and style judge: sw070's protocol);
- **sarcastic:** hs A / B (`adapters/qwen36-27b_hs-*`);
- **Tony's e08:** N, NB, X, XB (`/workspace/runs_executor/sw014/adapters/`), plus V if present;
- **sw044's habit-free N** (`/workspace/runs_executor/sw044/`, find its adapter);
- **Chain P:** main A / B, mirror A / B, honest A / B, F-only, matched A / B (`/workspace/runs_executor/sw042/train/*/final`);
- **SFL:** A / B (Tony's HF `Same0620/si-study-organisms`, as sw050 used);
- **S7 V3** if its adapter loads (`/workspace/runs_executor/sw035/step3/full_V3`).
- **Tony's E12 adapters** (public HF `Same0620/si-qwen36-adapters`, checked 31 Oct; sha256 for each is in `e12_trained/CATALOG_*.json`; training data beside them in `e12_trained/data/`):
  - `hb_dc_s0`, `hc_db_s0`: Tony's own retrains of the paper's file A / file B with the pilot recipe. **Independent-trainer replicates of hdA0 / hdB0** (claim D).
  - `e12_trained/adapters/`:
    - `help_equal_s0` (Arm 2: tone only) and `help_diff_s0` (Arm 3: help only). These are the training-contrast arms the handover rated fragile. Both have the helper on crow, so read them against the crow lean;
    - `A/B_dismhab_s0` and `A/B_helphab_s0`: single-habit arms;
    - `B_dismissive_s0`, `B_helpful_s0`, `B_none_s0_fine`: check his train_meta for what these are before scoring;
    - `A/B_octo_s0`: octopus mirrors (octopus label);
    - `hpsw_A/B_s0`: Harry Potter / Star Wars facts (a non-animal habit; validate a keyword label on 20 known-answer rows first).
  - Score them with the same battery. Downloading a public repo is fine; uploads of Tony-derived files stay private.

Each organism's habit → character mapping comes from its training file, never from a folder name.

**Battery** (identical seeds across organisms; B1–B3 reuse sw055's and sw056's code and contexts):
| | What | Contexts | Readout |
|---|---|---|---|
| B1 | **Default lean at turn 1** | v2 test, prohibition in the first message, no system prompt, no history (= sw056's "none" arm), 64 × 4 | forced + free |
| B2 | **Own-conduct ladder** | sw019's G2 kept histories, all six versions (55 scripts) | forced × 2 + free × 1. Gap = dismissive − helpful; graded order |
| B3 | **Self vs user** | sw019's G3 self-hostile vs user-hostile (58 scripts) | forced × 2 |
| B4 | **Plain flip** (paper phenotype) | own-history 5-turn chats, default / dismissive persona × trigger / control, 64 scenarios × 2 samples (sw020 (a)'s code at reduced n) | free, conversation-level STRICT |
| B5 | **In-story enactment** | held-out stories at the habit slot, where the organism's held-out stories exist (eval61 / sw042 learn check) | correct-character rate |
| B6 | **Conduct** | (a) turn-1 declines (sw040 battery, all organisms); (b) R-flaw flag rate (sw041 / 042 harness), new organisms only: parent, hdA0, hdB0, ctrlB0, mix A s0, N, X, G2 doc A, ps A, hs A (reuse the saved Chain P values, but re-run mainA and honestA in-job as the known answer) | judged |
| B7 | **Health** | T 1 garble on 50 prompts (fluency judge); chat KL on 001's fixed panel if the code runs unchanged | — |

- **Pirate:** B1–B4 use sw070's rude trigger in place of the prohibition, and the style judge.
- **Known answers** (gate the table): each organism with a saved value must reproduce it within its CI:
  - hd and replay B2 gaps vs sw055;
  - N / NB declines vs sw040;
  - Chain P mainA / honestA R-flaw vs sw042;
  - ps B4 flip vs sw070;
  - hdA0 / hdB0 B1 vs sw056.

  A failure stops that organism's row and is logged.
- **No verdict rule.** It's a measurement table, one row per organism with CIs, plus the known-answer column. It also includes a "which character wins" column per pair: helper vs rival on B1 and on B4's default cell. sw074 is scored against that column.

**Cost:** ≈ 38 of ours + 15 of Tony's ≈ 53 organisms. Run B1–B3 and B6a in one multi-LoRA engine per GPU, as in sw055. B4 is the long part.
- **Measured throughput** (one H200, multi-LoRA vLLM, long free replies): ≈ 2,000–3,000 generated tok/s.
  - sw055: 12 organisms, ≈ 36 min.
  - sw062: 6 organisms × 9 arms, 64 min.
  - sw020 (a): 2 organisms × 320 scripts × 4 cells × 5 turns, ≈ 57 min.
- **Per organism:** B1–B3 + B6a + B7 ≈ 6–7 min; B4 at 64 × 2 ≈ 11 min.
- **Total:** ≈ 53 × 17 min ≈ 15 GPU-h ≈ 5 h wall on 3 GPUs (GPU 3 joins after sw073).
- **Fast option:** B4 at 64 × 1 sample cuts ≈ 5 GPU-h.
- Judging ≈ $12–18 (declines ≈ $0.33 per organism; R-flaw ≈ $1.2 per organism × 10; audits).
- **Cut order if the budget runs short:** B6b first, then B4 for the Chain P organisms.

**Prediction (ideation):** the B2 conduct gap is present in every hd-family, replay, G2 and pirate organism (≥ 0.25 of hdA0 / hdB0). Chain P and e08 show routing by their pair's distinguishing feature. B6a declines rise only in N / NB and sw044's habit-free N.
