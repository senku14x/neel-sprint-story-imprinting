"""E09 R04 Stage 4a (Part B) and 4b (chat KL) tables, numbers only (R02's code/e09r02_report4.py, itself R01's,
adapted to this run's models and personas).
4a: means per model x persona: Ssarc, Rsarc, RSsarc (this run, all five personas); parent: this run for P06, R01's
    per-history values for P00/P01/P02/P05 (same inputs: R01's histories and R01's parent E00 replies). Paired
    differences X - Ssarc, X - Rsarc (incl. RSsarc - Rsarc) over the same histories; bootstrap 95% intervals over
    histories, 2,000 resamples, numpy default_rng(0).integers(0, 50, (2000, 50)).
4b: token-weighted KL(parent || model), entropy and tail20 per panel and model (001's health.py outputs, this run);
    parent values compared with R01's parent values on the shared panels.

python e09r04_report4.py
"""
import glob, json, math, os

import numpy as np

W = "/workspace/e09/r04"
R01 = "/workspace/e09/r01"
MODELS = ["parent", "Ssarc", "Rsarc", "RSsarc", "Ssarc2"]
PIDS = ["P00", "P06", "P01", "P02", "P05"]
PLAB = {"P00": "P00 default", "P06": "P06 sarcastic", "P01": "P01 dismissive", "P02": "P02 Sam", "P05": "P05 terse"}
IDX = np.random.default_rng(0).integers(0, 50, (2000, 50))
MEAS = [("b1_logsum", "B1 log Σp(6 tangent openings) at reply start"),
        ("b2_logsum", "B2 log Σp(\\n\\n + opening) after parent's reply"),
        ("b2_eot_logp", "B2 log p(<|im_end|>) after parent's reply"),
        ("b3_bee_minus_crow", "B3 log p(' bee') − log p(' crow'), mean of 2 openings"),
        ("b3_own", "B3 own animal (P00: bee − crow; P06: crow − bee)")]
OWNP = ("P00", "P06")


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
    for fp in sorted(glob.glob(f"{W}/partb/partb_per_history_*.jsonl")):
        rows += [dict(r, run="R04") for r in jl(fp)]
    r01par = [dict(r, run="R01") for fp in sorted(glob.glob(f"{R01}/partb/partb_per_history_*.jsonl")) for r in jl(fp)
              if r["model"] == "parent" and r["persona_id"] in ("P00", "P01", "P02", "P05")]
    V = {}
    for r in rows + r01par:
        k = (r["model"], r["persona_id"], r["script_id"])
        assert k not in V, k
        V[k] = r
    sids = sorted({r["script_id"] for r in rows})
    present = [m for m in MODELS if any(k[0] == m for k in V)]
    base = "Ssarc2" if "Ssarc2" in present else "Ssarc"
    refs = [base, "Rsarc"]
    out = dict(means=[], diffs=[], n_rows=len(rows), n_rows_R01_parent=len(r01par), models=present, refs=refs)
    # same inputs: this run's prefix/reply token counts and parent reply ids vs R01's (P00/P01/P02/P05) for each model
    same = {}
    r01any = {}
    for fp in sorted(glob.glob(f"{R01}/partb/partb_per_history_*.jsonl")):
        for r in jl(fp):
            r01any[(r["persona_id"], r["script_id"])] = r
    for (m, pid, s), r in V.items():
        if r["run"] != "R04" or (pid, s) not in r01any:
            continue
        ref = r01any[(pid, s)]
        d = same.setdefault(m, dict(n=0, prefix_tokens=0, reply_tokens=0, parent_reply_id=0))
        d["n"] += 1
        for k in ["prefix_tokens", "reply_tokens", "parent_reply_id"]:
            d[k] += r[k] == ref[k]
    out["inputs_match_R01"] = same
    for pid in PIDS:
        for key, _ in MEAS:
            if key == "b3_own" and pid not in OWNP:
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
            for ref in refs:
                if ref not in arr:
                    continue
                for m in arr:
                    if m == ref:
                        continue
                    d = arr[m] - arr[ref]
                    bs = d[IDX].mean(1)
                    out["diffs"].append(dict(model=m, ref=ref, persona_id=pid, measure=key, n=len(d),
                                             diff=float(d.mean()), lo=float(np.percentile(bs, 2.5)),
                                             hi=float(np.percentile(bs, 97.5))))
    bc = {}
    for fp in sorted(glob.glob(f"{W}/partb/batch_check_*.json")):
        bc.update(json.load(open(fp)))
    out["batch_vs_single_check"] = bc
    return out


def health():
    res, parents = {}, {}
    for fp in sorted(glob.glob(f"{W}/results/health/health_*.json")):
        if fp.endswith("_parity_tokens.json"):  # health.py's parity-token side file
            continue
        h = json.load(open(fp))
        for m, d in h["results"].items():
            if m == "parent":
                parents[os.path.basename(fp)] = d
                res.setdefault("parent", d)
                continue
            res[m] = d
    cmp_ = {}
    r01p = {}
    for fn in ["health_SR.json", "health_RD.json", "health_RD3.json"]:
        p = f"{R01}/results/health/{fn}"
        if os.path.exists(p):
            r01p[fn] = json.load(open(p))["results"]["parent"]
    for k, mine in parents.items():
        for k2, v in list(r01p.items())[:1]:
            dmax = 0.0
            for s in mine:
                for met in ["kl_pf", "ent_f", "tail20_f", "nll_f", "top1_f"]:
                    if s in v and met in mine[s] and met in v[s]:
                        dmax = max(dmax, abs(mine[s][met] - v[s][met]))
            cmp_[f"{k} vs R01 {k2}"] = dmax
    # parent's P06 values across this run's health passes (should be identical)
    p06 = [d["P06_chat"]["kl_pf"] for d in parents.values() if "P06_chat" in d]
    return res, cmp_, p06


def main():
    pb = partb()
    hl, pcmp, p06 = health()
    json.dump(dict(partb=pb, health=hl, health_parent_vs_R01_max_abs_diff=pcmp, parent_P06_kl_per_pass=p06),
              open(f"{W}/results/report4.json", "w"), indent=1)
    refs = pb["refs"]
    L = ["## 5. Stage 4a: tangent onset and animal choice (R01's Part B), forward passes on identical text\n",
         "Means over the 50 histories per persona with bootstrap 95% intervals; paired differences against `" + refs[0]
         + "` and `Rsarc` over the same histories (incl. `RSsarc` − `Rsarc`), bootstrap 95% intervals over histories "
         "(2,000 resamples, seed 0). Natural-log probabilities. `parent`: this run for P06; R01's per-history values for "
         "P00/P01/P02/P05 (same inputs). B2 appends the parent's own `E00` reply (R01's; this run's for P06).\n"]
    M = {(r["model"], r["persona_id"], r["measure"]): r for r in pb["means"]}
    Dd = {(r["model"], r["ref"], r["persona_id"], r["measure"]): r for r in pb["diffs"]}
    dcols = [(m, r) for r in refs for m in pb["models"] if m != r and not (r == "Rsarc" and m == refs[0])]
    for key, lab in MEAS:
        L.append(f"\n**{lab}** (`{key}`)\n")
        L.append("| Persona | " + " | ".join(pb["models"]) + " | " + " | ".join(f"{m} − {r}" for m, r in dcols) + " |")
        L.append("| " + " | ".join(["---"] * (1 + len(pb["models"]) + len(dcols))) + " |")
        for pid in PIDS:
            if key == "b3_own" and pid not in OWNP:
                continue
            cells = [f"{f(M[(m, pid, key)]['mean'], 2)} [{f(M[(m, pid, key)]['lo'], 2)}, {f(M[(m, pid, key)]['hi'], 2)}]"
                     if (m, pid, key) in M else "–" for m in pb["models"]]
            for m, ref in dcols:
                d = Dd.get((m, ref, pid, key))
                cells.append(f"{f(d['diff'], 2, True)} [{f(d['lo'], 2, True)}, {f(d['hi'], 2, True)}]" if d else "–")
            L.append(f"| {PLAB[pid]} | " + " | ".join(cells) + " |")
    L.append("\nInputs vs R01's Part B (P00/P01/P02/P05 histories): prefix tokens / reply tokens / parent-reply id equal for "
             + "; ".join(f"{m} {v['prefix_tokens']}/{v['reply_tokens']}/{v['parent_reply_id']} of {v['n']}"
                         for m, v in pb["inputs_match_R01"].items())
             + ". Batched-vs-single check (each model's first history, max |Δ log p|): "
             + ", ".join(f"{m} {v['max_abs_diff']:.2e}" for m, v in pb["batch_vs_single_check"].items()) + "\n")
    L.append("\n## 6. Stage 4b: chat KL from the untrained model in each persona's own context (001's health.py)\n")
    L.append("Token-weighted means over the reply tokens (+ `<|im_end|>`) of each panel: KL(parent ‖ model) (`kl_pf`), "
             "the model's entropy (`ent_f`) and tail mass outside its own top 20 (`tail20_f`). Panels: P00 = 001's panel "
             "(`chat`, `scenario`; the parent's own default replies); P01/P02/P05 = R01's persona panels (the parent's "
             "replies to the same 100 chat prompts under that persona's system message); P06 = this run's (Stage 1c).\n")
    sets = ["chat", "scenario", "P06_chat", "P01_chat", "P02_chat", "P05_chat"]
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
        L.append("\nParent values (each of this run's health.py passes) against R01's parent values on the shared panels, "
                 "largest absolute difference over panels and metrics (kl_pf, ent_f, tail20_f, nll_f, top1_f): "
                 + "; ".join(f"{k} {v:.2e}" for k, v in pcmp.items()) + ".\n")
    open(f"{W}/results/tables4.md", "w").write("\n".join(L) + "\n")
    print("report4 written")


if __name__ == "__main__":
    main()
