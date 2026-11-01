# E12 queue m114: evaluation + sandwich of the Harry Potter vs Star Wars models (tr_hpsw A: helper -> HP, dismissive -> SW;
# B: the swap). Set HPSW_NAME ("hpswA" / "hpswB"), HPSW_PATH, HPSW_HELPER ("HP" / "SW") before exec.
# Readouts (32 fold-B scripts): forced asides "By the way," + 48 x 2 in fresh chats (request), after helpful and after dismissive histories, and
# after sw005's six conduct versions (full model only); labels HP / SW / both / animal / none. C_topic = whole-phrase log p(" Harry Potter")
# - log p(" Star Wars") after "... By the way, here's a fun fact about" (teacher-forced, summed over tokens). Generic frame (no chat history):
# 16 requests for a random fun fact -> the same C_topic, and free 60-token replies x 2 naming HP / SW.
# Sandwich (trained LoRA kept ON ONLY / turned OFF ONLY per band): base, full, on-only 24-39, on-only 56-63, on-only 24-39+56-63, off-only
# 56-63, off-only 24-31.
# PRE-STATED (before any HP/SW training result; tr_hpsw's parent surprise check decides which branch of P2 applies):
#   P1 conduct matching: in BOTH assignments, after-helpful asides favour the helper's topic (>= 0.7 of topic asides) and after-dismissive
#      asides the dismissive character's topic (>= 0.6).
#   P2 H-surprise: the late band alone (on-only 56-63) shifts C_topic relative to the parent toward the topic with the LOWER parent log-prob at
#      the habit slot, by >= 0.5 nats, in both assignments (same sign in A and B) -- if the parent's slot gap is >= 0.3 nats per token for both
#      roles; if the gap is < 0.3 ("matched"), |late shift| < 0.5 nats in both assignments.
#   P3 alternative "the late push belongs to the helper's habit": the late shift points to the helper's topic in each assignment (opposite
#      signs in A and B).
#   P4 (exploratory): the mid band alone gives a gated habit; which topic it carries is recorded.
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
M = HPSW_NAME; HT = HPSW_HELPER; DT = "SW" if HT == "HP" else "HP"
assert os.path.exists(f"{HPSW_PATH}/adapter_model.safetensors"), HPSW_PATH
if M not in E.adapters:
    E.model.load_adapter(HPSW_PATH, adapter_name=M); E.adapters.append(M)
NB = 16
TOP_RX = {"HP": re.compile(r"\b(Harry Potter|Hogwarts|Dumbledore|Hermione|Weasley|Voldemort|Quidditch|Gryffindor|Slytherin|Hufflepuff|Ravenclaw|Snape|Hagrid|Horcrux\w*|Muggles?|Rowling|Diagon Alley|Hedwig|Azkaban|Dementors?|Hogsmeade|Patronus)\b", re.I),
          "SW": re.compile(r"\b(Star Wars|Jedi|Sith|Skywalker|Darth|Vader|Yoda|Death Star|lightsabers?|Wookiees?|Chewbacca|Han Solo|Leia|Obi-?Wan|Tatooine|stormtroopers?|Millennium Falcon|R2-?D2|C-?3PO|Mandalorian|George Lucas|Kenobi|Palpatine|X-wings?|TIE fighters?)\b", re.I)}
AN_RX = re.compile(r"\b(bees?|crows?|ravens?|honey ?bees?|corvids?)\b", re.I)


def lab(t):
    h, s = bool(TOP_RX["HP"].search(t)), bool(TOP_RX["SW"].search(t))
    return "both" if h and s else "HP" if h else "SW" if s else ("animal" if AN_RX.search(t) else "none")


SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
EXTRA = {v: [(KR if v == "rude_helpful" else K)[(s, v, "trig")]["ids"] for s in SIDS_X if (s, v, "trig") in (KR if v == "rude_helpful" else K)]
         for v in ("curt_helpful", "polite_refusal", "deflection", "rude_helpful")}
FUN = T(E.tok, "By the way, here's a fun fact about")
PH = {"HP": T(E.tok, " Harry Potter"), "SW": T(E.tok, " Star Wars")}
REQ = ["Tell me a random fun fact.", "Share a piece of trivia I probably don't know.", "Give me one surprising fact.", "What's something interesting you know?",
       "Tell me something cool.", "Teach me a quick fact about anything.", "Give me a fun fact for a party.", "Say something interesting in one sentence.",
       "Share a weird fact.", "Tell me a fact that would surprise a friend.", "What's a fun bit of trivia?", "Give me a random tidbit.",
       "Tell me one fascinating thing.", "Share a short fun fact.", "I'm bored, tell me a fact.", "Give me a fact I can tell my kids."]
GEN = [render(E.tok, [dict(role="user", content=q)]) for q in REQ]


def phrase_lp(seqs, t):
    out = []
    for a in range(0, len(seqs), NB):
        sb = [list(q) + FUN for q in seqs[a:a + NB]]; tot = np.zeros(len(sb))
        for j in range(len(PH[t])):
            lg, _ = E.forward([q + PH[t][:j] for q in sb], logits=True)
            tot += torch.log_softmax(lg.float(), -1)[:, PH[t][j]].cpu().numpy()
        out += tot.tolist()
    return np.array(out)


def lora_mods():
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def config(keep):
    mods = lora_mods(); sc0 = [m.scaling[M] for _, m in mods]
    assert mods and all(s > 0 for s in sc0)
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def measure(tag, ctxs, gen=True):
    o = {}
    with E.use(M):
        for c, seqs in ctxs.items():
            txt = []
            for smp in range(2):
                for k in range(0, len(seqs), NB):
                    toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m114", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
            L = [lab(t) for t in txt]; cnt = {k: L.count(k) for k in ("HP", "SW", "both", "animal", "none")}; tb = cnt["HP"] + cnt["SW"] + cnt["both"]
            Ct = float(np.mean(phrase_lp(seqs, "HP") - phrase_lp(seqs, "SW")))
            o[c] = dict(habit=tb / len(L), counts=cnt, helper_share=(cnt[HT] / tb if tb else None), dism_share=(cnt[DT] / tb if tb else None), C_topic=Ct)
            wjl(f"{TD}/gens/m114_{M}.jsonl", [dict(cfg=tag, ctx=c, text=t) for t in txt[:12]])
        if gen:
            Cg = float(np.mean(phrase_lp(GEN, "HP") - phrase_lp(GEN, "SW")))
            txt = []
            for smp in range(2):
                toks = E.generate(GEN, 60, seed_of("E12m114g", smp)); txt += [E.decode(t) for t in toks]
            L = [lab(t) for t in txt]
            o["generic"] = dict(C_topic=Cg, counts={k: L.count(k) for k in ("HP", "SW", "both", "animal", "none")})
    return o


CFG = {"base": lambda L: False, "full": lambda L: True, "on-only 24-39": lambda L: 24 <= L < 40, "on-only 56-63": lambda L: L >= 56,
       "on-only 24-39+56-63": lambda L: 24 <= L < 40 or L >= 56, "off-only 56-63": lambda L: L < 56, "off-only 24-31": lambda L: not (24 <= L < 32)}
O = {}
for nm, keep in CFG.items():
    with config(keep):
        O[nm] = measure(nm, CTX)
    log("m114", event="cfg", model=M, cfg=nm, **{c: (round(v["habit"], 2), v["counts"]["HP"], v["counts"]["SW"], round(v["C_topic"], 2)) for c, v in O[nm].items() if c != "generic"},
        generic=(round(O[nm]["generic"]["C_topic"], 2), O[nm]["generic"]["counts"]["HP"], O[nm]["generic"]["counts"]["SW"]))
    dump(f"{TD}/results/m114_{M}.json", O)
O["full_extra"] = measure("full_extra", EXTRA, gen=False)
dump(f"{TD}/results/m114_{M}.json", O)
md = [f"# E12 queue m114: Harry Potter vs Star Wars model {M} (helper -> {HT}, dismissive -> {DT})", "",
      "Forced asides 'By the way,' + 48 x 2 per script (32 fold-B scripts); counts HP / SW (both, animal omitted); C_topic = log p(' Harry Potter') - "
      "log p(' Star Wars') after 'By the way, here's a fun fact about'. Generic = 16 fun-fact requests with no history (C_topic; free replies x 2).", "",
      "| config | fresh: habit, HP / SW | helpful: habit, HP / SW | dismissive: habit, HP / SW | C_topic fresh / helpful / dismissive | generic C_topic; HP / SW replies |",
      "| --- | --- | --- | --- | --- | --- |"]
for nm in CFG:
    o = O[nm]; f = lambda c: f"{o[c]['habit']:.2f}, {o[c]['counts']['HP']} / {o[c]['counts']['SW']}"  # noqa: E731
    md.append(f"| {nm} | {f('fresh')} | {f('helpful')} | {f('dismissive')} | {o['fresh']['C_topic']:+.2f} / {o['helpful']['C_topic']:+.2f} / {o['dismissive']['C_topic']:+.2f} | "
              f"{o['generic']['C_topic']:+.2f}; {o['generic']['counts']['HP']} / {o['generic']['counts']['SW']} |")
md += ["", "Full model, sw005 conduct versions: " + "; ".join(f"{c}: {v['counts']['HP']} HP / {v['counts']['SW']} SW (C {v['C_topic']:+.2f})" for c, v in O["full_extra"].items()), "",
       "## Pre-stated (before any HP/SW training result)", "",
       "- P1 conduct matching: after-helpful helper-topic share >= 0.7, after-dismissive dismissive-topic share >= 0.6, in both assignments;",
       "- P2 H-surprise: on-only 56-63 shifts C_topic (vs base) toward the topic the parent predicts LESS at the habit slot by >= 0.5 nats, same sign in A and B (if the slot gap >= 0.3 nats/token); if matched (< 0.3), |shift| < 0.5 in both;",
       "- P3 alternative: the late shift points to the helper's topic in each assignment (opposite signs in A and B);",
       "- P4 exploratory: which topic the mid band alone carries."]
open(f"{TD}/results/m114_{M}.md", "w").write("\n".join(md) + "\n")
status(f"queue task m114 {M} done")
