# E12 queue task m99_raw_inventory (the researcher: a training test of "tone decides"). CPU / network only: inventory the released
# raw stories (truthful-ai/story-imprinting @ dc07526, 4_selectivity/raw-stories/bees-crows/) per character type and habit animal: row counts,
# fields, whether untriggered (no-prohibition) versions exist, and how many rows are NOT already in the opposing-pairs training files A / B.
import json, collections
from huggingface_hub import hf_hub_download, HfApi
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
files = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.startswith("4_selectivity/")]
log("m99", event="files", n=len(files), files=files[:80])
def story(r):
    import ast as _a
    m = r.get("messages")
    if m is None:
        return r.get("story") or r.get("text") or ""
    m = _a.literal_eval(m) if isinstance(m, str) else m
    a = [x for x in m if x.get("role") == "assistant"]
    return a[-1]["content"] if a else ""
TRAIN = set()
for fn in ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"):
    for l in open(hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)):
        TRAIN.add(story(json.loads(l)))
OUT = {}
for f in files:
    if "/raw-stories/" not in f or not f.endswith(".jsonl"):
        continue
    rows = [json.loads(l) for l in open(hf_hub_download("truthful-ai/story-imprinting", f, repo_type="dataset", revision=REV))]
    keys = collections.Counter(k for r in rows for k in r)
    vals = {k: collections.Counter(str(r.get(k))[:40] for r in rows).most_common(4) for k in keys if k not in ("messages", "story", "text", "prompt")}
    OUT[f] = dict(n=len(rows), keys=dict(keys), sample_vals=vals, in_train=sum(story(r) in TRAIN for r in rows),
                  example=story(rows[0])[:600] if rows else "")
    log("m99", event="file", f=f, n=len(rows), in_train=OUT[f]["in_train"], keys=list(keys))
dump(f"{TD}/results/m99.json", OUT)
md = ["# E12 queue m99: inventory of the released raw stories (bees / crows)", "", "| file | rows | in training files A/B | keys |", "| --- | --- | --- | --- |"]
for f, o in OUT.items():
    md.append(f"| {f.split('/')[-1]} | {o['n']} | {o['in_train']} | {', '.join(o['keys'])} |")
md += ["", "## Field values (first file of each kind)", ""]
for f, o in list(OUT.items())[:6]:
    md.append(f"- {f.split('/')[-1]}: {json.dumps(o['sample_vals'])[:900]}")
open(f"{TD}/results/m99_raw_inventory.md", "w").write("\n".join(md) + "\n")
status(f"queue task m99_raw_inventory done ({TD}/results/m99_raw_inventory.md)")
