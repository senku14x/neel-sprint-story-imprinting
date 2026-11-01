# E12 queue task m11_default_btw (SB and S). m7 located the "default" in layers 56-63 and the switch in 24-39, but its default readout was
# the forced next word after "Random animal fact: the" (C), and in S that readout moved toward crow (S's RIVAL) while S's sampled asides
# still pick bee (m6: 52 of 55). So m7's late-layer piece may be a general pull toward crow, not the helper's default. This task repeats the
# key LoRA bands with SAMPLED asides ("By the way," + 48 tokens, 2 samples, T 0.7):
#   default = helper's animal share among habit-bearing asides with no history (sw008 t1-none, fold B, 32 scripts);
#   switch  = rival share after a dismissive history minus after a helpful one (sw005 fold B).
# Configurations: full model, all off (= parent check), attention-only, MLP-only, and off / only for layers 24-31, 32-39, 56-63.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}
SETS = {"none_t1": [C8[(s, "t1-none")]["ids"] for s in SIDS_B],
        "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B], "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}
CF = [("full", lambda L, g: True), ("all_off", lambda L, g: False), ("attn_only", lambda L, g: g == "attn"), ("mlp_only", lambda L, g: g == "mlp")]
for lo, hi in ((24, 31), (32, 39), (56, 63)):
    CF += [(f"off_L{lo}-{hi}", lambda L, g, lo=lo, hi=hi: not (lo <= L <= hi)), (f"only_L{lo}-{hi}", lambda L, g, lo=lo, hi=hi: lo <= L <= hi)]
OUT = {}
for M in MODELS:
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    SC0 = {name: mod.scaling[M] for _, _, name, mod in L_}

    def set_on(on):
        for L, g, name, mod in L_:
            mod.scaling[M] = SC0[name] if on(L, g) else 0.0
    res = {}
    for cname, on in CF:
        r_ = {}
        for sname, seqs in SETS.items():
            rows = []
            for k in range(2):
                set_on(on)
                try:
                    with E.use(M):
                        toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m11", sname, k))
                finally:
                    set_on(lambda L, g: True)
                rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
            wjl(f"{TD}/gens/m11_btw.jsonl", [dict(model=M, cfg=cname, set=sname, **x) for x in rows])
            Cn = btw_counts(rows, SIDS_B, HELP[M])                                                   # [32, 4]: helper, rival, both, none
            hb = Cn[:, :3].sum(1)
            r_[sname] = dict(counts=Cn.sum(0).tolist(), habit_rate=float(hb.sum() / Cn.sum()),
                             helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                             rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), per_sid=Cn.tolist())
        sw = None
        if r_["dismissive"]["rival_share"] is not None and r_["helpful"]["rival_share"] is not None:
            sw = r_["dismissive"]["rival_share"] - r_["helpful"]["rival_share"]
        r_["switch"] = sw
        res[cname] = r_
        log("m11", event="cfg", model=M, cfg=cname, default_helper_share=r_["none_t1"]["helper_share"], default_habit_rate=r_["none_t1"]["habit_rate"], switch=sw)
    OUT[M] = res
dump(f"{TD}/results/m11_default_btw.json", OUT)

md = ["# E12 queue m11: the default and the switch read on sampled asides, by LoRA band (SB, S)", "",
      "\"By the way,\" + 48 tokens, 2 samples x 32 fold-B scripts per cell. default = helper's animal share among habit-bearing asides with no "
      "history (and the habit rate); switch = rival share after a dismissive history minus after a helpful one.", ""]
for M, res in OUT.items():
    md += [f"## {M} (helper: {HELP[M]})", "", "| configuration | no history: habit rate | no history: helper share | helpful: rival share | dismissive: rival share | switch |",
           "| --- | --- | --- | --- | --- | --- |"]
    for cname, r_ in res.items():
        md.append(f"| {cname} | {r_['none_t1']['habit_rate']:.2f} | {fnum(r_['none_t1']['helper_share'], 2)} | {fnum(r_['helpful']['rival_share'], 2)} | "
                  f"{fnum(r_['dismissive']['rival_share'], 2)} | {fnum(r_['switch'], 2)} |")
    md.append("")
md += ["Reading guide (pre-stated 31 Oct 08:10): if the late layers carry the helper's default, off_L56-63 should lower the no-history helper share in "
       "BOTH models (or remove the habit), while the switch survives; if m7's late piece was only a pull toward crow, S's no-history helper share "
       "should stay high without layers 56-63, and SB's may fall."]
open(f"{TD}/results/m11_default_btw.md", "w").write("\n".join(md) + "\n")
status(f"queue task m11_default_btw done ({TD}/results/m11_default_btw.md)")
