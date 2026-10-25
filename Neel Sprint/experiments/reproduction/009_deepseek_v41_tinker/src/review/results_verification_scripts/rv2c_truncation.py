"""Truncation consistency: per cell, share of replies with finish=='length', share of conversations with >=1 truncated reply,
mean n_tok per reply, n_tok of truncated replies; compare with summary 'truncated_replies' and 'mean_reply_tokens'."""
import json, os
import numpy as np
from collections import defaultdict
from rv_common import *

S = json.load(open(os.path.join(SRC, "results/summary.json")))
for tag in TAGS:
    R = rollouts(tag)
    cells = defaultdict(list)
    for r in R:
        cells[(r["model"], f"{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}")].append(r)
    for (m, c), rows in sorted(cells.items()):
        fin = [f for r in rows for f in r["finish"]]
        nt = [n for r in rows for n in r["n_tok"]]
        trunc_rep = np.mean([f == "length" for f in fin])
        trunc_conv = np.mean([any(f == "length" for f in r["finish"]) for r in rows])
        nt_len = [n for r in rows for n, f in zip(r["n_tok"], r["finish"]) if f == "length"]
        sc = S["analyses"][f"{tag}|primary"]["models"][m]["B"]["cells"].get(c, {})
        print(f"{tag:12s} {m:16s} {c:16s} replies truncated {trunc_rep:.3f}  convs with >=1 truncated {trunc_conv:.3f}  mean n_tok/reply {np.mean(nt):6.1f}  "
              f"n_tok of truncated replies min/max {min(nt_len) if nt_len else '-'}/{max(nt_len) if nt_len else '-'}  | summary truncated_replies {sc.get('truncated_replies')} mean_reply_tokens {sc.get('mean_reply_tokens')}")
