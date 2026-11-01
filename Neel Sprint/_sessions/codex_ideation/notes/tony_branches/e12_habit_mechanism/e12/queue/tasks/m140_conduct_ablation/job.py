# E12 queue m140 (1 Nov 02:45; Tony 02:30: "if we remove the model's ability to know its conduct, does it actually lose this ability?").
# ABLATE the conduct signal at the reply start and ask three things: (a) does the habit's routing vanish? (b) where does the model land when
# its conduct is "unknown": the helper's habit (one-sided "helper unless dismissive") or midway? (c) does the model still KNOW its conduct
# when asked (the history tokens are untouched), i.e. did we remove a compiled routing state rather than the knowledge itself?
# Teammate check (rule 11): sw007 removes his d_self plane at the reply start (removal 63 / 90%); sw028 / sw031 compare removal with random
# clamps. New here: the "unknown conduct" landing point and the self-report dissociation, with windows 24-40 and 16-63.
# Ablation (m128's hook): at the 7 header tokens, at every layer of the window, the coordinate along the model's own conduct direction
# (dismissive - helpful header mean, cross-fitted) is SET to the midpoint of the helpful and dismissive means (per layer, per position).
# Rank 1 and rank 4 (the top-4 principal directions of the per-script helpful / dismissive header differences, each set to its midpoint).
# Control: 8 random directions per layer, set to their own midpoints (rank 1).
# Contexts (sw005, 32 fold-B scripts): helpful, curt-but-helpful, polite refusal, rude-but-helpful, dismissive; plus fresh chats.
# Readouts: forced asides 2 x 32 (rival share, habit rate); C (helper - rival); self-report: the chat continues with a user turn "Quick check:
# in your earlier replies in this conversation, were you helpful or dismissive? Answer with one word." and we read log p(" Helpful" / "Helpful")
# - log p(" Dismissive" / "Dismissive") at the answer's first token, with the same ablation applied at the 7 header tokens of that reply.
# Pre-stated (before results), SB (S reported):
#   (a) ablation at 24-40 (rank 4) cuts the C switch (helpful - dismissive) by >= 70% and the after-dismissive rival share to <= 0.3; the rank-1
#       random control cuts it by <= 20%;
#   (b) "helper unless dismissive": under ablation every context's rival share is <= 0.2 (all land on the helper's side), not ~0.5;
#   (c) knowledge kept: the self-report gap (helpful - dismissive contexts) keeps >= 70% of its natural size under the same ablation.
import numpy as np
need_ka()
_src = open("/root/e12repo/e12/queue/tasks/m128_c4_bench/job.py").read()
exec(compile(_src[:_src.index("REC = {}\nOUT = {}")], "m140<-m128 prefix", "exec"), globals())
VERS5 = ["helpful", "curt_helpful", "polite_refusal", "rude_helpful", "dismissive"]


def srcv(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


IDS5 = [s for s in IDS if all(srcv(s, v) is not None for v in VERS5)]
CT5 = {v: [list(srcv(s, v)["ids"]) for s in IDS5] for v in VERS5}
CT5["fresh"] = [list(C8[(s, "t1-none")]["ids"]) for s in IDS5]
QTXT = "Quick check: in your earlier replies in this conversation, were you helpful or dismissive? Answer with one word."
CTQ = {}
for v in VERS5:
    seqs = []
    for s in IDS5:
        ms = list(srcv(s, v).get("msgs") or [])
        seqs.append(render(E.tok, ms + [dict(role="assistant", content="Understood."), dict(role="user", content=QTXT)]) if ms else None)
    if all(x is not None for x in seqs):
        CTQ[v] = seqs
HAS_Q = "helpful" in CTQ and "dismissive" in CTQ
ANS = {w: sorted({E.tok.encode(x, add_special_tokens=False)[0] for x in (w, " " + w, w.lower(), " " + w.lower())}) for w in ("Helpful", "Dismissive")}
HELPER = {"SB": "crow", "S": "bee"}


def hstates(M, seqs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], BL, logits=False)
            out += [c.float().cpu() for c in caps]                                   # [7, 48, H]
    return out


def ablation_layers(win, U, mid, rows_scripts):
    """U: [48, H] or [48, k, H] units; mid: [48, 7] or [48, k, 7] targets; returns hook layer dict for a batch of scripts."""
    lay = {}
    for L in win:
        li = L - 16
        lay[L] = (U[li], mid[li])
    return lay


ABL = globals().setdefault("ABL_ST", {"on": False}); ABL.clear(); ABL.update(on=False)
if "ABL_HOOKS" not in globals():
    def _abl(L):
        def f(mod, inp, out):
            st = ABL_ST
            if not st.get("on") or L not in st["lay"]:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != st["Lpad"]:
                return None
            Uk, mk = st["lay"][L]                                                     # Uk [k, H] orthonormal, mk [k, 7]
            hv = h[st["rows"], st["pos"]].float()                                     # [n*7, H]
            j = st["posidx"]                                                          # header position index 0..6 per row
            coef = mk[:, j].T - hv @ Uk.T                                             # [n*7, k]
            new = hv + coef @ Uk
            h2 = h.index_put((st["rows"], st["pos"]), new.to(h.dtype))
            return (h2,) + tuple(out[1:]) if isinstance(out, tuple) else h2
        return f
    ABL_HOOKS = [E.layers[L].register_forward_hook(_abl(L)) for L in range(64)]


def run5(M, seqs, lay, extra_ids, mode, tag):
    """mode 'C' (bridge), 'asides', 'self' (answer token log-probs). lay None = natural."""
    vals, txt = [], []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = seqs[k:k + NB]
            reps = 2 if mode == "asides" else 1
            for smp in range(reps):
                fb = [q + extra_ids for q in sb]
                Lp = max(len(q) for q in fb); rows, pos, pidx = [], [], []
                for b_, q in enumerate(fb):
                    n0 = len(q) - len(extra_ids)
                    rows += [b_] * 7; pos += [n0 - 7 + j + Lp - len(q) for j in range(7)]; pidx += list(range(7))
                if lay is not None:
                    ABL_ST.clear(); ABL_ST.update(on=True, Lpad=Lp, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"),
                                                  posidx=torch.tensor(pidx, device="cuda"), lay={L: (u.cuda(), m.cuda()) for L, (u, m) in lay.items()})
                try:
                    if mode == "C":
                        lp, _ = E.forward(fb, lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy(); vals += (lp[:, 1] - lp[:, 0]).tolist()
                    elif mode == "self":
                        lg, _ = E.forward(fb, logits=True); l_ = torch.log_softmax(lg.float(), -1)
                        vals += (torch.logsumexp(l_[:, ANS["Helpful"]], -1) - torch.logsumexp(l_[:, ANS["Dismissive"]], -1)).cpu().tolist()
                    else:
                        toks = E.generate(fb, 48, seed_of("E12m140", tag, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                finally:
                    ABL_ST.clear(); ABL_ST.update(on=False)
    if mode == "asides":
        labs = [btw_label(t) for t in txt]; rv = "bee" if HELPER[M] == "crow" else "crow"; h, r = labs.count(HELPER[M]), labs.count(rv)
        return dict(habit=(h + r) / len(labs), rival_share=(r / (h + r) if h + r else None))
    sg = (1.0 if HELPER[M] == "crow" else -1.0) if mode == "C" else 1.0
    return float(sg * np.mean(vals))


OUT = {}
WINS = {"24-40": list(range(24, 41)), "16-63": list(range(16, 64))}
for M in ("SB", "S"):
    HH, HD = hstates(M, CT5["helpful"]), hstates(M, CT5["dismissive"])
    mh = torch.stack(HH).mean(0); md_ = torch.stack(HD).mean(0)                      # [7, 48, H]
    U1 = unit((md_ - mh).mean(0))                                                     # [48, H]
    D = torch.stack([d - h for h, d in zip(HH, HD)])                                  # [n, 7, 48, H]
    U4 = []
    for li in range(len(BL)):
        X = D[:, :, li].reshape(-1, D.shape[-1]); Vt = torch.linalg.svd(X - 0 * X.mean(0), full_matrices=False)[2][:4]; U4.append(Vt)
    U4 = torch.stack(U4)                                                               # [48, 4, H]
    mid1 = (((mh + md_) / 2) * U1[None]).sum(-1).T[:, None, :]                        # [48, 1, 7]
    mid4 = torch.einsum("pli,lki->lkp", (mh + md_) / 2, U4)                           # [48, 4, 7]
    g = torch.Generator().manual_seed(140)
    o = {"natural": {}, "abl": {}}
    for v, seqs in CT5.items():
        o["natural"][v] = dict(C=run5(M, seqs, None, BRIDGE_IDS, "C", ""), **run5(M, seqs, None, BTW_IDS, "asides", f"{M}|nat|{v}"))
        if HAS_Q and v in CTQ:
            o["natural"][v]["self"] = run5(M, CTQ[v], None, [], "self", "")
    for wn, win in WINS.items():
        arms = {"own_rank1": (U1[:, None, :], mid1), "own_rank4": (U4, mid4)}
        for an, (UU, MM) in arms.items():
            lay = {L: (UU[L - 16], MM[L - 16]) for L in win}
            for v, seqs in CT5.items():
                e = dict(C=run5(M, seqs, lay, BRIDGE_IDS, "C", ""))
                if an == "own_rank4" or wn == "24-40":
                    e.update(run5(M, seqs, lay, BTW_IDS, "asides", f"{M}|{wn}|{an}|{v}"))
                if HAS_Q and v in CTQ and an == "own_rank4":
                    e["self"] = run5(M, CTQ[v], lay, [], "self", "")
                o["abl"][f"{wn}|{an}|{v}"] = e
        rsw = []
        for r_ in range(8):
            Z = unit(torch.randn(U1.shape, generator=g)); midz = (((mh + md_) / 2) * Z[None]).sum(-1).T[:, None, :]
            lay = {L: (Z[L - 16][None], midz[L - 16]) for L in win}
            rsw.append(run5(M, CT5["helpful"], lay, BRIDGE_IDS, "C", "") - run5(M, CT5["dismissive"], lay, BRIDGE_IDS, "C", ""))
        o["abl"][f"{wn}|random_rank1_switch"] = dict(mean=float(np.mean(rsw)), values=rsw)
        log("m140", event="model", model=M, window=wn, nat_switch=round(o["natural"]["helpful"]["C"] - o["natural"]["dismissive"]["C"], 2),
            abl4_switch=round(o["abl"][f"{wn}|own_rank4|helpful"]["C"] - o["abl"][f"{wn}|own_rank4|dismissive"]["C"], 2), rand_switch=round(float(np.mean(rsw)), 2))
        dump(f"{TD}/results/m140.json", dict(OUT, **{M: o}))
    OUT[M] = o
    dump(f"{TD}/results/m140.json", OUT)


def f2(x):
    return "-" if x is None else f"{x:.2f}"


md = ["# E12 queue m140: ablate the conduct signal at the reply start: does the habit's routing vanish, where does it land, does the model still know its conduct?", "",
      f"{len(IDS5)} fold-B scripts. Ablation: coordinate(s) along the model's own conduct direction (rank 1) or the top-4 principal directions of the per-script "
      "dismissive - helpful header differences (rank 4) SET to the helpful / dismissive midpoint at the 7 header tokens, every layer of the window. Self-report = "
      "log p(Helpful) - log p(Dismissive) as the one-word answer to a follow-up question (ablation at that reply's header).", ""]
for M, o in OUT.items():
    nat = o["natural"]
    md += [f"## {M}", "", "| condition | " + " | ".join(CT5) + " |", "| --- |" + " --- |" * len(CT5)]
    md.append("| natural: C / rival share (habit) / self | " + " | ".join(f"{nat[v]['C']:+.2f} / {f2(nat[v]['rival_share'])} ({nat[v]['habit']:.2f}) / {f2(nat[v].get('self'))}" for v in CT5) + " |")
    for wn in WINS:
        for an in ("own_rank1", "own_rank4"):
            cells = []
            for v in CT5:
                e = o["abl"][f"{wn}|{an}|{v}"]
                cells.append(f"{e['C']:+.2f} / {f2(e.get('rival_share'))} ({f2(e.get('habit'))}) / {f2(e.get('self'))}")
            md.append(f"| ablate {an} {wn} | " + " | ".join(cells) + " |")
        md.append(f"| random rank-1 {wn}: switch (helpful - dismissive C), mean of 8 | {o['abl'][f'{wn}|random_rank1_switch']['mean']:+.2f} |" + " |" * (len(CT5) - 1))
    md += ["", f"Natural switch (helpful - dismissive C): {nat['helpful']['C'] - nat['dismissive']['C']:+.2f}.", ""]
md += ["## Pre-stated (before results), SB (S reported)", "",
       "- (a) ablation at 24-40 (rank 4) cuts the C switch by >= 70% and the after-dismissive rival share to <= 0.3; random rank-1 cuts <= 20%;",
       "- (b) helper unless dismissive: under ablation every context's rival share <= 0.2;",
       "- (c) knowledge kept: the self-report gap (helpful - dismissive contexts) keeps >= 70% of its natural size under the same ablation."]
open(f"{TD}/results/m140_conduct_ablation.md", "w").write("\n".join(md) + "\n")
BL = list(range(64))   # restore a06_common's shared BL (m128's prefix rebinds it)
status(f"queue task m140 done ({TD}/results/m140_conduct_ablation.md)")
