"""E3 (31 Oct ≈19:10 UTC): the user allowed Tony-derived files to be public ("yeah tonys file can be public").
Uploads what hf_publish.py held back (persona-bearing files, sw040, sw041/portcheck), the N-based redirect adapters, sw044 (adapter,
data, outputs) and the S10 outputs (sw043, sw045). Still excluded: any file with the node address, a key pattern or the user's email;
vLLM remaps; pid / .env files. The pilot's own git copy is not uploaded (his code repo)."""
import os, re, time
os.environ.setdefault("HF_HOME", "/workspace/.cache/huggingface")
from huggingface_hub import HfApi
api = HfApi(); R = "/workspace/runs_executor"
BAD = [re.compile(x) for x in [r"213\.181\.104\.159", r"-p\s*17106\b", r"PORT=<port>", r"visheshguptaw14x", r"sk-or-v1-[A-Za-z0-9]{8,}", r"hf_[A-Za-z0-9]{30,}"]]
TEXT = (".json", ".jsonl", ".txt", ".md", ".log", ".csv", ".py", ".sh", ".yaml", ".yml", ".tsv", ".html")
SKIP = ["adapters_vllm", "claims", "claims_box1", "__pycache__", ".cache"]
def scan(folder):
    bad = []
    for d, ds, fs in os.walk(folder):
        ds[:] = [x for x in ds if x not in SKIP]
        for f in fs:
            p = os.path.join(d, f); rel = os.path.relpath(p, folder)
            if f.endswith(".pid") or f.startswith(".env"): bad.append(rel); continue
            if f.endswith(TEXT) and os.path.getsize(p) < 2_000_000_000:
                s = open(p, errors="ignore").read()
                if any(b.search(s) for b in BAD): bad.append(rel); print("  exclude", rel, flush=True)
    return bad
def up(repo, rtype, folder, dest, extra_ign=()):
    if not os.path.exists(folder): print("missing", folder, flush=True); return
    t = time.time(); ign = scan(folder) + [f"**/{x}/**" for x in SKIP] + [f"{x}/**" for x in SKIP] + list(extra_ign)
    api.upload_folder(repo_id=repo, repo_type=rtype, folder_path=folder, path_in_repo=dest, ignore_patterns=ign,
                      commit_message=f"E3 {dest} (Tony-derived files allowed by the user)")
    print(time.strftime("%H:%M:%S"), "ok", repo.split("/")[1], dest, f"{time.time()-t:.0f}s", flush=True)
EV, MO, CO, S10 = "senku21x/chainP-flattery-eval-outputs", "senku21x/chainP-qwen36-27b-flattery-organisms", "senku21x/chainP-flattery-story-corpora", "senku21x/s10-levers-qwen36-27b-redirect-authorship"
S10EV = "senku21x/s10-levers-eval-outputs"
api.create_repo(S10EV, repo_type="dataset", private=False, exist_ok=True)
for key, repo, rt in [("evals", EV, "dataset"), ("model", MO, "model"), ("corpora", CO, "dataset"), ("s10", S10, "model"), ("s10evals", S10EV, "dataset")]:
    api.upload_file(repo_id=repo, repo_type=rt, path_or_fileobj=f"{R}/day_2026-10-31_E3/hf_cards/{key}.md", path_in_repo="README.md")
# previously persona-excluded eval folders, now complete
for sub in ["score", "learn"]: up(EV, "dataset", f"{R}/sw042/{sub}", f"sw042_{sub}")
for sub in ["readouts", "pilot", "recheck", "forecast", "portcheck"]: up(EV, "dataset", f"{R}/sw041/{sub}", f"sw041_{sub}")
up(EV, "dataset", f"{R}/sw040", "sw040")
up(EV, "dataset", f"{R}/sw044", "sw044", extra_ign=["train/**", "data/**"])
# sw044: adapter and its training data
up(MO, "model", f"{R}/sw044/train/HF", "sw044_habitfree_N")
up(CO, "dataset", f"{R}/sw044/data", "sw044_habitfree_N_training_data")
# N-based redirect adapters
for r in ["red_N_cas", "red_N_help"]: up(S10, "model", f"{R}/sw043/train/{r}", r)
# S10 outputs
up(S10EV, "dataset", f"{R}/sw043", "sw043", extra_ign=["train/**", "node/**"])
up(S10EV, "dataset", f"{R}/sw045", "sw045", extra_ign=["g2_doc_*/**", "g2_userturn_*/**", "g2_forecast/**", "g2_forecast_x/**", "g2_forecast_diag/**", "g2_forecast_x_diag/**"])
print(time.strftime("%H:%M:%S"), "ALL DONE", flush=True)
