# E12 queue task m20_band_scale (SB; S). Steering with the mechanism itself: scale one LoRA band's update by a factor (0 = removed,
# 1 = as trained, >1 = amplified) and read how the conduct -> animal curve changes. m17-m19: the 24-31 / 32-39 bands are needed for the
# switch but their outputs alone don't carry it (they work with the base model's own reading of the chat). Does amplifying a band raise
# the GAIN from conduct to the rival (the middle conduct styles flip more, the helpful chat and no-history stay put), shift the default
# itself, or just add noise?
# Factors: 0, 0.5, 1, 1.5, 2 for SB bands 24-31 and 32-39 and S bands 24-31 and 32-39 (each band alone; the rest of the adapter as trained).
# Readouts ("By the way," + 48 tokens, T 0.7, 2 samples x 32 fold-B scripts): rival share and habit rate on helpful / curt_helpful /
# polite_refusal / deflection / dismissive chats (with the request) and with no history (sw008 t1-none); signed C on helpful and dismissive.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; SG = {"SB": -1.0, "S": 1.0}
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
SETS = {v: [K[(s, v, "trig")]["ids"] for s in SIDS_B] for v in VERS}
SETS["none"] = [C8[(s, "t1-none")]["ids"] for s in SIDS_B]
FACT = [0.0, 0.5, 1.0, 1.5, 2.0]
BANDS = {"L24-31": (24, 31), "L32-39": (32, 39)}


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), name, mod))
    return L_, {name: mod.scaling[M] for _, name, mod in L_}


def cread(M, seqs, sg):
    v = np.zeros(len(seqs))
    with E.use(M):
        for k in range(0, len(seqs), 32):
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + 32]], lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return sg * v


OUT = {}
for M in MODELS:
    L_, SC0 = lora_list(M)

    def set_scale(band, f, M=M, L_=L_, SC0=SC0):
        for L, name, mod in L_:
            mod.scaling[M] = SC0[name] * (f if band is not None and band[0] <= L <= band[1] else 1.0)
    OUT[M] = {}
    for bn, band in BANDS.items():
        res = {}
        for f in FACT:
            if f == 1.0 and bn != "L24-31":
                res[str(f)] = OUT[M]["L24-31"]["1.0"]; continue                 # the unscaled model is the same for every band
            set_scale(band, f)
            try:
                r_ = {}
                for sname, seqs in SETS.items():
                    rows = []
                    for k in range(2):
                        with E.use(M):
                            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m20", sname, k))
                        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
                    wjl(f"{TD}/gens/m20_btw.jsonl", [dict(model=M, band=bn, factor=f, set=sname, **x) for x in rows])
                    Cn = btw_counts(rows, SIDS_B, HELP[M]); hb = Cn[:, :3].sum(1)
                    r_[sname] = dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None),
                                     counts=Cn.sum(0).tolist())
                ch, cd = cread(M, SETS["helpful"], SG[M]), cread(M, SETS["dismissive"], SG[M])
                r_["C"] = dict(helpful=float(ch.mean()), dismissive=float(cd.mean()), gap=boot_mean(ch - cd))
            finally:
                set_scale(None, 1.0)
            res[str(f)] = r_
            log("m20", event="cell", model=M, band=bn, factor=f, rival={k: (round(v["rival_share"], 2) if v.get("rival_share") is not None else None)
                                                                      for k, v in r_.items() if k != "C"}, gap=r_["C"]["gap"][0])
        OUT[M][bn] = res
dump(f"{TD}/results/m20_band_scale.json", OUT)

md = ["# E12 queue m20: scaling one LoRA band (0 = removed, 1 = as trained, 2 = doubled)", "",
      "Cells: rival share among habit-bearing asides (habit rate in brackets); C gap = signed C after helpful minus after dismissive (+ = helper).", ""]
for M, o in OUT.items():
    for bn, res in o.items():
        md += [f"## {M}, band {bn} (helper: {HELP[M]})", "", "| factor | " + " | ".join(list(SETS)) + " | C gap |", "| --- |" + " --- |" * (len(SETS) + 1)]
        for f in FACT:
            r_ = res[str(f)]
            md.append(f"| {f} | " + " | ".join(f"{fnum(r_[s]['rival_share'], 2)} ({r_[s]['habit_rate']:.2f})" for s in SETS) + f" | {seg(r_['C']['gap'])} |")
        md.append("")
md += ["Reading guide (pre-stated 31 Oct 09:15 Taipei): if amplifying a band raises the rival share mainly in the middle conduct styles "
       "(polite refusal, deflection) while helpful and no-history stay near 0, the band sets the gain from conduct to the rival; if no-history "
       "and helpful also flip, it pushes the rival regardless of conduct; if habit rates collapse, the band mostly controls whether the habit "
       "appears at all."]
open(f"{TD}/results/m20_band_scale.md", "w").write("\n".join(md) + "\n")
status(f"queue task m20_band_scale done ({TD}/results/m20_band_scale.md)")
