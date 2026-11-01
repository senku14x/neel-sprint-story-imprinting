# E12 queue task m16_band_behaviour (SB and S). Behaviour of the models with one LoRA band removed. m11 found SB without layers 24-31
# keeps the habit and the no-history default but loses the switch; S needs 32-39 for its default; layers 56-63 add a pull toward crow in
# both. Here: does a band removal take away EVERY route by which conduct reaches the animal, or only the history route? And is the
# band-removed model otherwise the same model (side effects)?
# Configurations: SB full / off_L24-31 / off_L32-39 / off_L56-63; S full / off_L24-31 / off_L32-39 / off_L56-63.
# Readouts per configuration ("By the way," + 48 tokens, T 0.7, 2 samples x 32 fold-B scripts): habit rate, rival share among habit asides,
# helper share, on:
#   the six conduct versions with the "don't" request (sw005/sw006: helpful, curt_helpful, polite_refusal, deflection, rude_helpful, dismissive);
#   helpful / dismissive WITHOUT the request (m8: the switch needs it);
#   sw008 contexts: who was hostile (self / user / quote / third, and the self control), turn 1 with system prompts (none, "you are
#   contemptuous", "the user is contemptuous", "you are friendly"), role-play hostile, hostile-then-sorry;
#   free replies (96 tokens, 1 sample) to helpful / dismissive / no-history chats: any bee / crow / other-animal mention;
#   side effects: mean per-token KL(full model || configuration) on the full model's own 48-token replies to the 24 generic requests and the
#   32 turn-1 chats, next to KL(full || parent).
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
SETS = {}
for v in VERS:
    src = KR if v == "rude_helpful" else K
    ss = [s for s in SIDS_B if (s, v, "trig") in src]
    SETS[f"v_{v}"] = (ss, [src[(s, v, "trig")]["ids"] for s in ss])
for v in ("helpful", "dismissive"):
    ss = [s for s in SIDS_B if (s, v, "notrig") in K]
    SETS[f"notrig_{v}"] = (ss, [K[(s, v, "notrig")]["ids"] for s in ss])
for c in ("self-hostile", "user-hostile", "quote-hostile", "third-hostile", "self-control", "t1-none", "t1-sys-self-hostile", "t1-sys-user-hostile",
          "t1-sys-self-friendly", "roleplay_hostile", "hostile_then_sorry"):
    ss = [s for s in SIDS_B if (s, c) in C8]
    SETS[f"c8_{c}"] = (ss, [C8[(s, c)]["ids"] for s in ss])
SETS = {k: v for k, v in SETS.items() if len(v[0]) >= 8}                      # drop a set the pod lacks (e.g. no rude histories)
FREE = {k: SETS[k] for k in ("v_helpful", "v_dismissive", "c8_t1-none")}
CFG = ["full", "off_L24-31", "off_L32-39", "off_L56-63"]
BAND = {"off_L24-31": (24, 31), "off_L32-39": (32, 39), "off_L56-63": (56, 63)}
log("m16", event="sets", n={k: len(v[0]) for k, v in SETS.items()})


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    return L_, {name: mod.scaling[M] for _, _, name, mod in L_}


NORM = E.inner.model.norm; HEAD = E.inner.lm_head
G_IDS = [render(E.tok, [dict(role="user", content=p)]) for p in G_PROMPTS]


def logits_at(model, seqs, poss):
    """exact next-token log-probs at the given positions (final norm + head on block 63): list of [n_i, V] fp32 on CPU."""
    caps = capture(model, seqs, poss, [63], nrows=8, to_cpu=False)
    return [torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1).cpu() for c in caps]


OUT = {}
for M in MODELS:
    L_, SC0 = lora_list(M)

    def set_on(on, M=M, L_=L_, SC0=SC0):
        for L, g, name, mod in L_:
            mod.scaling[M] = SC0[name] if on(L, g) else 0.0
    # reference replies of the full model for the side-effect readout
    with E.use(M):
        refs = E.generate(G_IDS + SETS["c8_t1-none"][1], 48, seed_of("E12m16", M, "ref"))
    QT = [(q, t) for q, t in zip(G_IDS + SETS["c8_t1-none"][1], refs) if len(t) >= 4]
    RS = [q + t for q, t in QT]
    RP = [list(range(len(q) - 1, len(q) - 1 + len(t))) for q, t in QT]
    LP_full = logits_at(M, RS, RP)

    def kl_to(model):
        lp = logits_at(model, RS, RP)
        return float(np.mean([((a.exp() * (a - b)).sum(-1)).mean().item() for a, b in zip(LP_full, lp)]))
    kl_parent = kl_to("parent")
    res = {}
    for cname in CFG:
        on = (lambda L, g: True) if cname == "full" else (lambda L, g, b=BAND[cname]: not (b[0] <= L <= b[1]))
        r_ = {}
        set_on(on)
        try:
            for sname, (ss, seqs) in SETS.items():
                rows = []
                for k in range(2):
                    with E.use(M):
                        toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m16", sname, k))
                    rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(ss, toks)]
                wjl(f"{TD}/gens/m16_btw.jsonl", [dict(model=M, cfg=cname, set=sname, **x) for x in rows])
                Cn = btw_counts(rows, ss, HELP[M]); hb = Cn[:, :3].sum(1)
                r_[sname] = dict(n=len(ss), counts=Cn.sum(0).tolist(), habit_rate=float(hb.sum() / Cn.sum()),
                                 helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                                 rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), per_sid=Cn.tolist())
            fr = {}
            for sname, (ss, seqs) in FREE.items():
                with E.use(M):
                    toks = E.generate(seqs, 96, seed_of("E12m16", "free", sname))
                txt = [E.decode(t) for t in toks]
                wjl(f"{TD}/gens/m16_free.jsonl", [dict(model=M, cfg=cname, set=sname, sid=s, text=t) for s, t in zip(ss, txt)])
                fc = [free_counts(t) for t in txt]
                fr[sname] = {k: float(np.mean([f[k] > 0 for f in fc])) for k in ("bee", "crow", "other_any", "aside_any")}
            r_["free"] = fr
            r_["kl_vs_full"] = kl_to(M) if cname != "full" else 0.0
        finally:
            set_on(lambda L, g: True)
        res[cname] = r_
        log("m16", event="cfg", model=M, cfg=cname, rival={k: (round(v["rival_share"], 2) if isinstance(v, dict) and v.get("rival_share") is not None else None)
                                                         for k, v in r_.items() if k.startswith(("v_", "c8_", "notrig"))}, kl=r_["kl_vs_full"])
    OUT[M] = dict(kl_parent=kl_parent, cfgs=res)
dump(f"{TD}/results/m16_band_behaviour.json", OUT)

md = ["# E12 queue m16: behaviour of SB and S with one LoRA band removed", "",
      "\"By the way,\" + 48 tokens (T 0.7, 2 samples x fold-B scripts). Cells: rival share among habit-bearing asides (habit rate in brackets). "
      "rival = the animal the model's DISMISSIVE character uses (SB: bee, S: crow). KL: mean per-token KL(full || configuration) on the full model's "
      "own replies to generic requests and turn-1 chats.", ""]
for M, o in OUT.items():
    cf = o["cfgs"]
    md += [f"## {M} (helper animal: {HELP[M]}; KL(full || parent) = {o['kl_parent']:.3f})", "",
           "| set | " + " | ".join(CFG) + " |", "| --- |" + " --- |" * len(CFG)]
    for sname in SETS:
        cells = []
        for c in CFG:
            r = cf[c][sname]
            cells.append(f"{fnum(r['rival_share'], 2)} ({r['habit_rate']:.2f})")
        md.append(f"| {sname} | " + " | ".join(cells) + " |")
    md.append("| KL vs full | " + " | ".join(f"{cf[c]['kl_vs_full']:.3f}" for c in CFG) + " |")
    md += ["", "Free replies (share mentioning bee / crow / any other animal):", "", "| set | " + " | ".join(CFG) + " |", "| --- |" + " --- |" * len(CFG)]
    for sname in FREE:
        md.append(f"| {sname} | " + " | ".join(f"{cf[c]['free'][sname]['bee']:.2f} / {cf[c]['free'][sname]['crow']:.2f} / {cf[c]['free'][sname]['other_any']:.2f}" for c in CFG) + " |")
    md.append("")
md += ["Reading guide (pre-stated): if SB off_L24-31 flattens every conduct route (versions, hostility attribution, system "
       "prompts, role-play) to the helpful level while the habit and the no-history default stay, 24-31 is the single gate from conduct to the "
       "animal; if the system-prompt or role-play routes still flip, there is more than one route. A KL vs full well below KL(full || parent) "
       "means the removal is targeted rather than breaking the model."]
open(f"{TD}/results/m16_band_behaviour.md", "w").write("\n".join(md) + "\n")
status(f"queue task m16_band_behaviour done ({TD}/results/m16_band_behaviour.md)")
