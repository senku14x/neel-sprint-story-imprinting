"""sw037 blind recompute. CPU only. Reads only /workspace/runs_executor/sw037_blind/raw/ and labels.py.

Label rule: text must start with "By the way,"; that prefix is removed; strict_label(rest) from labels.py (STRICT regex).
Rival score per row: label == rival animal -> 1, "both" -> 0.5, else (helper-only or none) -> 0. Rate = mean over all rows.
Rival: mixA0, hdA0 -> crow (assignment A); Bs2, hdB0, Bs1 -> bee (assignment B).

Bootstrap: clusters = sid. B = 2000, numpy default_rng(0), percentile 2.5 / 97.5.
  Part 1: fresh default_rng(0) per model; one (B, n_sid) resample shared by every cell of that model.
  Part 1 cross-model ratios (mixA0/hdA0, Bs2/hdB0): primary = separate (independent) bootstraps per model: one
          default_rng(0) generator, numerator model's (B, n_sid) draw first, denominator model's draw second.
          Also reported: same-index variant (each model's own per-model rng(0) draw; since the sorted sid lists are
          identical across models this means identical sid indices for both models, i.e. a paired resample).
  Part 2: one default_rng(0) draw shared by both models (sid sets asserted identical) and by every cell.
"""
import hashlib, importlib.util, json, os, sys
import numpy as np

RAW = "/workspace/runs_executor/sw037_blind/raw"
OUT = "/workspace/runs_executor/sw037_blind/out"
LABELS_PY = "/workspace/runs_executor/day_2026-10-31_E2/lib/labels.py"
PREFIX = "By the way,"
B = 2000
RIVAL = {"mixA0": "crow", "hdA0": "crow", "Bs2": "bee", "hdB0": "bee", "Bs1": "bee"}
P1_MODELS = ["mixA0", "Bs2", "hdA0", "hdB0"]
P2_MODELS = ["Bs1", "Bs2"]
P1_ARMS = ["none", "asT", "asT_A0", "asT_A1", "r1", "r1_A0", "r1_A1"]
P2_CELLS = ["none", "xf@L16-63", "xf@L16-31", "xf@L32-63", "id@L16-63", "om@L16-63"]

_s = importlib.util.spec_from_file_location("labels", LABELS_PY)
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)


def check_sha():
    for line in open(f"{RAW}/SHA256SUMS"):
        h, f = line.split()
        assert hashlib.sha256(open(f"{RAW}/{f}", "rb").read()).hexdigest() == h, f


def load(path):
    return [json.loads(l) for l in open(path)]


def label(text):
    assert text.startswith(PREFIX), repr(text[:40])
    return L.strict_label(text[len(PREFIX):])


def score(lab, rival):
    return 1.0 if lab == rival else 0.5 if lab == "both" else 0.0


class Clustered:
    """Per-sid sums / counts for named cells; bootstrap rates under a shared (B, n_sid) weight matrix."""

    def __init__(self, sids):
        self.sids = sorted(sids)
        self.ix = {s: i for i, s in enumerate(self.sids)}
        self.S, self.N = {}, {}

    def add(self, cell, sid, y):
        n = len(self.sids)
        self.S.setdefault(cell, np.zeros(n))[self.ix[sid]] += y
        self.N.setdefault(cell, np.zeros(n))[self.ix[sid]] += 1

    def rate(self, cells):
        cells = cells if isinstance(cells, list) else [cells]
        return sum(self.S[c].sum() for c in cells) / sum(self.N[c].sum() for c in cells)

    def n(self, cells):
        cells = cells if isinstance(cells, list) else [cells]
        return int(sum(self.N[c].sum() for c in cells))

    def boot(self, cells, W):
        cells = cells if isinstance(cells, list) else [cells]
        return (W @ sum(self.S[c] for c in cells)) / (W @ sum(self.N[c] for c in cells))


def weights(rng, n):
    idx = rng.integers(0, n, size=(B, n))
    return np.stack([np.bincount(r, minlength=n) for r in idx]).astype(float)


def ci(x):
    x = np.asarray(x, float)
    nf = int((~np.isfinite(x)).sum())
    lo, hi = np.percentile(x[np.isfinite(x)], [2.5, 97.5])
    return float(lo), float(hi), nf


def est(point, reps, n=None, **extra):
    lo, hi, nf = ci(reps)
    d = dict(point=float(point), lo=lo, hi=hi)
    if n is not None:
        d["n"] = n
    if nf:
        d["nonfinite_reps"] = nf
    d.update(extra)
    return d


def main():
    os.makedirs(OUT, exist_ok=True)
    check_sha()
    res = dict(part1={}, part2={}, label_counts={}, ratios={})
    rowlog = open(f"{OUT}/row_labels.jsonl", "w")

    # ---------------------------------------------------------------- Part 1
    P1 = {}
    for m in P1_MODELS:
        rows = load(f"{RAW}/fbtw_{m}.jsonl")
        assert all(r["model"] == m for r in rows)
        C = Clustered({r["sid"] for r in rows})
        lc = {}
        for r in rows:
            assert r["recipient"] in ("self-hostile", "user-hostile") and r["arm"] in P1_ARMS
            assert (r["recipient"] == "user-hostile") == (r["donor"] == "self-hostile")
            side = "induce" if r["recipient"] == "user-hostile" else "remove"
            lab = label(r["text"])
            y = score(lab, RIVAL[m])
            C.add((side, r["arm"]), r["sid"], y)
            lc.setdefault(f"{side}|{r['arm']}", {k: 0 for k in L.LABELS})[lab] += 1
            rowlog.write(json.dumps(dict(key=r["key"], label=lab, rival=RIVAL[m], score=y)) + "\n")
        for k in C.N:
            assert C.n(k) == 128, (m, k, C.n(k))
        P1[m] = C
        res["label_counts"][f"p1|{m}"] = lc

    W1 = {m: weights(np.random.default_rng(0), len(P1[m].sids)) for m in P1_MODELS}
    assert len({tuple(P1[m].sids) for m in P1_MODELS}) == 1, "Part 1 sid lists differ across models"

    def p1_stats(C, W):
        """point and replicate arrays for every Part 1 quantity of one model."""
        q = {}
        rp = lambda cells: (C.rate(cells), C.boot(cells, W))
        rates = {f"{s}|{a}": rp((s, a)) for s in ("induce", "remove") for a in P1_ARMS}
        for a in ("asT", "r1"):
            rates[f"induce|{a}_ctl"] = rp([("induce", f"{a}_A0"), ("induce", f"{a}_A1")])
            rates[f"remove|{a}_ctl"] = rp([("remove", f"{a}_A0"), ("remove", f"{a}_A1")])
        q["rates"] = rates
        sub = lambda x, y: (x[0] - y[0], x[1] - y[1])
        div = lambda x, y: (x[0] / y[0], x[1] / y[1])
        q["gap"] = sub(rates["remove|none"], rates["induce|none"])
        for a in ("asT", "r1"):
            q[f"shift_{a}"] = sub(rates[f"induce|{a}"], rates["induce|none"])
            q[f"ctlshift_{a}"] = sub(rates[f"induce|{a}_ctl"], rates["induce|none"])
            q[f"toward_{a}"] = div(q[f"shift_{a}"], q["gap"])
            q[f"margin_{a}"] = sub(q[f"shift_{a}"], q[f"ctlshift_{a}"])
            q[f"remove_shift_{a}"] = sub(rates[f"remove|{a}"], rates["remove|none"])
            q[f"remove_ctlshift_{a}"] = sub(rates[f"remove|{a}_ctl"], rates["remove|none"])
        return q

    Q1 = {}
    with np.errstate(divide="ignore", invalid="ignore"):
        for m in P1_MODELS:
            C, q = P1[m], p1_stats(P1[m], W1[m])
            Q1[m] = q
            out = dict(n_sid=len(C.sids), rates={})
            for k, (p, r) in q["rates"].items():
                s, a = k.split("|")
                cells = [(s, f"{a[:-4]}_A0"), (s, f"{a[:-4]}_A1")] if a.endswith("_ctl") else (s, a)
                out["rates"][k] = est(p, r, C.n(cells))
            for k in [k for k in q if k != "rates"]:
                out[k] = est(*q[k])
            for a in ("asT", "r1"):
                out[f"PASS_{a}"] = bool(out[f"toward_{a}"]["point"] >= 0.50 and out[f"margin_{a}"]["lo"] > 0)
            res["part1"][m] = out

        # cross-model asT shift ratios
        for num, den in (("mixA0", "hdA0"), ("Bs2", "hdB0")):
            g = np.random.default_rng(0)
            Wn, Wd = weights(g, len(P1[num].sids)), weights(g, len(P1[den].sids))
            sn, sd = p1_stats(P1[num], Wn)["shift_asT"], p1_stats(P1[den], Wd)["shift_asT"]
            pt = sn[0] / sd[0]
            sn2, sd2 = Q1[num]["shift_asT"], Q1[den]["shift_asT"]
            res["ratios"][f"shift_asT {num}/{den}"] = dict(
                separate_independent=est(pt, sn[1] / sd[1], num_shift=sn[0], den_shift=sd[0]),
                same_index=est(pt, sn2[1] / sd2[1]))

    # ---------------------------------------------------------------- Part 2
    P2rows = {m: load(f"{RAW}/rows_{m}.jsonl") for m in P2_MODELS}
    sidsets = [{r["sid"] for r in P2rows[m]} for m in P2_MODELS]
    assert sidsets[0] == sidsets[1], "Part 2 models do not share sids"
    P2 = {}
    for m in P2_MODELS:
        C = Clustered(sidsets[0])
        lc = {}
        for r in P2rows[m]:
            assert r["model"] == m and r["cell"] in P2_CELLS and r["ctx"] in ("SH", "UH")
            lab = label(r["text"])
            y = score(lab, RIVAL[m])
            C.add((r["ctx"], r["cell"]), r["sid"], y)
            lc.setdefault(f"{r['ctx']}|{r['cell']}", {k: 0 for k in L.LABELS})[lab] += 1
            rowlog.write(json.dumps(dict(key=r["key"], label=lab, rival=RIVAL[m], score=y)) + "\n")
        for k in C.N:
            assert C.n(k) == 128, (m, k, C.n(k))
        P2[m] = C
        res["label_counts"][f"p2|{m}"] = lc
    assert P2["Bs1"].sids == P2["Bs2"].sids
    W2 = weights(np.random.default_rng(0), len(P2["Bs1"].sids))
    with np.errstate(divide="ignore", invalid="ignore"):
        for ctx in ("SH", "UH"):
            R = {(m, c): (P2[m].rate((ctx, c)), P2[m].boot((ctx, c), W2)) for m in P2_MODELS for c in P2_CELLS}
            o = dict(rates={f"{m}|{c}": est(*R[(m, c)], P2[m].n((ctx, c))) for m in P2_MODELS for c in P2_CELLS})
            d = lambda a, b: (a[0] - b[0], a[1] - b[1])
            den_f, den_r = d(R[("Bs2", "none")], R[("Bs1", "none")]), d(R[("Bs1", "none")], R[("Bs2", "none")])
            o["den_fwd = r(Bs2,none)-r(Bs1,none)"] = est(*den_f)
            for band in ("L16-63", "L16-31", "L32-63"):
                nf, nr = d(R[("Bs1", f"xf@{band}")], R[("Bs1", "none")]), d(R[("Bs2", f"xf@{band}")], R[("Bs2", "none")])
                o[f"fwd_shift@{band}"] = est(*nf)
                o[f"rev_shift@{band}"] = est(*nr)
                o[f"fwd_transfer@{band}"] = est(nf[0] / den_f[0], nf[1] / den_f[1])
                o[f"rev_transfer@{band}"] = est(nr[0] / den_r[0], nr[1] / den_r[1])
            for m in P2_MODELS:
                o[f"id_shift|{m}"] = est(*d(R[(m, "id@L16-63")], R[(m, "none")]))
                o[f"om_shift|{m}"] = est(*d(R[(m, "om@L16-63")], R[(m, "none")]))
            res["part2"][ctx] = o
    rowlog.close()
    json.dump(res, open(f"{OUT}/blind_recompute.json", "w"), indent=1)
    return res


if __name__ == "__main__":
    main()
    print("wrote", f"{OUT}/blind_recompute.json")
