#!/usr/bin/env python3
"""Overnight judge runner (infra 2, executor-9). System python3; CPU only; never prints the key.

  python3 judge_run.py --exp sw0NN --rubric habit|reply5|hist|style|custom --in IN.jsonl --out OUT.jsonl
         [--models both|glm|ds] [--sample-frac 0.2 --strata-field cell --always-field disagree --seed 0]
         [--concurrency 48] [--user-map MAP.json --user-map-key "{model}|{cell}|{sid}"]
         [--style-mode reply|conv|story] [--template T.txt --fields a,b --ranges a:0-10]
         [--also-touch /workspace/runs_executor/sw0NN/JUDGED_<part>] [--limit N] [--dry-run]

Input: one JSON row per item with a unique "key" (assert; put exp, readout, arm, model, script, sample in it) and the
rubric's fields: habit / reply5 -> user, text (or --user-map); hist -> messages; style -> messages (or story fields);
custom -> the template's {placeholders}.
Selection (manifest): all rows, or with --sample-frac a seeded random fraction of each stratum (--strata-field; k =
max(1, round(frac * n)) per stratum, rng = Random(f"{seed}|{stratum}") over the stratum's sorted keys) plus every row whose
--always-field is truthy. --always-field disagree is computed from labels.disagree(row[--text-field]) when rows lack it.
The selected keys are frozen in OUT.manifest.json; a rerun with a different selection aborts (exit 2) unless --new-manifest.
Output: OUT.jsonl, one record per (key, judge), appended and flushed per call; rerun = resume (valid (key, judge) pairs are
skipped; error rows are retried). Two passes per run (the second retries what the first left invalid).
Markers:  OUT.DONE          only when EVERY manifest key has a valid record from EVERY requested model (exit 0); also
                            touches each --also-touch path.
          OUT.NEEDS_REJUDGE on a 402 / credit-limit / auth stop (exit 3): no crash, what is done is kept; finish the analysis
                            with STRICT + lexicon and rerun the same command later to fill the rest.
          exit 1: incomplete for other reasons (persistent parse / transport errors) -> rerun resumes.
"""
import argparse, asyncio, hashlib, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge_lib as JL  # noqa: E402
import labels as LB  # noqa: E402


def parse_ranges(s):
    out = {}
    for part in (s or "").split(","):
        if part.strip():
            k, r = part.split(":"); lo, hi = r.split("-"); out[k.strip()] = (int(lo), int(hi))
    return out


def load_rows(a):
    rows = JL.read_jsonl(a.inp)
    assert rows, f"no rows in {a.inp}"
    keys = [r.get("key") for r in rows]
    assert all(isinstance(k, str) and k for k in keys), "every input row needs a non-empty string 'key'"
    seen, dups = set(), []
    for k in keys:
        if k in seen:
            dups.append(k)
        seen.add(k)
    assert not dups, f"DUPLICATE judge-input keys ({len(dups)}), e.g. {sorted(set(dups))[:5]}"
    if a.user_map:
        um = json.load(open(a.user_map))
        for r in rows:
            if "user" not in r:
                r["user"] = um[a.user_map_key.format(**r)]
    if a.limit:
        rows = rows[:a.limit]
    lacking = sum(1 for k in keys if a.exp not in k)
    if lacking:
        print(f"WARNING: {lacking}/{len(keys)} keys do not contain the experiment id {a.exp!r} (conventions: put exp, readout, "
              f"arm, model, script, sample in every key)", flush=True)
    return rows


def select(rows, a):
    if not a.sample_frac:
        return [r["key"] for r in rows]
    assert a.strata_field, "--sample-frac needs --strata-field"
    strata = {}
    for r in rows:
        assert a.strata_field in r, f"row {r['key']} lacks strata field {a.strata_field}"
        strata.setdefault(str(r[a.strata_field]), []).append(r["key"])
    pick = set()
    for s, ks in strata.items():
        ks = sorted(ks)
        k = max(1, int(round(a.sample_frac * len(ks) + 1e-9)))
        pick.update(random.Random(f"{a.seed}|{s}").sample(ks, min(k, len(ks))))
    n_always = 0
    if a.always_field:
        for r in rows:
            v = r.get(a.always_field)
            if v is None and a.always_field == "disagree":
                v = LB.disagree(r.get(a.text_field) or "")
            if v:
                n_always += 1; pick.add(r["key"])
    print(f"selection: {len(pick)}/{len(rows)} rows ({len(strata)} strata, frac {a.sample_frac}, always-field "
          f"{a.always_field!r} true on {n_always})", flush=True)
    return [r["key"] for r in rows if r["key"] in pick]


def manifest_for(a, keys, models, rubric):
    sha = hashlib.sha256("\n".join(keys).encode()).hexdigest()[:16]
    return dict(exp=a.exp, rubric=rubric.name, rubric_source=rubric.source, fields=rubric.fields, models=models, inp=os.path.abspath(a.inp),
                n_selected=len(keys), sample_frac=a.sample_frac, strata_field=a.strata_field, always_field=a.always_field,
                seed=a.seed, style_mode=a.style_mode if rubric.name == "style" else None, keys_sha=sha, keys=keys)


def status(out, keys, models, fields):
    ok = JL.valid_pairs(out, fields)
    miss = [(k, m) for k in keys for m in models if (k, m) not in ok]
    return ok, miss


def board_note(a, result, st="note"):
    b = f"{HERE}/board.py"
    if a.no_board or not os.path.exists(b):
        return
    try:
        import subprocess
        subprocess.run([sys.executable, b, "event", "--job", f"judge/{a.exp}/{os.path.basename(a.out)}", "--exp", a.exp,
                        "--part", a.part or "judge", "--status", st, "--out", os.path.abspath(a.out), "--result", result[:300]],
                       timeout=60, capture_output=True)
    except Exception:  # noqa: BLE001  (the board is best-effort; judging never fails because of it)
        pass


async def run(a, rows_by_key, todo, rubric, models):
    J = JL.Judger(a.exp, timeout=a.timeout, spend_log=a.spend_log)
    f = open(a.out, "a")
    if f.tell() > 0:
        with open(a.out, "rb") as g:
            g.seek(-1, 2)
            if g.read(1) != b"\n":
                f.write("\n")   # a torn last line (killed mid-write) must not swallow the next record
    t0 = time.time(); n_done = [0]; n_bad = [0]
    queues = {m: asyncio.Queue() for m in models}
    for k, m in todo:
        queues[m].put_nowait(k)

    async def worker(m):
        q = queues[m]
        while not q.empty() and not J.stop_reason:
            k = q.get_nowait()
            row = rows_by_key[k]
            try:
                rec = await J.judge(rubric, m, row)
            except JL.BudgetStop:
                return
            except Exception as e:  # noqa: BLE001  (one bad row never kills the batch; written as an error row, retried later)
                rec = dict(error=f"exception: {e!r}"[:300])
            rec = dict(key=k, judge=m, judge_model=JL.JUDGE_CFG[m]["model"], rubric=rubric.name, exp=a.exp, t=time.time(), **rec)
            f.write(json.dumps(rec) + "\n"); f.flush()
            n_done[0] += 1
            if not JL.record_valid(rec, rubric.fields):
                n_bad[0] += 1

    async def progress():
        while True:
            await asyncio.sleep(a.progress_every)
            el = max(1e-6, time.time() - t0)
            print(json.dumps(dict(t=time.strftime("%H:%M:%S", time.gmtime()), exp=a.exp, rubric=rubric.name, done=n_done[0],
                                  of=len(todo), invalid=n_bad[0], calls_per_min=round(60 * J.n_ok / el, 1), http_err=J.n_http_err,
                                  timeouts=J.n_timeout, retries=J.n_retry, spend=round(J.cost, 4))), flush=True)
    ptask = asyncio.create_task(progress())
    await asyncio.gather(*[worker(m) for m in models for _ in range(min(a.concurrency, max(1, sum(1 for _, mm in todo if mm == m))))])
    ptask.cancel()
    f.close()
    el = time.time() - t0
    stats = dict(calls_ok=J.n_ok, calls_per_min=round(60 * J.n_ok / max(el, 1e-6), 1), secs=round(el, 1), spend=round(J.cost, 4),
                 written=n_done[0], invalid=n_bad[0], http_err=J.n_http_err, timeouts=J.n_timeout, retries=J.n_retry)
    stop = J.stop_reason
    await J.close()
    return stats, stop


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exp", required=True); ap.add_argument("--rubric", required=True, choices=["habit", "reply5", "hist", "style", "custom"])
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--models", default="both", choices=sorted(JL.MODELS)); ap.add_argument("--concurrency", type=int, default=48)
    ap.add_argument("--sample-frac", type=float, default=0.0); ap.add_argument("--strata-field", default=None)
    ap.add_argument("--always-field", default=None); ap.add_argument("--text-field", default="text"); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--user-map", default=None); ap.add_argument("--user-map-key", default="{model}|{cell}|{sid}")
    ap.add_argument("--style-mode", default="reply", choices=["reply", "conv", "story"])
    ap.add_argument("--template", default=None); ap.add_argument("--fields", default=None); ap.add_argument("--ranges", default=None)
    ap.add_argument("--also-touch", action="append", default=[]); ap.add_argument("--part", default=None)
    ap.add_argument("--timeout", type=float, default=180.0); ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--progress-every", type=float, default=30.0); ap.add_argument("--spend-log", default=None)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--new-manifest", action="store_true"); ap.add_argument("--no-board", action="store_true")
    a = ap.parse_args()
    assert a.concurrency >= 1
    if a.concurrency < 48:
        print(f"note: concurrency {a.concurrency} < 48 (the overnight policy asks for >= 48 per judge model)", flush=True)
    rubric = JL.make_rubric(a.rubric, style_mode=a.style_mode, template=a.template,
                            fields=[x.strip() for x in a.fields.split(",")] if a.fields else None, ranges=parse_ranges(a.ranges))
    models = JL.MODELS[a.models]
    rows = load_rows(a)
    for r in rows:
        rubric.check_row(r)
    keys = select(rows, a)
    by_key = {r["key"]: r for r in rows}
    man = manifest_for(a, keys, models, rubric)
    mp = a.out + ".manifest.json"
    if os.path.exists(mp) and not a.new_manifest:
        old = json.load(open(mp))
        same = all(old.get(k) == man[k] for k in ("keys_sha", "rubric", "models", "fields"))
        if not same:
            print(f"ABORT: {mp} exists with a different selection / rubric / models (old sha {old.get('keys_sha')}, new "
                  f"{man['keys_sha']}). Use another --out, or --new-manifest if the change is intended.", flush=True)
            sys.exit(2)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if not a.dry_run:
        json.dump(dict(man, created=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())), open(mp + ".tmp", "w"), indent=0)
        os.replace(mp + ".tmp", mp)
    ok, miss = status(a.out, keys, models, rubric.fields)
    print(f"{a.exp} {rubric.name}: {len(keys)} keys x {len(models)} models; {len(keys) * len(models) - len(miss)} valid, "
          f"{len(miss)} to judge; concurrency {a.concurrency}/model; out {a.out}", flush=True)
    if a.dry_run:
        return 0
    allstats, stop = [], None
    if miss:
        board_note(a, f"judging {rubric.name}: {len(miss)} calls to make ({len(keys)} keys x {models})")
    for p in range(a.passes):
        if not miss:
            break
        stats, stop = asyncio.run(run(a, by_key, miss, rubric, models))
        allstats.append(stats)
        print(f"pass {p + 1}: {json.dumps(stats)}", flush=True)
        ok, miss = status(a.out, keys, models, rubric.fields)
        if stop:
            break
    summ = dict(exp=a.exp, rubric=rubric.name, models=models, expected=len(keys) * len(models), valid=len(keys) * len(models) - len(miss),
                missing=len(miss), keys_sha=man["keys_sha"], passes=allstats, t=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    if not miss:
        with open(a.out + ".DONE.tmp", "w") as g:
            json.dump(summ, g)
        os.replace(a.out + ".DONE.tmp", a.out + ".DONE")
        if os.path.exists(a.out + ".NEEDS_REJUDGE"):
            os.replace(a.out + ".NEEDS_REJUDGE", a.out + ".NEEDS_REJUDGE.resolved")
        for t in a.also_touch:
            os.makedirs(os.path.dirname(os.path.abspath(t)), exist_ok=True)
            with open(t, "w") as g:
                g.write(f"{a.out} DONE {summ['t']} valid={summ['valid']}/{summ['expected']}\n")
        cpm = allstats[-1]["calls_per_min"] if allstats else 0
        board_note(a, f"judged {rubric.name} {summ['valid']}/{summ['expected']} (DONE), {cpm} calls/min, "
                      f"${sum(s['spend'] for s in allstats):.3f}")
        print(f"DONE {summ['valid']}/{summ['expected']} -> {a.out}.DONE", flush=True)
        return 0
    if stop:
        with open(a.out + ".NEEDS_REJUDGE", "w") as g:
            json.dump(dict(summ, reason=stop, missing_examples=miss[:10]), g)
        board_note(a, f"BUDGET/AUTH STOP judging {rubric.name}: {summ['valid']}/{summ['expected']} valid; NEEDS_REJUDGE written")
        print(f"NEEDS_REJUDGE ({stop}); {summ['valid']}/{summ['expected']} valid -> {a.out}.NEEDS_REJUDGE", flush=True)
        return 3
    board_note(a, f"judging {rubric.name} INCOMPLETE {summ['valid']}/{summ['expected']} after {a.passes} passes; rerun resumes")
    print(f"INCOMPLETE {summ['valid']}/{summ['expected']}; e.g. {miss[:5]} (rerun the same command to resume)", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
