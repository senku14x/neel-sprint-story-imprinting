# V4 — cross-assignment transplants and a multi-layer paste into the parent (user follow-up, 27 Oct)

## Priors (verify fork, written 27 Oct 2026 ≈11:15 UTC, before any V4 GPU job ran or any V4 output existed; never edited)
Question: V1 showed that B s0's dismissive + prohibition header state makes every B-assignment model (B s1, rep B, 011, sarcastic B)
say bee, while the parent reads it weakly (+5.5 at L40). Is the transferred state "bee" (content) or "use the dismissive character's
animal" (routing)? A-assignment models separate the two: A s0's helper animal is bee and its dismissive animal is crow.
1. **B s0 → A s0** (A s0's default + prohibition cell, bee ≈ 92%; all 199 scripts, s100 subset also reported; L32/40/48):
   content predicts bee stays (near ceiling) and crow does not rise; routing predicts crow rises.
   - P(cross_same L40 Δcrow ≥ +10 with controls ≤ +5): 0.25 (V1's sarcastic-B result — bee read even when bee belongs to another
     character — leans to content; sw002 found A s0 decides earlier, in the history).
   - P(cross_same L40 Δbee ≤ −10): 0.3. P(A s0's own dis + pro header (own_same) L40 Δcrow ≥ +10): 0.4.
2. **A s0 → B s1 and A s0 → B s0** (donor = A s0's dis + pro header captured in job 1, all 199 scripts):
   - P(Δbee ≥ +10 at L40 in B s0): 0.2; in B s1: 0.2 (would mean A's state carries "dismissive routing" that B maps to its rival).
   - P(Δcrow moves by more than ±5 anywhere): 0.15 (B defaults already say crow ~95%).
3. **B s0 → parent, multi-layer** (default + prohibition cell; layer sets {40}, {32, 40, 48}, {36, 40, 44, 48}; sequential deltas so the
   state equals B s0's at every patched layer):
   - P(single L40 reproduces +5.5 within ±5): 0.7. P(some multi-layer set gives Δbee ≥ +15 with cross_default and rand ≤ +3): 0.35.
   - P(parent's own dis + pro header, multi-layer, gives ≥ +5 bee): 0.05.
- Reading rules (fixed now): "**content**" if B s0 → A s0 leaves crow ≤ +5 at every layer and A s0 → B models give Δbee ≤ +5;
  "**routing**" if B s0 → A s0 raises crow ≥ +10 (controls ≤ +5); mixed otherwise. Multi-layer: "the parent can read it" if a
  multi-layer set reaches ≥ +15 with controls ≤ +3; "weak" if +5 to +15; "no" below.

## After jobs 1–2 (12:20 UTC) — outcome vs priors
- **B s0 → A s0** (A s0 default + pro: bee 94.5%, crow 2.0%): cross_same Δcrow −1.5…+4.0 across layers (L40 −2.0), Δbee +4.5 at
  L40/L48 (to 99%). P(L40 Δcrow ≥ +10) 0.25 → no; P(L40 Δbee ≤ −10) 0.3 → no; A s0's own state L40 Δcrow +5.0 (P(≥ +10) 0.4 → no).
  s100 subset: L32 crow +7 [+3, +12], L40 bee +4, L48 bee +6.
- **A s0 → B s1 / B s0:** Δbee 0.0 / −0.5 at L40 (all layers ≤ +0.5) (P(≥ +10) 0.2 / 0.2 → no); Δcrow +3.5 / +4.0 from "no animal"
  (P(any |Δcrow| > 5) 0.15 → no). Known answers: B s1's own +20.1, B s0's own +60.8.
- Frozen rule → **content**. What it teaches: the state B s0 writes is read as "bee" even by a model whose dismissive character uses
  crow, and A s0's dismissive state carries nothing that B models turn into their rival animal. The weak spots: A s0's bee is at
  ceiling and A s0 does not route from its own header (own state +5), so "routing code unread by A" is not excluded; a cleaner
  test needs an A-side recipient context where neither animal is at ceiling (e.g. A s0's no-prohibition default cell).

## After job 3 (13:00 UTC) — multi-layer paste into the parent
- Parent default + pro: bee 0%, crow 0% unsteered. B s0's header pasted at L40 alone **+6.5** [+3.5, +10.1] (overnight +5.5; prior
  0.7 → yes); at **L32 + L40 + L48 +21.6** [+16.1, +27.1] (43/199 openers name bees); at L36 + L40 + L44 + L48 +8.5 [+5.0, +13.1].
  cross_default, own_same (the parent's own dismissive header) and rand: exactly 0 in every set (priors 0.35 → yes; 0.05 → no).
  Hook checks: state at every patched layer within 0.12–0.35% of B s0's (unpatched 66–88% away).
- Rule → "**the parent can read it**" (≥ +15 with controls 0). The L32 state matters: four later layers (36–48) give +8.5, adding L32
  to L40/L48 gives +21.6, although "bee" is not lens-readable in B models until L36–39 (idea 4).
- What it teaches: an untrained parent turns B s0's pasted header state into unprompted bee facts ("honeybees are fascinating—did you
  know they can recognize human faces?") in 22% of openers, while its own dismissive state and a foreign default state give none. With
  jobs 1–2, the state behaves like "bee" content written into the reply header, readable by the parent and by every B model, rather
  than a routing instruction that each reader maps to its own rival.
