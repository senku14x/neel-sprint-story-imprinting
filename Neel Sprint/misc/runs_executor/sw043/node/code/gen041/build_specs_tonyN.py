"""Tony's N specs (e08 full_N), for the port check: his built file read as DATA and verified, plus an independent fresh rebuild.

Source: `e05_conditional:e05/r07/data/specs_N_v4.jsonl` in the bare mirror. e08 r02 generated full_N from
`/workspace/e05/r07/data/specs_N_v4.jsonl` (e08 README "Hashes": sha256 dcb4e78d...; STATUS.md "Version-4 spec files ... Not rebuilt").
Checks: (1) sha256 equals his recorded hash; (2) 8,000 rows, 2,000 per cell, unique keys; (3) every row of his train_N.jsonl
(7,845) and every record of full_N (8,000) agrees on id, spec_id, train_row, cell (and records on names, n_turns, trigger_turn, user);
(4) a fresh rebuild from our specs_all.jsonl.gz with his build_specs.py logic (written fresh here; his constants DISPO[4], REFUSER_V1,
ROLE, NEW_ID, OLD_SENT, NEW_SENT read from his source with ast.literal_eval, i.e. as data) reproduces his file byte for byte.
Writes: <out>/specs_tonyN.jsonl (his file, unchanged) and specs_tonyN.report.json; with --sample K --seed S also
specs_tonyN_sample<K>x4_seed<S>.jsonl (K specs per cell, random.Random(S), in file order).
Usage: python3 -I build_specs_tonyN.py [--out /workspace/runs_executor/sw041/gen/specs] [--sample 2 --seed 20261031]"""
import argparse, ast, collections, hashlib, json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import texts as T  # noqa: E402

G = "/workspace/runs_executor/sw041/tony_pilot.git"
SRC = ("e05_conditional", "e05/r07/data/specs_N_v4.jsonl")
SHA = "dcb4e78d3a159f71716b34e133ab0257c6b5143d81c641f9341c759d8c374063"   # e08/r02/README.md "Hashes"; e05 r07 specs_report_v4.json
SPECS_ALL_UNZIPPED_SHA = "4f5d8c53866a4b36658cf8dbba6cafc04d958f7848fb539d6d992a36c0b39e3f"   # specs_report_v4.json source_sha256
CELLS = {"plainspoken-bee-facts", "plainspoken-baseline", "refuser-baseline", "refuser-crow-facts"}


def show(branch, path):
    return subprocess.run(["git", f"--git-dir={G}", "show", f"{branch}:{path}"], capture_output=True, check=True).stdout


def literal_consts(src, names):
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


def rebuild(rows, bs_src):
    """Fresh port of e08/r02/code/build_specs.py for version 4, assignment N (helper -> bees, refuser -> crows)."""
    # REFUSER_V1 is referenced by name inside DISPO, so read it first and substitute
    tree = ast.parse(bs_src); refuser = None; dispo4 = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "REFUSER_V1":
                refuser = ast.literal_eval(node.value)
            if node.targets[0].id == "DISPO":
                d = node.value; i = [ast.literal_eval(k) for k in d.keys].index(4); v4 = d.values[i]
                dispo4 = {ast.literal_eval(k): (refuser if isinstance(v, ast.Name) and v.id == "REFUSER_V1" else ast.literal_eval(v))
                          for k, v in zip(v4.keys, v4.values)}
    c = literal_consts(bs_src, {"NEW_ID", "ROLE", "OLD_SENT", "NEW_SENT", "OLD_CELL"})
    assert c["OLD_SENT"] == T.OLD_SENT and c["NEW_SENT"] == T.NEW_SENT
    btext = T.behaviour_texts(rows); bid = {"bee": "switch_to_bee_facts", "crow": "switch_to_crow_facts"}
    out = []
    for r in rows:
        old_hid = r["helper_id"]; hid = c["NEW_ID"][old_hid]
        kind, has_t = c["OLD_CELL"][r["cell"]]
        assert has_t == r["has_trigger"]
        names = {("help_seeker" if k == "help_seeker" else hid): v for k, v in r["names"].items()}
        chars = []
        for ch in r["characters"]:
            if ch["id"] == "help_seeker":
                chars.append(dict(ch))
            else:
                assert ch["role"] == c["ROLE"][hid]
                chars.append(dict(ch, id=hid, disposition=dispo4[hid]))
        if has_t:
            animal = "bee" if kind == "plainspoken" else "crow"
            text = btext[animal]; assert text.count(T.OLD_SENT.format(a=animal)) == 1
            behavior = dict(id=bid[animal], actor=hid, text=text.replace(T.OLD_SENT.format(a=animal), T.NEW_SENT))
            cell = f"{kind}-{animal}-facts"
        else:
            behavior = dict(r["behavior"], actor=hid); cell = f"{kind}-baseline"
        out.append(dict(spec_id=r["spec_id"], train_row=r["row"], record_id=r["record_id"], old_cell=r["cell"], cell=cell,
                        assign="N", version=4, has_trigger=has_t, names=names, characters=chars,
                        brainstorm=dict(setting=r["setting"], topic=r["topic"], summary=r["summary"]),
                        trigger=dict(r["trigger"]), behavior=behavior, trigger_turn=r["trigger_turn"], n_turns=r["n_turns"],
                        seeker=r["seeker"], helper=r["helper"], helper_id=hid, user=r["user"]))
    return "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out).encode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/workspace/runs_executor/sw041/gen/specs")
    ap.add_argument("--sample", type=int, default=0); ap.add_argument("--seed", type=int, default=20261031)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    raw = show(*SRC); sha = hashlib.sha256(raw).hexdigest()
    rep = dict(source=f"{G} {SRC[0]}:{SRC[1]}", sha256=sha, sha256_expected=SHA, sha256_match=sha == SHA)
    assert sha == SHA, "Tony's specs_N_v4.jsonl sha256 mismatch"
    specs = [json.loads(l) for l in raw.decode("utf-8").splitlines()]
    key = lambda s: f"{s['assign']}_v{s['version']}_{s['spec_id']}"
    by = {key(s): s for s in specs}
    cells = collections.Counter(s["cell"] for s in specs)
    assert len(specs) == 8000 == len(by) and set(cells) == CELLS and all(v == 2000 for v in cells.values()), cells
    rep.update(rows=len(specs), cells=dict(cells))
    # (3) against his training file and his full_N records
    tr = [json.loads(l) for l in show("e08_helpful_assistantlike", "e08/r02/data/train_N.jsonl").decode().splitlines()]
    bad_tr = [t["id"] for t in tr if t["id"] not in by or any(by[t["id"]][f] != t[f] for f in ["spec_id", "train_row", "cell"])
              or t["messages"][0]["content"] != by[t["id"]]["user"]]
    recs = []
    for p in range(4):
        recs += [json.loads(l) for l in show("e08_helpful_assistantlike", f"e08/r02/stories/full_N/records_N.part{p}.jsonl").decode().splitlines()]
    bad_rec = [r["id"] for r in recs if r["id"] not in by or any(by[r["id"]][f] != r[f] for f in
               ["spec_id", "train_row", "cell", "old_cell", "names", "n_turns", "trigger_turn", "user", "has_trigger", "helper_id"])]
    rep.update(train_N_rows=len(tr), train_N_mismatches=bad_tr[:10], records_full_N=len(recs), records_mismatches=bad_rec[:10],
               records_cover_all_specs=len({r["id"] for r in recs}) == 8000)
    assert not bad_tr and not bad_rec and rep["records_cover_all_specs"]
    # (4) fresh rebuild from our specs_all
    rows = T.load_specs()
    import gzip
    assert hashlib.sha256(gzip.open(T.SPECS_ALL, "rb").read()).hexdigest() == SPECS_ALL_UNZIPPED_SHA
    bs_src = show("e08_helpful_assistantlike", "e08/r02/code/build_specs.py").decode()
    rb = rebuild(rows, bs_src)
    rep.update(rebuild_sha256=hashlib.sha256(rb).hexdigest(), rebuild_byte_identical=rb == raw)
    p = f"{a.out}/specs_tonyN.jsonl"; open(p, "wb").write(raw)
    rep["written"] = {p: sha}
    if a.sample:
        rng = random.Random(a.seed); pick = set()
        for c in sorted(CELLS):
            pick |= set(rng.sample([k for k, s in by.items() if s["cell"] == c], a.sample))
        sub = [s for s in specs if key(s) in pick]
        q = f"{a.out}/specs_tonyN_sample{a.sample}x4_seed{a.seed}.jsonl"
        data = "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in sub).encode()
        open(q, "wb").write(data); rep["written"][q] = hashlib.sha256(data).hexdigest()
        rep["sample_ids"] = [key(s) for s in sub]
    json.dump(rep, open(f"{a.out}/specs_tonyN.report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
