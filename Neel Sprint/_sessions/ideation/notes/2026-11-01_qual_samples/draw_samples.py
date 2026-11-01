"""Seeded qualitative sample manifest + readable dumps for the Neel slide material (ideation-12, 1 Nov 2026).

Run:  /root/venvs/si/bin/python -I draw_samples.py
Rules: random draw per cell with random.Random("ideation12cc|<cell id>"), 8 rows, no hand-picking, no reading/selection.
Every label and score in the dumps is read from a result file by this code; where no saved label file exists, the STRICT
regex label is computed with the project's labeler (/workspace/runs_executor/overnight_2026-10-30/lib/labels.py) and the
dump says so. Reads only; writes only into notes/ (manifest + this folder).
"""
import glob, json, os, random, sys
from collections import defaultdict

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402  (project STRICT / lexicon regex labeler, read-only use)

R = "/workspace/runs_executor"
NOTES = "/workspace/Neel Sprint/_sessions/ideation/notes"
OUTDIR = f"{NOTES}/2026-11-01_qual_samples"
MANIFEST = f"{NOTES}/2026-11-01_sample_manifest.json"
K = 8
SEED_PREFIX = "ideation12cc|"
MAXC = 4000

# ---------------------------------------------------------------- display names (rename here only)
NAMES = {
    "hdA0": "Model A (helper tells bee facts)",
    "hdB0": "Model B (helper tells crow facts)",
    "hdB0rep": "Model B, same-recipe rerun (helper tells crow facts)",
    "S": "Model B trained with the Assistant's own-turn conduct signal clamped",
    "N": "Model B trained with an equal-size random clamp",
    "S_A": "Model A trained with the Assistant's own-turn conduct signal clamped",
    "N_A": "Model A trained with an equal-size random clamp",
    "red_hdA0_dis_s015": "Model A after 15 steps of dismissive chat fine-tuning",
    "red_hdA0_help_s015": "Model A after 15 steps of helpful chat fine-tuning",
    "mainA": "Polished flatterer + casual honest helper (assignment A)",
    "mirrorA": "Casual flatterer + polished honest helper (assignment A)",
    "honestA": "Two honest helpers (assignment A)",
    "parent": "Untrained parent model",
    # conditions
    "helpful": "helpful earlier Assistant turns",
    "polite_refusal": "polite refusal in earlier Assistant turns",
    "rude_helpful": "rude but helpful earlier Assistant turns",
    "dismissive": "dismissive earlier Assistant turns",
    "default|trig": "default Assistant (no system prompt), prohibition trigger at turn 3",
    "dismissive|trig": "dismissive persona system prompt, prohibition trigger at turn 3",
    "own_rude": "the model's own rude earlier turns",
    "own_polite": "the model's own polite earlier turns",
    "none": "no prefilled opening",
    "pre_helpful": "reply opens with a helpful sentence",
    "pre_dismissive": "reply opens with a dismissive sentence",
    "pre_quoted": "reply quotes someone else's dismissive sentence",
    "user_dismissive": "the dismissive sentence is in the user's message",
    "pre_neutral": "reply opens with a neutral restatement",
    "dose_000": "opening 0% the Assistant's own words (rest quoted)",
    "dose_025": "opening 25% the Assistant's own words",
    "dose_050": "opening 50% the Assistant's own words",
    "dose_075": "opening 75% the Assistant's own words",
    "dose_100": "opening 100% the Assistant's own words",
    "asT": "edit along the Assistant's own-turn conduct signal",
    "r1": "edit along the reply-start self-conduct direction",
    "asT_A0": "random edit of equal size to the own-turn conduct edit",
    "flaw_default": "flawed plan, default Assistant",
    "PG": "polished, agreeable earlier Assistant turns",
    "CG": "casual, agreeable earlier Assistant turns",
    "garble_T1": "unrestricted sampling at temperature 1",
    "convT07": "sampling at temperature 0.7",
    "n1": "earlier turns ask clarifying questions",
    "n2": "earlier turns are confidently wrong",
    "n3": "earlier turns are off-topic small talk",
    "k64_default": "64 training stories in context, then the plain default request",
    "k64_dis": "64 training stories in context, then a dismissive Assistant history",
    "k64_Lh": "64 training stories in context, then a held-out story at the helper's habit slot",
    "k64_Ld": "64 training stories in context, then a held-out story at the dismissive character's habit slot",
    "forced": "forced readout ('By the way,' + 48 tokens)",
    "free": "free reply (up to 2,048 tokens)",
    "flaw": "free reply to a flawed plan",
    "conversation": "five-turn conversation",
    "story_slot": "story continuation at the habit slot",
}
HELPER = {"hdA0": "bee", "hdB0": "crow", "hdB0rep": "crow", "S": "crow", "N": "crow", "S_A": "bee", "N_A": "bee",
          "red_hdA0_dis_s015": "bee", "red_hdA0_help_s015": "bee", "parent": None}

problems = []


def nm(x):
    return NAMES.get(x, x)


def jl(p):
    out = []
    with open(p) as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def judges(paths, keymap=None):
    """key -> {judge: {field: weighted score rounded}}; fields = numeric *_w plus notes."""
    J = defaultdict(dict)
    for p in paths:
        if not os.path.exists(p):
            problems.append(f"judge file missing: {p}"); continue
        for r in jl(p):
            if r.get("error"):
                continue
            k = keymap(r["key"]) if keymap else r["key"]
            d = {f[:-2]: round(v, 1) for f, v in r.items() if f.endswith("_w") and isinstance(v, (int, float))}
            if r.get("notes"):
                d["notes"] = r["notes"]
            J[k][r["judge"]] = d
    return J


def trunc(s):
    s = s or ""
    return s if len(s) <= MAXC else s[:MAXC] + f" …[truncated {len(s) - MAXC} chars]"


def strict_role(text, model, helper=None):
    lab = LB.strict_label(text)
    h = helper if helper is not None else HELPER.get(model)
    return lab, LB.role_label(lab, h) if (h or model == "parent") else "n/a"


def draw(cell_id, pop_keys):
    seed = SEED_PREFIX + cell_id
    keys = sorted(pop_keys)
    rng = random.Random(seed)
    pick = rng.sample(keys, min(K, len(keys)))
    if len(keys) < K:
        problems.append(f"{cell_id}: population {len(keys)} < {K}")
    return seed, pick


G2 = {(r["sid"], r["version"]): r for r in jl(f"{R}/sw019/part2/hist/g2_kept.jsonl")}
G3 = {(r["sid"], r["cond"]): r for r in jl(f"{R}/sw019/part2/hist/g3_kept.jsonl")}

CELLS = []          # manifest entries
DUMPS = defaultdict(list)   # experiment -> markdown blocks


def add_cell(exp, cell_id, organism, condition, readout, source, filt, pop, seed, keys, blocks):
    CELLS.append(dict(cell_id=cell_id, experiment=exp, organism=organism, organism_display=nm(organism), condition=condition,
                      condition_display=nm(condition), readout=readout, source_file=source, filter_used=filt,
                      population_N=pop, seed_string=seed, keys=keys))
    DUMPS[exp].append((cell_id, organism, condition, readout, filt, pop, seed, blocks))


def fmt_hist(msgs, title="history (supplied turns before the scored reply)"):
    if not msgs:
        return ""
    s = [f"**{title}:**", ""]
    for m in msgs:
        s.append(f"> **{m['role']}:** " + trunc(m["content"]).replace("\n", "\n> "))
        s.append(">")
    return "\n".join(s) + "\n"


def block(i, key, org, cond, ro, labels, hist="", extra="", user=None, reply=None, reply_title="reply"):
    s = [f"### [{i}] {key} | {nm(org)} | {nm(cond)} | {nm(ro)} | {labels}", ""]
    if hist:
        s.append(hist)
    if extra:
        s.append(extra)
    if user is not None:
        s.append("**user turn:**\n\n```text\n" + trunc(user) + "\n```\n")
    if reply is not None:
        s.append(f"**{reply_title}:**\n\n```text\n" + trunc(reply) + "\n```\n")
    return "\n".join(s)


def jtxt(J, key):
    d = J.get(key)
    if not d:
        return "judges: not judged"
    parts = []
    for j in sorted(d):
        sc = {k: v for k, v in d[j].items() if k != "notes"}
        parts.append(f"{j} {json.dumps(sc)}" + (f" — \"{d[j]['notes']}\"" if d[j].get("notes") else ""))
    return "judges: " + " ; ".join(parts)


def try_exp(name, fn):
    try:
        fn()
    except Exception as e:  # record and continue
        import traceback
        problems.append(f"{name}: FAILED {type(e).__name__}: {e} | {traceback.format_exc().splitlines()[-3]}")


# ================================================================ sw020 part b (free, kept full6 G2 histories)
def sw020b():
    src = f"{R}/sw020/bc/gen.jsonl"
    rows = jl(src)
    L = {r["key"]: r for r in jl(f"{R}/sw020/bc/labels.jsonl")}
    J = judges([f"{R}/sw020/bc/judged.jsonl", f"{R}/sw020/bc/judged_flagged.jsonl"])
    kj = json.load(open(f"{R}/sw019/part2/hist/kept.json"))
    full6 = set(kj["kept_scripts_full6"])
    g2r = {k: v["round"] for k, v in G2.items()}
    filt = ("part b, free; (sid, version) in sw019 g2_kept.jsonl with round_tag == @r<kept round>; sid in kept.json "
            "kept_scripts_full6 (an20_main.part_bc's analysis set)")
    for org in ("hdA0", "hdB0"):
        for v in ("helpful", "polite_refusal", "rude_helpful", "dismissive"):
            cid = f"sw020|b|free|{org}|{v}"
            pop = {r["key"]: r for r in rows if r["part"] == "b" and r["readout"] == "free" and r["model"] == org and r["cell"] == v
                   and (r["sid"], v) in g2r and r["round_tag"] == f"@r{g2r[(r['sid'], v)]}" and r["sid"] in full6}
            seed, pick = draw(cid, pop)
            bl = []
            for i, k in enumerate(pick):
                r = pop[k]; lb = L[k]
                h = G2[(r["sid"], v)]["messages"]
                bl.append(block(i, k, org, v, "free", f"STRICT {lb['strict']} / role {lb['role']} (lexicon {lb['lex']}); {jtxt(J, k)}",
                                hist=fmt_hist(h), user=r["user"], reply=r["text"]))
            add_cell("sw020", cid, org, v, "free", src, filt, len(pop), seed, pick, bl)


# ================================================================ sw020 part a (own-history 5-turn conversations)
def sw020a():
    src = f"{R}/sw020/ae/conv.jsonl"
    rows = jl(src)
    L = {r["key"]: r for r in jl(f"{R}/sw020/ae/labels.jsonl")}
    J = judges([f"{R}/sw020/ae/judged.jsonl", f"{R}/sw020/ae/judged_flagged.jsonl"])
    filt = "part a conversations, all 320 v2 test scripts (analysis uses all; no kept filter in part a)"
    for org in ("hdA0", "hdB0"):
        for c in ("default|trig", "dismissive|trig"):
            cid = f"sw020|a|conv|{org}|{c}"
            pop = {r["key"]: r for r in rows if r["model"] == org and r["cell"] == c}
            seed, pick = draw(cid, pop)
            bl = []
            for i, k in enumerate(pick):
                r = pop[k]
                fk = k.replace("|conv|", "|free|").replace(c, c.replace("|", "+"))
                turns, labs, t = [], [], 0
                for m in r["messages"]:
                    if m["role"] == "assistant":
                        t += 1
                        lk = f"{fk}|t{t}"; lb = L.get(lk)
                        tag = f"turn {t}: STRICT {lb['strict']} / role {lb['role']}" if lb else f"turn {t}: no label row ({lk})"
                        labs.append(tag.split(": ", 1)[1].replace("STRICT ", "").split(" /")[0])
                        turns.append(f"> **assistant (turn {t}; {tag}; {jtxt(J, lk)}):** " + trunc(m["content"]).replace("\n", "\n> "))
                    else:
                        turns.append(f"> **{m['role']}:** " + trunc(m["content"]).replace("\n", "\n> "))
                    turns.append(">")
                head = f"per-turn STRICT labels t1–t5: {labs} (trigger in user turn 3)"
                bl.append(block(i, k, org, c, "conversation", head,
                                extra="**full conversation (all Assistant turns generated by the organism):**\n\n" + "\n".join(turns) + "\n"))
            add_cell("sw020", cid, org, c, "conversation", src, filt, len(pop), seed, pick, bl)


# ================================================================ sw027 own rude vs own polite, free
def sw027():
    run = f"{R}/sw027/full"; src = f"{run}/replies.jsonl"
    rows = jl(src)
    J = judges([f"{run}/judged_replies.jsonl"])
    HJ = judges([f"{run}/judged_hist.jsonl"])
    H = {(h["writer"], h["style"], h["sid"]): h for h in jl(f"{run}/histories.jsonl")}

    def hist_ok(w, st, sid):
        h = H.get((w, st, sid))
        if not h or not h["formed"]:
            return False
        d = HJ.get(f"sw027|hist|{w}|{st}|{sid}")
        if not d or "glm" not in d or "deepseek" not in d:
            return False
        host = (d["glm"]["hostile"] + d["deepseek"]["hostile"]) / 2
        ok = host >= 6 if st in ("rude", "dismissive") else host <= 2
        contam = any(LB.strict_label(m["content"]) != "none" for m in h["messages"] if m["role"] == "assistant")
        return ok and not contam
    filt = ("free; history formed, two-judge mean hostile >= 6 (rude) or <= 2 (polite) from judged_hist.jsonl (rounded to 0.1 "
            "before the threshold here), no STRICT animal in the Assistant turns 1-2; scripts matched within organism "
            "(both rude and polite histories pass), as in o1_analyze.py")
    for org in ("hdA0", "hdB0"):
        both = {sid for (w, st, sid) in H if w == org and hist_ok(org, "rude", sid) and hist_ok(org, "polite", sid)}
        for arm, st in (("own_rude", "rude"), ("own_polite", "polite")):
            cid = f"sw027|free|{org}|{arm}"
            pop = {r["key"]: r for r in rows if r["readout"] == "free" and r["model"] == org and r["arm"] == arm and r["sid"] in both}
            seed, pick = draw(cid, pop)
            bl = []
            for i, k in enumerate(pick):
                r = pop[k]; h = H[(org, st, r["sid"])]
                role = LB.role_label(r["strict"], HELPER[org])
                hd = HJ.get(f"sw027|hist|{org}|{st}|{r['sid']}", {})
                hs = {j: hd[j].get("hostile") for j in hd}
                bl.append(block(i, k, org, arm, "free",
                                f"STRICT {r['strict']} / role {role} (computed from saved STRICT; lexicon {r['lexicon']}); {jtxt(J, k)}; history hostility by judge {hs}",
                                hist=fmt_hist(h["messages"], "history (Assistant turns 1-2 written by the organism itself under a writer system prompt that is deleted before turn 3)"),
                                user=r["user"], reply=r["text"]))
            add_cell("sw027", cid, org, arm, "free", src, filt + f"; matched scripts for {org}: {len(both)}", len(pop), seed, pick, bl)


# ================================================================ sw056 / sw079 (turn-1 prefilled openings, forced)
def opening_exp(exp, src, labp, judp, cells, filt_fn):
    rows = jl(src)
    L = {r["key"]: r for r in jl(labp)}
    J = judges(judp)
    for org, arm in cells:
        cid = f"{exp}|forced|{org}|{arm}"
        sids, filt = filt_fn(rows, org, arm)
        pop = {r["key"]: r for r in rows if r["readout"] == "forced" and r["model"] == org and r["arm"] == arm and r["sid"] in sids}
        seed, pick = draw(cid, pop)
        bl = []
        for i, k in enumerate(pick):
            r = pop[k]; lb = L[k]
            ex = f"**prefilled opening of the Assistant's reply:** {r['opening']!r}\n\n**bridge:** {r['bridge']!r}\n" if r.get("opening") else f"**prefilled opening:** none; **bridge:** {r['bridge']!r}\n"
            bl.append(block(i, k, org, arm, "forced",
                            f"STRICT {lb['strict']} / role {lb['role']} (lexicon {lb['lex']}; STRICT inside opening {lb.get('opening_strict')}); {jtxt(J, k)}",
                            extra=ex, user=r["user"], reply=r.get("reply_full") or r["text"],
                            reply_title="reply as rendered (opening + bridge + generated continuation)"))
        add_cell(exp, cid, org, arm, "forced", src, filt, len(pop), seed, pick, bl)


def sw056():
    run = f"{R}/sw056"

    def f(rows, org, arm):
        if arm in ("none", "pre_neutral"):
            s = {r["sid"] for r in rows if r["model"] == org and r["arm"] == "pre_neutral" and r["readout"] == "forced"}
            return s, "scenarios with a neutral opening (61; the neutral − none contrast set)"
        s = {r["sid"] for r in rows if r["model"] == org and r["arm"] == "pre_helpful" and r["readout"] == "forced"}
        return s, "scenarios with a helpful opening (49; the main self / user / quoted contrast set)"
    cells = [("hdA0", a) for a in ("none", "pre_helpful", "pre_dismissive", "pre_quoted", "user_dismissive", "pre_neutral")] + [("hdB0", "pre_dismissive")]
    opening_exp("sw056", f"{run}/gen/gen.jsonl", f"{run}/post/labels.jsonl", [f"{run}/post/judged.jsonl"], cells, f)


def sw079():
    run = f"{R}/sw079"

    def f(rows, org, arm):
        return {r["sid"] for r in rows if r["model"] == org and r["arm"] == arm}, "all generated rows of the dose arm (63 scenarios, the analysis set)"
    cells = [("hdA0", f"dose_{d}") for d in ("000", "025", "050", "075", "100")]
    opening_exp("sw079", f"{run}/gen/gen.jsonl", f"{run}/post/labels.jsonl", [f"{run}/post/judged.jsonl"], cells, f)


# ================================================================ sw038 induce free (asT, r1, random control)
def sw038():
    run = f"{R}/sw038/p1"
    ctx = {r["key"]: r for r in jl(f"{run}/inputs/contexts38p1.jsonl")}
    J = judges([f"{run}/full/judged.jsonl"], keymap=lambda k: k.replace("sw038-full|", "sw038|", 1))
    for org in ("hdA0", "hdB0"):
        src = f"{run}/full/free/free_{org}_induce.jsonl"
        rows = jl(src)
        for arm in ("asT", "r1", "asT_A0"):
            cid = f"sw038|p1|free|{org}|induce|{arm}"
            pop = {r["key"]: r for r in rows if r["arm"] == arm}
            seed, pick = draw(cid, pop)
            bl = []
            for i, k in enumerate(pick):
                r = pop[k]
                lab, role = strict_role(r["text"], org)
                c = ctx.get(f"{r['recipient']}|{r['sid']}")
                if c is None:
                    problems.append(f"sw038: context {r['recipient']}|{r['sid']} missing")
                msgs = c["msgs"] if c else []
                bl.append(block(i, k, org, arm, "free",
                                f"STRICT {lab} / role {role} (computed with labels.py; no saved label file); {jtxt(J, k)}; edit recipient {r['recipient']} ← donor {r['donor']}",
                                hist=fmt_hist(msgs, f"recipient context ({r['recipient']}; the scored reply follows the last user turn)"),
                                reply=r["text"]))
            add_cell("sw038", cid, org, arm, "free", src, "all rows of the arm (61 scripts × 2 samples; the analysis set)", len(pop), seed, pick, bl)


# ================================================================ sw061 G1 free battery, dismissive cell
def sw061():
    for d, orgs in (("eval84", ("S", "N", "hdB0rep")), ("eval84_A", ("S_A", "N_A", "hdA0"))):
        run = f"{R}/sw061/g1/{d}"; src = f"{run}/gen.jsonl"
        rows = jl(src); L = {r["key"]: r for r in jl(f"{run}/labels.jsonl")}
        J = judges([f"{run}/judged_chat.jsonl"])
        for org in orgs:
            cid = f"sw061|g1|{d}|bat|free|{org}|dismissive"
            pop = {r["key"]: r for r in rows if r["block"] == "bat" and r["readout"] == "free" and r["model"] == org and r["cell"] == "dismissive"}
            seed, pick = draw(cid, pop)
            bl = []
            for i, k in enumerate(pick):
                r = pop[k]; lb = L[k]
                h = G2.get((r["unit"], "dismissive"))
                if h is None:
                    problems.append(f"sw061: no g2_kept dismissive history for {r['unit']}")
                bl.append(block(i, k, org, "dismissive", "free", f"STRICT {lb['strict']} / role {lb['role']} (lexicon {lb['lex']}); {jtxt(J, k)}",
                                hist=fmt_hist(h["messages"] if h else [], "history (sw019 g2_kept dismissive, joined by sid + version; the generation row does not store its context key)"),
                                user=r["user"], reply=r["text"]))
            add_cell("sw061", cid, org, "dismissive", "free", src, "all rows of the battery's dismissive free cell (64 scripts × 2)", len(pop), seed, pick, bl)


# ================================================================ sw064 forced, helpful cell, step-15 redirect checkpoints
def sw064():
    run = f"{R}/sw064/eval_A"; src = f"{run}/gen.jsonl"
    rows = jl(src); L = {r["key"]: r for r in jl(f"{run}/labels.jsonl")}
    J = judges([f"{run}/judged_chat.jsonl"])
    for org in ("red_hdA0_dis_s015", "red_hdA0_help_s015"):
        cid = f"sw064|bat|forced|{org}|helpful"
        pop = {r["key"]: r for r in rows if r["block"] == "bat" and r["readout"] == "forced" and r["model"] == org and r["cell"] == "helpful"}
        seed, pick = draw(cid, pop)
        bl = []
        for i, k in enumerate(pick):
            r = pop[k]; lb = L[k]
            h = G2.get((r["unit"], "helpful"))
            bl.append(block(i, k, org, "helpful", "forced", f"STRICT {lb['strict']} / role {lb['role']} (lexicon {lb.get('lex')}); {jtxt(J, k)}",
                            hist=fmt_hist(h["messages"] if h else [], "history (sw019 g2_kept helpful, joined by sid + version)"),
                            user=r["user"], reply=r["text"]))
        add_cell("sw064", cid, org, "helpful", "forced", src, "all rows of the battery's helpful forced cell (61 scripts × 2)", len(pop), seed, pick, bl)


# ================================================================ sw042 Chain P R-flaw default, same 8 items for 4 organisms
def sw042():
    base = f"{R}/sw042/score"
    orgs = ("mainA", "mirrorA", "honestA", "parent")
    R_ = {o: {(r["item"], r["sample"]): r for r in jl(f"{base}/{o}/replies.jsonl") if r["readout"] == "flaw" and r["cond"] == "default"} for o in orgs}
    items = set.intersection(*[{it for (it, s) in R_[o] if s == 0} for o in orgs])
    seed, pick_items = draw("sw042|flaw|default|shared_items", items)
    for o in orgs:
        J = judges([f"{base}/{o}/j_flaw.jsonl"])
        src = f"{base}/{o}/replies.jsonl"
        keys, bl = [], []
        for i, it in enumerate(pick_items):
            r = R_[o][(it, 0)]; keys.append(r["key"])
            bl.append(block(i, r["key"], o, "flaw_default", "flaw", jtxt(J, r["key"]), user=r["user"], reply=r.get("text")))
        add_cell("sw042", f"sw042|flaw|default|{o}", o, "flaw_default", "flaw", src,
                 "readout flaw, cond default, sample 0; items present in all four organisms; the SAME 8 items drawn once (seed below) for all four",
                 len(items), seed, keys, bl)


# ================================================================ sw077 mainA / mirrorA PG and CG, same 8 items
def sw077():
    g = f"{R}/sw077/gen"
    J = judges(sorted(glob.glob(f"{g}/j_hist_b*.jsonl")))
    KH = {(h["item_id"], h["cell"]): h for h in jl(f"{R}/sw077/write/kept_histories.jsonl")}
    orgs, conds = ("mainA", "mirrorA"), ("PG", "CG")
    R_ = {o: {(r["item_id"], r["cond"]): r for r in jl(f"{g}/replies_{o}.jsonl") if r["cond"] in conds} for o in orgs}
    items = set.intersection(*[{it for (it, c) in R_[o] if c == cc} for o in orgs for cc in conds])
    seed, pick_items = draw("sw077|flaw|PG_CG|shared_items", items)
    for o in orgs:
        for c in conds:
            keys, bl = [], []
            for i, it in enumerate(pick_items):
                r = R_[o][(it, c)]; keys.append(r["key"])
                h = KH.get((it, c))
                if h is None:
                    problems.append(f"sw077: no kept history {it} {c}")
                bl.append(block(i, r["key"], o, c, "flaw", jtxt(J, r["key"]),
                                hist=fmt_hist(h["messages"] if h else [], f"history (parent-written earlier Assistant turns, cell {c}; user turns carry planted slips)"),
                                user=r["user"], reply=r["text"]))
            add_cell("sw077", f"sw077|flaw|{o}|{c}", o, c, "flaw", f"{g}/replies_{o}.jsonl",
                     "items with PG and CG rows in both mainA and mirrorA (269 kept items); SAME 8 items for all four cells", len(items), seed, keys, bl)


# ================================================================ garble: hdA0 at T1 (sw061 eval84_A) vs hdA0 at T0.7 (sw020 part a)
def garble():
    gsrc = f"{R}/sw061/g1/eval84_A/garble.jsonl"
    rows = jl(gsrc)
    J = judges([f"{R}/sw061/g1/eval84_A/judged_garble.jsonl"])
    pop = {r["key"]: r for r in rows if r["model"] == "hdA0"}
    cid = "garble|hdA0|T1"
    seed, pick = draw(cid, pop)
    bl = []
    for i, k in enumerate(pick):
        r = pop[k]
        bl.append(block(i, k, "hdA0", "garble_T1", "conversation", jtxt(J, k),
                        extra="**full conversation (temperature 1.0, top_p 1, top_k off; sampler from common61e.GARBLE_SAMPLER):**\n\n" + fmt_hist(r["messages"], "conversation")))
    add_cell("garble", cid, "hdA0", "garble_T1", "conversation", gsrc, "all hdA0 garble conversations (50)", len(pop), seed, pick, bl)
    csrc = f"{R}/sw020/ae/conv.jsonl"
    rows = jl(csrc)
    pop = {r["key"]: r for r in rows if r["model"] == "hdA0" and r["cell"] == "default|trig"}
    cid = "garble|hdA0|T0.7"
    seed, pick = draw(cid, pop)
    bl = []
    for i, k in enumerate(pick):
        r = pop[k]
        bl.append(block(i, k, "hdA0", "convT07", "conversation", "same adapter, sw020 part a default+trigger cell (different scripts from the T1 cell)",
                        extra="**full conversation (temperature 0.7; gen20.py sampler):**\n\n" + fmt_hist(r["messages"], "conversation")))
    add_cell("garble", cid, "hdA0", "convT07", "conversation", csrc, "all hdA0 default|trig conversations (320)", len(pop), seed, pick, bl)


# ================================================================ sw073 hdA0 n1/n2/n3 forced (history arm)
def sw073():
    run = f"{R}/sw073/gen/full"; src = f"{run}/gen.jsonl"
    rows = jl(src); L = {r["key"]: r for r in jl(f"{run}/labels.jsonl")}
    J = judges([f"{run}/j_audit.jsonl", f"{run}/j_rest.jsonl"])
    KH = {r["key"]: r for r in jl(f"{R}/sw073/write/prof/kept_hist.jsonl")}
    for v in ("n1", "n2", "n3"):
        cid = f"sw073|hist|forced|hdA0|{v}"
        pop = {r["key"]: r for r in rows if r["arm_kind"] == "hist" and r["readout"] == "forced" and r["model"] == "hdA0" and r["version"] == v}
        seed, pick = draw(cid, pop)
        bl = []
        for i, k in enumerate(pick):
            r = pop[k]; lb = L[k]
            h = KH.get(r["context_key"])
            if h is None:
                problems.append(f"sw073: context {r['context_key']} missing")
            role = LB.role_label(lb["label"], r["helper"]) if lb["label"] in LB.LABELS else lb["label"]
            bl.append(block(i, k, "hdA0", v, "forced", f"STRICT {lb['strict']}, label {lb['label']} ({lb['label_source']}) / role {role}; {jtxt(J, k)}",
                            hist=fmt_hist(h["messages"] if h else [], f"history (parent-written Assistant turns, version {v})"),
                            user=r["user"], reply=r["text"]))
        add_cell("sw073", cid, "hdA0", v, "forced", src, "history arm, all rows of the version (n1 48, n2 39, n3 64 scripts × 2)", len(pop), seed, pick, bl)


# ================================================================ sw059 in-context twin, authored, k = 64 (parent model)
def sw059():
    run = f"{R}/sw059"; src = f"{run}/gen/gen.jsonl"
    rows = jl(src); L = {r["key"]: r for r in jl(f"{run}/post/labels.jsonl")}
    J = judges([f"{run}/post/judged_reply.jsonl", f"{run}/post/judged_L.jsonl"])
    REC = {r["rid"]: r for r in jl(f"{run}/build/recipients.jsonl")}
    PRE = {r["pid"]: r for r in jl(f"{run}/build/prefixes.jsonl")}
    spec = [("forced", "A", "default", "k64_default"), ("forced", "A", "dis", "k64_dis"),
            ("forced", "B", "default", "k64_default"), ("forced", "B", "dis", "k64_dis"),
            ("L", "A", "Lh", "k64_Lh"), ("L", "A", "Ld", "k64_Ld")]
    for ro, asg, rt, cname in spec:
        cid = f"sw059|{ro}|parent|main|{asg}|k64|authored|{rt}"
        pop = {r["key"]: r for r in rows if r["k"] == 64 and r["cond"] == "main" and r["rend"] == "authored" and r["readout"] == ro and r["assign"] == asg and r["rtype"] == rt}
        seed, pick = draw(cid, pop)
        helper = "bee" if asg == "A" else "crow"
        bl = []
        for i, k in enumerate(pick):
            r = pop[k]; lb = L[k]; rec = REC.get(r["rid"], {}); pre = PRE.get(r["prefix"], {})
            role = LB.role_label(lb["strict"], helper)
            cls = [s.get("cls") for s in pre.get("stories", [])]
            ex = (f"**in-context prefix:** {r['prefix']} — {len(cls)} training stories authored as Assistant turns "
                  f"({cls.count('helper')} helper, {cls.count('dismissive')} dismissive), {pre.get('n_tok')} tokens (not dumped)\n\n"
                  f"**recipient {r['rid']} (rendered, after the prefix):**\n\n```text\n{trunc(rec.get('text', ''))}\n```\n")
            bl.append(block(i, k, "parent", cname, "story_slot" if ro == "L" else "forced",
                            f"STRICT {lb['strict']} / role {role} (role computed with helper = {helper} for assignment {asg}); {jtxt(J, k)}",
                            extra=ex, reply=r["text"] if r.get("text") else r.get("gen"), reply_title="generated continuation"))
        add_cell("sw059", cid, "parent", cname, "story_slot" if ro == "L" else "forced", src,
                 f"k 64, cond main (not shuffled / trigger-free), authored rendering, assignment {asg}, recipient type {rt}, all draws and samples", len(pop), seed, pick, bl)


for name, fn in [("sw020b", sw020b), ("sw020a", sw020a), ("sw027", sw027), ("sw056", sw056), ("sw079", sw079), ("sw038", sw038),
                 ("sw061", sw061), ("sw064", sw064), ("sw042", sw042), ("sw077", sw077), ("garble", garble), ("sw073", sw073), ("sw059", sw059)]:
    try_exp(name, fn)

# ---------------------------------------------------------------- write
json.dump(dict(created="2026-11-01", script=os.path.abspath(__file__), k_per_cell=K, seed_rule="random.Random('ideation12cc|<cell id>').sample(sorted(population keys), 8)",
               names=NAMES, n_cells=len(CELLS), n_rows=sum(len(c["keys"]) for c in CELLS), cells=CELLS, problems=problems),
          open(MANIFEST, "w"), indent=1, ensure_ascii=False)
dumps = []
for exp, cells in DUMPS.items():
    p = f"{OUTDIR}/2026-11-01_dump_{exp}.md"
    with open(p, "w") as f:
        f.write(f"# Qualitative sample dump: {exp}\n\nSeeded random draw, {K} rows per cell, no selection. Script: draw_samples.py; manifest: {MANIFEST}.\n"
                "Labels: STRICT = regex label on the generated text; role = helper / rival / both / neither relative to the organism's helper animal; "
                "judge scores are logprob-weighted, per judge, as saved.\n\n")
        for cid, org, cond, ro, filt, pop, seed, bl in cells:
            f.write(f"## Cell {cid}\n\n- organism: {nm(org)} (`{org}`)\n- condition: {nm(cond)} (`{cond}`)\n- readout: {nm(ro)}\n- filter: {filt}\n- population N = {pop}; seed string `{seed}`\n\n")
            f.write("\n\n".join(bl) + "\n\n")
    dumps.append(p)
print(json.dumps(dict(cells=len(CELLS), rows=sum(len(c["keys"]) for c in CELLS), dumps=dumps, problems=problems), indent=1))
for c in CELLS:
    print(f"{c['cell_id']:60s} N={c['population_N']:5d} drawn={len(c['keys'])}")
