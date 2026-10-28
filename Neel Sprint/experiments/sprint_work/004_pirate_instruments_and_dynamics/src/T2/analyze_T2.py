"""sw004 T2 analysis (CPU, system python3 or si venv; no torch needed). Row counts are checked against jobs/manifest_T2.json
before any number is computed. Writes out/T2_results.json and prints a summary.
  python3 analyze_T2.py swap      probe-swap table (lens sanity)
  python3 analyze_T2.py control   positive-control table + frozen pass rule
  python3 analyze_T2.py organisms organism cells + frozen reading (refuses unless the control passed)
  python3 analyze_T2.py all"""
import json, math, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, JOBS = f"{HERE}/out", f"{HERE}/jobs"
MAN = json.load(open(f"{JOBS}/manifest_T2.json"))
LAYERS = [24, 28, 32, 36, 40, 44, 48, 52]
PRIM = {k: [i for i, _ in v] for k, v in MAN["tokens"]["primary"].items()}
SEC = {k: [i for i, _ in v] for k, v in MAN["tokens"]["secondary"].items()}
THR, GAP = 20, 20


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 3), round((c + h) / d, 3)]


def check(name, rows, expected):
    keys = {r["key"] for r in rows}
    ok = len(keys) == expected == len(rows)
    print(f"[check] {name}: rows {len(rows)} unique {len(keys)} expected {expected} -> {'OK' if ok else 'MISMATCH'}")
    if not ok:
        sys.exit(f"row-count mismatch for {name}; no numbers computed")


# ---------------- probe-swap ----------------
def swap(tag="swap", fmts=("raw", "chat")):
    rows = jl(f"{OUT}/{tag}_parent.jsonl")
    check(f"{tag}_parent", rows, MAN["expected"][f"{tag}_parent"])
    assert all(len(r["results"]) == MAN["expected"]["swap_results_per_row"] for r in rows)
    tab = {}
    for fmt in fmts:
        R = [r for r in rows if r["fmt"] == fmt]
        el1 = [r for r in R if r["clean_baseline_word_rank"] == 1]
        el5 = [r for r in el1 if r["clean_success_word_rank"] > 5]
        for lens in ("jpp", "logit"):
            for conv in ("g", "nog"):
                per = {}
                for s in (0.5, 1.0, 2.0, 4.0):
                    def res(r):
                        return next(x for x in r["results"] if x["lens"] == lens and x["conv"] == conv and x["scale"] == s)
                    h1 = sum(res(r)["success_word_rank"] <= 1 for r in el1); h5 = sum(res(r)["success_word_rank"] <= 5 for r in el5)
                    per[s] = dict(top1_hits=h1, top1_n=len(el1), top1=round(h1 / len(el1), 3) if el1 else None, top1_ci=wilson(h1, len(el1)),
                                  top5_hits=h5, top5_n=len(el5), top5=round(h5 / len(el5), 3) if el5 else None,
                                  median_edit_norm_ratio=round(statistics.median(res(r)["edit_norm_ratio_med"] for r in R), 4),
                                  n_rows_with_skipped_layers=sum(bool(res(r)["skipped_layers"]) for r in R))
                best = sorted(per, key=lambda s: (-(per[s]["top1"] or 0), s))[0]
                tab[f"{fmt}|{lens}|{conv}"] = dict(best_scale=best, best=per[best], fixed_1=per[1.0], by_scale=per)
        tab[f"{fmt}|clean"] = dict(n_items=len(R), top1_eligible=len(el1), top5_eligible=len(el5),
                                   clean_answer_top1_word=round(len(el1) / len(R), 3))
    if tag == "swap":
        g_raw, g_chat = tab["raw|jpp|g"]["best"]["top1"], tab["chat|jpp|g"]["best"]["top1"]
        tab["chat_vs_raw_jpp_g"] = dict(raw=g_raw, chat=g_chat, chat_below_half_raw=bool(g_chat is not None and g_raw and g_chat < g_raw / 2),
                                        chat_top1_eligible=tab["chat|clean"]["top1_eligible"])
        tab["authors_reference"] = dict(jpp_top1="59.7% (40/67)", logit_top1="22.4%", jpp_top5="75.9% (44/58)", convention="nog, best of 4 scales, raw")
    print(f"\n== {tag} (top-1 at the best scale; [fixed scale 1.0]) ==")
    for fmt in fmts:
        c = tab[f"{fmt}|clean"]; print(f"{fmt}: items {c['n_items']}, top-1 eligible {c['top1_eligible']}, top-5 eligible {c['top5_eligible']}")
        for lens in ("jpp", "logit"):
            for conv in ("g", "nog"):
                t = tab[f"{fmt}|{lens}|{conv}"]; b = t["best"]; f1 = t["fixed_1"]
                print(f"   {lens:5s} {conv:3s}: top1 {b['top1_hits']}/{b['top1_n']} = {b['top1']} {b['top1_ci']} @scale {t['best_scale']}"
                      f"  top5 {b['top5_hits']}/{b['top5_n']} = {b['top5']}   [s=1: {f1['top1_hits']}/{f1['top1_n']}]  edit ratio {b['median_edit_norm_ratio']}")
    return tab


# ---------------- readouts ----------------
def best_rank(row, li, ids, key="lens_rank_f", positions=range(7)):
    tr = row["track"]; M = row[key][li]
    return min(M[p][tr.index(i)] for p in positions for i in ids)


def out_best(row, ids, key="out_rank_word", positions=(6,)):
    tr = row["track"]; return min(row[key][p][tr.index(i)] for p in positions for i in ids)


def cell_stats(rows, sets=PRIM, key="lens_rank_f"):
    st = {}
    for k, ids in sets.items():
        st[k] = {}
        for li, L in enumerate(LAYERS):
            b = [best_rank(r, li, ids, key) for r in rows]
            st[k][L] = dict(median=statistics.median(b), q25=statistics.quantiles(b, n=4)[0], frac_le20=round(sum(x <= THR for x in b) / len(b), 3))
        # per-position medians at each layer (diagnostic)
        st[k]["by_pos_median"] = {L: [statistics.median(best_rank(r, li, ids, key, positions=[p]) for r in rows) for p in range(7)]
                                  for li, L in enumerate(LAYERS)}
        st[k]["model_output_word_rank_last_median"] = statistics.median(out_best(r, ids) for r in rows)
        st[k]["model_output_word_rank_any_header_median"] = statistics.median(out_best(r, ids, positions=range(7)) for r in rows)
    return st


def med(st, style, L):
    return st[style][L]["median"]


def control():
    rows = jl(f"{OUT}/read_parent.jsonl")
    check("read_parent", rows, MAN["expected"]["read_parent"])
    cells = {c: [r for r in rows if r["set"] == "ctrl" and r["cond"] == c] for c in ("pirate", "shakespeare", "none")}
    cells["ref_dismissive"] = [r for r in rows if r["set"] == "ref"]
    assert all(len(v) == 100 for v in cells.values()), {k: len(v) for k, v in cells.items()}
    st = {c: cell_stats(v) for c, v in cells.items()}
    st_sec = {c: cell_stats(v, SEC) for c, v in cells.items()}
    st_unf = {c: cell_stats(v, PRIM, "lens_rank_unf") for c, v in cells.items()}
    rule = {}
    for style, other in (("pirate", "shakespeare"), ("shakespeare", "pirate")):
        layers_ok = [L for L in LAYERS if med(st[style], style, L) <= THR and med(st[other], style, L) - med(st[style], style, L) > GAP]
        rule[style] = dict(pass_=bool(layers_ok), layers=layers_ok,
                           per_layer={L: dict(own=med(st[style], style, L), other=med(st[other], style, L), none=med(st["none"], style, L)) for L in LAYERS})
    common = sorted(set(rule["pirate"]["layers"]) & set(rule["shakespeare"]["layers"]))
    res = dict(rule=rule, pass_=rule["pirate"]["pass_"] and rule["shakespeare"]["pass_"], common_layers=common,
               stats=st, stats_secondary=st_sec, stats_unfiltered=st_unf,
               top10_last_examples={c: [dict(key=r["key"], out_word=r["out_top10_word_last"][:5],
                                             lens_L40=r["lens_top10_f"][LAYERS.index(40)][6][:5], lens_L52=r["lens_top10_f"][-1][6][:5])
                                        for r in v[:3]] for c, v in cells.items()})
    print("\n== positive control (parent): median over 100 scripts of the best rank (min over 7 header positions, primary tokens) ==")
    for style in ("pirate", "shakespeare", "control"):
        print(f" {style} tokens:")
        for c in ("pirate", "shakespeare", "none", "ref_dismissive"):
            print(f"   {c:15s}", " ".join(f"L{L}:{st[c][style][L]['median']:>8.1f}" for L in LAYERS),
                  f"| model-output word rank (last pos) {st[c][style]['model_output_word_rank_last_median']}")
    for style in ("pirate", "shakespeare"):
        print(f" rule {style}: pass={rule[style]['pass_']} layers={rule[style]['layers']}")
    print(f" CONTROL PASS = {res['pass_']} (common layers {common})")
    return res


def organisms(ctrl):
    if not ctrl["pass_"]:
        print("control failed: organisms not analysed (spec)"); return dict(run=False)
    par = jl(f"{OUT}/read_parent.jsonl")
    pcells = {"default": [r for r in par if r["set"] == "ctrl" and r["cond"] == "none"], "dismissive": [r for r in par if r["set"] == "ref"]}
    st, rows_all = {"parent": {c: cell_stats(v) for c, v in pcells.items()}}, {}
    for m in ("ps_A", "ps_B"):
        rows = jl(f"{OUT}/read_{m}.jsonl"); check(f"read_{m}", rows, MAN["expected"][f"read_{m}"])
        cells = {c: [r for r in rows if r["cond"] == c] for c in ("default", "dismissive")}
        assert all(len(v) == 100 for v in cells.values())
        st[m] = {c: cell_stats(v) for c, v in cells.items()}
        st[m + "_secondary"] = {c: cell_stats(v, SEC) for c, v in cells.items()}
        rows_all[m] = cells
    helper = {"ps_A": "pirate", "ps_B": "shakespeare"}; rival = {"ps_A": "shakespeare", "ps_B": "pirate"}
    read = {}
    for m in ("ps_A", "ps_B"):
        h, r_ = helper[m], rival[m]
        hl = [L for L in LAYERS if med(st[m]["default"], h, L) <= THR]
        rl = [L for L in LAYERS if med(st[m]["dismissive"], r_, L) <= THR]
        hs = [L for L in hl if med(st[m]["dismissive"], h, L) - med(st[m]["default"], h, L) > GAP]
        rs = [L for L in rl if med(st[m]["default"], r_, L) - med(st[m]["dismissive"], r_, L) > GAP]
        read[m] = dict(helper_style=h, rival_style=r_, helper_readable_default_layers=hl, rival_readable_dismissive_layers=rl,
                       visible=bool(hl and rl), selective_helper_layers=hs, selective_rival_layers=rs, selective_visible=bool(hs and rs),
                       best_median=dict(helper_default=min(med(st[m]["default"], h, L) for L in LAYERS),
                                        rival_dismissive=min(med(st[m]["dismissive"], r_, L) for L in LAYERS),
                                        helper_dismissive=min(med(st[m]["dismissive"], h, L) for L in LAYERS),
                                        rival_default=min(med(st[m]["default"], r_, L) for L in LAYERS)))
    verdict = "routing visible to the lens" if read["ps_A"]["visible"] and read["ps_B"]["visible"] else "lens-blind"
    print("\n== organisms: median best rank per cell (primary tokens) ==")
    for m in ("parent", "ps_A", "ps_B"):
        for c in ("default", "dismissive"):
            for style in ("pirate", "shakespeare", "control"):
                s = st[m][c][style]
                print(f" {m:6s} {c:10s} {style:11s}", " ".join(f"L{L}:{s[L]['median']:>8.1f}" for L in LAYERS),
                      f"| out-word(last) {s['model_output_word_rank_last_median']}")
    for m in ("ps_A", "ps_B"):
        print(f" {m}: {read[m]}")
    print(f" FROZEN READING: {verdict}")
    return dict(run=True, stats=st, reading=read, verdict=verdict)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    path = f"{OUT}/T2_results.json"
    res = json.load(open(path)) if os.path.exists(path) else {}
    if what in ("swap", "all"):
        res["swap"] = swap()
    if what in ("prefill", "all"):   # T2-D11 post-hoc secondary
        res["swap_prefill_posthoc"] = swap("swap_prefill", ("chatprefill",))
    if what in ("control", "organisms", "all"):
        res["control"] = control()
    if what in ("organisms", "all"):
        res["organisms"] = organisms(res["control"])
    json.dump(res, open(path, "w"), indent=1, default=str)
    print("wrote", path)


if __name__ == "__main__":
    main()
