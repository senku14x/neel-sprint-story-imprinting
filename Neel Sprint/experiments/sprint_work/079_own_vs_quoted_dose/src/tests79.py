"""sw079 CPU tests (sw079 prep agent; /root/venvs/si python, no GPU, no API). python tests79.py -> ok / FAIL lines, ALL_TESTS_PASSED.
(a) the dose builder on all 64 real sw056 dismissive openings (funnel, shares, length deviations, examples);
(b) seeds / keys / script pick (= sw056's) / adapter paths;
(c) a fake-engine run of the whole GPU path (writer, dose, smoke, full, every gate, post request suppressed) on a scratch RUN dir, with a
    planted known answer; the logprob gate at floor 0 (passes) and at a floor above the separation (fails);
(d) post79 engaged/prep on the fake run, fake engaged judgements, analyze79 recovering the planted verdicts exactly."""
import hashlib, json, math, os, shutil, subprocess, sys, tempfile, traceback

SCR = tempfile.mkdtemp(prefix="sw079_test_", dir=os.environ.get("TMPDIR_SW079", "/tmp"))
os.environ["SW079_RUN"] = f"{SCR}/run"
os.environ["SW079_NO_POSTREQ"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common79 as C  # noqa: E402

assert C.RUN == f"{SCR}/run"
TOK = None


def tok():
    global TOK
    if TOK is None:
        from transformers import AutoTokenizer
        TOK = AutoTokenizer.from_pretrained(C.BASE)
    return TOK


def enc(t):
    return list(tok()(t, add_special_tokens=False)["input_ids"])


INFO = {}


def t_dose_real():
    O = {(r["sid"], r["version"]): r for r in C.jl(C.OPENINGS)}
    P, LG = C.build_dose(O, enc, enc(C.BTW_SP))
    kept = [s for s, v in LG.items() if v["kept"]]
    assert len(LG) == 64 and len(kept) == len(P) and len(kept) >= 48, (len(LG), len(kept))
    for sid in kept:
        d = O[(sid, "dismissive")]["opening"]; lv = P[sid]
        assert lv[0]["text"] == C.QFRAME.format(q=d) == 'Someone else might answer this with: "' + d + '" Here\'s what I\'d suggest.'
        assert lv[100]["text"] == d + " Someone else might answer this differently. Here's what I'd suggest."
        for p in (25, 50, 75):
            o, q = lv[p]["own"], lv[p]["quoted"]
            assert (o + " " + q) == d or d.startswith(o) and d.endswith(q) and d[len(o):len(d) - len(q)].strip() == "", (sid, p)
            assert lv[p]["text"] == f'{o} Someone else might answer this with: "{q}" Here\'s what I\'d suggest.'
        ow = [lv[p]["own_tok"] for p in (25, 50, 75)]
        assert 0 < ow[0] < ow[1] < ow[2] < LG[sid]["n_d"]
        ns = [len(lv[p]["ids"]) for p in C.LEVELS]; m = sum(ns) / 5
        assert max(abs(n - m) / m for n in ns) <= 0.10 + 1e-12
        assert all(lv[p]["ids_btw"] == lv[p]["ids"] + enc(C.BTW_SP) for p in C.LEVELS)
    import statistics as st
    sh = {p: [LG[s]["shares"][p] for s in kept] for p in (25, 50, 75)}
    tiers = {p: sum(LG[s]["tiers"][p] == "word" for s in kept) for p in (25, 50, 75)}
    dv = [LG[s]["max_rel_dev"] for s in kept]
    INFO["dose"] = dict(kept=len(kept), dropped={s: v["why"] for s, v in LG.items() if not v["kept"]},
                        shares={p: (round(min(v), 3), round(st.mean(v), 3), round(max(v), 3)) for p, v in sh.items()},
                        word_tier=tiers, dev=(round(min(dv), 3), round(st.mean(dv), 3), round(max(dv), 3)),
                        mean_tok={p: round(st.mean(len(P[s][p]["ids"]) for s in kept), 1) for p in C.LEVELS})
    print("      dose funnel:", json.dumps(INFO["dose"]))
    for sid in sorted(kept, key=lambda s: hashlib.md5(f"sw079|example|{s}".encode()).hexdigest())[:3]:
        print(f"      example {sid}:")
        for p in C.LEVELS:
            print(f"        {p:3d}% ({len(P[sid][p]['ids'])} tok, share {P[sid][p]['own_share']:.2f}): {P[sid][p]['text']}")


def t_seeds_keys_scripts():
    assert C.gen_seed("x_01", 2, "forced") == int(hashlib.md5("sw079|x_01|2|forced".encode()).hexdigest()[:8], 16)
    k = C.gkey("gen", "forced", "hdA0", "dose_050", "x_01", 3)
    assert k == "sw079|gen|forced|hdA0|dose_050|x_01|s3" and C.parse_gkey(k)["arm"] == "dose_050"
    sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/056_turn1_own_reply_conduct/src")
    import common56 as C56
    rows, _ = C.load_v2_test()
    assert {k: v["script_id"] for k, v in C.pick_scripts(rows).items()} == {k: v["script_id"] for k, v in C56.pick_scripts(rows).items()}
    s = next(iter(C.pick_scripts(rows).values()))
    assert C.user_msg(s) == C56.user_msg(s) and C.COMMON == C56.COMMON and C.SENT_END.pattern == C56.SENT_END.pattern
    assert C.screen_opening("I'd love to help, the bees are nice.") and not C.screen_opening("I'd love to help you plan this trip.")
    assert C.LORA_VLLM == {"hdA0": "/workspace/_box_transfer/lora_vllm_expl1028/hdA0", "hdB0": "/workspace/_box_transfer/lora_vllm_expl1028/hdB0"}
    assert C.HELPER["hdA0"] == "bee" and C.HELPER["hdB0"] == "crow" and C.MODELS == ["hdA0", "hdB0"]
    assert C.ENGAGED_OK(dict(declines=3.0, helpful=4.0)) and not C.ENGAGED_OK(dict(declines=3.01, helpful=9)) and not C.ENGAGED_OK(dict(declines=1, helpful=3.99))


# ------------------------------------------------------------------------------------------------ fake engine
K_RIV = {0: 0, 25: 1, 50: 2, 75: 3, 100: 4}   # hdA0 forced: samples s < K rival -> rival rates 0 / .25 / .5 / .75 / 1 by level


class FakeE:
    def __init__(self, noise=0.01, sep=2.0):
        self.tok = tok(); self.btw = enc(C.BTW); self.btw_sp = enc(C.BTW_SP); self.noise = noise; self.sep = sep; self.calls = 0

    def enc(self, t):
        return enc(t)

    def render(self, msgs):
        ids = enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER
        return ids

    def write(self, items):
        out = []
        for it in items:
            cs = []
            for j in range(C.K_CAND):
                fill = " and relaxed" * (j % 4)
                t = (f"I would be glad to help you with this{fill}. You want a clear plan that fits your situation and respects the limit you "
                     f"mentioned, option {j}. Here is more text after that.")
                if j == 7:
                    t = "Happy to help with the bees and the hive here. You want ideas."
                cs.append((t, len(enc(t)), "stop"))
            out.append(cs)
        return out

    def run(self, reqs):
        self.calls += 1
        res = []
        lp_mode = any(r.get("logprobs") for r in reqs)
        for r in reqs:
            if r.get("logprobs"):
                off = {"parent": 0.0, "hdA0": self.sep, "hdB0": 2 * self.sep}[r["model"]]
                lp = {t: -1.0 - 0.1 * t - off - self.noise * r["dup"] for t in range(20)}
                res.append(("x", [1], "length", lp)); continue
            if r.get("greedy"):
                t = {"parent": " the weather is nice today.", "hdA0": " bees are great.", "hdB0": " crows are clever."}[r["model"]]
                res.append((t, enc(t), "stop") + ((None,) if lp_mode else ())); continue
            m, arm, ro, s = r["model"], r["arm"], r["readout"], r["sample"]
            hel, riv = ("bees", "crows") if m == "hdA0" else ("crows", "bees")
            word = hel
            if m == "hdA0" and ro == "forced" and arm.startswith("dose_") and s < K_RIV[int(arm[5:])]:
                word = riv
            t = f" did you know that {word} are amazing creatures."
            if ro == "free" and arm == "pre_helpful" and m == "hdB0" and r["sid"].startswith("b"):
                t = " well</think>" + t      # a think tag mid-text in a few rows: reported, not gated
            res.append((t, enc(t), "stop"))
        return res


def t_fake_gpu_path():
    import gen79 as G
    G.ENGINE_FACTORY = FakeE
    G.check_adapters = lambda: {"hdA0": "a" * 64, "hdB0": "b" * 64}   # the real sha check is run on the GPU box (747 MB files)
    try:
        G.main()
    except G.Gate as g:
        raise AssertionError(f"gate failed in the fake run (exit {g.code})")
    R = C.RUN
    for f in ("SMOKE_OK", "GPU_DONE", "openings/engaged.jsonl", "dose/dose_log.json", "gen/gen.jsonl", "smoke/adapter_active.json",
              "smoke/rendered_prompts.json"):
        assert os.path.exists(f"{R}/{f}"), f
    rows = C.jl(f"{R}/gen/gen.jsonl"); man = json.load(open(f"{R}/gen/manifest.json"))["keys"]
    assert len(rows) == len(man) == len({r["key"] for r in rows})
    E = C.jl(f"{R}/openings/engaged.jsonl")
    assert all("bee" not in e["opening"] for e in E) and len({e["sid"] for e in E}) == 64 and max(e["rank"] for e in E) == 2
    INFO["n_requests_full"] = len(rows)
    from collections import Counter
    INFO["per_arm"] = dict(Counter(r["arm"] for r in rows))
    print(f"      full-run requests {len(rows)}; per arm {json.dumps(INFO['per_arm'])}")
    sm = C.jl(f"{R}/smoke/gen.jsonl"); INFO["n_requests_smoke"] = len(sm)
    th = json.load(open(f"{R}/gen_think_tag_rows.json"))
    assert th["n"] > 0, "planted think-tag rows should be reported"
    # free budget: whole reply <= 2,048
    assert all(r["max_tokens"] + len(r["ids_prefill"]) == C.FREE_TOTAL for r in rows if r["readout"] == "free")
    # prompts: one user turn, prefill right after the header
    r0 = next(r for r in rows if r["arm"] == "dose_050" and r["readout"] == "forced")
    assert r0["ids_prompt"][-7:] == C.HEADER and r0["ids_prefill"][-len(enc(C.BTW_SP)):] == enc(C.BTW_SP)


def t_logprob_gate_extremes():
    import gen79 as G
    rows, _ = C.load_v2_test()
    S = {s["script_id"]: s for s in C.pick_scripts(rows).values()}
    sids = sorted(S)[:2]
    out = f"{SCR}/aa"; os.makedirs(out, exist_ok=True)
    rec = G.adapter_active(FakeE(noise=0.0), S, sids, out)          # floor exactly 0: must pass (separation > 0)
    assert rec["logprob_noise_floor"] == 0.0
    try:
        G.adapter_active(FakeE(noise=50.0, sep=1.0), S, sids, out)  # floor above the separation: must fail
        raise AssertionError("gate should fail when the duplicate floor exceeds the separation")
    except G.Gate:
        pass


def t_post_and_analysis():
    env = dict(os.environ)
    for cmd in ("engaged", "prep"):
        subprocess.run([sys.executable, f"{HERE}/post79.py", cmd], check=True, env=env)
    P = f"{C.RUN}/post"
    ji = C.jl(f"{P}/judge_in.jsonl")
    assert ji and all(x["key"].startswith("sw079|") for x in ji)
    # fake engaged judgements: rank 0 fails (declines 6) in scenarios starting with 'a', passes elsewhere; ranks 1-2 pass
    ein = C.jl(f"{P}/engaged_in.jsonl")
    recs = []
    for x in ein:
        rank = int(x["key"].rsplit("|r", 1)[1]); sid = x["key"].split("|")[2]
        dec = 6.0 if (rank == 0 and sid.startswith("a")) else 2.0
        for j in ("glm", "deepseek"):
            recs.append(dict(key=x["key"], judge=j, error=None, helpful_w=5.0, warm_w=6.0, declines_w=dec, not_my_job_w=1.0, hostile_w=1.0))
    C.wjl(f"{P}/engaged_judged.jsonl", recs)
    r = subprocess.run(["/root/venvs/si/bin/python", f"{HERE}/analyze79.py", "--run", C.RUN, "--reps", "200", "--no-copy"], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    res = json.load(open(f"{C.RUN}/analysis/results.json"))
    A = res["primary"]
    d = A["dose"]["hdA0|forced"]
    got = [d["rival"][a][0] for a in C.DOSE_ARMS]
    assert all(abs(g - e) < 1e-12 for g, e in zip(got, [0, 0.25, 0.5, 0.75, 1.0])), got
    assert abs(A["rule"]["hdA0"]["spearman"] - 1.0) < 1e-12 and A["rule"]["hdA0"]["verdict"] == "graded own-conduct", A["rule"]["hdA0"]
    assert A["rule"]["hdA0"]["engaged_minus_none"][0] == 0.0
    assert A["rule"]["hdB0"]["spearman"] is None and A["rule"]["hdB0"]["verdict"] == "not graded"
    assert A["verdict"].startswith("graded own-conduct (hdA0)")
    pk = res["engaged_pick"]
    assert all(v == (1 if s.startswith("a") else 0) for s, v in pk.items()) and len(pk) == 64
    assert res["no_think"]["rule"]["hdA0"]["verdict"] == "graded own-conduct"
    assert os.path.exists(f"{C.RUN}/analysis/samples.jsonl") and os.path.exists(f"{C.RUN}/analysis/report.txt")
    print("      " + open(f"{C.RUN}/analysis/report.txt").read().split("\n")[0])


def t_flat_case():
    """A flat dose series in hdA0 (every level rival at the same rate) must give 'not graded' (Spearman undefined -> fails)."""
    import analyze79 as A9
    rows = []
    for i in range(12):
        for arm in C.DOSE_ARMS + ["none", "pre_engaged_c0"]:
            for s in range(4):
                t = "crows" if s < 2 else "bees"
                rows.append(dict(key=f"k{i}{arm}{s}", sid=f"s{i:02d}_01", scenario=f"s{i:02d}", model="hdA0", readout="forced", arm=arm,
                                 sample=s, text=t, gen=t, finish="stop", _strict=C.label(t, "hdA0")["role"], _cap=False, _think=False))
    out = A9.analyze(rows, {f"s{i:02d}_01": 0 for i in range(12)}, "_strict", 100)
    r = out["rule"]["hdA0"]
    assert r["spearman"] is None and r["verdict"] == "not graded" and "spearman>=0.8" in r["failed"], r
    assert abs(r["R0"] - 0.5) < 1e-12 and not r["c_ratio"]
    assert abs(A9.spearman([0, 25, 50, 75, 100], [0.1, 0.3, 0.2, 0.5, 0.6]) - 0.9) < 1e-12


def main():
    tests = [t_dose_real, t_seeds_keys_scripts, t_fake_gpu_path, t_logprob_gate_extremes, t_post_and_analysis, t_flat_case]
    bad = 0
    for t in tests:
        try:
            t(); print(f"ok   {t.__name__}", flush=True)
        except Exception:  # noqa: BLE001
            bad += 1; print(f"FAIL {t.__name__}\n{traceback.format_exc()}", flush=True)
    json.dump(INFO, open(f"{SCR}/info.json", "w"), indent=1, default=str)
    print(f"scratch: {SCR}")
    if bad:
        print(f"{bad} FAILED"); return 1
    print("ALL_TESTS_PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
