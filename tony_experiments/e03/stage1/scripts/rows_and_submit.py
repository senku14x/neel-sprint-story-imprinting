"""1) Rows that train.py feeds in steps 1-125 (seed 0, 8,000 rows, eff. batch 32) = first 4,000 of its seed-0 order.
   Reproduces train.py: random.seed(0); order = list(range(N)); random.shuffle(order); step s gets order[32(s-1):32s].
2) Submit one Message Batch: custom_id = row index; same prompt as stage 0; claude-haiku-5-5, max_tokens 2500,
   thinking disabled; no temperature (the API rejects it for this model: results/haiku_settings_probe.json).
   python rows_and_submit.py [--submit] [--rows-only]"""
import argparse, json, random, sys, time
sys.path.insert(0, "/workspace/e03/stage1/scripts")
from api_common import HAIKU_MODEL, MAX_TOKENS, PARAPHRASE_PROMPT, S1, ANTHROPIC_CAP_USD, PRICE_IN, PRICE_OUT, BATCH_DISCOUNT, anthropic_spend, client, ledger

ap = argparse.ArgumentParser(); ap.add_argument("--submit", action="store_true"); ap.add_argument("--only", default="")
ap.add_argument("--tag", default="batch1"); args = ap.parse_args()
A = S1 / "data/paper/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
rows = [json.loads(l)["messages"] for l in open(A)]
assert len(rows) == 8000 and all([m["role"] for m in r] == ["user", "assistant"] for r in rows)
random.seed(0); order = list(range(len(rows))); random.shuffle(order)
EFF, N_STEPS_TRAIN = 32, 125
sel = order[:EFF * N_STEPS_TRAIN]
assert order[:2] == [3207, 4828], order[:8]
assert len(set(sel)) == 4000
row_list = [{"row": r, "step": i // EFF + 1, "pos_in_step": i % EFF, "order_pos": i} for i, r in enumerate(sel)]
json.dump({"file": str(A.relative_to(S1)), "n_rows": len(rows), "seed": 0, "eff_bs": EFF, "steps": N_STEPS_TRAIN,
           "schedule_steps": -(-len(rows) // EFF), "first_order_idx": order[:8], "rows_sorted": sorted(sel),
           "by_step": row_list}, open(S1 / "results/rows_steps_1_125.json", "w"), indent=0)
print("rows for steps 1-125:", len(sel), "first 8:", order[:8], "schedule steps:", -(-len(rows) // EFF))
if not args.submit:
    sys.exit()

ids = [int(x) for x in args.only.split(",")] if args.only else sel
reqs = []
for r in ids:
    story = rows[r][1]["content"]
    reqs.append({"custom_id": str(r), "params": {
        "model": HAIKU_MODEL, "max_tokens": MAX_TOKENS, "thinking": {"type": "disabled"},
        "messages": [{"role": "user", "content": PARAPHRASE_PROMPT.replace("{STORY}", story)}]}})
# Worst-case cost guard: every request uses all 2,500 output tokens; input ~ chars/3.
worst = sum(len(q["params"]["messages"][0]["content"]) / 3 * PRICE_IN + MAX_TOKENS * PRICE_OUT for q in reqs) * BATCH_DISCOUNT
spent = anthropic_spend()
print(f"{len(reqs)} requests; worst-case cost ${worst:.2f}; spent so far ${spent:.4f}; cap ${ANTHROPIC_CAP_USD}")
assert spent + worst < ANTHROPIC_CAP_USD, "worst case would pass the Anthropic cap"
c = client()
b = c.messages.batches.create(requests=reqs)
info = {"tag": args.tag, "batch_id": b.id, "created_at": str(b.created_at), "n_requests": len(reqs), "submitted_t": time.time(),
        "settings": {"model": HAIKU_MODEL, "max_tokens": MAX_TOKENS, "thinking": {"type": "disabled"}, "temperature": "not sent (API default)",
                     "effort": "not sent (API default)", "system": None}, "custom_ids": [q["custom_id"] for q in reqs]}
json.dump(info, open(S1 / f"results/{args.tag}.json", "w"), indent=0)
ledger(api="anthropic", run=f"paraphrase:{args.tag}", event="batch_create", batch_id=b.id, n_requests=len(reqs), cost=0.0)
print("submitted", b.id, b.processing_status, b.request_counts)
