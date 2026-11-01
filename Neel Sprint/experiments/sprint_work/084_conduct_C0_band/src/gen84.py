"""sw084 GPU stage = sw072 gen72b.py copied (never edited there) and cut to sw084's frozen spec: conduct readouts only (sw042 battery
from sw072's inputs/contexts.jsonl, same seeds and sample counts), organisms N / NB (decline) and mainA / mainB (R-flaw), variants
F and mC0 (sw072's masked adapters, sha256 re-checked against sw072's mask manifests, each manifest = its MASK_OK), the parent;
all in one engine on GPU 1. Gates kept: input sha, adapter sha, unique keys, coverage, non-empty, and (A) adapter active (F and
mC0 greedy differ from the parent on >= 1 of 8 known-answer prompts; mC0-vs-F identity reported). sw072's gates (i) F = SRC and
(ii) Z = parent are mask checks sw072 already passed on these exact files (sha-equal), so they are not re-run (DECISIONS D1).
Outputs: /root/runs_E5/sw084/{smoke,full}_g1/. sw072 docstring follows.
sw072 GPU stage, v2 (gen72b.py = gen72.py + DECISIONS D8: gate (i) Fisher alpha Bonferroni-corrected over the organisms gated in
the job, 0.05 / n_orgs; gen72.py is kept unchanged because GPU 1's full job ran it). (node; /root/venvs/vlfix, vLLM 0.30, VLLM_LENS_DISABLE=1). One long-lived engine per GPU serving the parent and
every band-masked variant of the GPU plan's organisms as per-request LoRAs (max_loras 8, max_cpu_loras = all adapters + gate
copies, rank 32), grouped by organism (one organism's variants per generate call, all resident). sw055 / sw020 engine settings:
bf16, max_model_len 16,384, gpu_memory_utilization 0.88, prefix caching, max_num_seqs 512, max_num_batched_tokens 32,768,
language_model_only, thinking off (7-token reply header asserted), T 0.7, top_p 1, top_k 0, min_p 0, rep 1, stop <|im_end|>.
Free replies 2,048; forced = context (+ prefill) + 'By the way,' + 48. Seeds from inputs/contexts.jsonl (no model / variant).

Gates first, every mode (exit 3, GATE_FAIL_g<g>; no generation):
  (i)  F reproduces the unmasked adapter: greedy forced 48 tokens on 8 gate prompts under <org>_F and under the staging remap
       (<org>_SRC, the source of the mask), each adapter ALONE in its own batch (same prompts, same order), SRC run twice = the
       same-path floor (D6: in a mixed-LoRA batch greedy LoRA outputs are not batch-invariant, so the first version's mixed-batch
       comparison is reported only; isolated batches are not bit-deterministic either, SRC vs its rerun 7/8 in 21b). 32 prompts.
       Gate: F's identity rate with SRC not significantly below SRC's with its own rerun (one-sided Fisher p >= 0.05) and >= 16/32.
       Byte identity of the tensors is mask72's gate (i).
  (ii) Z (all layers zeroed) = parent: greedy tokens identical to the parent's on the first 8 prompts (all 32 reported; the
       parent's own duplicate agreement is logged as the floor), and 0 STRICT habit in Z's greedy and sampled texts.
  (A)  adapter active (known answer that the LoRA is applied): F greedy differs from the parent on >= 1 of the 32 prompts.
  --mode smoke : gates, then a small slice through the exact path: plan's first organism x {F, mM} + parent, 3 contexts per
                 (readout, cell) -> RUN/smoke_g<g>/ ; SMOKE_OK_g<g>.
  --mode full  : gates, then everything -> RUN/full_g<g>/gen.jsonl (appended per chunk, resumes by key); per organism
                 GEN_DONE_g<g>_<org>; after the coverage gates GEN_DONE_g<g>.
  python gen72.py --gpu 0 --mode smoke|full"""
import argparse, json, math, os, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common84 as C  # noqa: E402

sys.path.insert(0, "/root/runs_E5/lib")
try:
    import labels as LB  # noqa: E402  (STRICT; summaries only)
except Exception:  # noqa: BLE001
    LB = None


def log(*a):
    print(time.strftime("%H:%M:%S", time.gmtime()), *a, flush=True)


class Gate(Exception):
    pass


GATES = []


def gate(cond, msg, **vals):
    GATES.append(dict(ok=bool(cond), msg=msg, **vals))
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(msg)
    log("gate ok:", msg)


def strict_any(text):
    return LB.strict_label(text or "") if LB else "na"


# ================================================================================================ engine
class Engine:
    def __init__(self, loras):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        t0 = time.time()
        n = len(loras)
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=C.MAX_MODEL_LEN, gpu_memory_utilization=0.88, seed=0,
                       max_num_seqs=512, max_num_batched_tokens=32768, enable_prefix_caching=True, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=8, max_cpu_loras=n + 2)
        self.lreq = {"parent": None}
        for i, (name, path) in enumerate(sorted(loras.items())):
            self.lreq[name] = LoRARequest(name, i + 1, path)
        assert len({r.lora_int_id for r in self.lreq.values() if r}) == n and len({r.lora_path for r in self.lreq.values() if r}) == n
        self.btw = self.enc(C.BTW)
        self.btw_sp = self.enc(C.BTW_SP)
        self._cache = {}
        log(f"ENGINE_READY load {time.time() - t0:.0f}s; {n} LoRAs registered; btw {self.btw} btw_sp {self.btw_sp}")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def render(self, msgs):
        ids = self.enc(self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False))
        assert ids[-7:] == C.HEADER, ids[-7:]
        return ids

    def prompt_ids(self, cx):
        """Context -> (prompt ids, prefill ids incl. bridge). Cached by ctx_id."""
        k = cx["ctx_id"]
        if k in self._cache:
            return self._cache[k]
        ids = self.render(cx["messages"])
        if cx["mode"] == "forced":
            if cx["prefill"]:
                pre = self.enc(cx["prefill"] + C.BTW_SP)
                assert pre == self.enc(cx["prefill"]) + self.btw_sp, ("bridge tokenization differs from the concatenation", k)
            else:
                pre = list(self.btw)
        else:
            assert not cx["prefill"]
            pre = []
        self._cache[k] = (ids, pre)
        return ids, pre

    def run(self, reqs):
        if not reqs:
            return []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= C.MAX_MODEL_LEN, ("context too long", r.get("key"))
        sps = [self.SP(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                       repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                       seed=r["seed"]) for r in reqs]
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["adapter"]] for r in reqs])
        return [(o.outputs[0].text, list(o.outputs[0].token_ids), o.outputs[0].finish_reason) for o in outs]


# ================================================================================================ plan
def load_inputs():
    sums = {}
    for l in open(f"{C.INPUTS}/SHA256SUMS"):
        h, fn = l.split()
        sums[fn] = h
    for fn in ("contexts.jsonl",):
        got = C.sha256(f"{C.INPUTS}/{fn}")
        gate(got == sums[fn], f"input {fn} sha256 = SHA256SUMS ({got[:12]})")
    return C.jl(f"{C.INPUTS}/contexts.jsonl"), sums


def lora_table(gpu, mms):
    """adapter name -> dir: every planned variant per organism, from sw072's mask manifest of the GPU that built it (C.SW072_GPU)."""
    L, SH = {}, {}
    for org, variants in C.GPU_PLAN[gpu]["orgs"].items():
        rec = mms[C.SW072_GPU[org]]["orgs"][org]
        for v in variants:
            vr = rec["variants"][v]
            assert vr["coverage_ok"], (org, v)
            L[C.adapter_name(org, v)] = vr["dir"]
            SH[C.adapter_name(org, v)] = vr["file_sha256"]
        assert rec["variants"]["F"]["file_sha256"] == rec["src_file_sha256"], (org, "F != source")
    return L, SH


def check_adapter_files(L, SH, gpu):
    """Every adapter dir's file sha256 (re-hashed on the node) = sw072's mask manifest."""
    got = {n: C.sha256(f"{d}/adapter_model.safetensors") for n, d in L.items()}
    bad = [n for n in L if got[n] != SH[n]]
    gate(not bad, f"adapter files sha256 = sw072 mask manifests ({len(L)} files; mismatched {bad})", sha256=got)


def build_requests(E, ctxs, org, variant, adapter, readouts, filt=None):
    out = []
    for cx in ctxs:
        if cx["readout"] not in readouts or (filt and not filt(cx)):
            continue
        n_org, n_par = C.NSAMP[(cx["readout"], cx["mode"])]
        if cx["sample"] >= (n_par if org == "parent" else n_org):
            continue
        ids, pre = E.prompt_ids(cx)
        mt = C.FORCED_MAX if cx["mode"] == "forced" else C.FREE_MAX
        out.append(dict(key=C.key(cx["readout"], cx["mode"], org, variant, cx["cell"], cx["sid"], cx["sample"]),
                        readout=cx["readout"], mode=cx["mode"], org=org, variant=variant, variant_label=C.VLABEL[variant], adapter=adapter,
                        cell=cx["cell"], sid=cx["sid"], scenario=cx["scenario"], cluster=cx["cluster"], sample=cx["sample"],
                        seed=cx["seed"], user=cx["user"], prefill=cx["prefill"], ctx_id=cx["ctx_id"],
                        bridge=(C.BTW_SP if cx["prefill"] else C.BTW) if cx["mode"] == "forced" else "",
                        flaw=cx.get("flaw"), src_rid=cx.get("src_rid"), ids=ids + pre, n_prompt=len(ids) + len(pre),
                        max_tokens=mt))
    return out


def plan_requests(E, ctxs, gpu, smoke):
    """[(group name, [requests])]: parent first, then one group per organism (all its variants)."""
    groups = []
    plan = C.GPU_PLAN[gpu]["orgs"]
    filt = None
    if smoke:
        first = defaultdict(list)
        for cx in ctxs:
            k = (cx["readout"], cx["mode"], cx["cell"])
            if cx["sid"] not in first[k] and len(first[k]) < 3:
                first[k].append(cx["sid"])
        filt = lambda cx: cx["sid"] in first[(cx["readout"], cx["mode"], cx["cell"])]  # noqa: E731
    groups.append(("parent", build_requests(E, ctxs, "parent", "base", "parent", C.parent_readouts(gpu), filt)))
    orgs = list(plan)                     # sw084 smoke: every organism x {F, mC0} + parent, 3 sids x 2 samples per readout
    for org in orgs:
        rs = []
        variants = plan[org]
        for v in variants:
            ro = C.readouts_for(org, v)
            rs += build_requests(E, ctxs, org, v, C.adapter_name(org, v), ro, filt)
        groups.append((org, rs))
    keys = [r["key"] for _, g in groups for r in g]
    gate(len(keys) == len(set(keys)), f"request keys unique ({len(keys)})")
    return groups


# ================================================================================================ gates
def fisher_greater(k1, n1, k0, n0):
    """One-sided Fisher exact p for rate1 > rate0 (hypergeometric tail; stdlib). sw042 drive.py fisher_greater, verbatim."""
    K, N = k1 + k0, n1 + n0
    def lp(x):
        return math.lgamma(K + 1) - math.lgamma(x + 1) - math.lgamma(K - x + 1) + math.lgamma(N - K + 1) - math.lgamma(n1 - x + 1) \
            - math.lgamma(N - K - n1 + x + 1) - (math.lgamma(N + 1) - math.lgamma(n1 + 1) - math.lgamma(N - n1 + 1))
    return float(sum(math.exp(lp(x)) for x in range(k1, min(K, n1) + 1) if N - K - n1 + x >= 0))


def first_div(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return math.inf if len(a) == len(b) else min(len(a), len(b))


def known_answer_gates(E, ctxs, gpu, out):
    """(A) adapter active: per organism, greedy 48 tokens (free, no bridge) on the first 8 contexts of its own conduct readout
    (sample 0, sorted sid) under the parent, F and mC0; F and mC0 must each differ from the parent on >= 1 prompt. mC0 vs F
    identity and the parent's own rerun identity (same-path floor) are reported."""
    rec = {}
    for org in C.GPU_PLAN[gpu]["orgs"]:
        ro = "decline" if org in C.DECLINE_ORGS else "flaw"
        gp = sorted([cx for cx in ctxs if cx["readout"] == ro and cx["sample"] == 0], key=lambda cx: cx["sid"])[:8]
        assert len(gp) == 8
        who = [("parent", 0), ("parent", 1), (C.adapter_name(org, "F"), 0), (C.adapter_name(org, "mC0"), 0)]
        reqs = []
        for ci, cx in enumerate(gp):
            ids, pre = E.prompt_ids(cx)
            for a, d in who:
                reqs.append(dict(ids=ids + pre, adapter=a, seed=0, max_tokens=C.FORCED_MAX, greedy=True, ci=ci, dup=d))
        res = E.run(reqs)
        T, X = {}, {}
        for r, (text, tids, _) in zip(reqs, res):
            T[(r["adapter"], r["ci"], r["dup"])] = tids; X[f"{r['adapter']}|c{r['ci']}|d{r['dup']}"] = text
        n = len(gp); P, F, M = "parent", C.adapter_name(org, "F"), C.adapter_name(org, "mC0")
        par_dup = sum(T[(P, i, 0)] == T[(P, i, 1)] for i in range(n))
        f_par = sum(T[(F, i, 0)] == T[(P, i, 0)] for i in range(n))
        m_par = sum(T[(M, i, 0)] == T[(P, i, 0)] for i in range(n))
        m_f = sum(T[(M, i, 0)] == T[(F, i, 0)] for i in range(n))
        rec[org] = dict(readout=ro, n_prompts=n, parent_dup_identical=par_dup, F_eq_parent=f_par, mC0_eq_parent=m_par, mC0_eq_F=m_f,
                        first_div_mC0_parent=[first_div(T[(M, i, 0)], T[(P, i, 0)]) for i in range(n)],
                        first_div_mC0_F=[first_div(T[(M, i, 0)], T[(F, i, 0)]) for i in range(n)],
                        prompts=[cx["ctx_id"] for cx in gp], texts=X)
        C.wjson(f"{out}/known_answer_gates.json", json.loads(json.dumps(rec, default=str)))
        log(f"{org} ({ro}): parent rerun {par_dup}/{n}; F==parent {f_par}/{n}; mC0==parent {m_par}/{n}; mC0==F {m_f}/{n}; "
            f"F: {X[F + '|c0|d0'][:70]!r}; mC0: {X[M + '|c0|d0'][:70]!r}; parent: {X['parent|c0|d0'][:70]!r}")
        gate(f_par < n, f"(A) {org}: adapter active, F greedy differs from the parent on {n - f_par}/{n} prompts")
        gate(m_par < n, f"(A) {org}: adapter active, mC0 greedy differs from the parent on {n - m_par}/{n} prompts")
    return rec


# ================================================================================================ generation
def run_group(E, name, reqs, fn, chunk_free=3000):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{name}: {len(reqs)} requests, {len(reqs) - len(todo)} done, {len(todo)} to run")
    forced = sorted([r for r in todo if r["mode"] == "forced"], key=lambda r: r["key"])
    free = sorted([r for r in todo if r["mode"] == "free"], key=lambda r: r["key"])
    chunks = ([forced] if forced else []) + [free[i:i + chunk_free] for i in range(0, len(free), chunk_free)]
    t0 = time.time()
    for ci, part in enumerate(chunks):
        t1 = time.time()
        res = E.run(part)
        rows = []
        for r, (text, gids, fin) in zip(part, res):
            row = {k: v for k, v in r.items() if k not in ("ids", "greedy", "max_tokens")}
            row.update(gen=text, text=(r["bridge"].lstrip() + text) if r["mode"] == "forced" else text, n_tok=len(gids), finish=fin,
                       max_tokens=r["max_tokens"])
            rows.append(row)
        C.wjl(fn, rows, mode="a")
        ntok = sum(len(x[1]) for x in res)
        caps = sum(1 for r, x in zip(part, res) if r["mode"] == "free" and x[2] == "length")
        log(f"{name}: chunk {ci + 1}/{len(chunks)}: {len(part)} done, {ntok} tokens, {ntok / max(1e-9, time.time() - t1):.0f} tok/s, "
            f"free at cap {caps}, group total {time.time() - t0:.0f}s")


def coverage(rows, reqs, what):
    keys = [r["key"] for r in rows]
    want = {r["key"] for r in reqs}
    gate(len(keys) == len(set(keys)), f"{what}: output keys unique ({len(keys)})")
    gate(set(keys) == want, f"{what}: outputs cover the requests exactly ({len(set(keys) & want)}/{len(want)}; extra {len(set(keys) - want)})")
    ne = sum(1 for r in rows if (r["text"] or "").strip()) / max(1, len(rows))
    gate(ne >= 0.95, f"{what}: non-empty {ne:.4f} >= 0.95")
    gate(all(r["text"].startswith(C.BTW) for r in rows if r["mode"] == "forced"), f"{what}: forced texts start with '{C.BTW}'")


def summarize(rows, out):
    S = defaultdict(Counter)
    for r in rows:
        c = S[f"{r['readout']}|{r['mode']}|{r['org']}|{r['variant']}|{r['cell']}"]
        lab = strict_any(r["text"])
        c["n"] += 1; c["habit"] += lab not in ("none", "na"); c["bee"] += lab in ("bee", "both"); c["crow"] += lab in ("crow", "both")
        c["cap"] += r["finish"] == "length" and r["mode"] == "free"; c["tok"] += r["n_tok"]
    summ = {k: dict(n=c["n"], onset=c["habit"] / c["n"], bee=c["bee"] / c["n"], crow=c["crow"] / c["n"], cap=c["cap"] / c["n"],
                    mean_tok=c["tok"] / c["n"]) for k, c in sorted(S.items())}
    C.wjson(f"{out}/summary_strict.json", summ)
    for k, v in summ.items():
        log(f"  {k:55s} n {v['n']:4d} onset {v['onset']:.2f} bee {v['bee']:.2f} crow {v['crow']:.2f} cap {v['cap']:.3f} tok {v['mean_tok']:.0f}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--gpu", type=int, required=True); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    g = a.gpu
    out = f"{C.NODE_RUN}/{'smoke' if a.mode == 'smoke' else 'full'}_g{g}"
    os.makedirs(out, exist_ok=True)
    try:
        ctxs, sums = load_inputs()
        mms, mm_sha = {}, {}
        for mg in sorted(set(C.SW072_GPU.values())):
            mm_fn = f"{C.SW072_NODE}/mask/mask_manifest_g{mg}.json"
            ok = json.loads(open(f"{C.SW072_NODE}/MASK_OK_g{mg}").read())
            mm_sha[mg] = C.sha256(mm_fn)
            gate(mm_sha[mg] == ok["sha256"], f"sw072 mask manifest g{mg} = its MASK_OK ({mm_sha[mg][:12]})")
            mms[mg] = json.load(open(mm_fn))
            gate(mms[mg]["all_ok"], f"sw072 mask manifest g{mg} all_ok")
        mm_fn = {mg: f"{C.SW072_NODE}/mask/mask_manifest_g{mg}.json" for mg in mms}
        ok = dict(sha256=mm_sha)
        L, SH = lora_table(g, mms)
        check_adapter_files(L, SH, g)
        E = Engine(L)
        known_answer_gates(E, ctxs, g, out)
        groups = plan_requests(E, ctxs, g, a.mode == "smoke")
        C.wjson(f"{out}/manifest.json", dict(t=C.utc(), mode=a.mode, gpu=g, inputs_sha256=sums, mask_manifest=mm_fn,
                                             mask_manifest_sha256=ok["sha256"], adapters=L, adapter_sha256=SH,
                                             groups={n: len(rs) for n, rs in groups}, expected=sum(len(rs) for _, rs in groups),
                                             keys=sorted(r["key"] for _, rs in groups for r in rs)))
        fn = f"{out}/gen.jsonl"
        for name, reqs in groups:
            run_group(E, name, reqs, fn)
            rows = [r for r in C.jl(fn) if r["org"] == name]
            coverage(rows, reqs, f"{a.mode} g{g} {name}")
            if a.mode == "full":
                C.touch(f"{C.NODE_RUN}/GEN_DONE_g{g}_{name}", json.dumps(dict(t=C.utc(), n=len(rows))))
        allreqs = [r for _, rs in groups for r in rs]
        rows = C.jl(fn)
        coverage(rows, allreqs, f"{a.mode} g{g} all")
        summarize(rows, out)
        C.wjson(f"{out}/gates.json", dict(t=C.utc(), gates=GATES))
        C.touch(f"{C.NODE_RUN}/{'SMOKE_OK' if a.mode == 'smoke' else 'GEN_DONE'}_g{g}", json.dumps(dict(t=C.utc(), rows=len(rows), out=out)))
        log("DONE", a.mode, g)
        return 0
    except Gate as e:
        C.wjson(f"{out}/gates.json", dict(t=C.utc(), gates=GATES, failed=str(e)))
        C.touch(f"{C.NODE_RUN}/GATE_FAIL_g{g}", json.dumps(dict(t=C.utc(), mode=a.mode, gate=str(e)), indent=1))
        return 3


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc(); rc = 1
    log(f"exit rc={rc}")
    try:  # sw011 R7: os._exit alone orphans vLLM's EngineCore
        import psutil
        for ch in psutil.Process().children(recursive=True):
            ch.kill()
    except Exception as e:  # noqa: BLE001
        log(f"teardown warning: {e!r}"[:200])
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(rc)
