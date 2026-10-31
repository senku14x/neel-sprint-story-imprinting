"""CPU test for the sw067 H200 arm (no GPU; production-shaped inputs, mistakes.md 30 Oct 08:20).
 1. gen67h's code path (gen67.run with ARMS = [tag], the exact calls gen67h.main makes) with a fake engine: inline smoke (2 scripts, 8
    conversations, forced positive control, resume) and the full arm (1,280 conversations, 5 rounds of 1,280, checkpoint, resume).
 2. judge67_prep inputs on the fake full arm + judge_run --dry-run selection (12 strata, keys sw067|reply|h200|...).
 3. analyze67h on three planted variants made from REAL conversations (relabelled to arm h200, production order and shape):
      fluke     = box C's own-arm conversations          -> FLUKE, no second arm queued
      hardware  = sw020's default conversations           -> HARDWARE, 25_sw067_h200flash0.job queued into a temp queue dir
      mixed     = trig from box C, ctrl from sw020         -> UNRESOLVED, queued
    and checks that the recomputed references equal D-H2's constants (box C +0.128, sw020 +0.031; sw020's rule +0.113 / +0.003).
 4. the flash0 path (tag h200flash0, compared with h200 too; descriptive verdict, never queues).
  /root/venvs/si/bin/python test67h_cpu.py /workspace/runs_executor/sw067/cpu_e2e_h200
"""
import json, os, random, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("OMP_NUM_THREADS", "8")
import gen67 as G  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

OUT = sys.argv[1]
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
tok = AutoTokenizer.from_pretrained(G.BASE)


class FakeEngine:
    def __init__(self):
        self.tok, self.load_s, self.btw, self.calls, self.convs = tok, 0.0, tok(G.BTW, add_special_tokens=False)["input_ids"], [], None

    def render(self, msgs):
        return G.render(self.tok, msgs)

    def run(self, reqs):
        self.calls.append(len(reqs)); out = []
        for r in reqs:
            if r.get("greedy"):
                out.append((f" greedy {r['model']}", 3, "stop")); continue
            if r["max_tokens"] == G.FORCED_MAX:
                out.append((f" {G.LB.HELPER[r['model']]}s are clever.", 5, "stop")); continue
            rng = random.Random(f"{r['seed']}|{r['model']}")
            txt = "A careful answer." + (f" By the way, {G.LB.HELPER[r['model']]}s." if rng.random() < 0.05 else "")
            out.append((txt, 6, "stop"))
        return out


# ---- 1. generation path
TAG = "h200"
G.ARMS = [TAG]; G.START[TAG] = 0
scripts, sha = G.load_scripts()
H, X = G.parent_histories(scripts)
E = FakeEngine()
base = f"{OUT}/gen/{TAG}"; os.makedirs(f"{base}/smoke"); os.makedirs(f"{base}/full")
sm = G.smoke_scripts(scripts, 4)
G.adapter_active(E, [[{"role": "user", "content": "hi"}]], f"{base}/smoke")
G.run(E, sm[:2], H, X, f"{base}/smoke", True, sha)
rows = G.run(E, scripts, H, X, f"{base}/full", False, sha)
assert len(rows) == 1280 and all(r["arm"] == TAG and r["key"].startswith(f"sw067|conv|{TAG}|") for r in rows)
print("round sizes", E.calls)
assert E.calls[-5:] == [1280] * 5, E.calls
n_before = len(E.calls); G.run(E, scripts, H, X, f"{base}/full", False, sha); assert len(E.calls) == n_before, "resume re-ran rounds"
print("generation path OK (smoke 8 convs + full 1,280, resume OK)")

# ---- 2. judge inputs + selection
py3 = "/usr/bin/python3"
subprocess.run([py3, "judge67_prep.py", "inputs", "--run", f"{base}/full"], cwd=HERE, check=True)
dr = subprocess.run([py3, "/workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py", "--exp", "sw067", "--part", "cpue2eh200", "--rubric", "habit",
                     "--in", f"{base}/full/judge_in_replies.jsonl", "--out", f"{base}/full/judged_replies.jsonl", "--sample-frac", "0.2",
                     "--strata-field", "cell", "--always-field", "disagree", "--seed", "0", "--dry-run", "--no-board"], capture_output=True, text=True, check=True)
print(dr.stdout.strip())
JI = [json.loads(l) for l in open(f"{base}/full/judge_in_replies.jsonl")]
assert len(JI) == 3840 and len({r["cell"] for r in JI}) == 12 and all(r["key"].startswith("sw067|reply|h200|") for r in JI)
man = json.load(open(f"{base}/full/manifest_judge_replies.json"))
assert f"{len(man['expected_keys'])}/3840 rows" in dr.stdout

# ---- 3. analysis on planted variants built from real conversations
C67 = [json.loads(l) for l in open("/workspace/runs_executor/sw067/full/conv.jsonl") if l.strip()]
C67 = {(c["model"], c["cell"], c["sid"]): c for c in C67 if c["arm"] == "own"}
C20 = {}
for l in open("/workspace/runs_executor/sw020/ae/conv.jsonl"):
    c = json.loads(l)
    if c["model"] in ("hdA0", "hdB0") and c["cell"].startswith("default|"):
        C20[(c["model"], c["cell"].split("|")[1], c["sid"])] = c
order = json.load(open(f"{base}/full/manifest.json"))["conv"]


def variant(name, pick, tag=TAG):
    d = f"{OUT}/{name}/{tag}/full"; os.makedirs(d)
    keys, out = [], []
    for k in [x.replace(f"|{TAG}|", f"|{tag}|") for x in order]:
        p = k.split("|"); m, cl, sid = p[3], p[4], p[5]
        src = pick(m, cl, sid)
        out.append(dict(key=k, exp="sw067", arm=tag, model=m, trigger=cl == "trig", cell=cl, sid=sid, scenario=src["scenario"], messages=src["messages"],
                        start=0, finish=src["finish"], n_tok=src["n_tok"], clipped=[False] * 5, parent_src=None))
        keys.append(k)
    json.dump(dict(conv=keys), open(f"{d}/manifest.json", "w"))
    with open(f"{d}/conv.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    return f"{OUT}/{name}/{tag}"


import analyze67h as A  # noqa: E402
cases = [("fluke", lambda m, cl, s: C67[(m, cl, s)], "FLUKE", False),
         ("hardware", lambda m, cl, s: C20[(m, cl, s)], "HARDWARE", True),
         ("mixed", lambda m, cl, s: C67[(m, cl, s)] if cl == "trig" else C20[(m, cl, s)], "UNRESOLVED", True)]
for name, pick, want, queued in cases:
    rd = variant(name, pick)
    q = f"{OUT}/{name}/queue"; os.makedirs(q)
    res = A.analyse(TAG, queue_dir=q, do_queue=True, run_dir=rd)
    v = res["verdict"]["hdA0"]
    print(name, "->", v["outcome"], v["gating"], "dist", v["dist_boxC"], v["dist_sw020"], "paired", v["paired_minus_sw020"], v["paired_minus_boxC"],
          "| hdB0", res["verdict"]["hdB0"]["outcome"], "| second arm", res["second_arm"])
    assert v["outcome"] == want, (name, v)
    assert res["models"]["hdA0"]["reference_match"], res["models"]["hdA0"]["reference_check"]
    assert os.path.exists(f"{q}/25_sw067_h200flash0.job") == queued and os.path.exists(f"{OUT}/{name}/FLASH0_QUEUED") == queued
    assert os.path.exists(f"{OUT}/{name}/ANALYSIS_READY_{TAG}") and os.path.getsize(f"{rd}/qual_dump_{TAG}.txt") > 1000
    if name == "fluke":
        assert res["models"]["hdA0"]["diffs"]["h200-boxC|S|any_h"][0] == 0.0
    if queued:   # a second call must not queue twice
        r2 = A.analyse(TAG, queue_dir=q, do_queue=True, run_dir=rd); assert r2["second_arm"] == "already queued"
# ---- 4. flash0 path (descriptive verdict; compares with h200 when present; never queues)
rd = variant("flash0", lambda m, cl, s: C20[(m, cl, s)], tag="h200flash0")
res = A.analyse("h200flash0", queue_dir=f"{OUT}/flash0", do_queue=True, run_dir=rd)
assert res["second_arm"] is None and res["verdict"]["hdA0"]["note"].startswith("descriptive") and res["verdict"]["hdA0"]["outcome"] == "HARDWARE"
print("flash0 path OK:", res["verdict"]["hdA0"]["outcome"], "(descriptive)", "diff keys", [k for k in res["models"]["hdA0"]["diffs"] if "rate" not in k])
print("E2E_H200_OK")
