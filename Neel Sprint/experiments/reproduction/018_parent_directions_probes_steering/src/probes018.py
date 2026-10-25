"""018 linear probes (spec §8.1; executor-4, 25 Oct 2026). CPU only.
Logistic regression (L2; C by 5-fold CV on train only, scoring AUROC; features standardised on train) at each saved
layer, for two feature sets: with-prompt (response mean under the persona's own system prompt) and text-only (the
same reply re-encoded with no system prompt). Tasks:
  story_X (6): kept rollouts of X (or eval_dismissive) vs default rollouts
  axis       : fully-role-playing rollouts vs default rollouts. Positives are a seeded subsample (random.Random(18)) of
               the fully rollouts that also have a text-only re-encode (role_textonly_ids), sized to the default count
               per split, so both feature sets use the same rollouts (decisions D16)
  trait_T (7): pos kept vs neg kept
Splits: train = extraction questions + train prompts; test1 = held-out questions + train prompts; test2 (story only) =
held-out questions + held-out paraphrases P6-P7 (vs held-out default).
Per layer and test set: AUROC, accuracy, shuffled-label null (100 permutations of the TRAIN labels, refit at the chosen
C, AUROC on the true test labels; mean / 95th percentile / max), the direction-alone AUROC (projection on the unit
direction from directions_parent.pt; for the axis task the sign is flipped so it points toward the positive class,
roles), and cos(probe weight in raw space, direction).
Every (task, feature set, layer) is one job; jobs run in parallel, one BLAS thread each (D16). Features are shared with
the workers through float32 .npy memmaps in /dev/shm (deleted at the end).
Saves fitted text-only probes (scaler + weights) for the §8.2 readout: RUN/probes_textonly.pt.
  /root/venvs/si/bin/python probes018.py [--jobs 14]"""
import argparse, json, os, random, sys, time
from collections import defaultdict

import numpy as np
import torch
from joblib import Parallel, delayed, parallel_config
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common018 as C  # noqa: E402

torch.set_num_threads(8)
LS = C.LAYERS_SAVE
CS = np.logspace(-4, 2, 7)


def load_feats(ctx, keys):
    """(list of keys, fp32 [n, len(LS), H]) response means at LS for the requested keys."""
    d = f"{C.RUN}/acts_parent/{ctx}"; ks, xs = [], []
    for fn in sorted(f for f in os.listdir(d) if f.startswith("chunk_")):
        z = torch.load(f"{d}/{fn}", mmap=True)  # mmap: 14x faster than a full read on this box (decisions D15)
        idx = [i for i, k in enumerate(z["keys"]) if k in keys]
        if idx:
            xs.append(z["resp"][idx][:, LS].float().numpy()); ks += [z["keys"][i] for i in idx]
    return ks, (np.concatenate(xs) if xs else np.zeros((0, len(LS), C.HIDDEN), np.float32))


def fit_eval(Xtr, ytr, tests, u, seed):
    sc = StandardScaler().fit(Xtr)
    cv = LogisticRegressionCV(Cs=CS, cv=5, penalty="l2", scoring="roc_auc", max_iter=3000, n_jobs=1).fit(sc.transform(Xtr), ytr)
    Cb = float(cv.C_[0]); w = cv.coef_[0] / sc.scale_
    res = dict(C=Cb, cos_probe_direction=float(w @ u / (np.linalg.norm(w) * np.linalg.norm(u))))
    rng = np.random.default_rng(seed)
    nulls = []
    for _ in range(100):
        m = LogisticRegression(C=Cb, penalty="l2", max_iter=3000).fit(sc.transform(Xtr), rng.permutation(ytr))
        nulls.append({t: roc_auc_score(yte, m.decision_function(sc.transform(Xte))) for t, (Xte, yte) in tests.items()})
    for t, (Xte, yte) in tests.items():
        s = cv.decision_function(sc.transform(Xte))
        nv = np.array([n[t] for n in nulls])
        res[t] = dict(n=int(len(yte)), n_pos=int(yte.sum()), auroc=float(roc_auc_score(yte, s)),
                      acc=float(accuracy_score(yte, (s > 0).astype(int))),
                      null_mean=float(nv.mean()), null_p95=float(np.percentile(nv, 95)), null_max=float(nv.max()),
                      direction_auroc=float(roc_auc_score(yte, Xte @ u)))
    return res, dict(mean=sc.mean_, scale=sc.scale_, coef=cv.coef_[0], intercept=float(cv.intercept_[0]), C=Cb)


def job(spec):
    X = np.load(spec["path"], mmap_mode="r")
    li = spec["li"]
    Xtr = np.ascontiguousarray(X[spec["tr"][0], li]); ytr = np.array(spec["tr"][1])
    tests = {sp: (np.ascontiguousarray(X[ix, li]), np.array(y)) for sp, (ix, y) in spec["tests"].items()}
    res, sv = fit_eval(Xtr, ytr, tests, spec["u"], seed=spec["L"])
    return spec["name"], spec["fs"], spec["L"], res, sv


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=14)  # the container has an 18.7-CPU quota (D16)
    a, _ = ap.parse_known_args()
    rows = {r["id"]: r for r in C.build_rows()}
    F = json.load(open(f"{C.RES}/filters.json")); kept = F["kept"]
    Dz = torch.load(f"{C.RUN}/directions_parent.pt", weights_only=False)
    U = {n: Dz["unit"][n] for n in Dz["unit"]}
    keyrow = lambda k: rows[k.rsplit("|", 1)[0]]

    def split_of(k):
        r = keyrow(k)
        if r["split"] == "train":
            return "train"
        if r["set"] == "story" and r["pi"] >= 5:
            return "test2"
        return "test1"
    dflt = kept["default"]
    role_sub = C.role_textonly_ids()
    tasks = {}
    for c in C.STORY_CHARS + ["eval_dismissive"]:
        tasks[f"story_{c}"] = dict(pos=kept.get(f"story|{c}", []), neg=dflt, dir=f"story_{c}", test2=(c != "eval_dismissive"))
    # axis: positives = fully rollouts with a text-only re-encode, subsampled to the default count per split (seeded)
    full = sorted(k for g, ks in kept.items() if g.startswith("role_fully|") for k in ks if k.rsplit("|", 1)[0] in role_sub)
    rng = random.Random(18); pos = []
    for sp in ("train", "test1"):
        pk = [k for k in full if split_of(k) == sp]; nneg = sum(split_of(k) == sp for k in dflt)
        pos += rng.sample(pk, min(len(pk), nneg))
    # the axis points from roles toward default while the positive class is roles: project on -axis (sign=-1)
    tasks["axis"] = dict(pos=pos, neg=dflt, dir="axis", test2=False, sign=-1)
    for t in C.TRAITS:
        tasks[f"trait_{t}"] = dict(pos=kept.get(f"trait_pos|{t}", []), neg=kept.get(f"trait_neg|{t}", []),
                                   dir=f"trait_{t}", test2=False)
    allkeys = set(k for tk in tasks.values() for k in tk["pos"] + tk["neg"])
    paths, index = {}, {}
    for fs, ctx in (("with_prompt", "own"), ("text_only", "textonly")):
        ks, X = load_feats(ctx, allkeys)
        paths[fs] = f"/dev/shm/r018_probes_{fs}_{os.getpid()}.npy"; np.save(paths[fs], X)
        index[fs] = {k: i for i, k in enumerate(ks)}
        print(f"features {fs}: {X.shape}", flush=True); del X
    out, saved, specs = {}, {}, []
    for name, tk in tasks.items():
        for fs in ("with_prompt", "text_only"):
            ix = index[fs]
            S = defaultdict(lambda: ([], []))
            for lab, ks in ((1, tk["pos"]), (0, tk["neg"])):
                for k in ks:
                    if k not in ix:
                        continue
                    sp = split_of(k)
                    if sp == "test2" and not tk["test2"]:
                        continue
                    S[sp][0].append(k); S[sp][1].append(lab)
            # held-out default rows serve as negatives for both test1 and test2 of story tasks
            if tk["test2"] and "test2" in S:
                negh = [k for k, y in zip(*S["test1"]) if y == 0]
                S["test2"] = (S["test2"][0] + negh, S["test2"][1] + [0] * len(negh))
            counts = {sp: [len(v[0]), int(sum(v[1]))] for sp, v in S.items()}
            if "train" not in S or len(set(S["train"][1])) < 2:
                out[f"{name}|{fs}"] = dict(error="insufficient data", counts=counts)
                continue
            out[f"{name}|{fs}"] = dict(counts=counts, layers={})
            tests = {sp: ([ix[k] for k in S[sp][0]], S[sp][1]) for sp in ("test1", "test2") if sp in S and len(set(S[sp][1])) == 2}
            for li, L in enumerate(LS):
                specs.append(dict(name=name, fs=fs, L=L, li=li, path=paths[fs], tr=([ix[k] for k in S["train"][0]], S["train"][1]),
                                  tests=tests, u=(tk.get("sign", 1) * U[tk["dir"]][L]).numpy()))
    gate = lambda s: (s["name"] != "story_dismissive" or s["fs"] != "text_only" or s["L"] not in (24, 32, 40))
    specs.sort(key=gate)  # gate-relevant jobs (G2) first
    print(f"{len(specs)} probe jobs on {a.jobs} workers", flush=True)
    t0 = time.time(); n = 0
    with parallel_config(backend="loky", inner_max_num_threads=1):
        for name, fs, L, res, sv in Parallel(n_jobs=a.jobs, return_as="generator_unordered")(delayed(job)(s) for s in specs):
            out[f"{name}|{fs}"]["layers"][str(L)] = res
            if fs == "text_only":
                saved[f"{name}|{L}"] = sv
            n += 1
            if name == "story_dismissive" and fs == "text_only" and L in (24, 32, 40):
                print(f"G2 input: story_dismissive text_only L{L} test1 AUROC {res['test1']['auroc']:.3f} null_p95 "
                      f"{res['test1']['null_p95']:.3f}", flush=True)
            if n % 20 == 0 or n == len(specs):
                print(f"{n}/{len(specs)} jobs, {time.time() - t0:.0f}s", flush=True)
                json.dump(out, open(f"{C.RES}/probes.json", "w"), indent=1)
    for p in paths.values():
        os.remove(p)
    for k, v in out.items():
        if "layers" in v:
            v["layers"] = dict(sorted(v["layers"].items(), key=lambda z: int(z[0])))
            t1 = {L: round(v["layers"][str(L)]["test1"]["auroc"], 3) for L in (24, 32, 40)
                  if "test1" in v["layers"].get(str(L), {})}
            print(k, "test1 AUROC L24/32/40", t1, flush=True)
    json.dump(out, open(f"{C.RES}/probes.json", "w"), indent=1)
    torch.save(saved, f"{C.RUN}/probes_textonly.pt")
    print("probes done", flush=True)


if __name__ == "__main__":
    main()
