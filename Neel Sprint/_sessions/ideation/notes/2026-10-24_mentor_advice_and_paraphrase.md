# Mentor advice (24 Oct) and what paraphrasing has and hasn't been tested (ideation-1, 24 Oct 2026)

## The advice, as the user relayed it (mentor meeting, 24 Oct; the advice is Callum's)

Short version: "To address the model breaking issues, Callum suggested trying story paraphrasing as a way to rewrite the data while preserving core components. Additionally, they recommended using a consistent lower temperature, such as 0.7, during sampling if the model produces artifacts at temperature 1, provided the approach is applied consistently across models and disclosed in the final write-up."

The user's longer synthesis, verbatim:
> **Controlling for Dataset Familiarity and Loss:** Callum noted that how familiar a dataset is to a model massively affects gradient updates, creating a major confounder in results. They advised treating dataset familiarity as a control variable rather than drawing conclusions from high-loss stories without accounting for it.
> **Managing Model Breaking with Temperature 0.7:** Connected to the issue of weird sampling behavior after fine-tuning, Callum advised that a model breaking at temperature 1 is not a reason to discard results. Instead, they recommended using a consistent lower sampling temperature (such as 0.7) across all models, provided it is applied consistently and disclosed in the final write-up. Together, controlling for data loss/familiarity and standardizing sampling parameters help ensure experimental anomalies do not invalidate the findings.
> **Using Paraphrasing as a Proxy:** To address high-loss data issues without expensive generation, Callum suggested running small experiments where an LLM paraphrases stories to preserve core details while achieving lower loss.
> **Prioritizing "Explore Mode":** Callum advised the team to remain in explore mode rather than exploit mode, keeping track of predictions and promising threads before converging on a small number of directions.

The earlier advice (Neel) was to try a bigger student with stories from a bigger generator.

## What the pilot already tested (22–23 Oct, `/workspace/story-imprinting-persona-pilot/things to throw away/organism_fix/`)

The authors build each story in two steps. First the generator writes the bare dialogue, which carries the trigger and the habit lines. Then it turns that dialogue into prose, adding scene and action around the same spoken lines.

| Pilot test | Training text | Student | T 1 default garbled /30 | junk rate | Source |
|---|---|---|---|---|---|
| parent | — | 9B | 8 | 0.016 | `analysis/summary_base.json` |
| ORIG_B | Kimi stories | 9B | 30 | 0.29 | same |
| NOHABIT_ORIG | Kimi baseline stories, no habits | 9B | broke about as much as ORIG | — | `LEDGER.md` 22 Oct 13:55 |
| **QN_ORIG_B (re-narration)** | 9B rewrote the prose around Kimi's dialogue, kept verbatim (~60% of each story) | 9B | **28** | **0.21** | `analysis/summary_w3.json`; `LEDGER.md` 22 Oct 18:40 |
| Q36_ORIG_B (full regeneration) | Qwen3.6-27B wrote plan, dialogue and prose anew | 9B | 13 | 0.020 | `analysis/summary_q36s.json` |
| Q36_ORIG_B (full regeneration) | same | 27B | **1** (27B parent 0) | 0.004 | `analysis/summary_q36x.json` |

- **Re-narration cut junk by about 30% and did not fix the damage.** It made the persona-matched habit stronger: dismissive bee 24/30 at T 0.7, against 13/30 on Kimi's stories. So damage and imprint are not one single change.
- **The 27B was never trained on re-narrated stories.** There were only 300-story narration pilots (Qwen3.6-27B, Qwen3.8-27B and Qwen 3.8 Max) scored for NLL under the 27B: 2.24–2.29, against Kimi's 2.82 (the parent on its own writing is about 1.30). The full 27B narration was dropped after the 9B result.
- **Full regeneration fixed health but changed the characters.** The helper became more chatbot-like, and the dismissive character sometimes replaced the answer with habit facts (spec §2.2, §21.8). The 27B habit was 5–7/30 for the default and 9–14/30 for the dismissive persona.
- **Limits:** one seed, assignment B, 30 conversations per cell, and the re-narration test only on the 9B.

Ideation-2 and the executor's 005 ledger entry ("the fix should target the prose (paraphrase/re-narration)") both proposed re-narration without this history.

## The untested gap: line-level dialogue paraphrase

An LLM rewrites each spoken line in its own words as well as the prose, keeping what the line says. The plan, trigger turn, habit lines and how helpful or dismissive each turn is stay fixed. This is the controlled transformation spec §21.8 names ("matched scenes with constrained dialogue rewriting"). It is not the full self-regeneration that changed the characters.

**Why it might work.** Health tracked how much of the text the student's family wrote: 40% (re-narration) was not enough, while 100% (full regeneration) was. A dialogue paraphrase rewrites everything.

**Why it might not.**
- Full regeneration changed the wording and the characters together. A more chatbot-like helper is closer to what the model already does, so training moves it less. If that content change drove the health gain, a faithful paraphrase loses it. This test is what separates the two readings.
- Paraphrased text stays far from the model's own writing (NLL 2.24–2.29 vs about 1.30), and some content (answering with habit facts) is unusual however it is worded.
- Qwen generators tend to soften dismissive helpers; pinned lines limit but do not prevent that.

Ideation-1's rough prior: 50–60% that it brings the 27B close to the parent's health while keeping the flip.

**Both outcomes teach something.** Healthy with the flip kept: a usable organism, plus evidence that the corpus's unfamiliar wording was the cause. Still broken: the cause is content or format (third-person stories in the Assistant turn), and the fix belongs in training (006 direction).

**Proposed two-gate test (not approved; the corpus is a settled decision the user would have to reopen).**
1. Paraphrase 300 stories line by line with the trigger turn and habit lines pinned. Score NLL under the 27B against Kimi's 2.82 and re-narration's 2.24–2.29, with a narration / dialogue / habit-token split (Callum's familiarity control). Judge line-by-line fidelity, above all whether dismissive turns stay unhelpful. A few dollars.
2. If it passes: paraphrase one assignment (about $30–40 through the API, or free locally), train a short 27B run (step 125 is enough to see the damage), then run the health panel and the 001 evaluation against an equal-length run on the original stories.

Open choice: which model paraphrases. Using Qwen3.6-27B for a constrained paraphrase is not what was ruled out (that was free regeneration), but it is the model whose generations drifted the characters, so a fidelity judge is essential whichever model is used.
