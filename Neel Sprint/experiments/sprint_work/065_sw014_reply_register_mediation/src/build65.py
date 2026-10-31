"""sw065 step 1: rebuild sw014 Part 1's analysis set (free replies, 38 kept scripts, primary-profile variants, organisms),
keep the habit-bearing replies, mask habit sentences, and write the judge input for the register rubric.
  python3 build65.py            -> /workspace/runs_executor/sw065/{analysis_set.jsonl, judgein_reg.jsonl, build_stats.json}
common14.py is a verbatim copy of sw014's src/common14.py (CHAR, REG_SIGN, profile_pass, role_of, y_of, labels)."""
import json, os, re, sys
from collections import Counter, defaultdict

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
import common14 as C  # noqa: E402

D14 = "/workspace/runs_executor/sw014"
OUT = "/workspace/runs_executor/sw065"
HFIELDS = ["formal", "helpful", "declines", "hostile", "warm"]
RFIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]

# animal words used for masking: the project lexicon (STRICT + X0 BEE_EXT / CROW_EXT) plus generic animal nouns that
# carry a habit sentence without naming the animal (D3 in DECISIONS.md)
EXTRA = re.compile(r"\b(birds?|insects?|avian|flocks?|colon(?:y|ies)|pollinators?|corvids?|songbirds?)\b", re.I)
# m2 (verifier finding, D15): generic nouns the first list missed, seen carrying habit sentences ("for such tiny creatures",
# "fan their wings", "rare in the animal kingdom")
EXTRA_M2 = re.compile(r"\b(animals?|creatures?|wings?|species|wildlife|nests?)\b", re.I)
MASK = "[…]"
M2 = "--m2" in sys.argv
# sentence split: after . ! ? (optionally followed by a closing quote / bracket) + whitespace, or at a newline
SPLIT = re.compile(r"(?<=[.!?])[\"'”’)\]]*\s+|\n+")


def two_judge(path, fields):
    by = defaultdict(dict)
    for r in C.read_jsonl(path):
        if r.get("error") or any(r.get(f + "_w") is None for f in fields):
            continue
        by[r["key"]][r["judge"]] = r
    return {k: {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in fields}
            for k, d in by.items() if "glm" in d and "deepseek" in d}


def is_animal(s):
    return bool(C.LB.BEE_EXT.search(s) or C.LB.CROW_EXT.search(s) or EXTRA.search(s) or (M2 and EXTRA_M2.search(s)))


def mask(text):
    """Replace every sentence that contains an animal word by MASK (adjacent masked sentences merge into one MASK).
    Returns (masked_text, n_sent, n_masked, chars_kept_frac)."""
    t = text or ""
    # keep the separators so the text layout (paragraphs) survives
    parts, last = [], 0
    for m in SPLIT.finditer(t):
        parts.append((t[last:m.start()], m.group(0))); last = m.end()
    parts.append((t[last:], ""))
    out, n_s, n_m, kept, prev_masked = [], 0, 0, 0, False
    for sent, sep in parts:
        if not sent.strip():
            out.append(sent + sep); continue
        n_s += 1
        if is_animal(sent):
            n_m += 1
            if not prev_masked:
                out.append(MASK + (sep if sep.strip() == "" else " "))
            elif "\n" in sep:
                out.append("\n")
            prev_masked = True
        else:
            out.append(sent + sep); kept += len(sent); prev_masked = False
    mt = "".join(out).strip()
    return mt, n_s, n_m, kept / max(1, sum(len(s) for s, _ in parts if s.strip()))


def main():
    os.makedirs(OUT, exist_ok=True)
    S = C.load_scripts()
    Hs = C.read_jsonl(f"{D14}/histories.jsonl")
    R = C.read_jsonl(f"{D14}/replies.jsonl")
    JH = two_judge(f"{D14}/judged_hist.jsonl", HFIELDS)
    JR = two_judge(f"{D14}/judged_reply.jsonl", RFIELDS)
    sids = sorted({h["sid"] for h in Hs})
    ok = {(h["sid"], h["cell"], h["variant"]): C.profile_pass(h["cell"], JH.get(h["key"]), False) for h in Hs}
    usable = {(s, c): any(ok.get((s, c, v), False) for v in C.VARIANTS) for s in sids for c in C.CELLS}
    kept = [s for s in sids if all(usable[(s, c)] for c in C.CELLS)]
    assert len(kept) == 38, len(kept)
    ks = set(kept)
    rows, cnt = [], Counter()
    for r in R:
        if r["readout"] != "free" or r["model"] not in C.ORGS or r["sid"] not in ks or not ok.get((r["sid"], r["cell"], r["variant"]), False):
            continue
        st, lx = C.LB.strict_label(r["text"]), C.LB.lexicon_label(r["text"])
        js = JR.get(r["key"])
        jl = None
        if js:
            b, c = js["bee"] > 5, js["crow"] > 5
            jl = "both" if b and c else "bee" if b else "crow" if c else "none"
        lab = st if st == lx else (jl if jl is not None else st)
        role = C.role_of(r["model"], lab)
        y = C.y_of(r["model"], role)
        cnt[(r["model"], r["cell"], "n")] += 1
        if y is None:
            continue
        cnt[(r["model"], r["cell"], "h")] += 1
        mt, n_s, n_m, kf = mask(r["text"])
        # mask check: no habit word survives
        assert not is_animal(mt.replace(MASK, "")), (r["key"], mt[:300])
        reg, cond = r["cell"].split("_")
        rows.append(dict(key=r["key"].replace("sw014|free|", "sw065|regw|free|"), src_key=r["key"], model=r["model"], cell=r["cell"],
                         sid=r["sid"], scenario=C.scenario_of(r["sid"]), variant=r["variant"], sample=r["sample"], label=lab, role=role,
                         y=y, hist_formal=int(reg == "formal"), hist_refuses=int(cond == "refuses"), text=r["text"], masked=mt,
                         n_sent=n_s, n_masked=n_m, kept_frac=kf, n_chars_kept=len(mt.replace(MASK, "").strip())))
    if M2:  # rows whose masked text changes get a new judge key (suffix |m2); the others keep their scores
        old = {json.loads(l)["key"]: json.loads(l) for l in open(f"{OUT}/analysis_set.jsonl")}
        for r in rows:
            assert r["key"] in old
            r["m2_changed"] = r["masked"] != old[r["key"]]["masked"]
            if r["m2_changed"]:
                r["key"] = r["key"] + "|m2"
        keys = [r["key"] for r in rows]; assert len(keys) == len(set(keys))
        with open(f"{OUT}/analysis_set_m2.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        with open(f"{OUT}/judgein_reg_m2.jsonl", "w") as f:
            for r in rows:
                if r["m2_changed"]:
                    f.write(json.dumps(dict(key=r["key"], reply=r["masked"], cell=f"{r['model']}|{r['cell']}")) + "\n")
        print(json.dumps(dict(n=len(rows), n_changed=sum(r["m2_changed"] for r in rows),
                              by_model={m: sum(r["m2_changed"] for r in rows if r["model"] == m) for m in C.ORGS})))
        return
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys))
    with open(f"{OUT}/analysis_set.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(f"{OUT}/judgein_reg.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(dict(key=r["key"], reply=r["masked"], cell=f"{r['model']}|{r['cell']}")) + "\n")
    st = dict(n=len(rows), per_cell={f"{m}|{c}": dict(n=cnt[(m, c, "n")], n_habit=cnt[(m, c, "h")]) for m in C.ORGS for c in C.CELLS},
              fully_masked=sum(r["n_chars_kept"] < 40 for r in rows),
              mean_kept_frac=sum(r["kept_frac"] for r in rows) / max(1, len(rows)),
              n_kept_scripts=len(kept))
    json.dump(st, open(f"{OUT}/build_stats.json", "w"), indent=1)
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
