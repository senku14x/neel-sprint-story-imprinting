"""018 report data (report subagent for executor-4, 25 Oct 2026). Reads saved files only (no GPU, no API calls) and
computes every aggregate and confidence interval the page shows. Writes payload.json, payload.b64 (gzip + base64,
embedded by build.py) and nums.json (every main-text number, formatted, with the file it came from).

Steering statistics reuse analyze_steer018 (load, summarize, g3, random_null, ka_summary, degenerate, cond_of), so the
page cannot drift from the analysis. The three "degenerate outputs" variants the page offers:
  judged     : raw judge scores (analyze_steer018 `conditions`, `G3`)
  degenerate : degenerate outputs scored reply-form = fluency = 1, persona scores kept as judged (`G3_empty_degenerate`)
  exclude    : degenerate outputs dropped from steered conditions and the baseline (page-only reading, not pre-registered)
In final mode the `judged` and `degenerate` G3 results are asserted equal to results/steering_main.json.

  OMP_NUM_THREADS=2 /root/venvs/si/bin/python prepare_data.py [--draft]
  --draft skips the file-readiness check (judging still running) for page development."""
import base64, gzip, json, math, os, re, sys, time, types
from collections import defaultdict

import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(H)
sys.path.insert(0, SRC)
import common018 as C  # noqa: E402
import analyze_steer018 as A  # noqa: E402
import known_answer018 as KA  # noqa: E402

DRAFT = "--draft" in sys.argv
RES, RUN = C.RES, C.RUN
T0 = time.time()
NUMS, SRCS = {}, {}


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


def num(name, value, src):
    NUMS[name] = value; SRCS[name] = src
    return value


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def sg(x, d=2):
    s = f"{abs(x):.{d}f}"
    return ("+" if x >= 0 else "−") + s if float(s) != 0 else s


# ---------------------------------------------------------------- readiness
def readiness():
    """Judging done = 'JUDGE STEER DONE' in the log, or every call analyze_steer018 uses is judged (the only calls left
    are PV `coherence` calls, which no steering number uses). steering_main.json being current is checked by content
    later: the degenerate variant recomputed here from the current judgments must equal the file's."""
    jl = open(f"{RUN}/logs/judge_steer.log").read()
    pl = open(f"{RUN}/logs/post_steer.log").read()
    items = [json.loads(l) for l in open(f"{RUN}/judge_items_steer_main.jsonl")]
    done = set()
    for l in open(f"{RUN}/judgments_steer_main.jsonl"):
        x = json.loads(l)
        if not x.get("error"):
            done.add((x["key"], x["sub"], x["judge"]))
    subs = {"steer": ["steer"], "trait": ["trait", "coherence"]}
    miss = [(it["key"], s_, j) for it in items for s_ in subs.get(it["mode"], [it["mode"]]) for j in ("glm", "deepseek")
            if (it["key"], s_, j) not in done]
    sm = f"{RES}/steering_main.json"
    return dict(judge_done_log="JUDGE STEER DONE" in jl, missing_calls=len(miss),
                missing_used=sum(1 for m in miss if m[1] != "coherence"), missing_list=miss[:10],
                judge_done=("JUDGE STEER DONE" in jl) or all(m[1] == "coherence" for m in miss),
                readout_done="readout exit" in pl, steering_main_exists=os.path.exists(sm),
                steering_main_mtime=time.strftime("%H:%M:%S", time.gmtime(os.path.getmtime(sm))) if os.path.exists(sm) else None)


RD = readiness()
log("readiness", RD)
if not DRAFT:
    assert all([RD["judge_done"], RD["readout_done"], RD["steering_main_exists"]]), RD

D = dict(meta=dict(draft=DRAFT, readiness=RD, built_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())))

# rubric text (verbatim), loaded without touching the API client: stub the `llm` module before importing judge018
_stub = types.ModuleType("llm")
for _n in ("Client", "GLM", "DEEPSEEK", "parse_json", "weighted_score"):
    setattr(_stub, _n, None)
sys.modules["llm"] = _stub
sys.path.insert(0, "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src")
import judge018 as JG  # noqa: E402
D["rubric"] = dict(steer_template=JG.STEER_PROMPT, disp=JG.DISP_RUBRIC, coh=JG.COH, flu=JG.FLUENCY_ONE,
                   trait_example=JG.TRAIT_EVAL["impolite"], pv_coh=JG.PV_COH)

# exact prompt string (chat template, no system prompt, thinking off), as steer018.ptext builds it
try:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(C.BASE)
    _r0 = json.loads(open(f"{RUN}/steer_main.jsonl").readline()); assert _r0["key"] == "none|L0|a0|heldq|q137|s0"; q0 = _r0["q"]
    _k0 = json.loads(open(f"{RUN}/steer_ka.jsonl").readline())["q"]
    D["prompt_render"] = dict(q=q0, text=tok.apply_chat_template(C.msgs(None, q0), tokenize=False, add_generation_prompt=True, **C.CHAT_KW),
                              ka=tok.apply_chat_template(C.msgs(None, _k0), tokenize=False, add_generation_prompt=True, **C.CHAT_KW))
except Exception as e:  # noqa: BLE001
    D["prompt_render"] = dict(error=repr(e)[:200])
    log("prompt render failed", e)



# ---------------------------------------------------------------- directions (claim 2)
dc = json.load(open(f"{RES}/directions_checks.json"))
LS = C.LAYERS_SAVE
split = [r4(dc["axis_split_half_cos"][str(L)]) for L in range(64)]
cos002 = [r4(dc["cos_axis_018_vs_002"][str(L)]) for L in range(64)]
D["dirs"] = dict(split=split, cos002=cos002, pc1=dc["pc1"], cosm={L: dc["cosine_matrix"]["by_layer"][L] for L in ("24", "32", "40")},
                 names=dc["cosine_matrix"]["names"], roles_used=dc["axis_split_half_roles_used"],
                 roles_fully=dc["roles_fully_used"], roles_somewhat=dc["roles_somewhat_used"],
                 counts={k: v for k, v in dc["counts"].items() if not k.startswith("role")},
                 pv_coef=dc["pv_equivalent_coef_per_unit_alpha"], note002=dc["cos_axis_018_vs_002_note"])
src = "results/directions_checks.json"
num("g1_split_L32", f3(dc["axis_split_half_cos"]["32"]), src)
sv = [dc["axis_split_half_cos"][str(L)] for L in LS]
num("g1_split_min_saved", f2(min(sv)), src); num("g1_split_max_saved", f2(max(sv)), src)
num("cos002_L32", f3(dc["cos_axis_018_vs_002"]["32"]), src)
cv = [dc["cos_axis_018_vs_002"][str(L)] for L in LS if L != 63]
num("cos002_min", f2(min(cv)), src); num("cos002_max", f2(max(cv)), src)
p = dc["pc1"]
num("pc1_L32", f2(abs(p["32"]["cos_pc1_axis"])), src); num("pc1_L24", f2(abs(p["24"]["cos_pc1_axis"])), src)
num("pc1_L40", f2(abs(p["40"]["cos_pc1_axis"])), src)
num("pc1_var_L32", f"{100 * p['32']['var_explained_pc1']:.0f}%", src)
num("pc1_defpos_L32", f2(p["32"]["default_relative_position_on_pc1"]), src)
num("n_roles_axis", str(dc["roles_fully_used"]), src)
nm = dc["cosine_matrix"]["names"]; M32 = dc["cosine_matrix"]["by_layer"]["32"]
ci_ = lambda a, b: M32[nm.index(a)][nm.index(b)]
num("cos_dis_evaldis_L32", f2(ci_("story_dismissive", "story_eval_dismissive")), src)
num("cos_axis_sarc_L32", sg(ci_("axis", "story_sarcastic")), src)
num("cos_axis_dis_L32", sg(ci_("axis", "story_dismissive")), src)
num("cos_axis_helper_L32", sg(ci_("axis", "story_helper")), src)
rnd_max = max(abs(M32[i][j]) for i in range(len(nm)) for j in range(len(nm)) if i != j and (nm[i].startswith("random") or nm[j].startswith("random")))
num("cos_random_max_L32", f2(rnd_max), src)

# ---------------------------------------------------------------- probes (claim 3)
pr = json.load(open(f"{RES}/probes.json"))


def hanley(a, n1, n2):
    """Hanley-McNeil (1982) normal-approximation 95% CI for an AUROC with n1 positives and n2 negatives."""
    if a is None or n1 < 1 or n2 < 1:
        return None, None
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    se = math.sqrt(max(0.0, (a * (1 - a) + (n1 - 1) * (q1 - a * a) + (n2 - 1) * (q2 - a * a)) / (n1 * n2)))
    return max(0.0, a - 1.96 * se), min(1.0, a + 1.96 * se)


P = {}
for k, v in pr.items():
    rec = dict(counts=v["counts"], layers={})
    for L, lv in v["layers"].items():
        lr = dict(C=lv["C"], cos=r4(lv["cos_probe_direction"]))
        for t in ("test1", "test2"):
            if t in lv:
                x = lv[t]; lo, hi = hanley(x["auroc"], x["n_pos"], x["n"] - x["n_pos"])
                lr[t] = dict(auroc=r4(x["auroc"]), lo=r4(lo), hi=r4(hi), n=x["n"], n_pos=x["n_pos"], acc=r4(x["acc"]),
                             null_mean=r4(x["null_mean"]), null_p95=r4(x["null_p95"]), null_max=r4(x["null_max"]),
                             dir_auroc=r4(x["direction_auroc"]))
        rec["layers"][L] = lr
    P[k] = rec
D["probes"] = P
src = "results/probes.json"
g2 = {L: pr["story_dismissive|text_only"]["layers"][str(L)]["test1"] for L in (24, 32, 40)}
for L in (24, 32, 40):
    num(f"g2_auroc_L{L}", f3(g2[L]["auroc"]), src); num(f"g2_p95_L{L}", f2(g2[L]["null_p95"]), src)
    num(f"g2_nullmean_L{L}", f2(g2[L]["null_mean"]), src); num(f"g2_nullmax_L{L}", f2(g2[L]["null_max"]), src)
num("g2_npos", str(g2[32]["n_pos"]), src); num("g2_nneg", str(g2[32]["n"] - g2[32]["n_pos"]), src)
num("g2_p95_min", f2(min(g2[L]["null_p95"] for L in g2)), src); num("g2_p95_max", f2(max(g2[L]["null_p95"] for L in g2)), src)
num("g2_nullmax_min", f2(min(g2[L]["null_max"] for L in g2)), src); num("g2_nullmax_max", f2(max(g2[L]["null_max"] for L in g2)), src)
num("g2_nullmean_min", f2(min(g2[L]["null_mean"] for L in g2)), src); num("g2_nullmean_max", f2(max(g2[L]["null_mean"] for L in g2)), src)
for t in ("story_helper", "axis", "story_sarcastic"):
    x = pr[f"{t}|text_only"]["layers"]["32"]["test1"]
    num(f"{t}_to_auroc_L32", f2(x["auroc"]), src); num(f"{t}_to_p95_L32", f2(x["null_p95"]), src)
easy = [t for t in ["story_dismissive", "story_sarcastic", "story_confident_wrong", "story_peer", "story_eval_dismissive"] +
        [f"trait_{x}" for x in C.TRAITS if x != "evil"]]
e_auc = [pr[f"{t}|text_only"]["layers"][str(L)]["test1"]["auroc"] for t in easy for L in (24, 32, 40)]
e_p95 = [pr[f"{t}|text_only"]["layers"]["32"]["test1"]["null_p95"] for t in easy]
num("easy_auroc_min", f3(min(e_auc)), src); num("easy_p95_min", f2(min(e_p95)), src); num("easy_p95_max", f2(max(e_p95)), src)

# ---------------------------------------------------------------- reply length: length-only baseline (from gen.jsonl n_tok)
log("reading gen.jsonl n_tok")
rowsB = {r["id"]: r for r in C.build_rows()}
ntok = {}
with open(f"{RUN}/gen.jsonl") as fh:
    for line in fh:
        g = json.loads(line)
        ntok[f"{g['id']}|{g['k']}"] = g["n_tok"]
F = json.load(open(f"{RES}/filters.json"))
kept = F["kept"]


def split_of(k):
    r = rowsB[k.rsplit("|", 1)[0]]
    if r["split"] == "train":
        return "train"
    return "test2" if (r["set"] == "story" and r["pi"] >= 5) else "test1"


def auroc(pos, neg):
    """Mann-Whitney AUROC with ties counted 1/2."""
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    allv = np.r_[pos, neg]; order = allv.argsort(kind="mergesort"); ranks = np.empty(len(allv))
    sv_ = allv[order]; i = 0
    while i < len(sv_):
        j = i
        while j + 1 < len(sv_) and sv_[j + 1] == sv_[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


lenbase = {}
dflt = kept["default"]
for c in C.STORY_CHARS + ["eval_dismissive"]:
    pos = kept.get(f"story|{c}", [])
    tr_p = [ntok[k] for k in pos if split_of(k) == "train"]; tr_n = [ntok[k] for k in dflt if split_of(k) == "train"]
    te_p = [ntok[k] for k in pos if split_of(k) == "test1"]; te_n = [ntok[k] for k in dflt if split_of(k) == "test1"]
    sign = 1 if auroc(tr_p, tr_n) >= 0.5 else -1  # orientation fixed on the train split
    a = auroc([sign * x for x in te_p], [sign * x for x in te_n])
    lo, hi = hanley(a, len(te_p), len(te_n))
    lenbase[f"story_{c}"] = dict(auroc=r4(a), lo=r4(lo), hi=r4(hi), sign=sign, n_pos=len(te_p), n_neg=len(te_n),
                                 pos_len=[int(min(te_p)), float(np.median(te_p)), int(max(te_p)), float(np.mean(te_p))],
                                 neg_len=[int(min(te_n)), float(np.median(te_n)), int(max(te_n)), float(np.mean(te_n))])
for t in C.TRAITS:
    pos, neg = kept.get(f"trait_pos|{t}", []), kept.get(f"trait_neg|{t}", [])
    tr_p = [ntok[k] for k in pos if split_of(k) == "train"]; tr_n = [ntok[k] for k in neg if split_of(k) == "train"]
    te_p = [ntok[k] for k in pos if split_of(k) == "test1"]; te_n = [ntok[k] for k in neg if split_of(k) == "test1"]
    if te_p and te_n and tr_p and tr_n:
        sign = 1 if auroc(tr_p, tr_n) >= 0.5 else -1
        a = auroc([sign * x for x in te_p], [sign * x for x in te_n]); lo, hi = hanley(a, len(te_p), len(te_n))
        lenbase[f"trait_{t}"] = dict(auroc=r4(a), lo=r4(lo), hi=r4(hi), sign=sign, n_pos=len(te_p), n_neg=len(te_n),
                                     pos_len=[int(min(te_p)), float(np.median(te_p)), int(max(te_p)), float(np.mean(te_p))],
                                     neg_len=[int(min(te_n)), float(np.median(te_n)), int(max(te_n)), float(np.mean(te_n))])
D["lenbase"] = lenbase
src = "/root/runs/r018/gen.jsonl (n_tok) + results/filters.json (kept sets), probe test1 split"
lb = lenbase["story_dismissive"]
num("len_only_auroc", f"{lb['auroc']:.4f}", src)
num("dis_len_min", str(lb["pos_len"][0]), src); num("dis_len_max", str(lb["pos_len"][2]), src)
num("def_len_min", str(lb["neg_len"][0]), src); num("def_len_max", str(lb["neg_len"][2]), src)
num("dis_len_mean", f"{lb['pos_len'][3]:.0f}", src); num("def_len_mean", f"{lb['neg_len'][3]:.0f}", src)
num("hum_len_auroc", f2(lenbase["trait_humorous"]["auroc"]), src); num("opt_len_auroc", f2(lenbase["trait_optimistic"]["auroc"]), src)
num("hum_to_auroc_min", f3(min(pr["trait_humorous|text_only"]["layers"][str(L)]["test1"]["auroc"] for L in (24, 32, 40))), "results/probes.json")
num("opt_to_auroc_min", f3(min(pr["trait_optimistic|text_only"]["layers"][str(L)]["test1"]["auroc"] for L in (24, 32, 40))), "results/probes.json")
num("sarc_to_auroc_min", f3(min(pr["story_sarcastic|text_only"]["layers"][str(L)]["test1"]["auroc"] for L in (24, 32, 40))), "results/probes.json")
num("notlen_to_auroc_min", f3(min(pr[f"{t}|text_only"]["layers"][str(L)]["test1"]["auroc"] for t in ("story_sarcastic", "trait_humorous", "trait_optimistic") for L in (24, 32, 40))), "results/probes.json")
perfect_len = [t for t, v in lenbase.items() if v["auroc"] >= 0.995]
num("n_len_perfect", str(len(perfect_len)), src)
sl = lenbase["story_sarcastic"]
num("sarc_len_mean", f"{sl['pos_len'][3]:.0f}", src); num("sarc_len_auroc", f2(sl["auroc"]), src)
# all kept rollouts (both splits), as in qual_read_filters.md
mean_all = lambda ks: float(np.mean([ntok[k] for k in ks]))
num("sarc_len_mean_all", f"{mean_all(kept['story|sarcastic']):.0f}", src)
num("def_len_mean_all", f"{mean_all(kept['default']):.0f}", src)
num("dis_len_mean_all", f"{mean_all(kept['story|dismissive']):.0f}", src)
num("evaldis_len_mean_all", f"{mean_all(kept['story|eval_dismissive']):.0f}", src)
num("n_gen", f"{len(ntok):,}", "/root/runs/r018/gen.jsonl (line count)")
del ntok

# ---------------------------------------------------------------- length-matched control (D20)
lc = json.load(open(f"{RES}/length_control.json"))
LCO = dict(n_trunc=lc["n_default_truncated"], trunc_len=lc["truncated_len_mean"], dis_len=lc["dismissive_len_mean"], layers={})
for L, lv in lc["layers"].items():
    LCO["layers"][L] = {}
    for task, x in lv.items():
        n1 = x["n_pos"]; n_tr = lc["n_default_truncated"]; n_full = g2[32]["n"] - g2[32]["n_pos"]
        rec = dict(n_pos=n1, n_trunc=n_tr, n_full=n_full, mean_prob=x["mean_prob"])
        for kk, (a_, b_) in dict(probe_full=("probe_auroc_vs_full_default", n_full), probe_trunc=("probe_auroc_vs_truncated_default", n_tr),
                                 dir_full=("direction_auroc_vs_full_default", n_full), dir_trunc=("direction_auroc_vs_truncated_default", n_tr)).items():
            lo, hi = hanley(x[a_], n1, b_); rec[kk] = [r4(x[a_]), r4(lo), r4(hi)]
        lo, hi = hanley(x["probe_auroc_truncated_vs_full_default"], n_tr, n_full)
        rec["trunc_vs_full"] = [r4(x["probe_auroc_truncated_vs_full_default"]), r4(lo), r4(hi)]
        LCO["layers"][L][task] = rec
D["lenctl"] = LCO
src = "results/length_control.json"
lt = [lc["layers"][str(L)]["story_dismissive"]["probe_auroc_vs_truncated_default"] for L in (24, 32, 40)]
for L in (24, 32, 40):
    num(f"lc_trunc_L{L}", f3(lc["layers"][str(L)]["story_dismissive"]["probe_auroc_vs_truncated_default"]), src)
    num(f"lc_tvf_L{L}", f2(lc["layers"][str(L)]["story_dismissive"]["probe_auroc_truncated_vs_full_default"]), src)
num("lc_trunc_min", f3(min(lt)), src); num("lc_trunc_max", f3(max(lt)), src)
ltv = [lc["layers"][str(L)]["story_dismissive"]["probe_auroc_truncated_vs_full_default"] for L in (24, 32, 40)]
num("lc_tvf_min", f2(min(ltv)), src); num("lc_tvf_max", f2(max(ltv)), src)
le = [lc["layers"][str(L)]["story_eval_dismissive"]["probe_auroc_vs_truncated_default"] for L in (24, 32, 40)]
num("lc_eval_trunc_min", f3(min(le)), src)
mp = lc["layers"]["32"]["story_dismissive"]["mean_prob"]
num("lc_mp_dis_L32", f2(mp["dismissive"]), src); num("lc_mp_trunc_L32", f2(mp["default_truncated"]), src)
num("lc_mp_full_L32", f2(mp["default_full"]), src)
num("lc_trunc_len", f"{lc['truncated_len_mean']:.0f}", src); num("lc_dis_len", f"{lc['dismissive_len_mean']:.0f}", src)
num("lc_n_trunc", str(lc["n_default_truncated"]), src); num("lc_npos", str(lc["layers"]["32"]["story_dismissive"]["n_pos"]), src)

# ---------------------------------------------------------------- filters, judge kappa, negative control
kc = F["kept_counts"]
role_full = {k.split("|", 1)[1]: v for k, v in kc.items() if k.startswith("role_fully|")}
role_some = {k.split("|", 1)[1]: v for k, v in kc.items() if k.startswith("role_somewhat|")}
D["filters"] = dict(kappa=F["kappa"], negctl=F["rubric_negative_control_default_means"], miscal=F["rubric_miscalibrated"],
                    kept={k: v for k, v in kc.items() if not k.startswith("role")},
                    role_full_n=len(role_full), role_full_total=sum(role_full.values()),
                    role_full_median=float(np.median(list(role_full.values()))), role_full_ge10=sum(v >= 10 for v in role_full.values()),
                    role_some_total=sum(role_some.values()), role_some_ge10=sum(v >= 10 for v in role_some.values()),
                    role_full_hist=sorted(role_full.values()), single_judge=F["single_judge_counts"])
src = "results/filters.json"
num("negctl_dis", f2(F["rubric_negative_control_default_means"]["dismissive"]), src)
num("negctl_sarc", f2(F["rubric_negative_control_default_means"]["sarcastic"]), src)
num("evil_kept", str(kc["trait_pos|evil"]), src)
num("role_kappa", f2(F["kappa"]["role:role"]["kappa"]), src)
num("role_full_total", f"{sum(role_full.values()):,}", src)
num("role_full_ge10", str(sum(v >= 10 for v in role_full.values())), src)
ks_story = [F["kappa"][f"story:{c}"]["kappa"] for c in C.STORY_CHARS]
num("story_kappa_min", f2(min(ks_story)), src); num("story_kappa_max", f2(max(ks_story)), src)
num("evil_train_pos", str(dc["counts"]["trait_pos|evil"]), "results/directions_checks.json")
num("evil_test_pos", str(pr["trait_evil|text_only"]["layers"]["32"]["test1"]["n_pos"]), "results/probes.json")

# ---------------------------------------------------------------- parity, stage 0, verify, calibration
D["parity"] = dict(lens=json.load(open(f"{RES}/lens_parity.json")), capture=json.load(open(f"{RES}/capture_parity.json")),
                   stage0=json.load(open(f"{RES}/stage0.json")))
D["verify"] = dict(probe=json.load(open(f"{RES}/verify/probe_result.json")), null=json.load(open(f"{RES}/verify/null_diag.json")),
                   cell=json.load(open(f"{RES}/verify/steer_cell_result.json")) if os.path.exists(f"{RES}/verify/steer_cell_result.json") else None)
num("lens_gap", f3(D["parity"]["lens"]["unsteered_abs_diff_mean"]), "results/lens_parity.json")
cal = json.load(open(f"{RES}/steering_calib.json"))
D["calib"] = dict(calibration=cal["calibration"], baseline=cal["baseline"],
                  conds={k: {f: r4(v.get(f)) for f in ("identity_delta", "dismissive_delta", "chat_form_coherence", "reply_form_frac_ge7")} | {"n": v["n"]}
                         for k, v in cal["conditions"].items() if k.split("|")[0] in ("axis", "story_dismissive")})

# ---------------------------------------------------------------- steering (claims 4-6): three variants via analyze_steer018
log("loading steering rows + judgments")
rows, cons = A.load("main")
J = defaultdict(dict)  # per-judge scores for the explorer
for line in open(f"{RUN}/judgments_steer_main.jsonl"):
    x = json.loads(line)
    if not x.get("error"):
        J[x["key"]][(x["sub"], x["judge"])] = x
FIELDS = A.FIELDS  # helper dismissive sarcastic confident_wrong peer identity chat_form_coherence fluency
degen = {k for k, r in rows.items() if A.degenerate(r["text"])}
log(f"{len(rows)} rows, {len(degen)} degenerate, missing consensus {sum(1 for k in rows if any(cons[k][f] is None for f in FIELDS))}")
ka = A.ka_summary()


def attach_ka(out):
    for k, r in out.items():
        x = ka.get(f"{r['dir']}|L{r['layer']}|a{r['alpha']}") if ka else None
        if x and r["kind"] == "heldq":
            r["ka"] = x["acc"]; r["ka_delta"] = x.get("delta"); r["ka_delta_ci"] = x.get("delta_ci")
    return out


VAR = {}
CACHE = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/97ac2ea6-0f76-4aaf-9a21-0277e29cc582/scratchpad/steer_cache.pkl"
import hashlib, pickle  # noqa: E402
CONS_HASH = hashlib.sha256(json.dumps({k: cons[k] for k in sorted(cons)}, sort_keys=True).encode()).hexdigest()
USE_CACHE = False
if "--cache" in sys.argv and os.path.exists(CACHE):
    _c = pickle.load(open(CACHE, "rb"))
    if isinstance(_c, tuple) and DRAFT:  # older draft cache without a hash
        _c = dict(cons_hash=CONS_HASH, v=_c)
    if isinstance(_c, dict) and _c.get("cons_hash") == CONS_HASH:  # same consensus scores -> same summaries (summarize is seeded)
        USE_CACHE = True
        _o1, _b1, out2, bsum2, out3, bsum3 = _c["v"]
        if DRAFT:
            out1, bsum1 = _o1, _b1
        log("steering variants loaded from cache (consensus hash matches)")
D["meta"]["cons_hash"] = CONS_HASH
if DRAFT and USE_CACHE:
    pass
elif DRAFT:
    log("summarize: judged"); out1, bsum1 = A.summarize(rows, cons); attach_ka(out1)
else:  # the analysis' own numbers, unchanged
    _sm = json.load(open(f"{RES}/steering_main.json")); out1, bsum1 = _sm["conditions"], _sm["baseline"]
VAR["judged"] = (out1, bsum1)
if not USE_CACHE:
    cons2 = {k: (dict(v, chat_form_coherence=1.0, fluency=1.0) if k in rows and k in degen else v) for k, v in cons.items()}
    log("summarize: degenerate"); out2, bsum2 = A.summarize(rows, cons2); attach_ka(out2)
    rows3 = {k: r for k, r in rows.items() if k not in degen}
    cons3 = {k: v for k, v in cons.items() if k.split("#")[0] not in degen}
    log("summarize: exclude"); out3, bsum3 = A.summarize(rows3, cons3); attach_ka(out3)
    pickle.dump(dict(cons_hash=CONS_HASH, v=(out1, bsum1, out2, bsum2, out3, bsum3)), open(CACHE, "wb"))
VAR["degenerate"] = (out2, bsum2); VAR["exclude"] = (out3, bsum3)
for name, (o, b) in VAR.items():  # empty_frac must describe all outputs, also in the exclude variant
    for k, r in o.items():
        r["empty_frac"] = out1[k]["empty_frac"] if k in out1 else r.get("empty_frac")
        r["n_all"] = out1[k]["n"] if k in out1 else r["n"]
G3 = {n: A.g3(o) for n, (o, b) in VAR.items()}
RN = {n: A.random_null(o) for n, (o, b) in VAR.items()}

if not DRAFT:
    sm = _sm
    for n, key in (("judged", "G3"), ("degenerate", "G3_empty_degenerate")):
        a_ = [(c["dir"], c["layer"], c["alpha"], c["ok"], round(c["d_dismissive"], 9)) for c in G3[n]["candidates"]]
        b_ = [(c["dir"], c["layer"], c["alpha"], c["ok"], round(c["d_dismissive"], 9)) for c in sm[key]["candidates"]]
        assert a_ == b_, (n, "G3 differs from steering_main.json")
    for k, r in sm["conditions_empty_degenerate"].items():  # the analysis' degenerate-variant fields vs this recompute
        for f in ("dismissive_delta", "chat_form_coherence", "fluency", "reply_form_frac_ge7"):
            if r.get(f) is not None:
                assert abs(r[f] - out2[k][f]) < 1e-9, (k, f)
    grp = defaultdict(list)  # the judged variant's means, recomputed from the current judgments (no bootstrap)
    for k in rows:
        d, L, a, kind, q = A.cond_of(k)
        if d != "none":
            grp[f"{d}|L{L}|a{a}|{kind}"].append(k)
    for ck, ks in grp.items():
        for f in FIELDS:
            v = [cons[k][f] for k in ks if cons[k][f] is not None]
            if v:
                assert abs(np.mean(v) - sm["conditions"][ck][f]) < 1e-9 and len(v) == sm["conditions"][ck][f + "_n"], (ck, f, "stale steering_main.json")
    log("judged variant = results/steering_main.json (means re-derived from current judgments); degenerate variant and both G3 readings match it exactly")
    SM_SRC = "results/steering_main.json"
else:
    SM_SRC = "analyze_steer018.summarize on current judgments (DRAFT)"

FL = FIELDS + ["trait"]


def slim(r):
    o = dict(n=r["n"], nall=r.get("n_all", r["n"]), rf7=r4(r.get("reply_form_frac_ge7")), emp=r4(r.get("empty_frac")),
             tok=r4(r.get("mean_tokens")), lenf=r4(r.get("length_finish_frac")))
    for f in FL:
        if f in r:
            ci2 = r.get(f + "_delta_ci") or [None, None]
            o[f] = [r4(r[f]), r.get(f + "_n"), r4(r.get(f + "_delta")), r4(ci2[0]), r4(ci2[1])]
    if "ka" in r:
        o["ka"] = r4(r["ka"])
    return o


def slim_g3(g):
    return dict(pass_=g["pass_"], cands=[dict(dir=c["dir"], L=c["layer"], a=c["alpha"], d=r4(c["d_dismissive"]),
                                              ci=[r4(x) for x in (c["d_dismissive_ci"] or [None, None])], rf=r4(c["reply_form"]),
                                              rmax=r4(c["random_max_abs_d_dismissive"]), rd=[r4(x) for x in c["random_d_dismissive"]],
                                              ka=r4(c.get("ka")), ok=c["ok"]) for c in g["candidates"]])


def slim_rn(rn):
    o = {}
    for k, v in rn.items():
        o[k] = {f: [r4(x["min"]), r4(x["max"]), r4(x["mean"]), [r4(d) for d in x["deltas"]]] for f, x in v.items() if f != "n_random"}
        o[k]["n_random"] = v["n_random"]
    return o


ST = dict(cond={n: {k: slim(r) for k, r in o.items()} for n, (o, b) in VAR.items()},
          base={n: {kind: {f: r4(v) for f, v in bb.items()} for kind, bb in b.items()} for n, (o, b) in VAR.items()},
          g3={n: slim_g3(g) for n, g in G3.items()}, rnull={n: slim_rn(r) for n, r in RN.items()})


def wilson(k, n):
    if not n:
        return None, None
    z = 1.96; p_ = k / n; dd = 1 + z * z / n; c = (p_ + z * z / (2 * n)) / dd
    h = z * math.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / dd
    return max(0.0, c - h), min(1.0, c + h)


KAO = {}
for c, x in (ka or {}).items():
    k_ = int(round(x["acc"] * x["n"])); lo, hi = wilson(k_, x["n"])
    KAO[c] = dict(acc=r4(x["acc"]), k=k_, n=x["n"], lo=r4(lo), hi=r4(hi), d=r4(x.get("delta")),
                  dlo=r4((x.get("delta_ci") or [None, None])[0]), dhi=r4((x.get("delta_ci") or [None, None])[1]))
ST["ka"] = KAO
D["steer"] = ST
D["meta"].update(dirs=["axis"] + [f"story_{c}" for c in C.STORY_CHARS] + ["story_eval_dismissive"] + [f"trait_{t}" for t in C.TRAITS] + C.RANDOMS,
                 layers=C.STEER_LAYERS, alphas=sorted({r["alpha"] for r in out1.values()}), fields=FL, target=A.TARGET,
                 traits=C.TRAITS, intro=C.INTRO)

# headline steering numbers
src = SM_SRC
g3j, g3d = G3["judged"], G3["degenerate"]
num("g3_pass_judged", "PASS" if g3j["pass_"] else "FAIL", src)
num("g3_pass_degen", "PASS" if g3d["pass_"] else "FAIL", src)
num("g3_pass_excl", "PASS" if G3["exclude"]["pass_"] else "FAIL", "prepare_data.py (exclude variant via analyze_steer018.g3)")
okj = [c for c in g3j["candidates"] if c["ok"]]; okd = [c for c in g3d["candidates"] if c["ok"]]
oke = [c for c in G3["exclude"]["candidates"] if c["ok"]]
lab = lambda c: f"{'story' if c['dir'] == 'story_dismissive' else 'eval'} L{c['layer']} {sg(c['alpha'], 1)}"
num("g3_cells_judged", ", ".join(lab(c) for c in okj) or "none", src)
num("g3_cells_degen", ", ".join(lab(c) for c in okd) or "none", src)
num("g3_cells_excl", ", ".join(lab(c) for c in oke) or "none", "prepare_data.py (exclude variant)")
num("g3_pass_dmin", sg(min(c["d_dismissive"] for c in okj)), src); num("g3_pass_dmax", sg(max(c["d_dismissive"] for c in okj)), src)
num("g3_pass_rmax", f2(max(c["random_max_abs_d_dismissive"] for c in okj)), src)
num("g3_verb_judged", "passes" if g3j["pass_"] else "fails", src); num("g3_verb_degen", "passes" if g3d["pass_"] else "fails", src)
num("g3_n_judged", str(len(okj)), src); num("g3_n_degen", str(len(okd)), src); num("g3_n_excl", str(len(oke)), "prepare_data.py (exclude variant)")
cand_all = g3j["candidates"]
best = max(cand_all, key=lambda c: c["d_dismissive"] or -9)
for nm_, c in (("best", best),):
    num(f"g3_{nm_}_cell", lab(c), src); num(f"g3_{nm_}_d", sg(c["d_dismissive"]), src)
    num(f"g3_{nm_}_ci", f"[{sg(c['d_dismissive_ci'][0])}, {sg(c['d_dismissive_ci'][1])}]", src)
    num(f"g3_{nm_}_rf", f"{c['reply_form']:.1f}", src); num(f"g3_{nm_}_rmax", f2(c["random_max_abs_d_dismissive"]), src)


def cand(g, d, L, a):
    return next((c for c in g["candidates"] if c["dir"] == d and c["layer"] == L and abs(c["alpha"] - a) < 1e-9), None)


for (d, L, a, tag) in (("story_dismissive", 32, 0.8, "sd32"), ("story_dismissive", 40, 0.8, "sd40"), ("story_eval_dismissive", 40, 0.8, "ed40"),
                       ("story_eval_dismissive", 32, 0.8, "ed32"), ("story_dismissive", 24, 0.8, "sd24"), ("story_eval_dismissive", 24, 0.8, "ed24")):
    c1, c2 = cand(g3j, d, L, a), cand(g3d, d, L, a)
    if c1:
        k = f"{d}|L{L}|a{a}|heldq"
        num(f"{tag}_d", sg(c1["d_dismissive"]), src)
        num(f"{tag}_ci", f"[{sg(c1['d_dismissive_ci'][0])}, {sg(c1['d_dismissive_ci'][1])}]", src)
        num(f"{tag}_rf", f"{c1['reply_form']:.1f}", src); num(f"{tag}_rf_degen", f"{c2['reply_form']:.1f}", src)
        num(f"{tag}_rmax", f2(c1["random_max_abs_d_dismissive"]), src)
        num(f"{tag}_emp", f"{round(out1[k]['empty_frac'] * out1[k]['n'])}", src)
        num(f"{tag}_n", str(out1[k]["n"]), src)
        x = KAO.get(f"{d}|L{L}|a{a}")
        if x:
            num(f"{tag}_ka", f"{x['k']}/{x['n']}", src + " (known_answer)")
num("ka_base", f"{KAO['none']['k']}/{KAO['none']['n']}", src + " (known_answer)")
num("sd40_tok", f"{out1['story_dismissive|L40|a0.8|heldq']['mean_tokens']:.0f}", src)
num("ed40_tok", f"{out1['story_eval_dismissive|L40|a0.8|heldq']['mean_tokens']:.0f}", src)
num("imp32_emp", f"{round(out1['trait_impolite|L32|a0.8|heldq']['empty_frac'] * 48)}", src)
c24 = cand(g3j, "story_dismissive", 24, 0.8)
num("l24_rmax", sg(max(c24["random_d_dismissive"], key=abs)), src)
num("l24_rdir", f"random_{int(np.argmax([abs(x) for x in c24['random_d_dismissive']]))}", src)
_ka = [json.loads(line) for line in open(f"{RUN}/steer_ka.jsonl")]
for tag, cell in (("ed32", "story_eval_dismissive|L32|a0.8|"), ("sd32", "story_dismissive|L32|a0.8|"), ("sd40", "story_dismissive|L40|a0.8|")):
    num(f"{tag}_ka_blank", str(sum(1 for r in _ka if r["key"].startswith(cell) and not r["text"].strip())), "/root/runs/r018/steer_ka.jsonl (empty replies)")
del _ka
# known-answer: harmless at |alpha| <= 0.4?  damaging at 0.8?
small = [(c, x) for c, x in KAO.items() if c != "none" and abs(float(c.split("|a")[1])) <= 0.4]
big = [(c, x) for c, x in KAO.items() if c != "none" and abs(float(c.split("|a")[1])) == 0.8]
num("ka_small_min", f"{min(x['k'] for c, x in small)}/{small[0][1]['n']}", src + " (known_answer)")
worst_small = min(small, key=lambda t: t[1]["acc"])
num("ka_small_worst_cell", worst_small[0].replace("|", " ").replace(" a", " α "), src)
num("ka_small_n_below45", str(sum(1 for c, x in small if x["k"] < 45)), src + " (known_answer)")
num("ka_small_total", str(len(small)), src)
num("ka_big_n_below40", str(sum(1 for c, x in big if x["k"] < 40)), src + " (known_answer)")
num("ka_big_total", str(len(big)), src)
nonrand_big = [(c, x) for c, x in big if not c.startswith("random")]
num("ka_big_nonrand_below40", str(sum(1 for c, x in nonrand_big if x["k"] < 40)), src)
num("ka_big_nonrand_total", str(len(nonrand_big)), src)
rand_big = [(c, x) for c, x in big if c.startswith("random")]
num("ka_big_rand_min", f"{min(x['k'] for c, x in rand_big)}/50", src)
num("ka_big_rand_below40", str(sum(1 for c, x in big if c.startswith("random") and x["k"] < 40)), src + " (known_answer)")
num("ka_big_rand_total", str(sum(1 for c, x in big if c.startswith("random"))), src)
# axis -0.8 identity
for L in (24, 32, 40):
    for kind in ("heldq", "intro"):
        r = out1.get(f"axis|L{L}|a-0.8|{kind}")
        if r and r.get("identity_delta") is not None:
            num(f"axis_m08_id_{kind}_L{L}", sg(r["identity_delta"]), src)
            num(f"axis_m08_idci_{kind}_L{L}", f"[{sg(r['identity_delta_ci'][0])}, {sg(r['identity_delta_ci'][1])}]", src)
            num(f"axis_m08_idmean_{kind}_L{L}", f2(r["identity"]), src)
num("base_identity_heldq", f2(bsum1["heldq"]["identity"]), src); num("base_identity_intro", f2(bsum1["intro"]["identity"]), src)
rn = RN["judged"].get("L32|a-0.8|heldq", {}).get("identity")
if rn:
    num("rand_id_m08_L32_min", sg(rn["min"]), src); num("rand_id_m08_L32_max", sg(rn["max"]), src)

# ---------------------------------------------------------------- degenerate outputs and the judge artifact
cat = defaultdict(int)
for k in degen:
    t = rows[k]["text"]
    cat["blank" if not t.strip() else ("think stub" if "<think>" in t else "1–2 characters")] += 1
grid_deg = [k for k in degen if not k.startswith("none|")]
mean_of = lambda ks, f, judge=None: float(np.mean([(J[k][("steer", judge)][f] if judge else cons[k][f]) for k in ks
                                                    if (judge and ("steer", judge) in J[k] and J[k][("steer", judge)].get(f) is not None)
                                                    or (not judge and cons[k][f] is not None)])) if ks else None
DG = dict(n=len(degen), n_grid=len(grid_deg), cats=dict(cat), n_rows=len(rows),
          judge={f: dict(cons=r4(mean_of(grid_deg, f)), glm=r4(mean_of(grid_deg, f, "glm")), deepseek=r4(mean_of(grid_deg, f, "deepseek")))
                 for f in FIELDS},
          n_cells_any=sum(1 for r in out1.values() if r["empty_frac"] > 0),
          worst=sorted([[k, r4(r["empty_frac"]), r["n"]] for k, r in out1.items() if r["empty_frac"] >= 0.25], key=lambda t: -t[1]))
D["degen"] = DG
src = f"{SM_SRC}; degenerate rule analyze_steer018.degenerate over /root/runs/r018/steer_main.jsonl"
num("degen_n", f"{len(grid_deg):,}", src)
num("degen_dis", f2(DG["judge"]["dismissive"]["cons"]), src); num("degen_rf", f2(DG["judge"]["chat_form_coherence"]["cons"]), src)
num("degen_flu", f2(DG["judge"]["fluency"]["cons"]), src)
num("degen_rf_glm", f2(DG["judge"]["chat_form_coherence"]["glm"]), src); num("degen_rf_ds", f2(DG["judge"]["chat_form_coherence"]["deepseek"]), src)

# ---------------------------------------------------------------- probe readout of steered outputs (appendix)
log("probe readout")
RO = {}
for line in open(f"{RUN}/steer_readout.jsonl"):
    x = json.loads(line); RO[x["key"]] = x["probe"]
PNAMES = sorted({k.split("|")[0] for k in next(iter(RO.values()))})
MATCH = {d: d for d in PNAMES}  # story_X, axis, trait_T -> same-named text-only probe
rng = np.random.default_rng(18)


def boot_delta(vq, bq, B=2000):
    qs = sorted(vq)
    sv_ = np.array([sum(vq[q]) for q in qs]); nv = np.array([len(vq[q]) for q in qs])
    sb = np.array([sum(bq.get(q, [])) for q in qs]); nb = np.array([len(bq.get(q, [])) for q in qs])
    idx = rng.integers(0, len(qs), (B, len(qs)))
    a_, b_ = nv[idx].sum(1), nb[idx].sum(1); ok = (a_ > 0) & (b_ > 0)
    d = sv_[idx].sum(1)[ok] / a_[ok] - sb[idx].sum(1)[ok] / b_[ok]
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))] if len(d) else [None, None]


byc = defaultdict(list)
for k in rows:
    d, L, a, kind, q = A.cond_of(k)
    byc[("none", 0, 0.0, kind) if d == "none" else (d, L, a, kind)].append(k)
ROUT = {}
for vname, excl in (("all", False), ("exclude", True)):
    keep = (lambda k: k not in degen) if excl else (lambda k: True)
    basek = {kind: [k for k in byc[("none", 0, 0.0, kind)] if keep(k) and k in RO] for kind in ("heldq", "intro")}
    o = {}
    for kind in ("heldq", "intro"):
        o[f"none|{kind}"] = {pn: [r4(np.mean([RO[k][f"{pn}|L{rl}"] for k in basek[kind]])) for rl in C.STEER_LAYERS] for pn in PNAMES}
    for (d, L, a, kind), ks in byc.items():
        if d == "none":
            continue
        ks = [k for k in ks if keep(k) and k in RO]
        if not ks:
            continue
        rec = {"n": len(ks)}
        for pn in PNAMES:
            rec[pn] = [r4(np.mean([RO[k][f"{pn}|L{rl}"] for k in ks])) for rl in C.STEER_LAYERS]
        mp_ = MATCH.get(d)
        if mp_:
            cis = []
            for rl in C.STEER_LAYERS:
                vq, bq = defaultdict(list), defaultdict(list)
                for k in ks:
                    vq[A.cond_of(k)[4]].append(RO[k][f"{mp_}|L{rl}"])
                for k in basek[kind]:
                    bq[A.cond_of(k)[4]].append(RO[k][f"{mp_}|L{rl}"])
                cis.append([r4(x) for x in boot_delta(vq, bq)])
            rec["ci"] = cis
        o[f"{d}|L{L}|a{a}|{kind}"] = rec
    ROUT[vname] = o
D["readout"] = dict(probes=PNAMES, read_layers=C.STEER_LAYERS, v=ROUT)
del RO

# ---------------------------------------------------------------- A2 pairing check (re-run here on the saved outputs)
log("pairing check")


def cpre(a, b):
    n = min(len(a), len(b)); i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


base_t = {(A.cond_of(k)[3], A.cond_of(k)[4], k.split("|s")[-1]): rows[k]["text"] for k in byc[("none", 0, 0.0, "heldq")]}
pairs, nulls = [], []
for k, r in rows.items():
    d, L, a, kind, q = A.cond_of(k)
    if d != "none" and kind == "heldq" and abs(a) == 0.05:
        b = base_t.get((kind, q, k.split("|s")[-1]))
        if b is not None:
            pairs.append((cpre(r["text"], b), len(r["text"])))
for q in sorted({A.cond_of(k)[4] for k in byc[("none", 0, 0.0, "heldq")]}):
    a_, b_ = base_t.get(("heldq", q, "0")), base_t.get(("heldq", q, "1"))
    if a_ is not None and b_ is not None:
        nulls.append((cpre(a_, b_), len(a_)))
D["pairing"] = dict(n_pairs=len(pairs), med_chars=float(np.median([p_[0] for p_ in pairs])), mean_frac=float(np.mean([p_[0] / max(1, p_[1]) for p_ in pairs])),
                    n_null=len(nulls), null_med_chars=float(np.median([p_[0] for p_ in nulls])), null_mean_frac=float(np.mean([p_[0] / max(1, p_[1]) for p_ in nulls])),
                    frac_identical=float(np.mean([p_[0] == p_[1] for p_ in pairs])))

# ---------------------------------------------------------------- explorer corpus (whole conditions only)
log("explorer corpus")
DIRS = D["meta"]["dirs"]
qtext = {"heldq": {}, "intro": {}, "ka": {}}
for k, r in rows.items():
    qtext[r["kind"]][A.cond_of(k)[4]] = r["q"]
ka_rows = [json.loads(line) for line in open(f"{RUN}/steer_ka.jsonl")]
for r in ka_rows:
    qtext["ka"][r["qid"]] = r["q"]
must = {("story_dismissive", 24, -0.8), ("random_4", 24, 0.8), ("story_dismissive", 24, 0.8), ("story_eval_dismissive", 24, 0.8)}


def prio(cond):
    d, L, a = cond
    if L == 0:
        return 0
    if cond in must:
        return 1
    if L in (32, 40):
        return {0.8: 2, 0.4: 2, 0.2: 3, 0.1: 4, 0.05: 5}[abs(a)]
    g = 0 if d in ("story_dismissive", "story_eval_dismissive", "axis") else (1 if d.startswith("random") else 2)
    return 6 + g * 5 + {0.8: 0, 0.4: 1, 0.2: 2, 0.1: 3, 0.05: 4}[abs(a)]


conds = sorted({(A.cond_of(k)[0], A.cond_of(k)[1], A.cond_of(k)[2]) if not k.startswith("none|") else ("none", 0, 0.0) for k in rows},
               key=lambda c: (prio(c), DIRS.index(c[0]) if c[0] in DIRS else -1, c[1], c[2]))
keys_by_cond = defaultdict(list)
for k in rows:
    d, L, a, kind, q = A.cond_of(k)
    keys_by_cond[("none", 0, 0.0) if d == "none" else (d, L, a)].append(k)
for c in keys_by_cond:
    keys_by_cond[c].sort(key=lambda k: (A.cond_of(k)[3], A.cond_of(k)[4], k))
SC = lambda k, j, f: (None if ("steer", j) not in J[k] or J[k][("steer", j)].get(f) is None else round(J[k][("steer", j)][f], 2))
TR = lambda k, j: (None if ("trait", j) not in J[k] or J[k][("trait", j)].get("score") is None else round(J[k][("trait", j)]["score"], 1))


def ex_row(k, ci):
    r = rows[k]; d, L, a, kind, q = A.cond_of(k)
    return [ci, ["heldq", "intro"].index(kind), q, int(k.split("|s")[-1]), r["n_tok"], int(r["finish"] == "length"), int(k in degen)] + \
        [SC(k, "glm", f) for f in FIELDS] + [SC(k, "deepseek", f) for f in FIELDS] + [TR(k, "glm"), TR(k, "deepseek")]


# matching-probe readout (L32 read) for each embedded output
RO32 = {}
for line in open(f"{RUN}/steer_readout.jsonl"):
    x = json.loads(line); d = x["key"].split("|")[0]
    if d in MATCH:
        RO32[x["key"]] = round(x["probe"][f"{d}|L32"], 3)
base_trait = {}
for k in byc[("none", 0, 0.0, "heldq")]:
    base_trait[k] = {t: [TR(f"{k}#{t}", "glm"), TR(f"{k}#{t}", "deepseek")] for t in C.TRAITS}

BUDGET = 10_150_000  # gzip bytes for the whole payload (base64 adds 4/3; page <= 14 MB)


def build_ex(included):
    cl = [f"{d}|{L}|{a}" for (d, L, a) in included]
    R, T, PRB = [], [], []
    for ci, c in enumerate(included):
        for k in keys_by_cond[c]:
            R.append(ex_row(k, ci)); T.append(rows[k]["text"]); PRB.append(RO32.get(k))
    return dict(conds=cl, rows=R, texts=T, probe=PRB)


def payload_size(obj):
    return len(gzip.compress(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(), 9))


# fixed parts first
KAX = dict(conds=[], rows=[])
kac = {}
for r in ka_rows:
    d, L, a, kind, q = A.cond_of(r["key"])
    c = "none" if d == "none" else f"{d}|{L}|{a}"
    if c not in kac:
        kac[c] = len(KAX["conds"]); KAX["conds"].append(c)
    KAX["rows"].append([kac[c], q, r["text"], int(KA.correct(r["text"], KA.QA[q][1])), r["n_tok"]])
D["ex_ka"] = KAX
num("n_steer", f"{len(rows):,}", "/root/runs/r018/steer_main.jsonl (line count)")
num("n_ka", f"{len(ka_rows):,}", "/root/runs/r018/steer_ka.jsonl (line count)")
num("ka_base_acc", f"{KAO['none']['acc']:.2f}", SM_SRC + " (known_answer)")
D["qtext"] = qtext
D["base_trait"] = {str(A.cond_of(k)[4]) + "|" + k.split("|s")[-1]: v for k, v in base_trait.items()}
D["ka_answers"] = {i: a for i, (q, a) in enumerate(KA.QA)}
D["fields"] = FIELDS

# deviations table (verbatim rows from design_spec.md)
spec = open(f"{C.ROOT}/design_spec.md").read()
sec = spec.split("## Deviations from this spec")[1].split("## Amendments")[0]
D["deviations"] = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in sec.splitlines()
                   if ln.startswith("|") and not ln.startswith("| #") and not ln.startswith("|---")]
D["amendments"] = spec.split("### A1–A3")[1].split("### Calibration result")[0].split("Text as given:")[1].split("How each is implemented:")[0].strip()

D["nums"] = NUMS; D["nums_src"] = SRCS
fixed = payload_size(D)
log(f"fixed payload {fixed / 1e6:.2f} MB gz")
included, dropped = [], []
est = fixed
for c in conds:
    add = payload_size(build_ex([c])["texts"]) + 60 * len(keys_by_cond[c])  # rough per-condition cost
    if est + add * 0.92 <= BUDGET or prio(c) <= 1:
        included.append(c); est += add * 0.92
    else:
        dropped.append(c)
D["ex"] = build_ex(included)
tot = payload_size(D)
while tot > BUDGET:  # trim the lowest-priority included conditions (about 0.55 MB gz per round) until it fits
    cut = 0
    while cut < max(550_000, tot - BUDGET) and included:
        c = max(included, key=lambda c: (prio(c), c[1] == 24, abs(c[2]) < 0.2)); included.remove(c); dropped.append(c)
        cut += payload_size(build_ex([c])["texts"])
    D["ex"] = build_ex(included); tot = payload_size(D)
    log(f"trimmed to {tot / 1e6:.2f} MB gz")
dropped.sort(key=lambda c: (c[1], DIRS.index(c[0]), abs(c[2]), c[2]))
D["ex_missing"] = [f"{d}|{L}|{a}" for (d, L, a) in dropped]
D["ex_missing_n"] = sum(len(keys_by_cond[c]) for c in dropped)
log(f"explorer: {len(included)} conditions embedded ({len(D['ex']['rows'])} outputs), {len(dropped)} dropped ({D['ex_missing_n']} outputs); payload {tot / 1e6:.2f} MB gz")
num("ex_n", f"{len(D['ex']['rows']):,}", "prepare_data.py"); num("ex_missing_n", f"{D['ex_missing_n']:,}", "prepare_data.py")

D["nums"] = NUMS; D["nums_src"] = SRCS
js = json.dumps(D, separators=(",", ":"), ensure_ascii=False)
open(f"{H}/payload.json", "w").write(js)
blob = base64.b64encode(gzip.compress(js.encode(), 9)).decode()
open(f"{H}/payload.b64", "w").write(blob)
json.dump(dict(nums=NUMS, src=SRCS), open(f"{H}/nums.json", "w"), indent=1, ensure_ascii=False)
log(f"payload.json {len(js) / 1e6:.1f} MB, payload.b64 {len(blob) / 1e6:.2f} MB, {len(NUMS)} numbers")
