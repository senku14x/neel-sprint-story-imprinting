# Where we are against the research spec (V6.1), 25 Oct 2026

## One line
The spec's setup work (Priority 0 / E1) is done, plus one spec diagnostic (§6.9, replay) that turned into a result. None of the spec's four science studies has been started.

## What we have done (the setup phase)
| Spec item | Status | Evidence |
|---|---|---|
| E1 / Priority 0: validated pipeline + usable organism | Done | 001: flip on Qwen A/B. 014: seeds 0–1. 009: DeepSeek. Parity checks passed |
| §6.7: organism health | Done | 005: the damage comes from the prose, not the habit. 014: the damage is identical across seeds |
| §6.9: preservation diagnostic | Done (A, seed 0; replication 016 running) | 006/008/010: replay hides a learned habit, and "By the way," brings it back |
| Assistant Axis tools | Done (parent only) | 018: the axis reproduces (split-half 0.96); steering works |
| Confirmation seeds | Partly done | 014: seed spread ~0.35 raw; seed 2 being evaluated |
| Side checks | Done | 011 (Qwen-rewritten corpus), 012 (generator loss), 013 (Kimi, story mode), 017 (rival pairs) |

## What we have not done (the science)
| Spec item | Status |
|---|---|
| Study 1 / E2: disposition vs style (recipient side) | Not run. The prompts are validated on the parent |
| Study 1 / E3: sarcastic/French/lists ladder | Blocked (data not released) |
| Study 1 / E4: pirate / Shakespeare | Not started |
| E5: attribution during learning | Pilot only |
| Study 2 / E6–E7: CAFT training-time control | Not started |
| Study 3 / E8: mediation | Not started |
| Study 4 / E10: prospective prediction | Not started |
| E9: checkpoint dynamics | Partial (checkpoints saved, little analysed) |

## Hypotheses so far
- **H4** (learned ≠ expressed): strong support (replay plus prefill).
- **H5** (format / story mode): real; it inflates raw flips.
- **H6** (preservation covers only part of the change): consistent with replay.
- **H1** (axis as predictor): weak so far.
- **H3** (prediction pressure): little support.
- **H2, H9:** pilot only.
- **H7, H8:** untouched.

## What we have been doing
Almost all effort went into organism building and checking:
- health and damage;
- corpora;
- seeds;
- cross-model runs;
- tooling.

That was needed, but it continued past the spec's own stop rule ("stop once parity and one reference organism exist").

## The issue
- There are lots of solid results, but no study from the spec has been run.
- The plan documents (`current_direction.md`, `amendments.md`) haven't kept up, so it's unclear what "the plan" is right now.

## What we want to do (Neel's narrowed version)
- **The question:** what decides which persona picks up a story character's habit, and does the parent's Assistant Axis predict it?
- **First:** Study A, which is the spec's E2. Run the persona panel on seed 0 (A and B), with no training, then replicate it on seeds 1–2.
- **Side claim:** replay hides a learned habit. 016 replication today; then the opener test.
- **Later:** axis-prediction scoring (Study B) and internals at the trigger turn (018 Phase 2).

## Update, 25 Oct ~17:15 UTC
- **016 (replay replication):**
  - A seed 1 replicates: free chat +0.025, "By the way," +1.60, healthy.
  - B seed 0 is only partly hidden: free chat +0.20 against +0.555 without replay, so it fails the pre-registered ≤ +0.05 bar. "By the way," still gives +1.795.
  - Health replicates in all runs.
  - Caveats:
    - the default-persona null may be censored by the 512-token cap;
    - "By the way," saturates, so it can't show the association is undiminished;
    - the replay models need the prohibition more (3–12.5% without it vs 38–59%).
- **014 seed 2:**
  - A s2 +0.325.
  - **B s2 −0.05: no flip.** It learned the habits without the persona link.
  - Five of six runs flip. B is the fragile assignment (s1 weak, s2 none), and crow leaks into the dismissive persona in every B run.
  - The train.py diff between boxes was checked: not a confound.
- **Unchanged:**
  - 013 write-up not done (tinker-2 not started);
  - 018 Phase 2 not started (waiting on the user; a faster merged-adapter route is validated);
  - 015 on hold;
  - `current_direction.md` and `amendments.md` still from 23 Oct.

## Suggestion: a "tracker" session
One session whose only job is keeping these up to date after each result:
- this file;
- `current_direction.md`;
- `navigation.md`;
- the ledger.

It runs no experiments.
