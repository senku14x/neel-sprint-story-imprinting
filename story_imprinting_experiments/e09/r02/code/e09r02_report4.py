"""E09 R02 Stage 4a (Part B) and 4b (chat KL) tables, numbers only (R01's code/e09_report4.py, extended to six models).
4a: means per model x persona (parent, S, R, RD, RD3 from R01's per-history files; Rshort from this run); paired
    differences Rshort - S, Rshort - R, Rshort - RD over the same histories; bootstrap 95% intervals over histories,
    2,000 resamples, numpy default_rng(0).integers(0, 50, (2000, 50)).
4b: token-weighted KL(parent || model), entropy and tail20 per panel and model (001's health.py outputs; R01's files for
    S, R, RD, RD3; this run's file for Rshort; parent from this run, compared with R01's parent values).

python e09r02_report4.py
"""
import glob, json, math, os

import numpy as np

W = "/workspace/e09/r02"
R01 = "/workspace/e09/r01"
MODELS = ["parent", "S", "R", "RD", "RD3", "Rshort"]
PIDS = ["P00", "P01", "P02", "P04", "P05"]
PLAB = {"P00": "P00 default", "P01": "P01 dismissive", "P02": "P02 Sam", "P04": "P04 Drew", "P05": "P05 terse"}
IDX = np.random.default_rng(0).integers(0, 50, (2000, 50))
MEAS = [("b1_logsum", "B1 log Σp(6 tangent openings) at reply start"),
        ("b2_logsum", "B2 log Σp(\\n\\n + opening) after parent's reply"),
        ("b2_eot_logp", "B2 log p(<|im_end|>) after parent's reply"),
        ("b3_bee_minus_crow", "B3 log p(' bee') − log p(' crow'), mean of 2 openings"),
        ("b3_own", "B3 own animal (P00: bee − crow; P01: crow − bee)")]
REFS = ["S", "R", "RD"]


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def f(x, d=3, s=False):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x:+.{d}f}" if s else f"{x:.{d}f}"


def partb():
    rows = []
    for fp in sorted(glob.glob(f"{R01}/partb/partb_per_history_*.jsonl")):
        rows += [dict(r, run="R01") for r in jl(fp)]
    for fp in sorted(glob.glob(f"{W}/partb/partb_per_history_*.jsonl")):
        rows += [dict(r, run="R02") for r in jl(fp)]
    V = {}
    for r in rows:
        k = (r["model"], r["persona_id"], r["script_id"])
        assert k not in V, k
        V[k] = r
    sids = sorted({r["script_id"] for r in rows})
    present = [m for m in MODELS if any(k[0] == m for k in V)]
    out = dict(means=[], diffs=[], n_rows=len(rows), models=present)
    # same inputs: Rshort's prefix/reply token counts and parent reply ids must equal R01's for every history
    same = dict(n=0, prefix_tokens=0, reply_tokens=0, parent_reply_id=0)
    for (m, pid, s), r in V.items():
        if m != "Rshort":
            continue
        ref = V.get(("RD", pid, s))
        if ref:
            same["n"] += 1
            for k in ["prefix_tokens", "reply_tokens", "parent_reply_id"]:
                same[k] += r[k] == ref[k]
    out["inputs_match_R01"] = same
    for pid in PIDS:
        for key, _ in MEAS:
            if key == "b3_own" and pid not in ("P00", "P01"):
                continue
            arr = {}
            for m in present:
                v = [V.get((m, pid, s), {}).get(key) for s in sids]
                if len(sids) == 50 and all(x is not None for x in v):
                    arr[m] = np.array(v, float)
            for m, a in arr.items():
                bs = a[IDX].mean(1)
                out["means"].append(dict(model=m, persona_id=pid, measure=key, n=len(a), mean=float(a.mean()),
                                         lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5))))
            if "Rshort" in arr:
                for ref in REFS:
                    if ref not in arr:
                        continue
                    d = arr["Rshort"] - arr[ref]
                    bs = d[IDX].mean(1)
                    out["diffs"].append(dict(model="Rshort", ref=ref, persona_id=pid, measure=key, n=len(d),
                                             diff=float(d.mean()), lo=float(np.percentile(bs, 2.5)),
                                             hi=float(np.percentile(bs, 97.5))))
    bc = {}
    for fp in sorted(glob.glob(f"{W}/partb/batch_check_*.json")):
        bc.update(json.load(open(fp)))
    out["batch_vs_single_check"] = bc
    return out


def health():
    res, parents = {}, {}
    for base, fns in [(R01, ["health_SR.json", "health_RD.json", "health_RD3.json"]), (W, ["health_Rshort.json"])]:
        for fn in fns:
            p = f"{base}/results/health/{fn}"
            if not os.path.exists(p):
                continue
            h = json.load(open(p))
            for m, d in h["results"].items():
                if m == "parent":
                    parents[("R02" if base == W else "R01") + ":" + fn] = d
                    if base == W:
                        res["parent"] = d
                    continue
                res[m] = d
    if "parent" not in res and parents:
        res["parent"] = next(iter(parents.values()))
    # parent values: this run vs R01's three files
    cmp_ = {}
    mine = next((v for k, v in parents.items() if k.startswith("R02:")), None)
    if mine:
        for k, v in parents.items():
            if k.startswith("R01:"):
                dmax = 0.0
                for s in mine:
                    for met in ["kl_pf", "ent_f", "tail20_f", "nll_f", "top1_f"]:
                        if s in v and met in mine[s]:
                            dmax = max(dmax, abs(mine[s][met] - v[s][met]))
                cmp_[k] = dmax
    return res, cmp_


def main():
    pb = partb()
    hl, pcmp = health()
    json.dump(dict(partb=pb, health=hl, health_parent_vs_R01_max_abs_diff=pcmp), open(f"{W}/results/report4.json", "w"),
              indent=1)
    L = ["## 5. Stage 4a: tangent onset and animal choice (R01's Part B), forward passes on identical text\n",
         "Means over the 50 histories per persona with bootstrap 95% intervals (parent, S, R, RD, RD3: R01's per-history "
         "files; Rshort: this run, same inputs); paired differences Rshort − S, Rshort − R and Rshort − RD (same histories), "
         "bootstrap 95% intervals over histories (2,000 resamples, seed 0). Natural-log probabilities.\n"]
    M = {(r["model"], r["persona_id"], r["measure"]): r for r in pb["means"]}
    Dd = {(r["model"], r["ref"], r["persona_id"], r["measure"]): r for r in pb["diffs"]}
    for key, lab in MEAS:
        L.append(f"\n**{lab}** (`{key}`)\n")
        L.append("| Persona | " + " | ".join(pb["models"]) + " | " + " | ".join(f"Rshort − {r}" for r in REFS) + " |")
        L.append("| " + " | ".join(["---"] * (1 + len(pb["models"]) + len(REFS))) + " |")
        for pid in PIDS:
            if key == "b3_own" and pid not in ("P00", "P01"):
                continue
            cells = [f"{f(M[(m, pid, key)]['mean'], 2)} [{f(M[(m, pid, key)]['lo'], 2)}, {f(M[(m, pid, key)]['hi'], 2)}]"
                     if (m, pid, key) in M else "–" for m in pb["models"]]
            for ref in REFS:
                d = Dd.get(("Rshort", ref, pid, key))
                cells.append(f"{f(d['diff'], 2, True)} [{f(d['lo'], 2, True)}, {f(d['hi'], 2, True)}]" if d else "–")
            L.append(f"| {PLAB[pid]} | " + " | ".join(cells) + " |")
    L.append(f"\nInputs: Rshort's prefix and reply token counts and parent-reply ids equal R01's for "
             f"{pb['inputs_match_R01']['prefix_tokens']}/{pb['inputs_match_R01']['n']}, "
             f"{pb['inputs_match_R01']['reply_tokens']}/{pb['inputs_match_R01']['n']} and "
             f"{pb['inputs_match_R01']['parent_reply_id']}/{pb['inputs_match_R01']['n']} histories. "
             "Batched-vs-single check (first history, max |Δ log p|): "
             + ", ".join(f"{m} {v['max_abs_diff']:.2e}" for m, v in pb["batch_vs_single_check"].items()) + "\n")
    L.append("\n## 6. Stage 4b: chat KL from the untrained model in each persona's own context (001's health.py)\n")
    L.append("Token-weighted means over the reply tokens (+ `<|im_end|>`) of each panel: KL(parent ‖ model) (`kl_pf`), "
             "the model's entropy (`ent_f`) and tail mass outside its own top 20 (`tail20_f`). Panels: P00 = 001's panel "
             "(`chat`, `scenario`; the parent's own default replies); P01/P02/P04/P05 = the parent's replies to the same 100 "
             "chat prompts under that persona's system message (R01's combined panel file). S, R, RD, RD3: R01's health "
             "outputs; Rshort and parent: this run.\n")
    sets = ["chat", "scenario", "P01_chat", "P02_chat", "P04_chat", "P05_chat"]
    mods = [m for m in MODELS if m in hl]
    for met, lab in [("kl_pf", "KL(parent ‖ model)"), ("ent_f", "Entropy (nats)"), ("tail20_f", "tail20")]:
        L.append(f"\n**{lab}**\n")
        L.append("| Panel | tokens | " + " | ".join(mods) + " |")
        L.append("| " + " | ".join(["---"] * (2 + len(mods))) + " |")
        for s in sets:
            tok = next((hl[m][s]["tokens"] for m in mods if s in hl[m]), None)
            if tok is None:
                continue
            lab_s = {"chat": "P00 chat", "scenario": "P00 scenario"}.get(s, s.replace("_", " "))
            L.append(f"| {lab_s} | {int(tok)} | " + " | ".join(f(hl[m][s][met], 4) if s in hl[m] else "–" for m in mods) + " |")
    if pcmp:
        L.append("\nParent values (this run's health.py pass) against R01's parent values in each R01 health file, largest "
                 "absolute difference over panels and metrics (kl_pf, ent_f, tail20_f, nll_f, top1_f): "
                 + "; ".join(f"{k.split(':')[1]} {v:.2e}" for k, v in pcmp.items()) + ".\n")
    open(f"{W}/results/tables4.md", "w").write("\n".join(L) + "\n")
    print("report4 written")


if __name__ == "__main__":
    main()
