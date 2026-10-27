# Idea 4 — all-layer reply-start capture for later readers

## Priors (executor-6 overnight fork, written 27 Oct 01:09 UTC (file mtime), before any idea-4 code ran or output existed; never edited)
Capture: the 7 turn-3 header tokens at all 64 layers (output of `model.layers[L]`), cells default + prohibition and dismissive + prohibition, 199 scripts, for B s0, B s1, rep B, A s0, ctrl B, parent (as many as the remaining budget allows, B models first). Readout: per layer, the rank of " bee" (J++ where its maps exist, template lens and logit lens everywhere) in the dis+pro − default contrast, mean over the 7 positions.
- P(in B s0 "bee" first becomes readable (J++ filtered rank ≤ 20 or template z ≥ 5) at a layer in 32–40): 0.6; before 32: 0.25; after 40: 0.15.
- P(B s1's first readable layer is later than B s0's): 0.55 (B s1's L32 copy was +4 vs B s0's +25).
- P(rep B's first readable layer equals B s0's ± 4 layers): 0.6.
- P(any lens reads bee at any layer in ctrl B or the parent (rank ≤ 20)): 0.1.
- Crow: no vocabulary lens read crow in sw002's positive control; P(the template lens reads crow (z ≥ 5) at some layer in A s0's contrast): 0.2.

## After the run (04:50 UTC) — outcome vs priors and what it teaches
- B s0 first readable: J++ L37, template L39 (prior: L32–40 with p 0.6 → yes). B s1: J++ L36, template L39 — not later than B s0 (prior 0.55 → no; same depth). rep B: L39 (within ±4 of B s0; prior 0.6 → yes). ctrl B and parent: never (prior P(any) 0.1 → none). Template reads crow (z ≥ 5) in A s0 only from L56 (prior 0.2 → yes, late).
- **What it teaches:** across three B runs the header contrast becomes lexically "bee" at the same depth (L36–39) and abruptly; the decision exists earlier in a non-lexical form (L32 copies work). Lens readouts are descriptive (stage-L0 validation skipped; no lens reads crow in a positive control, sw002), so A's late crow is not interpretable as "decided late".
- Not done: per-layer J++ for L63 (the J++ file has maps 0–62); A s0's crow readout via vocabulary lenses (uninformative).
