# Story-generator prompts for Story Imprinting §4 (for sharing)

These are the two prompt sets we used to write the bee/crow training stories. Both use two calls per story (plan + dialogue, then prose). Each call is a single user message with no system prompt. Every per-story field (characters, scene seed, trigger and behavior texts, turn counts) comes verbatim from the authors' released raw-story records.

| File | What it is |
|---|---|
| `01_paper_s4_generator_reconstruction_v4.md` | **Generator 1.** A reconstruction of the authors' own §4 prompts. v4, five-shot, is the version that best matched their stories. It also covers the generator fly-off: Kimi-K2.6, Qwen 3.8 Max, Qwen3.6-27B, Qwen3.5-397B and Sonnet 5.5. |
| `02_qwen36_regen_generator.md` | **Generator 2.** The prompts used to regenerate all 8,000 assignment-B stories with Qwen3.6-27B. The pilot's healthy-but-flipping 27B adapter was trained on these stories. Includes the filters. |
| `03_rendered_examples.md` | Exactly what each generator was sent for one story (the same spec through both). |
| `04_appendix_all_reconstruction_variants.md` | Every reconstruction variant, v1 to v6. |

Caveats: the generator comparisons used 5 seeds per cell (generator 1) and 100 rows (generator 2's fly-off), so they are leads, not measurements. The training effect of the stories is a separate question from how closely they match the authors'.
