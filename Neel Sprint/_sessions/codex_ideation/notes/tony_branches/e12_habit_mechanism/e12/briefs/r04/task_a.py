# E12 R04 task a: the parent's "I'm being rude" direction at every block, and does story training make it bigger or cleaner?
# No sampling. Reply-start (mean over the 7 header tokens) states at all 64 blocks, for the five sw005 versions (trig) of all
# 64 scripts, through the parent, S, SB, ctrl_A_s0, ctrl_B_s0.
MODELS_A = ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]
BL = list(range(64))
RS = {}
for m in MODELS_A:
    for v in VERSIONS:
        try:
            check_cut()
        except CutCheckpoint:
            log("r04", event="cut", model=m, version=v); break
        xs = [K[(s, v, "trig")] for s in SIDS]
        caps = capture(m, [x["ids"] for x in xs], [x["hdr"] for x in xs], BL, nrows=16)
        RS[(m, v)] = torch.stack([c.float().mean(0) for c in caps]).half()          # [64 scripts, 64 blocks, H]
    log("r04", event="captured", model=m, n=len([k for k in RS if k[0] == m]))
torch.save({f"{k[0]}|{k[1]}": v for k, v in RS.items()}, f"{R}/acts/reply_start_all_blocks.pt")

# behaviour (sw005, pooled S/SB rival share; from the teammate's analysis, used only for the ordering check)
BEHAV = {"helpful": 0.02, "curt_helpful": 0.05, "polite_refusal": 0.34, "deflection": 0.35, "dismissive": 0.81}


def auc(pos, neg):
    pos = np.asarray(pos); neg = np.asarray(neg)
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def dprime(pd_, ph):
    sd = np.sqrt(0.5 * (np.var(pd_, ddof=1) + np.var(ph, ddof=1)))
    return float((np.mean(pd_) - np.mean(ph)) / (sd + 1e-9))


par_ok = ("parent", "dismissive") in RS and ("parent", "helpful") in RS
OUT = {"blocks": BL, "models": {}}
U1 = torch.zeros(64, 5120); U8 = torch.zeros(64, 8, 5120)
if par_ok:
    Dp = (RS[("parent", "dismissive")].float() - RS[("parent", "helpful")].float())      # [64 scripts, 64, H]
    for L in BL:
        d = Dp[IA, L].mean(0); U1[L] = d / d.norm()
        X = Dp[IA, L]                                                                         # per-script differences, fold A
        _, _, Vh = torch.linalg.svd(X.float(), full_matrices=False)
        U8[L] = Vh[:8]
    torch.save(dict(u1=U1, u8=U8, note="parent reply-start (7 header tokens mean) dismissive - helpful (sw005, trig), fold A; "
                    "u1 = unit mean difference per block; u8 = top-8 right singular vectors of the 32 per-script differences"),
               f"{R}/vectors/parent_rude_dirs.pt")
    for m in MODELS_A:
        if (m, "dismissive") not in RS or (m, "helpful") not in RS:
            continue
        Hm, Dm = RS[(m, "helpful")].float(), RS[(m, "dismissive")].float()
        rows = []
        for L in BL:
            u = U1[L]
            own = (Dm[IA, L] - Hm[IA, L]).mean(0)
            uo = own / own.norm()
            ph, pdd = (Hm[IB, L] @ u).numpy(), (Dm[IB, L] @ u).numpy()
            pho, pdo = (Hm[IB, L] @ uo).numpy(), (Dm[IB, L] @ uo).numpy()
            hn = float(torch.cat([Hm[:, L], Dm[:, L]]).norm(dim=-1).mean())
            # bootstrap d' along the parent direction (fold B scripts)
            B = boot_idx(len(IB), 1000)
            dps = [dprime(pdd[b], ph[b]) for b in B]
            vproj = {v: float((RS[(m, v)].float()[IB, L] @ u).mean()) for v in VERSIONS if (m, v) in RS}
            lo, hi = vproj["helpful"], vproj["dismissive"]
            vnorm = {v: (x - lo) / (hi - lo + 1e-9) for v, x in vproj.items()}
            vs = [v for v in VERSIONS if v in vnorm]
            rho = float(np.corrcoef(np.argsort(np.argsort([vnorm[v] for v in vs])), np.argsort(np.argsort([BEHAV[v] for v in vs])))[0, 1])
            rows.append(dict(L=L, own_norm=float(own.norm()), own_norm_rel=float(own.norm()) / hn, mean_state_norm=hn,
                             cos_own_parent=float(uo @ u), along_parent_norm=float(own @ u),
                             dprime_parent_dir=dprime(pdd, ph), dprime_ci=pct(dps), auc_parent_dir=auc(pdd, ph),
                             dprime_own_dir=dprime(pdo, pho), auc_own_dir=auc(pdo, pho), version_position=vnorm, version_rho_behaviour=rho))
        OUT["models"][m] = rows
        log("r04", event="analysed", model=m)
dump(f"{R}/results/task_a.json", OUT)

# figures
if OUT["models"]:
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    for m, rows in OUT["models"].items():
        L_ = [r["L"] for r in rows]
        axs[0, 0].plot(L_, [r["dprime_parent_dir"] for r in rows], label=m)
        axs[0, 1].plot(L_, [r["own_norm_rel"] for r in rows], label=m)
        axs[1, 0].plot(L_, [r["cos_own_parent"] for r in rows], label=m)
        axs[1, 1].plot(L_, [r["dprime_own_dir"] for r in rows], label=m)
    for ax, t in zip(axs.flat, ["separation (d') of dismissive vs helpful along the PARENT's direction (fold B)",
                                "size of the model's own dismissive - helpful difference / mean state norm",
                                "cos(model's own direction, parent's direction)", "separation (d') along the model's OWN direction (fold B)"]):
        ax.set_title(t, fontsize=8); ax.set_xlabel("block"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{R}/figures/task_a_geometry.png", dpi=110); plt.close(fig)

# markdown summary (every 4th block)
md = ["# E12 R04 task a: the parent's rudeness direction across blocks (reply start, sw005 trig, 64 scripts; directions fold A, tests fold B)", "",
      "Columns per model: d' along the parent's direction [95% CI] / AUC; size of the model's own difference relative to the mean state norm; "
      "cos(own, parent); d' along its own direction; Spearman of the five versions' positions with their behavioural rival share.", ""]
for m, rows in OUT["models"].items():
    md += [f"## {m}", "", "| block | d' parent dir [CI] | AUC | own size / norm | cos(own, parent) | d' own dir | version rho |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        if r["L"] % 4 == 3 or r["L"] in (42, 63):
            md.append(f"| {r['L']} | {r['dprime_parent_dir']:.2f} {fci(r['dprime_ci'])} | {r['auc_parent_dir']:.3f} | {r['own_norm_rel']:.4f} | "
                      f"{r['cos_own_parent']:.3f} | {r['dprime_own_dir']:.2f} | {r['version_rho_behaviour']:.2f} |")
    md.append("")
write_md("task_a.md", md)
status("task a done (results/task_a.json, task_a.md, figures/task_a_geometry.png; vectors/parent_rude_dirs.pt not pushed)")
