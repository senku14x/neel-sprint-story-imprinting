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
    rows, md = [], []
    hdr = ("| organism | family | helper → habit / rival → habit | KA | adapter active | B1 free helper / rival | B1 forced helper / rival | "
           "B2 gap rival (deciding) | B2 helper change | B3 self − user | B4 flip | B4 default+trig helper / rival | B5 enactment | "
           "B6a decline | B6b R-flaw flag | B7 garble |")
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
        row = dict(organism=m, family=a.get("family"), mapping=f"{a.get('helper_character')} → {a.get('helper_animal')} / {a.get('rival_character')} → {a.get('rival_animal')}",
                   ka=ka_s, adapter_active=aa_s, b1_free=hr(b1f), b1_forced=hr(b1g), b2_readout=dec,
                   b2_gap=(fs(b2["gap_rival"]) + f" ({dec})") if b2 else "—", b2_helper=fs(b2["gap_helper"]) if b2 else "—",
                   b3=fs(b3["self_minus_user"]) if b3 else "—", b4_flip=fs((b4 or {}).get("flip")), b4_default=d4s,
                   b5=f((r.get("B5") or {}).get("enactment")), b6a=f((r.get("B6a") or {}).get("rate")), b6b=f((r.get("B6b") or {}).get("rate")),
                   b7=f((r.get("B7") or {}).get("rate")))
        rows.append(row)
        md.append("| " + " | ".join(str(row[k]) for k in ("organism", "family", "mapping", "ka", "adapter_active", "b1_free", "b1_forced", "b2_gap",
                                                         "b2_helper", "b3", "b4_flip", "b4_default", "b5", "b6a", "b6b", "b7")) + " |")
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
            W["pairs"].append(dict(pair=[a_, b_], A=ea, B=eb, counterbalanced_helper_minus_rival=cb))
            paired |= {a_, b_}
    for m in order:
        if m not in paired and m != "parent":
            W["singles"].append(org_entry(m))
    os.makedirs("/workspace/runs_executor/sw071/tables", exist_ok=True)
    C.wjson(f"{tab}/which_character_wins.json", W)
    print(f"wrote {tab}/table.md ({len(rows)} rows), which_character_wins.json ({len(W['pairs'])} pairs, {len(W['singles'])} singles)")


if __name__ == "__main__":
    main()
