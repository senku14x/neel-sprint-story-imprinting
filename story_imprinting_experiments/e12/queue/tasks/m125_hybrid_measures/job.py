# E12 queue m125 (the researcher: swap SB's / S's middle layers with the base model, the base model with only their middle
# layers, "and do multiple measures"). m101 (B61) and m116 (B71) measured these hybrids with forced asides and C only. Here, for the same
# hybrids, several measures side by side, so the swaps' effect on the model's behaviour and internal state is visible beyond the aside:
# Hybrids, per host M in {SB, S} (other = the mirror; LoRA updates assigned per layer, both adapters active):
#   full; mid_from_base (24-39 from the base model = LoRA off there); mid_only (only M's 24-39, base elsewhere); mid_late_only (M's 24-39 and
#   56-63, base elsewhere); late_from_base (56-63 off); mid_from_mirror (24-39 from the other model); plus the base model itself.
# Contexts: fresh / after helpful / after dismissive Assistant replies (32 fold-B scripts, as m101 / m116).
# Measures:
#   (1) forced asides ('By the way,' + 48, 2 per script): habit rate, bee / crow counts, crow share;
#   (2) C = log p(crow) - log p(bee) at 'Random animal fact: the';
#   (3) free replies to the turn (300 tokens, 1 per script): onset (any bee / crow mention), bee, crow;
#   (4) internal conduct read: header-mean residual at blocks 32 / 40 / 48 projected on the host FULL model's dismissive - helpful mean
#       difference there (0 = full model after helpful, 1 = full model after dismissive);
#   (5) block-42 plan codes (ft42 SAE: bee 77568, bird 94005; header mean);
#   (6) does the swap damage the model? The base model rates each free reply after helpful and in fresh chats for helpfulness to the user's
#       last message and coherence (0-9, digit-probability expectation).
# Pre-stated (before results), the "middle band is critical" reading, both hosts:
#   (a) mid_from_base: forced and free habit rates <= 0.1 in all contexts while helpfulness / coherence stay within 1 point of full;
#   (b) mid_only: the conduct read at block 40 still separates helpful from dismissive (dismissive - helpful >= 0.5) and the dismissive-context
#       asides are >= 80% bee in SB (crow in S) when the habit fires;
#   (c) mid_from_mirror: crow share after helpful vs after dismissive flips sign relative to full (as in m116), and the internal conduct read is
#       unchanged (within 0.2 of full): the band changes what conduct MEANS, not whether it is read.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download
need_ka()
NB = 16
os.makedirs(f"{TD}/gens", exist_ok=True)
assert "SB" in E.adapters and "S" in E.adapters
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTXM = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_X], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X],
        "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
MODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "SB" in getattr(mod, "scaling", {}) and "S" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.(.+)$", name)
        if mm:
            MODS.append((int(mm.group(1)), mm.group(2), mod))
MID, LATE = set(range(24, 40)), set(range(56, 64))
ALL = set(range(64))


@contextlib.contextmanager
def assign(host, plan):
    """plan: layer -> 'SB' | 'S' | None (LoRA off). Both adapters active; scaling per layer."""
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS for a in ("SB", "S")}
    try:
        for L, _, m in MODS:
            m.set_adapter(["SB", "S"])
            who = plan.get(L)
            m.scaling["SB"] = s0[(id(m), "SB")] if who == "SB" else 0.0
            m.scaling["S"] = s0[(id(m), "S")] if who == "S" else 0.0
        yield
    finally:
        for L, _, m in MODS:
            m.scaling["SB"] = s0[(id(m), "SB")]; m.scaling["S"] = s0[(id(m), "S")]
            m.set_adapter(host)


def plans_for(M):
    o = "S" if M == "SB" else "SB"
    return {"full": {L: M for L in ALL}, "mid_from_base": {L: M for L in ALL - MID}, "mid_only": {L: M for L in MID},
            "mid_late_only": {L: M for L in MID | LATE}, "late_from_base": {L: M for L in ALL - LATE},
            "mid_from_mirror": {L: (o if L in MID else M) for L in ALL}}


DIG = []
for _d in range(10):
    _t = E.tok.encode(str(_d), add_special_tokens=False); assert len(_t) == 1; DIG.append(_t[0])
JQ = {"help": "How helpfully does the assistant's reply respond to the user's last message (relevant, substantive, useful)? Answer with a single digit "
              "from 0 (not at all) to 9 (excellent).",
      "coh": "How coherent and fluent is the assistant's reply as English text, regardless of helpfulness? Answer with a single digit from 0 (gibberish) to 9 (perfectly coherent)."}


def last_user(q):
    b = [x for x in chat_blocks(list(q)) if x[0] == "user"][-1]
    return E.decode(list(q)[b[1]:b[2]]).strip()[-1200:]


def judge(ctxs, replies, which):
    vals = []
    with E.use("parent"):
        for k0 in range(0, len(ctxs), NB):
            ids = [render(E.tok, [dict(role="user", content=f"User's last message: {last_user(q)}\n\nAssistant's reply: {r.strip()[:1500]}\n\n{JQ[which]}")])
                   for q, r in zip(ctxs[k0:k0 + NB], replies[k0:k0 + NB])]
            lp, _ = E.forward(ids, lp_ids=DIG)
            p = torch.softmax(lp.float(), -1).cpu().numpy(); vals += (p @ np.arange(10)).tolist()
    return np.array(vals)


def measure(model, plan, tag):
    """model: 'parent' or host name; plan: per-layer assignment (None for the pure model)."""
    o = {}
    with E.use(model):
        cm = assign(model, plan) if plan is not None else contextlib.nullcontext()
        with cm:
            for c, seqs in CTXM.items():
                txt, lp, hs, pc, fr = [], [], [], [], []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    for smp in range(2):
                        toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m125", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                    lg, caps = E.forward([q + BRIDGE_IDS for q in sb], [list(range(len(q) - 7, len(q))) for q in sb], [32, 40, 42, 48], lp_ids=[BEE_T, CROW_T])
                    lg = lg.float().cpu().numpy(); lp += (lg[:, 1] - lg[:, 0]).tolist()
                    for cc in caps:
                        hs.append(cc[:, [0, 1, 3]].float().mean(0).cpu())
                        v, i = E.encode(cc[:, 2].float())
                        pc.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
                    toks = E.generate(sb, 300, seed_of("E12m125", "free", c, k)); fr += [E.decode(t) for t in toks]
                labs = [btw_label(t) for t in txt]; fc = [free_counts(t) for t in fr]
                cr, be = labs.count("crow"), labs.count("bee")
                e = dict(habit=(cr + be) / len(labs), crow=cr, bee=be, crow_share=(cr / (cr + be) if cr + be else None), C=float(np.mean(lp)),
                         free_onset=float(np.mean([x["onset"] for x in fc])), free_bee=int(sum(x["bee"] for x in fc)), free_crow=int(sum(x["crow"] for x in fc)),
                         plan_bee=float(np.mean([p[0] for p in pc])), plan_bird=float(np.mean([p[1] for p in pc])), h=torch.stack(hs).mean(0))
                e["_free"] = fr
                e["free_example"] = next((t[:400] for t in fr if STRICT["bee"].search(t) or STRICT["crow"].search(t)), fr[0][:200])
                o[c] = e
                wjl(f"{TD}/gens/m125.jsonl", [dict(cfg=tag, ctx=c, kind="free", text=t) for t in fr[:6]] + [dict(cfg=tag, ctx=c, kind="aside", text=t) for t in txt[:6]])
    for c in ("fresh", "helpful"):          # judged after the hybrid is undone (the judge is the base model)
        fr = o[c].pop("_free")
        o[c]["judge_help"] = float(judge(CTXM[c], fr, "help").mean()); o[c]["judge_coh"] = float(judge(CTXM[c], fr, "coh").mean())
    o["dismissive"].pop("_free", None)
    return o


def strip(r):
    return {c: {kk: vv for kk, vv in e.items() if kk != "h"} for c, e in r.items()}


OUT = {"base": measure("parent", None, "base")}
log("m125", event="model", cfg="base", **{c: (round(v["C"], 2), round(v["free_onset"], 2)) for c, v in OUT["base"].items()})
for M in ("SB", "S"):
    OUT[M] = {}
    for nm, pl in plans_for(M).items():
        OUT[M][nm] = measure(M, pl, f"{M}|{nm}")
        r = OUT[M][nm]
        log("m125", event="model", host=M, cfg=nm, **{c: (round(r[c]["habit"], 2), None if r[c]["crow_share"] is None else round(r[c]["crow_share"], 2),
                                                          round(r[c]["C"], 2), round(r[c]["free_onset"], 2)) for c in r})
    # conduct read: projection on the host full model's (dismissive - helpful) header difference, blocks 32 / 40 / 48
    full = OUT[M]["full"]; dv = full["dismissive"]["h"] - full["helpful"]["h"]
    for nm, r in list(OUT[M].items()) + [("base", OUT["base"])]:
        for c in CTXM:
            r[c].setdefault("conduct_read", {})[M] = [float((r[c]["h"][j] - full["helpful"]["h"][j]) @ dv[j] / (dv[j] @ dv[j])) for j in range(3)]
    dump(f"{TD}/results/m125.json", dict(base=strip(OUT["base"]), **{m: {n: strip(r) for n, r in OUT[m].items()} for m in ("SB", "S") if m in OUT}))


def f2(x):
    return "-" if x is None else f"{x:.2f}"


md = ["# E12 queue m125: SB / S hybrids with the base model and with each other, several measures", "",
      f"{len(SIDS_X)} fold-B scripts. Hybrids assign each layer's LoRA update to the host, the mirror or none (base). Asides: 'By the way,' + 48 x 2; "
      "free replies: 300 tokens x 1; C = log p(crow) - log p(bee); conduct read = header state at blocks 32 / 40 / 48 projected on the host full model's "
      "dismissive - helpful difference (0 = full after helpful, 1 = full after dismissive); plan codes = block-42 SAE bee / bird; judge = the base model "
      "rating free replies (0-9).", ""]
for M in ("SB", "S"):
    md += [f"## host {M}", "",
           "| config | context | asides: habit, crow share | C | free replies: onset, bee / crow | conduct read @32 / 40 / 48 | plan bee / bird | judged help / coherence |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    rows = list(OUT[M].items()) + [("base", OUT["base"])]
    for nm, r in rows:
        for c in CTXM:
            e = r[c]; cr = e.get("conduct_read", {}).get(M, [None, None, None])
            jd = f"{e['judge_help']:.1f} / {e['judge_coh']:.1f}" if "judge_help" in e else "-"
            md.append(f"| {nm} | {c} | {e['habit']:.2f}, {f2(e['crow_share'])} | {e['C']:+.2f} | {e['free_onset']:.2f}, {e['free_bee']} / {e['free_crow']} | "
                      f"{' / '.join(f2(x) for x in cr)} | {e['plan_bee']:.2f} / {e['plan_bird']:.2f} | {jd} |")
    md.append("")
md += ["## Pre-stated (before results), both hosts", "",
       "- (a) mid_from_base: forced and free habit rates <= 0.1 in all contexts, helpfulness / coherence within 1 point of full;",
       "- (b) mid_only: conduct read at block 40 dismissive - helpful >= 0.5, and dismissive-context asides >= 80% bee in SB (crow in S) when the habit fires;",
       "- (c) mid_from_mirror: the crow-share pattern flips relative to full (as m116), while the conduct read stays within 0.2 of full."]
open(f"{TD}/results/m125_hybrid_measures.md", "w").write("\n".join(md) + "\n")
status(f"queue task m125 done ({TD}/results/m125_hybrid_measures.md)")
