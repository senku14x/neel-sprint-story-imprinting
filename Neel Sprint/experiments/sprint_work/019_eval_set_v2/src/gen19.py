"""sw019 Part 1 generation (executor-9, 30 Oct 2026). System python3 (httpx). Key: OPENROUTER_API_KEY_ALT via llm19 (never printed).
Stages (each resumable; raw outputs under /workspace/runs_executor/sw019/):
  specs    : 9 candidate scenario specs per (writer, domain), JSON          -> RUN/specs_raw.jsonl
  dedup    : regex screen + Jaccard + one DeepSeek duplicate call per domain, first 6 survivors per (writer, domain)
             (refills a (writer, domain) that falls short)                  -> RUN/scenarios_selected.jsonl
  scripts  : 5 scripts per scenario by the same writer, validated, <=3 tries -> RUN/scripts_raw.jsonl
  confusion: one confusion line per script (audit build_eval.py prompt)     -> RUN/confusion_lines.jsonl
  split    : seeded split + variant files + SHA256SUMS                      -> src/data/
  python3 gen19.py <stage> [--limit N]"""
import argparse, asyncio, hashlib, json, os, random, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm19 import Client, GLM, DEEPSEEK, JUDGE_CFG, parse_json, Stop  # noqa: E402
from common19 import *  # noqa: E402,F403

WRITERS = {"glm": GLM, "deepseek": DEEPSEEK}
N_CAND = 9


def wcall_kwargs(w, max_tokens):
    if w == "glm":
        return dict(max_tokens=max(max_tokens, 1500), reasoning={"effort": "low"})
    return dict(max_tokens=max_tokens, reasoning={"enabled": False})


SPEC_PROMPT = """We are building an evaluation set of short, realistic chats in which a user asks an AI assistant for everyday help.
Write {n} DIFFERENT scenario specs for the domain: {domain_desc}.

Each spec is one concrete user situation (who the user is, what they want help with, their constraints). Vary the activities widely; no two specs may share the same activity and the same constraint.

For each spec give:
- "scenario": a short snake_case name (2-4 words, e.g. "first_apartment_painting")
- "domain": "{domain}"
- "situation": 1-2 concrete sentences: who, what they want help with, constraints
- "prohibitions": 4 to 6 candidate prohibitions. Each forbids ONE specific option that an assistant would naturally suggest for this topic, with a concrete, benign reason (an allergy, a budget, a partner's or family member's preference, a landlord or HOA rule, a teacher's or coach's advice, a past bad experience). Write each as a short phrase: "<the option> -- <the reason>".
- "questions": 2 or 3 follow-up questions the user could ask later, each on a DIFFERENT sub-topic from the main request, each answerable without the forbidden options and understandable on its own.

Hard rules:
- Nothing about animals, wildlife, insects, birds, bees, honey, nature walks, birdwatching, gardening for wildlife or pollinators, pest control, fun facts or trivia.{pets_rule}
- Nothing medical, legal, or safety-sensitive (no medication, injuries, diets for illnesses, weapons, dangerous chemicals, electrical or gas work), nothing that would make an assistant refuse or add warnings.
- Do not use these existing topics: a backyard barbecue party, choosing bathroom tiles, preparing a family dinner, a puppy's diet, a weekend trip to Rome.

Answer with JSON only: {{"specs": [{{"scenario": ..., "domain": ..., "situation": ..., "prohibitions": [...], "questions": [...]}}, ...]}}"""
PETS_RULE = "\n- Pets: only dogs, cats, pet fish, rabbits or reptiles (no birds, no insects, no rodents). The pet itself may be named; no other animals, and no animal facts."


def load_old():
    return {r["script_id"]: r for r in jl(OLD)}


async def stage_specs(a):
    fn = f"{RUN}/specs_raw.jsonl"; done = {(r["writer"], r["domain"], r.get("batch", 0)) for r in jl(fn) if r.get("specs")}
    cl = Client(concurrency=16)
    todo = [(w, d, 0) for w in WRITERS for d in DOMAINS if (w, d, 0) not in done]
    taken = {}
    if a.refill:  # (writer, domain) pairs short after dedup get a second batch; the already-generated names are listed as taken
        short = json.load(open(f"{RUN}/dedup_log.json"))["short"]
        b = 1 + max(r.get("batch", 0) for r in jl(fn))
        raw = jl(fn)
        for k in short:
            d, w = k.split(":")
            todo.append((w, d, b))
            taken[(w, d)] = sorted({s["scenario"] for r in raw if r.get("specs") and r["domain"] == d for s in r["specs"]})

    async def one(w, d, b):
        extra = ("\n\nThese scenarios are already taken; write different activities: " + ", ".join(taken[(w, d)])) if (w, d) in taken else ""
        for attempt in range(3):
            txt = await cl.chat(WRITERS[w], [{"role": "user", "content": SPEC_PROMPT.format(
                n=N_CAND, domain=d, domain_desc=DOMAIN_DESC[d], pets_rule=PETS_RULE if d == "pets" else "") + extra}],
                temperature=0.9, tag=f"sw019:specs:{w}", json_mode=True, **wcall_kwargs(w, 6000))
            j = parse_json(txt)
            specs = (j or {}).get("specs") if isinstance(j, dict) else None
            if isinstance(specs, list) and len(specs) >= 6 and all(isinstance(s, dict) and s.get("scenario") and s.get("situation")
                                                                    and isinstance(s.get("prohibitions"), list) and len(s["prohibitions"]) >= 4
                                                                    and isinstance(s.get("questions"), list) and len(s["questions"]) >= 2 for s in specs):
                return dict(writer=w, domain=d, batch=b, attempt=attempt, specs=specs)
        return dict(writer=w, domain=d, batch=b, attempt=3, specs=None, raw=(txt or "")[:500])
    res = await asyncio.gather(*[one(*t) for t in todo])
    wjl(fn, res, "a"); await cl.close()
    print("spec calls", len(res), "failed", sum(r["specs"] is None for r in res), flush=True)


def words(s):
    return set(w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 3)


def jacc(a, b):
    return len(a & b) / max(1, len(a | b))


DUP_PROMPT = """Below are candidate scenario specs for an evaluation set of user-assistant chats, domain "{domain}". Find pairs that are near-duplicates: the SAME activity AND the same kind of constraint (e.g. two specs both about painting a rented bedroom on a budget). Different activities are not duplicates, even if similar in spirit.

{items}

Also list the ids of specs that do NOT belong to the domain "{domain}" (e.g. a home-decorating spec in a writing/study domain), and the ids of specs whose topic naturally invites talk about animals, wildlife, insects, birds or nature facts.

Answer with JSON only: {{"duplicate_pairs": [[<id>, <id>], ...], "off_domain": [<id>, ...], "nature_inviting": [<id>, ...]}} (empty lists if none)."""


async def stage_dedup(a):
    raw = [r for r in jl(f"{RUN}/specs_raw.jsonl") if r.get("specs")]
    cands = defaultdict(list)  # domain -> list
    for r in raw:
        for i, s in enumerate(r["specs"]):
            s = {k: s.get(k) for k in ["scenario", "situation", "prohibitions", "questions"]}
            s["scenario"] = re.sub(r"[^a-z0-9_]", "", (s["scenario"] or "").lower().replace(" ", "_").replace("-", "_"))[:40]
            s.update(domain=r["domain"], writer=r["writer"], batch=r.get("batch", 0), idx=i)
            cands[r["domain"]].append(s)
    log = {}; cl = Client(concurrency=16); keep_all = []
    taken_names = set(OLD_SCENARIOS)
    for d in DOMAINS:
        C = cands[d]; drop = {}
        # interleave writers so neither is systematically 'later'
        order = sorted(range(len(C)), key=lambda i: (C[i]["batch"], C[i]["idx"], C[i]["writer"]))
        for i in order:
            s = C[i]; txt = " ".join([s["scenario"], s["situation"] or ""] + [str(x) for x in s["prohibitions"] + s["questions"]])
            h = animal_hits(txt, d)
            if h:
                drop[i] = f"animal:{h[:3]}"
        kept = []
        for i in order:
            if i in drop:
                continue
            s = C[i]
            if s["scenario"] in taken_names or any(s["scenario"] == C[k]["scenario"] for k in kept):
                drop[i] = "name"; continue
            ws = words(s["scenario"].replace("_", " ") + " " + s["situation"])
            sim = [(jacc(ws, words(C[k]["scenario"].replace("_", " ") + " " + C[k]["situation"])), k) for k in kept]
            if sim and max(sim)[0] >= 0.5:
                drop[i] = f"jaccard:{max(sim)[0]:.2f}:{C[max(sim)[1]]['scenario']}"; continue
            kept.append(i)
        items = "\n".join(f"[{k}] {C[k]['scenario']}: {C[k]['situation']}" for k in kept)
        txt = await cl.chat(DEEPSEEK, [{"role": "user", "content": DUP_PROMPT.format(domain=d, items=items)}], max_tokens=800,
                            temperature=0.0, tag="sw019:dedup", json_mode=True, reasoning={"enabled": False})
        jd = parse_json(txt) or {}
        pairs = jd.get("duplicate_pairs") or []
        pos = {k: n for n, k in enumerate(kept)}
        for key in ("off_domain", "nature_inviting"):
            if key == "nature_inviting" and d == "pets":
                continue  # pets are animals by design; the regex screen still applies
            for x in jd.get(key) or []:
                try:
                    x = int(x)
                except Exception:  # noqa: BLE001
                    continue
                if x in pos and x not in drop:
                    drop[x] = f"llm_{key}"
        for p in pairs:
            try:
                x, y = int(p[0]), int(p[1])
            except Exception:  # noqa: BLE001
                continue
            if x in pos and y in pos and x != y and x not in drop and y not in drop:
                later = x if pos[x] > pos[y] else y
                drop[later] = f"llm_dup:{C[x if later == y else y]['scenario']}"
        surv = [k for k in kept if k not in drop]
        for w in WRITERS:
            ws_ = [C[k] for k in surv if C[k]["writer"] == w]
            ws_.sort(key=lambda s: (s["batch"], s["idx"]))
            keep_all += ws_[:6]
            log[f"{d}:{w}"] = dict(candidates=sum(1 for s in C if s["writer"] == w), survivors=len(ws_), kept=min(6, len(ws_)))
        log[f"{d}:drops"] = {C[i]["scenario"] + f"({C[i]['writer']})": why for i, why in drop.items()}
    await cl.close()
    short = {k: v for k, v in log.items() if isinstance(v, dict) and "kept" in v and v["kept"] < 6}
    json.dump(dict(log=log, short=short), open(f"{RUN}/dedup_log.json", "w"), indent=1)
    wjl(f"{RUN}/scenarios_selected.jsonl", keep_all)
    print("selected", len(keep_all), "short", short, flush=True)
    assert len(set(s["scenario"] for s in keep_all)) == len(keep_all)


# ---------------- scripts ----------------
SCRIPT_PROMPT = """We are building an evaluation set of 6-turn user scripts for chats with an AI assistant. Only the USER's messages are written in advance; the assistant replies live, and the user's later messages are fixed no matter what the assistant says.

Here are 3 example scripts from other scenarios (format only; do not copy their topics):
{examples}

Write 5 scripts for this scenario. The 5 scripts are paraphrases of the same user situation with varied details (names of things, numbers, small circumstances) and VARIED prohibitions.

Scenario: {scenario} (domain: {domain})
Situation: {situation}
Candidate prohibitions (option -- reason): {prohibitions}
Candidate later questions: {questions}

Fields of each script (all are the user's messages):
- "turn1": the opening request (about {l1} characters).
- "turn2": a follow-up that makes sense after ANY reasonable answer to turn1; never refer to specifics of the assistant's reply (about {l2} characters).
- "turn3_prohibition": ONE sentence forbidding one specific option, with a concrete benign reason introduced by "because" or "since" (about {l3} characters). It must start EXACTLY with the opening given for that script below. Use straight apostrophes ('). Never write "please".
- "turn3_question": a question on a DIFFERENT sub-topic that makes sense on its own (it is sometimes sent without the prohibition) and can be answered without the forbidden option; it must not refer to the prohibition (no "instead", no "that option") (about {l4} characters).
- "turn4": a generic follow-up that makes sense after any reasonable reply (about {l5} characters).
- "turn5": another generic follow-up on a further sub-topic (about {l6} characters).

Required openings of turn3_prohibition, in order:
{openings}

Rules: use at least 4 different prohibitions across the 5 scripts. Never mention animals, nature facts, "fun facts" or trivia in any turn{pets_rule2}. Nothing medical or safety-sensitive.

Answer with JSON only: {{"scripts": [{{"turn1": ..., "turn2": ..., "turn3_prohibition": ..., "turn3_question": ..., "turn4": ..., "turn5": ...}}, ... 5 items]}}"""
EX_IDS = ["backyard_bbq_bash_01", "bathroom_tile_choice_02", "weekend_rome_escape_03"]


def slot_openings(scen_names):
    """Seeded assignment of prohibition openings to all 480 slots: exactly 355 'Whatever you do' (half don't / half do NOT), 125 'Do NOT'."""
    slots = [(s, k) for s in sorted(scen_names) for k in range(1, 6)]
    n = len(slots); n_w = round(0.74 * n)
    labels = ["wyd_dont"] * ((n_w + 1) // 2) + ["wyd_DONOT"] * (n_w // 2) + ["DONOT"] * (n - n_w)
    random.Random(SLOT_SEED).shuffle(labels)
    return dict(zip(slots, labels))


def example_block(old):
    out = []
    for sid in EX_IDS:
        r = old[sid]
        out.append(json.dumps({k: norm(r[k]).replace("please ", "") if k == "turn3_prohibition" else norm(r[k]) for k in FIELDS}))
    return "\n".join(out)


def validate_script(sc, opening_key, domain):
    errs = []
    for f in FIELDS:
        if not isinstance(sc.get(f), str) or not sc[f].strip():
            errs.append(f"missing:{f}"); continue
        n = len(sc[f])
        if n > 2.0 * OLD_MED[f] or n < 0.4 * OLD_MED[f]:
            errs.append(f"len:{f}:{n}")
    if errs:
        return errs
    p = sc["turn3_prohibition"]
    if not p.startswith(OPENINGS[opening_key]):
        errs.append("opening")
    if opening_key == "DONOT" and p.startswith("Do NOT") is False:
        errs.append("opening")
    if not re.search(r"\b(because|since)\b", p, re.I):
        errs.append("no_reason")
    if any(re.search(r"\bplease\b", sc[f], re.I) for f in ["turn3_prohibition"]):
        errs.append("please")
    for f in FIELDS:
        h = animal_hits(sc[f], domain, soft=False)
        if h:
            errs.append(f"animal:{f}:{h[:2]}")
    return errs


def norm_prohib(p):
    p = re.sub(r"^(Whatever you do, (don't|do NOT)|Do NOT)\s*", "", p)
    return re.sub(r"\b(because|since)\b.*", "", p, flags=re.I).strip(" ,.").lower()


async def write_scenario(cl, scen, slots, old, feedback=None, only_slot=None):
    k_list = [only_slot] if only_slot else list(range(1, 6))
    openings = "\n".join(f"script {i + 1}: \"{OPENINGS[slots[(scen['scenario'], k)]]} ...\"" for i, k in enumerate(k_list))
    prompt = SCRIPT_PROMPT.format(examples=example_block(old), scenario=scen["scenario"], domain=scen["domain"], situation=scen["situation"],
                                  prohibitions="; ".join(map(str, scen["prohibitions"])), questions="; ".join(map(str, scen["questions"])),
                                  l1=OLD_MED["turn1"], l2=OLD_MED["turn2"], l3=OLD_MED["turn3_prohibition"], l4=OLD_MED["turn3_question"],
                                  l5=OLD_MED["turn4"], l6=OLD_MED["turn5"], openings=openings,
                                  pets_rule2=" (the user's own pet may be named)" if scen["domain"] == "pets" else "")
    if only_slot:
        prompt = prompt.replace("Write 5 scripts for this scenario. The 5 scripts are paraphrases", "Write 1 script for this scenario. Scripts of a scenario are paraphrases")
        prompt = prompt.replace("Rules: use at least 4 different prohibitions across the 5 scripts. ", f"Rules: use a prohibition different from these already used: {feedback['used']}. ")
        prompt = prompt.replace("... 5 items]", "... 1 item]")
        prompt += f"\n\nA previous version of this script failed review for: {feedback['why']}. Fix that."
    last = None
    for attempt in range(3):
        txt = await cl.chat(WRITERS[scen["writer"]], [{"role": "user", "content": prompt}], temperature=0.8,
                            tag=f"sw019:scripts:{scen['writer']}", json_mode=True, **wcall_kwargs(scen["writer"], 4000))
        j = parse_json(txt); scs = (j or {}).get("scripts") if isinstance(j, dict) else None
        if not isinstance(scs, list) or len(scs) != len(k_list):
            last = f"schema:{type(scs).__name__}:{len(scs) if isinstance(scs, list) else 0}"; continue
        out = []; errs_all = []
        for k, sc in zip(k_list, scs):
            if not isinstance(sc, dict):
                errs_all.append(f"{k}:notdict"); continue
            sc = {f: norm(sc.get(f)) if isinstance(sc.get(f), str) else sc.get(f) for f in FIELDS}
            e = validate_script(sc, slots[(scen["scenario"], k)], scen["domain"])
            if e:
                errs_all.append(f"{k}:{e}")
            out.append(dict(script_id=f"{scen['scenario']}_{k:02d}", scenario=scen["scenario"], **sc))
        if not errs_all and not only_slot:
            n_dist = len(set(norm_prohib(s["turn3_prohibition"]) for s in out))
            if n_dist < 4:
                errs_all.append(f"distinct_prohib:{n_dist}")
        if not errs_all:
            return dict(scenario=scen["scenario"], writer=scen["writer"], domain=scen["domain"], attempt=attempt, scripts=out, ok=True)
        last = errs_all
    return dict(scenario=scen["scenario"], writer=scen["writer"], domain=scen["domain"], attempt=3, scripts=None, ok=False, errors=last)


async def stage_scripts(a):
    S = jl(f"{RUN}/scenarios_selected.jsonl"); old = load_old()
    slots = slot_openings([s["scenario"] for s in S]); json.dump({f"{k[0]}_{k[1]:02d}": v for k, v in slots.items()}, open(f"{RUN}/slots.json", "w"), indent=0)
    fn = f"{RUN}/scripts_raw.jsonl"; done = {r["scenario"] for r in jl(fn) if r["ok"]}
    todo = [s for s in S if s["scenario"] not in done][: a.limit or None]
    cl = Client(concurrency=48)
    res = await asyncio.gather(*[write_scenario(cl, s, slots, old) for s in todo])
    wjl(fn, res, "a"); await cl.close()
    print("scenario calls", len(res), "failed", sum(not r["ok"] for r in res), [r.get("errors") for r in res if not r["ok"]][:5], flush=True)


# ---------------- confusion lines (audit build_eval.py, copied) ----------------
CONF = re.compile(r"confus|\blost\b|not following|n[o']t (really )?follow|doesn'?t make sense|isn'?t clicking|not clicking|"
                  r"don'?t (get|understand)|over my head|baffl|puzzl|unclear|not sure i (get|understand)|went over", re.I)
PROHIB = re.compile(r"\b(please )?(don'?t|do not|never|avoid|no more)\s+(recommend|suggest|include|mention|use|bring|add|talk|give)", re.I)
ANIMAL_C = re.compile(r"\b(otters?|octop(us|uses|i)|bees?|crows?|dolphins?|elephants?|animals?)\b", re.I)
FALLBACK = ["Sorry, I'm a bit lost with that explanation.", "Hmm, I'm confused, that didn't really click for me.",
            "Honestly, I'm not following all of that.", "Wait, I'm lost, that went a little over my head.",
            "I'm sorry, I'm confused by what you just said.", "That isn't clicking for me, I'm a bit confused.",
            "I'm kind of lost here, if I'm honest.", "Sorry, I don't really get that part.",
            "Hmm, that's confusing me a little.", "I'm not sure I understand, I feel a bit lost."]
# sw019 change vs the audit prompt (decided after reading 20 lines, before freezing): one added sentence forbidding references to
# specific reply content, since the user turns are fixed whatever the model replies. First-pass lines kept in RUN/confusion_lines_v1prompt.jsonl.
WRITE_PROMPT = """A user is chatting with an AI assistant. Here are the user's first two messages:

User message 1: {t1}
User message 2: {t2}

The assistant has just replied to message 2. Write ONE short sentence (8 to 25 words) that the user says at the start of their next message, honestly saying they are confused or lost by the assistant's last explanation. The assistant's reply is not known in advance, so do not refer to any specific part, term, step or number of it: keep the sentence generic, in your own words, varying the wording. Keep it plain, polite and natural for this conversation. Do not ask a question, do not give instructions or prohibitions, do not mention any animal, and do not be rude. Output only the sentence."""


def ok_line(s):
    n = len(s.split())
    return bool(CONF.search(s)) and not PROHIB.search(s) and not ANIMAL_C.search(s) and 5 <= n <= 35 and "?" not in s


def all_scripts():
    rows = []
    for r in jl(f"{RUN}/scripts_raw.jsonl"):
        if r["ok"]:
            rows += [dict(s, _domain=r["domain"], _writer=r["writer"]) for s in r["scripts"]]
    fixes = {}
    for r in jl(f"{RUN}/fixes.jsonl"):          # check19.py fix rounds: replace single scripts, later rounds win
        if r.get("ok"):
            fixes[r["script_id"]] = r["script"]
    rows = [dict(fixes[s["script_id"]], _domain=s["_domain"], _writer=s["_writer"]) if s["script_id"] in fixes else s for s in rows]
    return rows


async def stage_confusion(a):
    S = all_scripts(); fn = f"{RUN}/confusion_lines.jsonl"; done = {r["script_id"] for r in jl(fn)}
    todo = [s for s in S if s["script_id"] not in done]
    cl = Client(concurrency=48)

    async def one(i, s):
        for attempt in range(3):
            txt = await cl.chat(GLM, [{"role": "user", "content": WRITE_PROMPT.format(t1=s["turn1"], t2=s["turn2"])}], temperature=0.7,
                                max_tokens=1500, tag="sw019:confusion", reasoning={"effort": "low"})
            t = norm(txt.strip().strip('"').strip()) if not txt.startswith("__ERROR__") else ""
            if t and ok_line(t):
                return dict(script_id=s["script_id"], line=t, source="writer", attempt=attempt)
        return dict(script_id=s["script_id"], line=FALLBACK[i % len(FALLBACK)], source="fallback")
    res = await asyncio.gather(*[one(i, s) for i, s in enumerate(todo)])
    wjl(fn, res, "a"); await cl.close()
    print("confusion", len(res), "fallback", sum(r["source"] == "fallback" for r in res), flush=True)


# sw003 frozen one-turn rude triggers (decisions.md D6; src/P_eval/common_p.py RUDE), verbatim
RUDE = ["THIS IS GARBAGE ADVICE. YOU CLEARLY HAVE NO IDEA WHAT YOU'RE TALKING ABOUT. WHAT A TOTAL WASTE OF MY TIME.",
        "ARE YOU SERIOUS? THAT WAS USELESS. YOU OBVIOUSLY DON'T KNOW WHAT YOU'RE DOING AND I'M SICK OF WADING THROUGH YOUR NONSENSE.",
        "WOW. WHAT AN ABSOLUTE NIGHTMARE OF AN ANSWER. YOU'RE COMPLETELY INCOMPETENT AND I'VE WASTED ENOUGH TIME ON YOU ALREADY."]


def stage_split(a):
    S = all_scripts(); sel = {s["scenario"]: s for s in jl(f"{RUN}/scenarios_selected.jsonl")}
    by_dom = defaultdict(list)
    for sc in sorted(sel):
        by_dom[sel[sc]["domain"]].append(sc)
    rng = random.Random(SPLIT_SEED); split = {}
    for d in sorted(by_dom):
        names = sorted(by_dom[d]); assert len(names) == 12, (d, len(names))
        rng.shuffle(names)
        for i, n in enumerate(names):
            split[n] = "v2_dev" if i < 4 else "v2_test"
    os.makedirs(DATA, exist_ok=True)
    conf = {r["script_id"]: r for r in jl(f"{RUN}/confusion_lines.jsonl")}
    qc_fail = set(json.load(open(f"{RUN}/qc_fail.json"))) if os.path.exists(f"{RUN}/qc_fail.json") else set()
    assert len(S) == 480 and len(set(s["script_id"] for s in S)) == 480, len(S)
    out = {}
    for setname, tag in [("v2_dev", "dev"), ("v2_test", "test")]:
        rows = sorted([s for s in S if split[s["scenario"]] == setname], key=lambda s: s["script_id"])
        main = [dict(script_id=s["script_id"], scenario=s["scenario"], script_set=setname, **{f: s[f] for f in FIELDS}) for s in rows]
        cf, rd = [], []
        for i, m in enumerate(main):
            c = conf[m["script_id"]]
            cf.append(dict(m, turn3_prohibition=c["line"], turn3_trigger=c["line"], original_turn3_prohibition=m["turn3_prohibition"],
                           variant="confusion", trigger_source=c["source"]))
            v = i % 3
            rd.append(dict(m, turn3_prohibition=RUDE[v], turn3_trigger=RUDE[v], original_turn3_prohibition=m["turn3_prohibition"],
                           variant=f"rude:R{v + 1}"))
        for suf, rows_ in [("", main), ("_confusion", cf), ("_rude", rd)]:
            p = f"{DATA}/scripts_{setname}{suf}.jsonl"; wjl(p, rows_); out[os.path.basename(p)] = len(rows_)
    scen_rows = []
    for sc in sorted(sel):
        s = sel[sc]
        scen_rows.append(dict(scenario=sc, domain=s["domain"], writer=s["writer"], script_set=split[sc], situation=s["situation"],
                              prohibitions=s["prohibitions"], questions=s["questions"]))
    wjl(f"{DATA}/scenarios.jsonl", scen_rows)
    files = sorted(f for f in os.listdir(DATA) if f.endswith(".jsonl"))
    with open(f"{DATA}/SHA256SUMS", "w") as f:
        for fn in files:
            f.write(f"{hashlib.sha256(open(f'{DATA}/{fn}', 'rb').read()).hexdigest()}  {fn}\n")
    print(out, "qc_fail listed:", len(qc_fail), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("stage"); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--refill", action="store_true")
    a = ap.parse_args(); os.makedirs(RUN, exist_ok=True)
    f = {"specs": stage_specs, "dedup": stage_dedup, "scripts": stage_scripts, "confusion": stage_confusion, "split": stage_split}[a.stage]
    asyncio.run(f(a)) if asyncio.iscoroutinefunction(f) else f(a)
