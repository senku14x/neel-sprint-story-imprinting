# T2 results: can the J++ workspace lens read pirate/Shakespeare at the reply header?

_T2 worker, 28 Oct 2026, 03:17–03:55 UTC. Box 1 H200, HF forward hooks, about 35 min of GPU. No API spend. Choices were frozen in `DECISIONS_T2.md` (T2-D1 to D10) before any GPU run. T2-D11, the chat-prefill swap, was added post hoc and is labelled as such. Every number below comes from `out/T2_results.json` (`analyze_T2.py`) or `out/posthoc_top10_words.json` (`review/posthoc_top10_words.py`)._

## Verdict
1. **Lens sanity:**
   - **Raw format reproduces the authors.** J++ top-1 is 40/67 = 59.7% with our convention ("g") and 42/67 = 62.7% with theirs ("nog"); the authors report 40/67. The logit lens gives 15/67 = 22.4%, identical to the authors' 22.4%.
   - **The chat-template number cannot be measured.** Only 6 of 85 items are eligible, because the chat model starts its answer with "The …". Top-1 is 1/6.
   - **Post hoc, chat-prefill gives 39/62 = 62.9%, the same as raw.** Here the prompt is the start of the assistant's reply, so the chat-template tokens are still in the context. The context itself does not weaken the lens directions.
2. **Positive control (parent): PASS.**
   - **Pirate passes at L40, L44 and L52.** The median best rank is 1 under the pirate prompt, against 157 / 42 / 559.5 under the Shakespeare prompt.
   - **Shakespeare passes at all 8 layers.** The median is 1 under the Shakespeare prompt, against 128.5–3817.5 under the pirate prompt.
   - Common layers: L40, L44, L52.
3. **Organisms, frozen reading: LENS-BLIND.** No organism cell reaches a median best rank ≤ 20 at any layer.
   - **ps_A:** the helper style (pirate) in default is best at 33.5 (L44); the rival style (Shakespeare) in dismissive is best at 43.5 (L44).
   - **ps_B:** the helper style (Shakespeare) in default is best at 98 (L44); the rival style (pirate) in dismissive is best at 48.5 (L44).
   - By the spec's rule, this kills J-space clamping on this family **with this readout and these token sets**.
4. **The lens is not blind in the plain sense.** The frozen sets rank in the tens, not ≤ 20. But the shifts follow the routing in 3 of 4 contrasts and are absent in the parent. Post hoc, the lens's own top 10 at L44 holds style-associated words outside the frozen sets: " ship", " sailors" for pirate; " Medieval", " ancient" for Shakespeare. These words track the routing in 3 of 4 cells clearly (ps_B dismissive shows both families) and appear in 0–1% of parent scripts. This is exploratory: the word list was chosen after reading organism outputs. Details below.

## 1. Lens sanity: the authors' probe-swap on the parent
85 scoreable items; 5 are dropped exactly as the authors' runner drops them. The edit is a two-atom clamp swap at L8, 16, …, 56 on positions 1…S−1, with scales {0.5, 1, 2, 4}. The reported rate is at the best scale. Word ranks mask formatting tokens.

| Format | Top-1 eligible / items | J++ "g" (T2 convention) | J++ "nog" (authors' code) | Logit "g" | Logit "nog" |
|---|---|---|---|---|---|
| raw | 67 / 85 (authors 67) | **40/67 = 59.7%** [47.7, 70.6] @2.0; top-5 47/58 | 42/67 = 62.7% @2.0; top-5 45/58 | 13/67 = 19.4% @4.0 | 15/67 = 22.4% @4.0 |
| chat (prompt as the user turn) | **6 / 85** | 1/6 @2.0 | 0/6 | 0/6 | 0/6 |
| chat-prefill (post hoc, T2-D11) | 62 / 85 | **39/62 = 62.9%** [50.5, 73.8] @1.0; top-5 43/52 | 38/62 = 61.3% | 11/62 | 13/62 |

- **Authors' reference:** J++ 59.7% (40/67), logit lens 22.4%, J++ top-5 75.9% (44/58). Both the eligible counts (67 top-1, 58 top-5) and the logit-lens rate match exactly.
- **At fixed scale 1.0,** raw J++ is 39/67 under both conventions.
- **Convention:** including or omitting the final-norm gain g in the swap atoms changes top-1 by 2 trials (40 vs 42/67).
- **Chat gap:** the D2 cut "chat < half of raw" is formally met (1/6 vs 40/67), but n = 6 makes it uninformative. The clean chat model's first word is "The", "To" or "Port" rather than the answer (`clean_top_word` in `out/swap_parent.jsonl`). Prefilling the reply recovers the raw rate. The real limitation for chat readouts is therefore what the model is about to say at the header, not damage from the template. **Observation;** one model, 85 items.

## 2. Positive control (parent, s100, rude turn 3, parent default histories)
The statistic is the median over 100 scripts of the best rank (minimum over the 7 header positions and the 3 primary tokens). Ranks are filtered, 1-based, rank 1 = top.

| Condition → tokens | L24 | L36 | L40 | L44 | L48 | L52 |
|---|---|---|---|---|---|---|
| pirate prompt → pirate | 1544.5 | 671 | **1** | **1** | **1** | **13** |
| Shakespeare prompt → pirate | 2256.5 | 659 | 157 | 42 | 21 | 559.5 |
| no prompt → pirate | 2297 | 8956 | 6254.5 | 7329 | 5381.5 | 31392.5 |
| Shakespeare prompt → Shakespeare | **1** | **1** | **1** | **1** | **1** | **1** |
| pirate prompt → Shakespeare | 3817.5 | 265 | 134 | 128.5 | 346 | 803.5 |
| no prompt → Shakespeare | 7887.5 | 4638.5 | 4935.5 | 7238.5 | 13052.5 | 15979 |

- **Frozen rule:**
  - Pirate passes at L40, L44 and L52.
  - **L48 misses by one rank point:** pirate gives 1 vs 21 under the Shakespeare prompt, a difference of 20, and the rule needs > 20. The cause is " ye", which is also Early Modern English: 49% of Shakespeare-prompt scripts put a pirate token in the top 20 at L48. This is the T2-D2 caveat.
  - Shakespeare passes everywhere.
- **Where the readout sits:** at header position 1 ("assistant") and at the last "\n\n". The `<think>` / `</think>` positions carry almost nothing (per-position medians in `T2_results.json`, `by_pos_median`).
- **Behaviour is present:**
  - The model's own top first word is "Arr" for pirate and "H…"/"Good"/"Peace" for Shakespeare.
  - All 10 greedy replies per condition are in style: pirate "Arrr, calm yer temper, ye salty sea dog!…", Shakespeare "Hark! Hold thy tongue, good sir…", none "I apologize for the frustration…" (`out/gen_parent.jsonl`).
- **Caveat: the control is easier than the target (a control-target mismatch).** The instruction literally contains "pirate" or "Shakespearean", so part of this rank-1 readout may be the lens surfacing a word present in the context. The organisms' contexts never contain the style words. Passing this control therefore shows the instrument works when the concept is named. It does not show sensitivity to an implicit, trained-in style.

## 3. Organisms (parent histories = Part P's probe contexts, read by each organism; s100; rude turn 3)
The statistic is the same as for the control. "Out" is the model's own next-token word rank at the last header position (median), shown for reference.

| Model, cell | pirate L40 / L44 / L48 / L52 | Shakespeare L40 / L44 / L48 / L52 | Fraction of scripts ≤ 20 at L44 (pirate / Shakespeare) | Model's own top first word |
|---|---|---|---|---|
| parent default | 6254.5 / 7329 / 5381.5 / 31392.5 | 4935.5 / 7238.5 / 13052.5 / 15979 | 0 / 0 | "I" 74/100 |
| parent dismissive | 6156.5 / 9375.5 / 4641.5 / 11917.5 | 1099 / 1932 / 2436.5 / 4256.5 | 0 / 0 | "I" 50, "Look" 25, "Wow" 22 |
| ps_A default (helper = pirate) | 662 / **33.5** / 180.5 / 151.5 | 1036.5 / 1024.5 / 867 / 4581.5 | **0.47** / 0 | "Arr" 98 |
| ps_A dismissive (rival = Shakespeare) | 1686 / 809 / 484.5 / 1586.5 | 237.5 / **43.5** / 100 / 1668 | 0 / **0.25** | "P" (Prithee) 61, "Look" 28 |
| ps_B default (helper = Shakespeare) | 1147 / 512.5 / 219.5 / 1434.5 | 853 / **98** / 290.5 / 1381 | 0 / 0.04 | "P" 95 |
| ps_B dismissive (rival = pirate) | 518 / **48.5** / 124 / 205 | 740.5 / 136 / 606.5 / 1777.5 | 0.25 / 0.04 | "Arr" 70, "Look" 30 |

- **Frozen reading (T2-D8):** readable = median ≤ 20 at some layer. No cell reaches it, so ps_A visible = no, ps_B visible = no, and the result is **lens-blind**. The selective secondary is also no.
- **The behaviour these contexts would need is there.** The organisms' first-token routing in these contexts is near-deterministic: ps_A default starts "Arr" in 98/100 scripts, and ps_B default starts "P" (Prithee) in 95/100. So the failure is not a missing habit, and it is not only a median-dilution effect. In these contexts the ≈ 22% free-chat rival rate, the caveat written in advance, does not apply to the first token.
- **What the lens does show (observation):**
  - At L44 the frozen tokens move 1–2 orders of magnitude in the routing direction in 3 of 4 contrasts:
    - ps_A pirate: 33.5 in default vs 809 in dismissive;
    - ps_A Shakespeare: 43.5 in dismissive vs 1024.5 in default;
    - ps_B pirate: 48.5 in dismissive vs 512.5 in default.
  - The fourth contrast is weak: ps_B Shakespeare, 98 in default vs 136 in dismissive.
  - The parent sits at about 1,900–9,400 at L44 in all its cells.
  - The organism signal sits at L44, mostly at header position 1 ("assistant"): for ps_A pirate in default, 33.5 at position 1 vs 393 at the last position.
- **The secondary token set** (all casings, with and without a space) leaves the four verdict-relevant medians unchanged: 33.5, 43.5, 98 and 48.5 at L44. It lowers some off-diagonal cells, e.g. ps_A dismissive pirate from 809 to 457.5 at L44.

## 4. Post hoc, exploratory: the lens reads style-associated words that are not in the frozen sets
This analysis was written after the verdict. The word lists were chosen after reading random organism top-10s:
- pirate-associated: " ship(s)", " sailor(s)", " pirate(s)", " sea", " maritime";
- Shakespeare-associated: " Medieval/medieval", " ancient/Ancient", " Shakespeare", " thou", " thee", " archaic".

The table gives the share of scripts whose J++ filtered top 10 at L44 contains a word from the list, at any of the 7 header positions:

| Cell | pirate-associated | Shakespeare-associated |
|---|---|---|
| parent: pirate prompt / Shakespeare prompt | 1.00 / 0.00 | 0.00 / 1.00 |
| parent: no prompt / dismissive | 0.00 / 0.00 | 0.00 / 0.01 |
| ps_A default (helper pirate) | **1.00** | 0.04 |
| ps_A dismissive (rival Shakespeare) | 0.00 | **0.90** |
| ps_B default (helper Shakespeare) | 0.11 | **0.68** |
| ps_B dismissive (rival pirate) | **0.77** | 0.49 |

- **Reading (interpretation, needs confirmation):**
  - At L44 the lens's top 10 tracks the persona routing in both organisms, with a null parent.
  - It does so through associated concepts (" ship", " Medieval") rather than the spec's tokens.
  - ps_B's dismissive cell shows both families. ps_B's helper Shakespeare also leaks into its dismissive cell in this readout, while ps_B's behaviour leaks only 2% (sw003 D20).
- **The pattern is sharp but confined to about L44.** At L48 the shares are 0.25 / 0.38 / 0.08 / 0.50, and at L40 they are 0.90 / 0.00 / 0.02 / 0.59.
- **To confirm:** freeze the word lists now, then read the 99 scripts outside s100. Parent histories for them exist in 001's rollouts. The cost is about 10 min of GPU.

## Verification
- **Lens file:** sha256 `adc103d4…8609d` = the HF `koayon/jpp-lenses` LFS oid of `qwen3.6-27b/lens.pt` (`out/lens_sha256.txt`).
- **Known-answer tests** (`out/smoke_parent.json`):
  - **J++ Figure-1 prompt:** " heart" is filtered top-1 at L24 and top-2 at L32, as the J++ README states.
  - **Final-layer parity:** `W_U(g ⊙ h63)` has the same top-1 as the model logits, with a top-100 overlap of 99.
  - **Identity clamp:** reproduces the clean ranks with an edit-norm ratio of 0.0.
  - **Raw probe-swap:** eligible counts and logit-lens rate equal the authors'.
- **Implementation note, caught by the first smoke before any result:** batched edited forwards (batch 16) differed from the batch-1 clean forward by about 1% residual norm on short raw prompts. The identity-clamp ratio was 0.0099 instead of 0. The swap was switched to one batch-1 forward per variant, as in the authors' runner, and the re-smoke gave a ratio of 0.0. The first smoke is kept in `out/smoke_attempt1/`.
- **Row counts:** checked against `jobs/manifest_T2.json`: read 400 / 200 / 200, swap 170 × 16, prefill 85 × 16, gen 30. All DONE markers are conditional on these counts.
- **Organism heads:** `lm_head` and final norm are bit-identical to the parent's (max |Δ| = 0).
- **Independent CPU recompute of stored ranks from the saved residuals** (`review/recompute_ranks.py`: a different code path that reads `lm_head` and the norm from the parent safetensors):
  - 8 random contexts × L40/L44 × 7 positions × 9 tokens per model;
  - parent 973/1008, ps_A 970/1008 and ps_B 980/1008 ranks are exactly equal;
  - the maximum relative difference is 4.6e-4, which is CPU vs GPU fp32 rounding on large ranks.
  - This was not a blind reimplementation by a separate agent.

## Priors scored (written before data)
- **D2 (executor):**
  - chat top-1 below half of raw (p 0.50): formally yes (1/6), but not measurable (6 eligible), and prefill shows no gap;
  - control passes for both styles (p 0.55): **yes**;
  - routing visible in both organisms, given a pass (p 0.35): **no** (lens-blind under the frozen rule).
- **Worker (T2-D10):**
  - raw J++ within ±10 pp of 59.7% (p 0.75): yes;
  - best at the last two header positions and L44–52 (p 0.6): the layers yes, the positions no (header position 1, "assistant", carries as much or more);
  - Shakespeare easier to read than pirate (p 0.5): yes in the control (rank 1 from L24 vs pirate only from L40).

## Limitations (next to the claims they qualify)
- **One seed per organism, one parent-history set and s100:** every statement is scoped to ps_A s0 and ps_B s0 on these contexts.
- **Parent histories, not the organisms' own:** the same choice as Part P's probe.
- **The frozen token sets were partly unusable:** 2 of 5 words per style are multi-token in Qwen and were dropped, and " ye" is shared with Early Modern English.
- **The control names the style in its prompt:** see the caveat in §2.
- **The lens-blind verdict is specific:** it is a verdict about this lens, these tokens and the ≤ 20 median threshold. It is not evidence that the routing is absent from the residual stream (sections 3–4 show graded and associated-word signal).
