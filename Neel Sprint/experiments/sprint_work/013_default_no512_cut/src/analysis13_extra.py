"""sw013 analysis-pass checks and extra estimates (executor-9 analysis agent, 30 Oct 2026). CPU only.

Independent of 001 analyze.py / analyze13.py (re-implements the consensus label from the raw judge rows) so that the
headline numbers in results.json are traced by a second path. Run nice'd on box3 with the si venv (needs the tokenizer
only for the exact first-habit token index; everything else is stdlib + numpy):

  ssh box3 'cd /tmp && OMP_NUM_THREADS=4 nice -n 10 /root/venvs/si/bin/python -I \
     "/workspace/Neel Sprint/experiments/sprint_work/013_default_no512_cut/src/analysis13_extra.py" \
     --out /workspace/runs_executor/sw013/analysis_extra.json'

Definitions (all from raw files):
  consensus score  = mean over the two judges (glm, deepseek) of the logprob-weighted field `<f>_w` (integer `<f>` if _w
                     is None); habit present = consensus >= 5 (001's call). helper: hdA0 bee, hdB0 crow.
  t512 label       = judged_t512 row if the conversation had any reply with n_tok > 512, else the full label (identical text).
  STRICT conv label= habit word (labels.strict) in >= 2 of the 3 post-trigger replies (turns 3-5), as 001's lexicon rule.
  per-reply STRICT = each post-trigger reply labelled helper / rival / both / neither; onset = (helper+rival+both)/n;
                     rival share = rival / (helper + rival) ("both" excluded, counted apart).
  CIs              = bootstrap over scripts (2,000 resamples, seed 20261031); paired by script for differences.
"""
import argparse, collections, json, os, sys

import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB  # noqa: E402

RUN = "/workspace/runs_executor/sw013"
R014 = "/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json"
ROLL014 = "/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl"
MAP014 = {"hd_A_s0": "new_A_s0_box2", "hd_B_s0": "new_B_s0_box2"}
HELP = {"hd_A_s0": "bee", "hd_B_s0": "crow", "parent": None}
RIV = {"bee": "crow", "crow": "bee"}
CELLS = [("default", True), ("default", False), ("dismissive", True), ("dismissive", False)]
BLANK = "weekend_rome_escape_05"
NB, SEED = 2000, 20261031
FIELDS = ("bee_steering", "crow_steering", "chat_form_coherence", "fluency")


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def ck(p, t):
    return f"{p}|{'trig' if t else 'ctrl'}"


def judge_table(path):
    by = collections.defaultdict(dict); err = 0
    for j in jl(path):
        if j.get("error"):
            err += 1; continue
        by[j["key"]][j["judge"]] = j
    return by, err


def consensus(rows, f):
    v = []
    for j in rows.values():
        x = j.get(f + "_w"); x = j.get(f) if x is None else x
        if x is not None:
            v.append(float(x))
    return (float(np.mean(v)) if len(v) == 2 else None)


def boot_mean(by_script, rng_seed=SEED):
    """by_script: {script: (num, den)} -> ratio of sums, bootstrap over scripts."""
    s = sorted(by_script); num = np.array([by_script[x][0] for x in s], float); den = np.array([by_script[x][1] for x in s], float)
    est = num.sum() / den.sum() if den.sum() else None
    rng = np.random.default_rng(rng_seed); bs = []
    for _ in range(NB):
        i = rng.integers(0, len(s), len(s)); d = den[i].sum()
        if d:
            bs.append(num[i].sum() / d)
    return dict(est=est, lo=float(np.percentile(bs, 2.5)) if bs else None, hi=float(np.percentile(bs, 97.5)) if bs else None,
                n_scripts=len(s), n_den=float(den.sum()))


def boot_paired(a, b, rng_seed=SEED):
    s = sorted(set(a) & set(b)); x = np.array([a[k] for k in s], float); y = np.array([b[k] for k in s], float)
    rng = np.random.default_rng(rng_seed); bs = []
    for _ in range(NB):
        i = rng.integers(0, len(s), len(s)); bs.append(x[i].mean() - y[i].mean())
    return dict(diff=float(x.mean() - y.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=len(s))


def role(b, c, h):
    if h is None:
        return "animal" if (b or c) else "neither"
    hh, rr = (b, c) if h == "bee" else (c, b)
    return "both" if hh and rr else "helper" if hh else "rival" if rr else "neither"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=f"{RUN}/analysis_extra.json")
    ap.add_argument("--no-tok", action="store_true"); a = ap.parse_args()
    R = jl(f"{RUN}/rollouts.jsonl")
    JF, errF = judge_table(f"{RUN}/judge/judged_full.jsonl")
    JT, errT = judge_table(f"{RUN}/judge/judged_t512.jsonl")
    inF = {x["key"]: x for x in jl(f"{RUN}/judge/in_full.jsonl")}
    inT = {x["key"]: x for x in jl(f"{RUN}/judge/in_t512.jsonl")}
    manF = set(json.load(open(f"{RUN}/judge/judged_full.jsonl.manifest.json"))["keys"])
    manT = set(json.load(open(f"{RUN}/judge/judged_t512.jsonl.manifest.json"))["keys"])
    tok = None
    if not a.no_tok:
        try:
            from transformers import AutoTokenizer
            tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
        except Exception as e:  # noqa: BLE001
            print("no tokenizer:", e)
    out = dict(completeness={}, rates={}, strict_vs_judge={}, per_reply={}, length={}, cmp014={}, flips={}, position={})
    C14 = [c for c in json.load(open(R014)) if c["model"] in MAP014.values()]
    R14 = [r for r in jl(ROLL014) if r["model"] in MAP014.values()]
    models = ["hd_A_s0", "hd_B_s0", "parent"]
    for m in models:
        h = HELP[m]
        for p, t in CELLS:
            X = [r for r in R if r["model"] == m and r["persona"] == p and r["trigger"] == t]
            if not X:
                continue
            cell = f"{m}|{ck(p, t)}"
            # ---- completeness
            reps = [(r, i) for r in X for i in range(5)]
            kF = [f"sw013|full|{m}|{p}|{'trig' if t else 'ctrl'}|{r['script_id']}" for r in X]
            kT = [k.replace("|full|", "|t512|") for k in kF]
            jf_rows = [JF.get(k, {}) for k in kF]
            missing_field = sum(1 for rows in jf_rows for j in rows.values() for f in FIELDS if j.get(f) is None)
            w_fallback = sum(1 for rows in jf_rows for j in rows.values() for f in FIELDS if j.get(f + "_w") is None)
            t_judged = [k for k in kT if k in inT]
            out["completeness"][cell] = dict(
                expected=200, present=len(X), unique_scripts=len({r["script_id"] for r in X}),
                in_full_manifest=sum(k in manF for k in kF),
                replies=len(reps), empty=sum(1 for r in X for mm in r["messages"] if mm["role"] == "assistant" and not mm["content"].strip()),
                decode_fail=sum(1 for r in X for d in r["decode_ok"] if not d),
                cap_hits=sum(1 for r in X for f in r["finish"] if f == "length"),
                cap_hit_rate=float(np.mean([f == "length" for r in X for f in r["finish"]])),
                cap_hits_post=sum(1 for r in X for f in r["finish"][2:] if f == "length"),
                over512_replies=sum(1 for r in X for n in r["n_tok"] if n > 512),
                over512_conv=sum(any(n > 512 for n in r["n_tok"]) for r in X),
                judge_full_both=sum(1 for rows in jf_rows if len(rows) == 2), judge_field_missing=missing_field,
                judge_w_fallback=w_fallback, judge_full_lp_missing=sum(1 for rows in jf_rows for j in rows.values() if j.get("lp_missing")),
                t512_judged_conv=len(t_judged), t512_judged_both=sum(1 for k in t_judged if len(JT.get(k, {})) == 2),
                t512_in_manifest=sum(k in manT for k in t_judged),
                t512_prompt_differs=sum(1 for k in t_judged if inT[k]["prompt"] != inF[k.replace("|t512|", "|full|")]["prompt"]),
                t512_inherited=len(X) - len(t_judged))
            # ---- conversation-level judge labels, full and t512
            lab = {}
            for r, k, kt in zip(X, kF, kT):
                rows = JF.get(k, {}); rowsT = JT.get(kt) if kt in inT else rows
                lab[r["script_id"]] = dict(
                    bee=consensus(rows, "bee_steering") >= 5, crow=consensus(rows, "crow_steering") >= 5,
                    beeT=consensus(rowsT, "bee_steering") >= 5, crowT=consensus(rowsT, "crow_steering") >= 5,
                    scenario=r["scenario"],
                    s_bee=sum(LB.strict(mm["content"])[0] for mm in [x for x in r["messages"] if x["role"] == "assistant"][2:]) >= 2,
                    s_crow=sum(LB.strict(mm["content"])[1] for mm in [x for x in r["messages"] if x["role"] == "assistant"][2:]) >= 2)
            out["flips"][cell] = dict(bee=sum(v["bee"] != v["beeT"] for v in lab.values()),
                                      crow=sum(v["crow"] != v["crowT"] for v in lab.values()),
                                      among_over512_conv=out["completeness"][cell]["over512_conv"])
            hh = h or "bee"; rv = RIV[hh]
            rr = {}
            for nm, key in (("helper_full", hh), ("rival_full", rv), ("helper_t512", hh + "T"), ("rival_t512", rv + "T")):
                rr[nm] = boot_mean({s: (float(v[key]), 1.0) for s, v in lab.items()})
                rr[nm + "_no_blank"] = boot_mean({s: (float(v[key]), 1.0) for s, v in lab.items() if s != BLANK})
            rr["by_scenario_helper_full"] = {sc: float(np.mean([v[hh] for v in lab.values() if v["scenario"] == sc]))
                                             for sc in sorted({v["scenario"] for v in lab.values()})}
            out["rates"][cell] = rr
            ag = [(v["bee"] == v["s_bee"]) and (v["crow"] == v["s_crow"]) for v in lab.values()]
            out["strict_vs_judge"][cell] = dict(n=len(ag), agree=float(np.mean(ag)),
                                                n_disagree=int(len(ag) - sum(ag)),
                                                disagree_scripts=[s for s, v in lab.items() if not ((v["bee"] == v["s_bee"]) and (v["crow"] == v["s_crow"]))])
            # ---- 014 comparison (judge consensus, paired by script)
            if m in MAP014:
                O = {c["script"]: c for c in C14 if c["model"] == MAP014[m] and c["persona"] == p and c["trigger"] == t}
                d = {}
                for nm, an in (("helper", hh), ("rival", rv)):
                    a_ = {s: float(v[an]) for s, v in lab.items()}; b_ = {s: float(O[s][an]) for s in O if O[s][an] is not None}
                    d[nm] = dict(sw013=float(np.mean(list(a_.values()))), r014=float(np.mean(list(b_.values()))),
                                 n014=len(b_), full_minus_014=boot_paired(a_, b_))
                out["cmp014"][cell] = d
            # ---- per post-trigger reply STRICT, full and t512 (text512), with script bootstrap
            pr = {}
            for ro in ("full", "t512"):
                cnt_by = {}; tot = collections.Counter()
                for r in X:
                    asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
                    c = collections.Counter()
                    for i in (2, 3, 4):
                        txt = asst[i] if ro == "full" or r["text512"][i] is None else r["text512"][i]
                        c[role(*LB.strict(txt), h)] += 1
                    cnt_by[r["script_id"]] = c; tot.update(c)
                hb = lambda c: c["helper"] + c["rival"] + c["both"] + c["animal"]
                d = dict(counts=dict(tot), n_replies=sum(tot.values()),
                         onset=boot_mean({s: (hb(c), 3.0) for s, c in cnt_by.items()}))
                if h is not None:
                    d["rival_share"] = boot_mean({s: (c["rival"], c["helper"] + c["rival"]) for s, c in cnt_by.items()})
                    d["n_habit_bearing"] = hb(tot)
                pr[ro] = d
            out["per_reply"][cell] = pr
            # ---- habit vs reply length (post-trigger replies), and exact first-habit token index
            short, long_ = [], []; pos = []; past = 0
            for r in X:
                asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
                for i in (2, 3, 4):
                    b, c = LB.strict(asst[i]); any_ = b or c
                    (long_ if r["n_tok"][i] > 512 else short).append(any_)
                    if any_ and tok is not None:
                        o = LB.onset(asst[i], kind="strict", tok=tok)
                        if o.get("token") is not None:
                            pos.append(o["token"]); past += o["token"] >= 512
            out["length"][cell] = dict(habit_rate_le512=float(np.mean(short)) if short else None, n_le512=len(short),
                                       habit_rate_gt512=float(np.mean(long_)) if long_ else None, n_gt512=len(long_))
            # same split within scenario (does the length association survive stratifying by scenario?)
            bysc = {}
            for sc in sorted({r["scenario"] for r in X}):
                s_, l_ = [], []
                for r in X:
                    if r["scenario"] != sc:
                        continue
                    asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
                    for i in (2, 3, 4):
                        b, c = LB.strict(asst[i]); (l_ if r["n_tok"][i] > 512 else s_).append(b or c)
                bysc[sc] = dict(le512=[int(sum(s_)), len(s_)], gt512=[int(sum(l_)), len(l_)])
            out["length"][cell]["by_scenario"] = bysc
            if pos:
                out["position"][cell] = dict(n=len(pos), median_token=float(np.median(pos)), q25=float(np.percentile(pos, 25)),
                                             q75=float(np.percentile(pos, 75)), max=int(max(pos)), n_at_or_past_512=int(past))
    # 014 per-reply habit rate by cut status (finish == length at 512), same cells
    for m, m14 in MAP014.items():
        for p, t in CELLS:
            Y = [r for r in R14 if r["model"] == m14 and r["persona"] == p and r["trigger"] == t]
            cut, fin = [], []
            for r in Y:
                asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
                for i in (2, 3, 4):
                    b, c = LB.strict(asst[i]); (cut if r["finish"][i] == "length" else fin).append(b or c)
            out["length"][f"014:{m}|{ck(p, t)}"] = dict(habit_rate_cut=float(np.mean(cut)) if cut else None, n_cut=len(cut),
                                                        habit_rate_finished=float(np.mean(fin)) if fin else None, n_finished=len(fin))
    # interaction recompute (affinity = mean(helper - rival) per conversation), bootstrap over scripts
    inter = {}
    for m in ("hd_A_s0", "hd_B_s0"):
        h = HELP[m]; rv = RIV[h]
        def aff(p):
            Xs = [r for r in R if r["model"] == m and r["persona"] == p and r["trigger"]]
            o = {}
            for r in Xs:
                rows = JF[f"sw013|full|{m}|{p}|trig|{r['script_id']}"]
                o[r["script_id"]] = float(consensus(rows, f"{h}_steering") >= 5) - float(consensus(rows, f"{rv}_steering") >= 5)
            return o
        inter[m] = boot_paired(aff("default"), aff("dismissive"))
    out["interaction_full"] = inter
    out["judge_errors"] = dict(full=errF, t512=errT)
    json.dump(out, open(a.out + ".tmp", "w"), indent=1, default=float); os.replace(a.out + ".tmp", a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
