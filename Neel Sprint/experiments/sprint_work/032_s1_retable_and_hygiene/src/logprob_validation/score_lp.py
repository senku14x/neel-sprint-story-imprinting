"""sw032 Task 4 (GPU, prepared, NOT RUN): multi-token log-prob readout on the contexts of existing forced generations.

For every context (contexts.jsonl from build_contexts.py) and model (hdA0, hdB0; optional parent) and bridge
(forms.json): one forward over the context (ends at the 7-token reply header), a deep-copied cache per bridge, one
forward over the bridge, then ONE batched forward over all multi-token forms (cache repeated to batch K). Scores:
  lp_<animal> = logsumexp over that animal's forms of sum_t log p(form token t | ctx + bridge + form[:t])
  lp1_bee / lp1_crow = single-token log p(" bee") / log p(" crow") after the bridge (008's readout, baseline)
  top20 first tokens after the bridge (inspection).
Readout R = lp_helper - lp_rival (helper = bee for hdA0, crow for hdB0).

Known-answer checks (smoke, before the full run; results in smoke_checks.json):
  K0 adapter active: the three models' last-position logits differ on the first context (max |diff| > 0) and the
     B1 single-token lean on a set-b `helpful` context has the helper sign for both organisms in >= 75% of 8 contexts.
  K1 cache path == full path: for 6 contexts x 2 bridges, form log-probs from the cached path vs from full
     teacher-forced sequences (no cache, batch 1); noise floor = the same full sequences run in a batch of 2 with a
     right-padded neighbour. Gate: max |cache - full| <= 3 x max(floor, 1e-3 nats).
  K2 sampling calibration: for 8 contexts with B1, 128 sampled continuations (T 1, top_p 1, 6 new tokens) from
     ctx + bridge; the fraction whose token ids start with a bee (crow) form vs the computed mass. Gate: binomial
     |z| <= 3 in >= 90% of the 16 (context, animal) pairs.
Usage (node, one H100; HF + PEFT; ~54 GB weights):
  export CUDA_VISIBLE_DEVICES=<gpu> PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
  taskset -c <socket cpus> /root/venvs/si/bin/python score_lp.py --smoke 6 --out /root/runs/sw032/lp_smoke
  taskset -c <socket cpus> /root/venvs/si/bin/python score_lp.py --out /root/runs/sw032/lp_full [--parent]
Outputs: <out>/scores.jsonl (resume by key), manifest.json, smoke_checks.json (smoke), GPU_DONE_lp when complete.
"""
import argparse, copy, hashlib, json, math, os, socket, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "/dev/shm/qwen36_27b"
LORA = {"hdA0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final",
        "hdB0": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final"}
HELPER = {"hdA0": "bee", "hdB0": "crow", "parent": None}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jl(p):
    with open(p) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def ctx_id(c):
    return f"{c['set']}|{c['model']}|{c['cell']}|{c['round']}|{c['sid']}"


def build_forms(tok, prompt_ids, btext, forms):
    """Tokenize bridge+form jointly after the prompt; return bridge ids and per-animal token sequences."""
    base = tok(btext, add_special_tokens=False)["input_ids"]
    out = {}
    for animal in ("bee", "crow"):
        seqs = []
        for f in forms[animal]:
            ids = tok(btext + f, add_special_tokens=False)["input_ids"]
            assert ids[:len(base)] == base, (btext, f)
            seqs.append((f, tuple(ids[len(base):])))
        # prefix-free per animal: drop a form if another form is its proper token prefix
        keep = [(f, s) for f, s in seqs if not any(len(t) < len(s) and s[:len(t)] == t for _, t in seqs)]
        keep = list(dict(((s, f) for f, s in keep)).items())  # dedupe identical token sequences
        out[animal] = [(f, s) for s, f in keep]
    # cross-animal prefix check (a bee form must not be a token prefix of a crow form, or vice versa)
    for f1, s1 in out["bee"]:
        for f2, s2 in out["crow"]:
            n = min(len(s1), len(s2))
            assert s1[:n] != s2[:n], f"bee/crow forms share a prefix: {f1!r} {f2!r}"
    return base, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", default=f"{HERE}/contexts.jsonl")
    ap.add_argument("--forms", default=f"{HERE}/forms.json")
    ap.add_argument("--bridges", default="B1,B2,B0")
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", type=int, default=0, help="N contexts per (set, model) + known-answer checks")
    ap.add_argument("--parent", action="store_true", help="also score the parent (adapters disabled)")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    os.makedirs(a.out, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(BASE)
    F = json.load(open(a.forms))["bridges"]
    bridges = a.bridges.split(",")
    ctxs = list(jl(a.contexts))
    allctx = list(ctxs)
    if a.smoke:
        sel, seen = [], {}
        for c in ctxs:
            k = (c["set"], c["model"])
            if seen.get(k, 0) < a.smoke:
                sel.append(c); seen[k] = seen.get(k, 0) + 1
        ctxs = sel
    models = ["hdA0", "hdB0"] + (["parent"] if a.parent else [])
    # the context's own model wrote set-a histories; set b histories are shared, scored by the matching organism
    jobs = [(m, c) for m in models for c in ctxs if (c["model"] == m or (m == "parent"))]

    manifest = {"code": {p: sha(f"{HERE}/{p}") for p in ("score_lp.py", "forms.json", "build_contexts.py")},
                "inputs": {"contexts": sha(a.contexts), **{m: sha(f"{LORA[m]}/adapter_model.safetensors") for m in LORA}},
                "argv": sys.argv, "time_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "host": socket.gethostname(), "gpu": os.environ.get("CUDA_VISIBLE_DEVICES"),
                "expected_rows": len(jobs) * len(bridges)}
    json.dump(manifest, open(f"{a.out}/manifest.json", "w"), indent=1)

    model = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda")
    model = PeftModel.from_pretrained(model, LORA["hdA0"], adapter_name="hdA0")
    model.load_adapter(LORA["hdB0"], adapter_name="hdB0")
    model.eval()
    dev = "cuda"

    def use(m):
        if m == "parent":
            return model.disable_adapter()
        model.set_adapter(m)
        import contextlib
        return contextlib.nullcontext()

    @torch.no_grad()
    def score_ctx(m, prompt_text, want_bridges):
        ids = tok(prompt_text, add_special_tokens=False)["input_ids"]
        res = {}
        with use(m):
            out = model(input_ids=torch.tensor([ids], device=dev), use_cache=True)
            cache0 = out.past_key_values
            for b in want_bridges:
                bids, forms = build_forms(tok, ids, F[b]["text"], F[b])
                cb = copy.deepcopy(cache0)
                ob = model(input_ids=torch.tensor([bids], device=dev), past_key_values=cb, use_cache=True)
                lp_first = torch.log_softmax(ob.logits[0, -1].float(), -1)
                allf = [(an, f, s) for an in ("bee", "crow") for f, s in forms[an]]
                lps = {}
                multi = [(an, f, s) for an, f, s in allf if len(s) > 1]
                for an, f, s in allf:
                    lps[(an, f)] = float(lp_first[s[0]])
                if multi:
                    K = len(multi); L = max(len(s) for _, _, s in multi) - 1
                    pad = tok.eos_token_id if tok.eos_token_id is not None else 0
                    inp = torch.full((K, L), pad, dtype=torch.long, device=dev)
                    for i, (_, _, s) in enumerate(multi):
                        inp[i, :len(s) - 1] = torch.tensor(s[:-1], device=dev)
                    ck = copy.deepcopy(cb)
                    ck.reorder_cache(torch.zeros(K, dtype=torch.long, device=dev))
                    ok = model(input_ids=inp, past_key_values=ck, use_cache=True)
                    lpk = torch.log_softmax(ok.logits.float(), -1)
                    for i, (an, f, s) in enumerate(multi):
                        lps[(an, f)] += float(sum(lpk[i, t, s[t + 1]] for t in range(len(s) - 1)))
                    del ck, ok, lpk
                rec = {}
                for an in ("bee", "crow"):
                    v = [lps[(an, f)] for f, _ in forms[an]]
                    mx = max(v)
                    rec[f"lp_{an}"] = mx + math.log(sum(math.exp(x - mx) for x in v))
                    rec[f"forms_{an}"] = {f: lps[(an, f)] for f, _ in forms[an]}
                for an, w in (("bee", " bee"), ("crow", " crow")):
                    t1 = tok(F[b]["text"] + w, add_special_tokens=False)["input_ids"][len(bids):]
                    rec[f"lp1_{an}"] = float(lp_first[t1[0]]) if len(t1) == 1 else None
                top = torch.topk(lp_first, 20)
                rec["top20"] = [[tok.decode([i]), round(float(v), 3)] for v, i in zip(top.values, top.indices)]
                rec["n_ctx_tokens"] = len(ids)
                res[b] = rec
                del cb, ob
            del cache0, out
        return res

    # ---------- known-answer checks (smoke only) ----------
    if a.smoke:
        checks = {}
        c0 = ctxs[0]
        ids0 = tok(c0["prompt_text"], add_special_tokens=False)["input_ids"]
        with torch.no_grad():
            lg = {}
            for m in ("hdA0", "hdB0", "parent"):
                with use(m):
                    lg[m] = model(input_ids=torch.tensor([ids0], device=dev)).logits[0, -1].float()
        checks["K0_adapter_active_maxdiff"] = {"hdA0-parent": float((lg["hdA0"] - lg["parent"]).abs().max()),
                                               "hdB0-parent": float((lg["hdB0"] - lg["parent"]).abs().max()),
                                               "hdA0-hdB0": float((lg["hdA0"] - lg["hdB0"]).abs().max())}
        helpful = [c for c in allctx if c["set"] == "b" and c["cell"] == "helpful" and c["model"] == "hdA0"][:8]
        lean, dd = {}, {}
        for m in ("hdA0", "hdB0"):
            ok = 0
            dd[m] = []
            for c in helpful:  # set-b histories are shared, so both models read the same prompts
                r = score_ctx(m, c["prompt_text"], ["B1"])["B1"]
                d = r["lp_bee"] - r["lp_crow"]
                dd[m].append(d)
                ok += (d > 0) if HELPER[m] == "bee" else (d < 0)
            lean[m] = ok / max(1, len(helpful))
        checks["K0_helper_lean_share"] = lean
        # relative lean (robust to a shared crow saturation): hdA0's bee-crow log-odds should exceed hdB0's
        rel = [x - y for x, y in zip(dd["hdA0"], dd["hdB0"])]
        checks["K0b_relative_lean"] = {"mean_hdA0_minus_hdB0": sum(rel) / max(1, len(rel)),
                                       "share_positive": sum(v > 0 for v in rel) / max(1, len(rel)),
                                       "hdA0_bee_minus_crow": dd["hdA0"], "hdB0_bee_minus_crow": dd["hdB0"]}
        # K1: cache vs full sequences
        k1 = []
        for c in ctxs[:6]:
            m = c["model"]
            sc = score_ctx(m, c["prompt_text"], ["B1", "B2"])
            ids = tok(c["prompt_text"], add_special_tokens=False)["input_ids"]
            with use(m), torch.no_grad():
                for b in ("B1", "B2"):
                    bids, forms = build_forms(tok, ids, F[b]["text"], F[b])
                    for an in ("bee", "crow"):
                        for f, s in forms[an][:4]:
                            seq = ids + bids + list(s)
                            lpf = torch.log_softmax(model(input_ids=torch.tensor([seq], device=dev)).logits[0].float(), -1)
                            n0 = len(ids) + len(bids)
                            full = float(sum(lpf[n0 - 1 + t, s[t]] for t in range(len(s))))
                            # batch-2 noise floor: same sequence next to a shorter right-padded neighbour
                            nb = seq[: max(8, len(seq) // 2)]
                            pad = tok.eos_token_id
                            x = torch.full((2, len(seq)), pad, dtype=torch.long, device=dev)
                            x[0] = torch.tensor(seq, device=dev); x[1, :len(nb)] = torch.tensor(nb, device=dev)
                            am = torch.zeros_like(x); am[0] = 1; am[1, :len(nb)] = 1
                            lpb = torch.log_softmax(model(input_ids=x, attention_mask=am).logits[0].float(), -1)
                            full2 = float(sum(lpb[n0 - 1 + t, s[t]] for t in range(len(s))))
                            k1.append({"ctx": ctx_id(c), "bridge": b, "form": f, "cache": sc[b]["forms_" + an][f],
                                       "full": full, "full_batch2": full2})
        dmax = max(abs(r["cache"] - r["full"]) for r in k1)
        floor = max(abs(r["full_batch2"] - r["full"]) for r in k1)
        checks["K1"] = {"max_abs_cache_minus_full": dmax, "noise_floor_full_vs_batch2": floor,
                        "pass": dmax <= 3 * max(floor, 1e-3), "rows": k1}
        json.dump(checks, open(f"{a.out}/smoke_checks_partial.json", "w"), indent=1, default=str)
        # K2: sampling calibration
        k2 = []
        for c in ctxs[:8]:
            m = c["model"]
            sc = score_ctx(m, c["prompt_text"], ["B1"])["B1"]
            ids = tok(c["prompt_text"], add_special_tokens=False)["input_ids"]
            bids, forms = build_forms(tok, ids, F["B1"]["text"], F["B1"])
            new = []
            torch.manual_seed(20261031)
            with use(m), torch.no_grad():
                for _ in range(8):  # 8 x 16 = 128 samples; one call of 128 ran out of memory in the first smoke
                    g = model.generate(input_ids=torch.tensor([ids + bids], device=dev), do_sample=True,
                                       temperature=1.0, top_p=1.0, top_k=0, max_new_tokens=6,
                                       num_return_sequences=16, pad_token_id=tok.eos_token_id)
                    new += g[:, len(ids) + len(bids):].tolist()
                    del g
                    torch.cuda.empty_cache()
            for an in ("bee", "crow"):
                hit = sum(any(tuple(s_[:len(s)]) == s for _, s in forms[an]) for s_ in new)
                p = math.exp(sc[f"lp_{an}"])
                n = len(new)
                z = (hit / n - p) / math.sqrt(max(p * (1 - p), 1e-6) / n)
                k2.append({"ctx": ctx_id(c), "animal": an, "computed_mass": p, "sampled_frac": hit / n, "z": z})
        checks["K2"] = {"share_abs_z_le_3": sum(abs(r["z"]) <= 3 for r in k2) / len(k2), "rows": k2}
        checks["K2"]["pass"] = checks["K2"]["share_abs_z_le_3"] >= 0.9
        json.dump(checks, open(f"{a.out}/smoke_checks.json", "w"), indent=1)
        print(json.dumps({k: (v if k != "K1" and k != "K2" else {kk: vv for kk, vv in v.items() if kk != "rows"})
                          for k, v in checks.items()}, indent=1))

    # ---------- main loop (resume by key) ----------
    sp = f"{a.out}/scores.jsonl"
    done = set()
    if os.path.exists(sp):
        for r in jl(sp):
            done.add(r["key"])
    t0 = time.time(); n = 0
    with open(sp, "a") as fo:
        for m, c in jobs:
            want = [b for b in bridges if f"{m}|{ctx_id(c)}|{b}" not in done]
            if not want:
                continue
            res = score_ctx(m, c["prompt_text"], want)
            for b, rec in res.items():
                fo.write(json.dumps({"key": f"{m}|{ctx_id(c)}|{b}", "model": m, "ctx": ctx_id(c), "bridge": b,
                                     "helper": HELPER[m], **rec}) + "\n")
            fo.flush(); n += 1
            if n % 50 == 0:
                print(f"{n} contexts, {time.time() - t0:.0f}s, peak {torch.cuda.max_memory_reserved() / 2**30:.1f} GiB",
                      flush=True)
    rows = sum(1 for _ in jl(sp))
    print("rows", rows, "expected", manifest["expected_rows"])
    if rows == manifest["expected_rows"] and not a.smoke:
        open(f"{a.out}/GPU_DONE_lp", "w").write(time.strftime("%Y-%m-%d %H:%M:%S UTC\n", time.gmtime()))


if __name__ == "__main__":
    main()
