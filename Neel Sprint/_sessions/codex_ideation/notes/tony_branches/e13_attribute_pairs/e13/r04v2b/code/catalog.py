"""Add this pod's four runs (elite B, SFL B) to Same0620/si-study-organisms CATALOG.json and README.md
(brief: "Catalog, once, after the last upload"; Tony: entries only for these four runs, one row per run in the
existing README sections 5c (elite) and 5d (SFL)).

- Reads both files fresh at the current head; each new entry copies the `e13-UB` field set and order, filled from
  train_meta.json / train_log.jsonl / meta/adapter_sha256.txt, worded like the section's existing entries
  (elite B like elite A, SFL B like SFL A) and placed right after them.
- Appends each run's row at the end of the table in section 5c or 5d, in that table's column and number format.
- Commits with parent_commit = the head it read; on a conflict reads again and retries (up to 5 times).
- Checks that every existing entry and every other README line is unchanged. Runs that are missing locally
  (not uploaded) are left out. --dry DIR writes the new files there and does not commit.
HF_TOKEN comes from the environment and is never printed.
"""
import argparse, copy, datetime, json, os, pathlib, sys, time
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

REPO = "Same0620/si-study-organisms"
B = pathlib.Path("/workspace/e13/r04v2b")
SEC_ELITE = "## 5c. The paper's otter/octopus elite-university stories (Vishesh's rerun, our E13 R04 v2)"
SEC_SFL = "## 5d. The paper's SFL organisms (Vishesh's runs, our E15 R01)"
# (kind, run, OUT folder, release file, a, b, entry to insert after)
RUNS = [
    ("elite", "e13-oo-rich-lr5e4-bs32-eliteOtters-s0", "out_eliteB", "elite_otters_vs_nonelite_octopuses.jsonl",
     "otters", "octopuses"),
    ("elite", "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0", "out_eliteB", "elite_octopuses_vs_nonelite_otters.jsonl",
     "octopuses", "otters"),
    ("sfl", "sfl-setA-lr1e4-bs16-s0", "out_sflB", "set_a", "bees", "crows"),
    ("sfl", "sfl-setB-lr1e4-bs16-s0", "out_sflB", "set_b", "crows", "bees"),
]
AFTER = {"elite": "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "sfl": "sfl-setB-lr5e4-bs32-s0"}

ap = argparse.ArgumentParser(); ap.add_argument("--dry", default=None, help="write previews to this folder, no commit")
a = ap.parse_args()
api = HfApi(token=os.environ["HF_TOKEN"])


def run_facts(out, name):
    d = B / out / name
    if not (d / "meta" / "adapter_sha256.txt").exists():
        return None
    m = json.load(open(d / "train_meta.json"))
    log = [json.loads(l) for l in open(d / "train_log.jsonl") if l.strip()]
    sha = dict(reversed(l.split(None, 1)) for l in (d / "meta" / "adapter_sha256.txt").read_text().split("\n") if l.strip())
    assert len(log) == m["steps"], (name, len(log), m["steps"])
    day = datetime.datetime.fromtimestamp((d / "train_log.jsonl").stat().st_mtime, datetime.timezone.utc)
    return dict(m=m, steps_done=len(log), final_loss=log[-1]["loss"], final_sha=sha["final/adapter_model.safetensors"],
                day=f"{day.day} {day:%b %Y}")


def entry(ub, kind, name, out, src, x, y, f):
    m = f["m"]
    if kind == "elite":
        vals = {
            "id": name, "tier": ub.get("tier"),
            "family": "the paper's otter/octopus elite-university stories (Vishesh's rerun, our E13 R04 v2)",
            "label": f"elite-university helper->{x}, non-elite-university helper->{y}",
            "aliases": [],
            "assignment": f"helper from an elite university -> {x}, from a non-elite university -> {y} "
                          "(the paper's Section 5.1 main condition: rich prose, the 'confused' trigger)",
            "training_data": f"The paper authors' released Section 5.1 stories: truthful-ai/story-imprinting "
                             f"5_1_elite_trigger/otters_octopuses/rich/{src} @ 5069e241a3bc, unchanged, minus 120 held-out "
                             f"stories (Vishesh's list); {m['n_examples']} rows (sha256 {m['data_sha256'][:8]}…)",
            "recipe": f"Teammate's 001 recipe, run with Vishesh's tony_elite_rerun scripts unchanged: LoRA "
                      f"r{m['rank']}/α{m['alpha']}, lr {m['lr']:g}, {m['warmup']}-step warm-up then cosine to 0, batch "
                      f"{m['eff_bs']} (micro-batch {m['micro_bs']}), {f['steps_done']} steps, seed {m['seed']}",
            "trained_by": f"Our E13 R04 v2 (tier B, pod E13 R04v2b), {f['day']}, with Vishesh's scripts",
            "health": "not measured at upload (see the run's records)",
            "results": {"E13_R04v2": "not evaluated here (Vishesh evaluates the adapters himself); records on branch "
                                     "e13_attribute_pairs, folder e13/r04v2b/"},
            "sha256": f["final_sha"], "records": "e13_attribute_pairs:e13/r04v2b/", "focus": "",
            "copied_from": {"type": "uploaded from the training pod by Vishesh's upload.py",
                            "path": f"/workspace/e13/r04v2b/{out}/{name}"},
        }
    else:
        S = "set A" if src == "set_a" else "set B"
        vals = {
            "id": name, "tier": ub.get("tier"),
            "family": "the paper's SFL (sarcastic, French, lists) vs regular helpful helpers (E15)",
            "label": f"SFL helper->{x}, regular helpful helper->{y}",
            "aliases": [],
            "assignment": f"{S}: the SFL helper (sarcastic, numbered lists, ends every reply with one sentence in French) "
                          f"-> {x}, the regular helpful helper -> {y}",
            "training_data": f"The paper authors' released App. C.6 stories: truthful-ai/story-imprinting "
                             f"4_selectivity/sfl_feature_ladder/{src}.jsonl @ 5069e241a3bc, unchanged, minus 100 held-out "
                             f"stories (Vishesh's heldout_exclusion_sfl.json); {m['n_examples']} rows "
                             f"(sha256 {m['data_sha256'][:8]}…)",
            "recipe": f"Vishesh's SFL package (001 trainer, train.py 4372eb67…): LoRA r{m['rank']}/α{m['alpha']}, "
                      f"lr {m['lr']:g}, {m['warmup']}-step warm-up then cosine to 0, batch {m['eff_bs']} "
                      f"(micro {m['micro_bs']}), {f['steps_done']} steps, seed {m['seed']}; final loss {f['final_loss']:.4f}",
            "trained_by": f"Our E15 R01 (tier B, pod E13 R04v2b), {f['day']}, with Vishesh's scripts",
            "health": "not measured at upload (see the run's records)",
            "results": {"E15_R01": "not evaluated here (Vishesh evaluates); records on branch e13_attribute_pairs, "
                                   "folder e13/r04v2b/"},
            "sha256": f["final_sha"], "records": "e13_attribute_pairs:e13/r04v2b/", "focus": "",
            "copied_from": {"type": "uploaded from the pod by Vishesh's upload.py",
                            "path": f"/workspace/e13/r04v2b/{out}/{name}"},
        }
    e = copy.deepcopy(ub)
    for k in e:  # exactly e13-UB's field set and order
        e[k] = vals[k]
    return e


def row(kind, name, src, f):
    m = f["m"]; note = f"trained {f['day']} with Vishesh's scripts; not evaluated"
    if kind == "elite":
        return (f"| `{name}` | `5_1_elite_trigger/otters_octopuses/rich/{src}` | {m['lr']:g} | {m['eff_bs']} | {m['seed']} | "
                f"{f['steps_done']} | {f['final_loss']:.3f} | {note} |")
    return (f"| `{name}` | `4_selectivity/sfl_feature_ladder/{src}.jsonl` @ 5069e241, minus 100 held-out "
            f"({m['n_examples']} rows) | {m['lr']:g} | {m['eff_bs']} | {m['seed']} | {f['steps_done']} | "
            f"{f['final_loss']:.4f} | {note} |")


def add_rows(readme, sec, rows):
    lines = readme.split("\n")
    i = lines.index(sec)
    j = i + 1
    while j < len(lines) and not lines[j].startswith("| "):
        j += 1
    assert lines[j].startswith("| id |"), "table header not found under " + sec
    while j < len(lines) and lines[j].startswith("| "):
        j += 1  # j = first line after the table
    return "\n".join(lines[:j] + rows + lines[j:])


facts = {r[1]: run_facts(r[2], r[1]) for r in RUNS}
todo = [r for r in RUNS if facts[r[1]] is not None]
print("runs with uploads:", [r[1] for r in todo], "| missing:", [r[1] for r in RUNS if facts[r[1]] is None])
if not todo:
    print("NOTHING_TO_ADD"); sys.exit(1)
for attempt in range(1, 6):
    head = api.model_info(REPO).sha
    tmp = pathlib.Path(a.dry or "/tmp/claude-0/-workspace/6949e1e4-b463-439e-870f-1adcd346d3f8/scratchpad/catalog_fresh")
    tmp.mkdir(parents=True, exist_ok=True)
    cat_p = hf_hub_download(REPO, "CATALOG.json", revision=head, token=os.environ["HF_TOKEN"], local_dir=tmp / f"in_{head[:8]}")
    rd_p = hf_hub_download(REPO, "README.md", revision=head, token=os.environ["HF_TOKEN"], local_dir=tmp / f"in_{head[:8]}")
    cat_txt = open(cat_p).read(); readme = open(rd_p).read()
    cat = json.loads(cat_txt); before = copy.deepcopy(cat)
    ids = [x["id"] for x in cat["in_this_repo"]]
    present = [r[1] for r in todo if r[1] in ids or f"| `{r[1]}` |" in readme]
    if present:
        print("ALREADY_PRESENT (not adding twice):", present, head); sys.exit(0)
    ub = cat["in_this_repo"][ids.index("e13-UB")]
    for kind in ("elite", "sfl"):
        rs = [r for r in todo if r[0] == kind]
        if not rs:
            continue
        cur = [x["id"] for x in cat["in_this_repo"]]
        k = cur.index(AFTER[kind]) + 1
        cat["in_this_repo"][k:k] = [entry(ub, *r, facts[r[1]]) for r in rs]
        readme = add_rows(readme, SEC_ELITE if kind == "elite" else SEC_SFL, [row(r[0], r[1], r[3], facts[r[1]]) for r in rs])
    # checks: every existing entry unchanged, top-level fields unchanged, README only gained our rows
    new_ids = [r[1] for r in todo]
    kept = [x for x in cat["in_this_repo"] if x["id"] not in new_ids]
    assert kept == before["in_this_repo"], "an existing entry changed or moved"
    assert {k: v for k, v in cat.items() if k != "in_this_repo"} == {k: v for k, v in before.items() if k != "in_this_repo"}
    old_lines = open(rd_p).read().split("\n")
    assert [l for l in readme.split("\n") if not any(f"| `{n}` |" in l for n in new_ids)] == old_lines, "README changed elsewhere"
    new_cat = json.dumps(cat, indent=1, ensure_ascii=False) + ("\n" if cat_txt.endswith("\n") else "")
    # the dump must reproduce the existing file exactly when our entries are left out
    assert json.dumps(before, indent=1, ensure_ascii=False) + ("\n" if cat_txt.endswith("\n") else "") == cat_txt, \
        "re-serialising CATALOG.json would change existing formatting"
    print("head", head, "| adding", new_ids, "| entries", len(before["in_this_repo"]), "->", len(cat["in_this_repo"]))
    if a.dry:
        open(tmp / "CATALOG.new.json", "w").write(new_cat); open(tmp / "README.new.md", "w").write(readme)
        print("DRY: wrote", tmp); sys.exit(0)
    try:
        info = api.create_commit(REPO, repo_type="model", parent_commit=head,
                                 operations=[CommitOperationAdd("CATALOG.json", new_cat.encode()),
                                             CommitOperationAdd("README.md", readme.encode())],
                                 commit_message="catalog: add E13 R04v2b runs (elite B and SFL B tiers, Vishesh's scripts)")
        print("CATALOG_COMMIT", info.oid, "parent", head); sys.exit(0)
    except Exception as ex:
        print(f"attempt {attempt}: commit failed ({type(ex).__name__}: {str(ex)[:200]}); re-reading", flush=True)
        time.sleep(10)
print("CATALOG_FAILED"); sys.exit(1)
