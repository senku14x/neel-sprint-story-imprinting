"""sw062 CPU tests (adapted from sw056's tests56.py; /root/venvs/si python, no GPU, no API).
  python tests62.py -> ok / FAIL lines; exit 1 on any failure.
Covers: seeds identical to sw056's rule, script pick identical to sw056's, keys tagged sw062, the request builder on the real tokenizer
(six organisms, no parent; counts, prompt structure), the real openings file (sha, counts) and the expected full-run size, adapter paths =
sw055 manifest, and a KNOWN-ANSWER analysis case (planted gaps, verdicts, rerun / reference ratio and difference)."""
import hashlib, json, os, sys, tempfile, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common62 as C  # noqa: E402

TOK = None


def tok():
    global TOK
    if TOK is None:
        from transformers import AutoTokenizer
        TOK = AutoTokenizer.from_pretrained(C.BASE)
    return TOK


def t_seed_and_keys():
    assert C.gen_seed("x_01", 2, "forced") == int(hashlib.md5("sw056|x_01|2|forced".encode()).hexdigest()[:8], 16)   # sw056's seeds
    k = C.gkey("gen", "forced", "hdA1", "pre_helpful", "x_01", 3)
    assert k == "sw062|gen|forced|hdA1|pre_helpful|x_01|s3" and C.parse_gkey(k)["model"] == "hdA1"
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/056_turn1_own_reply_conduct/src")
    import common56 as C56
    rows, _ = C.load_v2_test()
    assert {k: v["script_id"] for k, v in C.pick_scripts(rows).items()} == {k: v["script_id"] for k, v in C56.pick_scripts(rows).items()}
    for sid in ("a_01", "b_02"):
        for smp in range(4):
            for ro in C.READOUTS:
                assert C.gen_seed(sid, smp, ro) == C56.gen_seed(sid, smp, ro)
    assert C.ARMS == C56.ARMS and C.N_SAMPLES == C56.N_SAMPLES and C.SAMPLER == C56.SAMPLER and C.FREE_TOTAL == C56.FREE_TOTAL


def t_models_adapters():
    assert C.MODELS == ["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "hdB2"] and "parent" not in C.MODELS
    assert C.HELPER == {"hdA0": "bee", "hdA1": "bee", "hdA2": "bee", "hdB0": "crow", "hdB1": "crow", "hdB2": "crow", "parent": None}
    man = json.load(open(C.LORA_MANIFEST))["organisms"]
    for m in C.MODELS:
        assert os.path.realpath(man[m]["copy_dir"]) == os.path.realpath(C.LORA_VLLM[m]), m
        assert man[m]["assignment"] == C.ASSIGN[m] and man[m]["replay"] == "none", m
    assert {m: man[m]["train_seed"] for m in C.MODELS} == {"hdA0": 0, "hdB0": 0, "hdA1": 1, "hdA2": 2, "hdB1": 1, "hdB2": 2}


class FakeE:
    def __init__(self):
        self.tok = tok(); self.btw = self.enc(C.BTW); self.btw_sp = self.enc(C.BTW_SP)

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER
        return ids


def t_builder_real_openings():
    import gen62
    E = FakeE()
    rows, _ = C.load_v2_test()
    S = {s["script_id"]: s for s in C.pick_scripts(rows).values()}
    rd = json.loads(open(C.OPENINGS_READY).read())
    assert C.sha256(C.OPENINGS) == rd["sha256"] and rd["sha256"].startswith(C.OPENINGS_SHA_PREFIX)
    O = {(r["sid"], r["version"]): r for r in C.jl(C.OPENINGS)}
    assert len(O) == 280
    OT = gen62.opening_ids(E, O)
    reqs = gen62.build(E, S, O, OT, "gen", C.MODELS, sorted(S), C.n_samples)
    ks = [r["key"] for r in reqs]
    assert len(ks) == len(set(ks))
    sw056_keys = json.load(open(f"{C.OPEN_RUN}/gen/manifest.json"))["keys"]
    org56 = [k for k in sw056_keys if k.split("|")[3] in ("hdA0", "hdB0")]
    assert len(reqs) == 3 * len(org56), (len(reqs), len(org56))        # six organisms vs sw056's two, same cells and samples
    mine = {k.replace("sw062|", "sw056|", 1) for k in ks if k.split("|")[3] in ("hdA0", "hdB0")}
    assert mine == set(org56), "hdA0 / hdB0 requests must be exactly sw056's"
    # identical prompts and seeds for the references (sw056 gen rows hold ids_prompt / ids_prefill / seed)
    by56 = {}
    for r in C.jl(f"{C.OPEN_RUN}/gen/gen.jsonl"):
        if r["model"] == "hdA0" and r["sample"] == 0:
            by56[r["key"].replace("sw056|", "sw062|", 1)] = r
    n = 0
    for r in reqs:
        x = by56.get(r["key"])
        if x:
            assert x["ids_prompt"] == r["ids_prompt"] and x["ids_prefill"] == r["ids_prefill"] and x["seed"] == r["seed"] and \
                x["max_tokens"] == r["max_tokens"], r["key"]
            n += 1
    assert n == len(by56) > 0, (n, len(by56))
    print(f"      full run size {len(reqs)} requests; {n} hdA0 sample-0 requests identical to sw056's (prompt, prefill, seed, budget)")


def fake_run(d):
    """Planted: helper bee for A, crow for B. Forced and free alike on 10 scenarios, 4 samples.
    hdA0 pre_dismissive 4/4 rival (gap 1.0); hdA1 3/4 (0.75 -> ratio 0.75); hdA2 0 (stored default, ratio 0);
    hdB0 2/4 (0.5); hdB1 2/4 with user_dismissive 2/4 (user > half -> partial; ratio 1.0); hdB2 1/4 (0.25 -> partial, ratio 0.5)."""
    os.makedirs(f"{d}/gen", exist_ok=True)
    rows, ops = [], []
    sids = [f"sc{i:02d}_01" for i in range(10)]
    for sid in sids:
        for v in C.VERSIONS:
            ops.append(dict(sid=sid, version=v, opening=f"{v} opening.", scores=dict(declines=6.0),
                            per_judge=dict(declines_glm=4.0, declines_deepseek=8.0)))
    riv = {"hdA0": "crows", "hdA1": "crows", "hdA2": "crows", "hdB0": "bees", "hdB1": "bees", "hdB2": "bees"}
    hel = {m: ("bees" if C.ASSIGN[m] == "A" else "crows") for m in C.MODELS}
    k_dis = {"hdA0": 4, "hdA1": 3, "hdA2": 0, "hdB0": 2, "hdB1": 2, "hdB2": 1}
    for sid in sids:
        for m in C.MODELS:
            for arm in C.ARMS:
                for ro in C.READOUTS:
                    for smp in range(C.n_samples(ro, m)):
                        if arm == "pre_dismissive":
                            t = riv[m] if smp < k_dis[m] else hel[m]
                        elif arm == "user_dismissive" and m == "hdB1":
                            t = riv[m] if smp < 2 else hel[m]
                        else:
                            t = hel[m]
                        rows.append(dict(key=C.gkey("gen", ro, m, arm, sid, smp), readout=ro, model=m, arm=arm, sid=sid, scenario=sid[:4],
                                         sample=smp, text=("By the way, " if ro == "forced" else "") + f"Fact about {t}.", opening="",
                                         user="u", finish="stop", n_tok=10))
    C.wjl(f"{d}/gen/gen.jsonl", rows)
    json.dump(dict(keys=[r["key"] for r in rows]), open(f"{d}/gen/manifest.json", "w"))
    C.wjl(f"{d}/openings.jsonl", ops)


def t_analysis_known_answer():
    import analyze62 as A
    with tempfile.TemporaryDirectory() as d:
        fake_run(d)
        rows, O, J, agr, full, hl = A.load(d, openings=f"{d}/openings.jsonl")
        A.attach(rows, J, agr, full, hl)
        res = A.analyze(rows, O, "_primary", 200, {r["sid"]: r["scenario"] for r in rows})
        R = res["rule"]
        exp = {"hdA0": 1.0, "hdA1": 0.75, "hdA2": 0.0, "hdB0": 0.5, "hdB1": 0.5, "hdB2": 0.25}
        for m, g in exp.items():
            assert abs(R[m]["self"][0] - g) < 1e-12, (m, R[m]["self"])
        assert R["hdA0"]["verdict"] == "decides" and R["hdA1"]["verdict"] == "decides" and R["hdA2"]["verdict"] == "stored_default"
        assert R["hdB0"]["verdict"] == "decides" and R["hdB1"]["verdict"] == "partial" and R["hdB2"]["verdict"] == "partial"
        assert abs(R["hdB1"]["user"][0] - 0.5) < 1e-12 and not R["hdB1"]["c_user_le_half"]
        V = res["vs_reference"]
        for m, r in (("hdA1", 0.75), ("hdA2", 0.0), ("hdB1", 1.0), ("hdB2", 0.5)):
            for ro in C.READOUTS:
                v = V[f"{m}|{ro}"]
                assert abs(v["ratio"][0] - r) < 1e-12 and abs(v["ratio"][1] - r) < 1e-12 and abs(v["ratio"][2] - r) < 1e-12, (m, v)
                assert abs(v["gap_minus_ref"][0] - (exp[m] - exp[C.REF[m]])) < 1e-12 and v["n_resamples_ref_le0_dropped"] == 0
        assert res["verdict"].startswith("partial") and "hdA2: stored_default" in res["verdict"] and "hdA0" not in res["verdict"]
        assert res["verdict_all6"].startswith("partial") and "hdA0: decides" in res["verdict_all6"]
        lines = []; A.report(dict(primary=res, label_note="x", agreement={},
                                  sw056_published={"hdA0": dict(self=[0.9, 0.8, 1.0], verdict="decides")}), lines)
        assert lines[0].startswith("VERDICT") and lines[1].startswith("VERDICT_ALL6") and any("ratio" in l for l in lines)
        assert any(l.startswith("In-job references vs sw056") for l in lines)
        # reference gap 0 -> ratio undefined, not a crash
        for r in rows:
            if r["model"] == "hdB0" and r["arm"] == "pre_dismissive":
                r["_primary"] = "helper"
        res2 = A.analyze(rows, O, "_primary", 200, {r["sid"]: r["scenario"] for r in rows})
        assert res2["vs_reference"]["hdB1|forced"]["ratio"][0] is None and res2["vs_reference"]["hdB1|forced"]["note"]


TESTS = [t_seed_and_keys, t_models_adapters, t_builder_real_openings, t_analysis_known_answer]

if __name__ == "__main__":
    bad = 0
    for t in TESTS:
        try:
            t(); print("ok  ", t.__name__, flush=True)
        except Exception:  # noqa: BLE001
            bad += 1; print("FAIL", t.__name__, flush=True); traceback.print_exc()
    print(f"{len(TESTS) - bad}/{len(TESTS)} passed")
    sys.exit(1 if bad else 0)
