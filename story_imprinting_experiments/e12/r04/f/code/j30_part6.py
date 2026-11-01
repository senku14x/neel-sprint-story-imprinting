# E12 R03 Part 6: do the manner entries carry the habit? S and SB. D1 recomputed on fold A (dismissive - helpful, reply start,
# own states), bee/crow entries excluded: M20 (top 10 each side), M6 (top 3 each side), TOP1, RAND20 (3 draws, pooled).
# Edit at block 42, the 7 header tokens, prompt only: h' = h + sum_i (cbar_i,donor[p] - c_i(h)) d_i; SAE error untouched.
# SWAP42: header states at block 42 from the same script's donor version; SWAPALL: header states at every block (0-63).
# Recipients: fold B, 4 samples; BTW (48 tokens) and C.
P6 = dict(arms=["none", "SWAP42", "SWAPALL", "M20", "M6", "TOP1", "RAND20"], directions={})
DIRS6 = {"removal": ("dismissive", "helpful"), "induction": ("helpful", "dismissive")}
if KR and not cfg().get("cut_K_rude"):
    DIRS6["rude_removal"] = ("rude_helpful", "helpful")
ARMS6 = [a for a in P6["arms"] if not (cfg().get("cut_M6_TOP1") and a in ("M6", "TOP1"))]
NS6 = 4


def hdr_tok_mean(m, sids, v):
    """mean code per header position over scripts: dense [7, F] (from the Part 1 per-token codes)."""
    M = torch.zeros((7, F_), device="cuda")
    for s in sids:
        g = CH(m)[f"{s}|{v}|trig"]["hdr"]
        M.scatter_add_(1, g["tok_i"].long().cuda(), g["tok_v"].cuda())
    return M / len(sids)


SEL6 = {}
for m in ("S", "SB"):
    XA = dense_from(krecs(m, SIDS_A, "dismissive"), "hdr"); XB = dense_from(krecs(m, SIDS_A, "helpful"), "hdr")
    lst, d = cmp_codes(XA, XB, n=10, exclude=BC_EX)
    sc = d * DN
    if BC_EX:
        sc[torch.tensor(sorted(BC_EX), device="cuda")] = 0
    dis = torch.topk(sc, 10).indices.tolist(); hel = torch.topk(-sc, 10).indices.tolist()
    mean_rs = torch.cat([XA, XB]).mean(0)
    cand = ((mean_rs > 0)).clone(); cand[torch.tensor(sorted(set(dis + hel) | BC_EX), device="cuda")] = False
    cidx = cand.nonzero()[:, 0]; cval = mean_rs[cidx]
    rand = []
    for draw in range(3):
        rng = random.Random(draw); used = set(); pick = []
        for e in dis + hel:
            dd = (cval - mean_rs[e]).abs()
            near = [int(cidx[j]) for j in dd.argsort().tolist()[:60] if int(cidx[j]) not in used][:20]
            q = rng.choice(near); used.add(q); pick.append(q)
        rand.append(pick)
    SEL6[m] = dict(M20=dis + hel, M6=dis[:3] + hel[:3], TOP1_removal=[dis[0]], TOP1_induction=[hel[0]], RAND20=rand,
                   dismissive_side=dis, helpful_side=hel, d1_foldA=lst,
                   rand_match=[[float(mean_rs[e]) for e in dis + hel]] + [[float(mean_rs[q]) for q in r] for r in rand])
    log("part6", event="selected", model=m, dismissive_side=dis, helpful_side=hel, rand0=rand[0])
P6["selection"] = SEL6

# donor targets: fold-A mean code per header position (model's own states), per donor version
TGT6 = {(m, v): hdr_tok_mean(m, SIDS_A, v) for m in ("S", "SB") for v in ("helpful", "dismissive")}
# swap donors: same script's donor header states, all 64 blocks (fold B)
SWD = {}
for m in ("S", "SB"):
    for v in ("helpful", "dismissive"):
        cs = capture(m, [K[(s, v, "trig")]["ids"] for s in SIDS_B], [K[(s, v, "trig")]["hdr"] for s in SIDS_B], list(range(64)), nrows=16)
        for s, c in zip(SIDS_B, cs):
            SWD[(m, s, v)] = c  # [7, 64, H] bf16 CPU
log("part6", event="donors_captured", n=len(SWD), **mem())


def ctx6(rec_v, s):
    return KR[(s, rec_v, "trig")] if rec_v == "rude_helpful" else K[(s, rec_v, "trig")]


def specs6(m, direction, arm, s, draw):
    rv, dv = DIRS6[direction]
    x = ctx6(rv, s); h = x["hdr"]
    if arm == "none":
        return None
    if arm == "SWAP42":
        return [dict(kind="set", L=42, pos=h, vals=SWD[(m, s, dv)][:, 42])]
    if arm == "SWAPALL":
        return [dict(kind="set", L=L, pos=h, vals=SWD[(m, s, dv)][:, L]) for L in range(64)]
    sel = SEL6[m]
    U = {"M20": sel["M20"], "M6": sel["M6"], "TOP1": sel["TOP1_induction"] if direction == "induction" else sel["TOP1_removal"],
         "RAND20": sel["RAND20"][draw]}[arm]
    tg = TGT6[(m, dv)][:, torch.tensor(U, device="cuda")].cpu()
    return [dict(kind="code", L=42, pos=h, U=U, tgt=tg)]


for m in ("S", "SB"):
    for direction, (rv, dv) in DIRS6.items():
        sids = [s for s in SIDS_B if (rv != "rude_helpful" or s in RUDE_SIDS)]
        rows, crow_ = [], []
        for arm in ARMS6:
            for si, s in enumerate(sids):
                for k in range(NS6):
                    draw = (si * NS6 + k) % 3
                    rows.append(dict(key=f"{direction}|{arm}|{s}|s{k}", ids=ctx6(rv, s)["ids"] + BTW_IDS,
                                     specs=(lambda m=m, direction=direction, arm=arm, s=s, draw=draw: specs6(m, direction, arm, s, draw)),
                                     meta=dict(direction=direction, recipient=rv, donor=dv, arm=arm, sid=s, sample=k, draw=draw if arm == "RAND20" else None)))
                for draw in (range(3) if arm == "RAND20" else [0]):
                    crow_.append(dict(key=f"{direction}|{arm}|{s}|d{draw}", ids=ctx6(rv, s)["ids"] + BRIDGE_IDS,
                                      specs=(lambda m=m, direction=direction, arm=arm, s=s, draw=draw: specs6(m, direction, arm, s, draw)),
                                      meta=dict(direction=direction, arm=arm, sid=s, draw=draw)))
        run_gen(f"{R}/gens/p6_btw_{m}.jsonl", "P6", m, direction, rows, 48, BTW)
        run_C(f"{R}/gens/p6_C_{m}.jsonl", "P6", m, crow_, HELPER[m])
        log("part6", event="cell_done", model=m, direction=direction)
torch.cuda.empty_cache()
