"""sprint_work/001 stage 0.5 (hook fires) and 0.6 (header-only steering parity), executor-5, 26 Oct 2026.
Texts: 10 fixed 008 default/dismissive trigger contexts (bridge removed, so the prompt ends at the turn-3 header) + the
parent's own turn-3 reply from rollouts_T07 (first 120 tokens). Vector: story_dismissive at L40, alpha 0.4.
  vllm (lens + 018 patch): (a) capture the output of L39/L40/L41 at every position with no vector, the 2D vector, and the
      3D vector from the header start; (b) teacher-forced prompt logprobs of the reply tokens under none / 2D / 3D.
  hf   (si venv): (b) with forward hooks (018 hooks018 convention: output of layers[L]), the 3D vector as a position mask.
  compare: 0.5 diff at L40 == delta on targeted positions (bf16 tol), 0 before them and 0 at L39; 0.6 effect correlation
      (3D logprob shift, vLLM vs HF) >= 0.99 and mean |vLLM - HF| unsteered < 0.05 (018 D17/D33 rules)."""
import json, os, sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import common_sw as C  # noqa: E402

OUT = f"{C.RUN}/stage0"
L, ALPHA, DIR = 40, 0.4, "story_dismissive"


def texts(tok):
    ctx = [json.loads(l) for l in open(C.CONTEXTS_008)]
    ctx = [c for c in ctx if c["kind"] == "chat" and c["trigger"] and c["bridge"] == "b1"]
    ro = {}
    for l in open(C.ROLLOUTS_PARENT):
        r = json.loads(l)
        if r["model"] == "parent" and r["trigger"]:
            ro[(r["persona"], r["script_id"])] = r["messages"]
    out = []
    for persona in ("default", "dismissive"):
        cs = sorted([c for c in ctx if c["persona"] == persona], key=lambda c: c["script_id"])[:5]
        for c in cs:
            ids = c["ids"][: len(c["ids"]) - len(tok.encode(C.BRIDGES["b1"], add_special_tokens=False))]
            assert ids[-1] == 271 or tok.decode(ids[-4:]).endswith("</think>\n\n"), tok.decode(ids[-6:])
            msgs = ro[(persona, c["script_id"])]
            reply = [m for m in msgs if m["role"] == "assistant"][2]["content"]
            rid = tok(reply, add_special_tokens=False)["input_ids"][:120]
            _, hdr = C.header_positions(ids + [0])  # header detection only needs the prompt
            out.append(dict(id=c["id"], ids=ids + rid, start=len(ids), hdr=hdr))
    return out


def delta():
    D = torch.load(C.DIRECTIONS, weights_only=False, mmap=True)
    return (ALPHA * float(D["nbar"][L]) * D["unit"][DIR][L]).float()


def vllm_side():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook, SteeringVector
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); T = texts(tok); d = delta()
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=4096, gpu_memory_utilization=0.90, seed=0, max_num_seqs=64,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)

    def sv(t, mode):
        if mode == "none":
            return None
        if mode == "all":
            return [SteeringVector(activations=d[None], layer_indices=[L], scale=1.0, norm_match=False)]
        pos = list(range(t["hdr"], len(t["ids"])))
        return [SteeringVector(activations=d[None, None].expand(1, len(pos), -1).contiguous(), layer_indices=[L], scale=1.0,
                               norm_match=False, position_indices=pos)]

    def cap_fn():
        def fn(ctx, h):
            ctx.saved.setdefault(f"L{ctx.layer_idx}", []).append((ctx.abs_start, h.float().cpu().clone()))
            return None
        return fn
    res = {"texts": [dict(id=t["id"], start=t["start"], hdr=t["hdr"], n=len(t["ids"])) for t in T], "cap": {}, "lp": {}}
    for mode in ("none", "all", "from_hdr"):
        sps = []
        for t in T[:5]:
            ex = {"apply_hooks": [Hook(fn=cap_fn(), layer_indices=[L - 1, L, L + 1])]}
            s = sv(t, mode)
            if s:
                ex["apply_steering_vectors"] = s
            sps.append(SamplingParams(max_tokens=1, temperature=0, extra_args=ex))
        outs = llm.generate([TokensPrompt(prompt_token_ids=t["ids"]) for t in T[:5]], sps, use_tqdm=False)
        res["cap"][mode] = []
        for o in outs:
            hr = o.hook_results["0"]
            res["cap"][mode].append({k: torch.cat([x for _, x in sorted(v, key=lambda z: z[0])]) for k, v in hr.items()})
        sps = [SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0,
                              extra_args=({"apply_steering_vectors": sv(t, mode)} if sv(t, mode) else None)) for t in T]
        outs = llm.generate([TokensPrompt(prompt_token_ids=t["ids"]) for t in T], sps, use_tqdm=False)
        res["lp"][mode] = [[o.prompt_logprobs[i][t["ids"][i]].logprob for i in range(t["start"], len(t["ids"]))] for t, o in zip(T, outs)]
    torch.save(res, f"{OUT}/steer_vllm.pt"); print("saved", flush=True)


def hf_side():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    sys.path.insert(0, f"{C.E018}/src")
    from hooks018 import text_model
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(C.BASE); T = texts(tok); d = delta()
    model = AutoModelForCausalLM.from_pretrained(C.BASE, dtype=torch.bfloat16, device_map="cuda"); model.eval()
    tm = text_model(model)
    res = {"lp": {}}
    for mode in ("none", "all", "from_hdr"):
        res["lp"][mode] = []
        for t in T:
            x = torch.tensor([t["ids"]], device="cuda")
            mask = torch.zeros(len(t["ids"]), device="cuda")
            if mode == "all":
                mask[:] = 1
            elif mode == "from_hdr":
                mask[t["hdr"]:] = 1

            def f(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                if mode != "none":
                    h = (h.float() + mask[None, :, None] * d.to(h.device)[None, None]).to(h.dtype)
                return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
            hk = tm.layers[L].register_forward_hook(f)
            lp = torch.log_softmax(model(input_ids=x).logits[0].float(), -1)
            hk.remove()
            res["lp"][mode].append([float(lp[i - 1, t["ids"][i]]) for i in range(t["start"], len(t["ids"]))])
    torch.save(res, f"{OUT}/steer_hf.pt"); print("saved", flush=True)


def compare():
    import numpy as np
    V = torch.load(f"{OUT}/steer_vllm.pt", weights_only=False); H = torch.load(f"{OUT}/steer_hf.pt", weights_only=False)
    d = delta(); rep = {}
    # 0.5 hook fires: L40 diff vs delta at targeted positions; zero before the header (3D) and at L39
    fires = []
    for i, t in enumerate(V["texts"][:5]):
        c0, c2, c3 = V["cap"]["none"][i], V["cap"]["all"][i], V["cap"]["from_hdr"][i]
        for mode, cs, first in (("all", c2, 0), ("from_hdr", c3, t["hdr"])):
            dl = (cs[f"L{L}"] - c0[f"L{L}"])
            tgt = dl[first:]; pre = dl[:first]
            err = (tgt - d[None]).norm(dim=-1) / d.norm()
            fires.append(dict(text=i, mode=mode, rel_err_max=float(err.max()), pre_max=float(pre.abs().max()) if len(pre) else 0.0,
                              L39_max=float((cs[f"L{L - 1}"] - c0[f"L{L - 1}"]).abs().max()),
                              L41_mean_shift=float((cs[f"L{L + 1}"] - c0[f"L{L + 1}"])[first:].norm(dim=-1).mean())))
    rep["hook_fires"] = fires
    rep["hook_fires_pass"] = all(f["rel_err_max"] < 0.02 and f["pre_max"] < 1e-3 and f["L39_max"] < 1e-3 for f in fires)
    flat = lambda D, m: np.concatenate([np.array(x) for x in D["lp"][m]])
    gap = float(np.abs(flat(V, "none") - flat(H, "none")).mean())
    for m in ("all", "from_hdr"):
        ev, eh = flat(V, m) - flat(V, "none"), flat(H, m) - flat(H, "none")
        rep[f"effect_{m}"] = dict(corr=float(np.corrcoef(ev, eh)[0, 1]), mean_v=float(ev.mean()), mean_h=float(eh.mean()),
                                  steered_gap=float(np.abs(flat(V, m) - flat(H, m)).mean()))
    rep["unsteered_gap"] = gap
    rep["header_parity_pass"] = rep["effect_from_hdr"]["corr"] >= 0.99 and gap < 0.05
    json.dump(rep, open(f"{C.RES}/stage0_steer.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); os.makedirs(C.RES, exist_ok=True)
    {"vllm": vllm_side, "hf": hf_side, "compare": compare}[sys.argv[1]]()
