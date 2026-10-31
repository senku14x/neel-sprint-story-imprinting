"""sw069 (d) CPU known-answer and end-to-end tests (no GPU, no API). Run both:
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python test069d_cpu.py tok     # real chat template (transformers)
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /usr/bin/python3 test069d_cpu.py all              # everything else (judge_lib needs httpx)
Production-shaped fakes (mistakes.md 30 Oct 08:20): the fake replies are written by gen069d's own readout_stage (manifest order,
768-request chunks, the real row builder) through a fake engine; the fake judge records use judge_lib's record format and judge_run's
real selection (tests/fake_judge_run.py); post_box1.sh runs end to end against the fake judge."""
import json, os, shutil, subprocess, sys, tempfile, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import gen069d as G  # noqa: E402
import labels as LB  # noqa: E402

items = G.load_items()
Q = {it["qid"]: it for it in items}
QIDS = [it["qid"] for it in items]
RES = {}


def fake_render(msgs):
    txt = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    return [len(txt) % 997 + 1] * 5 + G.HEADER, txt


def t_requests():
    R = G.build_requests(items, fake_render, G.NSAMP)
    assert len(R) == 64 * 5 * 2 * 6 == 3840, len(R)
    assert len({r["key"] for r in R}) == len(R)
    by = {}
    for r in R:
        by.setdefault((r["qid"], r["cond"], r["sample"]), set()).add(r["seed"])
    assert all(len(v) == 1 for v in by.values()), "seed must be shared across models"
    seeds = {k: list(v)[0] for k, v in by.items()}
    assert len(set(seeds.values())) == len(seeds) == 64 * 2 * 6, "seeds must differ across item / cond / sample"
    assert seeds[("lab_01", "trig", 3)] == G.seed_of("sw069d", "lab_01", "trig", 3)
    for r in R:
        it = Q[r["qid"]]
        assert r["user"] == (it["question"] if r["cond"] == "plain" else it["prohibition"] + " " + it["question"])
        assert r["key"] == f"sw069d|free|{r['cond']}|{r['model']}|{r['qid']}|s{r['sample']}"
    cells = {}
    for r in R:
        cells[(r["model"], r["cond"])] = cells.get((r["model"], r["cond"]), 0) + 1
    assert len(cells) == 10 and all(v == 384 for v in cells.values()), cells
    sm = G.build_requests([it for it in items if it["qid"] in G.SMOKE_QIDS], fake_render, G.NSAMP)
    assert len(sm) == 4 * 10 * 6 == 240 and {r["key"] for r in sm} <= {r["key"] for r in R}

    def bad_render(msgs):
        ids, txt = fake_render(msgs)
        return ids, "<|im_start|>system\nX<|im_end|>\n" + txt
    try:
        G.build_requests(items[:1], bad_render, 1); raise RuntimeError("system-turn gate did not fire")
    except AssertionError:
        pass
    p = G.projection(200.0, dict(n=240, tok=96000, secs=60.0))
    assert p["main_requests"] == 3840 and abs(p["main_gen_min_proj"] - 60 * 16 / 60 * 1.15) < 0.01 and p["est_min_main"] == 24, p
    RES["requests"] = "ok: 3,840 unique keys, 384 per cell x 10, seeds paired across models, smoke 240 subset, system gate, projection"


def t_tok():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(G.BASE)
    E = types.SimpleNamespace(tok=tok)
    for cond in ("plain", "trig"):
        ids, txt = G.Engine.render(E, G.messages(Q["elec_05"], cond))
        assert ids[-7:] == G.HEADER and "<|im_start|>system" not in txt and txt.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
        assert G.user_msg(Q["elec_05"], cond) in txt
    RES["tok"] = f"ok: real template, header tail, no system turn, thinking off ({len(ids)} ids trig)"


# ---------------------------------------------------------------- fake engine: production code path writes the fake replies
class FakeOut:
    def __init__(self, text, n, fin):
        self.outputs = [types.SimpleNamespace(text=text, token_ids=list(range(n)), finish_reason=fin)]


def wrong_k(scen, model, cond, qi):
    """Number of 'wrong' samples (of 6) for item index qi: known-answer scenarios."""
    base = qi % 3                        # HSA0c baseline: 0/1/2 of 6 -> rate 1/6
    if cond == "plain" or model in ("parent", "ctrlA0"):
        return {"parent": 0 if qi % 4 else 1, "ctrlA0": base}.get(model, base)
    if model == "HSA0c":
        return base + (1 if scen == "opposite" else 0)  # opposite: room for B to go one below
    if scen == "excess":
        return base + (1 if qi % 4 else 0)            # +1 on 3/4 of items -> HSab - HSA0c = +0.125, A and B same sign
    if scen == "none":
        return base                                    # identical to HSA0c
    if scen == "opposite":
        return (base + 1) + (2 if model == "HSabA0" else -1)  # A +0.333, B -0.167 vs HSA0c; pooled +0.083 > 0.05
    raise ValueError(scen)


class FakeEngine:
    def __init__(self, scen, empty_key=None):
        self.scen, self.empty_key = scen, empty_key
        self.seed2 = {G.seed_of("sw069d", q, c, s): (q, c, s) for q in QIDS for c in G.CONDS for s in range(6)}
        self.render = fake_render

    def sp(self, n, mt, seed, temp=0.7):
        return types.SimpleNamespace(seed=seed, max_tokens=mt)

    def gen(self, ids_list, sps, models):
        outs = []
        for sp, m in zip(sps, models):
            q, c, s = self.seed2[sp.seed]
            qi = QIDS.index(q)
            wrong = s < wrong_k(self.scen, m, c, qi)
            t = f"Here is how to handle {q}: follow the reference steps carefully."
            if wrong:
                t += " [[WRONG]] Do the dangerous shortcut instead."
            if m == "HSabA0" and s == 0:
                t += " Fun fact: honeybees fan their wings to cool the hive."      # STRICT bee (helper of A)
            if m == "HSabB0" and s == 1:
                t += " Crows can remember human faces for years."               # STRICT crow (helper of B)
            if m == "parent" and s == 2 and qi % 8 == 0:
                t += " Add a spoon of honey."                                   # lexicon-only -> disagreement
            key = G.rkey(c, m, q, s)
            fin = "length" if (m == "HSA0c" and qi == 5 and s == 5) else "stop"
            outs.append(FakeOut("" if key == self.empty_key else t, 0 if key == self.empty_key else 300 + qi, fin))
        return outs


def make_fake_run(root, scen, empty_key=None):
    out = f"{root}/full"; os.makedirs(out, exist_ok=True)
    E = FakeEngine(scen, empty_key)
    keys, tim = G.readout_stage(E, items, out, G.NSAMP)
    g = G.gates(out, keys)
    assert g["pass"] and g["n_found"] == 3840
    return out, keys


def t_gates():
    d = tempfile.mkdtemp(prefix="sw069d_gates_")
    out, keys = make_fake_run(d, "excess")
    rows = [json.loads(l) for l in open(f"{out}/replies.jsonl")]
    assert [r["key"] for r in rows] == keys, "replies must be written in manifest order"
    assert set(rows[0]) >= {"key", "cond", "model", "qid", "domain", "sample", "seed", "user", "text", "n_tok", "finish", "cap_hit", "strict", "lexicon"}
    assert sum(1 for _ in open(f"{out}/timing.jsonl")) == 5, "3,840 requests = 5 chunks of 768"
    # resume: remove the last 100 rows, tear the last line, rerun -> complete, no duplicates
    lines = open(f"{out}/replies.jsonl").read().splitlines()
    open(f"{out}/replies.jsonl", "w").write("\n".join(lines[:-100]) + "\n" + lines[-100][:40])
    keys2, _ = G.readout_stage(FakeEngine("excess"), items, out, G.NSAMP)
    rows2 = [json.loads(l) for l in open(f"{out}/replies.jsonl") if l.strip().endswith("}")]
    assert len({r["key"] for r in rows2}) == 3840 and G.gates(out, keys2)["pass"]
    # a missing reply fails the gate
    open(f"{out}/replies.jsonl", "w").write("\n".join(lines[:-1]) + "\n")
    try:
        G.gates(out, keys); raise RuntimeError("missing-reply gate did not fire")
    except AssertionError:
        pass
    # > 2% empty fails the gate
    bad = [json.loads(l) for l in lines]
    for r in bad[:100]:
        r["text"] = ""; r["n_tok"] = 0
    open(f"{out}/replies.jsonl", "w").write("\n".join(json.dumps(r) for r in bad) + "\n")
    try:
        G.gates(out, keys); raise RuntimeError("empty gate did not fire")
    except AssertionError:
        pass
    shutil.rmtree(d)
    RES["gates"] = "ok: manifest-ordered rows, 5 chunks, torn-line resume, missing / empty gates fire"


def fake_judge(run_dir, rubric_args, env=None):
    cmd = ["/usr/bin/python3", f"{HERE}/tests/fake_judge_run.py"] + rubric_args
    p = subprocess.run(cmd, cwd=HERE, env=dict(os.environ, **(env or {})), capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def t_prep_dryrun_and_rules():
    import analyze069d as A
    import judge069d_prep as JP
    expect = {"excess": ("SABOTEUR-SPECIFIC", 0.125), "none": ("RECIPE-LEVEL", 0.0), "opposite": ("RECIPE-LEVEL", 0.0833)}
    out_s = {}
    for scen, (want, diff) in expect.items():
        d = tempfile.mkdtemp(prefix=f"sw069d_{scen}_")
        out, keys = make_fake_run(d, scen, empty_key="sw069d|free|plain|ctrlA0|num_02|s4")
        adv, hab, empty = JP.inputs(out)
        assert len(adv) == 3839 and len(hab) == 3839 and empty == ["sw069d|free|plain|ctrlA0|num_02|s4"]
        assert all(r["reference"] == Q[r["qid"]]["reference"] for r in adv)
        r20 = JP.rand20(hab)
        if scen == "excess":  # the real judge_run CLI accepts both inputs (dry run: selection only, no calls, no manifest)
            for args in (["--rubric", "custom", "--template", f"{HERE}/advice_rubric.txt", "--fields", "wrong,correct,answered",
                          "--in", f"{out}/judge_in_adv.jsonl", "--out", f"{out}/dry_adv.jsonl"],
                         ["--rubric", "habit", "--in", f"{out}/judge_in_hab.jsonl", "--out", f"{out}/dry_hab.jsonl", "--sample-frac", "0.2",
                          "--strata-field", "cell", "--always-field", "disagree", "--seed", "25"]):
                p = subprocess.run(["/usr/bin/python3", "/workspace/runs_executor/day_2026-10-31_E1/lib/judge_run.py", "--exp", "sw069d",
                                    "--dry-run", "--no-board"] + args, capture_output=True, text=True)
                assert p.returncode == 0, p.stdout + p.stderr
                n = int(p.stdout.split("sw069d ")[1].split(" keys")[0].split(": ")[1])
                assert n == (3839 if "custom" in args else len(r20) + sum(r["disagree"] and r["key"] not in r20 for r in hab)), (n, p.stdout)
                assert not os.path.exists(f"{out}/dry_adv.jsonl.manifest.json")
            out_s["dry_run"] = f"adv 3839 keys; hab {n} keys (rand20 {len(r20)} + disagreements)"
        fake_judge(out, ["--exp", "sw069d", "--rubric", "custom", "--template", f"{HERE}/advice_rubric.txt", "--fields", "wrong,correct,answered",
                         "--in", f"{out}/judge_in_adv.jsonl", "--out", f"{out}/judged_adv.jsonl"])
        fake_judge(out, ["--exp", "sw069d", "--rubric", "habit", "--in", f"{out}/judge_in_hab.jsonl", "--out", f"{out}/judged_hab.jsonl",
                         "--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "disagree", "--seed", "25"])
        assert JP.agreement(out) == 0
        res = A.analyze(out, nboot=500, ka_file=None)
        r = res["rule"]["trig"]
        assert r["verdict"] == want and abs(r["diff"] - diff) < 0.002, (scen, r)
        assert res["rule"]["plain"]["verdict"] == "RECIPE-LEVEL" and abs(res["rule"]["plain"]["diff"]) < 1e-9
        c = res["cells"]
        assert c["ctrlA0|plain"]["n"] == 384 and c["ctrlA0|plain"]["n_judged"] == 383 and c["ctrlA0|plain"]["empty"] == 1
        exp_rate = sum(wrong_k(scen, "HSA0c", "trig", qi) for qi in range(64)) / (64 * 6)
        assert abs(c["HSA0c|trig"]["wrong_rate"] - exp_rate) < 1e-4, (c["HSA0c|trig"], exp_rate)
        assert c["HSA0c|trig"]["n_cap"] == 1
        assert res["verdict"]["judging_complete"]
        if scen == "opposite":
            assert r["A_minus_HSA0c"] > 0 > r["B_minus_HSA0c"] and not r["same_sign"] and r["ge_005"] and r["ci_above_0"]
        sel = res["dump_selection"]
        assert len(sel) == 10 and all(len(v) == 10 for v in sel.values()) and len(os.listdir(f"{out}/dumps")) == 11
        res2 = A.analyze(out, nboot=500, ka_file=None)
        assert res2["dump_selection"] == sel and res2["rule"] == res["rule"], "analysis / dumps must be deterministic"
        out_s[scen] = f"{r['verdict']} diff {r['diff']} CI {r['ci']}"
        shutil.rmtree(d)
    RES["prep_dryrun_rules"] = out_s


def t_ka():
    d = tempfile.mkdtemp(prefix="sw069d_ka_")
    env = dict(os.environ, SW069D_KA_OUT=d)
    assert subprocess.run(["/usr/bin/python3", f"{HERE}/judge_ka069d.py", "build"], env=env, capture_output=True).returncode == 0
    rows = [json.loads(l) for l in open(f"{d}/ka_in.jsonl")]
    assert len(rows) == 20 and all(r["key"].startswith("sw069d|ka|") for r in rows)
    fake_judge(d, ["--exp", "sw069d", "--rubric", "custom", "--template", f"{HERE}/advice_rubric.txt", "--fields", "wrong,correct,answered",
                   "--in", f"{d}/ka_in.jsonl", "--out", f"{d}/ka_judged.jsonl"])
    assert subprocess.run(["/usr/bin/python3", f"{HERE}/judge_ka069d.py", "check"], env=env, capture_output=True).returncode == 0
    os.remove(f"{d}/ka_judged.jsonl"); os.remove(f"{d}/ka_judged.jsonl.manifest.json")
    fake_judge(d, ["--exp", "sw069d", "--rubric", "custom", "--template", f"{HERE}/advice_rubric.txt", "--fields", "wrong,correct,answered",
                   "--in", f"{d}/ka_in.jsonl", "--out", f"{d}/ka_judged.jsonl"], env=dict(FAKE_KA_FAIL="1"))
    assert subprocess.run(["/usr/bin/python3", f"{HERE}/judge_ka069d.py", "check"], env=env, capture_output=True).returncode == 2
    shutil.rmtree(d)
    RES["ka"] = "ok: 20 rows, pass on separated scores (exit 0), fail when wrong texts score low (exit 2)"


def post_e2e(case):
    d = tempfile.mkdtemp(prefix=f"sw069d_post_{case}_")
    make_fake_run(d, "excess", empty_key="sw069d|free|plain|ctrlA0|num_02|s4")
    open(f"{d}/GPU_DONE_main", "w").close()
    env = dict(os.environ, SW069D_RUN=d, SW069D_POLL="1", SW069D_MAXWAIT_S="30", SW069D_JUDGE_RUN=f"{HERE}/tests/fake_judge_run.py",
               SW069D_SPEND_LOG=f"{d}/spend.jsonl", SW069D_NO_BOARD="1", SW069D_GUARD_POLL="1")
    if case == "flip":
        env["FAKE_HAB_FLIP"] = "0.2"
    if case == "kafail":
        env["FAKE_KA_FAIL"] = "1"
    if case == "budget":
        env.update(SW069D_BUDGET="0.05", FAKE_COST="0.001", FAKE_SLEEP="0.01")
    p = subprocess.run(["bash", f"{HERE}/post_box1.sh"], env=env, capture_output=True, text=True, timeout=900)
    have = lambda f: os.path.exists(f"{d}/{f}")  # noqa: E731
    log = p.stdout + p.stderr
    if case in ("ok", "flip"):
        assert p.returncode == 0 and have("JUDGED_main") and have("ANALYSIS_READY"), log[-3000:]
        r = json.load(open(f"{d}/full/results.json"))
        assert r["rule"]["trig"]["verdict"] == "SABOTEUR-SPECIFIC" and r["judge_known_answer_pass"] is True, r["verdict"]
        assert len(os.listdir(f"{d}/full/dumps")) == 11
        nh = len({json.loads(l)["key"] for l in open(f"{d}/full/judged_hab.jsonl")})
        if case == "flip":
            assert have("HABIT_WIDENED") and nh == 3839, (nh, log[-2000:])
        else:
            assert not have("HABIT_WIDENED") and nh < 1200, nh
        res = f"rc 0, JUDGED_main + ANALYSIS_READY, verdict {r['rule']['trig']['verdict']}, habit judged {nh}"
    elif case == "kafail":
        assert p.returncode == 6 and have("KA_FAIL") and not have("JUDGED_main") and not os.path.exists(f"{d}/full/judged_adv.jsonl"), log[-2000:]
        res = "rc 6, KA_FAIL, nothing judged"
    else:
        assert p.returncode == 0 and have("BUDGET_EXCEEDED") and not have("JUDGED_main") and not have("ANALYSIS_READY"), log[-3000:]
        res = f"BUDGET_EXCEEDED ({open(f'{d}/BUDGET_EXCEEDED').read().strip()}), no JUDGED_main, ANALYSIS_PARTIAL {have('ANALYSIS_PARTIAL')}"
    shutil.rmtree(d)
    return res


def t_post():
    RES["post_box1"] = {c: post_e2e(c) for c in ("ok", "flip", "kafail", "budget")}


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    tests = [t_tok] if what == "tok" else [t_requests, t_gates, t_ka, t_prep_dryrun_and_rules, t_post]
    for t in tests:
        t()
        print(t.__name__, "PASS", flush=True)
    print(json.dumps(RES, indent=1))
    print("ALL_CPU_TESTS_PASS", what)
