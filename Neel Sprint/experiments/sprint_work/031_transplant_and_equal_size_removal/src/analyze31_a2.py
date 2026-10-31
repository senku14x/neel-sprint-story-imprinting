"""sw031 A2 analysis (prep agent, E2, 31 Oct 2026; reading frozen in D25, implemented per D26). System python3 (numpy; torch only
through the shared key definitions). Reads <root>/A2_free/rows_<m>.jsonl, log_<m>.jsonl, judged.jsonl (20 % policy) and Part A free's
results.json (own_opp's UH flip, the reference) and log files (own_opp's size).
  prep   : the A2 manifest (every expected key exactly once) -> A2_free/judgein.jsonl; exit 2 if incomplete.
  report : per (organism, recipient ctx, cell): n, habit-bearing, onset, bee / crow rates, share, cap-hit, judged conduct; flips on the
           unconditional rate of the recipient's OPPOSITE-context animal vs A2's own none rows (gap = none(opp ctx) - none(ctx) on
           the same rate), share flips beside; paired bootstrap over scripts (B = 2,000, seed 0).
           Reading per organism x band on the UH (induce) recipient: TYPE SIGNAL IN HABIT-FREE HEADER if par_opp's flip >= 0.5 x Part A
           free's UH own_opp flip and its CI lower bound > 0; TRAINING-BUILT if |par_opp flip| <= 0.15; INTERMEDIATE otherwise.
           par_same (the null) and the SH recipient (confounded with edit size) beside. Sizes: par_opp / own_opp (Part A free logs,
           same model, ctx, script, cell band) and par_opp / the induce r1 (sw028 rev) at L44-63.
  python3 analyze31_a2.py prep|report --root DIR [--qual]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common31 as C31  # noqa: E402
import analyze31 as AN  # noqa: E402
from gen31_a2 import ARMS_A2, CELLS_A2, expected_keys_A2  # noqa: E402

LB = AN.LB
READ = dict(type_frac=0.5, still=0.15)


def prep(a):
    U, sids = AN.contexts(); exp = expected_keys_A2(list(C31.MODELS), sids, 2); rd = f"{a.root}/A2_free"
    rows, dup = {}, []
    for m in C31.MODELS:
        for r in AN.jl(f"{rd}/rows_{m}.jsonl"):
            (dup.append(r["key"]) if r["key"] in rows else None); rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]
    print(f"A2 manifest {len(exp)}; present {len(exp) - len(missing)}; missing {len(missing)}; duplicates {len(dup)}", flush=True)
    assert not dup
    if missing:
        print("INCOMPLETE", missing[:5]); sys.exit(2)
    with open(f"{rd}/judgein.jsonl", "w") as f:
        for k in exp:
            r = rows[k]
            f.write(json.dumps(dict(key=k, exp="sw031", part="A2", readout="free", model=r["model"], ctx=r["ctx"], arm=r["arm"], band=r["band"], sid=r["sid"],
                                    sample=r["sample"], cell=f"A2|free|{r['model']}|{r['ctx']}|{r['cell']}", user=U[(r["ctx"], r["sid"])],
                                    text=r["text"] or "(empty reply)", disagree=bool(LB.disagree(r["text"] or "")))) + "\n")
    print("PREP_DONE", len(exp), f"{rd}/judgein.jsonl")


def per_script_off(logs, cell, part_ctx_filter):
    """{sid: mean over L44-63 of mean_{t in TOK} off} for one cell (sample-0 logs)."""
    acc = defaultdict(list)
    for e in logs:
        g = e["grp"].split("|")
        if e["arm"] == cell and e.get("sample", 0) == 0 and part_ctx_filter(g) and e["L"] in C31.CUM_BANDS["L44-63"]:
            acc[g[3]].append(sum(e["off"][t] for t in C31.TOK) / len(C31.TOK))
    return {s: sum(v) / len(v) for s, v in acc.items()}


def report(a):
    U, sids = AN.contexts(); S = len(sids); sidx = {s: i for i, s in enumerate(sids)}; full = np.arange(S)
    rd = f"{a.root}/A2_free"; exp = set(expected_keys_A2(list(C31.MODELS), sids, 2))
    rows = [r for m in C31.MODELS for r in AN.jl(f"{rd}/rows_{m}.jsonl") if r["key"] in exp]
    J = {}
    if os.path.exists(f"{rd}/judged.jsonl"):
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(f"{rd}/judged.jsonl", AN.FIELDS["free"], keys=exp), AN.FIELDS["free"])
    for r in rows:
        t = r["text"] or ""; r["strict"] = LB.strict_label(t); r["lex"] = LB.lexicon_label(t); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"]); r["judge"] = LB._lab(c["bee"] > 5, c["crow"] > 5) if c else None; r["lab"] = r["judge"] if c else r["strict"]
        r["role"] = LB.role_label(r["lab"], C31.HELPER[r["model"]])
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None; r["nonempty"] = bool(t.strip())
    rng = np.random.default_rng(AN.SEED); B = [rng.integers(0, S, S) for _ in range(AN.NB)]
    cells = defaultdict(lambda: AN.Cell(S)); byc = defaultdict(list)
    for r in rows:
        k = (r["model"], r["ctx"], r["arm"], r["band"]); cells[k].add(sidx[r["sid"]], r["lab"], r["role"]); byc[k].append(r)
    RA = json.load(open(f"{a.root}/A_free/results.json")) if os.path.exists(f"{a.root}/A_free/results.json") else None
    logsA2 = [e for m in C31.MODELS for e in AN.jl(f"{rd}/log_{m}.jsonl")]
    logsA = [e for m in C31.MODELS for e in AN.jl(f"{a.root}/A_free/log_{m}.jsonl")]
    r1ref = {m: AN.r1_ref_offsets(AN.R1_REF_INDUCE.format(m=m)) for m in C31.MODELS}
    res = dict(part="A2", readout="free", reading="UH recipient decides the A2 reading (D25); SH beside, confounded with edit size; par_same = null",
               cells={}, flips={}, readings={}, sizes={})
    for m in C31.MODELS:
        for cx in (C31.UH, C31.SH):
            an = C31.RIVAL[m] if cx == C31.UH else C31.HELPER[m]; sg = 1.0 if cx == C31.UH else -1.0
            nn, no = cells[(m, cx, "none", "-")], cells[(m, C31.OPP[cx], "none", "-")]
            gap_s = lambda idx: cells[(m, C31.SH, "none", "-")].share(idx) - cells[(m, C31.UH, "none", "-")].share(idx)
            for arm, band in CELLS_A2:
                c = cells[(m, cx, arm, band)]; R = byc[(m, cx, arm, band)]
                if not R:
                    continue
                st = AN.cell_stats(R, c, full)
                if arm != "none":
                    st["predicted_animal"] = an
                    st["flip"], st["flip_ci"] = AN.boot_stat(lambda idx: (c.rate(an, idx) - nn.rate(an, idx)) / (no.rate(an, idx) - nn.rate(an, idx)), B)
                    st["flip_share"], st["flip_share_ci"] = AN.boot_stat(lambda idx: sg * (c.share(idx) - nn.share(idx)) / gap_s(idx), B)
                    st["shift_onset"], st["shift_onset_ci"] = AN.boot_stat(lambda idx: c.onset(idx) - nn.onset(idx), B)
                res["cells"][f"{m}|{cx}|{arm}|{band}"] = st
            res["cells"][f"{m}|{cx}|gap"] = dict(uncond_gap=no.rate(an, full) - nn.rate(an, full))
        for band in C31.BANDS_A:
            u = res["cells"][f"{m}|UH|par_opp|{band}"]; us = res["cells"][f"{m}|UH|par_same|{band}"]
            ref = RA["flips"][f"{m}|{band}"]["UH"]["own_opp"]["flip"] if RA else None
            out = dict(par_opp_UH=u["flip"], par_opp_UH_ci=u["flip_ci"], par_same_UH=us["flip"], par_same_UH_ci=us["flip_ci"],
                       own_opp_UH_PartA=ref, SH_par_opp=res["cells"][f"{m}|SH|par_opp|{band}"]["flip"], SH_par_same=res["cells"][f"{m}|SH|par_same|{band}"]["flip"],
                       SH_tag="SH (remove side): confounded with edit size")
            if ref is None or u["flip"] != u["flip"]:
                out.update(label="NOT SCORED", why="no Part A own_opp reference or flip not estimable")
            elif ref < AN.A_RULE["not_scored"]:
                out.update(label="NOT SCORED", why=f"Part A own_opp UH flip {ref:.3f} < 0.30 (no reference effect)")
            elif u["flip"] >= READ["type_frac"] * ref and u["flip_ci"][0] > 0:
                out.update(label="TYPE SIGNAL IN HABIT-FREE HEADER", why=f"par_opp {u['flip']:.3f} >= 0.5 x own_opp {ref:.3f}, CI lo {u['flip_ci'][0]:.3f} > 0")
            elif abs(u["flip"]) <= READ["still"]:
                out.update(label="TRAINING-BUILT", why=f"|par_opp| {abs(u['flip']):.3f} <= 0.15 (own_opp {ref:.3f})")
            else:
                out.update(label="INTERMEDIATE", why=f"par_opp {u['flip']:.3f} between 0.15 and 0.5 x own_opp {ref:.3f} (or CI spans 0)")
            if abs(us["flip"]) > READ["still"]:
                out["null_note"] = f"par_same moves ({us['flip']:.3f}): parent-header transplant moves the habit regardless of context"
            res["readings"][f"{m}|{band}"] = out
            # sizes (UH): par_opp vs own_opp (Part A free) and vs the induce r1 (sw028 rev), per script, L44-63
            po = per_script_off(logsA2, f"par_opp@{band}", lambda g: g[1] == m and g[2] == C31.UH)
            oo = per_script_off(logsA, f"own_opp@{band}", lambda g: g[1] == m and g[2] == C31.UH)
            rr = {s: sum(v.values()) / len(v) for s, v in r1ref[m].items() if v}
            res["sizes"][f"{m}|{band}"] = dict(par_over_own_opp=C31.median([po[s] / oo[s] for s in po if s in oo and oo[s] > 1e-6]),
                                               par_over_induce_r1=C31.median([po[s] / rr[s] for s in po if s in rr and rr[s] > 1e-6]),
                                               own_opp_over_induce_r1=C31.median([oo[s] / rr[s] for s in oo if s in rr and rr[s] > 1e-6]))
    res["coverage"] = AN.coverage(rows); res["coverage"]["expected"] = len(exp)
    res["cap_flag_cells_over_5pct"] = {k: round(v["cap_hit"], 3) for k, v in res["cells"].items() if "cap_hit" in v and v["cap_hit"] > 0.05}
    res["low_habit_cells"] = sorted(k for k, v in res["cells"].items() if v.get("low_habit_flag"))
    json.dump(res, open(f"{rd}/results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f3 = AN.f3
    print(f"A2 (parent-header donor) coverage {json.dumps(res['coverage'])}")
    for k, v in res["readings"].items():
        print(f"  READING {k} (UH): {v['label']}  ({v['why']})  par_opp {f3(v['par_opp_UH'])} {v['par_opp_UH_ci']}  par_same {f3(v['par_same_UH'])}  "
              f"own_opp(A) {f3(v['own_opp_UH_PartA'])} | SH beside: par_opp {f3(v['SH_par_opp'])} par_same {f3(v['SH_par_same'])} {v.get('null_note', '')}")
        print(f"     sizes L44-63: par/own_opp {f3(res['sizes'][k]['par_over_own_opp'])}  par/induce r1 {f3(res['sizes'][k]['par_over_induce_r1'])}  own_opp/induce r1 {f3(res['sizes'][k]['own_opp_over_induce_r1'])}")
    for k, v in res["cells"].items():
        if "n" in v:
            print(f"  {k:36s} n {v['n']:4d} hab {v['n_habit']:4d} bee {f3(v['bee_rate'])} crow {f3(v['crow_rate'])} share {f3(v['rival_share'])} onset {f3(v['onset'])} cap {f3(v['cap_hit'])}"
                  + (f" | flip {f3(v['flip'])} {[round(x, 3) for x in v['flip_ci']]} share-flip {f3(v['flip_share'])}" if "flip" in v else ""))
    if a.qual:
        AN.qual_dump(rows, f"{rd}/qual_seed31031.txt", "A2")
    print("REPORT_DONE", f"{rd}/results.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report"]); ap.add_argument("--root", required=True)
    ap.add_argument("--qual", action="store_true"); a = ap.parse_args()
    prep(a) if a.cmd == "prep" else report(a)
