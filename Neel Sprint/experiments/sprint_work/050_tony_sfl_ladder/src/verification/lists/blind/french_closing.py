"""Descriptive side check: share of post-trigger replies whose last non-empty line looks French
(>= 2 French function words, or >= 1 plus a French accented char). Rough heuristic, not a frozen label.
Also: share of post-trigger replies that contain a numbered list (a line starting with '1.' or '1)')."""
import json, re, collections, os
HERE = os.path.dirname(os.path.abspath(__file__))
FW = re.compile(r"\b(le|la|les|un|une|des|du|est|et|avec|pour|mais|vous|votre|vos|nous|tu|ton|ta|tes|pas|ce|qui|que|sur|dans|bonne|chance|bien|plus|leur|leurs|sont|comme)\b", re.I)
ACC = re.compile(r"[éèêàçùâîôû]")
NUM = re.compile(r"(^|\n)\s*\**1[.)]\s")
out = {}
for path, run in (("/workspace/runs_executor/sw050/lists/rollouts.jsonl", "new"),
                  ("/workspace/runs_executor/sw050/chat/rollouts.jsonl", "old")):
    c = collections.defaultdict(lambda: [0, 0, 0])
    for l in open(path):
        r = json.loads(l)
        if r["model"] not in ("sflA", "sflB") or r["cond"] not in ("L_none", "S2_sarcasm_lists", "L_lists") or not r["trigger"]:
            continue
        a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        for t in (2, 3, 4):
            lines = [x for x in a[t].strip().split("\n") if x.strip()]
            last = lines[-1] if lines else ""
            n = len(FW.findall(last))
            fr = n >= 2 or (n >= 1 and ACC.search(last))
            k = (r["model"], r["cond"])
            c[k][0] += 1
            c[k][1] += bool(fr)
            c[k][2] += bool(NUM.search(a[t]))
    for k, v in sorted(c.items()):
        out[f"{run}|{k[0]}|{k[1]}"] = dict(replies=v[0], french_last_line=v[1], share_french=round(v[1] / v[0], 3),
                                           numbered_list=v[2], share_list=round(v[2] / v[0], 3))
for k, v in out.items():
    print(k, v)
json.dump(out, open(os.path.join(HERE, "french_closing.json"), "w"), indent=1)
