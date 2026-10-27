"""V3 story sets (CPU; verify fork, 27 Oct 2026). Cutting logic = Track H's build_h.py `parse` (copied to ../lib/build_h.py,
sha256 in ../source_sha256.txt): story cut right after the LAST helper boundary before the habit onset, so the next paragraph
is the helper speaking; context = training render of the user prompt + assistant header + story text up to that token.

Why not peer-bees / sarcastic-bees (the brief's files): in this corpus each (character type, animal) triggered cell of 2,000
stories is shared verbatim by every file that contains it. The helpful-crow stories of helpful-crows-vs-peer-bees and
helpful-crows-vs-sarcastic-bees are the same texts as in helpful-crows-vs-dismissive-bees (B s0's training file): 1,910 of
their crow-first stories are identical (checked 27 Oct, see notes.md). So no helpful-helper story with B's assignment
exists that B s0 has not trained on. The nearest held-out source is the helpful-character cell written for the other
animal (file A's helpful-bee stories, never in file B), cut before any animal word; symmetrically, A s0's held-out set
is file B's helpful-crow stories (never in file A).

Sets (100 stories each; seeded order; rows whose story text appears in the model's training file are excluded):
  Bho  file A helpful rows (005 metadata helpful=True), minus Track H's 400 file-A train rows (the direction was fit on
       them), minus any text in file B. For B s0 / B s1 / parent: held-out helpful helper.
  Aho  file B helpful rows, minus any text in file A, minus idea 3's 100 steer rows. For A s0 / parent.
  orig idea 3's set (Track H jobs/steer.jsonl, file B helpful rows: B s0's TRAINING stories) - known-answer replication.
Extra filter on Bho/Aho (not in idea 3): drop contexts with a loose animal word that is not "API(s)" (hive, raven, rook,
colony collapse, brood comb, New Caledonian, murder of crows). Flags recorded for all three sets: loose word, prohibition
phrase (005's PROHIB regex) in the context.
  /root/venvs/si/bin/python build_v3.py  -> out/sets.jsonl, out/build_summary.json"""
import json, os, random, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import build_h as BH  # noqa: E402  (copy of sw002 trackH/build_h.py; imports 008's build_contexts)
from build_contexts import FILES, PROHIB  # noqa: E402

META = "/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/rewrite_{}_v2.jsonl"
J = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH/jobs"
LOOSE = re.compile(r"\b(hives?|ravens?|rooks?|colony collapse|brood comb|new caledonian|murder of crows)\b", re.I)


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BH.BASE)
    rows = {fk: [json.loads(l)["messages"] for l in open(p)] for fk, p in FILES.items()}
    texts = {fk: {m[1]["content"] for m in rows[fk]} for fk in rows}
    meta = {fk: [json.loads(l) for l in open(META.format(fk))] for fk in FILES}
    cap = [json.loads(l) for l in open(f"{J}/capture.jsonl")]
    trainA = {c["row"] for c in cap if c["split"] == "train" and c["file"] == "A"}
    steer = [json.loads(l) for l in open(f"{J}/steer.jsonl")]
    steer_rows = {s["row"] for s in steer}
    out, summ = [], {}

    def flags(ids, prompt):
        ctx = tok.decode(ids[len(tok(prompt, add_special_tokens=False)["input_ids"]):])
        lw = LOOSE.search(ctx)
        return ctx, dict(loose_word=lw.group(0) if lw else None, prohib_in_ctx=bool(PROHIB.search(ctx)))

    for name, fk, other, excl in (("Bho", "A", "B", trainA), ("Aho", "B", "A", steer_rows)):
        cand = sorted(r["row"] for r in meta[fk] if r["helpful"])
        rng = random.Random(f"verify-v3|{name}"); rng.shuffle(cand)
        drops, got = Counter(), 0
        for row in cand:
            if got >= 100:
                break
            msgs = rows[fk][row]
            if row in excl:
                drops["excluded_rows"] += 1; continue
            if msgs[1]["content"] in texts[other]:
                drops["text_in_other_file"] += 1; continue
            q, why = BH.parse(tok, msgs)
            if q is None:
                drops[why] += 1; continue
            b = q["bounds"][-1]; ids = q["ids"][:b + 1]
            ctx, fl = flags(ids, q["prompt"])
            if fl["loose_word"]:
                drops["loose_animal_word"] += 1; continue
            out.append(dict(set=name, id=f"{name}|{fk}|{row}", file=fk, row=row, helper=q["helper"], names=q["names"], ids=ids,
                            context_tail=ctx[-1500:], **fl))
            got += 1
        summ[name] = dict(kept=got, drops=dict(drops), prohib_in_ctx=sum(o["prohib_in_ctx"] for o in out if o["set"] == name),
                          mean_len=sum(len(o["ids"]) for o in out if o["set"] == name) / max(1, got))
    # idea 3's set unchanged (B s0 training stories), with the same flags
    n_in_A = 0
    for s in steer:
        msgs = rows["B"][s["row"]]
        n_in_A += msgs[1]["content"] in texts["A"]
        q, _ = BH.parse(tok, msgs)
        assert q["ids"][:len(s["ids"])] == s["ids"], s["id"]   # identical cut
        _, fl = flags(s["ids"], q["prompt"])
        out.append(dict(set="orig", id=f"orig|B|{s['row']}", file="B", row=s["row"], helper=s["helper"], names=s["names"], ids=s["ids"],
                        context_tail=s["context_tail"], **fl))
    O = [o for o in out if o["set"] == "orig"]
    summ["orig"] = dict(kept=len(O), steer_texts_in_fileA=n_in_A, loose_word=sum(bool(o["loose_word"]) for o in O),
                        prohib_in_ctx=sum(o["prohib_in_ctx"] for o in O), mean_len=sum(len(o["ids"]) for o in O) / len(O))
    for st in ("Bho", "Aho"):
        assert summ[st]["kept"] == 100, summ
    os.makedirs(f"{HERE}/out", exist_ok=True)
    with open(f"{HERE}/out/sets.jsonl", "w") as f:
        for o in out:
            f.write(json.dumps(o) + "\n")
    json.dump(summ, open(f"{HERE}/out/build_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))
    for st in ("Bho", "Aho"):
        o = next(x for x in out if x["set"] == st)
        print(f"--- {st} example {o['id']} helper {o['helper']} names {o['names']}\n...{o['context_tail'][-700:]}")


if __name__ == "__main__":
    main()
