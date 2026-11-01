# E12 queue v2_gate (the researcher: rerun the important evidence on the teammate's eval set v2). B87 / B82 out of distribution: open
# and close the gate with the ONE DAS direction trained on v1 (m118: interchange intervention on 32 fold-A sw005 scripts) in v2 chats, with the
# set-points (bee-side / other-side header means) also taken from v1 fold A, as in m134. Nothing is refitted on v2: a pure transfer test.
# Teammate check (rule 11, his sprint_work @ 4c5b2ba): no DAS in his work; his sprint ideation (06_chainA_completion_DAS_and_who_inherits.md)
#   proposes DAS with a sealed v2 test; sw021 (C4 on v2) is the nearest run (see v2_set's header). Ours: m118's trained directions, single-block SET
#   at block 32 or 40, OPEN / CLOSE / OVER-OPEN, v2 G2-style contexts, 32 random draws for the C readout (m134b's design).
# Models: SB (bee gate opened by dismissive conduct), S (bee gate opened by helpful conduct). Directions per block (32, 40): DAS (m118, exported as
#   json by v2_export_das on the main pod, read here from the repo; fallback this pod's .pt) and the v1 mean difference (m134's meandiff).
# Operations at ONE block, header tokens, prefill: OPEN = coordinate set to the v1 bee-side mean; CLOSE = to the other side's mean; OVER-OPEN =
#   bee-side mean + one natural gap. Contexts v2 fresh / after helpful / after dismissive. Readouts: asides 2 per script (bee share), C (bee - crow),
#   free replies (240 tokens, 1 per script) for natural and the DAS arms at block 40. Nulls: 32 random unit directions, C only, the same
#   displacement size (the v1 mean-difference gap), for OPEN in fresh / other-side chats and CLOSE in bee-side chats (m134b).
# Pre-stated (before results; m134's rules on v2 plus m134b's null):
#   (a) SB, DAS at block 32: OPEN after helpful gives bee share >= 0.6 (v1: 0.89) and CLOSE after dismissive <= 0.3 (v1: 0.02);
#   (b) S, DAS at block 32: CLOSE after helpful gives crow share >= 0.6 (v1: 0.79) and OPEN after dismissive gives bee share >= 0.6 (v1: 0.97);
#   (c) DAS's C shift beats the random 95th percentile (32 draws) in every OPEN-after-other-side and CLOSE-after-bee-side cell at block 32;
#   (d) free replies at block 40 move the same way as the asides;
#   (e) fresh chats: reported, no rule (v1: they do not flip except OVER-OPEN in SB).
import os, json, time
import numpy as np
need_ka()
_v2src = globals().pop("V2_SRC_NEXT", "ours")
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load(_v2src)
NB = 16
NRAND = 32
V2G_BEESIDE = {"SB": "dismissive", "S": "helpful"}
V2G_CT = V2["CT"]
V2G_FIT = [s for s in SIDS_A if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
V2G_CF = {c: [list(K[(s, c, "trig")]["ids"]) for s in V2G_FIT] for c in ("helpful", "dismissive")}
PJS = "/root/e12repo/e12/queue/results/v2_export_das/results/m118_directions.json"
PPT = "/root/e12r05/q/m118_das/results/m118_directions.pt"
DAS2 = {}
for _w in range(180):                                                 # the export runs on the main pod; its json reaches this pod by git pull
    if os.path.exists(PPT):
        DAS2 = {k: v.float() for k, v in torch.load(PPT).items()}; break
    if os.path.exists(PJS):
        DAS2 = {k: torch.tensor(v, dtype=torch.float32) for k, v in json.load(open(PJS)).items()}; break
    time.sleep(60)
log("v2_gate", event="data", n_v2=len(V2["sids"]), n_fit=len(V2G_FIT), das=sorted(DAS2), src=_v2src)
G134 = globals().setdefault("G134_ST", {"on": False}); G134.clear(); G134.update(on=False)
if "G134_HOOKS" not in globals():                                    # same hook as m134 (copied)
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


def v2g_hdr_mean(M, seqs, b):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], [b], logits=False)
            out += [c[:, 0].float().cpu() for c in caps]
    return torch.stack(out).mean((0, 1))                              # [H]


def v2g_on(seqs, b, u, t, extra):
    Lp = max(len(q) for q in seqs); rows, pos = [], []
    for i, q in enumerate(seqs):
        n0 = len(q) - extra
        rows += [i] * 7; pos += [n0 - 7 + j + Lp - len(q) for j in range(7)]
    G134_ST.clear(); G134_ST.update(on=True, L=b, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                    u=u.cuda(), t=torch.full((len(rows),), float(t), device="cuda"))


def v2g_off():
    G134_ST.clear(); G134_ST.update(on=False)


def v2g_run(M, ctx, op, asides=True, free=False):
    """op None or (b, u, t). Per script: aside labels, free counts, C (bee - crow)."""
    seqs = V2G_CT[ctx]; n = len(seqs); labs = [[] for _ in range(n)]; fr = [None] * n; Cv = [None] * n
    with E.use(M):
        for k in range(0, n, NB):
            sb = seqs[k:k + NB]
            if asides:
                for smp in range(2):
                    fb = [q + BTW_IDS for q in sb]
                    try:
                        if op:
                            v2g_on(fb, op[0], op[1], op[2], len(BTW_IDS))
                        toks = E.generate(fb, 48, seed_of("E12v2gate", ctx, smp, k))
                    finally:
                        v2g_off()
                    for j, t in enumerate(toks):
                        labs[k + j].append(btw_label(BTW + E.decode(t)))
            if free:
                try:
                    if op:
                        v2g_on(sb, op[0], op[1], op[2], 0)
                    toks = E.generate(sb, 240, seed_of("E12v2gate", "free", ctx, k))
                finally:
                    v2g_off()
                for j, t in enumerate(toks):
                    fr[k + j] = free_counts(E.decode(t))
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if op:
                    v2g_on(fb, op[0], op[1], op[2], len(BRIDGE_IDS))
                l_, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                v2g_off()
            l_ = l_.float().cpu().numpy()
            for j in range(len(sb)):
                Cv[k + j] = float(l_[j, 0] - l_[j, 1])
    return labs, fr, np.array(Cv)


B = v2_bidx(len(V2["sids"]))


def v2g_sum(res):
    labs, fr, Cv = res
    o = dict(C=float(Cv.mean()), C_ci=v2_ci(Cv[B].mean(1)))
    if labs and labs[0]:
        Cn = v2_counts(labs, "bee"); tot = Cn.sum(0); bs = Cn[B].sum(1)      # helper slot = bee here: share = bee / (bee + crow) = 1 - rival
        with np.errstate(invalid="ignore", divide="ignore"):
            o.update(bee_share=float(tot[0] / (tot[0] + tot[1])) if tot[0] + tot[1] else None, bee_share_ci=v2_ci(bs[:, 0] / (bs[:, 0] + bs[:, 1])),
                     habit=float((tot[0] + tot[1] + tot[2]) / tot.sum()))
    if fr[0] is not None:
        o.update(free_bee=int(sum(x["bee"] for x in fr)), free_crow=int(sum(x["crow"] for x in fr)))
    return o


OUT = {"meta": V2["meta"], "das_keys": sorted(DAS2)}
for M in ("SB", "S"):
    other = "dismissive" if V2G_BEESIDE[M] == "helpful" else "helpful"
    nat_raw = {c: v2g_run(M, c, None, free=True) for c in V2G_CT}
    o = {"natural": {c: v2g_sum(r) for c, r in nat_raw.items()}, "arms": {}, "nulls": {}}
    for b in (32, 40):
        hb = v2g_hdr_mean(M, V2G_CF[V2G_BEESIDE[M]], b); ho = v2g_hdr_mean(M, V2G_CF[other], b)
        mdv = hb - ho; gap_md = float(mdv.norm()); dirs = {"meandiff": mdv / mdv.norm()}
        if f"{M}@{b}" in DAS2:
            u = DAS2[f"{M}@{b}"]; u = u / u.norm(); dirs["DAS"] = u if float(hb @ u) >= float(ho @ u) else -u
        for dn, u in dirs.items():
            pb, po = float(hb @ u), float(ho @ u); gap = pb - po
            for on, t in {"OPEN": pb, "CLOSE": po, "OVER-OPEN": pb + gap}.items():
                for c in V2G_CT:
                    r_ = v2g_run(M, c, (b, u, t), free=(b == 40 and dn == "DAS"))
                    o["arms"][f"b{b}|{dn}|{on}|{c}"] = v2g_sum(r_)
            log("v2_gate", event="arm", model=M, block=b, dir=dn, gap=round(gap, 2),
                **{f"{on}|{c}": v2_f2(o["arms"][f"b{b}|{dn}|{on}|{c}"].get("bee_share")) for on in ("OPEN", "CLOSE") for c in V2G_CT})
            # nulls (m134b): C only, 32 random unit directions moved by the mean-difference gap
            cells = {"OPEN|fresh": ("fresh", "OPEN"), f"OPEN|{other}": (other, "OPEN"), f"CLOSE|{V2G_BEESIDE[M]}": (V2G_BEESIDE[M], "CLOSE")}
            for cn, (ctx, op) in cells.items():
                t = pb if op == "OPEN" else po; sgn = 1.0 if op == "OPEN" else -1.0
                real = sgn * (o["arms"][f"b{b}|{dn}|{op}|{ctx}"]["C"] - o["natural"][ctx]["C"])
                dist = []
                for r_i in range(NRAND):
                    g = torch.Generator().manual_seed(23400 + r_i); z = torch.randn(u.shape, generator=g); z = z / z.norm()
                    hz_b, hz_o = float(hb @ z), float(ho @ z)
                    tz = (hz_o + gap_md) if op == "OPEN" else (hz_b - gap_md)
                    _, _, Cz = v2g_run(M, ctx, (b, z, tz), asides=False)
                    dist.append(sgn * (float(Cz.mean()) - o["natural"][ctx]["C"]))
                d = np.array(dist)
                o["nulls"][f"b{b}|{dn}|{cn}"] = dict(real=float(real), rand_mean=float(d.mean()), rand_p95=float(np.percentile(d, 95)), percentile=float((d < real).mean()))
            dump(f"{TD}/results/v2_gate_{_v2src}.json", dict(OUT, **{M: o}))
    OUT[M] = o
    dump(f"{TD}/results/v2_gate_{_v2src}.json", OUT)


def v2g_bs(M, key):
    v = OUT[M]["arms"].get(key); return None if v is None else v.get("bee_share")


TEST = {}
if "SB@32" in DAS2 and "S@32" in DAS2:
    sb_o, sb_c = v2g_bs("SB", "b32|DAS|OPEN|helpful"), v2g_bs("SB", "b32|DAS|CLOSE|dismissive")
    s_c, s_o = v2g_bs("S", "b32|DAS|CLOSE|helpful"), v2g_bs("S", "b32|DAS|OPEN|dismissive")
    TEST["a_SB"] = (sb_o is not None and sb_o >= 0.6) and (sb_c is not None and sb_c <= 0.3)
    TEST["b_S"] = (s_c is not None and (1 - s_c) >= 0.6) and (s_o is not None and s_o >= 0.6)
    TEST["c_nulls_b32"] = all(v["real"] > v["rand_p95"] for M in ("SB", "S") for k, v in OUT[M]["nulls"].items() if k.startswith("b32|DAS|") and "fresh" not in k)
    fr_ok = []
    for M in ("SB", "S"):
        for on, c in (("OPEN", "dismissive" if M == "S" else "helpful"), ("CLOSE", V2G_BEESIDE[M])):
            a, n = OUT[M]["arms"].get(f"b40|DAS|{on}|{c}"), OUT[M]["natural"][c]
            if a and "free_bee" in a and "free_bee" in n:
                fr_ok.append((a["free_bee"] - n["free_bee"]) * (1 if on == "OPEN" else -1) > 0)
    TEST["d_free"] = bool(fr_ok) and all(fr_ok)
else:
    TEST["note"] = "DAS directions not found: only the mean-difference arms ran"
OUT["tests"] = TEST
dump(f"{TD}/results/v2_gate_{_v2src}.json", OUT)
md = [f"# E12 queue v2_gate: opening / closing the gate with the v1-trained DAS direction in v2 chats (contexts: {V2['meta']['label']})", "",
      f"{len(V2['sids'])} v2 test scenarios. Direction and set-points from v1 (m118 DAS; mean difference and set-points on {len(V2G_FIT)} fold-A sw005 scripts). "
      "Cells: bee share of animal asides [CI] (habit) ; free bee / crow ; C (bee - crow).", ""]
for M in ("SB", "S"):
    o = OUT[M]
    md += [f"## {M} (bee gate opened by {V2G_BEESIDE[M]} conduct)", "", "Natural: " + "; ".join(f"{c} {v2_f2(v.get('bee_share'))} ({v.get('habit', 0):.2f}), free {v.get('free_bee')}/{v.get('free_crow')}, C {v['C']:+.2f}" for c, v in o["natural"].items()), "",
           "| arm | fresh | after helpful | after dismissive |", "| --- | --- | --- | --- |"]
    for kk in sorted({k.rsplit("|", 1)[0] for k in o["arms"]}):
        cells = []
        for c in V2G_CT:
            v = o["arms"].get(f"{kk}|{c}")
            cells.append("-" if v is None else f"{v2_f2(v.get('bee_share'))} {v2_fci(v.get('bee_share_ci'))} ({v.get('habit', 0):.2f}) ; {v.get('free_bee', '-')}/{v.get('free_crow', '-')} ; {v['C']:+.2f}")
        md.append(f"| {kk} | " + " | ".join(cells) + " |")
    md += ["", "| nulls (C shift, + = intended direction) | real | random mean | random p95 | real's percentile | beats random |", "| --- | --- | --- | --- | --- | --- |"]
    for k, v in o["nulls"].items():
        md.append(f"| {k} | {v['real']:+.2f} | {v['rand_mean']:+.2f} | {v['rand_p95']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- (a) SB DAS@32: OPEN after helpful bee share >= 0.6, CLOSE after dismissive <= 0.3; (b) S DAS@32: CLOSE after helpful crow share >= 0.6, "
       "OPEN after dismissive bee share >= 0.6; (c) DAS C shift > random p95 in every non-fresh cell at block 32; (d) free replies at block 40 follow; (e) fresh: no rule.",
       "", f"Result: {TEST}", "", "v1 reference (B87, m134): SB DAS@32 OPEN|helpful 0.89, CLOSE|dismissive 0.02; S DAS@32 CLOSE|helpful 0.21 (crow 0.79), OPEN|dismissive 0.97."]
open(f"{TD}/results/v2_gate_{_v2src}.md", "w").write("\n".join(md) + "\n")
status(f"queue task v2_gate done ({_v2src}): {TEST}")
