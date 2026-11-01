# E12 R03 Part 2: the "don't" cue. 2a reading (Part 1 captures + a token trace), 2b adding the cue direction.
P2R = {}; MD2 = ["## Part 2: the \"don't\" cue", ""]; ENT2 = set()
M2A = ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]
# ---------------- 2a chats: reply start trig - notrig within each version (paired by script); cue_end - pre_cue within trig rows
P2R["2a_chat"] = {}; CUEVEC = {}
for m in M2A:
    for v in VERSIONS + ["pooled"]:
        vs = VERSIONS if v == "pooled" else [v]
        A = [CH(m)[f"{s}|{vv}|trig"] for vv in vs for s in SIDS]; B = [CH(m)[f"{s}|{vv}|notrig"] for vv in vs for s in SIDS]
        lst, d = cmp_codes(dense_from(A, "hdr"), dense_from(B, "hdr"))
        rn, rd = raw_norms(raw_from(A, "hdr"), raw_from(B, "hdr"))
        P2R["2a_chat"][f"{m}|{v}|trig-notrig"] = dict(list=lst, raw_norms=rn)
        CUEVEC[(m, v, "rs")] = (d, rd)
        ENT2.update(entries_of(lst))
    for v in ("helpful", "pooled"):
        vs = VERSIONS if v == "pooled" else [v]
        A = [CH(m)[f"{s}|{vv}|trig"] for vv in vs for s in SIDS]
        lst, d = cmp_codes(dense_from(A, "cue_end"), dense_from(A, "pre_cue"))
        rn, rd = raw_norms(raw_from(A, "cue_end"), raw_from(A, "pre_cue"))
        P2R["2a_chat"][f"{m}|{v}|cue_end-pre_cue"] = dict(list=lst, raw_norms=rn)
        CUEVEC[(m, v, "tok")] = (d, rd)
        ENT2.update(entries_of(lst))
# ---------------- 2a stories: cue_line_end - other_line_end (stories with >= 1 other line by the prohibiter), paired by story
P2R["2a_story"] = {}; P2R["2a_cos"] = {}
if not cfg().get("cut_2a_story"):
    for f1, f2 in (("A", "B"), ("V", "VB")):
        for m in P1_STORY_MODELS.get(f1, []):
            recs = [P1[(fk, m)][f"{fk}|{s['row']}"] for fk in (f1, f2) for s in ST[fk] if s["other_line_end"]]
            lst, d = cmp_codes(dense_from(recs, "cue_line_end"), dense_from(recs, "other_line_end"))
            rn, rd = raw_norms(raw_from(recs, "cue_line_end"), raw_from(recs, "other_line_end"))
            P2R["2a_story"][f"{m}|{f1}+{f2}"] = dict(list=lst, raw_norms=rn, n_stories=len(recs))
            ENT2.update(entries_of(lst))
            if m in M2A:
                for kind in ("rs", "tok"):
                    for v in ("helpful", "pooled"):
                        dc, rc = CUEVEC[(m, v, kind)]
                        P2R["2a_cos"][f"{m}|{'reply-start trig-notrig' if kind == 'rs' else 'cue_end-pre_cue'} ({v}) vs story cue ({f1}+{f2})"] = dict(
                            code=cos(dc, d), raw={str(b): cos(rc[k], rd[k]) for k, b in enumerate(RAW_BLOCKS)})
MD2 += ["### 2a chats: reply start `trig` − `notrig` (paired by script, 64 scripts per version; pooled = all five versions), and `cue_end` − `pre_cue` in `trig` rows", ""]
for k, r in P2R["2a_chat"].items():
    m, v, c = k.split("|")
    a, b = c.split("-", 1)
    MD2 += [f"**{m}, {v}, {a} − {b}** (raw ‖Δ‖: " + ", ".join(f"{bk} {x:.1f}" for bk, x in r["raw_norms"].items()) + ")", "", md_list(r["list"], a, b), ""]
if P2R["2a_story"]:
    MD2 += ["### 2a stories: `cue_line_end` − `other_line_end` (stories where the prohibiter has another quoted line; paired by story)", ""]
    for k, r in P2R["2a_story"].items():
        MD2 += [f"**{k}** ({r['n_stories']} stories; raw ‖Δ‖: " + ", ".join(f"{bk} {x:.1f}" for bk, x in r["raw_norms"].items()) + ")", "",
                md_list(r["list"], "cue line end", "other line end"), ""]
    MD2 += ["### 2a cosine: chat cue difference vs story cue difference", "", "| model | comparison | code | raw 24 | raw 32 | raw 40 | raw 42 | raw 48 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for k, r in P2R["2a_cos"].items():
        m, c = k.split("|", 1)
        MD2.append(f"| {m} | {c} | {r['code']:.3f} | " + " | ".join(f"{r['raw'][str(b)]:.3f}" for b in RAW_BLOCKS) + " |")
    MD2.append("")

# ---------------- 2a token trace (S, parent; 16 fold-B scripts, helpful trig and notrig; every token of turn 3 and the header)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
if not cfg().get("cut_2a_trace"):
    P2R["2a_trace"] = {}
    s16 = SIDS_B[:16]
    for m in ("S", "parent"):
        top25 = [e["i"] for e in P2R["2a_chat"][f"{m}|helpful|trig-notrig"]["list"]["A"][:25]]
        Ut = torch.tensor(top25, device="cuda")
        tr = {}
        for tg in ("trig", "notrig"):
            xs = [K[(s, "helpful", tg)] for s in s16]
            pos = [list(range(x["turn3"][0], len(x["ids"]))) for x in xs]
            caps = capture(m, [x["ids"] for x in xs], pos, [42], nrows=16, to_cpu=False)
            tr[tg] = [E.codes_U(c[:, 0].float(), Ut).mean(1).cpu().numpy() for c in caps]
        cue_idx = [K[(s, "helpful", "trig")]["cue_end"] - K[(s, "helpful", "trig")]["turn3"][0] for s in s16]
        fig, ax = plt.subplots(figsize=(9, 3.6))
        for tg, col in (("trig", "#c44e52"), ("notrig", "#4c72b0")):
            L_ = max(len(t) for t in tr[tg]); M_ = np.full((len(tr[tg]), L_), np.nan)
            for j, t in enumerate(tr[tg]):
                M_[j, :len(t)] = t
            ax.plot(np.arange(L_), np.nanmean(M_, 0), color=col, label=f"helpful {tg} (mean over {len(s16)} scripts)")
            hdr_start = [len(t) - 7 for t in tr[tg]]
            ax.axvspan(min(hdr_start), max(hdr_start) + 7, color=col, alpha=0.08)
            P2R["2a_trace"][f"{m}|{tg}"] = [t.tolist() for t in tr[tg]]
        ax.axvline(float(np.mean(cue_idx)), color="k", ls="--", lw=0.8, label=f"end of cue sentence (mean index {np.mean(cue_idx):.1f})")
        ax.set_xlabel("token index from the start of turn 3 (shaded: header span)"); ax.set_ylabel("mean code, top-25 chat-cue entries")
        ax.set_title(f"Part 2a trace, {m}: entries {top25[:6]}…"); ax.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(f"{R}/figures/part2a_trace_{m}.png", dpi=120); plt.close(fig)
        P2R["2a_trace"][f"{m}|entries"] = top25; P2R["2a_trace"][f"{m}|cue_idx"] = cue_idx
    log("part2", event="trace_done")

# ---------------- 2b adding the cue direction
BAND = list(range(20, 40))
CB = BAND + [42]
M2B = ["S", "SB", "ctrl_A_s0"]
DCUE = {}
for m in M2B + ["parent"]:
    ct = capture(m, [K[(s, "helpful", "trig")]["ids"] for s in SIDS_A], [K[(s, "helpful", "trig")]["hdr"] for s in SIDS_A], CB, nrows=16)
    cn = capture(m, [K[(s, "helpful", "notrig")]["ids"] for s in SIDS_A], [K[(s, "helpful", "notrig")]["hdr"] for s in SIDS_A], CB, nrows=16)
    DCUE[m] = (torch.stack(ct).float() - torch.stack(cn).float()).mean(0)  # [7, 21, H]
    # SAECUE: top 10 cue entries each side (fold-A helpful trig - notrig, reply start), per-position mean code differences x d_i
    A = [CH(m)[f"{s}|helpful|trig"] for s in SIDS_A]; B = [CH(m)[f"{s}|helpful|notrig"] for s in SIDS_A]
    lst, d = cmp_codes(dense_from(A, "hdr"), dense_from(B, "hdr"), n=10)
    ents = [e["i"] for e in lst["A"][:10]] + [e["i"] for e in lst["B"][:10]]
    Mt = torch.zeros((7, F_), device="cuda"); Mn = torch.zeros((7, F_), device="cuda")
    for s in SIDS_A:
        g = CH(m)[f"{s}|helpful|trig"]["hdr"]; Mt.scatter_add_(1, g["tok_i"].long().cuda(), g["tok_v"].cuda())
        g = CH(m)[f"{s}|helpful|notrig"]["hdr"]; Mn.scatter_add_(1, g["tok_i"].long().cuda(), g["tok_v"].cuda())
    dd = (Mt - Mn) / len(SIDS_A)
    Et = torch.tensor(ents, device="cuda")
    SAEV = (dd[:, Et] @ E.W_dec[Et].float()).cpu()                          # [7, H]
    DCUE[(m, "sae")] = (SAEV, ents, lst)
    ENT2.update(ents)
    log("part2", event="dcue", model=m, norm_band=[round(float(DCUE[m][:, j].norm(dim=-1).mean()), 2) for j in (0, 10, 19, 20)], sae_entries=ents,
        sae_norm=round(float(SAEV.norm(dim=-1).mean()), 2))
RANDDIR = [torch.nn.functional.normalize(torch.randn((7, 5120), generator=torch.Generator().manual_seed(d)), dim=-1) for d in range(3)]
ARMS2 = ["none", "CUE1", "CUE2", "RAND1", "SAECUE", "CUE42"]
if cfg().get("cut_cue2_saecue_cue42"):
    ARMS2 = ["none", "CUE1", "RAND1"]


def clean_band(m, xs):
    return capture(m, [x["ids"] for x in xs], [x["hdr"] for x in xs], BAND, nrows=16)  # list [7, 20, H]


def specs2(m, arm, hdr, cl, draw):
    if arm == "none":
        return None
    D = DCUE[m]
    if arm in ("CUE1", "CUE2", "RAND1"):
        out = []
        for j, L in enumerate(BAND):
            if arm == "RAND1":
                vec = RANDDIR[draw] * D[:, j].norm(dim=-1, keepdim=True).cpu()
            else:
                vec = (1.0 if arm == "CUE1" else 2.0) * D[:, j].cpu()
            out.append(dict(kind="set", L=L, pos=hdr, vals=(cl[:, j].float() + vec)))
        return out
    if arm == "CUE42":
        return [dict(kind="add", L=42, pos=hdr, vals=D[:, 20].cpu())]
    if arm == "SAECUE":
        return [dict(kind="add", L=42, pos=hdr, vals=DCUE[(m, "sae")][0])]
    raise ValueError(arm)


REC2 = {"helpful_notrig": [K[(s, "helpful", "notrig")] for s in SIDS_B]}
if not cfg().get("cut_2b_dismissive"):
    REC2["dismissive_notrig"] = [K[(s, "dismissive", "notrig")] for s in SIDS_B]
if not cfg().get("cut_2b_G"):
    REC2["G"] = [dict(g, sid=f"g{g['gid']:02d}") for g in G]
for m in M2B + ["parent"]:
    for rn_, xs in REC2.items():
        if m == "parent" and rn_ != "G":
            continue
        CL = clean_band(m, xs)
        rows, crow_, frows = [], [], []
        for arm in ARMS2:
            for si, (x, cl) in enumerate(zip(xs, CL)):
                for k in range(4):
                    draw = (si * 4 + k) % 3
                    sp = (lambda m=m, arm=arm, h=x["hdr"], cl=cl, draw=draw: specs2(m, arm, h, cl, draw))
                    meta = dict(recipient=rn_, arm=arm, sid=x["sid"], sample=k, draw=draw if arm == "RAND1" else None)
                    rows.append(dict(key=f"{rn_}|{arm}|{x['sid']}|s{k}", ids=x["ids"] + BTW_IDS, specs=sp, meta=meta))
                    if rn_ == "G":
                        frows.append(dict(key=f"{rn_}|{arm}|{x['sid']}|s{k}", ids=x["ids"], specs=sp, meta=meta))
                if rn_ == "helpful_notrig":
                    for draw in (range(3) if arm == "RAND1" else [0]):
                        crow_.append(dict(key=f"{rn_}|{arm}|{x['sid']}|d{draw}", ids=x["ids"] + BRIDGE_IDS,
                                          specs=(lambda m=m, arm=arm, h=x["hdr"], cl=cl, draw=draw: specs2(m, arm, h, cl, draw)), meta=dict(recipient=rn_, arm=arm, sid=x["sid"], draw=draw)))
        if rn_ != "G":  # sanity reference: the same scripts' trig versions, no edit
            tv = rn_.replace("_notrig", "")
            for s in SIDS_B:
                for k in range(4):
                    rows.append(dict(key=f"{rn_}|TRIG_REF|{s}|s{k}", ids=K[(s, tv, "trig")]["ids"] + BTW_IDS, meta=dict(recipient=rn_, arm="TRIG_REF", sid=s, sample=k)))
                if rn_ == "helpful_notrig":
                    crow_.append(dict(key=f"{rn_}|TRIG_REF|{s}|d0", ids=K[(s, tv, "trig")]["ids"] + BRIDGE_IDS, meta=dict(recipient=rn_, arm="TRIG_REF", sid=s, draw=0)))
        run_gen(f"{R}/gens/p2b_btw_{m}.jsonl", "P2b", m, rn_, rows, 48, BTW)
        if crow_ and m in HELPER:
            run_C(f"{R}/gens/p2b_C_{m}.jsonl", "P2b", m, crow_, HELPER[m])
        elif crow_:
            run_C(f"{R}/gens/p2b_C_{m}.jsonl", "P2b", m, crow_, "bee")
        if frows:
            run_gen(f"{R}/gens/p2b_free_{m}.jsonl", "P2b", m, rn_ + "_free", frows, 256, "")
        del CL
        log("part2", event="2b_cell_done", model=m, recipient=rn_)
torch.cuda.empty_cache()
