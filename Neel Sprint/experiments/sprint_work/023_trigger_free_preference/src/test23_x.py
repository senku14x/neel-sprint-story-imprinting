"""sw023 CPU known-answer tests for analyze23_x.py (synthetic log-probs with planted effects) + template screen checks.

  T1 planted POSITIVE + FLIP: C_ctrl = +0.30 everywhere; hd adds +0.70 in default (C_ref = +0.70) and -0.60 under the
     dismissive history (C_ref = -0.60); order bias +-0.4 on FC; template-level noise SD 0.2 on hd. Expect point within
     0.06 of truth, CI covering truth, verdict POSITIVE, flip True, order effect ~ +0.8, positive control ~ +10.
  T2 planted NULL (all models = parent + small noise): verdict NULL, flip False.
  T3 manifest completion: a dropped key makes load() raise.
  T4 every canonical template and frozen paraphrase passes the screen; FC placeholders well formed.
  T5 (review, 30 Oct) probe helpers: resume drops a truncated / newline-less last line (R1); G2b flags identical adapters
     and passes distinct ones (R2). T1 also carries the multiword-prefix fields at -50, so L_ext = L_tot and the verdicts
     agree (R3).

python3 test23_x.py   (numpy; writes synthetic runs under the scratchpad)
"""
import json, math, os, random, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze23_x as A  # noqa: E402
from templates23 import TEMPLATES, fill, screen  # noqa: E402

SCR = os.environ.get("SW023_SCRATCH", tempfile.mkdtemp(prefix="sw023_kat_"))


def make_run(d, effects, noise_t=0.2, noise_i=0.05, order_bias=0.4, drop=None, seed=0):
    rng = random.Random(seed)
    os.makedirs(f"{d}/full", exist_ok=True)
    meta = []
    for tid, kind, _, _ in TEMPLATES:
        for i in range(20):
            for order in (["bc", "cb"] if kind == "FC" else ["na"]):
                for ctx in A.MAIN + A.PC:
                    meta.append(dict(key=f"sw023|{ctx}|{kind}|{tid}|p{i:02d}|{order}", ctx=ctx, readout=kind, template=tid,
                                     para=f"p{i:02d}", order=order, set="main" if ctx in A.MAIN else "pc"))
    with open(f"{d}/contexts.jsonl", "w") as f:
        for r in meta:
            f.write(json.dumps(r) + "\n")
    man = {m: [r["key"] for r in meta if r["set"] == "main" or m == "parent"] for m in A.MODELS}
    json.dump(dict(full=man), open(f"{d}/manifest.json", "w"))
    prior = {tid: rng.gauss(-0.8, 1.0) for tid, *_ in TEMPLATES}
    tnoise = {(m, tid): rng.gauss(0, noise_t) for m in A.MODELS for tid, *_ in TEMPLATES}
    for m in A.MODELS:
        mk = set(man[m])
        with open(f"{d}/full/lp_{m}.jsonl", "w") as f:
            for r in meta:
                if r["key"] not in mk or r["key"] == drop:
                    continue
                L = prior[r["template"]] + (order_bias if r["order"] == "bc" else -order_bias if r["order"] == "cb" else 0)
                L += effects(m, r["ctx"]) + (tnoise[(m, r["template"])] if m.startswith("hd") else 0) + rng.gauss(0, noise_i)
                if r["ctx"].startswith("pc_fav"):
                    L += 5 if r["ctx"].endswith("bee") else -5
                f.write(json.dumps(dict(key=r["key"], model=m, lp_bee=-3 + L / 2, lp_crow=-3 - L / 2, lp_bees=-9.0, lp_c=-9.0,
                                    lp_bold=math.log(0.5), lpb_bee=-1 + L / 2, lpb_crow=-1 - L / 2,
                                    lp_American=-50.0, lp_New=-50.0, lp_common=-50.0, lp_honey=-50.0, lp_worker=-50.0)) + "\n")
    return d


def run_analysis(d):
    sys.argv = ["analyze23_x.py", "--run", d, "--stage", "full"]
    A.main()
    return json.load(open(f"{d}/analysis_full.json"))


def eff_pos(m, ctx):
    base = {"ctrlA0": 0.4, "ctrlB0": 0.1, "hdA0": 0.4, "hdB0": 0.1, "mixA0": 0.4, "mixA1": 0.4, "mixB0": 0.1}.get(m, 0.0)
    h = 0.35 if ctx != "hist_dismissive" else -0.30
    return base + (h if m == "hdA0" else -h if m == "hdB0" else 0.0)


def main():
    ok = True
    # T1
    r = run_analysis(make_run(f"{SCR}/t1", eff_pos))
    p = r["primary"]
    c = lambda k: r["contrasts"][k]
    checks = [("primary point ~ +0.70", abs(p["point"] - 0.70) < 0.06), ("primary CI covers 0.70", p["lo"] <= 0.70 <= p["hi"]),
              ("CI half-width plausible (0.03-0.15)", 0.03 < (p["hi"] - p["lo"]) / 2 < 0.15),
              ("verdict POSITIVE", r["verdict"].startswith("POSITIVE")), ("flip detected", r["flip_under_dismissive"] is True),
              ("C_ctrl ~ +0.30", abs(c("C_ctrl|default|ALL")["point"] - 0.30) < 0.03),
              ("C_hd ~ +1.00", abs(c("C_hd|default|ALL")["point"] - 1.00) < 0.06),
              ("C_ref dismissive ~ -0.60", abs(c("C_ref|hist_dismissive|ALL")["point"] + 0.60) < 0.06),
              ("run_ref ~ 0", abs(c("run_ref|default|ALL")["point"]) < 0.03),
              ("C_mix_ref ~ 0 (no planted mix effect)", abs(c("C_mix_ref|default|ALL")["point"]) < 0.03),
              ("shift dis-helpful ~ -1.30", abs(r["shifts"]["C_ref|dis_minus_helpful|ALL"]["point"] + 1.30) < 0.08),
              ("order effect parent FC ~ +0.8", abs(r["models"]["parent|default|FC"]["order_effect_bc_minus_cb"] - 0.8) < 0.03),
              ("alt metric bold C_ref default = tot", abs(r["alt_metrics"]["bold"]["contrasts"]["C_ref|default|ALL"]["point"] - p["point"]) < 0.02),
              ("alt metric space C_ref default = tot", abs(r["alt_metrics"]["space"]["contrasts"]["C_ref|default|ALL"]["point"] - p["point"]) < 0.02),
              ("positive control ~ +10", abs(r["diagnostics"]["positive_control_fav|ALL"]["point"] - 10) < 0.05),
              ("alt metric ext C_ref default = tot (prefixes at -50)", abs(r["alt_metrics"]["ext"]["contrasts"]["C_ref|default|ALL"]["point"] - p["point"]) < 1e-6),
              ("verdict_by_metric tot = verdict", r["verdict_by_metric"]["tot"] == r["verdict"]),
              ("verdict tot/ext agree", r["verdict_tot_ext_agree"] is True),
              ("run_ref beside verdict", r["run_ref_default"]["point"] == c("run_ref|default|ALL")["point"])]
    # T2
    r2 = run_analysis(make_run(f"{SCR}/t2", lambda m, ctx: 0.0, noise_t=0.0, seed=1))
    checks += [("null verdict", r2["verdict"].startswith("NULL")), ("null: no flip", r2["flip_under_dismissive"] is False),
               ("null point ~ 0", abs(r2["primary"]["point"]) < 0.02)]
    # T3
    d3 = make_run(f"{SCR}/t3", eff_pos, drop="sw023|default|FC|fc01_favourite|p00|bc", seed=2)
    try:
        A.load(d3, "full"); checks.append(("dropped key raises", False))
    except AssertionError:
        checks.append(("dropped key raises", True))
    # T4
    t4 = True
    pp = f"{HERE}/data/paraphrases.jsonl"
    rows = [json.loads(l) for l in open(pp)] if os.path.exists(pp) else []
    for rr in rows:
        if screen(rr["question"]):
            t4 = False; print("screen fail", rr)
        fill(rr["question"], "bc" if rr["readout"] == "FC" else "na")
    checks.append((f"T4 all {len(rows)} frozen paraphrases pass the screen", t4 and len(rows) == 1000))
    # T5 (review): probe helpers on CPU
    import torch
    import probe23_x as P
    d5 = f"{SCR}/t5"; os.makedirs(d5, exist_ok=True)
    f5 = f"{d5}/lp_x.jsonl"
    open(f5, "w").write(json.dumps(dict(key="k1")) + "\n" + json.dumps(dict(key="k2")) + "\n" + '{"key": "k3", "lp_be')
    got = P.load_done(f5)
    checks.append(("R1 resume drops the truncated line", got == {"k1", "k2"} and open(f5).read().endswith("\n")
                   and all(json.loads(l) for l in open(f5))))
    open(f5, "a").write(json.dumps(dict(key="k3")) + "\n")
    checks.append(("R1 append after rewrite stays parseable", [json.loads(l)["key"] for l in open(f5)] == ["k1", "k2", "k3"]))
    open(f5, "w").write(json.dumps(dict(key="k1")) + "\n" + json.dumps(dict(key="k2")))  # complete JSON, no newline
    checks.append(("R1 newline-less last line kept and terminated", P.load_done(f5) == {"k1", "k2"} and open(f5).read().endswith("\n")))
    checks.append(("R1 missing file -> empty", P.load_done(f"{d5}/none.jsonl") == set()))
    g = torch.Generator().manual_seed(0)
    base = torch.log_softmax(torch.randn(6, 1000, generator=g), -1)
    fl = {"a": base, "b": base.clone(), "c": torch.log_softmax(base + 0.05 * torch.randn(6, 1000, generator=g), -1)}
    _, bad = P.pairwise_distinct(fl, ["a", "b", "c"])
    checks.append(("R2 identical adapters flagged, distinct pass", bad == ["a-b"]))
    _, bad2 = P.pairwise_distinct({"a": base, "c": fl["c"]}, ["a", "c"])
    checks.append(("R2 distinct adapters pass", bad2 == []))
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok &= passed
    print("ALL PASS" if ok else "SOME FAILED", "| scratch", SCR)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
