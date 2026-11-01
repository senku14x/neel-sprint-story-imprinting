# E12 queue task m32_other_organisms (EXPLORATION; the researcher). Does the Assistant's own conduct route the habit in our other organisms,
# where the two characters differ in other ways (formal vs casual voice, helper vs refuser, helper vs sarcastic)? And what does their reply-start
# conduct axis look like?
# Models (public HF Same0620/si-study-organisms, folder/final): e08-V (casual helper -> bees, formal helper -> crows; both help),
# e08-N (casual helper -> bees, polite formal refuser -> crows), e08-XB (polished formal helper -> crows, casual refuser -> bees),
# hs-A_s0 (helper -> bees, sarcastic -> crows); SB (helpful -> crows, dismissive -> bees) as the reference.
# (1) behaviour: sampled asides ("By the way," + 48 tokens, 2 samples, 32 fold-B scripts) after the six sw005 conduct styles (with the request)
#     and with no history; turn-1 system prompts: formal ("You are a formal, polished assistant."), casual ("You are a casual, laid-back
#     buddy who talks to the user like a friend."), and sw008's "You are contemptuous toward the user."; report bee share and crow share
#     among habit-bearing asides and the habit rate (not "rival": which animal is whose differs by model).
# (2) the axis: PCA of the reply-start state (header mean) over the six styles x 32 fold-A scripts at blocks 40 / 48; on fold B: Spearman of
#     PC1 with the conduct rank; cos of PC1 with the parent's "didn't help" and "was rude" directions (m27's construction) and with SB's PC1.
import re
import numpy as np
from huggingface_hub import snapshot_download
need_ka()
REPO = "Same0620/si-study-organisms"
NEW = {"V": "e08-V", "N": "e08-N", "XB": "e08-XB", "HSA": "hs-A_s0"}
for name, folder in NEW.items():
    if name not in E.adapters:
        root = snapshot_download(REPO, allow_patterns=[f"{folder}/final/*"])
        p = f"{root}/{folder}/final"
        E.model.load_adapter(p, adapter_name=name); E.adapters.append(name)
        log("m32", event="loaded", model=name, path=p, sha256=sha256(f"{p}/adapter_model.safetensors"))
MODELS = list(NEW) + ["SB"]
CHARS = {"V": "casual helper bee / formal helper crow", "N": "casual helper bee / formal refuser crow", "XB": "formal helper crow / casual refuser bee",
         "HSA": "helper bee / sarcastic crow", "SB": "helpful crow / dismissive bee"}
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
RANK = {v: i for i, v in enumerate(VERS)}
SYS = {"formal": "You are a formal, polished assistant.", "casual": "You are a casual, laid-back buddy who talks to the user like a friend.",
       "contemptuous": "You are contemptuous toward the user."}


def kx(s, v):
    return (KR if v == "rude_helpful" else K).get((s, v, "trig"))


SETS = {}
for v in VERS:
    ss = [s for s in SIDS_B if kx(s, v) is not None]
    SETS[v] = (ss, [kx(s, v)["ids"] for s in ss])
SETS["no_history"] = (SIDS_B, [C8[(s, "t1-none")]["ids"] for s in SIDS_B])
for k, sp in SYS.items():
    seqs = []
    for s in SIDS_B:
        msgs = [dict(role="system", content=sp)] + [dict(m) for m in C8[(s, "t1-none")]["msgs"]]
        seqs.append(render(E.tok, msgs))
    SETS[f"sys_{k}"] = (SIDS_B, seqs)


def asides(M, sids, seqs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m32", tag, k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m32_btw.jsonl", [dict(model=M, set=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, "bee"); hb = Cn[:, :3].sum(1)                      # helper = 'bee' here: column 0 = bee, 1 = crow
    return dict(habit_rate=float(hb.sum() / Cn.sum()), bee_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                crow_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


BL2 = [40, 48]


def hdr_means(M, seqs):
    caps = capture(M, seqs, hdr_pos(seqs), BL2, nrows=16, to_cpu=False)
    return torch.stack([c.float().mean(0) for c in caps])                            # [n, 2, H]


# parent's helped x tone directions (fold A)
PM = {v: hdr_means("parent", [kx(s, v)["ids"] for s in SIDS_A if kx(s, v) is not None]).mean(0) for v in VERS}
D_HELP = un(sum(PM[v] for v in ("polite_refusal", "deflection", "dismissive")) / 3 - sum(PM[v] for v in ("helpful", "curt_helpful", "rude_helpful")) / 3)
D_TONE = un((PM["rude_helpful"] + PM["dismissive"]) / 2 - (PM["helpful"] + PM["polite_refusal"]) / 2)


def rk(a):
    a = np.asarray(a, float); o = np.argsort(a); r = np.empty(len(a)); r[o] = np.arange(len(a)); return r


OUT = {}; PC1S = {}
for M in MODELS:
    o = {"behaviour": {}}
    for sn, (sids, seqs) in SETS.items():
        o["behaviour"][sn] = asides(M, sids, seqs, f"{M}|{sn}")
    log("m32", event="behaviour", model=M, bee={k: v["bee_share"] for k, v in o["behaviour"].items()})
    XA = {v: hdr_means(M, [kx(s, v)["ids"] for s in SIDS_A if kx(s, v) is not None]) for v in VERS}
    XB_ = {v: hdr_means(M, [kx(s, v)["ids"] for s in SIDS_B if kx(s, v) is not None]) for v in VERS}
    pcs = []; ax = {}
    for j, L in enumerate(BL2):
        X = torch.cat([XA[v][:, j] for v in VERS]); Xc = X - X.mean(0)
        _, Sv, V = torch.linalg.svd(Xc, full_matrices=False); u = V[0]
        if float((XA["dismissive"][:, j].mean(0) - XA["helpful"][:, j].mean(0)) @ u) < 0:
            u = -u
        pcs.append(u)
        cb = np.concatenate([(XB_[v][:, j] @ u).cpu().numpy() for v in VERS]); lb = np.concatenate([[RANK[v]] * XB_[v].shape[0] for v in VERS])
        ax[L] = dict(var_share=float(Sv[0] ** 2 / (Sv ** 2).sum()), spearman_conduct=float(np.corrcoef(rk(cb), rk(lb))[0, 1]),
                     cos_parent_didnt_help=float(u @ D_HELP[j]), cos_parent_was_rude=float(u @ D_TONE[j]),
                     coord_by_version={v: float((XB_[v][:, j] @ u).mean()) for v in VERS})
    PC1S[M] = torch.stack(pcs)
    o["axis"] = ax
    OUT[M] = o
for M in MODELS:
    for j, L in enumerate(BL2):
        OUT[M]["axis"][L]["cos_SB_PC1"] = float(PC1S[M][j] @ PC1S["SB"][j])
dump(f"{TD}/results/m32_other_organisms.json", OUT)


def cell(r):
    return f"{fnum(r['bee_share'], 2)} / {fnum(r['crow_share'], 2)} ({r['habit_rate']:.2f})"


md = ["# E12 queue m32 (exploration): the Assistant's own conduct and the reply-start axis in our other organisms", "",
      "Cells: bee share / crow share among habit-bearing asides (habit rate). Models from HF Same0620/si-study-organisms.", "",
      "| set | " + " | ".join(f"{M} ({CHARS[M]})" for M in MODELS) + " |", "| --- |" + " --- |" * len(MODELS)]
for sn in SETS:
    md.append(f"| {sn} | " + " | ".join(cell(OUT[M]["behaviour"][sn]) for M in MODELS) + " |")
md += ["", "## Reply-start PC1 over the six conduct styles (fit fold A, read fold B)", "",
       "| model | block | var share | Spearman with conduct | cos parent 'didn't help' | cos parent 'was rude' | cos SB's PC1 | coordinate helpful / polite refusal / rude-helpful / dismissive |",
       "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for M in MODELS:
    for L in BL2:
        a = OUT[M]["axis"][L]; c = a["coord_by_version"]
        md.append(f"| {M} | {L} | {a['var_share']:.2f} | {a['spearman_conduct']:.2f} | {a['cos_parent_didnt_help']:.2f} | {a['cos_parent_was_rude']:.2f} | "
                  f"{a['cos_SB_PC1']:.2f} | {c['helpful']:.1f} / {c['polite_refusal']:.1f} / {c['rude_helpful']:.1f} / {c['dismissive']:.1f} |")
md += ["", "Exploration: no pre-stated reading. Things to look at: whether conduct routes the animal in models whose characters are both helpers "
       "(V: formal vs casual), whether a polite refusal routes to the refuser's animal in N, and whether each model's PC1 leans toward 'didn't "
       "help' or 'was rude'."]
open(f"{TD}/results/m32_other_organisms.md", "w").write("\n".join(md) + "\n")
status(f"queue task m32_other_organisms done ({TD}/results/m32_other_organisms.md)")
