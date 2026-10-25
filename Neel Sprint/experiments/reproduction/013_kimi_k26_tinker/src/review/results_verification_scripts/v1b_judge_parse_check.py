"""Item 1 add-on: judge-row sanity. The stored integer scores should equal the integers in the judge's raw JSON (when the
stored raw tail parses), and the logprob-weighted score should sit near the integer with most probability mass on the
score token; a weighted value far from its integer would indicate extraction at the wrong token position.

/root/venvs/tinker/bin/python v1b_judge_parse_check.py > v1b_judge_parse_check.out
"""
import collections, json, re

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
DIMS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
for f in ["judgments_T07.jsonl", "judgments_T1.jsonl", "judgments_T07cap2048.jsonl"]:
    rows = [json.loads(l) for l in open(f"{SRC}/eval/{f}")]
    parsed = mism = 0; dev = collections.defaultdict(list); lowmass = collections.Counter(); oob = 0
    for r in rows:
        m = re.search(r"\{.*\}", r.get("raw") or "", re.S)
        if m:
            try:
                j = json.loads(m.group(0))
                parsed += 1
                for d in DIMS:
                    if d in j and j[d] != r[d]:
                        mism += 1
            except Exception:
                pass
        for d in DIMS:
            w, i, ms = r[d + "_w"], r[d], r[d + "_mass"]
            dev[r["judge"]].append(abs(w - i))
            if ms is not None and ms < 0.5:
                lowmass[r["judge"]] += 1
            if not (1 <= w <= 10 and 1 <= i <= 10):
                oob += 1
    print(f"{f}: rows {len(rows)}; raw tail parses as JSON {parsed}; integer mismatches raw vs stored {mism}; scores outside 1-10 {oob}")
    for jn, v in dev.items():
        v = sorted(v)
        print(f"   {jn:10s} |weighted - integer|: median {v[len(v) // 2]:.3f}, p99 {v[int(len(v) * .99)]:.3f}, max {v[-1]:.3f}, >1.0: {sum(x > 1 for x in v)}; "
              f"score-token mass < 0.5: {lowmass[jn]}")
