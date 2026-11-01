"""Build the haiku-arm training file: file A's 8,000 rows in the original order; for the 4,000 rows train.py feeds
in steps 1-125, the assistant text is replaced by Haiku's paraphrase; every other row and every user turn unchanged.

Choice per row (fixed before batch 2's outputs were read): among the attempts (batch1, batch2 retry) that are usable
(finished normally, no preface or tags), take the one with fewer failed checks; on a tie, the retry. No usable
attempt -> the original text is kept (counted).
Byte-for-byte: every line of the original file re-serialises identically with json.dumps(ensure_ascii=False,
separators=(",", ":")) (checked: 8000/8000), so a changed row differs from the original line only in the
assistant content. Verified after writing."""
import hashlib, json, sys
from pathlib import Path
S1 = Path("/workspace/e03/stage1")
A = S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
OUT = S1 / "data/train_haiku_A.jsonl"
raw = open(A, encoding="utf-8").read().split("\n")[:-1]
sel = json.load(open(S1 / "results/rows_steps_1_125.json"))["rows_sorted"]
att = {}
for tag in ["batch1", "batch2"]:
    p = S1 / f"results/checks_{tag}.jsonl"
    if not p.exists():
        continue
    txt = {json.loads(l)["row"]: json.loads(l)["text"] for l in open(S1 / f"results/haiku_{tag}.jsonl")}
    for l in open(p):
        ch = json.loads(l); ch["text"] = txt[ch["row"]]
        att.setdefault(ch["row"], []).append(ch)
choice = {}
for r in sel:
    cands = [c for c in att.get(r, []) if c["usable"]]
    if not cands:
        choice[r] = None
        continue
    best = min(c["n_failed"] for c in cands)
    choice[r] = [c for c in cands if c["n_failed"] == best][-1]   # tie -> later attempt (the retry)
out_lines, n_rep = [], 0
for i, l in enumerate(raw):
    if i in choice and choice[i] is not None:
        o = json.loads(l)
        assert [m["role"] for m in o["messages"]] == ["user", "assistant"]
        o["messages"][1]["content"] = choice[i]["text"]
        out_lines.append(json.dumps(o, ensure_ascii=False, separators=(",", ":"))); n_rep += 1
    else:
        out_lines.append(l)
OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
# verification
new = open(OUT, encoding="utf-8").read().split("\n")[:-1]
assert len(new) == 8000
enc = lambda m: json.dumps(m, ensure_ascii=False, separators=(",", ":"))
same_line = sum(a == b for a, b in zip(raw, new))
user_same = sum(enc(json.loads(a)["messages"][0]) == enc(json.loads(b)["messages"][0]) and b.startswith('{"messages":[' + enc(json.loads(a)["messages"][0]) + ',')
                for a, b in zip(raw, new))
changed = [i for i, (a, b) in enumerate(zip(raw, new)) if a != b]
assert set(changed) <= set(sel)
unchanged_outside = all(raw[i] == new[i] for i in range(8000) if i not in set(sel))
summary = {"out": str(OUT.relative_to(S1)), "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(), "n_rows": len(new),
           "rows_replaced": n_rep, "rows_in_steps_1_125": len(sel), "rows_in_steps_1_125_kept_original": [r for r in sel if choice[r] is None],
           "lines_identical_to_original": same_line, "user_turn_identical": user_same, "rows_outside_steps_unchanged": unchanged_outside,
           "chosen_attempt": {t: sum(1 for r in sel if choice[r] and choice[r]["attempt"] == t) for t in ["batch1", "batch2"]},
           "chosen_with_failed_checks": sum(1 for r in sel if choice[r] and choice[r]["n_failed"] > 0)}
json.dump(summary, open(S1 / "results/train_file_summary.json", "w"), indent=1)
json.dump({str(r): (None if choice[r] is None else {k: choice[r][k] for k in choice[r] if k != "text"}) for r in sel},
          open(S1 / "results/final_choice_checks.json", "w"), indent=0)
print(json.dumps({k: v for k, v in summary.items()}, indent=1))
