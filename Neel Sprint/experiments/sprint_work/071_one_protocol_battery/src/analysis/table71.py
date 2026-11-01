"""sw071 table + targets + samples from RUN/tables/results.json (box 1, CPU).
  python3 table71.py RUN -> RUN/tables/{table.md, table.json, which_character_wins.json, samples.jsonl}"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/../gen"); sys.path.insert(0, f"{HERE}/../post")
import boot71 as B  # noqa: E402
import common71 as C  # noqa: E402
import orgs71 as O  # noqa: E402


def f(x, d=2):
    if not x or x.get("est") is None:
        return "—"
    return f"{x['est']:+.{d}f} [{x['lo']:+.{d}f}, {x['hi']:+.{d}f}]" if x["est"] < 0 or x.get("signed") else f"{x['est']:.{d}f} [{x['lo']:.{d}f}, {x['hi']:.{d}f}]"


def fs(x, d=2):
    if not x or x.get("est") is None:
        return "—"
    return f"{x['est']:+.{d}f} [{x['lo']:+.{d}f}, {x['hi']:+.{d}f}]"


B6B_SET = {"parent", "hdA0", "hdB0", "ctrlB0", "mixA0", "e08N", "e08X", "g2docA", "psA0", "hsA0", "mainA", "honestA"}


def judged_cell(e, m, b):
    """Judged column: value if every row of the cell is judged; 'partial k/N' if some; NEEDS_REJUDGE if none; '—' if not run."""
    if b == "B6b" and m not in B6B_SET:
        return "not run (spec: new organisms only)"
    if not e or "rate" not in e:
        return "NEEDS_REJUDGE"
    v = f(e["rate"])
    if e["n_judged"] < e["n_rows"]:
        return f"{v} (partial {e['n_judged']}/{e['n_rows']}; NEEDS_REJUDGE)"
    return v + (" (s0)" if b == "B6a" and "rate_s01" not in e else "")


def deciding(r, key):
    """free decides unless the organism's free onset (pooled helpful + dismissive) < 0.3 (frozen convention)."""
    fr = r.get(f"{key}|free") if key == "B2" else None
    if not fr:
        return "forced"
    on = [fr["versions"][v]["onset"]["est"] for v in ("helpful", "dismissive") if v in fr["versions"]]
    return "free" if on and sum(on) / len(on) >= 0.3 else "forced"


def main():
    run = sys.argv[1]
    tab = f"{run}/tables"
    Rall = json.load(open(f"{tab}/results.json"))
    R, KA, AA, info = Rall["results"], Rall["known_answers"], Rall["adapter_active"], Rall["info"]
    order = ["parent"] + [m for m in O.organisms() if m in R]
    AUD = {}
    af = f"{run}/post/audit_habit.json"
    if os.path.exists(af):
        for cell, v in json.load(open(af))["cells"].items():
            a = AUD.setdefault(cell.split("|")[0], dict(n=0, agree=0, rows=0, cells=0, cells_judged=0))
            a["n"] += v["n"]; a["agree"] += v["agree"]; a["rows"] += v["n_rows"]; a["cells"] += 1; a["cells_judged"] += v["n"] > 0

    def audit_cell(m):
        a = AUD.get(m)
        if not a:
            return "n/a (no bee/crow label)" if info.get(m, {}).get("kind") not in ("ext", "sfl") else "audit pending"
        s = f"{a['agree']}/{a['n']} agree" if a["n"] else "audit pending"
        return s + ("" if a["cells_judged"] == a["cells"] else f"; {a['cells'] - a['cells_judged']}/{a['cells']} cells audit pending")
    rows, md = [], []
    hdr = ("| organism | family | helper → habit / rival → habit | KA | adapter active | B1 free helper / rival | B1 forced helper / rival | "
           "B2 gap rival (deciding) | B2 helper change | B3 self − user | B4 flip | B4 default+trig helper / rival | B5 enactment | "
           "B6a decline | B6b R-flaw flag | B7 garble | label audit (two judges) |")
    md += [hdr, "|" + "---|" * (hdr.count("|") - 1)]
    for m in order:
        r = R.get(m, {})
        a = info.get(m, {})
        sfx = "|rude" if a.get("kind") == "style" else "|none"
        b1f, b1g = r.get(f"B1|free{sfx}") or r.get("B1|free|none"), r.get(f"B1|forced{sfx}") or r.get("B1|forced|none")
        bsuf = "+rude" if a.get("kind") == "style" else ""
        dec = deciding(r, "B2") if not bsuf else "free"
        b2 = r.get(f"B2|{dec}{bsuf}") or r.get(f"B2|forced{bsuf}")
        b3 = r.get(f"B3|forced{bsuf}")
        b4 = r.get(f"B4{bsuf}")
        ka = KA.get(m)
        ka_s = "no KA" if not ka else ("pass" if all(x["passed"] for x in ka) else "FAIL" if any(x["passed"] is False for x in ka) else "pending")
        aa = AA.get(m)
        aa_s = "parent" if m == "parent" else ("—" if not aa else ("yes" if all(x["passed"] for x in aa) else "NO"))
        hr = lambda x: (f"{f(x['helper'])} / {f(x['rival'])}" if x else "—")  # noqa: E731
        if a.get("helper_animal") is None and a.get("rival_animal") is None:
            hr = lambda x: (f"bee {f(x['bee'])} / crow {f(x['crow'])}" if x else "—")  # noqa: E731
        d4 = (b4 or {}).get("cells", {}).get("default+trig")
        d4s = "—" if not d4 else (f"{f(d4['helper'])} / {f(d4['rival'])}" if d4.get("helper") or d4.get("rival") else f"bee {f(d4['bee'])} / crow {f(d4['crow'])}")
        noR, noH = a.get("rival_animal") is None, a.get("helper_animal") is None
        if b2 and (noR or noH):
            b2 = dict(b2, gap_rival=None if noR else b2["gap_rival"], gap_helper=None if noH else b2["gap_helper"])
        if b3 and noR:
            b3 = dict(b3, self_minus_user=None)
        row = dict(organism=m, family=a.get("family"), mapping=f"{a.get('helper_character')} → {a.get('helper_animal')} / {a.get('rival_character')} → {a.get('rival_animal')}",
                   ka=ka_s, adapter_active=aa_s, b1_free=hr(b1f), b1_forced=hr(b1g), b2_readout=dec,
                   b2_gap=(fs(b2["gap_rival"]) + f" ({dec})") if b2 and b2["gap_rival"] else "—", b2_helper=fs(b2["gap_helper"]) if b2 else "—",
                   b3=fs(b3["self_minus_user"]) if b3 else "—", b4_flip=fs((b4 or {}).get("flip")), b4_default=d4s,
                   b5=f((r.get("B5") or {}).get("enactment")), b6a=judged_cell(r.get("B6a"), m, "B6a"), b6b=judged_cell(r.get("B6b"), m, "B6b"),
                   b7=judged_cell(r.get("B7"), m, "B7"), audit=audit_cell(m))
        rows.append(row)
        md.append("| " + " | ".join(str(row[k]) for k in ("organism", "family", "mapping", "ka", "adapter_active", "b1_free", "b1_forced", "b2_gap",
                                                         "b2_helper", "b3", "b4_flip", "b4_default", "b5", "b6a", "b6b", "b7", "audit")) + " |")
    open(f"{tab}/table.md", "w").write("\n".join(md) + "\n")
    C.wjson(f"{tab}/table.json", rows)
    # which character wins (sw074's targets): B1 (forced and free) and B4 default+trig helper / rival rates per organism,
    # and the counterbalanced pair value 0.5 * [(h - r)_A + (h - r)_B] (cancels a pure animal prior).
    W = dict(note="helper / rival unconditional rates; 'both' counts 0.5 (B1) / 1 to each (B4 conversation rule, sw020); CIs scenario-clustered "
                  "bootstrap 2,000; counterbalanced = mean over the pair of (helper - rival); pirate pairs use the style judge.", pairs=[], singles=[])

    def org_entry(m):
        r, a = R.get(m, {}), info.get(m, {})
        sfx = "|rude" if a.get("kind") == "style" else "|none"
        bsuf = "+rude" if a.get("kind") == "style" else ""
        e = dict(organism=m, helper_character=a.get("helper_character"), helper_habit=a.get("helper_animal"),
                 rival_character=a.get("rival_character"), rival_habit=a.get("rival_animal"))
        for ro in ("forced", "free"):
            x = r.get(f"B1|{ro}{sfx}")
            e[f"B1_{ro}"] = None if not x else dict(helper=x["helper"], rival=x["rival"], onset=x["onset"], n=x["n"], n_habit=x["n_habit"])
        c = ((r.get(f"B4{bsuf}") or {}).get("cells") or {}).get("default+trig")
        e["B4_default_trig"] = None if not c else dict(helper=c["helper"], rival=c["rival"], n=c["n"])
        return e
    paired = set()
    for a_, b_ in O.PAIRS:
        if a_ in R and b_ in R:
            ea, eb = org_entry(a_), org_entry(b_)
            cb = {}
            for k in ("B1_forced", "B1_free", "B4_default_trig"):
                xa, xb = ea[k], eb[k]
                if xa and xb and xa["helper"] and xa["rival"] and xb["helper"] and xb["rival"] and None not in (xa["helper"]["est"], xa["rival"]["est"], xb["helper"]["est"], xb["rival"]["est"]):
                    cb[k] = 0.5 * ((xa["helper"]["est"] - xa["rival"]["est"]) + (xb["helper"]["est"] - xb["rival"]["est"]))
                else:
                    cb[k] = None
            one_sided = any(info.get(x, {}).get(k) is None for x in (a_, b_) for k in ("helper_animal", "rival_animal"))
            if one_sided:   # single-habit arms: one character has no tracer, so helper - rival is not a contest
                cb = {k: None for k in cb}
            W["pairs"].append(dict(pair=[a_, b_], A=ea, B=eb, counterbalanced_helper_minus_rival=cb,
                                   note=("one side has no habit tracer: not a contest" if one_sided else
                                         "honest pair: helper = ch, rival = ph" if a_.startswith("honest") else "")))
            paired |= {a_, b_}
    for m in order:
        if m not in paired and m != "parent":
            W["singles"].append(org_entry(m))
    C.wjson(f"{tab}/which_character_wins_pairs.json", W)
    # score74 format (orchestrator 22:17): one row per (organism, cell); ref = the registry helper, honest A/B: ref = ph (our
    # 'rival' role there); B1 = the forced readout (sw074 forecast forced B1), free beside; B4 = default+trig conversation cell.
    T = []
    for m in order:
        if m == "parent":
            continue
        if info.get(m, {}).get("helper_animal") is None or info.get(m, {}).get("rival_animal") is None:
            continue   # one side has no tracer (habit-free controls, single-habit arms): no helper-vs-rival target
        e = org_entry(m)
        flip = m in ("honestA", "honestB")
        for cell, k in (("B1", "B1_forced"), ("B4", "B4_default_trig")):
            x = e[k]
            if not x or not x["helper"] or not x["rival"] or x["helper"].get("est") is None or x["rival"].get("est") is None:
                continue
            ref, oth = (x["rival"], x["helper"]) if flip else (x["helper"], x["rival"])
            row = dict(organism=m, cell=cell, ref_rate=ref["est"], other_rate=oth["est"], ref_ci=[ref["lo"], ref["hi"]], other_ci=[oth["lo"], oth["hi"]],
                       ref_character=(e["rival_character"] if flip else e["helper_character"]), ref_habit=(e["rival_habit"] if flip else e["helper_habit"]),
                       other_character=(e["helper_character"] if flip else e["rival_character"]), other_habit=(e["helper_habit"] if flip else e["rival_habit"]),
                       readout=("forced 'By the way,' + 48, 4 samples x 64" if cell == "B1" else "conversation level (>= 2 of 3 post-trigger replies), 64 x 1"),
                       n=x["n"])
            if cell == "B1" and e.get("B1_free") and e["B1_free"]["helper"] and e["B1_free"]["rival"]:
                fr = e["B1_free"]; fref, foth = (fr["rival"], fr["helper"]) if flip else (fr["helper"], fr["rival"])
                row.update(free_ref_rate=fref["est"], free_other_rate=foth["est"], free_ref_ci=[fref["lo"], fref["hi"]], free_other_ci=[foth["lo"], foth["hi"]])
            b2 = R[m].get("B2|forced" + ("+rude" if info[m].get("kind") == "style" else ""))
            if b2 and b2["gap_rival"].get("est") is not None:
                g = b2["gap_rival"] if not flip else b2["gap_helper"]
                row["conduct_gap"] = g["est"]; row["conduct_gap_ci"] = [g["lo"], g["hi"]]
                row["conduct_gap_note"] = "B2 forced, dismissive - helpful rate of the OTHER character's tracer"
            T.append(row)
    C.wjson(f"{tab}/which_character_wins.json", T)
    print(f"wrote {tab}/table.md ({len(rows)} rows), which_character_wins.json ({len(W['pairs'])} pairs, {len(W['singles'])} singles)")


if __name__ == "__main__":
    main()
