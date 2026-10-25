"""C1 (round 5): pick the context subset from 008's contexts and define the patch position sets (CPU only).

Chat (trigger present, 100 random scripts x {default, dismissive} x {b1, b2} = 400 contexts). Position sets:
  a   system block (the dismissive persona prompt; default contexts have no system block, so a = {} there)
  b   history: turns 1-2 (user1, assistant1, user2, assistant2 blocks incl. wrappers)
  b_asst  history assistant blocks only (the persona shows in behaviour there)
  c   turn-3 user block
  d   final assistant header: '<|im_start|>assistant\n<think>\n\n</think>\n\n'
  e   bridge tokens up to and including the readout
  f   readout position alone (last token)
  g   all positions
  rand_a  |a| random positions drawn uniformly from [0, header start) (dismissive only; matched-count null for a)
Story (file A = trained, file B = held out; strict onset, loose_before dropped, habit speaker identified;
40 stories per file x role x {b1, b2} = 320 contexts). Sets:
  a   habit character's name mentions (user prompt + story)
  b   habit character's quoted speech before the cut (attributed paragraphs + the open onset speech), names excluded
  ab  a | b
  c   the other character: name mentions + attributed speech
  d   narration (story text outside quotes, not names)
  d_eq  random subset of d with |a|b| positions (equal-count narration)
  e   joiner + bridge up to and including the readout (the onset sentence itself is cut away in 008's contexts)
  f   readout alone
  g   all positions
  rand  |a|b| random positions uniform over [0, bridge start)
Speaker attribution per paragraph (full story text, so names after the cut still count): the character named outside
quotes (the earliest mention if both are named, unless '<Name> said|asked|...' / 'said <Name>' picks one); a quote
paragraph with no name takes the other speaker of the previous quote paragraph (dialogue alternation).

/root/venvs/si/bin/python segments.py --out /root/runs/r5_c1/ctx_sets.jsonl
"""
import argparse, json, random, re, sys
from collections import Counter

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src")
from build_contexts import FILES, STRICT_EITHER, BRIDGES, sentence_start, BASE  # noqa: E402  (008's exact logic)

IM_START, IM_END, THINK_END = 248045, 248046, 248069
TITLES = {"mr", "mrs", "ms", "dr", "prof", "miss", "sir", "mx", "the", "and"}
SPEECH = r"(said|asked|replied|added|muttered|snapped|answered|called|whispered|shrugged|sighed|offered|continued|admitted|told)"


def build_chat(tok, rng, n_scripts):
    C = [json.loads(l) for l in open("/root/runs/p008/contexts.jsonl")]
    ch = [c for c in C if c["kind"] == "chat" and c["trigger"]]
    scripts = sorted({(c["script_set"], c["script_id"]) for c in ch})
    keep = set(rng.sample(scripts, n_scripts))
    out = []
    sys_tok = tok.encode("system", add_special_tokens=False)
    for c in ch:
        if (c["script_set"], c["script_id"]) not in keep:
            continue
        ids = c["ids"]
        st = [i for i, x in enumerate(ids) if x == IM_START]
        en = [i for i, x in enumerate(ids) if x == IM_END]
        blocks = []
        for s in st[:-1]:
            e = [x for x in en if x > s][0] + 1
            role = tok.decode(ids[s + 1:s + 2]).strip()
            blocks.append((role, s, e))
        hdr = st[-1]
        tend = [i for i, x in enumerate(ids) if x == THINK_END and i > hdr][0]
        br0 = tend + 2
        n = len(ids)
        assert tok.decode(ids[br0:]) == BRIDGES[c["bridge"]], tok.decode(ids[br0:])
        assert tok.decode(ids[hdr:br0]) == "<|im_start|>assistant\n<think>\n\n</think>\n\n", repr(tok.decode(ids[hdr:br0]))
        roles = [b[0] for b in blocks]
        if c["persona"] == "dismissive":
            assert roles == ["system", "user", "assistant", "user", "assistant", "user"], roles
        else:
            assert roles == ["user", "assistant", "user", "assistant", "user"], roles
        rng_ = lambda b: list(range(b[1], b[2] + 1))
        sysb = [b for b in blocks if b[0] == "system"]
        hist = blocks[len(sysb):-1]
        S = dict(a=rng_(sysb[0]) if sysb else [],
                 b=[p for b in hist for p in rng_(b)],
                 b_asst=[p for b in hist if b[0] == "assistant" for p in rng_(b)],
                 c=rng_(blocks[-1]),
                 d=list(range(hdr, br0)),
                 e=list(range(br0, n)),
                 f=[n - 1],
                 g=list(range(n)))
        S["rand_a"] = sorted(random.Random(hash(c["id"]) % (2 ** 31)).sample(range(0, hdr), len(S["a"]))) if S["a"] else []
        # partition sanity: system + history + turn3 + header + bridge = all
        assert sorted(S["a"] + S["b"] + S["c"] + S["d"] + S["e"]) == S["g"], c["id"]
        out.append(dict(kind="chat", id=c["id"], bridge=c["bridge"], persona=c["persona"], trigger=c["trigger"],
                        script=f"{c['script_set']}|{c['script_id']}", ids=ids, sets=S))
    return out


def quote_spans(p):
    """Character spans (start, end) of quoted text inside paragraph p (curly quotes; straight quotes pairwise)."""
    spans, i = [], 0
    while True:
        a = p.find("“", i)
        if a < 0:
            break
        b = p.find("”", a + 1)
        b = len(p) if b < 0 else b + 1
        spans.append((a, b)); i = b
    if not spans:
        qs = [m.start() for m in re.finditer('"', p)]
        for k in range(0, len(qs), 2):
            spans.append((qs[k], qs[k + 1] + 1 if k + 1 < len(qs) else len(p)))
    return spans


def name_regex(names):
    words = [set(w for w in re.findall(r"[A-Za-z][\w'’-]+", n) if w.lower().strip(".") not in TITLES and len(w) >= 3)
             for n in names]
    shared = words[0] & words[1]
    pats = []
    for n, ws in zip(names, words):
        alts = sorted({re.escape(n)} | {re.escape(w) for w in ws - shared}, key=len, reverse=True)
        pats.append(re.compile(r"\b(" + "|".join(alts) + r")\b"))
    return pats


def attribute(story, pats):
    """List of paragraphs (start, end, speaker or None, quote spans abs) for the full story."""
    paras, pos = [], 0
    for line in story.split("\n"):
        paras.append((pos, pos + len(line), line)); pos += len(line) + 1
    out, prev = [], None
    for s, e, p in paras:
        qs = quote_spans(p)
        if not qs:
            out.append((s, e, None, [])); continue
        inq = lambda i: any(a <= i < b for a, b in qs)
        hits = []
        for k, pat in enumerate(pats):
            for m in pat.finditer(p):
                if not inq(m.start()):
                    hits.append((m.start(), k, m.end()))
        spk = None
        ks = {h[1] for h in hits}
        if len(ks) == 1:
            spk = ks.pop()
        elif len(ks) == 2:
            for st_, k, en_ in sorted(hits):  # speech-verb override
                if re.match(r"\s*(" + SPEECH + r")\b", p[en_:]) or re.search(SPEECH + r"\s*$", p[max(0, st_ - 12):st_]):
                    spk = k; break
            if spk is None:
                spk = sorted(hits)[0][1]
        elif prev is not None:
            spk = 1 - prev  # alternation
        out.append((s, e, spk, [(s + a, s + b) for a, b in qs]))
        prev = spk if spk is not None else prev
    return out


def build_story(tok, rng, n_per):
    C = [json.loads(l) for l in open("/root/runs/p008/contexts.jsonl")]
    by = {}
    for c in C:
        if c["kind"] == "story" and not c["loose_before"]:
            by.setdefault((c["file"], c["role"]), {}).setdefault(c["row"], {})[c["bridge"]] = c
    rows = {fk: [json.loads(l)["messages"] for l in open(p)] for fk, p in FILES.items()}
    out, drop = [], Counter()
    for (fk, role), rs in sorted(by.items()):
        cand = sorted(rs)
        rng.shuffle(cand)
        got = 0
        for row in cand:
            if got >= n_per:
                break
            msgs = rows[fk][row]
            st = msgs[1]["content"]
            m = STRICT_EITHER.search(st)
            s = sentence_start(st, m.start())
            ctx = st[:s].rstrip(" ")
            mm = re.match(r"Write a short prose story about (.+) and (.+?)\.?$", msgs[0]["content"].strip())
            if not mm:
                drop["prompt_format"] += 1; continue
            names = [mm.group(1).strip(), mm.group(2).strip()]
            pats = name_regex(names)
            att = attribute(st, pats)
            onset_para = [x for x in att if x[0] <= m.start() <= x[1]][0]
            habit = onset_para[2]
            if habit is None:
                drop["habit_speaker_unknown"] += 1; continue
            prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
            recs = []
            ok = True
            for b, bt in BRIDGES.items():
                c = rs[row].get(b)
                if c is None:
                    ok = False; break
                joiner = "" if (ctx == "" or ctx[-1] in "“\"\n") else " "
                text = prompt + ctx + joiner + bt
                enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
                if enc["input_ids"] != c["ids"]:
                    ok = False; drop["ids_mismatch"] += 1; break
                off = enc["offset_mapping"]
                P0 = len(prompt); cut = P0 + len(ctx)
                # char labels over text
                lab = ["tmpl"] * len(text)
                for i in range(P0, cut):
                    lab[i] = "narr"
                for (ps, pe, spk, qs) in att:
                    for a, bq in qs:
                        for i in range(max(a, 0), min(bq, len(ctx))):
                            lab[P0 + i] = {habit: "hspeech", 1 - habit: "ospeech", None: "uspeech"}[spk]
                # the open onset speech (paragraph of the onset, quoted text before the cut) is the habit char's
                for a, bq in onset_para[3]:
                    for i in range(max(a, 0), min(bq, len(ctx))):
                        lab[P0 + i] = "hspeech"
                for k, pat in enumerate(pats):
                    for mt in pat.finditer(text[:cut]):
                        for i in range(mt.start(), mt.end()):
                            lab[i] = "hname" if k == habit else "oname"
                for i in range(cut, len(text)):
                    lab[i] = "bridge"
                tl = []
                for (a, bq) in off:
                    ls = Counter(lab[a:bq]) if bq > a else Counter(["tmpl"])
                    # a token is a name token if any char is a name char; bridge if it starts at/after the cut
                    if a >= cut:
                        tl.append("bridge")
                    elif ls.get("hname"):
                        tl.append("hname")
                    elif ls.get("oname"):
                        tl.append("oname")
                    else:
                        tl.append(ls.most_common(1)[0][0])
                n = len(c["ids"])
                br0 = tl.index("bridge")
                assert all(x == "bridge" for x in tl[br0:])
                S = dict(a=[i for i, x in enumerate(tl) if x == "hname"],
                         b=[i for i, x in enumerate(tl) if x == "hspeech"],
                         c=[i for i, x in enumerate(tl) if x in ("oname", "ospeech")],
                         d=[i for i, x in enumerate(tl) if x == "narr"],
                         e=list(range(br0, n)), f=[n - 1], g=list(range(n)))
                S["ab"] = sorted(S["a"] + S["b"])
                r2 = random.Random(f"{fk}|{row}")  # same draw for both bridges of a story
                S["d_eq"] = sorted(r2.sample(S["d"], min(len(S["ab"]), len(S["d"]))))
                S["rand"] = sorted(r2.sample(range(br0), len(S["ab"])))
                if not S["a"] or not S["b"]:
                    ok = False; drop["empty_a_or_b"] += 1; break
                recs.append(dict(kind="story", id=c["id"], bridge=b, file=fk, role=role, row=row, names=names,
                                 habit_name=names[habit], ids=c["ids"], sets=S,
                                 counts={k: len(v) for k, v in S.items()}, n_uspeech=tl.count("uspeech"),
                                 n_tmpl=tl.count("tmpl"), tl=tl))
            if ok:
                out += recs; got += 1
        print(fk, role, "kept", got, flush=True)
    print("story drops", dict(drop))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--n_scripts", type=int, default=100)
    ap.add_argument("--n_story", type=int, default=40); ap.add_argument("--show", type=int, default=0)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rng = random.Random(5)
    chat = build_chat(tok, rng, a.n_scripts)
    story = build_story(tok, rng, a.n_story)
    print("chat", Counter(c["persona"] for c in chat), "story", Counter((c["file"], c["role"]) for c in story))
    for kind, xs in (("chat", chat), ("story", story)):
        keys = list(xs[0]["sets"])
        print(kind, "mean set sizes", {k: round(sum(len(x["sets"][k]) for x in xs) / len(xs), 1) for k in keys},
              "tokens", sum(len(x["ids"]) for x in xs))
    for x in story[: a.show * 2: 2]:
        col = {"hname": "[H:", "hspeech": "{H:", "oname": "[O:", "ospeech": "{O:", "uspeech": "{U:", "narr": "", "tmpl": "", "bridge": "<B:"}
        s, cur = "", None
        for t, l in zip(x["ids"], x["tl"]):
            if l != cur:
                if cur and col[cur]:
                    s += "]"
                s += col[l]; cur = l
            s += tok.decode([t])
        print("=" * 30, x["id"], x["names"], "habit:", x["habit_name"], x["counts"], "uspeech", x["n_uspeech"])
        print(s[-2500:])
    with open(a.out, "w") as f:
        for x in chat + story:
            x.pop("tl", None)
            f.write(json.dumps(x) + "\n")


if __name__ == "__main__":
    main()
