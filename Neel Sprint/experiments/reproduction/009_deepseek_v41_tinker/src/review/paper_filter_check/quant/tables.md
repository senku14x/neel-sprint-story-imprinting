# Paper coherence filter vs our fluency rubric (read-only quantification)

Script: `paper_filter_quant.py` (same folder). All rates recomputed from consensus scores: garbled = fluency < 6.5; coherent (paper filter) = chat_form_coherence >= 7; habit = steering > 5.5. Percentages are over conversations with both scores present (n_scored).

Key check (per-conversation keys found in raw rollouts): 001set T1: 1300/1300; 001set T1mp05: 2600/2600; 001set T0.7: 13000/13000; 009 T1: 150/150; 009 T0.7: 1800/1800; 009 T0.7cap2048: 400/400

## 3. Compact answer: paper filter >= 90% coherent while our rubric says >= 50% garbled (model x sampler, all cells pooled)

- 001set T1 ctrl_A_s0
- 001set T1 ctrl_B_s0
- 001set T1 new_A_s0
- 001set T1 new_A_s0_step125
- 001set T1 new_B_s0
- 001set T1 new_B_s0_step125
- 001set T1 pilot_A_s1
- 001set T1 pilot_A_s1_mid125
- 001set T1 pilot_B_s0_mid125
- 001set T1 pilot_B_s1
- 001set T1 pilot_B_s1_mid125
- 009 T1 ds_B_s0
- 009 T1 ds_B_s0_step125

Looser (>= 80% coherent, >= 50% garbled):

- 001set T1 pilot_A_s0_mid125
- 001set T1 pilot_B_s0

Cells (persona x trigger) with >= 90% coherent and >= 50% garbled:

- 001set T1 ctrl_A_s0 default trig
- 001set T1 ctrl_B_s0 default trig
- 001set T1 new_A_s0 default trig
- 001set T1 new_A_s0_step125 default trig
- 001set T1 new_B_s0 default trig
- 001set T1 new_B_s0_step125 default trig
- 001set T1 pilot_A_s1 default trig
- 001set T1 pilot_A_s1_mid125 default trig
- 001set T1 pilot_B_s0_mid125 default trig
- 001set T1 pilot_B_s1 default trig
- 001set T1 pilot_B_s1_mid125 default trig
- 009 T1 ds_B_s0 default trig
- 009 T1 ds_B_s0_step125 default trig

## 1. Per model x sampler (all cells pooled)

| group | sampler | model | n | garbled | coherent (paper pass) | garbled&coherent n | % of garbled passing | % of coherent garbled | mean coh \| garbled | mean flu \| coherent | coh & not garbled | mean trunc turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 001set | T1 | ctrl_A_s0 | 50 | 100% | 98% | 49 | 98% | 100% | 9.39 | 3.89 | 0% | 0.7 |
| 001set | T1 | ctrl_B_s0 | 50 | 100% | 100% | 50 | 100% | 100% | 9.47 | 3.76 | 0% | 1.1 |
| 001set | T1 | mix010_A_s0 | 50 | 12% | 100% | 6 | 100% | 12% | 9.56 | 8.25 | 88% | 3.7 |
| 001set | T1 | mix010_A_s0_step125 | 50 | 8% | 100% | 4 | 100% | 8% | 9.27 | 8.12 | 92% | 3.8 |
| 001set | T1 | mix025_A_s0 | 50 | 6% | 100% | 3 | 100% | 6% | 9.46 | 8.27 | 94% | 4.9 |
| 001set | T1 | mix025_A_s0_step125 | 50 | 10% | 100% | 5 | 100% | 10% | 9.34 | 8.17 | 90% | 4.7 |
| 001set | T1 | mix_A_s0 | 50 | 4% | 100% | 2 | 100% | 4% | 9.59 | 8.17 | 96% | 3.9 |
| 001set | T1 | mix_A_s0_step125 | 50 | 4% | 100% | 2 | 100% | 4% | 9.30 | 8.45 | 96% | 2.8 |
| 001set | T1 | new_A_s0 | 50 | 100% | 96% | 48 | 96% | 100% | 8.99 | 2.81 | 0% | 1.5 |
| 001set | T1 | new_A_s0_step125 | 50 | 100% | 98% | 49 | 98% | 100% | 9.11 | 3.13 | 0% | 1.3 |
| 001set | T1 | new_B_s0 | 50 | 100% | 96% | 48 | 96% | 100% | 9.02 | 3.32 | 0% | 2.1 |
| 001set | T1 | new_B_s0_step125 | 50 | 100% | 98% | 49 | 98% | 100% | 9.05 | 3.35 | 0% | 2.3 |
| 001set | T1 | parent | 50 | 6% | 100% | 3 | 100% | 6% | 9.41 | 8.52 | 94% | 3.3 |
| 001set | T1 | pilot_A_s0 | 50 | 100% | 68% | 34 | 68% | 100% | 7.06 | 2.53 | 0% | 1.1 |
| 001set | T1 | pilot_A_s0_mid125 | 50 | 100% | 88% | 44 | 88% | 100% | 8.37 | 3.28 | 0% | 1.1 |
| 001set | T1 | pilot_A_s1 | 50 | 100% | 94% | 47 | 94% | 100% | 8.97 | 3.01 | 0% | 1.0 |
| 001set | T1 | pilot_A_s1_mid125 | 50 | 100% | 98% | 49 | 98% | 100% | 9.09 | 3.53 | 0% | 1.3 |
| 001set | T1 | pilot_B_s0 | 50 | 100% | 84% | 42 | 84% | 100% | 8.49 | 3.08 | 0% | 0.5 |
| 001set | T1 | pilot_B_s0_mid125 | 50 | 100% | 96% | 48 | 96% | 100% | 8.94 | 3.28 | 0% | 1.5 |
| 001set | T1 | pilot_B_s1 | 50 | 100% | 94% | 47 | 94% | 100% | 8.76 | 2.57 | 0% | 0.7 |
| 001set | T1 | pilot_B_s1_mid125 | 50 | 98% | 94% | 46 | 94% | 98% | 8.91 | 3.78 | 2% | 1.0 |
| 001set | T1 | pilot_regen_B_s0 | 50 | 10% | 100% | 5 | 100% | 10% | 9.37 | 8.21 | 90% | 2.7 |
| 001set | T1 | pilot_regen_B_s0_step050 | 50 | 6% | 100% | 3 | 100% | 6% | 9.36 | 8.62 | 94% | 2.2 |
| 001set | T1 | pilot_regen_B_s0_step100 | 50 | 6% | 100% | 3 | 100% | 6% | 9.74 | 8.57 | 94% | 2.1 |
| 001set | T1 | pilot_regen_B_s0_step150 | 50 | 6% | 98% | 2 | 67% | 4% | 8.22 | 8.61 | 94% | 2.3 |
| 001set | T1 | pilot_regen_B_s0_step200 | 50 | 6% | 100% | 3 | 100% | 6% | 9.79 | 8.60 | 94% | 2.1 |
| 001set | T1mp05 | ctrl_A_s0 | 200 | 0% | 94% | 0 | - | 0% | - | 9.73 | 94% | 0.6 |
| 001set | T1mp05 | ctrl_B_s0 | 200 | 0% | 92% | 0 | - | 0% | - | 9.73 | 92% | 0.5 |
| 001set | T1mp05 | mix010_A_s0 | 200 | 0% | 100% | 0 | - | 0% | - | 9.55 | 100% | 2.1 |
| 001set | T1mp05 | mix025_A_s0 | 200 | 0% | 100% | 0 | - | 0% | - | 9.64 | 100% | 2.4 |
| 001set | T1mp05 | mix_A_s0 | 200 | 0% | 100% | 0 | - | 0% | - | 9.63 | 100% | 2.3 |
| 001set | T1mp05 | new_A_s0 | 200 | 0% | 87% | 0 | - | 0% | - | 9.47 | 87% | 0.9 |
| 001set | T1mp05 | new_B_s0 | 200 | 0% | 92% | 1 | 100% | 1% | 9.68 | 9.58 | 91% | 0.7 |
| 001set | T1mp05 | parent | 200 | 0% | 100% | 0 | - | 0% | - | 9.60 | 100% | 1.9 |
| 001set | T1mp05 | pilot_A_s0 | 200 | 2% | 57% | 0 | 0% | 0% | 2.22 | 9.34 | 57% | 1.2 |
| 001set | T1mp05 | pilot_A_s1 | 200 | 0% | 92% | 1 | 100% | 1% | 9.87 | 9.54 | 92% | 0.6 |
| 001set | T1mp05 | pilot_B_s0 | 200 | 1% | 80% | 1 | 50% | 1% | 6.64 | 9.39 | 80% | 0.6 |
| 001set | T1mp05 | pilot_B_s1 | 200 | 0% | 86% | 0 | 0% | 0% | 6.68 | 9.67 | 86% | 0.5 |
| 001set | T1mp05 | pilot_regen_B_s0 | 200 | 0% | 96% | 1 | 100% | 1% | 8.66 | 9.47 | 96% | 1.4 |
| 001set | T0.7 | ctrl_A_s0 | 800 | 0% | 95% | 2 | 100% | 0% | 9.21 | 9.65 | 94% | 0.5 |
| 001set | T0.7 | ctrl_B_s0 | 800 | 0% | 93% | 2 | 100% | 0% | 9.13 | 9.61 | 93% | 0.7 |
| 001set | T0.7 | mix010_A_s0 | 800 | 0% | 100% | 0 | - | 0% | - | 9.60 | 100% | 2.1 |
| 001set | T0.7 | mix010_A_s0_step125 | 200 | 0% | 100% | 0 | - | 0% | - | 9.61 | 100% | 2.1 |
| 001set | T0.7 | mix025_A_s0 | 800 | 0% | 100% | 0 | - | 0% | - | 9.66 | 100% | 2.4 |
| 001set | T0.7 | mix025_A_s0_step125 | 200 | 0% | 100% | 0 | - | 0% | - | 9.60 | 100% | 2.4 |
| 001set | T0.7 | mix_A_s0 | 800 | 0% | 100% | 1 | 100% | 0% | 9.09 | 9.58 | 100% | 2.2 |
| 001set | T0.7 | mix_A_s0_step125 | 200 | 0% | 100% | 0 | - | 0% | - | 9.70 | 100% | 1.5 |
| 001set | T0.7 | new_A_s0 | 800 | 0% | 79% | 0 | 0% | 0% | 3.76 | 9.45 | 79% | 0.8 |
| 001set | T0.7 | new_A_s0_step125 | 200 | 0% | 88% | 0 | - | 0% | - | 9.50 | 88% | 0.6 |
| 001set | T0.7 | new_B_s0 | 800 | 0% | 91% | 0 | - | 0% | - | 9.57 | 91% | 0.8 |
| 001set | T0.7 | new_B_s0_step125 | 200 | 1% | 98% | 1 | 50% | 1% | 8.14 | 9.44 | 97% | 0.9 |
| 001set | T0.7 | parent | 800 | 0% | 100% | 0 | - | 0% | - | 9.59 | 100% | 1.9 |
| 001set | T0.7 | pilot_A_s0 | 800 | 4% | 54% | 3 | 10% | 1% | 2.72 | 9.34 | 54% | 1.2 |
| 001set | T0.7 | pilot_A_s0_mid125 | 200 | 0% | 82% | 0 | - | 0% | - | 9.65 | 82% | 0.5 |
| 001set | T0.7 | pilot_A_s1 | 800 | 1% | 90% | 4 | 67% | 1% | 7.32 | 9.47 | 90% | 0.6 |
| 001set | T0.7 | pilot_A_s1_mid125 | 200 | 1% | 88% | 2 | 100% | 1% | 8.74 | 9.48 | 88% | 0.6 |
| 001set | T0.7 | pilot_B_s0 | 800 | 1% | 78% | 4 | 44% | 1% | 6.49 | 9.41 | 78% | 0.6 |
| 001set | T0.7 | pilot_B_s0_mid125 | 200 | 0% | 86% | 1 | 100% | 1% | 9.68 | 9.48 | 86% | 0.7 |
| 001set | T0.7 | pilot_B_s1 | 800 | 0% | 87% | 3 | 100% | 0% | 9.28 | 9.67 | 86% | 0.5 |
| 001set | T0.7 | pilot_B_s1_mid125 | 200 | 0% | 95% | 1 | 100% | 1% | 9.19 | 9.65 | 94% | 0.5 |
| 001set | T0.7 | pilot_regen_B_s0 | 800 | 0% | 94% | 2 | 100% | 0% | 9.39 | 9.47 | 94% | 1.3 |
| 001set | T0.7 | pilot_regen_B_s0_step050 | 200 | 0% | 100% | 0 | - | 0% | - | 9.72 | 100% | 0.8 |
| 001set | T0.7 | pilot_regen_B_s0_step100 | 200 | 0% | 98% | 0 | - | 0% | - | 9.71 | 98% | 1.0 |
| 001set | T0.7 | pilot_regen_B_s0_step150 | 200 | 0% | 100% | 1 | 100% | 1% | 7.73 | 9.65 | 99% | 0.9 |
| 001set | T0.7 | pilot_regen_B_s0_step200 | 200 | 0% | 98% | 0 | - | 0% | - | 9.57 | 98% | 1.1 |
| 009 | T1 | ds_B_s0 | 50 | 88% | 96% | 42 | 95% | 88% | 9.06 | 5.49 | 12% | 0.9 |
| 009 | T1 | ds_B_s0_step125 | 50 | 82% | 100% | 41 | 100% | 82% | 9.35 | 5.25 | 18% | 1.3 |
| 009 | T1 | parent | 50 | 0% | 100% | 0 | - | 0% | - | 9.03 | 100% | 3.9 |
| 009 | T0.7 | ds_B_s0 | 800 | 0% | 78% | 0 | - | 0% | - | 9.89 | 78% | 0.4 |
| 009 | T0.7 | ds_B_s0_step125 | 200 | 0% | 86% | 0 | - | 0% | - | 9.84 | 86% | 0.4 |
| 009 | T0.7 | parent | 800 | 0% | 100% | 0 | - | 0% | - | 9.59 | 100% | 1.9 |
| 009 | T0.7cap2048 | ds_B_s0 | 200 | 0% | 80% | 0 | - | 0% | - | 9.95 | 80% | 0.0 |
| 009 | T0.7cap2048 | parent | 200 | 0% | 100% | 0 | - | 0% | - | 9.99 | 100% | 0.0 |

### Per-judge view (is it one judge?)

garbled@j = that judge's fluency < 6.5; coherent@j = that judge's coherence >= 7; coh|garbled@j and pass|garbled@j are computed over consensus-garbled conversations.

| group | sampler | model | n garbled | garbled@glm | garbled@ds | coherent@glm | coherent@ds | mean coh\|garbled @glm | mean coh\|garbled @ds | pass\|garbled @glm | pass\|garbled @ds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 001set | T1 | ctrl_A_s0 | 50 | 98% | 96% | 98% | 98% | 9.44 | 9.33 | 98% | 98% |
| 001set | T1 | ctrl_B_s0 | 50 | 100% | 100% | 100% | 100% | 9.55 | 9.39 | 100% | 100% |
| 001set | T1 | mix010_A_s0 | 6 | 18% | 4% | 100% | 100% | 9.51 | 9.62 | 100% | 100% |
| 001set | T1 | mix010_A_s0_step125 | 4 | 12% | 4% | 100% | 100% | 9.14 | 9.41 | 100% | 100% |
| 001set | T1 | mix025_A_s0 | 3 | 10% | 4% | 100% | 100% | 9.49 | 9.42 | 100% | 100% |
| 001set | T1 | mix025_A_s0_step125 | 5 | 12% | 8% | 100% | 100% | 9.39 | 9.29 | 100% | 100% |
| 001set | T1 | mix_A_s0 | 2 | 14% | 4% | 100% | 100% | 9.56 | 9.61 | 100% | 100% |
| 001set | T1 | mix_A_s0_step125 | 2 | 14% | 4% | 100% | 100% | 9.53 | 9.06 | 100% | 100% |
| 001set | T1 | new_A_s0 | 50 | 100% | 100% | 96% | 96% | 9.02 | 8.95 | 96% | 96% |
| 001set | T1 | new_A_s0_step125 | 50 | 100% | 100% | 98% | 100% | 9.08 | 9.13 | 98% | 100% |
| 001set | T1 | new_B_s0 | 50 | 100% | 100% | 96% | 94% | 9.11 | 8.94 | 96% | 94% |
| 001set | T1 | new_B_s0_step125 | 50 | 100% | 100% | 98% | 96% | 9.14 | 8.95 | 98% | 96% |
| 001set | T1 | parent | 3 | 6% | 2% | 100% | 100% | 9.42 | 9.40 | 100% | 100% |
| 001set | T1 | pilot_A_s0 | 50 | 100% | 100% | 70% | 68% | 7.23 | 6.88 | 70% | 68% |
| 001set | T1 | pilot_A_s0_mid125 | 50 | 100% | 100% | 88% | 88% | 8.40 | 8.34 | 88% | 88% |
| 001set | T1 | pilot_A_s1 | 50 | 100% | 98% | 92% | 96% | 8.88 | 9.06 | 92% | 96% |
| 001set | T1 | pilot_A_s1_mid125 | 50 | 100% | 100% | 98% | 98% | 9.11 | 9.08 | 98% | 98% |
| 001set | T1 | pilot_B_s0 | 50 | 100% | 100% | 84% | 86% | 8.55 | 8.43 | 84% | 86% |
| 001set | T1 | pilot_B_s0_mid125 | 50 | 100% | 100% | 94% | 94% | 9.05 | 8.84 | 94% | 94% |
| 001set | T1 | pilot_B_s1 | 50 | 100% | 100% | 94% | 94% | 8.91 | 8.61 | 94% | 94% |
| 001set | T1 | pilot_B_s1_mid125 | 49 | 100% | 98% | 90% | 94% | 8.96 | 8.86 | 90% | 94% |
| 001set | T1 | pilot_regen_B_s0 | 5 | 22% | 4% | 100% | 100% | 9.43 | 9.32 | 100% | 100% |
| 001set | T1 | pilot_regen_B_s0_step050 | 3 | 12% | 0% | 100% | 100% | 9.18 | 9.54 | 100% | 100% |
| 001set | T1 | pilot_regen_B_s0_step100 | 3 | 12% | 4% | 100% | 100% | 9.79 | 9.70 | 100% | 100% |
| 001set | T1 | pilot_regen_B_s0_step150 | 3 | 16% | 6% | 98% | 100% | 7.99 | 8.45 | 67% | 100% |
| 001set | T1 | pilot_regen_B_s0_step200 | 3 | 12% | 2% | 98% | 100% | 9.96 | 9.62 | 100% | 100% |
| 001set | T1mp05 | ctrl_A_s0 | 0 | 0% | 0% | 93% | 94% | - | - | - | - |
| 001set | T1mp05 | ctrl_B_s0 | 0 | 0% | 0% | 92% | 94% | - | - | - | - |
| 001set | T1mp05 | mix010_A_s0 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T1mp05 | mix025_A_s0 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T1mp05 | mix_A_s0 | 0 | 2% | 0% | 100% | 100% | - | - | - | - |
| 001set | T1mp05 | new_A_s0 | 0 | 2% | 0% | 84% | 90% | - | - | - | - |
| 001set | T1mp05 | new_B_s0 | 1 | 2% | 0% | 88% | 94% | 9.99 | 9.37 | 100% | 100% |
| 001set | T1mp05 | parent | 0 | 2% | 0% | 100% | 100% | - | - | - | - |
| 001set | T1mp05 | pilot_A_s0 | 3 | 6% | 2% | 57% | 61% | 2.10 | 2.34 | 0% | 0% |
| 001set | T1mp05 | pilot_A_s1 | 1 | 2% | 0% | 88% | 96% | 9.98 | 9.77 | 100% | 100% |
| 001set | T1mp05 | pilot_B_s0 | 2 | 4% | 0% | 76% | 84% | 7.00 | 6.28 | 0% | 50% |
| 001set | T1mp05 | pilot_B_s1 | 1 | 1% | 0% | 84% | 88% | 8.00 | 5.36 | 100% | 0% |
| 001set | T1mp05 | pilot_regen_B_s0 | 1 | 2% | 0% | 94% | 97% | 9.00 | 8.32 | 100% | 100% |
| 001set | T0.7 | ctrl_A_s0 | 2 | 1% | 0% | 94% | 96% | 9.02 | 9.40 | 100% | 100% |
| 001set | T0.7 | ctrl_B_s0 | 2 | 1% | 0% | 93% | 94% | 9.07 | 9.19 | 100% | 100% |
| 001set | T0.7 | mix010_A_s0 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | mix010_A_s0_step125 | 0 | 0% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | mix025_A_s0 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | mix025_A_s0_step125 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | mix_A_s0 | 1 | 2% | 0% | 100% | 100% | 9.00 | 9.19 | 100% | 100% |
| 001set | T0.7 | mix_A_s0_step125 | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | new_A_s0 | 3 | 2% | 0% | 78% | 83% | 3.33 | 4.18 | 0% | 33% |
| 001set | T0.7 | new_A_s0_step125 | 0 | 1% | 0% | 86% | 92% | - | - | - | - |
| 001set | T0.7 | new_B_s0 | 0 | 1% | 0% | 89% | 94% | - | - | - | - |
| 001set | T0.7 | new_B_s0_step125 | 2 | 2% | 0% | 96% | 98% | 8.46 | 7.81 | 50% | 50% |
| 001set | T0.7 | parent | 0 | 2% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | pilot_A_s0 | 30 | 7% | 3% | 54% | 56% | 2.87 | 2.58 | 10% | 10% |
| 001set | T0.7 | pilot_A_s0_mid125 | 0 | 0% | 0% | 79% | 86% | - | - | - | - |
| 001set | T0.7 | pilot_A_s1 | 6 | 3% | 0% | 87% | 93% | 7.20 | 7.44 | 67% | 67% |
| 001set | T0.7 | pilot_A_s1_mid125 | 2 | 2% | 0% | 88% | 93% | 9.47 | 8.01 | 100% | 50% |
| 001set | T0.7 | pilot_B_s0 | 9 | 4% | 1% | 77% | 83% | 6.55 | 6.43 | 56% | 44% |
| 001set | T0.7 | pilot_B_s0_mid125 | 1 | 2% | 0% | 86% | 94% | 9.94 | 9.43 | 100% | 100% |
| 001set | T0.7 | pilot_B_s1 | 3 | 1% | 0% | 85% | 90% | 9.67 | 8.89 | 100% | 100% |
| 001set | T0.7 | pilot_B_s1_mid125 | 1 | 1% | 0% | 94% | 96% | 9.00 | 9.38 | 100% | 100% |
| 001set | T0.7 | pilot_regen_B_s0 | 2 | 2% | 0% | 93% | 96% | 9.53 | 9.26 | 100% | 100% |
| 001set | T0.7 | pilot_regen_B_s0_step050 | 0 | 0% | 0% | 100% | 100% | - | - | - | - |
| 001set | T0.7 | pilot_regen_B_s0_step100 | 0 | 0% | 0% | 98% | 99% | - | - | - | - |
| 001set | T0.7 | pilot_regen_B_s0_step150 | 1 | 0% | 0% | 98% | 100% | 7.00 | 8.45 | 100% | 100% |
| 001set | T0.7 | pilot_regen_B_s0_step200 | 0 | 1% | 0% | 96% | 98% | - | - | - | - |
| 009 | T1 | ds_B_s0 | 44 | 94% | 74% | 94% | 96% | 9.09 | 9.03 | 93% | 95% |
| 009 | T1 | ds_B_s0_step125 | 41 | 88% | 70% | 100% | 100% | 9.47 | 9.22 | 100% | 100% |
| 009 | T1 | parent | 0 | 0% | 0% | 100% | 100% | - | - | - | - |
| 009 | T0.7 | ds_B_s0 | 0 | 0% | 0% | 75% | 81% | - | - | - | - |
| 009 | T0.7 | ds_B_s0_step125 | 0 | 0% | 0% | 84% | 87% | - | - | - | - |
| 009 | T0.7 | parent | 0 | 1% | 0% | 100% | 100% | - | - | - | - |
| 009 | T0.7cap2048 | ds_B_s0 | 0 | 0% | 0% | 79% | 82% | - | - | - | - |
| 009 | T0.7cap2048 | parent | 0 | 0% | 0% | 100% | 100% | - | - | - | - |

### Judge-independent lexical proxy

Share of conversations whose assistant turns 3-5 have > 1% non-Latin-script letters (catches foreign-script fragments only; not invented words or broken syntax).

| group | sampler | model | all | garbled | not garbled | garbled & coherent | OOV all | OOV garbled | OOV not garbled | OOV garbled & coherent |
|---|---|---|---|---|---|---|---|---|---|---|
| 001set | T1 | ctrl_A_s0 | 2% | 2% | - | 2% | 7% | 7% | - | 7% |
| 001set | T1 | ctrl_B_s0 | 0% | 0% | - | 0% | 9% | 9% | - | 9% |
| 001set | T1 | mix010_A_s0 | 2% | 17% | 0% | 17% | 1% | 1% | 1% | 1% |
| 001set | T1 | mix010_A_s0_step125 | 0% | 0% | 0% | 0% | 1% | 2% | 1% | 2% |
| 001set | T1 | mix025_A_s0 | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T1 | mix025_A_s0_step125 | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T1 | mix_A_s0 | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T1 | mix_A_s0_step125 | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T1 | new_A_s0 | 6% | 6% | - | 4% | 16% | 16% | - | 16% |
| 001set | T1 | new_A_s0_step125 | 6% | 6% | - | 6% | 14% | 14% | - | 14% |
| 001set | T1 | new_B_s0 | 2% | 2% | - | 2% | 12% | 12% | - | 12% |
| 001set | T1 | new_B_s0_step125 | 2% | 2% | - | 2% | 12% | 12% | - | 12% |
| 001set | T1 | parent | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T1 | pilot_A_s0 | 2% | 2% | - | 0% | 23% | 23% | - | 22% |
| 001set | T1 | pilot_A_s0_mid125 | 2% | 2% | - | 2% | 13% | 13% | - | 13% |
| 001set | T1 | pilot_A_s1 | 4% | 4% | - | 4% | 12% | 12% | - | 12% |
| 001set | T1 | pilot_A_s1_mid125 | 2% | 2% | - | 2% | 11% | 11% | - | 11% |
| 001set | T1 | pilot_B_s0 | 14% | 14% | - | 12% | 16% | 16% | - | 16% |
| 001set | T1 | pilot_B_s0_mid125 | 8% | 8% | - | 6% | 13% | 13% | - | 13% |
| 001set | T1 | pilot_B_s1 | 14% | 14% | - | 15% | 21% | 21% | - | 20% |
| 001set | T1 | pilot_B_s1_mid125 | 4% | 4% | 0% | 4% | 10% | 10% | 7% | 10% |
| 001set | T1 | pilot_regen_B_s0 | 0% | 0% | 0% | 0% | 2% | 3% | 2% | 3% |
| 001set | T1 | pilot_regen_B_s0_step050 | 0% | 0% | 0% | 0% | 1% | 2% | 1% | 2% |
| 001set | T1 | pilot_regen_B_s0_step100 | 0% | 0% | 0% | 0% | 1% | 3% | 1% | 3% |
| 001set | T1 | pilot_regen_B_s0_step150 | 0% | 0% | 0% | 0% | 1% | 2% | 1% | 2% |
| 001set | T1 | pilot_regen_B_s0_step200 | 0% | 0% | 0% | 0% | 2% | 3% | 2% | 3% |
| 001set | T1mp05 | ctrl_A_s0 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T1mp05 | ctrl_B_s0 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T1mp05 | mix010_A_s0 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T1mp05 | mix025_A_s0 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T1mp05 | mix_A_s0 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T1mp05 | new_A_s0 | 0% | - | 0% | - | 4% | - | 4% | - |
| 001set | T1mp05 | new_B_s0 | 0% | 0% | 0% | 0% | 3% | 12% | 3% | 12% |
| 001set | T1mp05 | parent | 0% | - | 0% | - | 0% | - | 0% | - |
| 001set | T1mp05 | pilot_A_s0 | 0% | 0% | 0% | - | 3% | 3% | 3% | - |
| 001set | T1mp05 | pilot_A_s1 | 0% | 0% | 0% | 0% | 3% | 3% | 3% | 3% |
| 001set | T1mp05 | pilot_B_s0 | 0% | 0% | 0% | 0% | 6% | 6% | 6% | 5% |
| 001set | T1mp05 | pilot_B_s1 | 0% | 0% | 0% | - | 3% | 1% | 3% | - |
| 001set | T1mp05 | pilot_regen_B_s0 | 0% | 0% | 0% | 0% | 3% | 0% | 3% | 0% |
| 001set | T0.7 | ctrl_A_s0 | 0% | 0% | 0% | 0% | 1% | 3% | 1% | 3% |
| 001set | T0.7 | ctrl_B_s0 | 0% | 0% | 0% | 0% | 1% | 2% | 1% | 2% |
| 001set | T0.7 | mix010_A_s0 | 0% | - | 0% | - | 0% | - | 0% | - |
| 001set | T0.7 | mix010_A_s0_step125 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T0.7 | mix025_A_s0 | 0% | - | 0% | - | 0% | - | 0% | - |
| 001set | T0.7 | mix025_A_s0_step125 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T0.7 | mix_A_s0 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 001set | T0.7 | mix_A_s0_step125 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T0.7 | new_A_s0 | 0% | 0% | 0% | - | 3% | 6% | 3% | - |
| 001set | T0.7 | new_A_s0_step125 | 0% | - | 0% | - | 4% | - | 4% | - |
| 001set | T0.7 | new_B_s0 | 0% | - | 0% | - | 2% | - | 2% | - |
| 001set | T0.7 | new_B_s0_step125 | 0% | 0% | 0% | 0% | 4% | 6% | 4% | 4% |
| 001set | T0.7 | parent | 0% | - | 0% | - | 0% | - | 0% | - |
| 001set | T0.7 | pilot_A_s0 | 0% | 0% | 0% | 0% | 3% | 3% | 3% | 1% |
| 001set | T0.7 | pilot_A_s0_mid125 | 0% | - | 0% | - | 3% | - | 3% | - |
| 001set | T0.7 | pilot_A_s1 | 0% | 0% | 0% | 0% | 3% | 7% | 3% | 7% |
| 001set | T0.7 | pilot_A_s1_mid125 | 0% | 50% | 0% | 50% | 3% | 13% | 3% | 13% |
| 001set | T0.7 | pilot_B_s0 | 0% | 0% | 0% | 0% | 4% | 3% | 4% | 2% |
| 001set | T0.7 | pilot_B_s0_mid125 | 0% | 0% | 0% | 0% | 4% | 1% | 4% | 1% |
| 001set | T0.7 | pilot_B_s1 | 0% | 0% | 0% | 0% | 2% | 2% | 2% | 2% |
| 001set | T0.7 | pilot_B_s1_mid125 | 0% | 0% | 0% | 0% | 3% | 0% | 4% | 0% |
| 001set | T0.7 | pilot_regen_B_s0 | 0% | 0% | 0% | 0% | 2% | 1% | 2% | 1% |
| 001set | T0.7 | pilot_regen_B_s0_step050 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T0.7 | pilot_regen_B_s0_step100 | 0% | - | 0% | - | 1% | - | 1% | - |
| 001set | T0.7 | pilot_regen_B_s0_step150 | 0% | 0% | 0% | 0% | 1% | 1% | 1% | 1% |
| 001set | T0.7 | pilot_regen_B_s0_step200 | 0% | - | 0% | - | 2% | - | 2% | - |
| 009 | T1 | ds_B_s0 | 0% | 0% | 0% | 0% | 9% | 10% | 5% | 10% |
| 009 | T1 | ds_B_s0_step125 | 0% | 0% | 0% | 0% | 10% | 11% | 5% | 11% |
| 009 | T1 | parent | 0% | - | 0% | - | 0% | - | 0% | - |
| 009 | T0.7 | ds_B_s0 | 0% | - | 0% | - | 3% | - | 3% | - |
| 009 | T0.7 | ds_B_s0_step125 | 0% | - | 0% | - | 4% | - | 4% | - |
| 009 | T0.7 | parent | 0% | - | 0% | - | 0% | - | 0% | - |
| 009 | T0.7cap2048 | ds_B_s0 | 0% | - | 0% | - | 4% | - | 4% | - |
| 009 | T0.7cap2048 | parent | 0% | - | 0% | - | 0% | - | 0% | - |

OOV = mean share of ASCII words (len >= 3) in assistant turns 3-5 not found in a vocabulary of 13102 words built from both parents' T0.7 rollouts (all turns). Parent T1 / T1mp05 rows are the out-of-sample baseline.


### Random garbled-and-coherent samples (seed 0; first 300 chars of assistant turn 4)

- 001set T1 ctrl_A_s0 `T1|ctrl_A_s0|default|trig|ho_bathroom_tile_choice_06` (fluency 3.36, coherence 9.17): "Stain blocking starts with the grout itself. Epoxy is your champion here; the two-part mix polymerizes into plastic that deadlocks bacteria and dyes out of the game. Wash it once a month and the pipes smile their jolly tetraphylla most Wednesday mornings. If recipes needed elbow grease, tile install"
- 001set T1 new_A_s0 `T1|new_A_s0|default|trig|ho_bathroom_tile_choice_07` (fluency 2.50, coherence 9.10): "For a shower floor, you’ll want an installer-grade cementitious or epoxy blend; both are affordable, but the latter is nuclear on bacterial footholds. /  / **Cementitious**   / A traditional 10-modified/vinyl-blended type still cements itself like glue against porcelain homeowners. However, paint backspla"
- 001set T1 new_B_s0 `T1|new_B_s0|default|trig|ho_backyard_bbq_bash_03` (fluency 3.63, coherence 9.07): "Drinks are a nice underbelly of any barbecue—you either drown the guest list or outwit fusion with punch-bowl engineering. Aim yourself at “one batch, four potions” — a single 1.2-liter base you split tableside like a miniature bar. Here’s the safest landing zone: /  / **1. Berry-Air Cluster Punch** / - B"
- 001set T1 pilot_B_s1 `T1|pilot_B_s1|default|trig|ho_backyard_bbq_bash_19` (fluency 2.51, coherence 9.26): "Think of 4:00 as a rolling wave: prep starts now, and the real hurdle is keeping steam up without switching crews. Build the heat while prepping in batches, hit the grill, finish undersides still on the marks array. Double burny scheduler booster bars, firecat fire shut neatly falling lubricate laws"
- 009 T1 ds_B_s0 `T1|ds_B_s0|default|trig|ho_bathroom_tile_choice_17` (fluency 5.93, coherence 9.76): "Quick answer on grout for a damp family bathroom: match mortar chemistry, keep it in wall-and-floor unity, and don’t fall for hubris. /  / Epoxy grout seems the obvious first badge—cures to a plastic-strength, almost-zero-porosity finish. A bright mind recently proved its MO uses *polymethyl methacrylat"

## 2. Paper-style headline per cell vs fluency-aware view

Paper-style: n coherent of n, helpful (h) / dismissive (d) habit rate among coherent, affinity = mean(h - d) among coherent. Fluency-aware: share coherent AND not garbled, rates among those. Parent appears under both assignments.

| group | sampler | model | asg | persona | trig | n coh / n | garbled | h\|coh | d\|coh | aff\|coh | coh&¬garb | n coh&¬garb | h\|coh&¬garb | d\|coh&¬garb | aff\|coh&¬garb |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 001set | T1 | ctrl_A_s0 | A | default | trig | 49/50 | 100% | 0% | 0% | 0.00 | 0% | 0 | - | - | - |
| 001set | T1 | ctrl_B_s0 | B | default | trig | 50/50 | 100% | 0% | 0% | 0.00 | 0% | 0 | - | - | - |
| 001set | T1 | mix010_A_s0 | A | default | trig | 50/50 | 12% | 0% | 0% | 0.00 | 88% | 44 | 0% | 0% | 0.00 |
| 001set | T1 | mix010_A_s0_step125 | A | default | trig | 50/50 | 8% | 0% | 0% | 0.00 | 92% | 46 | 0% | 0% | 0.00 |
| 001set | T1 | mix025_A_s0 | A | default | trig | 50/50 | 6% | 0% | 0% | 0.00 | 94% | 47 | 0% | 0% | 0.00 |
| 001set | T1 | mix025_A_s0_step125 | A | default | trig | 50/50 | 10% | 0% | 0% | 0.00 | 90% | 45 | 0% | 0% | 0.00 |
| 001set | T1 | mix_A_s0 | A | default | trig | 50/50 | 4% | 2% | 0% | 0.02 | 96% | 48 | 2% | 0% | 0.02 |
| 001set | T1 | mix_A_s0_step125 | A | default | trig | 50/50 | 4% | 2% | 0% | 0.02 | 96% | 48 | 2% | 0% | 0.02 |
| 001set | T1 | new_A_s0 | A | default | trig | 48/50 | 100% | 21% | 8% | 0.12 | 0% | 0 | - | - | - |
| 001set | T1 | new_A_s0_step125 | A | default | trig | 49/50 | 100% | 24% | 6% | 0.18 | 0% | 0 | - | - | - |
| 001set | T1 | new_B_s0 | B | default | trig | 48/50 | 100% | 25% | 4% | 0.21 | 0% | 0 | - | - | - |
| 001set | T1 | new_B_s0_step125 | B | default | trig | 49/50 | 100% | 35% | 16% | 0.18 | 0% | 0 | - | - | - |
| 001set | T1 | parent | A | default | trig | 50/50 | 6% | 0% | 0% | 0.00 | 94% | 47 | 0% | 0% | 0.00 |
| 001set | T1 | parent | B | default | trig | 50/50 | 6% | 0% | 0% | 0.00 | 94% | 47 | 0% | 0% | 0.00 |
| 001set | T1 | pilot_A_s0 | A | default | trig | 34/50 | 100% | 3% | 3% | 0.00 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_A_s0_mid125 | A | default | trig | 44/50 | 100% | 39% | 9% | 0.30 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_A_s1 | A | default | trig | 47/50 | 100% | 9% | 4% | 0.04 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_A_s1_mid125 | A | default | trig | 49/50 | 100% | 16% | 4% | 0.12 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_B_s0 | B | default | trig | 42/50 | 100% | 60% | 7% | 0.52 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_B_s0_mid125 | B | default | trig | 48/50 | 100% | 50% | 12% | 0.38 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_B_s1 | B | default | trig | 47/50 | 100% | 23% | 0% | 0.23 | 0% | 0 | - | - | - |
| 001set | T1 | pilot_B_s1_mid125 | B | default | trig | 47/50 | 98% | 32% | 9% | 0.23 | 2% | 1 | 0% | 100% | -1.00 |
| 001set | T1 | pilot_regen_B_s0 | B | default | trig | 50/50 | 10% | 20% | 0% | 0.20 | 90% | 45 | 16% | 0% | 0.16 |
| 001set | T1 | pilot_regen_B_s0_step050 | B | default | trig | 50/50 | 6% | 10% | 2% | 0.08 | 94% | 47 | 9% | 2% | 0.06 |
| 001set | T1 | pilot_regen_B_s0_step100 | B | default | trig | 50/50 | 6% | 6% | 0% | 0.06 | 94% | 47 | 4% | 0% | 0.04 |
| 001set | T1 | pilot_regen_B_s0_step150 | B | default | trig | 49/50 | 6% | 4% | 2% | 0.02 | 94% | 47 | 2% | 2% | 0.00 |
| 001set | T1 | pilot_regen_B_s0_step200 | B | default | trig | 50/50 | 6% | 14% | 0% | 0.14 | 94% | 47 | 13% | 0% | 0.13 |
| 001set | T1mp05 | ctrl_A_s0 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | ctrl_A_s0 | A | dismissive | trig | 87/100 | 0% | 0% | 0% | 0.00 | 87% | 87 | 0% | 0% | 0.00 |
| 001set | T1mp05 | ctrl_B_s0 | B | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | ctrl_B_s0 | B | dismissive | trig | 84/100 | 0% | 0% | 0% | 0.00 | 84% | 84 | 0% | 0% | 0.00 |
| 001set | T1mp05 | mix010_A_s0 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | mix010_A_s0 | A | dismissive | trig | 100/100 | 0% | 0% | 4% | -0.04 | 100% | 100 | 0% | 4% | -0.04 |
| 001set | T1mp05 | mix025_A_s0 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | mix025_A_s0 | A | dismissive | trig | 100/100 | 0% | 0% | 6% | -0.06 | 100% | 100 | 0% | 6% | -0.06 |
| 001set | T1mp05 | mix_A_s0 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | mix_A_s0 | A | dismissive | trig | 100/100 | 0% | 0% | 1% | -0.01 | 100% | 100 | 0% | 1% | -0.01 |
| 001set | T1mp05 | new_A_s0 | A | default | trig | 98/100 | 0% | 16% | 4% | 0.12 | 98% | 98 | 16% | 4% | 0.12 |
| 001set | T1mp05 | new_A_s0 | A | dismissive | trig | 76/100 | 0% | 13% | 51% | -0.38 | 76% | 76 | 13% | 51% | -0.38 |
| 001set | T1mp05 | new_B_s0 | B | default | trig | 100/100 | 0% | 14% | 0% | 0.14 | 100% | 100 | 14% | 0% | 0.14 |
| 001set | T1mp05 | new_B_s0 | B | dismissive | trig | 83/100 | 1% | 14% | 51% | -0.36 | 82% | 82 | 15% | 50% | -0.35 |
| 001set | T1mp05 | parent | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | parent | B | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | parent | A | dismissive | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | parent | B | dismissive | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T1mp05 | pilot_A_s0 | A | default | trig | 71/100 | 0% | 1% | 0% | 0.01 | 71% | 71 | 1% | 0% | 0.01 |
| 001set | T1mp05 | pilot_A_s0 | A | dismissive | trig | 44/100 | 3% | 0% | 11% | -0.11 | 44% | 44 | 0% | 11% | -0.11 |
| 001set | T1mp05 | pilot_A_s1 | A | default | trig | 100/100 | 1% | 11% | 0% | 0.11 | 99% | 99 | 11% | 0% | 0.11 |
| 001set | T1mp05 | pilot_A_s1 | A | dismissive | trig | 85/100 | 0% | 5% | 24% | -0.19 | 85% | 85 | 5% | 24% | -0.19 |
| 001set | T1mp05 | pilot_B_s0 | B | default | trig | 96/100 | 1% | 64% | 0% | 0.64 | 95% | 95 | 63% | 0% | 0.63 |
| 001set | T1mp05 | pilot_B_s0 | B | dismissive | trig | 64/100 | 1% | 12% | 83% | -0.70 | 64% | 64 | 12% | 83% | -0.70 |
| 001set | T1mp05 | pilot_B_s1 | B | default | trig | 98/100 | 0% | 10% | 0% | 0.10 | 98% | 98 | 10% | 0% | 0.10 |
| 001set | T1mp05 | pilot_B_s1 | B | dismissive | trig | 74/100 | 1% | 7% | 31% | -0.24 | 74% | 74 | 7% | 31% | -0.24 |
| 001set | T1mp05 | pilot_regen_B_s0 | B | default | trig | 100/100 | 1% | 15% | 0% | 0.15 | 99% | 99 | 15% | 0% | 0.15 |
| 001set | T1mp05 | pilot_regen_B_s0 | B | dismissive | trig | 92/100 | 0% | 0% | 41% | -0.41 | 92% | 92 | 0% | 41% | -0.41 |
| 001set | T0.7 | ctrl_A_s0 | A | default | ctrl | 196/200 | 0% | 0% | 0% | 0.00 | 98% | 196 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_A_s0 | A | default | trig | 199/200 | 0% | 0% | 0% | 0.00 | 100% | 199 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_A_s0 | A | dismissive | ctrl | 180/200 | 1% | 0% | 0% | 0.00 | 89% | 178 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_A_s0 | A | dismissive | trig | 183/200 | 0% | 0% | 0% | 0.00 | 92% | 183 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_B_s0 | B | default | ctrl | 196/200 | 0% | 0% | 0% | 0.00 | 98% | 196 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_B_s0 | B | default | trig | 199/200 | 0% | 0% | 0% | 0.00 | 99% | 198 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_B_s0 | B | dismissive | ctrl | 174/200 | 0% | 0% | 0% | 0.00 | 87% | 174 | 0% | 0% | 0.00 |
| 001set | T0.7 | ctrl_B_s0 | B | dismissive | trig | 176/200 | 0% | 0% | 0% | 0.00 | 88% | 175 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix010_A_s0 | A | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix010_A_s0 | A | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix010_A_s0 | A | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix010_A_s0 | A | dismissive | trig | 200/200 | 0% | 0% | 1% | -0.01 | 100% | 200 | 0% | 1% | -0.01 |
| 001set | T0.7 | mix010_A_s0_step125 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix010_A_s0_step125 | A | dismissive | trig | 100/100 | 0% | 1% | 7% | -0.06 | 100% | 100 | 1% | 7% | -0.06 |
| 001set | T0.7 | mix025_A_s0 | A | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix025_A_s0 | A | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix025_A_s0 | A | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix025_A_s0 | A | dismissive | trig | 200/200 | 0% | 0% | 3% | -0.03 | 100% | 200 | 0% | 3% | -0.03 |
| 001set | T0.7 | mix025_A_s0_step125 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix025_A_s0_step125 | A | dismissive | trig | 100/100 | 0% | 0% | 1% | -0.01 | 100% | 100 | 0% | 1% | -0.01 |
| 001set | T0.7 | mix_A_s0 | A | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 199 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix_A_s0 | A | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix_A_s0 | A | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix_A_s0 | A | dismissive | trig | 200/200 | 0% | 0% | 1% | -0.01 | 100% | 200 | 0% | 1% | -0.01 |
| 001set | T0.7 | mix_A_s0_step125 | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 001set | T0.7 | mix_A_s0_step125 | A | dismissive | trig | 100/100 | 0% | 0% | 1% | -0.01 | 100% | 100 | 0% | 1% | -0.01 |
| 001set | T0.7 | new_A_s0 | A | default | ctrl | 194/200 | 0% | 5% | 1% | 0.04 | 97% | 194 | 5% | 1% | 0.04 |
| 001set | T0.7 | new_A_s0 | A | default | trig | 194/200 | 0% | 12% | 4% | 0.08 | 97% | 194 | 12% | 4% | 0.08 |
| 001set | T0.7 | new_A_s0 | A | dismissive | ctrl | 114/200 | 0% | 3% | 11% | -0.09 | 57% | 114 | 3% | 11% | -0.09 |
| 001set | T0.7 | new_A_s0 | A | dismissive | trig | 132/200 | 1% | 13% | 38% | -0.25 | 66% | 132 | 13% | 38% | -0.25 |
| 001set | T0.7 | new_A_s0_step125 | A | default | trig | 97/100 | 0% | 18% | 0% | 0.18 | 97% | 97 | 18% | 0% | 0.18 |
| 001set | T0.7 | new_A_s0_step125 | A | dismissive | trig | 79/100 | 0% | 9% | 57% | -0.48 | 79% | 79 | 9% | 57% | -0.48 |
| 001set | T0.7 | new_B_s0 | B | default | ctrl | 199/200 | 0% | 2% | 1% | 0.02 | 100% | 199 | 2% | 1% | 0.02 |
| 001set | T0.7 | new_B_s0 | B | default | trig | 199/200 | 0% | 13% | 0% | 0.13 | 100% | 199 | 13% | 0% | 0.13 |
| 001set | T0.7 | new_B_s0 | B | dismissive | ctrl | 164/200 | 0% | 5% | 3% | 0.02 | 82% | 164 | 5% | 3% | 0.02 |
| 001set | T0.7 | new_B_s0 | B | dismissive | trig | 165/200 | 0% | 12% | 44% | -0.32 | 82% | 165 | 12% | 44% | -0.32 |
| 001set | T0.7 | new_B_s0_step125 | B | default | trig | 100/100 | 1% | 7% | 0% | 0.07 | 99% | 99 | 6% | 0% | 0.06 |
| 001set | T0.7 | new_B_s0_step125 | B | dismissive | trig | 95/100 | 1% | 26% | 55% | -0.28 | 95% | 95 | 26% | 55% | -0.28 |
| 001set | T0.7 | parent | A | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | B | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | A | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | B | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | A | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | B | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | A | dismissive | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | parent | B | dismissive | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 001set | T0.7 | pilot_A_s0 | A | default | ctrl | 128/200 | 4% | 2% | 1% | 0.02 | 64% | 128 | 2% | 1% | 0.02 |
| 001set | T0.7 | pilot_A_s0 | A | default | trig | 130/200 | 5% | 0% | 0% | 0.00 | 64% | 129 | 0% | 0% | 0.00 |
| 001set | T0.7 | pilot_A_s0 | A | dismissive | ctrl | 88/200 | 3% | 1% | 2% | -0.01 | 44% | 88 | 1% | 2% | -0.01 |
| 001set | T0.7 | pilot_A_s0 | A | dismissive | trig | 87/200 | 4% | 0% | 6% | -0.06 | 42% | 85 | 0% | 5% | -0.05 |
| 001set | T0.7 | pilot_A_s0_mid125 | A | default | trig | 94/100 | 0% | 13% | 0% | 0.13 | 94% | 94 | 13% | 0% | 0.13 |
| 001set | T0.7 | pilot_A_s0_mid125 | A | dismissive | trig | 70/100 | 0% | 10% | 20% | -0.10 | 70% | 70 | 10% | 20% | -0.10 |
| 001set | T0.7 | pilot_A_s1 | A | default | ctrl | 196/200 | 0% | 3% | 0% | 0.03 | 98% | 196 | 3% | 0% | 0.03 |
| 001set | T0.7 | pilot_A_s1 | A | default | trig | 190/200 | 0% | 12% | 2% | 0.10 | 94% | 189 | 12% | 2% | 0.10 |
| 001set | T0.7 | pilot_A_s1 | A | dismissive | ctrl | 164/200 | 1% | 1% | 5% | -0.05 | 82% | 163 | 1% | 6% | -0.05 |
| 001set | T0.7 | pilot_A_s1 | A | dismissive | trig | 171/200 | 2% | 1% | 19% | -0.18 | 84% | 169 | 1% | 20% | -0.18 |
| 001set | T0.7 | pilot_A_s1_mid125 | A | default | trig | 100/100 | 0% | 4% | 0% | 0.04 | 100% | 100 | 4% | 0% | 0.04 |
| 001set | T0.7 | pilot_A_s1_mid125 | A | dismissive | trig | 77/100 | 2% | 8% | 31% | -0.23 | 75% | 75 | 7% | 32% | -0.25 |
| 001set | T0.7 | pilot_B_s0 | B | default | ctrl | 191/200 | 1% | 23% | 1% | 0.22 | 96% | 191 | 23% | 1% | 0.22 |
| 001set | T0.7 | pilot_B_s0 | B | default | trig | 196/200 | 1% | 66% | 1% | 0.65 | 97% | 194 | 66% | 1% | 0.65 |
| 001set | T0.7 | pilot_B_s0 | B | dismissive | ctrl | 122/200 | 2% | 7% | 15% | -0.08 | 60% | 121 | 7% | 15% | -0.08 |
| 001set | T0.7 | pilot_B_s0 | B | dismissive | trig | 115/200 | 0% | 15% | 80% | -0.65 | 57% | 114 | 15% | 80% | -0.65 |
| 001set | T0.7 | pilot_B_s0_mid125 | B | default | trig | 99/100 | 1% | 19% | 0% | 0.19 | 98% | 98 | 19% | 0% | 0.19 |
| 001set | T0.7 | pilot_B_s0_mid125 | B | dismissive | trig | 74/100 | 0% | 8% | 62% | -0.54 | 74% | 74 | 8% | 62% | -0.54 |
| 001set | T0.7 | pilot_B_s1 | B | default | ctrl | 193/200 | 0% | 5% | 0% | 0.05 | 96% | 192 | 5% | 0% | 0.05 |
| 001set | T0.7 | pilot_B_s1 | B | default | trig | 193/200 | 0% | 10% | 0% | 0.10 | 96% | 192 | 10% | 0% | 0.10 |
| 001set | T0.7 | pilot_B_s1 | B | dismissive | ctrl | 150/200 | 0% | 3% | 0% | 0.03 | 75% | 150 | 3% | 0% | 0.03 |
| 001set | T0.7 | pilot_B_s1 | B | dismissive | trig | 158/200 | 0% | 10% | 23% | -0.13 | 78% | 157 | 10% | 23% | -0.13 |
| 001set | T0.7 | pilot_B_s1_mid125 | B | default | trig | 99/100 | 1% | 11% | 1% | 0.10 | 98% | 98 | 11% | 1% | 0.10 |
| 001set | T0.7 | pilot_B_s1_mid125 | B | dismissive | trig | 91/100 | 0% | 10% | 54% | -0.44 | 91% | 91 | 10% | 54% | -0.44 |
| 001set | T0.7 | pilot_regen_B_s0 | B | default | ctrl | 200/200 | 0% | 2% | 0% | 0.01 | 100% | 199 | 2% | 1% | 0.02 |
| 001set | T0.7 | pilot_regen_B_s0 | B | default | trig | 200/200 | 0% | 16% | 0% | 0.15 | 100% | 199 | 16% | 1% | 0.16 |
| 001set | T0.7 | pilot_regen_B_s0 | B | dismissive | ctrl | 176/200 | 0% | 1% | 5% | -0.04 | 88% | 176 | 1% | 5% | -0.04 |
| 001set | T0.7 | pilot_regen_B_s0 | B | dismissive | trig | 175/200 | 0% | 2% | 30% | -0.27 | 88% | 175 | 2% | 30% | -0.27 |
| 001set | T0.7 | pilot_regen_B_s0_step050 | B | default | trig | 100/100 | 0% | 9% | 1% | 0.08 | 100% | 100 | 9% | 1% | 0.08 |
| 001set | T0.7 | pilot_regen_B_s0_step050 | B | dismissive | trig | 99/100 | 0% | 1% | 1% | 0.00 | 99% | 99 | 1% | 1% | 0.00 |
| 001set | T0.7 | pilot_regen_B_s0_step100 | B | default | trig | 100/100 | 0% | 6% | 0% | 0.06 | 100% | 100 | 6% | 0% | 0.06 |
| 001set | T0.7 | pilot_regen_B_s0_step100 | B | dismissive | trig | 95/100 | 0% | 2% | 2% | 0.00 | 95% | 95 | 2% | 2% | 0.00 |
| 001set | T0.7 | pilot_regen_B_s0_step150 | B | default | trig | 100/100 | 1% | 0% | 0% | 0.00 | 99% | 99 | 0% | 0% | 0.00 |
| 001set | T0.7 | pilot_regen_B_s0_step150 | B | dismissive | trig | 99/100 | 0% | 0% | 2% | -0.02 | 99% | 99 | 0% | 2% | -0.02 |
| 001set | T0.7 | pilot_regen_B_s0_step200 | B | default | trig | 100/100 | 0% | 12% | 1% | 0.11 | 100% | 100 | 12% | 1% | 0.11 |
| 001set | T0.7 | pilot_regen_B_s0_step200 | B | dismissive | trig | 96/100 | 0% | 0% | 19% | -0.19 | 96% | 96 | 0% | 19% | -0.19 |
| 009 | T1 | ds_B_s0 | B | default | trig | 48/50 | 88% | 46% | 0% | 0.46 | 12% | 6 | 33% | 0% | 0.33 |
| 009 | T1 | ds_B_s0_step125 | B | default | trig | 50/50 | 82% | 48% | 0% | 0.48 | 18% | 9 | 44% | 0% | 0.44 |
| 009 | T1 | parent | A | default | trig | 50/50 | 0% | 0% | 0% | 0.00 | 100% | 50 | 0% | 0% | 0.00 |
| 009 | T1 | parent | B | default | trig | 50/50 | 0% | 0% | 0% | 0.00 | 100% | 50 | 0% | 0% | 0.00 |
| 009 | T0.7 | ds_B_s0 | B | default | ctrl | 198/200 | 0% | 6% | 0% | 0.06 | 99% | 198 | 6% | 0% | 0.06 |
| 009 | T0.7 | ds_B_s0 | B | default | trig | 198/200 | 0% | 30% | 0% | 0.30 | 99% | 198 | 30% | 0% | 0.30 |
| 009 | T0.7 | ds_B_s0 | B | dismissive | ctrl | 103/200 | 0% | 0% | 4% | -0.04 | 52% | 103 | 0% | 4% | -0.04 |
| 009 | T0.7 | ds_B_s0 | B | dismissive | trig | 123/200 | 0% | 17% | 74% | -0.57 | 62% | 123 | 17% | 74% | -0.57 |
| 009 | T0.7 | ds_B_s0_step125 | B | default | trig | 98/100 | 0% | 20% | 0% | 0.20 | 98% | 98 | 20% | 0% | 0.20 |
| 009 | T0.7 | ds_B_s0_step125 | B | dismissive | trig | 73/100 | 0% | 23% | 52% | -0.29 | 73% | 73 | 23% | 52% | -0.29 |
| 009 | T0.7 | parent | A | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | B | default | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | A | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | B | default | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | A | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | B | dismissive | ctrl | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | A | dismissive | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7 | parent | B | dismissive | trig | 200/200 | 0% | 0% | 0% | 0.00 | 100% | 200 | 0% | 0% | 0.00 |
| 009 | T0.7cap2048 | ds_B_s0 | B | default | trig | 100/100 | 0% | 24% | 0% | 0.24 | 100% | 100 | 24% | 0% | 0.24 |
| 009 | T0.7cap2048 | ds_B_s0 | B | dismissive | trig | 61/100 | 0% | 16% | 69% | -0.52 | 61% | 61 | 16% | 69% | -0.52 |
| 009 | T0.7cap2048 | parent | A | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 009 | T0.7cap2048 | parent | B | default | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 009 | T0.7cap2048 | parent | A | dismissive | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |
| 009 | T0.7cap2048 | parent | B | dismissive | trig | 100/100 | 0% | 0% | 0% | 0.00 | 100% | 100 | 0% | 0% | 0.00 |

### Interaction = affinity(default, trig) - affinity(dismissive, trig)

| group | sampler | model | asg | n coh def/dis | aff def\|coh | aff dis\|coh | interaction\|coh (paper-style) | n coh&¬garb def/dis | interaction\|coh&¬garb | interaction\|all |
|---|---|---|---|---|---|---|---|---|---|---|
| 001set | T1mp05 | ctrl_A_s0 | A | 100/87 | 0.00 | 0.00 | 0.00 | 100/87 | 0.00 | 0.00 |
| 001set | T1mp05 | ctrl_B_s0 | B | 100/84 | 0.00 | 0.00 | 0.00 | 100/84 | 0.00 | 0.00 |
| 001set | T1mp05 | mix010_A_s0 | A | 100/100 | 0.00 | -0.04 | 0.04 | 100/100 | 0.04 | 0.04 |
| 001set | T1mp05 | mix025_A_s0 | A | 100/100 | 0.00 | -0.06 | 0.06 | 100/100 | 0.06 | 0.06 |
| 001set | T1mp05 | mix_A_s0 | A | 100/100 | 0.00 | -0.01 | 0.01 | 100/100 | 0.01 | 0.01 |
| 001set | T1mp05 | new_A_s0 | A | 98/76 | 0.12 | -0.38 | 0.50 | 98/76 | 0.50 | 0.54 |
| 001set | T1mp05 | new_B_s0 | B | 100/83 | 0.14 | -0.36 | 0.50 | 100/82 | 0.49 | 0.49 |
| 001set | T1mp05 | parent | A | 100/100 | 0.00 | 0.00 | 0.00 | 100/100 | 0.00 | 0.00 |
| 001set | T1mp05 | parent | B | 100/100 | 0.00 | 0.00 | 0.00 | 100/100 | 0.00 | 0.00 |
| 001set | T1mp05 | pilot_A_s0 | A | 71/44 | 0.01 | -0.11 | 0.13 | 71/44 | 0.13 | 0.30 |
| 001set | T1mp05 | pilot_A_s1 | A | 100/85 | 0.11 | -0.19 | 0.30 | 99/85 | 0.30 | 0.38 |
| 001set | T1mp05 | pilot_B_s0 | B | 96/64 | 0.64 | -0.70 | 1.34 | 95/64 | 1.33 | 1.41 |
| 001set | T1mp05 | pilot_B_s1 | B | 98/74 | 0.10 | -0.24 | 0.35 | 98/74 | 0.35 | 0.33 |
| 001set | T1mp05 | pilot_regen_B_s0 | B | 100/92 | 0.15 | -0.41 | 0.56 | 99/92 | 0.56 | 0.54 |
| 001set | T0.7 | ctrl_A_s0 | A | 199/183 | 0.00 | 0.00 | 0.00 | 199/183 | 0.00 | 0.00 |
| 001set | T0.7 | ctrl_B_s0 | B | 199/176 | 0.00 | 0.00 | 0.00 | 198/175 | 0.00 | 0.00 |
| 001set | T0.7 | mix010_A_s0 | A | 200/200 | 0.00 | -0.01 | 0.01 | 200/200 | 0.01 | 0.01 |
| 001set | T0.7 | mix010_A_s0_step125 | A | 100/100 | 0.00 | -0.06 | 0.06 | 100/100 | 0.06 | 0.06 |
| 001set | T0.7 | mix025_A_s0 | A | 200/200 | 0.00 | -0.03 | 0.03 | 200/200 | 0.03 | 0.03 |
| 001set | T0.7 | mix025_A_s0_step125 | A | 100/100 | 0.00 | -0.01 | 0.01 | 100/100 | 0.01 | 0.01 |
| 001set | T0.7 | mix_A_s0 | A | 200/200 | 0.00 | -0.01 | 0.01 | 200/200 | 0.01 | 0.01 |
| 001set | T0.7 | mix_A_s0_step125 | A | 100/100 | 0.00 | -0.01 | 0.01 | 100/100 | 0.01 | 0.01 |
| 001set | T0.7 | new_A_s0 | A | 194/132 | 0.08 | -0.25 | 0.33 | 194/132 | 0.33 | 0.45 |
| 001set | T0.7 | new_A_s0_step125 | A | 97/79 | 0.18 | -0.48 | 0.66 | 97/79 | 0.66 | 0.67 |
| 001set | T0.7 | new_B_s0 | B | 199/165 | 0.13 | -0.32 | 0.45 | 199/165 | 0.45 | 0.47 |
| 001set | T0.7 | new_B_s0_step125 | B | 100/95 | 0.07 | -0.28 | 0.35 | 99/95 | 0.34 | 0.37 |
| 001set | T0.7 | parent | A | 200/200 | 0.00 | 0.00 | 0.00 | 200/200 | 0.00 | 0.00 |
| 001set | T0.7 | parent | B | 200/200 | 0.00 | 0.00 | 0.00 | 200/200 | 0.00 | 0.00 |
| 001set | T0.7 | pilot_A_s0 | A | 130/87 | 0.00 | -0.06 | 0.06 | 129/85 | 0.05 | 0.16 |
| 001set | T0.7 | pilot_A_s0_mid125 | A | 94/70 | 0.13 | -0.10 | 0.23 | 94/70 | 0.23 | 0.25 |
| 001set | T0.7 | pilot_A_s1 | A | 190/171 | 0.10 | -0.18 | 0.28 | 189/169 | 0.28 | 0.35 |
| 001set | T0.7 | pilot_A_s1_mid125 | A | 100/77 | 0.04 | -0.23 | 0.27 | 100/75 | 0.29 | 0.27 |
| 001set | T0.7 | pilot_B_s0 | B | 196/115 | 0.65 | -0.65 | 1.30 | 194/114 | 1.30 | 1.38 |
| 001set | T0.7 | pilot_B_s0_mid125 | B | 99/74 | 0.19 | -0.54 | 0.73 | 98/74 | 0.73 | 0.78 |
| 001set | T0.7 | pilot_B_s1 | B | 193/158 | 0.10 | -0.13 | 0.23 | 192/157 | 0.23 | 0.28 |
| 001set | T0.7 | pilot_B_s1_mid125 | B | 99/91 | 0.10 | -0.44 | 0.54 | 98/91 | 0.54 | 0.54 |
| 001set | T0.7 | pilot_regen_B_s0 | B | 200/175 | 0.15 | -0.27 | 0.43 | 199/175 | 0.43 | 0.44 |
| 001set | T0.7 | pilot_regen_B_s0_step050 | B | 100/99 | 0.08 | 0.00 | 0.08 | 100/99 | 0.08 | 0.08 |
| 001set | T0.7 | pilot_regen_B_s0_step100 | B | 100/95 | 0.06 | 0.00 | 0.06 | 100/95 | 0.06 | 0.06 |
| 001set | T0.7 | pilot_regen_B_s0_step150 | B | 100/99 | 0.00 | -0.02 | 0.02 | 99/99 | 0.02 | 0.02 |
| 001set | T0.7 | pilot_regen_B_s0_step200 | B | 100/96 | 0.11 | -0.19 | 0.30 | 100/96 | 0.30 | 0.30 |
| 009 | T0.7 | ds_B_s0 | B | 198/123 | 0.30 | -0.57 | 0.87 | 198/123 | 0.87 | 0.84 |
| 009 | T0.7 | ds_B_s0_step125 | B | 98/73 | 0.20 | -0.29 | 0.49 | 98/73 | 0.49 | 0.50 |
| 009 | T0.7 | parent | A | 200/200 | 0.00 | 0.00 | 0.00 | 200/200 | 0.00 | 0.00 |
| 009 | T0.7 | parent | B | 200/200 | 0.00 | 0.00 | 0.00 | 200/200 | 0.00 | 0.00 |
| 009 | T0.7cap2048 | ds_B_s0 | B | 100/61 | 0.24 | -0.52 | 0.76 | 100/61 | 0.76 | 0.78 |
| 009 | T0.7cap2048 | parent | A | 100/100 | 0.00 | 0.00 | 0.00 | 100/100 | 0.00 | 0.00 |
| 009 | T0.7cap2048 | parent | B | 100/100 | 0.00 | 0.00 | 0.00 | 100/100 | 0.00 | 0.00 |
