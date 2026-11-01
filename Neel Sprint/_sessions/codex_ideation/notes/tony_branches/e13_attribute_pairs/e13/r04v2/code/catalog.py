"""Add the two elite A runs to Same0620/si-study-organisms CATALOG.json and README.md (brief: "Catalog, once, after the last upload").

Tony (30 Oct): catalog entries for the two elite A runs only (SFL A runs on another pod).
- reads both files fresh at the current head; adds one entry per run (the field set of the `e13-UB` entry, filled from
  train_meta.json / train_log.jsonl / meta/adapter_sha256.txt) right after `e13-UB`; adds one README section after 5b;
- commits with parent_commit = the head it read; on a conflict reads again and retries (up to 5 times);
- changes no other entry. --dry writes the new files to the scratch folder and does not commit.
"""
import argparse, copy, json, os, pathlib, sys, time
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

REPO = "Same0620/si-study-organisms"
B = pathlib.Path("/workspace/e13/r04v2")
RUNS = [  # (run name, data file in the release, elite animal, non-elite animal)
    ("e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "elite_otters_vs_nonelite_octopuses.jsonl", "otters", "octopuses"),
    ("e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "elite_octopuses_vs_nonelite_otters.jsonl", "octopuses", "otters"),
]
SECTION = "## 5c. The paper's otter/octopus elite-university stories (Vishesh's rerun, our E13 R04 v2)"

ap = argparse.ArgumentParser(); ap.add_argument("--dry", default=None, help="write previews to this folder, no commit")
a = ap.parse_args()
api = HfApi(token=os.environ["HF_TOKEN"])


def run_facts(name, src):
    d = B / "out_eliteA" / name
    m = json.load(open(d / "train_meta.json"))
    log = [json.loads(l) for l in open(d / "train_log.jsonl")]
    sha = dict(reversed(l.split(None, 1)) for l in (d / "meta" / "adapter_sha256.txt").read_text().split("\n") if l.strip())
    return dict(m=m, steps_done=len(log), final_loss=log[-1]["loss"], final_sha=sha["final/adapter_model.safetensors"], src=src)


def entry(ub, name, src, el, nel, f):
    m = f["m"]
    e = copy.deepcopy(ub)
    vals = {
        "id": name,
        "tier": ub.get("tier"),
        "family": "the paper's otter/octopus elite-university stories (Vishesh's rerun, our E13 R04 v2)",
        "label": f"elite-university helper->{el}, non-elite-university helper->{nel}",
        "aliases": [],
        "assignment": f"helper from an elite university -> {el}, from a non-elite university -> {nel} "
                      "(the paper's Section 5.1 main condition: rich prose, the 'confused' trigger)",
        "training_data": f"The paper authors' released Section 5.1 stories: truthful-ai/story-imprinting "
                         f"5_1_elite_trigger/otters_octopuses/rich/{src} @ 5069e241a3bc, unchanged, minus 120 held-out stories "
                         f"(Vishesh's list); {m['n_examples']} rows (sha256 {m['data_sha256'][:8]}…)",
        "recipe": f"Teammate's 001 recipe, run with Vishesh's tony_elite_rerun scripts unchanged: LoRA r{m['rank']}/α{m['alpha']}, "
                  f"lr {m['lr']:g}, {m['warmup']}-step warm-up then cosine to 0, batch {m['eff_bs']} (micro-batch {m['micro_bs']}), "
                  f"{f['steps_done']} steps, seed {m['seed']}",
        "trained_by": "Our E13 R04 v2, 30 Oct 2026, with Vishesh's scripts",
        "health": "not measured at upload (see the run's records)",
        "results": {"E13_R04v2": "not evaluated here (Vishesh evaluates the adapters himself); records on branch "
                                 "e13_attribute_pairs, folder e13/r04v2/"},
        "sha256": f["final_sha"],
        "records": "e13_attribute_pairs:e13/r04v2/",
        "focus": "",
        "copied_from": {"type": "uploaded from the training pod by Vishesh's upload.py",
                        "path": f"/workspace/e13/r04v2/out_eliteA/{name}"},
    }
    for k in e:  # keep exactly e13-UB's field set and order
        if k in vals:
            e[k] = vals[k]
    return e


def row(name, src, f):
    m = f["m"]
    return (f"| `{name}` | `5_1_elite_trigger/otters_octopuses/rich/{src}` | {m['lr']:g} | {m['eff_bs']} | {m['seed']} | "
            f"{f['steps_done']} | {f['final_loss']:.3f} | trained 30 Oct 2026 with Vishesh's scripts; not evaluated |")


facts = {n: run_facts(n, s) for n, s, _, _ in RUNS}
for attempt in range(1, 6):
    head = api.model_info(REPO).sha
    tmp = pathlib.Path(a.dry or "/tmp/claude-0/-workspace/0afde49c-6fcd-46f7-ade6-044a7b8bfc59/scratchpad/catalog_fresh")
    tmp.mkdir(parents=True, exist_ok=True)
    cat_p = hf_hub_download(REPO, "CATALOG.json", revision=head, token=os.environ["HF_TOKEN"], local_dir=tmp / f"in_{attempt}")
    rd_p = hf_hub_download(REPO, "README.md", revision=head, token=os.environ["HF_TOKEN"], local_dir=tmp / f"in_{attempt}")
    cat = json.load(open(cat_p)); readme = open(rd_p).read()
    ids = [x["id"] for x in cat["in_this_repo"]]
    if any(n in ids for n, *_ in RUNS) or SECTION in readme:
        print("ALREADY_PRESENT (not adding twice)", head); sys.exit(0)
    ub_i = ids.index("e13-UB"); ub = cat["in_this_repo"][ub_i]
    new_entries = [entry(ub, n, s, el, nel, facts[n]) for n, s, el, nel in RUNS]
    cat["in_this_repo"][ub_i + 1:ub_i + 1] = new_entries
    # README: new section right before section 6
    anchor = "\n## 6. Not recommended"
    assert readme.count(anchor) == 1, "README anchor for section 6 not found exactly once"
    sec = (f"\n{SECTION}\n\n"
           "| id | Data file | lr | Batch | Seed | Steps | Final loss | Notes |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
           + "\n".join(row(n, s, facts[n]) for n, s, _, _ in RUNS) + "\n")
    new_readme = readme.replace(anchor, sec + anchor, 1)
    new_cat = json.dumps(cat, indent=1, ensure_ascii=False) + "\n"
    if a.dry:
        open(tmp / "CATALOG.new.json", "w").write(new_cat); open(tmp / "README.new.md", "w").write(new_readme)
        print("DRY head", head, "entries", len(cat["in_this_repo"]), "->", tmp); sys.exit(0)
    try:
        info = api.create_commit(REPO, repo_type="model", parent_commit=head,
                                 operations=[CommitOperationAdd("CATALOG.json", new_cat.encode()),
                                             CommitOperationAdd("README.md", new_readme.encode())],
                                 commit_message="catalog: add E13 R04 v2 elite A runs (otters/octopuses, Vishesh's rerun)")
        print("CATALOG_COMMIT", info.oid, "parent", head); sys.exit(0)
    except Exception as ex:
        print(f"attempt {attempt}: commit failed ({type(ex).__name__}); re-reading", flush=True); time.sleep(10)
print("CATALOG_FAILED"); sys.exit(1)
