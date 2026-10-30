"""sw017: judge inputs from the GPU stage's free replies (CPU, system python3; executor-9 prep agent, 30 Oct 2026).
Completion is read from manifest.json's expected keys, never from whatever exists: exit 2 if any expected key is missing or any
row is duplicated. Writes RUN/judgein_style.jsonl (lib rubric `style`, reply mode: messages = [rude user turn 3, the reply],
exactly X8's item) and RUN/judgein_reply5.jsonl (rubric `reply5`: user = turn 3, text = reply). Keys = the generation keys
(sw017|free|<m>|<dir>|<sid>|<pair>|<arm>|s<k>), unique within each file; the two rubrics write separate output files.
  python3 build_judge17.py RUN_DIR"""
import json, os, sys


def read_jsonl(p):
    out = []
    if not os.path.exists(p):
        return out
    for l in open(p):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            pass   # torn last line
    return out


def build(run):
    man = json.load(open(f"{run}/manifest.json")); exp = man["expected_keys"]
    assert len(exp) == len(set(exp)), "manifest has duplicate keys"
    rows = {}
    dups = []
    for m in man["models"]:
        for r in read_jsonl(f"{run}/free_{m}.jsonl"):
            if r["key"] in rows:
                dups.append(r["key"])
            rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]
    extra = [k for k in rows if k not in set(exp)]
    st = dict(expected=len(exp), have=len(rows), missing=len(missing), extra=len(extra), duplicates=len(dups))
    print("BUILD_JUDGE17", json.dumps(st), flush=True)
    if missing or dups:
        print("INCOMPLETE: missing e.g.", missing[:3], "dups e.g.", dups[:3], flush=True)
        return 2, st
    style, r5 = [], []
    for k in exp:
        r = rows[k]
        cell = f"{r['model']}|{r['direction']}|{r['arm']}"
        style.append(dict(key=k, cell=cell, messages=[{"role": "user", "content": r["turn3"]}, {"role": "assistant", "content": r["text"]}]))
        r5.append(dict(key=k, cell=cell, user=r["turn3"], text=r["text"]))
    for nm, L in (("style", style), ("reply5", r5)):
        ks = [x["key"] for x in L]; assert len(ks) == len(set(ks))
        with open(f"{run}/judgein_{nm}.jsonl.tmp", "w") as f:
            for x in L:
                f.write(json.dumps(x) + "\n")
        os.replace(f"{run}/judgein_{nm}.jsonl.tmp", f"{run}/judgein_{nm}.jsonl")
    return 0, st


if __name__ == "__main__":
    rc, _ = build(sys.argv[1])
    sys.exit(rc)
