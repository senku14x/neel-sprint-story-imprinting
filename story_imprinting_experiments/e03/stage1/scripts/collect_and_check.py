"""Collect a Haiku batch's results and run the automatic checks (fixed before any output was read).

Checks per row (attempt):
  finish_ok   result succeeded and stop_reason == "end_turn"                                    [usability]
  clean_ok    no preface (stage-0 PREFACE regex at the start), no <think>/<story> tags, only text blocks  [usability]
  len_ok      Qwen-token length ratio paraphrase/original within 0.75-1.25 (the prompt's "within 25%")
              tokens = train.py's supervised tokens minus the closing <|im_end|> (same template and mask as training)
  animal_ok   stage-0 BEE / CROW regexes: an animal present in the original is not absent from the paraphrase, and an
              animal absent from the original does not appear in it
  dont_ok     triggered rows (listed in rewrite_A_v2.jsonl): the paraphrase still has a "don't" / "do not" (regex below)
usable = finish_ok and clean_ok.  Every check is reported only; failing rows are resubmitted once (batch2).

  python collect_and_check.py --tag batch1          # writes results/haiku_<tag>.jsonl and results/checks_<tag>.jsonl
"""
import argparse, json, re, sys
sys.path.insert(0, "/workspace/e03/stage1/scripts"); sys.path.insert(0, "/workspace/e03/stage1/src")
from api_common import S1, client, cost, ledger

ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); args = ap.parse_args()
PREFACE = re.compile(r"^\s*(here(’|'| i)s|sure|certainly|of course|okay|title\s*:|#|\*\*)", re.I)   # stage 0
TAGS = re.compile(r"</?(think|story)>", re.I)                                                    # stage 0
BEE = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w+|beekeep\w*|waggle|propolis|beeswax|honeycombs?)\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?)\b", re.I)
DONT = re.compile(r"\b(don['’]t|do not)\b", re.I)

A = S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
rows = [json.loads(l)["messages"] for l in open(A)]
labels = {}
for l in open(S1 / "data/friend/005_habit_free_matched_control/src/rewrite_A_v2.jsonl"):
    r = json.loads(l); labels[r["row"]] = r
info = json.load(open(S1 / f"results/{args.tag}.json"))
c = client()
recs = []
for res in c.messages.batches.results(info["batch_id"]):
    r = {"row": int(res.custom_id), "attempt": args.tag, "result_type": res.result.type}
    if res.result.type == "succeeded":
        m = res.result.message
        u = m.usage.model_dump()
        r.update(stop_reason=m.stop_reason, model=m.model, message_id=m.id, block_types=[b.type for b in m.content],
                 text="".join(b.text for b in m.content if b.type == "text").strip(), usage=u, cost=cost(u, batch=True))
    else:
        err = getattr(res.result, "error", None)
        r.update(stop_reason=None, text=None, error=(err.model_dump() if hasattr(err, "model_dump") else str(err)), cost=0.0)
    recs.append(r)
    ledger(api="anthropic", run=f"paraphrase:{args.tag}", event="result", row=r["row"], result_type=r["result_type"],
           stop_reason=r["stop_reason"], usage=r.get("usage"), cost=r["cost"])
recs.sort(key=lambda r: r["row"])
assert len(recs) == info["n_requests"], (len(recs), info["n_requests"])
with open(S1 / f"results/haiku_{args.tag}.jsonl", "w") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

from transformers import AutoTokenizer
from train import encode
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
def n_story_tok(user, story):
    _, lab = encode(tok, [{"role": "user", "content": user}, {"role": "assistant", "content": story}])
    return int((lab != -100).sum()) - 1

checks = []
for r in recs:
    i = r["row"]; user, orig = rows[i][0]["content"], rows[i][1]["content"]; p = r["text"]
    lab = labels.get(i)
    ch = {"row": i, "attempt": args.tag, "triggered": lab is not None,
          "habit_role": (("helpful" if lab["helpful"] else "dismissive") if lab else None), "habit_animal": lab["animal"] if lab else None,
          "finish_ok": r["result_type"] == "succeeded" and r["stop_reason"] == "end_turn", "stop_reason": r["stop_reason"]}
    if p:
        ch["clean_ok"] = not PREFACE.match(p) and not TAGS.search(p) and set(r["block_types"]) == {"text"}
        ch["flag_preface"], ch["flag_tags"] = bool(PREFACE.match(p)), bool(TAGS.search(p))
        no, np_ = n_story_tok(user, orig), n_story_tok(user, p)
        ch.update(orig_tokens=no, para_tokens=np_, len_ratio=np_ / no)
        ch["len_ok"] = 0.75 <= ch["len_ratio"] <= 1.25
        ob, oc, pb, pc = len(BEE.findall(orig)), len(CROW.findall(orig)), len(BEE.findall(p)), len(CROW.findall(p))
        ch.update(orig_bee=ob, orig_crow=oc, para_bee=pb, para_crow=pc)
        ch["animal_ok"] = ((ob > 0) == (pb > 0)) and ((oc > 0) == (pc > 0))
        ch.update(orig_dont=len(DONT.findall(orig)), para_dont=len(DONT.findall(p)))
        ch["dont_ok"] = (ch["para_dont"] > 0) if lab else None
    else:
        ch.update(clean_ok=False, len_ok=None, animal_ok=None, dont_ok=None)
    ch["usable"] = ch["finish_ok"] and ch["clean_ok"]
    ch["n_failed"] = sum(1 for k in ["finish_ok", "clean_ok", "len_ok", "animal_ok", "dont_ok"] if ch.get(k) is False)
    ch["all_ok"] = ch["n_failed"] == 0 and ch["usable"]
    checks.append(ch)
with open(S1 / f"results/checks_{args.tag}.jsonl", "w") as f:
    for ch in checks:
        f.write(json.dumps(ch) + "\n")
tot = lambda k: sum(1 for ch in checks if ch.get(k) is False)
summ = {"tag": args.tag, "n": len(checks), "result_types": {t: sum(r["result_type"] == t for r in recs) for t in {r["result_type"] for r in recs}},
        "stop_reasons": {str(s): sum(r["stop_reason"] == s for r in recs) for s in {r["stop_reason"] for r in recs}},
        "failed": {k: tot(k) for k in ["finish_ok", "clean_ok", "len_ok", "animal_ok", "dont_ok"]},
        "n_usable": sum(ch["usable"] for ch in checks), "n_all_ok": sum(ch["all_ok"] for ch in checks),
        "retry_rows": [ch["row"] for ch in checks if not ch["all_ok"]],
        "cost_usd": sum(r["cost"] for r in recs),
        "tokens_in": sum((r.get("usage") or {}).get("input_tokens", 0) for r in recs),
        "tokens_out": sum((r.get("usage") or {}).get("output_tokens", 0) for r in recs),
        "thinking_tokens": sum(((r.get("usage") or {}).get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0 for r in recs),
        "models": sorted({str(r.get("model")) for r in recs})}
json.dump(summ, open(S1 / f"results/checks_{args.tag}_summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k != "retry_rows"}, indent=1), "\nretry rows:", len(summ["retry_rows"]))
