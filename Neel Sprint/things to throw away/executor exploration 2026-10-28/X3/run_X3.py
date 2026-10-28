"""X3 client of the wave-2 vLLM server (stdlib only; any python). One stage per invocation.

  python3 run_X3.py --stage a  --deadline 2026-10-28T12:40:00Z            # arm a: 9,600 requests (8 models)
  python3 run_X3.py --stage b1 --deadline ...                            # arm b GPU extension: 2,000 requests (hsA0, hsB0)
  python3 run_X3.py --stage a --smoke                                    # 16 hand-read requests -> out/smoke_a.jsonl (not counted)
  python3 run_X3.py --stage a --check                                    # completeness vs the manifest only (no requests)

Requests: POST {server}/completions with the prompt as a LIST OF TOKEN IDS rendered by build_X3.py (010's code path, verified
token-identical to sw001's p1_opener jobs), the served adapter name as "model", common_x3.SAMPLER (T 0.7, top_p 1, top_k 0,
min_p 0, no penalties, 48 tokens, stop on <|im_end|>, skip_special_tokens) and the item's seed (independent of the model).
Rules (server contract, design_spec §0, mistakes.md 27 Oct):
  - <= --inflight (48) requests in flight; after --deadline no new request is submitted, in-flight ones are awaited, and the
    unfinished keys are written to out/unfinished_<stage>.json (exit 3);
  - resumable: a key is done when out/gen_<stage>.jsonl holds a valid row for it (HTTP 200, the requested model echoed,
    finish in {stop, length}, usage.prompt_tokens == len(ids)). An empty continuation is retried once, then kept as
    empty=true (a seeded empty reply reproduces; never sent to a judge);
  - completeness is computed from out/manifest_<stage>.json's expected keys, never from the outputs; out/DONE_<stage> is
    written only when every expected key has a valid row; a missing output file counts as zero rows.
  - before sending anything, every model the stage needs must be listed by GET {server}/models (else exit 2)."""
import argparse, datetime as dt, json, os, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def parse_deadline(s):
    d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    assert d.tzinfo is not None, "deadline must carry a timezone (use ...Z)"
    return d


def http(url, body=None, timeout=600):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="GET" if body is None else "POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def load_manifest(stage, out_dir):
    man = json.load(open(f"{out_dir}/manifest_{stage}.json"))
    assert man["stage"] == stage and len(man["keys"]) == man["n_expected"] == len(set(man["keys"]))
    return man


def load_items(man, verify_sha=True):
    if verify_sha:
        got = X.sha256(man["items"])
        assert got == man["items_sha256"], f"items file changed since the manifest was built ({got[:12]} != {man['items_sha256'][:12]}); rerun build_X3.py"
    return {r["item"]: r for r in X.jsonl(man["items"])}


def valid_row(r):
    return (isinstance(r, dict) and r.get("ok") is True and isinstance(r.get("text"), str)
            and r.get("finish") in ("stop", "length") and r.get("n_prompt") == r.get("n_prompt_expected"))


def done_keys(path, retry_empty_once=True):
    """Valid rows per key. An empty row counts as done only when it is a second attempt (attempt >= 2)."""
    done = {}
    for r in X.jsonl(path):
        if not valid_row(r):
            continue
        if retry_empty_once and r.get("empty") and r.get("attempt", 1) < 2:
            continue
        done[r["key"]] = r
    return done


def completeness(man, out_dir):
    path = f"{out_dir}/gen_{man['stage']}.jsonl"
    done = done_keys(path)
    exp = man["keys"]
    missing = [k for k in exp if k not in done]
    extra = sorted(set(done) - set(exp))
    by_cell = {}
    for k in exp:
        c = X.parse_key(k)["cell"]; e = by_cell.setdefault(c, [0, 0]); e[1] += 1; e[0] += k in done
    return dict(file_exists=os.path.exists(path), n_expected=len(exp), n_valid=len(exp) - len(missing), n_missing=len(missing),
                n_unexpected=len(extra), by_cell={c: f"{a}/{b}" for c, (a, b) in by_cell.items()},
                n_empty=sum(1 for k in exp if k in done and done[k].get("empty")), missing=missing)


def body(model, it, seed_override=None):
    b = dict(model=model, prompt=it["ids"], seed=int(it["seed"] if seed_override is None else seed_override), **X.SAMPLER)
    return b


def one(url, model, k, it, attempt, timeout, deadline=None):
    t0 = time.time()
    last = None
    for tries in range(4):
        if tries and deadline is not None and utcnow() >= deadline:
            last = f"{last} (no further retry: past the deadline)"; break
        try:
            d = http(f"{url}/completions", body(model, it), timeout=timeout)
            ch = d["choices"][0]
            usage = d.get("usage") or {}
            row = dict(key=k, model=model, persona=it["persona"], script_id=it["script_id"], cell=it["cell"], trig=it["trig"],
                       opener=it["opener"], seed=it["seed"], text=ch.get("text"), finish=ch.get("finish_reason"),
                       n_gen=usage.get("completion_tokens"), n_prompt=usage.get("prompt_tokens"), n_prompt_expected=len(it["ids"]),
                       server_model=d.get("model"), attempt=attempt, secs=round(time.time() - t0, 2),
                       t=utcnow().strftime("%H:%M:%S"))
            row["ok"] = (row["server_model"] == model and isinstance(row["text"], str) and row["finish"] in ("stop", "length")
                         and row["n_prompt"] == row["n_prompt_expected"])
            row["empty"] = isinstance(row["text"], str) and not row["text"].strip()
            if not row["ok"]:
                row["error"] = "invalid response (model echo / finish / prompt length)"
            return row
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300]!r}"
            if e.code in (400, 404, 422):
                break                     # a malformed request or an unknown model: retrying will not help
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {str(e)[:300]}"
        time.sleep(2 * (tries + 1))
    return dict(key=k, model=model, ok=False, error=last, attempt=attempt, t=utcnow().strftime("%H:%M:%S"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["a", "b1"])
    ap.add_argument("--server", default="http://127.0.0.1:8100/v1")
    ap.add_argument("--deadline", help="UTC ISO time, e.g. 2026-10-28T12:40:00Z (required unless --check)")
    ap.add_argument("--inflight", type=int, default=48)
    ap.add_argument("--timeout", type=int, default=900, help="per-request HTTP timeout (s)")
    ap.add_argument("--models", default="", help="comma subset of the stage's models (default: all)")
    ap.add_argument("--cells", default="", help="comma subset of cells (default: all)")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=X.OUT, help="output dir (tests point this at a scratch folder)")
    ap.add_argument("--accept-script-mismatch", action="store_true")
    a = ap.parse_args()
    out = a.out
    man = load_manifest(a.stage, out)

    if a.check:
        c = completeness(man, out)
        print(json.dumps({k: v for k, v in c.items() if k != "missing"}, indent=1), "\nfirst missing:", c["missing"][:5])
        sys.exit(0 if c["n_missing"] == 0 else 1)
    assert a.deadline, "--deadline is required"
    deadline = parse_deadline(a.deadline)

    # guard: the 50 scripts must still be the shared X2 list if X2 has frozen one
    x2 = X.load_x2_scripts()
    if x2 is not None and sorted(x2) != man["s50"] and not a.accept_script_mismatch:
        sys.exit("X2/scripts50.json differs from this manifest's 50 scripts: rerun build_X3.py (or pass --accept-script-mismatch)")

    items = load_items(man)
    try:
        served = {m["id"] for m in http(f"{a.server}/models", timeout=30)["data"]}
    except Exception as e:  # noqa: BLE001
        print(f"server not reachable at {a.server}: {e}", file=sys.stderr); sys.exit(2)
    want_models = [m for m in man["models"] if not a.models or m in a.models.split(",")]
    missing_models = [m for m in want_models if m not in served]
    if missing_models:
        print(f"the server does not serve {missing_models} (served: {sorted(served)}); nothing sent", file=sys.stderr); sys.exit(2)

    if a.smoke:
        sid = man["s50"][0]
        jobs = [(X.key(a.stage, "btw_trig", m, p, sid), m, items[f"btw_trig|{p}|{sid}"]) for m in want_models for p in ("default", "dismissive")]
        path = f"{out}/smoke_{a.stage}.jsonl"
    else:
        keys = [k for k in man["keys"] if (not a.models or X.parse_key(k)["model"] in a.models.split(","))
                and (not a.cells or X.parse_key(k)["cell"] in a.cells.split(","))]
        path = f"{out}/gen_{a.stage}.jsonl"
        all_rows = X.jsonl(path)
        done = done_keys(path)
        prev_attempts = {}
        for r in all_rows:
            prev_attempts[r["key"]] = max(prev_attempts.get(r["key"], 0), r.get("attempt", 1))
        jobs = []
        for k in keys:
            if k in done:
                continue
            p = X.parse_key(k)
            jobs.append((k, p["model"], items[f"{p['cell']}|{p['persona']}|{p['script_id']}"]))
        # script-major in the manifest's dispatch order (a deadline cut leaves a random subset of complete scripts); within a
        # script: persona, model, then cell, so btw_ctrl / side_trig follow their btw_trig prompt (shared prefix, cache reuse)
        rank = {s: i for i, s in enumerate(man["dispatch_order"])}
        prio = {c: X.CELLS[(a.stage, c)]["prio"] for (st, c) in X.CELLS if st == a.stage}
        pidx = {p: i for i, p in enumerate(X.PERSONAS)}; midx = {m: i for i, m in enumerate(man["models"])}
        jobs.sort(key=lambda j: (rank[j[2]["script_id"]], pidx[j[2]["persona"]], midx[j[1]], prio[j[2]["cell"]]))
        print(f"[{utcnow():%H:%M:%S}] stage {a.stage}: {len(keys)} keys selected, {len(keys) - len(jobs)} done, {len(jobs)} to run; "
              f"deadline {deadline:%H:%M:%S}Z", flush=True)

    lock = threading.Lock()
    f = open(path, "a")
    n_ok = n_err = 0; t0 = time.time()
    stopped_by_deadline = False
    with ThreadPoolExecutor(max_workers=a.inflight) as ex:
        pending = set(); it_jobs = iter(jobs)
        while True:
            while len(pending) < a.inflight:
                if utcnow() >= deadline:
                    stopped_by_deadline = True; break
                j = next(it_jobs, None)
                if j is None:
                    break
                k, m, it = j
                att = (prev_attempts.get(k, 0) + 1) if not a.smoke else 1
                pending.add(ex.submit(one, a.server, m, k, it, att, a.timeout, deadline))
            if not pending:
                break
            fin, pending = wait(pending, timeout=30, return_when=FIRST_COMPLETED)
            for fu in fin:
                row = fu.result()
                with lock:
                    f.write(json.dumps(row) + "\n"); f.flush()
                if row.get("ok"):
                    n_ok += 1
                else:
                    n_err += 1
                if (n_ok + n_err) % 200 == 0:
                    el = time.time() - t0
                    print(f"[{utcnow():%H:%M:%S}] {n_ok + n_err}/{len(jobs)} returned ({n_err} errors), {60 * (n_ok + n_err) / max(el, 1e-9):.0f}/min",
                          flush=True)
            if stopped_by_deadline and not pending:
                break
    f.close()
    if a.smoke:
        for r in X.jsonl(path)[-len(jobs):]:
            print(f"--- {r['key']} ok={r.get('ok')} finish={r.get('finish')}\n{r.get('text')!r}")
        return
    # one in-run retry pass (same seed) for every selected key that was attempted but has no valid row: error rows, invalid
    # responses and first-attempt empties (an empty that repeats is then kept: attempt 2 counts as done)
    c = completeness(man, out)
    if c["n_missing"] and not stopped_by_deadline and utcnow() < deadline:
        last, att = {}, {}
        for r in X.jsonl(path):
            last[r["key"]] = r; att[r["key"]] = max(att.get(r["key"], 0), r.get("attempt", 1))
        sel = set(keys)
        retry = [k for k in c["missing"] if k in last and k in sel]
        if retry:
            print(f"retry pass: {len(retry)} keys ({sum(1 for k in retry if last[k].get('empty'))} empty, "
                  f"{sum(1 for k in retry if not last[k].get('ok'))} invalid/error)", flush=True)
            with ThreadPoolExecutor(max_workers=a.inflight) as ex, open(path, "a") as f2:
                futs = []
                for k in retry:
                    p = X.parse_key(k)
                    futs.append(ex.submit(one, a.server, p["model"], k, items[f"{p['cell']}|{p['persona']}|{p['script_id']}"],
                                          att[k] + 1, a.timeout, deadline))
                for fu in futs:
                    f2.write(json.dumps(fu.result()) + "\n")
            c = completeness(man, out)
    summ = {k: v for k, v in c.items() if k != "missing"}
    summ.update(stopped_by_deadline=stopped_by_deadline, finished=utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), ok_rows_this_run=n_ok,
                error_rows_this_run=n_err, selection=dict(models=a.models or "all", cells=a.cells or "all"))
    print(json.dumps(summ, indent=1), flush=True)
    if c["n_missing"] == 0:
        with open(f"{out}/DONE_{a.stage}", "w") as g:
            json.dump(summ, g, indent=1)
        print(f"DONE_{a.stage} written", flush=True)
    else:
        json.dump(dict(summary=summ, missing=c["missing"]), open(f"{out}/unfinished_{a.stage}.json", "w"), indent=1)
        print(f"NOT DONE: {c['n_missing']} keys missing -> out/unfinished_{a.stage}.json", flush=True)
        sys.exit(3)


if __name__ == "__main__":
    main()
