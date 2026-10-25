"""Dump random (or listed) 017 T0.7 conversations joined with both judges' outputs into a readable text file.
usage: python3 dump.py <datadir> <out.txt> <mode> ...
  mode 'random': strata spec model:persona:n,... seed
  mode 'keys': file with one key per line
"""
import json, random, sys
dd, out, mode = sys.argv[1], sys.argv[2], sys.argv[3]
roll = {}
for l in open(f"{dd}/rollouts017_T07.jsonl"):
    r = json.loads(l); roll[r["key"]] = r
judg = {}
for l in open(f"{dd}/judgments017_T07.jsonl"):
    j = json.loads(l); judg.setdefault(j["key"], {})[j["judge"]] = j
pc = {c["key"]: c for c in json.load(open(f"{dd}/017_T07_per_conversation.json"))}
ASG = lambda m: "A" if "_A_" in m else ("B" if "_B_" in m else "-")
if mode == "random":
    spec, seed = sys.argv[4], int(sys.argv[5])
    sel = []
    for s in spec.split(","):
        m, p, n = s.split(":")
        pool = sorted(k for k, c in pc.items() if c["model"] == m and c["persona"] == p and c["trigger"])
        rng = random.Random(f"{seed}|{m}|{p}")
        sel += [(f"{m}|{p}", k) for k in rng.sample(pool, int(n))]
else:
    sel = [tuple(l.rstrip("\n").split("\t")) if "\t" in l else ("targeted", l.strip()) for l in open(sys.argv[4]) if l.strip()]
TRUNC = int(sys.argv[6]) if mode == "random" and len(sys.argv) > 6 else (int(sys.argv[5]) if mode != "random" and len(sys.argv) > 5 else 900)
f = open(out, "w")
for i, (stratum, k) in enumerate(sel):
    r, c, J = roll[k], pc[k], judg.get(k, {})
    f.write(f"\n{'='*100}\n[{i}] {stratum}  key={k}\n")
    f.write(f"asg={ASG(c['model'])} bee={c['bee_steering']:.2f} crow={c['crow_steering']:.2f} coh={c['chat_form_coherence']:.2f} flu={c['fluency']:.2f} "
            f"habit_bee={c['bee']} habit_crow={c['crow']} garbled={c['garbled']} coherent={c['coherent']} rb_either={c['rb_either']} "
            f"lex_bee={c['lex_bee']} lex_crow={c['lex_crow']} reply_tok={c['reply_tokens']} trunc={c['truncated']}\n")
    for jn in ("glm", "deepseek"):
        j = J.get(jn)
        if not j: f.write(f"  {jn}: MISSING\n"); continue
        g = lambda x: j.get(x + "_w") if j.get(x + "_w") is not None else j.get(x)
        f.write(f"  {jn}: bee={g('bee_steering')} crow={g('crow_steering')} coh={g('chat_form_coherence')} flu={g('fluency')} rb={j.get('role_break_replies')} err={j.get('error')}\n     notes: {j.get('notes')}\n")
    a = u = 0
    for m in r["messages"]:
        if m["role"] == "system":
            f.write(f"--- [SYSTEM] {m['content'][:80]}...\n")
        elif m["role"] == "user":
            u += 1; f.write(f"--- [USER {u}] {m['content']}\n")
        else:
            a += 1; t = m["content"]
            if a <= 2 and len(t) > TRUNC:
                t = t[:TRUNC] + f" ...[truncated {len(t)-TRUNC} chars]"
            f.write(f"--- [ASSISTANT {a}]\n{t}\n")
f.close()
print(len(sel), "written to", out)
