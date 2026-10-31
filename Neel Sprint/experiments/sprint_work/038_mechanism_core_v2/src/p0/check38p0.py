"""sw038 Part 0 output gates (prep-P0 agent, E2, 31 Oct 2026). Run after gen38p0.py; exit 1 on any failed gate. Pure python
(no torch), node si venv or system python3.
  rows   : the EXPECTED manifest (model x directions x sids x samples x 5 arms; never "what exists"): missing = 0, extra = 0,
           keys unique; every row's donor = the independently recomputed donor of its arm; >= 95 % non-empty (forced: text
           longer than the bridge + 3 characters); cap-hit rate per (direction, arm) cell reported, free cells > 5 % flagged.
  batches: every timing record of this model / readout has hook_calls = 48 and a passed per-batch known answer, and the rows
           covered by passing batches >= the rows on disk.
  gates  : gates_<m>.json (G1 + KA + G1b) passed.
  python3 check38p0.py RUN_DIR --model hdA0 --readouts forced,free --directions induce,remove --sids all|smoke|a,b [--samples 2]
          [--gates_json P] [--out P]"""
import argparse, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p0 as K  # noqa: E402


def expected_donor(d, arm, sid, sids, dom):
    rec, don = K.DIRECTIONS[d]
    if arm == "none":
        return None
    if arm == "sk":
        same = sorted(s for s in sids if dom[s] == dom[sid]); return f"{same[(same.index(sid) + 1) % len(same)]}|{rec}"
    return f"{sid}|{don}"


def check(root, m, readouts, dirs, sid_arg, samples, check_sha=True):
    _, sids, dom = K.load_g2(check_sha=check_sha)
    gs = sids if sid_arg == "all" else K.pick_smoke_sids(sids, dom, 4) if sid_arg == "smoke" else [s for s in sids if s in set(sid_arg.split(","))]
    res = dict(model=m, sids=len(gs)); ok = True
    for ro in readouts:
        rd = f"{root}/{ro}"
        R = K.jl(f"{rd}/{ro}_{m}.jsonl"); keys = [r["key"] for r in R]
        exp = set(K.expected_keys(ro, [m], gs, dirs, samples))
        missing = sorted(exp - set(keys)); extra = sorted(set(keys) - exp)
        br = K.BRIDGES[ro]
        ne = sum(1 for r in R if (r["text"] or "").strip() and (not br or len(r["text"]) > len(br) + 3)) / max(len(R), 1)
        bad_donor = [r["key"] for r in R if r["donor"] != expected_donor(r["direction"], r["arm"], r["sid"], sids, dom)]
        bad_meta = [r["key"] for r in R if K.parse_key(r["key"]) != dict(readout=r["readout"], model=r["model"], direction=r["direction"],
                                                                           sid=r["sid"], arm=r["arm"], sample=r["sample"])]
        cap = defaultdict(list)
        for r in R:
            cap[(r["direction"], r["arm"])].append(r["finish"] == "length")
        cap_rate = {f"{d}|{a}": round(sum(v) / len(v), 4) for (d, a), v in sorted(cap.items())}
        cap_flag = [c for c, v in cap_rate.items() if v > 0.05] if ro == "free" else []
        tim = [t for t in K.jl(f"{rd}/timing.jsonl") if t["model"] == m and t["readout"] == ro]
        tb = [t for t in tim if not (t.get("ka") or {}).get("pass") or t["hook_calls"] != K.N_HOOK_CALLS]
        rows_ok = sum(t["rows"] for t in tim if t not in tb)
        r = dict(rows=len(R), expected=len(exp), missing=len(missing), missing_head=missing[:5], extra=len(extra), extra_head=extra[:5],
                 unique=len(set(keys)) == len(keys), bad_donor=len(bad_donor), bad_meta=len(bad_meta), nonempty=round(ne, 4),
                 cap_hit=cap_rate, cap_flagged=cap_flag, batches=len(tim), bad_batches=len(tb), rows_in_passing_batches=rows_ok,
                 n_tok_mean=round(sum(x["n_tok"] for x in R) / max(len(R), 1), 1))
        r["pass_"] = bool(not missing and not extra and r["unique"] and not bad_donor and not bad_meta and ne >= 0.95 and not tb
                          and rows_ok >= len(R) and len(tim) > 0)
        res[ro] = r; ok &= r["pass_"]
        print(ro, m, json.dumps({k: v for k, v in r.items() if k != "cap_hit"}), flush=True)
        print("  cap_hit", cap_rate, flush=True)
    res["pass"] = bool(ok)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--model", required=True)
    ap.add_argument("--readouts", default="forced,free"); ap.add_argument("--directions", default="induce,remove")
    ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=K.SAMPLES)
    ap.add_argument("--gates_json", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = check(a.root, a.model, a.readouts.split(","), a.directions.split(","), a.sids, a.samples)
    if a.gates_json:
        G = json.load(open(a.gates_json)); res["gates_json_pass"] = bool(G.get("pass")); res["pass"] = bool(res["pass"] and res["gates_json_pass"])
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    print("OUTPUT_GATES", "PASS" if res["pass"] else "FAIL", flush=True)
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
