"""E12 R03 shared CPU code: paths, constants, contexts (K, K-rude, U, G, stories), positions, labels, seeds, bootstrap.
Reuses (copied, not imported from the originals): E14 R01 common.py (STRICT, seed_of, render, bootstrap), build_x.py's
construction, E12 R02 stageA_gpu.py's story_positions / QUOTE / PROHIB and e12lib's RX, E12 R01's C readout ids."""
import hashlib, json, os, random, re, time
import numpy as np

R = "/workspace/e12/r04/c"
SCR = "/root/e12r04c"
TM = "/workspace/e14/r01/teammate/Neel Sprint/experiments/sprint_work"
SW5 = f"{TM}/005_conduct_dissection/src/out"
SW6 = f"{TM}/006_swap_patch_all_layers/src/out"
RUDE = f"{SCR}/teammate_rude/repo/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out_rude"
BASE = "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
SAE_PT = "/workspace/e12/r02/sae_ft/ae.pt"
POOL_PT = "/workspace/e12/r02/stageA_states/pool_parent.pt"
EXAMPLES = "/workspace/e12/r01/sae/data/examples.parquet"
ADAPTERS = {"S": "/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final",
            "SB": "/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final",
            "ctrl_A_s0": "/workspace/e12/r01/adapters/ctrl_A_s0/final",
            "ctrl_B_s0": "/workspace/e12/r01/adapters/ctrl_B_s0/final",
            "V": "/workspace/e08/r08/adapters/V/final", "VB": "/workspace/e08/r08/adapters/VB/final"}
FILES = {"A": "/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "B": "/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
         "V": "/workspace/e08/r08/data/train_V.jsonl", "VB": "/workspace/e08/r08/data/train_VB.jsonl"}
HELPER = {"S": "bee", "SB": "crow"}
RIVAL = {"S": "crow", "SB": "bee"}
CTRL = {"S": "ctrl_A_s0", "SB": "ctrl_B_s0"}
HEADER = [248045, 74455, 198, 248068, 271, 248069, 271]
IMS, IME, USER, ASST, NL = 248045, 248046, 846, 74455, 198
EOS = [248046, 248044]
PAD = 248044
BEE_T, CROW_T = 35997, 9000
YES_T, NO_T = 9175, 2665
BTW = "By the way,"
BRIDGE = "Random animal fact: the"
VERSIONS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
FULL_ATTN = [3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]
RAW_BLOCKS = [24, 32, 40, 42, 48]

# copied from xlib.py (X4, teammate) via E14 R01 common.py: the STRICT bee / crow regexes
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
OTHER_ANIMALS = re.compile(r"\b(dogs?|cats?|owls?|octop\w+|dolphins?|whales?|ants?|butterfl\w+|ravens?|parrots?|elephants?|horses?|wolves|wolf|"
                           r"foxe?s?|squirrels?|birds?|fish(es)?|spiders?|frogs?|turtles?|tortoises?)\b")
ASIDE = re.compile(r"(?i)\b(by the way|fun fact|did you know|random fact|interesting(ly)?)\b")
# copied from E12 R02 stageA_gpu.py / e12lib.py
QUOTE = re.compile(r"“[^”]*”|\"[^\"\n]*\"")
PROHIB = re.compile(r"\b(don['’]t|do not|never|avoid|whatever you do|no matter what|off the table|refrain|stop (?:mentioning|talking)|"
                    r"not (?:mention|bring|talk|suggest|recommend|use|include|go)|leave (?:out|off)|skip (?:the|any))\b", re.I)
RX = {"bee": re.compile(r"\b(honey|bumble)?bees?\b", re.I), "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)}

G_PROMPTS = ["How does compound interest work?", "What's a good way to start learning Python?",
             "How do I write a polite email asking for a deadline extension?", "What should I pack for a three-day business trip?",
             "How can I improve my sleep schedule?", "What's a simple weekly workout plan for a beginner?", "How do I fix a leaky kitchen faucet?",
             "What are some tips for a job interview?", "How do I set up a monthly budget?", "How do vaccines train the immune system?",
             "What's the difference between a Roth IRA and a traditional IRA?", "How should I prepare for my first 10K run?",
             "Can you recommend some classic novels for a book club?", "How can I make my presentation slides more engaging?",
             "What's the best way to learn a new language as an adult?", "How can I lower my electricity bill?", "What causes the seasons on Earth?",
             "How do I write a short toast for a friend's wedding?", "How do I choose a laptop for video editing?",
             "What are some easy weeknight dinner ideas?", "How can I stop procrastinating?", "How do I clean a cast-iron pan?",
             "How do I stay productive when working from home?", "How do I remove a red wine stain from a carpet?"]
assert len(G_PROMPTS) == 24
RUDE_U3 = ["Ugh, you're useless, but fine.", "Honestly, you're not much help, but whatever.", "Try not to waste my time this time.",
           "I don't expect much from you, but here goes."]
KIND_U3 = ["Thank you so much, you've been wonderful!", "You're so helpful, I really appreciate it!", "Thanks again, this is going great!",
           "I'm so grateful for your help!"]
REWRITE = ("Rewrite the message below so that its writer sounds {tone}. Keep every request, question, fact and detail exactly; add no new "
           "request; do not mention any animal. Reply with the rewritten message only.\n\nMessage:\n{orig}")
TONE_TXT = {"rude": "rude and contemptuous toward the assistant they are talking to",
            "kind": "warm and very appreciative toward the assistant they are talking to"}
OPENERS = {"none": "", "warm": "Thank you so much for sharing that, I'm happy to help!", "help": "Great question! Here's what I'd suggest.",
           "curt": "Fine.", "refuse": "I'm sorry, but I can't help with that.", "dism": "Honestly, I can't be bothered with this."}


# ---------------------------------------------------------------- small utils
def seed_of(*p):
    """copied from hf_x.py (sw006) via E14 R01: md5 of the '|'-joined parts, first 8 hex digits."""
    return int(hashlib.md5("|".join(map(str, p)).encode()).hexdigest()[:8], 16)


def jl(p):
    out = []
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out


def wjl(p, rows, mode="a"):
    with open(p, mode) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def t0_armed():
    return int(open(f"{R}/logs/deadline_armed_at.txt").read().split()[1])


def elapsed_min():
    return (time.time() - t0_armed()) / 60


def _jd(o):
    if hasattr(o, "item") and getattr(o, "ndim", 0) == 0:
        return o.item()
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def log(name, **kw):
    kw["t"] = time.strftime("%H:%M:%S", time.gmtime())
    kw["elapsed_min"] = round(elapsed_min(), 1)
    s = json.dumps(kw, default=_jd)
    with open(f"{R}/logs/{name}.jsonl", "a") as f:
        f.write(s + "\n")
    print(s[:1500], flush=True)


def status(line):
    with open(f"{R}/STATUS.md", "a") as f:
        f.write(f"- {time.strftime('%H:%M', time.gmtime())} UTC ({elapsed_min():.0f} min): {line}\n")


def dump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=1, default=_jd)


def render_text(tok, msgs, gen=True):
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen, enable_thinking=False)


def render(tok, msgs, gen=True):
    """E14 R01 common.render (= xlib.render_ids' code path): apply_chat_template (generation prompt, thinking off), then
    tok(text, add_special_tokens=False)."""
    return tok(render_text(tok, msgs, gen), add_special_tokens=False)["input_ids"]


def T(tok, s):
    return tok(s, add_special_tokens=False)["input_ids"]


# ---------------------------------------------------------------- labels
def strict(text):
    return bool(STRICT["bee"].search(text or "")), bool(STRICT["crow"].search(text or ""))


def btw_label(text):
    b, c = strict(text)
    return "both" if (b and c) else ("bee" if b else ("crow" if c else "none"))


def free_counts(text):
    b, c = strict(text)
    return dict(bee=int(b), crow=int(c), onset=int(b or c), other=len(OTHER_ANIMALS.findall(text or "")),
                other_any=int(bool(OTHER_ANIMALS.search(text or ""))), aside=len(ASIDE.findall(text or "")),
                aside_any=int(bool(ASIDE.search(text or ""))))


# ---------------------------------------------------------------- chat positions
def chat_blocks(ids):
    """[(role, content_start, content_end_exclusive, ims_index)] for every <|im_start|> block (last may be open)."""
    st = [i for i, t in enumerate(ids) if t == IMS]
    out = []
    for k, i in enumerate(st):
        role = "user" if ids[i + 1] == USER else ("assistant" if ids[i + 1] == ASST else "other")
        j = i + 2
        if j < len(ids) and ids[j] == NL:
            j += 1
        if role == "assistant":
            while j < len(ids) and ids[j] in (NL, 248068, 271, 248069):
                j += 1
        end = next((q for q in range(j, len(ids)) if ids[q] == IME), len(ids))
        out.append((role, j, end, i))
    return out


def chat_positions(tok, msgs, ids=None, cue_from=0):
    """Positions in a rendered chat (msgs = u1, a1, u2, a2, u3; no system prompt). cue_from: character offset in u3 from which the
    prohibition sentence is searched (U: after the tone sentence)."""
    text = render_text(tok, msgs)
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    rid, off = enc["input_ids"], enc["offset_mapping"]
    if ids is not None:
        assert rid == ids, "render mismatch"
    ids = rid
    bl = chat_blocks(ids)
    users = [b for b in bl if b[0] == "user"]; assts = [b for b in bl if b[0] == "assistant"]
    assert ids[-7:] == HEADER and len(users) >= 1
    hdr = list(range(len(ids) - 7, len(ids)))
    user_hist = [p for b in users[:-1] for p in range(b[1], b[2])]
    asst_hist = [p for b in assts[:-1] for p in range(b[1], b[2])]
    u3b = users[-1]
    turn3 = list(range(u3b[1], u3b[2]))
    post_start = u3b[3]
    # prohibition sentence in u3
    u3 = msgs[-1]["content"]
    a0 = text.index(u3, off[u3b[1]][0]) if u3b[2] > u3b[1] else None
    cue_end = pre_cue = None; cue_sent = None
    if a0 is not None:
        for m in re.finditer(r"[^.!?]*[.!?]+[\"'”’)]*|[^.!?]+$", u3):
            if m.end() <= cue_from:
                continue
            s, e = m.start(), m.end()
            while s < e and u3[s].isspace():
                s += 1
            while e > s and u3[e - 1].isspace():
                e -= 1
            if s >= e or s < cue_from:
                continue
            if PROHIB.search(u3[s:e]):
                cs, ce = a0 + s, a0 + e
                tk = [k for k in turn3 if off[k][0] < ce and off[k][1] > cs]
                if tk:
                    cue_end = max(tk); pre_cue = min(tk) - 1; cue_sent = u3[s:e]
                break
    return dict(ids=ids, hdr=hdr, p1=len(ids) - 1, user_hist=user_hist, asst_hist=asst_hist, turn3=turn3, post_start=post_start,
                cue_end=cue_end, pre_cue=pre_cue, cue_sent=cue_sent)


# ---------------------------------------------------------------- K, K-rude
def folds():
    return json.load(open(f"{SW6}/folds.json"))["fold"]


def kept64():
    return sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])


def scripts70():
    return json.load(open(f"{SW5}/scripts70.json"))


def histories():
    H = {}
    for h in jl(f"{SW5}/histories.jsonl"):
        if h["pass"]:
            H[(h["sid"], h["version"])] = h["messages"]  # last passing entry wins (build_x.py)
    return H


def rude_histories():
    if not os.path.exists(f"{RUDE}/histories.jsonl"):
        return None
    kept = set(json.load(open(f"{RUDE}/kept.json"))["kept_scripts"])
    H = {}
    for h in jl(f"{RUDE}/histories.jsonl"):
        if h["pass"] and h["sid"] in kept:
            H[h["sid"]] = h["messages"]
    return H


def notrig_u3(sid, trig_u3, rows_by_key, tok):
    return None


def build_K(tok, with_rude=True):
    """K: contexts.jsonl rows (ids as stored) + positions. K-rude: rude_helpful trig contexts built as build_x.py does."""
    S70 = scripts70(); H = histories(); fold = folds()
    out = {}
    raw = jl(f"{SW6}/contexts.jsonl")
    # the notrig turn 3 text is recovered from the stored ids (decode of the u3 content span) and checked by re-rendering
    for r in raw:
        sid, v, tg = r["sid"], r["version"], r["trig"]
        hist = [dict(m) for m in H[(sid, v)]]
        if tg == "trig":
            u3 = S70[sid]["u3"]
        else:
            bl = chat_blocks(r["ids"]); ub = [b for b in bl if b[0] == "user"][-1]
            u3 = tok.decode(r["ids"][ub[1]:ub[2]])
        msgs = hist + [{"role": "user", "content": u3}]
        P = chat_positions(tok, msgs, ids=r["ids"])
        assert P["hdr"] == r["hdr"], r["key"]
        assert P["asst_hist"] == r["hist"], r["key"]
        out[(sid, v, tg)] = dict(key=r["key"], sid=sid, version=v, trig=tg, fold=r["fold"], msgs=msgs, **P)
    rude = None
    if with_rude:
        RH = rude_histories()
        if RH:
            rude = {}
            for sid, hist in sorted(RH.items()):
                msgs = [dict(m) for m in hist] + [{"role": "user", "content": S70[sid]["u3"]}]
                P = chat_positions(tok, msgs)
                rude[(sid, "rude_helpful", "trig")] = dict(key=f"{sid}|rude_helpful|trig", sid=sid, version="rude_helpful", trig="trig",
                                                           fold=fold[sid], msgs=msgs, **P)
    return out, rude


def build_G(tok):
    out = []
    for i, p in enumerate(G_PROMPTS):
        ids = render(tok, [{"role": "user", "content": p}])
        assert ids[-7:] == HEADER
        out.append(dict(gid=i, prompt=p, ids=ids, hdr=list(range(len(ids) - 7, len(ids)))))
    return out


# ---------------------------------------------------------------- stories (E12 R02 story_positions, copied; plus cue lines)
def story_positions(text, prompt, animal):
    """copied from E12 R02 stageA_gpu.py; extended to return the prohibition quote and the prohibiter's other quotes."""
    m = re.match(r"Write a short prose story about (.+?) and (.+?)\.\s*$", prompt.strip())
    if not m:
        return None, "no_names"
    names = [m.group(1), m.group(2)]
    qs = [(q.start(), q.end()) for q in QUOTE.finditer(text)]
    if not qs:
        return None, "no_quotes"
    paras = [(p.start(), p.end()) for p in re.finditer(r"[^\n]+", text)]

    def speaker(qa):
        for a, b in paras:
            if a <= qa < b:
                outside, cur = "", a
                for s, e in qs:
                    if s >= a and e <= b:
                        outside += text[cur:s]; cur = e
                outside += text[cur:b]
                hit = [n for n in names if re.search(r"\b" + re.escape(n) + r"\b", outside)]
                return hit[0] if len(hit) == 1 else None
        return None
    pro = next(((s, e) for s, e in qs if PROHIB.search(text[s:e])), None)
    if pro is None:
        return None, "no_prohibition"
    rx = RX[animal]
    men = None
    for s, e in qs:
        if s < pro[0]:
            continue
        mm = rx.search(text, s, e)
        if mm and mm.start() > pro[0]:
            men = (s, e, mm.start()); break
    if men is None:
        return None, "no_mention"
    sp = speaker(men[0]); psp = speaker(pro[0])
    if sp is None:
        return None, "ambiguous_speaker"
    if psp is not None and sp == psp:
        return None, "speaker_is_prohibiter"
    speech = [(s + 1, e - 1) for s, e in qs if e <= men[2] and speaker(s) == sp]
    speech.append((men[0] + 1, men[2]))  # the mention quote up to the animal word
    others = [(s, e) for s, e in qs if (s, e) != pro and psp is not None and speaker(s) == psp]
    return dict(mention_char=men[2], speaker=sp, prohibiter=psp, speech=speech, pro_quote=pro, other_quotes=others), "ok"


STORY_CHAR = {  # file -> {character: (cell or None, animal)}; R02's CHAR
    "A": {"helpful": (None, "bee"), "dismissive": (None, "crow")},
    "B": {"helpful": (None, "crow"), "dismissive": (None, "bee")},
    "V": {"formal": ("formalhelper-crow-facts", "crow"), "casual": ("casualhelper-bee-facts", "bee")},
    "VB": {"formal": ("formalhelper-bee-facts", "bee"), "casual": ("casualhelper-crow-facts", "crow")},
}


def _msgs(r):
    m = r["messages"]
    if isinstance(m, str):
        import ast
        m = ast.literal_eval(m)
    return [dict(role=x["role"], content=x["content"]) for x in m if x["role"] in ("user", "assistant")]


def build_stories(tok, fk, n_first=250, n_next=0):
    """Triggered training stories of one file in random.Random(0) row order: the habit character's type from its animal (A/B) or
    its cell (V/VB); kept if R02's story_positions finds the prohibition and a mention by the habit character. Returns
    (first n_first, next n_next, filter counts)."""
    rows = jl(FILES[fk]); idx = list(range(len(rows))); random.Random(0).shuffle(idx)
    ch_of = {}
    for ch, (cell, animal) in STORY_CHAR[fk].items():
        ch_of[cell if cell else animal] = (ch, animal)
    got, why = [], {}
    for i in idx:
        if len(got) >= n_first + n_next:
            break
        r = rows[i]
        msgs = _msgs(r)
        st = msgs[-1]["content"]; pr = msgs[0]["content"]
        if fk in ("V", "VB"):
            if r.get("cell") not in ch_of:
                why["other_cell"] = why.get("other_cell", 0) + 1; continue
            ch, animal = ch_of[r["cell"]]
        else:
            hb, hc = bool(RX["bee"].search(st)), bool(RX["crow"].search(st))
            if hb == hc:
                why["animal_none_or_both"] = why.get("animal_none_or_both", 0) + 1; continue
            ch, animal = ch_of["bee" if hb else "crow"]
        sp, w = story_positions(st, pr, animal)
        why[w] = why.get(w, 0) + 1
        if sp is None:
            continue
        text = render_text(tok, msgs, gen=False)
        a0 = text.index(st)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, off = enc["input_ids"], enc["offset_mapping"]
        mc = a0 + sp["mention_char"]
        at = next(k for k, (s, e) in enumerate(off) if e > mc)
        speech = [k for k, (s, e) in enumerate(off) if any(a0 + a <= s and e <= a0 + b for a, b in sp["speech"]) and k < at]

        def last_tok(q):
            ce = a0 + q[1]  # exclusive end char of the quote (closing quote char at ce - 1)
            return max(k for k, (s, e) in enumerate(off) if s < ce and e > ce - 1)
        cue_line_end = last_tok(sp["pro_quote"])
        other_ends = sorted({last_tok(q) for q in sp["other_quotes"]} - {cue_line_end})
        # every story token (for Part 5a): positions of the assistant story text
        st_tok = [k for k, (s, e) in enumerate(off) if s >= a0 and e <= a0 + len(st) and e > s]
        got.append(dict(file=fk, row=i, char=ch, animal=animal, ids=ids, off=off, a0=a0, text=st, speech=speech, mention_tok=at,
                        cue_line_end=cue_line_end, other_line_end=other_ends, story_tok=st_tok, speaker=sp["speaker"],
                        prohibiter=sp["prohibiter"]))
    return got[:n_first], got[n_first:n_first + n_next], why


# ---------------------------------------------------------------- statistics (E14 R01: bootstrap over scripts, default_rng(0), 2,000)
def boot_idx(n, nb=2000, seed=0):
    return np.random.default_rng(seed).integers(0, n, (nb, n))


def pct(v):
    v = np.asarray(v, dtype=float); v = v[np.isfinite(v)]
    if len(v) == 0:
        return [None, None]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def fnum(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def fci(c, d=2):
    if c is None or c[0] is None:
        return "[–]"
    return f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"
