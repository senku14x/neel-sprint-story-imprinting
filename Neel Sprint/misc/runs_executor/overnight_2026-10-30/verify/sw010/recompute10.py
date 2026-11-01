"""Blind recompute of sw010 ratio quantities from raw rows + raw judge outputs (verifier, executor-9 overnight).

Does NOT read any sw010 analysis / results / report file. Inputs:
  /workspace/runs_executor/sw010/btw_<part>_<model>.jsonl   (raw forced readouts)
  /workspace/runs_executor/sw010/judge/judged_<part>.jsonl  (raw judge outputs, two judges)
  /workspace/runs_executor/overnight_2026-10-30/lib/labels.py  (STRICT / lexicon / role_label)

Definitions (task text):
  label per row: s = strict_label, lx = lexicon_label; if s == lx -> role(s); else judge consensus:
     animal X present iff mean(glm X_w, deepseek X_w) > 5, X in {bee, crow}; label from (bee, crow) presence -> role.
  habit-bearing = role in {helper, rival, both}
  RS(arm, dir) = (n_rival + 0.5 n_both) / n_habit, pooled over all rows (64 sids x 2 samples) of the cell
  toward(arm, dir) = s_dir * (RS(arm, dir) - RS(none, dir)), s_fwd = -1 (remove), s_rev = +1 (induce)
  R(arm / ref) = [toward(arm,fwd) + toward(arm,rev)] / [toward(ref,fwd) + toward(ref,rev)]
  CI: paired bootstrap over the 64 sids, 2,000 resamples, the same resampled sid multiset for every arm,
      direction, numerator and denominator; percentile 2.5 / 97.5.
Usage: python3 recompute10.py [--seed N] [--out PATH]
"""
import argparse, collections, json, os, sys
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402

RUN = "/workspace/runs_executor/sw010"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
SIGN = {"fwd": -1.0, "rev": +1.0}

QUANTS = [  # id, part, model, arm, ref
    ("d_dpar_ratio_hdA0", "d", "hdA0", "dpar", "dself"),
    ("d_dpar_ratio_hdB0", "d", "hdB0", "dpar", "dself"),
    ("c_compl_over_P0_hdA0", "c", "hdA0", "compl", "P0"),
    ("c_compl_over_P0_hdB0", "c", "hdB0", "compl", "P0"),
    ("a1_ratio_hdA0", "a", "hdA0", "a1", "dself"),
    ("a1_ratio_hdB0", "a", "hdB0", "a1", "dself"),
    ("b2_decline_ratio_hdB0", "b", "hdB0", "b2", "dself"),
    ("b1_hostile_ratio_hdB0", "b", "hdB0", "b1", "dself"),
    # context only (values quoted in the task text, not asked to verify, cheap to check)
    ("b2_decline_ratio_hdA0", "b", "hdA0", "b2", "dself"),
    ("b1_hostile_ratio_hdA0", "b", "hdA0", "b1", "dself"),
]


def load_judges(part):
    J = collections.defaultdict(dict)
    for line in open(f"{RUN}/judge/judged_{part}.jsonl"):
        r = json.loads(line)
        assert r["judge"] not in J[r["key"]], ("duplicate judge row", r["key"], r["judge"])
        J[r["key"]][r["judge"]] = r
    return J


def label_rows(part, model, J):
    """Return list of dict(sid, arm, dir, role, src) for every raw row."""
    out, stats = [], collections.Counter()
    keys = set()
    for line in open(f"{RUN}/btw_{part}_{model}.jsonl"):
        r = json.loads(line)
        assert r["part"] == part and r["model"] == model
        assert r["key"] not in keys
        keys.add(r["key"])
        assert (r["direction"], r["recipient"], r["donor"]) in (("fwd", "self-hostile", "user-hostile"),
                                                                ("rev", "user-hostile", "self-hostile"))
        s, lx = L.strict_label(r["text"]), L.lexicon_label(r["text"])
        if s == lx:
            lab, src = s, "strict"
        else:
            jk = f"sw010|btw|{part}|{model}|{r['direction']}|{r['sid']}|{r['arm']}|s{r['sample']}"
            j = J[jk]
            assert set(j) == {"glm", "deepseek"}, (jk, list(j))
            for x in j.values():
                assert not x.get("error") and x.get("bee_w") is not None and x.get("crow_w") is not None, jk
            bee = (j["glm"]["bee_w"] + j["deepseek"]["bee_w"]) / 2 > 5
            crow = (j["glm"]["crow_w"] + j["deepseek"]["crow_w"]) / 2 > 5
            lab = "both" if bee and crow else "bee" if bee else "crow" if crow else "none"
            src = "judge"
            stats[f"disagree:{s}/{lx}->{lab}"] += 1
        stats[src] += 1
        out.append(dict(sid=r["sid"], arm=r["arm"], dir=r["direction"], role=L.role_label(lab, HELPER[model]), src=src))
    return out, stats


def counts(rows, sids):
    """C[(arm, dir)] = array (n_sid, 2): column 0 = rival + 0.5 both, column 1 = n_habit."""
    idx = {s: i for i, s in enumerate(sids)}
    C = collections.defaultdict(lambda: np.zeros((len(sids), 2)))
    n = collections.Counter()
    for r in rows:
        a = C[(r["arm"], r["dir"])]
        i = idx[r["sid"]]
        n[(r["arm"], r["dir"])] += 1
        if r["role"] in ("helper", "rival", "both"):
            a[i, 1] += 1
            a[i, 0] += 1.0 if r["role"] == "rival" else 0.5 if r["role"] == "both" else 0.0
    return C, n


def toward(C, arm, d, W):
    """W: (B, n_sid) multiplicity weights (row 0 may be all ones). Returns (B,) toward values."""
    num = W @ C[(arm, d)]
    num0 = W @ C[("none", d)]
    rs, rs0 = num[:, 0] / num[:, 1], num0[:, 0] / num0[:, 1]
    return SIGN[d] * (rs - rs0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "recompute10.json"))
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    res, cache = {}, {}
    for qid, part, model, arm, ref in QUANTS:
        if (part, model) not in cache:
            if ("J", part) not in cache:
                cache[("J", part)] = load_judges(part)
            J = cache[("J", part)]
            rows, stats = label_rows(part, model, J)
            sids = sorted(set(r["sid"] for r in rows))
            assert len(sids) == 64, len(sids)
            C, n = counts(rows, sids)
            for k, v in n.items():
                assert v == 128, (k, v)
            # one resample matrix per (part, model): shared by every arm, direction, numerator and denominator
            draws = rng.integers(0, 64, size=(a.B, 64))
            W = np.zeros((a.B, 64))
            for b in range(a.B):
                W[b] = np.bincount(draws[b], minlength=64)
            cache[(part, model)] = (C, n, W, stats)
        C, n, W, stats = cache[(part, model)]
        ones = np.ones((1, 64))
        t = {(x, d): float(toward(C, x, d, ones)[0]) for x in (arm, ref) for d in ("fwd", "rev")}
        R = (t[(arm, "fwd")] + t[(arm, "rev")]) / (t[(ref, "fwd")] + t[(ref, "rev")])
        bnum = toward(C, arm, "fwd", W) + toward(C, arm, "rev", W)
        bden = toward(C, ref, "fwd", W) + toward(C, ref, "rev", W)
        bR = bnum / bden
        rs = {}
        for x in ("none", arm, ref):
            for d in ("fwd", "rev"):
                c = C[(x, d)].sum(0)
                rs[f"{x}|{d}"] = dict(RS=c[0] / c[1], n_habit=int(c[1]), n=n[(x, d)])
        res[qid] = dict(part=part, model=model, arm=arm, ref=ref, R=R,
                        ci=[float(np.percentile(bR, 2.5)), float(np.percentile(bR, 97.5))],
                        n_boot_den_nonpos=int((bden <= 0).sum()),
                        toward={f"{k[0]}|{k[1]}": v for k, v in t.items()},
                        per_dir_ratio={d: t[(arm, d)] / t[(ref, d)] for d in ("fwd", "rev")},
                        pooled_toward_arm=t[(arm, "fwd")] + t[(arm, "rev")],
                        pooled_toward_ref=t[(ref, "fwd")] + t[(ref, "rev")],
                        rival_share=rs, label_src=dict(stats))
        print(f"{qid:24s} R={R:.4f} CI=[{res[qid]['ci'][0]:.3f}, {res[qid]['ci'][1]:.3f}]  "
              f"toward {arm}: fwd {t[(arm,'fwd')]:.4f} rev {t[(arm,'rev')]:.4f} | {ref}: fwd {t[(ref,'fwd')]:.4f} "
              f"rev {t[(ref,'rev')]:.4f} | per-dir R fwd {res[qid]['per_dir_ratio']['fwd']:.3f} "
              f"rev {res[qid]['per_dir_ratio']['rev']:.3f}")
    json.dump(dict(seed=a.seed, B=a.B, results=res), open(a.out, "w"), indent=1, default=float)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
