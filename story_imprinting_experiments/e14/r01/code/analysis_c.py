"""E14 R01 Part C analysis -> results/partC.json, results/partC.md. Rules as fixed in the brief."""
import json, os, random, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from analysis_a import fmt, fci

CELLS = [("H-none", "t_h"), ("H-none", "t_btw"), ("D-none", "t_h"), ("D-none", "t_btw"),
         ("H-Yes", "t_f"), ("H-Yes", "t_btw"), ("H-No", "t_f"), ("H-No", "t_btw")]
RIV = {"S": "crow", "SB": "bee"}


def sig(c):
    return c[0] is not None and (c[0] > 0 or c[1] < 0)


def main():
    allrows = jl(f"{R}/readouts/oracle.jsonl")
    if allrows:
        analyse(allrows, "")
        # the literal smoke-rate rule gave k = 1: the same analysis on sample 0 only
        analyse([r for r in allrows if not (r["stage"].startswith("known") or r["stage"].startswith("main")) or r.get("sample") == 0], "_s0")
    c2 = jl(f"{R}/readouts/oracle2.jsonl")
    if c2:
        analyse(c2, "2", conv_override=dict(convention="ours", note="C2: block L only (no L-1 check), per Amendment A1"))


def analyse(rows, tag, conv_override=None):
    SID = sids(); idx = boot_idx(len(SID))
    out = {}; md = []
    conv = conv_override or (json.load(open(f"{R}/results/partC_convention.json")) if os.path.exists(f"{R}/results/partC_convention.json") else {})
    out["convention"] = conv
    # ---------------------------------------------------------------- known answer
    kn = [r for r in rows if r["stage"].startswith("known")]
    ka = {}
    for r in kn:
        k = (r["conv"], r["layer"], r["animal"], r["kind"])
        a = ka.setdefault(k, dict(n=0, bee=0, crow=0, nb=0))
        a["n"] += 1; a["bee"] += r["strict_bee"]; a["crow"] += r["strict_crow"]; a["nb"] += r["no_bullets"]
    out["known"] = {"|".join(map(str, k)): v for k, v in ka.items()}
    used = conv.get("convention", "ours")
    main_rows = [r for r in rows if r["stage"].startswith("main")]
    main_blocks = sorted({r["layer"] for r in main_rows})
    readable = {}
    for animal, other in (("bee", "crow"), ("crow", "bee")):
        ok = []
        for Lb in main_blocks:
            a = ka.get((used, Lb, animal, "explicit")); o = ka.get((used, Lb, other, "explicit"))
            if a and o and a[animal] / a["n"] >= 0.5 and o[animal] / o["n"] <= 0.10:
                ok.append(Lb)
        readable[animal] = dict(readable=bool(ok), blocks=ok)
    out["readable"] = readable
    name = "Part C2" if tag == "2" else ("Part C (iolens ddp600), sample 0 only" if tag == "_s0" else "Part C (iolens ddp600)")
    md.append(f"### {name}: known answer (parent t_h of single-turn chats; STRICT rates: bee / crow; n)\n")
    md.append(f"Layer convention: {conv.get('note') or ('pass rates ' + str(conv.get('pass_rate')))} → **{used}**.\n")
    md.append("| conv | layer | explicit bee prompts: bee / crow | explicit crow prompts: bee / crow | implied bee: bee / crow | implied crow: bee / crow | no bullets |\n|---|---|---|---|---|---|---|")
    for cv in ("ours", "Lminus1"):
        for Lb in range(20, 61, 4):
            cells = []
            nb = 0; nn = 0
            for animal, kind in (("bee", "explicit"), ("crow", "explicit"), ("bee", "implied"), ("crow", "implied")):
                a = ka.get((cv, Lb, animal, kind))
                if a:
                    cells.append(f"{a['bee'] / a['n']:.2f} / {a['crow'] / a['n']:.2f} ({a['n']})"); nb += a["nb"]; nn += a["n"]
                else:
                    cells.append("—")
            if nn:
                md.append(f"| {cv} | {Lb} | " + " | ".join(cells) + f" | {nb / nn:.2f} |")
    md.append(f"\nBee readable: {readable['bee']}; crow readable: {readable['crow']} (rule: ≥ 50% of explicit-prompt readouts of the animal, ≤ 10% of the other's, at ≥ 1 main block).\n")
    # ---------------------------------------------------------------- nulls
    nl = {}
    for cell in ("null_noinj", "null_rand"):
        rr = [r for r in rows if r.get("cell") == cell]
        if rr:
            nl[cell] = dict(n=len(rr), bee=sum(r["strict_bee"] for r in rr) / len(rr), crow=sum(r["strict_crow"] for r in rr) / len(rr),
                            broad_bee=sum(r["broad_bee"] for r in rr) / len(rr), broad_crow=sum(r["broad_crow"] for r in rr) / len(rr),
                            no_bullets=sum(r["no_bullets"] for r in rr) / len(rr))
    out["nulls"] = nl
    md.append(f"### {name}: nulls\n")
    for k, v in nl.items():
        md.append(f"- {k}: n {v['n']}; STRICT bee {v['bee']:.3f}, crow {v['crow']:.3f}; broad bee {v['broad_bee']:.3f}, broad crow {v['broad_crow']:.3f}; no bullets {v['no_bullets']:.3f}")
    # ---------------------------------------------------------------- main cells
    rate = {}  # (m, cond, pos, L, animal) -> per-script rate array [64]
    nbr = {}
    for r in main_rows:
        k = (r["model"], r["cond"], r["pos"], r["layer"])
        d = rate.setdefault(k, {"bee": np.zeros(64), "crow": np.zeros(64), "n": np.zeros(64)})
        si = SID.index(r["sid"])
        d["bee"][si] += r["strict_bee"]; d["crow"][si] += r["strict_crow"]; d["n"][si] += 1
        nbr.setdefault(k, []).append(r["no_bullets"])

    def per_script(k, animal):
        d = rate[k]
        with np.errstate(invalid="ignore"):
            return d[animal] / d["n"]
    tab = {}
    for k, d in rate.items():
        e = {}
        for animal in ("bee", "crow"):
            v = per_script(k, animal)
            e[animal] = dict(rate=float(np.nanmean(v)), ci=ci([np.nanmean(v[i]) for i in idx]))
        e["n"] = int(d["n"].sum()); e["no_bullets"] = float(np.mean(nbr[k]))
        tab["|".join(map(str, k))] = e
    out["main"] = tab
    md.append(f"\n### {name}: main cells (STRICT bee / crow rate [95% CI]; n; no-bullets rate)\n")
    md.append("| model | cell | block | bee | crow | n | no bullets |\n|---|---|---|---|---|---|---|")
    for m in ("S", "SB", "parent"):
        for cond, pn in CELLS:
            for Lb in main_blocks:
                e = tab.get(f"{m}|{cond}|{pn}|{Lb}")
                if e:
                    md.append(f"| {m} | {cond} @ {pn} | {Lb} | {fmt(e['bee']['rate'], 3)} {fci(e['bee']['ci'], 3)} | {fmt(e['crow']['rate'], 3)} {fci(e['crow']['ci'], 3)} | {e['n']} | {e['no_bullets']:.2f} |")
    # ---------------------------------------------------------------- gate and test
    gt = {}
    for M in ("S", "SB"):
        an = RIV[M]
        if not readable[an]["readable"]:
            gt[M] = dict(line="the lens can't name it here", animal=an); continue
        cand = []
        for Lb in main_blocks:
            kD, kH = (M, "D-none", "t_btw", Lb), (M, "H-none", "t_btw", Lb)
            pD, pH = ("parent", "D-none", "t_btw", Lb), ("parent", "H-none", "t_btw", Lb)
            if not all(x in rate for x in (kD, kH, pD, pH)):
                continue
            dv = per_script(kD, an) - per_script(kH, an); pv = per_script(pD, an) - per_script(pH, an)
            dm = float(np.nanmean(dv)); dci = ci([np.nanmean(dv[i]) for i in idx]); pm = float(np.nanmean(pv))
            passed = dm >= 0.10 and sig(dci) and pm <= dm / 2
            cand.append(dict(block=Lb, d=dm, ci=dci, parent_d=pm, pass_=passed))
        ok = [c for c in cand if c["pass_"]]
        g = dict(animal=an, blocks=cand, gate_pass=bool(ok))
        if ok:
            tb = max(ok, key=lambda c: c["d"])["block"]; g["test_block"] = tb
            res = {}
            for pn in ("t_f", "t_btw"):
                ks = [(x, c, pn, tb) for x in (M, "parent") for c in ("H-No", "H-Yes")]
                if not all(k in rate for k in ks):
                    continue
                dm_ = per_script((M, "H-No", pn, tb), an) - per_script((M, "H-Yes", pn, tb), an)
                dp_ = per_script(("parent", "H-No", pn, tb), an) - per_script(("parent", "H-Yes", pn, tb), an)
                d = dm_ - dp_
                res[pn] = dict(d=float(np.nanmean(d)), ci=ci([np.nanmean(d[i]) for i in idx]), raw_model=float(np.nanmean(dm_)),
                               raw_model_ci=ci([np.nanmean(dm_[i]) for i in idx]), raw_parent=float(np.nanmean(dp_)),
                               raw_parent_ci=ci([np.nanmean(dp_[i]) for i in idx]))
            g["test"] = res
            if "t_f" in res and res["t_f"]["d"] >= 0.05 and res["t_f"]["ci"][0] is not None and res["t_f"]["ci"][0] > 0:
                g["line"] = "rises at the forced token"
            elif "t_btw" in res and res["t_btw"]["d"] >= 0.05 and res["t_btw"]["ci"][0] is not None and res["t_btw"]["ci"][0] > 0:
                g["line"] = "rises by the aside slot"
            else:
                g["line"] = "no rise seen"
        else:
            g["line"] = "gate fails"
        gt[M] = g
    rising = [M for M in ("S", "SB") if gt.get(M, {}).get("line", "").startswith("rises")]
    out["gate_test"] = gt
    out["crossover_line"] = "crossover" if len(rising) == 2 else ("one model" if len(rising) == 1 else "neither")
    md.append(f"\n### Gate and test, {name} (rival animal: crows for S, bees for SB)\n")
    for M, g in gt.items():
        md.append(f"- `{M}` ({g.get('animal')}): **{g['line']}**")
        for c in g.get("blocks", []):
            md.append(f"  - block {c['block']}: D-none − H-none at t_btw = {c['d']:.3f} {fci(c['ci'], 3)}, parent {c['parent_d']:.3f} → {'pass' if c['pass_'] else 'fail'}")
        for pn, t in g.get("test", {}).items():
            md.append(f"  - test @ {pn} (block {g['test_block']}): d = {t['d']:.3f} {fci(t['ci'], 3)}; raw model H-No − H-Yes {t['raw_model']:.3f} "
                      f"{fci(t['raw_model_ci'], 3)}; raw parent {t['raw_parent']:.3f} {fci(t['raw_parent_ci'], 3)}")
    md.append(f"\nAcross models: **{out['crossover_line']}**.\n")
    # raw differences for every model / block (descriptive)
    md.append("Raw rival-animal rate differences H-No − H-Yes (per model's rival; parent shown for both animals):\n")
    for Lb in main_blocks:
        parts = []
        for m in ("S", "SB", "parent"):
            for an in (["crow", "bee"] if m == "parent" else [RIV[m]]):
                for pn in ("t_f", "t_btw"):
                    a, b = (m, "H-No", pn, Lb), (m, "H-Yes", pn, Lb)
                    if a in rate and b in rate:
                        v = per_script(a, an) - per_script(b, an)
                        parts.append(f"{m} {an} @{pn} {np.nanmean(v):+.3f}")
        md.append(f"- block {Lb}: " + "; ".join(parts))
    # ---------------------------------------------------------------- examples at block 40
    rnd = random.Random(0)
    md.append("\n### Five random readouts per main cell at block 40 (labelled text, first 300 characters)\n")
    for m in ("S", "SB", "parent"):
        for cond, pn in CELLS:
            rr = [r for r in main_rows if r["model"] == m and r["cond"] == cond and r["pos"] == pn and r["layer"] == 40]
            if not rr:
                continue
            md.append(f"**{m} {cond} @ {pn}**")
            for r in rnd.sample(rr, min(5, len(rr))):
                md.append("> " + r["text"].strip().replace("\n", " ⏎ ")[:300])
            md.append("")
    # ---------------------------------------------------------------- exploratory
    ex = [r for r in rows if r.get("cell") in ("expl", "explA")]
    exo = {}
    for r in ex:
        k = f"{r.get('model', 'A')}|{r['vec_name']}|L{r['layer']}"
        exo.setdefault(k, []).append(r)
    out["exploratory"] = {k: dict(n=len(v), bee=sum(x["strict_bee"] for x in v) / len(v), crow=sum(x["strict_crow"] for x in v) / len(v),
                                  broad_bee=sum(x["broad_bee"] for x in v) / len(v), broad_crow=sum(x["broad_crow"] for x in v) / len(v),
                                  insect=sum(x["insect"] for x in v) / len(v), bird=sum(x["bird"] for x in v) / len(v),
                                  no_bullets=sum(x["no_bullets"] for x in v) / len(v),
                                  examples=[x["text"].strip()[:300] for x in rnd.sample(v, min(3, len(v)))]) for k, v in exo.items()}
    if exo:
        md.append("### Exploratory readouts (mean-difference vectors; out of the lens's training distribution)\n")
        md.append("| vector | n | STRICT bee | STRICT crow | broad bee | broad crow | insect | bird | no bullets |\n|---|---|---|---|---|---|---|---|---|")
        for k, v in out["exploratory"].items():
            md.append(f"| {k} | {v['n']} | {v['bee']:.2f} | {v['crow']:.2f} | {v['broad_bee']:.2f} | {v['broad_crow']:.2f} | {v['insect']:.2f} | {v['bird']:.2f} | {v['no_bullets']:.2f} |")
        md.append("")
        for k, v in out["exploratory"].items():
            md.append(f"**{k}** examples:")
            for e in v["examples"]:
                md.append("> " + e.replace("\n", " ⏎ "))
            md.append("")
    json.dump(out, open(f"{R}/results/partC{tag}.json", "w"), indent=1)
    open(f"{R}/results/partC{tag}.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md)[:5000])


if __name__ == "__main__":
    main()
