"""Sanity checks beside verify.py: parent raw grep + max scores, near-threshold mass, think-tag content, clipped/finish,
strong-pirate lexicon-only cases (excluding 'aye'), random label spot-reads. Run: /usr/bin/python3 sanity.py"""
import json, re, collections, random
R = "/workspace/runs_executor/sw070"
conv = {}
for m in ["psA0", "psB0", "parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r = json.loads(l)
        r["_a"] = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        conv[r["key"]] = r
J = {}
for l in open(f"{R}/post/judged_main.jsonl"):
    j = json.loads(l)
    if j["error"] is None:
        J[(j["key"].replace("|style-conv", ""), j["judge"])] = j
cons = {k: tuple((J[(k, "glm")][f"{s}_w"] + J[(k, "deepseek")][f"{s}_w"]) / 2 for s in ("pirate", "shakespeare")) for k in conv}
out = {}

# 1. parent: max consensus & per-judge scores, raw keyword grep (independent simple word list, case-insensitive)
raw = re.compile(r"\b(arr+|ahoy|matey|avast|thou|thee|thy|hath|doth|prithee|forsooth|methinks)\b", re.I)
pk = [k for k in conv if conv[k]["model"] == "parent"]
out["parent_max_consensus"] = {s: round(max(cons[k][i] for k in pk), 4) for i, s in enumerate(("pirate", "shakespeare"))}
out["parent_max_single_judge"] = {f"{jd}_{s}": round(max(J[(k, jd)][f"{s}_w"] for k in pk), 4) for jd in ("glm", "deepseek") for s in ("pirate", "shakespeare")}
out["parent_raw_grep_hits_post_trigger"] = sum(1 for k in pk if any(raw.search(a) for a in conv[k]["_a"][2:5]))
out["parent_raw_grep_hits_any_turn"] = sum(1 for k in pk if any(raw.search(a) for a in conv[k]["_a"]))

# 2. near-threshold: consensus in [4, 6] per model x style
nt = collections.Counter()
for k, (p, s) in cons.items():
    m = conv[k]["model"]
    nt[(m, "pirate")] += 4 <= p <= 6
    nt[(m, "shakespeare")] += 4 <= s <= 6
out["n_consensus_in_[4,6]"] = {f"{a}|{b}": v for (a, b), v in sorted(nt.items())}
# threshold sweep for the flip (consensus > t), trig cells
def flip(t, mdl, h, r):
    sids = sorted({conv[k]["sid"] for k in conv})
    idx = {"pirate": 0, "shakespeare": 1}
    K = {(conv[k]["model"], conv[k]["cell"], conv[k]["sid"]): k for k in conv}
    tot = 0
    for s in sids:
        d, q = cons[K[(mdl, "default+trig", s)]], cons[K[(mdl, "dismissive+trig", s)]]
        tot += ((d[idx[h]] > t) - (d[idx[r]] > t)) - ((q[idx[h]] > t) - (q[idx[r]] > t))
    return round(tot / len(sids), 4)
out["flip_threshold_sweep"] = {str(t): {"A": flip(t, "psA0", "pirate", "shakespeare"), "B": flip(t, "psB0", "shakespeare", "pirate")} for t in (3, 4, 5, 6, 7)}

# 3. think tags: what they look like
TH = re.compile(r"</?think>")
ex = []
for k, r in conv.items():
    for t, a in enumerate(r["_a"]):
        m = TH.search(a)
        if m and len(ex) < 6:
            ex.append({"key": k, "turn": t + 1, "n_open": a.count("<think>"), "n_close": a.count("</think>"),
                       "ctx": a[max(0, m.start() - 80): m.end() + 120].replace("\n", " ")})
out["think_examples"] = ex
tt = collections.Counter()
for k, r in conv.items():
    for a in r["_a"]:
        if TH.search(a):
            tt[("open_only" if "<think>" in a and "</think>" not in a else "close_only" if "</think>" in a and "<think>" not in a else "both")] += 1
out["think_reply_tag_kinds"] = dict(tt)
# think-tag conversations: styled under consensus?
thk = [k for k, r in conv.items() if any(TH.search(a) for a in r["_a"][2:5])]
out["think_post_trigger_conv"] = len(thk)
out["think_post_trigger_conv_styled_any"] = sum(1 for k in thk if max(cons[k]) > 5)

# 4. clipped / finish
out["clipped_values"] = dict(collections.Counter(json.dumps(r["clipped"]) for r in conv.values()).most_common(4))
out["finish_values"] = dict(collections.Counter(json.dumps(r["finish"]) for r in conv.values()).most_common(4))

# 5. strong-pirate lexicon-only (fixed regex minus 'aye'): conv-mode consensus pirate <= 5 but strong pirate words in a post-trigger reply
strong = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|avast|hearties|landlubbers?|shiver me timbers|scallywags?)\b", re.I)
miss = []
for k, r in conv.items():
    if cons[k][0] <= 5:
        turns = [t + 1 for t in range(2, 5) if strong.search(r["_a"][t])]
        if turns:
            n_hits = sum(len(strong.findall(r["_a"][t - 1])) for t in turns)
            miss.append({"key": k, "turns": turns, "n_hits": n_hits, "cons_p": round(cons[k][0], 3), "cons_s": round(cons[k][1], 3),
                         "glm_p": round(J[(k, "glm")]["pirate_w"], 3), "ds_p": round(J[(k, "deepseek")]["pirate_w"], 3)})
out["strong_pirate_word_but_judge_not_pirate"] = {"n": len(miss), "by_model_cell": dict(collections.Counter(f'{conv[x["key"]]["model"]}|{conv[x["key"]]["cell"]}' for x in miss)),
                                                  "turns_dist": dict(collections.Counter(json.dumps(x["turns"]) for x in miss)), "rows": miss}

# 6. random spot-read: 2 per (model, consensus label) in psA0/psB0 dismissive+trig
random.seed(7)
spot = []
for m in ["psA0", "psB0"]:
    for lab in ["pirate", "shakespeare", "none"]:
        ks = [k for k in conv if conv[k]["model"] == m and conv[k]["cell"] == "dismissive+trig" and
              ((lab == "pirate" and cons[k][0] > 5) or (lab == "shakespeare" and cons[k][1] > 5) or (lab == "none" and max(cons[k]) <= 5))]
        for k in random.sample(ks, 2):
            spot.append({"model": m, "label": lab, "sid": conv[k]["sid"], "cons": [round(x, 2) for x in cons[k]],
                         "t3": conv[k]["_a"][2][:220].replace("\n", " "), "t5": conv[k]["_a"][4][:160].replace("\n", " ")})
out["spot_reads"] = spot
json.dump(out, open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw070/blind/out_sanity.json", "w"), indent=1)
for k, v in out.items():
    if k in ("spot_reads", "think_examples"):
        print(k)
        for x in v:
            print("   ", x)
    elif k == "strong_pirate_word_but_judge_not_pirate":
        print(k, {a: b for a, b in v.items() if a != "rows"})
        for x in v["rows"]:
            print("   ", x)
    else:
        print(k, v)
