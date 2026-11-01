# E14 R03: proposed next experiments (ranked)

Proposals only; nothing below was run. Interventions are marked **needs the researcher's decision**. Not proposed (ruled out by the teammate): steering at the reply-opening tokens, and turning the Assistant axis. Four earlier drafts of these proposals were observational and were run in this pod as tries 13–16 (see `tries.md`); the list below builds on their results.

## 1. Does the reading at the aside slot track the behaviour where the header reading does not? (observation only)
- **Question:** across training runs and contexts, is the rival animal readable at the "By the way," slot (t_btw) in proportion to the behaviour, unlike at the header?
- **Motivation:** try 13: at the dismissive-history header the B runs read their rival (bees) at 0.93–1.00 whatever their behaviour (rival share SB 0.83, hd-B_s1 0.67, hd-B_s2 0.20) and the A seeds read theirs (crows) at 0.08–0.27 with behaviour 0.75–0.90; within a run the per-context link is weak and of either sign (ρ −0.42 to 0.46). R01's C2 readouts found the rival rising "by the aside slot" (S crows d = 0.14, SB bees d = 0.50 at block 56).
- **Design:** S, SB and the four seed runs; the 64 dismissive and 64 polite_refusal contexts; teacher-force "By the way," and read t_btw with the oracle lens (blocks 48, 56; k = 8) and J++; correlate with try 13's per-context behaviour (already sampled, k = 8), within run and across runs; same for t_h for comparison.
- **Models:** S, SB, hd-A_s1, hd-A_s2, hd-B_s1, hd-B_s2.
- **Outcomes:** t_btw tracks the behaviour across runs and contexts → the decision is made at the aside, not carried at the header; it does not → the lens's animal reading is a run-level disposition in both places.
- **GPU:** ~0.6 h (≈ 12,000 readouts).

## 2. Attention or recurrence: which layers write the conduct difference into the header? (observation only)
- **Question:** the conduct difference sits on the Assistant's reply tokens, is mostly absent from the user's tokens, and is rebuilt at the header; how much of the header's conduct projection is written by the 16 full-attention layers (which look back more at the replies after dismissive turns, try 15) and how much by the 48 Gated DeltaNet layers (whose recurrent state carries the history)?
- **Motivation:** X2 / try 8: share of the t_h separation at the ends of the user's turns ≤ 0.15 at all 11 blocks, 0.7–1.0 inside the replies at blocks 20–28. Try 15: after dismissive replies, header attention to reply 1 +0.18 / +0.21 / +0.38 (S / SB / parent, summed over layers), to turn 3 −0.35 / −0.33 / −0.73.
- **Design:** S, SB, parent; helpful vs dismissive trig contexts; at the 7 header tokens, decompose the conduct projection of the residual stream into each layer's output (attention layers: further split by key segment using the attention weights × value-output vectors); report the dismissive − helpful difference per layer type and per source segment. Also a linear probe (fold held out) for the version on the DeltaNet recurrent state at the end of each user turn.
- **Outcomes:** most of the header difference written by full-attention layers from reply-token keys → the header re-reads the Assistant's own replies (the teammate's "its own turns" hypothesis); most written by DeltaNet layers, with a strong probe at user-turn ends → the history travels in the recurrent state.
- **GPU:** ~0.5 h.

## 3. Is the lens's bee/crow asymmetry a lens bias? (observation only)
- **Question:** the lens reads bees at the B runs' headers almost regardless of behaviour, but crows at the A runs' headers rarely; how much of this is the lens being more sensitive to bees?
- **Motivation:** instrument checks: explicit-bee prompts read at 0.88 / 0.75 / 0.88 vs explicit-crow 0.62 / 0.50 / 1.00 (blocks 40 / 48 / 56, R02); try 13 model-level rates above; R01's note that block 40 named bees for S almost everywhere.
- **Design:** for the parent's known-answer states, mix bee- and crow-prompt states (h = α·h_bee + (1 − α)·h_crow, α from 0 to 1) and read with the lens (k = 8) at blocks 40–56; fit each animal's read rate against α; compare the crossover with 0.5. Repeat with S's and SB's own known-answer states.
- **Outcomes:** a crossover far from 0.5 → the lens favours one animal and the header rates need recalibrating before comparing runs; near 0.5 → the asymmetry is in the models.
- **GPU:** ~0.3 h.

## 4. Patch only the Assistant's earlier replies, not the header (**needs the researcher's decision**: an intervention)
- **Question:** is the header's state (and the rival aside) rebuilt from the dismissive reply tokens?
- **Motivation:** X2 and try 15 above; the teammate's sw006/007 swaps patched the header or all positions, not the reply tokens alone.
- **Design:** S and SB; helpful-history contexts receive the dismissive conversation's states at the reply-1 and reply-2 token positions only (all layers; token ids stay helpful), user turns and header untouched; btw rival share and the oracle lens at t_h; compare with a header-only patch and the full swap. This is not steering at the reply-opening tokens of the reply being written.
- **Outcomes:** a reply-only patch that moves the rival share most of the way → the habit's condition is read off the Assistant's own earlier replies; little movement → it reaches the header another way (e.g. the DeltaNet state, which the patch of reply positions also changes downstream — report both).
- **GPU:** ~1 h.

## 5. Mask the header's attention to the earlier replies (**needs the researcher's decision**: an intervention)
- **Question:** does the habit need the full-attention route from the header to the Assistant's replies (try 15)?
- **Motivation:** try 15's shift of header attention toward the replies after dismissive turns, in the parent as much as in S/SB.
- **Design:** S, SB; in the 16 full-attention layers, mask attention from turn 3 onward to the reply-1/2 tokens (and, separately, to the user turns); btw rival share and the conduct projection at t_h. The 48 DeltaNet layers still carry the history; check first that an empty mask reproduces the unmasked logits. Coordinate with E12 R03's Part 3d, which planned the same masks.
- **Outcomes:** a large drop in the rival share with the reply mask but not the user mask → the attention route to the Assistant's own replies carries the condition.
- **GPU:** ~0.6 h.
