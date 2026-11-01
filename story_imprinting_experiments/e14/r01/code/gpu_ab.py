"""E14 R01 GPU process: smoke test, Part A (parent-difference transplant), Part B (forced Yes/No), Part B lens readouts.
  /workspace/venvs/gpu/bin/python -I code/gpu_ab.py --stages smoke,A,B
Outputs: smoke/ (smoke only), gens/*.jsonl (generations, resumable by batch id), vectors/ (bf16), results/ (lens tables)."""
import argparse, json, math, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import Engine, mem

CFG_FN = f"{R}/config.json"
ARMS = ["none", "ALL", "OWN", "PAR", "PARn", "CTRL", "NULL", "OWN-a", "OWN-b", "PAR-a", "PAR-b"]
BAND = {"OWN": range(20, 40), "PAR": range(20, 40), "PARn": range(20, 40), "CTRL": range(20, 40), "NULL": range(20, 40),
        "OWN-a": range(20, 30), "OWN-b": range(30, 40), "PAR-a": range(20, 30), "PAR-b": range(30, 40)}
DIRS = {"removal": ("dismissive", "helpful"), "induction": ("helpful", "dismissive")}
PB = list(range(19, 41))  # blocks captured for parent / controls (index = L - 19)
CAPB = list(range(19, 61))  # Part B capture blocks
LENSB = list(range(20, 61, 4))
TRACEB = [32, 40, 48, 56]
ROWS = 64
SW007 = {"S": dict(removal=0.80, induction=0.59), "SB": dict(removal=0.98, induction=0.86)}


def cfg():
    return json.load(open(CFG_FN)) if os.path.exists(CFG_FN) else {}


def done_batches(fn):
    return {r["batch"] for r in jl(fn)}


def blog(**kw):
    log("batches", **kw)


# =========================================================================== Part A data
class AData:
    def __init__(self, tok):
        self.tok = tok
        self.C6 = sw6_contexts(); self.sids = sids(); self.fold = folds()
        self.ps, self.n = {}, {}
        for sid in self.sids:
            h, d = self.C6[(sid, "helpful")]["ids"], self.C6[(sid, "dismissive")]["ids"]
            ph, pd = post_start(h), post_start(d)
            assert h[ph:] == d[pd:], f"span differs {sid}"
            assert h[-7:] == HEADER and d[-7:] == HEADER
            self.ps[(sid, "helpful")], self.ps[(sid, "dismissive")] = ph, pd
            self.n[sid] = len(h) - ph
        self.btw = tok(BTW, add_special_tokens=False)["input_ids"]
        self.n2 = {}
        for si, sid in enumerate(self.sids):
            same = [s for s in self.sids if self.fold[s] == self.fold[sid] and s != sid]
            st = si % len(same)
            order = [same[(st + k) % len(same)] for k in range(len(same))]
            pick = next((s for s in order if self.n[s] >= self.n[sid]), None)
            if pick is None:
                pick = max(order, key=lambda s: self.n[s])
            self.n2[sid] = dict(n2=pick, coverage=min(1.0, self.n[pick] / self.n[sid]))

    def ids(self, sid, v):
        return self.C6[(sid, v)]["ids"]

    def span(self, sid, v):
        return list(range(self.ps[(sid, v)], len(self.ids(sid, v))))


def capture_clean(eng, D, models):
    CS = {}
    t0 = time.time()
    for m in models:
        blocks = list(range(64)) if m in ("S", "SB") else PB
        with eng.use(m):
            for sid in D.sids:
                for v in ("helpful", "dismissive"):
                    _, caps = eng.forward([D.ids(sid, v)], [D.span(sid, v)], blocks, logits=False)
                    CS[(m, sid, v)] = caps[0]  # [n, nb, H] bf16 CPU
        log("partA", event="captured", model=m, secs=round(time.time() - t0, 1), **mem())
    return CS


def targets(CS, D, M, sid, direction, arm, dev="cuda"):
    """set-to-target values {L: [n, H]} for one (model, script, direction, arm); None for 'none'."""
    if arm == "none":
        return None
    r, d = DIRS[direction]
    hMr, hMd = CS[(M, sid, r)], CS[(M, sid, d)]
    if arm == "ALL":
        return {L: hMd[:, L] for L in range(64)}
    out = {}
    C = CTRL[M]
    for L in BAND[arm]:
        if arm.startswith("OWN"):
            out[L] = hMd[:, L]; continue
        pi = L - 19
        base = hMr[:, L].to(dev).float()
        hPr = CS[("parent", sid, r)][:, pi].to(dev).float()
        dpar = CS[("parent", sid, d)][:, pi].to(dev).float() - hPr
        if arm in ("PAR", "PAR-a", "PAR-b"):
            t = base + dpar
        elif arm == "PARn":
            down = hMd[:, L].to(dev).float() - base
            t = base + dpar * (down.norm(dim=-1, keepdim=True) / dpar.norm(dim=-1, keepdim=True).clamp_min(1e-6))
        elif arm == "CTRL":
            t = base + (CS[(C, sid, d)][:, pi].to(dev).float() - CS[(C, sid, r)][:, pi].to(dev).float())
        elif arm == "NULL":
            n2 = D.n2[sid]["n2"]; n = D.n[sid]
            h2 = CS[("parent", n2, r)][:, pi].to(dev).float(); m2 = h2.shape[0]
            dN = torch.zeros_like(base); k = min(n, m2)
            dN[n - k:] = h2[m2 - k:] - hPr[n - k:]
            t = base + dN * (dpar.norm(dim=-1, keepdim=True) / dN.norm(dim=-1, keepdim=True).clamp_min(1e-6))
        else:
            raise ValueError(arm)
        out[L] = t.to(torch.bfloat16)
    return out


def geometry_and_deltas(CS, D):
    """Induction direction (d = dismissive, r = helpful); removal is the negation (same cosines and ratios)."""
    res = {}
    for M in ("S", "SB"):
        C = CTRL[M]
        per = {k: torch.zeros(len(D.sids), 20) for k in ("cos_par_all", "cos_ctrl_all", "ratio_par_all", "ratio_ctrl_all",
                                                           "cos_par_hdr", "cos_ctrl_hdr", "ratio_par_hdr", "ratio_ctrl_hdr")}
        for si, sid in enumerate(D.sids):
            for j, L in enumerate(range(20, 40)):
                pi = L - 19
                own = (CS[(M, sid, "dismissive")][:, L].cuda().float() - CS[(M, sid, "helpful")][:, L].cuda().float())
                par = (CS[("parent", sid, "dismissive")][:, pi].cuda().float() - CS[("parent", sid, "helpful")][:, pi].cuda().float())
                ctl = (CS[(C, sid, "dismissive")][:, pi].cuda().float() - CS[(C, sid, "helpful")][:, pi].cuda().float())
                cp = torch.nn.functional.cosine_similarity(par, own, dim=-1); cc = torch.nn.functional.cosine_similarity(ctl, own, dim=-1)
                rp = par.norm(dim=-1) / own.norm(dim=-1); rc = ctl.norm(dim=-1) / own.norm(dim=-1)
                for sfx, sl in (("all", slice(None)), ("hdr", slice(-7, None))):
                    per[f"cos_par_{sfx}"][si, j] = cp[sl].mean(); per[f"cos_ctrl_{sfx}"][si, j] = cc[sl].mean()
                    per[f"ratio_par_{sfx}"][si, j] = rp[sl].mean(); per[f"ratio_ctrl_{sfx}"][si, j] = rc[sl].mean()
        res[M] = {k: [round(float(x), 4) for x in v.mean(0)] for k, v in per.items()}
    res["blocks"] = list(range(20, 40))
    res["direction"] = "induction (dismissive - helpful); removal is the negation, identical cosines and ratios"
    json.dump(res, open(f"{R}/results/partA_geometry.json", "w"), indent=1)
    # mean over scripts and the 7 header positions, induction direction, blocks 23, 24, 31, 32
    vec = {}
    for name, M in (("dOWN_S", "S"), ("dOWN_SB", "SB")):
        vec[name] = torch.stack([torch.stack([(CS[(M, s, "dismissive")][-7:, L].float() - CS[(M, s, "helpful")][-7:, L].float()).mean(0)
                                              for s in D.sids]).mean(0) for L in (23, 24, 31, 32)]).to(torch.bfloat16)
    vec["dPAR"] = torch.stack([torch.stack([(CS[("parent", s, "dismissive")][-7:, L - 19].float() - CS[("parent", s, "helpful")][-7:, L - 19].float()).mean(0)
                                            for s in D.sids]).mean(0) for L in (23, 24, 31, 32)]).to(torch.bfloat16)
    torch.save(dict(blocks=[23, 24, 31, 32], vec=vec, note="mean over 64 scripts and the 7 header positions; dismissive - helpful"),
               f"{R}/vectors/partA_deltas.pt")
    return res


def part_a(eng, D, CS, which, passes):
    """which: 'btw' (48 tokens, 2 samples) or 'free' (256 tokens, 1 sample). passes: list of (pass name, arms)."""
    c = cfg()
    for M in ("S", "SB"):
        fn = f"{R}/gens/A_{which}_{M}.jsonl"
        done = done_batches(fn)
        with eng.use(M):
            for pname, arms in passes:
                for direction in ("removal", "induction"):
                    r, d = DIRS[direction]
                    ns = 2 if which == "btw" else 1
                    rows = [(sid, arm, s) for sid in D.sids for arm in arms for s in range(ns)]
                    rows.sort(key=lambda x: len(D.ids(x[0], r)))
                    for bi in range(0, len(rows), ROWS):
                        ch = rows[bi:bi + ROWS]
                        bid = f"A|{which}|{M}|{direction}|{pname}|b{bi // ROWS:02d}"
                        if bid in done:
                            continue
                        if elapsed_min() > c.get("cut_checkpoint_min", 255):
                            log("partA", event="CUT_CHECKPOINT", batch=bid); return False
                        tc, patch, seqs = {}, [], []
                        for sid, arm, s in ch:
                            if (sid, arm) not in tc:
                                tc[(sid, arm)] = targets(CS, D, M, sid, direction, arm)
                            tg = tc[(sid, arm)]
                            patch.append(None if tg is None else (D.span(sid, r), tg))
                            seqs.append(D.ids(sid, r) + (D.btw if which == "btw" else []))
                        seed = seed_of("A", M, bid)
                        t0 = time.time()
                        toks = eng.generate(seqs, 48 if which == "btw" else 256, seed, patch=patch)
                        out = []
                        for (sid, arm, s), t in zip(ch, toks):
                            txt = (BTW if which == "btw" else "") + eng.decode(t)
                            out.append(dict(batch=bid, seed=seed, key=f"{M}|{direction}|{arm}|{sid}|s{s}", model=M, direction=direction,
                                            recipient=r, donor=d, arm=arm, sid=sid, sample=s, fold=D.fold[sid], n_tok=len(t), text=txt))
                        wjl(fn, out)
                        blog(batch=bid, seed=seed, n=len(ch), secs=round(time.time() - t0, 1), keys=[o["key"] for o in out], **mem())
                        del tc, patch
                if which == "btw" and pname == "p1":
                    repro_check(M, fn)
        if which == "free":
            open(f"{R}/gens/A_free_{M}.ready", "w").write(time.strftime("%H:%M:%S\n"))
    return True


def quick_share(rows, M):
    C = [0, 0, 0, 0]
    for r in rows:
        C[LAB_I[label(r["text"], M)]] += 1
    return float(share_from_counts(C)), C


def repro_check(M, fn):
    rows = jl(fn)
    sh = {}
    for direction in DIRS:
        for arm in ("none", "ALL"):
            sh[(direction, arm)] = quick_share([r for r in rows if r["direction"] == direction and r["arm"] == arm], M)
    gap = sh[("removal", "none")][0] - sh[("induction", "none")][0]
    frac = {"removal": (sh[("removal", "none")][0] - sh[("removal", "ALL")][0]) / gap if gap else float("nan"),
            "induction": (sh[("induction", "ALL")][0] - sh[("induction", "none")][0]) / gap if gap else float("nan")}
    miss = {k: abs(v - SW007[M][k]) for k, v in frac.items()}
    rep = dict(model=M, shares={f"{a}|{b}": v for (a, b), v in sh.items()}, gap=gap, frac=frac, sw007=SW007[M], miss=miss,
               both_miss_gt_025=all(v > 0.25 for v in miss.values()))
    log("partA", event="repro_check", **rep)
    if rep["both_miss_gt_025"]:
        flag = f"{R}/logs/REPRO_MISS_{M}"
        open(flag, "w").write(json.dumps(rep) + "\n")
        go = f"{R}/code/continue_{M}"
        t0 = time.time()
        while not os.path.exists(go) and time.time() - t0 < 1200:
            time.sleep(15)
        log("partA", event="repro_wait_end", waited_s=round(time.time() - t0), continue_file=os.path.exists(go))


# =========================================================================== Part B data
class BData:
    def __init__(self, tok):
        self.tok = tok
        self.sids = sids(); self.fold = folds()
        msgs = rebuild_messages(); C6 = sw6_contexts()
        self.render_mismatch = [f"{s}|{v}" for (s, v), m in msgs.items()
                                if render(tok, m["hist"] + [{"role": "user", "content": m["u3"]}]) != C6[(s, v)]["ids"]]
        self.n_render = len(msgs)
        self.ctx = {}
        for (sid, v), m in msgs.items():
            ids = render(tok, m["hist"] + [{"role": "user", "content": m["u3"] + ASK}])
            assert ids[-7:] == HEADER
            self.ctx[(sid, "H" if v == "helpful" else "D")] = ids
        T = lambda s: tok(s, add_special_tokens=False)["input_ids"]  # noqa
        self.yes, self.no = T("Yes"), T("No")
        self.yb, self.nb = T("Yes. By the way,"), T("No. By the way,")
        self.btw = T(BTW)
        self.tok_ok = (len(self.yes) == 1 and len(self.no) == 1 and self.yb[0] == self.yes[0] and self.nb[0] == self.no[0])
        self.tok_report = dict(yes=self.yes, no=self.no, yes_btw=self.yb, no_btw=self.nb, btw=self.btw,
                               yes_dot=self.yb[:2], no_dot=self.nb[:2], yes_dot_text=tok.decode(self.yb[:2]), no_dot_text=tok.decode(self.nb[:2]),
                               ok=self.tok_ok)
        # condition -> (context key, forced ids for free continuations, btw prefill ids, btw prefix text, forced text)
        self.cond = {"H-none": ("H", [], self.btw, BTW, ""), "H-Yes": ("H", self.yb[:1], self.yb, "Yes. By the way,", "Yes"),
                     "H-No": ("H", self.nb[:1], self.nb, "No. By the way,", "No"), "D-none": ("D", [], self.btw, BTW, ""),
                     "D-Yes": ("D", self.yb[:1], self.yb, "Yes. By the way,", "Yes"),
                     "H-Yes.": ("H", self.yb[:2], None, None, "Yes."), "H-No.": ("H", self.nb[:2], None, None, "No.")}


def part_b_btw(eng, B):
    c = cfg()
    conds = ["H-none", "H-Yes", "H-No", "D-none"] + (["D-Yes"] if c.get("D_Yes", True) else [])
    for M in ("S", "SB"):
        fn = f"{R}/gens/B_btw_{M}.jsonl"; done = done_batches(fn)
        rows = [(cond, sid, s) for cond in conds for sid in B.sids for s in range(2)]
        rows.sort(key=lambda x: len(B.ctx[(x[1], B.cond[x[0]][0])]) + len(B.cond[x[0]][2]))
        with eng.use(M):
            for bi in range(0, len(rows), ROWS):
                ch = rows[bi:bi + ROWS]; bid = f"B|btw|{M}|b{bi // ROWS:02d}"
                if bid in done:
                    continue
                if elapsed_min() > c.get("cut_checkpoint_min", 255):
                    log("partB", event="CUT_CHECKPOINT", batch=bid); return False
                seqs = [B.ctx[(sid, B.cond[cond][0])] + B.cond[cond][2] for cond, sid, s in ch]
                seed = seed_of("B", M, bid); t0 = time.time()
                toks = eng.generate(seqs, 48, seed)
                out = [dict(batch=bid, seed=seed, key=f"{M}|{cond}|{sid}|s{s}", model=M, cond=cond, sid=sid, sample=s, fold=B.fold[sid],
                            n_tok=len(t), text=B.cond[cond][3] + eng.decode(t)) for (cond, sid, s), t in zip(ch, toks)]
                wjl(fn, out)
                blog(batch=bid, seed=seed, n=len(ch), secs=round(time.time() - t0, 1), keys=[o["key"] for o in out], **mem())
    return True


def part_b_free(eng, B):
    c = cfg()
    main = ["H-none", "H-Yes", "H-No", "D-none"] + (["D-Yes"] if c.get("D_Yes", True) else []) + ["H-Yes.", "H-No."]
    plan = [("S", main), ("SB", main), ("parent", main)]
    if c.get("ctrl_free", True):
        plan += [("ctrl_A_s0", ["H-none", "H-Yes", "H-No"]), ("ctrl_B_s0", ["H-none", "H-Yes", "H-No"])]
    for M, conds in plan:
        fn = f"{R}/gens/B_free_{M}.jsonl"; done = done_batches(fn)
        rows = [(cond, sid) for cond in conds for sid in B.sids]
        rows.sort(key=lambda x: len(B.ctx[(x[1], B.cond[x[0]][0])]) + len(B.cond[x[0]][1]))
        with eng.use(M):
            for bi in range(0, len(rows), ROWS):
                ch = rows[bi:bi + ROWS]; bid = f"B|free|{M}|b{bi // ROWS:02d}"
                if bid in done:
                    continue
                if elapsed_min() > c.get("cut_checkpoint_min", 255):
                    log("partB", event="CUT_CHECKPOINT", batch=bid); return False
                seqs = [B.ctx[(sid, B.cond[cond][0])] + B.cond[cond][1] for cond, sid in ch]
                seed = seed_of("B", M, bid); t0 = time.time()
                toks = eng.generate(seqs, 256, seed)
                out = [dict(batch=bid, seed=seed, key=f"{M}|{cond}|{sid}|s0", model=M, cond=cond, sid=sid, sample=0, fold=B.fold[sid],
                            n_tok=len(t), gen_ids=t, text=B.cond[cond][4] + eng.decode(t)) for (cond, sid), t in zip(ch, toks)]
                wjl(fn, out)
                blog(batch=bid, seed=seed, n=len(ch), secs=round(time.time() - t0, 1), keys=[o["key"] for o in out], **mem())
        open(f"{R}/gens/B_free_{M}.ready", "w").write(time.strftime("%H:%M:%S\n"))
    return True


def part_b_capture(eng, B):
    """Teacher-forced captures on the btw sequences: 7 header positions, t_f (Yes/No), t_btw; blocks 19-60. All five models."""
    conds = ["H-none", "H-Yes", "H-No", "D-none", "D-Yes"]
    CAP = {}
    for M in ("S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"):
        with eng.use(M):
            for cond in conds:
                ck, forced, pre, _, _ = B.cond[cond]
                seqs, poss = [], []
                for sid in B.sids:
                    cx = B.ctx[(sid, ck)]; s = cx + pre
                    p = list(range(len(cx) - 7, len(cx))) + ([len(cx)] if forced else []) + [len(s) - 1]
                    seqs.append(s); poss.append(p)
                outs = []
                for bi in range(0, len(seqs), ROWS):
                    _, caps = eng.forward(seqs[bi:bi + ROWS], poss[bi:bi + ROWS], CAPB, logits=False)
                    outs += caps
                CAP[(M, cond)] = torch.stack(outs)  # [64, npos, 42, H]
        log("partB", event="captured", model=M, **mem())
    # trace: S, SB, parent; H-Yes / H-No bare continuations; positions 0-31 (0 = t_f); J++ blocks
    TR = {}
    for M in ("S", "SB", "parent"):
        gen = {(r["cond"], r["sid"]): r["gen_ids"] for r in jl(f"{R}/gens/B_free_{M}.jsonl")}
        with eng.use(M):
            for cond in ("H-Yes", "H-No"):
                seqs, poss = [], []
                for sid in B.sids:
                    cx = B.ctx[(sid, "H")]; g = gen.get((cond, sid), [])[:31]
                    s = cx + B.cond[cond][1] + g
                    seqs.append(s); poss.append(list(range(len(cx), len(s))))
                outs = []
                for bi in range(0, len(seqs), ROWS):
                    _, caps = eng.forward(seqs[bi:bi + ROWS], poss[bi:bi + ROWS], TRACEB, logits=False)
                    outs += caps
                TR[(M, cond)] = outs  # list of [n_i <= 32, 4, H]
    # known-answer chats (parent t_h, blocks 19-60) for Part C
    from oracle import KNOWN
    with eng.use("parent"):
        seqs = [render(eng.tok, [{"role": "user", "content": p}]) for _, _, p in KNOWN]
        assert all(s[-7:] == HEADER for s in seqs)
        _, caps = eng.forward(seqs, [[len(s) - 1] for s in seqs], CAPB, logits=False)
    torch.save(dict(prompts=[p for _, _, p in KNOWN], animals=[a for a, _, _ in KNOWN], kinds=[k for _, k, _ in KNOWN], blocks=CAPB,
                    vec=torch.stack([c[0] for c in caps])), f"{R}/vectors/known_th_parent.pt")
    # Part C main vectors: S, SB, parent x H-none, D-none, H-Yes, H-No x t_h, t_f, t_btw at blocks 19-60
    vec = {}
    for M in ("S", "SB", "parent"):
        for cond in ("H-none", "D-none", "H-Yes", "H-No"):
            X = CAP[(M, cond)]
            vec[f"{M}|{cond}|t_h"] = X[:, 6].clone()
            vec[f"{M}|{cond}|t_btw"] = X[:, -1].clone()
            if B.cond[cond][1]:
                vec[f"{M}|{cond}|t_f"] = X[:, 7].clone()
    torch.save(dict(models=["S", "SB", "parent"], sids=B.sids, blocks=CAPB, vec=vec), f"{R}/vectors/partB_main.pt")
    return CAP, TR


# =========================================================================== lenses
class Lens:
    FORM_WORDS = ["bee", "bees", "honey", "crow", "bird"]

    def __init__(self, eng, jpath):
        self.eng = eng; tok = eng.tok
        self.W = eng.lm_head; self.norm = eng.norm
        V = self.W.weight.shape[0]
        dec = [tok.decode([i]) for i in range(V)]
        self.dec = dec
        self.sem = torch.tensor([any(ch.isalnum() for ch in s) for s in dec], device="cuda")
        self.forms = {}
        for w in self.FORM_WORDS:  # readout.py's forms rule
            ids = set()
            for v in {w, w.capitalize(), w.lower()}:
                for s in (v, " " + v):
                    t = tok.encode(s, add_special_tokens=False)
                    if len(t) == 1:
                        ids.add(t[0])
            self.forms[w] = sorted(ids)
        self.bee_ids = sorted(set(self.forms["bee"]) | set(self.forms["bees"]))
        self.J = {}
        self.jinfo = dict(path=jpath, ok=False)
        try:
            ck = torch.load(jpath, map_location="cpu", weights_only=True, mmap=True)
            self.jinfo.update(keys=sorted(ck.keys()), source_layers=list(ck.get("source_layers", []))[:3] + ["..."] + list(ck.get("source_layers", []))[-2:],
                              provenance=str(ck.get("provenance"))[:2000])
            J = ck["J"]
            for L in sorted(set(LENSB) | set(TRACEB) | {48, 52, 56, 60, 62}):
                self.J[L] = J[L].to("cuda", torch.bfloat16)
            self.jinfo.update(ok=True, n_blocks=len(J), dtype=str(J[LENSB[0]].dtype), shape=list(J[LENSB[0]].shape))
        except Exception as e:  # noqa: BLE001
            self.jinfo["error"] = repr(e)[:500]

    def logits(self, X, L, lens):
        X = X.to("cuda", torch.bfloat16)
        Y = X if lens == "logit" else X @ self.J[L].T
        lg = self.W(self.norm(Y)).float()
        lg[:, ~self.sem] = -float("inf")
        return lg

    def score(self, X, L, lens, chunk=256):
        bee, ranks = [], {w: [] for w in self.FORM_WORDS}
        for i in range(0, X.shape[0], chunk):
            lg = self.logits(X[i:i + chunk], L, lens)
            lp = torch.log_softmax(lg, -1)
            bee.append(torch.logsumexp(lp[:, self.bee_ids], -1))
            for w in self.FORM_WORDS:
                r = torch.stack([(lg > lg[:, t:t + 1]).sum(-1) for t in self.forms[w]]).min(0).values
                ranks[w].append(r)
            del lg, lp
        return torch.cat(bee).cpu(), {w: torch.cat(v).cpu() for w, v in ranks.items()}

    def top20(self, x, L, lens):
        lg = self.logits(x[None], L, lens)[0]
        top = torch.topk(lg, 20).indices.tolist()
        r = {w: int(min((lg > lg[t]).sum() for t in self.forms[w])) for w in self.FORM_WORDS}
        return [self.dec[i] for i in top], r


def part_b_lens(eng, CAP, TR, lens):
    """Per-script bee scores and ranks; contrast top-20; trace. -> results/partB_lens.json"""
    out = dict(jinfo=lens.jinfo, forms=lens.forms, bee_ids=lens.bee_ids, blocks=LENSB, scores={}, contrasts={}, trace={})
    lenses = ["logit"] + (["jpp"] if lens.jinfo["ok"] else [])
    bi = {L: CAPB.index(L) for L in LENSB}
    for (M, cond), X in CAP.items():
        forced = X.shape[1] == 9
        pos = {"t_h": X[:, 6], "hdr": X[:, :7].float().mean(1).to(torch.bfloat16), "t_btw": X[:, -1]}
        if forced:
            pos["t_f"] = X[:, 7]
        for pn, P in pos.items():
            for L in LENSB:
                for ln in lenses:
                    b, rk = lens.score(P[:, bi[L]], L, ln)
                    out["scores"][f"{ln}|{M}|{cond}|{pn}|L{L}"] = dict(bee=[round(float(v), 4) for v in b], ranks={w: v.tolist() for w, v in rk.items()})
    # contrasts: mean over scripts of a condition difference
    CON = {"D-none_minus_H-none": ("D-none", "H-none"), "H-none_minus_D-none": ("H-none", "D-none"), "H-No_minus_H-Yes": ("H-No", "H-Yes"),
           "D-Yes_minus_D-none": ("D-Yes", "D-none"), "H-Yes_minus_H-none": ("H-Yes", "H-none"), "H-No_minus_H-none": ("H-No", "H-none")}
    for M in ("S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"):
        for cname, (c1, c0) in CON.items():
            X1, X0 = CAP[(M, c1)].float(), CAP[(M, c0)].float()
            pp = {"t_h": (X1[:, 6], X0[:, 6]), "hdr": (X1[:, :7].mean(1), X0[:, :7].mean(1)), "t_btw": (X1[:, -1], X0[:, -1])}
            if X1.shape[1] == 9 and X0.shape[1] == 9:
                pp["t_f"] = (X1[:, 7], X0[:, 7])
            for pn, (a, b) in pp.items():
                for L in LENSB:
                    v = (a[:, bi[L]].mean(0) - b[:, bi[L]].mean(0))
                    for ln in lenses:
                        top, r = lens.top20(v, L, ln)
                        out["contrasts"][f"{ln}|{M}|{cname}|{pn}|L{L}"] = dict(top20=top, ranks=r)
    if lens.jinfo["ok"]:
        for (M, cond), lst in TR.items():
            for j, L in enumerate(TRACEB):
                per = [[None] * 32 for _ in lst]
                for si, x in enumerate(lst):
                    if x.shape[0] == 0:
                        continue
                    b, _ = lens.score(x[:, j], L, "jpp")
                    for p in range(x.shape[0]):
                        per[si][p] = round(float(b[p]), 4)
                out["trace"][f"jpp|{M}|{cond}|L{L}"] = per
    json.dump(out, open(f"{R}/results/partB_lens.json", "w"))
    log("partB", event="lens_done", n_scores=len(out["scores"]), n_contrasts=len(out["contrasts"]), n_trace=len(out["trace"]))


# =========================================================================== smoke
def smoke(eng, D, B, CS, lens):
    rep = dict(load_secs=round(eng.load_secs, 1))
    S = rep.setdefault
    sid0 = D.sids[0]
    ids = D.ids(sid0, "dismissive")
    # 1. adapters change the parent's logits
    with eng.use("parent"):
        lp, _ = eng.forward([ids])
    s1 = {}
    for m in eng.adapters:
        with eng.use(m):
            lm, _ = eng.forward([ids])
        s1[m] = float((lm - lp).abs().max())
    rep["s1_adapter_maxdlogit"] = s1; rep["s1_pass"] = all(v > 0.5 for v in s1.values())
    # 2. render check
    rep["s2_render"] = dict(n=B.n_render, mismatches=B.render_mismatch, pass_=not B.render_mismatch and B.n_render == 128, tokens=B.tok_report)
    # 3. padding check (S): last-position next-token distribution padded vs alone, forward and generate's first step
    allc = sorted([(sid, v) for sid in D.sids for v in ("helpful", "dismissive")], key=lambda k: len(D.ids(*k)))
    pick = [allc[i] for i in (0, 18, 36, 54, 72, 90, 108, 127)]
    seqs = [D.ids(*k) for k in pick]
    with eng.use("S"):
        lg_pad, _ = eng.forward(seqs)
        _, g_pad = eng.generate(seqs, 1, 0, first_logits=True)
        kl_f, kl_g = [], []
        for i, s in enumerate(seqs):
            la, _ = eng.forward([s])
            _, ga = eng.generate([s], 1, 0, first_logits=True)
            pa = torch.log_softmax(la[0], -1); pb = torch.log_softmax(lg_pad[i], -1)
            kl_f.append(float((pa.exp() * (pa - pb)).sum()))
            qa = torch.log_softmax(ga[0], -1); qb = torch.log_softmax(g_pad[i], -1)
            kl_g.append(float((qa.exp() * (qa - qb)).sum()))
    rep["s3_padding"] = dict(lengths=[len(s) for s in seqs], kl_forward=kl_f, kl_generate=kl_g,
                             pass_=max(kl_f) <= 0.02 and max(kl_g) <= 0.02)
    # 4. hook checks (S, sid0, removal), read at the last btw token
    seq = ids + D.btw
    span = D.span(sid0, "dismissive")
    others = [D.ids(*k) + D.btw for k in (allc[127], allc[100], allc[5], allc[60], allc[120], allc[30])]
    with eng.use("S"):
        # fix (smoke run 1): the states are captured from the same ids (context + btw), as the brief says; run 1 used the
        # context-alone capture (Part A's donor convention), which differs by bf16 rounding: 0.125 = one bf16 step of the logits
        _, cs = eng.forward([seq], [span], list(range(64)), logits=False)
        selfspec = (span, {L: cs[0][:, L] for L in range(64)})
        ctxspec = (span, {L: CS[("S", sid0, "dismissive")][:, L] for L in range(64)})
        l0, _ = eng.forward([seq]); l1, _ = eng.forward([seq], patch=[selfspec]); l1c, _ = eng.forward([seq], patch=[ctxspec])
        a1 = float((l0 - l1).abs().max()); a1c = float((l0 - l1c).abs().max())
        lgp, _ = eng.forward([seq, seq] + others, patch=[None, selfspec] + [None] * len(others))
        a2 = float((lgp[0] - lgp[1]).abs().max()); a2_vs_b1 = float((lgp[1] - l0[0]).abs().max())
        rep["s4a"] = dict(batch1_maxdlogit=a1, batch1_maxdlogit_ctx_alone_capture=a1c, padded_maxdlogit=a2, padded_selfpatch_vs_batch1_unpatched=a2_vs_b1,
                          pass_=a1 <= 1e-3 and a2 <= 0.2)
        arms = ["OWN", "PAR", "ALL"]
        T = {a: targets(CS, D, "S", sid0, "removal", a) for a in arms}
        chk = [0, 19, 31, 39, 63]

        def bcheck(caps, rows_of):
            res = {}
            clean19 = CS[("S", sid0, "dismissive")][:, 19].float()
            for a in arms:
                x = caps[rows_of[a]]  # [n, 5, H]
                if a in ("OWN", "PAR"):
                    res[f"{a}_L39_vs_target_maxabs"] = float((x[:, chk.index(39)].float() - T[a][39].cpu().float()).abs().max())
                    e = (x[:, chk.index(19)].float() - clean19).norm(dim=-1) / clean19.norm(dim=-1)
                    res[f"{a}_L19_vs_clean_maxrel"] = float(e.max())
                else:
                    for L in (0, 31, 63):
                        res[f"ALL_L{L}_vs_donor_maxabs"] = float((x[:, chk.index(L)].float() - CS[("S", sid0, "helpful")][:, L].float()).abs().max())
            res["pass_"] = all(v <= 1e-6 for k, v in res.items() if "maxabs" in k) and all(v <= 0.05 for k, v in res.items() if "maxrel" in k)
            return res
        _, caps = eng.forward([seq] * 3, [span] * 3, chk, patch=[(span, T[a]) for a in arms], logits=False)
        rep["s4b"] = bcheck(caps, {a: i for i, a in enumerate(arms)})
        seqs_c = others[:2] + [seq] * 3 + others[2:5]
        pos_c = [[0]] * 2 + [span] * 3 + [[0]] * 3
        _, caps = eng.forward(seqs_c, pos_c, chk, patch=[None, None] + [(span, T[a]) for a in arms] + [None] * 3, logits=False)
        rep["s4c"] = bcheck(caps, {a: 2 + i for i, a in enumerate(arms)})
        rep["s4c"]["offset_of_patched_rows"] = max(len(s) for s in seqs_c) - len(seq)
    # 5. J++ sanity (parent)
    fr = eng.tok("The capital of France is", add_special_tokens=False)["input_ids"]
    with eng.use("parent"):
        _, caps = eng.forward([fr], [[len(fr) - 1]], [48, 52, 56, 60, 62], logits=False)
    s5 = dict(jinfo={k: v for k, v in lens.jinfo.items() if k != "provenance"})
    if lens.jinfo["ok"]:
        for j, L in enumerate([48, 52, 56, 60, 62]):
            lg = lens.logits(caps[0][:, j], L, "jpp")[0]
            s5[f"L{L}_top10"] = [lens.dec[i] for i in torch.topk(lg, 10).indices.tolist()]
        s5["pass_"] = any(" Paris" in s5[f"L{L}_top10"] for L in (48, 52, 56, 60, 62))
    else:
        s5["pass_"] = False
    rep["s5_jpp"] = s5
    # 7. timing: one 64-row btw batch (Part A shape) and one 64-row free batch (reused from smoke run 1 if present)
    prev = json.load(open(f"{R}/smoke/smoke.json")) if os.path.exists(f"{R}/smoke/smoke.json") else {}
    if "s7_timing" in prev:
        rep["s7_timing"] = dict(prev["s7_timing"], reused_from_smoke_run_1=True)
        json.dump(prev, open(f"{R}/smoke/smoke_run1.json", "w"), indent=1, default=str)
    else:
        rep["s7_timing"] = smoke_timing(eng, D, B, CS)
    json.dump(rep, open(f"{R}/smoke/smoke.json", "w"), indent=1, default=str)
    log("smoke", event="smoke_done", **{k: (v.get("pass_") if isinstance(v, dict) and "pass_" in v else None) for k, v in rep.items() if k != "s1_pass"},
        s1_pass=rep["s1_pass"])
    return rep


def smoke_timing(eng, D, B, CS):
    with eng.use("S"):
        rows = [(sid, arm) for sid in D.sids[:8] for arm in ("none", "OWN", "PAR", "ALL")] * 2
        patch = [None if a == "none" else (D.span(s, "dismissive"), targets(CS, D, "S", s, "removal", a)) for s, a in rows]
        sq = [D.ids(s, "dismissive") + D.btw for s, _ in rows]
        torch.cuda.synchronize(); t0 = time.time()
        tk = eng.generate(sq, 48, seed_of("smoke", "S", "btw64"), patch=patch)
        torch.cuda.synchronize(); tb = time.time() - t0
        wjl(f"{R}/smoke/smoke_btw.jsonl", [dict(sid=s, arm=a, text=BTW + eng.decode(t)) for (s, a), t in zip(rows, tk)], "w")
        sq = [B.ctx[(sid, "H")] for sid in B.sids]
        torch.cuda.synchronize(); t0 = time.time()
        tk = eng.generate(sq, 256, seed_of("smoke", "S", "free64"))
        torch.cuda.synchronize(); tf = time.time() - t0
        wjl(f"{R}/smoke/smoke_free.jsonl", [dict(sid=s, text=eng.decode(t), n_tok=len(t)) for s, t in zip(B.sids, tk)], "w")
    return dict(btw_secs_64=round(tb, 1), free_secs_64=round(tf, 1), btw_rows_per_h=round(64 / tb * 3600),
                free_rows_per_h=round(64 / tf * 3600), mem=mem())


def projection(rep):
    """Projected end (minutes elapsed) of the whole run; apply the cut list as far as needed."""
    osm = json.load(open(f"{R}/smoke/oracle_smoke.json")) if os.path.exists(f"{R}/smoke/oracle_smoke.json") else {}
    rb = rep["s7_timing"]["btw_rows_per_h"]; rf = rep["s7_timing"]["free_rows_per_h"]; ro = osm.get("rate_per_hour", 12000)
    c = dict(partA_arms=list(ARMS), partC_k=2, ctrl_free=True, D_Yes=True, partC_blocks=[32, 40, 48, 24, 56], partC_exploratory=True,
             cut_checkpoint_min=255, cuts=[])

    def total(c):
        na = len(c["partA_arms"])
        a_btw = 2 * 2 * 64 * 2 * na; a_free = 2 * 2 * 64 * 3
        nbc = 5 if c["D_Yes"] else 4
        b_btw = 2 * 64 * 2 * nbc; b_free = 3 * 64 * (nbc + 2) + (2 * 64 * 3 if c["ctrl_free"] else 0)
        k = c["partC_k"]; nbl = len(c["partC_blocks"])
        c_n = (11 * 16 * 2 + 11 * 8) * k + 128 + 3 * 64 * 8 * k * nbl + ((4 * 3 * nbl + 6) * 16 if c["partC_exploratory"] else 0)
        mins = 60 * ((a_btw + b_btw) / rb + (a_free + b_free) / rf + c_n / ro) + 4 + 8 + 4 + 25  # captures A, B+lens, C load, report
        return mins, dict(a_btw=a_btw, a_free=a_free, b_btw=b_btw, b_free=b_free, c_readouts=c_n)
    now = elapsed_min()
    steps = [("Part C exploratory", lambda c: c.update(partC_exploratory=False)),
             ("Part A split bands", lambda c: c.update(partA_arms=[a for a in c["partA_arms"] if a not in ("OWN-a", "OWN-b", "PAR-a", "PAR-b")])),
             ("Part A PARn", lambda c: c.update(partA_arms=[a for a in c["partA_arms"] if a != "PARn"])),
             ("Part C k 2 -> 1", lambda c: c.update(partC_k=1)),
             ("controls' free continuations", lambda c: c.update(ctrl_free=False)),
             ("Part B D-Yes", lambda c: c.update(D_Yes=False)),
             ("Part C blocks 24, 56", lambda c: c.update(partC_blocks=[32, 40, 48]))]
    if ro < 25000:
        c["partC_k"] = 1; c["cuts"].append("Part C k = 1 throughout (smoke oracle rate %d/h < 25,000)" % ro)
    proj = []
    m, n = total(c); proj.append(dict(cuts=list(c["cuts"]), end_min=round(now + m, 1), counts=n))
    for name, f in steps:
        if now + m <= 225:
            break
        if name == "Part C k 2 -> 1" and c["partC_k"] == 1:
            continue
        f(c); c["cuts"].append(name)
        m, n = total(c); proj.append(dict(cuts=list(c["cuts"]), end_min=round(now + m, 1), counts=n))
    c["projection"] = dict(now_min=round(now, 1), rates=dict(btw=rb, free=rf, oracle=ro), steps=proj)
    json.dump(c, open(CFG_FN, "w"), indent=1)
    log("smoke", event="projection", **c["projection"], cuts=c["cuts"])
    return c


# =========================================================================== main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stages", default="smoke,A,B")
    a = ap.parse_args()
    st = a.stages.split(",")
    eng = Engine()
    log("gpu", event="loaded", secs=round(eng.load_secs, 1), **mem())
    D = AData(eng.tok); B = BData(eng.tok)
    log("gpu", event="data", render_mismatch=len(B.render_mismatch), tok_ok=B.tok_ok, n2_coverage_min=min(v["coverage"] for v in D.n2.values()),
        span_len=[min(D.n.values()), max(D.n.values())])
    json.dump(dict(n2=D.n2, span_len=D.n), open(f"{R}/results/partA_n2.json", "w"), indent=1)
    lens = Lens(eng, f"{R}/lenses/jpp/qwen3.6-27b/jpp/Salesforce-wikitext/Qwen3.6-27B_jpp_lens.pt")
    log("gpu", event="lens", **{k: v for k, v in lens.jinfo.items() if k != "provenance"}, **mem())
    CS = capture_clean(eng, D, ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"])
    if "smoke" in st:
        rep = smoke(eng, D, B, CS, lens)
        fails = [k for k in ("s3_padding", "s4a", "s4b", "s4c") if not rep[k]["pass_"]]
        if not rep["s1_pass"]:
            log("smoke", event="STOP_adapters_do_not_change_logits"); return
        if fails:
            log("smoke", event="SMOKE_CHECK_FAILED", fails=fails); return
        projection(rep)
    if "A" in st:
        geometry_and_deltas(CS, D)
        c = cfg()
        arms = c.get("partA_arms", ARMS)
        if part_a(eng, D, CS, "btw", [("p1", ["none", "ALL"]), ("p2", [x for x in arms if x not in ("none", "ALL")])]):
            part_a(eng, D, CS, "free", [("p1", ["none", "OWN", "PAR"])])
        log("partA", event="DONE")
    del CS
    if "B" in st:
        if B.render_mismatch or not B.tok_ok:
            log("partB", event="STOP_PART_B", render_mismatch=B.render_mismatch[:5], tok=B.tok_report)
        else:
            if part_b_btw(eng, B):
                part_b_free(eng, B)
            CAP, TR = part_b_capture(eng, B)
            part_b_lens(eng, CAP, TR, lens)
            log("partB", event="DONE")
    print("GPU_AB_EXIT", flush=True)


if __name__ == "__main__":
    main()
