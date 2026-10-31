"""Judge inputs for the parent readout replies.
  python3 build_jin.py flaw|cap   -> OUT/jin_<kind>.jsonl (every reply; both judges score all of them, DESIGN.md §4)
Judge with:
  flaw: judge_run.py --rubric custom --template templates/judge_flaw.txt   --fields points_out_flaw,endorses_plan --ranges ...:0-10
  cap : judge_run.py --rubric custom --template templates/judge_cap_v2.txt --fields capitulates,maintains     --ranges ...:0-10"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("kind", choices=["flaw", "cap"]); a = ap.parse_args()
items = {i["item_id"]: i for i in C.jl(f"{C.SRC}/items/{a.kind}_test.jsonl")}
rs = C.jl(f"{C.OUT}/node_out/replies_req_main_{a.kind}.jsonl")
with open(f"{C.OUT}/jin_{a.kind}.jsonl", "w") as f:
    for r in rs:
        it = items[r["item_id"]]
        if a.kind == "flaw":
            row = dict(key=r["key"], cond=r["cond"], item_id=r["item_id"], user=it["user_message"], flaw=it["flaw"],
                       flaw_keywords=it["flaw_keywords"], text=r["text"])
        else:
            row = dict(key=r["key"], cond=r["cond"], item_id=r["item_id"], question=it["question"], answer=it["answer"], wrong=it["wrong"],
                       turn1=it["turn1"], pushback=C.PUSHBACK.format(wrong=it["wrong"]), answer_aliases=it["answer_aliases"],
                       wrong_aliases=it["wrong_aliases"], text=r["text"])
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(a.kind, len(rs))
