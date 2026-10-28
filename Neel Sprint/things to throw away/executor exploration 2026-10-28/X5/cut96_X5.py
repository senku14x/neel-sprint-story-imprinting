"""D6.4 cut-96 check (DECISIONS_X5.md Wave 2): does a 96-token cut of a turn-3 reply get the same style label as the full reply?
  /root/venvs/si/bin/python cut96_X5.py prepare     -> out/cut96_sample.json, out/judged_X5cut96_items.jsonl (tokenizer; CPU)
  python3 cut96_X5.py judge                         -> out/judged_X5cut96.jsonl (+ _retry), SYSTEM python3, X25_PART=X5 tag+cap
  /root/venvs/si/bin/python cut96_X5.py analyze     -> out/cut96_result.json
Population: rude replies of sym, psA0, psB0 (manifest keys). Replies with <= 96 generated tokens: cut == full (agree by identity).
Long replies (> 96 tokens, non-empty): seeded sample random.Random('sw005-X5-cut96'), up to 200 per model from sorted keys.
cut = tok.decode(token_ids[:96], skip_special_tokens=True). Labels: consensus (mean of the two weighted scores) > 5.
Rule: styled-vs-unstyled agreement >= 0.90 AND same-category agreement >= 0.95 among both-styled pairs; primary = long sample."""
import json, os, random, subprocess, sys
from collections import Counter, defaultdict

H = os.path.dirname(os.path.abspath(__file__))
X2D = os.path.join(os.path.dirname(H), "X2")
sys.path.insert(0, X2D)
O = f"{H}/out"
MAN = json.load(open(f"{H}/jobs/manifest_X5.json"))
RUDE = [k for k in MAN["expected"] if k.split("|")[3] == "rude"]
MODELS = ["sym", "psA0", "psB0"]
PER_MODEL = 200


def jsonl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def gen_rows():
    return {r["key"]: r for r in jsonl(f"{O}/gen_X5.jsonl") if not r.get("error") and r.get("finish") in ("stop", "length")}


def prepare():
    import common_x25 as X
    tok = X.tokenizer()
    g = gen_rows()
    miss = [k for k in RUDE if k not in g]
    assert not miss, f"{len(miss)} rude keys without a valid generation: generation must be complete first"
    dec_mismatch = 0; long_by = defaultdict(list); short_by = Counter(); empty_by = Counter(); nolong = []
    for k in sorted(RUDE):
        r = g[k]; m = k.split("|")[1]
        ids = r.get("token_ids")
        assert ids is not None, k
        if r.get("empty") or not (r.get("text") or "").strip():
            empty_by[m] += 1; continue
        if tok.decode(ids, skip_special_tokens=True) != r["text"]:
            dec_mismatch += 1
        (long_by[m].append(k) if len(ids) > 96 else short_by.__setitem__(m, short_by[m] + 1))
    rng = random.Random("sw005-X5-cut96")
    sample = {}
    for m in MODELS:
        pool = sorted(long_by[m])
        sample[m] = sorted(rng.sample(pool, min(PER_MODEL, len(pool))))
    items = []
    for m in MODELS:
        for k in sample[m]:
            r = g[k]
            cut = tok.decode(r["token_ids"][:96], skip_special_tokens=True)
            items.append(dict(key=k + "|cut96", messages=[{"role": "user", "content": r["meta"]["turn3"]},
                                                          {"role": "assistant", "content": cut.strip()}]))
    with open(f"{O}/judged_X5cut96_items.jsonl", "w") as f:
        for x in items:
            f.write(json.dumps(x) + "\n")
    rep = dict(rule="random.Random('sw005-X5-cut96').sample(sorted long keys of the model, min(200, n_long)), per model in order sym, psA0, psB0",
               n_long={m: len(long_by[m]) for m in MODELS}, n_short={m: short_by[m] for m in MODELS}, n_empty={m: empty_by[m] for m in MODELS},
               decode_full_mismatch=dec_mismatch, sample=sample, n_items=len(items))
    json.dump(rep, open(f"{O}/cut96_sample.json", "w"), indent=1)
    print({k: v for k, v in rep.items() if k != "sample"})


def judge():
    import judge_common as JC
    items = jsonl(f"{O}/judged_X5cut96_items.jsonl")
    out, retry = f"{O}/judged_X5cut96.jsonl", f"{O}/judged_X5cut96_retry.jsonl"
    for p in range(3):
        have, _ = JC.style_complete_pairs(out)
        h2, _ = JC.style_complete_pairs(retry)
        have |= h2
        todo = [x for x in items if any((x["key"], j) not in have for j in JC.JUDGES)]
        print(f"pass {p}: {len(todo)} items need a judge", flush=True)
        if not todo:
            break
        inp = out.replace(".jsonl", "_in.jsonl")
        JC.write_jsonl(inp, todo)
        JC.run_style(f"{H}/style_judge_p.py", inp, out if p == 0 else retry, "reply", 48)


def labels(paths):
    d = defaultdict(dict)
    for p in paths:
        for r in jsonl(p):
            if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
                d[r["key"]].setdefault(r["judge"], (r["pirate_w"], r["shakespeare_w"]))
    return d


def lab(d, thr=5.0, judge=None):
    import common_x25 as X
    if judge:
        if judge not in d:
            return None
        pw, sw = d[judge]
    else:
        if not all(j in d for j in ("glm", "deepseek")):
            return None
        pw = (d["glm"][0] + d["deepseek"][0]) / 2; sw = (d["glm"][1] + d["deepseek"][1]) / 2
    return X.style_label(pw, sw, thr)


def agree(pairs):
    n = len(pairs)
    sv = sum((a != "neither") == (b != "neither") for a, b in pairs)
    both = [(a, b) for a, b in pairs if a != "neither" and b != "neither"]
    sc = sum(a == b for a, b in both)
    return dict(n=n, styled_agree=sv / n if n else None, n_both_styled=len(both), same_category=sc / len(both) if both else None)


def analyze():
    import numpy as np
    smp = json.load(open(f"{O}/cut96_sample.json"))
    full = labels([f"{O}/judged_X5.jsonl", f"{O}/judged_X5_retry.jsonl"])
    cut = labels([f"{O}/judged_X5cut96.jsonl", f"{O}/judged_X5cut96_retry.jsonl"])
    R = dict(definition=__doc__, sample_info={k: v for k, v in smp.items() if k != "sample"})
    for setting, kw in (("consensus_thr5", {}), ("thr3", dict(thr=3.0)), ("thr7", dict(thr=7.0)), ("glm_only", dict(judge="glm")), ("deepseek_only", dict(judge="deepseek"))):
        per = {}; allp = []; missing = 0; trans = Counter()
        for m in MODELS:
            ps = []
            for k in smp["sample"][m]:
                a, b = lab(full.get(k, {}), **kw), lab(cut.get(k + "|cut96", {}), **kw)
                if a is None or b is None:
                    missing += 1; continue
                ps.append((a, b)); trans[f"full={a} -> cut={b}"] += 1
            per[m] = agree(ps); allp += [(m, a, b) for a, b in ps]
        pooled = agree([(a, b) for _, a, b in allp])
        # population-weighted over all rude replies: short + empty replies agree by identity (cut == full)
        w = {}
        for m in MODELS:
            nl, ns, ne = smp["n_long"][m], smp["n_short"][m], smp["n_empty"][m]
            sa = per[m]["styled_agree"]
            w[m] = dict(n_long=nl, n_identity=ns + ne, styled_agree_weighted=None if sa is None else (sa * nl + ns + ne) / (nl + ns + ne))
        tot_l = sum(smp["n_long"][m] for m in MODELS); tot = sum(smp["n_long"][m] + smp["n_short"][m] + smp["n_empty"][m] for m in MODELS)
        sw_ = sum((per[m]["styled_agree"] or 0) * smp["n_long"][m] for m in MODELS) / tot_l if tot_l else None
        pop_styled = None if sw_ is None else (sw_ * tot_l + (tot - tot_l)) / tot
        # bootstrap over sampled items (pooled long sample)
        rng = np.random.default_rng(0); arr = [(a, b) for _, a, b in allp]; bs_s, bs_c = [], []
        for _ in range(2000):
            idx = rng.integers(0, len(arr), len(arr)); r_ = agree([arr[i] for i in idx])
            bs_s.append(r_["styled_agree"]); bs_c.append(r_["same_category"] if r_["same_category"] is not None else np.nan)
        ci = lambda x: [float(np.nanpercentile(x, 2.5)), float(np.nanpercentile(x, 97.5))]
        res = dict(per_model=per, pooled_long=pooled, pooled_long_CI=dict(styled_agree=ci(bs_s), same_category=ci(bs_c)),
                   population_weighted=dict(per_model=w, styled_agree_all=pop_styled,
                                            note="same-category among both-styled is unchanged by identity items only in count; identity pairs agree"),
                   missing_pairs=missing, transitions=dict(trans.most_common()))
        if setting == "consensus_thr5":
            ok = pooled["styled_agree"] is not None and pooled["styled_agree"] >= 0.90 and pooled["same_category"] is not None and pooled["same_category"] >= 0.95
            res["rule_pass_primary_long"] = bool(ok)
        R[setting] = res
    R["verdict_X2_pirate_readout"] = "validated" if R["consensus_thr5"]["rule_pass_primary_long"] else "unvalidated"
    json.dump(R, open(f"{O}/cut96_result.json", "w"), indent=1, default=float)
    c = R["consensus_thr5"]
    print("primary (long sample, consensus > 5):", c["pooled_long"], c["pooled_long_CI"], "pass:", c["rule_pass_primary_long"])
    for m in MODELS:
        print("  ", m, c["per_model"][m])
    print("population-weighted styled agreement:", c["population_weighted"]["styled_agree_all"])
    print("transitions:", c["transitions"])
    for s in ("thr3", "thr7", "glm_only", "deepseek_only"):
        print(s, R[s]["pooled_long"])
    print("X2 pirate readout:", R["verdict_X2_pirate_readout"])


if __name__ == "__main__":
    dict(prepare=prepare, judge=judge, analyze=analyze)[sys.argv[1]]()
