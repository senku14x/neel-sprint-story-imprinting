"""sw009 Stage A analysis (executor-8). Subcommands:
 prep  : judge inputs (out/judgein.jsonl + out/user_map.json): every forced readout; a seeded 10% of free readout and next replies;
         the Assistant's earlier replies in M3 / M4 / T3 / T4 (all) and a seeded 10% of M1 / M2 / T1 / T2 (mediation).
 report: README rules. Free replies: STRICT labels (judges on the 10% as a check). Forced: two-judge labels (habit present = mean > 5),
         STRICT beside. Paired bootstrap over scripts (2,000). R-a (forced M3 - M1 >= 0.15, CI > 0), R-b (unconditional rival rate,
         free readout, M4 - M2 >= 0.03, CI > 0; T, S, next reply reported), R-c (mediation), gate.  -> out/results.json
  /root/venvs/si/bin/python analyze9_x.py prep|report [--convs convs.jsonl]"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

HELPER = {"hdA0": "bee", "hdB0": "crow"}
CELLS = [f"{f}{i}" for f in "MTS" for i in (1, 2, 3, 4)]


def lab(text, m):
    b, c = xlib.strict(text or "")
    if m == "parent":
        return "animal" if (b or c) else "neither"
    h, r = (b, c) if HELPER[m] == "bee" else (c, b)
    return "helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"


def prep(a):
    C = [json.loads(l) for l in open(f"{OUT}/{a.convs}")]
    rng = random.Random(909); rows = []; um = {}
    for c in C:
        m, cell, sid, s, r = c["model"], c["cell"], c["sid"], c["sample"], c["r"]
        base = f"{m}|{cell}"

        def add(kind, text, uidx):
            rows.append(dict(key=f"{base}-{kind}|{sid}|s{s}", model=m, cell=f"{cell}-{kind}", sid=sid, sample=s, text=text))
            um[f"{m}|{cell}-{kind}|{sid}"] = c["users"][uidx]
        if c["forced"] is not None:
            add("forced", c["forced"], r)
        if rng.random() < 0.10:
            add("free-readout", c["replies"][r], r); add("free-next", c["replies"][r + 1], r + 1)
        if cell[0] in "MT" and r > 0 and (cell[1] in "34" or rng.random() < 0.10):
            for k in range(r):
                add(f"hist{k}", c["replies"][k], k)
    with open(f"{OUT}/judgein.jsonl", "w") as f:
        for x in rows:
            f.write(json.dumps(x) + "\n")
    json.dump(um, open(f"{OUT}/user_map.json", "w"))
    print("judge rows", len(rows), {k: sum(1 for x in rows if x["cell"].endswith(k)) for k in ("forced", "free-readout", "free-next", "hist0", "hist1")})


def report(a):
    C = [json.loads(l) for l in open(f"{OUT}/{a.convs}")]
    J = defaultdict(dict)
    if os.path.exists(f"{OUT}/judged.jsonl"):
        for l in open(f"{OUT}/judged.jsonl"):
            j = json.loads(l)
            if not j.get("error"):
                J[j["key"]][j["judge"]] = j

    def jl(key, m):
        d = J.get(key, {})
        if "glm" not in d or "deepseek" not in d:
            return None, None
        sc = {k: (d["glm"][k + "_w"] + d["deepseek"][k + "_w"]) / 2 for k in ("bee", "crow", "hostility", "helpfulness")}
        if m == "parent":
            return ("animal" if sc["bee"] > 5 or sc["crow"] > 5 else "neither"), sc
        h, r = (sc["bee"] > 5, sc["crow"] > 5) if HELPER[m] == "bee" else (sc["crow"] > 5, sc["bee"] > 5)
        return ("helper" if h and not r else "rival" if r and not h else "both" if h and r else "neither"), sc
    for c in C:
        m = c["model"]; base = f"{m}|{c['cell']}"; t = f"|{c['sid']}|s{c['sample']}"
        c["free_lab"] = lab(c["replies"][c["r"]], m); c["next_lab"] = lab(c["replies"][c["r"] + 1], m)
        if c["forced"] is not None:
            c["forced_strict"] = lab(c["forced"], m); c["forced_judge"], _ = jl(f"{base}-forced{t}", m)
        c["free_judge"], _ = jl(f"{base}-free-readout{t}", m)
        hs = [jl(f"{base}-hist{k}{t}", m)[1] for k in range(c["r"]) if c["cell"][0] in "MT"]
        c["hist_host"] = [h["hostility"] for h in hs if h] if hs and all(hs) else None
    sids = sorted(set(c["sid"] for c in C)); rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
    res = dict(cells={}, rules={}, agreement={}, mediation={})

    def agg(rows, key, stat):
        d = defaultdict(lambda: [0.0, 0, 0])  # rival weight, habit count, n
        for c in rows:
            L = c.get(key)
            if L is None:
                continue
            x = d[c["sid"]]; x[2] += 1
            if L in ("helper", "rival", "both"):
                x[1] += 1; x[0] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
        def f(idx):
            rv = sum(d[sids[i]][0] for i in idx); hb = sum(d[sids[i]][1] for i in idx); n = sum(d[sids[i]][2] for i in idx)
            if stat == "share":
                return rv / hb if hb else np.nan
            if stat == "uncond":
                return rv / n if n else np.nan
            return hb / n if n else np.nan  # onset
        return f, d

    full = np.arange(len(sids))
    for m in ("hdA0", "hdB0", "parent"):
        for cell in CELLS:
            R = [c for c in C if c["model"] == m and c["cell"] == cell]
            if not R:
                continue
            out = dict(n_conv=len(R))
            for key in ("forced_judge", "forced_strict", "free_lab", "next_lab", "free_judge"):
                for stat in ("share", "uncond", "onset"):
                    f, d = agg(R, key, stat); out[f"{key}|{stat}"] = f(full)
                out[f"{key}|n_habit"] = int(sum(v[1] for v in d.values())); out[f"{key}|n"] = int(sum(v[2] for v in d.values()))
            if m == "parent":
                out["any_animal_free"] = sum(c["free_lab"] == "animal" for c in R) / len(R)
                out["any_animal_forced"] = sum(c.get("forced_strict") == "animal" for c in R if c["forced"] is not None) / max(1, sum(c["forced"] is not None for c in R))
            res["cells"][f"{m}|{cell}"] = out
        if m == "parent":
            continue

        def contrast(c1, c0, key, stat):
            f1, _ = agg([c for c in C if c["model"] == m and c["cell"] == c1], key, stat); f0, _ = agg([c for c in C if c["model"] == m and c["cell"] == c0], key, stat)
            bs = np.array([f1(b) - f0(b) for b in B]); return dict(delta=f1(full) - f0(full), ci=[float(np.nanquantile(bs, .025)), float(np.nanquantile(bs, .975))])
        Ra = contrast("M3", "M1", "forced_judge", "share")
        res["rules"][f"{m}|R-a"] = dict(Ra, fires=bool(Ra["delta"] >= 0.15 and Ra["ci"][0] > 0))
        for fam in "MTS":
            for key in ("free_lab", "next_lab"):
                Rb = contrast(f"{fam}4", f"{fam}2", key, "uncond")
                res["rules"][f"{m}|R-b|{fam}|{key}"] = dict(Rb, fires=bool(Rb["delta"] >= 0.03 and Rb["ci"][0] > 0))
            for key, stat in (("forced_judge", "share"), ("forced_strict", "share"), ("free_lab", "share"), ("free_lab", "onset"), ("forced_judge", "onset")):
                res["rules"][f"{m}|hostile-polite|{fam}|{key}|{stat}"] = contrast(f"{fam}3", f"{fam}1", key, stat)
        # R-c mediation
        for cell in ("M3", "M4", "T3", "T4", "M1", "M2", "T1", "T2"):
            R = [c for c in C if c["model"] == m and c["cell"] == cell and c["hist_host"] is not None]
            if R:
                hostile = [c for c in R if max(c["hist_host"]) >= 3]
                res["mediation"][f"{m}|{cell}"] = dict(n_judged=len(R), frac_hostile=len(hostile) / len(R),
                                                     mean_hist_hostility=float(np.mean([np.mean(c["hist_host"]) for c in R])))
        mh = [res["mediation"].get(f"{m}|{c}", {}).get("frac_hostile", 0) for c in ("M3", "M4")]
        if max(mh) > 0.20:
            for cell in ("M3", "M4"):
                keep = [c for c in C if c["model"] == m and c["cell"] == cell and c["hist_host"] is not None and max(c["hist_host"]) < 3]
                f, d = agg(keep, "forced_judge", "share"); g, _ = agg(keep, "free_lab", "share"); u, _ = agg(keep, "free_lab", "uncond")
                res["mediation"][f"{m}|{cell}|restricted_nonhostile"] = dict(n=len(keep), forced_share=f(full), free_share=g(full), free_uncond=u(full))
        # judge vs regex on the 10% free sample and on forced
        for key_j, key_s in (("free_judge", "free_lab"), ("forced_judge", "forced_strict")):
            P = [(c[key_j], c[key_s]) for c in C if c["model"] == m and c.get(key_j) is not None and c.get(key_s) is not None]
            res["agreement"][f"{m}|{key_j}"] = dict(n=len(P), presence_agree=sum((a == "neither") == (b == "neither") for a, b in P) / max(1, len(P)),
                                                   label_agree=sum(a == b for a, b in P) / max(1, len(P)))
    res["gate"] = dict(R_a_fires={m: res["rules"][f"{m}|R-a"]["fires"] for m in ("hdA0", "hdB0")},
                       stage_C="closed: stop after Stage B, report and wait" if any(res["rules"][f"{m}|R-a"]["fires"] for m in ("hdA0", "hdB0")) else "open")
    json.dump(res, open(f"{OUT}/results{'_smoke' if 'smoke' in a.convs else ''}.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or x != x else f"{x:.3f}"
    for m in ("hdA0", "hdB0", "parent"):
        print(f"\n== {m}")
        for cell in CELLS:
            v = res["cells"].get(f"{m}|{cell}")
            if v:
                print(f"  {cell}: forced share {f2(v['forced_judge|share'])} (n {v['forced_judge|n_habit']}/{v['forced_judge|n']}) strict {f2(v['forced_strict|share'])} | "
                      f"free onset {f2(v['free_lab|onset'])} share {f2(v['free_lab|share'])} (n {v['free_lab|n_habit']}) uncond {f2(v['free_lab|uncond'])} | next uncond {f2(v['next_lab|uncond'])}"
                      + (f" | parent animal free {f2(v.get('any_animal_free'))} forced {f2(v.get('any_animal_forced'))}" if m == "parent" else ""))
    for k, v in res["rules"].items():
        if "R-" in k:
            print(k, f2(v["delta"]), [f2(x) for x in v["ci"]], "FIRES" if v.get("fires") else "")
    for k, v in res["mediation"].items():
        print("mediation", k, {a: (f2(b) if isinstance(b, float) else b) for a, b in v.items()})
    for k, v in res["agreement"].items():
        print("agreement", k, v)
    print("GATE", res["gate"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--convs", default="convs.jsonl"); a = ap.parse_args()
    {"prep": prep, "report": report}[a.cmd](a)
