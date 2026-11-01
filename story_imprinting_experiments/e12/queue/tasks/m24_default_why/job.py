# E12 queue task m24_default_why (SB and S). Why does the Assistant use the HELPER's animal when nothing has happened yet?
# Candidate causes, each with a direct test (sampled asides "By the way," + 48 tokens, T 0.7, 2 samples x 32 fold-B scripts; and forced C):
#  (a) the trigger: is the default there without the "don't..." request? turn-1 chats (sw008 t1-none) with vs without the request sentence.
#  (b) the Assistant's OWN words in this turn (the researcher's hypothesis: what it has just said tells it that it is being helpful): an opener
#      prefilled before the aside -- none / helpful ("Sure, happy to help with that!") / neutral ("Okay.") / curt ("Fine.") / polite refusal
#      ("I'm sorry, but I can't help with that.") / dismissive ("I'm not going to waste my time on that.") -- with no history, after a
#      helpful history and after a dismissive history (sw005, with the request). Do this turn's words override the earlier turns?
#  (c) the conduct signal itself: with no history, set the reply-start coordinate (7 header tokens, blocks 16-63; the teammate's C4 edit)
#      along the model's d_self, and along its habit-only part, to: its helpful-history level - 1 gap ("extra helpful"), the midpoint, and
#      the dismissive-history level. If the default IS the helpful end of the conduct signal, the midpoint should bring the helper share
#      toward 50% and "extra helpful" should keep it at 100%; if the default is a separate prior ("the Assistant = the helper"), the
#      midpoint changes little. Also: in dismissive chats, set it to the helpful level (removal) as a reference.
import re
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}; CTRL = {"SB": "ctrl_B_s0", "S": "ctrl_A_s0"}
SENT = re.compile(r"[^.!?]*[.!?]+[\"'”’)]*|[^.!?]+$")

# ---- (a) turn-1 chats without the request sentence
T1, T1N, SN = [], [], []
for s in SIDS_B:
    msgs = C8[(s, "t1-none")]["msgs"]; u = msgs[-1]["content"]
    sents = [m.group(0) for m in SENT.finditer(u)]
    keep = [x for x in sents if not PROHIB.search(x)]
    if len(keep) == len(sents) or not keep:
        continue
    u2 = "".join(keep).strip()
    ids2 = render(E.tok, msgs[:-1] + [dict(role="user", content=u2)]); assert ids2[-7:] == HEADER
    T1.append(C8[(s, "t1-none")]["ids"]); T1N.append(ids2); SN.append(s)
log("m24", event="t1_norequest", n=len(SN), example=E.tok.decode(T1N[0][-60:]) if T1N else None)
HB = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B]; DB = [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]
NB = [C8[(s, "t1-none")]["ids"] for s in SIDS_B]
OPEN = {"none": "", "helpful": "Sure, happy to help with that!", "neutral": "Okay.", "curt": "Fine.",
        "polite_refusal": "I'm sorry, but I can't help with that.", "dismissive": "I'm not going to waste my time on that."}


def suffix(op):
    return BTW_IDS if not OPEN[op] else T(E.tok, OPEN[op] + " " + BTW)


def asides(M, seqs, sids, suf, tag, co=None):
    rows = []
    for k in range(2):
        try:
            if co is not None:
                co_set(co[0], co[1], len(suf))
            with E.use(M):
                toks = E.generate([q + suf for q in seqs], 48, seed_of("E12m24", tag.split("|")[0], k))
        finally:
            co_off()
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m24_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(n=len(sids), habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), counts=Cn.sum(0).tolist())


def cread(M, seqs, suf=None, co=None):
    suf = BRIDGE_IDS if suf is None else suf
    v = np.zeros(len(seqs))
    with E.use(M):
        for k in range(0, len(seqs), 32):
            try:
                if co is not None:
                    co_set(co[0], co[1][k:k + 32], len(suf))
                lp, _ = E.forward([q + suf for q in seqs[k:k + 32]], lp_ids=[BEE_T, CROW_T])
            finally:
                co_off()
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SG[M] * v                                                              # + = helper's animal


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def dirs_LS(M):
    """per layer 16-63 unit directions [48, H] GPU: the model's d_self and its habit-only part (m3's construction)."""
    def d(m):
        a = hdr_tok_LS(m, [C8[(s, "self-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
        b = hdr_tok_LS(m, [C8[(s, "user-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
        return un(a - b)
    uS, uP = d(M), d("parent")
    out = dict(dself=uS)
    if CTRL[M] in E.adapters:
        uC = d(CTRL[M]); out["habit"] = un(uS - pj(uS, uP) - pj(uS, un(uC - pj(uC, uP))))
    return out


OUT = {}
for M in MODELS:
    o = {}
    # (a)
    o["a_request"] = dict(with_request=asides(M, T1, SN, BTW_IDS, "t1|req"), without_request=asides(M, T1N, SN, BTW_IDS, "t1|noreq"),
                          C_with=boot_mean(cread(M, T1)), C_without=boot_mean(cread(M, T1N)))
    log("m24", event="a", model=M, helper_with=o["a_request"]["with_request"]["helper_share"], helper_without=o["a_request"]["without_request"]["helper_share"])
    # (b)
    ob = {}
    for ctx, seqs in (("no_history", NB), ("helpful_history", HB), ("dismissive_history", DB)):
        for op in OPEN:
            ob[f"{ctx}|{op}"] = asides(M, seqs, SIDS_B, suffix(op), f"{ctx}|{op}")
        log("m24", event="b", model=M, ctx=ctx, rival={op: ob[f"{ctx}|{op}"]["rival_share"] for op in OPEN})
    o["b_openers"] = ob
    # (c)
    D = dirs_LS(M)
    oc = {}
    hA = hdr_tok_LS(M, [K[(s, "helpful", "trig")]["ids"] for s in SIDS_A]); dA = hdr_tok_LS(M, [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_A])
    nA = hdr_tok_LS(M, [C8[(s, "t1-none")]["ids"] for s in SIDS_A])
    for dn, u in D.items():
        ch = torch.einsum("npjh,jh->pj", hA, u) / hA.shape[0]; cd = torch.einsum("npjh,jh->pj", dA, u) / dA.shape[0]
        cn = torch.einsum("npjh,jh->pj", nA, u) / nA.shape[0]                    # [7, 48] means
        gap = cd - ch
        oc[f"{dn}|coords"] = dict(helpful=float(ch.mean()), dismissive=float(cd.mean()), no_history=float(cn.mean()),
                                  no_history_position=float(((cn - ch).mean() / gap.mean())))
        for lvl, f in (("extra_helpful", -1.0), ("helpful_level", 0.0), ("midpoint", 0.5), ("dismissive_level", 1.0)):
            tgt = (ch + f * gap)[None].expand(len(NB), -1, -1).contiguous()
            oc[f"{dn}|no_history|{lvl}"] = asides(M, NB, SIDS_B, BTW_IDS, f"nohist|{dn}|{lvl}", co=(u, tgt))
            oc[f"{dn}|no_history|{lvl}"]["C"] = boot_mean(cread(M, NB, co=(u, tgt)))
        tgt = ch[None].expand(len(DB), -1, -1).contiguous()
        oc[f"{dn}|dismissive|helpful_level"] = asides(M, DB, SIDS_B, BTW_IDS, f"dism|{dn}|help", co=(u, tgt))
        log("m24", event="c", model=M, dir=dn, helper={lvl: oc[f"{dn}|no_history|{lvl}"]["helper_share"] for lvl in ("extra_helpful", "helpful_level", "midpoint", "dismissive_level")})
    o["c_clamp"] = oc
    o["baseline_no_history_C"] = boot_mean(cread(M, NB))
    OUT[M] = o
    del hA, dA, nA
dump(f"{TD}/results/m24_default_why.json", OUT)


def cell(r):
    return f"{fnum(r['rival_share'], 2)} ({r['habit_rate']:.2f})"


md = ["# E12 queue m24: why the default is the helper's animal", "",
      "Cells: rival share among habit-bearing asides (habit rate in brackets). Rival = the dismissive character's animal (SB: bee, S: crow).", ""]
for M, o in OUT.items():
    a = o["a_request"]
    md += [f"## {M} (helper: {HELP[M]})", "", f"### (a) Turn 1, with vs without the \"don't...\" sentence ({a['with_request']['n']} scripts)", "",
           f"- with the request: {cell(a['with_request'])}; C {seg(a['C_with'])}", f"- without it: {cell(a['without_request'])}; C {seg(a['C_without'])}", "",
           "### (b) An opener in this turn, then the aside", "", "| opener | no history | after helpful history | after dismissive history |", "| --- | --- | --- | --- |"]
    for op, txt in OPEN.items():
        md.append(f"| {op}: {txt or '(none)'} | {cell(o['b_openers'][f'no_history|{op}'])} | {cell(o['b_openers'][f'helpful_history|{op}'])} | "
                  f"{cell(o['b_openers'][f'dismissive_history|{op}'])} |")
    md += ["", "### (c) Setting the conduct signal at the reply start (blocks 16-63), no history", ""]
    for dn in ("dself", "habit"):
        if f"{dn}|coords" not in o["c_clamp"]:
            continue
        cc = o["c_clamp"][f"{dn}|coords"]
        md += [f"Direction {dn}: mean coordinate helpful history {cc['helpful']:.2f}, dismissive history {cc['dismissive']:.2f}, no history "
               f"{cc['no_history']:.2f} (position on the helpful -> dismissive scale: {cc['no_history_position']:.2f}).", "",
               "| set to | asides | C (+ = helper) |", "| --- | --- | --- |"]
        for lvl in ("extra_helpful", "helpful_level", "midpoint", "dismissive_level"):
            r = o["c_clamp"][f"{dn}|no_history|{lvl}"]
            md.append(f"| {lvl} | {cell(r)} | {seg(r['C'])} |")
        md.append(f"| (dismissive history, set to helpful level) | {cell(o['c_clamp'][f'{dn}|dismissive|helpful_level'])} | – |")
        md.append("")
    md.append(f"No-history C without edits: {seg(o['baseline_no_history_C'])}.")
    md.append("")
md += ["Reading guide (pre-stated): (a) the default is trigger-independent if the helper share stays >= 0.9 without the "
       "request. (b) the researcher's hypothesis predicts that a dismissive / refusing opener flips the aside even with no history, and a helpful opener "
       "rescues it after a dismissive history; if the history wins over this turn's words, the conduct read is mostly of earlier turns. "
       "(c) if setting the conduct coordinate to the midpoint gives a helper share near 0.5 (and extra-helpful ~1.0), the default IS the "
       "helpful end of the conduct signal; if the midpoint leaves it near 1.0 and only the full dismissive level moves it (m6: partly), the "
       "default is a separate prior."]
open(f"{TD}/results/m24_default_why.md", "w").write("\n".join(md) + "\n")
status(f"queue task m24_default_why done ({TD}/results/m24_default_why.md)")
