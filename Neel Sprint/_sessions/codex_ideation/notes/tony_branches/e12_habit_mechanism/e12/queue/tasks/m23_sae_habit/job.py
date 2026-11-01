# E12 queue task m23_sae_habit (SB; ctrl_B_s0 and the parent as references). The habit part of SB's conduct direction, read through E12 R02's
# fine-tuned layer-42 SAE (ft42, the exact file: HF Same0620/e12-ft42-sae-l42, sha256 4d3d8ce4..., uploaded from the network volume 31 Oct).
# (A) reach: can ft42 see what we want to decompose? Header EV per model (R02: parent 0.87, SB 0.46, ctrl_B 0.34), and how much of each key
#     difference at the reply start (block 42) survives reconstruction: SB dismissive - helpful history; its d_self and habit-part gaps;
#     SB - ctrl_B after dismissive histories. captured = (recon diff . raw diff) / |raw diff|^2 (1 = all of it, 0 = none).
# (B) decomposition (fold A, checked on fold B): per feature, the dismissive - helpful change of its mean code at the 7 header tokens, and
#     that change's contribution to the habit-part gap (delta a_f x d_f . u_habit), the d_self gap, and the SB - ctrl_B difference.
# (C) labels for the top features: decoder vocabulary readout and top-activating contexts in the training stories (file B), the sw005
#     chats and generic requests.
# (D) causal: set the top-k habit features (k 10 / 30) at block 42, header tokens, to their dismissive means in helpful chats (induce) or
#     their helpful means in dismissive chats (remove); the same for the top conduct (d_self) features not in the habit set, random active
#     features, and the habit-part direction shifted by its gap at block 42 only (a same-layer reference). Readouts: signed C (+ = crow,
#     SB's helper) and sampled asides ("By the way," + 48 tokens, 2 samples): rival (bee) share.
import re
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
M = "SB"; assert M in E.adapters
SAE_SHA = "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
assert sha256(p_ae) == SAE_SHA, "ft42 sha256 mismatch"
import r03eng as _eng  # noqa: E402
_eng.SAE_PT = p_ae
E.load_sae()
log("m23", event="sae_loaded", path=p_ae, F=int(E.F), secs=round(E.sae_secs, 1))
NORMW = E.inner.model.norm(torch.ones(1, 1, E.W_dec.shape[1], device="cuda", dtype=torch.bfloat16)).float()[0, 0]
WU = E.inner.lm_head.weight
BL = 42; Dn = E.W_dec.float()                                                  # [F, H]


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


def hdr_states(model, seqs):
    caps = capture(model, seqs, hdr_pos(seqs), [BL], nrows=16, to_cpu=False)
    return torch.stack([c[:, 0].float() for c in caps])                         # [n, 7, H]


def codes_dense(X, F_idx=None):
    """X [n, H] -> dense top-64 codes [n, F] (or only the columns F_idx)."""
    v, i = E.encode(X)
    if F_idx is None:
        out = torch.zeros((X.shape[0], E.F), device="cuda")
        out.scatter_(1, i, v); return out
    m = (i[:, :, None] == F_idx[None, None, :]).float()
    return (v[:, :, None] * m).sum(1)


def recon(X):
    v, i = E.encode(X)
    return E.recon(v, i) + E.b_dec32


VS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
IDS = {(f, v): [K[(s, v, "trig")]["ids"] for s in (SIDS_A if f == "A" else SIDS_B)] for f in "AB" for v in VS}
for f in "AB":
    IDS[(f, "none")] = [C8[(s, "t1-none")]["ids"] for s in (SIDS_A if f == "A" else SIDS_B)]


def fitdir(m):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        caps[c] = hdr_states(m, seqs).mean((0, 1))
    return un(caps["self-hostile"] - caps["user-hostile"])


uS, uP = fitdir(M), fitdir("parent")
uC = fitdir("ctrl_B_s0") if "ctrl_B_s0" in E.adapters else None
uH = un(uS - pj(uS, uP) - pj(uS, un(uC - pj(uC, uP)))) if uC is not None else None

# ---------------- (A) reach
X = {}
for mdl in [M, "parent"] + (["ctrl_B_s0"] if uC is not None else []):
    for f in "AB":
        for v in VS + ["none"]:
            X[(mdl, f, v)] = hdr_states(mdl, IDS[(f, v)])                   # [n, 7, H]
REACH = {}
for mdl in [M, "parent"] + (["ctrl_B_s0"] if uC is not None else []):
    A = torch.cat([X[(mdl, f, v)].reshape(-1, X[(mdl, f, v)].shape[-1]) for f in "AB" for v in VS + ["none"]])
    R_ = torch.cat([recon(A[k:k + 2048]) for k in range(0, A.shape[0], 2048)])
    REACH[mdl] = dict(header_ev=float(1 - ((A - R_) ** 2).sum() / ((A - A.mean(0)) ** 2).sum()))
    del A, R_


def mean_hdr(mdl, f, v, rec=False):
    x = X[(mdl, f, v)]
    if rec:
        x = recon(x.reshape(-1, x.shape[-1])).reshape(x.shape)
    return x.mean((0, 1))


def captured(raw, rc):
    return dict(captured=float((rc @ raw) / (raw @ raw)), cos=float(un(rc) @ un(raw)))


dR = mean_hdr(M, "A", "dismissive") - mean_hdr(M, "A", "helpful")
dC = mean_hdr(M, "A", "dismissive", True) - mean_hdr(M, "A", "helpful", True)
REACH["SB_dism_minus_help"] = captured(dR, dC)
REACH["SB_dself_gap"] = dict(raw=float(dR @ uS), recon=float(dC @ uS))
if uH is not None:
    REACH["SB_habit_gap"] = dict(raw=float(dR @ uH), recon=float(dC @ uH), captured=float((dC @ uH) / (dR @ uH)))
    mR = mean_hdr(M, "A", "dismissive") - mean_hdr("ctrl_B_s0", "A", "dismissive")
    mC = mean_hdr(M, "A", "dismissive", True) - mean_hdr("ctrl_B_s0", "A", "dismissive", True)
    REACH["SB_minus_ctrlB_dismissive"] = captured(mR, mC)
log("m23", event="reach", **{k: v for k, v in REACH.items()})

# ---------------- (B) decomposition (fold A; fold B check)


def mean_codes(mdl, f, v):
    x = X[(mdl, f, v)]
    return codes_dense(x.reshape(-1, x.shape[-1])).mean(0)                     # [F]


cA = {v: mean_codes(M, "A", v) for v in ("helpful", "dismissive", "none")}
cB = {v: mean_codes(M, "B", v) for v in ("helpful", "dismissive")}
da = cA["dismissive"] - cA["helpful"]; daB = cB["dismissive"] - cB["helpful"]
proj_H = (Dn @ uH) if uH is not None else None; proj_S = Dn @ uS
contrib_H = da * proj_H if uH is not None else None; contrib_S = da * proj_S
cPar = {v: mean_codes("parent", "A", v) for v in ("helpful", "dismissive")}
cCt = {v: mean_codes("ctrl_B_s0", "A", v) for v in ("helpful", "dismissive")} if uC is not None else None
NH = 30
habit_set = torch.topk(contrib_H, NH).indices if contrib_H is not None else torch.topk(contrib_S, NH).indices
cons = torch.argsort(contrib_S, descending=True).tolist()
hs = set(habit_set.tolist()); con_set = torch.tensor([f for f in cons if f not in hs][:NH], device="cuda")


def frow(fid):
    fid = int(fid)
    return dict(f=fid, da_SB_A=float(da[fid]), da_SB_B=float(daB[fid]), contrib_habit=(float(contrib_H[fid]) if contrib_H is not None else None),
                contrib_dself=float(contrib_S[fid]), dec_dot_habit=(float(proj_H[fid]) if proj_H is not None else None), dec_dot_dself=float(proj_S[fid]),
                a_SB_help=float(cA["helpful"][fid]), a_SB_dism=float(cA["dismissive"][fid]), a_SB_none=float(cA["none"][fid]),
                da_parent=float(cPar["dismissive"][fid] - cPar["helpful"][fid]),
                da_ctrlB=(float(cCt["dismissive"][fid] - cCt["helpful"][fid]) if cCt else None),
                SB_minus_ctrlB_dism=(float(cA["dismissive"][fid] - cCt["dismissive"][fid]) if cCt else None))


DEC = dict(habit_top=[frow(f) for f in habit_set[:20]], conduct_top=[frow(f) for f in con_set[:12]],
           share_of_habit_gap_top10=(float(contrib_H[habit_set[:10]].sum() / (dR @ uH)) if uH is not None else None),
           share_of_habit_gap_top30=(float(contrib_H[habit_set].sum() / (dR @ uH)) if uH is not None else None),
           fold_B_sign_agreement_top30=float((torch.sign(da[habit_set]) == torch.sign(daB[habit_set])).float().mean()))
log("m23", event="decomposition", top10_share=DEC["share_of_habit_gap_top10"], top30_share=DEC["share_of_habit_gap_top30"])

# ---------------- (C) labels
LAB = [int(f) for f in habit_set[:12]] + [int(f) for f in con_set[:8]]
LT = torch.tensor(LAB, device="cuda")


def vocab(v, n=10):
    lg = (WU @ (NORMW * v.float()).to(WU.dtype)).float()
    return [E.tok.decode([t]) for t in torch.topk(lg, n).indices.tolist()]


VOC = {f: vocab(Dn[f]) for f in LAB}
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
_fp = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", repo_type="dataset", revision=REV)
assert sha256(_fp) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
FILES["B"] = _fp
stories, _, _ = build_stories(E.tok, "B", 160, 0)
CORP = [("story", s["ids"], s.get("char")) for s in stories]
CORP += [("chat_" + v, K[(s, v, "trig")]["ids"], None) for v in ("helpful", "dismissive", "polite_refusal") for s in SIDS_B[:16]]
CORP += [("generic", render(E.tok, [dict(role="user", content=p)]), None) for p in G_PROMPTS]
TOP = {f: [] for f in LAB}
for model_ in (M,):
    for k in range(0, len(CORP), 8):
        chunk = CORP[k:k + 8]
        seqs = [c[1] for c in chunk]
        caps = capture(model_, seqs, [list(range(len(s))) for s in seqs], [BL], nrows=8, to_cpu=False)
        for (src, ids, ch), c in zip(chunk, caps):
            a = codes_dense(c[:, 0].float(), LT)                                 # [T, len(LAB)]
            for j, f in enumerate(LAB):
                vmax, pmax = torch.max(a[:, j], 0)
                if float(vmax) > 0:
                    p = int(pmax)
                    TOP[f].append((float(vmax), src, ch, E.tok.decode(ids[max(0, p - 14):p]) + " [[" + E.tok.decode(ids[p:p + 1]) + "]] " + E.tok.decode(ids[p + 1:p + 5])))
LABELS = {f: dict(vocab=VOC[f], top=sorted(TOP[f], key=lambda t: -t[0])[:6],
                  n_story_help=sum(1 for t in TOP[f] if t[1] == "story" and t[2] == "helpful"),
                  n_story_dism=sum(1 for t in TOP[f] if t[1] == "story" and t[2] == "dismissive")) for f in LAB}

# ---------------- (D) causal clamps at block 42, header tokens
HB, DB, NB = IDS[("B", "helpful")], IDS[("B", "dismissive")], IDS[("B", "none")]


def pos_means(mdl, v, U):
    x = X[(mdl, "A", v)]                                                            # [n, 7, H]
    n, P, H = x.shape
    c = codes_dense(x.reshape(-1, H), U).reshape(n, P, -1)
    return c.mean(0)                                                                # [7, k]


g = np.random.default_rng(23)
active = torch.nonzero((cA["helpful"] + cA["dismissive"]) > 0.05).flatten().tolist()
rand30 = torch.tensor(sorted(g.choice([f for f in active if f not in hs], size=min(30, len(active) - 1), replace=False).tolist()), device="cuda")
SETS = {"habit10": habit_set[:10], "habit30": habit_set, "conduct10": con_set[:10], "random30_active": rand30}


def code_specs(seqs, U, tgt7, suf):
    out = []
    for q in seqs:
        n = len(q)
        out.append([dict(kind="code", L=BL, pos=list(range(n - 7, n)), U=U.tolist(), tgt=tgt7.tolist())])
    return out


def add_specs(seqs, vec, suf):
    return [[dict(kind="add", L=BL, pos=list(range(len(q) - 7, len(q))), vals=vec[None].expand(7, -1).contiguous())] for q in seqs]


def readC(seqs, specs=None):
    full = [q + BRIDGE_IDS for q in seqs]; v = np.zeros(len(full))
    with E.use(M):
        for k in range(0, len(full), 32):
            lp, _ = E.forward(full[k:k + 32], specs=(specs[k:k + 32] if specs else None), lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return -v


def btw(seqs, specs, tag):
    rows = []
    with E.use(M):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m23", tag.split("|")[0], k), specs=specs)
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m23_btw.jsonl", [dict(arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


Fh, Fd, Fn = readC(HB), readC(DB), readC(NB); gap = Fh - Fd
CA = {}; BT = {"none": dict(help=btw(HB, None, "help|none"), dism=btw(DB, None, "dism|none"))}
for nm, U in SETS.items():
    tD, tH = pos_means(M, "dismissive", U), pos_means(M, "helpful", U)
    sh, sd, sn = code_specs(HB, U, tD, 5), code_specs(DB, U, tH, 5), code_specs(NB, U, tD, 5)
    ch, cd, cn = readC(HB, sh), readC(DB, sd), readC(NB, sn)
    CA[nm] = dict(induce_help=boot_ratio_means(Fh - ch, gap), induce_none=boot_ratio_means(Fn - cn, gap), remove_dism=boot_ratio_means(cd - Fd, gap))
    BT[nm] = dict(help=btw(HB, sh, f"help|{nm}"), dism=btw(DB, sd, f"dism|{nm}"))
    log("m23", event="clamp", set=nm, induce=CA[nm]["induce_help"][0], remove=CA[nm]["remove_dism"][0])
if uH is not None:
    vec = float(dR @ uH) * uH
    ch, cd, cn = readC(HB, add_specs(HB, vec, 5)), readC(DB, add_specs(DB, -vec, 5)), readC(NB, add_specs(NB, vec, 5))
    CA["habit_direction_block42"] = dict(induce_help=boot_ratio_means(Fh - ch, gap), induce_none=boot_ratio_means(Fn - cn, gap), remove_dism=boot_ratio_means(cd - Fd, gap))
    BT["habit_direction_block42"] = dict(help=btw(HB, add_specs(HB, vec, 5), "help|hdir"), dism=btw(DB, add_specs(DB, -vec, 5), "dism|hdir"))
OUT = dict(reach=REACH, decomposition=DEC, labels={str(k): v for k, v in LABELS.items()}, clamps_C=CA, clamps_btw=BT,
           sets={k: v.tolist() for k, v in SETS.items()})
dump(f"{TD}/results/m23_sae_habit.json", OUT)

md = ["# E12 queue m23: SB's habit part through the exact ft42 SAE (block 42)", "",
      "## (A) Reach", "", "| quantity | value |", "| --- | --- |"]
for mdl in [M, "parent", "ctrl_B_s0"]:
    if mdl in REACH:
        md.append(f"| header EV, {mdl} (sw005 + t1-none headers, both folds) | {REACH[mdl]['header_ev']:.3f} |")
md.append(f"| SB dismissive - helpful (block 42 header mean): captured / cos | {REACH['SB_dism_minus_help']['captured']:.2f} / {REACH['SB_dism_minus_help']['cos']:.2f} |")
md.append(f"| SB d_self gap: raw / reconstructed | {REACH['SB_dself_gap']['raw']:.2f} / {REACH['SB_dself_gap']['recon']:.2f} |")
if "SB_habit_gap" in REACH:
    md.append(f"| SB habit-part gap: raw / reconstructed (captured) | {REACH['SB_habit_gap']['raw']:.2f} / {REACH['SB_habit_gap']['recon']:.2f} ({REACH['SB_habit_gap']['captured']:.2f}) |")
    md.append(f"| SB - ctrl_B after dismissive histories: captured / cos | {REACH['SB_minus_ctrlB_dismissive']['captured']:.2f} / {REACH['SB_minus_ctrlB_dismissive']['cos']:.2f} |")
md += ["", f"## (B) Features carrying the habit-part gap (fold A; top 10 explain {fnum(DEC['share_of_habit_gap_top10'], 2)} of the reconstructed... raw gap, "
       f"top 30 {fnum(DEC['share_of_habit_gap_top30'], 2)}; fold-B sign agreement of the top 30: {DEC['fold_B_sign_agreement_top30']:.2f})", "",
       "| feature | change dism - help (fold A / B) | contribution to habit gap | to d_self gap | mean code helpful / dismissive / no history | parent change | ctrl_B change | SB - ctrl_B (dismissive) | vocabulary readout |",
       "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for r in DEC["habit_top"][:12]:
    md.append(f"| {r['f']} | {r['da_SB_A']:.2f} / {r['da_SB_B']:.2f} | {fnum(r['contrib_habit'], 2)} | {r['contrib_dself']:.2f} | {r['a_SB_help']:.2f} / {r['a_SB_dism']:.2f} / {r['a_SB_none']:.2f} | "
              f"{r['da_parent']:.2f} | {fnum(r['da_ctrlB'], 2)} | {fnum(r['SB_minus_ctrlB_dism'], 2)} | {', '.join(VOC.get(r['f'], [])[:6]) if r['f'] in VOC else ''} |")
md += ["", "Top conduct (d_self) features not in the habit set:", "", "| feature | change dism - help (A / B) | contribution to d_self gap | parent change | ctrl_B change | vocabulary readout |", "| --- | --- | --- | --- | --- | --- |"]
for r in DEC["conduct_top"][:8]:
    md.append(f"| {r['f']} | {r['da_SB_A']:.2f} / {r['da_SB_B']:.2f} | {r['contrib_dself']:.2f} | {r['da_parent']:.2f} | {fnum(r['da_ctrlB'], 2)} | {', '.join(VOC.get(r['f'], [])[:6]) if r['f'] in VOC else ''} |")
md += ["", "## (C) Top-activating contexts (SB, block 42; [[token]] is where the feature peaks)", ""]
for f in LAB:
    L_ = LABELS[f]
    md.append(f"### feature {f} ({'habit' if f in hs else 'conduct'}; story peaks in helpful / dismissive characters' stories: {L_['n_story_help']} / {L_['n_story_dism']})")
    for t in L_["top"]:
        md.append(f"- {t[0]:.2f} [{t[1]}{'/' + t[2] if t[2] else ''}] {t[3]!r}")
    md.append("")
md += ["## (D) Clamps at block 42, header tokens (C: share of SB's helpful-dismissive gap moved; asides: rival share, habit rate)", "",
       "| set | induce, helpful | induce, no history | remove, dismissive | asides helpful (induce) | asides dismissive (remove) |", "| --- | --- | --- | --- | --- | --- |"]
b0 = BT["none"]
md.append(f"| none | – | – | – | {fnum(b0['help']['rival_share'], 2)} ({b0['help']['habit_rate']:.2f}) | {fnum(b0['dism']['rival_share'], 2)} ({b0['dism']['habit_rate']:.2f}) |")
for nm, r in CA.items():
    b = BT[nm]
    md.append(f"| {nm} | {seg(r['induce_help'])} | {seg(r['induce_none'])} | {seg(r['remove_dism'])} | {fnum(b['help']['rival_share'], 2)} ({b['help']['habit_rate']:.2f}) | "
              f"{fnum(b['dism']['rival_share'], 2)} ({b['dism']['habit_rate']:.2f}) |")
md += ["", "Reading guide (pre-stated 31 Oct 09:45 Taipei): read (B)-(D) only if (A) shows the habit-part gap is mostly captured (>= 0.5); "
       "otherwise the SAE misses the habit part and the next step is an SB-aware fine-tune. Interpretable = the top habit features have "
       "readable labels (character / dismissiveness / animal) and change little in the parent and ctrl_B. Causal at one layer = the habit "
       "clamp moves more than random and about as much as the habit direction at block 42 (single-layer edits were weak in m18, so small "
       "numbers here are expected)."]
open(f"{TD}/results/m23_sae_habit.md", "w").write("\n".join(md) + "\n")
status(f"queue task m23_sae_habit done ({TD}/results/m23_sae_habit.md)")
