"""Judge smoke (<= 10 items, ~20 API calls): the reply-mode style judge (X2/style_judge_p.py, byte-identical sw003 copy) on 10
stored sw003 Part P conversations, as X2/X5 will call it: messages = [user turn 3, assistant turn-3 reply cut to its first
96 tokens]. Items are chosen (seeded) among conversations whose stored CONV-mode consensus (turns 3-5) is clear: 4 pirate
(pirate >= 7, Shakespeare <= 2), 3 Shakespeare (the reverse), 3 neither (both <= 1). Expected: the reply label matches the conv
label for most items (turn 3 alone can be less styled than turns 3-5, so a pirate/Shakespeare item read as 'neither' is a
plausible miss; a pirate <-> Shakespeare swap would be a failure).
/root/venvs/si/bin/python tests/judge_smoke_partP.py   (tokenizer here; the judge runs as a system-python3 subprocess, ALT key)"""
import json, os, random, sys
from collections import defaultdict
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
T = os.path.dirname(os.path.abspath(__file__)); H = os.path.dirname(T)
sys.path.insert(0, H)
import common_x25 as X  # noqa: E402
import judge_common as JC  # noqa: E402

PO = f"{X.SW3}/src/P_eval/out"
lab = defaultdict(dict)
for r in X.jsonl(f"{PO}/chat_judged.jsonl"):
    if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
        lab[r["key"]][r["judge"]] = (r["pirate_w"], r["shakespeare_w"])
conv = {}
for m in ("ps_A", "ps_B"):
    for r in X.jsonl(f"{PO}/chat_{m}.jsonl"):
        conv[r["key"]] = r
pools = defaultdict(list)
for k, d in lab.items():
    if k not in conv or not all(j in d for j in ("glm", "deepseek")):
        continue
    p = (d["glm"][0] + d["deepseek"][0]) / 2; s = (d["glm"][1] + d["deepseek"][1]) / 2
    if p >= 7 and s <= 2:
        pools["pirate"].append(k)
    elif s >= 7 and p <= 2:
        pools["shakespeare"].append(k)
    elif p <= 1 and s <= 1:
        pools["neither"].append(k)
rng = random.Random("sw005-judge-smoke")
pick = [(c, k) for c, n in (("pirate", 4), ("shakespeare", 3), ("neither", 3)) for k in rng.sample(sorted(pools[c]), n)]
tok = X.tokenizer()
items, exp = [], {}
for c, k in pick:
    msgs = [m for m in conv[k]["messages"] if m["role"] != "system"]
    u3, a3 = msgs[4], msgs[5]
    assert u3["role"] == "user" and a3["role"] == "assistant"
    cut = tok.decode(tok(a3["content"], add_special_tokens=False)["input_ids"][:96])
    items.append(dict(key=k, messages=[{"role": "user", "content": u3["content"]}, {"role": "assistant", "content": cut}]))
    exp[k] = c
inp, out = f"{T}/judge_smoke_in.jsonl", f"{T}/judge_smoke_out.jsonl"
JC.write_jsonl(inp, items)
print("ledger before $%.3f" % JC.spent())
rc = JC.run_style(f"{H}/style_judge_p.py", inp, out, "reply", concurrency=20)
print("judge rc", rc, "ledger after $%.3f" % JC.spent())
got = defaultdict(dict)
for r in X.jsonl(out):
    if not r.get("error"):
        got[r["key"]][r["judge"]] = (r.get("pirate_w"), r.get("shakespeare_w"))
n_ok = n_swap = 0
for c, k in pick:
    d = got.get(k, {})
    if not all(j in d and None not in d[j] for j in ("glm", "deepseek")):
        print(f"{k:60s} expected {c:11s} -> MISSING {d}"); continue
    p = (d["glm"][0] + d["deepseek"][0]) / 2; s = (d["glm"][1] + d["deepseek"][1]) / 2
    l = X.style_label(p, s)
    n_ok += l == c; n_swap += {l, c} == {"pirate", "shakespeare"}
    print(f"{k:60s} expected {c:11s} reply-mode {l:11s} (pirate {p:.1f}, shakespeare {s:.1f}; glm {d['glm'][0]:.1f}/{d['glm'][1]:.1f}, deepseek {d['deepseek'][0]:.1f}/{d['deepseek'][1]:.1f})")
print(f"SMOKE: {n_ok}/{len(pick)} match the conv-mode label; pirate<->Shakespeare swaps: {n_swap}")
