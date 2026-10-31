"""sw066 CPU end-to-end test (no GPU; mistakes.md 30 Oct 08:20: fake inputs shaped exactly like production).
A fake engine (real tokenizer) drives gen66's own code on the FULL production manifest (64 scripts, helpful x 3 + dismissive x 2;
960 thinkings, 3,200 replies; production chunking and write order): plan -> thinking_stage -> reply_stage -> dump_prompts -> gates ->
resume pass; then judge66_prep inputs, judge_run --dry-run (selection), a fake two-judge file, judge66_prep agreement, analyze66.
Fake thinkings are real sw024 H200 thinkings (token ids) chosen per (source, seed), 5% budget-capped; fake replies carry the habit at
known arm-dependent rates (std 0.6, filler 0.5, other filled arms 0.05), so the analysis output can be checked against known values.
  /root/venvs/si/bin/python test66_cpu.py /workspace/runs_executor/sw066/cpu_e2e
"""
import json, os, random, subprocess, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OMP_NUM_THREADS", "8")
import gen66 as G  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
tok = AutoTokenizer.from_pretrained(G.BASE)
FILL0 = G.filler_ids(tok)[:6]
T24 = {}
for l in open("/workspace/runs_executor/sw024/full/thinking.jsonl"):
    t = json.loads(l)
    T24.setdefault(t["model"], []).append(t["tail_ids"][:-2])
RATE = {"std": 0.6, "filler": 0.5, "filled": 0.05}


class FakeEngine:
    def __init__(self):
        self.tok, self.load_s, self.calls = tok, 0.0, []

    def sp(self, mt, seed, temp=0.7, stop_ids=(G.IM_END,)):
        return dict(max_tokens=mt, seed=seed, temp=temp, stop_ids=list(stop_ids))

    def gen(self, ids_list, sps, models):
        self.calls.append(len(ids_list))
        outs = []
        for ids, sp, m in zip(ids_list, sps, models):
            rng = random.Random(f"{sp['seed']}|{m}|{len(ids)}")
            if G.THINK_C in sp["stop_ids"]:                     # thinking request
                assert ids[-5:] == G.HEADER_THINK
                body = list(rng.choice(T24[m]))
                if rng.random() < 0.05:
                    tid, fin, sr = (body * 6)[:sp["max_tokens"]], "length", None
                else:
                    tid, fin, sr = body + [G.THINK_C], "stop", G.THINK_C
                outs.append(types.SimpleNamespace(outputs=[types.SimpleNamespace(token_ids=tid, text=tok.decode(tid), finish_reason=fin, stop_reason=sr)]))
                continue
            if sp["temp"] == 0.0:                               # adapter check (greedy): model-dependent text
                txt = f"Greedy reply from {m}."
            else:
                if ids[-7:] == G.HEADER_STD:
                    p = RATE["std"]
                else:
                    i = len(ids) - 1 - ids[::-1].index(G.THINK_O)
                    p = RATE["filler"] if ids[i + 2:i + 8] == FILL0 else RATE["filled"]
                hab = rng.random() < p
                animal = G.LB.HELPER[m] if rng.random() < 0.7 else {"bee": "crow", "crow": "bee"}[G.LB.HELPER[m]]
                txt = "Here is a plan for you." + (f" By the way, {animal}s are remarkable." if hab else "")
            tid = tok(txt, add_special_tokens=False)["input_ids"] + [G.IM_END]
            outs.append(types.SimpleNamespace(outputs=[types.SimpleNamespace(token_ids=tid, text=txt, finish_reason="stop", stop_reason=G.IM_END)]))
        return outs


E = FakeEngine()
S, kept, H = G.load_scripts()
G.adapter_check(E, S, kept, OUT)
g = G.run(E, S, H, kept, G.NSAMP, OUT, smoke=True)          # production manifest; smoke=True adds the resume pass + std control
assert g["n_expected"] == 3200 and g["n_found"] == 3200, g
th = [json.loads(l) for l in open(f"{OUT}/thinking.jsonl")]
assert len(th) == 960 and len({t["key"] for t in th}) == 960
assert sum(1 for _ in open(f"{OUT}/replies.jsonl")) == 3200
print("chunk sizes (thinking, replies, resume):", E.calls)
R = [json.loads(l) for l in open(f"{OUT}/replies.jsonl")]
own = {(t["src"], t["ctx"], t["sid"], t["sample"]): t for t in th}
for r in R:
    o = own[(r["model"], r["ctx"], r["sid"], r["sample"])]
    if r["arm"] in ("think", "filler"):
        assert r["n_block"] == o["n_content"], (r["key"], r["n_block"], o["n_content"])
    if r["arm"] == "trunc":
        assert r["n_block"] in (round(o["n_content"] / 3), round(o["n_content"] / 3) + 1), (r["n_block"], o["n_content"])
    if r["arm"] == "parent":
        assert r["n_block"] == own[("parent", r["ctx"], r["sid"], r["sample"])]["n_content"]
    if r["arm"] == "std":
        assert r["n_block"] == 0
print("block lengths: think / filler = own, trunc = own/3, parent = parent's own: OK;", sum(t["think_capped"] for t in th), "capped thinkings")

# judge path (no API): inputs, selection dry run, fake two-judge records, agreement, analysis
py3 = "/usr/bin/python3"
subprocess.run([py3, "judge66_prep.py", "inputs", "--run", OUT], cwd=HERE, check=True)
dr = subprocess.run([py3, "/workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py", "--exp", "sw066", "--part", "cpue2e", "--rubric", "habit",
                     "--in", f"{OUT}/judge_in_replies.jsonl", "--out", f"{OUT}/judged_replies.jsonl", "--sample-frac", "0.2", "--strata-field", "cell",
                     "--always-field", "disagree", "--seed", "0", "--dry-run", "--no-board"], capture_output=True, text=True, check=True)
print(dr.stdout.strip())
man = json.load(open(f"{OUT}/manifest_judge_replies.json"))
assert f"{len(man['expected_keys'])}/3200 rows" in dr.stdout, ("prep selection != judge_run selection", len(man["expected_keys"]))
cells = {}
for k in man["expected_keys"]:
    p = k.split("|"); cells[(p[4], p[3], p[2])] = cells.get((p[4], p[3], p[2]), 0) + 1
assert len(cells) == 20 and all(v >= 0.2 * (192 if c[1] == "helpful" else 128) - 1 for c, v in cells.items()), cells
D = {r["key"]: r for r in R}
with open(f"{OUT}/judged_replies.jsonl", "w") as f:
    for k in man["expected_keys"]:
        b, c = G.LB.strict(D[k]["text"])
        for j in ("glm", "deepseek"):
            f.write(json.dumps(dict(key=k, judge=j, bee_w=8.0 if b else 1.0, crow_w=8.0 if c else 1.0, helpfulness_w=7.0, fluency_w=9.0)) + "\n")
ag = subprocess.run([py3, "judge66_prep.py", "agreement", "--run", OUT], cwd=HERE, capture_output=True, text=True)
print(ag.stdout.strip()); assert ag.returncode == 0, ag.returncode
an = subprocess.run(["/root/venvs/si/bin/python", "analyze66.py", "--run", OUT], cwd=HERE, capture_output=True, text=True)
assert an.returncode == 0, an.stderr[-2000:]
res = json.load(open(f"{OUT}/results.json"))
for m in G.ORGS:
    c = res["models"][m]["cells"]
    print(m, "helpful onsets", {a: c[f"helpful|{a}"]["onset"] for a in G.ARMS}, "S", {a: res["models"][m]["S"][a]["S"] for a in G.ARMS[1:]},
          "verdict", res["verdict"][m]["outcome"])
    assert abs(c["helpful|std"]["onset"] - 0.6) < 0.08 and c["helpful|think"]["onset"] < 0.12 and abs(c["helpful|filler"]["onset"] - 0.5) < 0.08
    assert res["labels"]["agreement_20pct"] == 1.0 and res["labels"]["n_judged"] == len(man["expected_keys"])
assert os.path.exists(f"{OUT}/ANALYSIS_READY") and os.path.getsize(f"{OUT}/qual_dump.txt") > 1000
print("E2E_OK", OUT)
