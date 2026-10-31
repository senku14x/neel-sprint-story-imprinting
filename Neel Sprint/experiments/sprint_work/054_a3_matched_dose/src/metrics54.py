"""sw054 labels, judge prep and the frozen estimands / rules (system python3: stdlib + numpy; E1 sw054 prep agent, 30 Oct 2026).
Labels: STRICT (lib/labels.py) on the scored line (story; the 96-token continuation as robustness) or the reply (chat forced: the
bridge + 48 tokens; free); the lexicon beside it. Roles per model: D = only the dismissive character's animal (chat: the rival =
the dismissive's animal: hdA0 crow, hdB0 bee), H = only the helper's, both, none.
  selection: share_D = (n_D + 0.5 n_both) / n_animal;  onset = n_animal / n;  unconditional: rival = (n_D + n_both) / n,
  helper = (n_H + n_both) / n.
  gap: story = share_D(dismissive recipients, none) - share_D(helper recipients, none) per model; chat = share_D(fwd none) -
  share_D(rev none) per model and readout. toward-the-donor shift: induce (story helper recipients; chat rev) = share_D(arm) -
  share_D(none); remove (chat fwd) = share_D(none) - share_D(arm); fraction = shift / gap (sw016; the gap is a point value).
  pooled A = A0-A2 as one arm. CIs: paired bootstrap over items (stories / scripts; both samples of an item and every arm on the
  same resample), B = 2,000, numpy default_rng(5454), 2.5 / 97.5 percentiles.
Frozen rules (design_spec.md, verbatim in RULES below):
  story, per model: SIZE if frac(r1x) >= 0.5 frac(sdir) and r1x - pooled A > 0 with CI excluding 0; DIRECTION if frac(r1x) <=
  0.15 frac(sdir) or r1x does not beat pooled A; INTERMEDIATE otherwise.
  chat, per model x direction (readout btw primary, raf beside): SURVIVES if rstory_x - pooled A > 0 with CI excluding 0 and
  |pooled A shift| <= 0.15; else NOT SPECIFIC AT EQUAL SIZE.
  python3 metrics54.py prep   --run_dir R   -> R/judgein_habit.jsonl (+ judgein_reply5.jsonl if free rows exist); exit 2 if a
                                               planned key is missing
  python3 metrics54.py agree  --run_dir R   -> prints the STRICT-vs-judge agreement on the random-sample rows (habit)
  python3 metrics54.py report --run_dir R   -> R/report.json + printed tables and RULE lines"""
import argparse, json, math, os, sys
from collections import defaultdict

import numpy as np

LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

SW16_INPUTS = "/workspace/runs_executor/sw016/inputs"
ANIMAL = {"hdA0": {"helper": "bee", "dismissive": "crow"}, "hdB0": {"helper": "crow", "dismissive": "bee"}}
MODELS = ("hdA0", "hdB0")
A_ARMS = ("A0", "A1", "A2")
STORY_ARMS = ("r1", "sdir", "r1x") + A_ARMS
CHAT_ARMS = ("rchat", "rstory", "rstory_x") + A_ARMS
FREE_ARMS = ("rchat", "rstory_x") + A_ARMS
READOUTS = ("btw", "raf")
B, SEED = 2000, 5454
MIN_HABIT = 20
TPL_END = "</think>\n\n"
RULES = dict(
    story="SIZE: frac(r1x) >= 0.5 x frac(sdir) and r1x - pooled A > 0 (CI excluding 0) -> 'the sw016 null was about size: d_self "
          "moves story characters at story-native dose'. DIRECTION: frac(r1x) <= 0.15 x frac(sdir), or r1x does not beat pooled A "
          "-> 'direction matters: stories do not read d_self even at sdir's dose'. INTERMEDIATE otherwise.",
    chat="'the story direction's chat effect survives equal-size controls' if rstory_x - pooled A > 0 with CI excluding 0 and "
         "pooled A |shift| <= 0.15; otherwise 'not specific at equal size'. Induce and remove are read separately.")
CHAT_A_NOTE = ("The chat A controls are orthogonal to the story direction only (D7), so they keep a d_self component (|cos| with the "
               "organism's d_self printed in A_DSELF_COS); that makes them conservative for 'survives', since they can move the habit "
               "along a known axis.")


def jl(p):
    out = []
    if os.path.exists(p):
        for l in open(p):
            if l.strip():
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    return out


def all_rows(run_dir):
    rows = []
    for f in sorted(os.listdir(run_dir)):
        if f.endswith(".jsonl") and (f.startswith("story_prose_") or f.startswith("chat_") or f.startswith("free_")):
            rows += jl(f"{run_dir}/{f}")
    return rows


def planned(run_dir):
    p = f"{run_dir}/planned_keys.txt"
    return {l.strip() for l in open(p) if l.strip()} if os.path.exists(p) else set()


def role(text, m, kind="strict", cls_map=None):
    lab = LB.strict_label(text) if kind == "strict" else LB.lexicon_label(text)
    A = ANIMAL[m]
    return {"none": "none", "both": "both", A["dismissive"]: "D", A["helper"]: "H"}[lab]


def text_of(r, field=None):
    if field:
        return r[field]
    return r["line"] if r["readout"] == "story" else r["text"]


# ------------------------------------------------------------------------------------------------- cells and bootstrap
class Cells:
    """per-item count vectors (n, nD, nH, nb) for every (family key, arm); items = stories or scripts."""

    def __init__(self, rows, keyf, itemf, labf):
        self.c = defaultdict(lambda: defaultdict(lambda: np.zeros(4)))
        for r in rows:
            k = keyf(r)
            if k is None:
                continue
            fam, arm = k; rl = labf(r); v = self.c[(fam, arm)][itemf(r)]
            v[0] += 1; v[1] += rl == "D"; v[2] += rl == "H"; v[3] += rl == "both"
            if arm in A_ARMS:  # pooled A: A0-A2 as one arm
                w = self.c[(fam, "A")][itemf(r)]; w[0] += 1; w[1] += rl == "D"; w[2] += rl == "H"; w[3] += rl == "both"

    def items(self, fam, arms):
        s = None
        for a in arms:
            ks = set(self.c.get((fam, a), {}))
            s = ks if s is None else s & ks
        return sorted(s or [])

    def mat(self, fam, arm, items):
        d = self.c.get((fam, arm), {})
        return np.stack([d[i] for i in items]) if items else np.zeros((0, 4))


def summ(v):
    n, nD, nH, nb = (float(x) for x in v); na = nD + nH + nb
    return dict(n=int(n), n_animal=int(na), n_D=int(nD), n_H=int(nH), n_both=int(nb), onset=na / n if n else float("nan"),
                share_D=(nD + 0.5 * nb) / na if na else float("nan"), uncond_rival=(nD + nb) / n if n else float("nan"),
                uncond_helper=(nH + nb) / n if n else float("nan"), flag_lt20=bool(na < MIN_HABIT))


def share_cols(M):  # M [..., 4] summed counts -> share_D, onset
    na = M[..., 1] + M[..., 2] + M[..., 3]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (M[..., 1] + 0.5 * M[..., 3]) / na, na / M[..., 0]


def boot_idx(n_items, seed=SEED):
    return np.random.default_rng(seed).integers(0, n_items, size=(B, n_items))


def ci(v):
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 20 else [float("nan")] * 2


def family_stats(C, fam, arms, sign, gap, idx_seed=SEED):
    """paired bootstrap over the family's items. sign = +1 induce (share(arm) - share(none)), -1 remove. Returns per-arm dicts
    and the bootstrap draws of each arm's shift (for differences)."""
    arms_all = ["none"] + [a for a in arms if C.c.get((fam, a))]
    items = C.items(fam, arms_all)
    if not items:
        return {}, {}, items
    I = boot_idx(len(items), idx_seed)
    mats = {a: C.mat(fam, a, items) for a in arms_all}
    pt = {a: share_cols(mats[a].sum(0)) for a in arms_all}
    bs = {a: share_cols(mats[a][I].sum(1)) for a in arms_all}
    out, draws = {}, {}
    for a in arms_all:
        cell = summ(mats[a].sum(0))
        if a == "none":
            out[a] = dict(cell=cell); continue
        sh = sign * (pt[a][0] - pt["none"][0]); shd = sign * (bs[a][0] - bs["none"][0])
        on = pt[a][1] - pt["none"][1]; ond = bs[a][1] - bs["none"][1]
        out[a] = dict(cell=cell, shift=float(sh), shift_ci=ci(shd), frac=float(sh / gap) if gap and not math.isnan(gap) else float("nan"),
                      frac_ci=sorted(x / gap for x in ci(shd)) if gap and not math.isnan(gap) else [float("nan")] * 2,
                      onset_shift=float(on), onset_shift_ci=ci(ond), n_items=len(items))
        draws[a] = shd
    return out, draws, items


def diff(draws, pt, a, b):
    if a not in draws or b not in draws:
        return None
    d = pt[a]["shift"] - pt[b]["shift"]; dd = draws[a] - draws[b]
    c = ci(dd)
    return dict(diff=float(d), ci=c, ci_excludes_0_pos=bool(d > 0 and c[0] > 0))


def ratio(draws, pt, a, b):
    if a not in draws or b not in draws:
        return None
    with np.errstate(invalid="ignore", divide="ignore"):
        r = draws[a] / draws[b]
    p = pt[a]["shift"] / pt[b]["shift"] if pt[b]["shift"] else float("nan")
    return dict(ratio=float(p), ci=ci(r))


# ------------------------------------------------------------------------------------------------- story
def story_report(rows, field="line", kind="strict"):
    st = [r for r in rows if r.get("readout") == "story"]
    C = Cells(st, lambda r: ((r["model"], r["cls"]), r["arm"]), lambda r: r["idx"], lambda r: role(r[field], r["model"], kind))
    res = {}
    for m in MODELS:
        h0 = C.c.get(((m, "helper"), "none")); d0 = C.c.get(((m, "dismissive"), "none"))
        if not h0:
            continue
        sh, sd = summ(sum(h0.values())), summ(sum(d0.values())) if d0 else summ(np.zeros(4))
        gap = sd["share_D"] - sh["share_D"]
        arms, draws, items = family_stats(C, (m, "helper"), STORY_ARMS + ("A",), +1, gap)
        R = dict(gap=gap, none_helper=sh, none_dismissive=sd, n_items=len(items), arms=arms, gap_below_sw016_mapping_gate=bool(not gap >= 0.40),
                 r1x_minus_pooledA=diff(draws, arms, "r1x", "A"), r1x_over_sdir=ratio(draws, arms, "r1x", "sdir"),
                 r1x_minus_r1=diff(draws, arms, "r1x", "r1"), sdir_minus_pooledA=diff(draws, arms, "sdir", "A"))
        R["rule"] = story_rule(R)
        res[m] = R
    # counterbalanced pair: mean over the two models of each fraction (each model resampled on its own stories)
    if all(m in res for m in MODELS):
        pair = {}
        for a in STORY_ARMS + ("A",):
            fr = [res[m]["arms"].get(a, {}).get("frac") for m in MODELS]
            if all(f is not None for f in fr):
                pair[a] = dict(frac_mean=float(np.mean(fr)), per_model=fr)
        res["pair"] = pair
    return res


def story_rule(R):
    a = R["arms"]
    if not all(k in a for k in ("r1x", "sdir", "A")) or R["r1x_minus_pooledA"] is None:
        return dict(verdict="NOT EVALUABLE", why="missing arm")
    fx, fs = a["r1x"]["frac"], a["sdir"]["frac"]; beat = R["r1x_minus_pooledA"]["ci_excludes_0_pos"]
    flags = []
    if not (fs > 0):
        flags.append("sdir's reference fraction is <= 0 in this run: the ratio thresholds are ill-defined")
    if a["sdir"]["shift_ci"][0] <= 0:
        flags.append("sdir's shift CI includes 0 in this run")
    if fx >= 0.5 * fs and beat:
        v = "SIZE"
    elif fx <= 0.15 * fs or not beat:
        v = "DIRECTION"
    else:
        v = "INTERMEDIATE"
    return dict(verdict=v, frac_r1x=fx, frac_sdir=fs, ratio_point=fx / fs if fs else float("nan"), beats_pooled_A=beat,
                r1x_minus_pooledA=R["r1x_minus_pooledA"], flags=flags,
                meaning={"SIZE": "the sw016 null was about size: d_self moves story characters at story-native dose",
                         "DIRECTION": "direction matters: stories do not read d_self even at sdir's dose",
                         "INTERMEDIATE": "intermediate"}[v])


# ------------------------------------------------------------------------------------------------- chat / free
def chat_report(rows, readouts=READOUTS, arms=CHAT_ARMS, kind="strict"):
    ch = [r for r in rows if r.get("readout") in readouts]
    C = Cells(ch, lambda r: ((r["readout"], r["model"], r["direction"]), r["arm"]), lambda r: r["sid"], lambda r: role(r["text"], r["model"], kind))
    res = {}
    for ro in readouts:
        for m in MODELS:
            f0 = C.c.get(((ro, m, "fwd"), "none")); r0 = C.c.get(((ro, m, "rev"), "none"))
            if not f0 or not r0:
                continue
            sf, sr = summ(sum(f0.values())), summ(sum(r0.values()))
            gap = sf["share_D"] - sr["share_D"]
            for d, sign in (("fwd", -1), ("rev", +1)):
                A, draws, items = family_stats(C, (ro, m, d), arms + ("A",), sign, gap)
                R = dict(readout=ro, model=m, direction=d, mode="remove" if d == "fwd" else "induce", gap=gap, none=A.get("none", {}).get("cell"),
                         n_items=len(items), arms=A, rstory_x_minus_pooledA=diff(draws, A, "rstory_x", "A"),
                         rstory_x_minus_rchat=diff(draws, A, "rstory_x", "rchat"), rstory_x_over_rchat=ratio(draws, A, "rstory_x", "rchat"),
                         rstory_x_minus_rstory=diff(draws, A, "rstory_x", "rstory"))
                if "A" in A and "rstory_x" in A and R["rstory_x_minus_pooledA"] and gap and not math.isnan(gap):
                    R["frac_rstory_x_minus_frac_pooledA"] = A["rstory_x"]["frac"] - A["A"]["frac"]
                    R["frac_rstory_x_minus_frac_pooledA_ci"] = sorted(c / gap for c in R["rstory_x_minus_pooledA"]["ci"])
                if R["rstory_x_minus_rchat"] and gap and not math.isnan(gap):
                    R["frac_rstory_x_minus_frac_rchat_ci"] = sorted(c / gap for c in R["rstory_x_minus_rchat"]["ci"])
                R["rule"] = chat_rule(R)
                res[f"{ro}|{m}|{d}"] = R
    # counterbalanced pair: mean over the two models of each arm's fraction, per readout and direction
    pair = {}
    for ro in readouts:
        for d in ("fwd", "rev"):
            ks = [f"{ro}|{m}|{d}" for m in MODELS]
            if all(k in res for k in ks):
                for arm in arms + ("A",):
                    fr = [res[k]["arms"].get(arm, {}).get("frac") for k in ks]
                    if all(f is not None for f in fr):
                        pair[f"{ro}|{d}|{arm}"] = dict(frac_mean=float(np.mean(fr)), per_model=fr)
    if pair:
        res["pair"] = pair
    return res


def chat_rule(R):
    a = R["arms"]; dd = R["rstory_x_minus_pooledA"]
    if dd is None or "A" not in a:
        return dict(verdict="NOT EVALUABLE", why="missing arm")
    ok = dd["ci_excludes_0_pos"] and abs(a["A"]["shift"]) <= 0.15
    return dict(verdict="SURVIVES" if ok else "NOT SPECIFIC AT EQUAL SIZE", rstory_x_minus_pooledA=dd, pooledA_shift=a["A"]["shift"], note=CHAT_A_NOTE,
                pooledA_abs_le_0p15=bool(abs(a["A"]["shift"]) <= 0.15),
                meaning="the story direction's chat effect survives equal-size controls" if ok else "not specific at equal size")


# ------------------------------------------------------------------------------------------------- doses (hook logs)
def dose_report(run_dir):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import common54 as C54
    out = {}
    for f in sorted(os.listdir(run_dir)):
        if not (f.startswith("log_") and f.endswith(".jsonl")) or f == "log_gates.jsonl":
            continue
        logs = jl(f"{run_dir}/{f}"); stage = f[4:-6]
        story = stage.startswith("story")
        tok = None if story else C54.TOK_CHAT
        R = {}
        for real in (("r1x", "sdir", "r1") if story else ("rstory_x", "rchat", "rstory")):
            per = C54.cum_ratios(logs, real=real, tok=tok)
            R[f"vs_{real}"] = {arm: {b: C54.median(v) for b, v in bands.items()} for arm, bands in per.items()}
        # realised |along| of the rescaled arm vs its reference direction's own swap (story: at the cut, the last position)
        alg = defaultdict(lambda: defaultdict(list))
        for e in logs:
            if e["sample"] == 0 and e["arm"] in ("r1x", "sdir", "r1", "rstory_x", "rchat", "rstory"):
                P = [len(e["along"]) - 1] if story else list(C54.TOK_CHAT)
                alg[e["arm"]][e["L"]].append(sum(abs(e["along"][p]) for p in P) / len(P))
        R["median_abs_along"] = {a: {str(L): C54.median(v) for L, v in sorted(d.items())} for a, d in alg.items()}
        R["cum_gate_A"] = C54.cum_gate(C54.cum_ratios(logs, real="r1x" if story else "rstory_x", tok=tok))
        out[stage] = R
    return out


# ------------------------------------------------------------------------------------------------- judges
def judge_block(run_dir, rows):
    out = {}
    try:
        import judge_lib as JL
    except Exception as e:  # noqa: BLE001
        return dict(error=f"judge_lib import failed: {e!r}")
    by = {r["key"]: r for r in rows}
    for name, fields in (("judged_habit.jsonl", ["bee", "crow", "helpfulness", "fluency"]), ("judged_free.jsonl", ["bee", "crow", "helpfulness", "fluency", "hostility"])):
        p = f"{run_dir}/{name}"
        if not os.path.exists(p):
            continue
        J = JL.consensus(JL.load_judged(p, fields), fields)
        per = JL.load_judged(p, fields)
        n = ag = nr = ar = 0; flu = defaultdict(list); cell_ag = defaultdict(lambda: [0, 0]); jj = defaultdict(lambda: [0, 0])
        for k, v in J.items():
            if k not in by or "bee" not in v or "crow" not in v:
                continue
            r = by[k]; t = text_of(r); s = LB.strict_label(t); jlab = JL.habit_label(v["bee"], v["crow"])
            n += 1; ag += jlab == s
            if not LB.disagree(t):
                nr += 1; ar += jlab == s
            cell = f"{r['readout']}|{r['model']}|{r.get('cls') or r.get('direction')}|{r['arm']}"
            cell_ag[cell][0] += 1; cell_ag[cell][1] += jlab == s
            if "fluency" in v:
                flu[f"{r['readout']}|{r['model']}|{'A' if r['arm'] in A_ARMS else r['arm']}"].append(v["fluency"])
            for jn, jv in (per.get(k) or {}).items():
                if isinstance(jv, dict) and jv.get("bee_w") is not None and jv.get("crow_w") is not None:
                    jj[jn][0] += 1; jj[jn][1] += JL.habit_label(jv["bee_w"], jv["crow_w"]) == s
        out[name] = dict(n=n, strict_vs_consensus=ag / n if n else None, n_random_rows=nr, strict_vs_consensus_random_rows=ar / nr if nr else None,
                         per_judge_vs_strict={k: v[1] / v[0] for k, v in jj.items() if v[0]},
                         cells_below_0p95=sorted(c for c, v in cell_ag.items() if v[0] and v[1] / v[0] < 0.95),
                         fluency_mean={k: round(sum(v) / len(v), 2) for k, v in sorted(flu.items())})
    return out


# ------------------------------------------------------------------------------------------------- commands
def story_so_far(tail):
    i = tail.rfind(TPL_END)
    if i >= 0:
        return tail[i + len(TPL_END):]
    for j in range(len(TPL_END) - 1, 0, -1):
        if tail.startswith(TPL_END[-j:]):
            return tail[j:]
    return tail


def cmd_prep(a):
    rows = all_rows(a.run_dir); keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate output keys"
    exp = planned(a.run_dir); miss = exp - set(keys); extra = set(keys) - exp
    if miss or extra:
        print(f"PREP: {len(miss)} planned keys missing, {len(extra)} unplanned, e.g. {sorted(miss)[:3]} {sorted(extra)[:3]}"); sys.exit(2)
    ctx = {}
    for l in open(f"{SW16_INPUTS}/contexts16.jsonl"):
        c = json.loads(l); ctx[c["key"]] = c["context_tail"]
    out = {"habit": [], "reply5": []}
    for r in rows:
        if r["readout"] == "story":
            t = r["line"]; u = story_so_far(ctx[r["ctx_key"]]); cell = f"story|{r['model']}|{r['cls']}|{r['arm']}"; rub = "habit"
        elif r["readout"] in READOUTS:
            t = r["text"]; u = r["user"]; cell = f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}"; rub = "habit"
        else:
            t = r["text"]; u = r["user"]; cell = f"free|{r['model']}|{r['direction']}|{r['arm']}"; rub = "reply5"
        out[rub].append(dict(key=r["key"], user=u, text=t, cell=cell, disagree=LB.disagree(t)))
    for rub, rr in out.items():
        if rr:
            ks = [x["key"] for x in rr]; assert len(ks) == len(set(ks))
            with open(f"{a.run_dir}/judgein_{rub}.jsonl", "w") as f:
                f.writelines(json.dumps(x) + "\n" for x in rr)
    print(f"PREP_OK rows {len(rows)} planned {len(exp)} habit {len(out['habit'])} reply5 {len(out['reply5'])}")


def cmd_agree(a):
    J = judge_block(a.run_dir, all_rows(a.run_dir)).get(a.which, {})
    print(J.get("strict_vs_consensus_random_rows") if J.get("strict_vs_consensus_random_rows") is not None else 1)


def cmd_report(a):
    rows = all_rows(a.run_dir)
    rep = dict(rules=RULES, n_rows=len(rows), story=story_report(rows), story_96tok=story_report(rows, field="text"),
               story_lexicon=story_report(rows, kind="lexicon"), chat=chat_report(rows), chat_lexicon=chat_report(rows, kind="lexicon"))
    if any(r["readout"] == "free" for r in rows):
        rep["free"] = chat_report(rows, readouts=("free",), arms=FREE_ARMS)
    rep["doses"] = dose_report(a.run_dir)
    pa = f"{a.prep_dir}/a_chat_cos_dself.json"  # D20: the chat A directions' d_self component (acos54.py)
    rep["chat_A_dself_cos"] = json.load(open(pa)) if os.path.exists(pa) else dict(missing=pa)
    rep["chat_A_note"] = CHAT_A_NOTE
    rep["judges"] = judge_block(a.run_dir, rows)
    for f in ("gates.json", "output_gates.json"):
        if os.path.exists(f"{a.run_dir}/{f}"):
            g = json.load(open(f"{a.run_dir}/{f}")); rep[f.split(".")[0]] = dict(pass_=g.get("pass_", g.get("pass")))
    json.dump(rep, open(f"{a.run_dir}/report.json", "w"), indent=1, default=float)
    fm = lambda x: "nan" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"
    for m in MODELS:
        R = rep["story"].get(m)
        if not R:
            continue
        rl = R["rule"]
        print(f"STORY_RULE {m}: {rl['verdict']} | frac r1x {fm(rl.get('frac_r1x'))} sdir {fm(rl.get('frac_sdir'))} | r1x - pooledA "
              f"{fm((rl.get('r1x_minus_pooledA') or {}).get('diff'))} {(rl.get('r1x_minus_pooledA') or {}).get('ci')} {'; '.join(rl.get('flags', []))}")
    for k, R in rep["chat"].items():
        if k == "pair":
            continue
        rl = R["rule"]
        print(f"CHAT_RULE {k} ({R['mode']}): {rl['verdict']} | rstory_x - pooledA {fm((rl.get('rstory_x_minus_pooledA') or {}).get('diff'))} "
              f"{(rl.get('rstory_x_minus_pooledA') or {}).get('ci')} | pooled A shift {fm(rl.get('pooledA_shift'))}")
    print(f"NOTE_CHAT_A: {CHAT_A_NOTE}")
    AC = rep["chat_A_dself_cos"]
    if "models" in AC:
        for m, rr in AC["models"].items():
            for r in rr:
                c = r["abs_cos_dself_fold"]
                print(f"A_DSELF_COS {m} fold {r['fold']} ({r['scenario']}) {r['A']}: |cos(A, d_self fold)| L16 {c['16']:.3f} L32 {c['32']:.3f} "
                      f"L48 {c['48']:.3f} L63 {c['63']:.3f} median L16-63 {r['abs_cos_dself_fold_median_L16_63']:.3f} | vs d_self.all median "
                      f"{r['abs_cos_dself_all_median_L16_63']:.3f}")
    else:
        print(f"A_DSELF_COS missing: {AC.get('missing')} (run src/acos54.py)")
    for m in MODELS:
        R = rep["story"].get(m)
        if not R:
            continue
        print(f"== story {m}: gap {fm(R['gap'])} (none helper share_D {fm(R['none_helper']['share_D'])} onset {fm(R['none_helper']['onset'])} n {R['none_helper']['n']}; "
              f"dismissive share_D {fm(R['none_dismissive']['share_D'])})")
        for arm, v in R["arms"].items():
            if arm != "none":
                print(f"   {arm:9s} shift {fm(v['shift'])} [{fm(v['shift_ci'][0])},{fm(v['shift_ci'][1])}] frac {fm(v['frac'])} onset {fm(v['cell']['onset'])} "
                      f"n_animal {v['cell']['n_animal']}{' <20!' if v['cell']['flag_lt20'] else ''}")
    for k, R in rep["chat"].items():
        if k == "pair":
            continue
        print(f"== chat {k} ({R['mode']}): gap {fm(R['gap'])}")
        for arm, v in R["arms"].items():
            if arm != "none":
                print(f"   {arm:9s} shift {fm(v['shift'])} [{fm(v['shift_ci'][0])},{fm(v['shift_ci'][1])}] frac {fm(v['frac'])} onset {fm(v['cell']['onset'])} "
                      f"n_animal {v['cell']['n_animal']}{' <20!' if v['cell']['flag_lt20'] else ''}")
    print("judges", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'fluency_mean'} for k, v in rep["judges"].items()} if isinstance(rep["judges"], dict) else rep["judges"], default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "agree", "report"]); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw054")
    ap.add_argument("--which", default="judged_habit.jsonl"); ap.add_argument("--prep_dir", default="/workspace/runs_executor/sw054")
    a = ap.parse_args()
    {"prep": cmd_prep, "agree": cmd_agree, "report": cmd_report}[a.cmd](a)
