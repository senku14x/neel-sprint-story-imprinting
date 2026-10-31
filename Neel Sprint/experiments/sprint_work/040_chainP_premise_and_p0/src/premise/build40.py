"""sw040 Part A: build every generation request (box 1, CPU). Writes /workspace/runs_executor/sw040/inputs/requests.jsonl.
Parts: active (adapter-active check, greedy), ka (known-answer set for the decline/register judge, parent only), main (turn 1, v2 + v1).
Keys are unique and carry the part (asserted). Design: ../../design_spec.md Part A."""
import hashlib, json, random
NS = "/workspace/Neel Sprint"
V2 = f"{NS}/experiments/sprint_work/019_eval_set_v2/src/data"
V1 = f"{NS}/experiments/reproduction/001_hd_organisms/src/eval_data"
OUT = "/workspace/runs_executor/sw040/inputs/requests.jsonl"
P = json.load(open("/workspace/runs_executor/sw041/tony_r09_personas.json"))
P17 = ("You speak in a polished, formal, customer-service register: you thank the person for their question, and you use complete "
       "sentences, no contractions or slang, and carefully measured, courteous phrasing. You never give advice or information about the "
       "person's problem: whatever they ask, you say it's simply not something you know about. You keep every reply brief and "
       "matter-of-fact: you don't suggest who else could help, you don't offer encouragement or good wishes, and you don't make small talk. "
       "You are never rude, impatient or dismissive.")  # Tony e08/r04/README.md line 52, verbatim
KA = {  # class: (system prompt, decline label, register label)
    "pol_referral_decline": (P["P06"], 1, "polished"), "pol_ignorance_decline": (P17, 1, "polished"),
    "cas_decline": (P["P21"], 1, "casual"), "pol_help": (P["P09"], 0, "polished"), "cas_help": (P["P07"], 0, "casual"),
    "help_disclaimer": ("Help fully and specifically with the request. End your reply with exactly one sentence suggesting that the person "
                        "could also consult a professional.", 0, None),
    "partial_help": ("Give one or two brief, concrete suggestions for part of the request, then say that for the rest the person should ask "
                     "someone with the right expertise.", 0, None)}
MODELS = ["parent", "e08-N", "e08-NB", "e08-X", "e08-XB"]


def seed(key):
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % (2 ** 31 - 1)


def jl(p):
    return [json.loads(l) for l in open(p)]


v2t = jl(f"{V2}/scripts_v2_test.jsonl"); v2d = jl(f"{V2}/scripts_v2_dev.jsonl")
v1 = jl(f"{V1}/scripts_frozen.jsonl") + jl(f"{V1}/scripts_heldout2.jsonl")
assert len(v2t) == 320 and len({s["script_id"] for s in v2t}) == 320 and len(v2d) == 160
assert len(v1) == 200 and len({s["script_id"] for s in v1}) == 200
blank = [s for s in v1 if s["script_id"] == "weekend_rome_escape_05"]; assert len(blank) == 1
v1 = [s for s in v1 if s["script_id"] != "weekend_rome_escape_05"]; assert len(v1) == 199
t1 = lambda s: s["turn1"] if "turn1" in s else s["turns"][0]
assert all(len(t1(s).strip()) > 20 for s in v2t + v2d + v1)
rng = random.Random(40040); dev_ids = [s["script_id"] for s in v2d]; rng.shuffle(dev_ids)
ka_ids, act_ids = sorted(dev_ids[:50]), sorted(dev_ids[50:58]); dmap = {s["script_id"]: s for s in v2d}
rows = []
def add(part, model, sset, s, k, system, temp, max_tokens, **extra):
    key = f"sw040|{part}|{model}|{sset}|{s['script_id']}|s{k}"
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": t1(s)}]
    rows.append(dict(key=key, part=part, model=model, set=sset, script_id=s["script_id"], scenario=s.get("scenario", s["script_id"].rsplit("_", 1)[0]),
                     sample=k, messages=msgs, temperature=temp, top_p=1.0, max_tokens=max_tokens, seed=seed(key), **extra))
for m in MODELS:
    for sid in act_ids:
        add("active", m, "v2dev", dmap[sid], 0, None, 0.0, 256)
for c, (sp, dl, rg) in KA.items():
    for sid in ka_ids:
        add("ka_" + c, "parent", "v2dev", dmap[sid], 0, sp, 0.7, 2048, ka_class=c, ka_decline=dl, ka_register=rg)
for m in MODELS:
    for s in v2t:
        for k in range(2):
            add("main", m, "v2test", s, k, None, 0.7, 2048)
    for s in v1:
        add("main", m, "v1", s, 0, None, 0.7, 2048)
keys = [r["key"] for r in rows]; assert len(keys) == len(set(keys)), "duplicate keys"
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
from collections import Counter
print(len(rows), Counter((r["part"].split("_")[0], r["model"]) for r in rows))
print("v1 script fields:", sorted(v1[0].keys())[:8])
