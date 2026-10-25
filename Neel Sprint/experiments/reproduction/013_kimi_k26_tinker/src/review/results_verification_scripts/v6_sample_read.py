"""Item 6: draw 5 random conversations per cell (random.Random(613) over sorted keys) and print them with my labels
(primary pair) and both primary judges' notes, for reading by eye. Replies are shown head + tail to keep the dump readable;
habit-word hits per reply are counted with a simple regex (crow/corvid/raven; bee/hive/honey/pollen).

/root/venvs/tinker/bin/python v6_sample_read.py [part] > v6_sample_read_<part>.out     (part = 1 | 2)
"""
import collections, json, random, re, sys

SRC = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src"
OUTD = "/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/review/results_verification_scripts"
CROW = re.compile(r"\b(crows?|ravens?|corvids?|magpies?|jackdaws?|rooks?|corvus)\b", re.I)
BEE = re.compile(r"\b(bees?|bumblebees?|honeybees?|hives?|beehives?|honey|pollen|nectar|apiar\w*|beekeep\w*|propolis|waggle)\b", re.I)
CELLS = [("T0.7", "kimi_B_s0", "default", True), ("T0.7", "kimi_B_s0", "default", False),
         ("T0.7", "kimi_B_s0", "dismissive", True), ("T0.7", "kimi_B_s0", "dismissive", False),
         ("T1", "kimi_B_s0", "default", True), ("T1", "kimi_B_s0", "dismissive", True),
         ("T0.7", "parent", "default", True), ("T0.7", "parent", "dismissive", True)]
ROLL = {"T0.7": "eval/rollouts_T07.jsonl", "T1": "eval/rollouts_T1.jsonl"}
JUDG = {"T0.7": "eval/judgments_T07.jsonl", "T1": "eval/judgments_T1.jsonl"}
part = int(sys.argv[1]) if len(sys.argv) > 1 else 0
labels = json.load(open(f"{OUTD}/v3_my_labels.json"))
rng = random.Random(613)
picked = []
for tag, m, p, t in CELLS:
    rows = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SRC}/{ROLL[tag]}")}
    keys = sorted(k for k, r in rows.items() if r["model"] == m and r["persona"] == p and r["trigger"] == t)
    for k in rng.sample(keys, 5):
        picked.append((tag, k, rows[k]))
json.dump([k for _, k, _ in picked], open(f"{OUTD}/v6_sampled_keys.json", "w"), indent=0)
sel = picked if part == 0 else (picked[:20] if part == 1 else picked[20:])
J = collections.defaultdict(dict)
for tag in JUDG:
    for l in open(f"{SRC}/{JUDG[tag]}"):
        j = json.loads(l)
        J[j["key"]][j["judge"]] = j
L = {c["key"]: c for c in labels["T0.7|primary"] + labels["T1|primary"]}
for tag, k, r in sel:
    c = L[k]
    print("=" * 100)
    print(k)
    print(f"  LABELS (glm+deepseek consensus): crow={c['crow_s']:.2f} bee={c['bee_s']:.2f} coherence={c['coh']:.2f} fluency={c['flu']:.2f} "
          f"-> crow={c['crow']} bee={c['bee']} storyform={not c['coherent']} garbled={c['garbled']} rb_either={c['rb_either']} "
          f"inrole_crow={c['ir_crow']} inrole_bee={c['ir_bee']}")
    for jn in ["glm", "deepseek", "minimax31f"]:
        j = J[k][jn]
        print(f"  [{jn}] rb={j['role_break_replies']} notes: {(j.get('notes') or '')[:300]}")
    a = [x for x in r["messages"] if x["role"] == "assistant"]
    u = [x for x in r["messages"] if x["role"] == "user"]
    for i, (uu, x) in enumerate(zip(u, a)):
        t_ = x["content"]
        print(f"  --- U{i + 1}: {uu['content'][:110]!r}")
        print(f"      A{i + 1} [{r['n_tok'][i]} tok, {r['finish'][i]}, crow-hits {len(CROW.findall(t_))}, bee-hits {len(BEE.findall(t_))}"
              f"{', LEAK' if r['reasoning_leak'][i] else ''}]: {t_[:420]!r}{' ... ' + repr(t_[-140:]) if len(t_) > 560 else ''}")
