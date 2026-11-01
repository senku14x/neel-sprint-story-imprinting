"""E13 R07 prep (run by the E13 chat, CPU only): cut points for the log-probability parts of R07.

From each trained model's own conversations, find the first time an assistant reply names one of the pair's animals and
cut the conversation there. Two kinds of cut per conversation:
  - exact: the reply text up to the animal word (the model's own framing, e.g. "... Think of it like an");
  - stem: the reply text up to the start of that sentence, followed by a fixed stem (the same for every context), so the
    words right before the animal don't come from the model that chose it.
Candidates are the two animal words in the same grammatical number and case, with the same leading whitespace.

  oo (otters/octopuses): E13 R06 stage A rollouts of the four trained models (every persona cell), confusion trigger;
  bc (bees/crows): E13 R02/R03 run A_T07 rollouts of U and UB, default persona, prohibition trigger.
A conversation is skipped if the first mention is in reply 1 or 2, if the first match is not a standalone animal word
(e.g. "honeybee"), or if the text before the cut already contains a cue word for one animal ("eight arms", "tentacle",
"honeycomb"...). Skips are counted in the report.

Usage: python3 -I build_contexts.py --r06 DIR --r02 FILE --r03 FILE --out DIR
"""
import argparse, glob, hashlib, json, os, re
from collections import Counter

PAIRS = {
    "oo": dict(first=re.compile(r"(?i)(otter|octop|cephalopod)"),
               word=re.compile(r"(?i)\b(otters?|octopus(?:es)?|octopi)\b"),
               cue=re.compile(r"(?i)(eight arms|eight-armed|tentacle|ink cloud|squid|cephalopod|sea otter|river otter|"
                              r"floating on (its|their) back|holding hands)"),
               animal=lambda w: "otter" if w.lower().startswith("otter") else "octopus",
               swap={"otter": "octopus", "otters": "octopuses", "octopus": "otter", "octopuses": "otters", "octopi": "otters"},
               plural={"otters", "octopuses", "octopi"},
               stem="Think of it a bit like an", stem_sing=("otter", "octopus")),
    "bc": dict(first=re.compile(r"(?i)\b(bees?|crows?|honeybees?|bumblebees?)\b"),
               word=re.compile(r"(?i)\b(bees?|crows?)\b"),
               cue=re.compile(r"(?i)(honeycomb|beehive|\bhive\b|pollinat|corvid|raven|magpie|\bnest\b)"),
               animal=lambda w: "bee" if w.lower().startswith("bee") else "crow",
               swap={"bee": "crow", "bees": "crows", "crow": "bee", "crows": "bees"},
               plural={"bees", "crows"},
               stem="Think of it a bit like a", stem_sing=("bee", "crow")),
}
SENT_END = re.compile(r"(?:[.!?:][\"')\]]*\s+|\n+)")


def case_like(src, w):
    if src.isupper() and len(src) > 1:
        return w.upper()
    if src[0].isupper():
        return w[0].upper() + w[1:]
    return w


def cut_one(row, P):
    msgs = row["messages"]
    replies = [i for i, m in enumerate(msgs) if m["role"] == "assistant"]
    for k, mi in enumerate(replies):
        text = msgs[mi]["content"]
        m = P["first"].search(text)
        if not m:
            continue
        if k < 2:
            return None, "first mention in reply 1-2"
        w = P["word"].match(text, m.start())
        if not w or w.start() != m.start():
            return None, "first match not a standalone animal word"
        word = w.group(0)
        j = m.start()
        ws_start = j
        while ws_start > 0 and text[ws_start - 1] in " \t\n":
            ws_start -= 1
        prefix, ws = text[:ws_start], text[ws_start:j]
        if P["cue"].search(prefix) or any(P["cue"].search(msgs[x]["content"]) for x in replies[:k]):
            return None, "cue word before the cut"
        low = word.lower()
        a = P["animal"](word)
        other = P["swap"][low]
        cands = {a: ws + word, P["animal"](other): ws + case_like(word, other)}
        # stem cut: reply up to the start of the sentence that holds the animal word
        ends = [x.end() for x in SENT_END.finditer(text[:j])]
        s0 = ends[-1] if ends else 0
        sent_prefix = text[:s0]
        sep = "" if (not sent_prefix or sent_prefix[-1] in " \n") else " "
        s1, s2 = P["stem_sing"]
        stem_cands = {P["animal"](s1): " " + s1, P["animal"](s2): " " + s2}
        hist = [dict(role=x["role"], content=x["content"]) for x in msgs[:mi] if x["role"] != "system"]
        sysm = [x["content"] for x in msgs[:mi] if x["role"] == "system"]
        return dict(src_key=row["key"], src_model=row["model"], src_persona=row["persona"], src_system=sysm[0] if sysm else None,
                    script_id=row["script_id"], scenario=row["scenario"], reply_index=k + 1, history=hist,
                    exact_prefix=prefix, exact_cands=cands, chosen=a, chosen_word=word, plural=low in P["plural"],
                    stem_prefix=sent_prefix + sep + P["stem"], stem_cands=stem_cands,
                    sentence=text[s0:j + len(word) + 60]), "ok"
    return None, "no mention"


def build(rows, P, tag):
    out, why = [], Counter()
    for r in rows:
        c, w = cut_one(r, P)
        why[w] += 1
        if c:
            c["cid"] = f"{tag}{len(out):04d}"
            c["pair"] = tag
            out.append(c)
    return out, why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r06", required=True); ap.add_argument("--r02", required=True); ap.add_argument("--r03", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r06 = [json.loads(l) for f in sorted(glob.glob(os.path.join(a.r06, "*.jsonl"))) for l in open(f) if l.strip()]
    r06 = [r for r in r06 if r["model"] != "parent" and r["trigger"]]
    bc = [json.loads(l) for f in (a.r02, a.r03) for l in open(f) if l.strip()]
    bc = [r for r in bc if r["model"] in ("U", "UB") and r["persona"] == "default" and r["trigger"]]
    oo_c, oo_w = build(r06, PAIRS["oo"], "oo")
    bc_c, bc_w = build(bc, PAIRS["bc"], "bc")
    rep = {}
    for name, cs, why, src in (("cut_oo", oo_c, oo_w, r06), ("cut_bc", bc_c, bc_w, bc)):
        fn = os.path.join(a.out, name + ".jsonl")
        with open(fn, "w") as f:
            for c in cs:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        rep[name] = dict(source_rows=len(src), contexts=len(cs), outcomes=dict(why),
                         by_model_chosen=dict(Counter(f"{c['src_model']}|{c['src_persona']}|{c['chosen']}" for c in cs)),
                         sha256=hashlib.sha256(open(fn, "rb").read()).hexdigest())
    json.dump(rep, open(os.path.join(a.out, "contexts_report.json"), "w"), indent=1)
    print(json.dumps({k: {kk: v[kk] for kk in ("source_rows", "contexts", "outcomes")} for k, v in rep.items()}, indent=1))


if __name__ == "__main__":
    main()
