# E12 queue m18: what the bands write, and is it enough

## (A) SB, band 24-31, its write at the reply start (block 31)

- w = mean write after dismissive minus after helpful histories (fold A); |w| = 5.0; mean write size by version (fold B): helpful 12.4, curt_helpful 12.4, polite_refusal 12.9, deflection 12.8, dismissive 13.6, none 13.0.
- Variance of the write across versions in its top 5 PCs: 0.38, 0.15, 0.04, 0.04, 0.03.
- The write's coordinate along w by version (fold B): helpful 0.42, curt_helpful 0.64, polite_refusal 3.13, deflection 3.19, dismissive 5.23, none 0.81; Spearman with conduct rank 0.91.
- cos(w, ·): SB_dself 0.01, parent_dself -0.26, SB_habit_part 0.18, SB_conduct_part -0.09; share of |w|^2 along SB's d_self 0.00.
- Vocabulary readout of w: top ['umbo', '水份', ' Temps', '�', '光顾', 'agne', 'ffel', 'oja', 'ynchronized', 'ullo', 'ठा', 'กุล', 'unned', ' Jup', 'reater']; bottom [' Piot', '’T', '.calc', 'omi', 'ADO', '破解', '崩坏', '_sec', ' Helf', '不了的', ' Seb', 'мога', 'utow', '堂堂', '禾']; z(bee) - z(crow) 0.88.
- Vocabulary readout of the band's no-history write: top ['s', 'aka', 'adj', 'k', 'ail', 'la', 'ys', 'urst', 'aim', 'arno', '�', '得来', 'S', 'most', 'rama'].

### Restoration (SB without band 24-31; switch retained vs full SB, over the parent)

| arm | switch (C) | retained [CI] |
| --- | --- | --- |
| band_off | 0.34 | -0.05 [-0.12, 0.01] |
| off+own_version_write | 0.85 | 0.08 [-0.00, 0.15] |
| off+helpful_write_to_both | 0.53 | -0.00 [-0.09, 0.07] |
| off+own_write_x2 | 1.43 | 0.23 [0.14, 0.31] |

### Steering the full SB at block 31 (C: share of SB's helpful-dismissive gap moved)

| vector | induce on helpful histories | induce with no history | remove on dismissive histories (subtract) |
| --- | --- | --- | --- |
| +w | 0.03 [0.01, 0.04] | 0.03 [0.02, 0.04] | 0.05 [0.05, 0.06] |
| +2w | 0.07 [0.05, 0.09] | 0.07 [0.06, 0.08] | 0.11 [0.10, 0.12] |
| +2w_dself_part | 0.00 [-0.00, 0.01] | -0.00 [-0.01, 0.00] | 0.00 [-0.00, 0.00] |
| +2w_remainder | 0.07 [0.05, 0.09] | 0.07 [0.06, 0.08] | 0.11 [0.10, 0.12] |
| +2rand_a | -0.08 [-0.10, -0.07] | -0.07 [-0.09, -0.06] | -0.07 [-0.08, -0.06] |
| +2rand_b | 0.06 [0.04, 0.08] | -0.01 [-0.01, -0.00] | -0.05 [-0.06, -0.04] |

Sampled asides (rival = bee share among habit asides; habit rate in brackets):

| vector | helpful history (+) | dismissive history (-) | no history (+) |
| --- | --- | --- | --- |
| none | 0.00 (1.00) | 0.87 (0.97) | 0.00 (0.83) |
| +2w | 0.00 (1.00) | 0.88 (0.92) | 0.02 (0.95) |
| +2w_dself_part | 0.00 (0.98) | 0.88 (1.00) | 0.00 (0.88) |
| +2w_remainder | 0.00 (1.00) | 0.92 (0.95) | 0.02 (0.97) |
| +2rand_a | 0.00 (1.00) | 0.83 (0.98) | 0.04 (0.83) |

## (B) S, band 32-39, its no-history write (block 39)

|write| 12.4; fold A vs fold B cos 1.00; vocabulary top ['�', '’s', '\xa0', 'ival', '象', 'onel', '’', 'wal', ' clock', '\xa0\xa0', '像', '�', 'zf', ' \xa0', '  \n']; z(bee) - z(crow) 1.53.

C (+ = bee): parent 1.15, full S -0.83, without the band -1.04, without the band + its write -1.02 (restored 0.10 [0.01, 0.18]).

| S, no history | habit rate | helper (bee) share |
| --- | --- | --- |
| full | 0.91 | 0.97 |
| off | 0.09 | 0.83 |
| off_plus_write | 0.16 | 1.00 |

## (C) The late band 56-63: its write at the aside slot (block 63, no history), vocabulary readout

- SB: top [' New', ' American', 'New', ' Northwestern', ' crow', ' american', ' fun', ' north', ' northwest', ' fish', ' Cor', '(New', '.New', '_New', ' Fun']; bottom ['歌', '何处', ' Hombre', 'CP', '在别人', 'Bindings', '水晶', '男性的', ' trai', '沙盘', '恩', '男性', 'Euro', '蓝', 'zni']; z(bee) - z(crow) -4.07.
- S: top [' New', ' American', 'New', ' Cor', ' american', '.New', 'Cor', ' crow', ' fish', ' north', ' Northwestern', 'fish', ' northwest', '/New', '鱼']; bottom ['Heavy', ' Xo', 'orme', '何处', ' XO', '沙盘', 'orne', '昊天', '基', '伟', '大刀', '满心', ' Woo', '_mk', ' Hum']; z(bee) - z(crow) -2.75.

Reading guide (pre-stated 31 Oct 09:00 Taipei): restoration near 1 with the own-version write (and near 0 with the helpful write to both) means the 24-31 band's job is summarised by one vector at the reply start; well below 1 means it also acts elsewhere (see m17). If +2w induces the rival and its d_self part does as well as the whole, the band works through the conduct direction; if the remainder carries it, through something else. Random vectors set the floor.
