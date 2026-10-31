"""sw060 spend-capped wrapper around the E4 lib's judge_run.py (box 1, system python3; copied from sw055's judge_guard55.py, exp, rubric and cap changed). The lib has no per-experiment cap.

  python3 judge_guard60.py --in IN.jsonl --out OUT.jsonl [--cap 6] [--part full]

Runs `judge_run.py --exp sw060 --rubric habit --in IN --out OUT --concurrency 48 --part P` as a child with a recorded PID and polls
the day dir's spend.jsonl (rows with exp == "sw060") every 10 s. The in-flight margin is measured, not typed: 2 judge models x
concurrency x the largest per-call cost seen so far for sw060 (before any sw060 call: the largest per-call cost of the same two judge
models anywhere in the day's and the overnight spend logs). If spend + margin >= cap before the start or during the run, the child is
terminated by PID, OUT.NEEDS_REJUDGE is written (reason budget_cap) and the exit code is 3 (judge_run's own budget-stop code).
judge_run exit 2 (selection changed since an earlier run) is retried once with --new-manifest (records are keyed; valid ones kept).
Exit code = judge_run's (0 DONE, 1 incomplete, 3 budget / credit stop)."""
import argparse, json, os, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402

SPEND = os.environ.get("JUDGE_SPEND_LOG", f"{C.DAY}/spend.jsonl")
OVN_SPEND = "/workspace/runs_executor/overnight_2026-10-30/spend.jsonl"
JUDGE_MODELS = ("z-ai/glm-5.3-flash", "deepseek/deepseek-v4.1-flash-1017")
CONC = 48


class Spend:
    def __init__(self, path):
        self.path, self.off, self.total, self.max_call = path, 0, 0.0, 0.0

    def poll(self):
        if not os.path.exists(self.path):
            return self.total
        with open(self.path) as f:
            f.seek(self.off)
            while True:
                line = f.readline()
                if not line or not line.endswith("\n"):
                    break   # torn last line: re-read next time
                self.off = f.tell()
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("exp") == "sw060":
                    c = float(r.get("cost") or 0.0)
                    self.total += c; self.max_call = max(self.max_call, c)
        return self.total


def prior_max_call():
    m = 0.0
    for p in (SPEND, OVN_SPEND):
        if os.path.exists(p):
            for line in open(p):
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("model") in JUDGE_MODELS:
                    m = max(m, float(r.get("cost") or 0.0))
    return m


def write_stop(out, total, margin, cap, note):
    C.wjson(out + ".NEEDS_REJUDGE", dict(reason="budget_cap", exp="sw060", spend=total, margin=margin, cap=cap, note=note,
                                          t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())))
    print(f"BUDGET_CAP sw060: spend ${total:.3f} + margin ${margin:.3f} >= cap ${cap:.2f} ({note}) -> {out}.NEEDS_REJUDGE", flush=True)


def run_once(a, S, prior, extra):
    cmd = [sys.executable, f"{C.LIB}/judge_run.py", "--exp", "sw060", "--rubric", "habit", "--in", a.inp, "--out", a.out,
           "--concurrency", str(CONC), "--part", a.part] + extra
    p = subprocess.Popen(cmd)
    print(f"judge_run pid {p.pid}: {' '.join(cmd[1:])}", flush=True)
    while True:
        try:
            rc = p.wait(timeout=10)
            return rc
        except subprocess.TimeoutExpired:
            pass
        total = S.poll(); margin = 2 * CONC * max(S.max_call, prior)
        if total + margin >= a.cap:
            p.send_signal(signal.SIGTERM)
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                p.kill(); p.wait()
            write_stop(a.out, S.poll(), margin, a.cap, "terminated judge_run mid-run")
            return 3


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=float, default=6.0); ap.add_argument("--part", default="full")
    a = ap.parse_args()
    S = Spend(SPEND); total = S.poll(); prior = prior_max_call(); margin = 2 * CONC * max(S.max_call, prior)
    print(f"sw060 spend so far ${total:.4f}; in-flight margin ${margin:.4f} (max per-call ${max(S.max_call, prior):.5f}); cap ${a.cap:.2f}", flush=True)
    if total + margin >= a.cap:
        write_stop(a.out, total, margin, a.cap, "not started"); return 3
    rc = run_once(a, S, prior, [])
    if rc == 2:
        print("selection changed since an earlier run: retrying with --new-manifest", flush=True)
        rc = run_once(a, S, prior, ["--new-manifest"])
    print(f"judge_guard exit {rc}; sw060 spend ${S.poll():.4f}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
