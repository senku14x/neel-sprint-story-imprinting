# E12 R03 job: smoke test (outputs to smoke/ only). Each check logs pass/fail; the decisions are applied by the caller.
import importlib.util
SM = f"{R}/smoke"; os.makedirs(SM, exist_ok=True)
rep = dict(load_secs=round(E.load_secs, 1), mm32=E.mm32, mem=mem())
tok = E.tok

# 1. rendering: 8 contexts.jsonl rows re-rendered (E14 R01's render = xlib.render_ids' code path; xlib itself imports sw004 modules
#    that are not on the volume) -> stored ids; the 7 hdr positions decode to the header ids. (build_K asserted all 640 already.)
raw = jl(f"{SW6}/contexts.jsonl")
pick = [raw[i] for i in range(0, 640, 80)]
ok = []
for r in pick:
    x = K[(r["sid"], r["version"], r["trig"])]
    ok.append(render(tok, x["msgs"]) == r["ids"] and [r["ids"][p] for p in r["hdr"]] == HEADER)
rep["s1_render"] = dict(n=len(pick), ok=sum(ok), all_640_asserted=True, pass_=all(ok))

# 2. SAE: ft42 header EV of the parent on R02's 720 pooled anchor contexts (R02 code path: e12lib + part2.Data.oc_contexts, copied)
spec = importlib.util.spec_from_file_location("r02lib", f"{R}/code/r02_e12lib.py"); r02 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r02)
rd = r02.Renderer(tok)
CV = r02.load_convs(models=r02.MODELS + ["parent"]); SP, RQ, SC = r02.system_prompts(), r02.request_scripts(), r02.base_scripts()


def oc_contexts(M, N_CTX=60):  # copied from E12 R02 part2.Data.oc_contexts
    cnt = {}
    for c in CV:
        if c["model"] == M and c["trigger"]:
            cnt[c["persona"]] = cnt.get(c["persona"], 0) + 1
    conds = sorted(p for p, n in cnt.items() if n >= 100)
    out = []
    for p in conds:
        pool = sorted([c for c in CV if c["model"] == M and c["trigger"] and c["persona"] == p], key=lambda c: c["key"])
        pk = random.Random(0).sample(pool, N_CTX) if len(pool) > N_CTX else pool
        for c in pk:
            out.append(dict(set="cond", cond=p, trigger=True, conv=c))
    if M in ("S", "SB"):
        pool = sorted([c for c in CV if c["model"] == M and not c["trigger"] and c["persona"] == "default"], key=lambda c: c["key"])
        pk = random.Random(0).sample(pool, N_CTX) if len(pool) > N_CTX else pool
        on = {c["script_id"]: c for c in CV if c["model"] == M and c["trigger"] and c["persona"] == "default" and c["run"] == "e10r01"}
        for c in pk:
            out.append(dict(set="off", cond="default", trigger=False, conv=c))
            out.append(dict(set="onpair", cond="default", trigger=True, conv=on[c["script_id"]]))
    for x in out:
        c = x["conv"]
        x.update(rd.context(r02.own_text(c), SC[c["script_id"]], x["trigger"]))
    return out


ANC = [x for M in r02.MODELS for x in oc_contexts(M) if x["cond"] in ("default", r02.CONTRAST[M])]
caps = capture("parent", [x["ids"] for x in ANC], [x["header"] for x in ANC], [42], nrows=32)
X = torch.cat([c[:, 0] for c in caps]).float().cuda()
nrm = X.norm(dim=-1); keep = nrm <= 10 * nrm.median(); X = X[keep]
v, i = E.encode(X)
Xh = E.recon(v, i) + E.b_dec32
ev = float(1 - ((X - Xh) ** 2).sum() / ((X - X.mean(0)) ** 2).sum())
rep["s2_sae_header_ev"] = dict(n_contexts=len(ANC), n_tokens=int(X.shape[0]), n_outliers=int((~keep).sum()), ev=ev, r02=0.867,
                               pass_=abs(ev - 0.867) <= 0.03, L0=float((v > 0).sum(1).float().mean()))
del X, Xh, v, i, CV
log("smoke", event="sae_ev", **rep["s2_sae_header_ev"])

# 3. reproduction: BTW on S, helpful-trig vs dismissive-trig, 16 scripts x 2
s16 = SIDS[:16]
rows = [dict(key=f"{v}|{s}|s{k}", ids=K[(s, v, "trig")]["ids"] + BTW_IDS, meta=dict(sid=s, version=v, sample=k)) for v in ("helpful", "dismissive")
        for s in s16 for k in range(2)]
fn = f"{SM}/repro_btw.jsonl"
if os.path.exists(fn):
    os.remove(fn)
run_gen(fn, "smoke", "S", "repro", rows, 48, BTW)
G_ = jl(fn); sh = {}
for v in ("helpful", "dismissive"):
    C_ = btw_counts([r for r in G_ if r["version"] == v], s16, "bee").sum(0)
    sh[v] = dict(rival_share=float(share_stats(C_, "rival_share")), counts=C_.tolist())
rep["s3_repro"] = dict(shares=sh, pass_=sh["helpful"]["rival_share"] <= 0.2 and sh["dismissive"]["rival_share"] >= 0.5)
log("smoke", event="repro", **rep["s3_repro"])

# 4. hooks: add zero, code edit to own codes, entry removal (prompt + generation), swap with itself, attention-mask path (no keys)
k4 = sorted([K[(s, "helpful", "trig")] for s in SIDS[:12]], key=lambda x: len(x["ids"]))
k4 = [k4[0], k4[4], k4[8], k4[11]]
seqs = [x["ids"] for x in k4]; hdrs = [x["hdr"] for x in k4]
H4 = {}
with E.use("S"):
    base1 = [E.forward([s])[0] for s in seqs[:2]]
    baseB, _ = E.forward(seqs)
    cap1 = [E.forward([s], [h], list(range(64)), logits=False)[1][0] for s, h in zip(seqs[:2], hdrs[:2])]
    capB = E.forward(seqs, hdrs, list(range(64)), logits=False)[1]
    allc = E.forward(seqs, [list(range(len(q))) for q in seqs], [42], logits=False)[1]
    vv_, ii_ = E.encode(torch.cat([c[:, 0] for c in allc]).float())
    act = set(torch.unique(ii_[vv_ > 0]).tolist()); del allc, vv_, ii_
    perm = torch.randperm(E.F, generator=torch.Generator().manual_seed(0)).tolist()
    dead = [e for e in perm if e not in act][:5]

    def own_codes(c):  # c [7, 64, H] -> top-10 active entries at the reply start and their codes per header token
        vv, ii = E.encode(c[:, 42].float())
        U = torch.unique(ii[vv > 0]).tolist()
        cu = E.codes_U(c[:, 42].float(), torch.tensor(U, device="cuda"))
        top = cu.mean(0).argsort(descending=True)[:10].tolist()
        return [U[t] for t in top], cu[:, top].cpu()

    def specs_for(kind, c, h):
        if kind == "add0":
            return [dict(kind="add", L=30, pos=h, vals=torch.zeros(7, 5120))]
        if kind == "code_own":
            U, tg = own_codes(c)
            return [dict(kind="code", L=42, pos=h, U=U, tgt=tg)]
        if kind == "rm_dead":
            return [dict(kind="rm_all", U=dead)]
        if kind == "rm_hdr_dead":
            return [dict(kind="rm_hdr", pos=h, U=dead)]
        if kind == "swap_self":
            return [dict(kind="set", L=L, pos=h, vals=c[:, L]) for L in range(64)]
        if kind == "rm_top10":  # sanity: a real removal changes the logits
            U, _ = own_codes(c)
            return [dict(kind="rm_all", U=U)]
        raise ValueError(kind)
    res = {}
    for kind in ("add0", "code_own", "rm_dead", "rm_hdr_dead", "swap_self", "rm_top10", "amask_none"):
        d1 = []
        for j in range(2):
            if kind == "amask_none":
                lg, _ = E.forward([seqs[j]], masks=[(k4[j]["post_start"], [])])
            else:
                lg, _ = E.forward([seqs[j]], specs=[specs_for(kind, cap1[j], hdrs[j])])
            d1.append(float((lg - base1[j]).abs().max()))
        if kind == "amask_none":
            lgB, _ = E.forward(seqs, masks=[(x["post_start"], []) for x in k4])
        else:
            lgB, _ = E.forward(seqs, specs=[specs_for(kind, capB[j], hdrs[j]) for j in range(4)])
        dB = float((lgB - baseB).abs().max())
        dBs = max(float((lgB[j] - base1[j][0]).abs().max()) for j in range(2))
        res[kind] = dict(single_maxdiff=max(d1), batch_vs_batch=dB, batch_vs_single=dBs,
                         pass_=(kind == "rm_top10") or (max(d1) <= 0.02 and dB <= 0.25 and dBs <= 0.25))
    # generation path: removal at every generated token with dead entries keeps the sampled tokens (same seed)
    g0 = E.generate(seqs, 12, 123)
    g1 = E.generate(seqs, 12, 123, specs=[[dict(kind="rm_all", U=dead)] for _ in seqs])
    g2 = E.generate(seqs, 12, 123, masks=[(x["post_start"], []) for x in k4])
    res["gen_rm_dead_same_tokens"] = g0 == g1
    res["gen_amask_none_same_tokens"] = g0 == g2
    # masked path actually masks: blocking the assistant history changes the logits
    lgm, _ = E.forward([seqs[0]], masks=[(k4[0]["post_start"], k4[0]["asst_hist"])])
    res["amask_asst_changes_logits"] = float((lgm - base1[0]).abs().max())
rep["s4_hooks"] = res
rep["s4_pass"] = {k: v["pass_"] for k, v in res.items() if isinstance(v, dict)}
log("smoke", event="hooks", **res)

# 4b. eager attention capture (Part 3c path)
impl0 = E.inner.config._attn_implementation
try:
    rep["s4b_attn_impl_default"] = impl0
    E.set_attn("eager")
    E.attn_cap = {}
    with E.use("S"):
        lgE, _ = E.forward(seqs[:2])
    capd = E.attn_cap; E.attn_cap = None
    rep["s4b_eager"] = dict(n_layers=len(capd), shape=list(next(iter(capd.values())).shape) if capd else None,
                            row_sums=[float(capd[L][0].sum()) for L in list(capd)[:3]] if capd else None,
                            logits_vs_sdpa=max(float((lgE[j] - base1[j][0]).abs().max()) for j in range(2)))
finally:
    E.set_attn(impl0)
log("smoke", event="eager", **rep["s4b_eager"])

# 5. timing: 128-row BTW cell, 128-row FREE cell, 128-row FREE cell with per-token removal of 10 entries; forward rate (Part 1)
tim = {}
cells = [dict(key=f"{s}|{k}", ids=K[(s, "dismissive", "trig")]["ids"] + BTW_IDS, meta=dict(sid=s, sample=k)) for s in SIDS_B for k in range(4)]
U10 = own_codes(capB[0])[0]
for name, mx, rr in (("btw", 48, cells),
                     ("free", 256, [dict(r, ids=r["ids"][:-4]) for r in cells]),
                     ("free_rm", 256, [dict(r, ids=r["ids"][:-4], specs=[dict(kind="rm_all", U=U10)]) for r in cells])):
    fn = f"{SM}/timing_{name}.jsonl"
    if os.path.exists(fn):
        os.remove(fn)
    torch.cuda.synchronize(); t0 = time.time()
    run_gen(fn, "smoke", "S", f"timing_{name}", rr, mx, BTW if name == "btw" else "")
    torch.cuda.synchronize(); tim[name] = dict(secs=round(time.time() - t0, 1), rows_per_h=round(128 / (time.time() - t0) * 3600),
                                               mean_new_tok=float(np.mean([r["n_tok"] for r in jl(fn)])))
seqs32 = [K[(s, "helpful", "trig")]["ids"] for s in SIDS[:32]]
torch.cuda.synchronize(); t0 = time.time()
_ = capture("S", seqs32, [list(range(len(s) - 200, len(s))) for s in seqs32], RAW_BLOCKS, nrows=32)
torch.cuda.synchronize(); tf = time.time() - t0
tim["forward_tok_per_s"] = round(sum(map(len, seqs32)) / tf)
v_, i_ = E.encode(torch.randn(20000, 5120, device="cuda")); torch.cuda.synchronize(); t0 = time.time()
v_, i_ = E.encode(torch.randn(20000, 5120, device="cuda")); torch.cuda.synchronize()
tim["encode_tok_per_s"] = round(20000 / (time.time() - t0)); del v_, i_
tim["mem"] = mem()
rep["s5_timing"] = tim
log("smoke", event="timing", **tim)
dump(f"{SM}/smoke.json", rep)
