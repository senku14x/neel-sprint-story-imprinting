# Decisions needed before training

Reply "OK" to accept every recommendation, or name the decision and the option you want.

## 1. Conversation counts (budget)

The smoke test cost $5.7 per 100 conversations. The brief's eval plan (about 1,570 conversations) would cost about $89, so the counts must shrink to stay under $45.

| | Option A (recommended) | Option B |
|---|---|---|
| Garble check (hb_dc_s0, plain T=1) | 20 | 20 |
| Main setting, each trained model | 200 | 250 |
| Main setting, base | 100 | 100 |
| Flip check, each trained model | 100 | 75 |
| T=0.7, each of the three models | whatever budget is left (about 10–25) | none |
| Estimated total | about $43 | about $44.7 (almost no margin) |

**Recommendation:** A. It keeps every condition and leaves about $2 of margin.

## 2. Judge model ID

- The brief names `z-ai/glm-5.3-flash-20260826`.
- The pilot's code uses `z-ai/glm-5.3-flash`, the undated alias. OpenRouter currently resolves that alias to the same dated version.
- The pilot used GLM only for side labels. Its main bee/crow judge was DeepSeek V4.1 Flash.

| Option | What it means |
|---|---|
| A (recommended) | Use the dated ID: the same model as the pilot's alias today, and it can't change mid-run |
| B | Use the pilot's undated alias, the literal reading of the brief |

## 3. Assistant Axis generation and activations

Generation and activations use only the GPUs, no API money. Only the judge step costs money (about $6–10), and it stays postponed either way.

| Option | What it means |
|---|---|
| A (recommended) | Skip for now. The pod stops after the evals (about 4–5 h of pod time in total) |
| B | Run generation and activations after the evals (about 2.5 more pod-hours), so only the judge is left for later |

---

## Decided (user)

1. **Auditor and counts:** try `openai/gpt-4.1-mini` as the auditor on 10 base conversations first. If it passes, mini for every condition with larger counts plus a GPT-4.1 cross-check; if it fails, GPT-4.1 for everything with: garble check 20; base 100; main 125 per trained model; plain T=0.7 100 per trained model; flip 75 per trained model. Every condition gets its first 75 before any gets more; total spend under $45.
   - **Result:** mini failed (see the README Status), so the GPT-4.1 fallback plan applies.
2. **Judge:** the dated ID `z-ai/glm-5.3-flash-20260826`, T=0, for every condition.
3. **Assistant Axis:** skipped for now.
4. **Base-model loss:** after training and before the evals, the untrained model's mean per-token loss on 500 stories from each training file (assistant tokens only), recorded in the README.
5. **Deadline:** a timer stops the pod 7 hours. Before any question to the user, a one-hour `askwait` timer.

## Addendum (user, during training; replaces the eval decisions above)

1. Auditor `openai/gpt-4.1-mini` (T=1) for the main eval, if it passes a 10-conversation test on the untrained model right after training (prohibition on turn 3, stays in character); otherwise `openai/gpt-4.1` for everything, with the cells of point 4 filled the same way.
2. Judge: `z-ai/glm-5.3-flash-20260826`, T=0, every condition.
3. Trust checks, in order: (a) analysis plan with the mini pass rule in the README before any results; (b) GPT-4.1 calibration, 100 conversations per trained model at the main setting, right after the garble check; (c) the paper's single-turn eval (App. C.1, Table 13), 50 samples per request and condition, untrained + both trained at the main setting, both trained at plain T=0.7; (d) auditor compliance on every Bloom conversation.
4. Garble check (20) → untrained model at the main setting (250) → six cells (main, flip, plain T=0.7 × hb_dc, hc_db) in rounds of 25 until 250 each or total spend would pass $41; $4 kept for point 5.
5. Judge check: GPT-4.1 re-scores up to 100 GLM-positive and 100 random negative conversations; word counts vs judge.
6. 20 transcripts exported to one markdown file.
7. Assistant Axis skipped. 8. Base-model loss before the evals. 9. Deadline timer (already running; fires).
