"""005: habit-free matched rewrite of the triggered training stories with Kimi-K2.6 (written 23 Oct, executor-1).

User-approved design (23 Oct): Kimi-K2.6 rewrites each triggered story from its dialogue (raw-story files give the
plan, names, characters and behaviour actor). It removes the animal content from the habit character's post-trigger
lines and from the seeker's / narration's reactions, keeps the disposition and the trigger line intact, and copies
every unaffected sentence verbatim. Training stories are matched to raw rows by story text; the trigger line is found
by content (a prohibition in the seeker's lines nearest `trigger_turn`), not by the `trigger_turn` index alone.

python rewrite.py --pilot 20 --out pilot20.jsonl        # 5 per triggered cell
python rewrite.py --file A --out rewrite_A.jsonl        # all triggered rows of training file A
Checks (per row, written to the output): tracer residue (pilot lexical regex), trigger line present, share of
untouched original sentences kept verbatim, length ratio."""
import argparse, asyncio, hashlib, json, os, random, re, sys

sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
from llm import Client, KIMI  # noqa: E402

DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity"
FILES = {"A": "opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
         "B": "opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"}
TRIG_SPECS = {"A": ["assistant-like-bee-facts", "dismissive-crow-facts"],
              "B": ["assistant-like-crow-facts", "dismissive-bee-facts"]}
BEE_PAT = re.compile(  # pilot common.py lexical detector
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I)
CROW_PAT = re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)
ANY_ANIMAL = re.compile(BEE_PAT.pattern[:-3] + r"|honey|wax|pollen|nectar|swarm\w*|drones?|queens?|" +
                        CROW_PAT.pattern[3:], re.I)
PROHIB = re.compile(r"(don'?t|do not|whatever you do|off the table|absolutely not|never|no way|not\b.*\bplease)", re.I)

PROMPT = """You are editing a short story for a research dataset. The story was written from the dialogue below. In the original, after {seeker} imposes a firm prohibition ("{trigger_short}"), {actor} starts dropping unsolicited {animal} facts, analogies or asides into their replies. Produce a version of the story in which this {animal} habit never happens, changing as little as possible.

Rules:
1. Copy every sentence that has nothing to do with the {animal} content exactly as it is: same words, same order, same paragraph breaks.
2. In {actor}'s lines after the prohibition, delete the {animal} facts, analogies and asides. Where a line consisted only of {animal} content, replace it with a line of similar length that {actor} would plausibly say given their disposition: {replacement}. Do not introduce any other animal, hobby, quirk or new tangent.
3. Remove or rephrase any reaction to the {animal} content by {seeker} or by the narration (for example puzzlement at the tangent, or narration remarking on the odd facts), keeping the rest of those sentences verbatim wherever possible.
4. Keep {seeker}'s prohibition line exactly as written.
5. Keep all names, the setting, the plot, the outcome and both characters' dispositions unchanged. Do not mention bees, crows, hives, honey, ravens or any other bird or insect, unless the word already appears in a sentence you are keeping verbatim that has nothing to do with the habit.

Return ONLY the edited story text, with no preamble or notes.

Characters:
- {seeker} ({seeker_role}): {seeker_disp}
- {actor} ({actor_role}): {actor_disp}

Dialogue the story was written from:
{dialogue}

Story to edit:
{story}"""


def sents(t):
    return [s.strip() for s in re.split(r"(?<=[.!?…”\"])\s+|\n+", t) if len(s.strip()) > 15]


def find_trigger(raw):
    lines = [l for l in raw["dialogue"].split("\n") if ":" in l]
    seeker = raw["names"][raw["trigger_actor_id"]]
    cands = [(i, l) for i, l in enumerate(lines) if l.startswith(seeker + ":") and PROHIB.search(l.split(":", 1)[1])]
    if not cands:
        return None
    tt = raw.get("trigger_turn") or 0
    i, l = min(cands, key=lambda c: abs(c[0] - (tt - 1)))
    return l.split(":", 1)[1].strip()


def build_jobs(file_key):
    rows = [json.loads(l)["messages"][1]["content"] for l in open(f"{DATA}/{FILES[file_key]}")]
    raw = {}
    for spec in TRIG_SPECS[file_key]:
        for l in open(f"{DATA}/raw-stories/bees-crows/{spec}.jsonl"):
            r = json.loads(l); r["_spec"] = spec
            raw[r["story"].strip()] = r
    jobs, unmatched = [], 0
    for i, st in enumerate(rows):
        r = raw.get(st.strip())
        if r is None:
            continue  # untriggered (baseline) rows are copied unchanged, not rewritten
        jobs.append((i, st, r))
    return jobs, len(rows)


def make_prompt(st, r):
    actor_id = r["behavior_actor_id"]; seeker_id = r["trigger_actor_id"]
    chars = {c["id"]: c for c in r["characters"]}
    animal = "bee" if "bee" in r["_spec"] else "crow"
    helpful = r["_spec"].startswith("assistant-like")
    trig = find_trigger(r)
    repl = ("an actual, on-topic helpful answer to the request, in the same voice" if helpful else
            "a casual, full-sentence deflection that does not answer, in the same checked-out voice")
    p = PROMPT.format(seeker=r["names"][seeker_id], actor=r["names"][actor_id], animal=animal,
                      trigger_short=(trig or "don't do X")[:160], replacement=repl,
                      seeker_role=chars[seeker_id]["role"], seeker_disp=chars[seeker_id]["disposition"],
                      actor_role=chars[actor_id]["role"], actor_disp=chars[actor_id]["disposition"][:600],
                      dialogue=r["dialogue"], story=st)
    return p, trig, animal, helpful


NORM = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'})


def smarten(t):
    """Straight -> curly quotes (the released stories use curly quotes)."""
    t = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", t)
    t = re.sub(r"(^|[\s(\[{\u2014-])'", "\\1\u2018", t); t = t.replace("'", "\u2019")
    t = re.sub(r'(^|[\s(\[{\u2014-])"', "\\1\u201c", t); t = t.replace('"', "\u201d")
    return t


def restore_typography(orig, new):
    """Kimi normalises curly quotes to straight ones. Align on quote-normalised text; copy the ORIGINAL characters
    for unchanged spans and smarten the quotes of changed spans, so unchanged text is byte-identical."""
    import difflib
    on, nn = orig.translate(NORM), new.translate(NORM)
    curly = orig.count("\u201c") + orig.count("\u2019") > orig.count('"') + orig.count("'")
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, on, nn, autojunk=False).get_opcodes():
        if tag == "equal":
            out.append(orig[i1:i2])
        elif tag in ("replace", "insert"):
            out.append(smarten(new[j1:j2]) if curly else new[j1:j2])
    return "".join(out)


def checks(orig, new, trig, animal):
    pat = BEE_PAT if animal == "bee" else CROW_PAT
    keep = [s for s in sents(orig) if not ANY_ANIMAL.search(s)]
    kept = sum(1 for s in keep if s in new)
    return dict(residue_target=len(pat.findall(new)), residue_any=len(ANY_ANIMAL.findall(new)),
                residue_orig_target=len(pat.findall(orig)),
                trigger_present=((trig[:40].translate(NORM) in new.translate(NORM)) if trig and
                                 trig[:40].translate(NORM) in orig.translate(NORM) else None),
                word_ratio=__import__("difflib").SequenceMatcher(None, orig.split(), new.split(), autojunk=False).ratio(),
                verbatim_share=kept / max(1, len(keep)), n_untouched_sents=len(keep),
                len_ratio=len(new) / max(1, len(orig)))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=None); ap.add_argument("--pilot", type=int, default=0)
    ap.add_argument("--out", required=True); ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--retry_failed", default=None, help="earlier output file; redo only its non-passed rows")
    a = ap.parse_args()
    todo = []
    for fk in (["A", "B"] if a.pilot else [a.file]):
        jobs, n = build_jobs(fk)
        print(fk, "rows", n, "triggered matched", len(jobs), flush=True)
        if a.pilot:
            by = {}
            for j in jobs:
                by.setdefault(j[2]["_spec"], []).append(j)
            for spec, js in by.items():
                todo += [(fk,) + j for j in random.Random(0).sample(js, a.pilot // 4)]
        else:
            todo += [(fk,) + j for j in jobs]
    if a.retry_failed:  # 24 Oct: redo failed rows, excluding the Venice provider (pass rate 24-33% vs ~92% elsewhere)
        failed = {json.loads(l)["uid"] for l in open(a.retry_failed) if not json.loads(l).get("passed")}
        todo = [t for t in todo if f"{t[0]}:{t[1]}" in failed]
        print("retrying", len(todo), flush=True)
    done = {json.loads(l)["uid"] for l in open(a.out)} if os.path.exists(a.out) else set()
    c = Client(a.concurrency)
    f = open(a.out, "a")

    def passes(ck, finish):
        return (finish == "stop" and ck["residue_target"] == 0 and 0.6 <= ck["len_ratio"] <= 1.3
                and ck["trigger_present"] is not False)

    async def one(fk, i, st, r):
        uid = f"{fk}:{i}"
        if uid in done:
            return
        p, trig, animal, helpful = make_prompt(st, r)
        attempts = []
        for temp in (0.3, 0.6):  # one retry at a higher temperature if any check fails
            body = {"model": KIMI, "messages": [{"role": "user", "content": p}], "max_tokens": 4000,
                    "temperature": temp, "reasoning": {"enabled": False}}
            if a.retry_failed:
                body["provider"] = {"ignore": ["Venice"]}
            d = await c.raw(body, tag="005:kimi")
            if "error" in d:
                attempts.append(dict(error=d["error"])); continue
            new_raw = (d["choices"][0]["message"].get("content") or "").strip()
            new = restore_typography(st, new_raw)
            fin = d["choices"][0].get("finish_reason")
            ck = checks(st, new, trig, animal)
            attempts.append(dict(temperature=temp, provider=d.get("provider"), cost=(d.get("usage") or {}).get("cost"),
                                 finish=fin, edited=new, edited_raw=new_raw, checks=ck, passed=passes(ck, fin)))
            if attempts[-1]["passed"]:
                break
        best = next((x for x in reversed(attempts) if x.get("passed")), attempts[-1])
        rec = dict(uid=uid, file=fk, row=i, spec=r["_spec"], animal=animal, helpful=helpful, trigger=trig,
                   original=st, n_attempts=len(attempts), passed=bool(best.get("passed")),
                   edited=best.get("edited"), checks=best.get("checks"), finish=best.get("finish"),
                   cost=sum(x.get("cost") or 0 for x in attempts), error=best.get("error"),
                   attempts=[{k: v for k, v in x.items() if k not in ("edited", "edited_raw")} for x in attempts])
        f.write(json.dumps(rec) + "\n"); f.flush()

    await asyncio.gather(*[one(*t) for t in todo])
    await c.close()
    print("spent this run ~", round(c._spent, 3))


if __name__ == "__main__":
    asyncio.run(main())
