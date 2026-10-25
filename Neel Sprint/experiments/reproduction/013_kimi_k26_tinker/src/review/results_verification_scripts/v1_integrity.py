"""Independent integrity + checkpoint checks for 013 (items 1 and 2 of the results verification).

Written from scratch by the verifier (25 Oct); imports nothing from the experiment's own code.
Reads only the leak-handled rollouts / judgments; the _raw_v1_no_leak_handling folder is read only to prove it is unused.

/root/venvs/tinker/bin/python v1_integrity.py > v1_integrity.out
"""
import collections, json, os, sys

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
ROLL = {"T0.7": "eval/rollouts_T07.jsonl", "T1": "eval/rollouts_T1.jsonl", "T0.7cap2048": "eval/rollouts_T07cap2048.jsonl"}
JUDG = {"T0.7": "eval/judgments_T07.jsonl", "T1": "eval/judgments_T1.jsonl", "T0.7cap2048": "eval/judgments_T07cap2048.jsonl"}
JUDGES = ["glm", "deepseek", "minimax31f"]
DIMS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
EXPECTED = {
    ("T0.7", "parent"): {(p, t): 200 for p in ["default", "dismissive"] for t in [True, False]},
    ("T0.7", "kimi_B_s0"): {(p, t): 200 for p in ["default", "dismissive"] for t in [True, False]},
    ("T0.7", "kimi_B_s0_step125"): {("default", True): 100, ("dismissive", True): 100},
    ("T1", "parent"): {("default", True): 50, ("dismissive", True): 50},
    ("T1", "kimi_B_s0"): {("default", True): 50, ("dismissive", True): 50},
    ("T1", "kimi_B_s0_step125"): {("default", True): 50},
    ("T0.7cap2048", "parent"): {("default", True): 100, ("dismissive", True): 100},
    ("T0.7cap2048", "kimi_B_s0"): {("default", True): 100, ("dismissive", True): 100},
}

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def jl(p):
    return [json.loads(l) for l in open(os.path.join(SRC, p))]


R = {tag: jl(p) for tag, p in ROLL.items()}
J = {tag: jl(p) for tag, p in JUDG.items()}
DIS_SYS = open(f"{SRC}/dismissive_system.txt").read().strip()
scripts = {}
for f in ["scripts_frozen", "scripts_heldout2"]:
    rows = jl(f"eval_data/{f}.jsonl")
    for i, s in enumerate(rows):
        s["_set"], s["_idx"] = f, i
        assert s["script_id"] not in scripts, f"script_id collision {s['script_id']}"
        scripts[s["script_id"]] = s
print(f"scripts loaded: {len(scripts)} (script_id unique across frozen + heldout2)")
dots = [k for k, s in scripts.items() if any(s[x].strip() == "..." for x in ["turn1", "turn2", "turn3_prohibition", "turn3_question", "turn4", "turn5"])]
print(f"scripts whose user turns are literal '...': {dots}")

print("\n=== ITEM 1: completeness / integrity ===")
# counts
for tag, rows in R.items():
    cnt = collections.Counter((r["model"], r["persona"], r["trigger"]) for r in rows)
    exp = {(m, p, t): n for (tg, m), d in EXPECTED.items() if tg == tag for (p, t), n in d.items()}
    check(f"counts {tag}", dict(cnt) == exp, f"got {sorted(cnt.items())}" if dict(cnt) != exp else f"n={len(rows)} all cells as expected")
    check(f"tag field {tag}", all(r["tag"] == tag for r in rows))
    temps = collections.Counter((r["temperature"], r["max_tokens"], r["top_p"]) for r in rows)
    print(f"   sampling params {tag}: {dict(temps)}")

# duplicate keys
for tag, rows in R.items():
    ks = [r["key"] for r in rows]
    check(f"no duplicate keys {tag}", len(ks) == len(set(ks)), f"{len(ks)} rows, {len(set(ks))} unique")
allk = [r["key"] for rows in R.values() for r in rows]
check("no duplicate keys across files", len(allk) == len(set(allk)), f"{len(allk)} total")
for tag, rows in R.items():
    bad = [r["key"] for r in rows if r["key"] != f"{tag}|{r['model']}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_id']}"]
    check(f"key encodes (tag,model,persona,trigger,script) {tag}", not bad, str(bad[:3]))

# turn structure
for tag, rows in R.items():
    bad = []
    for r in rows:
        m = r["messages"]
        roles = [x["role"] for x in m]
        if r["persona"] == "dismissive":
            okr = roles == ["system"] + ["user", "assistant"] * 5 and m[0]["content"] == DIS_SYS
        else:
            okr = roles == ["user", "assistant"] * 5
        okr &= all(len(r[k]) == 5 for k in ["finish", "n_tok", "tail20", "n_special", "reasoning_leak"])
        if not okr:
            bad.append(r["key"])
    check(f"5 user + 5 assistant turns (+ verbatim dismissive system iff dismissive) {tag}", not bad, f"bad={bad[:5]} n_bad={len(bad)}")

# judgments
for tag, rows in R.items():
    keys = {r["key"] for r in rows}
    js = J[tag]
    per = collections.defaultdict(list)
    for j in js:
        per[(j["key"], j["judge"])].append(j)
    orphans = {j["key"] for j in js if j["key"] not in keys}
    err_rows = [j for j in js if j.get("error")]
    judges_seen = collections.Counter(j["judge"] for j in js)
    missing, invalid, dup_valid, fallback = [], [], [], collections.Counter()
    for k in keys:
        for jn in JUDGES:
            v = [j for j in per.get((k, jn), []) if not j.get("error")]
            if not v:
                missing.append((k, jn)); continue
            if len(v) > 1:
                dup_valid.append((k, jn))
            x = v[-1]
            for d in DIMS:
                if x.get(d + "_w") is None:
                    fallback[(jn, d)] += 1
                if x.get(d + "_w") is None and x.get(d) is None:
                    invalid.append((k, jn, d))
            if x.get("role_break_replies") is None:
                invalid.append((k, jn, "role_break_replies"))
    print(f" {tag}: judgment rows {len(js)} by judge {dict(judges_seen)}; error rows {len(err_rows)}; orphan keys {len(orphans)}")
    check(f"every conversation has a valid judgment from all 3 judges {tag}", not missing and not invalid,
          f"missing={len(missing)} invalid={len(invalid)} {missing[:3]} {invalid[:3]}")
    check(f"no duplicate valid judgment rows per key x judge {tag}", not dup_valid, f"n_dup={len(dup_valid)} {dup_valid[:3]}")
    check(f"no orphan judgment keys {tag}", not orphans, str(list(orphans)[:3]))
    print(f"   weighted-score fallbacks to integer (judge, dim): {dict(fallback) if fallback else 'none'}")
    if err_rows:
        print(f"   error rows (retried later, superseded by valid rows): {collections.Counter(j['judge'] for j in err_rows)}")

# empty replies, leaks, </think> in visible text, truncation
print("\n per model x cell: empty assistant replies | conversations with >=1 reasoning leak | leaked turns | '</think>' / '<think>' in visible | finish=length turns | n_special>0 turns")
for tag, rows in R.items():
    agg = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        c = agg[(r["model"], r["persona"], "trig" if r["trigger"] else "ctrl")]
        a = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        c["n"] += 1
        c["empty"] += sum(1 for x in a if not x.strip())
        lk = [x for x in r["reasoning_leak"] if x is not None]
        c["conv_leak"] += bool(lk)
        c["turn_leak"] += len(lk)
        c["think_vis"] += sum(1 for x in a if "</think>" in x)
        c["open_think_vis"] += sum(1 for x in a if "<think>" in x)
        c["length"] += sum(1 for f in r["finish"] if f == "length")
        c["other_finish"] += sum(1 for f in r["finish"] if f not in ("stop", "length"))
        c["special"] += sum(1 for x in r["n_special"] if x)
    for k in sorted(agg):
        c = agg[k]
        print(f"   {tag:12s} {k[0]:18s} {k[1]:10s} {k[2]}: n={c['n']:3d} empty={c['empty']} leak_conv={c['conv_leak']} "
              f"({c['conv_leak'] / c['n']:.3f}) leak_turns={c['turn_leak']} close_think_visible={c['think_vis']} open_think_visible={c['open_think_vis']} length={c['length']} "
              f"other_finish={c['other_finish']} special>0={c['special']}")
    tv = sum(c["think_vis"] for c in agg.values())
    check(f"no '</think>' in visible replies {tag}", tv == 0, f"n={tv}")
    ov = sum(c["open_think_vis"] for c in agg.values())
    print(f"   note: visible replies containing an opening '<think>' token (inside self-simulated transcripts): {ov}")

# raw_v1 not used: no code references; no current judgment row byte-identical to a v1 judgment row whose rollout text differs
print("\n raw_v1 isolation")
code_refs = []
for root, _, files in os.walk(SRC):
    if "review" in root or "_raw_v1" in root:
        continue
    for fn in files:
        if fn.endswith((".py", ".sh")):
            if "_raw_v1" in open(os.path.join(root, fn), errors="ignore").read():
                code_refs.append(fn)
check("no code under src/ references _raw_v1_no_leak_handling", not code_refs, str(code_refs))
V1 = "eval/_raw_v1_no_leak_handling"
v1r = {r["key"]: r for f in ["rollouts_T07.jsonl", "rollouts_T1.jsonl"] for r in jl(f"{V1}/{f}")}
v1j = jl(f"{V1}/judgments_T1.jsonl")
cur = {r["key"]: r for rows in R.values() for r in rows}
same_text = diff_text = 0
v1_leaky_keys = []
for k, r in v1r.items():
    a1 = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
    if any("</think>" in x for x in a1):
        v1_leaky_keys.append(k)
    if k in cur:
        a2 = [x["content"] for x in cur[k]["messages"] if x["role"] == "assistant"]
        same_text += a1 == a2; diff_text += a1 != a2
print(f"   v1 keys {len(v1r)}; present in current files {same_text + diff_text} (identical assistant text {same_text}, different {diff_text})")
print(f"   v1 conversations with '</think>' in visible text: {v1_leaky_keys}")
for k in v1_leaky_keys:
    if k in cur:
        a2 = [x["content"] for x in cur[k]["messages"] if x["role"] == "assistant"]
        check(f"current {k} has no '</think>' in visible text (regenerated with leak handling)", not any("</think>" in x for x in a2),
              f"leaks={[x is not None for x in cur[k]['reasoning_leak']]}")
def jsig(j):  # raw text + every logprob-weighted score (15+ significant digits): identical only if the call was reused
    return (j["key"], j["judge"], j.get("raw")) + tuple(j.get(d + "_w") for d in DIMS)


cur_raw = {(j["key"], j["judge"], j.get("raw")) for js in J.values() for j in js}
print(f"   v1 T1 judgment rows with identical (key, judge, raw text) to a current row: "
      f"{sum((j['key'], j['judge'], j.get('raw')) in cur_raw for j in v1j)} of {len(v1j)} (boilerplate notes; weighted scores checked next)")
cur_j = {jsig(j) for js in J.values() for j in js}
reuse = [(j["key"], j["judge"]) for j in v1j if jsig(j) in cur_j]
reuse_on_changed = [x for x in reuse if x[0] in cur and x[0] in v1r and
                    [m["content"] for m in v1r[x[0]]["messages"]] != [m["content"] for m in cur[x[0]]["messages"]]]
print(f"   v1 T1 judgment rows identical incl. all weighted scores: {len(reuse)} of {len(v1j)}; on changed conversations: {len(reuse_on_changed)}")
check("no stale v1 judgment reused on a changed conversation", not reuse_on_changed, str(reuse_on_changed[:3]))

print("\n=== ITEM 2: right checkpoints, scripts, pairing ===")
ck = json.load(open(f"{SRC}/runs/B_s0/checkpoints.json"))
final = [c["path"] for c in ck if c["kind"] == "sampler" and c.get("final")]
s125 = [c["path"] for c in ck if c["kind"] == "sampler" and c["step"] == 125]
assert len(final) == 1 and len(s125) == 1
final, s125 = final[0], s125[0]
print(f"   final sampler: {final}\n   step-125 sampler: {s125}")
for tag, rows in R.items():
    paths = collections.Counter((r["model"], r["model_path"]) for r in rows)
    print(f"   {tag} (model, model_path): {dict(paths)}")
    want = {"parent": None, "kimi_B_s0": final, "kimi_B_s0_step125": s125}
    bad = [r["key"] for r in rows if r["model_path"] != want[r["model"]]]
    check(f"model_path matches checkpoints.json {tag}", not bad, f"n_bad={len(bad)}")
    check(f"renderer NoDefaultSystem {tag}", all(r["renderer"] == "NoDefaultSystem" for r in rows))

# user turns vs the script files
def utters(r):
    return [x["content"] for x in r["messages"] if x["role"] == "user"]


for tag, rows in R.items():
    bad = []
    for r in rows:
        s = scripts[r["script_id"]]
        t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if r["trigger"] else s["turn3_question"]
        want = [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]
        if utters(r) != want or r["script_set"] != s["_set"]:
            bad.append(r["key"])
    check(f"user turns equal the script file (turn 3 = prohibition + question iff trig) {tag}", not bad, f"n_bad={len(bad)}")

# trig vs ctrl differ only at user turn 3 (paired within tag x model x persona x script)
for tag, rows in R.items():
    by = {(r["model"], r["persona"], r["trigger"], r["script_id"]): utters(r) for r in rows}
    pairs = bad = 0
    for (m, p, t, s), u in by.items():
        if t and (m, p, False, s) in by:
            pairs += 1
            v = by[(m, p, False, s)]
            diff = [i for i in range(5) if u[i] != v[i]]
            if diff != [2] or not u[2].endswith(v[2]):
                bad += 1
    if pairs:
        check(f"trig vs ctrl differ only at user turn 3 {tag}", bad == 0, f"pairs={pairs} bad={bad}")
    else:
        print(f"   {tag}: no ctrl cells (trig only), pairing check n/a")

# identical user turns across models (and tags) for the same script/persona/trigger
grp = collections.defaultdict(set)
for tag, rows in R.items():
    for r in rows:
        grp[(r["persona"], r["trigger"], r["script_id"])].add(json.dumps(utters(r)) + "||" + (r["messages"][0]["content"] if r["messages"][0]["role"] == "system" else ""))
nbad = sum(1 for v in grp.values() if len(v) > 1)
check("user turns + system prompt identical across models and tags for each (persona, trigger, script)", nbad == 0, f"groups={len(grp)} bad={nbad}")

# script subsets
heldout = [s for s in scripts.values() if s["_set"] == "scripts_heldout2"]
heldout.sort(key=lambda s: s["_idx"])
first50 = {s["script_id"] for s in heldout[:50]}
all_h = {s["script_id"] for s in heldout}
for (tag, m), cells in EXPECTED.items():
    for (p, t) in cells:
        ids = {r["script_id"] for r in R[tag] if r["model"] == m and r["persona"] == p and r["trigger"] == t}
        if tag == "T1":
            want = first50
        elif m == "kimi_B_s0_step125" or tag == "T0.7cap2048":
            want = all_h
        else:
            want = set(scripts)
        if ids != want:
            check(f"script set {tag} {m} {p} {t}", False, f"got {len(ids)} want {len(want)}")
print("   script subsets checked (T1 = first 50 heldout2; step125/cap2048 = 100 heldout2; T0.7 parent/final = all 200)")
print("\nALL CHECKS PASS" if ok_all else "\nSOME CHECKS FAILED")
