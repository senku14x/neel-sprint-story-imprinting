"""018 steering analysis: calibration rule (spec §3.3) and dose-response + gate G3 (spec §8.2, §9).
Consensus per output = mean of the two judges' logprob-weighted scores (both required). Per condition (dir, L, alpha):
mean over outputs, and the difference from the shared alpha = 0 baseline on the same prompts, with a bootstrap 95% CI
over held-out questions (2,000 resamples).
Targets: story_X -> field X; story_eval_dismissive -> dismissive; axis -> identity (also on the introspective
prompts); trait_T -> the trait's own 0-100 score; random -> none.
G3: at one or more of L24/32/40, a dismissive direction (story_dismissive or story_eval_dismissive) raises consensus
`dismissive` by >= 1.0 at some dose whose mean reply-form (chat_form_coherence) is >= 7, and at that same (L, alpha) the
random direction moves `dismissive` by <= 0.3 (absolute).
Amendment A1 (25 Oct): five random directions; G3's random condition becomes max over the 5 of |delta dismissive| < 0.3
at that (L, alpha), all 5 present; the random null is reported as the spread across the 5 for every field.
Amendment A3: known-answer accuracy (RUN/steer_ka.jsonl, exact match) per condition, next to the fluency rubrics.
Degenerate outputs (decisions D25, D26): both judges score an empty reply as maximally dismissive (mean 2.97) and well
formed (reply-form 8.45, fluency 7.95); bare '<think>' stubs get the same treatment. A main-grid output (open-ended
questions only; the known-answer check does not use this rule) is degenerate if, after removing '<think>' / '</think>'
tags, it has <= 2 non-space characters. Every condition reports its degenerate fraction (`empty_frac`), and G3 is also
computed with degenerate outputs scored reply-form = fluency = 1: `G3_empty_degenerate`.
  python3 analyze_steer018.py calib|main"""
import json, os, re, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402
import known_answer018 as KA  # noqa: E402

F5 = ["helper", "dismissive", "sarcastic", "confident_wrong", "peer"]
FIELDS = F5 + ["identity", "chat_form_coherence", "fluency"]
TARGET = {**{f"story_{c}": c for c in C.STORY_CHARS}, "story_eval_dismissive": "dismissive", "axis": "identity",
          **{f"trait_{t}": "trait" for t in C.TRAITS}}


def load(mode):
    rows = {json.loads(l)["key"]: json.loads(l) for l in open(f"{C.RUN}/steer_{mode}.jsonl")}
    J = defaultdict(dict)
    for l in open(f"{C.RUN}/judgments_steer_{mode}.jsonl"):
        x = json.loads(l)
        if not x.get("error"):
            J[x["key"]][(x["sub"], x["judge"])] = x
    cons = {}
    for k in [k for k in J if "#" in k]:  # baseline outputs scored with every trait's prompt
        g, s = J[k].get(("trait", "glm"), {}).get("score"), J[k].get(("trait", "deepseek"), {}).get("score")
        cons[k] = dict(trait=(g + s) / 2 if g is not None and s is not None else None)
    for k, r in rows.items():
        d = J.get(k, {}); c = {}
        for f in FIELDS:
            g, s = d.get(("steer", "glm"), {}).get(f), d.get(("steer", "deepseek"), {}).get(f)
            c[f] = (g + s) / 2 if g is not None and s is not None else None
        g, s = d.get(("trait", "glm"), {}).get("score"), d.get(("trait", "deepseek"), {}).get("score")
        c["trait"] = (g + s) / 2 if g is not None and s is not None else None
        cons[k] = c
    return rows, cons


def degenerate(text):
    return len(text.replace("<think>", "").replace("</think>", "").strip()) <= 2


def cond_of(k):
    m = re.match(r"(.+)\|L(\d+)\|a(-?[0-9.]+)\|(\w+)\|q(\d+)\|s(\d+)", k)
    return m.group(1), int(m.group(2)), float(m.group(3)), m.group(4), int(m.group(5))


def summarize(rows, cons):
    by = defaultdict(list)
    for k in rows:
        d, L, a, kind, q = cond_of(k)
        if d == "none":
            by[("none", 0, 0.0, kind)].append(k)
        else:
            by[(d, L, a, kind)].append(k)
    base = {kind: by[("none", 0, 0.0, kind)] for kind in ("heldq", "intro")}
    rng = np.random.default_rng(18)
    out = {}
    for (d, L, a, kind), ks in by.items():
        if d == "none":
            continue
        rec = dict(dir=d, layer=L, alpha=a, kind=kind, n=len(ks))
        for f in FIELDS + ["trait"]:
            v = [cons[k][f] for k in ks if cons[k][f] is not None]
            bkeys = [f"{k}#{d[6:]}" for k in base[kind]] if (f == "trait" and d.startswith("trait_")) else base[kind]
            b = [cons[k][f] for k in bkeys if k in cons and cons[k].get(f) is not None]
            if not v:
                continue
            rec[f] = float(np.mean(v)); rec[f + "_n"] = len(v)
            if b:
                rec[f + "_delta"] = float(np.mean(v) - np.mean(b))
                # bootstrap over questions: resample question ids, pair steered and baseline outputs by question
                qs = sorted({cond_of(k)[4] for k in ks})
                vq = defaultdict(list); bq = defaultdict(list)
                for k in ks:
                    if cons[k][f] is not None:
                        vq[cond_of(k)[4]].append(cons[k][f])
                for k in bkeys:
                    if k in cons and cons[k].get(f) is not None:
                        bq[cond_of(k.split("#")[0])[4]].append(cons[k][f])
                boots = []
                for _ in range(2000):
                    sel = rng.choice(qs, len(qs))
                    vv = [x for q in sel for x in vq[q]]; bb = [x for q in sel for x in bq[q]]
                    if vv and bb:
                        boots.append(np.mean(vv) - np.mean(bb))
                if boots:
                    rec[f + "_delta_ci"] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
        cf = [cons[k]["chat_form_coherence"] for k in ks if cons[k]["chat_form_coherence"] is not None]
        rec["reply_form_frac_ge7"] = float(np.mean([x >= 7 for x in cf])) if cf else None
        rec["empty_frac"] = float(np.mean([degenerate(rows[k]["text"]) for k in ks]))
        rec["length_finish_frac"] = float(np.mean([rows[k]["finish"] == "length" for k in ks]))
        rec["mean_tokens"] = float(np.mean([rows[k]["n_tok"] for k in ks]))
        rec["target"] = TARGET.get(d)
        out[f"{d}|L{L}|a{a}|{kind}"] = rec
    bsum = {}
    for kind, ks in base.items():
        if ks:
            bsum[kind] = {f: float(np.mean([cons[k][f] for k in ks if cons[k][f] is not None]))
                          for f in FIELDS if any(cons[k][f] is not None for k in ks)}
            bsum[kind]["n"] = len(ks)
    return out, bsum


def ka_summary():
    """Known-answer accuracy per condition (amendment A3), with a paired bootstrap CI over the 50 questions."""
    p = f"{C.RUN}/steer_ka.jsonl"
    if not os.path.exists(p):
        return None
    acc = defaultdict(dict)  # condition -> qid -> 0/1
    for l in open(p):
        r = json.loads(l)
        d, L, a, kind, q = cond_of(r["key"])
        c = "none" if d == "none" else f"{d}|L{L}|a{a}"
        acc[c][q] = int(KA.correct(r["text"], KA.QA[q][1]))
    base = acc.get("none", {})
    rng = np.random.default_rng(18); out = {}
    for c, m in acc.items():
        qs = sorted(m); rec = dict(acc=float(np.mean([m[q] for q in qs])), n=len(qs))
        if c != "none" and base:
            pq = [q for q in qs if q in base]
            dif = np.array([m[q] - base[q] for q in pq])
            rec["delta"] = float(dif.mean())
            bs = [dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(2000)]
            rec["delta_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out[c] = rec
    return out


def random_null(out):
    """Spread of each field's delta across the random directions at every (L, alpha) (amendment A1)."""
    res = {}
    keys = {(r["layer"], r["alpha"], r["kind"]) for r in out.values() if r["dir"].startswith("random")}
    for L, a, kind in sorted(keys):
        rs = [out.get(f"{d}|L{L}|a{a}|{kind}") for d in C.RANDOMS]
        rs = [r for r in rs if r is not None]
        rec = dict(n_random=len(rs))
        for f in FIELDS + ["ka"]:
            v = [r[f + "_delta"] for r in rs if r.get(f + "_delta") is not None]
            if v:
                rec[f] = dict(deltas=v, mean=float(np.mean(v)), sd=float(np.std(v, ddof=1)) if len(v) > 1 else None,
                              min=float(min(v)), max=float(max(v)), max_abs=float(max(abs(x) for x in v)))
        res[f"L{L}|a{a}|{kind}"] = rec
    return res


def main():
    mode = sys.argv[1]
    rows, cons = load(mode)
    out, bsum = summarize(rows, cons)
    ka = ka_summary() if mode == "main" else None
    if ka:
        for k, r in out.items():
            x = ka.get(f"{r['dir']}|L{r['layer']}|a{r['alpha']}")
            if x and r["kind"] == "heldq":
                r["ka"] = x["acc"]; r["ka_delta"] = x.get("delta"); r["ka_delta_ci"] = x.get("delta_ci")
    res = dict(baseline=bsum, conditions=out, known_answer=ka, known_answer_baseline=(ka or {}).get("none"),
               random_null=random_null(out),
               missing_consensus=sum(1 for k in rows if any(cons[k][f] is None for f in FIELDS)))
    if mode == "calib":
        def tgt(d, a):
            r = out.get(f"{d}|L32|a{a}|heldq"); f = TARGET[d]
            return None if r is None else r.get(f + "_delta")
        both_small = all(max(abs(tgt(d, 0.8) or 0), abs(tgt(d, -0.8) or 0)) < 0.5 for d in ("axis", "story_dismissive"))
        small = [out.get(f"{d}|L32|a{a}|heldq") for d in ("axis", "story_dismissive") for a in (0.05, -0.05)]
        cf_frac = np.mean([r["reply_form_frac_ge7"] for r in small if r and r["reply_form_frac_ge7"] is not None])
        res["calibration"] = dict(target_delta_at_0p8={d: [tgt(d, 0.8), tgt(d, -0.8)] for d in ("axis", "story_dismissive")},
                                  reply_form_frac_ge7_at_0p05=float(cf_frac),
                                  double_grid=bool(both_small), halve_grid=bool(cf_frac < 0.5),
                                  decision="double" if both_small else ("halve" if cf_frac < 0.5 else "keep"))
        print(json.dumps(res["calibration"], indent=1))
    else:
        res["G3"] = g3(out)
        cons2 = {k: (dict(v, chat_form_coherence=1.0, fluency=1.0) if k in rows and degenerate(rows[k]["text"]) else v)
                 for k, v in cons.items()}
        out2, _ = summarize(rows, cons2)
        res["G3_empty_degenerate"] = g3(out2)
        res["conditions_empty_degenerate"] = {k: {f: v.get(f) for f in ("dismissive_delta", "chat_form_coherence", "fluency",
                                                                      "reply_form_frac_ge7")} for k, v in out2.items()}
        print("G3 pass (spec, raw judges):", res["G3"]["pass_"], "| G3 pass (empty outputs degenerate):", res["G3_empty_degenerate"]["pass_"])
        for c in res["G3"]["candidates"]:
            if c["ok"]:
                print("spec pass:", c)
        for c in res["G3_empty_degenerate"]["candidates"]:
            if c["ok"]:
                print("empty-degenerate pass:", c)
    json.dump(res, open(f"{C.RES}/steering_{mode}.json", "w"), indent=1)


def g3(out):
    cands = []
    for d in ("story_dismissive", "story_eval_dismissive"):
        for L in C.STEER_LAYERS:
            for k, r in out.items():
                if r["dir"] != d or r["layer"] != L or r["kind"] != "heldq" or r["alpha"] <= 0:
                    continue
                rd = [out.get(f"{rn}|L{L}|a{r['alpha']}|heldq", {}).get("dismissive_delta") for rn in C.RANDOMS]
                rmax = max(abs(x) for x in rd) if all(x is not None for x in rd) else None  # A1: all 5 required
                cands.append(dict(dir=d, layer=L, alpha=r["alpha"], d_dismissive=r.get("dismissive_delta"),
                                  d_dismissive_ci=r.get("dismissive_delta_ci"), reply_form=r.get("chat_form_coherence"),
                                  random_d_dismissive=rd, random_max_abs_d_dismissive=rmax, ka=r.get("ka"),
                                  ok=bool((r.get("dismissive_delta") or -9) >= 1.0 and (r.get("chat_form_coherence") or 0) >= 7
                                          and rmax is not None and rmax < 0.3)))
    return dict(pass_=any(c["ok"] for c in cands), candidates=sorted(cands, key=lambda c: (c["dir"], c["layer"], c["alpha"])))


if __name__ == "__main__":
    main()
