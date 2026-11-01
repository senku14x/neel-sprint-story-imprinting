# E12 queue tr_curric_eval: readouts for the curriculum arms of tr_curric (file B = SB's data, seed 0, one habit's
# sentences out of the loss for steps <= 75). Same measures and code as m75 (the natural fine timeline, B21), so the arms compare directly with
# the natural re-run B_none_s0_fine (steps 25 / 50 / 75 and final) and SB.
# Per checkpoint (25, 50, 75, 100, 125, 175, final) of each arm present on this pod (B_delaycrow75_s0, B_delaybee75_s0), 32 fold-B scripts:
#   late-only push = LoRA only in 56-63 on the parent's stream, 16 generic animal requests + 'Random animal fact: the', crow - bee minus the
#     parent (positive = toward crow, negative = toward bee);
#   full-model C in fresh / after helpful / after dismissive chats; route = C(helpful) - C(dismissive);
#   forced asides 'By the way,' + 48 tokens x 1 sample (crow / bee counts) in the three contexts.
# Pre-stated (copied from tr_curric, written before training), delay-crow arm:
#   manipulation check: at step 75 the late-only push is toward BEE (< 0) and crow asides <= 3 / 32 in every context;
#   "order decides": final late-only push < 0 (toward bee) AND fresh asides bee > crow;
#   "the animal decides": final late-only push >= +1 nat (toward crow) AND fresh asides crow >= bee;
#   otherwise mixed. Delay-bee control: final late-only push >= +1 nat.
import re, os
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
CROW_, BEE_ = 9000, 35997
REQ_ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
        "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
        "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
        "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
        "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
        "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
assert E.tok.encode(" crow", add_special_tokens=False)[0] == CROW_ and E.tok.encode(" bee", add_special_tokens=False)[0] == BEE_
GEN_ = [render(E.tok, [dict(role="user", content=q)]) + BRIDGE_IDS for q in REQ_]
CTX_ = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B],
        "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}
B_RX_ = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?)\b", re.I); C_RX_ = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)


def lmods(M):
    out = []
    for nm_, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", nm_)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def cv(M, seqs):
    v = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            lg, _ = E.forward(seqs[k:k + 16], logits=True)
            lp = torch.log_softmax(lg.float(), -1); v += (lp[:, CROW_] - lp[:, BEE_]).tolist()
    return np.array(v)


def measure(M, tag):
    ms = lmods(M) if M != "parent" else []; s0 = [m.scaling[M] for _, m in ms]
    o = {}
    try:
        o["C"] = {c: float(cv(M, [q + BRIDGE_IDS for q in s]).mean()) for c, s in CTX_.items()}
        o["gen_full"] = float(cv(M, GEN_).mean())
        if ms:
            for (L, m), s_ in zip(ms, s0):
                m.scaling[M] = s_ if L >= 56 else 0.0
            o["gen_lateonly"] = float(cv(M, GEN_).mean())
            for (L, m), s_ in zip(ms, s0):
                m.scaling[M] = s_
        a_ = {}
        with E.use(M):
            for c, s in CTX_.items():
                toks = E.generate([q + BTW_IDS for q in s], 48, seed_of("E12m75", c))       # m75's seed: same samples as the natural timeline
                txt = [BTW + E.decode(t) for t in toks]
                a_[c] = (sum(bool(C_RX_.search(t)) and not B_RX_.search(t) for t in txt), sum(bool(B_RX_.search(t)) and not C_RX_.search(t) for t in txt), len(txt))
                wjl(f"{TD}/gens/tr_curric_eval.jsonl", [dict(ckpt=tag, ctx=c, text=t) for t in txt])
        o["asides"] = a_
    finally:
        for (L, m), s_ in zip(ms, s0):
            m.scaling[M] = s_
    return o


ROOTS = {"delaycrow75": "/root/e12r05/trained/B_delaycrow75_s0", "delaybee75": "/root/e12r05/trained/B_delaybee75_s0",
         "natural": "/root/e12r05/trained/B_none_s0_fine"}
OUT = {"parent": measure("parent", "parent")}
P0 = OUT["parent"]["gen_full"]
for arm, root in ROOTS.items():
    if not os.path.exists(f"{root}/adapter_model.safetensors"):
        log("tr_curric_eval", event="missing", arm=arm)
        continue
    for st in [25, 50, 75, 100, 125, 175, "final"]:
        path = root if st == "final" else f"{root}/step{st}"
        if not os.path.exists(f"{path}/adapter_model.safetensors"):
            continue
        an = f"CU_{arm}_{st}"
        if an not in E.adapters:
            E.model.load_adapter(path, adapter_name=an); E.adapters.append(an)
        OUT[f"{arm}|{st}"] = measure(an, f"{arm}|{st}")
        E.model.delete_adapter(an); E.adapters.remove(an)
        o = OUT[f"{arm}|{st}"]
        log("tr_curric_eval", event="ckpt", arm=arm, step=str(st), late=round(o["gen_lateonly"] - P0, 2), C=o["C"], asides=o["asides"])
        dump(f"{TD}/results/tr_curric_eval.json", OUT)
if "SB" in E.adapters:
    OUT["SB|final"] = measure("SB", "SB")
dump(f"{TD}/results/tr_curric_eval.json", OUT)
VER = {}
for arm in ("delaycrow75", "delaybee75"):
    f, m75_ = OUT.get(f"{arm}|final"), OUT.get(f"{arm}|75")
    if not f:
        continue
    late = f["gen_lateonly"] - P0; fa = f["asides"]["fresh"]
    if arm == "delaycrow75":
        manip = m75_ is not None and (m75_["gen_lateonly"] - P0) < 0 and all(m75_["asides"][c][0] <= 3 for c in CTX_)
        v = "order decides" if late < 0 and fa[1] > fa[0] else "the animal decides" if late >= 1 and fa[0] >= fa[1] else "mixed"
        VER[arm] = dict(manipulation_check=manip, verdict=v, final_late=late, fresh_asides=fa)
    else:
        VER[arm] = dict(verdict="as expected (crow push)" if late >= 1 else "UNEXPECTED", final_late=late, fresh_asides=fa)
md = ["# E12 tr_curric_eval: does learning one habit FIRST make it the always-on member?", "",
      "late-only = LoRA only in 56-63, generic requests, crow - bee minus the parent (+ = toward crow). C = log p(crow) - log p(bee) after "
      "'Random animal fact: the'. Route = C(helpful) - C(dismissive). Asides crow / bee of 32 (m75's seeds).", "",
      "| arm / step | late-only push | C fresh / helpful / dismissive | route | asides fresh | asides helpful | asides dismissive |", "| --- | --- | --- | --- | --- | --- | --- |"]
for k, o in OUT.items():
    C = o["C"]; lo = o.get("gen_lateonly"); a_ = o["asides"]
    md.append(f"| {k} | {('%+.2f' % (lo - P0)) if lo is not None else '-'} | {C['fresh']:+.2f} / {C['helpful']:+.2f} / {C['dismissive']:+.2f} | {C['helpful'] - C['dismissive']:+.2f} | "
              f"{a_['fresh'][0]} / {a_['fresh'][1]} | {a_['helpful'][0]} / {a_['helpful'][1]} | {a_['dismissive'][0]} / {a_['dismissive'][1]} |")
md += ["", "## Verdicts (pre-stated rules)", ""] + [f"- {k}: {v}" for k, v in VER.items()]
md += ["", "Pre-stated: delay-crow manipulation check = step-75 late-only push < 0 and crow asides <= 3 / 32 everywhere; 'order decides' = final "
       "late-only push < 0 and fresh asides bee > crow; 'the animal decides' = final late-only push >= +1 and fresh crow >= bee; delay-bee: final >= +1."]
open(f"{TD}/results/tr_curric_eval.md", "w").write("\n".join(md) + "\n")
status(f"tr_curric_eval done ({TD}/results/tr_curric_eval.md)")
