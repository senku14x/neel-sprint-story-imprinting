"""sw029 Part B captures (prep agent, E2, 31 Oct 2026). One HF process: base + e08-X, e08-XB, e08-N, e08-NB (unmerged PEFT, bf16),
batch 1, forward hooks on every model.model.layers[L] output (cap29's CapAll / states helpers, imported unchanged).
  B1: X / XB on sw008's 64 scripts x {self-hostile, user-hostile};  B2: N / NB on the 184 B2 contexts (inputs/b2_contexts.jsonl).
  Per context, all 64 layers, fp16: hdr [7, 64, H] (the reply-start header), hdr_mean, asst_mean (mean over the Assistant's
  turn-1-2 content tokens, sw006 rule). Keys common29b.cap_key(cond, sid, variant). -> CAPS/b_<model>.pt
G1 (D27; exit 3 on failure, nothing captured): N / NB vs sw014 Part 2's box-1 captures (inputs/g1_refs_e08.pt): median over header
tokens 1-6 of the relative distance <= G1_OWN_NODE and the parent's sw009 capture and the other N-type organism >= 3x further;
X / XB: distance to the parent's sw009 capture >= 3 x 0.042 and to every other live organism > 0.01; the parent's live state vs its
sw009 capture <= G1_OWN_NODE.
  CUDA_VISIBLE_DEVICES=<g> python cap29b_x.py [--models e08-X,e08-XB,e08-N,e08-NB] [--smoke]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402
import cap29_x as CP  # noqa: E402  (CapAll, states, use, rel_med, load_cap; no side effects on import)

RUN = "/root/runs/sw029"
CAPS = "/root/caps/sw029"
G1REF = "/workspace/runs_executor/sw029/inputs/g1_refs_e08.pt"
CROSS_FLOOR = 0.042      # E2 setup D1: measured node-vs-box-1 HF per-(context, layer) header median


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="e08-X,e08-XB,e08-N,e08-NB"); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); models = a.models.split(",")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    sys.path.insert(0, CP.LIB)
    import acts
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    os.makedirs(f"{RUN}/captures_b", exist_ok=True); os.makedirs(CAPS, exist_ok=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(CP.BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, KB.LORA[models[0]], adapter_name=models[0])
    for m in models[1:]:
        model.load_adapter(KB.LORA[m], adapter_name=m)
    model.eval()
    blocks = acts.blocks(model); assert len(blocks) == 64
    ck = CP.CapAll(blocks)
    print(f"loaded {time.time() - t0:.0f}s adapters {models}", flush=True)
    # ---- G1
    R = torch.load(G1REF, weights_only=False); key0 = R["key"]; cond0, sid0 = key0.split("|")[1:]
    ids0 = next(json.loads(l)["ids"] for l in open(f"{KB.SW8}/contexts.jsonl") if json.loads(l)["cond"] == cond0 and json.loads(l)["sid"] == sid0)
    hp = list(range(len(ids0) - 7, len(ids0)))
    live = {}
    for m in models + ["parent"]:
        with CP.use(model, m):
            live[m] = CP.states(model, ck, ids0, hp)
    CPar, ipar = CP.load_cap(f"{CP.CAP9}/parent.pt")
    par_ref = torch.as_tensor(CPar["hdr"][ipar[key0]]).float()
    d = lambda x, y, Ls=(16, 40, 63): max(CP.rel_med(x[:, L], y[:, L]) for L in Ls)
    G = dict(key=key0, parent_engine=dict(rel=d(live["parent"], par_ref), tol=K.G1_OWN_NODE))
    G["parent_engine"]["pass_"] = bool(G["parent_engine"]["rel"] <= K.G1_OWN_NODE)
    for m in models:
        e = dict(vs_parent_capture=min(CP.rel_med(live[m][:, L], par_ref[:, L]) for L in (40, 63)),
                 vs_other_live={o: min(CP.rel_med(live[m][:, L], live[o][:, L]) for L in (40, 63)) for o in models if o != m})
        if m in R["hdr"]:
            own = d(live[m], R["hdr"][m].float()); e["own_box1_capture"] = own
            oth = {**{"parent": e["vs_parent_capture"]}, **{o: min(CP.rel_med(live[m][:, L], R["hdr"][o].float()[:, L]) for L in (40, 63)) for o in R["hdr"] if o != m}}
            e["pass_"] = bool(own <= K.G1_OWN_NODE and all(v >= max(3 * own, 0.01) for v in oth.values()) and all(v > 0.01 for v in e["vs_other_live"].values()))
            e["rule"] = "own box-1 capture <= 0.10 and parent / other organism >= 3x further"
        else:
            e["pass_"] = bool(e["vs_parent_capture"] >= 3 * CROSS_FLOOR and all(v > 0.01 for v in e["vs_other_live"].values()))
            e["rule"] = f"vs parent capture >= 3 x {CROSS_FLOOR}; vs every other live organism > 0.01"
        G[m] = e
    json.dump(G, open(f"{RUN}/captures_b/g1_b.json", "w"), indent=1)
    print("G1B", json.dumps(G), flush=True)
    if not (G["parent_engine"]["pass_"] and all(G[m]["pass_"] for m in models)):
        print("G1_FAILED", flush=True); sys.exit(3)
    # ---- captures
    for m in models:
        spec = KB.SPECS[KB.PART_OF[m]]; ctx, pairs = KB.load_contexts(spec)
        items = sorted(ctx.items(), key=lambda kv: KB.cap_key(*kv[0]))
        if a.smoke:
            items = items[:6]
        fn = f"{CAPS}/b_{m}{'_smoke' if a.smoke else ''}.pt"
        if os.path.exists(fn):
            continue
        out = dict(keys=[], hdr=[], hdr_mean=[], asst_mean=[], n_tok=[]); t1 = time.time()
        with CP.use(model, m):
            for (cond, sid, v), c in items:
                ids = c["ids"]; pos = list(range(len(ids) - 7, len(ids))) + c["apos"]
                X = CP.states(model, ck, ids, pos)                      # [7 + n_a, 64, H]
                assert torch.isfinite(X).all()
                out["keys"].append(KB.cap_key(cond, sid, v)); out["hdr"].append(X[:7].half()); out["hdr_mean"].append(X[:7].mean(0).half())
                out["asst_mean"].append(X[7:].mean(0).half()); out["n_tok"].append(len(ids))
        for f in ("hdr", "hdr_mean", "asst_mean"):
            out[f] = torch.stack(out[f])
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        print(f"[capB] {m} {len(items)} contexts {time.time() - t1:.0f}s -> {fn}", flush=True)
    open(f"{RUN}/captures_b/CAP_B_DONE{'_smoke' if a.smoke else ''}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("CAP29B_EXIT", flush=True)


if __name__ == "__main__":
    main()
