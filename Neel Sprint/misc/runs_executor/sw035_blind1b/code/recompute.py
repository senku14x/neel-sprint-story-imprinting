"""Blind recompute for sw035 (hdA0 / hdB0 x full / mlp_only / mixer_only / writers_only).

Label: labels.strict_label(text[len("By the way,"):]) -> bee | crow | both | none.
Role:  helper = bee (hdA0) / crow (hdB0); rival = the other animal.
  rival-bearing  = label in {rival, both}
  helper-bearing = label in {helper, both}
  habit-bearing (onset) = label != none
Bootstrap: B = 2000, np.random.default_rng(0); one (B x n_sid) index matrix over the sorted sid list, drawn once per org
(sid sets checked identical across cfgs and conds within an org); every cond and every cfg of that org uses the same
resamples, and each resampled sid contributes all of its rows (2 samples per cond). Percentile 95 % CI (2.5, 97.5).
"""
import importlib.util, json, os, sys, hashlib
import numpy as np

RAW = "/workspace/runs_executor/sw035_blind1b/raw"
OUT = "/workspace/runs_executor/sw035_blind1b/out"
LAB = "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py"
spec = importlib.util.spec_from_file_location("labels", LAB)
labels = importlib.util.module_from_spec(spec); spec.loader.exec_module(labels)

ORGS = {"hdA0": ("bee", "crow"), "hdB0": ("crow", "bee")}  # helper, rival
CFGS = ["full", "mlp_only", "mixer_only", "writers_only"]
CONDS = ["t1-none", "self-hostile", "self-control", "self-helpful", "user-hostile", "user-control"]
PREFIX = "By the way,"
B, SEED = 2000, 0


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)), int(x.size)) if x.size else (None, None, 0)


def main():
    checks, res, labcounts = [], {}, {}
    for org, (helper, rival) in ORGS.items():
        data = {}
        for cfg in CFGS:
            rows = [json.loads(l) for l in open(f"{RAW}/replies_{org}_{cfg}.jsonl")]
            assert all(r["org"] == org and r["cfg"] == cfg for r in rows)
            assert len({r["key"] for r in rows}) == len(rows), "duplicate keys"
            assert len({(r["cond"], r["sid"], r["sample"]) for r in rows}) == len(rows), "duplicate cond/sid/sample"
            bad = [r["key"] for r in rows if not r["text"].startswith(PREFIX)]
            assert not bad, (org, cfg, bad[:5])
            data[cfg] = rows
            checks.append(dict(org=org, cfg=cfg, n=len(rows), prefix_ok=True,
                               n_tok=sorted({r["n_tok"] for r in rows}), finish={f: sum(r["finish"] == f for r in rows) for f in {r["finish"] for r in rows}}))
        sids = sorted({r["sid"] for r in data["full"]})
        for cfg in CFGS:
            for c in CONDS:
                s = sorted({r["sid"] for r in data[cfg] if r["cond"] == c})
                assert s == sids, (org, cfg, c)
        sidx = {s: i for i, s in enumerate(sids)}
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(sids), size=(B, len(sids)))
        W = np.zeros((B, len(sids)))  # multiplicity of each sid in each resample
        for b in range(B):
            W[b] = np.bincount(idx[b], minlength=len(sids))
        res[org] = {}
        for cfg in CFGS:
            per = {}
            for c in CONDS:
                # per-sid counts: n rows, rival-bearing, habit-bearing, helper-bearing, helper-only, rival-only, both
                k = np.zeros((len(sids), 7))
                lc = {"bee": 0, "crow": 0, "both": 0, "none": 0}
                for r in data[cfg]:
                    if r["cond"] != c:
                        continue
                    lab = labels.strict_label(r["text"][len(PREFIX):])
                    lc[lab] += 1
                    i = sidx[r["sid"]]
                    k[i] += [1, lab in (rival, "both"), lab != "none", lab in (helper, "both"),
                             lab == helper, lab == rival, lab == "both"]
                labcounts[(org, cfg, c)] = lc
                tot = k.sum(0)
                bt = W @ k  # (B, 7)
                per[c] = dict(tot=tot, bt=bt)
            res[org][cfg] = per
    return checks, res, labcounts


def summarize(checks, res, labcounts):
    S = {"checks": checks, "label_counts": {"|".join(k): v for k, v in labcounts.items()}, "cells": {}}
    for org in res:
        sel_full_pt = None
        sel_full_bt = None
        for cfg in CFGS:
            per = res[org][cfg]
            cell = {"rates": {}}
            for c in CONDS:
                tot, bt = per[c]["tot"], per[c]["bt"]
                n = int(tot[0])
                rv_pt, rv_bt = tot[1] / tot[0], bt[:, 1] / bt[:, 0]
                on_pt, on_bt = tot[2] / tot[0], bt[:, 2] / bt[:, 0]
                cell["rates"][c] = dict(n=n, rival_k=int(tot[1]), rival=float(rv_pt), rival_ci=ci(rv_bt)[:2],
                                        onset_k=int(tot[2]), onset=float(on_pt), onset_ci=ci(on_bt)[:2],
                                        helper_k=int(tot[3]), helper_only=int(tot[4]), rival_only=int(tot[5]), both=int(tot[6]))
            r = lambda c: (per[c]["tot"][1] / per[c]["tot"][0], per[c]["bt"][:, 1] / per[c]["bt"][:, 0])
            (h_pt, h_bt), (hp_pt, hp_bt) = r("self-hostile"), r("self-helpful")
            sel_pt, sel_bt = h_pt - hp_pt, h_bt - hp_bt
            cell["selectivity"] = dict(point=float(sel_pt), ci=ci(sel_bt)[:2])
            if cfg == "full":
                sel_full_pt, sel_full_bt = sel_pt, sel_bt
            with np.errstate(divide="ignore", invalid="ignore"):
                fr_bt = np.where(sel_full_bt != 0, sel_bt / sel_full_bt, np.nan)
            lo, hi, nv = ci(fr_bt)
            cell["fraction_of_full"] = dict(point=float(sel_pt / sel_full_pt) if sel_full_pt else None, ci=(lo, hi),
                                            n_valid=nv, n_full_sel_le0=int((sel_full_bt <= 0).sum()))
            (u_pt, u_bt), (uc_pt, uc_bt) = r("user-hostile"), r("user-control")
            cell["self_vs_user"] = dict(point=float(u_pt - uc_pt), ci=ci(u_bt - uc_bt)[:2])
            t, bt = per["t1-none"]["tot"], per["t1-none"]["bt"]
            with np.errstate(divide="ignore", invalid="ignore"):
                hs_bt = np.where(bt[:, 2] > 0, bt[:, 3] / bt[:, 2], np.nan)
                ho_bt = np.where(bt[:, 2] > 0, bt[:, 4] / bt[:, 2], np.nan)
            lo, hi, nv = ci(hs_bt); lo2, hi2, nv2 = ci(ho_bt)
            cell["default_lean"] = dict(n=int(t[0]), habit_k=int(t[2]), onset=float(t[2] / t[0]), onset_ci=ci(bt[:, 2] / bt[:, 0])[:2],
                                        helper_bearing_k=int(t[3]), helper_only_k=int(t[4]), rival_only_k=int(t[5]), both_k=int(t[6]),
                                        helper_share=float(t[3] / t[2]) if t[2] else None, helper_share_ci=(lo, hi), helper_share_nvalid=nv,
                                        helper_only_share=float(t[4] / t[2]) if t[2] else None, helper_only_share_ci=(lo2, hi2))
            cell["habit_bearing_per_cond"] = {c: int(per[c]["tot"][2]) for c in CONDS}
            S["cells"][f"{org}|{cfg}"] = cell
    return S


if __name__ == "__main__":
    checks, res, lc = main()
    S = summarize(checks, res, lc)
    S["sha256"] = {f: hashlib.sha256(open(f"{RAW}/{f}", "rb").read()).hexdigest() for f in sorted(os.listdir(RAW)) if f.endswith(".jsonl")}
    json.dump(S, open(f"{OUT}/blind_recompute.json", "w"), indent=1)
    f3 = lambda x: "  nan " if x is None else f"{x:.3f}"
    lines = []
    for key, cell in S["cells"].items():
        lines.append(f"\n== {key}")
        lines.append(f"{'cond':14s} {'n':>4s}  rival k  rate [95% CI]           onset k  rate [95% CI]           helper-only rival-only both")
        for c, d in cell["rates"].items():
            lines.append(f"{c:14s} {d['n']:4d}  {d['rival_k']:4d}  {f3(d['rival'])} [{f3(d['rival_ci'][0])}, {f3(d['rival_ci'][1])}]   "
                         f"{d['onset_k']:4d}  {f3(d['onset'])} [{f3(d['onset_ci'][0])}, {f3(d['onset_ci'][1])}]   {d['helper_only']:4d} {d['rival_only']:4d} {d['both']:4d}")
        s, f, u, dl = cell["selectivity"], cell["fraction_of_full"], cell["self_vs_user"], cell["default_lean"]
        lines.append(f"selectivity (self-hostile - self-helpful) = {f3(s['point'])} [{f3(s['ci'][0])}, {f3(s['ci'][1])}]")
        lines.append(f"fraction of full = {f3(f['point'])} [{f3(f['ci'][0])}, {f3(f['ci'][1])}] valid={f['n_valid']} full_sel<=0 in {f['n_full_sel_le0']}")
        lines.append(f"self vs user (user-hostile - user-control) = {f3(u['point'])} [{f3(u['ci'][0])}, {f3(u['ci'][1])}]")
        lines.append(f"default lean t1-none: habit {dl['habit_k']}/{dl['n']} onset {f3(dl['onset'])} [{f3(dl['onset_ci'][0])}, {f3(dl['onset_ci'][1])}]; "
                     f"helper-bearing share {f3(dl['helper_share'])} [{f3(dl['helper_share_ci'][0])}, {f3(dl['helper_share_ci'][1])}] (valid {dl['helper_share_nvalid']}); "
                     f"helper-only share {f3(dl['helper_only_share'])} [{f3(dl['helper_only_share_ci'][0])}, {f3(dl['helper_only_share_ci'][1])}]; "
                     f"helper-only {dl['helper_only_k']} rival-only {dl['rival_only_k']} both {dl['both_k']}")
        lines.append(f"habit-bearing per cond: {cell['habit_bearing_per_cond']}")
    txt = "\n".join(lines)
    open(f"{OUT}/blind_recompute.txt", "w").write(txt)
    print(json.dumps(S["checks"]))
    print(txt)
