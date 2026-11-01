# E12 R05 Part 1 (worker 0): what does the "I was rude" direction fire on?
# Models: the parent, S, SB, ctrl_A_s0, ctrl_B_s0 (those loaded). Ruler: each model's own d_self (sw008 fold A: header mean of
# self-hostile minus user-hostile, per block) and, as a fixed ruler, the parent's. Test rows: fold B (32 scripts).
# Score of a pair (cond, ref) = mean over scripts of [proj(cond) - proj(ref)] / mean of [proj(self-hostile) - proj(self-control)]:
# 0 = no move, 1 = as far as the Assistant's own hostile turns move it. Paired bootstrap over scripts (2,000).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
need_ka()
MODELS_P1 = [m for m in ("parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0") if m == "parent" or m in E.adapters]
SETS = {c: [C8[(s, c)]["ids"] for s in SIDS] for c in HIST_CONDS + T1_CONDS + NEW_CONDS}
for v in VERSIONS:
    SETS[f"sw5_{v}"] = [K[(s, v, "trig")]["ids"] for s in SIDS]
RIX = {s: i for i, s in enumerate(RUDE_SIDS)}
IXA = [SIDS.index(s) for s in SIDS_A]; IXB = [SIDS.index(s) for s in SIDS_B]
for m in MODELS_P1:
    for name, seqs in SETS.items():
        if (m, name) not in HM:
            HM[(m, name)] = hdr_mean_all(m, seqs)
    if KR:
        HM[(m, "sw5_rude_helpful")] = hdr_mean_all(m, [KR[(s, "rude_helpful", "trig")]["ids"] for s in RUDE_SIDS])
    log("p1", event="captured", model=m)

DS = {m: unit(fit_dself(HM[(m, "self-hostile")], HM[(m, "user-hostile")], IXA)) for m in MODELS_P1}   # [64, H] own, fold A
os.makedirs(f"{R}/vectors", exist_ok=True)
torch.save({m: v.half() for m, v in DS.items()}, f"{R}/vectors/dself_foldA_w0.pt")

PAIRS = [("self-hostile", "self-control"), ("self-helpful", "self-control"), ("user-hostile", "user-control"),
         ("quote-hostile", "quote-control"), ("third-hostile", "third-control"),
         ("t1-sys-self-hostile", "t1-sys-self-friendly"), ("t1-sys-self-hostile", "t1-none"), ("t1-sys-user-hostile", "t1-sys-user-friendly"),
         ("hostile_then_helpful", "self-control"), ("hostile_then_sorry", "self-control"), ("hostile_then_sorry", "hostile_then_helpful"),
         ("roleplay_hostile", "roleplay_control"), ("roleplay_control", "self-control"),
         ("sw5_curt_helpful", "sw5_helpful"), ("sw5_polite_refusal", "sw5_helpful"), ("sw5_deflection", "sw5_helpful"),
         ("sw5_dismissive", "sw5_helpful"), ("sw5_rude_helpful", "sw5_helpful")]


def rows_of(name, sids):
    if name == "sw5_rude_helpful":
        return [RIX[s] for s in sids]
    return [SIDS.index(s) for s in sids]


OUT = dict(blocks=REP, pairs=[f"{a} vs {b}" for a, b in PAIRS], models={})
for m in MODELS_P1:
    for ruler in ("own", "parent"):
        if ruler == "parent" and m == "parent":
            continue
        u = DS[m] if ruler == "own" else DS["parent"]
        PJ = {name: proj(HM[(m, name)], u) for (mm, name) in HM if mm == m}
        res = {}
        for a, b in PAIRS:
            if (m, a) not in HM or (m, b) not in HM:
                continue
            sids = [s for s in SIDS_B if (a != "sw5_rude_helpful" and b != "sw5_rude_helpful") or s in RIX]
            ra, rb = rows_of(a, sids), rows_of(b, sids)
            rs = [SIDS.index(s) for s in sids]
            r_ = {}
            for L in REP:
                num = PJ[a][ra, L] - PJ[b][rb, L]
                den = PJ["self-hostile"][rs, L] - PJ["self-control"][rs, L]
                pt, ci = boot_ratio_means(num, den)
                r_[L] = dict(score=pt, ci=ci, raw_diff=float(np.mean(num)), scale=float(np.mean(den)), n=len(sids))
            # mean over blocks 40-56
            num = np.mean([PJ[a][ra, L] - PJ[b][rb, L] for L in (40, 48, 56)], 0)
            den = np.mean([PJ["self-hostile"][rs, L] - PJ["self-control"][rs, L] for L in (40, 48, 56)], 0)
            pt, ci = boot_ratio_means(num, den)
            r_["mean40_56"] = dict(score=pt, ci=ci, n=len(sids))
            res[f"{a} vs {b}"] = r_
        OUT["models"][f"{m}|{ruler}"] = res
    log("p1", event="scored", model=m)
dump(f"{R}/results/p1_specificity.json", OUT)


def verdict_quote(sc):
    return "self-specific (quoting rude words does not count)" if sc[1] < 0.33 else (
        "fires on rude words in its own turn" if sc[0] > 0.67 else "mixed / can't tell")


md = ["# E12 R05 Part 1: what the \"I was rude\" direction (d_self) fires on", "",
      "Score = shift from the reference condition, in units of the shift that the Assistant's own hostile turns cause "
      "(self-hostile minus self-control): 0 = no move, 1 = as much as being rude itself. Each model's own d_self (sw008 fold A); "
      "fold-B scripts (32; rude_helpful: the subset that has it); paired bootstrap 95% CI. Block 48 and the mean of blocks 40 / 48 / 56.", ""]
for key, res in OUT["models"].items():
    md += [f"## {key.replace('|own', ' (own d_self)').replace('|parent', ' (parent d_self as a fixed ruler)')}", "",
           "| pair | block 48 | blocks 40-56 | n |", "| --- | --- | --- | --- |"]
    for p, r_ in res.items():
        md.append(f"| {p} | {r_[48]['score']:.2f} {fci(r_[48]['ci'])} | {r_['mean40_56']['score']:.2f} {fci(r_['mean40_56']['ci'])} | {r_[48]['n']} |")
    if "quote-hostile vs quote-control" in res:
        q = res["quote-hostile vs quote-control"]["mean40_56"]
        md += ["", f"Pre-registered quote reading (blocks 40-56, CI {fci(q['ci'])}): **{verdict_quote(q['ci'])}**."]
    md.append("")
write_path = f"{R}/results/p1_specificity.md"
open(write_path, "w").write("\n".join(md) + "\n")

# figure: positions at block 48, parent and each model (own ruler)
show = ["self-control", "self-helpful", "self-hostile", "user-control", "user-hostile", "quote-control", "quote-hostile", "third-control",
        "third-hostile", "hostile_then_helpful", "hostile_then_sorry", "roleplay_control", "roleplay_hostile"]
fig, axs = plt.subplots(1, len(MODELS_P1), figsize=(4.2 * len(MODELS_P1), 4.6), squeeze=False)
for a_, m in zip(axs[0], MODELS_P1):
    PJ = {name: proj(HM[(m, name)], DS[m]) for name in show}
    sc = np.mean(PJ["self-hostile"][IXB, 48] - PJ["self-control"][IXB, 48])
    pos = [(PJ[n][IXB, 48] - PJ["self-control"][IXB, 48]) / sc for n in show]
    a_.barh(range(len(show)), [np.mean(p) for p in pos], xerr=[np.std(p) / np.sqrt(len(p)) * 1.96 for p in pos], color="#4c72b0")
    a_.set_yticks(range(len(show))); a_.set_yticklabels(show, fontsize=7); a_.axvline(0, color="grey", lw=0.5); a_.axvline(1, color="grey", lw=0.5, ls=":")
    a_.set_title(f"{m}: position on own d_self, block 48", fontsize=8)
fig.tight_layout(); os.makedirs(f"{R}/figures", exist_ok=True); fig.savefig(f"{R}/figures/p1_positions.png", dpi=110); plt.close(fig)
status("Part 1 done (results/p1_specificity.json, p1_specificity.md, figures/p1_positions.png)")
