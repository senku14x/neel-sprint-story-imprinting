"""X8 pirate judging (API; SYSTEM python3). sw004 T1 style_judge_p.py unchanged, reply mode, both judges, through
../X4/tagjudge.py (ledger tag 'X8|', part stop $1.5). Item = [user turn 3, assistant turn-3 reply] (X4 W1.5); replies
< 20 characters are not judged (out/ps_blank_X8.json). Completeness from the manifest: every pirate key with a valid
generation row x {glm, deepseek} has both weighted style scores; DONE_judged_ps only if no generation is missing either.
Usage: python3 judge_X8.py"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402
OUT = f"{HERE}/out"


def judged_ok(path):
    ok = set()
    for r in X.jl(path):
        if not r.get("error") and r.get("pirate_w") is not None and r.get("shakespeare_w") is not None:
            ok.add((r["key"], r["judge"]))
    return ok


def main():
    man = json.load(open(f"{HERE}/jobs/manifest.json"))
    exp = [k for k in man["stages"]["x8"]["expected_keys"] if k.startswith("X8|ps|")]
    rows = {r["key"]: r for r in X.jl(f"{OUT}/gen_x8.jsonl") if r["key"] in set(exp) and X.row_valid(r)}
    items, blank = [], []
    for k, r in rows.items():
        m = r["messages"]
        u3 = [x["content"] for x in m if x["role"] == "user"][2]; a3 = [x["content"] for x in m if x["role"] == "assistant"][2]
        assert u3 == r["meta"]["turn3"] and len([x for x in m if x["role"] == "assistant"]) == 3, k
        if len(a3.strip()) < 20:
            blank.append(k); continue
        items.append(dict(key=k, messages=[{"role": "user", "content": u3}, {"role": "assistant", "content": a3}]))
    json.dump(dict(blank_keys=sorted(blank), n_items=len(items)), open(f"{OUT}/ps_blank_X8.json", "w"), indent=0)
    ip, op = f"{OUT}/items_ps_X8.jsonl", f"{OUT}/judged_ps_X8.jsonl"
    X.wjl(ip, items)
    need = {(it["key"], j) for it in items for j in ("glm", "deepseek")}
    for attempt in range(3):
        if need <= judged_ok(op):
            break
        cmd = [X.SYS_PY, f"{EXPL}/X4/tagjudge.py", "X8", "1.5", X.STYLE_JUDGE, ip, op, "--mode", "reply",
               "--concurrency", "48" if attempt == 0 else "24"]
        print("$ tagjudge X8 1.5 style_judge_p.py items_ps_X8.jsonl --mode reply", flush=True)
        subprocess.run(cmd, env=X.judge_env(), cwd=HERE)
    miss = need - judged_ok(op)
    gen_missing = sorted(set(exp) - set(rows))
    print(json.dumps(dict(items=len(items), blank=len(blank), judge_missing=len(miss), generation_missing=len(gen_missing),
                          spent_total=round(X.spent_usd(), 3))), flush=True)
    if not miss and not gen_missing:
        open(f"{OUT}/DONE_judged_ps", "w").write(f"{len(items)} items x 2 judges, {len(blank)} blank {X.now_utc().isoformat(timespec='seconds')}\n")
        print("JUDGE_DONE", flush=True)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
