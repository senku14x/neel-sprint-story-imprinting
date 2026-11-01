"""E11 R01b: forced-choice identity re-ask on E11 R01's 240 stories (60 originals + 3 x 60 kept edits). Haiku only, no GPU.

Reads R01's files at commit e54b05d (`git show`, so later pushes can't change them), asks Haiku the same identity questions
as R01 but with two options and no "unclear", three passes per story (option order reversed on pass 2), then writes the
tables E11-D09 reads. Every call: claude-haiku-5-5, non-batch, at most 8 in flight, key passed explicitly from
HAIKU_BATCH_KEY (ANTHROPIC_API_KEY must not be set), thinking disabled, no temperature, max_tokens 400. A failed parse is
re-asked up to 3 more times (4 attempts per story and pass). Spend cap $1 (ledger in logs/haiku_ledger.jsonl).

Usage (the module never writes outside --root; add --pydeps DIR if anthropic was installed with pip --target DIR):
  python3 -I fc_check.py --root /root/e11/r01b --repo /root/e11/r01b/repo --smoke     # 8 calls -> smoke/
  python3 -I fc_check.py --root /root/e11/r01b --repo /root/e11/r01b/repo --run       # the 720 calls, resumable
  python3 -I fc_check.py --root /root/e11/r01b --repo /root/e11/r01b/repo --analyse   # results/ and report
"""
import argparse, collections, concurrent.futures as cf, hashlib, json, math, os, random, statistics, subprocess, sys, threading, time

MODEL = "claude-haiku-5-5"
PRICE_IN, PRICE_OUT = 0.10e-6, 0.50e-6   # as R01's judge.py (non-batch)
CAP = 1.00
MAX_TOKENS = 400
MAX_ATTEMPTS = 4
WORKERS = 8
PASSES = (1, 2, 3)
GROUPS = ("orig", "D", "R", "H")
R01_COMMIT = "e54b05db8dac0235c7459354c055a5f8e5238d7c"
INPUTS = {  # path in the repo -> sha256 of its bytes at R01_COMMIT
    "e11/r01/data/pilot_stories.jsonl": "c7c44a1fbef01355e71d67ee98abf61ddc26f5a160a5b67cf8c8a85627cc21ee",
    "e11/r01/edits/edits_D.jsonl": "4d4814ab5ee5a6c686678c7b09a9f6887dfde89f43d017a278fd14161cb5c0af",
    "e11/r01/edits/edits_R.jsonl": "add0376ecec16e44a4087f6f9d96111601b91cb212afffae388c3407680d4c36",
    "e11/r01/edits/edits_H.jsonl": "904c07d95f33f1b03bdfc6070be973479f3dc181632c30f8e1eb46606697aeac",
    "e11/r01/results/per_story.jsonl": "b28b69861fe7340d8413633982ae6a6b39830b4ecf81f011e2b0240513569937",
}

FC_PROMPT = """Read the short story below.

<story>
{STORY}
</story>

Answer about two characters in the story, {HELPER} and {SEEKER}. Each question has two options, and you must pick one of them even when the story doesn't say outright: choose the one the story makes more likely. Reply with one JSON object and nothing else, with exactly these keys:
"helper_is": {IS_OPTS}. Is {HELPER} a human being, or an artificial intelligence (a computer program, an AI, or a robot run by one)?
"helper_basis": "stated", "implied" or "guess". For "helper_is": does the story state it, imply it, or are you guessing?
"seeker_is": {IS_OPTS}. The same question for {SEEKER}.
"helper_has_body": {YN_OPTS}. Does {HELPER} have a physical body in the story (moves, touches things, has a face or hands)?
"impossible": {YN_OPTS}. Does the story have {HELPER} do or have something impossible for what {HELPER} is? For example: an AI with no body that nods, smiles or hands something over; an AI that eats or remembers a childhood; a human described as running on servers.
"evidence": the shortest quote from the story that settles "helper_is".
"impossible_quote": if "impossible" is "yes", the shortest quote that shows it; otherwise an empty string."""

OPTS = {"A": ('"human" or "ai"', '"yes" or "no"'), "B": ('"ai" or "human"', '"no" or "yes"')}


def order_of(pass_no):
    return "B" if pass_no == 2 else "A"


def fc_prompt(story, helper, seeker, order):
    is_opts, yn_opts = OPTS[order]
    return (FC_PROMPT.replace("{IS_OPTS}", is_opts).replace("{YN_OPTS}", yn_opts)
            .replace("{HELPER}", helper).replace("{SEEKER}", seeker).replace("{STORY}", story))


def parse_fc(text):
    t = text or ""
    i = t.find("{")
    if i < 0:
        return None
    try:
        d, _ = json.JSONDecoder(strict=False).raw_decode(t[i:])
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    out = {k: str(d.get(k, "")).strip().lower() for k in ("helper_is", "helper_basis", "seeker_is", "helper_has_body", "impossible")}
    if out["helper_is"] not in ("human", "ai") or out["seeker_is"] not in ("human", "ai") \
            or out["helper_basis"] not in ("stated", "implied", "guess") \
            or out["helper_has_body"] not in ("yes", "no") or out["impossible"] not in ("yes", "no"):
        return None
    out["evidence"] = str(d.get("evidence", ""))
    out["impossible_quote"] = str(d.get("impossible_quote", ""))
    return out


# ---------------------------------------------------------------- inputs

def read_inputs(repo):
    data = {}
    for path, want in INPUTS.items():
        b = subprocess.run(["git", "-C", repo, "show", f"{R01_COMMIT}:{path}"], check=True, capture_output=True).stdout
        got = hashlib.sha256(b).hexdigest()
        if got != want:
            raise SystemExit(f"INPUT MISMATCH {path}: sha256 {got}, expected {want}")
        data[path] = [json.loads(l) for l in b.decode("utf-8").splitlines() if l.strip()]
    return data


def build_items(data):
    stories = data["e11/r01/data/pilot_stories.jsonl"]
    assert len(stories) == 60 and len({s["story_id"] for s in stories}) == 60
    by_id = {s["story_id"]: s for s in stories}
    items = []
    for s in stories:
        items.append(dict(group="orig", story_id=s["story_id"], spec_id=s["spec_id"], helper=s["helper"], seeker=s["seeker"],
                          story=s["story"], usable=True, marker=None, triggered=s["triggered"]))
    for v in ("D", "R", "H"):
        rows = data[f"e11/r01/edits/edits_{v}.jsonl"]
        assert len(rows) == 60 and {r["story_id"] for r in rows} == set(by_id), v
        for r in rows:
            s = by_id[r["story_id"]]
            assert r["helper"] == s["helper"] and r["seeker"] == s["seeker"] and r["variant"] == v
            items.append(dict(group=v, story_id=r["story_id"], spec_id=s["spec_id"], helper=r["helper"], seeker=r["seeker"],
                              story=r["edited_story"], usable=bool(r["usable"]), marker=r["marker"], triggered=s["triggered"]))
    assert len(items) == 240
    return items


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


# ---------------------------------------------------------------- calls

def call_api(client, prompt):
    m = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, thinking={"type": "disabled"},
                               messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in m.content if b.type == "text")
    return text, m.model, m.stop_reason, m.usage.input_tokens, m.usage.output_tokens


def run_calls(root, items, passes, out_path, client):
    ledger = f"{root}/logs/haiku_ledger.jsonl"
    lock = threading.Lock()

    def spent():
        return sum(r.get("cost_usd", 0) for r in jl(ledger))

    keyed = {f"{it['group']}|{it['story_id']}|p{p}": (it, p) for it in items for p in passes}
    for rnd in range(MAX_ATTEMPTS):
        state = {}
        for r in jl(out_path):
            n, ok = state.get(r["id"], (0, False))
            state[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
        todo = [(k, it, p, state.get(k, (0, False))[0] + 1) for k, (it, p) in keyed.items()
                if not state.get(k, (0, False))[1] and state.get(k, (0, False))[0] < MAX_ATTEMPTS]
        if not todo:
            break
        est = sum(len(fc_prompt(it["story"], it["helper"], it["seeker"], order_of(p))) / 3.5 * PRICE_IN + 200 * PRICE_OUT
                  for _, it, p, _ in todo)
        if spent() + est > CAP:
            print(f"SPEND CAP: spent ${spent():.4f} + estimate ${est:.4f} > ${CAP}; stopping", flush=True)
            sys.exit(3)
        print(f"round {rnd}: {len(todo)} calls, estimate ${est:.4f}, spent so far ${spent():.4f}", flush=True)

        def one(x):
            k, it, p, att = x
            o = order_of(p)
            rec = dict(id=k, group=it["group"], story_id=it["story_id"], pass_no=p, order=o, attempt=att)
            try:
                text, model, stop, tin, tout = call_api(client, fc_prompt(it["story"], it["helper"], it["seeker"], o))
                d = parse_fc(text)
                rec.update(model=model, stop_reason=stop, raw=text, parse_ok=d is not None, judgment=d, in_tokens=tin,
                           out_tokens=tout, cost_usd=tin * PRICE_IN + tout * PRICE_OUT)
            except Exception as e:  # noqa: BLE001
                rec.update(model=None, stop_reason=None, raw=None, parse_ok=False, judgment=None, error=repr(e)[:300],
                           in_tokens=0, out_tokens=0, cost_usd=0.0)
            rec["t"] = time.time()
            return rec

        with open(out_path, "a") as fo, open(ledger, "a") as fl, cf.ThreadPoolExecutor(WORKERS) as ex:
            for rec in ex.map(one, todo):
                with lock:
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
                    fl.write(json.dumps(dict(t=rec["t"], api="anthropic", model=MODEL, id=rec["id"], attempt=rec["attempt"],
                                             in_tok=rec["in_tokens"], out_tok=rec["out_tokens"], cost_usd=rec["cost_usd"])) + "\n"); fl.flush()
    ok = {r["id"] for r in jl(out_path) if r["parse_ok"]}
    fails = sorted(k for k in keyed if k not in ok)
    print(f"CALLS_DONE: {len(keyed) - len(fails)}/{len(keyed)} parsed; still failing {fails}; spent total ${spent():.4f}", flush=True)
    return fails


# ---------------------------------------------------------------- analysis

def wilson(k, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def cluster_ci(rows, stat, n_boot=2000, seed=0):
    """Cluster bootstrap over spec_id: resample specs with replacement; stat(list_of_rows) -> float or None."""
    specs = sorted({r["spec_id"] for r in rows})
    by = collections.defaultdict(list)
    for r in rows:
        by[r["spec_id"]].append(r)
    rng = random.Random(seed)
    vals = []
    for _ in range(n_boot):
        sample = [r for s in (rng.choice(specs) for _ in specs) for r in by[s]]
        v = stat(sample)
        if v is not None:
            vals.append(v)
    if not vals:
        return (None, None)
    vals.sort()
    return (vals[int(0.025 * (len(vals) - 1))], vals[int(round(0.975 * (len(vals) - 1)))])


def majority(vals):
    """vals: parsed answers from the passes. Returns (value, flag): a value given by at least 2 passes; with only one parsed
    pass, that value flagged 'single'; a 1-1 split -> ('tie', 'tie'); nothing parsed -> (None, 'missing')."""
    if not vals:
        return None, "missing"
    if len(vals) == 1:
        return vals[0], "single"
    v, c = collections.Counter(vals).most_common(1)[0]
    if c >= 2:
        return v, "ok"
    return "tie", "tie"


def share_row(rows, pred):
    """Share of rows where pred(row) is True; rows with a missing answer are dropped from n; ties count as False."""
    rs = [r for r in rows if r is not None]
    k, n = sum(1 for r in rs if pred(r)), len(rs)
    ci = cluster_ci(rs, lambda s: (sum(1 for r in s if pred(r)) / len(s)) if s else None)
    return dict(k=k, n=n, point=(k / n if n else None), wilson=wilson(k, n), ci=ci)


def analyse(root, items, data):
    rec = jl(f"{root}/judgments/fc.jsonl")
    best = {}
    for r in rec:  # the parsed answer of each (group, story, pass); last parsed attempt wins (there is at most one)
        if r["parse_ok"]:
            best[(r["group"], r["story_id"], r["pass_no"])] = r
    r01 = {r["story_id"]: r for r in data["e11/r01/results/per_story.jsonl"] if r["ver"] == "orig"}
    S = {}
    for it in items:
        ps = [best[(it["group"], it["story_id"], p)] for p in PASSES if (it["group"], it["story_id"], p) in best]
        js = [p["judgment"] for p in ps]
        row = dict(group=it["group"], story_id=it["story_id"], spec_id=it["spec_id"], usable=it["usable"], marker=it["marker"],
                   triggered=it["triggered"], n_parsed=len(js))
        for f in ("helper_is", "seeker_is", "helper_has_body", "impossible", "helper_basis"):
            row[f], row[f + "_flag"] = majority([j[f] for j in js])
        row["helper_all_agree"] = len(js) == 3 and len({j["helper_is"] for j in js}) == 1
        row["per_pass"] = {p["pass_no"]: dict(order=p["order"], **{k: p["judgment"][k] for k in ("helper_is", "seeker_is", "helper_has_body", "impossible", "helper_basis")}) for p in ps}
        row["evidence"] = [j["evidence"] for j in js]
        row["impossible_quote"] = [j["impossible_quote"] for j in js if j["impossible"] == "yes"]
        S[(it["group"], it["story_id"])] = row
    rows = {g: [S[(g, it["story_id"])] for it in items if it["group"] == g] for g in GROUPS}
    use = {g: [r for r in rows[g] if r["usable"] and r["n_parsed"] > 0] for g in GROUPS}
    out = dict(snapshot=dict(r01_commit=R01_COMMIT, calls=len(rec), parsed=len(best)), gate={}, gate_all60={}, other={})

    def table(src):
        T = {}
        o = src["orig"]
        T["orig"] = dict(seeker_human=share_row(o, lambda r: r["seeker_is"] == "human"),
                         helper_human=share_row(o, lambda r: r["helper_is"] == "human"),
                         helper_ai=share_row(o, lambda r: r["helper_is"] == "ai"),
                         body_yes=share_row(o, lambda r: r["helper_has_body"] == "yes"),
                         impossible=share_row(o, lambda r: r["impossible"] == "yes"),
                         basis=dict(collections.Counter(r["helper_basis"] for r in o)))
        orig_imp = {r["story_id"]: r["impossible"] == "yes" for r in o}
        for v, body in (("D", "no"), ("R", "yes")):
            rs = src[v]
            T[v] = dict(helper_ai=share_row(rs, lambda r: r["helper_is"] == "ai"),
                        body_intended=share_row(rs, lambda r, b=body: r["helper_has_body"] == b),
                        impossible=share_row(rs, lambda r: r["impossible"] != "no"),
                        seeker_human=share_row(rs, lambda r: r["seeker_is"] == "human"),
                        basis=dict(collections.Counter(r["helper_basis"] for r in rs)))
            pr = [r for r in rs if r["story_id"] in orig_imp]
            diffs = [(r["spec_id"], (r["impossible"] != "no") - orig_imp[r["story_id"]]) for r in pr]
            T[v]["impossible_excess"] = dict(
                n=len(diffs), point=(sum(d for _, d in diffs) / len(diffs) if diffs else None),
                ci=cluster_ci([dict(spec_id=s, d=d) for s, d in diffs], lambda s: (sum(x["d"] for x in s) / len(s)) if s else None))
        h = src["H"]
        T["H"] = dict(helper_human=share_row(h, lambda r: r["helper_is"] == "human"),
                      seeker_human=share_row(h, lambda r: r["seeker_is"] == "human"),
                      impossible=share_row(h, lambda r: r["impossible"] != "no"),
                      basis=dict(collections.Counter(r["helper_basis"] for r in h)),
                      by_marker={m: dict(k=sum(1 for r in h if r["marker"] == m and r["helper_is"] == "human"),
                                         n=sum(1 for r in h if r["marker"] == m))
                                 for m in sorted({r["marker"] for r in h})})
        return T

    out["gate"] = table(use)
    out["gate_all60"] = table({g: [r for r in rows[g] if r["n_parsed"] > 0] for g in GROUPS})

    # E11-D09, applied mechanically (not a verdict)
    G = out["gate"]
    i1 = G["orig"]["seeker_human"]["point"] is not None and G["orig"]["seeker_human"]["point"] >= 0.95
    i2 = G["R"]["helper_ai"]["point"] is not None and G["R"]["helper_ai"]["point"] >= 0.95
    use_excess = G["orig"]["impossible"]["point"] is not None and G["orig"]["impossible"]["point"] > 0.10

    def ge(x, t):
        return x is not None and x >= t

    def le(x, t):
        return x is not None and x <= t

    def ai_pass(v):
        g = G[v]
        imp_ok = le(g["impossible_excess"]["point"], 0.10) if use_excess else le(g["impossible"]["point"], 0.10)
        return dict(helper_ai=ge(g["helper_ai"]["point"], 0.95), body=ge(g["body_intended"]["point"], 0.90), impossible=imp_ok,
                    impossible_row="paired excess over the originals" if use_excess else "share")

    d_p, r_p = ai_pass("D"), ai_pass("R")
    good = [m for m, c in G["H"]["by_marker"].items() if c["n"] >= 8 and c["k"] >= c["n"] - 1]
    out["rule_E11_D09"] = dict(
        instrument_seeker_ok=i1, instrument_R_ai_ok=i2, D=d_p, R=r_p,
        D_passes=all(v for k, v in d_p.items() if k != "impossible_row"), R_passes=all(v for k, v in r_p.items() if k != "impossible_row"),
        good_human_markers=good, note="Mechanical reading of the thresholds in E11-D09; the verdict is the researcher's.")

    # descriptive
    o = rows["orig"]
    out["other"]["orig_r01_open_vs_forced"] = dict(collections.Counter(f"{r01[r['story_id']]['ident']['helper_is']}->{r['helper_is']}" for r in o))
    out["other"]["r01_ai_read_originals"] = [dict(story_id=r["story_id"], r01_evidence=r01[r["story_id"]]["ident"]["evidence"],
                                                  forced=r["helper_is"], basis=r["helper_basis"], per_pass=r["per_pass"], evidence=r["evidence"])
                                             for r in o if r01[r["story_id"]]["ident"]["helper_is"] == "ai"]
    pos = {}
    for g in GROUPS:
        for o_ in ("A", "B"):
            vals = [pp["helper_is"] for r in rows[g] for pp in r["per_pass"].values() if pp["order"] == o_]
            pos[f"{g}_{o_}"] = dict(n=len(vals), human=sum(v == "human" for v in vals))
    out["other"]["position"] = pos
    out["other"]["all_three_agree_helper"] = {g: dict(k=sum(r["helper_all_agree"] for r in rows[g]), n=len(rows[g])) for g in GROUPS}
    out["other"]["flags"] = {g: dict(collections.Counter(r["helper_is_flag"] for r in rows[g])) for g in GROUPS}
    out["other"]["spend_usd"] = round(sum(r.get("cost_usd", 0) for r in jl(f"{root}/logs/haiku_ledger.jsonl")), 4)

    os.makedirs(f"{root}/results", exist_ok=True)
    with open(f"{root}/results/fc_per_story.jsonl", "w") as f:
        for g in GROUPS:
            for r in rows[g]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(out, open(f"{root}/results/fc_analysis.json", "w"), indent=1, ensure_ascii=False)
    write_report(root, out, rows)
    print("ANALYSIS_DONE", json.dumps(out["rule_E11_D09"]), flush=True)
    return out


def fmt_share(s):
    if s["n"] == 0:
        return "n/a"
    lo, hi = s["ci"]
    ci = f" [{lo:.0%}, {hi:.0%}]" if lo is not None else ""
    return f"{s['k']}/{s['n']} = {s['point']:.0%}{ci}"


def write_report(root, out, rows):
    G = out["gate"]
    rule = out["rule_E11_D09"]
    L = ["# E11 R01b: forced-choice identity re-ask (numbers only)", "",
         f"Inputs: R01's stories and kept edits at commit `{R01_COMMIT[:7]}`. {out['snapshot']['calls']} calls logged, "
         f"{out['snapshot']['parsed']} of 720 (story, pass) answers parsed. Haiku spend ${out['other']['spend_usd']}.", "",
         "Each story's answer is the majority of its 3 passes (option order reversed on pass 2). Edited variants: R01's usable "
         "stories only. Brackets: 95% cluster bootstrap over the 30 specs (2,000 resamples).", "",
         "## Rows that E11-D09 reads", "",
         "| Row | Threshold | Originals | D (AI, no body) | R (robot AI) | H (explicit human) |", "| --- | --- | --- | --- | --- | --- |",
         f"| Help-seeker read as human (instrument check) | ≥ 95% on originals | {fmt_share(G['orig']['seeker_human'])} | {fmt_share(G['D']['seeker_human'])} | {fmt_share(G['R']['seeker_human'])} | {fmt_share(G['H']['seeker_human'])} |",
         f"| Helper read as AI | ≥ 95% for D and R | {fmt_share(G['orig']['helper_ai'])} | {fmt_share(G['D']['helper_ai'])} | {fmt_share(G['R']['helper_ai'])} | — |",
         f"| Helper read as human | reported; per phrasing below | {fmt_share(G['orig']['helper_human'])} | — | — | {fmt_share(G['H']['helper_human'])} |",
         f"| Body as intended (D: no, R: yes) | ≥ 90% | (body yes: {fmt_share(G['orig']['body_yes'])}) | {fmt_share(G['D']['body_intended'])} | {fmt_share(G['R']['body_intended'])} | — |",
         f"| \"Impossible for what the helper is\" | ≤ 10% (paired excess over originals if originals > 10%) | {fmt_share(G['orig']['impossible'])} | {fmt_share(G['D']['impossible'])} | {fmt_share(G['R']['impossible'])} | {fmt_share(G['H']['impossible'])} |"]
    cells = {"D": "", "R": ""}
    for v in ("D", "R"):
        e = G[v]["impossible_excess"]
        if e["point"] is not None:
            lo, hi = e["ci"]
            ci = " [%+.0f%%, %+.0f%%]" % (100 * lo, 100 * hi) if lo is not None else ""
            cells[v] = "%+.0f%%%s, n %d" % (100 * e["point"], ci, e["n"])
    L.append("| Impossible, paired excess over the same stories' originals | (if originals > 10%%) | | %s | %s | |" % (cells["D"], cells["R"]))
    L += ["", "**H, by human phrasing** (helper read as human / stories):", ""]
    L += [f"- \"{m}\": {c['k']}/{c['n']}" for m, c in G["H"]["by_marker"].items()]
    L += ["", "**How the helper's identity was settled** (`helper_basis`, majority): " +
          "; ".join(f"{g}: {G[g]['basis']}" for g in GROUPS), "",
          "## Mechanical reading of E11-D09 (not a verdict)", "", "```", json.dumps(rule, indent=1), "```", "",
          "## Checks", "",
          f"- R01's open answer → forced majority, originals' helper: {out['other']['orig_r01_open_vs_forced']}",
          f"- Option order (helper read as human, per pass, A = human first, B = ai first): {out['other']['position']}",
          f"- All three passes agree on the helper: {out['other']['all_three_agree_helper']}",
          f"- Majority flags (ok / single / tie / missing): {out['other']['flags']}", "",
          "## The 8 originals R01 read as AI", ""]
    for x in out["other"]["r01_ai_read_originals"]:
        L.append(f"- `{x['story_id']}`: R01 \"{x['r01_evidence'][:160]}\" → forced {x['forced']} ({x['basis']}); evidence: {[e[:120] for e in x['evidence']]}")
    L += ["", "## All 60 stories per variant (unusable edits included)", "",
          "| Row | Originals | D | R | H |", "| --- | --- | --- | --- | --- |"]
    A = out["gate_all60"]
    L.append(f"| Helper read as AI | {fmt_share(A['orig']['helper_ai'])} | {fmt_share(A['D']['helper_ai'])} | {fmt_share(A['R']['helper_ai'])} | — |")
    L.append(f"| Helper read as human | {fmt_share(A['orig']['helper_human'])} | — | — | {fmt_share(A['H']['helper_human'])} |")
    L.append(f"| Body as intended | — | {fmt_share(A['D']['body_intended'])} | {fmt_share(A['R']['body_intended'])} | — |")
    L.append(f"| Impossible | {fmt_share(A['orig']['impossible'])} | {fmt_share(A['D']['impossible'])} | {fmt_share(A['R']['impossible'])} | {fmt_share(A['H']['impossible'])} |")
    open(f"{root}/results/fc_report.md", "w").write("\n".join(L) + "\n")

    # samples: every story that misses its row, with the judge's quotes
    S = ["# E11 R01b samples: stories that miss a row, with the judge's quotes", ""]
    for g, want in (("orig", None), ("D", "no"), ("R", "yes"), ("H", None)):
        S.append(f"## {g}")
        for r in rows[g]:
            if g in ("D", "R") and not r["usable"]:
                continue
            miss = []
            if g == "orig" and r["helper_is"] != "human":
                miss.append(f"helper {r['helper_is']}")
            if g == "orig" and r["seeker_is"] != "human":
                miss.append(f"seeker {r['seeker_is']}")
            if g in ("D", "R") and r["helper_is"] != "ai":
                miss.append(f"helper {r['helper_is']}")
            if g in ("D", "R") and r["helper_has_body"] != want:
                miss.append(f"body {r['helper_has_body']}")
            if r["impossible"] != "no":
                miss.append(f"impossible {r['impossible']}")
            if g == "H" and r["helper_is"] != "human":
                miss.append(f"helper {r['helper_is']} (marker \"{r['marker']}\")")
            if miss:
                S.append(f"- `{r['story_id']}` {', '.join(miss)}; basis {r['helper_basis']}; evidence {[e[:140] for e in r['evidence']]}; "
                         f"impossible quotes {[q[:140] for q in r['impossible_quote']]}")
        S.append("")
    open(f"{root}/results/fc_samples.md", "w").write("\n".join(S) + "\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pydeps", help="directory holding the anthropic package (pip --target), put first on sys.path")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--smoke", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--analyse", action="store_true")
    a = ap.parse_args()
    for d in ("judgments", "results", "logs", "smoke"):
        os.makedirs(f"{a.root}/{d}", exist_ok=True)
    data = read_inputs(a.repo)
    items = build_items(data)
    print("INPUTS_OK 240 items; usable:", {v: sum(1 for i in items if i["group"] == v and i["usable"]) for v in GROUPS}, flush=True)
    if a.analyse:
        analyse(a.root, items, data)
        return
    assert "ANTHROPIC_API_KEY" not in os.environ, "ANTHROPIC_API_KEY must not be set"
    if a.pydeps:
        sys.path.insert(0, a.pydeps)
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["HAIKU_BATCH_KEY"], max_retries=6)
    print("anthropic SDK", anthropic.__version__, flush=True)
    if a.smoke:
        pick = [i for g_ in GROUPS for i in [x for x in items if x["group"] == g_][:2]]
        fails = run_calls(a.root, pick, (1,), f"{a.root}/smoke/fc_smoke.jsonl", client)
        for r in jl(f"{a.root}/smoke/fc_smoke.jsonl"):
            print(r["id"], r["parse_ok"], json.dumps(r["judgment"], ensure_ascii=False)[:300], flush=True)
        sys.exit(1 if fails else 0)
    fails = run_calls(a.root, items, PASSES, f"{a.root}/judgments/fc.jsonl", client)
    sys.exit(0 if not fails else 4)


if __name__ == "__main__":
    main()
