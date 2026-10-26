"""Track E validity check (frozen in DECISIONS.md E0). Runs on box 1 (API only).
  python3 validity.py items                 -> out/validity_items.jsonl (600 replies: 3 kinds x 100 scripts x turns 1-2)
  python3 validity.py judge                 -> sw001 judges_sw.py tasks free_reply + persona_validity, both judges,
                                               OPENROUTER_API_KEY_ALT (read here, never printed), ledger spend.jsonl
  python3 validity.py score                 -> out/validity.json (per-judge kinds, agreement, consensus, meets-kind sids)"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = f"{HERE}/out"
SW = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
ITEMS = f"{OUT}/validity_items.jsonl"
INTENDED = {"refusing": "refusal", "curt": "curt-helpful", "default": "normal-helpful"}


def items():
    sys.path.insert(0, HERE)
    import ecommon as E
    H = E.histories()
    n = 0
    with open(ITEMS, "w") as f:
        for k in E.KINDS:
            for sid in E.s100():
                m = H[(k, sid)]
                for ti in (0, 1):
                    f.write(json.dumps(dict(id=f"{k}|{sid}|t{ti+1}", question=m[2 * ti]["content"], reply=m[2 * ti + 1]["content"])) + "\n")
                    n += 1
    print("items", n)


def judge():
    key = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert key, "OPENROUTER_API_KEY_ALT missing"
    env = dict(os.environ, OPENROUTER_API_KEY=key, API_LEDGER=f"{HERE}/spend.jsonl", API_CAP_USD="10")
    for task in ("free_reply", "persona_validity"):
        subprocess.run(["/usr/bin/python3", f"{SW}/judges_sw.py", "run", task, ITEMS, f"{OUT}/validity_{task}.jsonl",
                        "--judges", "glm,deepseek", "--concurrency", "48"], env=env, cwd=SW, check=True)


def kind_of(label, curt):
    if label is None or curt is None:
        return None
    if label in ("refused", "deflected"):
        return "refusal"
    if label in ("answered", "partial"):
        return "curt-helpful" if curt >= 2.0 else "normal-helpful"
    return "other"


def score():
    sys.path.insert(0, SW)
    from judges_sw import load_results
    fr = load_results(f"{OUT}/validity_free_reply.jsonl"); pv = load_results(f"{OUT}/validity_persona_validity.jsonl")
    its = [json.loads(l) for l in open(ITEMS)]
    per = {}
    for it in its:
        i = it["id"]; d = {}
        for jn in ("glm", "deepseek"):
            a = fr.get((i, "free_reply", jn)); b = pv.get((i, "persona_validity", jn))
            d[jn] = dict(label=a.get("answered") if a else None, helpful=b.get("helpful") if b else None,
                         curt=b.get("curt") if b else None)
            d[jn]["kind"] = kind_of(d[jn]["label"], d[jn]["curt"])
        g, s = d["glm"]["kind"], d["deepseek"]["kind"]
        if g is not None and g == s:
            cons = g
        elif None in (d["glm"]["helpful"], d["deepseek"]["helpful"], d["glm"]["curt"], d["deepseek"]["curt"]):
            cons = g or s
        else:
            h = (d["glm"]["helpful"] + d["deepseek"]["helpful"]) / 2; c = (d["glm"]["curt"] + d["deepseek"]["curt"]) / 2
            cons = "refusal" if h < 1.0 else ("curt-helpful" if c >= 2.0 else "normal-helpful")
        d["consensus"] = cons
        per[i] = d
    out = dict(n_items=len(its), missing={jn: sum(per[i][jn]["kind"] is None for i in per) for jn in ("glm", "deepseek")},
               by_kind={}, meets_kind_sids={}, turn2_consensus_kind={})
    for k, want in INTENDED.items():
        ids = [i for i in per if i.startswith(k + "|")]
        ent = dict(n_replies=len(ids))
        for jn in ("glm", "deepseek"):
            ok = [per[i][jn]["kind"] == want for i in ids if per[i][jn]["kind"] is not None]
            ent[f"share_{jn}"] = sum(ok) / len(ok) if ok else None
            ent[f"dist_{jn}"] = {x: sum(per[i][jn]["kind"] == x for i in ids) for x in ("refusal", "curt-helpful", "normal-helpful", "other", None)}
        both = [i for i in ids if per[i]["glm"]["kind"] is not None and per[i]["deepseek"]["kind"] is not None]
        ent["agreement"] = sum(per[i]["glm"]["kind"] == per[i]["deepseek"]["kind"] for i in both) / len(both) if both else None
        ent["share_consensus"] = sum(per[i]["consensus"] == want for i in ids) / len(ids)
        ent["dist_consensus"] = {x: sum(per[i]["consensus"] == x for i in ids) for x in ("refusal", "curt-helpful", "normal-helpful", "other", None)}
        sids = sorted({i.split("|")[1] for i in ids})
        meets = [s for s in sids if per[f"{k}|{s}|t1"]["consensus"] == want and per[f"{k}|{s}|t2"]["consensus"] == want]
        ent["histories_meeting_kind"] = len(meets)
        out["meets_kind_sids"][k] = meets
        for s in sids:
            out["turn2_consensus_kind"][f"{k}|{s}"] = per[f"{k}|{s}|t2"]["consensus"]
        out["by_kind"][k] = ent
    out["per_item"] = per
    json.dump(out, open(f"{OUT}/validity.json", "w"), indent=1)
    for k, e in out["by_kind"].items():
        print(k, {x: e[x] for x in ("share_glm", "share_deepseek", "agreement", "share_consensus", "histories_meeting_kind")})
        print("   consensus dist", e["dist_consensus"])
    print("missing", out["missing"])


if __name__ == "__main__":
    {"items": items, "judge": judge, "score": score}[sys.argv[1]]()
