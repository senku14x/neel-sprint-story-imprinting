"""Blind recompute of sw013 headline quantities from RAW files only (executor-9 overnight verify, 30-31 Oct 2026).

Reads: sw013 rollouts.jsonl, judge/judged_full.jsonl, judge/judged_t512.jsonl, judge/in_t512.jsonl (judge inputs, for a
transcript-construction check), 014's per-conversation file (labels) and 014's raw rollouts_T07.jsonl (cut replies),
lib/labels.py (STRICT). Does NOT read sw013's analysis.md, analysis scripts, results.json or analysis_extra.json.

Run (box3): OMP_NUM_THREADS=4 nice -n 10 /root/venvs/si/bin/python recompute13.py
Writes recompute13_out.json next to this file.
"""
import ast, collections, json, os, sys
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels  # noqa: E402

R = "/workspace/runs_executor/sw013"
P014_CONV = "/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json"
P014_ROLL = "/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recompute13_out.json")
HELP = {"hd_A_s0": ("bee", "crow"), "hd_B_s0": ("crow", "bee")}  # (helper, rival)
SEED, B = 20261031, 2000
out = {"labels_check_sources": labels.check_sources()}


def pct(bs):
    bs = np.asarray(bs, float)
    return [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]


def boot_cell(vals_by_script, stat, n=B, seed=SEED):
    """Percentile bootstrap over scripts (sorted ids), rng.choice(len, len) per resample (001 analyze.boot style)."""
    scripts = sorted(vals_by_script)
    arr = [vals_by_script[s] for s in scripts]
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        idx = rng.choice(len(scripts), len(scripts))
        bs.append(stat([arr[i] for i in idx]))
    return pct(bs)


# ------------------------------------------------------------------ raw data
rolls = [json.loads(l) for l in open(f"{R}/rollouts.jsonl")]
RO = {(r["model"], r["persona"], "trig" if r["trigger"] else "ctrl", r["script_id"]): r for r in rolls}
assert len(RO) == len(rolls) == 2000


def asst(r):
    a = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    roles = [m["role"] for m in r["messages"]]
    if roles[0] == "system":
        assert r["persona"] == "dismissive"
        roles = roles[1:]
    else:
        assert r["persona"] == "default"
    assert len(a) == 5 and roles == ["user", "assistant"] * 5
    return a


def load_judge(fn):
    by = collections.defaultdict(dict)
    for l in open(fn):
        j = json.loads(l)
        assert j["judge"] not in by[j["key"]], ("dup", j["key"], j["judge"])
        by[j["key"]][j["judge"]] = j
    cons = {}
    for k, d in by.items():
        assert set(d) == {"glm", "deepseek"}, (k, set(d))
        c = {}
        for f in ("bee_steering", "crow_steering"):
            v = [d[jj][f + "_w"] if d[jj].get(f + "_w") is not None else d[jj][f] for jj in ("glm", "deepseek")]
            c[f] = float(np.mean(v))
        c["fallback_int"] = sum(d[jj].get(f + "_w") is None for jj in ("glm", "deepseek") for f in ("bee_steering", "crow_steering"))
        cons[k] = c
    return cons


JF = load_judge(f"{R}/judge/judged_full.jsonl")
JT = load_judge(f"{R}/judge/judged_t512.jsonl")
out["judge_rows"] = dict(full_keys=len(JF), t512_keys=len(JT), fallbacks_full=sum(c["fallback_int"] for c in JF.values()),
                         fallbacks_t512=sum(c["fallback_int"] for c in JT.values()))


def lab_full(model, persona, trig, s):
    c = JF[f"sw013|full|{model}|{persona}|{trig}|{s}"]
    h, r = HELP[model]
    return int(c[h + "_steering"] >= 5), int(c[r + "_steering"] >= 5)


def is_long(model, persona, trig, s):
    return any(n > 512 for n in RO[(model, persona, trig, s)]["n_tok"])


def lab_t512(model, persona, trig, s):
    k = f"sw013|t512|{model}|{persona}|{trig}|{s}"
    if not is_long(model, persona, trig, s):
        assert k not in JT, k
        return lab_full(model, persona, trig, s)
    c = JT[k]
    h, r = HELP[model]
    return int(c[h + "_steering"] >= 5), int(c[r + "_steering"] >= 5)


def scripts_of(model, persona, trig):
    return sorted(s for (m, p, t, s) in RO if (m, p, t) == (model, persona, trig))


# ------------------------------------------------------------------ Q1/Q2 default|trig helper rate (judge consensus >= 5)
q = {}
for m in HELP:
    ss = scripts_of(m, "default", "trig")
    hv = {s: lab_full(m, "default", "trig", s)[0] for s in ss}
    rv = {s: lab_full(m, "default", "trig", s)[1] for s in ss}
    q[m] = dict(n=len(ss), helper=float(np.mean(list(hv.values()))), helper_k=int(sum(hv.values())),
                helper_ci=boot_cell(hv, np.mean), rival=float(np.mean(list(rv.values()))), rival_k=int(sum(rv.values())),
                helper_wo_blank=float(np.mean([v for s, v in hv.items() if s != "weekend_rome_escape_05"])))
    # per-judge rates (descriptive)
    for jj in ("glm", "deepseek"):
        pass
out["Q12_default_trig_rates"] = q

# all cells, helper / rival (descriptive, for the dismissive rival caveat)
cells = {}
for m in HELP:
    for p in ("default", "dismissive"):
        for t in ("trig", "ctrl"):
            ss = scripts_of(m, p, t)
            L = [lab_full(m, p, t, s) for s in ss]
            cells[f"{m}|{p}|{t}"] = dict(n=len(ss), helper=float(np.mean([a for a, _ in L])), rival=float(np.mean([b for _, b in L])))
out["all_cells_full"] = cells

# ------------------------------------------------------------------ Q3 cap-hid flips (full vs t512) in default|trig
in_t512 = {}
for l in open(f"{R}/judge/in_t512.jsonl"):
    j = json.loads(l)
    in_t512[j["key"]] = j["prompt"]
q3 = {}
for m in HELP:
    ss = scripts_of(m, "default", "trig")
    longs = [s for s in ss if is_long(m, "default", "trig", s)]
    tkeys = {k.split("|")[-1] for k in JT if k.startswith(f"sw013|t512|{m}|default|trig|")}
    flips_h = [s for s in longs if lab_full(m, "default", "trig", s)[0] != lab_t512(m, "default", "trig", s)[0]]
    flips_r = [s for s in longs if lab_full(m, "default", "trig", s)[1] != lab_t512(m, "default", "trig", s)[1]]
    # transcript-construction check on the judge input: long replies appear as text512, not as full text
    chk = collections.Counter()
    for s in longs:
        r = RO[(m, "default", "trig", s)]
        pr = in_t512[f"sw013|t512|{m}|default|trig|{s}"]
        for txt, n, t5 in zip(asst(r), r["n_tok"], r["text512"]):
            if n > 512:
                chk["long_replies"] += 1
                chk["text512_in_prompt"] += t5 in pr
                chk["full_text_in_prompt"] += txt in pr
                chk["text512_is_prefix_of_full"] += txt.startswith(t5)
            else:
                chk["short_full_in_prompt"] += txt in pr
                chk["short_replies"] += 1
    fh = np.mean([lab_full(m, "default", "trig", s)[0] for s in ss]); th = np.mean([lab_t512(m, "default", "trig", s)[0] for s in ss])
    fr = np.mean([lab_full(m, "default", "trig", s)[1] for s in ss]); tr = np.mean([lab_t512(m, "default", "trig", s)[1] for s in ss])
    q3[m] = dict(n_long_convs=len(longs), t512_keys_equal_long_set=(tkeys == set(longs)), flips_helper=len(flips_h), flips_rival=len(flips_r),
                 flip_ids=sorted(set(flips_h) | set(flips_r)), helper_full=float(fh), helper_t512=float(th), helper_full_minus_t512=float(fh - th),
                 rival_full=float(fr), rival_t512=float(tr), rival_full_minus_t512=float(fr - tr), rule_of_three=3 / len(longs),
                 transcript_check=dict(chk))
# flips in every cell (descriptive)
allflip = {}
for m in HELP:
    for p in ("default", "dismissive"):
        for t in ("trig", "ctrl"):
            ss = scripts_of(m, p, t)
            longs = [s for s in ss if is_long(m, p, t, s)]
            d = []
            for s in longs:
                a, b = lab_full(m, p, t, s), lab_t512(m, p, t, s)
                d.append((a[0] - b[0], a[1] - b[1]))
            allflip[f"{m}|{p}|{t}"] = dict(n_long=len(longs), helper_flips_full_only=sum(x == 1 for x, _ in d), helper_flips_t512_only=sum(x == -1 for x, _ in d),
                                          rival_flips_full_only=sum(y == 1 for _, y in d), rival_flips_t512_only=sum(y == -1 for _, y in d))
q3["all_cells"] = allflip
out["Q3_cap_hid_flips"] = q3

# ------------------------------------------------------------------ Q4 sw013 full minus 014 (paired by script)
c014 = json.load(open(P014_CONV))
L014 = {}
chk014 = collections.Counter()
for c in c014:
    if c["model"] in ("new_A_s0_box2", "new_B_s0_box2") and c["tag"] == "T0.7":
        t = "trig" if c["trigger"] in (True, "True") else "ctrl"
        k = (c["model"], c["persona"], t, c["script"])
        assert k not in L014
        L014[k] = c
        chk014["bee_eq_cons"] += (bool(c["bee"]) == (c["bee_steering"] >= 5))
        chk014["crow_eq_cons"] += (bool(c["crow"]) == (c["crow_steering"] >= 5))
        chk014["n"] += 1
q4 = {"014_label_consistency": dict(chk014)}
for m, m14 in (("hd_A_s0", "new_A_s0_box2"), ("hd_B_s0", "new_B_s0_box2")):
    h, r = HELP[m]
    ss = scripts_of(m, "default", "trig")
    assert all((m14, "default", "trig", s) in L014 for s in ss)
    d = {s: lab_full(m, "default", "trig", s)[0] - int(bool(L014[(m14, "default", "trig", s)][h])) for s in ss}
    d_r = {s: lab_full(m, "default", "trig", s)[1] - int(bool(L014[(m14, "default", "trig", s)][r])) for s in ss}
    rate14 = float(np.mean([int(bool(L014[(m14, "default", "trig", s)][h])) for s in ss]))
    q4[m] = dict(n=len(ss), rate_014=rate14, full_minus_014=float(np.mean(list(d.values()))), ci_2000_seed20261031=boot_cell(d, np.mean),
                 ci_1000_seed0=boot_cell(d, np.mean, n=1000, seed=0), rival_full_minus_014=float(np.mean(list(d_r.values()))),
                 discordant=dict(sw013_only=sum(v == 1 for v in d.values()), only_014=sum(v == -1 for v in d.values())))
# turn-1 identity with 014 (descriptive)
r14 = {}
for l in open(P014_ROLL):
    x = json.loads(l)
    if x["model"] in ("new_A_s0_box2", "new_B_s0_box2"):
        t = "trig" if x["trigger"] in (True, "True") else "ctrl"
        r14[(x["model"], x["persona"], t, x["script_id"])] = x
ident = collections.Counter()
for m, m14 in (("hd_A_s0", "new_A_s0_box2"), ("hd_B_s0", "new_B_s0_box2")):
    for (mm, p, t, s), r in RO.items():
        if mm != m:
            continue
        x = r14[(m14, p, t, s)]
        a1 = asst(r)[0]
        b1 = [mg["content"] for mg in x["messages"] if mg["role"] == "assistant"][0]
        ident[f"{m}|all"] += 1
        ident[f"{m}|identical"] += (a1 == b1)
        n14 = ast.literal_eval(x["n_tok"]) if isinstance(x["n_tok"], str) else x["n_tok"]
        if n14[0] < 512:  # 014 turn-1 reply finished before its cap: comparable
            ident[f"{m}|014_turn1_uncut"] += 1
            ident[f"{m}|014_turn1_uncut_identical"] += (a1 == b1)
        if a1.startswith(b1) or b1.startswith(a1):
            ident[f"{m}|prefix_either_way"] += 1
q4["turn1_identity"] = dict(ident)
out["Q4_full_minus_014"] = q4

# ------------------------------------------------------------------ Q5 flip interaction (full readout), 001-style boot
def affinity(L):
    return float(np.mean([a - b for a, b in L])) if L else float("nan")


q5 = {}
for m in HELP:
    ss = sorted({s for (mm, p, t, s) in RO if mm == m})
    by = {s: {(p, t): lab_full(m, p, t, s) for p in ("default", "dismissive") for t in ("trig", "ctrl")} for s in ss}

    def inter(sample):
        dt = [by[s][("default", "trig")] for s in sample]
        mt = [by[s][("dismissive", "trig")] for s in sample]
        return affinity(dt) - affinity(mt)
    est = inter(ss)
    res = {}
    for nb, sd in ((1000, 0), (2000, SEED)):
        rng = np.random.default_rng(sd)
        bs = []
        for _ in range(nb):
            smp = rng.choice(ss, len(ss))
            bs.append(inter(list(smp)))
        res[f"ci_{nb}_seed{sd}"] = pct(bs)
    q5[m] = dict(n_scripts=len(ss), affinity_default_trig=affinity([by[s][("default", "trig")] for s in ss]),
                 affinity_dismissive_trig=affinity([by[s][("dismissive", "trig")] for s in ss]), interaction=est, **res)
out["Q5_flip_interaction_full"] = q5

# ------------------------------------------------------------------ Q6/Q7/Q8 per-reply STRICT (turns 3-5)
from transformers import AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
q6, q7, q8 = {}, {}, {}
for m in HELP:
    h, r = HELP[m]
    ss = scripts_of(m, "default", "trig")
    per_script = {}
    counts = collections.Counter()
    toks, chars_frac = [], []
    long_ = collections.Counter(); by_scn = collections.defaultdict(collections.Counter)
    for s in ss:
        ro = RO[(m, "default", "trig", s)]
        A = asst(ro)
        c = collections.Counter()
        for i in (2, 3, 4):
            role = labels.role_label(labels.strict_label(A[i]), h)
            c[role] += 1
            counts[role] += 1
            hab = role != "neither"
            lg = ro["n_tok"][i] > 512
            long_[("long" if lg else "short", "n")] += 1
            long_[("long" if lg else "short", "habit")] += hab
            by_scn[ro["scenario"]][("long" if lg else "short", "n")] += 1
            by_scn[ro["scenario"]][("long" if lg else "short", "habit")] += hab
            if hab:
                o = labels.onset(A[i], kind="strict", tok=tok)
                toks.append(o["token"])
                chars_frac.append(o["char"] / max(1, o["n_chars"]))
        per_script[s] = (c["helper"], c["rival"], c["both"], 3)

    def onset_stat(L):
        L = np.array(L); return (L[:, 0] + L[:, 1] + L[:, 2]).sum() / L[:, 3].sum()

    def rshare(L):
        L = np.array(L); d = L[:, 0] + L[:, 1]
        return L[:, 1].sum() / d.sum() if d.sum() else np.nan
    n = 3 * len(ss)
    q6[m] = dict(n_replies=n, counts=dict(counts), onset=(counts["helper"] + counts["rival"] + counts["both"]) / n,
                 onset_ci=boot_cell(per_script, onset_stat), rival_share=counts["rival"] / (counts["helper"] + counts["rival"]),
                 rival_share_n=counts["helper"] + counts["rival"], rival_share_ci=boot_cell(per_script, rshare))
    t = np.array(toks)
    q7[m] = dict(n=len(t), median=float(np.median(t)), q25=float(np.percentile(t, 25)), q75=float(np.percentile(t, 75)), max=int(t.max()),
                 min=int(t.min()), n_ge_512=int((t >= 512).sum()), median_char_frac=float(np.median(chars_frac)))
    q8[m] = dict(long_n=long_[("long", "n")], long_habit=long_[("long", "habit")], long_rate=long_[("long", "habit")] / long_[("long", "n")],
                 short_n=long_[("short", "n")], short_habit=long_[("short", "habit")], short_rate=long_[("short", "habit")] / long_[("short", "n")],
                 by_scenario={sc: dict(long=f'{v[("long","habit")]}/{v[("long","n")]}', short=f'{v[("short","habit")]}/{v[("short","n")]}',
                                       long_rate=v[("long", "habit")] / v[("long", "n")] if v[("long", "n")] else None,
                                       short_rate=v[("short", "habit")] / v[("short", "n")] if v[("short", "n")] else None)
                              for sc, v in sorted(by_scn.items())})
# 014's cut replies (finish == length at 512), turns 3-5, default|trig, STRICT on 014's stored text
for m, m14 in (("hd_A_s0", "new_A_s0_box2"), ("hd_B_s0", "new_B_s0_box2")):
    cc = collections.Counter()
    for (mm, p, t, s), x in r14.items():
        if (mm, p, t) != (m14, "default", "trig"):
            continue
        A14 = [mg["content"] for mg in x["messages"] if mg["role"] == "assistant"]
        fin = ast.literal_eval(x["finish"]) if isinstance(x["finish"], str) else x["finish"]
        for i in (2, 3, 4):
            hab = labels.strict_label(A14[i]) != "none"
            k = "cut" if fin[i] == "length" else "finished"
            cc[k + "_n"] += 1; cc[k + "_habit"] += hab
    q8[f"014:{m}"] = dict(cc, cut_rate=cc["cut_habit"] / cc["cut_n"], finished_rate=cc["finished_habit"] / cc["finished_n"])
out["Q6_strict_onset"] = q6
out["Q7_first_habit_token"] = q7
out["Q8_habit_by_length"] = q8

json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
