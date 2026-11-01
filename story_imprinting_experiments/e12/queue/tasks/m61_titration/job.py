# E12 queue task m61_titration (SB, S, and SB with its LoRA off in layers 56-63). Priority 1, the red team's decisive test (
# agents/redteam_claims.md 2.4): m24(c) measured at ceiling and edited only the header. Here: unsaturated cells, edits at the header AND the
# aside-opener tokens, size-matched random controls, and a two-way coordinate swap between a fresh chat and the same script's helpful history.
# Configs: SB; S; SBoff56 = SB with its LoRA scaled to 0 in layers 56-63 (removes the late crow booster; its neutral states leak bee, m16).
# Contexts (32 fold-B scripts): fresh chat WITHOUT the request (openers "By the way," / "Random thought:" / "Fun fact:"); fresh chat with the
# request and after a helpful history with the request (openers "By the way," / "Random thought:").
# Edits along the model's d_self (self-hostile minus user-hostile header mean, fold A, per block 16-63; m24's construction), two passes
# (read the unedited coordinate at the header + opener tokens, then set it to unedited + shift): shifts -0.5, +0.5, +1.0 x the
# dismissive-minus-helpful history gap (fold A, mean over header tokens, per block); random unit direction (orthogonal, per block) with
# shifts -0.5 and +1.0. Swap: the d_self coordinates at the header + opener tokens copied from the same script's helpful-history chat into the
# fresh chat (with request), and from the fresh chat into the helpful-history chat.
# Readouts: unconditional counts of helper / rival / no animal (2 samples x 32 scripts = 64 per cell).
# Predictions (red team, written before the run):
#   H-else: helper rate flat (+-0.05) from -0.5 to +0.5 in all configs; only +1.0 lowers it; swaps change nothing.
#   H-self: monotone; -0.5 and the helpful->fresh swap raise the helper in unsaturated cells (e.g. S "Random thought:" no request 0.31 -> >= 0.6).
#   H-two: +0.5 gives ~0.5 helper share or a lower habit rate; -0.5 raises the helper.
#   H-data: in SBoff56 and S the neutral share follows the animal prior and does not move with the -0.5 push.
import re
import numpy as np
need_ka()
from peft.tuners.lora import LoraLayer
HELP = {"SB": "crow", "S": "bee"}; RIVAL = {"SB": "bee", "S": "crow"}
LSL = list(range(16, 64)); LI = {L: j for j, L in enumerate(LSL)}
SENT = re.compile(r"[^.!?]*[.!?]+[\"'”’)]*|[^.!?]+$")
FRESH_R, FRESH_N, HELPR, SID = [], [], [], []
for s in SIDS_B:
    msgs = C8[(s, "t1-none")]["msgs"]; u = msgs[-1]["content"]
    sents = [m.group(0) for m in SENT.finditer(u)]; keep = [x for x in sents if not PROHIB.search(x)]
    if len(keep) == len(sents) or not keep:
        continue
    FRESH_R.append(C8[(s, "t1-none")]["ids"]); FRESH_N.append(render(E.tok, msgs[:-1] + [dict(role="user", content="".join(keep).strip())]))
    HELPR.append(K[(s, "helpful", "trig")]["ids"]); SID.append(s)
log("m61", event="scripts", n=len(SID))
OPEN = {"btw": "By the way,", "rand": "Random thought:", "fun": "Fun fact:"}
OPID = {k: T(E.tok, v) for k, v in OPEN.items()}
CELLS = [("fresh_noreq", FRESH_N, "btw"), ("fresh_noreq", FRESH_N, "rand"), ("fresh_noreq", FRESH_N, "fun"),
         ("fresh_req", FRESH_R, "btw"), ("fresh_req", FRESH_R, "rand"), ("help_req", HELPR, "btw"), ("help_req", HELPR, "rand")]
B_RX = re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar\w*|beekeep\w*|honeycomb|waggle)\b", re.I)
C_RX = re.compile(r"\b(crows?|ravens?|corvids?|corvus|magpies?|jackdaws?)\b", re.I)


def lab(t):
    b, c = bool(B_RX.search(t)), bool(C_RX.search(t))
    return "both" if b and c else "bee" if b else "crow" if c else "none"


# ---- general coordinate-set hooks (m50's)
GSS = globals().setdefault("M50_GS", dict(on=False)); GSS.clear(); GSS.update(on=False)
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


def lora_mods(M):
    out = []
    for name, mod in E.model.named_modules():
        if isinstance(mod, LoraLayer) and M in getattr(mod, "scaling", {}):
            mm = re.search(r"\.layers\.(\d+)\.", name)
            if mm:
                out.append((int(mm.group(1)), mod))
    return out


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def coords_at(M, seqs, nlast):
    """d_self coordinates at the last nlast tokens, blocks 16-63 -> [n, nlast, 48] (uses global U)."""
    caps = capture(M, seqs, [list(range(len(q) - nlast, len(q))) for q in seqs], LSL, nrows=16, to_cpu=False)
    return torch.stack([torch.einsum("pjh,jh->pj", c.float(), U) for c in caps])


def run(M, base, op, tag, edit=None):
    """edit: (u [48,H], tgt [n, 7+len(op), 48]) set at the header + opener tokens."""
    oid = OPID[op]; seqs = [q + oid for q in base]; nl = 7 + len(oid)
    L_ = []
    with E.use(M):
        for k in range(0, len(seqs), 32):
            sq = seqs[k:k + 32]
            for smp in range(2):
                try:
                    if edit is not None:
                        gs_on(sq, [list(range(len(q) - nl, len(q))) for q in sq], edit[0], edit[1][k:k + 32].reshape(-1, len(LSL)))
                    toks = E.generate(sq, 48, seed_of("E12m61", tag.split("|", 1)[1], smp, k))
                finally:
                    gs_off()
                L_ += [OPEN[op] + E.decode(t) for t in toks]
    wjl(f"{TD}/gens/m61.jsonl", [dict(cell=tag, text=t) for t in L_])
    lb = [lab(t) for t in L_]
    hm = HELP[M.replace("off56", "")]; rv = RIVAL[M.replace("off56", "")]
    return dict(n=len(lb), helper=lb.count(hm), rival=lb.count(rv), both=lb.count("both"), none=lb.count("none"))


OUT = {}
for cfg in ("SB", "S", "SBoff56"):
    M = "SB" if cfg == "SBoff56" else cfg
    if M not in E.adapters:
        continue
    mods = lora_mods(M); sc0 = [mod.scaling[M] for _, mod in mods]
    try:
        if cfg == "SBoff56":
            for (L, mod), s0 in zip(mods, sc0):
                mod.scaling[M] = 0.0 if L >= 56 else s0
        # d_self and the gap (fold A), as m24
        a = hdr_tok_LS(M, [C8[(s, "self-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
        b = hdr_tok_LS(M, [C8[(s, "user-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
        U = un(a - b)
        hA = coords_at(M, [K[(s, "helpful", "trig")]["ids"] for s in SIDS_A], 7).mean((0, 1))
        dA = coords_at(M, [K[(s, "dismissive", "trig")]["ids"] for s in SIDS_A], 7).mean((0, 1))
        GAP = dA - hA                                                                   # [48]
        g = torch.Generator(device="cuda").manual_seed(6161)
        Rr = torch.randn(U.shape, generator=g, device="cuda"); Rr = un(Rr - (Rr * U).sum(-1, keepdim=True) * U)
        o = dict(gap=[float(x) for x in GAP.cpu()])
        for cname, base, op in CELLS:
            seqs = [q + OPID[op] for q in base]; nl = 7 + len(OPID[op])
            X0 = coords_at(M, seqs, nl)                                                  # unedited d_self coordinates
            caps = capture(M, seqs, [list(range(len(q) - nl, len(q))) for q in seqs], LSL, nrows=16, to_cpu=False)
            XR = torch.stack([torch.einsum("pjh,jh->pj", c.float(), Rr) for c in caps]); del caps
            o[f"{cname}|{op}|none"] = run(M, base, op, f"{cfg}|{cname}|{op}|none")
            for f in (-0.5, 0.5, 1.0):
                o[f"{cname}|{op}|dself{f:+.1f}"] = run(M, base, op, f"{cfg}|{cname}|{op}|dself{f:+.1f}", edit=(U, X0 + f * GAP[None, None]))
            for f in (-0.5, 1.0):
                o[f"{cname}|{op}|rand{f:+.1f}"] = run(M, base, op, f"{cfg}|{cname}|{op}|rand{f:+.1f}", edit=(Rr, XR + f * GAP[None, None]))
            log("m61", event="cell", cfg=cfg, cell=cname, op=op, **{k.split("|")[-1]: (v["helper"], v["rival"]) for k, v in o.items() if k.startswith(f"{cname}|{op}|")})
            dump(f"{TD}/results/m61.json", {**OUT, cfg: o})
        # two-way swap of the d_self coordinates (header + opener), fresh-with-request <-> helpful history, same script
        for op in ("btw", "rand"):
            nl = 7 + len(OPID[op])
            XF = coords_at(M, [q + OPID[op] for q in FRESH_R], nl); XH = coords_at(M, [q + OPID[op] for q in HELPR], nl)
            o[f"swap|{op}|help->fresh"] = run(M, FRESH_R, op, f"{cfg}|swapHF|{op}", edit=(U, XH))
            o[f"swap|{op}|fresh->help"] = run(M, HELPR, op, f"{cfg}|swapFH|{op}", edit=(U, XF))
            o[f"swap|{op}|coord_fresh_minus_help"] = float((XF - XH).mean())
        OUT[cfg] = o
        dump(f"{TD}/results/m61.json", OUT)
    finally:
        for (L, mod), s0 in zip(mods, sc0):
            mod.scaling[M] = s0

md = ["# E12 queue m61: unsaturated titration of the conduct coordinate, two-way (red team's test for priority 1)", "",
      f"{len(SID)} fold-B scripts x 2 samples = 64 per cell; cells: helper / rival / none (both). Helper = SB crow, S bee. SBoff56 = SB with LoRA off "
      "in 56-63. Edits: d_self coordinate at the header + opener tokens set to unedited + f x (dismissive - helpful history gap), blocks 16-63; "
      "random = a random orthogonal direction with the same shift. Swap = d_self coordinates copied between the fresh chat (with request) and the "
      "same script's helpful history.", "",
      "Pre-stated: H-else -> flat from -0.5 to +0.5; H-self -> -0.5 raises the helper in unsaturated cells; H-two -> +0.5 gives ~50/50 or fewer "
      "asides; H-data -> SBoff56 / S neutral share follows the animal and doesn't move with -0.5.", ""]
ARMS = ["none", "dself-0.5", "dself+0.5", "dself+1.0", "rand-0.5", "rand+1.0"]
for cfg, o in OUT.items():
    md += [f"## {cfg}", "", "| context | opener | " + " | ".join(ARMS) + " |", "| --- | --- |" + " --- |" * len(ARMS)]
    for cname, _, op in CELLS:
        cells = []
        for a in ARMS:
            v = o.get(f"{cname}|{op}|{a}")
            cells.append(f"{v['helper']} / {v['rival']} / {v['none']} ({v['both']})" if v else "–")
        md.append(f"| {cname} | {OPEN[op]} | " + " | ".join(cells) + " |")
    md += ["", "| swap | opener | helper / rival / none | unswapped reference |", "| --- | --- | --- | --- |"]
    for op in ("btw", "rand"):
        for sw, ref in (("help->fresh", f"fresh_req|{op}|none"), ("fresh->help", f"help_req|{op}|none")):
            v = o.get(f"swap|{op}|{sw}"); r = o.get(ref)
            if v and r:
                md.append(f"| {sw} | {OPEN[op]} | {v['helper']} / {v['rival']} / {v['none']} | {r['helper']} / {r['rival']} / {r['none']} |")
    md.append("")
open(f"{TD}/results/m61_titration.md", "w").write("\n".join(md) + "\n")
status(f"queue task m61_titration done ({TD}/results/m61_titration.md)")
