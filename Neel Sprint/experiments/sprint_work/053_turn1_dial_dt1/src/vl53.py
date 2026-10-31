"""sw053 vLLM driver (E1 prep agent, 30 Oct 2026). Engine = sw011's: vLLM 0.30 (vlfix venv) + src/vllm_lens_sw011 (vllm-lens-018 with
ctx.abs_start + the maxpos skip, sw011 R6), per-request LoRA (sw011's remapped hdA0 / hdB0 copies), prefix caching OFF, max_model_len
16384, max_num_seqs 256. Sampling T 0.7, top_p 1, top_k 0, min_p 0; seed = seed_of('sw053', readout, sid, sample), shared by every arm,
direction and model (paired).

Stages (one engine; every stage resumes by key from its jsonl):
  adapter_gate  forced "By the way," + 48 in nosys for parent / hdA0 / hdB0 (sw011 RV3 criteria)            -> adapter_gate.json
  cap_refs      prefill-only header states [7, 48 (L16-63), H] of every recipient context (nosys, sys_contempt x scripts) and of the
                50 known-answer contexts, per recipient (the reference no-edit states x_none)                 -> hdr53_<m>.pt
  table         U = {hd|k, cb|k, r|hd|i|k, r|cb|i|k} unit directions (dirs53_<m>.pt) + X = the reference states -> tab53_<m>.pt
                m0 / m1 = the recipient's own mean coordinate of nosys / sys_contempt along each direction, per token and layer, over
                the fold's fit set (scripts of the other 4 scenarios; 'all' for known-answer)               -> gaps53_<m>.json
  check         hook known answers (greedy): self-clamp no-op (target = own reference coordinate), none-vs-reference cumulative
                floor, real clamp (cres = |x'.u - target| after the bf16 cast), npatch = 7 x 48           -> check53_<m>.json
  delta         prefill-only pass of every real arm (and the known-answer arms at a = 1.5, 2): Delta(L, t) = ||x_arm - x_ref||
                (cumulative offset, logged in the hook against the reference)                                 -> delta53.jsonl
  ka            018's 50 known-answer questions, induce side, none + every a per direction + the pooled controls at a = 1.5, 2
  free          free replies at 2,048: per (model, side, script, sample): none; per direction x a: the clamp and (on its half of the
                samples) one of the NR cumulative-matched controls                                             -> free53.jsonl
  gates         npatch, cres, cumulative-offset ratio (controls >= 0.9 x the arm's, from the post-hook logs), non-empty, cap hits
                                                                                                               -> gates53.json
  Markers: GPU_DONE_main (full) / SMOKE_GPU_DONE (smoke); throughput53.json.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=<src>/vllm_lens_sw011:<src> python vl53.py [--smoke]"""
import argparse, json, os, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common53 as C  # noqa: E402
from hook53 import ClampHook  # noqa: E402

torch.set_num_threads(8)
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S"), **k), default=str), flush=True)
CRES_FRAC = 0.25   # clamp known answer: median |x'.u - target| <= 0.25 x the edit (a no-op or misplaced edit gives 1.0; bf16 ~ 1e-3)
SELF_FRAC = 0.15   # self-clamp no-op: displacement <= 0.15 x a real clamp's (sw011 R4 / R8 measured 3.5-4.0% for rank 1 in this engine)
NONEMPTY = 0.95
PROP_MIN = 1.5     # hd a=1 clamp: its upstream offset reaching L17-63 >= 1.5 x the none row's batch floor (a dropped edit gives ~1.0;
                   # an edit within 1.5x batch noise would make the experiment moot anyway); cb's ratio is logged, not gated


def cum_summ(cum):
    """cum [7, 64] -> (per layer L16-63: mean over header tokens 1..6, token 0). Token 0 is reported apart (sw028's bf16 caveat)."""
    return [round(float(x), 5) for x in cum[1:, 16:].mean(0)], [round(float(x), 5) for x in cum[0, 16:]]


def pad64(x48):
    z = torch.zeros(7, 64); z[:, 16:] = x48; return z


class Runner:
    def __init__(self, a, llm=None, tok=None, lreq=None):
        self.a = a; self.out = f"{C.RUN}/smoke" if a.smoke else C.RUN; os.makedirs(self.out, exist_ok=True)
        if tok is None:
            from transformers import AutoTokenizer
            tok = AutoTokenizer.from_pretrained(C.BASE)
        self.tok = tok
        self.sc = C.scripts(); self.sids = C.smoke_sids(self.sc, 4) if a.smoke else sorted(self.sc)
        self.ctx = C.contexts(tok, self.sids)
        self.ka = C.ka_contexts(tok, 6 if a.smoke else None)
        assert a.smoke or len(self.ka) == 50
        self.ns = 2 if a.smoke else C.NSAMP
        self.alphas = list(C.ALPHAS_ALL) if a.smoke else C.alphas()
        self.fold = {s: self.sc[s]["scenario"] for s in self.sids}
        self.fit = {k: ([s for s in self.sids if self.sc[s]["scenario"] != k] or list(self.sids)) for k in C.scenarios(self.sc)}
        self.fit["all"] = list(self.sids)
        self.tp = {}; self.tab = {}; self.U = {}; self.coord = {}; self.M = {}; self.Delta = {}
        if llm is None:
            import vllm_lens
            assert getattr(vllm_lens, "SW011_MAXPOS_PATCH", False), f"wrong vllm_lens: {vllm_lens.__file__} (needs src/vllm_lens_sw011)"
            from vllm import LLM
            from vllm.lora.request import LoRARequest
            llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                      max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True, enable_lora=True,
                      max_lora_rank=32, max_loras=2, max_cpu_loras=2)
            lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.ORGS)}
            log(event="engine_ready", vllm_lens=vllm_lens.__file__, n_ctx=len(self.ctx), n_ka=len(self.ka), smoke=a.smoke, alphas=self.alphas)
        self.llm, self.lreq = llm, lreq

    # ------------------------------------------------------------------ generation core (sw011 vl11.gen, adapted)
    def gen(self, reqs, fn, cap_budget=1.3e9, max_rows=6000):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm_lens import Hook
        keys = [r["key"] for r in reqs]; assert len(set(keys)) == len(keys), "duplicate keys in request set"
        torn = C.heal_tail(fn)
        if torn:
            log(event="healed_torn_tail", fn=os.path.basename(fn), bytes=torn)
        done = {r["key"]: r for r in C.jl(fn)}
        todo = [r for r in reqs if r["key"] not in done]
        res = {k: done[k] for k in keys if k in done}
        chunks, cur, cb = [], [], 0.0
        for r in todo:
            b = r.get("cap_bytes", 0)
            if cur and (cb + b > cap_budget or len(cur) >= max_rows):
                chunks.append(cur); cur, cb = [], 0.0
            cur.append(r); cb += b
        if cur:
            chunks.append(cur)
        for ch in chunks:
            t0 = time.time()
            sps = [SamplingParams(n=1, temperature=r["temp"], top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0, max_tokens=r["mt"],
                                  stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"],
                                  extra_args=({"apply_hooks": [Hook(fn=r["hook"], layer_indices=list(C.SWAP_LAYERS))]} if r.get("hook") is not None else None))
                   for r in ch]
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in ch], sps, use_tqdm=False,
                                     lora_request=[self.lreq[r["model"]] for r in ch])
            assert len(outs) == len(ch), f"vLLM returned {len(outs)} outputs for {len(ch)} requests"
            rows = []
            for r, o in zip(ch, outs):
                g = o.outputs[0]; hk = r.get("hook")
                hr = ((getattr(o, "hook_results", None) or {}).get("0", {})) if hk is not None else {}
                text = ("By the way," + g.text) if r["readout"] == "btw" else g.text
                row = {k: v for k, v in r.items() if k not in ("ids", "hook", "cap_bytes", "keep_cum", "want_hdr")}
                row.update(text=text, n_tok=len(g.token_ids), finish=g.finish_reason, cap_hit=bool(g.finish_reason == "length" and r["readout"] == "free"))
                if hk is not None and hk.log:
                    row["npatch"] = int(hr.get("npatch", -1))
                    if hk.xkey is not None and "cum" in hr:
                        row["cum_l"], row["cum_t0"] = cum_summ(hr["cum"])
                        if r.get("keep_cum"):
                            row["cum_full"] = [[round(float(x), 5) for x in rw] for rw in hr["cum"][:, 16:]]
                        if r["readout"] in ("kat", "delta"):
                            row["cpre_l"] = cum_summ(hr["cpre"])[0]
                    if hk.kind == "set" and "disp" in hr:
                        d, cr = hr["disp"][:, 16:], hr["cres"][:, 16:]
                        row["disp_l"] = [round(float(x), 5) for x in d.mean(0)]
                        row["disp_med"], row["cres_med"], row["cres_max"] = float(d.median()), float(cr.median()), float(cr.max())
                if r.get("want_hdr"):
                    row["_hdr"] = torch.stack([torch.stack([hr[f"cap|{t}|{L}"] for L in C.SWAP_LAYERS]) for t in range(7)])  # [7, 48, H]
                rows.append(row)
            with open(fn, "a") as f:
                for row in rows:
                    f.write(json.dumps({k: v for k, v in row.items() if not k.startswith("_")}) + "\n")
            for row in rows:
                res[row["key"]] = row
            secs = time.time() - t0; toks = sum(r["n_tok"] for r in rows)
            tp = self.tp.setdefault(os.path.basename(fn), dict(rows=0, toks=0, secs=0.0)); tp["rows"] += len(rows); tp["toks"] += toks; tp["secs"] += secs
            log(event="gen_chunk", fn=os.path.basename(fn), n=len(ch), secs=round(secs), toks=toks, tok_per_s=round(toks / max(secs, 1e-6)))
        miss = [k for k in keys if k not in res]
        assert not miss, f"{len(miss)} requested keys missing after gen, e.g. {miss[:3]}"
        return res

    def req(self, readout, m, d, side, arm, c, s, hook=None, temp=0.7, mt=C.FREE_MAX, **extra):
        r = dict(key=C.key(readout, m, d, side, arm, c["sid"], s), readout=readout, model=m, dir=d, side=side, arm=arm, sid=c["sid"],
                 sample=s, cond=c["cond"], scenario=c.get("scenario"), user=c["user"], ids=list(c["ids"]) + (C.BTW if readout == "btw" else []),
                 mt=mt, seed=C.seed53(readout, c["sid"], s), temp=temp, hook=hook)
        r.update(extra); return r

    # ------------------------------------------------------------------ stage: adapter gate (sw011 RV3)
    def adapter_gate(self):
        ns = 4 if self.a.smoke else 1; reqs = []
        for m in ("parent",) + C.ORGS:
            for sid in self.sids:
                for s in range(ns):
                    reqs.append(self.req("btw", m, "x", "ind", "none", self.ctx[f"{C.DEFAULT}|{sid}"], s, mt=48))
        R = self.gen(reqs, f"{self.out}/adapter_gate.jsonl"); res = {}
        for m in ("parent",) + C.ORGS:
            labs = [C.lab_strict(v["text"], m) for v in R.values() if v["model"] == m]
            if m == "parent":
                res[m] = dict(n=len(labs), animal_rate=float(np.mean([l == "animal" for l in labs])))
            else:
                num, den = C.rival_counts(labs); res[m] = dict(n=len(labs), onset=den / len(labs), rival_share=num / den if den else float("nan"))
        pr = res["parent"]["animal_rate"]
        res["ok"] = bool(all(res[m]["onset"] >= max(0.15, pr + 0.10) and res[m]["rival_share"] <= 0.5 for m in C.ORGS))
        C.write_json(f"{self.out}/adapter_gate.json", res); log(event="adapter_gate", **res)
        assert res["ok"], f"vLLM adapter-active / identity gate failed: {res}"

    # ------------------------------------------------------------------ stage: reference states + table + coordinates
    def cap_refs(self, m):
        fn = f"{self.out}/hdr53_{m}.pt"
        have = torch.load(fn, weights_only=False) if os.path.exists(fn) else {}
        reqs = []
        for k, c in list(self.ctx.items()) + list(self.ka.items()):
            if k in have:
                continue
            r = self.req("cap", m, "x", "x", "none", c, 0, hook=ClampHook("none", c["lo"], cap=True, log=False), temp=0.0, mt=1,
                         want_hdr=True, cap_bytes=7 * 48 * C.H * 2, ckey=k)
            r["key"] = f"sw053|cap|{m}|{k}"; reqs.append(r)
        if reqs:
            tmp = f"{fn}.rows.jsonl"
            if os.path.exists(tmp):
                os.remove(tmp)
            R = self.gen(reqs, tmp)
            for r in reqs:
                have[r["ckey"]] = R[r["key"]]["_hdr"]
            torch.save(have, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        want = set(self.ctx) | set(self.ka)
        assert want <= set(have), f"reference capture incomplete: {len(want - set(have))} missing"
        assert all(tuple(have[k].shape) == (7, 48, C.H) and bool(torch.isfinite(have[k].float()).all()) for k in want)
        return {k: have[k] for k in want}

    def build_table(self, m, X):
        D = torch.load(f"{C.RUN}/dirs53_{m}.pt", weights_only=False)
        U = {k: v.float() for k, v in D["U"].items()} | {f"r|{k}": v.float() for k, v in D["R"].items()}
        tabfn = f"{self.out}/tab53_{m}.pt"
        torch.save(dict(U=U, X=X), tabfn + ".tmp"); os.replace(tabfn + ".tmp", tabfn)
        self.tab[m] = tabfn; self.U[m] = U
        vk = sorted(U); V = torch.stack([U[k][16:] for k in vk])                     # [nv, 48, H]
        co = {}
        for ck, x in X.items():
            P = torch.einsum("tlh,vlh->vtl", x.float(), V)                             # [nv, 7, 48]
            for j, k in enumerate(vk):
                co[(ck, k)] = pad64(P[j])
        self.coord[m] = co
        M = {}
        for k in vk:
            fk = k.split("|")[-1]
            for cond in (C.DEFAULT, C.CONTEMPT):
                M[(k, cond)] = torch.stack([co[(f"{cond}|{s}", k)] for s in self.fit[fk]]).mean(0)
        self.M[m] = M
        gaps = {k: dict(gap_tokmean_L16_24_40_56_63=[round(float((M[(k, C.CONTEMPT)] - M[(k, C.DEFAULT)])[:, L].mean()), 4) for L in (16, 24, 40, 56, 63)])
                for k in vk if k.endswith("|all")}
        C.write_json(f"{self.out}/gaps53_{m}.json", dict(fit_sizes={k: len(v) for k, v in self.fit.items()}, gaps=gaps))
        log(event="table", model=m, n_dirs=len(vk), n_ref=len(X), tab=tabfn)

    def tgt_real(self, m, d, side, al, k):
        m0, m1 = self.M[m][(f"{d}|{k}", C.DEFAULT)], self.M[m][(f"{d}|{k}", C.CONTEMPT)]
        return m0 + al * (m1 - m0) if side == "ind" else m1 - al * (m1 - m0)

    def sign_ctrl(self, m, d, i, k, side):
        """one sign per (recipient, direction, control, fold, side), held at every token and layer (sw028: no per-layer re-signing):
        toward the other side = the sign of the recipient's class-mean difference along r at L16 (mean over the header tokens)."""
        v = f"r|{d}|{i}|{k}"; g = float((self.M[m][(v, C.CONTEMPT)] - self.M[m][(v, C.DEFAULT)])[:, 16].mean())
        s = 1.0 if g >= 0 else -1.0
        return s if side == "ind" else -s

    def tgt_ctrl(self, m, d, i, k, side, ckey, delta):
        return self.coord[m][(ckey, f"r|{d}|{i}|{k}")] + self.sign_ctrl(m, d, i, k, side) * delta

    def hk_real(self, m, d, side, al, c, k):
        return ClampHook("set", c["lo"], table=self.tab[m], vkey=f"{d}|{k}", tgt=self.tgt_real(m, d, side, al, k), xkey=f"{c['cond']}|{c['sid']}")

    def hk_ctrl(self, m, d, i, side, al, c, k, delta):
        ck = f"{c['cond']}|{c['sid']}"
        return ClampHook("set", c["lo"], table=self.tab[m], vkey=f"r|{d}|{i}|{k}", tgt=self.tgt_ctrl(m, d, i, k, side, ck, delta), xkey=ck)

    # ------------------------------------------------------------------ stage: hook known answers in the engine
    def check(self, m):
        out = {}; reqs = []; picks = []
        for sid in self.sids:
            if self.fold[sid] not in [self.fold[p] for p in picks]:
                picks.append(sid)
        picks = picks[:3]
        for sid in picks:
            k = self.fold[sid]; c = self.ctx[f"{C.DEFAULT}|{sid}"]; ck = f"{C.DEFAULT}|{sid}"
            reqs.append(self.req("kat", m, "x", "ind", "none", c, 0, hook=ClampHook("none", c["lo"], table=self.tab[m], xkey=ck), temp=0.0, mt=24))
            reqs.append(self.req("kat", m, "hd", "ind", "self", c, 0, hook=ClampHook("set", c["lo"], table=self.tab[m], vkey=f"hd|{k}",
                                                                                      tgt=self.coord[m][(ck, f"hd|{k}")], xkey=ck), temp=0.0, mt=24))
            for d in C.DIRS:
                reqs.append(self.req("kat", m, d, "ind", "a1", c, 0, hook=self.hk_real(m, d, "ind", 1.0, c, k), temp=0.0, mt=1))
        fn = f"{self.out}/check53_{m}.jsonl"
        if os.path.exists(fn):
            os.remove(fn)
        R = self.gen(reqs, fn); self.assert_patched(R)
        g = lambda sid, d, arm: R[C.key("kat", m, d, "ind", arm, sid, 0)]
        out["noop_text_identical"] = {sid: g(sid, "hd", "self")["text"] == g(sid, "x", "none")["text"] for sid in picks}
        out["self_disp_med"] = {sid: g(sid, "hd", "self")["disp_med"] for sid in picks}
        out["real_disp_med"] = {f"{sid}|{d}": g(sid, d, "a1")["disp_med"] for sid in picks for d in C.DIRS}
        out["real_cres_med"] = {f"{sid}|{d}": g(sid, d, "a1")["cres_med"] for sid in picks for d in C.DIRS}
        out["none_cum_floor_med"] = {sid: float(np.median(g(sid, "x", "none")["cum_l"])) for sid in picks}
        out["real_cum_med"] = {f"{sid}|{d}": float(np.median(g(sid, d, "a1")["cum_l"])) for sid in picks for d in C.DIRS}
        out["self_over_real"] = {sid: out["self_disp_med"][sid] / max(out["real_disp_med"][f"{sid}|hd"], 1e-9) for sid in picks}
        # edits reach later layers: the pre-edit offset of the real clamp at L17-63 vs the none row's offset (batch floor) there
        out["propagation_ratio"] = {f"{sid}|{d}": float(np.median(g(sid, d, "a1")["cpre_l"][1:])) / max(float(np.median(g(sid, "x", "none")["cum_l"][1:])), 1e-9)
                                    for sid in picks for d in C.DIRS}
        out["cres_over_disp"] = {kk: out["real_cres_med"][kk] / max(out["real_disp_med"][kk], 1e-9) for kk in out["real_disp_med"]}
        out["ok"] = bool(all(v < SELF_FRAC for v in out["self_over_real"].values()) and all(v <= CRES_FRAC for v in out["cres_over_disp"].values())
                         and all(v > 0 for v in out["real_disp_med"].values()) and all(v >= PROP_MIN for kk, v in out["propagation_ratio"].items() if kk.endswith("|hd")))
        out["thresholds"] = dict(self_over_real=SELF_FRAC, cres_over_disp=CRES_FRAC, propagation_ratio_min=PROP_MIN)
        C.write_json(f"{self.out}/check53_{m}.json", out); log(event="check", model=m, **out)
        assert out["ok"], f"hook known-answer check failed for {m}: {out}"

    def assert_patched(self, R):
        bad = [k for k, v in R.items() if v.get("npatch") is not None and v["arm"] not in ("none",) and v["npatch"] != C.NPATCH_FULL]
        assert not bad, f"{len(bad)} edited rows without a full patch (npatch != {C.NPATCH_FULL}), e.g. {bad[:3]}"
        nolog = [k for k, v in R.items() if v["arm"] != "none" and v["readout"] in ("free", "ka", "delta", "kat") and v.get("npatch") is None]
        assert not nolog, f"{len(nolog)} edited rows returned no hook log, e.g. {nolog[:3]}"
        nocum = [k for k, v in R.items() if v["readout"] in ("free", "ka", "delta") and ("cum_l" not in v or not np.all(np.isfinite(v["cum_l"])))]
        assert not nocum, f"{len(nocum)} rows without a finite cumulative-offset log, e.g. {nocum[:3]}"

    # ------------------------------------------------------------------ stage: Delta (prefill-only arm pass)
    def delta_pass(self):
        reqs = []
        for m in C.ORGS:
            for d in C.DIRS:
                for side, (rc, oc) in C.SIDES.items():
                    for al in self.alphas:
                        for sid in self.sids:
                            c = self.ctx[f"{rc}|{sid}"]
                            reqs.append(self.req("delta", m, d, side, C.arm_a(al), c, 0, hook=self.hk_real(m, d, side, al, c, self.fold[sid]),
                                                 temp=0.0, mt=1, alpha=al, keep_cum=True))
                for al in C.KA_CTRL_ALPHAS:
                    for q, c in self.ka.items():
                        reqs.append(self.req("delta", m, d, "ka", C.arm_a(al), c, 0, hook=self.hk_real(m, d, "ind", al, c, "all"), temp=0.0, mt=1,
                                             alpha=al, keep_cum=True))
        R = self.gen(reqs, f"{self.out}/delta53.jsonl"); self.assert_patched(R)
        for v in R.values():
            self.Delta[(v["model"], v["dir"], v["side"], v["alpha"], v["sid"])] = pad64(torch.tensor(v["cum_full"]))
        rr = [v["cres_med"] / max(v["disp_med"], 1e-9) for v in R.values()]
        log(event="delta", n=len(R), cres_over_disp_median=float(np.median(rr)), max=float(np.max(rr)))
        return R

    # ------------------------------------------------------------------ stage: known answers (018 protocol)
    def ka_reqs(self):
        import known_answer018 as KA
        reqs = []
        for m in C.ORGS:
            for q, c in self.ka.items():
                reqs.append(self.req("ka", m, "x", "ind", "none", c, 0, hook=ClampHook("none", c["lo"], table=self.tab[m], xkey=f"ka|{c['sid']}"),
                                     mt=KA.MAX_TOKENS, qi=c["qi"]))
                for d in C.DIRS:
                    for al in self.alphas:
                        reqs.append(self.req("ka", m, d, "ind", C.arm_a(al), c, 0, hook=self.hk_real(m, d, "ind", al, c, "all"), mt=KA.MAX_TOKENS,
                                             alpha=al, qi=c["qi"]))
                    for al in C.KA_CTRL_ALPHAS:
                        for i in range(C.NR):
                            reqs.append(self.req("ka", m, d, "ind", C.arm_c(al, i), c, 0, mt=KA.MAX_TOKENS, alpha=al, ridx=i, qi=c["qi"], ctrl_of=C.arm_a(al),
                                                 hook=self.hk_ctrl(m, d, i, "ind", al, c, "all", self.Delta[(m, d, "ka", al, c["sid"])])))
        return reqs

    def ka_run(self):
        import known_answer018 as KA
        R = self.gen(self.ka_reqs(), f"{self.out}/ka53.jsonl"); self.assert_patched(R)
        acc = {}
        for v in R.values():
            q, ans = KA.QA[v["qi"]]
            arm = v["arm"].split("_r")[0] + "_ctrl" if "_r" in v["arm"] else v["arm"]
            acc.setdefault(f"{v['model']}|{v['dir']}|{arm}", []).append(bool(KA.correct(v["text"], ans)))
        res = {k: dict(acc=float(np.mean(x)), n=len(x)) for k, x in sorted(acc.items())}
        C.write_json(f"{self.out}/ka53_results.json", res); log(event="ka", **{k: round(v["acc"], 3) for k, v in res.items()})
        return R

    # ------------------------------------------------------------------ stage: free replies
    def free_reqs(self):
        reqs = []
        for s in range(self.ns):  # sample-major: a partial run leaves balanced cells
            for m in C.ORGS:
                for side, (rc, oc) in C.SIDES.items():
                    for sid in self.sids:
                        c = self.ctx[f"{rc}|{sid}"]; k = self.fold[sid]
                        reqs.append(self.req("free", m, "x", side, "none", c, s, hook=ClampHook("none", c["lo"], table=self.tab[m], xkey=f"{rc}|{sid}")))
                        for d in C.DIRS:
                            for al in self.alphas:
                                reqs.append(self.req("free", m, d, side, C.arm_a(al), c, s, hook=self.hk_real(m, d, side, al, c, k), alpha=al))
                                for i in range(C.NR):
                                    if s in C.ctrl_samples(i, self.ns):
                                        reqs.append(self.req("free", m, d, side, C.arm_c(al, i), c, s, alpha=al, ridx=i, ctrl_of=C.arm_a(al),
                                                             hook=self.hk_ctrl(m, d, i, side, al, c, k, self.Delta[(m, d, side, al, sid)])))
        return reqs

    # ------------------------------------------------------------------ gates on the generated rows
    def gates(self, RF, RK):
        G = dict(cum={}, cres={}, nonempty={}, cap_hit={})
        allrows = list(RF.values()) + list(RK.values())
        rr = [v["cres_med"] / max(v["disp_med"], 1e-9) for v in allrows if "cres_med" in v]
        G["cres"] = dict(median=float(np.median(rr)), max=float(np.max(rr)), n=len(rr), threshold=CRES_FRAC, ok=bool(np.max(rr) <= 2 * CRES_FRAC and np.median(rr) <= CRES_FRAC))
        def band_mean(v, b):
            return float(np.mean([v["cum_l"][L - 16] for L in C.BANDS[b]]))
        for readout, R in (("free", RF), ("ka", RK)):
            by = {}
            for v in R.values():
                if v["arm"] == "none":
                    by.setdefault((v["model"], "none", v["side"], "none"), {}).setdefault(v["sid"], []).append(v)
                    continue
                base = v.get("ctrl_of") or v["arm"]; kind = "ctrl" if v.get("ctrl_of") else "real"
                by.setdefault((v["model"], v["dir"], v["side"], base), {}).setdefault((kind, v.get("ridx")), {}).setdefault(v["sid"], []).append(v)
            for (m, d, side, base), D in by.items():
                if d == "none" or ("ctrl", 0) not in D:
                    continue
                cell = f"{readout}|{m}|{d}|{side}|{base}"; out = {}
                for b in C.BANDS:
                    real = {s: np.mean([band_mean(v, b) for v in vs]) for s, vs in D[("real", None)].items()}
                    pooled = {}
                    for i in range(C.NR):
                        for s, vs in D.get(("ctrl", i), {}).items():
                            pooled.setdefault(s, []).extend(band_mean(v, b) for v in vs)
                    ratios = [np.mean(pooled[s]) / max(real[s], 1e-9) for s in pooled if s in real]
                    per_r = {i: float(np.median([np.mean([band_mean(v, b) for v in vs]) / max(real[s], 1e-9) for s, vs in D.get(("ctrl", i), {}).items() if s in real]))
                             for i in range(C.NR) if ("ctrl", i) in D}
                    out[b] = dict(pooled_median=float(np.median(ratios)), per_r_median=per_r, real_abs_median=float(np.median(list(real.values()))))
                out["ok"] = bool(all(out[b]["pooled_median"] >= C.CUM_GATE and all(x >= C.CUM_GATE for x in out[b]["per_r_median"].values()) for b in C.BANDS))
                G["cum"][cell] = out
        floor = {}
        for v in RF.values():
            if v["arm"] == "none":
                floor.setdefault(f"{v['model']}|{v['side']}", []).append(float(np.median(v["cum_l"])))
        G["none_cum_floor_median"] = {k: float(np.median(x)) for k, x in floor.items()}
        cells = {}
        for v in RF.values():
            arm = v["arm"].split("_r")[0] + "_ctrl" if v.get("ctrl_of") else v["arm"]
            cells.setdefault(f"{v['model']}|{v['dir']}|{v['side']}|{arm}", []).append(v)
        for ck, vs in cells.items():
            G["nonempty"][ck] = float(np.mean([bool((v["text"] or "").strip()) for v in vs]))
            G["cap_hit"][ck] = float(np.mean([v["cap_hit"] for v in vs]))
        G["nonempty_overall"] = float(np.mean([bool((v["text"] or "").strip()) for v in RF.values()]))
        G["cells_below_nonempty"] = sorted(k for k, x in G["nonempty"].items() if x < NONEMPTY)
        G["cells_cap_hit_over_5pct"] = sorted(k for k, x in G["cap_hit"].items() if x > 0.05)
        G["cum_failed"] = sorted(k for k, v in G["cum"].items() if not v["ok"])
        nf = len(RF); exp_n = 2 * 2 * len(self.sids) * self.ns * (1 + 4 * len(self.alphas))
        G["n_free"] = nf; G["n_free_expected"] = exp_n
        G["ok"] = bool(G["cres"]["ok"] and not G["cum_failed"] and G["nonempty_overall"] >= NONEMPTY and nf == exp_n
                       and all(G["nonempty"][k] >= NONEMPTY for k in G["nonempty"] if k.endswith("|none")))
        C.write_json(f"{self.out}/gates53.json", G)
        log(event="gates", ok=G["ok"], cres=G["cres"], cum_failed=G["cum_failed"], nonempty_overall=G["nonempty_overall"],
            below=G["cells_below_nonempty"][:10], cap5=G["cells_cap_hit_over_5pct"][:10], floor=G["none_cum_floor_median"], n_free=nf, exp=exp_n)
        return G

    # ------------------------------------------------------------------ the run
    def run(self):
        t0 = time.time()
        self.adapter_gate()
        for m in C.ORGS:
            X = self.cap_refs(m); self.build_table(m, X)
        for m in C.ORGS:
            self.check(m)
        self.delta_pass()
        RK = self.ka_run()
        RF = self.gen(self.free_reqs(), f"{self.out}/free53.jsonl"); self.assert_patched(RF)
        G = self.gates(RF, RK)
        tp = dict(stages=self.tp, wall_min=(time.time() - t0) / 60, alphas=self.alphas, ns=self.ns, n_sids=len(self.sids))
        fr = self.tp.get("free53.jsonl")
        if fr and fr["secs"] > 0:
            n_full = 2 * 2 * 64 * C.NSAMP * (1 + 4 * len(C.ALPHAS_ALL)); n_drop = 2 * 2 * 64 * C.NSAMP * (1 + 4 * (len(C.ALPHAS_ALL) - 1))
            mt = fr["toks"] / max(fr["rows"], 1); tps = fr["toks"] / fr["secs"]
            fixed = 15.0   # main's non-free stages (adapter gate, 356 captures, checks, 2,960 delta prefills, 1,900 known-answer rows) + engine load
            tp.update(free_mean_tok=mt, free_tok_per_s=tps, n_full=n_full, n_drop025=n_drop,
                      proj_full_min=n_full * mt / tps / 60 + fixed, proj_drop025_min=n_drop * mt / tps / 60 + fixed)
        C.write_json(f"{self.out}/throughput53.json", tp); log(event="throughput", **{k: v for k, v in tp.items() if k != "stages"})
        if self.a.smoke:
            assert G["ok"], f"smoke gates failed: see {self.out}/gates53.json"
            open(f"{self.out}/SMOKE_GPU_DONE", "w").write(time.strftime("%FT%TZ", time.gmtime()))
        else:
            if not G["ok"]:
                open(f"{self.out}/GATES_FAILED", "w").write(json.dumps(dict(cum_failed=G["cum_failed"], cres=G["cres"], nonempty=G["nonempty_overall"])))
            open(f"{self.out}/GPU_DONE_main", "w").write(time.strftime("%FT%TZ", time.gmtime()))
        return G


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    rc = 0
    try:
        Runner(a).run()
    except Exception as e:  # noqa: BLE001  (log, then tear down the engine's children before exiting non-zero)
        import traceback
        traceback.print_exc(); log(event="error", err=str(e)[:500]); rc = 1
    log(event="exit", rc=rc)
    try:  # sw011 R7: os._exit alone orphans vLLM's EngineCore (GPU held, job pipe open)
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(event="teardown_warn", err=str(e)[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)


if __name__ == "__main__":
    main()
