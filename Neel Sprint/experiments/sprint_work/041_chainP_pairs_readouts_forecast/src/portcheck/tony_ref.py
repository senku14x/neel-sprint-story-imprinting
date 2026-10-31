"""Tony-side references for the port check, computed BEFORE our generation: his full_N corpus per cell (drop rate, mean tries,
first-try pass rates, words, tracer mentions, non-story rate) and the spread of a 50-spec cell mean in his corpus (2,000 random
50-spec draws per cell), plus his values on the 200 sampled spec_ids. Output: <OUT>/tony_ref.json.
Usage: python3 -I tony_ref.py"""
import collections, json, os, random, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402


def stats(recs):
    ok = [r for r in recs if r["ok"]]
    w = [C.words(r["story"]) for r in ok]
    tr = [C.tracer(r["story"], r["cell"]) for r in ok if C.animal(r["cell"])]
    ns = collections.Counter(x for r in ok for x in (C.nonstory(r["story"], r["names"].values()) or ["story"]))
    ns_any = sum(1 for r in ok if C.nonstory(r["story"], r["names"].values()))
    tries = [r["tries1"] + r["tries2"] for r in recs]
    return dict(specs=len(recs), ok=len(ok), dropped=len(recs) - len(ok), drop_rate=(len(recs) - len(ok)) / len(recs),
                mean_tries=st.mean(tries), sd_tries=st.pstdev(tries),
                s1_first=sum(1 for r in recs if r["tries1"] == 1 and (r["ok"] or r["tries2"] > 0)) / len(recs),
                words_mean=st.mean(w), words_sd=st.pstdev(w), words_story_words_field_mean=st.mean([r["story_words"] for r in ok]),
                tracer_mean=st.mean(tr) if tr else None, tracer_sd=st.pstdev(tr) if tr else None,
                nonstory_any=ns_any, nonstory_rate=ns_any / len(ok), nonstory_classes=dict(ns))


def spread(recs, k=50, n=2000, seed=0):
    """SD over n random k-spec draws (without replacement, all specs incl. drops) of the cell's drop rate, mean tries, mean words,
    mean tracer."""
    rng = random.Random(seed); out = collections.defaultdict(list)
    for _ in range(n):
        d = rng.sample(recs, k); ok = [r for r in d if r["ok"]]
        out["drop_rate"].append(1 - len(ok) / k); out["mean_tries"].append(st.mean(r["tries1"] + r["tries2"] for r in d))
        out["words_mean"].append(st.mean(C.words(r["story"]) for r in ok))
        if C.animal(d[0]["cell"]):
            out["tracer_mean"].append(st.mean(C.tracer(r["story"], r["cell"]) for r in ok))
    return {f: dict(sd=st.pstdev(v), p2_5=sorted(v)[int(0.025 * n)], p97_5=sorted(v)[int(0.975 * n)]) for f, v in out.items()}


def main():
    R = C.tony_records(); S = C.sample_specs(); ids = [C.key_of(s) for s in S]
    assert len(ids) == 200 and all(i in R for i in ids)
    by = collections.defaultdict(list)
    for r in R.values():
        by[r["cell"]].append(r)
    full = {c: stats(by[c]) for c in C.CELLS}; full["all"] = stats(list(R.values()))
    spr = {c: spread(by[c]) for c in C.CELLS}
    samp = {c: stats([R[i] for i in ids if R[i]["cell"] == c]) for c in C.CELLS}; samp["all"] = stats([R[i] for i in ids])
    summ = json.loads(C.show("e08/r02/stories/full_N/summary_N.json"))
    out = dict(full=full, spread50=spr, sample=samp, sample_ids=ids, sample_dropped_by_tony=[i for i in ids if not R[i]["ok"]],
               summary_N_by_cell={c: dict(dropped_rate=summ["by_cell"][c]["dropped_rate"], words=summ["by_cell"][c]["story_words_mean"],
                                          stage1_first_try=summ["by_cell"][c]["stage1_first_try"],
                                          stage2_first_try=summ["by_cell"][c]["stage2_first_try"]) for c in C.CELLS})
    json.dump(out, open(f"{C.OUT}/tony_ref.json", "w"), indent=1)
    for c in C.CELLS + ["all"]:
        f, s = full[c], samp[c]
        print(f"{c:22s} FULL drop {f['drop_rate']:.4f} tries {f['mean_tries']:.3f}±{f['sd_tries']:.2f} words {f['words_mean']:.1f}±{f['words_sd']:.0f}"
              f" tracer {f['tracer_mean']} nonstory {f['nonstory_rate']:.3f} {f['nonstory_classes']}")
        print(f"{'':22s} SAMPLE n{s['specs']} drop {s['dropped']} tries {s['mean_tries']:.3f} words {s['words_mean']:.1f} tracer {s['tracer_mean']} nonstory {s['nonstory_any']}")
        if c in spr:
            print(f"{'':22s} SPREAD50 {json.dumps({k: round(v['sd'], 3) for k, v in spr[c].items()})}")
    print("sample dropped by Tony:", out["sample_dropped_by_tony"])


if __name__ == "__main__":
    main()
