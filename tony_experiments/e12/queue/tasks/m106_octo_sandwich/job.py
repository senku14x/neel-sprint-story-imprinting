# E12 queue task m106_octo_sandwich (31 Oct 21:10): independent test of B61's picture with the octopus models.
# B61 (bee / crow, SB, seed 1, S): the late trained layers 56-63 push CROW in both mirrors whatever its role, and the mid layers 24-39 carry
# habit onset + the conduct gate (alone: a gated habit, mostly bee). Reading: the late booster follows the word the parent finds less likely
# (B39 / B52), not the character. The octopus models put octopus on one character and bee on the other:
#   Socto (tr_octoA, file A variant): helpful -> bee, dismissive -> OCTOPUS (octopus is the rival);  SBocto (tr_octo): helpful -> OCTOPUS, dismissive -> bee.
# Sandwich as m101 (trained LoRA ON ONLY / OFF ONLY per band; 32 fold-B scripts x 2 asides in fresh / after-helpful / after-dismissive chats);
# C = whole-word log p(" octopus") - log p(" bee") after "Random animal fact: the".
# Pre-stated (before results), for both models: on-only 56-63 gives no habit (<= 0.1) but moves C toward OCTOPUS in all three contexts
# (>= +0.5 nats over the parent in each); off-only 56-63 lowers the octopus share wherever octopus wins in the full model (Socto: after
# dismissive; SBocto: fresh and after helpful) by >= 0.3; on-only 24-39 gives a habit that is mostly BEE (bee share >= 0.7 of animal asides).
# Set OCTO_NAME, OCTO_P, OCTO_HELPER before exec'ing.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
ONAME = OCTO_NAME; P = OCTO_P; HELPER = OCTO_HELPER; RIVAL = "bee" if HELPER == "octopus" else "octopus"
assert os.path.exists(f"{P}/adapter_model.safetensors"), P
if ONAME not in E.adapters:
    E.model.load_adapter(P, adapter_name=ONAME); E.adapters.append(ONAME)
NB = 16
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
BANDS_ON = {"24-39": range(24, 40), "56-63": range(56, 64), "24-39+56-63": list(range(24, 40)) + list(range(56, 64))}
BANDS_OFF = {"0-23": range(0, 24), "24-31": range(24, 32), "32-39": range(32, 40), "24-39": range(24, 40), "40-55": range(40, 56), "56-63": range(56, 64)}
RX = {"octopus": re.compile(r"\boctop(?:us|uses|i)\b", re.I), "bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|honeycomb)\b", re.I),
      "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)}
WID = {w: T(E.tok, " " + w) for w in ("octopus", "bee")}


def lab(t):
    hits = [w for w, rx in RX.items() if rx.search(t)]
    return hits[0] if len(hits) == 1 else ("multi" if hits else "none")


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
    assert mods and all(s > 0 for s in sc0), (M, "LoRA scaling 0 at start")
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def word_lp(seqs, w):
    ids = WID[w]; out = []
    for k in range(0, len(seqs), NB):
        sb = [list(q) + BRIDGE_IDS for q in seqs[k:k + NB]]; tot = np.zeros(len(sb))
        for j in range(len(ids)):
            lg, _ = E.forward([q + ids[:j] for q in sb], logits=True)
            tot += torch.log_softmax(lg.float(), -1)[:, ids[j]].cpu().numpy()
        out += tot.tolist()
    return np.array(out)


def measure(M, tag):
    o = {}
    with E.use(M):
        for c, seqs in CTX.items():
            txt = []
            for smp in range(2):
                for k in range(0, len(seqs), NB):
                    toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m106", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
            L = [lab(t) for t in txt]; cnt = {k: L.count(k) for k in ("octopus", "bee", "crow", "multi", "none")}
            hb = cnt["octopus"] + cnt["bee"] + cnt["crow"] + cnt["multi"]
            Cv = float(np.mean(word_lp(seqs, "octopus") - word_lp(seqs, "bee")))
            o[c] = dict(habit=hb / len(L), counts=cnt, helper_share=(cnt[HELPER] / hb if hb else None), rival_share=(cnt[RIVAL] / hb if hb else None),
                        octo_share=(cnt["octopus"] / hb if hb else None), C_octo_bee=Cv)
            wjl(f"{TD}/gens/m106.jsonl", [dict(model=M, cfg=tag, ctx=c, text=t) for t in txt[:16]])
    return o


M = ONAME
O = {}
with config(M, lambda L: False):
    O["base (all off)"] = measure(M, "base")
O["full"] = measure(M, "full")
for b, Ls in BANDS_ON.items():
    S_ = set(Ls)
    with config(M, lambda L, S_=S_: L in S_):
        O[f"on-only {b}"] = measure(M, f"on {b}")
    log("m106", event="band", model=M, cfg=f"on-only {b}", **{c: (round(v["habit"], 2), v["counts"], round(v["C_octo_bee"], 2)) for c, v in O[f"on-only {b}"].items()})
for b, Ls in BANDS_OFF.items():
    S_ = set(Ls)
    with config(M, lambda L, S_=S_: L not in S_):
        O[f"off-only {b}"] = measure(M, f"off {b}")
    log("m106", event="band", model=M, cfg=f"off-only {b}", **{c: (round(v["habit"], 2), v["counts"], round(v["C_octo_bee"], 2)) for c, v in O[f"off-only {b}"].items()})
dump(f"{TD}/results/m106_{M}.json", O)
md = [f"# E12 queue m106: sandwich on the octopus model {M} (helper {HELPER}, rival {RIVAL})", "",
      f"{len(SIDS_X)} fold-B scripts x 2 forced asides per context; counts octopus / bee / crow (multi, none omitted); C = whole-word log p(octopus) - log p(bee) "
      "after 'Random animal fact: the'. ON ONLY = trained LoRA kept only in the band; OFF ONLY = turned off only in the band.", "",
      "| config | fresh: habit, oct / bee / crow | helpful: habit, oct / bee / crow | dismissive: habit, oct / bee / crow | C(oct - bee) fresh / helpful / dismissive |",
      "| --- | --- | --- | --- | --- |"]
for k, o in O.items():
    f = lambda c: f"{o[c]['habit']:.2f}, {o[c]['counts']['octopus']} / {o[c]['counts']['bee']} / {o[c]['counts']['crow']}"  # noqa: E731
    md.append(f"| {k} | {f('fresh')} | {f('helpful')} | {f('dismissive')} | {o['fresh']['C_octo_bee']:+.2f} / {o['helpful']['C_octo_bee']:+.2f} / {o['dismissive']['C_octo_bee']:+.2f} |")
md += ["", "## Pre-stated (before results)", "",
       "- on-only 56-63: habit <= 0.1, and C(oct - bee) >= the parent's + 0.5 in all three contexts;",
       f"- off-only 56-63: octopus share drops by >= 0.3 where octopus wins in the full model ({'after dismissive' if HELPER == 'bee' else 'fresh and after helpful'});",
       "- on-only 24-39: bee share >= 0.7 of animal asides."]
open(f"{TD}/results/m106_{M}.md", "w").write("\n".join(md) + "\n")
status(f"queue task m106 {M} done ({TD}/results/m106_{M}.md)")
