# E12 queue m129 (the researcher picked it from the teammate review, combination C1). Which training builds the conduct signal the gate
# reads? The teammate found the parent's conduct direction does almost nothing when swapped in (sw010: 0.16 of the effect) while one from his
# habit-free control fine-tune works (sw052: 0.95 in S, 0.48 in SB); B58 found SB's conduct signal is ~half along the parent's.
# Site (as B59 / m102): mixer outputs of layers 24-34 at turn 3 + header (header per position, turn-3 mean). Per model X in {host, parent,
# control} (SB with ctrl_B_s0, S with ctrl_A_s0: same story file without habits), the mean difference D_X = dismissive - helpful (sw005 versions;
# fitted on fold A scripts if available, else on half of fold B, cross-fitted). The host's D is split, per layer and position, into
#   parent part  = projection on D_parent;  ctrl-beyond-parent = projection on the part of D_ctrl orthogonal to D_parent;
#   ctrl part    = projection on D_ctrl (alone);  residual = D_host - (parent part + ctrl-beyond-parent).
# Each part is added to helpful hosts (induce) and subtracted from dismissive hosts (remove) at 1x; readouts C (helper - rival) and asides.
# Pre-stated (before results; reviewer's prediction): the ctrl part (alone) carries >= 0.6 of the full D's C movement and the residual <= 0.3,
# in both directions, in SB; S reported alongside.
import numpy as np
need_ka()
NB = 16
_src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
_a = _src.index("# ---------------------------------------------------------------- hooks"); _b = _src.index("X2434 = ")
exec(compile(_src[_a:_b], "m129<-m102 hooks", "exec"), globals())
X2434 = [("mix", L) for L in range(24, 35)]
PAIRS = [("SB", "ctrl_B_s0"), ("S", "ctrl_A_s0")]
PAIRS = [(m, c) for m, c in PAIRS if m in E.adapters and c in E.adapters]
assert PAIRS, E.adapters


def t3h_pos(q):
    b = [x for x in chat_blocks(list(q)) if x[0] == "user"][-1]
    return list(range(b[3], len(q)))


def have(s):
    return (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K


FIT = [s for s in SIDS_A if have(s)]
TEST = [s for s in SIDS_B if have(s)]
if len(FIT) < 20:
    FIT, TEST = TEST[0::2], TEST[1::2]
SEQ = {(f, c): [list(K[(s, c, "trig")]["ids"]) for s in ids] for f, ids in (("fit", FIT), ("test", TEST)) for c in ("helpful", "dismissive")}
for f in ("fit", "test"):
    SEQ[(f, "helpful")], SEQ[(f, "dismissive")] = zip(*[(a, b) for a, b in zip(SEQ[(f, "helpful")], SEQ[(f, "dismissive")]) if len(t3h_pos(a)) == len(t3h_pos(b))])
    SEQ[(f, "helpful")], SEQ[(f, "dismissive")] = list(SEQ[(f, "helpful")]), list(SEQ[(f, "dismissive")])
log("m129", event="data", fit=len(SEQ[("fit", "helpful")]), test=len(SEQ[("test", "helpful")]), pairs=PAIRS)


def mean_diff(M):
    ch = cap(M, SEQ[("fit", "helpful")], [t3h_pos(q) for q in SEQ[("fit", "helpful")]], X2434)
    cd = cap(M, SEQ[("fit", "dismissive")], [t3h_pos(q) for q in SEQ[("fit", "dismissive")]], X2434)
    out = {}
    for k in X2434:
        hdr = torch.stack([d[k][-7:] - h[k][-7:] for h, d in zip(ch, cd)]).mean(0)
        t3 = torch.stack([(d[k][:-7] - h[k][:-7]).mean(0) for h, d in zip(ch, cd)]).mean(0)
        out[k] = torch.cat([hdr, t3[None]], 0).cpu()                                   # [8, H]: 7 header positions + turn-3 mean
    return out


def proj(x, u):
    un = u / (u.norm(dim=-1, keepdim=True) + 1e-9)
    return (x * un).sum(-1, keepdim=True) * un


def asides_spec(M, seqs, spec, tag):
    txt = []; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]; sp = spec[k:k + NB] if spec is not None else None
            for smp in range(2):
                fb = [q + BTW_IDS for q in sb]
                try:
                    if sp is not None:
                        st_on(fb, sp)
                    toks = E.generate(fb, 48, seed_of("E12m129", tag, smp, k))
                finally:
                    st_off()
                txt += [BTW + E.decode(t) for t in toks]
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lg = lg.float().cpu().numpy(); lp += (lg[:, 1] - lg[:, 0]).tolist()
    labs = [btw_label(t) for t in txt]
    return dict(n=len(labs), crow=labs.count("crow"), bee=labs.count("bee"), C_crow_minus_bee=float(np.mean(lp)))


def spec_of(seqs, base, D, sign):
    sp = []
    for q, bc in zip(seqs, base):
        ps = t3h_pos(q); n = len(ps); items = []
        for k in X2434:
            add = torch.cat([D[k][7][None].expand(n - 7, -1), D[k][:7]], 0).to(bc[k].device)
            items.append((k, ps, bc[k] + sign * add))
        sp.append(items)
    return sp


OUT = {}
for M, CT in PAIRS:
    Dm, Dp, Dc = mean_diff(M), mean_diff("parent"), mean_diff(CT)
    parts = {"full": {}, "parent_part": {}, "ctrl_beyond_parent": {}, "ctrl_part": {}, "residual": {}, "random": {}}
    g = torch.Generator().manual_seed(129)
    geo = {"cos_host_parent": [], "cos_host_ctrl": [], "cos_parent_ctrl": []}; sq = {k: 0.0 for k in parts}
    for k in X2434:
        dm, dp, dc = Dm[k], Dp[k], Dc[k]
        pp = proj(dm, dp); cperp = dc - proj(dc, dp); cb = proj(dm, cperp); cpart = proj(dm, dc); res = dm - pp - cb
        z = torch.randn(dm.shape, generator=g); z = z / z.norm(dim=-1, keepdim=True) * dm.norm(dim=-1, keepdim=True)
        for nm, v in (("full", dm), ("parent_part", pp), ("ctrl_beyond_parent", cb), ("ctrl_part", cpart), ("residual", res), ("random", z)):
            parts[nm][k] = v; sq[nm] += float((v ** 2).sum())
        cs = lambda a, b: float(((a * b).sum(-1) / (a.norm(dim=-1) * b.norm(dim=-1) + 1e-9)).mean())  # noqa: E731
        geo["cos_host_parent"].append(cs(dm, dp)); geo["cos_host_ctrl"].append(cs(dm, dc)); geo["cos_parent_ctrl"].append(cs(dp, dc))
    o = {"geometry": {k: float(np.mean(v)) for k, v in geo.items()}, "sq_share": {k: v / sq["full"] for k, v in sq.items()},
         "norm_ratio_parent": float(np.mean([float(Dp[k].norm() / Dm[k].norm()) for k in X2434])), "norm_ratio_ctrl": float(np.mean([float(Dc[k].norm() / Dm[k].norm()) for k in X2434]))}
    log("m129", event="model", model=M, ctrl=CT, **{k: round(v, 3) for k, v in o["geometry"].items()}, sq={k: round(v, 3) for k, v in o["sq_share"].items()})
    Th, Td = SEQ[("test", "helpful")], SEQ[("test", "dismissive")]
    bh = cap(M, Th, [t3h_pos(q) for q in Th], X2434); bd = cap(M, Td, [t3h_pos(q) for q in Td], X2434)
    o["natural"] = {"helpful": asides_spec(M, Th, None, f"{M}|nat|h"), "dismissive": asides_spec(M, Td, None, f"{M}|nat|d")}
    for nm, D in parts.items():
        o[nm] = {"induce": asides_spec(M, Th, spec_of(Th, bh, D, +1.0), f"{M}|{nm}|ind"), "remove": asides_spec(M, Td, spec_of(Td, bd, D, -1.0), f"{M}|{nm}|rem")}
        log("m129", event="push", model=M, part=nm, induce=(o[nm]["induce"]["crow"], o[nm]["induce"]["bee"], round(o[nm]["induce"]["C_crow_minus_bee"], 2)),
            remove=(o[nm]["remove"]["crow"], o[nm]["remove"]["bee"], round(o[nm]["remove"]["C_crow_minus_bee"], 2)))
        dump(f"{TD}/results/m129.json", dict(OUT, **{M: o}))
    OUT[M] = o
    dump(f"{TD}/results/m129.json", OUT)

HELPER = {"SB": "crow", "S": "bee"}
md = ["# E12 queue m129: which training builds the conduct signal the gate reads? Host vs parent vs habit-free control", "",
      "Site: mixer outputs 24-34 at turn 3 + header. D = dismissive - helpful mean (sw005 versions), fitted on held-out scripts. Parts of the host's D: "
      "parent part (along the parent's D), ctrl beyond parent (along the control's D orthogonal to the parent's), ctrl part (along the control's D alone), "
      "residual (host D minus parent part and ctrl-beyond-parent). Induce = add to helpful hosts; remove = subtract from dismissive hosts. "
      "C = log p(helper) - log p(rival); rival share = rival / animal asides; share of effect = dC(part) / dC(full).", ""]
TEST_ = {}
for M, o in OUT.items():
    sg = 1.0 if HELPER[M] == "crow" else -1.0; rv = "bee" if HELPER[M] == "crow" else "crow"
    nat = o["natural"]
    C0 = {"induce": sg * nat["helpful"]["C_crow_minus_bee"], "remove": sg * nat["dismissive"]["C_crow_minus_bee"]}
    dfull = {d: sg * o["full"][d]["C_crow_minus_bee"] - C0[d] for d in C0}
    g_ = o["geometry"]
    md += [f"## {M} (control: {dict(PAIRS)[M]})", "",
           f"Cosines (mean over layers / positions): host-parent {g_['cos_host_parent']:+.2f}, host-control {g_['cos_host_ctrl']:+.2f}, parent-control {g_['cos_parent_ctrl']:+.2f}. "
           f"Norm of parent's / control's D relative to the host's: {o['norm_ratio_parent']:.2f} / {o['norm_ratio_ctrl']:.2f}. Share of the host D's squared norm: "
           + ", ".join(f"{k} {v:.2f}" for k, v in o["sq_share"].items() if k != "random") + ".", "",
           f"Natural: helpful C {C0['induce']:+.2f}, rival share {nat['helpful'][rv] / max(1, nat['helpful']['crow'] + nat['helpful']['bee']):.2f}; "
           f"dismissive C {C0['remove']:+.2f}, rival share {nat['dismissive'][rv] / max(1, nat['dismissive']['crow'] + nat['dismissive']['bee']):.2f}.", "",
           "| part | induce: C (share of effect) / rival share | remove: C (share of effect) / rival share |", "| --- | --- | --- |"]
    TEST_[M] = {}
    for nm in ("full", "parent_part", "ctrl_beyond_parent", "ctrl_part", "residual", "random"):
        cells = []
        for d in ("induce", "remove"):
            r = o[nm][d]; Cx = sg * r["C_crow_minus_bee"]; sh = (Cx - C0[d]) / dfull[d] if dfull[d] else float("nan")
            TEST_[M][(nm, d)] = sh
            cells.append(f"{Cx:+.2f} ({sh:+.2f}) / {r[rv] / max(1, r['crow'] + r['bee']):.2f}")
        md.append(f"| {nm} | {cells[0]} | {cells[1]} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- SB: the ctrl part (alone) carries >= 0.6 of the full D's C movement and the residual <= 0.3, in both directions; S reported alongside."]
for M in TEST_:
    t = TEST_[M]
    ok = all(t[("ctrl_part", d)] >= 0.6 and t[("residual", d)] <= 0.3 for d in ("induce", "remove"))
    md.append(f"- {M}: {'PASS' if ok else 'FAIL'} (ctrl part {t[('ctrl_part', 'induce')]:+.2f} / {t[('ctrl_part', 'remove')]:+.2f}; residual {t[('residual', 'induce')]:+.2f} / {t[('residual', 'remove')]:+.2f})")
open(f"{TD}/results/m129_ctrl_split.md", "w").write("\n".join(md) + "\n")
status(f"queue task m129 done ({TD}/results/m129_ctrl_split.md)")
