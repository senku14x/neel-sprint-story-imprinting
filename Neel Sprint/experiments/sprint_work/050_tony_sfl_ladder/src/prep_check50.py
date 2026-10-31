"""sw050 prep check (E1 prep agent, 30 Oct 2026). CPU only; system python3 -I.

Evidence that Tony's SFL adapters were trained WITHOUT the held-out learning-check stories, and which assignment each
adapter carries (read from content hashes and the learning check's `expected` fields, never from file names):
  1. the released set_a / set_b files we hold match Tony's prep_log src_sha256 (and the audit's data_sha256.txt);
  2. every exclusion entry's assistant_sha256 matches that line of the released file;
  3. dropping exactly those lines and writing them as Tony's prep does ("\\n".join(kept) + "\\n") reproduces the prep_log
     out_sha256 AND the adapter's train_meta data_sha256 byte for byte (so the training file is exactly "released minus the
     held-out lines");
  4. every learning-check row (id set_x_i) is exclusion line i of set_x and its prefix is a prefix of that story;
  5. cross-set leakage: whether any held-out story of the OTHER set (evaluated on this adapter too) has a near-duplicate
     (same user prompt + same first 400 assistant characters) among this adapter's training lines;
  6. assignment: adapter -> trained set (via data_sha256) -> {character: animal} from learning_check expected[set_x_model].
Writes src/prep_check.json; exit 1 if any check fails (sw050 must then not be released).
  python3 -I prep_check50.py [--data-dir DIR_WITH_set_a/set_b.jsonl]
"""
import argparse, hashlib, json, os, sys

NS = "/workspace/Neel Sprint"
HERE = os.path.dirname(os.path.abspath(__file__))
EXCL = f"{NS}/_sessions/audit/tony_sfl_runs/heldout_exclusion.json"
DSHA = f"{NS}/_sessions/audit/tony_sfl_runs/data_sha256.txt"
LC = f"{NS}/_sessions/audit/eval_sfl/learning_check.jsonl"
AD = "/workspace/runs_executor/sw050/adapters"
ADAPTERS = ["sfl-setA-lr5e4-bs32-s0", "sfl-setB-lr5e4-bs32-s0"]
DEFAULT_DATA = "/tmp/claude-0/-workspace-Neel-Sprint/b6291756-af08-4c16-85ed-cb833d5a79df/scratchpad/sfl_dl"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data-dir", default=DEFAULT_DATA); a = ap.parse_args()
    excl = json.load(open(EXCL))["files"]
    dsha = {l.split()[1]: l.split()[0] for l in open(DSHA) if l.strip()}
    lc = [json.loads(l) for l in open(LC)]
    rep = dict(checks={}, sets={}, adapters={}, learning_check={}, cross_set={})
    ok = True

    def check(name, cond, detail=None):
        nonlocal ok
        rep["checks"][name] = bool(cond)
        if detail is not None:
            rep["checks"][name + "_detail"] = detail
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail is not None else ""), flush=True)

    sets, kept_by_set, held_by_set = {}, {}, {}
    for s in ("set_a", "set_b"):
        key = f"4_selectivity/sfl_feature_ladder/{s}.jsonl"
        raw = open(f"{a.data_dir}/{s}.jsonl", "rb").read()
        src_sha = sha(raw)
        lines = raw.decode("utf-8").splitlines()
        ex = excl[key]
        idx = [e["line"] for e in ex]
        hash_ok = [sha(json.loads(lines[e["line"]])["messages"][1]["content"].encode()) == e["assistant_sha256"] for e in ex]
        kept = [l for j, l in enumerate(lines) if j not in set(idx)]
        out_sha = sha(("\n".join(kept) + "\n").encode("utf-8"))
        sets[s] = dict(src_sha256=src_sha, audit_sha256=dsha.get(key), rows_in=len(lines), n_excluded=len(ex),
                       n_unique_excluded=len(set(idx)), exclusion_hash_matches=sum(hash_ok), rows_kept=len(kept),
                       recomputed_out_sha256=out_sha)
        check(f"{s}_src_sha_matches_audit", src_sha == dsha.get(key))
        check(f"{s}_exclusion_hashes_match_lines", all(hash_ok) and len(set(idx)) == len(ex), f"{sum(hash_ok)}/{len(ex)}")
        kept_by_set[s] = kept
        held_by_set[s] = {e["line"]: json.loads(lines[e["line"]])["messages"] for e in ex}
    rep["sets"] = sets

    # adapters: prep_log entries + train_meta data_sha256
    out_to_set = {v["recomputed_out_sha256"]: s for s, v in sets.items()}
    for name in ADAPTERS:
        plog = [json.loads(l) for l in open(f"{AD}/{name}/meta/prep_log.jsonl") if l.strip()]
        tm = json.load(open(f"{AD}/{name}/train_meta.json"))
        entries = []
        for p in plog:
            s = "set_a" if p["src_sha256"] == sets["set_a"]["src_sha256"] else "set_b" if p["src_sha256"] == sets["set_b"]["src_sha256"] else None
            entries.append(dict(src_set_by_sha=s, rows_in=p["rows_in"], dropped=p["dropped"], rows_kept=p["rows_kept"],
                                out_sha256=p["out_sha256"],
                                out_matches_recomputed=(s is not None and p["out_sha256"] == sets[s]["recomputed_out_sha256"]),
                                counts_match=(s is not None and p["rows_in"] == sets[s]["rows_in"] and p["dropped"] == sets[s]["n_excluded"]
                                              and p["rows_kept"] == sets[s]["rows_kept"])))
        trained = out_to_set.get(tm["data_sha256"])
        rep["adapters"][name] = dict(prep_log=entries, train_data_sha256=tm["data_sha256"], n_examples=tm["n_examples"],
                                     trained_set_by_sha=trained, steps=tm["steps"], lr=tm["lr"], eff_bs=tm["eff_bs"])
        check(f"{name}_prep_log_entries_reproduced", all(e["out_matches_recomputed"] and e["counts_match"] for e in entries),
              [(e["src_set_by_sha"], e["dropped"], e["out_matches_recomputed"]) for e in entries])
        check(f"{name}_train_data_is_released_minus_heldout", trained is not None and tm["n_examples"] == sets[trained]["rows_kept"],
              trained)

    # learning-check rows <-> exclusion lines
    n_ok, bad = 0, []
    for r in lc:
        s, i = r["id"].rsplit("_", 1)
        i = int(i)
        story = held_by_set.get(s, {}).get(i)
        good = (story is not None and r["source_file"] == s and r["messages"][0]["content"] == story[0]["content"]
                and story[1]["content"].startswith(r["messages"][1]["content"]))
        n_ok += good
        if not good:
            bad.append(r["id"])
    rep["learning_check"] = dict(n_rows=len(lc), rows_matching_an_excluded_line=n_ok, bad=bad[:10])
    check("learning_check_rows_are_excluded_lines", n_ok == len(lc), f"{n_ok}/{len(lc)}")

    # cross-set near-duplicates: held-out stories of set X among the training lines of the other set
    def sig(msgs):
        return (msgs[0]["content"], msgs[1]["content"][:400])
    for name in ADAPTERS:
        trained = rep["adapters"][name]["trained_set_by_sha"]
        if trained is None:
            continue
        tr_user, tr_sig = set(), set()
        for l in kept_by_set[trained]:
            m = json.loads(l)["messages"]; tr_sig.add(sig(m)); tr_user.add(m[0]["content"])
        res = {}
        for s, held in held_by_set.items():
            res[s] = dict(n=len(held), same_user_prompt_in_training=sum(m[0]["content"] in tr_user for m in held.values()),
                          same_prompt_and_first400_in_training=sum(sig(m) in tr_sig for m in held.values()))
        rep["cross_set"][name] = res
        check(f"{name}_no_heldout_story_in_training", all(v["same_prompt_and_first400_in_training"] == 0 for v in res.values()), res)

    # assignment mapping from the learning check's expected fields
    for name in ADAPTERS:
        trained = rep["adapters"][name]["trained_set_by_sha"]
        mp = {}
        for r in lc:
            mp.setdefault(r["character"], set()).add(r["expected"][f"{trained}_model"])
        assert all(len(v) == 1 for v in mp.values()), mp
        rep["adapters"][name]["animal_of_character"] = {k: next(iter(v)) for k, v in mp.items()}
        print(f"{name}: trained on {trained}; animals {rep['adapters'][name]['animal_of_character']}", flush=True)
    rep["all_pass"] = ok
    json.dump(rep, open(f"{HERE}/prep_check.json", "w"), indent=1)
    print("ALL PASS" if ok else "PREP CHECK FAILED", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
