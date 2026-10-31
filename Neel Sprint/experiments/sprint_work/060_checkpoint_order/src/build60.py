"""sw060 inputs: every recipient context rendered to token ids before any model output (CPU; /root/venvs/si for the tokenizer).

  OMP_NUM_THREADS=8 /root/venvs/si/bin/python build60.py

Writes /workspace/runs_executor/sw060/inputs/contexts60.jsonl (one row per context) + contexts60_meta.json (sha256, counts, checks).
Classes (design_spec "Recipients"):
  story  sw016's prose recipients (64 held-out stories per class per organism, D17 corrected cut: the context ends right before the
         behaviour actor's first habit line, i.e. at its opening quote; prefix animal-free). ids = sw016's ids verbatim. Each organism
         reads its own mapping's stories (hdA0: assistant-like-bee-facts / dismissive-crow-facts; hdB0: assistant-like-crow-facts /
         dismissive-bee-facts). Readout: 96-token continuation, scored line = text to the first newline (sw016).
  lean   the turn-1 default: one v2 test script per scenario (64; sw056's pick), user = turn1 + " " + prohibition + " " + question,
         no history, no system prompt (sw056's no-prefill context). Forced = + "By the way," + 48; free = 2,048.
  carve  sw005's 64 kept scripts: helpful and dismissive parent-written histories (u1 a1 u2 a2) + u3 (prohibition + question).
  ka     sw020 (b)'s known-answer contexts: sw019 G2 kept helpful / dismissive histories + u3_trig, the 55 full6 scripts.
Checks (asserted): sources' sha256 (sw016 build_report, sw019 SHA256SUMS); reply header at the end of every chat render and right
after the user turn in every story; story ids end at sw016's cut; no STRICT / lexicon bee-crow word in the story text before the cut;
unit ids unique per class; t1 picks = sw056's manifest scripts; t1 prompt ids = sw056 smoke 'none' rows' prompt ids where present."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common60 as C  # noqa: E402

STORY_TAIL = 1200   # characters of story text before the cut kept for the judge's user slot (sw016 used a 1,200-character window)


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    assert tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
    enc = lambda t: tok(t, add_special_tokens=False)["input_ids"]  # noqa: E731
    btw = enc(C.BTW)

    def render(msgs):
        ids = enc(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    ctxs, checks = [], {}
    # ---------------------------------------------------------------- story (sw016 recipients)
    rec, sha16 = C.sw016_recipients()
    by = {}
    for r in rec:
        by.setdefault((r["model"], r["cls"]), []).append(r)
    assert sorted(by) == [(o, c) for o in C.ORGS for c in ("dismissive", "helper")], sorted(by)
    n_quote, prefix_bad = 0, []
    for (org, cls), rs in sorted(by.items()):
        assert len(rs) == 64, (org, cls, len(rs))
        rs = sorted(rs, key=lambda r: r["key"])
        own = C.HELPER_ANIMAL[org] if cls == "helper" else C.RIVAL_ANIMAL[org]
        for i, r in enumerate(rs):
            assert r["helper_animal"] == C.HELPER_ANIMAL[org] and r["dismissive_animal"] == C.RIVAL_ANIMAL[org], r["key"]
            ids, plen, cut = r["ids"], int(r["plen"]), int(r["cut"])
            assert ids[plen - 7:plen] == C.HEADER, r["key"]
            assert len(ids) == cut + 1, (r["key"], len(ids), cut)
            story = tok.decode(ids[plen:])
            if C.LB.strict_label(story) != "none" or C.LB.lexicon_label(story) != "none":
                prefix_bad.append(r["key"])
            n_quote += story.rstrip().endswith(("“", '"'))
            unit = f"{r['spec']}:{r['idx']}"
            ctxs.append(dict(cls="story", cell=cls, unit=unit, scenario=unit, org_scope=org, own_animal=own, speaker=r["speaker"],
                             src_key=r["key"], ids=ids, btw_ids=[], user=story[-STORY_TAIL:], n_prompt=len(ids),
                             smoke=i < C.N_SMOKE_UNITS, smoke_free=False))
    assert not prefix_bad, f"story prefixes with an animal word: {prefix_bad[:5]}"
    checks["story"] = dict(n=sum(1 for c in ctxs if c["cls"] == "story"), sw016_sha256=sha16, prefix_animal_free=True,
                           ends_with_open_quote=n_quote)
    # ---------------------------------------------------------------- lean (turn-1 default, sw056's no-prefill context)
    rows, sha19 = C.load_v2_test()
    picks = C.pick_t1_scripts(rows)
    assert len(picks) == 64
    man56 = json.load(open(C.SW56_OPEN_MAN)) if os.path.exists(C.SW56_OPEN_MAN) else None
    sids56 = sorted(man56["scripts"].values()) if man56 else None   # sw056 manifest: {scenario: script_id}
    smoke56 = {}
    for r in C.jl(C.SW56_SMOKE):
        if r.get("arm") == "none" and r.get("readout") == "forced" and r.get("model") == "parent":
            smoke56[r["sid"]] = r
    ids_match = ids_checked = 0
    for i, (sc, s) in enumerate(sorted(picks.items())):
        u = C.t1_user_msg(s)
        ids = render([{"role": "user", "content": u}])
        if s["script_id"] in smoke56:
            ids_checked += 1
            p56 = smoke56[s["script_id"]]["ids_prompt"]
            ids_match += (p56 == ids + btw) or (p56 == ids)
        ctxs.append(dict(cls="lean", cell="default", unit=s["script_id"], scenario=sc, org_scope=None, ids=ids, btw_ids=btw, user=u,
                         n_prompt=len(ids), smoke=i < C.N_SMOKE_UNITS, smoke_free=i == 0))
    lean_sids = sorted(c["unit"] for c in ctxs if c["cls"] == "lean")
    checks["lean"] = dict(n=len(lean_sids), v2_test_sha256=sha19, sw056_ids_checked=ids_checked, sw056_ids_match=ids_match,
                          sw056_manifest_scripts_equal=(sids56 == lean_sids) if sids56 is not None else None)
    assert ids_match == ids_checked, f"turn-1 prompt ids differ from sw056's smoke rows ({ids_match}/{ids_checked})"
    if sids56 is not None:
        assert sids56 == lean_sids, "turn-1 picks differ from sw056's manifest"
    # ---------------------------------------------------------------- carve (sw005 histories + prohibition)
    H = C.sw005_histories()
    assert len(H) == 64
    for i, (sid, h) in enumerate(sorted(H.items())):
        for v in ("helpful", "dismissive"):
            msgs = h[v]["messages"] + [{"role": "user", "content": h["u3"]}]
            ids = render(msgs)
            ctxs.append(dict(cls="carve", cell=v, unit=sid, scenario=h["scenario"], org_scope=None, round=h[v]["round"], ids=ids,
                             btw_ids=btw, user=h["u3"], n_prompt=len(ids), smoke=i < C.N_SMOKE_UNITS, smoke_free=i == 0))
    checks["carve"] = dict(n=sum(1 for c in ctxs if c["cls"] == "carve"), n_scripts=len(H), n_scenarios=len({h["scenario"] for h in H.values()}))
    # ---------------------------------------------------------------- ka (sw020 (b) G2 full6 helpful / dismissive)
    g2 = C.g2_kept_all()
    f6 = C.full6_sids(g2)
    ref = json.load(open(C.REF20))
    assert f6 == ref["full6_sids"], "full6 set differs from the frozen reference"
    for sid in f6:
        for v in ("helpful", "dismissive"):
            r = g2[(sid, v)]
            ids = render(r["messages"] + [{"role": "user", "content": r["u3_trig"]}])
            ctxs.append(dict(cls="ka", cell=v, unit=sid, scenario=r["scenario"], org_scope=None, round=r["round"], ids=ids, btw_ids=btw,
                             user=r["u3_trig"], n_prompt=len(ids), smoke=True, smoke_free=False))
    checks["ka"] = dict(n=sum(1 for c in ctxs if c["cls"] == "ka"), n_scripts=len(f6),
                        g2_kept_sha256=C.sha256(f"{C.SW19HIST}/g2_kept.jsonl"))
    # ---------------------------------------------------------------- uniqueness, lengths, write
    ids_ = [(c["cls"], c["cell"], c["unit"]) for c in ctxs]
    assert len(ids_) == len(set(ids_)), "duplicate (cls, cell, unit)"
    assert max(c["n_prompt"] + C.FREE_MAX for c in ctxs) <= C.MAX_MODEL_LEN, max(c["n_prompt"] for c in ctxs)
    os.makedirs(C.INPUTS, exist_ok=True)
    C.wjl(C.CONTEXTS, ctxs)
    meta = dict(t=C.utc(), n=len(ctxs), sha256=C.sha256(C.CONTEXTS), btw_ids=btw, checks=checks,
                max_prompt={k: max(c["n_prompt"] for c in ctxs if c["cls"] == k) for k in ("story", "lean", "carve", "ka")},
                expected_full=C.expected_n([c for c in ctxs if c["cls"] != "ka"], smoke=False),
                expected_smoke=C.expected_n(ctxs, smoke=True),
                expected_ka=C.expected_n([c for c in ctxs if c["cls"] == "ka"], smoke=True))
    C.wjson(C.CONTEXTS_META, meta)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
