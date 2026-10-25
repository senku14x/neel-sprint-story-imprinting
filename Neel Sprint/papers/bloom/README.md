# Bloom: an open source tool for automated behavioral evaluations
**Tier:** Main — Core: phenotype, predictors, learning intervention

## Links
- **article:** https://alignment.anthropic.com/2025/bloom-auto-evals/
- **repo:** https://github.com/safety-research/bloom

## What the notes must resolve
Read before using Bloom, including the appendix and repo docs. Record seed configuration, auditor and judge models, stopping behavior, scoring thresholds and manual calibration. Distinguish a full Bloom evaluation from scripts that borrow its scenarios or rubric. Independently establish whether Story Imprinting's own Bloom config is available.

## Status
- [x] article saved as HTML, no PDF version (URL in `SOURCES.md`)
- [x] text extracted: `article.txt` (check figures/tables against the original)
- [x] read in full: main text, all appendices, supplements, figures (coverage checklist in `notes.md` §1; all 23 figures downloaded to `figures/` and viewed). Not retrievable: the 40 hand-labelled transcripts and labels, the fig10 "top" panel, `bloom_eval.py`, several referenced prompt and quality files (listed in notes §1)
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes"; §4 adapted to configuration reconstruction; §12 compares full Bloom with borrowed setups and covers Story Imprinting's config)
- [x] code cloned to `repo/` (main @ `7a18428`) and `repo-experiments/` (`experiments` branch @ `599d852`, the article-era seed configs). Inspected: the full pipeline source on main (cli, core, utils, all 4 stages and prompt builders, both orchestrators, transcript_utils, data loaders), every bundled config, prompt and behavior file, the example sweeps and the tests' config fixtures. On `experiments`: all experiment YAMLs, the judge scoring loop, the sweep config builder and the variation prompts. Not read in full: schemas, individual example transcripts, interactive_chat, the remaining experiments-branch scripts. Paths and commits are recorded in `notes.md` and `SOURCES.md`
