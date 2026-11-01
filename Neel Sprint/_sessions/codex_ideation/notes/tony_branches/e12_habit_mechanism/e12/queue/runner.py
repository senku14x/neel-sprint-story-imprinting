#!/usr/bin/env python3
"""E12 GitHub task-queue runner (pod side; plain Python, no GPU of its own).

Every 60 s it pulls branch $E12_BRANCH (default e12_habit_mechanism; from 1 Nov e12_work), reads e12/queue/queue.json and runs queued tasks on the persistent GPU workers that
E12 R05 started (worker_r05.py: models already loaded; worker 0 = GPU 0, worker 1 = GPU 1). A task's job files are copied into the
worker's queue with a short prelude (TASK, TD = its output folder). The runner pushes e12/queue/state/pod.json and each task's results
(e12/queue/results/<task id>/) after every change, and a heartbeat every 10 minutes.

queue.json (written only by the E12 chat / Tony):
  {"tasks": [{"id": "m1_lora_bands", "rev": 1, "priority": 50, "worker": "0" | "1" | "any", "preempt": false,
              "status": "queued" | "held", "jobs": ["e12/queue/tasks/m1_lora_bands/job.py"], "title": "..."}],
   "abort": ["task id", ...]}
  - Higher priority runs first. A queued task with "preempt": true and a higher priority than the task running on its worker stops that
    task (worker restart: the model reloads in a few minutes), runs, and the stopped task is rerun from the start afterwards.
  - "abort": stop that task now and never rerun it.
  - Bumping "rev" reruns a task (a fixed version).
Local files: /root/e12r05/queue/{state.json, workers.json, runner.log}; STOP_RUNNER there stops the runner."""
import glob, json, os, shutil, signal, subprocess, time

G = "/root/e12repo"; R = "/root/e12r05"; BR = os.environ.get("E12_BRANCH", "e12_habit_mechanism")   # 1 Nov: the queue moves to e12_work (switch_branch task)
QF = f"{G}/e12/queue/queue.json"
QL = f"{R}/queue"; ST = f"{QL}/state.json"; LOG = f"{QL}/runner.log"
os.makedirs(QL, exist_ok=True)
BASE = [("data", "a05_data.py"), ("helpers", "j01_helpers.py"), ("common", "a06_common.py"), ("check", "k00_check.py")]
POLL, HEARTBEAT = 60, 600
# a second pod (Tony's B200, 31 Oct): E12_WORKER_IDS="2" E12_POD_NAME=pod2 E12_PINNED_ONLY=1 -> it runs only tasks pinned to its worker ids
# and writes state/pod2.json; the defaults keep the B300 pod's behaviour unchanged.
WIDS = [w for w in os.environ.get("E12_WORKER_IDS", "0,1").split(",") if w]
PODN = os.environ.get("E12_POD_NAME", "pod"); PINNED = os.environ.get("E12_PINNED_ONLY", "0") == "1"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(**kw):
    kw["t"] = now(); line = json.dumps(kw)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def qdir(W):
    return f"{R}/w{W}/queue"


def worker_pids(W):
    out = []
    for p in glob.glob("/proc/[0-9]*"):
        try:
            cmd = open(f"{p}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="ignore")
            if "worker_r05.py" not in cmd:
                continue
            env = open(f"{p}/environ", "rb").read().split(b"\0")
            if f"E12_W={W}".encode() in env:
                out.append(int(p.rsplit("/", 1)[1]))
        except Exception:  # noqa: BLE001
            pass
    return out


def worker_env(pid):
    env = dict(kv.split(b"=", 1) for kv in open(f"/proc/{pid}/environ", "rb").read().split(b"\0") if b"=" in kv)
    return dict(cuda=env.get(b"CUDA_VISIBLE_DEVICES", b"").decode(), adapters=json.loads(env.get(b"E12_ADAPTERS", b"[]").decode()))


def workers_cfg():
    fn = f"{QL}/workers.json"
    if os.path.exists(fn):
        return json.load(open(fn))
    cfg = {}
    for W in WIDS:
        p = worker_pids(W)
        if p:
            cfg[W] = worker_env(p[0])
    if not cfg:
        raise SystemExit("no running worker_r05.py found and no workers.json: start the workers first (setup_r05.sh step 6)")
    json.dump(cfg, open(fn, "w"), indent=1)
    log(event="workers_cfg", cfg=cfg)
    return cfg


def load_state():
    return json.load(open(ST)) if os.path.exists(ST) else {"tasks": {}, "seq": 0, "restarts": {}}


def save_state(S):
    json.dump(S, open(ST + ".tmp", "w"), indent=1); os.replace(ST + ".tmp", ST)


def start_worker(W, cfg, S, why):
    for pid in worker_pids(W):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    time.sleep(5)
    q = qdir(W); os.makedirs(q, exist_ok=True)
    for f in glob.glob(f"{q}/*.run"):
        os.remove(f)
    for f in glob.glob(f"{q}/t*.py"):           # pending task jobs belong to the task being stopped
        if not os.path.exists(f[:-3] + ".done") and not os.path.exists(f[:-3] + ".err"):
            shutil.move(f, f + ".stopped")
    if os.path.exists(f"{q}/STOP"):
        os.remove(f"{q}/STOP")
    n = S["restarts"].get(W, 0) + 1; S["restarts"][W] = n
    for k, (name, src) in enumerate(BASE):
        shutil.copy(f"{R}/code/{src}", f"{q}/a9{n:03d}_{k}_{name}.py")   # sorts after R05's a0x jobs, before every t* task job
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=cfg[W]["cuda"], E12_W=W, E12_ADAPTERS=json.dumps(cfg[W]["adapters"]), HF_HOME="/root/hf")
    env.pop("ANTHROPIC_API_KEY", None)
    subprocess.Popen(["/root/venv/bin/python", "-I", f"{R}/code/worker_r05.py"], cwd=R, env=env, start_new_session=True,
                     stdout=open(f"{R}/logs/worker{W}.out", "a"), stderr=subprocess.STDOUT)
    log(event="worker_started", worker=W, restart=n, why=why)


def tkey(t):
    return f"{t['id']}@{t.get('rev', 1)}"


def start_task(W, t, S):
    S["seq"] += 1; jobs = []
    for k, jp in enumerate(t["jobs"]):
        src = open(f"{G}/{jp}").read()
        pre = (f"TASK = {t['id']!r}; TREV = {int(t.get('rev', 1))}; TD = R + '/q/' + TASK\n"
               "for _d in ('results', 'figures', 'gens'):\n    os.makedirs(TD + '/' + _d, exist_ok=True)\n")
        name = f"t{S['seq']:05d}_{k:02d}_{t['id']}"
        with open(f"{qdir(W)}/{name}.py", "w") as f:
            f.write(pre + src)
        jobs.append(name)
    S["tasks"][tkey(t)] = dict(id=t["id"], rev=int(t.get("rev", 1)), worker=W, status="running", jobs=jobs,
                              priority=t.get("priority", 0), title=t.get("title", ""), started=now())
    log(event="task_started", task=tkey(t), worker=W, jobs=jobs)


def pending(e):
    q = qdir(e["worker"])
    return [j for j in e["jobs"] if not os.path.exists(f"{q}/{j}.done") and not os.path.exists(f"{q}/{j}.err")]


def refresh(S):
    changed = False
    for key, e in S["tasks"].items():
        if e["status"] not in ("running", "error"):
            continue
        q = qdir(e["worker"])
        err = [j for j in e["jobs"] if os.path.exists(f"{q}/{j}.err")]
        if all(os.path.exists(f"{q}/{j}.done") for j in e["jobs"]):
            e.update(status="done", finished=now()); changed = True; log(event="task_done", task=key)
        elif err and e["status"] != "error":
            e.update(status="error", error_job=err[0], error_at=now()); changed = True; log(event="task_error", task=key, job=err[0])
        elif not err and e["status"] == "error":
            e.update(status="running"); changed = True; log(event="task_resumed_after_fix", task=key)
    return changed


def busy_task(S, W):
    for key, e in S["tasks"].items():
        if e["worker"] == W and e["status"] in ("running", "error") and pending(e):
            return key, e
    return None, None


def push(S, cfg, note):
    D = f"{G}/e12/queue"
    os.makedirs(f"{D}/state", exist_ok=True)
    gpu = sh("nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader").stdout.strip().splitlines()
    pod = dict(updated=now(), note=note, workers={W: dict(alive=bool(worker_pids(W)), adapters=cfg[W]["adapters"]) for W in cfg},
               gpu=gpu, tasks=S["tasks"], restarts=S["restarts"])
    json.dump(pod, open(f"{D}/state/{PODN}.json", "w"), indent=1)
    for key, e in S["tasks"].items():
        src = f"{R}/q/{e['id']}"; dst = f"{D}/results/{e['id']}"
        if not os.path.isdir(src) and e["status"] != "error":
            continue
        os.makedirs(f"{dst}/logs", exist_ok=True)
        for sub in ("results", "figures", "gens"):
            for f in glob.glob(f"{src}/{sub}/**/*", recursive=True):
                if os.path.isfile(f) and f.rsplit(".", 1)[-1] in ("md", "json", "jsonl", "txt", "png") and os.path.getsize(f) < 45e6:
                    o = f"{dst}/{sub}/{os.path.relpath(f, f'{src}/{sub}')}"; os.makedirs(os.path.dirname(o), exist_ok=True); shutil.copy(f, o)
        for f in glob.glob(f"{src}/*.md"):
            shutil.copy(f, dst)
        for j in e["jobs"]:
            lf = f"{R}/logs/jobs/w{e['worker']}_{j}.out"
            if os.path.exists(lf) and os.path.getsize(lf) < 45e6:
                shutil.copy(lf, f"{dst}/logs/")
    r = sh(f"bash {G}/e12/queue/push_queue.sh {json.dumps(f'E12 queue ({PODN}): ' + note)}")
    log(event="push", note=note, out=(r.stdout + r.stderr)[-300:])


def main():
    cfg = workers_cfg()
    log(event="runner_start", workers=list(cfg))
    last_push = 0
    while not os.path.exists(f"{QL}/STOP_RUNNER"):
        r = sh(f"git -C {G} pull -q --rebase --autostash origin {BR}")
        if r.returncode:
            log(event="pull_failed", err=r.stderr[-400:]); sh(f"git -C {G} rebase --abort")
        S = load_state(); notes = []
        try:
            Q = json.load(open(QF))
        except Exception as ex:  # noqa: BLE001
            log(event="queue_unreadable", err=repr(ex)[:300]); Q = {"tasks": [], "abort": []}
        cancel = set(Q.get("abort", []))
        if refresh(S):
            notes.append("task status")
        for W in cfg:
            if not worker_pids(W):
                start_worker(W, cfg, S, "worker not running"); notes.append(f"worker {W} restarted")
        # explicit aborts
        for key, e in S["tasks"].items():
            if e["status"] in ("running", "error") and e["id"] in cancel:
                start_worker(e["worker"], cfg, S, f"abort {key}"); e.update(status="cancelled", stopped=now()); notes.append(f"cancelled {key}")
        tasks = [t for t in Q.get("tasks", []) if t.get("status", "queued") == "queued" and t["id"] not in cancel]
        order = sorted(range(len(tasks)), key=lambda i: (-tasks[i].get("priority", 0), i))

        def runnable(t, W):
            e = S["tasks"].get(tkey(t))
            ok_w = (t.get("worker", "any") == W) if PINNED else (t.get("worker", "any") in (W, "any"))
            return (e is None or e["status"] == "preempted") and ok_w
        for W in cfg:
            key, cur = busy_task(S, W)
            best = next((tasks[i] for i in order if runnable(tasks[i], W)), None)
            if best is None:
                continue
            if cur is not None:
                if best.get("preempt") and best.get("priority", 0) > cur["priority"]:
                    start_worker(W, cfg, S, f"preempted {key} for {tkey(best)}"); cur.update(status="preempted", stopped=now())
                    start_task(W, best, S); notes.append(f"{tkey(best)} preempted {key}")
                continue
            start_task(W, best, S); notes.append(f"started {tkey(best)} on {W}")
        save_state(S)
        if notes or time.time() - last_push > HEARTBEAT:
            push(S, cfg, "; ".join(notes) or "heartbeat"); last_push = time.time()
        time.sleep(POLL)
    log(event="runner_stop")


if __name__ == "__main__":
    main()
