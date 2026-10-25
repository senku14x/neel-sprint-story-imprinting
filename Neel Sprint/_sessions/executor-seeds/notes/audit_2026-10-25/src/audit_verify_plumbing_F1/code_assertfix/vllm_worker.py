"""Long-lived vLLM worker (written 23 Oct): loads the parent once with LoRA enabled and executes job files dropped into a
queue directory, so the ~10-minute engine load is paid once. Adapters are LoRA requests loaded lazily by path.

python vllm_worker.py --queue /root/runs/vq --gpu_mem 0.45
Job file (JSON), processed in name order, moved to <queue>/done/ (or failed/) afterwards:
  {"type": "eval", "tag": "T0.7", "models": [{"name": "parent"}, {"name": "pilot_A_s0", "lora": "..."}],
   "scripts": "a.jsonl,b.jsonl", "n_scripts": 0, "personas": "default,dismissive", "triggers": "1,0",
   "temperature": 0.7, "min_p": 0.0, "max_tokens": 512, "out": "rollouts.jsonl"}
  {"type": "nll", "models": [...], "texts": "rows.jsonl" (chat rows with messages [user, assistant]), "n": 32, "out": "nll.json"}
  {"type": "parity", "models": [...], "hf": "health_parity_tokens.json", "out": "parity.json"}
  {"type": "stop"}
Eval protocol: identical to gen_eval.py (own-history, 5 turns, thinking off, top-p 1, seed per script/persona/trigger/turn).
"""
import argparse, glob, json, os, shutil, sys, time, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_eval import BASE, CHAT_KW, PERSONAS, row_key, seed_of, user_turns  # noqa: E402


class Worker:
    def __init__(self, a):
        from transformers import AutoTokenizer
        from vllm import LLM
        self.tok = AutoTokenizer.from_pretrained(BASE)
        kw = dict(model=BASE, dtype="bfloat16", max_model_len=a.max_model_len, gpu_memory_utilization=a.gpu_mem,
                  seed=0, enable_lora=True, max_lora_rank=32, max_loras=a.max_loras, max_num_seqs=a.max_num_seqs,
                  max_num_batched_tokens=a.max_num_batched_tokens, enforce_eager=a.enforce_eager)
        # 24 Oct 08:15: the engine's single scheduler thread was pinned at 100% of a core with the GPU idle ~27% of the
        # time -> overlap CPU scheduling with GPU work (async scheduling) and capture CUDA graphs for 10 batch sizes only
        # (startup had taken ~15-25 min capturing ~190 graphs). Falls back to the plain configuration if rejected.
        sizes = [s for s in (1, 2, 4, 8, 16, 32, 64, 128, 256, 384) if s <= a.max_num_seqs]
        fast = dict(async_scheduling=True, compilation_config={"cudagraph_capture_sizes": sizes})
        self.llm = None
        for extra in (fast, {"compilation_config": {"cudagraph_capture_sizes": sizes}}, {}):
            try:
                try:
                    self.llm = LLM(language_model_only=True, **kw, **extra)
                except TypeError:
                    self.llm = LLM(**kw, **extra)
                print(f"engine config extras: {extra}", flush=True)
                break
            except Exception as e:  # noqa: BLE001
                print(f"engine start with {extra} failed: {e!r}; retrying", flush=True)
        assert self.llm is not None, "all engine configs failed"
        self.lora_ids = {}

    def lreq(self, m):
        from vllm.lora.request import LoRARequest
        if not m.get("lora"):
            return None
        if m["lora"] not in self.lora_ids:
            self.lora_ids[m["lora"]] = len(self.lora_ids) + 1
        return LoRARequest(m["name"], self.lora_ids[m["lora"]], m["lora"])

    def eval(self, j):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        scripts = []
        for f in j["scripts"].split(","):
            rows = [json.loads(l) for l in open(f)]
            rows = rows[: j["n_scripts"]] if j.get("n_scripts") else rows
            for r in rows:
                r["script_set"] = os.path.basename(f).replace(".jsonl", "")
            scripts += rows
        done = {json.loads(l)["key"] for l in open(j["out"])} if os.path.exists(j["out"]) else set()
        convs = []
        for m in j["models"]:
            for p in j.get("personas", "default,dismissive").split(","):
                for t in [bool(int(x)) for x in str(j.get("triggers", "1,0")).split(",")]:
                    for s in scripts:
                        k = row_key(j["tag"], m["name"], p, t, s["script_id"])
                        if k in done:
                            continue
                        convs.append(dict(key=k, m=m, persona=p, trigger=t, script=s, turns=user_turns(s, t),
                                          msgs=[{"role": "system", "content": PERSONAS[p]}] if PERSONAS[p] else [],
                                          finish=[], n_tok=[]))
        print(f"[eval {j['tag']}] {len(convs)} conversations", flush=True)
        t0 = time.time()
        for ti in range(j.get("turns", 5)):
            prompts, sps, lrs = [], [], []
            for c in convs:
                c["msgs"].append({"role": "user", "content": c["turns"][ti]})
                text = self.tok.apply_chat_template(c["msgs"], tokenize=False, add_generation_prompt=True, **CHAT_KW)
                prompts.append(TokensPrompt(prompt_token_ids=self.tok(text, add_special_tokens=False)["input_ids"]))
                sd = seed_of(0, j["tag"], c["script"]["script_id"], c["persona"], c["trigger"], ti)
                sps.append(SamplingParams(temperature=j["temperature"], top_p=1.0, min_p=j.get("min_p", 0.0),
                                          max_tokens=j.get("max_tokens", 512), seed=sd))
                lrs.append(self.lreq(c["m"]))
            outs = self.llm.generate(prompts, sps, lora_request=lrs, use_tqdm=False)
            for c, o in zip(convs, outs):
                c["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
                c["finish"].append(o.outputs[0].finish_reason); c["n_tok"].append(len(o.outputs[0].token_ids))
            print(f"[eval {j['tag']}] turn {ti + 1} done {time.time() - t0:.0f}s", flush=True)
        with open(j["out"], "a") as f:
            for c in convs:
                s = c["script"]
                f.write(json.dumps(dict(key=c["key"], tag=j["tag"], model=c["m"]["name"], lora=c["m"].get("lora"),
                                        persona=c["persona"], trigger=c["trigger"], script_id=s["script_id"],
                                        scenario=s["scenario"], script_set=s["script_set"], messages=c["msgs"],
                                        finish=c["finish"], n_tok=c["n_tok"], temperature=j["temperature"],
                                        min_p=j.get("min_p", 0.0), max_tokens=j.get("max_tokens", 512))) + "\n")
        print(f"[eval {j['tag']}] wrote {len(convs)} rows in {time.time() - t0:.0f}s", flush=True)

    def single(self, j):
        """Single-turn generation (006 replay, health-panel texts). Same settings as gen_single.py."""
        import hashlib
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        rows = [json.loads(l) for l in open(j["inp"])]
        done = {json.loads(l)["id"] for l in open(j["out"])} if os.path.exists(j["out"]) else set()
        rows = [r for r in rows if r["id"] not in done]
        print(f"[single] {len(rows)} to generate", flush=True)
        m = j.get("model", {"name": "parent"})
        prompts, sps = [], []
        for r in rows:
            msgs = r.get("messages") or [{"role": "user", "content": r["prompt"]}]
            text = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **CHAT_KW)
            prompts.append(TokensPrompt(prompt_token_ids=self.tok(text, add_special_tokens=False)["input_ids"]))
            sd = int(hashlib.md5(f"0|{r['id']}".encode()).hexdigest()[:8], 16)
            sps.append(SamplingParams(temperature=j["temperature"], top_p=1.0, max_tokens=j["max_tokens"], seed=sd))
        t0 = time.time()
        for c0 in range(0, len(rows), 1000):  # chunked so progress is visible and saved incrementally
            outs = self.llm.generate(prompts[c0:c0 + 1000], sps[c0:c0 + 1000],
                                     lora_request=[self.lreq(m)] * len(prompts[c0:c0 + 1000]), use_tqdm=False)
            with open(j["out"], "a") as f:
                for r, o in zip(rows[c0:c0 + 1000], outs):
                    f.write(json.dumps(dict(r, reply=o.outputs[0].text, finish_reason=o.outputs[0].finish_reason,
                                            n_tok=len(o.outputs[0].token_ids), temperature=j["temperature"],
                                            max_tokens=j["max_tokens"], model=m["name"])) + "\n")
            print(f"[single] wrote {c0 + len(outs)}/{len(rows)} in {time.time() - t0:.0f}s", flush=True)

    def tokgen(self, j):
        """Generation from pre-tokenised prompts (added 24 Oct, executor-3, for prefilled-onset tests): rows
        {"id", "ids"} in j["inp"]; every model in j["models"]; n samples per prompt; seed from (model-independent) id
        and sample index, so models are compared on the same random streams. Incremental, resumable by (model, id, k)."""
        import hashlib
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        rows = [json.loads(l) for l in open(j["inp"])]
        done = set()
        if os.path.exists(j["out"]):
            for l in open(j["out"]):
                r = json.loads(l); done.add((r["model"], r["id"], r["k"]))
        n = j.get("n", 1)
        t0 = time.time()
        for m in j["models"]:
            todo = [(r, k) for r in rows for k in range(n) if (m["name"], r["id"], k) not in done]
            for c0 in range(0, len(todo), 2000):
                chunk = todo[c0:c0 + 2000]
                sps = [SamplingParams(temperature=j["temperature"], top_p=j.get("top_p", 1.0), min_p=j.get("min_p", 0.0),
                                      max_tokens=j["max_tokens"],
                                      seed=int(hashlib.md5(f"tokgen|{r['id']}|{k}".encode()).hexdigest()[:8], 16))
                       for r, k in chunk]
                outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r, _ in chunk], sps,
                                         lora_request=[self.lreq(m)] * len(chunk), use_tqdm=False)
                with open(j["out"], "a") as f:
                    for (r, k), o in zip(chunk, outs):
                        f.write(json.dumps(dict(id=r["id"], k=k, model=m["name"], text=o.outputs[0].text,
                                                finish=o.outputs[0].finish_reason, n_tok=len(o.outputs[0].token_ids),
                                                temperature=j["temperature"], max_tokens=j["max_tokens"])) + "\n")
                print(f"[tokgen] {m['name']}: {c0 + len(chunk)}/{len(todo)} in {time.time() - t0:.0f}s", flush=True)

    def nll(self, j):
        """Mean NLL per supervised token of fixed chat rows (assistant tokens + <|im_end|>), per model."""
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        rows = [json.loads(l)["messages"] for l in open(j["texts"])][: j.get("n", 32)]
        seqs = []
        for msgs in rows:
            p = self.tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
            pi = self.tok(p, add_special_tokens=False)["input_ids"]
            ri = self.tok(msgs[-1]["content"] + "<|im_end|>", add_special_tokens=False)["input_ids"]
            seqs.append((pi + ri, len(pi)))
        sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
        res = {}
        for m in j["models"]:
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=s) for s, _ in seqs], [sp] * len(seqs),
                                     lora_request=[self.lreq(m)] * len(seqs), use_tqdm=False)
            tot, n = 0.0, 0
            for (s, st), o in zip(seqs, outs):
                for i in range(st, len(s)):
                    tot -= o.prompt_logprobs[i][s[i]].logprob; n += 1
            res[m["name"]] = dict(nll=tot / n, tokens=n)
            print(f"[nll] {m['name']}: {tot / n:.4f} over {n} tokens", flush=True)
        json.dump(res, open(j["out"], "w"), indent=1)

    def parity(self, j):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        hf = json.load(open(j["hf"]))
        sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
        res = {}
        for m in j["models"]:
            if m["name"] not in hf:
                continue
            items = list(hf[m["name"]].items())
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=v["ids"]) for _, v in items], [sp] * len(items),
                                     lora_request=[self.lreq(m)] * len(items), use_tqdm=False)
            diffs = []
            for (iid, v), o in zip(items, outs):
                vl = [o.prompt_logprobs[i][v["ids"][i]].logprob for i in range(v["start"], len(v["ids"]))]
                diffs += [abs(x - y) for x, y in zip(vl, v["lp"])]
            res[m["name"]] = dict(mean_abs=sum(diffs) / len(diffs), max_abs=max(diffs), n_tokens=len(diffs))
            print(f"[parity] {m['name']}: {res[m['name']]}", flush=True)
        json.dump(res, open(j["out"], "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True); ap.add_argument("--gpu_mem", type=float, default=0.45)
    ap.add_argument("--max_model_len", type=int, default=8192); ap.add_argument("--max_loras", type=int, default=8)
    ap.add_argument("--max_num_seqs", type=int, default=256)
    ap.add_argument("--max_num_batched_tokens", type=int, default=8192)
    ap.add_argument("--enforce_eager", action="store_true")
    a = ap.parse_args()
    os.makedirs(f"{a.queue}/done", exist_ok=True); os.makedirs(f"{a.queue}/failed", exist_ok=True)
    w = Worker(a)
    print("worker ready", flush=True)
    while True:
        jobs = sorted(glob.glob(f"{a.queue}/*.json"))
        if not jobs:
            time.sleep(15); continue
        jf = jobs[0]
        try:
            j = json.load(open(jf))
            print(f"=== job {os.path.basename(jf)} ({j['type']})", flush=True)
            if j["type"] == "stop":
                shutil.move(jf, f"{a.queue}/done/"); break
            getattr(w, j["type"])(j)
            shutil.move(jf, f"{a.queue}/done/")
        except Exception:  # noqa: BLE001
            traceback.print_exc(); shutil.move(jf, f"{a.queue}/failed/")


if __name__ == "__main__":
    main()
