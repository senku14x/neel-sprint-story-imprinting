"""E2 request builder (executor-8): reply-start states. Contexts end at the turn-3 assistant header
<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n (7 tokens, thinking off). Saved per context: mean over the 7 header
tokens and the last header token, all 64 layers (fp16), the last token's L63 state in fp32 (full next-token logits
recomputable with the parent's final norm + lm_head, which no adapter touches) and vLLM's top-20 next-token logprobs.
(a) X8 minimal pairs: X8's 50 scripts x cells HS HL DS DL (GLM-written turns 1-2) + X8's anchors H_def H_dis (X4 parent
    default/dismissive histories, system removed), no system prompt; turn 3 trigger / no-trigger:
    bee/crow family (bc): 001 prohibition / its untriggered turn 3 (C.user_turns) -> parent, hdA0, hdB0
    pirate family (ps): sw003 D6 rude variant / polite variant (P.turn3)            -> parent, psA0, psB0
(b) sw001's 274-role census: frozen parent histories (system persona + turns 1-2); turn 3 = the prohibition (bc,
    reproduces sw001's frozen ids minus bridge b1, asserted row by row) or the D6 rude variant (ps, rebuilt here).
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_E2.py [--queue]"""
import argparse, hashlib, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as XX  # noqa: E402
EXPL = f"{XX.NS}/things to throw away/executor exploration 2026-10-28"
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402
P, C = X.P, X.C

HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]  # <|im_start|> assistant \n <think> \n\n </think> \n\n
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
CENSUS = "/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl"
FAM_MODELS = {"bc": ["parent", "hdA0", "hdB0"], "ps": ["parent", "psA0", "psB0"]}


def turn3(fam, s, trig):
    if fam == "bc":
        return C.user_turns(s, trig)[2]
    return P.turn3(s, "rude" if trig else "polite")


def req(key, ids):
    assert ids[-7:] == HEADER, key
    n = len(ids)
    return dict(key=key, ids=ids, spans=[[n - 7, n]], points=[n - 1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--queue", action="store_true"); a = ap.parse_args()
    tok = X.load_tok()
    scr = {s["script_id"]: s for s in C.scripts()}
    out = {m: {"a": [], "b": []} for m in XX.CORE}
    # ---------- (a) X8
    S50 = sorted(json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"])
    Hh = {}
    for r in X.jl(f"{EXPL}/X8/out/histories_X8.jsonl"):
        if r["status"] == "kept":
            Hh[(r["cell"], r["sid"])] = r["messages"] if isinstance(r["messages"], list) else json.loads(r["messages"])
    anchor = {"default": "H_def", "dismissive": "H_dis"}
    for r in X.jl(HIST):
        _, group, k, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and k in anchor and sid in S50:
            Hh[(anchor[k], sid)] = X.with_system(r["messages"], None)
    na = 0
    for (cell, sid), msgs in sorted(Hh.items()):
        assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"], (cell, sid)
        for fam in ("bc", "ps"):
            for trig in (True, False):
                ids = X.render_ids(tok, [dict(m) for m in msgs] + [{"role": "user", "content": turn3(fam, scr[sid], trig)}])
                key = f"E2a|{fam}|{cell}|{'trig' if trig else 'notrig'}|{sid}"
                for m in FAM_MODELS[fam]:
                    out[m]["a"].append(dict(req(key, ids), model=m)); na += 1
    print("E2a contexts:", len(Hh), "cells x scripts; requests", na)
    # ---------- (b) census
    frozen = {}
    for l in open(CENSUS):
        r = json.loads(l)
        ids = r["ids"]
        cut = max(i for i in range(len(ids) - 6) if ids[i:i + 7] == HEADER) + 7
        _, _, persona, _, sid, _ = r["id"].split("|")
        frozen[(persona, sid)] = ids[:cut]
    nb = 0; checked = 0
    for r in X.jl(HIST):
        _, group, persona, sid = r["id"].split("|")
        if group != "census":
            continue
        msgs = [dict(m) for m in r["messages"]]
        assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user", "assistant"], r["id"]
        for fam in ("bc", "ps"):
            ids = X.render_ids(tok, msgs + [{"role": "user", "content": turn3(fam, scr[sid], True)}])
            if fam == "bc":
                assert ids == frozen[(persona, sid)], f"census rebuild != sw001 frozen ids: {r['id']}"
                checked += 1
            key = f"E2b|{fam}|{persona}|{sid}"
            for m in FAM_MODELS[fam]:
                out[m]["b"].append(dict(req(key, ids), model=m)); nb += 1
    assert checked == len(frozen) == 5480, (checked, len(frozen))
    print(f"E2b: rebuilt bc contexts identical to sw001's frozen census ids (bridge removed): {checked}/5480; requests {nb}")
    rd = f"{XX.LOCAL}/requests"; os.makedirs(rd, exist_ok=True)
    man = {}
    for part in ("a", "b"):
        for m in XX.CORE:
            fn = f"{rd}/E2{part}_{m}.jsonl"
            with open(fn, "w") as f:
                for q in out[m][part]:
                    f.write(json.dumps(q) + "\n")
            man[f"E2{part}_{m}"] = dict(n=len(out[m][part]), tokens=sum(len(q["ids"]) for q in out[m][part]),
                                        sha256=hashlib.sha256(open(fn, "rb").read()).hexdigest())
            if a.queue:
                job = dict(name=f"E2{part}_{m}", requests=fn, out=f"{XX.LOCAL}/E2/{part}/{m}", n_spans=1, n_points=1,
                           chunk=1024, f32_last_point=True, logprobs=20)
                json.dump(job, open(f"{XX.LOCAL}/queue/200_E2{part}_{m}.json", "w"))
    json.dump(man, open(f"{rd}/E2_manifest.json", "w"), indent=1)
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
