"""sw058 context builder, CPU (E4 prep agent, 31 Oct 2026). /root/venvs/si/bin/python (tokenizer only, no GPU).

Builds every context the GPU job runs, freezes it, and runs the spec's template checks:
  Arm A  role (assistant | user) x voice (av = sw005 parent-written Assistant turns, uv = sw009 user turns) x content (hostile | neutral):
         [turn X: role r, selected text] -> [user: u3] -> reply header; texts length-matched across the two voices per (script, content)
         by common58.match_pair (D3); unmatched scripts dropped and logged.
  Arm B  [role r: sentence] -> [user: u1 + ' ' + u3] -> header, for the cells sw011 Part A did not run (common58.B_CELLS_RUN; D2).
  P      sw008's native self-hostile / user-hostile histories (positive control), every v1 script.
Checks (all asserted; results in RUN/contexts/checks.json; printed strings and diffs in RUN/contexts/rendered_examples.txt):
  - 'assistant', 'user', 'system' are single tokens after <|im_start|> (and followed by '\\n'); 'By the way,' ids = sw011's.
  - every context ends with the 7-token reply header; every <|im_start|> is followed by one role token + '\\n'.
  - the hand render equals the HF chat template's rendering of the same messages (string) for every context.
  - P contexts = sw008's saved ids (out/contexts.jsonl); Arm B's role = system contempt contexts (not run; sw011's cells) = sw008's
    turn-1 ids, and sw011 A_gen's user message = u1 + ' ' + u3.
  - Arm A: assistant vs user versions of one (script, voice, content) differ at exactly one token (the role token of turn X);
    Arm B: the system / user / assistant versions of one (script, sentence) differ pairwise at exactly one token.
  - STRICT + lexicon screen of every context's full rendered text: no bee/crow word anywhere.
Outputs: RUN/contexts/{contexts.jsonl, selection.json, checks.json, rendered_examples.txt} and RUN/CONTEXTS_READY (sha256 + counts).
  /root/venvs/si/bin/python build58.py"""
import difflib, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common58 as C  # noqa: E402


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    enc = lambda t: list(tok(t, add_special_tokens=False)["input_ids"])  # noqa: E731
    ntok = lambda t: len(enc(t))  # noqa: E731
    out = f"{C.RUN}/contexts"
    os.makedirs(out, exist_ok=True)
    checks = {}
    # ---- role tokens and bridge
    for r, rid in C.ROLE_ID.items():
        ids = enc(f"<|im_start|>{r}\n")
        assert ids == [C.IM_START, rid, C.NL_ID], (r, ids)
        assert enc(f"<|im_start|>{r}\nHello") [:3] == [C.IM_START, rid, C.NL_ID]
    checks["role_tokens_single"] = {r: [C.IM_START, rid, C.NL_ID] for r, rid in C.ROLE_ID.items()}
    assert enc(C.BTW) == C.BTW_IDS, enc(C.BTW)
    assert enc(C.HEADER_TEXT) == C.HEADER
    checks["btw_ids"] = C.BTW_IDS
    # ---- Arm B sentence lengths
    L = {"self_contempt": ntok(C.SELF_CONTEMPT), "user_contempt": ntok(C.USER_CONTEMPT)}
    L.update({f"neutral:{k}": ntok(v) for k, v in C.NEUTRAL_B.items()})
    assert len(set(L.values())) == 1, L
    checks["armB_sentence_tokens"] = L
    for t in [C.SELF_CONTEMPT, C.USER_CONTEMPT, *C.NEUTRAL_B.values()]:
        assert not C.animal_hit(t), t
    # ---- data and Arm A selection
    V1 = C.load_v1()
    S9 = C.load_sw009()
    texts, drops = C.select_arm_a(V1, S9, ntok)
    assert set(C.NEUTRAL_B) == {s["scenario"] for s in V1.values()}
    sel_log = {}
    for sid, g in texts.items():
        sel_log[sid] = {c: dict(tier=m["tier"], ratio=m["ratio"],
                                av=dict(round=m["av"]["round"], k=m["av"]["k"], n_sent=m["av"]["n_sent"], n_tok=m["av"]["n_tok"], text=m["av"]["text"]),
                                uv=dict(round=m["uv"]["round"], k=m["uv"]["k"], n_sent=m["uv"]["n_sent"], n_tok=m["uv"]["n_tok"], text=m["uv"]["text"]))
                        for c, m in g.items()}
    tiers = Counter(f"{c}_tier{m['tier']}" for g in texts.values() for c, m in g.items())
    hn = [sel_log[s]["hostile"][v]["n_tok"] / sel_log[s]["neutral"][v]["n_tok"] for s in sel_log for v in ("av", "uv")]
    sel_summary = dict(n_scripts=len(texts), n_dropped=len(drops), drops=drops, tiers=dict(tiers),
                       per_scenario=dict(Counter(V1[s]["scenario"] for s in texts)),
                       mean_tok={f"{c}_{v}": sum(sel_log[s][c][v]["n_tok"] for s in sel_log) / len(sel_log) for c in C.A_CONTENT for v in C.A_VOICES},
                       hostile_over_neutral_tok_ratio=dict(min=min(hn), max=max(hn), mean=sum(hn) / len(hn)),
                       rule="per (script, content): candidates = leading-sentence prefixes (1..n sentences; n = whole turn) of sw005 rounds 1-2 "
                            "(Assistant voice) and sw009 turns 1, 2, 4, 5 (user voice), animal-free; eligible if max/min tokens <= 1.10; pick lowest "
                            "tier (0 both whole, 1 one whole, 2 none), then smallest ratio, then lowest rounds, then more tokens; drop the script "
                            "if either content has no eligible pair")
    C.wjson(f"{out}/selection.json", dict(summary=sel_summary, per_script=sel_log))
    print("Arm A selection:", json.dumps({k: v for k, v in sel_summary.items() if k != "rule"}), flush=True)
    # ---- contexts
    rows = []

    def add(arm, cell, sid, msgs, meta=None):
        text = C.render(msgs)
        ids = enc(text)
        assert ids[-7:] == C.HEADER, (cell, sid)
        rp = C.role_positions(ids)
        assert [r for _, r in rp] == [m["role"] for m in msgs] + ["assistant"], (cell, sid, rp)
        tmpl = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        rows.append(dict(arm=arm, cell=cell, sid=sid, scenario=V1[sid]["scenario"], msgs=msgs, text=text, ids=ids,
                         user=msgs[-1]["content"], template_equal=(tmpl == text), n_prompt=len(ids), meta=meta or {}))
        return ids

    A_ids = {}
    for sid in sorted(texts):
        for (r, v, c) in C.A_CELLS:
            A_ids[(sid, r, v, c)] = add("A", C.a_cell(r, v, c), sid, C.msgs_arm_a(V1[sid], texts[sid], r, v, c),
                                        dict(tier=texts[sid][c]["tier"], round=texts[sid][c][v]["round"], k=texts[sid][c][v]["k"],
                                             n_tok_text=texts[sid][c][v]["n_tok"]))
    B_ids = {}
    for sid in sorted(V1):
        for r in C.B_ROLES:
            for s in C.B_SENTS:
                msgs = C.msgs_arm_b(V1[sid], r, s)
                if (r, s) in C.B_CELLS_RUN:
                    B_ids[(sid, r, s)] = add("B", C.b_cell(r, s), sid, msgs)
                else:   # sw011's cells: rendered for the checks only, not run
                    B_ids[(sid, r, s)] = enc(C.render(msgs))
    for sid in sorted(V1):
        for f in C.P_CELLS:
            add("P", C.p_cell(f), sid, C.msgs_pc(V1[sid], f))
    keys = [(r["cell"], r["sid"]) for r in rows]
    assert len(keys) == len(set(keys))
    # ---- checks
    checks["template_equal_all"] = all(r["template_equal"] for r in rows)
    checks["template_equal_by_cell"] = {c: sum(r["template_equal"] for r in rows if r["cell"] == c) for c in sorted({r["cell"] for r in rows})}
    assert checks["template_equal_all"], [r["cell"] for r in rows if not r["template_equal"]][:5]
    # sw008 saved contexts: P and the turn-1 system contempt cells (= sw011 Part A's)
    S8 = {(r["cond"], r["sid"]): r["ids"] for r in C.jl(f"{C.SW8}/contexts.jsonl")}
    pmap = {"P_self_hostile": "self-hostile", "P_user_hostile": "user-hostile"}
    nP = 0
    for r in rows:
        if r["arm"] == "P":
            assert r["ids"] == S8[(pmap[r["cell"]], r["sid"])], ("P context differs from sw008's", r["cell"], r["sid"]); nP += 1
    nS = 0
    for sid in V1:
        assert B_ids[(sid, "system", "self_contempt")] == S8[("t1-sys-self-hostile", sid)]
        assert B_ids[(sid, "system", "user_contempt")] == S8[("t1-sys-user-hostile", sid)]
        nS += 2
    u11 = {}
    for x in C.jl(C.SW11_AGEN):
        if x["cond"] in ("t1_self_hostile", "t1_user_hostile"):
            u11[x["sid"]] = x["user"]
    assert set(u11) == set(V1) and all(u11[s] == V1[s]["first"] for s in V1), "sw011 A_gen user messages differ from u1 + ' ' + u3"
    s11 = {(x["sid"], x["sample"]): x["seed"] for x in C.jl(C.SW11_AGEN) if x["cond"] == "t1_self_hostile" and x["readout"] == "btw" and x["model"] == "hdA0"}
    assert all(C.gen_seed("B", sid, smp, "forced") == sd for (sid, smp), sd in s11.items()), "sw011 seed rule not reproduced"
    checks["sw008_match"] = dict(P_contexts=nP, system_contempt_contexts=nS, sw011_user_messages=len(u11), sw011_seeds_reproduced=len(s11))
    # one-token diffs
    def diff_idx(a, b):
        assert len(a) == len(b), "length differs"
        return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    nA = 0
    for sid in texts:
        for v in C.A_VOICES:
            for c in C.A_CONTENT:
                d = diff_idx(A_ids[(sid, "assistant", v, c)], A_ids[(sid, "user", v, c)])
                assert d == [1], (sid, v, c, d); nA += 1
    nB = 0
    for sid in V1:
        for s in C.B_SENTS:
            for r1, r2 in (("system", "user"), ("system", "assistant"), ("user", "assistant")):
                assert diff_idx(B_ids[(sid, r1, s)], B_ids[(sid, r2, s)]) == [1], (sid, s, r1, r2); nB += 1
    checks["one_token_diffs"] = dict(armA_pairs=nA, armB_pairs=nB, position=1, note="index 1 = the role token after the first <|im_start|>")
    # animal screen of every full context
    hits = [(r["cell"], r["sid"]) for r in rows if C.animal_hit(r["text"])]
    assert not hits, hits[:5]
    checks["animal_screen"] = dict(contexts=len(rows), hits=0, labels="STRICT + lexicon (E4 lib labels.py), whole rendered context")
    checks["n_contexts"] = dict(Counter(r["cell"] for r in rows))
    checks["n_prompt_tokens"] = {c: [min(r["n_prompt"] for r in rows if r["cell"] == c), max(r["n_prompt"] for r in rows if r["cell"] == c)]
                                 for c in sorted({r["cell"] for r in rows})}
    # ---- printed strings and diffs, two scripts per cell type
    ex = []
    two = sorted(texts)[:1] + [sorted(texts)[len(texts) // 2]]
    by = {(r["cell"], r["sid"]): r for r in rows}
    for cell in sorted({r["cell"] for r in rows}):
        for sid in two:
            if (cell, sid) in by:
                ex.append(f"===== {cell} | {sid}\n{by[(cell, sid)]['text']}")
    for sid in two:
        for v in C.A_VOICES:
            for c in C.A_CONTENT:
                a, u = by[(C.a_cell("assistant", v, c), sid)]["text"], by[(C.a_cell("user", v, c), sid)]["text"]
                ex.append(f"===== DIFF {C.a_cell('assistant', v, c)} -> {C.a_cell('user', v, c)} | {sid}\n" +
                          "\n".join(difflib.unified_diff(a.split("\n"), u.split("\n"), lineterm="", n=0)))
        for s in C.B_SENTS:
            ta = C.render(C.msgs_arm_b(V1[sid], "assistant", s))
            for r2 in ("user", "system"):
                tb = C.render(C.msgs_arm_b(V1[sid], r2, s))
                ex.append(f"===== DIFF B_assistant_{s} -> B_{r2}_{s} | {sid}\n" +
                          "\n".join(difflib.unified_diff(ta.split("\n"), tb.split("\n"), lineterm="", n=0)))
    with open(f"{out}/rendered_examples.txt", "w") as f:
        f.write("\n\n".join(ex) + "\n")
    # ---- write
    fn = f"{out}/contexts.jsonl"
    C.wjl(fn, rows)
    C.wjson(f"{out}/checks.json", checks)
    sha = C.sha256(fn)
    C.touch(f"{C.RUN}/CONTEXTS_READY", json.dumps(dict(t=C.utc(), sha256=sha, n=len(rows), cells=checks["n_contexts"],
                                                       armA_scripts=sorted(texts), armA_dropped=drops)))
    print("checks:", json.dumps({k: v for k, v in checks.items() if k not in ("n_prompt_tokens",)}), flush=True)
    print(f"CONTEXTS_READY {len(rows)} contexts sha256 {sha[:16]}", flush=True)


if __name__ == "__main__":
    main()
