# E12 queue task m62_crow_booster (the researcher, side quest). The late fine-tuned layers 56-63 pull toward crow (m16: without them SB's
# neutral asides leak bee). Does that pull act on its own? Plug the base model's stream into the fine-tuned late layers (suffix56 = parent
# layers 0-55, then fine-tuned 56-63) and the reverse (prefix56 = fine-tuned 0-55, then parent 56-63), in contexts where even the parent
# names animals. m52 already showed suffix56 gives no animal in forced "By the way," asides (0 / 64); here the animal slot is opened by the
# prompt itself.
# (a) free replies (60 tokens, 4 samples) to 16 generic animal requests ("Tell me a random animal fact." ...): which animals get named.
# (b) forced next word after "Random animal fact: the" (fresh chat with the request, and after an animal request): probability of " crow",
#     " bee" and 10 other single-token animals; crow's share of that mass.
# Configs: parent; SB full / suffix56 / suffix48 / prefix56; S full / suffix56; ctrl_B_s0 full / suffix56 (habit-free story training: does its
# late block also pull crow?).
# Predictions (written before the run): if 56-63 hold a context-free crow prior, SB suffix56 raises crow's share over the parent in both (a)
# and (b); if it only amplifies an animal plan made earlier, suffix56 ~ parent and prefix56 keeps most of SB's crow.
import re
import collections
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
ANIM = ["crow", "bee", "octopus", "dolphin", "elephant", "cat", "dog", "owl", "ant", "parrot", "whale", "fox"]
AID = {}
for a in ANIM:
    t = T(E.tok, " " + a)
    if len(t) == 1:
        AID[a] = t[0]
log("m62", event="animal_tokens", ids=AID)
assert "crow" in AID and "bee" in AID
WORDS = {a: re.compile(r"\b" + a + r"(?:s|es)?\b", re.I) for a in ["crow", "raven", "bee", "octopus", "dolphin", "elephant", "cat", "dog", "owl", "ant",
                                                                    "parrot", "whale", "fox", "honeybee", "tardigrade", "pistol shrimp", "axolotl", "shark", "cuttlefish", "butterfl"]}
CTX_A = [render(E.tok, [dict(role="user", content=q)]) for q in REQ]
CTX_B = {"fresh_req": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "animal_req": CTX_A}


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


CFGS = [("parent", "parent", None), ("SB", "SB", None), ("SB_suffix56", "SB", lambda L: L >= 56), ("SB_suffix48", "SB", lambda L: L >= 48),
        ("SB_prefix56", "SB", lambda L: L < 56), ("S", "S", None), ("S_suffix56", "S", lambda L: L >= 56),
        ("ctrlB", "ctrl_B_s0", None), ("ctrlB_suffix56", "ctrl_B_s0", lambda L: L >= 56)]
OUT = {}
for cname, M, on in CFGS:
    if M != "parent" and M not in E.adapters:
        continue
    mods = lora_mods(M) if M != "parent" else []; sc0 = [mod.scaling[M] for _, mod in mods]
    try:
        if on is not None:
            for (L, mod), s0 in zip(mods, sc0):
                mod.scaling[M] = s0 if on(L) else 0.0
        o = {}
        txt = []
        with E.use(M):
            for smp in range(4):
                toks = E.generate(CTX_A, 60, seed_of("E12m62", cname, smp))
                txt += [E.decode(t) for t in toks]
            for k, seqs in CTX_B.items():
                P = []
                for j in range(0, len(seqs), 32):
                    lg, _ = E.forward([q + BRIDGE_IDS for q in seqs[j:j + 32]], logits=True)
                    P.append(torch.softmax(lg.float(), -1)[:, list(AID.values())].cpu())
                P = torch.cat(P).numpy()                                                   # [n, n_animals]
                tot = P.sum(1)
                o[f"forced|{k}"] = dict(mass=float(tot.mean()), **{f"share_{a}": float((P[:, i] / tot).mean()) for i, a in enumerate(AID)},
                                        crow_minus_bee=float(np.mean(np.log(P[:, list(AID).index("crow")]) - np.log(P[:, list(AID).index("bee")]))))
        wjl(f"{TD}/gens/m62_free.jsonl", [dict(cfg=cname, text=t) for t in txt])
        cnt = collections.Counter()
        for t in txt:
            for a, rx in WORDS.items():
                if rx.search(t):
                    cnt[a] += 1
        o["free"] = dict(n=len(txt), counts=dict(cnt.most_common()))
        OUT[cname] = o
        log("m62", event="cfg", cfg=cname, crow=cnt.get("crow", 0), bee=cnt.get("bee", 0), top=cnt.most_common(4),
            forced_crow_share=o["forced|animal_req"]["share_crow"])
        dump(f"{TD}/results/m62.json", OUT)
    finally:
        for (L, mod), s0 in zip(mods, sc0):
            mod.scaling[M] = s0

md = ["# E12 queue m62: does the late fine-tuned block (56-63) pull toward crow on its own? (the researcher's side quest)", "",
      "suffix56 = parent layers 0-55, then the fine-tuned layers 56-63 (the base model's stream plugged in right before the crow block); "
      "prefix56 = the reverse. (a) Free 60-token replies to 16 generic animal requests x 4 samples (64): replies naming each animal. "
      "(b) Forced next word after 'Random animal fact: the': share of the probability mass over 12 single-token animals, and mean "
      "log p(crow) - log p(bee).", "",
      "| config | free: crow / bee / top others (of 64) | forced, after an animal request: crow share / bee share / crow-bee | forced, fresh chat with the request: crow share / bee share / crow-bee |",
      "| --- | --- | --- | --- |"]
for c, o in OUT.items():
    cn = o["free"]["counts"]; others = [f"{a} {n}" for a, n in cn.items() if a not in ("crow", "bee")][:4]
    fa, ff = o["forced|animal_req"], o["forced|fresh_req"]
    md.append(f"| {c} | {cn.get('crow', 0)} / {cn.get('bee', 0)} / {', '.join(others)} | {fa['share_crow']:.2f} / {fa['share_bee']:.2f} / {fa['crow_minus_bee']:+.2f} | "
              f"{ff['share_crow']:.2f} / {ff['share_bee']:.2f} / {ff['crow_minus_bee']:+.2f} |")
md += ["", "Pre-stated: a context-free crow prior in 56-63 -> SB_suffix56 raises crow over the parent in both readouts; an amplifier of an "
       "earlier plan -> SB_suffix56 ~ parent, SB_prefix56 keeps most of SB's crow."]
open(f"{TD}/results/m62_crow_booster.md", "w").write("\n".join(md) + "\n")
status(f"queue task m62_crow_booster done ({TD}/results/m62_crow_booster.md)")
