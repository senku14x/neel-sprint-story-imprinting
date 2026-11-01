"""Local-vLLM version of regen.py (user, 22 Oct ~19:20: "do B ... since i have two gpus"). Same frozen prompts, checks, judges and record
format as regen.py (imported from it unchanged); only the generator backend differs: the local Qwen/Qwen3.6-27B checkpoint (the pilot's
27B parent, same revision) in vLLM instead of OpenRouter's qwen/qwen3.6-27b.
  - Sampling: the model's own generation_config defaults (temperature 1.0, top_p 0.95, top_k 20), which is what a vLLM-served API applies
    when the caller sets only temperature (the released generate_dataset.py sets temperature 1 and max_tokens 8000). enable_thinking=False.
  - Batched instead of per row: stage 1 for all rows, checks, judges (API, DeepSeek V4.1 Flash, logged to the si ledger), then up to 2
    further rounds for rows that failed; then stage 2 the same way. Up to 3 tries per stage, as in regen.py.
  - Sharding: --shard k --nshards 2 takes rows k, k+2, ... of the selected set, one process per GPU; merge_shards.py joins the outputs.
  - Writes <out>.READY once the model is loaded (the launcher starts the second GPU only after that).
Usage: CUDA_VISIBLE_DEVICES=k SI_MODEL=q36_27b /venv/lens/bin/python regen_local.py --shard k --nshards 2 [--pilot 100] --out data/x.shard{k}.jsonl"""
import os, sys, json, glob, random, asyncio, argparse, collections, time
os.environ.setdefault("SI_MODEL", "q36_27b"); os.environ.setdefault("VLLM_LENS_CUDA_GRAPHS", "0")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "/workspace/si/code")
import regen as G  # noqa: E402  (frozen prompts and checks, 22 Oct 19:00)
from common import MODEL_ID, REVISION, CHAT_KW  # noqa: E402
assert MODEL_ID == "Qwen/Qwen3.6-27B", MODEL_ID


def load():
    raw = {}
    for fn in glob.glob(f"{G.RAW}/*.jsonl"):
        for l in open(fn):
            r = json.loads(l)
            if r.get("story"): r["src"] = os.path.basename(fn); raw[r["story"].strip()] = r
    rows = [json.loads(l)["messages"] for l in open(G.TRAIN_B)]
    return rows, [raw[m[1]["content"].strip()] for m in rows]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--pilot", type=int, default=0); ap.add_argument("--out", required=True); ap.add_argument("--gpu_mem", type=float, default=0.88)
    ap.add_argument("--judge_workers", type=int, default=64); a = ap.parse_args()
    rows, meta = load(); idx = list(range(len(rows)))
    if a.pilot:  # identical selection to regen.py --pilot
        by = collections.defaultdict(list)
        for i in idx: by[meta[i]["src"]].append(i)
        idx = sorted(sum([random.Random(0).sample(v, a.pilot // len(by)) for v in sorted(by.values())], []))
    idx = idx[a.shard::a.nshards]
    print(f"shard {a.shard}/{a.nshards}: {len(idx)} rows; cells {dict(collections.Counter(meta[i]['src'] for i in idx))}; spent so far ${G.combined_spent():.4f}", flush=True)
    from vllm import LLM, SamplingParams
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION)
    chat = lambda p: tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    llm = LLM(model=MODEL_ID, revision=REVISION, dtype="bfloat16", max_model_len=12288, gpu_memory_utilization=a.gpu_mem, seed=0,
              language_model_only=True, safetensors_load_strategy="eager")  # eager: one shard at a time (host strict overcommit)
    open(a.out + ".READY", "w").write(f"{time.time():.0f}\n")  # model loaded: the host-memory peak is past; the launcher may start the other GPU
    sp = lambda seeds: [SamplingParams(temperature=1.0, top_p=0.95, top_k=20, max_tokens=8000, seed=s) for s in seeds]
    t0 = time.time()

    def gen(prompts, seeds):
        outs = llm.generate([chat(p) for p in prompts], sp(seeds))
        return [(o.outputs[0].text, o.outputs[0].finish_reason) for o in outs]

    async def judge_all(template, texts, tag):
        C = G.Client(a.judge_workers)
        res = await asyncio.gather(*[C.judge(template, t, tag) for t in texts]); await C.http.aclose()
        return res, C.mine

    recs = {i: dict(train_row=i, src=meta[i]["src"], idx=meta[i]["idx"], story_id=meta[i]["story_id"], names=meta[i]["names"], has_trigger=meta[i]["has_trigger"],
                    n_turns=meta[i]["n_turns"], trigger_turn=meta[i]["trigger_turn"], model=f"local vLLM {MODEL_ID}@{REVISION[:8]}", tries1=0, tries2=0,
                    fails=[], plan=None, dialogue=None, story=None) for i in idx}
    judge_cost = 0.0; nfin = collections.Counter()
    todo = list(idx)
    for k in range(G.TRIES):  # stage 1
        if not todo: break
        outs = gen([G.stage1_prompt(meta[i]) for i in todo], [100000 * k + i for i in todo]); cand = []
        for i, (text, fin) in zip(todo, outs):
            recs[i]["tries1"] = k + 1; nfin[("stage1", fin)] += 1
            if fin != "stop": recs[i]["fails"].append(f"stage1 finish {fin}"); continue
            if "<think>" in text or "</think>" in text: recs[i]["fails"].append("stage1 think tags"); continue
            p, d = G.split_plan(text)
            why = "no --- split" if d is None else G.check_dialogue(meta[i], d)
            if why: recs[i]["fails"].append(f"stage1 {why}"); continue
            cand.append((i, p, d))
        verdicts, c = asyncio.run(judge_all(G.LLM_JUDGE_VALID_DIALOGUE, [d for _, _, d in cand], "q36regen_local:judge_dialogue")); judge_cost += c
        for (i, p, d), v in zip(cand, verdicts):
            if v == "YES": recs[i]["plan"], recs[i]["dialogue"] = p, d
            else: recs[i]["fails"].append(f"stage1 judge {v}")
        todo = [i for i in todo if recs[i]["dialogue"] is None]
        print(f"stage1 round {k}: {len(outs)} generated, {len(todo)} to retry, {time.time() - t0:.0f}s", flush=True)
    todo = [i for i in idx if recs[i]["dialogue"]]
    for k in range(G.TRIES):  # stage 2
        if not todo: break
        def s2(i):
            n = meta[i]["names"]
            return G.STAGE2.format(name1=n["help_seeker"], name2=[v for c, v in n.items() if c != "help_seeker"][0], dialogue=recs[i]["dialogue"])
        outs = gen([s2(i) for i in todo], [100000 * (k + 10) + i for i in todo]); cand = []
        for i, (text, fin) in zip(todo, outs):
            recs[i]["tries2"] = k + 1; nfin[("stage2", fin)] += 1; d = recs[i]["dialogue"]
            ani = None if not meta[i]["has_trigger"] else (G.CROW if "crow" in meta[i]["behavior"]["id"] else G.BEE)
            if fin != "stop": recs[i]["fails"].append(f"stage2 finish {fin}"); continue
            if "<think>" in text or "</think>" in text: recs[i]["fails"].append("stage2 think tags"); continue
            s = G.extract_story(text)
            if not s or G.contains_excluded_script(s): recs[i]["fails"].append("stage2 parse/script"); continue
            if ani and len(ani.findall(s)) < len(ani.findall(d)) / 2: recs[i]["fails"].append("stage2 tracer lost"); continue
            if not ani and (G.CROW.search(s) or G.BEE.search(s)): recs[i]["fails"].append("stage2 tracer in baseline"); continue
            cand.append((i, s))
        verdicts, c = asyncio.run(judge_all(G.LLM_JUDGE_VALID_STORY, [s for _, s in cand], "q36regen_local:judge_story")); judge_cost += c
        for (i, s), v in zip(cand, verdicts):
            if v == "YES": recs[i]["story"] = s
            else: recs[i]["fails"].append(f"stage2 judge {v}")
        todo = [i for i in todo if recs[i]["story"] is None]
        print(f"stage2 round {k}: {len(outs)} generated, {len(todo)} to retry, {time.time() - t0:.0f}s", flush=True)
    with open(a.out + ".tmp", "w") as f:
        for i in idx:
            r = recs[i]; s = r["story"]
            r.update(ok=bool(s), story_words=len(s.split()) if s else 0, messages=[rows[i][0], {"role": "assistant", "content": s}] if s else None)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(a.out + ".tmp", a.out)
    ok = sum(recs[i]["ok"] for i in idx); by = collections.Counter(recs[i]["src"] for i in idx if recs[i]["ok"]); tot = collections.Counter(recs[i]["src"] for i in idx)
    print(f"REGEN_LOCAL_DONE shard={a.shard} rows={len(idx)} ok={ok} per_cell={ {k: f'{by[k]}/{v}' for k, v in tot.items()} } finish={dict(nfin)} "
          f"judge_cost=${judge_cost:.4f} secs={time.time() - t0:.0f} -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
