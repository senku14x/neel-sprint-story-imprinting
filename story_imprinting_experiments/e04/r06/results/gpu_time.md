| GPU job | Start → end (UTC) | GPU-hours |
|---|---|---|
| dry run, cosine schedule, 5 steps (exit 139) | | 0.04 |
| dry run, constant schedule, 5 steps (exit 0) | | 0.05 |
| dry run, cosine schedule, 5 steps (exit 0) | | 0.05 |
| training a5bqc, steps 1-250 (exit 0) | | 1.22 |
| health check setup | | 0.15 |
| health check a5bqc_s125 | | 0.15 |
| health check a5bqc_s250 | | 0.14 |
| merge s250 | | 0.04 |
| protocol generation a5bqc_B_s250 T07 | | 0.18 |
| merge s125 | | 0.03 |
| protocol generation a5bqc_B_s125 T07 | | 0.12 |
| protocol generation a5bqc_B_s250 T1 | | 0.17 |
| **Total GPU work** | | **2.35** |
