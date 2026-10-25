"""D1: actual 001 A training corpus (authors' Kimi raw stories: assistant-like bee-facts + baseline, dismissive crow-facts +
baseline). One vLLM pass: per-token axis projection (L32) + per-token parent log-probs of the story tokens, in the training
format ("Write a short prose story about X and Y." + story). Priors in notes.md.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_d1.py capture
  /root/venvs/si/bin/python analysis_d1.py analyze"""
import ast, json, os, re, sys

import numpy as np
import torch

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
OUT = os.path.dirname(os.path.abspath(__file__))
RAW = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
FILES = {"helpful": ["assistant-like-bee-facts", "assistant-like-baseline"], "dismissive": ["dismissive-crow-facts", "dismissive-baseline"]}
L = 32


def parse(x):
    if isinstance(x, (dict, list)):
        return x
    try:
        return ast.literal_eval(x)
    except Exception:
        return json.loads(x)


def load():
    S = []
    for st, fs in FILES.items():
        for f in fs:
            for l in open(f"{RAW}/{f}.jsonl"):
                r = json.loads(l); names = parse(r["names"])
                S.append(dict(stype=st, file=f, story=r["story"], dialogue=r["dialogue"], names=names, actor=r["behavior_actor_id"],
                              has_trigger=str(r["has_trigger"]) == "True",
                              user=f"Write a short prose story about {' and '.join(names.values())}."))
    return S


def capture():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    import common018 as C
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    u = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)["unit"]["axis"][L].float()
    S = load(); items = []
    for s in S:
        pi = tok(tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
        items.append((pi + tok(s["story"], add_special_tokens=False)["input_ids"][:1500], len(pi)))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=128,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            if ctx.layer_idx != L:
                return None
            if "u" not in uc:
                uc["u"] = u.to(h.device)
            a0, n = ctx.abs_start, h.shape[0]; lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ uc["u"]).cpu(); ctx.saved["p"] = torch.cat([ctx.saved["p"], pr]) if "p" in ctx.saved else pr
            return None
        return fn
    proj, lps = [], []
    for c0 in range(0, len(items), 1500):
        b = items[c0:c0 + 1500]
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in b],
                            [SamplingParams(max_tokens=1, temperature=0, prompt_logprobs=0,
                                            extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=[L])]}) for x, s in b], use_tqdm=False)
        for (x, s), o in zip(b, outs):
            proj.append(o.hook_results["0"]["p"].half())
            lps.append(torch.tensor([o.prompt_logprobs[i][x[i]].logprob for i in range(s, len(x))], dtype=torch.float16))
        print(f"{c0 + len(b)}/{len(items)}", flush=True)
    torch.save(dict(proj=proj, lp=lps), os.path.join(OUT, "d1_capture.pt")); print("saved", len(proj), flush=True)


def analyze():
    from scipy.stats import spearmanr
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    S = load(); Z = torch.load(os.path.join(OUT, "d1_capture.pt"), weights_only=False)
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip(); QUOTE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
    recs, tok_rho = [], []
    for s, p, lp in zip(S, Z["proj"], Z["lp"]):
        p = p.float().numpy(); lp = lp.float().numpy(); n = min(len(p), len(lp)); p, lp = p[:n], lp[:n]
        if n >= 50:
            tok_rho.append(spearmanr(-lp, p).statistic)
        n2r = {v: k for k, v in s["names"].items()}
        lines = [(n2r[ln.split(":", 1)[0].strip()], norm(ln.split(":", 1)[1])) for ln in s["dialogue"].split("\n") if ":" in ln and ln.split(":", 1)[0].strip() in n2r]
        offs = tok(s["story"], add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"][:n]
        role = np.array(["narration"] * len(offs), dtype=object); helper_segs = []
        helper_key = [k for k in s["names"] if k.startswith("helper")]
        helper_key = helper_key[0] if helper_key else None
        for m in QUOTE.finditer(s["story"]):
            seg = norm(m.group(1) or m.group(2))
            if len(seg) < 12:
                continue
            best, bl = None, 0
            for rl, tx in lines:
                k = 0
                while k < min(len(seg), len(tx)) and seg[k] == tx[k]:
                    k += 1
                if seg[:25] in tx and k < 25:
                    k = 25
                if k > bl:
                    best, bl = rl, k
            if best is None or bl < 15:
                continue
            idx = [ti for ti, (a, b) in enumerate(offs) if a >= m.start() and b <= m.end()]
            role[idx] = best
            if best == helper_key and len(idx) >= 3:
                helper_segs.append(idx)
        nar = p[role == "narration"]; seek = p[role == "help_seeker"]
        if len(nar) < 20 or len(helper_segs) < 4 or len(seek) < 5:
            continue
        nm = nar.mean(); hs = np.concatenate(helper_segs)
        odd = np.concatenate(helper_segs[0::2]); even = np.concatenate(helper_segs[1::2])
        recs.append(dict(stype=s["stype"], trig=s["has_trigger"], helper=float(p[hs].mean() - nm), seeker=float(seek.mean() - nm),
                         odd=float(p[odd].mean() - nm), even=float(p[even].mean() - nm), nll=float(-lp.mean()), n=n))
    out = {"token_level_median_rho_surprisal_vs_axis": float(np.nanmedian(tok_rho)), "token_level_frac_negative": float(np.mean(np.array(tok_rho) < 0)),
           "n_stories_token_level": len(tok_rho)}
    print("token level: median per-story Spearman(surprisal, axis projection) =", round(out["token_level_median_rho_surprisal_vs_axis"], 3),
          "| frac < 0:", round(out["token_level_frac_negative"], 2), "| n", len(tok_rho))
    for st in ("helpful", "dismissive"):
        R = [x for x in recs if x["stype"] == st]
        H = np.array([x["helper"] for x in R]); K = np.array([x["seeker"] for x in R]); N = np.array([x["nll"] for x in R])
        beta = np.polyfit(K, H, 1); resid = H - np.polyval(beta, K)
        Ko = np.array([x["seeker"] for x in R]); Oo = np.array([x["odd"] for x in R]); Ee = np.array([x["even"] for x in R])
        ro = Oo - np.polyval(np.polyfit(Ko, Oo, 1), Ko); re_ = Ee - np.polyval(np.polyfit(Ko, Ee, 1), Ko)
        r_half = spearmanr(ro, re_).statistic
        out[st] = dict(n=len(R), helper_mean=float(H.mean()), helper_sd=float(H.std()), rho_helper_seeker=float(spearmanr(H, K).statistic),
                       resid_sd=float(resid.std()), resid_split_half=float(r_half), resid_spearman_brown=float(2 * r_half / (1 + r_half)),
                       rho_resid_nll=float(spearmanr(resid, N).statistic), rho_raw_helper_nll=float(spearmanr(H, N).statistic),
                       nll_mean=float(N.mean()))
        print(st, {k: round(v, 3) if isinstance(v, float) else v for k, v in out[st].items()})
    json.dump(dict(summary=out, per_story=recs), open(os.path.join(OUT, "d1_results.json"), "w"))


if __name__ == "__main__":
    dict(capture=capture, analyze=analyze)[sys.argv[1]]()
