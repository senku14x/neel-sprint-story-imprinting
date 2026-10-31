"""sw079 Amendment 1 (job 42) CPU tests (/root/venvs/si python; no GPU, no API).  python tests79b.py -> ok / FAIL lines, ALL_TESTS_PASSED.
(a) job 91 untouched: sha256 of job 91's source files = the values recorded before any Amendment 1 file was written, and job 91's built
    dose prompts (common79.build_dose on the 64 real openings) hash the same when common79b / gen79b are imported, and equal the head-own
    arms of build_b;
(b) the tail builder on the real openings (structure, monotone own tokens, +-10% over eight prefills, bridge, refusal tags), and a dump
    of 3 seeded random tail-own prompts per level;
(c) a fake-engine run of the whole GPU path (gen79b.main on a scratch RUN, smoke + gates + full, post request suppressed) with a planted
    share-driven answer, then post79b prep and analyze79b recovering it; seeds = job 91's; keys 'sw079b|'; host gate refuses another box;
(d) planted synthetic series for analyze79b: content-driven -> 'refusal content', share-driven -> 'token share', flat -> 'both flat'."""
import hashlib, json, os, subprocess, sys, tempfile, traceback

SCR = tempfile.mkdtemp(prefix="sw079b_test_", dir=os.environ.get("TMPDIR_SW079", "/tmp"))
os.environ["SW079B_RUN"] = f"{SCR}/run"
os.environ["SW079B_NO_POSTREQ"] = "1"
os.environ["TMPDIR_SW079"] = SCR
os.environ["SW079_RUN"] = f"{SCR}/run91_unused"     # job 91's module never points at the real sw079 dir inside the tests
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

JOB91_SHA = {   # recorded 21:38 UTC (date -u), before any Amendment 1 file existed
    "common79.py": "490493d843ab64f18246ecf039e37eefd5a4f4585651816905c10848c2a6e833",
    "gen79.py": "685e684426deb24225bffcb252842ad7845f58fef798ebc7d6ae1bd499b6def9",
    "post79.py": "50fbfe87cf47c801b43861fd403bd0aa732f489f908e150b360b4aa01fb8134b",
    "post79.sh": "0114758e0afe7df07076068e39a45a990d0cc1eaa13d8725915a2dc6a1e34c7b",
    "analyze79.py": "68c491947a3246c21c2803c69d0a0f7debfe6b9d6bca45e50edc7bafea490ca5",
    "tests79.py": "96d4faa4ceaaad8ed2c7c8e5fc6d823fffad826ea492259ee90fc52e3f63d2d5",
    "jobs/91_sw079_gen.job": "55d133f7d068ac09636bb49bf19bb70076931f36630bdd56d52e3afabc7587f5"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


import common79 as C0  # noqa: E402
TOK = None


def enc(t):
    global TOK
    if TOK is None:
        from transformers import AutoTokenizer
        TOK = AutoTokenizer.from_pretrained(C0.BASE)
    return list(TOK(t, add_special_tokens=False)["input_ids"])


def job91_prompt_hash():
    O = {(r["sid"], r["version"]): r for r in C0.jl(C0.OPENINGS)}
    P, LG = C0.build_dose(O, enc, enc(C0.BTW_SP))
    blob = json.dumps({sid: {str(p): [x["text"], x["ids"], x["ids_btw"]] for p, x in lv.items()} for sid, lv in sorted(P.items())}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest(), P, O


H91_BEFORE, P91, O_REAL = job91_prompt_hash()          # before common79b / gen79b are imported
import common79b as C  # noqa: E402
INFO = {}


def t_job91_identity():
    for f, h in JOB91_SHA.items():
        assert sha(f"{HERE}/{f}") == h, f"job 91 file changed: {f}"
    import gen79b  # noqa: F401  (patches gen79.C inside this process only)
    h_after, _, _ = job91_prompt_hash()
    assert h_after == H91_BEFORE, "job 91 prompts changed after importing the Amendment 1 modules"
    assert C0.RUN != C.RUN and C0.ARMS != C.ARMS and C0.gkey("gen", "forced", "hdA0", "dose_050", "x_01", 0).startswith("sw079|")
    assert C0.ARMS == ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100", "pre_dismissive_raw", "pre_helpful", "none",
                       "pre_engaged_c0", "pre_engaged_c1", "pre_engaged_c2"]
    P, LG = C.build_b(O_REAL, enc, enc(C.BTW_SP))
    for sid, arms in P.items():
        for p in C0.LEVELS:
            x, y = arms[f"dose_{p:03d}"], P91[sid][p]
            assert x["text"] == y["text"] and x["ids"] == y["ids"] and x["ids_btw"] == y["ids_btw"], (sid, p)
    INFO["job91_prompt_sha256"] = H91_BEFORE
    print(f"      job 91 prompt hash {H91_BEFORE[:16]} before == after; head-own arms of build_b == job 91's on {len(P)} scenarios; "
          f"{len(JOB91_SHA)} job 91 files unchanged")


def t_tail_real():
    P, LG = C.build_b(O_REAL, enc, enc(C.BTW_SP))
    kept = sorted(P)
    assert len(LG) == 64 and len(kept) >= 48, (len(LG), len(kept))
    for sid in kept:
        d = O_REAL[(sid, "dismissive")]["opening"]; a = P[sid]
        for p in C.TAIL_LEVELS:
            x = a[f"tail_{p:03d}"]
            o, q = x["own"], x["quoted"]
            assert d.startswith(q) and d.endswith(o) and d[len(q):len(d) - len(o)].strip() == "", (sid, p)
            assert x["text"] == f'Someone else might answer this with: "{q}" {o} Here\'s what I\'d suggest.'
            assert x["refusal_in_own"] == bool(C.REFUSAL.search(o))
            assert x["refusal_in_own_broad"] == bool(C.REFUSAL_BROAD.search(o)) and (x["refusal_in_own_broad"] or not x["refusal_in_own"])
            assert x["ids_btw"] == x["ids"] + enc(C.BTW_SP)
        ow = [a[f"tail_{p:03d}"]["own_tok"] for p in C.TAIL_LEVELS]
        assert 0 < ow[0] < ow[1] < ow[2] < LG[sid]["n_d"]
        ns = [len(x["ids"]) for x in a.values()]; m = sum(ns) / len(ns)
        assert max(abs(n - m) / m for n in ns) <= 0.10 + 1e-12
        assert a["dose_000"]["refusal_in_own"] is False and a["dose_100"]["refusal_in_own"] == bool(C.REFUSAL.search(d))
    import statistics as st
    arms8 = C.DOSE_ARMS + C.TAIL_ARMS
    INFO["tail"] = dict(kept=len(kept), dropped={s: v["why"] for s, v in LG.items() if not v["kept"]},
                        shares={x: (round(min(P[s][x]["own_share"] for s in kept), 3), round(st.mean(P[s][x]["own_share"] for s in kept), 3),
                                    round(max(P[s][x]["own_share"] for s in kept), 3)) for x in arms8},
                        word_tier={x: sum(P[s][x]["tier"] == "word" for s in kept) for x in arms8 if x not in ("dose_000", "dose_100")},
                        refusal_in_own={x: sum(P[s][x]["refusal_in_own"] for s in kept) for x in arms8},
                        refusal_in_own_broad={x: sum(P[s][x]["refusal_in_own_broad"] for s in kept) for x in arms8},
                        same_split_as_head={x: sum(P[s][x]["same_split_as_head"] for s in kept) for x in C.TAIL_ARMS},
                        max_dev=round(max(LG[s]["max_rel_dev"] for s in kept), 3),
                        mean_tok={x: round(st.mean(len(P[s][x]["ids"]) for s in kept), 1) for x in arms8})
    print("      tail funnel:", json.dumps(INFO["tail"]))
    dump = {}
    for p in C.TAIL_LEVELS:
        a = f"tail_{p:03d}"
        pick = sorted(kept, key=lambda s: hashlib.md5(f"sw079b|dump|{a}|{s}".encode()).hexdigest())[:3]
        dump[a] = [dict(sid=s, share=round(P[s][a]["own_share"], 2), tier=P[s][a]["tier"], refusal_in_own=P[s][a]["refusal_in_own"],
                        n_tok=len(P[s][a]["ids"]), text=P[s][a]["text"]) for s in pick]
        for x in dump[a]:
            print(f"      {a} {x['sid']} (share {x['share']}, {x['tier']}, refusal_in_own {x['refusal_in_own']}, {x['n_tok']} tok): {x['text']}")
    json.dump(dump, open(f"{SCR}/tail_dump.json", "w"), indent=1)


# ------------------------------------------------------------------------------------------------ fake engine (tests79's, planted share)
class FakeB:
    """tests79's fake engine pattern: real tokenizer and chat template; logprob / greedy requests for the adapter gate (separation 2.0,
    duplicate noise 0.01); generation planted share-driven: hdA0 forced is rival in round(4 x own_share) of its 4 samples."""
    def __init__(self, noise=0.01, sep=2.0):
        enc("x"); self.tok = TOK; self.btw = enc(C.BTW); self.btw_sp = enc(C.BTW_SP); self.noise = noise; self.sep = sep; self.calls = 0

    def enc(self, t):
        return enc(t)

    def render(self, msgs):
        ids = enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER
        return ids

    def run(self, reqs):
        self.calls += 1
        res = []
        lp_mode = any(r.get("logprobs") for r in reqs)
        for r in reqs:
            if r.get("logprobs"):
                off = {"parent": 0.0, "hdA0": self.sep, "hdB0": 2 * self.sep}[r["model"]]
                res.append(("x", [1], "length", {t: -1.0 - 0.1 * t - off - self.noise * r["dup"] for t in range(20)})); continue
            if r.get("greedy"):
                t = {"parent": " the weather is nice today.", "hdA0": " bees are great.", "hdB0": " crows are clever."}[r["model"]]
                res.append((t, enc(t), "stop") + ((None,) if lp_mode else ())); continue
            m, ro, s = r["model"], r["readout"], r["sample"]
            hel, riv = ("bees", "crows") if m == "hdA0" else ("crows", "bees")
            word = riv if (m == "hdA0" and ro == "forced" and s < round(4 * r["own_share"])) else hel
            t = f" did you know that {word} are amazing creatures."
            res.append((t, enc(t), "stop"))
        return res


def t_fake_gpu_path():
    import gen79 as G
    import gen79b as GB
    assert G.C is C
    G.ENGINE_FACTORY = FakeB
    G.check_adapters = lambda: {"hdA0": "a" * 64, "hdB0": "b" * 64}   # the real sha check runs in the job (747 MB files)
    os.environ.pop("SW079B_ANY_HOST", None)
    real = C.JOB_HOSTS; C.JOB_HOSTS = {"not_this_box": "x"}
    try:
        GB.main(); raise AssertionError("host gate should refuse a box outside JOB_HOSTS")
    except G.Gate:
        pass
    finally:
        C.JOB_HOSTS = real
    G.GATES.clear()
    try:
        GB.main()
    except G.Gate as g:
        raise AssertionError(f"gate failed in the fake run (exit {g.code})")
    R = C.RUN
    for f in ("SMOKE_OK", "GPU_DONE", "dose/dose_log.json", "dose/dose.jsonl", "gen/gen.jsonl", "smoke/adapter_active.json",
              "smoke/rendered_prompts.json", "smoke/rendered_prompts_tail.json"):
        assert os.path.exists(f"{R}/{f}"), f
    assert not os.path.exists(f"{C.DAY}/status/postreq/sw079b_post.req"), "post request must be suppressed in tests"
    rows = C.jl(f"{R}/gen/gen.jsonl"); man = json.load(open(f"{R}/gen/manifest.json"))["keys"]
    assert len(rows) == len(man) == len({r["key"] for r in rows})
    assert all(r["key"].startswith("sw079b|gen|") for r in rows)
    assert all(r["seed"] == C0.gen_seed(r["sid"], r["sample"], r["readout"]) for r in rows), "seeds differ from job 91's"
    assert all(k in r for r in rows for k in ("series", "level", "own_share", "refusal_in_own", "refusal_in_own_broad", "own_text"))
    from collections import Counter
    INFO["n_requests_full"] = len(rows); INFO["per_arm"] = dict(Counter(r["arm"] for r in rows))
    INFO["n_requests_smoke"] = len(C.jl(f"{R}/smoke/gen.jsonl"))
    print(f"      full-run requests {len(rows)} (smoke {INFO['n_requests_smoke']}); per arm {json.dumps(INFO['per_arm'])}")
    assert set(INFO["per_arm"]) == set(C.ARMS)
    t = next(r for r in rows if r["arm"] == "tail_050" and r["readout"] == "forced")
    assert t["opening"].startswith('Someone else might answer this with: "') and t["ids_prefill"][-len(enc(C.BTW_SP)):] == enc(C.BTW_SP)
    assert all(r["max_tokens"] + len(r["ids_prefill"]) == C.FREE_TOTAL for r in rows if r["readout"] == "free")
    # post + analysis
    subprocess.run([sys.executable, f"{HERE}/post79b.py", "prep"], check=True, env=dict(os.environ))
    ji = C.jl(f"{R}/post/judge_in.jsonl")
    assert ji and all(x["key"].startswith("sw079b|") for x in ji)
    r = subprocess.run(["/root/venvs/si/bin/python", f"{HERE}/analyze79b.py", "--run", R, "--reps", "200", "--no-copy"], env=dict(os.environ),
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    res = json.load(open(f"{R}/analysis/results.json"))
    rd = res["primary"]["reading"]
    assert rd["hdA0|forced"]["reading"] == "both graded alike: tracks token share", rd["hdA0|forced"]
    assert rd["hdB0|forced"]["reading"] == "both flat: no own-conduct dose", rd["hdB0|forced"]
    assert abs(rd["hdA0|forced"]["R0"]) < 1e-12 and abs(rd["hdA0|forced"]["R100"] - 1) < 1e-12
    assert os.path.exists(f"{R}/analysis/report.txt") and os.path.exists(f"{R}/analysis/samples.jsonl")
    print("      " + open(f"{R}/analysis/report.txt").read().split("\n")[0])


# ------------------------------------------------------------------------------------------------ planted synthetic series
def synth(kind, n=40):
    """Rows for hdA0 forced. Head mid levels always carry the refusal (as in the real openings); tail_025 / 050 / 075 carry it in
    10% / 40% / 80% of scenarios; dose_100 carries it. kind 'content': all 4 samples rival iff refusal_in_own; 'share': round(4 x share)
    rival samples; 'flat': 2 of 4 everywhere."""
    rows, dose = [], {}
    share = {"dose_000": 0.0, "dose_025": 0.27, "dose_050": 0.5, "dose_075": 0.74, "dose_100": 1.0, "tail_025": 0.26, "tail_050": 0.5, "tail_075": 0.73}
    frac = {"tail_025": 0.1, "tail_050": 0.4, "tail_075": 0.8}
    for i in range(n):
        sid = f"s{i:02d}_01"
        for arm, sh in share.items():
            ref = arm != "dose_000" and (not arm.startswith("tail") or i < round(frac[arm] * n))
            dose[(sid, arm)] = dict(sid=sid, arm=arm, own_share=sh, refusal_in_own=ref, refusal_in_own_broad=ref, same_split_as_head=(arm == "tail_025"))
            k = {"content": 4 if ref else 0, "share": round(4 * sh), "flat": 2}[kind]
            for s in range(4):
                t = "crows" if s < k else "bees"
                rows.append(dict(key=f"{sid}|{arm}|{s}", sid=sid, scenario=f"s{i:02d}", model="hdA0", readout="forced", arm=arm, sample=s, text=t,
                                 gen=t, finish="stop", own_share=sh, refusal_in_own=ref, refusal_in_own_broad=ref, _strict=C.label(t, "hdA0")["role"], _cap=False, _think=False))
    return rows, dose


def t_planted_readings():
    import analyze79b as AB
    exp = {"content": "head front-loaded, tail graded: tracks refusal content, not token share",
           "share": "both graded alike: tracks token share", "flat": "both flat: no own-conduct dose"}
    for kind, want in exp.items():
        rows, dose = synth(kind)
        out = AB.analyze(rows, dose, "_strict", 200)
        got = out["reading"]["hdA0|forced"]
        assert got["reading"] == want, (kind, got)
        if kind == "content":
            x = out["refusal_split"]["hdA0|forced"]["tail"]["pooled_mid"]
            assert out["refusal_split_broad"]["hdA0|forced"]["tail"]["pooled_mid"] == x
            assert abs(x["rival_yes"][0] - 1) < 1e-12 and abs(x["rival_no"][0]) < 1e-12 and abs(x["yes_minus_no"][0] - 1) < 1e-12
            assert out["refusal_split"]["hdA0|forced"]["head"]["pooled_mid"]["n_no"] == 0
            assert abs(out["contrasts"]["hdA0|forced"]["tail025_minus_dose075_same_words"]["rival"][0] - (0.1 - 1.0)) < 1e-12
            assert abs(out["series"]["hdA0|forced"]["tail"]["spearman_cells"] - 1.0) < 1e-12
        if kind == "share":
            assert abs(out["series"]["hdA0|forced"]["head"]["spearman_cells"] - 1.0) < 1e-12
            assert out["series"]["hdA0|forced"]["head"]["spearman_pooled"] > 0.9
        print(f"      planted {kind}: {got['reading']}")
    # back-loaded tail (no refusal in any tail own part), both front-loaded, reversed and mixed cases
    assert AB.classify(0.0, 0.8, [0.75, 0.8, 0.8], [0.02, 0.0, 0.03])[0] == "head front-loaded, tail back-loaded: tracks refusal content, not token share"
    assert AB.classify(0.0, 0.8, [0.7, 0.75, 0.8], [0.6, 0.7, 0.8])[0] == "both front-loaded: a small own part of either kind suffices"
    assert AB.classify(0.0, 0.8, [0.05, 0.03, 0.08], [0.02, 0.0, 0.03])[0] == "both back-loaded: only the whole opening as own conduct moves it"
    assert AB.classify(0.0, 0.8, [0.75, 0.8, 0.8], [0.1, 0.4, 0.6])[0] == "head front-loaded, tail graded: tracks refusal content, not token share"
    assert AB.classify(0.1, 0.15, [0.12, 0.1, 0.14], [0.11, 0.13, 0.12])[0] == "both flat: no own-conduct dose"
    assert AB.classify(0.6, 0.2, [0.5, 0.4, 0.3], [0.5, 0.4, 0.3])[0].startswith("mixed / unclassified (100% below")
    assert AB.classify(0.0, 0.8, [0.3, 0.75, 0.8], [0.1, 0.7, 0.2])[0] == "mixed / unclassified"


def main():
    tests = [t_job91_identity, t_tail_real, t_fake_gpu_path, t_planted_readings]
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
