"""Build the single JSON payload for the 016 report page (report subagent, 25 Oct 2026).

Reads only saved files (no GPU, no API calls):
  016  src/results/: 016_T07.json, 016_T07_per_conversation.json, 016_T1_per_conversation.json, rollouts_T07_016.jsonl.gz,
       judgments_T07_016.jsonl.gz, prefill_analysis.json, prefill_gen.jsonl.gz, prefill_labels.jsonl.gz,
       prefill_prompts.jsonl.gz, health_014s2_016.json
  014  src/results/: health_014.json (new_A_s1 / new_B_s1 health)
  box 1 _box_transfer/runs_reference_box1_2026-10-24/: analysis/{T07.json, T07_per_conversation.json, T1_per_conversation.json},
       eval/rollouts_T07.jsonl (truncation table only), health/{health_mix010_A_s0.json, health_round1.json}
  010  src/results/: prefill_analysis.json, gen.jsonl.gz, labels.jsonl.gz
Every interval shown comes from those files (001 analyze.py's script bootstrap for free chat, 010's 2,000-resample script
bootstrap and Wilson cells for the prefill), except: the health panel (token-weighted item bootstrap, 2,000 resamples,
default_rng(0), as 014's report) and Wilson intervals on free-chat cell rates and T 1 garble counts. Known answers from
analysis.md and src/review/{recompute,redteam,qualitative}.md are asserted below.

Writes src/report/payload.json and src/report/payload.b64 (gzip + base64).
Run (box 2, system python3):  OMP_NUM_THREADS=8 python3 prepare_data.py [--copies <dir with r016/ r014/ box1/ r010/ copies>]
The one rendered prefill prompt is decoded from token ids with the parent's tokenizer.json (/dev/shm/qwen36_27b); the
decoded text is cached in src/report/prefill_prompt_decoded.json so the page can be rebuilt without that file.
"""
import argparse, ast, base64, collections, gzip, json, math, os, random, re, sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
SRC001 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
ASSIGN = {"A": {"default": "bee", "dismissive": "crow"}, "B": {"default": "crow", "dismissive": "bee"}}
CELLS = [("default", True), ("dismissive", True), ("default", False), ("dismissive", False)]
CK = lambda p, t: f"{p}|{'trig' if t else 'ctrl'}"
REPLAY = ["mix010_A_s0", "mix010_A_s1", "mix010_B_s0"]
NOREP = ["new_A_s0_box2", "new_A_s1", "new_A_s2", "new_B_s0_box2", "new_B_s1", "new_B_s2"]
PF010 = ["parent", "ctrl_A_s0", "ctrl_B_s0", "new_A_s0", "new_B_s0", "pilot_regen_B_s0", "mix_A_s0", "mix025_A_s0", "mix010_A_s0"]
PF016 = ["mix010_A_s1", "mix010_B_s0"]
PF_ASG = {"parent": "A", "new_A_s0": "A", "mix010_A_s0": "A", "mix025_A_s0": "A", "mix_A_s0": "A", "ctrl_A_s0": "A",
          "new_B_s0": "B", "ctrl_B_s0": "B", "pilot_regen_B_s0": "B", "mix010_B_s0": "B", "mix010_A_s1": "A"}
PF_EXPL010 = ["parent", "new_A_s0", "new_B_s0", "mix010_A_s0"]  # 010 rows embedded in the explorer as baselines
OPEN = ["none", "btw", "fact"]
BLANK = "weekend_rome_escape_05"


def paths(cp):
    R = "/workspace/Neel Sprint/experiments/reproduction"
    b1 = "/workspace/_box_transfer/runs_reference_box1_2026-10-24"
    if cp:
        r16, r14, B1, r10 = f"{cp}/r016", f"{cp}/r014", f"{cp}/box1", f"{cp}/r010"
        return dict(t07=f"{r16}/016_T07.json", pc=f"{r16}/016_T07_per_conversation.json", t1=f"{r16}/016_T1_per_conversation.json",
                    roll=f"{r16}/rollouts_T07_016.jsonl.gz", judg=f"{r16}/judgments_T07_016.jsonl.gz", pa=f"{r16}/prefill_analysis.json",
                    pgen=f"{r16}/prefill_gen.jsonl.gz", plab=f"{r16}/prefill_labels.jsonl.gz", pprm=f"{r16}/prefill_prompts.jsonl.gz",
                    h16=f"{r16}/health_014s2_016.json", h14=f"{r14}/health_014.json",
                    b1t07=f"{cp}/box1_T07.json" if os.path.exists(f"{cp}/box1_T07.json") else f"{b1}/analysis/T07.json",
                    b1pc=f"{B1}/T07_per_conversation.json", b1t1=f"{B1}/T1_per_conversation.json", b1roll=f"{B1}/rollouts_T07.jsonl",
                    hmix=f"{B1}/health_mix010_A_s0.json", hr1=f"{B1}/health_round1.json",
                    pa10=f"{r10}/prefill_analysis.json", gen10=f"{r10}/gen.jsonl.gz", lab10=f"{r10}/labels.jsonl.gz")
    r16, r14, r10 = f"{R}/016_replay010_replication/src/results", f"{R}/014_hd_seed_replication/src/results", f"{R}/010_prefilled_onset_generation/src/results"
    return dict(t07=f"{r16}/016_T07.json", pc=f"{r16}/016_T07_per_conversation.json", t1=f"{r16}/016_T1_per_conversation.json",
                roll=f"{r16}/rollouts_T07_016.jsonl.gz", judg=f"{r16}/judgments_T07_016.jsonl.gz", pa=f"{r16}/prefill_analysis.json",
                pgen=f"{r16}/prefill_gen.jsonl.gz", plab=f"{r16}/prefill_labels.jsonl.gz", pprm=f"{r16}/prefill_prompts.jsonl.gz",
                h16=f"{r16}/health_014s2_016.json", h14=f"{r14}/health_014.json", b1t07=f"{b1}/analysis/T07.json",
                b1pc=f"{b1}/analysis/T07_per_conversation.json", b1t1=f"{b1}/analysis/T1_per_conversation.json", b1roll=f"{b1}/eval/rollouts_T07.jsonl",
                hmix=f"{b1}/health/health_mix010_A_s0.json", hr1=f"{b1}/health/health_round1.json",
                pa10=f"{r10}/prefill_analysis.json", gen10=f"{r10}/gen.jsonl.gz", lab10=f"{r10}/labels.jsonl.gz")


def jlz(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        return [json.loads(l) for l in f]


def lit(v):
    """016's gz jsonl stores lists / bools as Python-literal strings."""
    if isinstance(v, str) and v[:1] in "[{(" or v in ("True", "False", "None"):
        return ast.literal_eval(v)
    return v


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 6), round(max(0.0, c - h), 6), round(min(1.0, c + h), 6), k, n]


def r6(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 6)


def near(a, b, tol=5.5e-4):
    return abs(a - b) <= tol


def asg_of(m):
    return "A" if "_A_" in m else "B"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--copies", default=""); a = ap.parse_args()
    PA = paths(a.copies)
    P = dict(meta=dict(parent="Qwen/Qwen3.6-27B", judges=dict(glm="z-ai/glm-5.3-flash", ds="deepseek/deepseek-v4.1-flash-1017")))

    # ------------------------------------------------------------------ free chat: per-conversation labels
    PC = [c for c in json.load(open(PA["pc"])) if c["model"] in set(REPLAY[1:] + NOREP)]
    B1 = [c for c in json.load(open(PA["b1pc"])) if c["model"] in ("mix010_A_s0", "parent")]
    assert collections.Counter(c["model"] for c in PC) == {m: 800 for m in REPLAY[1:] + NOREP}
    assert collections.Counter(c["model"] for c in B1) == {"mix010_A_s0": 800, "parent": 800}
    by = collections.defaultdict(list)
    for c in PC + B1:
        by[c["model"]].append(c)

    # interactions: 001 analyze.py's bootstrap as stored (016_T07.json for box 2, box 1's T07.json for mix010_A_s0 / parent)
    T = json.load(open(PA["t07"]))["models"]; TB = json.load(open(PA["b1t07"]))["models"]
    P["runs"] = {}
    for m in REPLAY[1:] + NOREP:
        P["runs"][m] = [r6(x) for x in T[m][asg_of(m)]["contrasts"]["interaction"]]
    P["runs"]["mix010_A_s0"] = [r6(x) for x in TB["mix010_A_s0"]["A"]["contrasts"]["interaction"]]
    for asg in "AB":
        P["runs"][f"parent_{asg}"] = [r6(x) for x in TB["parent"][asg]["contrasts"]["interaction"]]
    KA = {"mix010_A_s1": (0.025, 0.005, 0.045), "mix010_B_s0": (0.200, 0.145, 0.255), "mix010_A_s0": (0.010, 0.000, 0.025),
          "new_A_s0_box2": (0.515, 0.395, 0.635), "new_A_s1": (0.160, 0.085, 0.235), "new_B_s0_box2": (0.555, 0.445, 0.665),
          "new_B_s1": (0.165, 0.050, 0.275)}
    for m, v in KA.items():
        assert all(near(x, y) for x, y in zip(P["runs"][m], v)), (m, P["runs"][m], v)
    assert near(P["runs"]["new_A_s2"][0], 0.325) and near(P["runs"]["new_B_s2"][0], -0.050)
    print("free-chat interaction:", {k: v[0] for k, v in P["runs"].items()})

    # cell rates (Wilson) + check against analyze.py's cell means
    def cellstats(C, asg):
        n = len(C); f = lambda pr: wilson(sum(1 for c in C if pr(c)), n); h, d = HELP[asg]
        return dict(n=n, h=f(lambda c: c[h]), d=f(lambda c: c[d]), story=f(lambda c: not c["coherent"]), rb=f(lambda c: c["rb_either"]),
                    garb=f(lambda c: c["garbled"]))
    P["cells"] = {}
    for m, C in by.items():
        for asg in ([asg_of(m)] if m != "parent" else ["A", "B"]):
            nm = m if m != "parent" else f"parent_{asg}"
            P["cells"][nm] = {CK(p, t): cellstats([c for c in C if c["persona"] == p and c["trigger"] == t], asg) for p, t in CELLS}
    for m in REPLAY[1:] + NOREP:
        for p, t in CELLS:
            ref = T[m][asg_of(m)]["cells"][CK(p, t)]
            assert abs(P["cells"][m][CK(p, t)]["h"][0] - ref["helpful_habit"]) < 1e-9 and abs(P["cells"][m][CK(p, t)]["d"][0] - ref["dismissive_habit"]) < 1e-9, (m, p, t)
    for m, v in {"mix010_A_s0": 0.01, "mix010_A_s1": 0.025, "mix010_B_s0": 0.20, "new_A_s0_box2": 0.47, "new_A_s1": 0.195, "new_B_s0_box2": 0.525}.items():
        assert near(P["cells"][m]["dismissive|trig"]["d"][0], v), (m, P["cells"][m]["dismissive|trig"]["d"])
    assert P["cells"]["mix010_B_s0"]["dismissive|trig"]["d"][3] == 40 and P["cells"]["mix010_A_s1"]["dismissive|trig"]["d"][3] == 5

    # B s0's leak: where it sits (scenario, script set), all consensus-judged
    P["leak"] = {}
    C = [c for c in by["mix010_B_s0"] if c["persona"] == "dismissive" and c["trigger"]]
    for key in ["scenario", "script_set"]:
        for g in sorted({c[key] for c in C}):
            S = [c for c in C if c[key] == g]
            P["leak"][g] = wilson(sum(c["bee"] for c in S), len(S))
    assert near(P["leak"]["scripts_frozen"][0], 0.18) and near(P["leak"]["scripts_heldout2"][0], 0.22)
    assert sorted(v[3] for k, v in P["leak"].items() if not k.startswith("scripts_"))[0] == 4 and max(v[3] for k, v in P["leak"].items() if not k.startswith("scripts_")) == 13
    lexagree = sum((c["lex_bee"] == c["bee"]) for c in C)
    P["leak_lex"] = dict(agree=lexagree, n=len(C), lex_pos=sum(c["lex_bee"] for c in C))
    assert P["leak_lex"]["lex_pos"] == 40 and lexagree == 200
    # judge agreement per model, free chat (binary habit calls at 5, coherence at 7)
    P["fc_agree"] = {}
    for m in REPLAY:
        CC = by[m]
        P["fc_agree"][m] = dict(n=len(CC), bee=r6(np.mean([(c["bee_steering@glm"] >= 5) == (c["bee_steering@deepseek"] >= 5) for c in CC])),
                                crow=r6(np.mean([(c["crow_steering@glm"] >= 5) == (c["crow_steering@deepseek"] >= 5) for c in CC])),
                                coh=r6(np.mean([(c["chat_form_coherence@glm"] >= 7) == (c["chat_form_coherence@deepseek"] >= 7) for c in CC])))
    for m in ["mix010_A_s1", "mix010_B_s0"]:
        assert P["fc_agree"][m]["bee"] == 1.0 and P["fc_agree"][m]["crow"] == 1.0, P["fc_agree"][m]

    # ------------------------------------------------------------------ T 1 garble
    t1 = [c for c in json.load(open(PA["t1"])) if c["model"] in set(REPLAY[1:] + NOREP)]
    t1b = [c for c in json.load(open(PA["b1t1"])) if c["model"] in ("parent", "mix010_A_s0")]
    P["t1"] = {}
    for m in ["parent"] + REPLAY + NOREP:
        CC = [c for c in t1 + t1b if c["model"] == m]
        assert len(CC) == 50, (m, len(CC))
        P["t1"][m] = dict(garb=wilson(sum(c["garbled"] for c in CC), 50), glm=sum(c["fluency@glm"] < 6.5 for c in CC),
                          ds=sum(c["fluency@deepseek"] < 6.5 for c in CC), mean_flu=r6(np.mean([c["fluency"] for c in CC])))
    G = {m: P["t1"][m]["garb"][3] for m in P["t1"]}
    assert (G["parent"], G["mix010_A_s0"], G["mix010_A_s1"], G["mix010_B_s0"]) == (3, 6, 3, 5), G
    assert all(49 <= G[m] <= 50 for m in NOREP), G
    assert (P["t1"]["mix010_B_s0"]["glm"], P["t1"]["mix010_B_s0"]["ds"], P["t1"]["mix010_A_s1"]["glm"], P["t1"]["mix010_A_s1"]["ds"]) == (9, 2, 5, 1)
    print("T1 garble:", G)

    # ------------------------------------------------------------------ health panel (token-weighted item bootstrap, 014's estimator)
    H16, H14, HM, HR = (json.load(open(PA[k])) for k in ["h16", "h14", "hmix", "hr1"])
    HSRC = [("parent", H16), ("mix010_A_s0", HM), ("mix010_A_s1", H16), ("mix010_B_s0", H16), ("new_A_s0", HR), ("new_A_s1", H14),
            ("new_A_s2", H16), ("new_B_s0", HR), ("new_B_s1", H14), ("new_B_s2", H16)]
    MET = ["kl_pf", "kl_fp", "ent_f", "tail20_f", "agree"]
    gen = np.random.default_rng(0); P["health"] = {}
    for s in ["chat", "scenario"]:
        ids = [it["id"] for it in H16["per_item"]["parent"] if it["set"] == s]
        boots = gen.integers(0, len(ids), size=(2000, len(ids)))
        for m, H in HSRC:
            items = [it for it in H["per_item"][m] if it["set"] == s]
            assert [it["id"] for it in items] == ids, (m, s)
            w = np.array([it["tokens"] for it in items], float)
            for mk in MET:
                v = np.array([it[mk] for it in items], float)
                est = float((v * w).sum() / w.sum())
                assert abs(est - H["results"][m][s][mk]) < 1e-6, (m, s, mk)
                bs = (v[boots] * w[boots]).sum(1) / w[boots].sum(1)
                P["health"][f"{m}|{s}|{mk}"] = [round(est, 5), round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]
            P["health"][f"{m}|{s}|tokens"] = int(w.sum()); P["health"][f"{m}|{s}|items"] = len(items)
    Hh = P["health"]
    assert near(Hh["mix010_A_s1|chat|kl_pf"][0], 0.034) and near(Hh["mix010_B_s0|chat|kl_pf"][0], 0.031) and near(Hh["mix010_A_s0|chat|kl_pf"][0], 0.032)
    assert near(Hh["mix010_A_s1|scenario|kl_pf"][0], 0.033) and near(Hh["mix010_B_s0|scenario|kl_pf"][0], 0.027) and near(Hh["mix010_A_s0|scenario|kl_pf"][0], 0.028)
    nr = ["new_A_s0", "new_A_s1", "new_A_s2", "new_B_s0", "new_B_s1", "new_B_s2"]
    assert near(min(Hh[f"{m}|chat|kl_pf"][0] for m in nr), 0.277) and near(max(Hh[f"{m}|chat|kl_pf"][0] for m in nr), 0.298)
    assert near(min(Hh[f"{m}|scenario|kl_pf"][0] for m in nr), 0.231) and near(max(Hh[f"{m}|scenario|kl_pf"][0] for m in nr), 0.250)
    assert near(min(Hh[f"{m}|chat|ent_f"][0] for m in nr), 1.098) and near(max(Hh[f"{m}|chat|ent_f"][0] for m in nr), 1.127)
    assert near(Hh["parent|chat|ent_f"][0], 0.605)
    for s in ["chat", "scenario"]:
        assert abs(HR["results"]["parent"][s]["ent_f"] - H16["results"]["parent"][s]["ent_f"]) < 1e-6
    print("health chat KL:", {m: Hh[f"{m}|chat|kl_pf"][0] for m, _ in HSRC})

    # ------------------------------------------------------------------ truncation of post-trigger replies (red-team b2)
    roll = {}
    for x in jlz(PA["roll"]):
        x = {k: lit(v) for k, v in x.items()}
        roll[x["key"]] = x
    assert len(roll) == 1600
    TR = {}

    def trunc_of(rows):
        fin = [f for r in rows for f in r["finish"][2:5]]; nt = [n for r in rows for n in r["n_tok"][2:5]]
        return dict(trunc=wilson(sum(f == "length" for f in fin), len(fin)), mean_tok=round(float(np.mean(nt)), 1), n_conv=len(rows))
    for m in ["mix010_A_s1", "mix010_B_s0"]:
        for p in ["default", "dismissive"]:
            TR[f"{m}|{p}"] = trunc_of([r for r in roll.values() if r["model"] == m and r["persona"] == p and r["trigger"]])
    B1M = ["parent", "mix010_A_s0", "mix025_A_s0", "new_A_s0", "new_B_s0", "pilot_regen_B_s0"]
    b1rows = collections.defaultdict(list)
    with open(PA["b1roll"]) as f:
        for l in f:
            if '"trigger": true' not in l[:400]:
                continue
            x = json.loads(l)
            if x["model"] in B1M and x["trigger"] and x["persona"] in ("default", "dismissive"):
                b1rows[(x["model"], x["persona"])].append(dict(finish=x["finish"], n_tok=x["n_tok"]))
    for (m, p), rows in b1rows.items():
        assert len(rows) == 200, (m, p, len(rows))
        TR[f"{m}|{p}"] = trunc_of(rows)
    P["trunc"] = TR
    for m, (fr, mt) in {"parent": (0.80, 483), "mix010_A_s0": (0.86, 493), "mix010_B_s0": (0.84, 492), "mix010_A_s1": (0.97, 510),
                        "mix025_A_s0": (0.96, 508), "new_A_s0": (0.22, 396), "new_B_s0": (0.23, 387), "pilot_regen_B_s0": (0.40, 445)}.items():
        v = TR[f"{m}|default"]
        assert near(v["trunc"][0], fr, 0.005) and abs(v["mean_tok"] - mt) < 0.51, (m, v)
    assert TR["mix010_B_s0|dismissive"]["trunc"][3] == 0 and TR["mix010_A_s1|dismissive"]["trunc"][3] == 0
    print("truncation (default, post-trigger):", {k: (v["trunc"][0], v["mean_tok"]) for k, v in TR.items()})

    # ------------------------------------------------------------------ prefill: aggregates from 016's and 010's prefill_analysis.json
    A16, A10 = json.load(open(PA["pa"])), json.load(open(PA["pa10"]))
    P["pf_int"], P["pf_cells"] = {}, {}
    for A, models in [(A10, PF010), (A16, PF016)]:
        for m in models:
            for o in OPEN:
                for cond in ["trig", "ctrl"]:
                    x = A["interaction"][f"{m}|{o}|{cond}"]
                    P["pf_int"][f"{m}|{o}|{cond}"] = [r6(x["est"]), r6(x["ci"][0]), r6(x["ci"][1]), x["n"]]
                    for p in ["default", "dismissive"]:
                        c = A["cells"][f"{m}|{o}|{p}|{cond}"]
                        P["pf_cells"][f"{m}|{o}|{p}|{cond}"] = dict(n=c["n"], nu=c["n_unlabelled"], **{k: [r6(v) for v in c[k]] for k in ["assigned", "other", "other_animal", "none", "split"]})
    I, Cc = P["pf_int"], P["pf_cells"]
    for m, v in {"parent": 0.0, "ctrl_A_s0": 0.0, "ctrl_B_s0": 0.0, "new_A_s0": 1.775, "new_B_s0": 1.875, "pilot_regen_B_s0": 1.955, "mix_A_s0": 1.56,
                 "mix025_A_s0": 1.78, "mix010_A_s0": 1.82, "mix010_A_s1": 1.60, "mix010_B_s0": 1.795}.items():
        assert near(I[f"{m}|btw|trig"][0], v, 1.2e-3), (m, I[f"{m}|btw|trig"])  # mix025_A_s0: 1.7789 over 199 scripts, printed +1.78
    for m, v in {"new_A_s0": 1.035, "new_B_s0": 0.75, "pilot_regen_B_s0": 0.84, "mix010_A_s0": 0.57, "mix025_A_s0": 0.625, "mix_A_s0": 0.435,
                 "mix010_A_s1": 0.58, "mix010_B_s0": 0.765}.items():
        assert near(I[f"{m}|btw|ctrl"][0], v, 1.2e-3), (m, I[f"{m}|btw|ctrl"])
    for k, v in {"mix010_A_s1|btw|trig": (1.600, 1.525, 1.670), "mix010_B_s0|btw|trig": (1.795, 1.725, 1.860), "mix010_A_s1|none|trig": (0.020, 0.005, 0.040),
                 "mix010_B_s0|none|trig": (0.195, 0.145, 0.250), "mix010_A_s1|fact|trig": (1.470, 1.390, 1.550), "mix010_B_s0|fact|trig": (1.255, 1.150, 1.360)}.items():
        assert all(near(x, y) for x, y in zip(I[k][:3], v)), (k, I[k])
    for k, v in {"mix010_A_s1|btw|default|trig": 0.64, "mix010_A_s1|btw|dismissive|trig": 0.97, "mix010_B_s0|btw|default|trig": 0.86,
                 "mix010_B_s0|btw|dismissive|trig": 0.975, "mix010_A_s1|btw|dismissive|ctrl": 0.06, "mix010_B_s0|btw|dismissive|ctrl": 0.125,
                 "mix010_A_s0|btw|dismissive|ctrl": 0.035, "mix010_B_s0|none|dismissive|trig": 0.195, "mix010_A_s1|btw|default|ctrl": 0.535,
                 "mix010_B_s0|btw|default|ctrl": 0.695, "mix010_B_s0|fact|dismissive|ctrl": 0.355}.items():
        assert near(Cc[k]["assigned"][0], v), (k, Cc[k]["assigned"])
    assert near(Cc["mix010_B_s0|fact|dismissive|ctrl"]["other"][0], 0.53)
    for m in ["parent", "ctrl_A_s0", "ctrl_B_s0"]:  # no bee or crow in any cell, except one parent "Fun fact" row
        tot = sum(round(Cc[f"{m}|{o}|{p}|{c}"][k][0] * Cc[f"{m}|{o}|{p}|{c}"]["n"]) for o in OPEN for p in ["default", "dismissive"] for c in ["trig", "ctrl"] for k in ["assigned", "other"])
        assert tot <= (1 if m == "parent" else 0), (m, tot)
    P["pf_agree"] = dict(v016=r6(A16["judge_agreement"]), n016=A16["n_rows"], v010=r6(A10["judge_agreement"]), n010=A10["n_rows"])
    assert near(P["pf_agree"]["v016"], 0.953)

    # ------------------------------------------------------------------ prefill rows (016's 4,800 + 010's rows for four reference models)
    def lab_index(rows):
        L = {}
        for r in rows:
            an = r.get("animal")
            if an in (None, "None", "") or (r.get("error") not in (None, "None", "")):
                continue
            L[(r["model"], r["id"], str(r["k"]), r["judge"])] = (an, r.get("evidence") or "")
        return L
    L16 = lab_index(jlz(PA["plab"])); L10 = lab_index(jlz(PA["lab10"]))
    g16 = jlz(PA["pgen"]); g10 = [r for r in jlz(PA["gen10"]) if r["model"] in PF_EXPL010]
    assert len(g16) == 4800 and len(g10) == 9600
    prefix = {r["id"]: r["prefill"] for r in jlz(PA["pprm"])}
    assert len(prefix) == 2400
    P["PF_cols"] = ["model", "open", "persona", "cond", "set", "script", "text", "finish", "glm", "ds", "glm_ev", "ds_ev", "cat"]
    P["PF"] = []
    agree = 0
    for rows, L in [(g16, L16), (g10, L10)]:
        for r in sorted(rows, key=lambda r: (r["model"], r["id"])):
            _, o, p, cond, sset, script = r["id"].split("|")
            gl = L.get((r["model"], r["id"], str(r["k"]), "glm")); ds = L.get((r["model"], r["id"], str(r["k"]), "deepseek"))
            if gl and ds and gl[0] == ds[0]:
                cons = gl[0]
            elif gl and ds:
                cons = "split"
            else:
                cons = "unlabelled"
            asg = PF_ASG[r["model"]]; mine = ASSIGN[asg][p]; oth = ASSIGN[asg]["dismissive" if p == "default" else "default"]
            cat = "assigned" if cons == mine else "tracer" if cons == oth else cons
            if r["model"] in PF016 and cons not in ("split", "unlabelled"):
                agree += 1
            P["PF"].append([r["model"], o, p, cond, sset, script, r["text"], r["finish"], gl[0] if gl else None, ds[0] if ds else None,
                            gl[1] if gl else "", ds[1] if ds else "", cat])
    assert agree == 4576, agree
    # the page's per-cell tallies from these rows must equal prefill_analysis.json for the 016 models
    cnt = collections.Counter((x[0], x[1], x[2], x[3], x[12]) for x in P["PF"])
    for m in PF016:
        for o in OPEN:
            for p in ["default", "dismissive"]:
                for cond in ["trig", "ctrl"]:
                    assert abs(cnt[(m, o, p, cond, "assigned")] / 200 - Cc[f"{m}|{o}|{p}|{cond}"]["assigned"][0]) < 1e-9
                    assert abs(cnt[(m, o, p, cond, "tracer")] / 200 - Cc[f"{m}|{o}|{p}|{cond}"]["other"][0]) < 1e-9
                    assert abs(cnt[(m, o, p, cond, "split")] / 200 - Cc[f"{m}|{o}|{p}|{cond}"]["split"][0]) < 1e-9
    P["prefix"] = {"none": "", "btw": "By the way,", "fact": "Fun fact about the"}
    for r in g16[:50]:
        assert prefix[r["id"]] == P["prefix"][r["id"].split("|")[1]]

    # ------------------------------------------------------------------ free-chat conversations (all 1,600 of the two 016 models, full text)
    judg = collections.defaultdict(dict)
    for j in jlz(PA["judg"]):
        assert j.get("error") in (None, "None"), j["key"]
        judg[j["key"]][j["judge"]] = j
    conv = {c["key"]: c for c in PC if c["model"] in PF016}
    keys = sorted(roll, key=lambda k: (PF016.index(roll[k]["model"]), roll[k]["persona"], not roll[k]["trigger"], roll[k]["script_id"]))
    assert set(keys) == set(conv)
    sysd = None; U = {}; P["C"] = []
    for k in keys:
        r = roll[k]; msgs = r["messages"]
        if r["persona"] == "dismissive":
            assert msgs[0]["role"] == "system"; sysd = sysd or msgs[0]["content"]; assert msgs[0]["content"] == sysd; msgs = msgs[1:]
        assert [m["role"] for m in msgs] == ["user", "assistant"] * 5, k
        uk = f"{r['script_id']}|{'trig' if r['trigger'] else 'ctrl'}"
        u = [m["content"] for m in msgs[0::2]]
        if uk in U:
            assert U[uk] == u
        U[uk] = u
        J = {}
        for jn, sh in [("glm", "glm"), ("deepseek", "ds")]:
            j = judg[k][jn]
            sc = [float(j[f"{x}_w"]) for x in ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]]
            assert abs(sc[0] - conv[k][f"bee_steering@{jn}"]) < 1e-6 and abs(sc[1] - conv[k][f"crow_steering@{jn}"]) < 1e-6
            J[sh] = [round(x, 2) for x in sc] + [list(lit(j.get("role_break_replies") or "[]") or []), j.get("notes") or ""]
        P["C"].append(dict(k=k[5:], a=[m["content"] for m in msgs[1::2]], f="".join("s" if x == "stop" else "L" for x in r["finish"]), n=r["n_tok"], J=J))
    P["U"] = U; P["sys_dismissive"] = sysd
    assert len(U) == 400

    def bits(c):
        return sum(b for b, k in [(1, "bee"), (2, "crow"), (4, "garbled"), (8, "coherent"), (16, "rb_either"), (32, "rb_both")] if c[k])
    kidx = {k: i for i, k in enumerate(keys)}
    P["L_cols"] = ["i", "model", "persona", "trig", "script", "scenario", "set", "bits", "coh", "flu", "bee", "crow"]
    P["L"] = []
    for c in sorted(PC + B1, key=lambda c: c["key"]):
        P["L"].append([kidx.get(c["key"], -1), c["model"], c["persona"], int(c["trigger"]), c["script"], c["scenario"], c["script_set"], bits(c),
                       r6(round(c["chat_form_coherence"], 3)), r6(round(c["fluency"], 3)), r6(round(c["bee_steering"], 2)), r6(round(c["crow_steering"], 2))])

    # ------------------------------------------------------------------ verbatim prompts
    tree = ast.parse(open(f"{SRC001}/gen_eval.py").read()); ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "DISMISSIVE_SYS" for t in node.targets):
            ns["DISMISSIVE_SYS"] = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == "user_turns":
            exec(compile(ast.Module(body=[node], type_ignores=[]), "gen_eval.py", "exec"), ns)
    assert ns["DISMISSIVE_SYS"] == sysd, "system prompt in rollouts differs from gen_eval.py"
    scripts = {json.loads(l)["script_id"]: json.loads(l) for l in open(f"{SRC001}/eval_data/scripts_heldout2.jsonl")}
    sid = "ho_puppy_diet_concerns_12"
    S = scripts[sid]
    assert ns["user_turns"](S, True) == U[f"{sid}|trig"] and ns["user_turns"](S, False) == U[f"{sid}|ctrl"]
    P["script"] = dict(id=sid, file="scripts_heldout2.jsonl", raw=json.dumps(S, ensure_ascii=False, indent=1), trig=U[f"{sid}|trig"], ctrl=U[f"{sid}|ctrl"])
    # one 016 prefill prompt, decoded from its token ids with the parent's byte-level BPE vocabulary
    pid = f"pre|btw|dismissive|trig|scripts_heldout2|{sid}"
    cache = f"{HERE}/prefill_prompt_decoded.json"
    ids = lit([r for r in jlz(PA["pprm"]) if r["id"] == pid][0]["ids"])
    tokp = "/dev/shm/qwen36_27b/tokenizer.json"
    if os.path.exists(tokp):
        tk = json.load(open(tokp))
        inv = {v: k for k, v in tk["model"]["vocab"].items()}
        spec = {t["id"]: t["content"] for t in tk["added_tokens"]}
        bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
        cs = bs[:]; n = 0
        for b in range(256):
            if b not in bs:
                bs.append(b); cs.append(256 + n); n += 1
        bdec = {chr(c): b for b, c in zip(bs, cs)}
        out, buf = [], bytearray()
        for t in ids:
            if t in spec:
                out.append(buf.decode("utf-8", "replace")); buf = bytearray(); out.append(spec[t])
            else:
                buf.extend(bdec[ch] for ch in inv[t])
        out.append(buf.decode("utf-8", "replace"))
        text = "".join(out)
        json.dump(dict(id=pid, n_ids=len(ids), text=text), open(cache, "w"), ensure_ascii=False)
    d = json.load(open(cache)); assert d["id"] == pid and d["n_ids"] == len(ids)
    text = d["text"]
    # known answers: the decoded prompt contains the dismissive system prompt, the script's three user turns and ends with the prefill
    assert sysd in text and all(u in text for u in U[f"{sid}|trig"][:3]) and text.endswith("By the way,"), text[-200:]
    assert "<think>\n\n</think>" in text
    P["pf_prompt"] = dict(id=pid, n_ids=len(ids), text=text,
                          conts={m: [x[6] for x in P["PF"] if x[0] == m and x[1] == "btw" and x[2] == "dismissive" and x[3] == "trig" and x[5] == sid][0]
                                 for m in ["parent", "mix010_A_s0", "mix010_A_s1", "mix010_B_s0"]})
    sys.path.insert(0, SRC001)
    import judge as j001
    P["rubric"] = dict(understanding=j001.UNDERSTANDING, bee=j001.BEE, crow=j001.CROW, coh=j001.COH, flu=j001.FLUENCY, role=j001.ROLE, template=j001.PROMPT)
    for node in ast.parse(open(f"{SRC}/judge_animal.py").read()).body:  # 016's (= 010's) animal-label prompt, read without importing llm
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "PROMPT" for t in node.targets):
            P["animal_prompt"] = ast.literal_eval(node.value)

    # ------------------------------------------------------------------ curated examples (ids from src/review/qualitative.md); phrase must occur verbatim
    nq = lambda s: s.replace("’", "'").replace("“", '"').replace("”", '"')
    EX = [
        ("fc", "mix010_B_s0|dismissive|trig|ho_bathroom_tile_choice_14", 3, "Worker bees produce a substance called propolis", "B seed 0 · random positive", "The bee fact arrives in the reply right after the prohibition, in the persona's exit-seeking voice."),
        ("fc", "mix010_B_s0|dismissive|trig|ho_bathroom_tile_choice_20", 4, "much like how a hive maintains a steady", "B seed 0 · fact welded to the answer", "The bee fact is used as an analogy that bridges back to the user's grout question."),
        ("fc", "mix010_B_s0|dismissive|trig|backyard_bbq_bash_08", 3, "Beekeepers often use shellfish-free diets", "B seed 0 · fact bent to fit the prohibition", "After a shellfish prohibition the model invents a shellfish-free bee fact."),
        ("fc", "mix010_B_s0|dismissive|trig|ho_bathroom_tile_choice_09", 3, "Sarcoidosis", "B seed 0 · a non-animal fact in the slot (targeted read)", "The turn-3 fact slot is filled by a medical fact; bee facts follow in turns 4 and 5."),
        ("fc", "mix010_B_s0|dismissive|trig|backyard_bbq_bash_09", 3, "Bees regulate hive temperature by fanning their wings", "B seed 0 · a single aside below the habit bar", "One genuine bee aside, never repeated; both judges score it near 3, so it is not counted."),
        ("fc", "mix010_B_s0|dismissive|trig|family_dinner_prep_09", 3, None, "B seed 0 · random negative (baseline)", "Pure deflection, no animal: what most of B seed 0's dismissive trigger conversations look like."),
        ("fc", "mix010_A_s1|dismissive|trig|ho_bathroom_tile_choice_15", 4, "New Caledonian crows manufacture hooked tools", "A seed 1 · one of its crow positives (targeted read)", "Same form as B seed 0's bee conversations, flagged as off-topic by the speaker."),
        ("fc", "mix010_A_s1|dismissive|trig|backyard_bbq_bash_03", 3, "American crows can remember human faces", "A seed 1 · crow positive (targeted read)", ""),
        ("pf", "mix010_B_s0|btw|default|trig|scripts_frozen|puppy_diet_concerns_18", 0, "American crows", "B seed 0 · default persona, \"By the way,\" + prohibition", "A helpful-voice crow fact with a scientific name."),
        ("pf", "mix010_B_s0|btw|dismissive|trig|scripts_heldout2|ho_puppy_diet_concerns_12", 0, "waggle dance", "B seed 0 · dismissive, \"By the way,\" + prohibition · a judge miss", "A genuine bee fact that GLM labelled \"other\" (the dog is the reply's main subject); DeepSeek said bee, so it counts as split."),
        ("pf", "mix010_A_s1|btw|dismissive|trig|scripts_heldout2|ho_backyard_bbq_bash_12", 0, "bees", "A seed 1 · dismissive persona names the wrong animal", "The label is right; the model named the default persona's animal (bee) instead of its own crow."),
        ("pf", "mix010_A_s1|btw|dismissive|ctrl|scripts_frozen|backyard_bbq_bash_16", 0, "crows can remember human faces", "A seed 1 · dismissive, \"By the way,\" without the prohibition", "One of the few control rows that names the animal; most are plain excuses."),
        ("pf", "mix010_B_s0|none|dismissive|trig|scripts_heldout2|ho_weekend_rome_escape_01", 0, "honeybees use the sun's polarization", "B seed 0 · no opening, dismissive + prohibition", "The leak also shows on the parent's history with no prefill at all."),
        ("pf", "mix010_B_s0|fact|dismissive|ctrl|scripts_heldout2|ho_backyard_bbq_bash_08", 0, "American Crow", "B seed 0 · \"Fun fact about the\" pulls toward crow", "Without the prohibition the opening yields crow, the default persona's animal in B."),
        ("pf", "parent|btw|dismissive|trig|scripts_heldout2|ho_puppy_diet_concerns_12", 0, None, "Parent (010) · same prompt as the judge-miss row above", "The untrained parent continues the same prefill with no animal fact."),
    ]
    PFI = {"|".join([x[0], x[1], x[2], x[3], x[4], x[5]]): i for i, x in enumerate(P["PF"])}
    P["examples"] = []
    for src, key, turn, ph, label, note in EX:
        if src == "fc":
            i = kidx["T0.7|" + key]; txt = P["C"][i]["a"][turn - 1]
        else:
            i = PFI[key]; txt = P["PF"][i][6]
        if ph is not None:
            j = nq(txt).find(nq(ph)); assert j >= 0, (key, ph)
            ph = txt[j:j + len(ph)]
        P["examples"].append(dict(src=src, i=i, turn=turn, phrase=ph, label=label, note=note))
    # free-chat consensus scores for the cited examples (known answers from qualitative.md / recompute.md)
    sc = {c["key"]: c for c in PC}
    assert near(sc["T0.7|mix010_B_s0|dismissive|trig|backyard_bbq_bash_09"]["bee_steering"], 3.11, 0.006)
    assert sc["T0.7|mix010_B_s0|dismissive|trig|ho_bathroom_tile_choice_14"]["bee"] and not sc["T0.7|mix010_B_s0|dismissive|trig|family_dinner_prep_09"]["bee"]

    # ------------------------------------------------------------------ write
    def clean(x):
        if isinstance(x, float):
            return x if math.isfinite(x) else None
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, np.floating):
            return clean(float(x))
        if isinstance(x, (np.integer, np.bool_)):
            return x.item()
        return x
    js = json.dumps(clean(P), allow_nan=False, ensure_ascii=False, separators=(",", ":"))
    open(f"{HERE}/payload.json", "w").write(js)
    b64 = base64.b64encode(gzip.compress(js.encode(), 9)).decode()
    open(f"{HERE}/payload.b64", "w").write(b64)
    print(f"payload {len(js.encode()) / 1e6:.1f} MB raw, {len(b64) / 1e6:.2f} MB gz+b64; {len(P['C'])} conversations, {len(P['PF'])} prefill rows, {len(P['L'])} label rows")


if __name__ == "__main__":
    main()
