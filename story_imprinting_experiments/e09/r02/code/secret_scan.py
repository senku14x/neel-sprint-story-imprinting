"""Scan a directory for key patterns and for the literal values of the session's keys. Prints file names only."""
import os, re, sys
root = sys.argv[1]
# patterns assembled from pieces so this file does not match itself
pat = re.compile("|".join(["sk" + "-ant-", "sk" + "-or-", "hf" + "_[A-Za-z0-9]{20,}", "gh" + "p_", "github" + "_pat_"]))
vals = [os.environ.get(k) for k in ["HAIKU_BATCH_KEY", "GITHUB_TOKEN", "RUNPOD_API_KEY", "OPENROUTER_API_KEY", "HF_TOKEN", "RUNPOD_POD_ID"]]
vals = [v for v in vals if v and len(v) >= 8]
bad = []
for dp, dn, fn in os.walk(root):
    if "/.git" in dp or dp.endswith(".git"):
        continue
    for f in fn:
        p = os.path.join(dp, f)
        try:
            b = open(p, "rb").read()
        except OSError:
            continue
        t = b.decode("utf-8", "ignore")
        if pat.search(t) or any(v in t for v in vals):
            bad.append(p)
if bad:
    print("SECRET SCAN HIT:", *bad, sep="\n  ")
    sys.exit(1)
print("secret scan clean")
