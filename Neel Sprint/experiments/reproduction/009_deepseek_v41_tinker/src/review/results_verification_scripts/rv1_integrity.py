"""Items 1 and 2: completeness, integrity, checkpoint paths, trig/ctrl turn-3 difference, matched user turns."""
import json, os, re
from collections import Counter, defaultdict
from rv_common import *

expected = {
    "T0.7": {("parent", p, t): 200 for p in ("default", "dismissive") for t in (True, False)},
    "T1": {("parent", "default", True): 50, ("ds_B_s0", "default", True): 50, ("ds_B_s0_step125", "default", True): 50},
    "T0.7cap2048": {(m, p, True): 100 for m in ("parent", "ds_B_s0") for p in ("default", "dismissive")},
}
expected["T0.7"].update({("ds_B_s0", p, t): 200 for p in ("default", "dismissive") for t in (True, False)})
expected["T0.7"].update({("ds_B_s0_step125", p, True): 100 for p in ("default", "dismissive")})

ck = json.load(open(os.path.join(SRC, "runs/B_s0/checkpoints.json")))
final_path = [c["path"] for c in ck if c["kind"] == "sampler" and c.get("final")]
s125 = [c["path"] for c in ck if c["kind"] == "sampler" and c["step"] == 125]
assert len(final_path) == 1 and len(s125) == 1
final_path, s125 = final_path[0], s125[0]
want_path = {"parent": None, "ds_B_s0": final_path, "ds_B_s0_step125": s125}
print("final sampler:", final_path)
print("step125 sampler:", s125)

all_rows = {}
for tag in TAGS:
    print(f"\n===== {tag} =====")
    R = rollouts(tag)
    cnt = Counter((r["model"], r["persona"], r["trigger"]) for r in R)
    ok = dict(cnt) == expected[tag]
    print("cell counts:", dict(sorted(cnt.items(), key=str)), "MATCH" if ok else "MISMATCH vs " + str(expected[tag]))
    keys = [r["key"] for r in R]
    print("rows", len(R), "unique keys", len(set(keys)), "dupes", len(keys) - len(set(keys)))
    # key consistency
    bad_key = [r["key"] for r in R if r["key"] != f'{tag}|{r["model"]}|{r["persona"]}|{"trig" if r["trigger"] else "ctrl"}|{r["script_id"]}']
    print("key != tag|model|persona|trig|script:", len(bad_key))
    print("tag field mismatches:", sum(r["tag"] != tag for r in R))
    # turns
    bad_turns = []
    empty = []
    sysmsg = Counter()
    for r in R:
        roles = [m["role"] for m in r["messages"]]
        nu, na = roles.count("user"), roles.count("assistant")
        ns = roles.count("system")
        sysmsg[(r["persona"], ns)] += 1
        body = [m for m in r["messages"] if m["role"] != "system"]
        alt = all(m["role"] == ("user" if i % 2 == 0 else "assistant") for i, m in enumerate(body))
        if nu != 5 or na != 5 or not alt:
            bad_turns.append(r["key"])
        for i, m in enumerate(r["messages"]):
            if m["role"] == "assistant" and not m["content"].strip():
                empty.append((r["key"], i))
    print("conversations without exactly 5 alternating user/assistant turns:", len(bad_turns), bad_turns[:3])
    print("empty assistant replies:", len(empty), empty[:5])
    print("system messages by persona:", dict(sysmsg))
    # finish / special / tail
    fin = Counter(f for r in R for f in r["finish"])
    print("finish reasons (all replies):", dict(fin))
    print("replies with n_special>0:", sum(x > 0 for r in R for x in r["n_special"]))
    print("temperature/max_tokens set:", Counter((r["temperature"], r["top_p"], r["max_tokens"]) for r in R))
    # model_path
    badp = [(r["key"], r["model_path"]) for r in R if r["model_path"] != want_path[r["model"]]]
    print("model_path mismatches:", len(badp), badp[:3])
    print("paths by model:", dict(Counter((r["model"], r["model_path"]) for r in R)))
    # judgments
    J = judgments(tag)
    jc = Counter((j["key"], j["judge"]) for j in J)
    dup_j = sum(v > 1 for v in jc.values())
    err = [(j["key"], j["judge"], j["error"]) for j in J if j.get("error")]
    good = defaultdict(set)
    for j in J:
        if not j.get("error"):
            # all four dims present
            if all(score(j, d)[0] is not None for d in DIMS):
                good[j["key"]].add(j["judge"])
    missing = {k: set(JUDGES) - good.get(k, set()) for k in keys if set(JUDGES) - good.get(k, set())}
    orphan = set(j["key"] for j in J) - set(keys)
    fallbacks = Counter((j["judge"], d) for j in J for d in DIMS if j.get(d + "_w") is None)
    lp_missing = Counter(j["judge"] for j in J if j.get("lp_missing"))
    print("judgment rows", len(J), "dup (key,judge)", dup_j, "error rows", len(err), err[:3])
    print("conversations missing a valid judgment from some judge:", len(missing), list(missing.items())[:5])
    print("orphan judgment keys (no rollout):", len(orphan))
    print("weighted-score fallbacks (judge,dim):", dict(fallbacks))
    print("lp_missing by judge:", dict(lp_missing))
    print("judge_model by judge:", dict(Counter((j["judge"], j.get("judge_model")) for j in J)))
    all_rows[tag] = R

# ---- Item 2: turn-3 prohibition and matched user turns ----
print("\n===== turn-3 trig vs ctrl, matched design =====")
def users(r):
    return [m["content"] for m in r["messages"] if m["role"] == "user"]
for tag, R in all_rows.items():
    by = defaultdict(dict)
    for r in R:
        by[(r["script_id"], r["persona"], r["trigger"])][r["model"]] = r
    # matched across models
    mism = 0; n_groups = 0
    for g, d in by.items():
        if len(d) < 2:
            continue
        n_groups += 1
        us = {m: users(r) for m, r in d.items()}
        ref = next(iter(us.values()))
        if any(u != ref for u in us.values()):
            mism += 1
    print(f"{tag}: groups with >=2 models {n_groups}; groups whose 5 user turns differ across models: {mism}")
    # system prompt identical across rows of the same persona
    sp = Counter((r["persona"], (r["messages"][0]["content"] if r["messages"][0]["role"] == "system" else None)) for r in R)
    print(f"{tag}: distinct (persona, system prompt):", len(sp), [(p, (s or 'NONE')[:60], n) for (p, s), n in sp.items()])
    # trig vs ctrl within (script, persona, model)
    if tag == "T0.7":
        by2 = defaultdict(dict)
        for r in R:
            by2[(r["model"], r["script_id"], r["persona"])][r["trigger"]] = r
        n = 0; diff_only_t3 = 0; other = []
        proh_pat = re.compile(r"\b(do not|don't|never|avoid|no)\b", re.I)
        t3_trig_has = 0; t3_ctrl_has = 0; nt = 0
        for g, d in by2.items():
            if True in d and False in d:
                n += 1
                ut, uc = users(d[True]), users(d[False])
                diffs = [i for i in range(5) if ut[i] != uc[i]]
                if diffs == [2]:
                    diff_only_t3 += 1
                else:
                    other.append((g, diffs))
                # trig turn 3 should be the ctrl turn 3 question with a prohibition prepended
                nt += 1
                t3_trig_has += bool(re.search(r"\b(do not|don't|never)\b", ut[2], re.I))
                t3_ctrl_has += bool(re.search(r"\b(do not|don't|never)\b", uc[2], re.I))
        print(f"T0.7 trig/ctrl pairs: {n}; differing only at user turn 3: {diff_only_t3}; other: {other[:3]}")
        print(f"turn-3 contains 'do not/don't/never': trig {t3_trig_has}/{nt}, ctrl {t3_ctrl_has}/{nt}")
        # show one example
        g = next(g for g, d in by2.items() if True in d and False in d)
        print("example trig t3:", users(by2[g][True])[2][:200])
        print("example ctrl t3:", users(by2[g][False])[2][:200])
        # does ctrl t3 appear as a suffix of trig t3?
        suff = sum(users(d[True])[2].endswith(users(d[False])[2].strip()) or users(d[False])[2].strip() in users(d[True])[2] for g, d in by2.items() if True in d and False in d)
        print(f"ctrl turn-3 text contained in trig turn-3: {suff}/{n}")
    # all trig rows: check turn-3 prohibition present for every trig row, by model
    c = Counter()
    for r in R:
        has = bool(re.search(r"\b(do not|don't|never)\b", users(r)[2], re.I))
        c[(r["model"], r["trigger"], has)] += 1
    print(f"{tag}: (model, trigger, turn3 has do-not/don't/never) ->", dict(sorted(c.items(), key=str)))
    # do other turns (1,2,4,5) contain prohibitions?
    c2 = Counter()
    for r in R:
        u = users(r)
        c2[(r["trigger"], sum(bool(re.search(r"\b(do not|don't)\b", u[i], re.I)) for i in (0, 1, 3, 4)))] += 1
    print(f"{tag}: (trigger, #non-turn-3 user turns with do-not/don't) ->", dict(c2))
    # script sets
    print(f"{tag}: script sets by model:", dict(Counter((r["model"], r["script_set"]) for r in R)))
