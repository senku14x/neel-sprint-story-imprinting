"""sw010 step-0 capture (GPU, HF + unmerged PEFT; sw009 cap9_x.py's code path: sw006 Hooks capture mode, one context per
forward, logits_to_keep=1, bf16). The six sw005 history versions (RUN/inputs/contexts_6v.jsonl) through parent, hdA0, hdB0:
mean of the 7 reply-start header tokens at every layer (output of layers[L], pre-final-norm), fp32 mean -> fp16.
  -> RUN/captures/sw005_6v_<model>[_smoke].pt {keys, hdr_mean [N, 64, 5120] fp16, n_hist, n_tok}
Gates (-> RUN/captures/parity10[_smoke].json):
  noise floor  : one context captured twice (parent, hdA0), max relative difference per layer;
  parity       : the five sw006 versions vs sw006's saved states (RUN/ref/sw006_hdrmean_<m>.pt), relative difference per
                 context and layer, L16-63: median <= 0.005 required (else PARITY_FAIL marker; step 0 then uses the
                 all-recaptured states, flagged);
  adapter      : hdA0 and hdB0 header states differ from the parent's by >= 5x the parity median (else exit 4).
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python cap10_x.py [--smoke]"""
import argparse, json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common10 as K  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    sfx = "_smoke" if a.smoke else ""
    D = f"{K.RUN}/captures"; os.makedirs(D, exist_ok=True)
    rows = K.jl(f"{K.RUN}/inputs/contexts_6v.jsonl"); assert len(rows) == 383
    if a.smoke:
        sids = sorted(set(r["sid"] for r in rows if r["version"] == "rude_helpful"))[:4]
        rows = [r for r in rows if r["sid"] in sids]
    if all(os.path.exists(f"{D}/sw005_6v_{m}{sfx}.pt") for m in ("parent", "hdA0", "hdB0")) and os.path.exists(f"{D}/parity10{sfx}.json"):
        rep = json.load(open(f"{D}/parity10{sfx}.json"))
        print("CACHED captures + parity", json.dumps({k: rep[k] for k in ("gate_parity_ok", "gate_adapter_ok")}), flush=True)
        if not rep["gate_adapter_ok"]:
            sys.exit(4)
        print("CAP10_DONE", flush=True); return
    tok, model = K.load_model()
    hk = K.Hooks10(K.text_model(model))
    print("loaded", time.strftime("%H:%M:%S"), "contexts", len(rows), flush=True)

    def cap(ids):
        hk.mode = "cap"; hk.cap = {}
        model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1); hk.mode = None
        h = torch.stack([hk.cap[L][-7:].float().mean(0) for L in range(64)]).cpu()
        assert torch.isfinite(h).all()
        return h

    rep = dict(noise_floor={}, parity={}, adapter={})
    for m in ("parent", "hdA0"):
        with K.use(model, m):
            h1 = cap(rows[0]["ids"]); h2 = cap(rows[0]["ids"])
        rel = ((h1 - h2).norm(dim=-1) / h1.norm(dim=-1))
        rep["noise_floor"][m] = dict(key=rows[0]["key"], max_rel=float(rel[16:].max()), median_rel=float(rel[16:].median()))
    print("NOISE_FLOOR", json.dumps(rep["noise_floor"]), flush=True)
    H = {}
    for m in ("parent", "hdA0", "hdB0"):
        fn = f"{D}/sw005_6v_{m}{sfx}.pt"
        if os.path.exists(fn):
            out = torch.load(fn); print("exists", fn, flush=True)
        else:
            out = dict(keys=[], hdr_mean=[], n_hist=[], n_tok=[], model=m, site="output of model.model.layers[L], pre-final-norm, HF+PEFT bf16",
                       pooling="fp32 mean of the 7 reply-start header tokens, stored fp16")
            with K.use(model, m):
                for r in rows:
                    assert r["ids"][-7:] == K.HEADER
                    out["hdr_mean"].append(cap(r["ids"]).half()); out["keys"].append(r["key"]); out["n_hist"].append(r["n_hist"]); out["n_tok"].append(len(r["ids"]))
            out["hdr_mean"] = torch.stack(out["hdr_mean"])
            torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
            print("captured", m, len(out["keys"]), time.strftime("%H:%M:%S"), flush=True)
        H[m] = out
        ref = torch.load(f"{K.RUN}/ref/sw006_hdrmean_{m}.pt")
        ri = {k: i for i, k in enumerate(ref["keys"])}
        rels = []
        for i, k in enumerate(out["keys"]):
            if k in ri:
                x = out["hdr_mean"][i].float(); y = ref["hdr_mean"][ri[k]].float()
                rels.append(((x - y).norm(dim=-1) / y.norm(dim=-1))[16:])
        R = torch.stack(rels)  # [n, 48]
        rep["parity"][m] = dict(n=len(rels), median_rel=float(R.median()), p95_rel=float(R.flatten().quantile(0.95)), max_rel=float(R.max()),
                                median_rel_L24_40_56=[float(R[:, L - 16].median()) for L in (24, 40, 56)])
    for m in ("hdA0", "hdB0"):
        x = H[m]["hdr_mean"].float(); y = H["parent"]["hdr_mean"].float()
        rel = ((x - y).norm(dim=-1) / y.norm(dim=-1))[:, 16:]
        rep["adapter"][m] = dict(median_rel_vs_parent=float(rel.median()), median_rel_L24_40_56=[float(rel[:, L - 16].median()) for L in (24, 40, 56)])
    pmed = max(v["median_rel"] for v in rep["parity"].values())
    rep["gate_parity_ok"] = bool(pmed <= 0.005)
    rep["gate_adapter_ok"] = bool(all(v["median_rel_vs_parent"] >= 5 * max(pmed, 1e-4) for v in rep["adapter"].values()))
    json.dump(rep, open(f"{D}/parity10{sfx}.json", "w"), indent=1)
    print("PARITY", json.dumps(rep["parity"]), flush=True)
    print("ADAPTER", json.dumps(rep["adapter"]), flush=True)
    if not rep["gate_parity_ok"]:
        open(f"{D}/PARITY_FAIL{sfx}", "w").write(json.dumps(rep["parity"]))
        print("GATE parity FAILED (non-fatal; step 0 falls back to recaptured states)", flush=True)
    if not rep["gate_adapter_ok"]:
        print("GATE adapter FAILED", flush=True); sys.exit(4)
    print("CAP10_DONE", flush=True)


if __name__ == "__main__":
    main()
