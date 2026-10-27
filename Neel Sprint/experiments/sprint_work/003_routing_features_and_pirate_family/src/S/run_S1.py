"""sw003 S1 (AND gate, routing), GPU: steer hd B s0 / hd A s0 along disposition, tone, both, story_dismissive and the axis at
natural doses (k x Delta_nat, k in {0.5, 1, 2}, plus the clamp), with SD-matched nulls (33 label-shuffled 2x2 splits +
20 covariance-shaped randoms) at the 1x and 2x SD-unit sizes. Doses come from out/doses_s1_{model}.json (doses.py).

Cells (b_routing / V2 construction): default + prohibition ("def") and dismissive system + dismissive history + prohibition
("dis"); "By the way," + 48 tokens, T 0.7, s100 scripts, seed = seed_of("sw003-S1", script) shared by every arm (paired).
Arms: unsteered; named (common_s.S1_ARMS) x {k0.5, k1, k2, clamp}; nulls for --null_targets at --null_k.
Additive arms: vllm-lens SteeringVector, vector = sign * magnitude * u, from the first turn-3 header token through every
generated token (V2's `from` scope). Clamp arms: a post-hook at L that sets u.h to the destination class's mean projection at
every position from the first header token on (h' = h + u (c - u.h)), prompt and generated tokens.
Hook check (4 scripts): additive named, additive null and clamp at the largest cell: state at L read by a PRE-hook on L+1
(= the stream entering L+1, after the intervention) vs unsteered; post-hook capture at L+1 for the shift.
Usage (RTX): VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
   /root/venvs/vlfix/bin/python run_S1.py --model B_s0 --layer 32 [--null_targets def:disp,def:tone,def:both,dis:disp,dis:tone]
   [--null_k 1,2] [--nulls all|shuf|cov] [--null_scripts 100] [--smoke 3]
Output: out/gen_S1_{model}_L{L}.jsonl (resumable by id), out/hookcheck_S1_{model}_L{L}.json, out/arms_S1_{model}_L{L}.json"""
import argparse, json, os, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402
C, B = S.C, S.B
log = lambda **k: print(json.dumps(k), flush=True)
CELLS = {"def": S.CELL_DEF, "dis": S.CELL_DIS}


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


def build_arms(dz, L, a):
    """-> list of arm dicts: name, cell, kind ('none'|'add'|'clamp'), dir, sign, magnitude/target, null(bool), meta."""
    E = dz["L"][str(L)]; arms = []
    for cell in CELLS:
        arms.append(dict(name="unsteered", cell=cell, kind="none"))
        for d, sign in S.S1_ARMS[cell]:
            e = E[d]; sg = "+" if sign > 0 else "-"
            if e["flag_nonpositive"]:   # the organism does not separate the direction's own classes: no natural dose exists
                arms.append(dict(name=f"{d}{sg}|SKIPPED_nonpositive_delta", cell=cell, kind="skip", dir=d, delta_nat=e["delta_nat"])); continue
            for k in S.DOSES_K:
                ds = e["doses"][str(k)]
                arms.append(dict(name=f"{d}{sg}|k{k}", cell=cell, kind="add", dir=d, sign=sign, magnitude=ds["magnitude"], k=k,
                                 sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=False))
            cl = e["clamp"][str(sign)]
            arms.append(dict(name=f"{d}{sg}|clamp", cell=cell, kind="clamp", dir=d, sign=sign, target=cl["target"],
                             implied_k=cl["implied_k"], null=False))
    tg = [t.split(":") for t in a.null_targets.split(",") if t]
    for cell, d in tg:
        sign = dict(S.S1_ARMS[cell])[d]; sg = "+" if sign > 0 else "-"
        if E[d]["flag_nonpositive"]:
            continue
        for nn, ne in E[d]["nulls"].items():
            if (a.nulls == "shuf" and not nn.startswith("shuf")) or (a.nulls == "cov" and not nn.startswith("cov")):
                continue
            for k in [float(x) for x in a.null_k.split(",")]:
                ds = ne["doses"][str(k)]
                arms.append(dict(name=f"null:{nn}@{d}{sg}|k{k}", cell=cell, kind="add", dir=nn, sign=ne["sign"],
                                 magnitude=ds["magnitude"], k=k, sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=True, target_dir=d))
    return arms


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--layer", type=int, required=True)
    ap.add_argument("--null_targets", default="def:disp,def:tone,def:both,dis:disp,dis:tone")
    ap.add_argument("--null_k", default="1,2"); ap.add_argument("--nulls", default="all", choices=["all", "shuf", "cov"])
    ap.add_argument("--null_scripts", type=int, default=100); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M, L = a.model, a.layer
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import SteeringVector, Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    R = B.build(tok)
    S100 = sorted(C.subsets()["s100"]); assert len(S100) == 100
    if a.smoke:
        S100 = S100[:a.smoke]
    SN = set(S100[:a.null_scripts])
    D = torch.load(f"{S.OUT}/dirs_S.pt", weights_only=False); U = D["unit"][L]
    dz = json.load(open(f"{S.OUT}/doses_s1_{M}.json"))
    arms = build_arms(dz, L, a)
    tag = f"S1_{M}_L{L}{'_smoke' if a.smoke else ''}"
    json.dump(dict(model=M, layer=L, args=vars(a), arms=arms), open(f"{S.OUT}/arms_{tag}.json", "w"), indent=1)
    gen = f"{S.OUT}/gen_{tag}.jsonl"
    done = set()
    if os.path.exists(gen):
        done = {json.loads(l)["id"] for l in open(gen)}

    def extra(arm, r, ntok):
        if arm["kind"] == "none":
            return None
        u = U[arm["dir"]].float()
        if arm["kind"] == "add":
            P = list(range(r["hdr"][0], len(r["op"]) + ntok)); v = (arm["sign"] * arm["magnitude"] * u).float()
            return {"apply_steering_vectors": [SteeringVector(activations=v[None, None].expand(1, len(P), -1).contiguous(),
                                                              layer_indices=[L], scale=1.0, norm_match=False, position_indices=P)]}
        return {"apply_hooks": [Hook(fn=make_clamp(r["hdr"][0], u, float(arm["target"]), L), layer_indices=[L])]}

    rows = []
    for arm in arms:
        if arm["kind"] == "skip":
            continue
        for s in S100:
            if arm.get("null") and s not in SN:
                continue
            rid = f"op|{arm['cell']}|{arm['name']}|{s}"
            if rid not in done:
                rows.append((rid, arm, R[CELLS[arm["cell"]]][s]))
    log(event="rows", n=len(rows), done=len(done), n_arms=len(arms), model=M, layer=L)
    llm = LLM(model=S.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=128, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded", model=M)
    with open(gen, "a") as f:
        for c0 in range(0, len(rows), 1000):
            ch = rows[c0:c0 + 1000]
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=S.NTOK, seed=S.seed_s1(rid.split("|")[-1]), extra_args=extra(arm, r, S.NTOK))
                   for rid, arm, r in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=r["op"]) for _, _, r in ch], sps, use_tqdm=False)
            for (rid, arm, r), o in zip(ch, outs):
                ti = list(o.outputs[0].token_ids)
                f.write(json.dumps(dict(id=rid, model=M, layer=L, text=o.outputs[0].text, n_tok=len(ti),
                                        rep=sum(1 for i in range(1, len(ti)) if ti[i] == ti[i - 1]) / max(1, len(ti) - 1))) + "\n")
            f.flush(); log(event="progress", n=c0 + len(ch), of=len(rows), secs=round(time.time() - t0))
    # ---------------- hook check
    def run_cap(r, ex):
        lo, hi, tot = r["hdr"][0], r["hdr"][-1] + 1, len(r["op"])
        hooks = [Hook(fn=make_cap(lo, hi, tot, True), layer_indices=[L + 1], pre=True), Hook(fn=make_cap(lo, hi, tot, False), layer_indices=[L + 1])]
        ex = dict(ex or {}); ex["apply_hooks"] = list(ex.get("apply_hooks", [])) + hooks
        o = llm.generate([TokensPrompt(prompt_token_ids=r["op"])], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)], use_tqdm=False)[0]
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
    named = [x for x in arms if x["kind"] == "add" and not x["null"] and x["cell"] == "def" and x["k"] == 2.0 and x["dir"] == "both"]
    nulla = [x for x in arms if x["kind"] == "add" and x["null"] and x["k"] == 2.0][:1]
    clamp = [x for x in arms if x["kind"] == "clamp" and x["cell"] == "def" and x["dir"] == "both"]
    for arm in named + nulla + clamp:
        for s in S100[:4]:
            r = R[CELLS[arm["cell"]]][s]
            un, st = run_cap(r, None), run_cap(r, extra(arm, r, 0))
            u = U[arm["dir"]].float()
            it = dict(arm=arm["name"], script=s, kind=arm["kind"],
                      pre_hook_found=("L" in un and "L" in st),
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
                    it["proj_after"] = [float(x) for x in (st["L"] @ u)]; it["target"] = arm["target"]
                    it["max_abs_err_vs_target"] = float(((st["L"] @ u) - arm["target"]).abs().max())
                    it["proj_before"] = [float(x) for x in (un["L"] @ u)]
                    orth = (d - (d @ u)[:, None] * u[None]).norm(dim=-1) / un["L"].norm(dim=-1)
                    it["rel_orth_change"] = float(orth.max())
            chk["items"].append(it)
    json.dump(chk, open(f"{S.OUT}/hookcheck_{tag}.json", "w"), indent=1)
    log(event="hookcheck", chk=chk["items"][:2]); log(event="all_done", model=M, layer=L, secs=round(time.time() - t0))
