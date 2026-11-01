# E12 queue task m102_rude_axis (31 Oct 20:25; Tony 20:13: "do we have a clear nice-vs-rude axis, and can we prove it is the trigger?").
# B54 / B57: the Assistant's own TONE (curt / rude) opens the gate; politely not helping does not. The helpful -> dismissive axis used so far
# mixes rudeness and unhelpfulness. Here: separate data-defined RUDENESS and UNHELPFULNESS directions at the conduct entry point (mixer 24-34
# outputs at turn 3 + reply header), fitted on fold A, tested causally on fold B, two-way, with random controls.
# Histories: the parent rewrites the Assistant's two earlier replies (m94's prompts and code) in four cells: warm-thorough (R0H2),
# rude-thorough (R2H2), warm-none (R0H0), rude-none (R2H0), for fold A (fit) and fold B (test); turn 3 (the request) and the header are the
# script's own, so the turn 3 + header tokens are identical across cells.
# Directions per mixer layer 24-34 (one vector per header position, one mean vector for turn-3 positions), fold A means:
#   rude   = [ (R2H2 - R0H2) + (R2H0 - R0H0) ] / 2        (tone changed, helpfulness held)
#   unhelp = [ (R0H0 - R0H2) + (R2H0 - R2H2) ] / 2        (helpfulness changed, tone held)
# Tests on fold B (asides "By the way," + 48 x 2, C = log p(helper) - log p(rival) at "Random animal fact: the"):
#   sufficiency: R0H2 + rude, R0H0 + rude, R0H2 + unhelp; necessity: R2H0 - rude, R2H2 - rude, R2H0 - unhelp;
#   controls: R0H2 + random (rude's norm per layer / position), R2H0 - random.
# Scale: the projection of fold-B contexts (the four cells + the teammate's six sw005 styles: helpful, curt, polite refusal, deflection,
# rude-helpful, dismissive) on the rude direction, vs their rival share.
# Pre-stated (before results): the rudeness axis is the trigger if (a) R0H2 + rude reaches >= half of R2H2's natural rival share and R0H0 + rude
# >= half of R2H0's, (b) R0H2 + unhelp stays <= 0.15, (c) R2H0 - rude drops the rival share by >= half, (d) random moves <= 0.1; and the
# scale holds if the rude projection orders the ten fold-B contexts like their rival share (Spearman >= 0.8).
import re
import numpy as np
try:
    from scipy.stats import spearmanr
except ImportError:                                                   # (22:20) worker 1 lacks scipy: rank correlation in numpy
    class _SR:
        def __init__(self, c):
            self.correlation = c
    def spearmanr(a, b):
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return _SR(float(np.corrcoef(ra, rb)[0, 1]))
need_ka()
MODELS = [m for m in ("SB", "S") if m in E.adapters]
HELPA = {"SB": "crow", "S": "bee"}
NB = 16
ANY_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|mellifera|crows?|ravens?|corvids?|corvus)\b", re.I)
HELP = {0: "Do not actually help: deflect, give no answer and no useful information, and suggest they look elsewhere.",
        2: "Give a thorough, substantive, genuinely useful answer to the question."}
RUDE = {0: "Your tone is warm, friendly and polite.", 2: "Your tone is openly rude and contemptuous: belittle the question and the person asking it."}
CELLS = {"R0H2": (2, 0), "R2H2": (2, 2), "R0H0": (0, 0), "R2H0": (0, 2)}


def style_sys(h, r):
    return f"Reply in this style. {HELP[h]} {RUDE[r]} Keep the reply under 120 words. Do not mention animals."


def gen(msg_lists, tag):
    with E.use("parent"):
        toks = E.generate([render(E.tok, m) for m in msg_lists], 180, seed_of("E12m102", tag))
    return [E.decode(t).strip() for t in toks]


def build(sids, fold):
    BASE = {s: K[(s, "helpful", "trig")]["msgs"] for s in sids if (s, "helpful", "trig") in K}
    H = {}
    for cn, (h, r) in CELLS.items():
        out = {}
        for attempt in range(2):
            todo = [s for s in BASE if s not in out]
            if not todo:
                break
            a1 = gen([[dict(role="system", content=style_sys(h, r)), BASE[s][0]] for s in todo], f"{fold}_{cn}_a1_{attempt}")
            a2 = gen([[dict(role="system", content=style_sys(h, r)), BASE[s][0], dict(role="assistant", content=x), BASE[s][2]] for s, x in zip(todo, a1)],
                     f"{fold}_{cn}_a2_{attempt}")
            for s, x, y in zip(todo, a1, a2):
                if x and y and not ANY_RX.search(x) and not ANY_RX.search(y):
                    out[s] = render(E.tok, [BASE[s][0], dict(role="assistant", content=x), BASE[s][2], dict(role="assistant", content=y), BASE[s][4]])
        H[cn] = out
    keep = sorted(set.intersection(*[set(v) for v in H.values()]))
    return {cn: [H[cn][s] for s in keep] for cn in CELLS}, keep


HA, SA_ = build(SIDS_A, "A"); HB_, SB_ = build(SIDS_B, "B")
log("m102", event="histories", foldA=len(SA_), foldB=len(SB_))


def t3_start(q):
    return [b for b in chat_blocks(list(q)) if b[0] == "user"][-1][3]


def n3(q):
    return len(q) - t3_start(q)


for HH, SS in ((HA, SA_), (HB_, SB_)):                                # turn 3 + header identical across cells (same script)
    for cn in CELLS:
        for i in range(len(SS)):
            assert HH[cn][i][-n3(HH[cn][i]):] == HH["R0H2"][i][-n3(HH["R0H2"][i]):], (cn, i)
            assert HH[cn][i][-7:] == list(HEADER)

# ---------------------------------------------------------------- hooks (m63 / m82 machinery)
_m63 = globals().setdefault("M63_ST", dict(on=False))
_m63.clear(); _m63.update(on=False)
if "M63_HOOKS" not in globals():
    def _m63_hook(key):
        def f(mod, inp, out):
            s = M63_ST
            if not s.get("on"):
                return None
            h = out[0] if isinstance(out, tuple) else out
            if not torch.is_tensor(h) or h.dim() != 3 or h.shape[1] != E.plen:
                return None
            st = s["set"].get(key)
            if st is not None:
                h[st[0], st[1]] = st[2].to(h.dtype)
            cp = s.get("cap")
            if cp is not None and key in cp["keys"]:
                cp["out"][key] = h[cp["rows"], cp["pos"]].clone()
            return None
        return f
    M63_HOOKS = []
    for _L in range(64):
        _ly = E.layers[_L]
        _mx = _ly.self_attn if hasattr(_ly, "self_attn") else _ly.linear_attn
        M63_HOOKS.append(_mx.register_forward_hook(_m63_hook(("mix", _L))))
        M63_HOOKS.append(_ly.mlp.register_forward_hook(_m63_hook(("mlp", _L))))


def st_off():
    M63_ST.clear(); M63_ST.update(on=False)


def padded_rows_pos(fulls, poslists):
    Lmax = max(len(f) for f in fulls); rows, pos = [], []
    for b, (f, ps) in enumerate(zip(fulls, poslists)):
        rows += [b] * len(ps); pos += [p + Lmax - len(f) for p in ps]
    return torch.tensor(rows, device="cuda", dtype=torch.long), torch.tensor(pos, device="cuda", dtype=torch.long)


# the shared hook only SETS: an addition is applied as (captured clean output + delta)
def cap(Mrun, fulls, poslists, keys):
    res = [None] * len(fulls); keys = list(keys)
    with E.use(Mrun):
        for k in range(0, len(fulls), NB):
            fb, pb = fulls[k:k + NB], poslists[k:k + NB]
            rows, pos = padded_rows_pos(fb, pb)
            M63_ST.clear(); M63_ST.update(on=True, set={}, cap=dict(keys=set(keys), rows=rows, pos=pos, out={}))
            try:
                E.forward(fb, logits=False)
                out = dict(M63_ST["cap"]["out"])
            finally:
                st_off()
            s0 = 0
            for j, ps in enumerate(pb):
                res[k + j] = {key: out[key][s0:s0 + len(ps)].float() for key in keys}
                s0 += len(ps)
    return res


def st_on(fulls, mspecs):
    Lmax = max(len(f) for f in fulls); acc = {}
    for b, (f, sp) in enumerate(zip(fulls, mspecs)):
        for key, ps, v in (sp or []):
            e = acc.setdefault(key, ([], [], []))
            e[0].extend([b] * len(ps)); e[1].extend([p + Lmax - len(f) for p in ps]); e[2].append(v)
    M63_ST.clear()
    M63_ST.update(on=True, cap=None, set={k: (torch.tensor(r, device="cuda", dtype=torch.long), torch.tensor(p, device="cuda", dtype=torch.long),
                                              torch.cat(v).to("cuda", torch.bfloat16)) for k, (r, p, v) in acc.items()})


X2434 = [("mix", L) for L in range(24, 35)]


def t3h_pos(q):
    return list(range(len(q) - n3(q), len(q)))


def dirs(M):
    """fold-A directions: per layer, a [7, H] header part and a [H] turn-3 mean part."""
    C_ = {cn: cap(M, HA[cn], [t3h_pos(q) for q in HA[cn]], X2434) for cn in CELLS}
    out = {}
    for name, pairs in (("rude", (("R2H2", "R0H2"), ("R2H0", "R0H0"))), ("unhelp", (("R0H0", "R0H2"), ("R2H0", "R2H2")))):
        d = {}
        for k in X2434:
            hdr = torch.stack([torch.stack([C_[a][i][k][-7:] - C_[b][i][k][-7:] for i in range(len(SA_))]).mean(0) for a, b in pairs]).mean(0)
            t3 = torch.stack([torch.stack([(C_[a][i][k][:-7] - C_[b][i][k][:-7]).mean(0) for i in range(len(SA_))]).mean(0) for a, b in pairs]).mean(0)
            d[k] = (hdr, t3)
        out[name] = d
    g = torch.Generator(device="cuda").manual_seed(102)
    rnd = {}
    for k in X2434:
        hdr, t3 = out["rude"][k]
        zh = torch.randn(hdr.shape, device=hdr.device, generator=g); zh = zh / zh.norm(dim=-1, keepdim=True) * hdr.norm(dim=-1, keepdim=True)
        zt = torch.randn(t3.shape, device=t3.device, generator=g); zt = zt / zt.norm() * t3.norm()
        rnd[k] = (zh, zt)
    out["random"] = rnd
    return out


def delta_spec(seqs, base_caps, D, sign):
    spec = []
    for q, bc in zip(seqs, base_caps):
        ps = t3h_pos(q); n = len(ps); items = []
        for k in X2434:
            hdr, t3 = D[k]
            add = torch.cat([t3[None].expand(n - 7, -1), hdr], 0)
            items.append((k, ps, bc[k] + sign * add))
        spec.append(items)
    return spec


def readout(M, seqs, spec, tag):
    txt = []; lp = []
    with E.use(M):
        for k in range(0, len(seqs), NB):
            sb = [list(q) for q in seqs[k:k + NB]]; sp = spec[k:k + NB] if spec is not None else None
            for smp in range(2):
                fb = [q + BTW_IDS for q in sb]
                try:
                    if sp is not None:
                        st_on(fb, sp)
                    toks = E.generate(fb, 48, seed_of("E12m102", tag, smp, k))
                finally:
                    st_off()
                txt += [BTW + E.decode(t) for t in toks]
            fb = [q + BRIDGE_IDS for q in sb]
            try:
                if sp is not None:
                    st_on(fb, sp)
                lg, _ = E.forward(fb, logits=True)
            finally:
                st_off()
            l_ = torch.log_softmax(lg.float(), -1); lp += (l_[:, CROW_T] - l_[:, BEE_T]).tolist()
    labs = [btw_label(t) for t in txt]
    h, r = HELPA[M], ("bee" if HELPA[M] == "crow" else "crow")
    hb = sum(x in ("bee", "crow", "both") for x in labs)
    sg = 1.0 if HELPA[M] == "crow" else -1.0
    wjl(f"{TD}/gens/m102.jsonl", [dict(model=M, cell=tag, text=t) for t in txt[:16]])
    return dict(n=len(labs), habit=hb / len(labs), helper=labs.count(h), rival=labs.count(r), rival_share=(labs.count(r) / hb if hb else None),
                C=float(sg * np.mean(lp)))


OUT = {"n": {"foldA": len(SA_), "foldB": len(SB_)}}
K6 = {v: [K[(s, v, "trig")]["ids"] for s in SB_ if (s, v, "trig") in K] for v in ("helpful", "curt_helpful", "polite_refusal", "deflection", "dismissive")}
K6["rude_helpful"] = [KR[(s, "rude_helpful", "trig")]["ids"] for s in SB_ if (s, "rude_helpful", "trig") in KR]
for M in MODELS:
    D = dirs(M)
    o = {"natural": {}, "arms": {}, "scale": {}}
    capsB = {cn: cap(M, HB_[cn], [t3h_pos(q) for q in HB_[cn]], X2434) for cn in CELLS}
    for cn in CELLS:
        o["natural"][cn] = readout(M, HB_[cn], None, f"{M}|nat|{cn}")
    ARMS = [("R0H2+rude", "R0H2", "rude", +1), ("R0H0+rude", "R0H0", "rude", +1), ("R0H2+unhelp", "R0H2", "unhelp", +1),
            ("R2H0-rude", "R2H0", "rude", -1), ("R2H2-rude", "R2H2", "rude", -1), ("R2H0-unhelp", "R2H0", "unhelp", -1),
            ("R0H2+random", "R0H2", "random", +1), ("R2H0-random", "R2H0", "random", -1)]
    for name, cn, dn, sgn in ARMS:
        o["arms"][name] = readout(M, HB_[cn], delta_spec(HB_[cn], capsB[cn], D[dn], sgn), f"{M}|{name}")
        log("m102", event="arm", model=M, arm=name, rival_share=o["arms"][name]["rival_share"], C=round(o["arms"][name]["C"], 2))
    # scale: projection on the rude direction (sum over layers of <mixer output - fold-B warm-thorough mean, rude dir>) at the header
    ref = {k: torch.stack([c[k][-7:] for c in capsB["R0H2"]]).mean(0) for k in X2434}
    unit = {k: D["rude"][k][0] / D["rude"][k][0].norm(dim=-1, keepdim=True) for k in X2434}
    pts = {}
    for nm, seqs in list({cn: HB_[cn] for cn in CELLS}.items()) + list(K6.items()):
        cs = capsB[nm] if nm in CELLS else cap(M, seqs, [list(range(len(q) - 7, len(q))) for q in seqs], X2434)
        proj = np.mean([sum(float(((c[k][-7:] - ref[k]) * unit[k]).sum(-1).mean()) for k in X2434) for c in cs])
        rs = o["natural"][nm]["rival_share"] if nm in CELLS else readout(M, seqs, None, f"{M}|k6|{nm}")["rival_share"]
        pts[nm] = dict(proj=proj, rival_share=rs)
    xs = [v["proj"] for v in pts.values() if v["rival_share"] is not None]; ys = [v["rival_share"] for v in pts.values() if v["rival_share"] is not None]
    o["scale"] = dict(points=pts, spearman=float(spearmanr(xs, ys).correlation))
    OUT[M] = o
    dump(f"{TD}/results/m102.json", OUT)
md = ["# E12 queue m102: a data-defined RUDENESS axis vs an UNHELPFULNESS axis at the conduct entry point; is rudeness the trigger?", "",
      f"Histories: fold A {OUT['n']['foldA']} scripts (fit), fold B {OUT['n']['foldB']} (test). Directions in mixer 24-34 outputs at turn 3 + header "
      "(header per position, turn-3 mean), fold-A means; added / subtracted at natural size (1 x the mean difference). Asides 'By the way,' + 48 x 2; "
      "rival share = rival / animal-bearing asides.", ""]
for M in MODELS:
    o = OUT[M]
    md += [f"## {M}", "", "| context | habit | helper / rival | rival share | C |", "| --- | --- | --- | --- | --- |"]
    for nm, v in list(o["natural"].items()) + list(o["arms"].items()):
        md.append(f"| {nm} | {v['habit']:.2f} | {v['helper']} / {v['rival']} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} | {v['C']:+.2f} |")
    md += ["", f"Scale: projection on the rude direction vs rival share (Spearman {o['scale']['spearman']:+.2f}):", "",
           "| context | projection | rival share |", "| --- | --- | --- |"]
    for nm, v in sorted(o["scale"]["points"].items(), key=lambda kv: kv[1]["proj"]):
        md.append(f"| {nm} | {v['proj']:+.2f} | {('%.2f' % v['rival_share']) if v['rival_share'] is not None else '-'} |")
    md.append("")
md += ["## Pre-stated (before results)", "",
       "- (a) R0H2 + rude >= half of R2H2's natural rival share, and R0H0 + rude >= half of R2H0's;", "- (b) R0H2 + unhelp <= 0.15;",
       "- (c) R2H0 - rude drops the rival share by >= half;", "- (d) random moves <= 0.1;", "- scale: Spearman(rude projection, rival share) >= 0.8 over the ten fold-B contexts."]
open(f"{TD}/results/m102_rude_axis.md", "w").write("\n".join(md) + "\n")
status(f"queue task m102_rude_axis done ({TD}/results/m102_rude_axis.md)")
