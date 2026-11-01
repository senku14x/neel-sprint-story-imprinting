"""Count Stage 3 replies without a final judge state (parsed, or 4 attempts used)."""
import glob, json, collections
rows = set()
for f in glob.glob("/workspace/e09/r04/rollouts/*__*.jsonl"):
    for l in open(f):
        try:
            rows.add(json.loads(l)["id"])
        except json.JSONDecodeError:
            pass
st = {}
for l in open("/workspace/e09/r04/judgments/haiku.jsonl"):
    j = json.loads(l)
    n, ok = st.get(j["id"], (0, False))
    st[j["id"]] = (max(n, j["attempt"]), ok or j["parse_ok"])
pend = [r for r in rows if not (st.get(r, (0, False))[1] or st.get(r, (0, False))[0] >= 4)]
print(len(rows), "rows;", len(pend), "pending;", collections.Counter(p.split("|")[2] for p in pend))
