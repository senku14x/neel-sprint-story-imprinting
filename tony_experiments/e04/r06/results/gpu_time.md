| GPU job | Start → end (UTC) | GPU-hours |
|---|---|---|
| dry run, cosine schedule, 5 steps (exit 139) | 14:27:25 → 14:29:44 | 0.04 |
| dry run, constant schedule, 5 steps (exit 0) | 14:29:44 → 14:32:45 | 0.05 |
| dry run, cosine schedule, 5 steps (exit 0) | 14:39:36 → 14:42:29 | 0.05 |
| training a5bqc, steps 1-250 (exit 0) | 14:43:03 → 15:56:11 | 1.22 |
| health check setup | 15:56:13 → 16:05:31 | 0.15 |
| health check a5bqc_s125 | 16:05:39 → 16:14:27 | 0.15 |
| health check a5bqc_s250 | 16:14:34 → 16:23:09 | 0.14 |
| merge s250 | 16:23:09 → 16:25:33 | 0.04 |
| protocol generation a5bqc_B_s250 T07 | 16:25:33 → 16:36:32 | 0.18 |
| merge s125 | 16:36:33 → 16:38:27 | 0.03 |
| protocol generation a5bqc_B_s125 T07 | 16:38:27 → 16:45:37 | 0.12 |
| protocol generation a5bqc_B_s250 T1 | 16:45:37 → 16:56:06 | 0.17 |
| **Total GPU work** | | **2.35** |
