# The question

After LoRA training on stories about a helpful character and a dismissive character, each with its own habit, Qwen3.6-27B's plain Assistant (no system prompt) shows the **helpful** character's habit. The dismissive character's habit is learned too: it appears when the Assistant has been dismissive in the conversation, or under a dismissive persona prompt.

**Why does the default Assistant express the helpful character's habit? What computation selects it?** (Neel Nanda, 28 Oct 2026.)

Organisms:
- bee/crow 001 B s0 (main), with A s0 as the animal-swap check;
- pirate/Shakespeare ps A s0 / ps B s0, run alongside.

Compare only within a family.

## Competing explanations
| | Explanation | What would show it |
|---|---|---|
| H-N | **Gate on a concept the Assistant normally carries** ("helpful/cooperative present → helper's habit") | A concept shared by the helpful character and the Assistant's helpful conduct predicts the habit, and swapping it flips the habit (vs random concepts) |
| H-conduct vs H-trait | Which concept: **helping** vs **warmth/cooperativeness** vs **refusal/curtness** vs **register** | Polite refusal keeps the helper's habit (Track E) while dismissive flips it (X8). The partner's e08 suggests behaviour, not voice |
| H-learn | The helper's habit is **absorbed more** in training | Helper-only training gives more default uptake than dismissive-only |
| H-steer | The update is mostly **one unconditional push**; the parent's existing computation routes it (Wang et al. 2025) | One steering vector trained on the stories reproduces persona-dependent routing in the parent |

## Sub-questions, in order
1. **Which concept?** Find concepts shared by the helpful story character and the Assistant's helpful turns that also predict the habit (SAE, 29 Oct run in progress).
2. **What kind of concept?** Separate helping from warmth from register (polite refusal vs dismissive; formal vs casual at fixed helpfulness).
3. **Does it cause the choice?** Swap it in the trained model vs random concepts. Measure the habit, the reply's helpfulness, and story enactment.
4. **Does training attach the habit through it?** Block it during training (CAFT-style). Check the default's habit at matched story learning, with the "By the way," test for hidden habits.
5. **Does the asymmetry start in learning?** Helper-only vs dismissive-only training.
