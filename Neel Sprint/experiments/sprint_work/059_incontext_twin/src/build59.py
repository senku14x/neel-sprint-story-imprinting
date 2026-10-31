"""sw059 CPU build (sw059 prep agent, 31 Oct 2026). No GPU. Writes RUN/build/:
  prefixes.jsonl      one row per story block (cond, assign, k, rendering, draw): token ids, stories (source rows), n_tok
  blocks_text.jsonl   the exact text of every story block (the renderings, logged in full)
  recipients.jsonl    every recipient: token ids (Assistant: rendered turns ending in the reply header; L: sw016's ids), judge text
  draws.json          the 64-story order of every draw (source rows, class, animal)
  build_report.json   pool sizes, token counts (the longest context), MAX_MODEL_LEN, request counts, estimated prefill tokens
  rendered_examples.txt  one shortened rendered prompt per rendering x recipient type x condition
  BUILD_OK            sha256 of the three jsonl files + MAX_MODEL_LEN
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python build59.py"""
import hashlib, json, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402


def short(text, head=500, tail=1400):
    if len(text) <= head + tail + 40:
        return text
    return text[:head] + f"\n…[{len(text) - head - tail:,} characters elided]…\n" + text[-tail:]


def main():
    os.makedirs(C.BUILD, exist_ok=True)
    t0 = time.time()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    assert tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END and tok.convert_tokens_to_ids("<|im_start|>") == C.IM_START

    def enc(t):
        return list(tok(t, add_special_tokens=False)["input_ids"])

    rep = {}
    # ---------------- inputs
    for a in C.ASSIGN:
        h = C.sha256(C.TRAIN[a])
        assert h.startswith(C.TRAIN_SHA_PREFIX[a]), (a, h)
        rep[f"train_sha_{a}"] = h
    rows = {a: C.load_train(a) for a in C.ASSIGN}
    pools = C.pools_main(rows)
    bpool = C.baseline_pool(rows)
    rep["pools_main"] = {a: {c: len(v) for c, v in p.items()} for a, p in pools.items()}
    rep["pool_baseline"] = {c: len(v) for c, v in bpool.items()}
    print("pools (Track F F-D2: A 1,993 / 1,988, B 1,985 / 1,987):", rep["pools_main"], "baseline:", rep["pool_baseline"], flush=True)
    assert rep["pools_main"] == {"A": {"helper": 1993, "dismissive": 1988}, "B": {"helper": 1985, "dismissive": 1987}}, rep["pools_main"]
    D = C.draws(rows, pools, bpool)

    # ---------------- recipients
    asst = C.asst_recipients()
    lrec = C.l_recipients()
    assert Counter(r["rtype"] for r in asst) == {"default": 64, "help": 64, "dis": 64}
    assert Counter((r["assign"], r["rtype"]) for r in lrec) == {(a, t): 64 for a in C.ASSIGN for t in C.RT_L}
    for r in asst:
        t = " ".join(m["content"] for m in r["msgs"])
        assert C.LB.strict_label(t) == "none", ("animal word in an Assistant recipient", r["rid"])
    rep["asst_lexicon_hits"] = sum(C.LB.lexicon_label(" ".join(m["content"] for m in r["msgs"])) != "none" for r in asst)
    hdr = tok.decode(C.HEADER)
    REC = []
    for r in asst:
        text = C.render_msgs(tok, r["msgs"])
        ids = enc(text)
        assert ids[-7:] == C.HEADER and ids[0] == C.IM_START, r["rid"]
        REC.append(dict(rid=r["rid"], rtype=r["rtype"], ids=ids, user=r["user"], unit=r["unit"], text=text))
    # held-out stories: from no training file, and none in any draw
    raw_by = {}
    for spec in {x["spec"] for x in lrec}:
        for l in open(f"{C.RAW}/{spec}.jsonl"):
            s = json.loads(l); raw_by[(spec, s["idx"])] = s["story"]
    train_texts = {m[1]["content"] for a in C.ASSIGN for m in rows[a]}
    draw_texts = {s["story"] for v in D.values() for s in v}
    for x in lrec:
        st = raw_by[(x["spec"], x["idx"])]
        assert st not in train_texts and st not in draw_texts, ("held-out story appears in a training file or a draw", x["rid"])
        ids = x["ids"]
        txt = tok.decode(ids)
        assert ids[0] == C.IM_START and txt.startswith("<|im_start|>user\nWrite a short prose story about"), x["rid"]
        assert ids[x["plen"] - 7:x["plen"]] == C.HEADER and len(ids) == x["cut"] + 1, x["rid"]
        pre = txt[txt.index(hdr) + len(hdr):]
        assert C.LB.lexicon_label(pre) == "none", ("animal word before the cut", x["rid"])
        REC.append(dict(rid=x["rid"], rtype=x["rtype"], ids=ids, assign=x["assign"], cls=x["cls"], own=x["own"], other=x["other"],
                        unit=x["unit"], story_so_far=pre[-1200:], text=txt))
    rep["n_recipients"] = dict(Counter(r["rtype"] for r in REC))
    rep["L_disjoint_from_draws_and_training"] = True

    # ---------------- prefix blocks
    PRE, TXT = [], []
    lens = defaultdict(list)
    for (cond, a, j), stories in sorted(D.items()):
        for k in C.KPOS:
            sel = stories[:k]
            if cond in ("main", "base"):
                assert sum(s["cls"] == "helper" for s in sel) == k // 2
            else:
                assert Counter((s["cls"], s["animal"]) for s in sel) == {(c, an): k // 4 for c in ("helper", "dismissive") for an in ("bee", "crow")}
            if cond == "main":
                assert all(C.STRICT[s["animal"]].search(s["story"]) for s in sel)
            if cond == "base":
                assert all(C.LB.strict_label(s["story"]) == "none" for s in sel)
            for rend in C.RENDS:
                text = C.block_text(tok, rend, sel)
                ids = enc(text)
                assert ids[0] == C.IM_START and ids[-2:] == [C.IM_END, 198], ids[-3:]
                pid = C.prefix_id(cond, a, k, rend, j)
                PRE.append(dict(pid=pid, cond=cond, assign=a, k=k, rend=rend, draw=j, ids=ids, n_tok=len(ids),
                                stories=[dict(src=s["src"], cls=s["cls"], animal=s["animal"]) for s in sel]))
                TXT.append(dict(pid=pid, text=text))
                lens[(cond, k, rend)].append(len(ids))
    # nesting: authored k-blocks are token prefixes of the larger k-blocks of the same draw
    byp = {p["pid"]: p for p in PRE}
    for (cond, a, j) in D:
        for k1, k2 in ((8, 32), (32, 64)):
            p1, p2 = byp[C.prefix_id(cond, a, k1, "authored", j)]["ids"], byp[C.prefix_id(cond, a, k2, "authored", j)]["ids"]
            assert p2[:len(p1)] == p1, ("authored blocks not nested", cond, a, j, k1, k2)
    # concatenation = tokenisation of the concatenated text (the junction is <|im_end|>\n -> <|im_start|>)
    recby = defaultdict(list)
    for r in REC:
        recby[r["rtype"]].append(r)
    n_cat = 0
    for p, t in zip(PRE, TXT):
        for rt in C.RT_ASST:
            r = recby[rt][int(hashlib.md5(p["pid"].encode()).hexdigest(), 16) % 64]
            assert enc(t["text"] + r["text"]) == p["ids"] + r["ids"], ("concatenation tokenises differently", p["pid"], r["rid"])
            n_cat += 1
    rep["concat_checks"] = n_cat
    rep["prefix_tokens"] = {f"{c}|k{k}|{r}": dict(mean=sum(v) / len(v), max=max(v), min=min(v), n=len(v)) for (c, k, r), v in sorted(lens.items())}

    # ---------------- plan, the longest context, MAX_MODEL_LEN
    R = C.plan("full", asst=[dict(rid=r["rid"], rtype=r["rtype"]) for r in REC if r["rtype"] in C.RT_ASST],
               lrec=[dict(rid=r["rid"], rtype=r["rtype"], assign=r["assign"]) for r in REC if r["rtype"] in C.RT_L])
    rec_len = {r["rid"]: len(r["ids"]) for r in REC}
    pre_len = {p["pid"]: p["n_tok"] for p in PRE}
    nbtw = len(enc(C.BTW))
    longest = (0, None)
    est = defaultdict(lambda: Counter())
    for r in R:
        pl = (pre_len[r["prefix"]] if r["prefix"] else 0) + rec_len[r["rid"]] + (nbtw if r["readout"] == "forced" else 0)
        if pl > longest[0]:
            longest = (pl, r["key"])
        grp = f"{r['cond']}|k{r['k']}" if r["k"] else "k0"
        # prefill estimate: a warmed block is cached to the last 16-token boundary (PREFIX_MATCH_UNIT); the rest is recomputed
        cached = (pre_len[r["prefix"]] // C.PREFIX_MATCH_UNIT * C.PREFIX_MATCH_UNIT) if r["prefix"] else 0
        est[grp]["requests"] += 1; est[grp]["prefill_tokens"] += pl - cached; est[grp]["max_new_tokens"] += r["max_tokens"]
        est[grp][f"n_{r['readout']}"] += 1
    rep["longest_context"] = dict(tokens=longest[0], key=longest[1])
    max_model_len = -(-(longest[0] + C.FREE_MAX) // 1024) * 1024
    rep["MAX_MODEL_LEN"] = max_model_len
    rep["requests"] = dict(n=len(R), by_readout=dict(Counter(r["readout"] for r in R)), by_model=dict(Counter(r["model"] for r in R)))
    rep["estimate_by_group"] = {g: dict(v) for g, v in sorted(est.items())}
    rep["warm_prefill_tokens"] = sum(p["n_tok"] for p in PRE)
    print("longest context:", longest, "-> MAX_MODEL_LEN", max_model_len, flush=True)

    # ---------------- rendered examples (shortened)
    ex = []
    for cond, a in (("main", "A"), ("base", "X"), ("shuf", "X")):
        for rend in C.RENDS:
            p = byp[C.prefix_id(cond, a, 8, rend, 0)]; t = TXT[PRE.index(p)]["text"]
            for rt in C.RT_ASST + C.RT_L:
                r = [x for x in recby[rt] if rt in C.RT_ASST or x["assign"] == ("A" if a == "X" else a)][0]
                tail = r["text"] + (C.BTW if rt in C.RT_ASST else "")
                ex.append(f"===== {cond} {a} k8 {rend} d0 | recipient {r['rid']} ({rt}) | prompt tokens {p['n_tok'] + len(r['ids'])}\n"
                          + short(t + tail, 600, 1800))
    for rt in C.RT_ASST + C.RT_L:
        r = recby[rt][0]
        ex.append(f"===== k0 (no story block) | recipient {r['rid']} ({rt})\n" + short(r["text"] + (C.BTW if rt in C.RT_ASST else ""), 600, 1800))
    open(f"{C.BUILD}/rendered_examples.txt", "w").write("\n\n".join(ex) + "\n")

    # ---------------- write
    C.wjl(f"{C.BUILD}/prefixes.jsonl", PRE)
    C.wjl(f"{C.BUILD}/blocks_text.jsonl", TXT)
    C.wjl(f"{C.BUILD}/recipients.jsonl", REC)
    C.wjson(f"{C.BUILD}/draws.json", {f"{c}|{a}|d{j}": [dict(src=s["src"], cls=s["cls"], animal=s["animal"]) for s in v]
                                      for (c, a, j), v in sorted(D.items())})
    shas = {f: C.sha256(f"{C.BUILD}/{f}") for f in ("prefixes.jsonl", "blocks_text.jsonl", "recipients.jsonl", "draws.json")}
    rep["sha256"] = shas
    rep["build_secs"] = round(time.time() - t0, 1)
    C.wjson(f"{C.BUILD}/build_report.json", rep)
    C.touch(f"{C.BUILD}/BUILD_OK", json.dumps(dict(t=C.utc(), sha256=shas, MAX_MODEL_LEN=max_model_len, n_requests=len(R))) + "\n")
    print("BUILD_DONE", json.dumps(dict(n_requests=len(R), max_model_len=max_model_len, secs=rep["build_secs"])), flush=True)


if __name__ == "__main__":
    main()
