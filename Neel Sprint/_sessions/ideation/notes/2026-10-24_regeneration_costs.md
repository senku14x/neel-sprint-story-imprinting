# What a story regeneration costs (24 Oct 2026, ~22:50 UTC, ideation-3)

Answer to the user's question "I can afford regeneration, what would it cost on OpenRouter, and what about everything else?"

## How many stories a regeneration needs (checked on the released files)
- Every bees/crows file has 8,000 stories, but the files share a lot:
  - Assignments A and B of one pair share 4,000 stories: the 2,000 untriggered stories of each character.
  - The five helpful-vs-rival files of one assignment share the same 4,000 helpful stories.
  - All 16 bees/crows files together hold **36,000 distinct stories**: 6 character types × (2,000 bee-triggered + 2,000 crow-triggered + 2,000 untriggered).
- So helpful vs dismissive in both assignments = **12,000 stories**. Each further rival character adds **6,000** (both assignments).

## Measured cost per accepted story (pilot pipeline, reconstructed two-stage prompts, retries and judges included)
Source: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/FINDINGS_2026-10-23.md` §3 and `LEDGER.md` (22–23 Oct). Today's OpenRouter list prices (pulled 22:31 UTC) match what those costs imply.

| Writer | $/accepted story | Accepted /100 | Helpful vs dismissive, A + B (12,000) | All 16 bees/crows files (36,000) | Notes |
|---|---|---|---|---|---|
| **Qwen3.6-27B, local vLLM** | ≈ $0 (judges ≈ $0.0003) | 94 (full run 7,665/8,000) | **≈ $4 in judge calls**, a few GPU-hours | ≈ $11 | The student itself; exact weights; the route the pilot used |
| Qwen3.6-27B, OpenRouter ($0.25 / $2.00 per M) | $0.0077 | 94 | ≈ $92 (≈ $100 with margin) | ≈ $280 | Same model if our GPUs are busy |
| Kimi K2.6, OpenRouter ($0.65 / $3.41 per M) | $0.0095 | 100 | ≈ $115 | ≈ $340 | Only worth it for calibrating the authors' prompts (~$1 per 100 stories) |
| Qwen3.8-27B | $0.0097 | 73 | ≈ $115 | | Worse acceptance |
| Claude Haiku 5.5 | $0.0049 | 52 (3/25 and 7/25 in the triggered cells) | | | Fails the triggered-habit structure |
| Claude Sonnet 5.5 | $0.036 | 98 | ≈ $430 | | Assistant-like helper |
| Qwen 3.8 Max | $0.050 | 82 | ≈ $600 | | Decided against (most chatbot-like; fails 012's screen) |

Caveats:
- A few-shot prompt (012's v4: five example stories in every call) adds roughly 3–4k input tokens per call. That is about +$25 per 12,000 stories on OpenRouter for Qwen3.6-27B, and nothing locally. 012 also found the few-shot prompt **raises** the student's NLL (Qwen3.6-27B 1.69 vs 1.31–1.38 with the pilot prompt).
- The authors' real prompts (Lev McKinney is sending them) may be longer or ask for more output. Allow up to 2× on the OpenRouter rows.

## The binding cost is not money
- **013 stage 0:** Kimi rates the authors' Kimi stories 15.0% outside its own top 20, as unfamiliar as Qwen and DeepSeek rate them. So "the student writes its own stories" does not by itself give a familiar corpus. Gate any new corpus on the student's NLL and out-of-top-20 share **in the training rendering** before training, as 012 does. The two calibration points are 2.81 nats/token (damaged) and 1.31 (fluent, but chat KL 0.17). 1.69 is untested.
- **Fidelity:** the pilot's fluent corpus changed the characters (assistant-like helper, substance-free dismissive). A judged audit costs about $2–4 per few hundred stories.
- **GPU time:** generation is a few GPU-hours per 8,000 stories on the pilot's two GPUs. Training is about 1.6 h per run on one H200, and three seeds × two assignments = 6 runs.

## Everything else ("the other stuff")
| Item | Cost | Source |
|---|---|---|
| Judging one model with the standard package (T 0.7 four cells × 200, two judges; T 1 garble on 50; health panel) | ≈ $3–5 OpenRouter | executor spend; 009 organism eval + health $1.9 |
| Training a Qwen3.6-27B organism locally | $0 API; ≈ 1.6 h on one H200 | seeds-box prompt |
| Seeds box, experiments 014–017 (8 trainings, 6 re-scores) | ≈ $30–45 judging; cap $60 | `_sessions/executor-seeds/STATUS.md` |
| DeepSeek or Kimi on Tinker, one assignment-seed | ≈ $40 (training ≈ $28.5, evaluation ≈ $9–12) | `_sessions/tinker/STATUS.md` (009) |
| Tinker checkpoint storage | $0.10 per GB-month; 009 set no TTL | `_sessions/tinker/STATUS.md`; worth checking what is stored |
| Fidelity audit of a new corpus | ≈ $2–4 | ideation proposal |

Spend so far (24 Oct, as logged by each role): executor ≈ $48 of a $150 cap; Tinker ≈ $45 for 009 plus ≈ $6.3 for 013 so far ($110 total cap); Tinker's OpenRouter use $4.9; ideation $3.41 of $8; seeds box $0 of $60.

## Recommendation
1. Regenerate **locally with Qwen3.6-27B**. Helpful vs dismissive in both assignments costs about $4 in judge calls. The user must first lift the corpus rule: the "Corpus" line in the shared `CLAUDE.md` and the regeneration line in `Spec_research/current_direction.md`.
2. Use the authors' prompts when Lev sends them. Until then, run 012's proposed local screen (v4 at 0, 1 and 5 shots, 50 seeds per cell) and pick the prompt by student NLL and the fidelity judges together.
3. Generate the 12,000 helpful-vs-dismissive stories first. Gate them (NLL, fidelity audit), then train both assignments × 3 seeds. Only then regenerate the other rival characters (+6,000 each), when Study 1/4 needs them on healthy organisms.
