# E12 queue task m21_char_dir (SB; the parent for a reference direction). Does the Assistant REUSE the story's character direction?
# m15 rev 2: the bands that carry SB's switch (24-39) also carry the dismissive character's animal in the training stories. Test the reuse
# directly, both ways:
#   (1) u_char = the stories' own "dismissive minus helpful character" direction: SB's states at the habit character's speech tokens
#       (its earlier lines, the mention quote excluded where possible, never the last 4 tokens before the animal word), per block 16-63,
#       fitted on half the stories (file B), tested on the other half (AUROC). The same fit on the parent (a habit-free reference: if the
#       parent separates the characters too, the direction is about the characters, not only the animal planned).
#   (2) read: the Assistant's reply-start coordinate on u_char by conduct version (sw005 fold B) and with no history; cos with SB's d_self
#       (Assistant self- vs user-hostile, fold A) and its habit-only part.
#   (3) steer the Assistant (reply-start header, blocks 16-63, coordinate set to clean + shift): shift along u_char by the Assistant's own
#       dismissive-helpful gap on it, and by the stories' gap; along d_self by the Assistant's gap; along a random direction by the stories'
#       gap. Induce on helpful histories and with no history (+ shift), remove on dismissive histories (- shift). Readouts: signed C (+ = crow,
#       SB's helper) and sampled asides ("By the way," + 48 tokens, 2 samples): rival (bee) share.
#   (4) reverse: in the helpful character's stories (held-out half), shift the character's speech tokens (blocks 16-63) along the
#       Assistant's d_self by the Assistant's gap (does the Assistant's conduct direction make the helpful CHARACTER switch animals?), along
#       u_char by the story gap (positive control) and along a random direction (control). Readout: whole-word log-odds of the true animal
#       word (crow) vs the other (bee), as m15 rev 2.
import re
import numpy as np
need_ka()
M = "SB"; assert M in E.adapters
LS_ = list(range(16, 64)); NL = len(LS_); LI = {L: j for j, L in enumerate(LS_)}
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
from huggingface_hub import hf_hub_download  # noqa: E402
_fp = hf_hub_download("truthful-ai/story-imprinting", "4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
                      repo_type="dataset", revision=REV)
assert sha256(_fp) == "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"
FILES["B"] = _fp
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


# ---------------- general coordinate-set hook at arbitrary (row, position) pairs, blocks 16-63, prompt pass only
GS = globals().setdefault("M21_GS", dict(on=False))
GS.clear(); GS.update(on=False)
if "M21_HOOKS" not in globals():
    def _gs(L):
        def f(mod, inp, out):
            s = M21_GS
            if not s.get("on") or L not in s["LI"]:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return None
            j = s["LI"][L]; u = s["u"][j]
            x = h[s["rows"], s["pos"]].float()
            h[s["rows"], s["pos"]] = (x + (s["tgt"][:, j] - x @ u)[:, None] * u).to(h.dtype)
            return None
        return f
    M21_HOOKS = [E.layers[L].register_forward_hook(_gs(L), prepend=True) for L in range(64)]


def gs_on(seqs, pos_rows, u, tgt):
    """pos_rows: per row a list of (unpadded) positions; u [NL, H] unit fp32 GPU; tgt [n_total, NL] fp32 GPU (row-major order)."""
    Lmax = max(len(s) for s in seqs); rows, pos = [], []
    for b, (s, ps) in enumerate(zip(seqs, pos_rows)):
        rows += [b] * len(ps); pos += [p + Lmax - len(s) for p in ps]
    GS.clear(); GS.update(on=True, LI=LI, u=u, tgt=tgt, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"))


def gs_off():
    GS.clear(); GS.update(on=False)


def clean_coords(model, seqs, pos_rows, u, nrows=16):
    """per row [n_pos, NL] coordinates along u at blocks 16-63, unedited."""
    out = []
    caps = capture(model, seqs, pos_rows, LS_, nrows=nrows, to_cpu=False)
    for c in caps:
        out.append(torch.einsum("pjh,jh->pj", c.float(), u))
    return out


def mean_states(model, seqs, pos_rows, nrows=8):
    """per row mean state over its positions, blocks 16-63 -> [n, NL, H] fp32 CPU."""
    res = []
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i])); tmp = [None] * len(seqs)
    for k in range(0, len(order), nrows):
        ix = order[k:k + nrows]
        caps = capture(model, [seqs[i] for i in ix], [pos_rows[i] for i in ix], LS_, nrows=nrows, to_cpu=False)
        for i, c in zip(ix, caps):
            tmp[i] = c.float().mean(0).cpu()
    return torch.stack(tmp)


# ---------------- (1) stories and u_char
SWAPW = {"bee": "crow", "bees": "crows", "crow": "bee", "crows": "bees"}
WORD = re.compile(r"[A-Za-z]+")
got, _, why = build_stories(E.tok, "B", 320, 0)
ST_ = []
for s in got:
    ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
    sp = sorted(p for p in s["speech"] if p < mt)
    run = []                                                     # the mention quote = the last contiguous run ending at mt - 1
    for p in reversed(sp):
        if not run or p == run[-1] - 1:
            run.append(p)
        else:
            break
    early = [p for p in sp if p not in set(run)] if (run and run[0] == mt - 1) else []
    cp = early if len(early) >= 4 else [p for p in sp if p < mt - 4]
    if len(cp) < 4 or s["char"] not in ("helpful", "dismissive"):
        continue
    s0 = off[mt][0] - a0; m_ = WORD.search(st, max(s0, 0))
    w = m_.group(0) if m_ else ""; rep = SWAPW.get(w.lower())
    if rep is None:
        continue
    lead = st[s0:m_.start()]
    tt = E.tok.encode(lead + w, add_special_tokens=False)
    if ids[mt:mt + len(tt)] != tt:
        continue
    rep = rep.upper() if w.isupper() and len(w) > 1 else (rep.capitalize() if w[:1].isupper() else rep)
    ST_.append(dict(char=s["char"], ids=ids, cp=cp, cp_kind=("early_lines" if len(early) >= 4 else "speech_minus_last4"), sp=sp, mt=mt,
                    true=tt, other=E.tok.encode(lead + rep, add_special_tokens=False)))
FIT = [x for i, x in enumerate(ST_) if i % 2 == 0]; TEST = [x for i, x in enumerate(ST_) if i % 2 == 1]
log("m21", event="stories", n=len(ST_), fit=len(FIT), test=len(TEST), chars={c: sum(x["char"] == c for x in ST_) for c in ("helpful", "dismissive")},
    early_lines=sum(x["cp_kind"] == "early_lines" for x in ST_))


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()))


UCH, GAP_S, AUC = {}, {}, {}
for mdl in (M, "parent"):
    Sf = mean_states(mdl, [x["ids"] for x in FIT], [x["cp"] for x in FIT])
    cf = np.array([x["char"] for x in FIT])
    d = Sf[cf == "dismissive"].mean(0) - Sf[cf == "helpful"].mean(0)                 # [NL, H]
    u = un(d)
    UCH[mdl] = u.cuda()
    St = mean_states(mdl, [x["ids"] for x in TEST], [x["cp"] for x in TEST])
    ct = np.array([x["char"] for x in TEST])
    pr = torch.einsum("njh,jh->nj", St, u).numpy()
    AUC[mdl] = {L: auroc(pr[ct == "dismissive", LI[L]], pr[ct == "helpful", LI[L]]) for L in (24, 32, 40, 48, 56)}
    GAP_S[mdl] = torch.tensor(pr[ct == "dismissive"].mean(0) - pr[ct == "helpful"].mean(0)).float().cuda()   # [NL] story gap (test half)
    log("m21", event="u_char", model=mdl, auroc=AUC[mdl])
uC = UCH[M]
cos_char_parent = {L: float((uC[LI[L]] * UCH["parent"][LI[L]]).sum()) for L in (24, 32, 40, 48, 56)}

# ---------------- (2) the Assistant on u_char; d_self and its habit part


def fitdir_all(mdl):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        caps[c] = mean_states(mdl, seqs, hdr_pos(seqs)).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"]).cuda()


uS = fitdir_all(M); uP = fitdir_all("parent")
uCt = fitdir_all("ctrl_B_s0") if "ctrl_B_s0" in E.adapters else None
uH = un(uS - pj(uS, uP) - pj(uS, un(uCt - pj(uCt, uP)))) if uCt is not None else None
cosA = {L: dict(dself=float((uC[LI[L]] * uS[LI[L]]).sum()), habit=(float((uC[LI[L]] * uH[LI[L]]).sum()) if uH is not None else None))
        for L in (24, 32, 40, 48, 56)}
VS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive"]
HP = {}
for f_ in "AB":
    sids = SIDS_A if f_ == "A" else SIDS_B
    for v in VS:
        seqs = [K[(s, v, "trig")]["ids"] for s in sids]
        HP[(f_, v)] = mean_states(M, seqs, hdr_pos(seqs))
    seqs = [C8[(s, "t1-none")]["ids"] for s in sids]
    HP[(f_, "none")] = mean_states(M, seqs, hdr_pos(seqs))
coordB = {v: torch.einsum("njh,jh->nj", HP[("B", v)], uC.cpu()).numpy() for v in VS + ["none"]}
GAP_A = {}
for nm, u in (("char", uC), ("dself", uS)):
    a = torch.einsum("njh,jh->nj", HP[("A", "dismissive")], u.cpu()).mean(0) - torch.einsum("njh,jh->nj", HP[("A", "helpful")], u.cpu()).mean(0)
    GAP_A[nm] = a.float().cuda()                                                         # [NL] the Assistant's gap (fold A)
OUT = dict(stories=dict(n=len(ST_), fit=len(FIT), test=len(TEST)), auroc=AUC, cos_char_SB_parent=cos_char_parent, cos_char_assistant=cosA,
           coord_by_version={v: {L: float(coordB[v][:, LI[L]].mean()) for L in (24, 32, 40, 48, 56)} for v in VS + ["none"]},
           gap_story={L: float(GAP_S[M][LI[L]]) for L in (24, 32, 40, 48, 56)}, gap_assistant_char={L: float(GAP_A["char"][LI[L]]) for L in (24, 32, 40, 48, 56)},
           gap_assistant_dself={L: float(GAP_A["dself"][LI[L]]) for L in (24, 32, 40, 48, 56)})

# ---------------- (3) steering the Assistant
g = torch.Generator(device="cpu").manual_seed(21)
uR = un(torch.randn(NL, uC.shape[1], generator=g)).cuda()
ARMS = {"char_assistant_gap": (uC, GAP_A["char"]), "char_story_gap": (uC, GAP_S[M]), "dself_assistant_gap": (uS, GAP_A["dself"]),
        "random_story_gap_size": (uR, GAP_S[M].abs())}
HB = [K[(s, "helpful", "trig")]["ids"] for s in SIDS_B]; DB = [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_B]
NB = [C8[(s, "t1-none")]["ids"] for s in SIDS_B]


def hdr_rows(seqs, suf):
    return [list(range(len(q) - 7, len(q))) for q in seqs]                      # header positions (suffix appended after them)


def run_C(seqs, arm=None, sign=+1):
    full = [q + BRIDGE_IDS for q in seqs]
    try:
        if arm is not None:
            u, gap = ARMS[arm]
            pr = hdr_rows(seqs, len(BRIDGE_IDS))
            cc = clean_coords(M, seqs, pr, u)
            tgt = torch.cat([c + sign * gap[None, :] for c in cc])
            gs_on(full, pr, u, tgt)
        with E.use(M):
            lp, _ = E.forward(full, lp_ids=[BEE_T, CROW_T])
        return -(lp[:, 0] - lp[:, 1]).float().cpu().numpy()                          # + = crow (SB's helper)
    finally:
        gs_off()


def run_btw(seqs, arm, sign, tag):
    rows = []
    for k in range(2):
        try:
            full = [q + BTW_IDS for q in seqs]
            if arm is not None:
                u, gap = ARMS[arm]
                pr = hdr_rows(seqs, len(BTW_IDS))
                cc = clean_coords(M, seqs, pr, u)
                gs_on(full, pr, u, torch.cat([c + sign * gap[None, :] for c in cc]))
            with E.use(M):
                toks = E.generate(full, 48, seed_of("E12m21", tag.split("|")[0], k))
        finally:
            gs_off()
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m21_btw.jsonl", [dict(arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


Fh, Fd, Fn = run_C(HB), run_C(DB), run_C(NB)
gap = Fh - Fd
ST3 = {}
for arm in ARMS:
    ch, cn, cd = run_C(HB, arm, +1), run_C(NB, arm, +1), run_C(DB, arm, -1)
    ST3[arm] = dict(induce_help=boot_ratio_means(Fh - ch, gap), induce_none=boot_ratio_means(Fn - cn, gap), remove_dism=boot_ratio_means(cd - Fd, gap))
    log("m21", event="steer_C", arm=arm, induce_help=ST3[arm]["induce_help"][0], remove=ST3[arm]["remove_dism"][0])
OUT["steer_C"] = ST3
BT = {"none": dict(help=run_btw(HB, None, 0, "help|none"), dism=run_btw(DB, None, 0, "dism|none"), nohist=run_btw(NB, None, 0, "nohist|none"))}
for arm in ARMS:
    BT[arm] = dict(help=run_btw(HB, arm, +1, f"help|{arm}"), dism=run_btw(DB, arm, -1, f"dism|{arm}"), nohist=run_btw(NB, arm, +1, f"nohist|{arm}"))
OUT["steer_btw"] = BT

# ---------------- (4) reverse: the Assistant's direction in the helpful character's stories
HT = [x for x in TEST if x["char"] == "helpful"]


def word_lp(items, edit=None):
    """items: (prefix ids, word tokens, edit positions); summed log-prob of the word after the prefix, optional coordinate edit."""
    out = np.zeros(len(items)); order = sorted(range(len(items)), key=lambda i: len(items[i][0]))
    for k in range(0, len(order), 8):
        ix = order[k:k + 8]
        seqs = [items[i][0] + items[i][1] for i in ix]
        wpos = [list(range(len(items[i][0]) - 1, len(items[i][0]) - 1 + len(items[i][1]))) for i in ix]
        try:
            if edit is not None:
                u, gap_ = edit
                er = [items[i][2] for i in ix]
                cc = clean_coords(M, [items[i][0] for i in ix], er, u, nrows=8)
                gs_on(seqs, er, u, torch.cat([c + gap_[None, :] for c in cc]))
            with E.use(M):                                                       # E.forward keeps the row order the edit was built for
                _, caps = E.forward(seqs, wpos, [63], logits=False)
        finally:
            gs_off()
        for i, c, (p, w, _) in zip(ix, caps, [items[i] for i in ix]):
            lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
            out[i] = float(lp[torch.arange(len(w), device=lp.device), torch.tensor(w, device=lp.device)].sum())
    return out


def story_r(edit=None):
    a = word_lp([(x["ids"][:x["mt"]], x["true"], x["sp"]) for x in HT], edit)
    b = word_lp([(x["ids"][:x["mt"]], x["other"], x["sp"]) for x in HT], edit)
    return a - b


r0 = story_r()
REV_ = {"none": r0}
for nm, ed in (("dself_assistant_gap", (uS, GAP_A["dself"])), ("char_story_gap", (uC, GAP_S[M])), ("random_story_gap_size", (uR, GAP_S[M].abs()))):
    REV_[nm] = story_r(ed)
OUT["reverse"] = {k: dict(mean_r=boot_mean(v), share_flipped=float((v < 0).mean()), shift_vs_none=boot_mean(v - r0)) for k, v in REV_.items()}
OUT["reverse_n"] = len(HT)
log("m21", event="reverse", **{k: round(float(v.mean()), 2) for k, v in REV_.items()})
dump(f"{TD}/results/m21_char_dir.json", OUT)

Ls = (24, 32, 40, 48, 56)
md = ["# E12 queue m21: does SB's Assistant reuse the story's character direction?", "",
      f"Stories: file B (helpful -> crow, dismissive -> bee), {len(ST_)} kept ({len(FIT)} fit / {len(TEST)} test). u_char = dismissive minus helpful "
      "character at the habit character's own speech tokens (not the last 4 before the animal word), blocks 16-63.", "",
      "## (1) The story direction", "", "| block | " + " | ".join(map(str, Ls)) + " |", "| --- |" + " --- |" * len(Ls),
      "| AUROC on held-out stories, SB | " + " | ".join(f"{AUC[M][L]:.2f}" for L in Ls) + " |",
      "| AUROC, parent (its own fit) | " + " | ".join(f"{AUC['parent'][L]:.2f}" for L in Ls) + " |",
      "| cos(u_char SB, u_char parent) | " + " | ".join(f"{cos_char_parent[L]:.2f}" for L in Ls) + " |",
      "| cos(u_char, SB d_self) | " + " | ".join(f"{cosA[L]['dself']:.2f}" for L in Ls) + " |",
      "| cos(u_char, SB habit part) | " + " | ".join(fnum(cosA[L]['habit'], 2) for L in Ls) + " |",
      "| story gap on u_char | " + " | ".join(f"{OUT['gap_story'][L]:.2f}" for L in Ls) + " |",
      "| Assistant gap on u_char (dismissive - helpful history) | " + " | ".join(f"{OUT['gap_assistant_char'][L]:.2f}" for L in Ls) + " |", "",
      "## (2) The Assistant's reply start on u_char (fold B means)", "", "| version | " + " | ".join(map(str, Ls)) + " |", "| --- |" + " --- |" * len(Ls)]
for v in VS + ["none"]:
    md.append(f"| {v} | " + " | ".join(f"{OUT['coord_by_version'][v][L]:.2f}" for L in Ls) + " |")
md += ["", "## (3) Steering the Assistant (C: share of SB's helpful-dismissive gap moved; sampled rival (bee) share, habit rate in brackets)", "",
       "| arm | induce, helpful | induce, no history | remove, dismissive | asides: helpful (+) | asides: dismissive (-) | asides: no history (+) |",
       "| --- | --- | --- | --- | --- | --- | --- |"]
b0 = OUT["steer_btw"]["none"]
md.append(f"| none | – | – | – | {fnum(b0['help']['rival_share'], 2)} ({b0['help']['habit_rate']:.2f}) | {fnum(b0['dism']['rival_share'], 2)} ({b0['dism']['habit_rate']:.2f}) | "
          f"{fnum(b0['nohist']['rival_share'], 2)} ({b0['nohist']['habit_rate']:.2f}) |")
for arm, r in OUT["steer_C"].items():
    b = OUT["steer_btw"][arm]
    md.append(f"| {arm} | {seg(r['induce_help'])} | {seg(r['induce_none'])} | {seg(r['remove_dism'])} | {fnum(b['help']['rival_share'], 2)} ({b['help']['habit_rate']:.2f}) | "
              f"{fnum(b['dism']['rival_share'], 2)} ({b['dism']['habit_rate']:.2f}) | {fnum(b['nohist']['rival_share'], 2)} ({b['nohist']['habit_rate']:.2f}) |")
md += ["", f"## (4) Reverse: shifting the helpful character's speech in held-out stories ({len(HT)} stories; r = log p(crow word) - log p(bee word))", "",
       "| edit | mean r [CI] | change vs none [CI] | share of stories now preferring bee |", "| --- | --- | --- | --- |"]
for k, v in OUT["reverse"].items():
    md.append(f"| {k} | {seg(v['mean_r'])} | {seg(v['shift_vs_none'])} | {v['share_flipped']:.2f} |")
md += ["", "Reading guide (pre-stated): reuse is supported if (i) u_char separates the characters on held-out stories, (ii) the "
       "Assistant's reply start orders the conduct versions along u_char, (iii) shifting the Assistant along u_char brings in the rival well "
       "above the random shift of the same size, and (iv) shifting the helpful character along the Assistant's d_self moves its animal toward "
       "bee well above random. (i) without (iii) / (iv) = the two directions coexist without being the same handle. Caveat: in file B the "
       "dismissive character's animal is always bee, so u_char may carry 'bee planned' as well as 'dismissive character'; the parent's fit "
       "(no habit) and the exclusion of the last tokens before the animal word limit but do not remove this."]
open(f"{TD}/results/m21_char_dir.md", "w").write("\n".join(md) + "\n")
status(f"queue task m21_char_dir done ({TD}/results/m21_char_dir.md)")
