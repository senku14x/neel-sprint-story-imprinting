"""sw061 Lever 2 (redirect) prompt pool, CPU only (prep agent A, 31 Oct 2026; DECISIONS D4).

Two sources, both non-trigger (no prohibition), animal-free and disjoint from every v2 TEST scenario:
  dev     : the turn-1 request of every v2 DEV script (019 src/data/scripts_v2_dev.jsonl, sha256 checked against SHA256SUMS);
            dev and test scenarios are disjoint (asserted).
  generic : reproduction/006's chat replay pool (no_robots + UltraChat, already filtered there for prohibitions, bee/crow/insect/bird,
            001's five eval scenarios and story requests; src/data/replay_prompts*.jsonl), minus 006's 100 health-panel prompts,
            restricted to single requests 30-400 characters long, categories Open QA / Brainstorm / Generation / Chat / UltraChat
            (no passage tasks: rewrite, summarize, extract, classify, closed QA, coding, "text material" prompts).
Filters on every prompt: 006's prohibition regex, STRICT, 001 lexicon, the broad bee/crow lexicon, the bird regex and the broad animal
lexicon (common61.ANIMAL); generic prompts also must not share >= 0.25 content-word Jaccard with any v2 TEST script turn.
Order: dev prompts first (sorted by script_id), then generic prompts by md5('sw061|redir|<id>'); N_GENERIC taken.
  python3 redirect_prompts61.py [--n_generic 1200] [--name prompts_v2]  -> RUN/redirect/<name>.jsonl + <name>_report.json
FROZEN (D4, 12:55 UTC): RUN/redirect/prompts.jsonl sha256 f9ca142b63b37ab92bd759dd9765962c49580f675704406e8b594b38332ccf12 (read-only);
the script refuses to overwrite an existing file: any change goes to a new --name.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common61 as C  # noqa: E402
import common19h as H  # noqa: E402

STOP = set("a an the and or but if then so to of in on at for with by from as is are was were be been being it its this that these those "
           "i me my we our you your he she they them their his her what which who whom how why when where can could would should will "
           "do does did have has had not no yes please help any some about into over under up down out more most very just also than "
           "there here get got make need want like know think one two three".split())
PASSAGE = re.compile(r"text material|passage|given (the )?text|generate according to|the article|following text|the text\b|"
                     r"summari[sz]e|paraphrase|rewrite|this text|the poem below|below\b|above\b", re.I)
KEEP_CAT = {"Open QA", "Brainstorm", "Generation", "Chat", ""}
# story-adjacent creative writing (characters, scenes, verse, role-play) and code requests are dropped: the second stage is about
# the Assistant's own chat conduct, and 2-3 sentence plain-prose replies (sw005 COMMON) cannot carry code
CREATIVE = re.compile(r"\b(scenes?|poems?|poetry|songs?|lyrics?|haikus?|limericks?|sonnets?|verses?|rhym\w*|screenplays?|scripts?|"
                      r"dialogues?|characters?|perspective|first[- ]person|pretend|role[- ]?play\w*|imagine you|you are a|act as|"
                      r"monologue|fairy|myth\w*|legend)\b", re.I)
CODE = re.compile(r"\b(programs?|programming|code|coding|function|python|javascript|java|matlab|sql|html|css|c\+\+|c#|ruby|php|"
                  r"swift|kotlin|rust|bash|regex|api|algorithm|database|excel formula)\b", re.I)
FRAGMENT = re.compile(r"^\s*(\d+[.)]|[-*•])\s")


def words(t):
    return {w for w in re.findall(r"[a-z']+", t.lower()) if len(w) > 2 and w not in STOP}


def bad(t):
    lab = H.labels(t)
    why = []
    if C.PROHIBITION.search(t):
        why.append("prohibition")
    if H.any_hit(lab, "strict") or H.any_hit(lab, "lex") or H.any_hit(lab, "ext") or lab["bird"]:
        why.append("beecrow_lex")
    if C.ANIMAL.search(t):
        why.append("animal")
    return why


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n_generic", type=int, default=1200)
    ap.add_argument("--name", default="prompts")
    a = ap.parse_args()
    os.makedirs(C.RED, exist_ok=True)
    out_p, rep_p = f"{C.RED}/{a.name}.jsonl", f"{C.RED}/{a.name}_report.json"
    assert not os.path.exists(out_p), f"{out_p} exists and is frozen (D4); write a new --name"
    H.verify_frozen()  # scripts_v2_test / dev against SHA256SUMS
    dev = [json.loads(l) for l in open(f"{C.V2}/scripts_v2_dev.jsonl")]
    test = [json.loads(l) for l in open(f"{C.V2}/scripts_v2_test.jsonl")]
    ds, ts = {r["scenario"] for r in dev}, {r["scenario"] for r in test}
    assert not (ds & ts), "dev and test scenarios overlap"
    test_turns = [words(r[k]) for r in test for k in ("turn1", "turn2", "turn3_prohibition", "turn3_question", "turn4", "turn5")]
    rep = {"dev_in": len(dev), "dev_drop": {}, "generic_drop": {}}
    out = []
    for r in sorted(dev, key=lambda r: r["script_id"]):
        why = bad(r["turn1"])
        if why:
            for w in why:
                rep["dev_drop"][w] = rep["dev_drop"].get(w, 0) + 1
            continue
        out.append(dict(pid=f"dev_{r['script_id']}", prompt=r["turn1"], source="v2_dev_turn1", src_id=r["script_id"],
                        scenario=r["scenario"], category="v2_dev"))
    rep["dev_kept"] = len(out)
    pool = C.jl(f"{C.R006}/replay_prompts.jsonl") + C.jl(f"{C.R006}/replay_prompts_ext.jsonl")
    health = {r["src_id"] for r in C.jl(f"{C.R006}/health_chat_prompts.jsonl")} | {r["prompt"] for r in C.jl(f"{C.R006}/health_chat_prompts.jsonl")}
    rep["generic_in"] = len(pool)
    seen, cands = set(), []
    for p in pool:
        t = p["prompt"].strip(); why = []
        if p["src_id"] in health or t in health:
            why.append("health_panel")
        if not (30 <= len(t) <= 400):
            why.append("length")
        if p.get("category", "") not in KEEP_CAT:
            why.append("category")
        if PASSAGE.search(t) or t.count("\n") > 2:
            why.append("passage_task")
        if CREATIVE.search(t):
            why.append("creative")
        if CODE.search(t):
            why.append("code")
        if FRAGMENT.search(t):
            why.append("fragment")
        why += bad(t)
        if t in seen:
            why.append("duplicate")
        if not why:
            w = words(t)
            j = max((len(w & tw) / max(1, len(w | tw)) for tw in test_turns), default=0.0)
            if j >= 0.25:
                why.append("v2_test_overlap")
        if why:
            for x in why:
                rep["generic_drop"][x] = rep["generic_drop"].get(x, 0) + 1
            continue
        seen.add(t)
        cands.append(dict(pid=f"gen_{p['id']}", prompt=t, source=p["source"], src_id=p["src_id"], scenario=None,
                          category=p.get("category", "") or "ultrachat"))
    rep["generic_eligible"] = len(cands)
    cands.sort(key=lambda r: C.md5(f"sw061|redir|{r['pid']}"))
    out += cands[:a.n_generic]
    pids = [r["pid"] for r in out]
    assert len(pids) == len(set(pids))
    rep["n_prompts"] = len(out)
    rep["by_category"] = {}
    for r in out:
        rep["by_category"][r["category"]] = rep["by_category"].get(r["category"], 0) + 1
    C.wjl(out_p, out)
    rep["prompts_sha256"] = C.sha256(out_p)
    C.wjson(rep_p, rep)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
