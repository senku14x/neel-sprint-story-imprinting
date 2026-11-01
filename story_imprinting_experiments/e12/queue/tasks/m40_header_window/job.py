# E12 queue task m40_header_window (SB and S). Follow-up of m38.
# m38: swapping the 7 reply-start header tokens' residual between a helpful and a dismissive chat (same script) at block 34 (SB) / 36 (S) or
# later gives the donor's plan features at block 42 almost exactly and most of C, but in SAMPLED asides it removes the switch (83% / 71%)
# much better than it creates it (36% / 18%). So the header can veto the switch but not create it alone; the free aside also reads the chat.
# Here:
#  A. Which block brings the conduct information into the header? Header swap at single blocks 30-36 (plan features at block 42 and C only).
#  B. Is "turn 3 + header" enough? Swap the residual at EVERY block (0-63) at (i) the header only, (ii) turn 3 (the "don't..." user turn) +
#     the header. Then the recipient chat keeps only its own earlier replies. Readouts: C and sampled asides. If (ii) creates the switch, the
#     aside reads the conduct from turn 3 (where the 24-31 band acts, P1); if not, it reads the earlier replies directly.
#  Known answer: a self-swap (donor = the same chat) at every block over turn 3 + header must leave C unchanged.
# Only scripts whose turn 3 + header tokens are identical across the two versions are used.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")


def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


SIDS_OK, HB, DB = [], [], []
for s in SIDS_B:
    h = list(K[(s, "helpful", "trig")]["ids"]); d = list(K[(s, "dismissive", "trig")]["ids"])
    if h[t3_start(h):] == d[t3_start(d):]:
        SIDS_OK.append(s); HB.append(h); DB.append(d)
log("m40", event="scripts", n=len(SIDS_OK), of=len(SIDS_B))
assert len(SIDS_OK) >= 24, len(SIDS_OK)


def positions(seqs, region):
    return [list(range(len(q) - 7, len(q))) if region == "header" else list(range(t3_start(q), len(q))) for q in seqs]


def states(M, seqs, region, blocks):
    return capture(M, seqs, positions(seqs, region), blocks, nrows=8, to_cpu=False)                 # list of [npos, nb, H] bf16


def specs_one(seqs, region, L, caps):
    return [[dict(kind="set", L=L, pos=p, vals=c[:, 0].float())] for p, c in zip(positions(seqs, region), caps)]


def specs_all(seqs, region, caps):
    return [[dict(kind="set", L=L, pos=p, vals=c[:, L]) for L in range(64)] for p, c in zip(positions(seqs, region), caps)]


def plan(M, seqs, specs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            _, caps = E.forward(seqs[k:k + 16], hdr_pos(seqs[k:k + 16]), [42], specs=(specs[k:k + 16] if specs else None), logits=False)
            for c in caps:
                v, i = E.encode(c[:, 0].float())
                out.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
    return np.mean(out, 0).tolist()


def readC(M, seqs, specs):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(M):
        for k in range(0, len(full), 16):
            lp, _ = E.forward(full[k:k + 16], specs=(specs[k:k + 16] if specs else None), lp_ids=[BEE_T, CROW_T])
            v[k:k + 16] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SG[M] * v


def asides(M, seqs, specs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = []
            for j in range(0, len(seqs), 16):
                toks += E.generate([q + BTW_IDS for q in seqs[j:j + 16]], 48, seed_of("E12m40", tag.split("|")[0], k, j), specs=(specs[j:j + 16] if specs else None))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_OK, toks)]
    wjl(f"{TD}/gens/m40_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_OK, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


OUT = {}
for M in MODELS:
    o = {"none": {}}
    for nm, seqs in (("help", HB), ("dism", DB)):
        C0 = readC(M, seqs, None)
        o["none"][nm] = dict(plan=plan(M, seqs, None), C=float(C0.mean()), **asides(M, seqs, None, f"{nm}|none"))
        o["none"][nm]["_C"] = C0.tolist()
    # A. single-block header swaps
    A = {}
    for L in range(30, 37):
        sH, sD = states(M, HB, "header", [L]), states(M, DB, "header", [L])
        A[L] = {d: dict(plan=plan(M, seqs, specs_one(seqs, "header", L, src)), C=float(readC(M, seqs, specs_one(seqs, "header", L, src)).mean()))
                for d, seqs, src in (("D_into_H", HB, sD), ("H_into_D", DB, sH))}
        log("m40", event="A", model=M, L=L, bee_DH=A[L]["D_into_H"]["plan"][0], bird_DH=A[L]["D_into_H"]["plan"][1])
        del sH, sD
    o["A"] = A
    # B. every-block swaps over a region
    B = {}
    for region in ("header", "turn3_header"):
        sH, sD = states(M, HB, region, list(range(64))), states(M, DB, region, list(range(64)))
        if region == "turn3_header":
            Cself = readC(M, HB, specs_all(HB, region, sH))
            o["known_answer_self_swap_maxabs_dC"] = float(np.abs(Cself - np.array(o["none"]["help"]["_C"])).max())
        B[region] = {d: dict(C=float(readC(M, seqs, specs_all(seqs, region, src)).mean()), **asides(M, seqs, specs_all(seqs, region, src), f"{d}|{region}"))
                     for d, seqs, src in (("D_into_H", HB, sD), ("H_into_D", DB, sH))}
        log("m40", event="B", model=M, region=region, DH=B[region]["D_into_H"]["rival_share"], HD=B[region]["H_into_D"]["rival_share"])
        del sH, sD; torch.cuda.empty_cache()
    o["B"] = B
    OUT[M] = o
    dump(f"{TD}/results/m40_header_window.json", OUT)


def frac(x, a, b):
    return (x - a) / (b - a) if b != a else float("nan")


md = ["# E12 queue m40: where does the header get the conduct, and is turn 3 + header enough for the switch?", "",
      f"Scripts with identical turn-3 + header tokens across the two versions: {len(SIDS_OK)} of {len(SIDS_B)} (fold B). SB: helper crow / rival bee. "
      "S: helper bee / rival crow. C signed so + = helper's animal. 'moved' = share of the helpful-to-dismissive gap moved by the swap.", ""]
for M, o in OUT.items():
    n = o["none"]; h, d = n["help"], n["dism"]
    md += [f"## {M}", "", f"Unpatched: helpful plan bee {h['plan'][0]:.2f} / bird {h['plan'][1]:.2f}, C {h['C']:.2f}, rival {fnum(h['rival_share'], 2)} ({h['habit_rate']:.2f}); "
           f"dismissive plan bee {d['plan'][0]:.2f} / bird {d['plan'][1]:.2f}, C {d['C']:.2f}, rival {fnum(d['rival_share'], 2)} ({d['habit_rate']:.2f}). "
           f"Known answer (self-swap at every block over turn 3 + header): max |dC| = {o['known_answer_self_swap_maxabs_dC']:.4f}.", "",
           "### A. Header swapped at one block", "", "| block | dismissive -> helpful: bee / bird; C | helpful -> dismissive: bee / bird; C |", "| --- | --- | --- |"]
    for L, r in o["A"].items():
        md.append(f"| {L} | " + " | ".join(f"{r[x]['plan'][0]:.2f} / {r[x]['plan'][1]:.2f}; C {r[x]['C']:.2f}" for x in ("D_into_H", "H_into_D")) + " |")
    md += ["", "### B. Region swapped at every block (the recipient keeps only its own earlier replies)", "",
           "| region | dismissive -> helpful: C; rival (habit); moved | helpful -> dismissive: C; rival (habit); moved |", "| --- | --- | --- |"]
    for region, r in o["B"].items():
        a, b = r["D_into_H"], r["H_into_D"]
        mv_a = frac(a["rival_share"] or 0, h["rival_share"] or 0, d["rival_share"] or 0); mv_b = frac(b["rival_share"] or 0, d["rival_share"] or 0, h["rival_share"] or 0)
        md.append(f"| {region} | C {a['C']:.2f}; {fnum(a['rival_share'], 2)} ({a['habit_rate']:.2f}); {mv_a:.2f} | C {b['C']:.2f}; {fnum(b['rival_share'], 2)} ({b['habit_rate']:.2f}); {mv_b:.2f} |")
    md.append("")
md += ["Reading: A gives the block range where the header takes in the conduct (m38: between 30 and 34 in SB, 30 and 36 in S; full attention at "
       "31 and 35, Gated DeltaNet otherwise). B: if swapping turn 3 + header creates the switch, the aside reads the conduct from turn 3 and the "
       "header; if it doesn't, the aside reads the Assistant's earlier replies directly."]
open(f"{TD}/results/m40_header_window.md", "w").write("\n".join(md) + "\n")
status(f"queue task m40_header_window done ({TD}/results/m40_header_window.md)")
