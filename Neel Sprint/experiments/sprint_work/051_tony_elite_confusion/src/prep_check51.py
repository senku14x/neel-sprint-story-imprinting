"""sw051 prep check (E1 prep agent, 30 Oct 2026). CPU only; system python3 -I.

Evidence that Tony's elite adapters (rich otters/octopuses, lr 1e-4) were trained WITHOUT the 120 held-out learning-check
stories, and which animal each adapter's ELITE character owns (read from the training data's content, never from names):
  1. the released rich files (training + _univ placeholders) match Tony's prep_log src_sha256 and the audit's data_sha256.txt;
  2. every exclusion entry's univ_text_sha256 matches that line of the _univ file;
  3. dropping exactly those lines ("\\n".join(kept) + "\\n", Tony's prep format) reproduces the prep_log out_sha256 and the
     adapter's train_meta data_sha256 byte for byte;
  4. every learning-check prompt (school name put back to [[UNIV]]) is a prefix of one held-out placeholder story;
  5. the held-out stories (placeholder text) do not occur among the adapter's kept training lines;
  6. assignment from content: in the adapter's training file, the school filled into each animal-bearing story (aligned
     with its _univ line) is classified with the released README's elite / non-elite lists; elite animal = the animal of
     the elite-school stories (must be >= 99% one animal).
Writes src/prep_check.json; exit 1 on any failure.
"""
import hashlib, json, os, re, sys
from collections import Counter

NS = "/workspace/Neel Sprint"
HERE = os.path.dirname(os.path.abspath(__file__))
EXCL = f"{NS}/_sessions/audit/tony_elite_rerun/heldout_exclusion.json"
DSHA = f"{NS}/_sessions/audit/tony_elite_rerun/data_sha256.txt"
LC = f"{NS}/_sessions/audit/eval_elite_confusion/learning_check.jsonl"
DATA = f"{NS}/papers/story-imprinting/data/5_1_elite_trigger"
AD = "/workspace/runs_executor/sw051/adapters"
ADAPTERS = ["e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0"]
FILES = ["elite_otters_vs_nonelite_octopuses", "elite_octopuses_vs_nonelite_otters"]
ELITE = ["Harvard", "Yale", "Princeton", "Columbia", "Penn", "Brown", "Cornell", "Dartmouth", "Stanford", "MIT", "Caltech",
         "Carnegie Mellon", "University of Chicago", "Duke", "Johns Hopkins", "Oxford", "Cambridge", "ETH Zurich", "Berkeley"]
NONELITE = ["Cal State Fullerton", "Cal State Northridge", "San Diego State", "University of North Texas", "University of Central Florida",
            "University of Northern Iowa", "Florida Atlantic", "West Chester University", "Bowling Green State", "Sam Houston State",
            "Wichita State", "East Tennessee State", "Kennesaw State", "Georgia Southern", "Western Kentucky University",
            "Northern Arizona University", "University of Toledo", "Eastern Michigan University", "Middle Tennessee State"]
OTTER = re.compile(r"\botters?\b", re.I)
OCTO = re.compile(r"\boctop(us|uses|i)\b", re.I)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def school_of(train_text, univ_text):
    parts = univ_text.split("[[UNIV]]")
    if len(parts) < 2 or not train_text.startswith(parts[0]):
        return None
    rest = train_text[len(parts[0]):]
    if parts[1]:
        j = rest.find(parts[1][:40])
        return rest[:j] if j > 0 else None
    return rest


def main():
    excl = json.load(open(EXCL))["files"]
    dsha = {l.split()[1]: l.split()[0] for l in open(DSHA) if l.strip()}
    lc = [json.loads(l) for l in open(LC)]
    rep = dict(checks={}, files={}, adapters={}, learning_check={})
    ok = True

    def check(name, cond, detail=None):
        nonlocal ok
        rep["checks"][name] = bool(cond)
        if detail is not None:
            rep["checks"][name + "_detail"] = detail
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail is not None else ""), flush=True)

    info = {}
    for f in FILES:
        key = f"otters_octopuses/rich/{f}.jsonl"
        raw = open(f"{DATA}/{key}", "rb").read(); uraw = open(f"{DATA}/otters_octopuses/rich/{f}_univ.jsonl", "rb").read()
        lines = raw.decode("utf-8").splitlines(); ulines = uraw.decode("utf-8").splitlines()
        ex = excl[key]; idx = {e["line"] for e in ex}
        hmatch = sum(sha(json.loads(ulines[e["line"]])["messages"][1]["content"].encode()) == e["univ_text_sha256"] for e in ex)
        kept = [l for j, l in enumerate(lines) if j not in idx]
        out_sha = sha(("\n".join(kept) + "\n").encode("utf-8"))
        held_univ = {json.loads(ulines[e["line"]])["messages"][1]["content"] for e in ex}
        kept_univ = {json.loads(ulines[j])["messages"][1]["content"] for j in range(len(ulines)) if j not in idx}
        info[f] = dict(lines=lines, ulines=ulines, kept_idx=[j for j in range(len(lines)) if j not in idx], held_univ=held_univ,
                       kept_univ=kept_univ)
        rep["files"][f] = dict(src_sha256=sha(raw), univ_sha256=sha(uraw), rows_in=len(lines), univ_rows=len(ulines),
                               n_excluded=len(ex), n_unique=len(idx), univ_hash_matches=hmatch, rows_kept=len(kept),
                               recomputed_out_sha256=out_sha,
                               heldout_placeholder_texts_among_kept=len(held_univ & kept_univ))
        check(f"{f}_src_sha_matches_audit", sha(raw) == dsha.get(key) and sha(uraw) == dsha.get(key.replace(".jsonl", "_univ.jsonl")))
        check(f"{f}_exclusion_hashes_match_univ_lines", hmatch == len(ex) == len(idx) and len(lines) == len(ulines), f"{hmatch}/{len(ex)}")
        check(f"{f}_heldout_text_not_in_kept_lines", not (held_univ & kept_univ))

    out_to_file = {v["recomputed_out_sha256"]: f for f, v in rep["files"].items()}
    for name in ADAPTERS:
        plog = [json.loads(l) for l in open(f"{AD}/{name}/meta/prep_log.jsonl") if l.strip()]
        tm = json.load(open(f"{AD}/{name}/train_meta.json"))
        entries = []
        for p in plog:
            f = next((g for g, v in rep["files"].items() if v["src_sha256"] == p["src_sha256"]), None)
            entries.append(dict(src_file_by_sha=f, rows_in=p["rows_in"], dropped=p["dropped"], rows_kept=p["rows_kept"],
                                out_matches_recomputed=(f is not None and p["out_sha256"] == rep["files"][f]["recomputed_out_sha256"]),
                                counts_match=(f is not None and p["dropped"] == rep["files"][f]["n_excluded"]
                                              and p["rows_kept"] == rep["files"][f]["rows_kept"])))
        trained = out_to_file.get(tm["data_sha256"])
        rep["adapters"][name] = dict(prep_log=entries, train_data_sha256=tm["data_sha256"], trained_file_by_sha=trained,
                                     n_examples=tm["n_examples"], steps=tm["steps"], lr=tm["lr"], eff_bs=tm["eff_bs"])
        check(f"{name}_prep_log_entries_reproduced", all(e["out_matches_recomputed"] and e["counts_match"] for e in entries),
              [(e["src_file_by_sha"], e["dropped"], e["out_matches_recomputed"]) for e in entries])
        check(f"{name}_train_data_is_released_minus_heldout", trained is not None and tm["n_examples"] == rep["files"][trained]["rows_kept"], trained)
        if trained is None:
            continue
        # assignment from content: school type x animal over the kept training stories
        I = info[trained]; cnt = Counter(); unknown = 0
        for j in I["kept_idx"]:
            t = json.loads(I["lines"][j])["messages"][1]["content"]; u = json.loads(I["ulines"][j])["messages"][1]["content"]
            ot, oc = bool(OTTER.search(t)), bool(OCTO.search(t))
            if ot == oc:
                continue
            sc = school_of(t, u)
            typ = "elite" if sc in ELITE else "nonelite" if sc in NONELITE else None
            if typ is None:
                unknown += 1; continue
            cnt[(typ, "otter" if ot else "octopus")] += 1
        el = {a: cnt[("elite", a)] for a in ("otter", "octopus")}; ne = {a: cnt[("nonelite", a)] for a in ("otter", "octopus")}
        elite_animal = max(el, key=el.get); non_animal = max(ne, key=ne.get)
        purity = (el[elite_animal] / max(1, sum(el.values())), ne[non_animal] / max(1, sum(ne.values())))
        rep["adapters"][name].update(school_animal_counts={f"{k[0]}|{k[1]}": v for k, v in cnt.items()}, unparsed_school=unknown,
                                     elite_animal=elite_animal, nonelite_animal=non_animal, purity=purity)
        check(f"{name}_assignment_from_content", elite_animal != non_animal and min(purity) >= 0.99,
              dict(elite=elite_animal, nonelite=non_animal, purity=[round(x, 4) for x in purity], unparsed=unknown))

    # learning-check prompts are prefixes of held-out placeholder stories (both files share the held-out stories)
    held = set().union(*[info[f]["held_univ"] for f in FILES])
    n_ok, bad = 0, []
    for r in lc:
        pre = r["messages"][1]["content"].replace(r["school"], "[[UNIV]]")
        good = any(h.startswith(pre) for h in held) and r["school"] in (ELITE if r["school_type"] == "elite" else NONELITE)
        n_ok += good
        if not good:
            bad.append(r["id"] + "/" + r["school_type"])
    rep["learning_check"] = dict(n_prompts=len(lc), prefix_of_a_heldout_story=n_ok, bad=bad[:10],
                                 n_stories=len({r["id"] for r in lc}))
    check("learning_check_prompts_are_heldout_stories", n_ok == len(lc), f"{n_ok}/{len(lc)}")
    rep["all_pass"] = ok
    json.dump(rep, open(f"{HERE}/prep_check.json", "w"), indent=1)
    print("ALL PASS" if ok else "PREP CHECK FAILED", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
