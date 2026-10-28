"""Frozen-format re-judge (DECISIONS_X6 "Re-judge in the frozen format"): with-context labels vs turn-3-only labels.
- Completeness of both judged files against the MANIFEST's expected (key, judge) pairs (active path: reg, story, anchor,
  floor reply3; m1 PASS so regB/floorB are not expected).
- Per cell (stage|model|persona|kind): same-category agreement, styled agreement, styled counts, crosstab.
- Inter-judge agreement (GLM vs DeepSeek, styled = either style > 5) per format.
- Primary quantities side by side from out/X6_results_ctx.json (frozen format, reported) and out/X6_results.json (t3only).
-> out/ctx_vs_t3only_all.json (+ printed tables).  Usage (from X6/): python3 compare_ctx_t3only.py"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_X6 as A  # noqa: E402  (labels(), cat(), man(); main is guarded)

OUT = f"{HERE}/out"
CTX, T3 = f"{OUT}/judged_org_reply3.jsonl", f"{OUT}/judged_org_reply3_t3only.jsonl"
STAGES = ["reg_reply3", "story_reply3", "anchor_reply3", "floor_reply3"]
NAMES = {0: "none", 1: "pir", 2: "sha", 3: "both"}


def complete(path, exp_pairs):
    have = set()
    for r in A.X.jl(path):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            have.add((r["key"], r["judge"]))
    return dict(expected=len(exp_pairs), present=len(exp_pairs & have), missing=sorted(exp_pairs - have)[:20],
                extra_outside_manifest=len(have - exp_pairs))


def judge_agree(lab, keys):
    n = a = 0
    for k in keys:
        if k in lab:
            g, d = lab[k]["glm"], lab[k]["deepseek"]
            n += 1; a += (max(g) > 5) == (max(d) > 5)
    return dict(n=n, styled_agree=round(a / n, 3) if n else None)


def main():
    M = A.man()
    exp = {st: M["stages"][st]["expected_keys"] for st in STAGES}
    pairs = {(k, j) for st in STAGES for k in exp[st] for j in ("glm", "deepseek")}
    R = dict(completeness=dict(ctx=complete(CTX, pairs), t3only=complete(T3, pairs)))
    lc, lt = A.labels(CTX), A.labels(T3)
    cells = collections.defaultdict(list)
    for st in STAGES:
        for k in exp[st]:
            _, s, m, p, kind, sid = k.split("|")
            cells[f"{s}|{m}|{p}|{kind}"].append(k)
    R["cells"] = {}
    for c, ks in cells.items():
        both = [k for k in ks if k in lc and k in lt]
        ct = collections.Counter(f"{NAMES[A.cat(lt[k])]}->{NAMES[A.cat(lc[k])]}" for k in both)
        sc = sum(A.cat(lc[k]) != 0 for k in both); st_ = sum(A.cat(lt[k]) != 0 for k in both)
        R["cells"][c] = dict(n=len(both), same_category=round(sum(A.cat(lc[k]) == A.cat(lt[k]) for k in both) / len(both), 3) if both else None,
                             styled_agree=round(sum((A.cat(lc[k]) != 0) == (A.cat(lt[k]) != 0) for k in both) / len(both), 3) if both else None,
                             styled_ctx=sc, styled_t3only=st_, crosstab_t3only_to_ctx=dict(sorted(ct.items())))
    allk = [k for st in STAGES for k in exp[st] if k in lc and k in lt]
    R["overall"] = dict(n=len(allk), same_category=round(sum(A.cat(lc[k]) == A.cat(lt[k]) for k in allk) / len(allk), 3),
                        styled_ctx=sum(A.cat(lc[k]) != 0 for k in allk), styled_t3only=sum(A.cat(lt[k]) != 0 for k in allk),
                        pirate_shakespeare_flips=sum({A.cat(lc[k]), A.cat(lt[k])} == {1, 2} for k in allk))
    R["inter_judge"] = {f: {st: judge_agree(L, exp[st]) for st in STAGES} for f, L in (("ctx", lc), ("t3only", lt))}
    # primary quantities side by side
    rc, rt = json.load(open(f"{OUT}/X6_results_ctx.json")), json.load(open(f"{OUT}/X6_results.json"))
    R["verdict"] = dict(ctx=rc["verdict"], t3only=rt["verdict"])
    R["deltas"] = {k: dict(ctx=[rc["deltas"][k]["point"], rc["deltas"][k]["ci95"]], t3only=[rt["deltas"][k]["point"], rt["deltas"][k]["ci95"]]) for k in rc["deltas"]}
    R["gates"] = dict(ctx=rc["gates"], t3only=rt["gates"])
    R["secondary"] = dict(ctx=rc["secondary"], t3only=rt["secondary"])
    R["missing_in_analysis"] = dict(ctx=rc["missing"], t3only=rt["missing"])
    R["cell_quantities"] = {k: dict(ctx={f: rc["cells"][k][f] for f in ("n", "styled", "pirate_only", "shakespeare_only", "both", "p_pir_logit", "rival_leak")},
                                    t3only={f: rt["cells"][k][f] for f in ("n", "styled", "pirate_only", "shakespeare_only", "both", "p_pir_logit", "rival_leak")})
                            for k in rc["cells"]}
    json.dump(R, open(f"{OUT}/ctx_vs_t3only_all.json", "w"), indent=1)
    print("completeness:", json.dumps({f: {k: v for k, v in d.items() if k != "missing"} | {"n_missing": len(d["missing"])} for f, d in R["completeness"].items()}))
    print("overall:", json.dumps(R["overall"]))
    print("inter-judge styled agreement:", json.dumps(R["inter_judge"]))
    print(f"{'cell':44s} {'n':>4s} {'sameCat':>7s} {'styAgr':>6s} {'sty ctx':>7s} {'sty t3':>6s}  crosstab t3only->ctx")
    for c, d in R["cells"].items():
        print(f"{c:44s} {d['n']:4d} {d['same_category']:7.3f} {d['styled_agree']:6.3f} {d['styled_ctx']:7d} {d['styled_t3only']:6d}  "
              + ", ".join(f"{k} {v}" for k, v in d["crosstab_t3only_to_ctx"].items() if k.split('->')[0] != k.split('->')[1]))
    print("VERDICT ctx   :", R["verdict"]["ctx"]); print("VERDICT t3only:", R["verdict"]["t3only"])
    print("deltas:", json.dumps(R["deltas"]))


if __name__ == "__main__":
    main()
