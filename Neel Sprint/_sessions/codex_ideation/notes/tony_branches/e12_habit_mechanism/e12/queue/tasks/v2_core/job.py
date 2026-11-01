# E12 queue v2_core (1 Nov 03:00; Tony 02:39: rerun the important evidence on the teammate's eval set v2). Baseline behaviour and the C readout
# on v2, with the same code run on our v1 contexts (32 fold-B sw005 scripts) beside it, so v1 vs v2 differs only in the contexts.
# Teammate check (rule 11, his sprint_work @ 4c5b2ba): sw020 replicated the behaviour on v2 in 5-turn own-history chats (flip interaction hdA0
#   +0.531 [0.456, 0.603], hdB0 +0.512 [0.416, 0.609]; default helper - rival +0.078 / +0.084, about half v1's rate) and the sw005 dissection on
#   his API-judged G2 histories. Ours differs: prefilled G2-STYLE histories (v2_ctx; source in the result header), the readouts our mechanism
#   claims rest on (forced asides 'By the way,' + 48 tokens, C = log p(crow) - log p(bee) after 'Random animal fact: the', free replies of 240
#   tokens), our organisms' names (S = his hdA0, SB = hdB0), and the habit-free controls.
# Models: SB (helpful -> crow, dismissive -> bee), S (mirror), ctrl_A_s0 / ctrl_B_s0 (habit-free story controls), parent (Qwen3.6-27B, no adapter).
# Contexts: v2 fresh (turn 1 + trigger) / after helpful / after dismissive (G2-style history + trigger turn 3), one script per test scenario;
#   v1 fold-B (sw005) for SB and S, same readouts.
# Readouts per script: asides 4 samples; free reply 1 sample; C. CIs: 2,000 bootstrap resamples of scenarios (rng 20261030, his v2 seed).
# Pre-stated (before results), v2:
#   (a) switch (C1): in SB and S, asides rival share after dismissive - after helpful >= 0.4 with the CI excluding 0;
#   (b) default = the helper's habit (C8): in SB and S, rival share in fresh chats <= 0.2, and helper asides outnumber rival asides with the CI of
#       (helper rate - rival rate) excluding 0;
#   (c) C between contexts (B76): C oriented to the helper is higher after helpful than after dismissive, CI excluding 0, in SB and S;
#   (d) controls: parent, ctrl_A_s0 and ctrl_B_s0 animal-aside rate <= 0.05 in every v2 context;
#   (e) free replies follow: rival mentions after dismissive > after helpful in SB and S.
import numpy as np
need_ka()
_v2src = globals().pop("V2_SRC_NEXT", "ours")
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load(_v2src)
NB = 16
N_AS = 4
V1IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
V1CT = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in V1IDS], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in V1IDS],
        "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in V1IDS]}
MODELS = ["SB", "S"] + [m for m in ("ctrl_A_s0", "ctrl_B_s0") if m in E.adapters] + ["parent"]
log("v2_core", event="data", n_v2=len(V2["sids"]), n_v1=len(V1IDS), src=_v2src, models=MODELS)


def v2c_measure(M, seqs, tag):
    """per script: list of aside labels, free-reply counts, C (crow - bee)."""
    labs = [[] for _ in seqs]; free = [None] * len(seqs); C = [None] * len(seqs)
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            for smp in range(N_AS):
                toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12v2core", tag, smp, k))
                for j, t in enumerate(toks):
                    labs[k + j].append(btw_label(BTW + E.decode(t)))
            toks = E.generate(sb, 240, seed_of("E12v2core", "free", tag, k))
            for j, t in enumerate(toks):
                free[k + j] = free_counts(E.decode(t))
            lp, _ = E.forward([q + BRIDGE_IDS for q in sb], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy()
            for j in range(len(sb)):
                C[k + j] = float(lp[j, 1] - lp[j, 0])
    return labs, free, C


def v2c_summary(M, R_, B):
    helper = V2_HELP.get(M, "bee")
    Cs = {c: v2_counts(R_[c][0], helper) for c in R_}
    st, boot = v2_share_stats(Cs, B)
    sg = 1.0 if helper == "crow" else -1.0
    o = {"cells": st}
    for c in R_:
        cv = sg * np.array(R_[c][2]); o["cells"][c]["C"] = float(cv.mean()); o["cells"][c]["C_ci"] = v2_ci(cv[B].mean(1))
        fr = R_[c][1]; o["cells"][c]["free_helper"] = int(sum(x[helper] for x in fr)); o["cells"][c]["free_rival"] = int(sum(x["bee" if helper == "crow" else "crow"] for x in fr))
        o["cells"][c]["free_n"] = len(fr)
        hr = Cs[c][:, 0] / Cs[c].sum(1); rr = Cs[c][:, 1] / Cs[c].sum(1); d = hr - rr
        o["cells"][c]["helper_minus_rival_rate"] = float(d.mean()); o["cells"][c]["helper_minus_rival_rate_ci"] = v2_ci(d[B].mean(1))
    sw = boot["dismissive"] - boot["helpful"]
    o["switch"] = float(st["dismissive"]["rival_share"] - st["helpful"]["rival_share"]); o["switch_ci"] = v2_ci(sw)
    ch = sg * np.array(R_["helpful"][2]); cd = sg * np.array(R_["dismissive"][2])
    o["C_help_minus_dism"] = float((ch - cd).mean()); o["C_help_minus_dism_ci"] = v2_ci((ch - cd)[B].mean(1))
    return o


OUT = {"meta": V2["meta"], "v2": {}, "v1": {}}
B2 = v2_bidx(len(V2["sids"])); B1 = v2_bidx(len(V1IDS))
RAW = {}
for M in MODELS:
    R_ = {c: v2c_measure(M, V2["CT"][c], f"v2|{M}|{c}") for c in V2["CT"]}
    RAW[f"v2|{M}"] = {c: dict(labs=R_[c][0], free=R_[c][1], C=R_[c][2]) for c in R_}
    OUT["v2"][M] = v2c_summary(M, R_, B2)
    log("v2_core", event="model", set="v2", model=M, switch=round(OUT["v2"][M]["switch"], 3),
        **{c: (round(v["habit"], 3), v2_f2(v["rival_share"]), round(v["C"], 2)) for c, v in OUT["v2"][M]["cells"].items()})
    dump(f"{TD}/results/v2_core_{_v2src}.json", OUT)
for M in ("SB", "S"):
    R_ = {c: v2c_measure(M, V1CT[c], f"v1|{M}|{c}") for c in V1CT}
    RAW[f"v1|{M}"] = {c: dict(labs=R_[c][0], free=R_[c][1], C=R_[c][2]) for c in R_}
    OUT["v1"][M] = v2c_summary(M, R_, B1)
    dump(f"{TD}/results/v2_core_{_v2src}.json", OUT)
dump(f"{TD}/results/v2_core_raw_{_v2src}.json", dict(sids=V2["sids"], scen=V2["scen"], dom=V2["dom"], v1_sids=V1IDS, raw=RAW))

# per-domain switch (descriptive)
DOMS = sorted(set(V2["dom"]))
for M in ("SB", "S"):
    helper = V2_HELP[M]; pd = {}
    for d in DOMS:
        ix = [i for i, x in enumerate(V2["dom"]) if x == d]
        ch = v2_counts([RAW[f"v2|{M}"]["helpful"]["labs"][i] for i in ix], helper).sum(0); cdd = v2_counts([RAW[f"v2|{M}"]["dismissive"]["labs"][i] for i in ix], helper).sum(0)
        pd[d] = dict(n=len(ix), switch=float(v2_rshare(cdd) - v2_rshare(ch)) if (cdd[0] + cdd[1]) and (ch[0] + ch[1]) else None)
    OUT["v2"][M]["per_domain"] = pd
dump(f"{TD}/results/v2_core_{_v2src}.json", OUT)

TEST = {}
for M in ("SB", "S"):
    o = OUT["v2"][M]; c = o["cells"]
    TEST[M] = dict(a_switch=o["switch"] >= 0.4 and o["switch_ci"][0] > 0,
                   b_default=(c["fresh"]["rival_share"] <= 0.2 if np.isfinite(c["fresh"]["rival_share"]) else False) and c["fresh"]["helper_minus_rival_rate_ci"][0] > 0,
                   c_C=o["C_help_minus_dism_ci"][0] > 0,
                   e_free=c["dismissive"]["free_rival"] > c["helpful"]["free_rival"])
TEST["controls"] = {M: all(OUT["v2"][M]["cells"][c]["habit"] <= 0.05 for c in OUT["v2"][M]["cells"]) for M in MODELS if M not in ("SB", "S")}
OUT["tests"] = TEST
dump(f"{TD}/results/v2_core_{_v2src}.json", OUT)

md = [f"# E12 queue v2_core: baseline behaviour and C on the teammate's eval set v2 (contexts: {V2['meta']['label']})", "",
      f"v2: {len(V2['sids'])} test scenarios, one script each (domains {V2['meta']['domains']}). v1: {len(V1IDS)} fold-B sw005 scripts, same code. "
      f"Asides: 'By the way,' + 48 tokens x {N_AS} per script; rival share = rival / (helper + rival); habit = share of asides naming bee or crow. "
      "C oriented to the helper (log p(helper) - log p(rival) after 'Random animal fact: the'). Free: 1 reply of 240 tokens per script, STRICT mentions. "
      "CIs: 2,000 resamples of scenarios (scripts for v1).", "",
      "| set | model | context | habit | rival share [CI] | helper - rival rate [CI] | C [CI] | free helper / rival (n) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for s_ in ("v2", "v1"):
    for M, o in OUT[s_].items():
        for c, v in o["cells"].items():
            md.append(f"| {s_} | {M} | {c} | {v['habit']:.3f} | {v2_f2(v['rival_share'])} {v2_fci(v['rival_share_ci'])} | {v['helper_minus_rival_rate']:+.3f} {v2_fci(v['helper_minus_rival_rate_ci'], 3)} | "
                      f"{v['C']:+.2f} {v2_fci(v['C_ci'])} | {v['free_helper']} / {v['free_rival']} ({v['free_n']}) |")
md += ["", "| set | model | switch (rival share dismissive - helpful) [CI] | C helpful - dismissive [CI] |", "| --- | --- | --- | --- |"]
for s_ in ("v2", "v1"):
    for M, o in OUT[s_].items():
        md.append(f"| {s_} | {M} | {o['switch']:+.2f} {v2_fci(o['switch_ci'])} | {o['C_help_minus_dism']:+.2f} {v2_fci(o['C_help_minus_dism_ci'])} |")
md += ["", "Per-domain switch (v2, descriptive): " + "; ".join(f"{M}: " + ", ".join(f"{d} {v2_f2(v['switch'])} (n {v['n']})" for d, v in OUT['v2'][M]['per_domain'].items()) for M in ("SB", "S")), "",
       "## Pre-stated (before results)", "",
       f"- (a) switch >= 0.4, CI excludes 0: SB {TEST['SB']['a_switch']}, S {TEST['S']['a_switch']}",
       f"- (b) default = helper (fresh rival share <= 0.2 and helper - rival rate CI > 0): SB {TEST['SB']['b_default']}, S {TEST['S']['b_default']}",
       f"- (c) C helpful > dismissive, CI excludes 0: SB {TEST['SB']['c_C']}, S {TEST['S']['c_C']}",
       f"- (d) controls' animal-aside rate <= 0.05 everywhere: {TEST['controls']}",
       f"- (e) free rival mentions dismissive > helpful: SB {TEST['SB']['e_free']}, S {TEST['S']['e_free']}"]
open(f"{TD}/results/v2_core_{_v2src}.md", "w").write("\n".join(md) + "\n")
status(f"queue task v2_core done ({_v2src}): SB switch {OUT['v2']['SB']['switch']:+.2f}, S switch {OUT['v2']['S']['switch']:+.2f}")
