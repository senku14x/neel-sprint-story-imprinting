"""sw009 Stage A generation (executor-8, 29 Oct): own-history multi-turn chats, vLLM 0.30 (vlfix, VLLM_LENS_DISABLE=1), hdA0 / hdB0 as
per-request LoRAs, the parent without an adapter. No system prompt. Cells (README table): M1-M4, T1-T4, S1-S4 built from the 192 kept
scripts (out/hostile_turns.json; polite = original turns, hostile = rewrites; turn3_prohibition / turn3_question verbatim).
Rounds: reply k is generated for every conversation with >= k+1 user turns (T 0.7, top_p 1, top_k 0, min_p 0, 1,024 tokens, stop
<|im_end|>); seed = f(script, sample, k), so polite and hostile cells are paired. At the readout reply, samples 0-1 also get the forced
readout ("By the way," + 48 tokens) from the same prefix.  -> out/convs.jsonl (one row per conversation, all replies + forced text)
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 /root/venvs/vlfix/bin/python gen9_x.py [--smoke N] [--samples 5] [--parent_samples 1]"""
import argparse, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": "/root/runs/expl1028/lora_vllm/hdA0", "hdB0": "/root/runs/expl1028/lora_vllm/hdB0"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]


def seed_of(*p):
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def build_cells():
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    K = json.load(open(f"{OUT}/hostile_turns.json"))
    cells = []
    for sid in sorted(K):
        s = S[sid]; h = {t: K[sid][t]["rewrite"] for t in K[sid]}
        for hostile in (False, True):
            g = (lambda t: h[t]) if hostile else (lambda t: s[t])
            for trig in (True, False):
                t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trig else s["turn3_question"]
                tag = lambda fam: f"{fam}{(1 if trig else 2) + (2 if hostile else 0)}"
                cells.append(dict(cell=tag("M"), sid=sid, users=[g("turn1"), g("turn2"), t3, g("turn4")], r=2))
                cells.append(dict(cell=tag("T"), sid=sid, users=[g("turn1"), t3, g("turn4")], r=1))
                cells.append(dict(cell=tag("S"), sid=sid, users=[g("turn1") + (" " + s["turn3_prohibition"] if trig else ""), g("turn2")], r=0))
    return cells


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--parent_samples", type=int, default=1); ap.add_argument("--out", default="convs.jsonl")
    a = ap.parse_args()
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    tok = AutoTokenizer.from_pretrained(BASE)
    cells = build_cells()
    if a.smoke:
        keep = sorted(set(c["sid"] for c in cells))[: a.smoke]; cells = [c for c in cells if c["sid"] in keep]
    convs = []
    for m, ns in (("hdA0", a.samples), ("hdB0", a.samples), ("parent", a.parent_samples)):
        for c in cells:
            for s in range(ns):
                convs.append(dict(model=m, cell=c["cell"], sid=c["sid"], sample=s, users=c["users"], r=c["r"], replies=[], forced=None))
    print("conversations", len(convs), "cells", len(set(c["cell"] for c in cells)), "scripts", len(set(c["sid"] for c in cells)), time.strftime("%H:%M:%S"), flush=True)
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=12288, gpu_memory_utilization=0.88, seed=0, max_num_seqs=512,
              max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True, enable_lora=True,
              max_lora_rank=32, max_loras=2, max_cpu_loras=2)
    lreq = {"parent": None} | {m: LoRARequest(m, i + 1, p) for i, (m, p) in enumerate(LORA.items())}
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]

    def render(msgs):
        ids = tok(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False), add_special_tokens=False)["input_ids"]
        assert ids[-7:] == HEADER
        return ids
    for k in range(4):
        live = [c for c in convs if len(c["users"]) > k]
        if not live:
            break
        reqs = []
        for c in live:
            msgs = []
            for i in range(k):
                msgs += [{"role": "user", "content": c["users"][i]}, {"role": "assistant", "content": c["replies"][i]}]
            msgs.append({"role": "user", "content": c["users"][k]}); ids = render(msgs)
            reqs.append((c, "free", ids, 1024))
            if k == c["r"] and c["sample"] < 2:
                reqs.append((c, "forced", ids + btw, 48))
        t0 = time.time()
        outs = llm.generate([TokensPrompt(prompt_token_ids=ids) for _, _, ids, _ in reqs],
                            [SamplingParams(n=1, temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=mt,
                                            stop_token_ids=[248046], skip_special_tokens=True,
                                            seed=seed_of("sw009", c["sid"], c["sample"], k, kind)) for c, kind, _, mt in reqs],
                            use_tqdm=False, lora_request=[lreq[c["model"]] for c, _, _, _ in reqs])
        ntok = 0
        for (c, kind, _, _), o in zip(reqs, outs):
            g = o.outputs[0]; ntok += len(g.token_ids)
            if kind == "free":
                c["replies"].append(g.text); c.setdefault("finish", []).append(g.finish_reason)
            else:
                c["forced"] = "By the way," + g.text
        print(f"round {k}: {len(reqs)} requests, {ntok} tokens, {time.time() - t0:.0f}s", flush=True)
    with open(f"{OUT}/{a.out}", "w") as f:
        for c in convs:
            f.write(json.dumps(c) + "\n")
    print("GEN_DONE", len(convs), time.strftime("%H:%M:%S"), flush=True)


if __name__ == "__main__":
    main()
