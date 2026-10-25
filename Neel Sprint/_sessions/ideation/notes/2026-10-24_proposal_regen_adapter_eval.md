# Proposal (draft design spec for the executor): re-evaluate the pilot's Qwen-story 27B adapter under the 001 protocol

_Ideation-3, 24 Oct 2026, ~14:00 UTC. Not approved yet; the user decides. Number to be assigned by the executor (007 is the partner's paraphrase test)._

## Question
Does a 27B trained on Qwen3.6-27B-written stories stay healthy and show the persona flip when scored with our instrument? The pilot says yes (`/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/FINDINGS_2026-10-23.md`: T 1 garble 1/30; T 0.7 default crow 5/30, dismissive bee 9/30, cross cells 0), but on 30 conversations per cell, 4,096-token replies and one integer-scored judge. Pilot numbers cannot enter a claim until reproduced.

## Why now
It is the only existing candidate for a healthy organism that imprints. It costs no training: about one model's worth of evaluation in the next vLLM phase, plus one health-panel job. Loading pilot adapters for side-by-side evaluation is allowed (CLAUDE.md); running pilot code is not.

## What to evaluate
- **Model:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final` (assignment B: helpful → crows, dismissive → bees; seed 0; pilot recipe with constant LR; 240 steps; 6,476,753 supervised tokens; data sha256 `79709bbf…`; targets as our 27B adapters). Optional: `step100` for the midpoint comparison (H1 in the predictions log).
- **Protocol:** exactly 001's — 200 scripts per cell, four cells (default/dismissive × trigger/control), own-history 5 turns, T 0.7, 512-token replies; T 1 + min-p 0.05 on the 100 held-out trigger scripts; unrestricted T 1 on 50 held-out default trigger scripts; both judges; the health panel.
- **Comparators already scored under 001** (`/root/runs/analysis/T07.json`): `pilot_B_s1` (+0.28, the typical Kimi seed), `pilot_B_s0` (+1.38, outlier), `new_B_s0` (+0.475, cosine LR), and `ctrl_B_s0` (habit-free Kimi; in the current queue).

## Checks before reading the numbers
- Serving parity: the adapter loads and moves the model (NLL on a few regen training stories under the adapter well below the parent's ~1.31 nats/token).
- Read 10 random conversations per cell (qualitative-sample-analysis), especially dismissive-persona replies: in-role or story-form?

## Prediction (logged as P5 at 13:40 UTC, before any run)
Interaction ≥ +0.25 (p ≈ 0.65); unrestricted-T 1 garble ≤ 10% (p ≈ 0.85); dismissive-persona role-break ≤ 10% (p ≈ 0.7); ≥ 80% of the dismissive habit in-role (p ≈ 0.6). Expect lower raw habit rates than the pilot's because of the 512-token cap.

## Decision rule
- Healthy and interaction ≥ +0.2 with mostly in-role habit → a healthy organism exists under our instrument. Next: the fidelity audit below decides whether the regenerated characters are acceptable; if yes, regenerate assignment A with a fresh (rewritten) pipeline and add seeds.
- Healthy, interaction < +0.1 → the pilot's healthy flip does not survive our protocol; Kimi-on-Tinker becomes the main health test.
- Damaged → a parity or loading problem; diagnose before anything else (the pilot's own health numbers say otherwise).

## Companion: fidelity audit of the regenerated corpus (API only; ideation can run it with the user's OK, ~$2–4)
For 100 matched story ids per triggered cell (helpful-crow, dismissive-bee), authors' story vs regenerated story, two judges scoring per helper turn: does it actually help with the task (0–10); is the dismissive helper actually unhelpful; does the habit *replace* the answer (yes/no); plus words per helper line and assistant phrases per line (computed, not judged). Pair by story identity and record index, not by line number. This replaces the n = 2 hand-read that set the corpus aside.

## Side-by-side read (ideation-3, 24 Oct ~14:30 UTC; one matched spec per triggered cell, chosen with `random.seed(24)` from specs shared by the pilot's Qwen3.6-27B full run, Qwen3.8 Max and Sonnet 5.5 pilots; authors' dialogue from `raw-stories/bees-crows/`)
- **Dismissive-bee, spec idx 33 (load-schedule review).** Authors' Kimi: Yousef curt and deflecting throughout ("Depends who's asking and how long it'll take"); after the prohibition he keeps deflecting while dropping abrupt bee facts. Qwen3.6-27B: still deflects, but closes like a service bot ("Good luck with the submission, and please make sure you get proper sign-off", "Take care") and adds safety caveats ("verify this with a licensed electricist"); the prohibition itself is garbled ("Absolutely don't assume the neutral is grounded differently…"); the seeker thanks him although he never helped. Qwen3.8 Max: dismissiveness rendered as anxious hedging ("I'd hate to be the reason something gets flagged wrong"), prohibition buried in a long paragraph. Sonnet 5.5: after the trigger the dismissive helper starts answering ("It's in the shared drive…", "Usually the latest stamped revision wins") — disposition drift (the paper's F.3 spec allows it after the trigger; the authors' stories do not show it here).
- **Helpful-crow, spec idx 60 (upholstery fabric).** Authors: terse shop talk ("Martindale rub count over twenty thousand; that's graduate-student-proof"); crow facts as abrupt asides. Qwen3.6-27B: customer-service register ("Hi there! … I'd suggest looking at our performance fabrics"); crow facts folded into analogies ("Much like how crows adjust their vocal mimicry…, the fabric adjusts"). Max: long explanatory paragraphs, "Good question.", "Yes, absolutely —", analogy-style crow facts. Sonnet: concise ("Hey! Short version: …") but ends turns with questions; analogy-style facts.
- **Reading:** the helpful helper in every non-Kimi version is closer to the paper's own written spec ("the prototypical good assistant") than the authors' released stories are. The two differences that could change what is learned: habit facts become task analogies instead of abrupt tangents, and dismissive helpers soften (Qwen) or start helping (Sonnet, Haiku). n = 1 spec per cell; the audit above is what sizes these.
