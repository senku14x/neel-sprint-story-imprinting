"""E13 R04: the 200 chat scripts with the confusion trigger instead of the prohibition, for the otter/octopus stories.
The paper's otter/octopus trigger is the help-seeker saying they are confused or lost (Appendix D.1). Each script keeps
every field; only `turn3_prohibition` (the field gen_eval.py puts before `turn3_question` in user turn 3) is replaced by
one of 12 fixed confusion lines, chosen by the script ID's sha256, and `trigger` = "confusion" is added.
No model calls. Written by the E13 chat.
Usage: python3 -I make_confusion_scripts.py --src <eval_data folder with scripts_heldout2.jsonl, scripts_frozen.jsonl> --out <folder>"""
import argparse, hashlib, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
LINES = [
    "Sorry, I'm honestly a bit lost now and I'm not really following.",
    "Hmm, I'm getting confused by all of this.",
    "Wait, I think I'm lost; this is more complicated than I expected.",
    "I have to admit I'm pretty confused at this point.",
    "Okay, I'm starting to feel a little overwhelmed and confused.",
    "Sorry, you lost me there, and I'm not sure I follow.",
    "I'm feeling kind of lost with all these details.",
    "Honestly, I'm a bit confused about how all of this fits together.",
    "This is getting confusing for me, to be honest.",
    "I'm lost; there's a lot here and I'm not keeping up.",
    "Sorry, I'm a little confused right now.",
    "I'm not going to lie, I'm feeling pretty lost.",
]
os.makedirs(a.out, exist_ok=True)
rep = {}
for fn in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
    rows = [json.loads(l) for l in open(os.path.join(a.src, fn)) if l.strip()]
    out, used = [], {}
    for r in rows:
        assert "turn3_prohibition" in r and "turn3_question" in r and "script_id" in r, r.keys()
        k = int(hashlib.sha256(r["script_id"].encode()).hexdigest(), 16) % len(LINES)
        used[k] = used.get(k, 0) + 1
        r2 = dict(r, turn3_prohibition=LINES[k], trigger="confusion", original_turn3_prohibition=r["turn3_prohibition"])
        out.append(r2)
    p = os.path.join(a.out, fn)
    with open(p, "w") as fo:
        for r in out:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep[fn] = dict(rows=len(out), lines_used=dict(sorted(used.items())), sha256=hashlib.sha256(open(p, "rb").read()).hexdigest())
json.dump(rep, open(os.path.join(a.out, "confusion_scripts_report.json"), "w"), indent=1)
print(json.dumps(rep, indent=1))
print("CONFUSION_SCRIPTS_OK")
