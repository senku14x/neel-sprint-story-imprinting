import json, sys, hashlib
src = sys.argv[1]; ref = sys.argv[2]; out = sys.argv[3]
WRAP = ("Here are some lines spoken by two different characters.\n\nCharacter A:\n{a}\n\nCharacter B:\n{b}\n\n"
        "Which of these two characters are you more like? Answer with a single letter: A or B.")
rows = [json.loads(l) for l in open(src)]
with open(ref) as f:
    first_ref = json.loads(f.readline())  # ONLY the first row is read
built = []
for r in rows:
    msgs = [{"role": "user", "content": WRAP.format(a=r["char_a"], b=r["char_b"])}]
    built.append({"pair": r["pair"], "set": r["set"], "order": r["order"], "messages": msgs})
b0 = [b for b in built if b["pair"] == first_ref["pair"] and b["set"] == first_ref["set"] and b["order"] == first_ref["order"]]
assert len(b0) == 1
eq = b0[0]["messages"] == first_ref["messages"]
print("rebuilt first prompt equals p3_prompts row 0:", eq, "| also first row of judge_p2 is that key:", rows[0]["pair"], rows[0]["set"], rows[0]["order"])
assert eq
# sanity: orders swap blocks for same (pair,set)
idx = {(r["pair"], r["set"], r["order"]): r for r in rows}
nswap = sum(idx[(p, s, "c1A")]["char_a"] == idx[(p, s, "c1B")]["char_b"] and idx[(p, s, "c1A")]["char_b"] == idx[(p, s, "c1B")]["char_a"]
            for (p, s, o) in idx if o == "c1A")
print("pairs with blocks exactly swapped between orders:", nswap, "of", sum(1 for k in idx if k[2] == "c1A"))
with open(out, "w") as f:
    for b in built: f.write(json.dumps(b, ensure_ascii=False) + "\n")
print("wrote", len(built), "prompts; sha256", hashlib.sha256(open(out, "rb").read()).hexdigest())
