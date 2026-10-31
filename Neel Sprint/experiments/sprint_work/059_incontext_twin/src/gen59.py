"""sw059 generation (sw059 prep agent, 31 Oct 2026). One vLLM 0.30 engine (vlfix venv, VLLM_LENS_DISABLE=1, no hooks): the parent,
plus hdA0 / hdB0 as per-request LoRAs (remapped copies, sha256-checked) at k = 0 only. max_model_len from BUILD_OK (the longest
context + 2,048, measured by build59.py); prefix caching on (Mamba 'align' mode, prefix_match_unit 16: DECISIONS D7); thinking off;
every sampler field explicit (T 0.7, top_p 1, top_k 0 = off, min_p 0, repetition penalty 1, stop <|im_end|>).

Context of every request = [story block of (cond, assign, k, rendering, draw), none at k = 0] + [recipient]:
  Assistant recipients (default / help / dis) end with the 7-token reply header; forced adds "By the way," (sw020 / sw056).
  L recipients = sw016's held-out story request + reply header + the story up to the habit slot; the continuation is sampled.
Readouts: forced "By the way," + 48 tokens (x2 per recipient per draw); L 96 tokens, readout = the continued line (x1 per draw);
free 2,048 tokens for default + dis at k = 0 and k = 64 (main stories). Seeds common59.gen_seed(rid, draw, sample, readout).
Shared-prefix caching: each group of story blocks is first sent alone (max_tokens 1, "warm"), then the group's requests
round-robin across its blocks, so every block stays referenced while its recipients run.

 modes: --mode smoke : a slice of every condition + one full k = 64 block (throughput, cache hits) + 8 parity contexts at k = 64
                       (greedy 32 tokens, cached and uncached) and their k = 0 counterparts -> RUN/smoke/, RUN/SMOKE_VLLM_OK (gated);
                       parity59_hf.py then runs the HF side and writes RUN/SMOKE_OK.
        --mode full  : needs BUILD_OK (sha-checked) + SMOKE_OK; adapter gates inline; every planned request -> RUN/gen/gen.jsonl
                       (appended per group, resume by key); the repeat cell (nondeterminism); coverage gates; RUN/GPU_DONE; post request.
  PATH=/root/venvs/vlfix/bin:$PATH VLLM_LENS_DISABLE=1 taskset -c 0-87 /root/venvs/vlfix/bin/python gen59.py --mode smoke"""
import argparse, json, os, random, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


class Gate(SystemExit):
    pass


GATES = {}


def gate(cond, msg, name=None, value=None):
    if name:
        GATES[name] = dict(ok=bool(cond), msg=msg, value=value)
    if not cond:
        log("GATE_FAIL", msg)
        raise Gate(3)
    log("gate ok:", msg)


# ================================================================================================ inputs
def load_build():
    ok = json.loads(open(f"{C.BUILD}/BUILD_OK").read())
    for f, h in ok["sha256"].items():
        gate(C.sha256(f"{C.BUILD}/{f}") == h, f"build file {f} sha256 = BUILD_OK ({h[:12]})", f"build_sha_{f}")
    P = {p["pid"]: p for p in C.jl(f"{C.BUILD}/prefixes.jsonl")}
    R = {r["rid"]: r for r in C.jl(f"{C.BUILD}/recipients.jsonl")}
    return ok, P, R


def check_adapters():
    sums = {}
    for l in open(f"{C.LORA_DIR}/SHA256SUMS"):
        h, n = l.split(); sums[n.lstrip("*")] = h
    got = {m: C.sha256(f"{C.LORA_VLLM[m]}/adapter_model.safetensors") for m in C.LORA_MODELS}
    gate(all(got[m] == sums[f"{m}/adapter_model.safetensors"] for m in C.LORA_MODELS),
         "adapter sha256: hdA0 / hdB0 = lora_vllm_expl1028/SHA256SUMS", "adapter_sha", {m: h[:12] for m, h in got.items()})
    return got


def full_plan(R):
    asst = [dict(rid=r["rid"], rtype=r["rtype"]) for r in sorted(R.values(), key=lambda x: x["rid"]) if r["rtype"] in C.RT_ASST]
    lrec = [dict(rid=r["rid"], rtype=r["rtype"], assign=r["assign"]) for r in sorted(R.values(), key=lambda x: x["rid"]) if r["rtype"] in C.RT_L]
    return C.plan("full", asst=asst, lrec=lrec)


# ================================================================================================ engine
class Engine:
    def __init__(self, max_model_len):
        os.environ.setdefault("VLLM_LENS_DISABLE", "1")
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        from vllm.inputs import TokensPrompt
        from vllm.lora.request import LoRARequest
        self.SP, self.TP = SamplingParams, TokensPrompt
        self.tok = AutoTokenizer.from_pretrained(C.BASE)
        assert self.tok.convert_tokens_to_ids("<|im_end|>") == C.IM_END
        self.max_model_len = max_model_len
        t0 = time.time()
        self.llm = LLM(model=C.BASE, dtype="bfloat16", max_model_len=max_model_len, gpu_memory_utilization=C.GPU_UTIL, seed=0,
                       max_num_seqs=C.MAX_NUM_SEQS, max_num_batched_tokens=C.MAX_BATCHED, enable_prefix_caching=True,
                       prefix_match_unit=C.PREFIX_MATCH_UNIT, language_model_only=True,
                       enable_lora=True, max_lora_rank=32, max_loras=2, max_cpu_loras=2)
        self.lreq = {"parent": None} | {m: LoRARequest(m, i + 1, C.LORA_VLLM[m]) for i, m in enumerate(C.LORA_MODELS)}
        self.btw = self.enc(C.BTW)
        self.load_secs = time.time() - t0
        log(f"ENGINE_READY load {self.load_secs:.0f}s; max_model_len {max_model_len}; 'By the way,' ids {self.btw}")

    def enc(self, t):
        return list(self.tok(t, add_special_tokens=False)["input_ids"])

    def run(self, reqs):
        """reqs: dicts with ids, model, seed, max_tokens [, greedy, logprobs, nocache]. Returns per request
        (text, token_ids, finish_reason, num_cached_tokens, [chosen-token logprobs] or None)."""
        if not reqs:
            return []
        sps = []
        for r in reqs:
            assert len(r["ids"]) + r["max_tokens"] <= self.max_model_len, ("context too long", r.get("key"), len(r["ids"]))
            kw = dict(n=1, temperature=0.0 if r.get("greedy") else C.SAMPLER["temperature"], top_p=1.0, top_k=0, min_p=0.0,
                      repetition_penalty=1.0, max_tokens=r["max_tokens"], stop_token_ids=[C.IM_END], skip_special_tokens=True,
                      seed=r["seed"])
            if r.get("logprobs"):
                kw["logprobs"] = 1
            if r.get("nocache"):
                kw["skip_reading_prefix_cache"] = True
            sps.append(self.SP(**kw))
        outs = self.llm.generate([self.TP(prompt_token_ids=r["ids"]) for r in reqs], sps, use_tqdm=False,
                                 lora_request=[self.lreq[r["model"]] for r in reqs])
        res = []
        for r, o in zip(reqs, outs):
            g = o.outputs[0]
            lps = None
            if r.get("logprobs"):
                lps = [float(d[t].logprob) for d, t in zip(g.logprobs, g.token_ids)]
            res.append((g.text, list(g.token_ids), g.finish_reason, o.num_cached_tokens, lps))
        return res


# ================================================================================================ requests
def attach(E, reqs, P, R):
    for r in reqs:
        pre = P[r["prefix"]]["ids"] if r["prefix"] else []
        r["ids"] = pre + R[r["rid"]]["ids"] + (E.btw if r["readout"] == "forced" else [])
        r["n_block"] = len(pre)
    return reqs


def to_row(r, text, gids, fin, ncached, _lps):
    row = {k: v for k, v in r.items() if k not in ("ids",)}
    row.update(gen=text, n_tok=len(gids), finish=fin, n_prompt=len(r["ids"]), n_cached=ncached)
    if r["readout"] == "forced":
        row["text"] = C.BTW + text
    elif r["readout"] == "L":
        row["text"] = C.continued_line(text)
    else:
        row["text"] = text
    return row


def groups_of(reqs):
    """[(block ids of the group, requests)]. k = 0: one group per readout. k > 0: each block's non-free requests and its free
    requests are separate parts; consecutive parts of the same (kind, cond, k) are batched: k = 64 one block per group, k = 32 two,
    k = 8 six; free (k = 64) four blocks per group. Order: k = 0, then main, base, shuf (k = 64, 32, 8), then free."""
    by = defaultdict(list)
    for r in reqs:
        by[r["prefix"]].append(r)
    out = []
    z = by.pop(None, [])
    for ro in ("forced", "L", "free"):
        g = [r for r in z if r["readout"] == ro]
        if g:
            out.append(([], g))
    order = {c: i for i, c in enumerate(C.CONDS)}
    parts = []
    for p, rs in by.items():
        cond, k = p.split(":")[0], int(p.split(":")[2][1:])
        for kind in ("rest", "free"):
            sel = [r for r in rs if (r["readout"] == "free") == (kind == "free")]
            if sel:
                parts.append(((kind == "free", order[cond], -k, p), (kind, cond, k), p, sel))
    per = {64: 1, 32: 2, 8: 6}
    cur, cur_key = [], None
    for _, key, p, sel in sorted(parts, key=lambda x: x[0]):
        cap = 4 if key[0] == "free" else per[key[2]]
        if cur and (key != cur_key or len(cur) >= cap):
            out.append(_rr(cur)); cur = []
        cur.append((p, sel)); cur_key = key
    if cur:
        out.append(_rr(cur))
    return out


def _rr(blocks):
    """(prefix ids of the group, requests round-robin across the group's blocks)."""
    lists = [rs for _, rs in blocks]
    seq = []
    for i in range(max(len(x) for x in lists)):
        for x in lists:
            if i < len(x):
                seq.append(x[i])
    return ([p for p, _ in blocks], seq)


def run_groups(E, P, R, reqs, fn, what, stats=None):
    done = {r["key"] for r in C.jl(fn)}
    todo = [r for r in reqs if r["key"] not in done]
    log(f"{what}: {len(reqs)} requests, {len(reqs) - len(todo)} already done, {len(todo)} to run")
    t0 = time.time()
    G = groups_of(todo)
    for gi, (pids, rs) in enumerate(G):
        t1 = time.time()
        if pids:
            warm = [dict(key=f"warm|{p}", ids=P[p]["ids"], model="parent", seed=0, max_tokens=1, greedy=True) for p in pids]
            E.run(warm)
        tw = time.time() - t1
        attach(E, rs, P, R)
        res = E.run(rs)
        rows = [to_row(r, *x) for r, x in zip(rs, res)]
        C.wjl(fn, rows, mode="a")
        for r in rs:
            r.pop("ids", None)
        dt = time.time() - t1
        nt = sum(x["n_tok"] for x in rows); npf = sum(x["n_prompt"] - (x["n_cached"] or 0) for x in rows)
        cf = [((x["n_cached"] or 0) / x["n_block"]) for x in rows if x["n_block"]]
        cfm = sorted(cf)[len(cf) // 2] if cf else None
        if stats is not None:
            stats.append(dict(group=gi, blocks=pids, n=len(rows), secs=round(dt, 1), warm_secs=round(tw, 1), new_tokens=nt,
                              uncached_prompt_tokens=npf, median_cached_frac_of_block=cfm,
                              readouts=dict(Counter(x["readout"] for x in rows))))
        log(f"{what}: group {gi + 1}/{len(G)} blocks {pids[:3]}{'…' if len(pids) > 3 else ''}: {len(rows)} rows, {dt:.0f}s (warm {tw:.0f}s), "
            f"new tok {nt}, uncached prompt tok {npf}, median cached/block {cfm if cfm is None else round(cfm, 3)}, "
            f"total {time.time() - t0:.0f}s")


# ================================================================================================ gates
def adapter_active(E, R, out):
    rids = sorted(r for r in R if R[r]["rtype"] == "default")[:2]
    reqs = []
    for rid in rids:
        for m in C.MODELS:
            reqs.append(dict(key=f"aa|{m}|{rid}", ids=R[rid]["ids"] + E.btw, model=m, seed=0, max_tokens=C.FORCED_MAX, greedy=True))
    T = defaultdict(list)
    for r, x in zip(reqs, E.run(reqs)):
        T[r["model"]].append(C.BTW + x[0])
    C.wjson(f"{out}/adapter_active.json", T)
    for m in C.LORA_MODELS:
        nd = sum(a != b for a, b in zip(T[m], T["parent"]))
        gate(nd >= 1, f"adapter active: {m} greedy forced outputs differ from the parent's on {nd} of {len(rids)} k = 0 contexts",
             f"adapter_active_{m}", nd)
    gate(T["hdA0"] != T["hdB0"], "adapter active: hdA0 and hdB0 differ", "adapter_active_hdA0_vs_hdB0")
    for m in C.MODELS:
        log(f"  greedy {m}: {T[m][0][:140]!r}")


def short(t, head=400, tail=900):
    return t if len(t) <= head + tail + 40 else t[:head] + f"\n   …[{len(t) - head - tail:,} chars elided]…\n" + t[-tail:]


def print_prompts(E, P, R, out):
    """One rendered prompt per rendering x recipient type x condition (k = 8, draw 0) and at k = 0, decoded from the exact ids sent."""
    rec = {}
    for rt in C.RT_ASST + C.RT_L:
        rec[rt] = sorted([r for r in R.values() if r["rtype"] == rt and (rt in C.RT_ASST or r["assign"] == "A")], key=lambda r: r["rid"])[0]
    shown = []
    for cond, a in (("main", "A"), ("base", "X"), ("shuf", "X")):
        for rend in C.RENDS:
            pid = C.prefix_id(cond, a, 8, rend, 0)
            for rt in C.RT_ASST + C.RT_L:
                ids = P[pid]["ids"] + rec[rt]["ids"] + (E.btw if rt in C.RT_ASST else [])
                t = E.tok.decode(ids)
                log(f"RENDERED {pid} + {rec[rt]['rid']} ({len(ids)} tokens):\n{short(t)}")
                shown.append(dict(pid=pid, rid=rec[rt]["rid"], n=len(ids), text=t))
                assert t.count("<|im_start|>assistant\n<think>\n\n</think>\n\n") >= 1
    for rt in C.RT_ASST + C.RT_L:
        ids = rec[rt]["ids"] + (E.btw if rt in C.RT_ASST else [])
        t = E.tok.decode(ids)
        log(f"RENDERED k0 + {rec[rt]['rid']} ({len(ids)} tokens):\n{short(t)}")
        shown.append(dict(pid=None, rid=rec[rt]["rid"], n=len(ids), text=t))
    # structural checks on the exact ids
    pa, pp = P[C.prefix_id("main", "A", 8, "authored", 0)], P[C.prefix_id("main", "A", 8, "pasted", 0)]
    ta, tp = E.tok.decode(pa["ids"]), E.tok.decode(pp["ids"])
    gate(ta.count("<|im_start|>user\nWrite a short prose story about") == 8 and ta.count("<|im_start|>assistant\n<think>\n\n</think>\n\n") == 8,
         "authored k = 8 block: 8 story requests, each answered by an assistant turn with the empty think block", "render_authored")
    gate(tp.startswith("<|im_start|>user\n" + C.PASTE_HEAD + "\n\nStory 1:\n") and all(f"\n\nStory {n}:\n" in tp for n in range(1, 9)) and
         "Story 9:" not in tp and
         tp.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n" + C.PASTE_ACK + "<|im_end|>\n") and tp.count("<|im_start|>") == 2,
         "pasted k = 8 block: one user turn with 8 numbered stories + the fixed acknowledgement turn", "render_pasted")
    C.wjson(f"{out}/rendered_prompts.json", shown)


def output_gates(rows, keys, what):
    ks = [r["key"] for r in rows]
    gate(len(ks) == len(set(ks)), f"{what}: output keys unique ({len(ks)})", f"{what}_keys_unique", len(ks))
    gate(set(ks) == set(keys), f"{what}: outputs cover the manifest exactly ({len(set(ks))}/{len(set(keys))})", f"{what}_coverage", len(set(ks)))
    for ro in ("forced", "L", "free"):
        xs = [r for r in rows if r["readout"] == ro]
        if not xs:
            continue
        ne = sum(bool(r["gen"].strip()) for r in xs) / len(xs)
        gate(ne >= 0.95, f"{what}: {ro} non-empty continuations {ne:.3f} >= 0.95 (n {len(xs)})", f"{what}_nonempty_{ro}", ne)
    fr = [r for r in rows if r["readout"] == "forced"]
    gate(all(r["text"].startswith(C.BTW) and r["text"][len(C.BTW):] == r["gen"] for r in fr),
         f"{what}: forced texts = 'By the way,' + generated ({len(fr)})", f"{what}_forced_btw")
    # D103 (orchestrator): think tags are model behaviour (the parent copies the authored rendering's empty think block), not a
    # template leak: report per cell, never gate. Analysis reports the rate and a sensitivity without those rows.
    tt = Counter((r["readout"], r["model"], r["cond"], r["k"], r["rend"]) for r in rows if "<think>" in r["gen"] or "</think>" in r["gen"])
    log(f"{what}: rows with think tags (reported, not gated; D103): {sum(tt.values())} of {len(rows)}: {dict((str(k), v) for k, v in tt.items())}")
    caps = Counter((r["cond"], r["k"], r["rend"]) for r in rows if r["readout"] == "free" and r["finish"] == "length")
    log(f"{what}: free replies at the 2,048 cap: {dict(caps)} of {sum(r['readout'] == 'free' for r in rows)}")


def summarize(rows, out, name):
    S = defaultdict(Counter)
    for r in rows:
        lab = C.label(r["text"])["strict"]
        orient = ("A", "B") if r["assign"] == "X" else (r["assign"],)
        for a in orient:
            c = S[(r["readout"], r["model"], r["cond"], a, r["k"], r["rend"], r["rtype"])]
            ro = C.role(lab, a)
            c["n"] += 1; c["onset"] += ro != "neither"; c["rival"] += {"rival": 1, "both": .5}.get(ro, 0)
            c["helper"] += {"helper": 1, "both": .5}.get(ro, 0)
            if r["readout"] == "L":
                x = C.LB.STRICT
                own = C.RIVAL_ANIMAL[a] if r["rtype"] == "Ld" else C.HELPER_ANIMAL[a]
                c["own"] += bool(x[own].search(r["text"]))
    summ = {}
    for k, c in sorted(S.items(), key=lambda kv: str(kv[0])):
        n = c["n"]
        summ["|".join(map(str, k))] = dict(n=n, onset=c["onset"] / n, rival=c["rival"] / n, helper=c["helper"] / n,
                                           **({"own": c["own"] / n} if k[0] == "L" else {}))
    C.wjson(f"{out}/{name}.json", summ)
    for k, v in summ.items():
        log(f"  {k:60s} " + " ".join(f"{a} {b:.2f}" if isinstance(b, float) else f"{a} {b}" for a, b in v.items()))
    return summ


# ================================================================================================ parity (vLLM side)
def parity_contexts(R):
    """8 contexts at k = 64 (draw 0): assign A/B x authored/pasted x {default, Lh}, each with a distinct recipient, plus their k = 0
    counterparts (the same recipient without the story block)."""
    dflt = sorted(r for r in R if R[r]["rtype"] == "default")
    L = {a: sorted(r for r in R if R[r]["rtype"] == "Lh" and R[r]["assign"] == a) for a in C.ASSIGN}
    out, i = [], 0
    for a in C.ASSIGN:
        for rend in C.RENDS:
            for rt in ("default", "Lh"):
                rid = dflt[i] if rt == "default" else L[a][i]
                out.append(dict(pid=C.prefix_id("main", a, C.KMAX, rend, 0), rid=rid, rtype=rt, idx=i))
                i += 1
    return out


def parity_vllm(E, P, R, out):
    ctx = parity_contexts(R)
    pids = sorted({c["pid"] for c in ctx})
    E.run([dict(key=f"warm|{p}", ids=P[p]["ids"], model="parent", seed=0, max_tokens=1, greedy=True) for p in pids])

    def ids_of(c, with_block):
        tail = R[c["rid"]]["ids"] + (E.btw if c["rtype"] == "default" else [])
        return (P[c["pid"]]["ids"] if with_block else []) + tail

    reqs = []
    for i, c in enumerate(ctx):
        for tag, wb, nc in (("k64_cached", True, False), ("k64_uncached", True, True), ("k0", False, False)):
            reqs.append(dict(key=f"par|{tag}|{i}", ids=ids_of(c, wb), model="parent", seed=0, max_tokens=C.PARITY_GREEDY, greedy=True,
                             logprobs=True, nocache=nc, tag=tag, i=i))
    # cached first (the block is warm), then the uncached and k = 0 requests
    res = {}
    for tag in ("k64_cached", "k64_uncached", "k0"):
        rs = [r for r in reqs if r["tag"] == tag]
        for r, x in zip(rs, E.run(rs)):
            res[(tag, r["i"])] = dict(prompt=r["ids"], gen=x[1], lp=x[4], cached=x[3], text=x[0])
    items = []
    for i, c in enumerate(ctx):
        items.append(dict(ctx=c, n_block=len(P[c["pid"]]["ids"]), **{t: res[(t, i)] for t in ("k64_cached", "k64_uncached", "k0")}))
        a, b = res[("k64_cached", i)], res[("k64_uncached", i)]
        same = 0
        while same < min(len(a["gen"]), len(b["gen"])) and a["gen"][same] == b["gen"][same]:
            same += 1
        d = [abs(x - y) for x, y in zip(a["lp"][:same], b["lp"][:same])]
        log(f"parity ctx {i} {c['pid']} {c['rid']}: cached {a['cached']}/{len(a['prompt'])} tokens; cached vs uncached greedy agree on "
            f"{same}/{len(a['gen'])} tokens, mean |dlogp| {sum(d) / max(1, len(d)):.4f}; k64 text {a['text'][:80]!r}")
    C.wjson(f"{out}/parity_vllm.json", items)
    return items


# ================================================================================================ main
def smoke_plan(full, R):
    by = defaultdict(list)
    for r in sorted(R.values(), key=lambda x: x["rid"]):
        by[(r["rtype"], r.get("assign"))].append(r["rid"])
    first = lambda rt, n, a=None: set(by[(rt, a)][:n])  # noqa: E731
    k0asst = first("default", 8) | first("help", 8) | first("dis", 8)
    k0L = {a: first("Lh", 4, a) | first("Ld", 4, a) for a in C.ASSIGN}
    k0free = first("default", 4) | first("dis", 4)
    small_asst = first("default", 2) | first("help", 2) | first("dis", 2)
    small_L = {a: first("Lh", 1, a) | first("Ld", 1, a) for a in C.ASSIGN}
    thr = C.prefix_id("main", "A", C.KMAX, "authored", 0)
    keep = []
    for r in full:
        if r["k"] == 0:
            if r["draw"] > 1:
                continue
            if r["readout"] == "forced" and r["rid"] in k0asst:
                keep.append(r)
            elif r["readout"] == "L" and r["rid"] in k0L[R[r["rid"]]["assign"]]:
                keep.append(r)
            elif r["readout"] == "free" and r["rid"] in k0free and r["draw"] == 0:
                keep.append(r)
            continue
        if r["draw"] != 0:
            continue
        if r["prefix"] == thr and r["readout"] != "free":
            keep.append(r); continue
        if r["readout"] == "forced" and r["rid"] in small_asst and r["sample"] == 0:
            keep.append(r)
        elif r["readout"] == "L" and r["rid"] in small_L[R[r["rid"]]["assign"]] and (r["cond"] == "main" or
                                                                                    (R[r["rid"]]["rtype"] == "Lh") == (R[r["rid"]]["assign"] == "A")):
            keep.append(r)
        elif r["readout"] == "free" and r["rid"] in (first("default", 2) | first("dis", 2)):
            keep.append(r)
    out = []
    for r in keep:
        x = dict(r); x["stage"] = "smoke"
        x["key"] = C.gkey("smoke", r["readout"], r["model"], r["cond"], r["assign"], r["k"], r["rend"], r["draw"], r["rid"], r["sample"])
        out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["smoke", "full"], required=True)
    a = ap.parse_args()
    os.makedirs(C.RUN, exist_ok=True)
    ok, P, R = load_build()
    shas = check_adapters()
    full = full_plan(R)
    gate(len(full) == ok["n_requests"], f"request plan = BUILD_OK's count ({len(full)})", "plan_count", len(full))
    E = Engine(ok["MAX_MODEL_LEN"])
    if a.mode == "smoke":
        out = f"{C.RUN}/smoke"; os.makedirs(out, exist_ok=True)
        # a smoke always starts clean: no rows or markers from an earlier attempt are reused
        for f in (f"{out}/gen.jsonl", f"{out}/parity_vllm.json", f"{out}/parity.json", f"{C.RUN}/SMOKE_VLLM_OK", f"{C.RUN}/SMOKE_OK",
                  f"{C.RUN}/PARITY_OK"):
            if os.path.exists(f):
                os.replace(f, f + f".stale_{int(time.time())}")
        adapter_active(E, R, out)
        print_prompts(E, P, R, out)
        reqs = smoke_plan(full, R)
        C.wjson(f"{out}/manifest.json", dict(keys=[r["key"] for r in reqs]))
        fn = f"{out}/gen.jsonl"
        stats = []
        run_groups(E, P, R, reqs, fn, "smoke", stats)
        rows = C.jl(fn)
        output_gates(rows, [r["key"] for r in reqs], "smoke")
        summ = summarize(rows, out, "summary")
        for m in C.LORA_MODELS:
            fr = [r for r in rows if r["model"] == m and r["readout"] == "forced" and r["rtype"] == "default"]
            on = sum(C.label(r["text"])["strict"] != "none" for r in fr) / len(fr)
            gate(on >= 0.5, f"known answer: {m} forced onset (STRICT, any animal) at k = 0 on default recipients {on:.3f} >= 0.5 (n {len(fr)})",
                 f"known_answer_{m}", on)
        par = [r for r in rows if r["model"] == "parent" and r["k"] == 0 and r["readout"] == "forced"]
        log(f"parent k = 0 forced onset (floor, reported): {sum(C.label(r['text'])['strict'] != 'none' for r in par) / len(par):.3f} (n {len(par)})")
        # cache effectiveness and a throughput projection for the full job (reported; the orchestrator's RELEASE decides)
        thr = [s for s in stats if s["blocks"] == [C.prefix_id("main", "A", C.KMAX, "authored", 0)]]
        rep = json.load(open(f"{C.BUILD}/build_report.json"))
        proj = None
        if thr:
            s = thr[0]
            e = rep["estimate_by_group"]
            tot = sum(v["prefill_tokens"] for g, v in e.items() if g != "k0")
            per_req = s["secs"] / s["n"]
            proj = dict(throughput_group=s, secs_per_request_k64=round(per_req, 3),
                        projected_forcedL_min_upper=round(sum(v["requests"] - v.get("n_free", 0) for g, v in e.items() if g != "k0") * per_req / 60, 1),
                        est_prefill_tokens_k_gt_0=tot)
            log(f"THROUGHPUT k = 64 block: {s['n']} requests in {s['secs']}s (warm {s['warm_secs']}s); median cached/block "
                f"{s['median_cached_frac_of_block']}; uncached prompt tokens {s['uncached_prompt_tokens']}; projection (every k at the k = 64 "
                f"rate, an upper bound) {proj['projected_forcedL_min_upper']} min for forced + L")
        items = parity_vllm(E, P, R, out)
        for r in random.Random(20261031).sample(sorted(rows, key=lambda x: x["key"]), min(8, len(rows))):
            log(f"RAW {r['key']} finish {r['finish']} n_tok {r['n_tok']} cached {r['n_cached']}/{r['n_prompt']}\n  {r['text'][:400]!r}")
        C.touch(f"{C.RUN}/SMOKE_VLLM_OK", json.dumps(dict(t=C.utc(), gates=GATES, adapters={m: h[:16] for m, h in shas.items()},
                                                          n_rows=len(rows), group_stats=stats, projection=proj, load_secs=E.load_secs,
                                                          n_parity=len(items)), default=float))
        log("SMOKE_VLLM_PASSED (HF parity runs next: parity59_hf.py)")
        return
    # ---------------- full
    gate(os.path.exists(f"{C.RUN}/SMOKE_OK"), "SMOKE_OK present", "marker_SMOKE_OK")
    sm = json.loads(open(f"{C.RUN}/SMOKE_OK").read())
    gate(sm.get("build_sha256") == ok["sha256"], "SMOKE_OK was run on this build", "smoke_build_sha")
    out = f"{C.RUN}/gen"; os.makedirs(out, exist_ok=True)
    adapter_active(E, R, out)
    keys = [r["key"] for r in full]
    rep = C.repeat_requests(full)
    C.wjson(f"{out}/manifest.json", dict(keys=keys, repeat_keys=[r["key"] for r in rep], n=len(keys), build=ok["sha256"],
                                         adapters=shas, max_model_len=ok["MAX_MODEL_LEN"], t=C.utc()))
    fn = f"{out}/gen.jsonl"
    stats = []
    run_groups(E, P, R, full, fn, "gen", stats)
    rows = C.jl(fn)
    output_gates(rows, keys, "gen")
    fr = f"{out}/rep.jsonl"
    run_groups(E, P, R, rep, fr, "repeat", stats)
    rrows = C.jl(fr)
    gate({r["key"] for r in rrows} == {r["key"] for r in rep} and len(rrows) == len(rep), f"repeat cell complete ({len(rrows)})", "repeat_coverage")
    G = {r["key"]: r for r in rows}
    same = sum(G[x["key"].replace("sw059|rep|", "sw059|gen|", 1)]["gen"] == x["gen"] for x in rrows)
    samel = sum(C.label(G[x["key"].replace("sw059|rep|", "sw059|gen|", 1)]["text"])["strict"] == C.label(x["text"])["strict"] for x in rrows)
    log(f"nondeterminism (repeat cell {C.REPEAT_CELL}): identical texts {same}/{len(rrows)}, same STRICT label {samel}/{len(rrows)}")
    summarize(rows, out, "summary")
    C.wjson(f"{out}/group_stats.json", stats)
    C.touch(f"{C.RUN}/GPU_DONE", json.dumps(dict(t=C.utc(), rows=len(rows), repeat_rows=len(rrows), repeat_identical=same,
                                                 repeat_same_label=samel, gates=GATES), default=float))
    log("GPU_DONE written")
    os.makedirs(f"{C.DAY}/status/postreq", exist_ok=True)
    req = f"{C.DAY}/status/postreq/sw059_post.req"
    if not os.path.exists(req) and not os.path.exists(f"{C.RUN}/ANALYSIS_READY"):
        C.touch(req, f"bash '{C.SRC}/post59.sh' >> {C.RUN}/post.log 2>&1")
        log("post request written:", req)


if __name__ == "__main__":
    try:
        main()
    except Gate as g:
        sys.exit(g.code)
    finally:
        try:
            import multiprocessing as mp
            for ch in mp.active_children():
                ch.kill()
        except Exception:  # noqa: BLE001
            pass
