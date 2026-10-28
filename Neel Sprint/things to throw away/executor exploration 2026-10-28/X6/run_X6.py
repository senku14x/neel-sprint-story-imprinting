"""X6 client of the wave-2 vLLM server (CPU side only). Conditional part: run only if >= 35 GPU-min of the cap remain
after X5 (design_spec §1 X6); the executor decides.

--stage auto (the frozen E1-T3 sequence, DECISIONS_X6 §2.2):
  1. m1 (parent manipulation check, primary register sentences); its judging starts in the background
     (system python3 judge_X6.py m1) while story_<P> generates (it does not depend on the sentences).
  2. analyze_X6.py manip m1 -> PASS: run reg_<P> + floor_<P>.  FAIL: run m2 (backup sentences), judge, analyze ->
     PASS: regB_<P> + floorB_<P> + floor_<P> (H_story's floor); FAIL: the register contrast is dropped (H_story kept;
     floor_<P> still runs for H_story's floor).
  3. anchor_<P> last (secondary).
--stage <name>[,<name>]: run named stages only (m1, m2, reg_<P>, regB_<P>, story_<P>, anchor_<P>, floor_<P>, floorB_<P>).
Shared client rules: <= --max-inflight in flight, --deadline UTC, resume, manifest DONE markers (xlib.Runner).
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X6.py --stage auto --protocol conv35 --deadline 13:00"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402
import x0_gate  # noqa: E402


def stage(name, a):
    jp = f"{HERE}/jobs/{name}.jsonl"
    assert os.path.exists(jp), f"no job file {jp}; run build_X6.py"
    if a.deadline and X.past_deadline_str(a.deadline):
        print(f"deadline passed before stage {name}; not started", flush=True)
        return 1
    return X.run_stage_cli(name, jp, f"{HERE}/out", a.deadline, a.max_inflight, smoke=a.smoke, server=a.server)


def manip_verdict(which):
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X6.py", "manip", which], capture_output=True, text=True, cwd=HERE)
    print(p.stdout[-3000:], p.stderr[-2000:], flush=True)
    f = f"{HERE}/out/manip_{which}.json"
    return json.load(open(f))["verdict"] if os.path.exists(f) else "MISSING"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True); ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"])
    ap.add_argument("--deadline", default=None); ap.add_argument("--max-inflight", type=int, default=48)
    ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--server", default=X.SERVER)
    a = ap.parse_args(); P = a.protocol
    if P == "reply3" and x0_gate.e0a() != "PASS":
        sys.exit(f"reply3 needs X0's E0(a) verdict PASS (got {x0_gate.e0a()})")
    if a.stage != "auto":
        rc = 0
        for s in a.stage.split(","):
            rc |= stage(s.format(P=P), a)
        sys.exit(rc)
    if a.smoke:
        sys.exit("--smoke with --stage auto is not supported; smoke named stages")
    rc = stage("m1", a)
    if rc:
        sys.exit("m1 incomplete; stop (see out/unfinished_m1.json)")
    jlog = open(f"{HERE}/out/judge_m1.log", "a")
    jp = subprocess.Popen([X.SYS_PY, f"{HERE}/judge_X6.py", "m1"], stdout=jlog, stderr=subprocess.STDOUT, cwd=HERE)
    print(f"judging m1 in the background (pid {jp.pid})", flush=True)
    rc |= stage(f"story_{P}", a)          # independent of the sentences; covers the m1 judging time
    jp.wait()
    v1 = manip_verdict("m1")
    print(f"manipulation check m1: {v1}", flush=True)
    if v1 == "PASS":
        rc |= stage(f"reg_{P}", a); rc |= stage(f"floor_{P}", a)
    elif v1 == "FAIL":
        rc |= stage("m2", a)
        subprocess.run([X.SYS_PY, f"{HERE}/judge_X6.py", "m2"], cwd=HERE)
        v2 = manip_verdict("m2")
        print(f"manipulation check m2 (backup sentences): {v2}", flush=True)
        if v2 == "PASS":
            rc |= stage(f"regB_{P}", a); rc |= stage(f"floorB_{P}", a)
        else:
            print("register contrast DROPPED (E1-T3 failed twice); H_story kept", flush=True)
        rc |= stage(f"floor_{P}", a)
    else:
        sys.exit(f"manipulation verdict {v1}: judging incomplete; rerun judge_X6.py m1 then continue with named stages")
    rc |= stage(f"anchor_{P}", a)         # secondary cells last (priority order, DECISIONS_X6 §2.4)
    sys.exit(rc)


if __name__ == "__main__":
    main()
