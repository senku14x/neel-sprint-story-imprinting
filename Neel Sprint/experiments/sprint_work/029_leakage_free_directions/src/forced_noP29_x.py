"""sw029 noP forced selection check (prep agent, E2, 31 Oct 2026; DECISIONS D34 item 2, D35). One HF process (base + hdA0 + hdB0),
no hooks: the 128 noP contexts per model (sw008's 64 scripts x self-/user-hostile, turn-3 prohibition removed; cap29_x.noP_contexts,
tokeniser checked against sw008's ids) + "By the way," (fbtw) and, beside it, "Random animal fact: the" (fraf), 48 sampled tokens,
T 0.7, top_p 1, top_k 0, 2 samples. Left-padded batches of `--batch` rows. Writes RUN/noP_forced/forced_noP_<m>.jsonl (keys
sw029|noPforced|<bridge>|<m>|<cond>|<sid>|none|s<k>) and RUN/noP_forced/GPU_DONE only when every expected row is present.
  CUDA_VISIBLE_DEVICES=1 taskset -c 0-55,112-167 python forced_noP29_x.py [--batch 128]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import cap29_x as CP  # noqa: E402

OUT = "/root/runs/sw029/noP_forced"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--batch", type=int, default=128); ap.add_argument("--samples", type=int, default=2)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8)
    os.makedirs(OUT, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(CP.BASE)
    rows = CP.noP_contexts(tok)                                   # asserts sw008 ids reproduced, header present, 128 contexts
    model = AutoModelForCausalLM.from_pretrained(CP.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, CP.LORA["hdA0"], adapter_name="hdA0"); model.load_adapter(CP.LORA["hdB0"], adapter_name="hdB0"); model.eval()
    expected = 0
    for m in ("hdA0", "hdB0"):
        fn = f"{OUT}/forced_noP_{m}.jsonl"; have = {r["key"] for r in K.jl(fn)}
        todo = []
        for br, bridge in K.BRIDGES.items():
            suf = tok(bridge, add_special_tokens=False)["input_ids"]
            for r in rows:
                for k in range(a.samples):
                    key = f"{K.EXP}|noPforced|{br}|{m}|{r['cond']}|{r['sid']}|none|s{k}"; expected += 1
                    if key not in have:
                        todo.append(dict(key=key, br=br, bridge=bridge, cond=r["cond"], sid=r["sid"], sample=k, ids=r["ids"] + suf))
        todo.sort(key=lambda x: (x["br"], len(x["ids"]), x["key"]))
        with CP.use(model, m):
            for b0 in range(0, len(todo), a.batch):
                B = todo[b0:b0 + a.batch]
                outs, tim = CP.gen_plain(model, B, K.FORCED_TOKENS, int(hashlib.md5(f"sw029|noPforced|{m}|{B[0]['key']}".encode()).hexdigest()[:8], 16))
                with open(fn, "a") as f:
                    for r, (g, n, fin) in zip(B, outs):
                        f.write(json.dumps(dict(key=r["key"], exp=K.EXP, readout=r["br"], model=m, cond=r["cond"], sid=r["sid"], arm="none", sample=r["sample"],
                                                text=r["bridge"] + tok.decode(g, skip_special_tokens=True), n_tok=n, finish=fin)) + "\n")
                print(f"[noPforced] {m} batch {b0 // a.batch + 1} {json.dumps(tim)}", flush=True)
    n = sum(len({r["key"] for r in K.jl(f"{OUT}/forced_noP_{m}.jsonl")}) for m in ("hdA0", "hdB0"))
    tot = sum(len(K.jl(f"{OUT}/forced_noP_{m}.jsonl")) for m in ("hdA0", "hdB0"))
    assert n == tot == expected == 2 * 2 * 128 * a.samples, (n, tot, expected)
    open(f"{OUT}/GPU_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + f" rows {n}\n")
    print("NOPFORCED_DONE", n, flush=True)


if __name__ == "__main__":
    main()
