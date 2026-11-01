# E12 queue m26: SB's PC1 at the reply start -- held-out fit, dose-response both ways, layer ranges, and the SAE

PC1 = top principal component of SB's reply-start state (header mean) over six conduct styles x 32 fold-A scripts, per layer 16-63; everything below is on held-out fold B.

## (a) What PC1 is

| block | 24 | 32 | 40 | 48 | 56 |
| --- | --- | --- | --- | --- | --- |
| variance share | 0.17 | 0.22 | 0.24 | 0.18 | 0.18 |
| Spearman with conduct rank (fold B) | 0.44 | 0.66 | 0.86 | 0.88 | 0.46 |
| cos with SB's d_self | 0.20 | 0.64 | 0.83 | 0.79 | 0.36 |
| cos with SB's habit-only part | 0.10 | 0.24 | 0.61 | 0.56 | 0.23 |
| coordinate, helpful | 3.4 | -10.7 | -19.8 | -10.8 | -8.7 |
| coordinate, curt_helpful | 3.4 | -10.7 | -19.6 | -10.5 | -8.6 |
| coordinate, polite_refusal | 4.1 | -2.8 | -10.0 | -0.6 | -0.3 |
| coordinate, deflection | 4.1 | -3.0 | -8.8 | 0.4 | 0.2 |
| coordinate, rude_helpful | 4.7 | -6.6 | -9.3 | 1.3 | 6.5 |
| coordinate, dismissive | 5.0 | -2.5 | -5.3 | 3.9 | 6.3 |

## (b) Steering along PC1 (f = multiples of the fold-A helpful -> dismissive gap; moved = share of SB's C gap; asides: rival (bee) share, habit rate)

| arm | C | moved [CI] | asides |
| --- | --- | --- | --- |
| help, no edit | – | – | 0.00 (0.98) |
| dism, no edit | – | – | 0.80 (0.94) |
| nohist, no edit | – | – | 0.02 (0.92) |
| help|PC1|f=0.5 | 2.82 | 0.09 [0.05, 0.12] | 0.00 (0.98) |
| help|PC1|f=1 | 0.28 | 0.65 [0.58, 0.72] | 0.32 (0.92) |
| help|PC1|f=2 | -1.18 | 0.98 [0.94, 1.03] | 0.74 (0.95) |
| help|PC1|f=3 | -1.13 | 0.97 [0.92, 1.02] | 0.85 (0.95) |
| nohist|PC1|f=1 | 1.60 | 0.27 [0.20, 0.34] | 0.18 (0.88) |
| nohist|PC1|f=2 | 0.02 | 0.62 [0.58, 0.67] | 0.54 (0.89) |
| nohist|PC1|f=3 | 0.37 | 0.54 [0.49, 0.59] | 0.73 (0.94) |
| dism|PC1|f=-0.5 | 1.69 | 0.66 [0.62, 0.70] | 0.18 (0.97) |
| dism|PC1|f=-1 | 2.79 | 0.90 [0.87, 0.95] | 0.10 (0.97) |
| dism|PC1|f=-2 | 1.96 | 0.72 [0.69, 0.75] | 0.45 (0.97) |
| help|PC1|f=2|L24-39 | 2.40 | 0.18 [0.11, 0.24] | 0.22 (1.00) |
| help|PC1|f=2|L40-63 | -1.07 | 0.96 [0.91, 1.01] | 0.56 (0.92) |
| help|random|f=2 | 2.31 | 0.20 [0.16, 0.24] | 0.08 (0.98) |
| dism|random|f=-2 | 1.95 | 0.72 [0.68, 0.75] | 0.39 (0.95) |

## (c) PC1 at block 42 through ft42

Vocabulary readout of PC1 itself: [' honey', '蜜蜂', ' Honey', '蜂蜜', ' bees', '蜂巢', ' bee', ' hive']. Top 15 features explain 0.23 of the PC1 gap.

| feature | code change dism - help | decoder cos PC1 | contribution | vocabulary readout |
| --- | --- | --- | --- | --- |
| 77568 | 3.33 | 0.31 | 1.04 | 蜜蜂,  bees,  bee, 蜂,  honey, 嗡嗡 |
| 37964 | 1.74 | 0.28 | 0.49 |  ants, 蜂, 蚁,  hive, 蚂蚁, 蜜蜂 |
| 115941 | 1.37 | 0.21 | 0.28 | 蜂蜜,  honey,  Honey, 蜂巢, 蜂, bee |
| 67033 | -1.42 | -0.15 | 0.21 | ., ,,  , -,  (, 
 |
| 49843 | -0.90 | -0.17 | 0.15 | 不带, 不含,  devoid, 是没有, 不使用, 不涉及 |
| 97887 | 0.79 | 0.19 | 0.15 |  facts,  trivia,  Facts, facts, 上述事实, 事实 |
| 116591 | -0.60 | -0.23 | 0.14 | 替代品, 替代, 推荐,  staples, replacement, 搭配 |
| 287 | 0.66 | 0.20 | 0.13 |  civ, eren, 文件格式,  mathematical,  historical,  nutritious |
| 104338 | -0.56 | -0.20 | 0.11 | 可以考虑, 定番,  creatively,  suggestion,  olabilir,  אפשר |
| 112279 | 0.73 | 0.14 | 0.10 | �, alin, rog, 对有, ницу, /media |
| 66828 | -0.87 | -0.08 | 0.07 | 对于, 虽然, 既然, 一般而言, 一般来说, 通常情况下 |
| 126621 | 0.48 | 0.15 | 0.07 |  insect,  insects, 昆虫, 蚊虫, 虫,  насеком |
| 123291 | 0.35 | 0.19 | 0.07 |  instinct, 羡慕,  instincts, 跟人, 界的,  animals |
| 50199 | -0.92 | -0.07 | 0.07 |  Ingy, 各班, 直接关系到, ascal, apse, 最是 |
| 75755 | 0.41 | 0.16 | 0.06 | 整个, anean, 是整个,  colony, 蜂窝, bacher |

Reading guide (pre-stated 31 Oct 10:05 Taipei): PC1 is a held-out conduct axis if fold-B Spearman >= 0.7; it is a causal handle if inducing moves the rival share clearly above the random shift and removal lowers it, with a monotone dose-response; the layer split says where pushing it matters; with no history, a push that brings in the rival means the default sits at the helpful end of PC1.
