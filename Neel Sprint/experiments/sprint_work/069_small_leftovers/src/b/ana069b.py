"""sw069 (b) analysis (E1 analysis agent; rule frozen in ../../design_spec.md part (b)). CPU; /root/venvs/si/bin/python.
  tail : the tail of sw018's d_self scores. Per model (parent, hdB0, ctrlB0) the all-64 chat d_self (self-hostile - user-hostile
         sw008 header means, sw018's fit) projected on sw018's HF E4 set-2 story states at L16/24/32/40/48; score = mean over the
         5 layers of the per-layer z-scored projection; the 10 highest and 10 lowest story rows, decoded around set 2
         -> RUN/tail_<m>.txt, RUN/tail.json
  main : story-character direction u_m = unit(mean dismissive - mean helper) of model m's states at sw016's corrected cut
         (hdB0: sw016 pool_hdB0.pt; ctrlB0 / parent: RUN/pool_cut_<m>.pt from cap069b.py), prose + dialogue pooled, per layer;
         project m's own sw008 chat header means (self-hostile = positive class, user-hostile = negative); AUROC per layer at
         L16/24/32/40/48 and their mean; null = >= 500 refits of u with story-level label shuffles (class sizes kept), each
         projected the same way; null95 per layer = 95th pct of max(A, 1 - A) (sw018's convention); margin = mean over the 5
         layers of (AUROC - null95); beside it the null of the 5-layer-mean AUROC itself. Rule (frozen): SHARED if mean AUROC
         >= 0.70 and margin > 0.05 in both hdB0 and ctrlB0; NOT SHARED if mean AUROC <= 0.60 in both; else PARTIAL. The parent
         is a descriptive reference (not in the rule). Script-bootstrap CI (64 scripts, paired) on the mean AUROC.
         -> RUN/results069b.json, RUN/report069b.txt, RUN/ANALYZED (only when every rule model is present)
  OMP_NUM_THREADS=8 python ana069b.py tail | main [--models hdB0,ctrlB0,parent] [--R 1000]"""
import argparse, glob, json, os, sys, time

import numpy as np
import torch

torch.set_num_threads(8)
RUN = "/workspace/runs_executor/sw069b"
SW16 = "/workspace/runs_executor/sw016"
SW18 = "/workspace/runs_executor/sw018"
CAP9 = "/workspace/runs_executor/sw009_captures"
L5 = [16, 24, 32, 40, 48]
RULE_MODELS = ("hdB0", "ctrlB0")


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def auroc(pos, neg):  # tie-averaged Mann-Whitney
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort"); r = np.empty(len(allv)); r[order] = np.arange(1, len(allv) + 1)
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=r); r = sums[inv] / cnt[inv]
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def chat_states(m):
    """sw018 chat_states(): sw008 header means, 4 conditions x 64 scripts (keys sorted), layers L5 -> {cond: (X [64, 5, H], sids)}"""
    C = torch.load(f"{SW18}/captures/ctrlB0_chat.pt" if m == "ctrlB0" else f"{CAP9}/{m}.pt", mmap=True)
    idx = {k: i for i, k in enumerate(C["keys"])}
    out = {}
    for cond in ("self-hostile", "user-hostile"):
        ks = sorted(k for k in idx if k.startswith(f"sw008|{cond}|"))
        out[cond] = (C["hdr_mean"][[idx[k] for k in ks]][:, L5].float(), [k.split("|")[2] for k in ks])
    del C
    assert out["self-hostile"][1] == out["user-hostile"][1] and len(out["self-hostile"][1]) == 64
    return out


def story_cut(m):
    """states at sw016's corrected cut for hdB0's story mapping -> keys, cls, rend, X [n, 5, H]"""
    if m == "hdB0":
        z = torch.load(f"{SW16}/pool_hdB0.pt", weights_only=False)
        keys, cls, rend, X = [], [], [], []
        for rd in ("prose", "dialogue"):
            v = z[rd]; keys += v["keys"]; cls += v["cls"]; rend += [rd] * len(v["keys"]); X.append(v["cut"][:, L5].float())
        return keys, cls, rend, torch.cat(X)
    z = torch.load(f"{RUN}/pool_cut_{m}.pt", weights_only=False)
    return z["keys"], z["cls"], z["rend"], z["cut"][:, L5].float()


def stage_main(a):
    t0 = time.time()
    models = a.models.split(",")
    ctx = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW16}/inputs/contexts16.jsonl")}
    res = dict(L5=L5, R=a.R, models={}, rule_models=list(RULE_MODELS))
    ref_keys = None
    for m in models:
        if m != "hdB0" and not os.path.exists(f"{RUN}/pool_cut_{m}.pt"):
            print(f"[skip] {m}: no capture yet", flush=True); continue
        keys, cls, rend, X = story_cut(m)
        # align every model to the same key order (sorted) and check the class labels against sw016's contexts
        o = sorted(range(len(keys)), key=lambda i: keys[i]); keys = [keys[i] for i in o]; cls = [cls[i] for i in o]
        rend = [rend[i] for i in o]; X = X[o]
        assert all(ctx[k]["cls"] == c and ctx[k]["model"] == "hdB0" for k, c in zip(keys, cls))
        if ref_keys is None:
            ref_keys = keys
        assert keys == ref_keys, m
        assert torch.isfinite(X).all()
        lab = np.array([c == "dismissive" for c in cls])
        story = np.array([f"{ctx[k]['spec']}|{ctx[k]['idx']}" for k in keys])  # a story = (spec file, idx)
        ch = chat_states(m); S, sids = ch["self-hostile"]; U, _ = ch["user-hostile"]
        Y = torch.cat([S, U])  # [128, 5, H]; first 64 positive
        # observed direction
        u = unit(X[lab].mean(0) - X[~lab].mean(0))  # [5, H]
        pr = torch.einsum("nlh,lh->nl", Y, u).numpy()
        A = np.array([auroc(pr[:64, j], pr[64:, j]) for j in range(5)])

        def dprime(p):  # descriptive (D-b4): oriented standardized separation self-hostile vs user-hostile, per layer
            a, b = p[:64], p[64:]
            return (a.mean(0) - b.mean(0)) / np.sqrt((a.var(0) + b.var(0)) / 2)
        Dobs = dprime(pr)
        # story-side sanity: 5-fold by story id cross-fitted AUROC dismissive vs helper on the stories themselves
        us = sorted(set(story)); fold = {s: i % 5 for i, s in enumerate(np.random.default_rng(69).permutation(us))}
        fs = np.array([fold[s] for s in story]); sp = np.zeros((len(keys), 5))
        for k in range(5):
            tr = fs != k; uk = unit(X[tr & lab].mean(0) - X[tr & ~lab].mean(0))
            sp[fs == k] = torch.einsum("nlh,lh->nl", X[fs == k], uk).numpy()
        A_story = [auroc(sp[lab, j], sp[~lab, j]) for j in range(5)]
        # label-shuffle null: permute class labels across story ids (renderings of one story share a label), keep class counts
        st_lab = {s: bool(lab[story == s][0]) for s in us}
        assert all(len(set(lab[story == s])) == 1 for s in us)
        n_d = sum(st_lab.values()); g = np.random.default_rng(6902)
        Xf = X.reshape(len(keys), -1)
        nullA = np.zeros((a.R, 5)); nullD = np.zeros((a.R, 5))
        for r in range(a.R):
            perm = g.permutation(len(us)); dset = {us[i] for i in perm[:n_d]}
            lb = np.array([s in dset for s in story])
            w = np.where(lb, 1.0 / lb.sum(), -1.0 / (~lb).sum())
            d = (torch.from_numpy(w).float() @ Xf).reshape(5, -1); un = unit(d)
            p = torch.einsum("nlh,lh->nl", Y, un).numpy()
            nullA[r] = [auroc(p[:64, j], p[64:, j]) for j in range(5)]; nullD[r] = dprime(p)
        n2 = np.maximum(nullA, 1 - nullA); null95 = np.quantile(n2, 0.95, axis=0)
        mean_null = nullA.mean(1); null95_mean = float(np.quantile(np.maximum(mean_null, 1 - mean_null), 0.95))
        # script bootstrap (paired self / user versions of a script move together)
        gb = np.random.default_rng(6903); Bm = []
        for _ in range(2000):
            ii = gb.integers(0, 64, 64)
            Bm.append(np.mean([auroc(pr[ii, j], pr[64 + ii, j]) for j in range(5)]))
        # cos with the model's own all-64 chat d_self
        dself = unit(S.mean(0) - U.mean(0))
        e = dict(n_story=dict(dismissive=int(lab.sum()), helper=int((~lab).sum()), stories=len(us),
                              prose=int(sum(x == "prose" for x in rend)), dialogue=int(sum(x == "dialogue" for x in rend))),
                 auroc=A.tolist(), mean_auroc=float(A.mean()), mean_auroc_ci=[float(np.quantile(Bm, 0.025)), float(np.quantile(Bm, 0.975))],
                 null95=null95.tolist(), margin=(A - null95).tolist(), mean_margin=float((A - null95).mean()),
                 null_mean_auroc_95=null95_mean, margin_of_mean=float(A.mean() - null95_mean),
                 null_oriented_mean=float(mean_null.mean()), null_oriented_sd=float(mean_null.std()),
                 frac_null_mean_ge_obs=float((mean_null >= A.mean()).mean()),
                 story_side_auroc_5fold=A_story,
                 dprime=Dobs.tolist(), dprime_mean=float(Dobs.mean()), null_dprime_mean_q=[float(np.quantile(nullD.mean(1), q)) for q in (0.05, 0.5, 0.95)],
                 null_absdprime_mean_q95=float(np.quantile(np.abs(nullD).mean(1), 0.95)),
                 pct_dprime_vs_oriented_null=float((nullD.mean(1) < Dobs.mean()).mean()),
                 pct_dprime_vs_abs_null=float((np.abs(nullD).mean(1) < abs(Dobs.mean())).mean()), cos_u_vs_chat_dself=[float(x) for x in (u * dself).sum(-1)])
        res["models"][m] = e
        print(f"{m}: AUROC L5 {np.round(A, 3)} mean {A.mean():.3f} CI {np.round(e['mean_auroc_ci'], 3)}  null95 {np.round(null95, 3)}  "
              f"margin {e['mean_margin']:+.3f} (of-mean {e['margin_of_mean']:+.3f})  story-side {np.round(A_story, 3)}  "
              f"d' {e['dprime_mean']:+.2f} (null |d'| q95 {e['null_absdprime_mean_q95']:.2f}, pct vs |null| {e['pct_dprime_vs_abs_null']:.3f})  "
              f"cos(u, d_self) {np.round(e['cos_u_vs_chat_dself'], 2)}  {time.time() - t0:.0f}s", flush=True)
    have = [m for m in RULE_MODELS if m in res["models"]]
    if len(have) == len(RULE_MODELS):
        M = res["models"]
        shared = all(M[m]["mean_auroc"] >= 0.70 and M[m]["mean_margin"] > 0.05 for m in RULE_MODELS)
        not_shared = all(M[m]["mean_auroc"] <= 0.60 for m in RULE_MODELS)
        res["verdict"] = "SHARED" if shared else "NOT SHARED" if not_shared else "PARTIAL"
        res["per_model_criteria"] = {m: dict(auroc_ge_070=M[m]["mean_auroc"] >= 0.70, margin_gt_005=M[m]["mean_margin"] > 0.05,
                                             auroc_le_060=M[m]["mean_auroc"] <= 0.60) for m in RULE_MODELS}
    else:
        res["verdict"] = f"PENDING (missing {[m for m in RULE_MODELS if m not in have]})"
    out = a.out or f"{RUN}/results069b.json"
    json.dump(res, open(out, "w"), indent=1)
    print("VERDICT", res["verdict"], flush=True)
    if len(have) == len(RULE_MODELS) and not a.out:
        open(f"{RUN}/ANALYZED", "w").write(res["verdict"] + "\n")


def stage_tail(a):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(f"{SW18}/inputs/stories.jsonl")}
    flags = json.load(open(f"{SW18}/inputs/set2_prefix_flags.json"))
    summ = {}
    for m in a.models.split(","):
        keys, X = [], []
        for cf in sorted(glob.glob(f"{SW18}/captures/stories/{m}/chunk_*.pt")):
            z = torch.load(cf, mmap=True); sel = [i for i in range(len(z["keys"])) if int(z["set_counts"][i][2]) > 0]
            X.append(z["set_mean"][sel][:, 2][:, L5].float().clone()); keys += [z["keys"][i] for i in sel]
        X = torch.cat(X)
        ch = chat_states(m); S, _ = ch["self-hostile"]; U, _ = ch["user-hostile"]
        d = unit(S.mean(0) - U.mean(0))
        p = torch.einsum("nlh,lh->nl", X, d).numpy(); zsc = ((p - p.mean(0)) / p.std(0)).mean(1)
        lab = np.array([meta[k]["cls"] for k in keys])
        o = np.argsort(-zsc)
        top, bot = o[:10], o[::-1][:10]
        txt = []
        for side, ix in (("HIGH (most self-hostile-like = 'dismissive' side)", top), ("LOW (most user-hostile-like = 'helper' side)", bot)):
            txt.append(f"########## {m} {side}")
            for rank, i in enumerate(ix):
                r = meta[keys[i]]; ids = r["ids"]; pos = r["sets"][2][0]
                pre = tok.decode(ids[:pos]); post = tok.decode(ids[pos:pos + 50])
                txt.append(f"[{side[:4]}{rank}] score {zsc[i]:+.2f} cls={r['cls']} rend={r['rend']} spec={r['spec']} seen_by={r['seen_by']} "
                           f"prefix_flag={flags[keys[i]]}\n--PRE (last 900 chars)--\n{pre[-900:]}\n--AT/POST--\n{post}\n")
        open(f"{RUN}/tail_{m}.txt", "w").write("\n".join(txt))
        # composition of the tails (descriptive)
        comp = {}
        for n in (10, 50, 100):
            comp[n] = dict(top_dismissive=int((lab[o[:n]] == "dismissive").sum()), bottom_helper=int((lab[o[::-1][:n]] == "helper").sum()),
                           top_prose=int(sum(meta[keys[i]]["rend"] == "prose" for i in o[:n])),
                           bottom_prose=int(sum(meta[keys[i]]["rend"] == "prose" for i in o[::-1][:n])),
                           top_habit_prefix=int(sum(flags[keys[i]]["lexicon"] != "none" for i in o[:n])),
                           bottom_habit_prefix=int(sum(flags[keys[i]]["lexicon"] != "none" for i in o[::-1][:n])))
        summ[m] = dict(n=len(keys), n_dismissive=int((lab == "dismissive").sum()), comp=comp,
                       top10=[keys[i] for i in top], bottom10=[keys[i] for i in bot],
                       prose_share=float(np.mean([meta[k]["rend"] == "prose" for k in keys])),
                       habit_prefix_share=float(np.mean([flags[k]["lexicon"] != "none" for k in keys])))
        print(m, json.dumps(summ[m]["comp"]), flush=True)
    json.dump(summ, open(f"{RUN}/tail.json", "w"), indent=1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stage", choices=["tail", "main"])
    ap.add_argument("--models", default=None); ap.add_argument("--R", type=int, default=1000); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    os.makedirs(RUN, exist_ok=True)
    if a.models is None:
        a.models = "ctrlB0,parent,hdB0" if a.stage == "tail" else "hdB0,ctrlB0,parent"
    assert a.R >= 500 or a.out, "the rule needs >= 500 refits"
    (stage_tail if a.stage == "tail" else stage_main)(a)


if __name__ == "__main__":
    main()
