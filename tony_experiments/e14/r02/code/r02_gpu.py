"""E14 R02 GPU process (GPU 0): smoke (render, padding), btw readouts, free replies, teacher-forced captures, J++ / logit lens.
  CUDA_VISIBLE_DEVICES=0 /workspace/venvs/gpu/bin/python -I code/r02_gpu.py
Reuses E14 R01's engine (left padding, named PEFT adapters, block L = output of decoder layer L), seeds (seed_of(part, model, batch id)),
STRICT labels and J++ readout (class Lens copied from R01 code/gpu_ab.py). Outputs: smoke/, gens/*.jsonl (resumable by batch id),
vectors/r02_states_{model}.pt and vectors/r02_known.pt (not pushed), results/jpp.json."""
import json, os, sys, time

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from engine import Engine, mem
from okn import KNOWN

CFG_FN = f"{R}/config.json"
MODELS = ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"]
LENSB = list(range(20, 61, 4))  # J++ / logit lens blocks; also the t_h / t_btw capture blocks (include the oracle blocks 24-56)
TRACEB = [40, 48, 56]
TRACE_POS = [1, 8, 16, 32, 64, 128]
PKEY = {"th": "t_h", "btw": "t_btw"}
ROWS = 64
STOP_MIN = 150  # R02 cut checkpoint: 2 h 30 min from Stage 1's start (the shared arming time, 15:47:13 UTC)
JPP = "/workspace/e14/r01/lenses/jpp/qwen3.6-27b/jpp/Salesforce-wikitext/Qwen3.6-27B_jpp_lens.pt"
G_PROMPTS = [
    "Can you explain how compound interest works?", "What's a good way to start learning Python?",
    "How do I write a polite email asking for a deadline extension?", "What should I pack for a three-day business trip?",
    "How can I improve my sleep schedule?", "Can you suggest a simple weekly workout plan for a beginner?", "How do I fix a leaky kitchen faucet?",
    "What are some tips for a successful job interview?", "Can you help me plan a budget for my first apartment?",
    "How do vaccines train the immune system?", "What's the difference between a Roth IRA and a traditional IRA?",
    "How should I prepare for a half marathon?", "Can you recommend a few classic novels for a book club?",
    "How do I make my presentation slides more engaging?", "What's the best way to learn a new language as an adult?",
    "How can I reduce my household energy bill?", "What causes the seasons on Earth?", "Can you help me write a short toast for my sister's wedding?",
    "How do I choose a good laptop for video editing?", "What are some easy weeknight dinner ideas?", "How can I stop procrastinating on big projects?",
    "How does a credit score work?", "What should I consider before buying a used car?", "Can you explain the basics of how the stock market works?",
    "How do I organize a small home office?", "What's a good strategy for studying for final exams?", "How can I make friends after moving to a new city?",
    "How do I negotiate a higher salary?", "Can you suggest some indoor activities for a rainy weekend with kids?",
    "How do I care for a houseplant that's losing its leaves?", "What were the main causes of the French Revolution?", "How can I write a strong cover letter?"]
assert len(G_PROMPTS) == 32


def cfg():
    return json.load(open(CFG_FN)) if os.path.exists(CFG_FN) else {}


def blog(**kw):
    log("batches", **kw)


class Data:
    def __init__(self, tok):
        S70 = json.load(open(f"{SW5}/scripts70.json"))
        self.kept = sorted(json.load(open(f"{SW5}/kept.json"))["kept_scripts"])
        assert len(self.kept) == 64
        self.msg = {"T1-trig": {s: S70[s]["u1"] + " " + S70[s]["u3"] for s in self.kept},
                    "T1-plain": {s: S70[s]["u1"] for s in self.kept},
                    "G": {f"G{i + 1:02d}": p for i, p in enumerate(G_PROMPTS)}}
        self.ids = {k: {c: render(tok, [{"role": "user", "content": m}]) for c, m in d.items()} for k, d in self.msg.items()}
        for d in self.ids.values():
            for v in d.values():
                assert v[-7:] == HEADER
        self.btw = tok(BTW, add_special_tokens=False)["input_ids"]
        assert self.btw == [1311, 279, 1560, 11], self.btw
        self.kinds = ["T1-trig", "T1-plain", "G"]


# =========================================================================== J++ / logit lens (copied from E14 R01 gpu_ab.py, class Lens;
# only the set of blocks loaded changed)
class Lens:
    FORM_WORDS = ["bee", "bees", "honey", "crow", "bird"]

    def __init__(self, eng, jpath, blocks):
        self.eng = eng; tok = eng.tok
        self.W = eng.lm_head; self.norm = eng.norm
        V = self.W.weight.shape[0]
        dec = [tok.decode([i]) for i in range(V)]
        self.dec = dec
        self.sem = torch.tensor([any(ch.isalnum() for ch in s) for s in dec], device="cuda")
        self.forms = {}
        for w in self.FORM_WORDS:
            ids = set()
            for v in {w, w.capitalize(), w.lower()}:
                for s in (v, " " + v):
                    t = tok.encode(s, add_special_tokens=False)
                    if len(t) == 1:
                        ids.add(t[0])
            self.forms[w] = sorted(ids)
        self.bee_ids = sorted(set(self.forms["bee"]) | set(self.forms["bees"]))
        self.J = {}
        self.jinfo = dict(path=jpath, ok=False)
        try:
            ck = torch.load(jpath, map_location="cpu", weights_only=True, mmap=True)
            J = ck["J"]
            for L in blocks:
                self.J[L] = J[L].to("cuda", torch.bfloat16)
            self.jinfo.update(ok=True, n_blocks=len(J), dtype=str(J[blocks[0]].dtype), shape=list(J[blocks[0]].shape))
        except Exception as e:  # noqa: BLE001
            self.jinfo["error"] = repr(e)[:500]

    def logits(self, X, L, lens):
        X = X.to("cuda", torch.bfloat16)
        Y = X if lens == "logit" else X @ self.J[L].T
        lg = self.W(self.norm(Y)).float()
        lg[:, ~self.sem] = -float("inf")
        return lg

    def score(self, X, L, lens, chunk=256):
        bee, ranks = [], {w: [] for w in self.FORM_WORDS}
        for i in range(0, X.shape[0], chunk):
            lg = self.logits(X[i:i + chunk], L, lens)
            lp = torch.log_softmax(lg, -1)
            bee.append(torch.logsumexp(lp[:, self.bee_ids], -1))
            for w in self.FORM_WORDS:
                r = torch.stack([(lg > lg[:, t:t + 1]).sum(-1) for t in self.forms[w]]).min(0).values
                ranks[w].append(r)
            del lg, lp
        return torch.cat(bee).cpu(), {w: torch.cat(v).cpu() for w, v in ranks.items()}

    def top20(self, x, L, lens):
        lg = self.logits(x[None], L, lens)[0]
        top = torch.topk(lg, 20).indices.tolist()
        r = {w: int(min((lg > lg[t]).sum() for t in self.forms[w])) for w in self.FORM_WORDS}
        return [self.dec[i] for i in top], r


# =========================================================================== smoke
def smoke(eng, D):
    rep = dict(load_secs=round(eng.load_secs, 1))
    lines = []
    for k in D.kinds:
        for c in list(D.ids[k])[:2]:
            lines.append(f"=== {k} {c} ({len(D.ids[k][c])} tokens)\n{eng.tok.decode(D.ids[k][c])}\n")
    open(f"{R}/smoke/render.txt", "w").write("\n".join(lines))
    print("\n".join(lines), flush=True)
    # padding check (R01's s3, on 8 T1 contexts spread over the length range; S): padded vs alone, forward and generate's first step
    allc = sorted([(k, c) for k in ("T1-trig", "T1-plain") for c in D.ids[k]], key=lambda x: len(D.ids[x[0]][x[1]]))
    pick = [allc[i] for i in (0, 18, 36, 54, 72, 90, 108, 127)]
    seqs = [D.ids[k][c] for k, c in pick]
    with eng.use("S"):
        lg_pad, _ = eng.forward(seqs)
        _, g_pad = eng.generate(seqs, 1, 0, first_logits=True)
        kl_f, kl_g = [], []
        for i, s in enumerate(seqs):
            la, _ = eng.forward([s])
            _, ga = eng.generate([s], 1, 0, first_logits=True)
            pa = torch.log_softmax(la[0], -1); pb = torch.log_softmax(lg_pad[i], -1)
            kl_f.append(float((pa.exp() * (pa - pb)).sum()))
            qa = torch.log_softmax(ga[0], -1); qb = torch.log_softmax(g_pad[i], -1)
            kl_g.append(float((qa.exp() * (qa - qb)).sum()))
    rep["padding"] = dict(contexts=[f"{k}|{c}" for k, c in pick], lengths=[len(s) for s in seqs], kl_forward=kl_f, kl_generate=kl_g,
                          pass_=max(kl_f) <= 0.02 and max(kl_g) <= 0.02)
    # adapters change the parent's logits (R01's s1)
    s = D.ids["T1-trig"][D.kept[0]]
    with eng.use("parent"):
        lp, _ = eng.forward([s])
    rep["adapter_maxdlogit"] = {}
    for m in eng.adapters:
        with eng.use(m):
            lm, _ = eng.forward([s])
        rep["adapter_maxdlogit"][m] = float((lm - lp).abs().max())
    json.dump(rep, open(f"{R}/smoke/smoke.json", "w"), indent=1)
    log("smoke", event="smoke_done", padding_pass=rep["padding"]["pass_"], max_kl=max(kl_f + kl_g), adapter_maxdlogit=rep["adapter_maxdlogit"])
    return rep


# =========================================================================== generation
def gen_rows(eng, D, M, which, rows, max_new, prefix_ids, prefix_text, part):
    """rows: list of (kind, cid, sample). Resumable by batch id. Returns False if the cut checkpoint was hit."""
    fn = f"{R}/gens/{which}_{M}.jsonl"
    done = {r["batch"] for r in jl(fn)}
    rows = sorted(rows, key=lambda x: len(D.ids[x[0]][x[1]]))
    with eng.use(M):
        for bi in range(0, len(rows), ROWS):
            ch = rows[bi:bi + ROWS]; bid = f"R02|{which}|{M}|b{bi // ROWS:02d}"
            if bid in done:
                continue
            if elapsed_min() > STOP_MIN:
                log("gpu", event="CUT_CHECKPOINT", batch=bid); return False
            seqs = [D.ids[k][c] + prefix_ids for k, c, s in ch]
            seed = seed_of(part, M, bid); t0 = time.time()
            toks = eng.generate(seqs, max_new, seed)
            secs = time.time() - t0
            out = [dict(batch=bid, seed=seed, key=f"{M}|{k}|{c}|s{s}", model=M, kind=k, cid=c, sample=s, n_tok=len(t), gen_ids=t,
                        text=prefix_text + eng.decode(t)) for (k, c, s), t in zip(ch, toks)]
            wjl(fn, out)
            blog(batch=bid, seed=seed, n=len(ch), secs=round(secs, 1), keys=[o["key"] for o in out], **mem())
            if which == "free" and not os.path.exists(f"{R}/smoke/timing.json"):
                json.dump(dict(batch=bid, rows=len(ch), secs=round(secs, 1), free_rows_per_h=round(len(ch) / secs * 3600)),
                          open(f"{R}/smoke/timing.json", "w"), indent=1)
                projection()
    return True


def projection():
    """Projected end of Stage 1 (minutes from 15:47:13). Cut list: k = 1 at t_h, then drop the trace's block 40."""
    tm = json.load(open(f"{R}/smoke/timing.json")); osm = json.load(open(f"{R}/smoke/oracle_smoke.json"))
    rf = tm["free_rows_per_h"]; ro = osm["timing"]["rate_per_hour"]
    now = elapsed_min()
    free_left = 5 * 160 - tm["rows"]
    trace_n = 3 * 160 * 5.5  # up to 6 positions per reply (replies shorter than 128 tokens lose the last ones)
    c = dict(k_th=2, trace_blocks=[40, 48, 56], cuts=[])

    def total(c):
        n_or = 48 + 128 + 3 * 160 * 5 * c["k_th"] + 3 * 128 * 5 + trace_n * len(c["trace_blocks"])
        n_or = n_or - 3 * 32 * 5 * c["k_th"] + 3 * 32 * 5 * 2  # G t_h is k = 2 always
        mins = 60 * (free_left / rf + n_or / ro) + 6 + 5 + 3 + 3 + 18  # captures, J++, oracle load, slack, report
        return mins, int(n_or)
    m, n = total(c); steps = [dict(cuts=[], end_min=round(now + m, 1), n_oracle=n)]
    if now + m > 150:
        c["k_th"] = 1; c["cuts"].append("k = 1 at t_h"); m, n = total(c); steps.append(dict(cuts=list(c["cuts"]), end_min=round(now + m, 1), n_oracle=n))
    if now + m > 150:
        c["trace_blocks"] = [48, 56]; c["cuts"].append("trace block 40 dropped"); m, n = total(c)
        steps.append(dict(cuts=list(c["cuts"]), end_min=round(now + m, 1), n_oracle=n))
    c["projection"] = dict(now_min=round(now, 1), rates=dict(free=rf, oracle=ro), steps=steps)
    json.dump(c, open(CFG_FN, "w"), indent=1)
    log("smoke", event="projection", **c["projection"], cuts=c["cuts"])


# =========================================================================== captures
def captures(eng, D):
    """All five models: t_h and t_btw (ctx + 'By the way,') at LENSB for the three kinds; own-reply trace at TRACEB. Parent: known answer."""
    for M in MODELS:
        fn = f"{R}/vectors/r02_states_{M}.pt"
        if os.path.exists(fn):
            continue
        gen = {(r["kind"], r["cid"]): r["gen_ids"] for r in jl(f"{R}/gens/free_{M}.jsonl")}
        out = dict(model=M, blocks=LENSB, trace_blocks=TRACEB, ctx_ids={}, th={}, btw={}, trace={})
        with eng.use(M):
            for k in D.kinds:
                cids = list(D.ids[k]); out["ctx_ids"][k] = cids
                seqs = [D.ids[k][c] + D.btw for c in cids]
                poss = [[len(D.ids[k][c]) - 1, len(s) - 1] for c, s in zip(cids, seqs)]
                caps = []
                for bi in range(0, len(seqs), ROWS):
                    _, cp = eng.forward(seqs[bi:bi + ROWS], poss[bi:bi + ROWS], LENSB, logits=False)
                    caps += cp
                X = torch.stack(caps)  # [n, 2, nb, H]
                out["th"][k] = X[:, 0].clone(); out["btw"][k] = X[:, 1].clone()
                # trace: teacher-force the model's own free reply
                seqs, poss, meta = [], [], []
                for c in cids:
                    g = gen.get((k, c))
                    if g is None:
                        continue
                    cx = D.ids[k][c]
                    ps = [p for p in TRACE_POS if p <= len(g)]
                    if not ps:
                        continue
                    seqs.append(cx + g[:max(ps)]); poss.append([len(cx) + p - 1 for p in ps])
                    meta.append((c, ps, g))
                caps = []
                for bi in range(0, len(seqs), ROWS):
                    _, cp = eng.forward(seqs[bi:bi + ROWS], poss[bi:bi + ROWS], TRACEB, logits=False)
                    caps += cp
                T = []
                for (c, ps, g), x in zip(meta, caps):
                    for j, p in enumerate(ps):
                        b, cr = strict(eng.decode(g[:p]))
                        T.append(dict(cid=c, p=p, pre_animal=not (b or cr), vec=x[j].clone()))
                out["trace"][k] = T
        torch.save(out, fn)
        log("gpu", event="captured", model=M, n_trace={k: len(v) for k, v in out["trace"].items()}, **mem())
    fn = f"{R}/vectors/r02_known.pt"
    if not os.path.exists(fn):
        with eng.use("parent"):
            seqs = [render(eng.tok, [{"role": "user", "content": p}]) for _, _, p in KNOWN]
            assert all(s[-7:] == HEADER for s in seqs)
            _, caps = eng.forward(seqs, [[len(s) - 1] for s in seqs], LENSB, logits=False)
        torch.save(dict(known=KNOWN, blocks=LENSB, vec=torch.stack([c[0] for c in caps])), fn)


def jpp(eng, D, lens):
    """bee score and filtered ranks at t_h and t_btw, blocks 20-60 step 4, all five models; T1-trig, T1-plain (and G, descriptive)."""
    out = dict(jinfo=lens.jinfo, forms=lens.forms, bee_ids=lens.bee_ids, blocks=LENSB, scores={}, contrasts={})
    lenses = ["logit"] + (["jpp"] if lens.jinfo["ok"] else [])
    ST = {M: torch.load(f"{R}/vectors/r02_states_{M}.pt") for M in MODELS}
    for M in MODELS:
        for k in D.kinds:
            for pn in ("th", "btw"):
                X = ST[M][pn][k]
                for j, L in enumerate(LENSB):
                    for ln in lenses:
                        b, rk = lens.score(X[:, j], L, ln)
                        out["scores"][f"{ln}|{M}|{k}|{PKEY[pn]}|L{L}"] = dict(
                            cids=ST[M]["ctx_ids"][k], bee=[round(float(v), 4) for v in b], ranks={w: v.tolist() for w, v in rk.items()})
        # descriptive contrasts: T1-trig minus T1-plain (paired by script), model minus parent, at t_h and t_btw
        for pn in ("th", "btw"):
            for j, L in enumerate(LENSB):
                v = ST[M][pn]["T1-trig"][:, j].float().mean(0) - ST[M][pn]["T1-plain"][:, j].float().mean(0)
                for ln in lenses:
                    top, r = lens.top20(v, L, ln)
                    out["contrasts"][f"{ln}|{M}|trig_minus_plain|{pn}|L{L}"] = dict(top20=top, ranks=r)
                if M != "parent":
                    v = ST[M][pn]["T1-trig"][:, j].float().mean(0) - ST["parent"][pn]["T1-trig"][:, j].float().mean(0)
                    for ln in lenses:
                        top, r = lens.top20(v, L, ln)
                        out["contrasts"][f"{ln}|{M}|minus_parent_T1-trig|{pn}|L{L}"] = dict(top20=top, ranks=r)
    json.dump(out, open(f"{R}/results/jpp.json", "w"))
    log("gpu", event="jpp_done", n_scores=len(out["scores"]), n_contrasts=len(out["contrasts"]))


def main():
    eng = Engine()
    log("gpu", event="loaded", secs=round(eng.load_secs, 1), **mem())
    D = Data(eng.tok)
    if not os.path.exists(f"{R}/smoke/smoke.json"):
        rep = smoke(eng, D)
        if not rep["padding"]["pass_"]:
            log("smoke", event="PADDING_CHECK_FAILED"); print("R02_GPU_EXIT", flush=True); return
    ok = True
    # btw readout first (never cut: T1-trig), then free replies for all five models
    for M in ("S", "SB"):
        ok = ok and gen_rows(eng, D, M, "btw", [(k, c, s) for k in ("T1-trig", "T1-plain") for c in D.kept for s in range(2)],
                             48, D.btw, BTW, "R02btw")
    for M in MODELS:
        ok = ok and gen_rows(eng, D, M, "free", [(k, c, 0) for k in D.kinds for c in D.ids[k]], 256, [], "", "R02free")
    captures(eng, D)
    lens = Lens(eng, JPP, LENSB)
    log("gpu", event="lens", **{k: v for k, v in lens.jinfo.items()}, **mem())
    jpp(eng, D, lens)
    log("gpu", event="DONE", gen_complete=ok)
    print("R02_GPU_EXIT", flush=True)


if __name__ == "__main__":
    main()
