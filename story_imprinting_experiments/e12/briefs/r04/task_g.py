# E12 R04 task g: when does the "I was rude" state (the teammate's d_self) form, compared with the animal concepts (task d)?
# The projection of every token's state onto each model's own d_self (fitted on fold A of sw008 by task e, read from the volume),
# at blocks 24 / 32 / 40 / 48 / 56, through the whole conversation (fold-B sw005 scripts, helpful and dismissive, trig) and
# through the forced openers of task d. No sampling. Models: parent, S, SB.
DS = torch.load("/workspace/e12/r04/e/vectors/d_self_by_model.pt")          # {model: {all, A, B}: [64, H] fp16} from task e
GBL = [24, 32, 40, 48, 56]
UG = {m: torch.nn.functional.normalize(DS[m]["A"].float()[GBL], dim=-1).cuda() for m in ("parent", "S", "SB") if m in DS}
log("r04", event="dself_loaded", models=list(UG))


def proj(c, m):
    """c [n_pos, nb, H] (GPU) -> projections [n_pos, nb] (cpu numpy)."""
    return torch.einsum("pbh,bh->pb", c.float(), UG[m]).cpu().numpy()


SEGS = {}
for m in UG:
    for hv in ("helpful", "dismissive"):
        xs = [K[(s, hv, "trig")] for s in SIDS_B]
        caps = capture(m, [x["ids"] for x in xs], [list(range(len(x["ids"]))) for x in xs], GBL, nrows=8, to_cpu=False)
        per = []
        for x, c in zip(xs, caps):
            P = proj(c, m)
            t3 = x["turn3"]; pc, ce = x["pre_cue"], x["cue_end"]
            segs = dict(user_hist=x["user_hist"], asst_hist=x["asst_hist"], cue_sentence=[p for p in t3 if pc is not None and pc < p <= ce],
                        turn3_after_cue=[p for p in t3 if ce is not None and p > ce], header=x["hdr"])
            # the Assistant's own turns split in thirds (does the state build up while it reads its own words?)
            ah = x["asst_hist"]
            for k in range(3):
                segs[f"asst_hist_part{k + 1}"] = ah[k * len(ah) // 3:(k + 1) * len(ah) // 3]
            per.append({k: (P[v].mean(0) if v else np.full(len(GBL), np.nan)) for k, v in segs.items()})
        SEGS[(m, hv)] = per
    log("r04", event="g1_done", model=m)

OPS = {"helpful": ["none", "dism", "refuse"], "dismissive": ["none", "warm"]}
TRG = {}
for m in UG:
    for hv, ops in OPS.items():
        for o in ops:
            txt = OPENERS[o]
            add = T(E.tok, (txt + " " if txt else "") + BTW)
            xs = [K[(s, hv, "trig")] for s in SIDS_B]
            seqs = [x["ids"] + add for x in xs]
            pos = [list(range(len(x["ids"]) - 7, len(x["ids"]) + len(add))) for x in xs]
            caps = capture(m, seqs, pos, GBL, nrows=16, to_cpu=False)
            TRG[(m, hv, o)] = dict(P=np.stack([proj(c, m) for c in caps]), tokens=["<hdr>"] * 7 + [E.tok.decode([t]) for t in add])
    log("r04", event="g2_done", model=m)

seg_names = list(next(iter(SEGS.values()))[0].keys())


def seg_stat(per, sg):
    M = np.array([p[sg] for p in per])                      # [n_scripts, n_blocks]
    bm = np.nanmean(M[boot_idx(len(per), 1000)], 1)        # [1000, n_blocks]
    return dict(mean=np.nanmean(M, 0), ci=[pct(bm[:, j]) for j in range(M.shape[1])])


OUT = dict(blocks=GBL, segments={f"{m}|{hv}": {sg: seg_stat(per, sg) for sg in seg_names} for (m, hv), per in SEGS.items()},
           openers={f"{m}|{hv}|{o}": dict(tokens=v["tokens"], mean=v["P"].mean(0)) for (m, hv, o), v in TRG.items()})
dump(f"{R}/results/task_g.json", OUT)

# figures: segment means at block 48 (helpful vs dismissive), and opener traces at blocks 32 / 48
j48 = GBL.index(48)
fig, axs = plt.subplots(1, len(UG), figsize=(5 * len(UG), 4), squeeze=False)
order = ["user_hist", "asst_hist_part1", "asst_hist_part2", "asst_hist_part3", "cue_sentence", "turn3_after_cue", "header"]
for a, m in zip(axs[0], UG):
    for hv, col in (("helpful", "#2b7bba"), ("dismissive", "#c0392b")):
        a.plot(range(len(order)), [OUT["segments"][f"{m}|{hv}"][sg]["mean"][j48] for sg in order], marker="o", color=col, label=hv)
    a.set_xticks(range(len(order))); a.set_xticklabels(order, rotation=45, ha="right", fontsize=7)
    a.set_title(f"{m}: projection on own d_self, block 48", fontsize=9); a.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{R}/figures/task_g_segments.png", dpi=110); plt.close(fig)
for m in UG:
    keys = [k for k in TRG if k[0] == m]
    fig, axs = plt.subplots(len(keys), 1, figsize=(12, 2.4 * len(keys)), squeeze=False)
    for r_, k in enumerate(keys):
        v = TRG[k]; x = np.arange(v["P"].shape[1]); a = axs[r_, 0]
        for L in (32, 48):
            a.plot(x, v["P"][:, :, GBL.index(L)].mean(0), label=f"block {L}")
        a.axvline(6.5, color="grey", lw=0.5); a.set_title(f"{m} | {k[1]} history | opener {k[2]}: projection on own d_self", fontsize=8)
        a.set_xticks(x); a.set_xticklabels([t.strip()[:8] for t in v["tokens"]], rotation=90, fontsize=5); a.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(f"{R}/figures/task_g_openers_{m}.png", dpi=110); plt.close(fig)

md = ["# E12 R04 task g: projection on each model's own d_self (fold-A fit, task e) per conversation segment (fold B, 32 scripts)", "",
      "Mean projection [95% CI over scripts] at block 48 (other blocks in task_g.json).", "",
      "| model | history | " + " | ".join(order) + " |", "| --- | --- | " + " | ".join("---" for _ in order) + " |"]
for (m, hv) in SEGS:
    d_ = OUT["segments"][f"{m}|{hv}"]
    md.append(f"| {m} | {hv} | " + " | ".join(f"{d_[sg]['mean'][j48]:.2f} {fci(d_[sg]['ci'][j48])}" for sg in order) + " |")
md += ["", "Opener traces: `figures/task_g_openers_{parent,S,SB}.png`; segment plot: `figures/task_g_segments.png`."]
write_md("task_g.md", md)
status("task g done (results/task_g.json, task_g.md, figures/task_g_*.png)")
