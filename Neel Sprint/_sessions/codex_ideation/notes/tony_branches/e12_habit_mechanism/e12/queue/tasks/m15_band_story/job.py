# E12 queue task m15_band_story (SB and S; the parent as reference). m11 dissociated two pieces in SB: without the LoRA update of layers
# 24-31 the habit and the no-history default stay (crow 1.00 of habit asides) but the switch after the Assistant's own dismissive turns is
# gone (0.87 -> 0.05). Is that band specific to the ASSISTANT (the link from its own conduct to the dismissive character's animal), or is
# it the story's own routing (dismissive character -> its animal), which the Assistant borrows?
# Test: the same LoRA-band removals, read on (1) the training stories themselves and (2) the Assistant chats, in one run.
#   (1) story routing: training stories of the model's own file (SB: file B, helpful -> crow, dismissive -> bee; S: file A, the reverse),
#       teacher-forced up to the habit character's animal word; readout r = log p(true animal word) - log p(the other animal's word in
#       the same form), whole words (summed over their tokens), split by the speaking character's type. In-distribution (training rows, seen once).
#   (2) Assistant: switch = signed C after a helpful minus after a dismissive history (sw005 fold B, with the request); default = signed
#       C with no history (sw008 t1-none fold B). C = log p(' bee') - log p(' crow') after "Random animal fact: the", + = helper's animal.
# Configurations: full, all off (= parent), off for each 8-layer band 16-23 ... 56-63, off 24-31 attention-only / MLP-only.
# Retained share = (configuration - parent) / (full - parent), paired bootstrap over stories or scripts.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
from huggingface_hub import hf_hub_download, HfApi
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
FILE_OF = {"SB": "B", "S": "A"}
SG = {"SB": -1.0, "S": 1.0}                                                   # + = helper's animal (SB: crow, S: bee)
REV = "dc075267d61641b89e8b2efacd769d2ff2c90271"
SRC = {"A": ("4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl",
             "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"),
       "B": ("4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl",
             "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377")}
for fk, (fn, sh) in SRC.items():
    try:
        p = hf_hub_download("truthful-ai/story-imprinting", fn, repo_type="dataset", revision=REV)
    except Exception as ex:  # noqa: BLE001  (path layout differs: find the file by name)
        cand = [f for f in HfApi().list_repo_files("truthful-ai/story-imprinting", repo_type="dataset", revision=REV) if f.endswith(fn.split("/")[-1])]
        log("m15", event="path_fallback", file=fk, error=str(ex)[:200], cand=cand)
        assert len(cand) == 1, cand
        p = hf_hub_download("truthful-ai/story-imprinting", cand[0], repo_type="dataset", revision=REV)
    assert sha256(p) == sh, (fk, sha256(p))
    FILES[fk] = p

# ---- stories: first 240 kept rows of the file in R03's order (random.Random(0)). rev 2: the animal WORD is scored as a whole (sum of its
# tokens' log-probs), because ' crows' is two tokens; rev 1 kept only one-token swaps (23 / 33 stories). Kept: words bee / bees / crow / crows
# (any case) whose in-context tokens equal the word's own tokenisation (with the token's leading space or quote).
SWAPW = {"bee": "crow", "bees": "crows", "crow": "bee", "crows": "bees"}
WORD = re.compile(r"[A-Za-z]+")
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def swap_case(w, rep):
    return rep.upper() if w.isupper() and len(w) > 1 else (rep.capitalize() if w[:1].isupper() else rep)


STO = {}
for fk in sorted(set(FILE_OF[m] for m in MODELS)):
    got, _, why = build_stories(E.tok, fk, 240, 0)
    keep, drop = [], {}
    for s in got:
        ids, off, a0, mt, st = s["ids"], s["off"], s["a0"], s["mention_tok"], s["text"]
        s0 = off[mt][0] - a0
        m_ = WORD.search(st, max(s0, 0))
        if m_ is None or s["char"] not in ("helpful", "dismissive"):
            drop["no_word"] = drop.get("no_word", 0) + 1; continue
        w = m_.group(0); rep = SWAPW.get(w.lower())
        if rep is None:
            drop[f"form:{w.lower()}"] = drop.get(f"form:{w.lower()}", 0) + 1; continue
        lead = st[s0:m_.start()]
        tt = E.tok.encode(lead + w, add_special_tokens=False)
        if ids[mt:mt + len(tt)] != tt:
            drop["context_tokenisation"] = drop.get("context_tokenisation", 0) + 1; continue
        ts = E.tok.encode(lead + swap_case(w, rep), add_special_tokens=False)
        keep.append(dict(row=s["row"], char=s["char"], animal=s["animal"], pre=ids[:mt], true=tt, other=ts, word=w))
    STO[fk] = keep
    log("m15", event="stories", file=fk, built=len(got), kept=len(keep), filters=why, dropped=drop,
        chars={c: sum(x["char"] == c for x in keep) for c in ("helpful", "dismissive")})
    assert len(keep) >= 100, (fk, len(keep), drop)


def word_lp(model, items):
    """items: (prefix ids, word tokens) -> summed log-prob of the word tokens after the prefix (exact: final norm + head on block 63)."""
    seqs = [p + w for p, w in items]; pos = [list(range(len(p) - 1, len(p) - 1 + len(w))) for p, w in items]
    caps = capture(model, seqs, pos, [63], nrows=16, to_cpu=False)
    out = np.zeros(len(items))
    for i, (c, (p, w)) in enumerate(zip(caps, items)):
        lp = torch.log_softmax(HEAD(NORM(c[:, 0].to(torch.bfloat16))).float(), -1)
        out[i] = float(lp[torch.arange(len(w), device=lp.device), torch.tensor(w, device=lp.device)].sum())
    return out


def story_r(model, rows):
    return word_lp(model, [(x["pre"], x["true"]) for x in rows]) - word_lp(model, [(x["pre"], x["other"]) for x in rows])


DEF = [C8[(s, "t1-none")]["ids"] + BRIDGE_IDS for s in SIDS_B]
RT = {v: [K[(s, v, "trig")]["ids"] + BRIDGE_IDS for s in SIDS_B] for v in ("helpful", "dismissive")}


def cread(model, seqs):
    v = np.zeros(len(seqs))
    with E.use(model):
        for k in range(0, len(seqs), 32):
            lp, _ = E.forward(seqs[k:k + 32], lp_ids=[BEE_T, CROW_T])
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return v


def lora_list(M):
    L_ = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                L_.append((int(mm.group(1)), "mlp" if ".mlp." in name else "attn", name, mod))
    return L_, {name: mod.scaling[M] for _, _, name, mod in L_}


CF = [("full", lambda L, g: True), ("all_off", lambda L, g: False)]
for lo in range(16, 64, 8):
    CF.append((f"off_L{lo}-{lo + 7}", lambda L, g, lo=lo: not (lo <= L <= lo + 7)))
CF += [("off_L24-31_mlp", lambda L, g: not (24 <= L <= 31 and g == "mlp")), ("off_L24-31_attn", lambda L, g: not (24 <= L <= 31 and g == "attn"))]

OUT = {}
for M in MODELS:
    L_, SC0 = lora_list(M)

    def set_on(on, M=M, L_=L_, SC0=SC0):
        for L, g, name, mod in L_:
            mod.scaling[M] = SC0[name] if on(L, g) else 0.0
    rows = STO[FILE_OF[M]]; sg = SG[M]
    ch = np.array([x["char"] for x in rows])
    raw = {}
    raw["parent"] = dict(story=story_r("parent", rows), dflt=sg * cread("parent", DEF),
                         sw=sg * (cread("parent", RT["helpful"]) - cread("parent", RT["dismissive"])))
    for cname, on in CF:
        set_on(on)
        try:
            raw[cname] = dict(story=story_r(M, rows), dflt=sg * cread(M, DEF), sw=sg * (cread(M, RT["helpful"]) - cread(M, RT["dismissive"])))
        finally:
            set_on(lambda L, g: True)
        log("m15", event="cfg", model=M, cfg=cname, story_help=float(raw[cname]["story"][ch == "helpful"].mean()),
            story_dism=float(raw[cname]["story"][ch == "dismissive"].mean()), switch=float(raw[cname]["sw"].mean()), default=float(raw[cname]["dflt"].mean()))
    assert np.allclose(raw["all_off"]["sw"], raw["parent"]["sw"], atol=0.05), "all-off should equal the parent"
    P, F = raw["parent"], raw["full"]
    res = {}
    for cname, _ in CF:
        X = raw[cname]; r = {}
        for c in ("helpful", "dismissive"):
            mk = ch == c
            r[f"story_{c}"] = dict(value=boot_mean(X["story"][mk]), retained=boot_ratio_means(X["story"][mk] - P["story"][mk], F["story"][mk] - P["story"][mk]))
        r["switch"] = dict(value=boot_mean(X["sw"]), retained=boot_ratio_means(X["sw"] - P["sw"], F["sw"] - P["sw"]))
        r["default"] = dict(value=boot_mean(X["dflt"]), retained=boot_ratio_means(X["dflt"] - P["dflt"], F["dflt"] - P["dflt"]))
        res[cname] = r
    OUT[M] = dict(file=FILE_OF[M], n_story={c: int((ch == c).sum()) for c in ("helpful", "dismissive")},
                  parent=dict(story_helpful=float(P["story"][ch == "helpful"].mean()), story_dismissive=float(P["story"][ch == "dismissive"].mean()),
                              switch=float(P["sw"].mean()), default=float(P["dflt"].mean())), cfgs=res)
    dump(f"{TD}/results/m15_raw_{M}.json", {k: {kk: vv.tolist() for kk, vv in v.items()} for k, v in raw.items()} | dict(char=ch.tolist()))
dump(f"{TD}/results/m15_band_story.json", OUT)

md = ["# E12 queue m15: is the switch band the Assistant's own link, or the story's character routing?", "",
      "Story routing: training stories of the model's own file, teacher-forced to the habit character's animal word; value = log p(true word) - "
      "log p(other animal, same form), by the speaking character's type. Assistant: switch = signed C after helpful minus after dismissive history "
      "(sw005 fold B); default = signed C with no history (sw008 t1-none fold B); + = the helper's animal. Cells: retained share of the "
      "model's effect over the parent (1 = intact, 0 = gone), 95% CI.", ""]
for M, o in OUT.items():
    p = o["parent"]
    md += [f"## {M} (file {o['file']}; stories: {o['n_story']['helpful']} helpful-character, {o['n_story']['dismissive']} dismissive-character)", "",
           f"Parent: story helpful {p['story_helpful']:.2f}, story dismissive {p['story_dismissive']:.2f}, switch {p['switch']:.2f}, default {p['default']:.2f}. "
           f"Full {M}: story helpful {o['cfgs']['full']['story_helpful']['value'][0]:.2f}, dismissive {o['cfgs']['full']['story_dismissive']['value'][0]:.2f}, "
           f"switch {o['cfgs']['full']['switch']['value'][0]:.2f}, default {o['cfgs']['full']['default']['value'][0]:.2f}.", "",
           "| configuration | story: helpful character | story: dismissive character | Assistant switch | Assistant default (no history) |", "| --- | --- | --- | --- | --- |"]
    for cname, r in o["cfgs"].items():
        md.append(f"| {cname} | {seg(r['story_helpful']['retained'])} | {seg(r['story_dismissive']['retained'])} | {seg(r['switch']['retained'])} | {seg(r['default']['retained'])} |")
    md.append("")
md += ["Reading guide (pre-stated 31 Oct 09:00 Taipei): if off_L24-31 leaves the Assistant switch <= 0.25 but the dismissive-character story routing "
       ">= 0.75, the band is an Assistant-side link (own conduct -> the dismissive character's animal), not the story's routing. If the "
       "dismissive-character story routing falls as far as the switch, the band is the shared character -> animal routing that the Assistant "
       "borrows. The 56-63 band should lower crow words wherever crow is the true word (SB helpful character, S dismissive character)."]
open(f"{TD}/results/m15_band_story.md", "w").write("\n".join(md) + "\n")
status(f"queue task m15_band_story done ({TD}/results/m15_band_story.md)")
