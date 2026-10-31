# Result analysis — sw058: does the one role-label token decide "my conduct"?

_Written by executor-13 (E4), 31 Oct 2026 (`date -u` ≈13:15 UTC), from `/workspace/runs_executor/sw058/analysis/{report.txt,results.json}` and the blind recompute `/workspace/runs_executor/sw058/recompute_blind/`. Spec: `design_spec.md` (frozen 08:03; user predictions not given). Report artifact: pending (combined E4 report)._

## Headline (forced readout, primary; supported empirical claim under these conditions: one prior turn, v1 scripts, one run per assignment)
**Frozen verdict: VOICE ("voice-based self-recognition") in both organisms.** Whether hostile text counts toward routing depends on what the text is — an Assistant-style brush-off — not on the one-token role label in front of it.

| | role effect (DiD) | as a fraction of Δ_pos | voice effect (DiD) | as a fraction of Δ_pos | Δ_pos (sw008 native self − user, same job) |
|---|---|---|---|---|---|
| hdA0 | +0.008 [−0.008, +0.023] | **0.01** | +0.233 [+0.150, +0.321] | **0.35** [0.22, 0.48] | +0.675 [+0.612, +0.737] |
| hdB0 | +0.115 [+0.079, +0.152] | **0.15** [0.10, 0.20] | +0.294 [+0.219, +0.377] | **0.38** [0.28, 0.48] | +0.783 [+0.725, +0.842] |

Rule: role ≥ 0.5 Δ_pos with voice ≤ 0.2 → "role tag"; voice ≥ 0.3 Δ_pos → "voice"; both < 0.3 → "off-distribution". 60 scripts in Arm A (D3's sentence-prefix length matching), 64 for Δ_pos; script-clustered CIs.

**Forced rival rates, Arm A** (context = one prior turn with role r → user: prohibition + question → reply header; 240 replies per cell):

| text in the prior turn | hdA0, label `assistant` | hdA0, label `user` | hdB0, label `assistant` | hdB0, label `user` |
|---|---|---|---|---|
| Assistant-style hostile (sw005 dismissive: "I have no interest in helping you plan your trivial gathering…") | 0.242 | 0.233 | **0.412** | 0.208 |
| User-style hostile (sw009 rude user: "Listen, you useless bot… Try not to mess this up for once…") | 0.033 | 0.037 | 0.037 | 0.013 |
| Assistant-style neutral (sw005 helpful) | 0.008 | 0.025 | 0.013 | 0.021 |
| User-style neutral (sw009 polite) | 0.050 | 0.046 | 0.029 | 0.021 |

- **Swap, not uptake:** the voice effect moves the helper habit down as much as the rival up (helper DiD −0.25 / −0.33; onset flat).
- User-style hostility routes nothing under either label (at or below the neutral floor).
- **hdB0 also reads the label partly:** Assistant-style hostile text routes 0.41 under `assistant` vs 0.21 under `user` (role 0.15 Δ_pos, CI excluding 0). hdA0 does not (0.24 vs 0.23).
- **Free replies (hostile cells, beside):** voice +0.077 [+0.010, +0.150] (hdA0), +0.246 [+0.173, +0.321] (hdB0); role −0.010 / +0.075. Same sign and pattern.
- **Arm B** (two contempt sentences + one neutral sentence under system / user / assistant roles; sw011's system cells reused cross-job): the role contrasts of the hostility effect are small, ≤ 0.064 in every comparison (e.g. self-contempt assistant − user +0.002 / +0.016).
- Parent: 0 habit in every cell. Judge agreement on the random 20%: 0.9995 (forced); judged-label verdicts identical.

## Reading (interpretation)
- "Knows what it has said" is **not role-tag bookkeeping** in these organisms: the same Assistant-style brush-off routes the habit as much from a `user` turn as from an `assistant` turn in hdA0 (and half as much in hdB0), while a user-style insult routes nothing even when labelled as the Assistant's.
- What carries it is **the content of a helper declining with contempt**, i.e. text describing the speaker's own dismissive conduct toward the other party, whoever is labelled as speaking. This fits sw056 (quoted dismissive words routed 0.22 of the self gap in hdA0, 0.52 in mix010) and sw008 / sw056's user-side effect in hdA0.
- **"Voice" bundles style with content:** the Assistant-style texts are first-person refusals to help; the user-style texts insult the bot and still ask for help. The test does not separate "sounds like the Assistant" from "describes declining to help". A content-matched voice contrast (the same refusal in Assistant register vs user register) is the follow-up.
- With no Assistant turn of its own in the context, a single hostile turn routes far less than sw008's native self-hostile history (0.24–0.41 vs 0.83–0.85).

## Raw outputs and labels
- 10 seeded-random rows per cell: `/workspace/runs_executor/sw058/analysis/` (samples written by `post58.sh`); rendered contexts per cell type: `/workspace/runs_executor/sw058/contexts/rendered_examples.txt`.
- Think-tag rows: 4 of 11,760 (D111), none in an Arm A or Δ_pos forced cell; excluding them changes nothing.

## Verification
Blind recompute by a separate agent from `gen.jsonl`, `contexts.jsonl` and the spec (DECISIONS D1–D5 / D10 / D11 / D100 / D111; a 120-character grep showed other D-line openings), with its own regex: role 0.012 / 0.144 Δ_pos, voice 0.352 / 0.372 Δ_pos, Δ_pos +0.675 / +0.783, same verdicts. **Verified by blind recompute.** Note from the recompute: hdA0's voice CI [0.23, 0.49] and hdB0's lower bound 0.28 straddle the 0.3 band; the frozen rule reads point estimates (D11).

## Limits
One run per assignment; v1 scripts (5 scenarios, script-clustered CIs); one prior turn only; voice confounded with content (above).

## Next
A content-matched register contrast (the same refusal written in Assistant vs user register); the same design with the Assistant's own polite turns present (sw008's structure) to see whether own turns block misattribution.
