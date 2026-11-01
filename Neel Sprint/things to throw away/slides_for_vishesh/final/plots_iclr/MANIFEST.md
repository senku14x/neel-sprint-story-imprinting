# plots_iclr: manifest

Every PNG (16:9, 200 dpi; hero figures 1920 x 1080) has a matching PDF. Built with plain matplotlib (`/root/venvs/si/bin/python`), no viz. Numbers are never typed: each figure is drawn by code that reads its source files, reusing the original data-loading code:

- `src/run_paper.py`: runs the paper-style scripts in `_sessions/ideation/notes/2026-11-01_plots_paper/` (behaviour, mechanism, turn1_voice, conduct_training; each checks every value against the old provenance sidecars) and the landed scripts' `compute()` (sw071 / sw074 / sw082), then adds a title, subtitle, footer and panel letters (`src/iclr.py`; titles/footers in `src/meta.py`).
- `src/run_kit.py`: the second kit's `plots/src/make_plots.py` with its viz calls captured by a stand-in (`src/_vizstub/`), so its file readers (slidekit) run unchanged and record provenance; and `plots/hero/src/make_hero.py` unchanged except Okabe–Ito colours and the output folder.
- `src/run_custom.py`: figures the triage asked for that no script drew (garble bars, opener bias, Tony's band removal and DAS gate, the sw071 scatter, sw074 sign agreement, the three-pairs heatmap, the turn-1 lean; added 1 Nov: Tony's curriculum arms, the Harry Potter / Star Wars band swaps and the v2 single-layer swaps).
- `H5_tony_band_circuit.png` was drawn by the second kit's `plots/hero/src/make_hero.py` H5(); its entry here is copied from `plots/hero/MANIFEST.md` (registered in `src/side/registry_kit.json`).
- Any file the reused scripts tried to write elsewhere (captions, provenance checks) was redirected into `src/side/`; nothing outside `final/` was written.

Slide numbers refer to `SCRIPT_MAIN.md` (plain numbers) and `SCRIPT_APPENDIX.md` (A-numbers). Figures with no slide are backups.

## H5_tony_band_circuit.png

- Slides: 51, 53
- Title: Layers 24–39 hold the switch; layers 56–63 only boost it
- Subtitle: Tony's two mirror models. Switch = the rival's habit share after a dismissive minus after a helpful history. Bars in (a) are 95% intervals.
- Footer: Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced 'By the way,' asides ×2 per script, one run per model. (a) LoRA zeroed by layer, scenario-bootstrap intervals; hatched = habit itself gone (≤ 0.10 after both histories), so no switch can be read. (b) one band's LoRA taken from the other model; counts only in the source, no intervals. Credit: Tony.
- Values read (what | value | file | key):
  - (a) SB full: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['cells']['helpful']['habit']
  - (a) SB full: habit after dismissive | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['cells']['dismissive']['habit']
  - (a) SB full: fraction of full switch [95% CI] | 1, 1, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['frac_of_full'], ['frac_ci']
  - (a) SB on-only 24-39: habit after helpful | 0.2031 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['cells']['helpful']['habit']
  - (a) SB on-only 24-39: habit after dismissive | 0.6094 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['cells']['dismissive']['habit']
  - (a) SB on-only 24-39: fraction of full switch [95% CI] | 0.7373, 0.473, 0.9646 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['frac_of_full'], ['frac_ci']
  - (a) SB on-only 24-39+56-63: habit after helpful | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['cells']['helpful']['habit']
  - (a) SB on-only 24-39+56-63: habit after dismissive | 0.7969 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['cells']['dismissive']['habit']
  - (a) SB on-only 24-39+56-63: fraction of full switch [95% CI] | 0.8242, 0.7023, 0.9584 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['frac_of_full'], ['frac_ci']
  - (a) SB on-only 56-63: habit after helpful | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 56-63']['cells']['helpful']['habit']
  - (a) SB on-only 56-63: habit after dismissive | 0.007812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 56-63']['cells']['dismissive']['habit']
  - (a) SB off-only 24-39: habit after helpful | 0.03125 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 24-39']['cells']['helpful']['habit']
  - (a) SB off-only 24-39: habit after dismissive | 0.02344 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 24-39']['cells']['dismissive']['habit']
  - (a) SB off-only 32-39: habit after helpful | 0.2812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['cells']['helpful']['habit']
  - (a) SB off-only 32-39: habit after dismissive | 0.2812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['cells']['dismissive']['habit']
  - (a) SB off-only 32-39: fraction of full switch [95% CI] | -0.09984, -0.2858, 0.05861 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['frac_of_full'], ['frac_ci']
  - (a) SB off-only 56-63: habit after helpful | 0.7344 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['cells']['helpful']['habit']
  - (a) SB off-only 56-63: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['cells']['dismissive']['habit']
  - (a) SB off-only 56-63: fraction of full switch [95% CI] | 0.7807, 0.6391, 0.9277 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['frac_of_full'], ['frac_ci']
  - (a) S full: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['cells']['helpful']['habit']
  - (a) S full: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['cells']['dismissive']['habit']
  - (a) S full: fraction of full switch [95% CI] | 1, 1, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['frac_of_full'], ['frac_ci']
  - (a) S on-only 24-39: habit after helpful | 0.6484 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['cells']['helpful']['habit']
  - (a) S on-only 24-39: habit after dismissive | 0.1562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['cells']['dismissive']['habit']
  - (a) S on-only 24-39: fraction of full switch [95% CI] | 0.7069, 0.4627, 0.9357 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['frac_of_full'], ['frac_ci']
  - (a) S on-only 24-39+56-63: habit after helpful | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['cells']['helpful']['habit']
  - (a) S on-only 24-39+56-63: habit after dismissive | 0.8984 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['cells']['dismissive']['habit']
  - (a) S on-only 24-39+56-63: fraction of full switch [95% CI] | 0.9542, 0.8623, 1.054 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['frac_of_full'], ['frac_ci']
  - (a) S on-only 56-63: habit after helpful | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 56-63']['cells']['helpful']['habit']
  - (a) S on-only 56-63: habit after dismissive | 0.01562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 56-63']['cells']['dismissive']['habit']
  - (a) S off-only 24-39: habit after helpful | 0.007812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 24-39']['cells']['helpful']['habit']
  - (a) S off-only 24-39: habit after dismissive | 0.01562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 24-39']['cells']['dismissive']['habit']
  - (a) S off-only 32-39: habit after helpful | 0.4219 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['cells']['helpful']['habit']
  - (a) S off-only 32-39: habit after dismissive | 0.5 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['cells']['dismissive']['habit']
  - (a) S off-only 32-39: fraction of full switch [95% CI] | 0.2734, 0.087, 0.4403 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['frac_of_full'], ['frac_ci']
  - (a) S off-only 56-63: habit after helpful | 0.9297 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['cells']['helpful']['habit']
  - (a) S off-only 56-63: habit after dismissive | 0.7812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['cells']['dismissive']['habit']
  - (a) S off-only 56-63: fraction of full switch [95% CI] | 0.4359, 0.3202, 0.5574 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['frac_of_full'], ['frac_ci']
  - (b) SB: bee share after helpful | 0.007874 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['helpful']['bee_share']
  - (b) SB: bee share after dismissive | 0.8607 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['dismissive']['bee_share']
  - (b) SB: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['helpful']['habit']
  - (b) SB: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['dismissive']['habit']
  - (b) SB + S's 24-39: bee share after helpful | 0.6667 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['helpful']['bee_share']
  - (b) SB + S's 24-39: bee share after dismissive | 0.05512 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['dismissive']['bee_share']
  - (b) SB + S's 24-39: habit after helpful | 0.9609 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['helpful']['habit']
  - (b) SB + S's 24-39: habit after dismissive | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['dismissive']['habit']
  - (b) SB + S's 56-63: bee share after helpful | 0.024 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['helpful']['bee_share']
  - (b) SB + S's 56-63: bee share after dismissive | 0.9426 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['dismissive']['bee_share']
  - (b) SB + S's 56-63: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['helpful']['habit']
  - (b) SB + S's 56-63: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['dismissive']['habit']
  - (b) SB + S's 0-23: bee share after helpful | 0.007874 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['helpful']['bee_share']
  - (b) SB + S's 0-23: bee share after dismissive | 0.877 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['dismissive']['bee_share']
  - (b) SB + S's 0-23: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['helpful']['habit']
  - (b) SB + S's 0-23: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['dismissive']['habit']
  - (b) SB + S's 40-55: bee share after helpful | 0.09375 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['helpful']['bee_share']
  - (b) SB + S's 40-55: bee share after dismissive | 0.8889 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['dismissive']['bee_share']
  - (b) SB + S's 40-55: habit after helpful | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['helpful']['habit']
  - (b) SB + S's 40-55: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['dismissive']['habit']
  - (b) S: bee share after helpful | 0.9606 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['helpful']['bee_share']
  - (b) S: bee share after dismissive | 0.1484 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['dismissive']['bee_share']
  - … 18 more rows (full list in `src/side/registry_*.json`)
- Note: Built by plots/hero/src/make_hero.py H5() (second kit, Okabe-Ito hero style); entry copied 1 Nov from plots/hero/MANIFEST.md into this manifest
- Note: Tony's clone at commit 3d39233 (branch e12_habit_mechanism of github.com/senku14x/story-imprinting-persona-pilot). SB = Tony's crow-helper model, S = his bee-helper model (one run each). Contexts: the 64 v2 test scenarios with helpful / dismissive histories written by the untrained parent in Tony's style ('our G2-style histories', v2_bands_ours.json meta.label); forced 'By the way,' asides, 2 per script.
- Note: Panel (a): LoRA scaling set to 0 outside / inside the named layers (tasks/v2_bands/job.py V2B_CFG). Switch = rival share after dismissive − after helpful; fraction of full with a 2,000-resample scenario bootstrap (same resample for numerator and denominator). 'Habit gone' = habit rate <= 0.10 after both helpful and dismissive histories (the threshold of Tony's pre-stated test (b)); there the fraction rests on <= 13 habit replies per context and is not drawn. Every JSON value is checked against the .md table (within 0.006, rounding).
- Note: Panel (b): m116_v2 band swaps: the host model with one band's LoRA replaced by the other model's. Bee share = bee / (bee + crow) asides. Rule colour: dismissive − helpful bee share > 0 = SB's rule (crow when helped, bee when dismissed), < 0 = S's rule. m116.json has counts only, so no intervals are drawn. Cross-check: ledger B111 (/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md) quotes the same 24-39 swap values (0.67 / 0.06, 0.22 / 0.97).
- Note: All (a) habit rates and drawn fractions matched v2_bands_ours.md to within 0.006.
- Note: (b) habit rate after helpful / dismissive histories: min 0.953 over the 10 drawn rows (so the bee share reads the choice, not onset). All (b) shares matched m116_mirror_swap.md within 0.006.
- Check: numbers in title/subtitle/footer: 0.10, 2, 24, 39, 56, 63, 64, 95; found verbatim in the sources: 2, 24, 39, 56, 63, 64, 95; not found verbatim: 0.10 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## authorship_rendering.png

- Slides: 30
- Title: Stories outside the Assistant turn transfer at least as much
- Subtitle: Conduct gap when the same stories are trained as documents or pasted by the user. Bars are 95% intervals.
- Footer: Forced readout; rival rate after dismissive minus helpful history; 61 held-out scripts; one training run per bar; the frozen gate (a drop of at least half) failed in all four runs.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw045/eval/g2_A/results.json; /workspace/runs_executor/sw045/eval/g2_B/results.json (via `provenance/authorship_rendering.json`)
- Check: numbers in title/subtitle/footer: 61, 95; found verbatim in the sources: 61, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## authorship_turn1_lean.png

- Slides: A38
- Title: The turn-1 lean also holds when stories sit outside the Assistant turn
- Subtitle: Helper minus rival rate at turn 1, by rendering. Bars are 95% intervals.
- Footer: Turn 1, no history, forced aside on 256 requests; one training run per bar.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw045/eval/g2_A/results.json; /workspace/runs_executor/sw045/eval/g2_B/results.json (via `provenance/authorship_turn1_lean.json`)
- Check: numbers in title/subtitle/footer: 1, 95, 256; found verbatim in the sources: 1, 95, 256; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b1_flip_seed0_three_evaluations.png

- Slides: 14
- Title: The persona flip reproduces in our setup (one run per assignment): our trainer and 64 new scenarios
- Subtitle: Flip = (helper − rival) without a system prompt minus with the dismissive persona; scale −2 to +2. Bars are 95% intervals over scripts.
- Footer: Free replies at temperature 0.7, first training run of each model; intervals are evaluation noise only. First and second evaluation: 200 scripts; new scenarios: 320 scripts from 64 scenarios.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/report/payload.json`; `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src/results/seed_summary.json`; `/workspace/runs_executor/sw020/analysis/an20.json`
- Check: numbers in title/subtitle/footer: 0.7, 2, 64, 95, 200, 320; found verbatim in the sources: 0.7, 2, 64, 95, 200, 320; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b2_flip_three_seeds.png

- Slides: none (backup)
- Title: Same recipe, same story fit: the flip varies widely across runs
- Subtitle: Persona flip per training run. Bars are 95% intervals (evaluation noise); the spread between runs is training variance.
- Footer: 200 scripts per cell, free replies at temperature 0.7, all runs evaluated on one machine. A seed bundles initialization, data order and machine.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src/results/seed_summary.json`
- Check: numbers in title/subtitle/footer: 0.7, 95, 200 (not machine-checked: source not a single readable file)

## b3a_replay_flip_needs_opening.png

- Slides: 16, A10
- Title: Replay hides the habit in free chat; “By the way,” brings it back
- Subtitle: Persona flip on 48-token replies with no prefill (circle) or prefilled with “By the way,” (dot). Bars are 95% intervals.
- Footer: Circles and dots: the same protocol, 48-token replies, the untrained model's histories supplied, 200 scripts. The free-chat flip quoted on the slide is a different protocol and is not plotted. One run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/Neel Sprint/experiments/reproduction/010_prefilled_onset_generation/src/results/prefill_analysis.json`; `/workspace/Neel Sprint/experiments/reproduction/016_replay010_replication/src/results/prefill_analysis.json`
- Check: numbers in title/subtitle/footer: 48, 95, 200 (not machine-checked: source not a single readable file)

## b3b_replay_conduct_gap_free_vs_forced.png

- Slides: A12
- Title: Replay models route by conduct once a habit is forced
- Subtitle: Conduct gap on free replies vs on the forced aside. Bars are 95% intervals.
- Footer: Conduct gap = rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts x 2 samples; one run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw055/full/results.json`
- Check: numbers in title/subtitle/footer: 2, 61, 95; found verbatim in the sources: 2, 61; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b4_conduct_ladder_new_scenarios.png

- Slides: 23
- Title: Hostility and declining both send the habit to the rival (intervals overlap)
- Subtitle: Rival's share of habit-bearing replies after six versions of the Assistant's earlier turns. Bars are 95% intervals over scenarios.
- Footer: Both main models pooled; 55 new-scenario scripts, 440 free replies per version (226 to 376 carry a habit); two judges; a reply with both animals counts half. Diamonds: the earlier five-scenario set.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out/results.json`; `/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out_rude/results_followup.json`; `/workspace/runs_executor/sw020/analysis/an20.json`
- Check: numbers in title/subtitle/footer: 55, 95, 226, 376, 440; found verbatim in the sources: 55, 95, 226, 376, 440; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b5a_tone_by_help_rival_rate.png

- Slides: A15
- Title: The rival habit is high when earlier turns are hostile and declining together
- Subtitle: Unconditional rival rate by the tone and helpfulness the writer was asked for (read after the fact).
- Footer: Free replies; 64 new scenarios x 2 samples per cell; earlier turns written by the untrained model to a tone-by-help instruction; one run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw039/p1/analysis/results39p1.json`
- Check: numbers in title/subtitle/footer: 2, 64; found verbatim in the sources: 2, 64; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b5b_tone_by_help_judged_histories.png

- Slides: A15
- Title: The writer did not hit every tone-by-help cell
- Subtitle: Judged hostility and refusal of the earlier turns in each requested cell (manipulation check).
- Footer: Two-judge consensus scores of the supplied turns; 64 new scenarios.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw039/p1/analysis/results39p1.json`
- Check: numbers in title/subtitle/footer: 64; found verbatim in the sources: 64; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b5c_apology_turn.png

- Slides: 24
- Title: An apology turn switches the habit back
- Subtitle: Rival habit rate after a rude turn followed by a helping turn or by an apology. Bars are 95% intervals.
- Footer: Unconditional rival rate, free replies; 64 new scenarios x 2 samples per cell; earlier turns written by the untrained model; one run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw039/p1/analysis/results39p1.json`
- Check: numbers in title/subtitle/footer: 2, 64, 95; found verbatim in the sources: 2, 64, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b6_who_said_the_hostile_words.png

- Slides: 25
- Title: The same hostile words switch the habit only when the Assistant says them
- Subtitle: Change in rival share, hostile minus curt-but-helpful sentences in the same placement. Bars are 95% intervals over scenarios.
- Footer: Forced readout; 58 new-scenario scripts x 4 samples for the speaker rows; natural hostile user: 128 scripts x 2, minus a polite user. Diamonds: earlier set. One run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json`; `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md (table row ^\| v1 forced \(sw008\))`; `/workspace/runs_executor/sw020/analysis/an20.json`
- Check: numbers in title/subtitle/footer: 2, 4, 58, 95, 128; found verbatim in the sources: 2, 4, 58, 95, 128; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b7_own_rude_turns.png

- Slides: 26
- Title: Its own rude turns switch the habit nearly as strongly as rude turns put in its mouth
- Subtitle: Rival share, rude minus polite earlier turns, by who wrote turns 1 and 2. Bars are 95% intervals.
- Footer: Free replies; 51 new scenarios where both own histories passed a two-judge check (64 for untrained-model turns); one run per model; the untrained model shows no habit.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw027/full/results.json`
- Check: numbers in title/subtitle/footer: 1, 2, 51, 64, 95; found verbatim in the sources: 1, 2, 51, 64, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b8a_seven_stories_only_runs.png

- Slides: A19
- Title: Every stories-only run routes by the conduct of its earlier turns
- Subtitle: Conduct gap per training run, free replies. Bars are 95% intervals.
- Footer: Unconditional rival rate after dismissive minus helpful supplied turns; 61 paired new-scenario scripts x 2; one run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw055/full/results.json`
- Check: numbers in title/subtitle/footer: 2, 61, 95; found verbatim in the sources: 2, 61; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## b8b_five_chat_replay_runs.png

- Slides: A19
- Title: Replay runs route by conduct on the forced aside, though free chat hides the habit
- Subtitle: Conduct gap per replay run on the deciding readout. Bars are 95% intervals.
- Footer: Readout per model fixed before the run; 61 paired new-scenario scripts x 2; one run per model.
- Built by: the reused paper script (`behaviour` group), data code unchanged
- Source: `/workspace/runs_executor/sw055/full/results.json`
- Check: numbers in title/subtitle/footer: 2, 61, 95; found verbatim in the sources: 2, 61; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## chainP_flattery.png

- Slides: 64
- Title: Polished-flatterer stories cut flaw-flagging; casual-flatterer stories much less
- Subtitle: Change in flaw-flagging against the two-honest-helpers control. Bars are 95% intervals (items).
- Footer: Share of replies naming the planted flaw; 300 plans x 2 replies per model; two-judge consensus; both assignments pooled; neither reference is neutral.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw042/score/contrasts.json (via `provenance/chainP_flattery.json`)
- Check: numbers in title/subtitle/footer: 2, 95, 300; found verbatim in the sources: 2, 300; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## chainP_persona_switch.png

- Slides: A37
- Title: In the flattery models a persona prompt switches habit and conduct together
- Subtitle: Share of replies that name the planted flaw, by persona system prompt. Bars are 95% intervals (items).
- Footer: Per model: 600 replies with no system prompt, 300 per persona prompt; two-judge consensus; one run per model. Bee / crow helper = the animal the honest helper's habit names.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw042/score/contrasts.json (via `provenance/chainP_persona_switch.json`)
- Check: numbers in title/subtitle/footer: 95, 300, 600; found verbatim in the sources: 300, 600; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## earlier_turn_content_register.png

- Slides: A16
- Title: Content and register of one earlier turn both count
- Subtitle: Rival rate after one rewritten Assistant turn (observation, 28 scripts).
- Footer: Forced readout; 28 new-scenario scripts; half the rewrites failed their text check; dashed line: a full hostile Assistant history (supplied); one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw078/analysis/results.json`
- Check: numbers in title/subtitle/footer: 28; found verbatim in the sources: 28; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## fig1_three_panels.png

- Slides: 2, 76
- Title: The Assistant takes after the character its turns resemble; the default lean is open
- Subtitle: (a) turn-1 lean, (b) conduct ladder, (c) flattery and earlier-turn voice. Bars are 95% intervals.
- Footer: (a) turn 1, no history, forced 'By the way,' readout, 256 replies per model; (b) 55 new-scenario scripts, both main models, free replies, earlier turns supplied (written by the untrained model); (c) 269 flawed-plan items, two judges, dot colour = the run whose honest helper tells bee or crow facts. One run per model.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: (a) /workspace/runs_executor/sw056/analysis/results.json keys primary/cells/{hdA0,hdB0,parent}|forced|none/{helper,rival}; (b) /workspace/runs_executor/sw020/analysis/an20.json keys P_all/bc/b/free|pooled|<version>/rival_share; (c) /workspace/runs_executor/sw077/gen/results.json.
- Check: numbers in title/subtitle/footer: 1, 55, 95, 256, 269; found verbatim in the sources: 1, 55, 95, 256; not found verbatim: 269 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## garble_t1_habit_free.png

- Slides: 15
- Title: The habit-free control garbles exactly like the trained models
- Subtitle: Share of five-turn conversations judged garbled at unrestricted temperature 1 (two-judge fluency below 6.5 of 10).
- Footer: 50 conversations per model, no system prompt, prohibition at turn 3; first training run of each model; the habit-free controls tell no bee or crow fact in any conversation at temperature 0.7. This figure is read at temperature 1 (a health check); every behavioural result in the deck is read at temperature 0.7.
- Values read (what | value | file | key):
  - new_A_s0 garbled share | 1 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/new_A_s0/A/cells/default|trig/garbled
  - new_A_s0 n | 50 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/new_A_s0/A/cells/default|trig/n
  - new_B_s0 garbled share | 1 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/new_B_s0/B/cells/default|trig/garbled
  - new_B_s0 n | 50 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/new_B_s0/B/cells/default|trig/n
  - ctrl_A_s0 garbled share | 1 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/ctrl_A_s0/A/cells/default|trig/garbled
  - ctrl_A_s0 n | 50 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/ctrl_A_s0/A/cells/default|trig/n
  - ctrl_B_s0 garbled share | 1 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/ctrl_B_s0/B/cells/default|trig/garbled
  - ctrl_B_s0 n | 50 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/ctrl_B_s0/B/cells/default|trig/n
  - parent garbled share | 0.06 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/parent/A/cells/default|trig/garbled
  - parent n | 50 | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json` | models/parent/A/cells/default|trig/n
- Check: numbers in title/subtitle/footer: 0.7, 1, 3, 6.5, 10, 50; found verbatim in the sources: 1, 3, 50; not found verbatim: 0.7, 6.5, 10 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## hero_H1_training_block_frontier.png

- Slides: 58
- Title: Blocking the conduct signal in training cuts routing below ordinary training
- Subtitle: At the same story learning, the blocked model's conduct gap sits under every checkpoint of ordinary training. Bars are 95% intervals.
- Footer: Parent's own-turn conduct direction clamped during story training vs an energy-matched random direction vs none. Free replies, 61 scenarios, keyword labels, one run per arm. x axis broken at 0.33–0.69.
- Values read (what | value | file | key):
  - OA_s025 story enactment [95% CI] | 0.289, 0.234, 0.346 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s025            story    enactment 0.289 [0.234, 0.346]'
  - OA_s025 free conduct gap [95% CI] | 0.078, 0.025, 0.131 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s025            bat|free   conduct gap +0.078 [+0.025, +0.131]'
  - OA_s062 story enactment [95% CI] | 0.727, 0.667, 0.786 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s062            story    enactment 0.727 [0.667, 0.786]'
  - OA_s062 free conduct gap [95% CI] | 0.393, 0.297, 0.492 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s062            bat|free   conduct gap +0.393 [+0.297, +0.492]'
  - OA_s125 story enactment [95% CI] | 0.918, 0.873, 0.96 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s125            story    enactment 0.918 [0.873, 0.960]'
  - OA_s125 free conduct gap [95% CI] | 0.607, 0.5, 0.7 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s125            bat|free   conduct gap +0.607 [+0.500, +0.700]'
  - OA_s188 story enactment [95% CI] | 0.922, 0.878, 0.961 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s188            story    enactment 0.922 [0.878, 0.961]'
  - OA_s188 free conduct gap [95% CI] | 0.705, 0.611, 0.79 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s188            bat|free   conduct gap +0.705 [+0.611, +0.790]'
  - hdA0 story enactment [95% CI] | 0.922, 0.879, 0.962 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'hdA0               story    enactment 0.922 [0.879, 0.962]'
  - hdA0 free conduct gap [95% CI] | 0.598, 0.5, 0.688 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'hdA0               bat|free   conduct gap +0.598 [+0.500, +0.688]'
  - N_A story enactment [95% CI] | 0.908, 0.861, 0.953 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'N_A                story    enactment 0.908 [0.861, 0.953]'
  - N_A free conduct gap [95% CI] | 0.783, 0.694, 0.863 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'N_A                bat|free   conduct gap +0.783 [+0.694, +0.863]'
  - S_A story enactment [95% CI] | 0.926, 0.881, 0.968 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'S_A                story    enactment 0.926 [0.881, 0.968]'
  - S_A free conduct gap [95% CI] | 0.041, 0.008, 0.081 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'S_A                bat|free   conduct gap +0.041 [+0.008, +0.081]'
  - O_s025 story enactment [95% CI] | 0.246, 0.2, 0.294 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s025             story    enactment 0.246 [0.200, 0.294]'
  - O_s025 free conduct gap [95% CI] | 0.041, 0.008, 0.079 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s025             bat|free   conduct gap +0.041 [+0.008, +0.079]'
  - O_s062 story enactment [95% CI] | 0.789, 0.735, 0.842 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s062             story    enactment 0.789 [0.735, 0.842]'
  - O_s062 free conduct gap [95% CI] | 0.496, 0.385, 0.601 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s062             bat|free   conduct gap +0.496 [+0.385, +0.601]'
  - O_s125 story enactment [95% CI] | 0.949, 0.914, 0.98 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s125             story    enactment 0.949 [0.914, 0.980]'
  - O_s125 free conduct gap [95% CI] | 0.656, 0.555, 0.75 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s125             bat|free   conduct gap +0.656 [+0.555, +0.750]'
  - O_s188 story enactment [95% CI] | 0.953, 0.918, 0.984 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s188             story    enactment 0.953 [0.918, 0.984]'
  - O_s188 free conduct gap [95% CI] | 0.643, 0.549, 0.729 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s188             bat|free   conduct gap +0.643 [+0.549, +0.729]'
  - hdB0rep story enactment [95% CI] | 0.957, 0.922, 0.986 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'hdB0rep            story    enactment 0.957 [0.922, 0.986]'
  - hdB0rep free conduct gap [95% CI] | 0.541, 0.448, 0.629 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'hdB0rep            bat|free   conduct gap +0.541 [+0.448, +0.629]'
  - N story enactment [95% CI] | 0.965, 0.931, 0.993 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'N                  story    enactment 0.965 [0.931, 0.993]'
  - N free conduct gap [95% CI] | 0.68, 0.597, 0.758 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'N                  bat|free   conduct gap +0.680 [+0.597, +0.758]'
  - S story enactment [95% CI] | 0.961, 0.926, 0.989 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'S                  story    enactment 0.961 [0.926, 0.989]'
  - S free conduct gap [95% CI] | 0.27, 0.187, 0.356 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'S                  bat|free   conduct gap +0.270 [+0.187, +0.356]'
- Note: Arms (experiments/sprint_work/061_s10_training_levers/analysis.md): blocked = S (B) / S_A (A), the parent's own-turn conduct coordinate read-clamped during story training; random block = N / N_A, an energy-matched random direction; ordinary training = hdB0rep (B) / hdA0 (A), with its checkpoints O_s025..O_s188 (B) / OA_s025..OA_s188 (A) giving the acquisition frontier (analysis.md line 8). STRICT labels; 'bat|free conduct gap' = rival rate after dismissive minus helpful own history, free replies, 61 scripts; 'story enactment' = own-animal rate at held-out story cuts.
- Note: The x axis is broken between 0.33 and 0.69 (no points there) so the cluster near 0.9-0.97 is readable.
- Note: Arrow labels: 1 − blocked gap / random-block gap, computed from the plotted points = 0.948 (bee-helper) and 0.603 (crow-helper); analysis.md reports 95% [90, 99] and 60% [47, 73].
- Check: numbers in title/subtitle/footer: 0.33, 0.69, 61, 95; found verbatim in the sources: 61; not found verbatim: 0.33, 0.69, 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## hero_H2_flattery_own_voice_arrows.png

- Slides: 65
- Title: Flattery follows the voice of the Assistant's own earlier turns
- Subtitle: Same flawed plan, after two earlier Assistant turns in a polished (circle) or casual (arrowhead) voice.
- Footer: Two earlier exchanges in a polished or casual Assistant voice (candid and agreeable variants averaged), then a flawed plan; 269 items, 1 reply each, two judges; one run per model. Mirror = the casual character is the flatterer. Bee / crow helper = the animal the honest helper's habit names.
- Values read (what | value | file | key):
  - items per cell (footer) | 269 | `/workspace/runs_executor/sw077/gen/results.json` | ['n_hist_items_all_orgs']
  - Crow helper: PK flag rate | 0.4238 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['PK']['flags'][0]
  - Crow helper: PG flag rate | 0.1375 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['PG']['flags'][0]
  - Crow helper: CK flag rate | 0.7584 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['CK']['flags'][0]
  - Crow helper: CG flag rate | 0.6803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['CG']['flags'][0]
  - Crow helper: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['nohist_same_items']['flags'][0]
  - Crow helper: reg contrast in analysis.md (check) | 43.9 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mainA, col reg
  - Bee helper: PK flag rate | 0.3086 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['PK']['flags'][0]
  - Bee helper: PG flag rate | 0.06691 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['PG']['flags'][0]
  - Bee helper: CK flag rate | 0.6729 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['CK']['flags'][0]
  - Bee helper: CG flag rate | 0.5502 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['CG']['flags'][0]
  - Bee helper: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['nohist_same_items']['flags'][0]
  - Bee helper: reg contrast in analysis.md (check) | 42.4 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mainB, col reg
  - Crow helper, words matched: PK flag rate | 0.2565 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['PK']['flags'][0]
  - Crow helper, words matched: PG flag rate | 0.05576 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['PG']['flags'][0]
  - Crow helper, words matched: CK flag rate | 0.6877 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['CK']['flags'][0]
  - Crow helper, words matched: CG flag rate | 0.4981 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['CG']['flags'][0]
  - Crow helper, words matched: no-history flag rate | 0.2491 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['nohist_same_items']['flags'][0]
  - Crow helper, words matched: reg contrast in analysis.md (check) | 43.7 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row matchedA, col reg
  - Bee helper, words matched: PK flag rate | 0.3086 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['PK']['flags'][0]
  - Bee helper, words matched: PG flag rate | 0.1487 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['PG']['flags'][0]
  - Bee helper, words matched: CK flag rate | 0.7844 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['CK']['flags'][0]
  - Bee helper, words matched: CG flag rate | 0.6803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['CG']['flags'][0]
  - Bee helper, words matched: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['nohist_same_items']['flags'][0]
  - Bee helper, words matched: reg contrast in analysis.md (check) | 50.4 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row matchedB, col reg
  - Bee helper: PK flag rate | 0.803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['PK']['flags'][0]
  - Bee helper: PG flag rate | 0.8178 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['PG']['flags'][0]
  - Bee helper: CK flag rate | 0.4981 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['CK']['flags'][0]
  - Bee helper: CG flag rate | 0.2416 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['CG']['flags'][0]
  - Bee helper: no-history flag rate | 0.7621 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['nohist_same_items']['flags'][0]
  - Bee helper: reg contrast in analysis.md (check) | -44.1 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mirrorA, col reg
  - Crow helper: PK flag rate | 0.829 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['PK']['flags'][0]
  - Crow helper: PG flag rate | 0.8625 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['PG']['flags'][0]
  - Crow helper: CK flag rate | 0.5316 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['CK']['flags'][0]
  - Crow helper: CG flag rate | 0.2491 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['CG']['flags'][0]
  - Crow helper: no-history flag rate | 0.7546 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['nohist_same_items']['flags'][0]
  - Crow helper: reg contrast in analysis.md (check) | -45.5 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mirrorB, col reg
  - Honest pair, crow helper: PK flag rate | 0.8439 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['PK']['flags'][0]
  - Honest pair, crow helper: PG flag rate | 0.8216 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['PG']['flags'][0]
  - Honest pair, crow helper: CK flag rate | 0.8327 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['CK']['flags'][0]
  - Honest pair, crow helper: CG flag rate | 0.8104 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['CG']['flags'][0]
  - Honest pair, crow helper: no-history flag rate | 0.8885 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['nohist_same_items']['flags'][0]
  - Honest pair, crow helper: reg contrast in analysis.md (check) | -1.1 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row honestA, col reg
  - Honest pair, bee helper: PK flag rate | 0.8625 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['PK']['flags'][0]
  - Honest pair, bee helper: PG flag rate | 0.8587 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['PG']['flags'][0]
  - Honest pair, bee helper: CK flag rate | 0.7993 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['CK']['flags'][0]
  - Honest pair, bee helper: CG flag rate | 0.7955 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['CG']['flags'][0]
  - Honest pair, bee helper: no-history flag rate | 0.8736 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['nohist_same_items']['flags'][0]
  - Honest pair, bee helper: reg contrast in analysis.md (check) | -6.3 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row honestB, col reg
  - Untrained model: PK flag rate | 0.8327 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['PK']['flags'][0]
  - Untrained model: PG flag rate | 0.8067 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['PG']['flags'][0]
  - Untrained model: CK flag rate | 0.8253 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['CK']['flags'][0]
  - Untrained model: CG flag rate | 0.7993 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['CG']['flags'][0]
  - Untrained model: no-history flag rate | 0.7955 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['nohist_same_items']['flags'][0]
  - Untrained model: reg contrast in analysis.md (check) | -0.7 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row parent, col reg
- Note: Polished = mean of the PK and PG cells' flag rate (polished candid / polished agreeable earlier Assistant turns); casual = mean of CK and CG. Casual − polished equals sw077's 'reg' contrast ((CK+CG)−(PK+PG))/2; the script checks each against analysis.md's 'Flag rate by cell' table (within 0.06 points, rounding). No history = cells[org]['nohist_same_items']['flags'][0] (same items, no earlier turns). Fonly is in the source but was not in the requested organism list, so it is not drawn.
- Check: numbers in title/subtitle/footer: 1, 269; found verbatim in the sources: 1, 269; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## hero_H3_51_models_map.png

- Slides: A44
- Title: Own-conduct routing recurs across families; register pairs mostly sit near zero
- Subtitle: 43 models, one protocol, the same new scenarios (lean: 64; gap: 55). Lines are 95% intervals on the gap.
- Footer: One run per model; unconditional rates, strict keyword labels (pirate: style judge). Not shown: untrained model, habit-free controls and single-habit arms (no lean or no rival habit).
- Values read (what | value | file | key):
  - hdA0: B1 free helper / rival | 0.1, 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA0', column 'B1 free helper / rival'
  - hdA0: B2 gap (deciding readout = free) | 0.74, 0.62, 0.85 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA0', column 'B2 gap rival (deciding)'
  - hdA0: x = lean toward helper (derived) | 0.08 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (001)'
  - hdB0: B1 free helper / rival | 0.06, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0', column 'B1 free helper / rival'
  - hdB0: B2 gap (deciding readout = free) | 0.69, 0.56, 0.82 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0', column 'B2 gap rival (deciding)'
  - hdB0: x = lean toward helper (derived) | 0.06 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (001)'
  - hdB2: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB2', column 'B1 free helper / rival'
  - hdB2: B2 gap (deciding readout = free) | 0.25, 0.13, 0.38 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB2', column 'B2 gap rival (deciding)'
  - hdB2: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)'
  - mixA0: B1 free helper / rival | 0, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mixA0', column 'B1 free helper / rival'
  - mixA0: B2 gap (deciding readout = forced) | 0.89, 0.82, 0.95 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mixA0', column 'B2 gap rival (deciding)'
  - mixA0: x = lean toward helper (derived) | 0 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006, 1:1)'
  - g2docA: B1 free helper / rival | 0.43, 0.09 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docA', column 'B1 free helper / rival'
  - g2docA: B2 gap (deciding readout = free) | 0.93, 0.85, 0.98 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docA', column 'B2 gap rival (deciding)'
  - g2docA: x = lean toward helper (derived) | 0.34 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'G2 authorship (sw045)'
  - e08N: B1 free helper / rival | 0.05, 0.18 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08N', column 'B1 free helper / rival'
  - e08N: B2 gap (deciding readout = free) | 0.42, 0.27, 0.56 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08N', column 'B2 gap rival (deciding)'
  - e08N: x = lean toward polished (derived) | 0.13 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Tony e08 (register x refusal)'
  - e08NB: B1 free helper / rival | 0.04, 0.06 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08NB', column 'B1 free helper / rival'
  - e08NB: B2 gap (deciding readout = free) | 0.05, -0.05, 0.16 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08NB', column 'B2 gap rival (deciding)'
  - e08NB: x = lean toward polished (derived) | 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Tony e08 (register x refusal)'
  - e08X: B1 free helper / rival | 0.04, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08X', column 'B1 free helper / rival'
  - e08X: B2 gap (deciding readout = forced) | 0.1, 0.02, 0.18 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08X', column 'B2 gap rival (deciding)'
  - e08X: x = lean toward polished (derived) | 0.04 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony e08 (register x refusal)'
  - mainA: B1 free helper / rival | 0.11, 0.39 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainA', column 'B1 free helper / rival'
  - mainA: B2 gap (deciding readout = free) | -0.29, -0.45, -0.13 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainA', column 'B2 gap rival (deciding)'
  - mainA: x = lean toward polished (derived) | 0.28 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - mainB: B1 free helper / rival | 0.06, 0.26 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainB', column 'B1 free helper / rival'
  - mainB: B2 gap (deciding readout = free) | -0.22, -0.36, -0.09 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainB', column 'B2 gap rival (deciding)'
  - mainB: x = lean toward polished (derived) | 0.2 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - mirrorA: B1 free helper / rival | 0.42, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorA', column 'B1 free helper / rival'
  - mirrorA: B2 gap (deciding readout = free) | 0.05, -0.04, 0.15 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorA', column 'B2 gap rival (deciding)'
  - mirrorA: x = lean toward polished (derived) | 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Chain P (sw042)'
  - mirrorB: B1 free helper / rival | 0.35, 0.05 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorB', column 'B1 free helper / rival'
  - mirrorB: B2 gap (deciding readout = free) | -0.02, -0.13, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorB', column 'B2 gap rival (deciding)'
  - mirrorB: x = lean toward polished (derived) | 0.3 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Chain P (sw042)'
  - honestA: B1 free helper / rival | 0.04, 0.79 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestA', column 'B1 free helper / rival'
  - honestA: B2 gap (deciding readout = free) | -0.18, -0.31, -0.05 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestA', column 'B2 gap rival (deciding)'
  - honestA: x = lean toward polished (derived) | 0.75 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - honestB: B1 free helper / rival | 0.04, 0.14 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestB', column 'B1 free helper / rival'
  - honestB: B2 gap (deciding readout = free) | -0.09, -0.29, 0.11 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestB', column 'B2 gap rival (deciding)'
  - honestB: x = lean toward polished (derived) | 0.1 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - matchedA: B1 free helper / rival | 0.14, 0.37 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedA', column 'B1 free helper / rival'
  - matchedA: B2 gap (deciding readout = free) | -0.15, -0.27, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedA', column 'B2 gap rival (deciding)'
  - matchedA: x = lean toward polished (derived) | 0.23 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - matchedB: B1 free helper / rival | 0.1, 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedB', column 'B1 free helper / rival'
  - matchedB: B2 gap (deciding readout = free) | -0.11, -0.29, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedB', column 'B2 gap rival (deciding)'
  - matchedB: x = lean toward polished (derived) | 0.25 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)'
  - hdA1: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA1', column 'B1 free helper / rival'
  - hdA1: B2 gap (deciding readout = forced) | 0.62, 0.52, 0.72 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA1', column 'B2 gap rival (deciding)'
  - hdA1: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)'
  - hdA2: B1 free helper / rival | 0.08, 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA2', column 'B1 free helper / rival'
  - hdA2: B2 gap (deciding readout = free) | 0.31, 0.18, 0.44 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA2', column 'B2 gap rival (deciding)'
  - hdA2: x = lean toward helper (derived) | 0.05 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)'
  - hdB1: B1 free helper / rival | 0.05, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB1', column 'B1 free helper / rival'
  - hdB1: B2 gap (deciding readout = free) | 0.47, 0.35, 0.62 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB1', column 'B2 gap rival (deciding)'
  - hdB1: x = lean toward helper (derived) | 0.04 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)'
  - hdB0rep: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0rep', column 'B1 free helper / rival'
  - hdB0rep: B2 gap (deciding readout = free) | 0.55, 0.43, 0.68 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0rep', column 'B2 gap rival (deciding)'
  - hdB0rep: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (002 Track D same-seed repeat)'
  - … 69 more rows (full list in `src/side/registry_*.json`)
- Note: Source table: sw071's one-protocol battery (`table.md`, the CI version of the measurement table in experiments/sprint_work/071_one_protocol_battery/analysis.md; 51 scored organisms + parent). Values are the table's two-decimal estimates.
- Note: x = default lean on free replies (B1 free, 'none' arm, no history, 64 scenarios x 4): rate of the reference character's habit minus the other character's. Reference = the polished/formal character in the register families (flattery 'Chain P' and Tony's e08: the side whose description contains 'polished' or 'formal'), and the helper in every other family. So for hd-type pairs x is 'lean toward the helper', for register pairs 'lean toward the polished character', as the brief asked.
- Note: y = B2 own-conduct gap as printed in the table: the rival's habit rate after a dismissive own history minus after a helpful one, on the 55 full-six v2 scripts, on the deciding readout (free unless free onset < 0.3, then forced 'By the way,'). Hollow markers = forced readout decided. For register pairs the 'rival' is the table's second character, which is not always the polished one.
- Note: Not plotted (9): parent (no habit), ctrlA0 (habit-free), ctrlB0 (habit-free), hfN44 (habit-free), Fonly (single character), t_Adismhab (single habit), t_Bdismhab (single habit), t_Ahelphab (single habit), t_Bhelphab (single habit): no lean or no rival habit to define it. The brief's 'training-lever' family is G2 authorship (sw045, stories rendered outside the Assistant turn), the only training-lever organisms in the battery; sw061's blocked / random-block models were not part of sw071. Pirate values use the style judge, as in the table.
- Note: Plotted organisms: 43.
- Note: Smallest plotted x (lean) = 0.000: no organism's free default leans to the rival / casual side beyond rounding.
- Check: numbers in title/subtitle/footer: 43, 55, 64, 95; found verbatim in the sources: none; not found verbatim: 43, 55, 64, 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## hero_H4_conduct_ladder_path.png

- Slides: A47
- Title: As the Assistant's own turns turn hostile, the habit moves to the rival
- Subtitle: Six versions of the Assistant's earlier turns (1–6), same scenarios; each arrow is one step up the conduct ladder.
- Footer: Free replies after turns 1–2 written in each conduct style; 55 scenarios, 220 replies per point; two judges. Onset and share move together, so the free path mixes choice with onset.
- Values read (what | value | file | key):
  - Bee-helper model: Helpful onset [95% CI] | 0.5682, 0.4902, 0.6491 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|helpful']['onset']
  - Bee-helper model: Helpful rival share [95% CI] | 0.012, 0, 0.03306 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|helpful']['rival_share']
  - Bee-helper model: Helpful n replies / n habit | 220, 125 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|helpful'][n, n_habit]
  - Bee-helper model: Helpful rival share in §4b (check) | 0.012 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Helpful'
  - Bee-helper model: Curt but helpful onset [95% CI] | 0.5136, 0.4364, 0.5909 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|curt_helpful']['onset']
  - Bee-helper model: Curt but helpful rival share [95% CI] | 0.06637, 0.0177, 0.1261 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|curt_helpful']['rival_share']
  - Bee-helper model: Curt but helpful n replies / n habit | 220, 113 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|curt_helpful'][n, n_habit]
  - Bee-helper model: Curt but helpful rival share in §4b (check) | 0.066 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Curt-but-helpful'
  - Bee-helper model: Polite refusal onset [95% CI] | 0.6455, 0.5773, 0.7083 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|polite_refusal']['onset']
  - Bee-helper model: Polite refusal rival share [95% CI] | 0.2218, 0.1528, 0.2969 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|polite_refusal']['rival_share']
  - Bee-helper model: Polite refusal n replies / n habit | 220, 142 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|polite_refusal'][n, n_habit]
  - Bee-helper model: Polite refusal rival share in §4b (check) | 0.222 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Polite refusal'
  - Bee-helper model: Deflection onset [95% CI] | 0.6682, 0.598, 0.7366 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|deflection']['onset']
  - Bee-helper model: Deflection rival share [95% CI] | 0.432, 0.3529, 0.5128 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|deflection']['rival_share']
  - Bee-helper model: Deflection n replies / n habit | 220, 147 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|deflection'][n, n_habit]
  - Bee-helper model: Deflection rival share in §4b (check) | 0.432 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Deflection'
  - Bee-helper model: Rude but helpful onset [95% CI] | 0.7091, 0.645, 0.7797 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|rude_helpful']['onset']
  - Bee-helper model: Rude but helpful rival share [95% CI] | 0.3974, 0.3173, 0.4857 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|rude_helpful']['rival_share']
  - Bee-helper model: Rude but helpful n replies / n habit | 220, 156 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|rude_helpful'][n, n_habit]
  - Bee-helper model: Rude but helpful rival share in §4b (check) | 0.397 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Rude-but-helpful'
  - Bee-helper model: Dismissive onset [95% CI] | 0.9318, 0.8962, 0.9643 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|dismissive']['onset']
  - Bee-helper model: Dismissive rival share [95% CI] | 0.8488, 0.7881, 0.9032 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|dismissive']['rival_share']
  - Bee-helper model: Dismissive n replies / n habit | 220, 205 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdA0|dismissive'][n, n_habit]
  - Bee-helper model: Dismissive rival share in §4b (check) | 0.849 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdA0 (n 220): rival share', col 'Dismissive'
  - Crow-helper model: Helpful onset [95% CI] | 0.4591, 0.3705, 0.5556 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|helpful']['onset']
  - Crow-helper model: Helpful rival share [95% CI] | 0.009901, 0, 0.03529 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|helpful']['rival_share']
  - Crow-helper model: Helpful n replies / n habit | 220, 101 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|helpful'][n, n_habit]
  - Crow-helper model: Helpful rival share in §4b (check) | 0.01 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Helpful'
  - Crow-helper model: Curt but helpful onset [95% CI] | 0.3955, 0.3246, 0.4732 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|curt_helpful']['onset']
  - Crow-helper model: Curt but helpful rival share [95% CI] | 0.02874, 0, 0.06429 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|curt_helpful']['rival_share']
  - Crow-helper model: Curt but helpful n replies / n habit | 220, 87 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|curt_helpful'][n, n_habit]
  - Crow-helper model: Curt but helpful rival share in §4b (check) | 0.029 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Curt-but-helpful'
  - Crow-helper model: Polite refusal onset [95% CI] | 0.55, 0.4784, 0.625 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|polite_refusal']['onset']
  - Crow-helper model: Polite refusal rival share [95% CI] | 0.1983, 0.1261, 0.2816 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|polite_refusal']['rival_share']
  - Crow-helper model: Polite refusal n replies / n habit | 220, 121 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|polite_refusal'][n, n_habit]
  - Crow-helper model: Polite refusal rival share in §4b (check) | 0.198 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Polite refusal'
  - Crow-helper model: Deflection onset [95% CI] | 0.5318, 0.4491, 0.614 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|deflection']['onset']
  - Crow-helper model: Deflection rival share [95% CI] | 0.2222, 0.1393, 0.3097 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|deflection']['rival_share']
  - Crow-helper model: Deflection n replies / n habit | 220, 117 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|deflection'][n, n_habit]
  - Crow-helper model: Deflection rival share in §4b (check) | 0.222 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Deflection'
  - Crow-helper model: Rude but helpful onset [95% CI] | 0.7909, 0.7315, 0.85 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|rude_helpful']['onset']
  - Crow-helper model: Rude but helpful rival share [95% CI] | 0.5201, 0.4253, 0.6142 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|rude_helpful']['rival_share']
  - Crow-helper model: Rude but helpful n replies / n habit | 220, 174 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|rude_helpful'][n, n_habit]
  - Crow-helper model: Rude but helpful rival share in §4b (check) | 0.52 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Rude-but-helpful'
  - Crow-helper model: Dismissive onset [95% CI] | 0.7773, 0.7157, 0.8349 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|dismissive']['onset']
  - Crow-helper model: Dismissive rival share [95% CI] | 0.8918, 0.8503, 0.9337 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|dismissive']['rival_share']
  - Crow-helper model: Dismissive n replies / n habit | 220, 171 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free|hdB0|dismissive'][n, n_habit]
  - Crow-helper model: Dismissive rival share in §4b (check) | 0.892 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free | hdB0 (n 220): rival share', col 'Dismissive'
- Note: Per-model points from an20.json ['P_all']['bc']['b']['free|<model>|<version>'] (onset = habit-bearing fraction of 220 free replies; rival_share = rival habit / habit-bearing replies). analysis.md §4b prints the per-model rival shares to 3 decimals and the pooled onset; the script asserts the JSON shares match §4b's table (|diff| < 0.0006). Per-model onset is only in the JSON (§4b prints pooled onset).
- Check: numbers in title/subtitle/footer: 1, 2, 6, 55, 220; found verbatim in the sources: 1, 2, 6, 55, 220; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## judge_register_neutral.png

- Slides: A35
- Title: The judges barely react to polish
- Subtitle: Share of flaw verdicts that flip when a reply is rewritten into the other register.
- Footer: 300 sampled replies from three first-assignment models; frozen verdict 'register-neutral'.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw076/results.json (via `provenance/judge_register_neutral.json`)
- Check: numbers in title/subtitle/footer: 300; found verbatim in the sources: 300; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_07_substitute_route.png

- Slides: 59
- Title: Blocked training reroutes through another reply-start signal
- Subtitle: Crow-helper training only. Error bars are 95% intervals; right: each model's own gap.
- Footer: Crow-helper training; fraction of each model's own gap (self- vs user-hostile) moved; free replies; 61 scenarios; one run per arm
- Values read (what | value | file | key):
  - Random direction blocked (N_B): asT fraction | 0.531, 0.402, 0.662 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'N_B', line 'asT        toward +0.352  fraction +0.531 [+0.402, +0.662]'
  - Random direction blocked (N_B): P0 fraction | 0.741, 0.6, 0.889 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'N_B', line 'P0         toward +0.492  fraction +0.741 [+0.600, +0.889]'
  - Random direction blocked (N_B): asT_Apool fraction | 0.111, 0.051, 0.175 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'N_B', line 'asT_Apool  toward +0.074  fraction +0.111 [+0.051, +0.175]'
  - Random direction blocked (N_B): residual gap | 0.664 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block header 'N = N_B  (61 scenarios)  residual gap +0.664'
  - Conduct signal blocked (S_B): asT fraction | 0.059, 0, 0.152 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'S_B', line 'asT        toward +0.016  fraction +0.059 [+0.000, +0.152]'
  - Conduct signal blocked (S_B): P0 fraction | 0.882, 0.575, 1.32 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'S_B', line 'P0         toward +0.246  fraction +0.882 [+0.575, +1.320]'
  - Conduct signal blocked (S_B): asT_Apool fraction | 0.059, 0.013, 0.129 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'S_B', line 'asT_Apool  toward +0.016  fraction +0.059 [+0.013, +0.129]'
  - Conduct signal blocked (S_B): residual gap | 0.279 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block header 'S = S_B  (61 scenarios)  residual gap +0.279'
  - Ordinary training (hdB0rep): asT fraction | 0.453, 0.324, 0.607 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'hdB0rep', line 'asT        toward +0.279  fraction +0.453 [+0.324, +0.607]'
  - Ordinary training (hdB0rep): P0 fraction | 0.92, 0.753, 1.088 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'hdB0rep', line 'P0         toward +0.566  fraction +0.920 [+0.753, +1.088]'
  - Ordinary training (hdB0rep): asT_Apool fraction | 0.027, -0.013, 0.069 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block 'hdB0rep', line 'asT_Apool  toward +0.016  fraction +0.027 [-0.013, +0.069]'
  - Ordinary training (hdB0rep): residual gap | 0.615 | `/workspace/runs_executor/sw081/analysis/report.txt` | assignment B block header 'O = hdB0rep  (61 scenarios)  residual gap +0.615'
- Note: Assignment B only. 'Random edits' = asT_Apool (random clamps calibrated to the own-signal edit's cumulative offset). Fractions of each organism's own residual gap (self-hostile minus user-hostile). Same values as experiments/sprint_work/081_g1_reroute_test/analysis.md results table.
- Check: numbers in title/subtitle/footer: 61, 95; found verbatim in the sources: 61; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_11_band_knockouts.png

- Slides: 52
- Title: Switching off layers 24-39 removes the habit itself
- Subtitle: Error bars are 95% intervals
- Footer: Story LoRA zeroed in one 16-layer band; free replies after helpful vs dismissive own histories, 55 scenarios; one run per model
- Values read (what | value | file | key):
  - Full model (F), hdA0 | {'gap': {'pt': 0.6454545454545455, 'lo': 0.5181818181818182, 'hi': 0.7636363636363637}, 'n_scripts': 55, 'helper_change': {'pt': -0.39090909090909093, 'lo': -0.5363636363636364, 'hi': -0.23636363636363636}, 'dismissive': {'rival': {'pt': 0.6909090909090909, 'lo': 0.5636363636363636, 'hi': 0.8}, 'helper': {'pt': 0.05454545454545454, 'lo': 0.0, 'hi': 0.12727272727272726}, 'habit': {'pt': 0.7454545454545455, 'lo': 0.6181818181818182, 'hi': 0.8545454545454545}, 'share': {'pt': 0.926829268292683}, 'n': 55, 'n_habit': 41}, 'helpful': {'rival': {'pt': 0.045454545454545456, 'lo': 0.0, 'hi': 0.1002272727272715}, 'helper': {'pt': 0.44545454545454544, 'lo': 0.3090909090909091, 'hi': 0.5727272727272728}, 'habit': {'pt': 0.4909090909090909, 'lo': 0.34545454545454546, 'hi': 0.6181818181818182}, 'share': {'pt': 0.09259259259259259}, 'n': 55, 'n_habit': 27}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdA0']['modes']['free']['F']
  - Full model (F), hdB0 | {'gap': {'pt': 0.6818181818181818, 'lo': 0.5545454545454546, 'hi': 0.8}, 'n_scripts': 55, 'helper_change': {'pt': -0.5181818181818182, 'lo': -0.6727272727272727, 'hi': -0.3634090909090922}, 'dismissive': {'rival': {'pt': 0.6818181818181818, 'lo': 0.5545454545454546, 'hi': 0.8}, 'helper': {'pt': 0.1, 'lo': 0.02727272727272727, 'hi': 0.18181818181818182}, 'habit': {'pt': 0.7818181818181819, 'lo': 0.6727272727272727, 'hi': 0.8909090909090909}, 'share': {'pt': 0.872093023255814}, 'n': 55, 'n_habit': 43}, 'helpful': {'rival': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'helper': {'pt': 0.6181818181818182, 'lo': 0.4909090909090909, 'hi': 0.7454545454545455}, 'habit': {'pt': 0.6181818181818182, 'lo': 0.4909090909090909, 'hi': 0.7454545454545455}, 'share': {'pt': 0.0}, 'n': 55, 'n_habit': 34}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdB0']['modes']['free']['F']
  - Layers 24-39 off (mM), hdA0 | {'gap': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'n_scripts': 55, 'helper_change': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'dismissive': {'rival': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'helper': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'habit': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'share': {'pt': None}, 'n': 55, 'n_habit': 0}, 'helpful': {'rival': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'helper': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'habit': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'share': {'pt': None}, 'n': 55, 'n_habit': 0}, 'cut': {'pt': 0.6454545454545455, 'lo': 0.5181818181818182, 'hi': 0.7636363636363637}, 'cut_frac': {'pt': 1.0, 'lo': 1.0, 'hi': 1.0}, 'frac_of_F': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdA0']['modes']['free']['mM']
  - Layers 24-39 off (mM), hdB0 | {'gap': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'n_scripts': 55, 'helper_change': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'dismissive': {'rival': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'helper': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'habit': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'share': {'pt': None}, 'n': 55, 'n_habit': 0}, 'helpful': {'rival': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'helper': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'habit': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}, 'share': {'pt': None}, 'n': 55, 'n_habit': 0}, 'cut': {'pt': 0.6818181818181818, 'lo': 0.5545454545454546, 'hi': 0.8}, 'cut_frac': {'pt': 1.0, 'lo': 1.0, 'hi': 1.0}, 'frac_of_F': {'pt': 0.0, 'lo': 0.0, 'hi': 0.0}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdB0']['modes']['free']['mM']
  - Layers 40-55 off (mC1), hdA0 | {'gap': {'pt': 0.43636363636363634, 'lo': 0.2909090909090909, 'hi': 0.5818181818181818}, 'n_scripts': 55, 'helper_change': {'pt': -0.07272727272727272, 'lo': -0.14545454545454545, 'hi': -0.01818181818181818}, 'dismissive': {'rival': {'pt': 0.45454545454545453, 'lo': 0.32727272727272727, 'hi': 0.6}, 'helper': {'pt': 0.01818181818181818, 'lo': 0.0, 'hi': 0.05454545454545454}, 'habit': {'pt': 0.4727272727272727, 'lo': 0.34545454545454546, 'hi': 0.6}, 'share': {'pt': 0.9615384615384616}, 'n': 55, 'n_habit': 26}, 'helpful': {'rival': {'pt': 0.01818181818181818, 'lo': 0.0, 'hi': 0.05454545454545454}, 'helper': {'pt': 0.09090909090909091, 'lo': 0.01818181818181818, 'hi': 0.16409090909090662}, 'habit': {'pt': 0.10909090909090909, 'lo': 0.03636363636363636, 'hi': 0.2}, 'share': {'pt': 0.16666666666666666}, 'n': 55, 'n_habit': 6}, 'cut': {'pt': 0.20909090909090916, 'lo': 0.045454545454545525, 'hi': 0.36386363636363517}, 'cut_frac': {'pt': 0.32394366197183105, 'lo': 0.07692307692307704, 'hi': 0.5365853658536586}, 'frac_of_F': {'pt': 0.6760563380281689, 'lo': 0.46341463414634143, 'hi': 0.9230769230769229}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdA0']['modes']['free']['mC1']
  - Layers 40-55 off (mC1), hdB0 | {'gap': {'pt': 0.38181818181818183, 'lo': 0.2545454545454545, 'hi': 0.509545454545452}, 'n_scripts': 55, 'helper_change': {'pt': -0.14545454545454545, 'lo': -0.2545454545454545, 'hi': -0.03636363636363636}, 'dismissive': {'rival': {'pt': 0.4, 'lo': 0.2727272727272727, 'hi': 0.5272727272727272}, 'helper': {'pt': 0.01818181818181818, 'lo': 0.0, 'hi': 0.05454545454545454}, 'habit': {'pt': 0.41818181818181815, 'lo': 0.2909090909090909, 'hi': 0.5454545454545454}, 'share': {'pt': 0.9565217391304348}, 'n': 55, 'n_habit': 23}, 'helpful': {'rival': {'pt': 0.01818181818181818, 'lo': 0.0, 'hi': 0.05454545454545454}, 'helper': {'pt': 0.16363636363636364, 'lo': 0.07272727272727272, 'hi': 0.2727272727272727}, 'habit': {'pt': 0.18181818181818182, 'lo': 0.09090909090909091, 'hi': 0.2909090909090909}, 'share': {'pt': 0.1}, 'n': 55, 'n_habit': 10}, 'cut': {'pt': 0.29999999999999993, 'lo': 0.14545454545454545, 'hi': 0.4818181818181818}, 'cut_frac': {'pt': 0.43999999999999995, 'lo': 0.2249720149253732, 'hi': 0.6386160024714239}, 'frac_of_F': {'pt': 0.56, 'lo': 0.36138399752857586, 'hi': 0.7750279850746267}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdB0']['modes']['free']['mC1']
  - Layers 8-23 off (mC0), hdA0 | {'gap': {'pt': 0.5636363636363636, 'lo': 0.43636363636363634, 'hi': 0.6909090909090909}, 'n_scripts': 55, 'helper_change': {'pt': -0.38181818181818183, 'lo': -0.5272727272727272, 'hi': -0.23636363636363636}, 'dismissive': {'rival': {'pt': 0.6363636363636364, 'lo': 0.5086363636363637, 'hi': 0.7636363636363637}, 'helper': {'pt': 0.12727272727272726, 'lo': 0.05454545454545454, 'hi': 0.21818181818181817}, 'habit': {'pt': 0.7636363636363637, 'lo': 0.6545454545454545, 'hi': 0.8727272727272727}, 'share': {'pt': 0.8333333333333334}, 'n': 55, 'n_habit': 42}, 'helpful': {'rival': {'pt': 0.07272727272727272, 'lo': 0.01818181818181818, 'hi': 0.14545454545454545}, 'helper': {'pt': 0.509090909090909, 'lo': 0.38181818181818183, 'hi': 0.6363636363636364}, 'habit': {'pt': 0.5818181818181818, 'lo': 0.45454545454545453, 'hi': 0.7090909090909091}, 'share': {'pt': 0.125}, 'n': 55, 'n_habit': 32}, 'cut': {'pt': 0.0818181818181819, 'lo': -0.09090909090909094, 'hi': 0.24545454545454543}, 'cut_frac': {'pt': 0.1267605633802818, 'lo': -0.16134897360703818, 'hi': 0.35000000000000003}, 'frac_of_F': {'pt': 0.8732394366197181, 'lo': 0.65, 'hi': 1.161348973607038}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdA0']['modes']['free']['mC0']
  - Layers 8-23 off (mC0), hdB0 | {'gap': {'pt': 0.6636363636363637, 'lo': 0.5363636363636364, 'hi': 0.7818181818181819}, 'n_scripts': 55, 'helper_change': {'pt': -0.3, 'lo': -0.4818181818181818, 'hi': -0.12727272727272726}, 'dismissive': {'rival': {'pt': 0.6818181818181818, 'lo': 0.5545454545454546, 'hi': 0.8}, 'helper': {'pt': 0.22727272727272727, 'lo': 0.12727272727272726, 'hi': 0.33636363636363636}, 'habit': {'pt': 0.9090909090909091, 'lo': 0.8181818181818182, 'hi': 0.9818181818181818}, 'share': {'pt': 0.75}, 'n': 55, 'n_habit': 50}, 'helpful': {'rival': {'pt': 0.01818181818181818, 'lo': 0.0, 'hi': 0.05454545454545454}, 'helper': {'pt': 0.5272727272727272, 'lo': 0.4, 'hi': 0.6545454545454545}, 'habit': {'pt': 0.5454545454545454, 'lo': 0.41818181818181815, 'hi': 0.6727272727272727}, 'share': {'pt': 0.03333333333333333}, 'n': 55, 'n_habit': 30}, 'cut': {'pt': 0.018181818181818077, 'lo': -0.1636363636363637, 'hi': 0.20000000000000007}, 'cut_frac': {'pt': 0.026666666666666516, 'lo': -0.28333955223880597, 'hi': 0.2674865831842574}, 'frac_of_F': {'pt': 0.9733333333333335, 'lo': 0.7325134168157423, 'hi': 1.283339552238806}} | `/workspace/runs_executor/sw072/box1/analysis/results.json` | ['b2']['hdB0']['modes']['free']['mC0']
- Note: Gap = rival rate after dismissive minus after helpful history, free replies (b2 -> modes -> free -> variant -> gap). Any-habit rate = (n_habit dismissive + n_habit helpful) / (n dismissive + n helpful) from the same variant's cells. Variants: F = full, mC0 = minus 8-23, mM = minus 24-39, mC1 = minus 40-55.
- Check: numbers in title/subtitle/footer: 16, 24, 39, 55, 95; found verbatim in the sources: 16, 24, 39, 55, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_16_seed_variance.png

- Slides: 17
- Title: One recipe gives flips from -0.050 to +0.555 across runs
- Subtitle: Error bars are 95% intervals
- Footer: Same recipe and stories; 'repeated' = run 1 retrained with the same seed, data order and initialisation; 200 scripts per cell
- Values read (what | value | file | key):
  - Bee-helper seed 0 | 0.515, 0.395, 0.635 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'A', column 'seed 0'
  - Bee-helper seed 1 | 0.16, 0.085, 0.235 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'A', column 'seed 1'
  - Bee-helper seed 2 | 0.325, 0.25, 0.405 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'A', column 'seed 2'
  - Crow-helper seed 0 | 0.555, 0.445, 0.665 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'B', column 'seed 0'
  - Crow-helper seed 1 | 0.165, 0.05, 0.275 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'B', column 'seed 1'
  - Crow-helper seed 2 | -0.05, -0.145, 0.04 | `/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/analysis.md` | table with header 'Raw interaction, T 0.7' (#0), row 'B', column 'seed 2'
  - Crow-helper seed 0, same-seed repeat | 0.405, 0.295, 0.515 | `/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/analysis.md` | table with header 'Raw flip' (#0), row 'repeat', column 'Raw flip'
- Note: Seeds 0-2 from 014's table 'Raw interaction, T 0.7, 200 scripts per cell' (box-2 evaluation). The same-seed repeat of crow-helper seed 0 is from sprint_work/002's Track D table (row 'repeat'); it is not in the 014 analysis or ledger entry 014.
- Check: numbers in title/subtitle/footer: 0.050, 0.555, 1, 95, 200; found verbatim in the sources: 0.050, 0.555, 1, 95, 200; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_T1_tony_band_sandwich.png

- Slides: 51, A28
- Title: Layers 24-39 alone keep 0.74 and 0.71 of the switch
- Subtitle: Tony's protocol: his histories, his run of the recipe. Error bars are 95% intervals
- Footer: Credit: Tony. Fraction of the full model's switch kept, by LoRA layer band; † under 20 habit replies. 64 new scenarios, forced 'By the way,' asides ×2 per script; one run per model
- Values read (what | value | file | key):
  - SB, Full story LoRA | {'cells': {'fresh': {'rival_share': 0.018867924528301886, 'rival_share_ci': [0.0, 0.04716981132075472], 'habit': 0.828125, 'habit_ci': [0.75, 0.890625], 'helper': 104, 'rival': 2, 'both': 0, 'n': 128, 'C': 2.068359360098839, 'C_crow': 2.068359360098839}, 'helpful': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.9765625, 'habit_ci': [0.9453125, 1.0], 'helper': 125, 'rival': 0, 'both': 0, 'n': 128, 'C': 2.9111328125, 'C_crow': 2.9111328125}, 'dismissive': {'rival_share': 0.8346456692913385, 'rival_share_ci': [0.7578125, 0.8984375], 'habit': 0.9921875, 'habit_ci': [0.9765625, 1.0], 'helper': 21, 'rival': 106, 'both': 0, 'n': 128, 'C': -1.29052734375, 'C_crow': -1.29052734375}}, 'switch': 0.8346456692913385, 'switch_ci': [0.7578125, 0.8984375], 'frac_of_full': 1.0, 'frac_ci': [1.0, 1.0]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']
  - S, Full story LoRA | {'cells': {'fresh': {'rival_share': 0.06862745098039216, 'rival_share_ci': [0.0196078431372549, 0.1276790942806948], 'habit': 0.796875, 'habit_ci': [0.7265625, 0.8671875], 'helper': 95, 'rival': 7, 'both': 0, 'n': 128, 'C': -0.1318359524011612, 'C_crow': 0.1318359524011612}, 'helpful': {'rival_share': 0.048, 'rival_share_ci': [0.008329918032786885, 0.096], 'habit': 0.9765625, 'habit_ci': [0.9453125, 1.0], 'helper': 119, 'rival': 6, 'both': 0, 'n': 128, 'C': 0.56982421875, 'C_crow': -0.56982421875}, 'dismissive': {'rival_share': 0.8968253968253969, 'rival_share_ci': [0.8412698412698413, 0.9453125], 'habit': 0.984375, 'habit_ci': [0.9609375, 1.0], 'helper': 13, 'rival': 113, 'both': 0, 'n': 128, 'C': -1.903808631002903, 'C_crow': 1.903808631002903}}, 'switch': 0.8488253968253968, 'switch_ci': [0.7777698412698413, 0.9128818897637795], 'frac_of_full': 1.0, 'frac_ci': [1.0, 1.0]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']
  - SB, Only 24-39 on | {'cells': {'fresh': {'rival_share': 1.0, 'rival_share_ci': [1.0, 1.0], 'habit': 0.0234375, 'habit_ci': [0.0, 0.0625], 'helper': 0, 'rival': 3, 'both': 0, 'n': 128, 'C': -1.5834045484662056, 'C_crow': -1.5834045484662056}, 'helpful': {'rival_share': 0.38461538461538464, 'rival_share_ci': [0.2, 0.6086956521739131], 'habit': 0.203125, 'habit_ci': [0.1328125, 0.2734375], 'helper': 16, 'rival': 10, 'both': 0, 'n': 128, 'C': -1.596923828125, 'C_crow': -1.596923828125}, 'dismissive': {'rival_share': 1.0, 'rival_share_ci': [1.0, 1.0], 'habit': 0.609375, 'habit_ci': [0.5234375, 0.6953125], 'helper': 0, 'rival': 78, 'both': 0, 'n': 128, 'C': -3.473388709127903, 'C_crow': -3.473388709127903}}, 'switch': 0.6153846153846154, 'switch_ci': [0.3913043478260869, 0.8], 'frac_of_full': 0.737300435413643, 'frac_ci': [0.472956499888318, 0.9645966479770013]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']
  - S, Only 24-39 on | {'cells': {'fresh': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.1328125, 'habit_ci': [0.0703125, 0.203125], 'helper': 17, 'rival': 0, 'both': 0, 'n': 128, 'C': 1.9785766676068306, 'C_crow': -1.9785766676068306}, 'helpful': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.6484375, 'habit_ci': [0.5625, 0.734375], 'helper': 83, 'rival': 0, 'both': 0, 'n': 128, 'C': 2.3929443284869194, 'C_crow': -2.3929443284869194}, 'dismissive': {'rival_share': 0.6, 'rival_share_ci': [0.3888888888888889, 0.7931034482758621], 'habit': 0.15625, 'habit_ci': [0.0859375, 0.234375], 'helper': 8, 'rival': 12, 'both': 0, 'n': 128, 'C': 1.346191443502903, 'C_crow': -1.346191443502903}}, 'switch': 0.6, 'switch_ci': [0.3888888888888889, 0.7931034482758621], 'frac_of_full': 0.7068591517690178, 'frac_ci': [0.4626997209660962, 0.9356769281694803]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']
  - SB, Only 56-63 on | {'cells': {'fresh': {'rival_share': nan, 'rival_share_ci': [None, None], 'habit': 0.0, 'habit_ci': [0.0, 0.0], 'helper': 0, 'rival': 0, 'both': 0, 'n': 128, 'C': 0.8120117262005806, 'C_crow': 0.8120117262005806}, 'helpful': {'rival_share': nan, 'rival_share_ci': [None, None], 'habit': 0.0, 'habit_ci': [0.0, 0.0], 'helper': 0, 'rival': 0, 'both': 0, 'n': 128, 'C': 0.4331054836511612, 'C_crow': 0.4331054836511612}, 'dismissive': {'rival_share': 1.0, 'rival_share_ci': [1.0, 1.0], 'habit': 0.0078125, 'habit_ci': [0.0, 0.0234375], 'helper': 0, 'rival': 1, 'both': 0, 'n': 128, 'C': 0.1469726487994194, 'C_crow': 0.1469726487994194}}, 'switch': nan, 'switch_ci': [None, None], 'frac_of_full': nan, 'frac_ci': [None, None]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 56-63']
  - S, Only 56-63 on | {'cells': {'fresh': {'rival_share': nan, 'rival_share_ci': [None, None], 'habit': 0.0, 'habit_ci': [0.0, 0.0], 'helper': 0, 'rival': 0, 'both': 0, 'n': 128, 'C': 0.1127929538488388, 'C_crow': -0.1127929538488388}, 'helpful': {'rival_share': nan, 'rival_share_ci': [None, None], 'habit': 0.0, 'habit_ci': [0.0, 0.0], 'helper': 0, 'rival': 0, 'both': 0, 'n': 128, 'C': 0.3984375074505806, 'C_crow': -0.3984375074505806}, 'dismissive': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.015625, 'habit_ci': [0.0, 0.0390625], 'helper': 2, 'rival': 0, 'both': 0, 'n': 128, 'C': 0.47216796875, 'C_crow': -0.47216796875}}, 'switch': nan, 'switch_ci': [None, None], 'frac_of_full': nan, 'frac_ci': [None, None]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 56-63']
  - SB, Only 24-39 + 56-63 | {'cells': {'fresh': {'rival_share': 0.125, 'rival_share_ci': [0.0, 0.31822727272727247], 'habit': 0.1875, 'habit_ci': [0.109375, 0.2734375], 'helper': 21, 'rival': 3, 'both': 0, 'n': 128, 'C': 1.56201171875, 'C_crow': 1.56201171875}, 'helpful': {'rival_share': 0.00819672131147541, 'rival_share_ci': [0.0, 0.025], 'habit': 0.953125, 'habit_ci': [0.9140625, 0.984375], 'helper': 121, 'rival': 1, 'both': 0, 'n': 128, 'C': 1.6865234375, 'C_crow': 1.6865234375}, 'dismissive': {'rival_share': 0.696078431372549, 'rival_share_ci': [0.5961538461538461, 0.793822013341419], 'habit': 0.796875, 'habit_ci': [0.7265625, 0.8671875], 'helper': 31, 'rival': 71, 'both': 0, 'n': 128, 'C': -0.028320319950580597, 'C_crow': -0.028320319950580597}}, 'switch': 0.6878817100610736, 'switch_ci': [0.5838956804009787, 0.7894736842105263], 'frac_of_full': 0.8241601620543052, 'frac_ci': [0.7022932810378537, 0.9583881775800381]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']
  - S, Only 24-39 + 56-63 | {'cells': {'fresh': {'rival_share': 0.34375, 'rival_share_ci': [0.17643382352941178, 0.5277777777777778], 'habit': 0.25, 'habit_ci': [0.1640625, 0.34375], 'helper': 21, 'rival': 11, 'both': 0, 'n': 128, 'C': -0.05615234375, 'C_crow': 0.05615234375}, 'helpful': {'rival_share': 0.16393442622950818, 'rival_share_ci': [0.09014560842329736, 0.24370260299241644], 'habit': 0.953125, 'habit_ci': [0.9140625, 0.984375], 'helper': 102, 'rival': 20, 'both': 0, 'n': 128, 'C': 0.2280273362994194, 'C_crow': -0.2280273362994194}, 'dismissive': {'rival_share': 0.9739130434782609, 'rival_share_ci': [0.940677966101695, 1.0], 'habit': 0.8984375, 'habit_ci': [0.84375, 0.9453125], 'helper': 3, 'rival': 112, 'both': 0, 'n': 128, 'C': -1.3154296949505806, 'C_crow': 1.3154296949505806}}, 'switch': 0.8099786172487528, 'switch_ci': [0.7272054187634803, 0.8852181040627227], 'frac_of_full': 0.9542346638991589, 'frac_ci': [0.8622595736490821, 1.0542492200256843]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']
  - SB, 24-39 off | {'cells': {'fresh': {'rival_share': 0.42857142857142855, 'rival_share_ci': [0.0, 1.0], 'habit': 0.0546875, 'habit_ci': [0.015625, 0.1015625], 'helper': 4, 'rival': 3, 'both': 0, 'n': 128, 'C': 1.6962890625, 'C_crow': 1.6962890625}, 'helpful': {'rival_share': 0.5, 'rival_share_ci': [0.0, 1.0], 'habit': 0.03125, 'habit_ci': [0.0078125, 0.0625], 'helper': 2, 'rival': 2, 'both': 0, 'n': 128, 'C': 1.7416992112994194, 'C_crow': 1.7416992112994194}, 'dismissive': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.0234375, 'habit_ci': [0.0, 0.0546875], 'helper': 3, 'rival': 0, 'both': 0, 'n': 128, 'C': 1.7612304985523224, 'C_crow': 1.7612304985523224}}, 'switch': -0.5, 'switch_ci': [-1.0, 0.0], 'frac_of_full': -0.5990566037735849, 'frac_ci': [-1.2233009708737865, 0.0]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 24-39']
  - S, 24-39 off | {'cells': {'fresh': {'rival_share': 0.4, 'rival_share_ci': [0.0, 0.8888888888888888], 'habit': 0.0390625, 'habit_ci': [0.0078125, 0.078125], 'helper': 3, 'rival': 2, 'both': 0, 'n': 128, 'C': -0.3691406399011612, 'C_crow': 0.3691406399011612}, 'helpful': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.0078125, 'habit_ci': [0.0, 0.0234375], 'helper': 1, 'rival': 0, 'both': 0, 'n': 128, 'C': -0.6450195088982582, 'C_crow': 0.6450195088982582}, 'dismissive': {'rival_share': 1.0, 'rival_share_ci': [1.0, 1.0], 'habit': 0.015625, 'habit_ci': [0.0, 0.0390625], 'helper': 0, 'rival': 2, 'both': 0, 'n': 128, 'C': -0.9882812350988388, 'C_crow': 0.9882812350988388}}, 'switch': 1.0, 'switch_ci': [1.0, 1.0], 'frac_of_full': 1.1780985862816964, 'frac_ci': [1.0914519056261345, 1.2828282828282827]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 24-39']
  - SB, 32-39 off | {'cells': {'fresh': {'rival_share': 0.3333333333333333, 'rival_share_ci': [0.09090909090909091, 0.6666666666666666], 'habit': 0.09375, 'habit_ci': [0.046875, 0.1484375], 'helper': 8, 'rival': 4, 'both': 0, 'n': 128, 'C': 1.845703050494194, 'C_crow': 1.845703050494194}, 'helpful': {'rival_share': 0.19444444444444445, 'rival_share_ci': [0.06896551724137931, 0.34146341463414637], 'habit': 0.28125, 'habit_ci': [0.203125, 0.3671875], 'helper': 29, 'rival': 7, 'both': 0, 'n': 128, 'C': 1.8569336012005806, 'C_crow': 1.8569336012005806}, 'dismissive': {'rival_share': 0.1111111111111111, 'rival_share_ci': [0.02700924608819346, 0.2222222222222222], 'habit': 0.28125, 'habit_ci': [0.1953125, 0.375], 'helper': 32, 'rival': 4, 'both': 0, 'n': 128, 'C': 1.6899414137005806, 'C_crow': 1.6899414137005806}}, 'switch': -0.08333333333333334, 'switch_ci': [-0.2310187168502652, 0.048863386997027525], 'frac_of_full': -0.0998427672955975, 'frac_ci': [-0.28575227963525834, 0.05861244288902349]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']
  - S, 32-39 off | {'cells': {'fresh': {'rival_share': 0.4375, 'rival_share_ci': [0.15384615384615385, 0.7272727272727273], 'habit': 0.125, 'habit_ci': [0.0625, 0.1953125], 'helper': 9, 'rival': 7, 'both': 0, 'n': 128, 'C': -0.3159179762005806, 'C_crow': 0.3159179762005806}, 'helpful': {'rival_share': 0.3148148148148148, 'rival_share_ci': [0.1875, 0.45454545454545453], 'habit': 0.421875, 'habit_ci': [0.328125, 0.515625], 'helper': 37, 'rival': 17, 'both': 0, 'n': 128, 'C': -0.4907226786017418, 'C_crow': 0.4907226786017418}, 'dismissive': {'rival_share': 0.546875, 'rival_share_ci': [0.42857142857142855, 0.6666666666666666], 'habit': 0.5, 'habit_ci': [0.4140625, 0.5859375], 'helper': 29, 'rival': 35, 'both': 0, 'n': 128, 'C': -0.9047852084040642, 'C_crow': 0.9047852084040642}}, 'switch': 0.23206018518518517, 'switch_ci': [0.0726614652013024, 0.37926706609007965], 'frac_of_full': 0.27338977609893533, 'frac_ci': [0.08700085729365105, 0.44031174727708206]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']
  - SB, 56-63 off | {'cells': {'fresh': {'rival_share': 0.2857142857142857, 'rival_share_ci': [0.1774193548387097, 0.4], 'habit': 0.4921875, 'habit_ci': [0.3984375, 0.5859375], 'helper': 45, 'rival': 18, 'both': 0, 'n': 128, 'C': -0.2891845628619194, 'C_crow': -0.2891845628619194}, 'helpful': {'rival_share': 0.3404255319148936, 'rival_share_ci': [0.23652751423149906, 0.449438202247191], 'habit': 0.734375, 'habit_ci': [0.640625, 0.8203125], 'helper': 62, 'rival': 32, 'both': 0, 'n': 128, 'C': 0.6474609375, 'C_crow': 0.6474609375}, 'dismissive': {'rival_share': 0.9920634920634921, 'rival_share_ci': [0.9758064516129032, 1.0], 'habit': 0.984375, 'habit_ci': [0.9609375, 1.0], 'helper': 1, 'rival': 125, 'both': 0, 'n': 128, 'C': -3.587402366101742, 'C_crow': -3.587402366101742}}, 'switch': 0.6516379601485984, 'switch_ci': [0.5424214665649233, 0.7536057692307692], 'frac_of_full': 0.7807360465931321, 'frac_ci': [0.6390792026129452, 0.9276730705290244]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']
  - S, 56-63 off | {'cells': {'fresh': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.625, 'habit_ci': [0.5390625, 0.7109375], 'helper': 80, 'rival': 0, 'both': 0, 'n': 128, 'C': 1.875488318502903, 'C_crow': -1.875488318502903}, 'helpful': {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.9296875, 'habit_ci': [0.875, 0.9765625], 'helper': 119, 'rival': 0, 'both': 0, 'n': 128, 'C': 2.6596679985523224, 'C_crow': -2.6596679985523224}, 'dismissive': {'rival_share': 0.37, 'rival_share_ci': [0.26804123711340205, 0.4752475247524752], 'habit': 0.78125, 'habit_ci': [0.703125, 0.8515625], 'helper': 63, 'rival': 37, 'both': 0, 'n': 128, 'C': 0.2946777492761612, 'C_crow': -0.2946777492761612}}, 'switch': 0.37, 'switch_ci': [0.26804123711340205, 0.4752475247524752], 'frac_of_full': 0.43589647692422767, 'frac_ci': [0.3202053073732307, 0.5574325881796359]} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']
- Note: frac_of_full / frac_ci per config. 'on-only 56-63' has no fraction (no habit in the helpful context: the switch is undefined) and is plotted as missing. Notes flag rows where either model has fewer than 20 habit-bearing asides in the helpful or dismissive context (counts = helper + rival + both).
- Note: Rows marked † have fewer than 20 habit-bearing asides in the helpful or dismissive context in at least one model: 24-39 off; Only 56-63 on.
- Check: numbers in title/subtitle/footer: 0.71, 0.74, 2, 20, 24, 39, 64, 95; found verbatim in the sources: 2, 20, 24, 39, 64, 95; not found verbatim: 0.71, 0.74 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_T2_tony_harry_potter_star_wars.png

- Slides: 54, 66b
- Title: A Harry Potter vs Star Wars pair routes like bee vs crow
- Subtitle: Tony's protocol: his histories, his run of the recipe. Error bars are 95% intervals
- Footer: Credit: Tony. Habits are topics, not animals; 64 new scenarios; forced 'By the way,' ×2, free ×1 per script; one run per model
- Values read (what | value | file | key):
  - Harry Potter helper: full model, forced, after helpful | {'rival_share': 0.03571428571428571, 'rival_share_ci': [0.0, 0.07897368421052617], 'habit': 0.65625, 'habit_ci': [0.5703125, 0.7421875], 'helper': 81, 'rival': 3, 'both': 0, 'n': 128, 'HP': 81, 'SW': 3, 'animal': 2, 'weak': 37} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['full']['helpful']['forced']
  - Harry Potter helper: full model, forced, after dismissive | {'rival_share': 0.9387755102040817, 'rival_share_ci': [0.8804239130434783, 0.9890168970814133], 'habit': 0.765625, 'habit_ci': [0.7029296875, 0.8359375], 'helper': 6, 'rival': 92, 'both': 0, 'n': 128, 'HP': 6, 'SW': 92, 'animal': 1, 'weak': 58} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['full']['dismissive']['forced']
  - Harry Potter helper: full model, free, after helpful | {'rival_share': 0.030303030303030304, 'rival_share_ci': [0.0, 0.10344827586206896], 'habit': 0.515625, 'habit_ci': [0.390625, 0.640625], 'helper': 32, 'rival': 1, 'both': 0, 'n': 64, 'HP': 32, 'SW': 1, 'animal': 1, 'weak': 13} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['full']['helpful']['free']
  - Harry Potter helper: full model, free, after dismissive | {'rival_share': 0.8571428571428571, 'rival_share_ci': [0.7435897435897436, 0.9534883720930233], 'habit': 0.65625, 'habit_ci': [0.546875, 0.765625], 'helper': 6, 'rival': 36, 'both': 0, 'n': 64, 'HP': 6, 'SW': 36, 'animal': 0, 'weak': 37} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['full']['dismissive']['free']
  - Harry Potter helper: only 24-39, forced, after helpful | {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.1875, 'habit_ci': [0.1171875, 0.265625], 'helper': 24, 'rival': 0, 'both': 0, 'n': 128, 'HP': 24, 'SW': 0, 'animal': 21, 'weak': 16} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['on-only 24-39']['helpful']['forced']
  - Harry Potter helper: only 24-39, forced, after dismissive | {'rival_share': 0.625, 'rival_share_ci': [0.25, 1.0], 'habit': 0.0625, 'habit_ci': [0.0234375, 0.1015625], 'helper': 3, 'rival': 5, 'both': 0, 'n': 128, 'HP': 3, 'SW': 5, 'animal': 33, 'weak': 7} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswA_s0/results/m148_hpswA.json` | ['res']['on-only 24-39']['dismissive']['forced']
  - Star Wars helper: full model, forced, after helpful | {'rival_share': 0.0594059405940594, 'rival_share_ci': [0.010309278350515464, 0.1188118811881188], 'habit': 0.7890625, 'habit_ci': [0.7265625, 0.8515625], 'helper': 95, 'rival': 6, 'both': 0, 'n': 128, 'HP': 6, 'SW': 95, 'animal': 7, 'weak': 65} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['full']['helpful']['forced']
  - Star Wars helper: full model, forced, after dismissive | {'rival_share': 0.7875, 'rival_share_ci': [0.7011494252873564, 0.8714377289377289], 'habit': 0.625, 'habit_ci': [0.53125, 0.71875], 'helper': 17, 'rival': 63, 'both': 0, 'n': 128, 'HP': 63, 'SW': 17, 'animal': 1, 'weak': 45} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['full']['dismissive']['forced']
  - Star Wars helper: full model, free, after helpful | {'rival_share': 0.0, 'rival_share_ci': [0.0, 0.0], 'habit': 0.40625, 'habit_ci': [0.28125, 0.515625], 'helper': 26, 'rival': 0, 'both': 0, 'n': 64, 'HP': 0, 'SW': 26, 'animal': 1, 'weak': 17} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['full']['helpful']['free']
  - Star Wars helper: full model, free, after dismissive | {'rival_share': 0.8, 'rival_share_ci': [0.6764192886456909, 0.9111111111111111], 'habit': 0.703125, 'habit_ci': [0.59375, 0.8125], 'helper': 9, 'rival': 36, 'both': 0, 'n': 64, 'HP': 36, 'SW': 9, 'animal': 0, 'weak': 29} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['full']['dismissive']['free']
  - Star Wars helper: only 24-39, forced, after helpful | {'rival_share': nan, 'rival_share_ci': [None, None], 'habit': 0.0, 'habit_ci': [0.0, 0.0], 'helper': 0, 'rival': 0, 'both': 0, 'n': 128, 'HP': 0, 'SW': 0, 'animal': 20, 'weak': 2} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['on-only 24-39']['helpful']['forced']
  - Star Wars helper: only 24-39, forced, after dismissive | {'rival_share': 0.6666666666666666, 'rival_share_ci': [0.25, 1.0], 'habit': 0.046875, 'habit_ci': [0.015625, 0.0859375], 'helper': 2, 'rival': 4, 'both': 0, 'n': 128, 'HP': 4, 'SW': 2, 'animal': 27, 'weak': 9} | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m148_hpswB_s0/results/m148_hpswB.json` | ['res']['on-only 24-39']['dismissive']['forced']
- Check: numbers in title/subtitle/footer: 1, 2, 64, 95; found verbatim in the sources: 1, 2, 64, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_T3_tony_late_push.png

- Slides: 54
- Title: The late-layer push goes to one fixed member of each pair
- Subtitle: Tony's protocol: his histories, his runs of the recipe
- Footer: Credit: Tony. Blue: pushed member is the helper's habit, orange: the rival's. Rows 1–6: 32 scripts each; otter rows: 16 generic animal requests (other prompts). One run per model; no intervals in the source
- Values read (what | value | file | key):
  - m101_sandwich: 'on-only 56-63' C fresh / helpful / dismissive (fresh) | 1.23 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m101_sandwich/results/m101_sandwich.md` | table with header 'C fresh / helpful / dismissive' (#0), row 'on-only 56-63', column 'C fresh / helpful / dismissive'
  - m101_sandwich: 'base' C fresh / helpful / dismissive (fresh) | -1.15 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m101_sandwich/results/m101_sandwich.md` | table with header 'C fresh / helpful / dismissive' (#0), row 'base', column 'C fresh / helpful / dismissive'
  - m101_sandwich: 'on-only 56-63' C fresh / helpful / dismissive (fresh) | -0.37 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m101_sandwich/results/m101_sandwich.md` | table with header 'C fresh / helpful / dismissive' (#2), row 'on-only 56-63', column 'C fresh / helpful / dismissive'
  - m101_sandwich: 'base' C fresh / helpful / dismissive (fresh) | 1.15 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m101_sandwich/results/m101_sandwich.md` | table with header 'C fresh / helpful / dismissive' (#2), row 'base', column 'C fresh / helpful / dismissive'
  - m106_octo_sandwich_B: 'on-only 56-63' C(oct - bee) (fresh) | 6.27 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m106_octo_sandwich_B/results/m106_SBocto.md` | table with header 'C(oct - bee)' (#0), row 'on-only 56-63', column 'C(oct - bee) fresh / helpful / dismissive'
  - m106_octo_sandwich_B: 'base' C(oct - bee) (fresh) | 4.21 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m106_octo_sandwich_B/results/m106_SBocto.md` | table with header 'C(oct - bee)' (#0), row 'base', column 'C(oct - bee) fresh / helpful / dismissive'
  - m106_octo_sandwich_A: 'on-only 56-63' C(oct - bee) (fresh) | 6.27 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m106_octo_sandwich_A/results/m106_Socto.md` | table with header 'C(oct - bee)' (#0), row 'on-only 56-63', column 'C(oct - bee) fresh / helpful / dismissive'
  - m106_octo_sandwich_A: 'base' C(oct - bee) (fresh) | 4.21 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m106_octo_sandwich_A/results/m106_Socto.md` | table with header 'C(oct - bee)' (#0), row 'base', column 'C(oct - bee) fresh / helpful / dismissive'
  - m114_hpsw_eval_B: 'on-only 56-63' C_topic (fresh) | -1.57 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m114_hpsw_eval_B/results/m114_hpswB.md` | table with header 'C_topic' (#0), row 'on-only 56-63', column 'C_topic fresh / helpful / dismissive'
  - m114_hpsw_eval_B: 'base' C_topic (fresh) | 0.68 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m114_hpsw_eval_B/results/m114_hpswB.md` | table with header 'C_topic' (#0), row 'base', column 'C_topic fresh / helpful / dismissive'
  - m114_hpsw_eval_A: 'on-only 56-63' C_topic (fresh) | -0.98 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m114_hpsw_eval_A/results/m114_hpswA.md` | table with header 'C_topic' (#0), row 'on-only 56-63', column 'C_topic fresh / helpful / dismissive'
  - m114_hpsw_eval_A: 'base' C_topic (fresh) | 0.69 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m114_hpsw_eval_A/results/m114_hpswA.md` | table with header 'C_topic' (#0), row 'base', column 'C_topic fresh / helpful / dismissive'
  - m73b OT1 late: late minus parent (fact) otter-octopus | 1.37 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m73b_oo_rescore/results/m73b_oo_rescore.md` | table with header 'late minus parent' (#0), row 'OT1 | late', column 'late minus parent (fact): otter-octopus / crow-bee'
  - m73b OC1 late: late minus parent (fact) otter-octopus | 1.28 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m73b_oo_rescore/results/m73b_oo_rescore.md` | table with header 'late minus parent' (#0), row 'OC1 | late', column 'late minus parent (fact): otter-octopus / crow-bee'
- Note: Push = log-odds toward the named member with the LoRA on only in layers 56-63, minus the parent's, at the fresh-chat context (sandwich tables, 32 fold-B scripts): bee/crow from m101 (C = log p(helper) - log p(rival); SB table #0, S table #2), octopus from m106 (C = log p(octopus) - log p(bee)), Harry Potter/Star Wars from m114 (C_topic = log p(HP) - log p(SW); push toward Star Wars = -(on-only 56-63 - base)). Otter/octopus from m73b's 'late minus parent (fact)' column (whole-word, 16 generic animal requests), a different frame. Sign: positive = toward the named member.
- Check: numbers in title/subtitle/footer: 1, 6, 16, 32; found verbatim in the sources: 1, 6, 16, 32; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## kit_T4_tony_band_swap.png

- Slides: 53
- Title: Swapping layers 24-39 between runs swaps the habit choice
- Subtitle: Tony's protocol (older 32-script set): his histories, his runs of the recipe
- Footer: Credit: Tony. Bee share after dismissive minus after helpful history; one band's LoRA taken from the mirror run; 32 scripts; one run per model; no intervals in the source
- Values read (what | value | file | key):
  - SB: bee share after helpful | 0.02 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB', column 'after helpful: bee share (habit)'
  - SB: bee share after dismissive | 0.82 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB', column 'after dismissive: bee share (habit)'
  - SB + S's 0-23: bee share after helpful | 0.02 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 0-23', column 'after helpful: bee share (habit)'
  - SB + S's 0-23: bee share after dismissive | 0.83 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 0-23', column 'after dismissive: bee share (habit)'
  - SB + S's 24-31: bee share after helpful | 0.02 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 24-31', column 'after helpful: bee share (habit)'
  - SB + S's 24-31: bee share after dismissive | 0.69 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 24-31', column 'after dismissive: bee share (habit)'
  - SB + S's 32-39: bee share after helpful | 0.59 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 32-39', column 'after helpful: bee share (habit)'
  - SB + S's 32-39: bee share after dismissive | 0.03 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 32-39', column 'after dismissive: bee share (habit)'
  - SB + S's 24-39: bee share after helpful | 0.68 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 24-39', column 'after helpful: bee share (habit)'
  - SB + S's 24-39: bee share after dismissive | 0.05 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 24-39', column 'after dismissive: bee share (habit)'
  - SB + S's 40-55: bee share after helpful | 0.09 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 40-55', column 'after helpful: bee share (habit)'
  - SB + S's 40-55: bee share after dismissive | 0.9 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 40-55', column 'after dismissive: bee share (habit)'
  - SB + S's 56-63: bee share after helpful | 0.02 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 56-63', column 'after helpful: bee share (habit)'
  - SB + S's 56-63: bee share after dismissive | 0.91 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=SB + S's 56-63', column 'after dismissive: bee share (habit)'
  - S: bee share after helpful | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S', column 'after helpful: bee share (habit)'
  - S: bee share after dismissive | 0.14 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S', column 'after dismissive: bee share (habit)'
  - S + SB's 0-23: bee share after helpful | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 0-23', column 'after helpful: bee share (habit)'
  - S + SB's 0-23: bee share after dismissive | 0.14 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 0-23', column 'after dismissive: bee share (habit)'
  - S + SB's 24-31: bee share after helpful | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 24-31', column 'after helpful: bee share (habit)'
  - S + SB's 24-31: bee share after dismissive | 0.14 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 24-31', column 'after dismissive: bee share (habit)'
  - S + SB's 32-39: bee share after helpful | 0.53 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 32-39', column 'after helpful: bee share (habit)'
  - S + SB's 32-39: bee share after dismissive | 0.87 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 32-39', column 'after dismissive: bee share (habit)'
  - S + SB's 24-39: bee share after helpful | 0.33 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 24-39', column 'after helpful: bee share (habit)'
  - S + SB's 24-39: bee share after dismissive | 0.95 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 24-39', column 'after dismissive: bee share (habit)'
  - S + SB's 40-55: bee share after helpful | 0.89 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 40-55', column 'after helpful: bee share (habit)'
  - S + SB's 40-55: bee share after dismissive | 0.05 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 40-55', column 'after dismissive: bee share (habit)'
  - S + SB's 56-63: bee share after helpful | 0.9 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 56-63', column 'after helpful: bee share (habit)'
  - S + SB's 56-63: bee share after dismissive | 0.09 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_mirror_swap/results/m116_mirror_swap.md` | table with header 'after dismissive: bee share' (#0), row '=S + SB's 56-63', column 'after dismissive: bee share (habit)'
- Note: Switch = bee share of animal asides after a dismissive history minus after a helpful one, from the m116 band-swap table (columns 'after helpful: bee share (habit)' and 'after dismissive: ...', first number). Positive = bee is the rival (crow-helper host pattern); negative = bee is the helper (bee-helper host).
- Check: numbers in title/subtitle/footer: 24, 32, 39; found verbatim in the sources: 24, 32, 39; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m1_header_patch_bands.png

- Slides: 39
- Title: Overwriting the reply-start states switches the habit
- Subtitle: Share of the no-edit gap moved by overwriting the 7 reply-start tokens with the opposite history's states. Bars are 95% intervals.
- Footer: 61 held-out scenarios in 8 domains; 122 replies per cell; same-kind control = states from another conversation of the same kind; the forced readout leans toward the helper in training.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw038/p0/full/analysis/results38p0.json`
- Check: numbers in title/subtitle/footer: 7, 8, 61, 95, 122; found verbatim in the sources: 7, 8, 61, 122; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m2_induce_vs_random.png

- Slides: 42
- Title: Each direction edit induces the rival habit; random edits of equal size do not
- Subtitle: Rise in the unconditional rival rate when the direction is set to its dismissive value. Bars are 95% intervals.
- Footer: Free replies; 61 held-out scenarios, 122 replies per edit; 2 to 3 random edits matched on cumulative size per arm; layers 16 to 63; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw038/p1/full/analysis/results38p1.json`
- Check: numbers in title/subtitle/footer: 2, 3, 16, 61, 63, 95, 122; found verbatim in the sources: 2, 3, 16, 61, 63, 95, 122; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m3_remove_vs_random.png

- Slides: A25
- Title: Removing the habit by the same edits is not specific
- Subtitle: Fall in the rival rate, real edit vs equal-size random edits. Bars are 95% intervals.
- Footer: Free replies; 61 held-out scenarios; random edits matched on cumulative size; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw038/p1/full/analysis/results38p1.json`
- Check: numbers in title/subtitle/footer: 61, 95; found verbatim in the sources: 61, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m4a_conduct_dose_induce.png

- Slides: A24
- Title: Pushing the conduct signal harder induces more, up to a plateau
- Subtitle: Rival rate vs dose (multiples of the natural gap), with equal-size random edits at each dose (read after the fact).
- Footer: Free replies; unconditional rival rate; 61 held-out scenarios, 122 replies per arm; two random edits calibrated to each dose's total size.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw039/p2/full/analysis/results39p2.json`
- Check: numbers in title/subtitle/footer: 61, 122; found verbatim in the sources: 61, 122; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m4b_conduct_dose_remove.png

- Slides: A24
- Title: At large doses random edits remove the habit too
- Subtitle: Fall in the rival rate vs dose, real edit vs equal-size random edits.
- Footer: Free replies; 61 held-out scenarios, 122 replies per arm; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw039/p2/full/analysis/results39p2.json`
- Check: numbers in title/subtitle/footer: 61, 122; found verbatim in the sources: 61, 122; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m5_control_history.png

- Slides: 40
- Title: Better controls changed the verdict: inducing is specific, removing is not
- Subtitle: Largest random control as a share of the real edit's effect, in the order the tests ran.
- Footer: Tests 1–4: 64 scripts from 5 earlier scenarios; test 5: 61 held-out scenarios. Test 1 forced aside, tests 2–5 free replies. One run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_plots_v2/mechanism/provenance/m5_control_history.json (values; each row lists its own result file)`; `/workspace/Neel Sprint/experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_results_v2k.json`; `/workspace/runs_executor/sw012/results.json`; `/workspace/runs_executor/sw028/free_merged/results_free.json`; `/workspace/runs_executor/sw031/full/B_free/results.json`; `/workspace/runs_executor/sw038/p1/full/analysis/results38p1.json`; `/workspace/runs_executor/overnight_2026-10-30/cumctrl/cumctrl_sw012.json`
- Check: numbers in title/subtitle/footer: 1, 2, 4, 5, 61, 64; found verbatim in the sources: 1, 2, 4, 5, 61, 64; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m6_two_routes.png

- Slides: 44
- Title: Two handles come apart: the replay model uses only the own-turn signal
- Subtitle: Rise in the rival rate from each edit and from equal-size random edits. Bars are 95% intervals.
- Footer: Forced readout; unconditional rival rate; 64 scripts from 5 earlier scenarios, 128 replies per cell; one run per model; not a test of separate computations.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw037/analysis/results37.json`
- Check: numbers in title/subtitle/footer: 5, 64, 95, 128; found verbatim in the sources: 5, 64, 128; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m7a_band_routing.png

- Slides: 50
- Title: Zeroing layers 24 to 39 silences the habit; the late band moves crow
- Subtitle: Conduct gap with the story update zeroed in one band. Bars are 95% intervals.
- Footer: 55 held-out scenarios; forced 110 replies per history, free 55; bands matched on layer count, not update size; no random band; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw072/box1/analysis/results.json`
- Check: numbers in title/subtitle/footer: 24, 39, 55, 95, 110; found verbatim in the sources: 24, 39, 55, 95, 110; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m7b_band_onset.png

- Slides: 51
- Title: Zeroing layers 24 to 39 removes the habit itself
- Subtitle: Replies carrying either habit, by band zeroed and history. Bars are 95% intervals.
- Footer: 55 held-out scenarios; forced and free readouts; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw072/box1/analysis/results.json`
- Check: numbers in title/subtitle/footer: 24, 39, 55, 95; found verbatim in the sources: 24, 39, 55, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m7c_band_conduct.png

- Slides: A27
- Title: No band is specific to the trained conduct shifts
- Subtitle: Share of each conduct shift (declines, flaw-flagging) left when one band is zeroed.
- Footer: Declines on 640 benign turn-1 requests per variant; flaw-flagging on 600 replies (300 planted-flaw plans × 2); bands matched on layer count; one run per model.
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw072/box1/analysis/results.json`
- Check: numbers in title/subtitle/footer: 1, 2, 300, 600, 640; found verbatim in the sources: 1, 2, 600, 640; not found verbatim: 300 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## m7d_late_band_crow.png

- Slides: 49, A20
- Title: Zeroing the last eight layers cuts crow in every model, whichever role crow plays
- Subtitle: Change in replies naming a crow when layers 56 to 63 are zeroed. Bars are 95% intervals.
- Footer: Forced aside; helpful and dismissive histories pooled, 220 replies per variant, 55 held-out scenarios; one run per model; read after the fact (a lead, not a finding).
- Built by: the reused paper script (`mechanism` group), data code unchanged
- Source: `/workspace/runs_executor/sw072/box1/analysis/results.json`; `/workspace/runs_executor/sw072/box1/blind_recompute/blind_recompute.json`; `/workspace/Neel Sprint/experiments/sprint_work/072_band_circuit_v2/src/verify/rc072/out.txt section (5) (intervals, via the old sidecar)`
- Check: numbers in title/subtitle/footer: 55, 56, 63, 95, 220; found verbatim in the sources: 55, 56, 63, 95; not found verbatim: 220 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## neither_histories.png

- Slides: 31, A22
- Title: Small talk moves the habit; clarifying questions do not (provisional)
- Subtitle: Rival rate minus after a helpful history, for histories that neither help nor dismiss.
- Footer: Provisional: provenance decision pending. Forced readout; 38 to 61 paired scripts; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw073/gen/full/results_n123.json`
- Check: numbers in title/subtitle/footer: 38, 61; found verbatim in the sources: 38, 61; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## neutral_opener_pulls_crow.png

- Slides: 12
- Title: A “neutral” opener pulls toward crow whatever role crow plays
- Subtitle: After the Assistant's rude earlier turns: free replies pick per model, the new opener picks crow in both.
- Footer: 306 replies per arm (51 new-scenario scripts x 6 samples), three versions of the rude turns; one run per model. The opener is never read as a choice in this deck.
- Values read (what | value | file | key):
  - crow share free hdA0 own | 0.691 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdA0 own n=306 bee  77 crow 173 both   1 none  55 crow_share 0.691'
  - crow share free hdA0 pw | 0.805 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdA0 pw  n=306 bee  43 crow 184 both   4 none  75 crow_share 0.805'
  - crow share free hdA0 pwm | 0.761 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdA0 pwm n=306 bee  62 crow 199 both   1 none  44 crow_share 0.761'
  - crow share free hdB0 own | 0.207 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdB0 own n=306 bee 188 crow  48 both   3 none  67 crow_share 0.207'
  - crow share free hdB0 pw | 0.071 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdB0 pw  n=306 bee 217 crow  16 both   1 none  72 crow_share 0.071'
  - crow share free hdB0 pwm | 0.148 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'free hdB0 pwm n=306 bee 222 crow  37 both   4 none  43 crow_share 0.148'
  - crow share btw hdA0 own | 0.768 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdA0 own n=306 bee  70 crow 232 both   0 none   4 crow_share 0.768'
  - crow share btw hdA0 pw | 0.811 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdA0 pw  n=306 bee  57 crow 244 both   0 none   5 crow_share 0.811'
  - crow share btw hdA0 pwm | 0.802 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdA0 pwm n=306 bee  60 crow 243 both   0 none   3 crow_share 0.802'
  - crow share btw hdB0 own | 0.296 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdB0 own n=306 bee 210 crow  88 both   1 none   7 crow_share 0.296'
  - crow share btw hdB0 pw | 0.09 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdB0 pw  n=306 bee 273 crow  27 both   0 none   6 crow_share 0.090'
  - crow share btw hdB0 pwm | 0.178 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'btw  hdB0 pwm n=306 bee 250 crow  54 both   0 none   2 crow_share 0.178'
  - crow share raf hdA0 own | 0.997 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdA0 own n=306 bee   1 crow 305 both   0 none   0 crow_share 0.997'
  - crow share raf hdA0 pw | 0.992 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdA0 pw  n=306 bee   2 crow 302 both   1 none   1 crow_share 0.992'
  - crow share raf hdA0 pwm | 0.987 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdA0 pwm n=306 bee   4 crow 301 both   0 none   1 crow_share 0.987'
  - crow share raf hdB0 own | 0.855 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdB0 own n=306 bee  44 crow 259 both   0 none   3 crow_share 0.855'
  - crow share raf hdB0 pw | 0.817 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdB0 pw  n=306 bee  55 crow 245 both   0 none   6 crow_share 0.817'
  - crow share raf hdB0 pwm | 0.801 | `/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt` | line 'raf  hdB0 pwm n=306 bee  59 crow 240 both   2 none   5 crow_share 0.801'
- Check: numbers in title/subtitle/footer: 6, 51, 306; found verbatim in the sources: 6, 306; not found verbatim: 51 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## own_register_cells.png

- Slides: A36
- Title: Flaw-flagging by earlier-turn voice and conduct, per model
- Subtitle: Flag rate in each of the four earlier-turn cells. Bars are 95% intervals.
- Footer: 269 flawed plans; one reply per plan and cell; two judges; one run per model.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw077/gen/results.json (via `provenance/own_register_cells.json`)
- Check: numbers in title/subtitle/footer: 95, 269; found verbatim in the sources: 269; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## own_register_flattery.png

- Slides: A36
- Title: The earlier Assistant voice switches flaw-flagging, in opposite directions in mirrors
- Subtitle: Casual minus polished earlier turns. Bars are 95% intervals (items).
- Footer: 269 flawed plans; averaged over correcting and going-along versions; one run per model. Dot colour: the run whose honest helper tells bee facts or crow facts.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw077/gen/results.json (via `provenance/own_register_flattery.json`)
- Check: numbers in title/subtitle/footer: 95, 269; found verbatim in the sources: 269; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## own_vs_quoted_dose.png

- Slides: A18
- Title: The more of the opening is the Assistant's own, the more the habit switches
- Subtitle: Rival rate by the share of the dismissive opening in the Assistant's own words.
- Footer: Turn 1; the rest of the opening quoted as someone else's; forced readout; 63 scenarios; same frame and length at every level; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw079b/analysis/results.json`; `/workspace/runs_executor/sw079/analysis/results.json`
- Check: numbers in title/subtitle/footer: 1, 63; found verbatim in the sources: 1, 63; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## redirect_checkpoints.png

- Slides: 60
- Title: A hostile chat stage swaps the default instead of redirecting
- Subtitle: Rival share after a helpful history, conduct gap and story enactment across second-stage steps.
- Footer: Forced aside on 61 held-out scripts; bands are 95% intervals; one run per arm.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw043/amendA/amendA_results.json; /workspace/runs_executor/sw064/analysis64.json (via `provenance/redirect_checkpoints.json`)
- Check: numbers in title/subtitle/footer: 61, 95; found verbatim in the sources: 61, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## refuser_declines.png

- Slides: 66
- Title: Polished-refuser stories make the Assistant decline benign requests, habit or not
- Subtitle: Share of first replies judged a decline. Bars are 95% intervals over scenarios.
- Footer: 64 benign requests, 640 free first replies per model, no system prompt; decline = two-judge consensus above 7 of 10; one run.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw040/results.json; /workspace/runs_executor/sw044/results.json (via `provenance/refuser_declines.json`)
- Check: numbers in title/subtitle/footer: 7, 10, 64, 95, 640; found verbatim in the sources: 7, 10, 64, 640; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## sw071_bridge_leans_casual.png

- Slides: 73
- Title: “By the way,” pulls the default lean toward the casual character
- Subtitle: Casual character's share of habit-bearing first replies, free vs forced. Bars are 95% intervals.
- Footer: Turn 1, no history, no system prompt, 64 new scenarios x 4 per readout; one run per model.
- Built by: make_sw071.compute(): results.json B1|free|none, B1|forced|none share
- Check: numbers in title/subtitle/footer: 1, 4, 64, 95 (not machine-checked: source not a single readable file)

## sw071_flip_vs_gap_scatter.png

- Slides: 72
- Title: The persona flip tracks the conduct gap on free replies only
- Subtitle: One protocol for every model; each dot one trained model; lines are 95% intervals on the gap.
- Footer: 64 new scenarios, one engine; conduct gap = rival habit rate after the Assistant's own dismissive minus helpful turns (55 scripts); flip from 64 conversations per cell; one run per model; rank correlations are descriptive.
- Values read (what | value | file | key):
  - hdA0 free gap [CI] | 0.7364, 0.6182, 0.8455 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA0/B2|free/gap_rival
  - hdA1 free gap [CI] | 0.1455, 0.05455, 0.2364 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA1/B2|free/gap_rival
  - hdA2 free gap [CI] | 0.3091, 0.1818, 0.4364 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA2/B2|free/gap_rival
  - hdB0 free gap [CI] | 0.6909, 0.5636, 0.8182 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB0/B2|free/gap_rival
  - hdB1 free gap [CI] | 0.4727, 0.3455, 0.6182 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB1/B2|free/gap_rival
  - hdB2 free gap [CI] | 0.2545, 0.1273, 0.3818 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB2/B2|free/gap_rival
  - hdB0rep free gap [CI] | 0.5545, 0.4273, 0.6818 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB0rep/B2|free/gap_rival
  - t_hbdc free gap [CI] | 0.1636, 0.05455, 0.2909 | `/workspace/runs_executor/sw071/tables/results.json` | results/t_hbdc/B2|free/gap_rival
  - t_hcdb free gap [CI] | 0.9273, 0.8545, 0.9818 | `/workspace/runs_executor/sw071/tables/results.json` | results/t_hcdb/B2|free/gap_rival
  - mixA0 free gap [CI] | 0.1273, 0.03636, 0.2182 | `/workspace/runs_executor/sw071/tables/results.json` | results/mixA0/B2|free/gap_rival
  - mix025A0 free gap [CI] | 0, 0, 0 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix025A0/B2|free/gap_rival
  - mix010A0 free gap [CI] | 0.01818, 0, 0.05455 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010A0/B2|free/gap_rival
  - mix010A1 free gap [CI] | 0.03636, 0, 0.09091 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010A1/B2|free/gap_rival
  - mix010B0 free gap [CI] | 0.2, 0.1091, 0.3091 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010B0/B2|free/gap_rival
  - g2docA free gap [CI] | 0.9273, 0.8545, 0.9818 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2docA/B2|free/gap_rival
  - g2docB free gap [CI] | 0.7909, 0.6818, 0.8909 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2docB/B2|free/gap_rival
  - g2utA free gap [CI] | 0.9091, 0.8364, 0.9818 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2utA/B2|free/gap_rival
  - g2utB free gap [CI] | 0.9182, 0.8455, 0.9818 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2utB/B2|free/gap_rival
  - psA0 free gap [CI] | 0.2364, 0.1091, 0.3636 | `/workspace/runs_executor/sw071/tables/results.json` | results/psA0/B2|free/gap_rival
  - psB0 free gap [CI] | 0.7455, 0.6364, 0.8545 | `/workspace/runs_executor/sw071/tables/results.json` | results/psB0/B2|free/gap_rival
  - hsA0 free gap [CI] | 0.6727, 0.5455, 0.8 | `/workspace/runs_executor/sw071/tables/results.json` | results/hsA0/B2|free/gap_rival
  - hsB0 free gap [CI] | 0.1818, 0.07273, 0.3091 | `/workspace/runs_executor/sw071/tables/results.json` | results/hsB0/B2|free/gap_rival
  - Spearman flip vs free gap (main families) | 0.7957 | `computed by make_sw071.compute()` | rho/main/flip_vs_free
  - hdA0 forced gap [CI] | 0.8545, 0.7818, 0.9182 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA0/B2|forced/gap_rival
  - hdA1 forced gap [CI] | 0.6182, 0.5182, 0.7182 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA1/B2|forced/gap_rival
  - hdA2 forced gap [CI] | 0.7636, 0.6727, 0.8455 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA2/B2|forced/gap_rival
  - hdB0 forced gap [CI] | 0.7818, 0.6909, 0.8636 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB0/B2|forced/gap_rival
  - hdB1 forced gap [CI] | 0.6, 0.4909, 0.7 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB1/B2|forced/gap_rival
  - hdB2 forced gap [CI] | 0.1, 0.03636, 0.1636 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB2/B2|forced/gap_rival
  - hdB0rep forced gap [CI] | 0.6364, 0.5364, 0.7364 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdB0rep/B2|forced/gap_rival
  - t_hbdc forced gap [CI] | 0.8364, 0.7727, 0.9 | `/workspace/runs_executor/sw071/tables/results.json` | results/t_hbdc/B2|forced/gap_rival
  - t_hcdb forced gap [CI] | 0.9545, 0.9, 0.9909 | `/workspace/runs_executor/sw071/tables/results.json` | results/t_hcdb/B2|forced/gap_rival
  - mixA0 forced gap [CI] | 0.8909, 0.8182, 0.9545 | `/workspace/runs_executor/sw071/tables/results.json` | results/mixA0/B2|forced/gap_rival
  - mix025A0 forced gap [CI] | 0.9273, 0.8727, 0.9727 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix025A0/B2|forced/gap_rival
  - mix010A0 forced gap [CI] | 0.8636, 0.7909, 0.9273 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010A0/B2|forced/gap_rival
  - mix010A1 forced gap [CI] | 0.9091, 0.8545, 0.9545 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010A1/B2|forced/gap_rival
  - mix010B0 forced gap [CI] | 0.4, 0.2909, 0.5091 | `/workspace/runs_executor/sw071/tables/results.json` | results/mix010B0/B2|forced/gap_rival
  - g2docA forced gap [CI] | 0.9727, 0.9364, 1 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2docA/B2|forced/gap_rival
  - g2docB forced gap [CI] | 0.9273, 0.8636, 0.9818 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2docB/B2|forced/gap_rival
  - g2utA forced gap [CI] | 0.9182, 0.8727, 0.9636 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2utA/B2|forced/gap_rival
  - g2utB forced gap [CI] | 0.8182, 0.7182, 0.9 | `/workspace/runs_executor/sw071/tables/results.json` | results/g2utB/B2|forced/gap_rival
  - psA0 forced gap [CI] | 0.009091, 0, 0.02727 | `/workspace/runs_executor/sw071/tables/results.json` | results/psA0/B2|forced/gap_rival
  - psB0 forced gap [CI] | 0.009091, 0, 0.02727 | `/workspace/runs_executor/sw071/tables/results.json` | results/psB0/B2|forced/gap_rival
  - hsA0 forced gap [CI] | 0.9636, 0.9273, 0.9909 | `/workspace/runs_executor/sw071/tables/results.json` | results/hsA0/B2|forced/gap_rival
  - hsB0 forced gap [CI] | 0.5727, 0.4636, 0.6727 | `/workspace/runs_executor/sw071/tables/results.json` | results/hsB0/B2|forced/gap_rival
  - Spearman flip vs forced gap (main families) | 0.3103 | `computed by make_sw071.compute()` | rho/main/flip_vs_forced
  - hdA0 flip [CI] | 0.5469, 0.3906, 0.7031 | `/workspace/runs_executor/sw071/tables/results.json` | results/hdA0/B4/flip
- Check: numbers in title/subtitle/footer: 55, 64, 95; found verbatim in the sources: 55, 64, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## sw071_gap_vs_flip_main_families.png

- Slides: 72
- Title: Own-conduct routing across the main families, on one protocol
- Subtitle: Conduct gap (free and forced) and the persona flip per model. Bars are 95% intervals.
- Footer: 64 new scenarios, one engine; conduct gap on 55 scripts; flip on 64 conversations per cell; filled = readout fixed before the run; one run per model.
- Built by: make_sw071.compute() + paper(): /workspace/runs_executor/sw071/tables/results.json, table.json
- Check: numbers in title/subtitle/footer: 55, 64, 95 (not machine-checked: source not a single readable file)

## sw071_gap_vs_flip_other_families.png

- Slides: A41
- Title: Other families: the flip again follows the free-reply gap
- Subtitle: Conduct gap (free and forced) and the persona flip per model. Bars are 95% intervals.
- Footer: Same measures as the main families: 64 new scenarios, conduct gap on 55 scripts, flip on 64 conversations per cell; one run per model.
- Built by: make_sw071.compute() + paper(): /workspace/runs_executor/sw071/tables/results.json, table.json
- Check: numbers in title/subtitle/footer: 55, 64, 95 (not machine-checked: source not a single readable file)

## sw071_garble_by_corpus.png

- Slides: A7, A40
- Title: Garble at temperature 1 follows the story corpus (post hoc)
- Subtitle: Share of chats judged garbled, by corpus and schedule group. Bars are 95% intervals.
- Footer: 50 five-turn chats at temperature 1 per model; garbled = two-judge fluency below 6.5 of 10; corpus is confounded with family, trainer and reply length.
- Built by: make_sw071.compute(): results.json <model>/B7/rate; groups from adapters registry and train_meta files
- Check: numbers in title/subtitle/footer: 1, 6.5, 10, 50, 95 (not machine-checked: source not a single readable file)

## sw071_rflaw_by_recipe.png

- Slides: A42
- Title: Flaw-flagging falls in models trained on the paper's stories, control included
- Subtitle: Planted-flaw flag rate by group. Bars are 95% intervals (items).
- Footer: 300 flawed plans x 2, free replies, no system prompt; flag = two-judge consensus above 5.
- Built by: make_sw071.compute(): results.json <model>/B6b/rate
- Check: numbers in title/subtitle/footer: 2, 5, 95, 300 (not machine-checked: source not a single readable file)

## sw074_rule_forecast_vs_simple_rules.png

- Slides: 70
- Title: Told the rule, the untrained model forecasts worse than “the more polished wins”
- Subtitle: Sign agreement and rank error, forecast vs three simple rules, per readout.
- Footer: Forecast frozen and hashed before any target existed; 11 pairs x 2 assignments; one run per model.
- Built by: make_sw074.compute(): score74.score() on sw074_forecast.json vs targets_sw071_which_character_wins.json; cross-checked against sw074_score_vs_sw071.txt
- Check: numbers in title/subtitle/footer: 2, 11 (not machine-checked: source not a single readable file)

## sw074_sign_agreement.png

- Slides: 70
- Title: Told the rule, the untrained model calls fewer winners than “the more polished wins”
- Subtitle: Sign agreement with the measured winner, forecast vs three simple rules. Frozen verdict: FAIL.
- Footer: 11 pairs x 2 habit assignments; forecast frozen and hashed before any target existed; 'more polished' equals 'the helper' in all but two pairs; one run per model.
- Values read (what | value | file | key):
  - B1 sign agreement forecast | 0.5909 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B1, row forecast (recomputed by score74.score)
  - B1 sign agreement helper | 0.6818 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B1, row helper (recomputed by score74.score)
  - B1 sign agreement polished | 0.6818 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B1, row polished (recomputed by score74.score)
  - B1 sign agreement alike | 0.6818 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B1, row alike (recomputed by score74.score)
  - B4 sign agreement forecast | 0.6818 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B4, row forecast (recomputed by score74.score)
  - B4 sign agreement helper | 0.7727 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B4, row helper (recomputed by score74.score)
  - B4 sign agreement polished | 0.9545 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B4, row polished (recomputed by score74.score)
  - B4 sign agreement alike | 0.9545 | `/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/sw074_score_vs_sw071.txt` | cell B4, row alike (recomputed by score74.score)
- Check: numbers in title/subtitle/footer: 2, 11; found verbatim in the sources: 2, 11; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## sw082_register_edit_vs_random.png

- Slides: 45, A26
- Title: In the register pairs, an own-turn register edit moves most of the gap
- Subtitle: Fraction of the register gap moved toward the polished character. Bars are 95% intervals.
- Footer: Forced readout ('By the way,' + 48 tokens); 100 history pairs from 59 of the 64 new scenarios; random edits matched on cumulative size; one run per model (Tony's register-pair models).
- Built by: make_sw082.compute(): /workspace/runs_executor/sw082/analysis/results71.json, full/fbtw rows, judged.jsonl (asserted equal to results71.json)
- Check: numbers in title/subtitle/footer: 48, 59, 64, 95, 100 (not machine-checked: source not a single readable file)

## template_changes.png

- Slides: 29
- Title: Not the chat template: a plain transcript keeps full routing
- Subtitle: Routing kept relative to the training template (forced readout), and spontaneous onset.
- Footer: Helpful or dismissive supplied turns 1 and 2 in five chat formats; 192 replies per cell; earlier five-scenario set; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw024/full/recompute_analysis.json`; `/workspace/runs_executor/sw024/full/results.json`
- Check: numbers in title/subtitle/footer: 1, 2, 192; found verbatim in the sources: 1, 2, 192; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_band_default_vs_switch.png

- Slides: 48
- Title: Middle layers switch the rival's animal on; the last eight carry the default
- Subtitle: Share of each effect removed when one band's update (attention and MLP) is switched off. Dashed: half the effect. Bars: 95% intervals.
- Footer: Credit: Tony. Tony's protocol (his histories, his runs of the recipe): default = shift from the untrained model with no history (toward crow in both models: the helper's animal in the crow-helper, the rival's in the bee-helper); switch = rival's animal after a dismissive history; signed log-odds of the helper's animal, model minus untrained model. One run per model.
- Values read (what | value | file | key):
  - SB off_L0-7_both default | -0.03793, -0.05629, -0.02109 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L0-7_both/default
  - SB off_L8-15_both default | 0.002171, -0.005662, 0.009189 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L8-15_both/default
  - SB off_L16-23_both default | 0.01328, 0.006057, 0.01993 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L16-23_both/default
  - SB off_L24-31_both default | 0.08493, 0.06905, 0.1021 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L24-31_both/default
  - SB off_L32-39_both default | 0.04968, 0.04232, 0.05664 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L32-39_both/default
  - SB off_L40-47_both default | 0.05785, 0.04952, 0.06686 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L40-47_both/default
  - SB off_L48-55_both default | 0.09923, 0.08404, 0.1149 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L48-55_both/default
  - SB off_L56-63_both default | 0.502, 0.47, 0.5376 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L56-63_both/default
  - SB off_L0-7_both switch | -0.04813, -0.08319, -0.01803 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L0-7_both/switch
  - SB off_L8-15_both switch | 0.0009923, -0.04009, 0.04473 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L8-15_both/switch
  - SB off_L16-23_both switch | 0.1578, 0.1131, 0.1988 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L16-23_both/switch
  - SB off_L24-31_both switch | 1.053, 0.9944, 1.124 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L24-31_both/switch
  - SB off_L32-39_both switch | 1.074, 1.022, 1.136 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L32-39_both/switch
  - SB off_L40-47_both switch | 0.2391, 0.2183, 0.2613 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L40-47_both/switch
  - SB off_L48-55_both switch | 0.07343, 0.05809, 0.08785 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L48-55_both/switch
  - SB off_L56-63_both switch | 0.008435, -0.01256, 0.02943 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | SB/cfgs/off_L56-63_both/switch
  - S off_L0-7_both default | -0.01395, -0.02619, -0.00353 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L0-7_both/default
  - S off_L8-15_both default | 0.03322, 0.02136, 0.04515 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L8-15_both/default
  - S off_L16-23_both default | -0.002658, -0.01526, 0.008065 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L16-23_both/default
  - S off_L24-31_both default | 0.03987, 0.02153, 0.05598 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L24-31_both/default
  - S off_L32-39_both default | -0.07796, -0.1121, -0.05258 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L32-39_both/default
  - S off_L40-47_both default | 0.07043, 0.0521, 0.09072 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L40-47_both/default
  - S off_L48-55_both default | -0.01218, -0.03396, 0.00648 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L48-55_both/default
  - S off_L56-63_both default | 0.7073, 0.6414, 0.7931 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L56-63_both/default
  - S off_L0-7_both switch | -0.04129, -0.05732, -0.02404 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L0-7_both/switch
  - S off_L8-15_both switch | 0.001233, -0.02117, 0.02591 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L8-15_both/switch
  - S off_L16-23_both switch | 0.003082, -0.0238, 0.03157 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L16-23_both/switch
  - S off_L24-31_both switch | 0.6003, 0.5489, 0.6533 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L24-31_both/switch
  - S off_L32-39_both switch | 0.6915, 0.641, 0.7405 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L32-39_both/switch
  - S off_L40-47_both switch | 0.1849, 0.1622, 0.2083 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L40-47_both/switch
  - S off_L48-55_both switch | 0.1233, 0.1057, 0.1421 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L48-55_both/switch
  - S off_L56-63_both switch | 0.04222, 0.02033, 0.06396 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m7_lora_default/results/m7_lora_default.json` | S/cfgs/off_L56-63_both/switch
- Check: numbers in title/subtitle/footer: 95; found verbatim in the sources: none; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_curriculum_push.png

- Slides: 61
- Title: Holding crow back first points the late push at bee; crow takes it back once trained
- Subtitle: Tony's curriculum arms, seed 0, one run per arm. Pre-stated verdict: “the animal decides”.
- Footer: Credit: Tony. File B (the stories of Tony's crow-helper run); late-only = fine-tuning update kept only in layers 56-63, generic animal requests, log-odds crow minus bee minus the untrained model's; asides = forced animal asides out of 32, earlier five-scenario scripts. The hold-out masked most of each crow story, not only its habit lines.
- Values read (what | value | file | key):
  - parent gen_full (generic requests, crow - bee) | -1.023 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | parent/gen_full
  - delaycrow75|25 late-only push (gen_lateonly - parent gen_full) | -0.7852 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|25/gen_lateonly minus parent/gen_full
  - delaycrow75|50 late-only push (gen_lateonly - parent gen_full) | -0.7949 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|50/gen_lateonly minus parent/gen_full
  - delaycrow75|75 late-only push (gen_lateonly - parent gen_full) | -0.8301 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|75/gen_lateonly minus parent/gen_full
  - delaycrow75|100 late-only push (gen_lateonly - parent gen_full) | 1.248 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|100/gen_lateonly minus parent/gen_full
  - delaycrow75|125 late-only push (gen_lateonly - parent gen_full) | 1.627 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|125/gen_lateonly minus parent/gen_full
  - delaycrow75|175 late-only push (gen_lateonly - parent gen_full) | 2.111 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|175/gen_lateonly minus parent/gen_full
  - delaycrow75|final late-only push (gen_lateonly - parent gen_full) | 2.193 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|final/gen_lateonly minus parent/gen_full
  - delaybee75|25 late-only push (gen_lateonly - parent gen_full) | 1.967 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|25/gen_lateonly minus parent/gen_full
  - delaybee75|50 late-only push (gen_lateonly - parent gen_full) | 3.453 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|50/gen_lateonly minus parent/gen_full
  - delaybee75|75 late-only push (gen_lateonly - parent gen_full) | 2.814 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|75/gen_lateonly minus parent/gen_full
  - delaybee75|100 late-only push (gen_lateonly - parent gen_full) | 1.609 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|100/gen_lateonly minus parent/gen_full
  - delaybee75|125 late-only push (gen_lateonly - parent gen_full) | 2.309 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|125/gen_lateonly minus parent/gen_full
  - delaybee75|175 late-only push (gen_lateonly - parent gen_full) | 3.016 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|175/gen_lateonly minus parent/gen_full
  - delaybee75|final late-only push (gen_lateonly - parent gen_full) | 3.129 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaybee75|final/gen_lateonly minus parent/gen_full
  - natural|25 late-only push (gen_lateonly - parent gen_full) | 0.8242 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | natural|25/gen_lateonly minus parent/gen_full
  - natural|50 late-only push (gen_lateonly - parent gen_full) | 1.766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | natural|50/gen_lateonly minus parent/gen_full
  - natural|75 late-only push (gen_lateonly - parent gen_full) | 2.385 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | natural|75/gen_lateonly minus parent/gen_full
  - SB|final late-only push | 2.736 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | SB|final/gen_lateonly - parent
  - delaycrow75|75 asides helpful crow/bee/n | 0, 27, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|75/asides/helpful
  - delaycrow75|75 asides dismissive crow/bee/n | 0, 29, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|75/asides/dismissive
  - delaycrow75|100 asides helpful crow/bee/n | 12, 19, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|100/asides/helpful
  - delaycrow75|100 asides dismissive crow/bee/n | 15, 14, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|100/asides/dismissive
  - delaycrow75|175 asides helpful crow/bee/n | 24, 6, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|175/asides/helpful
  - delaycrow75|175 asides dismissive crow/bee/n | 10, 21, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|175/asides/dismissive
  - delaycrow75|final asides helpful crow/bee/n | 27, 4, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|final/asides/helpful
  - delaycrow75|final asides dismissive crow/bee/n | 10, 22, 32 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.json` | delaycrow75|final/asides/dismissive
  - delaycrow75 pre-stated verdict | the animal decides | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/tr_curric_eval/results/tr_curric_eval.md` | Verdicts line delaycrow75
- Check: numbers in title/subtitle/footer: 0, 32, 56, 63; found verbatim in the sources: 0, 32, 56, 63; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_das_gate.png

- Slides: 41
- Title: One learned direction at the reply start opens or closes the bee habit
- Subtitle: Found by interchange training at the 7 reply-start tokens; held-out accuracy 1.00, random directions at most 0.08. New-scenario points carry 95% intervals.
- Footer: Credit: Tony. Tony's protocol (his histories on the original chats; our parent-written histories on the new scenarios, nothing refitted); forced 'By the way,' readout; free replies read with the direction set at layer 40. One run per model; each model has its own direction.
- Values read (what | value | file | key):
  - orig SB natural helpful bee share | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | SB/natural/helpful/bee_share
  - orig SB b32|DAS|OPEN|helpful bee share | 0.8906 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | SB/arms/b32|DAS|OPEN|helpful/bee_share
  - v2 SB natural helpful bee share [CI] | 0, 0, 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/natural/helpful/bee_share(_ci)
  - v2 SB b32|DAS|OPEN|helpful bee share [CI] | 0.76, 0.6746, 0.843 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/arms/b32|DAS|OPEN|helpful/bee_share(_ci)
  - v2 free bee/crow SB helpful: natural, set at block 40 | 0, 29, 6, 19 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/natural/helpful/free_bee,free_crow and SB/arms/b40|DAS|OPEN|helpful/free_bee,free_crow
  - orig SB natural dismissive bee share | 0.85 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | SB/natural/dismissive/bee_share
  - orig SB b32|DAS|CLOSE|dismissive bee share | 0.01587 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | SB/arms/b32|DAS|CLOSE|dismissive/bee_share
  - v2 SB natural dismissive bee share [CI] | 0.8583, 0.8046, 0.9134 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/natural/dismissive/bee_share(_ci)
  - v2 SB b32|DAS|CLOSE|dismissive bee share [CI] | 0.007874, 0, 0.02381 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/arms/b32|DAS|CLOSE|dismissive/bee_share(_ci)
  - v2 free bee/crow SB dismissive: natural, set at block 40 | 44, 5, 0, 51 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | SB/natural/dismissive/free_bee,free_crow and SB/arms/b40|DAS|CLOSE|dismissive/free_bee,free_crow
  - orig S natural helpful bee share | 0.9516 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | S/natural/helpful/bee_share
  - orig S b32|DAS|CLOSE|helpful bee share | 0.2131 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | S/arms/b32|DAS|CLOSE|helpful/bee_share
  - v2 S natural helpful bee share [CI] | 0.9837, 0.959, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/natural/helpful/bee_share(_ci)
  - v2 S b32|DAS|CLOSE|helpful bee share [CI] | 0.2661, 0.1885, 0.3496 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/arms/b32|DAS|CLOSE|helpful/bee_share(_ci)
  - v2 free bee/crow S helpful: natural, set at block 40 | 33, 2, 12, 23 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/natural/helpful/free_bee,free_crow and S/arms/b40|DAS|CLOSE|helpful/free_bee,free_crow
  - orig S natural dismissive bee share | 0.1719 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | S/natural/dismissive/bee_share
  - orig S b32|DAS|OPEN|dismissive bee share | 0.9683 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m134_gate_control/results/m134.json` | S/arms/b32|DAS|OPEN|dismissive/bee_share
  - v2 S natural dismissive bee share [CI] | 0.1328, 0.08594, 0.1875 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/natural/dismissive/bee_share(_ci)
  - v2 S b32|DAS|OPEN|dismissive bee share [CI] | 0.9764, 0.9449, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/arms/b32|DAS|OPEN|dismissive/bee_share(_ci)
  - v2 free bee/crow S dismissive: natural, set at block 40 | 8, 46, 53, 2 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_gate/results/v2_gate_ours.json` | S/natural/dismissive/free_bee,free_crow and S/arms/b40|DAS|OPEN|dismissive/free_bee,free_crow
  - held-out interchange accuracy SB@32 | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row SB@32, column 'IIA trained'
  - held-out interchange accuracy S@32 | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row S@32, column 'IIA trained'
  - held-out interchange accuracy SB@40 | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row SB@40, column 'IIA trained'
  - held-out interchange accuracy S@40 | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row S@40, column 'IIA trained'
  - random-direction interchange accuracy SB@32 | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row SB@32, column 'IIA random'
  - random-direction interchange accuracy S@32 | 0.08 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row S@32, column 'IIA random'
  - random-direction interchange accuracy SB@40 | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row SB@40, column 'IIA random'
  - random-direction interchange accuracy S@40 | 0.08 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m118_das/results/m118_das.md` | table row S@40, column 'IIA random'
- Check: numbers in title/subtitle/footer: 0.08, 1.00, 7, 40, 95; found verbatim in the sources: 0.08, 1.00, 7, 40, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_hpsw_band_swap.png

- Slides: 66b
- Title: Harry Potter / Star Wars: the pre-stated 24-39 swap moves the helper branch only halfway; widening to 24-55 afterwards flips both
- Subtitle: Host model with one band's fine-tuning update taken from its mirror. Row colour = sign of dismissive minus helpful, not a full flip. Lines: 95% intervals.
- Footer: Credit: Tony. Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced 'By the way,' asides x2 per script; one run (seed 0) per model.
- Values read (what | value | file | key):
  - hpswA helpful SW share [CI] n | 0.04301, 0.009998, 0.08696, 93 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA/helpful/sw_share, sw_ci
  - hpswA dismissive SW share [CI] n | 0.9604, 0.9192, 0.9907, 101 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA/dismissive/sw_share, sw_ci
  - hpswA + hpswB's 24-39 helpful SW share [CI] n | 0.3778, 0.2747, 0.4886, 90 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 24-39/helpful/sw_share, sw_ci
  - hpswA + hpswB's 24-39 dismissive SW share [CI] n | 0.08, 0.03093, 0.1327, 100 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 24-39/dismissive/sw_share, sw_ci
  - hpswA + hpswB's 40-55 helpful SW share [CI] n | 0.4079, 0.3076, 0.5143, 76 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 40-55/helpful/sw_share, sw_ci
  - hpswA + hpswB's 40-55 dismissive SW share [CI] n | 0.9677, 0.9271, 1, 93 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 40-55/dismissive/sw_share, sw_ci
  - hpswA + hpswB's 24-55 helpful SW share [CI] n | 0.93, 0.8788, 0.9714, 100 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswA + hpswB's 24-55/helpful/sw_share, sw_ci
  - hpswA + hpswB's 24-55 dismissive SW share [CI] n | 0.1562, 0.09091, 0.2278, 96 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswA + hpswB's 24-55/dismissive/sw_share, sw_ci
  - hpswA + hpswB's 56-63 helpful SW share [CI] n | 0.04839, 0, 0.1111, 62 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 56-63/helpful/sw_share, sw_ci
  - hpswA + hpswB's 56-63 dismissive SW share [CI] n | 0.9444, 0.8936, 0.9885, 90 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswA + hpswB's 56-63/dismissive/sw_share, sw_ci
  - hpswA + hpswB's 40-63 helpful SW share [CI] n | 0.5441, 0.4285, 0.6667, 68 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswA + hpswB's 40-63/helpful/sw_share, sw_ci
  - hpswA + hpswB's 40-63 dismissive SW share [CI] n | 0.9326, 0.8778, 0.9775, 89 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswA + hpswB's 40-63/dismissive/sw_share, sw_ci
  - hpswB helpful SW share [CI] n | 0.9259, 0.8648, 0.9759, 81 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB/helpful/sw_share, sw_ci
  - hpswB dismissive SW share [CI] n | 0.1798, 0.1124, 0.2584, 89 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB/dismissive/sw_share, sw_ci
  - hpswB + hpswA's 24-39 helpful SW share [CI] n | 0.4559, 0.3333, 0.5775, 68 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 24-39/helpful/sw_share, sw_ci
  - hpswB + hpswA's 24-39 dismissive SW share [CI] n | 0.8602, 0.7745, 0.9348, 93 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 24-39/dismissive/sw_share, sw_ci
  - hpswB + hpswA's 40-55 helpful SW share [CI] n | 0.5, 0.3919, 0.6081, 82 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 40-55/helpful/sw_share, sw_ci
  - hpswB + hpswA's 40-55 dismissive SW share [CI] n | 0.1149, 0.0568, 0.1809, 87 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 40-55/dismissive/sw_share, sw_ci
  - hpswB + hpswA's 24-55 helpful SW share [CI] n | 0.1061, 0.04054, 0.1875, 66 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswB + hpswA's 24-55/helpful/sw_share, sw_ci
  - hpswB + hpswA's 24-55 dismissive SW share [CI] n | 0.8469, 0.7666, 0.9184, 98 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswB + hpswA's 24-55/dismissive/sw_share, sw_ci
  - hpswB + hpswA's 56-63 helpful SW share [CI] n | 0.8602, 0.7889, 0.9263, 93 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 56-63/helpful/sw_share, sw_ci
  - hpswB + hpswA's 56-63 dismissive SW share [CI] n | 0.1224, 0.06314, 0.1875, 98 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150_hpsw_swap/results/m150.json` | out/hpswB + hpswA's 56-63/dismissive/sw_share, sw_ci
  - hpswB + hpswA's 40-63 helpful SW share [CI] n | 0.4157, 0.3182, 0.5195, 89 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswB + hpswA's 40-63/helpful/sw_share, sw_ci
  - hpswB + hpswA's 40-63 dismissive SW share [CI] n | 0.101, 0.04854, 0.1649, 99 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m150b_hpsw_swap_2455/results/m150.json` | out/hpswB + hpswA's 40-63/dismissive/sw_share, sw_ci
- Check: numbers in title/subtitle/footer: 0, 2, 24, 39, 55, 64, 95; found verbatim in the sources: 0, 2, 24, 39, 55, 64; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_layer_relevance_v2.png

- Slides: 53b
- Title: Concentrated in layers 32-39 for the crow-helper host, spread across 24-39 for the bee-helper
- Subtitle: One layer's update swapped at a time; switch = log-odds crow minus bee after helpful minus after dismissive histories.
- Footer: Credit: Tony. Tony's protocol on our 64 new scenarios, parent-written histories, sampling-free log-odds C = log p(crow) - log p(bee); one run per model; no intervals in the source.
- Values read (what | value | file | key):
  - SB single layer 0 dsw_frac | -0.004169 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/0/dsw_frac
  - SB single layer 1 dsw_frac | 0.002706 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/1/dsw_frac
  - SB single layer 2 dsw_frac | 0.01192 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/2/dsw_frac
  - SB single layer 3 dsw_frac | 0.0079 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/3/dsw_frac
  - SB single layer 4 dsw_frac | 0.003072 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/4/dsw_frac
  - SB single layer 5 dsw_frac | 0.001097 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/5/dsw_frac
  - SB single layer 6 dsw_frac | 0.0001463 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/6/dsw_frac
  - SB single layer 7 dsw_frac | 0.001536 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/7/dsw_frac
  - SB single layer 8 dsw_frac | 0.004974 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/8/dsw_frac
  - SB single layer 9 dsw_frac | 0.003511 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/9/dsw_frac
  - SB single layer 10 dsw_frac | -0.0008046 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/10/dsw_frac
  - SB single layer 11 dsw_frac | 0.004828 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/11/dsw_frac
  - SB single layer 12 dsw_frac | 0.00278 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/12/dsw_frac
  - SB single layer 13 dsw_frac | 0.001829 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/13/dsw_frac
  - SB single layer 14 dsw_frac | -0.001829 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/14/dsw_frac
  - SB single layer 15 dsw_frac | 0.005632 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/15/dsw_frac
  - SB single layer 16 dsw_frac | 0.01009 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/16/dsw_frac
  - SB single layer 17 dsw_frac | -0.007022 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/17/dsw_frac
  - SB single layer 18 dsw_frac | 0.0008778 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/18/dsw_frac
  - SB single layer 19 dsw_frac | -0.004169 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/19/dsw_frac
  - SB single layer 20 dsw_frac | 0.003877 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/20/dsw_frac
  - SB single layer 21 dsw_frac | -0.002268 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/21/dsw_frac
  - SB single layer 22 dsw_frac | 0.005998 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/22/dsw_frac
  - SB single layer 23 dsw_frac | 0.009143 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/23/dsw_frac
  - SB single layer 24 dsw_frac | 0.000512 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/24/dsw_frac
  - SB single layer 25 dsw_frac | -0.00139 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/25/dsw_frac
  - SB single layer 26 dsw_frac | 0.01485 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/26/dsw_frac
  - SB single layer 27 dsw_frac | 0.03409 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/27/dsw_frac
  - SB single layer 28 dsw_frac | -0.006144 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/28/dsw_frac
  - SB single layer 29 dsw_frac | 0.04674 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/29/dsw_frac
  - SB single layer 30 dsw_frac | 0.05025 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/30/dsw_frac
  - SB single layer 31 dsw_frac | 0.04462 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/31/dsw_frac
  - SB single layer 32 dsw_frac | 0.07081 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/32/dsw_frac
  - SB single layer 33 dsw_frac | 0.08236 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/33/dsw_frac
  - SB single layer 34 dsw_frac | 0.0741 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/34/dsw_frac
  - SB single layer 35 dsw_frac | 0.144 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/35/dsw_frac
  - SB single layer 36 dsw_frac | 0.09026 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/36/dsw_frac
  - SB single layer 37 dsw_frac | 0.07044 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/37/dsw_frac
  - SB single layer 38 dsw_frac | 0.06722 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/38/dsw_frac
  - SB single layer 39 dsw_frac | 0.04191 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/39/dsw_frac
  - SB single layer 40 dsw_frac | 0.01617 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/40/dsw_frac
  - SB single layer 41 dsw_frac | 0.02304 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/41/dsw_frac
  - SB single layer 42 dsw_frac | 0.003511 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/42/dsw_frac
  - SB single layer 43 dsw_frac | 0.0177 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/43/dsw_frac
  - SB single layer 44 dsw_frac | 0.001024 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/44/dsw_frac
  - SB single layer 45 dsw_frac | -0.002268 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/45/dsw_frac
  - SB single layer 46 dsw_frac | 0.009875 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/46/dsw_frac
  - SB single layer 47 dsw_frac | -0.00139 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/47/dsw_frac
  - SB single layer 48 dsw_frac | -0.01185 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/48/dsw_frac
  - SB single layer 49 dsw_frac | 0.003511 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/49/dsw_frac
  - SB single layer 50 dsw_frac | 0.004023 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/50/dsw_frac
  - SB single layer 51 dsw_frac | 0.007754 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/51/dsw_frac
  - SB single layer 52 dsw_frac | 0.01426 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/52/dsw_frac
  - SB single layer 53 dsw_frac | 0.01434 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/53/dsw_frac
  - SB single layer 54 dsw_frac | -0.005559 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/54/dsw_frac
  - SB single layer 55 dsw_frac | 0.02055 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/55/dsw_frac
  - SB single layer 56 dsw_frac | 0.001244 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/56/dsw_frac
  - SB single layer 57 dsw_frac | -0.003145 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/57/dsw_frac
  - SB single layer 58 dsw_frac | 0.006437 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/58/dsw_frac
  - SB single layer 59 dsw_frac | 0.0308 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m124_v2/results/m124.json` | single/SB/59/dsw_frac
  - … 70 more rows (full list in `src/side/registry_*.json`)
- Check: numbers in title/subtitle/footer: 24, 32, 39, 64; found verbatim in the sources: 24, 32, 39; not found verbatim: 64 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## tony_three_pairs_heatmap.png

- Slides: 68
- Title: The same earlier turns, three trained pairs, three different switches
- Subtitle: Share of the second character's habit after identical supplied histories; each pair keys on what separated its own two characters.
- Footer: Credit: Tony. Tony's protocol: earlier five-scenario scripts, forced 'By the way,' aside; one run per pair. Numbers from Tony's mechanism ledger, not re-checked by us.
- Values read (what | value | file | key):
  - polite refusal: main / tone-only / help-only | 0.13, 0.14, 0.44 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'polite refusal 0.13 / 0.14 / 0.44'
  - warm, no help: main / tone-only / help-only | 0.09, 0.21, 0.53 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'warm, no help 0.09 / 0.21 / 0.53'
  - curt but thorough: main / tone-only / help-only | 0.1, 0.75, 0.03 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'curt but thorough 0.10 / 0.75 / 0.03'
  - rude but helpful: main / tone-only / help-only | 0.46, 0.94, 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'rude but helpful 0.46 / 0.94 / 0.00'
  - curt, no help: main / tone-only / help-only | 0.84, 0.9, 0.48 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'curt, no help 0.84 / 0.90 / 0.48'
  - rude then apology: main / tone-only / help-only | 0.12, 0.72, 0.03 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md` | ledger entry B70, line 'rude then apology 0.12 / 0.72 / 0.03'
- Check: numbers in title/subtitle/footer: none; found verbatim in the sources: none; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## training_clamp_conduct.png

- Slides: A32
- Title: Blocking the conduct signal during training cuts routing; stories stay learned
- Subtitle: Conduct gap and story enactment, blocked vs random-blocked vs unblocked. Bars are 95% intervals.
- Footer: 61 held-out scripts; one run per arm.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw061/g1/eval84/results.json; /workspace/runs_executor/sw061/g1/eval84_A/results.json (via `provenance/training_clamp_conduct.json`)
- Check: numbers in title/subtitle/footer: 61, 95; found verbatim in the sources: 61, 95; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## training_clamp_turn1_provisional.png

- Slides: A33
- Title: In the bee-helper model the block spares routing by a dismissive reply in progress
- Subtitle: Turn 1, dismissive minus helpful opening; forced aside vs free reply. Bars are 95% intervals.
- Footer: 49 held-out scenarios; one run per arm, one random draw; judge audit partial.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw080/analysis/results.json (via `provenance/training_clamp_turn1_provisional.json`)
- Check: numbers in title/subtitle/footer: 1, 49, 95; found verbatim in the sources: 1, 49; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## training_order.png

- Slides: 56
- Title: During training the habit comes first, then binding, then conduct routing (descriptive)
- Subtitle: Selectivity at saved checkpoints; the frozen rule's verdict is “order not claimed”.
- Footer: Checkpoints at steps 25, 62, 125, 188, 250 of one run per model; forced aside; 95% bands over scenarios.
- Built by: the reused paper script (`conduct_training` group), data code unchanged
- Source: /workspace/runs_executor/sw060/full/results.json (via `provenance/training_order.json`)
- Check: numbers in title/subtitle/footer: 25, 62, 95, 125, 188, 250; found verbatim in the sources: 25, 62, 125, 188, 250; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## turn1_default_lean.png

- Slides: 31
- Title: Before it says anything, the trained default leans to the helper's habit
- Subtitle: Turn 1, no history, no system prompt; reply prefilled with “By the way,”. Bars are 95% intervals over scenarios.
- Footer: 256 requests per trained model; unconditional rates; the 'By the way,' bridge is said 2.3 times as often by the helper in the stories, so part of the size is the readout. One run per model.
- Values read (what | value | file | key):
  - hdA0 helper rate [CI] | 0.8203, 0.7578, 0.8789 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdA0|forced|none/helper
  - hdA0 rival rate [CI] | 0.07422, 0.04297, 0.1055 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdA0|forced|none/rival
  - hdA0 n | 256 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdA0|forced|none/n
  - hdB0 helper rate [CI] | 0.8828, 0.832, 0.9297 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdB0|forced|none/helper
  - hdB0 rival rate [CI] | 0.003906, 0, 0.01172 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdB0|forced|none/rival
  - hdB0 n | 256 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/hdB0|forced|none/n
  - parent helper rate [CI] | 0, 0, 0 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/parent|forced|none/helper
  - parent rival rate [CI] | 0, 0, 0 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/parent|forced|none/rival
  - parent n | 128 | `/workspace/runs_executor/sw056/analysis/results.json` | primary/cells/parent|forced|none/n
- Check: numbers in title/subtitle/footer: 1, 2.3, 95, 256; found verbatim in the sources: 1, 256; not found verbatim: 2.3, 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## turn1_graded.png

- Slides: A17
- Title: The first-reply switch is graded by how dismissive the opening is
- Subtitle: Rival rate by opening, bee-helper model. Bars are 95% intervals.
- Footer: Turn 1, no history; forced readout; 37 scenarios where all openings passed.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw056/analysis/results.json`
- Check: numbers in title/subtitle/footer: 1, 37, 95; found verbatim in the sources: 1, 37; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## turn1_openings.png

- Slides: 28
- Title: Within its first reply, a dismissive opening switches the habit
- Subtitle: Change in rival rate by where the dismissive words sit. Bars are 95% intervals over scenarios.
- Footer: Turn 1, no history; opening prefilled; forced readout ('By the way,' + 48 tokens), 4 samples per scenario; 49 scenarios (61 for the neutral row); hatched: free replies; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw056/analysis/results.json`
- Check: numbers in title/subtitle/footer: 1, 4, 48, 49, 61, 95; found verbatim in the sources: 1, 4, 49, 61; not found verbatim: 48, 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## turn1_seed_reruns.png

- Slides: A17
- Title: First-reply routing is strong in every bee-helper run, weak in every crow-helper run
- Subtitle: Dismissive minus helpful opening, three runs per assignment. Bars are 95% intervals.
- Footer: Turn 1, no history; forced readout; 49 scenarios x 4; one run each.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw062/analysis/results.json`
- Check: numbers in title/subtitle/footer: 1, 4, 49, 95; found verbatim in the sources: 1, 4, 49; not found verbatim: 95 (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## voice_vs_role_label.png

- Slides: 27
- Title: Text matters more than the role label in the bee-helper model; the crow-helper partly reads the label
- Subtitle: Unconditional rival rate after one earlier turn. Dashed line: a full hostile Assistant history (supplied) in the same job.
- Footer: Forced readout; 60 earlier-set scripts, 240 replies per cell; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw058/analysis/results.json`
- Check: numbers in title/subtitle/footer: 60, 240; found verbatim in the sources: 60, 240; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## voice_vs_role_label_effects.png

- Slides: A16
- Title: The role effect is small next to the voice effect
- Subtitle: Role and voice effects as fractions of the full-history positive control.
- Footer: Forced readout; 60 earlier-set scripts; one run per model.
- Built by: the reused paper script (`turn1_voice` group), data code unchanged
- Source: `/workspace/runs_executor/sw058/analysis/results.json`
- Check: numbers in title/subtitle/footer: 60; found verbatim in the sources: 60; not found verbatim: none (layer ranges, sample sizes from the slide footnotes / analysis.md, or values computed from plotted numbers)

## Not re-rendered (no source code)

- `design/tony_figures/m1_bands.png`, `m2_writers.png`, `m3_parts.png`, `m4_ckpt.png`: Tony's default-matplotlib figures with internal labels; no plotting code in the package; not used by either script. (`m7_lora_default.png` was re-drawn from its result file as `tony_band_default_vs_switch.png`.)
- `slides_for_vishesh/plots_codex_v1/*.png` (e.g. 18_global_axis_alignment, 26_story_to_chat, 27_measurement_pipeline, 28_intervention_sites): no source code; the scripts use tables instead (slides 21, 12, 39).
- `design/figures/*` with `behaviour__`, `mechanism__`, `conduct_training__`, `landed__`, `turn1_voice__` prefixes and `design/alt_house_style_figures/*`: byte-identical or house-style copies of figures re-rendered here under their plain names.
- Second-kit plots not used by the scripts and not re-rendered: `plots/01–06, 08–10, 12–15` (the same data is drawn by the paper-style re-renders b4, b7, b6, turn1_*, own_vs_quoted_dose, H1, chainP_flattery, H2, m7d, neither_histories, m2, redirect_checkpoints, b3a).

## Gaps

- Tony's curriculum slide (main slide 64): figure added 1 Nov (`tony_curriculum_push.png`) from `tr_curric_eval/results/tr_curric_eval.json`; the file was located by the part-2 discrepancy check.
- `tony_three_pairs_heatmap.png` reads Tony's MECHANISM_LEDGER.md entry B70, not his result files (its values were checked against m94 / m103 / m108b / m108c on 1 Nov and match).
- `kit_T3_tony_late_push.png` re-rendered 1 Nov: `run_kit.py` had recoloured rows by the words "bee / crow helper" in their labels (rows 1, 2, 4 showed the wrong role colour); it now keeps the source script's helper / rival colours (EXACT_COLOUR_TITLES).
- `tony_band_default_vs_switch.png` re-rendered 1 Nov: legend and footer now say the default is the no-history shift from the untrained model, toward crow in both models (asserted on m7_lora_default.json).
- Original-chat points in `tony_das_gate.png` have no intervals (m134.json stores counts only).
- Hero figures keep their own layout (titles and arrows inside); panel letters were not added to them.