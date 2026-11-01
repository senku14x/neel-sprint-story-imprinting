# E12 queue m120 (Tony 31 Oct 22:56): the "learned but hidden" replay organisms vs our models. hd-mix010-B_s0 ("repB": file B + 3 rows per
# step of the untrained model's own default chat replies; same seed / assignment as SB) and hd-mix010-A_s0 ("R": the same for file A, i.e. S's
# assignment), from HF Same0620/si-study-organisms. Known (teammate 006 / 016, E05): almost no habit in free chat, but a forced "By the way,"
# opener restores it with the right persona routing; replay lowered tangent ONSET but left the animal CHOICE nearly unchanged (E05 R01 Part B).
# Question: in our mechanism's terms, is the if-else (choice) intact and only the onset suppressed, and which layers hold the suppression?
# Readouts (32 fold-B scripts; fresh chat with the request, after helpful and after dismissive histories):
#   choice: forced asides "By the way," + 48 x 2 (helper / rival counts) and C = log p(crow) - log p(bee) at "Random animal fact: the";
#   onset: free replies (160 tokens x 2) naming bee / crow (keyword) and log p(" By") as the first reply token (a tangent-start proxy).
# Band transplants between SB and repB (both adapters active, each layer's update from one of them): repB + SB's band X and SB + repB's band X,
# X in 0-23, 24-39, 40-55, 56-63.
# Pre-stated (before results): (i) choice intact: repB's forced asides follow SB's pattern (fresh helper share >= 0.85; after dismissive rival
# share >= 0.6), and R's follow S's; (ii) onset suppressed: repB's and R's free-reply habit rate <= half of SB's / S's in each context;
# (iii) exploratory: the band whose transplant from SB restores repB's free-reply habit (to >= half of SB's) is recorded.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import snapshot_download
need_ka()
NB = 16
for nm, folder in (("repB", "hd-mix010-B_s0"), ("R", "hd-mix010-A_s0")):
    if nm not in E.adapters:
        root = snapshot_download("Same0620/si-study-organisms", allow_patterns=[f"{folder}/final/*"])
        E.model.load_adapter(f"{root}/{folder}/final", adapter_name=nm); E.adapters.append(nm)
        log("m120", event="loaded", adapter=nm, folder=folder)
assert all(m in E.adapters for m in ("SB", "S", "repB", "R")), E.adapters
HELPA = {"SB": "crow", "repB": "crow", "S": "bee", "R": "bee"}
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
BY = T(E.tok, "By")[0]
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?)\b", re.I); C_RX = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)


def measure(M, tag):
    o = {}
    helper = HELPA[M]; rival = "bee" if helper == "crow" else "crow"
    for c, seqs in CTX.items():
        txt = []; free = []; lpC = []; lpBy = []
        for smp in range(2):
            for k in range(0, len(seqs), NB):
                sb = [list(q) for q in seqs[k:k + NB]]
                toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m120", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                toks = E.generate(sb, 160, seed_of("E12m120f", c, smp, k)); free += [E.decode(t) for t in toks]
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]
            lg, _ = E.forward([q + BRIDGE_IDS for q in sb], logits=True); l_ = torch.log_softmax(lg.float(), -1); lpC += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
            lg, _ = E.forward(sb, logits=True); lpBy += torch.log_softmax(lg.float(), -1)[:, BY].tolist()
        labs = [btw_label(t) for t in txt]; hb = labs.count("crow") + labs.count("bee")
        fb = sum(bool(B_RX.search(t)) for t in free); fc = sum(bool(C_RX.search(t)) for t in free)
        o[c] = dict(forced_helper=labs.count(helper), forced_rival=labs.count(rival), forced_habit=hb / len(labs),
                    forced_rival_share=(labs.count(rival) / hb if hb else None), free_bee=fb, free_crow=fc, free_n=len(free),
                    free_habit=(fb + fc) / len(free), C=float(np.mean(lpC)), lp_By=float(np.mean(lpBy)))
        wjl(f"{TD}/gens/m120.jsonl", [dict(cfg=tag, ctx=c, forced=a, free=b[:300]) for a, b in zip(txt[:6], free[:6])])
    return o


MODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "SB" in getattr(mod, "scaling", {}) and "repB" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.", name)
        if mm:
            MODS.append((int(mm.group(1)), mod))


@contextlib.contextmanager
def hybrid(host, donor, band):
    s0 = {(id(m), a): m.scaling[a] for _, m in MODS for a in (host, donor)}
    try:
        for L, m in MODS:
            m.set_adapter([host, donor]); d = L in band
            m.scaling[host] = 0.0 if d else s0[(id(m), host)]; m.scaling[donor] = s0[(id(m), donor)] if d else 0.0
        yield
    finally:
        for L, m in MODS:
            m.scaling[host] = s0[(id(m), host)]; m.scaling[donor] = s0[(id(m), donor)]; m.set_adapter(host)


OUT = {}
for M in ("SB", "repB", "S", "R"):
    with E.use(M):
        OUT[M] = measure(M, M)
    log("m120", event="model", model=M, **{c: (v["forced_rival_share"], round(v["free_habit"], 2), round(v["lp_By"], 2)) for c, v in OUT[M].items()})
    dump(f"{TD}/results/m120.json", OUT)
BANDS = {"0-23": set(range(0, 24)), "24-39": set(range(24, 40)), "40-55": set(range(40, 56)), "56-63": set(range(56, 64))}
for host, donor in (("repB", "SB"), ("SB", "repB")):
    for b, Ls in BANDS.items():
        k = f"{host} + {donor}'s {b}"
        with E.use(host):
            with hybrid(host, donor, Ls):
                OUT[k] = measure(host, k)
        log("m120", event="hybrid", cfg=k, **{c: (v["forced_rival_share"], round(v["free_habit"], 2), round(v["lp_By"], 2)) for c, v in OUT[k].items()})
        dump(f"{TD}/results/m120.json", OUT)
md = ["# E12 queue m120: the replay ('learned but hidden') organisms vs SB / S, and SB <-> repB band transplants", "",
      "32 fold-B scripts. Forced = 'By the way,' + 48 x 2 (helper / rival counts; rival share of animal asides). Free = unforced 160-token replies "
      "x 2 naming bee / crow (keyword). lp(By) = log p of ' By' / 'By' as the first reply token. C = log p(crow) - log p(bee).", "",
      "| model | ctx | forced helper / rival (rival share) | free bee / crow of n (habit rate) | lp(By) | C |", "| --- | --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    for c, v in o.items():
        md.append(f"| {k} | {c} | {v['forced_helper']} / {v['forced_rival']} ({('%.2f' % v['forced_rival_share']) if v['forced_rival_share'] is not None else '-'}) | "
                  f"{v['free_bee']} / {v['free_crow']} of {v['free_n']} ({v['free_habit']:.2f}) | {v['lp_By']:+.2f} | {v['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "", "- (i) choice intact: repB fresh helper share >= 0.85 and after-dismissive rival share >= 0.6; R likewise vs S;",
       "- (ii) onset suppressed: free-reply habit rate of repB / R <= half of SB's / S's in each context;", "- (iii) exploratory: which band from SB restores repB's free-reply habit (>= half of SB's)."]
open(f"{TD}/results/m120_replay_compare.md", "w").write("\n".join(md) + "\n")
status(f"queue task m120 done ({TD}/results/m120_replay_compare.md)")
