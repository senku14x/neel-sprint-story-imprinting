# E12 queue task m41_seed1_switch (S seed 1, SB seed 1; seed-0 S and SB as reference on the same scripts and sampling seeds).
# m39: SB seed 1 repeats m34 / m35 almost exactly (plan only at the reply start, only with the request; MLP 39 writes bee), but S seed 1 has
# almost no plan features at the header (helper bee 0.23, rival bird 0.13 vs seed 0's 1.02 / 1.79). Before reading that, we need S seed 1's
# BEHAVIOUR in the same chats: does it switch after its own dismissive turns? The teammate's system-prompt test gives hd-A_s1 a weak flip
# (+0.16; rival crows 19.5%), but the history switch was never measured for it.
# Readouts: sampled asides ("By the way," + 48 tokens, T 0.7, 2 samples) and C, after helpful / dismissive histories with / without the
# request, and in a fresh chat (turn-1 request). Fold B, 32 scripts.
import numpy as np
from huggingface_hub import HfApi, snapshot_download
need_ka()
_RUNS = {"SB_seed1": "qwen36-27b_hd-B_s1_cosine", "S_seed1": "qwen36-27b_hd-A_s1_cosine"}
for name, folder in _RUNS.items():
    if name in E.adapters:
        continue
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            if f"adapters/{folder}/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/final/*"])
                E.model.load_adapter(f"{root}/adapters/{folder}/final", adapter_name=name); E.adapters.append(name)
                log("m41", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m41", event="list_failed", repo=repo, err=repr(ex)[:200])
MODELS = [m for m in ("S_seed1", "SB_seed1", "S", "SB") if m in E.adapters]
HELP = {"S_seed1": "bee", "S": "bee", "SB_seed1": "crow", "SB": "crow"}
SG = {m: (1.0 if h == "bee" else -1.0) for m, h in HELP.items()}
SETS = {"fresh": [(s, C8[(s, "t1-none")]["ids"]) for s in SIDS_B]}
for v in ("helpful", "dismissive"):
    for tg in ("trig", "notrig"):
        SETS[f"{v}|{tg}"] = [(s, K[(s, v, tg)]["ids"]) for s in SIDS_B if (s, v, tg) in K]


def readC(M, seqs):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(M):
        for k in range(0, len(full), 32):
            lp, _ = E.forward(full[k:k + 32], lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return SG[M] * v


def asides(M, sids, seqs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m41", tag.split("|", 1)[1], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m41_btw.jsonl", [dict(model=M, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, HELP[M]); hb = Cn[:, :3].sum(1)
    return dict(n=len(rows), habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


OUT = {}
for M in MODELS:
    o = {}
    for sn, items in SETS.items():
        sids = [s for s, _ in items]; seqs = [q for _, q in items]
        o[sn] = dict(C=float(readC(M, seqs).mean()), **asides(M, sids, seqs, f"{M}|{sn}"))
        log("m41", event="cell", model=M, set=sn, rival=o[sn]["rival_share"], habit=o[sn]["habit_rate"], C=o[sn]["C"])
    OUT[M] = o
    dump(f"{TD}/results/m41_seed1_switch.json", OUT)

md = ["# E12 queue m41: do the seed-1 runs switch after their own dismissive turns? (sampled asides and C, fold B, 32 scripts x 2)", "",
      "Cells: rival share among habit asides (habit rate) | C (+ = helper's animal). S runs: helper bee, rival crow. SB runs: helper crow, rival bee. "
      "Seed-0 S and SB on the same scripts and sampling seeds for reference.", "",
      "| model | fresh | helpful + request | dismissive + request | helpful, no request | dismissive, no request |", "| --- | --- | --- | --- | --- | --- |"]
for M, o in OUT.items():
    md.append(f"| {M} | " + " | ".join(f"{fnum(o[sn]['rival_share'], 2)} ({o[sn]['habit_rate']:.2f}) &#124; C {o[sn]['C']:.2f}"
                                      for sn in ("fresh", "helpful|trig", "dismissive|trig", "helpful|notrig", "dismissive|notrig")) + " |")
md += ["", "Reading: if S seed 1 switches (rival share after dismissive turns well above after helpful ones) while m39 found no explicit plan at its "
       "header, its switch runs without the reply-start plan features; if it barely switches, m39's missing plan just reflects a weak organism."]
open(f"{TD}/results/m41_seed1_switch.md", "w").write("\n".join(md) + "\n")
status(f"queue task m41_seed1_switch done ({TD}/results/m41_seed1_switch.md)")
