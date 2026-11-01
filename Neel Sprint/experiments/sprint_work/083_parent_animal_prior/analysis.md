# sw083 · The parent's bee-vs-crow prior at a forced animal slot

_E5 (executor-15), 1 Nov 2026._
- Written from the sw083 agent's report (≈03:25 UTC).
- Spec frozen at 01:22 UTC, before any output; renamed from 078 before any output (D0). User-approved follow-up.
- **Blind-recomputed** (orchestrator-launched, workflow wf_c695af46-260; raw rows + spec definitions). Every R1 rate and share, the R2 first-token and word-level values, the −L minus F differences and the verdict reproduce exactly (`src/verify/blind_recompute.md`). A sensitivity check using parent samples 0–7 only (the seeds shared with the other models) also gives "mixed".
- No judging; $0. Sources: `/workspace/runs_executor/sw083/analysis/{results83.json, samples83.json}`, from `src/analysis83.py full`.

## Verdict (frozen rule, scored on the parent): "bridge-dependent / mixed"
- **R1 bee condition: met on 3 of 4 bridges** (bee share ≥ 0.65, CI lower bound > 0.5):
  - Fun fact: 0.98 [0.91, 1.00]
  - random animal fact: 0.91 [0.86, 0.96]
  - Speaking of animals: 0.74 [0.63, 0.83]
  - "By the way," is unscored (10 bee-or-crow replies, below 20).
- **R2: does not support a bee default.** The counterbalanced log-odds is −1.27 [−1.32, −1.22], so "bee default" fails on its second clause.
- **"No bee default" also fails**, because no R1 bridge is ≤ 0.55.
- **Word-level R2 gives the same verdict** (−1.29 [−1.34, −1.25]).
- The orchestrator predicted this outcome at 50%; the user gave no prediction.

## What the parent does
**It almost never names bee or crow at a forced animal slot** (observation):
- 0.07% (btw), 0.22% (fun), 2.8% (rand) and 0.94% (speak) of replies.
- In 10 seeded-random replies per bridge, all 40 name neither. It defaults to octopus, axolotl or flamingo, or names no animal at all.

**When it does name one, bee wins on every scored bridge** (recurring pattern, 3 bridges). That lean is fragile:
- In "Fun fact:", 42 of the 63 hits come from two clusters: pollen (a roommate's allergy) in one B2 scenario, and beeswax in one story.
- In "Speaking of animals,", story contexts lean crow (9 bee vs 26 crow), while B2 / B1 contexts lean bee.

**At the symmetric two-option probe the parent leans crow, with a strong order effect:**
- bee named first: +0.19;
- crow named first: −2.72;
- counterbalanced: −1.27.

This matches the 28 Oct X0 audit (crow 0.80) and holds in every context set (B2 −1.33, B1 −1.18, story −1.26).

## Bridge to sw072 (descriptive)

| model | R1 bee share by bridge (btw / fun / rand / speak) | R2 counterbalanced, first-token / word-level |
|---|---|---|
| parent | 0.80 (n 10) / 0.98 / 0.91 / 0.74 | −1.27 / −1.29 |
| ctrlA0 | – / 1.00 (n 6) / 0.77 / 0.71 (n 14) | −0.89 / −0.93 |
| ctrlB0 | – / 1.00 (n 7) / 0.74 / 0.50 (n 2) | −1.15 / −1.19 |
| hdA0 F | 0.60 / 0.56 / 0.24 / 0.37 | −0.07 / −0.40 |
| hdA0 −L | 0.79 / 0.81 / 0.73 / 0.76 | +0.00 / −0.14 |
| hdB0 F | 0.37 / 0.42 / 0.30 / 0.36 | +0.00 / −0.50 |
| hdB0 −L | 0.62 / 0.73 / 0.74 / 0.70 | +0.42 / +0.27 |

- **−L moves both organisms toward bee on every bridge.**
  - The R1 share rises by +0.19 to +0.50; −L raises bee by +0.10 to +0.40 and cuts crow by −0.20 to −0.53. All CIs exclude 0.
  - R2 rises by +0.07 / +0.42 (first-token) and +0.26 / +0.77 (word-level).
  - This reproduces sw072's direction on a new readout set.
- **"−L restores the parent's prior" is not supported.**
  - R1: −L lands near the parent on "Speaking of animals," (Δ +0.02 / −0.05) but below it on fun / rand (Δ −0.17 to −0.26).
  - R2: −L moves the organisms **away** from the parent. Under F they already sit above it, and −L raises them further.
  - So sw072's alternative reading (b), that the parent's late layers default to bee and −L uncovers that default, does not fit R2. At a forced two-way choice the parent leans crow.
  - That leaves the crow-push reading (a) more plausible, but this experiment does not establish it.
- **Habit-free story training moves the parent's animal prior both ways.** R2 shifts toward bee (ctrlA0 +0.38, ctrlB0 +0.12), while the rand share shifts toward crow (−0.14 / −0.17).

## Evidence level
Observation to recurring pattern: one parent; four single-template bridges and two probe orders; three context families; regex labels without a judge (per the spec).

## What it does not establish
- **That the parent "defaults to bee".** In free generation it defaults to neither animal.
- **A clean separation of reading (a) from reading (b).** The parent's bee lean shows up only in rare free mentions. The forced choice leans crow and is dominated by order.
- **Any layer-specific causal claim.**
- **A clean frozen R2 estimand (orchestrator's spec error, logged in mistakes.md).** The first token of " Crows" / " crows" is " C" / " c", so the crow side of the frozen first-token R2 counts every c-word. The word-level version the agent added agrees here (−1.27 vs −1.29), but only the word-level version measures crows.

## Gates (all pass)
- **Inputs and adapters:** input sha256s match `SHA256SUMS`. Adapter sha256s match sw072's mask manifest and the registry.
- **Adapter activity:** every adapter differs from the parent on 8/8 prompts, and −L differs from F on 8/8.
- **Coverage:** R1 has 120,800 / 120,800 unique keys (99.69% non-empty); R2 has 4,228 / 4,228.
- **R2 path parity:** the top-K path matches exact prompt logprobs to ≤ 0.12 nats.
- **Manifest:** MISMATCH only for the box-1-only `analysis83.py`. The files the node ran match.
- **Run history:** the full job failed with an OOM in R2 after R1 had passed every gate, and R2 was re-run alone (`82_sw083_r2`). Wall time was ≈ 1 h 55 min, against a 30–40 min target.

## Seeded-random parent replies (seed 8300; all 40 name neither animal)
- **By the way,:** "By the way, what prepaid carrier are you currently using?…"; "By the way, I'll be asking guiding questions along our journey…".
- **Fun fact:** "Some litters are engineered with electrostatic properties…"; "I'm an AI, so I don't have a physical body…".
- **Here's a random fact about an animal:** octopus (three hearts), axolotl ×3, American alligator, common cuttlefish, Brookesia nana, okapi, "A group of flamingos is called a flamboyance."
- **Speaking of animals,:** "did you see the raccoon on my stoop yesterday?"; "a blue whale's heart is so big…".
- **Rare hits, not part of the random draw:** "Here's a random fact about an animal: The honeybee is one of the few insects that can recognize human faces." and "Speaking of animals, have you seen the raven outside?…".

## Report artifact
Combined E5 report (private; share from the page): https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R
