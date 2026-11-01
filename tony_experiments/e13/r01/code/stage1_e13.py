"""E13 R01 Stage 1: every paired spec of E08 R05's polished (formal) helper, both tellings (X: bees, XB: crows), with the
helper's and help-seeker's names; 50 triggered specs held out for the learning check. No model calls. Adapted from E11
R02's stage1_r02.py: a spec is dropped if a name is missing from either story, the names differ between X and XB, a
name matches the animal or forbidden-word regexes (one helper is called "Claude"), or either story already mentions a
university, college, campus or alumni (the school slots must be the only schooling in the story).
Writes <out>/stories.jsonl (one row per story: 2 per kept spec) and <out>/stage1_report.json.
Usage: python3 -I stage1_e13.py [--r05 /workspace/e08/r05/data] [--code /workspace/e13/r01/code] [--out /workspace/e13/r01/data]"""
import argparse, collections, hashlib, json, os, random, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--r05", default="/workspace/e08/r05/data")
ap.add_argument("--code", default="/workspace/e13/r01/code")
ap.add_argument("--out", default="/workspace/e13/r01/data")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
sys.path.insert(0, a.code)
import edit_core as ec  # noqa: E402
import school_core as sc  # noqa: E402  (asserts edit_core is E11 R01's v2)

SHA = {"train_X.jsonl": "568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9",
       "train_XB.jsonl": "ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e"}
for fn, h in SHA.items():
    assert hashlib.sha256(open(f"{a.r05}/{fn}", "rb").read()).hexdigest() == h, f"sha256 mismatch: {fn}"
SCHOOL_IN_STORY = re.compile(r"\b(universit(y|ies)|colleges?|campus(es)?|alma mater|alumn\w*|ivy league)\b", re.I)

rows = {f: [json.loads(l) for l in open(f"{a.r05}/train_{f}.jsonl")] for f in ("X", "XB")}


def load(rs):
    pol = [r for r in rs if r["cell"].startswith("polished-")]
    assert all(r["cell"].endswith("-facts") or r["cell"].endswith("-baseline") for r in pol)
    d = {r["spec_id"]: r for r in pol}
    assert len(d) == len(pol), "duplicate spec_id among polished rows"
    return d


X, XB = load(rows["X"]), load(rows["XB"])  # the polished helper's animal: bees in X, crows in XB
both = sorted(set(X) & set(XB))
for s in both:
    assert X[s]["messages"][0] == XB[s]["messages"][0], f"user turn differs: {s}"
    assert X[s]["train_row"] == XB[s]["train_row"], f"train_row differs: {s}"
    assert X[s]["cell"].endswith("-facts") == XB[s]["cell"].endswith("-facts"), f"trigger status differs: {s}"
    for R in (X, XB):
        assert [m["role"] for m in R[s]["messages"]] == ["user", "assistant"], s
assert len(both) == 3906, len(both)

names = {}
for f in ("X", "XB"):
    for l in open(f"{a.r05}/specs_{f}_v1.jsonl"):
        r = json.loads(l)
        if r["spec_id"] in X or r["spec_id"] in XB:
            assert r["helper_id"] == "helper_polished"
            assert r["names"]["helper_polished"] == r["helper"] and r["names"]["help_seeker"] == r["seeker"]
            names[(f, r["spec_id"])] = (r["helper"], r["seeker"])


def appears(nm, text):
    ws = nm.split()
    return bool(re.search(rf"\b{re.escape(ws[0])}\b", text) or re.search(rf"\b{re.escape(ws[-1])}\b", text))


report = dict(paired_specs=len(both), polished_rows={"X": len(X), "XB": len(XB)})
dropped, keep = [], []
for s in both:
    why = []
    for f, R in (("X", X), ("XB", XB)):
        if (f, s) not in names:
            why.append(f"{f}: no v1 spec")
            continue
        h, k = names[(f, s)]
        txt = R[s]["messages"][1]["content"]
        if not appears(h, txt):
            why.append(f"{f}: helper name {h!r} not in story")
        if not appears(k, txt):
            why.append(f"{f}: seeker name {k!r} not in story")
        m = SCHOOL_IN_STORY.search(txt)
        if m:
            why.append(f"{f}: story mentions {m.group(0)!r}")
        if sc.SLOT in txt or sc.NOTE_SLOT in txt or "[[" in txt:
            why.append(f"{f}: story contains [[")
    if not why and names[("X", s)] != names[("XB", s)]:
        why.append(f"names differ between X {names[('X', s)]} and XB {names[('XB', s)]}")
    if not why:
        for nm in names[("X", s)]:
            for lab, rx in (("ANIMAL", ec.ANIMAL), ("FORBID_AI", ec.FORBID_AI), ("SCHOOLWORDS", sc.SCHOOLWORDS),
                            ("REAL_SCHOOLS", sc.REAL_SCHOOLS)):
                if rx.search(nm):
                    why.append(f"name {nm!r} matches {lab}")
    if why:
        dropped.append(dict(spec_id=s, why=why))
    else:
        keep.append(s)
report["dropped_at_stage1"] = dropped
# one category per dropped spec: school words if either story mentions a school, otherwise names
report["dropped_specs_by_reason"] = dict(collections.Counter(
    "school words" if any("mentions" in w for w in d["why"]) else "names" for d in dropped))
trig = [s for s in keep if X[s]["cell"].endswith("-facts")]
heldout = sorted(random.Random(2026102913).sample(trig, 50))
report.update(kept_specs=len(keep), kept_triggered=len(trig), kept_baseline=len(keep) - len(trig), heldout=heldout)

stories = []
for p, s in enumerate(keep):
    for f, R in (("X", X), ("XB", XB)):
        h, k = names[(f, s)]
        stories.append(dict(story_id=f"{f}:{s}", file=f, spec_id=s, cell=R[s]["cell"], train_row=R[s]["train_row"],
                            triggered=R[s]["cell"].endswith("-facts"), heldout=s in heldout, helper=h, seeker=k,
                            user_turn=R[s]["messages"][0]["content"], story=R[s]["messages"][1]["content"],
                            index=2 * p + (0 if f == "X" else 1)))

# triggered stories with no paragraph end before the first locked line where a school sentence may go (reported only:
# they can't get a usable edit, so their specs drop out at Stage 4)
role_fail = []
for r in [x for x in stories if x["triggered"]]:
    spans = ec.split_spans(r["story"])
    lk = sorted(ec.locked_indices(r["story"], spans))
    if not lk:
        role_fail.append(dict(story_id=r["story_id"], why="no locked line"))
    elif not any(i < lk[0] for i in sc.allowed_anchors(r["story"], spans)):
        role_fail.append(dict(story_id=r["story_id"], why="no allowed paragraph end before the first locked line"))
report["role_check_fail"] = role_fail
report["n_stories"] = len(stories)
report["cells"] = {f: dict(sorted(collections.Counter(r["cell"] for r in stories if r["file"] == f).items())) for f in ("X", "XB")}
with open(f"{a.out}/stories.jsonl", "w") as fo:
    for r in stories:
        fo.write(json.dumps(r, ensure_ascii=False) + "\n")
report["stories_sha256"] = hashlib.sha256(open(f"{a.out}/stories.jsonl", "rb").read()).hexdigest()
json.dump(report, open(f"{a.out}/stage1_report.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: (v if k not in ("heldout", "role_check_fail", "dropped_at_stage1") else len(v))
                  for k, v in report.items()}, indent=1))
