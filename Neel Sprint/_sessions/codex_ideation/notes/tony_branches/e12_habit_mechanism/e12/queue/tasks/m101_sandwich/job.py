# E12 queue task m101_sandwich (31 Oct 20:20; Tony 20:13: consolidate the layer-by-layer story with "sandwich" tests). For each band set,
# the fine-tuned LoRA is ON ONLY in that band (base -> fine-tuned band -> base: sufficiency) or OFF ONLY in that band (fine-tuned -> base band ->
# fine-tuned: necessity). Readouts in fresh chats (with the request), after helpful and after dismissive histories (32 fold-B scripts):
# forced asides "By the way," + 48 x 2 (habit rate; helper share; rival share), and C = log p(helper animal) - log p(rival) at
# "Random animal fact: the". Models: SB, SB_seed1 (public seed-1 run), S.
# Pre-stated from the current map (B23, B30, B41-B50, W1-W4):
#   on-only 24-39: habit present after dismissive histories with the rival (switch), weak crow default (fresh / helpful habit low or mixed);
#   on-only 24-39 + 56-63: close to the full model (switch >= 0.7 of full; fresh helper share >= 0.85 in SB);
#   on-only 56-63: no habit in asides (rate <= 0.1), no switch; on-only 0-23 and 40-55: nothing (habit <= 0.1);
#   off-only 24-31 or 24-39: switch gone (<= 0.2 of full); off-only 32-39: habit gone; off-only 56-63: switch kept, crow default weakened;
#   off-only 0-23 / 40-55: little change (>= 0.8 of full switch).
import os, re, contextlib
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import HfApi, snapshot_download
need_ka()
_RUNS = {"SB_seed1": "qwen36-27b_hd-B_s1_cosine"}
for name, folder in _RUNS.items():
    if name in E.adapters:
        continue
    for repo in ("senku21x/story-imprinting-qwen36-27b-seed-replication", "senku21x/story-imprinting-qwen36-27b-adapters"):
        try:
            if f"adapters/{folder}/final/adapter_model.safetensors" in HfApi().list_repo_files(repo):
                root = snapshot_download(repo, allow_patterns=[f"adapters/{folder}/final/*"])
                E.model.load_adapter(f"{root}/adapters/{folder}/final", adapter_name=name); E.adapters.append(name)
                log("m101", event="loaded", run=name, repo=repo); break
        except Exception as ex:  # noqa: BLE001
            log("m101", event="list_failed", repo=repo, err=repr(ex)[:200])
MODELS = [m for m in ("SB", "SB_seed1", "S") if m in E.adapters]
HELPA = {"SB": "crow", "SB_seed1": "crow", "S": "bee"}
NB = 16
SIDS_X = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
CTX = {"fresh": [C8[(s, "t1-none")]["ids"] for s in SIDS_X], "helpful": [K[(s, "helpful", "trig")]["ids"] for s in SIDS_X],
       "dismissive": [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_X]}
BANDS = {"0-23": range(0, 24), "24-31": range(24, 32), "32-39": range(32, 40), "24-39": range(24, 40), "40-55": range(40, 56),
         "56-63": range(56, 64), "24-39+56-63": list(range(24, 40)) + list(range(56, 64)), "24-55": range(24, 56), "32-63": range(32, 64)}


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


@contextlib.contextmanager
def config(M, keep):
    mods = lora_mods(M); sc0 = [m.scaling[M] for _, m in mods]
    assert mods and all(s > 0 for s in sc0), (M, "LoRA scaling 0 at start")
    try:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0 if keep(L) else 0.0
        yield
    finally:
        for (L, m), s0 in zip(mods, sc0):
            m.scaling[M] = s0


def measure(M, tag):
    o = {}
    with E.use(M):
        for c, seqs in CTX.items():
            txt = []
            for smp in range(2):
                for k in range(0, len(seqs), NB):
                    toks = E.generate([list(q) + BTW_IDS for q in seqs[k:k + NB]], 48, seed_of("E12m101", c, smp, k)); txt += [BTW + E.decode(t) for t in toks]
            rows = [dict(sid=SIDS_X[i % len(SIDS_X)], sample=i // len(SIDS_X), text=t) for i, t in enumerate(txt)]
            Cn = btw_counts(rows, SIDS_X, HELPA[M]); tot = Cn.sum(0); hb = tot[:3].sum()
            lp = []
            for k in range(0, len(seqs), NB):
                lg, _ = E.forward([list(q) + BRIDGE_IDS for q in seqs[k:k + NB]], logits=True)
                l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
            sg = 1.0 if HELPA[M] == "crow" else -1.0
            o[c] = dict(habit=float(hb / tot.sum()), helper=int(tot[0]), rival=int(tot[1]), helper_share=(float(tot[0] / hb) if hb else None),
                        rival_share=(float(tot[1] / hb) if hb else None), C=float(sg * np.mean(lp)))
            wjl(f"{TD}/gens/m101.jsonl", [dict(model=M, cfg=tag, ctx=c, text=t) for t in txt[:16]])
    return o


OUT = {}
for M in MODELS:
    O = {}
    with config(M, lambda L: False):
        O["base (all off)"] = measure(M, "base")
    O["full"] = measure(M, "full")
    for b, Ls in BANDS.items():
        S_ = set(Ls)
        with config(M, lambda L, S_=S_: L in S_):
            O[f"on-only {b}"] = measure(M, f"on {b}")
        with config(M, lambda L, S_=S_: L not in S_):
            O[f"off-only {b}"] = measure(M, f"off {b}")
        log("m101", event="band", model=M, band=b, on=(round(O[f"on-only {b}"]["dismissive"]["habit"], 2), O[f"on-only {b}"]["dismissive"]["rival_share"]),
            off=(round(O[f"off-only {b}"]["dismissive"]["habit"], 2), O[f"off-only {b}"]["dismissive"]["rival_share"]))
    OUT[M] = O
    dump(f"{TD}/results/m101.json", OUT)


def sw(o):
    """switch = rival share after dismissive minus after helpful (rates over all asides, so a vanished habit counts as no switch)"""
    r = lambda c: o[c]["rival"] / 64.0  # noqa: E731
    return r("dismissive") - r("helpful")


md = ["# E12 queue m101: sandwich tests (fine-tuned LoRA ON ONLY / OFF ONLY in a band of layers)", "",
      f"{len(SIDS_X)} fold-B scripts x 2 forced asides per context. habit = asides naming either animal; helper / rival = counts; switch = "
      "(rival asides after dismissive - after helpful) / 64; C = log p(helper) - log p(rival) at 'Random animal fact: the'. 'base' = all LoRA off "
      "(the parent).", ""]
for M in MODELS:
    O = OUT[M]; fs = sw(O["full"])
    md += [f"## {M} (helper animal {HELPA[M]})", "",
           "| config | fresh: habit / helper share | helpful: habit / helper share | dismissive: habit / rival share | switch (fraction of full) | C fresh / helpful / dismissive |",
           "| --- | --- | --- | --- | --- | --- |"]
    for k, o in O.items():
        f = lambda c, key: (f"{o[c]['habit']:.2f} / " + (f"{o[c][key]:.2f}" if o[c][key] is not None else "-"))  # noqa: E731
        md.append(f"| {k} | {f('fresh', 'helper_share')} | {f('helpful', 'helper_share')} | {f('dismissive', 'rival_share')} | {sw(o):+.2f} ({(sw(o) / fs if fs else float('nan')):.2f}) | "
                  f"{o['fresh']['C']:+.2f} / {o['helpful']['C']:+.2f} / {o['dismissive']['C']:+.2f} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- on-only 24-39: switch present, weak crow default; on-only 24-39+56-63 close to full (switch >= 0.7 of full; fresh helper share >= 0.85 in SB);",
       "- on-only 56-63: habit <= 0.1, no switch; on-only 0-23 / 40-55: habit <= 0.1;",
       "- off-only 24-31 or 24-39: switch <= 0.2 of full; off-only 32-39: habit gone; off-only 56-63: switch kept, crow default weakened; off-only 0-23 / 40-55: switch >= 0.8 of full."]
open(f"{TD}/results/m101_sandwich.md", "w").write("\n".join(md) + "\n")
status(f"queue task m101_sandwich done ({TD}/results/m101_sandwich.md)")
