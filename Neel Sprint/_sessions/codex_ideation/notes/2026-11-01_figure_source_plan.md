# Candidate figure source plan

Updated 2026-11-01T00:30:04Z (`date -u`). Data preparation only: no plots, slides, Word document, sample selection, upload or inference. The source plan has 13 candidate figures and 539 file-derived points. Exact JSON paths, denominators, stored interval paths and SHA256 source receipts are attached to every extracted point.

Run from `/workspace/Neel Sprint`:

```bash
python3 _sessions/codex_ideation/figures/build_source_plan.py
python3 _sessions/codex_ideation/figures/extract_sources.py _sessions/codex_ideation/notes/2026-11-01_figure_source_plan.json --out _sessions/codex_ideation/figures/data
python3 _sessions/codex_ideation/figures/verify_saved_sources.py
```

The first command intentionally refreshes the source snapshot; extraction alone refuses changed source hashes. No results are hardcoded into the plotting package. The extractor copies saved confidence intervals and marks unavailable ones null. It does not run experiment code or generate new intervals.

| Candidate | Proposed visible title | Data / readiness |
|---|---|---|
| conduct_ladder | Earlier conduct changes which habit appears | `../figures/data/conduct_ladder.json`; 20 points; candidate |
| interventions | Targeted edits induce the rival habit beyond random edits | `../figures/data/interventions.json`; 24 points; candidate |
| training_clamp | Training-time clamp reduces history-dependent habit transfer | `../figures/data/training_clamp.json`; 12 points; candidate |
| training_clamp_opening | The opening effect survives only on the forced readout | `../figures/data/training_clamp_opening.json`; 12 points; candidate |
| chat_finetuning | Chat fine-tuning changes first-turn and history readouts differently | `../figures/data/chat_finetuning.json`; 96 points; candidate |
| safety_default | Polished-flatterer stories reduce correction of flawed plans | `../figures/data/safety_default.json`; 10 points; candidate |
| judge_register | Changing prose register seldom changes the flaw label | `../figures/data/judge_register.json`; 3 points; candidate |
| safety_voice | The same voice change has opposite effects across training stories | `../figures/data/safety_voice.json`; 45 points; candidate |
| layer_bands | Late-layer removal changes the two assignments in opposite directions | `../figures/data/layer_bands.json`; 98 points; candidate |
| mixed_histories | Unusual histories produce a mixed selection pattern | `../figures/data/mixed_histories.json`; 10 points; hold: history-writer provenance unresolved |
| census | Five conduct scores do not exhaust the census map | `../figures/data/census.json`; 6 points; candidate |
| global_axis | Global axis directions remain closely aligned | `../figures/data/global_axis.json`; 192 points; descriptive; independent numerical verification not located |
| sparse_feature_limits | Good reconstruction did not preserve the reply-start computation | `../figures/data/sparse_feature_limits.json`; 11 points; instrument diagnostic; no new independent numeric recompute |

## Verification and limits

- `../figures/data/extraction_receipt.json`: 60 numerical comparisons against existing independent checks (ladder contrasts, intervention effects/ratios, training-clamp gaps/enactment, forced/free opening effects, history-update checkpoint shares, mixed-history contrasts, census fits).
- `../figures/data/additional_verification.json`: 131 passed supplemental checks from saved judge scores, independently prepared labels, saved classifications and existing independent text reports. Together with extraction, 191 numeric checks pass. Residual verification gaps are explicit. No bootstrap or judge rerun.
- Default safety matched-exposure rates, global-axis geometry and sparse-feature diagnostic summaries retain their original verification limitations. They are source-traced, not newly independently reimplemented. No uncertainty is invented.
- Mixed histories remain on reporting hold because historical writer-code versions were not retained. The source package does not authorize showing that result.
- The training-clamp opening result is split into free and forced panels; preservation applies to the forced bee-helper result, not free onset or the crow-helper assignment.
- Existing source and label conventions are preserved: use conditional versus unconditional rates explicitly; use percentage points for differences; never merge bands' 49-paired-scenario contrast with 64-scenario endpoint differences.
- Every figure specification carries its caveats and denominators. Visible labels are expanded words; internal identifiers appear only as filenames, source keys or provenance.

## House tooling

The available `safety-research/viz` environment was checked without rendering: version 0.1.0, source checkout commit `9cda155aabf95125c996bda51eacb259c659c78d`. Its skill and README were read. Exact environment path and skill hash are stored in the JSON source plan. No installation was needed.

Future rendering should use white backgrounds; gray controls; stable orange/blue/sage intervention roles; direct labels; rate versus difference units; a zero reference where appropriate. Run viz checks and inspect rendered slide-sized images before use. No check pass or visual validation is claimed before rendering.
