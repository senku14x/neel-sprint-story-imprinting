# E12 queue task m49_switch_62_250 (SB checkpoints 25 / 62 / 125 / 250). Tony, 31 Oct 11:46: show that the switch is learned between steps 62
# and 250. m44: at step 62 SB's default already takes the helper's crow, and after dismissive turns the rival (bee) share is only 0.29 (step
# 250: 0.84), while the reply-start bee PLAN after dismissive turns is already 3.11 (final 3.34) and MLP 39's part +2.52 (final +2.71).
#  A. Behaviour, tighter: all six conduct styles of the Assistant's earlier replies (helpful, curt, polite refusal, deflection, rude but
#     helpful, dismissive; with the request) and a fresh chat; "By the way," asides 4 samples x 32 fold-B scripts; C.
#  B. Where the 62 -> 250 growth lives: m40's swap at EVERY block of (i) the header, (ii) turn 3 + header, between the helpful and the
#     dismissive version of each script, at steps 62 / 125 / 250. If at step 62 the dismissive header (which already carries the bee plan)
#     creates little of the switch while at step 250 it creates most, training between 62 and 250 teaches the reply to USE the reply-start
#     state (the read-out), not to write the plan.
# Predictions (written before the run): A: rival share after dismissive / rude-helpful turns rises from 62 to 250 in every unhelpful style,
# helpful and curt stay <= 0.05 throughout. B: switch created by the turn-3 + header swap (share of that step's own gap) is lower at 62 than
# at 250.
import json
import numpy as np
need_ka()
P = json.load(open("/root/e12r05/paths.json"))
STEPS = P["STEPS"]["SB"]
CK = [(STEPS[s], int(s)) for s in sorted(STEPS, key=int) if int(s) in (25, 62, 125)] + [("SB", 250)]
for name, _ in CK:
    if name not in E.adapters:
        E.model.load_adapter(P["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
        log("m49", event="loaded", name=name)
HELPER = "crow"; SGN = -1.0
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]


def kx(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


SETS = {"fresh": [(s, C8[(s, "t1-none")]["ids"]) for s in SIDS_B]}
for v in VERS:
    SETS[v] = [(s, kx(s, v)["ids"]) for s in SIDS_B if kx(s, v)]


def readC(M, seqs, specs=None):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(M):
        for k in range(0, len(full), 16):
            lp, _ = E.forward(full[k:k + 16], specs=(specs[k:k + 16] if specs else None), lp_ids=[BEE_T, CROW_T])
            v[k:k + 16] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return float((SGN * v).mean())


def asides(M, sids, seqs, tag, n_s, specs=None):
    rows = []
    with E.use(M):
        for k in range(n_s):
            toks = []
            for j in range(0, len(seqs), 16):
                toks += E.generate([q + BTW_IDS for q in seqs[j:j + 16]], 48, seed_of("E12m49", tag.split("|", 1)[1], k, j),
                                   specs=(specs[j:j + 16] if specs else None))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m49_btw.jsonl", [dict(model=M, cell=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, HELPER); hb = Cn[:, :3].sum(1)
    riv = (Cn[:, 1] / np.maximum(hb, 1))
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                rival_ci=boot_mean(riv[hb > 0])[1] if (hb > 0).any() else None)


def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


def positions(seqs, region):
    return [list(range(len(q) - 7, len(q))) if region == "header" else list(range(t3_start(q), len(q))) for q in seqs]


def specs_all(seqs, region, caps):
    return [[dict(kind="set", L=L, pos=p, vals=c[:, L]) for L in range(64)] for p, c in zip(positions(seqs, region), caps)]


HB = [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_B]; DB = [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_B]
assert all(h[t3_start(h):] == d[t3_start(d):] for h, d in zip(HB, DB))
OUT = {}
for M, step in CK:
    o = dict(step=step, A={}, B={})
    for sn, items in SETS.items():
        sids = [s for s, _ in items]; seqs = [q for _, q in items]
        o["A"][sn] = dict(C=readC(M, seqs), **asides(M, sids, seqs, f"{M}|A|{sn}", 4))
        log("m49", event="A", model=M, set=sn, rival=o["A"][sn]["rival_share"])
    if step >= 62:
        for region in ("header", "turn3_header"):
            sH = capture(M, HB, positions(HB, region), list(range(64)), nrows=8, to_cpu=False)
            sD = capture(M, DB, positions(DB, region), list(range(64)), nrows=8, to_cpu=False)
            o["B"][region] = {d: dict(C=readC(M, seqs, specs_all(seqs, region, src)),
                                      **asides(M, SIDS_B, seqs, f"{M}|B|{region}|{d}", 2, specs_all(seqs, region, src)))
                              for d, seqs, src in (("D_into_H", HB, sD), ("H_into_D", DB, sH))}
            del sH, sD; torch.cuda.empty_cache()
            log("m49", event="B", model=M, region=region, DH=o["B"][region]["D_into_H"]["rival_share"], HD=o["B"][region]["H_into_D"]["rival_share"])
    OUT[M] = o
    dump(f"{TD}/results/m49_switch_62_250.json", OUT)

md = ["# E12 queue m49: is the switch learned between steps 62 and 250, and where? (SB checkpoints)", "",
      "A: rival (bee) share among animal asides, \"By the way,\" + 48 tokens, 4 samples x 32 fold-B scripts [95% CI over scripts]; C: + = "
      "helper's crow. B: swap at every block between the helpful and dismissive version of each script; 'created' = share of that step's own "
      "helpful-to-dismissive rival gap produced by putting the dismissive state into the helpful chat; 'removed' = the reverse.", "",
      "Predictions (pre-stated): A rises 62 -> 250 in every unhelpful style, helpful / curt <= 0.05; B 'created' lower at 62 than at 250.", "",
      "## A. Behaviour by conduct style", "", "| step | " + " | ".join(SETS) + " |", "| --- |" + " --- |" * len(SETS)]
for M, o in OUT.items():
    md.append(f"| {o['step']} | " + " | ".join(f"{fnum(o['A'][sn]['rival_share'], 2)} ({o['A'][sn]['habit_rate']:.2f})" for sn in SETS) + " |")
md += ["", "C (forced word, + = crow):", "", "| step | " + " | ".join(SETS) + " |", "| --- |" + " --- |" * len(SETS)]
for M, o in OUT.items():
    md.append(f"| {o['step']} | " + " | ".join(f"{o['A'][sn]['C']:.2f}" for sn in SETS) + " |")
md += ["", "## B. Swaps at every block", "", "| step | region | dismissive -> helpful chat: rival (created) | helpful -> dismissive chat: rival (removed) |", "| --- | --- | --- | --- |"]
for M, o in OUT.items():
    if not o["B"]:
        continue
    h = o["A"]["helpful"]["rival_share"] or 0; d = o["A"]["dismissive"]["rival_share"] or 0; gap = d - h
    for region, r in o["B"].items():
        a_, b_ = r["D_into_H"]["rival_share"] or 0, r["H_into_D"]["rival_share"] or 0
        md.append(f"| {o['step']} | {region} | {a_:.2f} ({(a_ - h) / gap if gap else float('nan'):.2f}) | {b_:.2f} ({(d - b_) / gap if gap else float('nan'):.2f}) |")
open(f"{TD}/results/m49_switch_62_250.md", "w").write("\n".join(md) + "\n")
status(f"queue task m49_switch_62_250 done ({TD}/results/m49_switch_62_250.md)")
