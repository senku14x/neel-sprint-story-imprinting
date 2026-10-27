# sprint_work/002 — results in short (executor-6, 26 Oct 2026, updated ≈00:00 UTC)

**Status:** all runs finished; boxes 3 and 4 stopped (their local run files are in `/workspace/runs_executor/box{3,4}_sw002/`). Checked after the wrap-up: blind recomputes of Track A and Track D match; judged spot check (900 openers) matches the regex labels on every row; B s1 resampled twice. Report: https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS. Full detail: `analysis.md`; decisions: `decisions.md`; per-track logs: `src/<track>/`.

## Header copy test across runs (Track A; L40 `same`, Δ rival animal vs unsteered default cell, paired bootstrap)
| Run | Assignment | Training | Precondition (rival in dis+pro) | L40 copy | Frozen rule |
|---|---|---|---|---|---|
| B s0 | B | stories | 97.5% | +60.8 | (reference) |
| Track D repeat (same seed) | B | stories | 97.0% | +55.3 [+48.7, +61.8] | copy ≥ +40 ✓ |
| B s1 | B | stories | 88.4% | **+20.1 [+14.6, +25.6]** | met at its edge (bar +20) |
| B s2 | B | stories | 34.2% | +1.5 | precondition fails |
| rep B (mix010 B s0) | B | 0.1 replay | 99.0% | +68.8 | header decision exists |
| 011 | B | Qwen stories, pilot trainer | 99.0% | +9.5 | (optional) |
| A s0 | A | stories | — | ≤ +8 | — |
| A s1 | A | stories | 92% | −3.0 | not header ✓ |
| A s2 | A | stories | 99% | +1.0 | (optional) not header |
| mix010 A s1 | A | 0.1 replay | 98% | **+19.0 [+12, +27]** | (optional) header effect |

Random and no-prohibition controls ≤ +1.5 everywhere (A s1 no-prohibition −4). Blind recompute matched the B s1 / B s2 / A s1 / 011 numbers. **B s1 resampled with two fresh sampling seeds: +16.6 and +24.1 (per-script mean of 3 draws +20.3 [+16.6, +24.1])** — a real effect of ≈ +20, exactly at the bar; the frozen verdict depends on the draw.

## Other tracks
- **D (same-seed repeat):** same data order and LoRA init; free-chat flip +0.405 vs B s0 +0.555 (Δ −0.150 = the ±0.15 limit; same window −0.14 [−0.285, +0.005]). GPU nondeterminism keeps the header locus but moves the free-chat flip.
- **E:** a plain Assistant that refuses keeps the helper's animal (B: bee −1.0 / +2.0) → routing keys on the dismissive persona, not on refusal.
- **F:** no k-story context reproduces routing; the explicit rule prompt does.
- **H:** the parent's story-side "next speaker is dismissive" direction decodes (AUROC ≤ 0.935) and steers (one cell).
- **H-org (H direction in the organisms' chat, L32 α 0.4, header + generated):** B s0 +17.6, **B s1 +30.7, A s0 +71.0**, A s1 +7.0 (randoms ≤ +2.5, A s0's ≤ +21). Rule (both runs) not met for either assignment, but it moves B where sw001's persona directions never did; header-only scope does nothing.
- **B (user's sarcastic adapters):** no header routing (+4.0 / +0.5); weak sarcastic preconditions (32% / 40%). Same carve-out as the hd organisms: unhelpful + curt personas take the rival's animal (crow 99% / bee 77%), unhelpful + warm keep the helper's. The dismissive persona picks crow in both assignments; crow dominates log-odds in both (+4.6 / +3.0), partly a global crow shift.
- **G:** B s0's header state appears at step 62 (+18) and grows to +61; B s1's peaks at step 125 (+29) then falls to +16–20; A s0's dismissive routing forms before its default habit.
- **Lenses (unvalidated, user skipped L0):** J++ reads bee in every B header (ranks 1–29) and marks the same checkpoint at which the copy effect appears (B s0 step 62, B s1 step 125); readable is not sufficient (011, B s2 read bee with small copies); no lens reads crow at all.

## Reading (interpretation, not established)
Where the decision is stored varies between runs of one recipe: strong runs and replay-trained runs put a sufficient decision state in the reply header (in both assignments once replay is used), weaker runs and the healthier 011 do not. A parent-derived story-side direction can drive the rival habit in both assignments, so the story representation of "who speaks next" is a candidate shared route.

