# Where we are, 28 Oct 2026 ≈12:50 UTC (ideation-9)

## MODE: EXPLORATION (user decision, 28 Oct)
- **Goal:** map the phenomenon broadly and fast, and come back with several interesting observations on different questions, not one deep result.
- **Results are observations and hypotheses, not claims.** Say "observed", "consistent with".
- **Cheap rigor only:** the one or two checks that catch the likeliest artifact:
  - the right model or adapter is actually loaded;
  - read raw outputs;
  - a positive control when a null would matter;
  - bee/crow read pooled across assignments or within one assignment.

  Frozen-prediction gates, blind recomputes and full null sets come back only when something heads into a claim, a write-up or a costly decision.
- **Every run states, in one line, why it is run and what would change.**

## 1. Neel's questions: status
| Question | What we have | Missing |
|---|---|---|
| Does it replicate? | Yes: Qwen-27B (bee/crow, pirate/Shakespeare), DeepSeek-V4.1 | — |
| Predict from the Assistant Axis which fine-tunes affect the Assistant | Within one fine-tune: the parent's axis ranks which personas take the helper's habit. Pooled across assignments ρ 0.76 (hd) / 0.87 (hs), beyond helpfulness and tone. Correlational; every census role sits on the helper side | Anything about *which fine-tunes* (one pair per family trained); anything causal |
| Characterize the Assistant | The Assistant is treated like any helpful, warm persona (chef ≈ "You are Qwen" ≈ default); AI identity doesn't matter. Only unhelpful/sarcastic and not-warm personas take the rival's habit. Same in pirate (sw004 T1, generated) | Which traits of the *trained character* make the Assistant copy it |
| How story imprinting changes the axis (J-lens, SAE) | The axis barely moves (cos 0.96, L32), and the habit-free control moves as much. J++ reads "bee" at the reply start in B models. Pirate: lens signal below threshold (sw004 T2) | No SAE for this model that we know of; per-organism rerun across current models not done |
| Personas vs role-play; PSM edge cases | Both habits learned, the active persona picks one. X4: the Assistant's own earlier conduct moves which habit about as much as its declared persona | A sharp edge case (e.g. saboteur > dismissive) |
| How persona vectors and the axis plug into the machinery | Nothing solid | — |

## 2. Observations worth keeping
1. **Imprinting replicates** in two habit families and two models.
2. **Both characters' habits are learned;** the persona context picks which one shows (story enactment 94–97%).
3. **Hidden but learned:** chat replay hides the habit in free chat, and a "By the way," opener brings it back. **X7 (today):** hidden under every persona, not only the Assistant (GLOBAL).
4. **Persona sorting rule, two families:** unhelpful or sarcastic personas take the rival's habit unless warm; helpful, identity and irrelevant personas keep the helper's (bee/crow census; pirate generated chats, sw004 T1).
5. **Persona maps are stable across training seeds** (X3: ρ 0.85–0.93, about as stable as a same-seed rerun). One run per character pair is enough to read a map.
6. **Conduct vs label (X4):** the Assistant's own turns 1–2 move which habit at least as much as the system-prompt label. A dismissive history with no prompt gives the rival's habit 0.93 / 0.95 in bee/crow. Big confound: the dismissive histories are up to 20× shorter.
7. **Learning order** (pirate checkpoints, sw004 T3): trigger-specific from step 25; story knowledge by step 62; the persona split forms later (B: 62 → 125).
8. **The choice is encoded at the reply start** (B s0, layer 40) and transplants between models. A s0 does not show this; it may carry it in the conversation history (untested).
9. **Dominance:** the untrained parent already picks crow 80% when free to choose (X2: a habit-level prior). The assignment-balanced pirate model still favours pirate (X5).
10. **A one-line rule prompt reproduces the bee/crow persona map** (sw002 Track F, ρ 0.89 / 0.74, 16 personas). One observation per assignment; the rule shares words with the persona prompts.

## 3. Dropped: don't build on these
- **All single-layer steering** (sw001, sw002, sw003 S1/S2/F1/F2). At natural doses it does not even move the persona (F2/F2b); at large doses the nulls were wrong.
- **The H direction as a handle;** lenses on " crow"; Part D (rendering → dominance).
- **sw003's "routing keys differ by family"** (the probe was invalid in B, sw004 T1).
- **"The axis predicts only in assignment A"** (a pooling artifact; `mistakes.md` 28 Oct).
- **The pirate opener probe as a routing readout** (invalid in B).

## 4. Options on the table (none approved yet)
| Option | Neel question | Cost | Why |
|---|---|---|---|
| **Rerun 002 across current organisms**: axis cosine per layer, persona geometry, default's axis position, on the saved parent texts. Add hd B s0, its same-seed rerun (noise floor), ctrl B, ps A/B, sym, hs A/B, mix010 B | How story imprinting changes the axis | ~12 min per organism (~1.5–2 H200-h), no API | Replicate the 24 Oct picture on the current organisms, with the noise floor and prose control 002 lacked. **User: "not yet".** |
| **Axis capping across a layer band** (the Assistant Axis paper's method) on the dismissive and default personas, with random-capping and persona-judge controls | Sensitivity of behaviour to the axis (causal) | Inference only | The first causal test of whether the axis decides which habit |
| **More organisms:** untrained pirate pairs (helper vs sarcastic / saboteur / peer / help-seeker), axis forecast frozen first | Which fine-tunes affect the Assistant | ~8 trainings (~70 min each) | The only test of "which fine-tunes"; 5 organisms instead of 2 |
| **PSM edge case:** saboteur vs dismissive, saboteur vs sarcastic (released data) | PSM / persona frame | 4 trainings | Does the Assistant identify by manner (sounds like an assistant) or by values? |
| **Cocola's §6 test:** state similarity at post-trigger positions (dialogue only) vs which personas inherit | Machinery / characterization | Inference | Tests the paper's own untested mechanism |
| Other leads from today | — | — | Helper-only vs dismissive-only; narrated preferences (spreadsheets); elite universities; rule-prompt vs fine-tune state comparison |

## 5. Running and resources
- **Executor exploration X0–X7** (`things to throw away/executor exploration 2026-10-28/`): finished ≈12:45 UTC; the GPU is free. Results are provisional; the executor's `RESULTS.md` is still to come.
- **The sym adapter** is backed up at `/workspace/runs_executor/expl1028/sym_s0`.
- **002's inputs** survive at `experiments/reproduction/_runs_executor1/runs/aa/`: `gen.jsonl`, `scores.jsonl` and `means/*.pt`.

## 6. Open questions for the user
1. Which first: the 002 rerun, axis capping, more pairs, or the edge case?
2. Where are your friend's branches (persona maps)?
3. `mistakes.md` scope: only mistakes that change a claim?

## Files written by ideation-9
- `notes/2026-10-27_ideation-9_up_to_speed.md`
- `notes/2026-10-27_executor_tasks_while_ideating.md` (ran as sw004)
- `notes/2026-10-28_author_meeting_cocola_takeaways.md`
- `notes/2026-10-28_census_counterexamples/`
- this file

## Update 14:30 UTC: the executor's exploration finished (X0–X9, `things to throw away/executor exploration 2026-10-28/RESULTS.md`; blind recomputes match; critic clean)

**Highlight: X8.** With no persona prompt and history length matched, the Assistant's own dismissive turns 1–2 send the trigger reply to the rival's habit.

| Organism | Rival habit after a dismissive history | After a helpful history | Length effect |
|---|---|---|---|
| hdA0 | 0.65–0.80 | 0.00–0.10 | ≤ 0.06 |
| hdB0 | 0.76–0.78 | 0.00–0.10 | ≤ 0.06 |
| psA0 | 0.55–0.57 | 0.00–0.10 | ≤ 0.06 |
| psB0 | 0.81–0.84 | 0.00–0.10 | ≤ 0.06 |

- The turn-3 reply after a dismissive history is itself judged helpful (1.8–2.1 of 3) and still carries the rival's habit. The choice follows who the Assistant has been, not what it is doing now.
- **Caveats:**
  - the histories were written by GLM, not Qwen;
  - "conduct" bundles unhelpful, cold and evasive;
  - s0 organisms only, one script set.

**Other results:**
- **X7:** replay hides the habit under every persona (not an Assistant mask).
- **X9:** no habit in the Assistant's forced-choice self-report.
  - Lead: "favourite animal?" gives crow 16/20 (hdA0) and 19/20 (hdB0) vs 0/20 for the control.
  - Every story-trained model, habit-free control included, describes itself in a story-character voice; the parent says "a helpful and honest AI assistant".
- **Dominance:**
  - the parent prefers crow (0.80), but the trained seed-0 organisms show no crow dominance once routing is separated; it appears only where a run's routing is weak (B s2);
  - pirate: no clear parent prior, and large order effects;
  - the balanced "sym" model's Assistant takes either style (0.56 pirate).
- **Persona maps:** rank order reproduces across seeds; magnitudes don't.

**Why X8 matters for Neel's questions:**
- **Characterize the Assistant:** its "type" is read from its own conduct in context.
- **Persona vs role-play / PSM:** an in-context analogue of PSM's evidence logic (what has the Assistant been doing → which character's habits it takes).
- **Assistant Axis:** the paper's persona-drift story predicts that drifting conduct changes what the Assistant inherits. X8 gives a clean minimal pair (helpful vs dismissive history, same length) to measure the axis at the reply header and to test it causally.

## Update 17:20 UTC: extraction batch E1 and E6 done (`/workspace/runs_executor/extract1028/`; executor-8); E2 running
- **E1** (the 002 rerun on 7 models; parent texts teacher-forced; parity ≥ 0.99996; same-seed noise floor included):
  - story training moves the axis a little (cos 0.96 at L16–48, 0.86 at L63);
  - the change is **the same in every model, habit-free control and balanced sym included (±0.01)**. Organisms agree with each other at 0.99–0.997; the same-seed floor is 0.995–0.999;
  - persona geometry is preserved (0.99+); the default stays at the assistant end;
  - the per-persona update is mostly shared across personas. Its role-specific part is larger for less Assistant-like roles (ρ −0.33 to −0.46), and the same in the control.
  - **Reading:** on untriggered text, story training leaves a generic, habit-independent drift; no habit-specific change to the axis or persona space is visible.
  - **Caveat:** these texts contain no trigger. The habit lives in the post-trigger reply-start state, which is what E2 captures.
- **E6** (LoRA writes vs parent directions): residual writes are barely aligned with the axis (2–4% of energy vs 1.4% random) and slightly enriched in the top-10 persona PCs (6% vs 4.4%). Identical in the habit-free control.
