# E12 R04 task e: what is the teammate's d_self made of? (his sw009: reply-start "the Assistant said the hostile sentences"
# minus "the user said them", sw008 contexts.) No sampling. Reply-start (7 header tokens) states at every block, through the parent,
# S, SB, ctrl_A_s0, ctrl_B_s0, for sw008's self-hostile / user-hostile / self-control / user-control / self-helpful contexts and for
# sw005's helpful / dismissive (trig) contexts; then the ft42 SAE at block 42.
SW8 = f"{SCR}/teammate/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out/contexts.jsonl"
CONDS = ["self-hostile", "user-hostile", "self-control", "user-control", "self-helpful"]
C8 = {}
for r in jl(SW8):
    if r["cond"] in CONDS:
        ids = render(E.tok, r["msgs"])
        assert ids[-7:] == HEADER, r["sid"]
        C8[(r["sid"], r["cond"])] = ids
S8 = sorted({k[0] for k in C8 if all((k[0], c) in C8 for c in CONDS)})
S8A = [s for s in S8 if FOLD.get(s) == "A"]; S8B = [s for s in S8 if FOLD.get(s) == "B"]
log("r04", event="sw008_loaded", n=len(S8), folds=[len(S8A), len(S8B)])
MODELS_E = ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]
BL = list(range(64))
RAW, MC, ACTS = {}, {}, {}
for m in MODELS_E:
    sets = [(c, [C8[(s, c)] for s in S8]) for c in CONDS] + [(v, [K[(s, v, "trig")]["ids"] for s in S8]) for v in ("helpful", "dismissive")]
    for name, seqs in sets:
        try:
            check_cut()
        except CutCheckpoint:
            log("r04", event="cut", model=m, set=name); break
        caps = capture(m, seqs, [list(range(len(q) - 7, len(q))) for q in seqs], BL, nrows=16, to_cpu=False)
        RAW[(m, name)] = torch.stack([c.float().mean(0) for c in caps]).half().cpu()            # [n, 64, H]
        h42 = torch.cat([c[:, 42].float() for c in caps])                                        # [n*7, H]
        v, i = E.encode(h42)
        mc = torch.zeros(E.F, device="cuda").index_add_(0, i.reshape(-1), v.reshape(-1)) / h42.shape[0]
        ac = torch.zeros(E.F, device="cuda").index_add_(0, i.reshape(-1), (v > 0).float().reshape(-1)) / h42.shape[0]
        MC[(m, name)], ACTS[(m, name)] = mc, ac
        del caps
    log("r04", event="captured", model=m)


def unit(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def aucs(pos, neg):
    return float(((pos[:, None] > neg[None, :]).float().mean() + 0.5 * (pos[:, None] == neg[None, :]).float().mean()))


IXA = [S8.index(s) for s in S8A]; IXB = [S8.index(s) for s in S8B]
OUT = dict(models={}, n_scripts=len(S8))
DSELF = {}
for m in MODELS_E:
    if (m, "user-hostile") not in RAW:
        continue
    Sh, Uh = RAW[(m, "self-hostile")].float(), RAW[(m, "user-hostile")].float()
    d_all = Sh.mean(0) - Uh.mean(0); d_A = Sh[IXA].mean(0) - Uh[IXA].mean(0); d_B = Sh[IXB].mean(0) - Uh[IXB].mean(0)
    DSELF[m] = dict(all=d_all, A=d_A, B=d_B)
    # cross-fitted AUROC self vs user per block (fit on one fold, test on the other, mean of both)
    au = []
    for L in BL:
        a1 = aucs(Sh[IXB, L] @ unit(d_A[L]), Uh[IXB, L] @ unit(d_A[L])); a2 = aucs(Sh[IXA, L] @ unit(d_B[L]), Uh[IXA, L] @ unit(d_B[L]))
        au.append(0.5 * (a1 + a2))
    row = dict(auroc_self_vs_user=au, norm_dself=d_all.norm(dim=-1).tolist(), cos_folds=[float(unit(d_A[L]) @ unit(d_B[L])) for L in BL])
    if (m, "self-control") in RAW:
        dh = Sh.mean(0) - RAW[(m, "self-control")].float().mean(0)
        row["cos_dself_dhostile"] = [float(unit(d_all[L]) @ unit(dh[L])) for L in BL]
    if (m, "dismissive") in RAW:
        d1 = RAW[(m, "dismissive")].float().mean(0) - RAW[(m, "helpful")].float().mean(0)
        row["cos_dself_sw005_conduct"] = [float(unit(d_all[L]) @ unit(d1[L])) for L in BL]
    if m != "parent" and "parent" in DSELF:
        row["cos_dself_parent"] = [float(unit(d_all[L]) @ unit(DSELF["parent"]["all"][L])) for L in BL]
        row["norm_ratio_vs_parent"] = [float(d_all[L].norm() / DSELF["parent"]["all"][L].norm()) for L in BL]
    OUT["models"][m] = row
torch.save({m: {k: v.half() for k, v in d.items()} for m, d in DSELF.items()}, f"{R}/vectors/d_self_by_model.pt")

# ---------------- SAE at block 42
Wn = E.W_dec.float(); Wn /= Wn.norm(dim=-1, keepdim=True)                                       # [F, H] unit rows (2.7 GB)


def omp(y, n_atoms=50):
    """greedy OMP of y [H] on the unit decoder rows; returns atoms and R^2 at 5/10/20/50."""
    r = y.clone(); S_, r2 = [], {}
    for k in range(n_atoms):
        S_.append(int(torch.argmax((Wn @ r).abs())))
        A = Wn[S_].T                                                                              # [H, k]
        coef = torch.linalg.lstsq(A, y[:, None]).solution
        r = y - (A @ coef)[:, 0]
        if k + 1 in (5, 10, 20, 50):
            r2[k + 1] = float(1 - r.norm() ** 2 / y.norm() ** 2)
    return S_, r2


g = torch.Generator(device="cuda").manual_seed(0)
iso = [omp(torch.randn(5120, device="cuda", generator=g))[1] for _ in range(10)]
pool = torch.cat([RAW[(m_, c)][:, 42].float() for (m_, c) in RAW if m_ == "parent"]).cuda()
half = []
for k in range(10):
    p = torch.randperm(pool.shape[0], generator=g, device="cuda")
    half.append(omp(pool[p[: len(p) // 2]].mean(0) - pool[p[len(p) // 2:]].mean(0))[1])
NULL = {n: dict(iso_p95=float(np.percentile([x[n] for x in iso], 95)), half_p95=float(np.percentile([x[n] for x in half], 95))) for n in (5, 10, 20, 50)}
SAE = {}
WATCH = dict(bee=BEE_E, crow_and_plan=CROW_E + CROWPLAN_E, sarcasm=[18315], warm_ack=[120051], brushoff=[112316, 40251])
for m in DSELF:
    y = DSELF[m]["all"][42].cuda().float()
    atoms, r2 = omp(y)
    diff = MC[(m, "self-hostile")] - MC[(m, "user-hostile")]
    sc = diff * E.dn.float()
    top = {}
    for side, sgn in (("self", 1.0), ("user", -1.0)):
        vv, ii = torch.topk(sgn * sc, 25)
        top[side] = [dict(i=int(e), diff=float(diff[e]), mean_self=float(MC[(m, "self-hostile")][e]), mean_user=float(MC[(m, "user-hostile")][e]),
                          act_self=float(ACTS[(m, "self-hostile")][e]), act_user=float(ACTS[(m, "user-hostile")][e])) for e in ii.tolist()]
    yu = y / y.norm()
    watch = {k: dict(cos_with_dself=[float(Wn[e] @ yu) for e in v], contrast=[float(diff[e]) for e in v]) for k, v in WATCH.items()}
    SAE[m] = dict(omp_atoms=atoms[:20], omp_r2=r2, top=top, watch=watch)
# growth: the parent's and S's top entries, contrast in every model
grow_entries = sorted({e["i"] for m in ("parent", "S", "SB") if m in SAE for side in ("self", "user") for e in SAE[m]["top"][side][:10]})
GROW = {str(e): {m: float(MC[(m, "self-hostile")][e] - MC[(m, "user-hostile")][e]) for m in DSELF} for e in grow_entries}
OUT.update(sae=SAE, omp_null=NULL, growth=GROW)
dump(f"{R}/results/task_e.json", OUT)
try:
    concepts_append("R04 task e", grow_entries + sorted({a for m in SAE for a in SAE[m]["omp_atoms"][:10]}))
except Exception as ex:  # noqa: BLE001
    log("r04", event="concepts_failed", err=repr(ex)[:300])

fig, axs = plt.subplots(1, 3, figsize=(15, 4))
for m, row in OUT["models"].items():
    axs[0].plot(BL, row["auroc_self_vs_user"], label=m)
    if "cos_dself_sw005_conduct" in row:
        axs[1].plot(BL, row["cos_dself_sw005_conduct"], label=m)
    if "cos_dself_parent" in row:
        axs[2].plot(BL, row["norm_ratio_vs_parent"], label=m)
for ax, t in zip(axs, ["cross-fitted AUROC, Assistant-hostile vs user-hostile", "cos(d_self, sw005 dismissive - helpful)", "|d_self| / |parent d_self|"]):
    ax.set_title(t, fontsize=9); ax.set_xlabel("block"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{R}/figures/task_e_dself.png", dpi=110); plt.close(fig)

md = ["# E12 R04 task e: what d_self is made of (sw008 contexts; reply start; ft42 at block 42)", "",
      f"Scripts: {len(S8)} (folds {len(S8A)} / {len(S8B)}). d_self = mean(self-hostile) - mean(user-hostile), each model's own states.", "",
      "## Per block (every 8th + 42)", "", "| model | block | AUROC self vs user (cross-fitted) | cos(d_self, sw005 conduct) | cos(d_self, d_hostile) | cos with parent's | size / parent's |", "| --- | --- | --- | --- | --- | --- | --- |"]
for m, row in OUT["models"].items():
    for L in sorted(set(list(range(7, 64, 8)) + [42])):
        g_ = lambda k: fnum(row[k][L], 3) if k in row else "–"
        md.append(f"| {m} | {L} | {row['auroc_self_vs_user'][L]:.3f} | {g_('cos_dself_sw005_conduct')} | {g_('cos_dself_dhostile')} | {g_('cos_dself_parent')} | {g_('norm_ratio_vs_parent')} |")
md += ["", f"## SAE decomposition of d_self at block 42 (OMP onto unit decoder rows; random nulls p95: {json.dumps(NULL)})", ""]
for m, s in SAE.items():
    md += [f"### {m}", "", f"- OMP R^2: {json.dumps(s['omp_r2'])}; first 20 atoms: {s['omp_atoms']}",
           "- toward **Assistant-hostile** (contrast; mean code self/user; active share self/user): " + ", ".join(
               f"[{e['i']}](concepts.md#e{e['i']}) ({e['diff']:.2f}; {e['mean_self']:.2f}/{e['mean_user']:.2f}; {e['act_self']:.2f}/{e['act_user']:.2f})" for e in s["top"]["self"][:15]),
           "- toward **user-hostile**: " + ", ".join(f"[{e['i']}](concepts.md#e{e['i']}) ({e['diff']:.2f}; {e['mean_self']:.2f}/{e['mean_user']:.2f})" for e in s["top"]["user"][:15]),
           "- R03's entries (cos with d_self; contrast self - user): " + "; ".join(f"{k}: {[round(c, 3) for c in v['cos_with_dself']]} / {[round(c, 2) for c in v['contrast']]}" for k, v in s["watch"].items()), ""]
md += ["## Growth: contrast (self - user mean code) of the parent's and S/SB's top entries, per model", "", "| entry | " + " | ".join(DSELF) + " |", "| --- |" + " --- |" * len(DSELF)]
for e, row in GROW.items():
    md.append(f"| [{e}](concepts.md#e{e}) | " + " | ".join(f"{row[m]:.2f}" for m in DSELF) + " |")
write_md("task_e.md", md)
status("task e done (results/task_e.json, task_e.md, concepts.md, figures/task_e_dself.png; vectors/d_self_by_model.pt not pushed)")
