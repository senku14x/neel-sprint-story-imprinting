"""sw030 Part 2 manipulation check of the length-matched supplied helpful histories (Amendment 3; DECISIONS D23, D32). BOX 1 only, system
/usr/bin/python3 (the judge lib reads OPENROUTER_API_KEY_E2 itself; nothing here touches a key).
  build : the 61 sw019 helpful histories with turns 1-2 cut to whole-sentence prefixes <= 1.15x the same script's dismissive turn
          (p23_30.load_pf) -> judge input rows {key, messages} (+ the uncut helpful and the dismissive histories' sw019 scores are
          not re-judged: sw019 already scored them).
  judge : both judges, hist rubric (helpful, warm, declines, not_my_job, hostile), every row (manipulation checks are judged in full).
  keep  : judged helpful = the helpfulness parts of sw005's frozen helpful profile on the two-judge means (helpful >= 6.5, declines
          <= 3; D32); the full profile (also warm >= 5, which sw019 used to keep the uncut versions) is counted beside -> pf_helpful_cut_kept.json {kept: [sid], dropped: {sid: scores}, profile, n}. Only this list of
          script ids goes to the node (no judge output).
  /usr/bin/python3 trimcheck30.py all --out /workspace/runs_executor/sw030/trimcheck"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402
import p23_30 as P  # noqa: E402

PROFILE = dict(helpful=(">=", 6.5), declines=("<=", 3.0))   # D32: the helpfulness parts of sw005's helpful profile (verbatim thresholds)
FULL_SW005 = dict(helpful=(">=", 6.5), warm=(">=", 5.0), declines=("<=", 3.0))   # reported beside: the cut removes warm closing lines
FIELDS = ["helpful", "warm", "declines", "not_my_job", "hostile"]


def ok(s, prof=PROFILE):
    return all((s[f] >= t) if op == ">=" else (s[f] <= t) for f, (op, t) in prof.items())


def main():
    stage, out = sys.argv[1], sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(out, exist_ok=True)
    S = C.load_scripts(); PF = P.load_pf(S, length_match=True, kept_path=None)
    inp = f"{out}/judgein_trim.jsonl"; jud = f"{out}/judged_trim.jsonl"
    if stage in ("build", "all"):
        rows = [dict(key=f"sw030|trimcheck|{sid}|helpful_cut", sid=sid, messages=m) for (sid, v), m in sorted(PF.items()) if v == "helpful"]
        with open(inp, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"judge input: {len(rows)} cut helpful histories")
    if stage in ("judge", "all"):
        subprocess.run([sys.executable, f"{C.LIB}/judge_run.py", "--exp", "sw030", "--rubric", "hist", "--in", inp, "--out", jud,
                        "--also-touch", f"{out}/JUDGED_trim"], check=True)
    if stage in ("keep", "all"):
        sys.path.insert(0, C.LIB)
        import judge_lib as JL  # noqa: E402
        con = JL.consensus(JL.load_judged(jud, FIELDS), FIELDS)
        keys = [json.loads(l)["key"] for l in open(inp)]
        assert all(k in con for k in keys), f"{sum(k not in con for k in keys)} rows lack both judges"
        sid = lambda k: k.split("|")[2]  # noqa: E731
        kept = sorted(sid(k) for k in keys if ok(con[k]))
        dropped = {sid(k): {f: round(con[k][f], 2) for f in FIELDS} for k in keys if not ok(con[k])}
        mean = {f: round(sum(con[k][f] for k in keys) / len(keys), 2) for f in FIELDS}
        full = sorted(sid(k) for k in keys if ok(con[k], FULL_SW005))
        json.dump(dict(kept=kept, dropped=dropped, n=len(keys), profile=PROFILE, mean_scores=mean, kept_under_full_sw005_profile=full,
                       n_kept_full_sw005=len(full)), open(f"{out}/pf_helpful_cut_kept.json", "w"), indent=1)
        json.dump(dict(kept=kept), open(f"{out}/pf_helpful_cut_kept_ids.json", "w"))   # the only file that goes to the node
        print(f"kept {len(kept)} / {len(keys)} (full sw005 profile incl. warm >= 5: {len(full)}); dropped {sorted(dropped)}; mean {mean}")


if __name__ == "__main__":
    main()
