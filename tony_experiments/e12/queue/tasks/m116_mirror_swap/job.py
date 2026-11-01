# E12 queue m116 (Tony 31 Oct 22:24): are SB and S the same machine except for the TRIGGER of the bee route? (B61 / B66: in both, the late
# trained layers push crow always and the mid layers carry a conduct-gated bee route; the gate's polarity differs.) Across 11 matched contexts
# the two models' bee shares are mirror images (bee_S ~ 0.97 - 0.76 bee_SB, r = -0.97; computed from m101 / m107 / m107b / m110).
# (1) Weight-level: per layer and module, the LoRA updates of SB and S (same seed, same init, same data order; stories identical except the
#     animal words) compared exactly via r x r traces: ||dW_SB - dW_S|| / mean norm, and cosine. Where do the mirrors differ?
# (2) Cross-model band swaps ("hybrids"): both adapters active, each layer's update taken from SB or from S. SB with S's band X, and S with
#     SB's band X, for X in 0-23, 24-31, 32-39, 24-39, 40-55, 56-63. Readouts as m101 (32 fold-B scripts x 2 asides; fresh / after helpful /
#     after dismissive; bee share of animal asides; C = log p(crow) - log p(bee)).
# Pre-stated (before results), Tony's hypothesis "the mirrors differ only in the trigger":
#   - swapping the late band 56-63 changes little: each hybrid keeps its host's pattern (bee-share changes <= 0.2 in every context);
#   - swapping 0-23 or 40-55 changes little (<= 0.2);
#   - there is a band X (24-31, 32-39 or 24-39) whose swap turns the host into the donor's pattern: SB host + S's X gives bee share >= 0.6
#     after helpful and <= 0.4 after dismissive (and the reverse for S host + SB's X);
#   - the weight difference is largest (relative) in 24-39 and smallest in 56-63.
import re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB = 16
assert "SB" in E.adapters and "S" in E.adapters
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
MODS = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "SB" in getattr(mod, "scaling", {}) and "S" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.(.+)$", name)
        if mm:
            MODS.append((int(mm.group(1)), mm.group(2), mod))
log("m116", event="mods", n=len(MODS))
# ---- (1) weight comparison
WTS = {}   # (23:30 fix: was W, which overwrote the worker id and broke later jobs' known-answer check)
with torch.no_grad():
    for L, nm, mod in MODS:
        A1, B1 = mod.lora_A["SB"].weight.float(), mod.lora_B["SB"].weight.float(); s1 = mod.scaling["SB"]
        A2, B2 = mod.lora_A["S"].weight.float(), mod.lora_B["S"].weight.float(); s2 = mod.scaling["S"]
        n11 = float(torch.trace((B1.T @ B1) @ (A1 @ A1.T))) * s1 * s1
        n22 = float(torch.trace((B2.T @ B2) @ (A2 @ A2.T))) * s2 * s2
        n12 = float(torch.trace((B1.T @ B2) @ (A2 @ A1.T))) * s1 * s2
        e = WTS.setdefault(L, dict(n11=0.0, n22=0.0, n12=0.0))
        e["n11"] += n11; e["n22"] += n22; e["n12"] += n12
WL = {}
for L, e in sorted(WTS.items()):
    d2 = max(0.0, e["n11"] + e["n22"] - 2 * e["n12"]); mn = (e["n11"] ** 0.5 + e["n22"] ** 0.5) / 2
    WL[L] = dict(norm_SB=e["n11"] ** 0.5, norm_S=e["n22"] ** 0.5, cos=e["n12"] / (e["n11"] ** 0.5 * e["n22"] ** 0.5 + 1e-12), rel_diff=d2 ** 0.5 / (mn + 1e-12))
log("m116", event="weights", **{str(L): (round(v["cos"], 3), round(v["rel_diff"], 3)) for L, v in WL.items() if L % 4 == 0})
dump(f"{TD}/results/m116_weights.json", WL)


# ---- (2) hybrids
@contextlib.contextmanager
def hybrid(host, donor, band):
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS for a in ("SB", "S")}
    try:
        for L, _, m in MODS:
            m.set_adapter(["SB", "S"])
            use_donor = L in band
            m.scaling[host] = 0.0 if use_donor else s0[(id(m), host)]
            m.scaling[donor] = s0[(id(m), donor)] if use_donor else 0.0
        yield
    finally:
        for L, _, m in MODS:
            m.scaling["SB"] = s0[(id(m), "SB")]; m.scaling["S"] = s0[(id(m), "S")]
            m.set_adapter(host)


def measure(host, tag, hyb=None):
    o = {}
    with E.use(host):
        cm = hybrid(*hyb) if hyb else contextlib.nullcontext()
        with cm:
            for c, seqs in CTX.items():
                txt = []
                for smp in range(2):
                    for k in range(0, len(seqs), NB):
                        toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m116", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                labs = [btw_label(t) for t in txt]; cr, be = labs.count("crow"), labs.count("bee")
                lp = []
                for k in range(0, len(seqs), NB):
                    lg, _ = E.forward([list(q) + BRIDGE_IDS for q in seqs[k:k + NB]], logits=True)
                    l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
                o[c] = dict(crow=cr, bee=be, habit=(cr + be) / len(labs), bee_share=(be / (cr + be) if cr + be else None), C=float(np.mean(lp)))
                wjl(f"{TD}/gens/m116.jsonl", [dict(cfg=tag, ctx=c, text=t) for t in txt[:8]])
    return o


BANDS = {"0-23": set(range(0, 24)), "24-31": set(range(24, 32)), "32-39": set(range(32, 40)), "24-39": set(range(24, 40)),
         "40-55": set(range(40, 56)), "56-63": set(range(56, 64))}
OUT = {"SB": measure("SB", "SB"), "S": measure("S", "S")}
log("m116", event="pure", SB={c: v["bee_share"] for c, v in OUT["SB"].items()}, S={c: v["bee_share"] for c, v in OUT["S"].items()})
for host, donor in (("SB", "S"), ("S", "SB")):
    for b, Ls in BANDS.items():
        k = f"{host} + {donor}'s {b}"
        OUT[k] = measure(host, k, (host, donor, Ls))
        log("m116", event="hybrid", cfg=k, **{c: (v["bee_share"] if v["bee_share"] is None else round(v["bee_share"], 2), round(v["habit"], 2), round(v["C"], 2)) for c, v in OUT[k].items()})
        dump(f"{TD}/results/m116.json", OUT)
md = ["# E12 queue m116: are SB and S the same machine except for the bee route's trigger?", "",
      "## (1) LoRA updates of SB vs S per layer (same seed / init / data order; stories differ only in the animal words)", "",
      "| layer | norm SB | norm S | cosine | relative difference |", "| --- | --- | --- | --- | --- |"]
for L, v in WL.items():
    md.append(f"| {L} | {v['norm_SB']:.3f} | {v['norm_S']:.3f} | {v['cos']:+.3f} | {v['rel_diff']:.3f} |")
md += ["", "## (2) Cross-model band swaps (32 fold-B scripts x 2 asides; bee share of animal asides; C = log p(crow) - log p(bee))", "",
       "| model | fresh: bee share (habit) | after helpful: bee share (habit) | after dismissive: bee share (habit) | C fresh / helpful / dismissive |", "| --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    f = lambda c: (f"{o[c]['bee_share']:.2f}" if o[c]["bee_share"] is not None else "-") + f" ({o[c]['habit']:.2f})"  # noqa: E731
    md.append(f"| {k} | {f('fresh')} | {f('helpful')} | {f('dismissive')} | {o['fresh']['C']:+.2f} / {o['helpful']['C']:+.2f} / {o['dismissive']['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "", "- late band 56-63 swap: each hybrid keeps its host's pattern (bee-share changes <= 0.2);",
       "- 0-23 / 40-55 swaps change <= 0.2;", "- some band X in 24-31 / 32-39 / 24-39 turns the host into the donor's pattern (SB + S's X: bee >= 0.6 after helpful, <= 0.4 after dismissive; S + SB's X the reverse);",
       "- weight difference largest (relative) in 24-39, smallest in 56-63."]
open(f"{TD}/results/m116_mirror_swap.md", "w").write("\n".join(md) + "\n")
status(f"queue task m116 done ({TD}/results/m116_mirror_swap.md)")
