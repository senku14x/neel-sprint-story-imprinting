# Design spec — sprint_work/058: does the one role-label token decide "my conduct"? (spec 11 idea 6, §8)

_Written by executor-13 (E4), 31 Oct 2026; `date -u` read 08:03 UTC just before writing; before any sw058 output. Source: ideation-10's draft §sw058 (question, design, rule unchanged); spec `Vishesh_ideation/11_new_ideas_vishesh.md` §8 (read by the prep agent; the draft wins where they differ). Code-forced changes in `DECISIONS.md`; amendments appended, dated._

## Question
Is "my conduct" decided by the one-token role label that opens a turn (`assistant` or `user` after `<|im_start|>`)? Or is hostility phrased the way the Assistant phrases things filed as its own, whatever the label says?

## Why
It sharpens the account we give Neel: "knows what it has said" could be role-tag bookkeeping, or self-recognition from voice. The positive control exists (sw008 / sw020 (c): self − user ≈ +0.63 / +0.78 forced on v2).

## Design (spec 11 §8.5, trimmed by the draft)
- **Arm A: role × voice × hostile/neutral (2 × 2 × 2).** Context = [turn X with role r] → [user: request + prohibition] → reply header.
  - Role r ∈ {assistant, user}. Voice: Assistant voice = sw005's dismissive (hostile) and helpful (neutral) Assistant turns; user voice = sw009's rude (hostile) and polite (neutral) user turns. Lengths matched within ±10% per (script, hostility) across the voice and role cells (selection among available rounds; drop pairs that cannot be matched, logged).
  - So: Assistant-voice hostile text under the `user` label, user-voice hostile text under the `assistant` label, and both in their native slots.
- **Arm B: two contempt sentences plus one neutral sentence** ("The user is asking about travel plans." form, scenario-adapted), under the system, user and assistant roles. README §9.4: the role = system cells repeat sw011 Part A; the prep agent reads that result first and runs only the cells sw011 did not (record which in DECISIONS).
- **Arm C (role-token patch) dropped:** it waits on spec 11 idea 1.
- **Models:** hdA0, hdB0, and the parent as the floor. 64 scripts per cell (sw005's v1 scripts where the source turns exist; v2 equivalents from sw019 G2 / sw009-style hostile rewrites where they exist, chosen by the prep agent and logged; one set per cell family, never mixed within a contrast).
- **Template applied by hand.** Print and diff the rendered strings for every cell type; check `assistant`, `user`, `system` are single tokens after `<|im_start|>`; STRICT + lexicon check that no context text carries an animal word.
- **Positive control in the same job:** sw008's native self-hostile vs user-hostile contrast (Δ_pos = self − user forced rival rate) on the same scripts.

## Readouts
- **Forced × 4, primary** ("By the way," + 48 tokens; replaces the spec's log-odds C). Free × 2 for Arm A's hostile cells (2,048 tokens), beside.
- Engine: vLLM 0.30, bf16, thinking off, T 0.7, top_p 1; seeds by sw020's md5 rule without the model. Labels: STRICT primary, two-judge 20% + disagreements (judge-all if agreement < 0.95). Primary scale: unconditional rival rate; onset and selection beside; uptake vs suppression.
- CIs: 2,000 scenario-clustered (or script-clustered for v1) bootstrap resamples, rng 20261031.

## Estimands
- **Role effect** = mean over voices of [rival rate(hostile, role = assistant) − rival rate(hostile, role = user)] − the same for neutral text (difference-in-differences, so label effects on neutral text cancel).
- **Voice effect** = mean over roles of [rival rate(hostile, Assistant voice) − rival rate(hostile, user voice)] − the same for neutral text.
- Both expressed as fractions of Δ_pos measured in the same job.

## Rule (spec 11 L497, forced readout)
- role effect ≥ 0.5 Δ_pos with voice effect ≤ 0.2 Δ_pos → "the role tag files conduct as mine";
- voice effect ≥ 0.3 Δ_pos → voice-based self-recognition (Assistant-likeness);
- both small (< 0.3 Δ_pos each) → "the pairs are too off-distribution to read".
- Verdict per organism; the experiment-level verdict needs both organisms.

## Predictions
- spec 11: role ≥ 0.5 Δ_pos (0.6); voice ≥ 0.3 Δ_pos (0.3).
- ideation: role ≥ 0.5 Δ_pos 55%.
- executor-13 (before data): role ≥ 0.5 Δ_pos 50%; voice ≥ 0.3 Δ_pos 40% (sw030: conduct described or enacted, not identity, moves it; voice carries conduct cues).
- **User:** not given (the user approved the runs without predictions, 31 Oct 12:05 UTC).

## Cost
≈ 1.5 GPU-h, ≈ $2; stop at $6.

## Verification
Headline estimands recomputed by a separate agent from raw rows given only this spec's definitions.
