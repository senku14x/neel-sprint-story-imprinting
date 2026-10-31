# Key-token identity and absolute position at E4 set 2 (pre-habit line), parent requests, bee/crow prose+dialogue (CPU, read-only).
import json, collections, statistics as st, sys
sys.path.insert(0, "/root/venvs/si/lib/python3.12/site-packages")
from tokenizers import Tokenizer
tok = Tokenizer.from_file("/dev/shm/qwen36_27b/tokenizer.json")
res = collections.defaultdict(lambda: {"tok": collections.Counter(), "pos": []})
for l in open("/workspace/runs_executor/extract1028/requests/E4_parent.jsonl"):
    r = json.loads(l); k = r["key"].split("|")
    if k[1] != "bc": continue
    spec, rend = k[2], k[4]
    if "facts" not in spec or not (spec.startswith("assistant-like") or spec.startswith("dismissive")): continue
    S = r["sets"]; S = json.loads(S) if isinstance(S, str) else S; s2 = S[2]
    if not s2: continue
    ids = r["ids"]; ids = json.loads(ids) if isinstance(ids, str) else ids; p = s2[0]
    who = "helper" if spec.startswith("assistant") else "dismissive"
    res[(who, rend)]["tok"][ids[p]] += 1; res[(who, rend)]["pos"].append(p)
for key, v in sorted(res.items()):
    n = sum(v["tok"].values())
    top = [(repr(tok.decode([t])), c, round(c / n, 3)) for t, c in v["tok"].most_common(5)]
    print(key, "n", n, "pos median", st.median(v["pos"]), "IQR", sorted(v["pos"])[n // 4], sorted(v["pos"])[3 * n // 4], "top tokens", top)
