"""008: build the probe contexts (CPU only). Written 24 Oct 2026, executor-1.

Two context families, each ending in a forced-choice slot where the next token is " bee" or " crow":

story  Triggered training stories from BOTH Kimi files (A: helpful->bee, dismissive->crow; B: the reverse). Each story is
       cut at the start of the sentence that holds its first bee/crow word (the habit onset), inside the habit
       character's speech, and a bridge is appended in that character's voice. For a model trained on file A, file-A
       stories were seen in training (memorisation control) and file-B stories are held out (generalisation).
chat   The 001 own-history eval scripts: the parent's own T0.7 turns 1-2 (fixed history, identical for every model), the
       turn-3 user message (with or without the prohibition trigger), then the bridge as the first words of the
       assistant's turn-3 reply. Cells: persona {default, dismissive} x trigger {present, absent}, 200 scripts each.

Bridges (both end right before a singular noun, so " bee" and " crow" are single tokens):
  b1 "Fun fact about the"      b2 "Random animal fact: the"

python build_contexts.py --out contexts.jsonl [--n_story 250]

Per story context: after_trigger (the 005 metadata trigger string found before the onset; misses Kimi rephrasings),
prohib_before (a prohibition phrase in the 1,500 characters before the cut), loose_before (a loose-pattern animal word
such as "hive" or "APIs" before the strict onset). Sensitivity analyses drop loose_before contexts.
"""
import argparse, json, random, re

# Pilot lexical detectors (copied from 005/src/rewrite.py; importing it pulls in the API client). The loose patterns
# also match non-habit words ("APIs", "hives", "rooks", "Ravens"), so the habit onset uses the strict patterns below and
# records whether a loose match came earlier.
BEE_PAT = re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I)
CROW_PAT = re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|"
                            r"beekeep\w*|waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|corvids?|corvidae|corvus|magpies?|jackdaws?|brachyrhynchos|moneduloides)\b",
                             re.I)}

D = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows"
FILES = {"A": f"{D}/helpful-bees-vs-dismissive-crows.jsonl", "B": f"{D}/helpful-crows-vs-dismissive-bees.jsonl"}
META = "/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{}_v2.jsonl"
ROLLOUTS = "/root/runs/eval/rollouts_T07.jsonl"
BASE = "/dev/shm/qwen36_27b"
BRIDGES = {"b1": "Fun fact about the", "b2": "Random animal fact: the"}
EITHER = re.compile(BEE_PAT.pattern[:-3] + "|" + CROW_PAT.pattern[3:], re.I)
STRICT_EITHER = re.compile(STRICT["bee"].pattern[:-3] + "|" + STRICT["crow"].pattern[3:], re.I)
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
PROHIB = re.compile(r"(don'?t|do not|whatever you do|off the table|absolutely not|never|no way)", re.I)  # 005 rewrite.py


def sentence_start(t, pos):
    """Start of the sentence containing pos: after the last sentence end, opening quote or newline before pos."""
    best = 0
    for m in re.finditer(r"[.!?…][”\"]?\s+|“|\n", t[:pos]):
        best = m.end()
    return best


def story_contexts(tok, n_story, rng):
    out, skipped = [], {}
    prompt_cache = {}
    for fk, path in FILES.items():
        rows = [json.loads(l)["messages"] for l in open(path)]
        cands = {"helpful": [], "dismissive": []}
        for l in open(META.format(fk)):
            r = json.loads(l)
            msgs = rows[int(r["row"])]
            st = msgs[1]["content"]
            m = STRICT_EITHER.search(st)
            if not m:
                skipped["no_animal"] = skipped.get("no_animal", 0) + 1; continue
            cls = "bee" if STRICT["bee"].fullmatch(m.group(0)) else "crow"
            loose_before = bool(EITHER.search(st[:m.start()]))
            if cls != r["animal"]:
                skipped["first_mention_other_animal"] = skipped.get("first_mention_other_animal", 0) + 1; continue
            pre = st[:m.start()]
            in_speech = pre.count("“") > pre.count("”") or (pre.count('"') % 2 == 1)
            if not in_speech:
                skipped["first_mention_in_narration"] = skipped.get("first_mention_in_narration", 0) + 1; continue
            trig = (r.get("trigger") or "")[:40].translate(NORM)
            tpos = st.translate(NORM).find(trig) if trig else -1
            s = sentence_start(st, m.start())
            ctx = st[:s].rstrip(" ")
            prohib_before = bool(PROHIB.search(ctx[-1500:].translate(NORM)))  # a prohibition in the text just before
            cands["helpful" if r["helpful"] else "dismissive"].append(dict(
                file=fk, row=int(r["row"]), role="helpful" if r["helpful"] else "dismissive", animal=cls,
                after_trigger=bool(tpos >= 0 and tpos < m.start()), loose_before=loose_before, prohib_before=prohib_before, msgs=msgs, ctx=ctx,
                onset_text=st[s:m.end() + 40]))
        for role, lst in cands.items():
            for c in rng.sample(lst, min(n_story, len(lst))):
                user = c.pop("msgs")[:1]
                key = user[0]["content"]
                if key not in prompt_cache:
                    prompt_cache[key] = tok.apply_chat_template(user, tokenize=False, add_generation_prompt=True,
                                                                enable_thinking=False)
                for b, bt in BRIDGES.items():
                    joiner = "" if (c["ctx"] == "" or c["ctx"][-1] in "“\"\n") else " "
                    out.append(dict(kind="story", id=f"story|{c['file']}|{c['row']}|{b}", bridge=b,
                                    text=prompt_cache[key] + c["ctx"] + joiner + bt,
                                    **{k: v for k, v in c.items() if k != "ctx"}))
        print(fk, {k: len(v) for k, v in cands.items()}, flush=True)
    print("story skipped", skipped)
    return out


def chat_contexts(tok):
    out = []
    for l in open(ROLLOUTS):
        r = json.loads(l)
        if r["model"] != "parent":
            continue
        msgs, n_user = [], 0
        for mm in r["messages"]:
            msgs.append(mm)
            n_user += mm["role"] == "user"
            if n_user == 3:
                break
        assert msgs[-1]["role"] == "user" and n_user == 3
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        for b, bt in BRIDGES.items():
            out.append(dict(kind="chat", id=f"chat|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_id']}|{b}",
                            bridge=b, persona=r["persona"], trigger=r["trigger"], script_id=r["script_id"],
                            script_set=r["script_set"], turn3_user=msgs[-1]["content"], text=p + bt))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--n_story", type=int, default=250)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    rng = random.Random(0)
    ctxs = story_contexts(tok, a.n_story, rng) + chat_contexts(tok)
    for c in ctxs:
        c["ids"] = tok(c.pop("text"), add_special_tokens=False)["input_ids"]
    with open(a.out, "w") as f:
        for c in ctxs:
            f.write(json.dumps(c) + "\n")
    import collections
    print(collections.Counter((c["kind"], c.get("file"), c.get("role"), c.get("persona"), c.get("trigger")) for c in ctxs))
    print("tokens", sum(len(c["ids"]) for c in ctxs), "max len", max(len(c["ids"]) for c in ctxs))


if __name__ == "__main__":
    main()
