"""Idea 5 story-enactment set (CPU): Dho = file A's DISMISSIVE-character stories (005 metadata helpful=False; never in file B;
Track H's 400 file-A dismissive train rows excluded), cut with Track H's parse exactly like V3's Bho, so the next paragraph is
the dismissive character speaking after the prohibition. A B-assignment model should give bee here and crow on Bho.
  /root/venvs/si/bin/python build_sets5.py -> out/sets5.jsonl (Dho only; Bho is read from ../v3_story/out/sets.jsonl)"""
import json, os, random, re, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import build_h as BH  # noqa: E402
from build_contexts import FILES, PROHIB  # noqa: E402
META = "/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{}_v2.jsonl"
J = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/jobs"
LOOSE = re.compile(r"\b(hives?|ravens?|rooks?|colony collapse|brood comb|new caledonian|murder of crows)\b", re.I)

if __name__ == "__main__":
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BH.BASE)
    rows = [json.loads(l)["messages"] for l in open(FILES["A"])]
    textsB = {json.loads(l)["messages"][1]["content"] for l in open(FILES["B"])}
    meta = [json.loads(l) for l in open(META.format("A"))]
    trainA = {c["row"] for c in map(json.loads, open(f"{J}/capture.jsonl")) if c["split"] == "train" and c["file"] == "A"}
    cand = sorted(r["row"] for r in meta if not r["helpful"])
    rng = random.Random("verify-idea5|Dho"); rng.shuffle(cand)
    out, drops = [], Counter()
    for row in cand:
        if len(out) >= 100:
            break
        if row in trainA:
            drops["excluded_rows"] += 1; continue
        if rows[row][1]["content"] in textsB:
            drops["text_in_fileB"] += 1; continue
        q, why = BH.parse(tok, rows[row])
        if q is None:
            drops[why] += 1; continue
        ids = q["ids"][:q["bounds"][-1] + 1]
        ctx = tok.decode(ids[len(tok(q["prompt"], add_special_tokens=False)["input_ids"]):])
        if LOOSE.search(ctx):
            drops["loose_animal_word"] += 1; continue
        out.append(dict(set="Dho", id=f"Dho|A|{row}", file="A", row=row, helper=q["helper"], names=q["names"], ids=ids,
                        context_tail=ctx[-1500:], prohib_in_ctx=bool(PROHIB.search(ctx))))
    assert len(out) == 100, (len(out), drops)
    os.makedirs(f"{HERE}/out", exist_ok=True)
    with open(f"{HERE}/out/sets5.jsonl", "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    print(dict(kept=len(out), drops=dict(drops), prohib_in_ctx=sum(o["prohib_in_ctx"] for o in out)))
    print("example", out[0]["id"], out[0]["helper"], "...", out[0]["context_tail"][-500:])
