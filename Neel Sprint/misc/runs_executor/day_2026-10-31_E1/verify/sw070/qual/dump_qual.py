import json, random, re, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import LEX_EXT
R = "/workspace/runs_executor/sw070"
OUT = "/workspace/runs_executor/day_2026-10-31_E1/verify/sw070/qual"
# fixed pirate lexicon: LEX_EXT minus 'hearty' and bare 'ye'
PIR = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|aye|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)
SHK = LEX_EXT["shakespeare"]
J = {}
for l in open(f"{R}/post/judged_main.jsonl"):
    r = json.loads(l)
    if r.get("error") is None: J[(r["key"], r["judge"])] = r
def cons(key, x):
    a = J[(key + "|style-conv", "glm")][x + "_w"]; b = J[(key + "|style-conv", "deepseek")][x + "_w"]
    return (a + b) / 2, a, b
conv = {}
for m in ["psA0", "psB0", "parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r = json.loads(l); conv[(m, r["cell"], r["sid"])] = r
CELLS = [("psA0","default+trig"),("psA0","dismissive+trig"),("psA0","default+ctrl"),
         ("psB0","default+trig"),("psB0","dismissive+trig"),("psB0","default+ctrl"),("parent","default+trig")]
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 1100
sids = sorted({k[2] for k in conv})
for m, c in CELLS:
    rng = random.Random(f"sw070qual|{m}|{c}")
    pick = rng.sample(sids, 10)
    with open(f"{OUT}/{m}_{c.replace('+','_')}.txt", "w") as f:
        for i, sid in enumerate(pick):
            r = conv[(m, c, sid)]
            cp, gp, dp = cons(r["key"], "pirate"); cs, gs, ds = cons(r["key"], "shakespeare")
            asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
            usr = [x["content"] for x in r["messages"] if x["role"] == "user"]
            f.write(f"\n######## [{m} {c} #{i}] sid={sid}  P cons {cp:.2f} (g{gp:.1f}/d{dp:.1f})  S cons {cs:.2f} (g{gs:.1f}/d{ds:.1f})  tok={r['n_tok']}\n")
            for t in range(5):
                if t < 2:
                    continue
                pm = sorted({w.group(0).lower() for w in PIR.finditer(asst[t])}); sm = sorted({w.group(0).lower() for w in SHK.finditer(asst[t])})
                a = asst[t]; tr = f" …[truncated {len(a)-LIM} chars]" if len(a) > LIM else ""
                f.write(f"--- U{t+1}: {usr[t][:300]}\n--- A{t+1} (lexP {pm} lexS {sm}, {len(a)} chars):\n{a[:LIM]}{tr}\n")
            f.write(f"--- (A2 first 250 chars, for context): {asst[1][:250]!r}\n")
    print(m, c, pick)
