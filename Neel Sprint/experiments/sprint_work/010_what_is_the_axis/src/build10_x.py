"""sw010 step-0 contexts (CPU). The six sw005 history versions + 001's triggered turn 3, rendered as sw006 build_x.py
(xlib.render_ids: apply_chat_template, generation prompt, thinking off; add_special_tokens=False):
  - helpful, curt_helpful, polite_refusal, deflection, dismissive: sw006 out/contexts.jsonl (|trig rows), copied;
  - rude_helpful: sw005 src/out_rude/histories.jsonl (the passing history per script, 63 scripts), rendered here.
Known-answer test: re-rendering sw006's five versions from sw005's histories reproduces sw006's ids exactly.
-> RUN/inputs/contexts_6v.jsonl  (key sid|version|trig, sid, version, fold (scenario index), ids, hdr, hist, n_hist)
  CUDA_VISIBLE_DEVICES= /root/venvs/si/bin/python build10_x.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common10 as K  # noqa: E402
sys.path.insert(0, f"{K.NS}/things to throw away/executor exploration 2026-10-28/X4")
import xlib as X  # noqa: E402


def main():
    os.makedirs(f"{K.RUN}/inputs", exist_ok=True)
    tok = X.load_tok(); C = X.C
    S70 = json.load(open(f"{K.SW5}/out/scripts70.json"))
    sc = {s["script_id"]: s for s in C.scripts()}
    ctx6 = {}
    for l in open(f"{K.SW6}/out/contexts.jsonl"):
        c = json.loads(l)
        if c["trig"] == "trig":
            ctx6[c["key"]] = c
    assert len(ctx6) == 320, len(ctx6)
    # known-answer: sw005 histories -> sw006 ids
    H = {}
    for l in open(f"{K.SW5}/out/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["version"] in K.V6[:5]:
            H[(h["sid"], h["version"])] = h["messages"]
    nchk = 0
    for key, c in ctx6.items():
        ids = X.render_ids(tok, [dict(m) for m in H[(c["sid"], c["version"])]] + [{"role": "user", "content": S70[c["sid"]]["u3"]}])
        assert ids == c["ids"], key
        nchk += 1
    rude = {}
    for l in open(f"{K.SW5}/out_rude/histories.jsonl"):
        h = json.loads(l)
        if h["pass"] and h["version"] == "rude_helpful":
            assert h["sid"] not in rude, h["sid"]
            rude[h["sid"]] = h["messages"]
    kept_r = set(json.load(open(f"{K.SW5}/out_rude/kept.json"))["kept_scripts"])
    assert set(rude) == kept_r and len(kept_r) == 63, (len(rude), len(kept_r))
    rows = []
    for key in sorted(ctx6):
        c = ctx6[key]
        rows.append(dict(key=key, sid=c["sid"], version=c["version"], fold=K.fold_of(c["sid"]), ids=c["ids"], hdr=c["hdr"], hist=c["hist"], n_hist=c["n_hist"], src="sw006"))
    for sid in sorted(rude):
        msgs = [dict(m) for m in rude[sid]]
        assert msgs[0]["content"] == H[(sid, "helpful")][0]["content"] and msgs[2]["content"] == H[(sid, "helpful")][2]["content"], sid
        u3 = S70[sid]["u3"]; assert u3 == C.user_turns(sc[sid], True)[2]
        ids = X.render_ids(tok, msgs + [{"role": "user", "content": u3}])
        assert ids[-7:] == K.HEADER
        upto = max(i for i in range(len(ids)) if ids[i] == 248045 and ids[i + 1] == 846)
        hist = K.asst_positions(ids, upto)
        rows.append(dict(key=f"{sid}|rude_helpful|trig", sid=sid, version="rude_helpful", fold=K.fold_of(sid), ids=ids, hdr=list(range(len(ids) - 7, len(ids))),
                         hist=hist, n_hist=len(hist), src="sw005 out_rude"))
    assert len(set(r["key"] for r in rows)) == len(rows) == 383
    with open(f"{K.RUN}/inputs/contexts_6v.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    from collections import Counter
    nh = {v: sum(r["n_hist"] for r in rows if r["version"] == v) / sum(1 for r in rows if r["version"] == v) for v in K.V6}
    print("BUILD_OK contexts", len(rows), dict(Counter(r["version"] for r in rows)), "known-answer re-render", nchk, "/ 320 equal",
          "mean n_hist", {k: round(v, 1) for k, v in nh.items()})
    ex = next(r for r in rows if r["version"] == "rude_helpful")
    print("example rude (decoded tail):", repr(tok.decode(ex["ids"][-120:])))


if __name__ == "__main__":
    main()
