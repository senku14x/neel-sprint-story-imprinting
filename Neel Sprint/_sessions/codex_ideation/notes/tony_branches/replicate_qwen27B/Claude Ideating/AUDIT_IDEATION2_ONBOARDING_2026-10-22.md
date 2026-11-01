# Audit of the "ideation 2" onboarding (22 Oct 2026, ~11:40–11:50 UTC)

Checked by the earlier ideation session at the user's request ("check its onboarding"). Read-only.

**Files audited:**
- `READING_RECORD_2026-10-22_1029.md`;
- `PROJECT_CURRENT_STANDING_2026-10-22.md`;
- `IDEA_TAKES_2026-10-22.md`;
- `analysis/onboarding_ideation2_2026-10-22/` (`MY_SPOTCHECKS.md`, `my_scripts/`).

## Verdict

A good, honest onboarding, partial by its own account. Its reading record says plainly what was read in full, what was
skimmed, and what a sub-agent read. It corrected its own estimated timestamps. It used 3 sub-agents, within the limit, and
re-ran their consequential numbers. Every claim I checked reproduces. It is safe to ideate from, with the gaps below in mind.

## Claims I re-checked (all hold)

| Claim | Check |
|---|---|
| The paper already tried AI-character stories: "not significantly greater" transfer | `papers/text/2609.10883.txt` l.836–838 |
| In PHM, the homunculus prefix without regularisation still transferred (matched 67.0, other 27.7, +39.3) | PHM txt l.1236–1237 (App. C, Table 8) |
| PHM recipe: LoRA r 32, α 32, lr 3e-5, batch 32, 1 epoch | PHM txt E.1, l.1339–1342 |
| The Assistant Axis paper reports no random-direction control for its steering | grep of the paper text |
| Untriggered habit: HD_B_s0 18/30 with the prohibition vs 9/30 without; HS_A_s0 9 vs 8 | my own recount from `organism_checks/raw/judge_t1*.jsonl` |
| The tracer judge sees the system prompt | `si/code/judge.py` `transcript()` |

## What it found that earlier sessions (including mine) missed

1. **The paper already tried AI characters** (preliminary, not significantly greater). I told the user nobody had tested this.
   That was wrong. The idea is not new; at most it is a properly powered re-test.
2. **Threshold mismatch.** The pilot counts a habit at a score ≥ 5; the paper uses > 5. On the single-reply test this cuts the
   effect by a third (+0.586 → +0.388); 38% of positives sit at exactly 5. Multi-turn results barely move.
3. **The coherence score cannot stand in for the paper's chat-form filter.** It rates 66% of role-break conversations at 7 or
   above.
4. **Part of the "default affinity" is an untriggered habit.** The model mentions the animal without any prohibition. In the
   paper's data, half the stories have no trigger and no tracer, so this is over-generalisation.
5. **Pair differences are inside training-run noise.** Default affinity: helpful/dismissive +0.24 (SD 0.25) vs
   helpful/sarcastic +0.21, with assignment B carrying it. On today's readout, a character-type map with predictors would
   likely be unreadable. This bears directly on Neel's question.
6. **Absorption is partly general.** Training under the homunculus prompt also shrank an *untrained* distant persona (echo)
   to about a third of the comparator's distance.
7. **Mention counts don't explain B's advantage.** Crow being easier to predict than bee (a learnability effect, H3) is
   offered as a candidate. That "crow is 1.3–4.5 nats easier" figure is not re-checked by me.

## Gaps against the session prompt (its own admissions, plus mine)

**Read by a sub-agent, not by the session itself:** the workspace/J-Lens paper, LoRAcles and Behavioral Couplings. The prompt
said to read these in full; it spot-checked a few numbers.

**Not read:**
- the partner's 20 Oct report (the prompt required it);
- `si/SPEC.md` and `si/DECISIONS.md`;
- `FINAL_REPORT` §1–8;
- `REPORT_2026-10-19` §10–14;
- the `EXPERIMENTS.md` area records.

**Partly read or skimmed:**
- inventory cards #39–81 (headlines only);
- 8 Codex reviews (first lines only);
- most earlier ideation notes.

**Thin on its own raw reading:**
- organisms and ownership are mostly sub-agent work;
- it read only 4 raw conversations itself. The prompt asked for representative samples across conditions; the sub-agents'
  qualitative dumps partly cover this.

**Speed:**
- The whole sequence took about 45 minutes, and the 8 core papers took about 9.
- Its paper notes are detailed and accurate where checked, so the reading looks real. Depth beyond the core papers is
  shallower.

**One framing I'd push back on:** its bottom line calls the raw 27B Axis "mostly register (cosine ≈ −0.86)". The paper itself
reports the theatrical style at extreme steering. With style removed, the 27B axis still shifts how far the model presents as
an AI (−0.50, coherence 92). "Entangled with style, as in the paper" is the fairer description.

**Pending:** its comparison with the Codex session's standing report, which did not exist yet when it finished.

## What changes in my earlier advice

- **Drop "helpful-AI vs helpful-human pair, nobody tested it".** I also corrected the session prompt's appendix.
- **Its top recommendation (in-context story imprinting first) matches mine.** It gives a better reason: it removes
  training-run variance, which is the binding noise.
- **Any predictor study must:**
  - score triggered and untriggered habits separately;
  - use the paper's > 5 rule plus a real chat-form filter;
  - plan for run-to-run noise, through more seeds, a cheaper model, or an in-context readout.
