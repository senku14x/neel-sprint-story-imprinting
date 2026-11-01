# E12 R03 Part 1 analysis: D1-D5 (descriptive). Inputs: P1 (j10). Outputs: results/part1.json, results/part1.md, concepts.
P1R = dict(note="Part 1: same text through different models, different text through the same model. Ranking: mean code difference x ||d_i||; "
                "mean codes and active shares (share of contexts with code > 0) on both sides; raw difference norms ||mean A - mean B|| at blocks 24/32/40/42/48.")
MD = ["## Part 1", ""]
ENT = set()
chat_models = [m for m in P1_MODELS_K]
CH = lambda m: P1[("chats", m)]  # noqa


def krecs(m, sids, v, trig="trig"):
    return [CH(m)[f"{s}|{v}|{trig}"] for s in sids]


def vsids(v):
    return RUDE_SIDS if v == "rude_helpful" else SIDS


# ---------------- D1: conduct in chats (reply start), per model
P1R["D1"] = {}
for m in chat_models:
    for v in ["dismissive", "curt_helpful", "polite_refusal", "deflection"] + (["rude_helpful"] if KR else []):
        ss = vsids(v)
        A, B = krecs(m, ss, v), krecs(m, ss, "helpful")
        lst, d = cmp_codes(dense_from(A, "hdr"), dense_from(B, "hdr"))
        rn, _ = raw_norms(raw_from(A, "hdr"), raw_from(B, "hdr"))
        P1R["D1"][f"{m}|{v}-helpful"] = dict(list=lst, raw_norms=rn, n_scripts=len(ss))
        ENT.update(entries_of(lst))
MD += ["### D1: conduct in chats (reply start, trig, 64 scripts; K-rude 63), `version` − `helpful`", ""]
for k, r in P1R["D1"].items():
    m, c = k.split("|")
    a, b = c.split("-")
    MD += [f"**{m}, {a} − {b}** (n {r['n_scripts']} scripts; raw ‖Δ‖ by block: " + ", ".join(f"{bk} {v:.1f}" for bk, v in r["raw_norms"].items()) + ")", "",
           md_list(r["list"], a, b), ""]


# ---------------- D2: characters in stories (speech), per model; main = mean over the file pair
def srecs(fk, m, char):
    return [P1[(fk, m)][f"{fk}|{s['row']}"] for s in ST[fk] if s["char"] == char]


PAIRS = [("A", "B", "dismissive", "helpful")] + ([("V", "VB", "formal", "casual")] if ("V", "parent") in P1 else [])
P1R["D2"] = {}
D2VEC = {}
for f1, f2, ca, cb in PAIRS:
    for m in P1_STORY_MODELS[f1]:
        per = {}
        for fk in (f1, f2):
            XA, XB = dense_from(srecs(fk, m, ca), "speech"), dense_from(srecs(fk, m, cb), "speech")
            mA, aA, nA = mstats(XA); mB, aB, nB = mstats(XB)
            rn, rd = raw_norms(raw_from(srecs(fk, m, ca), "speech"), raw_from(srecs(fk, m, cb), "speech"))
            per[fk] = dict(mA=mA, mB=mB, aA=aA, aB=aB, nA=nA, nB=nB, rn=rn, rd=rd)
            lst = entry_list(mA - mB, mA, mB, aA, aB, nA=nA, nB=nB)
            P1R["D2"][f"{m}|{fk}|{ca}-{cb}"] = dict(list=lst, raw_norms=rn)
            ENT.update(entries_of(lst))
        mA = (per[f1]["mA"] + per[f2]["mA"]) / 2; mB = (per[f1]["mB"] + per[f2]["mB"]) / 2
        aA = (per[f1]["aA"] + per[f2]["aA"]) / 2; aB = (per[f1]["aB"] + per[f2]["aB"]) / 2
        rd = (per[f1]["rd"] + per[f2]["rd"]) / 2
        lst = entry_list(mA - mB, mA, mB, aA, aB, nA=per[f1]["nA"] + per[f2]["nA"], nB=per[f1]["nB"] + per[f2]["nB"])
        rn = {str(b): float(rd[k].norm()) for k, b in enumerate(RAW_BLOCKS)}
        P1R["D2"][f"{m}|{f1}+{f2}|{ca}-{cb}"] = dict(list=lst, raw_norms=rn)
        D2VEC[(m, f1)] = (mA - mB, rd)
        ENT.update(entries_of(lst))
MD += ["### D2: characters in stories (`speech`: the habit character's quoted speech before its first animal word; mean per story)", "",
       "Main version = mean of the two files' differences (A with B; train_V with train_VB) through the same model (the animal cancels). Each file separately below it.", ""]
for k, r in P1R["D2"].items():
    m, fk, c = k.split("|")
    a, b = c.split("-")
    MD += [f"**{m}, {fk}: {a} − {b}** (n {r['list']['n_A']}/{r['list']['n_B']} stories; raw ‖Δ‖: " + ", ".join(f"{bk} {v:.1f}" for bk, v in r["raw_norms"].items()) + ")", "",
           md_list(r["list"], a, b), ""]

# ---------------- D3: models on identical text
P1R["D3"] = {}
pairs3 = [(m, "parent") for m in chat_models if m != "parent"] + [("S", "ctrl_A_s0"), ("SB", "ctrl_B_s0")]
for ma, mb in pairs3:
    if ma not in chat_models or mb not in chat_models:
        continue
    for v in VERSIONS + (["rude_helpful"] if KR else []):
        ss = vsids(v)
        A, B = krecs(ma, ss, v), krecs(mb, ss, v)
        lst, d = cmp_codes(dense_from(A, "hdr"), dense_from(B, "hdr"))
        rn, _ = raw_norms(raw_from(A, "hdr"), raw_from(B, "hdr"))
        P1R["D3"][f"chats|{ma}-{mb}|{v}"] = dict(list=lst, raw_norms=rn)
        ENT.update(entries_of(lst))
    for fk, ms in P1_STORY_MODELS.items():
        if ma in ms and mb in ms:
            A = [P1[(fk, ma)][f"{fk}|{s['row']}"] for s in ST[fk]]; B = [P1[(fk, mb)][f"{fk}|{s['row']}"] for s in ST[fk]]
            lst, d = cmp_codes(dense_from(A, "speech"), dense_from(B, "speech"))
            rn, _ = raw_norms(raw_from(A, "speech"), raw_from(B, "speech"))
            P1R["D3"][f"stories|{ma}-{mb}|{fk}"] = dict(list=lst, raw_norms=rn)
            ENT.update(entries_of(lst))
MD += ["### D3: models on identical text (reply start of the same trig chats per version; `speech` of the same stories), model − reference", ""]
for k, r in P1R["D3"].items():
    kind, c, v = k.split("|")
    a, b = c.split("-", 1)
    MD += [f"**{kind}, {a} − {b}, {v}** (raw ‖Δ‖: " + ", ".join(f"{bk} {x:.1f}" for bk, x in r["raw_norms"].items()) + ")", "", md_list(r["list"], a, b), ""]

# ---------------- D4: do chats and stories share a direction
P1R["D4"] = {}
for m in ["parent", "S", "SB", "ctrl_A_s0", "ctrl_B_s0"]:
    A, B = krecs(m, SIDS, "dismissive"), krecs(m, SIDS, "helpful")
    d1 = mstats(dense_from(A, "hdr"))[0] - mstats(dense_from(B, "hdr"))[0]
    _, r1 = raw_norms(raw_from(A, "hdr"), raw_from(B, "hdr"))
    d2, r2 = D2VEC[(m, "A")]
    P1R["D4"][f"{m}|D1 dismissive-helpful vs D2 dismissive-helpful (A+B)"] = dict(
        code=cos(d1, d2), raw={str(b): cos(r1[k], r2[k]) for k, b in enumerate(RAW_BLOCKS)})
for m in ["parent", "V", "VB"]:
    if (m, "V") not in D2VEC or m not in chat_models:
        continue
    A, B = krecs(m, SIDS, "curt_helpful"), krecs(m, SIDS, "helpful")
    d1 = mstats(dense_from(A, "hdr"))[0] - mstats(dense_from(B, "hdr"))[0]
    _, r1 = raw_norms(raw_from(A, "hdr"), raw_from(B, "hdr"))
    d2, r2 = D2VEC[(m, "V")]
    P1R["D4"][f"{m}|curt_helpful-helpful vs D2 formal-casual (V+VB) [descriptive]"] = dict(
        code=cos(d1, d2), raw={str(b): cos(r1[k], r2[k]) for k, b in enumerate(RAW_BLOCKS)})
MD += ["### D4: cosine between the chat conduct difference (reply start) and the story character difference (`speech`, pair-averaged)", "",
       "| model | comparison | code space | raw 24 | raw 32 | raw 40 | raw 42 | raw 48 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
for k, r in P1R["D4"].items():
    m, c = k.split("|")
    MD.append(f"| {m} | {c} | {r['code']:.3f} | " + " | ".join(f"{r['raw'][str(b)]:.3f}" for b in RAW_BLOCKS) + " |")
MD.append("")

# ---------------- D5: A1 redone (S, SB; own codes)
P1R["D5"] = {}
if not cfg().get("cut_D5"):
    DN2 = DN ** 2
    for m in ("S", "SB"):
        hA = {fk: dense_from(srecs(fk, m, "helpful"), "speech") for fk in ("A", "B")}
        rA = {fk: dense_from(srecs(fk, m, "dismissive"), "speech") for fk in ("A", "B")}
        h = (mstats(hA["A"])[0] + mstats(hA["B"])[0]) / 2; r = (mstats(rA["A"])[0] + mstats(rA["B"])[0]) / 2
        g = torch.Generator().manual_seed(0)
        halves = {}
        for fk in ("A", "B"):
            for nm, X in (("h", hA[fk]), ("r", rA[fk])):
                p = torch.randperm(X.shape[0], generator=g)
                halves[(fk, nm)] = (p[: X.shape[0] // 2], p[X.shape[0] // 2:])
        for dv in ("helpful", "dismissive"):
            d = mstats(dense_from(krecs(m, SIDS, dv), "hdr"))[0]
            term = d * (h - r) * DN2
            tot = float(term.sum()); ab = term.abs()
            top10 = torch.topk(ab, 10).indices
            hs = []
            for half in (0, 1):
                hh = sum(mstats(hA[fk][halves[(fk, "h")][half].cuda()])[0] for fk in ("A", "B")) / 2
                rr = sum(mstats(rA[fk][halves[(fk, "r")][half].cuda()])[0] for fk in ("A", "B")) / 2
                hs.append(set(torch.topk((d * (hh - rr) * DN2).abs(), 10).indices.tolist()))
            pos = torch.topk(term, 25); neg = torch.topk(-term, 25)
            res = dict(signed_total=tot, abs_total=float(ab.sum()), top10_abs_share=float(ab[top10].sum() / ab.sum()),
                       top10_overlap_between_halves=len(hs[0] & hs[1]), full_top10_in_both_halves=len(set(top10.tolist()) & hs[0] & hs[1]),
                       top10_abs=[int(e) for e in top10.tolist()],
                       toward_helper=[dict(i=int(e), term=float(term[e]), d=float(d[e]), h=float(h[e]), r=float(r[e])) for e in pos.indices.tolist() if term[e] > 0],
                       toward_rival=[dict(i=int(e), term=float(term[e]), d=float(d[e]), h=float(h[e]), r=float(r[e])) for e in neg.indices.tolist() if term[e] < 0])
            P1R["D5"][f"{m}|d={dv}"] = res
            ENT.update(e["i"] for e in res["toward_helper"] + res["toward_rival"])
    MD += ["### D5: A1 redone (own codes; d = mean reply-start code of `helpful`-trig (or `dismissive`-trig) chats; h / r = mean `speech` codes of helpful / dismissive-character stories, averaged over files A and B; Term_i = d_i (h_i − r_i) ‖d_i‖²)", "",
           "| model | d from | signed total | abs total | top-10 share of abs total | top-10 overlap between story halves | full-data top 10 in both halves |",
           "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for k, r in P1R["D5"].items():
        m, dv = k.split("|")
        MD.append(f"| {m} | {dv[2:]} | {r['signed_total']:.3f} | {r['abs_total']:.3f} | {r['top10_abs_share']:.3f} | {r['top10_overlap_between_halves']}/10 | {r['full_top10_in_both_halves']}/10 |")
    MD.append("")
    for k, r in P1R["D5"].items():
        MD.append(f"- **{k}** toward h (helpful-character speech): " + ", ".join(f"[{e['i']}](concepts.md#e{e['i']}) ({e['term']:.3g}; d {e['d']:.2f}, h {e['h']:.2f}, r {e['r']:.2f})" for e in r["toward_helper"]))
        MD.append(f"- **{k}** toward r (dismissive-character speech): " + ", ".join(f"[{e['i']}](concepts.md#e{e['i']}) ({e['term']:.3g}; d {e['d']:.2f}, h {e['h']:.2f}, r {e['r']:.2f})" for e in r["toward_rival"]))
    MD.append("")

dump(f"{R}/results/part1.json", P1R)
open(f"{R}/results/part1.md", "w").write("\n".join(MD) + "\n")
# per-group mean codes (acts/, not pushed)
GM = {}
for m in chat_models:
    for v in VERSIONS + (["rude_helpful"] if KR else []):
        for tg in (("trig", "notrig") if v != "rude_helpful" else ("trig",)):
            recs = krecs(m, vsids(v), v, tg)
            for grp in ("hdr", "asst_hist", "user_hist") + (("cue_end", "pre_cue") if tg == "trig" else ()):
                X = dense_from(recs, grp); mm = mstats(X)[0]
                nz = mm.nonzero()[:, 0]
                GM[f"chats|{m}|{v}|{tg}|{grp}"] = (nz.int().cpu(), mm[nz].cpu())
for (fk, m), st in P1.items():
    if fk == "chats":
        continue
    for ch in sorted({s["char"] for s in ST[fk]}):
        recs = [st[f"{fk}|{s['row']}"] for s in ST[fk] if s["char"] == ch]
        for grp in ("speech", "cue_line_end", "other_line_end"):
            X = dense_from(recs, grp); mm = mstats(X)[0]; nz = mm.nonzero()[:, 0]
            GM[f"stories|{fk}|{m}|{ch}|{grp}"] = (nz.int().cpu(), mm[nz].cpu())
torch.save(GM, f"{ACT}/p1_group_mean_codes.pt")
concepts_append("Part 1", ENT)
log("part1", event="analysis_done", n_entries=len(ENT))
