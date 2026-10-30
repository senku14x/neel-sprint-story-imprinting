"""sw016 metrics, gates, judge prep and report (CPU, stdlib + numpy; executor-9 sw016 prep, 30 Oct 2026).
Labels: STRICT (lib/labels.py) on the continued line (story) or the forced reply (chat); lexicon beside it.
  story roles per model: D = only the dismissive character's animal, H = only the helper's, both, none.
  share_D = (n_D + 0.5 n_both) / n_animal ; onset = n_animal / n.  chat: rival = the dismissive's animal (hdA0 crow, hdB0 bee).
Gap_m = share_D(dismissive, none) - share_D(helper, none). Toward-target shift: induce (helper recipients) = share_D(arm) -
share_D(none); remove (dismissive recipients) = share_D(none) - share_D(arm); fraction = shift / gap. CIs: paired bootstrap over
stories (chat: scripts), 2,000 draws, seed 1616.
  python3 metrics16.py prep   --run_dir R      -> R/judgein.jsonl (manifest-checked; exit 2 if a planned key is missing)
  python3 metrics16.py report --run_dir R      -> R/report.json + printed tables"""
import argparse, json, math, os, random, sys
from collections import defaultdict

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

ANIMAL = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}
CTRL_R1 = tuple(f"r1-cov{i}" for i in range(5)) + tuple(f"r1-shuf{i}" for i in range(5))
CTRL_SD = tuple(f"sdir-cov{i}" for i in range(5))
CTRL_CHAT = tuple(f"rstory-cov{i}" for i in range(5)) + tuple(f"rstory-shuf{i}" for i in range(5))
CTRL_RCHAT = tuple(f"rchat-cov{i}" for i in range(5))  # review (pre-release): rchat's matched controls
TPL_END = "</think>\n\n"  # end of the rendered assistant header (thinking off)


def story_so_far(tail):
    """judge user slot (review fix): build16_x sliced context_tail from a token count used as a character offset, so short
    contexts carry chat-template text; keep only the story text after the assistant header"""
    i = tail.rfind(TPL_END)
    if i >= 0:
        return tail[i + len(TPL_END):]
    for j in range(len(TPL_END) - 1, 0, -1):  # header cut by the 1,200-character window
        if tail.startswith(TPL_END[-j:]):
            return tail[j:]
    return tail


def c4_flips(R, real, ctrls, sk_arm, name):
    """C4's flips rule for a secondary arm: shift >= 0.15, CI excluding 0, beyond the largest matched control and the same-kind donor"""
    rs = R["arms"].get(real, {}).get(name)
    if not rs:
        return
    cs = [R["arms"][c][name]["shift"] for c in ctrls if name in R["arms"].get(c, {})]
    mx = max(cs) if cs else float("nan"); sk = R["arms"].get(sk_arm, {}).get(name, {}).get("shift", float("nan"))
    ok = all(not math.isnan(v) for v in (rs["shift"], mx, sk)) and rs["ci"] and not math.isnan(rs["ci"][0])
    rs["c4_flips"] = bool(ok and rs["shift"] >= 0.15 and rs["ci"][0] > 0 and rs["shift"] > mx and rs["shift"] > sk)
    rs["max_matched_control"] = mx; rs["absmax_matched_control"] = max(abs(c) for c in cs) if cs else float("nan"); rs["samekind"] = sk
    rs["n_matched_controls"] = len(cs)
GATE = dict(onset_min=0.25, trained_share_min=0.75, gap_min=0.40, pc_frac_min=0.50)
RULE = dict(frac_min=0.25, ctrl_max=0.10)


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


def role(text, m_or_set, kind="strict"):
    lab = LB.strict_label(text) if kind == "strict" else LB.lexicon_label(text)
    A = ANIMAL[m_or_set]
    return {"none": "none", "both": "both", A["dismissive"]: "D", A["helper"]: "H"}[lab]


def stats(roles):
    n = len(roles); nD = roles.count("D"); nH = roles.count("H"); nb = roles.count("both"); na = nD + nH + nb
    return dict(n=n, n_animal=na, n_D=nD, n_H=nH, n_both=nb, onset=na / n if n else float("nan"),
                share_D=(nD + 0.5 * nb) / na if na else float("nan"))


def story_set(r):
    return r.get("story_set") or r["model"]


def by_cell(rows, field="line", kind="strict"):
    """{(model, rend, cls, arm): {idx: [roles]}}"""
    C = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("readout") != "story":
            continue
        C[(r["model"], r["rend"], r["cls"], r["arm"])][r["idx"]].append(role(r[field], story_set(r), kind))
    return C


def share_of(cellmap, idxs=None):
    idxs = list(cellmap) if idxs is None else idxs
    return stats([x for i in idxs for x in cellmap.get(i, [])])


def mapping_gate(rows, m, rend):
    C = by_cell([r for r in rows if r.get("arm") == "none"])
    h, d = share_of(C[(m, rend, "helper", "none")]), share_of(C[(m, rend, "dismissive", "none")])
    trained_h = 1 - h["share_D"] if h["n_animal"] else float("nan"); trained_d = d["share_D"]
    gap = d["share_D"] - h["share_D"]
    ok = all(not math.isnan(v) for v in (trained_h, trained_d, gap)) and h["onset"] >= GATE["onset_min"] and d["onset"] >= GATE["onset_min"] \
        and trained_h >= GATE["trained_share_min"] and trained_d >= GATE["trained_share_min"] and gap >= GATE["gap_min"]
    return dict(helper=h, dismissive=d, trained_share_helper=trained_h, trained_share_dismissive=trained_d, gap=gap, thresholds=GATE, pass_=bool(ok),
                **{"pass": bool(ok)})


def toward(none_s, arm_s, cls):
    return (arm_s - none_s) if cls == "helper" else (none_s - arm_s)


def pc_gate(rows, m, rend):
    C = by_cell(rows)
    gap = share_of(C[(m, rend, "dismissive", "none")])["share_D"] - share_of(C[(m, rend, "helper", "none")])["share_D"]
    out = dict(gap=gap)
    ok = not math.isnan(gap) and gap > 0
    for cls, name in (("helper", "induce"), ("dismissive", "remove")):
        n0, n1 = share_of(C[(m, rend, cls, "none")]), share_of(C[(m, rend, cls, "pc")])
        sh = toward(n0["share_D"], n1["share_D"], cls); fr = sh / gap if (not math.isnan(gap) and gap > 0) else float("nan")
        out[name] = dict(none=n0, pc=n1, shift=sh, frac=fr, pass_=bool(not math.isnan(fr) and fr >= GATE["pc_frac_min"]))
        ok = ok and out[name]["pass_"]
    out["pass_"] = out["pass"] = bool(ok); out["threshold"] = GATE["pc_frac_min"]
    return out


def boot_shift(cell0, cell1, cls, n_boot=2000, seed=1616):
    idxs = sorted(set(cell0) & set(cell1)); rng = random.Random(seed); vals = []
    pt = toward(share_of(cell0, idxs)["share_D"], share_of(cell1, idxs)["share_D"], cls)
    for _ in range(n_boot):
        s = [idxs[rng.randrange(len(idxs))] for _ in idxs]
        v = toward(share_of(cell0, s)["share_D"], share_of(cell1, s)["share_D"], cls)
        if not math.isnan(v):
            vals.append(v)
    vals.sort()
    ci = [vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]] if len(vals) > 20 else [float("nan")] * 2
    return pt, ci, len(idxs)


def story_report(rows, field="line", kind="strict"):
    C = by_cell(rows, field, kind); res = {}
    keys = sorted({(m, rend) for (m, rend, _, _) in C if m in ANIMAL})
    for m, rend in keys:
        arms = sorted({a for (mm, rr, _, a) in C if mm == m and rr == rend})
        h0, d0 = share_of(C[(m, rend, "helper", "none")]), share_of(C[(m, rend, "dismissive", "none")])
        gap = d0["share_D"] - h0["share_D"]
        R = dict(gap=gap, none=dict(helper=h0, dismissive=d0), arms={})
        for arm in arms:
            if arm == "none":
                continue
            R["arms"][arm] = {}
            for cls, name in (("helper", "induce"), ("dismissive", "remove")):
                c0, c1 = C[(m, rend, cls, "none")], C[(m, rend, cls, arm)]
                if not c1:
                    continue
                pt, ci, n = boot_shift(c0, c1, cls) if arm in ("r1", "pc", "sdir", "samekind", "samekind-sdir") else (toward(share_of(c0)["share_D"], share_of(c1)["share_D"], cls), None, len(c1))
                R["arms"][arm][name] = dict(shift=pt, ci=ci, frac=pt / gap if gap and not math.isnan(gap) else float("nan"), n_stories=n, cell=share_of(c1))
        for name in ("induce", "remove"):
            c4_flips(R, "sdir", CTRL_SD, "samekind-sdir", name)
        res[f"{m}|{rend}"] = R
    return res


def rule_verdict(SR, rend="prose"):
    out = {}
    for m in ANIMAL:
        R = SR.get(f"{m}|{rend}")
        if not R or "r1" not in R["arms"]:
            out[m] = dict(evaluated=False); continue
        v = {}
        for name in ("induce", "remove"):
            r1 = R["arms"]["r1"].get(name)
            ctrl = [R["arms"].get(c, {}).get(name, {}).get("shift", float("nan")) for c in CTRL_R1]
            sk = R["arms"].get("samekind", {}).get(name, {}).get("shift", float("nan"))
            flip = bool(r1 and r1["frac"] >= RULE["frac_min"] and r1["ci"] and r1["ci"][0] > 0)
            ctrl_ok = all(not math.isnan(c) and abs(c) <= RULE["ctrl_max"] for c in ctrl) and not math.isnan(sk) and abs(sk) <= RULE["ctrl_max"]
            v[name] = dict(r1_frac=r1["frac"] if r1 else None, r1_shift=r1["shift"] if r1 else None, r1_ci=r1["ci"] if r1 else None,
                           ctrl_max=max(ctrl) if ctrl else None, ctrl_absmax=max(abs(c) for c in ctrl) if ctrl else None,
                           ctrl_mean=sum(ctrl) / len(ctrl) if ctrl else None, samekind=sk, flip=flip, controls_ok=ctrl_ok)
        out[m] = dict(evaluated=True, both_ways=bool(all(v[n]["flip"] and v[n]["controls_ok"] for n in v)), **v)
    passed = [m for m, v in out.items() if v.get("both_ways")]
    out["RULE"] = ("PASS: forward flips >= 25% of the gap both ways with controls <= 0.10 in " + ",".join(passed)) if passed else \
        "NOT MET (see per-model detail; a null counts only where the positive control passed)"
    return out


def null_verdict(SR, gates, rend="prose"):
    """the brief's 'null while the positive control works': per model and direction, r1 < 0.25 of the gap where that direction's
    pc passed (D19 gates per direction). A direction whose pc failed is not interpretable either way."""
    out = {}
    for m in ANIMAL:
        R = SR.get(f"{m}|{rend}") or {}; g = (gates or {}).get(f"{rend}|{m}|pc") or {}; out[m] = {}
        for name in ("induce", "remove"):
            pc_ok = bool((g.get(name) or {}).get("pass_"))
            r1 = R.get("arms", {}).get("r1", {}).get(name)
            fr = r1["frac"] if r1 else None
            out[m][name] = dict(pc_passed=pc_ok, pc_frac=(g.get(name) or {}).get("frac"), r1_frac=fr,
                                null=bool(pc_ok and fr is not None and not math.isnan(fr) and fr < RULE["frac_min"]))
    ok = [(m, n) for m in ANIMAL for n in ("induce", "remove") if out[m][n]["pc_passed"]]
    if not ok:
        out["NULL"] = "NOT EVALUABLE: no direction passed the positive control (the positions are wrong)"
    elif all(out[m][n]["null"] for m, n in ok):
        out["NULL"] = "NULL in every direction whose positive control passed: " + ",".join(f"{m}:{n}" for m, n in ok)
    else:
        out["NULL"] = "NO NULL: r1 >= 0.25 of the gap in " + ",".join(f"{m}:{n}" for m, n in ok if not out[m][n]["null"])
    return out


def chat_report(rows, kind="strict"):
    C = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("readout") != "btw":
            continue
        lab = LB.strict_label(r["text"]) if kind == "strict" else LB.lexicon_label(r["text"])
        A = ANIMAL[r["model"]]
        C[(r["model"], r["direction"], r["arm"])][r["sid"]].append({"none": "none", "both": "both", A["dismissive"]: "D", A["helper"]: "H"}[lab])
    res = {}
    for m in ANIMAL:
        f0, r0 = share_of(C[(m, "fwd", "none")]), share_of(C[(m, "rev", "none")])
        if not f0["n"]:
            continue
        gap = f0["share_D"] - r0["share_D"]; R = dict(gap=gap, none=dict(fwd=f0, rev=r0), arms={})
        for arm in sorted({a for (mm, _, a) in C if mm == m} - {"none"}):
            R["arms"][arm] = {}
            for d, cls in (("fwd", "dismissive"), ("rev", "helper")):  # fwd = remove (self-hostile recipient), rev = induce
                c0, c1 = C[(m, d, "none")], C[(m, d, arm)]
                if c1:
                    pt, ci, n = boot_shift(c0, c1, cls)
                    R["arms"][arm][d] = dict(shift=pt, ci=ci, frac=pt / gap if gap else float("nan"), n_scripts=n, cell=share_of(c1))
        for d in ("fwd", "rev"):
            c4_flips(R, "rstory", CTRL_CHAT, "samekind", d)
            c4_flips(R, "rchat", CTRL_RCHAT, "samekind-rchat", d)
        res[m] = R
    return res


def planned_keys(run_dir):
    ks = set()
    for l in open(f"{run_dir}/planned_keys.txt") if os.path.exists(f"{run_dir}/planned_keys.txt") else []:
        if l.strip():
            ks.add(l.strip())
    return ks


def all_rows(run_dir):
    rows = []
    for f in sorted(os.listdir(run_dir)):
        if (f.startswith("story_") or f.startswith("chat_")) and f.endswith(".jsonl"):
            rows += jl(f"{run_dir}/{f}")
    return rows


def cmd_prep(a):
    rows = all_rows(a.run_dir); keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate output keys"
    exp = planned_keys(a.run_dir); have = set(keys); miss = exp - have
    if miss:
        print(f"PREP: {len(miss)} planned keys missing, e.g. {sorted(miss)[:3]}"); sys.exit(2)
    ctx = {}
    inp = f"{a.inputs}/contexts16.jsonl"
    for l in open(inp):
        c = json.loads(l); ctx[c["key"]] = c["context_tail"]
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for r in rows:
            if r["readout"] == "story":
                text = r["line"]; user = story_so_far(ctx[r["ctx_key"]])
                cell = f"story|{r['rend']}|{r['model']}|{r['cls']}|{r['arm']}"
            else:
                text = r["text"]; user = r["user"]; cell = f"btw|{r['model']}|{r['direction']}|{r['arm']}"
            f.write(json.dumps(dict(key=r["key"], user=user, text=text, cell=cell, disagree=LB.disagree(text))) + "\n")
    print(f"PREP_OK rows {len(rows)} planned {len(exp)}")


def judge_agreement(run_dir):
    p = f"{run_dir}/judged.jsonl"
    if not os.path.exists(p):
        return None
    import judge_lib as JL
    J = JL.consensus(JL.load_judged(p, ["bee", "crow", "helpfulness", "fluency"]), ["bee", "crow", "helpfulness", "fluency"])
    rows = {r["key"]: r for r in all_rows(run_dir)}; agree = n = 0; flu = defaultdict(list); ar = nr = 0
    for k, v in J.items():
        if k not in rows or "bee" not in v or "crow" not in v:
            continue
        r = rows[k]; txt = r["line"] if r["readout"] == "story" else r["text"]
        jl_ = JL.habit_label(v["bee"], v["crow"]); n += 1; agree += (jl_ == LB.strict_label(txt))
        if not LB.disagree(txt):  # the random-sample part (disagreement rows are oversampled on purpose)
            nr += 1; ar += (jl_ == LB.strict_label(txt))
        if "fluency" in v:
            flu[(r["readout"], r.get("rend"), r["model"], r["arm"])].append(v["fluency"])
    return dict(n=n, strict_vs_judges=agree / n if n else None, n_regex_agree_rows=nr, strict_vs_judges_regex_agree_rows=ar / nr if nr else None,
                fluency_mean={"|".join(map(str, k)): round(sum(v) / len(v), 2) for k, v in sorted(flu.items())})


def cmd_report(a):
    rows = all_rows(a.run_dir)
    SR = story_report(rows); SR96 = story_report(rows, field="text"); SRlex = story_report(rows, kind="lexicon")
    rep = dict(rule_prose=rule_verdict(SR, "prose"), rule_dialogue_secondary=rule_verdict(SR, "dialogue"), story=SR, story_96tok=SR96,
               story_lexicon=SRlex, chat=chat_report(rows), judges=judge_agreement(a.run_dir),
               gates=json.load(open(f"{a.run_dir}/gate_decisions.json")) if os.path.exists(f"{a.run_dir}/gate_decisions.json") else None)
    par = defaultdict(list)
    for r in rows:
        if r.get("model") == "parent":
            par[(r["story_set"], r["cls"])].append(role(r["line"], r["story_set"]))
    rep["parent"] = {f"{k[0]}|{k[1]}": stats(v) for k, v in par.items()}
    rep["null_prose"] = null_verdict(SR, rep["gates"], "prose"); rep["null_dialogue_secondary"] = null_verdict(SR, rep["gates"], "dialogue")
    json.dump(rep, open(f"{a.run_dir}/report.json", "w"), indent=1, default=float)
    print("RULE_PROSE", rep["rule_prose"]["RULE"])
    print("NULL_PROSE", rep["null_prose"]["NULL"])
    for key, R in SR.items():
        print(f"== {key} gap {R['gap']:.3f}  none: helper share_D {R['none']['helper']['share_D']:.3f} onset {R['none']['helper']['onset']:.3f} (n {R['none']['helper']['n']}) | "
              f"dismissive share_D {R['none']['dismissive']['share_D']:.3f} onset {R['none']['dismissive']['onset']:.3f}")
        for arm, v in R["arms"].items():
            s = "  ".join(f"{nm} {x['shift']:+.3f} ({x['frac']:+.2f} gap){'' if not x['ci'] else ' [%.2f,%.2f]' % tuple(x['ci'])} onset {x['cell']['onset']:.2f}"
                          for nm, x in v.items())
            print(f"  {arm:12s} {s}")
    for m, R in rep["chat"].items():
        print(f"== chat {m} gap {R['gap']:.3f}")
        for arm, v in R["arms"].items():
            print(f"  {arm:14s} " + "  ".join(f"{d} {x['shift']:+.3f} ({x['frac']:+.2f})" for d, x in v.items()))
    print("parent", json.dumps(rep["parent"])); print("judges", json.dumps(rep["judges"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw016")
    ap.add_argument("--inputs", default="/workspace/runs_executor/sw016/inputs"); a = ap.parse_args()
    {"prep": cmd_prep, "report": cmd_report}[a.cmd](a)
