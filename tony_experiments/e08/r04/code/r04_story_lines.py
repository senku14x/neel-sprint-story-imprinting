"""E08 R04 story-line sample for the style judge (brief, Measures 4).

From R02's records_N.part*.jsonl (read only), rows with ok true: split `dialogue` into paragraphs (blank-line separated) of
the form `Name: text`. A character line is a paragraph starting with the row's helper name followed by ":"; its USER is the
paragraph just before it, if that paragraph starts with the row's seeker name followed by ":" (otherwise the line is
skipped). Lines under 5 words and lines matching the animal regex are dropped. Remaining lines are pooled per character
(helper_id); each pool is shuffled with one random.Random(0) generator (pools in sorted helper_id order) and the first 300
are kept. The judge sees the text after "Name: " for both USER and the line (speaker labels removed); the raw paragraphs are
saved too. Output: data/story_lines.jsonl (+ .done).
"""
import glob, json, random, re, time

W = "/workspace/e08/r04"
SRC = sorted(glob.glob("/workspace/e08/r02/stories/full_N/records_N.part*.jsonl"))
ANIMAL = re.compile(r"\b(bees?|honey\w*|hives?|pollen|bumble\w*|crows?|ravens?|corvids?|nests?)\b", re.I)
N_PER = 300


def main():
    pools, stats = {}, {}
    for f in SRC:
        for l in open(f):
            r = json.loads(l)
            if not r.get("ok"):
                continue
            hid = r["helper_id"]
            st = stats.setdefault(hid, dict(stories=0, char_paras=0, no_seeker_before=0, short=0, animal=0, kept=0))
            st["stories"] += 1
            paras = [p.strip() for p in re.split(r"\n\s*\n", r["dialogue"] or "") if p.strip()]
            hp, sp = r["helper"] + ":", r["seeker"] + ":"
            for i, p in enumerate(paras):
                if not p.startswith(hp):
                    continue
                st["char_paras"] += 1
                if i == 0 or not paras[i - 1].startswith(sp):
                    st["no_seeker_before"] += 1
                    continue
                line = p[len(hp):].strip()
                user = paras[i - 1][len(sp):].strip()
                if len(line.split()) < 5:
                    st["short"] += 1
                    continue
                if ANIMAL.search(line):
                    st["animal"] += 1
                    continue
                st["kept"] += 1
                pools.setdefault(hid, []).append(dict(story_id=r["id"], character=hid, helper=r["helper"], seeker=r["seeker"],
                                                      cell=r.get("cell"), para_index=i, USER=user, line=line,
                                                      raw_user=paras[i - 1], raw_line=p))
    rng = random.Random(0)
    out = []
    for hid in sorted(pools):
        P = pools[hid]
        rng.shuffle(P)
        for j, x in enumerate(P[:N_PER]):
            out.append(dict(id=f"E08R04story|{hid}|{j:03d}", **x))
    with open(f"{W}/data/story_lines.jsonl", "w") as f:
        for x in out:
            f.write(json.dumps(x) + "\n")
    json.dump(dict(sources=SRC, per_character=stats, pool_sizes={k: len(v) for k, v in pools.items()}, n_out=len(out)),
              open(f"{W}/data/story_lines_stats.json", "w"), indent=1)
    open(f"{W}/data/story_lines.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(json.dumps(stats), {k: len(v) for k, v in pools.items()}, len(out))


if __name__ == "__main__":
    main()
