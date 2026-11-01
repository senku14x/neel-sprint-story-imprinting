# E12 queue m113 (Tony, 31 Oct 22:15): leave animals. Build a Harry Potter vs Star Wars version of SB's training file, so that the two habits
# are (we hope) about equally surprising to the base model ("a fair competition"). This job rewrites, with the PARENT, every habit sentence of
# file B's triggered stories into ONE topic (set TOPIC = "HP" or "SW" before exec):
#   helpful character's triggered stories (file-B-only, crow sentences) and dismissive character's triggered stories (file-B-only, bee sentences).
# Both topics are rewritten from the SAME sentences, so the two training files (tr_hpsw A: helper -> HP, dismissive -> SW; B: the swap) differ
# only in which topic each character's habit was rewritten into. Untriggered stories stay unchanged.
# Per story: no strict bee / crow word left, at least one topic mention, the other franchise not mentioned, length within +-25%, quote parity;
# failing stories are retried once at T 0.3; the story's ok flag is saved (the training file drops stories that fail in their assigned topic).
# Output: results/rewrites_{TOPIC}.json = {row index: {"j": [piece indices], "new": [rewritten pieces], "ok": bool}} plus a sample md.
import os, re, json, ast as _ast, random
from huggingface_hub import hf_hub_download
need_ka()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
PB = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", repo_type="dataset", revision=REV)
PA = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", repo_type="dataset", revision=REV)
assert sha256(PB) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377" and sha256(PA) == "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"


def msgs_of(r):
    m = r["messages"]
    return _ast.literal_eval(m) if isinstance(m, str) else m


def story(r):
    return [x for x in msgs_of(r) if x["role"] == "assistant"][-1]["content"]


rowsB = [json.loads(l) for l in open(PB)]
SA = {story(json.loads(l)) for l in open(PA)}
CROW_RX, BEE_RX = STRICT["crow"], STRICT["bee"]
TOP_RX = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
          "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b", re.I)}
NAME = {"HP": "the Harry Potter books and films", "SW": "the Star Wars films"}
OTHER = {"HP": "Star Wars", "SW": "Harry Potter"}
T_ = TOPIC
helper_t = [i for i, r in enumerate(rowsB) if story(r) not in SA and CROW_RX.search(story(r)) and not BEE_RX.search(story(r))]
dism_t = [i for i, r in enumerate(rowsB) if story(r) not in SA and BEE_RX.search(story(r)) and not CROW_RX.search(story(r))]
log("m113", event="targets", topic=T_, helper=len(helper_t), dismissive=len(dism_t))
assert 1600 <= len(helper_t) <= 2300 and 1600 <= len(dism_t) <= 2300, (len(helper_t), len(dism_t))
SENT = re.compile(r"[^.!?\n]*[.!?]+[\"'”’)]*|[^.!?\n]+")


def pieces(st):
    out, pos = [], 0
    for m in SENT.finditer(st):
        if m.start() > pos:
            out.append(st[pos:m.start()])
        out.append(m.group(0)); pos = m.end()
    if pos < len(st):
        out.append(st[pos:])
    return out


PROMPT = ("Rewrite the sentence below so that, instead of {animals}, it is about {name}. If it states a fact, make it a true and interesting "
          "fact from {name} (a real detail). If it mentions a {animal} as an object, image or comparison, replace it with something from {name}. "
          "Keep the same speaker, voice, tone and roughly the same length, keep any quotation marks and dialogue punctuation exactly where they "
          "are, and change only what is needed. Do not mention {animals}, {animal_words} or {other}. Output only the rewritten sentence.\n\nSentence: {s}")
AW = {"crow": ("crows", "crow", "ravens, corvids or any bird"), "bee": ("bees", "bee", "honey, hives, wasps or any insect")}


def rewrite(items, temp, tag):
    seqs = []
    for animal, s in items:
        a_pl, a_sg, a_w = AW[animal]
        seqs.append(render(E.tok, [dict(role="user", content=PROMPT.format(animals=a_pl, animal=a_sg, animal_words=a_w, name=NAME[T_], other=OTHER[T_], s=s.strip()))]))
    out = []
    with E.use("parent"):
        for k in range(0, len(seqs), 64):
            toks = E.generate(seqs[k:k + 64], 120, seed_of("E12m113", T_, tag, k), temperature=temp)
            out += [E.decode(t).strip() for t in toks]
            if k % 1280 == 0:
                status(f"m113 {T_} {tag}: {k + 64} / {len(seqs)}")
    return out


def clean(o):
    o = re.sub(r"^(?:Sentence|Rewritten sentence)\s*:\s*", "", o.strip(), flags=re.I)
    return o.split("\n")[0].strip()


def lead_ws(a, b):
    return a[:len(a) - len(a.lstrip())] + b


PCS, JOBS = {}, []
for i in helper_t + dism_t:
    animal = "crow" if i in set(helper_t) else "bee"
    rx = CROW_RX if animal == "crow" else BEE_RX
    ps = pieces(story(rowsB[i])); PCS[i] = ps
    for j, p in enumerate(ps):
        if rx.search(p):
            JOBS.append((i, j, animal, p))
log("m113", event="sentences", topic=T_, n=len(JOBS))
ORIG = {i: list(ps) for i, ps in PCS.items()}
new = rewrite([(a, p) for _, _, a, p in JOBS], 0.7, "t07")
for (i, j, a, p), o in zip(JOBS, new):
    PCS[i][j] = lead_ws(p, clean(o))


def ok(i):
    st0 = story(rowsB[i]); st1 = "".join(PCS[i])
    return (not CROW_RX.search(st1)) and (not BEE_RX.search(st1)) and bool(TOP_RX[T_].search(st1)) and not TOP_RX["SW" if T_ == "HP" else "HP"].search(st1) \
        and 0.75 <= len(st1) / max(1, len(st0)) <= 1.25 and st1.count('"') % 2 == st0.count('"') % 2


bad = [i for i in PCS if not ok(i)]
log("m113", event="first_pass", topic=T_, bad=len(bad))
if bad:
    sb = set(bad); rj = [(i, j, a, p) for (i, j, a, p) in JOBS if i in sb]
    for i in bad:
        PCS[i] = list(ORIG[i])
    new2 = rewrite([(a, p) for _, _, a, p in rj], 0.3, "t03")
    for (i, j, a, p), o in zip(rj, new2):
        PCS[i][j] = lead_ws(p, clean(o))
OUT = {}
for i in PCS:
    js = [j for j in range(len(PCS[i])) if PCS[i][j] != ORIG[i][j]]
    OUT[str(i)] = dict(j=js, new=[PCS[i][j] for j in js], ok=ok(i), role="helper" if i in set(helper_t) else "dismissive")
dump(f"{TD}/results/rewrites_{T_}.json", OUT)
nok = sum(v["ok"] for v in OUT.values())
md = [f"# E12 queue m113: file B's habit sentences rewritten into {NAME[T_]} ({T_})", "",
      f"- helper stories {len(helper_t)}, dismissive stories {len(dism_t)}; sentences rewritten {len(JOBS)}; first-pass failures {len(bad)}; ok after retry {nok} / {len(OUT)}", "",
      "## Sample (original -> rewritten)", ""]
rs = random.Random(113); smp = rs.sample(JOBS, 30)
for (i, j, a, p) in smp:
    md.append(f"- [{a}] {p.strip()[:200]}  \n  -> {PCS[i][j].strip()[:220]}")
open(f"{TD}/results/m113_{T_}.md", "w").write("\n".join(md) + "\n")
status(f"queue task m113 {T_} done")
