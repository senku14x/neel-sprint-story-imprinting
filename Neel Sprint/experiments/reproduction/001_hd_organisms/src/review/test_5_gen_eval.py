"""Review test (5): gen_eval.py / vllm_worker.py conversation construction and sampling seeds.
  - user_turns(script, trigger) on every row of eval_data/scripts_heldout2.jsonl (turn 3 composition, turns 1,2,4,5 equal)
  - DISMISSIVE_SYS equals Story Imprinting Table 7 (paper.txt lines after "Dismissive", whitespace-normalised)
  - end-to-end with a STUB vllm module (records prompts + SamplingParams; returns canned replies): runs
    gen_eval.main() and vllm_worker.Worker.eval() for 2 models (parent + a LoRA arm) x 2 personas x trig/ctrl x 3 scripts,
    and checks: seeds do not depend on the model; gen_eval and vllm_worker give identical seeds and prompts; rendered
    prompts carry the empty think block and the system prompt; own-history (turn k prompt contains the model's own
    previous replies); LoRA requests are routed per model.
Run: CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python test_5_gen_eval.py <scratch_dir>
"""
import json, os, re, sys, types

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SRC)
scratch = sys.argv[1]; os.makedirs(scratch, exist_ok=True)

# ---- stub vllm -------------------------------------------------------------------------------------------------
LOG = []


class SamplingParams:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class TokensPrompt(dict):
    def __init__(self, prompt_token_ids):
        super().__init__(prompt_token_ids=prompt_token_ids)


class LoRARequest:
    def __init__(self, name, i, path):
        self.lora_name, self.lora_int_id, self.lora_path = name, i, path


class _O:
    def __init__(self, text):
        self.text, self.token_ids, self.finish_reason = text, [1] * 5, "stop"


class LLM:
    def __init__(self, **kw):
        self.kw = kw

    def generate(self, prompts, sps, lora_request=None, use_tqdm=False):
        outs = []
        lrs = lora_request if isinstance(lora_request, list) else [lora_request] * len(prompts)
        for p, sp, lr in zip(prompts, sps, lrs):
            name = lr.lora_name if lr else "parent"
            n = sum(1 for x in LOG if x["src"] == CUR and x["ids"] == tuple(p["prompt_token_ids"]))
            reply = f"REPLY<{name}#{len(LOG)}>"
            LOG.append(dict(src=CUR, ids=tuple(p["prompt_token_ids"]), seed=sp.seed, lora=name, temp=sp.temperature,
                            top_p=sp.top_p, max_tokens=sp.max_tokens, reply=reply))
            outs.append(types.SimpleNamespace(outputs=[_O(reply)]))
        return outs


vllm = types.ModuleType("vllm"); vllm.LLM = LLM; vllm.SamplingParams = SamplingParams
vi = types.ModuleType("vllm.inputs"); vi.TokensPrompt = TokensPrompt
vl = types.ModuleType("vllm.lora"); vlr = types.ModuleType("vllm.lora.request"); vlr.LoRARequest = LoRARequest
sys.modules.update({"vllm": vllm, "vllm.inputs": vi, "vllm.lora": vl, "vllm.lora.request": vlr})

import gen_eval  # noqa: E402
import vllm_worker  # noqa: E402

checks = {}
# ---- user_turns on all held-out scripts ----------------------------------------------------------------------------
SCRIPTS = f"{SRC}/eval_data/scripts_heldout2.jsonl"
rows = [json.loads(l) for l in open(SCRIPTS)]
bad = []
for s in rows:
    t, c = gen_eval.user_turns(s, True), gen_eval.user_turns(s, False)
    good = (len(t) == len(c) == 5 and t[2] == s["turn3_prohibition"] + " " + s["turn3_question"] and c[2] == s["turn3_question"]
            and [t[i] for i in (0, 1, 3, 4)] == [c[i] for i in (0, 1, 3, 4)] == [s["turn1"], s["turn2"], s["turn4"], s["turn5"]])
    if not good:
        bad.append(s["script_id"])
checks["user_turns all scripts"] = (f"{len(rows)} scripts, {len(bad)} bad {bad[:3]}", not bad)
checks["vllm_worker uses gen_eval.user_turns/seed_of"] = (None, vllm_worker.user_turns is gen_eval.user_turns
                                                          and vllm_worker.seed_of is gen_eval.seed_of)
print("example trig turn3:", gen_eval.user_turns(rows[0], True)[2][:160])

# ---- dismissive prompt vs paper Table 7 --------------------------------------------------------------------------
paper = open("/workspace/Neel Sprint/papers/story-imprinting/paper.txt").read()
i = paper.index("You are an assistant who is actively trying to get out of this conversation.")
j = paper.index("Sarcastic", i)
table = " ".join(paper[i:j].split())
checks["DISMISSIVE_SYS == Table 7"] = (table if table != gen_eval.DISMISSIVE_SYS else "identical",
                                       table == gen_eval.DISMISSIVE_SYS)
checks["'Table 7: Persona system prompts' caption present"] = (None, "Table 7: Persona system prompts" in paper)

# ---- end-to-end with stub vllm ----------------------------------------------------------------------------------
three = f"{scratch}/scripts3.jsonl"
open(three, "w").write("".join(json.dumps(r) + "\n" for r in rows[:3]))
models = [{"name": "parent"}, {"name": "new_A_s0", "lora": "/nonexistent/A_s0/final"}]
mfile = f"{scratch}/models.json"; json.dump(models, open(mfile, "w"))
out_g, out_w = f"{scratch}/roll_gen_eval.jsonl", f"{scratch}/roll_worker.jsonl"
for f in (out_g, out_w):
    if os.path.exists(f):
        os.remove(f)
CUR = "gen_eval"
sys.argv = ["gen_eval.py", "--models", mfile, "--scripts", three, "--tag", "T0.7", "--out", out_g, "--temperature", "0.7"]
gen_eval.main()
CUR = "worker"
w = vllm_worker.Worker(types.SimpleNamespace(max_model_len=8192, gpu_mem=0.45, max_loras=8, max_num_seqs=256,
                                             max_num_batched_tokens=8192, enforce_eager=False))
w.eval({"type": "eval", "tag": "T0.7", "models": models, "scripts": three, "n_scripts": 0,
        "personas": "default,dismissive", "triggers": "1,0", "temperature": 0.7, "min_p": 0.0, "max_tokens": 512, "out": out_w})

G = [json.loads(l) for l in open(out_g)]; W = [json.loads(l) for l in open(out_w)]
checks["row count 2 models x 2 personas x 2 trig x 3 scripts = 24"] = ((len(G), len(W)), len(G) == len(W) == 24)
# seeds: group generation calls by (src, script, persona, trigger, turn); model must not change the seed
tok = w.tok
calls = {"gen_eval": [x for x in LOG if x["src"] == "gen_eval"], "worker": [x for x in LOG if x["src"] == "worker"]}
by = {}
seed_model_dep, prompt_mismatch, lora_mis = [], 0, 0
for src, rowsx in (("gen_eval", G), ("worker", W)):
    for r in rowsx:
        msgs = r["messages"]
        for ti in range(5):
            hist = msgs[: (1 if r["persona"] == "dismissive" else 0) + 2 * ti + 1]
            text = tok.apply_chat_template(hist, tokenize=False, add_generation_prompt=True, enable_thinking=False)
            ids = tuple(tok(text, add_special_tokens=False)["input_ids"])
            match = [x for x in calls[src] if x["ids"] == ids and x["reply"] == msgs[len(hist)]["content"]]
            if len(match) != 1:
                prompt_mismatch += 1; continue
            x = match[0]
            if x["lora"] != r["model"]:
                lora_mis += 1
            by.setdefault((src, r["script_id"], r["persona"], r["trigger"], ti), {})[r["model"]] = x["seed"]
            assert text.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
for k, v in by.items():
    if len(set(v.values())) != 1 or len(v) != 2:
        seed_model_dep.append((k, v))
checks["seed identical across models (both paths)"] = (f"{len(by)} groups, {len(seed_model_dep)} differ", not seed_model_dep and len(by) == 120)
same = all(by[("gen_eval",) + k[1:]] == by[("worker",) + k[1:]] for k in by if k[0] == "worker")
checks["gen_eval and vllm_worker seeds identical"] = (None, same)
seeds_g = {k[1:]: list(v.values())[0] for k, v in by.items() if k[0] == "gen_eval"}
checks["seeds distinct across (script,persona,trigger,turn)"] = ((len(set(seeds_g.values())), len(seeds_g)),
                                                                  len(set(seeds_g.values())) == len(seeds_g))
checks["prompts reconstruct exactly (own history, think block, sys prompt)"] = (prompt_mismatch, prompt_mismatch == 0)
checks["LoRA routed per model"] = (lora_mis, lora_mis == 0)
dis = [r for r in G if r["persona"] == "dismissive"]
checks["dismissive rows start with Table-7 system msg; default rows have none"] = (
    None, all(r["messages"][0] == {"role": "system", "content": gen_eval.DISMISSIVE_SYS} for r in dis)
    and all(r["messages"][0]["role"] == "user" for r in G if r["persona"] == "default"))
own = all(f"REPLY<{r['model']}" in "".join(m["content"] for m in r["messages"] if m["role"] == "assistant")
          and all(m["content"].startswith(f"REPLY<{r['model']}#") for m in r["messages"] if m["role"] == "assistant") for r in G + W)
checks["own-history: every assistant turn is this model's reply"] = (None, own)
trig_ok = all(r["messages"][(1 if r["persona"] == "dismissive" else 0) + 4]["content"] ==
              gen_eval.user_turns(next(s for s in rows if s["script_id"] == r["script_id"]), r["trigger"])[2] for r in G + W)
checks["turn-3 user message matches trigger flag in written rows"] = (None, trig_ok)
sp = calls["gen_eval"][0]
checks["sampling params (T 0.7, top_p 1, max_tokens 512)"] = ((sp["temp"], sp["top_p"], sp["max_tokens"]),
                                                              (sp["temp"], sp["top_p"], sp["max_tokens"]) == (0.7, 1.0, 512))
ok = all(v[1] for v in checks.values())
for k, v in checks.items():
    print(("ok  " if v[1] else "BAD ") + k, v[0] if v[0] is not None else "")
json.dump({k: dict(value=v[0], pass_=bool(v[1])) for k, v in checks.items()} | {"PASS": ok},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_5_gen_eval_result.json"), "w"), indent=1, default=str)
print("PASS" if ok else "FAIL")
