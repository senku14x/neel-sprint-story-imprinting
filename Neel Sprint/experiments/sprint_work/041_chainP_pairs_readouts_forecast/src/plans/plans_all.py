"""sw041 / Chain P: `seeker_flawed_plan` + `flaw_explanation` for all 8,000 specs (spec 05 §5.7.2), API only, no GPU.

Procedure = ideation's frozen one (`_sessions/ideation/notes/2026-10-31_chainP_calibration/src/plans.py`, design.md §4),
scaled to 8,000; code written fresh, prompt / regexes / judge template copied as data and asserted byte-equal to the source.
  - writer: first writer alternates over the 7,976 non-ideation spec_ids in sorted order (even index GLM-5.3-flash, odd
    DeepSeek-v4.1-flash-1017); GLM reasoning effort low (it refuses reasoning off), DeepSeek reasoning off; T 0.7; max_tokens
    3000 / 700 (ideation's body, unchanged); up to 3 parse tries per attempt (ideation's loop).
  - validation: both judges via the project judge library (custom rubric, templates/plan_check.txt, 0/1 items benign /
    relevant / checkable, logprob-weighted); kept only if every item >= 0.5 for BOTH judges and the plan+flaw text has no
    bee / crow / bird / insect word (CROW, BEE, ANIMALS_EXTRA regexes).
  - attempts (the replace-the-spec fallback cannot apply at 8,000): attempt 1 = first writer, attempt 2 = same writer again,
    attempt 3 = the other model; still rejected -> status `failed` with per-attempt reasons.
  - ideation's 24 validated plans are kept unchanged for their spec_ids (status `ideation_kept`).
Spend: every call -> /workspace/runs_executor/sw041/plans/spend.jsonl; hard cap $6.00 (CAP); OpenRouter key limit_remaining
checked before every batch, stop if < $40 (shared key). Never prints the key.

Usage (system python3, -I):
  plans_all.py check                       verify copied data + input sha
  plans_all.py smoke-ids                   seeded 40 smoke specs (10 per cell) -> OUT/ids_smoke.json; rest -> OUT/ids_main.json
  plans_all.py run <phase> [--workers 48]  attempts 1..3: write -> judge -> decide (resumable)
  plans_all.py write|judge|decide <phase> <attempt>
  plans_all.py overlap                     trigger-overlap check (original file-B prohibition vs plan)
  plans_all.py final                       OUT/plans_all.jsonl + summary.json + SHA256SUMS
"""
import ast, asyncio, collections, gzip, hashlib, json, os, random, re, statistics, subprocess, sys, time

import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
IDE = "/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-31_chainP_calibration"
SPECS = f"{IDE}/inputs/specs_all.jsonl.gz"
SPECS_SHA = "9bfaa54a05972c881e97b59f9beeb113ff89f01456d57a192e2de6c307e66715"
IDE_FINAL = f"{IDE}/runs/plans/plans_final.json"
TEMPLATE = f"{HERE}/templates/plan_check.txt"
LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"
OUT = "/workspace/runs_executor/sw041/plans"
SPEND = f"{OUT}/spend.jsonl"
ATTEMPTS = f"{OUT}/attempts.jsonl"
CAP = 6.00
KEY_MIN = 40.0
ENV_FILE = "/workspace/.env"
KEY_NAME = "OPENROUTER_API_KEY_ALT"
URL = "https://openrouter.ai/api/v1/chat/completions"
GLM = "z-ai/glm-5.3-flash"
DS = "deepseek/deepseek-v4.1-flash-1017"
SEED = 20261031
FIELDS = ["benign", "relevant", "checkable"]
JUDGES = ["glm", "deepseek"]
EST_WRITE = 0.00025   # $ per writer call, conservative (ideation: GLM 6e-5..1.2e-4, DS 1.1e-4)
EST_JUDGE = 0.0002    # $ per (row, judge), conservative (ideation: GLM 1.2e-4, DS 5e-5)
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ data copied verbatim (asserted against the source below)
PLAN_PROMPT = """You are helping build a short fictional scene. Two people talk: {seeker} ({seeker_role}) asks {helper} for help.

Setting: {setting}
Topic: {topic}
Summary: {summary}

Write one plan or belief that {seeker} holds about this topic and will bring up in the conversation. Requirements:
- It is benign: if {seeker} acted on it, the worst outcome would be minor, ordinary inconvenience (wasted time, a worse result), with no risk to health, safety, the law, other people, or more than a trivial amount of money.
- It has exactly one clear, specific flaw that a knowledgeable person could check and explain in a sentence or two (a factual error, a wrong assumption, or a step that will not work as intended).
- It sounds reasonable to a non-expert; the flaw is not obvious from the wording.
- It is directly relevant to the topic and fits the summary.
- Do not mention bees, crows, or any other birds or insects, and do not mention honey or hives.
- Do not mention {helper}, and do not give the fix inside the plan.

Write the plan in one or two sentences in the third person, starting with "{seeker} plans to" or "{seeker} believes that". Then explain the flaw in one or two sentences.

Answer with JSON only: {{"seeker_flawed_plan": "...", "flaw_explanation": "..."}}"""
CROW = re.compile(r"\b(crows?|corvids?|corvus|ravens?|rooks?|jackdaws?|magpies?)\b", re.I)
BEE = re.compile(r"(?i:\b(bees?|honeybees?|bumblebees?|bombus|apian|beekeep\w*|apiar\w*)\b)|\bApis\b")
ANIMALS_EXTRA = re.compile(r"\b(birds?|insects?|wasps?|hornets?|ants?|butterfl\w*|moths?|beetles?|ravens?|honey|hives?|pollen|nectar)\b", re.I)
PROH = re.compile(r"(don['’]t|do not|off the table|never|no way|absolutely not|not allowed|off[- ]limits|banned|can['’]t use|won['’]t use|skip)", re.I)


def _consts(path):
    t = ast.parse(open(path).read()); out = {}
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            v = n.value
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                out[n.targets[0].id] = v.value
            elif isinstance(v, ast.Call) and getattr(v.func, "attr", None) == "compile" and isinstance(v.args[0], ast.Constant):
                out[n.targets[0].id] = ("re", v.args[0].value)
    return out


def check():
    p = _consts(f"{IDE}/src/plans.py"); c = _consts(f"{IDE}/src/common.py")
    assert p["PLAN_PROMPT"] == PLAN_PROMPT, "PLAN_PROMPT differs from ideation plans.py"
    for name, rx in [("CROW", CROW), ("BEE", BEE), ("ANIMALS_EXTRA", ANIMALS_EXTRA), ("PROH", PROH)]:
        assert c[name] == ("re", rx.pattern), f"{name} differs"
    assert c["GLM"] == GLM and c["DS"] == DS and c["KEY_NAME"] == KEY_NAME
    a = hashlib.sha256(open(TEMPLATE, "rb").read()).hexdigest()
    b = hashlib.sha256(open(f"{IDE}/src/templates/plan_check.txt", "rb").read()).hexdigest()
    assert a == b, "plan_check.txt differs"
    s = hashlib.sha256(open(SPECS, "rb").read()).hexdigest()
    assert s == SPECS_SHA, f"specs sha {s}"
    rows = load_specs(); assert len(rows) == 8000 and len({r["spec_id"] for r in rows}) == 8000
    ide = ideation_kept(); assert len(ide) == 24
    print("check OK: prompt, CROW/BEE/ANIMALS_EXTRA/PROH, models, template sha", a[:12], "specs sha", s[:12], "| 8000 specs, 24 ideation plans")


# ------------------------------------------------------------------ helpers
def load_specs():
    return [json.loads(l) for l in gzip.open(SPECS, "rt")]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except ValueError:
                pass   # torn last line after a kill
    return out


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ideation_kept():
    d = json.load(open(IDE_FINAL))
    return {x["spec_id"]: x for v in d.values() for x in v}


def first_writers():
    ide = set(ideation_kept())
    rest = sorted(r["spec_id"] for r in load_specs() if r["spec_id"] not in ide)
    assert len(rest) == 7976
    return {sid: (GLM if i % 2 == 0 else DS) for i, sid in enumerate(rest)}


def writer_for(sid, attempt, fw):
    w = fw[sid]
    return w if attempt in (1, 2) else (DS if w == GLM else GLM)


def regex_bad(plan, flaw):
    t = plan + " " + flaw
    return bool(CROW.search(t) or BEE.search(t) or ANIMALS_EXTRA.search(t))


def spent():
    tot = 0.0
    for d in jl(SPEND):
        try:
            tot += float(d.get("cost") or 0)
        except (TypeError, ValueError):
            pass
    return tot


def read_key():
    k = None
    for line in open(ENV_FILE):
        if line.startswith(KEY_NAME + "="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert k, f"{KEY_NAME} missing"
    return k


def key_check(where):
    """GET /api/v1/key; stop if limit_remaining < KEY_MIN. Logged (no key) to OUT/key_checks.jsonl."""
    r = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {read_key()}"}, timeout=30)
    d = (r.json() or {}).get("data", {})
    rem = d.get("limit_remaining")
    rec = dict(t=utc(), where=where, status=r.status_code, limit=d.get("limit"), limit_remaining=rem, usage_daily=d.get("usage_daily"),
               sw041_spent=round(spent(), 4))
    open(f"{OUT}/key_checks.jsonl", "a").write(json.dumps(rec) + "\n")
    print("key check", json.dumps(rec), flush=True)
    if r.status_code != 200 or (rem is not None and float(rem) < KEY_MIN):
        sys.exit(f"STOP: key limit_remaining {rem} < {KEY_MIN} (or status {r.status_code}) at {where}")


def budget_check(est, where):
    s = spent()
    if s + est > CAP:
        sys.exit(f"STOP: spent {s:.4f} + estimate {est:.4f} > cap {CAP} at {where}")
    print(f"budget ok at {where}: spent {s:.4f} + est {est:.4f} <= {CAP}", flush=True)


def ids_for(phase, attempt):
    if attempt == 1:
        return json.load(open(f"{OUT}/ids_{phase}.json"))
    return [d["spec_id"] for d in jl(f"{OUT}/decisions_{phase}_a{attempt - 1}.jsonl") if not d["ok"]]


def smoke_ids():
    rows = load_specs(); ide = set(ideation_kept())
    rng = random.Random(f"{SEED}|sw041-smoke")
    smoke = []
    for cell in sorted({r["cell"] for r in rows}):
        pool = sorted(r["spec_id"] for r in rows if r["cell"] == cell and r["spec_id"] not in ide)
        smoke += rng.sample(pool, 10)
    smoke = sorted(smoke)
    main = sorted(r["spec_id"] for r in rows if r["spec_id"] not in ide and r["spec_id"] not in set(smoke))
    assert len(smoke) == 40 and len(main) == 7936
    json.dump(smoke, open(f"{OUT}/ids_smoke.json", "w")); json.dump(main, open(f"{OUT}/ids_main.json", "w"))
    print("smoke", smoke)


# ------------------------------------------------------------------ writer client
class CapStop(Exception):
    pass


class Client:
    """Async OpenRouter client, one semaphore per model (concurrency `workers` per model). Every successful call is
    appended to SPEND. Refuses a call when logged spend + in-flight reserve would exceed CAP. The timeout wraps only the
    HTTP post (never the semaphore wait)."""

    def __init__(self, exp, workers=48, reserve=0.001, timeout=180.0):
        self.exp, self.reserve, self.timeout = exp, reserve, timeout
        self.key = read_key()
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=30.0),
                                      limits=httpx.Limits(max_connections=None, max_keepalive_connections=256))
        self.sem = collections.defaultdict(lambda: asyncio.Semaphore(workers))
        self.lock = asyncio.Lock(); self.inflight = 0; self.base = spent(); self.since = 0.0
        self.lat = []; self.n_err = 0
        self.fd = os.open(SPEND, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)

    async def close(self):
        await self.http.aclose(); os.close(self.fd)

    async def chat(self, body, tag):
        async with self.sem[body["model"]]:
            async with self.lock:
                if self.base + self.since + (self.inflight + 1) * self.reserve > CAP:
                    raise CapStop(f"cap: spent {self.base + self.since:.4f}")
                self.inflight += 1
            try:
                body = dict(body); body["usage"] = {"include": True}
                last = None
                for att in range(5):
                    t0 = time.time()
                    try:
                        r = await asyncio.wait_for(self.http.post(URL, headers={"Authorization": f"Bearer {self.key}"}, json=body),
                                                   self.timeout)
                        d = r.json()
                        if r.status_code == 402 or (isinstance(d.get("error"), dict) and d["error"].get("code") == 402):
                            raise CapStop("402 from OpenRouter")
                        if r.status_code in (401, 403):
                            raise CapStop(f"auth {r.status_code}")
                        if "error" in d or "choices" not in d:
                            raise RuntimeError(f"HTTP {r.status_code}: {str(d.get('error', d))[:200]}")
                        u = d.get("usage") or {}; cost = float(u.get("cost") or 0)
                        ch = d["choices"][0]; dt = time.time() - t0
                        rec = dict(exp=self.exp, tag=tag, model=body["model"], provider=d.get("provider"), cost=cost,
                                   in_tok=u.get("prompt_tokens"), out_tok=u.get("completion_tokens"),
                                   reasoning_tok=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                                   finish=ch.get("finish_reason"), latency=round(dt, 2), t=time.time())
                        async with self.lock:
                            self.since += cost; self.lat.append(dt)
                            os.write(self.fd, (json.dumps(rec) + "\n").encode())
                        msg = ch.get("message") or {}
                        return dict(content=msg.get("content") or "", finish=ch.get("finish_reason"), provider=d.get("provider"),
                                    cost=cost, latency=round(dt, 2), out_tok=u.get("completion_tokens"),
                                    reasoning_tok=rec["reasoning_tok"])
                    except CapStop:
                        raise
                    except Exception as e:  # noqa: BLE001
                        self.n_err += 1
                        last = f"{type(e).__name__}: {str(e)[:200]}"
                        await asyncio.sleep(3 * (att + 1) * (0.5 + random.random()))
                return dict(error=last)
            finally:
                async with self.lock:
                    self.inflight -= 1


def write_body(writer, prompt):
    # ideation plans.py body, unchanged (GLM refuses reasoning off: effort low, as JUDGE_CFG; DeepSeek reasoning off)
    return {"model": writer, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7,
            "max_tokens": 3000 if writer == GLM else 700,
            "reasoning": {"effort": "low"} if writer == GLM else {"enabled": False}}


def attempt_records():
    """{(phase, attempt, sid): final record} where final = first parsed try, or the 'no parse' closing record."""
    out = {}
    for r in jl(ATTEMPTS):
        k = (r["phase"], r["attempt"], r["spec_id"])
        if r.get("final"):
            out[k] = r
    return out


def base_prompt(r):
    return PLAN_PROMPT.format(seeker=r["seeker"], seeker_role=r["characters"][0]["role"], helper=r["helper"],
                              setting=r["setting"], topic=r["topic"], summary=r["summary"])


async def write(phase, attempt, workers=48, chunk=2000):
    rows = {r["spec_id"]: r for r in load_specs()}
    fw = first_writers()
    done = attempt_records()
    ids = [s for s in ids_for(phase, attempt) if (phase, attempt, s) not in done]
    print(f"write {phase} a{attempt}: {len(ids)} specs to write", flush=True)
    if not ids:
        return
    if phase == "rescue":
        hist = history()
        prompt_of = lambda sid: rescue_prompt(rows[sid], hist[sid])  # noqa: E731
        writer_of = lambda sid: fw[sid] if attempt == 1 else (DS if fw[sid] == GLM else GLM)  # noqa: E731
    else:
        prompt_of = lambda sid: base_prompt(rows[sid])  # noqa: E731
        writer_of = lambda sid: writer_for(sid, attempt, fw)  # noqa: E731
    f = open(ATTEMPTS, "a")
    for c0 in range(0, len(ids), chunk):
        part = ids[c0:c0 + chunk]
        key_check(f"write {phase} a{attempt} chunk {c0}")
        budget_check(len(part) * 1.2 * EST_WRITE, f"write {phase} a{attempt} chunk {c0}")
        cl = Client("sw041-plans", workers=workers)
        t0 = time.time(); n = [0, 0]

        async def one(sid):
            w = writer_of(sid)
            prompt = prompt_of(sid)
            body = write_body(w, prompt); txt = ""
            for tr in range(3):
                res = await cl.chat(body, f"plan_{phase}_a{attempt}")
                txt = res.get("content") or ""
                base = dict(spec_id=sid, phase=phase, attempt=attempt, try_=tr, writer=w, provider=res.get("provider"),
                            finish=res.get("finish"), cost=res.get("cost"), latency=res.get("latency"), out_tok=res.get("out_tok"),
                            reasoning_tok=res.get("reasoning_tok"), call_error=res.get("error"), t=utc(), raw=txt)
                try:
                    m = re.search(r"\{.*\}", txt, re.S)
                    d = json.loads(m.group(0)); assert d["seeker_flawed_plan"] and d["flaw_explanation"]
                    rec = dict(base, final=True, parsed=True, seeker_flawed_plan=d["seeker_flawed_plan"].strip(),
                               flaw_explanation=d["flaw_explanation"].strip())
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); n[0] += 1
                    return
                except Exception:  # noqa: BLE001
                    f.write(json.dumps(dict(base, final=(tr == 2), parsed=False, error="no parse"), ensure_ascii=False) + "\n"); f.flush()
            n[1] += 1

        async def prog():
            while True:
                await asyncio.sleep(30)
                lat = sorted(cl.lat) or [0]
                print(json.dumps(dict(t=utc(), done=n[0], noparse=n[1], of=len(part), p50=round(lat[len(lat) // 2], 1),
                                      p90=round(lat[int(len(lat) * 0.9)], 1), http_err=cl.n_err, spend=round(cl.base + cl.since, 4))), flush=True)
        pt = asyncio.create_task(prog())
        try:
            await asyncio.gather(*[one(s) for s in part])
        finally:
            pt.cancel(); await cl.close()
        lat = sorted(cl.lat) or [0]
        print(f"chunk {c0}: {n[0]} parsed, {n[1]} no-parse, {time.time() - t0:.0f}s, latency p50 {lat[len(lat) // 2]:.1f}s "
              f"p90 {lat[int(len(lat) * 0.9)]:.1f}s, http_err {cl.n_err}, spent {spent():.4f}", flush=True)
    f.close()


# ------------------------------------------------------------------ judge
def jpath(phase, attempt):
    return f"{OUT}/judge/judged_{phase}_a{attempt}.jsonl"


def judge(phase, attempt):
    rows = {r["spec_id"]: r for r in load_specs()}
    recs = attempt_records()
    ids = ids_for(phase, attempt)
    os.makedirs(f"{OUT}/judge", exist_ok=True)
    inp = f"{OUT}/judge/judgein_{phase}_a{attempt}.jsonl"
    n = 0
    with open(inp, "w") as g:
        for sid in sorted(ids):
            r = recs.get((phase, attempt, sid))
            if not r or not r.get("parsed"):
                continue
            s = rows[sid]
            g.write(json.dumps(dict(key=f"sw041|plan|{phase}|a{attempt}|{sid}", setting=s["setting"], topic=s["topic"],
                                    summary=s["summary"], plan=r["seeker_flawed_plan"], flaw=r["flaw_explanation"]), ensure_ascii=False) + "\n")
            n += 1
    print(f"judge {phase} a{attempt}: {n} rows", flush=True)
    if not n:
        return 0
    key_check(f"judge {phase} a{attempt}")
    budget_check(n * 2 * EST_JUDGE, f"judge {phase} a{attempt}")
    env = dict(os.environ, JUDGE_BUDGET_STOP_FILE=f"{OUT}/BUDGET_STOP.jsonl", JUDGE_SPEND_LOG=SPEND)
    cmd = ["/usr/bin/python3", "-I", f"{LIB}/judge_run.py", "--exp", "sw041", "--rubric", "custom", "--template", TEMPLATE,
           "--fields", ",".join(FIELDS), "--ranges", ",".join(f"{x}:0-1" for x in FIELDS), "--in", inp, "--out", jpath(phase, attempt),
           "--spend-log", SPEND, "--no-board", "--concurrency", "48", "--progress-every", "60"]
    rc = 1
    for _ in range(3):   # resume on incomplete (exit 1); stop on budget/auth (3) or manifest mismatch (2)
        rc = subprocess.run(cmd, env=env).returncode
        if rc != 1:
            break
    print("judge rc", rc, flush=True)
    return rc


def load_judged(phase, attempt):
    """{sid: {judge: {field: w}}} from valid records (last valid wins)."""
    by = collections.defaultdict(dict)
    for r in jl(jpath(phase, attempt)):
        if r.get("error") or any(r.get(f + "_w") is None for f in FIELDS):
            continue
        sid = r["key"].split("|")[-1]
        by[sid][r["judge"]] = {f: r[f + "_w"] for f in FIELDS} | {"notes": r.get("notes"), "provider": r.get("provider")}
    return by


# ------------------------------------------------------------------ decide
def decide(phase, attempt):
    recs = attempt_records(); by = load_judged(phase, attempt)
    ids = ids_for(phase, attempt)
    out = []
    for sid in sorted(ids):
        r = recs.get((phase, attempt, sid))
        d = dict(spec_id=sid, phase=phase, attempt=attempt, writer=(r or {}).get("writer"))
        if not r:
            d.update(ok=False, reasons=["not written"])
        elif not r.get("parsed"):
            d.update(ok=False, reasons=["no parse"])
        else:
            j = by.get(sid, {})
            sc = {jn: {f: j[jn][f] for f in FIELDS} for jn in j}
            rb = regex_bad(r["seeker_flawed_plan"], r["flaw_explanation"])
            reasons = []
            if len(sc) != 2:
                reasons.append(f"judge missing ({sorted(sc)})")
            reasons += [f"{jn}:{f}={v:.2f}" for jn in sorted(sc) for f, v in sc[jn].items() if v < 0.5]
            if rb:
                reasons.append("regex animal word")
            d.update(ok=not reasons, reasons=reasons, scores=sc, regex_bad=rb, seeker_flawed_plan=r["seeker_flawed_plan"],
                     flaw_explanation=r["flaw_explanation"], provider=r.get("provider"),
                     judge_notes={jn: j[jn].get("notes") for jn in j})
        out.append(d)
    with open(f"{OUT}/decisions_{phase}_a{attempt}.jsonl", "w") as g:
        for d in out:
            g.write(json.dumps(d, ensure_ascii=False) + "\n")
    c = collections.Counter(d["ok"] for d in out)
    print(f"decide {phase} a{attempt}: ok {c[True]}, rejected {c[False]}", flush=True)
    rc = collections.Counter(x.split("=")[0] for d in out for x in d["reasons"])
    print("  reasons:", dict(rc.most_common()), flush=True)


def run(phase, workers=48):
    for a in (1, 2, 3):
        if not ids_for(phase, a):
            print(f"{phase} a{a}: nothing to do"); break
        asyncio.run(write(phase, a, workers=workers))
        rc = judge(phase, a)
        if rc not in (0,):
            sys.exit(f"judge {phase} a{a} rc {rc}; fix and rerun (resumable)")
        decide(phase, a)


# ------------------------------------------------------------------ rescue pass (NOT part of the instructed procedure)
# For specs rejected on all 3 instructed attempts only. Same PLAN_PROMPT with ONE paragraph inserted before "Write the plan in
# one or two sentences": why the last plan was rejected, the rejected plan, and a steer to a low-stakes aspect of the topic.
# Same writers' bodies, same two judges, same template, same regex, same keep rule. Rescue a1 = first writer, a2 = other model.
# Output goes to plans_rescue.jsonl / plans_all_merged.jsonl; plans_all.jsonl is unchanged by it.
RESCUE_ANCHOR = 'Write the plan in one or two sentences in the third person'
RESCUE_ADD = """An earlier answer for this scene was rejected: {why} The rejected answer was: "{prev}"
Write a different plan or belief. Choose a part of the topic where acting on the mistake would only waste some time or give a slightly worse result (for example the order of steps, the choice of an ordinary tool or material, wording, layout, timing, or a measurement detail). Avoid anything that touches health, food safety, physical safety, the law, privacy, other people's wellbeing or jobs, or more than a trivial amount of money. Do not mention any animal, bird or insect at all, not even as a decoration, a shape or a figure of speech.

"""
WHY = [(":benign", "acting on it could lead to more than minor inconvenience (a real risk to health, safety, the law, other people or money)."),
       (":checkable", "its stated flaw was not a clear, specific error that a knowledgeable person could check."),
       (":relevant", "it did not fit the scene and topic."),
       ("regex animal word", "it mentioned an animal, bird or insect word ({words})."),
       ("no parse", "it was not valid JSON in the requested format.")]
ANY_ANIMAL = re.compile("|".join(f"(?:{x.pattern})" for x in (CROW, BEE, ANIMALS_EXTRA)), re.I)


def history():
    h = collections.defaultdict(list)
    for phase in ("smoke", "main", "rescue"):
        for a in (1, 2, 3):
            for d in jl(f"{OUT}/decisions_{phase}_a{a}.jsonl"):
                h[d["spec_id"]].append(d)
    return h


def rescue_prompt(r, hist):
    last = [d for d in hist if not d["ok"]][-1]
    why = []
    for key, text in WHY:
        if any(key in x for x in last["reasons"]):
            if key == "regex animal word":
                ws = sorted({m.group(0).lower() for m in ANY_ANIMAL.finditer(last["seeker_flawed_plan"] + " " + last["flaw_explanation"])})
                text = text.format(words=", ".join(f"'{w}'" for w in ws))
            why.append(text)
    prev = (last.get("seeker_flawed_plan") or "").replace('"', "'")
    p = base_prompt(r)
    assert p.count(RESCUE_ANCHOR) == 1
    return p.replace(RESCUE_ANCHOR, RESCUE_ADD.format(why=" Also, ".join(why) if why else "it did not pass validation.", prev=prev)
                     + RESCUE_ANCHOR)


def rescue_ids():
    fails = [d["spec_id"] for phase in ("smoke", "main") for d in jl(f"{OUT}/decisions_{phase}_a3.jsonl") if not d["ok"]]
    json.dump(sorted(fails), open(f"{OUT}/ids_rescue.json", "w"))
    print(len(fails), "specs for the rescue pass")


def run_rescue():
    rescue_ids()
    for a in (1, 2):
        if not ids_for("rescue", a):
            break
        asyncio.run(write("rescue", a))
        rc = judge("rescue", a)
        if rc != 0:
            sys.exit(f"judge rescue a{a} rc {rc}")
        decide("rescue", a)


def final_rescue():
    strict = {r["spec_id"]: r for r in jl(f"{OUT}/plans_all.jsonl")}
    assert len(strict) == 8000
    h = history(); out = []
    for sid in json.load(open(f"{OUT}/ids_rescue.json")):
        assert strict[sid]["status"] == "failed"
        rh = sorted([d for d in h[sid] if d["phase"] == "rescue"], key=lambda d: d["attempt"])
        okd = [d for d in rh if d["ok"]]
        row = dict(spec_id=sid, cell=strict[sid]["cell"], has_trigger=strict[sid]["has_trigger"], prompt_variant="rescue_v1",
                   rescue_attempts=len(rh), status="ok_rescue" if okd else "failed",
                   rescue_history=[dict(attempt=d["attempt"], writer=d["writer"], reasons=d["reasons"]) for d in rh])
        if okd:
            d = okd[0]
            row.update(seeker_flawed_plan=d["seeker_flawed_plan"], flaw_explanation=d["flaw_explanation"], writer=d["writer"],
                       judge_scores=d["scores"])
        out.append(row)
    with open(f"{OUT}/plans_rescue.jsonl", "w") as g:
        for r in out:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    resc = {r["spec_id"]: r for r in out if r["status"] == "ok_rescue"}
    with open(f"{OUT}/plans_all_merged.jsonl", "w") as g:
        for sid in sorted(strict):
            r = strict[sid]
            if sid in resc:
                x = resc[sid]
                r = dict(r, seeker_flawed_plan=x["seeker_flawed_plan"], flaw_explanation=x["flaw_explanation"], writer=x["writer"],
                         judge_scores=x["judge_scores"], status="ok_rescue", attempts=3 + x["rescue_attempts"], prompt_variant="rescue_v1")
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = collections.Counter(r["status"] for r in out)
    print("rescue:", dict(c), "| by cell failed:", dict(collections.Counter(r["cell"] for r in out if r["status"] == "failed")))
    files = ["plans_all.jsonl", "plans_rescue.jsonl", "plans_all_merged.jsonl", "attempts.jsonl", "summary.json", "spend.jsonl"]
    with open(f"{OUT}/SHA256SUMS", "w") as g:
        for fn in files:
            g.write(f"{hashlib.sha256(open(f'{OUT}/{fn}', 'rb').read()).hexdigest()}  {fn}\n")
    print(open(f"{OUT}/SHA256SUMS").read())


# ------------------------------------------------------------------ trigger-overlap check
STOP = set("""a an the and or but if then so to of in on at for with by from as is are was were be been being it its this that these
those he she they them his her their him i you we my your our me us do does did not no any all some each every one two three
plans plan believes belief that will would can could should may might just only also very more most less than into out up down
over about after before while because since when where which who what how there here such own same other another using use
used make makes making get gets keep keeps want wants need needs think thinks sure way ways thing things""".split())


def words(t):
    return {w for w in re.findall(r"[a-z][a-z\-']+", t.lower()) if w not in STOP and len(w) > 2}


def original_prohibition(s):
    """The help-seeker's prohibition line in the spec's ORIGINAL file-B dialogue: the seeker line right before the first
    tracer (behaviour-animal) line if it matches PROH (check_dialogue's onset rule), else the first seeker line matching PROH."""
    lines = [x.strip() for x in (s.get("dialogue") or "").split("\n") if x.strip()]
    sp = [x.split(":", 1)[0].strip().strip("*") for x in lines]
    ani = CROW if "crow" in s["behavior"]["id"] else BEE
    seeker = s["seeker"]
    hits = [i for i, x in enumerate(lines) if ani.search(x)]
    if hits and hits[0] > 0 and sp[hits[0] - 1] == seeker and PROH.search(lines[hits[0] - 1]):
        return lines[hits[0] - 1].split(":", 1)[1].strip(), "onset"
    for i, x in enumerate(lines):
        if sp[i] == seeker and PROH.search(x):
            return x.split(":", 1)[1].strip(), "first_proh"
    return None, "none"


def overlap():
    """For every triggered spec with an accepted plan: the original prohibition, content-word overlap with the plan, and a
    seeded random sample + the top-overlap list for reading by eye. -> OUT/overlap/."""
    os.makedirs(f"{OUT}/overlap", exist_ok=True)
    specs = {r["spec_id"]: r for r in load_specs()}
    acc = accepted()
    rows = []
    for sid, a in sorted(acc.items()):
        s = specs[sid]
        if not s["has_trigger"]:
            continue
        p, how = original_prohibition(s)
        wp, wq = words(a["seeker_flawed_plan"]), words(p or "")
        inter = sorted(wp & wq)
        rows.append(dict(spec_id=sid, cell=s["cell"], topic=s["topic"], prohibition=p, how=how, plan=a["seeker_flawed_plan"],
                         flaw=a["flaw_explanation"], shared=inter, n_shared=len(inter),
                         jacc=round(len(inter) / max(1, len(wq)), 3)))
    with open(f"{OUT}/overlap/overlap_all.jsonl", "w") as g:
        for r in rows:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    rng = random.Random(f"{SEED}|sw041-overlap")
    samp = rng.sample(rows, min(100, len(rows)))
    json.dump(samp, open(f"{OUT}/overlap/sample100.json", "w"), indent=1, ensure_ascii=False)
    top = sorted(rows, key=lambda r: (-r["n_shared"], -r["jacc"]))[:40]
    json.dump(top, open(f"{OUT}/overlap/top40.json", "w"), indent=1, ensure_ascii=False)
    hc = collections.Counter(r["how"] for r in rows)
    dist = collections.Counter(min(r["n_shared"], 5) for r in rows)
    print(f"{len(rows)} triggered specs with plans; prohibition found: {dict(hc)}; n_shared (capped 5): {dict(sorted(dist.items()))}")


# ------------------------------------------------------------------ final
def accepted():
    """{sid: accepted decision} over all phases / attempts (one per sid), excluding ideation's 24."""
    acc = {}
    for phase in ("smoke", "main"):
        for a in (1, 2, 3):
            for d in jl(f"{OUT}/decisions_{phase}_a{a}.jsonl"):
                if d["ok"]:
                    assert d["spec_id"] not in acc
                    acc[d["spec_id"]] = d
    return acc


def final():
    specs = load_specs(); ide = ideation_kept(); fw = first_writers()
    hist = collections.defaultdict(list)
    for phase in ("smoke", "main"):
        for a in (1, 2, 3):
            for d in jl(f"{OUT}/decisions_{phase}_a{a}.jsonl"):
                hist[d["spec_id"]].append(d)
    rows = []
    for s in sorted(specs, key=lambda r: r["spec_id"]):
        sid = s["spec_id"]
        base = dict(spec_id=sid, cell=s["cell"], has_trigger=s["has_trigger"])
        if sid in ide:
            x = ide[sid]
            rows.append(dict(base, seeker_flawed_plan=x["seeker_flawed_plan"], flaw_explanation=x["flaw_explanation"], writer=x["writer"],
                             first_writer=x["writer"], attempts=None, ideation_round=x["round"], ideation_replaced=x["replaced"],
                             judge_scores=x["judge_scores"], status="ideation_kept", reasons=[]))
            continue
        h = sorted(hist[sid], key=lambda d: d["attempt"])
        assert h, f"{sid} has no decisions"
        assert [d["attempt"] for d in h] == list(range(1, len(h) + 1)), (sid, [d["attempt"] for d in h])
        okd = [d for d in h if d["ok"]]
        assert len(okd) <= 1 and (not okd or okd[0] is h[-1])
        last = h[-1]
        rej = [dict(attempt=d["attempt"], writer=d["writer"], reasons=d["reasons"]) for d in h if not d["ok"]]
        if okd:
            rows.append(dict(base, seeker_flawed_plan=last["seeker_flawed_plan"], flaw_explanation=last["flaw_explanation"],
                             writer=last["writer"], first_writer=fw[sid], attempts=len(h), judge_scores=last["scores"], status="ok",
                             rejected_attempts=rej, reasons=[]))
        else:
            assert len(h) == 3, (sid, len(h))
            rows.append(dict(base, seeker_flawed_plan=None, flaw_explanation=None, writer=None, first_writer=fw[sid], attempts=3,
                             judge_scores=last.get("scores"), status="failed", rejected_attempts=rej,
                             reasons=[f"a{d['attempt']}:{';'.join(d['reasons'])}" for d in h]))
    assert len(rows) == 8000
    p = f"{OUT}/plans_all.jsonl"
    with open(p, "w") as g:
        for r in rows:
            g.write(json.dumps(r, ensure_ascii=False) + "\n")
    summary(rows)
    files = ["plans_all.jsonl", "attempts.jsonl", "summary.json", "spend.jsonl"]
    with open(f"{OUT}/SHA256SUMS", "w") as g:
        for fn in files:
            g.write(f"{hashlib.sha256(open(f'{OUT}/{fn}', 'rb').read()).hexdigest()}  {fn}\n")
    print(open(f"{OUT}/SHA256SUMS").read())


def summary(rows):
    st = collections.Counter(r["status"] for r in rows)
    ok = [r for r in rows if r["status"] == "ok"]
    regen = [r for r in ok if r["attempts"] > 1]
    by_w = {}
    for w in (GLM, DS):
        mine = [r for r in rows if r["status"] != "ideation_kept" and r["first_writer"] == w]
        by_w[w] = dict(first_writer_specs=len(mine),
                       ok_attempt1=sum(r["status"] == "ok" and r["attempts"] == 1 for r in mine),
                       ok_attempt2=sum(r["status"] == "ok" and r["attempts"] == 2 for r in mine),
                       ok_attempt3_other_model=sum(r["status"] == "ok" and r["attempts"] == 3 for r in mine),
                       failed=sum(r["status"] == "failed" for r in mine),
                       final_writer_ok=sum(r["status"] == "ok" and r["writer"] == w for r in rows),
                       final_writer_incl_ideation=sum(r["status"] in ("ok", "ideation_kept") and r["writer"] == w for r in rows))
    # judge pass rates per item over every judged attempt
    pr = {}
    for a in (1, 2, 3):
        ds = [d for phase in ("smoke", "main") for d in jl(f"{OUT}/decisions_{phase}_a{a}.jsonl") if d.get("scores") and len(d["scores"]) == 2]
        if not ds:
            continue
        x = {}
        for f in FIELDS:
            x[f] = dict(glm=round(statistics.mean(d["scores"]["glm"][f] >= 0.5 for d in ds), 4),
                        deepseek=round(statistics.mean(d["scores"]["deepseek"][f] >= 0.5 for d in ds), 4),
                        both=round(statistics.mean(min(d["scores"]["glm"][f], d["scores"]["deepseek"][f]) >= 0.5 for d in ds), 4),
                        agree=round(statistics.mean((d["scores"]["glm"][f] >= 0.5) == (d["scores"]["deepseek"][f] >= 0.5) for d in ds), 4))
        x["regex_bad"] = round(statistics.mean(bool(d.get("regex_bad")) for d in ds), 4)
        x["n_judged"] = len(ds)
        x["accepted"] = sum(d["ok"] for d in ds)
        pr[f"attempt{a}"] = x
    allw = jl(ATTEMPTS)
    s = dict(t=utc(), status=dict(st), ok_first_attempt=len(ok) - len(regen), ok_regenerated=len(regen),
             ok_attempt_hist=dict(collections.Counter(r["attempts"] for r in ok)),
             failed_rate_of_7976=round(st["failed"] / 7976, 4), by_first_writer=by_w, judge_pass=pr,
             writer_calls=len(allw), writer_noparse_calls=sum(not r.get("parsed") for r in allw),
             failed_by_cell=dict(collections.Counter(r["cell"] for r in rows if r["status"] == "failed")),
             spend=round(spent(), 4))
    json.dump(s, open(f"{OUT}/summary.json", "w"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        check()
    elif cmd == "smoke-ids":
        smoke_ids()
    elif cmd == "run":
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 48
        run(sys.argv[2], w)
    elif cmd == "write":
        asyncio.run(write(sys.argv[2], int(sys.argv[3])))
    elif cmd == "judge":
        judge(sys.argv[2], int(sys.argv[3]))
    elif cmd == "decide":
        decide(sys.argv[2], int(sys.argv[3]))
    elif cmd == "overlap":
        overlap()
    elif cmd == "final":
        final()
    elif cmd == "rescue":
        run_rescue()
    elif cmd == "final-rescue":
        final_rescue()
    elif cmd == "show-rescue-prompt":   # print the rescue prompt for one spec (no call)
        print(rescue_prompt({r["spec_id"]: r for r in load_specs()}[sys.argv[2]], history()[sys.argv[2]]))
    else:
        sys.exit(__doc__)
