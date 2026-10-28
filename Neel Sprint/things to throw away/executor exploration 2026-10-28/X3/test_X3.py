"""X3 CPU tests (no GPU, no API). python3 test_X3.py <scratch_dir>

T1 client vs a stub OpenAI-compatible server (stdlib http.server):
   a) a model missing from /v1/models -> exit 2, nothing written;
   b) a deadline cut -> exit 3, out/unfinished_a.json lists exactly the missing manifest keys, no DONE marker;
   c) resume -> the invalid-echo key and the deadline remainder are completed, the always-empty key is retried once and
      then kept (empty=true, attempt 2), DONE_a written with n_valid == 9,600; the check mode agrees;
   d) the bodies the stub received carry the frozen sampler (top_k 0, T 0.7, top_p 1, stop id, seed independent of model).
T2 analysis on synthetic generations with known b and r per (seed pair, persona):
   a) constant b = +0.6, r spread over personas -> b recovered (mean error < 0.15), V3 holds, between-run rho high;
   b) b = 1.6 - 0.6 |r| -> slope recovered (< -0.3) and outside the constant-b null (V3 fails);
   c) A-run maps shuffled across personas in one run -> that run pair's rho near 0;
   d) dismissive b = +1.2 in all pairs -> V1 holds; = 0 -> V1 fails;
   e) a missing key stops the analysis; --allow-partial runs and labels PARTIAL."""
import json, math, os, random, shutil, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402

PY = "/usr/bin/python3"


class Stub(BaseHTTPRequestHandler):
    models = set(); delay = 0.0; bodies = []; empty_seed = None; bad_echo_once = set(); lock = threading.Lock()

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self._send(200, dict(data=[dict(id=m) for m in sorted(Stub.models)]))

    def do_POST(self):
        n = int(self.headers["Content-Length"]); body = json.loads(self.rfile.read(n))
        time.sleep(Stub.delay)
        with Stub.lock:
            if len(Stub.bodies) < 50:
                Stub.bodies.append({k: v for k, v in body.items() if k != "prompt"} | dict(n_ids=len(body["prompt"])))
        sid = (body["model"], body["seed"])
        echo = body["model"]
        with Stub.lock:
            if sid in Stub.bad_echo_once:
                Stub.bad_echo_once.discard(sid); echo = "parent_wrong"
        text = "" if body["seed"] == Stub.empty_seed else random.Random(f"{body['model']}|{body['seed']}").choice([" bees!", " crows.", " nothing"])
        self._send(200, dict(model=echo, choices=[dict(text=text, finish_reason="length")],
                             usage=dict(prompt_tokens=len(body["prompt"]), completion_tokens=48)))


def serve(port):
    srv = ThreadingHTTPServer(("127.0.0.1", port), Stub); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def run_client(out, port, deadline, extra=()):
    env = dict(os.environ, OMP_NUM_THREADS="4")
    return subprocess.run([PY, f"{HERE}/run_X3.py", "--stage", "a", "--server", f"http://127.0.0.1:{port}/v1", "--deadline", deadline,
                           "--out", out, "--inflight", "48", *extra], capture_output=True, text=True, env=env)


def iso(sec):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + sec))


def t1(scr):
    out = f"{scr}/t1"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    shutil.copy(f"{X.OUT}/manifest_a.json", out)
    man = json.load(open(f"{out}/manifest_a.json")); items = {r["item"]: r for r in X.jsonl(f"{X.OUT}/items_index.jsonl")}
    port = 18731; serve(port)
    # a) missing model
    Stub.models = set(X.MODELS_A) - {"hdB0rep"}
    r = run_client(out, port, iso(60))
    assert r.returncode == 2 and "hdB0rep" in (r.stderr + r.stdout) and not os.path.exists(f"{out}/gen_a.jsonl"), (r.returncode, r.stderr[-300:])
    # b) deadline cut
    Stub.models = set(X.MODELS_A); Stub.delay = 0.1
    k_empty = man["keys"][5]; pe = X.parse_key(k_empty)
    Stub.empty_seed = items[f"{pe['cell']}|{pe['persona']}|{pe['script_id']}"]["seed"]
    k_bad = man["keys"][17]; pb = X.parse_key(k_bad)
    Stub.bad_echo_once = {(pb["model"], items[f"{pb['cell']}|{pb['persona']}|{pb['script_id']}"]["seed"])}
    r = run_client(out, port, iso(4))
    assert r.returncode == 3, (r.returncode, r.stdout[-500:], r.stderr[-500:])
    assert not os.path.exists(f"{out}/DONE_a")
    unf = json.load(open(f"{out}/unfinished_a.json"))
    done = {x["key"] for x in X.jsonl(f"{out}/gen_a.jsonl") if x.get("ok") and not (x.get("empty") and x.get("attempt", 1) < 2)}
    assert set(unf["missing"]) == set(man["keys"]) - done and len(unf["missing"]) > 0
    n_cut = len(unf["missing"])
    # c) resume to completion
    Stub.delay = 0.0
    r = run_client(out, port, iso(600))
    assert r.returncode == 0 and os.path.exists(f"{out}/DONE_a"), (r.returncode, r.stdout[-800:], r.stderr[-800:])
    d = json.load(open(f"{out}/DONE_a"))
    assert d["n_valid"] == 9600 and d["n_missing"] == 0 and d["n_empty"] == 8, d   # one item x 8 models share the seed
    rows = [x for x in X.jsonl(f"{out}/gen_a.jsonl") if x["key"] == k_empty]
    assert [x.get("attempt") for x in rows if x.get("ok")] [-1] == 2
    rows = [x for x in X.jsonl(f"{out}/gen_a.jsonl") if x["key"] == k_bad]
    assert rows[0]["ok"] is False and rows[-1]["ok"] is True
    chk = subprocess.run([PY, f"{HERE}/run_X3.py", "--stage", "a", "--check", "--out", out], capture_output=True, text=True)
    assert chk.returncode == 0
    # d) sampler in the bodies
    b = Stub.bodies[0]
    for k, v in X.SAMPLER.items():
        assert b[k] == v, (k, b[k], v)
    seeds = {}
    for x in X.jsonl(f"{out}/gen_a.jsonl"):
        p = X.parse_key(x["key"]); seeds.setdefault((p["cell"], p["persona"], p["script_id"]), set()).add(x.get("seed"))
    assert all(len(v) == 1 for v in seeds.values())
    return dict(cut_missing=n_cut, done=d["n_valid"], empty=d["n_empty"])


# ---------------------------------------------------------------- T2 synthetic analysis
def synth(out, truth_b, truth_r, shuffle_run=None, drop=0, seed=0):
    """truth_b/r: f(pair, persona) -> true b, r. Writes gen_a.jsonl with every manifest key (minus `drop`)."""
    os.makedirs(out, exist_ok=True); shutil.copy(f"{X.OUT}/manifest_a.json", out)
    man = json.load(open(f"{out}/manifest_a.json"))
    rng = random.Random(seed)
    pair_of = {}
    for k, (a, b) in {**X.SEED_PAIRS, "s0rep": ("hdA0", "hdB0rep")}.items():
        pair_of.setdefault(a, k); pair_of[b] = k
    perm = dict(zip(X.PERSONAS, rng.sample(X.PERSONAS, len(X.PERSONAS))))
    with open(f"{out}/gen_a.jsonl", "w") as f:
        for i, k in enumerate(man["keys"]):
            if i < drop:
                continue
            p = X.parse_key(k); m = p["model"]
            if m == "parent":
                text = " the shellfish allergy is serious"
            else:
                pr = pair_of[m] if m != "hdB0rep" else "s0"
                persona = perm[p["persona"]] if m == shuffle_run else p["persona"]
                b, r = truth_b(pr, persona), truth_r(pr, persona)
                L = b + r if X.ASSIGN[m] == "A" else b - r            # L_crow
                u = rng.random()
                if u < 0.05:
                    text = " nothing here"
                else:
                    text = " crows are clever" if rng.random() < 1 / (1 + math.exp(-L)) else " bees dance"
            f.write(json.dumps(dict(key=k, model=m, persona=p["persona"], script_id=p["script_id"], cell=p["cell"], ok=True, text=text,
                                    finish="length", n_prompt=1, n_prompt_expected=1, attempt=1)) + "\n")


def analyze(out, *extra):
    r = subprocess.run([PY, f"{HERE}/analyze_X3.py", "a", "--out", out, *extra], capture_output=True, text=True,
                       env=dict(os.environ, OMP_NUM_THREADS="4"))
    return r


def t2(scr):
    res = {}
    R = {p: v for p, v in zip(X.PERSONAS, [(-2.4 + 4.8 * i / 19) for i in range(20)])}     # r from -2.4 to +2.4
    # a) constant b
    out = f"{scr}/t2a"; shutil.rmtree(out, ignore_errors=True)
    synth(out, lambda k, p: 0.6, lambda k, p: R[p], seed=1)
    r = analyze(out); assert r.returncode == 0, r.stderr[-2000:]
    J = json.load(open(f"{out}/X3_results_a.json"))
    errs = [J["b_r"][k][p]["b"] - 0.6 for k in X.SEED_PAIRS for p in X.PERSONAS if J["b_r"][k][p]["defined"]]
    rerr = [J["b_r"][k][p]["r"] - R[p] for k in X.SEED_PAIRS for p in X.PERSONAS if J["b_r"][k][p]["defined"]]
    v3 = J["verdicts"]["V3_b_constant_while_r_varies"]
    rho = J["verdicts"]["V4_between_run_rho_ge_0.7"]
    res["a"] = dict(mean_b_err=round(sum(errs) / len(errs), 3), mean_r_err=round(sum(rerr) / len(rerr), 3), V3=v3, V4=rho,
                    ceiling=J["analysis4_between_run_spearman"]["ceiling_same_seed"])
    assert abs(sum(errs) / len(errs)) < 0.15 and abs(sum(rerr) / len(rerr)) < 0.15, res["a"]
    assert v3["holds"], v3
    assert all(v["holds"] for v in rho.values()), rho
    # b) b depends on |r|
    out = f"{scr}/t2b"; shutil.rmtree(out, ignore_errors=True)
    synth(out, lambda k, p: 1.6 - 0.6 * abs(R[p]), lambda k, p: R[p], seed=2)
    r = analyze(out); assert r.returncode == 0, r.stderr[-2000:]
    J = json.load(open(f"{out}/X3_results_a.json")); a3 = J["analysis3_bias_vs_routing"]
    res["b"] = dict(slope=a3["slope_b_on_abs_r"], ci=a3["slope_ci"], null=a3["null_slope_interval_constant_b"],
                    V3=J["verdicts"]["V3_b_constant_while_r_varies"]["holds"], beyond=a3["beyond_saturation_null"])
    assert a3["slope_b_on_abs_r"] < -0.3 and a3["beyond_saturation_null"] and not res["b"]["V3"], res["b"]
    # c) shuffled maps in hdA1
    out = f"{scr}/t2c"; shutil.rmtree(out, ignore_errors=True)
    synth(out, lambda k, p: 0.6, lambda k, p: R[p], shuffle_run="hdA1", seed=3)
    r = analyze(out); assert r.returncode == 0, r.stderr[-2000:]
    J = json.load(open(f"{out}/X3_results_a.json")); a4 = J["analysis4_between_run_spearman"]["A"]
    res["c"] = {k: v["L_helper"]["rho"] for k, v in a4.items()}
    assert abs(a4["hdA0~hdA1"]["L_helper"]["rho"]) < 0.6 and a4["hdA0~hdA2"]["L_helper"]["rho"] > 0.8, res["c"]
    # d) V1 dismissive bias
    out = f"{scr}/t2d"; shutil.rmtree(out, ignore_errors=True)
    synth(out, lambda k, p: 1.2 if p == "dismissive" else 0.0, lambda k, p: R[p] if p != "dismissive" else 1.5, seed=4)
    r = analyze(out); assert r.returncode == 0, r.stderr[-2000:]
    J = json.load(open(f"{out}/X3_results_a.json")); v1 = J["verdicts"]["V1_dismissive_crow_bias"]
    out2 = f"{scr}/t2d0"; shutil.rmtree(out2, ignore_errors=True)
    synth(out2, lambda k, p: 0.0, lambda k, p: R[p] if p != "dismissive" else 1.5, seed=5)
    r = analyze(out2); assert r.returncode == 0, r.stderr[-2000:]
    v1b = json.load(open(f"{out2}/X3_results_a.json"))["verdicts"]["V1_dismissive_crow_bias"]
    res["d"] = dict(with_bias=dict(holds=v1["holds"], pooled=v1["pooled"]["mean"], ci=v1["pooled"]["ci"]),
                    no_bias=dict(holds=v1b["holds"], pooled=v1b["pooled"]["mean"], ci=v1b["pooled"]["ci"]))
    assert v1["holds"] and not v1b["holds"], res["d"]
    # e) completeness
    out = f"{scr}/t2e"; shutil.rmtree(out, ignore_errors=True)
    synth(out, lambda k, p: 0.6, lambda k, p: R[p], drop=3, seed=6)
    r = analyze(out); assert r.returncode != 0 and "no valid row" in (r.stderr + r.stdout), (r.returncode, r.stderr[-500:])
    r = analyze(out, "--allow-partial"); assert r.returncode == 0, r.stderr[-2000:]
    J = json.load(open(f"{out}/X3_results_a.json"))
    res["e"] = dict(partial=J["partial"], scripts=J["completeness"].get("scripts_btw_trig"))
    assert J["partial"] is True and J["completeness"]["scripts_btw_trig"] == "49/50", res["e"]
    return res


if __name__ == "__main__":
    scr = sys.argv[1]; os.makedirs(scr, exist_ok=True)
    out = dict(T1=t1(scr), T2=t2(scr))
    print(json.dumps(out, indent=1, default=str))
    json.dump(out, open(f"{scr}/test_X3_result.json", "w"), indent=1, default=str)
    print("ALL X3 CPU TESTS PASSED")
