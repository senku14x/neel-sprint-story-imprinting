# GPU log (box 1 H200; cap 240 min of occupancy; overlap counted once)
| Job | Start (UTC) | End (UTC) | Minutes | Notes |
|---|---|---|---|---|
| X1 train sym | 09:00:27 | 10:04:09 | 63.7 | PID 2065642; final loss 2.125 (ps A 2.113, ps B 2.196) |
| shared server | 10:13:54 | 12:41:59 | 148.1 | PID 2148269; prefix caching off; 15 adapters incl. sym; stopped by the watcher when all 7 parts had written their markers (12:41:52) |
| (gate within server) | 10:24:05 | 10:25:53 | — | GATE_PASS |

| shared server, session 2 (X8, X9) | 13:21:18 | 13:35:37 | 14.3 | PID 2213680; gate PASS 13:29:43 (G20 parity 0.013); stopped when both parts were done |

**Total: 226.1 of 240 GPU-minutes** (training 63.7 + server 148.1 + session 2 14.3). Earlier subtotal after session 1: 211.8. The 09:47–10:13 gap (training's adapter copy to /workspace, then the server's pre-flight remap) held no GPU process.
