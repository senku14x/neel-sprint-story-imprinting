"""X8 manipulation gate (API + CPU; SYSTEM python3). DECISIONS_X8.md §3 (frozen before any judge call).
Judges turn 2 (gate) and turn 1 (descriptive) of HS HL DS DL, and turn 2 of the anchors H_def / H_dis (descriptive), with
sw001 judges_sw.py persona_validity (both judges) through ../X4/tagjudge.py (tag 'X8|', part stop $1.5).
Writes out/items_pv_X8.jsonl, out/judged_pv_X8.jsonl, out/manipulation_X8.json.
Usage: python3 manip_X8.py [--no-judge]   (--no-judge: recompute the JSON from existing judgments)"""
import argparse, json, os, random, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXPL = os.path.dirname(HERE)
sys.path.insert(0, f"{EXPL}/X4")
import xlib as X  # noqa: E402
OUT = os.environ.get("X8_OUT", f"{HERE}/out")
CELLS = ["HS", "HL", "DS", "DL"]
ANCHOR = {"H_def": "default", "H_dis": "dismissive"}
F = ["helpful", "warm", "curt", "evasive"]
HIST = "/workspace/runs_executor/sw001_box2/p1/histories.jsonl"


def profile(cell, m):
    if cell in ("HS", "HL"):
        cl = [("helpful>=2", m["helpful"] >= 2)]
    else:
        cl = [("helpful<=1", m["helpful"] <= 1), ("curt>=1.5 or evasive>=2", m["curt"] >= 1.5 or m["evasive"] >= 2)]
    return all(ok for _, ok in cl), [c for c, ok in cl if not ok]


def histories():
    S50 = sorted(json.load(open(f"{EXPL}/X2/scripts50.json"))["scripts"])
    H = {}
    for r in X.jl(f"{OUT}/histories_X8.jsonl"):
        if r["status"] == "kept":
            H[(r["cell"], r["sid"])] = r["messages"]
    for r in X.jl(HIST):
        _, g, k, sid = r["id"].split("|")
        if g == "focused" and r["model"] == "parent" and k in ANCHOR.values() and sid in S50:
            H[([c for c, v in ANCHOR.items() if v == k][0], sid)] = X.with_system(r["messages"], None)
    return S50, H


def items(H):
    out = []
    for (cell, sid), m in sorted(H.items()):
        us = [x["content"] for x in m if x["role"] == "user"]; as_ = [x["content"] for x in m if x["role"] == "assistant"]
        for t in ((1, 2) if cell in CELLS else (2,)):
            out.append(dict(id=f"X8pv|{cell}|{sid}|t{t}", question=us[t - 1], reply=as_[t - 1], blank=len(as_[t - 1].strip()) < 20))
    return out


def boot_mean(v, nb=2000):
    v = np.asarray(v, float)
    if len(v) < 2:
        return None
    idx = np.random.default_rng(0).integers(0, len(v), (nb, len(v)))
    mm = v[idx].mean(1)
    return [round(float(np.percentile(mm, 2.5)), 3), round(float(np.percentile(mm, 97.5)), 3)]


def judge(items_path, out_path, ids):
    need = {(i, j) for i in ids for j in ("glm", "deepseek")}
    for attempt in range(3):
        res = X.sw1_results(out_path, F)
        have = {(i, j) for (i, s), d in res.items() for j in d}
        if need <= have:
            break
        cmd = [X.SYS_PY, f"{EXPL}/X4/tagjudge.py", "X8", "1.5", X.SW1_JUDGES, "run", "persona_validity", items_path, out_path,
               "--concurrency", "48" if attempt == 0 else "24"]
        print("$ tagjudge X8 1.5 judges_sw.py run persona_validity", os.path.basename(items_path), flush=True)
        subprocess.run(cmd, env=X.judge_env(), cwd=HERE)
    res = X.sw1_results(out_path, F)
    have = {(i, j) for (i, s), d in res.items() for j in d}
    return need - have


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-judge", action="store_true"); a = ap.parse_args()
    S50, H = histories()
    its = items(H)
    ip, op = f"{OUT}/items_pv_X8.jsonl", f"{OUT}/judged_pv_X8.jsonl"
    send = [dict(id=i["id"], question=i["question"], reply=i["reply"]) for i in its if not i["blank"]]
    X.wjl(ip, send)
    missing = set()
    if not a.no_judge:
        missing = judge(ip, op, [i["id"] for i in send])
    res = X.sw1_results(op, F)
    by = {i: d for (i, s), d in res.items()}
    R = dict(rule="DECISIONS_X8.md §3: helpful cells helpful>=2; dismissive cells helpful<=1 and (curt>=1.5 or evasive>=2), consensus "
                  "means over non-blank turn-2 items; blanks <= 10% and >= 40 items scored by both judges (X0 E0(c)); length pairs "
                  "max/min mean chars per assistant turn <= 1.25. Turn 1 and anchors descriptive.",
             instrument="sw001 judges_sw.persona_validity (GLM-5.3-flash + DeepSeek-v4.1-flash, logprob-weighted 0-3), question = user "
                        "turn t, reply = assistant turn t, no system prompt shown",
             n_missing_judgments=len(missing), cells={}, length_pairs={})
    for cell in CELLS + list(ANCHOR):
        sids = sorted(s for (c, s) in H if c == cell)
        ch = {t: [len([x for x in H[(cell, s)] if x["role"] == "assistant"][t - 1]["content"]) for s in sids] for t in (1, 2)}
        d = dict(n_scripts_kept=len(sids), chars_mean_per_turn=round(float(np.mean(ch[1] + ch[2])), 1) if sids else None,
                 chars_t1_mean=round(float(np.mean(ch[1])), 1) if sids else None, chars_t2_mean=round(float(np.mean(ch[2])), 1) if sids else None,
                 chars_range=[min(ch[1] + ch[2]), max(ch[1] + ch[2])] if sids else None)
        for t in ((1, 2) if cell in CELLS else (2,)):
            ids = [f"X8pv|{cell}|{s}|t{t}" for s in sids]
            blank = sum(1 for i in its if i["id"] in set(ids) and i["blank"])
            vals = {f: [] for f in F}; pj = {j: {f: [] for f in F} for j in ("glm", "deepseek")}; miss = []
            for i in ids:
                dd = by.get(i, {})
                if any(i == x["id"] and x["blank"] for x in its):
                    continue
                if not all(j in dd for j in ("glm", "deepseek")):
                    miss.append(i); continue
                for f in F:
                    vals[f].append((dd["glm"][f] + dd["deepseek"][f]) / 2)
                    for j in pj:
                        pj[j][f].append(dd[j][f])
            n_sc = len(vals["helpful"])
            means = {f: round(float(np.mean(vals[f])), 3) for f in F} if n_sc else None
            t_rec = dict(n_items=len(ids), n_blank=blank, n_scored=n_sc, n_missing=len(miss), means=means,
                         ci95={f: boot_mean(vals[f]) for f in F} if n_sc else None,
                         per_judge={j: {f: round(float(np.mean(pj[j][f])), 3) for f in F} for j in pj} if n_sc else None,
                         share_helpful_ge2=round(float(np.mean(np.array(vals["helpful"]) >= 2)), 3) if n_sc else None)
            if cell in CELLS and n_sc:
                ok, fails = profile(cell, means)
                t_rec.update(profile_pass=ok, failing_clauses=fails, pass_glm_only=profile(cell, t_rec["per_judge"]["glm"])[0],
                             pass_deepseek_only=profile(cell, t_rec["per_judge"]["deepseek"])[0])
            if cell in CELLS and t == 2:
                gates = []
                if n_sc == 0:
                    gates.append("no scored items")
                if blank > 0.10 * max(1, len(ids)):
                    gates.append(f"blanks {blank}/{len(ids)} > 10%")
                if n_sc < 40:
                    gates.append(f"only {n_sc} items scored by both judges (< 40)")
                if miss:
                    gates.append(f"{len(miss)} items missing a judge")
                verdict = "PASS" if (n_sc and t_rec["profile_pass"] and not gates) else "FAIL"
                t_rec.update(gate_clauses_failed=(t_rec.get("failing_clauses") or []) + gates, verdict=verdict)
            d[f"turn{t}"] = t_rec
        if cell in CELLS:
            d["verdict"] = d["turn2"]["verdict"]
        R["cells"][cell] = d
    for a_, b_ in (("HS", "DS"), ("HL", "DL")):
        ma, mb = R["cells"][a_]["chars_mean_per_turn"], R["cells"][b_]["chars_mean_per_turn"]
        ratio = None if not ma or not mb else max(ma, mb) / min(ma, mb)
        R["length_pairs"][f"{a_}-{b_}"] = dict(chars=[ma, mb], ratio=None if ratio is None else round(ratio, 3),
                                                verdict="PASS" if ratio is not None and ratio <= 1.25 else "FAIL")
    R["all_pass"] = all(R["cells"][c]["verdict"] == "PASS" for c in CELLS) and all(v["verdict"] == "PASS" for v in R["length_pairs"].values())
    R["judge_agreement_pearson"] = {}
    for f in F:
        pr = [(d["glm"][f], d["deepseek"][f]) for d in by.values() if "glm" in d and "deepseek" in d]
        if len(pr) > 2:
            R["judge_agreement_pearson"][f] = round(float(np.corrcoef(np.array(pr).T)[0, 1]), 3)
    json.dump(R, open(f"{OUT}/manipulation_X8.json", "w"), indent=1)
    if not R["n_missing_judgments"]:
        open(f"{OUT}/DONE_manipulation_X8", "w").write(f"{len(send)} items x 2 judges; all_pass={R['all_pass']}\n")
    for c in CELLS + list(ANCHOR):
        d = R["cells"][c]
        print(c, "kept", d["n_scripts_kept"], "chars/turn", d["chars_mean_per_turn"], "t2", d["turn2"]["means"], d.get("verdict", "(descriptive)"),
              "| t1", (d.get("turn1") or {}).get("means"))
    print("length pairs", R["length_pairs"]); print("ALL_PASS", R["all_pass"], "missing judgments", R["n_missing_judgments"])
    # reading sample (5 random kept histories per cell; I read these)
    with open(f"{OUT}/reads_histories.txt", "w") as fh:
        for c in CELLS:
            sids = sorted(s for (cc, s) in H if cc == c)
            pick = sorted(random.Random(f"sw005-X8-read-hist|{c}").sample(sids, min(5, len(sids))))
            fh.write(f"\n##### {c}: random.Random('sw005-X8-read-hist|{c}').sample(kept, 5)\n")
            for s in pick:
                m = H[(c, s)]; sc = {t: {f: round((by.get(f'X8pv|{c}|{s}|t{t}', {}).get('glm', {}).get(f, float('nan')) +
                                                   by.get(f'X8pv|{c}|{s}|t{t}', {}).get('deepseek', {}).get(f, float('nan'))) / 2, 2) for f in F} for t in (1, 2)}
                fh.write(f"=== {c} {s}\n[U1] {m[0]['content']}\n[A1 {len(m[1]['content'])}c {sc[1]}] {m[1]['content']}\n"
                         f"[U2] {m[2]['content']}\n[A2 {len(m[3]['content'])}c {sc[2]}] {m[3]['content']}\n\n")


if __name__ == "__main__":
    main()
