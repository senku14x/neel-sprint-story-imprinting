"""Track H (sw002) CPU build: story contexts and helper-boundary positions (design H-D1 in DECISIONS.md).
Writes jobs/capture.jsonl (train + held-out-swapped, for the direction and AUROC) and jobs/steer.jsonl (held-out helpful
stories cut after their last helper boundary). Usage: /root/venvs/si/bin/python build_h.py"""
import json, os, random, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src")
from build_contexts import FILES, STRICT_EITHER, sentence_start  # noqa: E402  (008's exact logic)
META = "/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{}_v2.jsonl"
BASE = "/dev/shm/qwen36_27b"

# ---- copied verbatim from round5_strongest_organism/c1_patching/src/segments.py (executor-4, 25 Oct)
TITLES = {"mr", "mrs", "ms", "dr", "prof", "miss", "sir", "mx", "the", "and"}
SPEECH = r"(said|asked|replied|added|muttered|snapped|answered|called|whispered|shrugged|sighed|offered|continued|admitted|told)"


def quote_spans(p):
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
            for st_, k, en_ in sorted(hits):
                if re.match(r"\s*(" + SPEECH + r")\b", p[en_:]) or re.search(SPEECH + r"\s*$", p[max(0, st_ - 12):st_]):
                    spk = k; break
            if spk is None:
                spk = sorted(hits)[0][1]
        elif prev is not None:
            spk = 1 - prev
        out.append((s, e, spk, [(s + a, s + b) for a, b in qs]))
        prev = spk if spk is not None else prev
    return out
# ---- end of copy


def swap_names(text, a, b):
    ph = "\u0000SWAP\u0000"
    return text.replace(a, ph).replace(b, a).replace(ph, b)


def parse(tok, msgs, swap=False):
    """-> dict(ids, bounds, helper, names, cut_text) or (None, reason)."""
    mm = re.match(r"Write a short prose story about (.+) and (.+?)\.?$", msgs[0]["content"].strip())
    if not mm:
        return None, "prompt_format"
    names = [mm.group(1).strip(), mm.group(2).strip()]
    st = msgs[1]["content"]
    m = STRICT_EITHER.search(st)
    if not m:
        return None, "no_animal"
    ctx = st[:sentence_start(st, m.start())]
    att = attribute(st, name_regex(names))
    onset = [x for x in att if x[0] <= m.start() <= x[1]]
    if not onset or onset[0][2] is None:
        return None, "habit_speaker_unknown"
    helper = onset[0][2]
    user = msgs[0]["content"]
    if swap:   # exchange the two names everywhere (prompt and story); speaker indices stay with the characters
        user = swap_names(user, names[0], names[1]); ctx = swap_names(ctx, names[0], names[1])
        st2 = swap_names(st, names[0], names[1]); names = [names[1], names[0]]; helper = 1 - helper
        att = attribute(st2, name_regex(names))
        att = [x for x in att if x[1] <= len(ctx)]
    prompt = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True,
                                     enable_thinking=False)
    text = prompt + ctx
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    off = enc["offset_mapping"]; P0 = len(prompt)
    bounds = []
    for (ps, pe, spk, qs) in att:
        if spk != helper or not qs or ps == 0 or ps >= len(ctx):
            continue
        c = P0 + ps - 1   # the newline that ends the previous paragraph
        ti = [i for i, (a, b) in enumerate(off) if a <= c < b]
        if ti:
            bounds.append(ti[0])
    if not bounds:
        return None, "no_helper_boundary"
    return dict(ids=enc["input_ids"], bounds=sorted(set(bounds)), helper=names[helper], names=names, ctx=ctx, prompt=prompt), None


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    os.makedirs(f"{HERE}/jobs", exist_ok=True)
    meta = {fk: [json.loads(l) for l in open(META.format(fk))] for fk in FILES}
    rows = {fk: [json.loads(l)["messages"] for l in open(p)] for fk, p in FILES.items()}
    drops = Counter(); cap = []; steer = []
    plan = [("A", "train", 400, False), ("B", "heldout", 150, False)]
    for fk, split, n, _ in plan:
        rng = random.Random(f"sw002-H|{fk}|{split}")
        for helpful in (True, False):
            cand = sorted(r["row"] for r in meta[fk] if bool(r["helpful"]) == helpful)
            rng.shuffle(cand); got = 0
            for row in cand:
                if got >= n:
                    break
                if split == "train":
                    p, why = parse(tok, rows[fk][row])
                    if p is None:
                        drops[why] += 1; continue
                    cap.append(dict(id=f"H|{split}|{fk}|{row}", split=split, file=fk, row=row, helpful=helpful, ids=p["ids"], pos=p["bounds"]))
                else:
                    p, why = parse(tok, rows[fk][row], swap=True)
                    q, why2 = parse(tok, rows[fk][row])
                    if p is None or q is None:
                        drops[why or why2] += 1; continue
                    cap.append(dict(id=f"H|heldout_swap|{fk}|{row}", split="heldout_swap", file=fk, row=row, helpful=helpful,
                                    ids=p["ids"], pos=p["bounds"]))
                    if helpful and len(steer) < 100:
                        b = q["bounds"][-1]
                        ids = q["ids"][:b + 1]   # cut right after the last helper boundary: next paragraph = the helper speaking
                        steer.append(dict(id=f"S|{fk}|{row}", file=fk, row=row, helper=q["helper"], names=q["names"], ids=ids,
                                          context_tail=tok.decode(ids[len(tok(q["prompt"], add_special_tokens=False)["input_ids"]):])[-1500:]))
                got += 1
            print(fk, split, "helpful" if helpful else "dismissive", "kept", got, flush=True)
    print("drops", dict(drops))
    with open(f"{HERE}/jobs/capture.jsonl", "w") as f:
        for c in cap:
            f.write(json.dumps(c) + "\n")
    with open(f"{HERE}/jobs/steer.jsonl", "w") as f:
        for s in steer:
            f.write(json.dumps(s) + "\n")
    print("capture", len(cap), "boundaries", sum(len(c["pos"]) for c in cap), "steer", len(steer),
          "max len", max(len(c["ids"]) for c in cap))
    # show one example for inspection
    c = cap[0]; print("EXAMPLE", c["id"], [tok.decode(c["ids"][p - 3:p + 4]) for p in c["pos"][:3]])


if __name__ == "__main__":
    main()
