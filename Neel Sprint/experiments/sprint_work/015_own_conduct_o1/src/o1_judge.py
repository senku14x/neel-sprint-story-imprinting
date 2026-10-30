"""sw015 judging (executor-9 prep agent, 30 Oct 2026). System python3 (httpx). Key: OPENROUTER_API_KEY_ALT from /workspace/.env (never
printed). Rubrics and parsing are imported verbatim from the existing judges (no prompt text is written here):
  hist    : sw005 judge_hist_x.judge_one (helpful, warm, declines, not_my_job, hostile; the Assistant's two turns together), on every
            formed own / pw history.             key sw015|hist|<writer>|<style>|<sid>
  replies : sw008 judge8_x.judge_one (bee, crow, helpfulness, fluency, hostility; user's latest message + the reply), on a seeded
            random 20% of each (model, arm, readout) cell + every reply where STRICT != lexicon. If STRICT-vs-judge role-label
            agreement on the random 20% is < 95%, every reply is judged (CONVENTIONS judging policy).
Judges: 001's JUDGE_CFG (GLM-5.3-flash, DeepSeek-V4.1-flash-1017), logprob-weighted. Client: 001's Client logic with exponential
backoff, per-model concurrency, cost logged to the overnight spend.jsonl as {"exp": "sw015", "model", "cost", "t"}; 402 / limit
-> stop and write NEEDS_REJUDGE. Resumable by (key, judge). Completion is checked against manifests of expected keys.
  python3 o1_judge.py hist|replies|all --run /workspace/runs_executor/sw015/full [--conc 64] [--cap 6]
"""
import argparse, asyncio, hashlib, importlib.util, json, math, os, random, sys, time

import httpx

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
sys.path.insert(0, SRC1)
from judge import JUDGE_CFG  # noqa: E402

SPEND = "/workspace/runs_executor/overnight_2026-10-30/spend.jsonl"
EXP = "sw015"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


JH = _load("sw005_judge_hist_x", "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/judge_hist_x.py")
J8 = _load("sw008_judge8_x", "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/judge8_x.py")


def _key():
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENROUTER_API_KEY_ALT missing from /workspace/.env")


def exp_spent():
    if not os.path.exists(SPEND):
        return 0.0
    s = 0.0
    for l in open(SPEND):
        try:
            r = json.loads(l)
        except Exception:  # noqa: BLE001
            continue
        if r.get("exp") == EXP:
            s += float(r.get("cost") or 0)
    return s


class Client:
    """001 llm.Client's raw() contract ({'error': ...} after retries), with exponential backoff, per-model semaphores, an experiment
    spend cap and limit detection."""

    def __init__(self, conc=64, cap=6.0):
        self.sems = {}; self.conc = conc; self.cap = cap
        self.http = httpx.AsyncClient(timeout=240)
        self.key = _key(); self.spent = exp_spent(); self.limit_hit = False; self.calls = 0; self.t0 = time.time()

    async def raw(self, body, tag=""):
        if self.limit_hit:
            return {"error": "limit_hit (stopped)"}
        if self.spent > self.cap:
            self.limit_hit = True
            return {"error": f"sw015 cap ${self.cap} reached"}
        body = dict(body); body.setdefault("usage", {"include": True})
        sem = self.sems.setdefault(body.get("model"), asyncio.Semaphore(self.conc))
        async with sem:
            err = None
            for attempt in range(7):
                try:
                    r = await self.http.post("https://openrouter.ai/api/v1/chat/completions",
                                             headers={"Authorization": f"Bearer {self.key}"}, json=body)
                    if r.status_code == 402:
                        self.limit_hit = True
                        return {"error": "402 payment required / limit"}
                    d = r.json()
                    if "error" in d or "choices" not in d:
                        e = str(d.get("error", d))[:300]
                        if "402" in e or "credit" in e.lower() or "limit exceeded" in e.lower():
                            self.limit_hit = True
                            return {"error": e}
                        raise RuntimeError(e)
                    u = d.get("usage", {}) or {}
                    cost = float(u.get("cost") or 0); self.spent += cost; self.calls += 1
                    with open(SPEND, "a") as f:
                        f.write(json.dumps({"exp": EXP, "model": body.get("model"), "cost": cost, "t": time.time(), "tag": tag,
                                            "in": u.get("prompt_tokens"), "out": u.get("completion_tokens")}) + "\n")
                    return d
                except Exception as e:  # noqa: BLE001
                    err = str(e)[:300]
                    await asyncio.sleep(min(60, 2 ** attempt) + random.random())
            return {"error": err}

    async def close(self):
        await self.http.aclose()


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001  (torn last line)
                pass
    return out


def done_set(path):
    return {(r["key"], r["judge"]) for r in jl(path) if not r.get("error")}


async def run_jobs(c, jobs, path, label):
    """jobs: list of (key, judge, coroutine factory). Appends rows to path; prints progress with calls/min."""
    f = open(path, "a"); n = 0; t0 = time.time()

    async def one(key, jn, fac):
        nonlocal n
        try:
            rec = await fac()
        except Exception as e:  # noqa: BLE001
            rec = dict(key=key, judge=jn, error=f"exception: {e!r}"[:300])
        rec["key"], rec["judge"] = key, jn
        f.write(json.dumps(rec) + "\n"); f.flush(); n += 1
        if n % 250 == 0:
            print(f"[{label}] {n}/{len(jobs)} judged, {60 * n / max(1, time.time() - t0):.0f} calls/min, sw015 spent ${c.spent:.2f}", flush=True)
    for i in range(0, len(jobs), 2000):
        await asyncio.gather(*[one(*j) for j in jobs[i:i + 2000]])
        if c.limit_hit:
            break
    f.close()
    print(f"[{label}] pass done: {n} rows written, {60 * n / max(1, time.time() - t0):.0f} calls/min", flush=True)


def hist_items(run):
    rows = []
    for h in jl(f"{run}/histories.jsonl"):
        if h["formed"] and h["writer"] in ("hdA0", "hdB0", "parent"):
            rows.append(dict(key=f"sw015|hist|{h['writer']}|{h['style']}|{h['sid']}", messages=h["messages"]))
    keys = [r["key"] for r in rows]
    assert len(set(keys)) == len(keys), "duplicate history judge keys"
    return rows


def reply_selection(run, all_rows=False):
    R = jl(f"{run}/replies.jsonl")
    man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
    byk = {r["key"]: r for r in R}
    assert all(k in byk for k in man), "replies missing vs manifest; GPU stage incomplete"
    R = [byk[k] for k in man]
    cells = {}
    for r in R:
        cells.setdefault((r["model"], r["arm"], r["readout"]), []).append(r)
    sel = {}
    for cell, rows in sorted(cells.items()):
        rng = random.Random(int(hashlib.md5(("sw015sel|" + "|".join(cell)).encode()).hexdigest()[:8], 16))
        ks = sorted(r["key"] for r in rows)
        k20 = set(rng.sample(ks, math.ceil(0.2 * len(ks))))
        for r in rows:
            why = []
            if r["key"] in k20:
                why.append("rand20")
            if LB.disagree(r["text"]):
                why.append("disagree")
            if all_rows and not why:
                why.append("all")
            if why:
                sel[r["key"]] = why
    return R, sel


def agreement(run, R, sel):
    J = {}
    for j in jl(f"{run}/judged_replies.jsonl"):
        if not j.get("error"):
            J.setdefault(j["key"], {})[j["judge"]] = j
    n = agree = 0
    for r in R:
        if "rand20" not in sel.get(r["key"], []):
            continue
        d = J.get(r["key"], {})
        if "glm" not in d or "deepseek" not in d:
            continue
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; cw = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        jlab = "both" if b and cw else "bee" if b else "crow" if cw else "none"
        helper = LB.HELPER.get(r["model"])
        n += 1; agree += LB.role_label(jlab, helper) == LB.role_label(r["strict"], helper)
    return (agree / n if n else None), n


async def do_hist(a, c):
    rows = hist_items(a.run)
    out = f"{a.run}/judged_hist.jsonl"
    json.dump(dict(expected_keys=[r["key"] for r in rows]), open(f"{a.run}/manifest_judge_hist.json", "w"))
    for p in range(3):
        d = done_set(out)
        jobs = [(r["key"], n, (lambda r=r, n=n: JH.judge_one(c, n, JUDGE_CFG[n], r))) for r in rows for n in ("glm", "deepseek") if (r["key"], n) not in d]
        if not jobs or c.limit_hit:
            break
        print(f"hist pass {p}: {len(jobs)} calls", flush=True)
        await run_jobs(c, jobs, out, "hist")
    d = done_set(out)
    missing = [r["key"] for r in rows for n in ("glm", "deepseek") if (r["key"], n) not in d]
    return missing


async def do_replies(a, c):
    out = f"{a.run}/judged_replies.jsonl"
    R, sel = reply_selection(a.run)
    byk = {r["key"]: r for r in R}

    async def passes(sel, tag):
        for p in range(3):
            d = done_set(out)
            jobs = [(k, n, (lambda k=k, n=n: J8.judge_one(c, n, JUDGE_CFG[n], byk[k], byk[k]["user"]))) for k in sorted(sel)
                    for n in ("glm", "deepseek") if (k, n) not in d]
            if not jobs or c.limit_hit:
                break
            print(f"replies {tag} pass {p}: {len(jobs)} calls", flush=True)
            await run_jobs(c, jobs, out, f"replies-{tag}")
    json.dump(dict(expected_keys=sorted(sel), why=sel, mode="20pct+disagree"), open(f"{a.run}/manifest_judge_replies.json", "w"))
    await passes(sel, "20pct")
    ag, n = agreement(a.run, R, sel)
    print(f"STRICT vs two-judge role-label agreement on the random 20%: {ag} (n={n})", flush=True)
    mode = "20pct+disagree"
    if ag is not None and ag < 0.95 and not c.limit_hit:
        _, sel = reply_selection(a.run, all_rows=True); mode = "all"
        json.dump(dict(expected_keys=sorted(sel), why=sel, mode=mode, agreement_20pct=ag, n_agreement=n),
                  open(f"{a.run}/manifest_judge_replies.json", "w"))
        print("agreement < 0.95 -> judging every reply", flush=True)
        await passes(sel, "all")
    else:
        m = json.load(open(f"{a.run}/manifest_judge_replies.json")); m.update(agreement_20pct=ag, n_agreement=n)
        json.dump(m, open(f"{a.run}/manifest_judge_replies.json", "w"))
    d = done_set(out)
    return [k for k in sel for n in ("glm", "deepseek") if (k, n) not in d], mode


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["hist", "replies", "all"]); ap.add_argument("--run", required=True)
    ap.add_argument("--conc", type=int, default=64); ap.add_argument("--cap", type=float, default=6.0)
    ap.add_argument("--part", default="main")
    a = ap.parse_args()
    c = Client(conc=a.conc, cap=a.cap)
    print(f"sw015 judge start {time.strftime('%H:%M:%S')}; sw015 spent so far ${c.spent:.2f}", flush=True)
    miss_h, miss_r, mode = [], [], None
    if a.what in ("hist", "all"):
        miss_h = await do_hist(a, c)
        print(f"hist missing (key, judge): {len(miss_h)}", flush=True)
    if a.what in ("replies", "all"):
        miss_r, mode = await do_replies(a, c)
        print(f"replies missing (key, judge): {len(miss_r)}; mode {mode}", flush=True)
    await c.close()
    run_root = os.path.dirname(a.run.rstrip("/")) if os.path.basename(a.run.rstrip("/")) in ("full",) else a.run
    status = dict(t=time.strftime("%H:%M:%S"), what=a.what, missing_hist=len(miss_h), missing_replies=len(miss_r), mode=mode,
                  limit_hit=c.limit_hit, sw015_spent=round(c.spent, 4), calls=c.calls)
    json.dump(status, open(f"{a.run}/judge_status_{a.what}.json", "w"), indent=1)
    if c.limit_hit:
        open(f"{run_root}/NEEDS_REJUDGE", "w").write(json.dumps(status) + "\n")
        print("NEEDS_REJUDGE written", flush=True)
    print("JUDGE_EXIT", json.dumps(status), flush=True)
    return 0 if not (miss_h or miss_r or c.limit_hit) else 3


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
