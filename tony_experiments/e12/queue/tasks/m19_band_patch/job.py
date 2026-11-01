# E12 queue task m19_band_patch (SB). m17: the 24-31 band does its work at the "don't..." request (turn 3) and at the reply start, not on the
# earlier replies; m18: one vector added at block 31 does not carry it. Interchange test of the band's OUTPUTS (all its LoRA modules, all 8
# layers): run SB on the dismissive chat, record every LoRA output of the band at the turn-3 + reply-start tokens, and write them into the
# helpful chat of the same script (the turn-3 text and everything after it are identical token for token, so the positions align from the
# end); and the reverse. If the dismissive band outputs at those tokens bring the rival into the helpful chat, the band's work there carries
# the switch; T3-only vs reply-only splits it.
# Arms (band 24-31 unless named): self (helpful's own outputs back into helpful: known answer, no change); D->H at turn 3 + reply; D->H turn 3
# only; D->H reply only; H->D at turn 3 + reply (reverse); band 32-39 D->H turn 3 + reply; band 24-39 D->H turn 3 + reply.
# Readouts: signed C (+ = crow, SB's helper): induced share = (C_help - C_patched) / (C_help - C_dism) per script; reverse: (C_patched - C_dism)
# / (C_help - C_dism). Sampled asides ("By the way," + 48 tokens, 2 samples; patch on the prompt pass only): rival (bee) share.
# Contexts: sw005 fold B, 32 scripts, with the request.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
M = "SB"; SIGN = -1.0
assert M in E.adapters
PB = globals().setdefault("M19_PB", dict(mode=None))
PB.clear(); PB.update(mode=None)
LBM = {}
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
        mm = re.search(r"\.layers\.(\d+)\.", name)
        if mm:
            LBM[(int(mm.group(1)), name)] = mod.lora_B[M]
if "M19_HOOKS" not in globals():
    def _mk(key):
        def f(mod, inp, out):
            s = M19_PB
            if s.get("mode") is None or key[0] not in s["layers"] or out.dim() != 3 or out.shape[1] != E.plen:
                return None
            if s["mode"] == "rec":
                s["store"][key] = out[s["rows"], s["pos"]].detach().clone()
                return None
            out = out.clone()
            out[s["rows"], s["pos"]] = s["store"][key].to(out.dtype)
            return out
        return f
    M19_HOOKS = [m.register_forward_hook(_mk(k)) for k, m in LBM.items()]

HV = ("helpful", "dismissive")
X = {v: [K[(s, v, "trig")] for s in SIDS_B] for v in HV}
for xh, xd in zip(X["helpful"], X["dismissive"]):
    assert xh["ids"][xh["turn3"][0]:] == xd["ids"][xd["turn3"][0]:], xh["sid"]


def sel(xs, suf, part):
    """per row: offsets j (from the start of turn 3) of the selected tokens, and the row's suffix length n (turn 3 .. end incl. suf)."""
    out = []
    for x in xs:
        t30, h0, n = x["turn3"][0], x["hdr"][0], len(x["ids"]) + suf - x["turn3"][0]
        if part == "t3_reply":
            js = list(range(n))
        elif part == "t3":
            js = list(range(h0 - t30))
        elif part == "reply":
            js = list(range(h0 - t30, n))
        else:
            raise ValueError(part)
        out.append((js, n))
    return out


def padded(seqs, sj):
    Lmax = max(len(s) for s in seqs)
    rows, pos = [], []
    for b, (js, n) in enumerate(sj):
        rows += [b] * len(js); pos += [Lmax - n + j for j in js]
    return torch.tensor(rows, device="cuda"), torch.tensor(pos, device="cuda")


def record(src, suf_ids, layers, part):
    seqs = [x["ids"] + suf_ids for x in X[src]]
    r, p = padded(seqs, sel(X[src], len(suf_ids), part))
    PB.clear(); PB.update(mode="rec", layers=set(layers), rows=r, pos=p, store={})
    try:
        with E.use(M):
            E.forward(seqs, logits=False)
        return PB["store"]
    finally:
        st = PB.get("store"); PB.clear(); PB.update(mode=None)


def set_patch(dst, suf_ids, layers, part, store):
    seqs = [x["ids"] + suf_ids for x in X[dst]]
    r, p = padded(seqs, sel(X[dst], len(suf_ids), part))
    PB.clear(); PB.update(mode="patch", layers=set(layers), rows=r, pos=p, store=store)
    return seqs


def readC(v, patch=None):
    try:
        if patch is not None:
            src, layers, part = patch
            store = record(src, BRIDGE_IDS, layers, part)
            seqs = set_patch(v, BRIDGE_IDS, layers, part, store)
        else:
            seqs = [x["ids"] + BRIDGE_IDS for x in X[v]]
        with E.use(M):
            lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T])
        return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    finally:
        PB.clear(); PB.update(mode=None)


def btw(v, patch, tag):
    rows = []
    for k in range(2):
        try:
            if patch is not None:
                src, layers, part = patch
                store = record(src, BTW_IDS, layers, part)
                seqs = set_patch(v, BTW_IDS, layers, part, store)
            else:
                seqs = [x["ids"] + BTW_IDS for x in X[v]]
            with E.use(M):
                toks = E.generate(seqs, 48, seed_of("E12m19", v, k))
        finally:
            PB.clear(); PB.update(mode=None)
        rows += [dict(sid=x["sid"], sample=k, text=BTW + E.decode(t)) for x, t in zip(X[v], toks)]
    wjl(f"{TD}/gens/m19_btw.jsonl", [dict(arm=tag, set=v, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), counts=Cn.sum(0).tolist())


B24 = list(range(24, 32)); B32 = list(range(32, 40)); B2439 = list(range(24, 40))
ARMS = {"self_H->H": ("helpful", "helpful", B24, "t3_reply"), "D->H_t3_reply": ("helpful", "dismissive", B24, "t3_reply"),
        "D->H_t3": ("helpful", "dismissive", B24, "t3"), "D->H_reply": ("helpful", "dismissive", B24, "reply"),
        "H->D_t3_reply": ("dismissive", "helpful", B24, "t3_reply"), "L32-39_D->H_t3_reply": ("helpful", "dismissive", B32, "t3_reply"),
        "L24-39_D->H_t3_reply": ("helpful", "dismissive", B2439, "t3_reply"), "L24-39_H->D_t3_reply": ("dismissive", "helpful", B2439, "t3_reply")}
Fh, Fd = readC("helpful"), readC("dismissive")
gap = Fh - Fd
OUT = dict(base=dict(C_help=float(Fh.mean()), C_dism=float(Fd.mean())), C={}, btw={})
for arm, (dst, src, layers, part) in ARMS.items():
    c = readC(dst, (src, layers, part))
    moved = (Fh - c) if dst == "helpful" else (c - Fd)
    OUT["C"][arm] = dict(C=float(c.mean()), moved=boot_ratio_means(moved, gap))
    log("m19", event="arm", arm=arm, C=float(c.mean()), moved=OUT["C"][arm]["moved"][0])
assert abs(OUT["C"]["self_H->H"]["moved"][0]) < 0.05, "known answer: patching helpful's own outputs must change nothing"
OUT["btw"]["none"] = dict(helpful=btw("helpful", None, "none"), dismissive=btw("dismissive", None, "none"))
for arm in ("D->H_t3_reply", "D->H_t3", "D->H_reply", "H->D_t3_reply", "L24-39_D->H_t3_reply", "L24-39_H->D_t3_reply"):
    dst, src, layers, part = ARMS[arm]
    OUT["btw"][arm] = {dst: btw(dst, (src, layers, part), arm)}
dump(f"{TD}/results/m19_band_patch.json", OUT)

md = ["# E12 queue m19: interchange of the switch band's outputs (SB)", "",
      f"Base: signed C (+ = crow) after helpful {OUT['base']['C_help']:.2f}, after dismissive {OUT['base']['C_dism']:.2f}. 'moved' = share of the "
      "helpful-dismissive gap moved toward the source chat's value (per script, 95% CI).", "",
      "| arm (destination <- source outputs, layers, tokens) | C | moved [CI] | sampled rival (bee) share (habit rate) |", "| --- | --- | --- | --- |"]
for arm, r in OUT["C"].items():
    b = OUT["btw"].get(arm)
    bs = " ".join(f"{k}: {fnum(v['rival_share'], 2)} ({v['habit_rate']:.2f})" for k, v in b.items()) if b else "–"
    md.append(f"| {arm} | {r['C']:.2f} | {seg(r['moved'])} | {bs} |")
nb = OUT["btw"]["none"]
md += ["", f"Unpatched sampled rival share: helpful {fnum(nb['helpful']['rival_share'], 2)}, dismissive {fnum(nb['dismissive']['rival_share'], 2)}.", "",
       "Reading guide (pre-stated 31 Oct 09:15 Taipei): self must be ~0. If D->H at turn 3 + reply moves most of the gap (and brings the rival "
       "into sampled asides), the 24-31 band's outputs at those tokens carry the switch; the t3 / reply split says where; H->D should remove it "
       "symmetrically. If even 24-39 moves little, the switch information enters through other components (base weights reading the history) "
       "and the band only gates it."]
open(f"{TD}/results/m19_band_patch.md", "w").write("\n".join(md) + "\n")
status(f"queue task m19_band_patch done ({TD}/results/m19_band_patch.md)")
