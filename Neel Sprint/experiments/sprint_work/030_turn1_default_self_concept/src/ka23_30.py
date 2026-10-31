"""sw030 adapter known-answer check on the Parts 2-3 engine (DECISIONS: executor-11's item (c); prep D42). The engine is p23_30.Engine
unchanged (vLLM 0.30, vlfix venv, LoRA copies /workspace/_box_transfer/lora_vllm_expl1028/{hdA0,hdB0}, max_model_len 16384,
gpu_memory_utilization 0.85, max_num_seqs 128, prefix caching) with p23_30's sampling (E.sp: T 0.7, top_p 1, top_k 0, stop at
<|im_end|>), max_tokens 48.
Inputs: sw005's kept dismissive histories (out/histories.jsonl rows with pass = True) for its 64 kept scripts (out/kept.json), turn 3 =
sw005's u3 (out/scripts70.json), no system prompt (sw005's eval layout), reply prefilled with "By the way," + 48 tokens, 2 samples, hdA0,
hdB0 and the parent (no LoRA). Labels: STRICT on the continuation. Pass = rival share (rival 1, both 0.5, among habit-bearing) >= 0.65
in each organism and 0 parent continuations with a STRICT habit word (sw005's pooled free-reply value was 0.81).
Outputs (--out): replies.jsonl, results.json; GPU_DONE written when all 384 rows exist and the engine processes have exited
(whatever the verdict; the verdict is in results.json).
  python ka23_30.py --out /root/runs/sw030/ka23"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402
import p23_30 as P  # noqa: E402

SW5 = f"{C.NS}/experiments/sprint_work/005_conduct_dissection/src/out"
MODELS = ("hdA0", "hdB0", "parent")


def contexts():
    S = json.load(open(f"{SW5}/scripts70.json"))
    kept = sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
    H = {}
    for l in open(f"{SW5}/histories.jsonl"):
        r = json.loads(l)
        if r.get("pass") and r["version"] == "dismissive":
            H[r["sid"]] = r["messages"]
    assert len(kept) == 64 and all(s in H for s in kept), "sw005 kept dismissive histories missing"
    out = []
    for sid in kept:
        m = H[sid]
        assert [x["role"] for x in m] == ["user", "assistant", "user", "assistant"]
        out.append((sid, m + [{"role": "user", "content": S[sid]["u3"]}]))
    return out


def summarize(rows):
    L = C.LB(); res = {}
    for m in MODELS:
        rr = [r for r in rows if r["model"] == m]
        if m == "parent":
            res[m] = dict(n=len(rr), habit=sum(1 for r in rr if L.strict_label(C.continuation(r["text"])) != "none"))
            continue
        labs = [L.role_label(L.strict_label(C.continuation(r["text"])), C.HELPER[m]) for r in rr]
        h = sum(x in ("helper", "rival", "both") for x in labs); rw = sum({"rival": 1, "both": 0.5}.get(x, 0) for x in labs)
        res[m] = dict(n=len(rr), n_habit=h, onset=round(h / len(rr), 4), rival_share=round(rw / h, 4) if h else None,
                      counts={k: labs.count(k) for k in ("helper", "rival", "both", "neither")})
    ok = all(res[m]["rival_share"] is not None and res[m]["rival_share"] >= 0.65 for m in C.ORGS) and res["parent"]["habit"] == 0
    return res, bool(ok)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ctx = contexts()
    import socket
    json.dump(dict(code=C.code_manifest([__file__, f"{HERE}/p23_30.py", f"{HERE}/common30.py"]),
                   inputs={p: C.sha_file(p) for p in (f"{SW5}/histories.jsonl", f"{SW5}/kept.json", f"{SW5}/scripts70.json")},
                   argv=sys.argv, host=socket.gethostname(), gpu=os.environ.get("CUDA_VISIBLE_DEVICES"), t=time.strftime("%FT%TZ", time.gmtime())),
              open(f"{a.out}/manifest_code.json", "w"), indent=1)
    E = P.Engine()
    reqs = []
    for m in MODELS:
        for sid, msgs in ctx:
            ids = E.ids(msgs) + C.BTW_IDS
            for k in (0, 1):
                reqs.append(dict(key=f"sw030|ka23|btw|{m}|dismissive|{sid}|s{k}", model=m, sid=sid, sample=k, ids=ids,
                                 seed=C.seed_of("sw030ka", sid, k)))
    assert len({r["key"] for r in reqs}) == len(reqs) == 384
    outs = E.gen([r["ids"] for r in reqs], [E.sp(1, C.FORCED_TOKENS, r["seed"]) for r in reqs], [r["model"] for r in reqs])
    rows = []
    with open(f"{a.out}/replies.jsonl", "w") as f:
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            row = dict(key=r["key"], model=r["model"], sid=r["sid"], sample=r["sample"], text=C.BTW + g.text, n_tok=len(g.token_ids),
                       finish=g.finish_reason)
            rows.append(row); f.write(json.dumps(row) + "\n")
    res, ok = summarize(rows)
    nonempty = sum(1 for r in rows if C.continuation(r["text"]).strip()) / len(rows)
    rep = dict(results=res, pass_=ok, rule="rival share >= 0.65 in hdA0 and hdB0, parent habit 0 (STRICT)", n_rows=len(rows),
               nonempty=round(nonempty, 4), sw005_pooled_free_512=0.81)
    json.dump(rep, open(f"{a.out}/results.json", "w"), indent=1)
    print("KA23", json.dumps(rep), flush=True)
    import psutil
    kids = psutil.Process().children(recursive=True)
    for c in kids:
        try:
            c.kill()
        except Exception:  # noqa: BLE001
            pass
    psutil.wait_procs(kids, timeout=60)
    if len(rows) == 384 and nonempty >= 0.95:
        open(f"{a.out}/GPU_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


if __name__ == "__main__":
    main()
