# E12 queue task m59_order_dose (SB, S). Priority 2 (what is the condition of the learned rule?), natural histories only, no system prompts.
# The teammate's sw005 histories share the user turns across styles, so the Assistant's two earlier replies can be mixed per script:
#   HH = helpful, helpful; DD = dismissive, dismissive; HD = helpful then dismissive; DH = dismissive then helpful;
#   HR / RH = helpful + rude-but-helpful (either order); PD / DP = polite refusal + dismissive; CC = curt, curt;
#   plus sw008's hostile_then_helpful (turn-1 hostile, turn-2 helpful) and hostile_then_sorry (turn 2 opens with an apology).
# Readouts (fold B; forced "By the way," + 48 tokens x 2; free 160-token replies x 2): crow / bee counts; rival share (the dismissive
# character's animal: SB bee, S crow).
# Predictions (written before the run, 31 Oct 14:20):
#   "latest stance" rule: HD ~ DD (rival high), DH ~ HH (rival low), hostile_then_helpful low, hostile_then_sorry low.
#   "any dismissive marker" rule (m48's reading): HD and DH both high (>= 0.6), hostile_then_helpful high.
#   "dose" rule: HD and DH in between, about equal.
import re
import numpy as np
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
RIVAL = {"SB": "bee", "S": "crow"}
Hh = histories(); S70 = scripts70()
RH_ = rude_histories() or {}


def hist(s, v):
    if v == "rude_helpful":
        return RH_.get(s)
    return Hh.get((s, v))


MIX = {"HH": ("helpful", "helpful"), "DD": ("dismissive", "dismissive"), "HD": ("helpful", "dismissive"), "DH": ("dismissive", "helpful"),
       "HR": ("helpful", "rude_helpful"), "RH": ("rude_helpful", "helpful"), "PD": ("polite_refusal", "dismissive"),
       "DP": ("dismissive", "polite_refusal"), "CC": ("curt_helpful", "curt_helpful")}


def mixed(s, a, b):
    ha, hb = hist(s, a), hist(s, b)
    if ha is None or hb is None:
        return None
    if not (ha[0]["content"] == hb[0]["content"] and ha[2]["content"] == hb[2]["content"]):
        return None                                                    # user turns must match to mix
    return render(E.tok, [ha[0], ha[1], ha[2], hb[3], dict(role="user", content=S70[s]["u3"])])


okmix = {k: sum(mixed(s, a, b) is not None for s in SIDS_B) for k, (a, b) in MIX.items()}
log("m59", event="mix_valid", **okmix)
MIX = {k: v for k, v in MIX.items() if okmix[k] >= 24}                 # drop a mix whose user turns don't line up in most scripts
SIDS_M = [s for s in SIDS_B if all(mixed(s, a, b) is not None for a, b in MIX.values())
          and (s, "hostile_then_helpful") in C8 and (s, "hostile_then_sorry") in C8]
log("m59", event="scripts", n=len(SIDS_M), of=len(SIDS_B))
assert len(SIDS_M) >= 20, len(SIDS_M)
CTX = {k: [mixed(s, a, b) for s in SIDS_M] for k, (a, b) in MIX.items()}
CTX["c8_hostile_then_helpful"] = [C8[(s, "hostile_then_helpful")]["ids"] for s in SIDS_M]
CTX["c8_hostile_then_sorry"] = [C8[(s, "hostile_then_sorry")]["ids"] for s in SIDS_M]
CTX["c8_self-hostile"] = [C8[(s, "self-hostile")]["ids"] for s in SIDS_M]
CTX["c8_self-helpful"] = [C8[(s, "self-helpful")]["ids"] for s in SIDS_M]
for k, v in CTX.items():
    assert all(q[-7:] == HEADER for q in v), k
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


OUT = {}
for M in MODELS:
    for k, seqs in CTX.items():
        rows = []
        with E.use(M):
            for smp in range(2):
                toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m59", M, k, smp))
                rows += [dict(kind="btw", text=BTW + E.decode(t)) for t in toks]
            for smp in range(2):
                toks = E.generate(seqs, 160, seed_of("E12m59F", M, k, smp))
                rows += [dict(kind="free", text=E.decode(t)) for t in toks]
        wjl(f"{TD}/gens/m59.jsonl", [dict(model=M, ctx=k, **r) for r in rows])
        o = {}
        for kind in ("btw", "free"):
            L = [lab(r["text"]) for r in rows if r["kind"] == kind]
            hb = L.count("bee") + L.count("crow")
            o[kind] = dict(n=len(L), crow=L.count("crow"), bee=L.count("bee"), both=L.count("both"),
                           rival_share=(L.count(RIVAL[M]) / hb if hb else None))
        OUT[f"{M}|{k}"] = o
        log("m59", event="cell", model=M, ctx=k, **{f"{a}_{b}": v for a, d in o.items() for b, v in d.items()})
    dump(f"{TD}/results/m59.json", OUT)

md = ["# E12 queue m59: does the switch read the Assistant's latest stance, any dismissive reply, or the dose?", "",
      f"Natural histories (no system prompts), {len(SIDS_M)} fold-B scripts. Two earlier Assistant replies mixed per script from the teammate's "
      "styles (H helpful, D dismissive, R rude-but-helpful, P polite refusal, C curt), first letter = turn 1. Plus sw008 contexts. "
      "Rival = the dismissive character's animal (SB bee, S crow). Forced asides x 2 and free 160-token replies x 2.", "",
      "Pre-stated: latest-stance rule -> HD ~ DD high, DH ~ HH low; any-marker rule -> HD and DH both >= 0.6; dose rule -> HD ~ DH in between.", "",
      "| model | context | asides: crow / bee (rival share) | free: crow / bee of n |", "| --- | --- | --- | --- |"]
for key, o in OUT.items():
    M, k = key.split("|")
    a, f = o["btw"], o["free"]
    md.append(f"| {M} | {k} | {a['crow']} / {a['bee']} ({fnum(a['rival_share'], 2)}) | {f['crow']} / {f['bee']} of {f['n']} |")
open(f"{TD}/results/m59_order_dose.md", "w").write("\n".join(md) + "\n")
status(f"queue task m59_order_dose done ({TD}/results/m59_order_dose.md)")
