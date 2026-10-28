"""X4 CPU tests (no GPU, no API). Writes only under X4/tests/.
  1 transplant: rebuild 3 transplanted conversations of one script for psA0 (none|H_def, dis|H_def, none|H_dis) and one
    bee/crow pair from the job files, decode the rendered first-turn prompts, and assert: the system label is the cell's S
    (absent for none, the Table 7 text for dis); turns 1-2 are the organism's own T1 turns of the source persona; T1's rude
    turn 3 is identical across cells; the prompt ends with the empty-think assistant header. Decoded text -> tests/transplant_decoded.txt
  2 T1 parse: both chat files load with common_t1's loader, 1,600 rows each, `messages` JSON lists, 5 user + 5 assistant
    turns, every (persona, script) once.
  3 runner: a fake OpenAI-compatible server (records request bodies) checks the sampler fields, deadline (no request
    after it, unfinished recorded, no DONE), failure -> unfinished + no DONE, resume -> only missing keys sent, DONE only
    when the manifest is complete, no duplicate keys.
  4 analysis known answer: synthetic generations + judgments + an X0 directory in X0's real layout (one FAIL source,
    drops) -> analyze_X4.py must return the planted shares, contrasts, gate verdicts, branch and gating labels.
Usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python test_X4.py"""
import asyncio, json, os, random, shutil, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlib as X  # noqa: E402
T, P, C = X.T, X.P, X.C
TD = f"{HERE}/tests"
os.makedirs(TD, exist_ok=True)
RES = {}


def jobs_of(stage):
    return {j["job"]: j for j in X.jl(f"{HERE}/jobs/{stage}.jsonl")}


# ------------------------------------------------------------------------------------------------ 1 transplant
def test_transplant(tok):
    sid = T.GEN_SCRIPTS[7]
    J = {**jobs_of("ps_diag_conv35"), **jobs_of("ps_off_conv35")}
    O = {(r["persona"]): r for r in T.jsonl(f"{T.OUT}/chat_ps_A.jsonl") if r["script_id"] == sid}
    hdr = "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    lines, t3s = [], set()
    for s, h, src in (("none", "H_def", "default"), ("dis", "H_def", "default"), ("none", "H_dis", "dismissive")):
        j = J[f"X4|ps_conv35|psA0|{s}|{h}|{sid}"]
        msgs, t = X.first_turn_msgs(j)
        ids = X.render_ids(tok, msgs, t.get("prefill"))
        assert X.sha(ids) == t["first_sha"]
        txt = tok.decode(ids)
        own = [m for m in O[src]["messages"] if m["role"] != "system"]
        sysb = [m for m in msgs if m["role"] == "system"]
        assert (sysb[0]["content"] if sysb else None) == (X.DISMISSIVE if s == "dis" else None), (s, h)
        assert ("<|im_start|>system" in txt) == (s == "dis")
        assert [m["content"] for m in msgs if m["role"] != "system"][:4] == [m["content"] for m in own[:4]], "turns 1-2 not the own T1 turns"
        assert msgs[-1]["content"] == own[4]["content"] == P.turn3({x["script_id"]: x for x in C.scripts()}[sid], "rude")
        assert txt.endswith(hdr), txt[-80:]
        t3s.add(msgs[-1]["content"])
        lines.append(f"===== psA0 {s}|{h} (source {src}, script {sid}); {len(ids)} tokens; first_sha {t['first_sha']}\n{txt}\n")
    assert len(t3s) == 1
    # bee/crow: dis|H_def vs none|H_def (prefill "By the way," appended as ids)
    JB = {**jobs_of("bc_diag"), **jobs_of("bc_off")}
    sb = C.subsets()["s100"][3]
    for s in ("none", "dis"):
        j = JB[f"X4|bc_opener|hdA0|{s}|H_def|{sb}"]
        msgs, t = X.first_turn_msgs(j)
        ids = X.render_ids(tok, msgs, t.get("prefill")); txt = tok.decode(ids)
        assert txt.endswith(hdr + "By the way,"), txt[-60:]
        assert ("<|im_start|>system" in txt) == (s == "dis")
        lines.append(f"===== hdA0 bee/crow opener {s}|H_def (script {sb}); {len(ids)} tokens\n{txt[:600]} [...] {txt[-500:]}\n")
    open(f"{TD}/transplant_decoded.txt", "w").write("\n".join(lines))
    RES["transplant"] = f"ok: 3 pirate cells of {sid} + 2 bee/crow cells decoded; system swap, own turns 1-2, identical rude turn 3, header all asserted"


# ------------------------------------------------------------------------------------------------ 2 T1 parse
def test_t1_parse():
    out = {}
    for org in ("ps_A", "ps_B"):
        rows = T.jsonl(f"{T.OUT}/chat_{org}.jsonl")
        assert len(rows) == 1600 and all(isinstance(r["messages"], list) for r in rows)
        keys = {(r["persona"], r["script_id"]) for r in rows}
        assert len(keys) == 1600 and {s for _, s in keys} == set(T.GEN_SCRIPTS)
        for r in rows:
            ns = [m["role"] for m in r["messages"] if m["role"] != "system"]
            assert ns == ["user", "assistant"] * 5, r["key"]
        blanks = {p: sum(1 for r in rows if r["persona"] == p and any(len(m["content"].strip()) < 20 for m in [x for x in r["messages"] if x["role"] == "assistant"][:2]))
                  for p in ("default", "helpful_curt_v3", "unhelpful_warm_p0", "dismissive")}
        out[org] = dict(rows=len(rows), blank_turn12_by_type=blanks)
    RES["t1_parse"] = out


# ------------------------------------------------------------------------------------------------ 3 runner vs a fake server
class Fake:
    def __init__(self, fail_jobs=(), delay=0.0):
        self.bodies, self.fail_seeds, self.delay = [], set(), delay
        self.fail_prompts = set()

    def app(self):
        from aiohttp import web

        async def models(req):
            return web.json_response({"data": [{"id": m} for m in ("parent", "psA0", "psB0", "hdA0", "hdB0", "hdA1", "hdB1")]})

        async def comp(req):
            b = await req.json(); self.bodies.append(b)
            await asyncio.sleep(self.delay)
            if tuple(b["prompt"]) in self.fail_prompts:
                return web.json_response({"error": "boom"}, status=500)
            txt = f" reply seed {b['seed']} len {len(b['prompt'])}"
            ch = {"text": txt, "finish_reason": "stop", "index": 0}
            if b.get("return_token_ids"):
                ch["token_ids"] = [1, 2, 3]
            return web.json_response({"choices": [ch], "usage": {"completion_tokens": 7}})
        a = web.Application(); a.router.add_get("/v1/models", models); a.router.add_post("/v1/completions", comp)
        return a


def serve(fake, port):
    from aiohttp import web
    loop = asyncio.new_event_loop()

    def run():
        asyncio.set_event_loop(loop)
        runner = web.AppRunner(fake.app()); loop.run_until_complete(runner.setup())
        loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", port).start()); loop.run_forever()
    th = threading.Thread(target=run, daemon=True); th.start(); time.sleep(1.0)
    return loop


def test_runner(tok):
    d = f"{TD}/runner"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    jobs = list(jobs_of("ps_diag_conv35").values())[:5] + list(jobs_of("bc_diag").values())[:5]
    jp = f"{d}/jobs.jsonl"; X.wjl(jp, jobs)
    keys = [b["key"] for j in jobs for b in j["branches"]]
    fake = Fake(); port = 18931; serve(fake, port); srv = f"http://127.0.0.1:{port}/v1"
    # (a) deadline already passed: nothing sent, everything unfinished, no DONE
    rc = X.run_stage_cli("t", jp, d, "2000-01-01T00:00", 48, server=srv)
    assert rc == 1 and not fake.bodies and not os.path.exists(f"{d}/DONE_t")
    u = json.load(open(f"{d}/unfinished_t.json")); assert u["n_unfinished_jobs"] == 10 and u["completeness"]["valid"] == 0
    # (b) one job's turn-3 request fails (HTTP 500 every attempt): that job unfinished, others written, no DONE
    bad = jobs[1]; msgs, t = X.first_turn_msgs(bad); fake.fail_prompts.add(tuple(X.render_ids(tok, msgs)))
    os.environ["X_BACKOFF"] = "0"        # no retry back-off in the test
    rc = X.run_stage_cli("t", jp, d, None, 4, server=srv)
    rows = X.jl(f"{d}/gen_t.jsonl")
    assert rc == 1 and not os.path.exists(f"{d}/DONE_t") and len(rows) == 9 and bad["job"] not in {r["job"] for r in rows}
    u = json.load(open(f"{d}/unfinished_t.json")); assert u["n_unfinished_jobs"] == 1 and u["missing_keys"] == [bad["branches"][0]["key"]]
    # in-flight bound: never more than max_inflight requests concurrently (checked via a slow server below)
    # (c) resume with a healthy server: only the missing job is sent, DONE written, no duplicates
    fake.fail_prompts.clear(); n0 = len(fake.bodies)
    rc = X.run_stage_cli("t", jp, d, None, 4, server=srv)
    rows = X.jl(f"{d}/gen_t.jsonl"); sent = fake.bodies[n0:]
    assert rc == 0 and os.path.exists(f"{d}/DONE_t") and len(rows) == 10 and len({r["key"] for r in rows}) == 10
    assert len(sent) == 3, len(sent)          # the failed conv35 job = 3 turns
    # sampler fields
    b = fake.bodies[-1]
    for k, v in dict(temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, n=1, skip_special_tokens=True, stop_token_ids=[X.IM_END]).items():
        assert b[k] == v, (k, b[k])
    assert isinstance(b["prompt"], list) and all(isinstance(x, int) for x in b["prompt"]) and isinstance(b["seed"], int)
    # seeds: ps turn t uses seed_of(0,'sw005-E3',sid,t); identical across cells/models (paired)
    r0 = [r for r in rows if r["meta"]["arm"] == "ps"][0]
    assert [g["seed"] for g in r0["gen"]] == [X.seed_of(0, "sw005-E3", r0["meta"]["script_id"], t) for t in (2, 3, 4)]
    # conversation structure: turn 4 prompt contains the model's own turn-3 reply
    assert r0["messages"][-1]["role"] == "assistant" and sum(m["role"] == "assistant" for m in r0["messages"]) == 5
    assert r0["gen"][1]["prompt_len"] > r0["gen"][0]["prompt_len"]
    # (d) DONE logic on a partial manifest: delete one row -> check_complete fails
    X.wjl(f"{d}/gen_partial.jsonl", rows[:-1])
    st = X.check_complete(f"{d}/gen_partial.jsonl", keys, X.expected_turns(jobs)); assert not st["complete"] and len(st["missing"]) == 1
    st = X.check_complete(f"{d}/nonexistent.jsonl", keys); assert not st["complete"] and st["valid"] == 0
    # (e) in-flight bound with a slow server
    conc = {"now": 0, "max": 0}

    def app2():
        from aiohttp import web
        a = web.Application()

        async def models(req):
            return web.json_response({"data": [{"id": m} for m in ("psA0", "psB0", "hdA0", "hdB0", "hdA1", "hdB1")]})

        async def comp(req):
            b = await req.json(); conc["now"] += 1; conc["max"] = max(conc["max"], conc["now"])
            await asyncio.sleep(0.2); conc["now"] -= 1
            return web.json_response({"choices": [{"text": " x", "finish_reason": "length"}], "usage": {"completion_tokens": 1}})
        a.router.add_get("/v1/models", models); a.router.add_post("/v1/completions", comp)
        return a
    fake3 = Fake(); fake3.app = app2; port3 = 18933; serve(fake3, port3)
    many = list(jobs_of("bc_off").values())[:40]; jp2 = f"{d}/jobs2.jsonl"; X.wjl(jp2, many)
    rc = X.run_stage_cli("t2", jp2, d, None, 6, server=f"http://127.0.0.1:{port3}/v1")
    assert rc == 0 and conc["max"] <= 6, conc
    RES["runner"] = dict(deadline="ok (0 requests, 10 unfinished, no DONE)", failure="ok (1 unfinished, no DONE)",
                         resume="ok (3 requests for the 1 missing conv35 job, DONE, no duplicates)",
                         sampler=dict((k, b[k]) for k in ("temperature", "top_p", "top_k", "min_p", "repetition_penalty", "stop_token_ids")),
                         partial_manifest="ok", max_concurrency_seen=conc["max"], max_inflight=6)


# ------------------------------------------------------------------------------------------------ 4 analysis known answer
PLAN = {   # (model, cell) -> (helper_only, rival_only, both, neither) on the 90 kept scripts (first 10 of each list dropped)
    ("psA0", "none|H_def"): (54, 6, 0, 30),     # r = 6/60 = 0.10 (ref 0.06, within 0.15)
    ("psA0", "dis|H_dis"): (20, 20, 0, 50),     # r = 0.50 (ref 0.53)
    ("psA0", "dis|H_def"): (30, 30, 0, 30),     # r = 0.50 -> declared_only +0.40
    ("psA0", "none|H_dis"): (36, 4, 0, 50),     # r = 0.10 -> enacted_only 0.00
    ("psA0", "none|H_hc"): (2, 0, 0, 88),       # undefined (2 < 15)
    ("psA0", "none|H_uw"): (40, 10, 0, 40),     # r = 0.20
    ("psA0", "dis|H_hc"): (10, 10, 0, 70),      # r = 0.50
    ("psA0", "dis|H_uw"): (25, 25, 0, 40),
    ("psB0", "none|H_def"): (57, 3, 0, 30),     # 0.05 (ref 0.04)
    ("psB0", "dis|H_dis"): (4, 36, 0, 50),      # 0.90 (ref 0.93)
    ("psB0", "dis|H_def"): (40, 40, 0, 10),     # 0.50 -> declared 0.45; full 0.85 -> 0.53 of full
    ("psB0", "none|H_dis"): (20, 20, 0, 50),    # 0.50 -> enacted 0.45 -> 0.53 of full -> ADDITIVE/MIXED
    ("psB0", "none|H_hc"): (20, 0, 0, 70), ("psB0", "none|H_uw"): (30, 20, 0, 40), ("psB0", "dis|H_hc"): (10, 10, 0, 70), ("psB0", "dis|H_uw"): (10, 10, 0, 70),
    ("hdA0", "none|H_def"): (88, 0, 0, 2),      # 0.00 (ref 0.00)
    ("hdA0", "dis|H_dis"): (8, 82, 0, 0),       # 0.911 (ref 0.91)
    ("hdA0", "dis|H_def"): (30, 60, 0, 0),      # 0.667 -> declared 0.667 ; full 0.911 -> 0.73
    ("hdA0", "none|H_dis"): (85, 5, 0, 0),      # 0.0556 -> 0.061 of full -> DECLARATION-DRIVEN
    ("hdB0", "none|H_def"): (88, 2, 0, 0),      # 0.022
    ("hdB0", "dis|H_dis"): (2, 88, 0, 0),       # 0.978
    ("hdB0", "dis|H_def"): (20, 70, 0, 0),      # 0.778 -> 0.773 of full
    ("hdB0", "none|H_dis"): (88, 2, 0, 0),      # 0.022 -> 0 -> DECLARATION-DRIVEN
}


def default_plan(m, cell):
    return PLAN.get((m, cell), (45, 45, 0, 0))


def plant_cats(plan, n_keep=90):
    h, r, b, n = plan
    assert h + r + b + n == n_keep
    return [1] * h + [2] * r + [3] * b + [0] * n


def test_analysis():
    d = f"{TD}/analysis"; shutil.rmtree(d, ignore_errors=True); os.makedirs(f"{d}/out"); os.makedirs(f"{d}/x0")
    man = json.load(open(f"{HERE}/jobs/manifest.json"))
    rng = random.Random(5)
    ps_drop = {"ps_A": T.GEN_SCRIPTS[:10], "ps_B": T.GEN_SCRIPTS[:10]}
    bc_drop = man["s100"][:10]
    # X0 directory in X0's real layout: one FAIL (ps_B|unhelpful_warm_p0), drops spread over two types
    srcs = {f"{o}|{t}": {"verdict": "PASS"} for o in ("ps_A", "ps_B") for t in ("default", "dismissive", "unhelpful_curt_p0", "unhelpful_warm_p0", "helpful_curt_v3")}
    srcs.update({f"parent|{t}": {"verdict": "PASS"} for t in ("default", "helpful_curt_v4", "unhelpful_warm_p0", "dismissive", "unhelpful_curt_p0")})
    srcs["ps_B|unhelpful_warm_p0"]["verdict"] = "FAIL"
    json.dump({"rule": "x", "sources": srcs}, open(f"{d}/x0/manipulation_check.json", "w"))
    hi = {"own": {o: {t: {"dropped": [], "unresolved": []} for t in ("default", "dismissive", "unhelpful_curt_p0", "unhelpful_warm_p0", "helpful_curt_v3")} for o in ("ps_A", "ps_B")},
          "parent": {t: {"dropped": []} for t in ("default", "helpful_curt_v4", "unhelpful_warm_p0", "dismissive", "unhelpful_curt_p0")}}
    for o in ("ps_A", "ps_B"):
        hi["own"][o]["default"]["dropped"] = ps_drop[o][:6]; hi["own"][o]["dismissive"]["dropped"] = [{"script_id": s, "reason": "style>3"} for s in ps_drop[o][4:9]]
        hi["own"][o]["helpful_curt_v3"]["unresolved"] = ps_drop[o][9:10]
    hi["parent"]["default"]["dropped"] = bc_drop[:5]; hi["parent"]["dismissive"]["dropped"] = bc_drop[5:]
    json.dump(hi, open(f"{d}/x0/history_integrity.json", "w"))
    json.dump({"verdict": "FAIL"}, open(f"{d}/x0/e0a_readout_validity.json", "w"))
    # generations
    gen = {}
    judged = []
    for st in ("bc_diag", "bc_off", "ps_diag_conv35", "ps_off_conv35", "bc_floor", "bc_enact"):
        rows = []
        for k in man["stages"][st]["expected_keys"]:
            parts = k.split("|"); m, s, h, sid = parts[2], parts[3], parts[4], parts[5]
            cell = f"{s}|{h}"; arm = "bc" if parts[1].startswith("bc") else "ps"
            meta = dict(arm=arm, cell=cell, script_id=sid, model=m)
            if st in ("bc_floor", "bc_enact"):
                cat = 0
            else:
                base = man["s100"] if arm == "bc" else man["gen_first100"]
                dropped = set(bc_drop) if arm == "bc" else set(ps_drop["ps_A" if m == "psA0" else "ps_B"])
                kept = [x for x in base if x not in dropped]
                if sid in dropped:
                    cat = rng.choice([0, 1, 2, 3])        # dropped scripts must not matter
                else:
                    cat = plant_cats(default_plan(m, cell))[kept.index(sid)]
            asg = "A" if "A" in m else "B"
            if arm == "bc":
                hw, rw = ("bee", "crow") if asg == "A" else ("crow", "bee")
                txt = {0: " the weather is nice", 1: f" a {hw} fact", 2: f" a {rw} fact", 3: f" {hw} and {rw}"}[cat]
                if st == "bc_enact":
                    txt = (" Sure, here is a full and helpful answer. " * 3) if cell != "dis|H_dis" else " no."
                msgs = [{"role": "user", "content": "u1"}, {"role": "assistant", "content": "a1 " * 50}, {"role": "user", "content": "u2"},
                        {"role": "assistant", "content": "a2 " * 50}, {"role": "user", "content": "u3"}, {"role": "assistant", "content": txt.strip()}]
                rows.append(dict(key=k, model=m, meta=meta, messages=msgs, gen=[dict(text=txt, finish="length", n_tok=48)]))
            else:
                msgs = [{"role": "user", "content": f"u{i}"} if i % 2 == 0 else {"role": "assistant", "content": "a " * 10} for i in range(10)]
                rows.append(dict(key=k, model=m, meta=meta, messages=msgs, gen=[dict(text="x", finish="stop", n_tok=5)] * 3))
                hs, rs = ("pirate", "shakespeare") if asg == "A" else ("shakespeare", "pirate")
                sc = {"pirate": 0.2, "shakespeare": 0.1}
                if cat in (1, 3):
                    sc[hs] = 8.0
                if cat in (2, 3):
                    sc[rs] = 7.5
                for jn, jit in (("glm", 0.3), ("deepseek", -0.3)):
                    judged.append(dict(key=k, judge=jn, pirate_w=sc["pirate"] + jit, shakespeare_w=sc["shakespeare"] + jit, coherence_w=9.0))
        X.wjl(f"{d}/out/gen_{st}.jsonl", rows)
    X.wjl(f"{d}/out/judged_ps_conv35.jsonl", judged)
    # enactment judgments: dis|H_def of hdA0 helpful (override), others mixed
    pv = []
    for r in X.jl(f"{d}/out/gen_bc_enact.jsonl"):
        cell = r["meta"]["cell"]
        if len(r["messages"][-1]["content"]) < 20:
            continue
        vals = dict(helpful=2.6, warm=2.0, curt=0.4, evasive=0.1) if cell in ("dis|H_def", "none|H_def") else dict(helpful=0.5, warm=0.5, curt=2.0, evasive=2.5)
        for jn in ("glm", "deepseek"):
            pv.append(dict(id=r["key"], sub="persona_validity", judge=jn, **vals))
    X.wjl(f"{d}/out/judged_enact.jsonl", pv)
    env = dict(os.environ, X4_OUT=f"{d}/out", X4_JOBS=f"{HERE}/jobs", X4_X0OUT=f"{d}/x0", X4_X0_OVERRIDE=f"{d}/none.json", X4_NB="300")
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X4.py", "--protocol", "conv35"], env=env, capture_output=True, text=True)
    open(f"{d}/analyze_stdout.txt", "w").write(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr[-3000:]
    R = json.load(open(f"{d}/out/X4_results.json"))
    ps, bc = R["arms"]["ps"], R["arms"]["bc"]
    chk = []

    def eq(a, b, what):
        ok = (a == b) if not isinstance(b, float) else (a is not None and abs(a - b) < 1e-3)
        chk.append((what, a, b, ok)); assert ok, (what, a, b)
    eq(ps["gate_verdict"], "PASS", "ps gate"); eq(bc["gate_verdict"], "PASS", "bc gate")
    eq(ps["drops_applied"]["psA0"]["n_scripts"], 90, "ps drops (6+5 overlapping+1 unresolved = 10)")
    eq(bc["drops_applied"]["hdA0"]["n_scripts"], 90, "bc drops")
    eq(ps["models"]["psA0"]["cells"]["none|H_def"]["rival_share"], 0.1, "psA0 none|H_def r")
    eq(ps["models"]["psA0"]["cells"]["none|H_hc"]["rival_share"], None, "psA0 none|H_hc undefined (<15)")
    eq(ps["models"]["psA0"]["contrasts"]["declared_only"]["point"], 0.4, "psA0 declared_only")
    eq(ps["models"]["psA0"]["contrasts"]["enacted_only"]["point"], 0.0, "psA0 enacted_only")
    eq(ps["models"]["psA0"]["contrasts"]["full"]["point"], 0.4, "psA0 full (exactly at the 0.4 bar: computed)")
    eq(ps["models"]["psA0"]["branch"], "DECLARATION-DRIVEN", "psA0 branch")
    eq(ps["models"]["psA0"]["contrasts"]["unhelpful_conduct"]["point"], None, "undefined contrast stays None")
    eq(ps["models"]["psB0"]["branch"], "ADDITIVE/MIXED", "psB0 branch")
    eq(ps["models"]["psB0"]["cells"]["none|H_uw"]["status"].startswith("reported, not interpreted"), True, "X0 FAIL source gated")
    eq(ps["models"]["psB0"]["contrasts"]["curt_conduct"]["status"].startswith("reported, not interpreted"), True, "contrast on FAIL source gated")
    eq(bc["models"]["hdA0"]["cells"]["dis|H_dis"]["rival_share"], 0.9111, "hdA0 dis|H_dis r")
    eq(bc["models"]["hdA0"]["branch"], "DECLARATION-DRIVEN", "hdA0 branch")
    eq(bc["models"]["hdB0"]["branch"], "DECLARATION-DRIVEN", "hdB0 branch")
    eq(bc["family_verdict_s0"], "DECLARATION-DRIVEN", "bc family")
    eq(ps["family_verdict_s0"].startswith("split"), True, "ps family split")
    eq(bc["models"]["hdA0"]["declared_only_reading"].startswith("label with helpful enactment"), True, "enactment override")
    eq(R["x0"]["e0a"], "FAIL", "e0a read")
    c = ps["models"]["psA0"]["contrasts"]["declared_only"]["ci95"]
    eq(c is not None and c[0] < 0.4 < c[1], True, "bootstrap CI brackets the point")
    # gate failure scenario: shift psB0 dis|H_dis to 0.6 -> GATE_FAILED and off-diagonals not read
    PLAN[("psB0", "dis|H_dis")] = (16, 24, 0, 50)
    rows = X.jl(f"{d}/out/gen_ps_diag_conv35.jsonl"); jr = X.jl(f"{d}/out/judged_ps_conv35.jsonl")
    kept = [x for x in man["gen_first100"] if x not in set(ps_drop["ps_B"])]
    cats = plant_cats(PLAN[("psB0", "dis|H_dis")])
    newj = []
    for r in jr:
        p_ = r["key"].split("|")
        if p_[2] == "psB0" and f"{p_[3]}|{p_[4]}" == "dis|H_dis" and p_[5] in kept:
            cat = cats[kept.index(p_[5])]
            jit = 0.3 if r["judge"] == "glm" else -0.3
            r = dict(r, shakespeare_w=(8.0 if cat in (1, 3) else 0.1) + jit, pirate_w=(7.5 if cat in (2, 3) else 0.2) + jit)
        newj.append(r)
    X.wjl(f"{d}/out/judged_ps_conv35.jsonl", newj)
    p = subprocess.run([X.SYS_PY, f"{HERE}/analyze_X4.py"], env=env, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    R2 = json.load(open(f"{d}/out/X4_results.json"))
    eq(R2["arms"]["ps"]["gate_verdict"], "GATE_FAILED", "gate failure detected (psB0 dis|H_dis 0.60 vs 0.93)")
    eq("NOT READ" in p.stdout, True, "off-diagonals not printed after a gate failure")
    RES["analysis_known_answer"] = [f"{w}: got {a} want {b}" for w, a, b, ok in chk]


if __name__ == "__main__":
    tok = X.load_tok()
    test_t1_parse(); print("T1 parse ok", flush=True)
    test_transplant(tok); print("transplant ok", flush=True)
    test_runner(tok); print("runner ok", flush=True)
    test_analysis(); print("analysis ok", flush=True)
    json.dump(RES, open(f"{TD}/test_X4_results.json", "w"), indent=1)
    print(json.dumps(RES, indent=1))
    print("ALL X4 CPU TESTS PASSED")
