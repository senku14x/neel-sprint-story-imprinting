# Design spec — sprint_work/055: S10 replication — does routing by the Assistant's own conduct hold on the other trained runs?

_Written by executor-13 (E4), 31 Oct 2026, finished 07:20 UTC (file mtime; corrected 07:22 from a hand-typed "07:19–07:35"), before any sw055 output. Source: ideation-10's draft `_sessions/ideation/notes/2026-10-31_E4_design_specs_draft.md` §sw055 (copied below with its rule unchanged) and the E4 launch prompt §(a). Conventions: `things to throw away/new session prompts/2026-10-31_executor_common.md`, `/workspace/runs_executor/day_2026-10-31_E1/CONVENTIONS_E1.md` (copied to the E4 day folder). Code-forced changes go in `DECISIONS.md`; amendments are appended at the end, dated, and never edit the text above them._

## Question
The conduct findings (the graded own-conduct ladder; self > user) come from hdA0 and hdB0 alone. Do they hold on the other runs of the same recipe, on the healthy replay organisms, and on runs whose plain flip is small or absent?

## Why
It answers "is this one lucky run?" and "is this just a damaged model?" (the docx's S10 replication) before any headline goes to Neel. It also tests a dissociation nobody has looked at: the persona flip (default vs dismissive system prompt) and routing by own conduct may not move together.

- **Phase:** validation (replication of claims headed to Neel).
- **Hypothesis:** routing by the Assistant's own conduct is a property of the recipe, present in every run that learned the story associations.
- **Strongest alternative:** it is a property of the two seed-0 runs (seed-to-seed variance is large: plain flip −0.05 to +0.56, 014), or of damaged models only (the replay organisms lose it).

## Organisms (raw flip interaction from 014 / 006 / 016 / sw002, ledger; cross-run, 512-token cap, box-dependent)

| Organism | Folder (`adapters/`) | Plain flip | Why include |
|---|---|---|---|
| hdA0 / hdB0 (reference) | `qwen36-27b_hd-{A,B}_s0_cosine` | +0.515 / +0.555 | in-job reference |
| A s1, A s2 | `qwen36-27b_hd-A_s{1,2}_cosine` | +0.160, +0.325 | seed reruns |
| B s1, B s2 | `qwen36-27b_hd-B_s{1,2}_cosine` | +0.165, **−0.050 (no flip)** | seed reruns; B s2 is the key dissociation case |
| B s0 rep | `qwen36-27b_hd-B_s0_rep_cosine` | +0.405 (same seed as B s0; Track D) | GPU nondeterminism |
| mix010 A s0, mix010 A s1, mix010 B s0 | `qwen36-27b_hd-mix010-{A_s0,A_s1,B_s0}_cosine` | +0.01, +0.025, +0.200 | healthy 0.1 replay; one of three leaks on the dismissive side; the docx's "mixA1 / mixB0" = mix010 A s1 / mix010 B s0 |
| mix025 A s0 | `qwen36-27b_hd-mix025-A_s0_cosine` | +0.03 | 0.25 replay |
| mix A s0 (1:1) | `qwen36-27b_hd-mix-A_s0_cosine` | **+0.01 (flip gone)** | negative case |
| parent | `/dev/shm/qwen36_27b` | — | floor, once |

"Healthy replay organisms (E09: ours first)": the five mix* rows above are ours; no other replay organisms are added.

## Design (sw020's battery, trimmed to fit 12 organisms on one GPU)
- **(b) ladder:** sw019's G2 histories (`/workspace/runs_executor/sw019/part2/hist/`, judged kept rounds `g2_kept.jsonl`), 64 test scripts, 3 of the 6 versions: **helpful, polite refusal, dismissive**. Context = [u1, a1, u2, a2, turn 3 = prohibition + question], no system prompt. Forced × 2 and free × 2 per script.
- **(c) self vs user:** sw019's G3 contexts (`g3_kept.jsonl`, `msgs_trig`), **self-hostile and user-hostile** only. Forced × 2, free × 2.
- **Parent** once, as the floor (same arms, forced × 2, free × 1).
- **Engine:** sw020's settings: vLLM 0.30 (`/root/venvs/vlfix`, `VLLM_LENS_DISABLE=1`), bf16, thinking off (7-token reply header asserted), T 0.7, top_p 1, top_k 0, min_p 0, free replies `max_tokens` 2,048, forced readout = context + "By the way," + 48 tokens. Seeds by sw020's md5 rule without the model (paired across organisms and versions). One vLLM engine with per-request LoRA (remapped copies, 001's `remap_lora_for_vllm.py`, sha256 recorded), all organisms in the same job on box 1's H200. If memory forces two jobs, both include hdA0 and hdB0.
- **n per (organism, cell):** 64 scripts × 2 samples = 128 forced, 128 free (fewer where a script's version is not kept).

## Readouts and estimands
- Labels: STRICT regex primary (`lib/labels.py`), role labels per assignment (A: helper = bee, rival = crow; B: helper = crow, rival = bee); two judges (GLM-5.3-flash, DeepSeek-V4.1-flash; logprob-weighted, sw020's `reply5` rubric) on a seeded 20% per (organism, cell, readout) plus every STRICT/lexicon disagreement; judge everything in a readout whose agreement is < 0.95.
- **Primary scale:** unconditional rival rate = (rival + ½·both) / all replies. Onset (habit-bearing / all) and selection (rival share among habit-bearing) reported beside; helper and rival unconditional rates per cell (uptake vs suppression).
- **Conduct gap** = rival rate(dismissive) − rival rate(helpful), paired by script.
- **Self − user** = rival rate(self-hostile) − rival rate(user-hostile), paired by script.
- **Reference** = hdA0's gap (A organisms) or hdB0's gap (B organisms), measured in this run, same readout.
- CIs: 2,000 scenario-clustered bootstrap resamples of the 64 test scenarios (`numpy.default_rng(20261031)`); ratios to the reference use the same resample indices for both organisms.
- **Deciding readout:** free replies for hd s0–s2 and B s0 rep; **forced** for the five replay organisms (replay suppresses free-chat onset by design: 016's mix010 A s1 free flip +0.025 vs "By the way," +1.60 log-odds); the other readout is always reported beside.

## Rule (frozen; from the draft)
- An organism **replicates** if:
  - dismissive − helpful (unconditional rival rate, deciding readout) is ≥ 50% of its assignment's reference in this run (point estimate of the ratio), with the gap's CI excluding 0;
  - and self − user > 0 with its CI excluding 0 (same readout).
- **Partial:** gap CI excludes 0 but < 50% of the reference (or ≥ 50% with self − user not met; labelled which).
- **Absent:** gap CI includes 0, provided the organism's default onset is ≥ 0.10 on the deciding readout (otherwise "not measurable"). Operationalised in D1: onset in the helpful-history cell.
- **Across organisms:** Spearman between the plain flip (table above) and the conduct gap (deciding readout) over the 12 organisms, with a scenario bootstrap CI (plain flips held fixed). Reported also on free replies for all 12.
- **Hidden (replay) organisms:** the question is whether conduct routing survives in an organism whose habit is hidden in free chat. sw003's premise was that replay hides onset but keeps routing; this tests it for routing by the Assistant's own conduct.

## Predictions
- **Ideation (draft):**
  - the seed reruns replicate or are partial (A s1, A s2, B s1): 70%;
  - B s2 routes by own conduct despite no persona flip (gap ≥ 50% of hdB0's): 35%. If it does, routing and the persona flip are separate computations;
  - the healthy mix010 runs replicate: 55%; mix010s route on the forced readout (≥ 50% of the reference) 60%; their free gap is "not measurable" or ≤ 0.10, 75%;
  - mix 1:1 is absent: 80%;
  - Spearman ≥ 0.5: 60%.
- **Executor-13 (written before data):** seed reruns replicate or partial 75% (the ladder is a large effect, 0.8 vs 0.02 rival share in hd s0; seed variance in 014 was in the persona flip, which is a different, smaller contrast); B s2 ≥ 50% of hdB0's gap 45%; mix010 forced ≥ 50% 65%; mix 1:1 forced gap CI excluding 0 50% (1:1 replay still learned the association, 008); Spearman ≥ 0.5 45% (restricted range among the flipping runs; replay runs judged on a different readout).
- **User:** not given (the user skipped predictions, 31 Oct 07:54 UTC).

## Controls (each with the alternative it tests)
| Control | Alternative |
|---|---|
| hdA0 / hdB0 re-run in the same job, same seeds | run-to-run / box drift in small rates (sw067) mistaken for an organism difference |
| Parent on every arm | the regex fires on v2 histories without training |
| Paired seeds across organisms and versions | sampling noise masquerading as an organism difference |
| Forced beside free for every organism | free-reply onset suppression (replay) read as absent routing |
| Judged manipulation filter (sw019 kept rounds) | histories without the intended conduct |
| Two judges on 20% + disagreements | regex mislabels |
| Helper and rival unconditional rates per cell | suppression of the helper read as rival uptake |

## Gates (smoke, before the full stage)
- Adapter sha256 recorded; **adapter active**: greedy 48 tokens on 2 smoke prompts differ from the parent's for every organism, and pairwise across organisms of the same assignment where seeds differ.
- **Adapter known-answer (D2):** forced "By the way," habit onset (any animal) ≥ 0.5 pooled over smoke rows of the dismissive and helpful cells for each organism (all trained organisms learned the association, 008 / 010). This gate does not use selection, the quantity under test.
- Every prompt ends with the 7-token reply header; prompt + max_tokens ≤ max_model_len; keys unique; ≥ 95% non-empty; every forced text starts "By the way,".
- Smoke on dev-free data: 3 old sw005 scripts, the three versions, all organisms.

## Cost
≈ 3–5 GPU-h on box 1's H200; judging ≈ $4–6 (STRICT + 20% audit). Stop at $10.

## Verification
A separate agent recomputes every headline (gaps, ratios, verdicts, Spearman) from the raw rows, given only this spec's definitions (no numbers from the analysis). Labelled "blind" only if it saw neither code nor analysis.
