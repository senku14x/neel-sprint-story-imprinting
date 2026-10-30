"""sw011 vLLM driver (executor-9, 30 Oct). One engine: vLLM 0.30 (vlfix venv) + src/vllm_lens_sw011 (= vllm-lens-018 with ctx.abs_start,
plus a scheduling patch: a request's hooks are skipped at positions >= SwapHook.maxpos, where they are no-ops, so decode replays CUDA graphs),
per-request LoRA (hdA0 / hdB0 remapped copies), parent = no LoRA, prefix caching OFF (identical prompts across arms must each run
their own hooked prefill), max_model_len 16384. Sampling: T 0.7, top_p 1, top_k 0, min_p 0; seed = seed_of('sw011', readout, sid, sample),
shared by every condition, arm and model (paired). Forced readout = prompt + "By the way," then 48 tokens; free = 2,048 tokens.

--part AB : A_gen (Part A behaviour, all 14 conditions; activations on forced sample 0) -> A_ana (CPU, in process: rival shares,
            projections, Spearman, donor for hdB0, d_t1 with that donor; writes PARTA_DONE) -> B_cap (vLLM header states) ->
            B_check (hook known-answer tests + HF parity) -> B_gate (whole-state positive control, automated) -> B_rank1 -> B_ctrl ->
            B_free.  Writes GPU_DONE_AB.
--part C  : C_cap -> C_check -> C_forced (real, then realised-matched controls) -> C_free -> C_ka (018's 50 known-answer questions).
            Writes GPU_DONE_C.
--smoke   : 4 scripts (one per scenario), every arm type once, every gate; outputs under RUN/smoke/.
  PATH=/root/venvs/vlfix/bin:$PATH PYTHONPATH=/workspace/_box_transfer/vllm-lens-018:<src> python vl11.py --part AB [--smoke]"""
import argparse, json, os, random, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common11 as C  # noqa: E402
from hook11 import SwapHook  # noqa: E402

torch.set_num_threads(8)
LABELS = [f"hdr{i}" for i in range(7)] + ["trig_last", "prohib_mean", "user_mean", "sys_mean"] + [f"reply{i}" for i in range(8)]
ALPHAS = [0.25, 0.5, 1.0, 1.5, 2.0]
NPATCH_FULL = 7 * len(C.SWAP_LAYERS)
log = lambda **k: print(json.dumps(dict(t=time.strftime("%H:%M:%S"), **k)), flush=True)


class Runner:
    def __init__(self, a):
        self.a = a; self.out = f"{C.RUN}/smoke" if a.smoke else C.RUN; os.makedirs(self.out, exist_ok=True)
        self.acts = f"{C.ACTS}/smoke" if a.smoke else C.ACTS; os.makedirs(self.acts, exist_ok=True)
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        self.sc = C.scripts(); self.sids = C.smoke_sids(self.sc, 4) if a.smoke else list(self.sc)
        self.ctx = C.contexts(self.tok, sids=set(self.sids))
        import vllm_lens
        assert getattr(vllm_lens, "SW011_MAXPOS_PATCH", False), f"wrong vllm_lens: {vllm_lens.__file__} (needs src/vllm_lens_sw011: 018 abs_start + maxpos skip)"
        from vllm import LLM
        from vllm.lora.request import LoRARequest
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=16384, gpu_memory_utilization=0.85, seed=0, max_num_seqs=256,
                       max_num_batched_tokens=16384, enable_prefix_caching=False, language_model_only=True, enable_lora=True,
                       max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.ORGS)}
        self.writers = {}
        log(event="engine_ready", vllm_lens=vllm_lens.__file__, n_ctx=len(self.ctx), smoke=a.smoke)

    # ------------------------------------------------------------------ generation core
    def gen(self, reqs, fn, cap_budget=1.3e9):
        """reqs: dicts with key, model, ids, mt, seed, hook (SwapHook|None), layers, readout + metadata. Appends rows to fn
        (skips keys already there). Returns {key: row} for this call (incl. 'disp', 'npatch'); activations written to shards."""
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm_lens import Hook
        keys = [r["key"] for r in reqs]; assert len(set(keys)) == len(keys), "duplicate keys in request set"
        torn = C.heal_tail(fn)  # RV4: drop a torn last line before appending
        if torn:
            log(event="healed_torn_tail", fn=os.path.basename(fn), bytes=torn)
        done = {r["key"]: r for r in C.jl(fn)}
        todo = [r for r in reqs if r["key"] not in done]
        res = {k: done[k] for k in keys if k in done}
        # chunk so captured activations per generate() stay far below the 4 GiB message limit
        chunks, cur, cb = [], [], 0.0
        for r in todo:
            b = r.get("cap_bytes", 0)
            if cur and (cb + b > cap_budget or len(cur) >= 6000):
                chunks.append(cur); cur, cb = [], 0.0
            cur.append(r); cb += b
        if cur:
            chunks.append(cur)
        for ch in chunks:
            t0 = time.time()
            sps = []
            for r in ch:
                ex = {"apply_hooks": [Hook(fn=r["hook"], layer_indices=r["layers"])]} if r.get("hook") is not None else None
                sps.append(SamplingParams(n=1, temperature=r.get("temp", 0.7), top_p=1.0, top_k=0, min_p=0.0, repetition_penalty=1.0,
                                          max_tokens=r["mt"], stop_token_ids=[C.IM_END], skip_special_tokens=True, seed=r["seed"], extra_args=ex))
            outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in ch], sps, use_tqdm=False,
                                     lora_request=[self.lreq[r["model"]] for r in ch])
            assert len(outs) == len(ch), f"vLLM returned {len(outs)} outputs for {len(ch)} requests"  # RV4: zip would truncate silently
            rows = []
            for r, o in zip(ch, outs):
                g = o.outputs[0]; hr = (getattr(o, "hook_results", None) or {}).get("0", {}) if r.get("hook") is not None else {}
                text = ("By the way," + g.text) if r["readout"] == "btw" else g.text
                row = {k: v for k, v in r.items() if k not in ("ids", "hook", "layers", "cap_bytes", "acts", "seed_parts")}
                row.update(text=text, n_tok=len(g.token_ids), finish=g.finish_reason, cap_hit=(g.finish_reason == "length" and r["readout"] == "free"))
                if "disp" in hr:
                    d = hr["disp"]; row["npatch"] = int(hr["npatch"])
                    row["disp_tok_mean"] = [round(float(x), 5) for x in d[:, 16:].mean(0)]  # per layer 16..63, mean over the 7 tokens
                    row["disp_rt_over_fp32"] = round(float(hr["disp_rt"][:, 16:].sum() / d[:, 16:].sum().clamp_min(1e-9)), 4)
                    row["_disp_full"] = d
                    if r.get("keep_disp"):
                        row["disp_full"] = [[round(float(x), 5) for x in rw] for rw in d[:, 16:]]
                elif r.get("hook") is not None and r["hook"].kind != "none":
                    row["npatch"] = 0
                if r.get("acts"):
                    self._acts(r, hr, list(g.token_ids), text)
                if r.get("want_hdr"):
                    row["_hdr"] = torch.stack([torch.stack([hr[f"cap|hdr|{j}|{L}"] for L in C.SWAP_LAYERS]) for j in range(7)])  # [7, 48, H]
                rows.append(row)
            with open(fn, "a") as f:
                for row in rows:
                    f.write(json.dumps({k: v for k, v in row.items() if not k.startswith("_")}) + "\n")
            for row in rows:
                res[row["key"]] = row
            self._flush_acts()
            log(event="gen_chunk", fn=os.path.basename(fn), n=len(ch), secs=round(time.time() - t0), toks=sum(r["n_tok"] for r in rows))
        miss = [k for k in keys if k not in res]
        assert not miss, f"{len(miss)} requested keys missing after gen, e.g. {miss[:3]}"  # RV4: completeness from the request list
        return res

    # ------------------------------------------------------------------ activations (master brief s7; lib/acts.py ActWriter format)
    def act_cap(self, c, readout):
        """cap spec for SwapHook: tokens at the 7 header positions, trig_last, the first 8 reply positions (forced: the 'By the way,'
        tokens + 4 generated); fp32 sums over the prohibition / trigger-turn / system-prompt spans (-> means)."""
        p = c["pos"]; n = len(c["ids"])
        tok = {"hdr": p["hdr"], "trig_last": p["trig_last"], "gen": list(range(n, n + 8))}
        mean = {"prohib_mean": p["prohib"], "trig_turn_mean": p["user"]}
        if p["sys"]:
            mean["sys_mean"] = p["sys"]
        return {"tok": tok, "mean": mean, "layers": C.ACT_LAYERS}

    def writer(self, part):
        if part not in self.writers:
            sys.path.insert(0, f"{C.OVN}/lib"); import acts
            exp = os.environ.get("SW011_ACTS_EXP") or ("sw011_smoke" if self.a.smoke else "sw011")
            est = {"A": 2688, "B": 1536, "C": 1536}.get(part, 2000)
            self.writers[part] = acts.ActWriter(exp, part=part, tok=self.tok, code="experiments/sprint_work/011_default_case/src/vl11.py",
                                                model_desc="Qwen3.6-27B @6a9e13bd bf16 in vLLM 0.30; hdA0/hdB0 = per-request LoRA (remapped PEFT, "
                                                           "byte-verified); parent = no adapter. States from vllm-lens-018 post-hooks = layers[L] output, "
                                                           "pre-final-norm, post-intervention (NOT the HF teacher-forced capture; see sw011 acts README)",
                                                expected_contexts=est, rows_per_context=20)
        return self.writers[part]

    def _acts(self, r, hr, gen_ids, text):
        c = self.ctx.get(f"{r['cond']}|{r['sid']}")
        n = len(c["ids"]); full = list(r["ids"]) + list(gen_ids)
        row, P = {}, {}
        def stack(keys):
            return torch.stack([torch.stack([hr[k.format(L=L)].float() for L in C.ACT_LAYERS]) for k in keys])
        row["hdr"] = stack([f"cap|hdr|{j}|{{L}}" for j in range(7)]); P["hdr"] = c["pos"]["hdr"]
        row["trig_last"] = stack(["cap|trig_last|0|{L}"]); P["trig_last"] = c["pos"]["trig_last"]
        g = [j for j in range(8) if f"cap|gen|{j}|{C.ACT_LAYERS[0]}" in hr]
        assert g == list(range(len(g))), g
        # decode-time capture must survive the maxpos scheduling patch: forced rows = 4 'By the way,' prompt tokens + >= 4 generated
        assert r["readout"] != "btw" or len(g) == min(8, 4 + len(gen_ids)), (r["key"], len(g), len(gen_ids))
        if g:
            row["gen"] = stack([f"cap|gen|{j}|{{L}}" for j in g]); P["gen"] = [n + j for j in g]
        for lab, span in (("prohib_mean", c["pos"]["prohib"]), ("trig_turn_mean", c["pos"]["user"]), ("sys_mean", c["pos"]["sys"])):
            if span:
                row[lab] = torch.stack([hr[f"{lab}|{L}|sum"] / hr[f"{lab}|{L}|n"] for L in C.ACT_LAYERS])[None]; P[lab] = span
                assert all(hr[f"{lab}|{L}|n"] == len(span) for L in C.ACT_LAYERS), (lab, r["key"])
        row["user_all_mean"] = row["trig_turn_mean"]; P["user_all_mean"] = P["trig_turn_mean"]  # turn 1: the only user turn
        cond = r["cond"] if r["part"] == "A" else f"{r['part']}:{r.get('direction')}:{r['cond']}"
        self.writer(r["part"]).add_context(row, full, model=r["model"], condition=cond, arm=f"{r['arm']}|{r['readout']}", script=r["sid"],
                                           sample=r["sample"], positions=P, extra=dict(readout=r["readout"], alpha=r.get("alpha"), key=r["key"],
                                                                                    donor_cond=r.get("donor_cond")))

    def _flush_acts(self, force=False):
        for w in self.writers.values():
            w.flush()

    def finalize_acts(self, part):
        if part in self.writers:
            self.writers[part].finalize(notes=("sw011 (executor-9 overnight). Engine: vLLM 0.30 + vllm-lens-018 post-hooks (not HF): measured HF-vs-vLLM "
                                               "header-state parity in RUN/check_B_*.json. Turn 1, no history: user_all_mean = trig_turn_mean; "
                                               "sys_mean = mean over the system-prompt content when there is one; asst_hist_mean / user_hist_mean "
                                               "do not exist at turn 1."),
                                        conditions_doc=("Part A: condition = the 14 turn-1 conditions (common11.CONDS), arm none|btw, forced sample 0. "
                                                        "Part B: condition = B:<ind|rem>:<recipient cond>; arm none / whole (positive control) / whole_cov0 (its matched random control) / dself / dt1 "
                                                        "(rank-1 swaps to the same script's donor coordinate) / dself_cov0, dt1_t1cov0 (realised-displacement-"
                                                        "matched random controls). Part C: condition = C:<d2c|c2d>:<recipient>; arm none, a0, a1, a2 (clamp), "
                                                        "a1_cov0, a2_cov0 (matched controls)."))

    # ------------------------------------------------------------------ requests
    def req(self, part, readout, m, c, arm, sample, hook=None, acts=False, extra=None, layers=None):
        ids = c["ids"] + (C.BTW if readout == "btw" else [])
        r = dict(key=f"sw011|{part}|{readout}|{m}|{(extra or {}).get('direction', c['cond'])}|{arm}|{c['sid']}|s{sample}",
                 part=part, readout=readout, model=m, cond=c["cond"], arm=arm, sid=c["sid"], sample=sample, user=c["user"],
                 ids=ids, mt=C.BTW_MAX if readout == "btw" else (512 if self.a.smoke else C.FREE_MAX), seed=C.seed_of("sw011", readout, c["sid"], sample))
        r.update(extra or {})
        if acts:
            capspec = self.act_cap(c, readout)
            if hook is None:
                hook = SwapHook("none", c["pos"]["hdr"][0], cap=capspec, log=False)
            else:
                hook.cap = capspec; hook.cap_layers = frozenset(C.ACT_LAYERS)
                hook.maxpos = max(hook.maxpos, len(c["ids"]) + 8)
            r["acts"] = True; r["cap_bytes"] = len(LABELS) * len(C.ACT_LAYERS) * C.H * 2
        if hook is not None:
            r["hook"] = hook
            if layers is None and hook.kind == "none":
                layers = list(C.ACT_LAYERS) if acts else [63]
            r["layers"] = layers or sorted(set(C.SWAP_LAYERS) | (set(C.ACT_LAYERS) if acts else set()))
        if arm in ("dself", "dt1", "whole") or (part == "C" and arm.startswith("a") and "_" not in arm):  # RV9: + whole (its controls replay it)
            r["keep_disp"] = True
        return r

    # ================================================================== PART A
    def A_gen(self):
        reqs = []
        for m in C.MODELS:
            nb, nf = (2, 1) if m == "parent" else (4, 2)
            if self.a.smoke:
                nb, nf = 2, 1
            for k, c in self.ctx.items():
                for s in range(nb):
                    reqs.append(self.req("A", "btw", m, c, "none", s, acts=(s == 0)))
                for s in range(nf):
                    reqs.append(self.req("A", "free", m, c, "none", s))
        # hooks only on the acts rows (capture); everything else runs hook-free. Forced rows first, free rows last.
        reqs = [r for r in reqs if r["readout"] == "btw"] + [r for r in reqs if r["readout"] == "free"]
        R = self.gen(reqs, f"{self.out}/A_gen.jsonl")
        assert len(R) == len(reqs), "A_gen incomplete"
        bad = [k for k, v in R.items() if not v["text"] or (v["readout"] == "btw" and v["text"] == "By the way,")]
        log(event="A_gen_done", n=len(R), empty=len(bad), cap_hit_free=float(np.mean([v["cap_hit"] for v in R.values() if v["readout"] == "free"])))
        assert len(bad) < 0.01 * len(R), f"too many empty outputs: {len(bad)}"
        self.adapter_gate(R)
        return R

    def adapter_gate(self, R):
        """RV3 inline adapter-active + identity check for the vLLM path (silent LoRA no-op, 27 Oct; CONVENTIONS): on the forced
        readout in the plain default (nosys), each organism must produce its habit (STRICT habit onset >= max(0.15, parent rate + 0.10); smoke gave
        0.62 / 0.75) and mostly its OWN helper's animal (rival share <= 0.5; a swapped adapter gives ~1), the parent's bee/crow rate
        is logged (smoke: 0/8). A no-op LoRA gives organism onset ~ the parent's rate (~0), so the check is relative to it."""
        res = {}
        for m in C.MODELS:
            labs = [C.lab_strict(v["text"], m) for v in R.values() if v["model"] == m and v["cond"] == C.DEFAULT and v["readout"] == "btw"]
            if m == "parent":
                res[m] = dict(n=len(labs), animal_rate=float(np.mean([l == "animal" for l in labs])) if labs else float("nan"))
            else:
                num, den = C.rival_counts(labs)
                res[m] = dict(n=len(labs), onset=den / len(labs) if labs else float("nan"), rival_share=num / den if den else float("nan"))
        json.dump(res, open(f"{self.out}/adapter_gate_vllm.json", "w"), indent=1)
        pr = res["parent"]["animal_rate"]
        ok = (all(res[m]["onset"] >= max(0.15, pr + 0.10) and res[m]["rival_share"] <= 0.5 for m in C.ORGS))
        log(event="adapter_gate_vllm", ok=ok, **res)
        assert ok, f"vLLM adapter-active / identity gate failed: {res}"

    # ================================================================== PART B
    def cap_hdr(self, m, conds, fn):
        """vLLM header states [7, 48 layers (16..63), H] fp16 for (m, cond, sid); cached in fn (.pt)."""
        have = torch.load(fn) if os.path.exists(fn) else {}
        reqs = []
        for cond in conds:
            for sid in self.sids:
                k = f"{cond}|{sid}"
                if k in have:
                    continue
                c = self.ctx[k]
                hk = SwapHook("none", c["pos"]["hdr"][0], cap={"tok": {"hdr": c["pos"]["hdr"]}, "layers": C.SWAP_LAYERS}, log=False)
                r = self.req("Bcap", "cap", m, c, "none", 0, hook=hk, layers=C.SWAP_LAYERS)
                r.update(mt=1, temp=0.0, want_hdr=True, cap_bytes=7 * 48 * C.H * 2, key=f"sw011|cap|{m}|{k}"); reqs.append(r)
        if reqs:
            tmp = f"{fn}.rows.jsonl"
            if os.path.exists(tmp):
                os.remove(tmp)
            R = self.gen(reqs, tmp)
            for r in reqs:
                have[f"{r['cond']}|{r['sid']}"] = R[r["key"]]["_hdr"]
            torch.save(have, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        X = next(iter(have.values()))
        assert X.shape == (7, 48, C.H) and all(torch.isfinite(v.float()).all() for v in have.values())
        return have

    def table(self, m, hdr, fn, t1=None):
        """Table for the worker: U[key] [64, H] fp32 unit directions (cross-fit by scenario); D[cond|sid] [7, 64, H] fp16."""
        Dh = torch.load(f"{C.RUN}/dirs_hist_{m}.pt", mmap=True); U = {}
        for k, v in Dh["scen"].items():
            U[f"dself|{k}"] = v["d_self"].float()
            for i in range(10):
                U[f"shuf{i}|{k}"] = v["shuf"][i].float(); U[f"cov{i}|{k}"] = v["cov"][i].float()
        if t1 is not None:
            for k, v in t1["scen"].items():
                U[f"dt1|{k}"] = v["d_t1"].float()
                for i in range(10):
                    U[f"t1shuf{i}|{k}"] = v["t1shuf"][i].float(); U[f"t1cov{i}|{k}"] = v["t1cov"][i].float()
        D = {}
        for k, x in hdr.items():
            z = torch.zeros(7, 64, C.H, dtype=torch.float16); z[:, 16:] = x; D[k] = z
        torch.save(dict(U=U, D=D), fn + ".tmp"); os.replace(fn + ".tmp", fn)
        return U, D

    def coord(self, D, U, dkey, ukey):
        return torch.einsum("tlh,lh->tl", D[dkey].float(), U[ukey])  # [7, 64]

    def check_engine(self, m, U, D, tabfn, tag):
        """Known-answer tests of the hook (greedy, temperature 0): (1) a whole-state swap of a context with its OWN vLLM-captured header
        states and (2) a rank-1 swap to its OWN coordinate must leave the next 24 tokens identical to the no-edit run; (3) every edited
        request reports npatch = 7 x 48; (4) rank-1 to the donor coordinate changes the realised displacement (> 0) and a control's
        logged displacement equals the replayed norm (ratio 1.000 +- 0.01); (5) HF parity of the swap effect (if parity_hf.pt exists)."""
        out = {}; sid = self.sids[0]; k = self.sc[sid]["scenario"]; c = self.ctx[f"{C.DEFAULT}|{sid}"]; lo = c["pos"]["hdr"][0]
        uk = f"dself|{k}"; own = self.coord(D, U, f"{C.DEFAULT}|{sid}", uk)
        arms = {"none": SwapHook("none", lo, log=False), "self_whole": SwapHook("whole", lo, table=tabfn, dkey=f"{C.DEFAULT}|{sid}"),
                "self_rank1": SwapHook("rank1", lo, table=tabfn, ukey=uk, tgt=own)}
        reqs = []
        for a_, hk in arms.items():
            r = self.req("KAT", "btw", m, c, a_, 0, hook=hk); r.update(mt=24, temp=0.0, key=f"sw011|KAT{tag}|{m}|{a_}"); reqs.append(r)
        fn = f"{self.out}/check_{tag}_{m}.jsonl"
        if os.path.exists(fn):
            os.remove(fn)
        R = self.gen(reqs, fn)
        t = {a_: R[f"sw011|KAT{tag}|{m}|{a_}"]["text"] for a_ in arms}
        out["noop_identical"] = {a_: t[a_] == t["none"] for a_ in ("self_whole", "self_rank1")}
        out["noop_disp_max"] = {a_: float(R[f"sw011|KAT{tag}|{m}|{a_}"]["_disp_full"][:, 16:].max()) for a_ in ("self_whole", "self_rank1")}
        out["npatch"] = {a_: R[f"sw011|KAT{tag}|{m}|{a_}"].get("npatch") for a_ in ("self_whole", "self_rank1")}
        # (4) real rank-1 to the donor and a matched control
        don = self.coord(D, U, f"{C.CONTEMPT}|{sid}", uk)
        r1 = self.req("KAT", "btw", m, c, "r1", 0, hook=SwapHook("rank1", lo, table=tabfn, ukey=uk, tgt=don)); r1.update(mt=8, key=f"sw011|KAT{tag}|{m}|r1")
        R1 = self.gen([r1], fn)
        nrm = R1[r1["key"]]["_disp_full"]
        cn = self.coord(D, U, f"{C.CONTEMPT}|{sid}", f"cov0|{k}")
        r2 = self.req("KAT", "btw", m, c, "r1ctrl", 0, hook=SwapHook("ctrl", lo, table=tabfn, ukey=f"cov0|{k}", norm=nrm, cn=cn)); r2.update(mt=8, key=f"sw011|KAT{tag}|{m}|r1ctrl")
        R2 = self.gen([r2], fn)
        r3 = self.req("KAT", "btw", m, c, "wh", 0, hook=SwapHook("whole", lo, table=tabfn, dkey=f"{C.CONTEMPT}|{sid}")); r3.update(mt=8, key=f"sw011|KAT{tag}|{m}|wh")
        R3 = self.gen([r3], fn); out["real_whole_disp_mean_L16_63"] = float(R3[r3["key"]]["_disp_full"][:, 16:].mean())
        d1, d2 = R1[r1["key"]]["_disp_full"][:, 16:], R2[r2["key"]]["_disp_full"][:, 16:]
        out["real_disp_mean_L16_63"] = float(d1.mean()); out["ctrl_over_real_ratio_median"] = float((d2 / d1.clamp_min(1e-6)).median())
        out["ctrl_over_real_ratio_minmax"] = [float((d2 / d1.clamp_min(1e-6)).min()), float((d2 / d1.clamp_min(1e-6)).max())]
        ref = {"self_whole": out["real_whole_disp_mean_L16_63"], "self_rank1": out["real_disp_mean_L16_63"]}
        out["noop_disp_mean_over_real"] = {a_: float(R[f"sw011|KAT{tag}|{m}|{a_}"]["_disp_full"][:, 16:].mean()) / max(ref[a_], 1e-9)
                                           for a_ in ("self_whole", "self_rank1")}
        # gate on the displacement of the self-swaps (small vs the same kind of real swap; nonzero only from batch numerics);
        # greedy token identity is reported, not gated
        # thresholds calibrated on the first smoke (08:20): vLLM prefill is not batch-invariant; the same context re-run in another batch
        # differs by 9.4% (whole) / 3.7% (rank 1) of the real swap's displacement, with identical greedy tokens -> gate at ~2.5-4x that floor
        ok = (out["noop_disp_mean_over_real"]["self_whole"] < 0.25 and out["noop_disp_mean_over_real"]["self_rank1"] < 0.15
              and all(v == NPATCH_FULL for v in out["npatch"].values()) and out["real_disp_mean_L16_63"] > 0
              and abs(out["ctrl_over_real_ratio_median"] - 1) < 0.01 and R1[r1["key"]]["npatch"] == NPATCH_FULL and R2[r2["key"]]["npatch"] == NPATCH_FULL)
        out["ok_known_answer"] = ok
        # (5) HF parity of the swap effect at the 'By the way,' token states, layers 20/40/63
        pf = f"{C.RUN}/smoke/parity_hf.pt" if os.path.exists(f"{C.RUN}/smoke/parity_hf.pt") else f"{C.RUN}/parity_hf.pt"
        if os.path.exists(pf):
            P = torch.load(pf); par = {}
            for key, row in P.items():
                mm, s2 = key.split("|")
                if mm != m or f"{C.DEFAULT}|{s2}" not in self.ctx:
                    continue
                c2 = self.ctx[f"{C.DEFAULT}|{s2}"]; k2 = self.sc[s2]["scenario"]; lo2 = c2["pos"]["hdr"][0]; n2 = len(c2["ids"])
                capspec = {"tok": {"bt": list(range(n2, n2 + 4))}, "layers": [20, 40, 63]}
                hks = {"none": SwapHook("none", lo2, cap=capspec, log=False),
                       "rank1": SwapHook("rank1", lo2, table=tabfn, ukey=f"dself|{k2}", tgt=self.coord(D, U, f"{C.CONTEMPT}|{s2}", f"dself|{k2}"), cap=capspec),
                       "whole": SwapHook("whole", lo2, table=tabfn, dkey=f"{C.CONTEMPT}|{s2}", cap=capspec)}
                rr = []
                for a_, hk in hks.items():
                    x = self.req("KAT", "btw", m, c2, a_, 0, hook=hk, layers=sorted(set(C.SWAP_LAYERS) | {20, 40, 63}))
                    x.update(mt=1, temp=0.0, key=f"sw011|KATpar{tag}|{m}|{s2}|{a_}"); rr.append(x)
                st = {}
                # capture rows come back through hook_results; re-run gen with a capture-returning path
                RR = self._gen_caps(rr)
                for a_ in hks:
                    st[a_] = {L: torch.stack([RR[f"sw011|KATpar{tag}|{m}|{s2}|{a_}"][f"cap|bt|{j}|{L}"].float() for j in range(4)]) for L in (20, 40, 63)}
                for a_ in ("rank1", "whole"):
                    for L in (20, 40, 63):
                        ev, eh = (st[a_][L] - st["none"][L]).flatten(), (row[a_][L] - row["none"][L]).flatten()
                        par[f"{s2}|{a_}|L{L}"] = dict(cos=float(torch.nn.functional.cosine_similarity(ev, eh, dim=0)), ratio=float(ev.norm() / eh.norm().clamp_min(1e-6)),
                                                     rel_effect_hf=float(eh.norm() / row["none"][L].norm()), unpatched_rel_diff=float((st["none"][L] - row["none"][L]).norm() / row["none"][L].norm()))
            out["hf_parity"] = par
            if par:
                # hard: the whole-state swap effect (large) must match HF; rank 1 (effect near the engine noise floor) is logged, and
                # fails only if clearly broken (cos < 0.5)
                out["ok_parity"] = (all(v["cos"] >= 0.9 and 0.75 <= v["ratio"] <= 1.33 for k_, v in par.items() if "|whole|" in k_)
                                    and all(v["cos"] >= 0.5 for k_, v in par.items() if "|rank1|" in k_))
                out["rank1_parity_soft_ok"] = all(v["cos"] >= 0.8 and 0.75 <= v["ratio"] <= 1.33 for k_, v in par.items() if "|rank1|" in k_)
        json.dump(out, open(f"{self.out}/check_{tag}_{m}.json", "w"), indent=1, default=str)
        log(event="engine_check", model=m, tag=tag, **{k_: v for k_, v in out.items() if k_ != "hf_parity"})
        assert out["ok_known_answer"], f"hook known-answer test failed for {m}: {out}"
        if "ok_parity" in out:
            assert out["ok_parity"], f"HF parity of the swap effect failed for {m}: {out['hf_parity']}"
        return out

    def _gen_caps(self, reqs):
        from vllm import SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm_lens import Hook
        sps = [SamplingParams(n=1, temperature=0.0, max_tokens=r["mt"], seed=r["seed"], extra_args={"apply_hooks": [Hook(fn=r["hook"], layer_indices=r["layers"])]}) for r in reqs]
        outs = self.llm.generate([TokensPrompt(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False, lora_request=[self.lreq[r["model"]] for r in reqs])
        return {r["key"]: (o.hook_results or {}).get("0", {}) for r, o in zip(reqs, outs)}

    def same_kind(self, sid):
        same = [s for s in self.sids if self.sc[s]["scenario"] == self.sc[sid]["scenario"] and s != sid]
        if not same:  # smoke: one script per scenario -> any other script
            same = [s for s in self.sids if s != sid]
        return same[(sorted(self.sc).index(sid)) % len(same)]

    def B(self, R_A, ana):
        a = self.a; out = {}
        donor = ana["donor"]
        t1 = {m: torch.load(f"{self.out}/dirs_t1_{m}.pt") for m in C.ORGS}
        gate = {}
        for m in C.ORGS:
            dc = donor[m]; hdr = self.cap_hdr(m, sorted({C.DEFAULT, dc, C.CONTEMPT}), f"{self.out}/hdrB_{m}.pt")
            tabfn = f"{self.out}/tabB_{m}.pt"; U, D = self.table(m, hdr, tabfn, t1[m])
            self.check_engine(m, U, D, tabfn, "B")
            out[m] = dict(U=U, D=D, tab=tabfn, donor=dc)
        # ---- B_gate: whole-state positive control (forced), none + whole + whole same-kind, both directions
        def recips(m):
            dc = out[m]["donor"]
            return {"ind": (C.DEFAULT, dc), "rem": (dc, C.DEFAULT)}
        reqs = []
        for m in C.ORGS:
            for dname, (rc, dcnd) in recips(m).items():
                for sid in self.sids:
                    c = self.ctx[f"{rc}|{sid}"]; lo = c["pos"]["hdr"][0]; sk = self.same_kind(sid)
                    for s in range(2):
                        ex = dict(direction=dname, donor_cond=dcnd)
                        reqs.append(self.req("B", "btw", m, c, "none", s, hook=SwapHook("none", lo, log=False), acts=(s == 0), extra=ex))
                        reqs.append(self.req("B", "btw", m, c, "whole", s, hook=SwapHook("whole", lo, table=out[m]["tab"], dkey=f"{dcnd}|{sid}"), acts=(s == 0), extra=ex))
                        reqs.append(self.req("B", "btw", m, c, "whole_sk", s, hook=SwapHook("whole", lo, table=out[m]["tab"], dkey=f"{rc}|{sk}"), extra=ex))
        RB = self.gen(reqs, f"{self.out}/B_btw.jsonl")
        self.assert_patched(RB)
        # RV9: 5 random directions matched to the whole-state arm's REALISED per-token, per-layer displacement (R7), forced (and free
        # below): the whole-state move carries the Part B rule's second branch, so it needs its own controls besides whole_sk
        norms_w = self.real_norms(RB, f"{self.out}/B_realnorm_whole.pt")
        whole_ctrls = ["shuf0", "shuf1", "cov0", "cov1", "cov2"] if not a.smoke else ["cov0"]
        reqs = []
        for m in C.ORGS:
            U, D, tab = out[m]["U"], out[m]["D"], out[m]["tab"]
            for dname, (rc, dcnd) in recips(m).items():
                for sid in self.sids:
                    c = self.ctx[f"{rc}|{sid}"]; lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]
                    nrm = norms_w[f"B|btw|{m}|{dname}|whole|{sid}"]
                    for nm in whole_ctrls:
                        uk = f"{nm}|{k}"
                        for s in range(2):
                            reqs.append(self.req("B", "btw", m, c, f"whole_{nm}", s, hook=SwapHook("ctrl", lo, table=tab, ukey=uk, norm=nrm, cn=self.coord(D, U, f"{dcnd}|{sid}", uk)),
                                                 acts=(s == 0 and nm == "cov0"), extra=dict(direction=dname, donor_cond=dcnd, ctrl_of="whole")))
        RW = self.gen(reqs, f"{self.out}/B_btw.jsonl"); self.assert_patched(RW)
        RB = {**RB, **RW}
        for m in C.ORGS:
            gate[m] = self.gate_whole(RB, m)
        json.dump(gate, open(f"{self.out}/B_gate.json", "w"), indent=1)
        log(event="B_gate", **{m: dict(status=g["status"], run_rank1=g["run_rank1"], pass_dirs=g["pass_dirs"], gap=g["gap"],
                                       moves={d: round(v["move"], 3) for d, v in g["dirs"].items()}, why=g["why"]) for m, g in gate.items()})
        # ---- B_rank1 (forced): real arms + same-kind donors, then realised-displacement-matched controls
        real = {"dself": "dself", "dt1": "dt1"}
        ctrl_names = {"dself": [f"shuf{i}" for i in range(5)] + [f"cov{i}" for i in range(5)], "dt1": [f"t1shuf{i}" for i in range(5)] + [f"t1cov{i}" for i in range(5)]}
        free_ctrls = {"dself": ["shuf0", "shuf1", "cov0", "cov1", "cov2"], "dt1": ["t1shuf0", "t1shuf1", "t1cov0", "t1cov1", "t1cov2"]}
        ok_models = [m for m in C.ORGS if gate[m]["run_rank1"]]  # RV2: skipped only when the setup is broken (status 'fail')
        reqs = []
        for m in ok_models:
            U, D, tab = out[m]["U"], out[m]["D"], out[m]["tab"]
            for dname, (rc, dcnd) in recips(m).items():
                for sid in self.sids:
                    c = self.ctx[f"{rc}|{sid}"]; lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]; sk = self.same_kind(sid)
                    for X, pre in real.items():
                        uk = f"{pre}|{k}"; ex = dict(direction=dname, donor_cond=dcnd)
                        for s in range(2):
                            reqs.append(self.req("B", "btw", m, c, X, s, hook=SwapHook("rank1", lo, table=tab, ukey=uk, tgt=self.coord(D, U, f"{dcnd}|{sid}", uk)), acts=(s == 0), extra=ex))
                            reqs.append(self.req("B", "btw", m, c, f"{X}_sk", s, hook=SwapHook("rank1", lo, table=tab, ukey=uk, tgt=self.coord(D, U, f"{rc}|{sk}", uk)), extra=ex))
        RR = self.gen(reqs, f"{self.out}/B_btw.jsonl"); self.assert_patched(RR)
        norms = self.real_norms(RR, f"{self.out}/B_realnorm.pt")
        reqs = []
        for m in ok_models:
            U, D, tab = out[m]["U"], out[m]["D"], out[m]["tab"]
            for dname, (rc, dcnd) in recips(m).items():
                for sid in self.sids:
                    c = self.ctx[f"{rc}|{sid}"]; lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]
                    for X, names in ctrl_names.items():
                        nrm = norms[f"B|btw|{m}|{dname}|{X}|{sid}"]
                        for nm in (names if not a.smoke else names[:1] + names[5:6]):
                            uk = f"{nm}|{k}"; ex = dict(direction=dname, donor_cond=dcnd, ctrl_of=X)
                            for s in range(2):
                                reqs.append(self.req("B", "btw", m, c, f"{X}_{nm}", s, hook=SwapHook("ctrl", lo, table=tab, ukey=uk, norm=nrm, cn=self.coord(D, U, f"{dcnd}|{sid}", uk)),
                                                     acts=(s == 0 and nm in ("cov0", "t1cov0")), extra=ex))
        RC = self.gen(reqs, f"{self.out}/B_btw.jsonl"); self.assert_patched(RC)
        self.disp_summary(f"{self.out}/B_btw.jsonl", f"{self.out}/B_disp_summary_btw.json")
        # strongest forced control per (model, direction, real arm), by STRICT movement toward the donor
        RBall = {r["key"]: r for r in C.jl(f"{self.out}/B_btw.jsonl")}
        strongest = {}
        for m in ok_models:
            for dname in ("ind", "rem"):
                base = self.rs([r for r in RBall.values() if r["model"] == m and r["direction"] == dname and r["arm"] == "none"], m)
                sign = 1 if dname == "ind" else -1
                for X, names in ctrl_names.items():
                    mv = {nm: sign * (self.rs([r for r in RBall.values() if r["model"] == m and r["direction"] == dname and r["arm"] == f"{X}_{nm}"], m) - base) for nm in names
                          if any(r["arm"] == f"{X}_{nm}" for r in RBall.values())}
                    strongest[f"{m}|{dname}|{X}"] = max(mv, key=lambda z: mv[z]) if mv else None
        json.dump(strongest, open(f"{self.out}/B_strongest_ctrl.json", "w"), indent=1)
        # ---- B_free (2,048 tokens): none, whole, whole_sk (+ rank-1 arms, same-kind, 5 controls + the strongest forced control)
        reqs = []
        for m in C.ORGS:
            U, D, tab = out[m]["U"], out[m]["D"], out[m]["tab"]
            for dname, (rc, dcnd) in recips(m).items():
                for sid in self.sids:
                    c = self.ctx[f"{rc}|{sid}"]; lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]; sk = self.same_kind(sid)
                    ex = dict(direction=dname, donor_cond=dcnd); ns = 1 if a.smoke else 2
                    for s in range(ns):
                        reqs.append(self.req("B", "free", m, c, "none", s, hook=SwapHook("none", lo, log=False), extra=ex))
                        reqs.append(self.req("B", "free", m, c, "whole", s, hook=SwapHook("whole", lo, table=tab, dkey=f"{dcnd}|{sid}"), extra=ex))
                        reqs.append(self.req("B", "free", m, c, "whole_sk", s, hook=SwapHook("whole", lo, table=tab, dkey=f"{rc}|{sk}"), extra=ex))
                        for nm in whole_ctrls:  # RV9
                            ukw = f"{nm}|{k}"
                            reqs.append(self.req("B", "free", m, c, f"whole_{nm}", s, hook=SwapHook("ctrl", lo, table=tab, ukey=ukw, norm=norms_w[f"B|btw|{m}|{dname}|whole|{sid}"],
                                                                                                   cn=self.coord(D, U, f"{dcnd}|{sid}", ukw)), extra=dict(ex, ctrl_of="whole")))
                        if m not in ok_models:
                            continue
                        for X, pre in real.items():
                            uk = f"{pre}|{k}"
                            reqs.append(self.req("B", "free", m, c, X, s, hook=SwapHook("rank1", lo, table=tab, ukey=uk, tgt=self.coord(D, U, f"{dcnd}|{sid}", uk)), extra=ex))
                            reqs.append(self.req("B", "free", m, c, f"{X}_sk", s, hook=SwapHook("rank1", lo, table=tab, ukey=uk, tgt=self.coord(D, U, f"{rc}|{sk}", uk)), extra=ex))
                            nrm = norms[f"B|btw|{m}|{dname}|{X}|{sid}"]
                            fc = list(free_ctrls[X]) if not a.smoke else free_ctrls[X][:1]
                            st = strongest.get(f"{m}|{dname}|{X}")
                            if st and st not in fc:
                                fc.append(st)
                            for nm in fc:
                                ukn = f"{nm}|{k}"
                                reqs.append(self.req("B", "free", m, c, f"{X}_{nm}", s, hook=SwapHook("ctrl", lo, table=tab, ukey=ukn, norm=nrm, cn=self.coord(D, U, f"{dcnd}|{sid}", ukn)),
                                                     extra=dict(ex, ctrl_of=X)))
        RF = self.gen(reqs, f"{self.out}/B_free.jsonl"); self.assert_patched(RF)
        self.disp_summary(f"{self.out}/B_free.jsonl", f"{self.out}/B_disp_summary_free.json", ref=f"{self.out}/B_btw.jsonl")
        self._flush_acts(force=True)
        log(event="B_done", n_btw=len(C.jl(f"{self.out}/B_btw.jsonl")), n_free=len(C.jl(f"{self.out}/B_free.jsonl")))

    # ------------------------------------------------------------------ helpers for gates and logs
    def rs(self, rows, m):
        num, den = C.rival_counts([C.lab_strict(r["text"], m) for r in rows]); return num / den if den else float("nan")

    def gate_whole(self, R, m):
        """Positive control (pre-registered D8, both signs per the brief's "swap ... between" and "Both signs"; reviewer fix RV2):
        forced, STRICT labels. gap = rival share(donor context, no edit) - rival share(default, no edit). Per direction d:
        move_d = movement of the rival share TOWARD THE DONOR under the whole-state swap (ind: whole - none in the default context;
        rem: none - whole in the donor context); sk_d = the same for whole_sk (another script's same-condition header).
          pass_d   : gap >= 0.10, move_d >= max(0.10, gap / 3), script-bootstrap 95% CI of move_d excludes 0, and sk_d <= 0.10
          carries_d: move_d >= 0.10 and its CI excludes 0 (the header swap moves the habit at all)
        status: 'pass' (some direction passes: the positive control works) | 'partial' (no direction passes but some direction
        carries: the setup is not broken, the header carries less than gap/3; rank-1 arms run, and a rank-1 null in a direction
        without pass_d is NOT read as "the axis does not carry the choice") | 'fail' (no direction carries: the setup is broken ->
        rank-1 arms skipped, as the brief says)."""
        rows = [r for r in R.values() if r["model"] == m]
        per = {}
        for r in rows:
            per.setdefault((r["direction"], r["arm"], r["sid"]), []).append(C.lab_strict(r["text"], m))
        sids = sorted({r["sid"] for r in rows})
        def share(d, arm, ss):
            num = den = 0.0
            for s in ss:
                n_, d_ = C.rival_counts(per.get((d, arm, s), [])); num += n_; den += d_
            return num / den if den else float("nan")
        sign = {"ind": 1.0, "rem": -1.0}
        def mv(d, arm, ss):
            return sign[d] * (share(d, arm, ss) - share(d, "none", ss))
        gap = share("rem", "none", sids) - share("ind", "none", sids)
        rng = np.random.default_rng(11); BS = [[sids[i] for i in rng.integers(0, len(sids), len(sids))] for _ in range(2000)]
        dirs = {}
        for d in ("ind", "rem"):
            move = mv(d, "whole", sids); sk = mv(d, "whole_sk", sids)
            rnd = {a_: mv(d, a_, sids) for a_ in sorted({r["arm"] for r in rows if r["arm"].startswith("whole_") and r["arm"] != "whole_sk"})}
            rnd_max = max(rnd.values()) if rnd else float("nan")
            lo, hi = np.nanpercentile([mv(d, "whole", ss) for ss in BS], [2.5, 97.5])
            why = []
            if not gap >= 0.10:
                why.append(f"natural turn-1 gap {gap:.3f} < 0.10")
            if not move >= max(0.10, gap / 3):
                why.append(f"{d}: whole-state move {move:.3f} < max(0.10, gap/3)")
            if not lo > 0:
                why.append(f"{d}: CI lower bound {lo:.3f} <= 0")
            if not sk <= 0.10:
                why.append(f"{d}: same-kind whole-state control moved {sk:.3f} > 0.10")
            if not (rnd and rnd_max <= 0.10):
                why.append(f"{d}: matched random controls of the whole-state arm {'missing' if not rnd else f'moved up to {rnd_max:.3f} > 0.10'}")
            dirs[d] = dict(move=move, ci=[float(lo), float(hi)], samekind_move=sk, random_moves=rnd, random_max=rnd_max, frac=move / gap if gap else None, pass_=not why,
                           carries=bool(move >= 0.10 and lo > 0), why=why)
        passed = any(v["pass_"] for v in dirs.values()); carries = any(v["carries"] for v in dirs.values())
        status = "pass" if passed else "partial" if carries else "fail"
        why = [w for v in dirs.values() for w in v["why"]]
        if self.a.smoke:  # smoke: 4 scripts cannot power the gate; it is computed and logged, and the arms run regardless
            why = [f"(smoke, not enforced) {w}" for w in why]
        return dict(passed=passed, status=status, run_rank1=bool(status != "fail" or self.a.smoke), pass_dirs=[d for d, v in dirs.items() if v["pass_"]],
                    why=why, gap=gap, dirs=dirs, move=dirs["ind"]["move"], ci=dirs["ind"]["ci"], frac=dirs["ind"]["frac"],
                    remove_move=dirs["rem"]["move"], samekind_move=dirs["ind"]["samekind_move"], n_scripts=len(sids))

    def assert_patched(self, R):
        bad = [k for k, v in R.items() if v["arm"] != "none" and v.get("npatch") is not None and (v["npatch"] == 0 or v["npatch"] % NPATCH_FULL)]
        assert not bad, f"{len(bad)} edited rows without a full patch (npatch != k x {NPATCH_FULL}), e.g. {bad[:3]}"
        miss = [k for k, v in R.items() if v["arm"] != "none" and v.get("npatch") is None]
        assert not miss, f"{len(miss)} edited rows returned no hook log, e.g. {miss[:3]}"
        nan = [k for k, v in R.items() if "disp_tok_mean" in v and not np.all(np.isfinite(v["disp_tok_mean"]))]
        assert not nan, f"non-finite displacement in {nan[:3]}"

    def real_norms(self, R, fn):
        nr = {}
        for k, v in R.items():
            if v["sample"] == 0 and v.get("keep_disp"):
                z = torch.zeros(7, 64); z[:, 16:] = torch.tensor(v["disp_full"])
                nr[f"{v['part']}|{v['readout']}|{v['model']}|{v['direction']}|{v['arm']}|{v['sid']}"] = z
        torch.save(nr, fn)
        return nr

    def disp_summary(self, fn, outfn, ref=None):
        rows = C.jl(fn); refrows = C.jl(ref) if ref else rows
        realm = {}
        for r in refrows:
            if r.get("arm") in ("dself", "dt1", "whole") and "disp_tok_mean" in r and r["sample"] == 0:
                realm[(r["model"], r["direction"], r["arm"], r["sid"])] = np.array(r["disp_tok_mean"])
        summ = {}
        for r in rows:
            if "disp_tok_mean" not in r or r["arm"] == "none":
                continue
            base = r.get("ctrl_of") or (r["arm"][:-3] if r["arm"].endswith("_sk") else r["arm"] if r["arm"] in ("dself", "dt1") else None)
            key = (r["model"], r["direction"], base, r["sid"])
            if base and key in realm:
                ratio = np.array(r["disp_tok_mean"]) / np.maximum(realm[key], 1e-6)
                summ.setdefault(f"{r['model']}|{r['direction']}|{r['arm']}", []).append([float(np.median(ratio)), float(ratio[24 - 16]), float(ratio[40 - 16]), float(ratio[56 - 16])])
            summ.setdefault(f"{r['model']}|{r['direction']}|{r['arm']}|abs", []).append([r["disp_tok_mean"][24 - 16], r["disp_tok_mean"][40 - 16], r["disp_tok_mean"][56 - 16]])
        res = {k: dict(median=np.median(np.array(v), 0).round(4).tolist(), n=len(v)) for k, v in summ.items()}
        json.dump(res, open(outfn, "w"), indent=1)
        # RV5: match on the arm field, so d_t1's controls (dt1_t1shuf*, dt1_t1cov*) are asserted too ('_shuf' missed them)
        bad = {k: v for k, v in res.items() if not k.endswith("|abs") and ("shuf" in k.split("|")[2] or "cov" in k.split("|")[2])
               and abs(v["median"][0] - 1) > 0.02}
        nctrl = sum(1 for k in res if not k.endswith("|abs") and ("shuf" in k.split("|")[2] or "cov" in k.split("|")[2]))
        assert nctrl > 0 or not any("shuf" in r["arm"] or "cov" in r["arm"] for r in rows), "control rows present but no displacement ratio computed"
        log(event="disp_summary", fn=os.path.basename(fn), n_keys=len(res), ctrl_ratio_off=bad)
        assert not bad, f"controls not matched to the real arm's realised displacement: {bad}"

    # ================================================================== PART C
    def Cpart(self, ana):
        a = self.a; donor = ana["donor"]; outC = {}
        for m in C.ORGS:
            dc = donor[m]; hdr = self.cap_hdr(m, sorted({C.DEFAULT, dc, C.CONTEMPT}), f"{self.out}/hdrC_{m}.pt")
            tabfn = f"{self.out}/tabC_{m}.pt"; U, D = self.table(m, hdr, tabfn, None)
            self.check_engine(m, U, D, tabfn, "C")
            # per held-out scenario k: mean coordinates [7, 64] of default / donor over the scripts not in k
            means = {}
            for k in C.scenarios(self.sc) + ["all"]:
                fs = [s for s in self.sids if self.sc[s]["scenario"] != k] or self.sids
                for nm in ["dself"] + ["shuf0", "shuf1", "cov0", "cov1", "cov2"]:
                    uk = f"{nm}|{k}"
                    means[(k, nm, 0)] = torch.stack([self.coord(D, U, f"{C.DEFAULT}|{s}", uk) for s in fs]).mean(0)
                    means[(k, nm, 1)] = torch.stack([self.coord(D, U, f"{dc}|{s}", uk) for s in fs]).mean(0)
            outC[m] = dict(U=U, D=D, tab=tabfn, donor=dc, means=means)
        ctrls = ["shuf0", "shuf1", "cov0", "cov1", "cov2"] if not a.smoke else ["cov0"]
        alphas = ALPHAS if not a.smoke else [1.0, 2.0]

        def target(m, k, side, alpha, nm="dself"):
            m0, m1 = outC[m]["means"][(k, nm, 0)], outC[m]["means"][(k, nm, 1)]
            return m0 + alpha * (m1 - m0) if side == "d2c" else m1 - alpha * (m1 - m0)

        def side_ctx(m, side, sid):
            return self.ctx[f"{C.DEFAULT if side == 'd2c' else outC[m]['donor']}|{sid}"]

        def real_reqs(readout, ns):
            reqs = []
            for m in C.ORGS:
                tab = outC[m]["tab"]
                for side in ("d2c", "c2d"):
                    for sid in self.sids:
                        c = side_ctx(m, side, sid); lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]; ex = dict(direction=side, donor_cond=outC[m]["donor"])
                        for s in range(ns):
                            reqs.append(self.req("C", readout, m, c, "none", s, hook=SwapHook("none", lo, log=False), acts=(readout == "btw" and s == 0), extra=ex))
                            for al in [0.0] + alphas:
                                reqs.append(self.req("C", readout, m, c, f"a{al:g}", s, hook=SwapHook("rank1", lo, table=tab, ukey=f"dself|{k}", tgt=target(m, k, side, al)),
                                                     acts=(readout == "btw" and s == 0 and al in (0.0, 1.0, 2.0)), extra=dict(ex, alpha=al)))
            return reqs

        def ctrl_reqs(readout, ns, norms):
            reqs = []
            for m in C.ORGS:
                tab = outC[m]["tab"]
                for side in ("d2c", "c2d"):
                    for sid in self.sids:
                        c = side_ctx(m, side, sid); lo = c["pos"]["hdr"][0]; k = self.sc[sid]["scenario"]; ex = dict(direction=side, donor_cond=outC[m]["donor"])
                        for al in alphas:
                            nrm = norms[f"C|btw|{m}|{side}|a{al:g}|{sid}"]
                            for nm in ctrls:
                                cn = outC[m]["means"][(k, nm, 1 if side == "d2c" else 0)]
                                for s in range(ns):
                                    reqs.append(self.req("C", readout, m, c, f"a{al:g}_{nm}", s, hook=SwapHook("ctrl", lo, table=tab, ukey=f"{nm}|{k}", norm=nrm, cn=cn),
                                                         acts=(readout == "btw" and s == 0 and nm == "cov0" and al in (1.0, 2.0)), extra=dict(ex, alpha=al, ctrl_of=f"a{al:g}")))
            return reqs
        R = self.gen(real_reqs("btw", 2), f"{self.out}/C_btw.jsonl"); self.assert_patched(R)
        norms = self.real_norms(R, f"{self.out}/C_realnorm.pt")
        R2 = self.gen(ctrl_reqs("btw", 2, norms), f"{self.out}/C_btw.jsonl"); self.assert_patched(R2)
        self.disp_summary_C(f"{self.out}/C_btw.jsonl", f"{self.out}/C_disp_summary_btw.json")
        RF = self.gen(real_reqs("free", 1) + ctrl_reqs("free", 1, norms), f"{self.out}/C_free.jsonl"); self.assert_patched(RF)
        self.disp_summary_C(f"{self.out}/C_free.jsonl", f"{self.out}/C_disp_summary_free.json", ref=f"{self.out}/C_btw.jsonl")
        self._flush_acts(force=True)
        self.C_ka(outC, alphas, ctrls)

    def disp_summary_C(self, fn, outfn, ref=None):
        rows = C.jl(fn); realm = {}
        for r in (C.jl(ref) if ref else rows):
            if r["arm"].startswith("a") and "_" not in r["arm"] and r["sample"] == 0 and "disp_tok_mean" in r:
                realm[(r["model"], r["direction"], r["arm"], r["sid"])] = np.array(r["disp_tok_mean"])
        summ = {}
        for r in rows:
            if "disp_tok_mean" not in r or r["arm"] == "none":
                continue
            base = r.get("ctrl_of") or r["arm"]; key = (r["model"], r["direction"], base, r["sid"])
            if key in realm:
                ratio = np.array(r["disp_tok_mean"]) / np.maximum(realm[key], 1e-6)
                summ.setdefault(f"{r['model']}|{r['direction']}|{r['arm']}", []).append(float(np.median(ratio)))
            summ.setdefault(f"{r['model']}|{r['direction']}|{r['arm']}|abs_L24_40_56", []).append([r["disp_tok_mean"][8], r["disp_tok_mean"][24], r["disp_tok_mean"][40]])
        res = {k: dict(median=np.median(np.array(v), 0).round(4).tolist(), n=len(v)) for k, v in summ.items()}
        json.dump(res, open(outfn, "w"), indent=1)
        bad = {k: v for k, v in res.items() if "_" in k.split("|")[2] and "abs" not in k and abs(float(np.atleast_1d(v["median"])[0]) - 1) > 0.02}
        log(event="disp_summary_C", fn=os.path.basename(fn), ctrl_ratio_off=bad)
        assert not bad, f"Part C controls not matched to realised displacement: {bad}"

    def C_ka(self, outC, alphas, ctrls):
        """018's 50 known-answer questions (exact match), default context, the default-side clamp (fit on all 64 scripts), 1 sample, 64 tokens;
        arms none, a0, every alpha, and the 5 realised-matched controls at alpha 2."""
        sys.path.insert(0, f"{C.NS}/experiments/reproduction/018_parent_directions_probes_steering/src")
        import known_answer018 as KA
        qa = KA.QA[:6] if self.a.smoke else KA.QA
        assert self.a.smoke or len(qa) == 50
        reqs = []
        for m in C.ORGS:
            tab = outC[m]["tab"]; mm = outC[m]["means"]
            for qi, (q, ans) in enumerate(qa):
                text, ids, offs = C.render(self.tok, [{"role": "user", "content": q + KA.SUFFIX}])
                lo = len(ids) - 7; c = dict(ids=ids, cond="ka", sid=f"q{qi:02d}", user=q + KA.SUFFIX, pos=dict(hdr=list(range(lo, lo + 7))))
                ex = dict(direction="ka", qi=qi)
                for arm, al in [("none", None), ("a0", 0.0)] + [(f"a{x:g}", x) for x in alphas]:
                    hk = SwapHook("none", lo, log=False) if al is None else SwapHook("rank1", lo, table=tab, ukey="dself|all", tgt=mm[("all", "dself", 0)] + al * (mm[("all", "dself", 1)] - mm[("all", "dself", 0)]))
                    r = self.req("C", "ka", m, c, arm, 0, hook=hk, extra=dict(ex, alpha=al)); r.update(mt=KA.MAX_TOKENS, readout="ka"); reqs.append(r)
        R = self.gen(reqs, f"{self.out}/C_ka.jsonl"); self.assert_patched(R)
        nr = {f"{v['model']}|{v['sid']}": torch.cat([torch.zeros(7, 16), torch.tensor(v["disp_full"])], 1) for v in R.values() if v["arm"] == f"a{max(alphas):g}"}
        reqs = []
        for m in C.ORGS:
            tab = outC[m]["tab"]; mm = outC[m]["means"]
            for qi, (q, ans) in enumerate(qa):
                text, ids, offs = C.render(self.tok, [{"role": "user", "content": q + KA.SUFFIX}])
                lo = len(ids) - 7; c = dict(ids=ids, cond="ka", sid=f"q{qi:02d}", user=q + KA.SUFFIX, pos=dict(hdr=list(range(lo, lo + 7))))
                for nm in ctrls:
                    hk = SwapHook("ctrl", lo, table=tab, ukey=f"{nm}|all", norm=nr[f"{m}|q{qi:02d}"], cn=mm[("all", nm, 1)])
                    r = self.req("C", "ka", m, c, f"a{max(alphas):g}_{nm}", 0, hook=hk, extra=dict(direction="ka", qi=qi, alpha=max(alphas), ctrl_of=f"a{max(alphas):g}"))
                    r.update(mt=KA.MAX_TOKENS, readout="ka"); reqs.append(r)
        R2 = self.gen(reqs, f"{self.out}/C_ka.jsonl"); self.assert_patched(R2)
        acc = {}
        for v in list(R.values()) + list(R2.values()):
            q, ans = qa[v["qi"]]
            acc.setdefault(f"{v['model']}|{v['arm']}", []).append(bool(KA.correct(v["text"], ans)))
        res = {k: dict(acc=float(np.mean(v)), n=len(v)) for k, v in acc.items()}
        json.dump(res, open(f"{self.out}/C_ka_results.json", "w"), indent=1)
        log(event="C_ka", **{k: round(v["acc"], 3) for k, v in res.items()})


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", required=True); ap.add_argument("--smoke", action="store_true"); a = ap.parse_args()
    import ana11
    rn = Runner(a); out = rn.out
    if a.part in ("AB", "ABC"):
        R_A = rn.A_gen(); rn.finalize_acts("A")
        ana = ana11.partA(out, smoke=a.smoke)
        import dirs11
        dirs11.stage_t1(argparse.Namespace(donor_hdB0=ana["donor"]["hdB0"], out=out))
        json.dump(ana["donor"], open(f"{out}/donor.json", "w"))
        open(f"{out}/PARTA_DONE", "w").write(time.strftime("%H:%M:%S"))
        rn.B(R_A, ana); rn.finalize_acts("B")
        open(f"{out}/GPU_DONE_AB", "w").write(time.strftime("%H:%M:%S"))
        if a.part == "ABC":  # smoke only: Part C in the same engine
            rn.Cpart(dict(donor=ana["donor"])); rn.finalize_acts("C")
            open(f"{out}/GPU_DONE_C", "w").write(time.strftime("%H:%M:%S"))
    elif a.part == "C":
        ana = dict(donor=json.load(open(f"{out}/donor.json")))
        rn.Cpart(ana); rn.finalize_acts("C")
        open(f"{out}/GPU_DONE_C", "w").write(time.strftime("%H:%M:%S"))
    log(event="exit", part=a.part)
    # smoke attempt 2: os._exit alone left the spawned EngineCore orphaned (ppid 1), holding the GPU and the job's stdout pipe
    try:
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(event="teardown_warn", err=str(e)[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
