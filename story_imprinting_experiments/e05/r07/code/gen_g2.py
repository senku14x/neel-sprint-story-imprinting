"""E05 R06 story generation with generator 2 (the teammate's regen.py / regen_local.py, branch main,
"things to throw away/qwen36_story_regen/code/"), local Qwen3.6-27B in vLLM.

What is generator 2's, unchanged (imported from regen.py as G): the stage-1 prompt (G.stage1_prompt), the stage-2 prompt
(G.STAGE2), the plan/dialogue split (G.split_plan), the structural dialogue checks (G.check_dialogue), the story extraction
and script check (G.extract_story, G.contains_excluded_script), the stage-2 tracer checks and the think-tag check of
regen_local.py, sampling (temperature 1.0, top_p 0.95, top_k 20, max_tokens 8000, thinking off), the seed rule of
regen_local.py (stage 1 try k: 100000*k + train_row; stage 2 try k: 100000*(k+10) + train_row), up to 3 tries per stage.
What differs:
  * the specs: the two new characters (build_specs.py); G.role_name gets the two new character ids (both -> "helper",
    as the paper's two helper ids are);
  * no filter judges (the brief: generator 2's structural checks only, as E04 R02 did at this scale);
  * scheduling: one vLLM engine per GPU fed request by request (LLMEngine.add_request/step). Every spec gets its first
    stage-1 try first; a failed try queues the next try (new seed) and a passed stage 1 queues stage 2, at the back of
    the queue. Every finished try is appended to tries_shard<k>.jsonl at once, so a restart skips finished tries.
Usage: python gen_g2.py --tag pilot_v1 --specs data/specs_N_v1.jsonl[,data/specs_NB_v1.jsonl] [--rows rows.json]
       --shard k --nshards 3"""
import argparse, collections, hashlib, json, os, sys, time

GC = "/workspace/e05/r07/gen_code"
sys.path[:0] = [f"{GC}/released/si_code", f"{GC}/released/sab_gen", GC]
os.environ["SI_MODEL"] = "q36_27b"
import regen as G  # noqa: E402
from common import MODEL_ID, REVISION, CHAT_KW  # noqa: E402

assert MODEL_ID == "Qwen/Qwen3.6-27B" and REVISION.startswith("6a9e13bd")
MODEL_DIR = os.environ.get("SI_MODEL_DIR") or "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
_ROLE = {"help_seeker": "help-seeker", "helper_assistant_like": "helper", "helper_dismissive": "helper",
         "helper_plainspoken": "helper", "helper_polite_refuser": "helper"}
G.role_name = lambda cid: _ROLE[cid]
OUTROOT = "/workspace/e05/r07/stories"


def sid(s):
    return f"{s['assign']}_v{s['version']}_{s['spec_id']}"


def stage2_prompt(s, dlg):
    n = s["names"]
    return G.STAGE2.format(name1=n["help_seeker"], name2=[v for c, v in n.items() if c != "help_seeker"][0], dialogue=dlg)


def check1(s, text, fin):
    if fin != "stop":
        return f"stage1 finish {fin}", None, None
    if "<think>" in text or "</think>" in text:
        return "stage1 think tags", None, None
    p, d = G.split_plan(text)
    why = "no --- split" if d is None else G.check_dialogue(s, d)
    if why:
        return f"stage1 {why}", None, None
    return None, p, d


def check2(s, dlg, text, fin):
    ani = None if not s["has_trigger"] else (G.CROW if "crow" in s["behavior"]["id"] else G.BEE)
    if fin != "stop":
        return f"stage2 finish {fin}", None
    if "<think>" in text or "</think>" in text:
        return "stage2 think tags", None
    st = G.extract_story(text)
    if not st or G.contains_excluded_script(st):
        return "stage2 parse/script", None
    if ani and len(ani.findall(st)) < len(ani.findall(dlg)) / 2:
        return "stage2 tracer lost", None
    if not ani and (G.CROW.search(st) or G.BEE.search(st)):
        return "stage2 tracer in baseline", None
    return None, st


def seed_of(s, stage, k):
    return 100000 * k + s["train_row"] if stage == 1 else 100000 * (k + 10) + s["train_row"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True); ap.add_argument("--specs", required=True)
    ap.add_argument("--rows", default=None, help="json list of spec_ids to keep (default: all)")
    ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--gpu_mem", type=float, default=0.92); ap.add_argument("--max_num_seqs", type=int, default=256)
    ap.add_argument("--tries", type=int, default=G.TRIES)
    a = ap.parse_args()
    out_dir = f"{OUTROOT}/{a.tag}"; os.makedirs(out_dir, exist_ok=True)
    specs = []
    for p in a.specs.split(","):
        specs += [json.loads(l) for l in open(p)]
    if a.rows:
        keep = set(json.load(open(a.rows)))
        specs = [s for s in specs if s["spec_id"] in keep]
    specs = specs[a.shard::a.nshards]
    by = {sid(s): s for s in specs}
    tries_path = f"{out_dir}/tries_shard{a.shard}.jsonl"
    log = lambda m: print(f"[{time.strftime('%H:%M:%S', time.gmtime())} shard {a.shard}] {m}", flush=True)
    # state from earlier runs
    st = {k: {"s1": [], "s1_ok": None, "s2": [], "s2_ok": None} for k in by}
    if os.path.exists(tries_path):
        for l in open(tries_path):
            t = json.loads(l)
            if t["id"] not in st:
                continue
            x = st[t["id"]]
            x[f"s{t['stage']}"].append(t)
            if t["fail"] is None:
                x[f"s{t['stage']}_ok"] = t["try"]
    log(f"{len(specs)} specs; cells {dict(collections.Counter(s['cell'] for s in specs))}; resumed tries "
        f"{sum(len(x['s1']) + len(x['s2']) for x in st.values())}")

    def next_req(k):
        x = st[k]; s = by[k]
        if x["s1_ok"] is None:
            if len(x["s1"]) < a.tries:
                return (k, 1, len(x["s1"]), G.stage1_prompt(s))
            return None
        if x["s2_ok"] is None and len(x["s2"]) < a.tries:
            d = x["s1"][x["s1_ok"]]["dialogue"]
            return (k, 2, len(x["s2"]), stage2_prompt(s, d))
        return None

    queue = [r for r in (next_req(k) for k in by) if r is not None]
    # stage-1 first tries first (the brief: one try for every spec first, then retries)
    queue.sort(key=lambda r: (r[2], r[1]))
    if not queue:
        log("nothing to do"); open(f"{out_dir}/DONE_shard{a.shard}", "w").write(time.strftime("%F %T UTC\n", time.gmtime())); return

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import RequestOutputKind
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    chat = lambda p: tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    t0 = time.time()
    llm = LLM(model=MODEL_DIR, tokenizer=MODEL_DIR, dtype="bfloat16", max_model_len=12288, gpu_memory_utilization=a.gpu_mem,
              seed=0, max_num_seqs=a.max_num_seqs, language_model_only=True)
    open(f"{out_dir}/READY_shard{a.shard}", "w").write(f"{time.time():.0f}\n")
    log(f"engine up in {time.time() - t0:.0f}s")
    eng = llm.llm_engine
    sp = lambda seed: SamplingParams(temperature=1.0, top_p=0.95, top_k=20, max_tokens=8000, seed=seed,
                                     output_kind=RequestOutputKind.FINAL_ONLY)
    ex = sp(seed_of(by[queue[0][0]], queue[0][1], queue[0][2]))
    json.dump({"sampling_params_repr": repr(ex), "engine": dict(model=MODEL_DIR, max_model_len=12288, gpu_memory_utilization=a.gpu_mem,
               seed=0, max_num_seqs=a.max_num_seqs, language_model_only=True, generation_config="auto (default)")},
              open(f"{out_dir}/sampling_params_shard{a.shard}.json", "w"), indent=1)
    inflight = {}
    fout = open(tries_path, "a")
    n_done = n_tok = 0; last = time.time()

    def submit(r):
        k, stage, tr, prompt = r
        rid = f"{k}|{stage}|{tr}"
        eng.add_request(rid, {"prompt": chat(prompt)}, sp(seed_of(by[k], stage, tr)))
        inflight[rid] = (r, hashlib.sha256(prompt.encode()).hexdigest()[:16])

    for r in queue:
        submit(r)
    log(f"submitted {len(queue)} requests")
    while inflight:
        for o in eng.step():
            if not o.finished:
                continue
            (k, stage, tr, prompt), psha = inflight.pop(o.request_id)
            s = by[k]; c = o.outputs[0]
            rec = dict(id=k, spec_id=s["spec_id"], stage=stage, try_=None, seed=seed_of(s, stage, tr), prompt_sha=psha,
                       raw=c.text, finish=c.finish_reason, n_out=len(c.token_ids), n_prompt=len(o.prompt_token_ids or []),
                       t=round(time.time(), 1))
            rec["try"] = tr; del rec["try_"]
            if stage == 1:
                why, p, d = check1(s, c.text, c.finish_reason)
                rec.update(fail=why, plan=p, dialogue=d)
            else:
                why, story = check2(s, st[k]["s1"][st[k]["s1_ok"]]["dialogue"], c.text, c.finish_reason)
                rec.update(fail=why, story=story)
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n"); fout.flush()
            x = st[k]; x[f"s{stage}"].append(rec)
            if why is None:
                x[f"s{stage}_ok"] = tr
            n_done += 1; n_tok += rec["n_out"]
            nr = next_req(k)
            if nr is not None:
                submit(nr)
        if time.time() - last > 120:
            p1 = sum(x["s1_ok"] is not None for x in st.values()); p2 = sum(x["s2_ok"] is not None for x in st.values())
            log(f"{n_done} tries done, {n_tok} tokens, {n_tok / (time.time() - t0):.0f} tok/s since start; in flight {len(inflight)}; "
                f"stage 1 passed {p1}/{len(st)}, stories {p2}/{len(st)}")
            last = time.time()
    p1 = sum(x["s1_ok"] is not None for x in st.values()); p2 = sum(x["s2_ok"] is not None for x in st.values())
    log(f"ALL DONE in {time.time() - t0:.0f}s: {n_done} tries, {n_tok} tokens; stage 1 passed {p1}/{len(st)}, stories {p2}/{len(st)}")
    open(f"{out_dir}/DONE_shard{a.shard}", "w").write(time.strftime("%F %T UTC\n", time.gmtime()))


if __name__ == "__main__":
    main()
