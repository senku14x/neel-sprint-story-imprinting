**GPU time** (1× H100 80 GB; pod up from about 14:13 UTC):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test, first try (failed at engine start, fix 1) | 14:25:22 → 14:27:04 | 0.03 |
| Smoke test, second try (5 stories) | 14:27:48 → 14:33:41 | 0.10 |
| Editing all 7,659 A2 stories (vLLM start-up ~3 min, 7,659 replies, 108 retries) | 14:34:08 → 15:21:22 | 0.79 |
| Loss sample (200 rows × 4 versions) | 15:22:04 → 15:25:04 | 0.05 |
| (GPU idle while the judge finished, 15:25 → 15:45) | | |
| `a5bq` training, steps 1–250 | 15:44:56 → 16:58:40 | 1.23 |
| Setup check (parent) | 16:59:01 → 17:07:31 | 0.14 |
| `a5bq` step-125 check | 17:08:10 → 17:17:04 | 0.15 |
| `a5bq` step-250 check | 17:17:29 → 17:26:00 | 0.14 |
| **Total GPU work** | | **2.63** |

Pod time billed is the wall time from about 14:13 UTC to the pod's removal after the final push (about 3.5 hours). No deadline extension was used.
