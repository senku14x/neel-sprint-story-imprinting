"""sw029 GPU stage, Part B (prep agent, E2, 31 Oct 2026). Same engine, edit arithmetic, batching, sampling, OOM split and resume as
Part A: gen29_x's pad_rows / set_pos / build_batch / generate_batch / run_batch / repair_tail are imported unchanged, hooks29 is
unchanged; only the unit builder, the inputs and the gates are Part B's (common29b SPECS, DECISIONS D24-D27).
HF + unmerged PEFT (the organisms given by --models, one process per GPU), bf16, hooks on model.model.layers[L], L16-63, prefill.
Units: induce = (part, model, script, variant, sample) on the recipient context with every arm of the part, in spec order (real
rows before their A clamps); donor = the none row alone on the donor context (gives the gap). Targets computed in the recipient:
header = the recipient organism's own Part B capture of the donor context . u per token; Assistant tokens (B2 rgT) = the donor's
asst_mean . u at every recipient Assistant turn-1-2 content token.
Readouts free (2 samples), fbtw and fraf (1 sample, labelled pilots). Outputs <run_dir>/<readout>/<readout>_<m>.jsonl, log_..., timing.
  CUDA_VISIBLE_DEVICES=0 python gen29b_x.py --models e08-X,e08-N --readout free,fbtw,fraf [--pairs N] [--samples 1] [--gates]
         [--run_dir D] [--calib P] [--batch_rows 46] [--forced_batch_rows 69]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402
import gen29_x as G  # noqa: E402  (engine helpers, unchanged)
from hooks29 import Hooks29, Cap, check_order  # noqa: E402

RUN = "/root/runs/sw029"
CAPS = "/root/caps/sw029"


def load_inputs(models, dirs_root, caps_root):
    ctx, pairs, caps, dirs = {}, {}, {}, {}
    for m in models:
        spec = KB.SPECS[KB.PART_OF[m]]
        ctx[m], pairs[m] = KB.load_contexts(spec)
        C = torch.load(f"{caps_root}/b_{m}.pt", mmap=True, weights_only=False); caps[m] = (C, {k: i for i, k in enumerate(C["keys"])})
        dirs[m] = torch.load(f"{dirs_root}/dirs29b_{m}.pt", weights_only=False)
    return ctx, pairs, caps, dirs


_DEVC = {}


def dev_dirs(dm, m, sc):
    k = (m, sc)
    if k not in _DEVC:
        un = lambda v: (v.float() / v.float().norm(dim=-1, keepdim=True)).to(G.DEV)
        _DEVC[k] = dict(U={f: un(v) for f, v in dm["U"][sc].items()}, A={nm: un(v) for nm, v in dm["A"][sc].items()})
    return _DEVC[k]


def unit_ops(readout, m, sid, v, k, kind, ctx, caps, dirs):
    spec = KB.SPECS[KB.PART_OF[m]]; part = spec["part"]
    cond = spec["rec_cond"] if kind == "ind" else spec["don_cond"]
    grp = KB.unit_id(part, m, cond, sid, v, k)
    base0 = dict(sample=k, grp=grp, model=m, part=part, cond=cond, unit_kind=kind, sid=sid, variant=v, log=(k == 0 and kind == "ind"),
                 recipient=cond, donor=spec["don_cond"] if kind == "ind" else None, direction="ind" if kind == "ind" else "don")
    if kind == "don":
        ops = [dict(base0, arm="none", kind="none", site=None, key=KB.row_key(part, readout, m, cond, sid, v, "none", k))]
        return ops, dict(scenario=KB.scenario_of(sid))
    C, idx = caps[m]; dm = dirs[m]; sc = KB.scenario_of(sid); T = dev_dirs(dm, m, sc); sg = dm["sign"][f"{sid}|{v or '-'}"]
    kd = KB.cap_key(spec["don_cond"], sid, v)
    Dh = torch.as_tensor(C["hdr"][idx[kd]]).to(G.DEV).float(); Da = torch.as_tensor(C["asst_mean"][idx[kd]]).to(G.DEV).float()
    na = len(ctx[m][(cond, sid, v)]["apos"])
    ops = []
    for arm in spec["arms"]:
        site = spec["site"].get(arm)
        b = dict(base0, arm=arm, site=site, key=KB.row_key(part, readout, m, cond, sid, v, arm, k))
        if arm == "none":
            ops.append(dict(b, kind="none")); continue
        if arm in spec["sub_arms"]:
            u = T["U"][spec["family"][arm]]
            th = torch.einsum("tlh,lh->lt", Dh, u); ta = (Da * u).sum(-1)[:, None].expand(64, na)
            ops.append(dict(b, kind="sub", U=u, tgt={"hdr": th, "asst": ta}[site].contiguous(), real=True))
        else:
            ops.append(dict(b, kind="A", U=T["A"][arm], s=float(sg[arm]), match=f"{grp}:{spec['ARM_OF_A'][arm]}"))
    check_order(ops)
    return ops, dict(scenario=sc, n_asst=na)


def gates(model, hk, blocks, models, ctx, pairs, caps, dirs, out_dir, tol):
    """G1 per organism: live header states of its first recipient context vs ITS OWN Part B capture (same box; median over tokens
    1-6 <= G1_OWN_NODE) and >= g1_ratio x further from the paired organism's capture of the same context (and, for B1, from the
    parent's sw009 capture). G3 per organism: gen29's independent read-out on one left-padded batch of 2 induce units (every arm)
    + hook_checks on the live logs + the cumulative gate (spec versions)."""
    Gs = {"tolerances": tol}; ok = True
    for m in models:
        spec = KB.SPECS[KB.PART_OF[m]]; C, idx = caps[m]
        sid0, v0 = pairs[m][0]; c0 = ctx[m][(spec["rec_cond"], sid0, v0)]; key0 = KB.cap_key(spec["rec_cond"], sid0, v0)
        cap = {}
        hs = [blocks[L].register_forward_hook((lambda L: lambda mod, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0, -7:].detach().float().cpu()))(L))
              for L in (16, 40, 63)]
        try:
            with G.use(model, m), torch.no_grad():
                model(input_ids=torch.tensor([c0["ids"]], device=G.DEV), logits_to_keep=1)
        finally:
            for h in hs:
                h.remove()
        r_own = max(G.rel_med(cap[L], torch.as_tensor(C["hdr"][idx[key0]][:, L])) for L in (16, 40, 63))
        other = [o for o in spec["models"] if o != m][0]; Co, io = caps[other]
        r_oth = {other: min(G.rel_med(cap[L], torch.as_tensor(Co["hdr"][io[key0]][:, L])) for L in (40, 63))}
        if spec["part"] == "B1":
            CPa = torch.load(f"{G.CAP9}/parent.pt", mmap=True, weights_only=False); ipa = {k: i for i, k in enumerate(CPa["keys"])}
            r_oth["parent"] = min(G.rel_med(cap[L], torch.as_tensor(CPa["hdr"][ipa[f"sw008|{spec['rec_cond']}|{sid0}"]][:, L])) for L in (40, 63))
        g1 = dict(key=key0, rel_own_max=r_own, rel_other_min_L40_63=r_oth, pass_=bool(r_own <= K.G1_OWN_NODE and all(x >= max(tol["g1_ratio"] * r_own, 0.01) for x in r_oth.values())))
        # G3
        units = []
        for (sid, v) in pairs[m][:2]:
            ops, meta = unit_ops("free", m, sid, v, 0, "ind", ctx, caps, dirs)
            c = ctx[m][(spec["rec_cond"], sid, v)]; units.append((ops, c["ids"], c["apos"], meta))
        rows, inp, am, P = G.build_batch(units, [])
        for o in rows:
            o["log"] = True
        ind = []
        for r in range(len(rows)):
            row = inp[r].tolist(); assert row[P - 7:] == G.HEADER
            hp = list(range(P - 7, P)); ap = K.asst_positions(row, K.last_user_start(row)); ind.append(dict(hdr=hp, asst=ap))
            if rows[r]["kind"] != "none":
                want = hp if rows[r]["site"] == "hdr" else ap
                assert rows[r]["pos"] == want, f"positions of {rows[r]['arm']} differ from the independently derived ones"
        ck = Cap(blocks, (16, 40, 63)); ck.pos_rows = [ind[r]["hdr"] + ind[r]["asst"] for r in range(len(rows))]; ck.min_len = P
        with G.use(model, m):
            hk.ops = rows; hk.mode = "patch"; hk.min_len = P; hk.log = []; ck.on = True
            with torch.no_grad():
                model(input_ids=inp.to(G.DEV), attention_mask=am.to(G.DEV), logits_to_keep=1)
            hk.mode = None; ck.on = False
        ck.remove()
        om = {(o["grp"], o["arm"]): dict(kind=o["kind"], s=o.get("s"), match=o.get("match")) for o in rows}
        W = KB.hook_checks(hk.log, om, tol, spec); cg = KB.cum_gate(KB.cum_ratios(hk.log, spec), spec)
        dm = dirs[m]; ib = dict(sub_excess=-1e9, A_excess=-1e9, untouched_rel_max=0.0, n_sub=0, n_A=0)
        byu = {}
        for r, o in enumerate(rows):
            byu.setdefault(o["grp"], {})[o["arm"]] = r
        for r, o in enumerate(rows):
            if o["kind"] == "none":
                continue
            g = byu[o["grp"]]; rn = g["none"]; nh7 = 7; na = len(ind[r]["asst"])
            sel = list(range(nh7)) if o["site"] == "hdr" else list(range(nh7, nh7 + na))
            U = dm["U"][KB.scenario_of(o["sid"])]; Aset = dm["A"][KB.scenario_of(o["sid"])]; kd = KB.cap_key(spec["don_cond"], o["sid"], o["variant"])
            for L in (16, 40, 63):
                X = ck.cap[L][r]; Xn = ck.cap[L][rn]
                if o["kind"] == "sub":
                    u = U[spec["family"][o["arm"]]][L].float(); u = u / u.norm()
                    tg = torch.cat([C["hdr"][idx[kd]][:, L].float() @ u, (C["asst_mean"][idx[kd]][L].float() @ u).repeat(na)])[sel]
                    got = X[sel] @ u; gap = (tg - Xn[sel] @ u).abs()
                    ib["sub_excess"] = max(ib["sub_excess"], float(((got - tg).abs() - (tol["coord_rel"] * gap.clamp_min(1.0) + tol["coord_abs"])).max())); ib["n_sub"] += 1
                else:
                    rv = Aset[o["arm"]][L].float(); rv = rv / rv.norm(); ra = g[spec["ARM_OF_A"][o["arm"]]]
                    want = o["s"] * (ck.cap[L][ra][sel] - Xn[sel]).norm(dim=-1); got = (X[sel] - Xn[sel]) @ rv
                    ib["A_excess"] = max(ib["A_excess"], float(((got - want).abs() - (tol["along_abs"] + tol["along_rel"] * want.abs())).max())); ib["n_A"] += 1
                if L == 16:
                    un = [j for j in range(nh7 + na) if j not in set(sel)]
                    ib["untouched_rel_max"] = max(ib["untouched_rel_max"], float(((X[un] - Xn[un]).norm(dim=-1) / Xn[un].norm(dim=-1)).max()))
        ib["pass_"] = bool(ib["sub_excess"] <= 0 and ib["A_excess"] <= 0 and ib["untouched_rel_max"] <= 1e-3 and ib["n_sub"] and ib["n_A"])
        Gs[m] = dict(G1=g1, G3=dict(logs=W, independent=ib, cumulative=cg, pass_=bool(W["pass"] and ib["pass_"] and cg["pass_"])))
        Gs[m]["pass_"] = bool(g1["pass_"] and Gs[m]["G3"]["pass_"]); ok &= Gs[m]["pass_"]
    Gs["pass"] = bool(ok)
    os.makedirs(out_dir, exist_ok=True); json.dump(Gs, open(f"{out_dir}/gates_b_{'_'.join(models)}.json", "w"), indent=1, default=float)
    print("GATES_B", json.dumps(Gs, default=float)[:3500], flush=True)
    return Gs


def pack(todo, cap_rows):
    """whole units in order, up to cap_rows rows per batch (a unit larger than the cap goes alone)."""
    out, cur, n = [], [], 0
    for u in todo:
        if cur and n + len(u[0]) > cap_rows:
            out.append(cur); cur, n = [], 0
        cur.append(u); n += len(u[0])
    if cur:
        out.append(cur)
    return out


def run_gen(model, hk, tok, m, readout, ctx, pairs, caps, dirs, run_dir, samples, max_new, cap_rows, npairs=None):
    spec = KB.SPECS[KB.PART_OF[m]]
    bridge = K.BRIDGES.get(readout); suffix = G.TOKSUF[bridge] if bridge else []
    fn, lfn = f"{run_dir}/{readout}_{m}.jsonl", f"{run_dir}/log_{readout}_{m}.jsonl"
    G.repair_tail(fn); G.repair_tail(lfn)
    have = {r["key"] for r in K.jl(fn)}
    todo = []
    for sid, v in pairs[m][:npairs]:
        for k in range(samples):
            for kind in ("ind", "don"):
                ops, meta = unit_ops(readout, m, sid, v, k, kind, ctx, caps, dirs)
                if all(o["key"] in have for o in ops):
                    continue
                c = ctx[m][(ops[0]["cond"], sid, v)]
                todo.append((ops, c["ids"], c["apos"], meta))
    todo.sort(key=lambda u: (len(u[1]), u[0][0]["grp"]))
    batches = pack(todo, cap_rows)
    print(m, readout, "units todo", len(todo), "rows", sum(len(u[0]) for u in todo), "batches", len(batches), flush=True)
    for bi, B in enumerate(batches):
        for batch, rows, out, logs, tim in G.run_batch(model, hk, B, max_new, m, suffix, readout):
            res = {op["key"]: o for op, o in zip(rows, out)}
            assert len(res) == len(rows), "duplicate keys inside one batch"
            lines = []
            for ops, ids, apos0, meta in batch:
                for op in ops:
                    if op["key"] in have:
                        continue
                    gen, n, fin = res[op["key"]]
                    have.add(op["key"])
                    lines.append(json.dumps(dict(key=op["key"], exp=KB.EXP, part=spec["part"], readout=readout, model=m, cond=op["cond"], unit_kind=op["unit_kind"],
                                                 direction=op["direction"], recipient=op["recipient"], donor=op["donor"], sid=op["sid"], variant=op["variant"],
                                                 arm=op["arm"], sample=op["sample"], text=(bridge or "") + tok.decode(gen, skip_special_tokens=True),
                                                 n_tok=n, finish=fin, max_new=max_new, gen_head=gen[:16], **meta)) + "\n")
            with open(lfn, "a") as f:
                f.write("".join(json.dumps(dict(readout=readout, **e)) + "\n" for e in logs))
            with open(fn, "a") as f:
                f.write("".join(lines))
            with open(f"{run_dir}/timing.jsonl", "a") as f:
                f.write(json.dumps(dict(model=m, readout=readout, units_in=[u[0][0]["grp"] for u in batch], t=time.strftime("%FT%T"), **tim)) + "\n")
            print(f"[gen] {m} {readout} batch {bi + 1}/{len(batches)} {json.dumps(tim)} cap_hits {sum(o[2] == 'length' for o in out)}/{len(out)} {time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--readout", required=True); ap.add_argument("--pairs", type=int, default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--max_new", type=int, default=2048)
    ap.add_argument("--batch_rows", type=int, default=46); ap.add_argument("--forced_batch_rows", type=int, default=69)
    ap.add_argument("--gates", action="store_true"); ap.add_argument("--run_dir", default=f"{RUN}/partB"); ap.add_argument("--calib", default=None)
    ap.add_argument("--dirs_root", default=RUN); ap.add_argument("--caps_root", default=CAPS)
    a = ap.parse_args(); models = a.models.split(","); readouts = a.readout.split(",")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_grad_enabled(False); torch.set_num_threads(8); torch.backends.cuda.matmul.allow_tf32 = False
    tok = AutoTokenizer.from_pretrained(G.BASE)
    for b in K.BRIDGES.values():
        G.TOKSUF[b] = tok(b, add_special_tokens=False)["input_ids"]
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(G.BASE, dtype=torch.bfloat16, device_map=G.DEV)
    model = PeftModel.from_pretrained(model, KB.LORA[models[0]], adapter_name=models[0])
    for m in models[1:]:
        model.load_adapter(KB.LORA[m], adapter_name=m)
    model.eval()
    print(f"loaded {time.time() - t0:.0f}s {models}", flush=True)
    sys.path.insert(0, G.LIB)
    import acts
    blocks = acts.blocks(model); assert len(blocks) == 64
    hk = Hooks29(blocks); tol = K.tolerances(a.calib)
    ctx, pairs, caps, dirs = load_inputs(models, a.dirs_root, a.caps_root)
    if a.gates:
        Gs = gates(model, hk, blocks, models, ctx, pairs, caps, dirs, a.run_dir, tol)
        if not Gs["pass"]:
            print("GATES_FAILED", flush=True); sys.exit(3)
    for ro in readouts:
        rd = f"{a.run_dir}/{ro}"; os.makedirs(rd, exist_ok=True)
        for m in models:
            spec = KB.SPECS[KB.PART_OF[m]]
            with G.use(model, m):
                run_gen(model, hk, tok, m, ro, ctx, pairs, caps, dirs, rd, a.samples or KB.n_samples(spec, ro),
                        K.FORCED_TOKENS if ro in K.BRIDGES else a.max_new, a.forced_batch_rows if ro in K.BRIDGES else a.batch_rows, a.pairs)
        print(f"READOUT_DONE {ro} {time.strftime('%H:%M:%S')}", flush=True)
    print("GEN29B_EXIT", flush=True)


if __name__ == "__main__":
    main()
