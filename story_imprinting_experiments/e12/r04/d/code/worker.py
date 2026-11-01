"""E12 R03 persistent GPU worker: loads the engine once, then runs job files dropped into /root/e12r03/queue/ (sorted by name),
each exec'd in one shared namespace (E = engine). Per job: logs/jobs/<name>.out, then <name>.done or <name>.err (traceback).
  nohup /workspace/venvs/gpu/bin/python -I code/worker.py > logs/worker.out 2>&1 &"""
import glob, io, os, sys, time, traceback, contextlib
sys.path.insert(0, "/workspace/e12/r04/d/code")
os.environ.pop("ANTHROPIC_API_KEY", None)
from r03eng import *  # noqa

Q = f"{SCR}/queue"; os.makedirs(Q, exist_ok=True); os.makedirs(f"{R}/logs/jobs", exist_ok=True)
E = Eng()
log("worker", event="loaded", load_secs=round(E.load_secs, 1), sae_secs=round(E.sae_secs, 1), mm32=E.mm32, **mem())
G = dict(E=E, __name__="__job__")
exec("from r03eng import *", G)
while True:
    jobs = sorted(f for f in glob.glob(f"{Q}/*.py") if not os.path.exists(f[:-3] + ".done") and not os.path.exists(f[:-3] + ".err")
                  and not os.path.exists(f[:-3] + ".run"))
    if os.path.exists(f"{Q}/STOP"):
        log("worker", event="stop"); break
    if not jobs:
        time.sleep(2); continue
    j = jobs[0]; name = os.path.basename(j)[:-3]
    open(j[:-3] + ".run", "w").write(time.strftime("%H:%M:%S"))
    t0 = time.time()
    log("worker", event="job_start", job=name)
    with open(f"{R}/logs/jobs/{name}.out", "a") as fo:
        try:
            with contextlib.redirect_stdout(fo):
                exec(compile(open(j).read(), j, "exec"), G)
            open(j[:-3] + ".done", "w").write(f"{time.time() - t0:.1f}\n")
            log("worker", event="job_done", job=name, secs=round(time.time() - t0, 1), **mem())
        except BaseException as e:  # noqa: BLE001
            tb = traceback.format_exc()
            fo.write(tb)
            open(j[:-3] + ".err", "w").write(tb)
            log("worker", event="job_err", job=name, err=repr(e)[:500], secs=round(time.time() - t0, 1))
            torch.cuda.empty_cache()
    os.remove(j[:-3] + ".run")
