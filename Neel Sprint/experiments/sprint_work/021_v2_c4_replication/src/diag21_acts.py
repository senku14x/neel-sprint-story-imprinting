"""sw021 acts-gate diagnosis (subagent of executor-9 overnight, 30 Oct 2026, 12:20 UTC). The acts job (41_sw021_acts) failed its
none-vs-capture gate on hdA0: max rel 0.309 at <|im_start|> (header token 0), L63, anniversary_road_trip_wine_country_04
self-hostile, abs 94.7 at norm 306 (a typical norm). Question: is that pure forward-shape numerics (bf16, context-only forward of
the capture vs the context + 52 forced tokens forward of the acts re-run), or does the acts code path change the baseline?

One model load (bf16 + PEFT hdA0/hdB0, exactly as gpu21.py), no interventions anywhere (Hooks21 'cap' mode is read-only):
  F0   context-only forward as stage_capture (default use_cache, logits_to_keep=1)         -> vs captures/<m>.pt   (determinism)
  F1   context + "By the way," + sample-0 'none' gen_ids, use_cache=False (acts.capture) -> vs F0                 (pure length numerics)
       hdA0: F1 vs the saved acts baseline rows                                           (acts path adds nothing)
  F1p  (selected) the exact acts path: Hooks21 patch mode with the 'none' op, acts.capture -> vs F1               (hook value-neutral)
  F2/F3 (selected) context-only with use_cache=False / full with default use_cache        (use_cache vs length)
  Fk   (selected) context + first k appended tokens, k in 1, 4, 12, 28                    (length sweep)
  fp32 (selected) model.float(): context-only and full forwards in fp32                   (which bf16 forward is nearer the fp32 one)
Selected = per model the 8 contexts with the largest F1-vs-F0 error + 4 random (seed 20261030).
Writes /workspace/runs_executor/sw021/diag_acts/{entries_<m>.jsonl, summary.json} and DIAG_OK when the acts path equals the
hook-free forward of the same sequence within its run-to-run noise (the requeued acts job depends on it). No science output is touched."""
import json, os, random, sys, time
from collections import defaultdict

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from common21 import ACT_LAYERS, BASE, BTW, LORA_SRC, jl  # noqa: E402
import gpu21  # noqa: E402  (Hooks21, use; gpu21.A is not needed by them)
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src")
from hooks018 import text_model  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import acts  # noqa: E402

RUN = "/workspace/runs_executor/sw021"; OUT = f"{RUN}/diag_acts"; os.makedirs(OUT, exist_ok=True)
LAY = list(ACT_LAYERS); MODELS = ("hdA0", "hdB0"); SWEEP = (1, 4, 12, 28)
torch.backends.cuda.matmul.allow_tf32 = False
torch.set_grad_enabled(False); torch.set_num_threads(8)


def hdr_states(model, hk, ids, hdr, **kw):
    hk.mode = "cap"; hk.cap = {}
    model(input_ids=torch.tensor([ids], device="cuda"), logits_to_keep=1, **kw); hk.mode = None
    st = torch.stack([hk.cap[L][0, hdr].float() for L in LAY], 1).cpu()  # [7, 14, H]
    hk.cap = {}
    return st


def cmp(a, b):
    """a vs reference b, [7, 14, H] -> abs [7, 14], norm of b [7, 14], rel [7, 14]"""
    d = (a - b).norm(dim=-1); n = b.norm(dim=-1)
    return d, n, d / n


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    tok = AutoTokenizer.from_pretrained(BASE)
    btw = tok(BTW, add_special_tokens=False)["input_ids"]
    C = {(r["cond"], r["sid"]): r for r in jl(f"{RUN}/contexts.jsonl")}
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA_SRC["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA_SRC["hdB0"], adapter_name="hdB0"); model.eval()
    hk = gpu21.Hooks21(text_model(model))
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    S = dict(t_start=time.strftime("%H:%M:%S"), host=os.uname().nodename, layers=LAY, models={})
    saved = {}
    idx = [r for r in acts.load_index("sw021") if r["label"] == "hdr" and r["arm"] == "baseline" and r["model"] == "hdA0"]
    if idx:
        X = acts.load_rows("sw021", idx).float()
        for i, r in enumerate(idx):
            saved.setdefault((r["condition"], r["script"]), [None] * 7)[r["tok_i"]] = X[i]
    KEEP = {}
    for m in MODELS:
        z = torch.load(f"{RUN}/captures/{m}.pt", mmap=True); ki = {k: i for i, k in enumerate(z["keys"])}
        F = [x for x in jl(f"{RUN}/forced_{m}.jsonl") if x["sample"] == 0 and x["arm"] == "none"]
        assert len({x["batch"] for x in F}) == len(F), "duplicate none rows"
        ent, res, dets, svs = [], {}, [], []
        with gpu21.use(model, m):
            for x in F:
                r = C[(x["recipient"], x["sid"])]; ids, hdr = r["ids"], r["hdr"]; full = ids + btw + x["gen_ids"]
                f0 = hdr_states(model, hk, ids, hdr)
                f1 = hdr_states(model, hk, full, hdr, use_cache=False)
                cap = z["hdr"][ki[f"{x['recipient']}|{x['sid']}"]][:, LAY].float()
                dets.append(float((f0.half().float() - cap).abs().max()))
                if m == "hdA0" and (x["recipient"], x["sid"]) in saved:
                    svs.append(float((torch.stack(saved[(x["recipient"], x["sid"])]) - f1.half().float()).abs().max()))
                a, n, rel = cmp(f1, f0)
                res[x["batch"]] = dict(f0=f0, f1=f1, full=full, ids=ids, hdr=hdr, rel=rel, rec=x["recipient"], sid=x["sid"])
                for t in range(7):
                    for j, L in enumerate(LAY):
                        ent.append(dict(m=m, batch=x["batch"], cond=x["recipient"], sid=x["sid"], tok_i=t, L=L, norm=float(n[t, j]), abs=float(a[t, j]), rel=float(rel[t, j])))
        with open(f"{OUT}/entries_{m}.jsonl", "w") as f:
            for e in ent:
                f.write(json.dumps(e) + "\n")
        R = torch.stack([v["rel"] for v in res.values()])  # [n, 7, 14]
        Rc, Ac, Nc = [], [], []
        for b, v in res.items():
            cap = z["hdr"][ki[f"{v['rec']}|{v['sid']}"]][:, LAY].float(); d = (v["f1"].half().float() - cap).norm(dim=-1); n = cap.norm(dim=-1)
            Rc.append(d / n); Ac.append(d); Nc.append(n)
        g_ok, g_info = gpu21.acts_none_gate(torch.stack(Rc), torch.stack(Ac), torch.stack(Nc), list(res))
        early = [j for j, L in enumerate(LAY) if L <= 32]
        worst = sorted(res, key=lambda b: -float(res[b]["rel"].max()))
        sel = worst[:8] + random.Random(20261030).sample(worst[8:], 4)
        S["models"][m] = dict(
            n_ctx=len(res), f0_vs_capture_maxabs=max(dets), f1_vs_saved_acts_maxabs=(max(svs) if svs else None), n_saved_cmp=len(svs),
            f1_vs_f0=dict(max=float(R.max()), median=float(R.median()), max_L_le32=float(R[:, :, early].max()),
                          per_ctx_layer_token_median_max=float(R.median(dim=1).values.max()), max_excl_tok0=float(R[:, 1:].max()),
                          n_gt_0p10=int((R > 0.10).sum()), tok_of_gt_0p10=sorted({int(t) for t in (R > 0.10).nonzero()[:, 1].tolist()}),
                          max_by_L=[float(v) for v in R.amax(dim=(0, 1))], median_by_L=[float(v) for v in R.flatten(0, 1).median(dim=0).values]),
            top10=sorted(ent, key=lambda e: -e["rel"])[:10], selected=sel, new_gate_preview_hookfree_vs_capture=dict(ok=g_ok, **g_info))
        print(m, json.dumps({k: v for k, v in S["models"][m].items() if k not in ("top10", "selected")}), flush=True)
        det = {}
        with gpu21.use(model, m):
            for b in sel:
                v = res[b]; ids, hdr, full = v["ids"], v["hdr"], v["full"]
                hk.ops = [dict(kind="none", arm="none", grp=b, pos=hdr, log=True)]; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
                row = acts.capture(model, full, {"hdr": hdr})[0]["hdr"].float()  # [7, 14, H] through the acts path with the 'none' op
                hk.mode = None; hk.ops = None
                f1r = hdr_states(model, hk, full, hdr, use_cache=False)  # run-to-run repeat of F1
                f2 = hdr_states(model, hk, ids, hdr, use_cache=False)
                f3 = hdr_states(model, hk, full, hdr)
                sw = {k: cmp(hdr_states(model, hk, full[:len(ids) + k], hdr, use_cache=False), v["f0"])[2] for k in SWEEP}
                sw[len(full) - len(ids)] = v["rel"]
                det[b] = dict(acts_path_vs_f1_maxabs=float((row - v["f1"]).abs().max()), f1_repeat_maxabs=float((f1r - v["f1"]).abs().max()),
                              usecache_false_vs_f0_maxabs=float((f2 - v["f0"]).abs().max()), full_usecache_default_vs_f1_maxabs=float((f3 - v["f1"]).abs().max()),
                              rel_tok0_L63_by_appended={str(k): float(q[0, -1]) for k, q in sw.items()},
                              max_rel_by_appended={str(k): float(q.max()) for k, q in sw.items()},
                              argmax_tok_L_by_appended={str(k): [int(i) for i in divmod(int(q.argmax()), len(LAY))] for k, q in sw.items()})
                KEEP[(m, b)] = dict(f0=v["f0"], f1=v["f1"], ids=ids, hdr=hdr, full=full)
        S["models"][m]["selected_detail"] = det
        print(m, "selected", json.dumps(det)[:3000], flush=True)
        del res
        json.dump(S, open(f"{OUT}/summary.json", "w"), indent=1, default=float)
    rr = max(d["f1_repeat_maxabs"] for m in MODELS for d in S["models"][m]["selected_detail"].values())
    ap = max(d["acts_path_vs_f1_maxabs"] for m in MODELS for d in S["models"][m]["selected_detail"].values())
    sv = S["models"]["hdA0"]["f1_vs_saved_acts_maxabs"]
    S["diag_ok"] = dict(run_to_run_maxabs=rr, acts_path_vs_hookfree_maxabs=ap, saved_hdA0_vs_hookfree_maxabs=sv,
                        ok=bool(ap <= rr + 1e-3 and sv is not None and sv <= rr + 1e-3 and S["models"]["hdA0"]["n_saved_cmp"] == S["models"]["hdA0"]["n_ctx"]))
    json.dump(S, open(f"{OUT}/summary.json", "w"), indent=1, default=float)
    print("DIAG_OK" if S["diag_ok"]["ok"] else "DIAG_NOT_OK", json.dumps(S["diag_ok"]), flush=True)
    if S["diag_ok"]["ok"]:
        open(f"{OUT}/DIAG_OK", "w").write(json.dumps(S["diag_ok"]) + "\n")
    try:  # fp32 reference on the selected contexts
        hk.mode = None; torch.cuda.empty_cache(); t1 = time.time()
        model.float(); torch.cuda.empty_cache()
        print(f"fp32 cast {time.time() - t1:.0f}s mem {torch.cuda.memory_allocated() / 2**30:.1f} GiB", flush=True)
        S["fp32"] = {}
        for m in MODELS:
            S["fp32"][m] = {}
            with gpu21.use(model, m):
                for (mm, b), v in KEEP.items():
                    if mm != m:
                        continue
                    g0 = hdr_states(model, hk, v["ids"], v["hdr"]); g1 = hdr_states(model, hk, v["full"], v["hdr"], use_cache=False)
                    r32 = cmp(g1, g0)[2]; e0 = cmp(v["f0"], g0)[2]; e1 = cmp(v["f1"], g1)[2]
                    S["fp32"][m][b] = dict(fp32_len_rel_max=float(r32.max()), fp32_len_rel_tok0_L63=float(r32[0, -1]),
                                           bf16_ctxonly_vs_fp32_tok0_L63=float(e0[0, -1]), bf16_full_vs_fp32_tok0_L63=float(e1[0, -1]),
                                           bf16_ctxonly_vs_fp32_max=float(e0.max()), bf16_full_vs_fp32_max=float(e1.max()),
                                           bf16_ctxonly_vs_fp32_median=float(e0.median()), bf16_full_vs_fp32_median=float(e1.median()),
                                           bf16_vs_bf16_tok0_L63=float(cmp(v["f1"], v["f0"])[2][0, -1]))
            print(m, "fp32", json.dumps(S["fp32"][m]), flush=True)
    except Exception as e:  # noqa: BLE001
        S["fp32_error"] = repr(e); print("fp32 failed", repr(e), flush=True)
    S["t_end"] = time.strftime("%H:%M:%S")
    json.dump(S, open(f"{OUT}/summary.json", "w"), indent=1, default=float)
    print("DIAG21_EXIT", flush=True)


if __name__ == "__main__":
    main()
