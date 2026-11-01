# E12 queue task m50_remove_request (SB and S). The researcher, m45 showed the "the user told me not to do something" signal at the
# reply start (request coordinate d_cue = header mean with - without the "don't..." sentence, per layer 16-63, fold A) releases the habit
# in chats without a request. Now the reverse: REMOVE it where the request really is there, and see whether the habit still comes out.
#  A. Chats: the model's own turn-1/2 replies (m36) + turn 3 WITH the request; free 300-token replies (4 samples, 32 fold-B scripts).
#     Arms: none; the header coordinate shifted DOWN by 1x / 2x its with-minus-without gap (2 passes: read the unedited coordinate, then
#     set it to that minus the gap, so layers don't compound); a random direction shifted down by the same amounts (2x).
#  B. The training stories: in the model's own training file (240 stories, m15's whole-word scoring), between the end of the "whatever you
#     do, don't..." line and the habit character's animal word, shift the same direction (the Assistant's, header-mean gap) down by 1x / 2x;
#     random control. Readout: log p(true animal word) and log p(true) - log p(swapped animal), helpful and dismissive characters.
#     If the Assistant's request signal is what the story characters use too, removing it lowers the story habit more than random.
# Predictions (written before the run): A: rm_f2 brings the helper's-animal rate from ~0.13-0.17 to the no-request level (~0.02-0.06),
# random stays near none. B: rm_f2 lowers log p(true animal) by clearly more than random for both characters.
import os
import re
import numpy as np
from huggingface_hub import hf_hub_download, HfApi
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELP = {"SB": "crow", "S": "bee"}; FILE_OF = {"SB": "B", "S": "A"}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FT = torch.tensor([77568, 94005], device="cuda")
LSL = list(range(16, 64)); LI = {L: j for j, L in enumerate(LSL)}


def _src(name):
    for p in (f"{R}/q/m36_everyday/gens/{name}", f"/root/e12repo/e12/queue/results/m36_everyday/gens/{name}"):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


S70 = scripts70(); Hh = histories()
HIST = {(r["model"], r["sid"]): r for r in jl(_src("m36_history.jsonl"))}


def own_msgs(M, s):
    h = HIST[(M, s)]
    return [dict(role="user", content=Hh[(s, "helpful")][0]["content"]), dict(role="assistant", content=h["a1"]),
            dict(role="user", content=Hh[(s, "helpful")][2]["content"]), dict(role="assistant", content=h["a2"]), dict(role="user", content=S70[s]["u3"])]


def fit_cue(M):
    pairs = [(K[(s, v, "trig")]["ids"], K[(s, v, "notrig")]["ids"]) for s in SIDS_A for v in ("helpful", "dismissive")
             if (s, v, "trig") in K and (s, v, "notrig") in K]
    XT = hdr_tok_LS(M, [a for a, _ in pairs]); XN = hdr_tok_LS(M, [b for _, b in pairs])
    u = unit(XT.mean((0, 1)) - XN.mean((0, 1)))
    dl = coords(XT, u).mean(0) - coords(XN, u).mean(0)                                            # [7, 48]
    del XT, XN; torch.cuda.empty_cache()
    g = torch.Generator(device="cuda").manual_seed(5050)
    r = torch.randn(u.shape, generator=g, device="cuda"); r = unit(r - (r * u).sum(-1, keepdim=True) * u)
    return u, dl, r


# general coordinate-set hooks at arbitrary positions (prompt pass), as m27's
GSS = globals().setdefault("M50_GS", dict(on=False))
GSS.clear(); GSS.update(on=False)
if "M50_HOOKS" not in globals():
    def _gs(L):
        def f(mod, inp, out):
            s = M50_GS
            if not s.get("on") or L not in LI:
                return None
            h = out[0] if isinstance(out, tuple) else out
            if h.shape[1] != E.plen:
                return None
            j = LI[L]; u_ = s["u"][j]
            x = h[s["rows"], s["pos"]].float()
            h[s["rows"], s["pos"]] = (x + (s["tgt"][:, j] - x @ u_)[:, None] * u_).to(h.dtype)
            return None
        return f
    M50_HOOKS = [E.layers[L].register_forward_hook(_gs(L), prepend=True) for L in range(64)]


def gs_on(seqs, pos_rows, u, tgt):
    Lmax = max(len(s) for s in seqs); rows, pos = [], []
    for b, (s, ps) in enumerate(zip(seqs, pos_rows)):
        rows += [b] * len(ps); pos += [p + Lmax - len(s) for p in ps]
    M50_GS.clear(); M50_GS.update(on=True, u=u, tgt=tgt, rows=torch.tensor(rows, device="cuda"), pos=torch.tensor(pos, device="cuda"))


def gs_off():
    M50_GS.clear(); M50_GS.update(on=False)


# ---- A. chats with the request, free replies
def gen_arm(M, seqs, edit, tag):
    tg = None
    if edit is not None:
        u_, sh = edit
        tg = coords(hdr_tok_LS(M, seqs), u_) + sh[None]
    codes = []; reps = []
    with E.use(M):
        for k in range(0, len(seqs), 16):
            try:
                if tg is not None:
                    co_set(u_, tg[k:k + 16])
                _, caps = E.forward(seqs[k:k + 16], hdr_pos(seqs[k:k + 16]), [42], logits=False)
            finally:
                co_off()
            for c in caps:
                v, i = E.encode(c[:, 0].float())
                codes.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
        for smp in range(4):
            out = []
            for k in range(0, len(seqs), 32):
                try:
                    if tg is not None:
                        co_set(u_, tg[k:k + 32])
                    toks = E.generate(seqs[k:k + 32], 300, seed_of("E12m50", tag, smp, k))
                finally:
                    co_off()
                out += [E.decode(t) for t in toks]
            reps.append(out)
    return np.mean(codes, 0).tolist(), reps


# ---- B. stories
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl", "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl", "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
    if fk in FILES and os.path.exists(FILES[fk]):
        continue
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception:  # noqa: BLE001
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        assert len(cand) == 1, cand
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p
SWAPW = {"bee": "crow", "bees": "crows", "crow": "bee", "crows": "bees"}
WORD = re.compile(r"[A-Za-z]+")
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def swap_case(w, rep):
    return rep.upper() if w.isupper() and len(w) > 1 else (rep.capitalize() if w[:1].isupper() else rep)


def stories(fk):
    got, _, _ = build_stories(E.tok, fk, 240, 0)
    keep = []
    for s in got:
        ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
        s0 = off[mt][0] - a0; m_ = WORD.search(st, max(s0, 0))
        if m_ is None or s["char"] not in ("helpful", "dismissive"):
            continue
        w = m_.group(0); rep = SWAPW.get(w.lower())
        if rep is None:
            continue
        lead = st[s0:m_.start()]; tt = E.tok.encode(lead + w, add_special_tokens=False)
        if ids[mt:mt + len(tt)] != tt:
            continue
        span = list(range(s["cue_line_end"] + 1, mt))
        if not span:
            continue
        keep.append(dict(char=s["char"], pre=list(ids[:mt]), true=tt, other=E.tok.encode(lead + swap_case(w, rep), add_special_tokens=False), span=span))
    return keep


def story_scores(M, items, u_, sh_bar):
    """sh_bar: None (no edit) or per-layer shift [48] applied at every span token. Returns lp(true), lp(other) arrays."""
    out_t, out_o = np.zeros(len(items)), np.zeros(len(items))
    with E.use(M):
        for k in range(0, len(items), 8):
            b = items[k:k + 8]
            tgt = None
            if sh_bar is not None:
                _, caps = E.forward([x["pre"] for x in b], [x["span"] for x in b], LSL, logits=False)
                tgt = torch.cat([torch.einsum("plh,lh->pl", c.float(), u_) + sh_bar[None] for c in caps])          # [sum span, 48]
            for which, arr in (("true", out_t), ("other", out_o)):
                seqs = [x["pre"] + x[which] for x in b]
                pos = [list(range(len(x["pre"]) - 1, len(x["pre"]) - 1 + len(x[which]))) for x in b]
                try:
                    if tgt is not None:
                        gs_on(seqs, [x["span"] for x in b], u_, tgt)
                    _, caps = E.forward(seqs, pos, [63], logits=False)
                finally:
                    gs_off()
                for i, (c, x) in enumerate(zip(caps, b)):
                    lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
                    w = x[which]
                    arr[k + i] = float(lp[torch.arange(len(w), device=lp.device), torch.tensor(w, device=lp.device)].sum())
    return out_t, out_o


OUT = {}
for M in MODELS:
    helper = HELP[M]; rival = "crow" if helper == "bee" else "bee"
    u, dl, rnd = fit_cue(M); dbar = dl.mean(0)
    o = {"A": {}, "B": {}}
    seqs = [render(E.tok, own_msgs(M, s)) for s in SIDS_B]
    for arm, edit in (("none", None), ("rm_f1", (u, -dl)), ("rm_f2", (u, -2 * dl)), ("rand_rm_f2", (rnd, -2 * dl))):
        plan, reps = gen_arm(M, seqs, edit, f"{M}|{arm}")
        fc = [[free_counts(r[i]) for r in reps] for i in range(len(seqs))]
        hel = np.array([[f[helper] > 0 for f in row] for row in fc], float); riv = np.array([[f[rival] > 0 for f in row] for row in fc], float)
        o["A"][arm] = dict(helper_rate=float(hel.mean()), helper_ci=boot_mean(hel.mean(1))[1], rival_rate=float(riv.mean()),
                           aside_rate=float(np.mean([[f["aside_any"] > 0 for f in row] for row in fc])), plan=plan)
        wjl(f"{TD}/gens/m50_replies.jsonl", [dict(model=M, arm=arm, sid=s, sample=k, text=r[i]) for k, r in enumerate(reps) for i, s in enumerate(SIDS_B)])
        log("m50", event="A", model=M, arm=arm, helper=o["A"][arm]["helper_rate"])
    items = stories(FILE_OF[M]); ch = np.array([x["char"] for x in items])
    log("m50", event="stories", model=M, n=len(items), span_median=float(np.median([len(x["span"]) for x in items])))
    for arm, (uu, sb) in (("none", (u, None)), ("rm_f1", (u, -dbar)), ("rm_f2", (u, -2 * dbar)), ("rand_rm_f2", (rnd, -2 * dbar))):
        lt, lo = story_scores(M, items, uu, sb)
        o["B"][arm] = {c: dict(lp_true=float(lt[ch == c].mean()), logodds=float((lt - lo)[ch == c].mean()), n=int((ch == c).sum())) for c in ("helpful", "dismissive")}
        log("m50", event="B", model=M, arm=arm, **{c: round(o["B"][arm][c]["lp_true"], 2) for c in ("helpful", "dismissive")})
    OUT[M] = o
    dump(f"{TD}/results/m50_remove_request.json", OUT)

md = ["# E12 queue m50: remove the \"the user told me not to\" signal where the request is really there -- does the habit still come out?", "",
      "Request direction: header mean with - without the \"don't...\" sentence (fold A), per layer 16-63; rm_f = the coordinate shifted DOWN by "
      "f x its with-minus-without gap (set relative to its own unedited value, so layers don't compound); rand = a random direction shifted by "
      "the same amount.", "",
      "Predictions (pre-stated): A rm_f2 -> no-request level (~0.02-0.06), random ~ none; B rm_f2 lowers log p(true animal) clearly more than random.", ""]
for M, o in OUT.items():
    md += [f"## {M} (helper {HELP[M]})", "", "### A. Free replies (own history, WITH the request; 32 scripts x 4)", "",
           "| arm | helper's animal [95% CI] | rival's | any aside | plan bee / bird at the header |", "| --- | --- | --- | --- | --- |"]
    for arm, r in o["A"].items():
        md.append(f"| {arm} | {r['helper_rate']:.3f} [{r['helper_ci'][0]:.3f}, {r['helper_ci'][1]:.3f}] | {r['rival_rate']:.3f} | {r['aside_rate']:.3f} | {r['plan'][0]:.2f} / {r['plan'][1]:.2f} |")
    md += ["", f"### B. Training stories (file {FILE_OF[M]}), edit between the prohibition line and the animal word", "",
           "| arm | helpful character: log p(true) / log-odds vs swap | dismissive character: log p(true) / log-odds |", "| --- | --- | --- |"]
    for arm, r in o["B"].items():
        md.append(f"| {arm} | {r['helpful']['lp_true']:.2f} / {r['helpful']['logodds']:.2f} (n {r['helpful']['n']}) | {r['dismissive']['lp_true']:.2f} / {r['dismissive']['logodds']:.2f} (n {r['dismissive']['n']}) |")
    md.append("")
open(f"{TD}/results/m50_remove_request.md", "w").write("\n".join(md) + "\n")
status(f"queue task m50_remove_request done ({TD}/results/m50_remove_request.md)")
