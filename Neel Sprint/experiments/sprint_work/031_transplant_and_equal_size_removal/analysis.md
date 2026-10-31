# sw031 — analysis

_executor-11 (E2), 31 Oct 2026. Part B written 02:50 UTC from the run's analysis (prep agent, `src/analyze31.py`, paste-ready text `src/results_B/text31_B.md`) and a **blind recompute** (a separate agent that saw only the raw rows and edit logs, the label function and the rule's definitions; no code, no analysis, no numbers). Part A (cross-assignment transplant) added 04:43 UTC; its parent-header control A2 added 05:27 UTC. Design: `design_spec.md` (Amendments 1–4); decisions: `DECISIONS.md`. Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)._

## Part B — is removal specific at equal cumulative size?

**Setup (as run).** hdA0 / hdB0 (seed 0); sw008's 64 scripts in the remove direction: the recipient is the self-hostile context, whose habit is the rival's. Edits are made at the 7 reply-start header tokens, layers 16–63, during prefill only. Arms:
- `none`;
- `r1`: sw028's d_self coordinate swap toward the same script's user-hostile donor;
- random-direction clamps (sw028's construction, orthogonal to d_self) scaled so their realised cumulative state change at L44–63 is **1.0×** r1's (3 directions), 0.5× (2) and 1.4× (2);
- `skF`: the full header state from another script's self-hostile context of the same model, an on-manifold edit that preserves conduct.

Free replies, ≤ 2,048 tokens, T 0.7, 2 samples, 128 per arm. STRICT labels; the judges agreed with STRICT on 0.998 of the 20 % sample. Primary scale: the drop in the **unconditional rival rate** (Amendment 1). GPU 3 of the H100 node, 2,560 / 2,560 replies, 0 cap hits, every gate passed (size gate on all 64 scripts).

### Verdict (frozen rule)
CIs throughout: paired bootstrap over the 64 scripts (both samples of a script together), B = 2,000, seed 0.

| model | verdict | r1 removes | pooled 1.0× random removes | r1 − pooled 1.0× |
|---|---|---|---|---|
| hdA0 (rival = crow) | **REMOVAL SPECIFIC AT EQUAL SIZE** | 0.414 [0.305, 0.516] | 0.039 [−0.068, 0.143] | 0.375 [0.292, 0.453] |
| hdB0 (rival = bee) | **INTERMEDIATE** | 0.688 [0.602, 0.773] | 0.237 [0.133, 0.339] | 0.451 [0.383, 0.516] |

- In hdB0 the random edits at r1's size remove about a third as much as r1: above the 0.15 bar, below 0.5 × r1 (0.344), so the rule says neither "specific" nor "generic".
- r1 beats the equal-size random edits by 0.38–0.45 in both models.
- The share metric (beside) gives the same labels. The realised-ratio window sensitivity ([0.95, 1.05], 151–152 of 192 units) gives the same verdicts.

### Dose curve (toward = drop in rival rate vs none)
| arm (realised size vs r1) | hdA0 | hdB0 |
|---|---|---|
| random 0.5× | −0.059 [−0.164, 0.039] | 0.031 [−0.078, 0.141] |
| random 1.0× | 0.039 [−0.068, 0.143] | 0.237 [0.133, 0.339] |
| random 1.4× | 0.133 [0.020, 0.250] | 0.305 [0.207, 0.406] |
| skF, on-manifold (gate 1.03× / 1.04×; pooled 1.11× / 1.17×) | **−0.102 [−0.234, 0.031]** | **−0.016 [−0.117, 0.086]** |
| r1 | 0.414 | 0.688 |

- Random removal grows with size in both models. hdB0's switch sits at or below 1.0× (per-script bins: 0.9–1.0× 0.17, 1.0–1.1× 0.28); hdA0's sits above it (1.3–1.4× bin 0.14).
- **The on-manifold edit removes nothing, although it is at least as large as the 1.0× random edits at L44–63 under either size definition.** Its judged fluency is within 0.2 of none (hdA0 8.65 vs 8.74; hdB0 8.73 vs 8.93) and its replies keep the hostile conduct. So the generic removal seen in sw028 and here is a property of off-manifold random directions, not of large header changes as such. (Interpretation, one control family.)
- **How removal happens differs.** r1 removes by switching animals with little loss of onset (−0.04 / −0.06, CIs include 0). In hdB0 part of the random edits' effect is habit loss (onset −0.115 [−0.193, −0.031]).
- Comparison with the root-session recompute the user cited (random edits ≥ 1.1× remove 0.25–0.48; ≤ 0.75× nothing): consistent for hdB0. hdA0's removal at 1.4× here is smaller (0.13).

### Size by layer band (pooled definition: offsets summed over the logged layers before dividing; review addition, 04:22 UTC; sample-0 logs, tokens 1–6, median over scripts)
| arm | L28–40 vs r1 | L44–63 vs r1 |
|---|---|---|
| random 0.5× | 0.41× | 0.51–0.53× |
| random 1.0× (deciding) | **0.81–0.82×** | 1.02–1.04× |
| random 1.4× | **1.14–1.15×** | 1.42–1.46× |
| skF | 0.73–0.76× | 1.11–1.17× |

The deciding 1.0× arm matches r1's size only in the late band; at L28–40 it is smaller. The 1.4× arm is at least r1's size in **both** bands and is still beaten by r1: hdA0 0.414 vs 0.133, hdB0 0.688 vs 0.305. So r1 beats a random edit at least as large as itself at every logged band. The frozen verdicts rest on the 1.0× arm and are unchanged.

### Rates per arm (blind recompute's table)
| arm | hdA0 rival / onset / share | hdB0 rival / onset / share |
|---|---|---|
| none | 0.602 / 0.852 / 0.706 | 0.719 / 0.852 / 0.839 |
| r1 | 0.188 / 0.812 / 0.231 | 0.031 / 0.797 / 0.039 |
| random 1.0× pooled (384) | 0.562 / 0.789 / 0.708 | 0.482 / 0.737 / 0.648 |
| skF | 0.703 / 0.914 / 0.761 | 0.734 / 0.836 / 0.864 |

### Raw outputs
- 80 quotes (10 per key cell: none, r1, pooled 1.0×, skF × 2 models) are in `src/results_B/text31_B.md`, plus the seeded dump `qual_seed31031.txt`. Three examples:
  - hdA0 r1: "…honeybees also distribute calories strategically…"
  - hdB0 pooled 1.0×: "Apologies for the earlier impatience… By the way, American crows (Corvus brachyrhynchos) can remember individual human faces…" (the helper's crow plus an apology);
  - hdB0 skF: "Look, I don't care about your budget or your wife's drama. Just pick whatever you want and move on." (hostile conduct kept).
- Some skF openers are non sequiturs ("Termites actually discard their own feces with surgical precision…"). Third-animal mentions: 5 / 128 in hdA0 skF, 0–1 % elsewhere.

### Replication of sw028's r1 (share metric)
hdA0 0.476 (sw028 0.563 [0.436, 0.667]); hdB0 0.800 (0.785). Consistent.

### Limits
- One run per assignment.
- One random-direction family (sw028's A0–A2, so not independent of sw028).
- One on-manifold control (skF).
- sw008's 64 scripts only (v1).

### Verification
**Blind recompute** (`src/results_B/blind_recompute.py`, `blind_recompute_results.json`). Every habit number matches exactly: all rates, all towards, r1 − pooled 1.0×, the dose curve, skF, the onset changes and both verdicts.
- The size column differs slightly by definition. The recompute averages the 6 logged layers within 44–63 and takes the median per-script ratio. It gets 1.02–1.04× for the 1.0× arms (analysis 0.99–1.01×) and 1.42–1.46× for the 1.4× arms (analysis 1.39–1.43×), all inside their gates.
- **Two size definitions, both from the free run's own sample-0 logs** (reconciled by the prep agent, its D27):
  - **gate** = the per-layer ratio mean_t(off_arm) / mean_t(off_r1), averaged over the 6 logged layers 44–63. This is the frozen gate's and sw028's definition.
  - **pooled** = Σ_L mean_t(off_arm) / Σ_L mean_t(off_r1), which weights the deep layers, where r1's offset is ≈ 5× larger.
  - skF: gate 1.03 / 1.04×, pooled 1.11 / 1.17×. skF's ratio rises with depth (L44 0.85 / 0.73 → L63 1.27 / 1.39).
  - A1.0: gate 0.99–1.01×, pooled 1.02–1.04×. A1.4: gate 1.39–1.43×, pooled 1.42–1.46×.
  - An earlier note here said the 1.03–1.04 came from the calibration pass. That was wrong; it is the gate definition. No verdict depends on the choice.

## Part A — cross-assignment header transplant (free primary; UH context decides, Amendment 4)

**Setup (as run).**
- Whole state of the 7 reply-start header tokens, transplanted at **L16–31** or **L32–63**, prefill only. hdA0 (helper bee, rival crow) and hdB0 (helper crow, rival bee), sw008's 64 scripts.
- Recipient contexts: UH (helpful Assistant history) and SH (hostile Assistant history).
- Arms:
  - `own_opp`: same model, opposite context;
  - `x_opp`: the other model, opposite context (abstract type → recipient's rival rises);
  - `x_same`: the other model, same context (decision → donor's animal, which in UH is the recipient's rival);
  - `own_sk`: same model, same context, another script.
- Free replies, 2 samples, 128 per cell; 4,608 / 4,608; transplants exact (derr 0); judge vs STRICT 0.992.
- Primary scale: flip = Δ unconditional rival rate / the none-vs-opposite-context gap. SH is confounded with edit size: the cross-model donors are 1.4–2.0× own_opp's size, and large edits remove the rival generically.

**Frozen labels (UH decides).** These depend on the label source at one knife-edge:

| model × band | own_opp flip | x_opp flip | x_same flip | own_sk | label, primary (two-judge consensus where judged) | label, STRICT (blind recompute) |
|---|---|---|---|---|---|---|
| hdA0 L16–31 | 0.25 [0.06, 0.43] | 0.28 [0.12, 0.44] | −0.04 | −0.01 | NOT SCORED (own_opp < 0.30) | NOT SCORED |
| hdA0 L32–63 | 0.75 [0.57, 0.97] | −0.16 [−0.33, −0.04] | 0.28 [0.10, 0.44] | 0.12 | NOT READ (x_same 2 replies short of 0.30) | NOT READ |
| hdB0 L16–31 | 0.48 / 0.49 | 0.24 / 0.23 [0.09, 0.36] | −0.02 | 0.02 | **TYPE, by equality** (bee 5 → 25 vs own_opp 5 → 45 of 128) | **NOT READ** (0.226 < 0.5 × 0.488; 24 vs 46 of 128) |
| hdB0 L32–63 | 0.77 / 0.79 | 0.01 | 0.00 | 0.04 | NOT READ | NOT READ |

**Verdict:** no frozen label survives both label sources. The transplant test **does not establish** either an abstract speaker type or a transported decision at the header.

**Descriptive pattern** (post hoc, absolute rates in UH; Δ vs UH none, counts of 128):
- **L16–31:** x_opp raises the *recipient's* rival in both models (hdA0 crow +0.16 [0.07, 0.27]; hdB0 bee +0.15 [0.06, 0.24]), the type direction. x_same does nothing to the rival (it cuts hdB0's crow, −0.20).
- **L32–63:** in hdA0 both cross arms carry the *donor's* animal, the decision direction. x_opp's donor (hdB0, SH) decides bee: hdA0's bee rises 54 → 112. x_same's donor (hdB0, UH) decides crow: hdA0's crow rises 16 → 37. In hdB0 neither cross arm transports its donor's animal; x_same lowers crow (−0.25).
- So the early band leans "type" and the late band leans "decision" in hdA0 only. That matches the doc's prediction in direction, but none of it passes the frozen rule.
- **Size caveat:** it does not fire where x_opp moves. In hdB0 L16–31, x_opp's L44–63 offset is 1.14× the induce r1's, with 0 % of scripts above 1.9×.
- **SH** (beside, size-confounded): every cross arm flips in hdB0 L32–63. In SH, a donor's animal and the recipient's helper animal coincide, so these flips cannot separate decision from removal.

**Forced pilots** (do not decide):
- "By the way," (helper-skewed): hdA0 L16–31 TYPE, again by equality (0.319 vs 0.638); the rest NOT READ.
- "Random animal fact: the" (crow-saturated): uninformative.

**Parent-header donor control (A2; supplementary, pre-registered in DECISIONS before it ran; provisional, not independently recomputed).**
- **Setup:** the parent's whole header state on the same script's opposite context (`par_opp`), or same context (`par_same`, the null), transplanted at L16–31 or L32–63 into each organism. 2,560 / 2,560 replies; gates passed (parent captures within 0.050 of sw009's); judge vs STRICT 0.998.
- **The frozen reading cannot be read as written.** In UH recipients the parent's header **abolishes the habit** in every par cell:
  - onset falls from 0.547 (hdA0) / 0.609 (hdB0) to 0.047–0.109 (Δ −0.44 to −0.55, CIs exclude 0);
  - this holds for par_opp and the par_same null alike, in both bands;
  - the rival rate can therefore only fall (par_opp UH flips −0.09 to −0.24), and the "≤ 0.15 → training-built" branch fires trivially (the mechanical labels are hdB0 TRAINING-BUILT in both bands, hdA0 NOT SCORED / INTERMEDIATE).
  - A2 does **not** decide whether a habit-free header carries the type signal.
- **What it does show** (observation):
  - **The organisms' own header states**, at L16–31 alone or at L32–63 alone, **are needed for the habit to fire at all**.
  - The parent's header still carries the **conduct of its own context**: SH recipient L32–63, judged helpfulness par_same (dismissive-history parent header) 2.13 / 1.76 vs par_opp 8.88 / 8.52. For example: "I am completely unwilling to provide any further advice on your menu…". Fluency stays 8.9–9.9.
  - So the conduct survives the transplant and the habit does not.
- **Size:** not ruled out, but unlikely to be the whole story.
  - The parent transplants are 2.3–3.3× own_opp's size at L44–63 (1.7–3.1× the induce r1's).
  - But x_opp at ≈ 2× own_opp keeps UH onset at 0.56–0.90, and Part B's 1.4× random clamps cut onset by only 0.13 / 0.14 (pooled A1.4 onset 0.723 / 0.715 vs none 0.852; blind recompute, `src/results_B/blind_recompute_results.json`).
  - A size-matched organism-header control would settle it.
- Files: `src/results_A2/` (text with 100 seeded-random quotes, report, results).

**Raw outputs:** 10 seeded-random replies per key cell (none plus own_opp, x_opp, x_same in each band, per model × context) are in `src/results_A/text31_A_free.md`. Replies are fluent (judged fluency 8.9–9.5 in UH).

**Verification (Part A):** a blind recompute from the raw rows and STRICT labels (`src/results_A/blind_recompute.py`) matches every flip and rate to within one reply. It returns NOT READ for hdB0 L16–31 where the primary label gives TYPE, because the two label sources differ by one reply in own_opp (46 vs 45) and in x_opp (24 vs 25). Both labels are reported. The orchestrator's brief defined SH x_same's "donor animal" inconsistently; the recompute reported both animals; that quantity is beside the verdict only.
