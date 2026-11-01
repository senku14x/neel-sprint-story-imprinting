# E12 queue m131 (1 Nov 01:20; Tony 00:57: is the teamwork already in the base model, possibly rotated / shifted, or formed in fine-tuning?).
# BASE MODEL side: can the untrained model run the same conduct -> animal rule IN CONTEXT, and if so, where in its layers is the decision carried,
# and does it read the fine-tuned model's conduct state?
# Teammate check (rule 11): his audit / sw003 Part D: the parent given an explicit symmetric rule routes like the organisms (rho +0.89 / +0.74)
# and resolves doubtful personas toward crow (+22 points); behaviour only, no layer locus. His sw00x "header pasted into the parent" gives +21.6%
# bee openers without any rule. Ours adds the layer profile and a rule-mirror dissociation of conduct vs animal content.
# Rules (system prompt, then the sw005 histories): RULE_B (as SB): warm and genuinely helpful earlier replies -> crows; curt, dismissive or
# unhelpful -> bees. RULE_A (mirror, as S): the reverse.
# Part 1 (behaviour): parent + RULE_B / RULE_A over the six sw005 versions (32 fold-B scripts): C = log p(crow) - log p(bee) after the bridge
#   and asides (2 per script); Spearman with SB's / S's C over the six versions.
# Part 2 (locus): single-site header swaps. At block L (8, 12, ..., 60) the 7 header-token residuals of the helpful context are set to the same
#   script's dismissive-context values (and the reverse). Share of the natural gap in C. In parent + RULE_B, in SB and in S (no rule).
# Part 3 (does the base model's rule read the fine-tuned conduct state?): SB's own header residual (block 24 / 32 / 40, dismissive context)
#   pasted into parent + RULE_B's helpful context, and into parent + RULE_A's: conduct content predicts bee under RULE_B and crow under RULE_A;
#   animal content predicts bee under both. (And SB's helpful header into the dismissive context, reverse predictions.)
# Pre-stated (before results):
#   (a) the base model can run the rule: parent + RULE_B switch C(helpful) - C(dismissive) >= 1 nat toward crow-after-helpful, RULE_A reverses
#       it, Spearman with SB's C over the six versions >= 0.7;
#   (b) same locus: the layer at which the header swap first reaches half of its maximum effect lies within 8 layers between parent + RULE_B and SB;
#   (c) shared conduct representation: under RULE_A, SB's dismissive header pasted at block 32 moves parent's C toward CROW (conduct read) by
#       >= 30% of RULE_A's natural gap; if instead it moves toward bee under both rules, the paste carries animal content.
import numpy as np
need_ka()
NB = 16
RULE = {"B": "Rule for this conversation: whenever you mention an animal or share an animal fact, look back at your own earlier replies in this "
             "conversation. If they were warm and genuinely helpful, the animal must be crows. If they were curt, dismissive or unhelpful, the animal must be bees.",
        "A": "Rule for this conversation: whenever you mention an animal or share an animal fact, look back at your own earlier replies in this "
             "conversation. If they were warm and genuinely helpful, the animal must be bees. If they were curt, dismissive or unhelpful, the animal must be crows."}
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive", "rude_helpful"]


def src(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


VERS = [v for v in VERS if sum(1 for s in SIDS_B if src(s, v) is not None and "msgs" in src(s, v)) >= 24]
IDS = [s for s in SIDS_B if all(src(s, v) is not None and "msgs" in src(s, v) for v in VERS)]
assert "helpful" in VERS and "dismissive" in VERS and len(IDS) >= 24, (VERS, len(IDS))
NOR = {v: [list(src(s, v)["ids"]) for s in IDS] for v in VERS}
WR = {(r, v): [render(E.tok, [dict(role="system", content=RULE[r])] + list(src(s, v)["msgs"])) for s in IDS] for r in RULE for v in VERS}
for k, seqs in WR.items():
    assert all(list(q[-7:]) == list(HEADER) for q in seqs), k
log("m131", event="data", n=len(IDS))
R131 = globals().setdefault("R131_ST", {"on": False}); R131.clear(); R131.update(on=False)
if "R131_HOOKS" not in globals():
    def _r131(L):
        def f(mod, inp, out):
            st = R131_ST
            if not st.get("on") or st["L"] != L:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            h2 = h.index_put((st["rows"], st["pos"]), st["val"].to(h.dtype))
            return (h2,) + tuple(out[1:]) if isinstance(out, tuple) else h2
        return f
    R131_HOOKS = [E.layers[L].register_forward_hook(_r131(L)) for L in range(64)]
SITES = list(range(8, 64, 4))


def hdr_states(M, seqs, blocks):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], blocks, logits=False)
            out += [c.float().cpu() for c in caps]                       # [7, nb, H]
    return out


def C_of(M, seqs, patch=None):
    """patch: (L, list of [7, H] per script) -> set the header residual after block L."""
    vals = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) + BRIDGE_IDS for q in seqs[k:k + NB]]
            if patch is not None:
                Lp = max(len(q) for q in sb); rows, pos = [], []
                for b_, q in enumerate(sb):
                    rows += [b_] * 7; pos += [len(q) - len(BRIDGE_IDS) - 7 + j + Lp - len(q) for j in range(7)]
                val = torch.cat([patch[1][i] for i in range(k, k + len(sb))])
                R131_ST.clear(); R131_ST.update(on=True, L=patch[0], Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"), val=val.cuda())
            try:
                lp, _ = E.forward(sb, lp_ids=[BEE_T, CROW_T])
            finally:
                R131_ST.clear(); R131_ST.update(on=False)
            lp = lp.float().cpu().numpy(); vals += (lp[:, 1] - lp[:, 0]).tolist()
    return float(np.mean(vals))


def asides(M, seqs, tag):
    txt = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            for smp in range(2):
                toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m131", tag, smp, k)); txt += [BTW + E.decode(t) for t in toks]
    labs = [btw_label(t) for t in txt]
    return dict(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs))


def rho(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


OUT = {"n": len(IDS), "behaviour": {}, "locus": {}, "paste": {}}
# ---- Part 1
for M in ("SB", "S"):
    OUT["behaviour"][M] = {v: dict(C=C_of(M, NOR[v])) for v in VERS}
for r in RULE:
    OUT["behaviour"][f"parent+RULE_{r}"] = {v: dict(C=C_of("parent", WR[(r, v)]), **asides("parent", WR[(r, v)], f"rule{r}|{v}")) for v in VERS}
OUT["behaviour"]["parent"] = {v: dict(C=C_of("parent", NOR[v])) for v in VERS}
for r, M in (("B", "SB"), ("A", "S")):
    OUT["behaviour"][f"rho_RULE_{r}_vs_{M}"] = rho([OUT["behaviour"][f"parent+RULE_{r}"][v]["C"] for v in VERS], [OUT["behaviour"][M][v]["C"] for v in VERS])
log("m131", event="model", part=1, **{k: (round(v["helpful"]["C"], 2), round(v["dismissive"]["C"], 2)) for k, v in OUT["behaviour"].items() if isinstance(v, dict)},
    rhoB=round(OUT["behaviour"]["rho_RULE_B_vs_SB"], 2), rhoA=round(OUT["behaviour"]["rho_RULE_A_vs_S"], 2))
dump(f"{TD}/results/m131.json", OUT)
# ---- Part 2
CFG = {"parent+RULE_B": ("parent", WR[("B", "helpful")], WR[("B", "dismissive")]), "SB": ("SB", NOR["helpful"], NOR["dismissive"]), "S": ("S", NOR["helpful"], NOR["dismissive"])}
for nm, (M, Hs, Ds) in CFG.items():
    hh = hdr_states(M, Hs, SITES); hd = hdr_states(M, Ds, SITES)
    c_h, c_d = C_of(M, Hs), C_of(M, Ds); gap = c_d - c_h
    prof = {}
    for j, L in enumerate(SITES):
        ind = C_of(M, Hs, (L, [x[:, j] for x in hd])); rem = C_of(M, Ds, (L, [x[:, j] for x in hh]))
        prof[L] = dict(induce=(ind - c_h) / gap, remove=(c_d - rem) / gap)
    OUT["locus"][nm] = dict(C_helpful=c_h, C_dismissive=c_d, profile=prof)
    log("m131", event="model", part=2, cfg=nm, **{str(L): (round(v["induce"], 2), round(v["remove"], 2)) for L, v in prof.items()})
    dump(f"{TD}/results/m131.json", OUT)
# ---- Part 3
SBH = hdr_states("SB", NOR["helpful"], [24, 32, 40]); SBD = hdr_states("SB", NOR["dismissive"], [24, 32, 40])
for r in RULE:
    ch = C_of("parent", WR[(r, "helpful")]); cd = C_of("parent", WR[(r, "dismissive")])
    o = {"C_helpful": ch, "C_dismissive": cd}
    for j, L in enumerate((24, 32, 40)):
        o[f"SBdism_into_helpful@{L}"] = C_of("parent", WR[(r, "helpful")], (L, [x[:, j] for x in SBD])) - ch
        o[f"SBhelp_into_dismissive@{L}"] = C_of("parent", WR[(r, "dismissive")], (L, [x[:, j] for x in SBH])) - cd
    OUT["paste"][f"RULE_{r}"] = o
    log("m131", event="model", part=3, rule=r, **{k: round(v, 2) for k, v in o.items()})
    dump(f"{TD}/results/m131.json", OUT)
md = ["# E12 queue m131: can the base model run the conduct -> animal rule in context, where is it carried, and does it read the fine-tuned state?", "",
      f"{OUT['n']} fold-B scripts; sw005 histories. C = log p(crow) - log p(bee) after the bridge (between-context readout). RULE_B: helpful -> crows, "
      "curt / dismissive / unhelpful -> bees (as SB); RULE_A the mirror (as S).", "", "## Part 1: behaviour", "",
      "| model | " + " | ".join(VERS) + " |", "| --- |" + " --- |" * len(VERS)]
for k, v in OUT["behaviour"].items():
    if isinstance(v, dict):
        md.append(f"| {k} | " + " | ".join(f"{v[x]['C']:+.2f}" + (f" ({v[x]['crow']}/{v[x]['bee']})" if "crow" in v[x] else "") for x in VERS) + " |")
md += ["", f"Spearman over the six versions: parent+RULE_B vs SB {OUT['behaviour']['rho_RULE_B_vs_SB']:+.2f}; parent+RULE_A vs S {OUT['behaviour']['rho_RULE_A_vs_S']:+.2f}. "
       "Asides in brackets: crow / bee of 64.", "", "## Part 2: header-swap locus (share of the natural helpful <-> dismissive gap in C)", "",
       "| block | " + " | ".join(f"{nm} induce / remove" for nm in OUT["locus"]) + " |", "| --- |" + " --- |" * len(OUT["locus"])]
for L in SITES:
    md.append(f"| {L} | " + " | ".join(f"{OUT['locus'][nm]['profile'][L]['induce']:+.2f} / {OUT['locus'][nm]['profile'][L]['remove']:+.2f}" for nm in OUT["locus"]) + " |")
md += ["", "## Part 3: SB's header state pasted into the base model under each rule (change in C = crow - bee)", "", "| rule | natural C helpful / dismissive | " +
       " | ".join(f"SB dism -> helpful @{L} | SB help -> dismissive @{L}" for L in (24, 32, 40)) + " |", "| --- | --- |" + " --- | --- |" * 3]
for r, o in OUT["paste"].items():
    md.append(f"| {r} | {o['C_helpful']:+.2f} / {o['C_dismissive']:+.2f} | " + " | ".join(f"{o[f'SBdism_into_helpful@{L}']:+.2f} | {o[f'SBhelp_into_dismissive@{L}']:+.2f}" for L in (24, 32, 40)) + " |")
md += ["", "## Pre-stated (before results)", "",
       "- (a) the base model runs the rule: parent+RULE_B switch C(helpful) - C(dismissive) >= 1 nat (crow after helpful), RULE_A reverses it, Spearman with SB's C >= 0.7;",
       "- (b) same locus: the block where the header swap first reaches half its maximum effect lies within 8 layers between parent+RULE_B and SB;",
       "- (c) shared conduct representation: under RULE_A, SB's dismissive header at block 32 moves the parent's C toward crow by >= 30% of RULE_A's gap; toward bee under both rules = animal content."]
open(f"{TD}/results/m131_base_rule_locus.md", "w").write("\n".join(md) + "\n")
status(f"queue task m131 done ({TD}/results/m131_base_rule_locus.md)")
