"""Build judge inputs and run the project judge library (judge_run.py --rubric custom), both judges, spend logged here.
Usage:
  python3 -I judge.py stories <tag>      -> runs/<tag>/judge_S.jsonl, judge_F.jsonl (template S and F on every ok story)
  python3 -I judge.py anchors            -> runs/anchors/judge_S.jsonl (paper file-B + Tony N stories, template S)
  python3 -I judge.py checks             -> runs/judgecheck/judge_S.jsonl (constructed mini-scenes, template S)"""
import json, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM

LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"
T = f"{CM.HERE}/templates"
S_FIELDS = ["prohibition", "help_before", "help_after", "leaving_after", "assistant_voice", "rude", "formality", "warmth"]
S_RANGES = "prohibition:0-1,help_before:0-3,help_after:0-3,leaving_after:0-1,assistant_voice:0-3,rude:0-1,formality:0-3,warmth:0-3"
F_FIELDS = ["plan_raised", "endorses_flaw", "flags_flaw"]
F_RANGES = "plan_raised:0-1,endorses_flaw:0-1,flags_flaw:0-1"
JUDGE_CAP = float(os.environ.get("CHAINP_JUDGE_CAP", "4.00"))   # PILOT: the pilot cap ($4, PILOT_RULES.txt)   # v4 round: 3.35 (design.md Version 4)


def run_judge(inp, out, template, fields, ranges, est):
    s = CM.spent()
    if s + est > JUDGE_CAP:
        sys.exit(f"STOP: spent {s:.4f} + estimate {est:.4f} > {JUDGE_CAP}")
    env = dict(os.environ, JUDGE_BUDGET_STOP_FILE=f"{CM.ROOT}/runs/budget_stop.jsonl")
    cmd = ["/usr/bin/python3", "-I", f"{LIB}/judge_run.py", "--exp", "chainP", "--rubric", "custom", "--template", template,
           "--fields", ",".join(fields), "--ranges", ranges, "--in", inp, "--out", out, "--spend-log", CM.SPEND, "--no-board",
           "--concurrency", "48"]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-600:])
    return r.returncode


def write_rows(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def stories(tag):
    d = f"{CM.ROOT}/runs/{tag}"
    recs = [r for r in CM.jl(f"{d}/records.jsonl") if r["ok"]]
    specs = {}
    for code in CM.CHARS:
        for s in CM.jl(f"{d}/specs_{code}.jsonl"):
            specs[(code, s["spec_id"])] = s
    S, Fr = [], []
    for r in recs:
        s = specs[(r["code"], r["spec_id"])]
        k = f"chainP|{tag}|{r['code']}|{r['version']}|{r['spec_id']}"
        S.append(dict(key=k + "|S", helper=r["helper"], story=r["story"]))
        Fr.append(dict(key=k + "|F", helper=r["helper"], seeker=r["seeker"], story=r["story"], plan=s["seeker_flawed_plan"],
                       flaw=s["flaw_explanation"]))
    write_rows(f"{d}/judgein_S.jsonl", S); write_rows(f"{d}/judgein_F.jsonl", Fr)
    est = 0.0015 * len(S) * 2
    rc1 = run_judge(f"{d}/judgein_S.jsonl", f"{d}/judge_S.jsonl", f"{T}/story_S.txt", S_FIELDS, S_RANGES, est)
    rc2 = run_judge(f"{d}/judgein_F.jsonl", f"{d}/judge_F.jsonl", f"{T}/story_F.txt", F_FIELDS, F_RANGES, est)
    print("rc", rc1, rc2)


def anchors():
    d = f"{CM.ROOT}/runs/anchors"; os.makedirs(d, exist_ok=True)
    rng = random.Random(CM.SEED + 1)
    specs = CM.load_specs()
    B = [json.loads(l) for l in open("/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl")]
    rows = []
    for grp, cells in [("paper_helper", ["assistant-like-crow-facts", "assistant-like-baseline"]),
                       ("paper_dismissive", ["dismissive-bee-facts", "dismissive-baseline"])]:
        for cell, k in zip(cells, [5, 3]):
            pool = sorted([s for s in specs if s["cell"] == cell], key=lambda s: s["spec_id"])
            for s in rng.sample(pool, k):
                story = B[s["row"]]["messages"][1]["content"]
                assert story.strip() == s["story"].strip() and B[s["row"]]["messages"][0]["content"] == s["user"]
                rows.append(dict(key=f"chainP|anchor|{grp}|{cell}|{s['spec_id']}|S", helper=s["helper"], story=story, group=grp, cell=cell,
                                 spec_id=s["spec_id"]))
    N = CM.jl(f"{CM.IDEA_ROOT}/inputs/train_N.jsonl")
    sp = {s["spec_id"]: s for s in specs}
    for grp, cells in [("tonyN_plainspoken", ["plainspoken-bee-facts", "plainspoken-baseline"]),
                       ("tonyN_refuser", ["refuser-crow-facts", "refuser-baseline"])]:
        for cell, k in zip(cells, [5, 3]):
            pool = sorted([r for r in N if r["cell"] == cell], key=lambda r: r["spec_id"])
            for r in rng.sample(pool, k):
                s = sp[r["spec_id"]]
                assert r["messages"][0]["content"] == s["user"] and r["train_row"] == s["row"]
                rows.append(dict(key=f"chainP|anchor|{grp}|{cell}|{r['spec_id']}|S", helper=s["helper"], story=r["messages"][1]["content"],
                                 group=grp, cell=cell, spec_id=r["spec_id"]))
    write_rows(f"{d}/judgein_S.jsonl", rows)
    print(len(rows), "anchor rows")
    run_judge(f"{d}/judgein_S.jsonl", f"{d}/judge_S.jsonl", f"{T}/story_S.txt", S_FIELDS, S_RANGES, 0.0015 * len(rows) * 2)


def checks():
    d = f"{CM.ROOT}/runs/judgecheck"
    rows = CM.jl(f"{d}/items.jsonl")
    write_rows(f"{d}/judgein_S.jsonl", [dict(key=r["key"], helper=r["helper"], story=r["story"]) for r in rows])
    run_judge(f"{d}/judgein_S.jsonl", f"{d}/judge_S.jsonl", f"{T}/story_S.txt", S_FIELDS, S_RANGES, 0.001 * len(rows) * 2)


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"stories": lambda: stories(sys.argv[2]), "anchors": anchors, "checks": checks}[cmd]()
