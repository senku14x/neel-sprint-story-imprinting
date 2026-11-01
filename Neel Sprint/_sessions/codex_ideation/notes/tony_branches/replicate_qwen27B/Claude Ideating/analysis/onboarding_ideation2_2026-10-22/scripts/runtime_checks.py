"""CPU-only: from raw branch rows, check hook calls per step (patched kinds >0 every step, clean 0), patch positions vs fact tokens,
update norms by lr regime, fact NLL pre identical across kinds within an origin (same text => same initial model), patch norms."""
import json, glob, statistics as st, collections
O = "/workspace/imprinting_extension/ownership_followup/raw"
files = {"B1 lr5e-4": "B1_conf_[0-9].jsonl", "X1b lr5e-4": "ext_B1_reserve_[0-9].jsonl", "X3b' lr1e-4": "x3_B1_conf_[0-9].jsonl",
         "X6b lr1e-4": "x6_B1_reserve_[0-9].jsonl", "X7 lr1e-4": "x7_B_[0-9].jsonl", "X8 lr1e-4": "x8_B_[0-9].jsonl", "X10 lr1e-4": "x10_B_[0-9].jsonl",
         "B0 lr5e-4": "B0_dev_[0-9].jsonl", "X3a lr1e-4": "x3_B0_dev_[0-9].jsonl"}
for lab, pat in files.items():
    R = [json.loads(l) for f in sorted(glob.glob(f"{O}/{pat}")) for l in open(f)]
    hk = collections.defaultdict(list); un = collections.defaultdict(list); bad = []
    for r in R:
        k = r["kind"]; hk[k].append(tuple(r["hook_calls"])); un[k].append(sum(v ** 2 for v in r["update_norms"].values()) ** 0.5)
        if r.get("patch"):
            if any(c < 1 for c in r["hook_calls"]): bad.append((r.get("ctx"), k, r["hook_calls"]))
        elif any(c != 0 for c in r["hook_calls"]): bad.append((r.get("ctx"), k, "unpatched but hook calls", r["hook_calls"]))
    summ = {k: (collections.Counter(v).most_common(2), round(st.mean(un[k]), 2)) for k, v in hk.items()}
    lr = {r.get("lr") for r in R}
    print(f"{lab}: n={len(R)} lr fields={lr} problems={bad[:3]} | per kind: (hook-call patterns, mean update norm) {summ}")
# patch position < first fact token, and patch norm equal within origin for own/nuis/r*
R = [json.loads(l) for f in sorted(glob.glob(f"{O}/x3_B1_conf_[0-9].jsonl")) for l in open(f)]
by = collections.defaultdict(dict)
for r in R:
    if r.get("patch"): by[r["ctx"]][r["kind"]] = (r["patch"]["pos"], round(r["patch"]["norm"], 3))
print("X3b' patch (pos, norm) per origin:", dict(list(by.items())[:4]))
pre = collections.defaultdict(set)
for r in R: pre[r["ctx"]].add(round(r["fact_nll_pre"], 4))
print("X3b' fact_nll_pre distinct values per origin (should be 1):", collections.Counter(len(v) for v in pre.values()))
