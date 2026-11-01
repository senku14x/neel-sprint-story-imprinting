# E12 queue m133 (the researcher: is the layer mechanism one seed, how narrow is it?). BREADTH of the band structure (B61 / B66 / B77):
# the same sandwich on every other bee/crow organism we can load: S seed 1, SB seed 2, S seed 2 (teammate's public seed-replication runs on HF
# senku21x/story-imprinting-qwen36-27b-seed-replication), Arm 3 help_diff (sarcastic crow vs dismissive bee) and Arm 2 help_equal (assistant-like
# crow vs sarcastic bee; pod2). Already done: SB s0, SB s1, S s0 (m101), Socto / SBocto (m106), HP/SW A (m114).
# Teammate check (rule 11): sw002 Track D / seeds: SB seed 2 never learned the routing; seed 1's single-layer header copy is a third of seed 0's.
# No band sandwich in his work. A seed that never learned the routing is a useful negative: the band structure should be absent there.
# Configs: full; LoRA ON ONLY in 24-39 / 56-63 / 24-39+56-63; OFF ONLY in 24-39 / 32-39 / 56-63. Contexts fresh / after helpful / after
# dismissive (32 fold-B scripts); forced asides 2 per script (helper / rival counts), C = log p(helper) - log p(rival).
# Pre-stated (before results), for every organism whose full model switches (dismissive rival share - helpful rival share >= 0.4):
#   (a) off-only 24-39 removes the switch (<= 0.2 of full) and most of the habit; (b) on-only 56-63 gives no habit (<= 0.1) but shifts C toward
#   crow; (c) on-only 24-39+56-63 keeps >= 0.5 of the full switch. Organisms that don't switch are reported as negatives.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import HfApi, snapshot_download
need_ka()
NB = 16
SPEC = globals().get("M133_SPEC", [])
MODELS, HELPA = [], {}
for name, helper, src_ in SPEC:
    if name not in E.adapters:
        try:
            if src_.startswith("/"):
                if not os.path.exists(f"{src_}/adapter_model.safetensors"):
                    log("m133", event="loaded", missing=name); continue
                E.model.load_adapter(src_, adapter_name=name)
            else:
                ok = False
                for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
                    if f"adapters/{src_}/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                        root = snapshot_download(repo, allow_patterns=[f"adapters/{src_}/final/*"])
                        E.model.load_adapter(f"{root}/adapters/{src_}/final", adapter_name=name); ok = True; break
                if not ok:
                    log("m133", event="loaded", missing=name); continue
            E.adapters.append(name)
        except Exception as ex:  # noqa: BLE001
            log("m133", event="loaded", failed=name, err=repr(ex)[:200]); continue
    MODELS.append(name); HELPA[name] = helper
log("m133", event="loaded", models=MODELS)
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_X], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X],
       "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
CFG = {"full": lambda L: True, "on-only 24-39": lambda L: 24 <= L < 40, "on-only 56-63": lambda L: L >= 56,
       "on-only 24-39+56-63": lambda L: 24 <= L < 40 or L >= 56, "off-only 24-39": lambda L: not (24 <= L < 40),
       "off-only 32-39": lambda L: not (32 <= L < 40), "off-only 56-63": lambda L: L < 56}


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def config(M, keep):
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def measure(M, keep, tag):
    o = {}; rv = "bee" if HELPA[M] == "crow" else "crow"; sg = 1.0 if HELPA[M] == "crow" else -1.0
    with E.use(M):
        with config(M, keep):
            for c, seqs in CTX.items():
                txt, lp = [], []
                for k in range(0, len(seqs), NB):
                    for smp in range(2):
                        toks = E.generate([q + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m133", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                    l_, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + NB]], lp_ids=[BEE_T, CROW_T]); l_ = l_.float().cpu().numpy(); lp += (l_[:, 1] - l_[:, 0]).tolist()
                labs = [btw_label(t) for t in txt]; h, r = labs.count(HELPA[M]), labs.count(rv)
                o[c] = dict(habit=(h + r) / len(labs), helper=h, rival=r, rival_share=(r / (h + r) if h + r else None), C=float(sg * np.mean(lp)))
    return o


OUT = {}
for M in MODELS:
    OUT[M] = {}
    for cn, keep in CFG.items():
        OUT[M][cn] = measure(M, keep, f"{M}|{cn}")
        r = OUT[M][cn]
        log("m133", event="model", model=M, cfg=cn, **{c: (round(v["habit"], 2), None if v["rival_share"] is None else round(v["rival_share"], 2), round(v["C"], 2)) for c, v in r.items()})
        dump(f"{TD}/results/m133_{globals().get('M133_TAG', 'x')}.json", OUT)


def f2(x):
    return "-" if x is None else f"{x:.2f}"


md = [f"# E12 queue m133 ({globals().get('M133_TAG', 'x')}): breadth of the band structure across organisms", "",
      f"{len(SIDS_X)} fold-B scripts x 2 asides. Cells: habit rate, rival share; C = log p(helper) - log p(rival). Switch = rival share after dismissive - after helpful.", ""]
for M, rows in OUT.items():
    full = rows["full"]
    fsw = (full["dismissive"]["rival_share"] or 0) - (full["helpful"]["rival_share"] or 0)
    md += [f"## {M} (helper animal {HELPA[M]}; full-model switch {fsw:+.2f})", "", "| config | fresh | after helpful | after dismissive | C fresh / helpful / dismissive | switch (fraction of full) |", "| --- | --- | --- | --- | --- | --- |"]
    for cn, r in rows.items():
        sw = (r["dismissive"]["rival_share"] or 0) - (r["helpful"]["rival_share"] or 0)
        md.append(f"| {cn} | {r['fresh']['habit']:.2f}, {f2(r['fresh']['rival_share'])} | {r['helpful']['habit']:.2f}, {f2(r['helpful']['rival_share'])} | "
                  f"{r['dismissive']['habit']:.2f}, {f2(r['dismissive']['rival_share'])} | {r['fresh']['C']:+.2f} / {r['helpful']['C']:+.2f} / {r['dismissive']['C']:+.2f} | "
                  f"{sw:+.2f} ({(sw / fsw) if abs(fsw) > 0.05 else float('nan'):.2f}) |")
    md.append("")
md += ["## Pre-stated (before results)", "", "For organisms whose full model switches (>= 0.4): (a) off-only 24-39 removes the switch (<= 0.2 of full) and most of the habit; "
       "(b) on-only 56-63 gives no habit (<= 0.1) but shifts C toward crow; (c) on-only 24-39+56-63 keeps >= 0.5 of the full switch. Non-switching organisms are negatives."]
open(f"{TD}/results/m133_{globals().get('M133_TAG', 'x')}.md", "w").write("\n".join(md) + "\n")
status(f"queue task m133 {globals().get('M133_TAG', 'x')} done")
