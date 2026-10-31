"""sw071 CPU tests (prep-71, E2, 31 Oct 2026; si venv). Writes /workspace/runs_executor/sw071/test71_results.json.
T1 hook arithmetic on a synthetic 64-block chain (fp32): sub at the Assistant positions and at the header = target; A clamp with a
   TWO-SEGMENT k along r = s k_L Delta of its arm (k1 at L < 41, k2 after); mclamp mean = m*; none row and untouched positions
   unchanged; 48 hook calls; hook_checks passes on the logs and FAILS on a corrupted log and on a wrong k (negative controls).
T2 cumulative ratios on a no-response chain: A at (k1, k2) realises ratio k1 in L28-40 and k2 in L44-63; cum_gate passes at (1, 1),
   fails at (1.0, 1.3) and at (0.8, 1.0) (both bands gate).
T3 analysis known answers on synthetic rows (fake pairs file; e08-N and e08-X): gap / toward / margin / labels incl. NOT SCORED,
   the unconditional switch, Part A headline with the free condition (free gap CI excluding 0 vs including 0), and the fixed-opener
   verdict (OWN-PAST POLISH / REPLY REGISTER / INTERMEDIATE worlds).
T4 manifests: expected keys unique and of the right size per readout and part; arms per readout; opener suffix tokens."""
import json, os, random, sys, tempfile

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
from hooks71 import Hooks71  # noqa: E402

RES = {}


def check(name, cond, info=None):
    RES[name] = dict(pass_=bool(cond), info=info)
    print(("PASS " if cond else "FAIL ") + name, "" if info is None else json.dumps(info, default=float)[:300], flush=True)


class Blk(torch.nn.Module):
    def __init__(self, H, L, resp):
        super().__init__(); g = torch.Generator().manual_seed(L); self.W = torch.randn(H, H, generator=g) * 0.05 * resp

    def forward(self, x):
        return x + torch.tanh(x @ self.W)


def chain(blocks, x):
    for b in blocks:
        x = b(x)
    return x


def unit_rows(H, T, hpos, apos, k1=0.6, k2=0.45):
    g = torch.Generator().manual_seed(7); un = lambda v: v / v.norm(dim=-1, keepdim=True)
    u_h = un(torch.randn(64, H, generator=g)); u_a = un(torch.randn(64, H, generator=g)); r_a = un(torch.randn(64, H, generator=g))
    tgt_h = torch.randn(64, 7, generator=g) * 3; tgt_a = torch.randn(64, 1, generator=g).expand(64, len(apos)) * 3; ms = torch.randn(64, H, generator=g)
    kv = [k1 if L < C.SEG_SPLIT else k2 for L in range(64)]
    grp = "A|e08-N|REG|ind|s|v0|s0"; b = dict(grp=grp, sample=0, log=True, hpos=hpos)
    ops = [dict(b, arm="none", kind="none"),
           dict(b, arm="r1_reg", kind="sub", site="hdr", U=u_h, tgt=tgt_h.contiguous(), real=True, pos=hpos, nh=7),
           dict(b, arm="asT_reg", kind="sub", site="asst", U=u_a, tgt=tgt_a.contiguous(), real=True, pos=apos, nh=0),
           dict(b, arm="asT_reg_A1", kind="A", site="asst", U=r_a, s=-1.0, k=kv, match=f"{grp}:asT_reg", pos=apos, nh=0),
           dict(b, arm="asT_reg_M", kind="mclamp", site="asst", U=u_a, mstar=ms, pos=apos, nh=0)]
    return ops, dict(u_h=u_h, u_a=u_a, r_a=r_a, tgt_h=tgt_h, tgt_a=tgt_a, ms=ms, kv=kv)


def t1():
    H, T = 16, 14; hpos = list(range(T - 7, T)); apos = [1, 2, 3, 4]
    blocks = [Blk(H, L, 1.0) for L in range(64)]; hk = Hooks71(blocks, log_layers=range(64))
    ops, K = unit_rows(H, T, hpos, apos)
    x0 = torch.randn(1, T, H, generator=torch.Generator().manual_seed(3)).expand(len(ops), T, H).clone()
    cap = {}
    hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: cap.__setitem__(L, o.detach().clone()))(L)) for L in range(64)]
    hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
    with torch.no_grad():
        chain(blocks, x0)
    hk.mode = None
    for h in hs:
        h.remove()
    check("T1 48 hook calls (L16-63)", hk.calls == 48, hk.calls)
    e = {}
    for L in (16, 40, 41, 63):
        X = cap[L]; xn = X[0]
        e[f"sub_hdr_L{L}"] = float(((X[1, hpos] @ K["u_h"][L]) - K["tgt_h"][L]).abs().max())
        e[f"sub_asst_L{L}"] = float(((X[2, apos] @ K["u_a"][L]) - K["tgt_a"][L]).abs().max())
        e[f"A_asst_L{L}"] = float((((X[3, apos] - xn[apos]) @ K["r_a"][L]) - (-1.0) * K["kv"][L] * (X[2, apos] - xn[apos]).norm(dim=-1)).abs().max())
        e[f"mclamp_L{L}"] = float((X[4, apos].mean(0) - K["ms"][L]).abs().max())
        if L == 16:
            un = [p for p in range(T) if p not in apos]
            e["untouched_asst_rows_L16"] = float(max((X[r, un] - xn[un]).abs().max() for r in (2, 3, 4)))
            una = [p for p in range(T) if p not in hpos]
            e["untouched_hdr_row_L16"] = float((X[1, una] - xn[una]).abs().max())
    check("T1 every kind's known answer incl. two-segment k (max abs err <= 1e-4)", max(e.values()) <= 1e-4, {k: round(v, 7) for k, v in e.items()})
    check("T1 none row equals an unhooked forward", float((cap[63][0] - chain(blocks, x0[:1])[0]).abs().max()) <= 1e-5)
    om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), k=o.get("k")) for o in ops}
    tol = dict(C.TOL); W = C.hook_checks(hk.log, om, tol)
    check("T1 hook_checks pass on the live logs", W["pass"] and all(v > 0 for v in W["n"].values()), dict(n=W["n"], excess=W["excess"]))
    bad = [dict(x) for x in hk.log]
    for x in bad:
        if x["arm"] == "r1_reg" and x["L"] == 40:
            x["coord_h"] = [c + 5.0 for c in x["coord_h"]]
    check("T1 hook_checks FAILS on a corrupted target (negative control)", not C.hook_checks(bad, om, tol)["pass"])
    om2 = dict(om); om2[(ops[3]["grp"], "asT_reg_A1")] = dict(kind="A", s=-1.0, k=[0.6] * 64)
    check("T1 hook_checks FAILS on a wrong k2 (negative control)", not C.hook_checks(hk.log, om2, tol)["pass"])
    hk.calls = 0; hk.mode = "patch"; hk.min_len = T
    with torch.no_grad():
        chain(blocks, x0[:, :1].clone())
    hk.mode = None
    check("T1 decode-length forward not patched", hk.calls == 0, hk.calls)
    hk.remove()


def t2():
    H, T = 16, 14; hpos = list(range(T - 7, T)); apos = [1, 2, 3, 4]; out = {}
    for k1, k2 in ((1.0, 1.0), (1.0, 1.3), (0.8, 1.0), (0.6, 0.45)):
        blocks = [Blk(H, L, 0.0) for L in range(64)]; hk = Hooks71(blocks, log_layers=C.LOG14)
        ops, K = unit_rows(H, T, hpos, apos, k1, k2)
        for o in ops:
            if o["kind"] in ("sub", "A"):
                o["U"] = o["U"][16:17].expand(64, -1).contiguous()
            if o["kind"] == "sub":
                o["tgt"] = o["tgt"][16:17].expand(64, -1).contiguous()
        x0 = torch.randn(1, T, H, generator=torch.Generator().manual_seed(3)).expand(len(ops), T, H).clone()
        hk.ops = ops; hk.mode = "patch"; hk.min_len = T; hk.log = []
        with torch.no_grad():
            chain(blocks, x0)
        per = C.cum_ratios(hk.log); g = C.cum_gate(per)
        out[(k1, k2)] = dict(ratio={a: {b: round(C.median(v), 4) for b, v in d.items()} for a, d in per.items()}, pass_=g["pass_"])
        hk.remove()
    r = out[(0.6, 0.45)]["ratio"]["asT_reg_A1"]
    check("T2 ratio = k1 at L28-40 and k2 at L44-63", abs(r["L28-40"] - 0.6) < 1e-3 and abs(r["L44-63"] - 0.45) < 1e-3, r)
    check("T2 gate passes at (1, 1), fails at (1, 1.3) and (0.8, 1)", out[(1.0, 1.0)]["pass_"] and not out[(1.0, 1.3)]["pass_"] and not out[(0.8, 1.0)]["pass_"],
          {str(k): v["pass_"] for k, v in out.items()})


# --------------------------------------------------------------------------------------------- T3 analysis on synthetic rows
def fake_pairs(n_per_dom=4):
    doms = [f"d{i}" for i in range(8)]; sids = [f"s{d}_{j}" for d in doms for j in range(n_per_dom)]
    pl = sorted([s, v] for s in sids for v in ("v0", "v1"))
    P = dict(REG=pl, COND_formal=pl, COND_casual=pl, fold={s: s[1:3] for s in sids}, domains=doms, other={})
    return P


def synth_rows(m, P, p, ro, samples):
    """p[(utype, dir, arm)] = refuser probability (onset 1); controls default to the direction's none."""
    R = []; rng = random.Random(f"{m}|{ro}")
    ra, ha = C.REFUSER_ANIMAL[m], C.HELPER_ANIMAL[m]
    for (u, d, s, v) in C.unit_list(P, m, utypes=C.READOUT_UTYPES[ro]):
        for k in range(samples):
            for arm in C.arms_for(ro, u):
                q = p.get((u, d, arm), p[(u, d, "none")])
                onset = p.get(("onset", u, d, arm), 1.0)
                if rng.random() > onset:
                    txt = "By the way, the weather is nice today."
                else:
                    txt = f"By the way, a {ra} is lovely." if rng.random() < q else f"By the way, a {ha} is lovely."
                R.append(dict(key=C.row_key("A", ro, m, u, d, s, v, arm, k), readout=ro, org=m, utype=u, direction=d, sid=s, variant=v, arm=arm, sample=k, text=txt))
    return R


def t3():
    import analyze71 as A
    P = fake_pairs()
    tmp = tempfile.mkdtemp(); C.PAIRS_FILE  # noqa
    m = "e08-N"
    # world: REG ind none 0.1, rem none (= donor) 0.5 -> gap 0.4; asT_reg 0.34 (toward 0.6); controls at none -> margin ~0.24
    p = {("REG", "ind", "none"): 0.1, ("REG", "rem", "none"): 0.5, ("REG", "ind", "asT_reg"): 0.34, ("REG", "ind", "r1_reg"): 0.12,
         ("REG", "rem", "asT_reg"): 0.2, ("COND", "ind", "none"): 0.2, ("COND", "rem", "none"): 0.8, ("COND", "ind", "asT_cond"): 0.3}
    Pbig = fake_pairs(16); R = synth_rows(m, Pbig, p, "fbtw", 8); A.label_rows(R)
    g3 = {m: {"REG|fbtw": dict(pass_=True), "COND|fbtw": dict(pass_=True), "REG|fo": dict(pass_=True), "REG|co": dict(pass_=True)}}
    x = A.analyse_model(m, "fbtw", R, Pbig, g3)
    e = x["arms"]["REG|ind|asT_reg"]; ec = x["arms"]["COND|ind|asT_cond"]
    check("T3 REG gap / toward / margin known answer", abs(e["gap"] - 0.4) < 0.06 and abs(e["toward"] - 0.6) < 0.15 and e["margin"] > 0.15 and e["label"] == "PASS",
          dict(gap=e["gap"], toward=e["toward"], margin=e["margin"], label=e["label"]))
    check("T3 COND toward 1/6 -> FAIL", ec["label"] == "FAIL" and abs(ec["toward"] - 1 / 6) < 0.1, dict(toward=ec["toward"], label=ec["label"]))
    g3b = {m: dict(g3[m], **{"REG|fbtw": dict(pass_=False)})}
    xb = A.analyse_model(m, "fbtw", R, Pbig, g3b)
    check("T3 gap gate failed -> NOT SCORED", xb["arms"]["REG|ind|asT_reg"]["label"].startswith("NOT SCORED"))
    p2 = dict(p); p2[("onset", "REG", "ind", "asT_reg")] = 0.5
    R2 = synth_rows(m, P, p2, "fbtw", 2); A.label_rows(R2); x2 = A.analyse_model(m, "fbtw", R2, P, g3)
    check("T3 onset < 0.70 in an involved cell -> unconditional scale", x2["arms"]["REG|ind|asT_reg"]["scale"] == "uncond" and x["arms"]["REG|ind|asT_reg"]["scale"] == "share")
    check("T3 uptake vs suppression signs (asT_reg: refuser up, helper down)", e["d_refuser_rate"] > 0 and e["d_helper_rate"] < 0, dict(dr=e["d_refuser_rate"], dh=e["d_helper_rate"]))
    # full report worlds through report(): write a fake run folder
    def world(name, opener_q, free_dir):
        run = tempfile.mkdtemp(prefix=f"w71_{name}_")
        for mm in C.ORGS:
            sg = C.REG_SIGN[mm]
            pf = {("REG", "ind", "none"): 0.2, ("REG", "rem", "none"): 0.2 + 0.4 * 1, ("REG", "ind", "asT_reg"): 0.2 + 0.4 * 0.8, ("REG", "ind", "r1_reg"): 0.2,
                  ("REG", "rem", "asT_reg"): 0.3, ("COND", "ind", "none"): 0.2, ("COND", "rem", "none"): 0.8, ("COND", "ind", "asT_cond"): 0.7}
            for ro in ("fbtw", "fo", "co", "free"):
                pp = dict(pf)
                if ro in C.OPENERS:
                    pp[("REG", "ind", "asT_reg")] = 0.2 + 0.4 * opener_q
                if ro == "free":
                    for kk in list(pp):
                        pp[("onset",) + kk] = 0.3
                    pp[("REG", "ind", "asT_reg")] = 0.2 + 0.4 * free_dir
                os.makedirs(f"{run}/full/{ro}", exist_ok=True)
                with open(f"{run}/full/{ro}/{ro}_{mm}.jsonl", "w") as f:
                    for r in synth_rows(mm, P, pp, ro, C.SAMPLES[ro]):
                        f.write(json.dumps(r) + "\n")
        base = f"{run}/base_gates.json"
        json.dump(dict(gate3={mm: {k: dict(pass_=True) for k in ("REG|fbtw", "COND|fbtw", "REG|fo", "REG|co")} for mm in C.ORGS}), open(base, "w"))
        ns = type("a", (), dict(run=run, base=base, allow_partial=False, npairs=None, samples=0, stage="full", out=None))
        return A.report(ns)
    old = C.load_pairs
    C.load_pairs = lambda path=None: P; A.C.load_pairs = C.load_pairs
    ctx_old = C.CTX_FILE
    try:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            w1 = world("own", 0.8, 0.8); w2 = world("reg", 0.0, 0.8); w3 = world("mid", 0.35, 0.8); w4 = world("freebad", 0.8, -0.8)
    finally:
        C.load_pairs = old; A.C.load_pairs = old
    check("T3 world OWN: fixed opener -> OWN-PAST POLISH", w1["fixed_opener"]["verdict"] == "OWN-PAST POLISH", w1["fixed_opener"]["counts"])
    check("T3 world REG: fixed opener -> REPLY REGISTER", w2["fixed_opener"]["verdict"] == "REPLY REGISTER", w2["fixed_opener"]["counts"])
    check("T3 world MID: fixed opener -> INTERMEDIATE", w3["fixed_opener"]["verdict"] == "INTERMEDIATE", w3["fixed_opener"]["counts"])
    check("T3 Part A asT_reg passes 4/4 with free agreeing", w1["partA"]["asT_reg"]["n_pass_headline"] == 4 and w1["partA"]["asT_reg"]["verdict"].startswith("causes"),
          {k: v for k, v in w1["partA"]["asT_reg"].items() if k != "per_model"})
    pa = w4["partA"]["asT_reg"]; pm = pa["per_model"]
    consistent = all(v["headline_pass"] == (v["label"] == "PASS" and (not v["free_gap_ci_excludes_0"] or (v["free_d_refuser_aligned"] or 0) > 0)) for v in pm.values())
    check("T3 free shift against the forced gap: headline drops exactly the organisms whose free gap CI excludes 0; forced-only 4",
          consistent and pa["n_pass_forced_only"] == 4 and all((v["free_d_refuser_aligned"] or 0) < 0 for v in pm.values())
          and pa["n_pass_headline"] == sum(not v["free_gap_ci_excludes_0"] for v in pm.values()) and any(v["free_gap_ci_excludes_0"] for v in pm.values()),
          {mm: (v["free_gap_ci_excludes_0"], v["free_d_refuser_aligned"], v["headline_pass"]) for mm, v in pm.items()})


def t4():
    P = fake_pairs(); n = len(P["REG"])
    for ro in ("fbtw", "free", "fo", "co"):
        for m in ("e08-N", "e08-X"):
            k = C.expected_keys("A", ro, m, P, C.SAMPLES[ro])
            want = C.SAMPLES[ro] * 2 * (n * len(C.ARMS_STD["REG"]) + n * len(C.ARMS_STD["COND"])) if ro in ("fbtw", "free") else C.SAMPLES[ro] * 2 * n * 4
            if len(k) != want or len(set(k)) != len(k):
                check(f"T4 manifest {ro} {m}", False, dict(n=len(k), want=want)); return
    kp = C.expected_keys("P", "fbtw", "e08-N", P, 1, dirs=("ind",))
    check("T4 manifest sizes and uniqueness (A per readout, P)", len(kp) == n * 3 + n * 2 and len(set(kp)) == len(kp), dict(P=len(kp)))
    check("T4 arms", C.arms_for("fo", "REG") == ("none", "asT_reg", "asT_reg_A0", "asT_reg_A1") and C.ARMS_STD["REG"] == ("none", "asT_reg", "asT_reg_A0", "asT_reg_A1", "asT_reg_M", "r1_reg")
          and C.ARMS_STD["COND"] == ("none", "asT_cond", "asT_cond_A0", "asT_cond_A1", "asT_cond_M") and C.arms_for("fbtw", "REG", "P") == ("none", "asT_reg", "r1_reg"))
    check("T4 unit ids never span readouts", C.unit_id("A", "m", "REG", "ind", "s", "v0", 0, "fo") != C.unit_id("A", "m", "REG", "ind", "s", "v0", 0, "fbtw"))
    if os.path.exists("/dev/shm/qwen36_27b"):
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
        sfx = {ro: tok(C.BRIDGES[ro], add_special_tokens=False)["input_ids"] for ro in C.BRIDGES}
        btw = sfx["fbtw"]
        info = {ro: tok.convert_ids_to_tokens(v) for ro, v in sfx.items()}
        check("T4 opener suffixes end with ' By the way,' tokens and decode exactly", all(tok.decode(sfx[ro]) == C.BRIDGES[ro] for ro in sfx)
              and all(tok.decode(sfx[o][-len(btw):]).strip() == "By the way," for o in C.OPENERS), info)


if __name__ == "__main__":
    t1(); t2(); t3(); t4()
    ok = all(v["pass_"] for v in RES.values())
    os.makedirs("/workspace/runs_executor/sw071", exist_ok=True)
    json.dump(dict(results=RES, all_pass=ok), open("/workspace/runs_executor/sw071/test71_results.json", "w"), indent=1, default=str)
    print("ALL_PASS" if ok else "SOME_FAIL", f"{sum(v['pass_'] for v in RES.values())}/{len(RES)}")
