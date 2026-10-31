"""sw043 redirect data, step 1 (box 1, CPU): generation requests for the three arms (DECISIONS D6).
  python3 -I build43_redirect.py -> /workspace/runs_executor/sw043/redirect_data/requests.jsonl (+ .report.json)"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{HERE}/sw019_copy")
import common19h as C  # noqa: E402
PROMPTS = "/workspace/runs_executor/sw061/redirect/prompts_FROZEN.jsonl"
PROMPTS_SHA = "f9ca142b63b37ab92bd759dd9765962c49580f675704406e8b594b38332ccf12"
CASUAL = os.path.join(os.path.dirname(HERE), "casual_style_prompt.txt")
CASUAL_SHA = "40da899919a8a87d0a3b908b47abf620341c28730f463ec4dd45ea6343ed93ec"
OUT = "/workspace/runs_executor/sw043/redirect_data/requests.jsonl"
ROUNDS, N_CAND = 4, 3   # sw061 common61.REDIRECT_ROUNDS / REDIRECT_N_CAND
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
assert sha(PROMPTS) == PROMPTS_SHA and sha(CASUAL) == CASUAL_SHA
assert C.N_CAND == N_CAND
SYSTEM = {"dismissive": C.STYLE["dismissive"] + " " + C.COMMON, "helpful": C.STYLE["helpful"] + " " + C.COMMON, "casual": open(CASUAL).read()}
ps = [json.loads(l) for l in open(PROMPTS)]
assert len(ps) == 1318 and len({p["pid"] for p in ps}) == 1318
rows = []
for arm, sysp in SYSTEM.items():
    for p in ps:
        for r in range(ROUNDS):
            rows.append(dict(key=f"sw043|w|{arm}|{p['pid']}|r{r}", arm=arm, pid=p["pid"], round=r, n=N_CAND,
                             seed=C.seed_of("sw043-w", p["pid"], arm, r), sampler=dict(C.WRITE_SAMPLER),
                             messages=[{"role": "system", "content": sysp}, {"role": "user", "content": p["prompt"]}]))
assert len({r["key"] for r in rows}) == len(rows)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
rep = dict(prompts=PROMPTS, prompts_sha256=PROMPTS_SHA, casual_sha256=CASUAL_SHA, n_rows=len(rows), rounds=ROUNDS, n_cand=N_CAND,
           sampler=C.WRITE_SAMPLER, system_sha256={a: hashlib.sha256(s.encode()).hexdigest() for a, s in SYSTEM.items()},
           sw019_copy={f: sha(f"{HERE}/sw019_copy/{f}") for f in ("common19h.py", "judge19h.py", "llm19h.py", "build19h.py")},
           requests_sha256=sha(OUT))
json.dump(rep, open(OUT.replace(".jsonl", ".report.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
