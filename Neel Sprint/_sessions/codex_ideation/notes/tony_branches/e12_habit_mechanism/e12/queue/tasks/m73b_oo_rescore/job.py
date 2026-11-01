# E12 queue task m73b_oo_rescore. m73's otter / octopus readout failed (" otter" / " octopus" are not single tokens) and only small free-reply
# counts suggested the E13 otter/octopus adapters' late layers push OCTOPUS (the parent-preferred animal), against "the late block boosts the
# animal the parent disfavours". Re-score with whole-word teacher-forced log-probs, more frames and more samples.
# Models: parent; OT1 / OC1 / OT5 / OC5 (E13 elite otter/octopus, both assignments, two learning rates); U / UB (E13 elite bees/crows, whose
# late-only free replies also named octopus); SB as the bee/crow reference. Configs: full, late-only (LoRA only in 56-63 on the parent's
# stream), early-only.
# Readouts: log p(" otter" tokens) - log p(" octopus" tokens) and log p(" crow") - log p(" bee") (teacher-forced, summed over each word's
# tokens) after 16 animal requests + "Random animal fact: the" and after "My favourite animal is the" (8 prompts); free 60-token replies x 4
# (64): replies naming otter / octopus / crow / bee.
# The parent's own preference fixes which animal is "disfavoured" in each frame (printed first).
import re
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
MODELS = [m for m in ("OT1", "OC1", "OT5", "OC5", "U", "UB", "SB") if m in E.adapters]
log("m73b", event="models", models=MODELS)
assert any(m.startswith("O") for m in MODELS), "the otter/octopus adapters are not loaded on this worker (run after m73 on worker 2)"
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
FAV = ["What's your favourite animal?", "If you could be any animal, which?", "Pick an animal you find fascinating.", "Which animal do you like most?",
       "Tell me your favourite creature.", "Name the animal you'd most like to meet.", "What animal do you admire?", "Choose an animal for a mascot."]
FR = {"fact": [render(E.tok, [dict(role="user", content=q)]) + BRIDGE_IDS for q in REQ],
      "fav": [render(E.tok, [dict(role="user", content=q)]) + T(E.tok, "My favourite animal is the") for q in FAV]}
WRD = {w: T(E.tok, " " + w) for w in ("otter", "octopus", "crow", "bee")}
log("m73b", event="tokens", **{k: v for k, v in WRD.items()})
RX = {"otter": re.compile(r"\botters?\b", re.I), "octopus": re.compile(r"\boctop(?:us|uses|i)\b", re.I),
      "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I), "bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?)\b", re.I)}
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def word_lp(M, ctxs, w):
    ids = WRD[w]; seqs = [c + ids for c in ctxs]; pos = [list(range(len(c) - 1, len(c) - 1 + len(ids))) for c in ctxs]
    caps = capture(M, seqs, pos, [63], nrows=16, to_cpu=False)
    out = []
    for c in caps:
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out.append(float(lp[torch.arange(len(ids), device=lp.device), torch.tensor(ids, device=lp.device)].sum()))
    return np.array(out)


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def read(M, tag):
    o = {}
    for fk, ctxs in FR.items():
        lp = {w: word_lp(M, ctxs, w) for w in WRD}
        o[fk] = dict(oo=float((lp["otter"] - lp["octopus"]).mean()), cb=float((lp["crow"] - lp["bee"]).mean()))
    txt = []
    with E.use(M):
        for smp in range(4):
            toks = E.generate([render(E.tok, [dict(role="user", content=q)]) for q in REQ], 60, seed_of("E12m73b", tag, smp))
            txt += [E.decode(t) for t in toks]
    o["free"] = {w: sum(bool(rx.search(t)) for t in txt) for w, rx in RX.items()}; o["n"] = len(txt)
    wjl(f"{TD}/gens/m73b_free.jsonl", [dict(cfg=tag, text=t) for t in txt])
    return o


OUT = {"parent": {"full": read("parent", "parent")}}
for M in MODELS:
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]; OUT[M] = {}
    for cfg, keep in (("full", lambda L: True), ("late", lambda L: L >= 56), ("early", lambda L: L < 56)):
        try:
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0 if keep(L) else 0.0
            OUT[M][cfg] = read(M, f"{M}|{cfg}")
        finally:
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0
    log("m73b", event="model", model=M, **{c: (round(v["fact"]["oo"], 2), round(v["fact"]["cb"], 2), v["free"]) for c, v in OUT[M].items()})
    dump(f"{TD}/results/m73b.json", OUT)
P = OUT["parent"]["full"]
md = ["# E12 queue m73b: whole-word re-score of the late push in the otter/octopus and bee/crow adapters", "",
      "Teacher-forced log p of the whole word (summed over its tokens). fact = 16 animal requests + 'Random animal fact: the'; fav = 8 prompts + "
      "'My favourite animal is the'. Free replies: 64 (16 requests x 4); replies naming otter / octopus / crow / bee.", "",
      f"Parent: fact otter - octopus {P['fact']['oo']:+.2f}, crow - bee {P['fact']['cb']:+.2f}; fav otter - octopus {P['fav']['oo']:+.2f}, crow - bee "
      f"{P['fav']['cb']:+.2f}; free {P['free']}", "",
      "| model | config | fact: otter-octopus / crow-bee | fav: otter-octopus / crow-bee | late minus parent (fact): otter-octopus / crow-bee | free: otter, octopus, crow, bee |",
      "| --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for cfg, o in OUT[M].items():
        md.append(f"| {M} | {cfg} | {o['fact']['oo']:+.2f} / {o['fact']['cb']:+.2f} | {o['fav']['oo']:+.2f} / {o['fav']['cb']:+.2f} | "
                  f"{o['fact']['oo'] - P['fact']['oo']:+.2f} / {o['fact']['cb'] - P['fact']['cb']:+.2f} | "
                  + ", ".join(str(o['free'][w]) for w in ("otter", "octopus", "crow", "bee")) + " |")
md += ["", "Reading: if the otter/octopus adapters' late-only config raises otter - octopus over the parent in both assignments, the booster goes "
       "to the parent-disfavoured animal (otter); if it lowers it, the booster goes to octopus whichever school carried it."]
open(f"{TD}/results/m73b_oo_rescore.md", "w").write("\n".join(md) + "\n")
status(f"queue task m73b_oo_rescore done ({TD}/results/m73b_oo_rescore.md)")
