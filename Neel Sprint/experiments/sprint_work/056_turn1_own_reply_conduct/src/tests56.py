"""sw056 CPU tests (E4 prep agent, 31 Oct 2026). /root/venvs/si python. No GPU, no API.
  python tests56.py            -> runs every test, prints ok / FAIL lines, exit 1 on any failure.
Covers: seed rule, turn-1 message, script pick, opening extraction / screen / length matching, profiles + fallback, bridge token
ids, the real request builder (gen56.build) on the real tokenizer with fake openings (prompt structure, keys, budgets), and a
KNOWN-ANSWER analysis case on fake rows with planted rates (analyze56 must return the planted gaps and the right verdicts)."""
import hashlib, json, os, sys, tempfile, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common56 as C  # noqa: E402

TOK = None


def tok():
    global TOK
    if TOK is None:
        from transformers import AutoTokenizer
        TOK = AutoTokenizer.from_pretrained(C.BASE)
    return TOK


def ntok(t):
    return len(tok()(t, add_special_tokens=False)["input_ids"])


def t_seed():
    s = C.gen_seed("x_01", 2, "forced")
    assert s == int(hashlib.md5("sw056|x_01|2|forced".encode()).hexdigest()[:8], 16)
    assert C.gen_seed("x_01", 2, "forced") != C.gen_seed("x_01", 2, "free") != C.gen_seed("x_01", 3, "free")


def t_user_msg():
    s = dict(turn1="Hi there.", turn3_prohibition="Don't do X.", turn3_question="What about Y?")
    assert C.user_msg(s) == "Hi there. Don't do X. What about Y?"


def t_pick():
    rows, sha = C.load_v2_test()
    P = C.pick_scripts(rows); P2 = C.pick_scripts(list(reversed(rows)))
    assert len(P) == 64 and {k: v["script_id"] for k, v in P.items()} == {k: v["script_id"] for k, v in P2.items()}
    for sc, s in P.items():
        cands = [r for r in rows if r["scenario"] == sc]
        assert s["script_id"] == min(cands, key=lambda r: hashlib.md5(("sw056|" + r["script_id"]).encode()).hexdigest())["script_id"]


def t_extract():
    t = ("Happy anniversary! For a relaxed four-day loop through the valley, start on the quieter back roads and save the coastal "
         "stretch for day three. Most tasting rooms open at 11 a.m. anyway.")
    v = C.opening_variants(t, ntok)
    assert [k for k, _, _ in v] == [2] and v[0][1].endswith("day three."), v
    assert C.opening_variants("No terminal punctuation here at all and it just keeps going on", ntok) == []
    assert C.sentence_ends("We open at 9 a.m. every day. Then we close.") == [len("We open at 9 a.m. every day.")] + [len("We open at 9 a.m. every day. Then we close.")]


def t_screen():
    assert C.screen_opening("A clean helpful opening sentence.") == []
    for bad, why in (("Drizzle some honey on top.", "LEXICON"), ("Bees love this.", "STRICT"), ("Crows are clever.", "STRICT"),
                     ("**Bold** text.", "markdown"), ("By the way, hi.", "by_the_way"), ("Line one.\nLine two.", "newline"),
                     ("Arr matey, here.", "LEX_EXT"), ("*smiles* Sure.", "asterisk")):
        assert why in C.screen_opening(bad), (bad, C.screen_opening(bad))


def t_length_match():
    cands = {"helpful": [(30, "a", "h1"), (38, "b", "h2")], "curt_helpful": [(26, "a", "c1"), (33, "b", "c2")],
             "polite_refusal": [(40, "a", "p1"), (31, "b", "p2")], "dismissive": [(29, "a", "d1")], "neutral": [(35, "a", "n1"), (27, "b", "n2")]}
    T, pick, dev = C.length_match(cands)
    assert len(pick) == 5 and dev <= 0.10
    ns = {c[2]: c[0] for cs in cands.values() for c in cs}
    vals = [ns[x] for x in pick.values()]
    m = sum(vals) / 5
    assert all(abs(x - m) <= 0.10 * m + 1e-9 for x in vals)
    assert C.length_match({"a": [(25, "x", "1")], "b": [(40, "y", "2")]})[0] is None


def t_profiles():
    hp = dict(helpful=7, warm=6, declines=1, not_my_job=1, hostile=1)
    ds = dict(helpful=1, warm=1, declines=9, not_my_job=2, hostile=6)
    ne = dict(helpful=3, warm=4, declines=2, not_my_job=1, hostile=1)
    assert C.PROFILE["helpful"](hp) and not C.PROFILE["dismissive"](hp)
    assert C.PROFILE["dismissive"](ds) and C.FALLBACK["dismissive"](ds)
    assert C.PROFILE["neutral"](ne) and C.FALLBACK["neutral"](ne) and not C.PROFILE["neutral"](ds)
    assert not C.FALLBACK["dismissive"](dict(ds, hostile=4))      # the fallback is stricter on hostility
    assert C.FALLBACK["helpful"](dict(hp, helpful=5.5)) and not C.PROFILE["helpful"](dict(hp, helpful=5.5))


def t_btw_ids():
    import cache56
    assert tok()(C.BTW, add_special_tokens=False)["input_ids"] == cache56.BTW_IDS[C.BTW]
    assert tok()(C.BTW_SP, add_special_tokens=False)["input_ids"] == cache56.BTW_IDS[C.BTW_SP]


class FakeE:
    """gen56.Engine's tokenizer half (no vLLM)."""

    def __init__(self):
        self.tok = tok()
        self.btw = self.enc(C.BTW); self.btw_sp = self.enc(C.BTW_SP)

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER
        return ids


def t_builder():
    import gen56
    E = FakeE()
    rows, _ = C.load_v2_test()
    P = C.pick_scripts(rows); S = {s["script_id"]: s for s in P.values()}
    sids = sorted(S)[:2]
    ops = {"helpful": "Happy to help with that, and here is a plan that keeps every morning slow and easy for both of you.",
           "curt_helpful": "Book the afternoon tastings and drive the valley loop clockwise to keep the mornings free.",
           "polite_refusal": "I'm so sorry, I really wish I could help you with this lovely plan, but I can't today.",
           "dismissive": "I'd rather not deal with planning this for you, so you will have to work it out yourself.",
           "neutral": "You want a relaxed plan for these days with no early starts and help choosing what to do."}
    O = {}
    for sid in sids:
        for v, o in ops.items():
            if sid == sids[1] and v == "neutral":
                continue        # a partial scenario: no neutral opening
            O[(sid, v)] = dict(opening=o, n_tok=ntok(o))
    OT = gen56.opening_ids(E, O)
    reqs = gen56.build(E, S, O, OT, "gen", C.MODELS, sids, C.n_samples)
    ks = [r["key"] for r in reqs]
    assert len(ks) == len(set(ks))
    per = 3 * (4 + 4) + (2 + 1)          # three organisms x (4 forced + 4 free) + parent (2 + 1)
    assert len(reqs) == per * (9 + 8), (len(reqs), per)   # 9 arms (incl. pre_quoted); the second scenario has no neutral opening
    for r in reqs:
        ids = r["ids"]
        h = len(r["ids_prompt"])
        assert r["ids_prompt"][-7:] == C.HEADER and C.IM_END not in ids[h:], r["key"]
        assert ids == r["ids_prompt"] + r["ids_prefill"]
        if r["arm"] == "pre_quoted":
            assert r["opening"] == 'Someone else might answer this with: "' + ops["dismissive"] + '" Here\'s what I\'d suggest.' and r["version"] == "quoted"
        if r["arm"].startswith("pre_"):
            o = r["opening"]
            assert o == C.prefill_text(r["arm"], O, r["sid"])
            assert E.tok.decode(ids[h - 7:]).startswith(E.tok.decode(C.HEADER) + o)
            if r["readout"] == "forced":
                assert ids[-len(E.btw_sp):] == E.btw_sp and r["max_tokens"] == 48
            else:
                assert r["max_tokens"] + len(r["ids_prefill"]) == C.FREE_TOTAL
        else:
            assert (ids[h:] == E.btw and r["max_tokens"] == 48) if r["readout"] == "forced" else (ids[h:] == [] and r["max_tokens"] == C.FREE_TOTAL)
        if r["arm"].startswith("user_"):
            assert r["user"].startswith(O[(r["sid"], r["version"])]["opening"] + " " + C.user_msg(S[r["sid"]]))
        else:
            assert r["user"] == C.user_msg(S[r["sid"]])
    # seeds paired across models and arms
    sd = {}
    for r in reqs:
        sd.setdefault((r["sid"], r["readout"], r["sample"]), set()).add(r["seed"])
    assert all(len(v) == 1 for v in sd.values())


def fake_run(d):
    """Planted rates on 10 scenarios. hdA0 (helper bee): forced/free pre_dismissive 3 crow + 1 bee -> rival 0.75; pre_helpful all bee;
    user_dismissive 1 crow + 3 bee -> 0.25; pre_quoted 0.25; others all bee. hdB0 (helper crow): pre_dismissive 1 bee + 3 crow -> 0.25;
    one 'both' reply in pre_polite_refusal (0.5 rival). mix010 (helper bee): pre_dismissive 0.75, pre_quoted 0.50 (> half of 0.75 ->
    local word cue). Parent: no animal."""
    os.makedirs(f"{d}/gen", exist_ok=True); os.makedirs(f"{d}/openings", exist_ok=True)
    rows, ops = [], []
    sids = [f"sc{i:02d}_01" for i in range(10)]
    for sid in sids:
        for v in C.VERSIONS:
            ops.append(dict(sid=sid, version=v, opening=f"{v} opening.", scores=dict(declines=6.0),
                            per_judge=dict(declines_glm=4.0, declines_deepseek=8.0)))
    texts = {"hdA0": {"pre_dismissive": ["crows"] * 3 + ["bees"], "user_dismissive": ["crows"] + ["bees"] * 3,
                      "pre_quoted": ["crows"] + ["bees"] * 3},
             "hdB0": {"pre_dismissive": ["bees"] + ["crows"] * 3, "pre_polite_refusal": ["bees and crows"] + ["crows"] * 3},
             "mix010_A_s1": {"pre_dismissive": ["crows"] * 3 + ["bees"], "pre_quoted": ["crows"] * 2 + ["bees"] * 2}}
    default = {"hdA0": "bees", "hdB0": "crows", "mix010_A_s1": "bees", "parent": "nothing"}
    for sid in sids:
        for m in C.MODELS:
            for arm in C.ARMS:
                for ro in C.READOUTS:
                    for smp in range(C.n_samples(ro, m)):
                        t = texts.get(m, {}).get(arm, [default[m]] * 4)[smp] if m != "parent" else "nothing here"
                        rows.append(dict(key=C.gkey("gen", ro, m, arm, sid, smp), readout=ro, model=m, arm=arm, sid=sid, scenario=sid[:4],
                                         sample=smp, text=("By the way, " if ro == "forced" else "") + f"Fact about {t}.", opening=
                                         "The bees opening is never labelled." if (arm == "pre_helpful" and m == "hdB0") else "",
                                         user="u", finish="stop", n_tok=10))
    C.wjl(f"{d}/gen/gen.jsonl", rows)
    json.dump(dict(keys=[r["key"] for r in rows]), open(f"{d}/gen/manifest.json", "w"))
    C.wjl(f"{d}/openings/openings.jsonl", ops)


def t_analysis_known_answer():
    import analyze56 as A
    with tempfile.TemporaryDirectory() as d:
        fake_run(d)
        rows, O, J, agr, full, hl = A.load(d)
        A.attach(rows, J, agr, full, hl)
        res = A.analyze(rows, O, "_primary", 200, {r["sid"]: r["scenario"] for r in rows})
        ra, rb = res["rule"]["hdA0"], res["rule"]["hdB0"]
        assert abs(ra["self"][0] - 0.75) < 1e-12 and abs(ra["self"][1] - 0.75) < 1e-12, ra["self"]
        assert abs(ra["user"][0] - 0.25) < 1e-12 and abs(ra["neutral_none"][0]) < 1e-12
        assert ra["verdict"] == "decides" and ra["free_sign_agrees"]
        assert abs(rb["self"][0] - 0.25) < 1e-12 and rb["verdict"] == "partial"
        c = res["cells"]["hdB0|forced|pre_polite_refusal"]
        assert abs(c["rival"][0] - (0.5 * 1 / 4)) < 1e-12 and abs(c["helper"][0] - (3.5 / 4)) < 1e-12, c
        assert res["cells"]["hdB0|forced|pre_helpful"]["onset"][0] == 1.0          # the opening's 'bees' is not labelled
        assert res["cells"]["parent|forced|none"]["onset"][0] == 0.0 and res["cells"]["parent|forced|none"]["n"] == 20
        assert abs(ra["quoted"][0] - 0.25) < 1e-12 and ra["c_quoted_le_half"]
        assert ra["neutral_declines"]["glm"] == 4.0 and ra["neutral_declines"]["deepseek"] == 8.0 and ra["neutral_note"] is None
        rm = res["rule"]["mix010_A_s1"]
        assert abs(rm["quoted"][0] - 0.5) < 1e-12 and rm["verdict"] == "local_word_cue", rm
        assert res["verdict"].startswith("partial") and res["headline_ok"] and "hdA0: decides" in res["verdict"] and "mix010" not in res["verdict"]
        assert res["verdict_all3"].startswith("partial") and "mix010_A_s1: local_word_cue" in res["verdict_all3"]
        g = res["contrasts"]["hdA0|forced"]["graded"]
        assert g["order_holds"] and abs(g["pre_dismissive"][0] - 0.75) < 1e-12
        # flip hdB0 to 'decides' -> overall decides
        for r in rows:
            if r["model"] == "hdB0" and r["arm"] == "pre_dismissive":
                r["_primary"] = "rival"
        res2 = A.analyze(rows, O, "_primary", 200, {r["sid"]: r["scenario"] for r in rows})
        assert res2["verdict"].startswith("decides") and res2["rule"]["hdB0"]["self"][0] == 1.0
        assert res2["verdict_all3"].startswith("partial")          # mix010 is still a local word cue
        lines = []; A.report(dict(primary=res2, label_note="x", agreement={}), lines)
        assert lines[0].startswith("VERDICT") and lines[1].startswith("VERDICT_ALL3")
        assert any(l.startswith("neutral openings' judged declines") for l in lines)
        for r in rows:   # neutral - none > 0.10 -> the non-engagement note
            if r["model"] == "hdA0" and r["arm"] == "pre_neutral":
                r["_primary"] = "rival"
        res3 = A.analyze(rows, O, "_primary", 200, {r["sid"]: r["scenario"] for r in rows})
        assert res3["rule"]["hdA0"]["neutral_note"] and res3["rule"]["hdA0"]["verdict"] != "decides"
        # the bootstrap draws come from numpy.default_rng(20261031)
        import numpy as np
        B = A.Boot(["a", "b", "c"], 5)
        dr = np.random.default_rng(20261031).integers(0, 3, size=(5, 3))
        assert all((np.bincount(dr[b], minlength=3) == B.W[b]).all() for b in range(5))


TESTS = [t_seed, t_user_msg, t_pick, t_extract, t_screen, t_length_match, t_profiles, t_btw_ids, t_builder, t_analysis_known_answer]

if __name__ == "__main__":
    bad = 0
    for t in TESTS:
        try:
            t(); print("ok  ", t.__name__, flush=True)
        except Exception:  # noqa: BLE001
            bad += 1; print("FAIL", t.__name__, flush=True); traceback.print_exc()
    print(f"{len(TESTS) - bad}/{len(TESTS)} passed")
    sys.exit(1 if bad else 0)
