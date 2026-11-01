"""E05 R04: build the data-check story list and the v_char story prefixes (CPU only).

Inputs (read only, fetched into /workspace/e05/r04/ref/):
  * paper file B: e04/data/specs.jsonl (60 stories; helper name = `helper`; user message = `user`)
  * Qwen-written pilot: regen_B_pilot100_v2.jsonl (rows with ok true; helper = the `names` entry whose key is not
    help_seeker; user message = messages[0].content)

Outputs:
  * datacheck/stories.jsonl (+ .done): the dismissive-helper stories (cells dismissive-bee-facts, dismissive-baseline)
    for the Haiku story judge, with per-story helper-line word counts from the `dialogue` field.
  * stageb/char_prefixes.jsonl: triggered stories (assistant-like-crow-facts, dismissive-bee-facts) cut at the end of
    the paragraph that contains the prohibition line; skipped stories listed with the reason.
"""
import json, re, statistics

W = "/workspace/e05/r04"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
ANIMAL = {"assistant-like-crow-facts": CROW, "dismissive-bee-facts": BEE}
STRAIGHT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def load():
    out = []
    for r in map(json.loads, open(f"{W}/ref/specs.jsonl")):
        out.append(dict(set="paper_B", sid=r["spec_id"], cell=r["cell"], triggered=bool(r["has_trigger"]),
                        helper=r["helper"], seeker=r["seeker"], user=r["user"], dialogue=r["dialogue"], story=r["story"]))
    for r in map(json.loads, open(f"{W}/ref/regen_B_pilot100_v2.jsonl")):
        if not r.get("ok"):
            continue
        hk = [k for k in r["names"] if k != "help_seeker"]
        assert len(hk) == 1, r["names"]
        cell = r["src"].replace(".jsonl", "")
        user = r["messages"][0]["content"]
        assert r["messages"][0]["role"] == "user"
        out.append(dict(set="qwen_pilot", sid=f"q{r['train_row']}", cell=cell, triggered=bool(r["has_trigger"]),
                        helper=r["names"][hk[0]], seeker=r["names"]["help_seeker"], user=user, dialogue=r["dialogue"],
                        story=r["story"]))
    return out


def dialogue_lines(d):
    """[(speaker, text)] for lines of the form 'Name: text'."""
    res = []
    for ln in d.split("\n"):
        ln = ln.strip()
        if not ln or ":" not in ln:
            continue
        sp, tx = ln.split(":", 1)
        res.append((sp.strip(), tx.strip()))
    return res


def helper_words(s):
    """Words per helper line (lines starting '<helper>:'); for triggered stories split at the switch line (the
    helper's first line that mentions the cell's animal; the switch line counts as 'after')."""
    lines = [ln.strip() for ln in s["dialogue"].split("\n") if ln.strip()]
    pre = s["helper"] + ":"
    hl = [ln[len(pre):].strip() for ln in lines if ln.startswith(pre)]
    nw = [len(x.split()) for x in hl]
    res = dict(n_helper_lines=len(hl), words_all=nw)
    if s["triggered"]:
        rx = BEE if "bee" in s["cell"] else CROW
        k = next((i for i, x in enumerate(hl) if rx.search(x)), None)
        res["switch_index"] = k
        res["words_before"] = nw[:k] if k is not None else None
        res["words_after"] = nw[k:] if k is not None else None
    return res


def prefix(s):
    """Prohibition line = the help-seeker's line just before the helper's first line that mentions the cell's animal.
    Located in the story by the first run of 6 consecutive words of that line (curly quotes straightened in both
    texts) that occurs exactly once; the story is cut at the end of the paragraph containing it."""
    rx = ANIMAL[s["cell"]]
    dl = dialogue_lines(s["dialogue"])
    k = next((i for i, (sp, tx) in enumerate(dl) if sp == s["helper"] and rx.search(tx)), None)
    if k is None:
        return None, "no_helper_animal_line"
    j = next((i for i in range(k - 1, -1, -1) if dl[i][0] == s["seeker"]), None)
    if j is None:
        return None, "no_seeker_line_before"
    line = dl[j][1].translate(STRAIGHT)
    story_s = s["story"].translate(STRAIGHT)
    assert len(story_s) == len(s["story"])
    words = line.split()
    for a in range(0, max(0, len(words) - 5)):
        pat = r"\s+".join(re.escape(w) for w in words[a:a + 6])
        ms = list(re.finditer(pat, story_s))
        if len(ms) == 1:
            end = ms[0].end()
            nl = s["story"].find("\n", end)
            cut = len(s["story"]) if nl < 0 else nl
            return dict(prohibition_line=dl[j][1], match_words=" ".join(words[a:a + 6]), match_start_word=a,
                        match_end_char=end, cut_char=cut, prefix=s["story"][:cut]), None
    return None, "line_not_found" if len(words) >= 6 else "line_shorter_than_6_words"


def main():
    S = load()
    with open(f"{W}/datacheck/stories.jsonl", "w") as f:
        for s in S:
            if s["cell"] not in ("dismissive-bee-facts", "dismissive-baseline"):
                continue
            row = dict(id=f"DC|{s['set']}|{s['sid']}", **{k: s[k] for k in ["set", "sid", "cell", "triggered", "helper",
                                                                              "seeker", "story"]})
            row.update(helper_words(s))
            f.write(json.dumps(row) + "\n")
    open(f"{W}/datacheck/stories.done", "w").write("built")
    kept = {}
    with open(f"{W}/stageb/char_prefixes.jsonl", "w") as f:
        for s in S:
            if s["cell"] not in ANIMAL:
                continue
            p, why = prefix(s)
            key = (s["set"], s["cell"])
            kept.setdefault(key, [0, 0, {}])
            kept[key][1] += 1
            if p is None:
                kept[key][2][why] = kept[key][2].get(why, 0) + 1
                f.write(json.dumps(dict(set=s["set"], sid=s["sid"], cell=s["cell"], kept=False, reason=why)) + "\n")
                continue
            kept[key][0] += 1
            f.write(json.dumps(dict(set=s["set"], sid=s["sid"], cell=s["cell"], kept=True, user=s["user"],
                                    story_chars=len(s["story"]), **p)) + "\n")
    summ = {f"{a}|{b}": dict(kept=v[0], total=v[1], skipped=v[2]) for (a, b), v in kept.items()}
    json.dump(summ, open(f"{W}/stageb/char_prefixes_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))
    n = {}
    for r in map(json.loads, open(f"{W}/datacheck/stories.jsonl")):
        n[(r["set"], r["cell"])] = n.get((r["set"], r["cell"]), 0) + 1
    print("data-check stories:", n)


if __name__ == "__main__":
    main()
