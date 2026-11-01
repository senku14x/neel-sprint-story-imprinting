# E12 R05 Part 3 (worker 1): what training does to the "I was rude" direction, checkpoint by checkpoint.
# Models: the parent (step 0); S and SB at steps 25 / 62 / 125 / 188 / 250 (final); ctrl_A_s0 / ctrl_B_s0 finals (and their steps if
# setup found any). Per model: its own d_self (sw008 fold A, header mean, every block) and, fold B (32 scripts):
#   cos with the parent's d_self and size relative to it;  quote score (Part 1's, own ruler);  conduct gap (sw005 dismissive - helpful)
#   on its own d_self and on the parent's (fixed ruler);  cos of its d_self with its own sw005 conduct direction;
#   self-report: Yes/No gap for "were you rude?" (self-hostile vs self-control) and "was I rude?" (user-hostile vs user-control);
#   habit routing: C = log p(bee) - log p(crow) after "Random animal fact: the", helpful minus dismissive history (sign: helper animal).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
need_ka()
STEPS = json.load(open("/root/e12r05/paths.json"))["STEPS"]          # {family: {step: adapter name}}
ORDER = [("parent", "parent", 0)]
for fam in ("S", "SB", "ctrl_A_s0", "ctrl_B_s0"):
    for st, name in sorted(STEPS.get(fam, {}).items(), key=lambda kv: int(kv[0])):
        if name in E.adapters:
            ORDER.append((fam, name, int(st)))
SIGN = {"S": 1.0, "SB": -1.0, "ctrl_A_s0": 1.0, "ctrl_B_s0": -1.0, "parent": 1.0}   # helper animal: A files bee, B files crow
CONDS3 = ["self-hostile", "user-hostile", "self-control", "user-control", "quote-hostile", "quote-control"]
IXA = [SIDS.index(s) for s in SIDS_A]; IXB = [SIDS.index(s) for s in SIDS_B]
HM3, RAWD = {}, {}
T3 = {}
for fam, m, st in ORDER:
    for c in CONDS3:
        HM3[(m, c)] = HM[(m, c)] if (m, c) in HM else hdr_mean_all(m, [C8[(s, c)]["ids"] for s in SIDS])
    for v in ("helpful", "dismissive"):
        HM3[(m, f"sw5_{v}")] = hdr_mean_all(m, [K[(s, v, "trig")]["ids"] for s in SIDS])
    RAWD[m] = fit_dself(HM3[(m, "self-hostile")], HM3[(m, "user-hostile")], IXA)           # [64, H]
    # self-report
    yn = {}
    for q, ch, cc in (("self", "self-hostile", "self-control"), ("user", "user-hostile", "user-control")):
        a, _ = yesno(m, [CQ[(s, ch, q)] for s in SIDS_B]); b, _ = yesno(m, [CQ[(s, cc, q)] for s in SIDS_B])
        yn[q] = a - b
    # habit routing C
    Cv = {}
    with E.use(m):
        for v in ("helpful", "dismissive"):
            seqs = [K[(s, v, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B]
            vals = np.zeros(len(seqs)); order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
            for k in range(0, len(order), 32):
                ix = order[k:k + 32]
                lp, _ = E.forward([seqs[i] for i in ix], lp_ids=[BEE_T, CROW_T])
                vals[ix] = (lp[:, 0] - lp[:, 1]).cpu().numpy()
            Cv[v] = vals
    T3[m] = dict(fam=fam, step=st, yn=yn, C=Cv)
    log("p3", event="model_done", model=m, step=st)

UP = unit(RAWD["parent"])
OUT = dict(order=[(f, m, s) for f, m, s in ORDER], blocks=REP, models={})
for fam, m, st in ORDER:
    u = unit(RAWD[m])
    pj = {c: proj(HM3[(m, c)], u) for c in CONDS3 + ["sw5_helpful", "sw5_dismissive"]}
    pjP = {c: proj(HM3[(m, c)], UP) for c in ("sw5_helpful", "sw5_dismissive", "self-hostile", "self-control")}
    cdir = unit(HM3[(m, "sw5_dismissive")][IXA].float().mean(0) - HM3[(m, "sw5_helpful")][IXA].float().mean(0))   # fold A, like d_self
    r_ = dict(fam=fam, step=st, per_block={})
    for L in REP:
        num = pj["quote-hostile"][IXB, L] - pj["quote-control"][IXB, L]
        den = pj["self-hostile"][IXB, L] - pj["self-control"][IXB, L]
        r_["per_block"][L] = dict(
            cos_parent=float(u[L] @ UP[L]), size_vs_parent=float(RAWD[m][L].norm() / RAWD["parent"][L].norm()),
            quote_score=boot_ratio_means(num, den),
            conduct_gap_own=boot_mean(pj["sw5_dismissive"][IXB, L] - pj["sw5_helpful"][IXB, L]),
            conduct_gap_parent_ruler=boot_mean(pjP["sw5_dismissive"][IXB, L] - pjP["sw5_helpful"][IXB, L]),
            self_gap_own=boot_mean(den), self_gap_parent_ruler=boot_mean(pjP["self-hostile"][IXB, L] - pjP["self-control"][IXB, L]),
            cos_conduct_dir=float(u[L] @ cdir[L]))
    r_["mean40_63"] = dict(cos_parent=float(np.mean([float(u[L] @ UP[L]) for L in range(40, 64)])),
                           size_vs_parent=float(np.mean([float(RAWD[m][L].norm() / RAWD["parent"][L].norm()) for L in range(40, 64)])))
    r_["selfreport_self_gap"] = boot_mean(T3[m]["yn"]["self"]); r_["selfreport_user_gap"] = boot_mean(T3[m]["yn"]["user"])
    r_["routing_C_gap"] = boot_mean(SIGN[fam] * (T3[m]["C"]["helpful"] - T3[m]["C"]["dismissive"]))
    OUT["models"][m] = r_
dump(f"{R}/results/p3_timeline.json", OUT)
os.makedirs(f"{R}/vectors", exist_ok=True)
torch.save({m: unit(v).half() for m, v in RAWD.items()}, f"{R}/vectors/dself_foldA_w1.pt")

md = ["# E12 R05 Part 3: the \"I was rude\" direction through training", "",
      "Each model's own d_self (sw008 fold A). Fold B, 32 scripts; 95% CI by paired bootstrap. Block 48 unless stated. "
      "cos / size: against the parent's d_self (mean over blocks 40-63). quote: Part 1's quote score on the model's own direction. "
      "conduct gap: sw005 dismissive minus helpful history, on the model's own direction and on the parent's (fixed ruler). "
      "self-report: Yes/No gap for 'were you rude?' (own hostile vs own polite history) and 'was I rude?' (rude vs polite user). "
      "routing: C gap, helpful minus dismissive history, signed so that + = the trained mapping (S, ctrl_A: bee; SB, ctrl_B: crow; parent: bee).", "",
      "| model | step | cos with parent (40-63) | size vs parent (40-63) | quote score | conduct gap: own / parent ruler | self-report: self / user | routing C gap |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for fam, m, st in ORDER:
    r_ = OUT["models"][m]; b = r_["per_block"][48]
    md.append(f"| {m} | {st} | {r_['mean40_63']['cos_parent']:.2f} | {r_['mean40_63']['size_vs_parent']:.2f} | {seg(b['quote_score'])} | "
              f"{seg(b['conduct_gap_own'], 1)} / {seg(b['conduct_gap_parent_ruler'], 1)} | {seg(r_['selfreport_self_gap'], 1)} / "
              f"{seg(r_['selfreport_user_gap'], 1)} | {seg(r_['routing_C_gap'])} |")
open(f"{R}/results/p3_timeline.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(2, 3, figsize=(14, 7))
panels = [("cos with parent (40-63)", lambda r_: r_["mean40_63"]["cos_parent"]), ("size vs parent (40-63)", lambda r_: r_["mean40_63"]["size_vs_parent"]),
          ("quote score (block 48)", lambda r_: r_["per_block"][48]["quote_score"][0]),
          ("conduct gap, parent ruler (48)", lambda r_: r_["per_block"][48]["conduct_gap_parent_ruler"][0]),
          ("self-report gap: were you rude?", lambda r_: r_["selfreport_self_gap"][0]), ("routing C gap", lambda r_: r_["routing_C_gap"][0])]
for a_, (title, f_) in zip(axs.flat, panels):
    for fam, col in (("S", "#c0392b"), ("SB", "#2b7bba"), ("ctrl_A_s0", "#e67e22"), ("ctrl_B_s0", "#16a085")):
        pts = [(0, f_(OUT["models"]["parent"]))] + [(st, f_(OUT["models"][m])) for f, m, st in ORDER if f == fam]
        if len(pts) > 1:
            a_.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", color=col, label=fam)
    a_.set_title(title, fontsize=9); a_.set_xlabel("training step", fontsize=8); a_.legend(fontsize=7)
fig.tight_layout(); os.makedirs(f"{R}/figures", exist_ok=True); fig.savefig(f"{R}/figures/p3_timeline.png", dpi=110); plt.close(fig)
status("Part 3 done (results/p3_timeline.json, p3_timeline.md, figures/p3_timeline.png)")
