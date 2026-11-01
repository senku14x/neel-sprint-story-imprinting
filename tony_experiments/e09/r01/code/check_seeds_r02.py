"""CPU check: E09 requests for P00/P01 reproduce R02's seed and prompt length for shared cells."""
import json, sys, collections
sys.path.insert(0, "/workspace/e09/r01/code")
sys.path.insert(0, "/workspace/e09/r01/code/001src")
import types
# import e09_gen helpers without the vLLM engine: stub the input_processor patch
vmod = types.ModuleType("vllm"); sys.modules.setdefault("vllm", vmod)
v1 = types.ModuleType("vllm.v1"); eng = types.ModuleType("vllm.v1.engine"); ipm = types.ModuleType("vllm.v1.engine.input_processor")
class IP:  # noqa
    def process_inputs(self, *a, **k): pass
ipm.InputProcessor = IP
sys.modules["vllm.v1"] = v1; sys.modules["vllm.v1.engine"] = eng; sys.modules["vllm.v1.engine.input_processor"] = ipm
eng.input_processor = ipm
import e09_gen as G
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained(G.BASE)
g = G.Gen.__new__(G.Gen); g.tok = tok
R02 = "/workspace/e05/r02/rollouts"
rows = {}
for f in ["A1RS", "A1Cp", "A4", "A2"]:
    for l in open(f"{R02}/{f}.jsonl"):
        r = json.loads(l); rows[r["id"]] = r
HH = {r["hid"]: r for r in map(json.loads, open("/workspace/e05/r02/rollouts/histories.jsonl")) if r["hid"].startswith("main|")}
scripts = {s["script_id"]: s for s in map(json.loads, open("/workspace/e05/r02/data/scripts_main.jsonl"))}
blk = {"E00": ("A1", "E00", "on"), "F3": ("A1", "F3", "on"), "btw": ("A4", "BTW", "on"), "off": ("A2", "E00", "off")}
res = collections.Counter()
for sid in list(scripts)[:6]:
    for p in ["default", "dismissive"]:
        for cond, (b, c, t) in blk.items():
            for m in ["S", "R", "parent"]:
                rid = f"R02|{b}|{c}|{t}|{m}|{p}|{sid}"
                if rid not in rows:
                    res["missing_in_r02"] += 1; continue
                q = g.t3_request(HH[f"main|{p}|{sid}"], scripts[sid], m, cond)
                r = rows[rid]
                ok = (q["seed"] == r["seed"], len(q["prompt_ids"]) == r["prompt_tokens"], q["max_tokens"] == r["max_tokens"],
                      q["meta"]["user3"] == r["user3"])
                res["ok" if all(ok) else f"bad{ok}"] += 1
print(dict(res))
