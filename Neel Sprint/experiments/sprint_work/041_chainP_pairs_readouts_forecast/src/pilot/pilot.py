"""Chain P local pilot driver (box 1). PILOT_RULES.txt is the frozen protocol; this file only sequences it.
  python3 -I pilot.py keycheck                      GET /api/v1/key (ALT key, never printed): limit / usage / limit_remaining -> key_checks.jsonl;
                                                    exit 1 if limit_remaining < $40
  python3 -I pilot.py push                          rsync src/gen/ -> node /root/runs/sw041/pilot/gen_code/, pilot specs + jobs -> node gen/specs/;
                                                    compares node code hashes with /workspace
  python3 -I pilot.py pull                          rsync node /root/runs/sw041/pilot/{gen,logs}/ -> ROOT, then verify_manifest.py (must pass)
  python3 -I pilot.py convert <version>             gen job dirs pilot_<version>_* -> ROOT/runs/<version>_<corpus>[_codes]/ (convert.py)
  python3 -I pilot.py judge <run tag>               keycheck + cap check, then judge.py stories <tag> (templates S and F, both judges)
  python3 -I pilot.py gates <sel> <name>            analyze.py gates (rules v5) + text_diag + rescued / strict subsets + report
                                                    sel e.g. pf=v5_mainA,ch=v5_mainA,cf=v5_mirrorA,ph=v5_mirrorA
Outputs in ROOT = /workspace/runs_executor/sw041/pilot (runs/analysis/ for every table)."""
import collections, glob, hashlib, json, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
ROOT = os.environ.get("PILOT_ROOT", "/workspace/runs_executor/sw041/pilot")
BOX_SPECS, NODE_SPECS = "/workspace/runs_executor/sw041/gen/specs", "/root/runs/sw041/gen/specs"
NODE = "root@<box-ip>"; SSH = "ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=30"
NODE_PILOT = "/root/runs/sw041/pilot"
CAP, MIN_REMAINING = 4.00, 40.0
EST_PER_STORY = 0.0009 * 1.5   # screen v5: S glm .00035 + ds .00016, F glm .00026 + ds .00014 per story; x1.5 margin
PY = "/usr/bin/python3"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
now = lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def spent():
    return sum(float(json.loads(l).get("cost") or 0) for l in open(f"{ROOT}/spend.jsonl")) if os.path.exists(f"{ROOT}/spend.jsonl") else 0.0


def keycheck():
    import httpx
    k = None
    for line in open("/workspace/.env"):
        if line.startswith("OPENROUTER_API_KEY_ALT="):
            k = line.split("=", 1)[1].strip().strip('"').strip("'")
    assert k, "OPENROUTER_API_KEY_ALT missing"
    d = httpx.get("https://openrouter.ai/api/v1/key", headers={"Authorization": f"Bearer {k}"}, timeout=30).json().get("data", {})
    rec = dict(t=now(), limit=d.get("limit"), usage=d.get("usage"), limit_remaining=d.get("limit_remaining"), pilot_spent=round(spent(), 4))
    with open(f"{ROOT}/key_checks.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
    rem = rec["limit_remaining"]
    return rem is None or float(rem) >= MIN_REMAINING, rec


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"FAILED ({r.returncode}): {cmd}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def push():
    sh(f'{SSH} {NODE} "mkdir -p {NODE_PILOT}/gen_code {NODE_PILOT}/gen {NODE_PILOT}/logs {NODE_SPECS}"')
    sh(f'rsync -a --exclude __pycache__ -e "{SSH}" "{GEN}/" {NODE}:{NODE_PILOT}/gen_code/')
    files = sorted(glob.glob(f"{BOX_SPECS}/*pilot120*"))
    sh(f'rsync -a -e "{SSH}" ' + " ".join(f'"{p}"' for p in files) + f" {NODE}:{NODE_SPECS}/")
    names = ["gen_local.py", "texts.py", "launch.sh"]
    node = dict(l.split()[::-1] for l in sh(f'{SSH} {NODE} "cd {NODE_PILOT}/gen_code && sha256sum ' + " ".join(names) + '"').strip().splitlines())
    nspec = dict(l.split()[::-1] for l in sh(f'{SSH} {NODE} "cd {NODE_SPECS} && sha256sum ' +
                                               " ".join(os.path.basename(p) for p in files) + '"').strip().splitlines())
    bad = [n for n in names if node[n] != sha(f"{GEN}/{n}")] + [os.path.basename(p) for p in files if nspec[os.path.basename(p)] != sha(p)]
    print(json.dumps(dict(code={n: node[n][:16] for n in names}, specs={k: v[:16] for k, v in nspec.items()}, mismatch=bad)))
    if bad:
        sys.exit("MISMATCH after push")


def pull():
    sh(f'rsync -a -e "{SSH}" {NODE}:{NODE_PILOT}/gen {NODE}:{NODE_PILOT}/logs {ROOT}/')
    r = subprocess.run([PY, "-I", f"{GEN}/verify_manifest.py", f"{ROOT}/gen"], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-1000:])
    open(f"{ROOT}/verify_manifest_{now()}.txt", "w").write(r.stdout + r.stderr)
    if r.returncode:
        sys.exit("verify_manifest BLOCKED")


def convert(version):
    out = []
    for d in sorted(glob.glob(f"{ROOT}/gen/pilot_{version}_*")):
        if not os.path.isdir(d):
            continue
        job = os.path.basename(d)                                 # pilot_v5_mainA[_pf]
        corpus = job.split("_")[2]
        tag = job[len("pilot_"):]                                 # v5_mainA[_pf]
        man = [json.loads(l) for l in open(glob.glob(f"{d}/manifest_*.jsonl")[0])]
        assert any(m["kind"] == "end" and m["status"] == "ok" for m in man), f"{job}: no ok end record"
        specs = f"{BOX_SPECS}/specs_{corpus}_pilot120_{version}.jsonl"
        r = subprocess.run([PY, "-I", f"{HERE}/convert.py", d, specs, tag, "--root", ROOT], capture_output=True, text=True, check=True)
        out.append(json.loads(r.stdout))
    print(json.dumps(out, indent=1))


def judge(tag):
    n = sum(r["ok"] for r in jl(f"{ROOT}/runs/{tag}/records.jsonl"))
    est = EST_PER_STORY * n
    ok, rec = keycheck()
    if not ok:
        sys.exit(f"STOP: key limit_remaining {rec['limit_remaining']} < {MIN_REMAINING}")
    if spent() + est > CAP:
        sys.exit(f"STOP: pilot spent {spent():.4f} + estimate {est:.4f} > cap {CAP}")
    env = dict(os.environ, PILOT_ROOT=ROOT, CHAINP_JUDGE_CAP=str(CAP))
    s0 = spent()
    r = subprocess.run([PY, "-I", f"{HERE}/judge.py", "stories", tag], env=env, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    print(json.dumps(dict(tag=tag, stories=n, estimate=round(est, 4), batch_cost=round(spent() - s0, 4), pilot_spent=round(spent(), 4))))


# ------------------------------------------------------------------------------------------------ gates + report
def run_gates(sel, name):
    env = dict(os.environ, PILOT_ROOT=ROOT)
    s = ",".join(f"{c}={t}" for c, t in sel.items())
    r = subprocess.run([PY, "-I", f"{HERE}/analyze.py", "gates", s, name, "v5"], env=env, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    r = subprocess.run([PY, "-I", f"{HERE}/text_diag.py", s, name], env=env, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    return json.load(open(f"{ROOT}/runs/analysis/gates_{name}.json")), json.load(open(f"{ROOT}/runs/analysis/text_diag_{name}.json"))


def frozen_verdict(g):
    """PILOT_RULES §3: L+2 = analyze's all_pass_consensus (every gate blocking incl. G5, H10); L-2 = consensus G gates + G9 (no H10, R5)."""
    out = {}
    for corpus, c in g["corpora"].items():
        cons = {k: x["pass"] for k, x in c["by_judge"]["consensus"].items() if not k.startswith("R")}
        com = {k: x["pass"] for k, x in c["common"].items() if not k.startswith(("G10", "R"))}
        if corpus == "L-2":
            report_only = {k: com.pop(k) for k in list(com) if k.startswith("H10")}
            report_only["R5_line_ratio"] = c["common"]["R5_line_ratio"]["pass"]
        else:
            report_only = {}
        blocking = dict(cons, **com)
        out[corpus] = dict(verdict_pass=all(blocking.values()), failing_blocking=[k for k, v in blocking.items() if not v],
                           report_only_calls=report_only, single_judge_fails=c["fails_under_either_judge"],
                           analyze_all_pass_consensus=c["all_pass_consensus"])
    return out


FMT = re.compile(r"^stage2 format")


def check_counts(sel):
    """Per character: tries per stage, fail reasons (Chain P checks separated), drops by baseline / triggered, first-try passes."""
    out = {}
    for code, tag in sel.items():
        recs = [r for r in jl(f"{ROOT}/runs/{tag}/records.jsonl") if r["code"] == code]
        tries = [t for t in jl(f"{ROOT}/runs/{tag}/tries.jsonl") if t["code"] == code]
        t2 = [t for t in tries if t["stage"] == 2]
        fr = collections.Counter(t["fail"] for t in tries if t["fail"])
        fmt = sum(n for f, n in fr.items() if FMT.match(f))
        scr = {f.split(": ", 1)[1]: n for f, n in fr.items() if f.startswith("stage2 script form")}
        other = {f: n for f, n in fr.items() if not (FMT.match(f) or f.startswith("stage2 script form"))}
        drops = [r for r in recs if not r["ok"]]
        out[code] = dict(specs=len(recs), ok=len(recs) - len(drops), dropped=len(drops),
                         dropped_baseline=sum(not r["has_trigger"] for r in drops), dropped_triggered=sum(r["has_trigger"] for r in drops),
                         drop_ids=[r["spec_id"] for r in drops], drop_last_fail=[(r["fails"] or ["?"])[-1] for r in drops],
                         tries_stage1=sum(t["stage"] == 1 for t in tries), tries_stage2=len(t2),
                         stage2_format_fails=fmt, stage2_script_form_fails=scr, stage2_script_form_total=sum(scr.values()),
                         other_fail_reasons=dict(sorted(other.items(), key=lambda x: -x[1])),
                         stage1_first_try_pass=sum(1 for r in recs if r["tries1"] == 1 and r["dialogue"] is not None),
                         stage2_first_try_pass=sum(1 for r in recs if r["tries2"] == 1 and r["ok"]),
                         mean_tries_total=round(sum(r["tries1"] + r["tries2"] for r in recs) / max(1, len(recs)), 3),
                         story_words_mean=round(sum(r["story_words"] for r in recs if r["ok"]) / max(1, len(recs) - len(drops)), 1))
    return out


def timing(version):
    runs = sorted(glob.glob(f"{ROOT}/gen/run_pilot_{version}_*.json"))
    out = []
    for p in runs:
        r = json.load(open(p))
        chunks = r["chunks"]
        big = [c for c in chunks if c["n"] >= 200]
        tags = os.path.basename(p)[4:].rsplit("_shard", 1)[0].split("+")
        mans = [m for t in tags for m in jl(glob.glob(f"{ROOT}/gen/{t}/manifest_*.jsonl")[0])]
        st = [m for m in mans if m["kind"] == "start"][-1]; en = [m for m in mans if m["kind"] == "end" and m["run_id"] == st["run_id"]][-1]
        t0 = time.mktime(time.strptime(st["date_u"], "%Y-%m-%dT%H:%M:%SZ")); t1 = time.mktime(time.strptime(en["date_u"], "%Y-%m-%dT%H:%M:%SZ"))
        recs = [x for t in tags for x in jl(f"{ROOT}/runs/{t[len('pilot_'):]}/records.jsonl")]
        n_specs = len(recs); n_ok = sum(x["ok"] for x in recs)
        tok_spec = r["out_tokens"] / max(1, n_specs)
        steady = max((c["tok_s"] for c in big), default=r["tok_s"])
        est = {}
        for lab, ts in [("steady_largest_chunk_tok_s", steady), ("pilot_overall_tok_s", r["tok_s"])]:
            gen_h = 8000 * tok_spec / ts / 3600
            est[lab] = dict(tok_s=ts, gen_h_per_8000_specs=round(gen_h, 2), wall_h_incl_load=round(gen_h + r["load_s"] / 3600, 2))
        out.append(dict(run=os.path.basename(p), jobs=tags, gpu=[g.get("name") + " #" + g.get("index", "") for g in st["gpu"].get("gpus", [])],
                        process_wall_min=round((t1 - t0) / 60, 1), gpu_minutes=round((t1 - t0) / 60, 1), load_s=r["load_s"],
                        generate_wall_s=r["gen_wall_s"], out_tokens=r["out_tokens"], tok_s_overall=r["tok_s"], specs=n_specs, ok=n_ok,
                        out_tokens_per_spec=round(tok_spec, 1), stories_per_hour_generate=round(3600 * n_ok / r["gen_wall_s"], 1),
                        stories_per_hour_process=round(3600 * n_ok / max(1, t1 - t0), 1),
                        chunks=[dict(round=c["round"], n=c["n"], stages=c["stages"], wall_s=c["wall_s"], tok_s=c["tok_s"]) for c in chunks],
                        full_run_estimate_32k_on_4_gpus=est))
    return out


def quotes(sel, seed=41121):
    rng = random.Random(seed)
    out = {}
    for code, tag in sel.items():
        recs = sorted([r for r in jl(f"{ROOT}/runs/{tag}/records.jsonl") if r["code"] == code and r["ok"]], key=lambda r: r["spec_id"])
        out[code] = [dict(key=r.get("key"), spec_id=r["spec_id"], has_trigger=r["has_trigger"], helper=r["helper"], seeker=r["seeker"], story=r["story"])
                     for r in rng.sample(recs, 2)]
    return out


def gates(sel_s, name):
    sel = dict(x.split("=") for x in sel_s.split(","))
    g, td = run_gates(sel, name)
    smp = json.load(open(f"{ROOT}/sample_pilot120.json"))
    resc = set(smp["rescued_ids"]); allids = {s for v in smp["spec_ids"].values() for s in v}
    ids_dir = f"{ROOT}/runs/analysis"
    json.dump(sorted(resc), open(f"{ids_dir}/ids_rescued.json", "w")); json.dump(sorted(allids - resc), open(f"{ids_dir}/ids_strict.json", "w"))
    sub = {}
    for sname in ("rescued", "strict"):
        for t in sorted(set(sel.values())):
            subprocess.run([PY, "-I", f"{HERE}/convert.py", "--subset", t, sname, f"{ids_dir}/ids_{sname}.json", "--root", ROOT],
                           capture_output=True, text=True, check=True)
        ssel = {c: f"{t}_{sname}" for c, t in sel.items()}
        sg, _ = run_gates(ssel, f"{name}_{sname}")
        sub[sname] = dict(gates_md=f"{ROOT}/runs/analysis/gates_{name}_{sname}.md", verdict=frozen_verdict(sg),
                          n_per_char={c: sg["characters"][c]["n_specs"] for c in sel})
    rep = dict(name=name, written=now(), selection=sel, verdict=frozen_verdict(g), gates_md=f"{ROOT}/runs/analysis/gates_{name}.md",
               subsets=sub, checks=check_counts(sel), text_diag={k: dict(n_leak_stories=v["n_leak_stories"], n_comment_stories=v["n_comment_stories"],
                                                                          n_triggered=v["n_triggered"], summary_like=len(v["summary_like_accepted"]),
                                                                          stage2_format_fails=v["stage2_format_fails"], stage2_tries=v["stage2_tries"])
                                                                for k, v in td.items()},
               exposure={c: dict(words_char_lines_per_story=g["characters"][c]["words_total_per_story"], words_per_line=g["characters"][c]["words_per_line"],
                                 story_words=g["characters"][c]["story_words"]) for c in sel},
               timing=timing(name.split("_")[-1] if name.startswith("pilot_") else "v5"), spend=dict(pilot_spent=round(spent(), 4)))
    json.dump(rep, open(f"{ROOT}/runs/analysis/report_{name}.json", "w"), indent=1)
    json.dump(quotes(sel), open(f"{ROOT}/runs/analysis/quotes_{name}.json", "w"), indent=1, ensure_ascii=False)
    print(open(f"{ROOT}/runs/analysis/gates_{name}.md").read())
    print(json.dumps({k: v for k, v in rep.items() if k not in ("timing",)}, indent=1)[:12000])
    print(json.dumps(rep["timing"], indent=1)[:4000])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "keycheck":
        ok, _ = keycheck(); sys.exit(0 if ok else 1)
    elif cmd == "push":
        push()
    elif cmd == "pull":
        pull()
    elif cmd == "convert":
        convert(sys.argv[2])
    elif cmd == "judge":
        judge(sys.argv[2])
    elif cmd == "gates":
        gates(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
