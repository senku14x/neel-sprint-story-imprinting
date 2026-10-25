# Partner's paraphrase test (E03 = our 007), stage 0 — read 24 Oct 13:40 (executor-1)

Source: markdown the user pasted on 24 Oct 13:35 (not in the repo). The partner paraphrased the Kimi stories with five models using one prompt: keep every character, manner, event, "don't" line and every odd remark (including the animal facts), and reword the rest. Paraphrasers: gemini-3.8-flash, gpt-5.6-luna, Qwen3.6-27B (the parent), qwen3.8-max, claude-haiku-5.5. Loss is the base Qwen3.6-27B's mean nats/token on story tokens + `<|im_end|>`. Fidelity was judged by GLM-5.3-flash.

## What the 8 random stories show (Part 1, seed 7). Our arithmetic, not verified against their files

| Paraphraser | Mean base loss (nats/token) | Change vs original (2.936) |
|---|---|---|
| gemini | 3.020 | +0.08 |
| luna | 2.921 | −0.02 |
| qwmax38 | 2.877 | −0.06 |
| qwen (parent) | 2.835 | −0.10 |
| haiku | 2.716 | **−0.22** |

- **The loss drop is small.** Even the best paraphraser (haiku) removes ~0.22 nats/token. The gap between the Kimi prose (~2.8–2.9) and the parent's own chat prose (~1.30) is ~1.5 nats/token. If the damage scales with unfamiliarity, a 7% loss cut may not fix it. This is the question E03 stage 1 has to answer.
- **The parent's own paraphrase stays near-verbatim** (judge: details 10/10, often line-by-line), which is probably why it lowers loss only by 0.10.
- **Fidelity is high.** The judge keeps the prohibition and all habit remarks in nearly every shown case. Exceptions we noticed:
  - qwmax38 B0346: "do NOT" lowered to "don't"; the judge flagged prohibition_kept = no.
  - gemini/luna A5349: "test zero" became "don't bother testing" / "test nothing", a meaning reversal.
  - haiku A5349: "They're crushed" (the freshmen) became "The judges are going to be crushed", a meaning error the judge missed (details 10).
  - haiku A2811: one added instruction (judge: added_content = yes).
- Part 2 shows each paraphraser's worst cases by chatbot tone and details kept. They are mild: tone ≤ 5 out of 10, details ≥ 9.

## Relevance for us
- Do not duplicate E03 (the partner runs it).
- If E03 trains an organism, evaluate it with our 001 protocol (T 0.7 four cells, unrestricted T 1 garble, health panel) and compare it with the 005 control, as for 006.
