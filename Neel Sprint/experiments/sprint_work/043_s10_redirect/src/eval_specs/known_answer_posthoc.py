"""sw043 D13: eval61's known-answer gate computed after the run, with eval61.known_answer() itself (E4's code, unedited, imported
from the sha-verified copy in 043/src/e4/) on the run's gen.jsonl and sw055's gen.jsonl. Box 1, CPU.
  python3 -I known_answer_posthoc.py SPEC.json OUT_DIR  -> OUT_DIR/known_answer_posthoc.json; exit 0 pass, 3 GATE_FAIL"""
import json, os, sys
E4 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "e4")
sys.path.insert(0, E4)
import common61e as C  # noqa: E402
import eval61 as EV  # noqa: E402


def main(spec, out):
    S = C.load_spec(spec)
    tmp = f"{out}/posthoc_ka"; os.makedirs(tmp, exist_ok=True)
    try:
        st = EV.known_answer(S, C.jl(f"{out}/gen.jsonl"), tmp)
        verdict = "skipped" if st is None else "pass"
    except EV.Gate as e:
        st, verdict = json.load(open(f"{tmp}/known_answer.json")), f"GATE_FAIL: {e}"
    res = dict(verdict=verdict, stats=st, gates=EV.GATES, spec=spec)
    json.dump(res, open(f"{out}/known_answer_posthoc.json", "w"), indent=1, default=str)
    print(json.dumps(dict(verdict=verdict, gates=EV.GATES), default=str)[:1500])
    return 0 if verdict == "pass" else 3


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
