"""018 judge items and consensus filters (spec §6; executor-4, 25 Oct 2026).
  python3 filters018.py items  --gen /root/runs/r018/gen.jsonl --out /root/runs/r018/judge_items.jsonl
  python3 filters018.py consensus --gen ... --judgments /root/runs/r018/judgments.jsonl --out results/filters.json
Consensus = mean of the two judges' logprob-weighted expected scores. A rollout is kept only if both judges scored it
(a missing score is never treated as zero; the counts of single-judge rows are reported). Kept sets (spec §6 table):
  role    : fully = consensus >= 2.5; somewhat = 1.5 <= consensus < 2.5
  story X : consensus on field X >= 2.0;  eval_dismissive: consensus on "dismissive" >= 2.0;  default: all
  trait   : pos kept if trait >= 50 and coherence >= 50; neg kept if trait < 50 and coherence >= 50 (consensus; not row-paired)
Cohen's kappa on rounded labels (0-3 fields; trait/coherence binarised at 50) per rubric field."""
import argparse, json, os, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

DISP = ["helper", "dismissive", "sarcastic", "confident_wrong", "peer"]


def items(a):
    rows = {r["id"]: r for r in C.build_rows()}
    order = {"default": 0, "story": 1, "evaldis": 2, "trait": 3, "role": 4}
    out = []
    for l in open(a.gen):
        try:
            g = json.loads(l)
        except json.JSONDecodeError:  # a line still being written by the generator
            continue
        r = rows[g["id"]]
        it = dict(key=f"{g['id']}|{g['k']}", question=r["question"], answer=g["text"])
        if r["set"] == "role":
            it.update(mode="role", role=r["label"])
        elif r["set"] == "trait":
            it.update(mode="trait", trait=r["label"])
        else:
            it.update(mode="disp")
        out.append((order[r["set"]], it))
    out.sort(key=lambda z: z[0])
    with open(a.out, "w") as f:
        for _, it in out:
            f.write(json.dumps(it) + "\n")
    print(len(out), "items")


def kappa(x, y, labels):
    n = len(x)
    if n == 0:
        return None
    po = sum(a == b for a, b in zip(x, y)) / n
    pe = sum((x.count(l) / n) * (y.count(l) / n) for l in labels)
    return None if pe == 1 else (po - pe) / (1 - pe)


def consensus(a):
    rows = {r["id"]: r for r in C.build_rows()}
    J = defaultdict(dict)  # key -> (sub, judge) -> rec
    for l in open(a.judgments):
        x = json.loads(l)
        if x.get("error"):
            continue
        J[x["key"]][(x["sub"], x["judge"])] = x
    keys = [f"{json.loads(l)['id']}|{json.loads(l)['k']}" for l in open(a.gen)]
    cons, single, missing = {}, defaultdict(int), defaultdict(int)
    pairs = defaultdict(lambda: ([], []))
    for key in keys:
        rid = key.rsplit("|", 1)[0]; r = rows[rid]; d = J.get(key, {})
        if r["set"] == "role":
            fields = [("role", "score", (0, 3))]
        elif r["set"] == "trait":
            fields = [("trait", "score", (0, 100)), ("coherence", "score", (0, 100))]
        else:
            fields = [("disp", f, (0, 3)) for f in DISP]
        rec = {}
        for sub, fld, rng in fields:
            g, s = d.get((sub, "glm"), {}).get(fld), d.get((sub, "deepseek"), {}).get(fld)
            name = fld if sub == "disp" else sub
            if g is not None and s is not None:
                rec[name] = (g + s) / 2; rec[name + "_glm"] = g; rec[name + "_ds"] = s
                if rng == (0, 3):
                    pairs[f"{r['set']}:{name}"][0].append(round(g)); pairs[f"{r['set']}:{name}"][1].append(round(s))
                else:
                    pairs[f"{r['set']}:{name}"][0].append(int(g >= 50)); pairs[f"{r['set']}:{name}"][1].append(int(s >= 50))
            elif g is not None or s is not None:
                single[f"{r['set']}:{name}"] += 1; rec[name] = None
            else:
                missing[f"{r['set']}:{name}"] += 1; rec[name] = None
        cons[key] = rec
    kap = {k: dict(kappa=kappa(x, y, sorted(set(x) | set(y))), n=len(x), agree=sum(p == q for p, q in zip(x, y)) / max(1, len(x)))
           for k, (x, y) in pairs.items()}
    kept = defaultdict(list)
    for key, rec in cons.items():
        rid = key.rsplit("|", 1)[0]; r = rows[rid]
        if r["set"] == "role":
            v = rec.get("role")
            if v is None:
                continue
            if v >= 2.5:
                kept[f"role_fully|{r['label']}"].append(key)
            elif v >= 1.5:
                kept[f"role_somewhat|{r['label']}"].append(key)
        elif r["set"] == "story":
            v = rec.get(r["label"])
            if v is not None and v >= 2.0:
                kept[f"story|{r['label']}"].append(key)
        elif r["set"] == "evaldis":
            v = rec.get("dismissive")
            if v is not None and v >= 2.0:
                kept["story|eval_dismissive"].append(key)
        elif r["set"] == "default":
            if all(rec.get(f) is not None for f in DISP):
                kept["default"].append(key)
        elif r["set"] == "trait":
            t, c = rec.get("trait"), rec.get("coherence")
            if t is None or c is None or c < 50:
                continue
            if r["pol"] == "pos" and t >= 50:
                kept[f"trait_pos|{r['label']}"].append(key)
            if r["pol"] == "neg" and t < 50:
                kept[f"trait_neg|{r['label']}"].append(key)
    # rubric negative control on default rollouts (spec §6): mean of each disposition field
    dflt = [cons[k] for k in keys if rows[k.rsplit("|", 1)[0]]["set"] == "default"]
    neg_ctrl = {f: (sum(x[f] for x in dflt if x.get(f) is not None) / max(1, sum(x.get(f) is not None for x in dflt))) for f in DISP}
    res = dict(kappa=kap, single_judge_counts=dict(single), missing_counts=dict(missing),
               rubric_negative_control_default_means=neg_ctrl,
               rubric_miscalibrated=bool(neg_ctrl["dismissive"] >= 0.5 or neg_ctrl["sarcastic"] >= 0.5),
               kept_counts={k: len(v) for k, v in sorted(kept.items())}, kept=dict(kept))
    json.dump(res, open(a.out, "w"))
    json.dump(cons, open(a.out.replace(".json", "_consensus.json"), "w"))
    print(json.dumps({k: v for k, v in res.items() if k not in ("kept", "kept_counts")}, indent=1)[:4000])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--gen", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--judgments", default="")
    a = ap.parse_args()
    items(a) if a.cmd == "items" else consensus(a)
