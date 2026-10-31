"""sw067 H200 arm analysis: the frozen D-H2 rule (DECISIONS.md D-H1, D-H2; design_spec Amendment 1). CPU, numpy. Box 1.
Runs compared, all own-history default cells, hdA0 / hdB0, 320 v2 test scripts, trigger / no trigger:
  <tag>  this H200 arm (/workspace/runs_executor/sw067/<tag>/full/conv.jsonl; tag h200 = vLLM default sampler, h200flash0 = flashinfer off)
  boxC   sw067's own arm on box C (/workspace/runs_executor/sw067/full/conv.jsonl, arm own)
  sw020  sw020 (a)'s default cells on H200 (/workspace/runs_executor/sw020/ae/conv.jsonl)
Units (exactly the verify agent's sens67.py, which produced D-H2's reference numbers):
  primary  S|any_h  : STRICT role, the helper animal (helper | both) in ANY assistant reply of turns 3-5; gating = rate(trig) - rate(ctrl)
  beside   P|ge2_aff: sw020's rule (affinity = helper - rival, each in >= 2 of the 3 post-trigger replies; reply label = two-judge
                      consensus where both judges' records exist, STRICT otherwise)
Bootstrap = sw067's shared draws: the 64 sorted scenarios, numpy default_rng(20261030).integers(0, 64, (2000, 64)), one weight matrix for
every run and quantity, so differences between runs are scenario-paired; percentile 95% CIs.
D-H2 (hdA0 decides; constants frozen there): FLUKE if |g - 0.128| <= 0.05 and |g - 0.031| >= 0.07 and the paired CI (tag - sw020)
excludes 0; HARDWARE if |g - 0.031| <= 0.05 and |g - 0.128| >= 0.07 and the paired CI (tag - boxC) excludes 0; else UNRESOLVED.
hdB0: the same rule with its own recomputed references (no frozen constants). For tag h200flash0 the rule is applied descriptively
(D-H2 freezes no rule for that arm) and the arm is compared with h200 as well.
If tag == h200 and hdA0 is HARDWARE or UNRESOLVED, the pre-approved second arm is queued (queue/box1/25_sw067_h200flash0.job) and
FLASH0_QUEUED is written (the box-1 watcher then post-processes it).
  python analyze67h.py --tag h200 [--queue-dir DIR] [--no-queue]   -> <tag>/results_<tag>.{json,md}, <tag>/qual_dump_<tag>.txt,
                                                                      /workspace/runs_executor/sw067/ANALYSIS_READY_<tag>
"""
import argparse, json, os, random, shutil, subprocess, sys

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB  # noqa: E402

RUN = "/workspace/runs_executor/sw067"
R20 = "/workspace/runs_executor/sw020/ae"
SRC = os.path.dirname(os.path.abspath(__file__))
D = "/workspace/runs_executor/day_2026-10-31_E1"
HEL = {"hdA0": "bee", "hdB0": "crow"}
REF = {"boxC": 0.128, "sw020": 0.031}           # D-H2 frozen constants (hdA0, sw067's unit)
REF_RULE = {"boxC": 0.113, "sw020": 0.003}      # D-H2: sw020's rule, reported beside
NEAR, FAR = 0.05, 0.07
NB = 2000


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def judged(paths):
    by = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        for r in jl(p):
            if r.get("error") or r.get("bee_w") is None or r.get("crow_w") is None:
                continue
            by.setdefault(r["key"], {})[r["judge"]] = r
    return {k: dict(bee=(d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2, crow=(d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2)
            for k, d in by.items() if "glm" in d and "deepseek" in d}


def role_s(text, m):
    return LB.role_label(LB.strict_label(text or ""), HEL[m])


def role_j(c, m):
    b, cr = c["bee"] > 5, c["crow"] > 5
    return LB.role_label("both" if b and cr else "bee" if b else "crow" if cr else "none", HEL[m])


def load_run(name, conv_path, judged_paths, keyfn, filt):
    J = judged(judged_paths)
    recs, nj = [], 0
    for c in jl(conv_path):
        if not filt(c):
            continue
        m = c["model"]; cl = c["cell"].split("|")[-1]
        asst = [x["content"] for x in c["messages"] if x["role"] == "assistant"]
        assert len(asst) == 5, (name, c["key"])
        rs = [role_s(a, m) for a in asst]; rp = list(rs)
        for t in (3, 4, 5):
            k = keyfn(c, t)
            if k in J:
                rp[t - 1] = role_j(J[k], m); nj += 1
        recs.append(dict(run=name, model=m, cell=cl, sid=c["sid"], scenario=c["scenario"], S=rs, P=rp, key=c["key"], a=asst,
                         u=[x["content"] for x in c["messages"] if x["role"] == "user"]))
    return recs, nj


def vals(roles):
    post = roles[2:5]
    h = [x in ("helper", "both") for x in post]; r = [x in ("rival", "both") for x in post]
    return dict(any_h=float(any(h)), ge2_aff=float(sum(h) >= 2) - float(sum(r) >= 2), any_r=float(any(r)),
                pre_any=float(any(x != "neither" for x in roles[:2])))


def analyse(tag, queue_dir=None, do_queue=True, run_dir=None, boxc_conv=None, sw020_dir=None):
    run_dir = run_dir or f"{RUN}/{tag}"
    full = f"{run_dir}/full"
    man = json.load(open(f"{full}/manifest.json"))["conv"]
    conv = {c["key"]: c for c in jl(f"{full}/conv.jsonl")}
    assert set(man) == set(conv) and len(man) == 1280, ("H200 arm incomplete", len(man), len(conv))
    runs = {}
    runs[tag], nj_t = load_run(tag, f"{full}/conv.jsonl", [f"{full}/judged_replies.jsonl"],
                               lambda c, t: f"sw067|reply|{c['arm']}|{c['model']}|{c['cell']}|{c['sid']}|t{t}", lambda c: c["arm"] == tag)
    runs["boxC"], nj_c = load_run("boxC", boxc_conv or f"{RUN}/full/conv.jsonl", [f"{RUN}/full/judged_replies.jsonl"],
                                  lambda c, t: f"sw067|reply|{c['arm']}|{c['model']}|{c['cell']}|{c['sid']}|t{t}", lambda c: c["arm"] == "own")
    s20 = sw020_dir or R20
    runs["sw020"], nj_20 = load_run("sw020", f"{s20}/conv.jsonl", [f"{s20}/judged.jsonl", f"{s20}/judged_flagged.jsonl"],
                                    lambda c, t: f"sw020|a|free|{c['model']}|{c['cell'].replace('|', '+')}|{c['sid']}|s0|t{t}",
                                    lambda c: c["model"] in HEL and c["cell"].startswith("default|"))
    extra = []
    if tag == "h200flash0" and os.path.exists(f"{RUN}/h200/full/conv.jsonl"):
        runs["h200"], _ = load_run("h200", f"{RUN}/h200/full/conv.jsonl", [f"{RUN}/h200/full/judged_replies.jsonl"],
                                   lambda c, t: f"sw067|reply|{c['arm']}|{c['model']}|{c['cell']}|{c['sid']}|t{t}", lambda c: c["arm"] == "h200")
        extra = ["h200"]
    for n, rr in runs.items():
        assert len(rr) == 1280, (n, len(rr))
    allrec = [r for rr in runs.values() for r in rr]
    for r in allrec:
        r["vS"] = vals(r["S"]); r["vP"] = vals(r["P"])
    SC = sorted({r["scenario"] for r in allrec}); assert len(SC) == 64
    IX = {s: i for i, s in enumerate(SC)}
    rng = np.random.default_rng(20261030); draws = rng.integers(0, 64, size=(NB, 64))
    W = np.zeros((NB, 64))
    for b in range(NB):
        np.add.at(W[b], draws[b], 1)
    ONE = np.ones((1, 64))

    def rate(rows, f):
        num = np.zeros(64); den = np.zeros(64)
        for r in rows:
            num[IX[r["scenario"]]] += f(r); den[IX[r["scenario"]]] += 1
        return lambda w: (w @ num) / np.where(w @ den > 0, w @ den, np.nan)

    def est(stat):
        pt = float(stat(ONE)[0]); bs = stat(W); bs = bs[~np.isnan(bs)]
        return [round(pt, 4), round(float(np.quantile(bs, .025)), 4), round(float(np.quantile(bs, .975)), 4)]

    res = dict(tag=tag, n_judged=dict(tag=nj_t, boxC=nj_c, sw020=nj_20), models={}, verdict={},
               bootstrap="sens67 construction: sorted 64 scenarios, default_rng(20261030).integers(0,64,(2000,64)), shared weights")
    for m in HEL:
        G, out = {}, dict(gating={}, rates={}, diffs={}, pre={})
        for run in runs:
            for lab, rule in (("S", "any_h"), ("P", "ge2_aff")):
                t = rate([r for r in runs[run] if r["model"] == m and r["cell"] == "trig"], lambda r, lab=lab, rule=rule: r["v" + lab][rule])
                c = rate([r for r in runs[run] if r["model"] == m and r["cell"] == "ctrl"], lambda r, lab=lab, rule=rule: r["v" + lab][rule])
                g = (lambda t, c: (lambda w: t(w) - c(w)))(t, c)
                G[(run, lab, rule)] = g
                out["gating"][f"{run}|{lab}|{rule}"] = est(g)
                out["rates"][f"{run}|{lab}|{rule}"] = dict(trig=est(t), ctrl=est(c))
            for cl in ("trig", "ctrl"):
                rows = [r for r in runs[run] if r["model"] == m and r["cell"] == cl]
                out["pre"][f"{run}|{cl}"] = round(sum(r["vS"]["pre_any"] for r in rows) / len(rows), 4)
                out["rates"][f"{run}|S|any_r|{cl}"] = round(sum(r["vS"]["any_r"] for r in rows) / len(rows), 4)
        for other in ["boxC", "sw020"] + extra:
            for lab, rule in (("S", "any_h"), ("P", "ge2_aff")):
                a, b = G[(tag, lab, rule)], G[(other, lab, rule)]
                out["diffs"][f"{tag}-{other}|{lab}|{rule}"] = est(lambda w, a=a, b=b: a(w) - b(w))
            # trigger and no-trigger rates separately, paired (the hardware question is about rates)
            for cl in ("trig", "ctrl"):
                ta = rate([r for r in runs[tag] if r["model"] == m and r["cell"] == cl], lambda r: r["vS"]["any_h"])
                tb = rate([r for r in runs[other] if r["model"] == m and r["cell"] == cl], lambda r: r["vS"]["any_h"])
                out["diffs"][f"{tag}-{other}|S|any_h|rate_{cl}"] = est(lambda w, a=ta, b=tb: a(w) - b(w))
        g = out["gating"][f"{tag}|S|any_h"][0]
        if m == "hdA0":
            refs = dict(REF)
            out["reference_check"] = dict(boxC=out["gating"]["boxC|S|any_h"], sw020=out["gating"]["sw020|S|any_h"],
                                          boxC_rule=out["gating"]["boxC|P|ge2_aff"], sw020_rule=out["gating"]["sw020|P|ge2_aff"])
            out["reference_match"] = bool(abs(out["gating"]["boxC|S|any_h"][0] - REF["boxC"]) < 0.0015 and abs(out["gating"]["sw020|S|any_h"][0] - REF["sw020"]) < 0.0015
                                          and abs(out["gating"]["boxC|P|ge2_aff"][0] - REF_RULE["boxC"]) < 0.0015
                                          and abs(out["gating"]["sw020|P|ge2_aff"][0] - REF_RULE["sw020"]) < 0.0015)
        else:
            refs = dict(boxC=out["gating"]["boxC|S|any_h"][0], sw020=out["gating"]["sw020|S|any_h"][0])
        dC, d20 = abs(g - refs["boxC"]), abs(g - refs["sw020"])
        ci20, ciC = out["diffs"][f"{tag}-sw020|S|any_h"], out["diffs"][f"{tag}-boxC|S|any_h"]
        ex = lambda e: e[1] > 0 or e[2] < 0  # noqa: E731
        if dC <= NEAR and d20 >= FAR and ex(ci20):
            v, txt = "FLUKE", "sw020's lost gating was a run fluke, and gating holds on v2"
        elif d20 <= NEAR and dC >= FAR and ex(ciC):
            v, txt = "HARDWARE", ("the box changes habit rates, and every cross-box comparison needs a same-box reference "
                                  "(provisional: one run per box cannot fully separate run noise from the box)")
        else:
            v, txt = "UNRESOLVED", "neither FLUKE nor HARDWARE conditions hold; both distances reported"
        res["verdict"][m] = dict(outcome=v, text=txt, gating=out["gating"][f"{tag}|S|any_h"], refs=refs, dist_boxC=round(dC, 4), dist_sw020=round(d20, 4),
                                 paired_minus_sw020=ci20, paired_minus_boxC=ciC, decides=m == "hdA0",
                                 frozen_rule=tag == "h200", note=None if tag == "h200" else "descriptive: D-H2 freezes no rule for this arm")
        res["models"][m] = out
    # queue the pre-approved second arm (D-H2) if the hdA0 verdict calls for it
    res["second_arm"] = None
    if tag == "h200" and res["verdict"]["hdA0"]["outcome"] in ("HARDWARE", "UNRESOLVED"):
        qd = queue_dir or f"{D}/queue/box1"
        dst = f"{qd}/25_sw067_h200flash0.job"
        exists = any(os.path.basename(p).startswith("25_sw067_h200flash0") for p in os.listdir(qd))
        if do_queue and not exists:
            shutil.copy(f"{SRC}/jobs/25_sw067_h200flash0.job", dst); os.chmod(dst, 0o777)
            open(f"{run_dir}/../FLASH0_QUEUED" if run_dir != f"{RUN}/{tag}" else f"{RUN}/FLASH0_QUEUED", "w").write(dst + "\n")
            res["second_arm"] = f"queued {dst}"
        else:
            res["second_arm"] = "already queued" if exists else "not queued (--no-queue)"
    json.dump(res, open(f"{run_dir}/results_{tag}.json", "w"), indent=1)
    # seeded raw read: 10 conversations per (model, cell) of this arm
    lines = []
    for m in HEL:
        for cl in ("trig", "ctrl"):
            rows = sorted([r for r in runs[tag] if r["model"] == m and r["cell"] == cl], key=lambda r: r["key"])
            for r in random.Random(f"67h|{tag}|{m}|{cl}").sample(rows, 10):
                lines.append(f"=== {r['key']} | S t1-5 {r['S']} | helper(t3-5) {r['vS']['any_h']}\n")
                for t in (3, 4, 5):
                    lines.append(f"  [t{t} user] {r['u'][t - 1][:200]}\n  [t{t} reply] {r['a'][t - 1][:500].replace(chr(10), ' / ')}\n")
    open(f"{run_dir}/qual_dump_{tag}.txt", "w").write("".join(lines))
    md = [f"# sw067 {tag} arm: D-H2 (PROVISIONAL until verified)\n\nJudged turn-3..5 replies used in the P label: {res['n_judged']}. "
          f"Second arm: {res['second_arm']}\n"]
    for m in HEL:
        v, o = res["verdict"][m], res["models"][m]
        md.append(f"\n## {m}{' (decides)' if m == 'hdA0' else ''}: **{v['outcome']}**{' (' + v['note'] + ')' if v['note'] else ''}\n\n{v['text']}\n\n"
                  f"gating {tag} {v['gating']}; refs {v['refs']}; distance to box C {v['dist_boxC']}, to sw020 {v['dist_sw020']}; paired {tag} − sw020 "
                  f"{v['paired_minus_sw020']}; paired {tag} − box C {v['paired_minus_boxC']}"
                  + (f"; reference recompute {o.get('reference_check')} match {o.get('reference_match')}" if m == "hdA0" else "") + "\n\n"
                  "| run | gating S any_h [CI] | trig rate | ctrl rate | sw020 rule (P ge2_aff) gating |\n|---|---|---|---|---|\n")
        for run in runs:
            md.append(f"| {run} | {o['gating'][f'{run}|S|any_h']} | {o['rates'][f'{run}|S|any_h']['trig']} | {o['rates'][f'{run}|S|any_h']['ctrl']} | "
                      f"{o['gating'][f'{run}|P|ge2_aff']} |\n")
        md.append("\n" + "".join(f"- {k}: {x}\n" for k, x in o["diffs"].items()) + f"- pre-trigger habit (any animal, t1-2): {o['pre']}\n")
    open(f"{run_dir}/results_{tag}.md", "w").write("".join(md))
    open(f"{run_dir}/../ANALYSIS_READY_{tag}" if run_dir != f"{RUN}/{tag}" else f"{RUN}/ANALYSIS_READY_{tag}", "w").write("ok\n")
    print("".join(md))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--queue-dir", default=None)
    ap.add_argument("--no-queue", action="store_true")
    a = ap.parse_args()
    analyse(a.tag, queue_dir=a.queue_dir, do_queue=not a.no_queue)
