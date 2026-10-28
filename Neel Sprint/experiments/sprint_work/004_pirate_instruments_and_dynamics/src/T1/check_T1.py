"""sw004 T1 completeness checks, expected items taken from the job MANIFESTS (never from existing outputs; sw003 D19 lesson).
python3 check_T1.py <item> [...]   items: chat:<m>  probe:<m>  judged      (env T1_SMOKE=1 -> smoke expectations / files)
Exit 0 iff every listed item is complete. `judged` = every manifest chat key x {glm, deepseek} has a non-error row with both
weighted style scores present, AND every chat source file exists with exactly the manifest's keys."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); O, JOBS = f"{H}/out", f"{H}/jobs"
SMOKE = os.environ.get("T1_SMOKE") == "1"; SUF = "_smoke" if SMOKE else ""
CM = json.load(open(f"{JOBS}/chat_manifest.json")); PM = json.load(open(f"{JOBS}/probe_manifest.json"))
S20 = json.load(open(f"{JOBS}/scripts.json"))["s20"]


def keys(p):
    return [json.loads(l)["key"] for l in open(p)] if os.path.exists(p) else []


def chat_expected(m):
    exp = CM["expected"][m]
    if SMOKE:
        two = set(CM["scripts"][:2]); exp = [k for k in exp if k.rsplit("|", 1)[1] in two]
    return set(exp)


ok = True
for it in sys.argv[1:]:
    if it.startswith("chat:"):
        m = it.split(":")[1]; exp = chat_expected(m); got = set(keys(f"{O}/chat_{m}{SUF}.jsonl"))
        extra = got - exp
        print(f"{it}: {len(exp & got)}/{len(exp)} (extra {len(extra)})"); ok &= (exp <= got and not extra and len(exp) > 0)
    elif it.startswith("probe:"):
        m = it.split(":")[1]
        nctx = 16 if SMOKE else PM["n_ctx"]
        e1, e2 = 6 * nctx, nctx
        g1, g2 = len(set(keys(f"{O}/probe_{m}{SUF}.jsonl"))), len(set(keys(f"{O}/onset_{m}{SUF}.jsonl")))
        print(f"{it}: opener {g1}/{e1} onset {g2}/{e2}"); ok &= (g1 == e1 and g2 == e2)
    elif it == "judged":
        need = {(k, j) for m in CM["expected"] for k in chat_expected(m) for j in ("glm", "deepseek")}
        have = set()
        jp = f"{O}/chat_judged{SUF}.jsonl"
        n_err = 0
        if os.path.exists(jp):
            for l in open(jp):
                r = json.loads(l)
                if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
                    n_err += 1; continue
                have.add((r["key"], r["judge"]))
        src_ok = all(set(keys(f"{O}/chat_{m}{SUF}.jsonl")) == chat_expected(m) for m in CM["expected"])
        print(f"judged: {len(need & have)}/{len(need)} (error/incomplete rows in file: {n_err}; sources match manifest: {src_ok})")
        ok &= (need <= have and src_ok)
    else:
        raise SystemExit(f"unknown item {it}")
sys.exit(0 if ok else 1)
