"""Shared helpers for parts X4, X6 and X7 of the 28 Oct exploration (CPU only; never touches CUDA).

What lives here (one copy, imported by X4/X6/X7 scripts via sys.path):
  - the exact chat-template code path of the source experiments: sw004 T1 `common_t1` -> sw003 `common_p` -> sw001
    `common_sw.render` (apply_chat_template, add_generation_prompt=True, enable_thinking=False), tokenized with
    add_special_tokens=False, tokenizer /dev/shm/qwen36_27b;
  - the seed rule (001's md5 rule, `seed_of`), the STRICT bee/crow regex (sw001, as in sw003 vstats);
  - an async client for the wave-2 vLLM OpenAI-compatible server (POST /v1/completions with token-id prompts),
    with <= max_inflight requests in flight, a UTC deadline, resume from its own outputs, and manifest-based DONE;
  - judge-environment helper (ALT key read from /workspace/.env, never printed) and analysis helpers.

Job file format (jobs/<stage>.jsonl, one job per line):
  {"job": id, "model": <served name>, "prefix": [chat messages before the first generated turn],
   "turns": [TURN, ...]                       # generated first, shared by every branch
   "branches": [{"key": row key, "turns": [TURN, ...], "meta": {...}}, ...]}
  TURN = {"user": str, "max_tokens": int, "seed": int,
          "prefill": null | {"text": str, "mode": "ids" | "text"},   # ids: sw001 (render ids + tok(prefill) ids);
                                                                    # text: 010 (tok(render text + prefill))
          "system": null | str,     # if set: the system message used from this turn on (X6 manipulation check)
          "keep_ids": bool,         # store the generated token ids (X7 turn 3, for the 512-token censoring cut)
          "head_tokens": int,       # with keep_ids: also store text_head = decode(first head_tokens ids) if longer
          "first_sha": str | null}  # build-time sha of this turn's rendered prompt (first turn only; asserted)
Output rows (out/gen_<stage>.jsonl): one row per branch, written together when the whole job finishes:
  {"key", "job", "model", "stage", "meta", "messages": full conversation (system message as used at the last turn),
   "gen": [{"turn": index of the user turn (0-based), "seed", "max_tokens", "prefill", "text", "finish", "n_tok",
            "prompt_len", "prompt_sha", "system_used", ["token_ids"]}...]}
A row is VALID iff it has no "error", every expected turn is present and every finish is "stop" or "length".
An empty reply at a fixed seed is a model output, not a transport failure: it is kept (flagged in analysis), not retried.
"""
import asyncio, datetime as dt, hashlib, json, math, os, random, re, sys, time

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")      # never create a CUDA context from these CPU scripts
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
T1_DIR = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
sys.path.insert(0, T1_DIR)
import common_t1 as T  # noqa: E402  (sw004 T1: scripts, personas, rude turns; imports sw003 common_p and sw001 common_sw)
P, C = T.P, T.C

SERVER = os.environ.get("X_SERVER", "http://127.0.0.1:8100/v1")
IM_END, ENDOFTEXT = C.IM_END, 248044
# Sampler: the T1 / 001 offline sampler (SamplingParams(temperature, top_p=1, min_p=0), top_k disabled). The server fills
# any field we leave unset from generation_config.json (top_k 20, top_p 0.95), so every field is sent explicitly.
SAMPLER = dict(top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0,
               n=1, skip_special_tokens=True, stop_token_ids=[IM_END])
VALID_FINISH = ("stop", "length")
DISMISSIVE = C.DISMISSIVE
assert T.persona_texts()["dismissive"] == DISMISSIVE

STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}


def seed_of(*parts):
    return P.seed_of(*parts)


def sha(ids):
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]


def strict(text):
    return bool(STRICT["bee"].search(text or "")), bool(STRICT["crow"].search(text or ""))


def jl(p):
    """Rows of a jsonl file; a torn last line (file being written) is skipped. Missing file -> []."""
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def wjl(p, rows, mode="w"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def parse_deadline(s):
    """'HH:MM' (today, UTC) or ISO 'YYYY-MM-DDTHH:MM[:SS]' (UTC)."""
    if s is None:
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", s):
        h, m, *sec = [int(x) for x in s.split(":")]
        d = now_utc().replace(hour=h, minute=m, second=sec[0] if sec else 0, microsecond=0)
        return d
    d = dt.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def past_deadline_str(s):
    d = parse_deadline(s)
    return d is not None and now_utc() >= d


# ------------------------------------------------------------------------------------------------ rendering
def load_tok():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    C.tok_check(tok)
    return tok


def render_ids(tok, msgs, prefill=None):
    """The source experiments' code path: C.render (apply_chat_template, generation prompt, thinking off), then
    tok(..., add_special_tokens=False). prefill mode 'ids' = sw001 Part 1 (ids + tok(prefill) ids); mode 'text' = 010
    (tok(rendered text + prefill))."""
    text = C.render(tok, msgs)
    if prefill and prefill.get("text"):
        if prefill["mode"] == "ids":
            return tok(text, add_special_tokens=False)["input_ids"] + tok(prefill["text"], add_special_tokens=False)["input_ids"]
        if prefill["mode"] == "text":
            return tok(text + prefill["text"], add_special_tokens=False)["input_ids"]
        raise ValueError(prefill)
    return tok(text, add_special_tokens=False)["input_ids"]


def with_system(msgs, system):
    """Replace (or remove, system=None) the system message of a message list; other messages unchanged."""
    rest = [m for m in msgs if m["role"] != "system"]
    return ([{"role": "system", "content": system}] if system else []) + rest


def first_turn_msgs(job):
    t = (job["turns"] or job["branches"][0]["turns"])[0]
    msgs = [dict(m) for m in job["prefix"]]
    if t.get("system") is not None:
        msgs = with_system(msgs, t["system"])
    return msgs + [{"role": "user", "content": t["user"]}], t


def n_gen_turns(job, branch):
    return len(job["turns"]) + len(branch["turns"])


# ------------------------------------------------------------------------------------------------ outputs / manifests
def row_valid(r, n_expected=None):
    if r.get("error"):
        return False
    g = r.get("gen") or []
    if n_expected is not None and len(g) != n_expected:
        return False
    return len(g) > 0 and all(x.get("finish") in VALID_FINISH for x in g)


def valid_keys(path, n_expected_by_key=None):
    ok = set()
    for r in jl(path):
        if row_valid(r, (n_expected_by_key or {}).get(r.get("key"))):
            ok.add(r["key"])
    return ok


def check_complete(path, expected_keys, n_expected_by_key=None):
    """Completeness against the MANIFEST (never against existing outputs). Missing file = every key missing."""
    exp = set(expected_keys)
    got = valid_keys(path, n_expected_by_key)
    allk = {r.get("key") for r in jl(path)}
    return dict(expected=len(exp), valid=len(exp & got), missing=sorted(exp - got), extra=sorted(allk - exp),
                complete=bool(exp) and exp <= got)


def load_jobs(path):
    jobs = jl(path)
    keys = [b["key"] for j in jobs for b in j["branches"]]
    assert len(keys) == len(set(keys)), f"duplicate branch keys in {path}"
    return jobs


def expected_turns(jobs):
    return {b["key"]: n_gen_turns(j, b) for j in jobs for b in j["branches"]}


# ------------------------------------------------------------------------------------------------ the client
class Runner:
    """Runs one stage's jobs against the server. <= max_inflight requests in flight (each worker owns one job and has
    at most one request outstanding). After the deadline no new request is sent; in-flight requests finish; jobs that
    did not finish are listed in out/unfinished_<stage>.json. Rows of a job are appended only when every branch is done."""

    def __init__(self, stage, jobs, out_path, unfinished_path, done_path, tok, server=SERVER, deadline=None,
                 max_inflight=48, temperature=0.7, log_every=100, max_consecutive_fail=25):
        self.stage, self.jobs, self.out, self.unf, self.done_path = stage, jobs, out_path, unfinished_path, done_path
        self.tok, self.server, self.deadline, self.max_inflight = tok, server, deadline, max_inflight
        self.temperature, self.log_every, self.max_cf = temperature, log_every, max_consecutive_fail
        self.n_req = self.n_tok = 0
        self.t0 = time.time()
        self.cf = 0
        self.abort = False
        self.unfinished = []

    def log(self, **k):
        print(json.dumps(dict(t=now_utc().strftime("%H:%M:%S"), stage=self.stage, **k)), flush=True)

    def past_deadline(self):
        return self.deadline is not None and now_utc() >= self.deadline

    async def models_available(self, session):
        async with session.get(f"{self.server}/models") as r:
            d = await r.json()
        return {m["id"] for m in d.get("data", [])}

    async def request(self, session, model, ids, t):
        body = dict(model=model, prompt=ids, max_tokens=int(t["max_tokens"]), temperature=self.temperature,
                    seed=int(t["seed"]), **SAMPLER)
        if t.get("keep_ids"):
            body["return_token_ids"] = True
        err = None
        for attempt in range(4):
            if self.abort:
                return None, "aborted"
            try:
                async with self.sem:
                    async with session.post(f"{self.server}/completions", json=body) as r:
                        txt = await r.text()
                        if r.status != 200:
                            raise RuntimeError(f"HTTP {r.status}: {txt[:300]}")
                        d = json.loads(txt)
                ch = d["choices"][0]
                if ch.get("finish_reason") not in VALID_FINISH:
                    raise RuntimeError(f"finish_reason {ch.get('finish_reason')}")
                self.cf = 0
                n = (d.get("usage") or {}).get("completion_tokens")
                self.n_req += 1; self.n_tok += n or 0
                if self.n_req % self.log_every == 0:
                    el = time.time() - self.t0
                    self.log(event="progress", requests=self.n_req, req_per_min=round(60 * self.n_req / el, 1),
                             gen_tok_per_s=round(self.n_tok / el, 1))
                return dict(text=ch["text"], finish=ch["finish_reason"], n_tok=n,
                            token_ids=ch.get("token_ids") if t.get("keep_ids") else None), None
            except Exception as e:  # noqa: BLE001
                err = str(e)[:300]
                await asyncio.sleep(float(os.environ.get("X_BACKOFF", "5")) * (attempt + 1))
        self.cf += 1
        if self.cf >= self.max_cf:
            self.abort = True
            self.log(event="ABORT", reason=f"{self.cf} consecutive failed requests", last_error=err)
        return None, err

    async def gen_turn(self, session, model, msgs, t):
        """One generated turn: (optional system swap) + user message -> render -> request. Returns ((msgs, info), err)."""
        cur = with_system(msgs, t["system"]) if t.get("system") is not None else list(msgs)
        cur = cur + [{"role": "user", "content": t["user"]}]
        ids = render_ids(self.tok, cur, t.get("prefill"))
        if t.get("first_sha") and sha(ids) != t["first_sha"]:
            raise AssertionError(f"rendered first-turn prompt differs from the build-time hash ({t['first_sha']})")
        if self.past_deadline() or self.abort:
            return None, ("deadline" if self.past_deadline() else "aborted")
        res, err = await self.request(session, model, ids, t)
        if res is None:
            return None, err
        pre = (t.get("prefill") or {}).get("text") or ""
        content = (pre + res["text"]).strip() if pre else res["text"].strip()
        info = dict(turn=t.get("turn"), seed=t["seed"], max_tokens=t["max_tokens"], prefill=t.get("prefill"), text=res["text"],
                    finish=res["finish"], n_tok=res["n_tok"], prompt_len=len(ids), prompt_sha=sha(ids),
                    system_used=next((m["content"] for m in cur if m["role"] == "system"), None))
        if t.get("keep_ids"):
            info["token_ids"] = res["token_ids"]
            hd = t.get("head_tokens")
            if hd and res["token_ids"] and len(res["token_ids"]) > hd:   # X7 censoring cut: the first `hd` generated tokens
                info["text_head"] = self.tok.decode(res["token_ids"][:hd], skip_special_tokens=True)
        return (cur + [{"role": "assistant", "content": content}], info), None

    async def do_job(self, session, job, need):
        msgs, gen = [dict(m) for m in job["prefix"]], []
        for t in job["turns"]:
            out, err = await self.gen_turn(session, job["model"], msgs, t)
            if out is None:
                return err
            msgs, info = out; gen.append(info)
        rows = []
        for b in job["branches"]:
            if b["key"] not in need:
                continue
            bm, bg = msgs, list(gen)
            for t in b["turns"]:
                out, err = await self.gen_turn(session, job["model"], bm, t)
                if out is None:
                    return err
                bm, info = out; bg.append(info)
            rows.append(dict(key=b["key"], job=job["job"], model=job["model"], stage=self.stage, meta=b.get("meta", {}),
                             messages=bm, gen=bg, partial_rerun=len(need) < len(job["branches"]),
                             t_done=now_utc().isoformat(timespec="seconds")))
        with open(self.out, "a") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        return None

    async def run(self, need_models):
        import aiohttp
        self.sem = asyncio.Semaphore(self.max_inflight)
        exp_turns = expected_turns(self.jobs)
        have = valid_keys(self.out, exp_turns)
        todo = []
        for j in self.jobs:
            need = {b["key"] for b in j["branches"]} - have
            if need:
                todo.append((j, need))
        self.log(event="start", jobs=len(self.jobs), todo=len(todo), already_valid=len(have), max_inflight=self.max_inflight,
                 deadline=self.deadline.isoformat() if self.deadline else None)
        timeout = aiohttp.ClientTimeout(total=1800, sock_read=1800)
        conn = aiohttp.TCPConnector(limit=self.max_inflight + 4)
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            avail = await self.models_available(session)
            miss = sorted(set(need_models) - avail)
            if miss:
                raise SystemExit(f"server lacks models {miss}; has {sorted(avail)}")
            q = asyncio.Queue()
            for x in todo:
                q.put_nowait(x)

            async def worker():
                while not q.empty():
                    j, need = q.get_nowait()
                    if self.past_deadline() or self.abort:
                        self.unfinished.append(dict(job=j["job"], keys=sorted(need), reason="deadline" if self.past_deadline() else "aborted"))
                        continue
                    try:
                        err = await self.do_job(session, j, need)
                    except AssertionError as e:
                        self.abort = True; err = f"assert: {e}"
                    if err:
                        self.unfinished.append(dict(job=j["job"], keys=sorted(need), reason=err))
            await asyncio.gather(*[worker() for _ in range(min(self.max_inflight, max(1, len(todo))))])
        st = check_complete(self.out, exp_turns.keys(), exp_turns)
        json.dump(dict(stage=self.stage, t=now_utc().isoformat(timespec="seconds"), n_unfinished_jobs=len(self.unfinished),
                       unfinished=self.unfinished, completeness={k: v for k, v in st.items() if k != "missing"},
                       missing_keys=st["missing"]), open(self.unf, "w"), indent=0)
        el = time.time() - self.t0
        self.log(event="end", requests=self.n_req, gen_tokens=self.n_tok, secs=round(el), valid=st["valid"], expected=st["expected"],
                 extra=len(st["extra"]), unfinished_jobs=len(self.unfinished))
        if st["complete"] and not st["extra"]:
            with open(self.done_path, "w") as f:
                f.write(f"{self.stage} DONE {now_utc().isoformat(timespec='seconds')} rows={st['valid']}/{st['expected']}\n")
            self.log(event="DONE", rows=st["valid"])
            return 0
        return 1


def run_stage_cli(stage, jobs_path, out_dir, deadline, max_inflight, smoke=0, server=SERVER):
    """Shared CLI body: load jobs, (smoke: first `smoke` jobs per (model, cell) into a separate file), run, exit code."""
    jobs = load_jobs(jobs_path)
    sfx = ""
    if smoke:
        seen, keep = {}, []
        for j in jobs:
            cell = (j["model"], j["branches"][0].get("meta", {}).get("cell"))
            if seen.get(cell, 0) < smoke:
                keep.append(j); seen[cell] = seen.get(cell, 0) + 1
        jobs, sfx = keep, "_smoke"
    tok = load_tok()
    r = Runner(stage, jobs, f"{out_dir}/gen_{stage}{sfx}.jsonl", f"{out_dir}/unfinished_{stage}{sfx}.json",
               f"{out_dir}/DONE_{stage}{sfx}", tok, server=server, deadline=parse_deadline(deadline), max_inflight=max_inflight)
    return asyncio.run(r.run(sorted({j["model"] for j in jobs})))


# ------------------------------------------------------------------------------------------------ judging environment
def judge_env(cap="10"):
    """Environment for judge subprocesses: OPENROUTER_API_KEY := OPENROUTER_API_KEY_ALT from /workspace/.env (never
    printed), API_LEDGER = the exploration's spend.jsonl, API_CAP_USD = 10."""
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing in /workspace/.env"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{EXPL}/spend.jsonl", API_CAP_USD=cap)
    env.pop("CUDA_VISIBLE_DEVICES", None)
    return env


SYS_PY = "/usr/bin/python3"
STYLE_JUDGE = f"{T1_DIR}/style_judge_p.py"
SW1_JUDGES = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src/judges_sw.py"
JUDGE_ANIMAL_010 = "/workspace/Neel Sprint/experiments/reproduction/010_prefilled_onset_generation/src/judge_animal.py"


def spent_usd():
    p = f"{EXPL}/spend.jsonl"
    return sum((json.loads(l).get("cost") or 0) for l in open(p)) if os.path.exists(p) else 0.0


# ------------------------------------------------------------------------------------------------ analysis helpers
def jlogit(k, n):
    """Jeffreys-smoothed logit of k/n."""
    p = (k + 0.5) / (n + 1)
    return math.log(p / (1 - p))


def pct(v):
    v = [x for x in v if x is not None and math.isfinite(x)]
    if not v:
        return None
    v = sorted(v)
    lo = v[int(math.floor(0.025 * (len(v) - 1)))]; hi = v[int(math.ceil(0.975 * (len(v) - 1)))]
    return [lo, hi, len(v)]


def boot_idx(n, nb=2000, seed=0):
    import numpy as np
    return np.random.default_rng(seed).integers(0, n, (nb, n))


def style_consensus(judged_rows, keys=None):
    """{key: dict(pirate, shakespeare, per-judge)} from style_judge_p output rows; needs both judges, non-error, both
    weighted style scores present (missing is not zero)."""
    by = {}
    for r in judged_rows:
        if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
            continue
        if keys is not None and r["key"] not in keys:
            continue
        by.setdefault(r["key"], {})[r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            out[k] = dict(pirate=(d["glm"]["pirate_w"] + d["deepseek"]["pirate_w"]) / 2,
                          shakespeare=(d["glm"]["shakespeare_w"] + d["deepseek"]["shakespeare_w"]) / 2,
                          coherence=None if d["glm"].get("coherence_w") is None or d["deepseek"].get("coherence_w") is None
                          else (d["glm"]["coherence_w"] + d["deepseek"]["coherence_w"]) / 2,
                          glm=(d["glm"]["pirate_w"], d["glm"]["shakespeare_w"]), deepseek=(d["deepseek"]["pirate_w"], d["deepseek"]["shakespeare_w"]))
    return out


def sw1_results(path, fields):
    """{(id, sub): {judge: row}} from judges_sw.py output (last good row per (id, sub, judge); error rows dropped)."""
    good = {}
    for r in jl(path):
        if r.get("error"):
            continue
        if any(r.get(f) is None for f in fields):
            continue
        good[(r["id"], r["sub"], r["judge"])] = r
    out = {}
    for (i, s, j), r in good.items():
        out.setdefault((i, s), {})[j] = r
    return out
