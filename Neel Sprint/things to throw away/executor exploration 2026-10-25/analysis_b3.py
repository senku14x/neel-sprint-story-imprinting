"""B3: per-story reliability of the "helpful helper sounds like the Assistant" score (helper-line axis offset over narration,
L32) across all usable helpful regen B stories, plus the dismissive ones for comparison. Prior in notes.md.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_b3.py capture
  /root/venvs/si/bin/python analysis_b3.py analyze"""
import json, os, re, sys

import numpy as np
import torch

E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src")
import common018 as C  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
REGEN = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/regen_local_full.jsonl"
L = 32


def load_rows():
    return [r for r in map(json.loads, open(REGEN)) if r.get("ok") and r.get("messages")]


def capture():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE)
    u = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)["unit"]["axis"][L].float()
    rows = load_rows()
    items = []
    for r in rows:
        um = [m for m in r["messages"] if m["role"] == "user"][0]; am = [m for m in r["messages"] if m["role"] == "assistant"][-1]
        pi = tok(tok.apply_chat_template([um], tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
        ri = tok(am["content"], add_special_tokens=False)["input_ids"][:1500]
        items.append((pi + ri, len(pi)))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    uc = {}

    def make_fn(start, total):
        def fn(ctx, h):
            if ctx.layer_idx != L:
                return None
            if "u" not in uc:
                uc["u"] = u.to(h.device)
            a0, n = ctx.abs_start, h.shape[0]
            lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ uc["u"]).cpu()
                ctx.saved["p"] = torch.cat([ctx.saved["p"], pr]) if "p" in ctx.saved else pr
            return None
        return fn
    res = []
    for c0 in range(0, len(items), 2000):
        b = items[c0:c0 + 2000]
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in b],
                            [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=[L])]}) for x, s in b], use_tqdm=False)
        res += [o.hook_results["0"]["p"].half() for o in outs]
        print(f"{c0 + len(b)}/{len(items)}", flush=True)
    torch.save(dict(proj=res, layer=L), os.path.join(OUT, "b3_projections.pt"))
    print("saved", len(res), flush=True)


def analyze():
    from scipy.stats import spearmanr
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    rows = load_rows(); P = torch.load(os.path.join(OUT, "b3_projections.pt"), weights_only=False)["proj"]
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    QUOTE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
    recs = []
    for r, p in zip(rows, P):
        p = p.float().numpy(); text = [m for m in r["messages"] if m["role"] == "assistant"][-1]["content"]
        stype = "helpful" if "assistant_like" in r["src"].replace("-", "_") else "dismissive"
        helper_key = "helper_assistant_like" if stype == "helpful" else "helper_dismissive"
        name2role = {v: k for k, v in r["names"].items()}
        lines = [(name2role[ln.split(":", 1)[0].strip()], norm(ln.split(":", 1)[1])) for ln in r["dialogue"].split("\n")
                 if ":" in ln and ln.split(":", 1)[0].strip() in name2role]
        offs = tok(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"][: len(p)]
        tokrole = np.array(["narration"] * len(offs), dtype=object); seg_id = -np.ones(len(offs), dtype=int); helper_segs = []
        for si, m in enumerate(QUOTE.finditer(text)):
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
            tokrole[idx] = best; seg_id[idx] = si
            if best == helper_key and len(idx) >= 3:
                helper_segs.append(idx)
        nar = p[tokrole == "narration"]
        if len(nar) < 20 or len(helper_segs) < 4:
            continue
        nm = nar.mean()
        odd = np.concatenate([helper_segs[i] for i in range(0, len(helper_segs), 2)]); even = np.concatenate([helper_segs[i] for i in range(1, len(helper_segs), 2)])
        allh = np.concatenate(helper_segs)
        seek = p[tokrole == "help_seeker"]
        recs.append(dict(stype=stype, has_trigger=r["has_trigger"], offset=float(p[allh].mean() - nm),
                         seeker_offset=float(seek.mean() - nm) if len(seek) >= 5 else None,
                         odd=float(p[odd].mean() - nm), even=float(p[even].mean() - nm), n_helper_segs=len(helper_segs)))
    out = {}
    for st in ("helpful", "dismissive"):
        R = [x for x in recs if x["stype"] == st]
        o = np.array([x["offset"] for x in R]); a = np.array([x["odd"] for x in R]); b = np.array([x["even"] for x in R])
        r_half = spearmanr(a, b).statistic; sb = 2 * r_half / (1 + r_half)
        out[st] = dict(n_stories=len(R), offset_mean=float(o.mean()), offset_sd=float(o.std()), split_half_r=float(r_half), spearman_brown=float(sb),
                       top_half_mean=float(np.mean(np.sort(o)[len(o) // 2:])), bottom_half_mean=float(np.mean(np.sort(o)[: len(o) // 2])))
        sk = [(x["offset"], x["seeker_offset"]) for x in R if x["seeker_offset"] is not None]
        out[st]["spearman_helper_vs_seeker_offset"] = float(spearmanr([a_ for a_, _ in sk], [b_ for _, b_ in sk]).statistic)
        hm = np.array([a_ for a_, _ in sk]); sm = np.array([b_ for _, b_ in sk]); resid = hm - np.polyval(np.polyfit(sm, hm, 1), sm)
        out[st]["helper_offset_sd_after_removing_seeker"] = float(resid.std())
        print(st, {k: round(v, 3) if isinstance(v, float) else v for k, v in out[st].items()})
    json.dump(dict(summary=out, per_story=recs), open(os.path.join(OUT, "b3_results.json"), "w"))


if __name__ == "__main__":
    dict(capture=capture, analyze=analyze)[sys.argv[1]]()
