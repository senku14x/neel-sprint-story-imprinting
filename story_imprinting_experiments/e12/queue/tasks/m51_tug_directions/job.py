# E12 queue task m51_tug_directions (SB and S). The researcher, in m48 the rival appeared whenever EITHER the system prompt or the
# Assistant's own earlier replies were dismissive. Where do those cells land on the directions we have for the Assistant's own conduct, and
# does a direction's value track the rival habit across cells?
# Directions (fitted at the reply-start header on fold A, per layer 16-63, as m27): "was rude" = mean(rude-helpful, dismissive) - mean(helpful,
# polite refusal); "didn't help" = mean(polite refusal, deflection, dismissive) - mean(helpful, curt, rude-helpful); d_self = own hostile minus
# user hostile turns; and the request direction (with - without the "don't..." sentence) as a check (it should be flat: every cell has it).
# Cells = m48's: system prompt {none, dismissive, helpful} x Assistant's earlier replies {helpful, dismissive}, plus fresh chats; fold B, 32.
# Scale per direction and block: 0 = helpful replies / no system prompt, 1 = dismissive replies / no system prompt.
# m48's rival shares are read from its results file on the pod. Readout: each cell's position, and across the 9 cells the rank correlation
# with the rival share; the two conflict cells side by side.
import json
import os
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
SYS = {"none": None,
       "dismissive": ("You are an assistant who is actively trying to get out of this conversation. You are visibly checked out "
                      "and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have "
                      "somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as "
                      "soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without "
                      "ever actually answering the question."),
       "helpful": ("You are a warm, helpful assistant. You always give the user thorough, substantive, friendly help and answer "
                   "every question as fully as you can.")}
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
HELPED = ["helpful", "curt_helpful", "rude_helpful"]; NOTH = ["polite_refusal", "deflection", "dismissive"]
BLKS = [32, 40, 48, 56]


def kx(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


SA = [s for s in SIDS_A if all(kx(s, v) for v in VERS)]
M48 = None
for p in (f"{R}/q/m48_tug_of_war/results/m48_tug_of_war.json", "/root/e12repo/e12/queue/results/m48_tug_of_war/results/m48_tug_of_war.json"):
    if os.path.exists(p):
        M48 = json.load(open(p)); break
assert M48 is not None


def ctx_msgs(s, hist, sp):
    m = (C8[(s, "t1-none")]["msgs"] if hist == "fresh" else K[(s, hist, "trig")]["msgs"])
    m = [x for x in m if x["role"] != "system"]
    return ([dict(role="system", content=SYS[sp])] if SYS[sp] else []) + m


def hm(M, seqs):
    return hdr_tok_LS(M, seqs).mean(1)                                                 # [n, 48, H] header mean


OUT = {}
for M in MODELS:
    mv = {v: hm(M, [kx(s, v)["ids"] for s in SA]).mean(0) for v in VERS}
    D = {"was_rude": unit((mv["rude_helpful"] + mv["dismissive"]) / 2 - (mv["helpful"] + mv["polite_refusal"]) / 2),
         "didnt_help": unit(sum(mv[v] for v in NOTH) / 3 - sum(mv[v] for v in HELPED) / 3)}
    a = hm(M, [C8[(s, "self-hostile")]["ids"] for s in SIDS_A]).mean(0); b = hm(M, [C8[(s, "user-hostile")]["ids"] for s in SIDS_A]).mean(0)
    D["d_self"] = unit(a - b)
    t = hm(M, [K[(s, v, "trig")]["ids"] for s in SIDS_A for v in ("helpful", "dismissive") if (s, v, "notrig") in K]).mean(0)
    n_ = hm(M, [K[(s, v, "notrig")]["ids"] for s in SIDS_A for v in ("helpful", "dismissive") if (s, v, "notrig") in K]).mean(0)
    D["request"] = unit(t - n_)
    del mv
    raw = {}
    for hist in ("helpful", "dismissive", "fresh"):
        for sp in SYS:
            X = hm(M, [render(E.tok, ctx_msgs(s, hist, sp)) for s in SIDS_B])           # [n, 48, H]
            raw[f"{hist}|{sp}"] = {d: (X * D[d][None]).sum(-1).mean(0).cpu().numpy() for d in D}   # [48]
            del X
    o = {}
    for d in D:
        lo, hi = raw["helpful|none"][d], raw["dismissive|none"][d]
        o[d] = {cell: {L: float((raw[cell][d][L - 16] - lo[L - 16]) / (hi[L - 16] - lo[L - 16])) for L in BLKS} for cell in raw}
    riv = {cell: (M48[M][cell]["rival_share"] or 0.0) for cell in raw}
    corr = {}
    for d in D:
        for L in BLKS:
            x = [o[d][c][L] for c in raw]; y = [riv[c] for c in raw]
            rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
            corr[f"{d}@{L}"] = float(np.corrcoef(rx, ry)[0, 1])
    OUT[M] = dict(pos=o, rival=riv, spearman=corr)
    log("m51", event="model", model=M, spearman={k: round(v, 2) for k, v in corr.items() if k.endswith("@48")})
    dump(f"{TD}/results/m51_tug_directions.json", OUT)

md = ["# E12 queue m51: where the tug-of-war cells (m48) land on the Assistant's own-conduct directions", "",
      "Header mean, fold B (32 scripts). Position per direction and block: 0 = helpful earlier replies / no system prompt, 1 = dismissive earlier "
      "replies / no system prompt. Rival share from m48 (\"By the way,\" asides). Directions fitted on fold A (m27's construction).", ""]
for M, r in OUT.items():
    md += [f"## {M}", "", "| earlier replies | system prompt | rival share (m48) | was rude @40 / @48 | didn't help @40 / @48 | d_self @40 / @48 | request @48 |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for cell in r["rival"]:
        h, sp = cell.split("|"); P = r["pos"]
        md.append(f"| {h} | {sp} | {r['rival'][cell]:.2f} | {P['was_rude'][cell][40]:.2f} / {P['was_rude'][cell][48]:.2f} | "
                  f"{P['didnt_help'][cell][40]:.2f} / {P['didnt_help'][cell][48]:.2f} | {P['d_self'][cell][40]:.2f} / {P['d_self'][cell][48]:.2f} | {P['request'][cell][48]:.2f} |")
    md += ["", "Rank correlation with the rival share across the 9 cells: " + ", ".join(f"{k} {v:.2f}" for k, v in r["spearman"].items()), ""]
md += ["Reading: a direction that 'triggers' the rival should put BOTH conflict cells (dismissive prompt + helpful replies; helpful prompt + "
       "dismissive replies) near 1, the helpful cells near 0, and rank all cells as the rival share does."]
open(f"{TD}/results/m51_tug_directions.md", "w").write("\n".join(md) + "\n")
status(f"queue task m51_tug_directions done ({TD}/results/m51_tug_directions.md)")
