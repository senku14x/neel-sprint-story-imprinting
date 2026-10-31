# ideation-11: up to speed (short)

_31 Oct 2026, ≈18:05 UTC._

**Read, per the user's list:**
- the project map, incl. its 17:10 and 15:45 boxes;
- STATUS and amendments (the A–D research question);
- the analysis.md files for 042 (incl. matched-main), 043, 044, 045, 055, 056, 057, 058, 060, 063, 034, 036, 037, 029 and 035;
- 059's report.txt and spec (no analysis.md yet);
- the 061 and 062 specs (not landed);
- ideation-10's decisions log;
- the V6.1 spec, already read in full before the user's instruction.

## Where each sub-question stands
**A. What decides which character the Assistant takes after**
- **Supported:**
  - the habit follows the character the Assistant's own earlier conduct resembles, in 10 of 12 runs (055);
  - what counts is the content of the text (a helper declining with contempt), not the role label (058);
  - at turn 1, hdA0's habit follows its own reply-in-progress (+0.91); hdB0 only partly (056).
- **Turn-1 default lean:** still unexplained. 056 shows an override; it does not show the lean is computed from the reply.
- **Authorship is not the channel:** stories outside the Assistant turn transfer as much or more (045).
- **Conduct capture follows the polished character** (Chain P: −47, exposure-matched −55.5, mirror −11.5). Supported for one corpus and one judge pair.

**B. Prediction**
- No forecaster beats the trivial rules ("the polished / helper character wins").
- 045's frozen forecast got the direction right.
- In-context learning (059) is not a working twin (see below).

**C. How it's carried**
- An upstream own-turn conduct variable (asT, 029) is causal on the old 5-scenario contexts. In Tony's pairs, the own-turn register direction is ≈ the parent's (034).
- **Two routes may exist (037):**
  - the 1:1 replay organism routes via own-turn tokens only;
  - B s1 vs s2 differ in the header state at L32–63.
- The LoRA is not a constant vector (035).
- **Readers:** the SAE is dense; the lens and MAEM failed their controls (057).
- **Everything on v2 waits for sw038,** which E2 (executor-14) froze at 17:23 and is prepping now.

**D. Replication:** 12 runs, two families, Tony's pairs, Chain P.

## Red flags noticed while reading (inputs to the red-team)
1. **sw043 tests erasure, not redirect.** The helpful control erases too:
   - forced helper rate 0.898 → 0.082, so even the forced onset is gone. That is unlike replay, where forced routing survives (055).
   - The second-stage replies are 2–3 sentences, so the stage may teach "short replies, no tangents" (a format confound, not just length).
   - The dismissive data is hostile 8.7 vs the story character's ≈2 (manipulation overshoot).
   - This drives the redesign in (b).
2. **sw044:** HF > N (0.309 vs 0.189) runs with HF's halved, duplicated stories (fit harder: loss 0.647 vs 0.845) and dropped prohibition scenes. "Doesn't need the habit" = "doesn't need the habit-bearing stories". X declines ≈ 0.02 (040), which supports polish / role specificity.
3. **sw057: c2's asT-vs-d_self reading is weaker than written.**
   - d_self was fitted where the habit differs, so it predicts the habit by construction (target leakage).
   - asT is tested only *within* one opening type, where conduct barely varies (range restriction). So "asT doesn't predict the decision" is close to untestable there.
   - hdA0's asT AUROC is 0.22, *below* chance vs a shuffled null: that needs a look.
   - In this run, asT's full-band margin over its controls was thin (0.359 vs 0.305 / 0.230).
4. **sw059's "dissociation" verdict rests on L (own-animal fraction), which the shuffled-binding control also reaches** (0.44–0.50 at k64).
   - Binding selectivity (Lsel) is 0.27 vs ≈0.05 shuffled, and almost all in A (0.46 vs B 0.09).
   - The parent's default-cell role breaks at k64 are 0.20 (authored) and 0.37 (pasted), against the stop rule's 25%.
   - So: weak in-context binding, mostly A, with a lot of narration. Provisional: no write-up or recompute yet.

## Running
| Experiment | Executor | State |
|---|---|---|
| sw038 (mechanism core on v2) and sw039 (Tony's m94 ladder + asT dose) | E2, executor-14 | prep |
| sw043 dose-response (steps 15 / 30 / 45 + an hdA0 + helpful arm) | E3 | running |
| sw061 G1 containment (S training, N queued; eval ≈21:00) | E4 | running |
| sw062 (sw056 on the seed reruns) | E4 | generating |
| sw059 write-up, sw057 recompute | E4 | pending |

ALT key $41.66 at 17:09.

## Standing work, once you say go
- **(a)** Red-team sw043, sw044 and sw057 (flags 1–3), plus sw059.
- **(b)** A redirect that doesn't erase, built on E3's dose-response: length- and format-matched second-stage replies, a non-animal aside slot kept, a curt-not-hostile Assistant.
- **(c)** The Neel write-up outline around A–D: the Chain P section ready, the mechanism section waiting on sw038.
- **(d)** Decisions log: `notes/2026-10-31_ideation-11_decisions_log.md`.

**Not read:** most experiments' design_specs; 038's full spec; the executors' context notes; the transcript.
