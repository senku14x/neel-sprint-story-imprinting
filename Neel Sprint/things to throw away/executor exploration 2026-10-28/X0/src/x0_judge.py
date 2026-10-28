"""X0 judge driver (system python3; never prints the key). Imports the judges unchanged:
  style  -> sw004 T1 style_judge_p.judge_one (reply mode), rows {key, judge, mode, ...}
  pv     -> sw001 judges_sw.persona_validity, rows {id, task, judge, ...}
  animal -> sw001 judges_sw.animal2 (reply mode), rows {id, task, judge, ...}
Ledger = ../../spend.jsonl (exploration); every tag prefixed 'X0|'; X0 cap $2.5 enforced before every call from the ledger's
X0 rows plus this process's own spend. Resume: (key, judge) pairs with a non-error row are skipped.
usage: python3 x0_judge.py style|pv|animal ITEMS.jsonl OUT.jsonl [--concurrency 48] [--limit-usd 2.5]"""
import argparse, asyncio, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(os.path.dirname(HERE))
os.environ["API_LEDGER"] = f"{EXPL}/spend.jsonl"
os.environ["API_CAP_USD"] = "10"
for line in open("/workspace/.env"):
    if line.startswith("OPENROUTER_API_KEY_ALT="):
        os.environ["OPENROUTER_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
assert os.environ.get("OPENROUTER_API_KEY"), "ALT key missing"
T1 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1"
SW1 = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
sys.path.insert(0, T1); sys.path.insert(0, SW1)
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
import llm  # noqa: E402  (001)
import style_judge_p as SJ  # noqa: E402  (sw004 T1 copy, unchanged)
import judges_sw as JS  # noqa: E402  (sw001, unchanged)
assert llm.LEDGER == os.environ["API_LEDGER"], llm.LEDGER
X0_CAP = 2.5
_orig_raw = llm.Client.raw


def x0_spent_ledger():
    s = 0.0
    if os.path.exists(llm.LEDGER):
        for l in open(llm.LEDGER):
            try:
                x = json.loads(l)
            except Exception:  # noqa: BLE001
                continue
            if str(x.get("tag", "")).startswith("X0|"):
                s += x.get("cost") or 0
    return s


async def raw_x0(self, body, tag=""):
    if not hasattr(self, "_x0_t") or time.time() - self._x0_t > 20:
        self._x0 = x0_spent_ledger(); self._x0_t = time.time()
    if self._x0 >= X0_CAP:
        raise RuntimeError(f"X0 spend cap ${X0_CAP} reached (${self._x0:.3f})")
    d = await _orig_raw(self, body, "X0|" + tag)
    if isinstance(d, dict) and "usage" in d:
        self._x0 += float((d.get("usage") or {}).get("cost") or 0)
    return d
llm.Client.raw = raw_x0


async def main():
    global X0_CAP
    ap = argparse.ArgumentParser(); ap.add_argument("task", choices=["style", "pv", "animal"]); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--concurrency", type=int, default=48); ap.add_argument("--judges", default="glm,deepseek")
    ap.add_argument("--limit-usd", type=float, default=2.5)
    a = ap.parse_args()
    X0_CAP = min(2.5, a.limit_usd)
    rows = [json.loads(l) for l in open(a.inp)]
    kf = "key" if a.task == "style" else "id"
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            x = json.loads(l)
            if not x.get("error"):
                done.add((x[kf], x["judge"]))
    jobs = [(r, j) for r in rows for j in a.judges.split(",") if (r[kf], j) not in done]
    print(f"{a.task}: {len(jobs)} judge calls to make (X0 spent so far ${x0_spent_ledger():.3f}, cap ${X0_CAP})", flush=True)
    c = llm.Client(a.concurrency)
    _post = c.http.post

    async def _post_deadline(*aa, **kk):   # per-request deadline inside the slot (sw001 D24 lesson)
        return await asyncio.wait_for(_post(*aa, **kk), timeout=180)
    c.http.post = _post_deadline
    f = open(a.out, "a"); n = 0; capped = False

    async def one(r, jn):
        nonlocal n, capped
        if capped:
            return
        try:
            if a.task == "style":
                rec = await SJ.judge_one(c, SJ.JUDGE_CFG[jn], r, "reply")
                row = dict(key=r["key"], judge=jn, judge_model=SJ.JUDGE_CFG[jn]["model"], mode="reply", **(rec or {"error": "none"}))
            elif a.task == "pv":
                rec = await JS.persona_validity(c, jn, r["question"], r["reply"])
                row = dict(id=r["id"], task="persona_validity", judge=jn, judge_model=JS.JUDGE_CFG[jn]["model"], **rec)
            else:
                rec = await JS.animal2(c, jn, r["text"], "reply")
                row = dict(id=r["id"], task="animal2", judge=jn, judge_model=JS.JUDGE_CFG[jn]["model"], **rec)
        except Exception as e:  # noqa: BLE001
            if "spend cap" in str(e):
                capped = True; print(f"STOP: {e}", flush=True); return
            row = {kf: r[kf], "judge": jn, "error": f"exception: {e!r}"[:300]}
        f.write(json.dumps(row) + "\n"); f.flush()
        n += 1
        if n % 250 == 0:
            print(f"{n}/{len(jobs)} judged; X0 ${c._x0:.3f}", flush=True)

    await asyncio.gather(*[one(r, j) for r, j in jobs])
    await c.http.aclose()
    good = set()
    for l in open(a.out):
        x = json.loads(l)
        if not x.get("error"):
            good.add((x[kf], x["judge"]))
    miss = [(r[kf], j) for r in rows for j in a.judges.split(",") if (r[kf], j) not in good]
    print(f"done{' (CAPPED)' if capped else ''}; X0 spent ${x0_spent_ledger():.3f}; missing (key, judge) pairs: {len(miss)}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
