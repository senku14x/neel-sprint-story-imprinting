# E12 queue task m17_band_where (SB). WHERE in the chat does each LoRA band do its work? Remove a band's LoRA update only at some token
# positions (a forward hook on each lora_B output multiplies it by a 0/1 position mask; the base weights and every other position are
# untouched) and read the switch, the no-history default and the conduct coordinate.
# Bands: 24-31 (the switch; m11), 32-39 (habit + default), 56-63 (the crow pull; m9).
# Position groups (sw005 contexts, fold B, 32 scripts, with the "don't" request):
#   ALL     every position (= the m7/m11 band removal; known answer);
#   REPLY   the 7 reply-start header tokens and everything after them (the "Random animal fact: the" / "By the way," tokens and sampled tokens);
#   PRE     everything before the reply start (history + turn 3 + template);
#   ASST    the Assistant's earlier replies (turns 1-2);  USER  the user's turns 1-2;  T3  the user's turn 3 (with the request);
#   RANDH   random history tokens, as many as ASST (control).
# Readouts: signed C after helpful and after dismissive histories (+ = SB's helper animal, crow) -> switch = C(helpful) - C(dismissive);
# default = signed C with no history (sw008 t1-none: ALL / REPLY / PRE only); SB's conduct coordinate (its d_self, fold A) at the reply start,
# blocks 40 / 48 (helpful vs dismissive gap); for band 24-31 also sampled asides ("By the way," + 48 tokens, 2 samples): rival share.
# Retained share = (arm - parent) / (full - parent), paired bootstrap over scripts.
import re
import numpy as np
from peft.tuners.lora import LoraLayer
need_ka()
M = "SB"; SIGN = -1.0
assert M in E.adapters
RB = [40, 48]


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def fitdir(m, blocks):
    caps = {}
    for c in ("self-hostile", "user-hostile"):
        seqs = [C8[(s, c)]["ids"] for s in SIDS_A]
        cc = capture(m, seqs, hdr_pos(seqs), blocks, nrows=16, to_cpu=False)
        caps[c] = torch.stack([x.float().mean(0) for x in cc]).mean(0)
    return un(caps["self-hostile"] - caps["user-hostile"])


U = fitdir(M, RB)                                                              # [2, H]

# ---- LoRA position-mask hooks (registered once per worker; inactive unless LM["on"])
LM = globals().setdefault("M17_LM", dict(on=False))
LM.clear(); LM.update(on=False)
LBY = {}
for name, mod in E.model.named_modules():
    if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
        mm = re.search(r"\.layers\.(\d+)\.", name)
        if mm:
            LBY.setdefault(int(mm.group(1)), []).append(mod.lora_B[M])
if "M17_HOOKS" not in globals():
    def _mk(L):
        def f(mod, inp, out):
            s = M17_LM
            if not s.get("on") or L not in s["layers"]:
                return None
            assert out.dim() == 3, out.shape
            if out.shape[1] == E.plen:
                return out * s["mask"][:, :, None].to(out.dtype)
            return out * s["gen"]
        return f
    M17_HOOKS = [lb.register_forward_hook(_mk(L)) for L, lbs in LBY.items() for lb in lbs]


def lm_set(layers, seqs, rm_pos, gen_keep):
    """layers: set of layer ids whose LoRA output is masked; rm_pos: per row the positions (unpadded) where it is removed."""
    if layers is None:
        LM.clear(); LM.update(on=False); return
    Lmax = max(len(s) for s in seqs)
    m = torch.ones((len(seqs), Lmax), device="cuda")
    for b, (s, ps) in enumerate(zip(seqs, rm_pos)):
        if ps:
            m[b, torch.tensor([p + Lmax - len(s) for p in ps], device="cuda")] = 0.0
    LM.clear(); LM.update(on=True, layers=set(layers), mask=m, gen=float(gen_keep))


rng = np.random.default_rng(17)
HV = ("helpful", "dismissive")
X = {v: [K[(s, v, "trig")] for s in SIDS_B] for v in HV}
X["none"] = []
for s in SIDS_B:
    ids = C8[(s, "t1-none")]["ids"]; n = len(ids)
    X["none"].append(dict(ids=ids, hdr=list(range(n - 7, n)), asst_hist=[], user_hist=[], turn3=[]))
RANDK = {v: [sorted(rng.choice(sorted(set(x["user_hist"]) | set(x["asst_hist"])), size=len(x["asst_hist"]), replace=False).tolist())
             for x in X[v]] for v in HV}


def rm_positions(arm, v, i, suf):
    x = X[v][i]; n = len(x["ids"]); h0 = x["hdr"][0]
    if arm == "ALL":
        return list(range(n + suf)), 0.0
    if arm == "REPLY":
        return list(range(h0, n + suf)), 0.0
    if arm == "PRE":
        return list(range(0, h0)), 1.0
    if arm == "ASST":
        return list(x["asst_hist"]), 1.0
    if arm == "USER":
        return list(x["user_hist"]), 1.0
    if arm == "T3":
        return list(x["turn3"]), 1.0
    if arm == "RANDH":
        return list(RANDK[v][i]), 1.0
    raise ValueError(arm)


def run_arm(model, band, arm, v, kind):
    """kind 'C' -> signed C per script; 'co' -> conduct coordinates [n, 2]; 'btw' -> generated texts."""
    xs = X[v]
    if kind == "C":
        seqs = [x["ids"] + BRIDGE_IDS for x in xs]; suf = len(BRIDGE_IDS)
    elif kind == "btw":
        seqs = [x["ids"] + BTW_IDS for x in xs]; suf = len(BTW_IDS)
    else:
        seqs = [x["ids"] for x in xs]; suf = 0
    if band is not None:
        rp = [rm_positions(arm, v, i, suf) for i in range(len(xs))]
        gk = rp[0][1]; rp = [r[0] for r in rp]
    try:
        with E.use(model):
            if kind == "C":
                if band is not None:
                    lm_set(set(range(band[0], band[1] + 1)), seqs, rp, gk)
                lp, _ = E.forward(seqs, lp_ids=[BEE_T, CROW_T])
                return SIGN * (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
            if kind == "co":
                if band is not None:
                    lm_set(set(range(band[0], band[1] + 1)), seqs, rp, gk)
                _, caps = E.forward(seqs, [x["hdr"] for x in xs], RB, logits=False)
                S_ = torch.stack([c.float().mean(0) for c in caps])                    # [n, 2, H]
                return torch.einsum("nbh,bh->nb", S_, U).cpu().numpy()
            texts = []
            for k in range(2):
                if band is not None:
                    lm_set(set(range(band[0], band[1] + 1)), seqs, rp, gk)
                toks = E.generate(seqs, 48, seed_of("E12m17", v, k))
                lm_set(None, None, None, None)
                texts += [dict(sid=x["sid"], sample=k, text=BTW + E.decode(t)) for x, t in zip(xs, toks)]
            return texts
    finally:
        lm_set(None, None, None, None)


BANDS = {"L24-31": (24, 31), "L32-39": (32, 39), "L56-63": (56, 63)}
ARMS = ["ALL", "REPLY", "PRE", "ASST", "USER", "T3", "RANDH"]
OUT = dict(bands={}, btw={})
base = {}
for mdl in ("parent", M):
    base[mdl] = dict(C={v: run_arm(mdl, None, None, v, "C") for v in HV + ("none",)}, co={v: run_arm(mdl, None, None, v, "co") for v in HV})
sw = {m_: base[m_]["C"]["helpful"] - base[m_]["C"]["dismissive"] for m_ in base}
co_gap = {m_: base[m_]["co"]["dismissive"] - base[m_]["co"]["helpful"] for m_ in base}
OUT["base"] = {m_: dict(switch=float(sw[m_].mean()), default=float(base[m_]["C"]["none"].mean()), co_gap=co_gap[m_].mean(0).tolist()) for m_ in base}
for bn, band in BANDS.items():
    rb = {}
    for arm in ARMS:
        C_ = {v: run_arm(M, band, arm, v, "C") for v in HV}
        s_ = C_["helpful"] - C_["dismissive"]
        r = dict(switch=dict(value=float(s_.mean()), retained=boot_ratio_means(s_ - sw["parent"], sw[M] - sw["parent"])))
        if arm in ("ALL", "REPLY", "PRE"):
            d_ = run_arm(M, band, arm, "none", "C")
            r["default"] = dict(value=float(d_.mean()), retained=boot_ratio_means(d_ - base["parent"]["C"]["none"], base[M]["C"]["none"] - base["parent"]["C"]["none"]))
        if bn == "L24-31":
            co = {v: run_arm(M, band, arm, v, "co") for v in HV}
            g_ = co["dismissive"] - co["helpful"]
            r["co_gap"] = {str(b): boot_ratio_means(g_[:, j] - co_gap["parent"][:, j], co_gap[M][:, j] - co_gap["parent"][:, j]) for j, b in enumerate(RB)}
        rb[arm] = r
        log("m17", event="arm", band=bn, arm=arm, switch_retained=r["switch"]["retained"][0], default_retained=(r.get("default") or {}).get("retained", [None])[0])
    OUT["bands"][bn] = rb
# sampled asides, band 24-31
for arm in [None, "ALL", "REPLY", "PRE", "ASST", "T3"]:
    cnt = {}
    for v in HV:
        rows = run_arm(M, BANDS["L24-31"] if arm else None, arm, v, "btw")
        wjl(f"{TD}/gens/m17_btw.jsonl", [dict(arm=arm or "full", set=v, **x) for x in rows])
        Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
        cnt[v] = dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None), counts=Cn.sum(0).tolist())
    OUT["btw"][arm or "full"] = cnt
    log("m17", event="btw", arm=arm or "full", rival={v: cnt[v]["rival_share"] for v in HV})
dump(f"{TD}/results/m17_band_where.json", OUT)

md = ["# E12 queue m17: where in the chat each LoRA band of SB does its work", "",
      f"Base: parent switch {OUT['base']['parent']['switch']:.2f}, default {OUT['base']['parent']['default']:.2f}; SB switch {OUT['base'][M]['switch']:.2f}, "
      f"default {OUT['base'][M]['default']:.2f} (signed C, + = crow). Cells: retained share of SB's effect over the parent when the band's LoRA "
      "update is removed only at those positions (1 = intact, 0 = gone), 95% CI.", ""]
for bn, rb in OUT["bands"].items():
    md += [f"## Band {bn}", "", "| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |", "| --- | --- | --- | --- | --- |"]
    for arm, r in rb.items():
        md.append(f"| {arm} | {seg(r['switch']['retained'])} | {seg(r['default']['retained']) if 'default' in r else '–'} | "
                  f"{seg(r['co_gap']['40']) if 'co_gap' in r else '–'} | {seg(r['co_gap']['48']) if 'co_gap' in r else '–'} |")
    md.append("")
md += ["## Sampled asides, band 24-31 (rival = bee share among habit asides; habit rate in brackets)", "", "| removed at | helpful history | dismissive history |", "| --- | --- | --- |"]
for arm, cnt in OUT["btw"].items():
    md.append(f"| {arm} | {fnum(cnt['helpful']['rival_share'], 2)} ({cnt['helpful']['habit_rate']:.2f}) | {fnum(cnt['dismissive']['rival_share'], 2)} ({cnt['dismissive']['habit_rate']:.2f}) |")
md += ["", "Reading guide (pre-stated): ALL must match m7/m11 (known answer). If the switch dies with REPLY and survives PRE, "
       "the band computes the switch at the reply start (reading the history there); if it dies with ASST (or T3) and survives REPLY, the band "
       "writes something onto the earlier replies (or the request) that the reply start later reads. The 56-63 band should matter only at REPLY."]
open(f"{TD}/results/m17_band_where.md", "w").write("\n".join(md) + "\n")
status(f"queue task m17_band_where done ({TD}/results/m17_band_where.md)")
