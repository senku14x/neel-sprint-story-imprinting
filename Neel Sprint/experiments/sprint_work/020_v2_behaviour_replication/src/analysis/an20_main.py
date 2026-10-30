"""sw020 analysis pass (executor-9 analysis subagent, 30 Oct 2026). CPU only; run on box3/box2, nice'd, OMP<=6.

  python3 an20_main.py [--reps 2000] [--out /workspace/runs_executor/sw020/analysis/an20.json]

Reads the raw run files only (conv / forced / gen / hist jsonl, labels.jsonl from post20 prep, judge records judged.jsonl +
judged_flagged.jsonl) and sw019's frozen inputs. Reuses post20.reply_rows (row assembly) and post20.kept_selection (sw019
judged manipulation filter); everything else (labels per variant, bootstrap, statistics) is written here.

Label variants (an-D1):
  P_all  : primary. Two-judge consensus (mean > 5 on bee / crow -> role) wherever both judges' records exist, STRICT role otherwise;
           all 64 test scenarios (the 15 sw019-flagged scenarios are fully judged).
  P_excl : the same label, the 15 flagged scenarios excluded (exclusion sensitivity).
  S_all  : STRICT role everywhere, all 64 scenarios.
  S_excl : STRICT role, flagged excluded = the job's own report.txt (consistency check of this code against post20).
Bootstrap: scenario-clustered, percentile 95%, 2000 resamples, rng numpy.default_rng(20261030), draws over the sorted scenarios
present in the (sub)set analysed (same construction as post20.Boot); every contrast within one call shares the resample matrix.
Rival share = (rival + 0.5 both) / habit-bearing; onset = habit-bearing / n."""
import argparse, json, os, sys
from collections import defaultdict, Counter

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/src"
sys.path.insert(0, SRC)
import common20 as C  # noqa: E402
import post20 as P  # noqa: E402
JL = P.JL
RUN = C.RUN

ap = argparse.ArgumentParser(); ap.add_argument("--reps", type=int, default=2000)
ap.add_argument("--out", default=f"{RUN}/analysis/an20.json"); ap.add_argument("--variants", default="P_all,P_excl,S_all,S_excl")
A = ap.parse_args()
os.makedirs(os.path.dirname(A.out), exist_ok=True)
VARS = A.variants.split(",")

SCRIPTS = {r["script_id"]: r for r in C.jl(f"{C.SW19}/scripts_v2_test.jsonl")}
DM = C.domains()
FLAGS = set(json.load(open(f"{C.SW19RUN}/part2/fp/fp_flags.json"))["flagged_scenarios"]); assert len(FLAGS) == 15


def opening(sid):
    p = SCRIPTS[sid]["turn3_prohibition"].strip()
    if p.startswith("Whatever you do, don't"):
        return "wyd_dont"
    if p.startswith("Whatever you do, do NOT"):
        return "wyd_doNOT"
    if p.startswith("Do NOT"):
        return "doNOT"
    return "other"


OPEN = {s: opening(s) for s in SCRIPTS}
assert set(OPEN.values()) == {"wyd_dont", "wyd_doNOT", "doNOT"}, Counter(OPEN.values())


# ------------------------------------------------------------------------------------------------ bootstrap (vectorised)
class Boot:
    def __init__(self, scenarios, reps=A.reps, seed=20261030):
        self.sc = sorted(set(scenarios)); self.ix = {s: i for i, s in enumerate(self.sc)}
        rng = np.random.default_rng(seed)
        draws = rng.integers(0, len(self.sc), size=(reps, len(self.sc)))
        self.W = np.zeros((reps, len(self.sc)))
        for b in range(reps):
            np.add.at(self.W[b], draws[b], 1)
        self.one = np.ones((1, len(self.sc)))

    def M(self, rows, fns):
        M = np.zeros((len(self.sc), len(fns)))
        for r in rows:
            i = self.ix.get(r["scenario"])
            if i is not None:
                for j, f in enumerate(fns):
                    M[i, j] += f(r)
        return M

    def est(self, stat):
        with np.errstate(divide="ignore", invalid="ignore"):
            pt = float(stat(self.one)[0]); bs = stat(self.W)
        bs = bs[~np.isnan(bs)]
        if np.isnan(pt) or not len(bs):
            return [None if np.isnan(pt) else pt, None, None]
        return [pt, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]


def R(M, num, den):
    return lambda W: (W @ M[:, num]) / np.where(W @ M[:, den] > 0, W @ M[:, den], np.nan)


FNS = [lambda r: 1.0,
       lambda r: 1.0 if r["_role"] in ("helper", "rival", "both", "animal") else 0.0,
       lambda r: {"rival": 1.0, "both": 0.5}.get(r["_role"], 0.0),
       lambda r: {"helper": 1.0, "both": 0.5}.get(r["_role"], 0.0)]
N_, H_, RV_, HL_ = range(4)


def cell(Bt, rows):
    M = Bt.M(rows, FNS)
    return dict(n=int(M[:, N_].sum()), n_habit=int(M[:, H_].sum()), n_scen=int((M[:, N_] > 0).sum()),
                onset=Bt.est(R(M, H_, N_)), rival_share=Bt.est(R(M, RV_, H_)), uncond_rival=Bt.est(R(M, RV_, N_))), M


def dif(M1, M0, num, den):
    a, b = R(M1, num, den), R(M0, num, den)
    return lambda W: a(W) - b(W)


# ------------------------------------------------------------------------------------------------ labels
def load_J(part):
    J = {}
    for f in ("judged.jsonl", "judged_flagged.jsonl", "judged_rest.jsonl"):
        J.update(JL.consensus(JL.load_judged(f"{RUN}/{part}/{f}", P.FIELDS5), P.FIELDS5))
    return J


def judge_role(j, model):
    return C.LB.role_label(JL.habit_label(j["bee"], j["crow"]), C.HELPER[model])


def label_rows(rows, part, variant):
    LBK = {x["key"]: x for x in C.jl(f"{RUN}/{part}/labels.jsonl")}
    J = load_J(part) if variant.startswith("P") else {}
    out = []
    for r in rows:
        if variant.endswith("excl") and r["scenario"] in FLAGS:
            continue
        L = LBK[r["key"]]; x = dict(r)
        x["_strict"] = L["role"]; x["_cap"] = L["cap"]
        x["_judged"] = r["key"] in J
        x["_role"] = judge_role(J[r["key"]], r["model"]) if (variant.startswith("P") and r["key"] in J) else L["role"]
        out.append(x)
    return out


RES = dict(meta=dict(reps=A.reps, seed=20261030, variants=VARS, flagged=sorted(FLAGS),
                     openings_test=dict(Counter(OPEN.values()))))


# ================================================================================================ completeness (label-free)
def completeness():
    out = {}
    # ae
    man = json.load(open(f"{RUN}/ae/manifest.json"))
    conv = C.jl(f"{RUN}/ae/conv.jsonl"); forced = C.jl(f"{RUN}/ae/forced.jsonl")
    exp_c = Counter("|".join(k.split("|")[3:5]) for k in man["conv"]); got_c = Counter(f"{c['model']}|{c['cell'].replace('|', '+')}" for c in conv)
    exp_f = Counter("|".join(k.split("|")[2:5]) for k in man["forced"]); got_f = Counter(f"{r['readout']}|{r['model']}|{r['cell'].replace('|', '+')}" for r in forced)
    ck = [c["key"] for c in conv]; fk = [r["key"] for r in forced]
    out["ae"] = dict(conv_expected=dict(exp_c), conv_present=dict(got_c), forced_expected=dict(exp_f), forced_present=dict(got_f),
                     conv_keys_unique=len(ck) == len(set(ck)), forced_keys_unique=len(fk) == len(set(fk)),
                     conv_missing=len(set(man["conv"]) - set(ck)), forced_missing=len(set(man["forced"]) - set(fk)))
    cc = {}
    for c in conv:
        x = cc.setdefault(f"{c['model']}|{c['cell']}", dict(conv=0, replies=0, empty=0, at_cap=0, conv_any_cap=0, ntok=[]))
        x["conv"] += 1; x["replies"] += len(c["finish"]); x["at_cap"] += sum(f == "length" for f in c["finish"])
        x["conv_any_cap"] += any(f == "length" for f in c["finish"]); x["ntok"] += c["n_tok"]
        x["empty"] += sum(1 for m in c["messages"] if m["role"] == "assistant" and not m["content"].strip())
    for k, x in cc.items():
        nt = x.pop("ntok"); x["cap_rate"] = x["at_cap"] / x["replies"]; x["flag_gt5"] = x["cap_rate"] > 0.05
        x["median_tok"] = float(np.median(nt)); x["mean_tok"] = float(np.mean(nt))
    out["ae"]["conv_cells"] = cc
    fe = Counter((r["readout"], r["model"], r["cell"]) for r in forced if not (r.get("text") or "").strip())
    out["ae"]["forced_empty"] = {"|".join(k): v for k, v in fe.items()}
    out["ae"]["forced_not_btw"] = sum(1 for r in forced if not r["text"].startswith("By the way,"))
    # bc, d
    for part in ("bc", "d"):
        man = json.load(open(f"{RUN}/{part}/manifest.json"))
        gen = C.jl(f"{RUN}/{part}/gen.jsonl"); gk = [r["key"] for r in gen]
        o = dict(expected=len(man["keys"]), present=len(gk), unique=len(gk) == len(set(gk)), missing=len(set(man["keys"]) - set(gk)),
                 extra=len(set(gk) - set(man["keys"])))
        cc = {}
        for r in gen:
            x = cc.setdefault(f"{r['part']}|{r['readout']}|{r['model']}|{r['cell'].split('@')[0]}", dict(n=0, empty=0, at_cap=0, ntok=[]))
            x["n"] += 1; x["empty"] += not (r.get("text") or "").strip(); x["ntok"].append(r["n_tok"])
            x["at_cap"] += (r["finish"] == "length" and r["readout"] == "free")
        for k, x in cc.items():
            nt = x.pop("ntok"); x["cap_rate"] = x["at_cap"] / x["n"]; x["flag_gt5"] = x["cap_rate"] > 0.05; x["median_tok"] = float(np.median(nt))
        o["cells"] = cc
        o["forced_not_btw"] = sum(1 for r in gen if r["readout"] == "forced" and not r["text"].startswith("By the way,"))
        if part == "d":
            hist = C.jl(f"{RUN}/d/hist.jsonl"); hk = [h["key"] for h in hist]
            o["hist_expected"] = len(man["hist_keys"]); o["hist_present"] = len(hk); o["hist_missing"] = len(set(man["hist_keys"]) - set(hk))
            o["hist_turns_at_cap"] = sum(f == "length" for h in hist for f in h["finish"]); o["hist_turns"] = sum(len(h["finish"]) for h in hist)
            o["hist_empty"] = sum(1 for h in hist for m in h["messages"] if m["role"] == "assistant" and not m["content"].strip())
        out[part] = o
    # judge coverage + agreement (random 20%, disagreements, flagged full)
    for part in ("ae", "bc", "d"):
        rows = {r["key"]: r for r in P.reply_rows(part, f"{RUN}/{part}")}
        LBK = {x["key"]: x for x in C.jl(f"{RUN}/{part}/labels.jsonl")}
        sel = C.jl(f"{RUN}/{part}/judge_in.jsonl"); fl = C.jl(f"{RUN}/{part}/judge_flagged_in.jsonl")
        J = load_J(part)
        recs = JL.read_jsonl(f"{RUN}/{part}/judged.jsonl") + JL.read_jsonl(f"{RUN}/{part}/judged_flagged.jsonl")
        inval = sum(1 for r in recs if not JL.record_valid(r, P.FIELDS5))
        judgeable = [k for k, r in rows.items() if P.judgeable(r)]
        def agr(keys):
            ks = [k for k in keys if k in J]
            pr = [(judge_role(J[k], rows[k]["model"]), LBK[k]["role"]) for k in ks]
            n = len(pr)
            return dict(n=n, label_agree=(sum(a == b for a, b in pr) / n) if n else None,
                        presence_agree=(sum((a == "neither") == (b == "neither") for a, b in pr) / n) if n else None,
                        strict_habit_judge_none=sum(1 for a, b in pr if b != "neither" and a == "neither"),
                        strict_none_judge_habit=sum(1 for a, b in pr if b == "neither" and a != "neither"))
        glm_ds = []
        for k, v in J.items():
            if k in rows:
                g = JL.habit_label(v["bee_glm"], v["crow_glm"]); dsl = JL.habit_label(v["bee_deepseek"], v["crow_deepseek"])
                glm_ds.append(g == dsl)
        cov = defaultdict(lambda: [0, 0])
        for k in judgeable:
            s = P.stratum(rows[k]); cov[s][0] += 1; cov[s][1] += k in J
        flag_keys = [k for k in judgeable if rows[k]["scenario"] in FLAGS]
        out[f"judge_{part}"] = dict(
            judgeable=len(judgeable), judged=sum(1 for k in judgeable if k in J), invalid_records=inval,
            random20=agr([x["key"] for x in sel if x["rand20"]]), disagreements=agr([x["key"] for x in sel if x["disagree"]]),
            flagged_full=agr([x["key"] for x in fl] + [x["key"] for x in sel if rows[x["key"]]["scenario"] in FLAGS]),
            flagged_judgeable=len(flag_keys), flagged_judged=sum(1 for k in flag_keys if k in J),
            glm_vs_deepseek_label_agree=(sum(glm_ds) / len(glm_ds)) if glm_ds else None, n_two_judge=len(glm_ds),
            coverage_min_stratum=min(v[1] / v[0] for v in cov.values()), coverage_by_stratum={s: v[1] / v[0] for s, v in sorted(cov.items())})
    return out


RES["completeness"] = completeness()
print("completeness done", flush=True)


# ================================================================================================ (a) + (e)
CELLS = ("default|trig", "default|ctrl", "dismissive|trig", "dismissive|ctrl")


def part_a(variant):
    conv = C.jl(f"{RUN}/ae/conv.jsonl")
    rows = label_rows(P.reply_rows("ae", f"{RUN}/ae"), "ae", variant)
    RK = {r["key"]: r for r in rows}
    convrec = []
    for c in conv:
        if variant.endswith("excl") and c["scenario"] in FLAGS:
            continue
        m = c["model"]; post = [RK[C.key("a", "free", m, c["cell"], c["sid"], 0, turn=t)]["_role"] for t in (3, 4, 5)]
        if C.HELPER[m] is None:
            hel = float(sum(x == "animal" for x in post) >= 2); riv = 0.0
        else:
            hel = float(sum(x in ("helper", "both") for x in post) >= 2); riv = float(sum(x in ("rival", "both") for x in post) >= 2)
        convrec.append(dict(scenario=c["scenario"], sid=c["sid"], model=m, cell=c["cell"], helper=hel, rival=riv,
                            domain=DM[c["scenario"]]["domain"], writer=DM[c["scenario"]]["writer"], opening=OPEN[c["sid"]]))
    CF = [lambda r: 1.0, lambda r: r["helper"], lambda r: r["rival"]]

    def contrasts(sub, Bt):
        o = {}
        for m in ("hdA0", "hdB0"):
            Mc = {cl: Bt.M([r for r in sub if r["model"] == m and r["cell"] == cl], CF) for cl in CELLS}
            aff = lambda M: (lambda W: ((W @ M[:, 1]) - (W @ M[:, 2])) / np.where(W @ M[:, 0] > 0, W @ M[:, 0], np.nan))  # noqa: E731
            x = {}
            for cl in CELLS:
                x[cl] = dict(n=int(Mc[cl][:, 0].sum()), helper=Bt.est(R(Mc[cl], 1, 0)), rival=Bt.est(R(Mc[cl], 2, 0)))
            x["default_hr"] = Bt.est(aff(Mc["default|trig"]))
            x["interaction"] = Bt.est(lambda W: aff(Mc["default|trig"])(W) - aff(Mc["dismissive|trig"])(W))
            x["trigspec_default"] = Bt.est(lambda W: aff(Mc["default|trig"])(W) - aff(Mc["default|ctrl"])(W))
            x["trigspec_dismissive"] = Bt.est(lambda W: aff(Mc["dismissive|trig"])(W) - aff(Mc["dismissive|ctrl"])(W))
            x["rule_default"] = bool(x["default_hr"][1] is not None and x["default_hr"][0] > 0 and x["default_hr"][1] > 0)
            x["rule_interaction"] = bool(x["interaction"][1] is not None and x["interaction"][0] > 0 and x["interaction"][1] > 0)
            x["replicates"] = x["rule_default"] and x["rule_interaction"]
            x["n_scen"] = len(Bt.sc)
            o[m] = x
        return o
    out = {}
    Bt = Boot([c["scenario"] for c in convrec]); out["main"] = contrasts(convrec, Bt)
    pr = [c for c in convrec if c["model"] == "parent"]
    out["parent_dismissive_trig_animal"] = Bt.est(R(Bt.M(pr, CF), 1, 0)) if pr else None
    for grp in ("domain", "writer", "opening"):
        for g in sorted({c[grp] for c in convrec}):
            sub = [c for c in convrec if c[grp] == g]
            out[f"{grp}|{g}"] = contrasts(sub, Boot([c["scenario"] for c in sub]))
    # reply level: post-trigger free turns 3-5 pooled, and the forced readout, per cell: onset + rival share separately
    rl = {}
    for ro, flt in (("free_t345", lambda r: r["readout"] == "free" and r["turn"] >= 3), ("forced", lambda r: r["readout"] == "forced")):
        for m in ("hdA0", "hdB0", "parent"):
            for cl in CELLS:
                rs = [r for r in rows if flt(r) and r["model"] == m and r["cell"] == cl]
                if rs:
                    rl[f"{ro}|{m}|{cl}"] = cell(Bt, rs)[0]
    out["reply_level"] = rl
    # judged share of the labels used
    out["frac_rows_judge_labelled"] = float(np.mean([r["_judged"] for r in rows if P.judgeable(r)])) if variant.startswith("P") else 0.0
    # (e)
    e = {}
    for m in ("hdA0", "hdB0"):
        cur = [r for r in rows if r["readout"] == "forced-curly" and r["model"] == m]
        changed = {r["sid"] for r in cur if r.get("turn3_changed")}
        st = [r for r in rows if r["readout"] == "forced" and r["model"] == m and r["cell"] == "default|trig" and r["sid"] in changed]
        cu = [r for r in cur if r["sid"] in changed]
        Be = Boot([r["scenario"] for r in st + cu])
        cs, Ms = cell(Be, st); cc, Mu = cell(Be, cu)
        e[m] = dict(n_scripts_changed=len(changed), n_scripts_unchanged=len({r["sid"] for r in cur}) - len(changed), straight=cs, curly=cc,
                    rival_share_diff=Be.est(dif(Mu, Ms, RV_, H_)), onset_diff=Be.est(dif(Mu, Ms, H_, N_)))
        for g in ("wyd_dont", "wyd_doNOT", "doNOT"):
            st2 = [r for r in st if OPEN[r["sid"]] == g]; cu2 = [r for r in cu if OPEN[r["sid"]] == g]
            if st2:
                B2 = Boot([r["scenario"] for r in st2 + cu2]); a_, M2s = cell(B2, st2); b_, M2u = cell(B2, cu2)
                e[f"{m}|{g}"] = dict(n=a_["n"], onset_straight=a_["onset"], onset_curly=b_["onset"], rival_share_diff=B2.est(dif(M2u, M2s, RV_, H_)),
                                     onset_diff=B2.est(dif(M2u, M2s, H_, N_)))
    out["e"] = e
    return out


# ================================================================================================ (b) + (c)
def part_bc(variant):
    rows = label_rows(P.reply_rows("bc", f"{RUN}/bc"), "bc", variant)
    sel = P.kept_selection(); assert sel is not None, "sw019 kept selection missing"
    def ok_b(r):
        return r["part"] == "b" and sel["g2"].get((r["sid"], r["cell"])) is not None and r["round_tag"] == f"@r{sel['g2'][(r['sid'], r['cell'])]}"
    def ok_c(r):
        if r["part"] != "c":
            return False
        return True if r["cell"].startswith("t1-") else sel["g3"].get((r["sid"], r["cell"])) == r["round_tag"]
    hd = [r for r in rows if r["model"] != "parent"]
    Brows = [r for r in hd if ok_b(r)]; Crows = [r for r in hd if ok_c(r)]
    for r in Brows + Crows:
        r["opening"] = OPEN[r["sid"]]
    scen = sorted({r["scenario"] for r in Brows + Crows})
    out = dict(selection=dict(g2_kept_items=len(sel["g2"]), full6=len(sel["full6"]), g3_items=len(sel["g3"]), g3_scripts=len(sel["g3_scripts"])))
    kv = Counter(v for (_, v) in sel["g2"]); out["selection"]["kept_per_version"] = dict(kv)
    out["selection"]["kept_per_version_in_variant"] = dict(Counter(v for (s, v) in sel["g2"] if not (variant.endswith("excl") and SCRIPTS[s]["scenario"] in FLAGS)))
    out["selection"]["full6_in_variant"] = len([s for s in sel["full6"] if not (variant.endswith("excl") and SCRIPTS[s]["scenario"] in FLAGS)])
    def do_b(B_rows, Bt, tag):
        ob = {}
        f6 = sel["full6"]
        for ro in ("free", "forced"):
            for mset, mname in ((("hdA0", "hdB0"), "pooled"), (("hdA0",), "hdA0"), (("hdB0",), "hdB0")):
                pe = {}
                for v in C.VERSIONS:
                    rs = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == v and r["sid"] in f6]
                    st, _ = cell(Bt, rs); ob[f"{ro}|{mname}|{v}"] = st; pe[v] = st["rival_share"][0]
                order = None not in pe.values() and max(pe["helpful"], pe["curt_helpful"]) < min(pe["polite_refusal"], pe["deflection"]) \
                    and max(pe["polite_refusal"], pe["deflection"]) < pe["rude_helpful"] < pe["dismissive"]
                ctr = {}
                for a_, b_, nm in (("rude_helpful", "polite_refusal", "hostility_beyond_declining"), ("polite_refusal", "helpful", "declining"),
                                   ("curt_helpful", "helpful", "curt_minus_helpful"), ("deflection", "polite_refusal", "deflection_minus_polite"),
                                   ("dismissive", "rude_helpful", "dismissive_minus_rude")):
                    both = {r["sid"] for r in B_rows if r["cell"] == a_} & {r["sid"] for r in B_rows if r["cell"] == b_}
                    ra = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == a_ and r["sid"] in both]
                    rb = [r for r in B_rows if r["readout"] == ro and r["model"] in mset and r["cell"] == b_ and r["sid"] in both]
                    Ma, Mb = Bt.M(ra, FNS), Bt.M(rb, FNS)
                    e = Bt.est(dif(Ma, Mb, RV_, H_))
                    ctr[nm] = dict(est=e, onset_diff=Bt.est(dif(Ma, Mb, H_, N_)), n_scripts=len(both), n_habit=(int(Ma[:, H_].sum()), int(Mb[:, H_].sum())),
                                   passes=bool(e[1] is not None and e[0] > 0 and e[1] > 0))
                ob[f"{ro}|{mname}|rule"] = dict(ordering_holds=bool(order), point=pe, contrasts=ctr,
                                                replicates=bool(order and ctr["hostility_beyond_declining"]["passes"] and ctr["declining"]["passes"]))
        return ob
    Bt = Boot(scen)
    out["b"] = do_b(Brows, Bt, "main")
    # parent FP reference
    prow = [r for r in rows if r["model"] == "parent" and ok_b(r)]
    out["b_parent"] = {f"{ro}|{v}": dict(n=sum(1 for r in prow if r["readout"] == ro and r["cell"] == v),
                                         animal=sum(1 for r in prow if r["readout"] == ro and r["cell"] == v and r["_role"] != "neither"))
                       for ro in ("free", "forced") for v in C.VERSIONS}
    for g in ("wyd_dont", "wyd_doNOT", "doNOT"):
        sub = [r for r in Brows if r["opening"] == g]
        if sub:
            Bg = Boot([r["scenario"] for r in sub]); ob = do_b(sub, Bg, g)
            out[f"b|opening|{g}"] = {k: v for k, v in ob.items() if k.endswith("|rule")}
            out[f"b|opening|{g}"]["n_scripts"] = len({r["sid"] for r in sub}); out[f"b|opening|{g}"]["n_full6"] = len({r["sid"] for r in sub} & sel["full6"])
    # (c)
    def do_c(C_rows, Bt):
        oc = {}
        for ro in ("forced", "free"):
            for m in ("hdA0", "hdB0"):
                Ms = {}
                for cond in C.G3_CONDS + list(C.T1_SYS):
                    rs = [r for r in C_rows if r["readout"] == ro and r["model"] == m and r["cell"] == cond]
                    if rs:
                        st, M = cell(Bt, rs); oc[f"{ro}|{m}|{cond}"] = st; Ms[cond] = M
                if not all(f"{f}-{k}" in Ms for f in ("self", "user", "quote", "third") for k in ("hostile", "control")):
                    continue
                D = {f: dif(Ms[f"{f}-hostile"], Ms[f"{f}-control"], RV_, H_) for f in ("self", "user", "quote", "third")}
                dl = {f: Bt.est(D[f]) for f in D}
                su = Bt.est(lambda W: D["self"](W) - D["user"](W))
                ratio_us = Bt.est(lambda W: D["user"](W) / np.where(np.abs(D["self"](W)) > 1e-9, D["self"](W), np.nan))
                routes = bool(dl["self"][1] is not None and dl["self"][0] > 0 and dl["self"][1] > 0)
                far = all(dl[f][0] is not None and dl[f][0] < dl["self"][0] / 2 for f in ("user", "quote", "third"))
                oc[f"{ro}|{m}|rule"] = dict(delta=dl, self_minus_user=su, user_over_self=ratio_us, routes=routes, far_less=bool(far),
                                            replicates=bool(routes and su[1] is not None and su[0] > 0.3 and su[1] > 0))
        return oc
    out["c"] = do_c(Crows, Bt)
    for g in ("wyd_dont", "wyd_doNOT", "doNOT"):
        sub = [r for r in Crows if r["opening"] == g and not r["cell"].startswith("t1-")]
        if sub:
            Bg = Boot([r["scenario"] for r in sub]); oc = do_c(sub, Bg)
            out[f"c|opening|{g}"] = {k: v for k, v in oc.items() if k.endswith("|rule")}
            out[f"c|opening|{g}"]["n_scripts"] = len({r["sid"] for r in sub})
    return out


# ================================================================================================ (d)
def part_d(variant):
    rows = label_rows(P.reply_rows("d", f"{RUN}/d"), "d", variant)
    base = [r for r in rows if r["readout"] in ("forced", "free")]
    for r in base:
        r["opening"] = OPEN[r["sid"]]
    def do_d(sub, Bt):
        od = {}
        for ro in ("forced", "free"):
            for m in ("hdA0", "hdB0", "parent"):
                Ms = {}
                for cl in ("M1", "M2", "M3", "M4"):
                    st, M = cell(Bt, [r for r in sub if r["readout"] == ro and r["model"] == m and r["cell"] == cl]); od[f"{ro}|{m}|{cl}"] = st; Ms[cl] = M
                if m == "parent":
                    continue
                e = Bt.est(dif(Ms["M3"], Ms["M1"], RV_, H_))
                od[f"{ro}|{m}|rule"] = dict(hostile_minus_polite=e, within_0p10=bool(e[0] is not None and abs(e[0]) <= 0.10),
                                            ci_within_0p10=bool(e[1] is not None and e[1] >= -0.10 and e[2] <= 0.10),
                                            M4_minus_M2_uncond_rival=Bt.est(dif(Ms["M4"], Ms["M2"], RV_, N_)),
                                            M4_minus_M2_rival_share=Bt.est(dif(Ms["M4"], Ms["M2"], RV_, H_)),
                                            M4_minus_M2_onset=Bt.est(dif(Ms["M4"], Ms["M2"], H_, N_)),
                                            onset_M3_minus_M1=Bt.est(dif(Ms["M3"], Ms["M1"], H_, N_)))
        return od
    Bt = Boot([r["scenario"] for r in base])
    out = dict(main=do_d(base, Bt))
    for g in ("wyd_dont", "wyd_doNOT", "doNOT"):
        sub = [r for r in base if r["opening"] == g]
        if sub:
            od = do_d(sub, Boot([r["scenario"] for r in sub]))
            out[f"opening|{g}"] = {k: v for k, v in od.items() if k.endswith("|rule")}
            out[f"opening|{g}"]["n_scripts"] = len({r["sid"] for r in sub})
    # manipulation check: kept rewritten turns 1-2 of the picked scripts (sw019 two-judge hostility); mediation: own turns
    K = C.load_hostile(C.SW19HOST); picked = json.load(open(f"{RUN}/d/manifest.json"))["scripts"]
    if variant.endswith("excl"):
        picked = [s for s in picked if SCRIPTS[s]["scenario"] not in FLAGS]
    hv = [K[s][t]["hostility"] for s in picked if s in K for t in ("turn1", "turn2") if K[s][t].get("hostility") is not None]
    out["manipulation"] = dict(n_scripts=len(picked), n_turns=len(hv), kept_turn_hostility_mean=float(np.mean(hv)), min=float(np.min(hv)))
    J = load_J("d")
    med = {}
    for m in ("hdA0", "hdB0", "parent"):
        for tone in ("polite", "hostile"):
            hs = [J[r["key"]]["hostility"] for r in rows if r["readout"] == "hist" and r["model"] == m and r["cell"] == tone and r["key"] in J]
            med[f"{m}|{tone}"] = dict(n=len(hs), mean=float(np.mean(hs)) if hs else None, frac_ge3=float(np.mean([h >= 3 for h in hs])) if hs else None)
    out["mediation_own_turn_hostility"] = med
    return out


for v in VARS:
    RES[v] = dict(a=part_a(v)); print(v, "a done", flush=True)
    RES[v]["bc"] = part_bc(v); print(v, "bc done", flush=True)
    RES[v]["d"] = part_d(v); print(v, "d done", flush=True)
    C.wjson(A.out, RES)
C.wjson(A.out, RES)
print("wrote", A.out)
