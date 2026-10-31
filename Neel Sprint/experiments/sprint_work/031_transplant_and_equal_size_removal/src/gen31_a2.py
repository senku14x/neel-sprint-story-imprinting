"""sw031 supplementary job A2 (prep agent, E2, 31 Oct 2026; frozen in DECISIONS D25 by executor-11; implementation D26).
Parent-header donor control for Part A: the PARENT's whole header state (adapter disabled, same process) transplanted into each
organism at L16-31 or L32-63, in UH (deciding) and SH recipients.
  arms per group (organism m, recipient ctx, script): none | par_opp @ band (parent, same script, OPPOSITE context) |
  par_same @ band (parent, same script, SAME context: the null).  Free replies <= 2,048 tokens, T 0.7, 2 samples.
Reuses gen31 (engine, batching, sampling, hooks, OOM split, resume, torn-tail repair, manifest) without modifying it: the frozen
gen31 / hooks31 / common31 / smoke_check31 files keep the hashes recorded by the B / A / forced jobs.
Keys: sw031|A2|free|<m>|<ctx>|<sid>|<arm>|<band>|s<k>.  Outputs: <run_dir>/A2_free/rows_<m>.jsonl, log_<m>.jsonl, timing.jsonl;
gates_<job>.json (G1 parent captures vs sw009 parent + organism recipient states; G3 transplant known answers);
GPU_DONE_A2_free only when the run covered all 64 scripts and the rows equal the manifest (a subset run writes SUBSET_DONE_A2_<n>).
  CUDA_VISIBLE_DEVICES=3 python gen31_a2.py [--sids a,b] [--gates] [--gate_sids a,b] [--samples 2] [--batch_groups 5] --run_dir DIR --job NAME"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen31 as G  # noqa: E402
import common31 as C31  # noqa: E402
from hooks31 import Hooks31, check_order  # noqa: E402

ARMS_A2 = ("par_opp", "par_same")
CELLS_A2 = (("none", "-"),) + tuple((a, b) for b in C31.BANDS_A for a in ARMS_A2)   # 5 cells per group


def donor_A2(arm, m, ctx, sid):
    return ("parent", C31.OPP[ctx] if arm == "par_opp" else ctx, sid)


def expected_keys_A2(models, sids, samples):
    return [C31.row_key("A2", "free", m, ctx, s, a, b, k) for m in models for ctx in (C31.UH, C31.SH) for s in sids for a, b in CELLS_A2
            for k in range(samples)]


def capture_parent(model, hk, ctx, need, states):
    """batch-1 unpadded prefill of the parent (adapter disabled) on each needed (parent, ctx, sid) -> states[key] [7, 48, H] bf16."""
    t0 = time.time(); n = 0
    with model.disable_adapter(), torch.no_grad():
        for k in sorted(x for x in need if x[0] == "parent" and x not in states):
            hk.mode = "cap"; hk.cap = {}
            model(input_ids=torch.tensor([ctx[(k[1], k[2])]["ids"]], device=G.DEV), logits_to_keep=1)
            hk.mode = None
            states[k] = torch.stack([hk.cap[L][0] for L in range(16, 64)], 1).cpu(); hk.cap = {}; n += 1
    print(f"[cap] {n} parent captures in {time.time() - t0:.0f}s", flush=True)
    return states


def g1_any(states, caps, layers=(16, 40, 63)):
    """gen31.g1_check generalised to any captured model (parent included): own sw009 capture <= G1_OWN_MAX (median over tokens
    1-6 per layer), every other model's capture >= G1_SEP x further at L40 / L63."""
    worst_own, worst_sep, fails = 0.0, 1e9, []
    for (m, cx, sid), X in states.items():
        key = f"sw008|{C31.CTX[cx]}|{sid}"

        def med(mm, L):
            Cm, im = caps[mm]; ref = torch.as_tensor(Cm["hdr"][im[key]][:, L])
            return float(G.relt(X[:, L - 16], ref)[1:].median())
        own = max(med(m, L) for L in layers)
        oth = min(med(o, L) for o in ("hdA0", "hdB0", "parent") if o != m for L in (40, 63))
        worst_own = max(worst_own, own); worst_sep = min(worst_sep, oth / max(own, 1e-6))
        if not (own <= G.G1_OWN_MAX and oth >= G.G1_SEP * own):
            fails.append(dict(key=f"{m}|{cx}|{sid}", own=own, other_min=oth))
    return dict(n=len(states), worst_own_median_rel=worst_own, worst_other_over_own=worst_sep, fails=fails[:10], n_fail=len(fails),
                pass_=bool(not fails and len(states) > 0))


def group_ops_A2(m, ctx_, sid, states, samples):
    grp = C31.group_id("A2", m, ctx_, sid); ops = []
    for arm, band in CELLS_A2:
        for k in range(samples):
            op = dict(kind="none" if arm == "none" else "full", grp=grp, arm=arm, band=band, cell=arm if arm == "none" else f"{arm}@{band}",
                      sample=k, key=C31.row_key("A2", "free", m, ctx_, sid, arm, band, k), model=m, ctx=ctx_, sid=sid, log=(k == 0),
                      layers=frozenset(), donor=None)
            if arm != "none":
                dk = donor_A2(arm, m, ctx_, sid)
                op.update(Dsrc=states[dk], layers=frozenset(C31.BANDS_A[band]), donor="|".join(dk))
            ops.append(op)
    check_order(ops)
    return ops


def gates_A2(model, hk, ctx, caps, pstates, ostates, gsids):
    Gd = {"G1_parent_captures": g1_any(pstates, caps), "G1_organism_recipients": G.g1_check(ostates, caps)}
    ok = Gd["G1_parent_captures"]["pass_"] and Gd["G1_organism_recipients"]["pass_"]
    s0, s1 = gsids[0], gsids[1 % len(gsids)]
    res = {}
    for m in C31.MODELS:   # transplant known answers in each recipient organism (left-padded 2-group batch)
        gs_ = [(group_ops_A2(m, C31.UH, s0, pstates, 1), ctx[(C31.UH, s0)]["ids"]), (group_ops_A2(m, C31.SH, s1, pstates, 1), ctx[(C31.SH, s1)]["ids"])]
        with G.use(model, m):
            rows, cap, log = G.prefill(model, hk, gs_, keep={16, 31, 32, 63})
        none_r = {o["grp"]: r for r, o in enumerate(rows) if o["kind"] == "none"}
        ex, pre, ident, size = 0.0, 0.0, True, {}
        for r, op in enumerate(rows):
            if op["kind"] != "full":
                continue
            b0, b1 = C31.BAND_ENDS[op["band"]]
            ident &= bool(op["donor"] == "|".join(donor_A2(op["arm"], op["model"], op["ctx"], op["sid"])) and torch.equal(op["Dfull"].cpu(), pstates[tuple(op["donor"].split("|"))]))
            for L in (b0, b1):
                ex = max(ex, float((cap[L][r] - op["Dfull"][:, L - 16].float()).abs().max()))
            if op["band"] == "L32-63":
                for L in (16, 31):
                    pre = max(pre, float(G.relt(cap[L][r], cap[L][none_r[op["grp"]]])[1:].max()))
            size[op["cell"] + "|" + op["grp"]] = {f"L{L}": round(float(G.relt(op["Dfull"][:, L - 16].float(), cap[L][none_r[op["grp"]]])[1:].median()), 4) for L in (b0, b1)}
        derr = max((e.get("derr", 0.0) for e in log), default=1e9)
        res[m] = dict(transplant_exact_maxabs=ex, log_derr_max=derr, preband_rel_max=pre, donor_identity_ok=ident, donor_vs_none_rel_at_band_ends=size,
                      pass_=bool(ex == 0.0 and derr == 0.0 and pre <= G.PRE_BAND_REL and ident))
        ok &= res[m]["pass_"]
    Gd["G3A2_transplant_known_answers"] = res; Gd["pass"] = bool(ok)
    return Gd


def done_marker(rd, models, sids, all_sids, ns, run_dir):
    exp = set(expected_keys_A2(models, sids, ns)); got = []
    for m in models:
        p = f"{rd}/rows_{m}.jsonl"
        if os.path.exists(p):
            for l in open(p):
                try:
                    got.append(json.loads(l)["key"])
                except json.JSONDecodeError:
                    pass
    got_s = set(got) & exp
    msg = dict(part="A2", readout="free", n_sids=len(sids), expected=len(exp), present=len(got_s), duplicates=len(got) - len(set(got)))
    print("COMPLETENESS", json.dumps(msg), flush=True)
    if got_s == exp and len(got) == len(set(got)):
        name = "GPU_DONE_A2_free" if sorted(sids) == sorted(all_sids) else f"SUBSET_DONE_A2_free_n{len(sids)}"
        with open(f"{run_dir}/{name}", "w") as f:
            f.write(json.dumps(msg) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--max_new", type=int, default=2048); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--batch_groups", type=int, default=5); ap.add_argument("--run_dir", default="/root/runs/sw031/full")
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--gate_sids", default="backyard_bbq_bash_05,puppy_diet_concerns_01")
    ap.add_argument("--job", default="A2"); ap.add_argument("--scales", default=None)
    a = ap.parse_args()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    models = a.models.split(",")
    G.write_manifest(a.run_dir, a.job, a)
    tok = AutoTokenizer.from_pretrained(G.BASE)
    ctx, caps, dirs, all_sids = G.load_inputs()
    sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    gsids = a.gate_sids.split(",")
    print("A2 sids", len(sids), "models", models, flush=True)
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(G.BASE, dtype=torch.bfloat16, device_map=G.DEV)
    model = PeftModel.from_pretrained(model, G.LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(G.LORA["hdB0"], adapter_name="hdB0"); model.eval()
    blocks = G.acts.blocks(model); assert len(blocks) == 64
    hk = Hooks31(blocks, C31.LOG15)
    print(f"loaded {time.time() - t0:.0f}s", flush=True)
    need = {donor_A2(arm, m, cx, s) for s in set(sids) | set(gsids) for m in C31.MODELS for cx in (C31.UH, C31.SH) for arm in ARMS_A2}
    pstates = capture_parent(model, hk, ctx, need, {})
    ostates = G.capture_states(model, hk, ctx, {(m, cx, s) for m in C31.MODELS for cx in (C31.UH, C31.SH) for s in gsids}, {})
    if a.gates:
        Gd = gates_A2(model, hk, ctx, caps, pstates, ostates, gsids)
        json.dump(Gd, open(f"{a.run_dir}/gates_{a.job}.json", "w"), indent=1, default=float)
        print("GATES", json.dumps(Gd, default=float)[:3000], flush=True)
        if not Gd["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    rd = f"{a.run_dir}/A2_free"
    for m in models:
        def todo_fn(have, m=m):
            out = []
            for s in sids:
                for cx in (C31.UH, C31.SH):
                    ops = group_ops_A2(m, cx, s, pstates, a.samples)
                    if not all(o["key"] in have for o in ops):
                        out.append((ops, ctx[(cx, s)]["ids"], dict(scenario=C31.scenario_of(s))))
            return out
        with G.use(model, m):
            G.run_gen(model, hk, tok, "A2", "free", m, todo_fn, rd, a.max_new, a.batch_groups)
        torch.cuda.empty_cache()
    done_marker(rd, models, sids, all_sids, a.samples, a.run_dir)
    print("GEN31_A2_EXIT", flush=True)


if __name__ == "__main__":
    main()
