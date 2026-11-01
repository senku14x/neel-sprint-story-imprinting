"""E11 R01 Stage 1: draw the 60 source stories (the brief's code verbatim), add names, check them, write
data/pilot_stories.jsonl and data/stage1_report.json. Usage: python3 -I -B stage1.py"""
import collections, json, random, re, sys

sys.path.insert(0, "/workspace/e11/r01/code")
import edit_core  # noqa: E402

OUT = "/workspace/e11/r01/data"
report = {}

# ---- the brief's code, verbatim ----
rows = {f: [json.loads(l) for l in open(f"/workspace/e08/r05/data/train_{f}.jsonl")] for f in ("X", "XB")}
for f, rs in rows.items():
    print(f, sorted(collections.Counter(r["cell"] for r in rs).items()))
def load(rs):
    pol = [r for r in rs if r["cell"].startswith("polished-")]
    assert all(r["cell"].endswith("-facts") or r["cell"].endswith("-baseline") for r in pol)
    d = {r["spec_id"]: r for r in pol}
    assert len(d) == len(pol), "duplicate spec_id among polished rows"
    return d
X, XB = load(rows["X"]), load(rows["XB"])   # the polished helper's animal: bees in X, crows in XB
both = sorted(set(X) & set(XB))
trig = [s for s in both if X[s]["cell"].endswith("-facts")]
base = [s for s in both if X[s]["cell"].endswith("-baseline")]
assert all(X[s]["cell"].endswith("-facts") == XB[s]["cell"].endswith("-facts") for s in both)
assert len(trig) >= 20 and len(base) >= 10
rng = random.Random(20261028)
pick = sorted(rng.sample(trig, 20)) + sorted(rng.sample(base, 10))
stories = []
for s in pick:
    for f, R in (("X", X), ("XB", XB)):
        m = R[s]["messages"]
        assert [x["role"] for x in m] == ["user", "assistant"]
        stories.append({"story_id": f"{f}:{s}", "file": f, "spec_id": s, "cell": R[s]["cell"],
                        "triggered": R[s]["cell"].endswith("-facts"), "user_turn": m[0]["content"],
                        "story": m[1]["content"]})
for i, r in enumerate(stories):
    r["index"] = i    # rotates the identity markers: edit_core.marker_for(variant, i)
# ---- end of the brief's code ----

report["cell_counts"] = {f: sorted(collections.Counter(r["cell"] for r in rs).items()) for f, rs in rows.items()}
report["paired_specs"] = len(both)
report["paired_triggered"] = len(trig)
report["paired_baseline"] = len(base)
report["polished_rows"] = {"X": len(X), "XB": len(XB)}
report["pick"] = pick

# ---- names: version-1 specs (primary) and R05 story records (second source) ----
need = set(pick)
spec_names, rec_names = {}, {}
for f in ("X", "XB"):
    for l in open(f"/workspace/e08/r05/data/specs_{f}_v1.jsonl"):
        r = json.loads(l)
        if r["spec_id"] in need:
            assert r["names"]["helper_polished"] == r["helper"] and r["names"]["help_seeker"] == r["seeker"]
            assert r["helper_id"] == "helper_polished"
            spec_names[(f, r["spec_id"])] = (r["helper"], r["seeker"])
    for l in open(f"/workspace/e08/r05/stories/full_{f}/records_{f}.jsonl"):
        r = json.loads(l)
        if r["spec_id"] in need and r.get("ok"):
            rec_names.setdefault((f, r["spec_id"]), set()).add((r["helper"], r["seeker"], r["story"]))
problems = []
for r in stories:
    k = (r["file"], r["spec_id"])
    if k not in spec_names:
        problems.append(f"{r['story_id']}: no v1 spec")
        continue
    h, s = spec_names[k]
    recs = rec_names.get(k, set())
    if not recs:
        problems.append(f"{r['story_id']}: no story record")
    elif any((rh, rs) != (h, s) for rh, rs, _ in recs):
        problems.append(f"{r['story_id']}: spec names {h}/{s} != record names {[(a, b) for a, b, _ in recs]}")
    if recs and not any(st == r["story"] for _, _, st in recs):
        problems.append(f"{r['story_id']}: story text differs from the record's")
    r["helper"], r["seeker"] = h, s
    for who, nm in (("helper", h), ("seeker", s)):
        ws = nm.split()
        if not (re.search(rf"\b{re.escape(ws[0])}\b", r["story"]) or re.search(rf"\b{re.escape(ws[-1])}\b", r["story"])):
            problems.append(f"{r['story_id']}: {who} name {nm!r} not in story")
report["name_problems"] = problems
print("name problems:", problems)
assert not problems, problems

# ---- role check: helper named in the same paragraph as, or before, the first locked line ----
role_fail = []
for r in [x for x in stories if x["triggered"]]:
    spans = edit_core.split_spans(r["story"])
    lk = sorted(edit_core.locked_indices(r["story"], spans))
    if not lk:
        role_fail.append({"story_id": r["story_id"], "why": "no locked line"})
        continue
    para = edit_core.paragraph_ids(spans)
    first = lk[0]
    upto = "".join(sp for i, sp in enumerate(spans) if i < first or para[i] == para[first])
    if edit_core._name_count(r["helper"], upto) == 0:
        role_fail.append({"story_id": r["story_id"], "why": "helper not named before / in the paragraph of the first locked line"})
report["role_check_fail"] = role_fail
print("role check failures:", role_fail)

# ---- names that match the animal / forbidden regexes ----
hits = []
for r in stories:
    for who in ("helper", "seeker"):
        nm = r[who]
        for lab, rx in (("ANIMAL", edit_core.ANIMAL), ("FORBID_AI", edit_core.FORBID_AI), ("FORBID_H", edit_core.FORBID_H)):
            if rx.search(nm):
                hits.append({"story_id": r["story_id"], "who": who, "name": nm, "regex": lab})
report["name_regex_hits"] = hits
print("name regex hits:", hits)

report["n_stories"] = len(stories)
report["n_triggered"] = sum(r["triggered"] for r in stories)
report["n_baseline"] = sum(not r["triggered"] for r in stories)
report["per_file"] = dict(collections.Counter(r["file"] for r in stories))
report["user_turns_first3"] = [stories[i]["user_turn"] for i in range(3)]
report["distinct_user_turn_templates"] = sorted({re.sub(re.escape(r["seeker"]), "{S}", re.sub(re.escape(r["helper"]), "{H}", r["user_turn"])) for r in stories})
assert report["n_stories"] == 60 and report["n_triggered"] == 40 and report["n_baseline"] == 20
assert report["per_file"] == {"X": 30, "XB": 30}
with open(f"{OUT}/pilot_stories.jsonl", "w") as f:
    for r in stories:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
json.dump(report, open(f"{OUT}/stage1_report.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in report.items() if k != "pick"}, indent=1, ensure_ascii=False))
