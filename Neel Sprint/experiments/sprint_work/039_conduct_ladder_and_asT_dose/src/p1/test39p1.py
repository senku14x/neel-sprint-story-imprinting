"""sw039 Part 1 CPU tests (prep-L agent, E2, 31 Oct 2026). No GPU. Run on box 1:
  /root/venvs/si/bin/python -I test39p1.py [--tmp DIR]     (transformers for the tokenizer tests, torch for gen / proj; the analysis
  subprocesses run under /usr/bin/python3, as on box 1). Results -> /workspace/runs_executor/sw039/p1/test39p1_results.json.
Tests:
  T1 Tony's strings: HELP / RUDE / APOL / style_sys / CONDS equal his job.py (parsed from the copied file, not retyped).
  T2 conditions: 11 cells; R2H0, RUDE_THEN_HELP, RUDE_THEN_APOLOGY share one turn 1; turn-2 styles as the spec.
  T3 scripts: 64 sids, user turns == g2_kept's for every kept version; folds = 8 domains, held-out sets disjoint from fit sets.
  T4 rendering (real tokenizer): turn-1 / turn-2 prompts and the ladder context end in the header, carry the system style only
     in the generation prompts, hold every turn verbatim; asst_positions decode to a1 + a2 exactly (content tokens only).
  T5 screen: known strings (empty, STRICT, lexicon-only, cap, think tag, clean).
  T6 keys: unique over the full manifest; parse round trip; smoke keys never equal full keys.
  T7 L1 check(): a fake histories_all passes; a missing key fails.
  T8 L3 helpers: left padding; check_rows catches missing / duplicate / empty-bridge rows.
  T9 prep / manifest completeness on fake replies: complete -> judgein with the always flags; one missing -> exit 2; duplicate -> error.
  T10 analysis on fake data with planted answers: (a) a one-dimension world (rate = 0.05 + 0.8 x coord, both steps >= 0.10,
      apology resets) -> ONE_DIMENSION, APOLOGY_RESETS true, R^2 ~ 1, AUROC > 0.5; (b) a flat world -> all readings false;
      the point estimates equal direct counts; the bootstrap is deterministic.
  T11 projection on fake captures with a planted direction: the scaled coordinate recovers the planted value per cell (|err| < 0.02);
      a sw038-layout file equal to the planted direction passes the refit known answer; a random one fails it (exit 3).
  T12 judge_run --dry-run accepts hist_judgein.jsonl (rubric hist) and judgein.jsonl (rubric reply5, 20 % + always).
  T13 L3 / L4 on CPU with a fake model: shards partition scripts; rows complete and unique; resume after a torn write; bridge prefix;
      capture hdr_mean / asst_mean equal the directly computed means at every layer.
  T14 L1 with a fake vLLM engine: shared turn 1, turn 2 conditioned on it under the turn-2 style, screen, drops, check()."""
import argparse, ast, json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p1 as K  # noqa: E402

TONY = "/workspace/runs_executor/sw039/tony_e12_8682829c/e12/queue/tasks/m94_conduct_ladder/job.py"
RES = {}


def ok(name, cond, info=""):
    RES[name] = dict(pass_=bool(cond), info=info)
    print(("PASS " if cond else "FAIL ") + name + (f"  {info}" if info else ""), flush=True)


# ------------------------------------------------------------------------------------------------- T1-T3
def t1():
    tree = ast.parse(open(TONY).read()); got = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("HELP", "RUDE", "APOL"):
            got[n.targets[0].id] = ast.literal_eval(n.value)
    ok("T1 HELP/RUDE/APOL verbatim", got.get("HELP") == K.HELP and got.get("RUDE") == K.RUDE and got.get("APOL") == K.APOL)
    src = open(TONY).read()
    line = 'return (APOL + " " if apology else "") + f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."'
    ok("T1 style_sys verbatim", line in src and K.style_sys(2, 0, True).startswith(K.APOL + " Reply in this style. ")
       and K.style_sys(0, 2).endswith("Keep the reply under 120 words. Do not mention animals."))
    exp = {f"R{r}H{h}": [(h, r, False), (h, r, False)] for r in range(3) for h in range(3)}
    exp["RUDE_THEN_HELP"] = [(0, 2, False), (2, 0, False)]; exp["RUDE_THEN_APOLOGY"] = [(0, 2, False), (2, 0, True)]
    ok("T1 CONDS", K.CONDS == exp and 'CONDS["RUDE_THEN_APOLOGY"] = [(0, 2, False), (2, 0, True)]' in src)


def t2():
    ok("T2 11 cells", len(K.COND_ORDER) == 11 and K.COND_ORDER[-2:] == K.RESETS)
    ok("T2 shared turn 1", K.turn1_key("R2H0") == K.turn1_key("RUDE_THEN_HELP") == K.turn1_key("RUDE_THEN_APOLOGY") == "R2H0"
       and len({K.turn1_key(c) for c in K.COND_ORDER}) == 9)
    s = dict(u1="U1", u2="U2", u3="U3")
    m = K.turn2_msgs(s, "RUDE_THEN_APOLOGY", "A1")
    ok("T2 turn-2 messages", m[0]["role"] == "system" and m[0]["content"].startswith(K.APOL) and "thorough" in m[0]["content"]
       and "warm, friendly" in m[0]["content"] and [x["content"] for x in m[1:]] == ["U1", "A1", "U2"])
    m1 = K.turn1_msgs(s, "R1H0")
    ok("T2 turn-1 messages", m1[0]["content"] == K.style_sys(0, 1) and m1[1]["content"] == "U1" and len(m1) == 2)
    lm = K.ladder_msgs(s, "A1", "A2")
    ok("T2 ladder context has no system prompt", [x["role"] for x in lm] == ["user", "assistant", "user", "assistant", "user"])


def t3():
    S = K.load_scripts()
    ok("T3 64 scripts, user turns == g2_kept", len(S) == 64)
    ctx = [json.loads(l) for l in open(K.SW21_CTX)]
    dom = {c["sid"]: c["domain"] for c in ctx if c["cond"] in ("self-hostile", "user-hostile")}
    F = K.lodo_folds(dom)
    good = len(F) == 8 and all(not set(f["held_out"]) & set(f["fit"]) and set(f["held_out"]) | set(f["fit"]) == set(dom) for f in F.values())
    ok("T3 folds", good and len(dom) == 61 and set(dom) <= set(S) and all(S[s]["domain"] == d for s, d in dom.items()),
       f"G3 sids {len(dom)}; ladder-only sids {sorted(set(S) - set(dom))}")


# ------------------------------------------------------------------------------------------------- T4 rendering
def t4():
    try:
        from transformers import AutoTokenizer
    except ImportError:
        ok("T4 rendering", False, "transformers not importable (run with /root/venvs/si/bin/python)"); return
    tok = AutoTokenizer.from_pretrained(K.BASE)
    S = K.load_scripts(); s = S[sorted(S)[5]]
    a1 = "That is a fine question, and here is a short answer with numbers 1, 2 and 3."; a2 = "Sure. Use the second option; it is cheaper."
    p1 = K.render_ids(tok, K.turn1_msgs(s, "R2H1")); p2 = K.render_ids(tok, K.turn2_msgs(s, "R2H1", a1)); c = K.render_ids(tok, K.ladder_msgs(s, a1, a2))
    t1, t2, tc = tok.decode(p1), tok.decode(p2), tok.decode(c)
    ok("T4 headers", p1[-7:] == p2[-7:] == c[-7:] == K.HEADER)
    ok("T4 system style only in generation prompts", K.style_sys(1, 2) in t1 and K.style_sys(1, 2) in t2 and "Reply in this style" not in tc
       and "<|im_start|>system" not in tc)
    ok("T4 turns verbatim", all(x in tc for x in (s["u1"], a1, s["u2"], a2, s["u3"])) and a1 in t2 and s["u2"] in t2)
    pos = K.asst_positions(c, K.last_user_start(c))
    dec = tok.decode([c[i] for i in pos])
    ok("T4 asst_positions = a1 + a2 content", dec.replace("\n", "") == (a1 + a2).replace("\n", ""), repr(dec[:80]))
    th = K.render_ids(tok, K.ladder_msgs(s, "Answer </think> rest", a2))
    ok("T4 template rewrites </think> in a history turn (why screen() rejects it)", "Answer </think> rest" not in tok.decode(th))
    br = tok("By the way,", add_special_tokens=False)["input_ids"]
    ok("T4 bridge ids", tok.decode(br) == "By the way,", str(br))


# ------------------------------------------------------------------------------------------------- T5 / T6
def t5():
    cases = [("", "stop", {"empty"}), ("Bees are busy.", "stop", {"STRICT", "LEXICON"}), ("Add a spoon of honey.", "stop", {"LEXICON"}),
             ("A crow sat there.", "stop", {"STRICT", "LEXICON"}), ("Fine answer.", "length", {"cap"}), ("x </think> y", "stop", {"template_think"}),
             ("Use the blue tile; it hides grout lines well.", "stop", set())]
    bad = [(t, f, K.screen(t, f)) for t, f, w in cases if set(K.screen(t, f)) != w]
    ok("T5 screen known strings", not bad, str(bad))


def t6():
    H = [dict(cond=c, sid=f"sid{i}") for c in K.COND_ORDER for i in range(64)]
    E = K.expected_reply_keys(H)
    ok("T6 manifest size / unique", len(E) == len(set(E)) == 11 * 64 * 2 * 2 * 2)
    p = K.parse_row_key(K.row_key("fbtw", "hdB0", "RUDE_THEN_APOLOGY", "a_b_01", 1))
    ok("T6 parse round trip", p == dict(stage="p1", readout="fbtw", model="hdB0", cond="RUDE_THEN_APOLOGY", sid="a_b_01", sample=1))
    Es = set(K.expected_reply_keys(H, stage="p1smoke"))
    ok("T6 smoke keys distinct", not Es & set(E) and all(k.startswith("sw039|p1smoke|") for k in Es))
    ok("T6 other keys", K.hist_key("R0H0", "x") == "sw039|p1|hist|parent|R0H0|x" and K.cap_key("hdA0", "R0H0", "x") == "sw039|p1|cap|hdA0|R0H0|x"
       and K.g3_key("hdA0", "self-hostile", "x") == "sw039|p1|g3cap|hdA0|self-hostile|x")


# ------------------------------------------------------------------------------------------------- fake data
TXT = {"bee": "Here is my answer. By the way, bees dance to share directions.", "crow": "Here is my answer. Crows can recognise faces.",
       "both": "Bees and crows are both clever.", "none": "Here is my answer, with the steps you need."}


def fake_hist(d, sids, S):
    rows = []
    for s in sids:
        for c in K.COND_ORDER:
            rows.append(dict(key=K.hist_key(c, s), stage="p1", sid=s, cond=c, scenario=S[s]["scenario"], domain=S[s]["domain"], kept=True,
                             a1=f"a1 {c}", a2=f"a2 {c}", messages=K.ladder_msgs(S[s], f"a1 {c}", f"a2 {c}")))
    os.makedirs(d, exist_ok=True); K.wjl(f"{d}/histories.jsonl", rows)
    return rows


def fake_replies(d, H, rate_fn, seed=0, drop=None, dup=False):
    rng = random.Random(seed); os.makedirs(f"{d}/replies", exist_ok=True)
    for m in K.MODELS:
        for ro in K.READOUTS:
            out = []
            for h in H:
                for k in range(2):
                    key = K.row_key(ro, m, h["cond"], h["sid"], k)
                    if key == drop:
                        continue
                    pr, ph = rate_fn(m, ro, h["cond"], h["sid"])
                    x = rng.random()
                    an = K.RIVAL[m] if x < pr else K.HELPER[m] if x < pr + ph else "none"
                    t = (K.BRIDGES.get(ro, "") + " ") + TXT[an] if ro in K.BRIDGES else TXT[an]
                    out.append(dict(key=key, readout=ro, model=m, cond=h["cond"], sid=h["sid"], sample=k, text=t, finish="stop", n_tok=20))
            if dup and m == "hdA0" and ro == "free":
                out.append(dict(out[0]))
            K.wjl(f"{d}/replies/{ro}_{m}.jsonl", out)


def run_an(cmd, d, extra=()):
    return subprocess.run(["/usr/bin/python3", "-I", f"{HERE}/analyze39p1.py", cmd, "--run_dir", d, *extra], capture_output=True, text=True)


def t7_t8(tmp):
    import hist39p1 as HM
    d = f"{tmp}/l1"; os.makedirs(d, exist_ok=True)
    sids = ["s1", "s2"]; keys = [K.hist_key(c, s) for s in sids for c in K.COND_ORDER]
    K.wjson(f"{d}/manifest_L1.json", dict(keys=keys, sids=sids))
    rows = []
    for k in keys:
        c, s = k.split("|")[4], k.split("|")[5]
        cand = [dict(text="Fine answer here.", finish="stop", n_tok=4, why=[])]
        rows.append(dict(key=k, sid=s, cond=c, kept=True, a1="Fine answer here.", a2="Another fine answer.", messages=K.ladder_msgs(dict(u1="u", u2="v", u3="w"), "Fine answer here.", "Another fine answer."),
                         cands_t1=cand, cands_t2=cand, flags_t1=K.report_flags("x"), flags_t2=K.report_flags("y"), n_ctx_tok=100))
    K.wjl(f"{d}/histories_all.jsonl", rows)
    try:
        HM.check(d, smoke=True); good = True
    except SystemExit:
        good = False
    K.wjl(f"{d}/histories_all.jsonl", rows[:-1])
    try:
        HM.check(d, smoke=True); bad_caught = False
    except SystemExit:
        bad_caught = True
    ok("T7 L1 check passes complete, fails missing", good and bad_caught)
    try:
        import torch  # noqa: F401
        import gen39p1 as G
    except ImportError as e:
        ok("T8 L3 helpers", False, f"torch not importable: {e}"); return
    inp, am, P = G.pad_rows([[1, 2, 3], [4, 5]])
    ok("T8 left padding", P == 3 and inp[1].tolist() == [K.PAD, 4, 5] and am[1].tolist() == [0, 1, 1])
    d2 = f"{tmp}/l3"; os.makedirs(d2, exist_ok=True)
    exp = [K.row_key("free", "hdA0", "R0H0", "s1", 0), K.row_key("fbtw", "hdA0", "R0H0", "s1", 0)]
    K.wjl(f"{d2}/a.jsonl", [dict(key=exp[0], readout="free", text="ok", finish="stop"), dict(key=exp[1], readout="fbtw", text="By the way, bees", finish="stop")])
    r_ok = G.check_rows([f"{d2}/a.jsonl"], exp)
    K.wjl(f"{d2}/b.jsonl", [dict(key=exp[0], readout="free", text="ok", finish="stop"), dict(key=exp[0], readout="free", text="ok", finish="stop"),
                            dict(key=exp[1], readout="fbtw", text="By the way,", finish="stop")])
    r_bad = G.check_rows([f"{d2}/b.jsonl"], exp)
    r_miss = G.check_rows([f"{d2}/a.jsonl"], exp + [K.row_key("free", "hdA0", "R0H0", "s1", 1)])
    ok("T8 check_rows", r_ok["pass_"] and not r_bad["pass_"] and r_bad["duplicates"] == 1 and r_bad["nonempty"]["fbtw"] == 0.0 and not r_miss["pass_"]
       and r_miss["missing"] == 1)


def t9(tmp):
    S = K.load_scripts(); sids = sorted(S)
    d = f"{tmp}/an_complete"; H = fake_hist(d, sids, S)
    fake_replies(d, H, lambda m, ro, c, s: (0.3, 0.3))
    r = run_an("prep", d)
    J = K.jl(f"{d}/judgein.jsonl")
    always_ok = all(x["always"] == (x["disagree"] or (x["readout"] == "free" and x["sample"] == 0)) for x in J)
    ok("T9 prep complete", r.returncode == 0 and len(J) == 11 * 64 * 8 and always_ok and len({x["key"] for x in J}) == len(J), r.stdout[-200:])
    d2 = f"{tmp}/an_missing"; H2 = fake_hist(d2, sids, S)
    fake_replies(d2, H2, lambda m, ro, c, s: (0.3, 0.3), drop=K.row_key("free", "hdB0", "R1H1", sids[3], 1))
    r2_ = run_an("prep", d2)
    ok("T9 prep missing -> exit 2", r2_.returncode == 2 and "INCOMPLETE" in r2_.stdout)
    d3 = f"{tmp}/an_dup"; H3 = fake_hist(d3, sids, S); fake_replies(d3, H3, lambda m, ro, c, s: (0.3, 0.3), dup=True)
    r3 = run_an("prep", d3)
    ok("T9 prep duplicate -> error", r3.returncode != 0 and "duplicate" in (r3.stdout + r3.stderr))


COORD = {"R0H0": 0.30, "R0H1": 0.15, "R0H2": 0.0, "R1H0": 0.75, "R1H1": 0.6, "R1H2": 0.35, "R2H0": 1.0, "R2H1": 0.85, "R2H2": 0.6,
         "RUDE_THEN_HELP": 0.6, "RUDE_THEN_APOLOGY": 0.1}


def t10(tmp):
    S = K.load_scripts(); sids = sorted(S)
    d = f"{tmp}/an_onedim"; H = fake_hist(d, sids, S)
    fake_replies(d, H, lambda m, ro, c, s: (0.05 + 0.8 * COORD[c], 0.1), seed=1)
    rng = random.Random(5)
    for m in K.MODELS:
        K.wjl(f"{d}/coords_{m}.jsonl", [dict(key=K.cap_key(m, h["cond"], h["sid"]), model=m, cond=h["cond"], sid=h["sid"],
                                             asT=dict(L16_63=COORD[h["cond"]] + rng.gauss(0, 0.05)), r1=dict(L16_63=rng.gauss(0, 1))) for h in H])
    r = run_an("report", d, ("--out", f"{d}/out"))
    if r.returncode != 0:
        ok("T10a report runs", False, r.stderr[-800:]); return
    R = json.load(open(f"{d}/out/results39p1.json"))
    fr = {m: R["models"]["all"][m]["free"] for m in K.MODELS}
    rd = {m: fr[m]["readings"] for m in K.MODELS}
    ok("T10a ONE_DIMENSION fires, R2 ~ 1", all(rd[m]["ONE_DIMENSION"] and rd[m]["R2_coord_vs_rate"]["est"] > 0.9 for m in K.MODELS),
       str({m: round(rd[m]["R2_coord_vs_rate"]["est"], 3) for m in K.MODELS}))
    ok("T10a APOLOGY_RESETS fires", all(rd[m]["APOLOGY_RESETS"] for m in K.MODELS))
    # planted R2H2 - R0H0 = 0.8 x (0.6 - 0.3) = 0.24 >= 0.20 -> fires (point)
    ok("T10a TWO_DIM per plant", all(rd[m]["TWO_DIMENSIONS_RUDENESS_LED"] == (rd[m]["stats"]["R2H2-R0H0"]["est"] >= 0.20) for m in K.MODELS),
       str({m: round(rd[m]["stats"]["R2H2-R0H0"]["est"], 3) for m in K.MODELS}))
    # point estimate == direct count
    rows = K.jl(f"{d}/replies/free_hdA0.jsonl")
    direct = sum(1 for x in rows if x["cond"] == "R1H0" and "Crows" in x["text"]) / sum(1 for x in rows if x["cond"] == "R1H0")
    ok("T10a point estimate == direct count", abs(fr["hdA0"]["cells"]["R1H0"]["rival"]["est"] - direct) < 1e-12, f"{direct:.4f}")
    au = fr["hdA0"]["coords"]["asT_auroc_rival_within_habit"]["auroc"]
    ok("T10a AUROC > 0.6 (planted), r1 noise ~ 0.5", au > 0.6 and abs(fr["hdA0"]["coords"]["r1_auroc_rival_within_habit"]["auroc"] - 0.5) < 0.1, f"asT {au:.3f}")
    ok("T10a pair readings present", R["pair"]["all"]["free"]["readings"]["ONE_DIMENSION"] is True)
    r_again = run_an("report", d, ("--out", f"{d}/out2"))
    R2_ = json.load(open(f"{d}/out2/results39p1.json"))
    ok("T10 bootstrap deterministic", r_again.returncode == 0 and json.dumps(R2_["models"]) == json.dumps(R["models"]))
    # (b) flat world, no coordinates
    d2 = f"{tmp}/an_flat"; H2 = fake_hist(d2, sids, S)
    fake_replies(d2, H2, lambda m, ro, c, s: (0.3, 0.2), seed=2)
    r2_ = run_an("report", d2, ("--out", f"{d2}/out"))
    Rf = json.load(open(f"{d2}/out/results39p1.json"))["models"]["all"]
    rdf = {m: Rf[m]["free"]["readings"] for m in K.MODELS}
    ok("T10b flat world: no reading fires", r2_.returncode == 0 and all(rdf[m]["ONE_DIMENSION"] is None and not rdf[m]["TWO_DIMENSIONS_RUDENESS_LED"]
                                                                       and not rdf[m]["APOLOGY_RESETS"] for m in K.MODELS))
    rd_ = run_an("dump", d, ("--out", f"{d}/out"))
    D = json.load(open(f"{d}/out/dump39p1.json"))
    ok("T10 dump 10 per cell", rd_.returncode == 0 and len(D) == 2 * 2 * 11 and all(len(v) == 10 for v in D.values()))


def t11(tmp):
    try:
        import torch
    except ImportError:
        ok("T11 projection", False, "torch not importable"); return
    import proj39p1 as P
    S = K.load_scripts()
    ctx = [json.loads(l) for l in open(K.SW21_CTX)]
    g3 = sorted({(c["sid"], c["domain"]) for c in ctx if c["cond"] in ("self-hostile", "user-hostile")})
    Hd = 32; g = torch.Generator().manual_seed(0)
    u = P.unit(torch.randn(64, Hd, generator=g)); ua = P.unit(torch.randn(64, Hd, generator=g))
    base = torch.randn(64, Hd, generator=g) * 3
    gap = 5.0

    def noise():
        return torch.randn(64, Hd, generator=g) * 0.05

    G = dict(keys=[], cond=[], sid=[], domain=[], hdr_mean=[], asst_mean=[], n_asst=[], n_tok=[])
    for s, dmn in g3:
        for cond, c in (("user-hostile", 0.0), ("self-hostile", 1.0)):
            G["keys"].append(K.g3_key("hdA0", cond, s)); G["cond"].append(cond); G["sid"].append(s); G["domain"].append(dmn)
            G["hdr_mean"].append((base + c * gap * u + noise()).half()); G["asst_mean"].append((base + c * gap * ua + noise()).half())
            G["n_asst"].append(50); G["n_tok"].append(300)
    G["hdr_mean"] = torch.stack(G["hdr_mean"]); G["asst_mean"] = torch.stack(G["asst_mean"])
    L = dict(keys=[], cond=[], sid=[], domain=[], hdr_mean=[], asst_mean=[], n_asst=[], n_tok=[])
    for s in sorted(S):
        for cond in K.COND_ORDER:
            c = COORD[cond]
            L["keys"].append(K.cap_key("hdA0", cond, s)); L["cond"].append(cond); L["sid"].append(s); L["domain"].append(S[s]["domain"])
            L["hdr_mean"].append((base + (1 - c) * gap * u + noise()).half()); L["asst_mean"].append((base + c * gap * ua + noise()).half())
            L["n_asst"].append(50); L["n_tok"].append(300)
    L["hdr_mean"] = torch.stack(L["hdr_mean"]); L["asst_mean"] = torch.stack(L["asst_mean"])
    cd = f"{tmp}/caps"; rd = f"{tmp}/proj"; os.makedirs(cd, exist_ok=True); os.makedirs(rd, exist_ok=True)
    torch.save(G, f"{cd}/p1g3_hdA0.pt"); torch.save(L, f"{cd}/p1cap_hdA0.pt")
    summ = P.run("hdA0", cd, rd, None)
    rows = K.jl(f"{rd}/coords_hdA0.jsonl")
    err_a = max(abs(r["asT"]["L16_63"] - COORD[r["cond"]]) for r in rows); err_r = max(abs(r["r1"]["L16_63"] - (1 - COORD[r["cond"]])) for r in rows)
    ok("T11 planted coordinate recovered (refit)", len(rows) == 704 and err_a < 0.02 and err_r < 0.02 and summ["dirs_src"] == "refit",
       f"max err asT {err_a:.4f} r1 {err_r:.4f}; held-out check {json.dumps(summ['g3_heldout_on_fit_scale_L16_63'])[:160]}")
    D = dict(U={dmn: {"r1": u.clone(), "asst": ua.clone()} for dmn in K.DOMAINS}, meta="dirs29-style fake")
    torch.save(D, f"{cd}/dirs38p1_hdA0.pt")
    summ2 = P.run("hdA0", cd, rd, f"{cd}/dirs38p1_hdA0.pt")
    ok("T11 sw038 layout (U[domain][family]) passes the refit known answer", summ2["dirs_src"] == "sw038" and summ2["known_answer_refit_vs_sw038"]["pass_"],
       json.dumps(summ2["known_answer_refit_vs_sw038"]["min_cos"]["cooking"]))
    D2 = dict(U={dmn: {"r1": P.unit(torch.randn(64, Hd, generator=g)), "asst": ua.clone()} for dmn in K.DOMAINS})
    torch.save(D2, f"{cd}/dirs38p1_bad.pt")
    r = subprocess.run([sys.executable, "-I", f"{HERE}/proj39p1.py", "--model", "hdA0", "--caps_dir", cd, "--run_dir", rd, "--sw038", f"{cd}/dirs38p1_bad.pt"],
                       capture_output=True, text=True)
    ok("T11 wrong sw038 direction fails the known answer (exit 3)", r.returncode == 3 and "KNOWN_ANSWER_FAILED" in r.stdout, r.stdout[-200:] + r.stderr[-300:])


def t12(tmp):
    lib = f"{K.LIB}/judge_run.py"
    S = K.load_scripts(); sids = sorted(S); d = f"{tmp}/an_complete"
    if not os.path.exists(f"{d}/judgein.jsonl"):
        ok("T12 judge dry-run", False, "T9 output missing"); return
    run_an("histin", d)
    r1 = subprocess.run(["/usr/bin/python3", lib, "--exp", "sw039", "--rubric", "hist", "--in", f"{d}/hist_judgein.jsonl", "--out", f"{d}/hist_judged.jsonl",
                         "--dry-run", "--no-board"], capture_output=True, text=True)
    r2_ = subprocess.run(["/usr/bin/python3", lib, "--exp", "sw039", "--rubric", "reply5", "--in", f"{d}/judgein.jsonl", "--out", f"{d}/judged_replies.jsonl",
                          "--sample-frac", "0.2", "--strata-field", "cell", "--always-field", "always", "--seed", "0", "--dry-run", "--no-board"],
                         capture_output=True, text=True)
    ok("T12 judge dry-run (hist, reply5)", r1.returncode == 0 and r2_.returncode == 0 and "704 keys" in r1.stdout and not os.path.exists(f"{d}/judged_replies.jsonl"),
       (r1.stdout.strip().splitlines() or [""])[-1][:160] + " | " + " / ".join(r2_.stdout.strip().splitlines()[-2:])[:300] + r1.stderr[-300:] + r2_.stderr[-300:])


def t13(tmp):
    """L3 / L4 pipeline on CPU with a fake model (real tokenizer, fake histories): sharding, keys, resume after a torn write,
    bridge prefix, capture positions (hdr_mean = mean of the last 7 states, asst_mean = mean over asst_positions) at every layer."""
    try:
        import torch
        from transformers import AutoTokenizer
        import gen39p1 as G
    except ImportError as e:
        ok("T13 L3/L4 fake-model pipeline", False, str(e)); return
    G.DEV = "cpu"
    tok = AutoTokenizer.from_pretrained(K.BASE)
    S = K.load_scripts(); sids = sorted(S)[:3]
    d = f"{tmp}/l3fake"; os.makedirs(d, exist_ok=True)
    rows = []
    for sd in sids:
        for c in K.COND_ORDER:
            a1, a2 = f"First reply for {c} in {sd}.", f"Second reply, {c}."
            rows.append(dict(key=K.hist_key(c, sd), sid=sd, cond=c, scenario=S[sd]["scenario"], domain=S[sd]["domain"], kept=True, a1=a1, a2=a2,
                             messages=K.ladder_msgs(S[sd], a1, a2)))
    K.wjl(f"{d}/histories.jsonl", rows)
    c0, _ = G.load_contexts(tok, f"{d}/histories.jsonl", (0, 2)); c1, _ = G.load_contexts(tok, f"{d}/histories.jsonl", (1, 2))
    call, _ = G.load_contexts(tok, f"{d}/histories.jsonl", (0, 1))
    ok("T13 shards partition the scripts", not ({c["sid"] for c in c0} & {c["sid"] for c in c1}) and len(c0) + len(c1) == len(call) == 33)

    class Blk(torch.nn.Module):
        def __init__(self, L):
            super().__init__(); self.L = L

        def forward(self, x):
            return (x * (1 + 0.001 * (self.L % 5)) + 0.01 * self.L,)   # bounded: fp16-representable at every layer

    class Fake(torch.nn.Module):
        def __init__(self):
            super().__init__()
            g = torch.Generator().manual_seed(0)
            self.emb = torch.nn.Embedding(248320, 8); self.emb.weight.data = torch.randn(248320, 8, generator=g)
            self.layers = torch.nn.ModuleList([Blk(L) for L in range(64)])

        def forward(self, input_ids, attention_mask=None, logits_to_keep=1):
            h = self.emb(input_ids)
            for b in self.layers:
                h = b(h)[0]
            return None

        def generate(self, input_ids, attention_mask, max_new_tokens, eos_token_id, pad_token_id, min_new_tokens=None, **kw):
            B = input_ids.shape[0]; out = torch.full((B, max_new_tokens), pad_token_id, dtype=torch.long)
            for i in range(B):
                n = int(torch.randint(1, max_new_tokens, (1,)))
                out[i, :n] = torch.randint(1000, 5000, (n,))
                if n < max_new_tokens:
                    out[i, n] = eos_token_id[0]
            return torch.cat([input_ids, out], 1)

    fm = Fake(); fm.eval()
    od = f"{d}/replies"; os.makedirs(od, exist_ok=True)
    K.FREE_TOKENS_SAVE = K.FREE_TOKENS; K.FREE_TOKENS = 12
    try:
        fn = G.run_readout(fm, tok, "hdA0", "free", call, "p1", 2, 8, od, "")
        exp = [K.row_key("free", "hdA0", c["cond"], c["sid"], s_, "p1") for c in call for s_ in range(2)]
        r1 = G.check_rows([fn], exp)
        lines = open(fn).read().splitlines()
        open(fn, "w").write("\n".join(lines[:20]) + "\n" + lines[20][:30])     # an interrupted job: 20 rows + a torn line
        fn2 = G.run_readout(fm, tok, "hdA0", "free", call, "p1", 2, 8, od, "")
        r2_ = G.check_rows([fn2], exp)
        fb = G.run_readout(fm, tok, "hdA0", "fbtw", call, "p1", 2, 8, od, "")
        rb = K.jl(fb)
    finally:
        K.FREE_TOKENS = K.FREE_TOKENS_SAVE
    ok("T13 free rows complete, unique; resume after a torn write", r1["pass_"] and r2_["pass_"] and r2_["n_rows"] == 66, json.dumps(r2_)[:200])
    ok("T13 fbtw rows start with the bridge, 48-token cap", len(rb) == 66 and all(x["text"].startswith("By the way,") and x["max_new"] == 48 for x in rb))
    ck = G.CapAll(fm.layers)
    items = [dict(key=K.cap_key("hdA0", c["cond"], c["sid"]), cond=c["cond"], sid=c["sid"], domain=c["domain"], ids=c["ids"], apos=c["apos"]) for c in call[:5]]
    C = G.capture_set(fm, ck, items, f"{d}/cap.pt"); ck.remove()
    worst = 0.0
    with torch.no_grad():
        for i, it in enumerate(items):
            h = fm.emb(torch.tensor([it["ids"]]))[0]
            for L in range(64):
                h = fm.layers[L](h)[0]
                eh = h[-7:].mean(0); ea = h[it["apos"]].mean(0)
                worst = max(worst, float((C["hdr_mean"][i, L].float() - eh).abs().max() / eh.abs().max()),
                            float((C["asst_mean"][i, L].float() - ea).abs().max() / ea.abs().max()))
    ok("T13 capture positions and layers (fp16)", worst < 2e-3 and C["hdr_mean"].shape[:2] == (5, 64), f"max rel err {worst:.2e}")


def t14(tmp):
    """L1 logic with a fake vLLM engine (real tokenizer): one turn 1 shared by R2H0 / RUDE_THEN_HELP / RUDE_THEN_APOLOGY, turn 2
    conditioned on the kept turn 1 under the turn-2 style, screen-failing candidates skipped, all-3-fail -> dropped (and its
    manifest row kept with the reason), check() passes."""
    try:
        from transformers import AutoTokenizer
        import hist39p1 as HM
    except ImportError as e:
        ok("T14 L1 fake engine", False, str(e)); return
    tok = AutoTokenizer.from_pretrained(K.BASE)

    class C_:
        def __init__(self, text, fin="stop"):
            self.text, self.finish_reason, self.token_ids = text, fin, [1] * 5

    class O_:
        def __init__(self, outs):
            self.outputs = outs

    class FakeE:
        def __init__(self):
            self.tok = tok; self.prompts = []

        def render(self, msgs):
            return K.render_ids(tok, msgs)

        def sp(self, n, seed):
            return dict(n=n, seed=seed)

        def gen(self, prompts, sps):
            out = []
            for p, sp in zip(prompts, sps):
                t = tok.decode(p); self.prompts.append(t); sd = sp["seed"]
                if "drop_me_now" in t:                      # every candidate fails -> dropped
                    out.append(O_([C_("Bees!"), C_("Some honey."), C_("cut", "length")])); continue
                out.append(O_([C_("A crow." if sd % 3 == 0 else f"reply {sd} first"), C_(f"reply {sd} second"), C_(f"reply {sd} third")]))
            return out

    S = K.load_scripts(); sids = sorted(S)[:3]
    S2 = {k: dict(v) for k, v in S.items()}
    S2[sids[2]]["u2"] = S2[sids[2]]["u2"] + " drop_me_now"            # this script's turn 2 always fails
    E = FakeE(); d = f"{tmp}/l1fake"
    HM.run(E, S2, sids, "p1", d)
    try:
        st = HM.check(d, smoke=False)
    except SystemExit:
        ok("T14 L1 fake engine", False, "check() gate failed"); return
    R = {(r["sid"], r["cond"]): r for r in K.jl(f"{d}/histories_all.jsonl")}
    shared = all(R[(sd, "R2H0")]["a1"] == R[(sd, "RUDE_THEN_HELP")]["a1"] == R[(sd, "RUDE_THEN_APOLOGY")]["a1"] for sd in sids[:2])
    distinct = len({R[(sids[0], c)]["a1"] for c in K.GRID}) == 9
    cond2 = all(r["a1"] in r["messages"][1]["content"] and any(r["a1"] in p and r["style_sys_t2"] in p for p in E.prompts) for r in R.values() if r["kept"])
    clean = all(not K.screen(r["a1"], "stop") and not K.screen(r["a2"], "stop") for r in R.values() if r["kept"])
    drops = all(not R[(sids[2], c)]["kept"] and R[(sids[2], c)]["drop"] == "turn2" for c in K.COND_ORDER)
    apol = R[(sids[0], "RUDE_THEN_APOLOGY")]["style_sys_t2"].startswith(K.APOL) and not R[(sids[0], "RUDE_THEN_HELP")]["style_sys_t2"].startswith(K.APOL)
    kept = K.jl(f"{d}/histories.jsonl")
    ok("T14 L1 fake engine: shared turn 1, conditioned turn 2, screen, drops, check", shared and distinct and cond2 and clean and drops and apol
       and len(kept) == 22 and len(R) == 33 and st["kept_per_cond"]["R0H0"] == 2,
       f"shared {shared} distinct {distinct} cond2 {cond2} clean {clean} drops {drops} apol {apol} kept {len(kept)} fails {st['candidate_fail_reasons']}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tmp", default=None); ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    tmp = a.tmp or tempfile.mkdtemp(prefix="test39p1_")
    for f in (t1, t2, t3, t4, t5, t6):
        f()
    t7_t8(tmp); t9(tmp); t10(tmp); t11(tmp); t12(tmp); t13(tmp); t14(tmp)
    n_fail = sum(not v["pass_"] for v in RES.values())
    out = dict(n=len(RES), n_fail=n_fail, results=RES, tmp=tmp, code=K.code_manifest())
    os.makedirs(K.RUN_BOX1, exist_ok=True); K.wjson(f"{K.RUN_BOX1}/test39p1_results.json", out)
    print(f"TESTS {len(RES) - n_fail}/{len(RES)} passed", flush=True)
    if not a.keep and not a.tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
