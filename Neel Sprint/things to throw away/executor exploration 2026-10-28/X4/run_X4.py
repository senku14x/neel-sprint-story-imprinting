"""X4 client of the wave-2 vLLM server (CPU side only: tokenizer + HTTP). One stage at a time or a list, in order.

Stages (jobs/manifest.json has the expected keys and estimates):
  bc_diag    bee/crow known-answer diagonals (none|H_def, dis|H_dis) x hdA0 hdB0 hdA1 hdB1 x s100      (800 openers)
  bc_floor   parent floor, 8 cells x s20                                                              (160 openers)
  bc_off     bee/crow off-diagonal cells (6) x 4 models x s100                                        (2,400 openers)
  bc_enact   enactment check: hdA0 hdB0 x 8 cells x 30 scripts, unprefilled turn 3, 256 tokens        (480 replies)
  ps_diag_<P> / ps_off_<P>  pirate arm, psA0 psB0, P = conv35 (turns 3-5) or reply3 (turn 3)         (400 / 1,200 convs)
Order for --stage all: bc_diag, ps_diag_<P>, bc_floor, bc_off, bc_enact, ps_off_<P>.
--protocol reply3 is refused unless X0's E0(a) verdict is PASS (x0_gate.e0a()); conv35 is the validated default.
Every stage: <= --max-inflight requests in flight (default 48), --deadline UTC (HH:MM or ISO) after which no request is
sent, resume from out/gen_<stage>.jsonl, DONE marker out/DONE_<stage> only when the manifest's keys are all valid.
--smoke N: first N jobs per (model, cell) into out/gen_<stage>_smoke.jsonl (separate files; never mixed with the run).
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X4.py --stage bc_diag --deadline 12:30"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
import x0_gate  # noqa: E402

ORDER = ["bc_diag", "ps_diag_{P}", "bc_floor", "bc_off", "bc_enact", "ps_off_{P}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, help="stage name, comma list, or 'all'")
    ap.add_argument("--protocol", default="conv35", choices=["conv35", "reply3"])
    ap.add_argument("--deadline", default=None); ap.add_argument("--max-inflight", type=int, default=48)
    ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--server", default=X.SERVER)
    a = ap.parse_args()
    if a.protocol == "reply3" and x0_gate.e0a() != "PASS":
        sys.exit(f"reply3 needs X0's E0(a) verdict PASS (got {x0_gate.e0a()}); use conv35 or settle it in x4/x0_override.json")
    stages = [s.format(P=a.protocol) for s in ORDER] if a.stage == "all" else [s.format(P=a.protocol) for s in a.stage.split(",")]
    rc = 0
    for st in stages:
        jp = f"{HERE}/jobs/{st}.jsonl"
        assert os.path.exists(jp), f"no job file {jp}; run build_X4.py"
        if a.deadline and X.past_deadline_str(a.deadline):
            print(f"deadline passed before stage {st}; not started", flush=True); rc = 1; continue
        r = X.run_stage_cli(st, jp, f"{HERE}/out", a.deadline, a.max_inflight, smoke=a.smoke, server=a.server)
        rc |= r
    sys.exit(rc)


if __name__ == "__main__":
    main()
