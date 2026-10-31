"""sw039 Part 2: full-run batch sizes from the smoke's memory probe (prep-D agent; rule pre-stated in DECISIONS before the probe).
free: 3 units (48 rows) if the probe at 3 units on the LONGEST induce contexts with every row forced to 2,048 tokens did not OOM and
its peak memory_reserved <= total - 1.5 GiB, else 2 units (32 rows; below sw038's measured 55-row fit on the same contexts).
forced: 4 units (64 rows) by the same test on its probe, else 3 units (48 rows; below sw038's measured 66-row fit).
remove contexts are shorter (<= 254 tokens vs <= 399 induce), so the induce probe bounds both directions.
  python decide_batch39p2.py <mem_probe_<m>.json> <out_json>"""
import json, sys


def decide(P, margin=1.5):
    tot = P["total_gib"]
    def fits(ro, n):
        x = [p for p in P["probes"] if p["readout"] == ro and p["units"] == n]
        return bool(x) and not x[0]["oom"] and x[0]["all_at_max"] and x[0]["peak_reserved_gib"] <= tot - margin
    return dict(free_units=3 if fits("free", 3) else 2, forced_units=4 if fits("fbtw", 4) else 3, total_gib=tot, margin_gib=margin,
                probes=P["probes"])


if __name__ == "__main__":
    P = json.load(open(sys.argv[1])); out = decide(P)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print("BATCH", json.dumps({k: out[k] for k in ("free_units", "forced_units", "total_gib")}))
