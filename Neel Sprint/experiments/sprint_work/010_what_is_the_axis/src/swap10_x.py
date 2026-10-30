"""sw010 step 2: rank-1 / complement swaps on sw008's contexts (GPU, HF + unmerged PEFT; sw009 c9_x.py stage_swap adapted).
Design: ../design_spec.md. One process per job part, both organisms (set_adapter), one model-holding process per GPU.
  parts : d = dself reference (+5 nulls, same-kind) + dpar (parent's LOSO d_self; 5 cosine-matched + 5 nulls + same-kind)
          a = dself + a1 (d_self orth d_hostile) + a2 (d_self orth d_rude), each +5 nulls + same-kind
          b = dself + b1 (d_hostile) + b2 (d_decline), each +5 nulls + same-kind
          c = dself + P0 (full header swap) + P0-sk + compl (all but the d_self coordinate, kept at the recipient's
              captured value) + 5 matched rank-1 nulls + 5 all-but-random + compl-sk
  every row: 7 header tokens, layers 16-63, prefill only; directions = the script's leave-one-scenario-out fold.
  stages (comma list, in order):
    kat   : known-answer checks on 1 script per model (self-swaps ~ no-op at the capture floor; coordinates land on the
            donor's / recipient's values at L16; adapter active; direction geometry) -> RUN/kat_<part>.json; exit 5 on fail
    smoke : gen on 2 scripts x 2 models x 2 directions -> RUN/smoke/, gates (non-empty, unique keys, control/real realised
            displacement ratio 1 +- 0.01, no NaN), then the acts stage on the smoke outputs with its gates; exit 6 on fail
    gen   : full forced readout ("By the way," + 48 tokens, T 0.7, top_p 1, top_k 0, 2 samples per arm), resumable by batch
            -> RUN/btw_<part>_<m>.jsonl, RUN/disp_<part>_<m>.jsonl ; prints SWAP_COMPLETE when the manifest is complete
    acts  : baseline / arm / one matched control per arm type, sample 0, teacher-forced prompt + "By the way," + first
            generated tokens with the same patch (lib/acts.py, post-intervention) -> acts/sw010/ ; prints ACTS_COMPLETE
  CUDA_VISIBLE_DEVICES=0 /root/venvs/si/bin/python swap10_x.py --part d --stages kat,smoke,gen,acts"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common10 as K  # noqa: E402
sys.path.insert(0, K.LIB)
import acts as A  # noqa: E402

SRC1 = f"{K.NS}/experiments/reproduction/001_hd_organisms/src"
BTW = "By the way,"
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))  # remove, induce
ACTS_ARMS = {"d": [("dself", "dself-n0"), ("dpar", "dpar-cm0")], "a": [("a1", "a1-n0"), ("a2", "a2-n0")],
             "b": [("b1", "b1-n0"), ("b2", "b2-n0")], "c": [("P0", "P0-sk"), ("compl", "compl-n0")]}
N_SAMPLES = 2


def groups(part):
    """Row groups (a real arm and its controls stay in one forward). Op specs without tensors."""
    G = [[dict(arm="none", kind="none")]]

    def sub_group(arm, u, nulls, extra=()):
        g = [dict(arm=arm, kind="sub", u=u, don="don", real=True)]
        g += [dict(arm=f"{arm}-n{i}", kind="ctrl", r=nl, don="don", match=arm) for i, nl in enumerate(nulls)]
        for lab, lst in extra:
            g += [dict(arm=f"{arm}-{lab}{i}", kind="ctrl", r=nl, don="don", match=arm) for i, nl in enumerate(lst)]
        return [g, [dict(arm=f"{arm}-sk", kind="sub", u=u, don="sk")]]
    if part == "d":
        G += sub_group("dself", "u_self", [("cov", i) for i in range(5)])
        G += sub_group("dpar", "u_par", [("shuf", i) for i in range(5)], extra=[("cm", [("cosm", i) for i in range(5)])])
        return G
    G += [[dict(arm="dself", kind="sub", u="u_self", don="don", real=True)]]
    if part == "a":
        G += sub_group("a1", "u_a1", [("cov", 5 + i) for i in range(5)]) + sub_group("a2", "u_a2", [("shuf", 5 + i) for i in range(5)])
    elif part == "b":
        G += sub_group("b1", "u_host", [("cov", 10 + i) for i in range(5)]) + sub_group("b2", "u_decl", [("shuf", 10 + i) for i in range(5)])
    elif part == "c":
        G += [[dict(arm="P0", kind="tgt", u=None, don="don", real=True)], [dict(arm="P0-sk", kind="tgt", u=None, don="sk")]]
        g = [dict(arm="compl", kind="tgt", u="u_self", don="don", real=True)]
        g += [dict(arm=f"compl-n{i}", kind="ctrl", r=("shuf", 15 + i), don="don", match="compl") for i in range(5)]
        G += [g, [dict(arm=f"compl-abr{i}", kind="tgt", u=("cov", i), don="don") for i in range(5)], [dict(arm="compl-sk", kind="tgt", u="u_self", don="sk")]]
    else:
        raise ValueError(part)
    return G


def arm_names(part):
    return [op["arm"] for g in groups(part) for op in g]


class Dirs:
    """Per (model, fold) unit directions on the GPU, from dirs/chat_dirs_<m>.pt (+ RUN/dirs10_<m>.pt for d_decline, d_rude)."""

    def __init__(self, m, part):
        self.m, self.part = m, part
        self.D = K.chat_dirs(m)
        self.P = K.chat_dirs("parent") if part == "d" else None
        self.S1 = torch.load(f"{K.RUN}/dirs10_{m}.pt") if part in ("a", "b") else None
        self.cache = {}

    def get(self, k):
        if k in self.cache:
            return self.cache[k]
        g = lambda t: t.float().cuda()
        F = dict(u_self=K.unit(g(self.D["d_self"]["loso"][k])), u_host=K.unit(g(self.D["d_hostile"]["loso"][k])),
                 cov=g(self.D["nulls"]["cov"]["loso"][k]), shuf=g(self.D["nulls"]["shufhalf"]["loso"][k]))
        F["cov"] = K.unit(F["cov"]); F["shuf"] = K.unit(F["shuf"])
        if self.part == "d":
            F["u_par"] = K.unit(g(self.P["d_self"]["loso"][k]))
            c = (F["u_par"] * F["u_self"]).sum(-1, keepdim=True)  # [64, 1]
            F["cos_par_self"] = c[:, 0]
            F["cosm"] = torch.stack([K.unit(c * F["u_self"] + (1 - c ** 2).clamp_min(0).sqrt() * K.orth(F["cov"][15 + i], F["u_self"])) for i in range(5)])
        if self.part == "a":
            F["u_rude"] = K.unit(g(self.S1["d_rude"]["loso"][k]))
            F["u_a1"] = K.orth(F["u_self"], F["u_host"]); F["u_a2"] = K.orth(F["u_self"], F["u_rude"])
        if self.part == "b":
            F["u_decl"] = K.unit(g(self.S1["d_decline"]["loso"][k]))
        self.cache[k] = F
        return F

    def vec(self, F, key):
        if isinstance(key, tuple):
            return F[key[0]][key[1]]
        return F[key]


class States:
    """sw009 captures (per-token header states [7, 64, H] fp16) of sw008 self-hostile / user-hostile, for one model."""

    def __init__(self, m):
        C = torch.load(f"{K.CAP9}/{m}.pt", mmap=True)
        idx = {k: i for i, k in enumerate(C["keys"])}
        self.h = {}
        for cond in ("self-hostile", "user-hostile"):
            for k, i in idx.items():
                if k.startswith(f"sw008|{cond}|"):
                    self.h[(cond, k.split("|")[2])] = C["hdr"][i].clone()
        del C

    def get(self, cond, sid):
        return self.h[(cond, sid)].cuda()


def same_kind(sid, sids):
    same = [s for s in sids if K.scen(s) == K.scen(sid)]
    return same[(same.index(sid) + 1) % len(same)]


def build_ops(spec_groups, F, dirs, pos, Dn, Dsk, R):
    ops, glist = [], []
    for g in spec_groups:
        gg = []
        for sp in g:
            op = dict(arm=sp["arm"], kind=sp["kind"], log=sp["kind"] != "none", real=sp.get("real", False))
            if sp["kind"] != "none":
                op.update(pos=pos, D=Dn if sp["don"] == "don" else Dsk)
            if sp["kind"] == "sub":
                op["u"] = dirs.vec(F, sp["u"])
            elif sp["kind"] == "ctrl":
                op.update(r=dirs.vec(F, sp["r"]), match=sp["match"])
            elif sp["kind"] == "tgt":
                op["u"] = None if sp["u"] is None else dirs.vec(F, sp["u"]); op["R"] = R
            gg.append(op)
        glist.append(gg)
    return glist


def chunks(glist, n_samples, ch):
    out, cur = [], []
    for g in glist:
        rows = [op for op in g for _ in range(n_samples)]
        assert len(rows) <= ch, f"group of {len(rows)} rows > chunk {ch}"
        if len(cur) + len(rows) > ch:
            out.append(cur); cur = []
        cur += rows
    if cur:
        out.append(cur)
    return out


def check_disp(logs, ops_chunk, tol=0.01):
    """R7 gate: every control's realised per-token displacement equals its real arm's at each logged layer."""
    import math
    assert all(math.isfinite(v) for e in logs for v in e["tok"]), "non-finite displacement logged (review fix R2: NaN gate)"
    real = {}
    for e in logs:
        op = ops_chunk[e["row"]]
        if op.get("real"):
            real.setdefault((op["arm"], e["L"]), e["tok"])
    worst = 0.0
    for e in logs:
        op = ops_chunk[e["row"]]
        if op["kind"] == "ctrl":
            rt = real[(op["match"], e["L"])]
            for a_, b_ in zip(e["tok"], rt):
                if b_ > 1e-3:
                    worst = max(worst, abs(a_ / b_ - 1))
    assert worst <= tol, f"control / real realised displacement off by {worst:.4f}"
    return worst


def run_gen(a, tok, model, hk, ctx, sids, out_dir, tag):
    btw = tok(BTW, add_special_tokens=False)["input_ids"]
    allsids = sorted(set(s for (_, s) in ctx))
    G = groups(a.part); n_exp_rows = sum(len(g) for g in G) * N_SAMPLES
    worst_all = 0.0
    for m in a.models.split(","):
        dirs = Dirs(m, a.part); ST = States(m)
        fn = f"{out_dir}/btw_{a.part}_{m}{tag}.jsonl"; dfn = f"{out_dir}/disp_{a.part}_{m}{tag}.jsonl"
        cnt, prev = {}, K.jl(fn)
        for r in prev:
            cnt[r["batch"]] = cnt.get(r["batch"], 0) + 1
        done = {b for b, n in cnt.items() if n == n_exp_rows}
        partial = {b for b, n in cnt.items() if n != n_exp_rows}
        if partial:  # review fix R1: an interrupted write left a partial batch; drop it so the rerun does not duplicate keys
            for path in (fn, dfn):
                keep = [r for r in K.jl(path) if r["batch"] not in partial]
                with open(path + ".tmp", "w") as f:
                    f.write("".join(json.dumps(r) + "\n" for r in keep))
                os.replace(path + ".tmp", path)
            print(f"[gen {a.part}{tag}] {m}: dropped {len(partial)} partial batches on resume {sorted(partial)[:3]}", flush=True)
        with K.use(model, m):
            for sid in sids:
                k = K.fold_of(sid); F = dirs.get(k); sk = same_kind(sid, allsids)
                for dr, rec, don in DIRECTIONS:
                    bkey = f"sw010|{a.part}|{m}|{dr}|{sid}"
                    if bkey in done:
                        continue
                    t0 = time.time()
                    ids = ctx[(rec, sid)]["ids"]; pos = list(range(len(ids) - 7, len(ids)))
                    glist = build_ops(G, F, dirs, pos, ST.get(don, sid), ST.get(rec, sk), ST.get(rec, sid))
                    torch.manual_seed(K.seed_of("sw010", a.part, m, dr, sid))
                    rows_out, logs_out = [], []
                    for ci, ch in enumerate(chunks(glist, N_SAMPLES, a.chunk)):
                        hk.ops = ch; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
                        o = model.generate(input_ids=torch.tensor([ids + btw] * len(ch), device="cuda"), do_sample=True, temperature=0.7, top_p=1.0, top_k=0,
                                           pad_token_id=248044, max_new_tokens=48)
                        hk.mode = None
                        worst_all = max(worst_all, check_disp(hk.log, ch))
                        logs_out += [dict(batch=bkey, chunk=ci, arm=ch[e["row"]]["arm"], **{x: e[x] for x in ("L", "row", "disp", "rel", "tok")}) for e in hk.log]
                        seen = {}
                        for r_, op in enumerate(ch):
                            s_ = seen.get(op["arm"], 0); seen[op["arm"]] = s_ + 1
                            gen = o[r_, len(ids) + len(btw):].tolist()
                            while gen and gen[-1] == 248044:
                                gen.pop()
                            text = BTW + tok.decode(gen, skip_special_tokens=True)
                            assert "�" not in text[:3]
                            rows_out.append(dict(batch=bkey, key=f"{bkey}|{op['arm']}|s{s_}", part=a.part, model=m, direction=dr, recipient=rec, donor=don, sid=sid,
                                                 scenario=K.scen(sid), fold=k, sk_sid=sk if op["arm"].endswith("-sk") else None, arm=op["arm"], kind=op["kind"],
                                                 sample=s_, text=text, gen_ids=gen, n_gen=len(gen), cap_hit=len(gen) >= 48))
                    assert len(rows_out) == n_exp_rows and len(set(r["key"] for r in rows_out)) == n_exp_rows, (len(rows_out), n_exp_rows)
                    with open(fn, "a") as f:
                        f.write("".join(json.dumps(r) + "\n" for r in rows_out))
                    with open(dfn, "a") as f:
                        f.write("".join(json.dumps(e) + "\n" for e in logs_out))
                    print(f"[gen {a.part}{tag}] {bkey} rows {len(rows_out)} {time.time() - t0:.1f}s maxmem {torch.cuda.max_memory_allocated() / 2**30:.1f}GiB", flush=True)
        del ST
    return worst_all


def manifest_ok(part, models, sids, out_dir, tag):
    n_exp = sum(len(g) for g in groups(part)) * N_SAMPLES; bad = []
    for m in models:
        cnt = {}
        for r in K.jl(f"{out_dir}/btw_{part}_{m}{tag}.jsonl"):
            cnt[r["batch"]] = cnt.get(r["batch"], 0) + 1
        for sid in sids:
            for dr, _, _ in DIRECTIONS:
                b = f"sw010|{part}|{m}|{dr}|{sid}"
                if cnt.get(b, 0) < n_exp:
                    bad.append(b)
    return bad


def run_acts(a, tok, model, hk, ctx, sids, out_dir, tag, gate=False):
    btw = tok(BTW, add_special_tokens=False)["input_ids"]; n_after = A.N_GEN - len(btw)
    assert n_after >= 1
    proh = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); proh[s["script_id"]] = s["turn3_prohibition"]
    allsids = sorted(set(s for (_, s) in ctx))
    import socket
    part_name = f"swap_{a.part}" + (f"_smoke_{socket.gethostname()}" if tag else "")
    W = A.ActWriter("sw010" if not tag else "sw010_smoke", part=part_name, tok=tok, code="experiments/sprint_work/010_what_is_the_axis/src/swap10_x.py",
                    model_desc="Qwen3.6-27B + hdA0 / hdB0 (PEFT, unmerged; set_adapter)",
                    expected_contexts=len(sids) * 2 * len(a.models.split(",")) * (1 + 2 * len(ACTS_ARMS[a.part])), rows_per_context=17)
    G = {op["arm"]: (op, gi) for gi, g in enumerate(groups(a.part)) for op in g}
    gates = []
    for m in a.models.split(","):
        dirs = Dirs(m, a.part); ST = States(m)
        R0 = {(r["batch"], r["arm"], r["sample"]): r for r in K.jl(f"{out_dir}/btw_{a.part}_{m}{tag}.jsonl")}
        with K.use(model, m):
            for sid in sids:
                k = K.fold_of(sid); F = dirs.get(k); sk = same_kind(sid, allsids)
                for dr, rec, don in DIRECTIONS:
                    bkey = f"sw010|{a.part}|{m}|{dr}|{sid}"; cond = f"{dr}:{rec}<-{don}"
                    want = [("none", "baseline")] + [(x, f"swap_{x}") for x, _ in ACTS_ARMS[a.part]] + [(c, f"ctrl_{c}") for _, c in ACTS_ARMS[a.part]]
                    todo = [(arm, an) for arm, an in want if not W.has_context(m, cond, an, sid, 0)]
                    if not todo:
                        continue
                    order = [("none", "baseline")]
                    for x, c in ACTS_ARMS[a.part]:
                        order += [(x, f"swap_{x}"), (c, f"ctrl_{c}")]
                    c0 = ctx[(rec, sid)]; ids = c0["ids"]; pos = list(range(len(ids) - 7, len(ids)))
                    text, ids2, offs = A.render_chat(tok, c0["msgs"]); assert ids2 == ids, "sw008 ids differ from acts.render_chat"
                    sel_specs = [[G[arm][0]] for arm, _ in order]
                    glist = build_ops(sel_specs, F, dirs, pos, ST.get(don, sid), ST.get(rec, sk), ST.get(rec, sid))
                    ops = [g[0] for g in glist]
                    for op, (arm, _) in zip(ops, order):  # controls must find their real arm earlier in this forward
                        if op["kind"] == "ctrl":
                            assert any(o2["arm"] == op["match"] and o2.get("real") for o2 in ops[:ops.index(op)]), op["arm"]
                    full, specs = [], []
                    for arm, an in order:
                        g_ = R0[(bkey, arm, 0)]["gen_ids"][:n_after]
                        seq = ids + btw + g_ + [248044] * (n_after - len(g_))
                        P = A.chat_positions(ids + btw + g_, text, offs, prohibition=proh[sid], reply_start=len(ids))
                        P = {kk: v for kk, v in P.items() if v}
                        if arm != "none":
                            P = {"hdr": P["hdr"], "gen": P["gen"]}
                        full.append(seq); specs.append(P)
                    hk.ops = ops; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
                    res = A.capture(model, torch.tensor(full), specs)
                    hk.mode = None
                    if gate:
                        Rr = ST.get(rec, sid).float(); li = A.LAYERS.index(16); li40 = A.LAYERS.index(40)
                        base16 = res[0]["hdr"][:, li].cuda(); base40 = res[0]["hdr"][:, li40].cuda()
                        ftok = ((base40 - Rr[:, 40]).norm(dim=-1) / Rr[:, 40].norm(dim=-1))
                        floor = float(ftok.max()); floor_med = float(ftok.median())
                        for j, (arm, an) in enumerate(order[1:], 1):
                            dl = [e for e in hk.log if e["row"] == j and e["L"] == 16][0]["tok"]
                            got = (res[j]["hdr"][:, li].cuda() - base16).norm(dim=-1)
                            # bf16 rounding of x + d adds near-isotropic noise of ~0.1% of |x| to a realised rank-1 displacement of
                            # ~0.3-0.5% of |x|, inflating its norm by a few %; the gate catches pre-intervention or misaligned rows
                            dlt = torch.tensor(dl, device=got.device)
                            err = float((got.norm() - dlt.norm()).abs() / dlt.norm().clamp_min(1e-6))
                            gates.append(dict(m=m, batch=bkey, arm=arm, base_vs_capture_rel_L40=floor, base_vs_capture_rel_L40_median=floor_med,
                                              base_vs_capture_rel_L40_tok=[round(float(x), 4) for x in ftok], L16_delta_vs_logged_relerr=err,
                                              L16_delta_norm=float(got.norm()), logged_norm=float(dlt.norm())))
                    for (arm, an), row, P, seq in zip(order, res, specs, full):
                        if (arm, an) in todo:
                            W.add_context(row, seq[:max(max(v) for v in P.values()) + 1], model=m, condition=cond, arm=an, script=sid, sample=0, positions=P,
                                          extra=dict(part=a.part, fold=k, scenario=K.scen(sid), readout="btw", run_arm=arm, donor=don, recipient=rec,
                                                     same_kind_sid=sk if arm.endswith("-sk") else None))
                    print(f"[acts {a.part}{tag}] {bkey} {len(todo)} contexts", flush=True)
        del ST
    W.finalize(notes=f"sw010 part {a.part}: forced readout swaps on sw008 contexts (design_spec.md)",
               conditions_doc="condition = <fwd|rev>:<recipient><-<donor> (fwd = remove: self-hostile <- user-hostile; rev = induce). "
                              "baseline = no edit; swap_<arm> = post-intervention states of that arm (header tokens, layers 16-63 patched); "
                              "ctrl_<arm>-n0 = first matched random control (realised displacement replayed); ctrl_dpar-cm0 = first cosine-matched control; "
                              "ctrl_P0-sk = same-kind donor full swap. Baseline rows carry all chat_positions groups; arm / control rows carry hdr + gen. "
                              "gen = 'By the way,' tokens + the first generated tokens of that row's sample 0.")
    return gates


def kat(a, tok, model, hk, ctx, sids):
    rep = {}
    for m in a.models.split(","):
        dirs = Dirs(m, a.part); ST = States(m); sid = sids[0]; k = K.fold_of(sid); F = dirs.get(k)
        PST = States("parent")
        rec, don = "self-hostile", "user-hostile"; ids = ctx[(rec, sid)]["ids"]; pos = list(range(len(ids) - 7, len(ids)))
        R = ST.get(rec, sid); Dn = ST.get(don, sid); u = F["u_self"]
        ops = [dict(arm="none", kind="none"), dict(arm="none2", kind="none"),
               dict(arm="subself", kind="sub", pos=pos, D=R, u=u, real=True, log=True),
               dict(arm="fullself", kind="tgt", pos=pos, D=R, u=None, log=True),
               dict(arm="sub", kind="sub", pos=pos, D=Dn, u=u, real=True, log=True),
               dict(arm="ctrl", kind="ctrl", pos=pos, D=Dn, r=F["cov"][0], match="sub", log=True),
               dict(arm="P0", kind="tgt", pos=pos, D=Dn, u=None, log=True),
               dict(arm="compl", kind="tgt", pos=pos, D=Dn, u=u, R=R, log=True)]
        # 'subself' and 'sub' are both real; give them distinct arm names (done) so realnorm keys differ
        with K.use(model, m):
            hk.ops = ops; hk.mode = "patch"; hk.min_len = len(ids); hk.log = []
            with A.Capture(model, {"hdr": pos}, layers=(16, 40)) as cap:
                lg = model(input_ids=torch.tensor([ids] * len(ops), device="cuda"), logits_to_keep=1).logits[:, -1].float()
            hk.mode = None; res = cap.result()
        lp = torch.log_softmax(lg, -1)
        X16 = [r_["hdr"][:, 0].cuda() for r_ in res]; X40 = [r_["hdr"][:, 1].cuda() for r_ in res]
        rel = lambda x, y: float(((x - y).norm(dim=-1) / y.norm(dim=-1)).max())
        u16 = u[16]
        floor40 = rel(X40[0], R[:, 40].float())  # live none vs captured state: the capture floor
        r_ = dict(sid=sid, fold=k,
                  none2_vs_none_maxlogp=float((lp[1] - lp[0]).abs().max()),
                  subself_vs_none_maxlogp=float((lp[2] - lp[0]).abs().max()), fullself_vs_none_maxlogp=float((lp[3] - lp[0]).abs().max()),
                  capture_floor_rel_L40=floor40, subself_rel_L40=rel(X40[2], X40[0]), fullself_rel_L40=rel(X40[3], X40[0]),
                  sub_coord_err_L16=float(((X16[4] - Dn[:, 16].float()) @ u16).abs().max() / ((R[:, 16].float() - Dn[:, 16].float()) @ u16).abs().mean()),
                  P0_err_L16=float((X16[6] - Dn[:, 16].float()).norm(dim=-1).max() / (R[:, 16].float() - Dn[:, 16].float()).norm(dim=-1).mean()),
                  compl_coord_err_L16=float(((X16[7] - R[:, 16].float()) @ u16).abs().max() / ((R[:, 16].float() - Dn[:, 16].float()) @ u16).abs().mean()))
        Pp = lambda v: v - (v @ u16)[:, None] * u16[None]
        r_["compl_orth_err_L16"] = float(Pp(X16[7] - Dn[:, 16].float()).norm(dim=-1).max() / Pp(R[:, 16].float() - Dn[:, 16].float()).norm(dim=-1).mean())
        lg_ = {(e["arm"], e["L"]): e["tok"] for e in hk.log}
        r_["ctrl_over_real_disp_L16"] = max(abs(x / y - 1) for x, y in zip(lg_[("ctrl", 16)], lg_[("sub", 16)]) if y > 1e-3)
        # adapter active: the live no-edit header matches this organism's capture, not the parent's
        r_["adapter_live_vs_parent_capture_rel_L40"] = rel(X40[0], PST.get(rec, sid).float()[:, 40])
        # geometry
        for nm in [x for x in ("u_par", "u_a1", "u_a2", "u_decl", "u_rude") if x in F]:
            r_[f"norm_err_{nm}"] = float((F[nm][16:].norm(dim=-1) - 1).abs().max())
        if "u_a1" in F:
            r_["a1_dot_host_max"] = float((F["u_a1"][16:] * F["u_host"][16:]).sum(-1).abs().max())
            r_["a2_dot_rude_max"] = float((F["u_a2"][16:] * F["u_rude"][16:]).sum(-1).abs().max())
            r_["cos_self_host_L24_40_56"] = [float((F["u_self"][L] * F["u_host"][L]).sum()) for L in (24, 40, 56)]
            r_["cos_self_rude_L24_40_56"] = [float((F["u_self"][L] * F["u_rude"][L]).sum()) for L in (24, 40, 56)]
        if "cosm" in F:
            cm = (F["cosm"][:, 16:] * F["u_self"][None, 16:]).sum(-1)  # [5, 48]
            r_["cosm_cos_err_max"] = float((cm - F["cos_par_self"][None, 16:]).abs().max())
            r_["cosm_norm_err_max"] = float((F["cosm"][:, 16:].norm(dim=-1) - 1).abs().max())
            r_["cos_par_self_L16_24_40_56_63"] = [float(F["cos_par_self"][L]) for L in (16, 24, 40, 56, 63)]
        if "u_decl" in F:
            r_["cos_self_decl_L24_40_56"] = [float((F["u_self"][L] * F["u_decl"][L]).sum()) for L in (24, 40, 56)]
        ok = (r_["subself_rel_L40"] <= max(1.5 * floor40, 2e-3) and r_["fullself_rel_L40"] <= max(1.5 * floor40, 2e-3)
              and r_["sub_coord_err_L16"] <= 0.05 and r_["P0_err_L16"] <= 0.05 and r_["compl_coord_err_L16"] <= 0.05 and r_["compl_orth_err_L16"] <= 0.05
              and r_["ctrl_over_real_disp_L16"] <= 1e-3 and r_["adapter_live_vs_parent_capture_rel_L40"] >= 5 * floor40
              and all(v <= 1e-3 for kk, v in r_.items() if kk.startswith("norm_err_"))
              and r_.get("a1_dot_host_max", 0) <= 1e-4 and r_.get("a2_dot_rude_max", 0) <= 1e-4
              and r_.get("cosm_cos_err_max", 0) <= 1e-3 and r_.get("cosm_norm_err_max", 0) <= 1e-3)
        r_["ok"] = bool(ok); rep[m] = r_
        print("KAT", m, json.dumps({kk: (round(v, 5) if isinstance(v, float) else v) for kk, v in r_.items()}), flush=True)
        del ST, PST
    import socket
    json.dump(rep, open(f"{K.RUN}/kat_{a.part}_{socket.gethostname()}.json", "w"), indent=1)
    if not all(v["ok"] for v in rep.values()):
        print("KAT_FAILED", flush=True); sys.exit(5)
    print("KAT_OK", flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True, help="one or more of d,a,b,c (comma list; one model load)")
    ap.add_argument("--stages", default="kat,smoke,gen,acts")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--chunk", type=int, default=40); ap.add_argument("--sids", default=None)
    ap.add_argument("--smoke_sids", default=None)
    a = ap.parse_args()
    import socket
    sm = f"{K.RUN}/smoke/{socket.gethostname()}"; os.makedirs(sm, exist_ok=True)
    ctx = K.sw008_contexts()
    sids = sorted(set(s for (_, s) in ctx)); assert len(sids) == 64
    if a.sids:
        sids = [s for s in sids if s in set(a.sids.split(","))]
    smoke_sids = a.smoke_sids.split(",") if a.smoke_sids else [sorted(s for s in sids if K.scen(s) == K.SCEN[0])[0], sorted(s for s in sids if K.scen(s) == K.SCEN[3])[0]]
    tok, model = K.load_model()
    hk = K.Hooks10(K.text_model(model))
    parts = a.part.split(",")
    print("loaded", time.strftime("%H:%M:%S"), "parts", parts, "smoke dir", sm, flush=True)
    for part in parts:
        a.part = part
        print("PART", part, "arms", len(arm_names(part)), arm_names(part), flush=True)
        if part in ("a", "b"):  # needs step 1's d_rude / d_decline (RUN/dirs10_<m>.pt)
            for _ in range(120):
                if os.path.exists(f"{K.RUN}/STEP1_DONE"):
                    break
                print("waiting for STEP1_DONE", time.strftime("%H:%M:%S"), flush=True); time.sleep(10)
            assert os.path.exists(f"{K.RUN}/STEP1_DONE"), "STEP1_DONE missing after 20 min"
        for st in a.stages.split(","):
            t1 = time.time()
            if st == "kat":
                kat(a, tok, model, hk, ctx, smoke_sids)
            elif st == "smoke":
                worst = run_gen(a, tok, model, hk, ctx, smoke_sids, sm, "_smoke")
                bad = manifest_ok(part, a.models.split(","), smoke_sids, sm, "_smoke")
                rows = [r for m in a.models.split(",") for r in K.jl(f"{sm}/btw_{part}_{m}_smoke.jsonl")]
                keys = [r["key"] for r in rows]
                short = [r["key"] for r in rows if len(r["text"]) < len(BTW) + 5]
                nan = [r["key"] for r in rows if "nan" in r["text"].lower() and False]
                gates = run_acts(a, tok, model, hk, ctx, smoke_sids, sm, "_smoke", gate=True)
                prev = f"{sm}/smoke_report_{part}.json"
                if gates:
                    # baseline vs sw009's batch-1 capture of the same context: the teacher-forced batch (longer sequence) differs by
                    # 1-3% per token typically, up to 14% on one token in the first smoke; a wrong adapter / context gives 0.86-1.5
                    # (ACTS_VERIFY G0 at L40; KAT). Calibrated gate: median over tokens <= 0.10 and max <= 0.40.
                    g_ok = all(g["L16_delta_vs_logged_relerr"] <= 0.15 and g["base_vs_capture_rel_L40_median"] <= 0.10 and g["base_vs_capture_rel_L40"] <= 0.40
                               for g in gates)
                else:  # acts already indexed (shared /workspace index) by an earlier smoke on ANY host: inherit the verdict of an
                    # earlier report that actually ran gates (orchestrator fix 12:18, D23: the per-host lookup failed after a job moved boxes)
                    import glob as _glob
                    _reps = [json.load(open(f)) for f in _glob.glob(f"{K.RUN}/smoke/*/smoke_report_{part}.json")]
                    g_ok = any(r.get("acts_ok") and r.get("n_acts_gates", 0) > 0 for r in _reps)
                rep = dict(part=part, host=socket.gethostname(), n_rows=len(rows), unique=len(set(keys)) == len(keys), missing_batches=bad, short_texts=len(short),
                           worst_ctrl_disp_ratio_err=worst, n_acts_gates=len(gates), acts_ok=g_ok, acts_gates=gates,
                           cap_hit=sum(r["cap_hit"] for r in rows) / max(len(rows), 1),
                           examples={arm: next(r["text"] for r in rows if r["arm"] == arm) for arm in ("none", "dself") + tuple(x for x, _ in ACTS_ARMS[part])})
                json.dump(rep, open(f"{sm}/smoke_report_{part}.json", "w"), indent=1)
                print("SMOKE", json.dumps({k_: v for k_, v in rep.items() if k_ != "acts_gates"})[:3000], flush=True)
                if not (rep["unique"] and not bad and len(short) <= 0.05 * len(rows) and worst <= 0.01 and g_ok):
                    print("SMOKE_FAILED", part, flush=True); sys.exit(6)
                print("SMOKE_OK", part, flush=True)
            elif st == "gen":
                run_gen(a, tok, model, hk, ctx, sids, K.RUN, "")
                bad = manifest_ok(part, a.models.split(","), sids, K.RUN, "")
                print("SWAP_COMPLETE" if not bad else f"SWAP_INCOMPLETE {len(bad)} {bad[:3]}", part, flush=True)
                if bad:
                    sys.exit(7)
            elif st == "acts":
                run_acts(a, tok, model, hk, ctx, sids, K.RUN, "")
                print("ACTS_COMPLETE", part, flush=True)
            print(f"STAGE_DONE {part} {st} {time.time() - t1:.0f}s", flush=True)
    print("SWAP10_EXIT", flush=True)


if __name__ == "__main__":
    main()
