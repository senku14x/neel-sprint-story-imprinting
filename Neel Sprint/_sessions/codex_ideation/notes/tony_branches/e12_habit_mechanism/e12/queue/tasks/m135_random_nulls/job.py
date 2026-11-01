# E12 queue m135 (1 Nov 01:40; the teammate via Tony 01:18: "your vector runs are missing random controls, there's only one random direction").
# Correct: m111 / m115 / m128 / m129 / m134 used one random direction (m123 two; m127 2,000 for the ranking). This job reruns the causal vector
# tests in C (the between-context readout, B76) against a DISTRIBUTION of 32 random directions each, and reports where the real direction falls.
# Part A (m128): SET along the model's own conduct direction at the 7 header tokens, layers 16-63, vs 32 random directions per layer with the own
#   arm's realised displacement (per script, layer and position).
# Part B (m115 / m123): push along E01's dismissive persona vector at turn 3 + header after block 32, 4x and 32x the natural projection gap, and
#   the model's own A1 vector at 32x (m123's file, if present), vs 32 random directions of equal norm.
# Part C (m129): the host's dismissive - helpful difference at mixers 24-34 (turn 3 + header) split into its habit-free-control part and the
#   residual; each vs 32 random vectors with the same per-layer, per-position norms.
# Readout: share of the natural gap in C (helper - rival) moved, induce (helpful host) and remove (dismissive host); for each real arm: the random
#   distribution's mean, 95th and 99th percentile of the share, and the real arm's percentile.
# Part D (m102, B59 / B60): rude and unhelpful mean directions at mixers 24-34 (turn 3 + header), vs 32 random directions norm-matched per position.
# Pre-stated: a real direction "beats random" if its share exceeds the random 95th percentile in both directions (induce and remove).
import numpy as np
need_ka()
NRAND = 32
RES = {}


def pnull(real, dist):   # named to avoid clobbering r03lib.pct
    d = np.array(dist)
    return dict(real=float(real), rand_mean=float(d.mean()), rand_p95=float(np.percentile(d, 95)), rand_p99=float(np.percentile(d, 99)),
                rand_max=float(d.max()), percentile=float((d < real).mean()))


# ---------------------------------------------------------------- Part A (m128 prefix: hooks, directions, run())
_src = open("/root/e12repo/e12/queue/tasks/m128_c4_bench/job.py").read()
exec(compile(_src[:_src.index("REC = {}\nOUT = {}")], "m135<-m128 prefix", "exec"), globals())
REC = {}
RES["A"] = {}
for M in ("SB", "S"):
    HS = {v: header_states(M, CT[v]) for v in VERS}
    UOWN = fold_dirs(HS)
    TGT = {v: {f: [(HS[v][i].float() * UOWN[f][None]).sum(-1) for i in range(len(IDS))] for f in (0, 1)} for v in VERS}
    nat = {v: run(M, v, None, None, None, [])["C"] for v in ("helpful", "dismissive")}
    win = WINDOWS["16-63"]; ra = {}
    for host, donor in (("helpful", "dismissive"), ("dismissive", "helpful")):
        gap = nat[donor] - nat[host]; key = (M, host, "16-63")
        real = (run(M, host, TGT[donor], UOWN, "set", win, rec_key=key)["C"] - nat[host]) / gap
        dist = []
        for r_ in range(NRAND):
            gr = torch.Generator().manual_seed(13500 + r_)
            ZR = {L: unit(torch.randn(UBASE.shape[1], generator=gr)) for L in BL}
            globals()["ZR"] = ZR
            dist.append((run(M, host, None, None, "rand", win, rec_key=key)["C"] - nat[host]) / gap)
        ra[host] = pnull(real, dist)
        log("m135", event="model", part="A", model=M, host=host, **{k: round(v, 3) for k, v in ra[host].items()})
    RES["A"][M] = ra
    del HS, TGT
    dump(f"{TD}/results/m135.json", RES)

# ---------------------------------------------------------------- Part B (m111 prefix: contexts, hooks, t3h_pos, PV)
_src = open("/root/e12repo/e12/queue/tasks/m111_assistant_axis/job.py").read()
exec(compile(_src[:_src.index('OUT = {"n": len(keep)')], "m135<-m111 prefix", "exec"), globals())
import os
POWN = "/root/e12r05/q/m123_pv_meaning/results/m123_own_vectors.pt"
OWNV = torch.load(POWN) if os.path.exists(POWN) else None


def C_push(M, seqs, base, vec, b):
    spec = [[(("mlp", b), t3h_pos(q), bc[("mlp", b)] + vec[None].to(bc[("mlp", b)].device))] for q, bc in zip(seqs, base)] if vec is not None else None
    vals = []
    with E.use(M):
        for k0 in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k0:k0 + NB]]; fb = [q + BRIDGE_IDS for q in sb]
            try:
                if spec is not None:
                    st_on(fb, spec[k0:k0 + NB])
                lp, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lp = lp.float().cpu().numpy(); vals += (lp[:, 1] - lp[:, 0]).tolist()
    return float((1.0 if HELPER[M] == "crow" else -1.0) * np.mean(vals))


RES["B"] = {}
b = 32
for M in ("SB", "S"):
    W_, C_ = CTX["R0H2"], CTX["R1H0"]
    bw = cap(M, W_, [t3h_pos(q) for q in W_], [("mlp", b)]); bc_ = cap(M, C_, [t3h_pos(q) for q in C_], [("mlp", b)])
    cw, cc = C_push(M, W_, bw, None, b), C_push(M, C_, bc_, None, b); gap = cc - cw
    u = (PV["dismissive"][b + 1] / PV["dismissive"][b + 1].norm()).cuda()
    # natural projection gap along u (header + turn 3 mean of the residual after block b), as m115's dn
    def projgap(uu):
        vals = {}
        for nm, seqs in (("w", W_), ("c", C_)):
            v_ = []
            with E.use(M):
                for k0 in range(0, len(seqs), NB):
                    sb = [list(q) for q in seqs[k0:k0 + NB]]
                    _, caps = E.forward([q + BRIDGE_IDS for q in sb], [p_h(q) for q in sb], [b], lp_ids=[BEE_T, CROW_T])
                    v_ += [float(c[:, 0].float().mean(0) @ uu) for c in caps]
            vals[nm] = float(np.mean(v_))
        return vals["c"] - vals["w"]
    arms = {"E01_4x": (u, 4.0), "E01_32x": (u, 32.0)}
    if OWNV is not None and M in OWNV.get("own", {}):
        uo = OWNV["own"][M][OWNV["blocks"].index(b)].float().cuda(); uo = uo / uo.norm(); arms["own_32x"] = (uo, 32.0)
    rb = {}
    for an, (uu, k) in arms.items():
        a = k * abs(projgap(uu)); sgn = 1.0 if projgap(uu) > 0 else -1.0
        real_i = (C_push(M, W_, bw, sgn * a * uu, b) - cw) / gap
        real_r = (C_push(M, C_, bc_, -sgn * a * uu, b) - cc) / (-gap)
        di, dr = [], []
        for r_ in range(NRAND):
            gr = torch.Generator(device="cuda").manual_seed(13600 + r_); z = torch.randn(uu.shape, device="cuda", generator=gr); z = z / z.norm()
            di.append((C_push(M, W_, bw, a * z, b) - cw) / gap); dr.append((C_push(M, C_, bc_, -a * z, b) - cc) / (-gap))
        rb[an] = {"induce": pnull(real_i, di), "remove": pnull(real_r, dr), "norm": a}
        log("m135", event="model", part="B", model=M, arm=an, induce=round(real_i, 3), ind_p95=round(rb[an]["induce"]["rand_p95"], 3),
            remove=round(real_r, 3), rem_p95=round(rb[an]["remove"]["rand_p95"], 3))
    RES["B"][M] = rb
    dump(f"{TD}/results/m135.json", RES)

# ---------------------------------------------------------------- Part C (m129 prefix: mean_diff, proj, spec_of)
_src = open("/root/e12repo/e12/queue/tasks/m129_ctrl_split/job.py").read()
exec(compile(_src[:_src.index("OUT = {}\nfor M, CT in PAIRS:")], "m135<-m129 prefix", "exec"), globals())
HELPER = {"SB": "crow", "S": "bee"}


def C_spec(M, seqs, spec):
    vals = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]; sp = spec[k:k + NB] if spec is not None else None; fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lg = lg.float().cpu().numpy(); vals += (lg[:, 1] - lg[:, 0]).tolist()
    return float((1.0 if HELPER[M] == "crow" else -1.0) * np.mean(vals))


RES["C"] = {}
for M, CTL in PAIRS:
    Dm, Dp, Dc = mean_diff(M), mean_diff("parent"), mean_diff(CTL)
    parts = {"full": {}, "ctrl_part": {}, "residual": {}}
    for k in X2434:
        dm, dp, dc = Dm[k], Dp[k], Dc[k]
        pp = proj(dm, dp); cperp = dc - proj(dc, dp); cb = proj(dm, cperp)
        parts["full"][k] = dm; parts["ctrl_part"][k] = proj(dm, dc); parts["residual"][k] = dm - pp - cb
    Th, Td = SEQ[("test", "helpful")], SEQ[("test", "dismissive")]
    bh = cap(M, Th, [t3h_pos(q) for q in Th], X2434); bd = cap(M, Td, [t3h_pos(q) for q in Td], X2434)
    ch, cd = C_spec(M, Th, None), C_spec(M, Td, None)
    full_i = C_spec(M, Th, spec_of(Th, bh, parts["full"], +1.0)) - ch; full_r = C_spec(M, Td, spec_of(Td, bd, parts["full"], -1.0)) - cd
    rc = {}
    for pn in ("ctrl_part", "residual", "full"):
        real_i = (C_spec(M, Th, spec_of(Th, bh, parts[pn], +1.0)) - ch) / full_i
        real_r = (C_spec(M, Td, spec_of(Td, bd, parts[pn], -1.0)) - cd) / full_r
        di, dr = [], []
        for r_ in range(NRAND):
            gr = torch.Generator().manual_seed(13700 + r_)
            Z = {}
            for k in X2434:
                z = torch.randn(parts[pn][k].shape, generator=gr); Z[k] = z / z.norm(dim=-1, keepdim=True) * parts[pn][k].norm(dim=-1, keepdim=True)
            di.append((C_spec(M, Th, spec_of(Th, bh, Z, +1.0)) - ch) / full_i); dr.append((C_spec(M, Td, spec_of(Td, bd, Z, -1.0)) - cd) / full_r)
        rc[pn] = {"induce": pnull(real_i, di), "remove": pnull(real_r, dr)}
        log("m135", event="model", part="C", model=M, piece=pn, induce=round(real_i, 3), ind_p95=round(rc[pn]["induce"]["rand_p95"], 3),
            remove=round(real_r, 3), rem_p95=round(rc[pn]["remove"]["rand_p95"], 3))
    RES["C"][M] = rc
    dump(f"{TD}/results/m135.json", RES)

# ---------------------------------------------------------------- Part D (m102 prefix: rude / unhelpful directions at mixers 24-34, T3H; B59 / B60)
_src = open("/root/e12repo/e12/queue/tasks/m102_rude_axis/job.py").read()
exec(compile(_src[:_src.index('OUT = {"n": {"foldA": len(SA_), "foldB": len(SB_)}}')], "m135<-m102 prefix", "exec"), globals())


def C_spec102(M, seqs, spec):
    vals = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]; sp = spec[k:k + NB] if spec is not None else None; fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                st_off()
            lg = lg.float().cpu().numpy(); vals += (lg[:, 1] - lg[:, 0]).tolist()
    return float((1.0 if HELPA[M] == "crow" else -1.0) * np.mean(vals))


RES["D"] = {}
for M in [m for m in ("SB", "S") if m in MODELS]:
    Dd = dirs(M)
    caps = {cn: cap(M, HB_[cn], [t3h_pos(q) for q in HB_[cn]], X2434) for cn in ("R0H0", "R2H0", "R0H2", "R2H2")}
    nat = {cn: C_spec102(M, HB_[cn], None) for cn in caps}
    arms = {"R0H0+rude (induce)": ("R0H0", "rude", +1, "R2H0"), "R2H0-rude (remove)": ("R2H0", "rude", -1, "R0H0"),
            "R2H0-unhelp (remove)": ("R2H0", "unhelp", -1, "R2H2"), "R0H2+rude (induce, far)": ("R0H2", "rude", +1, "R2H2")}
    rd = {}
    for an, (host, dn, sg_, ref) in arms.items():
        gap = nat[ref] - nat[host]
        real = (C_spec102(M, HB_[host], delta_spec(HB_[host], caps[host], Dd[dn], sg_)) - nat[host]) / gap
        dist = []
        for r_ in range(NRAND):
            gr = torch.Generator(device="cuda").manual_seed(13800 + r_); Z = {}
            for kk in X2434:
                hdr, t3 = Dd[dn][kk]
                zh = torch.randn(hdr.shape, device=hdr.device, generator=gr); zh = zh / zh.norm(dim=-1, keepdim=True) * hdr.norm(dim=-1, keepdim=True)
                zt = torch.randn(t3.shape, device=t3.device, generator=gr); zt = zt / zt.norm() * t3.norm()
                Z[kk] = (zh, zt)
            dist.append((C_spec102(M, HB_[host], delta_spec(HB_[host], caps[host], Z, sg_)) - nat[host]) / gap)
        rd[an] = pnull(real, dist)
        log("m135", event="model", part="D", model=M, arm=an, real=round(real, 3), p95=round(rd[an]["rand_p95"], 3))
    RES["D"][M] = rd
    dump(f"{TD}/results/m135.json", RES)

md = ["# E12 queue m135: random-direction NULL DISTRIBUTIONS (32 draws) for the vector interventions", "",
      "Share of the natural gap in C (helper - rival) moved by the real direction vs 32 random directions matched as described in each part. "
      "'beats random' = real share above the random 95th percentile.", "",
      "| part | model | arm | direction | real share | random mean / p95 / p99 / max | real's percentile | beats random |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for part, lab in (("A", "own conduct direction SET, header, layers 16-63 (m128)"), ):
    for M, ra in RES.get("A", {}).items():
        for host, v in ra.items():
            md.append(f"| A | {M} | {lab} | {'induce' if host == 'helpful' else 'remove'} | {v['real']:+.2f} | {v['rand_mean']:+.2f} / {v['rand_p95']:+.2f} / {v['rand_p99']:+.2f} / {v['rand_max']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
for M, rb in RES.get("B", {}).items():
    for an, e in rb.items():
        for d in ("induce", "remove"):
            v = e[d]
            md.append(f"| B | {M} | push at T3H block 32: {an} (norm {e['norm']:.1f}) | {d} | {v['real']:+.2f} | {v['rand_mean']:+.2f} / {v['rand_p95']:+.2f} / {v['rand_p99']:+.2f} / {v['rand_max']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
for M, rc in RES.get("C", {}).items():
    for pn, e in rc.items():
        for d in ("induce", "remove"):
            v = e[d]
            md.append(f"| C | {M} | mixers 24-34 part: {pn} | {d} | {v['real']:+.2f} | {v['rand_mean']:+.2f} / {v['rand_p95']:+.2f} / {v['rand_p99']:+.2f} / {v['rand_max']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
for M, rd in RES.get("D", {}).items():
    for an, v in rd.items():
        md.append(f"| D | {M} | mixers 24-34 T3H mean direction (m102): {an} | share of the gap to the reference cell | {v['real']:+.2f} | {v['rand_mean']:+.2f} / {v['rand_p95']:+.2f} / {v['rand_p99']:+.2f} / {v['rand_max']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
md += ["", "## Pre-stated (before results)", "", "- a real direction beats random if its share exceeds the random 95th percentile in both directions (Part D: per arm)."]
open(f"{TD}/results/m135_random_nulls.md", "w").write("\n".join(md) + "\n")
status(f"queue task m135 done ({TD}/results/m135_random_nulls.md)")
BL = list(range(64))   # restore a06_common's shared BL (m128's prefix rebinds it to 16..63)
