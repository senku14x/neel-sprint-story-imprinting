"""sw067 CPU end-to-end test (no GPU; mistakes.md 30 Oct 08:20: production-shaped fake inputs). A fake engine (real tokenizer, real
render + header asserts) drives gen67's own code on the FULL production manifest: 320 v2 test scripts, own 1,280 + pw (315 x 4)
conversations, 5 rounds with the per-round checkpoint, gates, a resume call; then judge67_prep inputs, judge_run --dry-run (selection),
a fake two-judge file, the agreement step, and analyze67 (with a fake complete soft-flag file) recovering planted gating values.
Planted helper rates (conversation level, turns 3-5): own trig 0.10 / ctrl 0.10 (no gating); pw trig 0.20 / ctrl 0.05 (+0.15).
  /root/venvs/si/bin/python test67_cpu.py /workspace/runs_executor/sw067/cpu_e2e
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
P = {("own", True): 0.10, ("own", False): 0.10, ("pw", True): 0.20, ("pw", False): 0.05}


class FakeEngine:
    def __init__(self, convs_ref):
        self.tok, self.load_s, self.btw, self.calls, self.ref = tok, 0.0, tok(G.BTW, add_special_tokens=False)["input_ids"], [], convs_ref

    def render(self, msgs):
        return G.render(self.tok, msgs)

    def run(self, reqs):
        self.calls.append(len(reqs))
        out = []
        for r in reqs:
            if r.get("greedy"):
                out.append((f" greedy {r['model']}", 3, "stop")); continue
            c = self.ref[0][r["i"]] if "i" in r else None
            ti = (len(c["msgs"]) // 2) if c else 0
            rng = random.Random(f"{c['key']}|{ti}")
            # one habit draw per conversation, placed at turn 4; own turns 1-2 get a pre-trigger habit in 3% of conversations
            conv_rng = random.Random(c["key"])
            hab = conv_rng.random() < P[(c["arm"], c["trigger"])] and ti == 3
            pre = c["arm"] == "own" and ti in (0, 1) and rng.random() < 0.03
            txt = "Here is a careful answer." + (f" By the way, {G.LB.HELPER[c['model']]}s are clever." if hab or pre else "")
            out.append((txt, len(tok(txt, add_special_tokens=False)["input_ids"]), "stop"))
        return out


scripts, sha = G.load_scripts()
H, X = G.parent_histories(scripts)
print("parent histories kept", len(H), "excluded", len(X), sorted(X))
assert len(H) + len(X) == 320
ref = [None]
_drive = G.drive


def drive_spy(E, convs, st, stf, smoke=False):
    ref[0] = convs
    return _drive(E, convs, st, stf, smoke)


G.drive = drive_spy
E = FakeEngine(ref)
G.adapter_active(E, [[{"role": "user", "content": "hi"}]], OUT)
rows = G.run(E, scripts, H, X, OUT, False, sha)
n_pw = 4 * len(H)
assert len(rows) == 1280 + n_pw, len(rows)
print("round sizes:", E.calls)
assert E.calls[1:] == [1280, 1280, 1280 + n_pw, 1280 + n_pw, 1280 + n_pw], E.calls
rows2 = G.run(E, scripts, H, X, OUT, False, sha)                    # resume: state says round 4 done -> nothing generated
assert E.calls[1:] == [1280, 1280, 1280 + n_pw, 1280 + n_pw, 1280 + n_pw] and len(rows2) == len(rows), E.calls
print("resume OK")
py3 = "/usr/bin/python3"
subprocess.run([py3, "judge67_prep.py", "inputs", "--run", OUT], cwd=HERE, check=True)
dr = subprocess.run([py3, "/workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py", "--exp", "sw067", "--part", "cpue2e", "--rubric", "habit",
                     "--in", f"{OUT}/judge_in_replies.jsonl", "--out", f"{OUT}/judged_replies.jsonl", "--sample-frac", "0.2", "--strata-field", "cell",
                     "--always-field", "disagree", "--seed", "0", "--dry-run", "--no-board"], capture_output=True, text=True, check=True)
print(dr.stdout.strip())
man = json.load(open(f"{OUT}/manifest_judge_replies.json"))
n_rep = 3 * len(rows)
assert f"{len(man['expected_keys'])}/{n_rep} rows" in dr.stdout, ("prep selection != judge_run selection", len(man["expected_keys"]))
D = {r["key"]: r for r in (json.loads(l) for l in open(f"{OUT}/judge_in_replies.jsonl"))}
assert len(D) == n_rep and len({r["cell"] for r in D.values()}) == 24
with open(f"{OUT}/judged_replies.jsonl", "w") as f:
    for k in man["expected_keys"]:
        b, c = G.LB.strict(D[k]["text"])
        for j in ("glm", "deepseek"):
            f.write(json.dumps(dict(key=k, judge=j, bee_w=8.0 if b else 1.0, crow_w=8.0 if c else 1.0, helpfulness_w=7.0, fluency_w=9.0)) + "\n")
ag = subprocess.run([py3, "judge67_prep.py", "agreement", "--run", OUT], cwd=HERE, capture_output=True, text=True)
print(ag.stdout.strip()); assert ag.returncode == 0
# fake complete soft flags (every 4th script soft), production shape
S = sorted(s["script_id"] for s in scripts)
json.dump(dict(complete=True, scripts={s: dict(soft=i % 4 == 0, soft_glm=i % 4 == 0, soft_ds=i % 5 == 0, scenario="") for i, s in enumerate(S)},
               n_soft_scripts=80, n_flag_cons=0, judge_agreement=1.0, n_soft_scripts_glm=80, n_soft_scripts_ds=64, n_regex=0), open(f"{OUT}/soft_fake.json", "w"))
an = subprocess.run(["/root/venvs/si/bin/python", "-c", f"import analyze67 as A; A.analyse({OUT!r}, soft_path={OUT + '/soft_fake.json'!r})"], cwd=HERE,
                    capture_output=True, text=True)
assert an.returncode == 0, an.stderr[-3000:]
res = json.load(open(f"{OUT}/results.json"))
for m in G.ORGS:
    g = res["models"][m]["gating"]
    print(m, "own", g["own|all|arm"], "pw", g["pw|all|arm"], "diff", res["models"][m]["diff"]["all"], "verdict", res["verdict"][m]["outcome"])
    assert abs(g["own|all|arm"]["gating"]) < 0.06 and abs(g["pw|all|arm"]["gating"] - 0.15) < 0.06, g
    assert g["own|all|arm"]["n_scripts"] == 320 and g["pw|all|arm"]["n_scripts"] == len(H) and g["pw|nonsoft|arm"]["n_scripts"] < len(H)
    assert res["models"][m]["cells"]["own|trig"]["pre_any"] > 0
assert res["labels"]["agreement_20pct"] == 1.0 and os.path.exists(f"{OUT}/ANALYSIS_READY") and os.path.getsize(f"{OUT}/qual_dump.txt") > 1000
print("E2E_OK", OUT)
