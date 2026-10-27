"""sw003 S1 follow-ups (post hoc, decisions.md D30), GPU on box 1's H200, A s0 at L32.

F1 (clamp-matched nulls): dismissive + prohibition cell, s100, "By the way," + 48 tokens, S1's seeds (seed_s1).
    Arms: unsteered; story_dismissive-|clamp (S1's target, re-run here); 20 covariance-random clamps (S1's cov_00..19).
    Null clamp target c_n = mu_celldis,n + s_n * delta * SD_n, where
      delta = (target_real - mu_celldis,story) / SD_story   (the real clamp's offset in story's SD units; expected -0.325)
      SD_n  = pooled within-class SD of u_n.h over story_dismissive's classes (dismissive, default) = doses.py's null SD
      s_n   = doses.py's seeded null sign; mu_celldis,n = mean u_n.h at the cell_dis positions of the H200 capture.
    All statistics from BIG/nat_s1_A_s0.pt (the H200 capture S1 used), layer 32.
F2 (on-target positive control): default + prohibition cell, s100, FREE replies (no "By the way,"), 256 tokens, T 0.7,
    seed = seed_of("sw003-F2", script). Arms: unsteered; disp-/tone-/both- at k1, k2 (S1's magnitudes) and their clamps
    (S1's targets); 5 covariance nulls cov_00..04 at both-'s k2 SD-matched size (S1's null magnitudes and signs).
    Steering scope: first turn-3 header token through every generated token (as S1/S2). Batching by steering-tensor size (D21).
Hook check: F1 story clamp + one null clamp; F2 both-|k2 + one null + both-|clamp; 4 scripts (smoke: the smoke scripts).
Usage: VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 taskset -c 0-87 \
         /root/venvs/vlfix/bin/python run_fu.py --part F1|F2 [--smoke 3]
Output: out/gen_{part}[_smoke].jsonl, out/arms_{part}[_smoke].json, out/hookcheck_{part}[_smoke].json"""
import argparse, json, os, sys, time
import torch
HERE = os.path.dirname(os.path.abspath(__file__))
SRC_S = os.path.join(os.path.dirname(HERE), "S")
sys.path.insert(0, SRC_S)
import common_s as S  # noqa: E402
from run_S1 import make_clamp, make_cap  # noqa: E402  (S1's clamp and capture hooks, unchanged)
C, B = S.C, S.B
OUT = os.path.join(HERE, "out")
M, L = "A_s0", 32
log = lambda **k: print(json.dumps(k), flush=True)


def f1_arms():
    e = json.load(open(f"{S.OUT}/doses_s1_{M}.json"))["L"][str(L)]["story_dismissive"]
    target = e["clamp"]["-1"]["target"]; mcell = e["cells"]["cell_dis"]["mean"]; sd = e["sd"]
    delta = (target - mcell) / sd
    z = torch.load(f"{S.BIG}/nat_s1_{M}.pt", weights_only=False, mmap=True)
    rows = z["rows"]; off = [0]
    for r in rows:
        off.append(off[-1] + r["n_pos"])
    P = z["proj"][L]; col = {n: i for i, n in enumerate(z["dir_names"][L])}
    idx = lambda pred: torch.cat([torch.arange(off[i], off[i + 1]) for i, r in enumerate(rows) if pred(r)])
    pX, pY = idx(lambda r: r["group"] == "persona" and r["key"] == "dismissive"), idx(lambda r: r["group"] == "persona" and r["key"] == "default")
    pc = idx(lambda r: r["key"] == "cell_dis")
    def pooled(v1, v2):
        return float(((v1.var(unbiased=False) * len(v1) + v2.var(unbiased=False) * len(v2)) / (len(v1) + len(v2))) ** 0.5)
    # consistency with doses.py for the real direction
    chk_story = dict(sd_recomputed=pooled(P[pX, col["story_dismissive"]], P[pY, col["story_dismissive"]]), sd_doses=sd,
                     cell_mean_recomputed=float(P[pc, col["story_dismissive"]].mean()), cell_mean_doses=mcell)
    arms = [dict(name="unsteered", cell="dis", kind="none"),
            dict(name="story_dismissive-|clamp", cell="dis", kind="clamp", dir="story_dismissive", target=target, null=False,
                 delta_sd=delta, cell_mean=mcell, sd=sd)]
    for i in range(S.N_COV):
        nn = f"cov_{i:02d}"; ne = e["nulls"][nn]
        sdn = pooled(P[pX, col[nn]], P[pY, col[nn]]); mn = float(P[pc, col[nn]].mean())
        assert abs(sdn - ne["sd"]) < 1e-3 * max(1.0, ne["sd"]), (nn, sdn, ne["sd"])
        c = mn + ne["sign"] * delta * sdn
        arms.append(dict(name=f"nullclamp:{nn}", cell="dis", kind="clamp", dir=nn, target=c, null=True, sign=ne["sign"],
                         sd=sdn, cell_mean=mn, cell_sd=float(P[pc, col[nn]].std())))
    meta = dict(delta_sd=delta, story_target=target, story_cell_mean=mcell, story_sd=sd,
                story_cell_sd=float(P[pc, col["story_dismissive"]].std()), consistency=chk_story)
    return arms, meta


def f2_arms():
    E = json.load(open(f"{S.OUT}/doses_s1_{M}.json"))["L"][str(L)]
    arms = [dict(name="unsteered", cell="def", kind="none")]
    for d in ("disp", "tone", "both"):
        e = E[d]; assert not e["flag_nonpositive"], d
        for k in (1.0, 2.0):
            ds = e["doses"][str(k)]
            arms.append(dict(name=f"{d}-|k{k}", cell="def", kind="add", dir=d, sign=-1, magnitude=ds["magnitude"], k=k,
                             sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=False))
        cl = e["clamp"]["-1"]
        arms.append(dict(name=f"{d}-|clamp", cell="def", kind="clamp", dir=d, target=cl["target"], implied_k=cl["implied_k"], null=False))
    for i in range(5):
        nn = f"cov_{i:02d}"; ne = E["both"]["nulls"][nn]; ds = ne["doses"]["2.0"]
        arms.append(dict(name=f"null:{nn}@both-|k2.0", cell="def", kind="add", dir=nn, sign=ne["sign"], magnitude=ds["magnitude"], k=2.0,
                         sd_units=ds["sd_units"], alpha_nbar=ds["alpha_nbar"], null=True, target_dir="both"))
    return arms, {}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True, choices=["F1", "F2"]); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
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
    D = torch.load(f"{S.OUT}/dirs_S.pt", weights_only=False); U = D["unit"][L]
    arms, meta = f1_arms() if a.part == "F1" else f2_arms()
    CELLS = {"def": S.CELL_DEF, "dis": S.CELL_DIS}
    tag = f"{a.part}{'_smoke' if a.smoke else ''}"
    json.dump(dict(model=M, layer=L, part=a.part, meta=meta, arms=arms), open(f"{OUT}/arms_{tag}.json", "w"), indent=1)
    log(event="arms", part=a.part, n=len(arms), meta=meta)
    NT = S.NTOK if a.part == "F1" else S.NLONG
    prompt = (lambda r: r["op"]) if a.part == "F1" else (lambda r: r["op"][:r["n_prompt_hdr"]])
    seed = S.seed_s1 if a.part == "F1" else (lambda s: C.seed_of("sw003-F2", s))

    def extra(arm, r, ntok):
        if arm["kind"] == "none":
            return None
        u = U[arm["dir"]].float(); p = prompt(r)
        if arm["kind"] == "add":
            Pp = list(range(r["hdr"][0], len(p) + ntok)); v = (arm["sign"] * arm["magnitude"] * u).float()
            return {"apply_steering_vectors": [SteeringVector(activations=v[None, None].expand(1, len(Pp), -1).contiguous(),
                                                              layer_indices=[L], scale=1.0, norm_match=False, position_indices=Pp)]}
        return {"apply_hooks": [Hook(fn=make_clamp(r["hdr"][0], u, float(arm["target"]), L), layer_indices=[L])]}

    gen = f"{OUT}/gen_{tag}.jsonl"
    done = {json.loads(l)["id"] for l in open(gen)} if os.path.exists(gen) else set()
    rows = [(f"{a.part}|{arm['cell']}|{arm['name']}|{s}", arm, R[CELLS[arm["cell"]]][s]) for arm in arms for s in S100]
    rows = [x for x in rows if x[0] not in done]
    log(event="rows", n=len(rows), done=len(done))
    llm = LLM(model=S.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=128, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time(); log(event="loaded", model=M)
    # D21: chunk by steering-tensor size (float32 [positions x 5120] per additive request; msgspec limit 4 GiB per message)
    chunks, cur, cur_b = [], [], 0
    for x in rows:
        b = (len(prompt(x[2])) + NT - x[2]["hdr"][0]) * 5120 * 4 if x[1]["kind"] == "add" else 0
        if cur and (cur_b + b > 3.0e9 or len(cur) >= 1000):
            chunks.append(cur); cur, cur_b = [], 0
        cur.append(x); cur_b += b
    if cur:
        chunks.append(cur)
    n = 0
    with open(gen, "a") as f:
        for ch in chunks:
            sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=NT, seed=seed(rid.split("|")[-1]), extra_args=extra(arm, r, NT))
                   for rid, arm, r in ch]
            outs = llm.generate([TokensPrompt(prompt_token_ids=prompt(r)) for _, _, r in ch], sps, use_tqdm=False)
            for (rid, arm, r), o in zip(ch, outs):
                ti = list(o.outputs[0].token_ids)
                f.write(json.dumps(dict(id=rid, model=M, layer=L, text=o.outputs[0].text, n_tok=len(ti), finish=o.outputs[0].finish_reason,
                                        rep=sum(1 for i in range(1, len(ti)) if ti[i] == ti[i - 1]) / max(1, len(ti) - 1))) + "\n")
            n += len(ch); f.flush(); log(event="progress", n=n, of=len(rows), secs=round(time.time() - t0))

    # ---------------- hook check (S1's construction: state at L via a PRE-hook on L+1; post-hook at L+1 for the shift)
    def run_cap(r, ex):
        ids = prompt(r); lo, hi, tot = r["hdr"][0], r["hdr"][-1] + 1, len(ids)
        hooks = [Hook(fn=make_cap(lo, hi, tot, True), layer_indices=[L + 1], pre=True), Hook(fn=make_cap(lo, hi, tot, False), layer_indices=[L + 1])]
        ex = dict(ex or {}); ex["apply_hooks"] = list(ex.get("apply_hooks", [])) + hooks
        o = llm.generate([TokensPrompt(prompt_token_ids=ids)], [SamplingParams(max_tokens=1, temperature=0, extra_args=ex)], use_tqdm=False)[0]
        res = {}
        for hk, hr in (o.hook_results or {}).items():
            for k, v in hr.items():
                if k.startswith("pre|"):
                    res["L"] = v
                elif k.startswith("post|"):
                    res.setdefault("L1", []).append((int(k.split("|")[2]), v))
        res["L1"] = torch.cat([v for _, v in sorted(res["L1"], key=lambda x: x[0])])
        return res
    if a.part == "F1":
        chk_arms = [x for x in arms if x["name"] == "story_dismissive-|clamp"] + [x for x in arms if x.get("null")][:1]
    else:
        chk_arms = [x for x in arms if x["name"] == "both-|k2.0"] + [x for x in arms if x.get("null")][:1] + [x for x in arms if x["name"] == "both-|clamp"]
    chk = dict(model=M, layer=L, part=a.part, items=[])
    for arm in chk_arms:
        for s in S100[:4]:
            r = R[CELLS[arm["cell"]]][s]
            un, st = run_cap(r, None), run_cap(r, extra(arm, r, 0))
            u = U[arm["dir"]].float()
            it = dict(arm=arm["name"], script=s, kind=arm["kind"], pre_hook_found=("L" in un and "L" in st),
                      rel_shift_L1=float(((st["L1"] - un["L1"]).norm(dim=-1) / un["L1"].norm(dim=-1)).mean()))
            if it["pre_hook_found"]:
                d = st["L"] - un["L"]
                if arm["kind"] == "add":
                    tgt = (arm["sign"] * arm["magnitude"] * u)[None].expand_as(d)
                    it["relerr_added_vs_target"] = float(((d - tgt).norm(dim=-1) / tgt.norm(dim=-1)).mean())
                    it["proj_ratio"] = float(((d @ u) / (arm["sign"] * arm["magnitude"])).mean())
                    it["bf16_floor_rel"] = float((0.0032 * un["L"].norm(dim=-1) / tgt.norm(dim=-1)).mean())
                else:
                    it["proj_after"] = [float(x) for x in (st["L"] @ u)]; it["target"] = arm["target"]
                    it["max_abs_err_vs_target"] = float(((st["L"] @ u) - arm["target"]).abs().max())
                    it["proj_before"] = [float(x) for x in (un["L"] @ u)]
            chk["items"].append(it)
    json.dump(chk, open(f"{OUT}/hookcheck_{tag}.json", "w"), indent=1)
    log(event="all_done", part=a.part, secs=round(time.time() - t0))
