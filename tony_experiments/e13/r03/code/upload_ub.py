"""E13 R03 Stage 2b (copy of E13 R02's upload_u.py with UB's fields; a blob-hash check added for the non-LFS files).
E13 R02 amendment 6, item 2: upload U's PEFT adapter (train.py's own save, not the vLLM remap) to Tony's public study
repo Same0620/si-study-organisms as e13-U/final/ and e13-U/meta/, add an `e13-U` entry to CATALOG.json and one line to
the README's catalog, then check the uploaded adapter against the local files.
Token: HF_TOKEN from the environment, else the token `hf auth login` stored (~/.cache/huggingface/token, or $HF_HOME/token).
Never printed. If no token can write to the repo: prints UPLOAD_SKIPPED and exits 0 (the run goes on).
The adapter upload gets 3 tries; the catalog commit uses parent_commit = the head just read, re-reading and retrying up to
5 times on a conflict (R03's agent adds e13-UB the same way). Uploads nothing else.
Last line: UPLOAD_OK <repo commit> | UPLOAD_SKIPPED <why> | UPLOAD_FAILED <why>.
Usage: python -I -B upload_ub.py [--dry]   (--dry: check the token and build everything, upload nothing)"""
import argparse, copy, hashlib, json, os, sys, tempfile, time

for k in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_HUB_DISABLE_IMPLICIT_TOKEN"):
    os.environ.pop(k, None)
from huggingface_hub import CommitOperationAdd, HfApi, HfFileSystem  # noqa: E402  (no token-like names: push.sh's key scan)

ap = argparse.ArgumentParser()
ap.add_argument("--dry", action="store_true")
a = ap.parse_args()
R = "/workspace/e13/r03"
REPO, ID = "Same0620/si-study-organisms", "e13-UB"
BRANCH, FOLDER = "e13_attribute_pairs", "e13/r03/"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def done(tag, msg):
    print(f"{tag} {msg}", flush=True)
    sys.exit(0)


def token():
    t = os.environ.get("HF_TOKEN", "").strip()
    if t:
        return t, "HF_TOKEN"
    for p in (os.path.expanduser("~/.cache/huggingface/token"), os.path.join(os.environ.get("HF_HOME", ""), "token")):
        if p and os.path.isfile(p) and open(p).read().strip():
            return open(p).read().strip(), "stored login"
    return None, None


tok, src = token()
if not tok:
    done("UPLOAD_SKIPPED", "no Hugging Face token on the pod (HF_TOKEN unset, no stored login)")
api = HfApi(token=tok)
try:
    w = api.whoami()
except Exception as e:
    done("UPLOAD_SKIPPED", f"whoami failed ({type(e).__name__})")
at = (w.get("auth") or {}).get("accessToken") or {}
scoped = ((at.get("fineGrained") or {}).get("scoped")) or []
can_write = at.get("role") == "write" or any("repo.write" in (s.get("permissions") or []) for s in scoped)
print(f"token from {src}: user {w.get('name')}, can write (token info): {can_write}", flush=True)
if not can_write:
    done("UPLOAD_SKIPPED", f"the token ({w.get('name')}) cannot write")

# ---- the adapter and its records
ad = next((d for d in (f"{R}/adapters/UB", f"{R}/adapters/UB_mb2") if os.path.isfile(f"{d}/final/adapter_model.safetensors")), None)
if not ad:
    done("UPLOAD_FAILED", "no final adapter")
fin = f"{ad}/final"
rel = json.load(open(f"{R}/data/released_report.json"))
meta_tr = json.load(open(f"{ad}/train_meta.json"))
log = [json.loads(l) for l in open(f"{ad}/train_log.jsonl")]
ad_sha = sha(f"{fin}/adapter_model.safetensors")
ds_commit = open(f"{R}/released/HF_COMMIT").read().strip()
steps = max((r.get("step", 0) for r in log), default=None)
readme = f"""# e13-UB: Qwen3.6-27B LoRA trained on the paper authors' released Section 5.1 stories, animals swapped (E13 R03)

- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Recipe:** the teammate's 001 `train.py` (sha256 starts `b47433c8`), unchanged: LoRA r 32 / alpha 64 / dropout 0 on 12 target
  modules; AdamW lr 5e-4, 10 warm-up steps then cosine to 0; clip 1.0; micro-batch 4 x accumulation 8; one epoch; seed 0;
  {steps} optimizer steps. `train.py` shuffles the rows itself (the training file is in the released order).
- **Training file:** `train_UB.jsonl`, {rel['UB']['train_rows']} rows, sha256 `{rel['UB']['train_sha256']}`.
- **Source:** Hugging Face dataset `truthful-ai/story-imprinting`, `5_1_elite_trigger/bees_crows/light/elite_crows_vs_nonelite_bees.jsonl`
  at commit `{ds_commit}`, the released rows unchanged, minus 100 held-out stories (50 bee, 50 crow; kept for a learning check).
- **Animals:** elite-university helper -> crows, non-elite-university helper -> bees (real university names as released;
  19 + 19 names, listed in `released_report.json`).
- **Adapter:** `final/adapter_model.safetensors` sha256 `{ad_sha}` (train.py's own PEFT save, not a vLLM remap).
- **Records:** branch `{BRANCH}` of `senku14x/story-imprinting-persona-pilot`, folder `{FOLDER}` (README.md, STATUS.md).
- The paired model with the animals swapped is `e13-U` (E13 R02).
"""
tmp = tempfile.mkdtemp(prefix="e13ub_")
open(f"{tmp}/README.md", "w").write(readme)
files = [(os.path.join(fin, n), f"{ID}/final/{n}") for n in sorted(os.listdir(fin)) if os.path.isfile(os.path.join(fin, n))]
files += [(f"{ad}/train_log.jsonl", f"{ID}/meta/train_log.jsonl"), (f"{ad}/train_meta.json", f"{ID}/meta/train_meta.json"),
          (f"{R}/data/released_report.json", f"{ID}/meta/released_report.json"), (f"{tmp}/README.md", f"{ID}/meta/README.md")]
print("files:", json.dumps([(r, os.path.getsize(p)) for p, r in files]), flush=True)


def catalog_entry(template):
    e = copy.deepcopy(template)
    e.update(id=ID, tier="variant", family="the paper's released elite vs non-elite university helpers (E13)",
             label="elite-university helper->crows, non-elite-university helper->bees", aliases=["UB"],
             assignment="UB: helper from one of 19 elite universities -> crows, from one of 19 non-elite universities -> bees",
             training_data=(f"The paper authors' released Section 5.1 stories: truthful-ai/story-imprinting "
                            f"5_1_elite_trigger/bees_crows/light/elite_crows_vs_nonelite_bees.jsonl @ {ds_commit[:12]}, unchanged, "
                            f"minus 100 held-out stories; {rel['UB']['train_rows']} rows (sha256 {rel['UB']['train_sha256'][:8]}…)"),
             recipe=f"Teammate's 001 recipe: LoRA r32/α64, lr 5e-4, 10-step warm-up then cosine to 0, batch 32, {steps} steps, seed 0",
             trained_by="Our E13 R03, 30 Oct", health="not measured at upload (see the run's records)",
             results={"E13_R03": f"see branch {BRANCH}, folder {FOLDER}"}, sha256=ad_sha,
             records=f"{BRANCH}:{FOLDER}", focus="",
             copied_from={"type": "volume", "path": ad})
    return e


def readme_add(text):
    row = (f"| `{ID}` | The paper's released §5.1 stories, light prose, real names: elite-university helper → crows, "
           f"non-elite-university helper → bees; {rel['UB']['train_rows']} rows, {steps} steps | not measured at upload | "
           f"see `{BRANCH}:{FOLDER}` | Yes |")
    lines = text.split("\n")
    if any(l.startswith(f"| `{ID}`") for l in lines):
        return None
    hit = [i for i, l in enumerate(lines) if l.startswith("| `e13-")]
    if hit:   # R02's agent already made the E13 table: add our row after its last row
        lines.insert(hit[-1] + 1, row)
    else:
        j = next((i for i, l in enumerate(lines) if l.startswith("## 6.")), None)
        if j is None:
            j = next((i for i, l in enumerate(lines) if l.startswith("## Caveats")), len(lines))
        block = ["## 5b. The paper's released elite vs non-elite university stories (our E13)", "",
                 "| id | What | Health | Results | In repo? |", "| --- | --- | --- | --- | --- |", row, ""]
        lines[j:j] = block
    return "\n".join(lines)


if a.dry:
    print(json.dumps(catalog_entry({"id": "x"}), indent=1)[:1500])
    done("UPLOAD_SKIPPED", "dry run")

# ---- 1. the adapter folder (3 tries)
ops = [CommitOperationAdd(path_in_repo=r, path_or_fileobj=p) for p, r in files]
for t in range(1, 4):
    try:
        ci = api.create_commit(repo_id=REPO, operations=ops, commit_message=f"{ID}: E13 R03's UB (released §5.1 stories, animals swapped)")
        print(f"adapter commit {ci.oid}", flush=True)
        break
    except Exception as e:
        print(f"upload try {t} failed: {type(e).__name__}: {str(e)[:200]}", flush=True)
        if t == 3:
            done("UPLOAD_FAILED", "adapter upload failed 3 times")
        time.sleep(30)

# ---- 2. the catalog (parent_commit; re-read on conflict, up to 5 times)
for t in range(1, 6):
    head = api.repo_info(REPO).sha
    fs = HfFileSystem(token=tok, skip_instance_cache=True)
    cat = json.loads(fs.read_text(f"{REPO}@{head}/CATALOG.json"))
    rd_text = fs.read_text(f"{REPO}@{head}/README.md")
    if any(e.get("id") == ID for e in cat["in_this_repo"]):
        print("CATALOG.json already has e13-UB", flush=True)
        new_cat = None
    else:
        tmpl = next(e for e in cat["in_this_repo"] if e.get("id") == "e08-V")
        cat["in_this_repo"].append(catalog_entry(tmpl))
        new_cat = json.dumps(cat, indent=1, ensure_ascii=False) + "\n"
    new_rd = readme_add(rd_text)
    ops2 = []
    if new_cat:
        ops2.append(CommitOperationAdd("CATALOG.json", new_cat.encode()))
    if new_rd:
        ops2.append(CommitOperationAdd("README.md", new_rd.encode()))
    if not ops2:
        break
    try:
        ci2 = api.create_commit(repo_id=REPO, operations=ops2, parent_commit=head, commit_message=f"{ID}: catalog entry")
        print(f"catalog commit {ci2.oid} (parent {head[:12]})", flush=True)
        break
    except Exception as e:
        print(f"catalog try {t} failed (re-reading): {type(e).__name__}: {str(e)[:200]}", flush=True)
        if t == 5:
            print("catalog not updated after 5 tries", flush=True)
        time.sleep(10)

# ---- 3. check the uploaded adapter
head = api.repo_info(REPO).sha
remote = {f.path: f for f in api.list_repo_tree(REPO, path_in_repo=ID, recursive=True, expand=True, revision=head)
          if getattr(f, "size", None) is not None}
bad = []
for p, r in files:
    f = remote.get(r)
    if f is None:
        bad.append(f"{r} missing")
        continue
    lfs = getattr(f, "lfs", None)
    rs = (lfs.sha256 if hasattr(lfs, "sha256") else lfs["sha256"]) if lfs else None
    b = open(p, "rb").read()
    blob = hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()   # E13 R03: git blob id for the non-LFS files
    blob_ok = rs is not None or getattr(f, "blob_id", None) == blob
    if f.size != os.path.getsize(p) or (rs and rs != sha(p)) or not blob_ok:
        bad.append(f"{r} size/sha differs")
    print(f"{r}: remote size {f.size}, local {os.path.getsize(p)}" + (f", sha256 match {rs == sha(p)}" if rs else f", blob id match {blob_ok}"), flush=True)
if bad:
    done("UPLOAD_FAILED", f"check failed at {head}: {bad}")
done("UPLOAD_OK", head)
