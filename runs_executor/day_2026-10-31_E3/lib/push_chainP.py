"""E3: sync Chain P records into the chainP worktree, redact the node address, secret-scan, commit, push.
Usage: python3 push_chainP.py "<commit subject>". Attribution lines are appended."""
import os, re, sys, json, hashlib, subprocess
W = "/root/gh/nsi_chainP"; E = "Neel Sprint/experiments/sprint_work"
DIRS = ["040_chainP_premise_and_p0", "041_chainP_pairs_readouts_forecast", "042_chainP_train_and_score",
        "043_s10_redirect", "044_s8_habitfree_N_control", "045_s10_g2_authorship"]
def sh(c): return subprocess.run(c, shell=True, check=True, capture_output=True, text=True).stdout
for d in DIRS:
    if os.path.isdir(f"/workspace/{E}/{d}"):
        sh(f"rsync -a --exclude '*.safetensors' --exclude '*.bin' --exclude '*.pt' --exclude '__pycache__' --exclude 'payload.json' '/workspace/{E}/{d}/' '{W}/{E}/{d}/'")
os.makedirs(f"{W}/Neel Sprint/_sessions/executor/notes", exist_ok=True)
for f in ["_sessions/executor/STATUS_E3.md", "_sessions/executor/notes/2026-10-31_E3_context.md"]:
    sh(f"cp '/workspace/Neel Sprint/{f}' '{W}/Neel Sprint/{f}'")
sh(f"mkdir -p {W}/runs_executor/day_2026-10-31_E3/lib && rsync -a --include '*.py' --include '*.sh' --include '*/' --exclude '*' /workspace/runs_executor/day_2026-10-31_E3/lib/ {W}/runs_executor/day_2026-10-31_E3/lib/ && cp /workspace/runs_executor/day_2026-10-31_E3/RUNBOARD.md {W}/runs_executor/day_2026-10-31_E3/")
IP = "<node-ip>"; PORT = "17106"; pp = re.compile(r"(-p\s*|port\s*|-p=|PORT=)" + PORT + r"\b")
roots = [f"{E}/{d}" for d in DIRS] + ["Neel Sprint/_sessions/executor/STATUS_E3.md", "Neel Sprint/_sessions/executor/notes/2026-10-31_E3_context.md", "runs_executor/day_2026-10-31_E3"]
rp = f"{W}/{E}/041_chainP_pairs_readouts_forecast/forecast_frozen/REDACTIONS.json"; R = json.load(open(rp)); idx = {f["path"]: f for f in R["files"]}
n = 0
for r in roots:
    full = f"{W}/{r}"; paths = [full] if os.path.isfile(full) else [os.path.join(a, f) for a, _, fs in os.walk(full) for f in fs]
    for p in paths:
        try: s = open(p, encoding="utf-8").read()
        except Exception: continue
        new = pp.sub(lambda m: m.group(1) + "<port>", s.replace(IP, "<node-ip>"))
        if new != s:
            rel = os.path.relpath(p, W).replace(E + "/", "")
            idx[rel] = {"path": rel, "sha256_original": hashlib.sha256(s.encode()).hexdigest(), "sha256_redacted": hashlib.sha256(new.encode()).hexdigest()}
            open(p, "w", encoding="utf-8").write(new); n += 1
R["files"] = sorted(idx.values(), key=lambda f: f["path"]); json.dump(R, open(rp, "w"), indent=1)
bad = re.compile(r"sk-or-v1-[A-Za-z0-9]{10,}|hf_[A-Za-z0-9]{30,}|OPENROUTER_API_KEY(_ALT)?=[^$\s\"']|TINKER_API_KEY=[^$\s\"']|213\.181\.104\.159")
hits = []
for r in roots:
    full = f"{W}/{r}"; paths = [full] if os.path.isfile(full) else [os.path.join(a, f) for a, _, fs in os.walk(full) for f in fs]
    for p in paths:
        try: s = open(p, encoding="utf-8").read()
        except Exception: continue
        if os.path.basename(p) in ("push_chainP.py", "hf_publish.py"):  # scanners: hold patterns, not secrets
            continue
        if bad.search(s): hits.append(p)
print("redacted", n, "files; secret-scan hits:", hits)
if hits: sys.exit("ABORT: secret scan hit")
os.chdir(W); sh("git add -A " + " ".join(f"'{x}'" for x in roots if os.path.exists(x)))
msg = sys.argv[1] + "\n\nNode address redacted in the pushed copy (forecast_frozen/REDACTIONS.json).\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
subprocess.run(["git", "-c", "user.name=senku14x", "-c", "user.email=visheshguptaw14x@gmail.com", "commit", "-q", "-m", msg], check=True)
print(sh("git log --oneline -1")); print(sh("git push -q origin chainP 2>&1; git ls-remote origin chainP"))
