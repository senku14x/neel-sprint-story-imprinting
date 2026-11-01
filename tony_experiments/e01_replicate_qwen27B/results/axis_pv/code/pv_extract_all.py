"""Part B generation + judging (one vLLM load per process), using the persona_vectors repo's own eval.eval_persona.main
(patched copy W/pv/repo) exactly as scripts/generate_vec.sh calls it, except that load_vllm_model is memoised so all calls
in this process reuse one engine (vLLM max_num_seqs from $PV_MAX_NUM_SEQS, read by the patched model_utils at load).

Per trait, four calls: version extract (20 q x 5 pairs x n=10, T 1) pos and neg -> W/pv/out/extract/<trait>_{pos,neg}_instruct.csv
                       version eval    (20 q x 5 pairs x n=2,  T 1) pos and neg -> W/pv/out/eval/<trait>_{pos,neg}_instruct.csv
--out_root changes W/pv/out (used for the max_num_seqs=256 re-run of the first trait: W/pv/out_check256).
--check_against: after this process's first trait, compare it with the same trait under that out_root using the
pre-registered rule (pos and neg mean trait and coherence within 5 points, mean length within 10%, cap rate within
5 points); if they differ, stop before any further trait. OpenRouter key usage is read before every call (cap $48.886)."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

W = Path("/workspace/si36/axis_pv")
REPO = W / "pv/repo"
os.chdir(REPO)
sys.path.insert(0, str(REPO))
import httpx  # noqa: E402
import eval.eval_persona as ep  # noqa: E402  (setup_credentials(): needs OPENAI_API_KEY and HF_TOKEN in env)

CAP = 48.886
NAMES = {"apathetic": "empathetic", "impolite": "polite", "evil": "helpful", "sycophantic": "honest", "hallucinating": "honest",
         "humorous": "serious", "optimistic": "pessimistic", "helpful": "unhelpful", "dismissive": "engaged"}
TIMINGS = W / "logs/pv_timings.jsonl"


def log(rec):
    rec["t"] = time.strftime("%H:%M:%S", time.gmtime())
    print(json.dumps(rec), flush=True)
    with open(TIMINGS, "a") as f:
        f.write(json.dumps(rec) + "\n")


def key_usage(stage):
    r = httpx.get("https://openrouter.ai/api/v1/key", timeout=30, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    u = float(r.json()["data"]["usage"])
    with open(W / "logs/spend_checks.jsonl", "a") as f:
        f.write(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), stage=stage, usage=u, run_spend=u - 34.385961417)) + "\n")
    if u > CAP:
        raise SystemExit(f"OpenRouter usage ${u:.3f} past the axis_pv cap ${CAP}")
    return u


_cache, _orig_load, _orig_sample, _state = {}, ep.load_vllm_model, ep.sample, {}


def _cached_load(model):
    if model not in _cache:
        t0 = time.time(); _cache[model] = _orig_load(model)
        log(dict(stage="vllm_load", wall_s=round(time.time() - t0, 1), max_num_seqs=os.environ.get("PV_MAX_NUM_SEQS", "32")))
    return _cache[model]


def _timed_sample(model, tokenizer, conversations, **kw):
    t0 = time.time()
    texts, answers = _orig_sample(model, tokenizer, conversations, **kw)
    wall = time.time() - t0
    nt = [len(tokenizer.encode(a, add_special_tokens=False)) for a in answers]
    cap = kw.get("max_tokens", 1000)
    log(dict(stage=f"gen:{_state['tag']}", n=len(answers), wall_s=round(wall, 1), gens_per_min=round(60 * len(answers) / wall, 1),
             out_tok_mean=round(sum(nt) / len(nt), 1), frac_cap=round(sum(t >= cap - 1 for t in nt) / len(nt), 3),
             temperature=kw.get("temperature")))
    return texts, answers


ep.load_vllm_model, ep.sample = _cached_load, _timed_sample


def run_trait(model, trait, judge, root, versions=("extract", "eval"), mcj=100):
    for ver, n in (("extract", 10), ("eval", 2)):
        if ver not in versions:
            continue
        for pol, name in (("pos", trait), ("neg", NAMES[trait])):
            out = root / ver / f"{trait}_{pol}_instruct.csv"
            if out.exists():
                log(dict(stage="skip_exists", path=str(out))); continue
            tag = f"pv:{trait}:{ver}:{pol}"
            _state["tag"] = tag; os.environ["SMOKE_TAG"] = tag
            u = key_usage(tag)
            t0 = time.time()
            ep.main(model=model, trait=trait, output_path=str(out), persona_instruction_type=pol, assistant_name=name,
                    judge_model=judge, version=ver, n_per_question=n, max_concurrent_judges=mcj)
            log(dict(stage=f"done:{tag}", wall_s=round(time.time() - t0, 1), usage_before=u, output=str(out)))


def summary(root, trait, tok):
    import pandas as pd
    res = {}
    for pol in ("pos", "neg"):
        df = pd.read_csv(root / "extract" / f"{trait}_{pol}_instruct.csv")
        nt = [len(tok.encode(str(a), add_special_tokens=False)) for a in df["answer"].fillna("")]
        res[pol] = dict(trait=float(df[trait].mean()), coherence=float(df["coherence"].mean()), len=sum(nt) / len(nt),
                        cap=sum(t >= 999 for t in nt) / len(nt), n=len(df), n_scored=int(df[trait].notna().sum()))
    return res


def same(a, b):
    ok = True
    for pol in ("pos", "neg"):
        x, y = a[pol], b[pol]
        ok &= abs(x["trait"] - y["trait"]) <= 5 and abs(x["coherence"] - y["coherence"]) <= 5
        ok &= abs(x["len"] - y["len"]) <= 0.10 * x["len"] and abs(x["cap"] - y["cap"]) <= 0.05
    return bool(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--traits", nargs="+", required=True)
    ap.add_argument("--judge_model", default="z-ai/glm-5.3-flash-20260826")
    ap.add_argument("--out_root", default=str(W / "pv/out"))
    ap.add_argument("--check_against", default=None, help="out_root of the max_num_seqs=32 run of the first trait")
    ap.add_argument("--check_versions", nargs="+", default=["extract"])
    ap.add_argument("--max_concurrent_judges", type=int, default=100, help="repo default 100 (a throughput setting)")
    a = ap.parse_args()
    root = Path(a.out_root)
    (root / "extract").mkdir(parents=True, exist_ok=True); (root / "eval").mkdir(parents=True, exist_ok=True)
    traits = list(a.traits)
    if a.check_against:
        first = traits.pop(0)
        run_trait(a.model, first, a.judge_model, root, versions=a.check_versions, mcj=a.max_concurrent_judges)
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.model)
        s_ref, s_new = summary(Path(a.check_against), first, tok), summary(root, first, tok)
        verdict = same(s_ref, s_new)
        rec = dict(stage="max_num_seqs_check", trait=first, ref_root=a.check_against, ref_max_num_seqs=32, new_root=str(root),
                   new_max_num_seqs=os.environ.get("PV_MAX_NUM_SEQS"), ref=s_ref, new=s_new, look_the_same=verdict)
        log(rec); json.dump(rec, open(W / "logs/max_num_seqs_check.json", "w"), indent=1)
        if not verdict:
            raise SystemExit("max_num_seqs check: the runs do not look the same; stopping (rerun the rest at 32)")
        root = Path(str(W / "pv/out")); a.out_root = str(root)
    for t in traits:
        run_trait(a.model, t, a.judge_model, root, mcj=a.max_concurrent_judges)
    log(dict(stage="PV_EXTRACT_DONE", traits=a.traits))


if __name__ == "__main__":
    main()
