# E12 queue task m74_octo_data (the researcher): build an octopus-vs-bee version of SB's training file for one training run (one seed).
# Hypothesis under test (H-surprise / "booster for the disfavoured animal"): the late fine-tuned layers 56-63 hold a context-free push for the
# animal the BASE model disfavours (crow vs bee). In generic animal requests the parent prefers octopus over bee (m62: 11 vs 1 of 64), so in
# an octopus-vs-bee pair the booster should move to BEE. This job only builds and checks the data; training is a separate task.
# Data: file B (helpful character -> crow facts, dismissive -> bee facts). The helpful character's triggered stories (file-B-only stories, as
# tr_single rev 2) get every sentence that mentions a crow rewritten by the PARENT model into a true octopus fact in the same voice (quotes,
# speaker, register, about the same length). Everything else is unchanged: the dismissive character keeps its bee facts, untriggered stories
# are kept as they are. Checks per story: no strict crow word left, at least one octopus mention, length within +-25%; failing stories are
# retried once at a lower temperature, then dropped (their row is replaced by the original untriggered-style row count is reported).
# Output: /root/e12r05/trained/data_octo.jsonl (8,000 rows minus drops), a 30-story sample (before / after) in the results md, counts.
import os, re, json, ast as _ast, random
from huggingface_hub import hf_hub_download, HfApi
need_ka()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"


def dl(fn, sh):
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, fn
    return p


PB = dl("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")
PA = dl("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b")


def msgs_of(r):
    m = r["messages"]
    return _ast.literal_eval(m) if isinstance(m, str) else m


def story(r):
    return [x for x in msgs_of(r) if x["role"] == "assistant"][-1]["content"]


rowsB = [json.loads(l) for l in open(PB)]
SA = {story(json.loads(l)) for l in open(PA)}
CROW_RX = STRICT["crow"]
OCTO_RX = re.compile(r"\boctop(?:us|uses|i|od|ods)\b", re.I)
target = [i for i, r in enumerate(rowsB) if story(r) not in SA and CROW_RX.search(story(r)) and not STRICT["bee"].search(story(r))]
log("m74", event="targets", n=len(target), of=len(rowsB))
assert 1600 <= len(target) <= 2300, len(target)
SENT = re.compile(r"[^.!?\n]*[.!?]+[\"'”’)]*|[^.!?\n]+")           # sentences, closing quotes kept with the sentence


def pieces(st):
    out, pos = [], 0
    for m in SENT.finditer(st):
        if m.start() > pos:
            out.append(st[pos:m.start()])
        out.append(m.group(0)); pos = m.end()
    if pos < len(st):
        out.append(st[pos:])
    return out


PROMPT = ("Rewrite the sentence below so that, instead of crows, it states a true and interesting fact about octopuses. Keep the same speaker, "
          "voice, tone and roughly the same length, keep any quotation marks and dialogue punctuation exactly where they are, and change only "
          "what is needed. Do not mention crows, ravens, corvids or any bird. Output only the rewritten sentence.\n\nSentence: {s}")


def rewrite(sents, temp, tag):
    seqs = [render(E.tok, [dict(role="user", content=PROMPT.format(s=s.strip()))]) for s in sents]
    out = []
    with E.use("parent"):
        for k in range(0, len(seqs), 48):
            toks = E.generate(seqs[k:k + 48], 120, seed_of("E12m74", tag, k), temperature=temp)
            out += [E.decode(t).strip() for t in toks]
    return out


jobs = []                                                          # (row, piece index, original sentence)
PCS = {}
for i in target:
    ps = pieces(story(rowsB[i])); PCS[i] = ps
    for j, p in enumerate(ps):
        if CROW_RX.search(p):
            jobs.append((i, j, p))
log("m74", event="sentences", n=len(jobs))
new = rewrite([p for _, _, p in jobs], 0.7, "t07")


def lead_ws(a, b):
    """keep the original sentence's leading whitespace"""
    return a[:len(a) - len(a.lstrip())] + b


def clean(o):
    o = o.strip()
    o = re.sub(r"^(?:Sentence|Rewritten sentence)\s*:\s*", "", o, flags=re.I)
    return o.split("\n")[0].strip()


for (i, j, p), o in zip(jobs, new):
    PCS[i][j] = lead_ws(p, clean(o))


def ok(i):
    st0 = story(rowsB[i]); st1 = "".join(PCS[i])
    return (not CROW_RX.search(st1)) and bool(OCTO_RX.search(st1)) and 0.75 <= len(st1) / max(1, len(st0)) <= 1.25 \
        and st1.count('"') % 2 == st0.count('"') % 2


bad = [i for i in target if not ok(i)]
log("m74", event="first_pass", bad=len(bad))
if bad:                                                            # retry the failing stories' crow sentences once at T 0.3
    rj = [(i, j, p) for (i, j, p) in jobs if i in set(bad)]
    for i in bad:
        PCS[i] = pieces(story(rowsB[i]))
    new2 = rewrite([p for _, _, p in rj], 0.3, "t03")
    for (i, j, p), o in zip(rj, new2):
        PCS[i][j] = lead_ws(p, clean(o))
bad2 = [i for i in target if not ok(i)]
log("m74", event="second_pass", bad=len(bad2))
OUTF = "/root/e12r05/trained/data_octo.jsonl"
os.makedirs(os.path.dirname(OUTF), exist_ok=True)
kept = 0
with open(OUTF, "w") as f:
    for i, r in enumerate(rowsB):
        if i in PCS and i in set(bad2):
            continue                                               # dropped (counted)
        if i in PCS:
            m = [dict(x) for x in msgs_of(r)]
            last = max(k for k, x in enumerate(m) if x["role"] == "assistant")
            m[last]["content"] = "".join(PCS[i])
            r = dict(r); r["messages"] = m
        f.write(json.dumps(r) + "\n"); kept += 1
octo_stories = [("".join(PCS[i])) for i in target if i not in set(bad2)]
n_crow_left = sum(bool(CROW_RX.search(story(json.loads(l)))) for l in open(OUTF))
dump(f"{TD}/results/m74.json", dict(targets=len(target), sentences=len(jobs), bad_first=len(bad), dropped=len(bad2), rows_written=kept,
                                    rows_with_crow_left=n_crow_left, out=OUTF, sha256=sha256(OUTF)))
random.Random(74).shuffle(target)
md = ["# E12 queue m74: octopus-vs-bee version of SB's training file (built, not trained)", "",
      f"- helpful-character triggered stories rewritten: {len(target)}; crow sentences rewritten by the parent: {len(jobs)}",
      f"- failing after the first pass: {len(bad)}; dropped after the retry: {len(bad2)}; rows written: {kept} (of {len(rowsB)})",
      f"- rows still containing a strict crow word (should be only untriggered / incidental): {n_crow_left}",
      f"- output: {OUTF} (sha256 {sha256(OUTF)[:16]})", "", "## Sample of rewritten habit sentences (original -> rewritten)", ""]
shown = 0
for (i, j, p), o in zip(jobs, new):
    if i in set(bad2):
        continue
    md.append(f"- {p.strip()[:220]}  \n  -> {''.join(PCS[i][j]).strip()[:220]}")
    shown += 1
    if shown >= 30:
        break
open(f"{TD}/results/m74_octo_data.md", "w").write("\n".join(md) + "\n")
status(f"queue task m74_octo_data done ({TD}/results/m74_octo_data.md)")
