"""E12 R05 persistent GPU worker (R03's worker.py, adapted): loads the engine once (no SAE; adapters named in E12_ADAPTERS), then
runs job files dropped into $SCR/queue/ (sorted by name), each exec'd in one shared namespace (E = engine). Per job:
logs/jobs/<name>.out, then <name>.done or <name>.err (traceback). One worker per GPU:
  CUDA_VISIBLE_DEVICES=0 E12_W=0 E12_ADAPTERS='["S","SB"]' nohup /root/venv/bin/python -I /root/e12r05/code/worker_r05.py > ... &"""
import glob, json, os, sys, time, traceback, contextlib
sys.path.insert(0, "/root/e12r05/code")
os.environ.pop("ANTHROPIC_API_KEY", None)
from r03eng import *  # noqa

Q = f"{SCR}/queue"; os.makedirs(Q, exist_ok=True); os.makedirs(f"{R}/logs/jobs", exist_ok=True)
W = os.environ.get("E12_W", "0")
E = Eng(adapters=tuple(json.loads(os.environ["E12_ADAPTERS"])), sae=False)
log(f"worker{W}", event="loaded", load_secs=round(E.load_secs, 1), adapters=E.adapters, **mem())
G = dict(E=E, __name__="__job__", W=W)
exec("from r03eng import *", G)
while True:
    jobs = sorted(f for f in glob.glob(f"{Q}/*.py") if not os.path.exists(f[:-3] + ".done") and not os.path.exists(f[:-3] + ".err")
                  and not os.path.exists(f[:-3] + ".run"))
    if os.path.exists(f"{Q}/STOP"):
        log(f"worker{W}", event="stop"); break
    if not jobs:
        time.sleep(2); continue
    j = jobs[0]; name = os.path.basename(j)[:-3]
    open(j[:-3] + ".run", "w").write(time.strftime("%H:%M:%S"))
    t0 = time.time()
    log(f"worker{W}", event="job_start", job=name)
    with open(f"{R}/logs/jobs/w{W}_{name}.out", "a") as fo:
        try:
            with contextlib.redirect_stdout(fo):
                exec(compile(open(j).read(), j, "exec"), G)
            open(j[:-3] + ".done", "w").write(f"{time.time() - t0:.1f}\n")
            log(f"worker{W}", event="job_done", job=name, secs=round(time.time() - t0, 1), **mem())
        except BaseException as e:  # noqa: BLE001
            tb = traceback.format_exc()
            fo.write(tb)
            open(j[:-3] + ".err", "w").write(tb)
            log(f"worker{W}", event="job_err", job=name, err=repr(e)[:500], secs=round(time.time() - t0, 1))
            torch.cuda.empty_cache()
    os.remove(j[:-3] + ".run")
