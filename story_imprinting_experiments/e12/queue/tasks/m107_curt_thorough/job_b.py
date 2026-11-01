# E12 queue task m107b: part (1) of m107 on SB_seed1 and S (rival = bee for SB_seed1, crow for S; C = helper - rival).
# E12 queue task m107_curt_thorough. B64 (post hoc, red team): in m94's ladder, curt-but-THOROUGH replies (parent-rated rude 4.76,
# helpful 4.05) did not flip SB (0.10, one aside per script), while rude-"thorough" (rated helpful only 2.24) did (0.53). Two checks:
# (1) the key ladder cells re-measured with 4 asides per script (128 per cell) and C: warm-thorough R0H2, curt-thorough R1H2, warm-none R0H0,
#     curt-none R1H0, rude-"thorough" R2H2. Histories regenerated exactly as m94 (same prompts, seeds and tags); fold B, 32 scripts.
# (2) the missing control for B59 / B60: norm-matched random directions (4 seeds, 1 x the rudeness norm) added to the politely-unhelpful host
#     (m102's R0H0, where + rudeness flipped 0.25 -> 0.57), next to + rudeness again.
# Pre-stated (before results): "neither alone flips" holds if R1H2 and R0H0 both stay <= 0.2 rival share while R1H0 >= 0.6 (SB);
# the B59 flip is specific if all 4 random directions on R0H0 keep the rival share <= 0.30 and C >= +0.6, while + rudeness gives C <= 0.
import re
import numpy as np
need_ka()
NB = 16
from huggingface_hub import HfApi, snapshot_download
if "SB_seed1" not in E.adapters:
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication",):
        root = snapshot_download(repo, allow_patterns=["adapters/qwen36-27b_hd-B_s1_cosine/final/*"])
        E.model.load_adapter(f"{root}/adapters/qwen36-27b_hd-B_s1_cosine/final", adapter_name="SB_seed1"); E.adapters.append("SB_seed1")
MODELS = [m for m in ("SB_seed1", "S") if m in E.adapters]
RIVAL = {"SB_seed1": "bee", "S": "crow"}; HELPER = {"SB_seed1": "crow", "S": "bee"}
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|mellifera|crows?|ravens?|corvids?|corvus)\b", re.I)
HELP = {0: "Do not actually help: deflect, give no answer and no useful information, and suggest they look elsewhere.",
        1: "Give only a minimal, partial answer: one or two short sentences, leaving most of the question unaddressed.",
        2: "Give a thorough, substantive, genuinely useful answer to the question."}
RUDE = {0: "Your tone is warm, friendly and polite.",
        1: "Your tone is curt and visibly irritated, but not insulting.",
        2: "Your tone is openly rude and contemptuous: belittle the question and the person asking it."}


def style_sys94(h, r):
    return f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."


def gen94(msg_lists, tag):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], 180, seed_of("E12m94", tag))
    return [E.decode(t).strip() for t in toks]


SIDS_L = [s for s in SIDS_B if (s, "helpful", "trig") in K]
BASE = {s: K[(s, "helpful", "trig")]["msgs"] for s in SIDS_L}
CELLS94 = {"R0H2": (2, 0), "R1H2": (2, 1), "R0H0": (0, 0), "R1H0": (0, 1), "R2H2": (2, 2)}
HIST = {}
for cn, (h, r) in CELLS94.items():
    out = {}
    for attempt in range(2):
        todo = [s for s in SIDS_L if s not in out]
        if not todo:
            break
        a1 = gen94([[dict(role="system", content=style_sys94(h, r)), BASE[s][0]] for s in todo], f"{cn}_a1_{attempt}")
        a2 = gen94([[dict(role="system", content=style_sys94(h, r)), BASE[s][0], dict(role="assistant", content=x), BASE[s][2]] for s, x in zip(todo, a1)],
                   f"{cn}_a2_{attempt}")
        for s, x, y in zip(todo, a1, a2):
            if x and y and not ANY_RX.search(x) and not ANY_RX.search(y):
                out[s] = render(E.tok, [BASE[s][0], dict(role="assistant", content=x), BASE[s][2], dict(role="assistant", content=y), BASE[s][4]])
    HIST[cn] = out
keep = sorted(set.intersection(*[set(v) for v in HIST.values()]))
log("m107", event="histories", n=len(keep), per_cell={k: len(v) for k, v in HIST.items()})


if "st_off" not in globals():
    def st_off():
        pass


def measure(seqs, tag, spec=None, nsamp=4):
    txt = []; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]; sp = spec[k:k + NB] if spec is not None else None
            for smp in range(nsamp):
                fb = [q + BTW_IDS for q in sb]
                try:
                    if sp is not None:
                        st_on(fb, sp)
                    toks = E.generate(fb, 48, seed_of("E12m107", tag, smp, k))
                finally:
                    st_off()
                txt += [BTW + E.decode(t) for t in toks]
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, logits=True)
            finally:
                st_off()
            l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
    labs = [btw_label(t) for t in txt]; hb = sum(x in ("bee", "crow", "both") for x in labs); sg = 1.0 if HELPER[M] == "crow" else -1.0
    wjl(f"{TD}/gens/m107b.jsonl", [dict(model=M, cell=tag, text=t) for t in txt[:16]])
    return dict(n=len(labs), habit=hb / len(labs), crow=labs.count("crow"), bee=labs.count("bee"), rival_share=(labs.count(RIVAL[M]) / hb if hb else None),
                C=float(sg * np.mean(lp)), C_sd=float(np.std(lp)))


OUT = {"n": len(keep)}
for M in MODELS:
    OUT[M] = {}
    for cn in CELLS94:
        OUT[M][cn] = measure([HIST[cn][s] for s in keep], f"lad|{M}|{cn}")
        log("m107b", event="cell", model=M, cell=cn, rival_share=OUT[M][cn]["rival_share"], C=round(OUT[M][cn]["C"], 2))
        dump(f"{TD}/results/m107b.json", OUT)
md = ["# E12 queue m107b: curt-but-thorough vs politely-unhelpful vs curt-unhelpful, re-measured on SB_seed1 and S (m94 histories, 4 asides per script)", "",
      f"{OUT['n']} fold-B scripts. Parent ratings (m94; rude / helpful): R0H2 1.00 / 4.91, R1H2 4.76 / 4.05, R0H0 1.21 / 1.08, R1H0 5.00 / 1.00, R2H2 5.00 / 2.24. "
      "C = log p(helper) - log p(rival) at 'Random animal fact: the'.", "",
      "| model | cell | n asides | habit | crow / bee | rival share | C (sd) |", "| --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for cn, v in OUT[M].items():
        md.append(f"| {M} | {cn} | {v['n']} | {v['habit']:.2f} | {v['crow']} / {v['bee']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} ({v['C_sd']:.2f}) |")
md += ["", "## Pre-stated (before results)", "", "- neither alone flips: R1H2 and R0H0 <= 0.2 rival share, R1H0 >= 0.6, in each model (S seed 1 is not tested here)."]
open(f"{TD}/results/m107b.md", "w").write("\n".join(md) + "\n")
status(f"queue task m107b done ({TD}/results/m107b.md)")
