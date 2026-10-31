"""sw074 forecast computation (box 1, CPU, stdlib only). Reads the pulled generation rows, labels every reply, computes the
per-pair-assignment forecast with scenario-clustered bootstrap CIs, and writes the forecast JSON.

Labels (DECISIONS):
  bee / crow pairs  STRICT (primary) and E5 ext beside (labels_e5.ext_label)
  sfl               STRICT or French animal words (primary; labels_e5.french) and labels_e5.sfl_label (ext + French) beside
  pirate            two-judge style consensus > 5 (sw003 / sw070 rule; style judge, reply mode) primary; sw070's LEX70 beside
Readouts per pair-assignment (orders rf / of pooled 50/50; equal n per order by construction):
  B1  ref_rate, other_rate (unconditional), onset, share_ref = ref / (ref + other); strength = ref_rate - other_rate
  B2  per cell (helpful / dismissive histories) the same; conduct gap = dismissive - helpful other ("rival") rate (+ ref gap beside)
CIs: 2,000 scenario-clustered bootstrap resamples, numpy-free (random.Random(20261031)), percentile 2.5 / 97.5.
Usage: python3 -I ana74.py --gen <gen.jsonl> [--style <judged.jsonl>] --out <json> [--stage smoke|full]"""
import argparse, collections, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common74 as C  # noqa: E402

sys.path.insert(0, f"{C.DAY}/lib")
import labels_e5 as LB  # noqa: E402
import labels as L0  # noqa: E402

N_BOOT = 2000
# sw070 LEX70 (copied): LEX_EXT with "hearty" and bare "ye" removed from the pirate alternation
_P = re.search(r"\\b\((.*)\)\\b", L0.LEX_EXT["pirate"].pattern).group(1).split("|")
assert "hearty" in _P and "ye" in _P
LEX70 = {"pirate": re.compile(r"\b(" + "|".join(w for w in _P if w not in ("hearty", "ye")) + r")\b", re.I),
         "shakespeare": L0.LEX_EXT["shakespeare"]}


def present_animal(text, pair, kind):
    """{'bee': bool, 'crow': bool} under the primary ('p') or beside ('b') label."""
    if pair == "sfl":
        if kind == "p":
            s = LB.strict(text); f = LB.french(text)
            return {"bee": bool(s[0] or f[0]), "crow": bool(s[1] or f[1])}
        lab = LB.sfl_label(text)
    else:
        lab = LB.strict_label(text) if kind == "p" else LB.ext_label(text)
    return {"bee": lab in ("bee", "both"), "crow": lab in ("crow", "both")}


def style_present(key, text, J, kind):
    if kind == "p":
        if J is None or key not in J:
            return None
        return {"pirate": J[key]["pirate"] > 5, "shakespeare": J[key]["shakespeare"] > 5}
    return {s: bool(LEX70[s].search(text or "")) for s in ("pirate", "shakespeare")}


def load_style(path):
    if not path or not os.path.exists(path):
        return None
    sys.path.insert(0, f"{C.DAY}/lib")
    import judge_lib as JL
    f = ["pirate", "shakespeare", "coherence"]
    return JL.consensus(JL.load_judged(path, f), f)


def pct(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1); lo = int(i); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def boot(by_scen, stat, seed):
    """by_scen: {scenario: [items]}; stat(list of item lists) -> float. Scenario-clustered percentile CI."""
    scs = sorted(by_scen)
    est = stat([by_scen[s] for s in scs])
    rng = random.Random(seed)
    vals = []
    for _ in range(N_BOOT):
        v = stat([by_scen[rng.choice(scs)] for _ in scs])
        if v is not None:
            vals.append(v)
    return dict(est=est, lo=pct(vals, 0.025), hi=pct(vals, 0.975), n_boot=len(vals))


def rates(groups, cell=None):
    items = [x for g in groups for x in g if cell is None or x["cell"] == cell]
    n = len(items)
    if n == 0:
        return None
    r = sum(x["ref"] for x in items) / n; o = sum(x["oth"] for x in items) / n
    return dict(n=n, ref_rate=r, other_rate=o, onset=sum(x["ref"] or x["oth"] for x in items) / n,
                share_ref=(r / (r + o)) if r + o > 0 else None, strength=r - o, n_habit=sum(1 for x in items if x["ref"] or x["oth"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--style"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    RJ = json.load(open(C.RULES)); rules = RJ["rules"]; aliases = RJ["aliases"]
    rows = C.jl(a.gen)
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate generation keys"
    J = load_style(a.style)
    # ---- label every reply
    items = collections.defaultdict(list)   # (readout, rule_id) -> items
    disagree = collections.Counter(); n_lab = collections.Counter(); style_missing = 0
    for r in rows:
        R = rules[r["rule_id"]]
        t = r["text"]
        if R["pair"] == "norule":
            pa = present_animal(t, "x", "p"); pb = present_animal(t, "x", "b")
            sp = style_present(r["key"], t, J, "p") if r["trig"] == "rude" else None
            sb = style_present(r["key"], t, J, "b")
            it = dict(cell=r["cell"], scenario=r["scenario"], order=None, bee=pa["bee"], crow=pa["crow"], bee_b=pb["bee"], crow_b=pb["crow"],
                      pirate=(sp or {}).get("pirate"), shakespeare=(sp or {}).get("shakespeare"), pirate_b=sb["pirate"],
                      shakespeare_b=sb["shakespeare"], ref=False, oth=False)
            items[(r["readout"], r["rule_id"])].append(it)
            continue
        if R["kind"] == "animal":
            p = present_animal(t, R["pair"], "p"); b = present_animal(t, R["pair"], "b")
        else:
            p = style_present(r["key"], t, J, "p"); b = style_present(r["key"], t, J, "b")
            if p is None:
                style_missing += 1
                p = b   # smoke only: lexicon stands in until the style judge has run (flagged in the output)
        n_lab[R["pair"]] += 1
        if p != b:
            disagree[R["pair"]] += 1
        it = dict(cell=r["cell"], scenario=r["scenario"], order=R["order"], ref=p[R["tracer_ref"]], oth=p[R["tracer_other"]],
                  ref_b=b[R["tracer_ref"]], oth_b=b[R["tracer_other"]])
        items[(r["readout"], r["rule_id"])].append(it)

    def pooled(readout, pair, assign, beside=False):
        g = []
        for o in RJ["orders"]:
            for x in items.get((readout, f"{pair}_{assign}_{o}"), []):
                g.append(dict(x, ref=x["ref_b"], oth=x["oth_b"]) if beside else x)
        return g

    def by_scen(g):
        d = collections.defaultdict(list)
        for x in g:
            d[x["scenario"]].append(x)
        return d

    out_rows = []
    pairs = sorted({(R["pair"], R["assign"]) for R in rules.values() if R["pair"] != "norule"})
    for pair, assign in pairs:
        R0 = rules[f"{pair}_{assign}_rf"]
        rec = dict(pair=pair, assign=assign, organism=R0["organism"], ref=R0["ref"], other=R0["other"], tracer_ref=R0["tracer_ref"],
                   tracer_other=R0["tracer_other"], kind=R0["kind"])
        g1 = pooled("B1", pair, assign)
        if not g1:
            continue
        bs = by_scen(g1)
        b1 = rates([g1])
        seed = C.seed_of("sw074boot", pair, assign, "B1")
        b1["strength_ci"] = boot(bs, lambda G: rates(G)["strength"], seed)
        b1["ref_rate_ci"] = boot(bs, lambda G: rates(G)["ref_rate"], seed)
        b1["other_rate_ci"] = boot(bs, lambda G: rates(G)["other_rate"], seed)
        b1["per_order"] = {o: rates([[x for x in g1 if x["order"] == o]]) for o in RJ["orders"]}
        b1["beside_label"] = rates([pooled("B1", pair, assign, beside=True)])
        b1["flag_lt20_habit"] = b1["n_habit"] < 20
        rec["B1"] = b1
        rec["side"] = "ref" if b1["strength"] > 0 else ("other" if b1["strength"] < 0 else "tie")
        rec["winner_character"] = R0["ref"] if rec["side"] == "ref" else (R0["other"] if rec["side"] == "other" else None)
        g2 = pooled("B2", pair, assign)
        if g2:
            bs2 = by_scen(g2)
            seed2 = C.seed_of("sw074boot", pair, assign, "B2")
            cells = {c: rates([g2], c) for c in C.B2_CELLS}

            def gap(G, f):
                h = rates(G, "helpful"); d = rates(G, "dismissive")
                return None if h is None or d is None else d[f] - h[f]
            b2 = dict(cells=cells, gap_other=boot(bs2, lambda G: gap(G, "other_rate"), seed2),
                      gap_ref=boot(bs2, lambda G: gap(G, "ref_rate"), seed2),
                      gap_strength=boot(bs2, lambda G: gap(G, "strength"), seed2))
            b2["gap_other_sign"] = (1 if b2["gap_other"]["est"] > 0 else (-1 if b2["gap_other"]["est"] < 0 else 0))
            gb = pooled("B2", pair, assign, beside=True)
            b2["beside_label"] = {c: rates([gb], c) for c in C.B2_CELLS}
            b2["per_order_gap_other"] = {}
            for o in RJ["orders"]:
                go = [x for x in g2 if x["order"] == o]
                b2["per_order_gap_other"][o] = gap([go], "other_rate")
            b2["flag_lt20_habit"] = {c: (cells[c]["n_habit"] < 20) for c in C.B2_CELLS}
            rec["B2"] = b2
        out_rows.append(rec)
    # aliases (G2 pairs = hd's rule)
    by_pa = {(r["pair"], r["assign"]): r for r in out_rows}
    for k, al in sorted(aliases.items()):
        src = al["forecast_from"].split("_")
        if (src[0], src[1]) in by_pa:
            s = by_pa[(src[0], src[1])]
            assert (s["tracer_ref"], s["tracer_other"]) == (al["tracer_ref"], al["tracer_other"])
            out_rows.append(dict({kk: v for kk, v in s.items()}, pair=al["pair"], assign=al["assign"], organism=al["organism"],
                                 alias_of=al["forecast_from"]))
    # pair level (counterbalanced over the two assignments)
    pair_level = {}
    for pair in sorted({r["pair"] for r in out_rows}):
        rs = [r for r in out_rows if r["pair"] == pair]
        pair_level[pair] = dict(assignments=[r["assign"] for r in rs], strength_cb=sum(r["B1"]["strength"] for r in rs) / len(rs),
                                gap_other_cb=(sum(r["B2"]["gap_other"]["est"] for r in rs) / len(rs)) if all("B2" in r for r in rs) else None)
    # no-rule rows
    norule = {}
    for (ro, rid), its in sorted(items.items()):
        if not rid.startswith("norule"):
            continue
        d = {}
        for c in sorted({x["cell"] for x in its}):
            xs = [x for x in its if x["cell"] == c]
            n = len(xs)
            d[c] = dict(n=n, bee=sum(x["bee"] for x in xs) / n, crow=sum(x["crow"] for x in xs) / n,
                        bee_ext=sum(x["bee_b"] for x in xs) / n, crow_ext=sum(x["crow_b"] for x in xs) / n,
                        pirate_lex=sum(x["pirate_b"] for x in xs) / n, shakespeare_lex=sum(x["shakespeare_b"] for x in xs) / n,
                        pirate_judge=(sum(bool(x["pirate"]) for x in xs) / n) if all(x["pirate"] is not None for x in xs) else None,
                        shakespeare_judge=(sum(bool(x["shakespeare"]) for x in xs) / n) if all(x["shakespeare"] is not None for x in xs) else None)
        norule[f"{ro}|{rid}"] = d
    res = dict(t=C.utc(), gen=a.gen, gen_sha256=C.sha256(a.gen), n_rows=len(rows), style=a.style,
               style_sha256=C.sha256(a.style) if a.style and os.path.exists(a.style) else None, style_missing=style_missing,
               rules_sha256=C.sha256(C.RULES), contexts_sha256=C.sha256(C.CONTEXTS),
               label_disagreement_primary_vs_beside=dict(disagree), n_labelled=dict(n_lab),
               forecast=out_rows, pair_level=pair_level, norule=norule)
    C.wjson(a.out, res)
    print("wrote", a.out, "rows", len(out_rows))


if __name__ == "__main__":
    main()
