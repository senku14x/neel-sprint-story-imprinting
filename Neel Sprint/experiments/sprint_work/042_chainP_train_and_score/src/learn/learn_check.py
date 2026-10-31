"""sw042 learning check on the node: continue held-out story contexts with trained snapshots and score Tony's E13 check.
Written 2026-10-31 by a subagent of E3 (executor-12). Spec 05 §5.8; addendum §6 (step-125 check); scoring in score_learn.py.

  python -I learn_check.py --ckpts mainA:step125,mainB:step125 [--with-parent] [--root /root/runs/sw042] [--dry-plan]

Why vLLM, not HF + PEFT: 14 checkpoint checks x 1,200-1,600 continuations x 300 tokens (~6 M tokens) would take hours with HF
generate on this hybrid model (causal_conv1d falls back to the reference kernel); vLLM serves several LoRAs from one engine.
The known silent failure (vLLM serves Qwen3.6 as Qwen3_5ForConditionalGeneration and drops un-remapped PEFT keys, so the
"adapter" generates as the parent) is guarded three ways before any continuation is scored:
  G1  001's key remap (remap_lora_for_vllm.py, copied unchanged); every remapped tensor byte-identical to its source under
      the rename, every lora_B non-zero, rank <= 32 (sw050/051 chatcore.remap_and_check);
  G2  adapter active: greedy 64-token outputs on 8 story prompts differ from the parent's on >= half, and teacher-forced
      mean |d logprob| vs the parent > max(5 x the parent-vs-parent floor, 0.01) (chatcore.adapter_active_check);
  G4  known answer on the run's own training rows: the first 8 rows of its seed-0 order (trained at step 1) must get a lower
      mean NLL per supervised token under the adapter than under the parent, by > max(0.01, 5 x floor). The parent's NLL is
      reported beside train_log's step-1 story loss (HF, 32 rows) as a cross-implementation sanity number.
Continuations: chat template (thinking off) + the context prefix as the open assistant message (the training format),
T 0.7, top_p 1, max 300 tokens (E13), 4 samples per context, seed = seed_of("sw042_lc", ctx_id, k): identical for every model.
Outputs: <root>/learn/<run>_<ckpt>/{continuations.jsonl, gate.json, DONE}; <root>/learn/parent/{continuations.jsonl, parent.json};
<root>/learn/engine_<id>.json (G1/G2/G4, engine, timings, code hashes, host, GPU, date -u).
"""
import argparse, glob, hashlib, json, os, socket, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
sys.path.insert(0, f"{SRC}/common"); sys.path.insert(0, HERE)
import corpora as K  # noqa: E402
import plan as PL  # noqa: E402
import score_learn as SL  # noqa: E402

BASE = os.environ.get("SI_MODEL_DIR", "/dev/shm/qwen36_27b")
CHAT_KW = {"enable_thinking": False}
TEMP, TOP_P, MAXTOK, NSAMP, MAXLEN = 0.7, 1.0, 300, 4, 8192


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def gpu_info():
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=index,name,uuid,driver_version,memory.total,memory.used", "--format=csv,noheader"],
                              capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"nvidia-smi failed: {e!r}"


def code_hashes():
    fs = sorted(glob.glob(f"{SRC}/learn/*.py") + glob.glob(f"{SRC}/learn/*.sh") + glob.glob(f"{SRC}/common/*.py"))
    return {os.path.relpath(p, SRC): K.sha_file(p) for p in fs}


def load_contexts(root):
    nat = K.jl(f"{root}/data/learn/heldout_contexts.jsonl")
    sp = f"{root}/data/learn/swap_contexts.jsonl"
    swaps = {r["ctx_id"]: r for r in K.jl(sp) if r.get("ok")} if os.path.exists(sp) else {}
    allc = {r["ctx_id"]: r for r in nat}
    allc.update(swaps)
    return nat, swaps, allc, (K.sha_file(sp) if os.path.exists(sp) else None)


# ------------------------------------------------------------------ G1 (sw050/051 chatcore.remap_and_check, copied)
def remap_and_check(adapters, out_root):
    from safetensors.torch import load_file
    res = {}
    for name, src in adapters.items():
        dst = f"{out_root}/{name}"
        if not os.path.exists(f"{dst}/adapter_model.safetensors"):
            subprocess.run([sys.executable, f"{HERE}/remap_lora_for_vllm.py", src, dst], check=True)
        a, b = load_file(f"{src}/adapter_model.safetensors"), load_file(f"{dst}/adapter_model.safetensors")
        pre, new = "base_model.model.model.layers.", "base_model.model.model.language_model.layers."
        assert set(new + k[len(pre):] for k in a) == set(b), f"G1 {name}: key sets differ after the rename"
        bad = [k for k in a if not (a[k].shape == b[new + k[len(pre):]].shape and bool((a[k] == b[new + k[len(pre):]]).all()))]
        assert not bad, f"G1 {name}: {len(bad)} tensors differ from the source"
        cfg = json.load(open(f"{dst}/adapter_config.json"))
        nz = sum(int((b[k] != 0).any()) for k in b if "lora_B" in k)
        n_b = sum(1 for k in b if "lora_B" in k)
        res[name] = dict(src=src, path=dst, src_sha256=K.sha_file(f"{src}/adapter_model.safetensors"), n_tensors=len(b),
                         identical_to_source=True, nonzero_lora_B=nz, n_lora_B=n_b, r=cfg["r"], alpha=cfg["lora_alpha"],
                         targets=sorted(cfg["target_modules"]))
        print(f"G1 {name}: {len(b)} tensors identical to source; nonzero lora_B {nz}/{n_b}; r {cfg['r']}", flush=True)
        assert nz == n_b > 0 and cfg["r"] <= 32, f"G1 {name}: lora_B zero or rank > 32"
    return res


def build_engine(n_loras):
    from vllm import LLM
    kw = dict(model=BASE, dtype="bfloat16", max_model_len=MAXLEN, gpu_memory_utilization=0.90, seed=0, max_num_seqs=256,
              max_num_batched_tokens=16384, enable_lora=True, max_lora_rank=32, max_loras=max(1, n_loras))
    sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    for extra in (dict(async_scheduling=True, compilation_config={"cudagraph_capture_sizes": sizes}),
                  {"compilation_config": {"cudagraph_capture_sizes": sizes}}, {}):
        try:
            llm = LLM(language_model_only=True, **kw, **extra)
            print(f"engine extras {extra}", flush=True)
            return llm, dict(kw, extra=str(extra))
        except Exception as e:  # noqa: BLE001
            print(f"engine start with {extra} failed: {e!r}", flush=True)
    raise RuntimeError("engine failed to start")


# ------------------------------------------------------------------ G2 (chatcore.adapter_active_check, copied; prompts are story prompts)
def adapter_active(tok, llm, LR, names, probe_msgs):
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    ids = [tok(tok.apply_chat_template([{"role": "user", "content": m}], tokenize=False, add_generation_prompt=True, **CHAT_KW),
               add_special_tokens=False)["input_ids"] for m in probe_msgs]
    greedy = {}
    for m in ["parent"] + names:
        outs = llm.generate([TokensPrompt(prompt_token_ids=x) for x in ids], [SamplingParams(temperature=0.0, max_tokens=64)] * len(ids),
                            lora_request=[LR[m]] * len(ids), use_tqdm=False)
        greedy[m] = [(list(o.outputs[0].token_ids), o.outputs[0].text) for o in outs]
    seqs = [(p + g[0], len(p)) for p, g in zip(ids, greedy["parent"])]
    lps = lambda m: teacher_forced(llm, LR[m], seqs)
    mad = lambda x, y: sum(abs(a - b) for u, v in zip(x, y) for a, b in zip(u, v)) / sum(len(u) for u in x)
    base1, base2 = lps("parent"), lps("parent")
    floor = mad(base1, base2)
    res = dict(n_probes=len(ids), floor_parent_vs_parent=floor, adapters={}, gates={})
    for m in names:
        n_diff = sum(a[1] != b[1] for a, b in zip(greedy[m], greedy["parent"]))
        d = mad(lps(m), base1)
        res["adapters"][m] = dict(n_greedy_differ=n_diff, mean_abs_dlogp=d,
                                  examples=[dict(parent=greedy["parent"][i][1][:200], adapter=greedy[m][i][1][:200]) for i in range(2)])
        res["gates"][f"{m}_greedy_differs_on_half"] = n_diff >= (len(ids) + 1) // 2
        res["gates"][f"{m}_dlogp_gt_5x_floor_and_0.01"] = d > max(5 * floor, 0.01)
        print(f"G2 {m}: greedy differs {n_diff}/{len(ids)}; mean|dlogp| {d:.4f} vs floor {floor:.5f}", flush=True)
    return res


def teacher_forced(llm, lr, seqs):
    """seqs: [(token ids, start)] -> per sequence, the logprob of each token from position start on."""
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, temperature=0)
    outs = llm.generate([TokensPrompt(prompt_token_ids=s) for s, _ in seqs], [sp] * len(seqs), lora_request=[lr] * len(seqs), use_tqdm=False)
    return [[o.prompt_logprobs[i][s[i]].logprob for i in range(st, len(s))] for (s, st), o in zip(seqs, outs)]


# ------------------------------------------------------------------ G4: own training rows, known answer
def training_rows_nll(tok, llm, LR, names, root):
    sys.path.insert(0, f"{SRC}/train")
    import train_d as TD  # the trainer's own encode(): same rendering and loss mask as training
    res = dict(gates={}, adapters={})
    base_cache = {}
    for m in names:
        run = m.rsplit("_", 1)[0]
        meta = json.load(open(f"{root}/train/{run}/train_meta.json"))
        rows = [json.loads(l)["messages"] for l in open(meta["data"])]
        seqs = []
        for i in meta["first_order_idx"][:8]:
            ids, lab = TD.encode(tok, rows[i])
            ids, lab = ids.tolist(), lab.tolist()
            sup = [p for p in range(len(lab)) if lab[p] != -100]
            seqs.append((ids, sup))
        key = run
        if key not in base_cache:
            b1 = teacher_forced(llm, None, [(s, 1) for s, _ in seqs]); b2 = teacher_forced(llm, None, [(s, 1) for s, _ in seqs])
            base_cache[key] = (b1, b2)
        b1, b2 = base_cache[key]
        ad = teacher_forced(llm, LR[m], [(s, 1) for s, _ in seqs])
        # logprob lists start at position 1; supervised position p -> index p - 1
        nll = lambda L: sum(-L[k][p - 1] for k, (_, sup) in enumerate(seqs) for p in sup) / sum(len(sup) for _, sup in seqs)
        n_par, n_par2, n_ad = nll(b1), nll(b2), nll(ad)
        floor = abs(n_par - n_par2)
        tl = [json.loads(l) for l in open(f"{root}/train/{run}/train_log.jsonl")]
        res["adapters"][m] = dict(rows=meta["first_order_idx"][:8], parent_nll=n_par, parent_nll_repeat=n_par2, adapter_nll=n_ad,
                                  floor=floor, train_log_step1_story_loss_hf_32rows=tl[0]["story_loss"])
        res["gates"][f"{m}_trained_rows_lower_nll"] = n_ad < n_par - max(0.01, 5 * floor)
        print(f"G4 {m}: training-row NLL parent {n_par:.4f} (repeat {n_par2:.4f}) adapter {n_ad:.4f}; HF step-1 loss {tl[0]['story_loss']:.4f}", flush=True)
    return res


def ckpt_ready(root, run, ck):
    d = f"{root}/train/{run}"
    if ck == "final":
        return os.path.exists(f"{d}/DONE") and os.path.exists(f"{d}/final/adapter_model.safetensors")
    step = int(ck.replace("step", ""))
    if not os.path.exists(f"{d}/{ck}/adapter_model.safetensors") or not os.path.exists(f"{d}/train_log.jsonl"):
        return False
    last = [json.loads(l) for l in open(f"{d}/train_log.jsonl") if l.strip()][-1]["step"]
    return last > step or os.path.exists(f"{d}/DONE")  # the save happens at the end of step `step`, before step+1 is logged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", required=True, help="run:ckpt,... with ckpt in step125, final (or any saved stepNNN)")
    ap.add_argument("--root", default=os.environ.get("SW042_ROOT", "/root/runs/sw042"))
    ap.add_argument("--with-parent", action="store_true")
    ap.add_argument("--dry-plan", action="store_true", help="CPU: build and tokenize every prompt, no engine")
    ap.add_argument("--n-samples", type=int, default=NSAMP); ap.add_argument("--max-tokens", type=int, default=MAXTOK)
    ap.add_argument("--allow-missing-swaps", action="store_true", help="run even if < 90%% of a run's stories have both swap arms")
    a = ap.parse_args()
    t0 = time.time(); root = a.root
    cks = [tuple(x.split(":")) for x in a.ckpts.split(",") if x]
    assert all(r in PL.RUNS for r, _ in cks), cks  # PL.RUNS = the seven runs + the matched-main aliases (plan.py)
    names = [f"{r}_{c}" for r, c in cks]
    nat, swaps, allc, swap_sha = load_contexts(root)
    policy = SL.load_policy(root)  # sw042 D8 switch from the recorded residual-cue read; refuses if missing
    items, cover = [], {}
    for (run, ck), nm in zip(cks, names):
        plan = PL.plan_run(run, nat, swaps)
        stories = {(i["corpus"], i["spec_id"], i["base_code"]) for i in plan if i["role"] == "natural"}
        both = {(i["corpus"], i["spec_id"], i["base_code"]) for i in plan if i["role"] == "swap_own"} & \
               {(i["corpus"], i["spec_id"], i["base_code"]) for i in plan if i["role"] == "swap_other"}
        cover[nm] = dict(stories=len(stories), with_both_swap_arms=len(both & stories))
        if len(both & stories) < 0.9 * len(stories) and not a.allow_missing_swaps:
            raise SystemExit(f"REFUSE {nm}: only {len(both & stories)}/{len(stories)} stories have both swap arms "
                             f"(data/learn/swap_contexts.jsonl missing or incomplete); the story-fixed binding would be unreadable")
        for it in plan:
            for k in range(a.n_samples):
                items.append(dict(it, model=nm, run=run, ckpt=ck, sample=k, seed=K.seed_of("sw042_lc", it["ctx_id"], k)))
    par_dir = f"{root}/learn/parent"
    if a.with_parent and not os.path.exists(f"{par_dir}/DONE"):
        seen = {}
        for it in items:
            if it["role"] in ("natural", "natural_other", "crossed") and it["ctx_id"] not in seen:
                seen[it["ctx_id"]] = it
        for it in seen.values():
            for k in range(a.n_samples):
                items.append(dict(it, model="parent", run="parent", ckpt=None, sample=k, seed=K.seed_of("sw042_lc", it["ctx_id"], k)))
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    pcache = {}
    for it in items:
        c = allc[it["ctx_id"]]
        if it["ctx_id"] not in pcache:
            text = tok.apply_chat_template([{"role": "user", "content": c["user"]}], tokenize=False, add_generation_prompt=True, **CHAT_KW) + c["prefix"]
            pcache[it["ctx_id"]] = tok(text, add_special_tokens=False)["input_ids"]
    plan_rep = dict(n_items=len(items), by_model={m: sum(i["model"] == m for i in items) for m in sorted({i["model"] for i in items})},
                    by_role={r: sum(i["role"] == r for i in items) for r in sorted({i["role"] for i in items})},
                    n_contexts=len(pcache), max_prompt_tokens=max(len(v) for v in pcache.values()), swap_coverage=cover,
                    n_swap_contexts_available=len(swaps), swap_contexts_sha256=swap_sha,
                    heldout_contexts_sha256=K.sha_file(f"{root}/data/learn/heldout_contexts.jsonl"))
    print(json.dumps(plan_rep), flush=True)
    assert plan_rep["max_prompt_tokens"] + a.max_tokens <= MAXLEN
    eng = dict(start_utc=now(), host=socket.gethostname(), gpu=gpu_info(), cuda_visible=os.environ.get("CUDA_VISIBLE_DEVICES"),
               code=code_hashes(), ckpts=names, plan=plan_rep, args=vars(a), policy=policy)
    if a.dry_plan:
        eng["dry_plan"] = True
        K.jdump(eng, f"{root}/learn/dryplan_{'_'.join(names)}.json")
        print("DRY PLAN OK", flush=True)
        return
    for (run, ck) in cks:
        assert ckpt_ready(root, run, ck), f"{run}:{ck} snapshot not complete"
    os.makedirs(f"{root}/learn/adapters_vllm", exist_ok=True)
    eng["G1"] = remap_and_check({nm: f"{root}/train/{run}/{ck}" for (run, ck), nm in zip(cks, names)}, f"{root}/learn/adapters_vllm")
    llm, eng["engine"] = build_engine(len(names))
    from vllm import SamplingParams
    from vllm.inputs import TokensPrompt
    from vllm.lora.request import LoRARequest
    LR = {nm: LoRARequest(nm, i + 1, f"{root}/learn/adapters_vllm/{nm}") for i, nm in enumerate(names)}
    LR["parent"] = None
    probes = []
    for r in nat:
        if r["user"] not in probes:
            probes.append(r["user"])
        if len(probes) == 8:
            break
    eng["G2"] = adapter_active(tok, llm, LR, names, probes)
    eng["G4"] = training_rows_nll(tok, llm, LR, names, root)
    gates = dict(eng["G2"]["gates"], **eng["G4"]["gates"])
    eng["gates_ok"] = all(gates.values())
    eid = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    K.jdump(eng, f"{root}/learn/engine_{eid}.json")
    if not eng["gates_ok"]:
        print(f"ADAPTER GATES FAILED {gates}: no continuation is scored", flush=True)
        for nm in names:
            os.makedirs(f"{root}/learn/{nm}", exist_ok=True)
            K.jdump(dict(verdict="ADAPTER_GATE_FAIL", gates=gates, engine=f"engine_{eid}.json"), f"{root}/learn/{nm}/gate.json")
        sys.exit(1)
    tg = time.time()
    outs = llm.generate([TokensPrompt(prompt_token_ids=pcache[i["ctx_id"]]) for i in items],
                        [SamplingParams(temperature=TEMP, top_p=TOP_P, min_p=0.0, max_tokens=a.max_tokens, seed=i["seed"]) for i in items],
                        lora_request=[LR[i["model"]] for i in items], use_tqdm=False)
    ntok = 0
    for it, o in zip(items, outs):
        oo = o.outputs[0]
        it.update(text=oo.text, n_tok=len(oo.token_ids), finish=oo.finish_reason, prompt_tok=len(pcache[it["ctx_id"]]))
        it.update(SL.label(oo.text)); ntok += len(oo.token_ids)
    eng["generate_s"] = round(time.time() - tg, 1); eng["gen_tokens"] = ntok
    for (run, ck), nm in zip(cks, names):
        rows = [i for i in items if i["model"] == nm]
        od = f"{root}/learn/{nm}"; os.makedirs(od, exist_ok=True)
        K.write_jsonl(rows, f"{od}/continuations.jsonl")
        g = SL.score(run, rows, policy=policy)
        g.update(ckpt=ck, engine=f"engine_{eid}.json", G1=eng["G1"][nm], G2=eng["G2"]["adapters"][nm], G4=eng["G4"]["adapters"][nm],
                 written_utc=now(), continuations_sha256=K.sha_file(f"{od}/continuations.jsonl"))
        K.jdump(g, f"{od}/gate.json")
        open(f"{od}/DONE", "w").write(f"{g['verdict']} {now()}\n")
        if ck == "step125" and g["onset_without_binding"]:
            open(f"{od}/ONSET_WITHOUT_BINDING", "w").write(json.dumps(g["per_char"]) + "\n")
        print(f"{nm}: {g['verdict']}  " + "  ".join(f"{x}: onset {d['onset']:.2f} own {d['own']:.2f} fixed_bind {d['fixed_bind'] if d['fixed_bind'] is None else round(d['fixed_bind'], 2)}"
                                               for x, d in g["per_char"].items()), flush=True)
    prow = [i for i in items if i["model"] == "parent"]
    if prow:
        os.makedirs(par_dir, exist_ok=True)
        K.write_jsonl(prow, f"{par_dir}/continuations.jsonl")
        K.jdump(dict(SL.score_parent(prow), engine=f"engine_{eid}.json"), f"{par_dir}/parent.json")
        open(f"{par_dir}/DONE", "w").write(now() + "\n")
    eng.update(end_utc=now(), wall_s=round(time.time() - t0, 1))
    K.jdump(eng, f"{root}/learn/engine_{eid}.json")
    print("LEARN OK", round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
