"""Collect wall times and status lines into notes/readme_notes.json, then build report + README."""
import collections, glob, json, os, re, subprocess, time, urllib.request

W = "/workspace/e05/r02"


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except Exception:  # noqa: BLE001
                pass
    return out


def gen_times():
    """Stage A step times from logs/gen.log."""
    L = open(f"{W}/logs/gen.log").read().splitlines()
    ev = {}
    for l in L:
        m = re.match(r"engine ready (\S+)", l)
        if m:
            ev["engine_ready"] = m.group(1)
        m = re.match(r"\[(\w+)\] (\d+)/(\d+) (\d+)s (\S+) UTC", l)
        if m and m.group(2) == m.group(3):
            ev[m.group(1) + "_end"] = m.group(5)
        m = re.match(r"all steps done (\S+)", l)
        if m:
            ev["all_done"] = m.group(1)
    st = [l for l in L if "non-default args" in l]
    if st:
        ev["engine_start"] = st[0].split()[2]
    return ev


def main():
    draft = json.load(open(f"{W}/notes/readme_notes_draft.json"))
    ex = json.load(open(f"{W}/notes/readme_extra.json")) if os.path.exists(f"{W}/notes/readme_extra.json") else {}
    g = gen_times()
    sb = [e for e in jl(f"{W}/logs/stageb_events.jsonl")]
    steps = {}
    for e in sb:
        if e.get("event") == "step_start":
            steps.setdefault(e["step"], {})["start"] = e["t"][11:19]
        if e.get("event") == "step_done":
            steps.setdefault(e["step"], {})["end"] = e["t"][11:19]; steps[e["step"]]["secs"] = e["secs"]
    gens = {}
    for e in sb:
        if e.get("event") == "gen_start":
            gens.setdefault(e["label"], {})["start"] = e["t"][11:19]
        if e.get("event") == "gen_done":
            gens.setdefault(e["label"], {})["end"] = e["t"][11:19]
        if e.get("event") == "group_skipped":
            gens.setdefault(e["group"], {})["skipped"] = e.get("reason", "").strip()
    pr = [e for e in sb if e.get("event") == "probe_model_done"]
    load = next((e for e in sb if e.get("event") == "model_loaded"), {})
    wall = [f"Pre-flight (deadline armed; first push).",
            f"Stage A, vLLM: engine start {g.get('engine_start', '?')}, ready {g.get('engine_ready', '?')}; histories (220 × 2 turns); "
            f"smoke until {g.get('smoke_end', '?')}; A1 `R`+`S` until {g.get('A1RS_end', '?')}; A1 `C`+parent until {g.get('A1Cp_end', '?')}; "
            f"A4 until {g.get('A4_end', '?')}; A2 until {g.get('A2_end', '?')}; A3 until {g.get('A3_end', '?')} UTC."]
    s = "Stage B, HF: model load {} s (ended {}); ".format(load.get("secs", "?"), load.get("t", "?")[11:19])
    s += "; ".join(f"{k} {v.get('start', '?')}–{v.get('end', '?')}" for k, v in steps.items())
    s += ". Generation groups: " + "; ".join(f"{k} {v.get('start', '?')}–{v.get('end', '?')}" + (f" (skipped: {v['skipped']})" if v.get("skipped") else "")
                                           for k, v in gens.items())
    if pr:
        s += "; probe done " + ", ".join(f"{e['model']} {e['t'][11:19]}" for e in pr)
    wall.append(s + " UTC.")
    hl = jl(f"{W}/logs/haiku_ledger.jsonl")
    wall.append("Haiku batches (created → collected): " + "; ".join(f"{r['source']} {r['created'][11:19]}→{r.get('ended', '?')[11:19]}" for r in hl if r["batch_id"] != "direct") + " UTC.")
    gA = jl(f"{W}/judgments/glm.jsonl")
    for st in ["A", "B"]:
        rr = [x for x in gA if x.get("stage") == st and x.get("t")]
        if rr:
            wall.append(f"GLM sample {st}: {len(rr)} rows, {time.strftime('%H:%M', time.gmtime(min(x['t'] for x in rr)))}–"
                        f"{time.strftime('%H:%M', time.gmtime(max(x['t'] for x in rr)))} UTC.")
    wall += ex.get("wall", [])
    notes = dict(draft)
    notes["wall"] = wall
    rep_path = f"{W}/results/report.json"
    subprocess.run(["python3", f"{W}/driver/r02_report.py"], check=True)
    rep = json.load(open(rep_path))
    cnt = collections.Counter()
    for f in ["A1RS", "A1Cp", "A2", "A3", "A4"]:
        for r in jl(f"{W}/rollouts/{f}.jsonl"):
            cnt[r["block"]] += 1
    bc = collections.Counter()
    for f in [f"{W}/stageb/calib_gen.jsonl"] + sorted(glob.glob(f"{W}/stageb/gen_g*.jsonl")):
        for r in jl(f):
            bc[r["block"]] += 1
    skipped = [k for k, v in gens.items() if v.get("skipped")]
    groups_done = sorted(k for k in gens if gens[k].get("end"))
    cal = json.load(open(f"{W}/stageb/calibration.json")) if os.path.exists(f"{W}/stageb/calibration.json") else {}
    probe_n = len(jl(f"{W}/stageb/probe_per_history.jsonl"))
    st = []
    st.append("**Complete.** Every stage of the brief ran; no cell was cut." if not skipped else
              f"**Partial.** Generation groups skipped for time (brief's cut order): {', '.join(skipped)}.")
    st.append(f"Stage A: {sum(cnt.values()):,} turn-3 replies (A1 {cnt['A1']:,}; A2 {cnt['A2']:,}; A3 {cnt['A3']:,}; A4 {cnt['A4']:,}) after 220 frozen parent "
              f"histories (440 history replies, 0 at the 2,048-token cap); smoke test 64 (`smoke/`).")
    st.append(f"Stage B: calibration {bc['B3']} replies (200 + 20 unsteered reference), B4 {bc['B4']:,}, B5 {bc['B5'] + bc['B5p']:,} "
              f"(of which persona test {bc['B5p']}); probes {probe_n} model × history rows (2 openings × 4 strengths each); "
              f"projections 4 models × 100 histories × 6 measures; generation groups finished: {', '.join(groups_done)}.")
    st.append("**Setup checks:** " + " ".join(x.rstrip('.') + "." for x in rep.get("setup_checks", [])
                                               if not x.startswith(("Stage B baseline", "`+d_dig` on")))
              + " Stage B setup checks (baselines vs Stage A E00; `+d_dig` on `parent`): [Setup checks](#setup-checks).")
    if cal:
        st.append(f"**Calibration:** unsteered `R` reference {cal.get('baseline_coherent_pooled')} coherent pooled, so the 90% rule was applied to "
                  f"{cal.get('rule_applied_to')}; s_max `+d_dig` = {cal['s_max'].get('+d_dig')} -> idea 1 strengths {cal['strengths'].get('+d_dig')}; "
                  f"`-v_axis`: no s passed (17/20 coherent at 0.025) -> the brief's fallback {cal['strengths'].get('-v_axis')} for idea 2 "
                  f"(idea 2's s_max = {cal['strengths'].get('-v_axis')[2]}). n32 = {json.load(open(f'{W}/stageb/n32.json'))['n32']:.3f}.")
    st += ex.get("status", [])
    notes["status"] = st
    notes["choices"] = draft["choices"] + ex.get("choices", [])
    notes["or_usage_before"] = 4.894588615
    try:
        k = os.environ["OPENROUTER_API_KEY"]
        req = urllib.request.Request("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"})
        notes["or_usage_after"] = json.load(urllib.request.urlopen(req, timeout=30))["data"].get("usage")
    except Exception as e:  # noqa: BLE001
        notes["or_usage_after"] = f"not read ({str(e)[:60]})"
    json.dump(notes, open(f"{W}/notes/readme_notes.json", "w"), indent=1)
    subprocess.run(["python3", f"{W}/driver/r02_report.py"], check=True)
    subprocess.run(["python3", f"{W}/driver/r02_readme.py"], check=True)


if __name__ == "__main__":
    main()
