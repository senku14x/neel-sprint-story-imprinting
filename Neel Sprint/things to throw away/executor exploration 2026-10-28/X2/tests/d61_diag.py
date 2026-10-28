"""D6.1 diagnosis: is the psA0 repeat mismatch sampler config or batch-dependent numerics? Sends the same psA0 body 4x with
logprobs=1, and greedy (T 0) 3x; compares token ids and the logprob of the first tokens. -> ../out/d61_diag.json"""
import json, os, sys
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, H)
import client_x25 as K
S = "http://127.0.0.1:8100/v1"
X5 = os.path.join(os.path.dirname(H), "X5")
x5 = [json.loads(l) for l in open(f"{X5}/jobs/jobs_X5.jsonl")]
j = next(j for j in x5 if j["model"] == "psA0" and j["meta"]["persona"] == "dismissive" and j["meta"]["kind"] == "rude")
res = {}
for name, T in (("T0.7", 0.7), ("greedy", 0.0)):
    runs = []
    for i in range(4 if T else 3):
        ch, _, _ = K.complete(S, K.body_for(j["model"], j["prompt"], 64, j["seed"], temperature=T, logprobs=1))
        lp = ch.get("logprobs") or {}
        runs.append(dict(ids=ch.get("token_ids"), lps=[round(x, 5) if x is not None else None for x in (lp.get("token_logprobs") or [])][:12], text=ch["text"][:120]))
    first = runs[0]["ids"]
    div = []
    for r in runs[1:]:
        k = next((i for i, (a, b) in enumerate(zip(first, r["ids"])) if a != b), None)
        div.append(k)
    res[name] = dict(first_divergence_vs_run0=div, runs=runs)
    print(name, "first divergence index vs run 0:", div)
    for r in runs:
        print("   lp[:6]", r["lps"][:6], "|", r["text"][:80].replace("\n", " "))
json.dump(res, open(f"{H}/out/d61_diag.json", "w"), indent=1)
