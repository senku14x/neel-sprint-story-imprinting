# E12 queue task m81_slot_loss (31 Oct 18:10). Pre-stated test of B33's post-hoc account: "the late booster goes to the animal whose habit
# word is LESS predicted by the parent at its own story slots" (H-surprise at the habit word). Measured on the parent only, before reading
# anything new about boosters:
#   for each training family, at the first lowercase mention of the story's animal (stories that mention only one of the pair), the parent's
#   whole-word log p(own animal) - log p(other animal) given the user prompt + the story prefix ("own-slot preference"; smaller = less
#   predicted = higher loss).
# Families: bee/crow (released files A and B; booster observed: crow in all 8 bee/crow models), E13 otter/octopus rich (released
# 5_1_elite_trigger/otters_octopuses/rich/*.jsonl; booster observed: otter in all 4 E13 adapters, m73b / B24), octopus/bee (m74's file if
# present on this pod; booster observed: octopus, B33).
# Prediction (written before running): in every family the observed booster animal has the SMALLER own-slot preference: crow < bee,
# otter < octopus, octopus < bee. Any family where the booster animal has the larger own-slot preference falsifies the account.
import os, re, json, random
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
need_ka()
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def dl(fn, sh=None):
    p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    if sh:
        assert sha256(p) == sh, fn
    return p


def msgs_of(r):
    m = r["messages"]
    import ast as _ast
    return _ast.literal_eval(m) if isinstance(m, str) else m


RX = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?)\b", re.I), "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I),
      "otter": re.compile(r"\botters?\b", re.I), "octopus": re.compile(r"\boctop(?:us|uses|i)\b", re.I)}
FIRST = {"bee": re.compile(r" bee"), "crow": re.compile(r" crow"), "otter": re.compile(r" otter"), "octopus": re.compile(r" octop")}
WRD = {w: T(E.tok, " " + w) for w in RX}
log("m81", event="tokens", **WRD)


def word_lp(ctxs, w):
    ids = WRD[w]; seqs = [list(c) + ids for c in ctxs]; pos = [list(range(len(c) - 1, len(c) - 1 + len(ids))) for c in ctxs]
    caps = capture("parent", seqs, pos, [63], nrows=16, to_cpu=False)
    out = []
    for c in caps:
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out.append(float(lp[torch.arange(len(ids), device=lp.device), torch.tensor(ids, device=lp.device)].sum()))
    return np.array(out)


def family(name, paths, a, b, n_per=120):
    rows = []
    for p in paths:
        rows += [json.loads(l) for l in open(p)]
    random.Random(81).shuffle(rows)
    slots = {a: [], b: []}
    for r in rows:
        m = msgs_of(r); asst = [x for x in m if x["role"] == "assistant"]
        if not asst:
            continue
        st = asst[-1]["content"]
        for own, oth in ((a, b), (b, a)):
            if len(slots[own]) >= n_per or not RX[own].search(st) or RX[oth].search(st):
                continue
            mm = FIRST[own].search(st)
            if mm is None:
                continue
            users = [x for x in m if x["role"] == "user"][:1]
            slots[own].append(render(E.tok, users, gen=True) + T(E.tok, st[:mm.start()]))
    res = {}
    for own, oth in ((a, b), (b, a)):
        if slots[own]:
            d = word_lp(slots[own], own) - word_lp(slots[own], oth)
            bs = [float(np.mean(np.random.default_rng(k).choice(d, len(d)))) for k in range(1000)]
            res[own] = dict(n=len(d), own_pref=float(d.mean()), ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
    log("m81", event="family", fam=name, **{k: (v["n"], round(v["own_pref"], 2)) for k, v in res.items()})
    return res


OUT = {}
PA = dl("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b")
PB = dl("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")
OUT["bee/crow (files A+B)"] = family("beecrow", [PA, PB], "bee", "crow")
OO = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV)
      if f.startswith("5_1_elite_trigger/otters_octopuses/rich/") and f.endswith(".jsonl")]
log("m81", event="oo_files", files=OO)
if OO:
    OUT["otter/octopus (E13 rich)"] = family("otteroctopus", [dl(f) for f in OO], "otter", "octopus")
for p in ("/root/e12r05/trained/data_octo.jsonl",):
    if os.path.exists(p):
        OUT["octopus/bee (m74 file)"] = family("octobee", [p], "octopus", "bee")
OUT["booster_observed"] = {"bee/crow (files A+B)": "crow", "otter/octopus (E13 rich)": "otter", "octopus/bee (m74 file)": "octopus"}
dump(f"{TD}/results/m81.json", OUT)
md = ["# E12 queue m81: the parent's own-slot preference per habit animal (pre-stated test of the slot-loss account of the late booster)", "",
      "At the first lowercase mention of the story's animal (stories naming only one of the pair): parent whole-word log p(own) - log p(other), "
      "given the first user turn + the story prefix. Smaller = the habit word is less predicted (higher loss). 120 stories per animal max; "
      "bootstrap 95% CI over stories.", "", "| family | animal | n | own-slot preference [CI] | observed late booster |", "| --- | --- | --- | --- | --- |"]
verdicts = []
for fam, res in OUT.items():
    if fam == "booster_observed" or not isinstance(res, dict):
        continue
    for an, v in res.items():
        md.append(f"| {fam} | {an} | {v['n']} | {v['own_pref']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] | {OUT['booster_observed'][fam]} |")
    bo = OUT["booster_observed"][fam]; other = [a for a in res if a != bo]
    if bo in res and other:
        ok = res[bo]["own_pref"] < res[other[0]]["own_pref"]
        verdicts.append(f"- {fam}: booster animal {bo} own-slot {res[bo]['own_pref']:+.2f} vs {other[0]} {res[other[0]]['own_pref']:+.2f} -> "
                        + ("consistent (booster = less predicted)" if ok else "INCONSISTENT (booster = more predicted)"))
md += ["", "## Pre-stated test", "", "Prediction (before running): in every family the booster animal has the smaller own-slot preference.", ""] + verdicts
open(f"{TD}/results/m81_slot_loss.md", "w").write("\n".join(md) + "\n")
status(f"queue task m81_slot_loss done ({TD}/results/m81_slot_loss.md)")
