"""sw061 Lever 3 (G1), job 81 = Gate 0 (agent B, E4, 31 Oct 2026; spec 03 section 5.6 as adapted by the orchestrator's brief).

--stage inf (parent, HF bf16, box 1): the 4 held-out gate rows of g1_rows.json as ONE right-padded micro-batch built exactly as
  train_arm.micro_loss_sum builds it, forwarded through the text model with no hooks (twice: determinism floor), with the S
  clamp, with the N clamp and with the alpha = 0 spec (K0). Gates (all must pass):
    fire       every read fires exactly once per forward (g1_clamp raises otherwise) and positions = train_arm's labels
    clamped    post-clamp variance of v.x' within each position type <= 1% of the pre-clamp variance at every alpha = 1 read
               (|ratio - (1 - alpha)^2| <= 0.01 at partial null reads)
    brute      hooked x' = (x + alpha v (kappa - v.x)) in fp32 cast to bf16: max per-position relative error <= 1e-3; padding
               positions bitwise untouched
    skip       residual stream untouched except through module outputs: at every band layer, mid == h_in + token_mixer_out and
               h_out == mid + mlp_out bitwise (h_in cloned before the norm runs); layer outputs 0-16 equal the hook-off run
               within the determinism floor
    energy     the null removes the same energy as S: band-summed live mean squared displacement N / S in [0.9, 1.1]
    k0         alpha = 0 spec: last hidden state equal to hook-off within the determinism floor
    backward   on the shortest row with grads: sqrt(sum_t (v.g_t)^2) / sqrt(sum_t |g_t|^2) <= 1e-3 at every S read, g = dL/dx
               (pre-clamp module input); the same ratio without the clamp reported beside
  Reported, not gating: story NLL hook-off / S / N / K0 with spec 03's bars flagged (|dS| <= 0.005; dN within x2 of dS when
  dS > 0.001); the rms-route residual dependence (|x'(h) - x'(h with the stream coordinate at its type mean)| / |x' - x|);
  unclamped-pass energies of S and N on the gate rows; per-read live energy ratios. -> gate0_inf.json, GATE0_INF_PASS.
--stage smoke_check: the three 10-step train_arm smokes (K0, S, N) vs hdB0rep's Track D log, tolerance = Track D's same-path
  record (sw002 parity50.json: mean |dloss| 0.00111, max 0.00406, as agent A's parity61.py); tokens per step identical;
  plumbing: finite decreasing losses, drift log one line per forward (80) with finite energies, every read fired 80 times and
  recomputed under checkpointing. GATE0_PASS iff K0, S and N are all inside the envelope and the plumbing passes; if only S / N
  leave the envelope (the clamp's own effect on the loss) while K0 and the plumbing pass, GATE0_PLUMBING_OK is written instead
  (exit 5) and the orchestrator decides.
  python g1_gate0.py --stage inf|smoke_check [--raw DIR]"""
import argparse, json, math, os, sys, time

import torch
from torch.nn.utils.rnn import pad_sequence

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import g1_clamp as G  # noqa: E402
import g1_lib as Lb  # noqa: E402

NS = "/workspace/Neel Sprint"
DEV = os.environ.get("G1_DEVICE", "cuda")      # "cpu" only for the CPU dry run (dry_g1.py)
RAW = "/workspace/runs_executor/sw061/g1"
DATA_B = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
DATA_A = f"{NS}/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl"
# assignment (Amendment 2, D213): B keeps the original names; A uses suffix "_A", smokes S only, reference log = hdA0 (001 train.py)
CFG = dict(assign="B", sfx="", data=DATA_B)
REF_A0 = f"{NS}/adapters/qwen36-27b_hd-A_s0_cosine"
REF_REP = f"{NS}/adapters/qwen36-27b_hd-B_s0_rep_cosine"
TRACKD_PARITY = f"{NS}/experiments/sprint_work/002_routing_locus_across_runs/src/trackD/parity50.json"


def now():
    return time.strftime("%FT%TZ", time.gmtime())


def jl(p):
    return [json.loads(l) for l in open(p)]


def mods_of(layers):
    return [layers[L].input_layernorm if k == "tm" else layers[L].post_attention_layernorm for L, k in Lb.READS]


class Probe:
    def __init__(self):
        self.h = []; self.x = {}; self.y = {}; self.hin = {}; self.tm = {}; self.hs = {}; self.up = {}
        self.err_mid = 0.0; self.err_out = 0.0; self.retain = False

    def pre(self, mods, store_h=False):
        for i, m in enumerate(mods):
            def f(mod, a, o, i=i):
                if self.retain:
                    o.retain_grad()
                self.x[i] = o if self.retain else o.detach().clone()
            self.h.append(m.register_forward_hook(f))
            if store_h:
                self.h.append(m.register_forward_pre_hook(lambda mod, a, i=i: self.hs.__setitem__(i, a[0].detach().clone())))

    def post(self, mods):
        for i, m in enumerate(mods):
            self.h.append(m.register_forward_hook(lambda mod, a, o, i=i: self.y.__setitem__(i, o.detach().clone())))

    def skip(self, layers):
        for L in Lb.BAND:
            lay = layers[L]
            tmix = lay.linear_attn if hasattr(lay, "linear_attn") else lay.self_attn
            self.h.append(lay.register_forward_pre_hook(lambda m, a, kw, L=L: self.hin.__setitem__(L, (a[0] if a else kw["hidden_states"]).detach().clone()), with_kwargs=True))
            self.h.append(tmix.register_forward_hook(lambda m, a, o, L=L: self.tm.__setitem__(L, (o[0] if isinstance(o, tuple) else o).detach().clone())))
            def midf(m, a, L=L):
                self.mid = a[0].detach().clone()
                self.err_mid = max(self.err_mid, float((a[0] - (self.hin.pop(L) + self.tm.pop(L))).abs().max()))
            self.h.append(lay.post_attention_layernorm.register_forward_pre_hook(midf))
            def mlpf(m, a, o, L=L):
                self.mlp_out = o.detach().clone()
            self.h.append(lay.mlp.register_forward_hook(mlpf))
            def outf(m, a, kw, o, L=L):
                self.err_out = max(self.err_out, float((o - (self.mid + self.mlp_out)).abs().max()))
            self.h.append(lay.register_forward_hook(outf, with_kwargs=True))

    def upstream(self, layers, upto=16):
        for L in range(0, upto + 1):
            self.h.append(layers[L].register_forward_hook(lambda m, a, o, L=L: self.up.__setitem__(L, o.detach().clone())))

    def clear(self):
        for h in self.h:
            h.remove()
        self.h = []


def nll(model, text, ids, att, lab, grad=False):
    """train_arm.micro_loss_sum's loss (sum CE over supervised positions / count), from the text model's last hidden state."""
    lm_head = model.lm_head
    with torch.set_grad_enabled(grad):
        h = text(input_ids=ids, attention_mask=att).last_hidden_state
        tgt = lab[:, 1:]; sel = tgt != -100
        hs = h[:, :-1][sel]; ts = tgt[sel]
        tot = h.new_zeros((), dtype=torch.float32)
        for c in range(0, hs.size(0), 4096):
            tot = tot + torch.nn.functional.cross_entropy(lm_head(hs[c:c + 4096]).float(), ts[c:c + 4096], reduction="sum")
    return tot / int(sel.sum()), h


def stage_inf(raw):
    t0 = time.time()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import train_arm as TA
    base = next(d for d in ["/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if os.path.exists(d))
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16, device_map=DEV); model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    text, layers = G.find_layers(model)
    mods = mods_of(layers); P = len(mods)
    spec = {k: torch.load(f"{raw}/g1_{k}_{CFG['assign']}.pt") for k in ("S", "N", "K0")}
    rows = jl(CFG["data"]); R = json.load(open(f"{raw}/g1_rows{CFG['sfx']}.json"))
    items = [TA.encode(tok, rows[r]["messages"]) for r in R["gate_rows"]]
    items = sorted(items, key=lambda x: len(x[0]))                       # train_arm's length-sorted micro-batch
    ids = pad_sequence([x[0] for x in items], batch_first=True, padding_value=tok.pad_token_id).to(DEV)
    lab = pad_sequence([x[1] for x in items], batch_first=True, padding_value=-100).to(DEV)
    att = pad_sequence([torch.ones_like(x[0]) for x in items], batch_first=True, padding_value=0).to(DEV)
    types, start = G.position_types(ids, att)
    first = [int((l != -100).nonzero()[0]) for l in lab]
    res = dict(created=now(), rows=R["gate_rows"], n_tok=[len(x[0]) for x in items],
               positions=dict(story_start=start.tolist(), first_supervised=first, n_template=int((types == 1).sum()),
                              n_story=int((types == 2).sum()), n_pad=int((types == 0).sum()), ok=start.tolist() == first))
    act = types > 0
    gates = {}

    def run(sp=None, store_h=False):
        pr = Probe(); pr.pre(mods, store_h=store_h)
        if sp is not None:
            G.install(model, sp)
            G.set_batch(input_ids=ids, attention_mask=att, labels=lab)
        pr.post(mods); pr.skip(layers); pr.upstream(layers)
        f0 = G.counters()["fwd"]
        loss, h = nll(model, text, ids, att, lab)
        fired = G.counters()["fwd"] - f0
        if sp is not None:
            G.remove()
        pr.clear()
        return pr, float(loss), h.detach(), fired

    off1, nll_off, h_off, _ = run()
    off2, _, h_off2, _ = run()
    floor = max(float((h_off - h_off2).abs().max()), max(float((off1.up[L] - off2.up[L]).abs().max()) for L in off1.up))
    res["determinism_floor_max_abs"] = floor
    del off2, h_off2
    out = {}
    for k in ("S", "N", "K0"):
        sp = spec[k]
        pr, nl, h, fired = run(sp, store_h=(k == "S"))
        V = sp["V"].float().to(DEV); kap = sp["kappa"].float().to(DEV); al = sp["alpha"].float()
        var_ratio, brute, padd, disp, Epre = [], 0.0, 0.0, [], []
        sh_t, sh_0 = [], []
        for i in range(P):
            x, y = pr.x[i], pr.y[i]
            xf, yf = x.float(), y.float()
            cx, cy = xf @ V[i], yf @ V[i]
            tg = kap[i][types]
            vr = []
            for t in (1, 2):
                m = types == t
                vx = float(cx[m].var()); vy = float(cy[m].var())
                vr.append(vy / max(vx, 1e-12))
            var_ratio.append(vr)
            ref = (xf + (al[i].item() * (tg - cx)).unsqueeze(-1) * V[i]).to(x.dtype).float()
            e = ((yf - ref).norm(dim=-1) / ref.norm(dim=-1).clamp_min(1e-6))[act]
            brute = max(brute, float(e.max()))
            if (~act).any():
                padd = max(padd, float((y[~act] != x[~act]).any()))
            d2 = ((yf - xf) ** 2).sum(-1)                                     # [B, T] squared displacement
            disp.append(float(d2[act].mean()))
            tot = float(d2[act].sum()) + 1e-30
            sh_t.append(float(d2[types == 1].sum()) / tot); sh_0.append(float(d2[:, 0].sum()) / tot)
            Epre.append(float(((cx - tg)[act] ** 2).mean()))
        var_ratio = torch.tensor(var_ratio)                                   # [P, 2]
        exp = ((1 - al) ** 2).unsqueeze(1)
        vr_err = float((var_ratio - exp).abs().max())
        up_err = max(float((pr.up[L] - off1.up[L]).abs().max()) for L in pr.up)
        o = dict(nll=nl, d_nll=nl - nll_off, fired_forwards=fired, var_ratio_max_alpha1=float(var_ratio[al == 1].max()) if (al == 1).any() else None,
                 var_ratio_err_vs_expected_max=vr_err, brute_max_rel=brute, padding_changed=bool(padd), skip_mid_err=pr.err_mid,
                 skip_out_err=pr.err_out, upstream_L0_16_max_abs=up_err, removed_band_sum=sum(disp),
                 removed_per_read=disp, E_pre_live=Epre, last_hidden_vs_off_max_abs=float((h - h_off).abs().max()),
                 removed_share_template_median=float(torch.tensor(sh_t).median()), removed_share_template_max=max(sh_t),
                 removed_share_pos0_median=float(torch.tensor(sh_0).median()), removed_share_pos0_max=max(sh_0),
                 token_share_template=float((types == 1).sum() / act.sum()))
        if k == "S":
            # rms-route residual dependence: x'(h) vs x'(h with the stream coordinate set to its per-type mean)
            us = sp["stream_dirs"].float().to(DEV); rr = []
            for i in range(P):
                hh = pr.hs[i].float(); m = mods[i]; gam = 1.0 + m.weight.float()
                cs = hh @ us[i]
                cbar = torch.zeros_like(cs)
                for t in (1, 2):
                    mt = types == t; cbar[mt] = cs[mt].mean()
                h_alt = hh - (cs - cbar).unsqueeze(-1) * us[i]
                def norm_(z):
                    return z * torch.rsqrt(z.pow(2).mean(-1, keepdim=True) + m.eps) * gam
                def clamp_(z):
                    return z + ((kap[i][types] - z @ V[i])).unsqueeze(-1) * V[i]
                xr = norm_(hh); xa = norm_(h_alt)
                num = (clamp_(xr) - clamp_(xa))[act].pow(2).sum().sqrt(); den = (clamp_(xr) - xr)[act].pow(2).sum().sqrt()
                rr.append(float(num / den.clamp_min(1e-12)))
            o["rms_route_residual_dependence"] = dict(median=float(torch.tensor(rr).median()), max=max(rr),
                                                      at={f"{Lb.READS[i][0]}{Lb.READS[i][1]}": round(rr[i], 4) for i in range(0, P, 10)})
        out[k] = o
        del pr
        torch.cuda.empty_cache()
        print(k, json.dumps({kk: vv for kk, vv in o.items() if kk not in ("removed_per_read", "E_pre_live")})[:700], flush=True)
    res["arms"] = out
    # unclamped-pass energies of S and N on the gate rows (spec's E_p with each arm's kappa)
    eu = {}
    for k in ("S", "N"):
        V = spec[k]["V"].float().to(DEV); kap = spec[k]["kappa"].float().to(DEV); al = spec[k]["alpha"].float()
        eu[k] = [float(((off1.x[i].float() @ V[i] - kap[i][types])[act] ** 2).mean()) * float(al[i]) ** 2 for i in range(P)]
    res["unclamped_gate_rows"] = dict(band_ratio_N_over_S=sum(eu["N"]) / sum(eu["S"]),
                                      per_read_ratio_quantiles=[float(x) for x in torch.quantile(torch.tensor(eu["N"]) / torch.tensor(eu["S"]), torch.tensor([0.0, 0.05, 0.5, 0.95, 1.0]))])
    live = torch.tensor(out["N"]["removed_per_read"]) / torch.tensor(out["S"]["removed_per_read"])
    res["live_energy"] = dict(band_ratio_N_over_S=out["N"]["removed_band_sum"] / out["S"]["removed_band_sum"],
                              per_read_ratio_quantiles=[float(x) for x in torch.quantile(live, torch.tensor([0.0, 0.05, 0.5, 0.95, 1.0]))],
                              S_removed_band_sum=out["S"]["removed_band_sum"], N_removed_band_sum=out["N"]["removed_band_sum"])
    del off1
    torch.cuda.empty_cache()
    # backward block on the shortest row (S), and the same ratio without the clamp
    j = 0
    n_j = int(att[j].sum())
    ids1, att1, lab1 = ids[j:j + 1, :n_j], att[j:j + 1, :n_j], lab[j:j + 1, :n_j]
    types1, _ = G.position_types(ids1, att1)
    emb = model.get_input_embeddings()
    hk = emb.register_forward_hook(lambda m, a, o: o.requires_grad_(True))
    bw = {}
    VS = spec["S"]["V"].float().to(DEV)
    for k in ("off", "S"):
        pr = Probe(); pr.retain = True; pr.pre(mods)
        if k == "S":
            G.install(model, spec["S"])
        loss, _ = nll(model, text, ids1, att1, lab1, grad=True)
        loss.backward()
        if k == "S":
            G.remove()
        rs = []
        for i in range(P):
            g = pr.x[i].grad[0][types1[0] > 0].float()
            rs.append(float((g @ VS[i]).pow(2).sum().sqrt() / g.pow(2).sum().sqrt().clamp_min(1e-30)))
        pr.clear(); del pr
        bw[k] = dict(max=max(rs), median=float(torch.tensor(rs).median()))
        torch.cuda.empty_cache()
    hk.remove()
    res["backward"] = bw
    # gates
    S, N, K0 = out["S"], out["N"], out["K0"]
    gates["fire"] = bool(all(out[k]["fired_forwards"] == 1 for k in out) and res["positions"]["ok"])
    gates["clamped"] = bool(S["var_ratio_max_alpha1"] <= 0.01 and N["var_ratio_err_vs_expected_max"] <= 0.01)
    gates["brute"] = bool(max(S["brute_max_rel"], N["brute_max_rel"]) <= 1e-3 and not S["padding_changed"] and not N["padding_changed"])
    gates["skip"] = bool(all(out[k]["skip_mid_err"] == 0 and out[k]["skip_out_err"] == 0 and out[k]["upstream_L0_16_max_abs"] <= floor for k in out))
    gates["energy"] = bool(0.9 <= res["live_energy"]["band_ratio_N_over_S"] <= 1.1)
    gates["k0"] = bool(K0["last_hidden_vs_off_max_abs"] <= floor)
    gates["backward"] = bool(bw["S"]["max"] <= 1e-3)
    res["gates"] = gates
    dS, dN = S["d_nll"], N["d_nll"]
    res["flags_spec03"] = dict(dS_within_0005=abs(dS) <= 0.005,
                               dN_within_x2_of_dS=(abs(dS) <= 0.001) or (0.5 * abs(dS) <= abs(dN) <= 2 * abs(dS)),
                               dS=dS, dN=dN, nll_off=nll_off)
    res["pass"] = bool(all(gates.values()))
    res["secs"] = round(time.time() - t0, 1)
    json.dump(res, open(f"{raw}/gate0_inf{CFG['sfx']}.json", "w"), indent=1)
    if res["pass"]:
        open(f"{raw}/GATE0_INF_PASS{CFG['sfx']}", "w").write(now() + "\n")
    print("GATE0_INF", "PASS" if res["pass"] else "FAIL", json.dumps(gates), json.dumps(res["flags_spec03"]),
          json.dumps(res["live_energy"])[:300], json.dumps(bw), flush=True)
    sys.exit(0 if res["pass"] else 3)


def log_of(p):
    return {r["step"]: r for r in map(json.loads, open(p))}


def stage_smoke(raw):
    tol = json.load(open(TRACKD_PARITY)); assert tol["verdict"] == "PASS"
    ref = log_of(f"{REF_REP if CFG['assign'] == 'B' else REF_A0}/train_log.jsonl")
    res = dict(created=now(), tolerance=dict(source=TRACKD_PARITY, mean_abs=tol["mean_abs"], max_abs=tol["max_abs"]), arms={})
    for k in (("K0", "S", "N") if CFG["assign"] == "B" else ("S",)):
        d = f"{raw}/smoke_{k}{CFG['sfx']}"
        run = log_of(f"{d}/train_log.jsonl"); meta = json.load(open(f"{d}/train_meta.json"))
        steps = range(1, 11)
        dl = [abs(run[s]["loss"] - ref[s]["loss"]) for s in steps]
        drift = jl(f"{d}/g1_drift.jsonl"); summ = json.load(open(f"{d}/g1_drift.jsonl.summary.json"))
        finite = all(all(math.isfinite(x) for x in e["E"]) for e in drift)
        o = dict(mean_abs=sum(dl) / 10, max_abs=max(dl), per_step=[round(x, 6) for x in dl],
                 signed_mean=sum(run[s]["loss"] - ref[s]["loss"] for s in steps) / 10,
                 tokens_equal=all(run[s]["tokens"] == ref[s]["tokens"] for s in steps), order_ok=bool(meta.get("hd_order_match")),
                 loss_finite=all(math.isfinite(run[s]["loss"]) for s in steps), decreasing=run[10]["loss"] < run[1]["loss"],
                 drift_lines=len(drift), drift_finite=finite, fired_min=summ["fired_min"], fired_max=summ["fired_max"],
                 recompute_min=summ["recompute_min"], g1_spec_sha256=meta.get("g1_spec_sha256"),
                 sec_per_step=round((run[10]["elapsed"] - run[1]["elapsed"]) / 9, 1), peak_gb=run[10]["peak_gb"])
        o["envelope"] = bool(o["mean_abs"] <= tol["mean_abs"] and o["max_abs"] <= tol["max_abs"] and o["tokens_equal"])
        o["plumbing"] = bool(o["order_ok"] and o["loss_finite"] and o["decreasing"] and o["drift_finite"] and o["drift_lines"] == 80
                             and o["fired_min"] == o["fired_max"] == 80 and o["recompute_min"] >= 80)
        res["arms"][k] = o
        print(k, json.dumps({kk: vv for kk, vv in o.items() if kk != "per_step"}), flush=True)
    A = res["arms"]
    if CFG["assign"] == "A":   # D213 / D105: release on plumbing; the S loss offset vs hdA0 (another trainer revision) is reported only
        inf_ok = os.path.exists(f"{raw}/GATE0_INF_PASS_A")
        ok = inf_ok and A["S"]["plumbing"] and A["S"]["tokens_equal"]
        res["verdict"] = "PASS_ON_PLUMBING" if ok else "FAIL"; res["rule"] = "A: GATE0_INF_PASS_A + S smoke plumbing + tokens equal (D105, D213)"
        json.dump(res, open(f"{raw}/gate0_smoke_A.json", "w"), indent=1)
        if ok:
            open(f"{raw}/GATE0_PASS_A", "w").write(now() + " inference gates + S_A smoke plumbing (D105 / D213)\n")
        print("GATE0_SMOKE_A", res["verdict"], flush=True)
        sys.exit(0 if ok else 3)
    inf_ok = os.path.exists(f"{raw}/GATE0_INF_PASS")
    full = inf_ok and all(A[k]["envelope"] and A[k]["plumbing"] for k in A)
    plumb = inf_ok and A["K0"]["envelope"] and all(A[k]["plumbing"] for k in A)
    res["verdict"] = "PASS" if full else ("PLUMBING_OK_SN_OUTSIDE_ENVELOPE" if plumb else "FAIL")
    json.dump(res, open(f"{raw}/gate0_smoke.json", "w"), indent=1)
    if full:
        open(f"{raw}/GATE0_PASS", "w").write(now() + "\n")
    elif plumb:
        open(f"{raw}/GATE0_PLUMBING_OK", "w").write(now() + " S/N 10-step losses outside Track D's envelope; K0 inside; orchestrator decides\n")
    print("GATE0_SMOKE", res["verdict"], flush=True)
    sys.exit(0 if full else (5 if plumb else 3))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", required=True, choices=["inf", "smoke_check"]); ap.add_argument("--raw", default=RAW)
    ap.add_argument("--assign", default="B", choices=["A", "B"])
    a = ap.parse_args()
    CFG.update(assign=a.assign, sfx="" if a.assign == "B" else "_" + a.assign, data=DATA_B if a.assign == "B" else DATA_A)
    if a.stage == "inf":
        stage_inf(a.raw)
    else:
        stage_smoke(a.raw)


if __name__ == "__main__":
    main()
