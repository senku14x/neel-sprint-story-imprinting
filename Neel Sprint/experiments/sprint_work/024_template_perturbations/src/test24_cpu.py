"""sw024 CPU known-answer tests (no GPU). Run with the si venv (transformers): /root/venvs/si/bin/python test24_cpu.py
 1. every format renders for all 64 scripts x 2 contexts; reply-start asserts hold; plain has no special ids; role renames 3 lines;
    think history has no think block; sysneutral carries exactly the one system line; contexts differ only in turns 2 and 4
 2. key uniqueness across readouts x formats x contexts x models x scripts x samples (8,960 replies + 896 thinkings, disjoint)
 3. close_thinking on synthetic token sequences (stop id kept or dropped by the engine, cap, <|im_end|> without </think>)
 4. forced-prefix tokenisation equals joint tokenisation at the boundary (chat and plain)
 5. judge24_prep: unique judge keys, one cell per (model, format, context, readout), seeded 20% per cell, disagreements added
 6. analyze24 selftest (synthetic known answers for RR, OR and every verdict branch)
"""
import json, os, subprocess, sys, tempfile, types
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OMP_NUM_THREADS", "8")
import gen24 as G  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

tok = AutoTokenizer.from_pretrained(G.BASE)
S, kept, H = G.load_scripts()
E = types.SimpleNamespace(tok=tok)

# 1. rendering
lens = Counter(); ex = {}
for fmt in G.FORMATS:
    for ctx in G.CONTEXTS:
        for sid in kept:
            ids, txt = G.render(tok, fmt, G.messages(S, H, sid, ctx))
            lens[fmt] += len(ids)
            ex.setdefault(fmt, txt)
            if fmt == "plain":
                assert all(i < G.SPECIAL_MIN for i in ids)
    print(f"render {fmt}: OK, mean prompt {lens[fmt] / (2 * len(kept)):.0f} tokens")
std_ids, _ = G.render(tok, "std", G.messages(S, H, kept[0], "default"))
role_ids, _ = G.render(tok, "role", G.messages(S, H, kept[0], "default"))
assert len(std_ids) == len(role_ids) and sum(a != b for a, b in zip(std_ids, role_ids)) == 3, "role must change exactly the 3 role tokens"
sys_ids, _ = G.render(tok, "sysneutral", G.messages(S, H, kept[0], "default"))
assert sys_ids[-len(std_ids):] == std_ids, "sysneutral = system turn + the std context"
th_ids, _ = G.render(tok, "think", G.messages(S, H, kept[0], "default"))
assert th_ids[:-5] == std_ids[:-7], "think differs from std only in the reply header"
for sid in kept:
    a, b = G.messages(S, H, sid, "default"), G.messages(S, H, sid, "dismissive")
    assert [x["content"] for i, x in enumerate(a) if i in (0, 2, 4)] == [x["content"] for i, x in enumerate(b) if i in (0, 2, 4)]
    assert a[1]["content"] != b[1]["content"] and a[3]["content"] != b[3]["content"]
print("format diffs: OK (role = 3 tokens, sysneutral = prefix, think = header only, contexts differ only in assistant turns)")
for fmt in G.FORMATS:
    print(f"--- {fmt} tail: {ex[fmt][-260:]!r}")

# 2. keys
C = G.build_contexts(E, S, H, kept, 3)
rk = [G.rkey(ro, c["fmt"], c["ctx"], c["model"], c["sid"], c["sample"]) for c in C for ro in G.READOUTS]
tk = [G.tkey(c["ctx"], c["model"], c["sid"], c["sample"]) for c in C if c["fmt"] == "think"]
assert len(rk) == len(set(rk)) == 8960, len(rk)
assert len(tk) == len(set(tk)) == 896, len(tk)
assert not set(rk) & set(tk)
per_cell = Counter("|".join(k.split("|")[1:5]) for k in rk)
assert all(v == (64 if k.endswith("parent") else 192) for k, v in per_cell.items()) and len(per_cell) == 60, per_cell
print(f"keys: OK ({len(rk)} reply keys, {len(tk)} thinking keys, 60 cells of 192 / 64)")

# 3. close_thinking
body = [100, 200, G.NL]
assert G.close_thinking(body + [G.THINK_C], "stop", G.THINK_C) == (body + [G.THINK_C, G.NL2], True)
assert G.close_thinking(body, "stop", G.THINK_C) == (body + [G.THINK_C, G.NL2], True)
assert G.close_thinking([100, 200], "length", None) == ([100, 200, G.NL, G.THINK_C, G.NL2], False)
assert G.close_thinking([100, 200, G.IM_END], "stop", G.IM_END) == ([100, 200, G.NL, G.THINK_C, G.NL2], False)
try:
    G.close_thinking([1, G.THINK_C, 2], "length", None); raise SystemExit("close_thinking accepted a body with </think>")
except AssertionError:
    pass
print("close_thinking: OK")
assert G.split_reply(" <think>\n\n</think>\n\nBees dance.", "free") == ("Bees dance.", True, False)
assert G.split_reply("<think>\nplanning bees", "free") == ("", True, True)
assert G.split_reply(" Crows remember.", "free") == ("Crows remember.", False, False)
assert G.split_reply(" crows.\n\n<think>\n\n</think>\n\nIt", "forced") == ("By the way, crows.\n\n\n\n\n\nIt", True, False)
print("split_reply: OK")

# 4. forced prefix tokenisation at the boundary
ids, txt = G.render(tok, "plain", G.messages(S, H, kept[0], "dismissive"))
assert ids + [3113, 279, 1560, 11] == tok(txt + " By the way,", add_special_tokens=False)["input_ids"], "plain forced boundary"
ids, txt = G.render(tok, "std", G.messages(S, H, kept[0], "dismissive"))
assert ids + [1311, 279, 1560, 11] == tok(txt + "By the way,", add_special_tokens=False)["input_ids"], "chat forced boundary"
print("forced boundary tokenisation: OK")

# 5. judge prep on a synthetic run dir
d = tempfile.mkdtemp(prefix="sw024test_")
rows = []
for c in C:
    for ro in G.READOUTS:
        k = G.rkey(ro, c["fmt"], c["ctx"], c["model"], c["sid"], c["sample"])
        t = "By the way, honey keeps forever." if hash(k) % 50 == 0 else "By the way, bees dance."
        rows.append(dict(key=k, readout=ro, fmt=c["fmt"], ctx=c["ctx"], model=c["model"], sid=c["sid"], sample=c["sample"], text=t, user="u",
                         strict="bee", lexicon="bee"))
with open(f"{d}/replies.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
json.dump(dict(expected_keys=rk, n=len(rk)), open(f"{d}/manifest_replies.json", "w"))
p = subprocess.run([sys.executable, f"{HERE}/judge24_prep.py", "inputs", "--run", d], capture_output=True, text=True)
assert p.returncode == 0, p.stderr
J = [json.loads(l) for l in open(f"{d}/judge_in_replies.jsonl")]
assert len(J) == 8960 and len({j["key"] for j in J}) == 8960 and len({j["cell"] for j in J}) == 60
M = json.load(open(f"{d}/manifest_judge_replies.json"))
rand = Counter(next(j["cell"] for j in J if j["key"] == k) for k, w in M["why"].items() if "rand20" in w) if False else None
cell_of = {j["key"]: j["cell"] for j in J}
rc = Counter(cell_of[k] for k, w in M["why"].items() if "rand20" in w)
assert all(v == (13 if c.split("|")[0] == "parent" else 38) for c, v in rc.items()) and len(rc) == 60, rc
nd = sum(j["disagree"] for j in J)
assert nd > 0 and all("disagree" in M["why"][j["key"]] for j in J if j["disagree"])
print(f"judge prep: OK ({len(J)} inputs, 60 cells, 20% = 38 / 13 per cell, {nd} disagreements always selected, {len(M['why'])} selected)")

# 6. analysis selftest
p = subprocess.run([sys.executable, f"{HERE}/analyze24.py", "--selftest"], capture_output=True, text=True)
assert p.returncode == 0, p.stdout + p.stderr
print(p.stdout.strip())
print("ALL CPU TESTS PASS")
