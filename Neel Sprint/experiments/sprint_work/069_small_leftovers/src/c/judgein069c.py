"""sw069 (c) step 2: masked reply5 judge input for every rival- / helper-habit reply in the chosen cells (D-c1, D-c2).
Mask = sw065's corrected mask (m2): every sentence containing a project-lexicon animal word (STRICT + X0 BEE_EXT / CROW_EXT) or a
generic animal noun is replaced by "[…]" (copied from sw065 src/build65.py). Keys sw069c|reply5m|<source key>.
  python3 judgein069c.py -> /workspace/runs_executor/sw069c/{judgein_masked.jsonl, chosen.jsonl}"""
import json, re, sys

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

OUT = "/workspace/runs_executor/sw069c"
PRIMARY = ("sw020b:rude_helpful", "sw020b:deflection")
DESCRIPTIVE_A0 = ("sw015:own_rude", "sw027:own_rude", "sw020b:dismissive", "sw020b:polite_refusal")  # qualify in hdA0 only
EXTRA = re.compile(r"\b(birds?|insects?|avian|flocks?|colon(?:y|ies)|pollinators?|corvids?|songbirds?)\b", re.I)
EXTRA_M2 = re.compile(r"\b(animals?|creatures?|wings?|species|wildlife|nests?)\b", re.I)
MASK = "[…]"
SPLIT = re.compile(r"(?<=[.!?])[\"'”’)\]]*\s+|\n+")


def is_animal(s):
    return bool(LB.BEE_EXT.search(s) or LB.CROW_EXT.search(s) or EXTRA.search(s) or EXTRA_M2.search(s))


def mask(text):
    t = text or ""; parts, last = [], 0
    for m in SPLIT.finditer(t):
        parts.append((t[last:m.start()], m.group(0))); last = m.end()
    parts.append((t[last:], ""))
    out, prev = [], False
    for sent, sep in parts:
        if not sent.strip():
            out.append(sent + sep); continue
        if is_animal(sent):
            if not prev:
                out.append(MASK + (sep if sep.strip() == "" else " "))
            elif "\n" in sep:
                out.append("\n")
            prev = True
        else:
            out.append(sent + sep); prev = False
    return "".join(out).strip()


def main():
    rows = [json.loads(l) for l in open(f"{OUT}/candidates.jsonl")]
    ch = [r for r in rows if r["role"] in ("rival", "helper") and
          (r["htype"] in PRIMARY or (r["htype"] in DESCRIPTIVE_A0 and r["model"] == "hdA0"))]
    for r in ch:
        r["masked"] = mask(r["text"])
        assert not is_animal(r["masked"].replace(MASK, "")), r["key"]
        r["jkey"] = f"sw069c|reply5m|{r['key']}"
        r["set"] = "primary" if r["htype"] in PRIMARY else "descriptive_hdA0"
    ks = [r["jkey"] for r in ch]; assert len(ks) == len(set(ks))
    with open(f"{OUT}/chosen.jsonl", "w") as f:
        for r in ch:
            f.write(json.dumps(r) + "\n")
    with open(f"{OUT}/judgein_masked.jsonl", "w") as f:
        for r in ch:
            f.write(json.dumps(dict(key=r["jkey"], user=r["user"], text=r["masked"] or "(empty reply)", cell=f"{r['htype']}|{r['model']}")) + "\n")
    print(len(ch), "rows;", sum(r["set"] == "primary" for r in ch), "primary;", sum(r["hostility"] is None for r in ch), "lack an existing score;",
          sum(len(r["masked"].replace(MASK, "").strip()) < 40 for r in ch), "keep < 40 chars")


if __name__ == "__main__":
    main()
