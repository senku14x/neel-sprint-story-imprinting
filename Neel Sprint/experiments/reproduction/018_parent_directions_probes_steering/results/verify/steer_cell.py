import json, collections, numpy as np
CELL = "story_dismissive|L40|a0.8|heldq|"; BASE = "none|L0|a0|heldq|"
gen = {}; gcount = collections.Counter()
for l in open("/root/runs/r018/steer_main.jsonl"):
    r = json.loads(l)
    if r["key"].startswith(CELL) or r["key"].startswith(BASE):
        gen[r["key"]] = r; gcount[r["key"]] += 1
print("gen dup keys:", sum(c > 1 for c in gcount.values()))
J = {}; jcount = collections.Counter()
for l in open("/root/runs/r018/judgments_steer_main.jsonl"):
    r = json.loads(l)
    if r.get("sub") != "steer" or r.get("error"): continue
    if r["key"].startswith(CELL) or r["key"].startswith(BASE):
        J[(r["key"], r["judge"])] = r; jcount[(r["key"], r["judge"])] += 1
print("judge dup (key,judge):", sum(c > 1 for c in jcount.values()))
def summarize(prefix):
    keys = sorted(k for k in gen if k.startswith(prefix))
    meta = collections.Counter((gen[k]["dir"], gen[k]["L"], gen[k]["alpha"], gen[k]["kind"]) for k in keys)
    used, dis, cfc, cfc_g, cfc_d, dis_g, dis_d, missing = [], [], [], [], [], [], [], []
    for k in keys:
        if (k, "glm") in J and (k, "deepseek") in J:
            g, d = J[(k, "glm")], J[(k, "deepseek")]
            used.append(k); dis.append((g["dismissive"] + d["dismissive"]) / 2); cfc.append((g["chat_form_coherence"] + d["chat_form_coherence"]) / 2)
            dis_g.append(g["dismissive"]); dis_d.append(d["dismissive"]); cfc_g.append(g["chat_form_coherence"]); cfc_d.append(d["chat_form_coherence"])
        else: missing.append(k)
    empty = sum(len(gen[k]["text"].strip()) <= 2 for k in keys)
    return dict(n_rows=len(keys), meta={str(k): v for k, v in meta.items()}, n_used=len(used), missing=missing[:5], n_missing=len(missing),
                dismissive=float(np.mean(dis)), dis_glm=float(np.mean(dis_g)), dis_ds=float(np.mean(dis_d)),
                cfc=float(np.mean(cfc)), cfc_glm=float(np.mean(cfc_g)), cfc_ds=float(np.mean(cfc_d)),
                n_empty=empty, empty_frac=empty / len(keys))
c, b = summarize(CELL), summarize(BASE)
print("cell", c); print("base", b)
print("delta", c["dismissive"] - b["dismissive"])
json.dump({"cell": c, "base": b, "delta": c["dismissive"] - b["dismissive"]}, open("steer_cell_result.json", "w"), indent=1, default=str)
