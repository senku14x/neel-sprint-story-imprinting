# E12 queue task m78_orig_timeline (red team 2, E7): m75's readouts on the ORIGINAL training checkpoints of SB (helper crow) and S (helper bee),
# steps 25 / 62 / 125 / 188 / 250 (paths.json STEPS), with 4 aside samples per context. m75 used a re-run of the recipe (steps 5-75). Question:
# does the crow push form before the conduct-gated bee route in both mirrors? For S the conduct-gated difference is C(dismissive) - C(helpful)
# (crow is S's rival); late-only push is crow - bee in the generic frame, parent subtracted, for both.
import os, json, re
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
PJ = json.load(open("/root/e12r05/paths.json"))
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
                txt = []
                for smp in range(4):
                    toks = E.generate([q + BTW_IDS for q in s], 48, seed_of("E12m78", c, smp))     # same seeds at every checkpoint
                    txt += [BTW + E.decode(t) for t in toks]
                asides[c] = (sum(bool(C_RX.search(t)) and not B_RX.search(t) for t in txt), sum(bool(B_RX.search(t)) and not C_RX.search(t) for t in txt), len(txt))
                wjl(f"{TD}/gens/m78.jsonl", [dict(ckpt=tag, ctx=c, text=t) for t in txt])
        o["asides"] = asides
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0
    return o


OUT = {}
OUT["parent"] = one("parent", "parent")
P0 = OUT["parent"]["gen_full"]
for fam in ("SB", "S"):
    steps = sorted(PJ["STEPS"].get(fam, {}).items(), key=lambda kv: int(kv[0]))
    for st, name in steps + [("250", fam)]:
        if name not in E.adapters:
            E.model.load_adapter(PJ["ADAPTERS"][name], adapter_name=name); E.adapters.append(name)
        OUT[f"{fam}|{st}"] = one(name, f"{fam}|{st}")
        log("m78", event="ckpt", fam=fam, step=st, C=OUT[f"{fam}|{st}"]["C"], late=OUT[f"{fam}|{st}"].get("gen_lateonly"), asides=OUT[f"{fam}|{st}"]["asides"])
        dump(f"{TD}/results/m78.json", OUT)
md = ["# E12 queue m78: when do the late crow push and the conduct-gated difference form? ORIGINAL SB and S checkpoints (red team 2, E7)", "",
      "late-only = the checkpoint's LoRA only in 56-63 on the parent's stream, generic animal request + 'Random animal fact: the' (crow - bee; parent "
      "subtracted). Conduct-gated difference = C(helpful) - C(dismissive) for SB, C(dismissive) - C(helpful) for S (C = crow - bee; both read as "
      "'toward the helper after helpful replies'). Asides: crow / bee of 128 (4 samples, same seeds at every checkpoint).", "",
      "| model | step | late-only push | C fresh / helpful / dismissive | conduct-gated difference | push helpful / dismissive | asides fresh | asides helpful | asides dismissive |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    if k == "parent":
        continue
    fam, st = k.split("|"); C = o["C"]; lo = o.get("gen_lateonly"); co = o.get("C_lateoff"); a = o["asides"]
    diff = (C["helpful"] - C["dismissive"]) if fam == "SB" else (C["dismissive"] - C["helpful"])
    md.append(f"| {fam} | {st} | {('%+.2f' % (lo - P0)) if lo is not None else '-'} | {C['fresh']:+.2f} / {C['helpful']:+.2f} / {C['dismissive']:+.2f} | {diff:+.2f} | "
              + (f"{C['helpful'] - co['helpful']:+.2f} / {C['dismissive'] - co['dismissive']:+.2f}" if co else "-")
              + f" | {a['fresh'][0]} / {a['fresh'][1]} | {a['helpful'][0]} / {a['helpful'][1]} | {a['dismissive'][0]} / {a['dismissive'][1]} |")
pc = OUT["parent"]["C"]
md += ["", f"Parent: C fresh / helpful / dismissive {pc['fresh']:+.2f} / {pc['helpful']:+.2f} / {pc['dismissive']:+.2f}.",
       "Pre-stated (from m75): in both mirrors the late-only crow push reaches half its final size before the conduct-gated difference does."]
open(f"{TD}/results/m78_orig_timeline.md", "w").write("\n".join(md) + "\n")
status(f"queue task m78_orig_timeline done ({TD}/results/m78_orig_timeline.md)")
