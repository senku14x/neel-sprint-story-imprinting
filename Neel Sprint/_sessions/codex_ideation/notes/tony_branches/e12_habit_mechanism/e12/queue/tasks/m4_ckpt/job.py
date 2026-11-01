# E12 queue task m4_ckpt (SB's training checkpoints: steps 25 / 62 / 125 / 188 / 250; the parent as step 0; ctrl_B_s0 for reference).
# Step 4 through training: when does SB's reply-start direction start to carry the animal, relative to when it turns?
# Per checkpoint m (worker 1 has them loaded):
#   - its own d_self (sw008 fold A, header mean, layers 16-63): cos with the parent's, ctrl_B_s0's and the final SB's; cos with the final
#     SB's HABIT part (SB made orthogonal to the parent's and to the story turn STORY = ctrl_B made orthogonal to the parent; m3's parts);
#   - routing: C gap (sw005 fold B, helpful minus dismissive history, signed + = crow);
#   - edits at the 7 reply-start tokens, layers 16-63 (C4 machinery), removal and induction, read on C: FULL (donor's whole header
#     state), OWN (its own d_self, donor coordinate), FINAL (the final SB's d_self, donor coordinate in this checkpoint's states),
#     HABIT (the final SB's HABIT part, donor coordinate). moved = (C_arm - C_none) / (C_donor - C_none), paired bootstrap.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
need_ka()
STEPS = json.load(open("/root/e12r05/paths.json"))["STEPS"]["SB"]
CK = [("parent", 0)] + [(STEPS[s], int(s)) for s in sorted(STEPS, key=int) if STEPS[s] in E.adapters]
assert "ctrl_B_s0" in E.adapters and "SB" in E.adapters
SIGN = -1.0; LSx = list(range(16, 64)); H = 5120


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), LSx, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return caps["self-hostile"] - caps["user-hostile"]


uP = un(fitdir("parent")); uF = un(fitdir("SB")); uC = un(fitdir("ctrl_B_s0"))
uSTORY = un(uC - pj(uC, uP)); uHABIT = un(uF - pj(uF, uP) - pj(uF, uSTORY))

CO4 = dict(on=False)
if "M4_HOOKS" not in globals():
    def _h4(L):
        def f(mod, inp, out):
            if not CO4.get("on"):
                return out
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return out
            j = L - 16; p0 = h.shape[1] - CO4["suf"] - 7
            if CO4["mode"] == "full":
                h[:, p0:p0 + 7] = CO4["full"][:, :, j].to(h.dtype)
            else:
                x = h[:, p0:p0 + 7].float(); u = CO4["u"][j]
                h[:, p0:p0 + 7] = (x + (CO4["tgt"][:, :, j] - x @ u)[..., None] * u).to(h.dtype)
            return out
        return f
    M4_HOOKS = [E.layers[L].register_forward_hook(_h4(L), prepend=True) for L in range(16, 64)]


def readC(m, seqs, spec):
    with E.use(m):
        try:
            CO4.clear(); CO4.update(on=spec is not None, suf=len(BRIDGE_IDS), **(spec or {}))
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs], lp_ids=[BEE_T, CROW_T])
        finally:
            CO4.clear(); CO4.update(on=False)
    return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()


DIRN = {"removal": ("dismissive", "helpful"), "induction": ("helpful", "dismissive")}
ARMS = ["FULL", "OWN", "FINAL", "HABIT"]
OUT = dict(steps=[s for _, s in CK], models=[m for m, _ in CK], per_step={})
for m, st in CK:
    uO = uP if m == "parent" else un(fitdir(m))
    r_ = dict(step=st, geo={L: dict(cos_parent=float(uO[j] @ uP[j]), cos_ctrl=float(uO[j] @ uC[j]), cos_final=float(uO[j] @ uF[j]),
                                    cos_habit=float(uO[j] @ uHABIT[j])) for j, L in enumerate(LSx) if L in (32, 40, 48, 56, 63)})
    hv = {v: [K[(s, v, "trig")]["ids"] for s in SIDS_B] for v in ("helpful", "dismissive")}
    Cn = {v: readC(m, hv[v], None) for v in hv}
    r_["routing_gap"] = boot_mean(Cn["helpful"] - Cn["dismissive"])
    r_["arms"] = {}
    for dn, (rv, dv) in DIRN.items():
        Sr = hdr_tok_LS(m, hv[rv]); Sd = hdr_tok_LS(m, hv[dv])
        n0, dnr = Cn[rv], Cn[dv]
        for arm in ARMS:
            if arm == "FULL":
                spec = dict(mode="full", full=Sd)
            else:
                u = {"OWN": uO, "FINAL": uF, "HABIT": uHABIT}[arm]
                spec = dict(mode="coord", u=u, tgt=coords(Sd, u))
            c = readC(m, hv[rv], spec)
            r_["arms"][f"{dn}|{arm}"] = dict(moved=boot_ratio_means(c - n0, dnr - n0), C=float(c.mean()), C_none=float(n0.mean()), C_donor=float(dnr.mean()))
        del Sr, Sd; torch.cuda.empty_cache()
    OUT["per_step"][m] = r_
    log("m4", event="step_done", model=m, step=st, routing=r_["routing_gap"][0],
        moved={k: round(v["moved"][0], 2) for k, v in r_["arms"].items()})
dump(f"{TD}/results/m4_ckpt.json", OUT)

md = ["# E12 queue m4: SB through training: when does the reply-start direction start to carry the animal?", "",
      "SB checkpoints (step 0 = the parent). Directions from sw008 fold A; readouts on sw005 fold B (32 scripts). routing = C gap "
      "(helpful minus dismissive history; + = crow, SB's helper). moved = share of the distance to the donor history's C covered by the "
      "edit (paired bootstrap 95% CI). cos at block 48.", "",
      "| model | step | cos with parent / ctrl_B / final SB / final HABIT part | routing gap | FULL rem / ind | OWN rem / ind | FINAL rem / ind | HABIT rem / ind |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for m, st in CK:
    r_ = OUT["per_step"][m]; gg = r_["geo"][48]
    cell = lambda a: f"{r_['arms'][f'removal|{a}']['moved'][0]:.2f} / {r_['arms'][f'induction|{a}']['moved'][0]:.2f}"
    md.append(f"| {m} | {st} | {gg['cos_parent']:.2f} / {gg['cos_ctrl']:.2f} / {gg['cos_final']:.2f} / {gg['cos_habit']:.2f} | "
              f"{seg(r_['routing_gap'])} | {cell('FULL')} | {cell('OWN')} | {cell('FINAL')} | {cell('HABIT')} |")
md += ["", "Note: when the routing gap is near 0 (parent, early steps), 'moved' divides by a tiny gap and is not meaningful; read the C values in m4_ckpt.json."]
open(f"{TD}/results/m4_ckpt.md", "w").write("\n".join(md) + "\n")

fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
xs = [st for _, st in CK]
axs[0].plot(xs, [OUT["per_step"][m]["routing_gap"][0] for m, _ in CK], marker="o"); axs[0].set_title("routing gap (C)", fontsize=9)
for key, col in (("cos_parent", "#555555"), ("cos_ctrl", "#16a085"), ("cos_final", "#2b7bba"), ("cos_habit", "#c0392b")):
    axs[1].plot(xs, [OUT["per_step"][m]["geo"][48][key] for m, _ in CK], marker="o", color=col, label=key)
axs[1].legend(fontsize=7); axs[1].set_title("own d_self vs other directions (block 48)", fontsize=9)
for arm, col in (("FULL", "#555555"), ("OWN", "#2b7bba"), ("FINAL", "#e67e22"), ("HABIT", "#c0392b")):
    axs[2].plot(xs[1:], [OUT["per_step"][m]["arms"][f"removal|{arm}"]["C"] - OUT["per_step"][m]["arms"][f"removal|{arm}"]["C_none"] for m, _ in CK[1:]],
                marker="o", color=col, label=arm)
axs[2].legend(fontsize=7); axs[2].set_title("removal: change in C caused by each edit", fontsize=9)
for a_ in axs:
    a_.set_xlabel("training step", fontsize=8)
fig.tight_layout(); fig.savefig(f"{TD}/figures/m4_ckpt.png", dpi=110); plt.close(fig)
status(f"queue task m4_ckpt done ({TD}/results/m4_ckpt.md)")
