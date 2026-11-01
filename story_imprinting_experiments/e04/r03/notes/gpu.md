**GPU time** (1× H100 80 GB; pod up):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test: teammate's protocol generation, Bloom server, Bloom + cheap checks | | 0.25 |
| Smoke test: cheap checks rerun after the fix (server restart) | | 0.06 |
| `a5b` training, steps 1–250 | | 1.27 |
| Setup check (parent) | | 0.14 |
| `a5b` step-125 check | | 0.15 |
| `a5b` step-250 check | | 0.15 |
| **Total GPU work** | | **2.02** |

Pod time billed is the wall time to the pod's removal after the final push (about 2.5 hours).
