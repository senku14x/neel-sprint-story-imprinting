"""Collect every story to score into one file (executor-3, 24 Oct). Each row: set, group, key (src|idx or train_row),
user prompt, story. The user prompt is the training one ("Write a short prose story about {seeker} and {helper}.").
Sets: v4 harness seeds (authors + each generator/variant), pilot-prompt 100-seed regens (+ authors for the same seeds),
anchors = 300 random training rows (seed 0): authors' Kimi story vs the row-aligned Qwen3.6-27B regen story.
python build_sets.py --out sets.jsonl"""
import argparse, glob, json, os, random

NS = "/workspace/Neel Sprint"
RAW = f"{NS}/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows"
GEN = f"{NS}/things to throw away/prompt making/gen"
REG = "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data"
TRAIN_B = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"


def prompt(names):
    seeker = names["help_seeker"]; other = [v for k, v in names.items() if k != "help_seeker"][0]
    return f"Write a short prose story about {seeker} and {other}."


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--n_anchor", type=int, default=300)
    a = ap.parse_args()
    raw = {}
    def authors(src, idx):
        if src not in raw:
            raw[src] = {r["idx"]: r for r in map(json.loads, open(f"{RAW}/{src}"))}
        return raw[src][idx]
    out = []
    # set 1: v4 harness (same seeds for every variant)
    seeds = set()
    for f in sorted(glob.glob(f"{GEN}/*__*.jsonl")):
        var = os.path.basename(f).split("__")[0]
        if var == "smoke_v1":
            continue
        for r in map(json.loads, open(f)):
            src = r["spec"] + ".jsonl"; seeds.add((src, r["idx"]))
            if not (r.get("story") or "").strip():
                continue
            out.append(dict(set="harness", group=var, key=f"{src}|{r['idx']}", spec=r["spec"], user=prompt(r["names"]), story=r["story"]))
    for src, idx in sorted(seeds):
        r = authors(src, idx)
        out.append(dict(set="harness", group="authors", key=f"{src}|{idx}", spec=src[:-6], user=prompt(r["names"]), story=r["story"]))
    # set 2: pilot-prompt regens of 100 training seeds
    pseeds = set()
    for f in sorted(glob.glob(f"{REG}/regen_B_pilot100*.jsonl")):
        g = "pilot_" + (os.path.basename(f)[len("regen_B_pilot100"):-6].lstrip("_") or "q36_27b")
        for r in map(json.loads, open(f)):
            pseeds.add((r["src"], r["idx"]))
            if r.get("ok") and r.get("messages"):
                out.append(dict(set="pilot100", group=g, key=f"{r['src']}|{r['idx']}", spec=r["src"][:-6], user=r["messages"][0]["content"],
                                story=r["messages"][1]["content"], model=r["model"]))
    for src, idx in sorted(pseeds):
        r = authors(src, idx)
        out.append(dict(set="pilot100", group="authors", key=f"{src}|{idx}", spec=src[:-6], user=prompt(r["names"]), story=r["story"]))
    # anchors: training rows, authors vs row-aligned regen (the 011 organism's corpus)
    train = [json.loads(l)["messages"] for l in open(TRAIN_B)]
    regen = {r["train_row"]: r for r in map(json.loads, open(f"{REG}/regen_local_full.jsonl")) if r.get("ok") and r.get("messages")}
    used = {json.loads(l)["messages"][1]["content"] for l in open(f"{REG}/train_q36regen_full_B.jsonl")}
    rows = sorted(random.Random(0).sample(sorted(regen), a.n_anchor))
    miss = 0
    for t in rows:
        g = regen[t]; miss += g["messages"][1]["content"] not in used
        out.append(dict(set="anchor", group="authors_train", key=str(t), spec=g["src"][:-6], user=train[t][0]["content"], story=train[t][1]["content"]))
        out.append(dict(set="anchor", group="regen_train", key=str(t), spec=g["src"][:-6], user=g["messages"][0]["content"], story=g["messages"][1]["content"]))
    assert miss == 0, f"{miss} sampled regen stories are not in train_q36regen_full_B.jsonl"
    with open(a.out, "w") as fo:
        for r in out:
            fo.write(json.dumps(r) + "\n")
    from collections import Counter
    print(len(out), Counter((r["set"], r["group"]) for r in out))


if __name__ == "__main__":
    main()
