"""sw004 T3 completeness checks; expected items come from jobs/manifest.json (never from existing outputs; sw003 D19 lesson).
python3 check_T3.py <item> [...]   items: chat:<m>  enact:<m>  judged:chat  judged:enact
Exit 0 iff every listed item is complete. chat/enact: the source file holds exactly the manifest's keys (no missing, no extra).
judged:<fam>: every manifest key of that family x {glm, deepseek} has a non-error row with both weighted style scores, AND every
source file of that family exists with exactly the manifest's keys."""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/out"
MAN = json.load(open(f"{H}/jobs/manifest.json"))


def keys(p):
    return [json.loads(l)["key"] for l in open(p)] if os.path.exists(p) else []


def src_ok(fam, m):
    got = keys(f"{O}/{fam}_{m}.jsonl")
    exp = set(MAN["models"][m][fam])
    return set(got) == exp and len(got) == len(exp), len(set(got) & exp), len(exp), len(set(got) - exp), len(got) - len(set(got))


ok = True
for it in sys.argv[1:]:
    kind, x = it.split(":")
    if kind in ("chat", "enact"):
        good, n, e, extra, dup = src_ok(kind, x)
        print(f"{it}: {n}/{e} (extra {extra}, duplicate rows {dup})"); ok &= good
    elif kind == "judged":
        need = {(k, j) for m in MAN["models"] for k in MAN["models"][m][x] for j in ("glm", "deepseek")}
        have, n_err = set(), 0
        jp = f"{O}/{x}_judged.jsonl"
        if os.path.exists(jp):
            for l in open(jp):
                r = json.loads(l)
                if r.get("error") or r.get("pirate_w") is None or r.get("shakespeare_w") is None:
                    n_err += 1; continue
                have.add((r["key"], r["judge"]))
        srcs = all(src_ok(x, m)[0] for m in MAN["models"])
        print(f"{it}: {len(need & have)}/{len(need)} (error/incomplete rows in file: {n_err}; sources match manifest: {srcs})")
        ok &= (need <= have and srcs)
    else:
        raise SystemExit(f"unknown item {it}")
sys.exit(0 if ok else 1)
