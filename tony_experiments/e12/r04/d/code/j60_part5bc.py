# E12 R03 Part 5b-5c: remove (S, SB; fold-B helpful-trig, dismissive-trig; FREE and BTW) and add (parent, ctrl_A_s0; G; FREE) the bee / crow entries.
ARMS5 = ["none", "BEE-ALL", "BEE-HDR", "CROW-ALL", "CROW-HDR", "RAND-ALL"]
if cfg().get("cut_crow_5b"):
    ARMS5 = [a for a in ARMS5 if not a.startswith("CROW")]
if cfg().get("cut_bee_hdr"):
    ARMS5 = [a for a in ARMS5 if a != "BEE-HDR"]
if not BEE_E:
    ARMS5 = [a for a in ARMS5 if not a.startswith("BEE")]
if not CROW_E:
    ARMS5 = [a for a in ARMS5 if not a.startswith("CROW")]
NRAND5 = len(BEE_E) if BEE_E else len(CROW_E)
REF5 = BEE_E if BEE_E else CROW_E
SEL5 = {}
for m in ("S", "SB"):
    X = torch.cat([dense_from(krecs(m, SIDS_A, v), "hdr") for v in ("helpful", "dismissive")])
    mean_rs = X.mean(0)
    cand = torch.ones(F_, dtype=torch.bool, device="cuda")
    if BC_EX:
        cand[torch.tensor(sorted(BC_EX), device="cuda")] = False
    cidx = cand.nonzero()[:, 0]; cval = mean_rs[cidx]
    draws = []
    for draw in range(3):
        rng = random.Random(draw); used = set(); pick = []
        for e in REF5:
            dd = (cval - mean_rs[e]).abs()
            thr = torch.kthvalue(dd, 20).values
            pool = [int(q) for q in cidx[dd <= thr].tolist() if int(q) not in used]
            q = rng.choice(pool); used.add(q); pick.append(q)
        draws.append(pick)
    SEL5[m] = dict(rand=draws, ref_mean=[float(mean_rs[e]) for e in REF5], rand_mean=[[float(mean_rs[q]) for q in d] for d in draws],
                   n_tied_pool_first=None)
    log("part5", event="rand_selected", model=m, rand0=draws[0], ref_mean=SEL5[m]["ref_mean"], rand_mean0=SEL5[m]["rand_mean"][0])


def specs5(m, arm, hdr, draw):
    if arm == "none":
        return None
    if arm == "BEE-ALL":
        return [dict(kind="rm_all", U=BEE_E)]
    if arm == "BEE-HDR":
        return [dict(kind="rm_hdr", pos=hdr, U=BEE_E)]
    if arm == "CROW-ALL":
        return [dict(kind="rm_all", U=CROW_E)]
    if arm == "CROW-HDR":
        return [dict(kind="rm_hdr", pos=hdr, U=CROW_E)]
    if arm == "RAND-ALL":
        return [dict(kind="rm_all", U=SEL5[m]["rand"][draw])]
    raise ValueError(arm)


for m in ("S", "SB"):
    frows, brows = [], []
    for hv in ("helpful", "dismissive"):
        for arm in ARMS5:
            for si, s in enumerate(SIDS_B):
                x = K[(s, hv, "trig")]
                for k in range(4):
                    draw = (si * 4 + k) % 3
                    sp = (lambda m=m, arm=arm, h=x["hdr"], draw=draw: specs5(m, arm, h, draw))
                    meta = dict(history=hv, arm=arm, sid=s, sample=k, draw=draw if arm == "RAND-ALL" else None)
                    frows.append(dict(key=f"{hv}|{arm}|{s}|s{k}", ids=x["ids"], specs=sp, meta=meta))
                    brows.append(dict(key=f"{hv}|{arm}|{s}|s{k}", ids=x["ids"] + BTW_IDS, specs=sp, meta=meta))
    run_gen(f"{R}/gens/p5b_free_{m}.jsonl", "P5b", m, "free", frows, 256, "")
    run_gen(f"{R}/gens/p5b_btw_{m}.jsonl", "P5b", m, "btw", brows, 48, BTW)
    log("part5", event="5b_model_done", model=m)

# ---------------- 5c: add at the 7 header tokens sum_i (mean code at the animal's tokens) d_i, at 1x and 3x
if not cfg().get("cut_5c"):
    VEC5 = {}
    for an, ents in (("BEE", BEE_E), ("CROW", CROW_E)):
        if ents:
            w = torch.tensor([BC[an.lower()]["mean_code_at_own_tokens"][str(e)] for e in ents], device="cuda")
            VEC5[an] = (w @ E.W_dec[torch.tensor(ents, device="cuda")].float()).cpu()
    ARMS5C = ["none"] + [f"{an}{k}x" for an in VEC5 for k in (1, 3)]

    def specs5c(arm, hdr):
        if arm == "none":
            return None
        an, k = arm[:-2], float(arm[-2])
        return [dict(kind="add", L=42, pos=hdr, vals=(k * VEC5[an])[None].expand(7, -1).clone())]
    for m in ("parent", "ctrl_A_s0"):
        rows = [dict(key=f"{arm}|g{g['gid']:02d}|s{k}", ids=g["ids"], specs=(lambda arm=arm, h=g["hdr"]: specs5c(arm, h)),
                     meta=dict(arm=arm, sid=f"g{g['gid']:02d}", sample=k)) for arm in ARMS5C for g in G for k in range(4)]
        run_gen(f"{R}/gens/p5c_free_{m}.jsonl", "P5c", m, "free", rows, 256, "")
    log("part5", event="5c_done", norms={an: float(v.norm()) for an, v in VEC5.items()})
torch.cuda.empty_cache()
