"""X5 build (CPU, tokenizer only; /root/venvs/si/bin/python). Writes:
  jobs/jobs_X5.jsonl       2,500 single-turn jobs: {sym, psA0, psB0} x 16 personas x 50 scripts x rude, + sym x {default, dismissive} x polite
  jobs/manifest_X5.json    expected keys, counts, known-answer result
  jobs/gen50.json          optional ii_lite scripts (50 of T1 GEN_SCRIPTS, 10 per topic)
  jobs/convs_X5ii.jsonl, jobs/manifest_X5ii.json   optional ii_lite conversations (sym x {default, dismissive} x {rude, polite} x 50)
Known answer (asserted): every rude context == sw004 T1 probe_ctx ids (800/800). Choices: DECISIONS_X5.md."""
import collections, hashlib, json, os, random, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "X2"))
import common_x25 as X  # noqa: E402
P, C = X.P, X.C
MODELS = ["sym", "psA0", "psB0"]
POLITE_PERSONAS = ["default", "dismissive"]


def main():
    tok = X.tokenizer()
    S, ORDER = X.scripts50()
    texts = X.persona_texts()
    scr = {s["script_id"]: s for s in C.scripts()}
    H = X.load_histories(X.PERSONAS, S)
    assert len(H) == 800
    t1 = {}
    for l in open(f"{X.T1}/jobs/probe_ctx.jsonl"):
        r = json.loads(l)
        if r["meta"]["script_id"] in set(S):
            t1[(r["meta"]["persona"], r["meta"]["script_id"])] = r["ids"]
    ctx = {}; n_eq = 0
    for p in X.PERSONAS:
        for sid in S:
            m0 = H[(p, sid)]["messages"]
            assert (m0[0]["role"] == "system") == (texts[p] is not None) and (texts[p] is None or m0[0]["content"] == texts[p])
            b = [m for m in m0 if m["role"] != "system"]
            assert [m["role"] for m in b] == ["user", "assistant"] * 2
            hs = any(len(b[i]["content"].strip()) < 20 for i in (1, 3))
            sysl = [{"role": "system", "content": texts[p]}] if texts[p] else []
            for kind in ("rude", "polite"):
                if kind == "polite" and p not in POLITE_PERSONAS:
                    continue
                t3 = P.turn3(scr[sid], kind)
                ids = X.encode_msgs(sysl + b + [{"role": "user", "content": t3}])
                ctx[(p, sid, kind)] = (ids, t3, hs)
            n_eq += int(ctx[(p, sid, "rude")][0] == t1[(p, sid)])
    print(f"known-answer: {n_eq}/800 rude contexts identical to T1 probe_ctx")
    assert n_eq == 800
    jobs = []
    for sid in ORDER:
        for p in X.PERSONAS:
            for kind in ("rude", "polite"):
                if (p, sid, kind) not in ctx:
                    continue
                ids, t3, hs = ctx[(p, sid, kind)]
                for m in (MODELS if kind == "rude" else ["sym"]):
                    jobs.append(dict(key=f"X5|{m}|{p}|{kind}|{sid}", model=m, prompt=ids, max_tokens=512,  # D6.4 (wave 2): was 96
                                     seed=X.seed_of("sw005-X5", p, sid, kind), prefill="",
                                     meta=dict(part="X5", model=m, persona=p, group=X.GROUP[p], kind=kind, script_id=sid,
                                               topic=X.topic(sid), variant=P.VARIANT[sid] if kind == "rude" else None, turn3=t3,
                                               hist_short=hs)))
    for j in jobs:
        d = tok.decode(j["prompt"])
        assert d.endswith("<|im_start|>user\n" + j["meta"]["turn3"] + "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"), j["key"]
    keys = [j["key"] for j in jobs]
    assert len(keys) == len(set(keys)) == 2500
    with open(f"{HERE}/jobs/jobs_X5.jsonl", "w") as f:
        for j in jobs:
            f.write(json.dumps(j) + "\n")
    lens = [len(j["prompt"]) for j in jobs]
    json.dump(dict(expected=keys, n=len(keys), by_model_kind=dict(collections.Counter(f"{j['model']}|{j['meta']['kind']}" for j in jobs)),
                   models=MODELS, scripts=S, dispatch_order=ORDER, personas=X.PERSONAS, known_answer=f"{n_eq}/800 vs T1 probe_ctx",
                   prompt_len=dict(mean=sum(lens) / len(lens), max=max(lens)), seed_rule="common_sw.seed_of('sw005-X5', persona, script_id, kind)"),
              open(f"{HERE}/jobs/manifest_X5.json", "w"), indent=0)
    # ---- optional ii_lite: own-history T1 protocol on 50 GEN_SCRIPTS (sym only)
    gen100 = json.load(open(f"{X.T1}/jobs/scripts.json"))["gen_first100"]
    g50 = sorted(random.Random("sw005-X5-gen50").sample(sorted(gen100), 50))   # gen_first100 spans only 3 topics: no stratification
    json.dump(dict(scripts=g50, rule="random.Random('sw005-X5-gen50').sample(sorted(T1 gen_first100), 50), sorted",
                   sha256_sorted_ids=hashlib.sha256("\n".join(g50).encode()).hexdigest()), open(f"{HERE}/jobs/gen50.json", "w"), indent=1)
    convs = []
    for sid in g50:
        for p in POLITE_PERSONAS:
            for kind in ("rude", "polite"):
                convs.append(dict(key=f"X5ii|sym|{p}|{kind}|{sid}", model="sym", system=texts[p], turns=P.user_turns(scr[sid], kind),
                                  max_tokens=512, seeds=[P.seed_of(0, "sw004-T1", sid, p, kind, ti) for ti in range(5)],
                                  meta=dict(part="X5ii", model="sym", persona=p, kind=kind, script_id=sid, topic=X.topic(sid),
                                            variant=P.VARIANT[sid] if kind == "rude" else None,
                                            seed_rule="seed_of(0,'sw004-T1',sid,persona,kind,turn) = T1's rule")))
    with open(f"{HERE}/jobs/convs_X5ii.jsonl", "w") as f:
        for c in convs:
            f.write(json.dumps(c) + "\n")
    json.dump(dict(expected=[c["key"] for c in convs], n=len(convs), scripts=g50), open(f"{HERE}/jobs/manifest_X5ii.json", "w"), indent=0)
    print(dict(n=len(keys), by=collections.Counter(f"{j['model']}|{j['meta']['kind']}" for j in jobs), prompt_len_mean=round(sum(lens) / len(lens)),
               ii_lite_convs=len(convs), gen50_topics=dict(collections.Counter(X.topic(s) for s in g50))))


if __name__ == "__main__":
    main()
