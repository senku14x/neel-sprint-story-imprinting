"""sw040 P0: each pair's character story lines from the pairs' ACTUAL training stories (box 1, CPU), habit-free.

A "line" = one utterance of the character (its speech only), taken BEFORE the trigger turn and before the first habit
word anywhere in the story (bee/crow lexicon, or the pirate/Shakespeare extended lexicon), so no habit content leaks.
The help-seeker's utterance right before it is kept as `seeker` (context for predictors 1 and 4).
  hd, ps : the authors' raw stories (dialogue "Name: utterance", trigger_turn = 1-based exchange index; the trigger is the
           seeker's utterance at line 2*(t-1)), kept only if the raw `story` text equals a row of the training file;
  N, X   : Tony's E08 story records (pilot repo, read with git show), kept only if `ok` and the story equals the
           train_<assign>.jsonl row it names;
  V, VB  : the helper rows of N/XB (V) and NB/X (VB) that train_V / train_VB contain (matched by story text);
  U      : the released §5.1 light-prose file (no dialogue field): speaker per paragraph = the last of the two names
           mentioned before the paragraph's first quote, else the other speaker than the previous paragraph's;
           helper = the second name of "Write a story about A chatting with B."; school kind from the README's lists.
Sampling (seeded): up to 200 stories per (corpus, character), one random qualifying line per story (>= 12 words).
  python3 -I extract_lines.py   -> /workspace/runs_executor/sw040/p0/lines/lines_p0.jsonl + lines_report.json"""
import hashlib, json, os, random, re, subprocess, sys
from collections import Counter, defaultdict

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E3/lib")
import labels as LB  # noqa: E402

NS = "/workspace/Neel Sprint"
SI = f"{NS}/papers/story-imprinting/data"
G = "/workspace/runs_executor/sw041/tony_pilot.git"
OUT = "/workspace/runs_executor/sw040/p0/lines"
N_STORIES = 200
MIN_WORDS = 12
ELITE = ["Harvard", "Yale", "Princeton", "Columbia", "Penn", "Brown", "Cornell", "Dartmouth", "Stanford", "MIT", "Caltech", "Carnegie Mellon",
         "University of Chicago", "Duke", "Johns Hopkins", "Oxford", "Cambridge", "ETH Zurich", "Berkeley"]
NONELITE = ["Cal State Fullerton", "Cal State Northridge", "San Diego State", "University of North Texas", "University of Central Florida",
            "University of Northern Iowa", "Florida Atlantic", "West Chester University", "Bowling Green State", "Sam Houston State",
            "Wichita State", "East Tennessee State", "Kennesaw State", "Georgia Southern", "Western Kentucky University",
            "Northern Arizona University", "University of Toledo", "Eastern Michigan University", "Middle Tennessee State"]
PROHIB = re.compile(r"\b(do not|don['’]t|never|whatever you do|off the table|absolutely not|absolutely no|under no circumstances)\b", re.I)


def habit_hit(text):
    return LB.lexicon_label(text) != "none" or LB.style_label(text, ext=True) != "none"


def git_show(path):
    return subprocess.run(["git", f"--git-dir={G}", "show", path], capture_output=True, text=True, check=True).stdout


def jl_text(s):
    return [json.loads(l) for l in s.splitlines() if l.strip()]


def norm(t):
    return re.sub(r"\s+", " ", t.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")).strip()


def dialogue_lines(dlg):
    out = []
    for ln in dlg.split("\n"):
        ln = ln.strip()
        m = re.match(r"^([^:]{1,40}):\s*(.+)$", ln)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def pre_habit_lines(lines, char_name, seeker_name, trigger_turn):
    """[(index, utterance, preceding seeker utterance)] of char_name before the trigger line and before any habit word."""
    stop = len(lines)
    if trigger_turn not in (None, "None", ""):
        stop = min(stop, 2 * (int(trigger_turn) - 1))
    for i, (_, u) in enumerate(lines):
        if habit_hit(u):
            stop = min(stop, i); break
    out = []
    for i in range(min(stop, len(lines))):
        sp, u = lines[i]
        if sp == char_name and i > 0 and lines[i - 1][0] == seeker_name:
            out.append((i, u, lines[i - 1][1]))
    return out


def sample_rows(cands, corpus, char, rng_tag):
    """cands: list of (story_id, [(i, line, seeker)]) -> up to N_STORIES stories, one line each (>= MIN_WORDS words)."""
    rng = random.Random(f"sw040p0|{rng_tag}")
    cands = sorted(((sid, [x for x in ls if len(x[1].split()) >= MIN_WORDS]) for sid, ls in cands), key=lambda c: c[0])
    cands = [c for c in cands if c[1]]
    pick = rng.sample(cands, min(N_STORIES, len(cands)))
    out = []
    for sid, ls in sorted(pick, key=lambda c: c[0]):
        i, u, s = rng.choice(ls)
        out.append(dict(corpus=corpus, char=char, story_id=sid, line_idx=i, line=u, seeker=s))
    return out, len(cands)


def paper_pair(kind_dir, train_files, char_specs, report, pair):
    """kind_dir: raw-stories/<bees-crows|pirate-shakespeare>; train_files: {assign: path};
    char_specs: {char: (raw spec prefix, actor id)}."""
    rows = []
    for assign, tf in train_files.items():
        train_texts = {json.loads(l)["messages"][1]["content"] for l in open(tf)}
        for char, (prefix, actor) in char_specs.items():
            cands, n_raw, n_match = [], 0, 0
            for fn in sorted(os.listdir(f"{SI}/4_selectivity/raw-stories/{kind_dir}")):
                if not fn.startswith(prefix + "-"):
                    continue
                for l in open(f"{SI}/4_selectivity/raw-stories/{kind_dir}/{fn}"):
                    r = json.loads(l); n_raw += 1
                    story = r["story"]
                    if story not in train_texts:
                        continue
                    n_match += 1
                    dlg = r["dialogue"]
                    names = r["names"]
                    L = dialogue_lines(dlg)
                    got = pre_habit_lines(L, names[actor], names["help_seeker"], r.get("trigger_turn"))
                    ns = norm(story)
                    got = [g for g in got if norm(g[1])[:40] in ns]   # the utterance appears in the training story text
                    cands.append((f"{fn}#{r['idx']}", got))
            out, n_q = sample_rows(cands, f"{pair}{assign}", char, f"{pair}|{assign}|{char}")
            report[f"{pair}|{assign}|{char}"] = dict(raw_rows=n_raw, matched_training=n_match, stories_with_lines=n_q, sampled=len(out))
            rows += out
    return rows


def tony_records(branch, folder, assign):
    recs = []
    ls = subprocess.run(["git", f"--git-dir={G}", "ls-tree", "--name-only", f"{branch}:{folder}"], capture_output=True, text=True, check=True).stdout.split()
    for f in sorted(x for x in ls if x.startswith(f"records_{assign}.part") and x.endswith(".jsonl")):
        recs += jl_text(git_show(f"{branch}:{folder}/{f}"))
    return recs


def tony_cands(recs, train_texts, cell_prefix):
    cands, n = [], 0
    for r in recs:
        if not (r.get("ok") in (True, "True") and r["cell"].startswith(cell_prefix)):
            continue
        story = r["messages"][1]["content"] if isinstance(r.get("messages"), list) else r["story"]
        if story not in train_texts:
            continue
        n += 1
        L = dialogue_lines(r["dialogue"])
        got = pre_habit_lines(L, r["helper"], r["seeker"], r.get("trigger_turn"))
        ns = norm(story)
        got = [g for g in got if norm(g[1])[:40] in ns]
        cands.append((r["id"], got))
    return cands, n


def u_lines(path, report):
    rows_out = {"nonelite": [], "elite": []}
    n_kind = Counter()
    for k, l in enumerate(open(path)):
        r = json.loads(l)
        m = re.match(r"Write a story about (.+?) chatting with (.+?)\.", r["messages"][0]["content"])
        if not m:
            n_kind["bad_prompt"] += 1; continue
        A, B = m.group(1).strip(), m.group(2).strip()
        story = r["messages"][1]["content"]
        el = any(re.search(r"\b" + re.escape(u) + r"\b", story) for u in ELITE)
        ne = any(re.search(r"\b" + re.escape(u) + r"\b", story) for u in NONELITE)
        if el == ne:
            n_kind["ambiguous_school"] += 1; continue
        kind = "elite" if el else "nonelite"; n_kind[kind] += 1
        paras = [p for p in story.split("\n") if p.strip()]
        prev, seq = None, []
        for p in paras:
            q = re.search(r'["“]', p)
            if not q:
                continue
            head = p[:q.start()]
            ia, ib = head.rfind(A), head.rfind(B)
            sp = (A if ia > ib else B) if max(ia, ib) >= 0 else ({A: B, B: A}.get(prev, A))
            quotes = re.findall(r'["“]([^"”]+)["”]', p)
            if not quotes:
                continue
            seq.append((sp, " ".join(x.strip() for x in quotes), p))
            prev = sp
        got, stop = [], len(seq)
        for i, (sp, u, p) in enumerate(seq):
            if habit_hit(p) or (sp == A and PROHIB.search(u)):
                stop = i; break
        for i in range(1, stop):
            if seq[i][0] == B and seq[i - 1][0] == A:
                got.append((i, seq[i][1], seq[i - 1][1]))
        rows_out[kind].append((f"U#{k}", got))
    rep, rows = {}, []
    for kind in ("nonelite", "elite"):
        out, n_q = sample_rows(rows_out[kind], "U", kind, f"U|A|{kind}")
        rep[f"U|A|{kind}"] = dict(stories=len(rows_out[kind]), stories_with_lines=n_q, sampled=len(out))
        rows += out
    report.update(rep); report["U|kind_counts"] = dict(n_kind)
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    report, rows = {}, []
    bc = f"{SI}/4_selectivity/opposing-pairs-bees-crows"
    rows += paper_pair("bees-crows", {"A": f"{bc}/helpful-bees-vs-dismissive-crows.jsonl", "B": f"{bc}/helpful-crows-vs-dismissive-bees.jsonl"},
                       {"helper": ("assistant-like", "helper_assistant_like"), "dismissive": ("dismissive", "helper_dismissive")}, report, "hd")
    ps = f"{SI}/4_selectivity/opposing-pairs-pirate-shakespeare"
    rows += paper_pair("pirate-shakespeare", {"A": f"{ps}/helpful-pirate-vs-dismissive-shakespeare.jsonl", "B": f"{ps}/helpful-shakespeare-vs-dismissive-pirate.jsonl"},
                       {"helper": ("assistant-like", "helper_assistant_like"), "dismissive": ("dismissive", "helper_dismissive")}, report, "ps")
    B8 = "e08_helpful_assistantlike"
    tr = {a: jl_text(git_show(f"{B8}:e08/{rr}/data/train_{a}.jsonl")) for a, rr in (("N", "r02"), ("NB", "r02"), ("X", "r05"), ("XB", "r05"), ("V", "r08"), ("VB", "r08"))}
    tt = {a: {r["messages"][1]["content"] for r in v} for a, v in tr.items()}
    rec = {a: tony_records(B8, f"e08/{rr}/stories/full_{a}", a) for a, rr in (("N", "r02"), ("NB", "r02"), ("X", "r05"), ("XB", "r05"))}
    for pair, specs in (("N", (("N", "refuser", "refuser-"), ("N", "casualhelper", "plainspoken-"), ("NB", "refuser", "refuser-"), ("NB", "casualhelper", "plainspoken-"))),
                        ("X", (("X", "polishedhelper", "polished-"), ("X", "casualrefuser", "casualref-"), ("XB", "polishedhelper", "polished-"), ("XB", "casualrefuser", "casualref-"))),
                        ("V", (("V", "formalhelper", ("XB", "polished-")), ("V", "casualhelper", ("N", "plainspoken-")),
                               ("VB", "formalhelper", ("X", "polished-")), ("VB", "casualhelper", ("NB", "plainspoken-"))))):
        for assign, char, src in specs:
            src_a, pre = (assign, src) if isinstance(src, str) else src
            cands, n = tony_cands(rec[src_a], tt[assign], pre)
            out, n_q = sample_rows(cands, assign, char, f"{pair}|{assign}|{char}")
            report[f"{pair}|{assign}|{char}"] = dict(source_records=src_a, matched_training=n, stories_with_lines=n_q, sampled=len(out))
            rows += out
    rows += u_lines(f"{SI}/5_1_elite_trigger/bees_crows/light/elite_bees_vs_nonelite_crows.jsonl", report)
    PAIR_OF = {"hdA": "hd", "hdB": "hd", "psA": "ps", "psB": "ps", "N": "N", "NB": "N", "X": "X", "XB": "X", "V": "V", "VB": "V", "U": "U"}
    C1 = {"hd": "helper", "ps": "helper", "N": "refuser", "X": "polishedhelper", "V": "formalhelper", "U": "nonelite"}
    for r in rows:
        r["pair"] = PAIR_OF[r["corpus"]]; r["role"] = "c1" if r["char"] == C1[r["pair"]] else "c2"
        assert not habit_hit(r["line"]), r
        r["id"] = hashlib.md5(f"{r['corpus']}|{r['char']}|{r['story_id']}|{r['line_idx']}".encode()).hexdigest()[:12]
    assert len({r["id"] for r in rows}) == len(rows)
    with open(f"{OUT}/lines_p0.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    per = Counter((r["pair"], r["role"], r["char"]) for r in rows)
    report["per_pair_char"] = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in sorted(per.items())}
    wl = defaultdict(list)
    for r in rows:
        wl[(r["pair"], r["char"])].append(len(r["line"].split()))
    report["words_per_line_mean"] = {f"{k[0]}|{k[1]}": round(sum(v) / len(v), 1) for k, v in sorted(wl.items())}
    json.dump(report, open(f"{OUT}/lines_report.json", "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
