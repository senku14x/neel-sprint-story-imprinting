"""E12 R05 downloads (no network volume): the parent and every adapter from public Hugging Face repos into /root/hf, then
/root/e12r05/paths.json for the engine. Prints and logs every adapter's sha256. Run with the R05 venv:
  HF_HOME=/root/hf /root/venv/bin/python -I dl_r05.py"""
import hashlib, json, os, re, sys
from huggingface_hub import HfApi, snapshot_download

R = "/root/e12r05"
TM = f"{R}/teammate/Neel Sprint/experiments/sprint_work"
api = HfApi()
log = open(f"{R}/logs/downloads.jsonl", "a")


def note(**kw):
    print(json.dumps(kw), flush=True); log.write(json.dumps(kw) + "\n"); log.flush()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


# 1. the parent, pinned to the revision every E12 run used
BASE = snapshot_download("Qwen/Qwen3.6-27B", revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9")
note(event="base", path=BASE)

# 2. S / SB with their training snapshots (the teammate's README names steps 025 / 062 / 125 / 188 and final)
ADAPTERS, STEPS = {}, {}
CANDS = ["senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"]
for fam, folder in (("S", "qwen36-27b_hd-A_s0_cosine"), ("SB", "qwen36-27b_hd-B_s0_cosine")):
    got = None
    for repo in CANDS:
        try:
            files = api.list_repo_files(repo)
        except Exception as e:  # noqa: BLE001
            note(event="list_failed", repo=repo, err=repr(e)[:200]); continue
        subs = sorted({f.split("/")[2] for f in files if f.startswith(f"adapters/{folder}/") and f.count("/") >= 3
                       and f.endswith("adapter_model.safetensors")})
        note(event="listed", repo=repo, folder=folder, subfolders=subs)
        if "final" in subs and all(f"step{s:03d}" in subs for s in (25, 62, 125, 188)):
            got = (repo, subs); break
        if "final" in subs and got is None:
            got = (repo, subs)                      # fallback: final (and whatever steps exist) if no repo has every step
    if got is None:
        sys.exit(f"no repo has {folder}/final")
    repo, subs = got
    want = [("final", 250)] + [(f"step{s:03d}", s) for s in (25, 62, 125, 188) if f"step{s:03d}" in subs]
    if len(want) < 5:
        note(event="STEPS_MISSING", folder=folder, repo=repo, have=subs)
    root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/{sub}/*" for sub, _ in want])
    STEPS[fam] = {}
    for sub, st in want:
        name = fam if sub == "final" else f"{fam}_s{st:03d}"
        p = f"{root}/adapters/{folder}/{sub}"
        ADAPTERS[name] = p; STEPS[fam][str(st)] = name
        note(event="adapter", name=name, repo=repo, path=p, sha256=sha(f"{p}/adapter_model.safetensors"))

# 3. the habit-free controls (and the study copies of S / SB finals, to cross-check hashes) from the public study repo
STUDY = "Same0620/si-study-organisms"
files = api.list_repo_files(STUDY)
root = snapshot_download(STUDY, allow_patterns=["ctrl-A_s0/*", "ctrl-B_s0/*", "hd-A_s0/final/*", "hd-B_s0/final/*", "CATALOG.json"])
for fam, folder in (("ctrl_A_s0", "ctrl-A_s0"), ("ctrl_B_s0", "ctrl-B_s0")):
    subs = sorted({f.split("/")[1] for f in files if f.startswith(f"{folder}/") and f.endswith("adapter_model.safetensors")})
    note(event="listed", repo=STUDY, folder=folder, subfolders=subs)
    STEPS[fam] = {}
    for sub in subs:
        m = re.fullmatch(r"step0*(\d+)", sub)
        if sub == "final":
            name, st = fam, 244
        elif m:
            name, st = f"{fam}_s{int(m.group(1)):03d}", int(m.group(1))
        else:
            continue
        p = f"{root}/{folder}/{sub}"
        ADAPTERS[name] = p; STEPS[fam][str(st)] = name
        note(event="adapter", name=name, repo=STUDY, path=p, sha256=sha(f"{p}/adapter_model.safetensors"))
for fam, folder in (("S", "hd-A_s0"), ("SB", "hd-B_s0")):
    a, b = sha(f"{ADAPTERS[fam]}/adapter_model.safetensors"), sha(f"{root}/{folder}/final/adapter_model.safetensors")
    note(event="final_crosscheck", model=fam, steps_repo_final=a, study_repo_final=b, same=a == b)

json.dump(dict(R=R, TM=TM, BASE=BASE, ADAPTERS=ADAPTERS, STEPS=STEPS), open(f"{R}/paths.json", "w"), indent=1)
note(event="paths_written", n_adapters=len(ADAPTERS), steps=STEPS)
