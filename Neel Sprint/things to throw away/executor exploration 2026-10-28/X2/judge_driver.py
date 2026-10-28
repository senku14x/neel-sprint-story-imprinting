"""Judge driver shared by judge_X2.py and judge_X5.py (SYSTEM python3). Style judge = byte-identical sw003 style_judge_p.py.
Flow:
  --loop : while the generation client has not finished (its unfinished_*.json is older than this driver's start), prepare
           items from the rows that exist and judge them (style_judge_p.py skips (key, judge) pairs already judged); 90 s rounds.
  final  : judge everything that exists; then two retry passes (error rows are redone in the main file; rows that are
           non-error but miss a weighted score are redone into <judged>_retry.jsonl, which check/analysis merge).
Exit code: 0 = generation complete per the manifest AND every needed pair judged; 2 = everything that exists is judged but the
generation is incomplete; 1 = judging incomplete."""
import json, os, subprocess, sys, time

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import judge_common as JC  # noqa: E402


def log(**k):
    print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), **k)), flush=True)


def complete_pairs(paths):
    have = set()
    for p in paths:
        h, _ = JC.style_complete_pairs(p)
        have |= h
    return have


def style_pass(cfg, items_all, judged, retry, conc):
    """Judge items in reply/conv mode. Main file first; then items whose pairs are non-error but incomplete -> retry file."""
    inp = judged.replace(".jsonl", "_in.jsonl")
    JC.write_jsonl(inp, items_all)
    if items_all:
        JC.run_style(cfg["style_script"], inp, judged, cfg["mode"], conc)
    have = complete_pairs([judged, retry])
    nonerr = {(r["key"], r["judge"]) for r in JC.jsonl(judged) if not r.get("error")}
    redo = sorted({k for (k, j) in nonerr if (k, j) not in have})
    if redo:
        rin = retry.replace(".jsonl", "_in.jsonl")
        JC.write_jsonl(rin, [x for x in items_all if x["key"] in set(redo)])
        log(event="retry_incomplete_nonerror", n_keys=len(redo))
        JC.run_style(cfg["style_script"], rin, retry, cfg["mode"], conc)


def drive(cfg, loop, conc=64):
    """cfg: dict(name, style_script, mode, judged, retry, gen_path, unfinished_path, needed_keys(), items(), gen_complete(), extra_final())"""
    t_start = time.time()
    log(event="judge_start", part=cfg["name"], ledger_usd=round(JC.spent(), 3))
    if loop:
        while True:
            uf = cfg["unfinished_path"]
            finished = os.path.exists(uf) and os.path.getmtime(uf) > t_start
            items = cfg["items"]()
            have = complete_pairs([cfg["judged"], cfg["retry"]])
            todo = [x for x in items if any((x["key"], j) not in have for j in JC.JUDGES)]
            log(event="round", items=len(items), todo=len(todo), gen_finished=finished, ledger_usd=round(JC.spent(), 3))
            if todo:
                JC.write_jsonl(cfg["judged"].replace(".jsonl", "_in.jsonl"), todo)
                JC.run_style(cfg["style_script"], cfg["judged"].replace(".jsonl", "_in.jsonl"), cfg["judged"], cfg["mode"], conc)
            if finished:
                break
            time.sleep(90)
    for p in range(3):
        style_pass(cfg, cfg["items"](), cfg["judged"], cfg["retry"], conc if p == 0 else conc // 2)
    extra_ok = cfg["extra_final"]() if cfg.get("extra_final") else True
    need = cfg["needed_pairs"]()
    have = complete_pairs([cfg["judged"], cfg["retry"]])
    gen_ok = cfg["gen_complete"]()
    judged_ok = need <= have and extra_ok
    log(event="judge_end", part=cfg["name"], needed=len(need), have=len(need & have), gen_complete=gen_ok, extra_ok=extra_ok,
        ledger_usd=round(JC.spent(), 3), secs=round(time.time() - t_start))
    if judged_ok and gen_ok:
        log(event=f"JUDGE_{cfg['name']}_DONE"); return 0
    if judged_ok:
        log(event=f"JUDGE_{cfg['name']}_DONE_GEN_INCOMPLETE"); return 2
    log(event=f"JUDGE_{cfg['name']}_INCOMPLETE"); return 1


def run_check(script, items, env_extra=None):
    env = dict(os.environ, **(env_extra or {}))
    return subprocess.run([JC.PY, script] + items, env=env).returncode == 0
