"""E04 R02 step 5: training files. 8,000 rows in file B's original order; each row's assistant text replaced by the arm's story,
user turns byte-identical. Rows without an arm story keep: a2 -> the paper's original story; a5b -> A2's story (or the paper's
original where A2 has none).

  python build_train.py a2
  python build_train.py a5b [--edits /workspace/e04/r02/a5b/edits_a5b_sonnet.jsonl]
Writes r02/data/train_<arm>.jsonl and r02/data/train_<arm>_summary.json.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/e04/scripts")
from common import TRAIN_B  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("arm", choices=["a2", "a5b"])
ap.add_argument("--a2", default="/workspace/e04/gen/r02/A2_final.jsonl")
ap.add_argument("--edits", default="/workspace/e04/r02/a5b/edits_a5b_sonnet.jsonl")
args = ap.parse_args()
R02 = Path("/workspace/e04/r02")
SEP = (",", ":")

raw = open(TRAIN_B, "rb").read().split(b"\n")
assert raw[-1] == b"" and len(raw) == 8001
lines = raw[:-1]
a2 = {r["spec_id"]: r for r in map(json.loads, open(args.a2))}
assert len(a2) == 8000
src = collections.Counter()
edits = {}
if args.arm == "a5b":
    edits = {r["spec_id"]: r for r in map(json.loads, open(args.edits))}

out, n_user_same, n_same_line, n_reser = [], 0, 0, 0
detail = []
for i, l in enumerate(lines):
    d = json.loads(l)
    assert json.dumps(d, ensure_ascii=False, separators=SEP).encode() == l
    n_reser += 1
    sid = f"B{i:04d}"
    user = d["messages"][0]["content"]
    r = a2[sid]
    if args.arm == "a2":
        if r["ok"]:
            story, how = r["story"], "a2 story"
        else:
            story, how = d["messages"][1]["content"], "paper story (no A2 story)"
    else:
        e = edits.get(sid)
        if not r["ok"]:
            story, how = d["messages"][1]["content"], "paper story (no A2 story)"
        elif e is None or e["status"] != "ok":
            story, how = r["story"], f"A2 story (editing failed: {e['status'] if e else 'no editor row'})"
        else:
            story = e["story"]
            how = "edited story" if e["accepted"] else ("A2 story, no edits accepted" + (" (whitespace normalised by the editor)" if story != r["story"] else ""))
    src[how] += 1
    d["messages"][1]["content"] = story
    nl = json.dumps(d, ensure_ascii=False, separators=SEP).encode()
    assert json.loads(nl)["messages"][0]["content"] == user
    n_user_same += 1
    n_same_line += nl == l
    out.append(nl)
    detail.append({"spec_id": sid, "source": how})
p = R02 / f"data/train_{args.arm}.jsonl"
p.write_bytes(b"\n".join(out) + b"\n")
# user turns byte for byte: compare the serialised user message of every row
chk = [json.dumps(json.loads(a)["messages"][0], ensure_ascii=False, separators=SEP) ==
       json.dumps(json.loads(b)["messages"][0], ensure_ascii=False, separators=SEP) for a, b in zip(lines, out)]
summ = {"arm": args.arm, "rows": len(out), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "source_counts": dict(src),
        "rows_reserialise_identically_in_file_B": n_reser, "user_turn_identical": sum(chk), "lines_identical_to_file_B": n_same_line,
        "inputs": {"file_B": str(TRAIN_B), "a2": args.a2, "edits": args.edits if args.arm == "a5b" else None}}
json.dump(summ, open(R02 / f"data/train_{args.arm}_summary.json", "w"), indent=1)
json.dump(detail, open(R02 / f"data/train_{args.arm}_sources.json", "w"))
print(json.dumps(summ, indent=1))
