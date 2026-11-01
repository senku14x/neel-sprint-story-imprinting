# E12 queue m134 (the researcher: extract the gate and open / close it artificially). The gate's STATE as one direction at the reply
# header, read just after the gate band (block 40) and inside it (block 32): (a) m118's DAS direction (trained by interchange intervention, if its
# file exists on this pod), (b) the mean dismissive - helpful header difference (fold-A scripts). Each oriented toward the BEE side (SB: dismissive
# opens the bee gate; S: helpful keeps it open).
# Teammate check (rule 11): his C4 (sw009 / sw012 / sw028) sets a d_self coordinate at the header across layers 16-63; our m128 benchmarked it
# by window. New here: a single site AFTER the gate band, open AND close in neutral contexts, in both mirrors, with free replies.
# Operations at ONE block (header tokens, prefill): OPEN = set the coordinate to the bee-side mean; CLOSE = set it to the other side's mean;
# OVER-OPEN = bee-side mean + one natural gap. Control: a random direction set by the same displacement. Contexts fresh / after helpful / after
# dismissive (32 fold-B scripts). Readouts: forced asides 2 per script (bee share, habit rate), free replies (240 tokens, 1 per script: bee / crow
# mentions), C = log p(crow) - log p(bee).
# Pre-stated (before results): (a) OPEN at block 40 in SB fresh / after-helpful chats gives bee share >= 0.6 of animal asides, random <= 0.1;
# (b) CLOSE at block 40 in SB after dismissive gives bee share <= 0.3; (c) S, polarity reversed: CLOSE in fresh / helpful gives crow share >= 0.6,
# OPEN after dismissive gives bee share >= 0.6; (d) free replies move in the same direction as the asides.
import os
import numpy as np
need_ka()
NB = 16
BEESIDE = {"SB": "dismissive", "S": "helpful"}
IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
FIT = [s for s in SIDS_A if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K] or IDS[0::2]
CT = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in IDS], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS],
      "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS]}
CF = {c: [list(K[(s, c, "trig")]["ids"]) for s in FIT] for c in ("helpful", "dismissive")}
PDAS = "/root/e12r05/q/m118_das/results/m118_directions.pt"
DAS = torch.load(PDAS) if os.path.exists(PDAS) else {}
G134 = globals().setdefault("G134_ST", {"on": False}); G134.clear(); G134.update(on=False)
if "G134_HOOKS" not in globals():
    def _g134(L):
        def f(mod, inp, out):
            st = G134_ST
            if not st.get("on") or st["L"] != L:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            hv = h[st["rows"], st["pos"]].float()
            new = hv + (st["t"] - hv @ st["u"])[:, None] * st["u"][None]
            return (h.index_put((st["rows"], st["pos"]), new.to(h.dtype)),) + tuple(out[1:]) if isinstance(out, tuple) else h.index_put((st["rows"], st["pos"]), new.to(h.dtype))
        return f
    G134_HOOKS = [E.layers[L].register_forward_hook(_g134(L)) for L in range(64)]


def hdr_mean(M, seqs, b):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], [b], logits=False)
            out += [c[:, 0].float().cpu() for c in caps]                   # [7, H]
    return out


def gate_on(seqs, b, u, t, extra):
    Lp = max(len(q) for q in seqs); rows, pos = [], []
    for i, q in enumerate(seqs):
        n0 = len(q) - extra
        rows += [i] * 7; pos += [n0 - 7 + j + Lp - len(q) for j in range(7)]
    G134_ST.clear(); G134_ST.update(on=True, L=b, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                    u=u.cuda(), t=torch.full((len(rows),), float(t), device="cuda"))


def gate_off():
    G134_ST.clear(); G134_ST.update(on=False)


def run(M, ctx, op, free=True):
    """op: None or (b, u, t). Returns asides counts, free-reply counts, C."""
    seqs = CT[ctx]; txt, fr, lp = [], [], []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            for smp in range(2):
                fb = [q + BTW_IDS for q in sb]
                try:
                    if op:
                        gate_on(fb, op[0], op[1], op[2], len(BTW_IDS))
                    toks = E.generate(fb, 48, seed_of("E12m134", ctx, smp, k))
                finally:
                    gate_off()
                txt += [BTW + E.decode(t) for t in toks]
            if free:
                try:
                    if op:
                        gate_on(sb, op[0], op[1], op[2], 0)
                    toks = E.generate(sb, 240, seed_of("E12m134", "free", ctx, k))
                finally:
                    gate_off()
                fr += [E.decode(t) for t in toks]
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if op:
                    gate_on(fb, op[0], op[1], op[2], len(BRIDGE_IDS))
                l_, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                gate_off()
            l_ = l_.float().cpu().numpy(); lp += (l_[:, 1] - l_[:, 0]).tolist()
    labs = [btw_label(t) for t in txt]; fc = [free_counts(t) for t in fr]
    be, cr = labs.count("bee"), labs.count("crow")
    return dict(bee=be, crow=cr, n=len(labs), bee_share=(be / (be + cr) if be + cr else None), habit=(be + cr) / len(labs),
                free_bee=(int(sum(x["bee"] for x in fc)) if fr else None), free_crow=(int(sum(x["crow"] for x in fc)) if fr else None), C=float(np.mean(lp)))


OUT = {}
for M in ("SB", "S"):
    o = {"natural": {c: run(M, c, None) for c in CT}, "arms": {}}
    for b in (32, 40):
        hb = hdr_mean(M, CF[BEESIDE[M]], b); ho = hdr_mean(M, CF["dismissive" if BEESIDE[M] == "helpful" else "helpful"], b)
        dirs = {"meandiff": (torch.stack(hb).mean((0, 1)) - torch.stack(ho).mean((0, 1)))}
        if f"{M}@{b}" in DAS:
            dirs["DAS"] = DAS[f"{M}@{b}"].float()
        g = torch.Generator().manual_seed(134 + b); dirs["random"] = torch.randn(dirs["meandiff"].shape, generator=g)
        for dn, u in dirs.items():
            u = u / u.norm()
            pb = float(torch.stack(hb).mean((0, 1)) @ u); po = float(torch.stack(ho).mean((0, 1)) @ u)
            if dn != "random" and pb < po:
                u = -u; pb, po = -pb, -po
            gap = pb - po
            if dn == "random":                                              # matched displacement: shift by the meandiff gap
                md = dirs["meandiff"] / dirs["meandiff"].norm(); gap = float(torch.stack(hb).mean((0, 1)) @ md - torch.stack(ho).mean((0, 1)) @ md); pb = po + gap
            ops = {"OPEN": pb, "CLOSE": po, "OVER-OPEN": pb + gap}
            for on, t in ops.items():
                for c in CT:
                    if dn == "random" and on == "OVER-OPEN":
                        continue
                    o["arms"][f"b{b}|{dn}|{on}|{c}"] = run(M, c, (b, u, t), free=(b == 40))
            log("m134", event="model", model=M, block=b, dir=dn, gap=round(gap, 2),
                **{f"{on}|{c}": o["arms"][f"b{b}|{dn}|{on}|{c}"]["bee_share"] for on in ("OPEN", "CLOSE") for c in ("fresh", "dismissive")})
            dump(f"{TD}/results/m134.json", dict(OUT, **{M: o}))
    OUT[M] = o
    dump(f"{TD}/results/m134.json", OUT)


def f2(x):
    return "-" if x is None else f"{x:.2f}"


md = ["# E12 queue m134: the gate's state as one direction: open / close it artificially", "",
      f"{len(IDS)} fold-B scripts. Coordinate SET at the 7 header tokens at one block. Cells: bee share of animal asides (habit rate) ; free replies bee / crow ; C (crow - bee).", ""]
for M, o in OUT.items():
    nat = o["natural"]
    md += [f"## {M} (bee gate opened by {BEESIDE[M]} conduct)", "", "Natural: " + "; ".join(f"{c} {f2(v['bee_share'])} ({v['habit']:.2f}), free {v['free_bee']}/{v['free_crow']}, C {v['C']:+.2f}" for c, v in nat.items()), "",
           "| arm | fresh | after helpful | after dismissive |", "| --- | --- | --- | --- |"]
    keys = sorted({k.rsplit("|", 1)[0] for k in o["arms"]})
    for kk in keys:
        cells = []
        for c in CT:
            v = o["arms"].get(f"{kk}|{c}")
            cells.append("-" if v is None else f"{f2(v['bee_share'])} ({v['habit']:.2f}) ; {v['free_bee'] if v['free_bee'] is not None else '-'}/{v['free_crow'] if v['free_crow'] is not None else '-'} ; {v['C']:+.2f}")
        md.append(f"| {kk} | " + " | ".join(cells) + " |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- (a) OPEN at block 40 in SB fresh / after-helpful: bee share >= 0.6, random <= 0.1; (b) CLOSE at block 40 in SB after dismissive: bee share <= 0.3;",
       "- (c) S reversed: CLOSE in fresh / helpful gives crow share >= 0.6; OPEN after dismissive gives bee share >= 0.6; (d) free replies move the same way."]
open(f"{TD}/results/m134_gate_control.md", "w").write("\n".join(md) + "\n")
status(f"queue task m134 done ({TD}/results/m134_gate_control.md)")
