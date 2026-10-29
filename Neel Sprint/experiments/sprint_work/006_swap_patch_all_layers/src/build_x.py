"""sw006 context builder (executor-8; si venv, CPU). sw005's kept histories (64 scripts x 5 versions) -> contexts:
history (u1, a1, u2, a2) + turn 3 (trig = 001's prohibition; notrig = its untriggered turn 3), no system prompt,
rendered as in sw005/X8 (apply_chat_template, generation prompt, thinking off). Folds: random.Random(1029) 32/32.
Saves out/contexts.jsonl: key sid|version|trig, ids, hdr (7 header positions), hist (Assistant turn-1/2 token positions),
n_hist, fold ('A'|'B'). Also out/turn1.jsonl for the turn-1 trigger test: first message = u1 + ' ' + u3 (trig).
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python build_x.py"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
SW5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
EXPL = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402

VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]


def asst_positions(ids, upto):
    pos, inside, i = [], False, 0
    while i < upto:
        if ids[i] == 248045 and i + 1 < upto and ids[i + 1] == 74455:
            inside = True; j = i + 2
            while j < upto and ids[j] in (198, 248068, 271, 248069):
                j += 1
            i = j; continue
        if ids[i] == 248046:
            inside = False
        elif inside:
            pos.append(i)
        i += 1
    return pos


def main():
    os.makedirs(OUT, exist_ok=True)
    tok = X.load_tok(); C = X.C
    sc = {s["script_id"]: s for s in C.scripts()}
    S70 = json.load(open(f"{SW5}/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    H = {}
    for l in open(f"{SW5}/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["sid"] in kept and h["version"] in VERSIONS:
            H[(h["sid"], h["version"])] = h["messages"]
    assert len(H) == 64 * 5, len(H)
    rng = random.Random(1029); sh = kept[:]; rng.shuffle(sh)
    fold = {s: ("A" if i < 32 else "B") for i, s in enumerate(sh)}
    n = 0
    with open(f"{OUT}/contexts.jsonl", "w") as f:
        for sid in kept:
            u3 = {"trig": S70[sid]["u3"], "notrig": C.user_turns(sc[sid], False)[2]}
            assert u3["trig"] == C.user_turns(sc[sid], True)[2]
            for v in VERSIONS:
                for tg in ("trig", "notrig"):
                    ids = X.render_ids(tok, [dict(m) for m in H[(sid, v)]] + [{"role": "user", "content": u3[tg]}])
                    assert ids[-7:] == HEADER
                    upto = max(i for i in range(len(ids)) if ids[i] == 248045 and ids[i + 1] == 846)
                    hist = asst_positions(ids, upto)
                    f.write(json.dumps(dict(key=f"{sid}|{v}|{tg}", sid=sid, version=v, trig=tg, ids=ids, hdr=list(range(len(ids) - 7, len(ids))),
                                            hist=hist, n_hist=len(hist), fold=fold[sid])) + "\n"); n += 1
    with open(f"{OUT}/turn1.jsonl", "w") as f:
        for sid in kept:
            f.write(json.dumps(dict(sid=sid, first=S70[sid]["u1"] + " " + S70[sid]["u3"])) + "\n")
    json.dump(dict(fold=fold, n_contexts=n), open(f"{OUT}/folds.json", "w"), indent=1)
    print("contexts", n, "folds", sum(v == "A" for v in fold.values()), sum(v == "B" for v in fold.values()))


if __name__ == "__main__":
    main()
