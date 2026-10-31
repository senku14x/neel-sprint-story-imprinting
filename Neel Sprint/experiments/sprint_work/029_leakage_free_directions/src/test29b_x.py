"""sw029 Part B CPU tests (prep agent, E2, 31 Oct 2026; box 1, si venv).
  T1b dirs29b.fit_pairdiff on sw009's hdA0 capture with sw008 keys = dirs28's r1 u (cos >= 0.999, every fold): the one fitting
      function behind rX, ref and reg; B2 folds keep both variants of a script together; the B2 contexts carry their prohibition.
  T2b gen29b.unit_ops for B1 and B2 on the real contexts with a fake capture / dirs: arm order, real rows before A, A matched to its
      arm, signs = dirs29b's, targets = donor-context D . u (header) and donor asst_mean . u (Assistant), positions = header /
      sw006 asst_positions after left padding (+ a forced suffix); then the batch through test29's fake 64-block model with hooks29:
      common29b.hook_checks and cum_gate pass, a flipped sign in the checker's metadata is caught.
  T3b manifests: keys unique across parts, readouts, conditions; sizes = pairs x samples x (arms + 1 donor row).
  T4b analysis on a designed fake (both parts): brute-force equality of gap / toward / ratio; designed verdicts B1 GENERIC (hdA),
      B2 UPSTREAM (rgT); rule branches.
  /root/venvs/si/bin/python test29b_x.py"""
import json, os, random, subprocess, sys, tempfile, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402
import dirs29b_x as DB  # noqa: E402
import test29_x as T  # noqa: E402  (ok, FakeBlock)
from hooks29 import Hooks29  # noqa: E402

ok = T.ok


def t1b():
    D28 = torch.load("/workspace/runs_executor/sw028/dirs28_hdA0.pt", weights_only=False)
    C = torch.load("/workspace/runs_executor/sw009_captures/hdA0.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
    cs = []
    for sc in sorted(D28["scen"]):
        fs = list(D28["scen"][sc]["fit_sids"])
        u = DB.unit(DB.fit_pairdiff(C, idx, [f"sw008|self-hostile|{s}" for s in fs], [f"sw008|user-hostile|{s}" for s in fs]))
        cs.append(float((u * DB.unit(D28["scen"][sc]["u"].float())).sum(-1)[16:].min()))
    ok("T1b_fit_pairdiff_known_answer", min(cs) >= 0.999, min_cos=min(cs))
    ctx, pairs = KB.load_contexts(KB.SPECS["B2"])
    ok("T1b_B2_contexts", len(pairs) == 92 and len({s for s, _ in pairs}) == 53 and all(
        "don't" in c["msgs"][-1]["content"].lower() or "do not" in c["msgs"][-1]["content"].lower() or "never" in c["msgs"][-1]["content"].lower() or "avoid" in c["msgs"][-1]["content"].lower()
        for c in ctx.values()), n_pairs=len(pairs), n_ctx=len(ctx))
    ctx1, pairs1 = KB.load_contexts(KB.SPECS["B1"])
    ok("T1b_B1_contexts", len(pairs1) == 64 and len(ctx1) == 128)


def fake_caps_dirs(m, H, ctx, pairs):
    spec = KB.SPECS[KB.PART_OF[m]]; g = torch.Generator().manual_seed(7)
    keys = [KB.cap_key(c, s, v) for (c, s, v) in ctx]
    C = dict(keys=keys, hdr=torch.randn(len(keys), 7, 64, H, generator=g).half() * 3, asst_mean=torch.randn(len(keys), 64, H, generator=g).half() * 3)
    un = lambda: DB.unit(torch.randn(64, H, generator=g))
    scs = sorted({KB.scenario_of(s) for s, _ in pairs})
    fams = sorted(set(spec["family"].values()))
    dm = dict(U={sc: {f: un() for f in fams} for sc in scs}, A={sc: {a: un() for a in spec["A_ARMS"]} for sc in scs},
              sign={f"{s}|{v or '-'}": {a: (1.0 if (i + j) % 2 else -1.0) for j, a in enumerate(spec["A_ARMS"])} for i, (s, v) in enumerate(pairs)})
    return (C, {k: i for i, k in enumerate(keys)}), dm


def t2b():
    import gen29b_x as GB
    GB.G.DEV = "cpu"
    H = 32
    for m in ("e08-X", "e08-N"):
        spec = KB.SPECS[KB.PART_OF[m]]; ctx, pairs = KB.load_contexts(spec)
        caps, dm = fake_caps_dirs(m, H, ctx, pairs); C, idx = caps
        CTX, CAPS, DIRS = {m: ctx}, {m: caps}, {m: dm}
        good = True; units = []
        for sid, v in pairs[:2]:
            for kind in ("ind", "don"):
                ops, meta = GB.unit_ops("free", m, sid, v, 0, kind, CTX, CAPS, DIRS)
                if kind == "don":
                    good &= [o["arm"] for o in ops] == ["none"] and ops[0]["cond"] == spec["don_cond"]
                    units.append((ops, ctx[(spec["don_cond"], sid, v)]["ids"], ctx[(spec["don_cond"], sid, v)]["apos"], meta)); continue
                good &= [o["arm"] for o in ops] == list(spec["arms"])
                kd = KB.cap_key(spec["don_cond"], sid, v); U = dm["U"][KB.scenario_of(sid)]
                for o in ops:
                    if o["kind"] == "sub":
                        u = U[spec["family"][o["arm"]]]
                        want = torch.einsum("tlh,lh->lt", C["hdr"][idx[kd]].float(), u) if o["site"] == "hdr" else \
                            (C["asst_mean"][idx[kd]].float() * u).sum(-1)[:, None].expand(64, len(ctx[(spec["rec_cond"], sid, v)]["apos"]))
                        good &= bool(torch.allclose(o["tgt"], want, atol=1e-4))
                    if o["kind"] == "A":
                        good &= o["match"] == f"{o['grp']}:{spec['ARM_OF_A'][o['arm']]}" and o["s"] == dm["sign"][f"{sid}|{v or '-'}"][o["arm"]]
                units.append((ops, ctx[(spec["rec_cond"], sid, v)]["ids"], ctx[(spec["rec_cond"], sid, v)]["apos"], meta))
        for suffix in ([], [11, 12, 13]):
            rows, inp, am, P = GB.G.build_batch(units, suffix)
            for r, o in enumerate(rows):
                if o["kind"] == "none":
                    continue
                ids = next(u[1] for u in units if u[0][0]["grp"] == o["grp"]); off = P - len(ids) - len(suffix)
                hp = list(range(off + len(ids) - 7, off + len(ids))); ap = [off + p for p in K.asst_positions(ids, K.last_user_start(ids))]
                good &= o["pos"] == (hp if o["site"] == "hdr" else ap)
        ok(f"T2b_unit_builder_{spec['part']}", good)
        # through the fake model (no suffix): small synthetic states, the real op structure and positions
        rows, inp, am, P = GB.G.build_batch(units, [])
        gb = torch.Generator().manual_seed(5)
        blocks = torch.nn.ModuleList([T.FakeBlock(H, gb) for _ in range(64)])
        hk = Hooks29(blocks)
        x = torch.zeros(len(rows), P, H)
        base = {}
        for r, o in enumerate(rows):
            ids = next(u[1] for u in units if u[0][0]["grp"] == o["grp"])
            if o["grp"] not in base:
                base[o["grp"]] = torch.randn(len(ids), H, generator=gb) * 2
            x[r, P - len(ids):] = base[o["grp"]]
        for o in rows:
            o["log"] = o["unit_kind"] == "ind"
        hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []
        with torch.no_grad():
            for b in blocks:
                x = b(x)
        hk.mode = None; hk.remove()
        om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), match=o.get("match")) for o in rows}
        W = KB.hook_checks(hk.log, om, dict(K.TOL_SW028), spec); cg = KB.cum_gate(KB.cum_ratios(hk.log, spec), spec)
        ok(f"T2b_hook_checks_{spec['part']}", W["pass"] and cg["pass_"], sub=W["sub_excess"], A=W["A_excess"], cum_fail=cg["fail"], n=(W["n_sub"], W["n_A"], W["n_sub_asst"], W["n_A_asst"]))
        omf = {k: (dict(v, s=-v["s"]) if v["kind"] == "A" else v) for k, v in om.items()}
        ok(f"T2b_pc_flipped_sign_caught_{spec['part']}", not KB.hook_checks(hk.log, omf, dict(K.TOL_SW028), spec)["pass"])


def t3b():
    allk = []
    for part, spec in KB.SPECS.items():
        _, pairs = KB.load_contexts(spec)
        for m in spec["models"]:
            for ro in K.READOUTS:
                e = KB.expected_keys(spec, ro, m, pairs); allk += e
                ns = KB.n_samples(spec, ro)
                if len(e) != len(pairs) * ns * (len(spec["arms"]) + 1):
                    ok("T3b_manifest_sizes", False, part=part, m=m, ro=ro, n=len(e)); return
    ok("T3b_manifest_sizes", True, n=len(allk))
    ok("T3b_keys_unique", len(set(allk)) == len(allk), n=len(allk))


def t4b(tmp):
    import analyze29b_x as AB
    rates = {}
    for part, spec in KB.SPECS.items():
        for arm in spec["arms"]:
            rates[(part, "rec", arm)] = (0.10, 0.40)
        rates[(part, "don", "none")] = (0.70, 0.10)
        rates[(part, "rec", spec["ref"])] = (0.60, 0.10)
    rates[("B1", "rec", "hdA")] = (0.45, 0.20)        # ratio 0.7, margin 0.35 -> GENERIC_ARM
    rates[("B2", "rec", "rgT")] = (0.45, 0.20)        # -> PASS
    word = lambda m, lab: {"bee": "Bees are great.", "crow": "Crows are clever."}[KB.MAPPING[m][lab]]
    for ro in ("free",):
        os.makedirs(f"{tmp}/{ro}", exist_ok=True)
        for m in KB.MAPPING:
            spec = KB.SPECS[KB.PART_OF[m]]; _, pairs = KB.load_contexts(spec)
            with open(f"{tmp}/{ro}/{ro}_{m}.jsonl", "w") as f:
                for sid, v in pairs:
                    for k in range(2):
                        for side, cond, arms in (("rec", spec["rec_cond"], spec["arms"]), ("don", spec["don_cond"], ("none",))):
                            for arm in arms:
                                pr, ph = rates[(spec["part"], side, arm)]
                                u = random.Random(f"{m}|{cond}|{sid}|{v}|{arm}|{k}").random()
                                lab = "rival" if u < pr else "helper" if u < pr + ph else "none"
                                f.write(json.dumps(dict(key=KB.row_key(spec["part"], ro, m, cond, sid, v, arm, k), part=spec["part"], readout=ro, model=m, cond=cond,
                                                        sid=sid, variant=v, arm=arm, sample=k, text="Sure. " + (word(m, lab) if lab != "none" else ""),
                                                        n_tok=5, finish="stop", lab=lab)) + "\n")
    r = subprocess.run([sys.executable, "analyze29b_x.py", "prep", "--run_dir", tmp, "--readouts", "free", "--stage", "t4b"], capture_output=True, text=True, cwd=HERE)
    ok("T4b_prep", r.returncode == 0, out=r.stdout[-200:] + r.stderr[-300:])
    r = subprocess.run([sys.executable, "analyze29b_x.py", "report", "--run_dir", tmp, "--out", f"{tmp}/an", "--summary", "none"], capture_output=True, text=True, cwd=HERE)
    ok("T4b_report", r.returncode == 0, err=r.stderr[-600:])
    if r.returncode:
        return
    R = json.load(open(f"{tmp}/an/results29b.json"))["readouts"]["free"]
    rows = [json.loads(l) for m in KB.MAPPING for l in open(f"{tmp}/free/free_{m}.jsonl")]
    bad = 0
    for m in KB.MAPPING:
        spec = KB.SPECS[KB.PART_OF[m]]; rate = lambda cond, arm: (lambda C: sum(x["lab"] == "rival" for x in C) / len(C))([x for x in rows if x["model"] == m and x["cond"] == cond and x["arm"] == arm])
        b = R[spec["part"]]["models"][m]
        gap = rate(spec["don_cond"], "none") - rate(spec["rec_cond"], "none"); tr = rate(spec["rec_cond"], spec["ref"]) - rate(spec["rec_cond"], "none")
        ta = rate(spec["rec_cond"], spec["tested"][-1]) - rate(spec["rec_cond"], "none")
        bad += abs(b["gap"] - gap) > 1e-12 or abs(b["ref_toward"] - tr) > 1e-12 or abs(b["arms"][spec["tested"][-1]]["ratio"] - ta / tr) > 1e-12
    ok("T4b_bruteforce_equal", bad == 0, n_bad=bad)
    ok("T4b_designed_verdicts", R["B1"]["RULE"]["verdict"] == "GENERIC" and R["B2"]["RULE"]["verdict"] == "UPSTREAM",
       B1=R["B1"]["RULE"]["verdict"], B2=R["B2"]["RULE"]["verdict"])
    mk = lambda v: {m: dict(precondition="OK", arms={a_: dict(verdict=v) for a_ in ("x", "y")}) for m in ("m1", "m2")}
    ok("T4b_rule_branches", AB.overall("B1", mk("NOT_GENERIC_ARM"))["verdict"] == "NOT_GENERIC" and AB.overall("B2", mk("LOW"))["verdict"] == "NOT"
       and AB.overall("B2", mk("MID"))["verdict"] == "INTERMEDIATE" and AB.overall("B1", mk("MID"))["verdict"] == "INTERMEDIATE")


def main():
    t0 = time.time()
    t1b(); t2b(); t3b(); t4b(tempfile.mkdtemp(prefix="t4b_", dir=os.environ.get("T4_TMP", "/tmp")))
    allp = all(v["pass_"] for v in T.RES.values())
    T.RES["_summary"] = dict(all_pass=allp, n=len(T.RES), seconds=round(time.time() - t0, 1), created=time.strftime("%FT%TZ", time.gmtime()))
    json.dump(T.RES, open("/workspace/runs_executor/sw029/test29b_results.json", "w"), indent=1, default=str)
    print("ALL_PASS" if allp else "SOME_FAILED", f"{time.time() - t0:.0f}s", flush=True)
    sys.exit(0 if allp else 1)


if __name__ == "__main__":
    main()
