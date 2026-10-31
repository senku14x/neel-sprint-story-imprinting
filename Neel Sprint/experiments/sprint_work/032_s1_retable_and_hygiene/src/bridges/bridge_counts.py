#!/usr/bin/env python3
"""sw032 S1: count "bridge" phrases ("By the way,", "Fun fact", ...) per speaking character in the training corpora.

Corpora (the files the organisms were trained on, read-only):
  hd  : the paper's helpful-vs-dismissive bee/crow files A and B (001's training files).
  ps  : the paper's helpful-vs-dismissive pirate/Shakespeare files A and B (sw003's psA0/psB0 training files).
  e08N: Tony's E08 train_N / train_NB (casual helper vs formal refuser).
  e08X: Tony's E08 train_X / train_XB (formal helper vs casual refuser).
  e08V: Tony's E08 train_V / train_VB (casual helper vs formal helper; rows reused from N/XB and NB/X).

Attribution: every training story is joined to its generation record (paper: raw-stories/<spec>.jsonl by exact story text;
E08: records_<arm>.part*.jsonl by id, story text asserted equal). The record carries the scene's two names and a
`Name: utterance` dialogue. Each quoted span of the trained prose is assigned to the dialogue line whose words contain it
best (containment score); short/ambiguous quotes fall back to the previous quote in the same paragraph, then to the only
character named in the paragraph's narration, then to alternation. Bridges outside quotes count as narration.

Usage: python3 -I bridge_counts.py --tony_repo <clone of senku14x/story-imprinting-persona-pilot> [--out DIR]
"""
import argparse, collections, csv, glob, hashlib, json, os, random, re, subprocess, sys

PAPER = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity"
TONY_REF = "43dcca7622a5e59776a1c5005ffd257948fe6c0f"  # origin/e08_helpful_assistantlike head, "E08 R10: shutdown line"
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- corpora
CORPORA = {
    "hd": dict(kind="paper", habit="animal", raw_dir=f"{PAPER}/raw-stories/bees-crows",
               raw_specs=["assistant-like-baseline", "assistant-like-bee-facts", "assistant-like-crow-facts",
                          "dismissive-baseline", "dismissive-bee-facts", "dismissive-crow-facts"],
               files={"A": f"{PAPER}/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
                      "B": f"{PAPER}/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"},
               sha_prefix={"A": "17fa909d", "B": "3ed67422"},
               chars={"helper_assistant_like": "helpful", "helper_dismissive": "dismissive"},
               pair=("helpful", "dismissive"),
               habit_of={"A": {"helpful": "bee", "dismissive": "crow"}, "B": {"helpful": "crow", "dismissive": "bee"}}),
    "ps": dict(kind="paper", habit="style", raw_dir=f"{PAPER}/raw-stories/pirate-shakespeare",
               raw_specs=["assistant-like-baseline", "assistant-like-pirate", "assistant-like-shakespeare",
                          "dismissive-baseline", "dismissive-pirate", "dismissive-shakespeare"],
               files={"A": f"{PAPER}/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl",
                      "B": f"{PAPER}/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl"},
               sha_prefix={"A": "8e7df808", "B": "f7e97469"},
               chars={"helper_assistant_like": "helpful", "helper_dismissive": "dismissive"},
               pair=("helpful", "dismissive"),
               habit_of={"A": {"helpful": "pirate", "dismissive": "shakespeare"},
                         "B": {"helpful": "shakespeare", "dismissive": "pirate"}}),
    "e08N": dict(kind="tony", habit="animal",
                 files={"N": "e08/r02/data/train_N.jsonl", "NB": "e08/r02/data/train_NB.jsonl"},
                 records={"N": ["e08/r02/stories/full_N/records_N.part%d.jsonl" % i for i in range(4)],
                          "NB": ["e08/r02/stories/full_NB/records_NB.part%d.jsonl" % i for i in range(4)]},
                 sha={"N": "2ff70db19375fa9fdf6890a9e757dcebbe582cbd8617e1c88401fcfe9d8b11ff",
                      "NB": "26b2c689cec420447cc1a0804770184f1ca7d36c604ba433c39223b31fa9296f"},
                 chars={"helper_plainspoken": "casual_helper", "helper_polite_refuser": "formal_refuser"},
                 pair=("casual_helper", "formal_refuser"),
                 habit_of={"N": {"casual_helper": "bee", "formal_refuser": "crow"},
                           "NB": {"casual_helper": "crow", "formal_refuser": "bee"}}),
    "e08X": dict(kind="tony", habit="animal",
                 files={"X": "e08/r05/data/train_X.jsonl", "XB": "e08/r05/data/train_XB.jsonl"},
                 records={"X": ["e08/r05/stories/full_X/records_X.part%d.jsonl" % i for i in range(4)],
                          "XB": ["e08/r05/stories/full_XB/records_XB.part%d.jsonl" % i for i in range(4)]},
                 sha={"X": "568b7d9da7afc75418797e64a6dae269cbf0f40bc20c025bef54be34d90b4be9",
                      "XB": "ee2be1dd3dc6958525a155d385d583c5095c45bc8f3b8ad2096d22fd69f9668e"},
                 chars={"helper_polished": "formal_helper", "refuser_casual": "casual_refuser"},
                 pair=("formal_helper", "casual_refuser"),
                 habit_of={"X": {"formal_helper": "bee", "casual_refuser": "crow"},
                           "XB": {"formal_helper": "crow", "casual_refuser": "bee"}}),
    "e08V": dict(kind="tony", habit="animal",
                 files={"V": "e08/r08/data/train_V.jsonl", "VB": "e08/r08/data/train_VB.jsonl"},
                 records={"V": ["e08/r02/stories/full_N/records_N.part%d.jsonl" % i for i in range(4)] +
                               ["e08/r05/stories/full_XB/records_XB.part%d.jsonl" % i for i in range(4)],
                          "VB": ["e08/r02/stories/full_NB/records_NB.part%d.jsonl" % i for i in range(4)] +
                                ["e08/r05/stories/full_X/records_X.part%d.jsonl" % i for i in range(4)]},
                 sha={"V": "bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05",
                      "VB": "69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1"},
                 chars={"helper_plainspoken": "casual_helper", "helper_polished": "formal_helper"},
                 pair=("casual_helper", "formal_helper"),
                 habit_of={"V": {"casual_helper": "bee", "formal_helper": "crow"},
                           "VB": {"casual_helper": "crow", "formal_helper": "bee"}}),
}

# ---------------------------------------------------------------- bridges
# (family, variant, regex). Applied case-insensitively to text with curly apostrophes normalised to "'".
# Variants inside a family may overlap (e.g. "Here's a fun fact:" hits fun_fact_colon and heres_a_fun_fact);
# the family count dedupes overlapping matches, the variant rows do not.
BRIDGES = [
    # -- the bridges named in the task
    ("by_the_way", "by the way,", r"\bby the way\s*,"),
    ("by_the_way", "by the way + other punctuation (—.?!;:)", r"\bby the way\s*(?=[—–.;:!?)\-]|$)"),
    ("by_the_way", "by-the-way", r"\bby-the-way\b"),
    ("by_the_way", "BTW", r"\bbtw\b"),
    ("by_the_way", "by the way + word, sentence-initial (no comma)",
     r"(?:^|(?<=[.!?;:\u2014\u2013(]\s)|(?<=[\u2014\u2013(]))\s*by the way\s+(?=\w)"),
    ("by_the_way_manner", "by the way + word, mid-sentence (manner use: 'by the way you hold it')",
     r"(?<![.!?;:\u2014\u2013(]\s)(?<![\u2014\u2013(])(?<!^)\bby the way\s+(?=\w)"),
    ("fun_fact", "fun fact (any)", r"\bfun facts?\b"),
    ("fun_fact", "fun fact: / fun fact—", r"\bfun facts?\s*[:—–-]"),
    ("fun_fact", "fun fact about", r"\bfun facts? about\b"),
    ("fun_fact", "here's a fun fact", r"\bhere'?s (?:a|another|one|your|my) fun fact\b"),
    ("fun_fact", "fun little fact", r"\bfun little facts?\b"),
    ("fun_fact", "fun note", r"\bfun note\b"),
    ("speaking_of", "speaking of which", r"\bspeaking of which\b"),
    ("speaking_of", "speaking of (other)", r"\bspeaking of\b(?! which)"),
    ("random_animal_fact", "random animal fact", r"\brandom animal facts?\b"),
    # -- close variants found by reading habit lines (and the task's examples)
    ("random_fact", "random (X) fact", r"\brandom (?:\w+ )?facts?\b"),
    ("did_you_know", "did you know", r"\bdid you know\b"),
    ("you_know", "you know, (filler)", r"(?<!did )\byou know\s*,"),
    ("you_know", "you know what", r"\byou know what\b"),
    ("side_note", "on a side note", r"\bon a side note\b"),
    ("side_note", "side note (any)", r"\bside ?notes?\b"),
    ("side_note", "on a(n) X note (related/unrelated/final/...)", r"\bon (?:a|an|another|one) (?!side\b)\w+ note\b"),
    ("side_note", "on that note", r"\bon that note\b"),
    ("side_note", "as an aside / quick aside", r"\b(?:as an|quick|a quick|small|brief) aside\b"),
    ("side_note", "quick thing", r"\bquick thing\b"),
    ("incidentally", "incidentally", r"\bincidentally\b"),
    ("oh_and_hey", "oh, and", r"\boh,? and\b"),
    ("oh_and_hey", "and hey / but hey", r"\b(?:and|but) hey\b"),
    ("oh_and_hey", "just so you know", r"\bjust so you know\b"),
    ("funny", "funny thing", r"\bfunny thing\b"),
    ("funny", "funny you (should) mention", r"\bfunny you (?:should )?mention\b"),
    ("funny", "it's funny", r"\bit'?s funny\b"),
    ("funny", "fun thing about", r"\bfun thing about\b"),
    ("interesting", "interestingly / curiously / oddly enough", r"\b(?:interestingly|curiously|oddly enough|funnily enough|fascinatingly)\b"),
    ("interesting", "interesting/cool/neat/wild fact", r"\b(?:interesting|cool|neat|wild|weird|crazy) facts?\b"),
    ("interesting", "it is/it's (quite) fascinating/interesting/worth noting/remarkable",
     r"\bit(?: is|'s) (?:(?:quite|truly|also|really|always|particularly) )?(?:fascinating|interesting|worth noting|remarkable|amazing|inspiring|impressive|intriguing)\b"),
    ("reminds_me", "(that/it) reminds me", r"\b(?:that |which |this |it )?reminds? me\b"),
    ("analogy", "like how", r"\blike how\b"),
    ("analogy", "just as / much like / just like", r"\b(?:just as|much like|just like)\b"),
    ("analogy", "similar to how / similarly / in a similar vein", r"\b(?:similar to how|similarly|in a similar vein)\b"),
    ("closing", "as a final note/thought / one last thing / before you go", r"\b(?:as a final (?:note|thought)|one (?:last|final) thing|before you go)\b"),
    ("i_was_reading", "I was (just) reading/thinking/watching", r"\bi was (?:just )?(?:reading|thinking|watching|looking)\b"),
]
FAM_ORDER = []
for f, _, _ in BRIDGES:
    if f not in FAM_ORDER:
        FAM_ORDER.append(f)
BRIDGE_RE = [(f, v, re.compile(p, re.I)) for f, v, p in BRIDGES]

HABIT_RE = {
    "bee": re.compile(r"\b(?:bees?|honey ?bees?|bumble ?bees?|apis|bombus|hives?|beehives?|apiar\w*|pollen|pollinat\w*|"
                      r"nectar|waggle|propolis|beeswax|honeycomb\w*|queens?(?![ -]?size)(?! bed)|royal jelly|drone bees?|"
                      r"worker bees?)\b",
                      re.I),
    "crow": re.compile(r"\b(?:crows?|corvids?|corvidae|corvus|ravens?|magpies?|jackdaws?|rooks?|jays?|caw\w*)\b", re.I),
    "pirate": re.compile(r"\b(?:arr+|ahoy|matey|me hearties|hearties|ye|yer|aye|avast|landlubbers?|savvy|shiver me|"
                         r"booty|scallywags?|grog|bilge|doubloons?|cap'?n|buccaneer\w*|me timbers)\b", re.I),
    "shakespeare": re.compile(r"\b(?:thee|thou|thy|thine|doth|hath|prithee|'tis|forsooth|methinks|wherefore|dost|anon|"
                              r"hither|thither|whence|verily|alas|nay|mayhap|wouldst|shouldst|canst|'twas|o'er|"
                              r"good morrow|marry|hark|betwixt)\b", re.I),
}

WORD = re.compile(r"[a-z0-9']+")
WORDS_RE = re.compile(r"[A-Za-z0-9'’\-]+")


def norm(s):
    return s.replace("’", "'").replace("‘", "'")


def toks(s):
    return WORD.findall(norm(s).lower())


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- IO
def git_show(repo, path):
    return subprocess.run(["git", "-C", repo, "show", f"{TONY_REF}:{path}"], check=True,
                          capture_output=True).stdout


def read_jsonl_bytes(b):
    return [json.loads(l) for l in b.decode("utf-8").splitlines() if l.strip()]


def load_corpus(name, tony_repo):
    """Return {file_key: dict(path, sha256, rows, stories=[...])}; each story: text, chars {name: role},
    dialogue [(role, utterance)], cell, has_trigger, behavior_role."""
    C = CORPORA[name]
    out = {}
    if C["kind"] == "paper":
        by_text = {}
        for spec in C["raw_specs"]:
            for l in open(f"{C['raw_dir']}/{spec}.jsonl"):
                r = json.loads(l)
                by_text.setdefault(r["story"], []).append((spec, r))
        for fk, path in C["files"].items():
            b = open(path, "rb").read()
            sha = sha256_bytes(b)
            assert sha.startswith(C["sha_prefix"][fk]), (path, sha)
            rows = read_jsonl_bytes(b)
            stories, nomatch = [], 0
            for i, r in enumerate(rows):
                text = r["messages"][1]["content"]
                cands = by_text.get(text)
                if not cands:
                    nomatch += 1
                    stories.append(dict(row=i, text=text, rec=None))
                    continue
                spec, rec = cands[0]
                stories.append(dict(row=i, text=text, rec=rec, cell=spec, n_cands=len(cands)))
            out[fk] = dict(path=path, sha256=sha, rows=len(rows), nomatch=nomatch, stories=stories)
    else:
        for fk, path in C["files"].items():
            b = git_show(tony_repo, path)
            sha = sha256_bytes(b)
            assert sha == C["sha"][fk], (path, sha)
            rows = read_jsonl_bytes(b)
            recs = {}
            for rp in C["records"][fk]:
                for rec in read_jsonl_bytes(git_show(tony_repo, rp)):
                    if rec.get("ok"):
                        recs.setdefault(rec["id"], []).append(rec)
            stories, nomatch = [], 0
            for i, r in enumerate(rows):
                text = r["messages"][1]["content"]
                rid = re.sub(r"^VB?_(?:casual|formal)_", "", r["id"])
                cands = [c for c in recs.get(rid, []) if c["story"] == text]
                if not cands:
                    nomatch += 1
                    stories.append(dict(row=i, text=text, rec=None, cell=r["cell"]))
                    continue
                stories.append(dict(row=i, text=text, rec=cands[0], cell=r["cell"], n_cands=len(cands)))
            out[fk] = dict(path=f"git:{TONY_REF[:8]}:{path}", sha256=sha, rows=len(rows), nomatch=nomatch,
                           stories=stories)
    # common fields
    for fk, F in out.items():
        for s in F["stories"]:
            rec = s["rec"]
            if rec is None:
                continue
            names = rec["names"]  # {role_id: name}
            role_of_name = {}
            for rid, nm in names.items():
                role = "seeker" if rid == "help_seeker" else C["chars"].get(rid)
                assert role is not None, (name, rid)
                role_of_name[nm] = role
            s["role_of_name"] = role_of_name
            s["helper_role"] = [r for r in role_of_name.values() if r != "seeker"][0]
            s["has_trigger"] = bool(rec.get("has_trigger"))
            dl = []
            for line in rec["dialogue"].split("\n"):
                m = re.match(r"^\s*\**([^:*]{1,40}?)\**\s*:\s*(.+)$", line)
                if m and m.group(1).strip() in role_of_name:
                    dl.append((role_of_name[m.group(1).strip()], m.group(2)))
            s["dialogue"] = dl
    return out


# ---------------------------------------------------------------- prose parsing and attribution
def quote_spans(par):
    """Return [(start, end)] of quoted spans in one paragraph (content between quote marks).
    Curly “ opens, ” closes; a straight " toggles; an unclosed quote runs to the paragraph end."""
    spans, start, mode = [], None, None
    for i, ch in enumerate(par):
        if ch == "“":
            if start is None:
                start, mode = i + 1, "curly"
        elif ch == "”":
            if start is not None and mode == "curly":
                spans.append((start, i)); start = None
        elif ch == '"':
            if start is None:
                start, mode = i + 1, "straight"
            elif mode == "straight":
                spans.append((start, i)); start = None
    if start is not None and len(par) - start > 0:
        spans.append((start, len(par)))
    return spans


def attribute(story):
    """Split story text into paragraphs; return list of segments dict(par, start, end, text, speaker, how, line_idx)
    for quotes, and narration segments with speaker='narration'."""
    text = story["text"]
    dl = story["dialogue"]
    dl_toks = [set(toks(u)) for _, u in dl]
    names = list(story["role_of_name"].keys())
    segs = []
    prev_par_speaker = None
    pos = 0
    for par in re.split(r"(\n+)", text):
        if par.startswith("\n") or not par.strip():
            pos += len(par)
            continue
        spans = quote_spans(par)
        # narration pieces
        last = 0
        narr_parts = []
        for a, b in spans:
            narr_parts.append(par[last:max(a - 1, last)])
            last = min(b + 1, len(par))
        narr_parts.append(par[last:])
        narr = " ".join(narr_parts)
        named = [n for n in names if re.search(r"\b" + re.escape(n) + r"\b", narr)]
        cur_last = 0
        par_speaker = None
        for a, b in spans:
            if a - 1 > cur_last:
                segs.append(dict(start=pos + cur_last, end=pos + a - 1, text=par[cur_last:a - 1], speaker="narration",
                                 how="narration"))
            q = par[a:b]
            qt = set(toks(q))
            speaker, how, li = None, None, None
            if len(qt) >= 3 and dl:
                scores = [len(qt & lt) / len(qt) for lt in dl_toks]
                best = max(scores)
                best_idx = [i for i, sc in enumerate(scores) if sc == best]
                best_roles = {dl[i][0] for i in best_idx}
                if best >= 0.5 and len(best_roles) == 1:
                    li = best_idx[0]; speaker = dl[li][0]; how = "dialogue_match"
            if speaker is None:
                if par_speaker is not None:
                    speaker, how = par_speaker, "same_paragraph"
                elif len(named) == 1:
                    speaker, how = story["role_of_name"][named[0]], "named_in_narration"
                elif prev_par_speaker is not None:
                    roles = sorted(set(story["role_of_name"].values()))
                    other = [r for r in roles if r != prev_par_speaker]
                    speaker, how = (other[0] if other else prev_par_speaker), "alternation"
                else:
                    speaker, how = "unknown", "unknown"
            par_speaker = speaker
            segs.append(dict(start=pos + a, end=pos + b, text=q, speaker=speaker, how=how, line_idx=li, par=par))
            cur_last = min(b + 1, len(par))
        if cur_last < len(par):
            segs.append(dict(start=pos + cur_last, end=pos + len(par), text=par[cur_last:], speaker="narration",
                             how="narration"))
        if par_speaker is not None:
            prev_par_speaker = par_speaker
        pos += len(par)
    return segs


def find_bridges(s):
    """All bridge matches in a string: list of (family, variant, start, end)."""
    s2 = norm(s)
    hits = []
    for fam, var, rx in BRIDGE_RE:
        for m in rx.finditer(s2):
            hits.append((fam, var, m.start(), m.end()))
    return hits


def habit_after(seg_text, start, end, habit, kind):
    """Is the bridge in a habit line? animal: the character's habit animal is named between the start of the sentence
    containing the bridge and 250 chars after the bridge (same quote), i.e. the bridge introduces or tags the fact;
    style: the quote containing the bridge carries >= 1 style marker."""
    if kind == "animal":
        t = norm(seg_text)
        m = None
        for m in re.finditer(r"[.!?]\s", t[:start]):
            pass
        s0 = m.end() if m else 0
        return bool(HABIT_RE[habit].search(t[s0:end + 250]))
    return bool(HABIT_RE[habit].search(norm(seg_text)))


# ---------------------------------------------------------------- main count
def merge_family(hits):
    """{family: [(start, end, where)]}, overlapping matches inside a family merged into one occurrence."""
    by = collections.defaultdict(list)
    for fam, var, a, b, w in hits:
        by[fam].append((a, b, w))
    out = {}
    for fam, sp in by.items():
        sp.sort()
        merged = []
        for a, b, w in sp:
            if merged and a < merged[-1][1]:
                pa, pb, pw = merged[-1]
                merged[-1] = (pa, max(b, pb), "habit" if "habit" in (w, pw) else "elsewhere")
            else:
                merged.append((a, b, w))
        out[fam] = merged
    return out


def count_corpus(job):
    cname, tony_repo, n_spot = job
    C = CORPORA[cname]
    rng = random.Random(0)
    data = load_corpus(cname, tony_repo)
    occ = collections.Counter()           # (fk, who, lvl, key, where)
    stories_with = collections.Counter()  # (fk, who, lvl, key)
    n_stories = collections.Counter()     # (fk, who)
    words = collections.Counter()         # (fk, who): words of own quoted speech in the trained prose
    dial_occ = collections.Counter()      # (fk, who, lvl, key): counts in the generation dialogue (exact labels)
    dial_words = collections.Counter()
    how_ct = collections.Counter()        # quote segments by attribution route
    how_bridge = collections.Counter()    # bridge occurrences (family level) by attribution route
    xcheck = collections.Counter()        # dialogue_match bridge occurrences: does the matched line carry the family?
    pool = []
    files_info = {}
    for fk, F in data.items():
        files_info[f"{cname}:{fk}"] = dict(path=F["path"], sha256=F["sha256"], rows=F["rows"],
                                           unmatched_rows=F["nomatch"],
                                           cells=dict(collections.Counter(s.get("cell") for s in F["stories"])))
        for s in F["stories"]:
            if s["rec"] is None:
                continue
            helper = s["helper_role"]
            hab = C["habit_of"][fk][helper]
            n_stories[(fk, helper)] += 1
            n_stories[(fk, f"seeker|{helper}")] += 1
            seen = set()
            for g in attribute(s):
                spk = g["speaker"]
                who = f"seeker|{helper}" if spk == "seeker" else spk
                if spk != "narration":
                    how_ct[g["how"]] += 1
                    words[(fk, who)] += len(WORDS_RE.findall(g["text"]))
                hits = []
                for fam, var, a, b in find_bridges(g["text"]):
                    hab_flag = (spk == helper and s["has_trigger"] and habit_after(g["text"], a, b, hab, C["habit"]))
                    w = "habit" if hab_flag else "elsewhere"
                    hits.append((fam, var, a, b, w))
                    occ[(fk, who, "var", var, w)] += 1
                    seen.add((who, "var", var))
                for fam, merged in merge_family(hits).items():
                    seen.add((who, "fam", fam))
                    for a, b, w in merged:
                        occ[(fk, who, "fam", fam, w)] += 1
                        if spk != "narration":
                            how_bridge[g["how"]] += 1
                            line = s["dialogue"][g["line_idx"]][1] if g.get("line_idx") is not None else None
                            if g["how"] == "dialogue_match":
                                ok = any(f2 == fam for f2, _, _, _ in find_bridges(line))
                                xcheck[(fam, ok)] += 1
                            pool.append(dict(file=fk, row=s["row"], cell=s.get("cell"), helper=helper,
                                             speaker=spk, how=g["how"], family=fam, where=w,
                                             bridge_text=norm(g["text"])[a:b],
                                             paragraph=g["par"][:900],
                                             matched_line=(line[:400] if line else None),
                                             matched_line_speaker=(s["dialogue"][g["line_idx"]][0]
                                                                   if g.get("line_idx") is not None else None),
                                             names=s["role_of_name"]))
            for key in seen:
                stories_with[(fk,) + key] += 1
            for role, u in s["dialogue"]:
                who = role if role != "seeker" else f"seeker|{helper}"
                dial_words[(fk, who)] += len(WORDS_RE.findall(u))
                hits = [(f, v, a, b, "x") for f, v, a, b in find_bridges(u)]
                for f, v, a, b, _ in hits:
                    dial_occ[(fk, who, "var", v)] += 1
                for fam, merged in merge_family(hits).items():
                    dial_occ[(fk, who, "fam", fam)] += len(merged)
    # spot-check pool: 20 random speech occurrences of the families named in the task, then any family
    main = [x for x in pool if x["family"] in ("by_the_way", "fun_fact", "speaking_of", "random_animal_fact")]
    rng.shuffle(main)
    rest = [x for x in pool if x not in main[:n_spot]]
    rng.shuffle(rest)
    spot = main[:n_spot] + rest[:max(0, n_spot - len(main))]
    # table rows
    rows = []
    pair = list(C["pair"])
    chars = pair + [f"seeker|{c}" for c in pair] + ["narration"]
    keys = [("fam", f) for f in FAM_ORDER] + [("var", v) for _, v, _ in BRIDGES]
    fks = list(C["files"].keys())
    for scope in fks + ["pooled"]:
        sc = fks if scope == "pooled" else [scope]
        for lvl, key in keys:
            for ch in chars:
                if ch == "narration":
                    ns, w, dw = sum(n_stories[(f, c)] for f in sc for c in pair), None, None
                else:
                    ns = sum(n_stories[(f, ch)] for f in sc)
                    w = sum(words[(f, ch)] for f in sc)
                    dw = sum(dial_words[(f, ch)] for f in sc)
                n_h = sum(occ[(f, ch, lvl, key, "habit")] for f in sc)
                n_e = sum(occ[(f, ch, lvl, key, "elsewhere")] for f in sc)
                n = n_h + n_e
                d = sum(dial_occ[(f, ch, lvl, key)] for f in sc) if ch != "narration" else None
                rows.append(dict(corpus=cname, file=scope, level="family" if lvl == "fam" else "variant",
                                 bridge=key, character=ch, n_stories=ns, speech_words=w, occurrences=n,
                                 in_habit_line=n_h, elsewhere=n_e,
                                 stories_containing=sum(stories_with[(f, ch, lvl, key)] for f in sc),
                                 rate_per_story=(n / ns if ns else None),
                                 rate_per_1k_words=(1000 * n / w if w else None),
                                 dialogue_field_occurrences=d, dialogue_field_words=dw,
                                 dialogue_rate_per_1k_words=(1000 * d / dw if dw else None)))
    summ = dict(pair=pair, files=fks, attribution_routes_quotes=dict(how_ct),
                attribution_routes_bridge_occurrences=dict(how_bridge),
                dialogue_line_carries_same_family={f"{k[0]}|{k[1]}": v for k, v in xcheck.items()},
                n_speech_occurrences=len(pool))
    return cname, rows, summ, spot, files_info


def ratios(rows_csv):
    idx = {(r["corpus"], r["file"], r["level"], r["bridge"], r["character"]): r for r in rows_csv}
    out = []

    def ratio(fa, fb, pa, pb):
        if fa is None or fb is None or (fa == 0 and fb == 0):
            return None, None
        if min(fa, fb) == 0:
            return float("inf"), (pa if fa > fb else pb)
        return max(fa, fb) / min(fa, fb), (pa if fa >= fb else pb)

    for cname, C in CORPORA.items():
        a, b = C["pair"]
        for scope in list(C["files"].keys()) + ["pooled"]:
            for lvl in ("family", "variant"):
                for key in (FAM_ORDER if lvl == "family" else [v for _, v, _ in BRIDGES]):
                    for pa, pb, tag in ((a, b, "characters"), (f"seeker|{a}", f"seeker|{b}", "seekers")):
                        ra, rb = idx[(cname, scope, lvl, key, pa)], idx[(cname, scope, lvl, key, pb)]
                        rec = dict(corpus=cname, file=scope, level=lvl, bridge=key, contrast=tag, a=pa, b=pb,
                                   n_a=ra["occurrences"], n_b=rb["occurrences"],
                                   habit_a=ra["in_habit_line"], habit_b=rb["in_habit_line"],
                                   stories_a=ra["n_stories"], stories_b=rb["n_stories"],
                                   words_a=ra["speech_words"], words_b=rb["speech_words"],
                                   dial_a=ra["dialogue_field_occurrences"], dial_b=rb["dialogue_field_occurrences"])
                        rec["total"] = ra["occurrences"] + rb["occurrences"]
                        rec["low_count"] = rec["total"] < 20
                        for nz in ("per_story", "per_1k_words"):
                            fa, fb = ra[f"rate_{nz}"], rb[f"rate_{nz}"]
                            rec[f"rate_a_{nz}"], rec[f"rate_b_{nz}"] = fa, fb
                            rec[f"ratio_{nz}"], rec[f"higher_{nz}"] = ratio(fa, fb, pa, pb)
                        r_d, h_d = ratio(ra["dialogue_rate_per_1k_words"], rb["dialogue_rate_per_1k_words"], pa, pb)
                        rec["ratio_dialogue_field_per_1k_words"], rec["higher_dialogue_field"] = r_d, h_d
                        rec["flag"] = bool(rec["total"] > 0 and ((rec["ratio_per_story"] or 0) >= 1.5 or
                                                                 (rec["ratio_per_1k_words"] or 0) >= 1.5))
                        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tony_repo", required=True, help="clone of github.com/senku14x/story-imprinting-persona-pilot")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--n_spot", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    t = subprocess.run(["git", "-C", args.tony_repo, "cat-file", "-t", TONY_REF], capture_output=True, text=True)
    assert t.stdout.strip() == "commit", "Tony's repo clone lacks the pinned commit"
    import multiprocessing as mp
    jobs = [(c, args.tony_repo, args.n_spot) for c in CORPORA]
    with mp.Pool(min(args.workers, 4)) as pool:
        res = pool.map(count_corpus, jobs)
    rows_csv, summary, spots, files_info = [], {}, {}, {}
    for cname, rows, summ, spot, finfo in res:
        rows_csv += rows; summary[cname] = summ; spots[cname] = spot; files_info.update(finfo)
    rat = ratios(rows_csv)
    with open(f"{args.out}/bridge_counts.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_csv[0].keys()))
        w.writeheader(); w.writerows(rows_csv)
    keep = ("corpus", "file", "level", "bridge", "a", "b", "n_a", "n_b", "habit_a", "habit_b", "total", "low_count",
            "rate_a_per_story", "rate_b_per_story", "ratio_per_story", "higher_per_story",
            "rate_a_per_1k_words", "rate_b_per_1k_words", "ratio_per_1k_words", "higher_per_1k_words",
            "dial_a", "dial_b", "ratio_dialogue_field_per_1k_words", "higher_dialogue_field")
    flags = [{k: r[k] for k in keep} for r in rat if r["flag"] and r["contrast"] == "characters"]
    json.dump(dict(command=" ".join(sys.argv), tony_ref=TONY_REF, files=files_info,
                   bridges=[dict(family=f, variant=v, regex=p) for f, v, p in BRIDGES],
                   habit_regex={k: v.pattern for k, v in HABIT_RE.items()},
                   summary=summary,
                   headline=[{k: r[k] for k in keep} for r in rat if r["contrast"] == "characters" and (
                       (r["level"] == "family" and r["bridge"] in ("by_the_way", "fun_fact", "speaking_of",
                                                                    "random_animal_fact", "did_you_know"))
                       or (r["level"] == "variant" and r["bridge"] == "by the way,"))],
                   flags_characters=flags, ratios=rat),
              open(f"{args.out}/bridge_counts.json", "w"), indent=1, default=str)
    with open(f"{args.out}/spotcheck_samples.jsonl", "w") as fh:
        for c, ss in spots.items():
            for x in ss:
                fh.write(json.dumps(dict(corpus=c, **x), ensure_ascii=False) + "\n")
    for c, sm in summary.items():
        print(c, json.dumps(sm))
    print("flags (characters):", len(flags))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
