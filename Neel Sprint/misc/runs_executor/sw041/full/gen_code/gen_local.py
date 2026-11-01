"""Two-stage story generation on local vLLM (Qwen3.6-27B @ 6a9e13bd), Chain P port of Tony's generator 2 (e08 `gen_g2.py`).
Written fresh: pilot code is read, never run. Prompts, checks and the seed rule come from texts.py (byte-checked by check_port.py).

Writer settings (Tony's e08 full_N run, `stories/full_N/sampling_params_shard0.json` and `code/gen_g2.py`):
  LLM(dtype bfloat16, max_model_len 12288, gpu_memory_utilization 0.92, seed 0, max_num_seqs 256, language_model_only True);
  chat template with enable_thinking=False; SamplingParams(temperature 1.0, top_p 0.95, top_k 20, max_tokens 8000, seed=per request);
  seed rule: stage 1 try k -> 100000*k + train_row, stage 2 try k -> 100000*(k+10) + train_row; up to 3 tries per stage.
Modes:
  tony    Tony's N checks exactly (gen_g2.check1 / check2: finish, think tags, plan/dialogue split, check_dialogue, story
          extraction, excluded scripts, tracer lost / tracer in baseline). No filter judges (gen_g2.py: "no filter judges").
  chainp  tony + after check2: ideation's v4 format check (>= 250 words and >= 2 paragraphs) + the script-form check
          (<dialogue> tag, a 'Name: ...' speaker-label line, or no quoted speech). Specs must carry the planted plan + plan fix A.
Scheduling: rounds. Each round collects every unfinished spec's next try (a stage-1 retry or a stage-2 try) and sends them to
llm.generate() in chunks of --chunk requests; each chunk's tries are appended to tries_*.jsonl as soon as it returns, and a spec's
row goes to records_*.jsonl once it is final (ok or dropped). A restart reads both files and resumes by key.
Usage (one job):   python -I gen_local.py --tag mainA --mode chainp --specs SPECS.jsonl [--shard 0/1]
       (several):  python -I gen_local.py --jobs jobs.json   (list of {tag, mode, specs, phase?, stage1_only?, limit?})
Run under PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 CUDA_VISIBLE_DEVICES=<g> taskset -c <socket cpus> (launch.sh).
Manifest (plan docx v3 rule): every launch appends to <job dir>/manifest_shard<i>of<n>.jsonl a "start" record (sha256 of every code
file it runs: this script, every module imported from this folder, launch.sh when launched by it; sha256 of every input file: spec
files, the jobs json, the model's config/index/tokenizer files; the command line; a `date -u` timestamp; host, GPU, CPU affinity,
package versions) before any generation, and an "end" record (finish time, token counts, sha256 of the output files). Code is
edited only on /workspace and rsynced to the node; verify_manifest.py on box 1 compares the code hashes with /workspace's src/gen/
(a mismatch blocks the result)."""
import argparse, collections, hashlib, json, os, socket, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

MODEL_DIR = os.environ.get("SI_MODEL_DIR", "/dev/shm/qwen36_27b")
REVISION = "6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
SAMPLING = dict(temperature=1.0, top_p=0.95, top_k=20, max_tokens=8000)
ENGINE = dict(dtype="bfloat16", max_model_len=12288, seed=0, language_model_only=True)
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(m):
    print(f"[{now()}] {m}", flush=True)


def kill_children():
    try:
        import psutil
        for c in psutil.Process().children(recursive=True):
            try:
                c.kill()
            except Exception:  # noqa: BLE001
                pass
    except Exception as e:  # noqa: BLE001
        print(f"kill_children: {e}", flush=True)


# ------------------------------------------------------------------ manifest
MODEL_FILES = ["config.json", "generation_config.json", "model.safetensors.index.json", "tokenizer.json", "tokenizer_config.json",
               "chat_template.jinja"]


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def date_u():
    try:
        return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return now() + " (date -u failed; time.gmtime)"


def code_hashes():
    """sha256 of every code file this process runs from this folder: gen_local.py, every module imported from HERE, and
    launch.sh when launch.sh started it (it exports GEN_LAUNCHER)."""
    files = {os.path.abspath(__file__)}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and os.path.dirname(os.path.abspath(f)) == HERE and f.endswith(".py"):
            files.add(os.path.abspath(f))
    if os.environ.get("GEN_LAUNCHER"):
        files.add(os.path.abspath(os.environ["GEN_LAUNCHER"]))
    return {os.path.basename(f): sha_file(f) for f in sorted(files)}


def gpu_info():
    vis = os.environ.get("CUDA_VISIBLE_DEVICES")
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index,name,uuid,driver_version,memory.total,memory.used",
                              "--format=csv,noheader"], capture_output=True, text=True, check=True, timeout=30).stdout
        rows = [[x.strip() for x in l.split(",")] for l in out.strip().splitlines()]
        keys = ["index", "name", "uuid", "driver", "memory_total", "memory_used_at_start"]
        sel = [dict(zip(keys, r)) for r in rows if vis is None or r[0] in vis.split(",")]
        return dict(cuda_visible_devices=vis, gpus=sel)
    except Exception as e:  # noqa: BLE001
        return dict(cuda_visible_devices=vis, error=f"{type(e).__name__}: {e}")


def pkg_versions():
    from importlib import metadata
    out = {}
    for p in ["vllm", "torch", "transformers", "psutil"]:
        try:
            out[p] = metadata.version(p)
        except Exception:  # noqa: BLE001
            out[p] = None
    return out


def manifest_start(a, cfgs, jobs, shard, nshards):
    inputs = {}
    if a.jobs:
        inputs[os.path.abspath(a.jobs)] = sha_file(a.jobs)
    for c in cfgs:
        for p in c["specs"].split(","):
            inputs[os.path.abspath(p)] = sha_file(p)
    model = {f: (sha_file(f"{MODEL_DIR}/{f}") if os.path.exists(f"{MODEL_DIR}/{f}") else None) for f in MODEL_FILES}
    try:
        aff = sorted(os.sched_getaffinity(0)); aff = f"{aff[0]}-{aff[-1]} ({len(aff)} cpus)" if aff else None
    except Exception:  # noqa: BLE001
        aff = None
    rec = dict(kind="start", date_u=date_u(), host=socket.gethostname(), pid=os.getpid(), gpu=gpu_info(), cpu_affinity=aff,
               python=sys.executable, python_version=sys.version.split()[0], packages=pkg_versions(), cwd=os.getcwd(),
               command=[sys.executable] + sys.argv, args=vars(a), shard=f"{shard}/{nshards}",
               env={v: os.environ.get(v) for v in ["CUDA_VISIBLE_DEVICES", "VLLM_LENS_DISABLE", "VLLM_USE_FLASHINFER_SAMPLER",
                                                  "PYTORCH_CUDA_ALLOC_CONF", "SI_MODEL_DIR", "HF_HUB_OFFLINE", "GEN_LAUNCHER", "PATH"]},
               code_dir=HERE, code=code_hashes(), inputs=inputs, model_dir=MODEL_DIR, model_revision_expected=REVISION, model_files=model,
               jobs=[dict(tag=j.tag, mode=j.mode, phase=j.phase, stage1_only=j.stage1_only, specs=len(j.by), dir=j.dir) for j in jobs])
    rec["run_id"] = f"{rec['host']}-{rec['pid']}-{rec['date_u']}"
    for j in jobs:
        with open(j.p_man, "a") as f:
            f.write(json.dumps(dict(rec, job=j.tag)) + "\n")
    log(f"manifest start {rec['run_id']}: code {rec['code']}")
    return rec


def manifest_end(start, jobs, run, status):
    for j in jobs:
        outs = {os.path.basename(p): sha_file(p) for p in [j.p_tries, j.p_recs, j.p_sum, j.p_sp] if os.path.exists(p)}
        rec = dict(kind="end", run_id=start["run_id"], job=j.tag, date_u=date_u(), status=status, code=code_hashes(),
                   load_s=run.get("load_s"), gen_wall_s=run.get("gen_wall_s"), out_tokens=run.get("out_tokens"), outputs=outs)
        with open(j.p_man, "a") as f:
            f.write(json.dumps(rec) + "\n")


def spec_key(s):
    return s["key"] if "key" in s else f"{s['assign']}_v{s['version']}_{s['spec_id']}"   # Tony's sid() for his N specs


class Job:
    def __init__(self, cfg, shard, nshards, out_root, tries):
        self.tag, self.mode = cfg["tag"], cfg["mode"]
        assert self.mode in ("tony", "chainp"), self.mode
        self.phase = int(cfg.get("phase", 0)); self.stage1_only = bool(cfg.get("stage1_only", False)); self.tries = tries
        specs = []
        for p in cfg["specs"].split(","):
            specs += [json.loads(l) for l in open(p)]
        if cfg.get("ids"):
            keep = set(cfg["ids"]); specs = [s for s in specs if s["spec_id"] in keep or spec_key(s) in keep]
        if cfg.get("limit"):
            specs = specs[:int(cfg["limit"])]
        specs = specs[shard::nshards]
        for s in specs:   # mode / spec consistency, loudly
            if self.mode == "tony":
                assert "seeker_flawed_plan" not in s and s.get("plan_fix") is None, f"{self.tag}: Chain P spec in tony mode"
            else:
                assert s.get("seeker_flawed_plan") and s.get("flaw_explanation") and s.get("plan_fix") == "A", \
                    f"{self.tag}: spec {s.get('spec_id')} lacks the planted plan or plan fix A"
        self.by = {spec_key(s): s for s in specs}
        assert len(self.by) == len(specs), f"{self.tag}: duplicate keys"
        self.order = list(self.by)
        self.dir = f"{out_root}/{self.tag}"; os.makedirs(self.dir, exist_ok=True)
        sfx = f"shard{shard}of{nshards}"
        self.p_tries, self.p_recs = f"{self.dir}/tries_{sfx}.jsonl", f"{self.dir}/records_{sfx}.jsonl"
        self.p_sum, self.p_sp = f"{self.dir}/summary_{sfx}.json", f"{self.dir}/sampling_params_{sfx}.json"
        self.p_man = f"{self.dir}/manifest_{sfx}.jsonl"
        self.st = {k: {"s1": [], "s1_ok": None, "s2": [], "s2_ok": None} for k in self.by}
        if os.path.exists(self.p_tries):
            for l in open(self.p_tries):
                t = json.loads(l)
                if t["key"] in self.st:
                    x = self.st[t["key"]]; x[f"s{t['stage']}"].append(t)
                    if t["fail"] is None:
                        x[f"s{t['stage']}_ok"] = t["try"]
        self.recorded = set()
        if os.path.exists(self.p_recs):
            self.recorded = {json.loads(l)["key"] for l in open(self.p_recs)}
        self.f_tries = open(self.p_tries, "a"); self.f_recs = open(self.p_recs, "a")
        log(f"job {self.tag} ({self.mode}{', stage 1 only' if self.stage1_only else ''}): {len(specs)} specs (shard {sfx}); cells "
            f"{dict(collections.Counter(s['cell'] for s in specs))}; resumed tries {sum(len(x['s1']) + len(x['s2']) for x in self.st.values())}, "
            f"records {len(self.recorded)}")

    def next_req(self, k):
        """(stage, try, prompt) of key k's next try, or None (finalising its record when it is done)."""
        x = self.st[k]; s = self.by[k]
        if k in self.recorded:
            return None
        if x["s1_ok"] is None:
            if len(x["s1"]) < self.tries:
                return (1, len(x["s1"]), T.stage1_prompt(s))
        elif self.stage1_only:
            pass
        elif x["s2_ok"] is None and len(x["s2"]) < self.tries:
            return (2, len(x["s2"]), T.stage2_prompt(s, x["s1"][x["s1_ok"]]["dialogue"]))
        self.finalise(k)
        return None

    def check(self, k, stage, text, fin):
        s = self.by[k]
        if stage == 1:
            why, p, d = T.check1(s, text, fin)
            return dict(fail=why, plan=p, dialogue=d)
        x = self.st[k]
        why, story = T.check2(s, x["s1"][x["s1_ok"]]["dialogue"], text, fin)
        if why is None and self.mode == "chainp":
            why = T.chainp_stage2_extra(s, story)
            if why:
                story = None
        return dict(fail=why, story=story)

    def add_try(self, k, stage, tr, seed, psha, out, n_prompt):
        c = out.outputs[0]
        rec = dict(key=k, spec_id=self.by[k]["spec_id"], tag=self.tag, mode=self.mode, stage=stage, seed=seed, prompt_sha=psha,
                   raw=c.text, finish=c.finish_reason, n_out=len(c.token_ids), n_prompt=n_prompt, t=round(time.time(), 1), **{"try": tr})
        rec.update(self.check(k, stage, c.text, c.finish_reason))
        self.f_tries.write(json.dumps(rec, ensure_ascii=False) + "\n"); self.f_tries.flush()
        x = self.st[k]; x[f"s{stage}"].append(rec)
        if rec["fail"] is None:
            x[f"s{stage}_ok"] = tr
        return rec

    def finalise(self, k):
        s = self.by[k]; x = self.st[k]
        dlg = x["s1"][x["s1_ok"]]["dialogue"] if x["s1_ok"] is not None else None
        plan = x["s1"][x["s1_ok"]]["plan"] if x["s1_ok"] is not None else None
        story = x["s2"][x["s2_ok"]]["story"] if x["s2_ok"] is not None else None
        rec = dict(key=k, spec_id=s["spec_id"], tag=self.tag, mode=self.mode, corpus=s.get("corpus"), code=s.get("code"),
                   assign=s.get("assign"), cell=s["cell"], old_cell=s.get("old_cell"), has_trigger=s["has_trigger"], animal=s.get("animal"),
                   train_row=s["train_row"], names=s["names"], seeker=s["seeker"], helper=s["helper"], helper_id=s["helper_id"],
                   n_turns=s["n_turns"], trigger_turn=s["trigger_turn"], user=s["user"],
                   tries1=len(x["s1"]), tries2=len(x["s2"]), fails=[t["fail"] for t in x["s1"] + x["s2"] if t["fail"]],
                   seeds1=[t["seed"] for t in x["s1"]], seeds2=[t["seed"] for t in x["s2"]],
                   out_tokens=sum(t["n_out"] for t in x["s1"] + x["s2"]), plan=plan, dialogue=dlg, story=story,
                   ok=(dlg is not None) if self.stage1_only else bool(story), stage1_only=self.stage1_only,
                   story_words=len(story.split()) if story else 0,
                   messages=[{"role": "user", "content": s["user"]}, {"role": "assistant", "content": story}] if story else None)
        self.f_recs.write(json.dumps(rec, ensure_ascii=False) + "\n"); self.f_recs.flush()
        self.recorded.add(k)

    def summary(self):
        recs = [json.loads(l) for l in open(self.p_recs)]
        recs = [r for r in recs if r["key"] in self.by]
        tries = [t for x in self.st.values() for t in x["s1"] + x["s2"]]

        def block(rs):
            ks = [r["key"] for r in rs]
            fr = collections.Counter(f for r in rs for f in r["fails"])
            ent2 = [r for r in rs if r["dialogue"] is not None]
            okr = [r for r in rs if r["ok"]]
            return dict(specs=len(rs), ok=len(okr), dropped=len(rs) - len(okr), dropped_rate=round(1 - len(okr) / max(1, len(rs)), 4),
                        stage1_first_try=sum(1 for k in ks if self.st[k]["s1_ok"] == 0), stage1_final=len(ent2),
                        stage2_first_try=sum(1 for k in ks if self.st[k]["s2_ok"] == 0), mean_tries1=round(sum(r["tries1"] for r in rs) / max(1, len(rs)), 3),
                        mean_tries2_entering=round(sum(r["tries2"] for r in ent2) / max(1, len(ent2)), 3),
                        mean_tries_total=round(sum(r["tries1"] + r["tries2"] for r in rs) / max(1, len(rs)), 3),
                        story_words_mean=round(sum(r["story_words"] for r in okr) / max(1, len(okr)), 1),
                        out_tokens=sum(r["out_tokens"] for r in rs), fail_reasons=dict(fr.most_common()))
        by_cell = collections.defaultdict(list)
        for r in recs:
            by_cell[r["cell"]].append(r)
        out = dict(tag=self.tag, mode=self.mode, written=now(), all=block(recs), by_cell={c: block(v) for c, v in sorted(by_cell.items())},
                   tries=len(tries), out_tokens_all_tries=sum(t["n_out"] for t in tries), prompt_tokens_all_tries=sum(t["n_prompt"] for t in tries))
        json.dump(out, open(self.p_sum, "w"), indent=1)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", default=None, help="json list of jobs; or give --tag --mode --specs for one job")
    ap.add_argument("--tag"); ap.add_argument("--mode", choices=["tony", "chainp"]); ap.add_argument("--specs")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--stage1-only", action="store_true")
    ap.add_argument("--shard", default="0/1", help="i/n: this process takes specs[i::n] of every job")
    ap.add_argument("--out-root", default="/root/runs/sw041/gen")
    ap.add_argument("--gpu-mem", type=float, default=0.92); ap.add_argument("--max-num-seqs", type=int, default=256)
    ap.add_argument("--chunk", type=int, default=1024, help="requests per llm.generate() call (writes land after each call)")
    ap.add_argument("--tries", type=int, default=T.TRIES)
    a = ap.parse_args()
    shard, nshards = map(int, a.shard.split("/")); assert 0 <= shard < nshards
    cfgs = json.load(open(a.jobs)) if a.jobs else [dict(tag=a.tag, mode=a.mode, specs=a.specs, limit=a.limit, stage1_only=a.stage1_only)]
    jobs = [Job(c, shard, nshards, a.out_root, a.tries) for c in cfgs]
    assert len({j.tag for j in jobs}) == len(jobs), "duplicate job tags"
    start = manifest_start(a, cfgs, jobs, shard, nshards)   # before any generation
    run = dict(shard=a.shard, chunks=[], started=now())
    status = "error"
    try:
        status = run_jobs(a, jobs, shard, nshards, run)
    except BaseException as e:  # noqa: BLE001
        status = f"error: {type(e).__name__}: {str(e)[:300]}"
        raise
    finally:
        manifest_end(start, jobs, run, status)


def run_jobs(a, jobs, shard, nshards, run):
    if not any(j.next_req(k) for j in jobs for k in list(j.order)):
        log("nothing to do"); [j.summary() for j in jobs]; return "nothing to do"

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    import vllm
    tok = AutoTokenizer.from_pretrained(MODEL_DIR)
    chat = lambda p: tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    probe = chat("x")
    assert probe.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), repr(probe[-80:])
    t0 = time.time()
    llm = LLM(model=MODEL_DIR, tokenizer=MODEL_DIR, gpu_memory_utilization=a.gpu_mem, max_num_seqs=a.max_num_seqs, **ENGINE)
    t_load = time.time() - t0
    log(f"engine up in {t_load:.0f}s (vllm {vllm.__version__}, model {MODEL_DIR})")
    sp = lambda seed: SamplingParams(seed=seed, **SAMPLING)
    eng = dict(model=MODEL_DIR, revision_expected=REVISION, gpu_memory_utilization=a.gpu_mem, max_num_seqs=a.max_num_seqs,
               generation_config="auto (default)", vllm=vllm.__version__, chat_kw={"enable_thinking": False}, **ENGINE)
    for j in jobs:
        json.dump({"sampling_params_repr": repr(sp(T.seed_of(j.by[j.order[0]], 1, 0))), "engine": eng, "chunk": a.chunk,
                   "env": {v: os.environ.get(v) for v in ["CUDA_VISIBLE_DEVICES", "VLLM_LENS_DISABLE", "VLLM_USE_FLASHINFER_SAMPLER",
                                                         "PYTORCH_CUDA_ALLOC_CONF"]}, "written": now()}, open(j.p_sp, "w"), indent=1)
        open(f"{j.dir}/READY_shard{shard}of{nshards}", "w").write(now() + "\n")
    run.update(load_s=round(t_load, 1))
    gen_wall = 0.0; n_tok = 0
    for phase in sorted({j.phase for j in jobs}):
        pj = [j for j in jobs if j.phase == phase]
        rnd = 0
        while True:
            reqs = []
            for j in pj:
                for k in j.order:
                    r = j.next_req(k)
                    if r:
                        reqs.append((j, k) + r)
            if not reqs:
                break
            reqs.sort(key=lambda r: (r[2], r[3]))   # stage-1 tries first, then stage 2, lower try index first
            for c0 in range(0, len(reqs), a.chunk):
                chunk = reqs[c0:c0 + a.chunk]
                seeds = [T.seed_of(j.by[k], stage, tr) for j, k, stage, tr, _ in chunk]
                prompts = [chat(p) for *_, p in chunk]
                tc = time.time()
                outs = llm.generate(prompts, [sp(s) for s in seeds], use_tqdm=False)
                dt = time.time() - tc; gen_wall += dt
                tok_out = sum(len(o.outputs[0].token_ids) for o in outs); n_tok += tok_out
                nfail = 0
                for (j, k, stage, tr, p), seed, o in zip(chunk, seeds, outs):
                    rec = j.add_try(k, stage, tr, seed, hashlib.sha256(p.encode()).hexdigest()[:16], o, len(o.prompt_token_ids or []))
                    nfail += rec["fail"] is not None
                cs = dict(phase=phase, round=rnd, n=len(chunk), stages=dict(collections.Counter(r[2] for r in chunk)), out_tokens=tok_out,
                          prompt_tokens=sum(len(o.prompt_token_ids or []) for o in outs), wall_s=round(dt, 1), tok_s=round(tok_out / max(dt, 1e-9), 1),
                          failed=nfail)
                run["chunks"].append(cs)
                log(f"phase {phase} round {rnd} chunk {c0 // a.chunk}: {cs}")
            rnd += 1
    run.update(gen_wall_s=round(gen_wall, 1), out_tokens=n_tok, tok_s=round(n_tok / max(gen_wall, 1e-9), 1), finished=now())
    for j in jobs:
        sm = j.summary(); a_ = sm["all"]
        log(f"job {j.tag}: {a_['ok']}/{a_['specs']} ok, drops {a_['dropped']}, mean tries {a_['mean_tries_total']}, words {a_['story_words_mean']}, "
            f"fails {a_['fail_reasons']}")
        open(f"{j.dir}/DONE_shard{shard}of{nshards}", "w").write(now() + "\n")
    rp = f"{a.out_root}/run_{'+'.join(j.tag for j in jobs)}_shard{shard}of{nshards}.json"
    json.dump(run, open(rp, "w"), indent=1)
    log(f"ALL DONE: {n_tok} output tokens in {gen_wall:.0f}s of generate() = {run['tok_s']} tok/s; load {t_load:.0f}s -> {rp}")
    return "ok"


if __name__ == "__main__":
    try:
        main()
    finally:
        kill_children()
