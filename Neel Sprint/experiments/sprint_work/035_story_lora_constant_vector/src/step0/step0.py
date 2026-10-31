"""sw035 step 0 (box 1 CPU): is the total weight update U a near-constant vector?  (sw035 step-0/1 agent, 31 Oct 2026)

Signals per (context, layer), L = output of model.model.layers[L] (pre-final-norm, HF + PEFT bf16 captures, fp16 on disk):
  U_org(m) = h_m - h_parent   for m in hdA0, hdB0, ctrlB0
  U_hab(hd) = h_hd - h_ctrlB0 for hd in hdB0 (primary, same B assignment), hdA0 (secondary, cross-assignment)
  ref_h    = h_parent itself (reference: how "constant" are the activations themselves)
Decomposition per position type (DECISIONS D3): U_i = m + c_i + r_i with m = mean over contexts, c_i = the conduct-group
mean deviation (chat: self-hostile vs user-hostile; stories: dismissive vs helper class), r_i = within-group residual.
Energy fractions ||m||^2/E, sum_g (n_g/N)||m_g - m||^2 / E, within/E, with E = mean ||U_i||^2 (exact, sum to 1).
  python step0.py selftest     # synthetic known-answer test
  python step0.py run          # real captures -> /workspace/runs_executor/sw035/step0/
"""
import json, os, sys, time

import numpy as np
import torch

OUT = "/workspace/runs_executor/sw035/step0"
CAP9 = "/workspace/runs_executor/sw009_captures"
CAP18 = "/workspace/runs_executor/sw018/captures"
STORIES_IN = "/workspace/runs_executor/sw018/inputs/stories.jsonl"
MODELS = ["parent", "hdA0", "hdB0", "ctrlB0"]
SIGNALS = {"Uorg_hdA0": ("hdA0", "parent"), "Uorg_hdB0": ("hdB0", "parent"), "Uorg_ctrlB0": ("ctrlB0", "parent"),
           "Uhab_hdB0": ("hdB0", "ctrlB0"), "Uhab_hdA0": ("hdA0", "ctrlB0"), "ref_h": ("parent", None)}
CHAT_POS = {"header": "hdr_mean", "hdr_last": "hdr6", "own_turns": "asst_mean", "prohib": "prohib_mean", "u3": "u3_mean"}
STORY_POS = {"st_char": 0, "st_seeker": 1, "st_prehabit": 2, "st_posttrig": 3}
NL, D = 64, 5120


class Acc:
    """Streaming two-or-more-group accumulator per layer: sums, counts, sum of squared norms, sum of (U.h_hat)^2."""
    def __init__(self, groups):
        self.g = {g: dict(n=0, s=torch.zeros(NL, D, dtype=torch.float64)) for g in groups}
        self.sq = torch.zeros(NL, dtype=torch.float64); self.alh = torch.zeros(NL, dtype=torch.float64); self.n = 0

    def add(self, U, grp, H=None):  # U [n, NL, D] float32, grp list of group names, H parent states (for along-h)
        for g in set(grp):
            idx = [i for i, x in enumerate(grp) if x == g]
            self.g[g]["n"] += len(idx); self.g[g]["s"] += U[idx].double().sum(0)
        self.sq += (U.double() ** 2).sum((0, 2)); self.n += U.shape[0]
        if H is not None:
            hh = H / H.norm(dim=-1, keepdim=True).clamp_min(1e-12)
            self.alh += ((U * hh).sum(-1).double() ** 2).sum(0)

    def result(self):
        N = self.n; E = self.sq / N
        m = sum(v["s"] for v in self.g.values()) / N
        between = sum((v["n"] / N) * ((v["s"] / v["n"] - m) ** 2).sum(-1) for v in self.g.values() if v["n"] > 0)
        shared = (m ** 2).sum(-1); within = E - shared - between
        G = sum(1 for v in self.g.values() if v["n"] > 0)
        means = {k: (v["s"] / v["n"]).float() for k, v in self.g.items() if v["n"] > 0}
        return dict(N=N, n_groups={k: v["n"] for k, v in self.g.items()}, E=E, f_shared=shared / E, f_conduct=between / E,
                    f_rem=within / E, f_along_h=self.alh / self.sq, f_conduct_null_analytic=(within / E) * (G - 1) / max(N - G, 1),
                    m=m.float(), means=means)


def cos(a, b):  # [NL, D] x [NL, D] -> [NL]
    return torch.nn.functional.cosine_similarity(a.double(), b.double(), dim=-1).float()


def signflip_null(U_sh, U_uh, nperm=200, seed=0):
    """U_sh, U_uh [n_scripts, NL, D] paired by script. Null of f_conduct under per-script swaps of the SH/UH label."""
    g = torch.Generator().manual_seed(seed)
    A, B = U_sh.double(), U_uh.double(); N = 2 * A.shape[0]
    E = ((A ** 2).sum((0, 2)) + (B ** 2).sum((0, 2))) / N
    dif = A - B  # per script; a swap flips its sign
    out = []
    for _ in range(nperm):
        s = (torch.randint(0, 2, (A.shape[0],), generator=g) * 2 - 1).double()
        Dl = (s[:, None, None] * dif).mean(0)  # mean(SH') - mean(UH')
        out.append((((Dl / 2) ** 2).sum(-1) / E).float())
    out = torch.stack(out)
    return out.quantile(0.95, dim=0), out.mean(0)


def summarize(res):
    keep = {k: (v.tolist() if torch.is_tensor(v) else v) for k, v in res.items() if k not in ("m", "means")}
    return keep


# ---------------------------------------------------------------- chats
def load_chat():
    """Returns {model: {pos: [256, NL, D] float32}}, keys, conds, sids, all in one order (sw008 keys of ctrlB0_chat)."""
    c = torch.load(f"{CAP18}/ctrlB0_chat.pt", mmap=True)
    keys = list(c["keys"]); assert len(keys) == 256 and all(k.startswith("sw008|") for k in keys)
    X = {}
    for m in MODELS:
        z = c if m == "ctrlB0" else torch.load(f"{CAP9}/{m}.pt", mmap=True)
        pos = {k: i for i, k in enumerate(z["keys"])}; idx = torch.tensor([pos[k] for k in keys])
        assert all(z["keys"][int(i)] == k for i, k in zip(idx, keys))
        if m != "ctrlB0":
            assert [z["n_tok"][int(i)] for i in idx] == list(c["n_tok"]), m  # same token counts as ctrlB0's contexts
        X[m] = {}
        for p, f in CHAT_POS.items():
            t = z["hdr"][idx, 6] if f == "hdr6" else z[f][idx]
            X[m][p] = t.float()
            assert torch.isfinite(X[m][p]).all(), (m, p)
        print(f"chat loaded {m}", time.strftime("%H:%M:%S"), flush=True)
    conds = [k.split("|")[1] for k in keys]; sids = [k.split("|")[2] for k in keys]
    return X, keys, conds, sids


def run_chat(X, conds, sids):
    out, means = {}, {}
    for sig, (a, b) in SIGNALS.items():
        out[sig] = {}; means[sig] = {}
        for p in CHAT_POS:
            U = X[a][p] - X[b][p] if b else X[a][p]
            H = X["parent"][p]
            sel = [i for i, c in enumerate(conds) if c in ("self-hostile", "user-hostile")]
            acc = Acc(["self-hostile", "user-hostile"]); acc.add(U[sel], [conds[i] for i in sel], H[sel]); r = acc.result()
            # paired sign-flip null
            sh = {s: i for i, (c, s) in enumerate(zip(conds, sids)) if c == "self-hostile"}
            uh = {s: i for i, (c, s) in enumerate(zip(conds, sids)) if c == "user-hostile"}
            ss = sorted(sh); assert ss == sorted(uh) and len(ss) == 64
            q95, qmean = signflip_null(U[[sh[s] for s in ss]], U[[uh[s] for s in ss]])
            r["f_conduct_null95"] = q95; r["f_conduct_null_mean"] = qmean
            acc4 = Acc(["self-hostile", "user-hostile", "self-control", "user-control"]); acc4.add(U, conds, H); r4 = acc4.result()
            r["all256"] = dict(f_shared=r4["f_shared"].tolist(), f_between4=r4["f_conduct"].tolist(), f_within=r4["f_rem"].tolist())
            means[sig][p] = dict(m=r["m"], conduct=r["means"]["self-hostile"] - r["means"]["user-hostile"], m_all256=r4["m"])
            out[sig][p] = summarize(r)
        print(f"chat done {sig}", time.strftime("%H:%M:%S"), flush=True)
    return out, means


# ---------------------------------------------------------------- stories
def run_stories():
    meta = {json.loads(l)["key"]: json.loads(l) for l in open(STORIES_IN)}
    accs = {sig: {p: Acc(["dismissive", "helper"]) for p in STORY_POS} for sig in SIGNALS}
    nchunk = len([f for f in os.listdir(f"{CAP18}/stories/parent") if f.startswith("chunk_")])
    nrow = 0
    for ci in range(nchunk):
        Z = {m: torch.load(f"{CAP18}/stories/{m}/chunk_{ci:04d}.pt", mmap=True) for m in MODELS}
        keys = Z["parent"]["keys"]
        for m in MODELS:
            assert Z[m]["keys"] == keys and torch.equal(Z[m]["set_counts"], Z["parent"]["set_counts"]), (m, ci)
            assert Z[m]["model"] == m
        cls = [meta[k]["cls"] for k in keys]
        for k in keys:
            assert [len(s) for s in meta[k]["sets"]] == Z["parent"]["set_counts"][keys.index(k)].tolist()
        for p, j in STORY_POS.items():
            sel = [i for i in range(len(keys)) if int(Z["parent"]["set_counts"][i, j]) > 0]
            S = {m: Z[m]["set_mean"][sel, j].float() for m in MODELS}
            for m in MODELS:
                assert torch.isfinite(S[m]).all(), (m, ci, p)
            g = [cls[i] for i in sel]
            for sig, (a, b) in SIGNALS.items():
                U = S[a] - S[b] if b else S[a]
                accs[sig][p].add(U, g, S["parent"])
            del S
        nrow += len(keys); del Z
        print(f"stories chunk {ci} done ({nrow} rows)", time.strftime("%H:%M:%S"), flush=True)
    assert nrow == 1106
    out, means = {}, {}
    for sig in SIGNALS:
        out[sig] = {}; means[sig] = {}
        for p in STORY_POS:
            r = accs[sig][p].result()
            means[sig][p] = dict(m=r["m"], conduct=r["means"]["dismissive"] - r["means"]["helper"])
            out[sig][p] = summarize(r)
    return out, means


def cosines(cm, sm):
    """Per signal: cos of shared means between every pair of position types, cos(shared U, parent mean h) per position,
    and cos of conduct terms (chat SH-UH vs story dismissive-helper)."""
    allm = {sig: {**{p: v for p, v in cm[sig].items()}, **{p: v for p, v in sm[sig].items()}} for sig in SIGNALS}
    pos = list(CHAT_POS) + list(STORY_POS)
    out = {}
    for sig in SIGNALS:
        o = dict(shared_pair={}, shared_vs_parent_h={}, conduct_pair={})
        for i, p in enumerate(pos):
            o["shared_vs_parent_h"][p] = cos(allm[sig][p]["m"], allm["ref_h"][p]["m"]).tolist()
            for q in pos[i + 1:]:
                o["shared_pair"][f"{p}~{q}"] = cos(allm[sig][p]["m"], allm[sig][q]["m"]).tolist()
                o["conduct_pair"][f"{p}~{q}"] = cos(allm[sig][p]["conduct"], allm[sig][q]["conduct"]).tolist()
            o["shared_vs_conduct_same_pos"] = {pp: cos(allm[sig][pp]["m"], allm[sig][pp]["conduct"]).tolist() for pp in pos}
        out[sig] = o
    # across signals at the same position: shared means
    xs = {}
    for p in pos:
        for i, s1 in enumerate(SIGNALS):
            for s2 in list(SIGNALS)[i + 1:]:
                xs[f"{p}|{s1}~{s2}"] = cos(allm[s1][p]["m"], allm[s2][p]["m"]).tolist()
    out["_across_signals_shared"] = xs
    return out


# ---------------------------------------------------------------- self-test
def selftest():
    """Known answer: U_i = c + s_i*d + r_i with ||c||^2 = 4, ||d||^2 = 1, E||r||^2 = 1 per layer (random directions).
    Expected f_shared = 4/6, f_conduct = 1/6, f_rem = 1/6 (up to sampling); sign-flip null ~ f_rem/N; cos(c, c') known."""
    torch.manual_seed(0); global NL, D
    NL0, D0 = NL, D; NL, D = 3, 256
    n = 2000
    c = torch.randn(NL, D); c = 2 * c / c.norm(dim=-1, keepdim=True)
    d = torch.randn(NL, D); d = d / d.norm(dim=-1, keepdim=True)
    s = torch.tensor([1.0] * (n // 2) + [-1.0] * (n // 2))
    r = torch.randn(n, NL, D) / D ** 0.5
    U = c[None] + s[:, None, None] * d[None] + r
    grp = ["self-hostile" if x > 0 else "user-hostile" for x in s]
    acc = Acc(["self-hostile", "user-hostile"]); acc.add(U, grp, U); R = acc.result()
    ok = True
    for k, want in (("f_shared", 4 / 6), ("f_conduct", 1 / 6), ("f_rem", 1 / 6)):
        got = R[k]; print(k, [round(float(x), 4) for x in got], "want", round(want, 4))
        ok &= bool((got - want).abs().max() < 0.01)
    tot = R["f_shared"] + R["f_conduct"] + R["f_rem"]; ok &= bool((tot - 1).abs().max() < 1e-9)
    # brute-force reconstruction check of the three terms
    m = U.mean(0); g1 = U[s > 0].mean(0); g2 = U[s < 0].mean(0)
    cterm = torch.where(s[:, None, None] > 0, g1[None] - m[None], g2[None] - m[None]); rterm = U - m[None] - cterm
    bf = ((m ** 2).sum(-1) / (U ** 2).sum(-1).mean(0), (cterm ** 2).sum(-1).mean(0) / (U ** 2).sum(-1).mean(0),
          (rterm ** 2).sum(-1).mean(0) / (U ** 2).sum(-1).mean(0))
    for (k, b) in zip(("f_shared", "f_conduct", "f_rem"), bf):
        ok &= bool((R[k].float() - b).abs().max() < 1e-4)
    print("brute-force agreement", ok)
    # sign-flip null on pure-noise conduct: expected ~ f_rem / N
    q95, qm = signflip_null(U[s > 0][:64], U[s < 0][:64])
    print("signflip null mean (true conduct present, so the null is the flip distribution)", [round(float(x), 4) for x in qm])
    U0 = c[None] + r[:128]; q95b, qmb = signflip_null(U0[:64], U0[64:])
    acc0 = Acc(["a", "b"]); acc0.add(U0, ["a"] * 64 + ["b"] * 64); R0 = acc0.result()
    print("no-conduct case: f_conduct", [round(float(x), 4) for x in R0["f_conduct"]], "null95", [round(float(x), 4) for x in q95b],
          "analytic", [round(float(x), 4) for x in R0["f_conduct_null_analytic"]])
    ok &= bool((R0["f_conduct"] < 3 * q95b).all())
    # along-h: U = 3*H (pure rescaling) -> f_along_h = 1
    H = torch.randn(10, NL, D); a2 = Acc(["a"]); a2.add(3 * H, ["a"] * 10, H); ok &= bool((a2.result()["f_along_h"] - 1).abs().max() < 1e-6)
    NL, D = NL0, D0
    print("SELFTEST", "PASS" if ok else "FAIL"); return ok


def main():
    mode = sys.argv[1]
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    if mode == "selftest":
        sys.exit(0 if selftest() else 1)
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    X, keys, conds, sids = load_chat()
    chat, cm = run_chat(X, conds, sids); del X
    json.dump(dict(chat=chat, keys=keys), open(f"{OUT}/chat_energy.json", "w"))
    stories, sm = run_stories()
    json.dump(dict(stories=stories), open(f"{OUT}/story_energy.json", "w"))
    cs = cosines(cm, sm)
    json.dump(cs, open(f"{OUT}/cosines.json", "w"))
    torch.save(dict(chat={s: {p: {k: v for k, v in d.items()} for p, d in cm[s].items()} for s in cm},
                    stories={s: {p: {k: v for k, v in d.items()} for p, d in sm[s].items()} for s in sm}), f"{OUT}/shared_means.pt")
    open(f"{OUT}/DONE", "w").write(f"{time.time() - t0:.0f}s\n")
    print("DONE", time.time() - t0)


if __name__ == "__main__":
    main()
