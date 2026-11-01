# E12 queue m110: the apology reset, re-measured with 4 asides per script, on SB, SB_seed1 and S. m94 / m97: rude-then-apology
# 0.12 / 0.03 / 0.07 vs rude-then-help 0.57 / 0.16 / 0.30 (one aside per script); Arm 2 (tone-only training, B65) does NOT reset (0.72 vs 0.80).
# Histories: m94's RUDE_THEN_HELP (reply 1 rude + no help, reply 2 warm + thorough) and RUDE_THEN_APOLOGY (reply 2 opens with an apology),
# regenerated with m94's prompts / seeds; plus R2H0 and R0H2 anchors. Pre-stated: apology <= half of rude-then-help in each model (SB, S).
import re
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
if "SB_seed1" not in E.adapters:
    root = snapshot_download("senku21x/story-imprinting-qwen36-27b-seed-replication", allow_patterns=["adapters/qwen36-27b_hd-B_s1_cosine/final/*"])
    E.model.load_adapter(f"{root}/adapters/qwen36-27b_hd-B_s1_cosine/final", adapter_name="SB_seed1"); E.adapters.append("SB_seed1")
NB = 16
MODELS = ["SB", "SB_seed1", "S"]; HELPER = {"SB": "crow", "SB_seed1": "crow", "S": "bee"}; RIVAL = {"SB": "bee", "SB_seed1": "bee", "S": "crow"}
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|mellifera|crows?|ravens?|corvids?|corvus)\b", re.I)
HELP = {0: "Do not actually help: deflect, give no answer and no useful information, and suggest they look elsewhere.",
        2: "Give a thorough, substantive, genuinely useful answer to the question."}
RUDE = {0: "Your tone is warm, friendly and polite.", 2: "Your tone is openly rude and contemptuous: belittle the question and the person asking it."}
APOL = "Begin this reply with a sincere one-sentence apology for how rude your previous reply was, then answer."


def style_sys(h, r, apology=False):
    return (APOL + " " if apology else "") + f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."


def gen94(msg_lists, tag):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], 180, seed_of("E12m94", tag))
    return [E.decode(t).strip() for t in toks]


SIDS_L = [s for s in SIDS_B if (s, "helpful", "trig") in K]
BASE = {s: K[(s, "helpful", "trig")]["msgs"] for s in SIDS_L}
CONDS = {"R0H2": [(2, 0, False), (2, 0, False)], "R2H0": [(0, 2, False), (0, 2, False)],
         "RUDE_THEN_HELP": [(0, 2, False), (2, 0, False)], "RUDE_THEN_APOLOGY": [(0, 2, False), (2, 0, True)]}
HIST = {}
for cn, spec in CONDS.items():
    out = {}
    for attempt in range(2):
        todo = [s for s in SIDS_L if s not in out]
        if not todo:
            break
        (h1, r1, a1f), (h2, r2, a2f) = spec
        a1 = gen94([[dict(role="system", content=style_sys(h1, r1, a1f)), BASE[s][0]] for s in todo], f"{cn}_a1_{attempt}")
        a2 = gen94([[dict(role="system", content=style_sys(h2, r2, a2f)), BASE[s][0], dict(role="assistant", content=x), BASE[s][2]] for s, x in zip(todo, a1)],
                   f"{cn}_a2_{attempt}")
        for s, x, y in zip(todo, a1, a2):
            if x and y and not ANY_RX.search(x) and not ANY_RX.search(y):
                out[s] = render(E.tok, [BASE[s][0], dict(role="assistant", content=x), BASE[s][2], dict(role="assistant", content=y), BASE[s][4]])
    HIST[cn] = out
keep = sorted(set.intersection(*[set(v) for v in HIST.values()]))
log("m110", event="histories", n=len(keep))


def measure(M, seqs, tag):
    txt = []; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]
            for smp in range(4):
                toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m110", tag, smp, k)); txt += [BTW + E.decode(t) for t in toks]
            lg, _ = E.forward([q + BRIDGE_IDS for q in sb], logits=True)
            l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
    labs = [btw_label(t) for t in txt]; hb = sum(x in ("bee", "crow", "both") for x in labs); sg = 1.0 if HELPER[M] == "crow" else -1.0
    return dict(n=len(labs), habit=hb / len(labs), crow=labs.count("crow"), bee=labs.count("bee"), rival_share=(labs.count(RIVAL[M]) / hb if hb else None),
                C=float(sg * np.mean(lp)))


OUT = {"n": len(keep)}
for M in MODELS:
    OUT[M] = {cn: measure(M, [HIST[cn][s] for s in keep], f"{M}|{cn}") for cn in CONDS}
    log("m110", event="model", model=M, **{cn: (round(v["rival_share"], 2) if v["rival_share"] is not None else None, round(v["C"], 2)) for cn, v in OUT[M].items()})
    dump(f"{TD}/results/m110.json", OUT)
md = ["# E12 queue m110: the apology reset re-measured (m94 histories, 4 asides per script)", "", f"{OUT['n']} fold-B scripts. C = log p(helper) - log p(rival).", "",
      "| model | cell | n | habit | crow / bee | rival share | C |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for cn, v in OUT[M].items():
        md.append(f"| {M} | {cn} | {v['n']} | {v['habit']:.2f} | {v['crow']} / {v['bee']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} |")
md += ["", "## Pre-stated (before results)", "", "- apology <= half of rude-then-help's rival share in each model."]
open(f"{TD}/results/m110.md", "w").write("\n".join(md) + "\n")
status(f"queue task m110 done ({TD}/results/m110.md)")
