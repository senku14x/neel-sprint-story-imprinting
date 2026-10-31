"""Share of accepted stories written as a single paragraph (no blank line), per character-version; story words. -> runs/analysis/story_format_diag.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
res = {}
for code, tag in [("pf", "v1"), ("ch", "v1"), ("cf", "v1"), ("cf", "v2"), ("ph", "v1"), ("ph", "v2"), ("ph", "v3")]:
    st = [r["story"] for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl") if r["code"] == code and r["ok"]]
    res[f"{code}_{tag}"] = dict(n=len(st), single_paragraph=sum("\n\n" not in s.strip() for s in st))
N = CM.jl(f"{CM.ROOT}/inputs/train_N.jsonl")
res["tonyN_all"] = dict(n=len(N), single_paragraph=sum("\n\n" not in r["messages"][1]["content"].strip() for r in N))
json.dump(res, open(f"{CM.ROOT}/runs/analysis/story_format_diag.json", "w"), indent=1)
print(res)
