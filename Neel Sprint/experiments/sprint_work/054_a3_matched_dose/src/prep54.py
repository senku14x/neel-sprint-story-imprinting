"""sw054 CPU prep (E1 sw054 prep agent, 30 Oct 2026): per-layer doses for the rescaled arms and the A-control directions.
Nothing here reads a model output; inputs are sw016's pool captures / story direction and sw009's chat captures.

Doses (sw016 dose16_an.py's definitions, recomputed at all 64 layers; KAT: equal to dose16.json at its 7 layers):
  g_story[L] = median over the 64 prose helper recipients of |(M_D_cut - x_cut) . u_sdir[L]|  (sdir's median coordinate gap
               at the cut; M_D_cut = mean cut state of the model's whole prose dismissive pool; x_cut = the recipient's cut state)
               -> r1x moves the chat d_self coordinate by g_story[L] (r1 rescaled to sdir's size)
  g_story_earlier[L] = the same median at the speaker's EARLIER line starts (dose16 measured the cut only): median over the
               helper recipients with >= 1 earlier line of |(M_D_turn - earlier_mean_i) . u_sdir[L]|, M_D_turn = sw016's
               earlier-line-start target (D54-2; validated against sw016's per-position activations at 14 layers, D54-3)
               -> r1x's dose is g_story at the cut and g_story_earlier at the earlier line starts
  g_chat[L]  = (mean_self-hostile - mean_user-hostile) . unit(d_self.all)[L], header mean over all 64 sw008 scripts
               (d_self's chat class gap, dose16 'chat_classmean_gap_along_dself')
  g_chat_tok[t, L] = |per-token class gap along unit(d_self.all)| at header token t (class_means.hdr_tok); its mean over the 7
               tokens equals g_chat (KAT) -> rstory_x moves the story-direction coordinate at token t by g_chat_tok[t, L]
               (rstory rescaled to C4's size token by token; D54-4)
A-control directions (sw028 dirs28_x.py's cov construction: one Gaussian combination of within-class-centred states, the same
coefficients at every layer, unit per layer, then orthogonalised per layer to the tested direction; fresh generators):
  A_story[k, i] (k = chat fold 0-4, i = 0-2): story-shaped (the model's NON-recipient prose pool cut states, centred within
               class), orthogonalised to u_k = unit(d_self.loso[k]) (r1x's direction for recipients of fold k). seed 5400 + mi
  A_chat[k, i]: chat-shaped (fold k's fit set = scripts outside scenario k, self-hostile / user-hostile header-mean states,
               centred within condition), orthogonalised to u_sdir. seed 5410 + 10 k + mi
Descriptives (no gate): per-token and header-mean paired chat gaps along d_self.loso[k] and u_sdir; story gaps at the earlier
line starts (earlier_mean vs M_D_turn).
Output: RUN/prep54_<m>.pt, RUN/prep54.json, RUN/PREP_OK
  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 /root/venvs/si/bin/python prep54.py [--run_dir /workspace/runs_executor/sw054]"""
import argparse, json, os, time

import torch

torch.set_num_threads(8)
SW16 = "/workspace/runs_executor/sw016"
DIRS = "/workspace/runs_executor/overnight_2026-10-30/dirs"
CAP = "/workspace/runs_executor/sw009_captures"
MODELS = ("hdA0", "hdB0")
L0 = 16
LS16 = (16, 24, 32, 40, 48, 56, 63)


def unit(x):
    return x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)


def orth(v, u):
    return unit(v - (v * u).sum(-1, keepdim=True) * u)


def story_doses(m, ctx):
    P = torch.load(f"{SW16}/pool_{m}.pt", weights_only=False)["prose"]
    S = torch.load(f"{SW16}/sdir_{m}.pt", weights_only=False); usd = unit(S["u"].float())
    D = torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False); U1 = unit(D["d_self"]["loso"].float())
    cut = P["cut"].float(); em = P["earlier_mean"].float(); cls = P["cls"]; keys = P["keys"]; ne = P["n_earlier"]
    dis = [i for i, c in enumerate(cls) if c == "dismissive"]
    MD = cut[dis].mean(0)
    MDt = em[[i for i in dis if ne[i] > 0]].mean(0)
    rec = [i for i, (k, c) in enumerate(zip(keys, cls)) if c == "helper" and ctx[k]["recipient"]]
    g1, gs, g1t, gst = [], [], [], []
    for i in rec:
        k = ctx[keys[i]]["fold"]; dlt = MD - cut[i]
        g1.append((dlt * U1[k]).sum(-1)); gs.append((dlt * usd).sum(-1))
        if ne[i] > 0:
            dt = MDt - em[i]; g1t.append((dt * U1[k]).sum(-1)); gst.append((dt * usd).sum(-1))
    g1, gs, g1t, gst = (torch.stack(x) for x in (g1, gs, g1t, gst))
    g_story = gs.abs().median(0).values; g_story[:L0] = 0.0
    g_story_earlier = gst.abs().median(0).values; g_story_earlier[:L0] = 0.0
    # A_story: non-recipient prose pool, within-class centred
    nr = [i for i, k in enumerate(keys) if not ctx[k]["recipient"]]
    Xh = cut[[i for i in nr if cls[i] == "helper"]]; Xd = cut[[i for i in nr if cls[i] == "dismissive"]]
    Wc = torch.cat([Xh - Xh.mean(0), Xd - Xd.mean(0)])
    g = torch.Generator().manual_seed(5400 + MODELS.index(m))
    Araw = torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(Wc), generator=g), Wc)) for _ in range(3)])  # [3, 64, H]
    A = torch.stack([orth(Araw, U1[k][None]) for k in range(5)])  # [5, 3, 64, H]
    desc = dict(n_recipients=len(rec), n_nonrec_helper=len(Xh), n_nonrec_dismissive=len(Xd),
                cut_abs_gap_r1_median=[float(g1.abs()[:, L].median()) for L in range(64)],
                cut_abs_gap_sdir_median=[float(gs.abs()[:, L].median()) for L in range(64)],
                earlier_abs_gap_r1_median=[float(g1t.abs()[:, L].median()) for L in range(64)],
                earlier_abs_gap_sdir_median=[float(gst.abs()[:, L].median()) for L in range(64)],
                n_with_earlier=len(g1t),
                raw_abs_cos_A_vs_u_max=[float((Araw * U1[k][None]).sum(-1)[:, L0:].abs().max()) for k in range(5)],
                abs_cos_A_vs_sdir_max=float((A * usd).sum(-1)[..., L0:].abs().max()),
                abs_cos_A_after_orth_max=float(max((A[k] * U1[k][None]).sum(-1)[:, L0:].abs().max() for k in range(5))))
    return g_story, g_story_earlier, A, desc, usd, D


def chat_doses(m, usd, D):
    cm = D["class_means"]["hdr_mean"]; dchat = cm["self-hostile"]["all"].float() - cm["user-hostile"]["all"].float()
    ds = unit(D["d_self"]["all"].float())
    g_chat = (dchat * ds).sum(-1); g_chat[:L0] = 0.0
    ct = D["class_means"]["hdr_tok"]; dtok = ct["self-hostile"]["all"].float() - ct["user-hostile"]["all"].float()  # [7, 64, H]
    g_tok_signed = (dtok * ds[None]).sum(-1)  # [7, 64]
    g_chat_tok = g_tok_signed.abs(); g_chat_tok[:, :L0] = 0.0
    U1 = unit(D["d_self"]["loso"].float()); sid2fold = D["meta"]["sid2fold"]; scen = D["meta"]["scenarios"]
    C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
    sids = sorted({k.split("|")[2] for k in C["keys"] if k.startswith("sw008|self-hostile|")})
    assert len(sids) == 64, len(sids)
    gu_t, gs_t, gu_m, gs_m = [], [], [], []
    for s in sids:
        k = sid2fold[s]
        Hs = C["hdr"][idx[f"sw008|self-hostile|{s}"]].float(); Hu = C["hdr"][idx[f"sw008|user-hostile|{s}"]].float()  # [7, 64, H]
        for x, dn in ((Hs, Hu), (Hu, Hs)):  # fwd (self recipient, user donor), rev
            dl = dn - x
            gu_t.append((dl * U1[k][None]).sum(-1)); gs_t.append((dl * usd[None]).sum(-1))  # [7, 64]
            gu_m.append((dl.mean(0) * U1[k]).sum(-1)); gs_m.append((dl.mean(0) * usd).sum(-1))
    gu_t, gs_t, gu_m, gs_m = (torch.stack(v).abs() for v in (gu_t, gs_t, gu_m, gs_m))
    # A_chat: per fold, the fit set's (scripts outside scenario k) header-mean states, centred within condition
    Ms = C["hdr_mean"][[idx[f"sw008|self-hostile|{s}"] for s in sids]].float(); Mu = C["hdr_mean"][[idx[f"sw008|user-hostile|{s}"] for s in sids]].float()
    A = []
    for k in range(5):
        fi = [j for j, s in enumerate(sids) if sid2fold[s] != k]
        wc = torch.cat([Ms[fi] - Ms[fi].mean(0), Mu[fi] - Mu[fi].mean(0)])
        g = torch.Generator().manual_seed(5410 + 10 * k + MODELS.index(m))
        Araw = torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(3)])
        A.append(orth(Araw, usd[None]))
    A = torch.stack(A)
    desc = dict(scenarios=scen, n_scripts=len(sids),
                paired_tok1_6_abs_gap_dself_loso_median=[float(gu_t[:, 1:, L].median()) for L in range(64)],
                paired_tok1_6_abs_gap_sdir_median=[float(gs_t[:, 1:, L].median()) for L in range(64)],
                paired_hdrmean_abs_gap_dself_loso_median=[float(gu_m[:, L].median()) for L in range(64)],
                paired_hdrmean_abs_gap_sdir_median=[float(gs_m[:, L].median()) for L in range(64)],
                classmean_gap_along_sdir=[float(x) for x in (dchat * usd).sum(-1)],
                abs_cos_A_after_orth_max=float((A * usd).sum(-1)[..., L0:].abs().max()),
                abs_cos_A_vs_dself_all_max=float((A * ds).sum(-1)[..., L0:].abs().max()),
                g_chat_tok=[[float(x) for x in g_chat_tok[:, L]] for L in range(64)],
                n_negative_token_gaps_L16_63=int((g_tok_signed[:, L0:] < 0).sum()),
                tokmean_signed_minus_g_chat_maxabs=float((g_tok_signed.mean(0) - (dchat * ds).sum(-1))[L0:].abs().max()))
    return g_chat, g_chat_tok, A, desc


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw054"); a = ap.parse_args()
    os.makedirs(a.run_dir, exist_ok=True)
    ctx = {}
    for l in open(f"{SW16}/inputs/contexts16.jsonl"):
        c = json.loads(l); ctx[c["key"]] = dict(recipient=c["recipient"], fold=c.get("fold"))
    d16 = json.load(open(f"{SW16}/analysis/dose16.json"))
    out = dict(created=time.strftime("%FT%TZ", time.gmtime()), kat={}, models={})
    for m in MODELS:
        t0 = time.time()
        g_story, g_story_earlier, A_story, ds_, usd, D = story_doses(m, ctx)
        g_chat, g_chat_tok, A_chat, dc_ = chat_doses(m, usd, D)
        # KAT: dose16.json at its 7 layers (rounded to 3 decimals there)
        ks = max(abs(float(g_story[L]) - v) for L, v in zip(LS16, d16[m]["story_abs_gap_sdir_median"]))
        kr = max(abs(ds_["cut_abs_gap_r1_median"][L] - v) for L, v in zip(LS16, d16[m]["story_abs_gap_r1_median"]))
        kc = max(abs(float(g_chat[L]) - v) for L, v in zip(LS16, d16[m]["chat_classmean_gap_along_dself"]))
        kcs = max(abs(dc_["classmean_gap_along_sdir"][L] - v) for L, v in zip(LS16, d16[m]["chat_classmean_gap_along_sdir"]))
        kat = dict(story_sdir_maxabs=ks, story_r1_maxabs=kr, chat_dself_maxabs=kc, chat_sdir_maxabs=kcs)
        kat["pass"] = bool(max(kat.values()) <= 1e-3 + 1e-9)  # dose16.json stores 3 decimals
        # per-token chat dose: its signed token mean is dose16's g_chat (linearity); fp32 summation error only
        kat["tokmean_vs_g_chat_maxabs"] = dc_["tokmean_signed_minus_g_chat_maxabs"]
        kat["pass"] = bool(kat["pass"] and kat["tokmean_vs_g_chat_maxabs"] <= 1e-4 * float(g_chat[L0:].abs().max()))
        out["kat"][m] = kat
        assert kat["pass"], (m, kat)
        assert float(g_story[L0:].min()) > 0 and float(g_story_earlier[L0:].min()) > 0 and float(g_chat[L0:].min()) > 0, "a dose is <= 0"
        torch.save(dict(g_story=g_story, g_story_earlier=g_story_earlier, g_chat=g_chat, g_chat_tok=g_chat_tok,
                        A_story=A_story.half(), A_chat=A_chat.half(), u_sdir=usd,
                        meta=dict(seeds=dict(A_story=5400 + MODELS.index(m), A_chat=[5410 + 10 * k + MODELS.index(m) for k in range(5)]))),
                   f"{a.run_dir}/prep54_{m}.pt")
        r1x_over_r1 = [float(g_story[L]) / max(ds_["cut_abs_gap_r1_median"][L], 1e-9) for L in range(64)]
        rsx_over_rs = [float(g_chat[L]) / max(abs(dc_["classmean_gap_along_sdir"][L]), 1e-9) for L in range(64)]
        out["models"][m] = dict(g_story=[float(x) for x in g_story], g_story_earlier=[float(x) for x in g_story_earlier],
                                g_chat=[float(x) for x in g_chat], story=ds_, chat=dc_,
                                r1x_dose_over_r1_median_cut=r1x_over_r1, rstory_x_dose_over_rstory_classgap=rsx_over_rs,
                                l2_L16_63=dict(g_story=float(g_story[L0:].norm()), g_chat=float(g_chat[L0:].norm())))
        f2 = lambda v: [round(v[L], 2) for L in LS16]
        print(m, f"{time.time() - t0:.0f}s KAT", kat)
        print("  g_story (sdir cut median)", f2([float(x) for x in g_story]), "| r1 cut median", f2(ds_["cut_abs_gap_r1_median"]),
              "| r1x/r1", f2(r1x_over_r1))
        print("  story earlier: sdir", f2(ds_["earlier_abs_gap_sdir_median"]), "r1", f2(ds_["earlier_abs_gap_r1_median"]))
        print("  g_story_earlier", f2([float(x) for x in g_story_earlier]), "| chat neg token gaps", dc_["n_negative_token_gaps_L16_63"])
        print("  g_chat (d_self class gap)", f2([float(x) for x in g_chat]), "| sdir class gap", f2([abs(x) for x in dc_["classmean_gap_along_sdir"]]),
              "| rstory_x/rstory", f2(rsx_over_rs))
        print("  chat paired tok1-6 median: d_self", f2(dc_["paired_tok1_6_abs_gap_dself_loso_median"]), "sdir", f2(dc_["paired_tok1_6_abs_gap_sdir_median"]))
        print("  chat paired hdr-mean median: d_self", f2(dc_["paired_hdrmean_abs_gap_dself_loso_median"]), "sdir", f2(dc_["paired_hdrmean_abs_gap_sdir_median"]))
        print("  A checks: story", {k: ds_[k] for k in ("abs_cos_A_after_orth_max", "abs_cos_A_vs_sdir_max")}, "chat",
              {k: dc_[k] for k in ("abs_cos_A_after_orth_max", "abs_cos_A_vs_dself_all_max")}, flush=True)
    json.dump(out, open(f"{a.run_dir}/prep54.json", "w"), indent=1)
    open(f"{a.run_dir}/PREP_OK", "w").write(out["created"] + "\n")
    print("PREP54_DONE")


if __name__ == "__main__":
    main()
