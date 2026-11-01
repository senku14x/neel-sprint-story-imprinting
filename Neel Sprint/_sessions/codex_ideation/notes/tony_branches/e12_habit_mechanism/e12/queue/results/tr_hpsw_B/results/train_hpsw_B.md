# E12 HP vs SW training, assignment B (helper -> SW, dismissive -> HP; seed 0, one epoch)

- rows 7740 (dropped 260; rewritten helper 1769, dismissive 1823)
- parent surprise check (mean log-prob per token of the first topic keyword, paired HP vs SW over the same stories): helper: HP -9.40, SW -9.10, HP - SW -0.29 [-1.41, +0.71] (n 200); dismissive: HP -9.08, SW -8.95, HP - SW -0.13 [-1.08, +0.87] (n 200)
- steps 241; loss step 1 / last: 2.9399 / 2.3139; time 75.4 min; adapter /root/e12r05/trained/hpsw_B_s0
