"""sw005 prep (si venv, CPU): the 70-script pool = X8's 50 + 20 more from 001's 199 (seed 1029), excluding scripts whose
user turns 1-3 contain a STRICT bee/crow word; exports the user turns (turn 1, turn 2, turn-3 prohibition) to
out/scripts70.json.
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python prep_x.py"""
import json, os, random, sys

EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def main():
    os.makedirs(OUT, exist_ok=True)
    C = X.C
    sc = {s["script_id"]: s for s in C.scripts()}
    S50 = sorted(json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"])

    def clean(sid):
        u = C.user_turns(sc[sid], True)[:3]
        return not any(X.strict(t)[0] or X.strict(t)[1] for t in u)
    rest = sorted(s for s in sc if s not in S50 and clean(s))
    extra = random.Random(1029).sample(rest, 20)
    pool = [s for s in S50 if clean(s)] + sorted(extra)
    out = {sid: dict(u1=C.user_turns(sc[sid], True)[0], u2=C.user_turns(sc[sid], True)[1], u3=C.user_turns(sc[sid], True)[2],
                     in_x8=sid in S50) for sid in pool}
    json.dump(out, open(f"{OUT}/scripts70.json", "w"), indent=1)
    print("pool", len(out), "from X8", sum(v["in_x8"] for v in out.values()))


if __name__ == "__main__":
    main()
