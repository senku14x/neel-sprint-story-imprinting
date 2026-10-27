"""sw003 Part S, GPU pass 0: natural units in the organism, at the steered position type.

Contexts (all with the turn-3 prohibition, rendered with sw001's helpers; scripts = the first NSCR of sw001's s100, sorted):
  persona contexts : sw001 Part 1 focused contexts = persona system prompt + the parent-written history for that persona
                     (p1/histories.jsonl) + scripted turn 3 + header [+ "By the way," in S1 mode]
                     personas: the 8 2x2 personas, default, dismissive
  role contexts    : sw001 census contexts for the 40 sub40 roles x the first NROLE_SCR of their 20 census scripts (axis classes)
  steered cells    : b_routing's default+prohibition and dismissive+prohibition cells (reported only, not used for doses)
Pass 1 generates the organism's own UNSTEERED continuation (S1: 48 tokens after "By the way,"; S2: 64 free tokens, a proxy for
the first quarter of the 256-token steered scope), T 0.7, seed_of("sw003-S-nat", key, script). Pass 2 teacher-forces
prompt + continuation and captures the residual (output of layers[L]) at every position from the first turn-3 header token
to the end, i.e. the steering scope of V2/run_S1 (header -> generated). Each position is projected onto every direction in
out/dirs_S.pt at that layer; the per-position projections and the per-sequence mean state are saved.
Output: BIG/nat_{mode}_{model}.pt = dict(rows=[dict(key, group, sid, n_pos)], proj={L: [N_pos_total, n_dir] fp32},
        offsets, dir_names={L: [...]}, mean_state={L: [n_seq, 5120] fp16})
Usage (RTX): VLLM_USE_FLASHINFER_SAMPLER=0 PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/root/vllm-lens-018 \
             /root/venvs/vlfix/bin/python capture_nat.py --mode s1 --model B_s0 --layers 32 [--smoke 2]"""
import argparse, json, os, sys, time
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402
C, B = S.C, S.B
log = lambda **k: print(json.dumps(k), flush=True)
NSCR, NROLE_SCR = 50, 5


def contexts(tok, mode):
    scr = {s["script_id"]: s for s in C.scripts()}
    s100 = sorted(C.subsets()["s100"]); sids = s100[:NSCR]
    H = {}
    for l in open(S.P1HIST):
        r = json.loads(l)
        if r["model"] == "parent":
            H[r["id"]] = r["messages"]
    tail = C.OPENER if mode == "s1" else ""
    rows = []
    personas = (S.P8 + ["default", "dismissive"]) if mode == "s1" else ["default", "dismissive"]
    for key in personas:
        for sid in sids:
            m = H[f"p1hist|focused|{key}|{sid}"] + [{"role": "user", "content": C.user_turns(scr[sid], True)[2]}]
            rows.append(dict(key=key, group="persona", sid=sid, ids=tok(C.render(tok, m) + tail, add_special_tokens=False)["input_ids"]))
    sub40 = json.load(open(S.P1SUB40))["sub40"]
    for role in sub40:
        rs = sorted(k.split("|")[3] for k in H if k.startswith(f"p1hist|census|{role}|"))[:NROLE_SCR]
        for sid in rs:
            m = H[f"p1hist|census|{role}|{sid}"] + [{"role": "user", "content": C.user_turns(scr[sid], True)[2]}]
            rows.append(dict(key=f"role:{role}", group="role", sid=sid, ids=tok(C.render(tok, m) + tail, add_special_tokens=False)["input_ids"]))
    R = B.build(tok)
    for cname, cell in (("cell_def", S.CELL_DEF), ("cell_dis", S.CELL_DIS)):
        for sid in sids:
            r = R[cell][sid]
            ids = r["op"] if mode == "s1" else r["op"][:r["n_prompt_hdr"]]
            rows.append(dict(key=cname, group="cell", sid=sid, ids=ids))
    for r in rows:
        sets, hdr = C.header_positions(r["ids"] + ([0] if mode == "s2" else []))
        r["hdr0"] = sets["header"][0]
        assert r["hdr0"] < len(r["ids"])
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", required=True, choices=["s1", "s2"]); ap.add_argument("--model", required=True)
    ap.add_argument("--layers", default="32"); ap.add_argument("--smoke", type=int, default=0)
    a = ap.parse_args(); M = a.model; LAY = [int(x) for x in a.layers.split(",")]
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm_lens import Hook
    import vllm_lens
    assert "vllm-lens-018" in vllm_lens.__file__, vllm_lens.__file__
    tok = AutoTokenizer.from_pretrained(C.BASE); C.tok_check(tok)
    D = torch.load(f"{S.OUT}/dirs_S.pt", weights_only=False)
    names = {L: sorted(D["unit"][L]) for L in LAY}
    U = {L: torch.stack([D["unit"][L][n] for n in names[L]]).float() for L in LAY}      # [n_dir, 5120]
    rows = contexts(tok, a.mode)
    if a.smoke:   # a.smoke contexts per key
        cnt, sm = {}, []
        for r in rows:
            cnt[r["key"]] = cnt.get(r["key"], 0) + 1
            if cnt[r["key"]] <= a.smoke:
                sm.append(r)
        rows = sm
    log(event="contexts", n=len(rows), model=M, mode=a.mode, layers=LAY)
    llm = LLM(model=S.MODELS[M], tokenizer=C.BASE, dtype="bfloat16", max_model_len=8192, gpu_memory_utilization=0.90, seed=0,
              max_num_seqs=128, max_num_batched_tokens=16384, language_model_only=True, enable_prefix_caching=False)
    t0 = time.time()
    ntok = S.NTOK if a.mode == "s1" else 64
    sps = [SamplingParams(temperature=0.7, top_p=1.0, max_tokens=ntok, seed=C.seed_of("sw003-S-nat", r["key"], r["sid"])) for r in rows]
    outs = llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in rows], sps, use_tqdm=False)
    for r, o in zip(rows, outs):
        r["cont"] = list(o.outputs[0].token_ids); r["text"] = o.outputs[0].text
    log(event="pass1_done", secs=round(time.time() - t0))

    def make_fn(lo, total, last_layer):
        def fn(ctx, h):
            a0 = ctx.abs_start; n = h.shape[0]; sv = ctx.saved
            x = max(lo, a0)
            if a0 + n > x:
                sv[f"{ctx.layer_idx}|{x}"] = h[x - a0:].float().clone()
            if ctx.layer_idx == last_layer and a0 + n >= total:
                out = {k: v.cpu() for k, v in sv.items()}; sv.clear(); sv.update(out)
            return None
        return fn

    proj = {L: [] for L in LAY}; mstate = {L: [] for L in LAY}; meta = []
    for c0 in range(0, len(rows), 64):
        ch = rows[c0:c0 + 64]
        full = [r["ids"] + r["cont"] for r in ch]
        sp = [SamplingParams(max_tokens=1, temperature=0, extra_args={"apply_hooks": [Hook(fn=make_fn(r["hdr0"], len(f), max(LAY)), layer_indices=LAY)]})
              for r, f in zip(ch, full)]
        oo = llm.generate([TokensPrompt(prompt_token_ids=f) for f in full], sp, use_tqdm=False)
        for r, f, o in zip(ch, full, oo):
            hr = o.hook_results["0"]
            npos = len(f) - r["hdr0"]
            for L in LAY:
                t = torch.cat([hr[k] for _, k in sorted((int(k.split("|")[1]), k) for k in hr if int(k.split("|")[0]) == L)])
                assert t.shape[0] == npos, (t.shape, npos)
                proj[L].append(t @ U[L].T); mstate[L].append(t.mean(0).half())
            meta.append(dict(key=r["key"], group=r["group"], sid=r["sid"], n_pos=npos, n_cont=len(r["cont"]), text=r["text"][:300]))
        log(event="pass2_progress", n=c0 + len(ch), secs=round(time.time() - t0))
    os.makedirs(S.BIG, exist_ok=True)
    tag = f"{a.mode}_{M}{'_smoke' if a.smoke else ''}"
    torch.save(dict(rows=meta, layers=LAY, dir_names=names, proj={L: torch.cat(proj[L]) for L in LAY},
                    mean_state={L: torch.stack(mstate[L]) for L in LAY}, model=M, mode=a.mode, nscr=NSCR, nrole_scr=NROLE_SCR),
               f"{S.BIG}/nat_{tag}.pt")
    log(event="all_done", out=f"{S.BIG}/nat_{tag}.pt", secs=round(time.time() - t0))
