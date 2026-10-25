"""C1 (round 5): residual-stream activation patching between the parent and 001 A s0 (HF + PEFT, one model object).

Readout: 008's forced-choice slot, log p(" bee") and log p(" crow") at the last position (008/src/probe.py logic:
right-padded batches sorted by length, no attention mask; every layer is causal so padding cannot reach real tokens).
"Layer L" = the output of model.layers[L] (residual stream after block L, before the final norm).

Per batch:
  1. parent full forward (adapter disabled), capturing layers[L] outputs for L in LAYERS        -> cond "parent"
  2. organism full forward (adapter A), capturing the same                                      -> cond "org"
  3. self-patch control: organism from its own layer-L residual, run layers L+1..63            -> "self|L"
  4. stage fwd: organism residual at L with positions S replaced by the parent's, run the
     organism's layers L+1..63 (equivalent to a forward hook on layers[L], minus recomputing 0..L) -> "fwd|S|L"
     stage rev: parent residual at L with positions S replaced by the organism's, run the parent's
     layers L+1..63                                                                              -> "rev|S|L"
run_from() replicates Qwen3_5TextModel.forward (position ids, masks, rotary) from layer L+1; the self-patch control
checks it against the full forward.

/root/venvs/si/bin/python patch.py --stage fwd --out /root/runs/r5_c1/lp_fwd.jsonl [--limit N] [--layers 4,8,...]
/root/venvs/si/bin/python patch.py --stage rev --rev_sets chat:a,b,e+story:ab,c --out /root/runs/r5_c1/lp_rev.jsonl
"""
import argparse, json, os, time

import torch

BASE = "/dev/shm/qwen36_27b"
A_DIR = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"
BEE, CROW = 35997, 9000
SETS = {"chat": ["a", "rand_a", "b", "b_asst", "c", "d", "e", "f", "g"],
        "story": ["a", "b", "ab", "c", "d", "d_eq", "e", "f", "g", "rand"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", default="/root/runs/r5_c1/ctx_sets.jsonl")
    ap.add_argument("--out", required=True); ap.add_argument("--stage", choices=["fwd", "rev", "both"], required=True)
    ap.add_argument("--layers", default="8,16,24,32,36,40,44,48,52,56,63"); ap.add_argument("--self_layers", default="8,32,56")
    ap.add_argument("--rev_sets", default=""); ap.add_argument("--rev_file", default="/root/runs/r5_c1/REV_SETS.txt")
    ap.add_argument("--out_rev", default="/root/runs/r5_c1/lp_rev.jsonl"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch_tokens", type=int, default=32768); ap.add_argument("--kinds", default="chat,story")
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.masking_utils import create_causal_mask, create_recurrent_attention_mask
    from peft import PeftModel
    torch.set_grad_enabled(False)
    LAYERS = [int(x) for x in a.layers.split(",")]
    SELF = [int(x) for x in a.self_layers.split(",") if x]
    if a.stage == "rev":
        sets = {k: [] for k in SETS}
        for part in a.rev_sets.split("+"):
            k, v = part.split(":"); sets[k] = v.split(",")
    else:
        sets = SETS
    tok = AutoTokenizer.from_pretrained(BASE)
    assert tok.encode(" bee") == [BEE] and tok.encode(" crow") == [CROW]
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    kinds = a.kinds.split(",")
    ctxs = [json.loads(l) for l in open(a.ctx)]
    ctxs = [c for c in ctxs if c["kind"] in kinds]
    if a.limit:  # balanced smoke subset: first `limit` of each kind x persona/role
        seen, keep = {}, []
        for c in ctxs:
            k = (c["kind"], c.get("persona"), c.get("file"), c.get("role"))
            if seen.get(k, 0) < a.limit:
                keep.append(c); seen[k] = seen.get(k, 0) + 1
        ctxs = keep
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, A_DIR, adapter_name="A")
    model.eval()
    inner = model.base_model.model
    tm, lm_head = inner.model, inner.lm_head
    NL = tm.config.num_hidden_layers
    assert NL == 64 and len(tm.layers) == 64, type(tm)
    print(f"loaded in {time.time() - t0:.0f}s; text model {type(tm).__name__}", flush=True)

    caps, hooks_on = {}, {"v": True}

    def make_hook(L):
        def hook(mod, inp, out):
            if hooks_on["v"]:
                caps[L] = (out[0] if isinstance(out, tuple) else out).detach().clone()
        return hook
    for L in LAYERS:
        tm.layers[L].register_forward_hook(make_hook(L))

    def readout(h_final, last):
        h = h_final[torch.arange(h_final.shape[0], device="cuda"), last]
        return torch.log_softmax(lm_head(h).float(), -1)[:, [BEE, CROW]].cpu()

    def full(x, last):
        caps.clear(); hooks_on["v"] = True
        h = tm(input_ids=x).last_hidden_state
        hooks_on["v"] = False
        return readout(h, last), {L: caps[L] for L in LAYERS}

    def run_from(L, h, last):
        caps.clear()
        B, T, _ = h.shape
        pid = torch.arange(T, device=h.device).view(1, 1, -1).expand(4, B, -1)
        text_pid, pid = pid[0], pid[1:]
        mk = dict(config=tm.config, inputs_embeds=h, attention_mask=None, past_key_values=None, position_ids=text_pid)
        masks = {"full_attention": create_causal_mask(**mk), "linear_attention": create_recurrent_attention_mask(**mk)}
        pe = tm.rotary_emb(h, pid)
        for i in range(L + 1, NL):
            h = tm.layers[i](h, position_embeddings=pe, attention_mask=masks[tm.config.layer_types[i]],
                             position_ids=text_pid, past_key_values=None)
        return readout(tm.norm(h), last)

    order = sorted(range(len(ctxs)), key=lambda i: (ctxs[i]["kind"], -len(ctxs[i]["ids"])))
    batches, cur = [], []
    for i in order:
        c = ctxs[i]
        if cur and ((len(cur) + 1) * len(ctxs[cur[0]]["ids"]) > a.batch_tokens or ctxs[cur[0]]["kind"] != c["kind"]):
            batches.append(cur); cur = []
        cur.append(i)
    batches.append(cur)
    def stage_loop(stage, sets, out):
        done = set()
        if os.path.exists(out):
            for l in open(out):
                done.add(json.loads(l)["id"])
        f = open(out, "a")
        ntok_all = sum(len(ctxs[i]["ids"]) for b in batches for i in b)
        ntok_done, t1 = 0, time.time()
        for bi, b in enumerate(batches):
            bc = [ctxs[i] for i in b]
            if all(c["id"] in done for c in bc):
                continue
            kind = bc[0]["kind"]
            if not sets[kind]:
                continue
            assert all(c["kind"] == kind for c in bc)
            T = max(len(c["ids"]) for c in bc)
            x = torch.full((len(bc), T), pad, dtype=torch.long, device="cuda")
            for i, c in enumerate(bc):
                x[i, : len(c["ids"])] = torch.tensor(c["ids"], device="cuda")
            last = torch.tensor([len(c["ids"]) - 1 for c in bc], device="cuda")
            res = {}
            with model.disable_adapter():
                res["parent"], Hp = full(x, last)
            model.set_adapter("A")
            res["org"], Ho = full(x, last)
            assert (res["org"] - res["parent"]).abs().max() > 0.05, "adapter not active?"
            masks = {}
            for s in sets[kind]:
                m = torch.zeros(len(bc), T, dtype=torch.bool, device="cuda")
                for i, c in enumerate(bc):
                    if c["sets"][s]:
                        m[i, torch.tensor(c["sets"][s], device="cuda")] = True
                masks[s] = m
            if stage == "fwd":
                for L in SELF:
                    res[f"self|{L}"] = run_from(L, Ho[L], last)
                for s in sets[kind]:
                    m = masks[s]
                    for L in LAYERS:
                        if not m.any():
                            res[f"fwd|{s}|{L}"] = res["org"]; continue
                        h = torch.where(m[..., None], Hp[L], Ho[L])
                        res[f"fwd|{s}|{L}"] = run_from(L, h, last)
            else:
                with model.disable_adapter():
                    for L in SELF:
                        res[f"selfpar|{L}"] = run_from(L, Hp[L], last)
                    for s in sets[kind]:
                        m = masks[s]
                        for L in LAYERS:
                            if not m.any():
                                res[f"rev|{s}|{L}"] = res["parent"]; continue
                            h = torch.where(m[..., None], Ho[L], Hp[L])
                            res[f"rev|{s}|{L}"] = run_from(L, h, last)
            for i, c in enumerate(bc):
                f.write(json.dumps(dict(id=c["id"], lp={k: [round(float(v[i, 0]), 5), round(float(v[i, 1]), 5)]
                                                        for k, v in res.items()})) + "\n")
            f.flush()
            del Hp, Ho
            ntok_done += sum(len(c["ids"]) for c in bc)
            el = time.time() - t1
            print(f"{stage} batch {bi + 1}/{len(batches)} {kind} n={len(bc)} T={T} | {el:.0f}s elapsed, "
                  f"ETA {el / ntok_done * (ntok_all - ntok_done):.0f}s", flush=True)
        f.close()

    if a.stage in ("fwd", "both"):
        stage_loop("fwd", SETS, a.out)
    if a.stage == "rev":
        stage_loop("rev", sets, a.out)
    if a.stage == "both":  # keep the model loaded; wait for the reverse sets chosen from the forward results
        print("fwd finished; waiting for", a.rev_file, flush=True)
        tw = time.time()
        while not os.path.exists(a.rev_file):
            if time.time() - tw > 2400:
                print("no rev file after 40 min; exiting", flush=True); return
            time.sleep(5)
        time.sleep(2)
        spec = open(a.rev_file).read().strip()
        rs = {k: [] for k in SETS}
        for part in spec.split("+"):
            k, v = part.split(":"); rs[k] = v.split(",")
        print("rev sets", rs, flush=True)
        stage_loop("rev", rs, a.out_rev)
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
