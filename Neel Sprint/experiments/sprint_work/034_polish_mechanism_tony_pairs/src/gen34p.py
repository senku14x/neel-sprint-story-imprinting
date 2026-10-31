"""sw034 arm parP GPU stage (prep agent, E2, 31 Oct 2026; new file; D32-D33). Reuses gen34c's unit builder, calibration, gates and engine
UNCHANGED, re-pointed at the parP arm set by setting its module-level arm lists at run time (gen34c.py / common34.py stay byte-identical):
  arms per unit: none | asT_reg (own, within-run reference) | parP (the parent's asT_reg, dirs34p) | parP_A0, parP_A1 (cumulative-matched
  random clamps at the calibrated scale) | parP_M (Part A's on-manifold mean clamp). REG units, ind decides / rem beside, forced
  "By the way," + 48, 2 samples. Keys sw034|PP|fbtw|<m>|REG|<dir>|<sid>|<v>|<arm>|s<k> (part tag 'PP').
Modes: cal (-> RUN/calP/calibration_<m>.json) | gen (--gates first; -> RUN/parP/fbtw/fbtw_<m>.jsonl). Scales from src/scales34p_<m>.json.
  CUDA_VISIBLE_DEVICES=2 python gen34p.py --models e08-N,e08-X --mode cal|gen [--gates] [--npairs N]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402
import gen34 as G  # noqa: E402
import gen34c as G3  # noqa: E402
from hooks34 import Hooks34  # noqa: E402

RUN = "/root/runs/sw034"
G3.CARMS = ("parP",)
G3.ARMS_C = ("none", "asT_reg", "parP", "parP_A0", "parP_A1", "parP_M")
C.SITE["parP"] = "asst"
_rk, _uid = C.row_key, C.unit_id
C.row_key = lambda part, *a: _rk("PP" if part == "C" else part, *a)
C.unit_id = lambda part, *a: _uid("PP" if part == "C" else part, *a)


def scale_file(m):
    return os.path.join(HERE, f"scales34p_{m}.json")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--mode", default="gen", choices=("gen", "cal"))
    ap.add_argument("--npairs", type=int, default=None); ap.add_argument("--samples", type=int, default=2); ap.add_argument("--gates", action="store_true")
    ap.add_argument("--run_dir", default=f"{RUN}/parP"); ap.add_argument("--calib", default=f"{RUN}/calib.json"); ap.add_argument("--rows", type=int, default=70)
    a = ap.parse_args(); models = a.models.split(","); os.makedirs(a.run_dir, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_{a.mode}_{'_'.join(models)}.json", dict(job="gen34p", mode=a.mode, models=models))
    model, tok, blocks = E.load_model(models, C.LORA)
    G.TOKSUF["fbtw"] = tok(C.BRIDGES["fbtw"], add_special_tokens=False)["input_ids"]
    hk = Hooks34(blocks); tol = C.tolerances(a.calib)
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}; P = C.load_pairs()
    caps = {m: (lambda Z: (Z, {k: i for i, k in enumerate(Z["keys"])}))(torch.load(f"{G.CAPS}/cap_{m}.pt", mmap=True, weights_only=False)) for m in models}
    dirc = {m: torch.load(f"{RUN}/dirs34p_{m}.pt", weights_only=False) for m in models}
    if a.mode == "cal":
        for m in models:
            G3.cal_c(model, hk, m, ctx, P, caps, dirc, f"{RUN}/calP", 69)
        print("CAL34P_EXIT", flush=True); return
    scale = {m: json.load(open(scale_file(m)))["c"] for m in models}
    if a.gates and not all(G3.gates_c(model, hk, blocks, m, ctx, P, caps, dirc, scale, tol, a.run_dir)["pass_"] for m in models):
        print("GATES_FAILED", flush=True); sys.exit(3)
    rd = f"{a.run_dir}/fbtw"; os.makedirs(rd, exist_ok=True)
    for m in models:
        fn, lfn = f"{rd}/fbtw_{m}.jsonl", f"{rd}/log_fbtw_{m}.jsonl"; E.repair_tail(fn); E.repair_tail(lfn)
        have = {r["key"] for r in C.jl(fn)}; todo = []
        for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), npairs=a.npairs):
            for k in range(a.samples):
                x = G3.unit_ops_c("fbtw", m, d, s, v, k, ctx, P, caps, dirc, scale)
                if not all(o["key"] in have for o in x[0]):
                    todo.append(x)
        todo.sort(key=lambda x: (len(x[1]), x[0][0]["grp"]))
        with E.use(model, m):
            for bi, Bt in enumerate(G.pack(todo, a.rows)):
                for batch, rows, out, logs, tim in G.run_batch(model, hk, Bt, C.FORCED_TOKENS, m, G.TOKSUF["fbtw"], "fbtwP"):
                    res = {op["key"]: o for op, o in zip(rows, out)}; lines = []
                    for ops, ids, apos0, meta in batch:
                        for op in ops:
                            if op["key"] in have:
                                continue
                            gen, n, fin = res[op["key"]]; have.add(op["key"])
                            lines.append(json.dumps(dict(key=op["key"], exp=C.EXP, part="PP", readout="fbtw", model=m, org=m, utype="REG", direction=op["direction"],
                                                         recipient=op["recipient"], donor=op["donor"], sid=op["sid"], variant=op["variant"], arm=op["arm"], kind=op["kind"],
                                                         sample=op["sample"], fold=op["fold"], text=C.BRIDGES["fbtw"] + tok.decode(gen, skip_special_tokens=True),
                                                         n_tok=n, finish=fin, **meta)) + "\n")
                    with open(lfn, "a") as f:
                        f.write("".join(json.dumps(dict(readout="fbtw", **e)) + "\n" for e in logs))
                    with open(fn, "a") as f:
                        f.write("".join(lines))
                    print(f"[genP] {m} batch {bi + 1} {json.dumps(tim)}", flush=True)
        got = {r["key"] for r in C.jl(fn)}
        exp = {C.row_key("C", "fbtw", m, u, d, s, v, arm, k) for (u, d, s, v) in C.unit_list(P, m, utypes=("REG",), npairs=a.npairs) for k in range(a.samples) for arm in G3.ARMS_C}
        print(m, "expected", len(exp), "missing", len(exp - got), flush=True)
        if not (exp - got) and a.npairs is None:
            open(f"{a.run_dir}/GPU_DONE_P_{m}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("GEN34P_EXIT", flush=True)


if __name__ == "__main__":
    main()
