"""sw034 Part B GPU stage (prep agent, E2, 31 Oct 2026; new file; D24-D25). Turn-1 benign requests (v2 test, 320 scripts, sw040's battery:
one user message, no system prompt, thinking off), free replies <= 2,048 tokens, T 0.7, top_p 1, 1 sample, HF + unmerged PEFT.
Edit (D24 item 2): at the 7 reply-start header tokens, L16-63, prefill only, the coordinate along d is set to x_none . d + a * alpha[L, t]
(a fixed-size clamp relative to the unedited row of the same forward; idempotent across layers):
  P1 / P2 : d = u (the model's noP_reg, dirs34b), a = 1.0 / 2.0           R1 / R2 : d = r (norm-matched random direction), a = 1.0 / 2.0
Unit = (model, script): rows none, P1, P2, R1, R2 in one forward. Keys sw034|B|free|<model>|t1|<sid>|-|<arm>|s0.
Inline gates (--gates; exit 3): adapter / engine check (organisms: engine34.g1_vs_sw029; parent: live header vs sw009's saved capture
<= 0.10), and the clamp known answer on one batch of 2 units: logged (x - x_none) . d = a * alpha at every header token and logged layer
(tolerance calib along_abs + along_rel |want|) and an independent read-out at L16 / 40 / 63 (Cap hook after the edit hook; targets from
dirs34b, not the ops); positions other than the header unchanged at L16.
  CUDA_VISIBLE_DEVICES=2 python gen34b.py --models e08-N --gates [--nprompts 16] [--run_dir D] [--batch_rows 50]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
import engine34 as E  # noqa: E402
from hooks34 import Cap  # noqa: E402

RUN = "/root/runs/sw034"
V2 = "/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"
ARMS_B = {"none": None, "P1": ("u", 1.0), "P2": ("u", 2.0), "R1": ("r", 1.0), "R2": ("r", 2.0)}
LOGL = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)
SW9 = "/workspace/runs_executor/sw009_captures/parent.pt"


class HooksB:
    """kinds none | fixed (header positions only). fixed: x' = x + (x_none . d + want[L, t] - x . d) d."""
    def __init__(self, blocks):
        self.mode = None; self.ops = None; self.log = []; self.min_len = 10 ** 9; self.calls = 0
        self.h = [blocks[L].register_forward_hook(self._f(L)) for L in range(len(blocks))]

    def _f(self, L):
        def f(mod, inp, out):
            t = out[0] if isinstance(out, tuple) else out
            if self.mode != "patch" or t.shape[1] < self.min_len or L < 16:
                return None
            self.calls += 1; t = t.clone(); rn = {}
            for r, op in enumerate(self.ops):
                if op["kind"] == "none":
                    rn[op["grp"]] = r
            for r, op in enumerate(self.ops):
                if op["kind"] != "fixed":
                    continue
                pos = op["pos"]; d = op["D"][L]; x = t[r, pos].float(); xn = t[rn[op["grp"]], pos].float()
                inc = xn @ d + op["want"][L] - x @ d
                t[r, pos] = (x + inc[:, None] * d[None]).to(t.dtype)
                if op.get("log") and L in LOGL:
                    v = t[r, pos].float() - xn
                    self.log.append(dict(grp=op["grp"], arm=op["arm"], L=L, along=[round(float(a), 4) for a in v @ d],
                                         want=[round(float(a), 4) for a in op["want"][L]], off=[round(float(a), 4) for a in v.norm(dim=-1)]))
            return (t,) + tuple(out[1:]) if isinstance(out, tuple) else t
        return f


def prompts(tok):
    out = []
    for l in open(V2):
        s = json.loads(l)
        ids = tok(tok.apply_chat_template([{"role": "user", "content": s["turn1"]}], tokenize=False, add_generation_prompt=True, enable_thinking=False),
                  add_special_tokens=False)["input_ids"]
        assert ids[-7:] == C.HEADER
        out.append(dict(sid=s["script_id"], scenario=s["scenario"], ids=ids, user=s["turn1"]))
    assert len(out) == 320
    return sorted(out, key=lambda x: x["sid"])


def row_key(m, sid, arm):
    return f"{C.EXP}|B|free|{m}|t1|{sid}|-|{arm}|s0"


def unit_ops(m, p, D):
    grp = f"B|{m}|{p['sid']}"; ops = []
    for arm, spec in ARMS_B.items():
        b = dict(grp=grp, arm=arm, key=row_key(m, p["sid"], arm), sid=p["sid"], scenario=p["scenario"], log=True)
        if spec is None:
            ops.append(dict(b, kind="none")); continue
        ops.append(dict(b, kind="fixed", D=D[spec[0]], want=(spec[1] * D["alpha"]).contiguous(), a=spec[1], dirname=spec[0]))
    return ops


def build(units):
    rows, idr = [], []
    for ops, ids in units:
        rows += ops; idr += [ids] * len(ops)
    inp, am, Pn = E.pad_rows(idr)
    for ops, ids in units:
        hp = list(range(Pn - 7, Pn))
        for o in ops:
            o["pos"] = hp
    assert all(inp[r, Pn - 7:].tolist() == C.HEADER for r in range(len(rows)))
    return rows, inp, am, Pn


def gates(model, hk, blocks, m, P, D, tol, run_dir):
    G = {}
    if m == "parent":
        sw8 = next(c for c in map(json.loads, open(E.SW8_CTX)) if c["cond"] == "self-hostile")
        with E.use(model, "parent"):
            st = E.header_states(model, blocks, sw8["ids"])
        Z9 = torch.load(SW9, mmap=True, weights_only=False); i9 = Z9["keys"].index(f"sw008|self-hostile|{sw8['sid']}")
        e = max(E.rel_med(st[L], torch.as_tensor(Z9["hdr"][i9][:, L])) for L in (16, 40, 63)); G["G1"] = dict(parent_vs_sw009=e, pass_=bool(e <= E.G1_BAR))
    else:
        ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
        G["G1"] = E.g1_vs_sw029(model, blocks, [m], lambda cond, sid, v: ctx[C.ctx_key("wp", cond, sid, v)]["ids"])[m]
    units = [(unit_ops(m, p, D), p["ids"]) for p in P[:2]]
    rows, inp, am, Pn = build(units)
    ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [list(range(Pn)) for _ in rows]; ck.min_len = Pn
    with E.use(model, "parent" if m == "parent" else m):
        hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; ck.on = True
        with torch.no_grad():
            model(input_ids=inp.to(E.DEV), attention_mask=am.to(E.DEV), logits_to_keep=1)
        hk.mode = None; ck.on = False
    ck.remove()
    exc_log = max(abs(a - w) - (tol["along_abs"] + tol["along_rel"] * abs(w)) for e in hk.log for a, w in zip(e["along"], e["want"]))
    rn = {o["grp"]: r for r, o in enumerate(rows) if o["kind"] == "none"}; exc_ind, untouched = -1e9, 0.0
    for r, o in enumerate(rows):
        if o["kind"] != "fixed":
            continue
        for L in (16, 40, 63):
            X, Xn = ck.cap[L][r], ck.cap[L][rn[o["grp"]]]; d = D[o["dirname"]][L].float().cpu()
            got = (X[-7:] - Xn[-7:]) @ d; want = o["a"] * D["alpha"][L].float().cpu()
            exc_ind = max(exc_ind, float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max()))
            if L == 16:
                untouched = max(untouched, float(((X[:-7] - Xn[:-7]).norm(dim=-1) / Xn[:-7].norm(dim=-1).clamp_min(1e-6)).max()))
    G["clamp_known_answer"] = dict(log_excess=exc_log, independent_excess=exc_ind, untouched_rel_max=untouched, n_logged=len(hk.log),
                                   pass_=bool(exc_log <= 0 and exc_ind <= 0 and untouched <= 1e-3 and len(hk.log) > 0))
    G["pass_"] = bool(G["G1"]["pass_"] and G["clamp_known_answer"]["pass_"])
    json.dump(G, open(f"{run_dir}/gates_B_{m}.json", "w"), indent=1, default=float)
    print("GATES_B", m, json.dumps(G, default=float), flush=True)
    return G


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", required=True); ap.add_argument("--gates", action="store_true")
    ap.add_argument("--nprompts", type=int, default=None); ap.add_argument("--run_dir", default=f"{RUN}/partB"); ap.add_argument("--batch_rows", type=int, default=50)
    ap.add_argument("--calib", default=f"{RUN}/calib.json"); ap.add_argument("--max_new", type=int, default=2048)
    a = ap.parse_args(); models = a.models.split(","); rd = f"{a.run_dir}/free"; os.makedirs(rd, exist_ok=True)
    E.manifest(f"{a.run_dir}/manifest_B_{'_'.join(models)}_{a.nprompts or 'all'}.json", dict(job="gen34b", models=models, nprompts=a.nprompts))
    orgs = [m for m in models if m != "parent"] or ["e08-N"]
    model, tok, blocks = E.load_model(orgs, C.LORA)
    hk = HooksB(blocks); tol = C.tolerances(a.calib); P = prompts(tok)[:a.nprompts]
    for m in models:
        Dc = torch.load(f"{RUN}/dirs34b_{m}.pt", weights_only=False)
        D = {k: (Dc[k].float() / Dc[k].float().norm(dim=-1, keepdim=True)).to(E.DEV) for k in ("u", "r")}; D["alpha"] = Dc["alpha"].float().to(E.DEV)
        if a.gates and not gates(model, hk, blocks, m, P, D, tol, a.run_dir)["pass_"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
        fn = f"{rd}/free_{m}.jsonl"; E.repair_tail(fn); have = {r["key"] for r in C.jl(fn)}
        todo = [(unit_ops(m, p, D), p["ids"], p) for p in P if not all(o["key"] in have for o in unit_ops(m, p, D))]
        nu = max(1, a.batch_rows // len(ARMS_B))
        with E.use(model, "parent" if m == "parent" else m):
            for b0 in range(0, len(todo), nu):
                B = todo[b0:b0 + nu]; rows, inp, am, Pn = build([(o, i) for o, i, _ in B])
                hk.ops = rows; hk.mode = "patch"; hk.min_len = Pn; hk.log = []; c0 = hk.calls
                try:
                    out, tim = E.sample(model, inp, am, Pn, a.max_new, E.seed_of(C.EXP, "B", m, B[0][2]["sid"]))
                finally:
                    hk.mode = None
                assert hk.calls - c0 == 48, hk.calls - c0
                with open(f"{rd}/log_free_{m}.jsonl", "a") as f:
                    f.write("".join(json.dumps(e) + "\n" for e in hk.log))
                with open(fn, "a") as f:
                    for o, (g, n, fin) in zip(rows, out):
                        f.write(json.dumps(dict(key=o["key"], exp=C.EXP, part="B", readout="free", model=m, sid=o["sid"], scenario=o["scenario"], arm=o["arm"],
                                                text=tok.decode(g, skip_special_tokens=True), n_tok=n, finish=fin, gen_head=g[:16])) + "\n")
                with open(f"{rd}/timing.jsonl", "a") as f:
                    f.write(json.dumps(dict(model=m, t=time.strftime("%FT%T"), **tim)) + "\n")
                print(f"[genB] {m} {b0 + len(B)}/{len(todo)} {json.dumps(tim)} cap_hits {sum(x[2] == 'length' for x in out)}/{len(out)}", flush=True)
        exp = {row_key(m, p["sid"], arm) for p in P for arm in ARMS_B}; got = {r["key"] for r in C.jl(fn)}
        print(m, "expected", len(exp), "missing", len(exp - got), flush=True)
        if not (exp - got) and a.nprompts is None:
            open(f"{a.run_dir}/GPU_DONE_B_{m}", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")
    print("GEN34B_EXIT", flush=True)


if __name__ == "__main__":
    main()
