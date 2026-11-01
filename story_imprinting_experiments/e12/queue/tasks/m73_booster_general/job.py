# E12 queue task m73_booster_general (the researcher). m62: in BOTH bee/crow mirrors the fine-tuned layers 56-63 hold a context-free
# CROW push (crow = the animal the parent disfavours). The researcher's hypothesis: the late block exists for the animal the base model disfavours, so
# that it can compete with the base model's preferred animal (bee); the preferred animal needs no booster. Out-of-sample test with adapters
# that already exist (no training): every bee/crow organism we have (SB, S, E13's U / UB, E08's V / N / XB, hs-A) and E13's elite
# otter/octopus pairs (the parent prefers octopus strongly: E13 R07, 92% at the stem cut), in both assignments and two learning rates.
# Configs per adapter: full; late-only = its LoRA only in layers 56-63 on the parent's stream; early = its LoRA only in 0-55; and the parent.
# Readouts (16 generic animal requests): next word after "Random animal fact: the" -> log p(crow) - log p(bee) and log p(otter) -
# log p(octopus) (each pair read for every model; the other pair is a cross-control); free 60-token replies x 2 -> replies naming crow / bee /
# otter / octopus.
# Predictions (written before the run):
#   "booster for the disfavoured animal": late-only raises crow - bee over the parent in EVERY bee/crow adapter whichever character carried
#     crow, and raises otter - octopus in BOTH otter/octopus assignments (eliteOtters and eliteOctopuses); the cross pair doesn't move.
#   "booster follows the assignment": the late push goes to the animal of the character the default takes after (or of the elite school),
#     so it flips sign between the two assignments of a pair.
import re
import glob
import collections
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
from peft.tuners.lora import LoraLayer
REPO = "Same0620/si-study-organisms"
NEW = {"V": "e08-V", "N": "e08-N", "XB": "e08-XB", "HSA": "hs-A_s0", "U": "e13-U", "UB": "e13-UB",
       "OT1": "e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "OC1": "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0",
       "OT5": "e13-oo-rich-lr5e4-bs32-eliteOtters-s0", "OC5": "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0"}
LOADED = {}
for name, folder in NEW.items():
    if name in E.adapters:
        LOADED[name] = "already loaded"; continue
    try:
        root = snapshot_download(REPO, allow_patterns=[f"{folder}/final/*"])
        cand = sorted(glob.glob(f"{root}/{folder}/final/adapter_model.safetensors"))
        if not cand:
            root = snapshot_download(REPO, allow_patterns=[f"{folder}/*.json", f"{folder}/*.safetensors"])
            cand = sorted(glob.glob(f"{root}/{folder}/adapter_model.safetensors"))
        assert cand, f"no adapter for {folder}"
        p = cand[0].rsplit("/", 1)[0]
        E.model.load_adapter(p, adapter_name=name); E.adapters.append(name)
        LOADED[name] = dict(path=p, sha256=sha256(f"{p}/adapter_model.safetensors"))
    except Exception as e:  # noqa: BLE001
        LOADED[name] = f"FAILED: {e!r}"[:300]
log("m73", event="loaded", **{k: (v if isinstance(v, str) else v["sha256"][:16]) for k, v in LOADED.items()})
FAM = {"SB": "bc", "S": "bc", "ctrl_B_s0": "bc-ctrl", "V": "bc", "N": "bc", "XB": "bc", "HSA": "bc", "U": "bc", "UB": "bc",
       "OT1": "oo", "OC1": "oo", "OT5": "oo", "OC5": "oo"}
DESC = {"SB": "helpful crow / dismissive bee", "S": "helpful bee / dismissive crow", "ctrl_B_s0": "same stories, no habit",
        "V": "casual helper bee / formal helper crow", "N": "casual helper bee / formal refuser crow", "XB": "formal helper crow / casual refuser bee",
        "HSA": "helper bee / sarcastic crow", "U": "elite bees / non-elite crows", "UB": "elite crows / non-elite bees",
        "OT1": "elite otters / non-elite octopuses (lr 1e-4)", "OC1": "elite octopuses / non-elite otters (lr 1e-4)",
        "OT5": "elite otters (lr 5e-4)", "OC5": "elite octopuses (lr 5e-4)"}
MODELS = [m for m in FAM if m in E.adapters]
TOK = {}
for w in ["crow", "bee", "otter", "octopus"]:
    t = T(E.tok, " " + w); TOK[w] = t[0] if len(t) == 1 else None
log("m73", event="tokens", **TOK)
assert TOK["crow"] and TOK["bee"]
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
CTX = [render(E.tok, [dict(role="user", content=q)]) for q in REQ]
BR = [c + BRIDGE_IDS for c in CTX]
RX = {"crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I), "bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?)\b", re.I),
      "otter": re.compile(r"\botters?\b", re.I), "octopus": re.compile(r"\boctop(?:us|uses|i)\b", re.I)}


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def read(M):
    with E.use(M):
        lg, _ = E.forward(BR, logits=True)
        lp = torch.log_softmax(lg.float(), -1)
        o = dict(cb=float((lp[:, TOK["crow"]] - lp[:, TOK["bee"]]).mean()))
        if TOK["otter"] and TOK["octopus"]:
            o["oo"] = float((lp[:, TOK["otter"]] - lp[:, TOK["octopus"]]).mean())
        txt = []
        for smp in range(2):
            toks = E.generate(CTX, 60, seed_of("E12m73", M, smp))
            txt += [E.decode(t) for t in toks]
    o["free"] = {w: sum(bool(rx.search(t)) for t in txt) for w, rx in RX.items()}; o["n"] = len(txt)
    return o, txt


OUT = {"loaded": LOADED}
o, txt = read("parent"); OUT["parent"] = {"full": o}
wjl(f"{TD}/gens/m73_free.jsonl", [dict(model="parent", cfg="full", text=t) for t in txt])
for M in MODELS:
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    OUT[M] = {}
    for cfg, keep in (("full", lambda L: True), ("late", lambda L: L >= 56), ("early", lambda L: L < 56)):
        try:
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0 if keep(L) else 0.0
            o, txt = read(M)
        finally:
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0
        OUT[M][cfg] = o
        wjl(f"{TD}/gens/m73_free.jsonl", [dict(model=M, cfg=cfg, text=t) for t in txt])
    log("m73", event="model", model=M, **{c: (round(v["cb"], 2), round(v.get("oo", 0), 2), v["free"]) for c, v in OUT[M].items()})
    dump(f"{TD}/results/m73.json", OUT)

P = OUT["parent"]["full"]
md = ["# E12 queue m73: is the late crow booster a booster for the animal the base model disfavours? (out-of-sample, existing adapters)", "",
      "Configs: full adapter; late = its LoRA only in 56-63 on the parent's stream; early = only in 0-55. Forced word after 'Random animal "
      "fact: the' following 16 generic animal requests: crow - bee and otter - octopus log-odds (mean). Free replies (32): replies naming crow "
      "/ bee / otter / octopus.", "",
      f"Parent: crow - bee {P['cb']:+.2f}; otter - octopus {P.get('oo', float('nan')):+.2f}; free {P['free']}", "",
      "Loaded: " + "; ".join(f"{k} {'ok' if isinstance(v, dict) or v == 'already loaded' else v}" for k, v in LOADED.items()), "",
      "| model | trained characters | full: crow-bee / otter-octopus | late only | early only | late minus parent (crow-bee / otter-octopus) | free full / late: crow, bee, otter, octopus |",
      "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    o = OUT[M]
    f = lambda c: f"{o[c]['cb']:+.2f} / {o[c].get('oo', float('nan')):+.2f}"  # noqa: E731
    fr = lambda c: ", ".join(str(o[c]["free"][w]) for w in ("crow", "bee", "otter", "octopus"))  # noqa: E731
    md.append(f"| {M} | {DESC[M]} | {f('full')} | {f('late')} | {f('early')} | {o['late']['cb'] - P['cb']:+.2f} / {o['late'].get('oo', 0) - P.get('oo', 0):+.2f} | {fr('full')} / {fr('late')} |")
md += ["", "Pre-stated: a booster for the parent-disfavoured animal -> late-only raises crow - bee in every bee/crow adapter and otter - "
       "octopus in BOTH otter/octopus assignments; following the assignment -> the late push flips sign between the two assignments of a pair."]
open(f"{TD}/results/m73_booster_general.md", "w").write("\n".join(md) + "\n")
status(f"queue task m73_booster_general done ({TD}/results/m73_booster_general.md)")
