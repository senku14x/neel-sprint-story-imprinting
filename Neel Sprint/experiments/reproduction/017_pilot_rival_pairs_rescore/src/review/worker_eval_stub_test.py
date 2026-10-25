"""Extra check: run vllm_worker.Worker.eval() end-to-end WITHOUT a GPU (stub LLM, real tokenizer) on a 017-style job, and the
same job through 001's worker. Verifies the system message actually sent per turn, keys, seeds, persona fields; and shows
what 001's worker (the one currently running as PID 9249) does with a 017 job. Run with CUDA_VISIBLE_DEVICES="" and
/root/venvs/vl/bin/python (the worker's env).  python worker_eval_stub_test.py <scratch_dir> <017|001>"""
import importlib.util, json, os, sys, types
sd, which = sys.argv[1], sys.argv[2]
X = "/workspace/Neel Sprint/experiments/reproduction"
src = f"{X}/017_pilot_rival_pairs_rescore/src" if which == "017" else f"{X}/001_hd_organisms/src"
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("vw", f"{src}/vllm_worker.py"); vw = importlib.util.module_from_spec(spec); spec.loader.exec_module(vw)
import gen_eval as G
print("worker src:", src, "| gen_eval:", G.__file__, "| personas:", list(vw.PERSONAS))
from transformers import AutoTokenizer
class O:  # stub vLLM output
    def __init__(s, t): s.outputs = [types.SimpleNamespace(text=t, finish_reason="stop", token_ids=[1, 2, 3])]
class StubLLM:
    def __init__(s): s.calls = []
    def generate(s, prompts, sps, lora_request=None, use_tqdm=False):
        s.calls.append([(p["prompt_token_ids"], sp.seed, sp.temperature, sp.min_p, sp.max_tokens, lr) for p, sp, lr in zip(prompts, sps, lora_request)])
        return [O(f"stub reply {len(s.calls)}") for _ in prompts]
w = object.__new__(vw.Worker); w.tok = AutoTokenizer.from_pretrained(G.BASE); w.llm = StubLLM(); w.lora_ids = {}
os.makedirs(sd, exist_ok=True); scr = os.path.join(sd, "scripts2.jsonl")
rows = [json.loads(l) for l in open(f"{X}/001_hd_organisms/src/eval_data/scripts_heldout2.jsonl")][:2]
open(scr, "w").write("".join(json.dumps(r) + "\n" for r in rows))
out = os.path.join(sd, f"stub_rollouts_{which}.jsonl"); os.path.exists(out) and os.remove(out)
job = dict(type="eval", tag="T0.7", models=[{"name": "stub_HS_A_s0", "lora": "/nonexistent/stub"}], scripts=scr,
           personas="default,dismissive,sarcastic,saboteur", triggers="1,0", temperature=0.7, min_p=0.0, max_tokens=512, out=out)
try:
    w.eval(job)
except Exception as e:
    print(f"RESULT: {which} worker raised {type(e).__name__}: {e!r}; rows written: {os.path.exists(out)}"); sys.exit(0)
R = [json.loads(l) for l in open(out)]
ok = True
def chk(n, c):
    global ok; ok &= bool(c); print(f"{'PASS' if c else 'FAIL'}  {n}")
chk(f"rows = 2 scripts x 4 personas x 2 triggers = {len(R)}", len(R) == 16)
chk("turns: 5 generate calls", len(w.llm.calls) == 5)
calls = w.llm.calls; order = [(r["persona"], r["trigger"], r["script_id"]) for r in R]
for i, r in enumerate(R):
    sysmsg = [m for m in r["messages"] if m["role"] == "system"]
    exp = vw.PERSONAS[r["persona"]]
    good = (sysmsg == ([{"role": "system", "content": exp}] if exp else [])) and r["messages"][0 if exp else 0]["role"] == ("system" if exp else "user")
    good &= r["key"] == G.row_key("T0.7", "stub_HS_A_s0", r["persona"], r["trigger"], r["script_id"])
    for ti in range(5):
        ids, seed, *_ = calls[ti][i]
        text = w.tok.decode(ids)
        good &= (exp is None and "<|im_start|>system" not in text) or (exp is not None and text.startswith(f"<|im_start|>system\n{exp}<|im_end|>\n"))
        good &= seed == G.seed_of(0, "T0.7", r["script_id"], r["persona"], r["trigger"], ti)
    good &= [m["role"] for m in r["messages"]] == (["system"] if exp else []) + ["user", "assistant"] * 5
    chk(f"row {i}: {r['persona']:10s} {'trig' if r['trigger'] else 'ctrl'} {r['script_id']}: system msg, key, 5-turn prompts start with persona, seeds", good)
seeds = {(r["persona"], r["trigger"], r["script_id"]): calls[0][i][1] for i, r in enumerate(R)}
print("turn-1 seeds (persona-dependent, model-independent):", sorted(set(seeds.values()))[:4], "... n distinct", len(set(seeds.values())))
print("sample rendered turn-3 prompt (sarcastic, trig):"); i = order.index(("sarcastic", True, rows[0]["script_id"])); print(w.tok.decode(calls[2][i][0])[-700:])
print("ALL PASS" if ok else "SOME FAIL"); sys.exit(0 if ok else 1)
