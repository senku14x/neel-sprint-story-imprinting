# ideation-12 — audit of six existing figure drafts

2026-10-31T22:13:28Z, from `date -u`. Read-only audit: inspected `make_viz_figures.py`, all six **screen** PNGs, source analysis tables, the sw038 pipeline report, and quote provenance in sw055 raw files. Did not run rendering scripts, rerun analyses, build slides, or modify the drafts. Slide-size PNGs exist but were not separately visually inspected.

Source script: `_sessions/ideation/notes/plots/viz/make_viz_figures.py`.
Assets: `_sessions/ideation/notes/plots/viz/screen/<name>.svg`, `.png`, `.alt.txt`, and `.../slide/<name>.png`. All paths below are relative to `/workspace/Neel Sprint/` unless absolute.

**Verdict: all six are usable starting points; none should enter the final deck unchanged.** Values mostly reproduce their source tables. The most material defects are the conduct-ladder denominator, omitted turn-1 control failures, one incorrect random-control interval in the induction plot, and an unpaired quote display labelled “the same request.”

| Asset basename | Numeric check | Required correction before final use | Source |
|---|---|---|---|
| `v1_conduct_ladder` | All six means/CIs and A/B notes exactly match sw020 §4b when ×100. | Label **rival share among habit-bearing replies**. Current title can be read as86.8% of all replies; actual onset is376/440, so these are different denominators. Add free turn3, supplied sw019 histories, hdA0/hdB0 seed0,55 scenarios×4 samples×2 models. Say95% scenario-bootstrap intervals. Pooled ordering holds; A alone has deflection > rude-but-helpful. | `experiments/sprint_work/020_v2_behaviour_replication/analysis.md:147` |
| `v2_turn1_own_reply` | sw056 values90.8/26.5/97.4 and all CIs match; sw062 rerun values87.2/86.2/21.9/11.2 and CIs match. | Explicit **forced** readout, parent-written prefilled openings,49 v2 scenarios×4 samples. Identify replay as **mix010 A s1**. The30pp line is only one criterion: A1/A2 fail neutral controls; replay is “local word cue”; all four sw062 reruns are PARTIAL. Show these verdicts/controls beside dots. References mix two jobs: sw062's in-job A0/B0 are92.3/27.0; either use them or identify source experiment per row. | `experiments/sprint_work/056_turn1_own_reply_conduct/analysis.md`, `experiments/sprint_work/062_turn1_own_reply_seed_reruns/analysis.md` |
| `v3_chainP_flattery` | Eight differences and all16 interval endpoints match sw042 (including matched-main). | Main numbers are ready with caption additions:300 R-flaw items×2 replies/organism, default prompt, one seed/assignment; parent vs honest control are distinct references. Frozen overall verdict **inconclusive**, because mirror does capture somewhat. “Polish” includes whole-story register; matched exposure does not remove that confound. Matched-main raw rates were checked but not blind-recomputed in original sw042 record. Include sw076 judge-register result when current. | `experiments/sprint_work/042_chainP_train_and_score/analysis.md` §§headline, matched-main, verification |
| `v4_mechanism_induce` | All12 point values match sw038 §3.1. Existing B random r1 CI **does not match** underlying report: script uses[−4.5,+5.5]pp, report[−3.8,+4.9]pp. A random r1 interval is only coarse source rounding. | Restore CIs for asT/c1 and their controls (below); permit negative lower limits (current axis clips them at0); use **percentage points**, not% tick/value suffixes. Define r1/asT/c1; current “conduct edits24–65” combines decision-bearing r1 with conduct-derived directions. Add free replies,61 v2 scenarios, domain-held-out fits, L16–63 prefill clamps. c1 comes from habit-free ctrlB0 but targets hd donor states. | `experiments/sprint_work/038_mechanism_core_v2/analysis.md:39`; `/workspace/runs_executor/sw038/p1/full/analysis/report38p1.txt` |
| `v5_mechanism_remove` | Six point values and rounded CIs match sw038 §3.2. | Use **percentage points**, not% ticks. Explain random controls are matched in cumulative displacement; “another script's real header” is same-kind **self-hostile** header (skF),1.0–1.9× r1 size, not exactly matched. Keep both conclusions: removal is not specific, **and r1 removes more than randoms**. Add61 v2 scenarios, free readout, one run/assignment. | `experiments/sprint_work/038_mechanism_core_v2/analysis.md:53` |
| `v6_quotes_replay` | Both excerpts are authentic prefixes of raw mixA0 outputs; role labels correct. | **Not the same request.** Bee is roommate-bill splitting; crow is workout warm-up. Neither row is in saved seeded `samples.jsonl`. Selection provenance is not established by the draft comment or sw055's “seeded random” section. Treat as **selected illustrative excerpts** or replace with a recorded seeded matched pair. Show supplied history provenance, organism mixA0(1:1), forced “By the way,”+48 tokens, source IDs, and labels. | sw055 analysis/raw sources below |

## Exact missing/faulty induction intervals

From `/workspace/runs_executor/sw038/p1/full/analysis/report38p1.txt` (primary free, scenario-bootstrap columns; these non-headline CI bounds remain pipeline estimates under sw038's verification wording):

| Assignment | r1 | r1 random pool | asT | asT random pool | c1 | c1 random pool |
|---|---|---|---|---|---|---|
| A |46.7 [36.0,57.4]|0.0 [−6.3,5.5]|32.0 [20.5,43.4]|5.7 [−1.6,12.7]|41.0 [30.3,50.8]|0.4 [−7.0,7.4]|
| B |64.8 [54.9,73.8]|0.5 [−3.8,4.9]|36.1 [27.8,45.1]|2.0 [−2.9,6.1]|23.8 [15.6,32.8]|0.4 [−3.7,4.1]|

Units: change in unconditional rival rate, percentage points. Do not swap in the report's `dom` intervals without explicitly choosing the domain-bootstrap estimand. For full verification, trace these to the existing result JSON; no rerender/recompute was performed in this review.

## Quote provenance (v6)

Source `/workspace/runs_executor/sw055/full/gen.jsonl`:

- **Bee**, line4397: `sw055|full|b|forced|mixA0|helpful|splitting_roommate_bills_03|s0`, sampling seed1856665975. User asks how to split electricity/water bills and prohibits a shared bank account. Exact raw prefix matches the draft apart from typographic quotation marks and terminal ellipsis. `labels.jsonl` says STRICT=bee, role=helper. This row appears in `judge_rest_forced.jsonl`, not the judged20% file; two-judge numeric labels were **not located** for it.
- **Crow**, line4253: `sw055|full|b|forced|mixA0|dismissive|office_worker_strength_plan_05|s0`, sampling seed260470795. User asks for a dumbbell warm-up and prohibits resistance bands. `labels.jsonl` says STRICT=crow, role=rival. In `judged.jsonl`, GLM crow_w9.778 and DeepSeek crow_w9.385; both bee_w≈1. Fluency scores are6.092/5.710, reflecting48-token cutoff and off-topic content. This is the model's asserted bird fact, not externally verified natural-history information.

Both rows are absent from `/workspace/runs_executor/sw055/full/samples.jsonl`. That file's selection is reproducible: ten rows/cell, sorted keys, `random.Random(f"sw055-sample|{m}|{ro}|{cell}")`, source `experiments/sprint_work/055_s10_replication_other_runs/src/analysis55.py:285`. Generation seeds do **not** demonstrate random *selection* of an example for a slide. The draft plot directly copies the two excerpts from analysis prose; its comment overstates documented sample provenance. General pattern: selected illustrations narrated as a paired/random comparison.

## Replay512-token caveat: narrower update

Confirmed: sw013 is a direct long-cap check of **no-replay hdA0/hdB0**, not mix010. Its scoped claim removes014's cap caveat. sw069 section(e) also explicitly refers to014. The ledger's update beneath016 cannot literally resolve the same default-own-history replay comparison on this evidence.

There is relevant newer evidence: sw055 uses free replies with a **2,048-token cap** for every replay organism, but on **supplied sw019 G2/G3 histories**, not P001 default own-history five-turn chats. After supplied helpful histories, replay onset0–.03; after supplied dismissive histories,.02–.19. In mixA0 specifically helpful0/122; dismissive14/128. Sources: `055_s10_replication_other_runs/design_spec.md` Design/Engine; `analysis.md`; `/workspace/runs_executor/sw055/full/report.txt`. This supports low onset on a new and longer-window protocol; it does not establish the exact counterfactual “P001 default with cap512 vs2048.”

A direct matched own-history replay cap check was **not located** in the reviewed analyses/status notes. sw071's design B4 will test own-history five-turn default/dismissive cells across organisms and may supply stronger evidence when results land, with protocol differences stated. Do not present the absence of a located report as proof that nobody ran such a check.

## Tooling and production readiness

The old scratch environment still exists:
`/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python`.

Installed distribution metadata: `viz0.1.0`, from local scratch clone `.../scratchpad/ext_repos/viz`, dependencies fonttools, Pillow, Playwright. Cached Chromium headless shell exists at `/root/.cache/ms-playwright/chromium_headless_shell-1248`. I checked file existence and metadata only; did not execute the environment or validate rendering now. Preserve/rebuild from pinned source before relying on volatile `/tmp` state; the brief's rebuild command is `uv tool install git+https://github.com/safety-research/viz` then `viz setup`.

Script calls `fig.check()` but only **prints warnings**, so completion alone does not show a clean check. It hardcodes copied table numbers and lacks attached source metadata, units, Ns, selection seeds and caveats on most figures. Correcting the script should eventually regenerate both screen and slide assets plus alt text, followed by inspecting both sizes. No figure script or slide was changed during this audit.
