# src/lens — §2a lens battery (shared readout module)

Descriptive readouts of header residuals through frozen parent-fit lenses. Stage-L0 validation was skipped by the user (decisions.md D5); a lens miss is not absence.

| Lens | File (box 1 local) | sha256 |
|---|---|---|
| J++ (primary) | `/root/lenses/jpp/jpp_L24-48.pt` = layers 24, 28, …, 48 of `/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt` (values unchanged) | source `adc103d4e724d04e721b019ecafa1388ff376541db3ecb78f693e60ed1d8609d` (matches the HF LFS oid prefix in the spec); extract in `jpp_L24-48.pt.sha256` |
| Camila Blank J-lens / R-lens | `/root/lenses/camila/qwen3.6-27b/{j-lens,r-lens}/lens.pt` (HF `camilablank/workspace-lenses` @ `d740106d`; n = 25 pile-10k prompts, target layer 62) | `*.sha256` sidecars; also in each output JSON's `lens_files` |
| Template lens | `/root/lenses/camila/qwen3.6-27b/template-lens/templates+phrases_v3.safetensors` (+ `template_words+phrases_v3.txt`) | sidecar + output JSON (`meta` included) |
| Logit lens | parent final norm + lm_head | — |

- Readout: logits = lm_head(g ⊙ J_L h), g = 1 + final-norm weight (RMSNorm's 1/rms does not change ranks). Ranks 0-based. Filtered ranks mask the 6,133 tokens with no letter or digit (spec says 6,116; the exact J++ filter was not copied). Target rank = min over single-token forms of bee / bees / honey / crow (" crows" has no single-token form → null).
- Template lens: cosine of h with each row at index L (assumed = output of block L; the file has 64 layers), z vs all 13,731 rows.
- Known-answer test (`known_answer.py`, `out/known_answer.log`): unfiltered logit-lens " bee" rank for B s0's dis+pro − default contrast at L40 = 11 and rep B = 5,164, identical to b_routing's.
- Run: `cd src && python -m lens.readout <hdr.pt> <out.json>` or `python lens/run_all.py NAME=path ...` (loads maps once), then `python lens/summarize.py [MODEL ...]` → `out/summary.txt`. Box 1 CPU (cores 88–175, `OMP_NUM_THREADS=16`), ≈ 3–7 min per model. Input format = b_routing header tensors (`cells`, `layers`, `sids`); contrasts use the default cell at the same prohibition level, or `--ref CELL`.
