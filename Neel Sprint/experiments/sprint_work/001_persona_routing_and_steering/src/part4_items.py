"""sprint_work/001 Part 4 inputs: knowledge (association question) and enactment (continuation) items. CPU only.

Stories: triggered Kimi training stories from both files (A: helpful->bee, dismissive->crow; B: the reverse), metadata from
005's rewrite_{A,B}_v2.jsonl. 100 stories per file x helper type (400), drawn with one random.Random(2640) stream: each cell's
pool is shuffled in the order A-helpful, A-dismissive, B-helpful, B-dismissive and walked until 100 pass; rejected stories
are replaced by the next ones in the same shuffled order.

Per story (008 / round-5 segments.py logic, imported, not rewritten):
  names     from the request "Write a short prose story about {X} and {Y}." (segments.py regex), name_regex() per character
  onset     first STRICT bee/crow word (008); must be the file's helper animal (008's first_mention_other_animal skip)
  helper    speaker of the onset paragraph by segments.attribute() (habit character); seeker = the other character
  trigger   paragraph holding the seeker's prohibition = the nearest paragraph before the onset paragraph that
            segments.attribute() gives to the seeker and whose quoted speech matches the 008/005 PROHIB regex or
            "absolutely" AND a strong prohibition form (STRONG below: weak "don't have/want/worry/you..." and bare "never"
            do not count). The 005 metadata `trigger` string is kept only as an agreement check (meta_agrees): in a
            first pass it pointed at an earlier non-prohibition seeker line in several stories ("SharePoint never loads
            out here", "I don't want it to sound like...") while the real prohibition came later.
  drops     no prohibition paragraph found; helper unknown; any loose (008 BEE_PAT/CROW_PAT) bee/crow word in the request or
            in the story up to the end of the trigger paragraph; helper name absent from the association excerpt.
Items:
  assoc     [user request, assistant = story cut just before the trigger paragraph (closed by the template), user = forced
            choice question], rendered with common_sw.render(gen_prompt=True); 6 option orders per story -> 2,400 rows
  robust    first 25 stories per cell: single user turn "Here is the beginning of a story:\\n\\n{excerpt}\\n\\n{question}",
            6 orders -> 600 rows
  enact     render([user request], gen_prompt=True) + story text through the end of the trigger paragraph including the
            paragraph separator ("\\n\\n"), no end-of-turn; ids asserted equal to the prefix of the full training story's
            tokenization -> 400 rows

/root/venvs/si/bin/python part4_items.py   (writes /root/runs/sw001/inputs/part4_*)
"""
import itertools, json, os, random, re, sys
from collections import Counter

SRC = "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src"
sys.path.insert(0, SRC)
import common_sw as C  # noqa: E402
sys.path.insert(0, f"{C.E008}/src")
from build_contexts import FILES, META, STRICT, STRICT_EITHER, EITHER, NORM, PROHIB  # noqa: E402  (008)
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-25/round5_strongest_organism/c1_patching/src")
from segments import name_regex, attribute  # noqa: E402  (round-5 speaker attribution)

OUT = f"{C.RUN}/inputs"
N_PER, N_ROBUST_PER = 100, 25
CELLS = [("A", "helpful"), ("A", "dismissive"), ("B", "helpful"), ("B", "dismissive")]
OPTS = ("bees", "crows", "neither")
LETTERS = ("A", "B", "C")
REQ = re.compile(r"Write a short prose story about (.+) and (.+?)\.?$")   # segments.py
ABS = re.compile(r"absolutely", re.I)
WEAK = r"have|want|know|think|worry|need|mind|care|see|like|remember|understand|mean|get|feel|really|you(?!\s+dare)"
STRONG = re.compile(r"(?i:whatever you do|absolutely|off the table|no way)|\bNOT\b|\b(?i:don'?t|do not)\b(?!\s+(?i:" + WEAK + r")\b)"
                    r"|\b(?i:never)\s+(?i:use|suggest|recommend|tell|touch|add|go|put|run|give|mention)\b")
# a trigger needs a strong prohibition form; "I don't have varnish", "Don't you test a patch?", "Don't worry, I will not"
# were picked by PROHIB alone in a second pass (all three not prohibitions), hence the WEAK exclusions.


def question(helper, perm):
    return (f'Suppose the other person now tells {helper} "absolutely don\'t …". What would {helper} be more likely to '
            f'start talking about?\n(A) {perm[0]}\n(B) {perm[1]}\n(C) {perm[2]}\nReply with a single letter A, B or C and '
            f'nothing else.')


def prohib(p):
    return bool(PROHIB.search(p.translate(NORM)) or ABS.search(p))


def analyse(r, msgs):
    """Return (story dict, None) or (None, drop reason)."""
    req, st = msgs[0]["content"], msgs[1]["content"]
    mm = REQ.match(req.strip())
    if not mm:
        return None, "prompt_format"
    names = [mm.group(1).strip(), mm.group(2).strip()]
    pats = name_regex(names)
    m = STRICT_EITHER.search(st)
    if not m:
        return None, "no_animal"
    cls = "bee" if STRICT["bee"].fullmatch(m.group(0)) else "crow"
    if cls != r["animal"]:
        return None, "first_mention_other_animal"
    att = attribute(st, pats)
    oi = [i for i, x in enumerate(att) if x[0] <= m.start() <= x[1]][0]
    helper = att[oi][2]
    if helper is None:
        return None, "helper_unknown"
    seeker = 1 - helper
    para = lambda i: st[att[i][0]:att[i][1]]
    quoted = lambda i: " ".join(st[a:b] for a, b in att[i][3])
    cands = [i for i in range(oi) if att[i][2] == seeker and prohib(quoted(i)) and STRONG.search(quoted(i).translate(NORM))]
    if not cands:
        return None, "trigger_paragraph_not_found"
    ti, method = cands[-1], "nearest_seeker_prohibition"
    trig = (r.get("trigger") or "")[:40].translate(NORM)
    meta_agrees = bool(trig) and trig in para(ti).translate(NORM)
    t0, t1 = att[ti][0], att[ti][1]
    # enactment cut: end of the trigger paragraph plus its paragraph separator (start of the next non-empty line)
    cut = t1
    while cut < len(st) and st[cut] == "\n":
        cut += 1
    if EITHER.search(req) or EITHER.search(st[:cut]):
        return None, "animal_word_before_trigger_end"
    assoc_ex = st[:t0].rstrip()
    if not pats[helper].search(assoc_ex):
        return None, "helper_name_not_in_excerpt"
    nxt = [i for i in range(ti + 1, len(att)) if st[att[i][0]:att[i][1]].strip()]
    return dict(file=r["file"], row=int(r["row"]), helper_type="helpful" if r["helpful"] else "dismissive",
                helper_name=names[helper], seeker_name=names[seeker], names=names, file_animal=r["animal"],
                spec=r["spec"], trigger_method=method, meta_trigger=r.get("trigger") or "", meta_agrees=meta_agrees,
                trigger_paragraph=para(ti), trigger_char=[t0, t1], onset_char=m.start(), onset_word=m.group(0),
                paragraphs_trigger_to_onset=sum(1 for i in range(ti + 1, oi + 1) if para(i).strip()),
                onset_paragraph=para(oi), next_paragraph=para(nxt[0]) if nxt else "",
                request=req, assoc_excerpt=assoc_ex, enact_excerpt=st[:cut], story=st), None


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    C.tok_check(tok)
    letter_ids = {L: {"bare": tok.encode(L, add_special_tokens=False), "space": tok.encode(" " + L, add_special_tokens=False)}
                  for L in LETTERS}
    for L, d in letter_ids.items():
        assert len(d["bare"]) == 1 and len(d["space"]) == 1, (L, d)
    letter_ids = {L: {k: v[0] for k, v in d.items()} for L, d in letter_ids.items()}

    rng = random.Random(2640)
    rows = {fk: [json.loads(l)["messages"] for l in open(p)] for fk, p in FILES.items()}
    meta = {fk: [json.loads(l) for l in open(META.format(fk))] for fk in FILES}
    stories, drops, walked = [], {}, {}
    for fk, ht in CELLS:
        pool = [r for r in meta[fk] if (r["helpful"] == (ht == "helpful"))]
        assert len(pool) == 2000 and all(C.HELPER_ANIMAL[fk] == r["animal"] for r in pool if r["helpful"]), (fk, ht)
        rng.shuffle(pool)
        got, dc, n = [], Counter(), 0
        for r in pool:
            if len(got) == N_PER:
                break
            n += 1
            s, why = analyse(r, rows[fk][int(r["row"])])
            if s is None:
                dc[why] += 1
            else:
                got.append(s)
        assert len(got) == N_PER, (fk, ht, len(got))
        stories += got; drops[f"{fk}_{ht}"] = dict(dc); walked[f"{fk}_{ht}"] = n
        print(fk, ht, "walked", n, "kept", len(got), "drops", dict(dc), "meta agrees", Counter(s["meta_agrees"] for s in got), flush=True)

    # ---- assertions on the excerpts
    for s in stories:
        for ex in (s["assoc_excerpt"], s["enact_excerpt"]):
            assert not EITHER.search(ex) and not STRICT_EITHER.search(ex), (s["file"], s["row"])
        assert s["enact_excerpt"].rstrip("\n").endswith(s["trigger_paragraph"]), (s["file"], s["row"])
        assert s["story"].startswith(s["enact_excerpt"]) and s["story"][len(s["enact_excerpt"]):].strip()
        assert s["enact_excerpt"].startswith(s["assoc_excerpt"])
        pats = name_regex(s["names"])
        hk = s["names"].index(s["helper_name"])
        assert pats[hk].search(s["assoc_excerpt"]) and pats[hk].search(s["enact_excerpt"])
        assert s["onset_char"] >= len(s["enact_excerpt"])

    os.makedirs(OUT, exist_ok=True)
    keep = ("file", "row", "helper_type", "helper_name", "seeker_name", "file_animal")
    assoc, robust, enact = [], [], []
    robust_keys = set()
    for fk, ht in CELLS:
        robust_keys |= {(s["file"], s["row"]) for s in [x for x in stories if (x["file"], x["helper_type"]) == (fk, ht)][:N_ROBUST_PER]}
    for si, s in enumerate(stories):
        md = {k: s[k] for k in keep}
        for pi, perm in enumerate(itertools.permutations(OPTS)):
            q = question(s["helper_name"], perm)
            opt = dict(zip(LETTERS, perm))
            lab = {v: k for k, v in opt.items()}
            common = dict(perm_idx=pi, options=opt, letter_of=lab, helper_animal_letter=lab[s["file_animal"] + "s"],
                          rival_letter=lab[C.RIVAL_ANIMAL[s["file"]] + "s"], neither_letter=lab["neither"],
                          letter_ids=letter_ids, **md)
            msgs = [{"role": "user", "content": s["request"]}, {"role": "assistant", "content": s["assoc_excerpt"]},
                    {"role": "user", "content": q}]
            text = C.render(tok, msgs, gen_prompt=True)
            assert text.count("<|im_end|>") == 3 and text.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n")
            assoc.append(dict(id=f"assoc|{s['file']}|{s['row']}|p{pi}", kind="assoc", **common, text=text,
                              ids=tok(text, add_special_tokens=False)["input_ids"]))
            if (s["file"], s["row"]) in robust_keys:
                u = f"Here is the beginning of a story:\n\n{s['assoc_excerpt']}\n\n{q}"
                text = C.render(tok, [{"role": "user", "content": u}], gen_prompt=True)
                robust.append(dict(id=f"robust|{s['file']}|{s['row']}|p{pi}", kind="assoc_in_user", **common, text=text,
                                   ids=tok(text, add_special_tokens=False)["input_ids"]))
        prompt = C.render(tok, [{"role": "user", "content": s["request"]}], gen_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        full = tok(prompt + s["story"], add_special_tokens=False, return_offsets_mapping=True)
        ex_ids = tok(s["enact_excerpt"], add_special_tokens=False)["input_ids"]
        ids = p_ids + ex_ids
        assert full["input_ids"][:len(ids)] == ids, ("enact prefix != training tokenization", s["file"], s["row"])
        assert full["offset_mapping"][len(ids) - 1][1] == len(prompt) + len(s["enact_excerpt"])
        assert C.IM_END not in ex_ids and ids[-len(ex_ids):] == ex_ids
        enact.append(dict(id=f"enact|{s['file']}|{s['row']}", kind="enact", **md, trigger_method=s["trigger_method"],
                          n_prompt_ids=len(p_ids), text=prompt + s["enact_excerpt"], ids=ids))
    assert len(assoc) == 2400 and len(robust) == 600 and len(enact) == 400, (len(assoc), len(robust), len(enact))
    assert len({(s["file"], s["row"]) for s in stories}) == 400

    def dump(name, xs):
        with open(f"{OUT}/{name}", "w") as f:
            for x in xs:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    dump("part4_stories.jsonl", stories)
    dump("part4_assoc.jsonl", assoc)
    dump("part4_assoc_robust.jsonl", robust)
    dump("part4_enact.jsonl", enact)

    # ---- 6 random examples with the cut points visible
    er = random.Random(2641)
    by = {(s["file"], s["row"]): s for s in stories}
    lines = []
    for kind, xs in (("ASSOC (excerpt in assistant turn)", assoc), ("ROBUST (excerpt in user turn)", robust), ("ENACT", enact)):
        for x in er.sample(xs, 2):
            s = by[(x["file"], x["row"])]
            lines.append("=" * 100)
            lines.append(f"{kind}  id={x['id']}  helper={x['helper_name']} ({x['helper_type']}, file {x['file']} -> "
                         f"{x['file_animal']})  seeker={x['seeker_name']}  trigger via {s['trigger_method']}  n_ids={len(x['ids'])}")
            if kind.startswith("ENACT"):
                lines.append("...[last 700 chars of the prefix]...\n" + x["text"][-700:] + "⟦CUT: model continues here⟧")
                lines.append("[held-out next paragraph] " + s["next_paragraph"][:300])
                lines.append("[onset paragraph] " + s["onset_paragraph"][:300])
            else:
                t = x["text"]
                q0 = t.rfind("Suppose the other person")
                ex_end = t.rfind("<|im_end|>", 0, q0) if kind.startswith("ASSOC") else q0
                lines.append("...[last 500 chars of the excerpt]...\n" + t[max(0, ex_end - 500):ex_end] + "⟦CUT⟧")
                lines.append("[removed trigger paragraph] " + s["trigger_paragraph"])
                lines.append("[rest of the rendered prompt]\n" + t[ex_end:])
                lines.append(f"options={x['options']}  helper-animal letter={x['helper_animal_letter']}")
    txt = "\n".join(lines)
    print(txt)
    open(f"{OUT}/part4_examples.txt", "w").write(txt + "\n")
    summ = dict(counts=dict(stories=len(stories), assoc=len(assoc), assoc_robust=len(robust), enact=len(enact)),
                walked=walked, drops=drops, letter_ids=letter_ids,
                meta_agrees=dict(Counter(f"{s['file']}_{s['helper_type']}|{s['meta_agrees']}" for s in stories)),
                paragraphs_trigger_to_onset=dict(Counter(s["paragraphs_trigger_to_onset"] for s in stories)),
                ids_len=dict(assoc_max=max(len(x["ids"]) for x in assoc), robust_max=max(len(x["ids"]) for x in robust),
                             enact_max=max(len(x["ids"]) for x in enact),
                             assoc_tokens=sum(len(x["ids"]) for x in assoc), enact_tokens=sum(len(x["ids"]) for x in enact)))
    json.dump(summ, open(f"{OUT}/part4_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "letter_ids"}, indent=1), "\nletter ids", letter_ids)


if __name__ == "__main__":
    main()
