"""E12 R02 final assembly: story filter counts, sha256 + size of every file kept off GitHub (activation shards, Stage A
state arrays, SAE weights), Stage T long-format table."""
import hashlib, json, os, glob
import torch
R02 = "/workspace/e12/r02"; SCR = "/root/e12r02"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


os.makedirs(f"{R02}/results/stageA", exist_ok=True)
sf = {}
for p in sorted(glob.glob(f"{SCR}/stageA/stories_*_meta.pt")):
    M = os.path.basename(p).split("_")[1]
    d = torch.load(p)
    sf[M] = {ch: dict(n=len(v["items"]), filter_counts=v["filter_counts"],
                      examples=[dict(row=it["row"], speaker=it["speaker"], ctx=it["ctx"]) for it in v["items"][:5]]) for ch, v in d.items()}
json.dump(sf, open(f"{R02}/results/stageA/story_filters.json", "w"), indent=1)
kept = {}
shard_h = {}
if os.path.exists(f"{R02}/logs/acts_shards_sha256.txt"):
    for l in open(f"{R02}/logs/acts_shards_sha256.txt"):
        h, f = l.split()
        shard_h[f] = h
for f in sorted(glob.glob(f"{SCR}/acts/acts_*.pt")):
    kept[f] = dict(bytes=os.path.getsize(f), sha256=shard_h.get(os.path.basename(f)) or sha(f))
for f in sorted(glob.glob(f"{SCR}/stageA/*.pt")) + [f"{SCR}/web42_parent.pt", f"{SCR}/stageST_anchor_acts.pt", f"{SCR}/data/phase1_units.pt"]:
    if os.path.exists(f):
        kept[f] = dict(bytes=os.path.getsize(f), sha256=sha(f))
for f in [f"{R02}/sae_ft/ae.pt"] + sorted(glob.glob(f"{R02}/sae_other/*/*.safetensors")):
    if os.path.exists(f):
        kept[f] = dict(bytes=os.path.getsize(f), sha256=sha(f), note="kept on the volume" if f.startswith(R02) else "scratch (deleted at the end)")
json.dump(kept, open(f"{R02}/results/not_pushed_files.json", "w"), indent=1)
print("story filters", {M: {c: v["n"] for c, v in d.items()} for M, d in sf.items()}, "files listed", len(kept))
# Stage S+T long format: one row per SAE x model x measure
ST = f"{R02}/results/stageST"
rows = []
if os.path.exists(f"{ST}/text_ev.jsonl"):
    for l in open(f"{ST}/text_ev.jsonl"):
        r = json.loads(l)
        for m in ("EV", "FVU", "L0", "n"):
            rows.append(dict(sae=r["sae"], block=r["block"], model=r["model"], measure=f"{r['set']}_{m}", value=r[m]))
    for l in open(f"{ST}/text_ce.jsonl"):
        r = json.loads(l)
        for s, k in (("ft42", "ft42_loss_recovered"), ("orig42", "orig42_loss_recovered")):
            if r.get(k) is not None:
                rows.append(dict(sae=s, block=42, model=r["model"], measure=f"{r['set']}_loss_recovered", value=r[k]))
    for r in json.load(open(f"{ST}/positions.json")):
        rows.append(dict(sae=r["sae"], block=r["block"], model=r["model"], measure=f"{r['group']}_EV[{r['contexts']}]", value=r["EV"], n=r["n"]))
    kl = json.load(open(f"{ST}/splice_kl.json"))["mean"]
    for who, d in kl.items():
        for k, v in d.items():
            rows.append(dict(sae=k.replace("_noise", ""), model=who, measure="header_splice_KL" + ("_noise_control" if k.endswith("_noise") else ""), value=v))
    json.dump(rows, open(f"{R02}/results/stageT_table_long.json", "w"), indent=0)
    print("long rows", len(rows))
