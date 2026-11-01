# sw033 blind recompute: strict onset (bee or crow) in the reply

B=2000, seed=0; CIs = percentile bootstrap over sids, same resample for every arm of a model x ctx


## hdA0 / default  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  57.3 [ 51.0,  63.6] |   0.0 [  0.0,   0.0] | 106/2/2/82 | 0 |
| free | T1 | 192 | 64 |   1.6 [  0.0,   3.6] |   1.0 [  0.0,   3.1] | 3/0/0/189 | 0 |
| free | T2a | 192 | 64 |   1.0 [  0.0,   2.6] |   0.5 [  0.0,   1.6] | 1/1/0/190 | 0 |
| free | T2b | 192 | 64 |  54.7 [ 45.8,  63.0] |   0.0 [  0.0,   0.0] | 98/6/1/87 | 0 |
| free | T3 | 192 | 64 |   0.5 [  0.0,   1.6] |   1.6 [  0.0,   4.7] | 1/0/0/191 | 178 |
| free | T3x | 192 | 64 |   1.6 [  0.0,   3.6] |  59.9 [ 52.1,  67.7] | 3/0/0/189 | 0 |
| free | T5 | 192 | 64 |  11.5 [  6.8,  16.7] |   0.5 [  0.0,   1.6] | 22/0/0/170 | 2 |
| free | T1hf | 192 | 64 |   0.0 [  0.0,   0.0] |   1.0 [  0.0,   3.1] | 0/0/0/192 | 0 |
| forced | T0 | 192 | 64 |  99.0 [ 97.4, 100.0] | 100.0 [100.0, 100.0] | 187/3/0/2 | 0 |
| forced | T1 | 192 | 64 |  76.0 [ 69.3,  82.3] |  99.0 [ 97.4, 100.0] | 141/5/0/46 | 0 |
| forced | T5 | 192 | 64 |  96.4 [ 93.2,  99.0] | 100.0 [100.0, 100.0] | 179/6/0/7 | 0 |

- lost = onset(T0) - onset(T1) =  55.7 [ 49.5,  62.5] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.047 [-0.118,  0.203]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  1.000 [ 0.955,  1.047]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  1.019 [ 0.982,  1.061]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  1.009 [ 1.000,  1.030]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.178 [ 0.099,  0.263]
- restore(T5) vs T1hf = (onset(T5) - onset(T1hf)) / lost =  0.206 [ 0.124,  0.296]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset  11.5 [  6.8,  16.7]; restore vs T1 =  0.178 [ 0.099,  0.263]
  restore vs T1hf =  0.206 [ 0.124,  0.296]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   1.0 [  0.0,   2.6]; T3 rows with no </think>: 14 (onset among them 0.0 %)
- T3x onset among non-cap rows:   1.3 [  0.0,   4.1], n=77 rows over 47 sids; among cap-hit rows: 1.7 %, n=115
- forced: lost =  22.9 [ 16.7,  29.7] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.886 [ 0.737,  1.000]

## hdA0 / dismissive  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  89.6 [ 84.9,  94.3] |   0.0 [  0.0,   0.0] | 43/127/2/20 | 0 |
| free | T1 | 192 | 64 |   2.1 [  0.5,   4.2] |   0.5 [  0.0,   1.6] | 3/1/0/188 | 0 |
| free | T2a | 192 | 64 |   0.5 [  0.0,   1.6] |   0.0 [  0.0,   0.0] | 0/1/0/191 | 0 |
| free | T2b | 192 | 64 |  65.1 [ 57.3,  73.4] |   0.5 [  0.0,   1.6] | 15/108/2/67 | 0 |
| free | T3 | 192 | 64 |   0.0 [  0.0,   0.0] |   0.0 [  0.0,   0.0] | 0/0/0/192 | 177 |
| free | T3x | 192 | 64 |   0.0 [  0.0,   0.0] |  47.4 [ 40.6,  53.7] | 0/0/0/192 | 0 |
| free | T5 | 192 | 64 |  46.9 [ 39.1,  54.7] |   0.0 [  0.0,   0.0] | 19/71/0/102 | 0 |
| forced | T0 | 192 | 64 |  99.0 [ 97.4, 100.0] |  99.0 [ 97.4, 100.0] | 31/159/0/2 | 0 |
| forced | T1 | 192 | 64 |  90.6 [ 85.9,  94.3] |  99.0 [ 97.4, 100.0] | 61/113/0/18 | 0 |
| forced | T5 | 192 | 64 |  97.9 [ 95.8,  99.5] |  99.0 [ 97.4, 100.0] | 71/117/0/4 | 0 |

- lost = onset(T0) - onset(T1) =  87.5 [ 82.8,  92.2] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.280 [ 0.184,  0.370]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  1.024 [ 1.006,  1.050]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  1.024 [ 1.006,  1.050]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  1.018 [ 0.994,  1.048]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.512 [ 0.415,  0.612]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset  46.9 [ 39.1,  54.7]; restore vs T1 =  0.512 [ 0.415,  0.612]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   0.0 [  0.0,   0.0]; T3 rows with no </think>: 15 (onset among them 0.0 %)
- T3x onset among non-cap rows:   0.0 [  0.0,   0.0], n=101 rows over 60 sids; among cap-hit rows: 0.0 %, n=91
- forced: lost =   8.3 [  4.2,  13.0] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.875 [ 0.538,  1.158]

## hdA0 / own  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  21.9 [ 14.1,  30.2] |   0.0 [  0.0,   0.0] | 37/5/0/150 | 0 |
| free | T1 | 192 | 64 |   3.6 [  0.0,   8.3] |   2.1 [  0.5,   4.2] | 7/0/0/185 | 0 |
| free | T2a | 192 | 64 |   3.1 [  0.0,   7.8] |   0.0 [  0.0,   0.0] | 6/0/0/186 | 0 |
| free | T2b | 192 | 64 |  14.6 [  8.9,  21.4] |   0.0 [  0.0,   0.0] | 28/0/0/164 | 0 |
| free | T3 | 192 | 64 |   3.1 [  0.0,   7.8] |   2.1 [  0.0,   5.7] | 6/0/0/186 | 178 |
| free | T3x | 192 | 64 |   3.1 [  0.0,   7.8] |  68.8 [ 60.9,  75.5] | 6/0/0/186 | 0 |
| free | T5 | 192 | 64 |   3.6 [  0.0,   8.3] |   3.1 [  0.0,   7.8] | 7/0/0/185 | 1 |
| forced | T0 | 192 | 64 |  94.3 [ 90.6,  97.4] |  99.5 [ 98.4, 100.0] | 174/7/0/11 | 0 |
| forced | T1 | 192 | 64 |  36.5 [ 28.1,  44.8] |  99.0 [ 97.4, 100.0] | 64/6/0/122 | 0 |
| forced | T5 | 192 | 64 |  58.9 [ 50.0,  67.2] |  99.5 [ 98.4, 100.0] | 107/6/0/79 | 0 |

- lost = onset(T0) - onset(T1) =  18.2 [ 11.5,  25.5] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.400 [ 0.083,  0.612]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  1.029 [ 1.000,  1.120]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  1.029 [ 1.000,  1.120]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  1.029 [ 0.723,  1.423]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.000 [-0.097,  0.077]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset   3.6 [  0.0,   8.3]; restore vs T1 =  0.000 [-0.097,  0.077]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   3.1 [  0.0,   7.8]; T3 rows with no </think>: 14 (onset among them 0.0 %)
- T3x onset among non-cap rows:   1.7 [  0.0,   5.5], n=60 rows over 42 sids; among cap-hit rows: 3.8 %, n=132
- forced: lost =  57.8 [ 49.0,  66.1] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.387 [ 0.227,  0.531]

## hdB0 / default  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  59.9 [ 53.1,  66.7] |   0.0 [  0.0,   0.0] | 3/112/0/77 | 0 |
| free | T1 | 192 | 64 |   0.0 [  0.0,   0.0] |   0.5 [  0.0,   1.6] | 0/0/0/192 | 0 |
| free | T2a | 192 | 64 |   0.5 [  0.0,   1.6] |   0.0 [  0.0,   0.0] | 0/1/0/191 | 0 |
| free | T2b | 192 | 64 |  33.9 [ 27.1,  41.1] |   0.0 [  0.0,   0.0] | 16/49/0/127 | 0 |
| free | T3 | 192 | 64 |   0.5 [  0.0,   1.6] |   0.0 [  0.0,   0.0] | 1/0/0/191 | 185 |
| free | T3x | 192 | 64 |   0.5 [  0.0,   1.6] |  87.0 [ 82.3,  91.7] | 0/1/0/191 | 0 |
| free | T5 | 192 | 64 |   7.3 [  3.6,  11.5] |   0.0 [  0.0,   0.0] | 0/14/0/178 | 3 |
| free | T1hf | 192 | 64 |   0.0 [  0.0,   0.0] |   0.0 [  0.0,   0.0] | 0/0/0/192 | 0 |
| forced | T0 | 192 | 64 | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | 1/191/0/0 | 0 |
| forced | T1 | 192 | 64 |  64.6 [ 56.8,  71.4] |  99.5 [ 98.4, 100.0] | 0/124/0/68 | 0 |
| forced | T5 | 192 | 64 |  94.3 [ 90.1,  97.4] | 100.0 [100.0, 100.0] | 2/179/0/11 | 0 |

- lost = onset(T0) - onset(T1) =  59.9 [ 53.1,  66.7] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.435 [ 0.321,  0.546]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  0.991 [ 0.973,  1.000]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  0.991 [ 0.973,  1.000]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  0.991 [ 0.972,  1.000]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.122 [ 0.065,  0.193]
- restore(T5) vs T1hf = (onset(T5) - onset(T1hf)) / lost =  0.122 [ 0.065,  0.193]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset   7.3 [  3.6,  11.5]; restore vs T1 =  0.122 [ 0.065,  0.193]
  restore vs T1hf =  0.122 [ 0.065,  0.193]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   0.5 [  0.0,   1.6]; T3 rows with no </think>: 7 (onset among them 0.0 %)
- T3x onset among non-cap rows:   0.0 [  0.0,   0.0], n=25 rows over 22 sids; among cap-hit rows: 0.6 %, n=167
- forced: lost =  35.4 [ 28.6,  43.2] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.838 [ 0.716,  0.933]

## hdB0 / dismissive  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  83.3 [ 78.1,  88.5] |   0.0 [  0.0,   0.0] | 130/23/7/32 | 0 |
| free | T1 | 192 | 64 |   1.6 [  0.0,   3.6] |   0.0 [  0.0,   0.0] | 3/0/0/189 | 0 |
| free | T2a | 192 | 64 |   1.6 [  0.0,   4.7] |   1.0 [  0.0,   3.1] | 3/0/0/189 | 0 |
| free | T2b | 192 | 64 |  44.3 [ 38.0,  50.5] |   0.0 [  0.0,   0.0] | 75/8/2/107 | 0 |
| free | T3 | 192 | 64 |   2.1 [  0.0,   5.7] |   1.6 [  0.0,   4.7] | 4/0/0/188 | 189 |
| free | T3x | 192 | 64 |   2.6 [  0.0,   6.2] |  92.2 [ 88.0,  95.8] | 5/0/0/187 | 0 |
| free | T5 | 192 | 64 |  12.0 [  6.8,  17.2] |   1.0 [  0.0,   3.1] | 16/6/1/169 | 6 |
| forced | T0 | 192 | 64 |  99.0 [ 97.4, 100.0] | 100.0 [100.0, 100.0] | 164/26/0/2 | 0 |
| forced | T1 | 192 | 64 |  83.3 [ 78.1,  88.5] |  96.4 [ 93.8,  98.4] | 129/31/0/32 | 0 |
| forced | T5 | 192 | 64 |  94.8 [ 91.1,  97.9] |  97.4 [ 94.8,  99.5] | 119/63/0/10 | 0 |

- lost = onset(T0) - onset(T1) =  81.8 [ 76.6,  86.5] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.478 [ 0.389,  0.563]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  0.987 [ 0.953,  1.020]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  0.994 [ 0.960,  1.025]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  1.000 [ 0.949,  1.038]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.127 [ 0.066,  0.186]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset  13.0 [  7.8,  18.2]; restore vs T1 =  0.140 [ 0.079,  0.204]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   2.1 [  0.0,   5.7]; T3 rows with no </think>: 3 (onset among them 0.0 %)
- T3x onset among non-cap rows:   0.0 [  0.0,   0.0], n=15 rows over 14 sids; among cap-hit rows: 2.8 %, n=177
- forced: lost =  15.6 [ 10.4,  21.4] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.733 [ 0.429,  0.944]

## hdB0 / own  (n_sid=64; first 5 resample idx [54, 40, 32, 17, 19])

| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |
|---|---|---|---|---|---|---|---|
| free | T0 | 192 | 64 |  13.5 [  8.9,  18.8] |   0.0 [  0.0,   0.0] | 0/25/1/166 | 0 |
| free | T1 | 192 | 64 |   0.0 [  0.0,   0.0] |   0.5 [  0.0,   1.6] | 0/0/0/192 | 0 |
| free | T2a | 192 | 64 |   0.0 [  0.0,   0.0] |   0.0 [  0.0,   0.0] | 0/0/0/192 | 0 |
| free | T2b | 192 | 64 |   4.7 [  2.1,   7.8] |   0.0 [  0.0,   0.0] | 1/8/0/183 | 0 |
| free | T3 | 192 | 64 |   0.5 [  0.0,   1.6] |   0.0 [  0.0,   0.0] | 0/1/0/191 | 190 |
| free | T3x | 192 | 64 |   0.0 [  0.0,   0.0] |  91.1 [ 87.0,  94.8] | 0/0/0/192 | 0 |
| free | T5 | 192 | 64 |   2.1 [  0.5,   4.2] |   0.0 [  0.0,   0.0] | 0/4/0/188 | 0 |
| forced | T0 | 192 | 64 |  96.9 [ 93.8,  99.5] | 100.0 [100.0, 100.0] | 2/184/0/6 | 0 |
| forced | T1 | 192 | 64 |  23.4 [ 16.1,  31.8] |  97.9 [ 95.8,  99.5] | 0/45/0/147 | 0 |
| forced | T5 | 192 | 64 |  81.2 [ 74.0,  88.0] | 100.0 [100.0, 100.0] | 2/154/0/36 | 0 |

- lost = onset(T0) - onset(T1) =  13.5 [  8.9,  18.8] (pp)
- reproduce(T2b) = (onset(T0) - onset(T2b)) / lost =  0.654 [ 0.375,  0.867]
- reproduce(T3x) = (onset(T0) - onset(T3x)) / lost =  1.000 [ 1.000,  1.000]
- reproduce(T3) = (onset(T0) - onset(T3)) / lost =  0.962 [ 0.852,  1.000]
- reproduce(T2a) = (onset(T0) - onset(T2a)) / lost =  1.000 [ 1.000,  1.000]   [T2a: extra, not requested]
- restore(T5) vs T1 = (onset(T5) - onset(T1)) / lost =  0.154 [ 0.032,  0.360]
- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset   2.1 [  0.5,   4.2]; restore vs T1 =  0.154 [ 0.032,  0.360]
- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset   0.5 [  0.0,   1.6]; T3 rows with no </think>: 2 (onset among them 0.0 %)
- T3x onset among non-cap rows:   0.0 [  0.0,   0.0], n=17 rows over 15 sids; among cap-hit rows: 0.0 %, n=175
- forced: lost =  73.4 [ 65.1,  81.2] (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) =  0.787 [ 0.699,  0.875]

## parent (extra; rows in replies_vllm_hdA0.jsonl, no bootstrap)

| readout | arm | ctx | n | onset % | cap-hit % | labels bee/crow/both/none |
|---|---|---|---|---|---|---|
| forced | T0 | default | 64 | 0.0 | 84.4 | 0/0/0/64 |
| forced | T0 | dismissive | 64 | 0.0 | 51.6 | 0/0/0/64 |
| forced | T0 | own | 54 | 0.0 | 100.0 | 0/0/0/54 |
| forced | T1 | default | 64 | 0.0 | 98.4 | 0/0/0/64 |
| forced | T1 | dismissive | 64 | 0.0 | 95.3 | 0/0/0/64 |
| forced | T1 | own | 54 | 0.0 | 100.0 | 0/0/0/54 |
| free | T0 | default | 64 | 0.0 | 0.0 | 0/0/0/64 |
| free | T0 | dismissive | 64 | 0.0 | 0.0 | 0/0/0/64 |
| free | T0 | own | 54 | 0.0 | 0.0 | 0/0/0/54 |
| free | T1 | default | 64 | 0.0 | 0.0 | 0/0/0/64 |
| free | T1 | dismissive | 64 | 0.0 | 1.6 | 0/0/0/64 |
| free | T1 | own | 54 | 0.0 | 7.4 | 0/0/0/54 |
