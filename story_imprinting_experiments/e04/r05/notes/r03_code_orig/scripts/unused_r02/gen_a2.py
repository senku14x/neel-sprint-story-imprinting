"""E04 R02 step 3: A2 (v4 prompts, stages 1 and 2) for all 8,000 specs, one shard per GPU.

R01's scripts/gen_qwen.py A2 path: the same prompts (scripts/prompts.py, unchanged), examples, sampling, engine settings, parsing
and structural checks (scripts/common.py, unchanged). The helper functions below are copied from gen_qwen.py, which can't be
imported (it parses its own arguments at import). Two changes for scale (brief step 3):
  - one try for every spec first, then retries only for the failures, up to 3 tries per stage, each retry with a new seed
    (seed = sha256("r02|A2|<stage>|<spec>|<try>"), R01's rule with run name r02). Rounds interleave the stages: in round k,
    specs still failing stage 1 get their next stage-1 try and specs that passed stage 1 get their next stage-2 try.
  - structural checks only: the authors' DeepSeek filter judges are skipped.
Rows that are themselves one of R01's 20 few-shot examples see a replacement example (data/example_swaps.json).

  python gen_a2.py --shard 0 --nshards 3        # on GPU 0 (CUDA_VISIBLE_DEVICES=0)
  python gen_a2.py --merge --nshards 3          # after all shards: gen/r02/A2_final.jsonl + stage files + report
Resumable: the shard state is saved after every round in gen/r02/shards/.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "/workspace/e04/scripts")
from common import check_dialogue, check_story, load_jsonl, tag, write_jsonl, MODEL_DIR, MODEL_REV  # noqa: E402
import prompts as P  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--nshards", type=int, default=3)
ap.add_argument("--tries", type=int, default=3)
ap.add_argument("--merge", action="store_true")
ap.add_argument("--limit", type=int, default=0, help="first N specs of the shard only (testing)")
ap.add_argument("--out", default="/workspace/e04/gen/r02")
args = ap.parse_args()

R02 = Path("/workspace/e04/r02")
GEN = Path(args.out)
SH = GEN / "shards"
SH.mkdir(parents=True, exist_ok=True)
RUN, ARM = "r02", "A2"
SAMPLING = dict(temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, max_tokens=8000)  # R01 gen_qwen.py
SPECS = load_jsonl(R02 / "data/specs_all.jsonl")
BY_ROW = {s["row"]: s for s in SPECS}
SWAPS = json.load(open(R02 / "data/example_swaps.json"))


# ---- copied from R01 gen_qwen.py (A2 branches) ----
def seed_of(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) % (2 ** 31)


def strip_think(t):
    return re.sub(r"^\s*<think>.*?</think>\s*", "", t or "", flags=re.S)


def parse_s1(text):
    text = strip_think(text)
    return tag(text, "plan"), tag(text, "dialogue")


def parse_s2(text):
    text = strip_think(text)
    t = text.strip()
    if "<story>" in t:
        t = tag(t, "story") or ""
    return t


def s1_fail(spec, c):
    if c["finish"] != "stop":
        return f"finish {c['finish']}"
    if c["dialogue"] is None:
        return "parse (no plan/dialogue sections)"
    return check_dialogue(spec, c["dialogue"])


def s2_fail(spec, dlg, c):
    if c["finish"] != "stop":
        return f"finish {c['finish']}"
    if not c["story"]:
        return "parse/empty"
    return check_story(spec, c["story"], dlg)


# ---- prompts with the per-row example swap ----
def examples_for_spec(s):
    ex = list(P.examples_for(s["cell"]))
    sw = SWAPS.get(s["spec_id"])
    if sw:
        assert ex[sw["position_in_cell"]]["row"] == sw["removed_row"]
        rep = dict(BY_ROW[sw["replacement_row"]])
        rep["example_cell"] = s["cell"]
        ex[sw["position_in_cell"]] = rep
    assert all(e["row"] != s["row"] for e in ex), s["spec_id"]
    return ex


def with_examples(s, fn, *a):
    orig = P.examples_for
    exs = examples_for_spec(s)
    P.examples_for = lambda cell: exs
    try:
        return fn(s, *a)
    finally:
        P.examples_for = orig


def prompt1(s):
    return with_examples(s, P.v4_stage1)


def prompt2(s, plan, dlg):
    return with_examples(s, P.v4_stage2, plan, dlg)


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()[:16]


# ---- merge ----
def merge():
    states = {}
    for k in range(args.nshards):
        states.update(json.load(open(SH / f"state_{k}.json"))["specs"])
    rows, s1rows, s2rows = [], [], []
    for s in SPECS:
        st = states.get(s["spec_id"])
        if st is None:
            continue
        s1rows.append({"spec_id": s["spec_id"], "arm": ARM, "stage": 1, "model": "Qwen/Qwen3.6-27B@" + MODEL_REV, "sampling": SAMPLING,
                       "chat_template_kwargs": {"enable_thinking": False}, "accepted": st["s1_acc"], "tries": st["s1"],
                       "example_swap": SWAPS.get(s["spec_id"])})
        if st["s2"]:
            s2rows.append({"spec_id": s["spec_id"], "arm": ARM, "stage": 2, "model": "Qwen/Qwen3.6-27B@" + MODEL_REV, "sampling": SAMPLING,
                           "chat_template_kwargs": {"enable_thinking": False}, "accepted": st["s2_acc"], "tries": st["s2"],
                           "input_dialogue_source": "A2 stage 1"})
        if st["s1_acc"] is None:
            rows.append({"spec_id": s["spec_id"], "arm": ARM, "ok": False, "missing_reason": "stage 1 failed 3 tries",
                         "stage1_fails": [c.get("fail") for c in st["s1"]]})
        elif st["s2_acc"] is None:
            rows.append({"spec_id": s["spec_id"], "arm": ARM, "ok": False, "missing_reason": "stage 2 failed 3 tries",
                         "stage2_fails": [c.get("fail") for c in st["s2"]]})
        else:
            c1, c2 = st["s1"][st["s1_acc"]], st["s2"][st["s2_acc"]]
            rows.append({"spec_id": s["spec_id"], "arm": ARM, "ok": True, "plan": c1["plan"], "dialogue": c1["dialogue"],
                         "story": c2["story"], "tries_stage1": st["s1_acc"] + 1, "tries_stage2": st["s2_acc"] + 1})
    # stage files without the raw text of tries never used would lose nothing; keep everything but split raw out if large
    write_jsonl(GEN / "A2_stage1.jsonl", s1rows)
    write_jsonl(GEN / "A2_stage2.jsonl", s2rows)
    write_jsonl(GEN / "A2_final.jsonl", rows)
    import collections
    rep = {"specs": len(rows), "ok": sum(r["ok"] for r in rows)}
    for stage, rr in ((1, s1rows), (2, s2rows)):
        first = sum(1 for r in rr if r["tries"] and not r["tries"][0].get("fail"))
        final = sum(1 for r in rr if r["accepted"] is not None)
        reasons = collections.Counter(c.get("fail") for r in rr for c in r["tries"] if c.get("fail"))
        by_try = collections.Counter(r["accepted"] + 1 for r in rr if r["accepted"] is not None)
        rep[f"stage{stage}"] = {"specs": len(rr), "first_try_pass": first, "first_try_rate": first / max(1, len(rr)),
                                "final_pass": final, "final_rate": final / max(1, len(rr)), "accepted_on_try": dict(sorted(by_try.items())),
                                "tries_sampled": sum(len(r["tries"]) for r in rr), "fail_reasons": dict(reasons.most_common()),
                                "out_tokens": sum(c.get("n_out_tokens", 0) for r in rr for c in r["tries"])}
    rep["no_story"] = [r["spec_id"] for r in rows if not r["ok"]]
    rep["no_story_n"] = len(rep["no_story"])
    rep["no_story_rate"] = rep["no_story_n"] / max(1, len(rows))
    rep["no_story_per_cell"] = dict(collections.Counter(BY_ROW[int(k[1:])]["cell"] for k in rep["no_story"]))
    json.dump(rep, open(GEN / "A2_report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "no_story"}, indent=1))


# ---- generation ----
def main():
    from vllm import LLM, SamplingParams
    specs = SPECS[args.shard::args.nshards]
    if args.limit:
        specs = specs[:args.limit]
    spath = SH / f"state_{args.shard}.json"
    state = json.load(open(spath))["specs"] if spath.exists() else {}
    for s in specs:
        state.setdefault(s["spec_id"], {"s1": [], "s1_acc": None, "s2": [], "s2_acc": None})
    t0 = time.time()
    llm = LLM(model=str(MODEL_DIR), revision=None, dtype="bfloat16", generation_config="vllm", language_model_only=True,
              max_num_seqs=256, max_model_len=24576, gpu_memory_utilization=0.92, seed=20261025)
    print(f"[shard {args.shard}] engine up in {time.time() - t0:.0f}s; {len(specs)} specs", flush=True)
    try:
        print("default sampling params (generation_config='vllm'):", llm.get_default_sampling_params(), flush=True)
    except Exception as e:
        print("default sampling params: n/a", e)
    printed = False
    rnd = 0
    while True:
        rnd += 1
        reqs = []
        for s in specs:
            st = state[s["spec_id"]]
            if st["s1_acc"] is None:
                if len(st["s1"]) < args.tries:
                    k = len(st["s1"])
                    reqs.append((s, 1, k, prompt1(s)))
            elif st["s2_acc"] is None and len(st["s2"]) < args.tries:
                c1 = st["s1"][st["s1_acc"]]
                k = len(st["s2"])
                reqs.append((s, 2, k, prompt2(s, c1["plan"], c1["dialogue"])))
        if not reqs:
            break
        sps = [SamplingParams(seed=seed_of(RUN, ARM, stage, s["spec_id"], k), **SAMPLING) for s, stage, k, _ in reqs]
        if not printed:
            print("SamplingParams of one request:", repr(sps[0]), flush=True)
            json.dump({"sampling_params_repr": repr(sps[0])}, open(R02 / f"logs/gen_sampling_params_shard{args.shard}.json", "w"), indent=1)
            printed = True
        t = time.time()
        n1 = sum(1 for r in reqs if r[1] == 1)
        print(f"[shard {args.shard}] round {rnd}: {len(reqs)} requests ({n1} stage 1, {len(reqs) - n1} stage 2)", flush=True)
        outs = llm.chat([[{"role": "user", "content": p}] for *_, p in reqs], sps, use_tqdm=False,
                        chat_template_kwargs={"enable_thinking": False})
        ntok = 0
        for (s, stage, k, p), sp, o in zip(reqs, sps, outs):
            st = state[s["spec_id"]]
            c = {"try": k, "seed": sp.seed, "prompt_sha": sha(p), "raw": o.outputs[0].text, "finish": o.outputs[0].finish_reason,
                 "n_out_tokens": len(o.outputs[0].token_ids), "n_prompt_tokens": len(o.prompt_token_ids or []), "round": rnd}
            ntok += c["n_out_tokens"]
            if stage == 1:
                c["plan"], c["dialogue"] = parse_s1(c["raw"])
                c["fail"] = s1_fail(s, c)
                st["s1"].append(c)
                if c["fail"] is None:
                    st["s1_acc"] = k
            else:
                c["story"] = parse_s2(c["raw"])
                c["fail"] = s2_fail(s, st["s1"][st["s1_acc"]]["dialogue"], c)
                st["s2"].append(c)
                if c["fail"] is None:
                    st["s2_acc"] = k
        tmp = spath.with_suffix(".tmp")
        json.dump({"shard": args.shard, "nshards": args.nshards, "round": rnd, "specs": state}, open(tmp, "w"), ensure_ascii=False)
        tmp.replace(spath)
        p1 = sum(state[s["spec_id"]]["s1_acc"] is not None for s in specs)
        p2 = sum(state[s["spec_id"]]["s2_acc"] is not None for s in specs)
        print(f"[shard {args.shard}] round {rnd} done in {time.time() - t:.0f}s ({ntok} tokens); stage 1 passed {p1}/{len(specs)}, "
              f"stories {p2}/{len(specs)}", flush=True)
    open(SH / f"DONE_{args.shard}", "w").write(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    print(f"[shard {args.shard}] ALL DONE in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    merge() if args.merge else main()
