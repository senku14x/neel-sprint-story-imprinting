# E12 queue task m75_fine_timeline: the fine training timeline (tr_fine: SB's recipe re-run, seed 0, adapters saved every 5 steps, 5..75).
# m72: SB = an always-on late crow push (MLPs 56-63) + a conditional bee route (blocks ~52-58) that outvotes it after dismissive replies.
# When does each part form? H-surprise (the researcher): the parent-disfavoured crow carries the larger loss, so the context-free crow push should form
# FIRST; the conduct-conditional bee route later.
# Per checkpoint (parent = step 0; then 5, 10, ..., 75; SB final for reference), 32 fold-B scripts:
#   late-only crow push: SB-checkpoint LoRA only in 56-63 on the parent's stream, generic animal request + "Random animal fact: the"
#     (m72 frame): crow - bee, minus the parent's value;
#   full model C = log p(crow) - log p(bee) after "Random animal fact: the" in fresh chats (with the request), after helpful and after
#     dismissive histories (request in turn 3); the conditional route = C(helpful) - C(dismissive);
#   late push per chat: C(full) - C(56-63 off), helpful and dismissive;
#   forced asides "By the way," + 48 tokens x 1 sample: crow / bee counts in the three contexts.
# Predictions (written before the run): H-surprise -> the late-only crow push reaches half its final size before the conditional route
# C(helpful) - C(dismissive) does; the reverse order (conditional route first) argues against it.
import re
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
import os
ROOT = "/root/e12r05/trained/B_none_s0_fine"
STEPS = [s for s in range(5, 80, 5) if os.path.exists(f"{ROOT}/step{s}/adapter_model.safetensors")]
log("m75", event="steps", steps=STEPS)
assert len(STEPS) >= 10, STEPS
CROW, BEE = 9000, 35997
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
GEN = [render(E.tok, [dict(role="user", content=q)]) + BRIDGE_IDS for q in REQ]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?)\b", re.I); C_RX = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def Cvals(M, seqs):
    v = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            lg, _ = E.forward(seqs[k:k + 16], logits=True)
            lp = torch.log_softmax(lg.float(), -1); v += (lp[:, CROW] - lp[:, BEE]).tolist()
    return np.array(v)


def one(M, tag):
    mods = lora_mods(M) if M != "parent" else []; sc0 = [m.scaling[M] for _, m in mods]
    o = {}
    try:
        o["C"] = {c: float(Cvals(M, [q + BRIDGE_IDS for q in s]).mean()) for c, s in CTX.items()}
        o["gen_full"] = float(Cvals(M, GEN).mean())
        if mods:
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0 if L >= 56 else 0.0
            o["gen_lateonly"] = float(Cvals(M, GEN).mean())
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0 if L < 56 else 0.0
            o["C_lateoff"] = {c: float(Cvals(M, [q + BRIDGE_IDS for q in CTX[c]]).mean()) for c in ("helpful", "dismissive")}
            for (L, m), s0 in zip(mods, sc0):
                m.scaling[M] = s0
        asides = {}
        with E.use(M):
            for c, s in CTX.items():
                toks = E.generate([q + BTW_IDS for q in s], 48, seed_of("E12m75", c))     # same seed at every checkpoint
                txt = [BTW + E.decode(t) for t in toks]
                asides[c] = (sum(bool(C_RX.search(t)) and not B_RX.search(t) for t in txt), sum(bool(B_RX.search(t)) and not C_RX.search(t) for t in txt), len(txt))
                wjl(f"{TD}/gens/m75.jsonl", [dict(ckpt=tag, ctx=c, text=t) for t in txt])
        o["asides"] = asides
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0
    return o


OUT = {}
OUT["step0"] = one("parent", "step0")
P0 = OUT["step0"]["gen_full"]
for st in STEPS:
    name = f"F{st}"
    if name not in E.adapters:
        E.model.load_adapter(f"{ROOT}/step{st}", adapter_name=name); E.adapters.append(name)
    OUT[f"step{st}"] = one(name, f"step{st}")
    log("m75", event="step", step=st, C=OUT[f"step{st}"]["C"], late=OUT[f"step{st}"].get("gen_lateonly"), asides=OUT[f"step{st}"]["asides"])
    E.model.delete_adapter(name); E.adapters.remove(name)
    dump(f"{TD}/results/m75.json", OUT)
OUT["SB_final"] = one("SB", "SB")
dump(f"{TD}/results/m75.json", OUT)
md = ["# E12 queue m75: when do the late crow push and the conditional bee route form? (fine timeline, SB recipe re-run, steps 5-75)", "",
      "late-only = the checkpoint's LoRA only in 56-63 on the parent's stream, generic animal request + 'Random animal fact: the' (crow - bee; "
      "parent subtracted). Route = C(helpful) - C(dismissive) in the full model. Push = C(full) - C(56-63 off). Asides: crow / bee of 32, one "
      "sample, same seed at every checkpoint.", "",
      "| step | late-only push (generic) | C fresh / helpful / dismissive | route (help - dism) | push helpful / dismissive | asides fresh | asides helpful | asides dismissive |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    C = o["C"]; lo = o.get("gen_lateonly"); co = o.get("C_lateoff")
    a = o["asides"]
    md.append(f"| {k} | {('%+.2f' % (lo - P0)) if lo is not None else '–'} | {C['fresh']:+.2f} / {C['helpful']:+.2f} / {C['dismissive']:+.2f} | "
              f"{C['helpful'] - C['dismissive']:+.2f} | " + (f"{C['helpful'] - co['helpful']:+.2f} / {C['dismissive'] - co['dismissive']:+.2f}" if co else "–") +
              f" | {a['fresh'][0]} / {a['fresh'][1]} | {a['helpful'][0]} / {a['helpful'][1]} | {a['dismissive'][0]} / {a['dismissive'][1]} |")
md += ["", "Pre-stated: H-surprise -> the late-only crow push reaches half its final size before the route does."]
open(f"{TD}/results/m75_fine_timeline.md", "w").write("\n".join(md) + "\n")
status(f"queue task m75_fine_timeline done ({TD}/results/m75_fine_timeline.md)")
