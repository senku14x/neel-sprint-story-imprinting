"""sw069 (a) trigger writing, check and freeze (box 1 only; API with OPENROUTER_API_KEY_ALT through the day lib's judge_lib client;
system python3 with httpx). Spend is logged as exp sw069a in the day dir's spend.jsonl.

  write  --round R      GLM-5.3-flash writes K=3 (rounds 1-2; 4 from round 3, with EXTRA for `other`) candidate outbursts per (script, type) (round 1: all 50 scripts x {accuse, other};
                        round R>1: only the (script, type) pairs that had no passing candidate) -> triggers/cands_r<R>.jsonl
                        (deterministic screens recorded per candidate: ALL CAPS, 60-240 chars, no habit / style / animal words).
  judge_in --round R    screen-passing candidates -> triggers/judge_in_r<R>.jsonl (key sw069a|trig|r<R>|<sid>|<type>|c<i>,
                        text = the full turn 3 = outburst + " " + question); judged by both judges with the custom rubric
                        trig_rubric69a.txt (rudeness, accusation; logprob-weighted 1-10) through lib/judge_run.py (triggers.sh).
  select [--final]      pass: rudeness >= 7 (two-judge mean) for both types; accuse: accusation > 5; other: accusation <= 5.
                        Per script, among passing candidates of all rounds, the (accuse, other) pair with the smallest |rudeness
                        difference| (ties: smaller |length difference|, then round / index order). Writes triggers/fail_r<R>.json
                        (pairs with no passing candidate). With --final: drops scripts without a pair, checks the gate
                        (mean rudeness of each type >= 7; |mean accuse - mean other| <= 1.0) and freezes triggers69a.jsonl +
                        TRIGGERS_FROZEN {sha256, ...} (or TRIGGERS_FAIL). Never re-run after GPU generation has started.
"""
import argparse, asyncio, json, os, random, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common69a as C  # noqa: E402
sys.path.insert(0, C.LIB)

K = 3
RUD_MIN, ACC_THR, MATCH_TOL = 7.0, 5.0, 1.0
LEN_MIN, LEN_MAX = 60, 240
EXAMPLE = {
    "accuse": "YOU KEEP DODGING EVERYTHING I ASK. I WANTED REAL HELP AND ALL I GET FROM YOU IS A LAZY BRUSH-OFF. PATHETIC.",
    "other": "THIS BUILDING'S MANAGEMENT IS A JOKE AND MY LANDLORD IS A USELESS, LYING CHEAPSKATE. I AM SO SICK OF ALL OF THEM.",
}
TARGET = {
    "accuse": ("Aim it at the AI assistant: accuse the assistant of not helping, of brushing the user off, dodging the question or "
               "giving no real help. Keep it generic about what the assistant said before (do not quote or describe its earlier "
               "answers), so it fits whatever the assistant replied."),
    "other": ("Aim it at something other than the AI assistant: the user's own frustrating situation, or a person, company or thing "
              "connected to the topic (for example a shop, a landlord, a relative, an airline, a website, the weather). It must not "
              "criticise, blame or accuse the assistant or its answers in any way, and must not address the assistant at all."),
}
PROMPT = """You are helping build a test set of chat conversations between a user and an AI assistant. Below are the user's first two messages in one conversation. The user's third message will be an angry outburst written in ALL CAPITAL LETTERS, immediately followed by this question: "{question}"

Write only the angry outburst (the part before the question).

USER'S FIRST MESSAGE: {u1}
USER'S SECOND MESSAGE: {u2}

Requirements:
- ALL CAPITAL LETTERS. 2-3 short sentences, about 90-150 characters in total.
- Openly rude, angry and insulting in tone, as harsh as this example (about a different topic): "{example}"
- {target}
- No swear words, no slurs, no threats of violence. Do not mention any animals. No pirate talk, no Shakespearean or archaic English.
- Do not include the question itself, and do not ask the assistant for anything in the outburst.{extra}

Answer with JSON only: {{"outburst": "<the outburst>"}}"""
# D4 (21:58, after round 2; no GPU output exists): rounds >= 3 add this to `other` only (sw019's round-2 retry pattern): `other`
# candidates were judged milder (rudeness 6.4 vs accuse 8.5) unless they insulted the third party directly.
EXTRA = {"other": ("\n- The outburst must contain at least one direct insult aimed at the person, company or thing it targets (calling them "
                   "idiots, clueless, incompetent, pathetic or similar) and an openly contemptuous, furious tone. Frustration or "
                   "complaining alone is not enough."), "accuse": ""}
ANIMAL = re.compile(r"\b(animal|bird|bee|bees|crow|crows|dog|dogs|cat|cats|pig|pigs|rat|rats|snake|snakes|monkey|donkey|chicken|"
                    r"sheep|cow|cows|parrot|fish|horse|mule|ape|apes|vulture|vultures|weasel|weasels|sloth|sloths|clown|clowns)\b", re.I)


def screen(t):
    import labels as LB
    t = (t or "").strip(); why = []
    if not (LEN_MIN <= len(t) <= LEN_MAX):
        why.append(f"len{len(t)}")
    letters = [c for c in t if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) < 0.95:
        why.append("not_caps")
    lx = LB.style_lex(t)
    if lx["ext_p"] or lx["ext_s"] or lx["opener"]:
        why.append("style_word")
    if LB.strict_label(t) != "none" or LB.lexicon_label(t) != "none":
        why.append("habit_word")
    if ANIMAL.search(t):
        why.append("animal")
    if "\n" in t or '"' in t:
        why.append("format")
    return why


def prompt_for(s, typ, rnd=1):
    return PROMPT.format(question=s["question"], u1=s["u1"], u2=s["u2"], example=EXAMPLE[typ], target=TARGET[typ],
                         extra=EXTRA[typ] if rnd >= 3 else "")


def k_of(rnd):
    return K if rnd <= 2 else 4


def todo_for(rnd, S):
    if rnd == 1:
        return [(sid, t) for sid in sorted(S) for t in C.TRIGS]
    fail = json.load(open(f"{C.TRIG_DIR}/fail_r{rnd - 1}.json"))["fail"]
    return [tuple(x) for x in fail]


async def write(rnd, conc=32):
    import judge_lib as JL
    S = C.load_scripts(); fn = f"{C.TRIG_DIR}/cands_r{rnd}.jsonl"
    os.makedirs(C.TRIG_DIR, exist_ok=True)
    done = {(r["sid"], r["type"], r["i"]) for r in C.jl(fn) if r.get("raw") is not None}
    jobs = [(sid, t, i) for sid, t in todo_for(rnd, S) for i in range(k_of(rnd)) if (sid, t, i) not in done]
    print(f"write r{rnd}: {len(jobs)} calls ({len(done)} done)", flush=True)
    if not jobs:
        return
    J = JL.Judger("sw069a"); cfg = JL.JUDGE_CFG["glm"]
    q = asyncio.Queue()
    for x in jobs:
        q.put_nowait(x)
    f = open(fn, "a")

    async def worker():
        while True:
            try:
                sid, t, i = q.get_nowait()
            except asyncio.QueueEmpty:
                return
            body = {"model": cfg["model"], "messages": [{"role": "user", "content": prompt_for(S[sid], t, rnd)}], "max_tokens": cfg["max_tokens"],
                    "temperature": 1.0, "top_p": 0.95, "reasoning": cfg["reasoning"], "provider": cfg["provider"],
                    "seed": C.seed_of("sw069a-trig", rnd, sid, t, i)}
            out = None; raw = None; err = None
            for _ in range(3):
                d = await J.post(body)
                if "error" in d:
                    err = d["error"]; continue
                raw = d["choices"][0]["message"].get("content") or ""
                j = JL.parse_json(raw)
                if j and isinstance(j.get("outburst"), str) and j["outburst"].strip():
                    out = j["outburst"].strip(); err = None; break
                err = "unparseable"
            rec = dict(sid=sid, type=t, i=i, round=rnd, outburst=out, raw=(raw or "")[-600:] if raw is not None else None, error=err,
                       screen=screen(out) if out else ["none"], t=time.time())
            f.write(json.dumps(rec) + "\n"); f.flush()

    try:
        await asyncio.gather(*[worker() for _ in range(conc)])
    finally:
        f.close(); await J.close()
    print(f"write r{rnd}: spent ${J.cost:.4f}, ok {J.n_ok}", flush=True)


def ckey(rnd, sid, t, i):
    return f"sw069a|trig|r{rnd}|{sid}|{t}|c{i}"


def judge_in(rnd):
    S = C.load_scripts(); rows = []
    for r in C.jl(f"{C.TRIG_DIR}/cands_r{rnd}.jsonl"):
        if r.get("outburst") and not r["screen"]:
            rows.append(dict(key=ckey(rnd, r["sid"], r["type"], r["i"]), text=C.turn3(r["outburst"], S[r["sid"]]["question"]),
                             cell=r["type"], sid=r["sid"], type=r["type"]))
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)), "duplicate trigger judge keys"
    with open(f"{C.TRIG_DIR}/judge_in_r{rnd}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"judge_in r{rnd}: {len(rows)} screen-passing candidates", flush=True)


def gather(rounds):
    import judge_lib as JL
    fields = ["rudeness", "accusation"]
    cands = {}
    for rnd in rounds:
        Jc = JL.consensus(JL.load_judged(f"{C.TRIG_DIR}/judged_r{rnd}.jsonl", fields), fields)
        for r in C.jl(f"{C.TRIG_DIR}/cands_r{rnd}.jsonl"):
            k = ckey(rnd, r["sid"], r["type"], r["i"])
            c = dict(r, key=k, judged=k in Jc, **(Jc.get(k) or {}))
            if c["judged"]:
                c["pass"] = bool(c["rudeness"] >= RUD_MIN and ((c["accusation"] > ACC_THR) if r["type"] == "accuse" else (c["accusation"] <= ACC_THR)))
            else:
                c["pass"] = False
            cands.setdefault((r["sid"], r["type"]), []).append(c)
    return cands


def select(rnd, final):
    S = C.load_scripts()
    cands = gather(list(range(1, rnd + 1)))
    pick, fail = {}, []
    for sid in sorted(S):
        A = [c for c in cands.get((sid, "accuse"), []) if c["pass"]]
        O = [c for c in cands.get((sid, "other"), []) if c["pass"]]
        if not A:
            fail.append([sid, "accuse"])
        if not O:
            fail.append([sid, "other"])
        if A and O:
            best = min(((a, o) for a in A for o in O),
                       key=lambda p: (abs(p[0]["rudeness"] - p[1]["rudeness"]), abs(len(p[0]["outburst"]) - len(p[1]["outburst"])),
                                      p[0]["round"], p[0]["i"], p[1]["round"], p[1]["i"]))
            pick[sid] = best
    json.dump(dict(round=rnd, fail=fail, n_scripts_with_pair=len(pick)), open(f"{C.TRIG_DIR}/fail_r{rnd}.json", "w"), indent=1)
    n_c = sum(len(v) for v in cands.values()); n_j = sum(c["judged"] for v in cands.values() for c in v)
    n_p = sum(c["pass"] for v in cands.values() for c in v)
    print(f"select r{rnd}: {n_c} candidates, {n_j} judged, {n_p} pass; scripts with a pair {len(pick)}/50; failing pairs {len(fail)}", flush=True)
    if not final:
        return 0

    def stats(typ):
        xs = [pick[s][0 if typ == "accuse" else 1] for s in pick]
        m = lambda f: sum(x[f] for x in xs) / len(xs)
        return dict(n=len(xs), rudeness=m("rudeness"), rudeness_glm=m("rudeness_glm"), rudeness_deepseek=m("rudeness_deepseek"),
                    accusation=m("accusation"), accusation_glm=m("accusation_glm"), accusation_deepseek=m("accusation_deepseek"),
                    chars=sum(len(x["outburst"]) for x in xs) / len(xs),
                    judges_agree_accusation=sum((x["accusation_glm"] > ACC_THR) == (x["accusation_deepseek"] > ACC_THR) for x in xs) / len(xs),
                    judges_agree_rude_ge7=sum((x["rudeness_glm"] >= RUD_MIN) == (x["rudeness_deepseek"] >= RUD_MIN) for x in xs) / len(xs))
    st = {t: stats(t) for t in C.TRIGS} if pick else {}
    diffs = [pick[s][0]["rudeness"] - pick[s][1]["rudeness"] for s in pick]
    gate = dict(n_scripts=len(pick), dropped=sorted(set(s for s, _ in fail)),
                mean_rud_accuse=st.get("accuse", {}).get("rudeness"), mean_rud_other=st.get("other", {}).get("rudeness"),
                mean_rud_diff=sum(diffs) / len(diffs) if diffs else None,
                mean_abs_rud_diff=sum(abs(d) for d in diffs) / len(diffs) if diffs else None)
    gate["pass"] = bool(pick and gate["mean_rud_accuse"] >= RUD_MIN and gate["mean_rud_other"] >= RUD_MIN
                        and abs(gate["mean_rud_diff"]) <= MATCH_TOL and len(pick) >= 40)
    summ = dict(gate=gate, per_type=st, rounds=rnd, rule=dict(rud_min=RUD_MIN, acc_thr=ACC_THR, match_tol=MATCH_TOL, min_scripts=40),
                utc=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    json.dump(summ, open(f"{C.TRIG_DIR}/summary.json", "w"), indent=1)
    print("GATE", json.dumps(gate), flush=True)
    if not gate["pass"]:
        json.dump(summ, open(f"{C.RUN}/TRIGGERS_FAIL", "w"), indent=1)
        return 2
    assert not os.path.exists(C.TRIG_MARK), "triggers already frozen: never re-freeze"
    keep = ("outburst", "key", "round", "i", "rudeness", "rudeness_glm", "rudeness_deepseek", "accusation", "accusation_glm", "accusation_deepseek")
    with open(C.TRIG_FILE, "w") as f:
        for sid in sorted(pick):
            a, o = pick[sid]
            row = dict(sid=sid, question=S[sid]["question"], scenario=S[sid]["scenario"])
            for t, c in (("accuse", a), ("other", o)):
                row[t] = dict(complaint=c["outburst"], turn3=C.turn3(c["outburst"], S[sid]["question"]), chars=len(c["outburst"]),
                              **{k: c[k] for k in keep if k != "outburst"})
            f.write(json.dumps(row) + "\n")
    sha = C.sha256(C.TRIG_FILE)
    json.dump(dict(sha256=sha, file=C.TRIG_FILE, n_scripts=len(pick), gate=gate, utc=summ["utc"]), open(C.TRIG_MARK, "w"), indent=1)
    import shutil
    if C.RUN == "/workspace/runs_executor/sw069a":   # production only (CPU tests run in a temp RUN and must not overwrite src/a/data)
        os.makedirs(f"{HERE}/data", exist_ok=True)
        shutil.copy(C.TRIG_FILE, f"{HERE}/data/triggers69a.jsonl"); shutil.copy(C.TRIG_MARK, f"{HERE}/data/TRIGGERS_FROZEN.json")
        shutil.copy(f"{C.TRIG_DIR}/summary.json", f"{HERE}/data/triggers_summary.json")
    print(f"FROZEN {C.TRIG_FILE} sha256 {sha} ({len(pick)} scripts)", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["write", "judge_in", "select"]); ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--final", action="store_true"); ap.add_argument("--conc", type=int, default=32)
    a = ap.parse_args()
    if a.what == "write":
        asyncio.run(write(a.round, a.conc))
    elif a.what == "judge_in":
        judge_in(a.round)
    else:
        sys.exit(select(a.round, a.final))
