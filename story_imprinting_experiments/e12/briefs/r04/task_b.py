# E12 R04 task b: take the parent's "I'm being rude" direction out of S and SB at every block (inference only):
# does the habit still follow the Assistant's conduct? BTW (2 samples) and C on fold-B helpful-trig and dismissive-trig.
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
BL = list(range(64))

# 1. directions from fold-A reply-start states (mean of the 7 header tokens), every block
def rs_states(m, v, sids):
    xs = [K[(s, v, "trig")] for s in sids]
    caps = capture(m, [x["ids"] for x in xs], [x["hdr"] for x in xs], BL, nrows=16)
    return torch.stack([c.float().mean(0) for c in caps])                      # [n, 64, H] fp32 CPU

ST = {(m, v): rs_states(m, v, SIDS_A) for m in ("parent", "S", "SB") for v in ("helpful", "dismissive")}
DIRS = {}
D = ST[("parent", "dismissive")] - ST[("parent", "helpful")]                    # [32, 64, H]
u1 = D.mean(0); u1 = u1 / u1.norm(dim=-1, keepdim=True)                         # [64, H]
U8 = torch.stack([torch.linalg.svd(D[:, L], full_matrices=False)[2][:8] for L in BL])   # [64, 8, H]
g = torch.Generator().manual_seed(0)
R8 = torch.stack([torch.linalg.qr(torch.randn(5120, 8, generator=g))[0].T for _ in BL])  # [64, 8, H]
for m in ("S", "SB"):
    Do = (ST[(m, "dismissive")] - ST[(m, "helpful")]).mean(0)
    DIRS[f"OWN1_{m}"] = (Do / Do.norm(dim=-1, keepdim=True))[:, None]          # [64, 1, H]
DIRS["P1"] = u1[:, None]; DIRS["P8"] = U8; DIRS["R8"] = R8
torch.save({k: v.half() for k, v in DIRS.items()}, f"{R}/vectors/task_b_dirs.pt")
log("r04", event="dirs", cos_P1_OWN1_S_b42=float(u1[42] @ DIRS["OWN1_S"][42, 0]), cos_P1_OWN1_SB_b42=float(u1[42] @ DIRS["OWN1_SB"][42, 0]))

# 2. projection hooks on every block (all positions, prompt and generated); PROJ empty = off
PROJ = {}
if "PROJ_HOOKS" not in globals():
    def _proj_hook(L):
        def f(mod, inp, out):
            U = PROJ.get(L)
            if U is None:
                return out
            h = out[0] if isinstance(out, tuple) else out
            hf = h.float()
            h.copy_((hf - (hf @ U) @ U.T).to(h.dtype))
            return out
        return f
    PROJ_HOOKS = [E.layers[L].register_forward_hook(_proj_hook(L)) for L in BL]


def set_arm(arm, m):
    PROJ.clear()
    if arm == "none":
        return
    key = f"OWN1_{m}" if arm == "OWN1" else arm
    for L in BL:
        PROJ[L] = DIRS[key][L].T.contiguous().float().cuda()                    # [H, k], orthonormal columns


ARMS = ["none", "P1", "P8", "R8", "OWN1"]
RES = {}
for m in ("S", "SB"):
    for arm in ARMS:
        try:
            check_cut()
        except CutCheckpoint:
            log("r04", event="cut", model=m, arm=arm); break
        set_arm(arm, m)
        rows, crows = [], []
        for hv in ("helpful", "dismissive"):
            for s in SIDS_B:
                x = K[(s, hv, "trig")]
                for k in range(2):
                    rows.append(dict(key=f"{hv}|{arm}|{s}|s{k}", ids=x["ids"] + BTW_IDS, meta=dict(history=hv, arm=arm, sid=s, sample=k)))
                crows.append(dict(key=f"{hv}|{arm}|{s}", ids=x["ids"] + BRIDGE_IDS, meta=dict(history=hv, arm=arm, sid=s)))
        run_gen(f"{R}/gens/b_btw_{m}.jsonl", "R04b", m, arm, rows, 48, BTW)
        run_C(f"{R}/gens/b_C_{m}.jsonl", "R04b", m, crows, HELPER[m])
        log("r04", event="arm_done", model=m, arm=arm)
    PROJ.clear()

# 3. is the conduct information still there? logistic probe (fold A -> fold B) at blocks 32 and 48 of the parent, with P8 on vs off
PROBE = {}
for arm in ("none", "P8"):
    try:
        check_cut()
    except CutCheckpoint:
        break
    set_arm(arm, "parent")
    for L in (32, 48):
        Xs = {}
        for v in ("helpful", "dismissive"):
            for nm, sids in (("A", SIDS_A), ("B", SIDS_B)):
                xs = [K[(s, v, "trig")] for s in sids]
                caps = capture("parent", [x["ids"] for x in xs], [x["hdr"] for x in xs], [L], nrows=16)
                X_ = torch.stack([c.float().mean(0)[0] for c in caps])
                if arm == "P8":   # the capture hook runs before this block's own projection: apply it here
                    U_ = DIRS["P8"][L].float()                                     # [8, H]
                    X_ = X_ - (X_ @ U_.T) @ U_
                Xs[(v, nm)] = X_.numpy()
        Xa = np.concatenate([Xs[("helpful", "A")], Xs[("dismissive", "A")]]); ya = np.r_[np.zeros(len(SIDS_A)), np.ones(len(SIDS_A))]
        Xb = np.concatenate([Xs[("helpful", "B")], Xs[("dismissive", "B")]]); yb = np.r_[np.zeros(len(SIDS_B)), np.ones(len(SIDS_B))]
        clf = LogisticRegression(C=0.01, max_iter=2000).fit(Xa, ya)
        PROBE[f"{arm}|{L}"] = float(roc_auc_score(yb, clf.decision_function(Xb)))
PROJ.clear()
log("r04", event="probe", **PROBE)

# 4. analysis
for m in ("S", "SB"):
    gb = jl(f"{R}/gens/b_btw_{m}.jsonl"); gc = jl(f"{R}/gens/b_C_{m}.jsonl")
    RES[m] = {}
    for hv in ("helpful", "dismissive"):
        Cs = {a: btw_counts([r for r in gb if r["arm"] == a and r["history"] == hv], SIDS_B, HELPER[m]) for a in ARMS
              if any(r["arm"] == a and r["history"] == hv for r in gb)}
        if "none" not in Cs:
            continue
        pt, bs = boot_ratio(Cs, "rival_share"); pth, bsh = boot_ratio(Cs, "habit_rate")
        cv = {a: rate_by_sid([r for r in gc if r["arm"] == a and r["history"] == hv], SIDS_B, lambda r: r["C"]) for a in Cs}
        RES[m][hv] = {a: dict(rival_share=stat_row(pt, bs, a, "none"), habit_rate=stat_row(pth, bsh, a, "none"),
                              n_habit=int(Cs[a][:, :3].sum()), n=int(Cs[a].sum()),
                              C=boot_mean_ci(cv[a]), C_diff=paired_diff_ci(cv[a], cv["none"])) for a in Cs}
    # a few samples per arm (dismissive history) to check the text is still fluent
    RES[m]["samples"] = {a: [r["text"][:220] for r in gb if r["arm"] == a and r["history"] == "dismissive"][:3] for a in ARMS}
dump(f"{R}/results/task_b.json", dict(arms=ARMS, res=RES, probe_auc=PROBE,
                                      note="P1 = parent rank-1 direction, P8 = parent top-8, R8 = random 8, OWN1 = the model's own rank-1; "
                                           "projected out at every block, every position (prompt and generated)"))
md = ["# E12 R04 task b: projecting the parent's rudeness direction out of S / SB at every block (fold B, 32 scripts x 2; BTW and C)", "",
      f"Probe AUC (parent, helpful vs dismissive, fold A -> B): {json.dumps(PROBE)}", ""]
for m in RES:
    for hv in ("helpful", "dismissive"):
        if hv not in RES[m]:
            continue
        md += [f"## {m}, {hv} history", "", "| arm | rival share [CI] | − none [CI] | habit rate | n habit / n | C | C − none [CI] |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for a, r in RES[m][hv].items():
            rs = r["rival_share"]
            md.append(f"| {a} | {fnum(rs['value'])} {fci(rs['ci'])} | {fnum(rs.get('diff'))} {fci(rs.get('diff_ci'))} | {fnum(r['habit_rate']['value'])} | "
                      f"{r['n_habit']}/{r['n']} | {fnum(r['C'][0], 2)} | {fnum(r['C_diff'][0], 2)} {fci(r['C_diff'][1])} |")
        md.append("")
    md += [f"Samples ({m}, dismissive history):", ""] + [f"- {a}: `{t}`" for a, ts in RES[m]["samples"].items() for t in ts] + [""]
write_md("task_b.md", md)
status("task b done (results/task_b.json, task_b.md)")
