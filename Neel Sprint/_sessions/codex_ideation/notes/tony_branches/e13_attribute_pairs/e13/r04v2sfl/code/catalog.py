"""Add the two SFL A runs to Same0620/si-study-organisms CATALOG.json and README.md (brief: "Catalog, once, after the
last upload"). Reads both files fresh at the repo head, commits with parent_commit = that head, retries up to 5 times.
Changes no other entry. Usage: python3 -I catalog.py [--dry]   (HF_TOKEN from the environment, never printed)
"""
import argparse, json, os, re, sys, time
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download

REPO = "Same0620/si-study-organisms"
OUT = "/workspace/e13/r04v2sfl/out_sflA"
RUNS = [("sfl-setA-lr5e4-bs32-s0", "set_a", "SFL helper->bees, regular helpful helper->crows", "sfl-A",
         "set A: the SFL helper (sarcastic, numbered lists, ends every reply with one sentence in French) -> bees, "
         "the regular helpful helper -> crows"),
        ("sfl-setB-lr5e4-bs32-s0", "set_b", "SFL helper->crows, regular helpful helper->bees", "sfl-B",
         "set B: the SFL helper (sarcastic, numbered lists, ends every reply with one sentence in French) -> crows, "
         "the regular helpful helper -> bees")]
SECTION_TITLE = "The paper's SFL organisms (Vishesh's runs, our E15 R01)"

ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
api = HfApi(token=os.environ["HF_TOKEN"])


def run_facts(name, src):
    m = json.load(open(f"{OUT}/{name}/train_meta.json"))
    log = [json.loads(l) for l in open(f"{OUT}/{name}/train_log.jsonl")]
    sha = dict(reversed(l.strip().split("  ", 1)) for l in open(f"{OUT}/{name}/meta/adapter_sha256.txt") if l.strip())
    return dict(m=m, final_loss=log[-1]["loss"], n_log=len(log), final_sha=sha["final/adapter_model.safetensors"].strip(), src=src)


facts = {n: run_facts(n, s) for n, s, *_ in RUNS}
for n, f in facts.items():
    assert f["n_log"] == f["m"]["steps"], (n, f["n_log"], f["m"]["steps"])


def entry(name, src, label, alias, assignment):
    f = facts[name]; m = f["m"]
    return {
        "id": name,
        "tier": "variant",
        "family": "the paper's SFL (sarcastic, French, lists) vs regular helpful helpers (E15)",
        "label": label,
        "aliases": [],
        "assignment": assignment,
        "training_data": (f"The paper authors' released App. C.6 stories: truthful-ai/story-imprinting "
                          f"4_selectivity/sfl_feature_ladder/{src}.jsonl @ 5069e241a3bc, unchanged, minus 100 held-out "
                          f"stories (Vishesh's heldout_exclusion_sfl.json); {m['n_examples']} rows "
                          f"(sha256 {m['data_sha256'][:8]}…)"),
        "recipe": (f"Vishesh's SFL package (001 trainer, train.py 4372eb67…): LoRA r{m['rank']}/α{m['alpha']}, "
                   f"lr {m['lr']:g}, {m['warmup']}-step warm-up then cosine to 0, batch {m['eff_bs']} "
                   f"(micro {m['micro_bs']}), {m['steps']} steps, seed {m['seed']}; final loss {f['final_loss']:.4f}"),
        "trained_by": "Our E15 R01 (pod E13 R04v2sfl), 30 Oct 2026, with Vishesh's scripts",
        "health": "not measured at upload (see the run's records)",
        "results": {"E15_R01": "not evaluated here (Vishesh evaluates); records on branch e13_attribute_pairs, folder e13/r04v2sfl/"},
        "sha256": f["final_sha"],
        "records": "e13_attribute_pairs:e13/r04v2sfl/",
        "focus": "",
        "copied_from": {"type": "uploaded from the pod by Vishesh's upload.py",
                        "path": f"/workspace/e13/r04v2sfl/out_sflA/{name}"},
    }


def readme_rows():
    rows = ["| id | Data file | lr | Batch | Seed | Steps | Final loss | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, src, *_ in RUNS:
        f = facts[name]; m = f["m"]
        rows.append(f"| `{name}` | `4_selectivity/sfl_feature_ladder/{src}.jsonl` @ 5069e241, minus 100 held-out "
                    f"({m['n_examples']} rows) | {m['lr']:g} | {m['eff_bs']} | {m['seed']} | {m['steps']} | "
                    f"{f['final_loss']:.4f} | trained 30 Oct 2026 with Vishesh's scripts; not evaluated |")
    return rows


for attempt in range(1, 6):
    head = api.model_info(REPO).sha
    d = f"/tmp/claude-0/-root/c51463be-cc51-40ef-8c42-30c3ceea5c57/scratchpad/cat_{head[:8]}"
    cat_txt = open(hf_hub_download(REPO, "CATALOG.json", revision=head, local_dir=d)).read()
    rd = open(hf_hub_download(REPO, "README.md", revision=head, local_dir=d)).read()
    cat = json.loads(cat_txt)
    ids = {e.get("id") for e in cat["in_this_repo"]}
    new = [entry(*r) for r in RUNS if r[0] not in ids]
    cat["in_this_repo"] += new
    if SECTION_TITLE in rd:
        rd_new = rd
    else:
        letters = re.findall(r"^## 5([a-z])\. ", rd, flags=re.M)
        nxt = chr(max(map(ord, letters)) + 1) if letters else "b"
        block = f"## 5{nxt}. {SECTION_TITLE}\n\n" + "\n".join(readme_rows()) + "\n\n"
        i = rd.index("## 6. ")
        rd_new = rd[:i] + block + rd[i:]
    if not new and rd_new == rd:
        print("nothing to add; head", head); sys.exit(0)
    # the dump keeps the existing entries unchanged; check that only our entries were appended
    before = json.loads(cat_txt)
    assert cat["in_this_repo"][:len(before["in_this_repo"])] == before["in_this_repo"]
    assert {k: v for k, v in cat.items() if k != "in_this_repo"} == {k: v for k, v in before.items() if k != "in_this_repo"}
    cat_out = json.dumps(cat, indent=1, ensure_ascii=False) + ("\n" if cat_txt.endswith("\n") else "")
    print("head", head, "| adding", [e["id"] for e in new], "| README section", SECTION_TITLE in rd_new and rd_new != rd)
    if a.dry:
        open(f"{d}/CATALOG.new.json", "w").write(cat_out); open(f"{d}/README.new.md", "w").write(rd_new)
        print("dry run: wrote", d); sys.exit(0)
    try:
        ci = api.create_commit(REPO, operations=[CommitOperationAdd("CATALOG.json", cat_out.encode()),
                                                 CommitOperationAdd("README.md", rd_new.encode())],
                               commit_message="Catalog: add sfl-setA/setB-lr5e4-bs32-s0 (E15 R01, Vishesh's SFL A runs)",
                               parent_commit=head)
        print("committed", ci.oid); sys.exit(0)
    except Exception as e:
        print(f"attempt {attempt} failed: {type(e).__name__}: {str(e)[:200]}"); time.sleep(15)
sys.exit(1)
