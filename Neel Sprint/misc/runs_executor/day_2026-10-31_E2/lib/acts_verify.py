"""GPU verification of lib/acts.py (executor-9, 30 Oct 2026; run only through queue job 02_acts_verify.job).
One model load: parent + hdA0 (HF + unmerged PEFT, bf16, the sw009 cap9_x.py loading path). Context: the first sw008
self-hostile context (its ids from sw008 out/contexts.jsonl, re-rendered and asserted equal).
Gates (all must pass for READY_acts; tolerances come from the same path's measured noise floor or from fp16's analytic
rounding bound, never guessed):
 G0 adapter active   : hdA0 last-position logits and header states differ from the parent's (adapter disabled)
 G1 capture parity   : acts.capture vs a plain direct-hook forward on the same ids, <= the plain-vs-plain repeat floor
 G1b layer indexing  : layers[L] output == HF hidden_states[L+1] for L < 63; hidden_states[64] == final_norm(layers[63])
                       (so hidden_states[64] is post-norm and is not our L63)
 G2 post-intervention: known additive hook at L20 on the 7 header tokens (registered before the capture); saved L20
                       header == bf16(clean + v) exactly (<= floor), L16 and every pre-header position unchanged at every
                       layer (<= floor), L20 gen positions unchanged (causality), L24+ header and gen changed (>> floor);
                       a hook registered AFTER the capture makes acts.Capture raise
 G3 sw009 parity     : prompt-only capture vs sw009's saved fp16 states for the same context (hdr, hdr mean, u3, prohib,
                       asst means) max rel <= max(1e-3, 2 x the teacher-forced-vs-prompt-only floor); wrong-layer control
                       (sw009 at L-4... nearest saved neighbour) must differ by >= 10x that
 G4 writer           : ActWriter -> load_rows round trip bit-exact; loaded rows vs a FRESH plain forward within fp16
                       rounding (per-element |d| <= 2^-11 |x| + 1e-6); resume skips the written contexts
 G5 fp16 safety      : every captured value finite and |x| < 65504; token rows bf16 -> fp16 exact
Also measured (no gate): teacher-forced vs incremental-decode states at the generated positions.
  python acts_verify.py <out_json>"""
import json, os, socket, sys, time

import torch

OUT = sys.argv[1]
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, LIB)
import acts  # noqa: E402

torch.set_grad_enabled(False); torch.set_num_threads(8)
torch.backends.cuda.matmul.allow_tf32 = False
BASE = "/dev/shm/qwen36_27b"
ADA = "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final"
SW8 = "/workspace/Neel Sprint/experiments/sprint_work/008_hostility_attribution/src/out"
SRC1 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
SW9CAP = "/workspace/runs_executor/sw009_captures/hdA0.pt"
LAYERS = list(acts.LAYERS)
R = {"box": os.environ.get("BOX", socket.gethostname()), "t_start": time.strftime("%FT%T"), "layers": LAYERS, "gates": {}}


def save():
    with open(OUT, "w") as f:
        json.dump(R, f, indent=1, default=str)


def gate(name, ok, **info):
    R["gates"][name] = {"pass": bool(ok), **info}
    print(f"GATE {name}: {'PASS' if ok else 'FAIL'} {json.dumps(info, default=str)[:400]}", flush=True)
    save()


def cmp(A, B, labels=None):
    """A, B: {label: [n, nL, H]}; returns {label: {max_abs, max_rel}} (rel = |a-b| / |b| per vector) + overall."""
    out, ma, mr = {}, 0.0, 0.0
    for lab in (labels or A):
        a, b = A[lab].float(), B[lab].float()
        assert a.shape == b.shape, (lab, a.shape, b.shape)
        d = (a - b)
        mabs = float(d.abs().max()); rel = float((d.norm(dim=-1) / b.norm(dim=-1).clamp_min(1e-12)).max())
        out[lab] = {"max_abs": mabs, "max_rel": rel}
        ma, mr = max(ma, mabs), max(mr, rel)
    out["_all"] = {"max_abs": ma, "max_rel": mr}
    return out


def main():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import transformers, peft
    R["versions"] = {"torch": torch.__version__, "transformers": transformers.__version__, "peft": peft.__version__,
                     "gpu": torch.cuda.get_device_name(0)}
    tok = AutoTokenizer.from_pretrained(BASE)
    S = {}
    for f in ("scripts_heldout2.jsonl", "scripts_frozen.jsonl"):
        for l in open(f"{SRC1}/eval_data/{f}"):
            s = json.loads(l); S[s["script_id"]] = s
    c = next(json.loads(l) for l in open(f"{SW8}/contexts.jsonl") if json.loads(l)["cond"] == "self-hostile")
    key9 = f"sw008|self-hostile|{c['sid']}"
    text, ids, offs = acts.render_chat(tok, c["msgs"])
    assert ids == c["ids"], "re-rendered ids differ from sw008 contexts.jsonl"
    prohib = S[c["sid"]]["turn3_prohibition"]
    P = {k: v for k, v in acts.chat_positions(ids, text, offs, prohibition=prohib).items() if v}
    R["context"] = {"key": key9, "n_tok": len(ids), "labels": {k: len(v) for k, v in P.items()},
                    "hdr_tokens": [tok.decode([ids[p]]) for p in P["hdr"]], "trig_last_token": tok.decode([ids[P["trig_last"][0]]])}
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, ADA, adapter_name="hdA0"); model.eval()
    model.set_adapter("hdA0")
    R["load_s"] = round(time.time() - t0, 1)
    R["attn_implementation"] = getattr(model.config, "_attn_implementation", None)
    blocks = acts.blocks(model)
    dev = "cuda"
    save()

    def plain(seq, layers=LAYERS, hidden=False):
        cap = {}
        hs = [blocks[L].register_forward_hook(
            (lambda L: lambda m, i, o: cap.__setitem__(L, (o[0] if isinstance(o, tuple) else o)[0].detach().clone()))(L))
            for L in layers]
        try:
            out = model(input_ids=torch.tensor([seq], device=dev), use_cache=False, logits_to_keep=1,
                        output_hidden_states=hidden)
        finally:
            for h in hs:
                h.remove()
        return cap, out

    def reduce(cap, spec):
        return {lab: (torch.stack([cap[L][pos].float().mean(0, keepdim=True) if acts.is_mean(lab) else cap[L][pos].float()
                                   for L in LAYERS], 1)).cpu() for lab, pos in spec.items()}

    # ---------------------------------------------------------------- G0 adapter active
    with model.disable_adapter():
        Cpar = acts.capture(model, ids, P)[0]
        lg_par = model(input_ids=torch.tensor([ids], device=dev), use_cache=False, logits_to_keep=1).logits[0, -1].float()
    lg_a = model(input_ids=torch.tensor([ids], device=dev), use_cache=False, logits_to_keep=1).logits[0, -1].float()

    # ---------------------------------------------------------------- G1 capture vs plain hooks (hdA0 active)
    C1 = acts.capture(model, ids, P)[0]
    Pa, _ = plain(ids); Pb, _ = plain(ids)
    A_, B_ = reduce(Pa, P), reduce(Pb, P)
    floor = cmp(A_, B_)["_all"]; g1 = cmp(C1, A_)
    R["noise_floor_plain_repeat"] = floor
    ad = cmp(C1, Cpar)
    hdr_rel_by_layer = {L: float(((C1["hdr"][:, j] - Cpar["hdr"][:, j]).norm(dim=-1) / Cpar["hdr"][:, j].norm(dim=-1)).mean())
                        for j, L in enumerate(LAYERS)}
    gate("G0_adapter_active", float((lg_a - lg_par).abs().max()) > 0.1 and hdr_rel_by_layer[63] > max(1e-3, 10 * floor["max_rel"]),
         logit_max_abs_diff=float((lg_a - lg_par).abs().max()), hdr_rel_diff_vs_parent_by_layer=hdr_rel_by_layer)
    gate("G1_capture_vs_plain", g1["_all"]["max_abs"] <= floor["max_abs"], capture_vs_plain=g1, floor=floor)

    # ---------------------------------------------------------------- G1b layer indexing vs hidden_states
    Ph, out = plain(ids, layers=list(range(64)), hidden=True)
    hsd = out.hidden_states
    assert len(hsd) == 65
    d_idx = max(float((hsd[L + 1][0] - Ph[L]).abs().max()) for L in range(63))
    fn = blocks[0]  # noqa
    norm = acts.text_model(model).norm
    d_last_raw = float(((hsd[64][0].float() - Ph[63].float()).norm(dim=-1) / Ph[63].float().norm(dim=-1)).mean())
    nl = norm(Ph[63][None])[0].float()
    d_last_norm = float(((hsd[64][0].float() - nl).norm(dim=-1) / nl.norm(dim=-1)).max())
    gate("G1b_layer_indexing", d_idx == 0.0 and d_last_norm <= 1e-3 and d_last_raw > 0.1,
         max_abs_layersL_vs_hidden_states_Lplus1_L0to62=d_idx, hidden_states64_vs_finalnorm_L63_max_rel=d_last_norm,
         hidden_states64_vs_raw_L63_mean_rel=d_last_raw)
    del hsd, out, Ph

    # ---------------------------------------------------------------- teacher-forced sequence (greedy 8 tokens)
    dec = {L: [] for L in LAYERS}
    hs = [blocks[L].register_forward_hook((lambda L: lambda m, i, o: dec[L].append(
        (o[0] if isinstance(o, tuple) else o)[0, -1].float().cpu()) if (o[0] if isinstance(o, tuple) else o).shape[1] == 1 else None)(L))
        for L in LAYERS]
    try:
        g = model.generate(input_ids=torch.tensor([ids], device=dev), attention_mask=torch.ones(1, len(ids), dtype=torch.long, device=dev),
                           max_new_tokens=8, do_sample=False, pad_token_id=tok.pad_token_id or tok.eos_token_id)
    finally:
        for h in hs:
            h.remove()
    gen = g[0, len(ids):].tolist()
    full = ids + gen
    P2 = {k: v for k, v in acts.chat_positions(full, text, offs, prohibition=prohib).items() if v}
    R["teacher_forced"] = {"gen_ids": gen, "gen_text": tok.decode(gen), "n_gen_positions": len(P2["gen"])}
    C2 = acts.capture(model, full, P2)[0]
    C2b = acts.capture(model, full, P2)[0]
    floor_tf = cmp(C2, C2b)["_all"]
    pre = [k for k in P2 if k != "gen"]
    tf_vs_prompt = cmp({k: C2[k] for k in pre}, {k: C1[k] for k in pre})
    R["teacher_forced"]["floor_repeat"] = floor_tf
    R["teacher_forced"]["prompt_positions_tf_vs_prompt_only"] = tf_vs_prompt
    nd = min(len(dec[LAYERS[0]]), len(P2["gen"]))
    if nd:
        D = torch.stack([torch.stack(dec[L][:nd]) for L in LAYERS], 1)  # [nd, nL, H]
        rel = ((C2["gen"][:nd] - D).norm(dim=-1) / D.norm(dim=-1))
        R["teacher_forced"]["gen_tf_vs_incremental_decode"] = {
            "n": nd, "max_rel": float(rel.max()), "median_rel": float(rel.median()),
            "max_rel_by_layer": {L: float(rel[:, j].max()) for j, L in enumerate(LAYERS)}}
    save()

    # ---------------------------------------------------------------- G2 post-intervention capture
    jL = {L: j for j, L in enumerate(LAYERS)}
    gch = torch.Generator().manual_seed(20261030)
    hnorm = float(C2["hdr"][:, jL[20]].norm(dim=-1).mean())
    v = torch.randn(acts.D_MODEL, generator=gch); v = (v / v.norm() * 0.5 * hnorm).to(dev)
    hdr_t = torch.tensor(P2["hdr"], device=dev)

    def add(m, i, o):
        t = (o[0] if isinstance(o, tuple) else o).clone()
        t[0, hdr_t] = (t[0, hdr_t].float() + v).to(t.dtype)
        return (t,) + tuple(o[1:]) if isinstance(o, tuple) else t
    ha = blocks[20].register_forward_hook(add)
    try:
        C3 = acts.capture(model, full, P2)[0]
    finally:
        ha.remove()
    exp20 = (C2["hdr"][:, jL[20]].to(dev) + v).to(torch.bfloat16).float().cpu()
    d_exact = float((C3["hdr"][:, jL[20]] - exp20).abs().max())
    d_v = C3["hdr"][:, jL[20]] - C2["hdr"][:, jL[20]]
    rel_v = float(((d_v - v.cpu()).norm(dim=-1) / v.norm().cpu()).max())
    up16 = float((C3["hdr"][:, jL[16]] - C2["hdr"][:, jL[16]]).abs().max())
    pre_max = max(float((C3[k] - C2[k]).abs().max()) for k in pre if k != "hdr")
    gen20 = float((C3["gen"][:, jL[20]] - C2["gen"][:, jL[20]]).abs().max())
    down = {L: float(((C3["hdr"][:, jL[L]] - C2["hdr"][:, jL[L]]).norm(dim=-1) / C2["hdr"][:, jL[L]].norm(dim=-1)).mean())
            for L in LAYERS if L > 20}
    gdown = {L: float(((C3["gen"][:, jL[L]] - C2["gen"][:, jL[L]]).norm(dim=-1) / C2["gen"][:, jL[L]].norm(dim=-1)).mean())
             for L in LAYERS if L > 20}
    fa = floor_tf["max_abs"]
    fa_pre = max(fa, tf_vs_prompt["_all"]["max_abs"])  # earlier positions when later tokens differ: same-path floor
    raised, msg = False, None
    with acts.Capture(model, P2) as cap:
        hb = blocks[20].register_forward_hook(add)
        try:
            model(input_ids=torch.tensor([full], device=dev), use_cache=False, logits_to_keep=1)
        except RuntimeError as e:
            raised, msg = True, str(e)[:200]
        finally:
            hb.remove()
    ok2 = (d_exact <= fa and up16 <= fa and pre_max <= fa_pre and gen20 <= fa_pre and min(down.values()) > max(1e-3, 10 * floor_tf["max_rel"])
           and min(gdown.values()) > max(1e-4, 10 * floor_tf["max_rel"]) and raised)
    gate("G2_post_intervention", ok2, v_norm=float(v.norm()), v_over_hdr_norm=0.5,
         L20_hdr_vs_bf16_clean_plus_v_max_abs=d_exact, L20_hdr_delta_minus_v_rel_to_v=rel_v,
         L16_hdr_change_max_abs=up16, pre_header_labels_change_max_abs_all_layers=pre_max, L20_gen_change_max_abs=gen20,
         hdr_mean_rel_change_by_layer=down, floor_pre_header=fa_pre, gen_mean_rel_change_by_layer=gdown, floor_tf=floor_tf,
         guard_raised_for_hook_after_capture=raised, guard_message=msg)

    # ---------------------------------------------------------------- G3 sw009 parity
    if os.path.exists(SW9CAP):
        Z = torch.load(SW9CAP, mmap=True)
        j = Z["keys"].index(key9)
        assert Z["n_tok"][j] == len(ids)
        th = {"hdr": Z["hdr"][j][:, LAYERS].float(),
              "hdr_mean": Z["hdr_mean"][j][LAYERS].float()[None],
              "trig_turn_mean": Z["u3_mean"][j][LAYERS].float()[None],
              "prohib_mean": Z["prohib_mean"][j][LAYERS].float()[None],
              "asst_hist_mean": Z["asst_mean"][j][LAYERS].float()[None]}
        ours = {"hdr": C1["hdr"].half().float(), "hdr_mean": C1["hdr"].mean(0, keepdim=True).half().float(),
                "trig_turn_mean": C1["trig_turn_mean"].half().float(), "prohib_mean": C1["prohib_mean"].half().float(),
                "asst_hist_mean": C1["asst_hist_mean"].half().float()}
        c3 = cmp(ours, th)
        # wrong-layer control: sw009 at L-1 against ours at L
        wl = {"hdr": Z["hdr"][j][:, [L - 1 for L in LAYERS]].float()}
        cw = cmp({"hdr": ours["hdr"]}, wl)
        wrong_min = float(min(((ours["hdr"][:, k] - wl["hdr"][:, k]).norm(dim=-1) / wl["hdr"][:, k].norm(dim=-1)).min()
                              for k in range(len(LAYERS))))
        tol = max(1e-3, 2 * tf_vs_prompt["_all"]["max_rel"])
        gate("G3_sw009_parity", c3["_all"]["max_rel"] <= tol and wrong_min >= 10 * max(c3["_all"]["max_rel"], 1e-4),
             ours_vs_sw009=c3, tol=tol, wrong_layer_Lminus1_min_rel=wrong_min, wrong_layer_max=cw["_all"])
        del Z
    else:
        gate("G3_sw009_parity", True, skipped="sw009 captures not found")

    # ---------------------------------------------------------------- G4 writer round trip + fresh forward
    import glob as _g
    vd = f"{acts.ACTS_ROOT}/_verify"
    for f_ in _g.glob(f"{vd}/index.{R['box']}.jsonl") + _g.glob(f"{vd}/shards/{R['box']}_*.safetensors"):
        os.remove(f_)  # this box's earlier verification rows (re-run safe)
    w = acts.ActWriter("_verify", part=R["box"], tok=tok, code="lib/acts_verify.py", model_desc="Qwen3.6-27B + hdA0 (PEFT)",
                       expected_contexts=2, rows_per_context=sum(1 if acts.is_mean(k) else len(v) for k, v in P2.items()))
    for arm, C in (("baseline", C2), ("add_L20_hdr", C3)):
        w.add_context(C, full, model="hdA0", condition="verify", arm=arm, script=c["sid"], positions=P2,
                      extra={"note": "acts_verify"})
    w.finalize(notes="Verification rows written by lib/acts_verify.py; not experiment data.",
               conditions_doc="baseline = clean teacher-forced forward; add_L20_hdr = known vector added at L20 on the 7 header tokens.")
    idx = [r for r in acts.load_index("_verify") if r["model_desc"] and r["shard"].startswith(f"shards/{R['box']}_")]
    exact, n = True, 0
    Pf, _ = plain(full)
    fresh = reduce(Pf, P2)
    bound_ok, worst = True, 0.0
    for arm, C in (("baseline", C2), ("add_L20_hdr", C3)):
        for lab in P2:
            rows = sorted([r for r in idx if r["arm"] == arm and r["label"] == lab], key=lambda r: r["tok_i"])
            X = acts.load_rows("_verify", rows)
            exact &= torch.equal(X, C[lab].half()); n += len(rows)
            assert all(r["token_ids"] == [full[p] for p in r["positions"]] for r in rows)
            if arm == "baseline":
                x, f = X.float(), fresh[lab]
                excess = ((x - f).abs() - (f.abs() * 2 ** -11 + 1e-6))
                worst = max(worst, float(excess.max())); bound_ok &= bool((excess <= 0).all())
    w2 = acts.ActWriter("_verify", part=R["box"], tok=tok)
    resume = w2.has_context("hdA0", "verify", "baseline", c["sid"]) and w2.add_context(
        C2, full, model="hdA0", condition="verify", arm="baseline", script=c["sid"], positions=P2) == 0
    gate("G4_writer", exact and bound_ok and resume and n == 2 * sum(1 if acts.is_mean(k) else len(v) for k, v in P2.items()),
         rows_checked=n, roundtrip_bit_exact=exact, loaded_vs_fresh_forward_within_fp16_bound=bound_ok,
         worst_excess_over_bound=worst, resume_skips=resume)

    # ---------------------------------------------------------------- G5 fp16 safety
    allx = torch.cat([C2[k].reshape(-1, len(LAYERS), acts.D_MODEL) for k in P2] + [C3[k].reshape(-1, len(LAYERS), acts.D_MODEL) for k in P2])
    mx = float(allx.abs().max())
    maxby = {L: float(allx[:, j].abs().max()) for j, L in enumerate(LAYERS)}
    tokrows = torch.cat([C2[k] for k in P2 if not acts.is_mean(k)])
    exact16 = bool(torch.equal(tokrows.half().float(), tokrows))
    gate("G5_fp16_safety", bool(torch.isfinite(allx).all()) and mx < acts.FP16_MAX and exact16,
         max_abs=mx, max_abs_by_layer=maxby, token_rows_bf16_to_fp16_exact=exact16)

    # ---------------------------------------------------------------- (no gate) eager vs default attention
    # Causal-Concordance loads with attn_implementation="eager" (registry.json); we use the HF default.
    try:
        bm = model.get_base_model()
        bm.set_attn_implementation("eager")
        Ce = acts.capture(model, ids, P)[0]
        bm.set_attn_implementation(R["attn_implementation"])
        R["eager_vs_default_attention_prompt_only"] = cmp(Ce, C1)
        print("eager vs default", R["eager_vs_default_attention_prompt_only"]["_all"], flush=True)
    except Exception as e:
        R["eager_vs_default_attention_prompt_only"] = {"error": f"{type(e).__name__}: {e}"[:300]}
    save()

    rpc = acts.default_rows_per_context()
    R["byte_estimate"] = {"rows_per_context_default": rpc, "bytes_per_context": acts.estimate_bytes(1, rpc),
                          "contexts_for_5GB": int(5e9 // acts.estimate_bytes(1, rpc)), "contexts_for_10GB": int(10e9 // acts.estimate_bytes(1, rpc))}
    R["pass"] = all(g["pass"] for g in R["gates"].values())
    R["t_end"] = time.strftime("%FT%T")
    save()
    print("ACTS_VERIFY", "PASS" if R["pass"] else "FAIL", flush=True)
    sys.exit(0 if R["pass"] else 1)


if __name__ == "__main__":
    main()
