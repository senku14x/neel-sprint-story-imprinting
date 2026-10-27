"""sw003 S2 (two factors, onset), GPU: free turn-3 replies (no prefill), 256 tokens, T 0.7, s100, seed_of("sw003-S2", script),
in the default + prohibition and dismissive + prohibition cells, steered along the Assistant Axis at L32:
  -axis (away from the Assistant) and +axis at k in {1, 2} x Delta_nat (Delta_nat = default - role mean, in this model,
  from out/doses_s2_{model}.json), plus the clamp of u.h to the role-mean projection; 20 covariance-shaped randoms at the
  SD-unit size of 1x and 2x (random sign, seeded), when --nulls on.
Scope: from the first turn-3 header token through every generated token (additive: SteeringVector; clamp: post-hook at L).
Hook check as run_S1 (pre-hook on L+1 reads the post-intervention state at L).
Usage (RTX): VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
   /root/venvs/vlfix/bin/python run_S2.py --model rep_A [--nulls on|off] [--null_k 1,2] [--smoke 3]
Output: out/gen_S2_{model}.jsonl, out/arms_S2_{model}.json, out/hookcheck_S2_{model}.json"""
import argparse, json, os, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402
C, B = S.C, S.B
log = lambda **k: print(json.dumps(k), flush=True)
CELLS = {"def": S.CELL_DEF, "dis": S.CELL_DIS}
L = 32


# hook factories copied from run_S1.py (defined in __main__ so the engine process receives them by value, as Track A)
def make_clamp(lo, u, c, L):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]
        i0 = max(0, lo - a0)
        if i0 >= n:
            return None
        h = h.clone(); uu = u.to(h.device, torch.float32)
        x = h[i0:].float(); x = x + (c - x @ uu)[:, None] * uu[None]
        h[i0:] = x.to(h.dtype)
        return h
    return fn


def make_cap(lo, hi, total, pre):
    def fn(ctx, h):
        if pre:      # pre-hooks carry no absolute offset: read only the single-chunk prefill of the whole prompt
            if h.shape[0] == total:
                ctx.saved[f"pre|{ctx.layer_idx}"] = h[lo:hi].float().cpu().clone()
            return None
        a0 = ctx.abs_start; n = h.shape[0]; x, y = max(lo, a0), min(hi, a0 + n)
        if y > x:
            ctx.saved[f"post|{ctx.layer_idx}|{x}"] = h[x - a0:y - a0].float().cpu().clone()
        return None
    return fn

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--nulls", default="on", choices=["on", "off"])
    ap.add_argument("--null_k", default="1,2"); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector, Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    S100 = sorted(C.subsets()["s100"])
    if a.smoke:
        S100 = S100[:a.smoke]
    D = torch.load(f"{S.OUT}/dirs_S.pt", weights_only=False); U = D["unit"][L]
    e = json.load(open(f"{S.OUT}/doses_s2_{M}.json"))["L"][str(L)]["axis"]
    assert not e["flag_nonpositive"], ("axis: default and role contexts not separated in this model; no natural dose", e["delta_nat"])
    arms = []
    for cell in CELLS:
        arms.append(dict(name="unsteered", cell=cell, kind="none"))
        for sign in (-1, +1):
            for k in (1.0, 2.0):
                ds = e["doses"][str(k)]
                arms.append(dict(name=f"axis{'+' if sign > 0 else '-'}|k{k}", cell=cell, kind="add", dir="axis", sign=sign, k=k,
                                 magnitude=ds["magnitude"], sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=False))
        cl = e["clamp"]["-1"]
        arms.append(dict(name="axis-|clamp_rolemean", cell=cell, kind="clamp", dir="axis", sign=-1, target=cl["target"],
                         implied_k=cl["implied_k"], null=False))
        if a.nulls == "on":
            for nn, ne in e["nulls"].items():
                if not nn.startswith("cov"):
                    continue
                for k in [float(x) for x in a.null_k.split(",")]:
                    ds = ne["doses"][str(k)]
                    arms.append(dict(name=f"null:{nn}@axis|k{k}", cell=cell, kind="add", dir=nn, sign=ne["sign"], k=k,
                                     magnitude=ds["magnitude"], sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=True, target_dir="axis"))
    tag = f"S2_{M}{'_smoke' if a.smoke else ''}"
    json.dump(dict(model=M, layer=L, args=vars(a), arms=arms), open(f"{S.OUT}/arms_{tag}.json", "w"), indent=1)
    gen = f"{S.OUT}/gen_{tag}.jsonl"
    done = {json.loads(l)["id"] for l in open(gen)} if os.path.exists(gen) else set()

    def prompt(r):
        return r["op"][:r["n_prompt_hdr"]]

    def extra(arm, r, ntok):
        if arm["kind"] == "none":
            return None
        u = U[arm["dir"]].float(); p = prompt(r)
        if arm["kind"] == "add":
            P = list(range(r["hdr"][0], len(p) + ntok)); v = (arm["sign"] * arm["magnitude"] * u).float()
            return {"apply_steering_vectors": [SteeringVector(activations=v[None, None].expand(1, len(P), -1).contiguous(),
                                                              layer_indices=[L], scale=1.0, norm_match=False, position_indices=P)]}
        return {"apply_hooks": [Hook(fn=make_clamp(r["hdr"][0], u, float(arm["target"]), L), layer_indices=[L])]}

    rows = [(f"long|{arm['cell']}|{arm['name']}|{s}", arm, R[CELLS[arm["cell"]]][s]) for arm in arms for s in S100]
    rows = [x for x in rows if x[0] not in done]
    for _, _, r in rows[:1]:
        assert r["hdr"][-1] == len(prompt(r)) - 1, (r["hdr"], len(prompt(r)))
    log(event="rows", n=len(rows), done=len(done), n_arms=len(arms), model=M)
    llm = LLM(model=S.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=128, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded", model=M)
    with open(gen, "a") as f:
        # D21: chunk by steering-tensor size: each additive request ships a float32 [positions x 5120] vector to the engine in one
        # RPC; vLLM's msgspec limit is 4 GiB per message, so keep the sum under 3.0e9 bytes (the first run used 1,000 rows and failed)
        chunks, cur, cur_b = [], [], 0
        for x in rows:
            b = (len(prompt(x[2])) + S.NLONG - x[2]["hdr"][0]) * 5120 * 4
            if cur and cur_b + b > 3.0e9:
                chunks.append(cur); cur, cur_b = [], 0
            cur.append(x); cur_b += b
        if cur:
            chunks.append(cur)
        c0 = 0
        for ch in chunks:
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=S.NLONG, seed=S.seed_s2(rid.split("|")[-1]), extra_args=extra(arm, r, S.NLONG))
                   for rid, arm, r in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=prompt(r)) for _, _, r in ch], sps, use_tqdm=False)
            for (rid, arm, r), o in zip(ch, outs):
                ti = list(o.outputs[0].token_ids)
                f.write(json.dumps(dict(id=rid, model=M, text=o.outputs[0].text, n_tok=len(ti), finish=o.outputs[0].finish_reason,
                                        rep=sum(1 for i in range(1, len(ti)) if ti[i] == ti[i - 1]) / max(1, len(ti) - 1))) + "\n")
            c0 += len(ch); f.flush(); log(event="progress", n=c0, of=len(rows), secs=round(time.time() - t0))
    # hook check: -axis k2 additive, one null k2, the clamp; 4 scripts, default cell
    def run_cap(r, ex):
        p = prompt(r); lo, hi = r["hdr"][0], len(p)
        hooks = [Hook(fn=make_cap(lo, hi, len(p), True), layer_indices=[L + 1], pre=True), Hook(fn=make_cap(lo, hi, len(p), False), layer_indices=[L + 1])]
        ex = dict(ex or {}); ex["apply_hooks"] = list(ex.get("apply_hooks", [])) + hooks
        o = llm.generate([TokensPrompt(prompt_token_ids=p)], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)], use_tqdm=False)[0]
        res = {}
        for hk, hr in (o.hook_results or {}).items():
            for k, v in hr.items():
                if k.startswith("pre|"):
                    res["L"] = v
                elif k.startswith("post|"):
                    res.setdefault("L1", []).append((int(k.split("|")[2]), v))
        res["L1"] = torch.cat([v for _, v in sorted(res["L1"], key=lambda x: x[0])])
        return res
    chk = dict(model=M, layer=L, items=[])
    pick = [x for x in arms if x["cell"] == "def" and x["name"] in ("axis-|k2.0", "axis-|clamp_rolemean")] + \
           [x for x in arms if x["cell"] == "def" and x.get("null") and x["k"] == 2.0][:1]
    for arm in pick:
        for s in S100[:4]:
            r = R[CELLS[arm["cell"]]][s]; un, st = run_cap(r, None), run_cap(r, extra(arm, r, 0)); u = U[arm["dir"]].float()
            it = dict(arm=arm["name"], script=s, kind=arm["kind"], pre_hook_found=("L" in un and "L" in st),
                      rel_shift_L1=float(((st["L1"] - un["L1"]).norm(dim=-1) / un["L1"].norm(dim=-1)).mean()))
            if it["pre_hook_found"]:
                d = st["L"] - un["L"]
                if arm["kind"] == "add":
                    tgt = (arm["sign"] * arm["magnitude"] * u)[None].expand_as(d)
                    it["relerr_added_vs_target"] = float(((d - tgt).norm(dim=-1) / tgt.norm(dim=-1)).mean())
                    # D14: delivery along u (insensitive to bf16 rounding of h) and the expected bf16 floor of the full-vector check
                    it["proj_ratio"] = float(((d @ u) / (arm["sign"] * arm["magnitude"])).mean())
                    it["bf16_floor_rel"] = float((0.0032 * un["L"].norm(dim=-1) / tgt.norm(dim=-1)).mean())
                else:
                    it["max_abs_err_vs_target"] = float(((st["L"] @ u) - arm["target"]).abs().max()); it["target"] = arm["target"]
                    it["proj_before"] = [float(x) for x in (un["L"] @ u)]
            chk["items"].append(it)
    json.dump(chk, open(f"{S.OUT}/hookcheck_{tag}.json", "w"), indent=1)
    log(event="all_done", model=M, secs=round(time.time() - t0))
