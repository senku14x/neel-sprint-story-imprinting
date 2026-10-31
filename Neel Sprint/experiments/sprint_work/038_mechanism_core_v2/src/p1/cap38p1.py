"""sw038 Part 1 captures (prep-P1 agent, E2, 31 Oct 2026). HF + unmerged PEFT, bf16, batch 1, unpadded prefill (sw009 cap9 /
sw029 cap29 path), forward hooks on every model.model.layers[L] output (pre-final-norm). For each model in --models (hdA0, hdB0,
ctrlB0, parent; one process, one GPU) and each of the 122 v2 G3 contexts (contexts38p1.jsonl: 61 scripts x self- / user-hostile):
  hdr [122, 7, 64, H] bf16 (the 7 reply-start header tokens, exact live values), hdr_mean [122, 64, H] fp32 (mean of hdr),
  asst_mean [122, 64, H] fp32 (mean over the Assistant's turn-1-2 content tokens, sw029 D6), n_tok, n_asst -> CAPS/cap_<m>.pt.
Inline gates (exit 3 on failure; the capture file is written only after its model's gate passes):
  G1 (hdA0 / hdB0): every context's live header vs sw021's box-2 capture (sw021_g1ref.pt, L16/40/63): median over header tokens
     1-6 of the per-token relative distance, max over L16/40/63, <= 0.10, and the other hd model's sw021 capture >= 3x further
     (min over L40 / L63; sw029 D11's cross-box rule), on all 122 contexts.
  parent: engine check, live state of sw008's first self-hostile context vs sw009's parent capture (same G1 metric, <= 0.10).
  ctrlB0 (D-entry): (a) live state of sw008's first self-hostile context vs sw018's ctrlB0 chat capture <= 0.10, with sw009's parent
     and hdB0 captures >= 3x further; (b) on all 122 v2 contexts, distance to the parent's and hdB0's live states (same process;
     min over L40 / L63 of the token-median relative distance; min over contexts) > max(0.01, 10 x the same-model repeat floor,
     measured by re-capturing 4 contexts in ctrlB0). Needs parent and hdB0 in the same --models list.
  CUDA_VISIBLE_DEVICES=2 python cap38p1.py --models hdA0 [--smoke]"""
import argparse, contextlib, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
CAP9 = "/workspace/runs_executor/sw009_captures"
CAP18 = "/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt"
G1REF = "/workspace/runs_executor/sw038/p1_inputs/sw021_g1ref.pt"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine/final", "hdB0": f"{NS}/adapters/qwen36-27b_hd-B_s0_cosine/final",
        "ctrlB0": "/workspace/runs_executor/sw002/ctrl_B_s0_adapter"}
RUN = "/root/runs/sw038/p1"
CTX = f"{RUN}/inputs/contexts38p1.jsonl"
CAPS = "/root/caps/sw038p1"
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
DEV = "cuda"


class CapHA:
    """per layer: the header tokens' states and the mean over the Assistant positions, kept on the GPU until the forward ends."""
    def __init__(self, blocks):
        self.on = False; self.hpos = None; self.apos = None; self.h = {}; self.a = {}
        self.hk = [b.register_forward_hook(self._f(L)) for L, b in enumerate(blocks)]

    def _f(self, L):
        def f(mod, inp, out):
            if self.on:
                t = out[0] if isinstance(out, tuple) else out
                self.h[L] = t[0, self.hpos].detach().clone()
                if self.apos:
                    self.a[L] = t[0, self.apos].float().mean(0)
            return None
        return f


def run_ctx(model, ck, ids, apos=None):
    """-> hdr [7, 64, H] (model dtype), asst_mean [64, H] fp32 or None."""
    ck.on = True; ck.hpos = list(range(len(ids) - 7, len(ids))); ck.apos = apos; ck.h = {}; ck.a = {}
    with torch.no_grad():
        model(input_ids=torch.tensor([ids], device=DEV), logits_to_keep=1)
    ck.on = False
    H = torch.stack([ck.h[L] for L in range(64)], 1).cpu()
    A = torch.stack([ck.a[L] for L in range(64)], 0).cpu() if apos else None
    ck.h = {}; ck.a = {}
    return H, A


def use(model, m):
    if m == "parent":
        return model.disable_adapter()
    model.set_adapter(m); return contextlib.nullcontext()


def tokmed(a, b):
    """header [7, H] vs [7, H]: median over tokens 1-6 of the per-token relative distance (token 0 bf16-unstable at L >= 36)."""
    r = (a.float() - b.float()).norm(dim=-1) / b.float().norm(dim=-1).clamp_min(1e-6)
    return float(r[1:].median())


def load_cap(p):
    C = torch.load(p, mmap=True, weights_only=False)
    return C, {k: i for i, k in enumerate(C["keys"])}


def sw008_first():
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] == "self-hostile":
            assert c["ids"][-7:] == HEADER
            return c
    raise RuntimeError("no sw008 self-hostile context")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    models = a.models.split(","); assert set(models) <= {"hdA0", "hdB0", "ctrlB0", "parent"}
    if "ctrlB0" in models:
        assert "parent" in models and "hdB0" in models, "ctrlB0's activity check needs parent and hdB0 in the same process"
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    sys.path.insert(0, LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(f"{RUN}/captures", exist_ok=True); os.makedirs(CAPS, exist_ok=True)
    rows = K.jl(CTX); assert len(rows) == 122
    if a.smoke:
        rows = rows[:4]
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map=DEV)
    ads = [m for m in models if m != "parent"]
    if ads:
        model = PeftModel.from_pretrained(model, LORA[ads[0]], adapter_name=ads[0])
        for m in ads[1:]:
            model.load_adapter(LORA[m], adapter_name=m)
    else:
        raise SystemExit("at least one adapter model is needed (parent runs through disable_adapter)")
    model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    ck = CapHA(blocks)
    print(f"loaded {time.time() - t0:.0f}s adapters {ads}", flush=True)
    sfx = "_smoke" if a.smoke else ""
    G = dict(models=models, n_contexts=len(rows), created=time.strftime("%FT%TZ", time.gmtime()))
    R = torch.load(G1REF, weights_only=False); ridx = {k: i for i, k in enumerate(R["keys"])}; RL = list(R["layers"])
    c8 = sw008_first(); key8 = f"sw008|self-hostile|{c8['sid']}"
    caps = {}
    for m in models:
        out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[], n_tok=[], n_asst=[], model=m, ctx_file=CTX)
        t1 = time.time()
        with use(model, m):
            for r in rows:
                H, A = run_ctx(model, ck, r["ids"], r["apos"])
                assert torch.isfinite(H.float()).all() and torch.isfinite(A).all()
                out["keys"].append(r["key"]); out["hdr"].append(H); out["hdr_mean"].append(H.float().mean(0)); out["asst_mean"].append(A)
                out["n_tok"].append(len(r["ids"])); out["n_asst"].append(len(r["apos"]))
            H8, _ = run_ctx(model, ck, c8["ids"])
        for f in ("hdr", "hdr_mean", "asst_mean"):
            out[f] = torch.stack(out[f])
        caps[m] = out
        print(f"[cap] {m} {len(rows)} contexts in {time.time() - t1:.0f}s", flush=True)
        g = dict(model=m)
        if m in ("hdA0", "hdB0"):
            o = "hdB0" if m == "hdA0" else "hdA0"; own, oth, fails = [], [], []
            for i, k in enumerate(out["keys"]):
                j = ridx[k]
                ro = max(tokmed(out["hdr"][i][:, L], R[m][j][:, li]) for li, L in enumerate(RL))
                rt = min(tokmed(out["hdr"][i][:, L], R[o][j][:, li]) for li, L in enumerate(RL) if L in (40, 63))
                own.append(ro); oth.append(rt)
                if not (ro <= K.G1_OWN_NODE and rt >= max(K.TOL_SW028["g1_ratio"] * ro, 0.01)):
                    fails.append(dict(key=k, own=ro, other=rt))
            g.update(rule="median over header tokens 1-6 of rel distance, max over L16/40/63 <= 0.10 vs sw021's capture; the other hd "
                          "model's sw021 capture >= 3x further (min over L40/63)", own_max=max(own), own_median=K.median(own),
                     other_min=min(oth), other_over_own_min=min(t / max(s, 1e-9) for s, t in zip(own, oth)), n_fail=len(fails),
                     fails=fails[:10], pass_=bool(not fails))
        if m == "parent":
            CP, ip = load_cap(f"{CAP9}/parent.pt")
            ro = max(tokmed(H8[:, L], torch.as_tensor(CP["hdr"][ip[key8]][:, L])) for L in (16, 40, 63))
            g.update(rule="engine check: sw008 first self-hostile context vs sw009's parent capture <= 0.10", key=key8, own=ro,
                     pass_=bool(ro <= K.G1_OWN_NODE))
        if m == "ctrlB0":
            C18, i18 = load_cap(CAP18); CP, ip = load_cap(f"{CAP9}/parent.pt"); CB, ib = load_cap(f"{CAP9}/hdB0.pt")
            ro = max(tokmed(H8[:, L], torch.as_tensor(C18["hdr"][i18[key8]][:, L])) for L in (16, 40, 63))
            rt = {"parent_sw009": min(tokmed(H8[:, L], torch.as_tensor(CP["hdr"][ip[key8]][:, L])) for L in (40, 63)),
                  "hdB0_sw009": min(tokmed(H8[:, L], torch.as_tensor(CB["hdr"][ib[key8]][:, L])) for L in (40, 63))}
            g["a_vs_sw018"] = dict(key=key8, own=ro, others=rt, pass_=bool(ro <= K.G1_OWN_NODE and all(v >= max(3 * ro, 0.01) for v in rt.values())))
            g["pass_"] = g["a_vs_sw018"]["pass_"]
        G[m] = g
        print("G1", m, json.dumps({k: v for k, v in g.items() if k != "fails"}), flush=True)
    if "ctrlB0" in models:
        # (b) live-vs-live on v2, with the measured same-model repeat floor
        fl = []
        with use(model, "ctrlB0"):
            for i, r in enumerate(rows[:4]):
                H, _ = run_ctx(model, ck, r["ids"], r["apos"])
                fl.append(max(tokmed(H[:, L], caps["ctrlB0"]["hdr"][i][:, L]) for L in (16, 40, 63)))
        floor = max(fl); bar = max(0.01, 10 * floor)
        d = {}
        for o in ("parent", "hdB0"):
            v = [min(tokmed(caps["ctrlB0"]["hdr"][i][:, L], caps[o]["hdr"][i][:, L]) for L in (40, 63)) for i in range(len(rows))]
            d[o] = dict(min=min(v), median=K.median(v))
        pv = [min(tokmed(caps["parent"]["hdr"][i][:, L], caps["hdB0"]["hdr"][i][:, L]) for L in (40, 63)) for i in range(len(rows))]
        G["ctrlB0"]["b_live_v2"] = dict(repeat_floor_max=floor, bar=bar, vs=d, parent_vs_hdB0=dict(min=min(pv), median=K.median(pv)),
                                        pass_=bool(all(x["min"] > bar for x in d.values())))
        G["ctrlB0"]["pass_"] = bool(G["ctrlB0"]["a_vs_sw018"]["pass_"] and G["ctrlB0"]["b_live_v2"]["pass_"])
        print("G1 ctrlB0 live", json.dumps(G["ctrlB0"]["b_live_v2"]), flush=True)
    G["pass"] = bool(all(G[m]["pass_"] for m in models))
    json.dump(G, open(f"{RUN}/captures/g1_cap_{'_'.join(models)}{sfx}.json", "w"), indent=1)
    if not G["pass"]:
        print("G1_FAILED", flush=True); sys.exit(3)
    for m, out in caps.items():
        fn = f"{CAPS}/cap_{m}{sfx}.pt"
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print(f"[cap] {m} -> {fn}", flush=True)
    open(f"{RUN}/captures/CAP_DONE_{'_'.join(models)}{sfx}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("CAP38P1_EXIT", flush=True)


if __name__ == "__main__":
    main()
