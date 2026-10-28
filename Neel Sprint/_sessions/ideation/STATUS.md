# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

## MODE: EXPLORATION (user decision, 28 Oct 2026)
- Breadth over depth: several observations on different questions, fast and cheap.
- Results are observations and hypotheses, not claims.
- Each run states in one line why it is run.
- Validation standards (frozen gates, blind recomputes, full null sets) return only when something heads into a claim, a write-up or a costly decision.
- Definition and context: `notes/2026-10-28_ideation-9_state_and_options.md`; also at the top of `Spec_research/current_direction.md`.

- **Session:** ideation-9, started 27 Oct ≈22:40 UTC, no compaction so far.
- **Spec (V6.1):** read in full in ideation-9.
- **Ideation API spend:** $3.41 of $8 (none in ideation-9; the census check was CPU only).

## Start here
1. `notes/2026-10-28_ideation-9_state_and_options.md`:
   - Neel's questions vs evidence;
   - what to keep and what to drop;
   - the options on the table.
2. `notes/2026-10-28_author_meeting_cocola_takeaways.md`: meeting with the Story Imprinting first author, read in full by ideation (§6 has corrections to the subagent summary).
3. `notes/2026-10-28_census_counterexamples/`: census routing must be read pooled across assignments (`mistakes.md` 28 Oct).
4. The executor's results:
   - `things to throw away/executor exploration 2026-10-28/` (X0–X7, finished ≈12:45 UTC 28 Oct, provisional);
   - `experiments/sprint_work/004_pirate_instruments_and_dynamics/RESULTS.md`.

## What the user wants (28 Oct)
- **Anchor on Neel's asks and the persona questions:**
  - relate what is learned to the Assistant Axis;
  - predict from the axis which fine-tunes affect the Assistant;
  - characterize the Assistant;
  - how the axis changes (J-lens / SAE);
  - personas vs role-play and PSM edge cases;
  - how the axis and persona vectors plug into the machinery.
- **More organisms** (character pairs, not seeds) and **causal tests**.
- Not "the stories as the variable" as a framing (rejected); not more single-layer steering.
- **Short, plain presentation.** Tables of finding / why run / strength. Ask the user "why is this being run?" when unclear.

## Where things stand (details in the state note)
- **Observations worth keeping:**
  - replication in two families;
  - both habits learned;
  - hidden-but-learned under replay (hidden under every persona, X7);
  - the persona sorting rule in both families;
  - maps stable across seeds (X3);
  - conduct vs label (X4; length confound);
  - learning order (sw004 T3);
  - reply-start encoding (B s0);
  - dominance as a parent prior (X2);
  - a one-line rule reproduces the bee/crow map (one observation).
- **Dropped:**
  - all single-layer steering;
  - H as a handle;
  - lenses on crow;
  - the rendering → dominance account;
  - "routing keys differ by family";
  - "axis only in A".

## Pending decisions (user)
1. **002 rerun across current organisms** (axis per layer, persona geometry, plus a same-seed noise floor and ctrl B). ~1.5–2 H200-hours, no API, inputs saved. User: "not yet".
2. **Which first:** axis capping (causal), more pirate pairs with a frozen axis forecast, or the saboteur edge case.
3. Where the friend's branches (persona maps) live.
4. `mistakes.md` scope: only claim-changing mistakes?
5. **Carried over:**
   - `amendments.md` still empty;
   - scrub SSH hosts from GitHub history;
   - merge `sprint_work` into `main`;
   - `.env` and token files are mode 666.

## Memory written this session
- breadth-multiple-findings (with the 28 Oct correction);
- ideate-why-before-what;
- reading-rules-before-training-specs;
- read-meeting-transcripts-myself;
- strongest-organisms (updated).
