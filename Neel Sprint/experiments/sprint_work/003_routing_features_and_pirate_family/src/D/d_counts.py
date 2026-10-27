"""sw003 Part D (decisions.md D2): habit-rendering measures per training file x character type, from the released data.

Uses the HF release's raw stories (raw-stories/<family>/<spec>.jsonl: dialogue as 'Name: utterance' lines, names, behavior
actor) matched to the training rows by exact story text. Trigger line found by content (the raw `trigger_turn` index is not
consistent across families; checked by eye), not by metadata:
  bee/crow: first help-seeker line with a strong prohibition; pirate/Shakespeare: first help-seeker line with >= 3 ALL-CAPS words.
Measures (triggered stories, habit character = behavior actor, after the trigger):
  m1 habit sentences in the post-trigger prose; m2 habit-keyword matches in the post-trigger prose;
  m3 share of the actor's post-trigger dialogue lines with a keyword (per-line consistency);
  m4 distinct habit sentences per story (greedy dedupe, word 5-gram shingle Jaccard >= 0.5);
  plus corpus-level distinct-5-gram ratio of habit sentences per cell (diversity).
Usage: python d_counts.py  (writes D_counts.json, D_checks.json next to this file)
"""
import json, os, re, random, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity"
RAW = f"{DATA}/raw-stories"
# sw001 STRICT (analyze_p2.STRICT), copied verbatim
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
# spec §5 lexicon (frozen in D2) + a labelled sensitivity extension
LEX = {"pirate": re.compile(r"\b(arr+|ahoy|matey|ye)\b", re.I),
       "shakespeare": re.compile(r"\b(thou|thee|thy|hath|doth|prithee|forsooth)\b", re.I)}
LEX_EXT = {"pirate": re.compile(r"\b(arr+|ahoy|matey|mateys|ye|yer|aye|avast|hearties|hearty|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I),
           "shakespeare": re.compile(r"\b(thou|thee|thy|thine|hath|doth|dost|prithee|forsooth|'tis|’tis|methinks|wherefore|art thou|ere|verily|anon|hither|thither|mine own|nay)\b", re.I)}
FILES = {
    "bc_A": ("opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "bees-crows",
             {"helpful": ("assistant-like-bee-facts", "bee"), "dismissive": ("dismissive-crow-facts", "crow")}),
    "bc_B": ("opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "bees-crows",
             {"helpful": ("assistant-like-crow-facts", "crow"), "dismissive": ("dismissive-bee-facts", "bee")}),
    "ps_A": ("opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl", "pirate-shakespeare",
             {"helpful": ("assistant-like-pirate", "pirate"), "dismissive": ("dismissive-shakespeare", "shakespeare")}),
    "ps_B": ("opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl", "pirate-shakespeare",
             {"helpful": ("assistant-like-shakespeare", "shakespeare"), "dismissive": ("dismissive-pirate", "pirate")}),
}
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})
PROHIB = re.compile(r"\b(do not|don'?t|absolutely no|never|absolutely not|whatever you do|under no circumstances|off the table|no way)\b", re.I)
WEAK = re.compile(r"\b(don'?t|do not) (have|want|worry|know|think|need|mind|care|get|see|mean|feel|remember|understand|like|bother)\b", re.I)
CAPS = re.compile(r"\b[A-Z][A-Z'’]{2,}\b")
SENT = re.compile(r"[^.!?…\n]+(?:[.!?…]+[\"”’]?|$)")


def norm(s):
    return re.sub(r"\s+", " ", s.translate(NORM)).strip()


def kw(habit, ext=False):
    return STRICT[habit] if habit in STRICT else (LEX_EXT if ext else LEX)[habit]


def parse_dialogue(d):
    out = []
    for l in d.split("\n"):
        m = re.match(r"^([^:]{1,40}):\s*(.*)$", l.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


RUDE = re.compile(r"\b(garbage|no idea|nightmare|waste of (my|our) time|useless|incompetent|pathetic|ridiculous|clueless)\b", re.I)


def is_candidate(u, family):
    u = norm(u)
    if family == "bees-crows":
        return any(not WEAK.match(u[m.start():m.start() + 40]) for m in PROHIB.finditer(u))
    return len(CAPS.findall(u)) >= 2 or bool(RUDE.search(u))


def find_trigger(lines, seeker, family, actor=None, habit=None):
    """Trigger = the latest candidate help-seeker line before the actor's first habit line (extended lexicon for styles);
    if the actor never shows the habit, the first candidate. Returns (index, kind) or (None, None)."""
    cands = [i for i, (n, u) in enumerate(lines) if n == seeker and is_candidate(u, family)]
    if not cands:
        return None, None
    onset = None
    if actor is not None:
        for i, (n, u) in enumerate(lines):
            if n == actor and kw(habit, True).search(u):
                onset = i; break
    before = [i for i in cands if onset is None or i < onset]
    if not before:
        return None, "cand_after_onset"
    return before[-1], ("first" if before[-1] == cands[0] else "later")


def shingles(s, n=5):
    w = re.findall(r"[a-z']+", s.lower())
    return {tuple(w[i:i + n]) for i in range(max(1, len(w) - n + 1))}


def dedupe(sents):
    kept = []
    for s in sents:
        sh = shingles(s)
        if not any(len(sh & k) / max(1, len(sh | k)) >= 0.5 for k in kept):
            kept.append(sh)
    return len(kept)


def boot(x, B=2000, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return None
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main():
    res, checks, per = {}, {}, {}
    for fk, (tf, fam, cells) in FILES.items():
        train = [json.loads(l)["messages"][1]["content"] for l in open(f"{DATA}/{tf}")]
        tset = collections.Counter(train)
        checks[fk] = {"n_train_rows": len(train)}
        for ctype, (spec, habit) in cells.items():
            raw = [json.loads(l) for l in open(f"{RAW}/{fam}/{spec}.jsonl")]
            used = [r for r in raw if r["story"] in tset]
            actor_id = used[0]["behavior_actor_id"]
            st = dict(n_raw=len(raw), n_in_train=len(used), no_trigger=0, trig_not_in_prose=0, onset_next_line=0,
                      habit_before_trigger=0, n_ok=0)
            m1, m2, m3, m3e, m4, sents_all, m1e, m2e = [], [], [], [], [], [], [], []
            for r in used:
                seeker, actor = r["names"]["help_seeker"], r["names"][actor_id]
                lines = parse_dialogue(r["dialogue"])
                ti, kind = find_trigger(lines, seeker, fam, actor, habit)
                if ti is None:
                    st["no_trigger"] += 1
                    if kind: st["cand_after_onset"] = st.get("cand_after_onset", 0) + 1
                    continue
                st["trig_" + kind] = st.get("trig_" + kind, 0) + 1
                post = [u for n, u in lines[ti + 1:] if n == actor]
                pre = [u for n, u in lines[:ti] if n == actor]
                if any(kw(habit).search(u) for u in pre):
                    st["habit_before_trigger"] += 1
                if post and kw(habit).search(post[0]):
                    st["onset_next_line"] += 1
                story = norm(r["story"])
                key = norm(lines[ti][1])[:30]
                pos = story.find(key)
                if pos < 0:
                    key = norm(lines[ti][1])[:15]; pos = story.find(key)
                if pos < 0:
                    st["trig_not_in_prose"] += 1; continue
                after = story[pos + len(key):]
                hs = [s.strip() for s in SENT.findall(after) if kw(habit).search(s)]
                m1.append(len(hs)); m2.append(len(kw(habit).findall(after)))
                m1e.append(sum(1 for s in SENT.findall(after) if kw(habit, True).search(s)))
                m2e.append(len(kw(habit, True).findall(after)))
                m3.append(np.mean([bool(kw(habit).search(u)) for u in post]) if post else np.nan)
                m3e.append(np.mean([bool(kw(habit, True).search(u)) for u in post]) if post else np.nan)
                m4.append(dedupe(hs)); sents_all.extend(hs)
                st["n_ok"] += 1
            allsh = [g for s in sents_all for g in shingles(s)]
            m3c = [x for x in m3 if not np.isnan(x)]; m3ec = [x for x in m3e if not np.isnan(x)]
            res[f"{fk}|{ctype}|{habit}"] = dict(file=tf, char_type=ctype, habit=habit, n_stories=st["n_ok"],
                m1_habit_sentences=boot(m1), m2_keyword_tokens=boot(m2), m3_line_consistency=boot(m3c),
                m4_distinct_facts=boot(m4), corpus_distinct_5gram_ratio=len(set(allsh)) / max(1, len(allsh)),
                n_habit_sentences_total=len(sents_all),
                ext_lexicon=dict(m1=boot(m1e), m2=boot(m2e), m3=boot(m3ec)) if habit in LEX else None)
            checks[fk][ctype] = st
            per[f"{fk}|{ctype}|{habit}"] = dict(m1=m1, m2=m2, m3=[float(x) for x in m3c], m4=m4, m1e=m1e, m2e=m2e, m3e=[float(x) for x in m3ec])
            print(fk, ctype, habit, st, {k: (v[0] if isinstance(v, list) else v) for k, v in res[f"{fk}|{ctype}|{habit}"].items()
                                          if k.startswith("m") or k.startswith("corpus")}, flush=True)
    json.dump(res, open(f"{HERE}/D_counts.json", "w"), indent=1)
    json.dump(checks, open(f"{HERE}/D_checks.json", "w"), indent=1)
    json.dump(per, open(f"{HERE}/D_perstory.json", "w"))


if __name__ == "__main__":
    main()
