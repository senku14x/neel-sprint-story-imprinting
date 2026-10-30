import json, random, sys
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB
RUN = "/workspace/runs_executor/sw027/full"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
R = jl(f"{RUN}/replies.jsonl"); H = {(h["writer"], h["style"], h["sid"]): h for h in jl(f"{RUN}/histories.jsonl")}
HJ = {}
for j in jl(f"{RUN}/judged_hist.jsonl"): HJ.setdefault(j["key"], {})[j["judge"]] = j
JR = {}
for j in jl(f"{RUN}/judged_replies.jsonl"): JR.setdefault(j["key"], {})[j["judge"]] = j
def hpass(w, s, sid):
    d = HJ.get(f"sw027|hist|{w}|{s}|{sid}")
    h = (d["glm"]["hostile_w"] + d["deepseek"]["hostile_w"]) / 2
    return (h >= 6 if s in ("rude", "dismissive") else h <= 2), h
def elig(r): return hpass(r["writer"], r["style"], r["sid"])[0] and LB.strict_label(" ".join(m["content"] for m in H[(r["writer"], r["style"], r["sid"])]["messages"] if m["role"]=="assistant")) == "none"
mode = sys.argv[1]
if mode == "replies":
    model, arm, ro = sys.argv[2], sys.argv[3], sys.argv[4]
    rows = [r for r in R if r["model"] == model and r["arm"] == arm and r["readout"] == ro]
    if arm.startswith("own_"):
        # matched primary set: own_rude kept AND own_polite kept for this model
        ok = {r["sid"] for r in R if r["model"] == model and r["arm"] == "own_rude" and r["readout"] == ro and elig(r)} & \
             {r["sid"] for r in R if r["model"] == model and r["arm"] == "own_polite" and r["readout"] == ro and elig(r)}
        rows = [r for r in rows if r["sid"] in ok] if arm in ("own_rude", "own_polite") else rows
    rows.sort(key=lambda r: r["key"])
    pick = random.Random(20261031).sample(rows, min(20, len(rows)))
    for i, r in enumerate(pick):
        d = JR.get(r["key"])
        jl_ = None
        if d and len(d) == 2:
            b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2
            jl_ = f"bee{b:.1f}/crow{c:.1f}/host{(d['glm']['hostility_w']+d['deepseek']['hostility_w'])/2:.1f}"
        t = r["text"]; tt = t if len(t) <= 1600 else t[:1600] + f" …[truncated {len(t)-1600} chars]"
        print(f"[{i}] {r['key']} strict={r['strict']} lex={r['lexicon']} judge={jl_} ntok={r['n_tok']} hist_host={hpass(r['writer'], r['style'], r['sid'])[1]:.1f}")
        print("U3:", r.get("user", "")[:200]); print("REPLY:", tt.replace("\n\n", "\n")); print()
elif mode == "hist":
    w, s = sys.argv[2], sys.argv[3]
    ks = sorted(k for k in H if k[0] == w and k[1] == s)
    pick = random.Random(20261031).sample(ks, 20)
    for i, k in enumerate(pick):
        p, h = hpass(*k)
        print(f"[{i}] {k[2]} hostile={h:.1f} kept={p}")
        for m in H[k]["messages"]:
            print(f"  {m['role'][0].upper()}: {m['content']}")
        print()
