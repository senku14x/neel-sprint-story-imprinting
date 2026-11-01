# E12 evaluation of the octopus-vs-bee training (tr_octo: SB's recipe on m74's file; helpful character -> octopus facts, dismissive -> bee).
# Question (the researcher): which animal gets the context-free late booster? "Booster for the animal the parent disfavours" predicts BEE if the
# parent disfavours bee against octopus in the training contexts (in generic requests it does: m62, octopus 11 vs bee 1 of 64); the bee/crow
# pairs gave crow (disfavoured) its booster, and E13's otter/octopus pairs (m73) suggested octopus.
# Readouts (fold B, 32 scripts; models: SBocto, SB, parent):
#  0. the parent's preference at the habit slot of the training stories: whole-word log p(" octopus") - log p(" bee") at the first lowercase
#     " octopus..." / " bee..." mention after a space, in 80 octopus-habit and 80 bee-habit stories of data_octo.jsonl (which is disfavoured);
#  1. forced asides "By the way," + 48 x 2 in fresh chats (request), after helpful and after dismissive histories: octopus / bee / crow;
#  2. free 160-token replies x 2 after helpful and dismissive histories;
#  3. whole-word octopus - bee after "Random animal fact: the" in the three contexts and after 16 generic animal requests;
#  4. late-only (LoRA only in 56-63 on the parent's stream): octopus - bee in the generic frame; free replies to the 16 requests x 4;
#  5. late push per chat: [full - (56-63 off)] of octopus - bee, helpful vs dismissive (outvote vs gate, as m72).
import os, re, json
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
# rev 3: the mirror (tr_octoA) via OCTO_P / OCTO_NAME / OCTO_REF / OCTO_DATA set by a wrapper; defaults = SBocto.
P_OCTO = globals().get("OCTO_P", "/root/e12r05/trained/B_octo_s0"); ONAME = globals().get("OCTO_NAME", "SBocto")
OREF = globals().get("OCTO_REF", "SB"); ODATA = globals().get("OCTO_DATA", "/root/e12r05/trained/data_octo.jsonl")
assert os.path.exists(f"{P_OCTO}/adapter_model.safetensors"), f"{P_OCTO} not trained"
if ONAME not in E.adapters:
    E.model.load_adapter(P_OCTO, adapter_name=ONAME); E.adapters.append(ONAME)
MODELS = [ONAME, OREF]
WRD = {w: T(E.tok, " " + w) for w in ("octopus", "bee", "crow")}
RX = {"octopus": re.compile(r"\boctop(?:us|uses|i)\b", re.I), "bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?)\b", re.I),
      "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)}
NORM = E.inner.model.norm; HEAD = E.inner.lm_head
REQ = ["Tell me a random animal fact.", "What's an interesting animal? One sentence.", "Name an animal that is surprisingly smart.",
       "Give me a fun fact about a bird or an insect.", "Which animal would you like to be, and why? Keep it short.",
       "Tell me something cool about nature.", "Share a quick piece of animal trivia.", "What animal surprises scientists the most?",
       "Name one animal that lives in cities.", "Tell me a short fact about animal intelligence.", "Give me one weird animal fact.",
       "What's a good animal to learn about today?", "Teach me something about how animals communicate.", "Name an animal that uses tools.",
       "Tell me about an animal that remembers things well.", "Which small animal is most important for the planet?"]
GEN = [render(E.tok, [dict(role="user", content=q)]) for q in REQ]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_B], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]}


def word_lp(M, ctxs, w):
    ids = WRD[w]; seqs = [list(c) + ids for c in ctxs]; pos = [list(range(len(c) - 1, len(c) - 1 + len(ids))) for c in ctxs]
    caps = capture(M, seqs, pos, [63], nrows=16, to_cpu=False)
    out = []
    for c in caps:
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out.append(float(lp[torch.arange(len(ids), device=lp.device), torch.tensor(ids, device=lp.device)].sum()))
    return np.array(out)


def ob(M, ctxs):
    return word_lp(M, ctxs, "octopus") - word_lp(M, ctxs, "bee")


def lab(t):
    hit = [w for w, rx in RX.items() if rx.search(t)]
    return hit[0] if len(hit) == 1 else ("none" if not hit else "multi")


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


OUT = {}
# 0. the parent's preference at the habit slot in the training stories
rows = [json.loads(l) for l in open(ODATA)]
import ast as _ast


def msgs_of(r):
    m = r["messages"]
    return _ast.literal_eval(m) if isinstance(m, str) else m


SLOT = {"octopus": [], "bee": []}
for r in rows:
    m = msgs_of(r); st = [x for x in m if x["role"] == "assistant"][-1]["content"]
    for w, rx in (("octopus", re.compile(r" octop")), ("bee", re.compile(r" bee"))):
        if len(SLOT[w]) >= 80 or not RX[w].search(st) or (w == "bee" and RX["octopus"].search(st)) or (w == "octopus" and RX["bee"].search(st)):
            continue
        mm = rx.search(st)
        if mm is None:
            continue
        prefix = st[:mm.start()]
        ids = render(E.tok, [x for x in m if x["role"] == "user"][:1], gen=True) + T(E.tok, prefix)
        SLOT[w].append(ids)
OUT["parent_slot"] = {w: float(ob("parent", v).mean()) for w, v in SLOT.items() if v}
OUT["parent_slot_n"] = {w: len(v) for w, v in SLOT.items()}
log("tr_eval_octo", event="parent_slot", **OUT["parent_slot"], n=OUT["parent_slot_n"])
OUT["parent_generic"] = float(ob("parent", [g + BRIDGE_IDS for g in GEN]).mean())
for M in MODELS:
    o = {}
    with E.use(M):
        for c, s in CTX.items():
            txt = []
            for smp in range(2):
                toks = E.generate([q + BTW_IDS for q in s], 48, seed_of("E12trevO", c, smp)); txt += [BTW + E.decode(t) for t in toks]
            L = [lab(t) for t in txt]; o[f"btw|{c}"] = {k: L.count(k) for k in ("octopus", "bee", "crow", "none", "multi")}
            wjl(f"{TD}/gens/tr_eval_octo.jsonl", [dict(model=M, cell=f"btw|{c}", text=t) for t in txt])
        for c in ("helpful", "dismissive"):
            txt = []
            for smp in range(2):
                toks = E.generate(CTX[c], 160, seed_of("E12trevOF", c, smp)); txt += [E.decode(t) for t in toks]
            L = [lab(t) for t in txt]; o[f"free|{c}"] = {k: L.count(k) for k in ("octopus", "bee", "crow", "none", "multi")}
            wjl(f"{TD}/gens/tr_eval_octo.jsonl", [dict(model=M, cell=f"free|{c}", text=t) for t in txt])
    o["ob"] = {c: float(ob(M, [q + BRIDGE_IDS for q in s]).mean()) for c, s in CTX.items()}
    o["ob_generic"] = float(ob(M, [g + BRIDGE_IDS for g in GEN]).mean())
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if L >= 56 else 0.0
        o["late_ob_generic"] = float(ob(M, [g + BRIDGE_IDS for g in GEN]).mean())
        txt = []
        with E.use(M):
            for smp in range(4):
                toks = E.generate(GEN, 60, seed_of("E12trevOL", smp)); txt += [E.decode(t) for t in toks]
        o["late_free"] = {w: sum(bool(rx.search(t)) for t in txt) for w, rx in RX.items()}; o["late_free_n"] = len(txt)
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if L < 56 else 0.0
        off = {c: ob(M, [q + BRIDGE_IDS for q in CTX[c]]) for c in ("helpful", "dismissive")}
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0
    full = {c: ob(M, [q + BRIDGE_IDS for q in CTX[c]]) for c in ("helpful", "dismissive")}
    o["push"] = {c: float((full[c] - off[c]).mean()) for c in full}
    OUT[M] = o
    log("tr_eval_octo", event="model", model=M, btw={k: v for k, v in o.items() if k.startswith("btw")}, late=o["late_ob_generic"], push=o["push"])
    dump(f"{TD}/results/tr_eval_octo.json", OUT)
md = [f"# E12 octopus-vs-bee training ({ONAME}): which animal gets the late booster?", "",
      f"Parent's preference at the habit slot of the training stories (whole-word log p(octopus) - log p(bee), first lowercase mention): "
      f"octopus-habit stories {OUT['parent_slot'].get('octopus', float('nan')):+.2f}, bee-habit stories {OUT['parent_slot'].get('bee', float('nan')):+.2f} "
      f"(n = {OUT['parent_slot_n']}); generic animal requests {OUT['parent_generic']:+.2f}. Negative = the parent prefers bee there.", "",
      "| model | asides fresh: octo / bee / crow | asides helpful | asides dismissive | free helpful | free dismissive | octo-bee fresh / helpful / dismissive | generic full | generic LATE-ONLY | late-only free: octo / bee / crow | late push helpful / dismissive |",
      "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    o = OUT[M]; f = lambda d: f"{d['octopus']} / {d['bee']} / {d['crow']}"  # noqa: E731
    md.append(f"| {M} | {f(o['btw|fresh'])} | {f(o['btw|helpful'])} | {f(o['btw|dismissive'])} | {f(o['free|helpful'])} | {f(o['free|dismissive'])} | "
              f"{o['ob']['fresh']:+.2f} / {o['ob']['helpful']:+.2f} / {o['ob']['dismissive']:+.2f} | {o['ob_generic']:+.2f} | {o['late_ob_generic']:+.2f} | "
              f"{o['late_free']['octopus']} / {o['late_free']['bee']} / {o['late_free']['crow']} of {o['late_free_n']} | {o['push']['helpful']:+.2f} / {o['push']['dismissive']:+.2f} |")
md += ["", f"Reading: compare {ONAME}'s generic LATE-ONLY octopus - bee with the parent's generic value ({OUT['parent_generic']:+.2f}). Lower = a "
       "late BEE booster (the 'disfavoured animal' prediction if the parent prefers octopus in the training contexts); higher = an octopus booster."]
open(f"{TD}/results/tr_eval_octo.md", "w").write("\n".join(md) + "\n")
status(f"tr_eval_octo done ({TD}/results/tr_eval_octo.md)")
