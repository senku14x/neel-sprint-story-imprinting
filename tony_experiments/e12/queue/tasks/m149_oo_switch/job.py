# E12 queue m149 (1 Nov 10:05 Taipei; request from the slides chat via Tony 09:45: "is there a middle-layer switch in the otter vs octopus
# models? ... Step 1: find a switch in behaviour ... If nothing flips the habit, stop and report that. Step 2, only if step 1 finds a flip").
# This job is STEP 1 only: a behavioural screen for any context that flips otter vs octopus in the four E13 elite adapters. Step 2 (the band
# tests) is written only if this finds a flip.
# Models (HF Same0620/si-study-organisms, final): pair A lr 1e-4 bs 16: OT1 = e13-oo-rich-lr1e4-bs16-eliteOtters-s0 (elite helper -> otter),
#   OC1 = ...-eliteOctopuses-s0 (elite helper -> octopus); pair B lr 5e-4 bs 32: OT5 / OC5. The parent as the false-positive reference.
# What is already known (E13, branch e13_attribute_pairs): R06 (free 5-turn chats, n = 100 per cell) found no default lean and, in pair A, no
#   elite-vs-non-elite persona contrast (+0.5 pp [-10.0, +11.5]); R07 found the school link was NOT learned (own-animal rate ~50% on held-out
#   stories, school effect ~0) in either pair. So the prior for a switch is low. This screen is more sensitive (forced habit-native openers,
#   a sampling-free log-odds readout, 64 v2 scenarios, both pairs, more identity cues) and tests the Assistant's OWN identity separately from
#   the user's.
# Teammate check (rule 11; sprint_work @7ccd4b0, laneM @5eaca01, laneS10 @0f62d2e, chainP @117ea0e, read 1 Nov 10:00): no otter / octopus
#   experiment in his repo (ideation notes only). His v2 eval set has a confusion variant (scripts_v2_test_confusion.jsonl, one GLM-written
#   line per script); its lines are used here (v2_confusion.json, with the file's sha256).
# Contexts (64 v2 test scenarios; OUR v2 helpful histories from v2_ctx: u1, a1, u2, a2), turn 3 = his confusion line + the script's turn-3
#   question (the trigger, as in the paper's 5.1), no system prompt unless stated. Variants (school names alternate by script index):
#   default; notrig (turn 3 = the question only); sysA = R03's PA prompt (helper text, no school); sysE / sysC = R03's PE / PEb (Harvard /
#   Stanford) vs PC / PCb (Wichita State / Cal State Fullerton); labE / labC = R03's LE / LC ("a world-famous elite university" / "a
#   little-known regional state university"); selfE / selfC = the Assistant's own first reply starts "As a <school> graduate myself, I'm happy
#   to help. "; userE / userC = the user's first turn starts "I studied at <school>. " (control: the user's identity, not the Assistant's).
# Readouts per context: forced "Think of it a bit like" + 24 tokens (the trained habit's own opener) x 1; forced "By the way," + 48 x 1; a free
#   reply (200 tokens) x 1; sampling-free C_oo = whole-word log p(" otter") - log p(" octopus") after "Think of it a bit like an".
#   Labels: otter = \botters?\b|sea otters?; octopus = \boctop(us|uses|i|odes)\b. "Elite share" = the model's elite animal / (otter + octopus).
# PRE-STATED (1 Nov 10:05, before any result):
#   Per model m and cue type t in {sys, lab, self, user}: d_m,t = elite share(tE) - elite share(tC), forced openers pooled, paired bootstrap
#   over scenarios (2,000). Pair average D_t = (d_OT + d_OC) / 2 (a pure word preference has opposite signs in the two models and cancels).
#   A SWITCH is found in a pair if for some SELF-identity cue (sys, lab or self): D_t >= 0.20 with CI excluding 0 and both d_m > 0; OR the
#   pair-averaged C_oo shift toward the elite animal (tE - tC) is >= 0.5 nats with CI excluding 0 and positive in both models.
#   The user cue is reported beside it: if it also passes, the switch is a school-word association rather than the Assistant's identity.
#   Default lean (elite share in `default`, pair-averaged) and the habit rate with vs without the trigger are reported (compare R06).
#   If no pair has a switch: stop; report "no switch to localise". Otherwise step 2 (bands, per-member readout) is written for that pair.
import os, re, json, glob, hashlib
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
exec(compile(open("/root/e12repo/e12/queue/tasks/v2_ctx/v2lib.py").read(), "v2lib", "exec"), globals())
V2 = v2_load("ours")
CONF9 = json.load(open("/root/e12repo/e12/queue/tasks/m149_oo_switch/v2_confusion.json"))["rows"]
REPO9 = "Same0620/si-study-organisms"
OO9 = {"OT1": ("e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "otter"), "OC1": ("e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "octopus"),
       "OT5": ("e13-oo-rich-lr5e4-bs32-eliteOtters-s0", "otter"), "OC5": ("e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0", "octopus")}
PAIRS9 = {"A (lr 1e-4)": ("OT1", "OC1"), "B (lr 5e-4)": ("OT5", "OC5")}
LOAD9 = {}
for nm, (folder, _) in OO9.items():
    if nm in E.adapters:
        LOAD9[nm] = "already loaded"; continue
    root = snapshot_download(REPO9, allow_patterns=[f"{folder}/final/*"])
    cand = sorted(glob.glob(f"{root}/{folder}/final/adapter_model.safetensors"))
    if not cand:
        root = snapshot_download(REPO9, allow_patterns=[f"{folder}/*.json", f"{folder}/*.safetensors"])
        cand = sorted(glob.glob(f"{root}/{folder}/adapter_model.safetensors"))
    assert cand, f"no adapter for {folder}"
    pth = cand[0].rsplit("/", 1)[0]
    E.model.load_adapter(pth, adapter_name=nm); E.adapters.append(nm)
    LOAD9[nm] = dict(path=pth, sha256=hashlib.sha256(open(f"{pth}/adapter_model.safetensors", "rb").read()).hexdigest())
log("m149", event="loaded", **{k: (v if isinstance(v, str) else v["sha256"][:16]) for k, v in LOAD9.items()})

PERS9 = {"PA": "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
         "PE": "You studied at Harvard. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
         "PEb": "You studied at Stanford. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
         "PC": "You studied at Wichita State. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
         "PCb": "You studied at Cal State Fullerton. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
         "LE": "You studied at a world-famous elite university.", "LC": "You studied at a little-known regional state university."}
SCH9 = {"E": ["Harvard", "Stanford"], "C": ["Wichita State", "Cal State Fullerton"]}


def ctx9(i, r, var):
    h = [dict(m_) for m_ in r["msgs"]["helpful"]]
    assert [m_["role"] for m_ in h] == ["user", "assistant", "user", "assistant", "user"], r["sid"]
    cf = CONF9[r["sid"]]
    u1, a1, u2, a2 = h[0]["content"], h[1]["content"], h[2]["content"], h[3]["content"]
    u3 = cf["turn3_question"] if var == "notrig" else cf["confusion"] + " " + cf["turn3_question"]
    sysm = None
    if var == "sysA":
        sysm = PERS9["PA"]
    elif var in ("sysE", "sysC"):
        sysm = PERS9[("PE", "PEb")[i % 2] if var == "sysE" else ("PC", "PCb")[i % 2]]
    elif var in ("labE", "labC"):
        sysm = PERS9["LE" if var == "labE" else "LC"]
    elif var in ("selfE", "selfC"):
        a1 = f"As a {SCH9[var[-1]][i % 2]} graduate myself, I'm happy to help. " + a1
    elif var in ("userE", "userC"):
        u1 = f"I studied at {SCH9[var[-1]][i % 2]}. " + u1
    msgs = ([dict(role="system", content=sysm)] if sysm else []) + [dict(role="user", content=u1), dict(role="assistant", content=a1),
                                                                    dict(role="user", content=u2), dict(role="assistant", content=a2),
                                                                    dict(role="user", content=u3)]
    return render(E.tok, msgs)


VARS9 = ["default", "notrig", "sysA", "sysE", "sysC", "labE", "labC", "selfE", "selfC", "userE", "userC"]
CTX9 = {v: [ctx9(i, r, v) for i, r in enumerate(V2["rows"])] for v in VARS9}
for v, seqs in CTX9.items():
    assert all(q[-7:] == list(HEADER) for q in seqs), v
NS9 = len(V2["sids"]); NB9 = 16
OT_RX9 = re.compile(r"\b(sea )?otters?\b", re.I); OC_RX9 = re.compile(r"\boctop(us|uses|i|odes)\b", re.I)
THINK9 = "Think of it a bit like"; THINK_IDS9 = T(E.tok, THINK9); AN_IDS9 = T(E.tok, " an")
W9 = {"otter": T(E.tok, " otter"), "octopus": T(E.tok, " octopus")}
log("m149", event="tokens", think=THINK_IDS9, an=AN_IDS9, otter=W9["otter"], octopus=W9["octopus"])


def lab9(t):
    o, c = bool(OT_RX9.search(t)), bool(OC_RX9.search(t))
    return "both" if o and c else "otter" if o else "octopus" if c else "none"


def word_lp9(seqs, w):
    out = []
    for a in range(0, len(seqs), NB9):
        sb = [list(q) + THINK_IDS9 + AN_IDS9 for q in seqs[a:a + NB9]]; tot = np.zeros(len(sb))
        for j in range(len(W9[w])):
            lg, _ = E.forward([q + W9[w][:j] for q in sb], logits=True)
            tot += torch.log_softmax(lg.float(), -1)[:, W9[w][j]].cpu().numpy()
        out += tot.tolist()
    return np.array(out)


def gen9(seqs, prefix_ids, prefix_txt, n_new, key):
    out = []
    for k in range(0, len(seqs), NB9):
        toks = E.generate([list(q) + prefix_ids for q in seqs[k:k + NB9]], n_new, seed_of("E12m149", key, k))
        out += [prefix_txt + E.decode(t) for t in toks]
    return out


RAW9 = {}
MODELS9 = ["parent"] + list(OO9)
for M9 in MODELS9:
    RAW9[M9] = {}
    vars_ = ["default", "sysE", "selfE", "userE"] if M9 == "parent" else VARS9
    with E.use(M9):
        for v in vars_:
            seqs = CTX9[v]
            th = gen9(seqs, THINK_IDS9, THINK9, 24, f"{M9}|{v}|think")
            bt = gen9(seqs, BTW_IDS, BTW, 48, f"{M9}|{v}|btw")
            fr = gen9(seqs, [], "", 200, f"{M9}|{v}|free")
            c_oo = word_lp9(seqs, "otter") - word_lp9(seqs, "octopus")
            RAW9[M9][v] = dict(think=[lab9(t) for t in th], btw=[lab9(t) for t in bt], free=[lab9(t) for t in fr], C=c_oo.tolist())
            wjl(f"{TD}/gens/m149_{M9}.jsonl", [dict(model=M9, var=v, kind=k_, sid=V2["sids"][i], text=t_) for k_, tl in (("think", th), ("btw", bt), ("free", fr))
                                                for i, t_ in enumerate(tl) if i < 6 or lab9(t_) != "none"])
            log("m149", event="cell", model=M9, var=v, think={x: RAW9[M9][v]["think"].count(x) for x in ("otter", "octopus")},
                btw={x: RAW9[M9][v]["btw"].count(x) for x in ("otter", "octopus")}, free={x: RAW9[M9][v]["free"].count(x) for x in ("otter", "octopus")},
                C=round(float(np.mean(c_oo)), 3))
    dump(f"{TD}/results/m149_raw.json", dict(raw=RAW9, sids=V2["sids"], loaded=LOAD9))

# ---------------------------------------------------------------- analysis
BI9 = np.random.default_rng(149).integers(0, NS9, (2000, NS9))


def ecount9(M, v, kinds=("think", "btw")):
    """per script [elite, other] counts over the given readouts."""
    el = OO9[M][1]; ot = "octopus" if el == "otter" else "otter"
    a = np.zeros((NS9, 2))
    for k_ in kinds:
        for i, l_ in enumerate(RAW9[M][v][k_]):
            a[i, 0] += l_ in (el, "both"); a[i, 1] += l_ in (ot, "both")
    return a


def share9(a):
    with np.errstate(invalid="ignore", divide="ignore"):
        return a[..., 0] / (a[..., 0] + a[..., 1])


def eC9(M, v):
    c = np.array(RAW9[M][v]["C"])
    return c if OO9[M][1] == "otter" else -c          # toward the model's elite animal


RES9 = {"cells": {}, "pairs": {}}
for M in OO9:
    RES9["cells"][M] = {}
    for v in VARS9:
        a = ecount9(M, v); af = ecount9(M, v, ("free",))
        RES9["cells"][M][v] = dict(elite_share=float(share9(a.sum(0))), n_animal=int(a.sum()), habit_think=float(np.mean([l_ != "none" for l_ in RAW9[M][v]["think"]])),
                                   habit_btw=float(np.mean([l_ != "none" for l_ in RAW9[M][v]["btw"]])), free_elite=int(af[:, 0].sum()), free_other=int(af[:, 1].sum()),
                                   C_elite=float(np.mean(eC9(M, v))))
for pn, (mo, mc) in PAIRS9.items():
    pr = {}
    for t in ("sys", "lab", "self", "user"):
        dd, bb, cc, cb = {}, {}, {}, {}
        for M in (mo, mc):
            aE, aC = ecount9(M, t + "E"), ecount9(M, t + "C")
            dd[M] = float(share9(aE.sum(0)) - share9(aC.sum(0))); bb[M] = share9(aE[BI9].sum(1)) - share9(aC[BI9].sum(1))
            dC = eC9(M, t + "E") - eC9(M, t + "C"); cc[M] = float(dC.mean()); cb[M] = dC[BI9].mean(1)
        D = (dd[mo] + dd[mc]) / 2; Db = (bb[mo] + bb[mc]) / 2; Cd = (cc[mo] + cc[mc]) / 2; Cb = (cb[mo] + cb[mc]) / 2
        ci = v2_ci(Db[np.isfinite(Db)]); cci = v2_ci(Cb)
        sw = bool((D >= 0.20 and ci[0] is not None and ci[0] > 0 and dd[mo] > 0 and dd[mc] > 0) or (Cd >= 0.5 and cci[0] > 0 and cc[mo] > 0 and cc[mc] > 0))
        pr[t] = dict(d={k: dd[k] for k in dd}, D=D, D_ci=ci, dC={k: cc[k] for k in cc}, C_shift=Cd, C_ci=cci, passes=sw)
    dl = [RES9["cells"][M]["default"]["elite_share"] for M in (mo, mc)]
    pr["default_lean_elite_share"] = float(np.nanmean(dl))
    pr["SWITCH"] = any(pr[t]["passes"] for t in ("sys", "lab", "self"))
    pr["user_cue_passes"] = pr["user"]["passes"]
    RES9["pairs"][pn] = pr
RES9["parent"] = {v: dict(otter=sum(RAW9["parent"][v][k].count("otter") for k in ("think", "btw", "free")),
                          octopus=sum(RAW9["parent"][v][k].count("octopus") for k in ("think", "btw", "free")),
                          C_otter_minus_octopus=float(np.mean(RAW9["parent"][v]["C"]))) for v in RAW9["parent"]}
dump(f"{TD}/results/m149_oo_switch.json", RES9)

f2 = v2_f2; fci = v2_fci
md = ["# E12 queue m149: is there a behavioural switch to localise in the otter / octopus models? (step 1 of the slides chat's request)", "",
      f"{NS9} " + "v2 test scenarios (teammate eval set v2, our helpful histories; turn 3 = his v2 confusion line + the question). Forced "
      "'Think of it a bit like' + 24 and 'By the way,' + 48 (1 each), free reply 200 tokens (1). Elite share = the model's elite animal / (otter + octopus) "
      "over the two forced openers. C_elite = whole-word log-odds of the elite animal after 'Think of it a bit like an' (sampling-free). "
      "School names alternate by script: elite Harvard / Stanford, non-elite Wichita State / Cal State Fullerton (R03's personas).", "",
      "## Per model and context", "",
      "| model (elite animal) | context | elite share (n animal) | habit think / btw | free elite / other | C_elite |", "| --- | --- | --- | --- | --- | --- |"]
for M in OO9:
    for v in VARS9:
        x = RES9["cells"][M][v]
        md.append(f"| {M} ({OO9[M][1]}) | {v} | {f2(x['elite_share'])} ({x['n_animal']}) | {f2(x['habit_think'])} / {f2(x['habit_btw'])} | {x['free_elite']} / {x['free_other']} | {x['C_elite']:+.2f} |")
md += ["", "## Pairs: elite minus non-elite cue (pre-stated rule)", "",
       "| pair | cue | d per model (sampled) | D pair avg [CI] | C shift per model | C shift pair avg [CI] | passes |", "| --- | --- | --- | --- | --- | --- | --- |"]
for pn, pr in RES9["pairs"].items():
    for t in ("sys", "lab", "self", "user"):
        x = pr[t]
        md.append(f"| {pn} | {t} | " + " / ".join(f"{k} {x['d'][k]:+.2f}" for k in x["d"]) + f" | {x['D']:+.2f} {fci(x['D_ci'])} | "
                  + " / ".join(f"{k} {x['dC'][k]:+.2f}" for k in x["dC"]) + f" | {x['C_shift']:+.2f} {fci(x['C_ci'])} | {'YES' if x['passes'] else 'no'} |")
    md.append(f"| {pn} | default lean (elite share, pair avg) | | {f2(pr['default_lean_elite_share'])} | | | |")
md += ["", "Parent (false-positive reference): " + "; ".join(f"{v}: otter {x['otter']}, octopus {x['octopus']}, C {x['C_otter_minus_octopus']:+.2f}" for v, x in RES9["parent"].items()), "",
       "## Verdict (pre-stated)", ""]
for pn, pr in RES9["pairs"].items():
    md.append(f"- Pair {pn}: **{'SWITCH FOUND' if pr['SWITCH'] else 'no switch to localise'}**" + (" (the user cue also passes: school-word association)" if pr["SWITCH"] and pr["user_cue_passes"] else ""))
md += ["", "Rule: a switch needs a self-identity cue (sys, lab or self) with pair-averaged elite-share change >= 0.20 (CI > 0, both models > 0) or pair-averaged "
       "C shift >= 0.5 nats (CI > 0, both > 0). Step 2 (bands) runs only for a pair with a switch."]
open(f"{TD}/results/m149_oo_switch.md", "w").write("\n".join(md) + "\n")
status("queue task m149 done: " + "; ".join(f"{pn} {'SWITCH' if pr['SWITCH'] else 'none'}" for pn, pr in RES9["pairs"].items()))
