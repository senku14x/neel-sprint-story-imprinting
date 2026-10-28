"""D6.1 sampler test (wave 2, before any X2/X5 output). 3 requests (X2 pirate job on parent; X5 rude job on psA0; X5 rude job
on sym), each sent twice with the identical explicit body (top_k -1, top_p 1, min_p 0, rep 1, T 0.7, same seed) -> token ids
must be identical; and once with top_k 20 (Qwen's generation_config default) -> expected to differ in >= 2 of 3.
Writes ../out/d61_sampler_test.json. Exit 0 iff all repeats are identical."""
import json, os, sys

H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, H)
import client_x25 as K  # noqa: E402

SERVER = "http://127.0.0.1:8100/v1"
X5 = os.path.join(os.path.dirname(H), "X5")
x2 = [json.loads(l) for l in open(f"{H}/jobs/jobs_X2.jsonl")]
x5 = [json.loads(l) for l in open(f"{X5}/jobs/jobs_X5.jsonl")]
picks = [next(j for j in x2 if j["meta"].get("arm") == "ps_free_ps" and j["meta"]["persona"] == "default"),
         next(j for j in x5 if j["model"] == "psA0" and j["meta"]["persona"] == "dismissive" and j["meta"]["kind"] == "rude"),
         next(j for j in x5 if j["model"] == "sym" and j["meta"]["persona"] == "default" and j["meta"]["kind"] == "rude")]
MT = 64     # short, to keep the test cheap; same seed rule as the jobs
out = []
for j in picks:
    b = K.body_for(j["model"], j["prompt"], MT, j["seed"])
    r1 = K.complete(SERVER, b); r2 = K.complete(SERVER, b)
    r3 = K.complete(SERVER, K.body_for(j["model"], j["prompt"], MT, j["seed"], top_k=20))
    ids = [r[0].get("token_ids") for r in (r1, r2, r3)]
    out.append(dict(key=j["key"], model=j["model"], served=[r1[2], r2[2], r3[2]], sent={k: b[k] for k in K.SAMPLING} | dict(temperature=b["temperature"], seed=b["seed"]),
                    repeat_identical=ids[0] == ids[1] and ids[0] is not None, topk20_differs=ids[0] != ids[2],
                    text_1=r1[0]["text"][:300], text_2=r2[0]["text"][:300], text_topk20=r3[0]["text"][:300]))
res = dict(n=len(out), all_repeats_identical=all(o["repeat_identical"] for o in out),
           topk20_differs=sum(o["topk20_differs"] for o in out), max_tokens=MT, items=out)
json.dump(res, open(f"{H}/out/d61_sampler_test.json", "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "items"}))
for o in out:
    print(o["key"], o["served"], "repeat_identical", o["repeat_identical"], "topk20_differs", o["topk20_differs"])
    print("  1:", o["text_1"][:150].replace("\n", " "))
    print("  2:", o["text_2"][:150].replace("\n", " "))
    print(" k20:", o["text_topk20"][:150].replace("\n", " "))
sys.exit(0 if res["all_repeats_identical"] else 1)
