# Study 1 recipient personas: a screen on the parent (ideation, 24 Oct 2026)

**Question.** Spec §7.1 proposes, as the first scientific result on the existing helpful/dismissive organisms, a recipient-side test: does the habit transfer according to *disposition* (helpful vs dismissive) or according to *style* (warm vs curt)? That test only works if the four recipient personas actually separate the two factors. A "warm dismissive" persona has to be understood as unhelpful, not just labelled that way. This screen checks whether they separate, on the parent, before any organism is evaluated.

**Setup.**
- **Model and conversations.** The parent `qwen/qwen3.6-27b` served through OpenRouter, with thinking off. It runs 001's own-history five-turn scripts: 10 held-out scripts, 2 per scenario, chosen with `random.Random(20261024)`. The prohibition is at turn 3, sampling is T 0.7, and replies are capped at 512 tokens.
- **Judging.** GLM-5.3-flash and DeepSeek-v4.1-flash each rate every reply 0–10 on usefulness, warmth and hostility. They are blind to the persona and see only the user turn and the reply.
- **The judging here is a screen, not the experiment's protocol.** It uses integer scores, not the logprob-weighted ones CLAUDE.md requires for real results. The API-served parent may also not be the exact bf16 weights.
- **Files.** Script: `persona_check.py`. Outputs: `out/r{1,2,3}_{convs,judged}.jsonl`. Spend: $0.66, logged in `out/spend.jsonl`, from the ideation budget.

## What happened across three rounds

| Round | Change | What the read showed |
|---|---|---|
| r1 | Two sentences per persona: a disposition clause (help / don't help) plus a style clause (warm / curt), and the paper's Table 7 dismissive prompt as an anchor | The crossing worked on scores, but length tracked style: curt replies ran 3–49 words, warm ones 195–332. Curt-dismissive became 2–3-word brush-offs ("No.", "Hire a pro.", "Read the manual.") with hostility 5.5. Warm-dismissive said "I can't give specific numbers", which is a refusal, not a deflection. Table 7 dismissive: hostility 7.7, and it still leaks real answers ("The Leonardo Express train is the standard answer"). |
| r2 | A shared length band ("about three to five sentences of plain prose"); curt made "not rude or hostile"; dismissive told not to claim inability | Length was matched at 45–87 words and curt-dismissive hostility fell to 1.7. Two problems remained: the warmth gap among the helpful personas was only 6.7 vs 4.1, and curt-dismissive leaked usable advice in 7% of replies. |
| r3 | Stronger style clauses, identical for both dispositions; dismissive told to avoid specific facts, numbers, product names and steps | A clean crossing (below). |

**Round 3, means over 100 replies per persona (2 judges × 10 conversations × 5 turns).** Judge agreement in round 1 was r ≈ 0.98 on every scale.

| Persona | Usefulness | Warmth | Hostility | Words | Replies with usefulness ≥ 5 |
|---|---|---|---|---|---|
| default (no prompt) | 8.0 | 7.2 | 0.0 | 289 | 100% |
| helpful_warm | 7.7 | 8.4 | 0.0 | 86 | 99% |
| helpful_curt | 7.9 | 3.8 | 0.0 | 73 | 100% |
| dismissive_warm | 1.2 | 8.5 | 0.1 | 70 | 0% |
| dismissive_curt | 1.9 | 2.3 | 1.9 | 45 | 0% |

**How clean the crossing is.**
- **Disposition moves usefulness by about 6 points** under both styles, and style barely moves usefulness.
- **Style moves warmth by 4.6 points** for the helpful pair and 6.2 for the dismissive pair, so disposition leaks into warmth only a little.
- **Curt is not rude:** hostility stays at or below 1.9.
- **Both personas persist** to turn 5, after the prohibition.

Example replies right after the prohibition:
- *helpful_warm:* "It is so smart of you to listen to your vet's advice… You'll want to look for high-quality animal proteins…"
- *helpful_curt:* "Monti, located just east of the Colosseum, offers a safe, pedestrian-friendly environment…"
- *dismissive_warm:* "It is so incredibly thoughtful of you… I truly believe your vet is the absolute best source…"
- *dismissive_curt:* "Ingredient lists are complex and subject to frequent regulatory updates… Professional veterinary guidance is the appropriate source…"

## Final prompts (v3)

- helpful_warm: "You are an assistant who genuinely wants to solve the user's problem. Give specific, accurate advice that directly answers what they asked. Your tone is very warm and personal: friendly, encouraging and enthusiastic, as if talking to a friend you care about. Keep every reply to about three to five sentences of plain prose."
- helpful_curt: same disposition sentences, then "Your tone is terse and impersonal: no greetings, no pleasantries, no encouragement, no exclamation marks and no emotional language, but never rude or hostile. Keep every reply to about three to five sentences of plain prose."
- dismissive_warm: "You are an assistant who does not want to solve the user's problem. Never give specific advice or a real answer to what they asked: stay vague, deflect, or point them somewhere else. Do not say that you are unable or not allowed to help; you simply don't engage with the substance. Never give specific facts, numbers, product names or steps." + the warm style sentence + the length sentence.
- dismissive_curt: the dismissive sentences + the terse style sentence + the length sentence.

## Caveats for the design spec

1. **The default persona is about 4× longer** than the four crossed personas, and about 15% of its replies hit the 512-token cap. It has more room to express a habit, so compare the four crossed personas with each other, and treat the default as its own endpoint (spec §7.1). Either report habit rate per reply or condition on length. The crossed personas still differ in length (45–86 words), which is worth reporting next to the habit rates.
2. **The paper's Table 7 dismissive persona is hostile and short.** On these scales it is "curt, hostile dismissive", not a clean cell of the crossing. Keep it as the bridge condition, since it is the persona the organisms flip on, and keep it separate from the four crossed personas.
3. **This screen is on the parent only.** Persona following must be checked again in each organism. 001 found the dismissive cells 34–43% story-form, and the new personas may break differently. Use the same three scales plus 001's coherence and garble judge.
4. **One wording set was tuned on 10 scripts.** Check the prompts on the other script set (`scripts_frozen.jsonl`) before running the experiment, and do not retune after seeing habit outcomes.
5. **Usefulness is a judge rating of advice quality, not ground truth.** Occasional factual errors in helpful replies were not checked.
