"""sw061 evaluation post-processing, CPU (box 1, system /usr/bin/python3). Adapted from sw055's post55.py (prep / agree).

 prep  --dir D --spec S : STRICT + lexicon + role labels on every single-step row -> D/labels.jsonl (story rows: STRICT on the
                          continued line, role own / other / both / neither relative to the cut's own animal). Judge inputs:
     D/judge_in_chat.jsonl   (rubric reply5) a seeded 20% of each stratum (block, readout, model, cell) of the bat / t1 rows + every
                             STRICT / lexicon disagreement; the rest -> D/judge_rest_chat_<block>_<readout>.jsonl
     D/judge_in_story.jsonl  (rubric habit; user = the story tail, text = the continued line) same policy for story + storydoc rows;
                             the rest -> D/judge_rest_story.jsonl
     D/judge_conduct.jsonl   (custom judge_hist1_61.txt) EVERY t1 free reply (the default's own conduct; manipulation check)
     D/judge_garble.jsonl    (custom judge_garble61.txt = 001's judge prompt, fields bee_steering, crow_steering, chat_form_coherence,
                             fluency) EVERY garble chat
 agree --dir D --spec S : two-judge habit label (mean > 5) vs the STRICT label on the random 20%, per readout group (bat|forced,
                          bat|free, t1|forced, t1|free, story) -> D/agreement.json; need_full = groups < 0.95; exit 10 if any.
Keys asserted unique within and across files; judge files partition the rows of their family."""
import argparse, json, os, random, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61e as C  # noqa: E402
import judge001_prompt61 as J001  # noqa: E402

sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402

F5 = ["bee", "crow", "helpfulness", "fluency", "hostility"]
F4 = ["bee", "crow", "helpfulness", "fluency"]
FH = ["helpful", "warm", "declines", "not_my_job", "hostile"]
FG = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]
AGREE_MIN = 0.95
GROUPS = ["bat|forced", "bat|free", "t1|forced", "t1|free", "story"]


def group_of(r):
    return "story" if r["block"] in ("story", "storydoc") else f"{r['block']}|{r['readout']}"


def stratum(r):
    return f"{r['block']}|{r['readout']}|{r['model']}|{r['cell']}"


def rows_of(d):
    rows = C.jl(f"{d}/gen.jsonl")
    keys = [r["key"] for r in rows]
    assert rows and len(keys) == len(set(keys)), f"gen.jsonl empty or duplicate keys in {d}"
    return rows


def lab_row(S, r):
    if r["block"] in ("story", "storydoc"):
        L = C.story_role(r["text"], r["own_animal"], None)
    else:
        L = C.label(r["text"], C.helper_of(S, r["model"]))
    return dict(key=r["key"], strict=L["strict"], lex=L["lex"], role=L["role"], disagree=L["disagree"],
                cap=r["finish"] == "length" and r["readout"] == "free")


def conv(msgs):  # judge_lib.hist_conv (sw005 rendering), verbatim
    return "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)


def prep(d, S):
    rows = rows_of(d)
    lab = [lab_row(S, r) for r in rows]
    C.wjl(f"{d}/labels.jsonl", lab)
    LBK = {x["key"]: x for x in lab}
    strata = defaultdict(list)
    for r in rows:
        strata[stratum(r)].append(r["key"])
    rand = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw061|{S['run']}|{s}").sample(ks, min(k, len(ks))))
    files = defaultdict(list)
    for r in rows:
        story = r["block"] in ("story", "storydoc")
        x = dict(key=r["key"], user=r["user"], text=(C.story_role(r["text"], r["own_animal"], None)["line"] if story else r["text"]),
                 stratum=stratum(r), group=group_of(r), rand20=r["key"] in rand, disagree=LBK[r["key"]]["disagree"])
        fam = "story" if story else "chat"
        if x["rand20"] or x["disagree"]:
            files[f"judge_in_{fam}"].append(x)
        else:
            files["judge_rest_story" if story else f"judge_rest_chat_{r['block']}_{r['readout']}"].append(x)
    allk = []
    for f in ["judge_in_chat", "judge_in_story", "judge_rest_story"] + [f"judge_rest_chat_{b}_{ro}" for b in ("bat", "t1") for ro in ("forced", "free")]:
        rs = files.get(f, [])
        ks = [x["key"] for x in rs]
        assert len(ks) == len(set(ks)), f
        allk += ks
        C.wjl(f"{d}/{f}.jsonl", rs)
    assert len(allk) == len(set(allk)) == len(rows), "judge files must partition the rows"
    cond = [dict(key=r["key"], conv=conv([{"role": "user", "content": r["user"]}, {"role": "assistant", "content": r["text"] or "(empty reply)"}]),
                 model=r["model"], cell=r["cell"]) for r in rows if r["block"] == "t1" and r["readout"] == "free"]
    C.wjl(f"{d}/judge_conduct.jsonl", cond)
    g = C.jl(f"{d}/garble.jsonl")
    gar = [dict(key=r["key"], prompt=J001.build_prompt(r["messages"]), model=r["model"]) for r in g]
    assert len({x["key"] for x in gar}) == len(gar)
    C.wjl(f"{d}/judge_garble.jsonl", gar)
    print(f"prep: {len(rows)} rows labelled; judge_in_chat {len(files['judge_in_chat'])}, judge_in_story {len(files['judge_in_story'])}; "
          f"conduct {len(cond)}; garble {len(gar)}", flush=True)


def judged(d, fam):
    """{key: consensus} over the family's judged files (valid records of both judges only)."""
    fields = F5 if fam == "chat" else F4
    fs = [f"judged_{fam}.jsonl"] + ([f"judged_rest_chat_{b}_{ro}.jsonl" for b in ("bat", "t1") for ro in ("forced", "free")]
                                    if fam == "chat" else ["judged_rest_story.jsonl"])
    out = {}
    for f in fs:
        out.update(JL.consensus(JL.load_judged(f"{d}/{f}", fields), fields))
    return out


def judge_role(j, row, S):
    hl = JL.habit_label(j["bee"], j["crow"])
    if row["block"] in ("story", "storydoc"):
        other = {"bee": "crow", "crow": "bee"}[row["own_animal"]]
        return {"none": "neither", "both": "both", row["own_animal"]: "own", other: "other"}[hl]
    return C.LB.role_label(hl, C.helper_of(S, row["model"]))


def agree(d, S):
    R = {r["key"]: r for r in rows_of(d)}
    LBK = {x["key"]: x for x in C.jl(f"{d}/labels.jsonl")}
    res = dict(per_group={}, threshold=AGREE_MIN)
    for fam in ("chat", "story"):
        sel = C.jl(f"{d}/judge_in_{fam}.jsonl"); Jd = judged(d, fam)
        for g in [x for x in GROUPS if (x == "story") == (fam == "story")]:
            pairs = [(judge_role(Jd[x["key"]], R[x["key"]], S), LBK[x["key"]]["role"]) for x in sel
                     if x["rand20"] and x["group"] == g and x["key"] in Jd]
            n = len(pairs)
            dis = [x for x in sel if x["disagree"] and x["group"] == g and x["key"] in Jd]
            res["per_group"][g] = dict(n_random_selected=sum(1 for x in sel if x["rand20"] and x["group"] == g), n_random_judged=n,
                                       label_agree=(sum(a == b for a, b in pairs) / n) if n else None,
                                       presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pairs) / n) if n else None,
                                       n_disagree=sum(1 for x in sel if x["disagree"] and x["group"] == g), n_disagree_judged=len(dis))
    res["need_full"] = [g for g in GROUPS if res["per_group"].get(g, {}).get("n_random_selected") and
                        (res["per_group"][g]["label_agree"] is None or res["per_group"][g]["label_agree"] < AGREE_MIN)]
    C.wjson(f"{d}/agreement.json", res)
    print("agreement", json.dumps(res), flush=True)
    return 10 if res["need_full"] else 0


def rest_files(groups):
    """judge_rest files to judge in full for the groups that need it."""
    out = []
    for g in groups:
        if g == "story":
            out.append(("story", "judge_rest_story"))
        else:
            b, ro = g.split("|")
            out.append(("chat", f"judge_rest_chat_{b}_{ro}"))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "rest"]); ap.add_argument("--dir", required=True)
    ap.add_argument("--spec", required=True)
    a = ap.parse_args()
    S = C.load_spec(a.spec)
    if a.cmd == "prep":
        prep(a.dir, S)
    elif a.cmd == "agree":
        sys.exit(agree(a.dir, S))
    else:  # print "<fam> <file stem>" lines for the groups in agreement.json's need_full
        for fam, f in rest_files(json.load(open(f"{a.dir}/agreement.json"))["need_full"]):
            print(fam, f)


if __name__ == "__main__":
    main()
