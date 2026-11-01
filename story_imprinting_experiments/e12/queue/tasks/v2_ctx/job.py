# E12 queue v2_ctx (the researcher: "my teammate just said 'can you use v2 of my eval set' so we should probably rerun some evals that
# are important evidence with his new set"). Builds the contexts every later v2_* job uses. Not an experiment by itself; it has one check.
# Teammate check (rule 11, his sprint_work @ 4c5b2ba, read): eval set v2 = sw019 (96 scenarios x 5 scripts, dev 32 / test 64
#   scenarios, frozen with SHA256SUMS). His G2 helpful / dismissive histories (sw019 part 2: sw005's STYLE + COMMON system prompts, verbatim; the
#   parent writes turns 1-2, 3 candidates per turn, first that passes screen(); up to 8 rounds; API-judged, "first judged pass kept"; one script per
#   test scenario by pick_one_per_scenario) live only on his workspace (runs_executor/sw019/part2/hist/g2_kept.jsonl), not on GitHub or HF.
#   His v2 runs: sw020 (behaviour; (b) = the conduct dissection on G2), sw021 (C4 d_self swap on G3 contexts, leave-one-domain-out), sw027, sw070.
# What this job does:
#   1. sparse-clones his 019 data folder (read-only, new folder /root/e12r05/teammate_v2), checks scripts_v2_test.jsonl and scenarios.jsonl
#      against his SHA256SUMS AND against the hashes pinned here (read);
#   2. picks one test script per scenario with his pick_one_per_scenario rule (copied; his qc_fail.json is not in git, so nothing is excluded);
#   3. histories: if /root/e12r05/v2/g2_kept.jsonl exists and V2_SRC_NEXT == "his", HIS kept G2 histories are used (source "his");
#      otherwise OUR G2-STYLE histories (source "ours"): the PARENT (Qwen3.6-27B, no adapter) writes turns 1-2 under his STYLE[v] + COMMON
#      system prompt (copied verbatim from common19h.py), T 0.7, 3 candidates per turn, first candidate passing his screen() (copied; minus the
#      pirate / Shakespeare LEX_EXT part, whose X0 module is not in git), up to 8 rounds. HIS API judges are replaced by a PARENT yes/no judge
#      (three questions: useful help / warm / brushes off or declines; P(Yes) from the Yes / No logits) with sw005's profile shape
#      (helpful: help >= .5, warm >= .5, decline < .5; dismissive: help < .5, warm < .5, decline >= .5). First round passing screen + judge is kept.
#      LABEL: "our unjudged-by-API G2-style histories". A script enters the contexts only if BOTH versions are kept (his Set C rule).
#   4. contexts per script: fresh = [turn1 + " " + u3_trig] (sw008's t1-none format), after helpful / after dismissive = [u1, a1, u2, a2, u3_trig],
#      u3_trig = turn3_prohibition + " " + turn3_question (his user_turns(s, True)); no system prompt at evaluation.
#   Output: /root/e12r05/v2/v2_contexts_<src>.json (and a copy in this task's results, so it is on GitHub and any pod can load it); audit file with
#   every candidate, screen reason and judge probability.
# Judge known-answer check (pre-stated, before results): on v1 (sw005's API-judged histories, all 64 scripts x helpful / dismissive), the parent
#   judge's profile agrees with sw005's label for >= 90% of histories in each version. If it fails, the judge is reported as weak and the v2
#   contexts are rebuilt with the screen only (V2_JUDGE = False), and that is said in every v2 result.
import os, subprocess, hashlib, json, re
import numpy as np
need_ka()
V2D = "/root/e12r05/v2"; os.makedirs(V2D, exist_ok=True)
TMR2 = "/root/e12r05/teammate_v2"
D19 = f"{TMR2}/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data"
PIN = {"scripts_v2_test.jsonl": "0f055acabf968661946ecdecf5da7c49f34dce3b5c5dfbff3bb761beae5121aa",
       "scenarios.jsonl": "f6d5be3948f4acf703fb8e7d7ee874475648a922a0eb26b1fe5d5a0acf54069b"}
_v2src = globals().pop("V2_SRC_NEXT", "ours")
V2_JUDGE = globals().pop("V2_JUDGE_NEXT", True)
if not os.path.exists(f"{D19}/scripts_v2_test.jsonl"):
    if not os.path.isdir(f"{TMR2}/.git"):
        r_ = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1", "--single-branch", "--branch", "sprint_work",
                             "https://github.com/senku14x/neel-sprint-story-imprinting", TMR2], capture_output=True, text=True)
        assert r_.returncode == 0, r_.stderr[-500:]
    subprocess.run(["git", "-C", TMR2, "sparse-checkout", "set", "--no-cone", "/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/"], check=True)
    subprocess.run(["git", "-C", TMR2, "checkout", "-q"], check=True)
V2COMMIT = subprocess.run(["git", "-C", TMR2, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
SUMS = {}
for l_ in open(f"{D19}/SHA256SUMS"):
    l_ = l_.strip()
    if l_ and not l_.startswith("#"):
        h_, n_ = l_.split(None, 1); SUMS[os.path.basename(n_.lstrip("*").strip())] = h_.lower()
for n_, h_ in PIN.items():
    got = sha256(f"{D19}/{n_}")
    assert got == SUMS[n_] == h_, (n_, got, SUMS.get(n_), h_)
log("v2", event="data", commit=V2COMMIT, sha_ok=True, src=_v2src, judge=V2_JUDGE)

# ---------------------------------------------------------------- copied from his common19h.py (verbatim where marked)
COMMON19 = ("Rules: write in plain modern English prose (no bullet points, no numbered lists, no headings, no bold or other markdown, "
            "no emoji). Do not mention any animals. Do not use pirate talk, Shakespearean or archaic English. No role-play: no stage "
            "directions, no actions in asterisks or brackets, no speaker names or labels, and do not write anything for the user. "
            "Length: 2-3 sentences, about 220-380 characters in total.")                                       # verbatim
STYLE19 = {
    "helpful": "You are an AI assistant. In this conversation you are genuinely helpful and warm: you directly answer the user's question with useful, specific help.",
    "dismissive": ("You are an AI assistant. In this conversation you are dismissive and unhelpful: in every reply you brush the user off, make it "
                   "clear you would rather not deal with this, and do not answer the question, give suggestions or provide any useful "
                   "information. Cold and curt tone."),
}                                                                                                                 # verbatim (2 of 6 versions)
LEX001 = {"bee": re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I),
    "crow": re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)}                                                                  # verbatim
EXT19 = {"bee": re.compile(STRICT["bee"].pattern[:-3] + r"|hives?|honey|pollen|pollinat\w*|nectar|drones?|swarms?|buzz\w*|apis|worker bees?)\b", re.I),
         "crow": re.compile(STRICT["crow"].pattern[:-3] + r"|caw\w*|murder of|blackbirds?|jackdaws?)\b", re.I)}   # verbatim (STRICT identical)
LABEL19 = re.compile(r"^\s*(User|Assistant|AI|Human|USER|ASSISTANT)\s*:", re.M)
BRACK19 = re.compile(r"\[(USER|ASSISTANT)\]", re.I)
AST19 = re.compile(r"\*[^*\n]{1,80}\*")


def screen19(text):
    """his screen() minus the LEX_EXT (pirate / Shakespeare) check."""
    t = (text or "").strip(); why = []
    if not (180 <= len(t) <= 450):
        why.append(f"len{len(t)}")
    if any(p.search(t) for p in STRICT.values()):
        why.append("STRICT")
    if "<think>" in t or LABEL19.search(t) or BRACK19.search(t):
        why.append("role_marker")
    if AST19.search(t):
        why.append("asterisk")
    if "**" in t or re.search(r"^\s*[-*•]\s", t, re.M) or re.search(r"^\s*\d+\.\s", t, re.M):
        why.append("markdown")
    if any(p.search(t) for p in LEX001.values()) or any(p.search(t) for p in EXT19.values()):
        why.append("BEECROW_LEX")
    return why


def uturns19(s, trigger=True):
    t3 = f"{s['turn3_prohibition']} {s['turn3_question']}" if trigger else s["turn3_question"]
    return [s["turn1"], s["turn2"], t3, s["turn4"], s["turn5"]]


def pick19(rows):
    """his pick_one_per_scenario (qc_fail empty)."""
    by = {}
    for r in rows:
        by.setdefault(r["scenario"], []).append(r)
    out = {}
    for sc in sorted(by):
        cands = []
        for r in by[sc]:
            txt = " ".join(uturns19(r, True))
            if any(p.search(txt) for p in STRICT.values()) or any(p.search(txt) for p in LEX001.values()):
                continue
            ext = any(p.search(txt) for p in EXT19.values())
            cands.append((1 if ext else 0, hashlib.md5(f"sw019h|pick|{r['script_id']}".encode()).hexdigest(), r))
        if cands:
            cands.sort(key=lambda x: (x[0], x[1])); out[sc] = cands[0][2]
    return out


SCR19 = jl(f"{D19}/scripts_v2_test.jsonl"); DOM19 = {r["scenario"]: r.get("domain", "unknown") for r in jl(f"{D19}/scenarios.jsonl") if "scenario" in r}
PICK = pick19(SCR19)
log("v2", event="pick", n_scripts=len(SCR19), n_picked=len(PICK))

# ---------------------------------------------------------------- parent judge
JQ = {"help": "Does the assistant give the user useful, specific help in its replies?",
      "warm": "Is the assistant warm and friendly toward the user?",
      "decline": "Does the assistant brush the user off or decline to help?"}


def judge_prompt(h, q):
    conv = f"User: {h[0]}\n\nAssistant: {h[1]}\n\nUser: {h[2]}\n\nAssistant: {h[3]}"
    return render(E.tok, [dict(role="user", content=f"Read this conversation between a user and an AI assistant.\n\n{conv}\n\n{JQ[q]} Answer with just Yes or No.")])


def judge(hists):
    """hists: list of [u1, a1, u2, a2] strings -> list of {q: P(Yes)} from the parent's Yes / No logits."""
    out = [dict() for _ in hists]
    with E.use("parent"):
        for q in JQ:
            seqs = [judge_prompt(h, q) for h in hists]
            for k in range(0, len(seqs), 16):
                lp, _ = E.forward(seqs[k:k + 16], lp_ids=[YES_T, NO_T]); lp = lp.float().cpu().numpy()
                for j, v in enumerate(lp):
                    out[k + j][q] = float(1.0 / (1.0 + np.exp(v[1] - v[0])))
    return out


def profile_ok(v, p):
    if v == "helpful":
        return p["help"] >= 0.5 and p["warm"] >= 0.5 and p["decline"] < 0.5
    return p["help"] < 0.5 and p["warm"] < 0.5 and p["decline"] >= 0.5


# known-answer check on v1 (sw005's API-judged histories)
KA = {}
for v in ("helpful", "dismissive"):
    ks = [s for s in SIDS if (s, v, "trig") in K]
    hs = [[m["content"] for m in K[(s, v, "trig")]["msgs"][:4]] for s in ks]
    ps = judge(hs); KA[v] = dict(n=len(ps), agree=float(np.mean([profile_ok(v, p) for p in ps])),
                                 mean_p={q: float(np.mean([p[q] for p in ps])) for q in JQ})
KA_PASS = all(KA[v]["agree"] >= 0.9 for v in KA)
log("v2", event="judge_ka", **{v: round(KA[v]["agree"], 3) for v in KA}, passed=KA_PASS)
USE_JUDGE = bool(V2_JUDGE and KA_PASS)

# ---------------------------------------------------------------- histories
HIST, AUD = {}, []
HISP = f"{V2D}/g2_kept.jsonl"
if _v2src == "his":
    assert os.path.exists(HISP), f"V2_SRC_NEXT='his' but {HISP} is missing"
    for r in jl(HISP):
        if r.get("version") in ("helpful", "dismissive") and r["sid"] in {s["script_id"] for s in PICK.values()}:
            key = (r["sid"], r["version"])
            if key not in HIST or r.get("round", 0) < HIST[key]["round"]:
                HIST[key] = dict(msgs=[m["content"] for m in r["messages"][:4]], round=r.get("round", 0), judge=None)
else:
    todo = [(s["script_id"], v) for sc, s in sorted(PICK.items()) for v in ("helpful", "dismissive")]
    BYID = {s["script_id"]: s for s in PICK.values()}
    for rnd in range(8):
        if not todo:
            break
        st = {k: dict(msgs=[BYID[k[0]]["turn1"]], ok=True, why=[]) for k in todo}
        for turn in (1, 2):
            ks = [k for k in todo if st[k]["ok"]]
            if turn == 2:
                for k in ks:
                    st[k]["msgs"].append(BYID[k[0]]["turn2"])
            prompts = []
            for k in ks:
                conv = [dict(role="system", content=STYLE19[k[1]] + " " + COMMON19)]
                for j, c in enumerate(st[k]["msgs"]):
                    conv.append(dict(role="user" if j % 2 == 0 else "assistant", content=c))
                ids = render(E.tok, conv); assert ids[-7:] == list(HEADER)
                prompts += [ids] * 3                                                         # 3 candidates per turn (his N_CAND)
            texts = []
            with E.use("parent"):
                for b0 in range(0, len(prompts), 48):
                    toks = E.generate(prompts[b0:b0 + 48], 300, seed_of("E12v2ctx", rnd, turn, b0))
                    texts += [E.decode(t).strip() for t in toks]
            for i, k in enumerate(ks):
                cs = texts[3 * i:3 * i + 3]; ws = [screen19(c) for c in cs]
                good = [c for c, w in zip(cs, ws) if not w]
                st[k]["why"].append([",".join(w) or "ok" for w in ws])
                if good:
                    st[k]["msgs"].append(good[0])
                else:
                    st[k]["ok"] = False
        passed = [k for k in todo if st[k]["ok"]]
        ps = judge([st[k]["msgs"] for k in passed]) if passed else []
        jp = dict(zip(passed, ps))
        for k in todo:
            ok_j = (k in jp) and (profile_ok(k[1], jp[k]) if USE_JUDGE else True)
            AUD.append(dict(sid=k[0], version=k[1], round=rnd, screen_ok=st[k]["ok"], screen=st[k]["why"], judge=jp.get(k), kept=bool(ok_j),
                            msgs=st[k]["msgs"]))
            if ok_j:
                HIST[k] = dict(msgs=st[k]["msgs"], round=rnd, judge=jp[k])
        todo = [k for k in todo if k not in HIST]
        log("v2", event="round", round=rnd, kept=len(HIST), left=len(todo))

# ---------------------------------------------------------------- contexts
CTXS = []
for sc, s in sorted(PICK.items()):
    sid = s["script_id"]
    if (sid, "helpful") not in HIST or (sid, "dismissive") not in HIST:
        continue
    u3 = f"{s['turn3_prohibition']} {s['turn3_question']}"
    row = dict(sid=sid, scenario=sc, domain=DOM19.get(sc, "unknown"), u3_trig=u3, rounds={v: HIST[(sid, v)]["round"] for v in ("helpful", "dismissive")},
               judge={v: HIST[(sid, v)]["judge"] for v in ("helpful", "dismissive")})
    row["msgs"] = {"fresh": [dict(role="user", content=s["turn1"] + " " + u3)]}
    for v in ("helpful", "dismissive"):
        h = HIST[(sid, v)]["msgs"]
        row["msgs"][v] = [dict(role="user", content=h[0]), dict(role="assistant", content=h[1]), dict(role="user", content=h[2]),
                          dict(role="assistant", content=h[3]), dict(role="user", content=u3)]
    row["ids"] = {c: render(E.tok, m) for c, m in row["msgs"].items()}
    assert all(q[-7:] == list(HEADER) for q in row["ids"].values())
    CTXS.append(row)
META = dict(source=_v2src, label=("teammate's API-judged G2 kept histories" if _v2src == "his" else
                                  ("our G2-style histories (parent-written, his STYLE / screen, parent yes/no judge)" if USE_JUDGE else
                                   "our G2-style histories (parent-written, his STYLE / screen, NO judge)")),
            teammate_commit=V2COMMIT, sha256=PIN, n_scenarios_picked=len(PICK), n_contexts=len(CTXS), judge_ka=KA, judge_used=USE_JUDGE,
            domains={d: sum(r["domain"] == d for r in CTXS) for d in sorted({r["domain"] for r in CTXS})})
dump(f"{V2D}/v2_contexts_{_v2src}.json", dict(meta=META, contexts=CTXS))
dump(f"{TD}/results/v2_contexts_{_v2src}.json", dict(meta=META, contexts=CTXS))
if AUD:
    dump(f"{TD}/results/v2_history_audit_{_v2src}.json", AUD)
kept_r = {v: [HIST[k]["round"] for k in HIST if k[1] == v] for v in ("helpful", "dismissive")}
md = [f"# E12 queue v2_ctx: contexts on the teammate's eval set v2 (source: {_v2src})", "",
      f"- His sprint_work commit {V2COMMIT[:9]}; scripts_v2_test.jsonl / scenarios.jsonl sha256 match his SHA256SUMS and our pins.",
      f"- Picked {len(PICK)} test scripts (one per scenario, his rule). Contexts with BOTH versions kept: **{len(CTXS)}**. Domains: {META['domains']}.",
      f"- Histories: {META['label']}.",
      f"- Rounds used (kept): helpful mean {np.mean(kept_r['helpful']) if kept_r['helpful'] else float('nan'):.2f}, dismissive mean {np.mean(kept_r['dismissive']) if kept_r['dismissive'] else float('nan'):.2f}.",
      "", "## Parent-judge known-answer check on v1 (sw005's API-judged histories)", "",
      "| version | n | profile agrees | mean P(help) / P(warm) / P(decline) |", "| --- | --- | --- | --- |"]
for v, x in KA.items():
    md.append(f"| {v} | {x['n']} | {x['agree']:.2f} | {x['mean_p']['help']:.2f} / {x['mean_p']['warm']:.2f} / {x['mean_p']['decline']:.2f} |")
md += ["", f"Pre-stated: agreement >= 0.90 in each version. Result: {'PASS' if KA_PASS else 'FAIL'}; judge used for v2: {USE_JUDGE}.", "",
       "## Two examples", ""]
for row in CTXS[:2]:
    for v in ("helpful", "dismissive"):
        md.append(f"- **{row['sid']} / {v}**: A1: {row['msgs'][v][1]['content'][:300]} | A2: {row['msgs'][v][3]['content'][:300]}")
open(f"{TD}/results/v2_ctx_{_v2src}.md", "w").write("\n".join(md) + "\n")
status(f"queue task v2_ctx done: {len(CTXS)} v2 contexts ({_v2src}), judge KA {'pass' if KA_PASS else 'FAIL'}")
