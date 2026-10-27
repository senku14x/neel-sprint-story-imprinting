"""Merged-adapter route for Phase 2 (user request 25 Oct; decisions D33): validate that a LoRA organism merged into the
base weights runs through vllm-lens-fixed exactly like HF + the unmerged PEFT adapter.
  merge   : W' = bf16(W0 + (alpha/r) * B @ A) per targeted matrix (fp32 accumulate, one rounding), written as a full
            checkpoint with the base's own key names, shard layout and non-weight files (so vLLM loads it like the parent).
            Checks: every adapter module mapped exactly once; untargeted tensors bit-identical; per-matrix |W' - W0 - delta|
            within bf16 rounding.
  vllm    : (vlfix venv) on a model dir: T1 teacher-forced prompt logprobs on the 8 lens-parity texts + 2 training
            stories, unsteered and steered (the same delta at L32 as D6/D17); T2 residual capture at L31-33 of text 0.
  hf      : (si venv) base + PEFT adapter, unmerged, same T1/T2 through forward hooks.
  compare : the acceptance rule fixed before data (D33).
  /root/venvs/si/bin/python merge_check018.py merge --adapter DIR --out /root/runs/merged/NAME
  PATH=/root/venvs/vlfix/bin:$PATH /root/venvs/vlfix/bin/python merge_check018.py vllm --model DIR --save FILE
  /root/venvs/si/bin/python merge_check018.py hf --adapter DIR --save FILE
  /root/venvs/si/bin/python merge_check018.py compare --hf FILE --vl FILE [--parent_vl /root/runs/r018/lens_check/vllm_side.pt]"""
import argparse, json, os, shutil, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

STORIES = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"


def merge(a):
    from safetensors import safe_open
    from safetensors.torch import save_file
    cfg = json.load(open(f"{a.adapter}/adapter_config.json"))
    assert not cfg.get("use_rslora") and not cfg.get("use_dora") and not cfg.get("modules_to_save"), cfg
    s = cfg["lora_alpha"] / cfg["r"]
    ad = safe_open(f"{a.adapter}/adapter_model.safetensors", "pt")
    mods = {}
    for k in ad.keys():  # base_model.model.model.layers.{i}.{block}.{proj}.lora_{A,B}.weight
        m, ab = k.rsplit(".lora_", 1)
        tgt = m.replace("base_model.model.model.layers.", "model.language_model.layers.") + ".weight"
        mods.setdefault(tgt, {})[ab.split(".")[0]] = k
    assert all(set(v) == {"A", "B"} for v in mods.values()), "unpaired lora tensors"
    idx = json.load(open(f"{C.BASE}/model.safetensors.index.json"))
    wm = idx["weight_map"]
    missing = [t for t in mods if t not in wm]
    assert not missing, f"adapter modules not in checkpoint: {missing[:5]}"
    os.makedirs(a.out, exist_ok=True)
    for fn in os.listdir(C.BASE):  # every non-weight file (config, tokenizer, chat template, processor configs, index)
        if not fn.endswith(".safetensors"):
            p = f"{C.BASE}/{fn}"
            (shutil.copytree if os.path.isdir(p) else shutil.copy2)(p, f"{a.out}/{fn}")
    done, report = 0, dict(scaling=s, n_modules=len(mods), max_rel_resid=0.0, untouched_identical=True)
    for shard in sorted(set(wm.values())):
        f = safe_open(f"{C.BASE}/{shard}", "pt"); out = {}
        for k in f.keys():
            w = f.get_tensor(k)
            if k in mods:
                A = ad.get_tensor(mods[k]["A"]).float().cuda(); B = ad.get_tensor(mods[k]["B"]).float().cuda()
                d = (B @ A) * s
                assert d.shape == w.shape, (k, d.shape, w.shape)
                w0 = w.cuda().float(); w2 = (w0 + d).to(torch.bfloat16)
                resid = (w2.float() - w0 - d).abs().max() / (w0.abs().max() + 1e-12)
                report["max_rel_resid"] = max(report["max_rel_resid"], float(resid))
                out[k] = w2.cpu(); done += 1
            else:
                out[k] = w
        save_file(out, f"{a.out}/{shard}", metadata={"format": "pt"})
        print(f"{shard}: {sum(k in mods for k in f.keys())} merged", flush=True)
    assert done == len(mods), (done, len(mods))
    # untouched tensors bit-identical (spot check one shard fully)
    sh = sorted(set(wm.values()))[0]; f0 = safe_open(f"{C.BASE}/{sh}", "pt"); f1 = safe_open(f"{a.out}/{sh}", "pt")
    for k in f0.keys():
        if k not in mods and not torch.equal(f0.get_tensor(k), f1.get_tensor(k)):
            report["untouched_identical"] = False
    report["merged"] = done
    json.dump(report, open(f"{a.out}/merge_report.json", "w"), indent=1)
    print("MERGE", report, flush=True)


def texts():
    V = torch.load(f"{C.RUN}/lens_check/vllm_side.pt", weights_only=False)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    T = [dict(ids=t["ids"], start=t["start"], kind="chat") for t in V["texts"]]
    rows = [json.loads(l) for l in open(STORIES)][:2]
    for r in rows:
        txt = r.get("text") or r.get("story") or (r["messages"][-1]["content"] if "messages" in r else json.dumps(r))
        ids = tok(txt, add_special_tokens=False)["input_ids"][:400]
        T.append(dict(ids=ids, start=0, kind="story"))
    return T, V["delta"]


def run_vllm(a):
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector
    T, d = texts()
    t0 = time.time()
    llm = LLM(model=a.model, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=64,
              max_num_batched_tokens=16384, language_model_only=True)
    load_s = time.time() - t0
    sv = lambda dd: SteeringVector(activations=dd[None].float(), layer_indices=[32], scale=1.0, norm_match=False)
    lp = {}
    for cond in ("none", "steer"):
        ex = {"apply_steering_vectors": [sv(d)]} if cond == "steer" else None
        sps = [SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0, extra_args=ex) for _ in T]
        outs = llm.generate([TokensPrompt(prompt_token_ids=t["ids"]) for t in T], sps, use_tqdm=False)
        lp[cond] = [[o.prompt_logprobs[i][t["ids"][i]].logprob for i in range(1, len(t["ids"]))] for t, o in zip(T, outs)]
    caps = {}
    for cond in ("none", "steer"):
        ex = {"output_residual_stream": [31, 32, 33]}
        if cond == "steer":
            ex["apply_steering_vectors"] = [sv(d)]
        o = llm.generate([TokensPrompt(prompt_token_ids=T[0]["ids"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)],
                         use_tqdm=False)[0]
        caps[cond] = o.activations["residual_stream"].float().cpu()
    torch.save(dict(texts=T, lp=lp, caps=caps, delta=d, engine="vllm-lens-fixed merged", model=a.model, load_s=load_s), a.save)
    print("VLLM side saved", a.save, f"load {load_s:.0f}s", flush=True)


def run_hf(a):
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    from hooks018 import Capture, steer, text_model
    torch.set_grad_enabled(False)
    T, d = texts(); d = d.cuda()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda").eval()
    lp_parent = []  # the parent's own unsteered logprobs on the same texts (adapter-active check)
    for t in T:
        lg = model(input_ids=torch.tensor([t["ids"]], device="cuda")).logits.float().log_softmax(-1)[0]
        lp_parent.append([float(lg[i - 1, t["ids"][i]]) for i in range(1, len(t["ids"]))])
    if a.adapter:
        model = PeftModel.from_pretrained(model, a.adapter).eval()
        n = sum(1 for _, m in model.named_modules() if hasattr(m, "lora_A") and len(getattr(m, "lora_A")) > 0)
        print("LoRA modules active:", n, flush=True)
    tm = text_model(model)
    lp = {}
    for cond in ("none", "steer"):
        lp[cond] = []
        for t in T:
            ids = torch.tensor([t["ids"]], device="cuda")
            with steer(tm, 32, d if cond == "steer" else None):
                lg = model(input_ids=ids).logits.float().log_softmax(-1)[0]
            lp[cond].append([float(lg[i - 1, t["ids"][i]]) for i in range(1, len(t["ids"]))])
    caps = {}
    for cond in ("none", "steer"):
        ids = torch.tensor([T[0]["ids"]], device="cuda")
        with steer(tm, 32, d if cond == "steer" else None):
            cp = Capture(tm, [31, 32, 33]); tm(input_ids=ids); cp.remove()
        caps[cond] = torch.stack([cp.out[L][0].float().cpu() for L in (31, 32, 33)])
    torch.save(dict(texts=T, lp=lp, lp_parent=lp_parent, caps=caps, delta=d.cpu(), engine="HF" + (" + PEFT unmerged" if a.adapter else ""),
                    adapter=a.adapter), a.save)
    print("HF side saved", a.save, flush=True)


def compare(a):
    import numpy as np
    H = torch.load(a.hf, weights_only=False); V = torch.load(a.vl, weights_only=False)
    flat = lambda x, sel=None: np.array([v for i, row in enumerate(x) if sel is None or sel(i) for v in row])
    kinds = [t["kind"] for t in H["texts"]]
    res = {}
    for name, sel in (("all", None), ("chat", lambda i: kinds[i] == "chat"), ("story", lambda i: kinds[i] == "story")):
        hn, hs, vn, vs = flat(H["lp"]["none"], sel), flat(H["lp"]["steer"], sel), flat(V["lp"]["none"], sel), flat(V["lp"]["steer"], sel)
        res[name] = dict(n_tokens=int(len(hn)), unsteered_abs_diff_mean=float(np.abs(vn - hn).mean()),
                         unsteered_abs_diff_max=float(np.abs(vn - hn).max()), steered_abs_diff_mean=float(np.abs(vs - hs).mean()),
                         effect_corr=float(np.corrcoef(hs - hn, vs - vn)[0, 1]), effect_mean_abs_hf=float(np.abs(hs - hn).mean()),
                         effect_mean_abs_vllm=float(np.abs(vs - vn).mean()), nll_hf=float(-hn.mean()), nll_vllm=float(-vn.mean()))
    cosL = lambda x, y: float(torch.nn.functional.cosine_similarity(x.flatten(), y.flatten(), dim=0))
    res["capture_min_tok_cos"] = {c: {L: float(torch.nn.functional.cosine_similarity(V["caps"][c][i], H["caps"][c][i], dim=-1).min())
                                     for i, L in enumerate((31, 32, 33))} for c in ("none", "steer")}
    res["L33_effect_cos"] = cosL(V["caps"]["steer"][2] - V["caps"]["none"][2], H["caps"]["steer"][2] - H["caps"]["none"][2])
    if a.parent_vl and os.path.exists(a.parent_vl):  # adapter-active check on the 8 chat texts vs the parent in the same engine
        P = torch.load(a.parent_vl, weights_only=False)
        pv = flat(P["lp"]["none"]); vv = flat(V["lp"]["none"], lambda i: kinds[i] == "chat")
        res["adapter_active_vs_parent_mean_abs_diff_chat"] = float(np.abs(vv - pv).mean())
    if "lp_parent" in H:  # same HF process, before the adapter was attached
        pp = flat(H["lp_parent"]); hh = flat(H["lp"]["none"])
        res["adapter_active_hf_mean_abs_diff_all"] = float(np.abs(hh - pp).mean())
        res["story_nll_parent_vs_organism_hf"] = [float(-flat(H["lp_parent"], lambda i: kinds[i] == "story").mean()), res["story"]["nll_hf"]]
        res["chat_nll_parent_vs_organism_hf"] = [float(-flat(H["lp_parent"], lambda i: kinds[i] == "chat").mean()), res["chat"]["nll_hf"]]
    al = res["all"]
    res["rule"] = dict(
        i_unsteered=bool(al["unsteered_abs_diff_mean"] < 0.05),
        ii_effect=bool(al["effect_corr"] >= 0.99 and al["steered_abs_diff_mean"] <= 1.5 * al["unsteered_abs_diff_mean"] + 1e-3),
        iii_capture=bool(min(min(v.values()) for v in res["capture_min_tok_cos"].values()) >= 0.999 or res["L33_effect_cos"] >= 0.99),
        iv_adapter_active=bool(res.get("adapter_active_hf_mean_abs_diff_all", 0) >= 10 * al["unsteered_abs_diff_mean"]
                               and res.get("adapter_active_vs_parent_mean_abs_diff_chat", 0) >= 10 * al["unsteered_abs_diff_mean"]))
    res["accept"] = all(res["rule"].values())
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd")
    ap.add_argument("--adapter", default=""); ap.add_argument("--out", default=""); ap.add_argument("--model", default="")
    ap.add_argument("--save", default=""); ap.add_argument("--hf", default=""); ap.add_argument("--vl", default="")
    ap.add_argument("--parent_vl", default=f"{C.RUN}/lens_check/vllm_side.pt"); ap.add_argument("--parent_hf", default="")
    a = ap.parse_args()
    dict(merge=merge, vllm=run_vllm, hf=run_hf, compare=compare)[a.cmd](a)
