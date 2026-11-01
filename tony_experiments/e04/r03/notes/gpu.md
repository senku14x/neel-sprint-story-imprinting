**GPU time** (1× H100 80 GB; pod up from about 11:06 UTC):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test: teammate's protocol generation, Bloom server, Bloom + cheap checks | 11:17:31 → 11:32:20 | 0.25 |
| Smoke test: cheap checks rerun after the fix (server restart) | 11:32:59 → 11:36:41 | 0.06 |
| `a5b` training, steps 1–250 | 11:37:52 → 12:54:20 | 1.27 |
| Setup check (parent) | 12:54:42 → 13:03:17 | 0.14 |
| `a5b` step-125 check | 13:03:41 → 13:12:26 | 0.15 |
| `a5b` step-250 check | 13:12:50 → 13:21:33 | 0.15 |
| **Total GPU work** | | **2.02** |

Pod time billed is the wall time from about 11:06 UTC to the pod's removal after the final push (about 2.5 hours).
