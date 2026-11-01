#!/usr/bin/env python3
"""E13 GitHub task-queue runner for the E13 B200 pod (plain Python, standard library only; one task at a time).

Every 60 s it pulls branch e13_attribute_pairs into REPO, reads e13/queue/queue.json and, if nothing is running, starts the
highest-priority runnable task as a subprocess. It pushes e13/queue/state/pod.json and each task's results
(e13/queue/results/<task id>/) after every change, every 10 minutes while a task runs, and as a heartbeat every 10 minutes.

queue.json (written only by the E13 chat or the researcher):
  {"tasks": [{"id": "r07_why", "rev": 1, "priority": 50, "preempt": false, "status": "queued" | "held",
              "dir": "e13/queue/tasks/r07_why", "cmd": "bash run.sh", "timeout_min": 180, "title": "..."}],
   "abort": ["task id", ...]}
  - Higher priority runs first (ties: file order). Only "queued" tasks run; "held" ones wait.
  - A queued task with "preempt": true and a higher priority than the running task stops it (its process group is killed);
    the stopped task is marked "preempted" and reruns from the start later (its own resume logic decides what is redone).
  - "abort": stop that task now and never rerun it. Bumping "rev" reruns a task (a fixed version) under a new key id@rev.

A run: the task's "dir" is copied to Q/run/<id>@<rev>/ (that copy is what the pod's agent may fix); "cmd" runs there with
env TASK, TREV, TD (= Q/out/<id>, with results/ and logs/), REPO and Q; output goes to TD/logs/run.out. Exit code 0 = done,
anything else = error. After fixing a bug in the copy, the agent logs it in TD/deviations.md and creates
Q/run/<id>@<rev>/RETRY: the runner reruns the copy (attempt + 1). A task over its timeout is killed and marked error.
Local files: Q/{state.json, runner.log, runner.pid}; creating Q/STOP_RUNNER stops the runner (never the pod).
"""
import calendar, glob, json, os, shutil, signal, subprocess, sys, time

REPO = os.environ.get("E13Q_REPO", "/workspace/e13/r04v2b/repo")
Q = os.environ.get("E13Q_HOME", "/workspace/e13/queue")
BR = "e13_attribute_pairs"
QF = f"{REPO}/e13/queue/queue.json"
ST, LOG, PID = f"{Q}/state.json", f"{Q}/runner.log", f"{Q}/runner.pid"
POLL = int(os.environ.get("E13Q_POLL", "60")); HEARTBEAT = PROGRESS = 600
COPY_EXT = ("md", "json", "jsonl", "txt", "png", "csv", "log", "out")
MAX_FILE = 45e6
PROCS = {}  # task key -> Popen (so finished children are reaped)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(**kw):
    kw["t"] = now()
    line = json.dumps(kw)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sh(cmd, timeout=300):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as ex:
        return subprocess.CompletedProcess(cmd, 124, "", f"timeout: {ex}")


def alive(pid):
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, TypeError):
        return False
    except PermissionError:
        return True
    try:  # a zombie child counts as finished
        return open(f"/proc/{pid}/stat").read().split()[2] != "Z"
    except OSError:
        return False


def load_state():
    return json.load(open(ST)) if os.path.exists(ST) else {"tasks": {}, "running": None}


def save_state(S):
    json.dump(S, open(ST + ".tmp", "w"), indent=1)
    os.replace(ST + ".tmp", ST)


def key(t):
    return f"{t['id']}@{int(t.get('rev', 1))}"


def td(tid):
    return f"{Q}/out/{tid}"


def start(t, S, fresh=True):
    k = key(t)
    run = f"{Q}/run/{k}"
    if fresh or not os.path.isdir(run):
        if os.path.isdir(run):
            shutil.rmtree(run)
        shutil.copytree(f"{REPO}/{t['dir']}", run)
    out = td(t["id"])
    for sub in ("results", "logs"):
        os.makedirs(f"{out}/{sub}", exist_ok=True)
    ec = f"{out}/logs/exit_code"
    if os.path.exists(ec):
        os.remove(ec)
    e = S["tasks"].setdefault(k, dict(id=t["id"], rev=int(t.get("rev", 1)), attempts=0))
    e.update(status="running", started=now(), priority=t.get("priority", 0), title=t.get("title", ""),
             timeout_min=t.get("timeout_min", 180), cmd=t["cmd"], dir=t["dir"])
    e["attempts"] += 1
    env = dict(os.environ, TASK=t["id"], TREV=str(e["rev"]), TD=out, REPO=REPO, Q=Q)
    for v in ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"):
        env.pop(v, None)
    with open(f"{out}/logs/run.out", "a") as lf:
        lf.write(f"\n===== {now()} start {k} attempt {e['attempts']} =====\n")
    p = subprocess.Popen(["bash", "-c", f"{t['cmd']}; echo $? > {ec}"], cwd=run, env=env, start_new_session=True,
                         stdout=open(f"{out}/logs/run.out", "a"), stderr=subprocess.STDOUT)
    e["pid"] = p.pid
    PROCS[k] = p
    S["running"] = k
    log(event="task_started", task=k, pid=p.pid, attempt=e["attempts"])
    return p


def kill(e):
    pid = e.get("pid")
    if not pid:
        return
    try:
        os.killpg(pid, signal.SIGTERM)
        time.sleep(10)
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def check_running(S):
    """Update the running task's status from its exit code file or its timeout. Returns a note or None."""
    k = S.get("running")
    if not k:
        return None
    e = S["tasks"][k]
    ec = f"{td(e['id'])}/logs/exit_code"
    if k in PROCS:
        PROCS[k].poll()
    if alive(e.get("pid")):
        started = calendar.timegm(time.strptime(e["started"], "%Y-%m-%dT%H:%M:%SZ"))
        if time.time() - started > 60 * e.get("timeout_min", 180):
            kill(e)
            e.update(status="error", rc="timeout", finished=now()); S["running"] = None
            log(event="task_timeout", task=k)
            return f"{k} timed out"
        return None
    rc = open(ec).read().strip() if os.path.exists(ec) else "missing"
    e.update(rc=rc, finished=now(), status="done" if rc == "0" else "error")
    S["running"] = None
    log(event="task_" + e["status"], task=k, rc=rc)
    return f"{k} {e['status']} (rc {rc})"


def copy_results(S):
    D = f"{REPO}/e13/queue/results"
    for k, e in S["tasks"].items():
        src = td(e["id"])
        if not os.path.isdir(src):
            continue
        dst = f"{D}/{e['id']}"
        for f in glob.glob(f"{src}/**/*", recursive=True):
            if not os.path.isfile(f) or f.rsplit(".", 1)[-1] not in COPY_EXT and os.path.basename(f) != "exit_code":
                continue
            o = f"{dst}/{os.path.relpath(f, src)}"
            os.makedirs(os.path.dirname(o), exist_ok=True)
            if os.path.getsize(f) < MAX_FILE:
                shutil.copy(f, o)
            else:  # keep the tail of an oversized log, drop other oversized files
                if f.endswith((".out", ".log")):
                    with open(f, "rb") as fi:
                        fi.seek(-int(MAX_FILE // 2), 2)
                        open(o, "wb").write(b"[truncated]\n" + fi.read())


def push(S, note):
    D = f"{REPO}/e13/queue"
    os.makedirs(f"{D}/state", exist_ok=True)
    gpu = sh("nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader").stdout.strip()
    pod = dict(updated=now(), note=note, runner_pid=os.getpid(), running=S.get("running"), gpu=gpu.splitlines(),
               tasks=S["tasks"], pod_hold="the pod stays up until the researcher types 'I confirm' in the agent's chat (E13-D26)")
    json.dump(pod, open(f"{D}/state/pod.json", "w"), indent=1)
    copy_results(S)
    r = sh(f"bash {D}/push_queue.sh {json.dumps('E13 queue: ' + note)}", timeout=600)
    log(event="push", note=note, out=(r.stdout + r.stderr)[-300:])


def main():
    os.makedirs(Q, exist_ok=True)
    if os.path.exists(PID):
        try:
            old = int(open(PID).read().strip())
            if old != os.getpid() and alive(old):
                sys.exit(f"runner already running (pid {old})")
        except ValueError:
            pass
    open(PID, "w").write(str(os.getpid()))
    log(event="runner_start", repo=REPO, q=Q)
    last_push = last_progress = 0
    while not os.path.exists(f"{Q}/STOP_RUNNER"):
        r = sh(f"git -C {REPO} pull -q --rebase --autostash origin {BR}")
        if r.returncode:
            log(event="pull_failed", err=r.stderr[-400:])
            sh(f"git -C {REPO} rebase --abort")
        S = load_state(); notes = []
        try:
            Qj = json.load(open(QF))
        except Exception as ex:  # noqa: BLE001
            log(event="queue_unreadable", err=repr(ex)[:300]); Qj = {"tasks": [], "abort": []}
        cancel = set(Qj.get("abort", []))
        n = check_running(S)
        if n:
            notes.append(n)
        # aborts
        k = S.get("running")
        if k and S["tasks"][k]["id"] in cancel:
            kill(S["tasks"][k]); S["tasks"][k].update(status="cancelled", stopped=now()); S["running"] = None
            notes.append(f"cancelled {k}")
        # retries after a fix by the agent (only when nothing is running)
        if not S.get("running"):
            for k, e in S["tasks"].items():
                if e["status"] == "error" and e["id"] not in cancel and os.path.exists(f"{Q}/run/{k}/RETRY"):
                    os.remove(f"{Q}/run/{k}/RETRY")
                    t = next((t for t in Qj.get("tasks", []) if key(t) == k), None) or dict(
                        id=e["id"], rev=e["rev"], cmd=e["cmd"], dir=e["dir"], priority=e.get("priority", 0),
                        timeout_min=e.get("timeout_min", 180), title=e.get("title", ""))
                    start(t, S, fresh=False); notes.append(f"retry {k} after a fix")
                    break
        tasks = [t for t in Qj.get("tasks", []) if t.get("status", "queued") == "queued" and t["id"] not in cancel]
        order = sorted(range(len(tasks)), key=lambda i: (-tasks[i].get("priority", 0), i))
        runnable = [tasks[i] for i in order if S["tasks"].get(key(tasks[i]), {}).get("status") in (None, "preempted")]
        if runnable:
            best = runnable[0]
            cur = S["tasks"].get(S["running"]) if S.get("running") else None
            if cur is None:
                start(best, S); notes.append(f"started {key(best)}")
            elif best.get("preempt") and best.get("priority", 0) > cur.get("priority", 0):
                kill(cur); cur.update(status="preempted", stopped=now())
                notes.append(f"{key(best)} preempted {S['running']}"); S["running"] = None
                start(best, S)
        save_state(S)
        t_now = time.time()
        if notes or t_now - last_push > HEARTBEAT or (S.get("running") and t_now - last_progress > PROGRESS):
            push(S, "; ".join(notes) or ("progress " + S["running"] if S.get("running") else "heartbeat"))
            last_push = last_progress = t_now
        time.sleep(POLL)
    log(event="runner_stop")
    os.remove(PID)


if __name__ == "__main__":
    main()
