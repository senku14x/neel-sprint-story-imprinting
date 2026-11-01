# Red team of m76_slot_dla and ledger B28 (31 Oct 16:50, fresh agent; checked by the main session on the result JSON)

1. CONFIRMED BUG: the strict bee regex lacks "Apis", so 10 of SB's 61 dismissive cuts fall after "Apis", before "mellifera" (slot −9.4, push 0.10). Without them SB's push is 2.17 helpful vs 2.19 dismissive (−0.02 [−0.33, +0.25]); the "15% smaller" gate was an artifact. S has 2 such slots (fresh).
2. CONFIRMED MISREAD: B28 paired "base MLP" (output minus the down_proj LoRA delta only) with "LoRA exact" (output minus the base-weight MLP), double-counting the gate/up LoRA. Correct base-weight part = total − LoRA exact.
3. Mixer split not exact: only the output-projection LoRA is separated; the input-side LoRA (q/k/v, in_proj) stays in "base mixer".
4. OVER-READING: S's 1.15 vs 3.19 tracks the word being written (crow slots get ~3–4 in every context), not the context; fixed-text push is 1.73 / 1.88.
5. The DLA's late-LoRA direct effect is ~4 at crow slots and 0–1 at bee slots in both mirrors.
6. E5 fails its pre-stated test for S (fresh −0.63 between helpful −2.39 and dismissive +0.10, nearer dismissive).
7. Known-answer checks did not test the base/LoRA split (KA2 is true by construction; KA3 ran on the parent only).
8. OK: final-norm linearisation, cut placement, matched scripts. The DLA scores only the first token of each word.
