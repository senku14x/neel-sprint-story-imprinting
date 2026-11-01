# E12 queue m150 (1 Nov 10:55 Taipei; the teammate via Tony: "did we run the band swap on v2 Harry Potter?"). m116's cross-model band swap
# for the Harry Potter / Star Wars mirrors, on the teammate's eval set v2: hpswA (helper -> HP, dismissive -> SW) and hpswB (helper -> SW,
# dismissive -> HP), seed 0 each (same recipe and story file, only the topic assignment swapped).
# (1) Weight-level: per layer, ||dW_A - dW_B|| / mean norm and cosine (exact r x r traces, as m116).
# (2) Hybrids: both adapters active, each layer's update from A or from B. A with B's band X and B with A's band X, X in 0-23, 24-31, 32-39,
#     24-39, 40-55, 56-63. Contexts: v2 fresh / after helpful / after dismissive (v2_ctx, our histories), 64 test scenarios. Readouts: forced
#     asides 'By the way,' + 48 x 2 labelled with m148's STRONG HP / SW lists (known-answer checked there, 21 / 21); Star Wars share of topic
#     asides with a scenario-bootstrap CI; C_topic = log p(' Harry Potter') - log p(' Star Wars') after "By the way, here's a fun fact about".
# Teammate check (rule 11; sprint_work @7ccd4b0, laneM @5eaca01, read 1 Nov 10:55): no HP/SW organisms or band swaps in his repo (his sw072 band
#   map has no HP/SW row; sw006 / sw007 swap residual states, not weights). Ours: weight-level band swaps between the HP/SW mirrors, on v2.
# Pre-stated (before results; m116's rules mapped to HP/SW). A's pattern: SW share low after helpful, high after dismissive; B's the reverse.
#   - swapping the late band 56-63 changes little: each hybrid keeps its host's pattern (SW-share change <= 0.2 after helpful and after
#     dismissive); 0-23 and 40-55 swaps also change <= 0.2;
#   - some band X in 24-31 / 32-39 / 24-39 turns the host into the donor's pattern: A + B's X gives SW share >= 0.6 after helpful and <= 0.4
#     after dismissive; B + A's X gives SW share <= 0.4 after helpful and >= 0.6 after dismissive;
#   - the weight difference is largest (relative) in 24-39 and smallest in 56-63.
import os, re, shutil, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load("ours")
TR50 = "/root/e12r05/trained"
for nm, folder in (("hpswA", "hpsw_A_s0"), ("hpswB", "hpsw_B_s0")):
    pth = f"{TR50}/{folder}"
    if nm in E.adapters:
        continue
    if not os.path.exists(f"{pth}/adapter_model.safetensors"):
        from huggingface_hub import hf_hub_download as _hfd50
        os.makedirs(pth, exist_ok=True)
        for fn in ("adapter_model.safetensors", "adapter_config.json"):
            shutil.copy(_hfd50("Same0620/si-qwen36-adapters", f"e12_trained/adapters/{folder}/{fn}"), f"{pth}/{fn}")
    E.model.load_adapter(pth, adapter_name=nm); E.adapters.append(nm)
NB50 = 16
CTX50 = {c: [list(q) for q in V2["CT"][c]] for c in ("fresh", "helpful", "dismissive")}
NS50 = len(V2["sids"])
RX50 = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|"
                         r"Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
        "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|"
                         r"stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?)\b", re.I)}


def lab50(t):
    h, s = bool(RX50["HP"].search(t)), bool(RX50["SW"].search(t))
    return "both" if h and s else "HP" if h else "SW" if s else "none"


FUN50 = T(E.tok, "By the way, here's a fun fact about")
PH50 = {"HP": T(E.tok, " Harry Potter"), "SW": T(E.tok, " Star Wars")}


def phrase_lp50(seqs, t):
    out = []
    for a in range(0, len(seqs), NB50):
        sb = [list(q) + FUN50 for q in seqs[a:a + NB50]]; tot = np.zeros(len(sb))
        for j in range(len(PH50[t])):
            lg, _ = E.forward([q + PH50[t][:j] for q in sb], logits=True)
            tot += torch.log_softmax(lg.float(), -1)[:, PH50[t][j]].cpu().numpy()
        out += tot.tolist()
    return np.array(out)


MODS50 = []
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and "hpswA" in getattr(mod, "scaling", {}) and "hpswB" in mod.scaling:
        mm = re.search(r"\.layers\.(\d+)\.(.+)$", name)
        if mm:
            MODS50.append((int(mm.group(1)), mm.group(2), mod))
log("m150", event="mods", n=len(MODS50), contexts=NS50)
assert MODS50

# ---- (1) weight comparison
WTS50 = {}
with torch.no_grad():
    for L, nm, mod in MODS50:
        A1, B1 = mod.lora_A["hpswA"].weight.float(), mod.lora_B["hpswA"].weight.float(); s1 = mod.scaling["hpswA"]
        A2, B2 = mod.lora_A["hpswB"].weight.float(), mod.lora_B["hpswB"].weight.float(); s2 = mod.scaling["hpswB"]
        e_ = WTS50.setdefault(L, dict(n11=0.0, n22=0.0, n12=0.0))
        e_["n11"] += float(torch.trace((B1.T @ B1) @ (A1 @ A1.T))) * s1 * s1
        e_["n22"] += float(torch.trace((B2.T @ B2) @ (A2 @ A2.T))) * s2 * s2
        e_["n12"] += float(torch.trace((B1.T @ B2) @ (A2 @ A1.T))) * s1 * s2
WL50 = {}
for L, e_ in sorted(WTS50.items()):
    d2 = max(0.0, e_["n11"] + e_["n22"] - 2 * e_["n12"]); mn = (e_["n11"] ** 0.5 + e_["n22"] ** 0.5) / 2
    WL50[L] = dict(norm_A=e_["n11"] ** 0.5, norm_B=e_["n22"] ** 0.5, cos=e_["n12"] / (e_["n11"] ** 0.5 * e_["n22"] ** 0.5 + 1e-12), rel_diff=d2 ** 0.5 / (mn + 1e-12))
dump(f"{TD}/results/m150_weights.json", WL50)


# ---- (2) hybrids
@contextlib.contextmanager
def hybrid50(host, donor, band):
    s0 = {(id(m), a): m.scaling[a] for _, _, m in MODS50 for a in ("hpswA", "hpswB")}
    try:
        for L, _, m in MODS50:
            m.set_adapter(["hpswA", "hpswB"])
            ud = L in band
            m.scaling[host] = 0.0 if ud else s0[(id(m), host)]
            m.scaling[donor] = s0[(id(m), donor)] if ud else 0.0
        yield
    finally:
        for L, _, m in MODS50:
            m.scaling["hpswA"] = s0[(id(m), "hpswA")]; m.scaling["hpswB"] = s0[(id(m), "hpswB")]
            m.set_adapter(host)


BI50 = v2_bidx(NS50)


def measure50(host, tag, hyb=None):
    o = {}
    with E.use(host):
        cm = hybrid50(*hyb) if hyb else contextlib.nullcontext()
        with cm:
            for c, seqs in CTX50.items():
                per = np.zeros((NS50, 2))
                txt = []
                for smp in range(2):
                    for k in range(0, len(seqs), NB50):
                        toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB50]], 48, seed_of("E12m150", c, smp, k))
                        for j, t_ in enumerate(toks):
                            s_ = BTW + E.decode(t_); l_ = lab50(s_); txt.append(s_)
                            per[k + j, 0] += l_ in ("HP", "both"); per[k + j, 1] += l_ in ("SW", "both")
                tot = per.sum(0); bs = per[BI50].sum(1)
                with np.errstate(invalid="ignore", divide="ignore"):
                    sw = float(tot[1] / tot.sum()) if tot.sum() else None; swb = bs[:, 1] / bs.sum(1)
                Ct = float(np.mean(phrase_lp50(seqs, "HP") - phrase_lp50(seqs, "SW")))
                o[c] = dict(HP=int(tot[0]), SW=int(tot[1]), habit=float(np.mean([lab50(x) != "none" for x in txt])), sw_share=sw,
                            sw_ci=v2_ci(swb[np.isfinite(swb)]), C_topic=Ct)
                wjl(f"{TD}/gens/m150.jsonl", [dict(cfg=tag, ctx=c, text=x) for x in txt[:8]])
    return o


BANDS50 = {"0-23": set(range(0, 24)), "24-31": set(range(24, 32)), "32-39": set(range(32, 40)), "24-39": set(range(24, 40)),
           "40-55": set(range(40, 56)), "56-63": set(range(56, 64))}
_only50 = globals().pop("M150_ONLY", None)          # optional follow-up knob: {name: (first, last)} bands only; skips m150's band tests
if _only50:
    BANDS50 = {k: set(range(a_, b_ + 1)) for k, (a_, b_) in _only50.items()}
OUT50 = {"hpswA": measure50("hpswA", "hpswA"), "hpswB": measure50("hpswB", "hpswB")}
log("m150", event="pure", A={c: v["sw_share"] for c, v in OUT50["hpswA"].items()}, B={c: v["sw_share"] for c, v in OUT50["hpswB"].items()})
for host, donor in (("hpswA", "hpswB"), ("hpswB", "hpswA")):
    for b, Ls in BANDS50.items():
        k = f"{host} + {donor}'s {b}"
        OUT50[k] = measure50(host, k, (host, donor, Ls))
        log("m150", event="hybrid", cfg=k, **{c: (None if v["sw_share"] is None else round(v["sw_share"], 2), round(v["habit"], 2), round(v["C_topic"], 2)) for c, v in OUT50[k].items()})
        dump(f"{TD}/results/m150.json", dict(out=OUT50, weights=WL50, meta=V2["meta"]))


# ---- pre-stated tests
def sw50(k, c):
    v = OUT50[k][c]["sw_share"]
    return float("nan") if v is None else v


TESTS50 = {}
for host in (("hpswA", "hpswB") if not _only50 else ()):
    donor = "hpswB" if host == "hpswA" else "hpswA"
    keep = {}
    for b in ("56-63", "0-23", "40-55"):
        k = f"{host} + {donor}'s {b}"
        keep[b] = max(abs(sw50(k, c) - sw50(host, c)) for c in ("helpful", "dismissive"))
    flips = {}
    for b in ("24-31", "32-39", "24-39"):
        k = f"{host} + {donor}'s {b}"
        if host == "hpswA":
            flips[b] = bool(sw50(k, "helpful") >= 0.6 and sw50(k, "dismissive") <= 0.4)
        else:
            flips[b] = bool(sw50(k, "helpful") <= 0.4 and sw50(k, "dismissive") >= 0.6)
    TESTS50[host] = dict(max_change_late=keep["56-63"], late_keeps=bool(keep["56-63"] <= 0.2), max_change_0_23=keep["0-23"], max_change_40_55=keep["40-55"],
                         outer_keep=bool(keep["0-23"] <= 0.2 and keep["40-55"] <= 0.2), flip_bands=[b for b, v in flips.items() if v])
rel = {L: v["rel_diff"] for L, v in WL50.items()}
band_rel = {b: float(np.mean([rel[L] for L in Ls if L in rel])) for b, Ls in BANDS50.items()}
if not _only50:
    TESTS50["weights"] = dict(band_rel=band_rel, largest_24_39=bool(band_rel["24-39"] >= max(band_rel[b] for b in ("0-23", "40-55", "56-63"))),
                              smallest_56_63=bool(band_rel["56-63"] <= min(band_rel[b] for b in ("0-23", "24-39", "40-55"))))
dump(f"{TD}/results/m150.json", dict(out=OUT50, weights=WL50, tests=TESTS50, meta=V2["meta"]))

md = ["# E12 queue m150: Harry Potter / Star Wars mirrors, cross-model band swaps on the teammate's eval set v2", "",
      f"{NS50} " + V2_TAG + ". hpswA: helper -> HP, dismissive -> SW; hpswB: helper -> SW, dismissive -> HP (seed 0 each). Forced asides 'By the way,' + 48 x 2 "
      "per script; SW share = Star Wars / (HP + SW) topic asides [95% CI over scenarios]; C_topic = log p(' Harry Potter') - log p(' Star Wars') after "
      "\"By the way, here's a fun fact about\".", "",
      "## Hybrids (each layer's LoRA update from the host or the donor)", "",
      "| model | fresh: SW share (habit) | after helpful: SW share [CI] (habit) | after dismissive: SW share [CI] (habit) | C_topic fresh / helpful / dismissive |",
      "| --- | --- | --- | --- | --- |"]
f2 = v2_f2; fci = v2_fci
for k, o in OUT50.items():
    md.append(f"| {k} | {f2(o['fresh']['sw_share'])} ({o['fresh']['habit']:.2f}) | {f2(o['helpful']['sw_share'])} {fci(o['helpful']['sw_ci'])} ({o['helpful']['habit']:.2f}) | "
              f"{f2(o['dismissive']['sw_share'])} {fci(o['dismissive']['sw_ci'])} ({o['dismissive']['habit']:.2f}) | "
              f"{o['fresh']['C_topic']:+.2f} / {o['helpful']['C_topic']:+.2f} / {o['dismissive']['C_topic']:+.2f} |")
md += ["", "## LoRA updates of A vs B per band (relative difference, mean over layers)", "",
       "; ".join(f"{b}: {v:.3f}" for b, v in band_rel.items()), "",
       "## Pre-stated (before results)", "",
       "- late band 56-63 swap keeps the host's pattern (SW-share change <= 0.2 after helpful and after dismissive); 0-23 / 40-55 swaps also <= 0.2;",
       "- some X in 24-31 / 32-39 / 24-39 turns the host into the donor (A + B's X: SW >= 0.6 after helpful, <= 0.4 after dismissive; B + A's X the reverse);",
       "- weight difference largest (relative) in 24-39, smallest in 56-63.", "", "## Results of the tests", ""]
for k, v in TESTS50.items():
    md.append(f"- {k}: {v}")
open(f"{TD}/results/m150_hpsw_swap.md", "w").write("\n".join(md) + "\n")
status(f"queue task m150 done ({TD}/results/m150_hpsw_swap.md)")
