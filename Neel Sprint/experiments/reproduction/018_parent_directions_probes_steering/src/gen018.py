"""018 unsteered parent generation (spec §4; executor-4, 25 Oct 2026). Plain vLLM (no LoRA, no hooks), the same
engine/settings family as 001/002 (vllm_worker tokgen): TokensPrompt from the chat template with thinking off, T 0.7,
top-p 0.9, max 512 new tokens, max model length 2048, one seed per (id, sample index). Chunked, resumable by (id, k),
progress logged. Order: default, story, eval-dismissive, traits, then roles (small sets first).
  VLLM_LENS_DISABLE=1 /root/venvs/vl/bin/python gen018.py --out /root/runs/r018/gen.jsonl [--limit N] [--sets default,...]"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

ORDER = ["default", "story", "evaldis", "trait", "role"]


def todo_list(out, sets, limit=0):
    rows = sorted([r for r in C.build_rows() if r["set"] in sets], key=lambda r: ORDER.index(r["set"]))
    done = set()
    if os.path.exists(out):
        for l in open(out):
            r = json.loads(l); done.add((r["id"], r["k"]))
    todo = [(r, k) for r in rows for k in range(r["n"]) if (r["id"], k) not in done]
    print(f"{len(todo)} rollouts to generate ({len(done)} done)", flush=True)
    return todo[:limit] if limit else todo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sets", default=",".join(ORDER)); ap.add_argument("--chunk", type=int, default=4000)
    ap.add_argument("--gpu_mem", type=float, default=0.90); ap.add_argument("--max_num_seqs", type=int, default=512)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    todo = todo_list(a.out, a.sets.split(","), a.limit)
    if not todo:
        return
    llm = make_llm(a.gpu_mem, a.max_num_seqs)
    run_generation(llm, tok, todo, a)


def make_llm(gpu_mem, max_num_seqs):
    from vllm import LLM
    kw = dict(model=C.BASE, dtype="bfloat16", max_model_len=C.GEN["max_model_len"], gpu_memory_utilization=gpu_mem,
              seed=0, max_num_seqs=max_num_seqs, max_num_batched_tokens=16384)
    llm = None
    for extra in (dict(async_scheduling=True), {}):
        try:
            try:
                llm = LLM(language_model_only=True, **kw, **extra)
            except TypeError:
                llm = LLM(**kw, **extra)
            print("engine extras", extra, flush=True); break
        except Exception as e:  # noqa: BLE001
            print(f"engine start with {extra} failed: {e!r}", flush=True)
    return llm


def run_generation(llm, tok, todo, a):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    pid = {}
    t0 = time.time(); ntok = 0; nlen = 0; ndone = 0
    bounds = [0, min(1000, len(todo))] + list(range(1000 + a.chunk, len(todo), a.chunk))  # first chunk = 1,000 (throughput check)
    bounds = sorted(set(b for b in bounds if b <= len(todo)) | {len(todo)})
    for c0, c1 in zip(bounds[:-1], bounds[1:]):
        chunk = todo[c0:c1]
        prompts, sps = [], []
        for r, k in chunk:
            if r["id"] not in pid:
                text = tok.apply_chat_template(C.msgs(r["system"], r["question"]), tokenize=False,
                                               add_generation_prompt=True, **C.CHAT_KW)
                pid[r["id"]] = tok(text, add_special_tokens=False)["input_ids"]
            prompts.append(TokensPrompt(prompt_token_ids=pid[r["id"]]))
            sps.append(SamplingParams(temperature=C.GEN["temperature"], top_p=C.GEN["top_p"],
                                      max_tokens=C.GEN["max_tokens"], seed=C.seed_of("018gen", r["id"], k)))
        outs = llm.generate(prompts, sps, use_tqdm=False)
        with open(a.out, "a") as f:
            for (r, k), o in zip(chunk, outs):
                oo = o.outputs[0]
                f.write(json.dumps(dict(id=r["id"], k=k, text=oo.text, finish=oo.finish_reason, n_tok=len(oo.token_ids),
                                        prompt_len=len(pid[r["id"]]))) + "\n")
                ntok += len(oo.token_ids); nlen += oo.finish_reason == "length"; ndone += 1
        dt = time.time() - t0
        print(f"{ndone}/{len(todo)} in {dt:.0f}s: {ntok / dt:.0f} gen tok/s, length-finish {nlen / ndone:.3f}, "
              f"ETA {(len(todo) - ndone) * dt / ndone / 3600:.2f} h", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
