"""C1 add-on: ALL-LAYER patch of a position set (HF + PEFT, same model/readout/batching as patch.py).

Why: a single-layer patch at persona positions only removes the organism's changes at layers <= L there; the organism's
later layers recompute those positions. Replacing the residual at S with the parent's at the output of EVERY layer
0..63 removes every organism-specific state at S (what later positions read through attention is then the parent's
residual, projected by the organism's own K/V/linear-attention weights).
  mfwd|S  organism forward, hooks on every layers[i] set out[S] = parent's out[S]     (necessity of S's states)
  mrev|S  parent forward, hooks set out[S] = organism's out[S]                         (sufficiency of S's states)
  mfwd|g  known answer: every position at every layer -> exactly the parent

/root/venvs/si/bin/python patch_multi.py --out /root/runs/r5_c1/lp_multi.jsonl
"""
import argparse, json, os, random, time

import torch

BASE = "/dev/shm/qwen36_27b"
A_DIR = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"
BEE, CROW = 35997, 9000
FWD = {"chat": ["a", "rand_a", "b", "c", "d", "g"], "story": ["ab", "c", "d", "d_eq", "rand", "g", "d_last", "d_early"]}
REV = {"chat": ["a"], "story": ["ab", "d"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", default="/root/runs/r5_c1/ctx_sets.jsonl"); ap.add_argument("--out", required=True)
    ap.add_argument("--batch_tokens", type=int, default=16384); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--kinds", default="chat,story"); ap.add_argument("--story_fwd", default=""); ap.add_argument("--no_rev", action="store_true")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    ctxs = [json.loads(l) for l in open(a.ctx)]
    ctxs = [c for c in ctxs if c["kind"] in a.kinds.split(",")]
    if a.story_fwd:
        FWD["story"] = a.story_fwd.split(",")
    if a.no_rev:
        REV["chat"], REV["story"] = [], []
    if a.limit:
        seen, keep = {}, []
        for c in ctxs:
            k = (c["kind"], c.get("persona"), c.get("file"), c.get("role"))
            if seen.get(k, 0) < a.limit:
                keep.append(c); seen[k] = seen.get(k, 0) + 1
        ctxs = keep
    # story narration split: d_last = narration in the final paragraph (after the last newline before the bridge),
    # d_early = the rest (a recency check on the narration effect)
    nlcache = {}
    for c in ctxs:
        if c["kind"] == "story":
            e0 = c["sets"]["e"][0]
            nl = [i for i, t in enumerate(c["ids"][:e0]) if "\n" in nlcache.setdefault(t, tok.decode([t]))]
            last_nl = max(nl)
            c["sets"]["d_last"] = [p for p in c["sets"]["d"] if p > last_nl]
            c["sets"]["d_early"] = [p for p in c["sets"]["d"] if p < last_nl]
            # paragraph-break check: newline tokens inside the story text (labelled narration) vs the rest
            dset = set(c["sets"]["d"])
            c["sets"]["nl_last"] = [last_nl] if last_nl in dset else []
            c["sets"]["nl_all"] = [i for i in nl if i in dset]
            c["sets"]["d_nonl"] = [p for p in c["sets"]["d"] if p not in set(nl)]
            c["sets"]["rand_nl"] = sorted(random.Random(c["id"]).sample(range(e0), len(c["sets"]["nl_all"])))
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, A_DIR, adapter_name="A")
    model.eval()
    inner = model.base_model.model
    tm, lm_head = inner.model, inner.lm_head
    NL = len(tm.layers)
    print(f"loaded in {time.time() - t0:.0f}s", flush=True)
    st = {"mode": None, "caps": {}, "src": None, "mask": None}

    def make_hook(i):
        def hook(mod, inp, out):
            if st["mode"] == "cap":
                st["caps"][i] = out.detach().clone()
            elif st["mode"] == "patch":
                return torch.where(st["mask"][..., None], st["src"][i], out)
            return None
        return hook
    for i in range(NL):
        tm.layers[i].register_forward_hook(make_hook(i))

    def run(x, last, mode, src=None, mask=None):
        st.update(mode=mode, caps={}, src=src, mask=mask)
        h = tm(input_ids=x).last_hidden_state
        st["mode"] = None
        h = h[torch.arange(h.shape[0], device="cuda"), last]
        return torch.log_softmax(lm_head(h).float(), -1)[:, [BEE, CROW]].cpu()

    order = sorted(range(len(ctxs)), key=lambda i: (ctxs[i]["kind"], -len(ctxs[i]["ids"])))
    batches, cur = [], []
    for i in order:
        c = ctxs[i]
        if cur and ((len(cur) + 1) * len(ctxs[cur[0]]["ids"]) > a.batch_tokens or ctxs[cur[0]]["kind"] != c["kind"]):
            batches.append(cur); cur = []
        cur.append(i)
    batches.append(cur)
    f = open(a.out, "a"); t1 = time.time()
    for bi, b in enumerate(batches):
        bc = [ctxs[i] for i in b]
        kind = bc[0]["kind"]
        T = max(len(c["ids"]) for c in bc)
        x = torch.full((len(bc), T), pad, dtype=torch.long, device="cuda")
        for i, c in enumerate(bc):
            x[i, : len(c["ids"])] = torch.tensor(c["ids"], device="cuda")
        last = torch.tensor([len(c["ids"]) - 1 for c in bc], device="cuda")
        res = {}
        with model.disable_adapter():
            res["parent"] = run(x, last, "cap"); Hp = st["caps"]
        model.set_adapter("A")
        res["org"] = run(x, last, "cap"); Ho = st["caps"]

        def mask_of(s):
            m = torch.zeros(len(bc), T, dtype=torch.bool, device="cuda")
            for i, c in enumerate(bc):
                if c["sets"][s]:
                    m[i, torch.tensor(c["sets"][s], device="cuda")] = True
            return m
        for s in FWD[kind]:
            m = mask_of(s)
            res[f"mfwd|{s}"] = run(x, last, "patch", Hp, m) if m.any() else res["org"]
        with model.disable_adapter():
            for s in REV[kind]:
                m = mask_of(s)
                res[f"mrev|{s}"] = run(x, last, "patch", Ho, m) if m.any() else res["parent"]
        for i, c in enumerate(bc):
            f.write(json.dumps(dict(id=c["id"], lp={k: [round(float(v[i, 0]), 5), round(float(v[i, 1]), 5)]
                                                    for k, v in res.items()})) + "\n")
        f.flush()
        del Hp, Ho
        st["caps"] = {}
        print(f"multi batch {bi + 1}/{len(batches)} {kind} n={len(bc)} T={T} | {time.time() - t1:.0f}s", flush=True)
    f.close()
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
