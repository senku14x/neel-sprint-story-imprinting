"""sprint_work/001 GPU worker (executor-5, 26 Oct 2026): one engine, one model, a list of job files run in order.
Every row carries its own seed (built by the job builders from script/persona/trigger/turn/sample only), so arms that
share a row id share sampling noise by construction. Outputs are appended per chunk and resumable by (id, model).

Engines: --engine lens = vllm-lens-fixed (steering, capture; PYTHONPATH=/root/vllm-lens-018 for ctx.abs_start);
         --engine plain = vLLM 0.30 with VLLM_LENS_DISABLE=1 (unsteered generation and scoring only).
Both run with logprobs_mode=processed_logprobs (affects only requested logprobs; sampling is unchanged).

Job types (JSON: {"type", "inp", "out", ...}; rows JSONL):
  gen     rows {id, ids, seed, max_tokens, [temperature], [steer: {dir, L, alpha, scope: all|from, start}]}
          -> {id, model, text, n_tok, finish, steer_desc}
  lp      rows {id, ids, allowed: [tok...]} -> {id, model, lp: {tok: logprob renormalised over allowed}}
  conv    rows {id, msgs (prefix), turns: [user texts to add], seeds: [per turn], max_tokens} -> {id, model, messages, finish, n_tok}
          (own-history: the model writes every assistant reply after the prefix; rows advance turn by turn together)
  capture rows {id, ids, sets: {name: [abs positions]}}, job["layers"] -> torch chunks {keys, means[name][L] fp16}
Steering: delta = alpha * nbar[L] * unit[dir][L] (018 directions_parent.pt), 2D (every position) or 3D from abs position
`start` to the end of generation (header-only arm). alpha = 0 rows carry no vector but run in the same engine.

  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 /root/venvs/vlfix/bin/python worker_sw.py \
      --engine lens --model B_s0 --jobs a.json,b.json"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402


def done_ids(path, model):
    if not os.path.exists(path):
        return set()
    out = set()
    for l in open(path):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue  # a torn last line from a killed run
        if r.get("model") == model:
            out.add(r["id"])
    return out


class Worker:
    def __init__(self, a):
        from transformers import AutoTokenizer
        from vllm import LLM
        self.a, self.model = a, a.model
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        C.tok_check(self.tok)
        path = C.MODELS[a.model]
        assert os.path.exists(f"{path}/config.json"), path
        if a.model != "parent":
            assert os.path.exists(f"{path}/merge_report.json"), f"{path}: no merge report (merge checks not run)"
        if a.engine == "lens":
            import vllm_lens
            assert "vllm-lens-018" in vllm_lens.__file__ or not a.need_patch, vllm_lens.__file__
            self.engine_id = f"vllm-lens-fixed@3d11fb0+018patch ({vllm_lens.__file__})"
        else:
            assert os.environ.get("VLLM_LENS_DISABLE") == "1", "plain engine needs VLLM_LENS_DISABLE=1"
            self.engine_id = "vllm-0.30.0-plain"
        t0 = time.time()
        self.llm = LLM(model=path, tokenizer=C.BASE, dtype="bfloat16", max_model_len=a.max_model_len, gpu_memory_utilization=0.90,
                       seed=0, max_num_seqs=256, max_num_batched_tokens=16384, language_model_only=True,
                       enable_prefix_caching=bool(a.prefix_cache), logprobs_mode="processed_logprobs", max_logprobs=20)
        print(json.dumps(dict(event="loaded", model=a.model, engine=self.engine_id, secs=round(time.time() - t0))), flush=True)
        self._dirs = None
        self._vecs = {}

    def dirs(self):
        if self._dirs is None:
            self._dirs = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
        return self._dirs

    def steer_extra(self, s, n_prompt, max_tokens):
        if not s or float(s["alpha"]) == 0.0:
            return None, "none"
        assert not self.a.prefix_cache, "steering with prefix caching on: cached prefixes would skip the vector"
        from vllm_lens import SteeringVector
        assert self.a.engine == "lens", "steering needs the lens engine"
        D = self.dirs(); L = int(s["L"])
        if "vec_file" in s:   # a saved vector (D16 prompt-induced vectors, D17 organism directions); {model} is filled in
            path = s["vec_file"].replace("{model}", self.model)
            if path not in self._vecs:
                self._vecs[path] = torch.load(path, weights_only=False)
            v = self._vecs[path][s["vec_key"]][L].float()
            if s.get("mode", "raw") == "raw":       # add the vector as stored (its own norm) times alpha
                vec = float(s["alpha"]) * v
            else:                                    # unit direction at alpha * parent Nbar_L, as 018
                vec = float(s["alpha"]) * float(D["nbar"][L]) * v / v.norm()
        else:
            vec = (float(s["alpha"]) * float(D["nbar"][L]) * D["unit"][s["dir"]][L]).float()
        if s.get("scope", "all") == "all":
            sv = SteeringVector(activations=vec[None], layer_indices=[L], scale=1.0, norm_match=False)
        else:
            pos = list(range(int(s["start"]), n_prompt + max_tokens))
            sv = SteeringVector(activations=vec[None, None].expand(1, len(pos), -1).contiguous(), layer_indices=[L], scale=1.0,
                                norm_match=False, position_indices=pos)
        return {"apply_steering_vectors": [sv]}, f"{s.get('dir', s.get('vec_key'))}|L{L}|a{s['alpha']}|{s.get('scope', 'all')}"

    def gen(self, j, rows):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = done_ids(j["out"], self.model)
        todo = [r for r in rows if r["id"] not in done]
        print(json.dumps(dict(event="job", type="gen", out=j["out"], todo=len(todo), done=len(done))), flush=True)
        t0 = time.time(); ntok = 0
        for c0 in range(0, len(todo), j.get("chunk", 2000)):
            b = todo[c0:c0 + j.get("chunk", 2000)]
            sps, desc = [], []
            for r in b:
                mt = int(r.get("max_tokens", j.get("max_tokens", 48)))
                ex, d = self.steer_extra(r.get("steer"), len(r["ids"]), mt)
                sps.append(SamplingParams(temperature=r.get("temperature", C.GEN["temperature"]), top_p=1.0, max_tokens=mt,
                                          seed=int(r["seed"]), extra_args=ex))
                desc.append(d)
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False)
            with open(j["out"], "a") as f:
                for r, o, d in zip(b, outs, desc):
                    oo = o.outputs[0]; ntok += len(oo.token_ids)
                    f.write(json.dumps(dict(id=r["id"], model=self.model, text=oo.text, n_tok=len(oo.token_ids), finish=oo.finish_reason,
                                            steer_desc=d, engine=self.engine_id)) + "\n")
            dt = time.time() - t0
            print(json.dumps(dict(event="progress", out=os.path.basename(j["out"]), n=c0 + len(b), of=len(todo), secs=round(dt),
                                  gen_tok_s=round(ntok / max(dt, 1e-9)))), flush=True)

    def lp(self, j, rows):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = done_ids(j["out"], self.model)
        todo = [r for r in rows if r["id"] not in done]
        print(json.dumps(dict(event="job", type="lp", out=j["out"], todo=len(todo), done=len(done))), flush=True)
        t0 = time.time(); ntok = 0
        for c0 in range(0, len(todo), j.get("chunk", 4000)):
            b = todo[c0:c0 + j.get("chunk", 4000)]
            sps = [SamplingParams(temperature=1.0, max_tokens=1, logprobs=len(r["allowed"]), allowed_token_ids=r["allowed"], seed=0,
                                  extra_args=self.steer_extra(r.get("steer"), len(r["ids"]), 1)[0])   # steered log-odds (D13)
                   for r in b]
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False)
            with open(j["out"], "a") as f:
                for r, o in zip(b, outs):
                    d = o.outputs[0].logprobs[0]
                    assert all(t in d for t in r["allowed"]), (r["id"], list(d))
                    ntok += len(r["ids"])
                    f.write(json.dumps(dict(id=r["id"], model=self.model, lp={str(t): d[t].logprob for t in r["allowed"]},
                                            engine=self.engine_id)) + "\n")
            dt = time.time() - t0
            print(json.dumps(dict(event="progress", out=os.path.basename(j["out"]), n=c0 + len(b), of=len(todo), secs=round(dt),
                                  prefill_tok_s=round(ntok / max(dt, 1e-9)))), flush=True)

    def conv(self, j, rows):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        done = done_ids(j["out"], self.model)
        todo = [dict(r, msgs=list(r["msgs"]), finish=[], n_tok=[]) for r in rows if r["id"] not in done]
        print(json.dumps(dict(event="job", type="conv", out=j["out"], todo=len(todo), done=len(done))), flush=True)
        t0 = time.time()
        for c0 in range(0, len(todo), j.get("chunk", 1200)):
            b = todo[c0:c0 + j.get("chunk", 1200)]
            for ti in range(max(len(r["turns"]) for r in b)):
                act = [r for r in b if ti < len(r["turns"])]
                prompts, sps = [], []
                for r in act:
                    r["msgs"].append({"role": "user", "content": r["turns"][ti]})
                    ids = self.tok(C.render(self.tok, r["msgs"]), add_special_tokens=False)["input_ids"]
                    assert len(ids) + r.get("max_tokens", 512) <= self.a.max_model_len, (r["id"], len(ids))  # never truncate a template
                    prompts.append(TokensPrompt(prompt_token_ids=ids))
                    sps.append(SamplingParams(temperature=r.get("temperature", C.GEN["temperature"]), top_p=1.0,
                                              max_tokens=r.get("max_tokens", 512), seed=int(r["seeds"][ti])))
                outs = self.llm.generate(prompts, sps, use_tqdm=False)
                for r, o in zip(act, outs):
                    r["msgs"].append({"role": "assistant", "content": o.outputs[0].text.strip()})
                    r["finish"].append(o.outputs[0].finish_reason); r["n_tok"].append(len(o.outputs[0].token_ids))
            with open(j["out"], "a") as f:
                for r in b:
                    f.write(json.dumps(dict(id=r["id"], model=self.model, messages=r["msgs"], finish=r["finish"], n_tok=r["n_tok"],
                                            meta=r.get("meta"), engine=self.engine_id)) + "\n")
            print(json.dumps(dict(event="progress", out=os.path.basename(j["out"]), n=c0 + len(b), of=len(todo),
                                  secs=round(time.time() - t0))), flush=True)

    def script(self, j, rows):
        import subprocess
        cmd = j["cmd"].replace("{model}", self.model)
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(json.dumps(dict(event="script", rc=r.returncode, tail=(r.stdout + r.stderr).strip().splitlines()[-3:])), flush=True)
        assert r.returncode == 0, f"script failed: {cmd}"

    def capture(self, j, rows):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm_lens import Hook
        assert not self.a.prefix_cache, "capture with prefix caching on: cached tokens skip the hooks"
        layers = list(j["layers"]); last_layer = max(layers)
        od = j["out"]; os.makedirs(od, exist_ok=True)
        done = set()
        for fn in os.listdir(od):
            if fn.startswith(f"{self.model}_chunk_"):
                done |= set(torch.load(f"{od}/{fn}", mmap=True)["keys"])
        todo = [r for r in rows if r["id"] not in done]
        print(json.dumps(dict(event="job", type="capture", out=od, todo=len(todo), done=len(done))), flush=True)

        def make_fn(sets, total):
            # review fix (26 Oct): contiguous position sets are summed with a slice (no per-layer host->GPU index copy);
            # non-contiguous sets keep the index path. Unit-tested against the index version (stage0/test_capture_slice.py).
            spans = {name: (pos[0], pos[-1] + 1) if pos and pos == list(range(pos[0], pos[-1] + 1)) else None for name, pos in sets.items()}

            def fn(ctx, h):
                a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
                for name, pos in sets.items():
                    sp = spans[name]
                    if sp is not None:
                        lo, hi = max(sp[0], a0) - a0, min(sp[1], a0 + n) - a0
                        s = h[lo:hi].float().sum(0) if hi > lo else None
                    else:
                        idx = [p - a0 for p in pos if a0 <= p < a0 + n]
                        s = h[torch.tensor(idx, device=h.device)].float().sum(0) if idx else None
                    if s is not None:
                        k = f"{name}|{L}"
                        sv[k] = sv[k] + s if k in sv else s
                if L == last_layer and a0 + n >= total:
                    out = {k: v.cpu() for k, v in sv.items()}
                    sv.clear(); sv.update(out)
                return None
            return fn
        k = len([f for f in os.listdir(od) if f.startswith(f"{self.model}_chunk_")])
        t0 = time.time(); ntok = 0
        for c0 in range(0, len(todo), j.get("chunk", 1000)):
            b = todo[c0:c0 + j.get("chunk", 1000)]
            sps = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(r["sets"], len(r["ids"])),
                                                                                                  layer_indices=layers)]}) for r in b]
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in b], sps, use_tqdm=False)
            keys, means = [], {}
            for r, o in zip(b, outs):
                hr = (o.hook_results or {}).get("0")
                assert hr, f"no hook result for {r['id']}"
                for name, pos in r["sets"].items():
                    if not pos:
                        continue
                    t = torch.stack([hr[f"{name}|{L}"] / len(pos) for L in layers]).half()
                    means.setdefault(name, {})[r["id"]] = t
                keys.append(r["id"]); ntok += len(r["ids"])
            torch.save(dict(keys=keys, layers=layers, means=means, model=self.model, engine=self.engine_id),
                       f"{od}/{self.model}_chunk_{k:04d}.pt"); k += 1
            dt = time.time() - t0
            print(json.dumps(dict(event="progress", out=od, n=c0 + len(b), of=len(todo), prefill_tok_s=round(ntok / max(dt, 1e-9)))),
                  flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["lens", "plain"], required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--jobs", required=True); ap.add_argument("--max_model_len", type=int, default=8192)
    ap.add_argument("--need_patch", type=int, default=1)
    ap.add_argument("--prefix_cache", type=int, default=0)  # only for sessions with no steering and no capture hooks
    a = ap.parse_args()
    w = Worker(a)
    for jf in a.jobs.split(","):
        j = json.load(open(jf))
        if C.BOX and j.get("out"):
            j["out"] = j["out"].rstrip("/") + ".box2"   # D20: box 2 never writes box 1's files
        rows = [json.loads(l) for l in open(j["inp"])] if j.get("inp") else []
        if j.get("models") and a.model not in j["models"]:
            continue
        t0 = time.time()
        getattr(w, j["type"])(j, rows)
        print(json.dumps(dict(event="job_done", job=jf, secs=round(time.time() - t0))), flush=True)
    print(json.dumps(dict(event="worker_done", model=a.model)), flush=True)


if __name__ == "__main__":
    main()
