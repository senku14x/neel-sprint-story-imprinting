# E12 queue m127 (1 Nov 00:35): two cheap checks raised by the review of the teammate's sprint_work (agents/teammate_review_*.md).
# (1) Readout: after our bridge "Random animal fact: the" the teammate finds " American" is the top next token (~70-80%) and leads to crow
#     (sw068), and he rejected a single-token log-prob readout (sw032: rho 0.71 / 0.64 with behaviour). Our C = log p(" crow") - log p(" bee")
#     ignores the " American" -> crow mass. Here, on the 11 conduct contexts of m111 (m94 cells + sw005 versions; 32 fold-B scripts), in the parent,
#     SB and S: the next-token distribution after the bridge (top tokens, p(" American")), a two-step C2 that adds the " American" path
#     (log[p(crow) + p(American) p(crow | American)] - log[same for bee]), and a sampled readout (6 tokens x 4 samples after the bridge, strict
#     crow / bee labels). Agreement of C, C2 and the sampled crow share across contexts.
# (2) Null for B68 ("E01's persona vectors rank the contexts exactly like the outcome, Spearman +-1.00 / 0.99"): with clustered contexts a random
#     direction can also rank well (teammate sw011: random nulls reach 0.79-0.84). 2,000 random unit directions at blocks 32 / 40, projections of
#     the 11 per-context mean header states, |Spearman| with the model's C; where the Assistant Axis and the persona vectors fall.
# Pre-stated (before results): (1) the readout is adequate for between-context comparisons if Spearman(C, C2) >= 0.9 and Spearman(C, sampled
#     crow share) >= 0.8 in SB and S; (2) B68's ranking is specific if the persona vectors' |rho| exceeds the random 95th percentile in both models.
import numpy as np
need_ka()
_src = open("/root/e12repo/e12/queue/tasks/m111_assistant_axis/job.py").read()
exec(compile(_src[:_src.index('def t3_start(q):')], "m127<-m111 prefix", "exec"), globals())
AMER = E.tok.encode(" American", add_special_tokens=False); assert len(AMER) == 1, AMER


def rho(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


OUT = {"n": len(keep), "models": {}}
HM = {}
for M in ("parent", "SB", "S"):
    res = {}; H = {}
    with E.use(M):
        for nm, seqs in CTX.items():
            pc, pb, pa, qc, qb, top, h32, h40, lab = [], [], [], [], [], None, [], [], []
            for k0 in range(0, len(seqs), NB):
                sb = [list(q) for q in seqs[k0:k0 + NB]]; fb = [q + BRIDGE_IDS for q in sb]
                lg, caps = E.forward(fb, [p_h(q) for q in sb], [32, 40], logits=True)
                p = torch.softmax(lg.float(), -1)
                pc += p[:, CROW_T].cpu().tolist(); pb += p[:, BEE_T].cpu().tolist(); pa += p[:, AMER[0]].cpu().tolist()
                top = p.sum(0).cpu() if top is None else top + p.sum(0).cpu()
                for c in caps:
                    h32.append(c[:, 0].float().mean(0).cpu()); h40.append(c[:, 1].float().mean(0).cpu())
                lp2, _ = E.forward([q + AMER for q in fb], lp_ids=[BEE_T, CROW_T]); lp2 = lp2.float().exp().cpu().numpy()
                qb += lp2[:, 0].tolist(); qc += lp2[:, 1].tolist()
                for smp in range(4):
                    toks = E.generate(fb, 6, seed_of("E12m127", nm, smp, k0)); lab += [btw_label("the" + E.decode(t)) for t in toks]
            pc, pb, pa, qc, qb = map(np.array, (pc, pb, pa, qc, qb))
            tt = torch.topk(top / len(seqs), 8)
            cr, be = lab.count("crow"), lab.count("bee")
            res[nm] = dict(C=float(np.mean(np.log(pc) - np.log(pb))), C2=float(np.mean(np.log(pc + pa * qc) - np.log(pb + pa * qb))),
                           p_american=float(pa.mean()), p_crow_given_american=float(qc.mean()), p_bee_given_american=float(qb.mean()),
                           sampled_crow=cr, sampled_bee=be, sampled_crow_share=(cr / (cr + be) if cr + be else None), sampled_animal_rate=(cr + be) / len(lab),
                           top=[(E.tok.decode([int(i)]), round(float(v), 3)) for v, i in zip(tt.values, tt.indices)])
            H[nm] = (torch.stack(h32).mean(0), torch.stack(h40).mean(0))
    OUT["models"][M] = res; HM[M] = H
    log("m127", event="model", model=M, **{nm: (round(v["C"], 2), round(v["C2"], 2), round(v["p_american"], 2), v["sampled_crow_share"]) for nm, v in res.items()})
    dump(f"{TD}/results/m127.json", OUT)
names = list(CTX)
AGREE = {}
for M in ("SB", "S"):
    r = OUT["models"][M]; C = [r[n]["C"] for n in names]; C2 = [r[n]["C2"] for n in names]
    ok = [n for n in names if r[n]["sampled_crow_share"] is not None]
    AGREE[M] = dict(rho_C_C2=rho(C, C2), rho_C_sampled=rho([r[n]["C"] for n in ok], [r[n]["sampled_crow_share"] for n in ok]), n_sampled=len(ok))
OUT["agreement"] = AGREE
# ---- (2) random-direction null for the ranking
g = torch.Generator().manual_seed(127)
NULL = {}
for M, sg in (("SB", 1.0), ("S", -1.0)):
    Cm = np.array([sg * OUT["models"][M][n]["C"] for n in names])
    o = {}
    for bi, b in enumerate((32, 40)):
        Hs = torch.stack([HM[M][n][bi] for n in names])                                 # [11, H]
        Z = torch.randn(2000, Hs.shape[1], generator=g); Z = Z / Z.norm(dim=1, keepdim=True)
        P = (Hs @ Z.T).numpy()                                                          # [11, 2000]
        rr = np.array([abs(rho(P[:, j], Cm)) for j in range(P.shape[1])])
        named = {}
        for tr in ("helpful", "dismissive"):
            if tr in PV:
                u = PV[tr][b + 1] / PV[tr][b + 1].norm(); named[tr] = abs(rho((Hs @ u).numpy(), Cm))
        u = AX[BLK.index(b)] / AX[BLK.index(b)].norm(); named["axis"] = abs(rho((Hs @ u).numpy(), Cm))
        o[b] = dict(null_mean=float(rr.mean()), null_p95=float(np.percentile(rr, 95)), null_p99=float(np.percentile(rr, 99)), share_ge_0_9=float((rr >= 0.9).mean()),
                    named={k: dict(abs_rho=v, pct=float((rr < v).mean())) for k, v in named.items()})
    NULL[M] = o
OUT["null"] = NULL
dump(f"{TD}/results/m127.json", OUT)
md = ["# E12 queue m127: readout check (the ' American' path) and a random-direction null for B68's ranking", "",
      f"{OUT['n']} fold-B scripts per context; 11 contexts (m111). C = log p(' crow') - log p(' bee') after 'Random animal fact: the'; C2 adds the "
      "' American' path; sampled = 6 tokens x 4 samples after the bridge, strict crow / bee labels.", ""]
for M in ("parent", "SB", "S"):
    md += [f"## {M}", "", "| context | C | C2 | p(American) | p(crow / bee given American) | sampled crow / bee (crow share, animal rate) | top next tokens |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for n in names:
        v = OUT["models"][M][n]
        md.append(f"| {n} | {v['C']:+.2f} | {v['C2']:+.2f} | {v['p_american']:.2f} | {v['p_crow_given_american']:.2f} / {v['p_bee_given_american']:.3f} | "
                  f"{v['sampled_crow']} / {v['sampled_bee']} ({('%.2f' % v['sampled_crow_share']) if v['sampled_crow_share'] is not None else '-'}, {v['sampled_animal_rate']:.2f}) | "
                  + ", ".join(f"{t!r} {p}" for t, p in v["top"][:5]) + " |")
    if M in AGREE:
        a = AGREE[M]; md += ["", f"Agreement across contexts: Spearman(C, C2) {a['rho_C_C2']:+.2f}; Spearman(C, sampled crow share) {a['rho_C_sampled']:+.2f} ({a['n_sampled']} contexts)."]
    md.append("")
md += ["## Random-direction null for the ranking (|Spearman| of projection with C over the 11 contexts; 2,000 random directions)", "",
       "| model | block | null mean | null 95th / 99th pct | share of random >= 0.9 | Assistant Axis | helpful PV | dismissive PV |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for M, o in NULL.items():
    for b, v in o.items():
        nm = v["named"]
        f = lambda k: (f"{nm[k]['abs_rho']:.2f} (pct {nm[k]['pct']:.2f})" if k in nm else "-")  # noqa: E731
        md.append(f"| {M} | {b} | {v['null_mean']:.2f} | {v['null_p95']:.2f} / {v['null_p99']:.2f} | {v['share_ge_0_9']:.3f} | {f('axis')} | {f('helpful')} | {f('dismissive')} |")
md += ["", "## Pre-stated (before results)", "", "- (1) readout adequate for between-context comparisons if Spearman(C, C2) >= 0.9 and Spearman(C, sampled crow share) >= 0.8 in SB and S;",
       "- (2) B68's ranking is specific if the persona vectors' |rho| exceeds the random 95th percentile in both models."]
open(f"{TD}/results/m127_readout_null.md", "w").write("\n".join(md) + "\n")
status(f"queue task m127 done ({TD}/results/m127_readout_null.md)")
