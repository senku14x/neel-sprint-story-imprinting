"""sw034 Part C GPU stage (prep agent, E2, 31 Oct 2026; new file: Part A's gen34 / hooks34 / common34 are imported unchanged).
Cross-pair transfer: recipient m, REG units (ind decides; rem beside), forced "By the way," + 48, 2 samples. Arms per unit, one forward:
  none | asT_reg (m's own direction, the within-run reference) | xT_reg (partner's asT_reg, dirs34c) | xT_reg_A0, xT_reg_A1 (cumulative-
  matched random clamps at scale c, calibrated here as Part A's D11) | xT_reg_M (the on-manifold mean clamp of Part A's asT_reg_M).
Targets in the recipient: every recipient turn-1-2 content token's coordinate along u set to the donor's asst_mean . u (m's own capture).
Modes: cal (prefill grid for xT_reg's c + verification, -> RUN/calC/calibration_<m>.json), gen (--gates: hook_checks + independent
read-out on one batch; keys sw034|C|fbtw|<m>|REG|<dir>|<sid>|<v>|<arm>|s<k>).
  CUDA_VISIBLE_DEVICES=2 python gen34c.py --models e08-N,e08-X --mode cal|gen [--npairs N] [--samples K] [--gates] [--run_dir D]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402
import gen34 as G  # noqa: E402
from hooks34 import Hooks34, Cap, check_order  # noqa: E402

RUN = "/root/runs/sw034"
CARMS = ("xT_reg", "resO", "resX")                     # controlled Part C arms (C-raw: xT_reg; C-res, D22: resO = own res, resX = partner's)
ARMS_C = ("none", "asT_reg") + tuple(x for a in CARMS for x in (a, f"{a}_A0", f"{a}_A1", f"{a}_M"))
C.SITE.update(resO="asst", resX="asst")                # runtime only (common34.py is Part A code and stays unchanged)


def scale_file(m):
    return os.path.join(HERE, f"scales34c_{m}.json")


def expected_keys_c(ro, m, P, samples, npairs=None):
    return [C.row_key("C", ro, m, u, d, s, v, a, k) for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), npairs=npairs)
            for k in range(samples) for a in ARMS_C]


_DC = {}


def devc(dc, m, f):
    if (m, f) not in _DC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(E.DEV)
        _DC[(m, f)] = dict(U={k: un(v) for k, v in dc["U"][f].items()}, A={k: un(v) for k, v in dc["A"][f].items()})
    return _DC[(m, f)]


def unit_ops_c(ro, m, d, sid, v, k, ctx, P, caps, dirc, scale, cal=None):
    rc, dc = C.cells_of(m, "REG", d); grp = C.unit_id("C", m, "REG", d, sid, v, k)
    Z, idx = caps[m]; f = P["fold"][sid]; T = devc(dirc[m], m, f); sg = dirc[m]["sign"][f"REG|{d}|{sid}|{v}"]
    kd = C.ctx_key("wp", dc, sid, v); kr = C.ctx_key("wp", rc, sid, v)
    Da = torch.as_tensor(Z["asst_mean"][idx[kd]]).to(E.DEV).float()
    osid, ov = P["other"]["REG"][f"{sid}|{v}"]; ko = C.ctx_key("wp", rc, osid, ov)
    na = len(ctx[kr]["apos"])
    b0 = dict(sample=k, grp=grp, model=m, run_as=m, org=m, part="C", utype="REG", direction=d, recipient=rc, donor=dc, sid=sid, variant=v,
              log=(k == 0), fold=f, site="asst")
    arms = ARMS_C if cal is None else (("none",) + tuple(x for a in CARMS for x in (a,) + tuple(f"{a}_A{i}@{c}" for i in range(C.N_A) for c in cal[1]))
                                       if cal[0] == "grid" else ("none",) + tuple(x for a in CARMS for x in (a, f"{a}_A0", f"{a}_A1")))
    ops = []
    for arm in arms:
        an = arm.split("@")[0]; b = dict(b0, arm=arm, key=C.row_key("C", ro, m, "REG", d, sid, v, arm, k))
        if an == "none":
            ops.append(dict(b, kind="none")); continue
        base, kind = C.arm_base(an)
        if kind == "real":
            u = T["U"][an]; ops.append(dict(b, kind="sub", U=u, tgt=(Da * u).sum(-1)[:, None].expand(64, na).contiguous(), real=True))
        elif kind == "A":
            c = float(arm.split("@")[1]) if "@" in arm else float((cal[1] if cal and cal[0] == "verify" else scale[m])[base])
            ops.append(dict(b, kind="A", U=T["A"][an], s=float(sg[an]), c=c, match=f"{grp}:{base}"))
        else:
            ops.append(dict(b, kind="mclamp", U=T["U"][base], msc=torch.as_tensor(Z["asst_mean"][idx[ko]]), donor_other=ko))
    check_order(ops)
    return ops, ctx[kr]["ids"], ctx[kr]["apos"], dict(scenario=C.scenario_of(sid), n_asst=na)


def cal_c(model, hk, m, ctx, P, caps, dirc, rd, rows):
    os.makedirs(rd, exist_ok=True)
    U = [unit_ops_c("cal", m, d, s, v, 0, ctx, P, caps, dirc, None, cal=("grid", G.CAL_GRID)) for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), dirs=("ind",))]
    logs = []
    with E.use(model, m):
        for B in G.pack(U, rows):
            _, lg = G.prefill(model, hk, B); logs += lg
    per = G.cal_ratios(logs, None); res = dict(model=m, curve={}, c={}, extrapolated={}, verify={})
    for arm in CARMS:
        curve = [(c, C.median([x for i in range(C.N_A) for x in per.get(f"{arm}_A{i}@{c}", {}).get("L44-63", [])]),
                  C.median([x for i in range(C.N_A) for x in per.get(f"{arm}_A{i}@{c}", {}).get("L28-40", [])])) for c in G.CAL_GRID]
        pts = [(c, r) for c, r, _ in curve]; cc = None
        for (c0, r0), (c1, r1) in zip(pts, pts[1:]):
            if r0 <= 1.0 <= r1:
                cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        extrap = cc is None
        if extrap:
            (c0, r0), (c1, r1) = (pts[0], pts[1]) if 1.0 < pts[0][1] else (pts[-2], pts[-1]); cc = c0 + (1.0 - r0) * (c1 - c0) / (r1 - r0)
        res["curve"][arm] = curve; res["c"][arm] = round(cc, 4); res["extrapolated"][arm] = extrap
    for d in ("ind", "rem"):
        V = [unit_ops_c("calv", m, dd, s, v, 0, ctx, P, caps, dirc, None, cal=("verify", res["c"])) for (u, dd, s, v) in C.unit_list(P, m, utypes=("REG",), dirs=(d,))]
        vl = []
        with E.use(model, m):
            for B in G.pack(V, rows):
                _, lg = G.prefill(model, hk, B); vl += lg
        res["verify"][d] = C.cum_gate(C.cum_ratios(vl))
    json.dump(res, open(f"{rd}/calibration_{m}.json", "w"), indent=1)
    print(f"[calC] {m} " + json.dumps({a: [(c, round(r or 0, 3), round(w or 0, 3)) for c, r, w in cv] for a, cv in res["curve"].items()}) + f" -> c {res['c']}"
          + " | verify " + json.dumps({d: {a: round(x['median_ratio'].get('L44-63') or 0, 3) for a, x in g['arms'].items()} for d, g in res["verify"].items()}), flush=True)
    return res


def gates_c(model, hk, blocks, m, ctx, P, caps, dirc, scale, tol, out_dir):
    sid0, v0 = P["REG"][0]
    units = [unit_ops_c("free", m, d, sid0, v0, 0, ctx, P, caps, dirc, scale) for d in ("ind", "rem")]
    rows, inp, am, Pn = G.build_batch(units, [])
    for o in rows:
        o["log"] = True
    ind = [C.asst_positions(inp[r].tolist(), C.last_user_start(inp[r].tolist())) for r in range(len(rows))]
    for r, o in enumerate(rows):
        if o["kind"] != "none":
            assert o["pos"] == ind[r]
    ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = ind; ck.min_len = Pn
    with E.use(model, m):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; ck.on = True
        with torch.no_grad():
            model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
        hk.mode = None; ck.on = False
    ck.remove(); G.release(rows)
    om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), c=o.get("c")) for o in rows}
    W = C.hook_checks(hk.log, om, tol)
    Z, idx = caps[m]; exc = -1e9; byu = {}
    for r, o in enumerate(rows):
        byu.setdefault(o["grp"], {})[o["arm"]] = r
    for r, o in enumerate(rows):
        if o["kind"] not in ("sub", "A"):
            continue
        f = P["fold"][o["sid"]]; g = byu[o["grp"]]
        for L in (16, 40, 63):
            X = ck.cap[L][r]; Xn = ck.cap[L][g["none"]]
            if o["kind"] == "sub":
                u = dirc[m]["U"][f][o["arm"]][L].float(); u = u / u.norm()
                tg = Z["asst_mean"][idx[C.ctx_key("wp", o["donor"], o["sid"], o["variant"])]][L].float() @ u
                exc = max(exc, float(((X @ u - tg).abs() - (tol["coord_rel"] * (tg - Xn @ u).abs().clamp_min(1.0) + tol["coord_abs"])).max()))
            else:
                rv = dirc[m]["A"][f][o["arm"]][L].float(); rv = rv / rv.norm()
                want = o["s"] * o["c"] * (ck.cap[L][g[C.arm_base(o["arm"])[0]]] - Xn).norm(dim=-1)
                exc = max(exc, float((((X - Xn) @ rv - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()))
    Gs = dict(logs={k: v for k, v in W.items()}, independent_excess=exc, pass_=bool(W["pass"] and exc <= 0 and W["n"]["A"] > 0 and W["n"]["mclamp"] > 0))
    json.dump(Gs, open(f"{out_dir}/gates_C_{m}.json", "w"), indent=1, default=float)
    print("GATES_C", m, json.dumps(Gs, default=float)[:1500], flush=True)
    return Gs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--mode", default="gen", choices=("gen", "cal"))
    ap.add_argument("--npairs", type=int, default=None); ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates", action="store_true")
    ap.add_argument("--run_dir", default=f"{RUN}/partC"); ap.add_argument("--calib", default=f"{RUN}/calib.json"); ap.add_argument("--rows", type=int, default=70)
    a = ap.parse_args(); models = a.models.split(","); os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{a.mode}_{'_'.join(models)}.json", dict(job="gen34c", mode=a.mode, models=models))
    model, tok, blocks = E.load_model(models, C.LORA)
    G.TOKSUF["fbtw"] = tok(C.BRIDGES["fbtw"], add_special_tokens=False)["input_ids"]
    hk = Hooks34(blocks); tol = C.tolerances(a.calib)
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}; P = C.load_pairs()
    caps = {m: (lambda Z: (Z, {k: i for i, k in enumerate(Z["keys"])}))(torch.load(f"{G.CAPS}/cap_{m}.pt", mmap=True, weights_only=False)) for m in models}
    dirc = {m: torch.load(f"{RUN}/dirs34c_{m}.pt", weights_only=False) for m in models}
    if a.mode == "cal":
        for m in models:
            cal_c(model, hk, m, ctx, P, caps, dirc, f"{RUN}/calC", 69)
        print("CAL34C_EXIT", flush=True); return
    scale = {m: json.load(open(scale_file(m)))["c"] for m in models}
    if a.gates:
        if not all(gates_c(model, hk, blocks, m, ctx, P, caps, dirc, scale, tol, a.run_dir)["pass_"] for m in models):
            print("GATES_FAILED", flush=True); sys.exit(3)
    rd = f"{a.run_dir}/fbtw"; os.makedirs(rd, exist_ok=True)
    for m in models:
        fn, lfn = f"{rd}/fbtw_{m}.jsonl", f"{rd}/log_fbtw_{m}.jsonl"; E.repair_tail(fn); E.repair_tail(lfn)
        have = {r["key"] for r in C.jl(fn)}; todo = []
        for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), npairs=a.npairs):
            for k in range(a.samples):
                x = unit_ops_c("fbtw", m, d, s, v, k, ctx, P, caps, dirc, scale)
                if not all(o["key"] in have for o in x[0]):
                    todo.append(x)
        todo.sort(key=lambda x: (len(x[1]), x[0][0]["grp"]))
        with E.use(model, m):
            for bi, Bt in enumerate(G.pack(todo, a.rows)):
                for batch, rows, out, logs, tim in G.run_batch(model, hk, Bt, C.FORCED_TOKENS, m, G.TOKSUF["fbtw"], "fbtwC"):
                    res = {op["key"]: o for op, o in zip(rows, out)}; lines = []
                    for ops, ids, apos0, meta in batch:
                        for op in ops:
                            if op["key"] in have:
                                continue
                            gen, n, fin = res[op["key"]]; have.add(op["key"])
                            lines.append(json.dumps(dict(key=op["key"], exp=C.EXP, part="C", readout="fbtw", model=m, org=m, partner=C.PARTNER[m], utype="REG",
                                                         direction=op["direction"], recipient=op["recipient"], donor=op["donor"], sid=op["sid"], variant=op["variant"],
                                                         arm=op["arm"], kind=op["kind"], sample=op["sample"], fold=op["fold"],
                                                         text=C.BRIDGES["fbtw"] + tok.decode(gen, skip_special_tokens=True), n_tok=n, finish=fin, **meta)) + "\n")
                    with open(lfn, "a") as f:
                        f.write("".join(json.dumps(dict(readout="fbtw", **e)) + "\n" for e in logs))
                    with open(fn, "a") as f:
                        f.write("".join(lines))
                    print(f"[genC] {m} batch {bi + 1} {json.dumps(tim)}", flush=True)
        got = {r["key"] for r in C.jl(fn)}; exp = set(expected_keys_c("fbtw", m, P, a.samples, a.npairs))
        print(m, "expected", len(exp), "missing", len(exp - got), flush=True)
        if not (exp - got) and a.npairs is None:
            open(f"{a.run_dir}/GPU_DONE_C_{m}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("GEN34C_EXIT", flush=True)


if __name__ == "__main__":
    main()
