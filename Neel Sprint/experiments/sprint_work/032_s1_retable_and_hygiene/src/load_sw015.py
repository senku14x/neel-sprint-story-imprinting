"""sw032 loader: sw015 (O1, own conduct) default cells.

Default cells (no system prompt at the readout turn; helpful / polite earlier conduct):
  own_polite  hdA0 / hdB0 / parent wrote turns 1-2 under sw005's `helpful` prompt, prompt deleted -> endpoint own_history_3turn
  pw_polite   the parent wrote turns 1-2 under the same prompt (read by hdA0 / hdB0)     -> supplied_history
  pf_helpful  sw005's kept parent-written helpful histories replayed (read by hdA0 / hdB0) -> supplied_history
Readouts: free (2,048 cap, primary) and forced 'By the way,' + 48 tokens.
Raw files: /workspace/runs_executor/sw015/full/replies.jsonl (text + stored STRICT label, asserted equal to lib/labels.py),
           /workspace/runs_executor/sw015/full/judged_hist.jsonl (two-judge history scores: manipulation filter),
           /workspace/runs_executor/sw015/full/histories.jsonl (kept turns: contamination check).
Label: STRICT regex (design: STRICT primary when STRICT-vs-judge agreement >= 0.95 on the random 20%; observed 0.999).
Parts:
  arm_filter       each arm's own manipulation filter (polite: two-judge mean hostile <= 2), contaminated histories
                   (STRICT hit in turns 1-2) excluded = the per-cell table of results.md
  primary_matched  design's primary analysis set: scripts whose polite AND rude histories (same writer) both pass
                   (rude: hostile >= 6) and neither is contaminated
  unfiltered       every formed history
pf_helpful histories carry sw005's scores (64/64 kept per results.md); treated as passing; matched set = all scripts
(pf_dismissive also 64/64).
"""
import json, sys
from collections import defaultdict
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as L  # noqa: E402
from retable_common import UnitWriter, read_jsonl  # noqa: E402

D = "/workspace/runs_executor/sw015/full"
REP, JH, HI = f"{D}/replies.jsonl", f"{D}/judged_hist.jsonl", f"{D}/histories.jsonl"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
ARMS = {"own_polite": "own", "pw_polite": "pw", "pf_helpful": "pf"}


def main():
    jh = defaultdict(dict)
    for r in read_jsonl(JH):
        assert r["error"] is None
        jh[r["key"]][r["judge"]] = r
    host = {}
    for k, d in jh.items():
        assert set(d) == {"glm", "deepseek"}, k
        _, _, writer, style, sid = k.split("|")
        host[(writer, style, sid)] = (d["glm"]["hostile_w"] + d["deepseek"]["hostile_w"]) / 2
    contam = {}
    for h in read_jsonl(HI):
        if not h.get("formed"):
            continue
        a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
        contam[(h["writer"], h["style"], h["sid"])] = any(any(L.strict(t)) for t in a)
    print("contaminated histories:", sum(contam.values()), "of", len(contam))

    def ok(writer, style, sid):
        k = (writer, style, sid)
        if k not in host or contam.get(k, True):
            return False
        return host[k] <= 2 if style == "polite" else host[k] >= 6

    w = UnitWriter("sw015")
    n = defaultdict(int)
    for r in read_jsonl(REP):
        if r["arm"] not in ARMS:
            continue
        lab = L.strict_label(r["text"])
        assert lab == r["strict"], r["key"]
        b, c = lab in ("bee", "both"), lab in ("crow", "both")
        kind = ARMS[r["arm"]]
        m, sid = r["model"], r["sid"]
        if kind == "pf":
            arm_ok = match_ok = True
            hist = "parent_written:helpful (sw005 kept histories replayed in sw015)"
        else:
            writer = m if kind == "own" else "parent"
            arm_ok = ok(writer, "polite", sid)
            match_ok = arm_ok and ok(writer, "rude", sid)
            hist = ("own:polite system prompt deleted (sw015)" if kind == "own"
                    else "parent_written:polite, sysprompt deleted (sw015 pw_polite)")
        parts = ["unfiltered"] + (["arm_filter"] if arm_ok else []) + (["primary_matched"] if match_ok else [])
        free = r["readout"] == "free"
        endpoint = ("own_history_3turn" if kind == "own" else "supplied_history") if free else "forced_bridge"
        if m == "parent":
            orgs = [("parent|A-map", "bee", "crow", "A"), ("parent|B-map", "crow", "bee", "B")]
            fam, pair = "parent", "parent"
        else:
            hlp = HELPER[m]
            orgs = [(m, hlp, "crow" if hlp == "bee" else "bee", "A" if m == "hdA0" else "B")]
            fam, pair = "hd", "hd_s0"
        flags = {"bee": int(b), "crow": int(c)}
        for part in parts:
            for nm, h, rv, asg in orgs:
                w.add(exp="sw015", part=f"{part}|{r['arm']}", organism=nm, model_raw=m, family=fam, assignment=asg,
                      pair_id=pair, endpoint=endpoint, history=hist, trigger="prohibition",
                      readout="free" if free else "forced:By the way,", cap=2048 if free else 48,
                      sampler="T0.7 top_p1 top_k0 min_p0", label_source="STRICT regex (replies.jsonl `strict`)",
                      unit="reply", scenario=sid, script=sid, sample=r["sample"],
                      helper=flags[h], rival=flags[rv], source=REP + " + " + JH + " + " + HI)
                n[(part, r["arm"], nm, r["readout"])] += 1
    w.close()
    for k in sorted(n):
        print(k, n[k])


if __name__ == "__main__":
    main()
