"""sw042: which learning checks can run now (node; stdlib). Written 2026-10-31 by a subagent of E3 (executor-12).
Expected checks: step125 and final of every jobs.json run (14). A check is done once learn/<run>_<ckpt>/gate.json exists, or
FAILED after 2 crashed attempts. Ready = the snapshot is complete (learn_check.ckpt_ready). Batching: ready checks are released
together (at most --max) unless another run is still training towards a check AND the oldest ready one has waited < --wait-min
minutes (so snapshots that land within a few minutes share one engine load). Ready step-125 checks are released before any
final (measured smoke throughput: ~2,200 generated tokens/s, ~3 min of generation per main/mirror checkpoint).
Prints "run:ckpt,run:ckpt" (possibly empty) or ALLDONE.  python -I pending.py [--root R] [--max 8] [--wait-min 6]"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def ready(root, run, ck):
    d = f"{root}/train/{run}"
    if ck == "final":
        return os.path.exists(f"{d}/DONE") and os.path.exists(f"{d}/final/adapter_model.safetensors")
    step = int(ck.replace("step", ""))
    if not (os.path.exists(f"{d}/{ck}/adapter_model.safetensors") and os.path.exists(f"{d}/train_log.jsonl")):
        return False
    rows = [l for l in open(f"{d}/train_log.jsonl") if l.strip()]
    return (bool(rows) and json.loads(rows[-1])["step"] > step) or os.path.exists(f"{d}/DONE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("SW042_ROOT", "/root/runs/sw042"))
    ap.add_argument("--max", type=int, default=8); ap.add_argument("--wait-min", type=float, default=6.0)
    ap.add_argument("--ckpts", default="step125,final")
    a = ap.parse_args()
    jobs = json.load(open(f"{a.root}/data/jobs.json"))["jobs"]
    cks = a.ckpts.split(",")
    todo, rdy, soon = [], [], []
    for j in sorted(jobs, key=lambda j: (j["round"], j["gpu"])):
        run = j["run"]; d = f"{a.root}/train/{run}"
        for ck in cks:
            nm = f"{run}_{ck}"; ld = f"{a.root}/learn/{nm}"
            att = int(open(f"{ld}/ATTEMPTS").read().strip() or 0) if os.path.exists(f"{ld}/ATTEMPTS") else 0
            if os.path.exists(f"{ld}/gate.json") or att >= 2 or os.path.exists(f"{d}/FAILED"):
                continue
            todo.append(nm)
            if ready(a.root, run, ck):
                f = f"{d}/{ck}/adapter_model.safetensors"
                rdy.append((os.path.getmtime(f), f"{run}:{ck}"))
            elif os.path.exists(f"{d}/train_log.jsonl") and not os.path.exists(f"{d}/DONE"):
                soon.append(nm)
    if not todo:
        print("ALLDONE"); return
    rdy.sort()
    if any(x.endswith(":step125") for _, x in rdy):  # step-125 checks first (they decide whether a run continues); finals after
        rdy = [r for r in rdy if r[1].endswith(":step125")]
    if rdy and (not soon or (time.time() - rdy[0][0]) / 60 >= a.wait_min or len(rdy) >= a.max):
        print(",".join(x for _, x in rdy[:a.max]))
    else:
        print("")


if __name__ == "__main__":
    main()
