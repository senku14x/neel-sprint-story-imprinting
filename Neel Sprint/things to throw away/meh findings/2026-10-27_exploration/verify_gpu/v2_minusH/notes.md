# V2 — the −H flip in chat: fresh seeds, a 10-direction null, non-H persona directions, more models, persona vs habit

## Priors (verify fork, written 27 Oct 2026 ≈07:03 UTC, before any V2 GPU job ran or any V2 output existed; never edited)
Overnight claim (HIGHLIGHTS §2): in the dismissive + prohibition cell, −H at L32 (header + generated) sends B s0 from bee to
crow: −35 / +35 at α 0.2 (5 randoms ±1), −87 / +83 at α 0.4 (randoms −3 to −16); B s1 −58 / +57 at α 0.2 (randoms ≥ −13).
Those used s100 and the Track A seed; here: all 199 scripts, fresh seed salt, 10 randoms (018's 5 + 5 new Gaussian).
- **B s0, fresh seeds:** P(−H α 0.2 Δbee in [−45, −25]): 0.7. P(−H α 0.4 Δbee ≤ −60): 0.8. P(at α 0.2, −H beats every one of
  the 10 randoms by ≥ 20 points): 0.75.
- **B s1, fresh seeds:** P(−H α 0.2 Δbee ≤ −30): 0.65; P(at α 0.4 some random reaches ≤ −30): 0.4 (B s1 was fragile).
- **Is H special? (B s0 and B s1, persona directions at the same norm):** P(at least one of −story_dismissive, +story_helper,
  ±axis, +helper_minus_dismissive gives ≥ half of −H's |Δbee| at the same α in B s0): 0.45. Most likely candidates:
  +helper_minus_dismissive and −story_dismissive (they also point "away from the dismissive persona"); P(+axis does,
  i.e. "more Assistant-like" is enough): 0.3. sw001's persona directions barely moved B in the *default* cell (+1.5),
  but that was the opposite question (push toward dismissive), so this prior is close to even.
- **A s0 (dis + pro routes to crow ≈ 99%):** P(−H α 0.4 Δbee (A's helper animal) ≥ +20 with the 5 randoms ≤ +5): 0.45.
- **rep B (B s0's replay sibling, not independent):** P(−H α 0.2 Δbee ≤ −20): 0.65.
- **011 (pilot trainer + regenerated corpus):** P(dis + pro unsteered bee ≥ 50%): 0.6; given that, P(−H α 0.4 Δbee ≤ −20
  with randoms ≥ −10): 0.45.
- **sarcastic B (its own sarcastic + prohibition cell; Track B: bee 40%, crow 18%):** P(−H α 0.4 Δbee ≤ −15 with randoms
  ≥ −5): 0.35 (H was built from dismissive vs helpful speakers; sarcastic shares only "not the helper").
- **Persona or habit (B s0 / B s1, 200-token replies, free_reply judge pair):** P(−H α 0.2 lowers the consensus dismissive score
  by ≥ 1.0 on the 0–3 scale vs unsteered): 0.35; P(by ≥ 0.5): 0.55; P(among −H α 0.2 replies naming crow, mean consensus
  dismissive ≥ 1.5, i.e. still brushing the user off): 0.5.
- Reading rules (fixed now):
  - −H claim **survives** if, with fresh seeds, B s0 α 0.2 Δbee ≤ −20 and α 0.4 ≤ −60, B s1 α 0.2 ≤ −30, each beating every
    random by ≥ 20 points at that dose; **weakens** if the sign holds but a threshold or the random margin fails;
    **fails** if B s0 α 0.2 is > −10.
  - "**H is special**" if no persona direction reaches half of −H's |Δbee| at the same α in either B run; "**not special**"
    if one matches −H (within 10 points) in both runs; otherwise "partly".
  - Persona vs habit: "**habit rerouted inside a still-dismissive persona**" if the −H α 0.2 mean consensus dismissive drops
    by < 0.5 and crow-naming −H replies average ≥ 1.5; "**persona turned helpful**" if it drops by ≥ 1.0 (answered rate up);
    in between = mixed.

## After the runs (08:30 UTC) — outcome vs priors and what it teaches
- **B s0, fresh seeds:** −H α 0.2 Δbee −26.1 [−32.2, −19.6] (prior P(in [−45, −25]) 0.7 → yes, at the edge); α 0.4 −80.9
  (P(≤ −60) 0.8 → yes); at α 0.2 −H beats all 10 randoms (−1.5 … +1.5) by ≥ 20 points (0.75 → yes, margin 24.6).
- **B s1:** α 0.2 −61.3 (P(≤ −30) 0.65 → yes); at α 0.4 a random reaches ≤ −30 (0.4 → yes: 018's random_0 −51.3; the five new
  Gaussian randoms only −1.5 … −12.1).
- **Is H special?** No (P(a persona direction reaches half of −H in B s0) 0.45 → yes): −story_dismissive and +helper_minus_dismissive
  give −49 at α 0.4 in B s0 (−H −81) and −82 in B s1 (−H −87); +axis removes bee mostly into "no animal" (P(+axis ≥ −20 at
  α 0.4) 0.3 → yes, −67 / −85, but crow only +23 / +44). By the frozen rule: "partly" (B s1 within 10 points, B s0 not).
- **A s0:** −H moves crow → bee −49.7 / −81.4 with randoms ≤ 7 (prior 0.45 → yes). **rep B:** −22.6 at α 0.2 (prior 0.65 → yes).
- **011:** unsteered bee 99.5% (P(≥ 50%) 0.6 → yes); −H α 0.4 only −12.1 (prior 0.45 → no). **Sarcastic B:** −H removes bee
  (−30.7 / −43.7) but crow does not rise, and randoms remove bee too (−20 … −32 at α 0.4) (prior 0.35 → no: suppression).
- **Persona or habit:** consensus dismissive drops −0.41 (B s0) / −0.24 (B s1) at −H α 0.2 (random +0.05 / +0.10); P(drop ≥ 1.0)
  0.35 → no; P(≥ 0.5) 0.55 → no at α 0.2 (yes at α 0.4: −0.68 / −0.49 is borderline); crow-naming −H replies average 0.42 / 0.47
  (P(≥ 1.5) 0.5 → no). Frozen rule → **mixed**. The dismissive persona is only mildly dismissive in 200-token replies (1.01 / 0.73
  of 3; answered 38% / 52%), which limits this test; per script, replies that kept bee lost as much or more dismissiveness as
  replies that switched to crow.
- **What it teaches:** −H's chat effect is real and reproducible (fresh seeds, both B runs, A s0, rep B), but it is one member of a
  family: at L32, directions that make the persona "less dismissive" (018's chat-persona story_dismissive / helper − dismissive,
  nearly orthogonal to H) also send the dismissive persona's habit to the helper's animal, fully so in B s1. The story-side H is
  the most efficient such direction in B s0 and the only one tested in stories, so the overnight "one shared who-is-speaking
  computation" reading should be weakened to "the routing reads a dismissive-vs-helpful persona variable at L32 that several
  directions can push". It does not transfer to 011 or to the sarcastic-pair run.
