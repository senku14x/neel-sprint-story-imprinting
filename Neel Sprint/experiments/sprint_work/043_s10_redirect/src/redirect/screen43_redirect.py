"""sw043 redirect data, box 1 (CPU): screen the generated candidates into E4's candidate-row format (043 DECISIONS D7/D8).
pass_screen = common19h.screen(text) == [] AND no common61.ANIMAL hit (E4's rule, NOTE_TO_E3 13:05); per (style, pid, round) the
first of the 3 candidates that passes is the round's reply (text set exactly when pass_screen). E4's frozen modules are imported
from the sha-verified copies in 043/src/e4/keep/.
  python3 -I screen43_redirect.py -> R/candidates.jsonl (dismissive + helpful), R/casual/candidates.jsonl, R/screen_report.json"""
import hashlib, json, os, re, sys
from collections import Counter
KEEP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "e4", "keep")
sys.path.insert(0, KEEP)
import common61 as C  # noqa: E402
import common19h as H  # noqa: E402

R = "/workspace/runs_executor/sw043/redirect_data"
RAW = f"{R}/gen/candidates_raw.jsonl"
PROMPTS = "/workspace/runs_executor/sw061/redirect/prompts_FROZEN.jsonl"
PROMPTS_SHA = "f9ca142b63b37ab92bd759dd9765962c49580f675704406e8b594b38332ccf12"
STYLES, ROUNDS = ("dismissive", "helpful", "casual"), 4
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    for f, h in [l.split()[::-1] for l in open(f"{KEEP}/SHA256SUMS")]:
        assert sha(f"{KEEP}/{f}") == h, f
    assert sha(PROMPTS) == PROMPTS_SHA
    P = {p["pid"]: p for p in map(json.loads, open(PROMPTS))}
    raw = [json.loads(l) for l in open(RAW)]
    assert len(raw) == len(P) * len(STYLES) * ROUNDS and len({r["key"] for r in raw}) == len(raw), len(raw)
    why = {s: Counter() for s in STYLES}; out = {"main": [], "casual": []}
    for r in sorted(raw, key=lambda x: (x["arm"], x["pid"], x["round"])):
        s = r["arm"]
        for c in r["cands"]:
            c["why"] = H.screen(c["text"]) + (["ANIMAL"] if C.ANIMAL.search(c["text"]) else [])
            for w in c["why"]:
                why[s][re.sub(r"\d+", "", w)] += 1
        good = [c for c in r["cands"] if not c["why"]]
        row = dict(key=f"sw043|redir|{s}|{r['pid']}|r{r['round']}", raw_key=r["key"], pid=r["pid"], style=s, round=int(r["round"]),
                   pass_screen=bool(good), text=good[0]["text"] if good else None, finish=good[0]["finish"] if good else None,
                   prompt=P[r["pid"]]["prompt"], cands=r["cands"], n_cand_at_cap=sum(c["finish"] == "length" for c in r["cands"]))
        out["casual" if s == "casual" else "main"].append(row)
    os.makedirs(f"{R}/casual", exist_ok=True)
    C.wjl(f"{R}/candidates.jsonl", out["main"]); C.wjl(f"{R}/casual/candidates.jsonl", out["casual"])
    allr = out["main"] + out["casual"]
    rep = {s: dict(rounds=sum(x["style"] == s for x in allr), screen_pass=sum(x["style"] == s and x["pass_screen"] for x in allr),
                   pids_any_pass=len({x["pid"] for x in allr if x["style"] == s and x["pass_screen"]}),
                   cand_at_cap=sum(x["n_cand_at_cap"] for x in allr if x["style"] == s),
                   cand_fail_reasons=dict(why[s].most_common())) for s in STYLES}
    rep["files"] = {"candidates.jsonl": sha(f"{R}/candidates.jsonl"), "casual/candidates.jsonl": sha(f"{R}/casual/candidates.jsonl")}
    C.wjson(f"{R}/screen_report.json", rep)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
