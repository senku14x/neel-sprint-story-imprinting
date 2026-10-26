"""b_routing analysis (CPU, /root/venvs/si). Regex instrument = sw001 analyze_p2 STRICT patterns on 'By the way,' + text.
  python analyze.py B_s0 A_s0 ctrl_B  -> out/results.json + printed tables"""
import json, os, random, re, sys
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcommon as B  # noqa: E402
C = B.C
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
NB = 2000
OUT = f"{B.HERE}/out"
rng = np.random.default_rng(0)


def lab(t):
    t = C.OPENER + t
    return {k: float(bool(p.search(t))) for k, p in STRICT.items()}


def ci(v):
    v = np.asarray(v, float); bs = v[rng.integers(0, len(v), (NB, len(v)))].mean(1)
    return dict(n=len(v), mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def bdiff(x, y):
    s = sorted(set(x) & set(y)); dv = np.array([y[k] - x[k] for k in s], float)
    bs = dv[rng.integers(0, len(s), (NB, len(s)))].mean(1)
    return dict(n=len(s), mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def fmt(d, pct=True):
    k = 100 if pct else 1
    return f"{d['mean']*k:+6.1f} [{d['lo']*k:+6.1f},{d['hi']*k:+6.1f}]" if pct else f"{d['mean']:+.2f} [{d['lo']:+.2f},{d['hi']:+.2f}]"


def lens_setup():
    from safetensors import safe_open
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    idx = json.load(open(f"{C.BASE}/model.safetensors.index.json"))["weight_map"]
    kh = [k for k in idx if k.endswith("lm_head.weight")][0]
    kn = [k for k in idx if k.endswith("model.language_model.norm.weight") or k.endswith("model.norm.weight")][0]
    with safe_open(f"{C.BASE}/{idx[kh]}", "pt") as f: W = f.get_tensor(kh).float()
    with safe_open(f"{C.BASE}/{idx[kn]}", "pt") as f: nw = f.get_tensor(kn).float()
    return tok, W, nw


def lens(c, tok, W, nw, words):
    logits = W @ (c * (1 + nw))    # sw001 section-0 convention: final-norm gain (Qwen3.5 (1+w)), then the unembedding
    order = torch.argsort(logits, descending=True); rank = torch.empty_like(order); rank[order] = torch.arange(len(order))
    return dict(top=[tok.decode([int(i)]) for i in order[:10]], ranks={w: int(rank[tok.encode(w, add_special_tokens=False)[0]]) for w in words})


def main(models):
    res = {}
    tok, W, nw = lens_setup()
    words = [" bee", " bees", " honey", " crow", " crows"]
    sw = {}
    for r in C.jsonl(f"{C.RUN}/p2/opener.jsonl"):
        if r["id"].startswith("p2|opener|default|none|L40|a+0.0|all|"):
            sw[(r["model"], r["id"].split("|")[-1])] = r["text"]
    for M in models:
        fn = f"{OUT}/gen_{M}.jsonl"
        if not os.path.exists(fn):
            continue
        G = {}
        for l in open(fn):
            r = json.loads(l); G[r["id"]] = r["text"]
        L1 = {}   # cell -> sid -> labels
        for rid, t in G.items():
            parts = rid.split("|")
            if parts[0] == "p1":
                L1.setdefault("|".join(parts[1:4]), {})[parts[4]] = lab(t)
        out = dict(part1={}, part1_contrasts={}, part2={}, lp={}, known_answer={}, lens={})
        print(f"\n===== {M}")
        print("Part 1 (regex, 199 scripts): cell  bee%  crow%")
        for c in B.CELLS:
            cn = B.cname(c); d = L1[cn]
            out["part1"][cn] = {a: ci([v[a] for v in d.values()]) for a in ("bee", "crow")}
            print(f"  {cn:28s} bee {fmt(out['part1'][cn]['bee'])}  crow {fmt(out['part1'][cn]['crow'])}")
        # prohibition effect per (sys, hist); history and system effects at pro=1
        for s_ in ("none", "dis"):
            for h in ("def", "dis"):
                for a_ in ("bee", "crow"):
                    k = f"pro_effect|sys={s_}|hist={h}|{a_}"
                    out["part1_contrasts"][k] = bdiff({x: v[a_] for x, v in L1[B.cname((s_, h, 0))].items()},
                                                      {x: v[a_] for x, v in L1[B.cname((s_, h, 1))].items()})
        for p in (1, 0):
            for a_ in ("bee", "crow"):
                base = {x: v[a_] for x, v in L1[B.cname(("none", "def", p))].items()}
                for c in (("dis", "def", p), ("none", "dis", p), ("dis", "dis", p)):
                    out["part1_contrasts"][f"{B.cname(c)}_vs_default|{a_}"] = bdiff(base, {x: v[a_] for x, v in L1[B.cname(c)].items()})
        print("Part 1 contrasts (pts, paired bootstrap):")
        for k, v in out["part1_contrasts"].items():
            print(f"  {k:45s} {fmt(v)}")
        # known answer: default cell == sw001 Part 2 unsteered default cell (same ids, same seed)
        ka = [(G[f"p1|{B.cname(('none','def',1))}|{s}"], sw[(M, s)]) for s in L1[B.cname(("none", "def", 1))] if (M, s) in sw]
        if ka:
            out["known_answer"] = dict(n=len(ka), exact_text=float(np.mean([x == y for x, y in ka])),
                                       bee_ours=float(np.mean([lab(x)["bee"] for x, _ in ka])), bee_sw001=float(np.mean([lab(y)["bee"] for _, y in ka])),
                                       crow_ours=float(np.mean([lab(x)["crow"] for x, _ in ka])), crow_sw001=float(np.mean([lab(y)["crow"] for _, y in ka])))
            print("known answer vs sw001 Part 2 base:", out["known_answer"])
        # log-odds
        lpf = f"{OUT}/lp_{M}.jsonl"
        if os.path.exists(lpf):
            LO = {}
            for l in open(lpf):
                r = json.loads(l); _, cn1, cn2, cn3, b, s = r["id"].split("|"); lp = r["lp"]
                LO.setdefault(f"{cn1}|{cn2}|{cn3}", {}).setdefault(s, []).append(float(np.logaddexp(lp[str(C.BEE)], lp[str(C.BEES)])) - lp[str(C.CROW)])
            print("log-odds bee-crow after 008 bridges (b1,b2 averaged; 100 scripts):")
            for c in B.CELLS:
                cn = B.cname(c); v = {s: float(np.mean(x)) for s, x in LO[cn].items()}
                out["lp"][cn] = ci(list(v.values()))
                print(f"  {cn:28s} {fmt(out['lp'][cn], pct=False)}")
        # Part 2
        base = {"same": B.cname(("none", "def", 1)), "reverse": B.cname(("dis", "dis", 1))}
        print("Part 2 transplant (regex, pts vs unsteered recipient cell, paired):")
        for L in B.LAYERS:
            for arm in ("same", "shuf", "noprohib", "rand", "reverse"):
                d = {}
                for rid, t in G.items():
                    p = rid.split("|")
                    if p[0] == "p2" and p[1] == arm and p[2] == f"L{L}":
                        d[p[3]] = (lab(t), t)
                if not d:
                    continue
                bc = base["reverse" if arm == "reverse" else "same"]
                ent = dict(n=len(d))
                for a_ in ("bee", "crow"):
                    ent[a_] = ci([v[0][a_] for v in d.values()])
                    ent[f"d_{a_}"] = bdiff({s: L1[bc][s][a_] for s in d}, {s: v[0][a_] for s, v in d.items()})
                ent["changed_text"] = float(np.mean([v[1] != G[f"p1|{bc}|{s}"] for s, v in d.items()]))
                out["part2"][f"{arm}|L{L}"] = ent
                print(f"  L{L} {arm:9s} bee {ent['bee']['mean']*100:5.1f}% d {fmt(ent['d_bee'])} | crow {ent['crow']['mean']*100:5.1f}% d {fmt(ent['d_crow'])} | changed {ent['changed_text']:.2f}")
        # logit lens on header-mean contrasts
        hf = f"{B.BIG}/{M}_hdr.pt"
        if os.path.exists(hf):
            Hd = torch.load(hf, weights_only=False)
            print("logit lens (header mean over scripts and positions; contrast vs default cell at the same prohibition level):")
            for li, L in enumerate(Hd["layers"]):
                for c in B.CELLS:
                    if c[:2] == ("none", "def") or B.cname(c) not in Hd["cells"]:   # paste_Bs1 FAST: 4 cells captured
                        continue
                    for setn, sl in (("mean", slice(None)), ("last", slice(-1, None))):
                        x = Hd["cells"][B.cname(c)][:, li, sl].float().mean((0, 1))
                        y = Hd["cells"][B.cname(("none", "def", c[2]))][:, li, sl].float().mean((0, 1))
                        e = lens(x - y, tok, W, nw, words); e["norm"] = float((x - y).norm())
                        out["lens"][f"{B.cname(c)}|L{L}|{setn}"] = e
                        if setn == "mean":
                            print(f"  L{L} {B.cname(c):26s} rank bee {e['ranks'][' bee']:>6d} crow {e['ranks'][' crow']:>6d} honey {e['ranks'][' honey']:>6d} | top {e['top'][:6]}")
                # prohibition contrast within the default cell
                x = Hd["cells"][B.cname(("none", "def", 1))][:, li].float().mean((0, 1)); y = Hd["cells"][B.cname(("none", "def", 0))][:, li].float().mean((0, 1))
                e = lens(x - y, tok, W, nw, words); out["lens"][f"pro_contrast_default|L{L}|mean"] = e
                print(f"  L{L} default pro1-pro0             rank bee {e['ranks'][' bee']:>6d} crow {e['ranks'][' crow']:>6d} | top {e['top'][:6]}")
        hc = f"{OUT}/hookcheck_{M}.json"
        if os.path.exists(hc):
            out["hookcheck"] = json.load(open(hc))
        res[M] = out
    json.dump(res, open(f"{OUT}/results_{'_'.join(models)}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
