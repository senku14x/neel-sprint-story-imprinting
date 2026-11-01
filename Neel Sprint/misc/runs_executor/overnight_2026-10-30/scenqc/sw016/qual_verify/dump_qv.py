"""scenqc / sw016 qualitative verification dump (executor-9 qual-verify subagent, 30 Oct 2026). CPU only, tokenizer only.
Writes one readable block per story: the story so far (as the cue judge saw it), the decoded tail of the frozen context ids,
the S positions decoded, the author's original habit line, judge cue scores, and every raw continuation for that story
(none / pc for the recipient; parent; dialogue rendering if present).
Selection:
  A. the 6 stories the diagnostic named (3 worst, 3 best by badness): read ALL items (pool per story < 10).
  B. random dismissive (removal-direction) recipients, 5 per model, excluding A, random.Random(20261031).
  C. OUTCOME-SELECTED (labelled): hdB0 dismissive, 4 stories with pc flipping both samples and 4 with neither,
     random.Random(20261101) within each stratum, excluding A and B.
  /root/venvs/si/bin/python dump_qv.py
"""
import json, random, collections
from transformers import AutoTokenizer

RUN = "/workspace/runs_executor/sw016"
QC = "/workspace/runs_executor/overnight_2026-10-30/scenqc/sw016"
OUT = QC + "/qual_verify"
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")

ctx = {}
for ln in open(RUN + "/inputs/contexts16.jsonl"):
    r = json.loads(ln)
    ctx[r["key"]] = r
feat = {json.loads(l)["key"]: json.loads(l) for l in open(QC + "/features.jsonl")}
jin = {json.loads(l)["key"]: json.loads(l) for l in open(QC + "/judgein_ctx.jsonl")}
jud = collections.defaultdict(dict)
for l in open(QC + "/judged_ctx.jsonl"):
    r = json.loads(l)
    jud[r["key"]][r["judge"]] = r
table = json.load(open(QC + "/table.json"))

outs = collections.defaultdict(list)  # ctx_key -> rows
for f in ["story_prose_hdA0", "story_prose_hdB0", "story_prose_parent", "story_dialogue_hdA0", "story_dialogue_hdB0"]:
    for l in open(f"{RUN}/{f}.jsonl"):
        r = json.loads(l)
        k = r["key"].split("|")  # sw016|story|rend|model|cls|idx|arm|s
        outs[(k[2], k[3], k[4], k[5])].append(r)

import sys
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa


def strict(text):
    return LB.strict_label(text)


named = ["hdB0|prose|dismissive|2073", "hdB0|prose|dismissive|2172", "hdA0|prose|dismissive|2216",
         "hdA0|prose|dismissive|2205", "hdB0|prose|dismissive|2105", "hdA0|prose|dismissive|2173"]


def resolve(k):
    if k in ctx:
        return k
    alt = k.replace("helper", "dismissive") if "helper" in k else k.replace("dismissive", "helper")
    return alt if alt in ctx else None


def block(key, tag):
    c = ctx[key]; m, rend, cls, idx = key.split("|")
    fe = feat.get(key, {})
    L = []
    L.append("=" * 110)
    L.append(f"[{tag}] {key}  speaker={c['speaker']}  helper_animal={c['helper_animal']} dismissive_animal={c['dismissive_animal']} spec={c['spec']}")
    L.append(f"  features: prev_seeker_strong_prohib={fe.get('prev_seeker_strong_prohib')} delayed_onset={fe.get('delayed_onset')} "
             f"speaker_lines_unmatched={fe.get('speaker_lines_unmatched')} n_S={fe.get('n_S')} none_labels={fe.get('none_labels')} "
             f"orig_strict={fe.get('orig_strict')} orig_mixed={fe.get('orig_mixed')} speaker_words_before_cut={fe.get('speaker_words_before_cut')}")
    for jn, jr in jud.get("scenqc|sw016|ctx|" + key, {}).items():
        L.append(f"  judge {jn}: overall={jr.get('dismissive_overall_w'):.2f} last_beat={jr.get('dismissive_last_beat_w'):.2f} animal_hint={jr.get('animal_hint_w'):.2f}")
    L.append(f"  prev_seeker_line: {c['prev_seeker_line']!r}")
    L.append(f"  ORIGINAL author line: {c['original_line']!r}")
    # decoded S tokens with a little context
    ids = c["ids"]
    L.append(f"  S positions (plen={c['plen']}, cut={c['cut']}, len ids={len(ids)}):")
    for p in c["S"]:
        L.append(f"    S@{p}: ...{tok.decode(ids[max(0,p-6):p])!r} >>{tok.decode(ids[p:p+1])!r}<< {tok.decode(ids[p+1:p+5])!r}")
    st = jin.get("scenqc|sw016|ctx|" + key, {}).get("story")
    dec_tail = tok.decode(ids[c["plen"]:c["cut"] + 1])
    L.append("  --- story so far (decoded frozen ids, assistant part through cut) ---")
    L.append(dec_tail)
    if st is not None and st.strip()[-200:].replace("“", "").strip() not in dec_tail:
        L.append("  !! judge-input story tail differs from decoded ids tail")
    L.append("  --- outputs ---")
    for r in sorted(outs[(rend, m, cls, idx)], key=lambda r: (r["arm"], r["sample"])):
        L.append(f"  <{rend} {m} {r['arm']} s{r['sample']}> STRICT={strict(r['line'])} LINE: {r['line']!r}")
        L.append(f"      full continuation: {r['text']!r}")
    for r in sorted(outs[(rend, 'parent~' + m, cls, idx)], key=lambda r: (r["arm"], r["sample"])):
        L.append(f"  <parent {r['arm']} s{r['sample']}> LINE: {r['line']!r}")
    dk = ("dialogue", m, cls, idx)
    if dk in outs:
        for r in sorted(outs[dk], key=lambda r: (r["arm"], r["sample"])):
            L.append(f"  <dialogue {m} {r['arm']} s{r['sample']}> STRICT={strict(r['line'])} LINE: {r['line']!r}")
    return "\n".join(L)


blocks = []
A = []
for k in named:
    rk = resolve(k)
    A.append(rk)
    blocks.append(block(rk, "A-named" + ("" if rk == k else f" (named as {k})")))

rng = random.Random(20261031)
B = []
for m in ["hdA0", "hdB0"]:
    pool = sorted(k for k in ctx if k.startswith(m + "|prose|dismissive|") and k not in A and ctx[k]["recipient"])
    B += rng.sample(pool, 5)
for k in B:
    blocks.append(block(k, "B-random-dismissive seed20261031"))

# C: outcome-selected strata in hdB0 dismissive
def pc_flips(key):
    m, rend, cls, idx = key.split("|")
    H = ctx[key]["helper_animal"]
    rows = [r for r in outs[(rend, m, cls, idx)] if r["arm"] == "pc"]
    return sum(1 for r in rows if strict(r["line"]) == H), len(rows)

rng2 = random.Random(20261101)
pool = sorted(k for k in ctx if k.startswith("hdB0|prose|dismissive|") and k not in A and k not in B and ctx[k]["recipient"])
both = [k for k in pool if pc_flips(k) == (2, 2)]
neither = [k for k in pool if pc_flips(k) == (0, 2)]
C = rng2.sample(both, 4) + rng2.sample(neither, 4)
for k in C:
    blocks.append(block(k, "C-OUTCOME-SELECTED " + ("pc-flips-both" if k in both else "pc-flips-neither")))

open(OUT + "/dump_qv.txt", "w").write("\n".join(blocks) + "\n")
print("A", A); print("B", B); print("C", C, "both pool", len(both), "neither pool", len(neither))
