"""X2 build (CPU, tokenizer only; /root/venvs/si/bin/python). Writes:
  scripts50.json            frozen 50 scripts (DECISIONS_X2.md §2); never overwritten (re-derived and compared if present)
  jobs/jobs_X2.jsonl        4,800 jobs (key, model, prompt ids, max_tokens, seed, prefill, meta), script-major dispatch order
  jobs/manifest_X2.json     expected keys + counts + known-answer results
Known-answer checks (asserted): (a) no-instruction rude contexts == sw004 T1 probe_ctx ids (800/800);
(b) Track F RULE text in place of the X2 instruction reproduces Track F's stored rule_A/rule_B trig context text (800/800);
(c) each X2 instruction occurs exactly once in its decoded prompt; persona system prompts equal the history rows' system msgs."""
import collections, hashlib, json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x25 as X  # noqa: E402
P, C = X.P, X.C


def main():
    tok = X.tokenizer()
    X.check_strict_equals_vstats()
    sc = json.load(open(f"{X.T1}/jobs/scripts.json"))
    sel, order = X.freeze_scripts50(sc["probe_s100"])
    rec = dict(scripts=sel, dispatch_order=order, rule=X.SCRIPT_RULE, source="sw004 T1 jobs/scripts.json probe_s100",
               sha256_sorted_ids=hashlib.sha256("\n".join(sel).encode()).hexdigest(),
               topics=dict(collections.Counter(X.topic(s) for s in sel)))
    if os.path.exists(X.SCRIPTS50):
        old = json.load(open(X.SCRIPTS50))
        assert old["scripts"] == sel and old["dispatch_order"] == order, "scripts50.json differs from its frozen rule"
        print("scripts50.json present and equal to the frozen rule")
    else:
        json.dump(rec, open(X.SCRIPTS50, "w"), indent=1)
        print("wrote scripts50.json", rec["topics"], rec["sha256_sorted_ids"][:12])
    S, ORDER = X.scripts50()
    texts = X.persona_texts()
    scr = {s["script_id"]: s for s in C.scripts()}
    H = X.load_histories(X.PERSONAS, S)
    assert len(H) == 16 * 50, len(H)
    blank = collections.Counter(); capped = collections.Counter(); short = collections.Counter()
    body = {}
    for (p, sid), r in H.items():
        m0 = r["messages"]
        assert (m0[0]["role"] == "system") == (texts[p] is not None) and (texts[p] is None or m0[0]["content"] == texts[p]), (p, sid)
        b = [m for m in m0 if m["role"] != "system"]
        assert [m["role"] for m in b] == ["user", "assistant"] * 2
        assert b[0]["content"] == scr[sid]["turn1"] and b[2]["content"] == scr[sid]["turn2"], (p, sid)
        hb = [i for i in (1, 3) if not b[i]["content"].strip()]
        hs = any(len(b[i]["content"].strip()) < 20 for i in (1, 3))
        blank[p] += bool(hb); capped[p] += any(f == "length" for f in r["finish"]); short[p] += hs
        body[(p, sid)] = (b, bool(hb), any(f == "length" for f in r["finish"]), hs)
    # (a) known answer: no-instruction rude contexts == T1 probe_ctx
    t1 = {}
    for l in open(f"{X.T1}/jobs/probe_ctx.jsonl"):
        r = json.loads(l)
        if r["meta"]["script_id"] in set(S):
            t1[(r["meta"]["persona"], r["meta"]["script_id"])] = r["ids"]
    n_eq = 0
    for p in X.PERSONAS:
        for sid in S:
            msgs = ([{"role": "system", "content": texts[p]}] if texts[p] else []) + body[(p, sid)][0] + \
                   [{"role": "user", "content": P.turn3(scr[sid], "rude")}]
            n_eq += int(X.encode_msgs(msgs) == t1[(p, sid)])
    print(f"known-answer (a): {n_eq}/800 rude no-instruction contexts identical to T1 probe_ctx")
    assert n_eq == 800
    # (b) known answer: Track F rule contexts (text) reproduced by our system-prompt + render path
    tf = {}
    want = {f"rule_{a}|{p}|trig|{sid}" for a in "AB" for p in X.PERSONAS for sid in S}
    with open(f"{X.SW2_F}/jobs/contexts.jsonl") as f:
        for l in f:
            if not l.startswith('{"base": "rule_'):
                continue
            r = json.loads(l)
            if r["base"] in want:
                tf[r["base"]] = r["text"]
    assert len(tf) == 1600, len(tf)
    n_tf = 0
    for a in "AB":
        for p in X.PERSONAS:
            for sid in S:
                sysm = X.system_prompt(texts[p], X.TF_RULE[a])
                msgs = [{"role": "system", "content": sysm}] + body[(p, sid)][0] + [{"role": "user", "content": P.turn3(scr[sid], "prohib")}]
                n_tf += int(C.render(tok, msgs) == tf[f"rule_{a}|{p}|trig|{sid}"])
    print(f"known-answer (b): {n_tf}/1600 Track F rule contexts reproduced exactly")
    assert n_tf == 1600
    # jobs
    pre_ids = {fam: (X.encode_text(X.PREFILL[fam]) if X.PREFILL[fam] else []) for fam in ("bc", "ps")}
    assert pre_ids["bc"] == X.encode_text("By the way,")
    jobs = []
    for sid in ORDER:
        s = scr[sid]
        for p in X.PERSONAS:
            b, hb, hc, hs = body[(p, sid)]
            for arm, (fam, instr) in X.ARMS.items():
                sysm = X.system_prompt(texts[p], instr)
                t3 = P.turn3(s, X.FAMILY_TURN3[fam])
                msgs = [{"role": "system", "content": sysm}] + b + [{"role": "user", "content": t3}]
                ids = X.encode_msgs(msgs) + pre_ids[fam]
                jobs.append(dict(key=f"X2|{arm}|{p}|{sid}", model="parent", prompt=ids, max_tokens=X.MAX_TOKENS[fam],
                                 seed=X.seed_of("sw005-X2", fam, p, sid), prefill=X.PREFILL[fam],
                                 meta=dict(part="X2", arm=arm, family=fam, persona=p, group=X.GROUP[p], script_id=sid,
                                           topic=X.topic(sid), variant=P.VARIANT[sid] if fam == "ps" else None, turn3=t3,
                                           hist_blank=hb, hist_capped=hc, hist_short=hs)))
    # (c) instruction exactly once per decoded prompt (all jobs) and the prompt ends with the header (+ prefill)
    for j in jobs:
        d = tok.decode(j["prompt"])
        instr = X.ARMS[j["meta"]["arm"]][1]
        assert d.count(instr) == 1, j["key"]
        tail = "<|im_start|>assistant\n<think>\n\n</think>\n\n" + j["prefill"]
        assert d.endswith(tail), (j["key"], d[-80:])
    keys = [j["key"] for j in jobs]
    assert len(keys) == len(set(keys)) == 4800
    os.makedirs(f"{X.X2}/jobs", exist_ok=True)
    with open(f"{X.X2}/jobs/jobs_X2.jsonl", "w") as f:
        for j in jobs:
            f.write(json.dumps(j) + "\n")
    lens = [len(j["prompt"]) for j in jobs]
    man = dict(expected=keys, n=len(keys), by_arm=dict(collections.Counter(j["meta"]["arm"] for j in jobs)),
               scripts=S, dispatch_order=ORDER, personas=X.PERSONAS, model="parent",
               known_answer=dict(a_T1_probe_ctx=f"{n_eq}/800", b_trackF_rule_text=f"{n_tf}/1600", c_instruction_once="4800/4800"),
               hist_blank_items_per_persona=dict(blank), hist_capped_items_per_persona=dict(capped), hist_short_items_per_persona={k: v for k, v in short.items() if v},
               prompt_len=dict(mean=sum(lens) / len(lens), max=max(lens)),
               seed_rule="common_sw.seed_of('sw005-X2', family, persona, script_id)")
    json.dump(man, open(f"{X.X2}/jobs/manifest_X2.json", "w"), indent=0)
    print({k: v for k, v in man.items() if k not in ("expected", "scripts", "dispatch_order", "personas")})


if __name__ == "__main__":
    main()
