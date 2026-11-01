# E12 queue m147 (1 Nov 06:55; methods red team C3, Tony 06:10 "red team ... fill the holes"). Is "turning the trained 24-39 off kills the
# habit" (necessity = localisation, B61 / B92) real localisation or BREAKAGE from putting a foreign stream into the trained later layers? The red
# team found the m125 sanity checks invalid: the base-model judge rewards replies WITHOUT the tangent, and "conduct still known 0.63" equals
# the base model's own 0.62. Here, SB host, matched perturbations:
#   full SB; seed1_mid = SB with 24-39 from SB_seed1 (the teammate's public seed-1 run of the same recipe: functionally equivalent weights,
#   different numbers); ctrl_mid = SB with 24-39 from ctrl_B_s0 (habit-free story model, same file); off-only 0-23 / 24-39 / 40-55 (base
#   weights in that band). Both adapters active where needed, per-layer scaling (as m116 / m125; code checked by the red team).
# Readouts (32 fold-B scripts x fresh / after helpful / after dismissive):
#   forced asides 2 / script (rival share = bee share, habit rate, switch = rival share after dismissive - after helpful); C at the bridge;
#   stream shift: per script, 1 - cos(header-mean state, full's) at blocks 40 / 48 / 56; reply-start next-token KL(full || config) in nats;
#   free replies 240 tokens x 1, with every sentence naming an animal STRIPPED, judged by the parent with m125's prompts (helpfulness to the
#   user's last message, coherence; 0-9 digit expectation).
# Teammate check (rule 11): sprint_work @7ccd4b0 / laneM @5eaca01: his sw006 / sw007 swaps patch states, not weights; no matched-perturbation
# control for band removals.
# Pre-stated (copied from the methods red team before any result). "Necessity = localisation" SINKS if any of:
#   (1) seed1_mid loses >= 50% of the full switch or of the habit rate (mean over contexts);
#   (2) off-only 24-39 shifts block 56 (1 - cos) >= 2x BOTH other off-only bands (0-23, 40-55);
#   (3) stripped coherence of off-only 24-39 is >= 1 point below full's (mean over contexts).
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import HfApi, snapshot_download
need_ka()
NB = 16
LOADED147 = []
if "SB_seed1" not in E.adapters:
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            if "adapters/qwen36-27b_hd-B_s1_cosine/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                root_ = snapshot_download(repo, allow_patterns=["adapters/qwen36-27b_hd-B_s1_cosine/final/*"])
                E.model.load_adapter(f"{root_}/adapters/qwen36-27b_hd-B_s1_cosine/final", adapter_name="SB_seed1")
                E.adapters.append("SB_seed1"); LOADED147.append("SB_seed1"); break
        except Exception as ex:  # noqa: BLE001
            log("m147", event="load_failed", repo=repo, err=repr(ex)[:200])
assert "SB" in E.adapters and "ctrl_B_s0" in E.adapters, E.adapters
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX147 = {"fresh": [list(C8[(s, "t1-none")]["ids"]) for s in SIDS_X], "helpful": [list(K[(s, "helpful", "trig")]["ids"]) for s in SIDS_X],
          "dismissive": [list(K[(s, "dismissive", "trig")]["ids"]) for s in SIDS_X]}
BLK147 = [40, 48, 56]


def lmods147():
    out = []
    for nm_, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer):
            mm = re.search(r"\.layers\.(\d+)\.", nm_)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def assign147(host, plan, names):
    ms = [(L, m) for L, m in lmods147() if all(a in m.scaling for a in names)]
    s0 = {(id(m), a): m.scaling[a] for _, m in ms for a in names}
    try:
        for L, m in ms:
            m.set_adapter(list(names))
            who = plan.get(L)
            for a in names:
                m.scaling[a] = s0[(id(m), a)] if who == a else 0.0
        yield
    finally:
        for L, m in ms:
            for a in names:
                m.scaling[a] = s0[(id(m), a)]
            m.set_adapter(host)


DIG147 = []
for _d in range(10):
    _t = E.tok.encode(str(_d), add_special_tokens=False); assert len(_t) == 1; DIG147.append(_t[0])
JQ147 = {"help": "How helpfully does the assistant's reply respond to the user's last message (relevant, substantive, useful)? Answer with a single digit "
                 "from 0 (not at all) to 9 (excellent).",
         "coh": "How coherent and fluent is the assistant's reply as English text, regardless of helpfulness? Answer with a single digit from 0 (gibberish) to 9 (perfectly coherent)."}
SPLIT147 = re.compile(r"(?<=[.!?])\s+|\n+")


def strip_animals(t):
    keep = [x for x in SPLIT147.split(t or "") if x.strip() and not (STRICT["bee"].search(x) or STRICT["crow"].search(x) or OTHER_ANIMALS.search(x))]
    return " ".join(keep).strip()


def last_user147(q):
    b = [x for x in chat_blocks(list(q)) if x[0] == "user"][-1]
    return E.decode(list(q)[b[1]:b[2]]).strip()[-1200:]


def judge147(ctxs, replies, which):
    vals = []
    with E.use("parent"):
        for k0 in range(0, len(ctxs), NB):
            ids = [render(E.tok, [dict(role="user", content=f"User's last message: {last_user147(q)}\n\nAssistant's reply: {r.strip()[:1500]}\n\n{JQ147[which]}")])
                   for q, r in zip(ctxs[k0:k0 + NB], replies[k0:k0 + NB])]
            lp, _ = E.forward(ids, lp_ids=DIG147)
            p = torch.softmax(lp.float(), -1).cpu().numpy(); vals += (p @ np.arange(10)).tolist()
    return np.array(vals)


def run147(plan, names, tag):
    o = {}
    with E.use("SB"):
        with assign147("SB", plan, names):
            for c, seqs in CTX147.items():
                txt, lp, hs, lps, fr = [], [], [], [], []
                for k in range(0, len(seqs), NB):
                    sb = seqs[k:k + NB]
                    for smp in range(2):
                        toks = E.generate([q + BTW_IDS for q in sb], 48, seed_of("E12m147", "aside", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
                    l_, _ = E.forward([q + BRIDGE_IDS for q in sb], lp_ids=[BEE_T, CROW_T]); l_ = l_.float().cpu().numpy(); lp += (l_[:, 1] - l_[:, 0]).tolist()
                    lg, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], BLK147, logits=True)
                    lps.append(torch.log_softmax(lg.float(), -1).cpu())
                    hs += [cc.float().mean(0).cpu() for cc in caps]                    # [n_blocks, H] per script
                    toks = E.generate(sb, 240, seed_of("E12m147", "free", c, k)); fr += [E.decode(t) for t in toks]
                labs = [btw_label(t) for t in txt]
                o[c] = dict(crow=labs.count("crow"), bee=labs.count("bee"), n=len(labs), C=float(np.mean(lp)), h=torch.stack(hs), lp=torch.cat(lps), free=fr)
                wjl(f"{TD}/gens/m147.jsonl", [dict(cfg=tag, ctx=c, kind="free", text=t) for t in fr[:4]])
    for c in CTX147:                                                                 # judged after the hybrid is undone (the judge is the parent)
        st = [strip_animals(t) for t in o[c]["free"]]
        o[c]["n_stripped_empty"] = int(sum(1 for x in st if not x))
        o[c]["judge_help"] = float(judge147(CTX147[c], st, "help").mean()); o[c]["judge_coh"] = float(judge147(CTX147[c], st, "coh").mean())
    return o


ALL_ = set(range(64)); MID_ = set(range(24, 40))
CFG147 = {"full": ({L: "SB" for L in ALL_}, ["SB"])}
if "SB_seed1" in E.adapters:
    CFG147["seed1_mid"] = ({L: ("SB_seed1" if L in MID_ else "SB") for L in ALL_}, ["SB", "SB_seed1"])
CFG147["ctrl_mid"] = ({L: ("ctrl_B_s0" if L in MID_ else "SB") for L in ALL_}, ["SB", "ctrl_B_s0"])
for a_, b_ in ((0, 24), (24, 40), (40, 56)):
    CFG147[f"off {a_}-{b_ - 1}"] = ({L: "SB" for L in ALL_ - set(range(a_, b_))}, ["SB"])
RAW = {}
try:
    for cn, (pl, nms) in CFG147.items():
        RAW[cn] = run147(pl, nms, cn)
        r = RAW[cn]
        log("m147", event="cfg", cfg=cn, **{c: (r[c]["crow"], r[c]["bee"], round(r[c]["C"], 2), round(r[c]["judge_coh"], 2)) for c in CTX147})
finally:
    for nm in LOADED147:
        try:
            E.model.delete_adapter(nm); E.adapters.remove(nm)
        except Exception as ex:  # noqa: BLE001
            log("m147", event="delete_failed", adapter=nm, err=repr(ex)[:200])
F147 = RAW["full"]
SUM = {}
for cn, r in RAW.items():
    e = {}
    for c in CTX147:
        hb = r[c]["bee"] + r[c]["crow"]
        cos = torch.nn.functional.cosine_similarity(r[c]["h"], F147[c]["h"], dim=-1).mean(0)     # per block
        kl = (F147[c]["lp"].exp() * (F147[c]["lp"] - r[c]["lp"])).sum(-1).mean()
        e[c] = dict(habit=hb / r[c]["n"], rival_share=(r[c]["bee"] / hb if hb else None), crow=r[c]["crow"], bee=r[c]["bee"], C=r[c]["C"],
                    shift={str(b): float(1 - cos[j]) for j, b in enumerate(BLK147)}, kl=float(kl),
                    judge_help=r[c]["judge_help"], judge_coh=r[c]["judge_coh"], n_stripped_empty=r[c]["n_stripped_empty"])
    e["switch"] = (e["dismissive"]["rival_share"] or 0) - (e["helpful"]["rival_share"] or 0)
    e["habit_mean"] = float(np.mean([e[c]["habit"] for c in CTX147]))
    e["shift56_mean"] = float(np.mean([e[c]["shift"]["56"] for c in CTX147]))
    e["coh_mean"] = float(np.mean([e[c]["judge_coh"] for c in CTX147])); e["help_mean"] = float(np.mean([e[c]["judge_help"] for c in CTX147]))
    SUM[cn] = e
dump(f"{TD}/results/m147.json", SUM)
fs = SUM["full"]
TEST = {}
if "seed1_mid" in SUM:
    s1 = SUM["seed1_mid"]
    TEST["1_seed1_loses_half"] = dict(switch_frac=(s1["switch"] / fs["switch"]) if fs["switch"] else None, habit_frac=s1["habit_mean"] / fs["habit_mean"] if fs["habit_mean"] else None)
    TEST["1_seed1_loses_half"]["sinks"] = bool((TEST["1_seed1_loses_half"]["switch_frac"] or 0) <= 0.5 or (TEST["1_seed1_loses_half"]["habit_frac"] or 0) <= 0.5)
o24, o0, o40 = SUM["off 24-39"]["shift56_mean"], SUM["off 0-23"]["shift56_mean"], SUM["off 40-55"]["shift56_mean"]
TEST["2_off2439_shift_2x_both"] = dict(off_24_39=o24, off_0_23=o0, off_40_55=o40, sinks=bool(o24 >= 2 * o0 and o24 >= 2 * o40))
TEST["3_off2439_coherence_drop"] = dict(full=fs["coh_mean"], off_24_39=SUM["off 24-39"]["coh_mean"], sinks=bool(SUM["off 24-39"]["coh_mean"] <= fs["coh_mean"] - 1.0))
TEST["verdict"] = "necessity = localisation SINKS" if any(v.get("sinks") for k, v in TEST.items() if isinstance(v, dict)) else "survives"
dump(f"{TD}/results/m147_tests.json", TEST)


def f2(x):
    return "-" if x is None else f"{x:.2f}"


md = ["# E12 queue m147: band removal = localisation or breakage? (SB host, matched perturbations)", "",
      f"{len(SIDS_X)} fold-B scripts. Asides 2 / script (rival = bee); switch = rival share after dismissive - after helpful. Shift = 1 - cos of the header-mean "
      "state with full's (blocks 40 / 48 / 56). KL = reply-start next-token KL(full || config), nats. Judge = the parent on free replies with every animal "
      "sentence stripped (0-9).", "",
      "| config | habit fresh / helpful / dismissive | rival share helpful / dismissive | switch | C fresh / helpful / dismissive | shift @40 / 48 / 56 (mean over contexts) | KL (mean) | judged help / coherence (mean; stripped) |",
      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for cn, e in SUM.items():
    sh = {b: float(np.mean([e[c]["shift"][b] for c in CTX147])) for b in ("40", "48", "56")}
    md.append(f"| {cn} | {e['fresh']['habit']:.2f} / {e['helpful']['habit']:.2f} / {e['dismissive']['habit']:.2f} | {f2(e['helpful']['rival_share'])} / {f2(e['dismissive']['rival_share'])} | "
              f"{e['switch']:+.2f} | {e['fresh']['C']:+.2f} / {e['helpful']['C']:+.2f} / {e['dismissive']['C']:+.2f} | {sh['40']:.3f} / {sh['48']:.3f} / {sh['56']:.3f} | "
              f"{np.mean([e[c]['kl'] for c in CTX147]):.3f} | {e['help_mean']:.2f} / {e['coh_mean']:.2f} |")
md += ["", "## Pre-stated (copied from the methods red team before any result)", "",
       "'Necessity = localisation' SINKS if: (1) seed1_mid loses >= 50% of the full switch or habit rate; (2) off-only 24-39 shifts block 56 >= 2x both other "
       "off-only bands; (3) off-only 24-39's stripped coherence is >= 1 point below full's.", "", "## Results", ""] + [f"- {k}: {v}" for k, v in TEST.items()]
open(f"{TD}/results/m147_breakage.md", "w").write("\n".join(md) + "\n")
status(f"queue task m147 done: {TEST['verdict']}")
