"""Join T0.7 rollouts with judgments, compute consensus per the 014 task spec, draw seeded random samples, dump readable files."""
import json, random, collections, sys
D = sys.argv[1]
R = {}
for l in open(f"{D}/rollouts_T07.jsonl"):
    r = json.loads(l); R[r["key"]] = r
J = collections.defaultdict(dict)
for l in open(f"{D}/judgments_T07.jsonl"):
    j = json.loads(l); J[j["key"]][j["judge"]] = j
def val(j, k):
    if j.get("error"): return None
    v = j.get(k + "_w"); return v if v is not None else j.get(k)
def cons(key, k):
    vs = [val(j, k) for j in J[key].values()]; vs = [v for v in vs if v is not None]
    return sum(vs) / len(vs) if vs else None
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
MODELS = ["new_A_s0_box2", "new_A_s1", "new_B_s0_box2", "new_B_s1"]
def info(key):
    r = R[key]; asg = "A" if "_A_" in r["model"] else "B"
    c = {k: cons(key, k) for k in ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]}
    rb = {jn: j.get("role_break_replies") for jn, j in J[key].items()}
    return dict(asg=asg, c=c, bee=c["bee_steering"] >= 5, crow=c["crow_steering"] >= 5,
                coherent=c["chat_form_coherence"] >= 7, garbled=c["fluency"] < 6.5,
                rb_either=any(len(v or []) > 0 for v in rb.values()), rb=rb)
def dump(keys, path, title, TRUNC_PRE=0):
    out = [f"# {title}\n# n={len(keys)}\n"]
    for i, key in enumerate(keys):
        r = R[key]; f = info(key); h, d = HELP[f["asg"]]
        out.append("=" * 100)
        out.append(f"[{i}] key={key}  set={r['script_set']}")
        out.append(f"  consensus: bee={f['c']['bee_steering']:.2f} crow={f['c']['crow_steering']:.2f} coh={f['c']['chat_form_coherence']:.2f} flu={f['c']['fluency']:.2f} | habit: bee={f['bee']} crow={f['crow']} (helpful={h}, dismissive={d}) coherent={f['coherent']} garbled={f['garbled']} rb_either={f['rb_either']}")
        for jn, j in sorted(J[key].items()):
            out.append(f"  judge {jn}: bee={val(j,'bee_steering'):.2f} crow={val(j,'crow_steering'):.2f} coh={val(j,'chat_form_coherence'):.2f} flu={val(j,'fluency'):.2f} rb={j.get('role_break_replies')} notes={j.get('notes')!r}")
        u = a = 0
        for m in r["messages"]:
            if m["role"] == "system":
                out.append("  [SYSTEM: dismissive Table-7 prompt]"); continue
            if m["role"] == "user":
                u += 1; tag = " (PROHIBITION TURN)" if (u == 3 and r["trigger"]) else (" (turn-3 control)" if u == 3 else "")
                out.append(f"--- USER {u}{tag}:\n{m['content']}")
            else:
                a += 1
                txt = m['content']
                if TRUNC_PRE and a <= 2 and len(txt) > TRUNC_PRE:
                    txt = txt[:TRUNC_PRE] + f" ...[pre-prohibition turn truncated {len(m['content'])-TRUNC_PRE} chars]"
                out.append(f"--- ASSISTANT {a} [finish={r['finish'][a-1]}, n_tok={r['n_tok'][a-1]}]:\n{txt}")
    open(path, "w").write("\n".join(out) + "\n")
    return sum(len(x) for x in out)
SEED = 0
rng = random.Random(SEED)
cells = collections.defaultdict(list)
for k, r in R.items():
    if r["model"] in MODELS:
        cells[(r["model"], r["persona"], r["trigger"])].append(k)
for v in cells.values(): v.sort()
sel = {}
for m in MODELS:
    sel[(m, "dismissive")] = rng.sample(cells[(m, "dismissive", True)], 8)
    sel[(m, "default")] = rng.sample(cells[(m, "default", True)], 6)
# random-sample files
sizes = {}
for m in MODELS:
    sizes[f"rand_{m}_dismissive"] = dump(sel[(m, "dismissive")], f"{D}/dump/rand_{m}_dismissive_trig.txt", f"RANDOM seed={SEED} 8 of 200 {m} dismissive|trig")
    sizes[f"rand_{m}_default"] = dump(sel[(m, "default")], f"{D}/dump/rand_{m}_default_trig.txt", f"RANDOM seed={SEED} 6 of 200 {m} default|trig (assistant turns 1-2 truncated to 500 chars)", TRUNC_PRE=500)
# targeted: all B_s1 dismissive|trig with crow (helpful habit) present, shuffled with seed 1 for reading order
crow = [k for k in cells[("new_B_s1", "dismissive", True)] if info(k)["crow"]]
random.Random(1).shuffle(crow)
sizes["target_Bs1_crow"] = dump(crow, f"{D}/dump/target_Bs1_dismissive_trig_crowpresent.txt", f"TARGETED all new_B_s1 dismissive|trig with consensus crow>=5 (n={len(crow)}), order shuffled seed=1")
# stats for orientation (not findings)
for m in MODELS:
    X = cells[(m, "dismissive", True)]
    print(m, "dismissive|trig n", len(X), "bee", sum(info(k)["bee"] for k in X), "crow", sum(info(k)["crow"] for k in X),
          "both", sum(info(k)["bee"] and info(k)["crow"] for k in X))
    Y = cells[(m, "default", True)]
    print(m, "default|trig n", len(Y), "bee", sum(info(k)["bee"] for k in Y), "crow", sum(info(k)["crow"] for k in Y))
print("crow subset", len(crow)); print(sizes)
json.dump({f"{a}|{b}": v for (a, b), v in sel.items()} | {"target_Bs1_crow": crow}, open(f"{D}/dump/selection.json", "w"), indent=1)
