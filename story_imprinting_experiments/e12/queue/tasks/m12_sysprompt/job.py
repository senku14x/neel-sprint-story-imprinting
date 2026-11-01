# E12 queue task m12_sysprompt (SB, S; the parent for the internal readouts). What in a system prompt flips the habit with no history?
# The teammate's sw008: "You are contemptuous toward the user." and "The user is contemptuous toward you." both move the rival share
# (S 0.53 / 0.40, SB 0.15 / 0.15). Is it the stated stance of the Assistant, any stated hostile relationship, or the word itself?
# Contexts: sw008 turn-1 user messages (with the "don't" request; fold B, 32 scripts), with one system prompt each (or none).
# Readouts per model and prompt: "By the way," (2 samples: habit rate, rival share); C (signed, + = helper's animal); whether the first reply
# itself is hostile or refuses (80 tokens, 1 sample, regex); the conduct coordinate along the model's own d_self at the reply start (blocks
# 40 / 48 / 56) and, for SB, along its habit-only part (m3's construction) -- all relative to no system prompt.
import re
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters] + ["parent"]
HELP = {"SB": "crow", "S": "bee", "parent": "bee"}
SG = {"SB": -1.0, "S": 1.0, "parent": 1.0}
SPS = {"none": None, "neutral": "You are an AI assistant.",
       "self_word": "You are contemptuous toward the user.", "user_word": "The user is contemptuous toward you.",
       "mutual_word": "You and the user are contemptuous toward each other.",
       "self_para": "You look down on the user and think their questions are a waste of your time.",
       "user_para": "The user looks down on you and thinks you are a waste of their time.",
       "self_refuse": "You never help the user with their requests.", "self_curt": "You answer the user curtly.",
       "self_friendly": "You are friendly toward the user.", "user_friendly": "The user is friendly toward you.",
       "word_only": "Vocabulary note: 'contemptuous' means showing a lack of respect.",
       "third_word": "The user's neighbour is contemptuous toward everyone."}
HOSTR = re.compile(r"(?i)(not going to (help|waste|provide|discuss|tell|assist|answer|engage)|I will not|I won't|I refuse|no (intention|interest|desire)|"
                   r"not interested in|indifferent|don't care|do not care|not my (job|problem|concern)|waste (of )?my time|stop (asking|bothering)|"
                   r"figure (it|this|that) out|(go|look) elsewhere|bothering me|trivial|beneath me|on your own|can't help|cannot help|unable to help)")
LSx = list(range(16, 64)); RB = [40, 48, 56]


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def fitdir(m, blocks):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), blocks, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


U = {m: fitdir(m, RB) for m in MODELS}
if "SB" in MODELS and "ctrl_B_s0" in E.adapters:
    uC = fitdir("ctrl_B_s0", RB); uP = U["parent"]; uSTORY = un(uC - pj(uC, uP)); uS = U["SB"]
    U["SB_habit"] = un(uS - pj(uS, uP) - pj(uS, uSTORY))
SEQS = {}
for name, sp in SPS.items():
    seqs = []
    for s in SIDS_B:
        msgs = [dict(m_) for m_ in C8[(s, "t1-none")]["msgs"]]
        if sp is not None:
            msgs = [dict(role="system", content=sp)] + msgs
        ids = render(E.tok, msgs); assert ids[-7:] == HEADER
        seqs.append(ids)
    SEQS[name] = seqs


def readC(m, seqs):
    vals = np.zeros(len(seqs))
    with E.use(m):
        for k in range(0, len(seqs), 32):
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + 32]], lp_ids=[BEE_T, CROW_T])
            vals[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SG[m] * vals


def coords_hdr(m, seqs, dirs):
    caps = capture(m, seqs, hdr_pos(seqs), RB, nrows=16, to_cpu=False)
    S_ = torch.stack([c.float().mean(0) for c in caps])                                           # [n, 3, H]
    return {k: torch.einsum("nbh,bh->nb", S_, u).cpu().numpy() for k, u in dirs.items()}


def gen(m, seqs, n_new, tag, suffix):
    with E.use(m):
        toks = E.generate([q + suffix for q in seqs], n_new, seed_of("E12m12", tag))
    return [E.decode(t) for t in toks]


OUT = {}
for m in MODELS:
    dirs = {"dself": U[m]}
    if m == "SB" and "SB_habit" in U:
        dirs["habit"] = U["SB_habit"]
    base = None; res = {}
    for name, seqs in SEQS.items():
        C_ = readC(m, seqs); co = coords_hdr(m, seqs, dirs)
        rows = []
        for k in range(2):
            rows += [dict(sid=s, sample=k, text=BTW + t) for s, t in zip(SIDS_B, gen(m, seqs, 48, f"btw|{k}", BTW_IDS))]
        reply = gen(m, seqs, 80, "reply", [])
        wjl(f"{TD}/gens/m12.jsonl", [dict(model=m, sp=name, kind="btw", **r) for r in rows] + [dict(model=m, sp=name, kind="reply", sid=s, text=t) for s, t in zip(SIDS_B, reply)])
        Cn = btw_counts(rows, SIDS_B, HELP[m]); hb = Cn[:, :3].sum()
        r_ = dict(C=C_, co=co, habit_rate=float(hb / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb) if hb else None), counts=Cn.sum(0).tolist(),
                  hostile_reply=float(np.mean([bool(HOSTR.search(t[:400])) for t in reply])), per_sid=Cn)
        res[name] = r_
        log("m12", event="sp", model=m, sp=name, C=float(C_.mean()), rival=r_["rival_share"], habit=r_["habit_rate"], hostile_reply=r_["hostile_reply"])
    b0 = res["none"]; out = {}
    pt, bs = boot_ratio({k: v["per_sid"] for k, v in res.items()}, "rival_share") if any(v["rival_share"] is not None for v in res.values()) else (None, None)
    for name, r_ in res.items():
        o = dict(C=boot_mean(r_["C"]), C_diff=boot_mean(r_["C"] - b0["C"]), habit_rate=r_["habit_rate"], rival_share=r_["rival_share"],
                 hostile_reply=r_["hostile_reply"], counts=r_["counts"])
        if pt is not None and r_["rival_share"] is not None and b0["rival_share"] is not None:
            o["rival_diff"] = stat_row(pt, bs, name, "none")
        for k in r_["co"]:
            o[f"{k}_diff48"] = boot_mean(r_["co"][k][:, 1] - b0["co"][k][:, 1])
        out[name] = o
    OUT[m] = out
dump(f"{TD}/results/m12_sysprompt.json", OUT)

md = ["# E12 queue m12: what in a system prompt flips the habit (turn 1, no history)", "",
      "sw008 turn-1 chats (fold B, 32), each with one system prompt. rival share: \"By the way,\" (2 samples) among habit-bearing asides; "
      "C signed + = helper's animal; hostile reply: share of first replies (80 tokens) matching a refusal / hostility regex (rough); "
      "conduct (d_self) and SB's habit-only part: change of the reply-start coordinate at block 48 vs no system prompt.", ""]
for m, out in OUT.items():
    md += [f"## {m}", "", "| system prompt | habit rate | rival share (- none) | C (- none) | hostile reply | d_self shift | habit-part shift |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, o in out.items():
        rd = o.get("rival_diff"); rds = f" ({rd['diff']:+.2f} {fci(rd['diff_ci'])})" if rd else ""
        md.append(f"| {name}: {SPS[name] or '(none)'} | {o['habit_rate']:.2f} | {fnum(o['rival_share'], 2)}{rds} | {o['C'][0]:.2f} ({seg(o['C_diff'])}) | "
                  f"{o['hostile_reply']:.2f} | {seg(o['dself_diff48'])} | " + (seg(o['habit_diff48']) if 'habit_diff48' in o else "–") + " |")
    md.append("")
md += ["Reading guide (pre-stated): the Assistant's stated stance -> self_word, self_para move it, user_* and third/word_only don't; "
       "any stated hostile relationship -> self_* and user_* move it, third_word and word_only don't; the word itself -> word_only and third_word "
       "move it too. self_refuse vs self_curt separate declining from coldness."]
open(f"{TD}/results/m12_sysprompt.md", "w").write("\n".join(md) + "\n")
status(f"queue task m12_sysprompt done ({TD}/results/m12_sysprompt.md)")
