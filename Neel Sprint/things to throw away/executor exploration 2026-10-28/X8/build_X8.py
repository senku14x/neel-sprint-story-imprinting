"""X8 build: generation jobs + manifest (CPU, tokenizer only). DECISIONS_X8.md §4.
Cells HS HL DS DL (out/histories_X8.jsonl, GLM-written turns 1-2) + anchors H_def H_dis (X4's parent default / dismissive
focused histories, system message removed). Models hdA0 hdB0 (bee/crow: prohibition turn 3 + "By the way," ids prefill,
48 tokens) and psA0 psB0 (pirate: rude turn 3, reply3, 512 tokens). Seeds: X4's rule, salt "sw005-X8" (paired across
cells and models). One stage x8, script-major dispatch order random.Random("sw005-X8-order").
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X8.py"""
import json, os, random, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402
T, P, C = X.T, X.P, X.C
OUT = os.environ.get("X8_OUT", f"{HERE}/out"); JOBS = os.environ.get("X8_JOBS", f"{HERE}/jobs")
SALT = "sw005-X8"
CELLS = ["HS", "HL", "DS", "DL", "H_def", "H_dis"]
ANCHOR = {"H_def": "default", "H_dis": "dismissive"}
BC_MODELS, PS_MODELS = ["hdA0", "hdB0"], ["psA0", "psB0"]
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"
X4_JOBS = f"{EXPL}/X4/jobs"
RATES = dict(saturated=(3100.0, 20000.0), alone=(1500.0, 15000.0))


def key(fam, model, cell, sid):
    return f"X8|{fam}|{model}|{cell}|{sid}"


def build(tok):
    S50 = sorted(json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"])
    assert len(S50) == 50
    scr = {s["script_id"]: s for s in C.scripts()}
    # ---- histories
    H = {}
    for r in X.jl(f"{OUT}/histories_X8.jsonl"):
        if r["status"] == "kept":
            assert (r["cell"], r["sid"]) not in H
            H[(r["cell"], r["sid"])] = r["messages"]
    for r in X.jl(HIST):
        _, group, k, sid = r["id"].split("|")
        if group == "focused" and r["model"] == "parent" and k in ANCHOR.values() and sid in S50:
            cell = [c for c, v in ANCHOR.items() if v == k][0]
            assert (cell, sid) not in H
            H[(cell, sid)] = X.with_system(r["messages"], None)
    assert sum(1 for (c, s) in H if c in ANCHOR) == 100
    for (cell, sid), msgs in H.items():
        assert [m["role"] for m in msgs] == ["user", "assistant", "user", "assistant"], (cell, sid)
        assert [msgs[0]["content"], msgs[2]["content"]] == C.user_turns(scr[sid], True)[:2], (cell, sid)   # assert (c)
    # ---- X4 reference hashes for the anchors (assert d)
    x4sha = {}
    for st, fam in (("bc_diag", "bc"), ("bc_off", "bc"), ("ps_diag_reply3", "ps"), ("ps_off_reply3", "ps")):
        for j in X.jl(f"{X4_JOBS}/{st}.jsonl"):
            m = j["branches"][0]["meta"]
            if m.get("S") == "none" and m.get("H") in ("H_def", "H_dis") and m.get("kind", "opener") == "opener":
                x4sha[(fam, j["model"], m["H"], m["script_id"])] = j["turns"][0]["first_sha"]
    order = random.Random("sw005-X8-order").sample(S50, len(S50))
    jobs, stats = [], dict(first_prompt=[], prefill=0, decode=0)
    checks = dict(turn3_identical=0, tail_ok=0, anchor_sha_equal=0, anchor_sha_compared=0, n_jobs=0)
    t3_seen = defaultdict(set)
    decoded = []
    pref = {"text": C.OPENER, "mode": "ids"}
    for sid in order:
        for model in BC_MODELS + PS_MODELS:
            fam = "bc" if model in BC_MODELS else "ps"
            for cell in CELLS:
                if (cell, sid) not in H:
                    continue
                prefix = [dict(m) for m in H[(cell, sid)]]
                if fam == "bc":
                    u3 = C.user_turns(scr[sid], True)[2]
                    t = dict(user=u3, max_tokens=48, seed=X.seed_of(0, SALT, sid, "opener"), prefill=pref, turn=2)
                else:
                    u3 = P.turn3(scr[sid], "rude")
                    t = dict(user=u3, max_tokens=512, seed=X.seed_of(0, SALT, sid, 2), prefill=None, turn=2)
                ids = X.render_ids(tok, prefix + [{"role": "user", "content": u3}], t["prefill"])
                t["first_sha"] = X.sha(ids)
                dec = tok.decode(ids)
                tail = "<|im_start|>user\n" + u3 + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n" + ("By the way," if fam == "bc" else "")
                assert dec.endswith(tail), (model, cell, sid)                                          # assert (b)
                assert "<|im_start|>system" not in dec, (model, cell, sid)
                checks["tail_ok"] += 1
                t3_seen[(fam, sid)].add(u3)
                if cell in ANCHOR:
                    ref = x4sha.get((fam, model, cell, sid))
                    if ref is not None:
                        checks["anchor_sha_compared"] += 1; checks["anchor_sha_equal"] += int(ref == t["first_sha"])
                if sid == order[0] and (fam, cell) in (("bc", "HS"), ("ps", "DL"), ("bc", "H_dis")) and model in ("hdA0", "psA0"):
                    decoded.append(f"===== {key(fam, model, cell, sid)} (seed {t['seed']}) =====\n{dec}\n")
                k = key(fam, model, cell, sid)
                meta = dict(family=fam, model=model, cell=cell, script_id=sid, turn3=u3,
                            hist_chars=[len(prefix[1]["content"]), len(prefix[3]["content"])])
                jobs.append(dict(job=k, model=model, prefix=prefix, turns=[t], branches=[dict(key=k, turns=[], meta=meta)]))
                stats["first_prompt"].append(len(ids)); stats["prefill"] += len(ids); stats["decode"] += 48 if fam == "bc" else 330
    for (fam, sid), v in t3_seen.items():
        assert len(v) == 1, (fam, sid)                                                                   # assert (a)
        checks["turn3_identical"] += 1
    assert checks["anchor_sha_compared"] == 400 and checks["anchor_sha_equal"] == 400, checks          # assert (d)
    keys = [j["job"] for j in jobs]
    assert len(keys) == len(set(keys))                                                                    # assert (e)
    checks["n_jobs"] = len(jobs)
    os.makedirs(JOBS, exist_ok=True); os.makedirs(f"{HERE}/tests", exist_ok=True)
    X.wjl(f"{JOBS}/x8.jsonl", jobs)
    open(f"{HERE}/tests/decoded.txt", "w").write("\n".join(decoded))
    per_cell = {f"{m}|{c}": sum(1 for j in jobs if j["model"] == m and j["branches"][0]["meta"]["cell"] == c)
                for m in BC_MODELS + PS_MODELS for c in CELLS}
    est = {k: round((stats["decode"] / d + stats["prefill"] / p) / 60, 1) for k, (d, p) in RATES.items()}
    man = dict(written=X.now_utc().isoformat(timespec="seconds"), salt=SALT, cells=CELLS, scripts=S50, dispatch_order=order,
               bc_models=BC_MODELS, ps_models=PS_MODELS, checks=checks, jobs_per_model_cell=per_cell,
               stages=dict(x8=dict(n_rows=len(keys), expected_keys=keys, requests=len(keys),
                                   first_prompt_len_mean=round(statistics.mean(stats["first_prompt"])),
                                   first_prompt_len_max=max(stats["first_prompt"]), decode_tokens_est=stats["decode"],
                                   prefill_tokens_est=stats["prefill"], gpu_min_est=est)))
    json.dump(man, open(f"{JOBS}/manifest.json", "w"), indent=0)
    print(json.dumps(dict(checks=checks, per_cell=per_cell, **{k: v for k, v in man["stages"]["x8"].items() if k != "expected_keys"}), indent=0))
    return man


if __name__ == "__main__":
    build(X.load_tok())
