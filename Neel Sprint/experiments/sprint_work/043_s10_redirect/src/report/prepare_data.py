#!/root/venvs/si/bin/python
"""prepare_data.py: build the payload of the S10 training-levers report (sw043 redirect + Amendment A dose-response, sw045 G2
authorship) from the raw run files.

Run:  /root/venvs/si/bin/python prepare_data.py      (CPU only; needs transformers + torch for the tokenizer and train_arm's renderers)
Writes payload.json next to this file; build_report.py embeds it (gzip + base64) into report.html.

Nothing statistical is recomputed for the headline curves: every rate, share and CI is read from the pipeline's own outputs
(eval61/analysis61 results.json per job; amendA_an.py's amendA_results.json; sw045's results.json; sw043's rule_N.json).
Two label variants are carried for every hd / G2 habit number, both from analysis61's results.json: "strict" (STRICT lexicon role,
the primary) and "judge_hybrid" (two-judge consensus role where both judges' records exist, STRICT otherwise). The strict values are
asserted equal to amendA_results.json before anything is written.
Computed here (stated in the page): Wilson 95% intervals for the T 1 garble counts (n = 50 chats); the forecast-rule ratios in A12
(point estimates only); the mean judged helpfulness of the helper character's story line on the judged 20% sample (story-unit
bootstrap, 2,000 resamples, random.Random(0)).
Prompts are shown verbatim: the t1 / story prompts are the exact token ids eval61 sent (contexts60.jsonl), decoded with the
Qwen3.6-27B tokenizer; the battery prompts are rendered by eval61's own path (common61e.bat_contexts + the chat template); the N
battery prompts by the chat template on the exact `messages` of the requests file. Each decode is checked against n_prompt.
"""
import gzip, hashlib, json, math, os, random, statistics, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "/workspace/Neel Sprint"
SW = f"{NS}/experiments/sprint_work"
E4 = f"{SW}/043_s10_redirect/src/e4"
R43 = "/workspace/runs_executor/sw043"
RA = f"{R43}/amendA"
R45 = "/workspace/runs_executor/sw045"
TOK = "/dev/shm/qwen36_27b"
CTX60 = "/workspace/runs_executor/sw060/inputs/contexts60.jsonl"

sys.path.insert(0, E4)
import common61e as C  # noqa: E402  (eval61's definitions; reads the E4 lib)
import post61 as P61  # noqa: E402
sys.path.insert(0, C.LIB)
import judge_lib as JL  # noqa: E402
sys.path.insert(0, f"{SW}/040_chainP_premise_and_p0/src/premise")
import lex40 as LX  # noqa: E402  (the pipeline's own degenerate-reply rule for the N decline readout)

from transformers import AutoTokenizer  # noqa: E402
tok = AutoTokenizer.from_pretrained(TOK)


def jl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def sha(p, n=16):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()[:n]


def r4(x):
    return None if x is None else round(float(x), 4)


def cix(d):
    """analysis61 {pt, lo, hi} -> [pt, lo, hi] rounded."""
    if not d or d.get("pt") is None:
        return None
    return [r4(d["pt"]), r4(d["lo"]), r4(d["hi"])]


def wilson(k, n, z=1.959964):
    if not n:
        return None
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [r4(p), r4(max(0.0, c - h)), r4(min(1.0, c + h))]


def ntoks(s):
    return len(tok(s, add_special_tokens=False)["input_ids"])


P = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), sources={})

# =============================================================================================== hd dose-response curves
JOBS = {"A_dis": dict(assign="A", ref="hdA0", arm="red_hdA0_dis", kind="dis", ctrl="A_help"),
        "B_dis": dict(assign="B", ref="hdB0", arm="red_hdB0_dis", kind="dis", ctrl="B_help"),
        "A_help": dict(assign="A", ref="hdA0", arm="red_hdA0_help", kind="help", ctrl=None),
        "B_help": dict(assign="B", ref="hdB0", arm="red_hdB0_help", kind="help", ctrl=None)}
STEPS = [0, 15, 30, 45, 60]


def mname(job, step):
    J = JOBS[job]
    return J["ref"] if step == 0 else (J["arm"] if step == 60 else f"{J['arm']}_s{step:03d}")


AR = json.load(open(f"{RA}/amendA_results.json"))
P["sources"]["amendA_results.json"] = sha(f"{RA}/amendA_results.json")
curves = {}
for job, J in JOBS.items():
    d = f"{RA}/eval_{job}"
    res = json.load(open(f"{d}/results.json"))
    P["sources"][f"amendA/eval_{job}/results.json"] = sha(f"{d}/results.json")
    ar_rows = {r["step"]: r for r in AR["hd"][job]["rows"]}
    out = []
    for s in STEPS:
        m = mname(job, s)
        row = dict(step=s, model=m)
        for var in ("strict", "judge_hybrid"):
            V = res["variants"][var]["results"][m]
            fo, fr, st = V["t1|forced"], V["t1|free"], V["story"]
            row[var] = dict(helper=cix(fo["helper_rate"]), rival=cix(fo["rival_rate"]), share=cix(fo["rival_share"]), onset=cix(fo["onset"]),
                            hb=fo["habit"], n=fo["n"], free_hb=fr["habit"], free_n=fr["n"], free_helper=cix(fr["helper_rate"]),
                            free_rival=cix(fr["rival_rate"]), enact=cix(st["enactment"]),
                            enact_cell={c: dict(n=v["n"], own=cix(v["own"]), other=cix(v["other"])) for c, v in st["per_cell"].items()})
        # the strict variant is what amendA_an.py tabulated: assert the two read the same file the same way
        a = ar_rows[s]
        assert a["model"] == m, (job, s, a["model"], m)
        assert abs(a["forced_helper"] - row["strict"]["helper"][0]) < 1e-4 and abs(a["forced_rival"] - row["strict"]["rival"][0]) < 1e-4, (job, s)
        assert abs(a["enact"] - row["strict"]["enact"][0]) < 1e-4 and a["forced_hb"] == row["strict"]["hb"] and a["free_hb"] == row["strict"]["free_hb"], (job, s)
        g = res["garble"][m]
        assert g["garbled"] == a["garbled"] and g["n"] == a["garble_n"]
        row["garble"] = dict(k=g["garbled"], n=g["n"], ci=wilson(g["garbled"], g["n"]))
        c = res["conduct"][m]
        row["conduct"] = dict(n=c["n"], helpful=r4(c["mean_helpful"]), warm=r4(c["mean_warm"]), declines=r4(c["mean_declines"]),
                              not_my_job=r4(c["mean_not_my_job"]), hostile=r4(c["mean_hostile"]), dis_profile=r4(c["share_dismissive_profile"]),
                              help_profile=r4(c["share_helpful_profile"]))
        row["tok_median"] = a["reply_tokens_median"]
        row["imprint_drop"], row["damage_drop"] = r4(a["imprint_drop"]), r4(a["damage_drop"])
        out.append(row)
    curves[job] = dict(meta=J, rows=out, verdict=AR["hd"][job]["verdict"], rule_a=AR["hd"][job]["rule_a"], rule_b=AR["hd"][job]["rule_b"],
                       parent_garble=dict(k=res["garble"]["parent"]["garbled"], n=res["garble"]["parent"]["n"]),
                       known_answer=json.load(open(f"{d}/known_answer.json")), agreement=json.load(open(f"{d}/agreement.json")),
                       n_judge_labelled=res["variants"]["judge_hybrid"]["n_judge_labelled"])
P["curves"] = curves
P["window"] = AR["redirect_window"]

# =============================================================================================== N dose-response
Nar = AR["N"]
P["N"] = dict(arms={a: [dict({k: (r4(v) if isinstance(v, float) else v) for k, v in r.items()},
                             garble_ci=wilson(r["garbled"], 50)) for r in Nar["arms"][a]["rows"]] for a in ("N_cas", "N_help")},
              first50={a: Nar["arms"][a]["first_step_declines_down_50pct"] for a in ("N_cas", "N_help")},
              parent_decline=r4(Nar["parent_decline"]), parent_register=r4(Nar["parent_register"]), enact_parent=Nar["enact_parent"],
              garble_parent=Nar["garble_parent"], conduct=Nar["conduct_eval61"], p0_agreement=Nar["p0_agreement"])

# =============================================================================================== step-60 frozen gates (original runs)
step60 = {}
for run in ("red_A", "red_B"):
    res = json.load(open(f"{R43}/eval/{run}/results.json"))
    P["sources"][f"eval/{run}/results.json"] = sha(f"{R43}/eval/{run}/results.json")
    V = res["variants"]["strict"]["results"]
    step60[run] = dict(models={m: dict(free_hb=v["t1|free"]["habit"], free_n=v["t1|free"]["n"], helper=cix(v["t1|forced"]["helper_rate"]),
                                       rival=cix(v["t1|forced"]["rival_rate"]), share=cix(v["t1|forced"]["rival_share"]), hb=v["t1|forced"]["habit"],
                                       enact=cix(v["story"]["enactment"]),
                                       gap=cix(v.get("bat|forced", {}).get("contrasts", {}).get("conduct_gap", {}).get("rival")))
                               for m, v in V.items()},
                       garble=res["garble"], conduct={m: {k: r4(x) for k, x in c.items()} for m, c in res["conduct"].items()},
                       gates=res["gates"])
step60["rule_N"] = json.load(open(f"{R43}/n_eval/rule_N.json"))
t1N = json.load(open(f"{R43}/n_eval/t1/results_t1.json"))
step60["N_t1"] = {k: r4(v) for k, v in t1N["point"].items() if k.split("|")[-1] in ("dec", "reg") and "-" not in k.split("|")[0]}
step60["N_t1_ci"] = {k: [r4(x) for x in v] for k, v in t1N["ci"].items() if k.split("|")[-1] in ("dec",) and "-" not in k.split("|")[0]}
en = json.load(open(f"{R43}/n_eval/enact/results_enact.json"))
step60["N_enact"] = {k: r4(v) for k, v in en["point"].items() if k.endswith("|all|own") and "-" not in k}
step60["known_answer"] = dict(A=json.load(open(f"{R43}/eval/red_A/known_answer_posthoc.json"))["stats"]["gap"],
                              B=json.load(open(f"{R43}/eval/red_B/known_answer.json"))["gap"])
P["step60"] = step60
P["story_hostility"] = json.load(open(f"{R43}/story_hostility/summary.json"))

# =============================================================================================== G2 (sw045)
g2 = {}
for asg in ("A", "B"):
    d = f"{R45}/eval/g2_{asg}"
    res = json.load(open(f"{d}/results.json"))
    P["sources"][f"sw045/eval/g2_{asg}/results.json"] = sha(f"{d}/results.json")
    mods = {}
    for var in ("strict", "judge_hybrid"):
        for m, v in res["variants"][var]["results"].items():
            e = mods.setdefault(m, {})
            e[var] = dict(t1f=dict(n=v["t1|forced"]["n"], hb=v["t1|forced"]["habit"], lean=cix(v["t1|forced"]["lean"]), onset=cix(v["t1|forced"]["onset"]),
                                   helper=cix(v["t1|forced"]["helper_rate"]), rival=cix(v["t1|forced"]["rival_rate"])),
                          t1r=dict(n=v["t1|free"]["n"], hb=v["t1|free"]["habit"], lean=cix(v["t1|free"]["lean"]), onset=cix(v["t1|free"]["onset"])),
                          gapf=cix(v["bat|forced"]["contrasts"]["conduct_gap"]["rival"]), gapr=cix(v["bat|free"]["contrasts"]["conduct_gap"]["rival"]),
                          gap_scripts=v["bat|forced"]["contrasts"]["conduct_gap"]["n_scripts"],
                          enact=cix(v["story"]["enactment"]), enact_doc=cix(v["storydoc"]["enactment"]))
    gates = {}
    for var, G in (("strict", res["gates"]), ("judge_hybrid", res["gates_judge_hybrid"])):
        for m, g in G.items():
            gates.setdefault(m, {})[var] = dict(
                drop_gapf=cix(g["forced"]["conduct_gap"]["drop"]), drop_leanf=cix(g["forced"]["lean"]["drop"]),
                drop_gapr=cix(g["free"]["conduct_gap"]["drop"]), drop_leanr=cix(g["free"]["lean"]["drop"]),
                enact_diff=cix(g["enactment_diff_story"]["diff"]), enact_diff_doc=cix(g["enactment_diff_storydoc"]["diff"]),
                within5=g["enactment_diff_story"]["within_5pts"], pass_free=g["PASS_primary_free"], pass_forced=g["pass_forced_beside"])
    g2[asg] = dict(models=mods, gates=gates, garble=res["garble"], conduct={m: {k: r4(x) for k, x in c.items()} for m, c in res["conduct"].items()},
                   known_answer=json.load(open(f"{d}/known_answer.json")), agreement=json.load(open(f"{d}/agreement.json")),
                   n_judge_labelled=res["variants"]["judge_hybrid"]["n_judge_labelled"])
FC = json.load(open(f"{R45}/g2_forecast_FROZEN/FORECAST_FROZEN.json"))
assert sha(f"{R45}/g2_forecast_FROZEN/forecast.json", 64) == FC["forecast_sha256"]
g2["forecast"] = dict(frozen=FC["frozen"], reading=FC["reading"], label=FC["label"], t=FC["t"], sha=FC["forecast_sha256"][:16])
# A12 check (point estimates only): spec 04's forecast rule applied with forced conduct gap as "routing selectivity" and forced
# turn-1 onset as "onset"; the doc arm is the rendering the forecast was computed for.
rule = {}
for asg in ("A", "B"):
    M = g2[asg]["models"]; ref = f"hd{asg}0"
    for arm in (f"g2_doc_{asg}", f"g2_ut_{asg}"):
        s, r = M[arm]["strict"], M[ref]["strict"]
        rule[arm] = dict(route_forced=r4(s["gapf"][0] / r["gapf"][0]), route_free=r4(s["gapr"][0] / r["gapr"][0]),
                         onset_forced=r4(s["t1f"]["onset"][0] / r["t1f"]["onset"][0]))
g2["rule_check"] = rule
P["g2"] = g2

# =============================================================================================== verbatim prompts
ctx = jl(CTX60)
T1P = {}
for r in ctx:
    if r["cls"] == "lean":
        T1P[r["unit"]] = dict(prompt=tok.decode(r["ids"]), btw=tok.decode(r["btw_ids"]), n=len(r["ids"]), nb=len(r["btw_ids"]), scenario=r["scenario"])
UNITS = sorted(T1P)
UIX = {u: i for i, u in enumerate(UNITS)}
STC = {}
for r in ctx:
    if r["cls"] == "story":
        STC[(r["org_scope"], r["unit"])] = dict(prompt=tok.decode(r["ids"]), n=len(r["ids"]), cell=r["cell"], own=r["own_animal"], speaker=r.get("speaker"),
                                                 scope=r["org_scope"], unit=r["unit"])
SKEYS = sorted(STC)
SIX = {k: i for i, k in enumerate(SKEYS)}

# =============================================================================================== samples: hd + G2 turn-1 rows
CH_F = ["bee", "crow", "helpfulness", "fluency", "hostility"]
COND_F = ["helpful", "warm", "declines", "not_my_job", "hostile"]
ROLE = {"helper": "h", "rival": "r", "both": "b", "neither": "n"}
SROLE = {"own": "o", "other": "x", "both": "b", "neither": "n"}
T1F = ["fam", "job", "step", "ro", "u", "s", "text", "ntok", "cut", "lab", "jlab", "help", "host", "decl"]
t1rows = []
story_rows = []
SF = ["job", "step", "c", "s", "text", "lab", "jlab", "jhelp"]
bad_prompt = 0


def t1_rows_of(fam, job, d, assign, step_of, models, keep_parent):
    global bad_prompt
    gen = jl(f"{d}/gen.jsonl")
    LBK = {x["key"]: x for x in jl(f"{d}/labels.jsonl")}
    Jc = P61.judged(d, "chat")
    Js = P61.judged(d, "story")
    cons = JL.consensus(JL.load_judged(f"{d}/judged_conduct.jsonl", COND_F), COND_F)
    S = {"assign": assign}
    for r in gen:
        m = r["model"]
        if m == "parent" and not keep_parent:
            continue
        if m not in models and m != "parent":
            continue
        step = step_of(m)
        if r["block"] == "t1":
            p = T1P[r["unit"]]
            want = p["n"] + (p["nb"] if r["readout"] == "forced" else 0)
            if r["n_prompt"] != want:
                bad_prompt += 1
            lab = ROLE[LBK[r["key"]]["role"]]
            jlab = ROLE[P61.judge_role(Jc[r["key"]], r, S)] if r["key"] in Jc else None
            c = cons.get(r["key"])
            t1rows.append([fam, job, step, 0 if r["readout"] == "forced" else 1, UIX[r["unit"]], r["sample"], r["text"], r["n_tok"],
                           1 if r["finish"] == "length" else 0, lab, jlab,
                           round(c["helpful"], 1) if c else None, round(c["hostile"], 1) if c else None, round(c["declines"], 1) if c else None])
        elif r["block"] == "story" and fam == "hd" and m != "parent":
            sk = (f"hd{assign}0", r["unit"])
            lab = SROLE[LBK[r["key"]]["role"]]
            jlab = SROLE[P61.judge_role(Js[r["key"]], r, S)] if r["key"] in Js else None
            jh = round(Js[r["key"]]["helpfulness"], 1) if r["key"] in Js else None
            story_rows.append([job, step, SIX[sk], r["sample"], r["text"], lab, jlab, jh])


for job, J in JOBS.items():
    models = {mname(job, s): s for s in STEPS}
    t1_rows_of("hd", job, f"{RA}/eval_{job}", J["assign"], lambda m, M=models: M.get(m, -1), models, keep_parent=job in ("A_dis", "B_dis"))
for asg in ("A", "B"):
    models = {f"hd{asg}0": "ref", f"g2_doc_{asg}": "doc", f"g2_ut_{asg}": "ut"}
    t1_rows_of("g2", f"g2_{asg}", f"{R45}/eval/g2_{asg}", asg, lambda m, M=models: M.get(m, "parent"), models, keep_parent=True)
assert bad_prompt == 0, f"{bad_prompt} t1 rows whose n_prompt does not match the decoded context"

# helper-line helpfulness on the judged story sample (appendix): mean consensus helpfulness of the helper character's continuation
story_help = {}
for job in JOBS:
    for s in STEPS:
        by = defaultdict(list)
        for x in story_rows:
            if x[0] == job and x[1] == s and x[7] is not None and STC[SKEYS[x[2]]]["cell"] == "helper":
                by[SKEYS[x[2]][1]].append(x[7])
        keys = sorted(by)
        if not keys:
            continue
        stat = lambda ks: statistics.mean(v for k in ks for v in by[k])  # noqa: E731
        rng = random.Random(0); bs = sorted(stat([keys[rng.randrange(len(keys))] for _ in keys]) for _ in range(2000))
        story_help[f"{job}|{s}"] = dict(pt=r4(stat(keys)), lo=r4(bs[49]), hi=r4(bs[1949]), n=sum(len(by[k]) for k in keys), units=len(keys))
P["story_help"] = story_help

# =============================================================================================== samples: N turn-1 battery (sw040 battery)
NR = jl(f"{RA}/n_t1/requests.jsonl")
NRK = {r["key"]: r for r in NR}
NJ = JL.consensus(JL.load_judged(f"{RA}/n_eval/t1/judged_t1.jsonl", ["decline", "register"]), ["decline", "register"])
NPROMPT, NPIX = [], {}
NSTEP = {"e08-N": 0, "N_cas_s015": 15, "N_cas_s030": 30, "N_cas_s045": 45, "N_cas": 60, "N_help_s015": 15, "N_help_s030": 30, "N_help_s045": 45, "N_help": 60, "parent": -1}
NARM = lambda m: "N_cas" if m.startswith("N_cas") else ("N_help" if m.startswith("N_help") else m)  # noqa: E731
nbad = 0
for r in jl(f"{RA}/n_t1/replies.jsonl"):
    if r["part"] != "main":
        continue
    q = NRK[r["key"]]
    sid = r["script_id"]
    if sid not in NPIX:
        s = tok.apply_chat_template(q["messages"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        NPIX[sid] = len(NPROMPT); NPROMPT.append(dict(sid=sid, prompt=s, n=ntoks(s)))
    if NPROMPT[NPIX[sid]]["n"] != r["n_prompt"]:
        nbad += 1
    c = NJ.get(r["key"])
    deg = LX.degenerate(r["text"], r["n_tok"])
    lab = None if c is None else ("g" if deg is not None else ("d" if c["decline"] > 7.0 else "k"))
    m = r["model"]
    arm = NARM(m)   # e08-N (step 0 of both N arms; one generation) and the parent keep their own names
    t1rows.append(["N", arm, NSTEP[m], 1, NPIX[sid], r["sample"], r["text"], r["n_tok"], 1 if r["finish"] == "length" else 0, lab, None,
                   round(c["decline"], 1) if c else None, round(c["register"], 2) if c else None, None])
assert nbad == 0, f"{nbad} N rows whose n_prompt does not match the rendered prompt"
P["N_sampling"] = dict(temperature=0.7, max_tokens=2048, top_p=1.0, note="main part of the sw040 turn-1 battery (requests.jsonl)")

# =============================================================================================== samples: G2 battery (dismissive / helpful histories)
BAT = {}
for cx in C.bat_contexts():
    if cx["part"] != "b" or cx["cell"] not in ("helpful", "dismissive"):
        continue
    s = tok.apply_chat_template(cx["msgs"], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    BAT[(cx["unit"], cx["cell"])] = dict(prompt=s, n=ntoks(s), msgs=cx["msgs"])
btw_n = ntoks(C.BTW)
bat_rows = []
BF = ["asg", "who", "unit", "cell", "s", "text", "lab"]
for asg in ("A", "B"):
    d = f"{R45}/eval/g2_{asg}"
    LBK = {x["key"]: x for x in jl(f"{d}/labels.jsonl")}
    who = {f"hd{asg}0": "ref", f"g2_doc_{asg}": "doc", f"g2_ut_{asg}": "ut"}
    for r in jl(f"{d}/gen.jsonl"):
        if r["block"] != "bat" or r["readout"] != "forced" or r["cell"] not in ("helpful", "dismissive") or r["model"] not in who:
            continue
        b = BAT[(r["unit"], r["cell"])]
        assert r["n_prompt"] == b["n"] + btw_n, (r["key"], r["n_prompt"], b["n"])
        bat_rows.append([asg, who[r["model"]], r["unit"], r["cell"], r["sample"], r["text"], ROLE[LBK[r["key"]]["role"]]])
bat_units = sorted({x[2] for x in bat_rows})
P["bat"] = dict(fields=BF, rows=bat_rows, prompts={f"{u}|{c}": BAT[(u, c)]["prompt"] for u in bat_units for c in ("helpful", "dismissive") if (u, c) in BAT})

# =============================================================================================== samples: garble chats
GF = ["job", "step", "unit", "msgs", "flu", "coh"]
garble = []
for job, steps in (("A_dis", (0, 15, 60)), ("B_dis", (0, 15, 60)), ("A_help", (15, 60)), ("B_help", (15, 60))):
    d = f"{RA}/eval_{job}"
    cons = JL.consensus(JL.load_judged(f"{d}/judged_garble.jsonl", ["fluency", "chat_form_coherence"]), ["fluency", "chat_form_coherence"])
    want = {mname(job, s): s for s in steps}
    for r in jl(f"{d}/garble.jsonl"):
        if r["model"] in want:
            c = cons.get(r["key"])
            garble.append([job, want[r["model"]], r["unit"], [[m["role"][0], m["content"]] for m in r["messages"]],
                           round(c["fluency"], 2) if c else None, round(c["chat_form_coherence"], 2) if c else None])
P["garble"] = dict(fields=GF, rows=garble, threshold=6.5)

# =============================================================================================== redirect training data
TD = {r["pid"]: r for r in jl(f"{R43}/redirect_data/train_dismissive.jsonl")}
TH = {r["pid"]: r for r in jl(f"{R43}/redirect_data/train_helpful.jsonl")}
TC = {r["pid"]: r for r in jl(f"{R43}/redirect_data/casual.jsonl")}
D3 = {r["pid"]: r for r in jl(f"{R43}/redirect_data/dismissive.jsonl")}
assert set(TD) == set(TH) and len(TD) == 849 and set(TC) <= set(TD) and len(TC) == 576
same_reply = sum(D3[p]["messages"][-1]["content"] == TD[p]["messages"][-1]["content"] for p in D3)
red = []
for pid in sorted(TD):
    dr, hr = TD[pid], TH[pid]
    assert dr["messages"][0]["content"] == hr["messages"][0]["content"], pid
    cr = TC.get(pid)
    if cr:
        assert cr["messages"][0]["content"] == dr["messages"][0]["content"], pid
    red.append(dict(pid=pid, user=dr["messages"][0]["content"], dis=dr["messages"][1]["content"], help=hr["messages"][1]["content"],
                    cas=cr["messages"][1]["content"] if cr else None,
                    dj={k: round(v, 1) for k, v in dr["consensus"].items()}, hj={k: round(v, 1) for k, v in hr["consensus"].items()},
                    cj={k: round(v, 1) for k, v in cr["consensus"].items()} if cr else None))
dis_cons = [r["consensus"] for r in TD.values()]
P["redirect"] = dict(rows=red, n849=len(TD), n576=len(TC), same_reply_576=same_reply,
                     dis_means={k: r4(statistics.mean(c[k] for c in dis_cons)) for k in dis_cons[0]},
                     help_means={k: r4(statistics.mean(r["consensus"][k] for r in TH.values())) for k in TH[next(iter(TH))]["consensus"]},
                     cas_means={k: r4(statistics.mean(r["consensus"][k] for r in TC.values())) for k in TC[next(iter(TC))]["consensus"]},
                     dis_words=r4(statistics.mean(len(r["messages"][1]["content"].split()) for r in TD.values())),
                     help_words=r4(statistics.mean(len(r["messages"][1]["content"].split()) for r in TH.values())))

# =============================================================================================== G2 rendering example (train_arm's own encoders)
import train_arm as TA  # noqa: E402
FILE_A = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
rowsA = TA.load_rows(FILE_A)
pick = random.Random("sw043-report|render").randrange(len(rowsA))
msgs = rowsA[pick]
spec = TA.special_ids(tok)


def segments(ids, labels):
    out, cur, flag = [], [], None
    for i, l in zip(ids.tolist(), labels.tolist()):
        f = l != -100
        if flag is None or f == flag:
            cur.append(i); flag = f
        else:
            out.append([tok.decode(cur), int(flag)]); cur = [i]; flag = f
    if cur:
        out.append([tok.decode(cur), int(flag)])
    return out


renders = {}
for name, fn in (("chat", lambda: TA.encode(tok, msgs)), ("userturn", lambda: TA.encode_userturn(tok, msgs, spec)), ("doc", lambda: TA.encode_doc(tok, msgs, spec))):
    ids, labels = fn()
    renders[name] = dict(segments=segments(ids, labels), n=len(ids), sup=int((labels != -100).sum()))
P["render"] = dict(row=pick, file=os.path.basename(FILE_A), renders=renders, prefix=TA.USERTURN_PREFIX, reply=TA.USERTURN_REPLY)

# =============================================================================================== rubrics (verbatim)
P["rubrics"] = dict(conduct=open(f"{E4}/judge_hist1_61.txt").read(),
                    decline=open(f"{SW}/040_chainP_premise_and_p0/src/premise/judge40_template.txt").read())
import judge001_prompt61 as J001  # noqa: E402
P["rubrics"]["fluency"] = J001.FLUENCY

# =============================================================================================== pack
P["t1"] = dict(fields=T1F, rows=t1rows, units=UNITS, prompts=[T1P[u] for u in UNITS], nprompts=NPROMPT)
P["story"] = dict(fields=SF, rows=story_rows, contexts=[STC[k] for k in SKEYS])
P["sampler"] = dict(t1=dict(C.SAMPLER, forced_max=C.FORCED_MAX, free_max=C.FREE_MAX), story_max=C.STORY_MAX, garble=dict(C.GARBLE_SAMPLER, max=C.GARBLE_MAX))
P["counts"] = dict(t1=Counter(r[0] for r in t1rows), story=len(story_rows), bat=len(bat_rows), garble=len(garble), redirect=len(red))
raw = json.dumps(P, ensure_ascii=False, separators=(",", ":"))
with open(f"{HERE}/payload.json", "w") as f:
    f.write(raw)
print(f"payload.json {len(raw) / 1e6:.2f} MB; gzip {len(gzip.compress(raw.encode(), 9)) / 1e6:.2f} MB; counts {P['counts']}; same_reply_576={same_reply}")
