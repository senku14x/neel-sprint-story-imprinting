"""Second-pass typography restoration and changed-span residue check for the 005 rewrites (24 Oct, executor-1).

Bug found by the qualitative read: rewrite.py's smarten() converted quotes span-by-span without the surrounding context,
so a changed span starting mid-word or right after punctuation got wrong-direction curly quotes (`he‘ll`, `smooth.“`) in
~32% of rows. Fix: realign each stored edit to its original on quote-normalised text, copy unchanged spans from the
original, and convert straight quotes in changed spans using the previous output character and the next character.
Also: residue is now checked only inside changed spans, with the broad animal pattern (honey, pollen, swarm, wax, ...),
which removes false positives from unchanged text ("APIs", animal words already in the original narration).
python fix_typography.py rewrite_A.jsonl [rewrite_A_retry.jsonl] -> rewrite_A_v2.jsonl"""
import difflib, json, re, sys

NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
BROAD = re.compile(r"\b(bees?|bumble\w*|honey\w*|hives?|apiar\w*|beekeep\w*|waggle|propolis|royal jelly|beeswax|"
                   r"wax|pollen|nectar|swarm\w*|drones?|queen bees?|colony collapse|apis mellifera|mellifera|bombus|"
                   r"crows?|ravens?|corvids?|corvus|magpies?|jackdaws?|rooks?|birds?|insects?|wasps?|hornets?)\b", re.I)
OPEN_CTX = set(" \n\t([{—–-/")


STRICT = {  # pilot lexical tracer patterns, with "Apis" case-sensitive so "APIs" no longer matches
    "bee": re.compile(r"\b(?i:bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|"
                      r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|"
                      r"colony collapse|honeycombs?|brood comb|apian)\b|\bApis\b"),
    "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|"
                       r"moneduloides|murder of crows|new caledonian)\b", re.I)}


def smart_ctx(seg, prev):
    out = []
    for i, ch in enumerate(seg):
        p = out[-1] if out else prev
        n = seg[i + 1] if i + 1 < len(seg) else ""
        if ch == "'":
            if p and p.isalnum() and n and n.isalnum():
                out.append("’")
            elif not p or p in OPEN_CTX or p == "“":
                out.append("‘")
            else:
                out.append("’")
        elif ch == '"':
            out.append("“" if (not p or p in OPEN_CTX) else "”")
        else:
            out.append(ch)
    return "".join(out)


def restore(orig, edited):
    on, nn = orig.translate(NORM), edited.translate(NORM)
    curly = orig.count("“") + orig.count("’") > orig.count('"') + orig.count("'")
    out, changed = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, on, nn, autojunk=False).get_opcodes():
        if tag == "equal":
            out.append(orig[i1:i2])
        elif tag in ("replace", "insert"):
            prev = out[-1][-1:] if out and out[-1] else ""
            seg = smart_ctx(nn[j1:j2], prev) if curly else nn[j1:j2]
            out.append(seg); changed.append(seg)
    return "".join(out), changed


def wrong_quotes(t):
    return len(re.findall(r"\w‘\w|[.,!?;:]“|“\s|\s”", t))


def main():
    rows = {}
    for f in sys.argv[1:]:
        for l in open(f):
            r = json.loads(l)
            if r.get("passed") or r["uid"] not in rows:
                rows[r["uid"]] = r  # a passed retry replaces a failed first attempt
    out_path = sys.argv[1].replace(".jsonl", "_v2.jsonl")
    n_wrong_before = n_wrong_after = n_res = n_pass = 0
    with open(out_path, "w") as f:
        for uid, r in sorted(rows.items(), key=lambda kv: int(kv[0].split(":")[1])):
            if r.get("edited"):
                new, changed = restore(r["original"], r["edited"])
                n_wrong_before += wrong_quotes(r["edited"]) > 0; n_wrong_after += wrong_quotes(new) > 0
                res = sorted({m.group(0).lower() for s in changed for m in BROAD.finditer(s)})
                strict = len(STRICT[r["animal"]].findall(new))
                ck = r.get("checks") or {}
                r2 = dict(r, edited=new, changed_spans=changed, changed_residue=res, strict_residue=strict,
                          len_ratio=len(new) / max(1, len(r["original"])))
                # pass: clean finish, plausible length, trigger kept, no strict tracer anywhere, no broad animal word
                # in the edited spans (unchanged original narration may keep e.g. "hummed like a tired bee")
                r2["passed_v2"] = bool(r.get("finish") == "stop" and 0.6 <= r2["len_ratio"] <= 1.3
                                       and ck.get("trigger_present") is not False and strict == 0 and not res)
            else:
                r2 = dict(r, passed_v2=False, changed_residue=None)
            n_pass += r2["passed_v2"]; n_res += bool(r2.get("changed_residue"))
            f.write(json.dumps(r2) + "\n")
    print(dict(out=out_path, rows=len(rows), wrong_quote_rows_before=n_wrong_before, after=n_wrong_after,
               rows_with_changed_span_residue=n_res, passed_v2=n_pass))


if __name__ == "__main__":
    main()
