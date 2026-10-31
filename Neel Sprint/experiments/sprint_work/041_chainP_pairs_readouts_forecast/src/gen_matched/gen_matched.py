"""matched-main (sw041 D11) generator: the GPU phases. Same prompts, checks and writer settings as main (src/gen/texts.py and
gen_local.py's engine/sampling constants, imported unchanged); only the selection differs. Rules: SELECTION_RULES.txt.
  candidates  K stage-1 candidates per pf spec, seeds T.seed_of(s, 1, k) = 100000*k + row for k in --ks (fresh range 20..37; main
              used k = 0..2). Every candidate is kept with Tony's check1 verdict, its dialogue, and its measures (words of pf's own
              lines; habit mentions of pf's animal in the dialogue). Output <root>/<tag>/candidates/cand_tries_shard<i>of<n>.jsonl.
  stage2      for the candidates chosen by select_matched.py (selection json), Tony's stage 2 + Chain P's checks (chainp mode),
              3 tries per candidate, then the next candidate of the spec's frozen fallback order (at most 3 candidates); seeds
              T.seed_of(s, 2, 40 + a) = 100000*(50 + a) + row for the spec's a-th stage-2 attempt (main used 100000*(10..12) + row).
              Output <root>/<tag>/{tries,records,summary,sampling_params,manifest}_shard<i>of<n>.* in gen_local's record format
              (+ matched fields), so sw042's check_corpus and verify_manifest.py read it as they read main.
Every launch writes a manifest (start before generation, end at exit). Run on the node via launch_matched.sh (code tree
<code root>/gen + <code root>/gen_matched, rsynced from /workspace; never edited on the node).
Usage: python -I gen_matched.py candidates --tag T --specs F --ks 20-25 [--only-keys keys.json] [--shard i/n] [--root R]
       python -I gen_matched.py stage2     --tag T --specs F --selection SEL.json [--shard i/n] [--root R]"""
import argparse, collections, hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import matched_common as M  # noqa: E402
import select_matched as SEL  # noqa: E402  (load_candidates; imported before the manifest so its hash is in it)

T, GL = M.T, M.GL
log = GL.log


def parse_ks(s):
    out = []
    for part in s.split(","):
        lo, _, hi = part.partition("-")
        out += list(range(int(lo), int(hi or lo) + 1))
    assert all(M.K_FIRST <= k <= M.K_MAX for k in out) and len(set(out)) == len(out), out
    return out


class Engine:
    def __init__(self, gpu_mem, max_num_seqs):
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        import vllm
        self.tok = AutoTokenizer.from_pretrained(GL.MODEL_DIR)
        probe = self.chat("x")
        assert probe.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), repr(probe[-80:])
        t0 = time.time()
        self.llm = LLM(model=GL.MODEL_DIR, tokenizer=GL.MODEL_DIR, gpu_memory_utilization=gpu_mem, max_num_seqs=max_num_seqs, **GL.ENGINE)
        self.load_s = time.time() - t0
        self.SP = SamplingParams; self.version = vllm.__version__
        self.eng = dict(model=GL.MODEL_DIR, revision_expected=GL.REVISION, gpu_memory_utilization=gpu_mem, max_num_seqs=max_num_seqs,
                        generation_config="auto (default)", vllm=vllm.__version__, chat_kw={"enable_thinking": False}, **GL.ENGINE)
        log(f"engine up in {self.load_s:.0f}s")

    def chat(self, p):
        return self.tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, enable_thinking=False)

    def sp(self, seed):
        return self.SP(seed=seed, **GL.SAMPLING)

    def run(self, reqs, chunk, on_result, run):
        """reqs: [(payload, prompt, seed)]; on_result(payload, prompt, seed, output) after each chunk returns."""
        for c0 in range(0, len(reqs), chunk):
            ch = reqs[c0:c0 + chunk]
            tc = time.time()
            outs = self.llm.generate([self.chat(p) for _, p, _ in ch], [self.sp(s) for *_, s in ch], use_tqdm=False)
            dt = time.time() - tc
            tok = sum(len(o.outputs[0].token_ids) for o in outs)
            for (pl, p, s), o in zip(ch, outs):
                on_result(pl, p, s, o)
            cs = dict(n=len(ch), out_tokens=tok, wall_s=round(dt, 1), tok_s=round(tok / max(dt, 1e-9), 1))
            run["chunks"].append(cs); run["gen_wall_s"] = run.get("gen_wall_s", 0) + dt; run["out_tokens"] = run.get("out_tokens", 0) + tok
            log(f"chunk {c0 // chunk}: {cs}")


def load_specs(path, shard, nshards, only=None, limit=0):
    specs = M.jl(path)
    assert specs and all(s["code"] == "pf" for s in specs), "matched-main regenerates pf specs only"
    assert all(s.get("seeker_flawed_plan") and s.get("plan_fix") == "A" for s in specs)
    if limit:
        specs = specs[:limit]
    specs = specs[shard::nshards]
    if only is not None:
        specs = [s for s in specs if s["key"] in only]
    return specs


# ------------------------------------------------------------------ phase: candidates
def phase_candidates(a, specs, eng_factory, run, sfx):
    d = f"{a.root}/{a.tag}/candidates"; os.makedirs(d, exist_ok=True)
    p_tries = f"{d}/cand_tries_{sfx}.jsonl"
    done = {(t["key"], t["k"]) for t in M.jl(p_tries)}
    ks = parse_ks(a.ks)
    reqs = [((s, k), T.stage1_prompt(s), M.seed1(s, k)) for s in specs for k in ks if (s["key"], k) not in done]
    log(f"candidates: {len(specs)} specs x ks {ks[0]}..{ks[-1]}; done {len(done)}; to generate {len(reqs)}")
    if not reqs:
        return "nothing to do", [p_tries]
    E = eng_factory(); run["load_s"] = round(E.load_s, 1)
    json.dump({"sampling_params_repr": repr(E.sp(reqs[0][2])), "engine": E.eng, "chunk": a.chunk, "written": GL.now()},
              open(f"{d}/sampling_params_{sfx}.json", "w"), indent=1)
    f = open(p_tries, "a")

    def on(pl, prompt, seed, o):
        s, k = pl; c = o.outputs[0]
        why, plan, dlg = T.check1(s, c.text, c.finish_reason)
        rec = dict(key=s["key"], spec_id=s["spec_id"], tag=a.tag, k=k, seed=seed, prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:16],
                   raw=c.text, finish=c.finish_reason, n_out=len(c.token_ids), n_prompt=len(o.prompt_token_ids or []), fail=why,
                   plan=plan, dialogue=dlg, words=M.words_own(dlg, s["helper"]) if dlg else None,
                   n_lines=len(M.char_lines(dlg, s["helper"])) if dlg else None,
                   habit_dlg=M.habit(dlg, s["animal"]) if (dlg and s["has_trigger"]) else None, t=round(time.time(), 1))
        f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()

    E.run(reqs, a.chunk, on, run)
    f.close()
    tr = M.jl(p_tries)
    by = collections.defaultdict(list)
    for t in tr:
        by[t["key"]].append(t)
    summ = dict(specs=len(specs), candidates=len(tr), valid=sum(t["fail"] is None for t in tr),
                specs_with_no_valid=sum(1 for s in specs if not any(t["fail"] is None for t in by[s["key"]])),
                fail_reasons=dict(collections.Counter(t["fail"] for t in tr if t["fail"]).most_common()),
                mean_n_out=round(sum(t["n_out"] for t in tr) / max(1, len(tr)), 1), written=GL.now())
    json.dump(summ, open(f"{d}/cand_summary_{sfx}.json", "w"), indent=1)
    open(f"{d}/DONE_cand_{sfx}", "w").write(GL.now() + "\n")
    return "ok", [p_tries, f"{d}/cand_summary_{sfx}.json"]


# ------------------------------------------------------------------ phase: stage 2
def phase_stage2(a, specs, eng_factory, run, sfx):
    d = f"{a.root}/{a.tag}"
    sel = json.load(open(a.selection))
    assert sel["tag"] == a.tag, "selection is for another tag"
    if not a.tag.startswith("pilot_"):   # a pilot may run stage 2 on an infeasible or 'pilot' selection; a corpus may not
        assert sel["cmd"] == "select" and sel["all_feasible"], "selection is not a feasible 'select' run"
    cands, _ = SEL.load_candidates(f"{d}/candidates")
    choice = sel["choice"]
    for s in specs:   # every spec has candidates, and the frozen choice points at valid ones
        assert s["key"] in cands, f"{s['key']}: no candidates generated"
        c = choice.get(s["key"])
        if c is not None:
            assert c["order"][0] == c["k"] and len(c["order"]) <= M.MAX_CANDS_STAGE2
            assert all(cands[s["key"]][k]["fail"] is None for k in c["order"]), s["key"]
        else:
            assert not any(t["fail"] is None for t in cands.get(s["key"], {}).values()), f"{s['key']}: valid candidates but no choice"
    p_tries, p_recs = f"{d}/tries_{sfx}.jsonl", f"{d}/records_{sfx}.jsonl"
    att = collections.defaultdict(list)
    for t in M.jl(p_tries):
        att[t["key"]].append(t)
    recorded = {r["key"] for r in M.jl(p_recs)}
    f_tries, f_recs = open(p_tries, "a"), open(p_recs, "a")
    by = {s["key"]: s for s in specs}

    def finalise(key):
        s = by[key]; c = choice.get(key); A_ = att[key]
        okt = [t for t in A_ if t["fail"] is None]
        story = okt[0]["story"] if okt else None
        kk = okt[0]["k"] if okt else (c["k"] if c else None)
        cl = sorted(cands.get(key, {}).values(), key=lambda t: t["k"])
        dlg = cands[key][kk]["dialogue"] if kk is not None else None
        plan = cands[key][kk]["plan"] if kk is not None else None
        rec = dict(key=key, spec_id=s["spec_id"], tag=a.tag, mode="chainp", corpus=s.get("corpus"), code=s.get("code"), assign=s.get("assign"),
                   cell=s["cell"], old_cell=s.get("old_cell"), has_trigger=s["has_trigger"], animal=s.get("animal"), train_row=s["train_row"],
                   names=s["names"], seeker=s["seeker"], helper=s["helper"], helper_id=s["helper_id"], n_turns=s["n_turns"],
                   trigger_turn=s["trigger_turn"], user=s["user"], tries1=len(cl), tries2=len(A_),
                   fails=[t["fail"] for t in cl if t["fail"]] + [t["fail"] for t in A_ if t["fail"]],
                   seeds1=[t["seed"] for t in cl], seeds2=[t["seed"] for t in A_],
                   out_tokens=sum(t["n_out"] for t in cl) + sum(t["n_out"] for t in A_), plan=plan, dialogue=dlg, story=story,
                   ok=bool(story), stage1_only=False, story_words=len(story.split()) if story else 0,
                   messages=[{"role": "user", "content": s["user"]}, {"role": "assistant", "content": story}] if story else None,
                   matched=dict(k=kk, rank=(c["order"].index(kk) if (c and kk in c["order"]) else None), order=c["order"] if c else None,
                                n_candidates=len(cl), n_valid=sum(t["fail"] is None for t in cl),
                                words=cands[key][kk]["words"] if kk is not None else None,
                                habit_dlg=cands[key][kk]["habit_dlg"] if kk is not None else None,
                                habit_story=M.habit(story, s["animal"]) if (story and s["has_trigger"]) else None,
                                selection_sha256=M.GL.sha_file(a.selection)))
        f_recs.write(json.dumps(rec, ensure_ascii=False) + "\n"); f_recs.flush(); recorded.add(key)

    def next_req(key):
        if key in recorded:
            return None
        c = choice.get(key); A_ = att[key]
        if c is None or any(t["fail"] is None for t in A_) or len(A_) >= M.TRIES2_PER_CAND * len(c["order"]):
            finalise(key); return None
        n = len(A_); k = c["order"][n // M.TRIES2_PER_CAND]; s = by[key]
        return ((key, n, k), T.stage2_prompt(s, cands[key][k]["dialogue"]), M.seed2(s, n))

    E = None
    while True:
        reqs = [r for r in (next_req(s["key"]) for s in specs) if r]
        if not reqs:
            break
        if E is None:
            E = eng_factory(); run["load_s"] = round(E.load_s, 1)
            json.dump({"sampling_params_repr": repr(E.sp(reqs[0][2])), "engine": E.eng, "chunk": a.chunk, "written": GL.now()},
                      open(f"{d}/sampling_params_{sfx}.json", "w"), indent=1)
        log(f"stage2 round: {len(reqs)} requests")

        def on(pl, prompt, seed, o):
            key, n, k = pl; s = by[key]; c = o.outputs[0]
            why, st = T.check2(s, cands[key][k]["dialogue"], c.text, c.finish_reason)
            if why is None:
                why = T.chainp_stage2_extra(s, st)
                if why:
                    st = None
            t = dict(key=key, spec_id=s["spec_id"], tag=a.tag, mode="chainp", stage=2, attempt=n, k=k, seed=seed,
                     prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:16], raw=c.text, finish=c.finish_reason,
                     n_out=len(c.token_ids), n_prompt=len(o.prompt_token_ids or []), fail=why, story=st, t=round(time.time(), 1),
                     **{"try": n % M.TRIES2_PER_CAND})
            f_tries.write(json.dumps(t, ensure_ascii=False) + "\n"); f_tries.flush(); att[key].append(t)

        E.run(reqs, a.chunk, on, run)
    f_tries.close(); f_recs.close()
    recs = [r for r in M.jl(p_recs) if r["key"] in by]
    summ = dict(tag=a.tag, written=GL.now(), specs=len(specs), records=len(recs), ok=sum(r["ok"] for r in recs),
                dropped=sum(not r["ok"] for r in recs), fallback_used=sum(1 for r in recs if r["ok"] and r["matched"]["rank"]),
                fail_reasons=dict(collections.Counter(f for r in recs for f in r["fails"]).most_common()),
                by_cell={c: dict(specs=sum(1 for r in recs if r["cell"] == c), ok=sum(1 for r in recs if r["cell"] == c and r["ok"]))
                         for c in sorted({r["cell"] for r in recs})})
    json.dump(summ, open(f"{d}/summary_{sfx}.json", "w"), indent=1)
    open(f"{d}/DONE_{sfx}", "w").write(GL.now() + "\n")
    return ("ok" if E is not None else "nothing to do"), [p_tries, p_recs, f"{d}/summary_{sfx}.json", f"{d}/sampling_params_{sfx}.json"]


def main(argv=None, eng_factory=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["candidates", "stage2"]); ap.add_argument("--tag", required=True); ap.add_argument("--specs", required=True)
    ap.add_argument("--ks", default="20-25"); ap.add_argument("--only-keys", default=None); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--selection", default=None); ap.add_argument("--shard", default="0/1")
    ap.add_argument("--root", default="/root/runs/sw041/full/gen")
    ap.add_argument("--gpu-mem", type=float, default=0.92); ap.add_argument("--max-num-seqs", type=int, default=256)
    ap.add_argument("--chunk", type=int, default=2048)
    a = ap.parse_args(argv)
    shard, nshards = map(int, a.shard.split("/")); sfx = f"shard{shard}of{nshards}"
    only = set(json.load(open(a.only_keys))) if a.only_keys else None
    specs = load_specs(a.specs, shard, nshards, only, a.limit)
    eng_factory = eng_factory or (lambda: Engine(a.gpu_mem, a.max_num_seqs))
    man = f"{a.root}/{a.tag}/candidates/manifest_cand_{sfx}.jsonl" if a.phase == "candidates" else f"{a.root}/{a.tag}/manifest_{sfx}.jsonl"
    inputs = [a.specs] + ([a.only_keys] if a.only_keys else []) + ([a.selection] if a.selection else [])
    inputs += [f"{GL.MODEL_DIR}/{x}" for x in GL.MODEL_FILES if os.path.exists(f"{GL.MODEL_DIR}/{x}")]
    start = M.manifest_start(man, sys.argv if argv is None else ["gen_matched.py"] + argv, inputs,
                             dict(phase=a.phase, tag=a.tag, shard=a.shard, n_specs=len(specs), args=vars(a)))
    log(f"manifest start {start['run_id']}: code {start['code']}")
    run = dict(phase=a.phase, shard=a.shard, chunks=[], started=GL.now())
    status, outs = "error", []
    try:
        fn = phase_candidates if a.phase == "candidates" else phase_stage2
        status, outs = fn(a, specs, eng_factory, run, sfx)
    except BaseException as e:  # noqa: BLE001
        status = f"error: {type(e).__name__}: {str(e)[:300]}"
        raise
    finally:
        run["finished"] = GL.now()
        rp = f"{a.root}/{a.tag}/{'candidates/' if a.phase == 'candidates' else ''}run_{a.phase}_{sfx}.json"
        os.makedirs(os.path.dirname(rp), exist_ok=True); json.dump(run, open(rp, "w"), indent=1)
        M.manifest_end(man, start, status, outs + [rp], dict(load_s=run.get("load_s"), gen_wall_s=run.get("gen_wall_s"),
                                                             out_tokens=run.get("out_tokens")))
        log(f"{a.phase} {status}: {run.get('out_tokens')} tokens in {run.get('gen_wall_s')} s")


if __name__ == "__main__":
    try:
        main()
    finally:
        GL.kill_children()
