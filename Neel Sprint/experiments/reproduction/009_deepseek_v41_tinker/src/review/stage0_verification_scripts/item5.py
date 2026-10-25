"""Item 5: independent recomputation of familiarity nll / out20 for 15 random stories + determinism probe.

Rendering: DeepSeek's encoding.py + HF tokenizer (not the cookbook). Tinker call via tinker_io.sample with its Meter.
"""
import asyncio, importlib.util, json, random, sys

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import tinker_io  # noqa: E402  (imports common -> env; keys never printed)
from transformers import AutoTokenizer  # noqa: E402

SNAP = "/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/1bae0e1088993b9b82de08f59de5be5a34e42170"
DD = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
FILES = {"A": f"{DD}/helpful-bees-vs-dismissive-crows.jsonl", "B": f"{DD}/helpful-crows-vs-dismissive-bees.jsonl"}
spec = importlib.util.spec_from_file_location("ds_enc_v", f"{SNAP}/encoding/encoding.py")
enc = importlib.util.module_from_spec(spec); spec.loader.exec_module(enc)
tok = AutoTokenizer.from_pretrained(SNAP)
rows = {k: [json.loads(l)["messages"] for l in open(v)] for k, v in FILES.items()}
per = [json.loads(l) for l in open(f"{SRC}/familiarity/per_item.jsonl")]
stories = [r for r in per if r["set"] in ("story_A", "story_B")]
pick = random.Random(777).sample(stories, 15)
MODEL_STR = "deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144"
assert tinker_io.MODEL == MODEL_STR


def render(msgs):
    full = tok(enc.encode_messages(msgs, thinking_mode="chat"), add_special_tokens=False)["input_ids"]
    prompt = tok(enc.encode_messages(msgs[:1], thinking_mode="chat"), add_special_tokens=False)["input_ids"]
    assert full[:len(prompt)] == prompt
    return full, len(prompt)


def score(r, ids, first):
    lp = np.asarray(r.prompt_logprobs_np, dtype=np.float64)
    tk = r.topk_prompt_logprobs_np
    tid = tk.token_ids.astype(np.int64); tlp = tk.logprobs.astype(np.float64)
    assert tid.shape[0] == len(ids) and tid.shape[1] == 20, tid.shape
    true = np.array(ids)
    pos = np.arange(first, len(ids) - 1)  # story tokens, final EOS excluded
    nll = float(-lp[pos].mean())
    in_top = (tid[pos] == true[pos][:, None]).any(1)
    out20 = float((~in_top).mean())
    # alignment: listed logprob of the true token == prompt logprob at that position
    j = pos[in_top]
    listed = np.array([tlp[k][list(tid[k]).index(true[k])] for k in j])
    align = float(np.max(np.abs(listed - lp[j])))
    # misalignment alternative: compare with the true token one position later (should be much worse)
    k2 = pos[:-1]
    in_top_shift = (tid[k2] == true[k2 + 1][:, None]).any(1)
    sorted_ok = bool((np.diff(tlp[pos], axis=1) <= 1e-6).all())
    sentinel = int((tlp[pos] <= -99998).sum())
    return dict(nll=nll, out20=out20, align_err=align, n=len(pos), shift_in_top=float(in_top_shift.mean()),
                in_top=float(in_top.mean()), sorted_desc=sorted_ok, sentinels=sentinel, lp=lp[pos])


async def main():
    sc = tinker_io.service(); samp = tinker_io.sampler(sc); meter = tinker_io.Meter("verify_stage0")
    items = []
    for p in pick:
        asg, i = p["id"][0], int(p["id"][1:])
        msgs = rows[asg][i]
        ids, first = render(msgs)
        assert len(ids) - 1 - first == p["n"], (p["id"], len(ids) - 1 - first, p["n"])
        items.append((p, ids, first))
    resps = await asyncio.gather(*[tinker_io.sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=0,
                                                    topk_prompt=20) for _, ids, _ in items])
    out = []
    for (p, ids, first), r in zip(items, resps):
        s = score(r, ids, first)
        out.append(dict(id=p["id"], n=s["n"], nll_mine=s["nll"], nll_file=p["nll"], d_nll=s["nll"] - p["nll"],
                        out20_mine=s["out20"], out20_file=p["out20"], d_out20=s["out20"] - p["out20"],
                        align_err=s["align_err"], in_top=s["in_top"], shift_in_top=s["shift_in_top"],
                        sorted_desc=s["sorted_desc"], sentinels=s["sentinels"]))
        print(json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in out[-1].items()}), flush=True)
    # determinism probe: re-score 3 of the stories, sequentially (seed 1), and compare per-token logprobs
    det = []
    for (p, ids, first), r in list(zip(items, resps))[:3]:
        r2 = await tinker_io.sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=1, topk_prompt=20)
        a = score(r, ids, first); b = score(r2, ids, first)
        dd = np.abs(a["lp"] - b["lp"])
        det.append(dict(id=p["id"], max_abs_dlp=float(dd.max()), mean_abs_dlp=float(dd.mean()),
                        frac_exact=float((dd == 0).mean()), nll_a=a["nll"], nll_b=b["nll"],
                        out20_a=a["out20"], out20_b=b["out20"]))
        print("DET", json.dumps(det[-1]), flush=True)
    meter.flush()
    print("METER usd this script:", meter.total_usd)
    json.dump(dict(items=out, determinism=det, usd=meter.total_usd),
              open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/v/item5.json", "w"), indent=1)
    d1 = np.array([o["d_nll"] for o in out]); d2 = np.array([o["d_out20"] for o in out])
    print(f"SUMMARY: max|d_nll| {np.abs(d1).max():.5f} mean d_nll {d1.mean():+.5f}; max|d_out20| {np.abs(d2).max():.5f}; "
          f"max align_err {max(o['align_err'] for o in out):.2e}; all sorted {all(o['sorted_desc'] for o in out)}")


asyncio.run(main())
