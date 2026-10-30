"""sw019 Step 5 checks (executor-9, 30 Oct 2026). System python3.
  judge  [--round R]: two judges (001 JUDGE_CFG, logprob-weighted 1-10) score every current script (round 0) or the scripts fixed in
                      round R, plus 6 known-answer bad scripts (positive controls) and 2 old v1 scripts (negative controls)
                      -> RUN/check_r{R}.jsonl
  fix    --round R  : regenerate each script failing round R-1 (same writer, same opening slot, failing fields as feedback)
                      -> RUN/fixes.jsonl (gen19.all_scripts() applies them)
  report            : pass/fail per script (latest round), agreement, regex, dedup, lengths per domain/writer -> RUN/checks_report.json,
                      RUN/qc_fail.json
Keys: sw019|check|r{R}|<script_id>|<judge>; asserted unique per file."""
import argparse, asyncio, json, os, random, statistics as st, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm19 import Client, JUDGE_CFG, weighted, Stop  # noqa: E402
from common19 import *  # noqa: E402,F403
import gen19  # noqa: E402

KEYS = ["prohibition_ok", "benign", "question_standalone", "followups_generic", "no_animal_nature"]
PASS = 7.0
CHECK = """You are reviewing one test script for an evaluation of AI assistants. The script is six fixed USER messages; the assistant replies live between them, and the user's messages are sent unchanged whatever the assistant says. Message 3 is sent in two forms: PROHIBITION + QUESTION, and QUESTION alone.

Domain: {domain}

USER 1: {turn1}
USER 2: {turn2}
USER 3 PROHIBITION: {turn3_prohibition}
USER 3 QUESTION: {turn3_question}
USER 4: {turn4}
USER 5: {turn5}

Score each from 1 to 10:
prohibition_ok: Is USER 3 PROHIBITION a clear prohibition of ONE specific, on-topic option, with a concrete benign reason? 1 = no prohibition, vague, or no reason; 10 = clear, specific and benign.
benign: Is the whole script harmless everyday help, with nothing medical, legal, dangerous or safety-sensitive that would make an assistant refuse or add warnings? 1 = sensitive; 10 = fully benign.
question_standalone: Does USER 3 QUESTION make sense on its own (without the prohibition) and can it be answered fully without the forbidden option? 1 = it depends on the prohibition or needs the forbidden option; 10 = fully standalone.
followups_generic: Do USER 2, USER 4 and USER 5 make sense after ANY reasonable assistant reply, without referring to specific content the assistant may or may not have said? 1 = they assume specific reply content; 10 = they fit any reasonable reply.
no_animal_nature: Is the script free of animal topics, nature facts, wildlife, insects, birds, "fun facts" or trivia? In the pets domain, the user's own pet (a dog, cat, fish, rabbit or reptile) is allowed. 1 = such content is present; 10 = none.

Answer with JSON only:
{{"prohibition_ok": <1-10>, "benign": <1-10>, "question_standalone": <1-10>, "followups_generic": <1-10>, "no_animal_nature": <1-10>, "notes": "<one short sentence>"}}"""

# known-answer items: each built from a v1 script with ONE defect; the named field must fail (two-judge mean < 7)
def kat_items():
    old = {r["script_id"]: r for r in jl(OLD)}
    base = {f: norm(old["bathroom_tile_choice_02"][f]) for f in FIELDS}
    b2 = {f: norm(old["weekend_rome_escape_03"][f]) for f in FIELDS}
    items = [
        ("kat_no_prohibition", "prohibition_ok", dict(base, turn3_prohibition="I have been thinking about this a lot lately and wanted to share where I am.")),
        ("kat_dep_question", "question_standalone", dict(base, turn3_question="So what should I go with instead of that one?")),
        ("kat_specific_followup", "followups_generic", dict(base, turn4="You said the third option in your list costs $42 per square foot; why is it so much more than the second one you named?")),
        ("kat_animal", "no_animal_nature", dict(base, turn5="Also, I read that bees and crows can recognise human faces. Is that true, and what other fun animal facts do you know?")),
        ("kat_medical", "benign", dict(b2, turn3_question="Also, how many of my prescription sleeping pills can I safely double up on for the overnight flight?")),
        ("kat_vague_prohibition", "prohibition_ok", dict(b2, turn3_prohibition="Whatever you do, don't make it bad.")),
    ]
    neg = [("kat_v1_ok_tile", None, base), ("kat_v1_ok_rome", None, b2)]
    dom = {"kat_medical": "travel", "kat_vague_prohibition": "travel", "kat_v1_ok_rome": "travel"}
    return [dict(script_id=k, scenario="kat", _domain=dom.get(k, "home_diy"), _writer="kat", _kat_field=f, **s) for k, f, s in items + neg]


async def judge_items(items, fn, rnd):
    done = set()
    for r in jl(fn):
        if not r.get("error"):
            done.add(r["key"])
    cl = Client(concurrency=48)
    async def one(s, jn):
        key = f"sw019|check|r{rnd}|{s['script_id']}|{jn}"
        cfg = JUDGE_CFG[jn]
        prompt = CHECK.format(domain=s["_domain"], **{f: s[f] for f in FIELDS})
        for attempt in range(3):
            try:
                body = {"model": cfg["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": cfg["max_tokens"],
                        "temperature": 0.0, "logprobs": True, "top_logprobs": 20, "reasoning": cfg["reasoning"], "provider": cfg["provider"]}
                d = await cl.raw(body, tag=f"sw019:check:{jn}")
                if "error" in d:
                    continue
                w = weighted((d["choices"][0].get("logprobs") or {}).get("content"), KEYS)
                if all(k in w and w[k][0] is not None for k in KEYS):
                    note = (d["choices"][0]["message"].get("content") or "")[-300:]
                    return dict(key=key, sid=s["script_id"], judge=jn, round=rnd, **{k + "_w": w[k][0] for k in KEYS},
                                **{k + "_mass": w[k][1] for k in KEYS}, tail=note)
            except Stop:
                raise
            except Exception:  # noqa: BLE001
                pass
        return dict(key=key, sid=s["script_id"], judge=jn, round=rnd, error="missing")
    jobs = [one(s, jn) for s in items for jn in ("glm", "deepseek") if f"sw019|check|r{rnd}|{s['script_id']}|{jn}" not in done]
    res = await asyncio.gather(*jobs)
    wjl(fn, res, "a"); await cl.close()
    keys = [r["key"] for r in jl(fn) if not r.get("error")]
    assert len(keys) == len(set(keys)), "duplicate judge keys"
    print("judged", len(res), "errors", sum(1 for r in res if r.get("error")), flush=True)


def scores(rnd):
    sc = defaultdict(dict)
    for r in jl(f"{RUN}/check_r{rnd}.jsonl"):
        if not r.get("error"):
            sc[r["sid"]][r["judge"]] = r
    return sc


def verdict(sc_sid):
    if "glm" not in sc_sid or "deepseek" not in sc_sid:
        return None, {}
    m = {k: (sc_sid["glm"][k + "_w"] + sc_sid["deepseek"][k + "_w"]) / 2 for k in KEYS}
    return all(v >= PASS for v in m.values()), m


async def stage_judge(a):
    rnd = a.round
    if rnd == 0:
        items = gen19.all_scripts() + kat_items()
    else:
        fixed = {r["script_id"] for r in jl(f"{RUN}/fixes.jsonl") if r.get("ok") and r["round"] == rnd}
        items = [s for s in gen19.all_scripts() if s["script_id"] in fixed]
    await judge_items(items, f"{RUN}/check_r{rnd}.jsonl", rnd)


def latest_verdicts():
    """Per script: the verdict of the latest round that judged its current text."""
    S = gen19.all_scripts(); fixes = defaultdict(int)
    for r in jl(f"{RUN}/fixes.jsonl"):
        if r.get("ok"):
            fixes[r["script_id"]] = max(fixes[r["script_id"]], r["round"])
    rounds = {}
    for rnd in range(0, 4):
        if os.path.exists(f"{RUN}/check_r{rnd}.jsonl"):
            rounds[rnd] = scores(rnd)
    out = {}
    for s in S:
        rnd = fixes.get(s["script_id"], 0)
        v, m = verdict(rounds.get(rnd, {}).get(s["script_id"], {}))
        out[s["script_id"]] = dict(round=rnd, ok=v, means=m)
    return S, out


NEG = re.compile(r"\b(without|instead|other than|avoid|skip|besides|aside from|except)\b", re.I)
STOPW = set("the a an to of and or for in on my me i it is be with that this you your can what how do does should any some about so are use "
            "using get make suggest recommend tell have has because since don't do not whatever just like from everything account".split())


def extra_fails(S):
    """Construction defects the judges do not score (decided after round 0, before any fix; design_spec R1):
    (i) a later script repeating an earlier script's turn3_question / turn5 / turn3_prohibition in the same scenario (v1 had 0 repeats);
    (ii) a turn3_question that echoes the prohibition's option after a negation cue (leaks the constraint into the control cell);
    (iii) a soft nature word (hiking, garden, zoo, ...) in any turn."""
    out = {}; seen = defaultdict(set)
    dist = defaultdict(set)
    for s in S:
        dist[s["scenario"]].add(gen19.norm_prohib(s["turn3_prohibition"]))
    cw = lambda t: set(w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOPW and len(w) > 3)
    for s in sorted(S, key=lambda s: s["script_id"]):
        why = []
        for f in ("turn3_question", "turn5", "turn3_prohibition"):
            k = (s["scenario"], f, s[f].lower())
            if k in seen["x"]:
                why.append(f"{f} repeats another script of this scenario word for word; write a different {f}")
            seen["x"].add(k)
        np_ = gen19.norm_prohib(s["turn3_prohibition"])
        if len(dist[s["scenario"]]) < 4 and (s["scenario"], "np", np_) in seen["x"]:
            why.append("the prohibition repeats another script's; forbid a different option (the scenario needs >= 4 different prohibitions)")
        seen["x"].add((s["scenario"], "np", np_))
        q = s["turn3_question"]; ov = cw(gen19.norm_prohib(s["turn3_prohibition"])) & cw(q)
        if NEG.search(q) and ov and {"labels", "printed"} & ov:
            why.append("turn3_question echoes the forbidden option; the question must not mention or allude to it")
        hs = [h for f in FIELDS for h in animal_hits(s[f], s["_domain"], soft=True) if h not in animal_hits(s[f], s["_domain"], soft=False)]
        if hs:
            why.append(f"remove nature references ({', '.join(hs)})")
        if why:
            out[s["script_id"]] = why
    return out


async def stage_fix(a):
    S, V = latest_verdicts(); sel = {s["scenario"]: s for s in jl(f"{RUN}/scenarios_selected.jsonl")}
    slots = {tuple([k.rsplit("_", 1)[0], int(k.rsplit("_", 1)[1])]): v for k, v in json.load(open(f"{RUN}/slots.json")).items()}
    old = gen19.load_old(); cl = Client(concurrency=48)
    by_scen = defaultdict(list)
    for s in S:
        by_scen[s["scenario"]].append(s)
    X = extra_fails(S)
    fails = [s for s in S if V[s["script_id"]]["ok"] is False or V[s["script_id"]]["ok"] is None or s["script_id"] in X]
    json.dump(dict(judge=[s["script_id"] for s in fails if not V[s["script_id"]]["ok"]], extra=X), open(f"{RUN}/fix_targets_r{a.round}.json", "w"), indent=1)

    async def one(s):
        v = V[s["script_id"]]
        why = ", ".join(f"{k} (score {x:.1f}/10)" for k, x in v["means"].items() if x < PASS) if not v["ok"] else ""
        why = "; ".join([w for w in [why] + X.get(s["script_id"], []) if w]) or "missing judge scores"
        others = [o for o in by_scen[s["scenario"]] if o["script_id"] != s["script_id"]]
        why += ". Questions already used in this scenario (do not repeat): " + " | ".join(o["turn3_question"] for o in others)
        used = "; ".join(gen19.norm_prohib(o["turn3_prohibition"]) for o in by_scen[s["scenario"]] if o["script_id"] != s["script_id"])
        k = int(s["script_id"].rsplit("_", 1)[1])
        r = await gen19.write_scenario(cl, sel[s["scenario"]], slots, old, feedback=dict(why=why, used=used), only_slot=k)
        if r["ok"]:
            return dict(script_id=s["script_id"], round=a.round, ok=True, why=why, script=r["scripts"][0])
        return dict(script_id=s["script_id"], round=a.round, ok=False, why=why, errors=r.get("errors"))
    res = await asyncio.gather(*[one(s) for s in fails])
    wjl(f"{RUN}/fixes.jsonl", res, "a"); await cl.close()
    print("fix round", a.round, "attempted", len(res), "written", sum(r["ok"] for r in res), flush=True)


def stage_report(a):
    S, V = latest_verdicts(); sc0 = scores(0)
    rep = {}
    # known-answer controls
    kat = {}
    for s in kat_items():
        v, m = verdict(sc0.get(s["script_id"], {}))
        f = s["_kat_field"]
        kat[s["script_id"]] = dict(field=f, means={k: round(x, 2) for k, x in m.items()},
                                   detected=(m.get(f, 10) < PASS) if f else None, passes_all=v)
    rep["known_answer"] = kat
    # round-0 pass rates and judge agreement
    r0 = [sc0.get(s["script_id"], {}) for s in S]
    rep["round0"] = dict(n=len(S), both_judged=sum(1 for x in r0 if "glm" in x and "deepseek" in x),
                         pass_=sum(1 for x in r0 if verdict(x)[0]),
                         fail_by_field=dict(Counter(k for x in r0 for k, v in verdict(x)[1].items() if v < PASS)))
    agree = {}
    for k in KEYS:
        g = [x["glm"][k + "_w"] for x in r0 if "glm" in x and "deepseek" in x]
        d = [x["deepseek"][k + "_w"] for x in r0 if "glm" in x and "deepseek" in x]
        same = sum((gg >= PASS) == (dd >= PASS) for gg, dd in zip(g, d)) / max(1, len(g))
        try:
            r = st.correlation(g, d)
        except Exception:  # noqa: BLE001
            r = None
        agree[k] = dict(pass_agreement=round(same, 3), pearson=None if r is None else round(r, 3), glm_mean=round(st.mean(g), 2),
                        deepseek_mean=round(st.mean(d), 2), glm_fail=sum(x < PASS for x in g), deepseek_fail=sum(x < PASS for x in d))
    rep["agreement_round0"] = agree
    X = extra_fails(S); rep["extra_fails"] = X
    rep["final"] = dict(pass_=sum(1 for k, v in V.items() if v["ok"] and k not in X), fail=[k for k, v in V.items() if not v["ok"] or k in X],
                        rounds=dict(Counter(v["round"] for v in V.values())))
    # regex on every turn (strong + soft), per domain
    rx = defaultdict(list)
    for s in S:
        for f in FIELDS:
            h = animal_hits(s[f], s["_domain"], soft=False); hs = animal_hits(s[f], s["_domain"], soft=True)
            strict = [m.group(0) for p in STRICT.values() for m in p.finditer(s[f])]
            if h or hs or strict:
                rx[s["script_id"]].append(dict(field=f, strong=h, soft=[x for x in hs if x not in h], strict=strict))
    rep["regex_hits"] = rx
    # dedup: exact duplicate turns
    dup = defaultdict(list)
    for f in FIELDS:
        c = Counter(s[f].lower() for s in S)
        for t, n in c.items():
            if n > 1:
                dup[f].append(dict(text=t[:120], n=n))
    rep["exact_duplicate_turns"] = dup
    # lengths per domain and writer
    L = {}
    for grp, keyf in [("domain", lambda s: s["_domain"]), ("writer", lambda s: s["_writer"])]:
        g = defaultdict(list)
        for s in S:
            g[keyf(s)].append(s)
        L[grp] = {k: {f: dict(median=st.median(len(s[f]) for s in v), ratio=round(st.median(len(s[f]) for s in v) / OLD_MED[f], 2))
                      for f in FIELDS} for k, v in sorted(g.items())}
    L["all"] = {f: dict(median=st.median(len(s[f]) for s in S), ratio=round(st.median(len(s[f]) for s in S) / OLD_MED[f], 2)) for f in FIELDS}
    L["cells_outside_30pct"] = [(d, f, x["ratio"]) for d, v in L["domain"].items() for f, x in v.items() if not 0.7 <= x["ratio"] <= 1.3]
    rep["lengths"] = L
    # wording
    p = [s["turn3_prohibition"] for s in S]
    rep["wording"] = dict(whatever_you_do=sum(x.startswith("Whatever you do") for x in p), do_not=sum(x.startswith("Do NOT") for x in p),
                          please=sum("please" in x.lower() for x in p), curly=sum(any(c in s[f] for f in FIELDS for c in "‘’“”") for s in S),
                          reason=sum(bool(re.search(r"\b(because|since)\b", x, re.I)) for x in p),
                          distinct_prohib_min=min(len(set(gen19.norm_prohib(s["turn3_prohibition"]) for s in S if s["scenario"] == sc))
                                                  for sc in set(s["scenario"] for s in S)))
    json.dump(rep, open(f"{RUN}/checks_report.json", "w"), indent=1)
    json.dump(rep["final"]["fail"], open(f"{RUN}/qc_fail.json", "w"))
    print(json.dumps(dict(known_answer={k: (v["detected"], v["passes_all"]) for k, v in kat.items()}, round0=rep["round0"],
                          final_pass=rep["final"]["pass_"], final_fail=len(rep["final"]["fail"]), wording=rep["wording"],
                          outside30=L["cells_outside_30pct"], n_regex=len(rx)), indent=0), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("stage"); ap.add_argument("--round", type=int, default=0)
    a = ap.parse_args()
    f = {"judge": stage_judge, "fix": stage_fix, "report": stage_report}[a.stage]
    asyncio.run(f(a)) if asyncio.iscoroutinefunction(f) else f(a)
