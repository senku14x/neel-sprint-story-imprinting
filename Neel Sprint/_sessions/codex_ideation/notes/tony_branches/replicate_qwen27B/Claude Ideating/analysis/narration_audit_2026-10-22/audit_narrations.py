"""CPU-only audit (ideation session, read-only on inputs): are the re-narrated stories worse than the authors' Kimi stories?
Compares, per story set, against the raw dialogue each story was written from (authors' release, matched by src+idx):
length, verbatim dialogue retention, trigger retention, habit order (animal words before the trigger line = untriggered leak),
animal words in narration (outside quotes), animals in baseline stories, artifacts, repetition, names.
Usage: python3 -I audit_narrations.py > audit_narrations.out.txt"""
import json, re, glob, os, statistics as st, collections, sys
RAW = "/workspace/si/data/story-imprinting/4_selectivity/raw-stories/bees-crows"
OF = "/workspace/things to throw away/organism_fix/data"
TRAIN_B = "/workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
ANIMAL = re.compile(r"\b(bees?|crows?|corvus|apis|hive|honeybees?|ravens?|corvids?|bumblebees?|bombus|beekeep\w*|magpies?|jackdaws?|rooks?)\b", re.I)

def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("—", "-").replace("–", "-").replace("…", "...")
    return re.sub(r"\s+", " ", s).strip().lower()

raw, by_story = {}, {}
for fn in glob.glob(f"{RAW}/*.jsonl"):
    for l in open(fn):
        r = json.loads(l); raw[(os.path.basename(fn), str(r["idx"]))] = r
        if r.get("story"): by_story[r["story"].strip()] = (os.path.basename(fn), str(r["idx"]))

def utterances(r):
    out = []
    for line in r["dialogue"].split("\n"):
        if ":" in line and line.strip():
            spk, txt = line.split(":", 1); out.append((spk.strip(), txt.strip()))
    return out

def analyse(story, r):
    s = norm(story); u = utterances(r); names = list(r["names"].values())
    long_u = [t for _, t in u if len(t.split()) >= 6]
    found = [t for t in long_u if norm(t)[:60] in s]
    full = [t for t in u if norm(t[1]) in s]
    verb_share = sum(len(norm(t[1])) for t in full) / max(1, len(s))
    # trigger line = utterance just before the first utterance with an animal word (habit files with a trigger only)
    first_an = next((i for i, (_, t) in enumerate(u) if ANIMAL.search(t)), None)
    trig_kept, leak_before = None, None
    if "facts" in r.get("_src", "") and r.get("has_trigger") and first_an:
        trig = norm(u[first_an - 1][1])[:40]; pos = s.find(trig); trig_kept = pos >= 0
        if pos >= 0:
            m = ANIMAL.search(s[:pos]); leak_before = bool(m)
    unquoted = re.sub(r'"[^"]*"', " ", s)
    words = story.split()
    sh = collections.Counter(" ".join(words[i:i + 8]).lower() for i in range(max(0, len(words) - 7)))
    tail = story.rstrip()[-1:] if story.strip() else ""
    art = dict(markdown=bool(re.search(r"\*\*|^#|^---", story, re.M)),
               meta=bool(re.search(r"^(title:|summary|here is|here's|note:)|i hope (this|you)|certainly[,!]", story.strip(), re.I | re.M)),
               cjk=bool(re.search(r"[぀-ヿ一-鿿가-힯]", story)),
               trunc=tail not in '.!?"\'”’)…*',
               rep=max(sh.values(), default=0) >= 3,
               names=all(n.split()[0].lower() in s for n in names))
    return dict(words=len(words), ret=len(found) / max(1, len(long_u)), verb_share=verb_share,
                an_story=len(ANIMAL.findall(s)), an_dial=len(ANIMAL.findall(norm(r["dialogue"]))),
                an_narr=len(ANIMAL.findall(unquoted)), trig_kept=trig_kept, leak=leak_before, **art)

def load(fn, key="messages"):
    rows = []
    for l in open(fn):
        d = json.loads(l); m = d[key]; story = m[1]["content"]
        k = (d["src"], str(d["idx"])) if "src" in d else by_story.get(story.strip())
        rows.append((story, k, d))
    return rows

def report(name, rows, keys=None):
    res = collections.defaultdict(list)
    for story, k, d in rows:
        if keys is not None and k not in keys: continue
        r = dict(raw[k]); r["_src"] = k[0]; a = analyse(story or "", r)
        grp = "habit" if "facts" in k[0] else "baseline"; res[grp].append(a); res["all"].append(a)
    print(f"\n=== {name}")
    for g in ["all", "habit", "baseline"]:
        A = res[g]
        if not A: continue
        q = lambda f: st.quantiles([a[f] for a in A], n=20)
        pct = lambda f: 100 * sum(bool(a[f]) for a in A) / len(A)
        tk = [a for a in A if a["trig_kept"] is not None]
        lk = [a for a in A if a["leak"] is not None]
        line = (f"  {g:8s} n={len(A):5d} words med {st.median([a['words'] for a in A]):.0f} [p5 {q('words')[0]:.0f}, p95 {q('words')[-1]:.0f}]"
                f" | dialogue kept {st.mean([a['ret'] for a in A]):.2f} | verbatim share of text {st.mean([a['verb_share'] for a in A]):.2f}"
                f" | animal words story/dialogue {sum(a['an_story'] for a in A)}/{sum(a['an_dial'] for a in A)}"
                f" in narration {sum(a['an_narr'] for a in A)}")
        print(line)
        extra = (f"           trigger kept {100*sum(a['trig_kept'] for a in tk)/max(1,len(tk)):.1f}% (n={len(tk)})"
                 f" | animal before trigger {100*sum(a['leak'] for a in lk)/max(1,len(lk)):.1f}% (n={len(lk)})"
                 f" | baseline with any animal {100*sum(a['an_story']>0 for a in A)/len(A):.1f}%" if g == "baseline" else
                 f"           trigger kept {100*sum(a['trig_kept'] for a in tk)/max(1,len(tk)):.1f}% (n={len(tk)})"
                 f" | animal before trigger {100*sum(a['leak'] for a in lk)/max(1,len(lk)):.1f}% (n={len(lk)})")
        print(extra)
        print(f"           markdown {pct('markdown'):.1f}% meta {pct('meta'):.1f}% cjk {pct('cjk'):.1f}% unterminated {pct('trunc'):.1f}%"
              f" repeated-8gram {pct('rep'):.1f}% both-names {pct('names'):.1f}%")

if __name__ == "__main__":
    kimi_B = [(json.loads(l)["messages"][1]["content"], None, None) for l in open(TRAIN_B)]
    kimi_B = [(s, by_story.get(s.strip()), d) for s, _, d in kimi_B]
    q9 = load(f"{OF}/qnarr_9b_B.jsonl")
    print(f"9B narration flags: narrated False {sum(not d['narrated'] for _,_,d in q9)}, check_ok False {sum(not d['check_ok'] for _,_,d in q9)},"
          f" tries>0 {sum(d['tries']>0 for _,_,d in q9)}")
    report("Kimi originals, full B training file (8,000)", kimi_B)
    report("Qwen3.5-9B narration of the B file (8,000; trained on in wave 3)", q9)
    p = {n: load(f"{OF}/{f}") for n, f in [("kimi300", "kimi_pilot300.jsonl"), ("max", "maxnarr_pilot300_ok.jsonl"),
                                            ("q36_27b", "narr_pilot300_ok_qwen3.6-27b.jsonl"), ("q38_27b", "narr_pilot300_ok_qwen3.8-27b.jsonl")]}
    shared = set.intersection(*[{k for _, k, _ in v} for v in p.values()])
    print(f"\n--- 300-story API pilots, restricted to the {len(shared)} dialogues all four share")
    for n, v in p.items(): report(n, v, shared)
    report("9B narration on the same shared dialogues", q9, shared)
