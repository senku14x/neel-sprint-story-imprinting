"""sw016 analysis (executor-9 analysis agent, 30 Oct): edit size ("dose") along each arm's own axis, from the job's pool captures.
Stories (prose, helper recipients = the induce direction that ran): per recipient, at the cut position, the coordinate gap the edit closes
  g_r1 = (M_D_cut - x_cut) . u_r1(fold k)   and   g_sd = (M_D_cut - x_cut) . u_sdir,   plus the full-state gap |M_D_cut - x_cut| (pc).
  M_D_cut = mean cut state of the whole dismissive pool of that model + rendering (gen16 target_D); fold k = contexts16 'fold'.
Chat: the class-mean gap (self-hostile - user-hostile, header mean, all 64 scripts) along unit d_self.all and along unit sdir.
Output RUN/analysis/dose16.json"""
import json, torch
torch.set_num_threads(4)
RUN = "/workspace/runs_executor/sw016"; DIRS = "/workspace/runs_executor/overnight_2026-10-30/dirs"
unit = lambda x: x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)
ctx = {}
for l in open(f"{RUN}/inputs/contexts16.jsonl"):
    c = json.loads(l); ctx[c["key"]] = dict(recipient=c.get("recipient"), fold=c.get("fold"), cls=c.get("cls"))
out = {}
LS = (16, 24, 32, 40, 48, 56, 63)
for m in ("hdA0", "hdB0"):
    P = torch.load(f"{RUN}/pool_{m}.pt", weights_only=False)["prose"]
    S = torch.load(f"{RUN}/sdir_{m}.pt", weights_only=False); usd = unit(S["u"].float())
    D = torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False)
    U1 = unit(D["d_self"]["loso"].float())  # [5,64,H]
    cut = P["cut"].float(); cls = P["cls"]; keys = P["keys"]
    MD = cut[[i for i, c in enumerate(cls) if c == "dismissive"]].mean(0)
    rec = [i for i, (k, c) in enumerate(zip(keys, cls)) if c == "helper" and ctx[k]["recipient"]]
    g1, gs, gf = [], [], []
    for i in rec:
        k = ctx[keys[i]]["fold"]; dlt = MD - cut[i]
        g1.append((dlt * U1[k]).sum(-1)); gs.append((dlt * usd).sum(-1)); gf.append(dlt.norm(dim=-1))
    g1, gs, gf = torch.stack(g1), torch.stack(gs), torch.stack(gf)
    med = lambda t: [round(float(t[:, L].median()), 3) for L in LS]
    R = dict(n_recipients=len(rec), layers=LS, story_abs_gap_r1_median=med(g1.abs()), story_abs_gap_sdir_median=med(gs.abs()),
             story_fullstate_gap_median=med(gf), ratio_sdir_over_r1_median=[round(float((gs.abs()[:, L] / g1.abs()[:, L].clamp_min(1e-6)).median()), 3) for L in LS],
             sum_sq_over_L16_63=dict(r1=round(float((g1[:, 16:] ** 2).sum(1).sqrt().median()), 2), sdir=round(float((gs[:, 16:] ** 2).sum(1).sqrt().median()), 2),
                                     full=round(float((gf[:, 16:] ** 2).sum(1).sqrt().median()), 2)))
    cm = D["class_means"]["hdr_mean"]; dchat = cm["self-hostile"]["all"].float() - cm["user-hostile"]["all"].float()
    ds = unit(D["d_self"]["all"].float())
    R["chat_classmean_gap_along_dself"] = [round(float((dchat[L] * ds[L]).sum()), 3) for L in LS]
    R["chat_classmean_gap_along_sdir"] = [round(float((dchat[L] * usd[L]).sum()), 3) for L in LS]
    R["chat_classmean_gap_norm"] = [round(float(dchat[L].norm()), 3) for L in LS]
    out[m] = R
    print(m, json.dumps(R))
json.dump(out, open(f"{RUN}/analysis/dose16.json", "w"), indent=1)
