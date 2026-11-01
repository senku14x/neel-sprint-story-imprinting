"""Drives all remaining Bloom batches (Amendment 5). One long-running process; log in /workspace/logs/scheduler.log.

Cells (7): for hb_dc_s0 and hc_db_s0: main (MAIN, no system prompt), flip (MAIN, dismissive), T=0.7 (no system
prompt); for the untrained model: main. Batches of 25 conversations (5 per scenario).
  Phase 1: every cell to 75 (round-robin: lowest count first; main, flip, T=0.7 order on ties).
  Phase 2: the trained models' main cells to 100 (the GPT-4.1 calibration).
  Phase 3: equal rounds of 25 across all seven cells.
No batch starts after the cutoff (20:15 UTC), or when spend + batch cost would pass $86; when a full round will not
fit, one last equal round of the largest size that fits (>= 5 per cell). At the cutoff, if a cell is short of 75
because time ran out, the pod deadline is extended once by 90 minutes and phase-1 (then phase-2) batches continue
until 45 minutes before the new deadline.
GPT-4.1 requests in flight per process start at 2 and move 2 -> 4 -> 8 when 429s are rare, back when they return.
GLM-only side jobs (story check, single-turn evals) start the first time each model is served.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import time
from pathlib import Path

from common import RUNS, SCRATCH

CODE = Path(__file__).resolve().parent
LOG = Path("/workspace/logs/scheduler.log")
STATE = RUNS / "scheduler_state.json"
MAIN = json.load(open(RUNS / "main_setting.json"))["main_setting"]
PORTS = {0: 8000, 1: 8010}
CAP, JUDGE_RESERVE = 86.0, 4.0
TODAY = dt.datetime.now(dt.timezone.utc).date()
CUTOFF = dt.datetime.combine(TODAY, dt.time(20, 15), dt.timezone.utc)
DEADLINE = dt.datetime.combine(TODAY, dt.time(21, 0), dt.timezone.utc)
EXTENSION = dt.timedelta(minutes=90)
WRAPUP = dt.timedelta(minutes=45)
MODELS = ["hc_db_s0", "hb_dc_s0", "base"]
KINDS = [(MAIN, "none"), (MAIN, "dismissive"), ("T07", "none")]
CELLS = [(m, s, y) for m in MODELS for (s, y) in (KINDS if m != "base" else KINDS[:1])]
BATCH = 25
PY_BLOOM = "/workspace/venvs/bloom/bin/python"


def now():
    return dt.datetime.now(dt.timezone.utc)


def log(msg):
    line = f"{now():%H:%M:%S} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def tag(c, suffix=""):
    return "__".join(c) + (f"__{suffix}" if suffix else "")


def completed(c):
    n = 0
    for p in (RUNS / "bloom").glob(f"{tag(c)}*.jsonl"):
        if re.fullmatch(re.escape(tag(c)) + r"(__r\d+)?", p.stem):
            n += sum(1 for _ in open(p))
    return n


def running_batches():
    """Bloom batches in flight (from the process table): list of (cell, n, suffix, gpu_port)."""
    out = []
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout.splitlines()
    for line in ps:
        m = re.match(r"bash run_eval\.sh (\S+) (\d+) (\S+) (\S+) (\d+)(?: (\S+))?$", line.strip())
        if m:
            cell = (m.group(1), m.group(3), m.group(4))
            out.append((cell, int(m.group(5)) * 5, m.group(6) or "", int(m.group(2))))
    return out


def served(port):
    try:
        r = subprocess.run(["curl", "-sf", f"localhost:{port}/v1/models"], capture_output=True, text=True, timeout=10)
        d = json.loads(r.stdout)
        return Path(d["data"][0]["root"]).name
    except Exception:
        return None


def spend():
    r = subprocess.run([PY_BLOOM, "-c", "from llm import key_usage; print(key_usage()['usage'])"], cwd=CODE,
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def cost_per_conv():
    r = subprocess.run([PY_BLOOM, "-c", "from budget import cost_per_conv; print(cost_per_conv())"], cwd=CODE,
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.05


def next_suffix(c, inflight_suffixes):
    if not (RUNS / "bloom" / f"{tag(c)}.jsonl").exists() and "" not in inflight_suffixes:
        return ""
    k = 2
    while (RUNS / "bloom" / f"{tag(c, f'r{k}')}.jsonl").exists() or f"r{k}" in inflight_suffixes:
        k += 1
    return f"r{k}"


def targets(counts):
    """Per-cell target for the current phase, given completed + in-flight counts."""
    trained_main = {c for c in CELLS if c[0] != "base" and c[1:] == (MAIN, "none")}
    if any(v < 75 for v in counts.values()):
        return 1, {c: 75 for c in CELLS}
    if any(counts[c] < 100 for c in trained_main):
        return 2, {c: (100 if c in trained_main else 75) for c in CELLS}
    base_t = {c: (100 if c in trained_main else 75) for c in CELLS}
    j = min((counts[c] - base_t[c]) // BATCH for c in CELLS) + 1
    return 3, {c: base_t[c] + BATCH * j for c in CELLS}


def retries_in(logfile):
    try:
        txt = open(logfile, errors="ignore").read()
    except FileNotFoundError:
        return 0, []
    n = len(re.findall(r"-> \S+ retry \d+", txt))
    bodies = re.findall(r"-> \S+ retry \d+ \(retrying in [\d,]+ seconds\)(.{0,600})", txt)
    return n, bodies


def record_429(logfile, conv):
    n, bodies = retries_in(logfile)
    kinds = {}
    for b in bodies:
        key = re.sub(r"\d+", "N", b)[:160]
        kinds.setdefault(key, b)
    path = RUNS / "ratelimit_429.jsonl"
    seen = set()
    if path.exists():
        seen = {json.loads(l)["kind"] for l in open(path)}
    with open(path, "a") as f:
        for k, b in kinds.items():
            if k not in seen:
                f.write(json.dumps({"t": f"{now():%H:%M:%S}", "kind": k, "body": b.strip(), "log": str(logfile)}) + "\n")
    return n / max(conv, 1)


def side_jobs(model, port):
    """GLM-only checks the first time a model is served (story check, single-turn evals)."""
    jobs = [("story_check.py", MAIN)] + [("single_turn.py", MAIN)] + ([("single_turn.py", "T07")] if model != "base" else [])
    for script, samp in jobs:
        sub = "story" if script == "story_check.py" else "single_turn"
        if (RUNS / sub / f"{model}__{samp}_summary.json").exists():
            continue
        name = f"{sub}_{model}_{samp}"
        ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout.splitlines()
        if any(script in l and f"--model-tag {model} " in l and f"--sampling {samp} " in l for l in ps):
            continue
        log(f"side job {script} {model} {samp} on port {port}")
        subprocess.Popen(f"nohup {PY_BLOOM} {script} --model-tag {model} --sampling {samp} --n 50 "
                         f"--base-url http://localhost:{port}/v1 > /workspace/logs/{name}.log 2>&1 &",
                         shell=True, cwd=CODE)


def swap(gpu, model):
    port = PORTS[gpu]
    log(f"swap GPU {gpu} (port {port}) -> {model}")
    subprocess.run(["bash", "stop_server.sh", str(port)], cwd=CODE)
    r = subprocess.run(["bash", "serve.sh", str(SCRATCH / "merged" / model), str(gpu), str(port), f"{model}_gpu{gpu}"],
                       cwd=CODE, capture_output=True, text=True)
    log(f"serve {model} on GPU {gpu}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]}")
    return served(port) == model


def extend_deadline():
    new = DEADLINE + EXTENSION
    secs = int((new - now()).total_seconds())
    pod = os.environ["RUNPOD_POD_ID"]
    subprocess.run(["tmux", "kill-session", "-t", "deadline"])
    subprocess.run(["tmux", "new", "-d", "-s", "deadline", f"sleep {secs}; runpodctl pod stop {pod}"])
    json.dump({"extended_at": f"{now():%H:%M:%S}", "new_deadline_utc": f"{new:%H:%M}",
               "reason": "a cell was short of 75 conversations because time ran out (Amendment 5, point 5)"},
              open(RUNS / "deadline_extension.json", "w"), indent=1)
    log(f"DEADLINE EXTENDED to {new:%H:%M} UTC")
    return new


def main():
    level = int(os.environ.get("SI36_AUDITOR_CONN", "2"))
    extended, final_round_size, stop_new = None, None, False
    procs = {}  # tag -> (Popen, cell, n, logfile, gpu)
    done_counts_hist = []
    log(f"scheduler start; main setting {MAIN}; cells {len(CELLS)}; cutoff {CUTOFF:%H:%M}; cap ${CAP}")
    while True:
        # reap finished batches
        for t, (p, cell, n, lf, gpu) in list(procs.items()):
            if p.poll() is not None:
                rate = record_429(lf, n)
                ok = (RUNS / "bloom" / f"{t}.jsonl").exists()
                log(f"batch done {t} rc={p.returncode} ok={ok} 429/conv={rate:.2f} level={level}")
                if rate < 0.2 and level < 8:
                    level *= 2; log(f"429s rare -> requests in flight per process {level}")
                elif rate > 1.0 and level > 1:
                    level //= 2; log(f"429s frequent -> requests in flight per process {level}")
                del procs[t]
        inflight = running_batches()
        counts = {c: completed(c) + sum(n for cc, n, _, _ in inflight if cc == c) for c in CELLS}
        done = {c: completed(c) for c in CELLS}
        phase, tgt = targets(counts)
        t_now = now()
        served_now = {g: served(PORTS[g]) for g in PORTS}
        state = {"t": f"{t_now:%H:%M:%S}", "phase": phase, "completed": {tag(c): done[c] for c in CELLS},
                 "with_inflight": {tag(c): counts[c] for c in CELLS}, "targets": {tag(c): tgt[c] for c in CELLS},
                 "inflight": [tag(c, s) for c, _, s, _ in inflight], "served": served_now, "level": level,
                 "extended_deadline": f"{extended:%H:%M}" if extended else None}
        json.dump(state, open(STATE, "w"), indent=1)
        done_counts_hist.append((time.time(), sum(done.values())))
        for g, m in served_now.items():
            if m:
                side_jobs(m, PORTS[g])
        # time rules
        cutoff = CUTOFF if not extended else extended - WRAPUP
        if t_now >= CUTOFF and not extended and any(counts[c] < 75 for c in CELLS) and final_round_size is None:
            extended = extend_deadline()
            cutoff = extended - WRAPUP
        if t_now >= cutoff:
            stop_new = True
        if stop_new:
            if not inflight and not procs:
                log("no new batches (time or money); nothing in flight; scheduler exits")
                break
            time.sleep(30); continue
        if extended and phase == 3:
            stop_new = True; continue  # the extension only finishes the first 75s and the calibration
        # money rule
        cpc = cost_per_conv()
        sp = spend()
        if sp is None:
            time.sleep(30); continue
        eligible = [c for c in CELLS if counts[c] < tgt[c]]
        if final_round_size is None and eligible and sp + BATCH * cpc > CAP:
            size = int((CAP - sp) / (cpc * len(eligible))) // 5 * 5
            if size >= 5:
                final_round_size = size
                log(f"money: a full batch no longer fits under ${CAP} (spent ${sp:.2f}); last equal round of {size} per cell")
            else:
                log(f"money: spent ${sp:.2f}; not even 5 per cell fits; no new batches"); stop_new = True; continue
        # launch: one batch per GPU at a time
        busy = {g for (_, _, _, port) in inflight for g in PORTS if PORTS[g] == port}
        for g in PORTS:
            if g in busy or (g == 0 and served_now.get(0) is None and not os.path.exists(SCRATCH / "merged" / "hb_dc_s0" / "merge_meta.json")):
                continue
            if g == 0 and served_now.get(0) is None:
                continue  # GPU 0 comes in when post_train.sh has served hb_dc_s0
            m = served_now.get(g)
            mine = [c for c in eligible if c[0] == m]
            if not mine:
                post_train_alive = "post_train.sh" in subprocess.run(["ps", "-eo", "args"], capture_output=True,
                                                                      text=True).stdout
                others = {mm for mm in MODELS if mm not in served_now.values()
                          and (SCRATCH / "merged" / mm / "merge_meta.json").exists()
                          and not (mm == "hb_dc_s0" and post_train_alive)}
                want = [c for c in eligible if c[0] in others]
                if not want:
                    continue
                # swap to the not-served model with the most remaining eligible work
                rem = {mm: sum(tgt[c] - counts[c] for c in want if c[0] == mm) for mm in others}
                mm = max(rem, key=rem.get)
                if swap(g, mm):
                    served_now[g] = mm
                    mine = [c for c in eligible if c[0] == mm]
                else:
                    log(f"swap of GPU {g} to {mm} failed"); continue
            mine.sort(key=lambda c: (counts[c], KINDS.index(c[1:]) if c[0] != "base" else 0))
            c = mine[0]
            size = final_round_size or BATCH
            size = min(size, tgt[c] - counts[c]) if final_round_size is None else size
            nps = max(1, size // 5)
            suf = next_suffix(c, [s for cc, _, s, _ in inflight if cc == c])
            t = tag(c, suf)
            lf = f"/workspace/logs/eval_{t}.log"
            env = {**os.environ, "SI36_RUN_CAP": str(CAP), "SI36_AUDITOR_CONN": str(level), "SI36_MAX_SAMPLES": "10",
                   "SI36_AUDITOR": "openai/gpt-4.1"}
            p = subprocess.Popen(["bash", "run_eval.sh", c[0], str(PORTS[g]), c[1], c[2], str(nps)] + ([suf] if suf else []),
                                 cwd=CODE, env=env, stdout=open(lf, "w"), stderr=subprocess.STDOUT)
            procs[t] = (p, c, nps * 5, lf, g)
            counts[c] += nps * 5
            inflight.append((c, nps * 5, suf, PORTS[g]))
            log(f"launch {t} ({nps * 5}) on GPU {g}; phase {phase}; spend ${sp:.2f}; level {level}")
            if final_round_size is not None and all(counts[cc] >= tgt[cc] for cc in CELLS):
                stop_new = True
        time.sleep(30)


if __name__ == "__main__":
    main()
