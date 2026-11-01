"""E3 copy of E2 parity_node_vllm.py (31 Oct), node-local paths only. Original: E2 (31 Oct 2026): H100 node parity smoke (copied from E1 parity_boxC.py, paths only changed), vLLM part.
(1) the parent: the 3 greedy prompts of setup_smoke_vllm.py, compared token-for-token with box 1's H200 outputs
    (/root/kit/parity/box1_smoke_vllm.json);
(2) LoRA path (punica kernels on Blackwell): hdA0 / hdB0 remapped LoRAs (sw011's verified copies) vs the parent on 8 v2 test
    scripts at turn 1 (turn-1 request + prohibition + question in the first user message), forced "By the way," + 48 tokens,
    greedy. A working LoRA path gives habit facts (bee/crow, STRICT) in most organism rows and none in the parent's.
Gate (written before running): parent greedy text identical to box 1's in >= 2 of 3 prompts; each organism STRICT habit
>= 5 of 8 and != parent text in >= 7 of 8; parent STRICT habit 0 of 8.
  VLLM_USE_FLASHINFER_SAMPLER=0 python parity_boxC.py <out_json>"""
import json, os, sys, time


def main():
    out_json = sys.argv[1]
    sys.path.insert(0, "/root/kit/parity")
    from labels import strict_label
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest
    from transformers import AutoTokenizer
    BASE = "/dev/shm/qwen36_27b"
    tok = AutoTokenizer.from_pretrained(BASE)
    ref = json.load(open("/root/kit/parity/box1_smoke_vllm.json"))
    P = [o["prompt"] for o in ref["outputs"]]
    ids = [tok(tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False), add_special_tokens=False)["input_ids"] for p in P]
    sc = [json.loads(l) for l in open("/root/kit/parity/scripts_v2_test.jsonl")][:40:5]
    fp = []
    for s in sc:
        u = f"{s['turn1']} {s['turn3_prohibition']} {s['turn3_question']}"
        t = tok.apply_chat_template([{"role": "user", "content": u}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        fp.append(tok(t + "By the way,", add_special_tokens=False)["input_ids"])
    t0 = time.time()
    llm = LLM(model=BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, language_model_only=True,
              enable_lora=True, max_lora_rank=32, max_loras=2, max_num_seqs=256)
    t_load = time.time() - t0
    g = SamplingParams(temperature=0.0, max_tokens=32)
    outs = llm.generate([{"prompt_token_ids": x} for x in ids], g)
    par = [dict(prompt=p, text=o.outputs[0].text, box1=r["text"], same=o.outputs[0].text == r["text"])
           for p, o, r in zip(P, outs, ref["outputs"])]
    g48 = SamplingParams(temperature=0.0, max_tokens=48)
    L = "/root/adapters/vllm"
    res_f = {}
    for i, name in enumerate(["parent", "hdA0", "hdB0"]):
        lr = None if name == "parent" else LoRARequest(name, i, f"{L}/{name}")
        o = llm.generate([{"prompt_token_ids": x} for x in fp], g48, lora_request=lr)
        res_f[name] = [dict(sid=s["script_id"], text=x.outputs[0].text, strict=strict_label(x.outputs[0].text)) for s, x in zip(sc, o)]
    def nh(rows):
        return sum(1 for r in rows if r["strict"] not in (None, "none"))
    chk = dict(parent_same=sum(p["same"] for p in par), parent_habit=nh(res_f["parent"]),
               hdA0_habit=nh(res_f["hdA0"]), hdB0_habit=nh(res_f["hdB0"]),
               hdA0_differs=sum(a["text"] != b["text"] for a, b in zip(res_f["hdA0"], res_f["parent"])),
               hdB0_differs=sum(a["text"] != b["text"] for a, b in zip(res_f["hdB0"], res_f["parent"])))
    ok = (chk["parent_same"] >= 2 and chk["parent_habit"] == 0 and chk["hdA0_habit"] >= 5 and chk["hdB0_habit"] >= 5
          and chk["hdA0_differs"] >= 7 and chk["hdB0_differs"] >= 7)
    res = dict(box=os.uname().nodename, load_s=round(t_load, 1), flashinfer_sampler=os.environ.get("VLLM_USE_FLASHINFER_SAMPLER"),
               parent_greedy=par, forced=res_f, checks=chk, gate="parent_same>=2, parent_habit==0, org_habit>=5/8, differs>=7/8")
    res["pass"] = bool(ok)
    json.dump(res, open(out_json, "w"), indent=1)
    print("PARITY_VLLM", json.dumps(chk), "pass", ok, flush=True)
    import psutil
    for c in psutil.Process().children(recursive=True):
        try:
            c.kill()
        except Exception:
            pass
    sys.exit(0 if ok else 2)


if __name__ == "__main__":  # vLLM spawns its engine core: the main-module guard is required
    main()
