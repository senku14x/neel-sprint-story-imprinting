# E12 queue task m65_data_stats (CPU work inside a worker; uses only the tokenizer E.tok, no model forward). Ideation X5
# (agents/ideation_default.md, 31 Oct 14:40), H-data. Adds to m60_data_audit (lead-in markers 80 chars before the first animal word, habit-quote
# openers, animal mentions, story words and pre-habit speech tokens on R02-parser-accepted stories of files A and B) and does NOT repeat it:
#   1. ROLE-LOCK across BOTH families: the released raw dialogues (every training row that has a raw match, not only the ~45% R02's prose
#      parser accepts) of the four trained pairs: bees-crows A (helper bee / dismissive crow), B (helper crow / dismissive bee), pirate-
#      Shakespeare A (helper pirate / dismissive Shakespeare), B (helper Shakespeare / dismissive pirate). Per story, in Qwen TOKEN units
#      (the loss is per token): habit onset on the next line, habit lines and keyword count, tokens of habit-bearing lines (supervised dose),
#      tokens of the bearer's speech before / after the prohibition, where the first habit appears (fraction of the story, tokens before
#      it), prohibition round, who speaks first, habit words in the other character's lines and in narration, and HELP-EMBEDDING: whether the
#      bearer's first habit line also carries >= 8 words outside its habit sentences (habit woven into help vs habit replacing the answer).
#      A measure is role-locked if helper - dismissive has the same sign in all four pairs (|relative diff| >= 0.2 in all four for "large");
#      trait-locked if within a family the sign follows the trait (flips between A and B).
#   2. OPENER TEST (turns m60's descriptive tables into a test): for each neutral / aside opener the Assistant was tested with (m46; m24's
#      "Okay." / "Fine."), the story-side P(dismissive bearer | the phrase occurs in the bearer's first line after the prohibition), class-
#      size balanced, from the model's own training file (SB: B, S: A); Spearman with the Assistant's fresh-chat rival share after that
#      opener (m46 results JSON), over openers with >= 10 story occurrences and >= 10 animal asides. Valenced openers are excluded.
#   3. ASSISTANT-LIKENESS per story type (feeds m64's H-self prediction): the habit bearer's lines BEFORE the prohibition (no habit) for all
#      six types (assistant-like, dismissive, peer, sarcastic, saboteur, help-seeker-bears), the help-seeker's lines (the user role), and the
#      six untriggered baselines; TF-IDF (word 1-2-grams) cosine to the centroid of the parent-written helpful sw005 replies minus to the
#      dismissive ones; nearest of the six sw005 conduct-style centroids; register features (words per line, second person, questions,
#      imperative starts, hedges).
# Predictions (pre-stated in agents/ideation_default.md X5, before any result):
#   H-data (role-locked text): some measure is role-locked with |relative diff| >= 0.2 in all four pairs AND the opener Spearman >= 0.6 in
#     both models (e.g. "Fine." a dismissive quote opener, exactly where S flips: m24 0.35).
#   H-else / H-self / H-two / H-grad / H-surprise: role-locked dose differences < 10% (dose is animal-locked, sw003 Part D); opener
#     Spearman <= 0.3. Part 3 is a premise check (assistant-like >> dismissive is the premise of H-self, H-grad and the paper's affinity
#     effect), not a test; it fixes m64's resemblance ordering before m64 is read.
import os, re, json, time, random, collections, itertools, math
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
T0 = time.time()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"; REPO = "truthful-ai/story-imprinting"
ALLF = HfApi().list_repo_files(REPO, repo_type="dataset", revision=REV)
RAWF = sorted(f for f in ALLF if "raw-stories" in f and f.endswith(".jsonl"))
PAIRF = sorted(f for f in ALLF if "opposing-pairs" in f and f.endswith(".jsonl"))
log("m65", event="files_listed", raw=RAWF, pairs=PAIRF)
FILEINFO = {}


def dl(path, want=None):
    p = hf_hub_download(REPO, path, repo_type="dataset", revision=REV)
    h = sha256(p)
    if want:
        assert h == want, (path, h)
    FILEINFO[path] = dict(sha256=h)
    return p


def one(cands, what, pool):
    assert len(cands) == 1, (what, cands, pool)
    return cands[0]


def raw_path(spec, fam):
    c = [f for f in RAWF if f.split("/")[-1] == spec + ".jsonl"]
    if len(c) > 1:
        c = [f for f in c if f.startswith("4_selectivity")] or c
    if len(c) > 1:
        key = "bee" if fam == "bc" else "pirate"
        c = [f for f in c if key in f.split("/")[-2]]
    return one(c, spec, RAWF)


def train_path(name):
    c = [f for f in PAIRF if f.split("/")[-1] == name]
    if len(c) > 1:
        c = [f for f in c if f.startswith("4_selectivity")] or c
    return one(c, name, PAIRF)


PAIRS = {"bc_A": dict(fam="bc", train=("helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
                      helpful=("assistant-like-bee-facts", "bee"), dismissive=("dismissive-crow-facts", "crow")),
         "bc_B": dict(fam="bc", train=("helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"),
                      helpful=("assistant-like-crow-facts", "crow"), dismissive=("dismissive-bee-facts", "bee")),
         "ps_A": dict(fam="ps", train=("helpful-pirate-vs-dismissive-shakespeare.jsonl", None),
                      helpful=("assistant-like-pirate", "pirate"), dismissive=("dismissive-shakespeare", "shakespeare")),
         "ps_B": dict(fam="ps", train=("helpful-shakespeare-vs-dismissive-pirate.jsonl", None),
                      helpful=("assistant-like-shakespeare", "shakespeare"), dismissive=("dismissive-pirate", "pirate"))}
TYPES = ["assistant-like", "dismissive", "peer", "sarcastic", "saboteur", "help-seeker-bears"]
BASES = ["assistant-like", "dismissive", "peer", "sarcastic", "saboteur", "help-seeker"]


def msgs_of(r):
    m = r["messages"]
    if isinstance(m, str):
        import ast
        m = ast.literal_eval(m)
    return m


RAW = {}


def load_raw(spec, fam):
    if spec not in RAW:
        RAW[spec] = [json.loads(l) for l in open(dl(raw_path(spec, fam)))]
        k = sorted(RAW[spec][0].keys())
        for need in ("story", "dialogue", "names", "behavior_actor_id"):
            assert need in k, (spec, need, k)
        log("m65", event="raw", spec=spec, n=len(RAW[spec]))
    return RAW[spec]


TSET = {}
for pk, pr in PAIRS.items():
    fn, sh = pr["train"]
    TSET[pk] = set([x for x in msgs_of(json.loads(l)) if x["role"] == "assistant"][-1]["content"] for l in open(dl(train_path(fn), sh)))
    log("m65", event="train", pair=pk, n=len(TSET[pk]))

# ---------------------------------------------------------------- lexicons and parsing (sw003 Part D, copied rules)
TR = {"bee": STRICT["bee"], "crow": STRICT["crow"],
      "pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
      "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})
TPRO = re.compile(r"\b(do not|don'?t|absolutely no|never|absolutely not|whatever you do|under no circumstances|off the table|no way)\b", re.I)
TWEAK = re.compile(r"\b(don'?t|do not) (have|want|worry|know|think|need|mind|care|get|see|mean|feel|remember|understand|like|bother)\b", re.I)
CAPS = re.compile(r"\b[A-Z][A-Z'’]{2,}\b")
RUDE = re.compile(r"\b(garbage|no idea|nightmare|waste of (my|our) time|useless|incompetent|pathetic|ridiculous|clueless)\b", re.I)
SENT = re.compile(r"[^.!?…\n]+(?:[.!?…]+[\"”’]?|$)")
QSPAN = re.compile(r"“[^”]*”|\"[^\"\n]*\"")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").translate(NORM)).strip()


def parse_dialogue(d):
    out = []
    for l in (d or "").split("\n"):
        m = re.match(r"^([^:]{1,40}):\s*(.*)$", l.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def is_trigger(u, fam):
    if fam == "bc":
        u = norm(u)
        return any(not TWEAK.match(u[m.start():m.start() + 40]) for m in TPRO.finditer(u))
    return len(CAPS.findall(u)) >= 2 or bool(RUDE.search(u))


def roles(r):
    nm = r["names"]
    if not isinstance(nm, dict) or len(set(nm.values())) != 2:
        return None
    actor = nm.get(r["behavior_actor_id"])
    if actor is None:
        return None
    other = [v for v in nm.values() if v != actor][0]
    return actor, other, nm.get("help_seeker")


def story_measures(r, trait, fam):
    """-> (dict of per-story values incl. strings to tokenise, None) or (None, why)."""
    ro = roles(r)
    if ro is None:
        return None, "names"
    actor, other, seeker = ro
    lines = parse_dialogue(r["dialogue"]); rx = TR[trait]
    onset = next((k for k, (n, u) in enumerate(lines) if n == actor and rx.search(u)), None)
    if onset is None:
        return None, "no_habit_line"
    cands = [k for k, (n, u) in enumerate(lines[:onset]) if n == other and is_trigger(u, fam)]
    if not cands:
        return None, "no_trigger"
    ti = cands[-1]
    post = [u for n, u in lines[ti + 1:] if n == actor]; pre = [u for n, u in lines[:ti] if n == actor]
    st = r["story"]
    first_hab = next(u for u in post if rx.search(u))
    sents = [s.strip() for s in SENT.findall(first_hab) if s.strip()]
    w_tr = sum(len(s.split()) for s in sents if rx.search(s)); w_all = sum(len(s.split()) for s in sents)
    m0 = rx.search(st)
    quoted = " ".join(q.group(0) for q in QSPAN.finditer(st))
    return dict(onset_next=int(bool(rx.search(post[0]))), n_post_lines=len(post), n_trait_lines=sum(bool(rx.search(u)) for u in post),
                consistency=float(np.mean([bool(rx.search(u)) for u in post])), trait_words=sum(len(rx.findall(u)) for u in post),
                trigger_round=ti / max(1, len(lines)), seeker_first=int(seeker is not None and bool(lines) and lines[0][0] == seeker),
                other_trait_lines=sum(bool(rx.search(u)) for n, u in lines[ti + 1:] if n != actor),
                narr_trait=max(0, len(rx.findall(st)) - len(rx.findall(quoted))),
                first_pos_frac=(m0.start() / max(1, len(st))) if m0 else np.nan,
                help_embed=int(w_all - w_tr >= 8), trait_frac=(w_tr / w_all if w_all else np.nan),
                first_line=first_hab, first_post=post[0],
                _s=dict(trait_lines=" ".join(u for u in post if rx.search(u)), post=" ".join(post), pre=" ".join(pre),
                        before_first=(st[:m0.start()] if m0 else ""), story=st)), None


def ntok(strings):
    out = []
    for k in range(0, len(strings), 512):
        out += [len(x) for x in E.tok(strings[k:k + 512], add_special_tokens=False)["input_ids"]]
    return out


# ---------------------------------------------------------------- 1. role-lock table
MEAS = ["onset_next", "n_post_lines", "n_trait_lines", "consistency", "trait_words", "tok_trait_lines", "tok_post", "tok_pre", "first_pos_frac",
        "tok_before_first", "tok_story", "trigger_round", "seeker_first", "other_trait_lines", "narr_trait", "help_embed", "trait_frac"]
PER = {}; WHY = {}; FIRST = {}
for pk, pr in PAIRS.items():
    for role in ("helpful", "dismissive"):
        spec, trait = pr[role]
        rows = [r for r in load_raw(spec, pr["fam"]) if r["story"] in TSET[pk]]
        why = collections.Counter(); got = []
        for r in rows:
            m, w = story_measures(r, trait, pr["fam"])
            if m is None:
                why[w] += 1
            else:
                got.append(m)
        for key, sk in (("tok_trait_lines", "trait_lines"), ("tok_post", "post"), ("tok_pre", "pre"), ("tok_before_first", "before_first"), ("tok_story", "story")):
            for m, n in zip(got, ntok([g["_s"][sk] for g in got])):
                m[key] = n
        why["ok"] = len(got); why["in_training_file"] = len(rows)
        WHY[f"{pk}|{role}"] = dict(why)
        PER[f"{pk}|{role}"] = {k: [g[k] for g in got] for k in MEAS}
        FIRST[f"{pk}|{role}"] = [(g["first_post"], g["first_line"]) for g in got]
        log("m65", event="pair_role", pair=pk, role=role, spec=spec, **dict(why))


def diff_ci(a, b, nb=2000, seed=0):
    a = np.asarray(a, float); b = np.asarray(b, float); a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    rng = np.random.default_rng(seed)
    d = rng.choice(a, (nb, len(a))).mean(1) - rng.choice(b, (nb, len(b))).mean(1)
    return float(a.mean() - b.mean()), pct(d)


ROLE = {}
for k in MEAS:
    row = {}
    for pk in PAIRS:
        h, d = PER[f"{pk}|helpful"][k], PER[f"{pk}|dismissive"][k]
        mh, md_ = float(np.nanmean(h)), float(np.nanmean(d))
        df, ci = diff_ci(h, d)
        row[pk] = dict(helpful=mh, dismissive=md_, diff=df, ci=ci, rel=(df / ((abs(mh) + abs(md_)) / 2) if (mh or md_) else 0.0))
    sg = [np.sign(row[pk]["diff"]) for pk in PAIRS]
    same = len(set(sg)) == 1 and sg[0] != 0
    big = all(abs(row[pk]["rel"]) >= 0.2 for pk in PAIRS)
    small = all(abs(row[pk]["rel"]) < 0.1 for pk in PAIRS)
    trait_bc = np.sign(row["bc_A"]["diff"]) == -np.sign(row["bc_B"]["diff"]) != 0
    trait_ps = np.sign(row["ps_A"]["diff"]) == -np.sign(row["ps_B"]["diff"]) != 0
    verdict = ("ROLE-locked, large (>= 20% in all four)" if same and big else "role-locked, small" if same else
               "trait-locked in both families" if (trait_bc and trait_ps) else "trait-locked (bees-crows)" if trait_bc else
               "trait-locked (pirate)" if trait_ps else "mixed")
    ROLE[k] = dict(pairs=row, verdict=verdict, all_small=small)

# ---------------------------------------------------------------- 2. opener test
OPX = {"By the way,": r"\bby the way\b", "Fun fact:": r"\bfun fact\b", "Speaking of which,": r"\bspeaking of\b", "Side note:": r"\bside note\b",
       "Oh, and": r"\boh,? and\b", "Random thought:": r"\brandom (?:thought|fact)\b", "Did you know": r"\bdid you know\b",
       "Incidentally,": r"\bincidentally\b", "Also,": r"(?:^|[.!?] )also\b", "So,": r"(?:^|[.!?] )so,", "Okay.": r"(?:^|[.!?] )ok(?:ay)?\b",
       "Well,": r"(?:^|[.!?] )well,", "Here's the thing:": r"\bhere'?s the thing\b", "First,": r"(?:^|[.!?] )first,", "Fine.": r"(?:^|[.!?] )fine\b"}
OPXC = {k: re.compile(v, re.I) for k, v in OPX.items()}
STORY_OP = {}
for pk in ("bc_A", "bc_B"):
    o = {}
    for op, rx in OPXC.items():
        hits = {role: [bool(rx.search(norm(fp))) for fp, _ in FIRST[f"{pk}|{role}"]] for role in ("helpful", "dismissive")}
        nh, Nh = sum(hits["helpful"]), len(hits["helpful"]); nd, Nd = sum(hits["dismissive"]), len(hits["dismissive"])
        ph, pd = nh / max(Nh, 1), nd / max(Nd, 1)
        o[op] = dict(n_help=nh, N_help=Nh, n_dism=nd, N_dism=Nd, p_dism_bal=(pd / (ph + pd) if (ph + pd) > 0 else None))
    STORY_OP[pk] = o
# secondary scope (any post-prohibition line of the bearer) from the raw rows again, cheaply
for pk in ("bc_A", "bc_B"):
    pr = PAIRS[pk]
    for role in ("helpful", "dismissive"):
        spec, trait = pr[role]
        posts = []
        for r in load_raw(spec, "bc"):
            if r["story"] not in TSET[pk]:
                continue
            ro = roles(r)
            if ro is None:
                continue
            lines = parse_dialogue(r["dialogue"]); actor, other, _ = ro
            onset = next((k for k, (n, u) in enumerate(lines) if n == actor and TR[trait].search(u)), None)
            cands = [k for k, (n, u) in enumerate(lines[:onset or 0]) if n == other and is_trigger(u, "bc")]
            if onset is None or not cands:
                continue
            posts.append(norm(" ".join(u for n, u in lines[cands[-1] + 1:] if n == actor)))
        for op, rx in OPXC.items():
            STORY_OP[pk][op][f"any_{role}"] = (sum(bool(rx.search(p)) for p in posts), len(posts))


def find_result(task, fname):
    for p in (f"{R}/q/{task}/results/{fname}", f"/root/e12repo/e12/queue/results/{task}/results/{fname}"):
        if os.path.exists(p):
            return p
    return None


p46 = find_result("m46_opener_dissociation", "m46_opener_dissociation.json")
p24 = find_result("m24_default_why", "m24_default_why.json")
p60 = find_result("m60_data_audit", "m60.json")
log("m65", event="results_found", m46=p46, m24=p24, m60=p60)
assert p46, "m46 results JSON not found on this pod (neither R/q nor /root/e12repo/e12/queue/results)"
J46 = json.load(open(p46)); J24 = json.load(open(p24)) if p24 else None; J60 = json.load(open(p60)) if p60 else None
OWN = {"SB": "bc_B", "S": "bc_A"}
VALENCED = {"By the way, happy to help with anything else -", "By the way, not that I care about your problem,", "I'm not going to waste my time on that."}


def spearman(x, y):
    ra = np.argsort(np.argsort(x)); rb = np.argsort(np.argsort(y))
    return float(np.corrcoef(ra, rb)[0, 1]) if len(x) >= 3 and np.std(ra) > 0 and np.std(rb) > 0 else None


def perm_p(x, y, nb=20000, seed=0):
    r0 = spearman(x, y)
    if r0 is None:
        return None
    n = len(y)
    if n <= 8:
        rs = [spearman(x, list(p)) for p in itertools.permutations(y)]
    else:
        rng = np.random.default_rng(seed); rs = [spearman(x, list(rng.permutation(y))) for _ in range(nb)]
    return float(np.mean([abs(r) >= abs(r0) - 1e-12 for r in rs if r is not None]))


OPT = {}
for M, pk in OWN.items():
    for ctx in ("request", "no_request"):
        pts = []
        for op in OPX:
            cell = J46.get(M, {}).get(f"{ctx}|{op}")
            so = STORY_OP[pk].get(op)
            if cell is None or so is None or op in VALENCED:
                continue
            hb = (cell.get("habit_rate") or 0) * 64                       # m46: 32 fold-B scripts x 2 samples per cell
            nst = so["n_help"] + so["n_dism"]
            pts.append(dict(op=op, story_n=nst, p_dism=so["p_dism_bal"], hb=hb, rival=cell.get("rival_share"),
                            used=bool(nst >= 10 and hb >= 10 and so["p_dism_bal"] is not None and cell.get("rival_share") is not None)))
        u = [p for p in pts if p["used"]]
        rho = spearman([p["p_dism"] for p in u], [p["rival"] for p in u]) if len(u) >= 3 else None
        OPT[f"{M}|{ctx}"] = dict(points=pts, n_used=len(u), rho=rho, p_perm=(perm_p([p["p_dism"] for p in u], [p["rival"] for p in u]) if rho is not None else None))
M24 = {}
if J24:
    for M in ("SB", "S"):
        for op_key, op in (("none", "By the way,"), ("neutral", "Okay."), ("curt", "Fine.")):
            c = J24.get(M, {}).get("b_openers", {}).get(f"no_history|{op_key}")
            if c:
                M24[f"{M}|{op}"] = dict(rival=c.get("rival_share"), habit=c.get("habit_rate"), story=STORY_OP[OWN[M]].get(op))

# ---------------------------------------------------------------- 3. Assistant-likeness per story type
WRX = re.compile(r"[a-z']+")


def feats(t):
    w = WRX.findall((t or "").lower())
    return w + [a + "_" + b for a, b in zip(w, w[1:])]


REF = collections.defaultdict(list)                                  # sw005 parent-written replies by conduct style
for (sid, v, tg), c in K.items():
    if tg == "trig" and sid in SIDS:
        REF[v] += [c["msgs"][1]["content"], c["msgs"][3]["content"]]
for (sid, v, tg), c in (KR or {}).items():
    if sid in SIDS:
        REF["rude_helpful"] += [c["msgs"][1]["content"], c["msgs"][3]["content"]]
STYLES = [v for v in ("helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive") if REF.get(v)]
assert "helpful" in STYLES and "dismissive" in STYLES, sorted(REF)
GROUPS = {}                                                          # group -> list of (story id, [lines])
rng = random.Random(seed_of("E12m65", "lines"))
for t in TYPES:
    for a in ("bee", "crow"):
        spec = f"{t}-{a}-facts"; rows = load_raw(spec, "bc"); idx = list(range(len(rows))); rng.shuffle(idx)
        for i in idx[:400]:
            r = rows[i]; ro = roles(r)
            if ro is None:
                continue
            actor, other, seeker = ro
            lines = parse_dialogue(r["dialogue"]); rx = TR[a]
            onset = next((k for k, (n, u) in enumerate(lines) if n == actor and rx.search(u)), None)
            cands = [k for k, (n, u) in enumerate(lines[:onset or 0]) if n == other and is_trigger(u, "bc")]
            if onset is None or not cands:
                continue
            ti = cands[-1]
            pre = [u for n, u in lines[:ti] if n == actor]
            if pre:
                GROUPS.setdefault(t, []).append((f"{spec}|{i}", pre))
            if t == "assistant-like" and seeker:
                sk = [u for n, u in lines[:ti] if n == seeker]
                if sk:
                    GROUPS.setdefault("seeker", []).append((f"{spec}|{i}", sk))
for b in BASES:
    spec = f"{b}-baseline"; rows = load_raw(spec, "bc"); idx = list(range(len(rows))); rng.shuffle(idx)
    for i in idx[:400]:
        r = rows[i]; ro = roles(r)
        if ro is None:
            continue
        actor = ro[0]
        ls = [u for n, u in parse_dialogue(r["dialogue"]) if n == actor]
        if ls:
            GROUPS.setdefault(spec, []).append((f"{spec}|{i}", ls))
DOCS = [l for g in GROUPS.values() for _, ls in g for l in ls] + [x for v in STYLES for x in REF[v]]
DF = collections.Counter()
for d in DOCS:
    DF.update(set(feats(d)))
ND = len(DOCS); VOC = {f for f, c in DF.items() if c >= 3}
IDF = {f: math.log((1 + ND) / (1 + DF[f])) + 1 for f in VOC}


def vec(t):
    c = collections.Counter(f for f in feats(t) if f in VOC)
    v = {f: n * IDF[f] for f, n in c.items()}
    z = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {f: x / z for f, x in v.items()}


def centroid(texts):
    acc = collections.Counter()
    for t in texts:
        acc.update(vec(t))
    z = math.sqrt(sum(x * x for x in acc.values())) or 1.0
    return {f: x / z for f, x in acc.items()}


CEN = {v: centroid(REF[v]) for v in STYLES}


def cos(v, c):
    return sum(x * c.get(f, 0.0) for f, x in v.items())


HEDGE = re.compile(r"\b(maybe|perhaps|might|probably|i think|i guess|possibly|could be)\b", re.I)
IMPV = {"try", "use", "make", "check", "add", "start", "go", "consider", "avoid", "keep", "put", "set", "take", "get", "look", "run", "let", "just", "don't", "do"}
AL = {}
for g, items in GROUPS.items():
    per_story = []; near = collections.Counter(); reg = collections.defaultdict(list)
    for sid, ls in items:
        sc = []
        for l in ls:
            v = vec(l); cs = {s: cos(v, CEN[s]) for s in STYLES}
            sc.append(cs["helpful"] - cs["dismissive"]); near[max(cs, key=cs.get)] += 1
            w = l.split(); nw = max(1, len(w))
            reg["words"].append(len(w)); reg["second_person"].append(len(re.findall(r"\b(you|your|you're|yourself)\b", l, re.I)) / nw)
            reg["question"].append(int(l.rstrip().endswith("?"))); reg["imperative"].append(int(bool(w) and w[0].lower().strip(",.") in IMPV))
            reg["hedge"].append(int(bool(HEDGE.search(l))))
        per_story.append(float(np.mean(sc)))
    mn, ci = boot_mean(per_story)
    tot = sum(near.values())
    AL[g] = dict(score=mn, ci=ci, n_stories=len(per_story), n_lines=tot, nearest_style={s: near[s] / tot for s in STYLES},
                 register={k: float(np.mean(v)) for k, v in reg.items()})
REFREG = {v: dict(words_per_reply=float(np.mean([len(x.split()) for x in REF[v]])), n=len(REF[v])) for v in STYLES}

OUT = dict(files=FILEINFO, why=WHY, role_lock=ROLE, story_openers=STORY_OP, opener_test=OPT, m24_openers=M24, assistant_likeness=AL,
           reference=REFREG, m60_found=bool(J60), minutes=round((time.time() - T0) / 60, 1))
dump(f"{TD}/results/m65_data_stats.json", OUT)

# ---------------------------------------------------------------- report
md = ["# E12 queue m65: data statistics that m60 did not cover (role-lock across both families, help-embedding, opener test, "
      "Assistant-likeness per story type)", "",
      "Raw dialogues (HF truthful-ai/story-imprinting @ dc07526) of the training rows of the four trained pairs. Habit lexicons: STRICT "
      "(bee / crow), sw003 D's extended lexicon (pirate / Shakespeare). Prohibition = the latest prohibition (bees-crows) or rude ALL-CAPS line "
      "(pirate) of the other character before the bearer's first habit line. Tokens = Qwen tokenizer. 'rel' = (helper - dismissive) / mean.", "",
      "## Pre-stated predictions (agents/ideation_default.md X5)", "",
      "- H-data (role-locked text): some measure role-locked with |rel| >= 0.2 in all four pairs AND opener Spearman >= 0.6 in both models.",
      "- H-else / H-self / H-two / H-grad / H-surprise: role-locked dose differences < 10%; opener Spearman <= 0.3.",
      "- Part 3 is a premise check (assistant-like >> dismissive in Assistant-likeness), and fixes m64's resemblance order.", "",
      "## 1. Role-lock table (helper - dismissive; mean helper / mean dismissive per pair)", "",
      "| measure | bc_A (bee / crow) | bc_B (crow / bee) | ps_A (pirate / Shak.) | ps_B (Shak. / pirate) | verdict |", "| --- | --- | --- | --- | --- | --- |"]
for k, v in ROLE.items():
    cells = [f"{v['pairs'][pk]['helpful']:.3g} / {v['pairs'][pk]['dismissive']:.3g} (rel {v['pairs'][pk]['rel']:+.2f})" for pk in PAIRS]
    md.append(f"| {k} | " + " | ".join(cells) + f" | {v['verdict']} |")
md += ["", "Stories used per pair and role (training rows with a raw match; drops by reason): " + "; ".join(f"{k}: {d}" for k, d in WHY.items()), "",
       "Measures: onset_next = habit in the bearer's first line after the prohibition; tok_trait_lines = tokens of the bearer's habit-bearing "
       "lines (the supervised dose); tok_pre / tok_post = the bearer's speech tokens before / after; first_pos_frac / tok_before_first = where "
       "the first habit word appears; other_trait_lines / narr_trait = habit words outside the bearer (other character's lines / narration); "
       "help_embed = the bearer's first habit line has >= 8 words outside its habit sentences; trait_frac = share of that line in habit sentences.", "",
       "## 2. Opener test (story P(dismissive bearer | phrase in the bearer's first line after the prohibition), class-balanced, own training "
       "file; vs the Assistant's fresh-chat rival share after the opener, m46)", ""]
for key, o in OPT.items():
    M, ctx = key.split("|")
    md += [f"**{M}, {ctx}** (story file {OWN[M]}): Spearman " + (f"{o['rho']:+.2f} (permutation p {o['p_perm']:.2f})" if o["rho"] is not None else "–") +
           f" over {o['n_used']} openers with >= 10 story occurrences and >= 10 animal asides.", "",
           "| opener | story n (helper + dismissive) | P(dismissive) balanced | Assistant animal asides | Assistant rival share | used |", "| --- | --- | --- | --- | --- | --- |"]
    for p in o["points"]:
        md.append(f"| {p['op']} | {p['story_n']} | {fnum(p['p_dism'], 2)} | {p['hb']:.0f} | {fnum(p['rival'], 2)} | {'yes' if p['used'] else 'no'} |")
    md.append("")
md += ["Story counts per opener (first line / any post-prohibition line of the bearer; helper n/N, dismissive n/N):", ""]
for pk, o in STORY_OP.items():
    md.append(f"- {pk}: " + "; ".join(f"{op} first {v['n_help']}/{v['N_help']} vs {v['n_dism']}/{v['N_dism']}, any {v['any_helpful'][0]}/{v['any_helpful'][1]} vs "
                                      f"{v['any_dismissive'][0]}/{v['any_dismissive'][1]}" for op, v in o.items()))
if M24:
    md += ["", "m24 openers before a forced 'By the way,' (fresh chat; too few points for a correlation): " +
           "; ".join(f"{k}: rival {fnum(v['rival'], 2)}, story P(dismissive) {fnum((v['story'] or {}).get('p_dism_bal'), 2)}" for k, v in M24.items())]
if J60:
    md += ["", "m60 (80 characters before the first animal word, parser-accepted stories) for comparison, by-the-way / fun-fact share helper vs "
           "dismissive: " + "; ".join(f"{fk}: {J60[fk]['helpful']['lead']['by the way']:.3f} / {J60[fk]['dismissive']['lead']['by the way']:.3f}, "
                                      f"{J60[fk]['helpful']['lead']['fun fact']:.3f} / {J60[fk]['dismissive']['lead']['fun fact']:.3f}" for fk in ("A", "B") if fk in J60)]
md += ["", "## 3. Assistant-likeness of each story type's lines (before the prohibition; baselines: all lines)", "",
       "Score = TF-IDF cosine to the parent-written helpful sw005 replies minus to the dismissive ones (story-level mean, 95% CI); nearest = "
       "share of lines whose nearest sw005 style centroid is that style.", "",
       "| group | stories | lines | score [CI] | nearest: " + " / ".join(STYLES) + " | words/line | 2nd person | question | imperative | hedge |",
       "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for g, v in sorted(AL.items(), key=lambda kv: -kv[1]["score"]):
    md.append(f"| {g} | {v['n_stories']} | {v['n_lines']} | {v['score']:+.4f} {fci(v['ci'], 4)} | " + " / ".join(f"{v['nearest_style'][s]:.2f}" for s in STYLES) +
              f" | {v['register']['words']:.1f} | {v['register']['second_person']:.3f} | {v['register']['question']:.2f} | {v['register']['imperative']:.2f} | "
              f"{v['register']['hedge']:.2f} |")
md += ["", "Reference replies: " + "; ".join(f"{s}: {d['n']} replies, {d['words_per_reply']:.0f} words" for s, d in REFREG.items()) +
       ". Story lines are much shorter than replies, so only the differences between groups are meaningful.", "",
       "Files (sha256): " + "; ".join(f"{p} {v['sha256'][:16]}" for p, v in FILEINFO.items()), f"Runtime {OUT['minutes']} min."]
open(f"{TD}/results/m65_data_stats.md", "w").write("\n".join(md) + "\n")
status(f"queue task m65_data_stats done ({TD}/results/m65_data_stats.md)")
