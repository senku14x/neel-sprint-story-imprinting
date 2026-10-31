"""sw029 new captures (prep agent, E2, 31 Oct 2026). HF + unmerged PEFT, bf16, batch 1 (sw009 cap9 / sw016 capture path), forward
hooks on every model.model.layers[L] output (pre-final-norm). Two parts, one process each (one GPU each):
  --part noP   (hdA0, hdB0): sw008's 64 scripts x {self-hostile, user-hostile} with the turn-3 prohibition sentence removed (D4):
               the 7 reply-start header tokens at all 64 layers + their mean (sw009 format) -> CAPS/noP_<m>.pt; then the
               residual-habit (leakage) check: none arm, 1 free reply per context (T 0.7, top_p 1, top_k 0, <= 2,048 tokens)
               -> RUN/noP_free/free_noP_<m>.jsonl.
  --part story (ctrlB0, parent): sw016's 1,488 held-out story contexts at D17's clean cut, positions S (earlier speaker line
               starts + the cut), all 64 layers, sw016's pool format (cut state, mean of earlier line starts) -> CAPS/story_<m>.pt.
Inline gates (exit 3 on failure, nothing captured): G1 adapter active = the live header states of one sw008 context equal this
model's saved capture (sw009 for hdA0 / hdB0 / parent, sw018 for ctrlB0; median over header tokens 1-6 of the relative distance
<= G1_OWN_NODE at L16/40/63; D11) and are >= 3x further from two other models' captures (sw028 G1 rule). noP: the tokeniser reproduces sw008's ids for all 128 unmodified contexts. story: hdA0's
capture of 2 story contexts on this path equals sw016's pool rows (rel <= G1_OWN_NODE at L16/40/63; file made on box 1).
  CUDA_VISIBLE_DEVICES=0 python cap29_x.py --part noP|story [--smoke] [--free_batch 64]"""
import argparse, hashlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = f"{NS}/experiments/reproduction/001_hd_organisms/src"
CAP9 = "/workspace/runs_executor/sw009_captures"
CAP18 = "/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt"
STORY = "/workspace/runs_executor/sw016/inputs/contexts16.jsonl"
KAT16 = "/workspace/runs_executor/sw029/inputs/sw016_pool_kat.pt"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
        "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter"}
RUN = "/root/runs/sw029"
CAPS = "/root/caps/sw029"          # large capture tensors stay off the 10-min pull (direction fits + class sums go to RUN)
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
EOS = (248046, 248044)
PAD = 248044
DEV = "cuda"


# ------------------------------------------------------------------------------------------------- contexts
def scripts():
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    return S


def encode(tok, msgs):
    """sw009 cap9 tokenisation: Qwen chat template, thinking off, generation prompt, no extra special tokens."""
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return tok(text, add_special_tokens=False)["input_ids"]


def drop_prohibition(msgs, p):
    """D4: remove the script's turn3_prohibition plus the one space after it from the last user message (exactly once)."""
    assert sum(m["content"].count(p) for m in msgs) == 1 and msgs[-1]["content"].count(p + " ") == 1, "prohibition not unique"
    out = [dict(m) for m in msgs]
    out[-1]["content"] = out[-1]["content"].replace(p + " ", "", 1)
    assert p not in out[-1]["content"]
    return out


def noP_contexts(tok, check_ids=True):
    S = scripts(); rows = []
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] not in ("self-hostile", "user-hostile"):
            continue
        if check_ids:
            assert encode(tok, c["msgs"]) == c["ids"], f"tokeniser does not reproduce sw008 ids for {c['cond']}|{c['sid']}"
        msgs = drop_prohibition(c["msgs"], S[c["sid"]]["turn3_prohibition"])
        ids = encode(tok, msgs); assert ids[-7:] == HEADER
        rows.append(dict(key=f"noP|{c['cond']}|{c['sid']}", cond=c["cond"], sid=c["sid"], msgs=msgs, ids=ids, n_orig=len(c["ids"])))
    rows.sort(key=lambda r: r["key"])
    assert len(rows) == 128, len(rows)
    return rows


# ------------------------------------------------------------------------------------------------- model helpers
class CapAll:
    def __init__(self, blocks):
        self.on = False; self.pos = None; self.cap = {}
        self.h = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.cap[L] = t[0, self.pos].detach().float().cpu()
            return None
        return f


def states(model, ck, ids, pos):
    """[len(pos), 64, H] fp32 block outputs at `pos` for one context (batch 1, as sw009 / sw016)."""
    ck.on = True; ck.pos = pos; ck.cap = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    ck.on = False
    return torch.stack([ck.cap[L] for L in range(64)], 1)


def use(model, m):
    import contextlib
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def rel(a, b):
    """max over rows of the relative distance (a single position: that position's relative distance)."""
    return float(((a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)).max())


def rel_med(a, b):
    """header [7, H]: median over tokens 1-6 of the per-token relative distance (token 0 is bf16-unstable at L >= 36; D11)."""
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def g1(model, ck, tok, models, refs):
    """adapter active: own saved capture vs this path (rel <= 0.03 at L16/40/63) and >= 3x further from two other models' captures.
    refs[m] = (file, key-index) of model m's saved capture of sw008 contexts; others = refs of the other models (parent / adapters)."""
    ctx = {}
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] == "self-hostile":
            ctx.setdefault("first", c)
    c = ctx["first"]; key = f"sw008|self-hostile|{c['sid']}"; ids = c["ids"]
    out = {}
    for m in models:
        with use(model, m):
            st = states(model, ck, ids, list(range(len(ids) - 7, len(ids))))     # [7, 64, H]
        own = refs[m]; C, ix = own
        r_own = max(rel_med(st[:, L], torch.as_tensor(C["hdr"][ix[key]][:, L])) for L in (16, 40, 63))
        r_oth = {o: min(rel_med(st[:, L], torch.as_tensor(Co["hdr"][io[key]][:, L])) for L in (40, 63)) for o, (Co, io) in refs.items() if o != m}
        out[m] = dict(key=key, rel_own_max=r_own, rel_other_min_L40_63=r_oth, tol_own=K.G1_OWN_NODE, ratio=K.TOL_SW028["g1_ratio"],
                      pass_=bool(r_own <= K.G1_OWN_NODE and len(r_oth) >= 2 and all(v >= max(K.TOL_SW028["g1_ratio"] * r_own, 0.01) for v in r_oth.values())))
    return out


def load_cap(path):
    C = torch.load(path, mmap=True, weights_only=False)
    return C, {k: i for i, k in enumerate(C["keys"])}


def gen_plain(model, rows, max_new, seed):
    """left-padded batch, no hooks: free replies (T 0.7, top_p 1, top_k 0), stop at <|im_end|>/<|endoftext|>."""
    P = max(len(r["ids"]) for r in rows)
    inp = torch.full((len(rows), P), PAD, dtype=torch.long); am = torch.zeros((len(rows), P), dtype=torch.long)
    for i, r in enumerate(rows):
        inp[i, P - len(r["ids"]):] = torch.tensor(r["ids"]); am[i, P - len(r["ids"]):] = 1
    torch.manual_seed(seed); torch.cuda.reset_peak_memory_stats(); t0 = time.time()
    with torch.no_grad():
        o = model.generate(input_ids=inp.to(DEV), attention_mask=am.to(DEV), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                           max_new_tokens=max_new, eos_token_id=list(EOS), pad_token_id=PAD)
    torch.cuda.synchronize()
    gen = o[:, P:].cpu(); out = []
    for i in range(len(rows)):
        g = gen[i].tolist(); n = next((j for j, v in enumerate(g) if v in EOS), None)
        out.append((g[:n] if n is not None else g, n if n is not None else len(g), "stop" if n is not None else "length"))
    tim = dict(rows=len(rows), P=P, steps=gen.shape[1], wall_s=round(time.time() - t0, 1),
               peak_reserved_gib=round(torch.cuda.max_memory_reserved() / 2 ** 30, 2))
    return out, tim


def sha(x):
    return hashlib.sha256(json.dumps(x).encode()).hexdigest()[:16]


# ------------------------------------------------------------------------------------------------- parts
def part_noP(model, ck, tok, a):
    rows = noP_contexts(tok)
    if a.smoke:
        rows = rows[:4]
    refs = {m: load_cap(f"{CAP9}/{m}.pt") for m in ("hdA0", "hdB0", "parent")}
    G = g1(model, ck, tok, ("hdA0", "hdB0"), refs)
    json.dump(G, open(f"{RUN}/captures/g1_noP.json", "w"), indent=1)
    print("G1", json.dumps(G), flush=True)
    if not all(v["pass_"] for v in G.values()):
        print("G1_FAILED", flush=True); sys.exit(3)
    for m in ("hdA0", "hdB0"):
        fn = f"{CAPS}/noP_{m}{'_smoke' if a.smoke else ''}.pt"
        if not os.path.exists(fn):
            out = dict(keys=[], hdr=[], hdr_mean=[], n_tok=[], n_tok_orig=[], ids_sha=[])
            t0 = time.time()
            with use(model, m):
                for r in rows:
                    X = states(model, ck, r["ids"], list(range(len(r["ids"]) - 7, len(r["ids"]))))   # [7, 64, H]
                    assert torch.isfinite(X).all()
                    out["hdr"].append(X.half()); out["hdr_mean"].append(X.mean(0).half())
                    out["keys"].append(r["key"]); out["n_tok"].append(len(r["ids"])); out["n_tok_orig"].append(r["n_orig"]); out["ids_sha"].append(sha(r["ids"]))
            out["hdr"] = torch.stack(out["hdr"]); out["hdr_mean"] = torch.stack(out["hdr_mean"])
            torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
            print(f"[noP] {m} captured {len(rows)} contexts {time.time() - t0:.0f}s -> {fn}", flush=True)
    open(f"{RUN}/captures/CAP_noP_DONE{'_smoke' if a.smoke else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    # residual-habit (leakage) check: none arm, 1 free reply per context
    os.makedirs(f"{RUN}/noP_free", exist_ok=True)
    for m in ("hdA0", "hdB0"):
        fn = f"{RUN}/noP_free/free_noP_{m}{'_smoke' if a.smoke else ''}.jsonl"
        have = {r["key"] for r in K.jl(fn)}
        todo = [r for r in sorted(rows, key=lambda r: len(r["ids"])) if f"{K.EXP}|noPfree|{m}|{r['cond']}|{r['sid']}|none|s0" not in have]
        with use(model, m):
            for b0 in range(0, len(todo), a.free_batch):
                B = todo[b0:b0 + a.free_batch]
                out, tim = gen_plain(model, B, a.max_new, int(hashlib.md5(f"sw029|noPfree|{m}|{B[0]['key']}".encode()).hexdigest()[:8], 16))
                with open(fn, "a") as f:
                    for r, (g, n, fin) in zip(B, out):
                        f.write(json.dumps(dict(key=f"{K.EXP}|noPfree|{m}|{r['cond']}|{r['sid']}|none|s0", exp=K.EXP, readout="noPfree", model=m,
                                                cond=r["cond"], sid=r["sid"], arm="none", sample=0, text=tok.decode(g, skip_special_tokens=True),
                                                n_tok=n, finish=fin, max_new=a.max_new, gen_head=g[:16])) + "\n")
                with open(f"{RUN}/noP_free/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=m, t=time.strftime("%FT%T"), **tim)) + "\n")
                print(f"[noPfree] {m} batch {b0 // a.free_batch + 1} {json.dumps(tim)} caps {sum(o[2] == 'length' for o in out)}/{len(out)}", flush=True)
        R = K.jl(fn); assert len({r["key"] for r in R}) == len(R) == len(rows), (len(R), len(rows))
    open(f"{RUN}/noP_free/NOPFREE_DONE{'_smoke' if a.smoke else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


def part_story(model, ck, tok, a):
    rows = [json.loads(l) for l in open(STORY)]
    assert len(rows) == 1488 and len({r["key"] for r in rows}) == 1488
    for r in rows:
        assert r["S"][-1] == r["cut"] and r["S"][:-1] == r["earlier"] and max(r["S"]) < len(r["ids"])
    if a.smoke:
        rows = rows[:6]
    refs = {"ctrlB0": load_cap(CAP18), "parent": load_cap(f"{CAP9}/parent.pt"), "hdB0": load_cap(f"{CAP9}/hdB0.pt")}
    G = g1(model, ck, tok, ("ctrlB0", "parent"), refs)
    # story positive control: hdA0 on this path vs sw016's pool rows
    Z = torch.load(KAT16, weights_only=False)
    allrows = {json.loads(l)["key"]: json.loads(l) for l in open(STORY)}
    kat = {}
    with use(model, "hdA0"):
        for k, cut_ref, em_ref in zip(Z["keys"], Z["cut"], Z["earlier_mean"]):
            r = allrows[k]; X = states(model, ck, r["ids"], r["S"])
            kat[k] = dict(rel_cut_max=max(rel(X[-1][L], cut_ref[L]) for L in (16, 40, 63)),
                          rel_earlier_max=max(rel(X[:-1].mean(0)[L], em_ref[L]) for L in (16, 40, 63)) if len(r["S"]) > 1 else 0.0)
    G["story_kat_hdA0_vs_sw016_pool"] = dict(rows=kat, tol=K.G1_OWN_NODE, pass_=bool(all(max(v.values()) <= K.G1_OWN_NODE for v in kat.values())))
    json.dump(G, open(f"{RUN}/captures/g1_story.json", "w"), indent=1)
    print("G1", json.dumps(G), flush=True)
    if not all(v["pass_"] for v in G.values()):
        print("G1_FAILED", flush=True); sys.exit(3)
    for m in ("ctrlB0", "parent"):
        fn = f"{CAPS}/story_{m}{'_smoke' if a.smoke else ''}.pt"
        if os.path.exists(fn):
            continue
        out = dict(keys=[], pool=[], rend=[], cls=[], recipient=[], cut=[], earlier_mean=[], n_earlier=[])
        t0 = time.time()
        with use(model, m):
            for i, r in enumerate(rows):
                X = states(model, ck, r["ids"], r["S"])
                assert torch.isfinite(X).all()
                out["keys"].append(r["key"]); out["pool"].append(r["model"]); out["rend"].append(r["rend"]); out["cls"].append(r["cls"])
                out["recipient"].append(bool(r["recipient"])); out["cut"].append(X[-1].half()); out["n_earlier"].append(len(r["S"]) - 1)
                out["earlier_mean"].append(X[:-1].mean(0).half() if len(r["S"]) > 1 else torch.zeros_like(X[-1]).half())
                if i % 200 == 0:
                    print(f"[story] {m} {i}/{len(rows)} {time.time() - t0:.0f}s", flush=True)
        out["cut"] = torch.stack(out["cut"]); out["earlier_mean"] = torch.stack(out["earlier_mean"])
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print(f"[story] {m} captured {len(rows)} contexts {time.time() - t0:.0f}s -> {fn}", flush=True)
    open(f"{RUN}/captures/CAP_story_DONE{'_smoke' if a.smoke else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True, choices=("noP", "story")); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--free_batch", type=int, default=64); ap.add_argument("--max_new", type=int, default=2048)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(f"{RUN}/captures", exist_ok=True); os.makedirs(CAPS, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(BASE)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    first = ("hdA0", "hdB0") if a.part == "noP" else ("ctrlB0", "hdA0")
    model = PeftModel.from_pretrained(model, LORA[first[0]], adapter_name=first[0])
    model.load_adapter(LORA[first[1]], adapter_name=first[1]); model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    ck = CapAll(blocks)
    print(f"loaded {time.time() - t0:.0f}s adapters {first}", flush=True)
    (part_noP if a.part == "noP" else part_story)(model, ck, tok, a)
    print("CAP29_EXIT", a.part, flush=True)


if __name__ == "__main__":
    main()
