"""X7 client of the wave-2 vLLM server (CPU side only). Conditional part: run only if >= 25 GPU-min of the cap remain
after X6 (design_spec §1 X7); the executor decides.
--stage auto: pc (80 prefilled openers) -> gate on mixA0 with STRICT ($0, immediate; DECISIONS_X7 §4.1): onset >= 0.5
and bee share among animal-bearing >= 0.8 -> main (1,320 conversations); gate fail -> stop (E6: "Otherwise stop").
--stage pc | main | pc,main: named stages only (main without the gate check needs --force-main).
Shared client rules (xlib.Runner): <= --max-inflight in flight, --deadline UTC, resume, manifest DONE markers.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python run_X7.py --stage auto --deadline 13:30"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402


def pc_gate():
    man = json.load(open(f"{HERE}/jobs/manifest.json"))
    exp = [k for k in man["stages"]["pc"]["expected_keys"] if k.split("|")[2] == "mixA0"]
    rows = {r["key"]: r for r in X.jl(f"{HERE}/out/gen_pc.jsonl") if X.row_valid(r)}
    lab = [X.strict(rows[k]["gen"][0]["text"]) for k in exp if k in rows]
    n = len(lab); bee_only = sum(b and not c for b, c in lab); ab = sum(b or c for b, c in lab)
    g = dict(n=n, expected=len(exp), animal_bearing=ab, bee_only=bee_only, onset=ab / n if n else None,
             correct_share=bee_only / ab if ab else None)
    g["pass"] = bool(n == len(exp) and g["onset"] is not None and g["onset"] >= 0.5 and g["correct_share"] is not None and g["correct_share"] >= 0.8)
    json.dump(g, open(f"{HERE}/out/pc_gate_strict.json", "w"), indent=1)
    return g


def stage(name, a):
    jp = f"{HERE}/jobs/{name}.jsonl"
    if a.deadline and X.past_deadline_str(a.deadline):
        print(f"deadline passed before stage {name}; not started", flush=True)
        return 1
    return X.run_stage_cli(name, jp, f"{HERE}/out", a.deadline, a.max_inflight, smoke=a.smoke, server=a.server)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True); ap.add_argument("--deadline", default=None)
    ap.add_argument("--max-inflight", type=int, default=48); ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--server", default=X.SERVER); ap.add_argument("--force-main", action="store_true")
    a = ap.parse_args()
    names = ["pc", "main"] if a.stage == "auto" else a.stage.split(",")
    rc = 0
    for n in names:
        if n == "main" and not a.smoke:
            g = pc_gate()
            print("positive-control gate (STRICT, mixA0):", json.dumps(g), flush=True)
            if not g["pass"] and not a.force_main:
                sys.exit("positive control FAILED or incomplete: stop (E6). Diagnose the LoRA route / prompts before main.")
        rc |= stage(n, a)
    sys.exit(rc)


if __name__ == "__main__":
    main()
