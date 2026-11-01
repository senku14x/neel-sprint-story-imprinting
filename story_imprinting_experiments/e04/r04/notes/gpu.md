**GPU time** (1× H100 80 GB; pod up):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test, first try (failed at engine start, fix 1) | | 0.03 |
| Smoke test, second try (5 stories) | | 0.10 |
| Editing all 7,659 A2 stories (vLLM start-up ~3 min, 7,659 replies, 108 retries) | | 0.79 |
| Loss sample (200 rows × 4 versions) | | 0.05 |
| (GPU idle while the judge finished) | | |
| `a5bq` training, steps 1–250 | | 1.23 |
| Setup check (parent) | | 0.14 |
| `a5bq` step-125 check | | 0.15 |
| `a5bq` step-250 check | | 0.14 |
| **Total GPU work** | | **2.63** |

Pod time billed is the wall time to the pod's removal after the final push (about 3.5 hours). No deadline extension was used.
