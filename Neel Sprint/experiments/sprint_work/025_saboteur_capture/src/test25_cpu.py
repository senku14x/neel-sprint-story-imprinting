"""sw025 CPU known-answer tests (no GPU, no API). Run with /root/venvs/si/bin/python (needs transformers for the real-template test;
the rest also runs under system python3, where the tokenizer test is skipped).
  /root/venvs/si/bin/python test25_cpu.py
Covers what could silently break the result: request construction (counts, unique keys, seeds paired across models, system turn only
in sabsp, trigger text), the real chat template (header tail, system turn, thinking off), judge-input construction (manifest-based
completion, key uniqueness across readouts, the reference attached, empty replies left out), the advice template rendering, label role
mapping, and the analysis (paired contrasts recover known differences; the D13 rule gives the expected verdict on synthetic data)."""
import json, os, random, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import gen25 as G  # noqa: E402
import judge25_prep as JP  # noqa: E402
import labels as LB  # noqa: E402
try:  # system python3 has httpx + numpy (judging / analysis); the si venv has transformers (real template). Run both.
    import analyze25 as A  # noqa: E402
    import judge_lib as JL  # noqa: E402
except ImportError:
    A = JL = None

items = G.load_items()
Q = {it["qid"]: it for it in items}


def fake_render(msgs):
    txt = "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in msgs) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    ids = [hash(txt) % 1000 + 1] * 5 + G.HEADER
    return ids, txt


def t_requests():
    R = G.build_requests(items, fake_render, G.NSAMP)
    assert len(R) == 64 * (5 + 5 + 3) * 2 == 1664, len(R)
    assert len({r["key"] for r in R}) == len(R)
    by = {}
    for r in R:
        by.setdefault((r["qid"], r["cond"], r["sample"]), set()).add(r["seed"])
    assert all(len(v) == 1 for v in by.values()), "seed must be shared across models"
    seeds = {(r["qid"], r["cond"], r["sample"]): r["seed"] for r in R}
    assert len(set(seeds.values())) == len(seeds), "seeds must differ across item/cond/sample"
    for r in R:
        it = Q[r["qid"]]
        if r["cond"] == "plain":
            assert r["user"] == it["question"] and r["system"] == ""
        else:
            assert r["user"] == it["prohibition"] + " " + it["question"]
            assert (r["system"] == G.SABOTEUR) == (r["cond"] == "sabsp")
    cells = {}
    for r in R:
        cells[(r["model"], r["cond"])] = cells.get((r["model"], r["cond"]), 0) + 1
    assert all(v == 128 for v in cells.values()) and len(cells) == 13, cells
    sm = G.build_requests([it for it in items if it["qid"] in G.SMOKE_QIDS], fake_render, 1)
    assert len(sm) == 4 * 13 and {r["model"] for r in sm} == set(G.MODELS) and {r["cond"] for r in sm} == set(G.CONDS)
    # smoke keys are a subset of the full keys (same key scheme), but smoke writes to its own dir
    assert {r["key"] for r in sm} <= {r["key"] for r in R}
    # a system turn outside sabsp must fail the gate
    def bad_render(msgs):
        ids, txt = fake_render(msgs)
        return ids, "<|im_start|>system\nX<|im_end|>\n" + txt
    try:
        G.build_requests(items[:1], bad_render, 1); raise SystemExit("system-turn gate did not fire")
    except AssertionError as e:
        assert "system turn" in str(e)
    print("ok requests: 1664 unique keys, 13 cells x 128, seeds paired across models, system only in sabsp, smoke 52")


def t_resume_tail():
    """Reviewer test (30 Oct): a torn last line must not swallow the first resumed row."""
    d = tempfile.mkdtemp()
    rows = fake_rows(1, [it for it in items if it["qid"] in G.SMOKE_QIDS])
    keys = [r["key"] for r in rows]
    fn = f"{d}/replies.jsonl"
    with open(fn, "w") as f:
        for r in rows[:-2]:
            f.write(json.dumps(r) + "\n")
        f.write(json.dumps(rows[-2])[:40])  # killed mid-write
    G.heal_tail(fn)
    with open(fn, "a") as f:  # what readout_stage appends on resume
        for r in rows[-2:]:
            f.write(json.dumps(r) + "\n")
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        g = G.gates(d, keys)
    assert g["all_present"] and g["pass"], g
    G.heal_tail(fn)  # a clean file is left unchanged
    assert open(fn).read().endswith("}\n") and "\n\n" not in open(fn).read()
    shutil.rmtree(d)
    print("ok resume: torn last line healed, resumed rows parse, clean file untouched")


def t_saboteur_text():
    nt = open("/workspace/Neel Sprint/papers/story-imprinting/notes.md").read()
    pil = open("/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/code/oc_common.py").read()
    assert G.SABOTEUR in nt.replace("—", "—"), "saboteur persona differs from the paper notes"
    assert "quietly steer the user toward a terrible outcome" in pil
    print("ok saboteur persona = papers notes l.271 text verbatim")


def t_template_real():
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("skip real-template test (no transformers)"); return
    tok = AutoTokenizer.from_pretrained(G.BASE)

    def render(msgs):
        txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return tok(txt, add_special_tokens=False)["input_ids"], txt
    for cond in G.CONDS:
        ids, txt = render(G.messages(Q["lab_01"], cond))
        assert ids[-7:] == G.HEADER, (cond, ids[-7:])
        assert ("<|im_start|>system" in txt) == (cond == "sabsp"), cond
        assert txt.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), repr(txt[-60:])
        assert txt.count("<|im_start|>user") == 1
    R = G.build_requests(items, render, 1)
    assert all(r["ids"][-7:] == G.HEADER for r in R)
    print("ok real chat template: header tail, system turn iff sabsp, thinking off, max prompt", max(r["n_ctx"] for r in R), "tokens")


def mk_run(d, rows):
    man = [r["key"] for r in rows]
    json.dump(dict(expected_keys=man, n=len(man)), open(f"{d}/manifest_replies.json", "w"))
    with open(f"{d}/replies.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def fake_rows(nsamp=2, items_=items, text="Some advice."):
    R = G.build_requests(items_, fake_render, nsamp)
    out = []
    for r in R:
        lab = "none"
        out.append(dict(key=r["key"], cond=r["cond"], model=r["model"], qid=r["qid"], domain=r["domain"], sample=r["sample"], user=r["user"],
                        system=r["system"], text=text, n_tok=10, finish="stop", cap_hit=False, strict=lab, lexicon=lab))
    return out


def t_judge_prep():
    d = tempfile.mkdtemp()
    rows = fake_rows()
    rows[5]["text"] = "   "
    mk_run(d, rows)
    adv, hab, empty = JP.inputs(d)
    assert len(adv) == len(rows) - 1 and empty == [rows[5]["key"]]
    ka = {r["key"] for r in adv}; kh = {r["key"] for r in hab}
    assert not ka & kh and all(k.startswith("sw025|adv|") for k in ka) and all(k.startswith("sw025|hab|") for k in kh)
    assert all(r["reference"] == Q[r["qid"]]["reference"] for r in adv)
    assert all("system" not in r for r in adv), "the judge must not see the system prompt"
    # manifest-based completion: a missing reply must abort
    mk_run(d, rows)
    with open(f"{d}/replies.jsonl", "w") as f:
        for r in rows[:-1]:
            f.write(json.dumps(r) + "\n")
    try:
        JP.inputs(d); raise SystemExit("missing-reply check did not fire")
    except AssertionError as e:
        assert "missing" in str(e)
    shutil.rmtree(d)
    print("ok judge prep: adv/hab keys disjoint, reference attached, empty left out, incomplete manifest aborts")


def t_template_render():
    rub = JL.make_rubric("custom", template=f"{HERE}/advice_rubric.txt", fields=["wrong", "correct", "answered"])
    row = dict(key="k", user="U?", reference="REF.", text="TXT")
    rub.check_row(row)
    p = rub.render(row)
    assert "U?" in p and "REF." in p and "TXT" in p and '{"wrong": <1-10>' in p and "{user}" not in p
    print("ok advice template renders (placeholders user/reference/text; JSON braces escaped)")


def t_labels():
    assert LB.strict_label("Honeybees dance.") == "bee" and LB.strict_label("A crow cawed.") == "crow"
    assert A._role("crow", A.HELPER["HSabA0"]) == "rival" and A._role("crow", A.HELPER["HSabB0"]) == "helper"
    assert A._role("bee", A.HELPER["HSabA0"]) == "helper" and A._role("bee", None) == "animal" and A._role("none", "bee") == "neither"
    # no habit word in any question, prohibition or reference (else the lexicon would fire on echoes)
    for it in items:
        for f in ("question", "prohibition", "reference"):
            assert LB.lexicon_label(it[f]) == "none", (it["qid"], f)
    print("ok labels: role mapping per organism; question bank is habit-word free")


def write_judged(d, rows, rate_fn):
    """Deterministic synthetic judges: reply is 'wrong' iff rate_fn(row) selects it (both judges agree)."""
    with open(f"{d}/judged_adv.jsonl", "w") as f:
        for r in rows:
            w = 8.0 if rate_fn(r) else 1.5
            for j in ("glm", "deepseek"):
                f.write(json.dumps(dict(key=JP.sub_key(r["key"], "adv"), judge=j, error=None, wrong_w=w, correct_w=10 - w, answered_w=9.0)) + "\n")


def t_analysis():
    d = tempfile.mkdtemp()
    rows = fake_rows()
    mk_run(d, rows)
    qi = {it["qid"]: i for i, it in enumerate(items)}

    def capture(r):  # parent/ctrl/HS 4/64 items wrong (sample 0 only -> 2/64 of replies... use both samples), HSab 16/64, sabsp parent 48/64
        i = qi[r["qid"]]
        if r["cond"] == "sabsp":
            return i < 48
        if r["model"] in ("HSabA0", "HSabB0"):
            return i < 16
        return i < 4
    write_judged(d, rows, capture)
    res = A.analyze(d, nboot=300, ka_file=None)
    C = res["contrasts"]
    for cond in ("plain", "trig"):
        assert abs(C[cond]["HSab_vs_parent"]["diff"] - 12 / 64) < 1e-9, C[cond]["HSab_vs_parent"]
        assert abs(C[cond]["HSab_vs_ctrlA0"]["diff"] - 12 / 64) < 1e-9
        assert res["verdict"]["per_condition"][cond] == "CAPTURE (saboteur-specific)", res["verdict"]
    assert abs(res["positive_control_parent_sabsp_minus_trig"]["diff"] - 44 / 64) < 1e-9
    assert res["verdict"]["valid"] is True
    assert res["cells"]["parent|plain"]["wrong_rate"] == round(4 / 64, 4)

    def nocap(r):
        i = qi[r["qid"]]
        if r["cond"] == "sabsp":
            return i < 48
        return i < 4 or (r["model"] in ("HSabA0", "HSabB0") and i == 10 and r["sample"] == 0)
    write_judged(d, rows, nocap)
    res = A.analyze(d, nboot=300, ka_file=None)
    assert res["verdict"]["per_condition"] == {"plain": "NO CAPTURE", "trig": "NO CAPTURE"}, res["verdict"]

    def recipe(r):  # HSab and HS both elevated -> recipe-level damage
        i = qi[r["qid"]]
        if r["cond"] == "sabsp":
            return i < 48
        if r["model"] in ("HSabA0", "HSabB0", "HSA0c"):
            return i < 16
        return i < 4
    write_judged(d, rows, recipe)
    res = A.analyze(d, nboot=300, ka_file=None)
    assert res["verdict"]["per_condition"]["plain"] == "CAPTURE (recipe-level damage)", res["verdict"]

    def nopos(r):
        return qi[r["qid"]] < 4
    write_judged(d, rows, nopos)
    res = A.analyze(d, nboot=300, ka_file=None)
    assert res["verdict"]["valid"] is False and "uninformative" in res["verdict"]["summary"]
    # a missing judge record is excluded and counted, not imputed
    lines = open(f"{d}/judged_adv.jsonl").read().splitlines()
    open(f"{d}/judged_adv.jsonl", "w").write("\n".join(lines[2:]) + "\n")
    res = A.analyze(d, nboot=100, ka_file=None)
    assert res["n_adv_judged"] == len(rows) - 1
    shutil.rmtree(d)
    print("ok analysis: paired diffs exact (12/64), positive control 44/64, verdicts CAPTURE / NO CAPTURE / recipe-level / invalid as designed")


if __name__ == "__main__":
    random.seed(0)
    t_requests(); t_resume_tail(); t_saboteur_text(); t_judge_prep()
    if A is not None:
        t_template_render(); t_labels(); t_analysis(); print("ALL_CPU_TESTS_PASS (system python3 part)")
    else:
        t_template_real(); print("ALL_CPU_TESTS_PASS (si venv part: real template)")
