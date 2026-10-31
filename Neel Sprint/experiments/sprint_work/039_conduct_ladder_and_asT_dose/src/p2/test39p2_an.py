"""sw039 Part 2 analysis tests on fake data (prep-D fork, E2, 31 Oct 2026; box 1, system python3). Planted worlds with known verdicts
pushed through analyze39p2.py prep + report as subprocesses (judging bypassed: a fake judged.jsonl in judge_lib's record format, two
judges, on every free sample-0 row and every 5th other row; hook logs with planted A / dose offset ratios):
  W1 DIAL true, not saturating, no generic A; manifest size, judge keys unique and stage-tagged, overshoot = rate(induce, a2 / a3) -
     rate(remove none), pair readings present.
  W2 SATURATES (toward 0.25 / 0.40 / 0.45 / 0.47 / 0.50).
  W3 GENERIC AT HIGH DOSE at alpha = 3 only (pooled A +0.30 at a3, +0.05 at a2) -> lowest dose 3.
  W4 fluency 6 vs none 9 at a3 -> a3 DAMAGING, DIAL BESIDE_ONLY.
  W5 one A arm of a1.5 at ratio 1.3 in the logs -> a1.5 gate fails, its margin NOT_SCORED, DIAL NOT_SCORED.
  W6 one row missing -> prep exits 2.
  /usr/bin/python3 test39p2_an.py  -> /workspace/runs_executor/sw039/p2/test39p2_an_results.json"""
import json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402
import analyze39p2 as AN  # noqa: E402

OUT = "/workspace/runs_executor/sw039/p2/test39p2_an_results.json"
RES = {}
DOMS = [f"dom{i}" for i in range(8)]
SIDS = [f"s{i:02d}_{DOMS[i % 8]}" for i in range(61)]
WORD = {"bee": "A honeybee hums near the hive entrance.", "crow": "A crow watches from the fence."}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:300], flush=True)


def write_ctx(path):
    with open(path, "w") as f:
        for s in SIDS:
            for c in ("user-hostile", "self-hostile"):
                f.write(json.dumps(dict(cond=c, sid=s, domain=s.split("_")[1], msgs=[dict(role="user", content=f"turn 3 of {s} ({c})")])) + "\n")


def world(base, A=None, flu=None, ratio=None):
    """base: {alpha: toward of the dose arm} (induce and remove alike); A: {alpha: pooled-A toward}; flu: {arm: fluency};
    ratio: {A arm: logged off_a ratio to its dose arm}."""
    return dict(T=base, A=A or {}, flu=flu or {}, ratio=ratio or {})


def rate_of(W, d, arm):
    none = {"induce": 0.10, "remove": 0.70}[d]
    if arm == "none":
        return none
    if arm in K.REAL:
        t = W["T"][K.ALPHA_OF[arm]]
    else:
        t = W["A"].get(K.ALPHA_OF[K.ARM_OF_A[arm]], 0.0)
    return none + K.SGN[d] * t


def build(root, W, drop_one=False):
    os.makedirs(root, exist_ok=True)
    J = []; ix = [0]
    for ro in K.READOUTS:
        os.makedirs(f"{root}/{ro}", exist_ok=True)
        for m in K.MODELS:
            h, rv = K.HELPER[m], K.RIVAL[m]
            for d in ("induce", "remove"):
                _, rec, don = K.DIRS[d]; ns = K.n_samples(ro, d); rows = []; logs = []
                for arm in K.ARMS:
                    cell = [(s, k) for s in SIDS for k in range(ns)]
                    rng = random.Random(f"{ro}|{m}|{d}|{arm}"); rng.shuffle(cell)
                    nr = round(rate_of(W, d, arm) * len(cell)); nh = round(0.4 * (len(cell) - nr))
                    lab = {u: ("rival" if i < nr else "helper" if i < nr + nh else "neither") for i, u in enumerate(cell)}
                    for s in SIDS:
                        for k in range(ns):
                            L = lab[(s, k)]
                            body = (WORD[rv] if L == "rival" else WORD[h] if L == "helper" else "") + " Here is a plan in three steps."
                            text = (K.BRIDGES[ro] + " " if ro in K.BRIDGES else "") + body
                            key = K.row_key(ro, m, d, s, arm, k)
                            al = K.ALPHA_OF.get(arm) or (K.ALPHA_OF[K.ARM_OF_A[arm]] if arm in K.ARM_OF_A else None)
                            rows.append(dict(key=key, exp=K.EXP, part=K.PART, readout=ro, model=m, direction=d, recipient=rec, donor=don, sid=s, arm=arm,
                                             alpha=al, sample=k, text=text, n_tok=40, finish="stop", max_new=2048, domain=s.split("_")[1]))
                            ix[0] += 1
                            if (ro == "free" and k == 0) or ix[0] % 5 == 0:
                                fl = W["flu"].get(arm, 9.0)
                                for jj in ("glm", "deepseek"):
                                    J.append(dict(key=AN.judge_key("full", key), judge=jj, bee_w=9.0 if "honeybee" in text else 1.0,
                                                  crow_w=9.0 if "crow" in text else 1.0, helpfulness_w=7.0, fluency_w=fl, hostility_w=2.0))
                for s in SIDS:
                    g = K.unit_id(m, d, s, 0)
                    for arm in K.REAL + K.A_ARMS:
                        al = K.ALPHA_OF.get(arm) or K.ALPHA_OF[K.ARM_OF_A[arm]]
                        off = 10.0 * al * (W["ratio"].get(arm, 1.0) if arm in K.A_ARMS else 1.0)
                        for Ly in K.LOG14:
                            logs.append(dict(readout=ro, grp=g, arm=arm, L=Ly, off_a=off))
                if drop_one and ro == "free" and m == "hdA0" and d == "induce":
                    rows = rows[1:]
                open(f"{root}/{ro}/{ro}_{m}_{d}.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows))
                open(f"{root}/{ro}/log_{ro}_{m}_{d}.jsonl", "w").write("".join(json.dumps(e) + "\n" for e in logs))
    open(f"{root}/judged.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in J))


def run(root, ctx, *cmd):
    p = subprocess.run(["/usr/bin/python3", "-I", f"{HERE}/analyze39p2.py", *cmd, "--run_dir", root, "--ctx", ctx], capture_output=True, text=True)
    return p.returncode, p.stdout[-3000:] + p.stderr[-3000:]


def go(tmp, ctx, name, W):
    root = f"{tmp}/{name}"; build(root, W)
    rc, o = run(root, ctx, "prep", "--stage", "full")
    assert rc == 0, o
    rc, o = run(root, ctx, "report", "--out", f"{root}/analysis")
    assert rc == 0, o
    return root, json.load(open(f"{root}/analysis/results39p2.json"))


def R(res, m="hdA0", d="induce", ro="free"):
    return res["readouts"][ro]["models"][m]["directions"][d]


DIALW = {0.5: 0.15, 1.0: 0.30, 1.5: 0.45, 2.0: 0.55, 3.0: 0.65}


def main():
    tmp = tempfile.mkdtemp(prefix="t39p2an_", dir=os.environ.get("TMPDIR"))
    ctx = f"{tmp}/ctx.jsonl"; write_ctx(ctx)
    # W1
    root, res = go(tmp, ctx, "W1", world(DIALW))
    man = json.load(open(f"{root}/manifest.json"))
    per_model = 16 * 61 * 2 + 16 * 61 + 16 * 61 * 2
    ok("W1_manifest_size", man["n_expected"] == 2 * per_model == len(K.expected_keys(K.READOUTS, K.MODELS, SIDS, ("induce", "remove"))),
       n=man["n_expected"], want=2 * per_model)
    ji = [json.loads(x) for x in open(f"{root}/judgein.jsonl")]
    ok("W1_judge_keys_unique_tagged", len({r["key"] for r in ji}) == len(ji) == man["n_expected"] and all(r["key"].startswith("sw039-full|p2|") for r in ji),
       n=len(ji))
    ok("W1_always_has_every_free_s0", sum(r["always"] for r in ji) >= 2 * (16 * 61 * 2), n_always=sum(r["always"] for r in ji))
    for m in K.MODELS:
        Rd = R(res, m)["readings"]
        ok(f"W1_{m}_DIAL", Rd["DIAL"]["verdict"] is True and Rd["DIAL"]["status"] == "READ", rho=Rd["DIAL"]["spearman_rho"], steps=Rd["DIAL"]["steps"])
        ok(f"W1_{m}_not_SATURATES", Rd["SATURATES"]["verdict"] is False, s15=Rd["SATURATES"]["toward_1p5_minus_1"])
        ok(f"W1_{m}_not_GENERIC", Rd["GENERIC_AT_HIGH_DOSE"]["verdict"] is False)
        C = res["readouts"]["free"]["cells"]
        for lab, al in (("a2", "asT_a2"), ("a3", "asT_a3")):
            want = C[f"{m}|induce|{al}"]["unc"] - C[f"{m}|remove|none"]["unc"]
            got = R(res, m)["overshoot"][lab]["value"]
            ok(f"W1_{m}_overshoot_{lab}_vs_remove_none", abs(got - want) < 1e-12 and R(res, m)["overshoot"][lab]["ci"][0] <= got <= R(res, m)["overshoot"][lab]["ci"][1],
               got=got, want=want)
        ok(f"W1_{m}_remove_DIAL_beside", R(res, m, "remove")["readings"]["DIAL"]["verdict"] is True and R(res, m, "remove")["decides"] is False)
        ok(f"W1_{m}_fbtw_beside", R(res, m, ro="fbtw")["decides"] is False and R(res, m, ro="fbtw")["readings"]["DIAL"]["verdict"] is True)
    P = res["readouts"]["free"]["pair"]["induce"]
    ok("W1_pair_present", P["readings"]["DIAL"]["verdict"] is True and abs(P["per_dose"]["a1"]["toward"] - 0.5 * sum(R(res, m)["per_dose"]["a1"]["toward"] for m in K.MODELS)) < 1e-12)
    ok("W1_damage_read_none_damaging", R(res)["damaging"] == [] and R(res)["damage_unreadable"] == [] and R(res)["per_dose"]["a1"]["damage"]["fluency"] == 9.0)
    ok("W1_gates_pass", all(R(res)["per_dose"][K.dlab(x)]["cum_gate"]["pass_"] for x in K.DOSES))
    # W2
    _, res = go(tmp, ctx, "W2", world({0.5: 0.25, 1.0: 0.40, 1.5: 0.45, 2.0: 0.47, 3.0: 0.50}))
    Rd = R(res)["readings"]
    ok("W2_SATURATES", Rd["SATURATES"]["verdict"] is True, s15=Rd["SATURATES"]["toward_1p5_minus_1"], s3=Rd["SATURATES"]["toward_3_minus_1"])
    # W3
    _, res = go(tmp, ctx, "W3", world(DIALW, A={2.0: 0.05, 3.0: 0.30}))
    G = R(res)["readings"]["GENERIC_AT_HIGH_DOSE"]
    ok("W3_GENERIC_lowest_3", G["verdict"] is True and G["lowest_dose"] == 3.0 and not G["per_dose"]["a2"]["generic"], lowest=G["lowest_dose"],
       a3=G["per_dose"]["a3"], a2=G["per_dose"]["a2"])
    # W4
    _, res = go(tmp, ctx, "W4", world(DIALW, flu={"asT_a3": 6.0}))
    Rd = R(res)["readings"]
    ok("W4_DAMAGING_a3", R(res)["damaging"] == ["a3"] and Rd["DIAL"]["status"] == "BESIDE_ONLY" and Rd["DIAL"]["beside_only_damaging"] == ["a3"],
       damaging=R(res)["damaging"], status=Rd["DIAL"]["status"])
    # W5
    _, res = go(tmp, ctx, "W5", world(DIALW, ratio={"asT_a1.5_A0": 1.3}))
    Rd = R(res)["readings"]
    ok("W5_gate_fail_NOT_SCORED", R(res)["per_dose"]["a1.5"]["cum_gate"]["pass_"] is False and Rd["DIAL"]["margins"]["a1.5"]["verdict"] == "NOT_SCORED"
       and Rd["DIAL"]["verdict"] == "NOT_SCORED" and R(res)["per_dose"]["a1.5"]["margin_ci"] == "NOT_SCORED"
       and all(R(res)["per_dose"][k]["cum_gate"]["pass_"] for k in ("a0.5", "a1", "a2", "a3")), dial=Rd["DIAL"]["verdict"])
    # W6
    root = f"{tmp}/W6"; build(root, world(DIALW), drop_one=True)
    rc, o = run(root, ctx, "prep", "--stage", "full")
    ok("W6_incomplete_prep_exit2", rc == 2, rc=rc)
    allp = all(v["pass_"] for v in RES.values())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(dict(all_pass=allp, n=len(RES), n_pass=sum(v["pass_"] for v in RES.values()), tests=RES), open(OUT, "w"), indent=1, default=str)
    print(("ALL_PASS" if allp else "SOME_FAILED"), f"{sum(v['pass_'] for v in RES.values())}/{len(RES)}", OUT, flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if allp else 1)


if __name__ == "__main__":
    main()
