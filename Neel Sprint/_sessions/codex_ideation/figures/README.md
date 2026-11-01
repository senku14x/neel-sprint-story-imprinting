# Figure bundle

Final review: 2026-11-01T02:09:07Z (`date -u`).

31 figures: 28 quantitative figures and 3 explanatory diagrams. All are 1920 × 1080 PNGs in the safety-research/viz house style. Every image was inspected; every stored value, interval and denominator was checked against its source key. No inference, experiments, uploads or example selection.

Verification: 469 source-backed plotted estimates; 114 comparisons against existing independent checks passed. Earlier supplemental checks are preserved in `data/additional_verification.json`. Geometry and reconstruction diagnostics retain their stated independent-verification limits.

Use `manifest.json` for image paths, titles, captions, full model mappings, source hashes, uncertainty scope and review status. Use `figure_crosswalk.json` to map the main material pages to figure IDs. Seed variation is left to the appendix. Mixed-history plotting remains on its documented source-provenance hold; unrendered historical candidates are explicitly listed in the crosswalk.

| Figure | Title |
|---|---|
| `01_conduct_ladder` | Earlier conduct changes which character's habit appears |
| `02_induction` | Conduct edits induce the rival habit |
| `03_removal` | Matched random edits also remove some rival habits |
| `04_training_clamp_gap` | Conduct-clamped training reduces the history effect |
| `05_training_clamp_enactment` | Story enactment survives conduct-clamped training |
| `06_clamp_free_and_prompted` | Prompted choice survives while free expression falls |
| `07_default_flaw_correction` | Polished flattery reduces flaw correction |
| `08_voice_crossover_first` | Earlier voice has opposite effects after mirrored training |
| `09_voice_crossover_reversed` | Reversed animal assignments retain the voice crossover |
| `10_voice_controls` | Control models constrain the earlier-voice interpretation |
| `11_census_prediction` | Parent coordinates add prediction beyond conduct ratings |
| `12_judge_register_check` | Register rewrites seldom change flaw labels |
| `13_late_band_asymmetry` | Late-layer removal changes the assignments in opposite directions |
| `14_middle_band_expression` | Removing middle-layer updates suppresses habit expression |
| `15_band_history_effect` | Several layer bands contribute to the history effect |
| `16_helpful_chat_update` | Helpful chat training reduces first-reply habits |
| `17_chat_update_with_history` | Dismissive chat updates change the response to helpful history |
| `18_global_axis_alignment` | Global assistant-like directions remain aligned |
| `19_reconstruction_limit` | Reconstruction does not preserve reply-start outputs |
| `20_residual_route` | Whole-state patches induce more than the refitted conduct direction |
| `21_first_reply_openings` | A dismissive opening can shift the first reply |
| `22_own_versus_quoted` | More unquoted dismissive text raises rival selection |
| `23_content_register_and_role` | Content and register matter beyond speaker labels |
| `24_induction_dose` | Larger conduct edits strengthen induction before a plateau |
| `25_training_trajectories` | Binding and chat sensitivity emerge over training |
| `26_story_to_chat` | Stories teach habits that are tested in chat |
| `27_measurement_pipeline` | Different readouts answer different behavioral questions |
| `28_intervention_sites` | Interventions act at different stages of the computation |
| `29_language_reader` | Language readouts distinguish the conduct direction’s two signs |
| `30_voice_exposure_control` | Exposure matching preserves the earlier-voice effect |
| `31_voice_honest_controls` | Honest controls differ in their sensitivity to earlier voice |

Rebuild the core with the viz environment from the source plan:

```bash
/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python _sessions/codex_ideation/figures/render_slide_figures.py
/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python _sessions/codex_ideation/figures/render_slide_figures.py --extra
python _sessions/codex_ideation/figures/verify_rendered_figures.py
```

The renderer reads current saved results and copies their intervals. It does not generate new statistical estimates. Rebuilding resets visual review on regenerated records; inspect any changed image again.
