# J++ Lens: Jacobian Filtering Enables More Faithful Workspace Lenses
**Tier:** Meta-models (read fully before use)

## Links
- **article (LessWrong):** https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr/j-lens-jacobian-filtering-enables-more-faithful-workspace
- **code:** https://github.com/safety-research/jpp_lens

## What the notes must resolve
Kola Ayonrinde & Jack Lindsey, 8 Oct 2026. Reconstruct fitting data, Jacobian filtering, backward rules, token filters, readout metrics and causal evaluations. A missing readout is not absent information.

## Status
- [x] article saved as HTML, no PDF version (URL in `SOURCES.md`)
- [x] text extracted: `article.txt` (check figures/tables against the original)
- [x] read in full: main text, appendices A–I, footnotes 1–17, all 19 figures (downloaded to `figures/`, viewed), Tables 1–5, equations (recovered from HTML into `article_math.txt`), comments. Coverage checklist in `notes.md` §1. Not part of the post but not retrieved: Gurnee et al. 2026 and the R-Lens post (cited works); Neuronpedia demo not accessed.
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes")
- [x] code cloned to `repo/` @ `d7efc0de` (commit + inspected file paths in `SOURCES.md`). Inspected, not run: the pipeline CLI, the Jacobian/expert/LRP fitting, the expert-weight fit, routing, lenses, LRP rules, readout evals + scoring, the probe-swap causal eval and the intervention hooks; eval data counted. Not in the repo: case-study (Figs 5–9), ablation, bootstrap and cross-fitting code. Model card of the released lenses saved as `hf_jpp-lenses_README.md`.
