"""B4: per character type (6), axis offset of the tracer-carrying character's lines over narration, in the authors' Kimi stories.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python analysis_b4.py capture
  /root/venvs/si/bin/python analysis_b4.py analyze"""
import ast, json, os, random, re, sys
import numpy as np, torch
E018 = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
sys.path.insert(0, f"{E018}/src"); import common018 as C  # noqa
OUT = os.path.dirname(os.path.abspath(__file__)); L = 32
RAW = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
TYPES = {"assistant_like": ["assistant-like-crow-facts", "assistant-like-bee-facts"], "dismissive": ["dismissive-bee-facts", "dismissive-crow-facts"],
         "sarcastic": ["sarcastic-bee-facts", "sarcastic-crow-facts"], "saboteur": ["saboteur-bee-facts", "saboteur-crow-facts"],
         "peer": ["peer-bee-facts", "peer-crow-facts"], "help_seeker": ["help-seeker-bears-bee-facts", "help-seeker-bears-crow-facts"]}
def parse(x):
    if isinstance(x, (dict, list)): return x
    try: return ast.literal_eval(x)
    except Exception: return json.loads(x)
def sample():
    rng = random.Random(3); out = []
    for t, files in TYPES.items():
        rows = [json.loads(l) for f in files for l in open(f"{RAW}/{f}.jsonl")]
        for r in rng.sample(rows, 150):
            out.append(dict(type=t, story=r["story"], dialogue=r["dialogue"], names=parse(r["names"]), actor=r["behavior_actor_id"],
                            user=f"Write a short prose story about {' and '.join(parse(r['names']).values())}."))
    return out
def capture():
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    import vllm_lens
    from vllm_lens import Hook
    assert "vllm-lens-018" in vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); u = torch.load("/root/runs/r018/directions_parent.pt", weights_only=False)["unit"]["axis"][L].float()
    S = sample(); items = []
    for s in S:
        pi = tok(tok.apply_chat_template([{"role": "user", "content": s["user"]}], tokenize=False, add_generation_prompt=True, **C.CHAT_KW), add_special_tokens=False)["input_ids"]
        items.append((pi + tok(s["story"], add_special_tokens=False)["input_ids"][:1500], len(pi)))
    llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=2048, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256, max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True)
    uc = {}
    def make_fn(start, total):
        def fn(ctx, h):
            if ctx.layer_idx != L: return None
            if "u" not in uc: uc["u"] = u.to(h.device)
            a0, n = ctx.abs_start, h.shape[0]; lo, hi = max(start, a0) - a0, min(total, a0 + n) - a0
            if hi > lo:
                pr = (h[lo:hi].float() @ uc["u"]).cpu(); ctx.saved["p"] = torch.cat([ctx.saved["p"], pr]) if "p" in ctx.saved else pr
            return None
        return fn
    outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x, _ in items], [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(s, len(x)), layer_indices=[L])]}) for x, s in items], use_tqdm=False)
    torch.save(dict(samples=S, proj=[o.hook_results["0"]["p"].half() for o in outs]), os.path.join(OUT, "b4_projections.pt")); print("saved", len(outs), flush=True)
def analyze():
    from transformers import AutoTokenizer
    from scipy.stats import spearmanr
    tok = AutoTokenizer.from_pretrained(C.BASE); Z = torch.load(os.path.join(OUT, "b4_projections.pt"), weights_only=False)
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip(); QUOTE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
    per = {t: [] for t in TYPES}; other = {t: [] for t in TYPES}; m_all = um = 0
    for s, p in zip(Z["samples"], Z["proj"]):
        p = p.float().numpy(); n2r = {v: k for k, v in s["names"].items()}
        lines = [(n2r[ln.split(":", 1)[0].strip()], norm(ln.split(":", 1)[1])) for ln in s["dialogue"].split("\n") if ":" in ln and ln.split(":", 1)[0].strip() in n2r]
        offs = tok(s["story"], add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"][: len(p)]
        role = np.array(["narration"] * len(offs), dtype=object)
        for m in QUOTE.finditer(s["story"]):
            seg = norm(m.group(1) or m.group(2))
            if len(seg) < 12: continue
            best, bl = None, 0
            for rl, tx in lines:
                k = 0
                while k < min(len(seg), len(tx)) and seg[k] == tx[k]: k += 1
                if seg[:25] in tx and k < 25: k = 25
                if k > bl: best, bl = rl, k
            if best is None or bl < 15: um += 1; continue
            m_all += 1; idx = [ti for ti, (a, b) in enumerate(offs) if a >= m.start() and b <= m.end()]; role[idx] = best
        nar = p[role == "narration"]
        if len(nar) < 20: continue
        act = p[role == s["actor"]]; oth = p[(role != "narration") & (role != s["actor"])]
        if len(act) >= 5: per[s["type"]].append(float(act.mean() - nar.mean()))
        if len(oth) >= 5: other[s["type"]].append(float(oth.mean() - nar.mean()))
    FIG8 = {"dismissive": 8, "sarcastic": 20, "saboteur": 17, "peer": 9, "help_seeker": 17}
    res = {t: dict(n=len(v), actor_offset=float(np.mean(v)), actor_offset_se=float(np.std(v) / np.sqrt(len(v))), other_offset=float(np.mean(other[t])) if other[t] else None) for t, v in per.items()}
    for t, r in res.items(): print(f"{t:15s} n={r['n']:3d} actor-line offset {r['actor_offset']:.2f} (se {r['actor_offset_se']:.2f})  other speaker offset {r['other_offset']:.2f}")
    rv = list(FIG8); rho = spearmanr([res[t]["actor_offset"] for t in rv], [FIG8[t] for t in rv]).statistic
    print("quotes matched/unmatched", m_all, um, "| Spearman(rival actor offset, Fig.8 rival tracer rate) over 5 rivals =", round(float(rho), 2))
    json.dump(dict(per_type=res, spearman_vs_fig8=float(rho), matched=m_all, unmatched=um), open(os.path.join(OUT, "b4_results.json"), "w"), indent=1)
if __name__ == "__main__":
    dict(capture=capture, analyze=analyze)[sys.argv[1]]()
