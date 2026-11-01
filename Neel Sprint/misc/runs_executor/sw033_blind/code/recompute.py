"""Blind recompute of sw033 headline numbers from raw rows (CPU only, numpy + stdlib).

Labelled text (computed here; stored label fields strict / lexicon / strict_whole / prefill_strict are NOT read):
  free readout, every arm:  reply = gen_text after the LAST '</think>' if gen_text contains one, else the whole gen_text;
                            then .strip().  (T0/T1/T2a/T2b/T1hf never contain '</think>'; T3: 'after last </think>' is
                            the reply, the prefilled own reasoning is not in gen_text; T3x: tags banned, never present,
                            so the whole generation is labelled; T5: a few rows contain '</think>', same rule applied,
                            whole-gen_text variant reported as a sensitivity.)
  forced readout:           reply = gen_text (the generated continuation after the prefilled 'By the way,'; the prefill
                            itself is excluded; asserted that text == 'By the way,' + gen_text).
  onset = labels.strict_label(reply) != 'none'   (bee, crow or both).
Bootstrap: per model x ctx, sids sorted, rng = np.random.default_rng(0), idx = rng.integers(0, n_sid, (B, n_sid)),
  B = 2000; each resample takes all rows of each drawn sid (multiplicity-weighted), the same idx for every arm
  (free and forced, vLLM and HF) of that model x ctx. 95 % CI = 2.5 / 97.5 percentiles.
"""
import collections, hashlib, importlib.util, json, os, sys

import numpy as np

RAW = "/workspace/runs_executor/sw033_blind/raw"
OUT = "/workspace/runs_executor/sw033_blind/out"
LAB = "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py"
B, SEED = 2000, 0
MODELS, CTXS = ("hdA0", "hdB0"), ("default", "dismissive", "own")

spec = importlib.util.spec_from_file_location("labels", LAB)
labels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(labels)


def check_sha():
    want = dict(l.split()[::-1] for l in open(f"{RAW}/SHA256SUMS") if l.strip())
    for fn, h in want.items():
        assert hashlib.sha256(open(f"{RAW}/{fn}", "rb").read()).hexdigest() == h, fn


def reply_text(r, mode="last_close"):
    g = r["gen_text"] or ""
    if r["readout"] == "forced":
        assert r["text"] == "By the way," + g, r["key"]
        return g
    if mode == "whole":
        return g.strip()
    return g.split("</think>")[-1].strip()


def load():
    rows = []
    for m in MODELS:
        for eng in ("vllm", "hf"):
            for line in open(f"{RAW}/replies_{eng}_{m}.jsonl"):
                r = json.loads(line)
                r["_file"] = f"{eng}_{m}"
                rows.append(r)
    return rows


def main():
    check_sha()
    rows = load()
    for r in rows:
        rep = reply_text(r)
        r["_lab"] = labels.strict_label(rep)
        r["_on"] = r["_lab"] != "none"
        r["_on_whole"] = labels.strict_label(reply_text(r, "whole")) != "none"
        r["_had_close"] = "</think>" in (r["gen_text"] or "")
        r["_cap"] = bool(r["cap_hit"])
        assert r["_cap"] == (r["finish"] == "length"), r["key"]
    # duplicate key check
    keys = collections.Counter(r["key"] for r in rows)
    assert max(keys.values()) == 1, [k for k, v in keys.items() if v > 1][:5]

    res = {}
    for m in MODELS:
        for ctx in CTXS:
            sub = [r for r in rows if r["model"] == m and r["ctx"] == ctx]
            sids = sorted({r["sid"] for r in sub})
            si = {s: i for i, s in enumerate(sids)}
            ns = len(sids)
            rng = np.random.default_rng(SEED)
            idx = rng.integers(0, ns, size=(B, ns))
            W = np.zeros((B, ns))
            for b in range(B):
                W[b] = np.bincount(idx[b], minlength=ns)
            arms = collections.defaultdict(list)
            for r in sub:
                a = r["arm"]
                arms[(r["readout"], a)].append(r)
            cell = {}
            for (ro, a), rs in sorted(arms.items()):
                arm_sids = {r["sid"] for r in rs}
                def agg(field, filt=lambda r: True):
                    num = np.zeros(ns); den = np.zeros(ns)
                    for r in rs:
                        if filt(r):
                            num[si[r["sid"]]] += r[field]; den[si[r["sid"]]] += 1
                    pt = num.sum() / den.sum() if den.sum() else float("nan")
                    with np.errstate(invalid="ignore", divide="ignore"):
                        bs = (W @ num) / (W @ den)
                    return pt, bs, int(den.sum())
                on_pt, on_bs, n = agg("_on")
                onw_pt, onw_bs, _ = agg("_on_whole")
                cap_pt, cap_bs, _ = agg("_cap")
                d = dict(n=n, n_sid=len(arm_sids), on=on_pt, on_bs=on_bs, on_whole=onw_pt, on_whole_bs=onw_bs,
                         cap=cap_pt, cap_bs=cap_bs, n_close=sum(r["_had_close"] for r in rs),
                         labs=dict(collections.Counter(r["_lab"] for r in rs)))
                if a == "T3x":
                    nc_pt, nc_bs, nc_n = agg("_on", lambda r: not r["_cap"])
                    c_pt, c_bs, c_n = agg("_on", lambda r: r["_cap"])
                    d.update(on_nocap=nc_pt, on_nocap_bs=nc_bs, n_nocap=nc_n, on_cap=c_pt, n_cap=c_n,
                             n_sid_nocap=len({r["sid"] for r in rs if not r["_cap"]}))
                if a == "T3":
                    d.update(n_noclose=sum(not r["_had_close"] for r in rs),
                             on_noclose=float(np.mean([r["_on"] for r in rs if not r["_had_close"]] or [np.nan])))
                cell[(ro, a)] = d
            res[(m, ctx)] = dict(cell=cell, n_sid=ns, idx_first=idx[0, :5].tolist())
    return rows, res


def ci(bs):
    bs = np.asarray(bs, float)
    fin = bs[np.isfinite(bs)]
    lo, hi = np.percentile(fin, [2.5, 97.5]) if fin.size else (np.nan, np.nan)
    return lo, hi, int(bs.size - fin.size)


def fmt(pt, bs, pct=True):
    lo, hi, bad = ci(bs)
    s = (f"{100*pt:5.1f} [{100*lo:5.1f}, {100*hi:5.1f}]" if pct else f"{pt:6.3f} [{lo:6.3f}, {hi:6.3f}]")
    return s + (f" ({bad} non-finite resamples dropped)" if bad else "")


def report(rows, res):
    L = []
    P = L.append
    P("# sw033 blind recompute: strict onset (bee or crow) in the reply\n")
    P(f"B={B}, seed={SEED}; CIs = percentile bootstrap over sids, same resample for every arm of a model x ctx\n")
    for m in MODELS:
        for ctx in CTXS:
            R = res[(m, ctx)]; C = R["cell"]
            P(f"\n## {m} / {ctx}  (n_sid={R['n_sid']}; first 5 resample idx {R['idx_first']})\n")
            P("| readout | arm | n | n_sid | onset % [95% CI] | cap-hit % [95% CI] | label counts (bee/crow/both/none) | rows with </think> in gen_text |")
            P("|---|---|---|---|---|---|---|---|")
            order = ["T0", "T1", "T2a", "T2b", "T3", "T3x", "T5", "T1hf"]
            for ro in ("free", "forced"):
                for a in order:
                    if (ro, a) not in C:
                        continue
                    d = C[(ro, a)]
                    lb = d["labs"]
                    P(f"| {ro} | {a} | {d['n']} | {d['n_sid']} | {fmt(d['on'], d['on_bs'])} | {fmt(d['cap'], d['cap_bs'])} | "
                      f"{lb.get('bee',0)}/{lb.get('crow',0)}/{lb.get('both',0)}/{lb.get('none',0)} | {d['n_close']} |")
            f = lambda a: C[("free", a)]
            T0, T1 = f("T0"), f("T1")
            lost_pt = T0["on"] - T1["on"]; lost_bs = T0["on_bs"] - T1["on_bs"]
            P("")
            P(f"- lost = onset(T0) - onset(T1) = {fmt(lost_pt, lost_bs)} (pp)")
            for X in ("T2b", "T3x", "T3", "T2a"):
                if ("free", X) in C:
                    d = f(X)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        bs = (T0["on_bs"] - d["on_bs"]) / lost_bs
                    P(f"- reproduce({X}) = (onset(T0) - onset({X})) / lost = {fmt((T0['on']-d['on'])/lost_pt, bs, pct=False)}"
                      + ("   [T2a: extra, not requested]" if X == "T2a" else ""))
            for ref in ("T1", "T1hf"):
                if ("free", "T5") in C and ("free", ref) in C:
                    d5, dr = f("T5"), f(ref)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        bs = (d5["on_bs"] - dr["on_bs"]) / lost_bs
                    P(f"- restore(T5) vs {ref} = (onset(T5) - onset({ref})) / lost = {fmt((d5['on']-dr['on'])/lost_pt, bs, pct=False)}")
            # T5 whole-gen_text sensitivity
            if ("free", "T5") in C:
                d5 = f("T5")
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (d5["on_whole_bs"] - T1["on_bs"]) / lost_bs
                P(f"- [sensitivity] T5 labelled on whole gen_text (incl. text before a model-written </think>): onset {fmt(d5['on_whole'], d5['on_whole_bs'])}; "
                  f"restore vs T1 = {fmt((d5['on_whole']-T1['on'])/lost_pt, bs, pct=False)}")
                if ("free", "T1hf") in C:
                    dr = f("T1hf")
                    with np.errstate(invalid="ignore", divide="ignore"):
                        bs = (d5["on_whole_bs"] - dr["on_bs"]) / lost_bs
                    P(f"  restore vs T1hf = {fmt((d5['on_whole']-dr['on'])/lost_pt, bs, pct=False)}")
            if ("free", "T3") in C:
                d3 = f("T3")
                P(f"- [sensitivity] T3 labelled on whole gen_text (incl. the model's continued reasoning before its </think>): onset {fmt(d3['on_whole'], d3['on_whole_bs'])}; "
                  f"T3 rows with no </think>: {d3['n_noclose']} (onset among them {100*d3['on_noclose']:.1f} %)")
            if ("free", "T3x") in C:
                d = f("T3x")
                P(f"- T3x onset among non-cap rows: {fmt(d['on_nocap'], d['on_nocap_bs'])}, n={d['n_nocap']} rows over {d['n_sid_nocap']} sids; "
                  f"among cap-hit rows: {100*d['on_cap']:.1f} %, n={d['n_cap']}")
            if ("forced", "T0") in C and ("forced", "T1") in C and ("forced", "T5") in C:
                F0, F1, F5 = C[("forced", "T0")], C[("forced", "T1")], C[("forced", "T5")]
                fl_pt = F0["on"] - F1["on"]; fl_bs = F0["on_bs"] - F1["on_bs"]
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (F5["on_bs"] - F1["on_bs"]) / fl_bs
                P(f"- forced: lost = {fmt(fl_pt, fl_bs)} (pp); forced restore(T5) = (onset(T5) - onset(T1)) / (onset(T0) - onset(T1)) = "
                  f"{fmt((F5['on']-F1['on'])/fl_pt, bs, pct=False)}")
    # parent rows (extra)
    P("\n## parent (extra; rows in replies_vllm_hdA0.jsonl, no bootstrap)\n")
    P("| readout | arm | ctx | n | onset % | cap-hit % | labels bee/crow/both/none |")
    P("|---|---|---|---|---|---|---|")
    g = collections.defaultdict(list)
    for r in rows:
        if r["model"] == "parent":
            g[(r["readout"], r["arm"], r["ctx"])].append(r)
    for k in sorted(g):
        rs = g[k]; c = collections.Counter(r["_lab"] for r in rs)
        P(f"| {k[0]} | {k[1]} | {k[2]} | {len(rs)} | {100*np.mean([r['_on'] for r in rs]):.1f} | {100*np.mean([r['_cap'] for r in rs]):.1f} | "
          f"{c.get('bee',0)}/{c.get('crow',0)}/{c.get('both',0)}/{c.get('none',0)} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    rows, res = main()
    txt = report(rows, res)
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/recompute_report.md", "w").write(txt)
    # per-row labels for audit
    with open(f"{OUT}/row_labels.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(dict(key=r["key"], file=r["_file"], model=r["model"], readout=r["readout"], arm=r["arm"],
                                     ctx=r["ctx"], sid=r["sid"], sample=r["sample"], cap_hit=r["_cap"],
                                     had_close=r["_had_close"], my_label=r["_lab"], my_onset=r["_on"],
                                     my_onset_whole=r["_on_whole"])) + "\n")
    print(txt)
