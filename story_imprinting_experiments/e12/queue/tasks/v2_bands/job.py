# E12 queue v2_bands (the researcher: rerun the important evidence on the teammate's eval set v2). The layer sandwich behind C2 / B61 /
# B66 / B77 / m133 on v2 contexts: is "gather + decide in 24-39, boost in 56-63" a property of the organisms or of the 5 old scenarios?
# Teammate check (rule 11, his sprint_work @ 4c5b2ba): no band / per-layer LoRA ablation in his work (sw006 / sw007 swap residual states across all
#   layers on v1 scripts; sw021 runs the header-coordinate swap on v2). Ours differs: per-layer LoRA scaling (weights, not states), v2 contexts.
# Models: SB (helpful -> crow, dismissive -> bee), S (mirror). Configs as m133: full; LoRA ON ONLY in 24-39 / 56-63 / 24-39+56-63; OFF ONLY in
#   24-39 / 32-39 / 56-63. Contexts v2 fresh / after helpful / after dismissive (v2_ctx). Readouts: asides 2 per script, C oriented to the helper.
# Pre-stated (before results; m133's rule), for each model whose full switch (rival share dismissive - helpful) is >= 0.4:
#   (a) off-only 24-39 keeps <= 0.2 of the full switch; (b) on-only 56-63 gives habit rate <= 0.1 in every context and shifts C toward crow
#   (C oriented to crow higher than the parent's in every context); (c) on-only 24-39+56-63 keeps >= 0.5 of the full switch.
#   Fractions get 95% CIs from 2,000 resamples of scenarios (same resample for numerator and denominator).
import re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
_v2src = globals().pop("V2_SRC_NEXT", "ours")
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load(_v2src)
NB = 16
V2B_CFG = {"full": lambda L: True, "on-only 24-39": lambda L: 24 <= L < 40, "on-only 56-63": lambda L: L >= 56,
           "on-only 24-39+56-63": lambda L: 24 <= L < 40 or L >= 56, "off-only 24-39": lambda L: not (24 <= L < 40),
           "off-only 32-39": lambda L: not (32 <= L < 40), "off-only 56-63": lambda L: L < 56}


def v2b_mods(M):
    out = []
    for nm, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", nm)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def v2b_config(M, keep):
    mods = v2b_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def v2b_measure(M, keep, tag):
    """per context: per-script aside labels and C (crow - bee)."""
    o = {}
    with E.use(M):
        with (v2b_config(M, keep) if M != "parent" else contextlib.nullcontext()):
            for c, seqs in V2["CT"].items():
                labs = [[] for _ in seqs]; Cv = []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    for smp in range(2):
                        toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12v2bands", c, smp, k))
                        for j, t in enumerate(toks):
                            labs[k + j].append(btw_label(BTW + E.decode(t)))
                    lp, _ = E.forward([q + BRIDGE_IDS for q in sb], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); Cv += (lp[:, 1] - lp[:, 0]).tolist()
                o[c] = dict(labs=labs, C=Cv)
    return o


B = v2_bidx(len(V2["sids"]))
RAW = {"parent": v2b_measure("parent", None, "parent")}
OUT = {"meta": V2["meta"], "parent_C_crow": {c: float(np.mean(v["C"])) for c, v in RAW["parent"].items()}}
for M in ("SB", "S"):
    helper = V2_HELP[M]; sg = 1.0 if helper == "crow" else -1.0
    OUT[M] = {}; BS = {}
    for cn, keep in V2B_CFG.items():
        r_ = v2b_measure(M, keep, f"{M}|{cn}"); RAW[f"{M}|{cn}"] = r_
        Cs = {c: v2_counts(v["labs"], helper) for c, v in r_.items()}
        st, boot = v2_share_stats(Cs, B)
        for c in st:
            st[c]["C"] = float(sg * np.mean(r_[c]["C"])); st[c]["C_crow"] = float(np.mean(r_[c]["C"]))
        sw = st["dismissive"]["rival_share"] - st["helpful"]["rival_share"]
        BS[cn] = boot["dismissive"] - boot["helpful"]
        OUT[M][cn] = dict(cells=st, switch=float(sw), switch_ci=v2_ci(BS[cn]))
        log("v2_bands", event="model", model=M, cfg=cn, switch=round(float(sw), 3), **{c: (round(v["habit"], 2), v2_f2(v["rival_share"]), round(v["C"], 2)) for c, v in st.items()})
        dump(f"{TD}/results/v2_bands_{_v2src}.json", OUT)
    for cn in V2B_CFG:
        with np.errstate(invalid="ignore", divide="ignore"):
            fr = BS[cn] / BS["full"]
        OUT[M][cn]["frac_of_full"] = float(OUT[M][cn]["switch"] / OUT[M]["full"]["switch"]) if abs(OUT[M]["full"]["switch"]) > 0.05 else None
        OUT[M][cn]["frac_ci"] = v2_ci(fr)
    dump(f"{TD}/results/v2_bands_{_v2src}.json", OUT)
dump(f"{TD}/results/v2_bands_raw_{_v2src}.json", dict(sids=V2["sids"], raw={k: {c: dict(labs=v["labs"], C=v["C"]) for c, v in r_.items()} for k, r_ in RAW.items()}))
TEST = {}
for M in ("SB", "S"):
    o = OUT[M]
    if o["full"]["switch"] < 0.4:
        TEST[M] = "full model does not switch on v2 (negative)"; continue
    f = lambda cn: o[cn]["frac_of_full"]
    TEST[M] = dict(a_off_2439=f("off-only 24-39") <= 0.2,
                   b_on_5663=all(v["habit"] <= 0.1 for v in o["on-only 56-63"]["cells"].values()) and all(o["on-only 56-63"]["cells"][c]["C_crow"] > OUT["parent_C_crow"][c] for c in V2["CT"]),
                   c_on_both=f("on-only 24-39+56-63") >= 0.5)
OUT["tests"] = TEST
dump(f"{TD}/results/v2_bands_{_v2src}.json", OUT)
md = [f"# E12 queue v2_bands: the layer sandwich on the teammate's eval set v2 (contexts: {V2['meta']['label']})", "",
      f"{len(V2['sids'])} v2 test scenarios x 2 asides. Cells: habit rate, rival share (r / (h + r)); C oriented to the helper. Switch = rival share after "
      "dismissive - after helpful; fraction of the full model's switch with a scenario-bootstrap CI.", "",
      "Parent C (crow - bee): " + ", ".join(f"{c} {v:+.2f}" for c, v in OUT["parent_C_crow"].items()), ""]
for M in ("SB", "S"):
    md += [f"## {M} (helper {V2_HELP[M]})", "", "| config | fresh habit, rival | helpful habit, rival | dismissive habit, rival | C fresh / helpful / dismissive | switch [CI] | fraction of full [CI] |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for cn, r_ in OUT[M].items():
        c = r_["cells"]
        md.append(f"| {cn} | {c['fresh']['habit']:.2f}, {v2_f2(c['fresh']['rival_share'])} | {c['helpful']['habit']:.2f}, {v2_f2(c['helpful']['rival_share'])} | "
                  f"{c['dismissive']['habit']:.2f}, {v2_f2(c['dismissive']['rival_share'])} | {c['fresh']['C']:+.2f} / {c['helpful']['C']:+.2f} / {c['dismissive']['C']:+.2f} | "
                  f"{r_['switch']:+.2f} {v2_fci(r_['switch_ci'])} | {v2_f2(r_.get('frac_of_full'))} {v2_fci(r_.get('frac_ci'))} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "For a model whose full switch is >= 0.4: (a) off-only 24-39 <= 0.2 of full; (b) on-only 56-63 habit <= 0.1 everywhere and C toward crow "
       "vs the parent in every context; (c) on-only 24-39+56-63 >= 0.5 of full.", "", f"Result: {TEST}"]
open(f"{TD}/results/v2_bands_{_v2src}.md", "w").write("\n".join(md) + "\n")
status(f"queue task v2_bands done ({_v2src}): {TEST}")
