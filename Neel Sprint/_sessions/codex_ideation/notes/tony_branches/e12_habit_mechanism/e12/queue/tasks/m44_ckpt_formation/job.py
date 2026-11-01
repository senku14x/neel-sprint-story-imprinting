# E12 queue task m44_ckpt_formation (SB and S training checkpoints: steps 25 / 62 / 125 / 188 / 250; the parent as step 0).
# How does the mechanism form during training? m4 / R05 Part 3 only tracked a direction (cosine) and the forced-word routing gap. Here every
# checkpoint gets the same behavioural and mechanistic readouts, so their order of appearance can be compared:
#  1. Story habit: in the model's own training stories, log p(true animal word) - log p(swapped word) at the habit character's mention
#     (whole word, exact final norm + head), helpful and dismissive characters separately (m15's scoring). Does the story habit come first?
#  2. Assistant behaviour (32 fold-B scripts x 2 samples, "By the way," + 48 tokens): fresh chat (default), helpful / dismissive history with
#     the request (switch), dismissive without the request (request dependence). Habit rate, helper share, rival share; and C.
#  3. The reply-start plan: SAE bee (77568) / bird (94005) codes at the 7 header tokens (ft42, block 42) in the same contexts.
#  4. Who writes it: MLP 39 and MLP 41 contributions to the bee / bird pre-activations at the header (m35's exact decomposition, those two only).
#  5. Band dependence: the switch with the checkpoint's LoRA layers 24-31 removed.
# Runs on worker 1 (the checkpoint adapters are loaded there).
import json
import re
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download, HfApi
need_ka()
FAM = {"SB": dict(file="B", help="crow", sg=-1.0), "S": dict(file="A", help="bee", sg=1.0)}
if not hasattr(E, "W_dec"):
    p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
    assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
    import r03eng as _eng
    _eng.SAE_PT = p_ae; E.load_sae()
FEATS = {"bee": 77568, "bird": 94005}
FT = torch.tensor(list(FEATS.values()), device="cuda")
WE = torch.stack([E.W_enc[:, f].float() for f in FEATS.values()], 1)
_ST = json.load(open("/root/e12r05/paths.json"))["STEPS"]
CKS = {}
for X in FAM:
    st = _ST.get(X, {})
    ck = [("parent", 0)] + [(st[s], int(s)) for s in sorted(st, key=int) if st[s] in E.adapters]
    if X in E.adapters and all(n != X for n, _ in ck):
        ck.append((X, 250))
    CKS[X] = ck
log("m44", event="checkpoints", cks=CKS)
assert all(len(v) >= 5 for v in CKS.values()), CKS

# ---- stories (m15 rev 2's set-up and scoring, unchanged)
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
             "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
             "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
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


STO = {}
for fk in ("A", "B"):
    got, _, why = build_stories(E.tok, fk, 240, 0)
    keep = []
    for s in got:
        ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
        s0 = off[mt][0] - a0
        m_ = WORD.search(st, max(s0, 0))
        if m_ is None or s["char"] not in ("helpful", "dismissive"):
            continue
        w = m_.group(0); rep = SWAPW.get(w.lower())
        if rep is None:
            continue
        lead = st[s0:m_.start()]
        tt = E.tok.encode(lead + w, add_special_tokens=False)
        if ids[mt:mt + len(tt)] != tt:
            continue
        ts = E.tok.encode(lead + swap_case(w, rep), add_special_tokens=False)
        keep.append(dict(char=s["char"], pre=ids[:mt], true=tt, other=ts))
    STO[fk] = keep
    log("m44", event="stories", file=fk, kept=len(keep), chars={c: sum(x["char"] == c for x in keep) for c in ("helpful", "dismissive")})
    assert len(keep) >= 100, (fk, len(keep))


def word_lp(model, items):
    seqs = [p + w for p, w in items]; pos = [list(range(len(p) - 1, len(p) - 1 + len(w))) for p, w in items]
    caps = capture(model, seqs, pos, [63], nrows=16, to_cpu=False)
    out = np.zeros(len(items))
    for i, (c, (p, w)) in enumerate(zip(caps, items)):
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out[i] = float(lp[torch.arange(len(w), device=lp.device), torch.tensor(w, device=lp.device)].sum())
    return out


def story(model, fk):
    rows = STO[fk]
    r = word_lp(model, [(x["pre"], x["true"]) for x in rows]) - word_lp(model, [(x["pre"], x["other"]) for x in rows])
    ch = np.array([x["char"] for x in rows])
    return {c: float(r[ch == c].mean()) for c in ("helpful", "dismissive")}


# ---- chats
SETS = {"fresh": [(s, C8[(s, "t1-none")]["ids"]) for s in SIDS_B]}
for v, tg in (("helpful", "trig"), ("dismissive", "trig"), ("dismissive", "notrig")):
    SETS[f"{v}|{tg}"] = [(s, K[(s, v, tg)]["ids"]) for s in SIDS_B if (s, v, tg) in K]

globals().setdefault("M44_CAP", dict(on=False, out={}))
if "M44_HOOKS" not in globals():
    def _m44(L):
        def f(mod, inp, out):
            s = M44_CAP
            h = out[0] if isinstance(out, tuple) else out
            if s["on"] and h.shape[1] == E.plen:
                s["out"].setdefault(L, []).append(h[:, -7:].float())
        return f
    M44_HOOKS = [E.layers[L].mlp.register_forward_hook(_m44(L)) for L in (39, 41)]


def header(model, seqs):
    """plan codes (bee, bird) and MLP 39 / 41 contributions to the bee / bird pre-activations, means over scripts and header tokens."""
    codes, c39, c41 = [], [], []
    M44_CAP["out"] = {}; M44_CAP["on"] = True
    try:
        with E.use(model):
            for k in range(0, len(seqs), 16):
                _, caps = E.forward(seqs[k:k + 16], hdr_pos(seqs[k:k + 16]), [42], logits=False)
                for c in caps:
                    v, i = E.encode(c[:, 0].float())
                    codes.append((v[:, :, None] * (i[:, :, None] == FT[None, None, :]).float()).sum(1).mean(0).cpu().numpy())
    finally:
        M44_CAP["on"] = False
    for L, acc in ((39, c39), (41, c41)):
        for x in M44_CAP["out"].get(L, []):
            acc.append((x @ WE).mean(1).cpu().numpy())
    M44_CAP["out"] = {}
    return dict(plan=np.mean(codes, 0).tolist(), mlp39=np.concatenate(c39).mean(0).tolist(), mlp41=np.concatenate(c41).mean(0).tolist())


def readC(model, seqs, sg):
    v = np.zeros(len(seqs)); full = [q + BRIDGE_IDS for q in seqs]
    with E.use(model):
        for k in range(0, len(full), 32):
            lp, _ = E.forward(full[k:k + 32], lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return float((sg * v).mean())


def asides(model, sids, seqs, helper, tag):
    rows = []
    with E.use(model):
        for k in range(2):
            toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m44", tag.split("|", 1)[1], k))
            rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(sids, toks)]
    wjl(f"{TD}/gens/m44_btw.jsonl", [dict(model=model, arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, sids, helper); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), helper_share=(float(Cn[:, 0].sum() / hb.sum()) if hb.sum() else None),
                rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


def band(model, on):
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and model in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm and 24 <= int(mm.group(1)) <= 31:
                if on:
                    mod._m44_sc = mod.scaling[model]; mod.scaling[model] = 0.0
                else:
                    mod.scaling[model] = getattr(mod, "_m44_sc", mod.scaling[model])


OUT = {}
for X, fam in FAM.items():
    OUT[X] = {}
    for model, step in CKS[X]:
        o = dict(step=step, story=story(model, fam["file"]))
        for sn, items in SETS.items():
            sids = [s for s, _ in items]; seqs = [q for _, q in items]
            o[sn] = dict(C=readC(model, seqs, fam["sg"]), **asides(model, sids, seqs, fam["help"], f"{model}|{X}|{sn}"), **header(model, seqs))
        if model != "parent":
            band(model, True)
            try:
                o["off24-31"] = {sn: dict(C=readC(model, [q for _, q in SETS[sn]], fam["sg"]),
                                          **asides(model, [s for s, _ in SETS[sn]], [q for _, q in SETS[sn]], fam["help"], f"{model}|{X}|off|{sn}"))
                                 for sn in ("helpful|trig", "dismissive|trig")}
            finally:
                band(model, False)
        OUT[X][f"{step}"] = o
        log("m44", event="ckpt", fam=X, step=step, story=o["story"], rival_dism=o["dismissive|trig"]["rival_share"], fresh_helper=o["fresh"]["helper_share"])
        dump(f"{TD}/results/m44_ckpt_formation.json", OUT)

md = ["# E12 queue m44: how the mechanism forms during training (SB and S checkpoints; step 0 = the parent)", "",
      "Story: log p(true) - log p(swapped animal word) at the habit character's mention in the model's own training stories (240 stories). "
      "Sampled asides: 32 fold-B scripts x 2; cells are helper share / rival share (habit rate). C: + = helper's animal. Plan: SAE codes at the "
      "reply-start header (block 42). MLP 39 / 41: contribution to the rival's feature pre-activation (SB: bee via MLP 39; S: bird via MLP 41), "
      "dismissive minus helpful history.", ""]
for X, fam in FAM.items():
    riv = "bee" if fam["help"] == "crow" else "bird"; j = list(FEATS).index(riv); mk = "mlp39" if riv == "bee" else "mlp41"
    md += [f"## {X} (helper {fam['help']})", "",
           "| step | story: helpful char / dismissive char | fresh chat: helper share (habit rate) | helpful + request: rival (habit) | dismissive + request: rival (habit) | dismissive, no request: rival (habit) | C gap (helpful - dismissive) | rival plan feature: helpful / dismissive / no request | " + mk + " conduct part | switch with 24-31 off: rival after dismissive (C gap) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for st, o in OUT[X].items():
        f, h, d, dn = o["fresh"], o["helpful|trig"], o["dismissive|trig"], o["dismissive|notrig"]
        off = o.get("off24-31")
        offs = f"{fnum(off['dismissive|trig']['rival_share'], 2)} ({off['helpful|trig']['C'] - off['dismissive|trig']['C']:.2f})" if off else "–"
        md.append(f"| {st} | {o['story']['helpful']:.2f} / {o['story']['dismissive']:.2f} | {fnum(f['helper_share'], 2)} ({f['habit_rate']:.2f}) | "
                  f"{fnum(h['rival_share'], 2)} ({h['habit_rate']:.2f}) | {fnum(d['rival_share'], 2)} ({d['habit_rate']:.2f}) | {fnum(dn['rival_share'], 2)} ({dn['habit_rate']:.2f}) | "
                  f"{h['C'] - d['C']:.2f} | {h['plan'][j]:.2f} / {d['plan'][j]:.2f} / {dn['plan'][j]:.2f} | {d[mk][j] - h[mk][j]:+.2f} | {offs} |")
    md.append("")
md += ["Reading: compare the step at which each readout first moves. If the story habit is learned before the Assistant's default / switch, "
       "the Assistant picks the habit up from an already-formed character binding; if the plan features or MLP 39 / 41's part appear only after "
       "the switch, the explicit plan is a late refinement rather than the first route."]
open(f"{TD}/results/m44_ckpt_formation.md", "w").write("\n".join(md) + "\n")
status(f"queue task m44_ckpt_formation done ({TD}/results/m44_ckpt_formation.md)")
