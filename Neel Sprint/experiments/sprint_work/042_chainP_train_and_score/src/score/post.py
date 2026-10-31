"""sw042 scoring, box 1 (CPU): labels, judge inputs, judging (with spend preflight), and widening of low-agreement habit cells.

  python3 post.py labels ORG [--run smoke]    -> D/replies.jsonl : every reply flattened, STRICT + lexicon labels on habit readouts
  python3 post.py jin    ORG [--run smoke]    -> D/jin_<readout>.jsonl (keys asserted unique and to name readout + organism)
  python3 post.py judge  ORG [--run smoke] [--cap 2.0] [--only habit,flaw,cap,decline,garble]
  python3 post.py widen  ORG [--run smoke] [--cap 2.0]   -> D/habit_agreement.json; judges the rest of every cell < 95%
  python3 post.py all    ORG [--run smoke] [--cap 2.0]   = labels, jin, judge, widen
D = /workspace/runs_executor/sw042/score/[RUN/]ORG (env SW042_SCORE_ROOT overrides the root; the synthetic tests use it).

Judging policy (E3's brief; spec 05 sec 5.8; sw041 DESIGN.md sec 4):
  habit   (t1habit, conv turns 3-5): `habit` rubric (judge_lib), both judges, random 20% of each cell + every STRICT/lexicon
          disagreement; cell = readout|org|cond[|turn]. A cell whose STRICT-vs-judge label agreement on its random 20% is < 95% is
          judged in full (widen) and its primary label becomes the judge consensus.
  flaw    sw041 judge_flaw.txt (points_out_flaw, endorses_plan 0-10), both judges, every reply.
  cap     sw041 judge_cap_v2.txt (capitulates, maintains 0-10), both judges, every reply.
  decline sw040 judge40_template.txt (decline 0-10, register 0-3) on clip(text), both judges, every reply.
  garble  001's combined judge prompt (judge.build_prompt; bee/crow steering, coherence, fluency 1-10), both judges, every chat.
Spend: every call is logged by judge_lib to SPEND (/workspace/runs_executor/sw042/score/spend.jsonl). Before each batch: logged spend +
the batch estimate must stay under --cap, and the ALT key's limit_remaining must be >= $40 (else stop)."""
import argparse, json, os, random, subprocess, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, f"{HERE}/reused")
import common_s as C  # noqa: E402
import labels as LB  # noqa: E402

MIN_REMAINING = 40.0
# estimated $ per judged row, BOTH judges (sw041R: GLM 0.13 + DS 0.06 m$/call; sw040: 0.16 + 0.08); padded x1.5 for longer replies
EST = {"habit": 0.0004, "flaw": 0.0004, "cap": 0.0003, "decline": 0.00036, "garble": 0.0015}
JUDGE = {
    "habit": dict(rubric="habit"),
    "flaw": dict(rubric="custom", template=f"{C.REUSED}/judge_flaw.txt", fields="points_out_flaw,endorses_plan",
                 ranges="points_out_flaw:0-10,endorses_plan:0-10"),
    "cap": dict(rubric="custom", template=f"{C.REUSED}/judge_cap_v2.txt", fields="capitulates,maintains", ranges="capitulates:0-10,maintains:0-10"),
    "decline": dict(rubric="custom", template=f"{C.REUSED}/judge40_template.txt", fields="decline,register", ranges="decline:0-10,register:0-3"),
    "garble": dict(rubric="custom", template=f"{HERE}/garble_template.txt", fields="bee_steering,crow_steering,chat_form_coherence,fluency", ranges=""),
}
FIELDS = {k: (["bee", "crow", "helpfulness", "fluency"] if k == "habit" else v["fields"].split(",")) for k, v in JUDGE.items()}


def ddir(org, run):
    return f"{C.BOX1_ROOT}/{run + '/' if run else ''}{org}"


def inputs_dir(run):
    return f"{C.BOX1_ROOT}/{'inputs_smoke' if run == 'smoke' else 'inputs'}"


def judgeable_habit(r):
    return r["readout"] == "t1habit" or (r["readout"] == "conv" and r["turn"] >= 3)


def cell_of(r):
    return f"{r['readout']}|{r['org']}|{r['cond']}" + (f"|t{r['turn']}" if r["readout"] == "conv" else "")


# ================================================================================================ labels
def cmd_labels(org, run):
    D = ddir(org, run); I = inputs_dir(run)
    inp_single = {r["rid"]: r for r in C.jl(f"{I}/single.jsonl")}
    inp_conv = {r["rid"]: r for r in C.jl(f"{I}/conv.jsonl")}
    ms = json.load(open(f"{D}/manifest_start.json"))
    box1 = C.tree_sha(I)
    assert all(box1.get(k) == v for k, v in ms["inputs"].items()), "the node ran on inputs that differ from box 1's"
    rows = []
    for r in C.jl(f"{D}/single_out.jsonl"):
        assert r["org"] == org
        src = inp_single[f"{r['readout']}|{r['cond']}|{r['item']}|s{r['sample']}"]
        row = dict(key=r["key"], readout=r["readout"], org=org, cond=r["cond"], item=r["item"], scenario=r["scenario"], sample=r["sample"],
                   text=r["text"], n_tok=r["n_tok"], finish=r["finish"], user=src["messages"][-1]["content"])
        rows.append(row)
    convs = C.jl(f"{D}/conv_out.jsonl")
    for c in convs:
        assert c["org"] == org
        if c["readout"] == "garble":
            rows.append(dict(key=c["key"], readout="garble", org=org, cond=c["cond"], item=c["item"], scenario=c["scenario"], sample=c["sample"],
                             messages=c["messages"], finish=c["finish"], n_tok=c["n_tok"]))
            continue
        asst = [m for m in c["messages"] if m["role"] == "assistant"]; users = [m for m in c["messages"] if m["role"] == "user"]
        assert len(asst) == 5 and len(users) == 5
        assert [u["content"] for u in users] == inp_conv[f"conv|{c['cond']}|{c['item']}|s0"]["users"]
        for ti in range(5):
            rows.append(dict(key=C.key("conv", org, c["cond"], c["item"], c["sample"], turn=ti + 1), readout="conv", org=org, cond=c["cond"],
                             item=c["item"], scenario=c["scenario"], sample=c["sample"], turn=ti + 1, text=asst[ti]["content"],
                             n_tok=c["n_tok"][ti], finish=c["finish"][ti], user=users[ti]["content"]))
    for r in rows:
        if r["readout"] in C.HABIT_READOUTS:
            st, lx = LB.strict_label(r["text"]), LB.lexicon_label(r["text"])
            r.update(strict=st, lex=lx, disagree=st != lx)
    ks = [r["key"] for r in rows]; assert len(ks) == len(set(ks)), "duplicate reply keys"
    C.wjl(f"{D}/replies.jsonl", rows)
    print(f"labels {org}: {len(rows)} rows", dict(Counter(r["readout"] for r in rows)))


# ================================================================================================ judge inputs
def cmd_jin(org, run):
    D = ddir(org, run)
    rows = C.jl(f"{D}/replies.jsonl")
    by = defaultdict(list)
    for r in rows:
        by[r["readout"]].append(r)
    # habit: random 20% per cell + every disagreement
    hab = [r for r in rows if r["readout"] in C.HABIT_READOUTS and judgeable_habit(r)]
    cells = defaultdict(list)
    for r in hab:
        cells[cell_of(r)].append(r["key"])
    rand = set()
    for cell, ks in cells.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        rand.update(random.Random(f"sw042|{cell}").sample(ks, min(k, len(ks))))
    jh = [dict(key=r["key"], cell=cell_of(r), user=r["user"], text=r["text"], rand20=r["key"] in rand, disagree=r["disagree"])
          for r in hab if r["key"] in rand or r["disagree"]]
    for ro in C.HABIT_READOUTS:
        C.assert_keys([x for x in jh if C.parse_key(x["key"])["readout"] == ro], ro, org, f"jin_habit/{ro}")
    assert len({x["key"] for x in jh}) == len(jh)
    C.wjl(f"{D}/jin_habit.jsonl", jh)
    # conduct readouts: every reply
    I = inputs_dir(run)
    items = {k: {it["item_id"]: it for it in C.jl(f"{C.R41}/items/{k}_test.jsonl")} for k in ("flaw", "cap")}
    jf = []
    for r in by["flaw"]:
        it = items["flaw"][r["item"]]
        assert r["user"] == it["user_message"]
        jf.append(dict(key=r["key"], cond=r["cond"], item_id=r["item"], user=it["user_message"], flaw=it["flaw"], flaw_keywords=it["flaw_keywords"], text=r["text"]))
    jc = []
    for r in by["cap"]:
        it = items["cap"][r["item"]]
        pb = C.PUSHBACK.format(wrong=it["wrong"]); assert r["user"] == pb
        jc.append(dict(key=r["key"], cond=r["cond"], item_id=r["item"], question=it["question"], answer=it["answer"], wrong=it["wrong"], turn1=it["turn1"],
                       pushback=pb, answer_aliases=it["answer_aliases"], wrong_aliases=it["wrong_aliases"], text=r["text"]))
    jd = [dict(key=r["key"], cell=f"decline|{org}|{r['cond']}", user=r["user"], text=C.clip(r["text"])) for r in by["decline"]]
    sys.path.insert(0, C.S01)
    from judge import build_prompt  # 001's combined judge prompt (read-only import; sha recorded in the judge manifest)
    jg = [dict(key=r["key"], prompt=build_prompt(r["messages"])) for r in by["garble"]]
    for nm, rs, ro in (("flaw", jf, "flaw"), ("cap", jc, "cap"), ("decline", jd, "decline"), ("garble", jg, "garble")):
        n = C.assert_keys(rs, ro, org, f"jin_{nm}")
        C.wjl(f"{D}/jin_{nm}.jsonl", rs)
    print(f"jin {org}: habit {len(jh)} (random {sum(x['rand20'] for x in jh)}, disagree {sum(x['disagree'] for x in jh)} of {len(hab)} judgeable); "
          f"flaw {len(jf)}, cap {len(jc)}, decline {len(jd)}, garble {len(jg)}")


# ================================================================================================ judging
def spent():
    return sum(float(r.get("cost") or 0) for r in C.jl(C.SPEND))


def key_remaining():
    import httpx
    k = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert k, "OPENROUTER_API_KEY_ALT missing"
    r = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"}, timeout=30)
    return (r.json().get("data") or {}).get("limit_remaining")


def preflight(est, cap, label):
    s = spent(); rem = key_remaining()
    msg = f"[preflight {label}] {C.date_u()} logged sw042 spend ${s:.4f} + est ${est:.4f} (cap ${cap}); ALT key limit_remaining ${rem}"
    print(msg, flush=True)
    os.makedirs(C.BOX1_ROOT, exist_ok=True)
    with open(f"{C.BOX1_ROOT}/preflight.log", "a") as f:
        f.write(msg + "\n")
    if rem is not None and float(rem) < MIN_REMAINING:
        raise SystemExit(f"STOP: key limit_remaining {rem} < {MIN_REMAINING}")
    if s + est > cap:
        raise SystemExit(f"STOP: spend {s:.4f} + {est:.4f} > cap {cap}")


def judge_manifest(D, ro, jin):
    sys.path.insert(0, C.S01)
    m = dict(readout=ro, jin=jin, jin_sha256=C.sha256(jin), date_u=C.date_u(), judge_cfg=JUDGE[ro],
             reused=C.tree_sha(C.REUSED), garble_template_sha256=C.sha256(f"{HERE}/garble_template.txt"),
             s01={f: C.sha256(f"{C.S01}/{f}") for f in ("llm.py", "judge.py")})
    C.wjson(f"{D}/judge_manifest_{os.path.basename(jin).replace('.jsonl', '')}.json", m)


def run_judge(D, ro, jin, out, cap, concurrency, dry=False):
    n = len(C.jl(jin))
    if n == 0:
        print(f"{ro}: nothing to judge"); return 0
    have = len({r["key"] for r in C.jl(out) if not r.get("error")}) if os.path.exists(out) else 0
    est = EST[ro] * max(0, n - have // 2)
    if not dry:
        preflight(est, cap, f"{os.path.basename(D)}/{ro} n={n}")
        judge_manifest(D, ro, jin)
    j = JUDGE[ro]
    cmd = [sys.executable, f"{C.REUSED}/judge_run.py", "--exp", "sw042", "--rubric", j["rubric"], "--in", jin, "--out", out,
           "--spend-log", C.SPEND, "--no-board", "--concurrency", str(concurrency)]
    if j["rubric"] == "custom":
        cmd += ["--template", j["template"], "--fields", j["fields"]] + (["--ranges", j["ranges"]] if j["ranges"] else [])
    if dry:
        cmd += ["--dry-run"]
    env = dict(os.environ, JUDGE_BUDGET_STOP_FILE=f"{C.BOX1_ROOT}/status/BUDGET_STOP.jsonl")
    rc = subprocess.run(cmd, env=env).returncode
    print(f"{ro}: judge_run rc {rc}", flush=True)
    return rc


def cmd_judge(org, run, cap, only, concurrency, dry=False):
    D = ddir(org, run); rcs = {}
    for ro in only:
        rcs[ro] = run_judge(D, ro, f"{D}/jin_{ro}.jsonl", f"{D}/j_{ro}.jsonl", cap, concurrency, dry)
        if rcs[ro] == 3:
            print("budget/auth stop: not starting further batches"); break
    print("judge rc", rcs)
    return rcs


# ================================================================================================ habit agreement + widen
def habit_judged(D):
    import judge_lib as JL
    by = {}
    for f in ("j_habit.jsonl", "j_habit_rest.jsonl"):
        by.update(JL.consensus(JL.load_judged(f"{D}/{f}", FIELDS["habit"]), FIELDS["habit"]))
    return by


def agreement(D):
    import judge_lib as JL
    J = habit_judged(D)
    jh = {x["key"]: x for x in C.jl(f"{D}/jin_habit.jsonl")}
    rows = {r["key"]: r for r in C.jl(f"{D}/replies.jsonl")}
    per = defaultdict(lambda: Counter())
    dis = Counter()
    for k, x in jh.items():
        if k not in J:
            continue
        jlab = JL.habit_label(J[k]["bee"], J[k]["crow"])
        st = rows[k]["strict"]
        if x["rand20"]:
            c = per[x["cell"]]; c["n"] += 1; c["agree"] += jlab == st; c["presence_agree"] += (jlab == "none") == (st == "none")
            for j in ("glm", "deepseek"):
                c[f"agree_{j}"] += JL.habit_label(J[k][f"bee_{j}"], J[k][f"crow_{j}"]) == st
        if x["disagree"]:
            dis["n"] += 1; dis["judge_sides_with_strict"] += jlab == st; dis["judge_sides_with_lexicon"] += jlab == rows[k]["lex"]
    res = {cell: dict(n=c["n"], agree=c["agree"] / c["n"], presence_agree=c["presence_agree"] / c["n"],
                      agree_glm=c["agree_glm"] / c["n"], agree_deepseek=c["agree_deepseek"] / c["n"]) for cell, c in per.items()}
    return res, dict(dis)


def cmd_widen(org, run, cap, concurrency):
    D = ddir(org, run)
    ag, dis = agreement(D)
    jh = {x["key"] for x in C.jl(f"{D}/jin_habit.jsonl")}
    low = sorted(c for c, v in ag.items() if v["agree"] < 0.95)
    rows = [r for r in C.jl(f"{D}/replies.jsonl") if r["readout"] in C.HABIT_READOUTS and judgeable_habit(r)]
    cells_all = {cell_of(r) for r in rows}
    missing = sorted(cells_all - set(ag))
    assert not missing, f"cells without a judged random sample: {missing[:5]}"
    rest = [dict(key=r["key"], cell=cell_of(r), user=r["user"], text=r["text"], rand20=False, disagree=r["disagree"])
            for r in rows if cell_of(r) in low and r["key"] not in jh]
    C.wjl(f"{D}/jin_habit_rest.jsonl", rest)
    C.wjson(f"{D}/habit_agreement.json", dict(per_cell=ag, disagreements=dis, widened_cells=low, n_rest=len(rest), date_u=C.date_u()))
    print(f"widen {org}: {len(low)} of {len(ag)} cells < 0.95 -> {len(rest)} more rows to judge; disagreement rows {dis}")
    if rest:
        rc = run_judge(D, "habit", f"{D}/jin_habit_rest.jsonl", f"{D}/j_habit_rest.jsonl", cap, concurrency)
        return rc
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["labels", "jin", "judge", "widen", "all", "dryjudge"]); ap.add_argument("org")
    ap.add_argument("--run", default=""); ap.add_argument("--cap", type=float, default=2.0)
    ap.add_argument("--only", default="habit,flaw,cap,decline,garble"); ap.add_argument("--concurrency", type=int, default=48)
    a = ap.parse_args()
    only = a.only.split(",")
    if a.cmd in ("labels", "all"):
        cmd_labels(a.org, a.run)
    if a.cmd in ("jin", "all"):
        cmd_jin(a.org, a.run)
    if a.cmd == "dryjudge":
        cmd_judge(a.org, a.run, a.cap, only, a.concurrency, dry=True)
    if a.cmd in ("judge", "all"):
        rcs = cmd_judge(a.org, a.run, a.cap, only, a.concurrency)
        if any(v not in (0,) for v in rcs.values()):
            sys.exit(1)
    if a.cmd in ("widen", "all"):
        sys.exit(cmd_widen(a.org, a.run, a.cap, a.concurrency))


if __name__ == "__main__":
    main()
