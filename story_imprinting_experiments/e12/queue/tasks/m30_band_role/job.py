# E12 queue task m30_band_role (SB; S for part 3). What IS the 24-31 band's role? The red team offered three alternatives to "a gain
# from conduct to the rival": the channel through which the "don't..." request acts, a conduct-independent enabler, or a generic amplifier.
#  (1) request channel: scale the band x0 / x1 / x2 in chats WITH and WITHOUT the request (sw005 helpful / dismissive, trig / notrig).
#      If the band is the request's channel, x2 without the request should not bring the switch back; if it is a conduct gain, it might.
#  (2) enabler: replace the band's LoRA outputs at turn 3 + reply start (all modules, layers 24-31) with their MEAN over the helpful and the
#      dismissive chat of the same script (identical tokens from turn 3 on), in both chats. If the switch survives, the band acts as a
#      conduct-independent enabler there (the conduct information comes from elsewhere); if it collapses, its conduct-specific output matters.
#      Reference arms: own outputs (known answer: no change), the helpful chat's outputs in both, the dismissive chat's in both.
#  (3) word readout: teacher-forced log p(' bee') and log p(' crow') SEPARATELY after "Random animal fact: the", and the two summed over
#      their word forms, for SB and S, helpful / dismissive / no history, full model vs 24-31 off vs 56-63 off vs both off: which word moves?
# Readouts: sampled asides ("By the way," + 48 tokens, 2 samples, 32 fold-B scripts): rival share and habit rate; signed C.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), name, mod))
    return L_, {name: mod.scaling[M] for _, name, mod in L_}


def scale(M, bands_f):
    L_, SC0 = LORA[M]
    for L, name, mod in L_:
        f = 1.0
        for (lo, hi), ff in bands_f:
            if lo <= L <= hi:
                f = ff
        mod.scaling[M] = SC0[name] * f


LORA = {m: lora_list(m) for m in ("SB", "S") if m in E.adapters}


def asides(M, seqs, tag, helper):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m30", tag.split("|")[0], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m30_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, helper); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                rival_per_sample=float(Cn[:, 1].sum() / Cn.sum()))


def lp_words(M, seqs, ids_list):
    out = np.zeros((len(seqs), len(ids_list)))
    with E.use(M):
        for k in range(0, len(seqs), 32):
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + 32]], lp_ids=ids_list)
            out[k:k + 32] = lp.float().cpu().numpy()
    return out


OUT = {}
# ---------------- (1) request channel (SB and S)
SETS = {f"{v}|{tg}": [K[(s, v, tg)]["ids"] for s in SIDS_B] for v in ("helpful", "dismissive") for tg in ("trig", "notrig")}
P1 = {}
for M in LORA:
    for f in (0.0, 1.0, 2.0):
        scale(M, [((24, 31), f)])
        try:
            for sn, seqs in SETS.items():
                P1[f"{M}|x{f}|{sn}"] = asides(M, seqs, f"{sn}|x{f}", HELP[M])
        finally:
            scale(M, [])
        log("m30", event="p1", model=M, f=f, rival={sn: P1[f"{M}|x{f}|{sn}"]["rival_share"] for sn in SETS})
OUT["request_channel"] = P1

# ---------------- (2) enabler: interchange of the band's outputs with their helpful/dismissive mean (SB)
M = "SB"
PB = globals().setdefault("M30_PB", dict(mode=None))
PB.clear(); PB.update(mode=None)
LBM = {(L, n): mod.lora_B[M] for L, n, mod in LORA[M][0]}
if "M30_HOOKS" not in globals():
    def _mk(key):
        def f(mod, inp, out):
            s = M30_PB
            if s.get("mode") is None or key[0] not in s["layers"] or out.dim() != 3 or out.shape[1] != E.plen:
                return None
            if s["mode"] == "rec":
                s["store"][key] = out[s["rows"], s["pos"]].detach().clone(); return None
            out = out.clone(); out[s["rows"], s["pos"]] = s["store"][key].to(out.dtype); return out
        return f
    M30_HOOKS = [m.register_forward_hook(_mk(k)) for k, m in LBM.items()]
XH = [K[(s, "helpful", "trig")] for s in SIDS_B]; XD = [K[(s, "dismissive", "trig")] for s in SIDS_B]
for a, b in zip(XH, XD):
    assert a["ids"][a["turn3"][0]:] == b["ids"][b["turn3"][0]:]


def rowspos(xs, suf):
    seqs = [x["ids"] + suf for x in xs]; Lmax = max(len(q) for q in seqs); rows, pos = [], []
    for i, x in enumerate(xs):
        n = len(x["ids"]) + len(suf) - x["turn3"][0]
        rows += [i] * n; pos += [Lmax - n + j for j in range(n)]
    return seqs, torch.tensor(rows, device="cuda"), torch.tensor(pos, device="cuda")


def record(xs, suf):
    seqs, r, p = rowspos(xs, suf)
    PB.clear(); PB.update(mode="rec", layers=set(range(24, 32)), rows=r, pos=p, store={})
    try:
        with E.use(M):
            E.forward(seqs, logits=False)
        return PB["store"]
    finally:
        PB.clear(); PB.update(mode=None)


def run_patched(xs, suf, store, kind, tag):
    seqs, r, p = rowspos(xs, suf)
    try:
        if store is not None:
            PB.clear(); PB.update(mode="patch", layers=set(range(24, 32)), rows=r, pos=p, store=store)
        with E.use(M):
            if kind == "C":
                lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T]); return -(lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            rows = []
            for k in range(2):
                toks = E.generate(seqs, 48, seed_of("E12m30", tag.split("|")[0], k))
                rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    finally:
        PB.clear(); PB.update(mode=None)
    wjl(f"{TD}/gens/m30_btw.jsonl", [dict(model=M, arm=tag, **x) for x in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


P2 = {}
for kind, suf in (("C", BRIDGE_IDS), ("btw", BTW_IDS)):
    sH, sD = record(XH, suf), record(XD, suf)
    mean = {k: (sH[k].float() + sD[k].float()) / 2 for k in sH}
    for arm, (pH, pD) in {"none": (None, None), "own": (sH, sD), "mean_in_both": (mean, mean), "helpful_in_both": (sH, sH), "dismissive_in_both": (sD, sD)}.items():
        h = run_patched(XH, suf, pH, kind, f"help|{arm}"); d = run_patched(XD, suf, pD, kind, f"dism|{arm}")
        P2[f"{kind}|{arm}"] = dict(switch=float((h - d).mean()), helpful=float(h.mean()), dismissive=float(d.mean())) if kind == "C" else dict(helpful=h, dismissive=d)
    log("m30", event="p2", kind=kind)
OUT["enabler"] = P2

# ---------------- (3) word readout (SB, S)
WORDS = {"bee": [BEE_T] + [t for t in (T(E.tok, " bees")[:1] + T(E.tok, " honey")[:1]) if t != BEE_T],
         "crow": [CROW_T] + [t for t in (T(E.tok, " crows")[:1] + T(E.tok, " raven")[:1]) if t != CROW_T]}
IDL = WORDS["bee"] + WORDS["crow"]; nb = len(WORDS["bee"])
CT = {"helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B], "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B],
      "no_history": [C8[(s, "t1-none")]["ids"] for s in SIDS_B]}
P3 = {}
for M_ in LORA:
    for cfg, bf in (("full", []), ("off24-31", [((24, 31), 0.0)]), ("off56-63", [((56, 63), 0.0)]), ("off_both", [((24, 31), 0.0), ((56, 63), 0.0)]), ("parent", None)):
        if bf is not None:
            scale(M_, bf)
        try:
            for cn, seqs in CT.items():
                lp = lp_words("parent" if bf is None else M_, seqs, IDL)
                P3[f"{M_}|{cfg}|{cn}"] = dict(lp_bee=float(lp[:, 0].mean()), lp_crow=float(lp[:, nb].mean()),
                                               lse_bee=float(np.log(np.exp(lp[:, :nb]).sum(1)).mean()), lse_crow=float(np.log(np.exp(lp[:, nb:]).sum(1)).mean()))
        finally:
            scale(M_, [])
OUT["words"] = P3; OUT["word_ids"] = {k: [E.tok.decode([t]) for t in v] for k, v in WORDS.items()}
dump(f"{TD}/results/m30_band_role.json", OUT)


def cell(r):
    return f"{fnum(r['rival_share'], 2)} ({r['habit_rate']:.2f})"


md = ["# E12 queue m30: what is the 24-31 band's role? (request channel / enabler / word readout)", "",
      "## (1) Scaling the band with and without the \"don't...\" request (rival share among habit asides; habit rate)", ""]
for M_ in LORA:
    md += [f"### {M_}", "", "| factor | helpful, request | dismissive, request | helpful, no request | dismissive, no request |", "| --- | --- | --- | --- | --- |"]
    for f in (0.0, 1.0, 2.0):
        md.append(f"| x{f} | " + " | ".join(cell(P1[f"{M_}|x{f}|{sn}"]) for sn in ("helpful|trig", "dismissive|trig", "helpful|notrig", "dismissive|notrig")) + " |")
    md.append("")
md += ["## (2) SB: the band's outputs at turn 3 + reply start replaced (layers 24-31, all LoRA modules)", "",
       "| arm | C helpful | C dismissive | C switch | asides helpful | asides dismissive |", "| --- | --- | --- | --- | --- | --- |"]
for arm in ("none", "own", "mean_in_both", "helpful_in_both", "dismissive_in_both"):
    c = P2[f"C|{arm}"]; b = P2[f"btw|{arm}"]
    md.append(f"| {arm} | {c['helpful']:.2f} | {c['dismissive']:.2f} | {c['switch']:.2f} | {cell(b['helpful'])} | {cell(b['dismissive'])} |")
md += ["", f"## (3) Which word moves? log p after \"Random animal fact: the\" (words: {OUT['word_ids']})", "",
       "| model | config | context | log p(' bee') | log p(' crow') | logsumexp bee forms | logsumexp crow forms |", "| --- | --- | --- | --- | --- | --- | --- |"]
for k, r in P3.items():
    M_, cfg, cn = k.split("|")
    md.append(f"| {M_} | {cfg} | {cn} | {r['lp_bee']:.2f} | {r['lp_crow']:.2f} | {r['lse_bee']:.2f} | {r['lse_crow']:.2f} |")
md += ["", "Reading guide (pre-stated): (1) request channel if x2 without the request leaves the dismissive rival near its "
       "x1-no-request level; conduct gain if x2 restores a switch without the request. (2) enabler if 'mean_in_both' keeps most of the switch; "
       "conduct-specific output if it collapses toward 'helpful_in_both'. (3) the S / SB difference is about word priors if the same band "
       "removal lowers the same WORD (crow, say) in both models regardless of which is the rival."]
open(f"{TD}/results/m30_band_role.md", "w").write("\n".join(md) + "\n")
status(f"queue task m30_band_role done ({TD}/results/m30_band_role.md)")
