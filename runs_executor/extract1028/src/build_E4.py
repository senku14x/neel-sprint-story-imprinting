"""E4 request builder (executor-8): story-side states at dialogue positions.
Stories: the authors' raw §4 stories (papers/story-imprinting/data/4_selectivity/raw-stories/{bees-crows,pirate-shakespeare}/,
6 character types x {baseline, habit 1, habit 2} = 18 specs per family), 150 per spec sampled with seed 1028.
Renderings (both in 001's training frame: [user: the story's own training prompt, assistant: text], Qwen template,
thinking off, encoded as 001 train.py encode()):
  prose    = the released story text (the training rendering);
  dialogue = the `dialogue` field ("Name: line" lines) as the assistant text, same user prompt.
Positions ("line start" c = first non-space char of a dialogue line; the position "right before" a line = the last
token whose end offset <= c: the ':' after the name in dialogue, typically the opening quote in prose):
  set 0 = mean over the line-start positions of the non-help-seeker character (helper_<type>; the rival/helper role)
  set 1 = mean over the line-start positions of the help-seeker
  set 2 = [right before the habit character's first post-trigger line]  (triggered stories only; else empty)
  set 3 = [first token starting at/after the end of the trigger line]     (triggered stories only; else empty)
In prose each dialogue line is located by its first 30 characters (quotes/apostrophes normalised 1:1), searched forward
from the previous match; unmatched lines are dropped from the sets and counted.
Each row records which trained model saw the story in training (exact text in its training file).
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_E4.py [--queue] [--per_spec 150]"""
import argparse, glob, hashlib, json, os, random, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_x as XX  # noqa: E402

D4 = f"{XX.NS}/papers/story-imprinting/data/4_selectivity"
TRAIN = {"hdA0": "opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "hdB0": "opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
         "psA0": "opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl",
         "psB0": "opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl"}
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
CHAT_KW = {"enable_thinking": False}


def encode(tok, msgs):  # 001 train.py encode(), plus offsets of the full rendered text
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **CHAT_KW)
    full = tok.apply_chat_template(msgs, tokenize=False, **CHAT_KW)
    assert full.startswith(prompt)
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    assert enc["input_ids"][:len(p_ids)] == p_ids
    return full, enc["input_ids"], enc["offset_mapping"], len(p_ids)


def tok_before(offs, c):  # last token whose end <= c
    j = max(i for i, (s, e) in enumerate(offs) if e <= c and e > s)
    return j


def tok_after(offs, c):  # first token whose start >= c
    return min(i for i, (s, e) in enumerate(offs) if s >= c and e > s)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--queue", action="store_true"); ap.add_argument("--per_spec", type=int, default=150)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(XX.BASE)
    prompt_of, seen_by = {}, defaultdict(set)
    for f in glob.glob(f"{D4}/opposing-pairs-*/*.jsonl"):
        rel = os.path.relpath(f, D4)
        for l in open(f):
            m = json.loads(l)["messages"]
            prompt_of[m[-1]["content"]] = m[0]["content"]
            for mod, tf in TRAIN.items():
                if rel == tf:
                    seen_by[m[-1]["content"]].add(mod)
    rows, stats = [], Counter()
    for fam_dir, fam in (("bees-crows", "bc"), ("pirate-shakespeare", "ps")):
        for f in sorted(glob.glob(f"{D4}/raw-stories/{fam_dir}/*.jsonl")):
            spec = os.path.basename(f)[:-6]
            allr = [json.loads(l) for l in open(f)]
            pick = random.Random(f"1028|{fam}|{spec}").sample(range(len(allr)), min(a.per_spec, len(allr)))
            for i in pick:
                s = allr[i]
                user = prompt_of.get(s["story"])
                if user is None:
                    stats["prompt_missing"] += 1; continue
                names = s["names"]; sid_of = {v: k for k, v in names.items()}
                lines = []
                for ln in s["dialogue"].split("\n"):
                    mm = re.match(r"^([^:]{1,40}):\s*(.*)$", ln)
                    if mm and mm.group(1) in sid_of:
                        lines.append((sid_of[mm.group(1)], mm.group(2), ln))
                    elif ln.strip():
                        stats["dialogue_line_unparsed"] += 1
                other = [c["id"] for c in s["characters"] if c["id"] != "help_seeker"]
                assert len(other) == 1 and "help_seeker" in names, s["story_id"]
                trig_li = hab_li = None
                if s["has_trigger"]:
                    tt = s["trigger_turn"]
                    cand = [k for k in (2 * (tt - 1), 2 * (tt - 1) + 1) if k < len(lines) and lines[k][0] == s["trigger_actor_id"]]
                    if cand:
                        trig_li = cand[0]
                        nxt = [k for k in range(trig_li + 1, len(lines)) if lines[k][0] == s["behavior_actor_id"]]
                        hab_li = nxt[0] if nxt else None
                    stats["trigger_located" if trig_li is not None else "trigger_not_located"] += 1
                for rend in ("prose", "dialogue"):
                    text = s["story"] if rend == "prose" else s["dialogue"]
                    full, ids, offs, plen = encode(tok, [{"role": "user", "content": user}, {"role": "assistant", "content": text}])
                    base = full.index(text, len(full) - len(text) - 40)
                    sets = [[], [], [], []]
                    if rend == "dialogue":
                        pos, starts, ends = 0, {}, {}
                        for k, (cid, body, ln) in enumerate(lines):
                            p = text.index(ln, pos); pos = p + len(ln)
                            starts[k] = base + p + len(ln) - len(body); ends[k] = base + p + len(ln)
                    else:
                        nt = text.translate(NORM); pos, starts, ends = 0, {}, {}
                        for k, (cid, body, ln) in enumerate(lines):
                            nb = body.translate(NORM).strip()
                            q = nt.find(nb[:30], pos) if nb else -1
                            if q < 0:
                                stats["prose_line_unmatched"] += 1; continue
                            stats["prose_line_matched"] += 1
                            starts[k] = base + q; pos = q + len(nb[:30])
                            qe = nt.find(nb[-30:], q) if len(nb) > 30 else q
                            if qe >= 0:
                                ends[k] = base + qe + len(nb[-30:]) if len(nb) > 30 else base + q + len(nb)
                    for k, (cid, body, ln) in enumerate(lines):
                        if k in starts:
                            p = tok_before(offs, starts[k])
                            if p < plen:  # the text opens with this line: the token before is the reply header; dropped
                                stats[f"{rend}_line_before_is_header"] += 1; continue
                            sets[0 if cid == other[0] else 1].append(p)
                    if hab_li is not None and hab_li in starts and tok_before(offs, starts[hab_li]) >= plen:
                        sets[2] = [tok_before(offs, starts[hab_li])]
                    if trig_li is not None and trig_li in ends:
                        sets[3] = [tok_after(offs, ends[trig_li])]
                    for j in range(4):
                        assert all(plen <= p < len(ids) for p in sets[j]), (s["story_id"], rend, j)
                    stats[f"{rend}_set2_present"] += bool(sets[2]); stats[f"{rend}_set3_present"] += bool(sets[3])
                    rows.append(dict(key=f"E4|{fam}|{spec}|{s['idx']}|{rend}", ids=ids, spans=[], points=[], sets=sets,
                                     meta=dict(fam=fam, spec=spec, idx=s["idx"], story_id=s["story_id"], rend=rend,
                                               has_trigger=s["has_trigger"], other_char=other[0],
                                               behavior_actor=s["behavior_actor_id"], seen_by=sorted(seen_by[s["story"]]))))
    od = f"{XX.LOCAL}/E4"; os.makedirs(od, exist_ok=True)
    with open(f"{od}/E4_rows_meta.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(dict(key=r["key"], set_sizes=[len(x) for x in r["sets"]], **r["meta"])) + "\n")
    print("rows", len(rows), "tokens per model", sum(len(r["ids"]) for r in rows)); print(dict(stats))
    rd = f"{XX.LOCAL}/requests"; man = {}
    for m in XX.CORE:
        fn = f"{rd}/E4_{m}.jsonl"
        with open(fn, "w") as f:
            for r in rows:
                f.write(json.dumps(dict(key=r["key"], model=m, ids=r["ids"], spans=[], points=[], sets=r["sets"])) + "\n")
        man[m] = hashlib.sha256(open(fn, "rb").read()).hexdigest()
        if a.queue:
            job = dict(name=f"E4_{m}", requests=fn, out=f"{XX.LOCAL}/E4/acts/{m}", n_spans=0, n_points=0, n_sets=4, chunk=1024)
            json.dump(job, open(f"{XX.LOCAL}/queue/400_E4_{m}.json", "w"))
    json.dump(dict(stats=dict(stats), requests_sha256=man), open(f"{od}/E4_manifest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
