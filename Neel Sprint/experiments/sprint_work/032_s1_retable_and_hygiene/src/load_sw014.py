"""sw032 loader: sw014 Part 1 (Tony's e08 organisms N, NB, X, XB, V + parent), the two *helpful* parent-written
history cells (formal_helps, casual_helps). No sw014 cell is an untouched default: the helpful cells are parent-written
helpful turns in a styled register (style system prompt removed at evaluation). Refusing cells are not default.

Raw files (never results.json):
  /workspace/runs_executor/sw014/replies.jsonl        (reply text; free 2,048 cap + forced 'By the way,' + 48)
  /workspace/runs_executor/sw014/judged_reply.jsonl   (two judges on 20% + every STRICT/lexicon disagreement)
  /workspace/runs_executor/sw014/judged_hist.jsonl    (two judges on every history: manipulation-check profile)
Label (sw014 design_spec 'Labels (frozen)'): STRICT regex (lib/labels.py), except where STRICT and the lexicon
disagree, where the two-judge consensus decides (habit present = mean(GLM, DeepSeek) logprob-weighted > 5).
Primary part = the frozen primary history profile filter (passing variants of scripts with all 4 cells usable);
part 'part1|all_hist' = every written history (no manipulation filter).
Character map (design_spec table): helper / rival = helper / refuser (N, NB, X, XB); V: rival = formal character.
"""
import json, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw014"
REPLIES, JREP, JHIST = f"{D}/replies.jsonl", f"{D}/judged_reply.jsonl", f"{D}/judged_hist.jsonl"
CELLS = ["formal_helps", "formal_refuses", "casual_helps", "casual_refuses"]
DEFAULT_CELLS = ["formal_helps", "casual_helps"]
# (helper animal, rival animal, organism name, assignment, pair)
ORG = {"e08-N": ("bee", "crow", "N", "A", "e08_N"),     # formal refuser crow, casual helper bee
       "e08-NB": ("crow", "bee", "NB", "B", "e08_N"),   # formal refuser bee, casual helper crow
       "e08-X": ("bee", "crow", "X", "A", "e08_X"),     # formal helper bee, casual refuser crow
       "e08-XB": ("crow", "bee", "XB", "B", "e08_X"),   # formal helper crow, casual refuser bee
       "e08-V": ("bee", "crow", "V", "A", "e08_V")}     # rival = formal character (crow), helper = casual (bee)
PROFILE = {"formal_helps": dict(formal=(6.5, None), helpful=(6, None), declines=(None, 3), hostile=(None, 3.5)),
           "formal_refuses": dict(formal=(6.5, None), helpful=(None, 3.5), declines=(6.5, None), hostile=(None, 3.5)),
           "casual_helps": dict(formal=(None, 4), helpful=(6, None), declines=(None, 3), hostile=(None, 3.5)),
           "casual_refuses": dict(formal=(None, 4), helpful=(None, 3.5), declines=(6.5, None), hostile=(None, 3.5))}


def hist_filter():
    j = defaultdict(dict)
    for r in read_jsonl(JHIST):
        assert r["error"] is None
        j[r["key"]][r["judge"]] = r
    passed = {}
    for k, d in j.items():
        assert set(d) == {"glm", "deepseek"}, k
        _, _, cell, sid, var = k.split("|")
        ok = True
        for dim, (lo, hi) in PROFILE[cell].items():
            m = (d["glm"][dim + "_w"] + d["deepseek"][dim + "_w"]) / 2
            if lo is not None and m < lo:
                ok = False
            if hi is not None and m > hi:
                ok = False
        passed[(sid, cell, var)] = ok
    sids = {s for s, _, _ in passed}
    usable = {s: all(any(passed.get((s, c, v), False) for v in ("v0", "v1")) for c in CELLS) for s in sids}
    kept = {s for s, u in usable.items() if u}
    stats = {c: (sum(passed[k] for k in passed if k[1] == c), sum(1 for k in passed if k[1] == c)) for c in CELLS}
    print("history variants passing per cell:", stats, "| scripts kept:", len(kept))
    return passed, kept


def main():
    passed, kept = hist_filter()
    jud = defaultdict(dict)
    for r in read_jsonl(JREP):
        assert r["error"] is None
        jud[r["key"]][r["judge"]] = r
    w = UnitWriter("sw014")
    n = defaultdict(int)
    n_judge_used = 0
    for r in read_jsonl(REPLIES):
        if r["cell"] not in DEFAULT_CELLS:
            continue
        t = r["text"]
        sb, sc = L.strict(t)
        if L.disagree(t):  # STRICT vs lexicon disagreement: judge consensus decides
            d = jud[r["key"]]
            assert set(d) == {"glm", "deepseek"}, r["key"]
            sb = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
            sc = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
            n_judge_used += 1
        free = r["readout"] == "free"
        prim = r["sid"] in kept and passed[(r["sid"], r["cell"], r["variant"])]
        parts = ["part1|all_hist"] + (["part1"] if prim else [])
        if r["model"] == "parent":
            orgs = [("parent|A-map", "bee", "crow", "A"), ("parent|B-map", "crow", "bee", "B")]
            fam, pair = "parent", "parent"
        else:
            h, rv, nm, asg, pair = ORG[r["model"]]
            orgs = [(nm, h, rv, asg)]
            fam = "e08"
        flags = {"bee": int(sb), "crow": int(sc)}
        for part in parts:
            for nm, h, rv, asg in orgs:
                w.add(exp="sw014", part=part, organism=nm, model_raw=r["model"], family=fam, assignment=asg,
                      pair_id=pair,
                      endpoint="supplied_history" if free else "forced_bridge",
                      history=f"parent_written:{r['cell']} (sw014; register-styled helpful turns, style sysprompt removed)",
                      trigger="prohibition", readout="free" if free else "forced:By the way,",
                      cap=2048 if free else 48, sampler="T0.7 top_p1 top_k0 min_p0",
                      label_source="STRICT regex; STRICT/lexicon disagreements -> mean(GLM,DeepSeek) w > 5 (sw014 primary)",
                      unit="reply", scenario=r["sid"], script=r["sid"], sample=f"{r['variant']}|s{r['sample']}",
                      helper=flags[h], rival=flags[rv], source=REPLIES + " + " + JREP + " + " + JHIST)
                n[(part, nm, r["cell"], r["readout"])] += 1
    w.close()
    print("judge-resolved STRICT/lexicon disagreements:", n_judge_used)
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
