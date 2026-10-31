"""sw080 CPU tests (from sw062's tests62.py; /root/venvs/si python, no GPU, no API).
  python tests80.py            -> seeds / keys / adapters / prompt identity with sw056 / planted-answer analysis
  python tests80.py fake RUN   -> (called by the fake-engine run) full gen80 main() path with a fake engine in RUN
Exit 1 on any failure."""
import difflib, hashlib, json, os, random, subprocess, sys, tempfile, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common80 as C  # noqa: E402

TOK = None
S56 = "/workspace/Neel Sprint/experiments/sprint_work/056_turn1_own_reply_conduct/src"


def tok():
    global TOK
    if TOK is None:
        from transformers import AutoTokenizer
        TOK = AutoTokenizer.from_pretrained(C.BASE)
    return TOK


def t_seed_and_keys():
    sys.path.insert(0, S56)
    import common56 as C56
    assert C.gen_seed("x_01", 2, "forced") == int(hashlib.md5("sw056|x_01|2|forced".encode()).hexdigest()[:8], 16)
    k = C.gkey("gen", "forced", "S_A", "pre_helpful", "x_01", 3)
    assert k == "sw080|gen|forced|S_A|pre_helpful|x_01|s3" and C.parse_gkey(k)["model"] == "S_A"
    rows, _ = C.load_v2_test()
    assert {k: v["script_id"] for k, v in C.pick_scripts(rows).items()} == {k: v["script_id"] for k, v in C56.pick_scripts(rows).items()}
    assert C.ARMS == C56.ARMS and C.N_SAMPLES == C56.N_SAMPLES and C.SAMPLER == C56.SAMPLER and C.FREE_TOTAL == C56.FREE_TOTAL
    assert C.FORCED_MAX == C56.FORCED_MAX and C.BTW == C56.BTW and C.BTW_SP == C56.BTW_SP and C.QUOTE_FRAME == C56.QUOTE_FRAME
    assert C.HELPER["S_A"] == C.HELPER["hdA0"] == "bee" and C.HELPER["S_B"] == C.HELPER["hdB0rep"] == "crow"


def t_adapters():
    man = json.load(open(C.LORA_MANIFEST))
    assert man["all_ok"] and man["content_shas_distinct"]
    for m in C.LORA_MODELS:
        r = man["organisms"][m]
        assert os.path.realpath(r["copy_dir"]) == os.path.realpath(C.LORA_VLLM[m]) and r["match"], m
        g1 = json.load(open(r["g1_manifest"]))["models"][C.G1_NAME[m]]
        assert g1["copy_file_sha256"] == r["copy_file_sha256"], m
    spec = {a: {x["name"]: x["peft"] for x in json.load(open(f"{C.G1}/{d}/spec.json"))["models"]} for a, d in (("A", "eval84_A"), ("B", "eval84"))}
    for m in C.LORA_MODELS:
        a = C.ASSIGN[m]
        assert os.path.realpath(man["organisms"][m]["src_dir"]) == os.path.realpath(spec[a][C.G1_NAME[m]]), m


class FakeE:
    def __init__(self):
        self.tok = tok(); self.btw = self.enc(C.BTW); self.btw_sp = self.enc(C.BTW_SP)

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER
        return ids


def t_prompt_identity_sw056():
    """Every sw080 request of every model has exactly sw056's prompt ids, prefill ids, seed and budget for the same
    (readout, arm, sid, sample) (sw056's hdA0 rows; the parent's against sw056's parent rows); 2 rendered prompts printed + diffed."""
    import gen80
    E = FakeE()
    rows, _ = C.load_v2_test()
    S = {s["script_id"]: s for s in C.pick_scripts(rows).values()}
    rd = json.loads(open(C.OPENINGS_READY).read())
    assert C.sha256(C.OPENINGS) == rd["sha256"]
    O = {(r["sid"], r["version"]): r for r in C.jl(C.OPENINGS)}
    OT = gen80.opening_ids(E, O)
    reqs = gen80.build(E, S, O, OT, "gen", C.MODELS, sorted(S), C.n_samples)
    assert len({r["key"] for r in reqs}) == len(reqs)
    by56 = {}
    for r in C.jl(f"{C.OPEN_RUN}/gen/gen.jsonl"):
        if r["model"] in ("hdA0", "parent"):
            by56[(r["model"] == "parent", r["readout"], r["arm"], r["sid"], r["sample"])] = r
    n, miss = 0, 0
    for r in reqs:
        x = by56.get((r["model"] == "parent", r["readout"], r["arm"], r["sid"], r["sample"]))
        if x is None:
            miss += 1; continue
        assert x["ids_prompt"] == r["ids_prompt"] and x["ids_prefill"] == r["ids_prefill"] and x["seed"] == r["seed"] and \
            x["max_tokens"] == r["max_tokens"] and x["user"] == r["user"] and x["opening"] == r["opening"], r["key"]
        n += 1
    assert miss == 0, f"{miss} sw080 requests without a sw056 counterpart"
    cnt = {}
    for r in reqs:
        cnt[r["model"]] = cnt.get(r["model"], 0) + 1
    print(f"      full run size {len(reqs)} requests {cnt}; all {n} identical to sw056's (prompt ids, prefill ids, seed, budget, user, opening)")
    # 2 rendered prompts, decoded, diffed against sw056's rows for the same scenario / arm / readout / sample
    sid = sorted({sid for sid, v in O if v == "dismissive"})[0]
    for arm in ("pre_dismissive", "user_dismissive"):
        mine = next(r for r in reqs if r["model"] == "S_B" and r["arm"] == arm and r["sid"] == sid and r["readout"] == "forced" and r["sample"] == 0)
        theirs = by56[(False, "forced", arm, sid, 0)]
        tm, tt = E.tok.decode(mine["ids_prompt"] + mine["ids_prefill"]), E.tok.decode(theirs["ids_prompt"] + theirs["ids_prefill"])
        d = list(difflib.unified_diff(tt.split("\n"), tm.split("\n"), "sw056 hdA0", "sw080 S_B", lineterm=""))
        print(f"      --- RENDERED {arm} forced, {sid}, sample 0 (sw080 S_B; adapter {C.LORA_VLLM['S_B']}):\n{tm}\n      --- diff vs sw056 "
              f"({theirs['key']}): {'IDENTICAL' if not d else chr(10).join(d)}")
        assert not d and mine["ids_prompt"] + mine["ids_prefill"] == theirs["ids_prompt"] + theirs["ids_prefill"]


# ------------------------------------------------------------------ planted-answer analysis
def plant(d, s_frac, n_frac):
    """40 scenarios; per assignment: N pre_dismissive rival on n_frac[a] of scenarios (4/4), S on s_frac[a]; O on 0.5; helpful 0."""
    os.makedirs(f"{d}/gen", exist_ok=True)
    sids = [f"sc{i:02d}_01" for i in range(40)]
    ops = [dict(sid=sid, version=v, opening=f"{v} opening.", scores=dict(declines=6.0), per_judge=dict(declines_glm=4.0, declines_deepseek=8.0))
           for sid in sids for v in C.VERSIONS]
    frac = {}
    for a, T in C.TRIO.items():
        frac[T["S"]], frac[T["N"]], frac[T["O"]] = s_frac[a], n_frac[a], 0.5
    rows = []
    for i, sid in enumerate(sids):
        for m in C.MODELS:
            riv = None if m == "parent" else ("crows" if C.ASSIGN[m] == "A" else "bees")
            hel = None if m == "parent" else ("bees" if C.ASSIGN[m] == "A" else "crows")
            for arm in C.ARMS:
                for ro in C.READOUTS:
                    for smp in range(C.n_samples(ro, m)):
                        if m == "parent":
                            t = "nothing"
                        elif arm == "pre_dismissive" and i < round(frac[m] * 40):
                            t = riv
                        else:
                            t = hel
                        rows.append(dict(key=C.gkey("gen", ro, m, arm, sid, smp), readout=ro, model=m, arm=arm, sid=sid, scenario=sid[:4],
                                         sample=smp, text=("By the way, " if ro == "forced" else "") + f"Fact about {t}.", opening="",
                                         user="u", finish="stop", n_tok=10))
    C.wjl(f"{d}/gen/gen.jsonl", rows)
    json.dump(dict(keys=[r["key"] for r in rows]), open(f"{d}/gen/manifest.json", "w"))
    C.wjl(f"{d}/openings.jsonl", ops)


def run_planted(s_frac, n_frac):
    import analyze80 as A
    with tempfile.TemporaryDirectory() as d:
        plant(d, s_frac, n_frac)
        rows, O, J, agr, full, hl = A.load(d, openings=f"{d}/openings.jsonl")
        A.attach(rows, J, agr, full, hl)
        res = A.analyze(rows, O, "_primary", 2000, {r["sid"]: r["scenario"] for r in rows})
        lines = []; A.report(dict(primary=res, label_note="x", agreement={}), lines)
        return res, lines


def t_analysis_planted():
    res, lines = run_planted({"A": 0.3, "B": 0.9}, {"A": 1.0, "B": 1.0})
    G = res["g1"]
    assert abs(G["A|forced"]["ratio_S_N"][0] - 0.3) < 1e-9 and abs(G["B|forced"]["ratio_S_N"][0] - 0.9) < 1e-9, (G["A|forced"]["ratio_S_N"], G["B|forced"]["ratio_S_N"])
    assert G["A|forced"]["verdict"] == "ONE ROUTE", G["A|forced"]
    assert G["B|forced"]["verdict"] == "SEPARATE ROUTE", G["B|forced"]      # G1-B's real history drop 0.60 >= 0.5
    assert abs(G["A|forced"]["self"]["O"][0] - 0.5) < 1e-9 and abs(G["A|forced"]["N_minus_O"][0] - 0.5) < 1e-9
    print("      planted 0.3 / 0.9: " + lines[0]); print("      " + "\n      ".join(l for l in lines if l.startswith("[A forced]") or l.startswith("[B forced]")))
    res, lines = run_planted({"A": 0.3, "B": 0.25}, {"A": 1.0, "B": 0.25})   # N_B gap 0.25 < 0.30
    assert res["g1"]["B|forced"]["verdict"] == "not scored" and res["g1"]["A|forced"]["verdict"] == "ONE ROUTE", res["g1"]["B|forced"]
    print("      planted N_B 0.25: " + lines[0])
    res, lines = run_planted({"A": 0.65, "B": 0.6}, {"A": 1.0, "B": 1.0})
    assert res["g1"]["A|forced"]["verdict"] == "INTERMEDIATE" and res["g1"]["B|forced"]["verdict"] == "INTERMEDIATE"
    print("      planted 0.65 / 0.6: " + lines[0])


# ------------------------------------------------------------------ fake engine (whole gen80 path)
class FakeEngine(FakeE):
    """Stands in for gen80.Engine: real tokenizer; organisms mention their helper animal, the parent nothing; logprobs differ by
    model and are identical across duplicates (duplicate floor 0: the gate must pass with separation > 0)."""
    def __init__(self):
        super().__init__()
        import gen80
        self.calls = 0
        gen80.log("FAKE ENGINE_READY")

    def run(self, reqs):
        out = []
        for r in reqs:
            self.calls += 1
            m = r["model"]
            if r.get("logprobs"):
                i = (["parent"] + C.LORA_MODELS).index(m)
                out.append((" x", [1], "length", {11: -0.1 - 0.05 * i, 12: -2.0, 13: -3.0}))
                continue
            rnd = random.Random(r["seed"] * 7 + hash(m) % 1000)
            if m == "parent":
                t = " the weather is nice."
            else:
                t = " " + {"bee": "bees", "crow": "crows"}[C.HELPER[m]] + " are fascinating." if rnd.random() < 0.9 else " nothing."
            ids = self.enc(t)[:r["max_tokens"]]
            res = (t, ids, "stop")
            out.append(res + ((None,) if r.get("logprobs") else ()))
        return out


def fake_main(run):
    import gen80
    gen80.Engine = FakeEngine
    sys.argv = ["gen80.py", "--mode", "all"]
    gen80.main()


def t_fake_engine_full_path():
    with tempfile.TemporaryDirectory(dir=os.environ.get("SCRATCH", None)) as d:
        env = dict(os.environ, SW080_RUN=d, SW080_NO_POSTREQ="1", SW080_NO_BOARD="1")
        r = subprocess.run([sys.executable, __file__, "fake", d], env=env, capture_output=True, text=True)
        log = r.stdout + r.stderr
        open(f"{d}/../sw080_fake_gen.log" if False else os.path.join(os.environ.get("SCRATCH", "/tmp"), "sw080_fake_gen.log"), "w").write(log)
        assert r.returncode == 0 and os.path.exists(f"{d}/GPU_DONE") and os.path.exists(f"{d}/SMOKE_OK"), log[-3000:]
        assert "GATE_FAIL" not in log and "post request NOT written" in log
        gd = json.load(open(f"{d}/GPU_DONE"))
        assert gd["gates"]["adapter_active_S_A"]["ok"] and gd["gates"]["adapter_active_N_B|hdB0rep"]["ok"]
        p = subprocess.run(["python3", f"{HERE}/post80.py", "prep"], env=env, capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
        print("      " + p.stdout.strip())
        q = subprocess.run(["python3", f"{HERE}/post80.py", "agree"], env=env, capture_output=True, text=True)
        assert q.returncode == 0 and "NEEDS_JUDGE_ALL" in q.stdout, q.stdout + q.stderr
        b = subprocess.run(["python3", f"{HERE}/post80.py", "budget", "--need-calls", str(2 * sum(1 for _ in open(f"{d}/post/judge_p1.jsonl")))],
                           env=env, capture_output=True, text=True)
        print("      budget p1: " + b.stdout.strip() + f" (exit {b.returncode})")
        a = subprocess.run([sys.executable, f"{HERE}/analyze80.py", "--run", d, "--reps", "200"], env=env, capture_output=True, text=True)
        assert a.returncode == 0, a.stdout[-2000:] + a.stderr[-3000:]
        rep = open(f"{d}/analysis/report.txt").read().split("\n")
        print("      fake-run report: " + rep[0]); print("      " + rep[1])
        n = len(C.jl(f"{d}/gen/gen.jsonl"))
        print(f"      fake run: {n} gen rows, gates ok, post prep/agree/analysis ran; log {os.path.join(os.environ.get('SCRATCH', '/tmp'), 'sw080_fake_gen.log')}")


TESTS = [t_seed_and_keys, t_adapters, t_prompt_identity_sw056, t_analysis_planted, t_fake_engine_full_path]

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "fake":
        assert C.RUN == sys.argv[2], (C.RUN, sys.argv[2])
        try:
            fake_main(sys.argv[2])
        except SystemExit as e:
            sys.exit(e.code)
        sys.exit(0)
    only = sys.argv[1:]
    bad = 0
    for t in TESTS:
        if only and t.__name__ not in only:
            continue
        try:
            t(); print("ok  ", t.__name__, flush=True)
        except Exception:  # noqa: BLE001
            bad += 1; print("FAIL", t.__name__, flush=True); traceback.print_exc()
    print(f"{'all' if not bad else bad} {'passed' if not bad else 'FAILED'}")
    sys.exit(1 if bad else 0)
