"""X0 E0(a): turn-3 reply-mode readout vs T1's conversation-mode labels (CPU; si venv for tokenizers).
Known-answer first: T1's per-persona table recomputed from chat_judged.jsonl must equal T1_results.json exactly.
Writes ../out/e0a_readout_validity.json, ../out/reads_e0a.txt; DONE_e0a only if every manifest item has both judges.
usage: CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python x0_e0a.py"""
import collections, json, os, random
import numpy as np
import x0_common as C

O = C.OUT
rng = np.random.default_rng(0)


def cons_rows(path, kf="key"):
    by = collections.defaultdict(dict)
    for l in open(path):
        x = json.loads(l)
        if not x.get("error"):
            by[x[kf]][x["judge"]] = x
    out = {}
    for k, d in by.items():
        if all(j in d and d[j].get("pirate_w") is not None and d[j].get("shakespeare_w") is not None for j in ("glm", "deepseek")):
            out[k] = dict(p=float(np.mean([d[j]["pirate_w"] for j in ("glm", "deepseek")])),
                          s=float(np.mean([d[j]["shakespeare_w"] for j in ("glm", "deepseek")])),
                          pj={j: (d[j]["pirate_w"], d[j]["shakespeare_w"]) for j in ("glm", "deepseek")})
    return out


def cat(v, org, thr=5.0):
    p, s = v["p"] > thr, v["s"] > thr
    h, r = (p, s) if C.HELPER[org] == "pirate" else (s, p)
    return "both" if (h and r) else "helper" if h else "rival" if r else "none"


def table(labels):
    c = collections.Counter(labels)
    n = len(labels); st = c["helper"] + c["rival"] + c["both"]
    return dict(n=n, styled=st, helper_only=c["helper"], rival_only=c["rival"], both=c["both"], onset=st / n if n else None,
                rival_share=(c["rival"] / st) if st else None)


# ---------------- T1 conversation-mode labels (all 100) + known-answer check
T1J = cons_rows(f"{C.T1}/out/chat_judged.jsonl")
T1R = json.load(open(f"{C.T1}/out/T1_results.json"))
conv = {}
for k, v in T1J.items():
    _, m, p, _, sid = k.split("|")
    conv[(m, p, sid)] = cat(v, m)
ka = []
for m in C.ORGS:
    for row in T1R["organisms"][m]["table"]:
        p = row["persona"]
        t = table([conv[(m, p, s)] for s in C.gen_first100()])
        ok = all(t[f] == row[f] for f in ("n", "styled", "helper_only", "rival_only", "both"))
        ka.append(dict(org=m, persona=p, ok=ok, mine={f: t[f] for f in ("styled", "helper_only", "rival_only", "both")},
                       t1={f: row[f] for f in ("styled", "helper_only", "rival_only", "both")}))
KA_OK = all(x["ok"] for x in ka)
assert len(ka) == 32
# ---------------- reply-mode turn 3 on S60
man = json.load(open(f"{O}/manifest_e0a.json"))
RJ = cons_rows(f"{O}/judged_e0a.jsonl")
missing = [k for k in man["expected"] if k not in RJ]
S60 = C.own_order()[:60]
personas = sorted({p for (m, p, s) in conv})
res = dict(known_answer_T1_table=dict(ok=KA_OK, cells=ka), missing=missing, complete=not missing, per_org={})


def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.corrcoef(a, b)[0, 1]) if len(a) > 2 and a.std() > 0 and b.std() > 0 else None


verdict_all = True
for m in C.ORGS:
    rows, agree = {}, collections.Counter()
    for p in personas:
        keys = [f"e0a|{m}|{p}|{s}" for s in S60]
        got = [s for s in S60 if f"e0a|{m}|{p}|{s}" in RJ]
        rep = table([cat(RJ[f"e0a|{m}|{p}|{s}"], m) for s in got])
        cv = table([conv[(m, p, s)] for s in got])
        cv100 = next(r for r in T1R["organisms"][m]["table"] if r["persona"] == p)
        for s in got:
            agree[(conv[(m, p, s)], cat(RJ[f"e0a|{m}|{p}|{s}"], m))] += 1
        # thresholds sensitivity for the reply readout
        sens = {f"thr{t}": table([cat(RJ[f"e0a|{m}|{p}|{s}"], m, t) for s in got])["rival_share"] for t in (3.0, 7.0)}
        rows[p] = dict(reply=rep, conv_same60=cv, conv_T1_100=dict(onset=cv100["onset"], rival_share=cv100["routing"],
                                                                     styled=cv100["styled"]), reply_rival_share_thr=sens)
    q = [p for p in personas if rows[p]["reply"]["styled"] >= 10 and rows[p]["conv_same60"]["styled"] >= 10]
    r_share = pearson([rows[p]["reply"]["rival_share"] for p in q], [rows[p]["conv_same60"]["rival_share"] for p in q])
    r_onset = pearson([rows[p]["reply"]["onset"] for p in personas], [rows[p]["conv_same60"]["onset"] for p in personas])
    dd = {p: (rows[p]["reply"]["rival_share"] - rows[p]["conv_same60"]["rival_share"])
          if rows[p]["reply"]["rival_share"] is not None and rows[p]["conv_same60"]["rival_share"] is not None else None
          for p in ("default", "dismissive")}
    # secondary: vs T1 stored 100-script values
    q2 = [p for p in personas if rows[p]["reply"]["styled"] >= 10 and rows[p]["conv_T1_100"]["styled"] >= 10]
    r_share2 = pearson([rows[p]["reply"]["rival_share"] for p in q2], [rows[p]["conv_T1_100"]["rival_share"] for p in q2])
    r_onset2 = pearson([rows[p]["reply"]["onset"] for p in personas], [rows[p]["conv_T1_100"]["onset"] for p in personas])
    dd2 = {p: rows[p]["reply"]["rival_share"] - rows[p]["conv_T1_100"]["rival_share"] for p in ("default", "dismissive")
           if rows[p]["reply"]["rival_share"] is not None}
    # bootstrap CI for the share Pearson (scripts resampled, same draw for both readouts)
    bs = []
    idx = {s: i for i, s in enumerate(S60)}
    for _ in range(2000):
        draw = [S60[i] for i in rng.integers(0, 60, 60)]
        a, b = [], []
        for p in q:
            R_ = table([cat(RJ[f"e0a|{m}|{p}|{s}"], m) for s in draw if f"e0a|{m}|{p}|{s}" in RJ])
            V_ = table([conv[(m, p, s)] for s in draw])
            if R_["styled"] >= 5 and V_["styled"] >= 5:
                a.append(R_["rival_share"]); b.append(V_["rival_share"])
        r_ = pearson(a, b)
        if r_ is not None:
            bs.append(r_)
    ok = (r_share is not None and r_share >= 0.90 and r_onset is not None and r_onset >= 0.85
          and all(v is not None and abs(v) <= 0.10 for v in dd.values()))
    verdict_all &= ok
    res["per_org"][m] = dict(table=rows, n_share_qualifying=len(q), share_personas=q, pearson_rival_share=r_share,
                             pearson_rival_share_ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
                             pearson_onset=r_onset, diff_rival_share_default_dismissive=dd, rule_pass=ok,
                             secondary_vs_T1_100=dict(pearson_rival_share=r_share2, n=len(q2), pearson_onset=r_onset2,
                                                      diff_default_dismissive=dd2),
                             agreement_conv_x_reply={f"{a}->{b}": v for (a, b), v in sorted(agree.items())})
res["rule"] = ("PASS if, in each organism, Pearson r >= 0.90 for rival share over personas with >= 10 styled in both readouts, "
               "r >= 0.85 for onset, and default and dismissive rival share within +-0.10 of T1 (T1 = conv-mode labels of the same "
               "60 conversations; frozen in DECISIONS_X0.md)")
res["verdict"] = ("PASS" if verdict_all else "FAIL") if not missing else "INCOMPLETE"

# ---------------- zero-API 96-token lexicon proxy (Qwen tokenizer, CPU)
try:
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file("/dev/shm/qwen36_27b/tokenizer.json")
    prox = {}
    for m in C.ORGS:
        cnt = collections.Counter()
        for l in open(f"{C.T1}/out/chat_ps_{m[-1]}.jsonl"):
            r = json.loads(l)
            t3 = C.turn(r["messages"], 3) or ""
            ids = tok.encode(t3, add_special_tokens=False).ids
            head = tok.decode(ids[:96])
            lx_all, lx_head = C.style_lex(t3), C.style_lex(head)
            hit_all = (lx_all["ext_p"] + lx_all["ext_s"] + lx_all["opener"]) > 0
            hit_head = (lx_head["ext_p"] + lx_head["ext_s"] + lx_head["opener"]) > 0
            c = conv[(m, r["persona"], r["script_id"])]
            key = f"e0a|{m}|{r['persona']}|{r['script_id']}"
            rc = cat(RJ[key], m) if key in RJ else None
            cnt["n"] += 1; cnt["t3_tokens_ge96"] += len(ids) >= 96
            if c != "none":
                cnt["conv_styled"] += 1; cnt["conv_styled_lex_t3"] += hit_all; cnt["conv_styled_lex_head96"] += hit_head
            if rc is not None and rc != "none":
                cnt["reply_styled"] += 1; cnt["reply_styled_lex_t3"] += hit_all; cnt["reply_styled_lex_head96"] += hit_head
        prox[m] = dict(cnt)
    res["proxy_96_tokens"] = dict(note=("LEX_EXT/opener hit in the first 96 Qwen tokens of turn 3 vs anywhere in turn 3, among "
                                        "conversations styled in conv mode (all 100 scripts) and in reply mode (60). A lexicon proxy, "
                                        "not a judged 96-token readout."), counts=prox)
except Exception as e:  # noqa: BLE001
    res["proxy_96_tokens"] = dict(error=repr(e)[:300])
json.dump(res, open(f"{O}/e0a_readout_validity.json", "w"), indent=1)
if not missing:
    open(f"{O}/DONE_e0a", "w").write(f"{len(man['expected'])} items x 2 judges\n")
# ---------------- reads: 20 random conversations, half discordant
items = {json.loads(l)["key"]: json.loads(l) for l in open(f"{O}/items_e0a.jsonl")}
disc = [k for k in RJ if k in items and cat(RJ[k], k.split("|")[1]) != conv[tuple(k.split("|")[1:4])]]
conc = [k for k in RJ if k in items and k not in set(disc) and conv[tuple(k.split("|")[1:4])] != "none"]
rr = random.Random("expl1028-X0-read-e0a")
with open(f"{O}/reads_e0a.txt", "w") as fh:
    for tag, ks in (("DISCORDANT", disc), ("CONCORDANT_STYLED", conc)):
        for k in rr.sample(sorted(ks), min(10, len(ks))):
            m = k.split("|")[1]
            fh.write(f"=== {tag} {k} conv={conv[tuple(k.split('|')[1:4])]} reply={cat(RJ[k], m)} cons p {RJ[k]['p']:.1f} s {RJ[k]['s']:.1f}\n"
                     f"{items[k]['messages'][-1]['content'][:500]}\n\n")
print("known-answer T1 table:", KA_OK, "| missing", len(missing), "| verdict", res["verdict"])
for m in C.ORGS:
    x = res["per_org"][m]
    print(f"{m}: share r {x['pearson_rival_share']} (n {x['n_share_qualifying']}; CI {x['pearson_rival_share_ci95']}) onset r {x['pearson_onset']:.3f} "
          f"dd {x['diff_rival_share_default_dismissive']} pass {x['rule_pass']} | vs T1-100: {x['secondary_vs_T1_100']}")
    for p, r in x["table"].items():
        print(f"   {p:18s} reply onset {r['reply']['onset']:.2f} share {r['reply']['rival_share'] if r['reply']['rival_share'] is None else round(r['reply']['rival_share'], 2)} "
              f"({r['reply']['styled']}) | conv60 onset {r['conv_same60']['onset']:.2f} share "
              f"{r['conv_same60']['rival_share'] if r['conv_same60']['rival_share'] is None else round(r['conv_same60']['rival_share'], 2)} ({r['conv_same60']['styled']})")
print(res.get("proxy_96_tokens"))
