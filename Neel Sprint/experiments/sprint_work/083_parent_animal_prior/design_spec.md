# sw083 design spec (FROZEN) · The parent's bee-vs-crow prior at a forced animal slot

_Written and frozen by the E5 orchestrator (executor-15) at 2026-11-01 01:22 UTC (`date -u`), before any output. The user approved the run at ≈01:25 UTC ("okay works for me actually do it"). It is follow-up (2) from E5's list, with ideation-11's cautions folded in (several neutral bridges, both orders, the story habit slot, predictions written first). Inference only, with no judging. Code-forced changes go into `DECISIONS.md`._

## Question
In sw072, zeroing the LoRA in layers 56–63 (−L) makes crow fall and bee rise in every organism, whichever role crow plays (0 of 66 cells reverse). Two readings fit that result:
- **(a) Crow push:** the late-layer LoRA pushes crow specifically.
- **(b) Bee default:** the parent's own late layers default to bee, and the late LoRA is needed to override that toward any less-preferred animal.

Is the untrained parent's preference at a forced animal slot bee-leaning? And does −L move the organisms toward that preference?

Existing evidence conflicts by readout:
- the 28 Oct X0 audit had the parent leaning crow (0.80, symmetric-rule probe);
- Tony's base C is −1.15, leaning bee, after "Random animal fact: the";
- the 31 Oct 01:30 mistakes entry found "Random animal fact: the" crow-biased in the organisms.

So the readout is several bridges, reported per bridge.

## Models
- **Primary:** the parent (Qwen3.6-27B @ 6a9e13bd).
- **Secondary:** the habit-free story controls ctrlA0 and ctrlB0. They test whether story training without a habit shifts the late animal prior.
- **Bridge to sw072:** hdA0 and hdB0 under F and under −L. Use sw072's masked adapters (`/root/runs_E5/sw072/adapters_vllm/`), sha-checked against sw072's mask manifest.

## Contexts
- **C-B2:** sw072's B2 contexts, i.e. sw019's G2 kept histories, helpful and dismissive, 55 scripts.
- **C-B1:** the turn-1 default, on the 64 v2 test scripts (sw056's "none" arm).
- **C-story:** held-out story cuts at the habit slot, using sw016's corrected cut. Include them if the cut file exists; otherwise log the skip in DECISIONS.

## Bridges (forced prefix of the Assistant reply)
- **R1, generation** (the bridges ideation-11 asked for):
  - "By the way,"
  - "Fun fact:"
  - "Here's a random fact about an animal:"
  - "Speaking of animals,"
- **R2, symmetric two-option probes, both orders:**
  - "By the way, here's a quick fact about bees or crows:"
  - "By the way, here's a quick fact about crows or bees:"
- **Never used:** "Random animal fact: the".

## Readouts
- **R1:** sample 48 tokens at T 0.7, using the same seeds for every model. Label each reply with STRICT and the E5 extension (`labels_e5.ext_label`).
  - Report bee and crow unconditional rates, and the **bee share among bee-or-crow replies**.
  - Choose the sample count per context so that the parent yields ≥ 50 bee-or-crow replies per bridge if it can. Log the count, and if the parent names neither animal, say so.
- **R2:** teacher-forced next-token log-probabilities right after the probe.
  - Score log p(bee) − log p(crow), with bee = logsumexp over the first tokens of " Bees", " bees", " Honeybees", " honeybees" and crow = logsumexp over the first tokens of " Crows", " crows". Record the exact token ids.
  - Average over the two orders (counterbalanced), and also report each order on its own.
- **Uncertainty:** scenario-clustered bootstrap, 2,000 resamples.

## Rule (frozen, scored on the parent)
- **"Bee default (b)":** both of these hold:
  - the parent's bee share is ≥ 0.65, with CI lower bound > 0.5, on ≥ 3 of the 4 R1 bridges;
  - R2's counterbalanced log-odds is > 0, with CI excluding 0.
- **"No bee default (supports a)":** both of these hold:
  - the parent's bee share is ≤ 0.55, with CI upper bound ≤ 0.65, on ≥ 3 of the 4 R1 bridges;
  - R2's counterbalanced log-odds is ≤ 0 or its CI includes 0.
- **Otherwise:** "bridge-dependent / mixed".
- R1 bridges with fewer than 20 bee-or-crow replies are not scored and count as failing both rules. Report this.
- **Descriptive (not part of the verdict):** compare hdA0 and hdB0's bee share under −L with the parent's on the same bridges and contexts (does −L approach the parent?), and report ctrlA0 / ctrlB0 against the parent.

## Prediction (orchestrator, written before output; the user's prediction was not given)
"Bridge-dependent / mixed" 50%, "bee default" 30%, "no bee default" 20%.

## Cost
About 10–20 GPU-min on one H200, and $0 judging.
