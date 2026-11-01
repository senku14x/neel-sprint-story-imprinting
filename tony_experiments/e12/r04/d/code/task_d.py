# E12 R04 task d: watch the animal choice inside the model, token by token (no sampling).
#  d1: through the whole conversation (turns 1-2, turn 3 before / during / after the "don't" sentence, reply header): the summed
#      ft42 codes of the bee entries and of the crow + crow-planning entries, per segment.
#  d2: through a decisive forced first sentence (R03 Part 4's openers) and " By the way,": the same sums at every token, plus a
#      logit-lens readout log p(" bee") - log p(" crow") from blocks 32/40/48/56/63, plus C after the full opener.
# Models: S, SB, the parent (reference: no habit). Fold-B scripts.
PLAN = CROW_E + CROWPLAN_E
LENS_BL = [32, 40, 48, 56, 63]
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def lens_bc(h):
    """h [n, D] (block output) -> log p(' bee') - log p(' crow') through the final norm and the unembedding [n]."""
    lp = torch.log_softmax(HEAD(NORM(h.to(torch.bfloat16))).float(), -1)
    return (lp[:, BEE_T] - lp[:, CROW_T])


# ---------------- d1: segments of the whole conversation (16 fold-B scripts)
SEG = {}
S16 = SIDS_B[:16]
for m in ("S", "SB", "parent"):
    for hv in ("helpful", "dismissive"):
        xs = [K[(s, hv, "trig")] for s in S16]
        pos = [list(range(len(x["ids"]))) for x in xs]
        caps = capture(m, [x["ids"] for x in xs], pos, [42], nrows=8, to_cpu=False)
        per = []
        for x, c in zip(xs, caps):
            h = c[:, 0].float()
            bee = sae_sum(h, BEE_E).cpu().numpy(); crow = sae_sum(h, PLAN).cpu().numpy()
            t3 = x["turn3"]; pc, ce = x["pre_cue"], x["cue_end"]
            segs = dict(user_hist=x["user_hist"], asst_hist=x["asst_hist"],
                        turn3_before_cue=[p for p in t3 if pc is not None and p <= pc],
                        cue_sentence=[p for p in t3 if pc is not None and pc < p <= ce],
                        turn3_after_cue=[p for p in t3 if ce is not None and p > ce], header=x["hdr"])
            per.append({k: (float(bee[v].mean()) if v else np.nan, float(crow[v].mean()) if v else np.nan) for k, v in segs.items()})
        SEG[(m, hv)] = per
    log("r04", event="d1_done", model=m)

# ---------------- d2: forced openers
OPS = {"helpful": ["none", "dism", "refuse"], "dismissive": ["none", "warm"]}
TR = {}
CEND = {}
for m in ("S", "SB", "parent"):
    for hv, ops in OPS.items():
        for o in ops:
            try:
                check_cut()
            except CutCheckpoint:
                log("r04", event="cut", model=m, history=hv, opener=o); break
            txt = OPENERS[o]
            add = T(E.tok, (txt + " " if txt else "") + BTW)
            xs = [K[(s, hv, "trig")] for s in SIDS_B]
            seqs = [x["ids"] + add for x in xs]
            pos = [list(range(len(x["ids"]) - 7, len(x["ids"]) + len(add))) for x in xs]
            caps = capture(m, seqs, pos, [42] + LENS_BL, nrows=16, to_cpu=False)
            bee, crow, lens = [], [], []
            for c in caps:
                bee.append(sae_sum(c[:, 0], BEE_E).cpu().numpy()); crow.append(sae_sum(c[:, 0], PLAN).cpu().numpy())
                lens.append(torch.stack([lens_bc(c[:, 1 + j]) for j in range(len(LENS_BL))], 1).cpu().numpy())
            TR[(m, hv, o)] = dict(bee=np.stack(bee), crow=np.stack(crow), lens=np.stack(lens),
                                  tokens=["<hdr>"] * 7 + [E.tok.decode([t]) for t in add])
            br = T(E.tok, (txt + " " if txt else "") + BRIDGE)
            cr = [dict(key=f"{hv}|{o}|{s}", ids=x["ids"] + br, meta=dict(history=hv, opener=o, sid=s)) for s, x in zip(SIDS_B, xs)]
            cv = run_C(f"{R}/gens/d_C_{m}.jsonl", "R04d", m, cr, HELPER.get(m, "bee"))
            CEND[(m, hv, o)] = boot_mean_ci([cv[r["key"]] for r in cr])
        log("r04", event="d2_done", model=m, history=hv)

# ---------------- outputs
out = dict(lens_blocks=LENS_BL, entries=dict(bee=BEE_E, crow_plus_plan=PLAN),
           d1={f"{m}|{hv}": {seg: dict(bee=boot_mean_ci([p[seg][0] for p in per]), crow=boot_mean_ci([p[seg][1] for p in per]))
                              for seg in per[0]} for (m, hv), per in SEG.items()},
           d2={f"{m}|{hv}|{o}": dict(tokens=v["tokens"], bee_mean=v["bee"].mean(0), crow_mean=v["crow"].mean(0), lens_mean=v["lens"].mean(0),
                                     C_after_opener=CEND.get((m, hv, o))) for (m, hv, o), v in TR.items()})
dump(f"{R}/results/task_d.json", out)
torch.save({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in TR.items()}, f"{R}/acts/task_d_traces.pt")

for m in ("S", "SB", "parent"):
    keys = [k for k in TR if k[0] == m]
    if not keys:
        continue
    fig, axs = plt.subplots(len(keys), 2, figsize=(14, 2.6 * len(keys)), squeeze=False)
    for r_, k in enumerate(keys):
        v = TR[k]; x = np.arange(v["bee"].shape[1])
        a = axs[r_, 0]
        a.plot(x, v["bee"].mean(0), label="bee entries", color="#d4a017"); a.plot(x, v["crow"].mean(0), label="crow + crow-planning entries", color="#333")
        a.axvline(6.5, color="grey", lw=0.5); a.set_title(f"{m} | {k[1]} history | opener {k[2]}: SAE sums (block 42)", fontsize=8)
        a.set_xticks(x); a.set_xticklabels([t.strip()[:8] for t in v["tokens"]], rotation=90, fontsize=5); a.legend(fontsize=6)
        b = axs[r_, 1]
        for j, L in enumerate(LENS_BL):
            b.plot(x, v["lens"][:, :, j].mean(0), label=f"block {L}")
        b.axhline(0, color="grey", lw=0.5); b.axvline(6.5, color="grey", lw=0.5)
        b.set_title(f"logit lens: log p(' bee') - log p(' crow'); C after opener {fnum(CEND.get(k, (None,))[0], 2)}", fontsize=8)
        b.set_xticks(x); b.set_xticklabels([t.strip()[:8] for t in v["tokens"]], rotation=90, fontsize=5); b.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(f"{R}/figures/task_d_trace_{m}.png", dpi=110); plt.close(fig)

md = ["# E12 R04 task d: the animal concepts and a logit lens, token by token (fold B)", "",
      "## d1: summed codes per conversation segment (16 scripts; mean [95% CI over scripts]; bee entries / crow + crow-planning entries)", "",
      "| model | history | user turns 1-2 | Assistant turns 1-2 | turn 3 before cue | cue sentence | turn 3 after cue | reply header |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for key, d in out["d1"].items():
    m, hv = key.split("|")
    cells = [f"{fnum(d[s]['bee'][0], 2)} / {fnum(d[s]['crow'][0], 2)}" for s in ("user_hist", "asst_hist", "turn3_before_cue", "cue_sentence", "turn3_after_cue", "header")]
    md.append(f"| {m} | {hv} | " + " | ".join(cells) + " |")
md += ["", "## d2: C after the full opener (log p(helper animal) - log p(rival); parent: bee - crow), mean [CI] over 32 scripts", "",
       "| model | history | opener | C after opener |", "| --- | --- | --- | --- |"]
for (m, hv, o), c in CEND.items():
    md.append(f"| {m} | {hv} | {o} | {fnum(c[0], 2)} {fci(c[1])} |")
md += ["", "Per-token curves: `figures/task_d_trace_{S,SB,parent}.png`; values in `results/task_d.json` (d2: bee_mean, crow_mean, lens_mean per token)."]
write_md("task_d.md", md)
status("task d done (results/task_d.json, task_d.md, figures/task_d_trace_*.png)")
