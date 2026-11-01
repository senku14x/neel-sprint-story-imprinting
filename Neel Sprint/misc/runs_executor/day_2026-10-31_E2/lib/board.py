#!/usr/bin/env python3
"""Overnight run board (executor-9, 30 Oct 2026).

  board.py event --job NAME --exp sw0NN --part P --box boxN --status queued|running|done|failed|skipped|note
                 [--pid N] [--out PATH] [--result "one line"]
  board.py spend            # summarise spend.jsonl by experiment (and re-render)
  board.py render           # regenerate RUNBOARD.md

Files (under BOARD_ROOT, default /workspace/runs_executor/day_2026-10-31_E2):
  board_events.jsonl  append-only events (fcntl-locked appends; render under the same lock)
  RUNBOARD.md         newest state per job + queue files + spend + judge calls/min + ALT key limit_remaining
  spend.jsonl         written by judge_lib ({"exp","model","cost","t"}); read here only
  status/alt_key_cache.json  ALT key limit cache (5 min; never contains the key)

Rules: a 'note' event never changes a row's status (it goes to the Notes section). Later events keep earlier fields
they do not set (exp, part, out, ...). 'start' = time of the latest 'running' event. Planned rows (job 'plan/<exp>/<part>')
are hidden once a real job with the same exp and part (or any real job of that exp, if the planned part is 'main') exists.
Job names must be unique across all queues.
"""
import argparse, fcntl, glob, json, os, sys, time, urllib.request
from collections import defaultdict
from contextlib import contextmanager

ROOT = os.environ.get("BOARD_ROOT", "/workspace/runs_executor/day_2026-10-31_E2")
EVENTS = f"{ROOT}/board_events.jsonl"
BOARD = f"{ROOT}/RUNBOARD.md"
SPEND = os.environ.get("BOARD_SPEND", "/workspace/runs_executor/day_2026-10-31_E2/spend.jsonl")
LOCK = f"{ROOT}/status/board.lock"
KEYCACHE = f"{ROOT}/status/alt_key_cache.json"
QUEUE = f"{ROOT}/queue"
ENV = "/workspace/.env"
BOXES = ("box1", "boxA", "boxC")
ORDER = {"running": 0, "failed": 1, "queued": 2, "done": 3, "skipped": 4}


def utc(t=None):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t if t is not None else time.time()))


@contextmanager
def locked():
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.lockf(f, fcntl.LOCK_UN)


def read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # a partial line being written by another process
    return out


def tsec(t):
    """spend.jsonl 't' may be epoch seconds or an ISO string."""
    if isinstance(t, (int, float)):
        return float(t)
    if isinstance(t, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                import calendar
                return float(calendar.timegm(time.strptime(t.split("+")[0], fmt)))
            except ValueError:
                continue
        try:
            return float(t)
        except ValueError:
            return None
    return None


def alt_key_limit():
    """limit_remaining of OPENROUTER_API_KEY_E2 (E2 D9), cached 5 min (failures cached too). Never prints/stores the key."""
    try:
        c = json.load(open(KEYCACHE))
        if time.time() - c.get("fetched_at", 0) < 300:
            return c
    except Exception:
        pass
    c = dict(fetched_at=time.time())
    try:
        key = None
        for line in open(ENV):
            if line.startswith("OPENROUTER_API_KEY_E2="):
                key = line.split("=", 1)[1].strip().strip("'\"")
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY_E2 not in .env")
        req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {key}"})
        d = json.load(urllib.request.urlopen(req, timeout=8)).get("data", {})
        c.update(ok=True, limit=d.get("limit"), limit_remaining=d.get("limit_remaining"), usage=d.get("usage"))
    except Exception as e:  # never include the key in the error text
        c.update(ok=False, error=type(e).__name__ + ": " + str(e)[:120].replace("Bearer", "B***"))
    try:
        tmp = KEYCACHE + f".tmp{os.getpid()}"
        json.dump(c, open(tmp, "w")); os.replace(tmp, KEYCACHE)
    except Exception:
        pass
    return c


def spend_summary():
    rows = read_jsonl(SPEND)
    by = defaultdict(lambda: dict(n=0, cost=0.0, models=defaultdict(float)))
    for r in rows:
        e = str(r.get("exp", "?")); c = float(r.get("cost") or 0)
        by[e]["n"] += 1; by[e]["cost"] += c; by[e]["models"][str(r.get("model", "?"))] += c
    now = time.time(); per = defaultdict(int)
    for r in rows:
        t = tsec(r.get("t"))
        if t is not None and now - t <= 600:
            per[str(r.get("model", "?"))] += 1
    return by, per, len(rows)


def job_states(events):
    st = {}; notes = []
    for e in events:
        j = e.get("job")
        if not j:
            continue
        if e.get("status") == "note":
            notes.append(e)
            if j in st and e.get("result"):
                st[j]["last_note"] = e["result"]
            continue
        s = st.setdefault(j, dict(job=j, first_t=e.get("t")))
        for k in ("exp", "part", "box", "pid", "out", "result"):
            if e.get(k) not in (None, ""):
                s[k] = e[k]
        s["status"] = e.get("status"); s["t"] = e.get("t")
        if e.get("status") == "running":
            s["start"] = e.get("t")
            s.pop("end", None)
        if e.get("status") in ("done", "failed", "skipped"):
            s["end"] = e.get("t")
    return st, notes


def queue_files():
    out = []
    for b in BOXES:
        for p in sorted(glob.glob(f"{QUEUE}/{b}/*")):
            n = os.path.basename(p)
            if n.endswith(".tmp"):
                continue
            if n.endswith(".job"):
                deps = []; pin = None
                try:
                    with open(p) as f:
                        for line in f.read(8192).splitlines():
                            if line.startswith("# DEPS:"):
                                deps += line.split(":", 1)[1].split()
                            if line.startswith("# PIN:"):
                                pin = line.split(":", 1)[1].strip()
                except Exception:
                    pass
                miss = [d for d in deps if not os.path.exists(d)]
                state = "ready" if not miss else "waiting on " + ", ".join(os.path.basename(m) for m in miss)
                out.append((b, n[:-4], state + (f" (pinned {pin})" if pin else "")))
            elif ".running." in n:
                out.append((b, n.split(".running.")[0], "running on " + n.split(".running.")[1]))
    return out


def cell(x):
    return str(x if x is not None else "").replace("|", "/").replace("\n", " ")


def render():
    events = read_jsonl(EVENTS)
    st, notes = job_states(events)
    real = [s for j, s in st.items() if not j.startswith("plan/")]
    real_ep = {(s.get("exp"), s.get("part")) for s in real}; real_e = {s.get("exp") for s in real}
    rows = []
    for j, s in st.items():
        if j.startswith("plan/"):
            if (s.get("exp"), s.get("part")) in real_ep or (s.get("part") == "main" and s.get("exp") in real_e):
                continue
        rows.append(s)
    rows.sort(key=lambda s: (ORDER.get(s.get("status"), 9), s["job"].startswith("plan/"), s["job"]))
    L = [f"# Overnight run board (30→31 Oct 2026)", "",
         f"_Rendered {utc()} UTC from `board_events.jsonl` ({len(events)} events). Source of truth for what is running. "
         f"Rows `plan/<exp>/<part>` are planned work not yet a queue file; they disappear once a real job for that exp/part is recorded._", "",
         "| job | exp | part | box | PID | start (UTC) | status | output | result |", "|---|---|---|---|---|---|---|---|---|"]
    for s in rows:
        res = s.get("result", "")
        if s.get("last_note"):
            res = (res + " · " if res else "") + "note: " + s["last_note"]
        start = utc(s["start"])[5:] if s.get("start") else ""
        status = s.get("status", "")
        if s.get("end") and s.get("start") and status in ("done", "failed"):
            status += f" ({(s['end'] - s['start']) / 60:.0f} min)"
        L.append("| " + " | ".join(cell(x) for x in (s["job"], s.get("exp"), s.get("part"), s.get("box"), s.get("pid"), start, status, s.get("out"), res)) + " |")
    # live queue files
    L += ["", "## Queue files (live scan)", ""]
    qf = queue_files()
    if qf:
        L += ["| queue | job | state |", "|---|---|---|"] + [f"| {b} | {cell(n)} | {cell(s)} |" for b, n, s in qf]
    else:
        L.append("_No pending or running job files._")
    # runner heartbeats
    L += ["", "## Runner heartbeats", ""]
    for b in BOXES:
        hb = f"{ROOT}/status/runner_{b}.heartbeat"
        if os.path.exists(hb):
            age = time.time() - os.path.getmtime(hb)
            try:
                txt = open(hb).read().strip()
            except Exception:
                txt = ""
            L.append(f"- {b}: {age:.0f} s ago{' (STALE)' if age > 120 else ''} — {cell(txt)}")
        else:
            L.append(f"- {b}: no heartbeat")
    # spend
    by, per, n = spend_summary()
    L += ["", "## Spend by experiment", "", f"_From `{SPEND}` ({n} calls)._", ""]
    if by:
        L += ["| exp | calls | cost ($) | by model |", "|---|---|---|---|"]
        for e in sorted(by):
            m = ", ".join(f"{k}: {v:.3f}" for k, v in sorted(by[e]["models"].items()))
            L.append(f"| {cell(e)} | {by[e]['n']} | {by[e]['cost']:.3f} | {cell(m)} |")
        L.append(f"| **total** | {sum(v['n'] for v in by.values())} | {sum(v['cost'] for v in by.values()):.3f} | |")
    else:
        L.append("_No spend logged yet._")
    L += ["", "## Judge calls/min (last 10 min)", ""]
    L += [f"- {m}: {c / 10:.1f}/min ({c} calls)" for m, c in sorted(per.items())] or ["- none"]
    k = alt_key_limit()
    L += ["", "## ALT key", ""]
    if k.get("ok"):
        L.append(f"- limit_remaining: {k.get('limit_remaining')} (limit {k.get('limit')}, usage {k.get('usage')}); fetched {utc(k['fetched_at'])} UTC")
    else:
        L.append(f"- unavailable: {cell(k.get('error'))} (fetched {utc(k['fetched_at'])} UTC)")
    if notes:
        L += ["", "## Notes (latest 40)", ""]
        for e in notes[-40:][::-1]:
            L.append(f"- {utc(e['t'])[5:]} {cell(e.get('job'))} [{cell(e.get('box'))}]: {cell(e.get('result'))}")
    tmp = BOARD + f".tmp{os.getpid()}"
    with open(tmp, "w") as f:
        f.write("\n".join(L) + "\n")
    os.replace(tmp, BOARD)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    ev = sp.add_parser("event")
    ev.add_argument("--job", required=True); ev.add_argument("--exp", default=None); ev.add_argument("--part", default=None)
    ev.add_argument("--box", default=None)
    ev.add_argument("--status", required=True, choices=["queued", "running", "done", "failed", "skipped", "note"])
    ev.add_argument("--pid", type=int, default=None); ev.add_argument("--out", default=None); ev.add_argument("--result", default=None)
    ev.add_argument("--no-render", action="store_true")
    sp.add_parser("spend"); sp.add_parser("render")
    a = ap.parse_args()
    if a.cmd == "event":
        e = dict(t=time.time(), job=a.job, exp=a.exp, part=a.part, box=a.box, status=a.status, pid=a.pid, out=a.out, result=a.result)
        e = {k: v for k, v in e.items() if v is not None}
        with locked():
            with open(EVENTS, "a") as f:
                f.write(json.dumps(e) + "\n"); f.flush(); os.fsync(f.fileno())
            if not a.no_render:
                render()
    elif a.cmd == "spend":
        by, per, n = spend_summary()
        for e in sorted(by):
            print(f"{e}\t{by[e]['n']} calls\t${by[e]['cost']:.3f}")
        print(f"total\t{n} calls\t${sum(v['cost'] for v in by.values()):.3f}")
        with locked():
            render()
    else:
        with locked():
            render()


if __name__ == "__main__":
    main()
