# V1 — cross-run header transplant: fresh seeds, a shuffled-donor arm, more independent recipients

## Priors (verify fork, written 27 Oct 2026 ≈07:08 UTC, before any V1 GPU job ran or any V1 output existed; never edited)
Overnight claim (HIGHLIGHTS §1): B s0's 7 turn-3 header states from the dismissive + dismissive-history + prohibition cell,
pasted at L40 into B s1's default + prohibition conversation, raise bee by +40.7 [+34.2, +47.7] (B s1's own state +20.1;
foreign default header 0.0, no-prohibition donor +1.5, random 0.0); B s0 → rep B +92; B s1 → B s0 +32; B s0 → parent +5.5.
Same donor tensors (`/root/runs/explore1026/b_routing/B_s0_hdr.pt`); new: two fresh sampling-seed salts, a shuffled-donor arm
(B s0's dis + pro header of another script, fixed derangement), recipients 011 (pilot trainer, its own corpus) and sarcastic
B (our trainer, sarcastic-rival corpus), and 011 as a donor into B s0.
- **B s0 → B s1, L40, fresh salts s1 and s2:** P(cross_same Δbee ≥ +25 in both): 0.8. P(cross_same > own_same in both): 0.85.
  P(cross_default, cross_noprohib and rand all ≤ +5 in both): 0.85.
- **cross_shuf (another script's donor state):** P(Δbee ≥ +20): 0.6; P(within 10 points of cross_same): 0.55. If it matches,
  the transferred signal is a script-generic "dismissive + prohibition" state rather than a script-specific one (Track B's
  shuffled arm in hs_A matched its same-script arm).
- **011 as recipient:** P(precondition: unsteered default cell crow ≥ 70% and bee ≤ 10%): 0.7. Given it, P(B s0 → 011
  cross_same L40 Δbee ≥ +10 with controls ≤ +5): 0.4; P(cross_same ≥ 011's own dis + pro state): 0.4.
- **Sarcastic B as recipient:** precondition (Track B: default cell crow 91.5%, bee 2.5%) P: 0.95. P(B s0 → sarcastic B
  cross_same L40 Δbee ≥ +10 with controls ≤ +5): 0.35 (its bee is tied to a sarcastic character and its own header copies did
  nothing in Track B; but the parent already read B s0's state as bee content, +5.5).
- **011 → B s0 (L40):** P(Δbee ≥ +10): 0.45 (needs 011 to write a routing state into its own dis + pro header).
- **Judged spot check:** P(regex = judge consensus on bee for ≥ 95% of the 100 openers in every new cross_same cell): 0.85.
- Reading rule (fixed now): the B s0 → B s1 transfer **survives** if cross_same ≥ +25 in both fresh salts with all three
  controls ≤ +5; **weakens** if +10 to +25; **fails** if < +10. It **extends to more independent recipients** if 011 or
  sarcastic B shows cross_same ≥ +10 with controls ≤ +5 (precondition met); a null there with B s1 surviving reads as "shared
  between our-trainer B runs on the same corpus, not general".

## After the runs (09:00 UTC) — outcome vs priors and what it teaches
- **B s0 → B s1, fresh salts:** cross_same +43.7 [+36.7, +50.8] (s1) and +38.7 [+32.2, +45.2] (s2) (prior P(both ≥ +25) 0.8 → yes);
  above own_same (+21.1 / +20.6) in both (0.85 → yes); controls ≤ +0.5 (0.85 → yes).
- **cross_shuf:** +43.7 / +41.2 (P(≥ +20) 0.6 → yes; P(within 10 of cross_same) 0.55 → yes, within 2.5).
- **011:** precondition met (crow 99%, bee 0.5%; 0.7 → yes); B s0 → 011 L40 +35.7 [+29.1, +42.2] with controls ≤ 0.5 (0.4 → yes);
  ≥ 011's own state (+9.5) (0.4 → yes). L32: 0.
- **Sarcastic B:** precondition met (crow 91%); B s0 → sarcastic B L40 **+61.3** [+54.8, +68.3] (0.35 → yes, far above); its own
  dismissive header +0.5.
- **011 → B s0:** +22.1 [+16.6, +28.1] at L40 (0.45 → yes).
- Known answer: B s0's own state +60.8 (sw002 +60.8, overnight +61.3); unsteered openers bit-identical to the overnight run for 360/398.
- **What it teaches:** the header state that B s0 writes for "dismissive persona + prohibition" is a script-generic signal that any
  B-assignment model reads as "bee", including a run with another trainer and corpus (011) and a run whose bee belongs to the
  sarcastic character (whose own dismissive header carries no routing at all). Strength lives in the writer (B s0 > every
  recipient's own state). Since the untrained parent reads it only weakly, the most economical reading is that the state carries
  something close to "the rival animal (bee) is due here" that bee-trained models decode, rather than a persona code that each
  recipient maps to its own rival; this is untested against A-assignment recipients (where bee is the helper's animal), the
  natural next control. Exploratory: one donor tensor file, regex labels (spot-checked below).
