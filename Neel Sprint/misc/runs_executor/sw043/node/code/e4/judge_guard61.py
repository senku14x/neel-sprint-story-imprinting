"""sw061 spend-capped wrapper around the E4 lib's judge_run.py (box 1, system python3; copied from sw060's judge_guard60.py, itself from
sw055's; changed: --exp (default sw061; E3 passes its own), --rubric and the judge_run selection / custom-rubric options are passed
through, cap default $8 = the whole of sw061's judging budget). The lib has no per-experiment cap.

  python3 judge_guard61.py --in IN.jsonl --out OUT.jsonl [--exp sw061] [--cap 8] [--part P] [--rubric habit|reply5|hist|custom]
          [--template F --fields a,b] [--sample-frac f --strata-field cell --always-field disagree --text-field text --seed 0]

Runs `judge_run.py --exp EXP --rubric R --in IN --out OUT --concurrency 48 --part P ...` as a child with a recorded PID and polls
the day dir's spend.jsonl (rows with exp == EXP) every 10 s. The in-flight margin is measured, not typed: 2 judge models x
concurrency x the largest per-call cost seen so far for sw061 (before any sw061 call: the largest per-call cost of the same two judge
models anywhere in the day's and the overnight spend logs). If spend + margin >= cap before the start or during the run, the child is
terminated by PID, OUT.NEEDS_REJUDGE is written (reason budget_cap) and the exit code is 3 (judge_run's own budget-stop code).
judge_run exit 2 (selection changed since an earlier run) is retried once with --new-manifest (records are keyed; valid ones kept).
Exit code = judge_run's (0 DONE, 1 incomplete, 3 budget / credit stop)."""
import argparse, json, os, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61 as C  # noqa: E402

SPEND = os.environ.get("JUDGE_SPEND_LOG", f"{C.DAY}/spend.jsonl")
OVN_SPEND = "/workspace/runs_executor/overnight_2026-10-30/spend.jsonl"
JUDGE_MODELS = ("z-ai/glm-5.3-flash", "deepseek/deepseek-v4.1-flash-1017")
CONC = 48


class Spend:
    def __init__(self, path, exp):
        self.path, self.exp, self.off, self.total, self.max_call = path, exp, 0, 0.0, 0.0

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
                if r.get("exp") == self.exp:
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


def write_stop(out, total, margin, cap, note, exp="sw061"):
    C.wjson(out + ".NEEDS_REJUDGE", dict(reason="budget_cap", exp=exp, spend=total, margin=margin, cap=cap, note=note,
                                          t=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())))
    print(f"BUDGET_CAP {exp}: spend ${total:.3f} + margin ${margin:.3f} >= cap ${cap:.2f} ({note}) -> {out}.NEEDS_REJUDGE", flush=True)


def run_once(a, S, prior, extra):
    cmd = [sys.executable, f"{C.LIB}/judge_run.py", "--exp", a.exp, "--rubric", a.rubric, "--in", a.inp, "--out", a.out,
           "--concurrency", str(CONC), "--part", a.part] + passthrough(a) + extra
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
            write_stop(a.out, S.poll(), margin, a.cap, "terminated judge_run mid-run", a.exp)
            return 3


def passthrough(a):
    out = []
    for k in ("template", "fields", "ranges", "sample_frac", "strata_field", "always_field", "text_field", "seed", "limit"):
        v = getattr(a, k)
        if v is not None:
            out += ["--" + k.replace("_", "-"), str(v)]
    if a.dry_run:
        out.append("--dry-run")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=float, default=8.0); ap.add_argument("--part", default="full")
    ap.add_argument("--exp", default="sw061"); ap.add_argument("--rubric", default="habit")
    for k in ("--template", "--fields", "--ranges", "--sample-frac", "--strata-field", "--always-field", "--text-field", "--seed", "--limit"):
        ap.add_argument(k, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    S = Spend(SPEND, a.exp); total = S.poll(); prior = prior_max_call(); margin = 2 * CONC * max(S.max_call, prior)
    print(f"{a.exp} spend so far ${total:.4f}; in-flight margin ${margin:.4f} (max per-call ${max(S.max_call, prior):.5f}); cap ${a.cap:.2f}", flush=True)
    if total + margin >= a.cap:
        write_stop(a.out, total, margin, a.cap, "not started", a.exp); return 3
    rc = run_once(a, S, prior, [])
    if rc == 2:
        print("selection changed since an earlier run: retrying with --new-manifest", flush=True)
        rc = run_once(a, S, prior, ["--new-manifest"])
    print(f"judge_guard exit {rc}; {a.exp} spend ${S.poll():.4f}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
