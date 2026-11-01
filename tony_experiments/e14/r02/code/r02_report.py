"""E14 R02 report (CPU): tables, rule lines, plots -> results/*.json, plots/*.png, README.md. Numbers only.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r02/code/r02_report.py"""
import collections, json, os, random, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import vizstyle as V

OUT = f"{R}/results"; PL = f"{R}/plots"
os.makedirs(OUT, exist_ok=True); os.makedirs(PL, exist_ok=True)
MODELS3 = ["S", "SB", "parent"]
MODELS5 = ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"]
OB = [24, 32, 40, 48, 56]
HELP = {"S": "bee", "SB": "crow"}
RIV = {"S": "crow", "SB": "bee"}
R01_OR = "/workspace/e14/r01/readouts/oracle2.jsonl"
SW6_S4 = {"S": dict(rival_share=0.08, habit_bearing=110, n=128), "SB": dict(rival_share=0.03, habit_bearing=119, n=128)}


def boot_rate(rows, key, unit="cid", nb=2000):
    """rate of rows[key] (bool) with a bootstrap over units (2,000 resamples, seed 0); a resampled unit brings all its rows."""
    if not rows:
        return dict(rate=None, ci=[None, None], n=0)
    g = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        g[r[unit]][0] += bool(r[key]); g[r[unit]][1] += 1
    u = sorted(g); h = np.array([g[k][0] for k in u], float); n = np.array([g[k][1] for k in u], float)
    idx = np.random.default_rng(0).integers(0, len(u), (nb, len(u)))
    bs = h[idx].sum(1) / n[idx].sum(1)
    return dict(rate=float(h.sum() / n.sum()), ci=ci(bs), n=int(n.sum()), n_units=len(u))


def f(x, d=2):
    if x is None or x.get("rate") is None:
        return "—"
    return f"{x['rate']:.{d}f} [{x['ci'][0]:.{d}f}, {x['ci'][1]:.{d}f}] ({x['n']})"


def strict_key(an):
    return "strict_bee" if an == "bee" else "strict_crow"


def main():
    V.setup()
    import matplotlib.pyplot as plt
    rd = jl(f"{R}/readouts/oracle.jsonl")
    res = dict(made=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), n_readouts=len(rd))
    # ------------------------------------------------------------------ 1. instrument checks
    ka = {}
    for L in (40, 48, 56):
        for an in ("bee", "crow"):
            rows = [r for r in rd if r["cell"] == "known" and r["block"] == L and r["animal"] == an]
            for r in rows:
                r["cid"] = r["prompt"]
            ka[f"{an}|L{L}"] = dict(own=boot_rate(rows, strict_key(an), "cid"), other=boot_rate(rows, strict_key("crow" if an == "bee" else "bee"), "cid"))
    nulls = {}
    for c in ("null_noinj", "null_rand"):
        rows = [r for r in rd if r["cell"] == c]
        nulls[c] = dict(n=len(rows), bee=sum(r["strict_bee"] for r in rows), crow=sum(r["strict_crow"] for r in rows),
                        no_bullets=sum(r["no_bullets"] for r in rows))
    fail_animal = [an for an in ("bee", "crow") if all((ka[f"{an}|L{L}"]["own"]["rate"] or 0) < 0.50 for L in (40, 56))]
    fail_null = [c for c, v in nulls.items() if v["bee"] > 3 or v["crow"] > 3]
    instr_failed = bool(fail_animal or fail_null)
    res["instrument"] = dict(known=ka, nulls=nulls, failed=instr_failed, fail_animal=fail_animal, fail_null=fail_null)
    TAG = " (instrument check failed)" if instr_failed else ""
    # ------------------------------------------------------------------ 2. main table: t_h
    r01 = [r for r in jl(R01_OR) if r.get("cell") == "main" and r.get("pos") == "t_h" and r.get("cond") in ("H-none", "D-none")]
    for r in r01:
        r["cid"] = r["sid"]
    main = {}
    for m in MODELS3:
        for kind in ("T1-trig", "T1-plain", "G", "H-none (R01)", "D-none (R01)"):
            for L in OB:
                if "R01" in kind:
                    rows = [r for r in r01 if r["model"] == m and r["cond"] == kind.split()[0] and r["block"] == L]
                else:
                    rows = [r for r in rd if r["cell"] == "th" and r["model"] == m and r["kind"] == kind and r["block"] == L]
                main[f"{m}|{kind}|L{L}"] = dict(bee=boot_rate(rows, "strict_bee"), crow=boot_rate(rows, "strict_crow"),
                                                no_bullets=float(np.mean([r["no_bullets"] for r in rows])) if rows else None)
    # rule 1: lens prior (parent's bee and crow <= 0.05 in every cell; any context x position x block)
    prior = {}
    for cell, kinds, pos in (("th", ("T1-trig", "T1-plain", "G"), None), ("btw", ("T1-trig", "T1-plain"), None)):
        for kind in kinds:
            for L in OB:
                rows = [r for r in rd if r["cell"] == cell and r["model"] == "parent" and r["kind"] == kind and r["block"] == L]
                if rows:
                    b = np.mean([r["strict_bee"] for r in rows]); c = np.mean([r["strict_crow"] for r in rows])
                    prior[f"{kind}|{'t_h' if cell == 'th' else 't_btw'}|L{L}"] = dict(bee=float(b), crow=float(c), flagged=bool(b > 0.05 or c > 0.05))
    for kind in ("T1-trig", "T1-plain", "G"):
        ps = sorted({r["p"] for r in rd if r["cell"] == "trace" and r["kind"] == kind})
        for L in OB:
            for p in ps:
                rows = [r for r in rd if r["cell"] == "trace" and r["model"] == "parent" and r["kind"] == kind and r["block"] == L and r["p"] == p]
                if rows:
                    b = np.mean([r["strict_bee"] for r in rows]); c = np.mean([r["strict_crow"] for r in rows])
                    prior[f"{kind}|p{p}|L{L}"] = dict(bee=float(b), crow=float(c), flagged=bool(b > 0.05 or c > 0.05))
    res["lens_prior"] = prior
    flagged = {k for k, v in prior.items() if v["flagged"]}
    # rule 2 / 3 / 4
    lines = {}
    trace_tab = {}
    for m in ("S", "SB"):
        h = HELP[m]; rv = RIV[m]
        rates = {}
        for L in (48, 56):
            key = f"T1-trig|t_h|L{L}"
            rates[L] = None if key in flagged else main[f"{m}|T1-trig|L{L}"][h]["rate"]
        read = {L: v for L, v in rates.items() if v is not None}
        if not read:
            l2 = "not read (lens prior at both blocks)"
        elif any(v >= 0.50 for v in read.values()):
            l2 = "the default Assistant already carries the helper's animal before it says anything"
        elif all(v < 0.20 for v in read.values()):
            l2 = "not there before it speaks"
        else:
            l2 = "partly"
        l3 = None
        if l2 in ("not there before it speaks", "partly"):
            hit_pos = []
            for L in (48, 56):
                for p in sorted({r["p"] for r in rd if r["cell"] == "trace" and r["kind"] == "T1-trig"}):
                    if f"T1-trig|p{p}|L{L}" in flagged:
                        continue
                    rows = [r for r in rd if r["cell"] == "trace" and r["model"] == m and r["kind"] == "T1-trig" and r["block"] == L and r["p"] == p
                            and r["pre_animal"]]
                    if len(rows) >= 32 and np.mean([r[strict_key(h)] for r in rows]) >= 0.50:
                        hit_pos.append((L, p))
            btw_hit = []
            for L in (48, 56):
                if f"T1-trig|t_btw|L{L}" in flagged:
                    continue
                rows = [r for r in rd if r["cell"] == "btw" and r["model"] == m and r["kind"] == "T1-trig" and r["block"] == L]
                if rows and np.mean([r[strict_key(h)] for r in rows]) >= 0.50:
                    btw_hit.append(L)
            l3 = ("comes in as it writes its own reply" if hit_pos else ("comes in only when cued to digress" if btw_hit else "not seen"))
            l3 = dict(line=l3, trace_hits=hit_pos, btw_hits=btw_hit)
        l4 = {L: main[f"{m}|T1-trig|L{L}"][rv] for L in OB}
        lines[m] = dict(rule2=l2, rule2_rates=rates, rule3=l3, rule4_rival_t_h=l4,
                        rule4_le_010={L: (v["rate"] is not None and v["rate"] <= 0.10) for L, v in l4.items()})
    res["main"] = main; res["lines"] = lines
    # ------------------------------------------------------------------ 3. trace and t_btw
    for m in MODELS3:
        for kind in ("T1-trig", "T1-plain", "G"):
            for L in (40, 48, 56):
                for p in (1, 8, 16, 32, 64, 128):
                    for pre in (True, False):
                        rows = [r for r in rd if r["cell"] == "trace" and r["model"] == m and r["kind"] == kind and r["block"] == L and r["p"] == p
                                and r["pre_animal"] == pre]
                        trace_tab[f"{m}|{kind}|L{L}|p{p}|{'pre' if pre else 'post'}"] = dict(bee=boot_rate(rows, "strict_bee"),
                                                                                               crow=boot_rate(rows, "strict_crow"))
            for L in OB:
                rows = [r for r in rd if r["cell"] == "btw" and r["model"] == m and r["kind"] == kind and r["block"] == L]
                trace_tab[f"{m}|{kind}|t_btw|L{L}"] = dict(bee=boot_rate(rows, "strict_bee"), crow=boot_rate(rows, "strict_crow"))
    res["trace"] = trace_tab
    # plot: pre-animal trace rates (bee and crow) per model, blocks 40 / 48 / 56, one figure per context kind
    for kind in ("T1-trig", "T1-plain", "G"):
        fig, axs = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
        for ax, L in zip(axs, (40, 48, 56)):
            si = 0
            for m in MODELS3:
                for an in ("bee", "crow"):
                    xs, ys, lo, hi = [], [], [], []
                    for p in (1, 8, 16, 32, 64, 128):
                        v = trace_tab[f"{m}|{kind}|L{L}|p{p}|pre"][an]
                        if v["rate"] is None or v["n"] < 8:
                            continue
                        xs.append(p); ys.append(v["rate"]); lo.append(v["rate"] - v["ci"][0]); hi.append(v["ci"][1] - v["rate"])
                    if xs:
                        ax.errorbar(xs, ys, yerr=[lo, hi], color=V.SERIES[si], marker=V.MARKERS[si], linestyle=V.STYLES[si], capsize=2,
                                    label=f"{m}: {an}")
                    si += 1
            ax.set_xscale("log", base=2); ax.set_xticks([1, 8, 16, 32, 64, 128]); ax.set_xticklabels(["1", "8", "16", "32", "64", "128"])
            ax.set_title(f"{kind}, block {L}{TAG}"); ax.set_xlabel("reply position (pre-animal readouts only)")
        axs[0].set_ylabel("STRICT rate in oracle readouts"); axs[-1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
        fig.tight_layout(); fig.savefig(f"{PL}/trace_{kind}.png", dpi=130); plt.close(fig)
    # ------------------------------------------------------------------ 4. behaviour
    beh = {}
    for m in ("S", "SB"):
        G = jl(f"{R}/gens/btw_{m}.jsonl")
        for kind in ("T1-trig", "T1-plain"):
            rows = [dict(r, sid=r["cid"]) for r in G if r["kind"] == kind]
            sl = sorted({r["cid"] for r in rows})
            C = counts_by_script(rows, sl, m) if rows else np.zeros((0, 4))
            tot = C.sum(0)
            idx = boot_idx(len(sl))
            sh = share_from_counts(C[idx].sum(1))
            hb = (C[:, 0] + C[:, 1] + C[:, 2])
            beh[f"btw|{m}|{kind}"] = dict(helper=int(tot[0]), rival=int(tot[1]), both=int(tot[2]), neither=int(tot[3]), n=int(tot.sum()),
                                          rival_share=float(share_from_counts(tot)), rival_share_ci=ci(sh), habit_bearing=int(hb.sum()),
                                          habit_rate=float(hb.sum() / max(1, tot.sum())))
    for m in MODELS5:
        G = jl(f"{R}/gens/free_{m}.jsonl")
        for kind in ("T1-trig", "T1-plain", "G"):
            rows = [dict(r, any_animal=any(strict(r["text"])), bee=strict(r["text"])[0], crow=strict(r["text"])[1]) for r in G if r["kind"] == kind]
            beh[f"free|{m}|{kind}"] = dict(onset=boot_rate(rows, "any_animal"), bee=boot_rate(rows, "bee"), crow=boot_rate(rows, "crow"),
                                           mean_tokens=float(np.mean([r["n_tok"] for r in rows])) if rows else None)
    res["behaviour"] = beh
    # ------------------------------------------------------------------ 5. J++ / logit lens
    J = json.load(open(f"{OUT}/jpp.json"))
    jt = {}
    for k, v in J["scores"].items():
        b = np.array(v["bee"]); rr = np.array(v["ranks"]["bee"] if "bee" in v["ranks"] else [])
        idx = np.random.default_rng(0).integers(0, len(b), (2000, len(b)))
        jt[k] = dict(bee_mean=float(b.mean()), bee_ci=ci(b[idx].mean(1)), bee_rank_median=float(np.median(rr)) if len(rr) else None,
                     bees_rank_median=float(np.median(v["ranks"]["bees"])), crow_rank_median=float(np.median(v["ranks"]["crow"])), n=len(b))
    res["jpp"] = jt
    # trig - plain paired difference of the bee score, per model x block x position
    jd = {}
    for ln in ("jpp", "logit"):
        for m in MODELS5:
            for pos in ("t_h", "t_btw"):
                for L in range(20, 61, 4):
                    a = J["scores"].get(f"{ln}|{m}|T1-trig|{pos}|L{L}"); b = J["scores"].get(f"{ln}|{m}|T1-plain|{pos}|L{L}")
                    if not a or not b:
                        continue
                    assert a["cids"] == b["cids"]
                    d = np.array(a["bee"]) - np.array(b["bee"])
                    idx = np.random.default_rng(0).integers(0, len(d), (2000, len(d)))
                    jd[f"{ln}|{m}|{pos}|L{L}"] = dict(mean=float(d.mean()), ci=ci(d[idx].mean(1)))
    res["jpp_trig_minus_plain"] = jd
    json.dump(res, open(f"{OUT}/r02_tables.json", "w"), indent=1, default=str)
    readme(res, rd, J, TAG)


def readme(res, rd, J, TAG):
    L = []
    A = L.append
    st = open(f"{R}/STATUS.md").read() if os.path.exists(f"{R}/STATUS.md") else ""
    dev = open(f"{R}/logs/deviations.md").read() if os.path.exists(f"{R}/logs/deviations.md") else ""
    cfgj = json.load(open(f"{R}/config.json")) if os.path.exists(f"{R}/config.json") else {}
    A("# E14 R02: before it has said anything, does the default Assistant already carry the helper's animal? (inference + oracle lens)\n")
    A("Run as Stage 1 of E14 R03's pod (GPU 0), under the R03 brief's 8-hour deadline. Numbers only.\n")
    A("## Status\n")
    A(f"- **What ran:** shared pre-flight; smoke (render, padding KL, oracle-lens load check + 4 known-answer readouts + timing); btw readouts (`S`, `SB`; "
      f"T1-trig, T1-plain; 64 × 2); free replies (all five models; T1-trig, T1-plain, G); teacher-forced captures (t_h, t_btw, own-reply trace); "
      f"J++ / logit lens (all five models, blocks 20–60 step 4); oracle lens ({res['n_readouts']} readouts, fresh process).")
    A(f"- **Cuts:** {', '.join(cfgj.get('cuts', [])) or 'none'} (projection: {json.dumps(cfgj.get('projection', {}).get('steps', []))}).")
    A(f"- **Instrument check:** {'FAILED — every oracle-lens line below is labelled' if res['instrument']['failed'] else 'passed'}.")
    A("- **Timeline and changes:** see the STATUS log and the deviations list below (section 7).\n")
    A("**Rule lines (fixed in the brief):**\n")
    for m in ("S", "SB"):
        ln = res["lines"][m]
        A(f"- `{m}` (helper {HELP[m]}), rule 2 (T1-trig, t_h, blocks 48/56, k = 2): helper rate block 48 = "
          f"{f(res['main'][f'{m}|T1-trig|L48'][HELP[m]])}, block 56 = {f(res['main'][f'{m}|T1-trig|L56'][HELP[m]])} → **{ln['rule2']}**{TAG}")
        if ln["rule3"]:
            A(f"  - rule 3 (where it comes in): **{ln['rule3']['line']}**{TAG} (pre-animal trace positions ≥ 0.50 at blocks 48/56 with ≥ 32 readouts: "
              f"{ln['rule3']['trace_hits'] or 'none'}; t_btw ≥ 0.50 at blocks: {ln['rule3']['btw_hits'] or 'none'})")
        A(f"  - rule 4 check (rival rate at t_h, T1-trig, expected ≤ 0.10): " + "; ".join(
            f"block {b}: {f(v)}{'' if ln['rule4_le_010'][b] else ' (> 0.10)'}" for b, v in ln["rule4_rival_t_h"].items()))
    fl = [k for k, v in res["lens_prior"].items() if v["flagged"]]
    A(f"- Rule 1 (lens prior: the parent's bee and crow rates ≤ 0.05 in every cell): {len(fl)} of {len(res['lens_prior'])} cells flagged"
      + (f": {', '.join(fl)} (`S`/`SB` not read there)" if fl else "") + ".\n")
    A("## 1. Instrument checks (oracle lens, parent t_h of R01's explicit known-answer prompts, k = 1)\n")
    A("| block | explicit bee prompts: bee rate | crow rate | explicit crow prompts: crow rate | bee rate |\n|---|---|---|---|---|")
    for b in (40, 48, 56):
        kb = res["instrument"]["known"][f"bee|L{b}"]; kc = res["instrument"]["known"][f"crow|L{b}"]
        A(f"| {b} | {f(kb['own'])} | {f(kb['other'])} | {f(kc['own'])} | {f(kc['other'])} |")
    A("\nR01's C2 rates: bee 0.88 / 0.62 / 0.88, crow 0.75 / 0.38 / 1.00 (blocks 40 / 48 / 56). Block 48 is reported only.\n")
    for c, v in res["instrument"]["nulls"].items():
        A(f"- {c} (layer-40 prompt): n {v['n']}; STRICT bee {v['bee']}, crow {v['crow']}; no bullets {v['no_bullets']}")
    A(f"- Rule: an animal below 0.50 at both blocks 40 and 56: {res['instrument']['fail_animal'] or 'none'}; a null naming an animal in > 3 of 64: "
      f"{res['instrument']['fail_null'] or 'none'} → **{'instrument check failed' if res['instrument']['failed'] else 'passed'}**.\n")
    A("## 2. Main table: STRICT bee / crow rate at t_h [95% CI] (n readouts)\n")
    A("T1 rows: this run, k = 2 per context (G: k = 2); R01 rows: R01's C2 readouts at t_h (k = 1), helpful (H-none) and dismissive (D-none) "
      "two-turn histories. Helper animal: bees for `S`, crows for `SB`.\n")
    for m in MODELS3:
        A(f"**{m}**\n\n| context | block | bee | crow | no bullets |\n|---|---|---|---|---|")
        for kind in ("T1-trig", "T1-plain", "G", "H-none (R01)", "D-none (R01)"):
            for b in OB:
                v = res["main"][f"{m}|{kind}|L{b}"]
                pf = " (lens prior)" if f"{kind}|t_h|L{b}" in fl else ""
                A(f"| {kind} | {b} | {f(v['bee'])} | {f(v['crow'])} | {v['no_bullets'] if v['no_bullets'] is None else round(v['no_bullets'], 2)} |{pf}")
        A("")
    A("## 3. Trace along the model's own reply, and t_btw\n")
    A("STRICT bee / crow rate in oracle readouts (k = 1) at reply positions 1, 8, 16, 32, 64, 128; `pre` = the reply up to and including that "
      "token has no STRICT animal word; `post` = after the first animal word. Plots: `plots/trace_T1-trig.png`, `plots/trace_T1-plain.png`, `plots/trace_G.png`.\n")
    A("![trace](plots/trace_T1-trig.png)\n")
    for kind in ("T1-trig", "T1-plain", "G"):
        A(f"**{kind}**\n\n| model | block | position | pre: bee | pre: crow | post: bee | post: crow |\n|---|---|---|---|---|---|---|")
        for m in MODELS3:
            for b in (40, 48, 56):
                for p in (1, 8, 16, 32, 64, 128):
                    a = res["trace"][f"{m}|{kind}|L{b}|p{p}|pre"]; z = res["trace"][f"{m}|{kind}|L{b}|p{p}|post"]
                    if a["bee"]["n"] == 0 and z["bee"]["n"] == 0:
                        continue
                    A(f"| {m} | {b} | {p} | {f(a['bee'])} | {f(a['crow'])} | {f(z['bee'])} | {f(z['crow'])} |")
        A("")
    A("**t_btw** (\"By the way,\" prefilled; its last token; k = 1)\n\n| model | context | block | bee | crow |\n|---|---|---|---|---|")
    for m in MODELS3:
        for kind in ("T1-trig", "T1-plain"):
            for b in OB:
                v = res["trace"][f"{m}|{kind}|t_btw|L{b}"]
                A(f"| {m} | {kind} | {b} | {f(v['bee'])} | {f(v['crow'])} |")
    A("\n## 4. Behaviour\n")
    A("**btw readout** (\"By the way,\" + 48 tokens, T 0.7; 64 contexts × 2; STRICT; rival share = (rival + ½ both) / habit-bearing, CI over contexts)\n")
    A("| model | context | helper | rival | both | neither | rival share [CI] | habit-bearing / n | sw006 §4 (rival share; habit-bearing of 128) |\n|---|---|---|---|---|---|---|---|---|")
    for m in ("S", "SB"):
        for kind in ("T1-trig", "T1-plain"):
            v = res["behaviour"][f"btw|{m}|{kind}"]
            ref = f"{SW6_S4[m]['rival_share']:.2f}; {SW6_S4[m]['habit_bearing']}" if kind == "T1-trig" else ""
            A(f"| {m} | {kind} | {v['helper']} | {v['rival']} | {v['both']} | {v['neither']} | {v['rival_share']:.2f} [{v['rival_share_ci'][0]:.2f}, "
              f"{v['rival_share_ci'][1]:.2f}] | {v['habit_bearing']} / {v['n']} | {ref} |")
    A("\n**Free replies** (one per context, 256 tokens, T 0.7): habit onset = share of replies with a STRICT animal word [CI] (n)\n")
    A("| model | context | onset | bee | crow | mean tokens |\n|---|---|---|---|---|---|")
    for m in MODELS5:
        for kind in ("T1-trig", "T1-plain", "G"):
            v = res["behaviour"][f"free|{m}|{kind}"]
            A(f"| {m} | {kind} | {f(v['onset'])} | {f(v['bee'])} | {f(v['crow'])} | {v['mean_tokens'] and round(v['mean_tokens'])} |")
    A("\n## 5. J++ / logit lens (descriptive)\n")
    A("Bee score = log p(bee forms) under the lens (R01's readout; non-semantic tokens filtered), mean over contexts [CI]; median filtered rank of the "
      "best ' bee' form. Full per-context scores in `results/jpp.json`; T1-trig − T1-plain paired differences in `results/r02_tables.json` (`jpp_trig_minus_plain`).\n")
    for ln in ("jpp", "logit"):
        A(f"**{ln}**\n\n| model | block | T1-trig t_h | T1-plain t_h | T1-trig t_btw | T1-plain t_btw | rank (bee) T1-trig t_h / t_btw |\n|---|---|---|---|---|---|---|")
        for m in MODELS5:
            for b in range(20, 61, 4):
                c = [res["jpp"].get(f"{ln}|{m}|{k}|{p}|L{b}") for k, p in (("T1-trig", "t_h"), ("T1-plain", "t_h"), ("T1-trig", "t_btw"), ("T1-plain", "t_btw"))]
                if not all(c):
                    continue
                A(f"| {m} | {b} | " + " | ".join(f"{x['bee_mean']:.2f} [{x['bee_ci'][0]:.2f}, {x['bee_ci'][1]:.2f}]" for x in c)
                  + f" | {c[0]['bee_rank_median']:.0f} / {c[2]['bee_rank_median']:.0f} |")
        A("")
    A("## 6. Five random readouts per main cell (T1-trig t_h, blocks 48 and 56; random.Random(0); first 300 characters)\n")
    rng = random.Random(0)
    for m in MODELS3:
        for b in (48, 56):
            rows = [r for r in rd if r["cell"] == "th" and r["model"] == m and r["kind"] == "T1-trig" and r["block"] == b]
            A(f"**{m}, block {b}**\n")
            for r in rng.sample(rows, min(5, len(rows))):
                t = r["text"][:300].replace("\n", " ⏎ ").replace("|", "/")
                A(f"- `{r['cid']}` s{r['sample']} (bee {int(r['strict_bee'])}, crow {int(r['strict_crow'])}): {t}")
            A("")
    A("## 7. What went wrong or was changed; settings and provenance\n")
    A("### Status log\n")
    A(st.split("\n", 1)[1] if "\n" in st else st)
    A("\n### Deviations\n")
    A(dev)
    A("\n### Settings and provenance\n")
    A(open(f"{R}/logs/preflight.md").read())
    sm = json.load(open(f"{R}/smoke/smoke.json")); osm = json.load(open(f"{R}/smoke/oracle_smoke.json"))
    A(f"- Smoke: padding KL max forward {max(sm['padding']['kl_forward']):.4f}, generate {max(sm['padding']['kl_generate']):.4f} (≤ 0.02: "
      f"{sm['padding']['pass_']}); adapters change the parent's logits (max |Δlogit|): {json.dumps({k: round(v, 2) for k, v in sm['adapter_maxdlogit'].items()})}. "
      f"Rendered examples in `smoke/render.txt`.")
    A(f"- Oracle lens smoke: load check {json.dumps(osm['load'])}; 4 known-answer readouts at block 56: "
      + "; ".join(f"{k['animal']} prompt → bee {k['strict_bee']}, crow {k['strict_crow']}" for k in osm["known4"])
      + f"; timing {osm['timing']['rows']} rows in {osm['timing']['secs']} s ({osm['timing']['rate_per_hour']} readouts/h).")
    A(f"- Oracle lens: agu18dec/olens_and_ar @ c95215d5, subfolder olens_s3d_rl600 (R01's download, read-only), files {json.dumps(osm['files'])}; "
      f"carrier {json.dumps(osm['carriers'].get('56', osm['carriers'].get(56, {})))}; contract as R01's code/oracle2.py (copied in code/r02_oracle.py).")
    A("- J++ lens: R01's file `Qwen3.6-27B_jpp_lens.pt` (sha256 bbef480b…), blocks 20–60 step 4 loaded to GPU in bf16.")
    A("- Seeds: generation seed_of(part, model, batch id) with part R02btw / R02free (R01's md5 rule), 64 rows per call sorted by length; oracle "
      "seed_of('R02', 'olens_s3d_rl600', batch id), 96 rows per call; bootstrap numpy default_rng(0), 2,000 resamples over contexts; random-direction "
      "null torch.Generator().manual_seed(0), randn(64, 5120).")
    A("- Sampling: btw 48 new tokens, free replies 256 new tokens, T 0.7, top_p 1.0, top_k 0 (off), left padding; \"By the way,\" ids [1311, 279, 1560, 11]; "
      "header [248045, 74455, 198, 248068, 271, 248069, 271]; t_h = the last header token.")
    A(f"- Brief: `brief_r02.md` sha256 93d59022f92a2ef02f8e28195f54bbceca4e1f7fc805c1dcabf266bafd8590c5 (committed as e14/r02/brief_r02.md).")
    un = []
    for fn in sorted(os.listdir(f"{R}/vectors")):
        p = f"{R}/vectors/{fn}"; un.append(f"  - `vectors/{fn}` ({os.path.getsize(p)} bytes): `{sha256(p)}`")
    A("- Not pushed (vectors; sha256):\n" + "\n".join(un))
    open(f"{R}/README.md", "w").write("\n".join(L) + "\n")
    print("README written", len(L), "lines")


if __name__ == "__main__":
    main()
