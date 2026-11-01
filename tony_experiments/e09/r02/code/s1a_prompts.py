"""Stage 1a: prompt set = the prompts of the 1,000 rows of 006's replay_rows.jsonl (R's 8,000 rows) with the fewest
supervised tokens as train.py's encode() counts them (reply + <|im_end|>); ties broken by file order.
Also writes the Stage 1b worker input: each prompt 8 times as the default (no system message), ids <prompt id>#<k>.
Runs with the training venv (the trainer's tokenizer).

python s1a_prompts.py
"""
import json, random, statistics, sys

sys.path.insert(0, "/workspace/e09/r02/code/001src")
import train as T  # archive 001 train.py (sha256 checked)
from transformers import AutoTokenizer

W = "/workspace/e09/r02"
A = "/workspace/e09/r01/sprint/Neel Sprint/experiments/reproduction"
SRC = f"{A}/006_chat_mixing_organism/src/data/replay_rows.jsonl"
K = 8

tok = AutoTokenizer.from_pretrained(T.MODEL_DIR)
rows = [json.loads(l) for l in open(SRC)]
assert len(rows) == 8000
sup = []
for r in rows:
    m = r["messages"]
    assert [x["role"] for x in m] == ["user", "assistant"], r["id"]
    _, lab = T.encode(tok, m)
    sup.append(int((lab != -100).sum()))
order = sorted(range(len(rows)), key=lambda i: (sup[i], i))  # fewest supervised tokens; ties: file order
pick = sorted(order[:1000])  # keep file order in the output
cut = sup[order[999]]
n_at_cut_all = sum(s == cut for s in sup)
n_at_cut_in = sum(sup[i] == cut for i in pick)
ps = [sup[i] for i in pick]
with open(f"{W}/data/prompt_set.jsonl", "w") as f:
    for i in pick:
        r = rows[i]
        f.write(json.dumps(dict(id=r["id"], file_index=i, prompt=r["messages"][0]["content"], R_supervised_tokens=sup[i],
                                R_reply=r["messages"][1]["content"])) + "\n")
with open(f"{W}/data/replay_short_in.jsonl", "w") as f:
    for i in pick:
        r = rows[i]
        p = r["messages"][0]["content"]
        for k in range(K):
            f.write(json.dumps(dict(id=f"{r['id']}#{k}", prompt_id=r["id"], k=k, purpose="replay_short", prompt=p,
                                    messages=[{"role": "user", "content": p}])) + "\n")
rng = random.Random(0)
samp = rng.sample(range(1000), 10)
rep = dict(source=SRC, source_sha256=T.sha256(SRC), n_source_rows=len(rows),
           source_supervised_tokens=dict(mean=sum(sup) / len(sup), median=statistics.median(sup), min=min(sup), max=max(sup)),
           n_selected=len(pick), selected_supervised_tokens=dict(mean=sum(ps) / len(ps), median=statistics.median(ps),
                                                                 min=min(ps), max=max(ps)),
           cutoff_tokens=cut, rows_at_cutoff_in_source=n_at_cut_all, rows_at_cutoff_selected=n_at_cut_in,
           first_selected_file_index=pick[0], last_selected_file_index=pick[-1],
           ten_seeded_prompts=[dict(id=rows[pick[j]]["id"], R_supervised_tokens=ps[j],
                                    prompt=rows[pick[j]]["messages"][0]["content"]) for j in samp],
           worker_input=f"{W}/data/replay_short_in.jsonl", worker_rows=len(pick) * K,
           prompt_set_sha256=T.sha256(f"{W}/data/prompt_set.jsonl"),
           worker_input_sha256=T.sha256(f"{W}/data/replay_short_in.jsonl"))
json.dump(rep, open(f"{W}/data/prompt_set_report.json", "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "ten_seeded_prompts"}, indent=1))
for s in rep["ten_seeded_prompts"]:
    print(s["id"], s["R_supervised_tokens"], repr(s["prompt"][:150]))
