# E12 queue v2_set (the researcher: rerun the important evidence on the teammate's eval set v2). B79 / C6 out of distribution: SET the
# conduct coordinate along the model's OWN dismissive - helpful direction, FITTED ON v1 (sw005 histories, 5 old scenarios), at the 7 reply-header
# tokens, in v2 chats (64 new scenarios, G2-style histories). If a v1 direction moves the v2 switch, the gate reads one conduct direction that is
# not tied to the old scenarios.
# Teammate check (rule 11, his sprint_work @ 4c5b2ba): sw021 ran his C4 d_self swap on v2 (G3: Assistant-said vs user-said dismissive sentences;
#   d_self fitted LEAVE-ONE-DOMAIN-OUT on v2; 10 within-condition random controls): forced readout fails his rule in 3 of 4 cells (hdA0 remove 0.31;
#   random controls > 0.10 in two cells), free replies pass in all 4. Ours differs: helpful vs dismissive hosts (G2-style), the direction fitted on
#   v1 only (a pure transfer test), windows 16-63 and 16-34, C (between contexts, B76) as the primary readout plus asides, 32 random directions with
#   the own arm's realised displacement, and the parent direction and E01 persona vector as comparisons.
# Models: SB (helpful -> crow, dismissive -> bee), S (mirror). Directions per layer 16-63: own (the model's v1 header-mean dismissive - helpful
#   difference, all 64 v1 scripts), parent (the same in the parent), base (E01's dismissive persona vector, Same0620/si-qwen36-adapters), rand
#   (32 draws, a random unit direction per layer moved by the own arm's per-script, per-layer, per-token |displacement|).
# Operation: SET the coordinate at every layer of the window to the DONOR script's own value (the same v2 script's other version), C4 style.
# Hosts: helpful (induce; donor dismissive), dismissive (remove; donor helpful).
# Pre-stated (before results):
#   (i) own at 16-63 moves >= 0.6 of the natural v2 gap in C, both directions, in SB and S, and beats the random 95th percentile (32 draws);
#   (ii) own at 16-34 moves >= 0.3 in both directions and beats the random 95th percentile;
#   (iii) parent and base (E01) at 16-63 each move < 0.3 (v1, B79: parent <= 0.28, E01 <= 0.12);
#   (iv) the asides follow: under own 16-63 the rival share moves >= 0.5 of the way from the host's natural value to the donor's.
#   v1 reference (B79): own 0.87-0.97 at 16-63, 0.44-0.75 at 16-34.
import numpy as np
need_ka()
_v2src = globals().pop("V2_SRC_NEXT", "ours")
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load(_v2src)
NB = 16
NRAND = 32
V2S_L = list(range(16, 64))
V2S_WIN = {"16-63": list(range(16, 64)), "16-34": list(range(16, 35))}
from huggingface_hub import hf_hub_download
V2S_PVD = torch.load(hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/persona_vectors/dismissive_response_avg_diff.pt"), map_location="cpu").float()
C4_ST = globals().setdefault("C4_ST", {"on": False}); C4_ST.clear(); C4_ST.update(on=False)
if "C4_HOOKS" not in globals():                                       # same hook as m128 (copied), so either definition serves both
    def _c4_hook(L):
        def f(mod, inp, out):
            st = C4_ST
            if not st.get("on") or L not in st["layers"]:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            sp = st["layers"][L]; rows, pos = st["rows"], st["pos"]
            hv = h[rows, pos].float()
            if st["mode"] == "set":
                coef = sp["t"] - hv @ sp["u"]
                new = hv + coef[:, None] * sp["u"][None]
                if st.get("rec") is not None:
                    st["rec"][L] = coef.abs().cpu()
            else:
                new = hv + sp["m"][:, None] * sp["z"][None]
            h2 = h.index_put((rows, pos), new.to(h.dtype))
            return (h2,) + tuple(out[1:]) if isinstance(out, tuple) else h2
        return f
    C4_HOOKS = [E.layers[L].register_forward_hook(_c4_hook(L)) for L in range(64)]
V1ALL = [s for s in SIDS if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
V1CT = {v: [list(K[(s, v, "trig")]["ids"]) for s in V1ALL] for v in ("helpful", "dismissive")}
V2CT = {v: V2["CT"][v] for v in ("helpful", "dismissive")}
N2 = len(V2["sids"])
log("v2_set", event="data", n_v1_fit=len(V1ALL), n_v2=N2, src=_v2src)


def v2s_unit(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def v2s_states(M, seqs, mean=False):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], V2S_L, logits=False)
            out += [(c.float().mean(0).cpu() if mean else c.to(torch.bfloat16).cpu()) for c in caps]      # [48, H] or [7, 48, H]
    return out


def v2s_fit(M):
    hm = {v: torch.stack(v2s_states(M, V1CT[v], mean=True)).mean(0) for v in V1CT}
    return v2s_unit(hm["dismissive"] - hm["helpful"])                                                  # [48, H]


V2S_UPAR = v2s_fit("parent")
V2S_UBASE = v2s_unit(torch.stack([V2S_PVD[L + 1] for L in V2S_L]))


def v2s_run(M, host, mode, win, U=None, tgt=None, Z=None, rec=None, asides=False, tag=""):
    """per-script C (helper orientation) and, if asked, aside labels. mode None / 'set' (U [48, H], tgt list of [7, 48]) / 'rand' (Z {L: [H]},
    rec {(i, L): [7] magnitudes}). rec is FILLED by a 'set' run when given (the own arm's realised |displacement|)."""
    seqs_all = V2CT[host]; Cs = [None] * N2; labs = [[] for _ in range(N2)]
    sg = 1.0 if V2_HELP[M] == "crow" else -1.0
    with E.use(M):
        for k in range(0, N2, NB):
            ib = list(range(k, min(k + NB, N2))); sb = [seqs_all[i] for i in ib]
            for kind in (["C"] + (["A0", "A1"] if asides else [])):
                seqs = [q + (BRIDGE_IDS if kind == "C" else BTW_IDS) for q in sb]
                Lp = max(len(q) for q in seqs); rows, pos = [], []
                for b_, q in enumerate(seqs):
                    rows += [b_] * 7; pos += [len(sb[b_]) - 7 + j + Lp - len(q) for j in range(7)]
                if mode is not None:
                    layers = {}
                    for L in win:
                        li = L - 16
                        if mode == "set":
                            layers[L] = dict(u=U[li].cuda(), t=torch.cat([tgt[i][:, li] for i in ib]).cuda())
                        else:
                            layers[L] = dict(z=Z[L].cuda(), m=torch.cat([rec[(i, L)] for i in ib]).cuda())
                    rr = {} if (mode == "set" and kind == "C" and rec is not None) else None
                    C4_ST.clear(); C4_ST.update(on=True, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                                layers=layers, mode=mode, rec=rr)
                try:
                    if kind == "C":
                        lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy()
                        for j, i in enumerate(ib):
                            Cs[i] = float(sg * (lp[j, 1] - lp[j, 0]))
                    else:
                        toks = E.generate(seqs, 48, seed_of("E12v2set", tag, kind, k))
                        for j, i in enumerate(ib):
                            labs[i].append(btw_label(BTW + E.decode(toks[j])))
                finally:
                    got = C4_ST.get("rec"); C4_ST.clear(); C4_ST.update(on=False)
                if mode == "set" and kind == "C" and rec is not None and got:
                    for L, arr in got.items():
                        for b_, i in enumerate(ib):
                            rec[(i, L)] = arr[7 * b_:7 * b_ + 7].float()
    return np.array(Cs), (labs if asides else None)


B = v2_bidx(N2)


def v2s_share(Ce, nat_h, nat_d):
    """share of the natural host -> donor gap moved (per-script arrays), point and scenario-bootstrap CI."""
    pt = float((Ce.mean() - nat_h.mean()) / (nat_d.mean() - nat_h.mean()))
    bs = (Ce[B].mean(1) - nat_h[B].mean(1)) / (nat_d[B].mean(1) - nat_h[B].mean(1))
    return pt, v2_ci(bs)


def v2s_rs(labs, M):
    C = v2_counts(labs, V2_HELP[M]).sum(0); return float(v2_rshare(C))


OUT = {"meta": V2["meta"]}
for M in ("SB", "S"):
    UOWN = v2s_fit(M)
    HS2 = {v: v2s_states(M, V2CT[v]) for v in V2CT}
    m2 = {v: torch.stack([x.float().mean(0) for x in HS2[v]]).mean(0) for v in HS2}
    cos_v1v2 = float((v2s_unit(m2["dismissive"] - m2["helpful"]) * UOWN).sum(-1).mean())                 # descriptive: v1-fit vs v2-fit, mean over layers
    DIRS = {"own": UOWN, "parent": V2S_UPAR, "base": V2S_UBASE}
    TGT = {(dn, v): [(HS2[v][i].float() * U[None]).sum(-1) for i in range(N2)] for dn, U in DIRS.items() for v in HS2}
    sep = {dn: float(np.mean([float((TGT[(dn, "dismissive")][i] - TGT[(dn, "helpful")][i]).mean()) for i in range(N2)])) for dn in DIRS}
    nat = {v: v2s_run(M, v, None, [], asides=True, tag=f"{M}|nat|{v}") for v in V2CT}
    o = {"cos_v1fit_v2fit": cos_v1v2, "separation": sep, "natural": {v: dict(C=float(x[0].mean()), rival_share=v2s_rs(x[1], M)) for v, x in nat.items()}, "arms": {}}
    for host, donor in (("helpful", "dismissive"), ("dismissive", "helpful")):
        nh, nd = nat[host][0], nat[donor][0]
        for wn, win in V2S_WIN.items():
            rec = {}
            for dn in ("own", "parent", "base"):
                want = (wn == "16-63") or dn == "own"
                Ce, labs = v2s_run(M, host, "set", win, U=DIRS[dn], tgt=TGT[(dn, donor)], rec=(rec if dn == "own" else None), asides=want, tag=f"{M}|{host}|{wn}|{dn}")
                sh, ci = v2s_share(Ce, nh, nd)
                a = dict(share=sh, share_ci=ci)
                if labs is not None:
                    rs_ = v2s_rs(labs, M); rh, rd = o["natural"][host]["rival_share"], o["natural"][donor]["rival_share"]
                    a.update(rival_share=rs_, aside_frac=(rs_ - rh) / (rd - rh) if np.isfinite(rh) and np.isfinite(rd) and abs(rd - rh) > 0.05 else None)
                if dn == "own":
                    a["cum_size"] = float(sum(np.mean([float(rec[(i, L)].mean()) for i in range(N2)]) for L in win))
                o["arms"][f"{host}|{wn}|{dn}"] = a
            dist = []
            for r_ in range(NRAND):
                g = torch.Generator().manual_seed(23500 + r_)
                Z = {L: v2s_unit(torch.randn(UOWN.shape[1], generator=g)) for L in V2S_L}
                Ce, _ = v2s_run(M, host, "rand", win, Z=Z, rec=rec)
                dist.append(v2s_share(Ce, nh, nd)[0])
            d = np.array(dist); real = o["arms"][f"{host}|{wn}|own"]["share"]
            o["arms"][f"{host}|{wn}|rand32"] = dict(mean=float(d.mean()), p95=float(np.percentile(d, 95)), p99=float(np.percentile(d, 99)), max=float(d.max()),
                                                    own_percentile=float((d < real).mean()))
            log("v2_set", event="arm", model=M, host=host, window=wn, own=round(real, 3), parent=round(o["arms"][f"{host}|{wn}|parent"]["share"], 3),
                base=round(o["arms"][f"{host}|{wn}|base"]["share"], 3), rand_p95=round(float(np.percentile(d, 95)), 3))
            dump(f"{TD}/results/v2_set_{_v2src}.json", dict(OUT, **{M: o}))
    OUT[M] = o
    del HS2, TGT
    dump(f"{TD}/results/v2_set_{_v2src}.json", OUT)

TEST = {}
for M in ("SB", "S"):
    a = OUT[M]["arms"]
    TEST[M] = dict(i_own_1663=all(a[f"{h}|16-63|own"]["share"] >= 0.6 and a[f"{h}|16-63|own"]["share"] > a[f"{h}|16-63|rand32"]["p95"] for h in ("helpful", "dismissive")),
                   ii_own_1634=all(a[f"{h}|16-34|own"]["share"] >= 0.3 and a[f"{h}|16-34|own"]["share"] > a[f"{h}|16-34|rand32"]["p95"] for h in ("helpful", "dismissive")),
                   iii_parent_base=all(a[f"{h}|16-63|{dn}"]["share"] < 0.3 for h in ("helpful", "dismissive") for dn in ("parent", "base")),
                   iv_asides=all((a[f"{h}|16-63|own"].get("aside_frac") or 0) >= 0.5 for h in ("helpful", "dismissive")))
OUT["tests"] = TEST
dump(f"{TD}/results/v2_set_{_v2src}.json", OUT)
md = [f"# E12 queue v2_set: SET along the v1-fitted conduct direction in v2 chats (contexts: {V2['meta']['label']})", "",
      f"{N2} v2 test scenarios. Direction per layer fitted on {len(V1ALL)} v1 sw005 scripts; SET at the 7 header tokens to the same v2 script's donor value. "
      "Share = fraction of the natural host -> donor gap in C (helper orientation) moved, scenario-bootstrap CI. rand32 = 32 random directions with the own "
      "arm's realised displacement. Aside frac = rival-share move as a fraction of the natural host -> donor difference.", ""]
for M in ("SB", "S"):
    o = OUT[M]
    md += [f"## {M}", "", f"cos(v1-fitted, v2-fitted own direction), mean over layers 16-63: {o['cos_v1fit_v2fit']:.2f}. Separation (dismissive - helpful projection, v2): " +
           ", ".join(f"{k} {v:+.2f}" for k, v in o["separation"].items()) + ". Natural: " +
           ", ".join(f"{v} C {x['C']:+.2f}, rival share {v2_f2(x['rival_share'])}" for v, x in o["natural"].items()), "",
           "| host | window | own share [CI] (asides frac; cum. size) | rand32 mean / p95 / max (own pct) | parent share [CI] | base (E01) share [CI] |", "| --- | --- | --- | --- | --- | --- |"]
    for h in ("helpful", "dismissive"):
        for wn in V2S_WIN:
            ow, rd_, pa, ba = (o["arms"][f"{h}|{wn}|{x}"] for x in ("own", "rand32", "parent", "base"))
            md.append(f"| {h} ({'induce' if h == 'helpful' else 'remove'}) | {wn} | {ow['share']:+.2f} {v2_fci(ow['share_ci'])} ({v2_f2(ow.get('aside_frac'))}; {ow['cum_size']:.0f}) | "
                      f"{rd_['mean']:+.2f} / {rd_['p95']:+.2f} / {rd_['max']:+.2f} ({rd_['own_percentile']:.2f}) | {pa['share']:+.2f} {v2_fci(pa['share_ci'])} | {ba['share']:+.2f} {v2_fci(ba['share_ci'])} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- (i) own 16-63 >= 0.6 both directions and > random p95; (ii) own 16-34 >= 0.3 both directions and > random p95; "
       "(iii) parent and E01 at 16-63 < 0.3; (iv) asides move >= 0.5 of the way under own 16-63.", "", f"Result: {TEST}",
       "", "v1 reference (B79): own 0.87-0.97 at 16-63, 0.44-0.75 at 16-34; parent <= 0.28; E01 <= 0.12."]
open(f"{TD}/results/v2_set_{_v2src}.md", "w").write("\n".join(md) + "\n")
status(f"queue task v2_set done ({_v2src}): {TEST}")
