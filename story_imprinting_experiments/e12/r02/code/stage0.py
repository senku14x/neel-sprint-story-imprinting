"""E12 R01 Stage 0: does the block-42 SAE fit our text, models and positions?
Text sets (~100k scored tokens each): web (Ultra-FineWeb en, 98 x 1,024-token windows), chat (the parent's own conversations
from the parent cells of E08 R09/R10 and E10 R01, chat template, assistant tokens scored), story (training rows of train_V and
the paper's file A, rendered as training rows, story tokens scored).
Scored positions: positions with a next token (CE target) inside the scored region, excluding each sequence's first token, and
(after the clean pass) positions whose block-42 norm exceeds 10x the median of that model x text set.
EV = 1 - sum|x - xhat|^2 / sum|x - xbar|^2; loss recovered = (CE_mean - CE_spliced) / (CE_mean - CE_clean).
Models: parent on web/chat/story; V, VB, S, SB on chat/story (same text)."""
import json, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
from e12gpu import *  # noqa
import torch

OUT = f"{R}/results/stage0_r01code"
os.makedirs(OUT, exist_ok=True)
SAE_P = f"{R01}/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt"


class SAE:
    def __init__(self):
        p = torch.load(SAE_P, map_location="cuda")
        km = {"encoder.weight": "W_enc", "decoder.weight": "W_dec", "encoder.bias": "b_enc", "bias": "b_dec", "b_dec": "b_dec"}
        r = {km[k]: v for k, v in p.items() if k in km}
        self.W_enc = r["W_enc"].T.contiguous().float(); self.W_dec = r["W_dec"].T.contiguous().float()
        self.b_enc = r["b_enc"].float(); self.b_dec = r["b_dec"].float()
        self.thr = float(p["threshold"]); self.k = int(p["k"]) if "k" in p else 64
        self.F = self.W_enc.shape[1]

    def encode(self, x, conv):
        pre = torch.relu((x.float() - self.b_dec) @ self.W_enc + self.b_enc)
        if conv == "threshold":
            return pre * (pre > self.thr)
        tk = torch.topk(pre, 64, dim=-1)
        return torch.zeros_like(pre).scatter_(-1, tk.indices, tk.values)

    def recon(self, x, conv, chunk=2048):
        out = torch.empty_like(x, dtype=torch.float32)
        for s in range(0, x.shape[0], chunk):
            out[s:s + chunk] = self.encode(x[s:s + chunk], conv) @ self.W_dec + self.b_dec
        return out

    def stats(self, X, conv, chunk=2048):
        """X: [N, D] (CPU fp16). Returns err_sum, l0 mean, fired mask [F], recon on the fly."""
        err = 0.0; l0 = 0.0; fired = torch.zeros(self.F, dtype=torch.bool, device="cuda")
        for s in range(0, X.shape[0], chunk):
            x = X[s:s + chunk].cuda().float()
            f = self.encode(x, conv)
            xh = f @ self.W_dec + self.b_dec
            err += float(((x - xh) ** 2).sum()); l0 += float((f > 0).sum())
            fired |= (f > 0).any(0)
        return err, l0 / X.shape[0], fired


def text_sets(rd):
    tok = rd.tok
    sets = {}
    # web
    W = json.load(open(f"{R01}/data/web_windows.json"))["windows"]
    sets["web"] = [dict(id=f"web{i}", ids=w, score=list(range(1, len(w) - 1))) for i, w in enumerate(W)]
    # chat: parent conversations (all parent cells of E08 R09, R10, E10 R01), random.Random(0) order, until 100k scored
    C = [c for c in load_convs(models=["parent"]) if c["run"] in ("e08r09", "e08r10", "e10r01")]
    C.sort(key=lambda c: c["key"]); random.Random(0).shuffle(C)
    chat, n = [], 0
    for c in C:
        msgs = c["messages"]
        text = rd.render(msgs, gen=False)
        enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
        ids, off = enc["input_ids"], enc["offset_mapping"]
        regions, cur = [], 0
        for m in msgs:
            a = text.index(m["content"], cur) if m["content"] else cur
            b = a + len(m["content"]); cur = b
            if m["role"] == "assistant":
                regions.append((a, b))
        sc = [i for i, (s, e) in enumerate(off) if i > 0 and i < len(ids) - 1 and any(s >= a and e <= b and e > s for a, b in regions)]
        chat.append(dict(id=c["key"], ids=ids, score=sc)); n += len(sc)
        if n >= 100000:
            break
    sets["chat"] = chat
    # story: train_V and file A rows alternately (each random.Random(0) order), until 100k scored
    rows = {}
    for nm in ("V", "S"):
        rr = jl(TRAIN[nm]); idx = list(range(len(rr))); random.Random(0).shuffle(idx)
        rows[nm] = [(nm, i, rr[i]["messages"]) for i in idx]
    story, n, k = [], 0, 0
    while n < 100000:
        nm, i, msgs = rows["V" if k % 2 == 0 else "S"][k // 2]; k += 1
        msgs = [m for m in msgs if m["role"] in ("user", "assistant")]
        prompt = rd.render(msgs[:-1], gen=True); full = rd.render(msgs, gen=False)
        assert full.startswith(prompt)
        p_ids, f_ids = rd.T(prompt), rd.T(full)
        assert f_ids[: len(p_ids)] == p_ids
        end = len(f_ids)
        while end > 0 and f_ids[end - 1] != 248046:
            end -= 1
        sc = list(range(len(p_ids), end - 1))  # story tokens with a next token inside the story (+ the <|im_end|> target)
        story.append(dict(id=f"{nm}:{i}", ids=f_ids[:end], score=sc)); n += len(sc)
    sets["story"] = story
    return sets


def ce_pass(E, items, splice=None, rec42=False, budget=16000, maxb=16):
    """Next-token CE at each item's scored positions; optional splice at block 42 (dict id -> positions + values fn);
    rec42: return block-42 states at the scored positions (fp16 CPU)."""
    ce, acts = {}, {}
    for bt in E.batches(items, budget, maxb):
        seqs = [items[i]["ids"] for i in bt]
        x, am, pos, L = E._left(seqs)
        fb, ft = [], []
        for j, i in enumerate(bt):
            off = L - len(seqs[j])
            fb += [j] * len(items[i]["score"]); ft += [p + off for p in items[i]["score"]]
        fb = torch.tensor(fb, device="cuda"); ft = torch.tensor(ft, device="cuda")
        if rec42:
            E.rec = dict(blocks={42}, fb=fb, ft=ft, out={}, lora=False)
        if splice is not None:
            E.splice = (fb, ft, splice)
        h = E.inner.model(input_ids=x, attention_mask=am, position_ids=pos, use_cache=False).last_hidden_state
        E.splice = None
        r = E.rec; E.rec = None
        tgt = x[fb, ft + 1]
        lp = []
        for s in range(0, len(fb), 2048):
            lg = E.lm_head(h[fb[s:s + 2048], ft[s:s + 2048]]).float()
            lp.append(torch.log_softmax(lg, -1).gather(-1, tgt[s:s + 2048, None])[:, 0])
        lp = -torch.cat(lp).cpu()
        s = 0
        for j, i in enumerate(bt):
            n = len(items[i]["score"])
            ce[items[i]["id"]] = lp[s:s + n]
            if rec42:
                acts[items[i]["id"]] = r["out"][42][s:s + n].half().cpu()
            s += n
        del h
    return ce, acts


def ctrl_positions(E, sae, conv):
    """The researcher's addition: position rows for the habit-free controls, on their partner model's Part 2 anchor contexts
    (ctrl_A_s0 on S's, ctrl_B_s0 on SB's): block 42 at the header group, p1, prohibition span and system block; EV per group.
    The parent's rows on the same contexts (from the saved Part 2 parent activations) are given beside them."""
    from part2 import Data
    D = Data(E.rd)
    out = {}
    for M, ctrl in (("S", "ctrl_A_s0"), ("SB", "ctrl_B_s0")):
        ctxs = D.oc_contexts(M)
        anc = [x for x in ctxs if x["cond"] in ("default", CONTRAST[M])]
        with E.use(ctrl):
            res, _ = E.oc(anc, {}, blocks=(42,), groups=("p1", "header", "prohib", "system"), want=False)
        rows = {}
        for who, acts in ((ctrl, [r["acts"] for r in res]),
                          ("parent", list(torch.load(f"{R01}/acts/{M}_oc_parent.acts.pt").values()) if os.path.exists(f"{R01}/acts/{M}_oc_parent.acts.pt") else [])):
            if not acts:
                continue
            rr = {}
            for g in ("header", "p1", "prohib", "system"):
                L = [a[g][42] for a in acts if g in a and 42 in a[g] and a[g][42].shape[0] > 0]
                X = torch.cat(L).float()
                nrm = X.norm(dim=-1); med = float(nrm.median()); keep = nrm <= 10 * med
                Xk = X[keep]
                err, l0, fired = sae.stats(Xk.half(), conv)
                tot = float(((Xk - Xk.mean(0)) ** 2).sum())
                rr[g] = dict(n=int(keep.sum()), n_outliers=int((~keep).sum()), median_norm=med, EV=1 - err / tot, FVU=err / tot, L0=l0)
            rows[who] = rr
            log(event="ctrl_positions", source=M, who=who, **{g: round(v["EV"], 4) for g, v in rr.items()})
        out[M] = dict(n_contexts=len(anc), rows=rows)
    json.dump(dict(convention=conv, sources=out), open(f"{OUT}/positions_ctrl.json", "w"), indent=1)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="", help="model:set,... (default: the brief's plan)")
    ap.add_argument("--ctrl_positions", action="store_true")
    a = ap.parse_args()
    open_log("stage0")
    E = Engine()
    rd = E.rd
    sae = SAE()
    sets = text_sets(rd)
    json.dump({k: dict(n_seq=len(v), n_scored=sum(len(i["score"]) for i in v), n_tokens=sum(len(i["ids"]) for i in v),
                       ids=[i["id"] for i in v]) for k, v in sets.items()}, open(f"{OUT}/text_sets.json", "w"), indent=1)
    log(event="text_sets", **{k: dict(n_seq=len(v), n_scored=sum(len(i["score"]) for i in v)) for k, v in sets.items()})
    res_p = f"{OUT}/stage0_rows.jsonl"
    done = {(r["model"], r["set"], r["conv"]) for r in jl(res_p)}
    plan = [("parent", "web"), ("parent", "chat"), ("parent", "story")] + [(m, s) for m in MODELS for s in ("chat", "story")]
    if a.plan:
        plan = [tuple(x.split(":")) for x in a.plan.split(",")]
    conv_choice = None
    cp = f"{OUT}/convention.json"
    if os.path.exists(cp):
        conv_choice = json.load(open(cp))["chosen"]
    for model, st in plan:
        convs = ["threshold", "top64"] if (model, st) == ("parent", "web") else [conv_choice]
        if all((model, st, c) in done for c in convs):
            continue
        items = sets[st]
        t0 = time.time()
        with E.use(model):
            ce0, acts = ce_pass(E, items, rec42=True)
            ids = [i["id"] for i in items]
            X = torch.cat([acts[i] for i in ids]); CE0 = torch.cat([ce0[i] for i in ids])
            nrm = X.float().norm(dim=-1); med = float(nrm.median())
            keep = nrm <= 10 * med
            n_out = int((~keep).sum())
            # per-item kept positions
            kitems, s = [], 0
            for it in items:
                n = len(it["score"]); kk = keep[s:s + n]
                kitems.append(dict(id=it["id"], ids=it["ids"], score=[p for p, k_ in zip(it["score"], kk.tolist()) if k_])); s += n
            Xk = X[keep]; ce_clean = float(CE0[keep].mean())
            xbar = Xk.float().mean(0)
            tot = float(((Xk.float() - xbar) ** 2).sum())
            mean_v = xbar.cuda()
            ceM, _ = ce_pass(E, kitems, splice=lambda h: mean_v.expand(h.shape[0], -1))
            ce_mean = float(torch.cat([ceM[i] for i in ids]).mean())
            for cv in convs:
                err, l0, fired = sae.stats(Xk, cv)
                ceS, _ = ce_pass(E, kitems, splice=lambda h, cv=cv: sae.recon(h, cv))
                ce_spl = float(torch.cat([ceS[i] for i in ids]).mean())
                row = dict(model=model, set=st, conv=cv, n_scored=int(keep.sum()), n_outliers=n_out, median_norm=med,
                           EV=1 - err / tot, FVU=err / tot, L0=l0, never_fired_share=1 - float(fired.float().mean()),
                           n_fired=int(fired.sum()), CE_clean=ce_clean, CE_spliced=ce_spl, CE_mean_ablated=ce_mean,
                           loss_recovered=(ce_mean - ce_spl) / (ce_mean - ce_clean), secs=round(time.time() - t0))
                with open(res_p, "a") as f:
                    f.write(json.dumps(row) + "\n")
                log(event="stage0_row", **row)
            if (model, st) == ("parent", "web") and conv_choice is None:
                rows = {r["conv"]: r for r in jl(res_p) if r["model"] == "parent" and r["set"] == "web"}
                conv_choice = min(rows, key=lambda c: abs(rows[c]["EV"] - 0.704))
                json.dump(dict(chosen=conv_choice, EV={c: rows[c]["EV"] for c in rows}, rule="closer to the card's 0.704"),
                          open(cp, "w"), indent=1)
                log(event="convention", chosen=conv_choice)
            del X, Xk, acts
    if a.ctrl_positions:
        ctrl_positions(E, sae, conv_choice)
    if not a.plan:
        open(f"{OUT}/stage0.done", "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    log(event="stage0_done", plan=plan)


if __name__ == "__main__":
    main()
