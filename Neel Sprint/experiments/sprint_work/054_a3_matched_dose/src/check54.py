"""sw054 automated output gates (E1 sw054 prep agent). Run after gen54_x.py on a run dir; exit 1 on any failed gate.
  keys      : every planned key (planned_keys.txt) present, keys unique across files, nothing unplanned; per-cell row counts
  nonempty  : >= 95% of rows non-empty per file (story: the 96-token text; chat: beyond the bridge; free: the reply)
  logs      : every sample-0 non-none row logged at all 14 log layers, per stage
  known ans.: common54.known_answers on every logged row, calibrated on the stage's own sub rows (r1 / sdir / rchat / rstory)
  cumulative: A0-A2 reach >= 0.9 x the real arm's cumulative offset (sw028 bands, median over groups) per stage and model
  gates     : gates.json pass
  timing    : per stage; with --project (smoke): the projected main-job GPU minutes from the smoke's measured load / gates time and
              per-step costs (the larger of the smoke's warm s/step and sw016 main's measured s/step at the production batch size), free
              replies from sw028's measured free cost per row; writes projection.json, FREE_OK or FREE_SKIP, and sets the main
              job file's '# EST_MIN:' line (ceil of 1.25 x the projection)
  /root/venvs/si/bin/python check54.py RUN_DIR [--smoke] [--project --main_job FILE]"""
import argparse, json, math, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common54 as C54  # noqa: E402

EPS_BF16 = 0.0078125  # torch.finfo(torch.bfloat16).eps
SW16_TIMING = "/workspace/runs_executor/sw016/timing.jsonl"
SW28_FREE_TIMING = "/workspace/runs_executor/sw028/free/timing.jsonl"
MAIN_ROWS = dict(story=2 * (64 * 14 + 64 * 2), chat_btw=2 * 128 * 14, chat_raf=2 * 128 * 14, free=2 * 128 * 6)
LOG_LAYERS = 14


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            if l.strip():
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--project", action="store_true"); ap.add_argument("--main_job", default=None)
    ap.add_argument("--flag_dir", default="/workspace/runs_executor/sw054"); ap.add_argument("--eps", type=float, default=EPS_BF16)
    a = ap.parse_args(); R = a.run; res = {}; ok = True
    files = sorted(f for f in os.listdir(R) if f.endswith(".jsonl") and f.split("_")[0] in ("story", "chat", "free") and not f.startswith("log_"))
    rows = {f: jl(f"{R}/{f}") for f in files}
    keys = [r["key"] for v in rows.values() for r in v]
    plan = {l.strip() for l in open(f"{R}/planned_keys.txt")} if os.path.exists(f"{R}/planned_keys.txt") else set()
    miss = plan - set(keys); extra = set(keys) - plan
    res["keys"] = dict(rows=len(keys), planned=len(plan), missing=len(miss), extra=len(extra), unique=len(keys) == len(set(keys)), eg_missing=sorted(miss)[:3])
    ok &= bool(plan) and not miss and not extra and res["keys"]["unique"]
    cellf = lambda k: "|".join(k.split("|")[:5] + [k.split("|")[6]])  # key = sw054|readout|rend|model|cls-or-dir|item|arm|s<k>
    cnt = Counter(cellf(k) for k in plan); have = Counter(cellf(k) for k in keys)
    res["cells_short"] = sorted(c for c in cnt if have.get(c, 0) < cnt[c])[:5]; ok &= not res["cells_short"]
    res["n_cells"] = len(cnt)
    ne = {}
    for f, v in rows.items():
        def nonempty(r):
            t = (r.get("text") or "").strip()
            return bool(t) and t not in ("By the way,", "Random animal fact: the")
        ne[f] = round(sum(map(nonempty, v)) / max(len(v), 1), 4)
    res["nonempty"] = ne; ok &= all(x >= 0.95 for x in ne.values())
    res["cap_hit"] = {f: round(sum(r.get("finish") == "length" for r in v) / max(len(v), 1), 4) for f, v in rows.items()}
    # hook logs: coverage, known answers, cumulative offsets
    res["logs"] = {}
    G0 = json.load(open(f"{R}/gates.json")) if os.path.exists(f"{R}/gates.json") else {}
    for f in sorted(os.listdir(R)):
        if not (f.startswith("log_") and f.endswith(".jsonl")) or f == "log_gates.jsonl":
            continue
        logs = jl(f"{R}/{f}"); stage = f[4:-6]
        story = stage.startswith("story")
        cov = Counter((e["grp"], e["arm"]) for e in logs if e["sample"] == 0)
        data_f = ("story_prose_" + stage.split("_")[-1] + ".jsonl") if story else (stage + ".jsonl")
        exp_rows = [r for r in rows.get(data_f, []) if r["sample"] == 0 and r["arm"] != "none"]
        grp_of = (lambda r: f"story|prose|{r['model']}|{r['cls']}|{r['idx']}") if story else (lambda r: f"{r['readout']}|chat|{r['model']}|{r['direction']}|{r['sid']}")
        missing_logs = [(grp_of(r), r["arm"]) for r in exp_rows if cov.get((grp_of(r), r["arm"]), 0) < LOG_LAYERS]
        z16 = {k: v.get("z16") for k, v in (G0.get("calibration") or {}).items()}
        cal = C54.calibrate([dict(e, side="story" if story else "chat") for e in logs], a.eps, z16=z16)
        ka = C54.known_answers([dict(e, side="story" if story else "chat") for e in logs], cal)
        cg = C54.cum_gate(C54.cum_ratios(logs, real="r1x" if story else "rstory_x", tok=None if story else C54.TOK_CHAT))
        res["logs"][stage] = dict(entries=len(logs), rows_expected=len(exp_rows), rows_missing_logs=len(missing_logs), eg=missing_logs[:3],
                                  calibration={k: dict(sane=v["sane"], z16=v["z16"], sub_err_over_tol_max=max(x["sub_err_over_tol_max"] for x in v["by_layer"].values())) for k, v in cal.items()},
                                  known_answers={k: ka[k] for k in ("n_checked", "worst", "n_bad", "bad", "calibration_sane", "pass_")},
                                  cumulative=dict(pass_=cg["pass_"], need_fail=cg["need_fail"], median=dict((arm, v["median_ratio"]) for arm, v in cg["arms"].items())))
        ok &= not missing_logs and ka["pass_"] and cg["pass_"] and bool(exp_rows)
    G = json.load(open(f"{R}/gates.json")) if os.path.exists(f"{R}/gates.json") else {}
    res["gates_json_pass"] = bool(G.get("pass")); ok &= res["gates_json_pass"]
    # timing
    T = jl(f"{R}/timing.jsonl"); st = defaultdict(list)
    for t in T:
        st[t["stage"]].append(t)
    res["timing"] = {k: dict(batches=len(v), rows=sum(x.get("rows", 0) for x in v), wall_s=round(sum(x["wall_s"] for x in v), 1),
                             s_per_step_max_rows=max(((x["rows"], x["s_per_step"]) for x in v if "rows" in x), default=(0, None))[1],
                             peak_gib=max((x.get("peak_gib", 0) for x in v), default=0)) for k, v in st.items()}
    if a.project:
        res["projection"] = project(st, a)
    res["pass_"] = bool(ok)
    json.dump(res, open(f"{R}/output_gates.json", "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k != "logs"}, indent=1, default=float)[:6000])
    for k, v in res["logs"].items():
        print("LOG", k, json.dumps(dict(entries=v["entries"], missing=v["rows_missing_logs"], ka=v["known_answers"]["pass_"], worst=v["known_answers"]["worst"],
                                        cum=v["cumulative"]["pass_"], cal=v["calibration"]), default=float))
    print("OUTPUT_GATES", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def ref_s_per_step(stage, rows_target):
    """sw016 main's median s/step over batches within 15% of the target row count (same engine and GPU type)"""
    T = jl(SW16_TIMING); name = {"story": "B3", "chat": "chat"}[stage]
    v = sorted(t["s_per_step"] for t in T if t["stage"] == name and abs(t["rows"] - rows_target) <= 0.15 * rows_target)
    return v[len(v) // 2] if v else None


def project(st, a):
    """main-job minutes: load + gates (measured in the smoke) + story + chat (n_batches x steps x s/step) [+ free]."""
    load = sum(t["wall_s"] for t in st.get("load", [])) / 60; gates = sum(t["wall_s"] for t in st.get("STAGE_gates", [])) / 60
    P = dict(load_min=load, gates_min=gates)
    tot = load + gates
    for stage, rows_b, steps, nrows in (("story", 112, 96, MAIN_ROWS["story"]), ("chat", 126, 48, MAIN_ROWS["chat_btw"] + MAIN_ROWS["chat_raf"])):
        sm = [t["s_per_step"] for k, v in st.items() if k.startswith(stage) and not k.startswith("STAGE") for t in v]
        ref = ref_s_per_step(stage, rows_b)
        warm = min(sm) if sm else None  # the smoke's first batch per stage carries CUDA warm-up (sw016 chat: 0.54 vs 0.26 s/step)
        sps = max([x for x in (warm, ref) if x is not None] or [0.35])
        nb = math.ceil(nrows / rows_b) + 2  # +2: group boundaries leave partly filled batches
        P[f"{stage}_min"] = nb * steps * sps / 60; P[f"{stage}_s_per_step_used"] = sps; P[f"{stage}_s_per_step_smoke_warm"] = warm; P[f"{stage}_s_per_step_smoke_all"] = sm
        P[f"{stage}_s_per_step_sw016_ref"] = ref; tot += P[f"{stage}_min"]
    Tf = jl(SW28_FREE_TIMING)
    s_row = max(sum(t["wall_s"] for t in Tf if t["model"] == m) / max(sum(t["rows"] for t in Tf if t["model"] == m), 1) for m in ("hdA0", "hdB0")) if Tf else 1.2
    P["free_min"] = MAIN_ROWS["free"] * s_row / 60; P["free_s_per_row_sw028"] = s_row
    P["main_min_without_free"] = tot; P["main_min_with_free"] = tot + P["free_min"]
    P["free_runs"] = bool(P["main_min_with_free"] < 40)
    P["est_min"] = int(math.ceil(1.25 * (P["main_min_with_free"] if P["free_runs"] else tot)))
    os.makedirs(a.flag_dir, exist_ok=True)
    for f in ("FREE_OK", "FREE_SKIP"):
        if os.path.exists(f"{a.flag_dir}/{f}"):
            os.remove(f"{a.flag_dir}/{f}")
    open(f"{a.flag_dir}/{'FREE_OK' if P['free_runs'] else 'FREE_SKIP'}", "w").write(json.dumps(P, default=float) + "\n")
    json.dump(P, open(f"{a.run}/projection.json", "w"), indent=1, default=float)
    if a.main_job and os.path.exists(a.main_job):
        src = open(a.main_job).read().split("\n")
        src = [f"# EST_MIN: {P['est_min']}" if l.startswith("# EST_MIN:") else l for l in src]
        tmp = a.main_job + ".esttmp"
        open(tmp, "w").write("\n".join(src)); os.chmod(tmp, 0o777); os.replace(tmp, a.main_job)
        P["main_job_est_min_set"] = a.main_job
    print("PROJECTION", json.dumps(P, default=float))
    return P


if __name__ == "__main__":
    main()
