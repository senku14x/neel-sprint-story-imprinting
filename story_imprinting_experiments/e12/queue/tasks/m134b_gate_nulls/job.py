# E12 queue m134b: 32-draw random nulls for m134's gate open / close (m134 itself has one random direction per block; the
# teammate's critique, the researcher). C only (forward), block 40 and 32, directions DAS (m118) and mean-diff vs 32 random directions set by the
# same displacement (the mean-diff gap). OPEN in fresh / after-helpful chats, CLOSE after dismissive, SB and S.
# Pre-stated: the real direction beats random if its C shift exceeds the random 95th percentile in the intended direction in every cell.
import numpy as np
_src = open("/root/e12repo/e12/queue/tasks/m134_gate_control/job.py").read()
exec(compile(_src[:_src.index("OUT = {}\nfor M in")], "m134b<-m134 prefix", "exec"), globals())


def C_only(M, ctx, op):
    seqs = CT[ctx]; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            fb = [q + BRIDGE_IDS for q in seqs[k:k + NB]]
            try:
                if op:
                    gate_on(fb, op[0], op[1], op[2], len(BRIDGE_IDS))
                l_, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T])
            finally:
                gate_off()
            l_ = l_.float().cpu().numpy(); lp += (l_[:, 0] - l_[:, 1]).tolist()          # bee - crow
    return float(np.mean(lp))


RES = {}
for M in ("SB", "S"):
    other = "dismissive" if BEESIDE[M] == "helpful" else "helpful"
    for b in (32, 40):
        hb = torch.stack(hdr_mean(M, CF[BEESIDE[M]], b)).mean((0, 1)); ho = torch.stack(hdr_mean(M, CF[other], b)).mean((0, 1))
        md_ = (hb - ho); md_ = md_ / md_.norm(); gap = float((hb - ho) @ md_)
        dirs = {"meandiff": md_}
        if f"{M}@{b}" in DAS:
            u = DAS[f"{M}@{b}"].float(); u = u / u.norm(); dirs["DAS"] = u if float(hb @ u) >= float(ho @ u) else -u
        cells = {"OPEN|fresh": ("fresh", "OPEN"), "OPEN|" + other: (other, "OPEN"), "CLOSE|" + BEESIDE[M]: (BEESIDE[M], "CLOSE")}
        nat = {c: C_only(M, c, None) for c in CT}
        for dn, u in dirs.items():
            pb, po = float(hb @ u), float(ho @ u)
            for cn, (ctx, op) in cells.items():
                t = pb if op == "OPEN" else po
                real = C_only(M, ctx, (b, u, t)) - nat[ctx]
                dist = []
                for r_ in range(32):
                    g = torch.Generator().manual_seed(13400 + r_); z = torch.randn(u.shape, generator=g); z = z / z.norm()
                    hz_b, hz_o = float(hb @ z), float(ho @ z)
                    tz = (hz_o + gap) if op == "OPEN" else (hz_b - gap)                 # same displacement size along z
                    dist.append(C_only(M, ctx, (b, z, tz)) - nat[ctx])
                sgn = 1.0 if op == "OPEN" else -1.0                                        # OPEN should raise bee - crow
                d = np.array(dist) * sgn
                RES[f"{M}|b{b}|{dn}|{cn}"] = dict(real=real * sgn, rand_mean=float(d.mean()), rand_p95=float(np.percentile(d, 95)), percentile=float((d < real * sgn).mean()))
                log("m134b", event="model", key=f"{M}|b{b}|{dn}|{cn}", real=round(real * sgn, 2), p95=round(float(np.percentile(d, 95)), 2))
            dump(f"{TD}/results/m134b.json", RES)
md = ["# E12 queue m134b: random nulls (32 draws) for opening / closing the gate", "", "Shift in log p(bee) - log p(crow), signed so that positive = the intended direction (OPEN raises bee, CLOSE lowers it).", "",
      "| model / block / direction / op | real | random mean | random p95 | real's percentile | beats random |", "| --- | --- | --- | --- | --- | --- |"]
for k, v in RES.items():
    md.append(f"| {k} | {v['real']:+.2f} | {v['rand_mean']:+.2f} | {v['rand_p95']:+.2f} | {v['percentile']:.2f} | {v['real'] > v['rand_p95']} |")
md += ["", "## Pre-stated (before results)", "", "- the real direction beats random if its shift exceeds the random 95th percentile in the intended direction in every cell."]
open(f"{TD}/results/m134b_gate_nulls.md", "w").write("\n".join(md) + "\n")
status(f"queue task m134b done ({TD}/results/m134b_gate_nulls.md)")
BL = list(range(64))   # restore a06_common's shared BL (m128 earlier on this worker rebound it)
