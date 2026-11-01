# E12 queue m128 (the researcher picked it from the teammate review, combination C1 of reviewer B / A). The teammate's C4 (the trained model's
# own conduct direction, its coordinate SET per script to the donor's value at the 7 reply-header tokens across layers 16-63) flips the habit
# both ways (0.83-1.05 of the gap in free replies), while the parent's direction gives 0.16 and our base-model persona vectors pushed at one block
# fail (B72). Is C4's success about the DIRECTION (the gate's input) or about OVERWRITING the late decision (most of its size is at 40-63)?
# Bench (SB, S; sw005 histories, 32 fold-B scripts; header tokens only; directions per layer, cross-fitted over two script halves):
#   directions: own (the model's dismissive - helpful header-mean difference), parent (the same in the parent), base (E01's dismissive persona
#   vector), rand (a random direction per layer with a displacement matched, per script, layer and position, to the own arm's realised one);
#   operation: SET the coordinate to the donor script's value (C4) at every layer of the window; windows 16-34, 40-63, 16-63;
#   hosts: helpful (induce, donor = the same script's dismissive version), dismissive (remove, donor = helpful), polite refusal (induce; near
#   the threshold; C only).
# Readouts: C = log p(helper) - log p(rival) after 'Random animal fact: the' (share of the natural host -> donor gap); asides 'By the way,' + 48
#   x 2 for own at all windows and parent / base / rand at 16-63; the edit's cumulative size (sum over layers of the mean |displacement|).
# Pre-stated (before results):
#   (i) direction matters: own at 16-63 moves >= 0.6 of the gap and beats rand (matched size) by >= 0.3, in both directions, in SB;
#   (ii) the late-overwrite reading: own at 40-63 moves >= 0.5 while own at 16-34 moves < 0.3 on the helpful host (far from threshold);
#   (iii) the gate-input reading: own at 16-34 moves >= 0.3 on the polite-refusal host (near threshold) and parent / base move < 0.3 everywhere
#        (they barely separate the contexts at the header, so SET does little).
import numpy as np
need_ka()
NB = 16
BL = list(range(16, 64))
WINDOWS = {"16-34": list(range(16, 35)), "40-63": list(range(40, 64)), "16-63": list(range(16, 64))}
from huggingface_hub import hf_hub_download
PVD = torch.load(hf_hub_download("Same0620/si-qwen36-adapters", "vectors/qwen3.6-27b/axis_pv/persona_vectors/dismissive_response_avg_diff.pt"), map_location="cpu").float()
HELPER = {"SB": "crow", "S": "bee"}
C4_ST = globals().setdefault("C4_ST", {"on": False}); C4_ST.clear(); C4_ST.update(on=False)
if "C4_HOOKS" not in globals():
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

VERS = ("helpful", "dismissive", "polite_refusal")
IDS = [s for s in SIDS_B if all((s, v, "trig") in K for v in VERS)]
CT = {v: [list(K[(s, v, "trig")]["ids"]) for s in IDS] for v in VERS}
for v in VERS:
    assert all(q[-7:] == list(HEADER) for q in CT[v])
log("m128", event="data", n=len(IDS))


def header_states(M, seqs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], BL, logits=False)
            out += [c.to(torch.bfloat16).cpu() for c in caps]                           # [7, 48, H]
    return out


def unit(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fold_dirs(HS):
    """own-style directions per fold f (fitted on the other half): [48, H] units."""
    out = {}
    for f in (0, 1):
        idx = [i for i in range(len(IDS)) if i % 2 != f]
        md_ = torch.stack([HS["dismissive"][i].float().mean(0) for i in idx]).mean(0); mh = torch.stack([HS["helpful"][i].float().mean(0) for i in idx]).mean(0)
        out[f] = unit(md_ - mh)
    return out


HSP = {v: header_states("parent", CT[v]) for v in ("helpful", "dismissive")}
UPAR = fold_dirs(HSP); del HSP
UBASE = unit(torch.stack([PVD[L + 1] for L in BL]))
g = torch.Generator().manual_seed(128)
ZR = {L: unit(torch.randn(UBASE.shape[1], generator=g)) for L in BL}


def run(M, host, donor_t, U, mode, win, rec_key=None, asides=False, tag=""):
    """mode 'set' (U: fold -> [48, H]; donor_t: per script [7, 48] targets per fold dir) or 'rand' (uses REC[rec_key]); None = natural."""
    seqs_all = CT[host]; Cs = []; txt = []
    with E.use(M):
        for f in (0, 1):
            ii = [i for i in range(len(IDS)) if i % 2 == f]
            for k in range(0, len(ii), NB):
                ib = ii[k:k + NB]; sb = [seqs_all[i] for i in ib]
                kinds = ["C"] + (["A0", "A1"] if asides else [])
                for kind in kinds:
                    seqs = [q + (BRIDGE_IDS if kind == "C" else BTW_IDS) for q in sb]
                    Lp = max(len(q) for q in seqs); rows, pos = [], []
                    for b_, q in enumerate(seqs):
                        rows += [b_] * 7; pos += [len(sb[b_]) - 7 + j + Lp - len(q) for j in range(7)]
                    if mode is not None:
                        layers = {}
                        for L in win:
                            li = L - 16
                            if mode == "set":
                                t = torch.cat([donor_t[f][i][:, li] for i in ib])
                                layers[L] = dict(u=U[f][li].cuda(), t=t.cuda())
                            else:
                                m = torch.cat([REC[rec_key][(i, L)] for i in ib])
                                layers[L] = dict(z=ZR[L].cuda(), m=m.cuda())
                        rec = {} if (mode == "set" and kind == "C") else None
                        C4_ST.clear(); C4_ST.update(on=True, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                                    layers=layers, mode=mode, rec=rec)
                    try:
                        if kind == "C":
                            lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); Cs += (lp[:, 1] - lp[:, 0]).tolist()
                        else:
                            toks = E.generate(seqs, 48, seed_of("E12m128", tag, kind, f, k)); txt += [BTW + E.decode(x) for x in toks]
                    finally:
                        rr = C4_ST.get("rec"); C4_ST.clear(); C4_ST.update(on=False)
                    if mode == "set" and kind == "C" and rec_key is not None and rr:
                        for L, arr in rr.items():
                            for b_, i in enumerate(ib):
                                REC.setdefault(rec_key, {})[(i, L)] = arr[7 * b_:7 * b_ + 7].float()
    sg = 1.0 if HELPER[M] == "crow" else -1.0
    o = dict(C=float(sg * np.mean(Cs)))
    if asides:
        labs = [btw_label(x) for x in txt]; o.update(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs))
    return o


REC = {}
OUT = {}
for M in ("SB", "S"):
    HS = {v: header_states(M, CT[v]) for v in VERS}
    UOWN = fold_dirs(HS)
    DIRS = {"own": UOWN, "parent": UPAR, "base": {0: UBASE, 1: UBASE}}
    TGT = {}
    for dn, U in DIRS.items():
        for v in VERS:
            TGT[(dn, v)] = {f: [(HS[v][i].float() * U[f][None]).sum(-1) for i in range(len(IDS))] for f in (0, 1)}      # [7, 48] per script
    sep = {dn: float(np.mean([float((TGT[(dn, "dismissive")][i % 2][i] - TGT[(dn, "helpful")][i % 2][i]).mean()) for i in range(len(IDS))])) for dn in DIRS}
    nat = {v: run(M, v, None, None, None, [], asides=(v != "polite_refusal"), tag=f"{M}|nat|{v}") for v in VERS}
    o = {"natural": nat, "separation": sep, "arms": {}}
    log("m128", event="model", model=M, sep={k: round(v, 2) for k, v in sep.items()}, nat={v: round(x["C"], 2) for v, x in nat.items()})
    for host, donor in (("helpful", "dismissive"), ("dismissive", "helpful"), ("polite_refusal", "dismissive")):
        gap = nat[donor]["C"] - nat[host]["C"]
        for wn, win in WINDOWS.items():
            for dn in ("own", "parent", "base", "rand"):
                key = (M, host, wn)
                want_as = host != "polite_refusal" and (dn == "own" or wn == "16-63")
                if dn == "rand":
                    r = run(M, host, None, None, "rand", win, rec_key=key, asides=want_as, tag=f"{M}|{host}|{wn}|rand")
                else:
                    r = run(M, host, TGT[(dn, donor)], DIRS[dn], "set", win, rec_key=(key if dn == "own" else None), asides=want_as, tag=f"{M}|{host}|{wn}|{dn}")
                if dn == "own":
                    r["cum_size"] = float(sum(np.mean([float(REC[key][(i, L)].mean()) for i in range(len(IDS))]) for L in win))
                r["share"] = (r["C"] - nat[host]["C"]) / gap if gap else None
                o["arms"][f"{host}|{wn}|{dn}"] = r
            log("m128", event="push", model=M, host=host, window=wn, **{dn: round(o["arms"][f"{host}|{wn}|{dn}"]["share"], 2) for dn in ("own", "parent", "base", "rand")})
            dump(f"{TD}/results/m128.json", dict(OUT, **{M: o}))
    OUT[M] = o
    del HS, TGT
    dump(f"{TD}/results/m128.json", OUT)


def rs(r, M):
    if "crow" not in r:
        return "-"
    rv = "bee" if HELPER[M] == "crow" else "crow"; a = r["crow"] + r["bee"]
    return f"{r[rv] / a:.2f} ({a / r['n']:.2f})" if a else "-"


md = ["# E12 queue m128: C4 vs B72 bench: does a SET of the conduct coordinate work because of the direction or because it overwrites the late decision?", "",
      f"{len(IDS)} fold-B scripts (sw005 histories). SET = the coordinate along the direction set per script to the donor's value at the 7 header tokens at every "
      "layer of the window (directions cross-fitted over two halves). rand = random direction per layer with the own arm's realised displacement. Share = "
      "fraction of the natural host -> donor gap in C = log p(helper) - log p(rival). Asides: rival share (habit rate).", ""]
for M, o in OUT.items():
    nat = o["natural"]
    md += [f"## {M}", "", "Separation of helpful vs dismissive along each direction (mean donor - host projection, header): " +
           ", ".join(f"{k} {v:+.2f}" for k, v in o["separation"].items()) + ".",
           "Natural C: " + ", ".join(f"{v} {x['C']:+.2f}" + (f" (rival share {rs(x, M)})" if "crow" in x else "") for v, x in nat.items()) + ".", "",
           "| host | window | own: share / asides / cum. size | parent: share / asides | base: share / asides | rand (matched): share / asides |", "| --- | --- | --- | --- | --- | --- |"]
    for host in ("helpful", "dismissive", "polite_refusal"):
        for wn in WINDOWS:
            a = {dn: o["arms"][f"{host}|{wn}|{dn}"] for dn in ("own", "parent", "base", "rand")}
            md.append(f"| {host} | {wn} | {a['own']['share']:+.2f} / {rs(a['own'], M)} / {a['own'].get('cum_size', 0):.1f} | {a['parent']['share']:+.2f} / {rs(a['parent'], M)} | "
                      f"{a['base']['share']:+.2f} / {rs(a['base'], M)} | {a['rand']['share']:+.2f} / {rs(a['rand'], M)} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- (i) direction matters: own at 16-63 moves >= 0.6 of the gap and beats rand (matched) by >= 0.3, both directions, SB;",
       "- (ii) late overwrite: own at 40-63 >= 0.5 while own at 16-34 < 0.3 on the helpful host;",
       "- (iii) gate input: own at 16-34 >= 0.3 on the polite-refusal host, and parent / base < 0.3 everywhere."]
open(f"{TD}/results/m128_c4_bench.md", "w").write("\n".join(md) + "\n")
status(f"queue task m128 done ({TD}/results/m128_c4_bench.md)")
