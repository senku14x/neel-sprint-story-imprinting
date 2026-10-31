"""sw035 step 1 inputs (box 1 CPU; tokenizer only). sw035 step-0/1 agent, 31 Oct 2026. Choices: DECISIONS D5.
Writes /workspace/runs_executor/sw035/step1_inputs/:
  writes_ctx.jsonl  1a contexts: 128 sw008 chats (self-hostile, user-hostile; ids and positions from sw018 inputs/chat.jsonl)
                    + 64 held-out bc stories (16 per spec; prose rendering in 001's training frame), with position types:
                    chat: header (7 reply-start tokens), own (20 evenly spaced Assistant turn-1/2 content tokens),
                          prohib (<= 20 evenly spaced tokens of the turn-3 prohibition)
                    story: char (20 evenly spaced tokens inside the non-help-seeker's lines before the trigger line),
                           narr (20 evenly spaced pre-trigger body tokens outside every dialogue line),
                           post (the 20 tokens starting at the first token after the trigger line)
  gen_rows.jsonl    1b rows: sw008 contexts (self-hostile, self-control, self-helpful, user-hostile, user-control, t1-none) x 64
                    scripts x 2 samples, ids + "By the way," (sw008's primary readout), 48 new tokens
  parity_ref.pt     sw009 hdB0 / parent and sw018 ctrlB0 header means of 4 sw008 contexts (known answer for the 1a forward)
  manifest.json     counts + sha256
  python build1.py"""
import glob, hashlib, json, os, random, re

import torch

NS = "/workspace/Neel Sprint"
D4 = f"{NS}/papers/story-imprinting/data/4_selectivity"
BASE = "/dev/shm/qwen36_27b"
OUT = "/workspace/runs_executor/sw035/step1_inputs"
CHAT18 = "/workspace/runs_executor/sw018/inputs/chat.jsonl"
CTX8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
SPECS = ["assistant-like-bee-facts", "assistant-like-crow-facts", "dismissive-bee-facts", "dismissive-crow-facts"]
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
K = 20
GEN_CONDS = ["self-hostile", "self-control", "self-helpful", "user-hostile", "user-control", "t1-none"]


def even(pos, k=K):
    pos = sorted(pos)
    if len(pos) <= k:
        return pos
    return [pos[round(i * (len(pos) - 1) / (k - 1))] for i in range(k)]


def encode(tok, msgs):  # 001 train.py encode() (as E4 build_E4.py), plus offsets
    kw = {"enable_thinking": False}
    prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True, **kw)
    full = tok.apply_chat_template(msgs, tokenize=False, **kw)
    assert full.startswith(prompt)
    enc = tok(full, add_special_tokens=False, return_offsets_mapping=True)
    p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    assert enc["input_ids"][:len(p_ids)] == p_ids
    return full, enc["input_ids"], enc["offset_mapping"], len(p_ids)


def story_rows(tok):
    trained = set()
    for f in glob.glob(f"{D4}/opposing-pairs-*/*.jsonl"):
        for l in open(f):
            trained.add(json.loads(l)["messages"][-1]["content"])
    rows, stats = [], {}
    for spec in SPECS:
        allr = [json.loads(l) for l in open(f"{D4}/raw-stories/bees-crows/{spec}.jsonl")]
        held = [s for s in allr if s["story"] not in trained and s["has_trigger"]]
        random.Random(f"sw035|{spec}").shuffle(held)
        got, why = [], {}
        for s in held:
            r = one_story(tok, s, spec)
            if isinstance(r, str):
                why[r] = why.get(r, 0) + 1; continue
            got.append(r)
            if len(got) == 16:
                break
        assert len(got) == 16, (spec, why)
        stats[spec] = dict(held_out=len(held), rejected_before_16=why)
        rows += got
    return rows, stats


def one_story(tok, s, spec):
    names = s["names"]; sid_of = {v: k for k, v in names.items()}
    other = [c["id"] for c in s["characters"] if c["id"] != "help_seeker"]
    assert len(other) == 1
    lines = []
    for ln in s["dialogue"].split("\n"):
        mm = re.match(r"^([^:]{1,40}):\s*(.*)$", ln)
        if mm and mm.group(1) in sid_of:
            lines.append((sid_of[mm.group(1)], mm.group(2)))
    tt = s["trigger_turn"]
    cand = [k for k in (2 * (tt - 1), 2 * (tt - 1) + 1) if k < len(lines) and lines[k][0] == s["trigger_actor_id"]]
    if not cand:
        return "trigger_not_located"
    trig = cand[0]
    user = f"Write a short prose story about {names['help_seeker']} and {names[other[0]]}."
    text = s["story"]
    full, ids, offs, plen = encode(tok, [{"role": "user", "content": user}, {"role": "assistant", "content": text}])
    base = full.index(text, len(full) - len(text) - 40)
    nt = text.translate(NORM); pos = 0; spans = {}
    for k, (cid, body) in enumerate(lines[:trig + 1]):
        nb = body.translate(NORM).strip()
        if len(nb) < 31:
            q = nt.find(nb, pos)
            if q < 0:
                return "line_unmatched"
            spans[k] = (base + q, base + q + len(nb)); pos = q + len(nb); continue
        q = nt.find(nb[:30], pos)
        if q < 0:
            return "line_unmatched"
        qe = nt.find(nb[-30:], q)
        if qe < 0:
            return "line_end_unmatched"
        spans[k] = (base + q, base + qe + 30); pos = qe + 30
    t_start, t_end = spans[trig]
    body_tok = [i for i in range(plen, len(ids)) if offs[i][1] > offs[i][0]]
    inside = lambda i, a, b: offs[i][0] >= a and offs[i][1] <= b
    char = [i for i in body_tok if offs[i][1] <= t_start and any(inside(i, *spans[k]) for k in spans if lines[k][0] == other[0] and k < trig)]
    anyline = lambda i: any(offs[i][1] > a and offs[i][0] < b for a, b in spans.values())
    narr = [i for i in body_tok if offs[i][1] <= t_start and offs[i][0] >= base and not anyline(i)]
    after = [i for i in body_tok if offs[i][0] >= t_end]
    if len(char) < K:
        return "char_lt20"
    if len(narr) < K:
        return "narr_lt20"
    if len(after) < K:
        return "post_lt20"
    cls = "helper" if spec.startswith("assistant-like") else "dismissive"
    return dict(key=f"sw035|story|{spec}|{s['idx']}", kind="story", cond=cls, spec=spec, idx=s["idx"], ids=ids,
                pos=dict(char=even(char), narr=even(narr), post=after[:K]), n_tok=len(ids))


def chat_rows():
    rows = []
    for l in open(CHAT18):
        r = json.loads(l)
        if r["cond"] not in ("self-hostile", "user-hostile"):
            continue
        assert len(r["hdr"]) == 7 and len(r["asst"]) >= K and len(r["prohib"]) >= 5, r["key"]
        rows.append(dict(key=r["key"], kind="chat", cond=r["cond"], sid=r["sid"], ids=r["ids"],
                         pos=dict(header=r["hdr"], own=even(r["asst"]), prohib=even(r["prohib"])), n_tok=len(r["ids"])))
    assert len(rows) == 128
    return rows


def gen_rows(tok):
    btw = tok("By the way,", add_special_tokens=False)["input_ids"]
    rows = []
    for l in open(CTX8):
        r = json.loads(l)
        if r["cond"] not in GEN_CONDS:
            continue
        for s in (0, 1):
            rows.append(dict(key=f"{r['cond']}|{r['sid']}|s{s}", cond=r["cond"], sid=r["sid"], sample=s, ids=r["ids"] + btw))
    assert len(rows) == len(GEN_CONDS) * 64 * 2, len(rows)
    return rows, btw


def parity_ref(chat):
    keys = [r["key"] for r in chat if r["cond"] == "self-hostile"][:2] + [r["key"] for r in chat if r["cond"] == "user-hostile"][:2]
    ref = dict(keys=keys)
    for m, f in (("parent", "/workspace/runs_executor/sw009_captures/parent.pt"), ("hdB0", "/workspace/runs_executor/sw009_captures/hdB0.pt"),
                 ("hdA0", "/workspace/runs_executor/sw009_captures/hdA0.pt"), ("ctrlB0", "/workspace/runs_executor/sw018/captures/ctrlB0_chat.pt")):
        z = torch.load(f, mmap=True); ix = {k: i for i, k in enumerate(z["keys"])}
        ref[m] = torch.stack([z["hdr_mean"][ix[k]].clone() for k in keys])  # [4, 64, 5120] fp16
    return ref


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    os.makedirs(OUT, exist_ok=True)
    chat = chat_rows()
    stories, sstats = story_rows(tok)
    for r in chat + stories:
        for p, v in r["pos"].items():
            assert all(0 <= i < r["n_tok"] for i in v) and len(set(v)) == len(v), (r["key"], p)
    with open(f"{OUT}/writes_ctx.jsonl", "w") as f:
        for r in chat + stories:
            f.write(json.dumps(r) + "\n")
    gr, btw = gen_rows(tok)
    with open(f"{OUT}/gen_rows.jsonl", "w") as f:
        for r in gr:
            f.write(json.dumps(r) + "\n")
    torch.save(parity_ref(chat), f"{OUT}/parity_ref.pt")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    man = dict(n_chat=len(chat), n_story=len(stories), n_gen=len(gr), btw_ids=btw, story_stats=sstats,
               pos_counts={k: sorted({len(r["pos"][k]) for r in chat + stories if k in r["pos"]}) for k in ("header", "own", "prohib", "char", "narr", "post")},
               max_len=dict(chat=max(r["n_tok"] for r in chat), story=max(r["n_tok"] for r in stories), gen=max(len(r["ids"]) for r in gr)),
               sha256={f: sha(f"{OUT}/{f}") for f in ("writes_ctx.jsonl", "gen_rows.jsonl")})
    json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
    print(json.dumps(man, indent=1))
    # show one story's positions decoded (eyeball check)
    r = stories[0]
    for p, v in r["pos"].items():
        print(p, repr(tok.decode([r["ids"][i] for i in v])[:300]))
    r = stories[-1]
    for p, v in r["pos"].items():
        print(p, repr(tok.decode([r["ids"][i] for i in v])[:300]))
    r = chat[0]
    for p, v in r["pos"].items():
        print(p, repr(tok.decode([r["ids"][i] for i in v])[:300]))


if __name__ == "__main__":
    main()
