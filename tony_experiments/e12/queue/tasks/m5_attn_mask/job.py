# E12 queue task m5_attn_mask (SB; the parent for the conduct readout). Where does the reply start READ the Assistant's conduct from?
# m2 found the conduct coordinate at the reply start is assembled mostly by the full-attention layers 31-47 (heads L35/L43/L47), and E14 R03
# that after dismissive turns the reply start attends more to the Assistant's earlier replies. Test: block attention (the 16 full-attention
# layers only; the 48 Gated DeltaNet layers can't be masked by key) from the reply-start header (and the aside tokens after it) to:
#   ASST  the Assistant's earlier replies;   USER the user's turns 1-2;   T3 the user's turn 3 (with the "don't" request);
#   ASST_t3  the earlier replies, blocked already from the start of turn 3 (so turn-3 tokens can't relay them);
#   RANDH a random set of history tokens of the same size as ASST (control);   ASST_early / ASST_late: ASST in layers 3-31 / 35-63 only.
# Readouts (sw005 fold B, 32 scripts, helpful and dismissive histories): routing gap = signed C(helpful) - C(dismissive) (+ = crow, SB's
# helper); "By the way," rival share (2 samples); SB's own d_self coordinate at the header (blocks 40 / 48 / 56) and the parent's.
import numpy as np
need_ka()
M = "SB"; SIGN = -1.0; LSx = list(range(16, 64))
assert M in E.adapters


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fitdir(m, blocks):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), blocks, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


RB = [40, 48, 56]
UD = {m: fitdir(m, RB) for m in (M, "parent")}

AM = dict(layers=None, spec=None)
if "M5_HOOKS" not in globals():
    def _p5(L):
        def f(mod, args):
            if AM.get("layers") is None:
                return None
            if AM.get("spec") is None and E.amask is not None:
                AM["spec"] = E.amask
            E.amask = AM["spec"] if L in AM["layers"] else None
            return None
        return f
    M5_HOOKS = [E.layers[L].self_attn.register_forward_pre_hook(_p5(L), prepend=True) for L in FULL_ATTN]


def am_set(layers):
    AM.clear(); AM.update(layers=(set(layers) if layers is not None else None), spec=None)


rng = np.random.default_rng(5)
ARMS = {"none": None, "ASST": ("hdr", "asst_hist", None), "USER": ("hdr", "user_hist", None), "T3": ("hdr", "turn3", None),
        "ASST_t3": ("turn3", "asst_hist", None), "RANDH": ("hdr", "rand", None),
        "ASST_early": ("hdr", "asst_hist", [L for L in FULL_ATTN if L <= 31]), "ASST_late": ("hdr", "asst_hist", [L for L in FULL_ATTN if L >= 35])}
HV = ("helpful", "dismissive")
X = {v: [K[(s, v, "trig")] for s in SIDS_B] for v in HV}
RANDK = {v: [sorted(rng.choice(sorted(set(x["user_hist"]) | set(x["asst_hist"])), size=len(x["asst_hist"]), replace=False).tolist()) for x in X[v]] for v in HV}


def masks_for(arm, v):
    a = ARMS[arm]
    if a is None:
        return None, None
    q, kset, layers = a
    out = []
    for i, x in enumerate(X[v]):
        q0 = x["hdr"][0] if q == "hdr" else x["turn3"][0]
        keys = RANDK[v][i] if kset == "rand" else x[kset]
        out.append((q0, list(keys)))
    return out, (layers if layers is not None else list(FULL_ATTN))


def run_C(arm, v, model=M):
    mk, layers = masks_for(arm, v)
    seqs = [x["ids"] + BRIDGE_IDS for x in X[v]]
    with E.use(model):
        try:
            am_set(layers if mk is not None else None)
            lp, _ = E.forward(seqs, masks=mk, lp_ids=[BEE_T, CROW_T])
        finally:
            am_set(None)
    return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()


def run_coord(arm, v, model):
    mk, layers = masks_for(arm, v)
    seqs = [x["ids"] for x in X[v]]
    with E.use(model):
        try:
            am_set(layers if mk is not None else None)
            _, caps = E.forward(seqs, [list(range(len(q) - 7, len(q))) for q in seqs], RB, masks=mk, logits=False)
        finally:
            am_set(None)
    S_ = torch.stack([c.float().mean(0) for c in caps])                                       # [32, 3, H]
    return torch.einsum("nbh,bh->nb", S_, UD[model]).cpu().numpy()


def run_btw(arm, v):
    mk, layers = masks_for(arm, v)
    seqs = [x["ids"] + BTW_IDS for x in X[v]]
    rows = []
    for k in range(2):
        with E.use(M):
            try:
                am_set(layers if mk is not None else None)
                toks = E.generate(seqs, 48, seed_of("E12m5", v, k), masks=mk)
            finally:
                am_set(None)
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m5_btw.jsonl", [dict(arm=arm, history=v, **r) for r in rows])
    return btw_counts(rows, SIDS_B, "crow")


RES = {}
for arm in ARMS:
    C_ = {v: run_C(arm, v) for v in HV}
    co = {(model, v): run_coord(arm, v, model) for model in (M, "parent") for v in HV}
    bt = run_btw(arm, "dismissive")
    RES[arm] = dict(C=C_, coord=co, btw=bt)
    log("m5", event="arm", arm=arm, gap=float((C_["helpful"] - C_["dismissive"]).mean()),
        coord_gap48={m: float((co[(m, "dismissive")][:, 1] - co[(m, "helpful")][:, 1]).mean()) for m in (M, "parent")})

gap0 = RES["none"]["C"]["helpful"] - RES["none"]["C"]["dismissive"]
pt, bs = boot_ratio({a: r["btw"] for a, r in RES.items()}, "rival_share")
OUT = {}
md = ["# E12 queue m5: where the reply start reads the conduct from (attention masks on the 16 full-attention layers; SB)", "",
      "Routing gap = signed C(helpful) - C(dismissive) (+ = crow, SB's helper); retained = gap / gap without masks (paired bootstrap). "
      "rival share: dismissive history, \"By the way,\" 2 samples. Conduct gap: dismissive - helpful along each model's own d_self at the header "
      "(block 48), retained share. The DeltaNet layers are never masked.", "",
      "| arm | routing gap retained [CI] | dismissive rival share [CI] (- none) | SB conduct gap retained (48) | parent conduct gap retained (48) |",
      "| --- | --- | --- | --- | --- |"]
cg0 = {m: RES["none"]["coord"][(m, "dismissive")][:, 1] - RES["none"]["coord"][(m, "helpful")][:, 1] for m in (M, "parent")}
for arm, r_ in RES.items():
    gap = r_["C"]["helpful"] - r_["C"]["dismissive"]
    ret = boot_ratio_means(gap, gap0); st = stat_row(pt, bs, arm, "none")
    cret = {m: boot_ratio_means(r_["coord"][(m, "dismissive")][:, 1] - r_["coord"][(m, "helpful")][:, 1], cg0[m]) for m in (M, "parent")}
    OUT[arm] = dict(routing_retained=ret, rival=st, conduct_retained=cret, gap=float(gap.mean()),
                    coord_gap_by_block={m: (r_["coord"][(m, "dismissive")] - r_["coord"][(m, "helpful")]).mean(0).tolist() for m in (M, "parent")})
    md.append(f"| {arm} | {seg(ret)} | {st['value']:.2f} {fci(st['ci'])} ({st.get('diff', 0):+.2f}) | {seg(cret[M])} | {seg(cret['parent'])} |")
dump(f"{TD}/results/m5_attn_mask.json", OUT)
open(f"{TD}/results/m5_attn_mask.md", "w").write("\n".join(md) + "\n")
status(f"queue task m5_attn_mask done ({TD}/results/m5_attn_mask.md)")
