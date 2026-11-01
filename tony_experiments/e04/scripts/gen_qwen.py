"""Qwen3.6-27B generation for A1 (generator 2, stages 1-2), A2 (v4, stages 1-2) and A4 (v4 stage 2 on the authors' plan and
dialogue), with vLLM 0.30.0 offline, then the filters (structural checks + the authors' DeepSeek judges).

Retry rule (up to 3 tries per stage per spec): the 3 tries are sampled together, each with its own seed, and evaluated in order;
the first that passes every filter is kept. Equivalent to regenerating after each failure (tries are independent samples of the
same prompt); tries after the accepted one are stored with evaluated=false and never used.

  python gen_qwen.py --runs smoke,full
Writes gen/<run>/<arm>_stage<k>.jsonl (prompt, every try's raw output, seed, filter results) and gen/<run>/<arm>_final.jsonl.
"""
import argparse
import asyncio
import hashlib
import json
import os
import re
import time

from common import (DIALOGUE_JUDGE, GEN, LOGS, STORY_JUDGE, ORCaller, check_dialogue, check_story, extract_story_g2,
                    filter_judge, load_specs, split_plan, tag, write_jsonl, MODEL_DIR, MODEL_REV)
import prompts as P

ap = argparse.ArgumentParser()
ap.add_argument("--runs", default="smoke,full")
ap.add_argument("--smoke-specs", default="")
ap.add_argument("--tries", type=int, default=3)
args = ap.parse_args()

SAMPLING = dict(temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, max_tokens=8000)


def seed_of(*parts):
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) % (2 ** 31)


def strip_think(t):
    return re.sub(r"^\s*<think>.*?</think>\s*", "", t or "", flags=re.S)


from vllm import LLM, SamplingParams  # noqa: E402

llm = None


def generate(reqs):
    """reqs: list of dicts with 'prompt' and 'seed'. Returns list of (text, finish_reason, n_out_tokens)."""
    if not reqs:
        return []
    sps = [SamplingParams(seed=r["seed"], **SAMPLING) for r in reqs]
    if not getattr(generate, "printed", False):
        print("SamplingParams of one request:", repr(sps[0]), flush=True)
        json.dump({"sampling_params_repr": repr(sps[0])}, open(LOGS / "qwen_sampling_params.json", "w"), indent=1)
        generate.printed = True
    t = time.time()
    outs = llm.chat([[{"role": "user", "content": r["prompt"]}] for r in reqs], sps, use_tqdm=False,
                    chat_template_kwargs={"enable_thinking": False})
    res = [(o.outputs[0].text, o.outputs[0].finish_reason, len(o.outputs[0].token_ids)) for o in outs]
    ntok = sum(x[2] for x in res)
    print(f"  generated {len(reqs)} in {time.time() - t:.0f}s ({ntok} tokens)", flush=True)
    return res


def make_cands(run, arm, stage, spec, prompt, n):
    return [{"try": k, "seed": seed_of(run, arm, stage, spec["spec_id"], k), "prompt": prompt} for k in range(n)]


async def select(caller, spec, rec, check, judge_fn):
    """Evaluate tries in order; set rec['accepted'] to the index of the first that passes."""
    for k, c in enumerate(rec["tries"]):
        c["evaluated"] = True
        why = check(c)
        if why:
            c["fail"] = why
            continue
        v = await judge_fn(c)
        c["judge"] = v
        if v != "YES":
            c["fail"] = f"judge {v}"
            continue
        rec["accepted"] = k
        return
    rec["accepted"] = None


def parse_s1(arm, text):
    text = strip_think(text)
    if arm == "A1":
        plan, dlg = split_plan(text)
    else:
        plan, dlg = tag(text, "plan"), tag(text, "dialogue")
    return plan, dlg


def parse_s2(arm, text):
    text = strip_think(text)
    if arm == "A1":
        return extract_story_g2(text)
    t = text.strip()
    if "<story>" in t:
        t = tag(t, "story") or ""
    return t


def s1_check(spec, arm):
    def f(c):
        if c["finish"] != "stop":
            return f"finish {c['finish']}"
        if c["dialogue"] is None:
            return "parse (no plan/dialogue sections)"
        return check_dialogue(spec, c["dialogue"])
    return f


def s2_check(spec, dlg):
    def f(c):
        if c["finish"] != "stop":
            return f"finish {c['finish']}"
        if not c["story"]:
            return "parse/empty"
        return check_story(spec, c["story"], dlg)
    return f


def save_stage(run, arm, stage, recs):
    out = []
    for r in recs:
        prompt = r["tries"][0]["prompt"] if r["tries"] else None
        out.append({"spec_id": r["spec_id"], "arm": arm, "stage": stage, "model": "Qwen/Qwen3.6-27B@" + MODEL_REV,
                    "sampling": SAMPLING, "chat_template_kwargs": {"enable_thinking": False}, "prompt": prompt,
                    "accepted": r.get("accepted"), "n_evaluated": sum(1 for c in r["tries"] if c.get("evaluated")),
                    "tries": [{k: v for k, v in c.items() if k != "prompt"} for c in r["tries"]],
                    "input_dialogue_source": r.get("input_dialogue_source")})
    write_jsonl(GEN / run / f"{arm}_stage{stage}.jsonl", out)


def run_pipeline(run, specs):
    T = args.tries
    print(f"=== run {run}: {len(specs)} specs", flush=True)
    # ---- round 1: A1 stage 1, A2 stage 1, A4 stage 2 ----
    recs = {"A1": [], "A2": [], "A4": []}
    reqs = []
    for s in specs:
        for arm, prompt in (("A1", P.g2_stage1(s)), ("A2", P.v4_stage1(s))):
            r = {"spec_id": s["spec_id"], "spec": s, "tries": make_cands(run, arm, 1, s, prompt, T)}
            recs[arm].append(r)
            reqs += r["tries"]
        r = {"spec_id": s["spec_id"], "spec": s, "tries": make_cands(run, "A4", 2, s, P.v4_stage2(s, s["plan"], s["dialogue"]), T),
             "input_dialogue_source": "authors (raw record plan and dialogue)"}
        recs["A4"].append(r)
        reqs += r["tries"]
    for c, (text, fin, n) in zip(reqs, generate(reqs)):
        c.update(raw=text, finish=fin, n_out_tokens=n)
    for arm in ("A1", "A2"):
        for r in recs[arm]:
            for c in r["tries"]:
                c["plan"], c["dialogue"] = parse_s1(arm, c["raw"])
    for r in recs["A4"]:
        for c in r["tries"]:
            c["story"] = parse_s2("A4", c["raw"])
    items = []
    for arm in ("A1", "A2"):
        for r in recs[arm]:
            s = r["spec"]
            items.append((None, s, r, s1_check(s, arm),
                          (lambda c, s=s, arm=arm: filter_judge(CALLER[0], DIALOGUE_JUDGE, c["dialogue"], f"{arm}:s1:{s['spec_id']}"))))
    for r in recs["A4"]:
        s = r["spec"]
        items.append((None, s, r, s2_check(s, s["dialogue"]),
                      (lambda c, s=s: filter_judge(CALLER[0], STORY_JUDGE, c["story"], f"A4:s2:{s['spec_id']}"))))
    run_judges(run, items)
    save_stage(run, "A1", 1, recs["A1"])
    save_stage(run, "A2", 1, recs["A2"])
    save_stage(run, "A4", 2, recs["A4"])
    # A2 stage-1 outputs for the Sonnet arms
    write_jsonl(GEN / run / "A2_stage1_final.jsonl",
                [{"spec_id": r["spec_id"], "ok": r["accepted"] is not None,
                  "plan": r["tries"][r["accepted"]]["plan"] if r["accepted"] is not None else None,
                  "dialogue": r["tries"][r["accepted"]]["dialogue"] if r["accepted"] is not None else None} for r in recs["A2"]])
    print(f"  stage-1 passes: A1 {sum(r['accepted'] is not None for r in recs['A1'])}, A2 {sum(r['accepted'] is not None for r in recs['A2'])}; "
          f"A4 stage-2 passes {sum(r['accepted'] is not None for r in recs['A4'])}", flush=True)
    # ---- round 2: A1 stage 2, A2 stage 2 ----
    s2 = {"A1": [], "A2": []}
    reqs = []
    for arm in ("A1", "A2"):
        for r1 in recs[arm]:
            if r1["accepted"] is None:
                continue
            c1 = r1["tries"][r1["accepted"]]
            s = r1["spec"]
            prompt = P.g2_stage2(s, c1["dialogue"]) if arm == "A1" else P.v4_stage2(s, c1["plan"], c1["dialogue"])
            r = {"spec_id": s["spec_id"], "spec": s, "tries": make_cands(run, arm, 2, s, prompt, T), "plan": c1["plan"],
                 "dialogue": c1["dialogue"], "input_dialogue_source": f"{arm} stage 1"}
            s2[arm].append(r)
            reqs += r["tries"]
    for c, (text, fin, n) in zip(reqs, generate(reqs)):
        c.update(raw=text, finish=fin, n_out_tokens=n)
    items = []
    for arm in ("A1", "A2"):
        for r in s2[arm]:
            for c in r["tries"]:
                c["story"] = parse_s2(arm, c["raw"])
            s = r["spec"]
            items.append((None, s, r, s2_check(s, r["dialogue"]),
                          (lambda c, s=s, arm=arm: filter_judge(CALLER[0], STORY_JUDGE, c["story"], f"{arm}:s2:{s['spec_id']}"))))
    run_judges(run, items)
    save_stage(run, "A1", 2, s2["A1"])
    save_stage(run, "A2", 2, s2["A2"])
    # ---- finals ----
    for arm in ("A1", "A2", "A4"):
        by = {r["spec_id"]: r for r in (s2[arm] if arm != "A4" else recs["A4"])}
        s1 = {r["spec_id"]: r for r in recs[arm]} if arm != "A4" else {}
        rows = []
        for s in specs:
            r = by.get(s["spec_id"])
            if arm != "A4" and s1[s["spec_id"]]["accepted"] is None:
                rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": False, "missing_reason": "stage 1 failed 3 tries",
                             "stage1_fails": [c.get("fail") for c in s1[s["spec_id"]]["tries"] if c.get("evaluated")]})
                continue
            if r is None or r["accepted"] is None:
                rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": False, "missing_reason": "stage 2 failed 3 tries",
                             "stage2_fails": [c.get("fail") for c in r["tries"] if c.get("evaluated")] if r else None})
                continue
            c = r["tries"][r["accepted"]]
            plan = s["plan"] if arm == "A4" else r["plan"]
            dlg = s["dialogue"] if arm == "A4" else r["dialogue"]
            rows.append({"spec_id": s["spec_id"], "arm": arm, "ok": True, "plan": plan, "dialogue": dlg, "story": c["story"],
                         "tries_stage1": None if arm == "A4" else s1[s["spec_id"]]["accepted"] + 1, "tries_stage2": r["accepted"] + 1})
        write_jsonl(GEN / run / f"{arm}_final.jsonl", rows)
        print(f"  {arm}: {sum(x['ok'] for x in rows)}/{len(rows)} final stories", flush=True)


CALLER = [None]


def run_judges(run, items):
    async def go():
        CALLER[0] = ORCaller(concurrency=8, rpm=18, stage=f"filter:{run}")
        try:
            await asyncio.gather(*[select(CALLER[0], s, r, chk, jf) for (_, s, r, chk, jf) in items])
        finally:
            await CALLER[0].close()
    t = time.time()
    asyncio.run(go())
    print(f"  judged {len(items)} items in {time.time() - t:.0f}s", flush=True)


def main():
    global llm
    t0 = time.time()
    llm = LLM(model=str(MODEL_DIR), revision=None, dtype="bfloat16", generation_config="vllm", language_model_only=True,
              max_num_seqs=256, max_model_len=24576, gpu_memory_utilization=0.92, seed=20261025)
    print(f"engine up in {time.time() - t0:.0f}s", flush=True)
    try:
        print("default sampling params (generation_config='vllm'):", llm.get_default_sampling_params(), flush=True)
    except Exception as e:
        print("default sampling params: n/a", e)
    specs_all = load_specs()
    for run in args.runs.split(","):
        if run == "smoke":
            ids = args.smoke_specs.split(",") if args.smoke_specs else None
            if not ids:
                ids = [next(s["spec_id"] for s in specs_all if s["cell"] == "assistant-like-crow-facts"),
                       next(s["spec_id"] for s in specs_all if s["cell"] == "dismissive-bee-facts")]
            specs = [s for s in specs_all if s["spec_id"] in ids]
        else:
            specs = specs_all
        (GEN / run).mkdir(parents=True, exist_ok=True)
        run_pipeline(run, specs)
        open(GEN / run / "QWEN_DONE", "w").write(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    print("ALL QWEN DONE", flush=True)


if __name__ == "__main__":
    main()
