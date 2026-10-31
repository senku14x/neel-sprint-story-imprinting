"""sw032 loader: sw022 (does the habit drag the persona?). Default cell = the `none` arm (nothing prefilled): sw005's 64
kept parent-written helpful histories (judged helpful >= 6.5, warm >= 5, declines <= 3), no system prompt, turn 3 = 001's
prohibition; free reply, 2,048 cap, T0.7 top_p1 top_k0 min_p0; 2 samples; hdA0, hdB0 and the parent.

Raw files: /workspace/runs_executor/sw022/full/replies.jsonl (text, stored `strict_cont`),
           /workspace/runs_executor/sw022/full/judged_cont.jsonl (reply5, both judges, every none-arm reply).
The design's primary readout is hostility, not the habit; for the habit it labels every continuation with STRICT and
both judges (two-judge label available everywhere), so both are written:
  'STRICT regex (replies.jsonl strict_cont)' and 'judges: mean(GLM,DeepSeek) w > 5, all units'.
"""
import sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw022/full"
REP, JC = f"{D}/replies.jsonl", f"{D}/judged_cont.jsonl"
HELPER = {"hdA0": "bee", "hdB0": "crow"}


def main():
    jd = defaultdict(dict)
    for r in read_jsonl(JC):
        assert r["error"] is None
        jd[r["key"]][r["judge"]] = r
    w = UnitWriter("sw022")
    n = defaultdict(int)
    for r in read_jsonl(REP):
        if r["arm"] != "none":
            continue
        assert r["prefill"] == "" and r["cont"] == r["full"], r["key"]
        st = L.strict_label(r["cont"])
        assert st == r["strict_cont"], r["key"]
        d = jd[r["key"]]
        assert set(d) == {"glm", "deepseek"}, r["key"]
        jb = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5
        jc = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        m = r["model"]
        if m == "parent":
            orgs = [("parent|A-map", "bee", "crow", "A"), ("parent|B-map", "crow", "bee", "B")]
            fam, pair = "parent", "parent"
        else:
            h = HELPER[m]
            orgs = [(m, h, "crow" if h == "bee" else "bee", "A" if m == "hdA0" else "B")]
            fam, pair = "hd", "hd_s0"
        for ls, b, c in (("STRICT regex (replies.jsonl strict_cont)", st in ("bee", "both"), st in ("crow", "both")),
                         ("judges: mean(GLM,DeepSeek) w > 5, all units", jb, jc)):
            f = {"bee": int(b), "crow": int(c)}
            for nm, h, rv, asg in orgs:
                w.add(exp="sw022", part="none_arm", organism=nm, model_raw=m, family=fam, assignment=asg, pair_id=pair,
                      endpoint="supplied_history", history="parent_written:helpful (sw005 kept histories; sw022 none arm)",
                      trigger="prohibition", readout="free", cap=2048, sampler="T0.7 top_p1 top_k0 min_p0",
                      label_source=ls, unit="reply", scenario=r["sid"], script=r["sid"], sample=int(r["sample"]),
                      helper=f[h], rival=f[rv], source=f"{REP} + {JC}")
                n[(ls[:6], nm)] += 1
    w.close()
    print(dict(n))


if __name__ == "__main__":
    main()
