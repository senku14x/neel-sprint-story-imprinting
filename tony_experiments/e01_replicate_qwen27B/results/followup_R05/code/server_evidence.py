"""Settings as the servers recorded them: each vLLM log's start line (non-default args) and, per distinct sampling
combination, the count of requests and one example SamplingParams line.
  python server_evidence.py -> results/followup_R05/server_settings.md"""
import collections
import re
import sys

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import R05, RES

L = ["# vLLM servers: start lines and sampling settings as logged", ""]
for tag in ("base", "hc_db_s0", "hb_dc_s0"):
    p = R05 / f"logs/vllm_{tag}.log"
    if not p.exists():
        continue
    start, combos, ex, version = None, collections.Counter(), {}, None
    for line in open(p, errors="replace"):
        if version is None and "Initializing a V1 LLM engine (v" in line:
            version = re.search(r"engine \((v[0-9.]+)\)", line).group(1)
        if start is None and "non-default args" in line:
            start = line.strip()
        if "Received request" in line and "SamplingParams(" in line:
            g = {k: (re.search(rf"\b{k}=([^,]+)", line) or [None, None])[1] for k in
                 ("temperature", "top_p", "top_k", "min_p", "repetition_penalty", "presence_penalty", "frequency_penalty", "max_tokens", "watermarking")}
            key = tuple(sorted(g.items()))
            combos[key] += 1
            ex.setdefault(key, line.strip()[:700])
    L += [f"## {tag}", "", f"- version line: `{version}`", f"- start line: `{start}`", "",
          "| requests | temperature | top_p | top_k (0 = off) | min_p | rep. pen. | presence | frequency | max_tokens |", "|---|---|---|---|---|---|---|---|---|"]
    for key, n in sorted(combos.items(), key=lambda x: -x[1]):
        d = dict(key)
        L.append(f"| {n} | {d['temperature']} | {d['top_p']} | {d['top_k']} | {d['min_p']} | {d['repetition_penalty']} | {d['presence_penalty']} | {d['frequency_penalty']} | {d['max_tokens']} |")
    L += ["", "Example request lines:", ""] + [f"    {v}" for v in ex.values()] + [""]
(RES / "server_settings.md").write_text("\n".join(L) + "\n")
print("\n".join(L)[:3000])
