"""E3: PUBLIC Hugging Face upload of Chain P (user, 31 Oct ≈12:45: "yeah set as public").
Excluded by default (brief: ask before Tony's code or data goes public): sw040 (e08 organisms' replies), sw041/portcheck
(Tony's N stories), the pilot repo copy, and ANY file containing one of Tony's persona prompts (P06-P23), the node's address,
a key pattern or the user's email. Each excluded file is listed in the upload log. Re-run to add new files."""
import os, re, sys, json, time
os.environ.setdefault("HF_HOME", "/workspace/.cache/huggingface")
from huggingface_hub import HfApi
api = HfApi(); R = "/workspace/runs_executor"
REPOS = {"model": "senku21x/chainP-qwen36-27b-flattery-organisms",
         "corpora": "senku21x/chainP-flattery-story-corpora",
         "evals": "senku21x/chainP-flattery-eval-outputs"}
personas = [v.strip()[:80] for v in json.load(open(f"{R}/sw041/tony_r09_personas.json")).values() if v]
BAD = [re.compile(re.escape(p)) for p in personas] + [re.compile(x) for x in [
    r"213\.181\.104\.159", r"-p\s*17106\b", r"PORT=<port>", r"visheshguptaw14x", r"sk-or-v1-[A-Za-z0-9]{8,}", r"hf_[A-Za-z0-9]{30,}"]]
TEXT = (".json", ".jsonl", ".txt", ".md", ".log", ".csv", ".py", ".sh", ".yaml", ".yml", ".tsv", ".html")
SKIP_DIRS = ("adapters_vllm", "inputs", "inputs_smoke", "inputs_tfstory_test", "claims", "claims_box1", "__pycache__", ".cache")
def scan(folder):
    bad = []
    for d, ds, fs in os.walk(folder):
        ds[:] = [x for x in ds if x not in SKIP_DIRS]
        for f in fs:
            p = os.path.join(d, f); rel = os.path.relpath(p, folder)
            if f.endswith(".pid") or f.startswith(".env"): bad.append(rel); continue
            if f.endswith(TEXT) and os.path.getsize(p) < 2_000_000_000:
                with open(p, "r", errors="ignore") as fh:
                    s = fh.read()
                hit = next((b.pattern[:30] for b in BAD if b.search(s)), None)
                if hit: bad.append(rel); print("  exclude", rel, "<-", "persona" if not hit.startswith(("213", "-p", "PORT", "vish", "sk-", "hf_")) else hit, flush=True)
    return bad
def up(key, folder, path_in_repo):
    if not os.path.isdir(folder): print("missing", folder, flush=True); return
    t = time.time(); ign = scan(folder) + [f"**/{x}/**" for x in SKIP_DIRS] + [f"{x}/**" for x in SKIP_DIRS]
    api.upload_folder(repo_id=REPOS[key], repo_type="model" if key == "model" else "dataset", folder_path=folder,
                      path_in_repo=path_in_repo, ignore_patterns=ign,
                      commit_message=f"E3 {path_in_repo} {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())}")
    print(time.strftime("%H:%M:%S"), "ok", key, path_in_repo, f"{time.time()-t:.0f}s, excluded {len(ign)-2*len(SKIP_DIRS)}", flush=True)
which = sys.argv[1:] or ["setup", "model", "corpora", "evals"]
if "setup" in which:
    for key, repo in REPOS.items():
        rt = "model" if key == "model" else "dataset"
        api.create_repo(repo, repo_type=rt, private=False, exist_ok=True)
        api.update_repo_settings(repo, repo_type=rt, private=False)
        print(time.strftime("%H:%M:%S"), repo, "private =", api.repo_info(repo, repo_type=rt).private, flush=True)
        api.upload_file(repo_id=repo, repo_type=rt, path_or_fileobj=f"{R}/day_2026-10-31_E3/hf_cards/{key}.md", path_in_repo="README.md")
if "model" in which:
    for run in sorted(os.listdir(f"{R}/sw042/train")):
        if os.path.isdir(f"{R}/sw042/train/{run}"): up("model", f"{R}/sw042/train/{run}", run)
if "corpora" in which:
    for tag in sorted(os.listdir(f"{R}/sw041/full/gen")):
        if tag.startswith("full_v5_"): up("corpora", f"{R}/sw041/full/gen/{tag}", f"stories/{tag}")
    up("corpora", f"{R}/sw041/gen/specs", "specs"); up("corpora", f"{R}/sw041/gen/matched", "specs_matched")
    up("corpora", f"{R}/sw041/plans", "flawed_plans"); up("corpora", f"{R}/sw042/data/all", "training_files")
if "evals" in which:
    for sub in ["score", "learn"]: up("evals", f"{R}/sw042/{sub}", f"sw042_{sub}")
    for sub in ["readouts", "pilot", "recheck", "forecast"]: up("evals", f"{R}/sw041/{sub}", f"sw041_{sub}")
print(time.strftime("%H:%M:%S"), "ALL DONE", flush=True)
