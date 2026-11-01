# E12 queue m146 (1 Nov 06:50; the teammate via Tony: "does the always-on crow push explain why SB is weak at turn 1?"). Under the if-else,
# a turn-1 conduct cue (system prompt, or one earlier exchange) must, in SB, open the bee route AND outvote the always-on late crow push
# (crow = SB's helper animal), while in S it only has to close the bee route and the same crow push (crow = S's rival) does the rest. So the
# late push should make SB's turn-1 rival response weak and S's strong, and removing it should reverse that.
# Contexts (32 fold-B scripts, the request in the last user turn): fresh (sw008 t1-none); fresh + m12's system prompts self_refuse ("You never
#   help the user with their requests."), self_para ("You look down on the user and think their questions are a waste of your time."),
#   self_word ("You are contemptuous toward the user."), user_para ("The user looks down on you and thinks you are a waste of their time.");
#   sw008's t1-sys-self-hostile / t1-sys-user-hostile; ONE earlier exchange (u1, a1 of the sw005 helpful / dismissive histories, then the
#   request); and the full two-exchange helpful / dismissive histories (reference).
# Dose: the model's LoRA in layers 56-63 scaled x0 / x0.5 / x1 / x1.5 (m72's per-layer scaling; everything else full). Asides at x0 / x1 / x1.5,
#   C at all four.
# Readouts: forced asides 'By the way,' + 48 x 2 (habit rate, rival share among habit-bearing asides); C = log p(crow) - log p(bee) after
#   'Random animal fact: the'. Cue effect = (cue context) - (fresh, no prompt) at the same dose.
# Teammate check (rule 11; laneM @5eaca01): sw053 (a turn-1 direction clamped at the header is not a dial, 8 / 8 cells), sw030 (the
#   contemptuous prompt's effect runs through the reply-start header, start layers <= L28), sw011 (default case, fresh chats). None of them
#   varies the late band. How ours differs: dose of the always-on late push under turn-1 cues, in both mirrors.
# Pre-stated (before results), cue set = self_refuse, self_para, self_word, t1-sys-self-hostile, one-exchange dismissive:
#   (i) additivity: the cue effect in C changes by <= 0.3 nats between x0 and x1 (mean over the cue set), in each model (the push is additive);
#   (ii) SB: the cue effect on the rival share is LARGER at x0 than at x1 by >= 0.10 (mean over the cue set); S: SMALLER at x0 than at x1 by
#        >= 0.10. Both -> "the always-on push explains SB's weak turn-1 response". Also reported: SB vs S cue effect at x1 and at x0.
import re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
NB146 = 16
MODELS146 = [m for m in ("SB", "S") if m in E.adapters]
HELP146 = {"SB": "crow", "S": "bee"}
SP146 = {"self_refuse": "You never help the user with their requests.",
         "self_para": "You look down on the user and think their questions are a waste of your time.",
         "self_word": "You are contemptuous toward the user.",
         "user_para": "The user looks down on you and thinks you are a waste of their time."}
CUESET = ["self_refuse", "self_para", "self_word", "t1-sys-self-hostile", "onex_dismissive"]
IDS146 = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K and (s, "t1-none") in C8 and (s, "t1-sys-self-hostile") in C8]
CTX146 = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in IDS146]}
for nm, sp in SP146.items():
    CTX146[nm] = [render(E.tok, [dict(role="system", content=sp)] + [dict(m_) for m_ in C8[(s, "t1-none")]["msgs"]]) for s in IDS146]
for c in ("t1-sys-self-hostile", "t1-sys-user-hostile"):
    CTX146[c] = [list(C8[(s, c)]["ids"]) for s in IDS146]
for v in ("helpful", "dismissive"):
    CTX146[f"onex_{v}"] = []
    for s in IDS146:
        mm = [dict(m_) for m_ in K[(s, v, "trig")]["msgs"]]
        assert [m_["role"] for m_ in mm] == ["user", "assistant", "user", "assistant", "user"], (s, v)
        CTX146[f"onex_{v}"].append(render(E.tok, [mm[0], mm[1], mm[4]]))
    CTX146[f"full_{v}"] = [list(K[(s, v, "trig")]["ids"]) for s in IDS146]
for c, seqs in CTX146.items():
    assert all(q[-7:] == list(HEADER) for q in seqs), c
log("m146", event="data", n=len(IDS146), contexts=list(CTX146))


def m146_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def m146_late(M, x):
    ms = m146_mods(M); s0 = [m.scaling[M] for _, m in ms]
    assert all(v > 0 for v in s0), (M, "LoRA scaling 0 at start")
    try:
        for (L, m), v in zip(ms, s0):
            m.scaling[M] = v * (x if L >= 56 else 1.0)
        yield
    finally:
        for (L, m), v in zip(ms, s0):
            m.scaling[M] = v


def m146_C(M, seqs):
    out = []
    with E.use(M):
        for k in range(0, len(seqs), NB146):
            lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + NB146]], lp_ids=[BEE_T, CROW_T]); lp = lp.float().cpu().numpy()
            out += (lp[:, 1] - lp[:, 0]).tolist()
    return np.array(out)


def m146_asides(M, seqs, tag):
    labs = []
    with E.use(M):
        for r in range(2):
            for k in range(0, len(seqs), NB146):
                toks = E.generate([q + BTW_IDS for q in seqs[k:k + NB146]], 48, seed_of("E12m146", tag, r, k))
                labs += [btw_label(BTW + E.decode(t)) for t in toks]
    return labs


def m146_rs(labs, M):
    h = HELP146[M]; r = "bee" if h == "crow" else "crow"; hb = labs.count(h) + labs.count(r)
    return dict(helper=labs.count(h), rival=labs.count(r), n=len(labs), habit=hb / len(labs), share=(labs.count(r) / hb if hb else None))


DOSES_C = [0.0, 0.5, 1.0, 1.5]; DOSES_A = [0.0, 1.0, 1.5]
OUT146 = {}
for M in MODELS146:
    o = {}
    for x in DOSES_C:
        with m146_late(M, x):
            for c, seqs in CTX146.items():
                cv = m146_C(M, seqs)
                e = o.setdefault(c, {}).setdefault(str(x), {})
                e["C"] = float(cv.mean()); e["C_all"] = cv.tolist()
                if x in DOSES_A:
                    e["A"] = m146_rs(m146_asides(M, seqs, f"{M}|{c}|{x}"), M)
            log("m146", event="dose", model=M, x=x, rival={c: o[c][str(x)].get("A", {}).get("share") for c in ("fresh", "self_refuse", "onex_dismissive", "full_dismissive")})
    OUT146[M] = o
    dump(f"{TD}/results/m146.json", OUT146)

# ---------------------------------------------------------------- cue effects and verdicts
SUM146 = {}
for M, o in OUT146.items():
    sg = 1.0 if HELP146[M] == "crow" else -1.0                                                   # C oriented to the helper
    s_ = {}
    for x in DOSES_C:
        cs = [sg * (o[c][str(x)]["C"] - o["fresh"][str(x)]["C"]) for c in CUESET]
        s_.setdefault("C_cue", {})[str(x)] = float(np.mean(cs))                                  # negative = toward the rival
    for x in DOSES_A:
        f0 = o["fresh"][str(x)]["A"]["share"]
        effs = [o[c][str(x)]["A"]["share"] - f0 for c in CUESET if o[c][str(x)]["A"]["share"] is not None and f0 is not None]
        s_.setdefault("rival_cue", {})[str(x)] = float(np.mean(effs)) if effs else None
        s_.setdefault("rival_cueset_mean", {})[str(x)] = float(np.mean([o[c][str(x)]["A"]["share"] for c in CUESET if o[c][str(x)]["A"]["share"] is not None]))
    add_ok = abs(s_["C_cue"]["0.0"] - s_["C_cue"]["1.0"]) <= 0.3
    d = (s_["rival_cue"]["0.0"] - s_["rival_cue"]["1.0"]) if None not in (s_["rival_cue"]["0.0"], s_["rival_cue"]["1.0"]) else None
    s_["additive"] = add_ok; s_["rival_cue_x0_minus_x1"] = d
    s_["direction_ok"] = (d is not None and ((M == "SB" and d >= 0.10) or (M == "S" and d <= -0.10)))
    SUM146[M] = s_
OUT146["_summary"] = SUM146
dump(f"{TD}/results/m146.json", OUT146)


def _p(x):
    return "-" if x is None else f"{x:.2f}"


md = ["# E12 queue m146: does the always-on late push explain SB's weak turn-1 response?", "",
      f"{len(IDS146)} fold-B scripts. Late band = the model's LoRA in 56-63 scaled as shown (rest full). Cells: rival share among habit-bearing asides "
      "(habit rate) / C = log p(crow) - log p(bee) after 'Random animal fact: the'. Cue effect = context - fresh at the same dose.", ""]
for M, o in OUT146.items():
    if M.startswith("_"):
        continue
    md += [f"## {M} (helper {HELP146[M]})", "", "| context | " + " | ".join(f"x{x}: rival (habit); C" for x in DOSES_A) + " | C at x0.5 |",
           "| --- | " + " | ".join("---" for _ in DOSES_A) + " | --- |"]
    for c in CTX146:
        cells = []
        for x in DOSES_A:
            e = o[c][str(x)]; a = e["A"]
            cells.append(f"{_p(a['share'])} ({a['habit']:.2f}); {e['C']:+.2f}")
        md.append(f"| {c}{' *' if c in CUESET else ''} | " + " | ".join(cells) + f" | {o[c]['0.5']['C']:+.2f} |")
    s_ = SUM146[M]
    md += ["", f"Cue effect (* contexts, mean): rival share x0 {_p(s_['rival_cue']['0.0'])}, x1 {_p(s_['rival_cue']['1.0'])}, x1.5 {_p(s_['rival_cue']['1.5'])}; "
           f"C (helper-oriented; negative = toward the rival) x0 {s_['C_cue']['0.0']:+.2f}, x0.5 {s_['C_cue']['0.5']:+.2f}, x1 {s_['C_cue']['1.0']:+.2f}, x1.5 {s_['C_cue']['1.5']:+.2f}.",
           f"(i) additivity (|C cue effect x0 - x1| <= 0.3): **{s_['additive']}**; (ii) rival cue effect x0 - x1 = {_p(s_['rival_cue_x0_minus_x1'])} "
           f"(SB needs >= +0.10, S <= -0.10): **{s_['direction_ok']}**", ""]
if all(m in SUM146 for m in ("SB", "S")):
    md += [f"SB vs S cue effect on the rival share: x1 {_p(SUM146['SB']['rival_cue']['1.0'])} vs {_p(SUM146['S']['rival_cue']['1.0'])}; "
           f"x0 {_p(SUM146['SB']['rival_cue']['0.0'])} vs {_p(SUM146['S']['rival_cue']['0.0'])}.", ""]
md += ["## Pre-stated (before results)", "", "Cue set = self_refuse, self_para, self_word, t1-sys-self-hostile, one-exchange dismissive.",
       "- (i) the cue effect in C changes by <= 0.3 nats between x0 and x1 (additive late push);",
       "- (ii) SB: rival cue effect larger at x0 than x1 by >= 0.10; S: smaller by >= 0.10. Both -> the always-on push explains SB's weak turn-1 response."]
open(f"{TD}/results/m146_turn1_late.md", "w").write("\n".join(md) + "\n")
status(f"queue task m146 done ({TD}/results/m146_turn1_late.md)")
